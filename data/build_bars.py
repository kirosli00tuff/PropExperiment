"""Stage E.2a Task 7: research-window bar builds for the 45 admissible contracts (design D11.4).

    uv run python -m data.build_bars --products MNQ NQ      # one subprocess per product
    uv run python -m data.build_bars --group equity         # every admissible product of a group
    uv run python -m data.build_bars --probe ZN             # time the 2025-04 chunk (tmp output)
    uv run python -m data.build_bars --calendar-report      # classify the calendar bar checks
    uv run python -m data.build_bars --mes-regression       # MES through this path, into tmp

The MES template (data/build_mes_bars.py main) generalized to a group calendar
(data.group_session). Per product, in order: verify every input file's sha256 against the
step 1 purchase manifest (reports/stage_e1_purchase.json; a mismatch stops that product) ->
rolls from the cached symbology.resolve of <ROOT>.v.0 (free metadata; fetched once, never
rewritten) -> load the 15 ohlcv-1m files (data.bars.load_raw_bars) and check each file's row
count against the manifest -> hard checks on the raw bars (ordering, duplicates, OHLC
consistency, prices off the product's tick grid, negative volume, bars inside a scheduled
closure of the group calendar; gap runs reported) -> trade dates from the group calendar ->
drops, each counted by cause: trade dates outside 2025-04-01..2026-06-19 (the files'
2026-06-20/21 tail, weekend trading assigned to 2026-06-22), bars past the calendar's coverage,
bars whose instrument maps to no outright of the product on their UTC date (the D.1f rule) ->
the kept bars re-validated (gap_before_minutes) -> MES's flag columns (group flatten policy of
D9.1) -> the research-row re-check -> the parquet, written read-only, never over an existing file.

A contract failing a hard check is reported with its cause and left unbuilt; no check is loosened
and nothing is patched. The first trade date's evening before 2025-04-01 00:00 UTC is not in the
files: as in MES's research build, 2025-04-01 is kept as a partial trade date and the
expected-minute grid starts at 2025-04-01 00:00 UTC, so those minutes are neither expected nor
gaps. From research-window data this module computes bars, their validation and calendar checks
only: no return, volatility, volume or coverage statistic and no price summary.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from data.adapter import (
    RollBoundary,
    boundaries_from_intervals,
    read_rolls,
    write_rolls,
)
from data.bars import (
    PRICE_SCALE,
    instrument_raw_symbols,
    load_raw_bars,
    outright_pattern,
    raw_symbols_on_bar_dates,
)
from data.config import DATASET, PROCESSED_ROOT, REPO_ROOT, VENDOR_ROOT
from data.group_session import (
    STAGE_E_POLICIES,
    FlattenPolicy,
    GroupCalendar,
    OpenIntervals,
    assign_trade_dates,
    closed_windows,
    early_halt_labels,
    flatten_masks,
    group_of,
    open_intervals,
    roll_blackout,
    sha256_file,
    trade_date_of_instant,
    utc_midnight_ns,
)
from data.research_bars import RESEARCH, RESEARCH_EMBARGO, refuse_dates_outside
from data.session import ct_ns
from data.validate import in_windows, validate_bars, validate_calendar_group

RESEARCH_FIRST_TRADE_DATE = date(2025, 4, 1)
RESEARCH_LAST_TRADE_DATE = date(2026, 6, 19)
DATA_START_UTC = date(2025, 4, 1)
DATA_END_UTC = date(2026, 6, 21)  # exclusive: the step 1 files end at 2026-06-21 00:00 UTC
SPAN = f"{DATA_START_UTC}_{DATA_END_UTC}"
OHLCV_1M = "ohlcv-1m"
ROLL_BLACKOUT_SESSIONS = 2  # screening.runner.CANONICAL_ROLL_BLACKOUT_SESSIONS (a test pins it)
PURCHASE_MANIFEST = REPO_ROOT / "reports" / "stage_e1_purchase.json"
LIQUIDITY_JSON = REPO_ROOT / "reports" / "stage_e0_liquidity.json"
CONDITION_PATH = VENDOR_ROOT / "condition" / f"{DATASET}_2025-04-01_2026-09-16.json"
ROLLS_DIR = VENDOR_ROOT / "rolls"
REPORTS = REPO_ROOT / "reports"
BARS_JSON = REPORTS / "stage_e2a_bars.json"
PROBE_JSON = REPORTS / "stage_e2a_bars_probe.json"
BUILDER_FILES = ("data/build_bars.py", "data/build_bars_run.py", "data/build_bars_reports.py",
                 "data/group_session.py",
                 "data/validate.py", "data/bars.py", "data/adapter.py", "data/intervals.py",
                 "data/session.py", "data/research_bars.py", "data/build_mes_bars.py")
MAX_THREADS = 4
# Lead ruling L-10: how a consumer tells a booked-forward trade date's two calendar days apart.
DAY_SESSION_RULE = (
    "trade_date is CME's trade date. Design D6's day-session quantities (O, C) for trade date "
    "D are read only from bars whose CT calendar date (ts_event converted to America/Chicago) "
    "is D itself. On a crypto booked-forward trade date (booked_forward_sessions), the "
    "booked-in holiday session lies on an earlier CT calendar date and is never read as D's "
    "day session; its flatten flags follow its own calendar day (TopstepX treats each calendar "
    "day on its own). For every other product and date the CT calendar date of a day-session "
    "bar equals its trade_date."
)
CT_17 = datetime.strptime("17:00", "%H:%M").time()


class BuildRefused(RuntimeError):
    """The build was asked to do something it must never do (overwrite, read outside)."""


# ------------------------------------------------------------------ inputs ----
@dataclass(frozen=True)
class InputFile:
    path: Path
    sha256: str | None  # expected (the purchase manifest); None = not in a manifest (MES)
    record_count: int | None
    instrument_ids: tuple[str, ...] | None = None


@dataclass(frozen=True)
class ProductSpec:
    root: str
    group: str
    tick: str  # decimal string in the vendor's price units
    tick_source: str
    files: tuple[InputFile, ...]
    rolls_path: Path
    symbology_path: Path | None  # instrument_id -> raw_symbol intervals (the D.1f rule); None =
    #                              MES's Stage A.1 rule (the roll boundaries' raw symbols)
    policy: FlattenPolicy
    out: Path
    first_trade_date: date = RESEARCH_FIRST_TRADE_DATE
    last_trade_date: date = RESEARCH_LAST_TRADE_DATE
    data_start: date = DATA_START_UTC
    data_end: date = DATA_END_UTC  # exclusive, UTC

    @property
    def continuous(self) -> str:
        return f"{self.root}.v.0"

    @property
    def tick_fixed(self) -> int:
        return tick_fixed(self.tick)


def tick_fixed(tick: str) -> int:
    value = Decimal(tick) * PRICE_SCALE
    if value != value.to_integral_value() or value <= 0:
        raise ValueError(f"tick {tick} is not a positive whole number of 1e-9 price units")
    return int(value)


def parse_tick(text: str) -> str:
    """The numeric tick of an E.0 ``tick_size`` string: its leading decimal, or the decimal in
    parentheses when it leads with a fraction ("1/2 of 1/32 (0.015625)")."""
    import re

    lead = re.match(r"^\s*(\d+(?:\.\d+)?)(?=\s|$)", text)
    if lead:
        return lead.group(1)
    inner = re.search(r"\((\d+(?:\.\d+)?)\)", text)
    if inner:
        return inner.group(1)
    raise ValueError(f"no numeric tick in {text!r}")


def load_ticks(path: Path = LIQUIDITY_JSON) -> dict[str, tuple[str, str]]:
    """root -> (tick, the E.0 tick_size text) from reports/stage_e0_liquidity.json."""
    rows = json.loads(Path(path).read_text())["products"]
    return {r["symbol"]: (parse_tick(str(r["tick_size"])), str(r["tick_size"])) for r in rows}


def purchase_files(root: str, manifest: Path = PURCHASE_MANIFEST) -> tuple[InputFile, ...]:
    """The product's ohlcv-1m files of the step 1 purchase, oldest first."""
    files = json.loads(Path(manifest).read_text())["files"]
    rows = sorted((f for f in files if f["product"] == root and f["schema"] == OHLCV_1M),
                  key=lambda f: f["request_start"])
    return tuple(InputFile(REPO_ROOT / f["path"], f["sha256"], int(f["record_count"]),
                           tuple(str(i) for i in f.get("instrument_ids", []))) for f in rows)


