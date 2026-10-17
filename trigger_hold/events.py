"""Trigger extraction (lead_spec section 6; TriggerCoder brief): a FROZEN member, run unchanged
by the Stage E engine on a window's minute bars, gives its ENTRY EVENTS only.

    python -m trigger_hold.events extract --trigger "K2-monthend-01 ZN" --window ext|cf \
        --out reports/stage_e23_events/K2-monthend-01_ZN__ext.json
    python -m trigger_hold.events validate --trigger "K2-monthend-01 ZN" \
        --out reports/stage_e23_events/validation/K2-monthend-01_ZN__cf.json

A Stage E cluster member runs on the harness's own path (screening/stage_e_runner.screen_member
steps 1-4): harness preflight (the v13 sha256, first); the cluster freeze, its code verified, the
member resolved and built by its frozen factory (trigger_hold.events_members); bars per leg
(trigger_hold.events_bars: base_rules.store.load_product, then the engine's full column set of
the same checked file); screening.stage_e_align.member_window; the release calendar; then
screening.stage_e_engine.run_engine with screening.stage_e_rules.StageERules, unchanged: every
structural refusal, the D9 guards, the flatten and no-new windows (rules/sessions.py united with
the bars' flags), the roll blackout, the instrument guard, the fill guard, the CPI window, the
price-limit rule and the account gate. W_cf uses the frozen 2019-on inputs as the harness does;
W_ext runs inside trigger_hold.events_context.hist_context() (pattern_search.backward's 2010-2019
swap of calendars, session rules and member tables, plus the release rows of base_rules.costs).
E20H6-T1 runs through the frozen h6_rod code instead (trigger_hold.events_h6).

What is kept. An entry event is an opening strategy fill of the engine (Fill.reason "strategy",
Fill.opening True): d0 = the trade date of the decision bar, tau = the decision instant (the
decision bar's close = its open + 60 s, UTC ns), side +1 buy / -1 sell. The engine's ledger also
holds fill prices, exits and P&L: nothing but those three fields is read from a fill; nothing
else is written, printed or logged, and the ledger is dropped once counted. Counts (integers):
entry intents accepted and refused by the engine's reason, accepted entry orders cancelled
before filling by reason, D9 coverage minutes, window exclusions, and for table members each
table date of the window by outcome (not a trade date, outside the member window, decision bar
missing, early halt, entered, no entry otherwise). Exit-side facts (exit orders, forced
flattens, MLL liquidations, the engine's counters) are never counted.

Windows (lead message, shortlist): W_ext events on trade dates 2011-06-01..2019-04-30 (the book
starts 2011-07-27; earlier events let its first units exist); W_cf 2019-05-06 (or the declared
S_X if later)..2024-02-29.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import sys
from collections import Counter
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from base_rules import constants as BK
from data.stage_e_bars import LegFrame
from screening import harness_freeze
from screening.stage_e_align import member_window
from screening.stage_e_engine import Cancel, EngineResult, Fill, IntentRecord, run_engine
from screening.stage_e_frozen import leg_inputs, load_frozen_tables, sha256_file
from screening.stage_e_rules import ReleaseCalendar, StageERules, load_release_calendar
from strategy.interface import NS_PER_BAR
from trigger_hold import constants as TC
from trigger_hold import events_bars as EB
from trigger_hold import events_members as EM
from trigger_hold import events_tables as ET
from trigger_hold.types import TriggerEvent, events_record

HARNESS_SHA256 = "dd2bcc6025144e0debd19be1ca8d43c983872a27c9258895ef55ee3c138609e4"  # v13
W_EXT_EVENTS_FIRST = date(2011, 6, 1)  # lead message (shortlist): events from 2011-06
WINDOW_ARGS = {"ext": EB.W_EXT, "cf": EB.W_CF}
META_SCHEMA = "stage_e23_events_meta/1"
VALIDATION_SCHEMA = "stage_e23_events_validation/1"
CODE_FILES = ("trigger_hold/events.py", "trigger_hold/events_bars.py",
              "trigger_hold/events_context.py", "trigger_hold/events_members.py",
              "trigger_hold/events_tables.py", "trigger_hold/types.py")


class ExtractionRefused(RuntimeError):
    """The extraction cannot run as declared (refused by name before anything is written)."""


@dataclass(frozen=True)
class Capture:
    events: tuple[tuple[date, int, int], ...]  # (d0, tau_ns, side)
    counts: Mapping[str, int]


# ------------------------------------------------------------------ capture ----
def _frame(x: LegFrame | pd.DataFrame) -> pd.DataFrame:
    return x.frame if isinstance(x, LegFrame) else x


def _decision_trade_date(ts: np.ndarray, labels: np.ndarray, root: str, decision_ns: int
                         ) -> date:
    bar_open = decision_ns - NS_PER_BAR
    i = int(np.searchsorted(ts, bar_open))
    if i >= len(ts) or int(ts[i]) != bar_open:
        raise ExtractionRefused(f"{root}: no decision bar at {bar_open} for an entry")
    return date.fromisoformat(str(labels[i]))


def entries_of(result: EngineResult, frames: Mapping[str, LegFrame | pd.DataFrame]) -> Capture:
    """The engine's opening strategy fills as (d0, tau, side), and counts by reason."""
    lookup = {r: (_frame(f)["ts_event"].to_numpy(dtype="int64"),
                  _frame(f)["trade_date"].astype(str).to_numpy()) for r, f in frames.items()}
    counts: Counter[str] = Counter()
    events = []
    entry_decisions: set[int] = set()  # decision instants of accepted entry intents
    cancels: list[Cancel] = []
    for item in result.ledger:
        if isinstance(item, Fill):
            if item.reason == "strategy" and item.opening:
                ts, labels = lookup[item.root]
                d0 = _decision_trade_date(ts, labels, item.root, int(item.decision_ts_ns))
                events.append((d0, int(item.decision_ts_ns), 1 if item.side == "buy" else -1))
        elif isinstance(item, IntentRecord):
            if item.position_before == 0 and item.pending_before == 0:
                if item.accepted:
                    counts["entry_intent_accepted"] += 1
                    entry_decisions.add(int(item.decision_ts_ns))
                else:
                    reason = item.refusal.reason if item.refusal is not None else "unknown"
                    counts[f"entry_intent_refused:{reason}"] += 1
        elif isinstance(item, Cancel):
            cancels.append(item)
    # Only entry-side facts are counted: an accepted entry order that never filled, by the
    # engine's reason. Exit orders, forced flattens, MLL liquidations and the engine's other
    # counters concern the path after the decision bar and are not read (brief: nothing after
    # the decision bar is written).
    for c in cancels:
        if int(c.decision_ts_ns) in entry_decisions:
            counts[f"entry_order_cancelled:{c.reason}"] += 1
    counts["entries"] = len(events)
    if len(set(events)) != len(events):
        raise ExtractionRefused("two identical entry events")
    return Capture(tuple(sorted(events)), dict(counts))


