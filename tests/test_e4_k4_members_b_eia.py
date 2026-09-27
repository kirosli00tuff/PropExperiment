"""Stage E.4 K4 members of MemberCoder-B, part 2: K4-eiafade-01 and K4-eiamom-01
(reports/stage_e4_member_specs.md sections 0, 6, 7, 10, 11). The synthetic kit is
tests/test_e4_k4_members_b.py's. Synthetic bars only, run through the real Stage E engine.
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from screening.stage_e_engine import Fill
from strategy.members.k4 import _releases as tables
from strategy.members.k4 import eiafade, eiamom
from strategy.members.k4._event_common import BUY, SELL
from tests.test_e4_k4_members_b import (
    THU,
    WED,
    Day,
    base_ticks,
    decided,
    fills,
    forced_limit_rules,
    hm,
    intents,
    release_at,
    run,
    trade,
)

T0 = base_ticks("MCL")  # 7000 ticks = 70.00; 0.5% of it is 35 ticks exactly
HALF_PCT = T0 // 200
MOVED = date(2025, 5, 29)  # Thursday 12:00 ET WPSR (T_W 11:00 CT), the Memorial Day week
DROPPED = date(2026, 5, 28)  # section 11's dropped WPSR (Thursday 12:00 ET, T_W 11:00 CT)


def test_the_wpsr_rows_used_by_the_tests() -> None:
    wpsr = {r[0]: r for r in tables.WPSR}
    assert wpsr["2025-06-04"] == ("2025-06-04", "09:30", 2, True)
    assert wpsr["2019-05-30"] == ("2019-05-30", "10:00", 3, False)  # 11:00 ET
    assert wpsr["2025-05-29"] == ("2025-05-29", "11:00", 3, False)  # 12:00 ET
    assert wpsr["2024-12-27"] == ("2024-12-27", "12:00", 4, False)  # 13:00 ET
    assert "2025-05-28" not in wpsr and DROPPED.isoformat() not in wpsr
    assert "2025-12-29" not in wpsr  # the 16:00 CT row is dropped in section 11 as well
    assert HALF_PCT == 35


# -------------------------------------------------------------------- eiafade ----
def _fade_day(day: date = WED, t_w: int = hm(9, 30), move: int = 0, **kw: object) -> Day:
    """t0 = the T_W - 1 close at the base price, t14 = the T_W + 14 close ``move`` ticks away."""
    closes = {t_w - 1: 0, t_w + 14: move, **kw.pop("closes", {})}  # type: ignore[dict-item]
    return Day(day, closes=closes, **kw)  # type: ignore[arg-type]


def test_eiafade_the_side_rule_is_exact_on_integer_ticks() -> None:
    assert eiafade.fade_side(T0, T0 - HALF_PCT) == BUY  # M = -0.005 exactly
    assert eiafade.fade_side(T0, T0 - HALF_PCT + 1) is None  # just inside
    assert eiafade.fade_side(T0, T0 + HALF_PCT) == SELL  # M = +0.005 exactly
    assert eiafade.fade_side(T0, T0 + HALF_PCT - 1) is None
    assert eiafade.fade_side(T0, T0) is None
    assert eiafade.fade_side(201, 200) is None and eiafade.fade_side(200, 199) == BUY
    assert eiafade.fade_side(0, -10) is None and eiafade.fade_side(-100, 0) is None  # C10


def test_eiafade_m_at_exactly_minus_half_percent_buys() -> None:
    res = run(eiafade.make_mcl(), [_fade_day(move=-HALF_PCT)])
    assert intents(res) == decided(WED, "09:44", "13:28")
    assert fills(res) == trade(WED, "09:45", "13:29", side="buy")
    assert [f.qty for f in res.events(Fill)] == [4, 4]


def test_eiafade_m_at_exactly_plus_half_percent_sells() -> None:
    res = run(eiafade.make_mcl(), [_fade_day(move=HALF_PCT)])
    assert fills(res) == trade(WED, "09:45", "13:29", side="sell")


@pytest.mark.parametrize("move", [-HALF_PCT + 1, HALF_PCT - 1, 0])
def test_eiafade_just_inside_either_threshold_is_no_trade(move: int) -> None:
    res = run(eiafade.make_mcl(), [_fade_day(move=move)])
    assert intents(res) == [] and fills(res) == []


@pytest.mark.parametrize("t0_offset,t14_offset", [(-T0, -T0 - 10), (-T0 - 100, -T0)])
def test_eiafade_c10_a_non_positive_t_w_minus_1_close_is_no_trade(t0_offset: int,
                                                                    t14_offset: int) -> None:
    """t0 = 0.00 (with t14 = -0.10 the unguarded formula would BUY) and t0 = -1.00 (with t14 =
    0.00 it would SELL): C10 requires t0 > 0."""
    day = Day(WED, closes={hm(9, 29): t0_offset, hm(9, 44): t14_offset})
    res = run(eiafade.make_mcl(), [day])
    assert intents(res) == [] and fills(res) == []


@pytest.mark.parametrize("day,t_w,entry_fill", [
    (WED, hm(9, 30), "09:45"), (date(2019, 5, 30), hm(10, 0), "10:15"),
    (MOVED, hm(11, 0), "11:15"), (date(2024, 12, 27), hm(12, 0), "12:15")],
    ids=["0930", "1000", "1100", "1200"])
def test_eiafade_every_slot_enters_at_t_w_plus_15_and_exits_at_1329(day: date, t_w: int,
                                                                     entry_fill: str) -> None:
    res = run(eiafade.make_mcl(), [_fade_day(day, t_w, -HALF_PCT)])
    entry_decision = f"{(t_w + 14) // 60:02d}:{(t_w + 14) % 60:02d}"
    assert intents(res) == decided(day, entry_decision, "13:28")
    assert fills(res) == trade(day, entry_fill, "13:29", side="buy")


def test_eiafade_a_moved_release_moves_the_decisions_and_the_usual_slot_is_ignored() -> None:
    """2025-05-29: T_W = 11:00 CT. A 09:30-slot move does nothing; the 10:59 -> 11:14 move
    trades."""
    day = Day(MOVED, closes={hm(9, 29): 0, hm(9, 44): -HALF_PCT})
    assert fills(run(eiafade.make_mcl(), [day])) == []
    day = Day(MOVED, closes={hm(9, 29): 0, hm(9, 44): -HALF_PCT, hm(10, 59): 0,
                             hm(11, 14): HALF_PCT})
    assert fills(run(eiafade.make_mcl(), [day])) == trade(MOVED, "11:15", "13:29", side="sell")


def test_eiafade_a_dropped_release_and_a_non_table_date_are_not_traded() -> None:
    days = [_fade_day(DROPPED, hm(11, 0), -HALF_PCT), _fade_day(date(2025, 5, 28), move=-HALF_PCT)]
    res = run(eiafade.make_mcl(), days)
    assert intents(res) == [] and fills(res) == []


def test_eiafade_the_1600_ct_row_and_the_1313_bound() -> None:
    """T_W + 15 <= 13:13 CT: the 16:00 CT row (2025-12-29, also dropped in section 11) is out;
    a 12:58 row is in, a 12:59 row out (injected tables)."""
    rows = (("2025-12-29", "16:00", 0, False), ("2025-06-04", "12:58", 2, False),
            ("2025-06-05", "12:59", 3, False))
    assert eiafade.release_minutes(rows) == {WED: hm(12, 58)}
    assert set(eiafade.release_minutes(tables.WPSR).values()) == {
        hm(9, 30), hm(10, 0), hm(11, 0), hm(12, 0)}
    member = eiafade.EiaFade("MCL", wpsr=(("2025-12-29", "16:00", 0, False),))
    day = Day(date(2025, 12, 29), closes={hm(15, 59): 0, hm(16, 14): -HALF_PCT},
              end=hm(16, 20))
    res = run(member, [day])
    assert intents(res) == [] and fills(res) == []


@pytest.mark.parametrize("minute", [hm(9, 29), hm(9, 44)], ids=["t_w-1", "t_w+14"])
def test_eiafade_two_instrument_ids_on_the_signal_bars_is_no_trade(minute: int) -> None:
    res = run(eiafade.make_mcl(), [_fade_day(move=-HALF_PCT, ids={minute: 778})])
    assert intents(res) == [] and fills(res) == []


@pytest.mark.parametrize("minute", [hm(9, 29), hm(9, 44)], ids=["t_w-1", "t_w+14"])
def test_eiafade_a_missing_signal_or_entry_bar_is_no_trade(minute: int) -> None:
    res = run(eiafade.make_mcl(), [_fade_day(move=-HALF_PCT, skip=frozenset({minute}))])
    assert intents(res) == [] and fills(res) == []


def test_eiafade_an_early_halt_date_is_not_traded() -> None:
    res = run(eiafade.make_mcl(), [_fade_day(move=-HALF_PCT, halt="13:30")])
    assert intents(res) == [] and fills(res) == []


def test_eiafade_a_missing_1328_bar_sends_the_exit_on_the_next_present_bar() -> None:
    res = run(eiafade.make_mcl(), [_fade_day(move=-HALF_PCT, skip=frozenset({hm(13, 28)}))])
    assert intents(res) == decided(WED, "09:44", "13:29")
    assert fills(res) == trade(WED, "09:45", "13:30", side="buy")


def test_eiafade_the_release_guard_leaves_the_t_w_plus_15_entry() -> None:
    res = run(eiafade.make_mcl(), [_fade_day(move=-HALF_PCT)],
              releases=release_at("MCL", WED, 9, 30))
    assert fills(res) == trade(WED, "09:45", "13:29", side="buy")
    assert res.counters.get("fill_guard_deferral", 0) == 0
    res = run(eiafade.make_mcl(), [_fade_day(move=-HALF_PCT)],
              releases=release_at("MCL", WED, 9, 45))  # synthetic: D9.5a defers the entry
    assert fills(res) == trade(WED, "09:47", "13:29", side="buy")


def test_eiafade_a_position_open_at_a_synthetic_f_is_closed_by_the_engine() -> None:
    res = run(eiafade.make_mcl(), [_fade_day(move=HALF_PCT, flatten_from=hm(12, 0))])
    assert fills(res) == trade(WED, "09:45", "12:01", side="sell", exit_reason="forced_flatten")
    assert intents(res) == decided(WED, "09:44")


def test_eiafade_d9_7_engine_exit_no_duplicate_exit_no_reentry() -> None:
    member = eiafade.make_mcl()
    days = [_fade_day(move=-HALF_PCT, closes={hm(11, 0): -HALF_PCT - 40})]
    res = run(member, days, rules=forced_limit_rules(member, days, [(WED, hm(10, 30))]))
    assert fills(res) == trade(WED, "09:45", "10:31", side="buy", exit_reason="price_limit_exit")
    assert intents(res) == decided(WED, "09:44")


# --------------------------------------------------------------------- eiamom ----
def _mom_day(day: date = WED, r3: int = 4, **kw: object) -> Day:
    closes = {hm(9, 29): 0, hm(9, 59): r3, **kw.pop("closes", {})}  # type: ignore[dict-item]
    return Day(day, closes=closes, **kw)  # type: ignore[arg-type]


def test_eiamom_event_set_of_the_frozen_tables() -> None:
    events = eiamom.event_dates(tables.WPSR, tables.NYSE_NOT_FULL)
    standard = {date.fromisoformat(r[0]) for r in tables.WPSR if r[3]}
    assert events == standard - {date(2019, 7, 3), date(2024, 7, 3)}  # NYSE early closes
    assert WED in events and MOVED not in events and DROPPED not in events


def test_eiamom_r3_positive_buys_at_1430_and_exits_at_1459() -> None:
    res = run(eiamom.make_mcl(), [_mom_day(r3=4)])
    assert intents(res) == decided(WED, "14:29", "14:58")
    assert fills(res) == trade(WED, "14:30", "14:59", side="buy")
    assert [f.qty for f in res.events(Fill)] == [4, 4]


def test_eiamom_r3_negative_sells() -> None:
    res = run(eiamom.make_mcl(), [_mom_day(r3=-1)])
    assert fills(res) == trade(WED, "14:30", "14:59", side="sell")


def test_eiamom_r3_zero_is_no_trade() -> None:
    res = run(eiamom.make_mcl(), [_mom_day(r3=0, closes={hm(9, 45): 9})])
    assert intents(res) == [] and fills(res) == []


def test_eiamom_a_date_in_nyse_not_full_is_not_traded() -> None:
    """The same standard Wednesday trades, and does not once it is listed in NYSE_NOT_FULL
    (injected: the frozen table's standard Wednesdays in it, 2019-07-03 and 2024-07-03, also
    carry Topstep's 11:30 close-by)."""
    assert run(eiamom.EiaMom("MCL", nyse_not_full=()), [_mom_day()]).events(Fill)
    res = run(eiamom.EiaMom("MCL", nyse_not_full=(WED.isoformat(),)), [_mom_day()])
    assert intents(res) == [] and fills(res) == []


def test_eiamom_a_non_standard_wpsr_thursday_and_a_dropped_week_are_not_traded() -> None:
    days = [_mom_day(date(2025, 5, 28)), _mom_day(MOVED), _mom_day(DROPPED)]
    res = run(eiamom.make_mcl(), days)
    assert intents(res) == [] and fills(res) == []


def test_eiamom_an_early_halt_date_is_not_traded() -> None:
    res = run(eiamom.make_mcl(), [_mom_day(halt="13:30")])
    assert intents(res) == [] and fills(res) == []


@pytest.mark.parametrize("minute", [hm(9, 29), hm(9, 59), hm(14, 29)],
                         ids=["0929", "0959", "1429"])
def test_eiamom_the_guard_over_the_0929_0959_and_1429_bars(minute: int) -> None:
    res = run(eiamom.make_mcl(), [_mom_day(ids={minute: 778})])
    assert intents(res) == [] and fills(res) == []


@pytest.mark.parametrize("minute", [hm(9, 29), hm(9, 59), hm(14, 29)],
                         ids=["0929", "0959", "1429"])
def test_eiamom_a_missing_signal_or_entry_bar_is_no_trade(minute: int) -> None:
    res = run(eiamom.make_mcl(), [_mom_day(skip=frozenset({minute}))])
    assert intents(res) == [] and fills(res) == []


def test_eiamom_a_missing_1458_bar_sends_the_exit_on_the_next_present_bar() -> None:
    res = run(eiamom.make_mcl(), [_mom_day(skip=frozenset({hm(14, 58)}))])
    assert intents(res) == decided(WED, "14:29", "14:59")
    assert fills(res) == trade(WED, "14:30", "15:00", side="buy")


def test_eiamom_a_release_at_the_entry_fill_is_deferred_by_d9_5a() -> None:
    res = run(eiamom.make_mcl(), [_mom_day()], releases=release_at("MCL", WED, 9, 30))
    assert fills(res) == trade(WED, "14:30", "14:59", side="buy")  # the 09:30 WPSR: untouched
    res = run(eiamom.make_mcl(), [_mom_day()], releases=release_at("MCL", WED, 14, 30))
    assert fills(res) == trade(WED, "14:32", "14:59", side="buy")  # synthetic 14:30 release


def test_eiamom_a_position_open_at_a_synthetic_f_is_closed_by_the_engine() -> None:
    res = run(eiamom.make_mcl(), [_mom_day(flatten_from=hm(14, 45))])
    assert fills(res) == trade(WED, "14:30", "14:46", side="buy", exit_reason="forced_flatten")
    assert intents(res) == decided(WED, "14:29")


def test_eiamom_d9_7_engine_exit_no_duplicate_exit_no_reentry() -> None:
    member = eiamom.make_mcl()
    days = [_mom_day()]
    res = run(member, days, rules=forced_limit_rules(member, days, [(WED, hm(14, 40))]))
    assert fills(res) == trade(WED, "14:30", "14:41", side="buy", exit_reason="price_limit_exit")
    assert intents(res) == decided(WED, "14:29")


def test_eiamom_and_eiafade_trade_consecutive_weeks_independently() -> None:
    wed2 = WED + timedelta(days=7)
    days = [_mom_day(WED, 4), Day(THU), _mom_day(wed2, -3)]
    assert fills(run(eiamom.make_mcl(), days)) == (trade(WED, "14:30", "14:59")
                                                   + trade(wed2, "14:30", "14:59", "sell"))
    days = [_fade_day(WED, move=-HALF_PCT), Day(THU), _fade_day(wed2, move=HALF_PCT)]
    assert fills(run(eiafade.make_mcl(), days)) == (trade(WED, "09:45", "13:29")
                                                    + trade(wed2, "09:45", "13:29", "sell"))
