"""Stage E.4 Part 3, K3 members of MemberCoder-A, part 3: K3-cp3-01, the prior-close location
(reports/stage_e4c_member_specs.md sections 1-3; catalog reports/stage_e0_catalog_K3.md lines
340-379). Synthetic bars through the real engine, with the kit of tests/test_e4_k3_members_a.py.

The FX row's clock (O 07:20, C 14:00) is the same on all seven roots: daily bar [07:20, 14:00)
with the 13:59 close; entry on the 07:20 bar (fills at 07:21); exit on the first bar at or after
13:58 (fills at 13:59). Expected times are literals.
"""

from __future__ import annotations

from datetime import date

import pytest

from data.group_session import load_group_calendar, trade_dates_between
from strategy.members.k3 import cp3
from strategy.members.k3._port_common import EXPOSURES
from tests.test_e4_k3_members_a import (
    CLOCK_DAYS,
    FX_HALTS,
    MON,
    TUE,
    WED,
    Day,
    Fill,
    Ticks,
    fills,
    forced_limit_rules,
    halt_label,
    hm,
    intents,
    make,
    release_at,
    run,
    trade,
)

O_BAR, C_1_BAR, EXIT_BAR = hm(7, 20), hm(13, 59), hm(13, 58)


def daily(high: int, low: int, close: int) -> dict[int, Ticks]:
    """Paths making d's daily bar H = B+high, L = B+low, C (the 13:59 close) = B+close, plus two
    extreme bars OUTSIDE [07:20, 14:00) (07:10 and 14:15) that must not enter it."""
    return {hm(7, 10): (0, 50, -50, 0), hm(14, 15): (0, 50, -50, 0),
            hm(9, 0): (0, high, 0, 0), hm(10, 0): (0, 0, low, 0),
            C_1_BAR: (0, max(0, close), min(0, close), close)}


BUY_08 = daily(10, 0, 8)  # CLV = 8/10 = 0.8 exactly
SELL_02 = daily(10, 0, 2)  # CLV = 2/10 = 0.2 exactly


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp3_prior_clv_at_08_buys_on_the_0720_bar_and_exits_at_1358(root: str) -> None:
    res = run(make(cp3, root), [Day(MON, BUY_08), Day(TUE)])
    assert fills(res) == trade(TUE, "07:21", "13:59", "buy")  # MON: warm-up, no trade
    assert intents(res) == [(TUE, "07:20", True, None), (TUE, "13:58", True, None)]
    assert [f.qty for f in res.events(Fill)] == [1, 1]  # q_c = 1


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp3_prior_clv_at_02_sells(root: str) -> None:
    res = run(make(cp3, root), [Day(MON, SELL_02), Day(TUE)])
    assert fills(res) == trade(TUE, "07:21", "13:59", "sell")


@pytest.mark.parametrize("day", CLOCK_DAYS, ids=str)
def test_cp3_keeps_the_ct_clock_in_both_regimes(day: date) -> None:
    prior = Day(date.fromordinal(day.toordinal() - 7), BUY_08)  # a week earlier: d-1 complete
    for root in EXPOSURES:
        res = run(make(cp3, root), [prior, Day(day)])
        assert fills(res) == trade(day, "07:21", "13:59", "buy"), root


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp3_the_daily_bar_is_0720_to_1400_with_the_1359_close(root: str) -> None:
    # the extremes at 07:10 and 14:15 are outside the daily bar (else CLV would be 58/100 = 0.58
    # and no trade); a close at 14:00 (not 13:59) far below does not change C_d
    paths = {**BUY_08, hm(14, 0): (0, 0, -30, -30)}
    assert fills(run(make(cp3, root), [Day(MON, paths), Day(TUE)])) == trade(TUE, "07:21",
                                                                              "13:59")
    # the 07:20 and 13:59 bars are inside it: an extreme on either moves CLV off the cut
    low_at_o = {**BUY_08, O_BAR: (0, 0, -10, 0)}  # L = B-10: CLV = 18/20 = 0.9, still buys
    assert fills(run(make(cp3, root), [Day(MON, low_at_o), Day(TUE)]))[0][2] == "buy"
    high_at_o = {**BUY_08, O_BAR: (0, 30, 0, 0)}  # H = B+30: CLV = 8/30, no trade
    assert intents(run(make(cp3, root), [Day(MON, high_at_o), Day(TUE)])) == []


@pytest.mark.parametrize("close", [3, 5, 7])
def test_cp3_clv_strictly_between_the_cuts_is_no_trade(close: int) -> None:
    for root in EXPOSURES:
        res = run(make(cp3, root), [Day(MON, daily(10, 0, close)), Day(TUE)])
        assert intents(res) == []


