"""E20H6-T1 on NQ: trigger extraction through the frozen h6_rod code (lead message: shortlist).

The rule is not reimplemented: h6_rod.signal.compute_facts and t1_schedule give the schedule
(every eligible equity trade date: both signal bars present with one instrument_id and r_ROD != 0,
side sign(r_ROD)), and h6_rod.engine.run_schedule runs it through the Stage E engine on MNQ with
NQ's bars, exactly as h6_rod.run.evaluate does (vehicle_blackout of NQ's L-8 blackout, the
window's equity trade dates as window dates, ENGINE_LEAD_IN_DATES lead-in dates without entries,
the release calendar). An entry event is the engine's opening strategy fill
(trigger_hold.events.entries_of): d0, tau = the close of the C-31 bar, side. A shortened day is
refused by the engine as in E.20 (F = C-30 on an early-close date under the Topstep lead).

Bars: trigger_hold.events_bars.load_leg("MNQ", ...) (NQ's E.17 stores through
base_rules.store.load_product). W_cf: 2019-05-06..2024-02-29 on the frozen equity calendar and the
frozen release calendar (h6_rod.run's own inputs); the lead-in is h6_rod.clock.lead_in_dates (none
before the store's first date). W_ext: 2011-06-01..2019-04-30 inside
trigger_hold.events_context.hist_context() with the hist equity calendar passed explicitly to
every h6_rod.clock / signal call; the lead-in is the same rule (ENGINE_LEAD_IN_DATES previous
equity trade dates) without h6_rod's clamp at 2019-05-06, which is the step 2 store's first date
and has no meaning on the ext2010 store (it also gives the first window date its prior-close bar).
Nothing about r_ROD's value, a price, a fill price or P&L is written.
"""

from __future__ import annotations

from collections import Counter
from datetime import date
from typing import Any

from screening import harness_freeze
from screening.stage_e_frozen import sha256_file
from trigger_hold import constants as TC
from trigger_hold import events_bars as EB

H6_TRIGGER_ID = "E20H6-T1 NQ"
H6_IDS = ("E20H6-T1 NQ", "E20H6-T1_NQ", "E20H6-T1")
H6_FILES = ("__init__.py", "__main__.py", "clock.py", "constants.py", "engine.py", "gex.py",
            "guard.py", "member.py", "preflight.py", "report.py", "results_io.py", "run.py",
            "signal.py", "stats.py")
W_EXT_EVENTS_FIRST = date(2011, 6, 1)


def is_h6(trigger_id: str) -> bool:
    return trigger_id.strip() in H6_IDS


def h6_inputs() -> dict[str, dict[str, str]]:
    """The sha256 of every h6_rod file imported, and the prereg (lead: record them)."""
    from base_rules import constants as BK

    out = {}
    for name in H6_FILES:
        rel = f"h6_rod/{name}"
        out[f"code:{rel}"] = {"path": rel, "sha256": sha256_file(BK.repo_path(rel))}
    for rel in ("reports/stage_e20_prereg_H6.md", "reports/stage_e20_h6_freeze.json"):
        out[f"h6:{rel}"] = {"path": rel, "sha256": sha256_file(BK.repo_path(rel))}
    return out


def _lead_in(first: date, n: int, cal: Any, floor: date) -> tuple[date, ...]:
    from h6_rod import clock

    out, day = [], first
    for _ in range(n):
        prev = clock.previous_trade_date(day, cal)
        if prev is None or prev < floor:
            break
        out.append(prev)
        day = prev
    return tuple(sorted(out))


def _run(window: str, first: date, last: date, cal: Any, releases: Any,
         loaded: EB.LoadedLeg, lead_in: tuple[date, ...]) -> tuple[Any, dict[str, int]]:
    from h6_rod import clock, signal
    from h6_rod import engine as H6E
    from trigger_hold.events import entries_of

    frame = loaded.leg.frame
    days = clock.trade_dates(first, last, cal)
    facts = signal.compute_facts(frame[["ts_event", "close", "instrument_id"]], days, cal)
    sched = signal.t1_schedule(facts, first, last, cal)
    blackout = H6E.vehicle_blackout(frozenset(loaded.leg.roll_blackout))
    run = H6E.run_schedule(frame, sched, days, lead_in, blackout, releases)
    capture = entries_of(run.result, {"MNQ": frame})
    del run  # prices, exits and P&L dropped unread
    counts: Counter[str] = Counter(capture.counts)
    counts["window_trade_dates"] = len(days)
    counts["lead_in_dates"] = len(lead_in)
    counts["schedule_entries"] = len(sched.entries)
    for reason, n in sched.reason_counts().items():
        counts[f"schedule_excluded:{reason}"] = n
    entered = {d for d, _, _ in capture.events}
    counts["schedule_entry_not_entered"] = len([d for d in sched.entries if d not in entered])
    counts["shortened_window_dates"] = sum(1 for d in days if clock.is_shortened(d, cal))
    counts["schedule_entries_on_shortened_dates"] = sum(
        1 for d in sched.entries if clock.is_shortened(d, cal))
    counts["roll_blackout_window_dates"] = len([d for d in days if d in blackout])
    return capture, dict(counts)


