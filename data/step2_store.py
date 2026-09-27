"""Stage E.2b Task 4: the step 2 bar store (lead ruling OC-C; design D4, ML design M1).

    uv run python -m data.step2_store --products NQ ZN --harness-sha256 <sha256>

One parquet per product with every trade date 2019-05-06..2024-02-29 the product has bars on,
built from the product's 58 UNSEALED step 2 chunks (2019-05..2024-02) listed in its purchase
manifest reports/step2/purchase_<ROOT>.json (data.pull_step2). This one store is both the ML
route's training-window store (M1: S_X..2024-02-29) and the cluster confirmation-window store
(D4: S_X..2024-02-29); S_X (D4's start rule) is applied by its readers, not here.

Layout (reports/stage_e2b_task4_purchase_worker.md section 1):
  STEP2_ROOT/<ROOT>/ohlcv-1m_<ROOT>_v_0_2019-05-06_2024-02-29_step2.parquet   (0444, os.link)
  reports/step2/bars_<ROOT>.json                                              (the summary)
with STEP2_ROOT = data/processed_step2 (its own base; lead ruling: M7.4, V10 separate roots).

The per-product logic is data/build_bars.py's (the research store's): the group calendar and
flatten policy, rolls from the free symbology of <ROOT>.v.0 over 2019-05-01..2024-03-01, the
D.1f raw-symbol rule, MES's hard checks, the close-minute rule L-3, bars inside a scheduled
closure beyond the close minute held for the lead, flag_frame's columns and the parquet writer.
What differs, in order:
1. Inputs: only the product's unsealed chunks (58, or fewer for a contract listed after 2019-05:
   from its first vendor-priceable month, lead ruling OC-R), each verified by sha256 and record
   count against the purchase manifest. A sealed chunk, a holdout-2 or embargo chunk name,
   anything under the sealed stores, or anything outside 2019-05-01..2024-03-01 is refused
   BEFORE any file is opened (``refuse_inputs``); the builder never opens a sealed chunk.
2. Right after decoding, every row is given its trade date from ts_event alone and every row
   outside 2019-05-06..2024-02-29 is dropped before any check or flag reads a price
   (``drop_outside_window``): the February 2024 chunk's rows booked to 2024-03-01 (the embargo)
   are counted and never written. A row booked to a holdout-2 or later trade date in an unsealed
   file is a leak and raises.
3. The written frame is checked again: every trade date must be a confirmation-window date
   (data.research_bars.refuse_non_confirmation_dates) inside 2019-05-06..2024-02-29.
From the step 2 history this module computes bars, their validation and calendar checks only.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable, Sequence
from dataclasses import asdict
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from data import build_bars as bb
from data import holdout as ho
from data import step2_seal as seal
from data.bars import load_raw_bars
from data.config import DATA_ROOT, DATASET, REPO_ROOT, STEP2_ROOT, VENDOR_ROOT
from data.group_session import (
    NS_PER_MIN,
    STAGE_E_POLICIES,
    GroupCalendar,
    assign_trade_dates,
    closed_windows,
    group_of,
    load_group_calendar,
    open_intervals,
)
from data.research_bars import (
    CONFIRMATION_LAST_TRADE_DATE,
    CONFIRMATION_RAW_CHUNKS,
    EMBARGO2_START,
    HOLDOUT2_RAW_CHUNKS,
    HOLDOUT2_START,
    HoldoutLeakError,
    refuse_non_confirmation_dates,
)
from data.validate import in_windows, validate_bars

FIRST_TRADE_DATE = date(2019, 5, 6)  # D4: the earliest possible S_X
LAST_TRADE_DATE = CONFIRMATION_LAST_TRADE_DATE  # 2024-02-29
DATA_START = date(2019, 5, 1)  # the first step 2 chunk's start, 00:00 UTC
DATA_END = date(2024, 3, 1)  # exclusive: the last unsealed chunk's end
SPAN = f"{DATA_START}_{DATA_END}"
UNSEALED_NAMES = tuple(f"range={s}_{e}.dbn.zst" for s, e in CONFIRMATION_RAW_CHUNKS)
SEALED_NAMES = frozenset(f"range={s}_{e}.dbn.zst" for s, e in HOLDOUT2_RAW_CHUNKS)
STEP2_REPORTS = REPO_ROOT / "reports" / "step2"
CONDITION_PATH = VENDOR_ROOT / "condition" / f"{DATASET}_2019-04-01_2025-04-01.json"
ROLLS_DIR = VENDOR_ROOT / "rolls"
SEALED_ROOT = DATA_ROOT / "sealed"
BUILDER_FILES = ("data/step2_store.py", "data/build_bars.py")
if len(UNSEALED_NAMES) != 58 or (LAST_TRADE_DATE + timedelta(days=1)) != EMBARGO2_START:
    raise RuntimeError("the step 2 store reads the 58 chunks 2019-05..2024-02 and ends the day "
                       "before the embargo")


class Step2StoreRefused(bb.BuildRefused):
    """The store was asked to read something it must never read, or to write outside itself."""


# ------------------------------------------------------------------ paths ----
def step2_parquet_path(root: str, base: Path = STEP2_ROOT) -> Path:
    return base / root / f"ohlcv-1m_{root}_v_0_{FIRST_TRADE_DATE}_{LAST_TRADE_DATE}_step2.parquet"


def summary_path(root: str, base: Path = STEP2_REPORTS) -> Path:
    return base / f"bars_{root}.json"


def purchase_manifest_path(root: str, base: Path = STEP2_REPORTS) -> Path:
    return base / f"purchase_{root}.json"


def rolls_cache_path(root: str, rolls_dir: Path = ROLLS_DIR) -> Path:
    return rolls_dir / f"{root}_v_0_{SPAN}.jsonl"


def symbology_cache_path(root: str, rolls_dir: Path = ROLLS_DIR) -> Path:
    return rolls_dir / f"{root}_v_0_{SPAN}_symbology.json"


# ------------------------------------------------------------------ inputs ----
def expected_names(root: str) -> tuple[str, ...]:
    """``root``'s unsealed chunk names, from its first vendor-priceable month (lead ruling OC-R,
    data.pull_step2.FIRST_PRICED_MONTH) through 2024-02: 58 for a contract priced from 2019-05."""
    from data.pull_step2 import unsealed_chunks  # lazy: keeps the import graph one-way

    return tuple(f"range={s}_{e}.dbn.zst" for s, e in unsealed_chunks(root))


def input_files(root: str, manifest: Path) -> tuple[bb.InputFile, ...]:
    """The purchase manifest's unsealed files, oldest first. The manifest is data.pull_step2's."""
    payload = json.loads(Path(manifest).read_text(encoding="utf-8"))
    if payload.get("product") != root:
        raise Step2StoreRefused(f"{manifest.name} is {payload.get('product')!r}'s, not {root!r}")
    rows = sorted(payload["files"], key=lambda f: f["request_start"])
    return tuple(bb.InputFile(Path(f["path"]) if Path(f["path"]).is_absolute()
                              else REPO_ROOT / f["path"], f["sha256"], int(f["record_count"]),
                              tuple(str(i) for i in f.get("instrument_ids", []))) for f in rows)


def refuse_inputs(root: str, files: Sequence[bb.InputFile], *, sealed_roots: Sequence[Path] = (
        SEALED_ROOT,), seal_paths: Sequence[ho.HoldoutPaths] | None = None) -> None:
    """Before any file is opened: exactly the 58 unsealed chunk names, none of them sealed or
    under a sealed store, all in one product directory."""
    names = [f.path.name for f in files]
    bad = sorted(set(names) & SEALED_NAMES)
    if bad:
        raise Step2StoreRefused(f"{root}: holdout-2 / embargo chunk(s) {bad} are sealed-only; the "
                                "store never opens them")
    wanted = expected_names(root)
    if tuple(names) != wanted:
        missing = sorted(set(wanted) - set(names))
        extra = sorted(set(names) - set(wanted))
        raise Step2StoreRefused(f"{root}: inputs must be its {len(wanted)} unsealed chunks "
                                f"{wanted[0][6:16]}..2024-02 in order (missing {missing[:3]}, "
                                f"extra {extra[:3]})")
    paths = list(seal_paths) if seal_paths is not None else [seal.step2_holdout_paths(root)]
    for f in files:
        resolved = f.path.resolve()
        if any(resolved.is_relative_to(Path(s).resolve()) for s in sealed_roots):
            raise Step2StoreRefused(f"{root}: {f.path} lies under a sealed store")
        if any(ho.is_sealed_raw(f.path, p) for p in paths) or ho.is_sealed_raw(f.path):
            raise Step2StoreRefused(f"{root}: {f.path.name} is listed in a holdout manifest")
        if f.path.parent.name != f"{root}_v_0":
            raise Step2StoreRefused(f"{root}: {f.path} is not in {root}'s own directory")


def step2_spec(root: str, *, out_base: Path = STEP2_ROOT, reports_base: Path = STEP2_REPORTS,
               rolls_dir: Path = ROLLS_DIR) -> bb.ProductSpec:
    tick, text = bb.load_ticks()[root]
    group = group_of(root)
    return bb.ProductSpec(
        root=root, group=group, tick=tick,
        tick_source=f"reports/stage_e0_liquidity.json tick_size {text!r}",
        files=input_files(root, purchase_manifest_path(root, reports_base)),
        rolls_path=rolls_cache_path(root, rolls_dir),
        symbology_path=symbology_cache_path(root, rolls_dir), policy=STAGE_E_POLICIES[group],
        out=step2_parquet_path(root, out_base), first_trade_date=FIRST_TRADE_DATE,
        last_trade_date=LAST_TRADE_DATE, data_start=DATA_START, data_end=DATA_END)


# ------------------------------------------------------------------ drop ----
def drop_outside_window(raw: pd.DataFrame, cal: GroupCalendar
                        ) -> tuple[pd.DataFrame, np.ndarray, dict[str, Any]]:
    """Trade dates from ts_event alone (the group calendar, L-3 close minute), then every row
    outside FIRST_TRADE_DATE..LAST_TRADE_DATE dropped before any other column is used.
    Returns (kept rows, their trade dates, the drop log: counts and dates only)."""
    ts = raw["ts_event"].to_numpy().astype(np.int64)
    opened = open_intervals(cal, DATA_START - timedelta(days=7), DATA_END + timedelta(days=7))
    days = assign_trade_dates(opened, ts, close_minute_to_previous=True).days
    nat = np.isnat(days)
    first64, last64 = np.datetime64(FIRST_TRADE_DATE, "D"), np.datetime64(LAST_TRADE_DATE, "D")
    early = ~nat & (days < first64)
    embargo = ~nat & (days > last64)
    leak = ~nat & (days >= np.datetime64(HOLDOUT2_START, "D"))
    if leak.any() or nat.any():
        raise HoldoutLeakError(
            f"{int(leak.sum())} row(s) booked to holdout-2 or later and {int(nat.sum())} "
            "unbookable row(s) in the unsealed step 2 chunks: refused, nothing written")
    keep = ~early & ~embargo
    log = {"before_first_trade_date": bb._drops_by_date(days, early),
           "embargo_rows_dropped_unread": int(embargo.sum()),
           "embargo_trade_dates": sorted({str(d) for d in days[embargo]}),
           "rows_decoded": int(len(raw)), "rows_in_window": int(keep.sum())}
    return raw.loc[keep].reset_index(drop=True), days[keep], log


# ------------------------------------------------------------------ build ----
def build_step2_product(spec: bb.ProductSpec, cal: GroupCalendar, degraded: list[dict],
                        rolls: list, symbology: dict | None, roll_source: str, *,
                        harness_sha256: str,
                        load_bars: Callable[[list[Path]], pd.DataFrame] = load_raw_bars,
                        embedded: list[dict] | None = None,
                        seal_paths: Sequence[ho.HoldoutPaths] | None = None,
                        sealed_roots: Sequence[Path] = (SEALED_ROOT,)) -> bb.BuildResult:
    """Everything except writing. ``summary`` carries counts, dates and flags only."""
    refuse_inputs(spec.root, spec.files, sealed_roots=sealed_roots, seal_paths=seal_paths)
    summary: dict[str, Any] = {
        "product": spec.root, "group": spec.group, "continuous": spec.continuous,
        "schema": bb.OHLCV_1M, "store": "step2", "status": "refused", "refusal_causes": [],
        "window_trade_dates": [str(FIRST_TRADE_DATE), str(LAST_TRADE_DATE)],
        "data_utc": [str(DATA_START), str(DATA_END)], "harness_sha256": harness_sha256,
        "tick": {"tick": spec.tick, "tick_fixed_1e9": spec.tick_fixed, "source": spec.tick_source},
        "flatten_policy": spec.policy.as_dict(), "calendar_modules": cal.module_sha256(),
        "calendar_coverage": [str(d) for d in cal.coverage],
        "builder_files": {p: bb.sha256_file(REPO_ROOT / p) for p in BUILDER_FILES
                          if (REPO_ROOT / p).is_file()},
        "sealed_chunks_not_opened": sorted(SEALED_NAMES),
    }
    inputs, problems = bb.verify_inputs(spec)
    summary["input_files"] = inputs
    if problems:
        summary["refusal_causes"] = problems
        return bb.BuildResult(summary, None, None)
    decoded = load_bars([f.path for f in spec.files])
    problems += _record_counts(spec, decoded, summary)
    raw, days, drop_log = drop_outside_window(decoded, cal)
    del decoded
    summary["window_drops"] = drop_log
    return _build_window(spec, cal, degraded, rolls, symbology, roll_source, raw, days, summary,
                         problems, embedded)


def _record_counts(spec: bb.ProductSpec, raw: pd.DataFrame, summary: dict) -> list[str]:
    problems: list[str] = []
    per_file = raw.groupby("source_file").size().to_dict() if "source_file" in raw else {}
    for row, f in zip(summary["input_files"], spec.files, strict=True):
        row["records_loaded"] = int(per_file.get(f.path.name, 0))
        if f.record_count is not None and row["records_loaded"] != f.record_count:
            problems.append(f"{f.path.name}: {row['records_loaded']} records loaded, manifest "
                            f"{f.record_count}")
    return problems


def _window_ns(cal: GroupCalendar) -> tuple[int, int, Any]:
    """[first open of FIRST_TRADE_DATE, last close of LAST_TRADE_DATE + the close minute)."""
    opened = open_intervals(cal, FIRST_TRADE_DATE - timedelta(days=7),
                            LAST_TRADE_DATE + timedelta(days=7))
    first = [int(s) for s, d in zip(opened.starts, opened.days, strict=True)
             if d >= FIRST_TRADE_DATE]
    last = [int(e) for e, d in zip(opened.ends, opened.days, strict=True) if d == LAST_TRADE_DATE]
    if not first or not last:
        raise Step2StoreRefused(f"{cal.group}: the calendar has no session for "
                                f"{FIRST_TRADE_DATE} or {LAST_TRADE_DATE}")
    return min(first), max(last) + NS_PER_MIN, opened


def _build_window(spec: bb.ProductSpec, cal: GroupCalendar, degraded: list[dict], rolls: list,
                  symbology: dict | None, roll_source: str, raw: pd.DataFrame, days: np.ndarray,
                  summary: dict, problems: list[str], embedded: list[dict] | None
                  ) -> bb.BuildResult:
    lo_ns, hi_ns, opened = _window_ns(cal)
    c_starts, c_ends = closed_windows(opened, lo_ns, hi_ns)
    ts = raw["ts_event"].to_numpy().astype(np.int64)
    report, _ = validate_bars(raw, lo_ns, hi_ns, c_starts, c_ends, spec.tick_fixed, spec.tick)
    summary["raw_checks"] = bb._raw_checks(report, [])
    summary["raw_checks"]["grid_scale_probe"] = bb.grid_scale_probe(raw, spec.tick_fixed)
    outside = int(((ts < lo_ns) | (ts >= hi_ns)).sum())
    summary["raw_checks"]["kept_rows_outside_window_range"] = outside
    hard = list(problems) + list(report.hard_failures)
    if outside:
        hard.append("rows of the window's trade dates outside its UTC range")
    closure = in_windows(ts, c_starts, c_ends)
    boundary = assign_trade_dates(opened, ts, close_minute_to_previous=True).boundary
    summary["closure_bars"] = [
        {"ct": bb._ct_str(int(t)), "trade_date": str(d), "close_minute": bool(b)}
        for t, d, b in zip(ts[closure], days[closure], boundary[closure], strict=True)]
    summary["rolls"] = bb._roll_summary(spec, cal, opened, rolls, symbology, roll_source, raw,
                                        embedded)
    summary["calendar_check"] = bb._calendar_check(spec, cal, ts, days, hi_ns)
    if hard:
        summary["refusal_causes"] = hard
        return bb.BuildResult(summary, None, None)
    deep = [c for c in summary["closure_bars"] if not c["close_minute"]]
    if deep:
        summary["status"] = "held_for_lead"
        summary["refusal_causes"] = [
            f"{len(deep)} bars inside a scheduled closure beyond the close minute (first "
            f"{deep[0]['ct']} CT): held for the lead before building (ruling L-3)"]
        return bb.BuildResult(summary, None, None)
    return _flag(spec, cal, degraded, rolls, symbology, raw, days, lo_ns, hi_ns, opened, summary)


def _flag(spec: bb.ProductSpec, cal: GroupCalendar, degraded: list[dict], rolls: list,
          symbology: dict | None, raw: pd.DataFrame, days: np.ndarray, lo_ns: int, hi_ns: int,
          opened: Any, summary: dict) -> bb.BuildResult:
    symbols, unmapped, rule = bb._raw_symbols(spec, rolls, symbology, raw)
    no_outright = symbols == ""
    kept, kept_days = raw, days
    if symbology is not None and no_outright.any():
        kept, kept_days = raw[~no_outright].reset_index(drop=True), days[~no_outright]
        symbols = symbols[~no_outright]
    summary["drops"] = {
        **summary["window_drops"],
        "no_outright_on_bar_utc_date": {
            "total": int(no_outright.sum()) if symbology is not None else 0,
            "groups": unmapped[:200]},
        "raw_symbol_rule": rule}
    if kept.empty:
        summary["refusal_causes"] = ["no bar survives the window and raw-symbol drops"]
        return bb.BuildResult(summary, None, None)
    c_starts, c_ends = closed_windows(opened, lo_ns, hi_ns)
    report, gap_before = validate_bars(kept, lo_ns, hi_ns, c_starts, c_ends, spec.tick_fixed,
                                       spec.tick)
    summary["validation"] = {**bb._raw_checks(report, [bb._ct_str(t) for t in
                                                      report.bars_in_scheduled_closure]),
                             **bb._gap_summary(report), "hard_failures": report.hard_failures}
    if report.hard_failures:
        summary["refusal_causes"] = report.hard_failures
        return bb.BuildResult(summary, None, None)
    splice_days = {date.fromisoformat(s) for s in summary["rolls"]["splice_trade_dates"]}
    degraded_dates = sorted({str(d["date"]) for d in degraded})
    frame = bb.flag_frame(kept, cal, spec.policy, kept_days, c_starts, c_ends, gap_before,
                          set(degraded_dates), symbols, splice_days)
    trade_dates = sorted(set(frame["trade_date"]))
    refuse_non_confirmation_dates(trade_dates, "Stage E step 2 bar store")
    if trade_dates[0] < FIRST_TRADE_DATE or trade_dates[-1] > LAST_TRADE_DATE:
        raise Step2StoreRefused(f"trade dates {trade_dates[0]}..{trade_dates[-1]} outside "
                                f"{FIRST_TRADE_DATE}..{LAST_TRADE_DATE}")
    td_iso = {d.isoformat() for d in trade_dates}
    summary.update({
        "status": "built", "refusal_causes": [], "bars": len(frame),
        "trade_dates": len(trade_dates), "first_trade_date": str(trade_dates[0]),
        "last_trade_date": str(trade_dates[-1]),
        "booked_forward_sessions": [{"holiday": str(b), "trade_date": str(t)} for b, t in
                                    sorted(cal.booked_forward.items()) if t.isoformat() in td_iso],
        "degraded": {"condition_file": bb._rel(CONDITION_PATH),
                     "degraded_utc_dates": degraded_dates,
                     "on_store_trade_dates": sorted(td_iso & set(degraded_dates)),
                     "bars_flagged": int(frame["vendor_degraded_day"].sum())},
        "flag_counts": {c: int(frame[c].sum()) for c in (
            "in_flatten_window", "in_no_new_positions_window", "in_scheduled_closure",
            "is_roll_session", "vendor_degraded_day")}
        | {"bars_with_gap_before": int((frame["gap_before_minutes"] > 0).sum())},
    })
    return bb.BuildResult(summary, frame, _metadata(spec, rolls, summary))


def _metadata(spec: bb.ProductSpec, rolls: list, summary: dict) -> dict:
    return {
        "source": f"Databento {DATASET} {spec.continuous} {bb.OHLCV_1M}, unadjusted prices; "
                  f"Stage E step 2 store, trade dates {FIRST_TRADE_DATE}..{LAST_TRADE_DATE}",
        "stage": "E.2b Task 4 (data/step2_store.py)", "store": "step2",
        "flags_doc": "see data/bars.py (column meanings) and data/group_session.py (group "
                     "sessions, flatten policy)",
        "flatten_rule": spec.policy.as_dict(), "group": spec.group,
        "calendar_modules": summary["calendar_modules"], "builder_files": summary["builder_files"],
        "input_files": [{"name": r["name"], "sha256": r["sha256"]} for r in summary["input_files"]],
        "tick": summary["tick"], "rolls": [asdict(r) for r in rolls],
        "rolls_source": summary["rolls"]["source"],
        "splice_trade_dates": summary["rolls"]["splice_trade_dates"],
        "roll_blackout_dates": summary["rolls"]["roll_blackout_dates"],
        "degraded_vendor_days": summary["degraded"]["degraded_utc_dates"],
        "degraded_on_store_trade_dates": summary["degraded"]["on_store_trade_dates"],
        "raw_symbol_rule": summary["drops"]["raw_symbol_rule"],
        "drops": {k: v for k, v in summary["drops"].items() if k != "raw_symbol_rule"},
        "validation": {"rows": summary["bars"], "raw_hard_failures": [],
                       "gap_runs_total": summary["validation"]["gap_runs_total"],
                       "gap_runs_by_length": summary["validation"]["gap_runs_by_length"]},
        "trade_date_range": [summary["first_trade_date"], summary["last_trade_date"]],
        "calendar_check_passed": summary["calendar_check"].get("passed"),
        "day_session_rule": bb.DAY_SESSION_RULE,
        "booked_forward_sessions": summary.get("booked_forward_sessions", []),
        "purchase_manifest": summary.get("purchase_manifest"),
        "sealed_chunks_not_opened": summary["sealed_chunks_not_opened"],
        "harness_sha256": summary["harness_sha256"],
    }


# ------------------------------------------------------------------- run ----
def run_product(root: str, *, expected_harness_sha256: str, out_base: Path = STEP2_ROOT,
                reports_base: Path = STEP2_REPORTS, rolls_dir: Path = ROLLS_DIR,
                condition: Path = CONDITION_PATH,
                client_factory: Callable[[], Any] | None = None,
                log: Callable[[str], None] = print) -> dict:
    """One product end to end: the harness preflight FIRST (before any purchased file is read;
    its sha256 goes into the summary and the parquet metadata), then spec, rolls, build, write
    (never over an existing file)."""
    from screening import harness_freeze  # lazy: keeps the module importable without it

    harness_sha256 = harness_freeze.preflight(expected_harness_sha256)
    spec = step2_spec(root, out_base=out_base, reports_base=reports_base, rolls_dir=rolls_dir)
    refuse_inputs(root, spec.files)  # before the symbology fetch or any file is opened
    if spec.out.exists():
        raise Step2StoreRefused(f"REFUSED: {spec.out} already exists; nothing is overwritten")
    cal = load_group_calendar(spec.group)
    rolls, symbology, source = bb.ensure_rolls(spec, client_factory, log)
    embedded = bb.embedded_intervals([f.path for f in spec.files], spec.continuous)
    result = build_step2_product(spec, cal, bb.degraded_days(condition), rolls, symbology,
                                 source, harness_sha256=harness_sha256, embedded=embedded)
    manifest = purchase_manifest_path(root, reports_base)
    result.summary["purchase_manifest"] = {"path": bb._rel(manifest),
                                           "sha256": bb.sha256_file(manifest)}
    if result.frame is not None and result.meta is not None:
        result.meta["purchase_manifest"] = result.summary["purchase_manifest"]
        result.summary["parquet"] = {"path": bb._rel(spec.out),
                                     "sha256": bb.write_parquet(result.frame, result.meta,
                                                                spec.out)}
    out = summary_path(root, reports_base)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result.summary, indent=1, default=str) + "\n", encoding="utf-8")
    log(f"{root}: {result.summary['status']} {result.summary.get('bars', 0)} bars")
    return result.summary


def _client_factory() -> Any:  # noqa: ANN401 — run session only, never in tests
    """A Databento client for the free symbology.resolve calls of ``bb.ensure_rolls``."""
    import databento

    from data.config import require_databento_key

    return databento.Historical(require_databento_key())


def cli(argv: Sequence[str] | None = None, *,
        runner: Callable[..., dict] = run_product) -> int:
    from screening import harness_freeze

    parser = argparse.ArgumentParser(prog="python -m data.step2_store")
    parser.add_argument("--products", nargs="+", required=True)
    parser.add_argument("--harness-sha256", required=True)
    args = parser.parse_args(argv)
    try:
        harness_freeze.preflight(args.harness_sha256)  # before any file is read
        status = 0
        for root in args.products:  # each product runs the preflight again itself
            summary = runner(root, expected_harness_sha256=args.harness_sha256,
                             client_factory=_client_factory)
            status |= 0 if summary.get("status") == "built" else 1
    except harness_freeze.HarnessFreezeError as exc:
        print(f"REFUSED before any file was read: {exc}", file=sys.stderr)
        return 2
    return status


if __name__ == "__main__":
    sys.exit(cli())