def _halted(value: Any) -> bool:
    return str(value) not in ("", "None", "nan", "NaT")


def schedule_counts(member: Any, frames: Mapping[str, LegFrame], window_dates: Sequence[date],
                    first: date, last: date, events: Sequence[tuple[date, int, int]]
                    ) -> dict[str, int]:
    """For a table member: each table date of first..last by outcome, from timestamps, trade
    dates and the early-halt flag only (no price)."""
    from strategy.members.k2._event_common import ct_open_ns

    plans = EM.decision_schedule(member)
    if plans is None:
        return {}
    root = next(r for r, f in frames.items() if r == getattr(member, "root", r))
    leg = frames[root]
    ts = leg.frame["ts_event"].to_numpy(dtype="int64")
    labels = leg.frame["trade_date"].astype(str).to_numpy()
    halts = leg.frame["early_halt_ct"].to_numpy()
    trade_dates, window = set(leg.trade_dates), set(window_dates)
    entered = {d for d, _, _ in events}
    counts: Counter[str] = Counter()
    for day in sorted(d for d in plans if first <= d <= last):
        counts["table_dates_in_window_range"] += 1
        if day not in trade_dates:
            counts["table_date:not_a_trade_date"] += 1
            continue
        if day not in window:
            counts["table_date:outside_member_window (roll blackout)"] += 1
            continue
        target = ct_open_ns(day, plans[day])
        i = int(np.searchsorted(ts, target))
        if i >= len(ts) or int(ts[i]) != target or labels[i] != day.isoformat():
            counts["table_date:decision_bar_missing"] += 1
        elif _halted(halts[i]):
            counts["table_date:early_halt"] += 1
        elif day in entered:
            counts["table_date:entered"] += 1
        else:
            counts["table_date:no_entry_other (no signal, instrument guard or refusal)"] += 1
    counts["window_dates_not_table_dates"] = len([d for d in window if d not in plans])
    return dict(counts)


# ------------------------------------------------------------------ the run ----
def legs_inputs(legs: Sequence[Any]) -> dict[str, Any]:
    """screening.stage_e_runner._legs_inputs, step for step (the frozen tables per leg)."""
    tables = load_frozen_tables()
    return {leg.root: leg_inputs(leg.root, traded=leg.traded, tables=tables) for leg in legs}


