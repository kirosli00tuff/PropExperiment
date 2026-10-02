"""Stage E.9 K8-wkndbtc-01 of MemberCoder-B (reports/stage_e9_member_specs.md section 3; readings
K8-L-02, K8-L-03, K8-L-09, K8-L-12; S0.4, S0.6, S0.7, S0.9, S0.10, S0.12).

Synthetic bars only (the kit of tests/test_k8_members_oilcad.py); direct calls minute by minute
and the real Stage E engine on synthetic two-leg frames. No bar file is read.

A week for the Monday trade date d: MBT on Friday d - 3 at 14:57..15:00 (trade_date d - 3) and on
Sunday d - 1 at 17:57..18:01 (trade_date d); MNQ on Friday 14:00..15:00 (trade_date d - 3; the
price-limit reference of the engine), Sunday 17:00..18:30 and Monday 14:50..15:05 (trade_date
d). P_F (the MBT 14:59 Friday close) is B + p_f and P_S (the MBT 17:59 Sunday close) is
B + p_s ticks; every other MBT bar is a DECOY priced so that reading it in place of P_F or P_S
flips the side (or turns no trade into a trade). After the 24/7 change (Mondays from
2026-06-01) the week also holds weekend MBT bars booked to Monday: Friday 16:59 and 17:59,
Saturday 14:59 and 17:59, Sunday 14:59 and 16:59 (decoys too).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from datetime import date, time, timedelta
from typing import Any

import pytest

from screening.stage_e_engine import EngineResult, Fill, IntentRecord
from screening.stage_e_freeze import check_member_source
from screening.stage_e_frozen import load_frozen_tables
from strategy.members.k8 import wkndbtc
from strategy.members.k8._calendar import CRYPTO_FULL_SESSIONS, EQUITY_FULL_SESSIONS, WKNDBTC_DATES
from strategy.members.k8._releases import in_guard
from strategy.stage_e.interface import (
    LegSpec,
    MemberAccountView,
    StageEMember,
    TradingInterval,
)
from tests.test_k8_members_oilcad import (
    REPO,
    RootBar,
    account,
    drive,
    engine,
    fills,
    hm,
    intent_roots,
    mk_bar,
    ns_at,
    refusals,
    rules_of,
    runner_rules,
)

B_MBT = 20000  # 100,000 USD in 5.00 ticks
B_MNQ = 80000  # 20,000.00 in 0.25 ticks
CHANGE = date(2026, 6, 1)  # the first Monday whose weekend MBT bars carry Monday's trade date
MON = date(2025, 6, 2)  # Friday 2025-05-30, Sunday 2025-06-01
MON_BEFORE = date(2026, 5, 18)
MON_AFTER = date(2026, 6, 8)
HOLIDAY_MON = date(2025, 5, 26)  # Memorial Day: not a full session (EC-CAL)
AFTER_GOOD_FRIDAY = date(2025, 4, 21)  # Good Friday 2025-04-18
AFTER_HALT_FRIDAY = date(2025, 12, 1)  # Friday 2025-11-28 early halt


def mk() -> wkndbtc.WeekendBitcoin:
    return wkndbtc.make_mnq()


def sgn(x: int) -> int:
    return 1 if x >= 0 else -1


def week(monday: date, p_f: int = 0, p_s: int = 10, *, mbt_skip: Iterable[tuple[int, int]] = (),
         mnq_skip: Iterable[tuple[int, int]] = (), ids: Mapping[tuple[int, int], int] | None = None,
         sunday_label: date | None = None) -> list[RootBar]:
    """The week of ``monday`` (module doc). Skips and id overrides are keyed by (day offset from
    d, CT minute); ``sunday_label`` relabels the MBT Sunday 17:59 bar's trade_date."""
    ids, skip_b, skip_n = ids or {}, set(mbt_skip), set(mnq_skip)
    g = p_s - p_f
    as_pf, as_ps = p_s + 7 * sgn(g), p_f - 7 * sgn(g)  # decoy prices
    fri, sat, sun = (monday + timedelta(days=k) for k in (-3, -2, -1))
    mbt: list[tuple[int, int, int, date]] = [  # (offset, minute, ticks, trade date)
        (-3, hm(14, 57), as_pf, fri), (-3, hm(14, 58), as_pf, fri), (-3, hm(14, 59), p_f, fri),
        (-3, hm(15, 0), as_pf, fri),
        (-1, hm(17, 57), as_ps, monday), (-1, hm(17, 58), as_ps, monday),
        (-1, hm(17, 59), p_s, sunday_label or monday), (-1, hm(18, 0), as_ps, monday),
        (-1, hm(18, 1), as_ps, monday)]
    if monday >= CHANGE:  # weekend MBT bars booked to Monday
        mbt += [(-3, hm(16, 59), as_ps, monday), (-3, hm(17, 59), as_ps, monday),
                (-2, hm(14, 59), as_pf, monday), (-2, hm(17, 59), as_ps, monday),
                (-1, hm(14, 59), as_pf, monday), (-1, hm(16, 59), as_ps, monday)]
    out = [mk_bar("MBT", monday + timedelta(days=k), m, B_MBT + x, trade_day=td,
                  iid=ids.get((k, m), 777))
           for k, m, x, td in mbt if (k, m) not in skip_b]
    mnq = ([(-3, m, fri) for m in range(hm(14, 0), hm(15, 1))]
           + [(-1, m, monday) for m in range(hm(17, 0), hm(18, 31))]
           + [(0, m, monday) for m in range(hm(14, 50), hm(15, 6))])
    out += [mk_bar("MNQ", monday + timedelta(days=k), m, B_MNQ, trade_day=td)
            for k, m, td in mnq if (k, m) not in skip_n]
    assert sat.weekday() == 5 and sun.weekday() == 6
    return out


