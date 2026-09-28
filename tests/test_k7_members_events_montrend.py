"""Stage E.6 K7 members of MemberCoder-B, part 3: K7-montrend-01 (reports/stage_e6_member_specs.md
section 6; K7-L-01, K7-L-06, K7-L-07). Synthetic bars through the real Stage E engine, with direct
calls where the engine cannot go. The kit is tests/test_k7_members_events.py's.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import pytest

from screening.stage_e_engine import Fill
from strategy.members.k7 import montrend
from tests.test_k7_members_events import (
    Day,
    at,
    bar_at,
    call,
    eve,
    fills,
    forced_limit_rules,
    hm,
    intents,
    ns_at,
    run,
)

MON = date(2025, 6, 2)  # a regular Monday (full session), before the weekend regime
MON_247 = date(2026, 6, 8)  # a Monday of the weekend-assignment regime (from 2026-06-01)
S = "strategy"


def sun(d: date, hhmm: str) -> str:
    return at(d, hhmm, prev=True)


def monday(d: date = MON, **kw: Any) -> Day:
    """Sunday (CT date d-1) 17:00 to Monday 14:30, trade date d."""
    return Day(d, eve(17, 0), hm(14, 30), **kw)


# s_18 = sign(close(17:59) - open(17:00)) = sign(10 - 0) = +1; the 17:00 bar's close is -20, the
# 17:01 bar's open 30 and the 17:59 bar's open -30, so a rule reading the 17:00 CLOSE, the 17:01
# bar or the 17:59 OPEN would see -1 (R-T3-1).
FIRST_UP = {"opens": {eve(17, 0): 0, eve(17, 59): -30},
            "closes": {eve(17, 0): -20, eve(17, 1): 30, eve(17, 59): 10}}


def with_closes(base: dict, closes: dict, **extra: Any) -> dict:
    return {"opens": base.get("opens", {}), "closes": {**base.get("closes", {}), **closes},
            **extra}


def test_the_first_decision_is_sunday_18_00_from_the_sunday_17_00_bar() -> None:
    """Buy on Sunday 18:00 (fill 18:01); s_19 = 0 flattens on 18:59 (fill 19:00)."""
    res = run(montrend.make_mbt(), [monday(**FIRST_UP)])
    assert intents(res) == [(sun(MON, "18:00"), True), (sun(MON, "18:59"), True)]
    assert fills(res) == [(sun(MON, "18:01"), "buy", S), (sun(MON, "19:00"), "sell", S)]


def test_hold_on_an_equal_sign() -> None:
    res = run(montrend.make_mbt(), [monday(**with_closes(FIRST_UP, {eve(18, 59): 5}))])
    assert intents(res) == [(sun(MON, "18:00"), True), (sun(MON, "19:59"), True)]
    assert fills(res) == [(sun(MON, "18:01"), "buy", S), (sun(MON, "20:00"), "sell", S)]


def test_a_sign_change_flattens_on_t_minus_1_then_enters_on_t() -> None:
    res = run(montrend.make_mbt(), [monday(**with_closes(FIRST_UP, {eve(18, 59): -5}))])
    assert intents(res) == [(sun(MON, "18:00"), True), (sun(MON, "18:59"), True),
                            (sun(MON, "19:00"), True), (sun(MON, "19:59"), True)]
    assert fills(res) == [(sun(MON, "18:01"), "buy", S), (sun(MON, "19:00"), "sell", S),
                          (sun(MON, "19:01"), "sell", S), (sun(MON, "20:00"), "buy", S)]


def test_monday_morning_decisions_and_the_final_exit_on_13_59() -> None:
    """The Monday decisions (CT date d) run to 13:00; the last position exits on 13:59."""
    res = run(montrend.make_mbt(), [monday(closes={hm(12, 59): 10})])
    assert intents(res) == [(at(MON, "13:00"), True), (at(MON, "13:59"), True)]
    assert fills(res) == [(at(MON, "13:01"), "buy", S), (at(MON, "14:00"), "sell", S)]
    res = run(montrend.make_mbt(), [monday(closes={hm(0, 59): -10})])
    assert fills(res) == [(at(MON, "01:01"), "sell", S), (at(MON, "02:00"), "buy", S)]


def test_a_missing_13_59_bar_exits_on_the_first_later_bar() -> None:
    res = run(montrend.make_mbt(), [monday(closes={hm(12, 59): 10},
                                           skip=frozenset({hm(13, 59)}))])
    assert fills(res) == [(at(MON, "13:01"), "buy", S), (at(MON, "14:01"), "sell", S)]


def test_no_decision_after_13_00() -> None:
    """A signal ending at 13:59 (the would-be 14:00 decision) is never traded."""
    res = run(montrend.make_mbt(), [monday(closes={hm(13, 59): 10})])
    assert intents(res) == [] and fills(res) == []


def test_a_missing_t_minus_60_bar_is_signal_zero() -> None:
    """No 17:00 bar: s_18 = 0, no entry. With a long held through 19:00 (s_19 = +1), a missing
    19:00 bar makes s_20 = 0 and flattens on 19:59 although close(19:59) is up."""
    res = run(montrend.make_mbt(), [monday(**with_closes(FIRST_UP, {},
                                                         skip=frozenset({eve(17, 0)})))])
    assert intents(res) == [] and fills(res) == []
    held = with_closes(FIRST_UP, {eve(18, 59): 5, eve(19, 59): 5})
    res = run(montrend.make_mbt(), [monday(**held)])
    assert fills(res) == [(sun(MON, "18:01"), "buy", S), (sun(MON, "21:00"), "sell", S)]
    res = run(montrend.make_mbt(), [monday(**held, skip=frozenset({eve(19, 0)}))])
    assert intents(res) == [(sun(MON, "18:00"), True), (sun(MON, "19:59"), True)]
    assert fills(res) == [(sun(MON, "18:01"), "buy", S), (sun(MON, "20:00"), "sell", S)]


def test_a_missing_t_minus_1_bar_flattens_on_the_first_later_bar_without_entry() -> None:
    res = run(montrend.make_mbt(), [monday(**with_closes(FIRST_UP, {eve(18, 58): -5},
                                                         skip=frozenset({eve(18, 59)})))])
    assert intents(res) == [(sun(MON, "18:00"), True), (sun(MON, "19:00"), True)]
    assert fills(res) == [(sun(MON, "18:01"), "buy", S), (sun(MON, "19:01"), "sell", S)]


def test_a_missing_t_bar_means_no_entry_but_the_flatten_stands() -> None:
    res = run(montrend.make_mbt(), [monday(**with_closes(FIRST_UP, {eve(18, 59): -5},
                                                         skip=frozenset({eve(19, 0)})))])
    assert intents(res) == [(sun(MON, "18:00"), True), (sun(MON, "18:59"), True)]
    assert fills(res) == [(sun(MON, "18:01"), "buy", S), (sun(MON, "19:01"), "sell", S)]


def test_at_most_20_entries_one_per_decision() -> None:
    """Signs alternating every hour: an entry at each of the 20 decisions, no more."""
    closes = {}
    for k, t in enumerate(montrend.decision_minutes()):
        closes[t - 1] = 5 if k % 2 == 0 else -5
    res = run(montrend.make_mbt(), [monday(closes=closes)])
    entries = [f for f in res.events(Fill) if f.position_after != 0]
    assert len(entries) == 20 == len(montrend.decision_minutes())
    assert entries[0].side == "buy" and entries[-1].side == "sell"
    assert all(r for _, r in intents(res))
    assert fills(res)[-1] == (at(MON, "14:00"), "buy", S)


def test_the_20_decision_times() -> None:
    minutes = montrend.decision_minutes()
    assert minutes == tuple(range(eve(18, 0), hm(13, 0) + 1, 60)) and len(minutes) == 20
    schedule = montrend.day_schedule(MON)
    first = schedule.decisions[0]
    assert (first.start_ns, first.end_ns, first.entry_ns) == (
        ns_at(MON, eve(17, 0)), ns_at(MON, eve(17, 59)), ns_at(MON, eve(18, 0)))
    last = schedule.decisions[-1]
    assert (last.start_ns, last.end_ns, last.entry_ns) == (
        ns_at(MON, hm(12, 0)), ns_at(MON, hm(12, 59)), ns_at(MON, hm(13, 0)))
    assert schedule.final_exit_ns == ns_at(MON, hm(13, 59))


def test_weekend_bars_carrying_mondays_trade_date_are_never_read() -> None:
    """From 2026-06-01 the Friday 16:02 to Sunday 17:00 bars carry Monday's trade date. Here they
    hold a strong signal at every hh:00/hh:59 pair; only the Sunday-from-17:00 bars count."""
    loud = {m: (40 if m % 60 == 59 else -40) for m in range(eve(16, 2) - 2 * 1440, eve(17, 0))}
    weekend = Day(MON_247, eve(16, 2) - 2 * 1440, eve(17, 0), closes=loud)
    res = run(montrend.make_mbt(), [weekend, monday(MON_247, **FIRST_UP)])
    assert intents(res) == [(sun(MON_247, "18:00"), True), (sun(MON_247, "18:59"), True)]
    assert fills(res) == [(sun(MON_247, "18:01"), "buy", S), (sun(MON_247, "19:00"), "sell", S)]


def test_a_booked_forward_monday_is_not_traded() -> None:
    """2026-01-19 (booked forward): its bars, Sunday 17:00 to Monday 16:00 CT, carry Tuesday
    2026-01-20's trade date, which is not a Monday."""
    tue = date(2026, 1, 20)
    holiday = Day(tue, eve(17, 0), hm(14, 30), anchor=tue - timedelta(days=1), **FIRST_UP)
    res = run(montrend.make_mbt(), [holiday])
    assert intents(res) == [] and fills(res) == []