def admissible_products(manifest: Path = PURCHASE_MANIFEST) -> list[str]:
    files = json.loads(Path(manifest).read_text())["files"]
    return sorted({f["product"] for f in files if f["schema"] == OHLCV_1M})


def ohlcv_record_counts(manifest: Path = PURCHASE_MANIFEST) -> dict[str, int]:
    """Total ohlcv-1m records per product, from the manifest (the 'most liquid' ranking)."""
    out: Counter[str] = Counter()
    for f in json.loads(Path(manifest).read_text())["files"]:
        if f["schema"] == OHLCV_1M:
            out[f["product"]] += int(f["record_count"])
    return dict(out)


def research_parquet_path(root: str, base: Path = PROCESSED_ROOT) -> Path:
    return base / root / f"ohlcv-1m_{root}_v_0_2025-04-01_2026-06-19_research.parquet"


def rolls_cache_path(root: str) -> Path:
    return ROLLS_DIR / f"{root}_v_0_{SPAN}.jsonl"


def symbology_cache_path(root: str) -> Path:
    return ROLLS_DIR / f"{root}_v_0_{SPAN}_symbology.json"


def product_spec(root: str, out_base: Path = PROCESSED_ROOT) -> ProductSpec:
    tick, text = load_ticks()[root]
    group = group_of(root)
    return ProductSpec(
        root=root, group=group, tick=tick, tick_source=f"reports/stage_e0_liquidity.json "
        f"tick_size {text!r}", files=purchase_files(root), rolls_path=rolls_cache_path(root),
        symbology_path=symbology_cache_path(root), policy=STAGE_E_POLICIES[group],
        out=research_parquet_path(root, out_base))