Entry = tuple[date, str, str]  # (CT date of the view, CT hh:mm, side)


def entries(bars: Sequence[RootBar], acct: Any = None) -> list[Entry]:
    out = drive(mk(), sorted(bars, key=lambda rb: rb[1].ts_event_ns), acct)
    assert all(i[2] == "MNQ" and i[4] == 1 for i in out), out
    return [(i[0], i[1], i[3]) for i in out]


def sunday_of(monday: date) -> date:
    return monday - timedelta(days=1)


# ------------------------------------------------------------------- calendar facts ----
def test_scenario_dates_are_calendar_facts() -> None:
    w = set(WKNDBTC_DATES)
    for d in (MON, MON_BEFORE, MON_AFTER, date(2025, 6, 16)):
        assert d.weekday() == 0 and d in w and d - timedelta(days=3) in w
    assert HOLIDAY_MON not in w and HOLIDAY_MON - timedelta(days=3) in w
    assert AFTER_GOOD_FRIDAY in w and date(2025, 4, 18) not in w
    assert AFTER_HALT_FRIDAY in w and date(2025, 11, 28) not in w
    assert date(2025, 6, 5) in w and date(2025, 6, 2) in w  # a Thursday whose d - 3 is Monday
    assert set(WKNDBTC_DATES) == EQUITY_FULL_SESSIONS & CRYPTO_FULL_SESSIONS


def test_research_window_mondays_and_no_mnq_guard_at_sunday_18_00() -> None:
    """54 eligible Mondays in the research window (spec section 7); no MNQ guard instant meets
    a Sunday 18:00 fill or the Monday 14:59 exit fill (S0.10)."""
    mondays = [d for d in WKNDBTC_DATES if date(2025, 4, 1) <= d <= date(2026, 6, 19)
               and wkndbtc.is_trade_monday(d)]
    assert len(mondays) == 54
    assert sum(d < CHANGE for d in mondays) == 51
    for d in mondays:
        assert not in_guard("MNQ", ns_at(sunday_of(d), hm(18, 0)))
        assert not in_guard("MNQ", ns_at(d, hm(14, 59)))


# --------------------------------------------------------------- declaration and freeze ----
def test_factory_name_legs_size_and_protocol() -> None:
    m = mk()
    assert isinstance(m, StageEMember)
    assert m.name == "K8-wkndbtc-01 MNQ"
    assert m.legs == (LegSpec("MNQ", True), LegSpec("MBT", False))
    assert load_frozen_tables().vehicles["MNQ"].q_c == 1 == m._q
    with pytest.raises(ValueError):
        wkndbtc.WeekendBitcoin("MBT")


def test_trading_windows_are_s0_12() -> None:
    assert mk().trading_windows == {
        "MNQ": (TradingInterval(time(17, 59), time(18, 1), -1, -1),
                TradingInterval(time(14, 58), time(15, 0))),
        "MBT": (TradingInterval(time(17, 59), time(18, 0), -1, -1),
                TradingInterval(time(14, 59), time(15, 0))),
    }


