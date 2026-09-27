"""Stage E.4 Part 3 K3 members of MemberCoder-B, part 2: K3-ldnrev-01 and K3-ldnmom-01
(reports/stage_e4c_member_specs.md sections 4 and 5; catalog C 380-554; R-05).

Synthetic bars through the real Stage E engine, with the kit of tests/test_e4_k3_members_b.py.
Dates are real rows of the literal tables (pinned in part 1): a standard week (T_L 10:00 CT), the
C9 mismatch weeks (T_L 11:00 CT), a CST date, an early-halt month-end, E&W bank holidays.
"""

from __future__ import annotations

from datetime import date
from typing import Any

import pytest

from screening.stage_e_engine import Fill
from strategy.members.k3 import _calendar as cal_tables
from strategy.members.k3 import _clocks as clocks
from strategy.members.k3 import ldnmom, ldnrev
from tests.test_e4_k3_members_b import (
    Day,
    account_of,
    bar_at,
    decided,
    fills,
    flat,
    forced_limit_rules,
    hm,
    intents,
    make,
    release_at,
    run,
    trade,
    view_of,
)

# K3-ldnrev-01 event dates (MONTH_ENDS rows in FX_FULL_SESSIONS, not E&W bank holidays)
ME_STD = date(2025, 6, 30)  # Monday, CDT and BST: T_L 10:00 CT
ME_MISMATCH = date(2025, 10, 31)  # Friday of the autumn mismatch week: T_L 11:00 CT
ME_CST = date(2026, 1, 30)  # Friday, CST and GMT: T_L 10:00 CT
ME_HALTED = date(2025, 11, 28)  # ME(2025-11): EC-CAL early halt 13:45 (K3-L-06)
ME_EW = date(2020, 8, 31)  # ME(2020-08): the England-and-Wales Summer bank holiday
# K3-ldnmom-01 dates
STD = date(2025, 6, 3)  # Tuesday: T_L 10:00 CT
MISMATCH = date(2025, 10, 28)  # Tuesday of the autumn mismatch week: T_L 11:00 CT
SPRING_MISMATCH = date(2026, 3, 10)  # Tuesday of the spring mismatch week: T_L 11:00 CT
EW_HOLIDAY = date(2025, 8, 25)  # Summer bank holiday (England and Wales), a full FX session
LDN = {"start": hm(9, 0), "end": hm(12, 0)}  # the London-fix segment of CT date d


def day(d: date, **kw: Any) -> Day:
    return Day(d, **{**LDN, **kw})


def test_the_table_rows_the_ldn_tests_use() -> None:
    t_l, me = dict(clocks.T_L), {m: d for m, d in cal_tables.MONTH_ENDS}
    full, ew = set(cal_tables.FX_FULL_SESSIONS), set(cal_tables.EW_BANK_HOLIDAYS)
    assert (me["2025-06"], me["2025-10"], me["2026-01"]) == tuple(
        d.isoformat() for d in (ME_STD, ME_MISMATCH, ME_CST))
    assert (t_l["2025-06-30"], t_l["2025-10-31"], t_l["2026-01-30"]) == ("10:00", "11:00",
                                                                         "10:00")
    assert me["2025-11"] == "2025-11-28" and "2025-11-28" not in full  # halted ME
    assert me["2020-08"] == "2020-08-31" and "2020-08-31" in ew and "2020-08-31" in full
    assert (t_l["2025-06-03"], t_l["2025-10-28"], t_l["2026-03-10"]) == ("10:00", "11:00",
                                                                         "11:00")
    assert "2025-08-25" in ew and "2025-08-25" in full
    for d in (ME_STD, ME_MISMATCH, ME_CST, STD, MISMATCH, SPRING_MISMATCH):
        assert d.isoformat() in full and d.isoformat() not in ew


# ------------------------------------------------------------------- ldnrev ----
def rev_day(d: date, t_l: int, m: int, **kw: Any) -> Day:
    """Closes: 0 at T_L - 11, ``m`` at T_L - 1 (M = m)."""
    paths = {t_l - 11: flat(0), t_l - 1: flat(m), **kw.pop("paths", {})}
    return day(d, paths=paths, **kw)