# ------------------------------------------------------------------ symbology ----
def fetch_symbology(root: str, client: Any, start: date = DATA_START_UTC,  # noqa: ANN401
                    end: date = DATA_END_UTC) -> dict:
    """Two free symbology.resolve calls (data.adapter.resolve_rolls's), raw responses kept."""
    sym = f"{root}.v.0"
    by_id = client.symbology.resolve(dataset=DATASET, symbols=[sym], stype_in="continuous",
                                     stype_out="instrument_id", start_date=str(start),
                                     end_date=str(end))
    intervals = sorted(by_id["result"].get(sym, []), key=lambda e: str(e["d0"]))
    ids = sorted({str(e["s"]) for e in intervals})
    by_raw = client.symbology.resolve(dataset=DATASET, symbols=ids, stype_in="instrument_id",
                                      stype_out="raw_symbol", start_date=str(start),
                                      end_date=str(end))
    return {"symbol": sym, "start_date": str(start), "end_date": str(end),
            "fetched_utc": datetime.now(UTC).isoformat(), "continuous_to_instrument_id": by_id,
            "queried_instrument_ids": ids, "instrument_id_to_raw_symbol": by_raw}


def ensure_rolls(spec: ProductSpec, client_factory: Callable[[], Any] | None,
                 log: Callable[[str], None] = print) -> tuple[list[RollBoundary], dict | None, str]:
    """(boundaries, symbology payload or None, source). Cached files are never rewritten."""
    sym_path = spec.symbology_path
    if sym_path is not None and not sym_path.is_file() and client_factory is not None:
        try:
            payload = fetch_symbology(spec.root, client_factory(), spec.data_start, spec.data_end)
        except Exception as exc:  # noqa: BLE001 — the fallback below is logged, never silent
            log(f"{spec.root}: symbology.resolve unavailable ({type(exc).__name__}: {exc}); "
                "falling back to the files' embedded mappings")
        else:
            sym_path.parent.mkdir(parents=True, exist_ok=True)
            with sym_path.open("x") as fh:
                json.dump(payload, fh, indent=1, default=str)
            sym_path.chmod(0o444)
    payload = json.loads(sym_path.read_text()) if sym_path is not None and sym_path.is_file() \
        else None
    if payload is not None and not spec.rolls_path.is_file():
        sym = payload["symbol"]
        intervals = sorted(payload["continuous_to_instrument_id"]["result"].get(sym, []),
                           key=lambda e: str(e["d0"]))
        raw = payload["instrument_id_to_raw_symbol"]["result"]
        write_rolls(boundaries_from_intervals(sym, intervals, raw), spec.rolls_path)
        spec.rolls_path.chmod(0o444)
    if spec.rolls_path.is_file():
        cached = payload is not None or spec.symbology_path is None
        source = "symbology.resolve (cached)" if cached else "roll cache"
        return read_rolls(spec.rolls_path), payload, source
    return [], None, "none"


def embedded_intervals(paths: Sequence[Path], symbol: str) -> list[dict[str, str]]:
    """The continuous symbol's instrument-id intervals stored in the DBN files at download,
    as symbology.resolve's {d0, d1, s} (UTC dates, d1 exclusive), merged across files."""
    import databento  # lazy

    rows: list[dict[str, str]] = []
    for path in paths:
        store = databento.DBNStore.from_file(path)
        for e in store.mappings.get(symbol, []):
            rows.append({"d0": str(e["start_date"]), "d1": str(e["end_date"]),
                         "s": str(e["symbol"])})
    rows.sort(key=lambda r: r["d0"])
    merged: list[dict[str, str]] = []
    for r in rows:
        if merged and merged[-1]["s"] == r["s"] and merged[-1]["d1"] >= r["d0"]:
            merged[-1] = {**merged[-1], "d1": max(merged[-1]["d1"], r["d1"])}
        else:
            merged.append(dict(r))
    return merged


def _by_utc_date(intervals: Sequence[dict], start: date, end: date) -> dict[str, str]:
    out: dict[str, str] = {}
    day = start
    while day < end:
        iso = day.isoformat()
        hits = sorted({str(e["s"]) for e in intervals if str(e["d0"]) <= iso < str(e["d1"])})
        out[iso] = ",".join(hits)
        day += timedelta(days=1)
    return out


def mapping_crosscheck(resolved: Sequence[dict], embedded: Sequence[dict], start: date,
                       end: date) -> dict:
    """UTC dates where symbology.resolve and the files' embedded mappings name a different
    instrument (reported, never patched)."""
    a, b = _by_utc_date(resolved, start, end), _by_utc_date(embedded, start, end)
    diff = [{"utc_date": d, "symbology_resolve": a[d], "embedded": b[d]} for d in a if a[d] != b[d]]
    return {"utc_dates_compared": len(a), "disagreements": diff}


def splice_check(ts: np.ndarray, ids: np.ndarray, rolls: Sequence[RollBoundary]) -> dict:
    """data.build_mes_bars.splice_check's test, per boundary, plus the instrument changes in
    the bars that no boundary explains."""
    change = np.flatnonzero(np.diff(ids) != 0) + 1
    observed = [(int(ts[i]), int(ids[i - 1]), int(ids[i])) for i in change]
    rows, explained = [], 0
    for r in rolls:
        match = [o for o in observed if o[1] == int(r.from_instrument)
                 and o[2] == int(r.to_instrument)]
        first_new = match[0][0] if match else None
        ok = (first_new is not None and first_new >= r.ts_ns
              and not ((ts >= r.ts_ns) & (ids == int(r.from_instrument))).any()
              and not ((ts < r.ts_ns) & (ids == int(r.to_instrument))).any())
        explained += int(ok)
        rows.append({"roll_date_utc": r.date, "from": r.from_raw_symbol, "to": r.to_raw_symbol,
                     "symbology_splice_ns": r.ts_ns, "first_bar_of_new_contract_ns": first_new,
                     "consistent": ok})
    return {"per_roll": rows, "instrument_changes_in_bars": len(observed),
            "unexplained_instrument_changes": len(observed) - explained}