@pytest.mark.parametrize("d", [
    date(2026, 3, 16),  # a vendor-degraded Monday
    date(2021, 9, 6),  # a Monday with an early halt (12:00)
    date(2025, 6, 3),  # a Tuesday (its Monday-evening bars)
])
def test_no_trade_off_the_monday_entry_dates(d: date) -> None:
    res = run(montrend.make_mbt(), [monday(d, **FIRST_UP)])
    assert intents(res) == [] and fills(res) == []


def test_an_engine_closed_position_leaves_later_decisions_as_written() -> None:
    """K7-L-07: the engine closes the 18:01 long at 18:31; s_19 = +1 then enters at 19:00."""
    member = montrend.make_mbt()
    days = [monday(**with_closes(FIRST_UP, {eve(18, 59): 5}))]
    res = run(member, days, rules=forced_limit_rules(member, days, [ns_at(MON, eve(18, 30))]))
    assert fills(res) == [(sun(MON, "18:01"), "buy", S), (sun(MON, "18:31"), "sell",
                                                            "price_limit_exit"),
                          (sun(MON, "19:01"), "buy", S), (sun(MON, "20:00"), "sell", S)]


def test_signal_bars_with_two_instruments_are_signal_zero() -> None:
    ids = {m: 778 for m in range(eve(17, 30), hm(14, 30))}
    res = run(montrend.make_mbt(), [monday(**FIRST_UP, ids=ids)])
    assert intents(res) == [] and fills(res) == []


