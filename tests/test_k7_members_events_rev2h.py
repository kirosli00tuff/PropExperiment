"""Stage E.6 K7 members of MemberCoder-B, part 2: K7-rev2h-01 (reports/stage_e6_member_specs.md
section 5; K7-L-01, K7-L-06, K7-L-07, K7-L-08). Synthetic bars through the real Stage E engine,
with direct calls where the engine cannot go (a position across an instrument change raises an
engine invariant). The kit is tests/test_k7_members_events.py's.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import pytest

from strategy.members.k7 import rev2h
from tests.test_k7_members_events import (
    Day,
    at,
    bar_at,
    call,
    fills,
    forced_limit_rules,
    hm,
    intents,
    ns_at,
    run,
)

TUE = date(2025, 6, 3)  # a regular full crypto session, F 15:08
S = "strategy"


def day(d: date = TUE, **kw: Any) -> Day:
    return Day(d, hm(8, 0), hm(15, 0), **kw)


# B1: open(08:30) = 0 (its close 20), close(10:29) = 10 (its open -30): r1 = +10 -> target1 = -1
# (sell). A rule reading the 08:30 CLOSE (r1 = -10) or the 10:29 OPEN (r1 = -30) would buy
# (R-T3-1: the end bar's open has the other sign).
B1_UP = {"opens": {hm(8, 30): 0, hm(10, 29): -30},
         "closes": {hm(8, 30): 20, hm(10, 29): 10}}


def b2(r2_sign: int) -> dict:
    """B2 from open(10:30) = 5 (its close -20) to close(12:29) = 5 + 10 x sign (its open
    5 - 30 x sign); a rule reading the 10:30 CLOSE or the 12:29 OPEN sees another sign whenever
    r2 != 0 (R-T3-1)."""
    return {"opens": {hm(10, 30): 5, hm(12, 29): 5 - 30 * r2_sign},
            "closes": {hm(10, 30): -20, hm(12, 29): 5 + 10 * r2_sign}}


def merged(*parts: dict, **extra: Any) -> dict:
    out: dict = {"opens": {}, "closes": {}}
    for p in parts:
        out["opens"] = {**out["opens"], **p.get("opens", {})}
        out["closes"] = {**out["closes"], **p.get("closes", {})}
    return {**out, **extra}


def test_both_decisions_flatten_then_entry_on_the_named_bars() -> None:
    """B1 up -> sell at 10:30 (fill 10:31); B2 down -> target +1: flatten on 12:29 (fill 12:30),
    entry on 12:30 (fill 12:31); final exit on 14:29 (fill 14:30). Exactly 2 entries."""
    res = run(rev2h.make_mbt(), [day(**merged(B1_UP, b2(-1)))])
    assert intents(res) == [(at(TUE, "10:30"), True), (at(TUE, "12:29"), True),
                            (at(TUE, "12:30"), True), (at(TUE, "14:29"), True)]
    assert fills(res) == [(at(TUE, "10:31"), "sell", S), (at(TUE, "12:30"), "buy", S),
                          (at(TUE, "12:31"), "buy", S), (at(TUE, "14:30"), "sell", S)]


def test_b1_down_buys() -> None:
    parts = {"opens": {hm(8, 30): 0}, "closes": {hm(8, 30): -20, hm(10, 29): -10}}
    res = run(rev2h.make_mbt(), [day(**parts)])
    assert fills(res) == [(at(TUE, "10:31"), "buy", S), (at(TUE, "12:30"), "sell", S)]


def test_hold_when_the_target_equals_the_position() -> None:
    """target2 = -1 = the position: no order at 12:29 or 12:30; the position runs to 14:30."""
    res = run(rev2h.make_mbt(), [day(**merged(B1_UP, b2(+1)))])
    assert intents(res) == [(at(TUE, "10:30"), True), (at(TUE, "14:29"), True)]
    assert fills(res) == [(at(TUE, "10:31"), "sell", S), (at(TUE, "14:30"), "buy", S)]


def test_r_zero_is_target_zero() -> None:
    """r1 = 0: no entry at 10:30; a nonzero r2 then enters at 12:30 with no flatten."""
    res = run(rev2h.make_mbt(), [day(**b2(+1))])
    assert intents(res) == [(at(TUE, "12:30"), True), (at(TUE, "14:29"), True)]
    assert fills(res) == [(at(TUE, "12:31"), "sell", S), (at(TUE, "14:30"), "buy", S)]


def test_r2_zero_flattens_on_12_29_and_does_not_enter() -> None:
    res = run(rev2h.make_mbt(), [day(**merged(B1_UP, b2(0)))])
    assert intents(res) == [(at(TUE, "10:30"), True), (at(TUE, "12:29"), True)]
    assert fills(res) == [(at(TUE, "10:31"), "sell", S), (at(TUE, "12:30"), "buy", S)]


@pytest.mark.parametrize("missing", [hm(8, 30), hm(10, 29)])
def test_a_missing_b1_endpoint_is_target_zero(missing: int) -> None:
    res = run(rev2h.make_mbt(), [day(**merged(B1_UP, skip=frozenset({missing})))])
    assert intents(res) == [] and fills(res) == []


def test_a_missing_12_29_bar_flattens_on_the_first_later_bar_and_does_not_enter() -> None:
    """K7-L-08: target2 = 0; the flatten goes on the first later present bar (12:30)."""
    res = run(rev2h.make_mbt(), [day(**merged(B1_UP, b2(-1), skip=frozenset({hm(12, 29)})))])
    assert intents(res) == [(at(TUE, "10:30"), True), (at(TUE, "12:30"), True)]
    assert fills(res) == [(at(TUE, "10:31"), "sell", S), (at(TUE, "12:31"), "buy", S)]


def test_a_missing_10_30_bar_means_no_entry_and_no_b2_signal() -> None:
    """S0.6: no entry at 10:30; 10:30 is also B2's start bar, so target2 = 0."""
    res = run(rev2h.make_mbt(), [day(**merged(B1_UP, b2(-1), skip=frozenset({hm(10, 30)})))])
    assert intents(res) == [] and fills(res) == []