def extract_h6(window: str) -> tuple[dict[str, Any], dict[str, Any]]:
    from h6_rod import clock
    from h6_rod import constants as K
    from trigger_hold.events import HARNESS_SHA256, _file_role
    from trigger_hold.events_context import backward_inputs, hist_context
    from trigger_hold.types import TriggerEvent, events_record

    harness = harness_freeze.preflight(HARNESS_SHA256)
    n_lead = int(K.ENGINE_LEAD_IN_DATES or 0)
    man = EB.manifest()
    cals = EB.load_calendars_for(["MNQ"])
    if window == EB.W_CF:
        cal = clock.equity_calendar()
        first, last = TC.W_CF_FIRST, TC.W_CF_LAST
        lead_in = clock.lead_in_dates(first, n_lead, cal)
        loaded = EB.load_leg("MNQ", window, min((first, *lead_in)), last, run_manifest=man,
                             calendars=cals)
        from screening.stage_e_rules import load_release_calendar

        releases = load_release_calendar()
        capture, counts = _run(window, first, last, cal, releases, loaded, lead_in)
        extra_inputs = {"release_calendar": _file_role("reports/stage_e2b_release_calendar.json")}
        not_reproduced: list[str] = []
    elif window == EB.W_EXT:
        first, last = W_EXT_EVENTS_FIRST, TC.W_EXT_LAST
        hist_cal = cals["equity"].hist
        lead_in = _lead_in(first, n_lead, hist_cal, date(2010, 6, 7))
        loaded = EB.load_leg("MNQ", window, min((first, *lead_in)), last, run_manifest=man,
                             calendars=cals)
        with hist_context() as ctx:
            cal = ctx["tables"].calendars["equity"]
            capture, counts = _run(window, first, last, cal, ctx["release_rules"].calendar,
                                   loaded, lead_in)
            not_reproduced = list(ctx["not_reproduced"])
        extra_inputs = backward_inputs()
    else:
        raise ValueError(f"window {window!r}")
    inputs: dict[str, Any] = {
        "harness_freeze": {"path": "reports/stage_e2b_harness_freeze.json", "sha256": harness},
        "run_manifest": _file_role(EB.RUN_MANIFEST_PATH),
        "store:MNQ": {"path": loaded.info["path"], "sha256": loaded.info["sha256"]}}
    for s in loaded.info["stores_checked"]:
        inputs[f"store_checked:MNQ:{s['era']}"] = {"path": s["path"], "sha256": s["sha256"]}
    inputs.update(h6_inputs())
    inputs.update(extra_inputs)
    for f in ("trigger_hold/events.py", "trigger_hold/events_bars.py",
              "trigger_hold/events_context.py", "trigger_hold/events_h6.py",
              "trigger_hold/types.py"):
        inputs[f"code:{f}"] = _file_role(f)
    events = [TriggerEvent(d, tau, s, H6_TRIGGER_ID) for d, tau, s in capture.events]
    record = events_record(H6_TRIGGER_ID, "NQ", window, events, counts, inputs)
    meta = {"schema": "stage_e23_events_meta/1", "trigger_id": H6_TRIGGER_ID, "window": window,
            "first": first.isoformat(), "last": last.isoformat(),
            "lead_in": [d.isoformat() for d in lead_in], "vehicle": "MNQ", "price_path": "NQ",
            "engine_rules_not_reproduced": not_reproduced, "bars": dict(loaded.info)}
    return record, meta


__all__ = ["H6_TRIGGER_ID", "extract_h6", "h6_inputs", "is_h6"]