# ------------------------------------------------------------------ build ----
def _utc_ns(day: date) -> int:
    return utc_midnight_ns(day)


def _rel(path: Path) -> str:
    path = Path(path)
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def _ct_str(ns: int | None) -> str:
    if ns is None:
        return ""
    return pd.Timestamp(ns, tz="UTC").tz_convert("America/Chicago").strftime("%Y-%m-%d %a %H:%M")


def verify_inputs(spec: ProductSpec) -> tuple[list[dict], list[str]]:
    rows, problems = [], []
    for f in spec.files:
        if not f.path.is_file():
            problems.append(f"input file missing: {f.path.name}")
            rows.append({"name": f.path.name, "sha256": None, "sha256_verified": False})
            continue
        got = sha256_file(f.path)
        ok = f.sha256 is None or got == f.sha256
        if not ok:
            problems.append(f"sha256 mismatch for {f.path.name}: manifest {f.sha256}, file {got}")
        rows.append({"name": f.path.name, "path": _rel(f.path),
                     "sha256": got, "sha256_expected": f.sha256,
                     "sha256_verified": f.sha256 is not None and ok,
                     "records_expected": f.record_count})
    return rows, problems


def _builder_sha256() -> dict[str, str]:
    return {p: sha256_file(REPO_ROOT / p) for p in BUILDER_FILES if (REPO_ROOT / p).is_file()}


def _coverage_limit_ns(cal: GroupCalendar, data_end_ns: int, opened: OpenIntervals) -> int:
    """Bars at or after this instant are past the calendar's coverage: 17:00 CT of its last
    covered day (every group's session for that trade date has ended by then), or the end of a
    covered booked-forward target's session (crypto's 2026-06-22) when that is later."""
    last_open = int(opened.ends.max()) if len(opened) else 0
    return min(data_end_ns, max(ct_ns(cal.coverage[1], CT_17), last_open))


def _after_window_spans(cal: GroupCalendar, ts: np.ndarray, days: np.ndarray,
                        late: np.ndarray) -> dict[str, dict]:
    """Per dropped after-window trade date: bar count and CT span (never written anywhere).
    A CME booked-forward target in holdout-1 is labelled as lead ruling L-9 words it."""
    from data.research_bars import HOLDOUT1, trade_date_class

    out: dict[str, dict] = {}
    for d in np.unique(days[late]):
        day = d.astype(object)
        sel = ts[late & (days == d)]
        booked = sorted(str(b) for b, t in cal.booked_forward.items() if t == day)
        label = "dropped (after the research window)"
        if booked and trade_date_class(day) == HOLDOUT1:
            label = f"booked to {day} (holdout-1 trade date): dropped"
        out[str(day)] = {"bars": int(sel.size), "first_ct": _ct_str(int(sel.min())),
                         "last_ct": _ct_str(int(sel.max())), "booked_from": booked,
                         "label": label}
    return out


def _drops_by_date(days: np.ndarray, mask: np.ndarray) -> dict[str, int]:
    vals, counts = np.unique(days[mask].astype(str), return_counts=True)
    return {str(v): int(c) for v, c in zip(vals, counts, strict=True)}


def _gap_summary(report: Any) -> dict:  # noqa: ANN401 — data.validate.BarValidation
    runs = report.gap_runs
    buckets = Counter("1" if r.minutes == 1 else "2-5" if r.minutes <= 5 else "6-30"
                      if r.minutes <= 30 else ">30" for r in runs)
    return {"gap_runs_total": len(runs), "gap_runs_by_length": dict(buckets),
            "gap_runs_by_segment": dict(Counter(r.segment for r in runs)),
            "gap_runs_over_30min": [{"start_ct": r.start_ct, "minutes": r.minutes,
                                     "segment": r.segment} for r in runs if r.minutes > 30][:200]}


def _raw_checks(report: Any, closure_ct: list[str]) -> dict:  # noqa: ANN401
    return {"rows": report.rows, "non_increasing_steps": report.non_increasing_steps,
            "duplicate_timestamps": report.duplicate_timestamps,
            "negative_volume": report.negative_volume, "zero_volume_bars": report.zero_volume,
            "off_tick_prices": report.off_tick_prices,
            "ohlc_inconsistent": report.ohlc_inconsistent,
            "bars_in_scheduled_closure": len(report.bars_in_scheduled_closure),
            "bars_in_scheduled_closure_ct": closure_ct[:200]}


def grid_scale_probe(raw: pd.DataFrame, tick_fx: int) -> dict[str, int]:
    """Off-grid price counts at 1x, 10x and 100x the tick: a scale check on the vendor's price
    units (a cent-quoted product shows 0 at 100x when prices are in cents). Counts only."""
    prices = raw[["open_fixed", "high_fixed", "low_fixed", "close_fixed"]].to_numpy()
    return {f"x{m}": int((prices % (tick_fx * m) != 0).sum()) for m in (1, 10, 100)}