@pytest.mark.parametrize(("span", "num", "side"), [
    (10, 8, "buy"), (5, 4, "buy"), (15, 12, "buy"), (15, 11, None), (10, 7, None),
    (10, 2, "sell"), (5, 1, "sell"), (15, 3, "sell"), (15, 4, None), (10, 3, None),
    (1, 1, "buy"), (1, 0, "sell"), (0, 0, None)])
def test_cp3_clv_cuts_are_compared_exactly(span: int, num: int, side: str | None) -> None:
    prior = cp3.DailyBar(MON, high=100 + span, low=100, close=100 + num, instrument_id=777)
    assert cp3.clv_side(prior) == side


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp3_zero_range_is_no_trade(root: str) -> None:
    flat = {hm(7, 10): (0, 50, -50, 0)}  # the only non-flat bar is outside [07:20, 14:00)
    assert intents(run(make(cp3, root), [Day(MON, flat), Day(TUE)])) == []


def test_cp3_uses_d_minus_1_only_after_it_is_finalised() -> None:
    # MON's bar (buy) decides TUE; TUE's own bar (sell) decides WED, never TUE itself
    res = run(cp3.make_6e(), [Day(MON, BUY_08), Day(TUE, SELL_02), Day(WED)])
    assert fills(res) == trade(TUE, "07:21", "13:59", "buy") + trade(WED, "07:21", "13:59",
                                                                     "sell")


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp3_d_minus_1_is_the_most_recent_complete_day(root: str) -> None:
    # TUE lacks its 13:59 bar: incomplete, dropped; WED's d-1 is MON (buy), not "no trade".
    # TUE's exit, decided on 13:58, fills at the next present bar (14:00)
    tue = Day(TUE, SELL_02, skip=frozenset({C_1_BAR}))
    res = run(make(cp3, root), [Day(MON, BUY_08), tue, Day(WED)])
    assert fills(res) == trade(TUE, "07:21", "14:00", "buy") + trade(WED, "07:21", "13:59", "buy")


def test_cp3_a_day_with_two_instrument_ids_is_incomplete() -> None:
    mon = Day(MON, BUY_08, ids={hm(9, 0): 778})  # one bar in [07:20, 14:00) differs
    res = run(cp3.make_6b(), [mon, Day(TUE, SELL_02), Day(WED)])
    assert fills(res) == trade(WED, "07:21", "13:59", "sell")  # TUE: no complete d-1 yet


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp3_instrument_guard_compares_d_minus_1_with_the_0720_bar(root: str) -> None:
    tue = Day(TUE, BUY_08, instrument_id=778)  # a roll: TUE's bars carry the next contract
    res = run(make(cp3, root), [Day(MON, BUY_08), tue, Day(WED, instrument_id=778)])
    assert fills(res) == trade(WED, "07:21", "13:59", "buy")  # TUE refused by the guard


def test_cp3_the_guard_reads_the_0720_bar_only() -> None:
    # TUE's 07:20 bar carries MON's id; a bar before 07:20 (outside the daily bar, read by no
    # rule) carries another: the entry on TUE's 07:20 bar stands
    tue = Day(TUE, ids={hm(7, 15): 778})
    res = run(cp3.make_6j(), [Day(MON, BUY_08), tue])
    assert fills(res) == trade(TUE, "07:21", "13:59", "buy")


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp3_missing_0720_bar_is_no_trade_and_the_day_is_incomplete(root: str) -> None:
    tue = Day(TUE, SELL_02, skip=frozenset({O_BAR}))
    res = run(make(cp3, root), [Day(MON, BUY_08), tue, Day(WED)])
    assert fills(res) == trade(WED, "07:21", "13:59", "buy")  # WED's d-1 is MON


@pytest.mark.parametrize("halt_day", list(FX_HALTS), ids=str)
def test_cp3_early_halt_day_is_not_traded_and_is_incomplete(halt_day: date) -> None:
    # every research-window FX halt of EC-CAL: bars kept to 15:12 so the day would be complete
    # but for its halt; the engine would accept a 07:20 entry (F is 08:00 or later), so the
    # member's own test of trade date d (E.3-L-11; K3-L-04: the 07:20 bar's CT date is d) is what
    # blocks it. The next trade date's d-1 is the date before the halt, not the halt day.
    # (No "after" date's evening falls on the halt day's CT date: 12-26's is on 12-25.)
    before, after, _ = FX_HALTS[halt_day]
    label = halt_label(halt_day)
    for root in EXPOSURES:
        days = [Day(before, BUY_08), Day(halt_day, SELL_02, halt=label), Day(after)]
        res = run(make(cp3, root), days)
        assert [i for i in intents(res) if i[0] == halt_day] == [], root
        assert fills(res) == trade(after, "07:21", "13:59", "buy"), root


