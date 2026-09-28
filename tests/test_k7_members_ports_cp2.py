"""Stage E.6 K7 ports of MemberCoder-A, part 2: K7-cp2-01 (reports/stage_e6_member_specs.md
section 2; readings E.3-L-07, E.3-L-08, K4-L-06, K7-L-01).

Synthetic bars only, built with tests/test_k7_members_ports.py's kit and run through the real
Stage E engine. No bar file is read.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date
from decimal import Decimal
from typing import Any

import pandas as pd
import pytest

from rules.products import product
from screening.stage_e_engine import EngineInvariantError, Fill, run_engine
from strategy.members.k7 import cp2
from tests._stage_e_canary_kit import rules_for
from tests.test_k7_members_ports import (
    FRI_247,
    HALT_DAY,
    HOLIDAY_BF,
    MON_247,
    ROOT,
    TUE,
    TUE_BF,
    WED,
    Day,
    Ticks,
    account_of,
    bar_at,
    fill_dates,
    fills,
    forced_limit_rules,
    frame,
    halt_label,
    hm,
    holiday_session,
    intents,
    ns_at,
    release_at,
    run,
    trade,
    view_of,
    weekend,
)

# OR bars [08:30, 08:45): the 08:35 high is B+2, the 08:40 low is B-2 (the others at B)
CP2_OR = {hm(8, 35): (0, 2, 0, 0), hm(8, 40): (0, 0, -2, 0)}
UP4 = (0, 6, 0, 6)  # close = OR_high + 4 ticks = OR_high + 20.00
DOWN4 = (0, 0, -6, -6)  # close = OR_low - 4 ticks
UP3, DOWN3 = (0, 5, 0, 5), (0, 0, -5, -5)  # 3 ticks (15.00) beyond: no entry
WIDE = (0, 30, -30, 0)  # a bar that would widen the range to B-30..B+30 if it were read


def cp2_day(extra: Mapping[int, Ticks], day: date = TUE, **kw: Any) -> Day:
    return Day(day, paths={**CP2_OR, **extra}, **kw)


def test_cp2_literals_are_or_15_buffer_4_ticks_hold_75_k4_l06() -> None:
    assert (cp2.RANGE_MINUTES, cp2.BUFFER_TICKS, cp2.HOLD_BARS) == (15, 4, 75)
    assert cp2.BUFFER_TICKS * product(ROOT).vendor_tick == Decimal("20.00")


def test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars() -> None:
    res = run(cp2.make_mbt(), [cp2_day({hm(8, 45): UP4})])
    assert fills(res) == trade(TUE, "08:46", "10:01", "buy")  # 75 minutes fill to fill
    assert intents(res) == [(TUE, "08:45", True, None), (TUE, "10:00", True, None)]
    assert [f.qty for f in res.events(Fill)] == [1, 1]  # q_c = 1 (S0.3)


def test_cp2_a_deferred_exit_is_not_sent_twice() -> None:
    # a release at 10:01 CT moves the exit fill to 10:03 (D9.5a); while it is pending on the
    # 10:01 and 10:02 bars the member sends nothing more
    res = run(cp2.make_mbt(), [cp2_day({hm(8, 45): UP4})], releases=release_at(TUE, 10, 1))
    assert fills(res) == trade(TUE, "08:46", "10:03")
    assert intents(res) == [(TUE, "08:45", True, None), (TUE, "10:00", True, None)]


def test_cp2_the_0830_bar_is_a_range_bar() -> None:
    # the 08:30 bar's high B+3 is the range high: 08:45 (close B+6) does not trigger, 08:50
    # (close B+7) does
    day = cp2_day({hm(8, 30): (0, 3, 0, 0), hm(8, 45): UP4, hm(8, 50): (0, 7, 0, 7)})
    assert fills(run(cp2.make_mbt(), [day])) == trade(TUE, "08:51", "10:06")


def test_cp2_no_entry_while_an_order_is_pending() -> None:
    member = cp2.make_mbt()
    for minute, path in ((hm(8, 35), CP2_OR[hm(8, 35)]), (hm(8, 40), CP2_OR[hm(8, 40)])):
        bar = bar_at(TUE, minute, path)
        assert member.on_minute(view_of(bar.ts_event_ns, bar), account_of()) == ()
    trigger = bar_at(TUE, hm(8, 45), UP4)
    assert member.on_minute(view_of(trigger.ts_event_ns, trigger), account_of(0, 1)) == ()


def test_cp2_breakout_down_sells() -> None:
    res = run(cp2.make_mbt(), [cp2_day({hm(8, 45): DOWN4})])
    assert fills(res) == trade(TUE, "08:46", "10:01", "sell")


def test_cp2_the_buffer_is_exactly_four_ticks_either_side() -> None:
    res_up = run(cp2.make_mbt(), [cp2_day({hm(8, 50): UP3, hm(9, 0): UP4})])
    res_down = run(cp2.make_mbt(), [cp2_day({hm(8, 50): DOWN3, hm(9, 0): DOWN4})])
    assert fills(res_up) == trade(TUE, "09:01", "10:16", "buy")
    assert fills(res_down) == trade(TUE, "09:01", "10:16", "sell")


def price_at(day: pd.DataFrame, when: int, column: str) -> float:
    return float(day.loc[day["ts_event"] == when, column].iloc[0])


def test_cp2_the_buffer_is_20_usd_in_prices() -> None:
    # OR_high = 100010.00: a close of 100030.00 (20.00 beyond, the tie) buys; 100025.00 does not
    tie, short = cp2_day({hm(8, 45): UP4}), cp2_day({hm(8, 45): UP3})
    assert price_at(frame([tie]), ns_at(TUE, hm(8, 35)), "high") == 100_010.0
    assert price_at(frame([tie]), ns_at(TUE, hm(8, 45)), "close") == 100_030.0
    assert price_at(frame([short]), ns_at(TUE, hm(8, 45)), "close") == 100_025.0
    assert fills(run(cp2.make_mbt(), [tie])) == trade(TUE, "08:46", "10:01")
    assert intents(run(cp2.make_mbt(), [short])) == []


def test_cp2_a_close_1999_beyond_the_range_never_reaches_the_member() -> None:
    # 19.99 beyond is off MBT's 5.00 grid: the engine refuses the frame before any member call.
    # (S0.10's round() would count it as 4 ticks; no on-grid price lies strictly between 15.00
    # and 20.00 beyond, so on every bar the engine passes the 4-tick buffer is the 20.00 buffer.)
    day = frame([cp2_day({})])
    at = day.index[day["ts_event"] == ns_at(TUE, hm(8, 45))][0]
    day.loc[at, ["high", "close"]] = 100_010.0 + 19.99
    member = cp2.make_mbt()
    with pytest.raises(EngineInvariantError, match="off the vendor tick grid"):
        run_engine({ROOT: day}, member, member.legs, rules_for(member.legs, [TUE]))


def test_cp2_a_missing_bar_inside_the_hold_moves_the_exit_one_bar() -> None:
    res = run(cp2.make_mbt(), [cp2_day({hm(8, 45): UP4}, skip=frozenset({hm(9, 15)}))])
    assert fills(res) == trade(TUE, "08:46", "10:02")


def test_cp2_has_no_c_minus_2_exit() -> None:
    res = run(cp2.make_mbt(), [cp2_day({hm(13, 0): UP4})])
    assert fills(res) == trade(TUE, "13:01", "14:16")  # not 14:59


def test_cp2_no_entry_from_1500() -> None:
    res = run(cp2.make_mbt(), [cp2_day({hm(15, 0): UP4, hm(15, 5): UP4})])
    assert intents(res) == []


def test_cp2_the_last_eligible_bar_1459_is_held_to_f() -> None:
    # fills at 15:00; the 75th bar would be 16:14, so the engine's flatten at F (15:08) closes it
    # after 8 minutes (spec section 2, Hold)
    res = run(cp2.make_mbt(), [cp2_day({hm(14, 59): UP4})])
    assert intents(res) == [(TUE, "14:59", True, None)]
    assert fills(res) == trade(TUE, "15:00", "15:08", exit_reason="forced_flatten")


def test_cp2_f_binds_from_a_1353_fill() -> None:
    # a 13:52 fill exits on its own 75th bar (15:06, fill 15:07); from a 13:53 fill the 75-minute
    # exit would fill at F itself, where the engine's flatten closes the position first
    res = run(cp2.make_mbt(), [cp2_day({hm(13, 51): UP4})])
    assert fills(res) == trade(TUE, "13:52", "15:07")
    later = run(cp2.make_mbt(), [cp2_day({hm(13, 52): UP4})])
    assert fills(later) == trade(TUE, "13:53", "15:08", exit_reason="forced_flatten")


def test_cp2_position_open_at_a_synthetic_f_is_flattened_by_the_engine() -> None:
    res = run(cp2.make_mbt(), [cp2_day({hm(8, 45): UP4}, flatten_from=hm(9, 30))])
    assert fills(res) == trade(TUE, "08:46", "09:31", exit_reason="forced_flatten")
    assert [i[1] for i in intents(res)] == ["08:45"]


def test_cp2_one_entry_per_trade_date_even_when_the_engine_refuses_it() -> None:
    # TUE is not a window date: the 08:45 trigger is refused, the 08:55 trigger is not sent
    res = run(cp2.make_mbt(), [cp2_day({hm(8, 45): UP4, hm(8, 55): UP4})], window=[WED])
    assert intents(res) == [(TUE, "08:45", False, "engine_not_a_window_date")]


def test_cp2_the_first_qualifying_bar_takes_the_entry() -> None:
    # 08:50 qualifies (sell), 09:00 would buy: the first one decides
    res = run(cp2.make_mbt(), [cp2_day({hm(8, 50): DOWN4, hm(9, 0): UP4})])
    assert fills(res) == trade(TUE, "08:51", "10:06", "sell")


def test_cp2_one_entry_per_trade_date_after_the_exit() -> None:
    res = run(cp2.make_mbt(), [cp2_day({hm(8, 45): UP4, hm(10, 30): UP4, hm(11, 0): DOWN4})])
    assert fills(res) == trade(TUE, "08:46", "10:01")


def test_cp2_without_an_opening_range_bar_there_is_no_trade() -> None:
    day = cp2_day({hm(8, 45): UP4, hm(9, 30): (0, 40, 0, 40)},
                  skip=frozenset(range(hm(8, 30), hm(8, 45))))
    assert intents(run(cp2.make_mbt(), [day])) == []


def test_cp2_one_opening_range_bar_is_enough() -> None:
    # only the 08:44 bar of [08:30, 08:45) is present: OR = its high and low (B..B)
    day = cp2_day({hm(8, 45): (0, 4, 0, 4)}, skip=frozenset(range(hm(8, 30), hm(8, 44))))
    assert fills(run(cp2.make_mbt(), [day])) == trade(TUE, "08:46", "10:01")


def test_cp2_the_range_is_taken_from_the_present_bars() -> None:
    # the 08:35 bar (the B+2 high) is missing: OR_high = B, so a close of B+4 already buys
    day = cp2_day({hm(8, 45): (0, 4, 0, 4)}, skip=frozenset({hm(8, 35)}))
    assert fills(run(cp2.make_mbt(), [day])) == trade(TUE, "08:46", "10:01")
    full = cp2_day({hm(8, 45): (0, 4, 0, 4)})
    assert intents(run(cp2.make_mbt(), [full])) == []
    # the low side: the 08:40 bar (the B-2 low) is missing, a close of B-4 sells
    low = cp2_day({hm(8, 45): (0, 0, -4, -4)}, skip=frozenset({hm(8, 40)}))
    assert fills(run(cp2.make_mbt(), [low])) == trade(TUE, "08:46", "10:01", "sell")


def test_cp2_the_range_is_the_max_high_and_min_low() -> None:
    # two highs (B+2 at 08:35, B+1 at 08:31) and two lows (B-2, B-1): the range is B-2..B+2
    day = cp2_day({hm(8, 31): (0, 1, -1, 0), hm(8, 45): (0, 5, 0, 5), hm(8, 50): (0, 0, -5, -5),
                   hm(9, 0): UP4})
    assert fills(run(cp2.make_mbt(), [day])) == trade(TUE, "09:01", "10:16")


def test_cp2_bars_before_o_and_on_the_previous_evening_are_not_range_bars() -> None:
    day = cp2_day({hm(8, 29): WIDE, hm(8, 45): UP4}, evening={hm(17, 0): WIDE})
    assert fills(run(cp2.make_mbt(), [day])) == trade(TUE, "08:46", "10:01")


def test_cp2_the_0845_bar_is_eligible_and_not_a_range_bar() -> None:
    # a WIDE 08:45 bar closing at B+6 triggers; it does not widen the range first
    day = cp2_day({hm(8, 45): (0, 30, -30, 6)})
    assert fills(run(cp2.make_mbt(), [day])) == trade(TUE, "08:46", "10:01")


def test_cp2_has_no_instrument_guard() -> None:
    # the range bars and the trigger bar carry different instrument_ids: D6 and B-H1 name none
    day = cp2_day({hm(8, 45): UP4}, ids={m: 778 for m in range(hm(8, 30), hm(8, 45))})
    assert fills(run(cp2.make_mbt(), [day])) == trade(TUE, "08:46", "10:01")


def test_cp2_a_deferred_entry_fill_starts_the_count_at_the_fill() -> None:
    # a release at 08:46 CT: the entry fills at 08:48 (D9.5a); the bars while the order waits
    # do not count, so the exit fills 75 minutes after the fill
    res = run(cp2.make_mbt(), [cp2_day({hm(8, 45): UP4})], releases=release_at(TUE, 8, 46))
    assert fills(res) == trade(TUE, "08:48", "10:03")


def test_cp2_an_fomc_1300_fill_is_moved_by_the_engine() -> None:
    # C lines 363-366: an entry fill in [13:00, 13:02) on an FOMC day moves to 13:02
    res = run(cp2.make_mbt(), [cp2_day({hm(12, 59): UP4})], releases=release_at(TUE, 13, 0))
    assert fills(res) == trade(TUE, "13:02", "14:17")


def test_cp2_d97_engine_exit_no_duplicate_exit_and_no_reentry() -> None:
    days = [cp2_day({hm(8, 45): UP4, hm(10, 30): UP4, hm(11, 0): DOWN4})]
    member = cp2.make_mbt()
    res = run(member, days, rules=forced_limit_rules(member, days, [(TUE, hm(9, 10))]))
    assert fills(res) == trade(TUE, "08:46", "09:11", exit_reason="price_limit_exit")
    assert [i[1] for i in intents(res)] == ["08:45"]


def test_cp2_does_not_test_early_halts_the_engine_flattens_at_f() -> None:
    # 2025-07-04 (F 11:30): the port trades; the engine's flatten closes the position at F
    day = cp2_day({hm(10, 30): UP4}, HALT_DAY, halt=halt_label(HALT_DAY))
    res = run(cp2.make_mbt(), [day])
    assert intents(res)[0] == (HALT_DAY, "10:30", True, None)
    assert fills(res) == trade(HALT_DAY, "10:31", "11:30", exit_reason="forced_flatten")


def test_cp2_state_resets_each_trade_date() -> None:
    res = run(cp2.make_mbt(), [cp2_day({hm(8, 45): UP4}), cp2_day({hm(9, 30): DOWN4}, WED)])
    assert fills(res) == trade(TUE, "08:46", "10:01") + trade(WED, "09:31", "10:46", "sell")


def test_cp2_the_range_resets_each_trade_date() -> None:
    # TUE's WIDE range (B-30..B+30) must not carry into WED, whose own range is B-2..B+2
    tue = Day(TUE, paths={hm(8, 35): WIDE})
    res = run(cp2.make_mbt(), [tue, cp2_day({hm(8, 45): UP4}, WED)])
    assert fills(res) == trade(WED, "08:46", "10:01")
    # and a trade date without its own range bar does not use the previous one
    no_range = Day(WED, paths={hm(8, 45): UP4}, skip=frozenset(range(hm(8, 30), hm(8, 45))))
    res_none = run(cp2.make_mbt(), [cp2_day({}), no_range])
    assert intents(res_none) == []


def test_cp2_monday_from_2026_06_01_reads_no_weekend_bar() -> None:
    # Saturday's and Sunday's [08:30, 08:45) bars carry Monday's trade date and would widen the
    # range to B-30..B+30 (no Monday trigger); their 08:50 bars close at B+50 and would trigger
    # (the engine would refuse on a weekend bar, using up the day's entry)
    wrong = {hm(8, 35): WIDE, hm(8, 50): (0, 50, 0, 50)}
    mon = cp2_day({hm(8, 45): UP4}, MON_247, others=weekend(None, wrong, wrong))
    res = run(cp2.make_mbt(), [cp2_day({}, FRI_247), mon])
    assert fills(res) == trade(MON_247, "08:46", "10:01")
    assert intents(res) == [(MON_247, "08:45", True, None), (MON_247, "10:00", True, None)]


def test_cp2_after_a_booked_forward_monday_reads_only_the_tuesday() -> None:
    # the holiday 2026-01-19's bars carry trade date 2026-01-20 and trade until F 11:45 CT: its
    # range bars would widen the range and its 09:00 bar (close B+50) would be accepted by the
    # engine if the member read bars by trade date and clock
    wrong = {hm(8, 35): WIDE, hm(9, 0): (0, 50, 0, 50)}
    tue = cp2_day({hm(8, 45): UP4}, TUE_BF, others=holiday_session(None, wrong))
    res = run(cp2.make_mbt(), [tue])
    assert fills(res) == trade(TUE_BF, "08:46", "10:01")
    assert fill_dates(res) == [TUE_BF, TUE_BF]
    assert HOLIDAY_BF not in [i[0] for i in intents(res)]
