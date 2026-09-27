"""Stage E.4 Part 3 K3 members of MemberCoder-B, part 4: K3-tkypre-01 and K3-tkypost-01
(reports/stage_e4c_member_specs.md sections 8 and 9, K3-L-04, K3-L-08; catalog C 726-855).

Synthetic bars through the real Stage E engine, with the kit of tests/test_e4_k3_members_b.py.
Both members trade the CT evening of d-1 (inside trade date d, C3); "d-1 hh:mm" in the expected
fills marks that evening. The early-halt test reads trade date d (FX_FULL_SESSIONS), never the
evening bar's early_halt_ct (K3-L-04).
"""

from __future__ import annotations

from datetime import date
from typing import Any

import pytest

from screening.stage_e_engine import Fill
from strategy.members.k3 import _calendar as cal_tables
from strategy.members.k3 import _clocks as clocks
from strategy.members.k3 import tkypost, tkypre
from tests.test_e4_k3_members_b import (
    Day,
    account_of,
    bar_at,
    decided,
    eve,
    fills,
    forced_limit_rules,
    hm,
    intents,
    release_at,
    run,
    trade,
    view_of,
)

TKY = {"start": eve(17, 0), "end": hm(1, 30)}  # the evening of d-1 and the early hours of d
# K3-tkypre-01 event dates (gotobi or Tokyo month-end, full FX sessions)
GOTOBI_CDT = date(2025, 6, 5)  # Thursday: T_T 19:55 CDT on 06-04
GOTOBI_CST = date(2026, 1, 15)  # Thursday: T_T 18:55 CST on 01-14
GOTOBI_DST_SUNDAY = date(2025, 3, 10)  # Monday: d-1 is Sunday 03-09, the US spring-forward day
MONTH_END_CST = date(2026, 2, 27)  # Friday, the last Tokyo business day of February (not a gotobi)
MONTH_END_DEC = date(2025, 12, 30)  # Tuesday: 12-31 is closed in Tokyo, so 12-30 ends December
NOT_GOTOBI = date(2025, 6, 4)
GOTOBI_TOKYO_HOLIDAY = date(2025, 5, 5)  # Children's Day, a full FX session
HALTED_MONTH_END = date(2025, 11, 28)  # EC-CAL early halt 13:45; also Tokyo's November month-end
AFTER_HALT = date(2019, 7, 5)  # gotobi, a full session; d-1 = 2019-07-04 has an early halt 12:00
# K3-tkypost-01 dates
POST_CDT = date(2025, 6, 4)  # Wednesday: T_T 19:55 CDT on 06-03
POST_CST = date(2026, 1, 14)  # Wednesday: T_T 18:55 CST on 01-13
POST_FALL_BACK = date(2025, 11, 4)  # C9's known answer: T_T 18:55 CST on 11-03
TOKYO_HOLIDAY = date(2025, 11, 3)  # Culture Day, a full FX session
YEAR_START = date(2026, 1, 2)  # 2 January: Tokyo closed (EC-JP), a full FX session


def day(d: date, **kw: Any) -> Day:
    return Day(d, **{**TKY, **kw})


def test_the_table_rows_the_tky_tests_use() -> None:
    t_t, full = dict(clocks.T_T), set(cal_tables.FX_FULL_SESSIONS)
    events, business = set(cal_tables.GOTOBI_OR_TOKYO_MONTH_END), set(
        cal_tables.TOKYO_BUSINESS_DAYS)
    for d, hhmm in ((GOTOBI_CDT, "19:55"), (GOTOBI_CST, "18:55"), (GOTOBI_DST_SUNDAY, "19:55"),
                    (MONTH_END_CST, "18:55"), (MONTH_END_DEC, "18:55"), (AFTER_HALT, "19:55")):
        assert d.isoformat() in events and d.isoformat() in full and t_t[d.isoformat()] == hhmm
    for d in (NOT_GOTOBI, GOTOBI_TOKYO_HOLIDAY, YEAR_START, date(2025, 12, 31)):
        assert d.isoformat() in full and d.isoformat() not in events
    assert HALTED_MONTH_END.isoformat() in events and HALTED_MONTH_END.isoformat() not in full
    for d, hhmm in ((POST_CDT, "19:55"), (POST_CST, "18:55"), (POST_FALL_BACK, "18:55")):
        assert d.isoformat() in business and d.isoformat() in full and t_t[d.isoformat()] == hhmm
    for d in (TOKYO_HOLIDAY, YEAR_START, GOTOBI_TOKYO_HOLIDAY):
        assert d.isoformat() in full and d.isoformat() not in business