@dataclass
class BuildResult:
    summary: dict
    frame: pd.DataFrame | None  # the flagged bars (None when refused)
    meta: dict | None


def build_product(spec: ProductSpec, cal: GroupCalendar, degraded: list[dict],
                  rolls: list[RollBoundary], symbology: dict | None, roll_source: str, *,
                  load_bars: Callable[[list[Path]], pd.DataFrame] = load_raw_bars,
                  embedded: list[dict] | None = None) -> BuildResult:
    """Everything except writing. ``summary`` carries counts, dates and flags only."""
    summary: dict[str, Any] = {
        "product": spec.root, "group": spec.group, "continuous": spec.continuous,
        "schema": OHLCV_1M, "status": "refused", "refusal_causes": [],
        "window_trade_dates": [str(spec.first_trade_date), str(spec.last_trade_date)],
        "data_utc": [str(spec.data_start), str(spec.data_end)],
        "tick": {"tick": spec.tick, "tick_fixed_1e9": spec.tick_fixed, "source": spec.tick_source},
        "flatten_policy": spec.policy.as_dict(), "calendar_modules": cal.module_sha256(),
        "calendar_coverage": [str(d) for d in cal.coverage],
        "builder_files": _builder_sha256(),
    }
    inputs, problems = verify_inputs(spec)
    summary["input_files"] = inputs
    if problems:
        summary["refusal_causes"] = problems
        return BuildResult(summary, None, None)

    raw = load_bars([f.path for f in spec.files])
    per_file = raw.groupby("source_file").size().to_dict() if "source_file" in raw else {}
    for row, f in zip(summary["input_files"], spec.files, strict=True):
        row["records_loaded"] = int(per_file.get(f.path.name, 0))
        if f.record_count is not None and row["records_loaded"] != f.record_count:
            problems.append(f"{f.path.name}: {row['records_loaded']} records loaded, manifest "
                            f"{f.record_count}")
        if f.instrument_ids is not None and "source_file" in raw:
            got = sorted({str(int(i)) for i in
                          raw.loc[raw["source_file"] == f.path.name, "instrument_id"].unique()})
            row["instrument_ids"] = got
            # The manifest lists the ids of the file's embedded symbology mappings, which can
            # include an interval with no bar (a mapping that starts on the weekend before the
            # file). A bar whose id the manifest does not list is a problem; the reverse is not.
            row["manifest_ids_without_bars"] = sorted(set(f.instrument_ids) - set(got))
            extra = sorted(set(got) - set(f.instrument_ids))
            if extra:
                problems.append(f"{f.path.name}: instrument ids {extra} are not in the "
                                f"manifest's {sorted(f.instrument_ids)}")
    return _build_loaded(spec, cal, degraded, rolls, symbology, roll_source, raw, summary,
                         problems, embedded)


def _build_loaded(spec: ProductSpec, cal: GroupCalendar, degraded: list[dict],
                  rolls: list[RollBoundary], symbology: dict | None, roll_source: str,
                  raw: pd.DataFrame, summary: dict, problems: list[str],
                  embedded: list[dict] | None) -> BuildResult:
    data_start_ns, data_end_ns = _utc_ns(spec.data_start), _utc_ns(spec.data_end)
    opened = open_intervals(cal, spec.first_trade_date - timedelta(days=7),
                            spec.data_end + timedelta(days=7))
    limit_ns = _coverage_limit_ns(cal, data_end_ns, opened)
    c_starts, c_ends = closed_windows(opened, data_start_ns, limit_ns)
    ts = raw["ts_event"].to_numpy().astype(np.int64)

    raw_report, _ = validate_bars(raw, data_start_ns, limit_ns, c_starts, c_ends,
                                  spec.tick_fixed, spec.tick)
    summary["raw_checks"] = _raw_checks(raw_report, [])
    summary["raw_checks"]["grid_scale_probe"] = grid_scale_probe(raw, spec.tick_fixed)
    summary["raw_checks"]["bars_before_data_start"] = int((ts < data_start_ns).sum())
    summary["raw_checks"]["bars_at_or_after_data_end"] = int((ts >= data_end_ns).sum())
    # MES's hard checks (data.validate.BarValidation.hard_failures) plus the input integrity
    # checks; bars inside a scheduled closure are kept and flagged, as MES's (lead ruling L-3).
    hard = list(problems) + list(raw_report.hard_failures)
    if summary["raw_checks"]["bars_before_data_start"] or \
            summary["raw_checks"]["bars_at_or_after_data_end"]:
        hard.append("bars outside the files' UTC request range")

    assigned = assign_trade_dates(opened, ts, close_minute_to_previous=True)
    beyond = ts >= limit_ns
    days = assigned.days.copy()
    days[beyond] = np.datetime64("NaT", "D")
    closure = in_windows(ts, c_starts, c_ends)
    summary["closure_bars"] = [
        {"ct": _ct_str(int(t)), "trade_date": str(d), "close_minute": bool(b)}
        for t, d, b in zip(ts[closure], days[closure], assigned.boundary[closure], strict=True)]
    summary["rolls"] = _roll_summary(spec, cal, opened, rolls, symbology, roll_source, raw,
                                     embedded)
    summary["calendar_check"] = _calendar_check(spec, cal, ts, days, data_end_ns)
    if hard:
        summary["refusal_causes"] = hard
        return BuildResult(summary, None, None)
    deep = [c for c in summary["closure_bars"] if not c["close_minute"]]
    if deep:
        summary["status"] = "held_for_lead"
        summary["refusal_causes"] = [
            f"{len(deep)} bars inside a scheduled closure beyond the close minute (first "
            f"{deep[0]['ct']} CT): held for the lead before building (ruling L-3)"]
        return BuildResult(summary, None, None)
    return _keep_and_flag(spec, cal, degraded, rolls, symbology, raw, days, beyond, opened,
                          summary)


