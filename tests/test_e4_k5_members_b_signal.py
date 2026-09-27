"""Stage E.4 Part 2 K5 members of MemberCoder-B, part 2: K5-pmfix-01 and K5-fomc-01
(reports/stage_e4b_member_specs.md sections 5 and 6), both built on
strategy.members.k5._event_common.SignedMoveEvent. The synthetic kit is
tests/test_e4_k5_members_b.py's. Synthetic bars only; no bar file, no runner, no freeze.
"""

from __future__ import annotations

from datetime import date
from types import ModuleType
from typing import Any

import pytest

from screening.stage_e_engine import Fill
from screening.stage_e_rules import release_calendar_from_dict
from strategy.members.k5 import _releases as tables
from strategy.members.k5 import fomc, pmfix
from tests.test_e4_k5_members_b import (
    CALENDAR_JSON,
    CALENDAR_SHA256,
    FIVE_HOUR,
    FOMC_DAY,
    FOMC_FIVE_HOUR,
    NEXT,
    NORMAL,
    PM_NOT_HELD,
    ROOT,
    UK_BANK_HOLIDAY,
    Day,
    _json,
    account_of,
    bar_at,
    decided,
    fills,
    forced_limit_rules,
    hm,
    intents,
    ns_at,
    release_at,
    run,
    trade,
    view_of,
)

EARLY_HALT_FOMC = date(2025, 12, 10)  # an FOMC date used with a synthetic halt label


def pm_day(day: date = NORMAL, start: int = 0, end: int = 3, t_p: int = hm(9, 0),
           **kw: Any) -> Day:
    """A PM auction day with the T_P - 1 close at ``start`` and the T_P + 1 close at ``end``
    ticks (every other bar at 0)."""
    closes = {t_p - 1: start, t_p + 1: end, **kw.pop("closes", {})}
    return Day(day, closes=closes, **kw)


def fomc_day(day: date = FOMC_DAY, start: int = 0, end: int = 4, **kw: Any) -> Day:
    """An FOMC day with the 12:59 close at ``start`` and the 13:04 close at ``end`` ticks."""
    closes = {hm(12, 59): start, hm(13, 4): end, **kw.pop("closes", {})}
    return Day(day, closes=closes, **kw)


# ---------------------------------------------------------------------- pmfix ----
def test_pmfix_table_rows_used_by_the_tests() -> None:
    pm = dict(tables.GOLD_PM_AUCTIONS)
    assert (pm[NORMAL.isoformat()], pm[NEXT.isoformat()]) == ("09:00", "09:00")
    assert pm[FIVE_HOUR.isoformat()] == "10:00"
    assert PM_NOT_HELD.isoformat() not in pm and "2025-12-24" not in pm  # section 11
    assert UK_BANK_HOLIDAY.isoformat() not in pm
    assert pmfix.schedule((("2025-06-04", "09:00"), ("2025-10-28", "10:00"))) == {
        NORMAL: (hm(8, 59), hm(9, 1), hm(9, 11)), FIVE_HOUR: (hm(9, 59), hm(10, 1), hm(10, 11))}


def test_pmfix_normal_week_s_positive_buys_at_0902_and_exits_at_0912() -> None:
    res = run(pmfix.make_mgc(), [pm_day(start=0, end=3)])
    assert intents(res) == decided(NORMAL, "09:01", "09:11")
    assert fills(res) == trade(NORMAL, "09:02", "09:12", side="buy")
    assert [f.qty for f in res.events(Fill)] == [1, 1]  # q_c MGC = 1


def test_pmfix_s_negative_sells() -> None:
    res = run(pmfix.make_mgc(), [pm_day(start=2, end=-1)])
    assert intents(res) == decided(NORMAL, "09:01", "09:11")
    assert fills(res) == trade(NORMAL, "09:02", "09:12", side="sell")


def test_pmfix_s_zero_is_no_trade_whatever_the_bars_between_do() -> None:
    res = run(pmfix.make_mgc(), [pm_day(start=4, end=4, closes={hm(9, 0): 9})])
    assert intents(res) == [] and fills(res) == []


def test_pmfix_only_the_t_p_minus_1_and_t_p_plus_1_closes_make_s() -> None:
    """A move from 08:58 to 09:02 that is flat between 08:59 and 09:01 is no signal; a move
    between 08:59 and 09:01 whatever the 09:00 bar does is one."""
    flat = pm_day(start=0, end=0, closes={hm(8, 58): -7, hm(9, 0): 5, hm(9, 2): 7})
    assert fills(run(pmfix.make_mgc(), [flat])) == []
    up = pm_day(start=0, end=1, closes={hm(9, 0): -9})
    assert fills(run(pmfix.make_mgc(), [up])) == trade(NORMAL, "09:02", "09:12", side="buy")