@pytest.mark.parametrize("root", ["6E", "6J", "6S"])
def test_ldnrev_a_rise_into_the_fix_sells_at_1005_and_exits_at_1020(root: str) -> None:
    res = run(make(ldnrev, root), [rev_day(ME_STD, hm(10, 0), 3)])
    assert intents(res) == decided(ME_STD, "10:04", "10:19")
    assert fills(res) == trade(ME_STD, "10:05", "10:20", side="sell")  # M > 0: SELL
    assert [f.qty for f in res.events(Fill)] == [1, 1]  # q_c 1


@pytest.mark.parametrize("root", ["6E", "6J", "6S"])
def test_ldnrev_a_fall_into_the_fix_buys(root: str) -> None:
    res = run(make(ldnrev, root), [rev_day(ME_STD, hm(10, 0), -2)])
    assert fills(res) == trade(ME_STD, "10:05", "10:20", side="buy")  # M < 0: BUY


def test_ldnrev_signal_is_t_l_minus_11_to_t_l_minus_1_not_t_l_minus_16() -> None:
    """R-05: a T_L - 16 close that would flip the sign is not read; nor are the bars between."""
    paths = {hm(9, 44): flat(10), hm(9, 50): flat(-9), hm(9, 58): flat(-9), hm(10, 0): flat(-9)}
    res = run(ldnrev.make_6e(), [rev_day(ME_STD, hm(10, 0), 3, paths=paths)])
    assert fills(res) == trade(ME_STD, "10:05", "10:20", side="sell")
    paths = {hm(9, 44): flat(-10)}
    res = run(ldnrev.make_6e(), [rev_day(ME_STD, hm(10, 0), -3, paths=paths)])
    assert fills(res) == trade(ME_STD, "10:05", "10:20", side="buy")
    # N-5: T_L - 11, not T_L - 10: M = 3 - 0 > 0 sells; a T_L - 10 read (3 - 10 < 0) would buy
    paths = {hm(9, 50): flat(10)}
    res = run(ldnrev.make_6e(), [rev_day(ME_STD, hm(10, 0), 3, paths=paths)])
    assert fills(res) == trade(ME_STD, "10:05", "10:20", side="sell")


def test_ldnrev_signal_reads_closes_not_opens() -> None:
    """S-1: close to close is +5 (M > 0 sells); open to open is -9 (an open reading would buy)."""
    paths = {hm(9, 49): (5, 5, -2, -2), hm(9, 59): (-4, 3, -4, 3)}
    res = run(ldnrev.make_6j(), [day(ME_STD, paths=paths)])
    assert fills(res) == trade(ME_STD, "10:05", "10:20", side="sell")


def test_ldnrev_zero_signal_is_no_trade() -> None:
    paths = {hm(9, 49): flat(4), hm(9, 55): flat(-7), hm(9, 59): flat(4)}
    res = run(ldnrev.make_6e(), [day(ME_STD, paths=paths)])
    assert intents(res) == [] and fills(res) == []


def test_ldnrev_mismatch_week_moves_every_decision_by_an_hour() -> None:
    res = run(ldnrev.make_6e(), [rev_day(ME_MISMATCH, hm(11, 0), 2)])
    assert intents(res) == decided(ME_MISMATCH, "11:04", "11:19")
    assert fills(res) == trade(ME_MISMATCH, "11:05", "11:20", side="sell")
    # the standard-week bars carry no signal on this date: a 10:00-clock move is ignored
    res = run(ldnrev.make_6e(), [rev_day(ME_MISMATCH, hm(10, 0), 2)])
    assert intents(res) == [] and fills(res) == []  # M(11:00 clock) = 0


def test_ldnrev_cst_date_keeps_the_1005_clock() -> None:
    res = run(ldnrev.make_6s(), [rev_day(ME_CST, hm(10, 0), -1)])
    assert fills(res) == trade(ME_CST, "10:05", "10:20", side="buy")


def test_ldnrev_early_halt_month_end_is_not_traded_and_not_shifted() -> None:
    """K3-L-06: ME(2025-11) = 11-28 is halted; neither 11-26 nor 11-27 replaces it."""
    days = [rev_day(date(2025, 11, 26), hm(10, 0), 3), rev_day(date(2025, 11, 27), hm(10, 0), 3),
            rev_day(ME_HALTED, hm(10, 0), 3, halt="13:45")]
    res = run(ldnrev.make_6e(), days)
    assert intents(res) == [] and fills(res) == []