def run_member(member: Any, legs: Sequence[Any], frames: Mapping[str, LegFrame], store: str,
               releases: ReleaseCalendar) -> tuple[Capture, Any]:
    """member_window, StageERules and run_engine exactly as screen_member runs them."""
    mw = member_window(frames, store)
    if not mw.dates:
        raise ExtractionRefused("the window is empty after exclusions")
    if not releases.covers(mw.dates):
        raise ExtractionRefused(f"the release calendar ({releases.first}..{releases.last}) does "
                                f"not cover {mw.dates[0]}..{mw.dates[-1]}")
    rules = StageERules(legs_inputs(legs), frozenset(mw.dates), frozenset(mw.blackout_union),
                        releases)
    result = run_engine({r: f.frame for r, f in frames.items()}, member, legs, rules)
    capture = entries_of(result, frames)
    del result  # prices, exits and P&L are dropped here, unread
    return capture, mw


def _file_role(path: str | Path) -> dict[str, str]:
    return {"path": str(path), "sha256": sha256_file(BK.repo_path(path))}


def window_bounds(window: str, store_roots: Sequence[str]) -> tuple[date, date, str]:
    if window == EB.W_EXT:
        return W_EXT_EVENTS_FIRST, TC.W_EXT_LAST, "W_ext events: lead message (2011-06-01)"
    from screening import stage_e_start_dates as sd
    from screening.stage_e_runner import StartRuleMissing

    try:
        starts, _ = sd.start_dates_for(tuple(store_roots), allow_empty=True)
    except StartRuleMissing:
        starts = {}
    declared = [starts[r] for r in store_roots if r in starts]
    if declared and max(declared) > TC.W_CF_FIRST:
        return max(declared), TC.W_CF_LAST, "W_cf: the declared S_X"
    note = "the declared S_X is not later" if declared else "no start rule lists the store root"
    return TC.W_CF_FIRST, TC.W_CF_LAST, f"W_cf: 2019-05-06 ({note})"


@contextlib.contextmanager
def window_context(window: str) -> Iterator[dict[str, Any]]:
    """W_cf: nothing replaced (the harness's frozen inputs). W_ext: hist_context()."""
    if window == EB.W_CF:
        yield {"release_calendar": load_release_calendar(), "not_reproduced": [],
               "inputs": {"release_calendar": _file_role(ET.FROZEN_CALENDAR_PATH)}}
        return
    from trigger_hold.events_context import backward_inputs, hist_context

    with hist_context() as ctx:
        yield {"release_calendar": ctx["release_rules"].calendar,
               "not_reproduced": ctx["not_reproduced"], "inputs": backward_inputs()}


def _calendar_roles(loaded: Mapping[str, EB.LoadedLeg]) -> dict[str, Any]:
    out = {}
    for root, ld in loaded.items():
        cal = ld.calendar
        if getattr(cal, "file_path", None):
            out[f"calendar:{root}"] = {"path": str(cal.file_path), "sha256": cal.file_sha256}
        else:
            for i, p in enumerate(getattr(cal, "module_paths", ()) or ()):
                out[f"calendar:{root}:{i}"] = _file_role(Path(p))
    return out


