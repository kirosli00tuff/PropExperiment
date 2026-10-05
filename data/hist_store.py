"""Stage E.14 (harness v10): the hist bar stores of plans "es2011" (C2) and "ext2010" (C1).

    uv run python -m data.hist_store --plan es2011 --harness-sha256 <sha256>
    uv run python -m data.hist_store --plan ext2010 --products NG ZC --harness-sha256 <sha256>

One parquet per (plan, root) with every trade date of the plan's window the root has bars on:
es2011 ES 2011-05-02..2019-04-30 (2011-05-02 gives the first date's prior close); ext2010 NG,
NQ, ZN, 6E, GC and ZC 2010-06-07..2019-04-30 (rulings C5 and C6). Layout:
  HIST_ROOT/<plan>/<ROOT>/ohlcv-1m_<ROOT>_v_0_<first>_<last>_<plan>.parquet   (0444, os.link)
  reports/hist/bars_<ROOT>_<plan>.json                                       (the summary)
with HIST_ROOT = data/processed_hist (its own base, in harness_freeze.DATA_SUBDIRS).

The per-root logic is data/build_bars.py's and data/step2_store.py's (both unchanged; their
helpers are called, never edited): the group flatten policy, rolls from the free symbology of
<ROOT>.v.0 over the plan's data window, the D.1f raw-symbol rule, the hard checks, the close-minute
rule L-3, flag_frame's columns and the read-only parquet writer. What differs, in order:
1. Inputs: exactly the plan's chunks for the root, in order, listed in the plan's purchase
   manifest reports/hist/purchase_<ROOT>_<plan>.json (data.pull_hist), each verified by sha256
   and record count. Anything else, a file under a sealed store or in a holdout manifest, or a
   file outside the root's own directory is refused BEFORE any file is opened.
2. The calendar is the hist group calendar (data.hist_calendar, data/calendars/hist2010/), and the
   root must be one of its products. The free symbology and the dataset condition list must be on
   disk (the buy run fetches them); the store never calls the vendor.
3. Right after decoding, every row gets its trade date from ts_event alone; rows outside the plan's
   trade dates, and rows booked to an UNSOURCED calendar date (C1 ruling C12, C2 section 3), are
   dropped and counted before any check or flag reads a price. A row booked to no trade date the
   calendar can show, or to a holdout trade date, raises.
4. Bars inside a scheduled closure beyond the close minute are KEPT and FLAGGED automatically
   (in_scheduled_closure; v9's keep-and-flag principle, fixed in v10 before any data exists),
   counted in the summary, never held. Close-minute bars follow L-3 as before.
5. The written frame is checked again: every trade date inside the plan's window, none unsourced.
The build prints counts only (rows, trade dates, excluded dates by reason, rolls), never a price.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import asdict
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from data import build_bars as bb
from data import holdout as ho
from data import step2_store as s2
from data.bars import load_raw_bars
from data.config import DATA_ROOT, HIST_ROOT, REPO_ROOT
from data.group_session import (
    NS_PER_MIN,
    STAGE_E_POLICIES,
    CalendarNotReady,
    assign_trade_dates,
    closed_windows,
    group_of,
    open_intervals,
)
from data.hist_calendar import HIST_CALENDAR_DIR, HistGroupCalendar, load_hist_group_calendar
from data.pull_hist import (
    CONDITION_DIR,
    HIST_REPORTS,
    ROLLS_DIR,
    HistPlan,
    condition_path,
    get_plan,
    plan_chunks,
    purchase_manifest_path,
    rolls_cache_path,
    symbology_cache_path,
)
from data.pull_universe import target_path
from data.research_bars import HoldoutLeakError
from data.stage_e_bars import forbidden_class
from data.validate import in_windows, validate_bars, validate_calendar_group

SEALED_ROOT = DATA_ROOT / "sealed"
BUILDER_FILES = ("data/hist_store.py", "data/hist_calendar.py", "data/pull_hist.py",
                 "data/step2_store.py", "data/build_bars.py")
CLOSURE_POLICY = ("keep_and_flag: bars inside a scheduled closure beyond the close minute are "
                  "kept with their values unchanged and flagged in_scheduled_closure (harness "
                  "v10, automatic)")
SAMPLE = 200  # list lengths in the summary (timestamps and dates only)


class HistStoreRefused(bb.BuildRefused):
    """The store was asked to read something it must never read, or to write outside itself."""


# ------------------------------------------------------------------ paths ----
def hist_parquet_path(root: str, plan: str, base: Path = HIST_ROOT) -> Path:
    p = get_plan(plan)
    return Path(base) / plan / root / (f"ohlcv-1m_{root}_v_0_{p.first_trade_date}_"
                                       f"{p.last_trade_date}_{plan}.parquet")


def summary_path(root: str, plan: str, base: Path = HIST_REPORTS) -> Path:
    return Path(base) / f"bars_{root}_{plan}.json"


# ------------------------------------------------------------------ inputs ----
def expected_names(root: str, plan: HistPlan) -> tuple[str, ...]:
    return tuple(target_path(c.params, Path("v")).name for c in plan_chunks(plan, (root,)))


def input_files(root: str, plan: HistPlan, manifest: Path) -> tuple[bb.InputFile, ...]:
    """The plan's purchase manifest's files for ``root``, oldest first."""
    if not Path(manifest).is_file():
        raise HistStoreRefused(f"{root} {plan.name}: purchase manifest {Path(manifest).name} "
                               "does not exist")
    payload = json.loads(Path(manifest).read_text(encoding="utf-8"))
    if payload.get("product") != root or payload.get("plan") != plan.name:
        raise HistStoreRefused(f"{Path(manifest).name} is {payload.get('product')!r} plan "
                               f"{payload.get('plan')!r}, not {root} {plan.name}")
    rows = sorted(payload["files"], key=lambda f: f["request_start"])
    return tuple(bb.InputFile(Path(f["path"]) if Path(f["path"]).is_absolute()
                              else REPO_ROOT / f["path"], f["sha256"], int(f["record_count"]),
                              tuple(str(i) for i in f.get("instrument_ids", []))) for f in rows)


def refuse_inputs(root: str, plan: HistPlan, files: Sequence[bb.InputFile], *,
                  sealed_roots: Sequence[Path] = (SEALED_ROOT,)) -> None:
    """Before any file is opened: exactly the plan's chunk names for the root, in order, all in
    the root's own directory, none under a sealed store or listed in a holdout manifest."""
    if root not in plan.roots:
        raise HistStoreRefused(f"{root!r} is not a root of plan {plan.name}")
    names = tuple(f.path.name for f in files)
    wanted = expected_names(root, plan)
    if names != wanted:
        missing = sorted(set(wanted) - set(names))
        extra = sorted(set(names) - set(wanted))
        raise HistStoreRefused(f"{root} {plan.name}: inputs must be its {len(wanted)} plan "
                               f"chunks in order (missing {missing[:3]}, extra {extra[:3]})")
    for f in files:
        resolved = f.path.resolve()
        if any(resolved.is_relative_to(Path(s).resolve()) for s in sealed_roots):
            raise HistStoreRefused(f"{root}: {f.path} lies under a sealed store")
        if ho.is_sealed_raw(f.path):
            raise HistStoreRefused(f"{root}: {f.path.name} is listed in a holdout manifest")
        if f.path.parent.name != f"{root}_v_0":
            raise HistStoreRefused(f"{root}: {f.path} is not in {root}'s own directory")