def test_ldnrev_ew_bank_holiday_month_end_is_not_traded_and_not_shifted() -> None:
    days = [rev_day(date(2020, 8, 28), hm(10, 0), 3), rev_day(ME_EW, hm(10, 0), 3)]
    res = run(ldnrev.make_6j(), days)
    assert intents(res) == [] and fills(res) == []


def test_ldnrev_a_non_month_end_date_is_not_traded() -> None:
    res = run(ldnrev.make_6e(), [rev_day(date(2025, 6, 27), hm(10, 0), 3), rev_day(ME_STD,
                                                                                  hm(10, 0), 3)])
    assert fills(res) == trade(ME_STD, "10:05", "10:20", side="sell")


@pytest.mark.parametrize("missing", [hm(9, 49), hm(9, 59), hm(10, 4)])
def test_ldnrev_a_missing_signal_or_entry_bar_is_no_trade(missing: int) -> None:
    res = run(ldnrev.make_6e(), [rev_day(ME_STD, hm(10, 0), 3, skip=frozenset({missing}))])
    assert intents(res) == [] and fills(res) == []  # no late entry on the 10:05 bar


def test_ldnrev_a_missing_exit_bar_sends_the_exit_on_the_next_present_bar() -> None:
    res = run(ldnrev.make_6e(), [rev_day(ME_STD, hm(10, 0), 3, skip=frozenset({hm(10, 19)}))])
    assert intents(res) == decided(ME_STD, "10:04", "10:20")
    assert fills(res) == trade(ME_STD, "10:05", "10:21", side="sell")


@pytest.mark.parametrize("other", [hm(9, 49), hm(9, 59), hm(10, 4)])
def test_ldnrev_guard_one_instrument_id_across_the_three_bars(other: int) -> None:
    res = run(ldnrev.make_6e(), [rev_day(ME_STD, hm(10, 0), 3, ids={other: 888})])
    assert intents(res) == [] and fills(res) == []


def test_ldnrev_exit_is_sent_whatever_the_exit_bars_instrument_id() -> None:
    """K3-L-03: exit bars are not guarded (direct call; the engine forbids a splice inside a
    position)."""
    member = ldnrev.make_6e()
    entry = bar_at("6E", ME_STD, hm(10, 4))
    member.on_minute(view_of("6E", entry.ts_event_ns, entry), account_of("6E"))
    exit_bar = bar_at("6E", ME_STD, hm(10, 19), instrument_id=999)
    out = member.on_minute(view_of("6E", exit_bar.ts_event_ns, exit_bar), account_of("6E", -1))
    assert [(i.side, i.quantity) for i in out] == [("buy", 1)]


def test_ldnrev_d9_5a_defers_a_fill_in_the_two_minutes_after_a_release() -> None:
    res = run(ldnrev.make_6e(), [rev_day(ME_STD, hm(10, 0), 3)],
              releases=release_at("6E", ME_STD, hm(10, 5)))
    assert fills(res) == trade(ME_STD, "10:07", "10:20", side="sell")
    res = run(ldnrev.make_6e(), [rev_day(ME_STD, hm(10, 0), 3)],
              releases=release_at("6E", ME_STD, hm(10, 0)))  # [10:00, 10:02): before the fill
    assert fills(res) == trade(ME_STD, "10:05", "10:20", side="sell")
    res = run(ldnrev.make_6e(), [rev_day(ME_STD, hm(10, 0), 3)],
              releases=release_at("6E", ME_STD, hm(10, 20)))
    assert fills(res) == trade(ME_STD, "10:05", "10:22", side="sell")


def test_ldnrev_a_position_open_at_a_synthetic_f_is_closed_by_the_engine() -> None:
    res = run(ldnrev.make_6e(), [rev_day(ME_STD, hm(10, 0), 3, flatten_from=hm(10, 12))])
    assert fills(res) == trade(ME_STD, "10:05", "10:13", side="sell",
                               exit_reason="forced_flatten")
    assert intents(res) == decided(ME_STD, "10:04")  # no exit of its own, no re-entry