def test_member_file_passes_the_freeze_static_check() -> None:
    rel = "strategy/members/k8/wkndbtc.py"
    assert check_member_source(rel, (REPO / rel).read_text(), "K8") == []


# ---------------------------------------------------------- the clock points and sign ----
def test_buy_on_the_sunday_17_59_view_when_p_s_above_p_f() -> None:
    assert entries(week(MON, 0, 10)) == [(sunday_of(MON), "17:59", "buy")]


def test_sell_when_p_s_below_p_f() -> None:
    assert entries(week(MON, 10, 0)) == [(sunday_of(MON), "17:59", "sell")]


def test_g_zero_is_no_trade() -> None:
    assert entries(week(MON, 4, 4)) == []


def test_one_tick_moves_trade() -> None:
    assert entries(week(MON, 0, 1)) == [(sunday_of(MON), "17:59", "buy")]
    assert entries(week(MON, 1, 0)) == [(sunday_of(MON), "17:59", "sell")]


def test_side_of_is_the_sign_of_the_tick_difference() -> None:
    assert wkndbtc.side_of(1) == "buy" and wkndbtc.side_of(-1) == "sell"
    assert wkndbtc.side_of(0) is None


def test_friday_14_59_missing_14_58_and_15_00_never_used() -> None:
    assert entries(week(MON, 0, 10, mbt_skip=[(-3, hm(14, 59))])) == []


def test_sunday_17_59_mbt_missing_17_58_never_used_and_the_late_18_00_bar_neither() -> None:
    assert entries(week(MON, 0, 10, mbt_skip=[(-1, hm(17, 59))])) == []


def test_missing_mnq_entry_bar_is_no_trade_on_d() -> None:
    assert entries(week(MON, 0, 10, mnq_skip=[(-1, hm(17, 59))])) == []


def test_mbt_sunday_bar_must_carry_trade_date_d() -> None:
    assert entries(week(MON, 0, 10, sunday_label=sunday_of(MON))) == []


def test_one_instrument_id_across_p_f_and_p_s() -> None:
    assert entries(week(MON, 0, 10, ids={(-1, hm(17, 59)): 778})) == []
    assert entries(week(MON, 0, 10, ids={(-3, hm(14, 59)): 776})) == []


def test_p_f_comes_from_ct_date_d_minus_3_only_never_a_stale_friday() -> None:
    """The Friday 2025-06-06 14:59 MBT bar exists; the Friday 2025-06-13 one is missing: the
    Monday 2025-06-16 does not trade on the stale Friday."""
    d = date(2025, 6, 16)
    stale = mk_bar("MBT", date(2025, 6, 6), hm(14, 59), B_MBT)
    assert entries([stale, *week(d, 0, 10, mbt_skip=[(-3, hm(14, 59))])]) == []
    assert entries([stale, *week(d, 0, 10)]) == [(sunday_of(d), "17:59", "buy")]  # control


def test_a_non_monday_never_trades() -> None:
    """Thursday 2025-06-05: d - 3 = Monday 2025-06-02 is in WKNDBTC_DATES; the MBT 14:59 bar of
    that Monday and the MBT and MNQ 17:59 bars of Wednesday (trade_date Thursday) exist with a
    move: no trade."""
    d, dm3, dm1 = date(2025, 6, 5), date(2025, 6, 2), date(2025, 6, 4)
    bars = [mk_bar("MBT", dm3, hm(14, 59), B_MBT),
            mk_bar("MBT", dm1, hm(17, 59), B_MBT + 10, trade_day=d),
            *(mk_bar("MNQ", dm1, m, B_MNQ, trade_day=d) for m in range(hm(17, 55), hm(18, 5)))]
    assert entries(bars) == []
    assert not wkndbtc.is_trade_monday(d) and not wkndbtc.is_trade_monday(date(2025, 6, 3))


# ---------------------------------------------------------------------- exclusions ----
@pytest.mark.parametrize("monday", [HOLIDAY_MON, AFTER_GOOD_FRIDAY, AFTER_HALT_FRIDAY])
def test_excluded_mondays_do_not_trade(monday: date) -> None:
    assert entries(week(monday, 0, 10)) == []