def test_cp3_a_halt_label_on_the_evening_bars_only_does_not_block_day_d() -> None:
    # the evening bars of d sit on CT date d-1 and carry d-1's label; day d's own bars do not
    res = run(cp3.make_6e(), [Day(MON, BUY_08), Day(TUE, evening_halt="12:00")])
    assert fills(res) == trade(TUE, "07:21", "13:59", "buy")


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp3_missing_exit_bar_sends_the_exit_on_the_next_present_bar(root: str) -> None:
    res = run(make(cp3, root), [Day(MON, BUY_08), Day(TUE, skip=frozenset({EXIT_BAR}))])
    assert fills(res) == trade(TUE, "07:21", "14:00")
    assert intents(res)[-1] == (TUE, "13:59", True, None)


def test_cp3_missing_entry_bar_is_no_trade_on_a_later_bar() -> None:
    res = run(cp3.make_6a(), [Day(MON, BUY_08), Day(TUE, skip=frozenset({O_BAR}))])
    assert intents(res) == []


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp3_fill_in_the_d95a_guard_waits_two_minutes(root: str) -> None:
    res = run(make(cp3, root), [Day(MON, BUY_08), Day(TUE)], releases=release_at(root, TUE, 7, 21))
    assert fills(res) == trade(TUE, "07:23", "13:59")
    beside = run(make(cp3, root), [Day(MON, BUY_08), Day(TUE)],
                 releases=release_at(root, TUE, 7, 19))  # guard [07:19, 07:21)
    assert fills(beside) == trade(TUE, "07:21", "13:59")


def test_cp3_releases_while_holding_meet_no_fill_and_one_at_the_exit_holds_it() -> None:
    # catalog C lines 369-371: it holds through the 07:30 BLS release and the 13:00 FOMC
    for hh, mm in ((7, 30), (13, 0)):
        res = run(cp3.make_6c(), [Day(MON, BUY_08), Day(TUE)],
                  releases=release_at("6C", TUE, hh, mm))
        assert fills(res) == trade(TUE, "07:21", "13:59")
    at_exit = run(cp3.make_6c(), [Day(MON, BUY_08), Day(TUE)],
                  releases=release_at("6C", TUE, 13, 59))
    assert fills(at_exit) == trade(TUE, "07:21", "14:01")
    assert [i[1] for i in intents(at_exit)] == ["07:20", "13:58"]


def test_cp3_position_open_at_a_synthetic_f_is_flattened_by_the_engine() -> None:
    res = run(cp3.make_6s(), [Day(MON, BUY_08), Day(TUE, flatten_from=hm(13, 0))])
    assert fills(res) == trade(TUE, "07:21", "13:01", exit_reason="forced_flatten")
    assert [i[1] for i in intents(res)] == ["07:20"]


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp3_d97_engine_exit_no_duplicate_exit_and_no_reentry(root: str) -> None:
    days = [Day(MON, BUY_08), Day(TUE)]
    member = make(cp3, root)
    res = run(member, days, rules=forced_limit_rules(member, days, [(TUE, hm(9, 30))]))
    assert fills(res) == trade(TUE, "07:21", "09:31", exit_reason="price_limit_exit")
    assert [i[:2] for i in intents(res)] == [(TUE, "07:20")]


def test_cp3_one_entry_per_trade_date_even_when_the_engine_refuses_it() -> None:
    # TUE is not a window date: the 07:20 entry is refused and nothing is resent that day
    res = run(cp3.make_6n(), [Day(MON, BUY_08), Day(TUE)], window=[MON])
    assert intents(res) == [(TUE, "07:20", False, "engine_not_a_window_date")]


@pytest.mark.parametrize("holiday", [date(2025, 9, 1), date(2025, 11, 27), date(2026, 1, 19),
                                     date(2026, 2, 16), date(2026, 5, 25)], ids=str)
def test_cp3_a_us_holiday_ec_cal_fx_does_not_mark_is_traded_and_flattened_at_f(
        holiday: date) -> None:
    """OBSERVATION pinned for the lead (report section 'Observations'): EC-CAL FX lists these
    US holidays as trade dates with no early halt (metals and rates mark them), so their bars
    carry no early_halt_ct and E.3-L-11 does not exclude them; rules.sessions puts Topstep's F
    at 11:30 or 11:45, so the engine flattens the 07:21 entry there."""
    cal = load_group_calendar("fx")
    assert holiday in trade_dates_between(cal, holiday, holiday)
    assert cal.early_halt_ct(holiday) is None
    prior = date.fromordinal(holiday.toordinal() - 7)
    res = run(cp3.make_6e(), [Day(prior, BUY_08), Day(holiday)])
    f = "11:30" if holiday in (date(2025, 9, 1), date(2025, 11, 27)) else "11:45"
    assert fills(res) == trade(holiday, "07:21", f, exit_reason="forced_flatten")
