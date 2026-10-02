"""Stage E.9 K8-flight-01 of MemberCoder-A, part 3: engine-level tests (reports/stage_e9_member_
specs.md section 1, S0.5, S0.7, the S0 preamble; V16(a), D4, D11.5). The member runs through the
frozen Stage E engine (screening.stage_e_engine.run_engine) on synthetic two-leg frames, as
tests/test_stage_e_alignment.py does with an MES signal leg; the window and the union of the
legs' roll blackouts come from the frozen screening.stage_e_align.member_window, as the runner
builds them. No bar file is read.

Frames: the 20 reference dates of DAY carry the MES block bars of the kit (dips 1..10 ticks:
Q(DAY) = -3/B); DAY carries MES bars every minute 08:29..14:54 (close B, a 5-tick dip on the bar
at 08:44, so r_3 = -5/B triggers at t_3 = 08:45) and MGC bars every minute 08:30..15:10.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, date, datetime, time

import pandas as pd

from data.stage_e_bars import RESEARCH, LegFrame
from rules import sessions
from rules.products import product
from screening.stage_e_align import member_window
from screening.stage_e_engine import EngineResult, Fill, IntentRecord, run_engine
from screening.stage_e_frozen import leg_inputs
from screening.stage_e_rules import StageERules
from strategy.members.k8 import flight
from strategy.members.k8.flight import FlightToGold, reference_dates
from strategy.stage_e.interface import LegSpec
from tests._stage_e_canary_kit import NO_RELEASES, rules_for
from tests.test_k8_members_flight import (
    BLOCK_BARS,
    CT,
    DAY,
    DIPS,
    MES_ID,
    MGC_ID,
    NS,
    B,
    G,
    dip_path,
    end_bar,
    hm,
)
from tests.test_stage_e_rules import Script

LEGS = (LegSpec("MGC", True), LegSpec("MES", False))
REFS = reference_dates(DAY)
WINDOW = (*REFS, DAY)
DIP_K = 3  # the trigger block on DAY: entry bar 08:44, fill 08:45


def _rows(root: str, bars: Iterable[tuple[date, int, int, int]]) -> pd.DataFrame:
    """Flat bars (open = high = low = close) from (CT date, minute of day, close ticks, id), with
    the session flags of rules/sessions.py."""
    tick_fixed = product(root).vendor_tick_fixed
    rows = []
    for day, minute, close, iid in bars:
        local = datetime.combine(day, time(*divmod(minute, 60)), tzinfo=CT)
        state = sessions.session_state(root, local.astimezone(UTC))
        px = close * tick_fixed / 1e9
        rows.append({
            "ts_event": int(local.astimezone(UTC).timestamp()) * NS,
            "open": px, "high": px, "low": px, "close": px, "volume": 1,
            "instrument_id": iid, "raw_symbol": f"{root}U5", "trade_date": day.isoformat(),
            "in_flatten_window": bool(state.must_be_flat),
            "in_no_new_positions_window": bool(not state.can_open),
            "early_halt_ct": "", "in_scheduled_closure": False, "is_roll_session": False,
            "gap_before_minutes": 0, "vendor_degraded_day": False,
        })
    return pd.DataFrame(rows)


def frames(*, mes_skip: Iterable[int] = ()) -> dict[str, pd.DataFrame]:
    skip = set(mes_skip)
    mes_bars = []
    for i, ref in enumerate(REFS):
        dip = {10: DIPS[i]} if i < len(DIPS) else {}
        mes_bars += [(ref, BLOCK_BARS[j], c, MES_ID) for j, c in enumerate(dip_path(dip))]
    dip_bar = end_bar(DIP_K)
    mes_bars += [(DAY, m, B - 5 if m == dip_bar else B, MES_ID)
                 for m in range(hm(8, 29), hm(14, 55)) if m not in skip]
    mgc_bars = [(DAY, m, G, MGC_ID) for m in range(hm(8, 30), hm(15, 11))]
    return {"MGC": _rows("MGC", mgc_bars), "MES": _rows("MES", mes_bars)}


def run(member: object, frame_map: dict[str, pd.DataFrame], rules: object | None = None
        ) -> EngineResult:
    return run_engine(frame_map, member, LEGS, rules or rules_for(LEGS, WINDOW))


def ct_hm(ns: int) -> str:
    return f"{datetime.fromtimestamp(ns / NS, tz=UTC).astimezone(CT):%H:%M}"


def fills(res: EngineResult) -> list[tuple[str, str, str, int, str]]:
    return [(f.root, ct_hm(f.fill_ts_ns), f.side, f.qty, f.reason) for f in res.events(Fill)]


def intents(res: EngineResult) -> list[tuple[str | None, str, str | None]]:
    """(root, the emitting bar's CT hh:mm, refusal reason) of every intent."""
    return [(r.root, ct_hm(r.decision_ts_ns - 60 * NS),
             None if r.refusal is None else r.refusal.reason) for r in res.events(IntentRecord)]


def _leg_frame(root: str, frame: pd.DataFrame, blackout: Iterable[date] = ()) -> LegFrame:
    days = tuple(sorted({date.fromisoformat(d) for d in frame["trade_date"]}))
    return LegFrame(root, RESEARCH, f"{root}.parquet", "0" * 64, frame, days, (),
                    frozenset(blackout))


def runner_rules(frame_map: dict[str, pd.DataFrame], mes_blackout: Iterable[date] = ()
                 ) -> tuple[StageERules, object]:
    """The rules object exactly as screening.stage_e_runner._run_member builds it: the window
    and the union of every leg's roll blackouts from member_window."""
    legs = {"MGC": _leg_frame("MGC", frame_map["MGC"]),
            "MES": _leg_frame("MES", frame_map["MES"], mes_blackout)}
    mw = member_window(legs, RESEARCH)
    inputs = {leg.root: leg_inputs(leg.root, traded=leg.traded) for leg in LEGS}
    return StageERules(inputs, frozenset(mw.dates), frozenset(mw.blackout_union), NO_RELEASES), mw


# ---------------------------------------------------------------------- fills ----
def test_h30_fills_mgc_at_the_tk_open_and_exits_at_te_plus_30() -> None:
    res = run(flight.make_h30(), frames())
    assert fills(res) == [("MGC", "08:45", "buy", 1, "strategy"),
                          ("MGC", "09:15", "sell", 1, "strategy")]
    assert intents(res) == [("MGC", "08:44", None), ("MGC", "09:14", None)]


def test_heod_fills_mgc_at_the_tk_open_and_exits_at_1505() -> None:
    res = run(flight.make_heod(), frames())
    assert fills(res) == [("MGC", "08:45", "buy", 1, "strategy"),
                          ("MGC", "15:05", "sell", 1, "strategy")]
    assert {f.root for f in res.events(Fill)} == {"MGC"}


def test_an_mgc_bar_missing_at_tk_fills_later_and_h30_counts_from_the_fill() -> None:
    frame_map = frames()
    mgc = frame_map["MGC"]
    t_k = int(datetime.combine(DAY, time(8, 45), tzinfo=CT).timestamp()) * NS
    frame_map["MGC"] = mgc[mgc["ts_event"] != t_k].reset_index(drop=True)
    res = run(flight.make_h30(), frame_map)
    assert fills(res) == [("MGC", "08:46", "buy", 1, "strategy"),
                          ("MGC", "09:16", "sell", 1, "strategy")]


# ------------------------------------------------------- D11.5 and V16(a) by the engine ----
def test_a_missing_mes_bar_at_tk_minus_1_the_engine_refuses_and_the_member_never_asks() -> None:
    frame_map = frames(mes_skip={end_bar(DIP_K)})
    res = run(flight.make_h30(), frame_map)
    assert intents(res) == [] and fills(res) == []
    script = Script({(DAY, 8, 44): [("MGC", "buy", 1)]})
    res = run(script, frame_map)
    assert intents(res) == [("MGC", "08:44", "engine_leg_missing_bar")]
    assert fills(res) == []


def test_a_roll_blackout_of_the_signal_leg_only_blocks_the_entry_v16a() -> None:
    frame_map = frames()
    rules, mw = runner_rules(frame_map, mes_blackout={DAY})
    assert DAY in mw.excluded["roll_blackout_any_leg"] and DAY not in mw.dates
    assert DAY in mw.blackout_union
    res = run(flight.make_h30(), frame_map, rules)
    assert intents(res) == [("MGC", "08:44", "engine_not_a_window_date")]
    assert fills(res) == []


def test_the_engine_names_the_roll_blackout_when_d_is_a_window_date() -> None:
    frame_map = frames()
    inputs = {leg.root: leg_inputs(leg.root, traded=leg.traded) for leg in LEGS}
    rules = StageERules(inputs, frozenset(WINDOW), frozenset({DAY}), NO_RELEASES)
    res = run(flight.make_h30(), frame_map, rules)
    assert intents(res) == [("MGC", "08:44", "engine_roll_blackout")]
    assert fills(res) == []


def test_control_without_a_blackout_the_runner_rules_fill() -> None:
    frame_map = frames()
    rules, mw = runner_rules(frame_map)
    assert DAY in mw.dates and not mw.blackout_union
    res = run(flight.make_h30(), frame_map, rules)
    assert fills(res)[0] == ("MGC", "08:45", "buy", 1, "strategy")


def test_the_member_is_a_fresh_object_per_run() -> None:
    first, second = flight.make_h30(), flight.make_h30()
    assert isinstance(first, FlightToGold) and first is not second
    run(first, frames())
    assert fills(run(second, frames()))[0][1] == "08:45"