def test_is_trade_monday_needs_both_d_and_d_minus_3() -> None:
    assert wkndbtc.is_trade_monday(MON)
    assert not wkndbtc.is_trade_monday(HOLIDAY_MON)
    assert not wkndbtc.is_trade_monday(AFTER_GOOD_FRIDAY)
    assert not wkndbtc.is_trade_monday(AFTER_HALT_FRIDAY)


# ----------------------------------------------------------------------- both regimes ----
@pytest.mark.parametrize("monday", [MON_BEFORE, MON_AFTER])
def test_both_regimes_read_the_same_two_bars(monday: date) -> None:
    assert entries(week(monday, 0, 10)) == [(sunday_of(monday), "17:59", "buy")]
    assert entries(week(monday, 10, 0)) == [(sunday_of(monday), "17:59", "sell")]


def test_after_the_change_saturday_and_sunday_bars_never_stand_in() -> None:
    """MON_AFTER: the Friday 14:59 bar missing, Saturday and Sunday 14:59 bars (trade_date d)
    present: no trade; the Sunday 17:59 bar missing, Saturday and Friday 17:59 bars present:
    no trade."""
    assert entries(week(MON_AFTER, 0, 10, mbt_skip=[(-3, hm(14, 59))])) == []
    assert entries(week(MON_AFTER, 0, 10, mbt_skip=[(-1, hm(17, 59))])) == []


def test_a_saturday_mnq_bar_booked_to_monday_is_not_the_entry_bar() -> None:
    """MON_AFTER: a synthetic MNQ bar at Saturday 17:59 carrying trade_date d, next to the MBT
    Saturday 17:59 bar (booked to d after the change): the entry is still only the Sunday one."""
    sat = MON_AFTER - timedelta(days=2)
    extra = mk_bar("MNQ", sat, hm(17, 59), B_MNQ, trade_day=MON_AFTER)
    assert entries([*week(MON_AFTER, 0, 10), extra]) == [(sunday_of(MON_AFTER), "17:59", "buy")]


# ------------------------------------------------------------------- the C6 skip ----
def test_c6_tests_the_mnq_sunday_18_00_fill(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, int]] = []

    def spy(root: str, t_ns: int) -> bool:
        calls.append((root, t_ns))
        return False

    monkeypatch.setattr(wkndbtc, "in_guard", spy)
    assert entries(week(MON, 0, 10)) == [(sunday_of(MON), "17:59", "buy")]
    assert calls == [("MNQ", ns_at(sunday_of(MON), hm(18, 0)))]


def test_c6_skips_a_guarded_sunday_18_00_fill(monkeypatch: pytest.MonkeyPatch) -> None:
    sunday_fill = ns_at(sunday_of(MON), hm(18, 0))
    monkeypatch.setattr(wkndbtc, "in_guard", lambda root, t_ns: t_ns == sunday_fill)
    assert entries(week(MON, 0, 10)) == []


# ------------------------------------------------------------ flat-only and the exit ----
def _acct(from_ns: int, position: int = 0, pending: int = 0, pend_from: int | None = None
          ) -> Any:
    flat = account(("MNQ",))
    held = account(("MNQ",), position, pending)
    pend = account(("MNQ",), position, -position)

    def acct(ts: int) -> MemberAccountView:
        if ts < from_ns:
            return flat
        return pend if pend_from is not None and ts >= pend_from else held
    return acct


@pytest.mark.parametrize("position,pending", [(1, 0), (-1, 0), (0, 1), (0, -1)])
def test_no_entry_while_a_position_or_a_pending_order_exists(position: int, pending: int
                                                            ) -> None:
    acct = _acct(ns_at(sunday_of(MON), hm(17, 0)), position, pending)
    out = entries(week(MON, 0, 10), acct)
    assert [e for e in out if e[1] == "17:59"] == []


def test_exit_at_monday_14_58_resent_while_not_pending() -> None:
    """The member's entry on the Sunday 17:59 view, then a position from 18:00: no exit before
    14:58 Monday; exits on 14:58 and (refused, not pending) 14:59; pending from 15:00."""
    acct = _acct(ns_at(sunday_of(MON), hm(18, 0)), 1, pend_from=ns_at(MON, hm(15, 0)))
    out = entries(week(MON, 0, 10), acct)
    assert out == [(sunday_of(MON), "17:59", "buy"), (MON, "14:58", "sell"),
                   (MON, "14:59", "sell")]