# ------------------------------------------------------------------- tkypre ----
def test_tkypre_gotobi_cdt_sells_at_1730_and_exits_at_the_1955_fix() -> None:
    res = run(tkypre.make_6j(), [day(GOTOBI_CDT)])
    assert intents(res) == decided(date(2025, 6, 4), "17:29", "19:54")
    assert fills(res) == trade(GOTOBI_CDT, "d-1 17:30", "d-1 19:55", side="sell")
    assert [f.qty for f in res.events(Fill)] == [1, 1]  # q_c 1


def test_tkypre_gotobi_cst_exits_at_the_1855_fix() -> None:
    res = run(tkypre.make_6j(), [day(GOTOBI_CST)])
    assert intents(res) == decided(date(2026, 1, 14), "17:29", "18:54")
    assert fills(res) == trade(GOTOBI_CST, "d-1 17:30", "d-1 18:55", side="sell")


def test_tkypre_the_us_spring_forward_sunday_uses_cdt() -> None:
    res = run(tkypre.make_6j(), [day(GOTOBI_DST_SUNDAY)])
    assert intents(res) == decided(date(2025, 3, 9), "17:29", "19:54")
    assert fills(res) == trade(GOTOBI_DST_SUNDAY, "d-1 17:30", "d-1 19:55", side="sell")


@pytest.mark.parametrize("d,fix", [(MONTH_END_CST, "18:55"), (MONTH_END_DEC, "18:55"),
                                   (date(2025, 10, 31), "19:55")])
def test_tkypre_a_tokyo_month_end_is_traded(d: date, fix: str) -> None:
    res = run(tkypre.make_6j(), [day(d)])
    assert fills(res) == trade(d, "d-1 17:30", f"d-1 {fix}", side="sell")


@pytest.mark.parametrize("d", [NOT_GOTOBI, GOTOBI_TOKYO_HOLIDAY, YEAR_START,
                               date(2025, 12, 31), date(2025, 9, 15)])
def test_tkypre_non_event_dates_are_not_traded(d: date) -> None:
    """A non-gotobi date; Tokyo holidays on day 5 and 15; 2 January and 31 December (EC-JP's
    year-end rule: no shift of a nominal date)."""
    res = run(tkypre.make_6j(), [day(d)])
    assert intents(res) == [] and fills(res) == []


def test_tkypre_the_early_halt_test_is_trade_date_ds_not_the_evening_bars() -> None:
    """K3-L-04: d = 2025-11-28 (halted) is not traded although its evening bars (CT 11-27)
    carry no early_halt_ct; d = 2019-07-05 (full) is traded although its evening bars (CT
    2019-07-04) carry early_halt_ct 12:00."""
    res = run(tkypre.make_6j(), [day(HALTED_MONTH_END, halt="13:45")])
    assert intents(res) == [] and fills(res) == []
    res = run(tkypre.make_6j(), [day(AFTER_HALT, evening_halt="12:00")])
    assert fills(res) == trade(AFTER_HALT, "d-1 17:30", "d-1 19:55", side="sell")


def test_tkypre_a_missing_1729_bar_is_no_trade() -> None:
    res = run(tkypre.make_6j(), [day(GOTOBI_CDT, skip=frozenset({eve(17, 29)}))])
    assert intents(res) == [] and fills(res) == []  # no late entry on the 17:30 bar


def test_tkypre_a_missing_exit_bar_sends_the_exit_on_the_next_present_bar() -> None:
    res = run(tkypre.make_6j(), [day(GOTOBI_CDT, skip=frozenset({eve(19, 54)}))])
    assert intents(res) == decided(date(2025, 6, 4), "17:29", "19:55")
    assert fills(res) == trade(GOTOBI_CDT, "d-1 17:30", "d-1 19:56", side="sell")


