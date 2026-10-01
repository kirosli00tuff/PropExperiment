"""Stage E.8 K6 ports of MemberCoder-A, part 2: K6-cp2-01 on ZC, ZW, ZS, ZM, ZL, HE and LE
(reports/stage_e8_member_specs.md section 2; readings E.3-L-07, E.3-L-08, K4-L-06, K7-L-01).

Synthetic bars only, built with tests/test_k6_members_ports.py's kit and run through the real
Stage E engine, plus direct calls where the calendars never produce the case. No bar file is read.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, time
from decimal import Decimal
from typing import Any

import pytest

from rules.products import product
from strategy.members.k6 import cp2
from tests.test_k6_members_ports import (
    EVENING,
    GRAIN_ROOTS,
    HALT_XMAS,
    LIVESTOCK_ROOTS,
    MON,
    ROOTS,
    TICK,
    TUE,
    WED,
    Day,
    Ticks,
    account_of,
    bar_at,
    fill_qty,
    fills,
    frame,
    grp,
    halt_label,
    hm,
    intents,
    is_grain,
    make,
    price,
    run,
    stop_offsets,
    trade,
    view_of,
)

# OR bars [08:30, 08:45): the 08:35 high is B+2, the 08:40 low is B-2 (the others at B)
CP2_OR = {hm(8, 35): (0, 2, 0, 0), hm(8, 40): (0, 0, -2, 0)}
UP4 = (0, 6, 0, 6)  # close = OR_high + 4 ticks (the buffer)
DOWN4 = (0, 0, -6, -6)  # close = OR_low - 4 ticks
UP3, DOWN3 = (0, 5, 0, 5), (0, 0, -5, -5)  # 3 ticks beyond: no entry
WIDE = (0, 30, -30, 0)  # a bar that would widen the range to B-30..B+30 if it were read
BUFFER = {"ZC": Decimal("1.00"), "ZW": Decimal("1.00"), "ZS": Decimal("1.00"),
          "ZM": Decimal("0.40"), "ZL": Decimal("0.04"), "HE": Decimal("0.100"),
          "LE": Decimal("0.100")}


def clock(minute: int) -> str:
    return f"{minute // 60:02d}:{minute % 60:02d}"


def cp2_day(extra: Mapping[int, Ticks], day: date = TUE, **kw: Any) -> Day:
    return Day(day, paths={**CP2_OR, **extra}, **kw)


def m(root: str = "ZC") -> cp2.Cp2Breakout:
    return make(cp2, root)


@pytest.mark.parametrize("root", ROOTS)
def test_cp2_literals_are_or_15_buffer_4_ticks_hold_75_k4_l06(root: str) -> None:
    assert (cp2.RANGE_MINUTES, cp2.BUFFER_TICKS, cp2.HOLD_BARS) == (15, 4, 75)
    f_regular = {"grains": time(13, 18), "livestock": time(13, 3)}
    assert f_regular == cp2.F_REGULAR_CT
    buffer = cp2.BUFFER_TICKS * product(root).vendor_tick
    assert buffer == BUFFER[root]  # ZC, ZW, ZS 1.00; ZM 0.40; ZL 0.04; HE, LE 0.100
    assert product(root).vendor_tick == TICK[root]


@pytest.mark.parametrize("root", ROOTS)
def test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars(root: str) -> None:
    res = run(m(root), [cp2_day({hm(8, 45): UP4})])
    assert fills(res) == trade(TUE, "08:46", "10:01", "buy")  # 75 minutes fill to fill
    assert intents(res) == [(TUE, "08:45", True, None), (TUE, "10:00", True, None)]
    assert fill_qty(res) == [1, 1]


@pytest.mark.parametrize("root", ROOTS)
def test_cp2_breakout_down_sells(root: str) -> None:
    res = run(m(root), [cp2_day({hm(8, 50): DOWN4})])
    assert fills(res) == trade(TUE, "08:51", "10:06", "sell")


@pytest.mark.parametrize("root", ROOTS)
def test_cp2_the_buffer_is_exactly_four_ticks_either_side(root: str) -> None:
    # a close exactly at OR_high + 4 ticks buys, one tick less does not; the same below
    assert fills(run(m(root), [cp2_day({hm(9, 0): UP4})])) == trade(TUE, "09:01", "10:16")
    assert intents(run(m(root), [cp2_day({hm(9, 0): UP3})])) == []
    assert fills(run(m(root), [cp2_day({hm(9, 0): DOWN4})])) == trade(TUE, "09:01", "10:16",
                                                                       "sell")
    assert intents(run(m(root), [cp2_day({hm(9, 0): DOWN3})])) == []


@pytest.mark.parametrize("root", ROOTS)
def test_cp2_the_buffer_in_prices(root: str) -> None:
    # OR_high = B+2: the tie close is OR_high + BUFFER in the root's vendor units
    or_high = Decimal(repr(price(root, 2)))
    assert Decimal(repr(price(root, 6))) == or_high + BUFFER[root]
    assert Decimal(repr(price(root, 5))) == or_high + BUFFER[root] - TICK[root]
    or_low = Decimal(repr(price(root, -2)))
    assert Decimal(repr(price(root, -6))) == or_low - BUFFER[root]


@pytest.mark.parametrize("root", ("ZC", "HE"))
def test_cp2_the_first_qualifying_bar_takes_the_entry(root: str) -> None:
    # 08:50 qualifies down, 09:00 up: the first decides; one entry only
    res = run(m(root), [cp2_day({hm(8, 50): DOWN4, hm(9, 0): UP4})])
    assert fills(res) == trade(TUE, "08:51", "10:06", "sell")
    assert [i[1] for i in intents(res)] == ["08:50", "10:05"]


@pytest.mark.parametrize("root", ROOTS)
def test_cp2_one_entry_per_trade_date_even_when_the_engine_refuses_it(root: str) -> None:
    # the 08:50 close is at the D9.7 upper stop level (prior settlement B): CP2's trigger
    # fires, the engine refuses the open (price_limit_zone_no_entry), and the 09:00 trigger
    # is not used
    up, _ = stop_offsets(root, TUE, 0)
    res = run(m(root), [cp2_day({hm(8, 50): (0, up, 0, up), hm(9, 0): UP4})])
    assert intents(res) == [(TUE, "08:50", False, "price_limit_zone_no_entry")]
    assert fills(res) == []
    # one tick inside the stop: the 08:50 entry is accepted
    res = run(m(root), [cp2_day({hm(8, 50): (0, up - 1, 0, up - 1)})])
    assert fills(res) == trade(TUE, "08:51", "10:06")


def test_cp2_one_entry_per_trade_date_after_the_exit() -> None:
    res = run(m("ZW"), [cp2_day({hm(8, 45): UP4, hm(10, 30): UP4})])
    assert fills(res) == trade(TUE, "08:46", "10:01")


@pytest.mark.parametrize("root", ("ZS", "LE"))
def test_cp2_no_entry_while_an_order_is_pending(root: str) -> None:
    member = m(root)
    bars = [bar_at(root, TUE, hm(8, 35), (0, 2, -2, 0)), bar_at(root, TUE, hm(8, 45), UP4)]
    assert member.on_minute(view_of(root, bars[0].ts_event_ns, bars[0]), account_of(root)) == ()
    trigger = view_of(root, bars[1].ts_event_ns, bars[1])
    assert member.on_minute(trigger, account_of(root, 0, 1)) == ()  # pending: no entry
    (intent,) = member.on_minute(trigger, account_of(root))
    assert (intent.side, intent.quantity) == ("buy", 1)


@pytest.mark.parametrize("root", ("ZM", "HE"))
def test_cp2_a_missing_bar_inside_the_hold_moves_the_exit_one_bar(root: str) -> None:
    res = run(m(root), [cp2_day({hm(8, 45): UP4}, skip=frozenset({hm(9, 30)}))])
    assert fills(res) == trade(TUE, "08:46", "10:02")


@pytest.mark.parametrize("root", ROOTS)
def test_cp2_has_no_c_minus_2_exit(root: str) -> None:
    # grains: fill 12:01, 75th present bar 13:15, exit fill 13:16 (no 13:13 exit); livestock:
    # fill 11:46, 75th present bar 13:00, exit fill 13:01 (no 12:58 exit); both before F
    trig = hm(12, 0) if is_grain(root) else hm(11, 45)
    res = run(m(root), [cp2_day({trig: UP4})])
    assert fills(res) == trade(TUE, clock(trig + 1), clock(trig + 76))
    assert [i[1] for i in intents(res)] == [clock(trig), clock(trig + 75)]


@pytest.mark.parametrize("root", ROOTS)
def test_cp2_no_entry_from_c(root: str) -> None:
    c = hm(13, 15) if is_grain(root) else hm(13, 0)
    res = run(m(root), [cp2_day({c: UP4, c + 1: UP4})])
    assert intents(res) == [] and fills(res) == []


@pytest.mark.parametrize("root", ROOTS)
def test_cp2_the_last_eligible_bar_is_held_to_f(root: str) -> None:
    # C-1 qualifies (grains 13:14, livestock 12:59): fill at C, the engine flattens at the F
    # bar's open (grains 13:18, livestock 13:03)
    c = hm(13, 15) if is_grain(root) else hm(13, 0)
    f = hm(13, 18) if is_grain(root) else hm(13, 3)
    res = run(m(root), [cp2_day({c - 1: UP4})])
    assert fills(res) == trade(TUE, clock(c), clock(f), exit_reason="forced_flatten")
    assert [i[1] for i in intents(res)] == [clock(c - 1)]


@pytest.mark.parametrize("root", ("ZL", "LE"))
def test_cp2_position_open_at_a_synthetic_f_is_flattened_by_the_engine(root: str) -> None:
    res = run(m(root), [cp2_day({hm(8, 45): UP4}, flatten_from=hm(9, 30))])
    assert fills(res) == trade(TUE, "08:46", "09:31", exit_reason="forced_flatten")
    assert [i[1] for i in intents(res)] == ["08:45"]


def test_cp2_without_an_opening_range_bar_there_is_no_trade() -> None:
    for root in ("ZC", "HE"):
        skip = frozenset(range(hm(8, 30), hm(8, 45)))
        res = run(m(root), [cp2_day({hm(8, 45): UP4, hm(9, 0): (0, 40, 0, 40)}, skip=skip)])
        assert intents(res) == [], root


@pytest.mark.parametrize("root", ("ZS", "LE"))
def test_cp2_one_opening_range_bar_is_enough(root: str) -> None:
    only_range = frozenset(range(hm(8, 30), hm(8, 45))) - {hm(8, 44)}
    res = run(m(root), [Day(TUE, paths={hm(8, 44): (0, 2, -2, 0), hm(8, 50): UP4},
                            skip=only_range)])
    assert fills(res) == trade(TUE, "08:51", "10:06")


@pytest.mark.parametrize("root", ROOTS)
def test_cp2_the_range_is_taken_from_the_present_bars(root: str) -> None:
    # the 08:35 high bar missing: OR_high is B, so a close of B+4 already buys
    res = run(m(root), [cp2_day({hm(9, 0): (0, 4, 0, 4)}, skip=frozenset({hm(8, 35)}))])
    assert fills(res) == trade(TUE, "09:01", "10:16")
    assert intents(run(m(root), [cp2_day({hm(9, 0): (0, 4, 0, 4)})])) == []


def test_cp2_the_range_is_the_max_high_and_min_low() -> None:
    # the 08:30 and 08:44 bars are range bars and widen it to B+5 / B-5
    extra = {hm(8, 30): (0, 5, 0, 0), hm(8, 44): (0, 0, -5, 0), hm(9, 0): UP4,
             hm(9, 10): (0, 9, 0, 9)}
    res = run(m("ZC"), [cp2_day(extra)])
    assert fills(res) == trade(TUE, "09:11", "10:26")


@pytest.mark.parametrize("root", GRAIN_ROOTS)
def test_cp2_grain_evening_and_overnight_bars_are_not_range_bars(root: str) -> None:
    evening = {hm(19, 0): WIDE, hm(19, 4): WIDE}
    res = run(m(root), [cp2_day({hm(7, 40): WIDE, hm(7, 44): WIDE, hm(8, 45): UP4},
                                evening=evening)])
    assert fills(res) == trade(TUE, "08:46", "10:01")
    # nor are they eligible bars: a qualifying close there is no entry
    res = run(m(root), [cp2_day({hm(7, 44): UP4}, evening={hm(19, 0): UP4})])
    assert intents(res) == []


def test_cp2_the_0845_bar_is_eligible_and_not_a_range_bar() -> None:
    # 08:45 is wide (B-30..B+30) and closes at B: no trigger, and it does not widen the range
    res = run(m("HE"), [cp2_day({hm(8, 45): WIDE, hm(8, 46): UP4})])
    assert fills(res) == trade(TUE, "08:47", "10:02")


@pytest.mark.parametrize("root", ("ZC", "LE"))
def test_cp2_has_no_instrument_guard(root: str) -> None:
    ids = {hm(8, 35): 1, hm(8, 40): 2}  # the range bars' ids differ from the trigger's (777)
    res = run(m(root), [cp2_day({hm(8, 45): UP4}, ids=ids)])
    assert fills(res) == trade(TUE, "08:46", "10:01")


@pytest.mark.parametrize("root", ROOTS)
def test_cp2_d97_engine_exit_no_duplicate_exit_and_no_reentry(root: str) -> None:
    up, _ = stop_offsets(root, TUE, 0)
    res = run(m(root), [cp2_day({hm(8, 45): UP4, hm(9, 10): (0, up, 0, up),
                                 hm(9, 20): UP4})])
    assert fills(res) == trade(TUE, "08:46", "09:11", exit_reason="price_limit_exit")
    assert [i[1] for i in intents(res)] == ["08:45"]  # no 75-bar exit, no second entry


@pytest.mark.parametrize("root", ("ZW", "HE"))
def test_cp2_does_not_test_early_halts_the_engine_flattens_at_f(root: str) -> None:
    # 2025-12-24: F 11:45 (both groups); the 11:00 entry fills 11:01 and is flattened at the
    # 11:45 open
    end = hm(12, 5) if is_grain(root) else hm(12, 15)
    day = cp2_day({hm(11, 0): UP4}, HALT_XMAS, halt=halt_label(grp(root), HALT_XMAS), end=end)
    res = run(m(root), [day])
    assert fills(res) == trade(HALT_XMAS, "11:01", "11:45", exit_reason="forced_flatten")


@pytest.mark.parametrize("root", ("ZL", "LE"))
def test_cp2_state_and_range_reset_each_trade_date(root: str) -> None:
    # WED: no range bar; TUE's range must not carry over
    wed = Day(WED, paths={hm(9, 0): UP4}, skip=frozenset(range(hm(8, 30), hm(8, 45))))
    res = run(m(root), [cp2_day({hm(8, 45): UP4}), wed])
    assert fills(res) == trade(TUE, "08:46", "10:01")
    # WED's range is its own: B+20 high on WED makes TUE's B+6 close no trigger on WED
    wed2 = cp2_day({hm(8, 31): (0, 20, 0, 0), hm(9, 0): UP4}, WED)
    res = run(m(root), [cp2_day({hm(8, 45): UP4}), wed2])
    assert fills(res) == trade(TUE, "08:46", "10:01")
    both = run(m(root), [cp2_day({hm(8, 45): UP4}), cp2_day({hm(9, 0): UP4}, WED)])
    assert fills(both) == trade(TUE, "08:46", "10:01") + trade(WED, "09:01", "10:16")


@pytest.mark.parametrize("root", GRAIN_ROOTS)
def test_cp2_a_monday_reads_no_sunday_evening_bar(root: str) -> None:
    day = cp2_day({hm(8, 45): UP4}, MON, evening={hm(19, 0): WIDE})
    assert frame([day], root).iloc[0]["trade_date"] == MON.isoformat()
    assert fills(run(m(root), [day])) == trade(MON, "08:46", "10:01")
    assert len(EVENING) == 5


@pytest.mark.parametrize("root", LIVESTOCK_ROOTS)
def test_cp2_livestock_range_and_eligible_bars_are_bars_of_ct_date_d(root: str) -> None:
    # direct calls: bars of CT date d-1 carrying trade date d are never range or eligible bars
    member = m(root)
    bars = [bar_at(root, MON, hm(8, 35), WIDE, trade_day=TUE),
            bar_at(root, TUE, hm(8, 35), (0, 2, -2, 0)),
            bar_at(root, MON, hm(8, 50), UP4, trade_day=TUE),
            bar_at(root, TUE, hm(8, 50), UP4)]
    out = []
    for bar in bars:
        out += member.on_minute(view_of(root, bar.ts_event_ns, bar), account_of(root))
    (intent,) = out
    assert intent.ts_utc == view_of(root, bars[3].ts_event_ns, bars[3]).decision_ts_utc


@pytest.mark.parametrize("root", ("ZC", "HE"))
def test_cp2_a_pending_exit_is_not_sent_twice(root: str) -> None:
    # direct calls: after the trigger, 74 present bars with the position open send nothing; on
    # the 75th an exit pending on the leg (a deferred fill) suppresses a second exit
    member = m(root)
    for bar, acct in ((bar_at(root, TUE, hm(8, 35), (0, 2, -2, 0)), account_of(root)),
                      (bar_at(root, TUE, hm(8, 45), UP4), account_of(root))):
        out = member.on_minute(view_of(root, bar.ts_event_ns, bar), acct)
    assert len(out) == 1
    for k in range(74):
        bar = bar_at(root, TUE, hm(8, 46) + k)
        assert member.on_minute(view_of(root, bar.ts_event_ns, bar), account_of(root, 1)) == ()
    bar = bar_at(root, TUE, hm(10, 0))
    view = view_of(root, bar.ts_event_ns, bar)
    assert member.on_minute(view, account_of(root, 1, -1)) == ()
    (intent,) = member.on_minute(view, account_of(root, 1))
    assert (intent.side, intent.quantity) == ("sell", 1)