def test_exit_of_a_short_buys_and_a_missing_exit_bar_goes_to_the_next_bar() -> None:
    acct = _acct(ns_at(sunday_of(MON), hm(18, 0)), -1, pend_from=ns_at(MON, hm(15, 0)))
    out = entries(week(MON, 10, 0, mnq_skip=[(0, hm(14, 58))]), acct)
    assert out == [(sunday_of(MON), "17:59", "sell"), (MON, "14:59", "buy")]


def test_every_exit_closes_the_whole_position() -> None:
    acct = _acct(ns_at(sunday_of(MON), hm(18, 0)), 2, pend_from=ns_at(MON, hm(14, 59)))
    out = entries_any_qty(week(MON, 0, 10), acct)
    assert out == [(sunday_of(MON), "17:59", "buy", 1), (MON, "14:58", "sell", 2)]


def entries_any_qty(bars: Sequence[RootBar], acct: Any) -> list[tuple[date, str, str, int]]:
    out = drive(mk(), sorted(bars, key=lambda rb: rb[1].ts_event_ns), acct)
    return [(i[0], i[1], i[3], i[4]) for i in out]


# ---------------------------------------------------------------------- engine level ----
def run_week(monday: date, p_f: int = 0, p_s: int = 10, *, rules: Any = None, **kw: Any
             ) -> EngineResult:
    m = mk()
    bars = sorted(week(monday, p_f, p_s, **kw), key=lambda rb: rb[1].ts_event_ns)
    return engine(m, bars, rules_of(m, [monday]) if rules is None else rules)


def test_engine_fills_mnq_at_sunday_18_00_and_exits_monday_14_59() -> None:
    res = run_week(MON)
    assert fills(res) == [(sunday_of(MON), "18:00", "MNQ", "buy", "strategy"),
                          (MON, "14:59", "MNQ", "sell", "strategy")]
    assert intent_roots(res) == {"MNQ"}
    assert [f.qty for f in res.events(Fill)] == [1, 1]
    assert max(r.decision_ts_ns for r in res.events(IntentRecord)) <= ns_at(MON, hm(14, 59))


def test_engine_sell_side_after_the_24_7_change() -> None:
    res = run_week(MON_AFTER, 10, 0)
    assert fills(res) == [(sunday_of(MON_AFTER), "18:00", "MNQ", "sell", "strategy"),
                          (MON_AFTER, "14:59", "MNQ", "buy", "strategy")]


def test_engine_missing_exit_bar_exits_on_the_first_later_bar() -> None:
    res = run_week(MON, mnq_skip=[(0, hm(14, 58))])
    assert fills(res) == [(sunday_of(MON), "18:00", "MNQ", "buy", "strategy"),
                          (MON, "15:00", "MNQ", "sell", "strategy")]


def test_engine_refuses_on_a_signal_leg_roll_blackout_date_only() -> None:
    """V16(a) end to end: an MBT roll blackout on the Monday (MNQ clean). The runner's rules
    (member_window) drop the date: the open is refused as outside the window; kept in the
    window with the union as blackout: engine_roll_blackout; no blackout: it fills."""
    m = mk()
    bars = sorted(week(MON), key=lambda rb: rb[1].ts_event_ns)
    rules, mw = runner_rules(m, bars, {"MBT": [MON]})
    assert MON not in mw.dates and MON in mw.blackout_union
    res = engine(m, bars, rules)
    assert fills(res) == [] and refusals(res) == ["engine_not_a_window_date"]
    res = engine(mk(), bars, rules_of(m, [MON], blackout=mw.blackout_union))
    assert fills(res) == [] and refusals(res) == ["engine_roll_blackout"]
    clean, mw2 = runner_rules(m, bars, {})
    assert MON in mw2.dates
    assert fills(engine(mk(), bars, clean))[0] == (sunday_of(MON), "18:00", "MNQ", "buy",
                                                  "strategy")


def test_engine_a_friday_mbt_roll_blackout_alone_does_not_block_the_monday() -> None:
    """K8-L-12: d - 3 a roll-blackout date of MBT but d not: the engine allows the trade (the
    instrument_id test covers a contract change)."""
    m = mk()
    bars = sorted(week(MON), key=lambda rb: rb[1].ts_event_ns)
    res = engine(m, bars, rules_of(m, [MON], blackout=[MON - timedelta(days=3)]))
    assert fills(res)[0] == (sunday_of(MON), "18:00", "MNQ", "buy", "strategy")