def _calendar_check(spec: ProductSpec, cal: GroupCalendar, ts: np.ndarray, days: np.ndarray,
                    data_end_ns: int) -> dict:
    first64 = np.datetime64(spec.first_trade_date, "D")
    last64 = np.datetime64(spec.last_trade_date, "D")
    valid = ~np.isnat(days)
    in_window = valid & (days >= first64) & (days <= last64)
    try:
        closes = cal.day_session_close(spec.root)
    except Exception as exc:  # noqa: BLE001 — reported, the build does not depend on it
        return {"error": f"{type(exc).__name__}: {exc}"}
    check = validate_calendar_group(ts[in_window], cal, spec.first_trade_date,
                                    spec.last_trade_date, closes, data_end_ns=data_end_ns)
    out = check.as_dict()
    out["day_session_close_ct"] = {str(k): v.strftime("%H:%M") for k, v in closes.items()}
    return out


def _roll_summary(spec: ProductSpec, cal: GroupCalendar, opened: OpenIntervals,
                  rolls: list[RollBoundary], symbology: dict | None, roll_source: str,
                  raw: pd.DataFrame, embedded: list[dict] | None) -> dict:
    from sim.engine import roll_blackout_dates

    splices = []
    for r in rolls:
        td = trade_date_of_instant(opened, r.ts_ns)
        splices.append({"date_utc": r.date, "from": r.from_raw_symbol, "to": r.to_raw_symbol,
                        "from_instrument": r.from_instrument, "to_instrument": r.to_instrument,
                        "splice_trade_date": None if td is None else str(td)})
    splice_days = sorted({date.fromisoformat(s["splice_trade_date"]) for s in splices
                          if s["splice_trade_date"]})
    group_bo = sorted(roll_blackout(cal, splice_days, ROLL_BLACKOUT_SESSIONS))
    engine_bo = sorted(roll_blackout_dates(splice_days, ROLL_BLACKOUT_SESSIONS))
    in_window = [d for d in group_bo if spec.first_trade_date <= d <= spec.last_trade_date]
    out = {
        "source": roll_source, "rolls_file": _rel(spec.rolls_path),
        "boundaries": splices, "splice_trade_dates": [str(d) for d in splice_days],
        "roll_blackout_dates": [str(d) for d in group_bo],
        "roll_blackout_dates_in_window": [str(d) for d in in_window],
        "roll_blackout_sessions_before": ROLL_BLACKOUT_SESSIONS,
        "sim_engine_roll_blackout_differs": sorted(
            {str(d) for d in set(group_bo) ^ set(engine_bo)}),
        "splice_check": splice_check(raw["ts_event"].to_numpy(), raw["instrument_id"].to_numpy(),
                                     rolls),
    }
    if symbology is not None and embedded is not None:
        sym = symbology["symbol"]
        resolved = symbology["continuous_to_instrument_id"]["result"].get(sym, [])
        out["embedded_mapping_crosscheck"] = mapping_crosscheck(resolved, embedded,
                                                                spec.data_start, spec.data_end)
        out["bars_off_symbology_mapping"] = bars_off_mapping(
            raw["ts_event"].to_numpy(), raw["instrument_id"].to_numpy(), resolved)
    return out