def test_pmfix_five_hour_week_moves_every_decision_to_t_p_1000() -> None:
    day = pm_day(FIVE_HOUR, start=0, end=-2, t_p=hm(10, 0), closes={hm(8, 59): 0, hm(9, 1): 5})
    res = run(pmfix.make_mgc(), [day])
    assert intents(res) == decided(FIVE_HOUR, "10:01", "10:11")  # nothing at 09:01
    assert fills(res) == trade(FIVE_HOUR, "10:02", "10:12", side="sell")


@pytest.mark.parametrize("minute", [hm(8, 59), hm(9, 1)], ids=["T_P-1", "T_P+1"])
def test_pmfix_two_signal_bars_on_two_instrument_ids_is_no_trade(minute: int) -> None:
    res = run(pmfix.make_mgc(), [pm_day(start=0, end=3, ids={minute: 778})])
    assert intents(res) == [] and fills(res) == []


@pytest.mark.parametrize("minute", [hm(8, 59), hm(9, 1)], ids=["T_P-1", "T_P+1"])
def test_pmfix_a_missing_signal_or_entry_bar_is_no_trade(minute: int) -> None:
    res = run(pmfix.make_mgc(), [pm_day(start=0, end=3, skip=frozenset({minute}))])
    assert intents(res) == [] and fills(res) == []


def test_pmfix_a_missing_t_p_plus_11_bar_sends_the_exit_on_the_next_present_bar() -> None:
    res = run(pmfix.make_mgc(), [pm_day(start=0, end=3, skip=frozenset({hm(9, 11)}))])
    assert intents(res) == decided(NORMAL, "09:01", "09:12")
    assert fills(res) == trade(NORMAL, "09:02", "09:13", side="buy")


def test_pmfix_a_pm_no_auction_day_and_a_uk_bank_holiday_are_not_traded() -> None:
    res = run(pmfix.make_mgc(), [pm_day(PM_NOT_HELD), pm_day(UK_BANK_HOLIDAY)])
    assert intents(res) == [] and fills(res) == []


def test_pmfix_a_date_not_in_the_table_is_not_traded_and_a_moved_row_moves_it() -> None:
    without = tuple(row for row in tables.GOLD_PM_AUCTIONS if row[0] != NORMAL.isoformat())
    res = run(pmfix.PmFix(ROOT, pm_auctions=without), [pm_day()])
    assert intents(res) == [] and fills(res) == []
    moved = ((NORMAL.isoformat(), "10:00"),)
    day = pm_day(start=0, end=3, t_p=hm(10, 0))
    res = run(pmfix.PmFix(ROOT, pm_auctions=moved), [day])
    assert fills(res) == trade(NORMAL, "10:02", "10:12", side="buy")


def test_pmfix_an_early_halt_date_is_not_traded() -> None:
    res = run(pmfix.make_mgc(), [pm_day(halt="12:00")])
    assert intents(res) == [] and fills(res) == []


def test_pmfix_a_release_at_the_entry_fill_is_deferred_by_d9_5a() -> None:
    res = run(pmfix.make_mgc(), [pm_day()], releases=release_at(NORMAL, 9, 2))
    assert intents(res) == decided(NORMAL, "09:01", "09:11")
    assert fills(res) == trade(NORMAL, "09:04", "09:12", side="buy")
    assert res.counters["fill_guard_deferral"] == 2


def test_pmfix_a_release_at_the_auction_start_leaves_both_fills_alone() -> None:
    """A row at T_P (09:00) would guard [09:00, 09:02): the entry fills at 09:02, the first
    minute after it; the frozen calendar has no LBMA row (K5-L-04) and no MGC row near 09:00."""
    res = run(pmfix.make_mgc(), [pm_day()], releases=release_at(NORMAL, 9, 0))
    assert fills(res) == trade(NORMAL, "09:02", "09:12", side="buy")
    assert res.counters.get("fill_guard_deferral", 0) == 0
    frozen = release_calendar_from_dict(_json(CALENDAR_JSON), CALENDAR_SHA256, "frozen")
    res = run(pmfix.make_mgc(), [pm_day(), pm_day(FIVE_HOUR, t_p=hm(10, 0))], releases=frozen)
    assert fills(res) == (trade(NORMAL, "09:02", "09:12", side="buy")
                          + trade(FIVE_HOUR, "10:02", "10:12", side="buy"))
    assert res.counters.get("fill_guard_deferral", 0) == 0