def test_ldnrev_d9_7_engine_exit_no_duplicate_exit_no_reentry() -> None:
    member = ldnrev.make_6j()
    days = [rev_day(ME_STD, hm(10, 0), -3)]
    res = run(member, days, rules=forced_limit_rules(member, days, [(ME_STD, hm(10, 9))]))
    assert fills(res) == trade(ME_STD, "10:05", "10:10", side="buy",
                               exit_reason="price_limit_exit")
    assert intents(res) == decided(ME_STD, "10:04")


def test_ldnrev_a_moved_or_dropped_row_moves_or_drops_the_trade() -> None:
    moved = tuple((d, "11:00" if d == ME_STD.isoformat() else t) for d, t in clocks.T_L)
    res = run(ldnrev.LdnRev("6E", t_l=moved), [rev_day(ME_STD, hm(11, 0), 3)])
    assert fills(res) == trade(ME_STD, "11:05", "11:20", side="sell")
    dropped = tuple(r for r in cal_tables.MONTH_ENDS if r[1] != ME_STD.isoformat())
    res = run(ldnrev.LdnRev("6E", month_ends=dropped), [rev_day(ME_STD, hm(10, 0), 3)])
    assert intents(res) == [] and fills(res) == []


def test_ldnrev_consecutive_month_ends_trade_once_each() -> None:
    days = [rev_day(ME_STD, hm(10, 0), 3), rev_day(date(2025, 7, 31), hm(10, 0), -3)]
    res = run(ldnrev.make_6e(), days)
    assert fills(res) == (trade(ME_STD, "10:05", "10:20", side="sell")
                          + trade(date(2025, 7, 31), "10:05", "10:20", side="buy"))


# ------------------------------------------------------------------- ldnmom ----
def mom_day(d: date, t_l: int, s: int, **kw: Any) -> Day:
    """Open 0 at T_L - 15, close ``s`` at T_L - 13 (S = s)."""
    paths = {t_l - 15: flat(0), t_l - 13: flat(s), **kw.pop("paths", {})}
    return day(d, paths=paths, **kw)


@pytest.mark.parametrize("root", ["6E", "6J"])
def test_ldnmom_an_up_trend_buys_at_0948_and_exits_at_1005(root: str) -> None:
    res = run(make(ldnmom, root), [mom_day(STD, hm(10, 0), 2)])
    assert intents(res) == decided(STD, "09:47", "10:04")
    assert fills(res) == trade(STD, "09:48", "10:05", side="buy")  # S > 0: BUY
    assert [f.qty for f in res.events(Fill)] == [1, 1]  # q_c 1


@pytest.mark.parametrize("root", ["6E", "6J"])
def test_ldnmom_a_down_trend_sells(root: str) -> None:
    res = run(make(ldnmom, root), [mom_day(STD, hm(10, 0), -4)])
    assert fills(res) == trade(STD, "09:48", "10:05", side="sell")


def test_ldnmom_signal_is_the_open_of_t_l_minus_15_to_the_close_of_t_l_minus_13() -> None:
    """Open, not close, of 09:45; close, not open, of 09:47; 09:46 and 09:44 are not read."""
    paths = {hm(9, 44): flat(-20), hm(9, 45): (-3, 6, -3, 5), hm(9, 46): flat(30),
             hm(9, 47): (8, 8, 1, 1)}
    res = run(ldnmom.make_6e(), [day(STD, paths=paths)])
    assert fills(res) == trade(STD, "09:48", "10:05", side="buy")  # S = 1 - (-3) = 4
    # S-2: S = close(09:47) - open(09:45) = -6 - (-3) < 0 sells; an open reading of 09:47
    # (8 - (-3) > 0) would buy
    paths = {hm(9, 45): (-3, 6, -3, 5), hm(9, 47): (8, 8, -6, -6)}
    res = run(ldnmom.make_6e(), [day(STD, paths=paths)])
    assert fills(res) == trade(STD, "09:48", "10:05", side="sell")


def test_ldnmom_zero_signal_is_no_trade() -> None:
    paths = {hm(9, 45): (2, 2, 0, 0), hm(9, 46): flat(9), hm(9, 47): (0, 3, 0, 2)}
    res = run(ldnmom.make_6j(), [day(STD, paths=paths)])
    assert intents(res) == [] and fills(res) == []


