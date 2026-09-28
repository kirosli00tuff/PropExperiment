"""Stage E.7 K1 ports of MemberCoder-A, part 2: K1-cp2-01 on MNQ, M2K and MYM
(reports/stage_e7_member_specs.md section 2; readings E.3-L-07, E.3-L-08, K4-L-06, K7-L-01).

Synthetic bars only, built with tests/test_k1_members_ports.py's kit and run through the real
Stage E engine, plus direct calls where the equity calendar never produces the case. No bar file
is read.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, time, timedelta
from decimal import Decimal
from typing import Any

import pandas as pd
import pytest

from rules.products import product
from strategy.members.k1 import cp2
from tests.test_k1_members_ports import (
    FRI_MD,
    HOLIDAY_MD,
    MON,
    Q_C,
    ROOTS,
    TICK,
    TUE,
    TUE_MD,
    WED,
    Day,
    Ticks,
    account_of,
    bar_at,
    feed,
    fill_qty,
    fills,
    forced_limit_rules,
    frame,
    halt_label,
    hm,
    intents,
    make,
    ns_at,
    release_at,
    run,
    trade,
    view_of,
)

# OR bars [08:30, 08:45): the 08:35 high is B+2, the 08:40 low is B-2 (the others at B)
CP2_OR = {hm(8, 35): (0, 2, 0, 0), hm(8, 40): (0, 0, -2, 0)}
UP4 = (0, 6, 0, 6)  # close = OR_high + 4 ticks (the buffer: MNQ 1.00, M2K 0.40, MYM 4)
DOWN4 = (0, 0, -6, -6)  # close = OR_low - 4 ticks
UP3, DOWN3 = (0, 5, 0, 5), (0, 0, -5, -5)  # 3 ticks beyond: no entry
WIDE = (0, 30, -30, 0)  # a bar that would widen the range to B-30..B+30 if it were read


def cp2_day(extra: Mapping[int, Ticks], day: date = TUE, **kw: Any) -> Day:
    return Day(day, paths={**CP2_OR, **extra}, **kw)


def m(root: str = "MNQ") -> cp2.Cp2Breakout:
    return make(cp2, root)


@pytest.mark.parametrize("root", ROOTS)
def test_cp2_literals_are_or_15_buffer_4_ticks_hold_75_k4_l06(root: str) -> None:
    assert (cp2.RANGE_MINUTES, cp2.BUFFER_TICKS, cp2.HOLD_BARS) == (15, 4, 75)
    assert time(15, 8) == cp2.F_REGULAR_CT
    buffer = cp2.BUFFER_TICKS * product(root).vendor_tick
    assert buffer == {"MNQ": Decimal("1.00"), "M2K": Decimal("0.40"), "MYM": Decimal("4")}[root]
    assert product(root).vendor_tick == TICK[root]


@pytest.mark.parametrize("root", ROOTS)
def test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars(root: str) -> None:
    res = run(m(root), [cp2_day({hm(8, 45): UP4})])
    assert fills(res) == trade(TUE, "08:46", "10:01", "buy")  # 75 minutes fill to fill
    assert intents(res) == [(TUE, "08:45", True, None), (TUE, "10:00", True, None)]
    assert fill_qty(res) == [Q_C[root], Q_C[root]]  # q_c (S0.3); the exit closes it all


@pytest.mark.parametrize("root", ROOTS)
def test_cp2_breakout_down_sells(root: str) -> None:
    res = run(m(root), [cp2_day({hm(8, 45): DOWN4})])
    assert fills(res) == trade(TUE, "08:46", "10:01", "sell")
    assert fill_qty(res) == [Q_C[root], Q_C[root]]


@pytest.mark.parametrize("root", ROOTS)
def test_cp2_the_buffer_is_exactly_four_ticks_either_side(root: str) -> None:
    res_up = run(m(root), [cp2_day({hm(8, 50): UP3, hm(9, 0): UP4})])
    res_down = run(m(root), [cp2_day({hm(8, 50): DOWN3, hm(9, 0): DOWN4})])
    assert fills(res_up) == trade(TUE, "09:01", "10:16", "buy")
    assert fills(res_down) == trade(TUE, "09:01", "10:16", "sell")


def price_at(day: pd.DataFrame, when: int, column: str) -> float:
    return float(day.loc[day["ts_event"] == when, column].iloc[0])


@pytest.mark.parametrize(("root", "or_high", "tie", "short"), [
    ("MNQ", 20_000.50, 20_001.50, 20_001.25),  # buffer 1.00, one tick 0.25
    ("M2K", 2_000.20, 2_000.60, 2_000.50),  # buffer 0.40, one tick 0.10
    ("MYM", 40_002.0, 40_006.0, 40_005.0)])  # buffer 4, one tick 1
def test_cp2_the_buffer_in_prices_is_1_00_0_40_and_4(root: str, or_high: float, tie: float,
                                                      short: float) -> None:
    # a close exactly at OR_high + buffer buys; one tick less does not
    tie_day, short_day = cp2_day({hm(8, 45): UP4}), cp2_day({hm(8, 45): UP3})
    assert price_at(frame([tie_day], root), ns_at(TUE, hm(8, 35)), "high") == or_high
    assert price_at(frame([tie_day], root), ns_at(TUE, hm(8, 45)), "close") == tie
    assert price_at(frame([short_day], root), ns_at(TUE, hm(8, 45)), "close") == short
    assert fills(run(m(root), [tie_day])) == trade(TUE, "08:46", "10:01")
    assert intents(run(m(root), [short_day])) == []


@pytest.mark.parametrize(("root", "or_low", "tie", "short"), [
    ("MNQ", 19_999.50, 19_998.50, 19_998.75),
    ("M2K", 1_999.80, 1_999.40, 1_999.50),
    ("MYM", 39_998.0, 39_994.0, 39_995.0)])
def test_cp2_the_sell_buffer_in_prices_is_1_00_0_40_and_4(root: str, or_low: float, tie: float,
                                                           short: float) -> None:
    tie_day, short_day = cp2_day({hm(8, 45): DOWN4}), cp2_day({hm(8, 45): DOWN3})
    assert price_at(frame([tie_day], root), ns_at(TUE, hm(8, 40)), "low") == or_low
    assert price_at(frame([tie_day], root), ns_at(TUE, hm(8, 45)), "close") == tie
    assert price_at(frame([short_day], root), ns_at(TUE, hm(8, 45)), "close") == short
    assert fills(run(m(root), [tie_day])) == trade(TUE, "08:46", "10:01", "sell")
    assert intents(run(m(root), [short_day])) == []


def test_cp2_a_deferred_exit_is_not_sent_twice() -> None:
    # a release at 10:01 CT moves the exit fill to 10:03 (D9.5a); while it is pending on the
    # 10:01 and 10:02 bars the member sends nothing more
    res = run(m("M2K"), [cp2_day({hm(8, 45): UP4})], releases=release_at("M2K", TUE, 10, 1))
    assert fills(res) == trade(TUE, "08:46", "10:03")
    assert intents(res) == [(TUE, "08:45", True, None), (TUE, "10:00", True, None)]


def test_cp2_the_0830_bar_is_a_range_bar() -> None:
    # the 08:30 bar's high B+3 is the range high: 08:45 (close B+6) does not trigger, 08:50
    # (close B+7) does
    day = cp2_day({hm(8, 30): (0, 3, 0, 0), hm(8, 45): UP4, hm(8, 50): (0, 7, 0, 7)})
    assert fills(run(m("MYM"), [day])) == trade(TUE, "08:51", "10:06")


@pytest.mark.parametrize("root", ROOTS)
def test_cp2_no_entry_while_an_order_is_pending(root: str) -> None:
    member = m(root)
    assert feed(member, [bar_at(root, TUE, hm(8, 35), CP2_OR[hm(8, 35)]),
                         bar_at(root, TUE, hm(8, 40), CP2_OR[hm(8, 40)])]) == []
    trigger = bar_at(root, TUE, hm(8, 45), UP4)
    view = view_of(root, trigger.ts_event_ns, trigger)
    assert member.on_minute(view, account_of(root, 0, Q_C[root])) == ()
    (intent,) = member.on_minute(view, account_of(root))  # flat: the same bar triggers
    assert (intent.side, intent.quantity) == ("buy", Q_C[root])


@pytest.mark.parametrize("root", ROOTS)
def test_cp2_a_missing_bar_inside_the_hold_moves_the_exit_one_bar(root: str) -> None:
    res = run(m(root), [cp2_day({hm(8, 45): UP4}, skip=frozenset({hm(9, 15)}))])
    assert fills(res) == trade(TUE, "08:46", "10:02")


def test_cp2_has_no_c_minus_2_exit() -> None:
    res = run(m("MNQ"), [cp2_day({hm(13, 0): UP4})])
    assert fills(res) == trade(TUE, "13:01", "14:16")  # not 14:59


@pytest.mark.parametrize("root", ROOTS)
def test_cp2_no_entry_from_1500(root: str) -> None:
    res = run(m(root), [cp2_day({hm(15, 0): UP4, hm(15, 5): UP4})])
    assert intents(res) == []


@pytest.mark.parametrize("root", ROOTS)
def test_cp2_the_last_eligible_bar_1459_is_held_to_f(root: str) -> None:
    # fills at 15:00; the 75th bar would be 16:14, so the engine's flatten at F (15:08) closes it
    # after 8 minutes (spec section 2, Hold)
    res = run(m(root), [cp2_day({hm(14, 59): UP4})])
    assert intents(res) == [(TUE, "14:59", True, None)]
    assert fills(res) == trade(TUE, "15:00", "15:08", exit_reason="forced_flatten")


def test_cp2_f_binds_from_a_1353_fill() -> None:
    # a 13:52 fill exits on its own 75th bar (15:06, fill 15:07); from a 13:53 fill the 75-minute
    # exit would fill at F itself, where the engine's flatten closes the position first
    res = run(m("M2K"), [cp2_day({hm(13, 51): UP4})])
    assert fills(res) == trade(TUE, "13:52", "15:07")
    later = run(m("M2K"), [cp2_day({hm(13, 52): UP4})])
    assert fills(later) == trade(TUE, "13:53", "15:08", exit_reason="forced_flatten")


def test_cp2_position_open_at_a_synthetic_f_is_flattened_by_the_engine() -> None:
    res = run(m("MYM"), [cp2_day({hm(8, 45): UP4}, flatten_from=hm(9, 30))])
    assert fills(res) == trade(TUE, "08:46", "09:31", exit_reason="forced_flatten")
    assert [i[1] for i in intents(res)] == ["08:45"]


@pytest.mark.parametrize("root", ROOTS)
def test_cp2_one_entry_per_trade_date_even_when_the_engine_refuses_it(root: str) -> None:
    # TUE is not a window date: the 08:45 trigger is refused, the 08:55 trigger is not sent
    res = run(m(root), [cp2_day({hm(8, 45): UP4, hm(8, 55): UP4})], window=[WED])
    assert intents(res) == [(TUE, "08:45", False, "engine_not_a_window_date")]


@pytest.mark.parametrize("root", ROOTS)
def test_cp2_the_first_qualifying_bar_takes_the_entry(root: str) -> None:
    # 08:50 qualifies (sell), 09:00 would buy: the first one decides
    res = run(m(root), [cp2_day({hm(8, 50): DOWN4, hm(9, 0): UP4})])
    assert fills(res) == trade(TUE, "08:51", "10:06", "sell")


def test_cp2_one_entry_per_trade_date_after_the_exit() -> None:
    res = run(m("MNQ"), [cp2_day({hm(8, 45): UP4, hm(10, 30): UP4, hm(11, 0): DOWN4})])
    assert fills(res) == trade(TUE, "08:46", "10:01")


def test_cp2_without_an_opening_range_bar_there_is_no_trade() -> None:
    day = cp2_day({hm(8, 45): UP4, hm(9, 30): (0, 40, 0, 40)},
                  skip=frozenset(range(hm(8, 30), hm(8, 45))))
    assert intents(run(m("M2K"), [day])) == []


def test_cp2_one_opening_range_bar_is_enough() -> None:
    # only the 08:44 bar of [08:30, 08:45) is present: OR = its high and low (B..B)
    day = cp2_day({hm(8, 45): (0, 4, 0, 4)}, skip=frozenset(range(hm(8, 30), hm(8, 44))))
    assert fills(run(m("MYM"), [day])) == trade(TUE, "08:46", "10:01")


@pytest.mark.parametrize("root", ROOTS)
def test_cp2_the_range_is_taken_from_the_present_bars(root: str) -> None:
    # the 08:35 bar (the B+2 high) is missing: OR_high = B, so a close of B+4 already buys
    day = cp2_day({hm(8, 45): (0, 4, 0, 4)}, skip=frozenset({hm(8, 35)}))
    assert fills(run(m(root), [day])) == trade(TUE, "08:46", "10:01")
    full = cp2_day({hm(8, 45): (0, 4, 0, 4)})
    assert intents(run(m(root), [full])) == []
    # the low side: the 08:40 bar (the B-2 low) is missing, a close of B-4 sells
    low = cp2_day({hm(8, 45): (0, 0, -4, -4)}, skip=frozenset({hm(8, 40)}))
    assert fills(run(m(root), [low])) == trade(TUE, "08:46", "10:01", "sell")


def test_cp2_the_range_is_the_max_high_and_min_low() -> None:
    # two highs (B+2 at 08:35, B+1 at 08:31) and two lows (B-2, B-1): the range is B-2..B+2
    day = cp2_day({hm(8, 31): (0, 1, -1, 0), hm(8, 45): (0, 5, 0, 5), hm(8, 50): (0, 0, -5, -5),
                   hm(9, 0): UP4})
    assert fills(run(m("MNQ"), [day])) == trade(TUE, "09:01", "10:16")


def test_cp2_bars_before_o_and_on_the_previous_evening_are_not_range_bars() -> None:
    day = cp2_day({hm(8, 29): WIDE, hm(8, 45): UP4}, evening={hm(17, 0): WIDE})
    assert fills(run(m("M2K"), [day])) == trade(TUE, "08:46", "10:01")


def test_cp2_the_0845_bar_is_eligible_and_not_a_range_bar() -> None:
    # a WIDE 08:45 bar closing at B+6 triggers; it does not widen the range first
    day = cp2_day({hm(8, 45): (0, 30, -30, 6)})
    assert fills(run(m("MYM"), [day])) == trade(TUE, "08:46", "10:01")


def test_cp2_has_no_instrument_guard() -> None:
    # the range bars and the trigger bar carry different instrument_ids: D6 and B-H1 name none
    day = cp2_day({hm(8, 45): UP4}, ids={x: 778 for x in range(hm(8, 30), hm(8, 45))})
    assert fills(run(m("MNQ"), [day])) == trade(TUE, "08:46", "10:01")


def test_cp2_a_deferred_entry_fill_starts_the_count_at_the_fill() -> None:
    # a release at 08:46 CT: the entry fills at 08:48 (D9.5a); the bars while the order waits
    # do not count, so the exit fills 75 minutes after the fill
    res = run(m("M2K"), [cp2_day({hm(8, 45): UP4})], releases=release_at("M2K", TUE, 8, 46))
    assert fills(res) == trade(TUE, "08:48", "10:03")


@pytest.mark.parametrize("root", ROOTS)
def test_cp2_d97_engine_exit_no_duplicate_exit_and_no_reentry(root: str) -> None:
    days = [cp2_day({hm(8, 45): UP4, hm(10, 30): UP4, hm(11, 0): DOWN4})]
    member = m(root)
    res = run(member, days, rules=forced_limit_rules(member, days, [(TUE, hm(9, 10))]))
    assert fills(res) == trade(TUE, "08:46", "09:11", exit_reason="price_limit_exit")
    assert [i[1] for i in intents(res)] == ["08:45"]


@pytest.mark.parametrize("root", ROOTS)
def test_cp2_does_not_test_early_halts_the_engine_flattens_at_f(root: str) -> None:
    # Memorial Day 2025-05-26 (halt 12:00, F 11:30): the port trades; the engine's flatten closes
    # the position at F
    day = cp2_day({hm(10, 30): UP4}, HOLIDAY_MD, halt=halt_label(HOLIDAY_MD), end=hm(12, 0))
    res = run(m(root), [day])
    assert intents(res)[0] == (HOLIDAY_MD, "10:30", True, None)
    assert fills(res) == trade(HOLIDAY_MD, "10:31", "11:30", exit_reason="forced_flatten")


def test_cp2_state_resets_each_trade_date() -> None:
    res = run(m("MNQ"), [cp2_day({hm(8, 45): UP4}), cp2_day({hm(9, 30): DOWN4}, WED)])
    assert fills(res) == trade(TUE, "08:46", "10:01") + trade(WED, "09:31", "10:46", "sell")


def test_cp2_the_range_resets_each_trade_date() -> None:
    # TUE's WIDE range (B-30..B+30) must not carry into WED, whose own range is B-2..B+2
    tue = Day(TUE, paths={hm(8, 35): WIDE})
    res = run(m("MYM"), [tue, cp2_day({hm(8, 45): UP4}, WED)])
    assert fills(res) == trade(WED, "08:46", "10:01")
    # and a trade date without its own range bar does not use the previous one
    no_range = Day(WED, paths={hm(8, 45): UP4}, skip=frozenset(range(hm(8, 30), hm(8, 45))))
    res_none = run(m("MYM"), [cp2_day({}), no_range])
    assert intents(res_none) == []


def test_cp2_after_memorial_day_reads_only_the_tuesday() -> None:
    # the holiday's WIDE range and its 11:00 trigger (engine F 11:30) stay on 05-26; Tuesday
    # opens with the holiday's 17:00 reopen, whose bars carry the "12:00" label, and has its own
    # range B-2..B+2: its 08:45 bar triggers
    label = halt_label(HOLIDAY_MD)
    holiday = Day(HOLIDAY_MD, paths={hm(8, 35): WIDE, hm(11, 0): (0, 50, 0, 50)}, halt=label,
                  end=hm(12, 0))
    tue = cp2_day({hm(8, 45): UP4}, TUE_MD, evening={hm(17, 0): WIDE}, evening_halt=label)
    res = run(m("MNQ"), [Day(FRI_MD), holiday, tue])
    assert fills(res) == trade(HOLIDAY_MD, "11:01", "11:30", exit_reason="forced_flatten") + trade(
        TUE_MD, "08:46", "10:01")


def test_cp2_range_and_eligible_bars_are_bars_of_ct_date_d() -> None:
    # direct calls with bars the equity calendar never produces: bars at 08:35 and 08:45 of CT
    # date d-1 carrying trade date d are neither range bars nor eligible bars (S0.4, K7-L-01)
    prev = TUE - timedelta(days=1)
    wrong_range = bar_at("M2K", prev, hm(8, 35), WIDE, trade_day=TUE)
    member = m("M2K")
    assert feed(member, [wrong_range, bar_at("M2K", TUE, hm(8, 35), CP2_OR[hm(8, 35)])]) == []
    (intent,) = feed(member, [bar_at("M2K", TUE, hm(8, 45), UP4)])  # range B..B+2, not WIDE
    assert (intent.side, intent.quantity) == ("buy", 3)
    member = m("M2K")
    wrong_trigger = bar_at("M2K", prev, hm(8, 50), UP4, trade_day=TUE)
    assert feed(member, [bar_at("M2K", TUE, hm(8, 35), CP2_OR[hm(8, 35)]), wrong_trigger]) == []
    (intent,) = feed(member, [bar_at("M2K", TUE, hm(8, 55), DOWN4)])  # the entry is unused
    assert (intent.side, intent.quantity) == ("sell", 3)


def test_cp2_a_monday_reads_no_sunday_evening_bar() -> None:
    # Monday opens Sunday 17:00: those bars are not range bars
    mon = cp2_day({hm(8, 45): UP4}, MON, evening={hm(17, 0): WIDE, hm(17, 1): WIDE})
    assert fills(run(m("MYM"), [mon])) == trade(MON, "08:46", "10:01")