def test_a_missing_12_30_bar_flattens_but_does_not_enter() -> None:
    res = run(rev2h.make_mbt(), [day(**merged(B1_UP, b2(-1), skip=frozenset({hm(12, 30)})))])
    assert intents(res) == [(at(TUE, "10:30"), True), (at(TUE, "12:29"), True)]
    assert fills(res) == [(at(TUE, "10:31"), "sell", S), (at(TUE, "12:31"), "buy", S)]


def test_an_instrument_change_between_the_b1_endpoints_is_target_zero() -> None:
    ids = {m: 778 for m in range(hm(10, 0), hm(15, 0))}  # 10:29, 10:30, 12:29, 12:30 all 778
    res = run(rev2h.make_mbt(), [day(**merged(B1_UP, b2(-1), ids=ids))])
    assert intents(res) == [(at(TUE, "12:30"), True), (at(TUE, "14:29"), True)]
    assert fills(res) == [(at(TUE, "12:31"), "buy", S), (at(TUE, "14:30"), "sell", S)]


def test_an_entry_bar_with_another_instrument_is_no_entry() -> None:
    """S0.9, K7-L-06: the 10:30 entry bar must carry the 08:30 and 10:29 bars' id."""
    ids = {m: 778 for m in range(hm(10, 30), hm(15, 0))}
    res = run(rev2h.make_mbt(), [day(**merged(B1_UP, b2(-1), ids=ids))])
    assert intents(res) == [(at(TUE, "12:30"), True), (at(TUE, "14:29"), True)]
    assert fills(res) == [(at(TUE, "12:31"), "buy", S), (at(TUE, "14:30"), "sell", S)]


def _to_12_29(member: Any, *, b2_id: int = 777, close_1229: int = -5) -> tuple:
    """Direct calls through B1 (sell entry) to the 12:29 bar, with a -1 position afterwards."""
    assert call(member, bar_at(TUE, TUE, hm(8, 30), 20, open_=0)) == ()
    assert call(member, bar_at(TUE, TUE, hm(10, 29), 10)) == ()
    (entry,) = call(member, bar_at(TUE, TUE, hm(10, 30), -20, open_=5))
    assert (entry.side, entry.quantity) == ("sell", 1)
    return call(member, bar_at(TUE, TUE, hm(12, 29), close_1229, instrument_id=b2_id),
                position=-1)


def test_b2_signal_bars_with_two_instruments_flatten_and_do_not_enter() -> None:
    """With a position the engine cannot pass an instrument change, so direct calls: the 10:30
    and 12:29 bars differ -> target2 = 0 -> flatten on 12:29, no entry at 12:30."""
    member = rev2h.make_mbt()
    (flatten,) = _to_12_29(member, b2_id=778)
    assert (flatten.side, flatten.quantity) == ("buy", 1)
    assert call(member, bar_at(TUE, TUE, hm(12, 30), instrument_id=778)) == ()