def test_pmfix_a_position_open_at_a_synthetic_f_is_closed_by_the_engine() -> None:
    res = run(pmfix.make_mgc(), [pm_day(flatten_from=hm(9, 6))])
    assert fills(res) == trade(NORMAL, "09:02", "09:07", side="buy",
                               exit_reason="forced_flatten")
    assert intents(res) == decided(NORMAL, "09:01")


def test_pmfix_d9_7_engine_exit_no_duplicate_exit_no_reentry() -> None:
    member = pmfix.make_mgc()
    days = [pm_day(start=0, end=-3)]
    res = run(member, days, rules=forced_limit_rules(member, days, [(NORMAL, hm(9, 6))]))
    assert fills(res) == trade(NORMAL, "09:02", "09:07", side="sell",
                               exit_reason="price_limit_exit")
    assert intents(res) == decided(NORMAL, "09:01")


def test_pmfix_one_entry_per_date_and_each_date_uses_its_own_bars() -> None:
    """The T_P - 1 capture of one date is never carried to the next (no forward fill)."""
    days = [pm_day(start=0, end=3), pm_day(NEXT, start=0, end=3, skip=frozenset({hm(8, 59)}))]
    res = run(pmfix.make_mgc(), days)
    assert fills(res) == trade(NORMAL, "09:02", "09:12", side="buy")
    days = [pm_day(start=0, end=3), pm_day(NEXT, start=5, end=1)]
    res = run(pmfix.make_mgc(), days)
    assert fills(res) == (trade(NORMAL, "09:02", "09:12", side="buy")
                          + trade(NEXT, "09:02", "09:12", side="sell"))


# ----------------------------------------------------------------------- fomc ----
def test_fomc_table_rows_used_by_the_tests() -> None:
    assert FOMC_DAY.isoformat() in tables.FOMC_STATEMENT_DATES
    assert FOMC_FIVE_HOUR.isoformat() in tables.FOMC_STATEMENT_DATES
    assert EARLY_HALT_FOMC.isoformat() in tables.FOMC_STATEMENT_DATES
    assert NORMAL.isoformat() not in tables.FOMC_STATEMENT_DATES
    assert fomc.schedule(("2025-06-18",)) == {FOMC_DAY: (hm(12, 59), hm(13, 4), hm(13, 14))}


def test_fomc_s_positive_buys_at_1305_and_exits_at_1315() -> None:
    res = run(fomc.make_mgc(), [fomc_day(start=0, end=4)])
    assert intents(res) == decided(FOMC_DAY, "13:04", "13:14")
    assert fills(res) == trade(FOMC_DAY, "13:05", "13:15", side="buy")
    assert [f.qty for f in res.events(Fill)] == [1, 1]  # q_c MGC = 1


def test_fomc_s_negative_sells() -> None:
    res = run(fomc.make_mgc(), [fomc_day(start=3, end=-2)])
    assert fills(res) == trade(FOMC_DAY, "13:05", "13:15", side="sell")


def test_fomc_s_zero_is_no_trade() -> None:
    res = run(fomc.make_mgc(), [fomc_day(start=6, end=6, closes={hm(13, 0): -8})])
    assert intents(res) == [] and fills(res) == []


def test_fomc_a_non_fomc_date_is_not_traded() -> None:
    res = run(fomc.make_mgc(), [fomc_day(NORMAL), fomc_day(NEXT)])
    assert intents(res) == [] and fills(res) == []
    res = run(fomc.Fomc(ROOT, statement_dates=(NORMAL.isoformat(),)), [fomc_day(NORMAL)])
    assert fills(res) == trade(NORMAL, "13:05", "13:15", side="buy")  # the table decides


def test_fomc_in_a_5_hour_week_keeps_the_1300_ct_clock() -> None:
    res = run(fomc.make_mgc(), [fomc_day(FOMC_FIVE_HOUR, start=0, end=-1)])
    assert fills(res) == trade(FOMC_FIVE_HOUR, "13:05", "13:15", side="sell")


@pytest.mark.parametrize("minute", [hm(12, 59), hm(13, 4)], ids=["12:59", "13:04"])
def test_fomc_two_signal_bars_on_two_instrument_ids_is_no_trade(minute: int) -> None:
    res = run(fomc.make_mgc(), [fomc_day(ids={minute: 778})])
    assert intents(res) == [] and fills(res) == []