def extract(trigger_id: str, window: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """(the events record of trigger_hold.types, the meta record). Nothing is written here."""
    if window not in (EB.W_EXT, EB.W_CF):
        raise ExtractionRefused(f"window {window!r}")
    from trigger_hold.events_h6 import extract_h6, is_h6

    if is_h6(trigger_id):
        return extract_h6(window)
    harness = harness_freeze.preflight(HARNESS_SHA256)
    spec = EM.spec_for(trigger_id)
    if window == EB.W_EXT:
        EM.check_table_need(spec)
    decl, _, _ = EM.resolve(spec)
    legs = decl.legs
    store_roots = [EB.store_root_of(leg.root) for leg in legs]
    first, last, bounds_source = window_bounds(window, store_roots)
    man = EB.manifest()
    calendars = EB.load_calendars_for([leg.root for leg in legs])
    loaded = {leg.root: EB.load_leg(leg.root, window, first, last, run_manifest=man,
                                    calendars=calendars) for leg in legs}
    frames = {r: ld.leg for r, ld in loaded.items()}
    eras = {ld.era for ld in loaded.values()}
    if len(eras) != 1:
        raise ExtractionRefused(f"legs come from several eras {sorted(eras)}")
    table = None
    if window == EB.W_EXT and spec.injection is not None:
        table = ET.TABLE_BUILDERS[spec.injection.table](first, last)
    with window_context(window) as ctx:
        built = EM.build_member(spec, table, first, last)
        capture, mw = run_member(built.member, legs, frames, eras.pop(), ctx["release_calendar"])
        sched = schedule_counts(built.member, frames, mw.dates, first, last, capture.events)
        releases = ctx["release_calendar"]
        not_reproduced, ctx_inputs = list(ctx["not_reproduced"]), dict(ctx["inputs"])
    coverage = {r: EB.leg_coverage_on(loaded[r].calendar, frames[r], mw.dates,
                                      built.member.trading_windows[r]) for r in frames}
    counts = dict(capture.counts)
    for r, c in coverage.items():
        counts[f"coverage_present_minutes:{r}"] = int(c.present)
        counts[f"coverage_expected_minutes:{r}"] = int(c.expected)
    counts["window_trade_dates"] = len(mw.dates)
    for cause, days in mw.excluded.items():
        counts[f"window_excluded:{cause}"] = len(days)
    counts.update(sched)
    if table is not None:
        counts.update({f"table:{k}": int(v) for k, v in table.counts.items()})
    book_root = store_roots[[leg.traded for leg in legs].index(True)]
    if book_root not in TC.ROOTS:
        raise ExtractionRefused(f"{trigger_id}: book root {book_root} is not an E.21 root")
    inputs: dict[str, Any] = {
        "harness_freeze": {"path": "reports/stage_e2b_harness_freeze.json", "sha256": harness},
        "run_manifest": _file_role(EB.RUN_MANIFEST_PATH),
        "cluster_freeze": {"path": f"reports/stage_e_{spec.cluster.lower()}_member_freeze.json",
                           "sha256": built.freeze_sha256},
        "member_module": _file_role(decl.module.replace(".", "/") + ".py")}
    for r, ld in loaded.items():
        inputs[f"store:{r}"] = {"path": ld.info["path"], "sha256": ld.info["sha256"]}
        for s in ld.info["stores_checked"]:
            inputs[f"store_checked:{r}:{s['era']}"] = {"path": s["path"], "sha256": s["sha256"]}
    inputs.update(ctx_inputs)
    inputs.update(_calendar_roles(loaded))
    if table is not None:
        inputs.update({f"table:{k}": dict(v) for k, v in table.sources.items()})
    for f in CODE_FILES:
        inputs[f"code:{f}"] = _file_role(f)
    events = [TriggerEvent(d, tau, s, spec.trigger_id) for d, tau, s in capture.events]
    record = events_record(spec.trigger_id, book_root, window, events, counts, inputs)
    meta = {"schema": META_SCHEMA, "trigger_id": spec.trigger_id, "window": window,
            "first": first.isoformat(), "last": last.isoformat(), "bounds_source": bounds_source,
            "member": decl.as_dict(),
            "store_roots": dict(zip([leg.root for leg in legs], store_roots, strict=True)),
            "coverage": {r: {"present": c.present, "expected": c.expected,
                             "ratio": round(c.ratio, 6), "passes_0.95": c.passes}
                         for r, c in coverage.items()},
            "table": None if table is None else {"kind": table.kind, "rows": len(table.rows)},
            "release_calendar": {"first": releases.first.isoformat(),
                                 "last": releases.last.isoformat(), "sha256": releases.sha256},
            "engine_rules_not_reproduced": not_reproduced,
            "bars": {r: dict(ld.info) for r, ld in loaded.items()}}
    return record, meta


# ------------------------------------------------------------------ CLI ----
def write_once(path: Path, body: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as fh:
        fh.write(json.dumps(body, indent=1) + "\n")


def meta_path(out: Path) -> Path:
    return out.with_name(out.stem + ".meta.json")


def _summary(record: Mapping[str, Any]) -> str:
    c = record["counts"]
    keys = [k for k in sorted(c) if k.startswith(("entries", "table_date:", "entry_intent",
                                                  "schedule_"))]
    return "; ".join(f"{k}={c[k]}" for k in keys)


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m trigger_hold.events")
    sub = p.add_subparsers(dest="cmd", required=True)
    ex = sub.add_parser("extract")
    ex.add_argument("--trigger", required=True)
    ex.add_argument("--window", required=True, choices=sorted(WINDOW_ARGS))
    ex.add_argument("--out", required=True, type=Path)
    va = sub.add_parser("validate")
    va.add_argument("--trigger", required=True)
    va.add_argument("--out", required=True, type=Path)
    a = p.parse_args(argv)
    with contextlib.suppress(OSError):
        os.nice(10)
    out = Path(a.out)
    if out.exists() or meta_path(out).exists():
        print(f"refused: {out} (or its meta file) exists; outputs are written once")
        return 2
    if a.cmd == "extract":
        record, meta = extract(a.trigger, WINDOW_ARGS[a.window])
        write_once(out, record)
        write_once(meta_path(out), meta)
        print(f"wrote {out}: {len(record['events'])} events; {_summary(record)}")
        return 0
    from trigger_hold.events_validate import validate

    body = validate(a.trigger)
    write_once(out, body)
    print(f"wrote {out}: identical={body['identical']} same_d0_side={body['same_d0_and_side']} "
          f"adapter={body['adapter']['n']} harness={body['harness']['n']} "
          f"differences={len(body['differences'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