def test_an_entry_bar_with_another_instrument_is_no_entry() -> None:
    """S0.9: the 18:00 bar carries 778, the signal bars 777: no entry; the next hour's signal
    bars (18:00, 18:59) both carry 778 and enter at 19:00."""
    ids = {m: 778 for m in range(eve(18, 0), hm(14, 30))}
    res = run(montrend.make_mbt(), [monday(**with_closes(FIRST_UP, {eve(18, 59): 5}), ids=ids)])
    assert intents(res) == [(sun(MON, "19:00"), True), (sun(MON, "19:59"), True)]
    assert fills(res) == [(sun(MON, "19:01"), "buy", S), (sun(MON, "20:00"), "sell", S)]


def test_the_entry_bar_id_gates_only_the_entry_a_hold_is_kept() -> None:
    """K7-L-06 (direct calls; the engine refuses a position across an instrument change): at
    18:59 s_19 = +1 equals the long, so it is held; a 19:00 bar with another id sends nothing."""
    member = montrend.make_mbt()
    assert call(member, bar_at(MON, MON, eve(17, 0), -20, open_=0)) == ()
    assert call(member, bar_at(MON, MON, eve(17, 59), 10)) == ()
    assert len(call(member, bar_at(MON, MON, eve(18, 0)))) == 1
    assert call(member, bar_at(MON, MON, eve(18, 59), 5), position=1) == ()
    assert call(member, bar_at(MON, MON, eve(19, 0), instrument_id=778), position=1) == ()


def test_a_flatten_is_not_sent_while_an_order_is_pending_and_is_resent() -> None:
    member = montrend.make_mbt()
    assert call(member, bar_at(MON, MON, eve(17, 0), -20, open_=0)) == ()
    assert call(member, bar_at(MON, MON, eve(17, 59), 10)) == ()
    assert call(member, bar_at(MON, MON, eve(18, 0)), pending=1) == ()  # not flat: no entry
    assert call(member, bar_at(MON, MON, eve(18, 59), -5), position=1, pending=-1) == ()
    (flatten,) = call(member, bar_at(MON, MON, eve(19, 0)), position=1)
    assert (flatten.side, flatten.quantity) == ("sell", 1)