def test_tkypre_d9_5a_defers_fills_in_the_two_minutes_after_a_release() -> None:
    res = run(tkypre.make_6j(), [day(GOTOBI_CDT)],
              releases=release_at("6J", GOTOBI_CDT, eve(17, 30)))
    assert fills(res) == trade(GOTOBI_CDT, "d-1 17:32", "d-1 19:55", side="sell")
    res = run(tkypre.make_6j(), [day(GOTOBI_CDT)],
              releases=release_at("6J", GOTOBI_CDT, eve(19, 55)))
    assert fills(res) == trade(GOTOBI_CDT, "d-1 17:30", "d-1 19:57", side="sell")


def test_tkypre_a_position_open_at_a_synthetic_f_is_closed_by_the_engine() -> None:
    res = run(tkypre.make_6j(), [day(GOTOBI_CDT, flatten_from=eve(18, 0))])
    assert fills(res) == trade(GOTOBI_CDT, "d-1 17:30", "d-1 18:01", side="sell",
                               exit_reason="forced_flatten")
    assert intents(res) == decided(date(2025, 6, 4), "17:29")


def test_tkypre_d9_7_engine_exit_no_duplicate_exit_no_reentry() -> None:
    member = tkypre.make_6j()
    days = [day(GOTOBI_CDT)]
    res = run(member, days, rules=forced_limit_rules(member, days, [(GOTOBI_CDT, eve(18, 30))]))
    assert fills(res) == trade(GOTOBI_CDT, "d-1 17:30", "d-1 18:31", side="sell",
                               exit_reason="price_limit_exit")
    assert intents(res) == decided(date(2025, 6, 4), "17:29")


def test_tkypre_a_moved_or_dropped_row_moves_or_drops_the_trade() -> None:
    moved = tuple((d, "18:55" if d == GOTOBI_CDT.isoformat() else t) for d, t in clocks.T_T)
    res = run(tkypre.TkyPre("6J", t_t=moved), [day(GOTOBI_CDT)])
    assert fills(res) == trade(GOTOBI_CDT, "d-1 17:30", "d-1 18:55", side="sell")
    dropped = tuple(d for d in cal_tables.GOTOBI_OR_TOKYO_MONTH_END if d != GOTOBI_CDT.isoformat())
    res = run(tkypre.TkyPre("6J", event_days=dropped), [day(GOTOBI_CDT)])
    assert intents(res) == [] and fills(res) == []


def test_tkypre_consecutive_dates_trade_only_the_event_dates() -> None:
    days = [day(NOT_GOTOBI), day(GOTOBI_CDT), day(date(2025, 6, 6))]
    res = run(tkypre.make_6j(), days)
    assert fills(res) == trade(GOTOBI_CDT, "d-1 17:30", "d-1 19:55", side="sell")


# ------------------------------------------------------------------- tkypost ----
def test_tkypost_cdt_buys_after_the_1955_fix_and_exits_at_0100() -> None:
    res = run(tkypost.make_6j(), [day(POST_CDT)])
    assert intents(res) == [(date(2025, 6, 3), "19:55", True, None),
                            (POST_CDT, "00:59", True, None)]
    assert fills(res) == trade(POST_CDT, "d-1 19:56", "01:00", side="buy")
    assert [f.qty for f in res.events(Fill)] == [1, 1]  # q_c 1


@pytest.mark.parametrize("d,prev", [(POST_CST, date(2026, 1, 13)),
                                    (POST_FALL_BACK, date(2025, 11, 3))])
def test_tkypost_cst_buys_after_the_1855_fix(d: date, prev: date) -> None:
    res = run(tkypost.make_6j(), [day(d)])
    assert intents(res) == [(prev, "18:55", True, None), (d, "00:59", True, None)]
    assert fills(res) == trade(d, "d-1 18:56", "01:00", side="buy")


def test_tkypost_the_us_spring_forward_sunday_uses_cdt() -> None:
    res = run(tkypost.make_6j(), [day(GOTOBI_DST_SUNDAY)])
    assert fills(res) == trade(GOTOBI_DST_SUNDAY, "d-1 19:56", "01:00", side="buy")


@pytest.mark.parametrize("d", [TOKYO_HOLIDAY, YEAR_START, GOTOBI_TOKYO_HOLIDAY])
def test_tkypost_a_non_tokyo_business_day_is_not_traded(d: date) -> None:
    res = run(tkypost.make_6j(), [day(d)])
    assert intents(res) == [] and fills(res) == []