@pytest.mark.parametrize("d", [MISMATCH, SPRING_MISMATCH])
def test_ldnmom_mismatch_weeks_move_the_minutes_to_1048_and_1105(d: date) -> None:
    res = run(ldnmom.make_6e(), [mom_day(d, hm(11, 0), 1)])
    assert intents(res) == decided(d, "10:47", "11:04")
    assert fills(res) == trade(d, "10:48", "11:05", side="buy")


def test_ldnmom_an_ew_bank_holiday_is_not_traded() -> None:
    res = run(ldnmom.make_6e(), [mom_day(EW_HOLIDAY, hm(10, 0), 3)])
    assert intents(res) == [] and fills(res) == []


def test_ldnmom_early_halt_and_early_f_dates_are_not_traded() -> None:
    days = [mom_day(date(2025, 7, 4), hm(10, 0), 3, halt="12:00"),
            mom_day(date(2025, 11, 27), hm(10, 0), 3)]  # K3-L-11: engine F 11:30, no halt
    res = run(ldnmom.make_6e(), days)
    assert intents(res) == [] and fills(res) == []


@pytest.mark.parametrize("missing", [hm(9, 45), hm(9, 47)])
def test_ldnmom_a_missing_signal_or_entry_bar_is_no_trade(missing: int) -> None:
    res = run(ldnmom.make_6e(), [mom_day(STD, hm(10, 0), 3, skip=frozenset({missing}))])
    assert intents(res) == [] and fills(res) == []


def test_ldnmom_a_missing_exit_bar_sends_the_exit_on_the_next_present_bar() -> None:
    res = run(ldnmom.make_6e(), [mom_day(STD, hm(10, 0), 3,
                                         skip=frozenset({hm(10, 4), hm(10, 5)}))])
    assert intents(res) == decided(STD, "09:47", "10:06")
    assert fills(res) == trade(STD, "09:48", "10:07", side="buy")


def test_ldnmom_guard_one_instrument_id_on_the_two_signal_bars() -> None:
    res = run(ldnmom.make_6e(), [mom_day(STD, hm(10, 0), 3, ids={hm(9, 45): 888})])
    assert intents(res) == [] and fills(res) == []
    res = run(ldnmom.make_6e(), [mom_day(STD, hm(10, 0), 3, ids={hm(9, 46): 888})])
    assert fills(res) == trade(STD, "09:48", "10:05", side="buy")  # 09:46 is not read


def test_ldnmom_d9_5a_defers_the_entry_fill() -> None:
    res = run(ldnmom.make_6e(), [mom_day(STD, hm(10, 0), 3)],
              releases=release_at("6E", STD, hm(9, 48)))
    assert fills(res) == trade(STD, "09:50", "10:05", side="buy")


def test_ldnmom_a_position_open_at_a_synthetic_f_is_closed_by_the_engine() -> None:
    res = run(ldnmom.make_6e(), [mom_day(STD, hm(10, 0), -3, flatten_from=hm(9, 55))])
    assert fills(res) == trade(STD, "09:48", "09:56", side="sell",
                               exit_reason="forced_flatten")
    assert intents(res) == decided(STD, "09:47")


def test_ldnmom_d9_7_engine_exit_no_duplicate_exit_no_reentry() -> None:
    member = ldnmom.make_6e()
    days = [mom_day(STD, hm(10, 0), 3), mom_day(date(2025, 6, 4), hm(10, 0), -3)]
    res = run(member, days, rules=forced_limit_rules(member, days, [(STD, hm(9, 52))]))
    assert fills(res) == (trade(STD, "09:48", "09:53", exit_reason="price_limit_exit")
                          + trade(date(2025, 6, 4), "09:48", "10:05", side="sell"))
    assert intents(res) == decided(STD, "09:47") + decided(date(2025, 6, 4), "09:47", "10:04")


def test_ldnmom_a_dropped_or_moved_row_drops_or_moves_the_trade() -> None:
    full = tuple(d for d in cal_tables.FX_FULL_SESSIONS if d != STD.isoformat())
    res = run(ldnmom.LdnMom("6E", full_sessions=full), [mom_day(STD, hm(10, 0), 3)])
    assert intents(res) == [] and fills(res) == []
    moved = tuple((d, "11:00" if d == STD.isoformat() else t) for d, t in clocks.T_L)
    res = run(ldnmom.LdnMom("6E", t_l=moved), [mom_day(STD, hm(11, 0), 3)])
    assert fills(res) == trade(STD, "10:48", "11:05", side="buy")
