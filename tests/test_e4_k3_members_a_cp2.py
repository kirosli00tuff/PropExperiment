"""Stage E.4 Part 3, K3 members of MemberCoder-A, part 2: K3-cp2-01, the opening-range breakout
(reports/stage_e4c_member_specs.md sections 1-3; catalog reports/stage_e0_catalog_K3.md lines
285-339). Synthetic bars through the real engine, with the kit of tests/test_e4_k3_members_a.py.

The FX row's clock (O 07:20, C 14:00, F 15:08) is the same on all seven roots: OR [07:20, 07:35),
eligible bars [07:35, 14:00), a 75-present-bar hold, no C-2 exit. Expected times are literals.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date
from decimal import Decimal
from typing import Any

import pytest

from rules.products import product
from strategy.members.k3 import cp2
from strategy.members.k3._port_common import EXPOSURES
from tests.test_e4_k3_members_a import (
    CLOCK_DAYS,
    FX_HALTS,
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

UP4 = (0, 6, 0, 6)  # close = OR_high + 4 ticks (OR_high = B+2)
DOWN4 = (0, 0, -6, -6)  # close = OR_low - 4 ticks (OR_low = B-2)
# OR bars: the one at 07:25 has high B+2, the one at 07:30 has low B-2 (the others at B)
CP2_OR: Mapping[int, Ticks] = {hm(7, 25): (0, 2, 0, 0), hm(7, 30): (0, 0, -2, 0)}


def cp2_day(extra: Mapping[int, Ticks], day: date = TUE, **kw: Any) -> Day:
    return Day(day, paths={**CP2_OR, **extra}, **kw)


def test_cp2_literals_are_the_spec_values() -> None:
    assert cp2.RANGE_MINUTES == 15  # OR = [O, O+15) = [07:20, 07:35)
    assert cp2.BUFFER_TICKS == 4  # K4-L-06: 4 vendor ticks of the vehicle
    assert cp2.HOLD_BARS == 75  # E.3-L-07
    buffers = {root: cp2.BUFFER_TICKS * product(root).vendor_tick for root in EXPOSURES}
    assert buffers == {"6E": Decimal("0.0002"), "6A": Decimal("0.0002"), "6B": Decimal("0.0004"),
                       "6C": Decimal("0.0002"), "6J": Decimal("0.000002"),
                       "6S": Decimal("0.0002"), "6N": Decimal("0.0002")}


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars(root: str) -> None:
    res = run(make(cp2, root), [cp2_day({hm(7, 35): UP4})])
    assert fills(res) == trade(TUE, "07:36", "08:51", "buy")  # 75 minutes fill to fill
    assert intents(res) == [(TUE, "07:35", True, None), (TUE, "08:50", True, None)]
    assert [f.qty for f in res.events(Fill)] == [1, 1]  # q_c = 1


@pytest.mark.parametrize("day", CLOCK_DAYS, ids=str)
def test_cp2_keeps_the_ct_clock_in_both_regimes(day: date) -> None:
    for root in EXPOSURES:
        res = run(make(cp2, root), [cp2_day({hm(7, 35): DOWN4}, day)])
        assert fills(res) == trade(day, "07:36", "08:51", "sell"), root


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp2_the_opening_range_is_0720_to_0735(root: str) -> None:
    # a bar just before 07:20 carries extremes that would widen the range; the bars at 07:20 and
    # 07:34 are inside it; the 07:35 bar is the first eligible bar, not a range bar
    inside = {hm(7, 20): (0, 3, 0, 0), hm(7, 34): (0, 0, -3, 0)}  # OR_high B+3, OR_low B-3
    before = {hm(7, 19): (0, 40, -40, 0)}
    buy = run(make(cp2, root), [cp2_day({**inside, **before, hm(7, 35): (0, 7, 0, 7)})])
    assert intents(buy)[0] == (TUE, "07:35", True, None)  # B+7 = OR_high + 4
    assert fills(buy)[0] == (TUE, "07:36", "buy", "strategy")
    assert intents(run(make(cp2, root), [cp2_day({**inside, hm(7, 35): (0, 6, 0, 6)})])) == []
    # the sell-side pair pins the range's end: the 07:34 bar's B-3 low is in the range, so B-7
    # at 07:35 sells and B-6 does not. A 14-minute range [07:20, 07:34) would have OR_low B-2
    # and would sell at B-6
    sell = run(make(cp2, root), [cp2_day({**inside, hm(7, 35): (0, 0, -7, -7)})])
    assert fills(sell)[0] == (TUE, "07:36", "sell", "strategy")
    assert intents(run(make(cp2, root), [cp2_day({**inside, hm(7, 35): (0, 0, -6, -6)})])) == []


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp2_the_buffer_is_exactly_four_ticks_either_side(root: str) -> None:
    # 3 ticks beyond the range at 07:40: no entry; exactly 4 at 07:50: the entry
    up3, down3 = (0, 5, 0, 5), (0, 0, -5, -5)
    res_up = run(make(cp2, root), [cp2_day({hm(7, 40): up3, hm(7, 50): UP4})])
    res_down = run(make(cp2, root), [cp2_day({hm(7, 40): down3, hm(7, 50): DOWN4})])
    assert fills(res_up) == trade(TUE, "07:51", "09:06", "buy")
    assert fills(res_down) == trade(TUE, "07:51", "09:06", "sell")
    assert intents(res_up)[0] == intents(res_down)[0] == (TUE, "07:50", True, None)


def test_cp2_a_missing_bar_inside_the_hold_moves_the_exit_one_bar() -> None:
    res = run(cp2.make_6e(), [cp2_day({hm(7, 35): UP4}, skip=frozenset({hm(8, 0)}))])
    assert fills(res) == trade(TUE, "07:36", "08:52")
    assert intents(res)[-1] == (TUE, "08:51", True, None)


def test_cp2_a_missing_trigger_bar_moves_the_entry_to_the_next_qualifying_bar() -> None:
    # the entry is "the first eligible bar whose close is beyond": a missing bar is not a bar
    res = run(cp2.make_6j(), [cp2_day({hm(7, 35): UP4, hm(7, 36): UP4},
                                      skip=frozenset({hm(7, 35)}))])
    assert fills(res) == trade(TUE, "07:37", "08:52")


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp2_has_no_c_minus_2_exit(root: str) -> None:
    res = run(make(cp2, root), [cp2_day({hm(13, 0): UP4})])
    assert fills(res) == trade(TUE, "13:01", "14:16")  # not at 13:59


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp2_no_entry_from_1400(root: str) -> None:
    res = run(make(cp2, root), [cp2_day({hm(14, 0): UP4, hm(14, 5): UP4, hm(15, 0): DOWN4})])
    assert intents(res) == []


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp2_entry_at_1359_is_flattened_by_the_engine_at_f(root: str) -> None:
    # the catalog's "an entry filled after 13:53 is cut short by F" (C lines 324-325)
    res = run(make(cp2, root), [cp2_day({hm(13, 59): UP4, hm(14, 0): UP4})])
    assert fills(res) == trade(TUE, "14:00", "15:08", exit_reason="forced_flatten")
    assert [i[1] for i in intents(res)] == ["13:59"]  # 68 held bars < 75: no member exit


def test_cp2_an_entry_filled_at_1353_meets_f_and_one_at_1352_exits_itself() -> None:
    res = run(cp2.make_6n(), [cp2_day({hm(13, 52): UP4})])
    assert fills(res) == trade(TUE, "13:53", "15:08", exit_reason="forced_flatten")
    res2 = run(cp2.make_6n(), [cp2_day({hm(13, 51): UP4})])
    assert fills(res2) == trade(TUE, "13:52", "15:07")


def test_cp2_position_open_at_a_synthetic_f_is_flattened_by_the_engine() -> None:
    res = run(cp2.make_6e(), [cp2_day({hm(7, 35): UP4}, flatten_from=hm(8, 20))])
    assert fills(res) == trade(TUE, "07:36", "08:21", exit_reason="forced_flatten")
    assert [i[1] for i in intents(res)] == ["07:35"]


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp2_one_entry_per_trade_date_even_when_the_engine_refuses_it(root: str) -> None:
    # TUE is not a window date: the first trigger is refused, the second is not sent
    res = run(make(cp2, root), [cp2_day({hm(7, 35): UP4, hm(7, 45): UP4})], window=[WED])
    assert intents(res) == [(TUE, "07:35", False, "engine_not_a_window_date")]


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp2_one_entry_per_trade_date_after_the_exit(root: str) -> None:
    res = run(make(cp2, root), [cp2_day({hm(7, 35): UP4, hm(9, 0): UP4, hm(10, 0): DOWN4})])
    assert fills(res) == trade(TUE, "07:36", "08:51")


def test_cp2_without_an_opening_range_bar_there_is_no_trade() -> None:
    day = cp2_day({hm(7, 35): UP4, hm(8, 0): (0, 40, 0, 40)},
                  skip=frozenset(range(hm(7, 20), hm(7, 35))))
    assert intents(run(cp2.make_6c(), [day])) == []


def test_cp2_the_range_is_taken_from_the_present_bars() -> None:
    # the 07:25 bar (the B+2 high) is missing: OR_high = B, so a close of B+4 already buys
    day = cp2_day({hm(7, 35): (0, 4, 0, 4)}, skip=frozenset({hm(7, 25)}))
    assert fills(run(cp2.make_6s(), [day])) == trade(TUE, "07:36", "08:51")
    full = cp2_day({hm(7, 35): (0, 4, 0, 4)})
    assert intents(run(cp2.make_6s(), [full])) == []


def test_cp2_bars_before_0720_and_on_the_previous_evening_are_not_range_bars() -> None:
    day = cp2_day({hm(7, 10): (0, 30, -30, 0), hm(7, 35): UP4},
                  evening={hm(17, 0): (0, 30, -30, 0)})
    assert fills(run(cp2.make_6e(), [day])) == trade(TUE, "07:36", "08:51")


def test_cp2_the_range_has_no_instrument_guard() -> None:
    # D6 and B-H1 have none (E.3-L-08): a range bar with another instrument_id changes nothing
    day = cp2_day({hm(7, 35): UP4}, ids={hm(7, 25): 778})
    assert fills(run(cp2.make_6b(), [day])) == trade(TUE, "07:36", "08:51")


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp2_the_0730_release_inside_the_range_meets_no_fill(root: str) -> None:
    # catalog section 7 item 9 / C lines 330-334: on BLS days the range contains the 07:30 CT
    # release; the earliest fill, 07:36, is outside [07:30, 07:32); the range bars are read
    res = run(make(cp2, root), [cp2_day({hm(7, 35): UP4})], releases=release_at(root, TUE, 7, 30))
    assert fills(res) == trade(TUE, "07:36", "08:51")
    assert res.counters.get("fill_guard_deferral", 0) == 0


def test_cp2_a_deferred_entry_fill_starts_the_count_at_the_fill() -> None:
    # a release at 07:36 CT: the entry fills at 07:38 (D9.5a); the bars while the order waits
    # do not count, so the exit fills 75 minutes after the fill
    res = run(cp2.make_6e(), [cp2_day({hm(7, 35): UP4})], releases=release_at("6E", TUE, 7, 36))
    assert fills(res) == trade(TUE, "07:38", "08:53")


def test_cp2_a_release_next_to_the_fill_leaves_it_alone() -> None:
    for hh, mm in ((7, 34), (7, 37)):  # guards [07:34, 07:36) and [07:37, 07:39)
        res = run(cp2.make_6a(), [cp2_day({hm(7, 35): UP4})],
                  releases=release_at("6A", TUE, hh, mm))
        assert fills(res)[0] == (TUE, "07:36", "buy", "strategy")


def test_cp2_a_release_at_the_exit_fill_holds_the_exit() -> None:
    res = run(cp2.make_6j(), [cp2_day({hm(7, 35): UP4})], releases=release_at("6J", TUE, 8, 51))
    assert fills(res) == trade(TUE, "07:36", "08:53")
    assert [i[1] for i in intents(res)] == ["07:35", "08:50"]  # pending: no resend


@pytest.mark.parametrize("root", EXPOSURES)
def test_cp2_d97_engine_exit_no_duplicate_exit_and_no_reentry(root: str) -> None:
    days = [cp2_day({hm(7, 35): UP4, hm(9, 5): UP4, hm(10, 5): DOWN4})]
    member = make(cp2, root)
    res = run(member, days, rules=forced_limit_rules(member, days, [(TUE, hm(8, 0))]))
    assert fills(res) == trade(TUE, "07:36", "08:01", exit_reason="price_limit_exit")
    assert [i[1] for i in intents(res)] == ["07:35"]


@pytest.mark.parametrize("halt_day", list(FX_HALTS), ids=str)
def test_cp2_does_not_test_early_halts_the_engine_flattens_at_f(halt_day: date) -> None:
    # a port (C lines 49-50): it trades a halt day and the engine flattens at that day's F
    # (2026-04-03, Good Friday with the 07:30 NFP: F 08:00; the others 11:30 or 11:45)
    f = FX_HALTS[halt_day][2]
    trigger = hm(7, 40) if f == "08:00" else hm(10, 40)
    for root in EXPOSURES:
        res = run(make(cp2, root), [cp2_day({trigger: UP4}, halt_day, halt=halt_label(halt_day))])
        entry_fill = f"{(trigger + 1) // 60:02d}:{(trigger + 1) % 60:02d}"
        assert fills(res) == trade(halt_day, entry_fill, f, exit_reason="forced_flatten"), root


def test_cp2_state_resets_each_trade_date() -> None:
    res = run(cp2.make_6n(), [cp2_day({hm(7, 35): UP4}), cp2_day({hm(9, 0): DOWN4}, WED)])
    assert fills(res) == trade(TUE, "07:36", "08:51") + trade(WED, "09:01", "10:16", "sell")