def test_tkypost_the_early_halt_test_is_trade_date_ds_not_the_evening_bars() -> None:
    """K3-L-04, as for tkypre: 2025-11-28 and 2025-07-04 (halted d) are not traded;
    2019-07-05 (full d, halted d-1) is."""
    res = run(tkypost.make_6j(), [day(HALTED_MONTH_END, halt="13:45"),
                                  day(date(2025, 7, 4), halt="12:00")])
    assert intents(res) == [] and fills(res) == []
    res = run(tkypost.make_6j(), [day(AFTER_HALT, evening_halt="12:00")])
    assert fills(res) == trade(AFTER_HALT, "d-1 19:56", "01:00", side="buy")


def test_tkypost_a_missing_t_t_bar_is_no_trade() -> None:
    res = run(tkypost.make_6j(), [day(POST_CDT, skip=frozenset({eve(19, 55)}))])
    assert intents(res) == [] and fills(res) == []  # no late entry on the 19:56 bar


def test_tkypost_a_missing_0059_bar_sends_the_exit_on_the_next_present_bar() -> None:
    res = run(tkypost.make_6j(), [day(POST_CDT, skip=frozenset({hm(0, 59)}))])
    assert intents(res)[-1] == (POST_CDT, "01:00", True, None)
    assert fills(res) == trade(POST_CDT, "d-1 19:56", "01:01", side="buy")


def test_tkypost_d9_5a_defers_the_entry_fill() -> None:
    res = run(tkypost.make_6j(), [day(POST_CDT)],
              releases=release_at("6J", POST_CDT, eve(19, 56)))
    assert fills(res) == trade(POST_CDT, "d-1 19:58", "01:00", side="buy")


def test_tkypost_a_position_open_at_a_synthetic_f_is_closed_by_the_engine() -> None:
    res = run(tkypost.make_6j(), [day(POST_CDT, flatten_from=hm(0, 30))])
    assert fills(res) == trade(POST_CDT, "d-1 19:56", "00:31", side="buy",
                               exit_reason="forced_flatten")
    assert intents(res) == [(date(2025, 6, 3), "19:55", True, None)]


def test_tkypost_d9_7_engine_exit_no_duplicate_exit_no_reentry() -> None:
    member = tkypost.make_6j()
    days = [day(POST_CDT), day(date(2025, 6, 5))]
    res = run(member, days, rules=forced_limit_rules(member, days, [(POST_CDT, hm(0, 10))]))
    assert fills(res) == (trade(POST_CDT, "d-1 19:56", "00:11", side="buy",
                                exit_reason="price_limit_exit")
                          + trade(date(2025, 6, 5), "d-1 19:56", "01:00", side="buy"))


def test_tkypost_a_moved_or_dropped_row_moves_or_drops_the_trade() -> None:
    moved = tuple((d, "18:55" if d == POST_CDT.isoformat() else t) for d, t in clocks.T_T)
    res = run(tkypost.TkyPost("6J", t_t=moved), [day(POST_CDT)])
    assert fills(res) == trade(POST_CDT, "d-1 18:56", "01:00", side="buy")
    dropped = tuple(d for d in cal_tables.TOKYO_BUSINESS_DAYS if d != POST_CDT.isoformat())
    res = run(tkypost.TkyPost("6J", business_days=dropped), [day(POST_CDT)])
    assert intents(res) == [] and fills(res) == []


def test_tkypost_direct_calls_no_entry_while_pending_or_holding() -> None:
    member = tkypost.make_6j()
    entry = bar_at("6J", POST_CDT, eve(19, 55))
    assert member.on_minute(view_of("6J", entry.ts_event_ns, entry), account_of("6J",
                                                                             pending=1)) == ()
    fresh = tkypost.make_6j()
    out = fresh.on_minute(view_of("6J", entry.ts_event_ns, entry), account_of("6J"))
    assert [(i.side, i.quantity) for i in out] == [("buy", 1)]
    assert fresh.on_minute(view_of("6J", entry.ts_event_ns, entry), account_of("6J")) == ()
    before = bar_at("6J", POST_CDT, hm(0, 58))
    assert fresh.on_minute(view_of("6J", before.ts_event_ns, before), account_of("6J", 1)) == ()
    exit_bar = bar_at("6J", POST_CDT, hm(0, 59))
    out = fresh.on_minute(view_of("6J", exit_bar.ts_event_ns, exit_bar), account_of("6J", 1))
    assert [(i.side, i.quantity) for i in out] == [("sell", 1)]
