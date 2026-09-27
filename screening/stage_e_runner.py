"""The generalized Stage E screening runner (Stage E.2b Task 1; design D4, D5, D9, D11.5, D11.6).

The one way a Stage E cluster session screens (research window) or confirms (confirmation window)
a member. Public interface:

    screen_member(cluster, label, factory, legs, window, *, harness_sha256, research_root,
                  step2_root, out_dir) -> dict          # the member record, also written as JSON
    screen_cluster(cluster, window, *, harness_sha256, research_root, step2_root, out_dir)
                  -> dict                               # every frozen member, then D5's tiers
    python -m screening.stage_e_runner --harness-sha256 SHA --cluster K1 --member LABEL|--all \
        --window research|confirmation --research-root DIR --step2-root DIR --out-dir DIR

What the caller gives is only WHICH member and WHERE the data and outputs live. Everything that
could change a result is frozen and read here: the harness (screening.harness_freeze.preflight,
called first, before any file is read; its sha256 is written into every record), the cluster's
member code and declarations (screening.stage_e_freeze: label, ordinal, module, factory, legs),
the product rules, costs, vehicles, q_c and eps (screening.stage_e_frozen, hash-checked), the
calendars and flatten rules (data/calendars, rules/sessions.py), the release calendar
(screening.stage_e_rules.RELEASE_CALENDAR_PATH) and, for the confirmation window, S_X per leg
from the one shared loader screening.stage_e_start_dates (every
reports/stage_e_start_rule_<SET>.json, lead ruling OC-K; the ML route reads the same files; each
leg's S_X and the files and sha256 that give it are recorded; the step 2 store a confirmation run
or supply count reads must hash to the store its S_X was computed from, review F-3). A missing
frozen input is refused by name, never replaced by a default.

Per member, in order:
1. bars per leg (data.stage_e_bars: holdout-1, holdout-2 and embargo rows refused by CME trade
   date on the group calendar; MBT's rows booked to 2026-06-22 included);
2. the window (screening.stage_e_align.member_window: legs' common trade dates, less the union of
   their roll blackouts, less rule UR-1's 2026-06-18/19 on the research window);
3. D9's member-level coverage on every leg the member reads (>= 0.95); a member below it is
   labelled "coverage_below_0.95" and excluded before screening (lead ruling OC-H): it is not run;
4. the engine (screening.stage_e_engine with screening.stage_e_rules.StageERules);
5. the daily series in net ticks per contract per day of the primary (first traded) leg's vehicle,
   zeros on window dates without a trip (screening.stage_e_stats: one leg -> each trip divided by
   its own contracts; several traded legs -> combined dollars / (q_c x tick value));
6. the trade-rate floor (D9.3): labels "entries_above_20_per_day" when the member attempted a 21st
   entry (the engine refuses it), "hold_below_2min" when it attempted an exit sooner than 2 full
   minutes after an opening fill (refused likewise), "mean_holding_below_10min" when its mean
   round-trip hold over the window is under 10 minutes; such a member is screened and labelled,
   never dropped;
7. research window only: D5's screen (stage_e_stats.screen) and D4's power check
   (stage_e_stats.power_check at the confirmation supply, when S_X and the step 2 store exist;
   otherwise recorded as not run, with the reason). Lead ruling on runner Q10: D5's screen is
   "mean net P&L > 0 and daily t >= 1.0", so a series with mean <= 0 fails the screen whatever
   its variance (passes False, t None) and the member is Tier B; a zero-variance series leaves
   only its power check undefined, recorded "power check undefined" (a question for the user).
``screen_cluster`` then assigns Tier A / B / excluded with stage_e_stats.assign_tiers.

Records are written once (an existing file is never overwritten). Beside each member record,
``<record name>_trips.json`` (Stage E.4 H1) lists the member's round trips as extract_trips gives
them, each with the sum of its fills' gross_realized_cents, and names the record file and the
sha256 of its bytes; a member without an engine run lists none. Cents are exact: an int, or
"p/q" when a value is not a whole number of cents, with its float beside it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import statistics
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

from data.stage_e_bars import (
    RESEARCH,
    STEP2,
    LegFrame,
    StageEBarRefusal,
    load_confirmation_leg,
    load_research_leg,
    read_leg_dates,
)
from rules.products import product
from screening import harness_freeze
from screening import stage_e_start_dates as start_dates
from screening.stage_e_align import member_coverage, member_window
from screening.stage_e_engine import EngineRefusedCase, EngineResult, Fill, run_engine
from screening.stage_e_freeze import (
    load_cluster_freeze,
    resolve_member,
    verify_cluster_code,
)
from screening.stage_e_frozen import (
    FrozenInputError,
    LegInputs,
    leg_inputs,
    load_frozen_tables,
)
from screening.stage_e_rules import ReleaseCalendar, StageERules, load_release_calendar
from strategy.stage_e.interface import LegSpec

RESEARCH_WINDOW = "research"
CONFIRMATION_WINDOW = "confirmation"
WINDOWS = (RESEARCH_WINDOW, CONFIRMATION_WINDOW)
MEAN_HOLD_MIN_MINUTES = 10.0  # D9.3(c)
# Lead ruling on g2a Q-3: a leg whose start rule found no qualifying month supplies 0 days, so any
# n_b > 0 exceeds the supply and D4 labels the member "inconclusive by design".
EMPTY_WINDOW_NOTE = ("empty confirmation window: supply 0 days, so D4 labels the member "
                     "'inconclusive by design' (n_b > 0 exceeds 0); D4's full-size price-path "
                     "fallback (D2, D4; accepted as the user's call in U8) is the user's decision")
RECORD_SCHEMA = "stage_e_member_record/1"
TRIPS_SCHEMA = "stage_e_member_trips/1"
TRIPS_SUFFIX = "_trips"
CENTS_NOTE = ("net_cents and gross_cents are exact: an int, or 'p/q' when the value is not a "
              "whole number of cents; *_float beside each is float(value)")
LABEL_COVERAGE = "coverage_below_0.95"
LABEL_MEAN_HOLD = "mean_holding_below_10min"
LABEL_ENTRIES = "entries_above_20_per_day"
LABEL_MIN_HOLD = "hold_below_2min"


class RunnerRefusal(RuntimeError):
    """The runner cannot screen this member as asked; nothing is written."""


class StartRuleMissing(RunnerRefusal):
    """The confirmation window needs S_X per leg from a frozen start-rule file."""


class StartWindowEmpty(StartRuleMissing):
    """The start rule found no qualifying month for a root: its confirmation window is empty."""


class StartRuleConflict(RunnerRefusal):
    """Two start-rule files give one root different S_X."""


class StartRuleInvalid(RunnerRefusal):
    """A reports/stage_e_start_rule_*.json file is not a valid start-rule file."""


class StartRuleInconsistent(StartRuleInvalid):
    """A start-rule entry's s_x, v_ref, sensitivity dates or M* do not follow from its own
    monthly medians and first trade dates (review F-3)."""


# --------------------------------------------------------------------- trips ----
@dataclass(frozen=True)
class TripRecord:
    root: str
    open_ts_ns: int
    close_ts_ns: int
    trade_date: date  # the trade date of the closing fill
    net_cents: int | Fraction
    contracts: int  # the largest |position| the trip held
    close_reason: str
    locked: bool  # an exit of this trip waited on a limit lock (R-08)

    @property
    def hold_minutes(self) -> float:
        return (self.close_ts_ns - self.open_ts_ns) / 60e9

    @property
    def net_usd(self) -> float:
        return float(Fraction(self.net_cents) / 100)


def extract_trips(result: EngineResult) -> tuple[TripRecord, ...]:
    """Round trips per leg: the fill run from flat back to flat, in closing order."""
    open_: dict[str, dict] = {}
    trips: list[TripRecord] = []
    for f in result.events(Fill):
        cur = open_.get(f.root)
        if cur is None:
            cur = open_[f.root] = {"start": f.fill_ts_ns, "net": 0, "peak": 0, "locked": False}
        cur["net"] += f.gross_realized_cents - f.commission_cents - f.slippage_cents
        cur["peak"] = max(cur["peak"], abs(f.position_after))
        cur["locked"] = cur["locked"] or f.locked_bars_waited > 0
        if f.position_after == 0:
            if cur["peak"] == 0 or f.trade_date is None:
                raise AssertionError("a trip never held a position -- engine invariant broken")
            trips.append(TripRecord(f.root, cur["start"], f.fill_ts_ns, f.trade_date, cur["net"],
                                    cur["peak"], f.reason, cur["locked"]))
            del open_[f.root]
    if open_:
        raise AssertionError(f"trips never closed on {sorted(open_)} -- engine invariant broken")
    return tuple(trips)


def trip_gross_cents(result: EngineResult, trips: Sequence[TripRecord]
                     ) -> tuple[int | Fraction, ...]:
    """Per trip of ``trips`` (extract_trips of this ``result``), in its order, the sum of the
    trip's fills' gross_realized_cents (the trip list, Stage E.4 H1): extract_trips' flat-to-flat
    grouping replayed over the same Fill events, reading nothing else and changing nothing. A
    replay that does not give the same trips (root, open and close times) raises."""
    open_: dict[str, tuple[int, int | Fraction]] = {}
    out: list[tuple[str, int, int, int | Fraction]] = []
    for f in result.events(Fill):
        start, gross = open_.get(f.root, (f.fill_ts_ns, 0))
        gross = gross + f.gross_realized_cents
        if f.position_after == 0:
            out.append((f.root, start, f.fill_ts_ns, gross))
            open_.pop(f.root, None)
        else:
            open_[f.root] = (start, gross)
    if [o[:3] for o in out] != [(t.root, t.open_ts_ns, t.close_ts_ns) for t in trips]:
        raise AssertionError("the gross replay does not give extract_trips' trips -- the trip "
                             "list would not match the record")
    return tuple(o[3] for o in out)


def _exact_cents(value: int | Fraction) -> int | str:
    """A cents value exactly: the int when it is a whole number of cents, else "p/q"."""
    v = Fraction(value)
    return v.numerator if v.denominator == 1 else f"{v.numerator}/{v.denominator}"


def _utc_iso(ts_ns: int) -> str:
    seconds, nanos = divmod(ts_ns, 1_000_000_000)
    stamp = datetime.fromtimestamp(seconds, UTC).strftime("%Y-%m-%dT%H:%M:%S")
    return f"{stamp}.{nanos:09d}Z" if nanos else f"{stamp}Z"


def trip_rows(trips: Sequence[TripRecord], gross: Sequence[int | Fraction]) -> list[dict]:
    """The trip list's rows: every TripRecord field, its hold, and the trip's gross cents."""
    return [{"root": t.root, "open_ts_ns": t.open_ts_ns, "open_utc": _utc_iso(t.open_ts_ns),
             "close_ts_ns": t.close_ts_ns, "close_utc": _utc_iso(t.close_ts_ns),
             "trade_date": t.trade_date.isoformat(), "contracts": t.contracts,
             "net_cents": _exact_cents(t.net_cents), "net_cents_float": float(t.net_cents),
             "gross_cents": _exact_cents(g), "gross_cents_float": float(g),
             "close_reason": t.close_reason, "locked": t.locked, "hold_minutes": t.hold_minutes}
            for t, g in zip(trips, gross, strict=True)]


def daily_net_cents(result: EngineResult, trips: Sequence[TripRecord]) -> dict[date, Any]:
    out: dict[date, Any] = {}
    for t in trips:
        out[t.trade_date] = out.get(t.trade_date, 0) + t.net_cents
    return out


def trade_rate(result: EngineResult, trips: Sequence[TripRecord]) -> dict:
    per_day: dict[tuple[str, str], int] = {}
    for f in result.events(Fill):
        if f.opening:
            key = (f.root, str(f.trade_date))
            per_day[key] = per_day.get(key, 0) + 1
    holds = [t.hold_minutes for t in trips]
    return {
        "max_entries_per_product_day": max(per_day.values(), default=0),
        "entry_cap_refusals": int(result.counters.get("engine_entry_cap", 0)),
        "min_hold_refusals": int(result.counters.get("engine_min_hold", 0)),
        "mean_hold_minutes": statistics.fmean(holds) if holds else None,
        "min_hold_minutes": min(holds) if holds else None,
        "n_trips": len(trips),
    }


def floor_labels(rate: dict) -> tuple[str, ...]:
    labels = []
    if rate["entry_cap_refusals"] or rate["max_entries_per_product_day"] > 20:
        labels.append(LABEL_ENTRIES)
    if rate["min_hold_refusals"]:
        labels.append(LABEL_MIN_HOLD)
    if rate["mean_hold_minutes"] is not None and rate["mean_hold_minutes"] < MEAN_HOLD_MIN_MINUTES:
        labels.append(LABEL_MEAN_HOLD)
    return tuple(labels)


# ------------------------------------------------------------ frozen inputs ----
def _check_labels() -> None:
    from screening import stage_e_stats as st

    for lab in (LABEL_COVERAGE, LABEL_MEAN_HOLD, LABEL_ENTRIES, LABEL_MIN_HOLD):
        if lab not in st.D9_LABELS:
            raise RunnerRefusal(f"label {lab!r} is not in screening.stage_e_stats.D9_LABELS")


def _start_dates(roots: Sequence[str], allow_empty: bool = False
                 ) -> tuple[dict[str, date], dict]:
    """S_X per root from the one shared loader (screening.stage_e_start_dates, lead ruling OC-K)
    and, per root, the start-rule files and sha256 that give it. StartRuleMissing (or its
    StartWindowEmpty, unless ``allow_empty``), StartRuleConflict or StartRuleInvalid refuse by
    name."""
    return start_dates.start_dates_for(tuple(roots), allow_empty=allow_empty)


def _legs_inputs(legs: Sequence[LegSpec]) -> dict[str, LegInputs]:
    tables = load_frozen_tables()
    out = {leg.root: leg_inputs(leg.root, traded=leg.traded, tables=tables) for leg in legs}
    groups = {product(leg.root).group for leg in legs if leg.traded}
    if len(groups) > 1:
        raise RunnerRefusal(f"traded legs span calendars {sorted(groups)}: the account's trade "
                            "date would be ambiguous (not encoded; the catalog has no such member)")
    return out


def _load_frames(legs: Sequence[LegSpec], inputs: Mapping[str, LegInputs], window: str,
                 research_root: Path, step2_root: Path) -> tuple[dict[str, LegFrame], dict]:
    if window == RESEARCH_WINDOW:
        frames = {}
        for leg in legs:
            sha = inputs[leg.root].research_parquet_sha256
            if sha is None:
                raise RunnerRefusal(f"{leg.root}: no recorded research parquet sha256")
            frames[leg.root] = load_research_leg(leg.root, research_root, expected_sha256=sha)
        return frames, {}
    starts, provenance = _start_dates([leg.root for leg in legs])
    frames = {leg.root: load_confirmation_leg(  # the store S_X was computed from (review F-3)
        leg.root, step2_root, starts[leg.root],
        expected_sha256=provenance[leg.root]["step2_sha256"]) for leg in legs}
    return frames, {"start_rule": provenance,
                    "s_x": {r: starts[r].isoformat() for r in frames}}


def confirmation_supply_days(legs: Sequence[LegSpec], step2_root: Path) -> tuple[int, dict]:
    """Days the member's confirmation window supplies after exclusions (D4), from the step 2
    store's trade dates and roll metadata only (no price column is read). A leg with an empty
    window (no qualifying month) supplies 0 days (lead ruling on g2a Q-3)."""
    starts, provenance = _start_dates([leg.root for leg in legs], allow_empty=True)
    empty = [leg.root for leg in legs if leg.root not in starts]
    if empty:
        return 0, {"start_rule": provenance, "empty_window": empty, "note": EMPTY_WINDOW_NOTE}
    days, black = [], []
    for leg in legs:
        d, b = read_leg_dates(leg.root, step2_root, starts[leg.root],
                              expected_sha256=provenance[leg.root]["step2_sha256"])
        days.append(set(d))
        black.append(b)
    common = set.intersection(*days) - frozenset().union(*black)
    return len(common), {"start_rule": provenance}


# ------------------------------------------------------------------- record ----
def _jsonable(value: Any) -> Any:
    if isinstance(value, Fraction):
        return float(value)
    if isinstance(value, date | datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, list | tuple | set | frozenset):
        items = sorted(value) if isinstance(value, set | frozenset) else value
        return [_jsonable(v) for v in items]
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    return value


def _safe(label: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", label).strip("_")


def write_record(record: dict, out_dir: Path, name: str) -> Path:
    out = Path(out_dir) / f"{_safe(name)}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(_jsonable(record), indent=2, sort_keys=True) + "\n"
    try:
        with out.open("x", encoding="utf-8") as fh:
            fh.write(data)
    except FileExistsError as exc:
        raise RunnerRefusal(f"{out} already exists; records are written once") from exc
    return out


def write_member_record(record: dict, trips: Sequence[dict], out_dir: Path) -> Path:
    """The member record (write_record, unchanged) and beside it its trip list
    ``<record name>_trips.json`` (Stage E.4 H1): the record file's name and the sha256 of the
    bytes written for it, cluster, member, window, status and the trips. Both are written once;
    a trip list already there refuses before the record is written."""
    name = f"{record['cluster']}_{record['member']}_{record['window']}"
    trips_name = f"{name}{TRIPS_SUFFIX}"
    existing = Path(out_dir) / f"{_safe(trips_name)}.json"
    if existing.exists():
        raise RunnerRefusal(f"{existing} already exists; records are written once")
    path = write_record(record, out_dir, name)
    write_record({"schema": TRIPS_SCHEMA, "record_file": path.name,
                  "record_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                  "cluster": record["cluster"], "member": record["member"],
                  "window": record["window"], "status": record["status"], "cents": CENTS_NOTE,
                  "n_trips": len(trips), "trips": list(trips)}, out_dir, trips_name)
    return path


# ------------------------------------------------------------------- screen ----
def _run_member(member: Any, legs: Sequence[LegSpec], inputs: Mapping[str, LegInputs],
                frames: Mapping[str, LegFrame], dates: Sequence[date], blackout: frozenset,
                releases: ReleaseCalendar) -> EngineResult:
    rules = StageERules(inputs, frozenset(dates), frozenset(blackout), releases)
    return run_engine({r: f.frame for r, f in frames.items()}, member, legs, rules)


def _series(label: str, legs: Sequence[LegSpec], inputs: Mapping[str, LegInputs],
            trips: Sequence[TripRecord], dates: Sequence[date]) -> Any:
    from screening import stage_e_stats as st

    traded = [leg.root for leg in legs if leg.traded]
    primary = traded[0]
    if len(traded) == 1:
        return st.daily_series_from_trips(
            label, primary, [st.Trip(t.trade_date, t.net_usd, t.contracts) for t in trips], dates)
    by_day: dict[date, float] = {}
    for t in trips:
        by_day[t.trade_date] = by_day.get(t.trade_date, 0.0) + t.net_usd
    return st.daily_series_from_leg_dollars(label, primary, by_day, dates, len(trips))


def screen_member(cluster: str, label: str, factory: Callable[[], Any] | None,
                  legs: Sequence[LegSpec] | None, window: str, *, harness_sha256: str,
                  research_root: Path, step2_root: Path, out_dir: Path) -> dict:
    """Screen (research) or run (confirmation) one frozen member; returns and writes its record."""
    harness = harness_freeze.preflight(harness_sha256)  # first, before any file is read
    if window not in WINDOWS:
        raise RunnerRefusal(f"window {window!r} is not one of {WINDOWS}")
    _check_labels()
    freeze = load_cluster_freeze(cluster)
    verify_cluster_code(freeze)
    decl, factory = resolve_member(freeze, label, factory)
    if legs is not None and tuple(legs) != decl.legs:
        raise RunnerRefusal(f"{label}: legs {tuple(legs)} differ from the frozen {decl.legs}")
    legs = decl.legs
    inputs = _legs_inputs(legs)
    releases = load_release_calendar()
    frames, extra = _load_frames(legs, inputs, window, Path(research_root), Path(step2_root))
    store = RESEARCH if window == RESEARCH_WINDOW else STEP2
    mw = member_window(frames, store)
    if not mw.dates:
        raise RunnerRefusal(f"{label}: the {window} window is empty after exclusions")
    if not releases.covers(mw.dates):
        raise RunnerRefusal(f"the release calendar ({releases.first}..{releases.last}) does not "
                            f"cover the window {mw.dates[0]}..{mw.dates[-1]}")
    member = factory()
    coverage = member_coverage(frames, mw.dates, getattr(member, "trading_windows", {}))
    record: dict[str, Any] = {
        "schema": RECORD_SCHEMA, "cluster": cluster, "member": label, "ordinal": decl.ordinal,
        "window": window, "legs": [asdict(leg) for leg in legs],
        "primary_vehicle": next(leg.root for leg in legs if leg.traded),
        "harness_sha256": harness, "cluster_freeze_sha256": freeze.sha256,
        "frozen_tables": dict(load_frozen_tables().hashes),
        "release_calendar_sha256": releases.sha256,
        "bars": {r: {"path": Path(f.path).name, "sha256": f.sha256, "rows": len(f.frame),
                     "closure_bars": int(f.frame["in_scheduled_closure"].sum())}
                 for r, f in frames.items()},
        "window_dates": {"n": len(mw.dates), "first": mw.dates[0], "last": mw.dates[-1],
                         "excluded": {k: list(v) for k, v in mw.excluded.items()}},
        "coverage": {r: {"present": c.present, "expected": c.expected, "ratio": c.ratio,
                         "passes": c.passes} for r, c in coverage.items()},
        "created_utc": datetime.now(UTC).isoformat(timespec="seconds"), **extra,
    }
    if not all(c.passes for c in coverage.values()):
        record.update(status="excluded_before_screening", labels=[LABEL_COVERAGE], screen=None,
                      series=None, power=None)
        write_member_record(record, (), out_dir)
        return record
    try:
        result = _run_member(member, legs, inputs, frames, mw.dates, mw.blackout_union, releases)
    except (EngineRefusedCase, FrozenInputError) as exc:
        # OC-T (C-2): a case the frozen rules cannot resolve (EngineRefusedCase) or a frozen
        # input that cannot answer (FrozenInputError, e.g. CostLookupError) is a named
        # member-level refusal; the cluster run continues and lists it.
        record.update(status="refused_case", refusal=f"{type(exc).__name__}: {exc}", labels=[],
                      screen=None, series=None, power=None)
        write_member_record(record, (), out_dir)
        return record
    trips = extract_trips(result)
    rows = trip_rows(trips, trip_gross_cents(result, trips))  # the trip list only (E.4 H1)
    daily = daily_net_cents(result, trips)
    series = _series(label, legs, inputs, trips, mw.dates)
    rate = trade_rate(result, trips)
    record.update(
        status="run", labels=list(floor_labels(rate)), trade_rate=rate,
        engine={"bars": result.bars_processed, "minutes": result.minutes_processed,
                "accounts_started": result.accounts_started, "counters": dict(result.counters),
                "locked_trips": sum(t.locked for t in trips),
                "closure_bars_seen": {leg.root: int(result.counters.get(
                    f"closure_bars_seen:{leg.root}", 0)) for leg in legs},
                "closure_gap_fills": int(result.counters.get(
                    "fill_at_prior_close_closure_gap", 0))},
        series={"unit": "net ticks per contract per day", "vehicle": series.vehicle,
                "dates": list(series.dates), "values": list(series.values),
                "n_trips": series.n_trips},
        daily_net_usd=[float(Fraction(daily.get(d, 0)) / 100) for d in mw.dates])
    record.update(_research_statistics(cluster, decl.ordinal, legs, series, step2_root)
                  if window == RESEARCH_WINDOW else {"screen": None, "power": None})
    write_member_record(record, rows, out_dir)
    return record


def _screen(series: Any) -> Any:
    """D5's screen (stage_e_stats.screen). Lead ruling on runner Q10: D5 is "mean net P&L > 0 and
    daily t >= 1.0", so a finite series with mean <= 0 fails whatever its variance (passes False,
    t None) even where the stats module cannot compute t; any other undefined screen stays a
    named "screen_undefined" (the member is then not tiered)."""
    from screening import stage_e_stats as st

    try:
        return st.screen(series)
    except st.ScreenUndefined as exc:
        values = [float(v) for v in series.values]
        if values and all(math.isfinite(v) for v in values) and statistics.fmean(values) <= 0.0:
            return st.ScreenResult(member_id=series.member_id, n_days=len(values),
                                   n_trips=series.n_trips, mean_ticks=statistics.fmean(values),
                                   sd_pop_ticks=statistics.pstdev(values), t_daily=None,
                                   passes=False)
        return {"status": "screen_undefined", "reason": str(exc)}


def _research_statistics(cluster: str, ordinal: int, legs: Sequence[LegSpec], series: Any,
                         step2_root: Path) -> dict:
    """D5's screen and D4's power check. A member whose series has mean <= 0 fails the screen
    (Tier B, lead ruling on Q10); a zero-variance series leaves its power check undefined, which
    is recorded by name ("power check undefined", a question for the user) and the run goes on."""
    from screening import stage_e_stats as st

    screen = _screen(series)
    try:
        supply, meta = confirmation_supply_days(legs, Path(step2_root))
    except (RunnerRefusal, StageEBarRefusal) as exc:  # named refusals, recorded, never guessed
        return {"screen": screen, "power": {"status": "not_run",
                                            "reason": f"{type(exc).__name__}: {exc}"}}
    try:
        check = st.power_check(series, cluster, ordinal, supply)
    except st.PowerCheckUndefined as exc:
        return {"screen": screen, "power": {"status": "power check undefined",
                                            "supply_days": supply, "reason": str(exc), **meta}}
    return {"screen": screen, "power": {"status": "run", "supply_days": supply, **meta,
                                        "check": check}}


def screen_cluster(cluster: str, window: str, *, harness_sha256: str, research_root: Path,
                   step2_root: Path, out_dir: Path) -> dict:
    """Every member of the cluster's freeze, in ordinal order, then D5's tiers (research)."""
    harness_freeze.preflight(harness_sha256)
    freeze = load_cluster_freeze(cluster)
    records = [screen_member(cluster, m.label, None, m.legs, window,
                             harness_sha256=harness_sha256, research_root=research_root,
                             step2_root=step2_root, out_dir=out_dir)
               for m in sorted(freeze.members, key=lambda m: m.ordinal)]
    out: dict[str, Any] = {"cluster": cluster, "window": window,
                           "refused_members": {r["member"]: r["refusal"] for r in records
                                               if r["status"] == "refused_case"},
                           "members": [r["member"] for r in records]}
    if window == RESEARCH_WINDOW:
        from screening import stage_e_stats as st

        tierable = [r for r in records if r["status"] != "refused_case"
                    and not isinstance(r.get("screen"), dict)]
        tiers = st.assign_tiers(cluster, [st.TierInput(r["member"], r.get("screen"),
                                                       tuple(r.get("labels", ())))
                                          for r in tierable]) if tierable else None
        out["tiers"] = tiers
        out["not_tiered"] = {r["member"]: r.get("refusal") or r["screen"]["status"]
                             for r in records if r not in tierable}
        out["power_check_undefined"] = [  # tiered as usual; the undefined check is a user question
            r["member"] for r in records
            if isinstance(r.get("power"), dict) and r["power"].get("status")
            == "power check undefined"]
    write_record({**out, "harness_sha256": records[0]["harness_sha256"] if records else None},
                 out_dir, f"{cluster}_{window}_cluster")
    return out


# ---------------------------------------------------------------------- CLI ----
def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--harness-sha256", required=True)
    parser.add_argument("--cluster", required=True)
    who = parser.add_mutually_exclusive_group(required=True)
    who.add_argument("--member")
    who.add_argument("--all", action="store_true")
    parser.add_argument("--window", required=True, choices=WINDOWS)
    parser.add_argument("--research-root", required=True, type=Path)
    parser.add_argument("--step2-root", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    from compute.platform import lower_priority

    lower_priority()
    common = {"harness_sha256": args.harness_sha256, "research_root": args.research_root,
              "step2_root": args.step2_root, "out_dir": args.out_dir}
    if args.all:
        out = screen_cluster(args.cluster, args.window, **common)
        print(f"{args.cluster} {args.window}: {len(out['members'])} members, "
              f"{len(out['refused_members'])} refused")
        for member, why in out["refused_members"].items():
            print(f"REFUSED {member}: {why}")
    else:
        rec = screen_member(args.cluster, args.member, None, None, args.window, **common)
        print(f"{args.cluster} {args.member} {args.window}: {rec['status']} {rec['labels']}")
    return 0


if __name__ == "__main__":
    # C-1 (E.3 return, section 7; E.4 H1): under `python -m` this file runs as __main__, a second
    # copy of the module, while screening.stage_e_start_dates raises screening.stage_e_runner's
    # refusal classes. Run that module's main(), so one module object raises and catches them
    # however the runner is launched.
    from screening import stage_e_runner

    sys.exit(stage_e_runner.main())