def test_the_entry_bar_id_gates_only_the_entry_a_hold_is_kept() -> None:
    """K7-L-06 (reading raised with the lead): target2 = -1 = the position is decided at the
    12:29 close; a 12:30 bar with another id sends no order (no entry decision is taken)."""
    member = rev2h.make_mbt()
    assert _to_12_29(member, close_1229=15) == ()  # r2 = +10 -> target -1: hold
    assert call(member, bar_at(TUE, TUE, hm(12, 30), instrument_id=778), position=-1) == ()


def test_no_flatten_and_no_entry_while_an_order_is_pending() -> None:
    member = rev2h.make_mbt()
    assert _to_12_29(member) != ()  # a flatten (target +1 vs -1)
    member = rev2h.make_mbt()
    assert call(member, bar_at(TUE, TUE, hm(8, 30), 20, open_=0)) == ()
    assert call(member, bar_at(TUE, TUE, hm(10, 29), 10)) == ()
    assert call(member, bar_at(TUE, TUE, hm(10, 30)), pending=-1) == ()  # not flat
    member = rev2h.make_mbt()
    assert call(member, bar_at(TUE, TUE, hm(8, 30), 20, open_=0)) == ()
    assert call(member, bar_at(TUE, TUE, hm(10, 29), 10)) == ()
    assert len(call(member, bar_at(TUE, TUE, hm(10, 30), -20, open_=5))) == 1
    assert call(member, bar_at(TUE, TUE, hm(12, 29), -5), position=-1, pending=1) == ()
    assert len(call(member, bar_at(TUE, TUE, hm(12, 30)), position=-1)) == 1  # resent


def test_the_final_exit_is_the_14_29_bar_or_the_first_later_bar() -> None:
    res = run(rev2h.make_mbt(), [day(**merged(B1_UP, b2(+1), skip=frozenset({hm(14, 29)})))])
    assert intents(res) == [(at(TUE, "10:30"), True), (at(TUE, "14:30"), True)]
    assert fills(res) == [(at(TUE, "10:31"), "sell", S), (at(TUE, "14:31"), "buy", S)]


def test_an_engine_closed_position_leaves_the_12_30_decision_as_written() -> None:
    """K7-L-07: the engine closes the B1 short at 11:01; at 12:29 the account is flat, so
    target2 = -1 (equal to target1) is entered at 12:30."""
    member = rev2h.make_mbt()
    days = [day(**merged(B1_UP, b2(+1)))]
    res = run(member, days, rules=forced_limit_rules(member, days, [ns_at(TUE, hm(11, 0))]))
    assert fills(res) == [(at(TUE, "10:31"), "sell", S), (at(TUE, "11:01"), "buy",
                                                           "price_limit_exit"),
                          (at(TUE, "12:31"), "sell", S), (at(TUE, "14:30"), "buy", S)]
    assert intents(res) == [(at(TUE, "10:30"), True), (at(TUE, "12:30"), True),
                            (at(TUE, "14:29"), True)]


@pytest.mark.parametrize("d", [
    date(2025, 9, 17),  # vendor-degraded full session
    date(2025, 7, 4),  # early halt 12:00
    date(2024, 7, 3),  # no halt, but an early engine F (the F test alone)
])
def test_no_trade_off_the_entry_dates(d: date) -> None:
    res = run(rev2h.make_mbt(), [day(d, **merged(B1_UP, b2(-1)))])
    assert intents(res) == [] and fills(res) == []


def test_a_booked_forward_holidays_bars_are_never_read() -> None:
    """K7-L-01: Monday 2026-01-19 (booked forward) carries trade date 2026-01-20; its day-session
    bars are on CT date 2026-01-19, never the bars at hh:mm of 2026-01-20."""
    wed_like = date(2026, 1, 20)
    holiday = Day(wed_like, hm(8, 0), hm(15, 0), anchor=wed_like - timedelta(days=1),
                  **merged(B1_UP, b2(-1)))
    res = run(rev2h.make_mbt(), [holiday, day(wed_like)])
    assert intents(res) == [] and fills(res) == []


def test_bars_of_the_prior_evening_are_not_read_as_day_bars() -> None:
    """The evening bars of trade date d lie on CT date d-1; one at 08:30 would be read only by
    a rule that matched clock times without the CT date."""
    member = rev2h.make_mbt()
    prev = TUE - timedelta(days=1)
    assert call(member, bar_at(TUE, prev, hm(8, 30), 20, open_=0)) == ()
    assert call(member, bar_at(TUE, prev, hm(10, 29), 10)) == ()
    assert call(member, bar_at(TUE, prev, hm(10, 30))) == ()
    assert call(member, bar_at(TUE, TUE, hm(10, 30))) == ()  # 08:30 of CT date d never seen