def hist_spec(root: str, plan: HistPlan, *, out_base: Path = HIST_ROOT,
              reports_base: Path = HIST_REPORTS, rolls_dir: Path = ROLLS_DIR) -> bb.ProductSpec:
    tick, text = bb.load_ticks()[root]
    group = group_of(root)
    return bb.ProductSpec(
        root=root, group=group, tick=tick,
        tick_source=f"reports/stage_e0_liquidity.json tick_size {text!r}",
        files=input_files(root, plan, purchase_manifest_path(root, plan.name, reports_base)),
        rolls_path=rolls_cache_path(root, plan, rolls_dir),
        symbology_path=symbology_cache_path(root, plan, rolls_dir),
        policy=STAGE_E_POLICIES[group], out=hist_parquet_path(root, plan.name, out_base),
        first_trade_date=plan.first_trade_date, last_trade_date=plan.last_trade_date,
        data_start=plan.data_start, data_end=plan.data_end)


# ------------------------------------------------------------------ drop ----
def drop_outside_window(raw: pd.DataFrame, cal: HistGroupCalendar, spec: bb.ProductSpec
                        ) -> tuple[pd.DataFrame, np.ndarray, dict[str, Any]]:
    """Trade dates from ts_event alone (the hist calendar, L-3 close minute), then every row
    outside the plan's trade dates or on an unsourced date dropped before any other column is
    used. Returns (kept rows, their trade dates, the drop log: counts and dates only)."""
    ts = raw["ts_event"].to_numpy().astype(np.int64)
    opened = open_intervals(cal, spec.data_start - timedelta(days=7),
                            spec.data_end + timedelta(days=7))
    days = assign_trade_dates(opened, ts, close_minute_to_previous=True).days
    nat = np.isnat(days)
    if nat.any():
        raise HistStoreRefused(f"{int(nat.sum())} row(s) book to no trade date the {cal.group} "
                               "hist calendar can show: refused, nothing written")
    leaked = sorted({str(d) for d in np.unique(days) if forbidden_class(d.astype(object))})
    if leaked:
        raise HoldoutLeakError(f"rows booked to holdout trade dates {leaked[:3]}: refused")
    first64 = np.datetime64(spec.first_trade_date, "D")
    last64 = np.datetime64(spec.last_trade_date, "D")
    early, late = days < first64, days > last64
    unsourced_days = np.array([np.datetime64(d, "D") for d in sorted(cal.unsourced)],
                              dtype="datetime64[D]")
    unsourced = ~early & ~late & np.isin(days, unsourced_days)
    keep = ~early & ~late & ~unsourced
    log = {"rows_decoded": int(len(raw)),
           "before_first_trade_date": bb._drops_by_date(days, early),
           "after_last_trade_date_rows_dropped_unread": int(late.sum()),
           "after_last_trade_dates": sorted({str(d) for d in days[late]}),
           "unsourced_rows_dropped_unread": int(unsourced.sum()),
           "unsourced_trade_dates_with_rows": bb._drops_by_date(days, unsourced),
           "rows_in_window": int(keep.sum())}
    return raw.loc[keep].reset_index(drop=True), days[keep], log