def bars_off_mapping(ts: np.ndarray, ids: np.ndarray, intervals: Sequence[dict]) -> dict:
    """Bars whose instrument is not the one symbology maps the continuous symbol to on the
    bar's UTC date: a day-level splice check that also holds when the vendor's volume-ranked
    series flips back and forth between two contracts. Counts and UTC dates only."""
    days = (np.asarray(ts, dtype=np.int64) // 86_400_000_000_000).astype("datetime64[D]")
    want = np.full(days.shape, -1, dtype=np.int64)
    for e in intervals:
        mask = (days >= np.datetime64(str(e["d0"]))) & (days < np.datetime64(str(e["d1"])))
        want[mask] = int(e["s"])
    off = want != np.asarray(ids, dtype=np.int64)
    return {"bars": int(off.sum()), "utc_dates": sorted({str(d) for d in days[off]})[:50]}


def _raw_symbols(spec: ProductSpec, rolls: list[RollBoundary], symbology: dict | None,
                 kept: pd.DataFrame) -> tuple[np.ndarray, list[dict], str]:
    ts, ids = kept["ts_event"].to_numpy(), kept["instrument_id"].to_numpy()
    if spec.symbology_path is None:
        mapping = instrument_raw_symbols(rolls)
        return (np.array([mapping.get(int(i), "") for i in ids], dtype=object), [],
                "Stage A.1: the roll boundaries' raw symbol per instrument id (MES research)")
    if symbology is None:
        return (np.array([""] * len(kept), dtype=object), [],
                "none: symbology.resolve unavailable, raw_symbol left empty")
    raw_intervals = symbology["instrument_id_to_raw_symbol"]["result"]
    symbols, unmapped = raw_symbols_on_bar_dates(ts, ids, raw_intervals,
                                                 outright_pattern(spec.root), spec.root)
    return symbols, unmapped, (
        f"D.1f: kept iff a {spec.root} outright (root + month letter + year digit) is what "
        "symbology maps the bar's instrument_id to on the bar's UTC date")


def _keep_and_flag(spec: ProductSpec, cal: GroupCalendar, degraded: list[dict],
                   rolls: list[RollBoundary], symbology: dict | None, raw: pd.DataFrame,
                   days: np.ndarray, beyond: np.ndarray, opened: OpenIntervals,
                   summary: dict) -> BuildResult:
    first64 = np.datetime64(spec.first_trade_date, "D")
    last64 = np.datetime64(spec.last_trade_date, "D")
    nat = np.isnat(days)
    early = ~nat & (days < first64)
    late = ~nat & (days > last64)
    window_keep = ~nat & ~early & ~late
    kept = raw[window_keep].reset_index(drop=True)
    kept_days = days[window_keep]
    symbols, unmapped, rule = _raw_symbols(spec, rolls, symbology, kept)
    no_outright = symbols == ""
    if spec.symbology_path is not None and symbology is not None and no_outright.any():
        kept, kept_days = kept[~no_outright].reset_index(drop=True), kept_days[~no_outright]
        symbols = symbols[~no_outright]
    summary["drops"] = {
        "trade_date_before_window": _drops_by_date(days, early),
        "trade_date_after_window": _drops_by_date(days, late),
        "after_window_spans": _after_window_spans(cal, raw["ts_event"].to_numpy(), days, late),
        "past_calendar_coverage": int(beyond.sum()),
        "no_trade_date": int((nat & ~beyond).sum()),
        "no_outright_on_bar_utc_date": {
            "total": int(no_outright.sum()) if symbology is not None else 0,
            "groups": unmapped[:200]},
        "raw_symbol_rule": rule,
    }
    if kept.empty:
        summary["refusal_causes"] = ["no bar survives the window and raw-symbol drops"]
        return BuildResult(summary, None, None)
    return _flag_kept(spec, cal, degraded, rolls, kept, kept_days, symbols, opened, summary)


def _flag_kept(spec: ProductSpec, cal: GroupCalendar, degraded: list[dict],
               rolls: list[RollBoundary], kept: pd.DataFrame, kept_days: np.ndarray,
               symbols: np.ndarray, opened: OpenIntervals, summary: dict) -> BuildResult:
    data_start_ns, data_end_ns = _utc_ns(spec.data_start), _utc_ns(spec.data_end)
    last_day = kept_days.max().astype(object)
    last_end = max(int(e) for e, d in zip(opened.ends, opened.days, strict=True) if d == last_day)
    kept_end = min(last_end, data_end_ns)
    c_starts, c_ends = closed_windows(opened, data_start_ns, kept_end)
    report, gap_before = validate_bars(kept, data_start_ns, kept_end, c_starts, c_ends,
                                       spec.tick_fixed, spec.tick)
    summary["validation"] = {**_raw_checks(report, [_ct_str(t) for t in
                                                   report.bars_in_scheduled_closure]),
                             **_gap_summary(report), "hard_failures": report.hard_failures}
    if report.hard_failures:
        summary["refusal_causes"] = report.hard_failures
        return BuildResult(summary, None, None)
    splice_days = {date.fromisoformat(s) for s in summary["rolls"]["splice_trade_dates"]}
    degraded_dates = sorted({str(d["date"]) for d in degraded})
    frame = flag_frame(kept, cal, spec.policy, kept_days, c_starts, c_ends, gap_before,
                       set(degraded_dates), symbols, splice_days)
    trade_dates = sorted(set(frame["trade_date"]))
    refuse_dates_outside(trade_dates, frozenset({RESEARCH, RESEARCH_EMBARGO}),
                         "Stage E research bar build")
    if trade_dates[0] < spec.first_trade_date or trade_dates[-1] > spec.last_trade_date:
        raise BuildRefused(f"trade dates {trade_dates[0]}..{trade_dates[-1]} outside the window")
    td_iso = {d.isoformat() for d in trade_dates}
    summary["booked_forward_sessions"] = [
        {"holiday": str(b), "trade_date": str(t)}
        for b, t in sorted(cal.booked_forward.items()) if t.isoformat() in td_iso]
    summary.update({
        "status": "built", "refusal_causes": [], "bars": len(frame),
        "trade_dates": len(trade_dates), "first_trade_date": str(trade_dates[0]),
        "last_trade_date": str(trade_dates[-1]),
        "degraded": {"condition_file": _rel(CONDITION_PATH),
                     "degraded_utc_dates": degraded_dates,
                     "on_research_trade_dates": sorted(td_iso & set(degraded_dates)),
                     "bars_flagged": int(frame["vendor_degraded_day"].sum())},
        "flag_counts": {c: int(frame[c].sum()) for c in (
            "in_flatten_window", "in_no_new_positions_window", "in_scheduled_closure",
            "is_roll_session", "vendor_degraded_day")}
        | {"bars_with_gap_before": int((frame["gap_before_minutes"] > 0).sum())},
    })
    meta = _metadata(spec, cal, rolls, summary)
    return BuildResult(summary, frame, meta)


def flag_frame(bars: pd.DataFrame, cal: GroupCalendar, policy: FlattenPolicy, days: np.ndarray,
               closed_starts: np.ndarray, closed_ends: np.ndarray, gap_before: np.ndarray,
               degraded_utc_dates: set[str], raw_symbols: np.ndarray,
               splice_trade_dates: set[date]) -> pd.DataFrame:
    """MES's flag columns (data.bars.add_flags, same names, order and dtypes) from a group
    calendar and flatten policy. ``days``: each bar's trade date (datetime64[D])."""
    ts = bars["ts_event"].to_numpy()
    out = pd.DataFrame({
        "ts_event": ts,
        "open": bars["open_fixed"].to_numpy() / PRICE_SCALE,
        "high": bars["high_fixed"].to_numpy() / PRICE_SCALE,
        "low": bars["low_fixed"].to_numpy() / PRICE_SCALE,
        "close": bars["close_fixed"].to_numpy() / PRICE_SCALE,
        "volume": bars["volume"].to_numpy(),
        "instrument_id": bars["instrument_id"].to_numpy(),
    })
    if len(raw_symbols) != len(out):
        raise ValueError(f"{len(raw_symbols)} raw symbols for {len(out)} bars")
    out["raw_symbol"] = np.asarray(raw_symbols, dtype=object)
    in_flat, in_nonew = flatten_masks(cal, policy, ts, days)
    out["in_flatten_window"] = in_flat
    out["in_no_new_positions_window"] = in_nonew
    out["early_halt_ct"] = early_halt_labels(cal, ts)
    out["in_scheduled_closure"] = in_windows(ts, closed_starts, closed_ends)
    uniq, inverse = np.unique(days, return_inverse=True)
    as_dates = np.array([d.astype(object) for d in uniq], dtype=object)[inverse.reshape(-1)]
    out["trade_date"] = list(as_dates)
    cal.assert_coverage(set(as_dates.tolist()))
    out["is_roll_session"] = out["trade_date"].isin(splice_trade_dates)
    out["gap_before_minutes"] = gap_before
    utc_dates = pd.to_datetime(ts, utc=True).strftime("%Y-%m-%d")
    out["vendor_degraded_day"] = np.isin(utc_dates, sorted(degraded_utc_dates))
    return out


def _metadata(spec: ProductSpec, cal: GroupCalendar, rolls: list[RollBoundary],
              summary: dict) -> dict:
    return {
        "source": f"Databento {DATASET} {spec.continuous} {OHLCV_1M}, unadjusted prices; "
                  "Stage E.2a research window, trade dates "
                  f"{spec.first_trade_date}..{spec.last_trade_date}",
        "stage": "E.2a Task 7 (data/build_bars.py)",
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
        "degraded_on_research_trade_dates": summary["degraded"]["on_research_trade_dates"],
        "raw_symbol_rule": summary["drops"]["raw_symbol_rule"],
        "drops": {k: v for k, v in summary["drops"].items() if k != "raw_symbol_rule"},
        "validation": {"rows": summary["bars"], "raw_hard_failures": [],
                       "gap_runs_total": summary["validation"]["gap_runs_total"],
                       "gap_runs_by_length": summary["validation"]["gap_runs_by_length"]},
        "trade_date_range": [summary["first_trade_date"], summary["last_trade_date"]],
        "calendar_check_passed": summary["calendar_check"].get("passed"),
        "day_session_rule": DAY_SESSION_RULE,
        "booked_forward_sessions": summary.get("booked_forward_sessions", []),
    }


def write_parquet(frame: pd.DataFrame, meta: dict, out: Path) -> str:
    """Read-only (0444), never over an existing file (os.link). Returns the file's sha256."""
    from data.build_mes_bars import _write_read_only_parquet

    if out.exists():
        raise BuildRefused(f"REFUSED: {out} already exists; nothing is overwritten")
    _write_read_only_parquet(frame, out, meta)
    return sha256_file(out)


def existing_matches(spec: ProductSpec) -> bool:
    """True if the product's parquet exists and was built from exactly these input files."""
    import pyarrow.parquet as pq

    if not spec.out.is_file():
        return False
    meta = json.loads(pq.read_schema(spec.out).metadata[b"propexperiment"])
    stamped = {r["name"]: r["sha256"] for r in meta.get("input_files", [])}
    wanted = {f.path.name: f.sha256 for f in spec.files}
    return stamped == wanted


def degraded_days(path: Path = CONDITION_PATH) -> list[dict]:
    """The frozen dataset-condition file (fetched 2026-09-16 for MES; never fetched again)."""
    return [d for d in json.loads(Path(path).read_text()) if d["condition"] != "available"]


if __name__ == "__main__":
    from data.build_bars_run import cli

    sys.exit(cli())