@pytest.mark.parametrize("minute", [hm(12, 59), hm(13, 4)], ids=["12:59", "13:04"])
def test_fomc_a_missing_signal_or_entry_bar_is_no_trade(minute: int) -> None:
    res = run(fomc.make_mgc(), [fomc_day(skip=frozenset({minute}))])
    assert intents(res) == [] and fills(res) == []


def test_fomc_a_missing_1314_bar_sends_the_exit_on_the_next_present_bar() -> None:
    res = run(fomc.make_mgc(), [fomc_day(skip=frozenset({hm(13, 14), hm(13, 15)}))])
    assert intents(res) == decided(FOMC_DAY, "13:04", "13:16")
    assert fills(res) == trade(FOMC_DAY, "13:05", "13:17", side="buy")


def test_fomc_an_early_halt_date_is_not_traded() -> None:
    res = run(fomc.make_mgc(), [fomc_day(EARLY_HALT_FOMC, halt="12:00")])
    assert intents(res) == [] and fills(res) == []


def test_fomc_the_frozen_calendars_guard_at_1300_does_not_touch_these_fills() -> None:
    """The frozen calendar's FOMC row guards [13:00, 13:02) (D9.5a) and opens D8's event window
    [13:00, 13:30): the fills at 13:05 and 13:15 are outside the guard (not deferred) and inside
    the event window (the engine's event-window cost, not a member matter)."""
    frozen = release_calendar_from_dict(_json(CALENDAR_JSON), CALENDAR_SHA256, "frozen")
    for minute in (hm(13, 0), hm(13, 1)):
        assert frozen.in_fill_guard(ROOT, ns_at(FOMC_DAY, minute))
    for minute in (hm(13, 5), hm(13, 15)):
        assert not frozen.in_fill_guard(ROOT, ns_at(FOMC_DAY, minute))
        assert frozen.in_event_window(ROOT, ns_at(FOMC_DAY, minute))
    res = run(fomc.make_mgc(), [fomc_day()], releases=frozen)
    assert intents(res) == decided(FOMC_DAY, "13:04", "13:14")
    assert fills(res) == trade(FOMC_DAY, "13:05", "13:15", side="buy")
    assert res.counters.get("fill_guard_deferral", 0) == 0


def test_fomc_a_release_at_the_entry_fill_is_deferred_by_d9_5a() -> None:
    res = run(fomc.make_mgc(), [fomc_day()], releases=release_at(FOMC_DAY, 13, 5))
    assert fills(res) == trade(FOMC_DAY, "13:07", "13:15", side="buy")
    assert res.counters["fill_guard_deferral"] == 2


def test_fomc_a_position_open_at_a_synthetic_f_is_closed_by_the_engine() -> None:
    res = run(fomc.make_mgc(), [fomc_day(flatten_from=hm(13, 10))])
    assert fills(res) == trade(FOMC_DAY, "13:05", "13:11", side="buy",
                               exit_reason="forced_flatten")
    assert intents(res) == decided(FOMC_DAY, "13:04")


def test_fomc_d9_7_engine_exit_no_duplicate_exit_no_reentry() -> None:
    member = fomc.make_mgc()
    days = [fomc_day(start=0, end=-4)]
    res = run(member, days, rules=forced_limit_rules(member, days, [(FOMC_DAY, hm(13, 8))]))
    assert fills(res) == trade(FOMC_DAY, "13:05", "13:09", side="sell",
                               exit_reason="price_limit_exit")
    assert intents(res) == decided(FOMC_DAY, "13:04")


# ------------------------------------------------------------ direct calls ----
@pytest.mark.parametrize("module", [pmfix, fomc], ids=lambda m: m.MEMBER_ID)
def test_direct_calls_no_entry_while_pending_and_one_chance_per_date(module: ModuleType) -> None:
    day, start, entry = ((NORMAL, hm(8, 59), hm(9, 1)) if module is pmfix
                         else (FOMC_DAY, hm(12, 59), hm(13, 4)))
    member = module.make_mgc()
    bar0, bar1 = bar_at(day, start, 0), bar_at(day, entry, 2)
    assert member.on_minute(view_of(bar0.ts_event_ns, bar0), account_of()) == ()
    assert member.on_minute(view_of(bar1.ts_event_ns, bar1), account_of(pending=1)) == ()
    assert member.on_minute(view_of(bar1.ts_event_ns, bar1), account_of()) == ()  # spent
    fresh = module.make_mgc()
    fresh.on_minute(view_of(bar0.ts_event_ns, bar0), account_of())
    out = fresh.on_minute(view_of(bar1.ts_event_ns, bar1), account_of())
    assert [(i.side, i.quantity) for i in out] == [("buy", 1)]