def _window_ns(cal: HistGroupCalendar, spec: bb.ProductSpec) -> tuple[int, int, Any]:
    """[first open of the first trade date, last close of the last trade date + 1 minute)."""
    first, last = spec.first_trade_date, spec.last_trade_date
    opened = open_intervals(cal, first - timedelta(days=7), last + timedelta(days=7))
    starts = [int(s) for s, d in zip(opened.starts, opened.days, strict=True) if d >= first]
    ends = [int(e) for e, d in zip(opened.ends, opened.days, strict=True) if d == last]
    if not starts or not ends:
        raise HistStoreRefused(f"{cal.group}: the hist calendar has no session for {first} or "
                               f"{last}")
    return min(starts), max(ends) + NS_PER_MIN, opened


def _unsourced_in_window(cal: HistGroupCalendar, spec: bb.ProductSpec) -> dict[str, Any]:
    first, last = spec.first_trade_date, spec.last_trade_date
    days = [first + timedelta(days=n) for n in range((last - first).days + 1)]
    trade = [d for d in days if cal.is_trade_date(d)]
    unsourced = [d for d in trade if d in cal.unsourced]
    reasons = Counter(r for d in unsourced for r in cal.unsourced_reasons.get(d, ()))
    return {"calendar_trade_dates": len(trade), "unsourced_trade_dates": len(unsourced),
            "unsourced_share": (len(unsourced) / len(trade)) if trade else None,
            "unsourced_by_reason": dict(sorted(reasons.items())),
            "unsourced_dates": [str(d) for d in unsourced]}


