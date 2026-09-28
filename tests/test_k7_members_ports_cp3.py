"""Stage E.6 K7 ports of MemberCoder-A, part 3: K7-cp3-01 (reports/stage_e6_member_specs.md
section 3; readings E.3-L-09, E.3-L-10, E.3-L-11, K7-L-01).

Synthetic bars only, built with tests/test_k7_members_ports.py's kit and run through the real
Stage E engine, plus direct calls of ``clv_side``. No bar file is read.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from data.group_session import load_group_calendar
from screening.stage_e_engine import Fill
from strategy.members.k7 import cp3
from tests.test_k7_members_ports import (
    FRI,
    FRI_247,
    FRI_BF,
    HALT_DAY,
    HOLIDAY_BF,
    MON,
    MON_247,
    MON_HALT,
    THU_HALT,
    TUE,
    TUE_247,
    TUE_BF,
    WED,
    WED_BF,
    Day,
    Ticks,
    account_of,
    bar_at,
    fill_dates,
    fills,
    forced_limit_rules,
    halt_label,
    hm,
    holiday_session,
    intents,
    release_at,
    run,
    trade,
    view_of,
    weekend,
)

THU_BF = date(2026, 1, 15)
WIDE = (0, 30, -30, 0)  # would move a daily bar's range to B-30..B+30 if it were read


def daily(high: int, low: int, close: int, **kw: Ticks) -> dict[int, Ticks]:
    """Paths making d's daily bar H = B+high, L = B+low, C (14:59 close) = B+close, plus two
    extreme bars just OUTSIDE [08:30, 15:00), at 08:29 and 15:00, that must not enter it."""
    return {hm(8, 29): (0, 50, -50, 0), hm(15, 0): (0, 50, -50, 0),
            hm(10, 0): (0, high, 0, 0), hm(11, 0): (0, 0, low, 0),
            hm(14, 59): (0, max(0, close), min(0, close), close), **kw}


BUY_08 = daily(10, 0, 8)  # CLV = 8/10 = 0.8 exactly
SELL_02 = daily(10, 0, 2)  # CLV = 2/10 = 0.2 exactly


def test_cp3_literals_are_the_clv_cuts_and_the_clock() -> None:
    cuts = (cp3.CLV_BUY_AT_OR_ABOVE, cp3.CLV_SELL_AT_OR_BELOW)
    assert (Decimal("0.8"), Decimal("0.2")) == cuts
    assert (cp3.CLOSE_BEFORE_C_MIN, cp3.EXIT_BEFORE_C_MIN) == (1, 2)


def test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_1459() -> None:
    res = run(cp3.make_mbt(), [Day(MON, BUY_08), Day(TUE)])
    assert fills(res) == trade(TUE, "08:31", "14:59", "buy")  # MON: warm-up, no trade
    assert intents(res) == [(TUE, "08:30", True, None), (TUE, "14:58", True, None)]
    assert [f.qty for f in res.events(Fill)] == [1, 1]


def test_cp3_prior_clv_at_02_sells() -> None:
    res = run(cp3.make_mbt(), [Day(MON, SELL_02), Day(TUE)])
    assert fills(res) == trade(TUE, "08:31", "14:59", "sell")


@pytest.mark.parametrize("close", [3, 5, 7])
def test_cp3_clv_strictly_between_the_cuts_is_no_trade(close: int) -> None:
    assert intents(run(cp3.make_mbt(), [Day(MON, daily(10, 0, close)), Day(TUE)])) == []


@pytest.mark.parametrize(("close", "side"), [(10, "buy"), (9, "buy"), (1, "sell"), (0, "sell")])
def test_cp3_clv_beyond_the_cuts_trades(close: int, side: str) -> None:
    res = run(cp3.make_mbt(), [Day(MON, daily(10, 0, close)), Day(TUE)])
    assert fills(res) == trade(TUE, "08:31", "14:59", side)


@pytest.mark.parametrize(("span", "num", "side"), [
    (10, 8, "buy"), (5, 4, "buy"), (15, 12, "buy"), (15, 11, None), (10, 7, None),
    (10, 2, "sell"), (5, 1, "sell"), (15, 3, "sell"), (15, 4, None), (10, 3, None),
    (1, 1, "buy"), (1, 0, "sell"), (0, 0, None), (-1, 0, None)])
def test_cp3_clv_cuts_are_compared_exactly(span: int, num: int, side: str | None) -> None:
    prior = cp3.DailyBar(MON, high=100 + span, low=100, close=100 + num, instrument_id=777)
    assert cp3.clv_side(prior) == side


@pytest.mark.parametrize(("close", "side"), [(6, "buy"), (-6, "sell")])
def test_cp3_the_daily_low_is_the_min_low(close: int, side: str) -> None:
    # H = B+10, L = B-10 (the 11:00 bar): CLV = 16/20 = 0.8 buys, 4/20 = 0.2 sells
    res = run(cp3.make_mbt(), [Day(MON, daily(10, -10, close)), Day(TUE)])
    assert fills(res) == trade(TUE, "08:31", "14:59", side)


def test_cp3_day_accumulators_reset_each_trade_date() -> None:
    # MON's B-30..B+30 range (CLV 0.5) must not carry into TUE's daily bar (CLV 0.8)
    res = run(cp3.make_mbt(), [Day(MON, daily(30, -30, 0)), Day(TUE, BUY_08), Day(WED)])
    assert fills(res) == trade(WED, "08:31", "14:59", "buy")


def test_cp3_the_halt_flag_resets_each_trade_date() -> None:
    # 07-04's halt must not make 07-07 incomplete: 07-07 trades on 07-03 (sell), 07-08 on 07-07
    tue = date(2025, 7, 8)
    assert load_group_calendar("crypto").early_halt_ct(tue) is None
    days = [Day(THU_HALT, SELL_02), Day(HALT_DAY, halt=halt_label(HALT_DAY)),
            Day(MON_HALT, BUY_08), Day(tue)]
    res = run(cp3.make_mbt(), days)
    assert fills(res) == trade(MON_HALT, "08:31", "14:59", "sell") + trade(
        tue, "08:31", "14:59", "buy")


def test_cp3_zero_range_is_no_trade() -> None:
    flat = {hm(8, 29): (0, 50, -50, 0)}  # the only non-flat bar is outside [08:30, 15:00)
    assert intents(run(cp3.make_mbt(), [Day(MON, flat), Day(TUE)])) == []


def test_cp3_warm_up_no_complete_earlier_bar_is_no_trade() -> None:
    assert intents(run(cp3.make_mbt(), [Day(MON, BUY_08)])) == []
    mon = Day(MON, BUY_08, skip=frozenset({hm(14, 59)}))  # incomplete: no d-1 for TUE
    assert intents(run(cp3.make_mbt(), [mon, Day(TUE)])) == []


def test_cp3_uses_d_minus_1_only_after_it_is_finalised() -> None:
    # MON's bar (buy) decides TUE; TUE's own bar (sell) decides WED, never TUE itself
    res = run(cp3.make_mbt(), [Day(MON, BUY_08), Day(TUE, SELL_02), Day(WED)])
    assert fills(res) == trade(TUE, "08:31", "14:59", "buy") + trade(WED, "08:31", "14:59",
                                                                     "sell")


def test_cp3_d_minus_1_is_the_most_recent_complete_day() -> None:
    # TUE lacks its 14:59 bar: incomplete, dropped; WED's d-1 is MON (buy), not "no trade"
    tue = Day(TUE, SELL_02, skip=frozenset({hm(14, 59)}))
    res = run(cp3.make_mbt(), [Day(MON, BUY_08), tue, Day(WED)])
    # TUE's exit, decided on 14:58, fills at the next present bar (15:00)
    assert fills(res) == trade(TUE, "08:31", "15:00", "buy") + trade(WED, "08:31", "14:59",
                                                                     "buy")


def test_cp3_a_day_with_two_instrument_ids_is_incomplete() -> None:
    mon = Day(MON, BUY_08, ids={hm(9, 0): 778})  # one bar in [08:30, 15:00) differs
    res = run(cp3.make_mbt(), [mon, Day(TUE, SELL_02), Day(WED)])
    assert fills(res) == trade(WED, "08:31", "14:59", "sell")  # TUE: no complete d-1 yet


def test_cp3_other_ids_outside_the_daily_window_do_not_make_it_incomplete() -> None:
    mon = Day(MON, BUY_08, ids={hm(8, 29): 778, hm(15, 0): 778})
    res = run(cp3.make_mbt(), [mon, Day(TUE)])
    assert fills(res) == trade(TUE, "08:31", "14:59", "buy")


def test_cp3_instrument_guard_compares_d_minus_1_with_the_0830_bar() -> None:
    tue = Day(TUE, BUY_08, instrument_id=778)
    res = run(cp3.make_mbt(), [Day(MON, BUY_08), tue, Day(WED, instrument_id=778)])
    assert fills(res) == trade(WED, "08:31", "14:59", "buy")  # TUE refused by the guard
    # only the 08:30 bar is compared: the evening's and the 08:29 bar's ids do not matter (a
    # later bar cannot differ while a position is held: the engine refuses a contract splice)
    tue_late = Day(TUE, ids={hm(8, 29): 778}, evening_id=778)
    res_late = run(cp3.make_mbt(), [Day(MON, BUY_08), tue_late])
    assert fills(res_late) == trade(TUE, "08:31", "14:59", "buy")


def test_cp3_missing_0830_bar_is_no_trade_and_the_day_is_incomplete() -> None:
    tue = Day(TUE, SELL_02, skip=frozenset({hm(8, 30)}))
    res = run(cp3.make_mbt(), [Day(MON, BUY_08), tue, Day(WED)])
    assert fills(res) == trade(WED, "08:31", "14:59", "buy")  # WED's d-1 is MON


def test_cp3_early_halt_day_is_not_traded_and_is_incomplete() -> None:
    # 2025-07-04 (early halt 12:00, F 11:30): bars kept to 15:12 so it would be complete but for
    # its halt; the engine would accept an 08:30 entry, so the member's own test is what blocks it
    label = halt_label(HALT_DAY)
    days = [Day(THU_HALT, BUY_08), Day(HALT_DAY, SELL_02, halt=label), Day(MON_HALT)]
    res = run(cp3.make_mbt(), days)
    assert [i for i in intents(res) if i[0] == HALT_DAY] == []
    assert fills(res) == trade(MON_HALT, "08:31", "14:59", "buy")  # d-1 of 07-07 is 07-03


def test_cp3_a_halt_day_with_a_buy_prior_is_still_not_traded() -> None:
    # the halt excludes day d itself (E.3-L-09, E.3-L-11): 07-03's buy is not traded on 07-04
    label = halt_label(HALT_DAY)
    res = run(cp3.make_mbt(), [Day(THU_HALT, BUY_08), Day(HALT_DAY, halt=label)])
    assert intents(res) == [] and fills(res) == []


def test_cp3_missing_1458_bar_sends_the_exit_on_1459() -> None:
    res = run(cp3.make_mbt(), [Day(MON, BUY_08), Day(TUE, skip=frozenset({hm(14, 58)}))])
    assert fills(res) == trade(TUE, "08:31", "15:00")


def test_cp3_fill_in_the_d95a_guard_waits_two_minutes() -> None:
    res = run(cp3.make_mbt(), [Day(MON, BUY_08), Day(TUE)], releases=release_at(TUE, 8, 31))
    assert fills(res) == trade(TUE, "08:33", "14:59")


def test_cp3_position_open_at_a_synthetic_f_is_flattened_by_the_engine() -> None:
    res = run(cp3.make_mbt(), [Day(MON, BUY_08), Day(TUE, flatten_from=hm(14, 0))])
    assert fills(res) == trade(TUE, "08:31", "14:01", exit_reason="forced_flatten")
    assert [i[1] for i in intents(res)] == ["08:30"]


def test_cp3_d97_engine_exit_no_duplicate_exit_and_no_reentry() -> None:
    days = [Day(MON, BUY_08), Day(TUE)]
    member = cp3.make_mbt()
    res = run(member, days, rules=forced_limit_rules(member, days, [(TUE, hm(9, 30))]))
    assert fills(res) == trade(TUE, "08:31", "09:31", exit_reason="price_limit_exit")
    assert [i[:2] for i in intents(res)] == [(TUE, "08:30")]


def test_cp3_monday_before_2026_05_29_uses_fridays_bar() -> None:
    res = run(cp3.make_mbt(), [Day(FRI, BUY_08), Day(MON)])
    assert fills(res) == trade(MON, "08:31", "14:59", "buy")


def test_cp3_monday_from_2026_06_01_reads_no_weekend_bar() -> None:
    # Saturday's and Sunday's [08:30, 15:00) bars carry Monday's trade date: their 08:30 bar
    # would be an entry bar (refused on a weekend, using up the day), and their WIDE 08:40 bars
    # would widen Monday's daily bar to B-30..B+30 (Monday's CLV 0.2 would become 32/60)
    wrong = {hm(8, 40): WIDE, hm(14, 40): WIDE}
    mon = Day(MON_247, SELL_02, others=weekend(None, wrong, wrong))
    res = run(cp3.make_mbt(), [Day(FRI_247, BUY_08), mon, Day(TUE_247)])
    assert fills(res) == trade(MON_247, "08:31", "14:59", "buy") + trade(
        TUE_247, "08:31", "14:59", "sell")
    assert [i[:2] for i in intents(res)] == [(MON_247, "08:30"), (MON_247, "14:58"),
                                             (TUE_247, "08:30"), (TUE_247, "14:58")]


def test_cp3_after_a_booked_forward_monday_d_minus_1_is_the_friday() -> None:
    # trade date 2026-01-20 also holds the holiday 01-19's session. Its 08:30 bar would be an
    # entry bar the engine accepts (F 11:45 CT that day), and its WIDE bars would widen
    # Tuesday's daily bar (Tuesday's CLV 0.2 would become 32/60, so WED would not trade)
    wrong = {hm(8, 40): WIDE, hm(11, 0): WIDE}
    tue = Day(TUE_BF, SELL_02, others=holiday_session(None, wrong))
    res = run(cp3.make_mbt(), [Day(FRI_BF, BUY_08), tue, Day(WED_BF)])
    assert fills(res) == trade(TUE_BF, "08:31", "14:59", "buy") + trade(
        WED_BF, "08:31", "14:59", "sell")
    assert fill_dates(res) == [TUE_BF, TUE_BF, WED_BF, WED_BF]
    assert HOLIDAY_BF not in [i[0] for i in intents(res)]


def test_cp3_a_booked_forward_holiday_session_is_never_a_daily_bar() -> None:
    # Friday 01-16 is incomplete (no 14:59 bar); the holiday's session holds a complete-looking
    # sell day (08:30 and 14:59 bars, one id). Tuesday's d-1 is Thursday 01-15 (buy)
    assert load_group_calendar("crypto").is_trade_date(THU_BF)
    fri = Day(FRI_BF, SELL_02, skip=frozenset({hm(14, 59)}))
    tue = Day(TUE_BF, others=holiday_session(None, SELL_02))
    res = run(cp3.make_mbt(), [Day(THU_BF, BUY_08), fri, tue])
    assert fills(res)[-2:] == trade(TUE_BF, "08:31", "14:59", "buy")
    assert fill_dates(res)[-2:] == [TUE_BF, TUE_BF]


def test_cp3_emits_at_most_one_entry_per_trade_date_and_none_while_pending() -> None:
    def primed() -> cp3.Cp3CloseLocation:
        member = cp3.make_mbt()  # MON's complete daily bar, CLV 0.8, by direct calls
        for minute, path in sorted({hm(8, 30): (0, 0, 0, 0), **BUY_08}.items()):
            bar = bar_at(MON, minute, path)
            assert member.on_minute(view_of(bar.ts_event_ns, bar), account_of()) == ()
        return member

    entry = bar_at(TUE, hm(8, 30))
    view = view_of(entry.ts_event_ns, entry)
    member = primed()
    (intent,) = member.on_minute(view, account_of())
    assert (intent.side, intent.quantity) == ("buy", 1)
    assert member.on_minute(view, account_of()) == ()  # S0.6: once per trade date
    assert primed().on_minute(view, account_of(0, 1)) == ()  # S0.6: never while pending