# ------------------------------------------------------------------ build ----
def build_hist_product(spec: bb.ProductSpec, plan: HistPlan, cal: HistGroupCalendar,
                       degraded: list[dict], rolls: list, symbology: dict | None,
                       roll_source: str, *, harness_sha256: str,
                       load_bars: Callable[[list[Path]], pd.DataFrame] = load_raw_bars,
                       embedded: list[dict] | None = None,
                       sealed_roots: Sequence[Path] = (SEALED_ROOT,),
                       condition_file: Path | None = None) -> bb.BuildResult:
    """Everything except writing. ``summary`` carries counts, dates and flags only.
    ``condition_file``: where ``degraded`` came from (recorded only)."""
    refuse_inputs(spec.root, plan, spec.files, sealed_roots=sealed_roots)
    summary: dict[str, Any] = {
        "condition_file": None if condition_file is None else bb._rel(Path(condition_file)),
        "product": spec.root, "group": spec.group, "continuous": spec.continuous,
        "schema": bb.OHLCV_1M, "store": f"hist:{plan.name}", "plan": plan.name,
        "test": plan.test, "status": "refused", "refusal_causes": [],
        "window_trade_dates": [str(spec.first_trade_date), str(spec.last_trade_date)],
        "data_utc": [str(spec.data_start), str(spec.data_end)], "harness_sha256": harness_sha256,
        "tick": {"tick": spec.tick, "tick_fixed_1e9": spec.tick_fixed, "source": spec.tick_source},
        "flatten_policy": spec.policy.as_dict(), "calendar_modules": cal.module_sha256(),
        "hist_calendar": cal.record(), "calendar_coverage": [str(d) for d in cal.coverage],
        "calendar_unsourced": _unsourced_in_window(cal, spec), "closure_policy": CLOSURE_POLICY,
        "builder_files": {p: bb.sha256_file(REPO_ROOT / p) for p in BUILDER_FILES
                          if (REPO_ROOT / p).is_file()},
    }
    inputs, problems = bb.verify_inputs(spec)
    summary["input_files"] = inputs
    if problems:
        summary["refusal_causes"] = problems
        return bb.BuildResult(summary, None, None)
    decoded = load_bars([f.path for f in spec.files])
    problems += s2._record_counts(spec, decoded, summary)
    raw, days, drop_log = drop_outside_window(decoded, cal, spec)
    del decoded
    summary["window_drops"] = drop_log
    return _build_window(spec, plan, cal, degraded, rolls, symbology, roll_source, raw, days,
                         summary, problems, embedded)


def _closure_summary(ts: np.ndarray, days: np.ndarray, closure: np.ndarray,
                     boundary: np.ndarray) -> dict[str, Any]:
    deep = closure & ~boundary
    return {"total": int(closure.sum()), "close_minute": int((closure & boundary).sum()),
            "beyond_close_minute_kept_and_flagged": int(deep.sum()),
            "beyond_close_minute_by_trade_date": bb._drops_by_date(days, deep),
            "sample": [{"ct": bb._ct_str(int(t)), "trade_date": str(d), "close_minute": bool(b)}
                       for t, d, b in zip(ts[closure][:SAMPLE], days[closure][:SAMPLE],
                                          boundary[closure][:SAMPLE], strict=True)]}


def _calendar_check(spec: bb.ProductSpec, cal: HistGroupCalendar, ts: np.ndarray,
                    days: np.ndarray, data_end_ns: int) -> dict:
    """data.validate's step-4b check on the hist calendar's years (reported, never a gate)."""
    try:
        closes = cal.day_session_close(spec.root)
        check = validate_calendar_group(
            ts, cal, spec.first_trade_date, spec.last_trade_date, closes,
            data_end_ns=data_end_ns,
            entry_years=(spec.first_trade_date.year, spec.last_trade_date.year))
    except Exception as exc:  # noqa: BLE001 — reported, the build does not depend on it
        return {"error": f"{type(exc).__name__}: {exc}"}
    out = check.as_dict()
    out["day_session_close_ct"] = {str(k): v.strftime("%H:%M") for k, v in closes.items()}
    return out


def _build_window(spec: bb.ProductSpec, plan: HistPlan, cal: HistGroupCalendar,
                  degraded: list[dict], rolls: list, symbology: dict | None, roll_source: str,
                  raw: pd.DataFrame, days: np.ndarray, summary: dict, problems: list[str],
                  embedded: list[dict] | None) -> bb.BuildResult:
    lo_ns, hi_ns, opened = _window_ns(cal, spec)
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
    summary["closure_bars"] = _closure_summary(ts, days, closure, boundary)
    summary["rolls"] = bb._roll_summary(spec, cal, opened, rolls, symbology, roll_source, raw,
                                        embedded)
    summary["calendar_check"] = _calendar_check(spec, cal, ts, days, hi_ns)
    if hard:
        summary["refusal_causes"] = hard
        return bb.BuildResult(summary, None, None)
    return _flag(spec, plan, cal, degraded, rolls, symbology, raw, days, lo_ns, hi_ns, opened,
                 summary)


def _flag(spec: bb.ProductSpec, plan: HistPlan, cal: HistGroupCalendar, degraded: list[dict],
          rolls: list, symbology: dict | None, raw: pd.DataFrame, days: np.ndarray, lo_ns: int,
          hi_ns: int, opened: Any, summary: dict) -> bb.BuildResult:
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
            "groups": unmapped[:SAMPLE]},
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
    bad = [d for d in trade_dates if not spec.first_trade_date <= d <= spec.last_trade_date
           or d in cal.unsourced or forbidden_class(d)]
    if bad:
        raise HistStoreRefused(f"{len(bad)} written trade date(s) outside "
                               f"{spec.first_trade_date}..{spec.last_trade_date} or unsourced "
                               f"(first {bad[0]})")
    td_iso = {d.isoformat() for d in trade_dates}
    summary.update({
        "status": "built", "refusal_causes": [], "bars": len(frame),
        "trade_dates": len(trade_dates), "first_trade_date": str(trade_dates[0]),
        "last_trade_date": str(trade_dates[-1]),
        "degraded": {"condition_file": summary["condition_file"],
                     "degraded_utc_dates": degraded_dates,
                     "on_store_trade_dates": sorted(td_iso & set(degraded_dates)),
                     "bars_flagged": int(frame["vendor_degraded_day"].sum())},
        "flag_counts": {c: int(frame[c].sum()) for c in (
            "in_flatten_window", "in_no_new_positions_window", "in_scheduled_closure",
            "is_roll_session", "vendor_degraded_day")}
        | {"bars_with_gap_before": int((frame["gap_before_minutes"] > 0).sum())},
    })
    return bb.BuildResult(summary, frame, _metadata(spec, plan, rolls, summary))


def _metadata(spec: bb.ProductSpec, plan: HistPlan, rolls: list, summary: dict) -> dict:
    return {
        "source": f"Databento GLBX.MDP3 {spec.continuous} {bb.OHLCV_1M}, unadjusted prices; "
                  f"Stage E.14 hist store {plan.name}, trade dates {spec.first_trade_date}.."
                  f"{spec.last_trade_date}",
        "stage": "E.14 (data/hist_store.py, harness v10)", "store": f"hist:{plan.name}",
        "plan": plan.name, "test": plan.test,
        "flags_doc": "see data/bars.py (column meanings) and data/group_session.py (group "
                     "sessions, flatten policy)",
        "flatten_rule": spec.policy.as_dict(), "group": spec.group,
        "calendar_modules": summary["calendar_modules"],
        "hist_calendar": summary["hist_calendar"], "builder_files": summary["builder_files"],
        "input_files": [{"name": r["name"], "sha256": r["sha256"]} for r in summary["input_files"]],
        "tick": summary["tick"], "rolls": [asdict(r) for r in rolls],
        "rolls_source": summary["rolls"]["source"],
        "splice_trade_dates": summary["rolls"]["splice_trade_dates"],
        "roll_blackout_dates": summary["rolls"]["roll_blackout_dates"],
        "degraded_vendor_days": summary["degraded"]["degraded_utc_dates"],
        "degraded_on_store_trade_dates": summary["degraded"]["on_store_trade_dates"],
        "raw_symbol_rule": summary["drops"]["raw_symbol_rule"],
        "drops": {k: v for k, v in summary["drops"].items() if k != "raw_symbol_rule"},
        "closure_policy": CLOSURE_POLICY,
        "closure_bars_kept_and_flagged": summary["closure_bars"][
            "beyond_close_minute_kept_and_flagged"],
        "calendar_unsourced": {k: v for k, v in summary["calendar_unsourced"].items()
                               if k != "unsourced_dates"},
        "validation": {"rows": summary["bars"], "raw_hard_failures": [],
                       "gap_runs_total": summary["validation"]["gap_runs_total"],
                       "gap_runs_by_length": summary["validation"]["gap_runs_by_length"]},
        "trade_date_range": [summary["first_trade_date"], summary["last_trade_date"]],
        "calendar_check_passed": summary["calendar_check"].get("passed"),
        "day_session_rule": bb.DAY_SESSION_RULE,
        "purchase_manifest": summary.get("purchase_manifest"),
        "harness_sha256": summary["harness_sha256"],
    }


# ------------------------------------------------------------------- run ----
def _require_file(path: Path, what: str, root: str) -> Path:
    if not Path(path).is_file():
        raise HistStoreRefused(f"{root}: {what} {Path(path).name} is missing (the buy run "
                               "fetches it, free; the store never calls the vendor)")
    return Path(path)


def run_product(root: str, plan_name: str, *, expected_harness_sha256: str,
                out_base: Path = HIST_ROOT, reports_base: Path = HIST_REPORTS,
                rolls_dir: Path = ROLLS_DIR, condition_dir: Path = CONDITION_DIR,
                calendar_base: Path = HIST_CALENDAR_DIR,
                log: Callable[[str], None] = print) -> dict:
    """One root end to end: the harness preflight FIRST, then the inputs (refused before any
    file is opened), the calendar, the cached metadata, build, write (never over a file)."""
    from screening import harness_freeze  # lazy: keeps the module importable without it

    harness_sha256 = harness_freeze.preflight(expected_harness_sha256)
    plan = get_plan(plan_name)
    if root not in plan.roots:
        raise HistStoreRefused(f"{root!r} is not a root of plan {plan.name}")
    spec = hist_spec(root, plan, out_base=out_base, reports_base=reports_base,
                     rolls_dir=rolls_dir)
    refuse_inputs(root, plan, spec.files)
    if spec.out.exists():
        raise HistStoreRefused(f"REFUSED: {spec.out} already exists; nothing is overwritten")
    cal = load_hist_group_calendar(spec.group, base=calendar_base)
    if root not in cal.products:
        raise HistStoreRefused(f"{root} is not a product of the {spec.group} hist calendar")
    condition = _require_file(condition_path(plan, condition_dir), "condition list", root)
    _require_file(spec.symbology_path, "symbology", root)
    rolls, symbology, source = bb.ensure_rolls(spec, None, log)
    if symbology is None:
        raise HistStoreRefused(f"{root}: rolls need the cached symbology ({source})")
    embedded = bb.embedded_intervals([f.path for f in spec.files], spec.continuous)
    result = build_hist_product(spec, plan, cal, bb.degraded_days(condition), rolls, symbology,
                                source, harness_sha256=harness_sha256, embedded=embedded,
                                condition_file=condition)
    manifest = purchase_manifest_path(root, plan.name, reports_base)
    result.summary["purchase_manifest"] = {"path": bb._rel(manifest),
                                           "sha256": bb.sha256_file(manifest)}
    result.summary["metadata_files"] = {
        "condition": {"path": bb._rel(condition), "sha256": bb.sha256_file(condition)},
        "symbology": {"path": bb._rel(spec.symbology_path),
                      "sha256": bb.sha256_file(spec.symbology_path)}}
    if result.frame is not None and result.meta is not None:
        result.meta["purchase_manifest"] = result.summary["purchase_manifest"]
        result.meta["metadata_files"] = result.summary["metadata_files"]
        result.summary["parquet"] = {"path": bb._rel(spec.out),
                                     "sha256": bb.write_parquet(result.frame, result.meta,
                                                                spec.out)}
    out = summary_path(root, plan.name, reports_base)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result.summary, indent=1, default=str) + "\n", encoding="utf-8")
    for line in count_lines(result.summary):
        log(line)
    return result.summary


def count_lines(summary: dict) -> list[str]:
    """What the build prints: counts only (rows, trade dates, excluded dates by reason, rolls)."""
    drops = summary.get("window_drops", {})
    unsourced = summary.get("calendar_unsourced", {})
    rolls = summary.get("rolls", {})
    closure = summary.get("closure_bars", {})
    before = sum(drops.get("before_first_trade_date", {}).values())
    kept_flagged = closure.get("beyond_close_minute_kept_and_flagged")
    head = f"{summary['product']} {summary['plan']}: {summary['status']}"
    if summary["status"] != "built":
        return [head, *[f"  cause: {c}" for c in summary.get("refusal_causes", [])]]
    return [head,
            f"  rows decoded {drops.get('rows_decoded')}, in window {drops.get('rows_in_window')}"
            f", written {summary.get('bars')}; trade dates {summary.get('trade_dates')} "
            f"({summary.get('first_trade_date')}..{summary.get('last_trade_date')})",
            f"  dropped unread: before the window {before} rows, after it"
            f" {drops.get('after_last_trade_date_rows_dropped_unread')} rows, on "
            f"unsourced dates {drops.get('unsourced_rows_dropped_unread')} rows",
            f"  calendar: {unsourced.get('calendar_trade_dates')} trade dates, "
            f"{unsourced.get('unsourced_trade_dates')} unsourced "
            f"{unsourced.get('unsourced_by_reason')}",
            f"  rolls: {len(rolls.get('splice_trade_dates', []))} splices, "
            f"{len(rolls.get('roll_blackout_dates_in_window', []))} blackout dates in window",
            f"  closure bars kept and flagged: {kept_flagged}"
            f" (close-minute bars {closure.get('close_minute')})"]


def cli(argv: Sequence[str] | None = None, *,
        runner: Callable[..., dict] = run_product) -> int:
    from screening import harness_freeze

    parser = argparse.ArgumentParser(prog="python -m data.hist_store")
    parser.add_argument("--plan", required=True, choices=("es2011", "ext2010"))
    parser.add_argument("--products", nargs="+")
    parser.add_argument("--harness-sha256", required=True)
    args = parser.parse_args(argv)
    try:
        harness_freeze.preflight(args.harness_sha256)  # before any file is read
        roots = args.products or list(get_plan(args.plan).roots)
        status = 0
        for root in roots:  # each root runs the preflight again itself
            summary = runner(root, args.plan, expected_harness_sha256=args.harness_sha256)
            status |= 0 if summary.get("status") == "built" else 1
    except (harness_freeze.HarnessFreezeError, bb.BuildRefused, CalendarNotReady,
            HoldoutLeakError, OSError, ValueError, KeyError) as exc:
        print(f"REFUSED ({type(exc).__name__}): {exc}", file=sys.stderr)
        return 2
    return status


if __name__ == "__main__":
    sys.exit(cli())
