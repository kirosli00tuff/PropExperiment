"""Stage E.4 Part 3 K3 members of MemberCoder-B, part 3: K3-ecbfix-01
(reports/stage_e4c_member_specs.md section 7, K3-L-05; catalog C 648-725).

Synthetic bars through the real Stage E engine, with the kit of tests/test_e4_k3_members_b.py.
Two legs, sequential: leg 1 SELL 00:59/01:00 to T_E - 1/T_E; leg 2 BUY T_E/T_E + 1 to 15:04/15:05.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

import pytest

from rules.xfa_rules import Refusal
from screening.stage_e_engine import Fill
from screening.stage_e_rules import StageERules
from strategy.members.k3 import _calendar as cal_tables
from strategy.members.k3 import _clocks as clocks
from strategy.members.k3 import ecbfix
from tests._stage_e_canary_kit import NO_RELEASES, rules_for
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
    ns_at,
    release_at,
    run,
    view_of,
)

STD = date(2025, 6, 3)  # Tuesday: T_E 07:15 CT
NEXT = date(2025, 6, 4)
MISMATCH = date(2025, 10, 28)  # the autumn mismatch week: T_E 08:15 CT
SPRING = date(2026, 3, 10)  # the spring mismatch week: T_E 08:15 CT
CST = date(2026, 1, 13)  # CST, CET: T_E 07:15 CT
TGT_ONLY = date(2025, 5, 1)  # a TARGET closing day (Labour Day), a full FX session
ECB = {"start": hm(0, 30), "end": hm(15, 12)}  # the ecbfix segment of CT date d


def day(d: date, **kw: Any) -> Day:
    return Day(d, **{**ECB, **kw})


def legs(d: date, t_e: str = "07:15", leg1_exit: str | None = None,
         leg2_entry: str | None = None, leg2_exit: str = "15:05") -> list[tuple]:
    """The four fills of a normal day: leg 1 SELL 01:00 -> BUY at T_E; leg 2 BUY -> SELL."""
    t_plus = f"{t_e[:3]}{int(t_e[3:]) + 1:02d}"
    return [(d, "01:00", "sell", "strategy"), (d, leg1_exit or t_e, "buy", "strategy"),
            (d, leg2_entry or t_plus, "buy", "strategy"), (d, leg2_exit, "sell", "strategy")]


def test_the_table_rows_the_ecbfix_tests_use() -> None:
    t_e, full = dict(clocks.T_E), set(cal_tables.FX_FULL_SESSIONS)
    tgt = set(cal_tables.TGT_CLOSING_DAYS)
    assert [t_e[d.isoformat()] for d in (STD, NEXT, MISMATCH, SPRING, CST)] == [
        "07:15", "07:15", "08:15", "08:15", "07:15"]
    for d in (STD, NEXT, MISMATCH, SPRING, CST):
        assert d.isoformat() in full and d.isoformat() not in tgt
    assert TGT_ONLY.isoformat() in full and TGT_ONLY.isoformat() in tgt
    assert TGT_ONLY.isoformat() not in cal_tables.EW_BANK_HOLIDAYS  # only the TARGET rule


def test_ecbfix_standard_day_both_legs_at_the_spec_minutes() -> None:
    res = run(ecbfix.make_6e(), [day(STD)])
    assert intents(res) == decided(STD, "00:59", "07:14", "07:15", "15:04")
    assert fills(res) == legs(STD)
    assert [f.qty for f in res.events(Fill)] == [1, 1, 1, 1]  # q_c 1


@pytest.mark.parametrize("d", [MISMATCH, SPRING])
def test_ecbfix_mismatch_weeks_move_the_fix_minutes_to_0815(d: date) -> None:
    res = run(ecbfix.make_6e(), [day(d)])
    assert intents(res) == decided(d, "00:59", "08:14", "08:15", "15:04")
    assert fills(res) == legs(d, "08:15")


def test_ecbfix_cst_date_keeps_0715() -> None:
    res = run(ecbfix.make_6e(), [day(CST)])
    assert fills(res) == legs(CST)


def test_ecbfix_is_unconditional_whatever_the_prices_do() -> None:
    for x in (-40, 40):
        paths = {hm(0, 58): flat(x), hm(7, 14): flat(-x), hm(7, 15): flat(x)}
        res = run(ecbfix.make_6e(), [day(STD, paths=paths)])
        assert fills(res) == legs(STD)


def test_ecbfix_a_target_closing_day_is_not_traded() -> None:
    res = run(ecbfix.make_6e(), [day(TGT_ONLY), day(date(2025, 5, 2))])
    assert intents(res) == decided(date(2025, 5, 2), "00:59", "07:14", "07:15", "15:04")
    assert fills(res) == legs(date(2025, 5, 2))


def test_ecbfix_early_halt_and_early_f_dates_are_not_traded() -> None:
    days = [day(date(2025, 7, 4), halt="12:00"), day(date(2025, 11, 27))]  # K3-L-04, K3-L-11
    res = run(ecbfix.make_6e(), days)
    assert intents(res) == [] and fills(res) == []


def test_ecbfix_a_missing_0059_bar_means_no_trade_that_date_k3_l_12() -> None:
    """K3-L-12: a missing 00:59 bar is a C4 date exclusion for the whole two-leg trade: no leg 1
    (no late entry at 01:00) and no leg 2 at T_E; the next date trades normally."""
    res = run(ecbfix.make_6e(), [day(STD, skip=frozenset({hm(0, 59)})), day(NEXT)])
    assert intents(res) == decided(NEXT, "00:59", "07:14", "07:15", "15:04")
    assert fills(res) == legs(NEXT)


@dataclass(frozen=True)
class RefuseOpenRules(StageERules):
    """TEST ONLY: the real rules, plus a refusal (by name) of any opening intent emitted on the
    bars opening at ``refuse_at_ns``, to show what the member does when the engine refuses leg
    1's intent."""

    refuse_at_ns: frozenset[int] = frozenset()

    def structural_refusal(self, run: Any, norm: Any, ts: int, bars: Any) -> Refusal | None:
        if ts in self.refuse_at_ns and self._opens(run, norm):
            return Refusal("test_refused_open", "test-only refusal of an opening intent")
        return super().structural_refusal(run, norm, ts, bars)


def test_ecbfix_a_refused_leg_1_intent_means_no_leg_2_k3_l_12() -> None:
    """K3-L-12: the engine refuses leg 1 at 00:59, so the sequential pair never started: no
    leg 2 at T_E (the member stays flat all day); the next date trades normally."""
    member = ecbfix.make_6e()
    days = [day(STD), day(NEXT)]
    rules = rules_for(member.legs, [d.trade_date for d in days], NO_RELEASES,
                      cls=RefuseOpenRules, refuse_at_ns=frozenset({ns_at(STD, hm(0, 59))}))
    res = run(member, days, rules=rules)
    assert intents(res) == [(STD, "00:59", False, "test_refused_open")] + decided(
        NEXT, "00:59", "07:14", "07:15", "15:04")
    assert fills(res) == legs(NEXT)


def test_ecbfix_a_missing_t_e_minus_1_bar_means_no_leg_2() -> None:
    """K3-L-05: leg 1's exit goes on the T_E bar (fill T_E + 1); leg 1 is still open at T_E, so
    there is no leg 2 that day."""
    res = run(ecbfix.make_6e(), [day(STD, skip=frozenset({hm(7, 14)}))])
    assert intents(res) == decided(STD, "00:59", "07:15")
    assert fills(res) == [(STD, "01:00", "sell", "strategy"), (STD, "07:16", "buy", "strategy")]


def test_ecbfix_a_missing_t_e_bar_fills_leg_1_later_and_skips_leg_2() -> None:
    res = run(ecbfix.make_6e(), [day(STD, skip=frozenset({hm(7, 15)}))])
    assert intents(res) == decided(STD, "00:59", "07:14")  # no leg 2 without its entry bar
    assert fills(res) == [(STD, "01:00", "sell", "strategy"), (STD, "07:16", "buy", "strategy")]


def test_ecbfix_missing_fill_bars_move_the_fills_to_the_next_present_bar() -> None:
    res = run(ecbfix.make_6e(), [day(STD, skip=frozenset({hm(1, 0), hm(7, 16)}))])
    assert intents(res) == decided(STD, "00:59", "07:14", "07:15", "15:04")
    assert fills(res) == [(STD, "01:01", "sell", "strategy"), (STD, "07:15", "buy", "strategy"),
                          (STD, "07:17", "buy", "strategy"), (STD, "15:05", "sell", "strategy")]


def test_ecbfix_a_missing_1504_bar_sends_leg_2s_exit_on_the_next_present_bar() -> None:
    res = run(ecbfix.make_6e(), [day(STD, skip=frozenset({hm(15, 4)}))])
    assert intents(res) == decided(STD, "00:59", "07:14", "07:15", "15:05")
    assert fills(res) == legs(STD, leg2_exit="15:06")


def test_ecbfix_leg_2_still_open_at_the_real_f_1508_is_closed_by_the_engine() -> None:
    """No bar from 15:04 to 15:07: the member's exit bar never comes before F; the engine's own
    flatten (rules.sessions F = 15:08 CT) closes leg 2 and the member sends nothing more."""
    gap = frozenset({hm(15, 4), hm(15, 5), hm(15, 6), hm(15, 7)})
    res = run(ecbfix.make_6e(), [day(STD, skip=gap)])
    assert intents(res) == decided(STD, "00:59", "07:14", "07:15")
    assert fills(res) == legs(STD)[:3] + [(STD, "15:09", "sell", "forced_flatten")]


def test_ecbfix_leg_2_open_at_a_synthetic_f_is_closed_by_the_engine() -> None:
    res = run(ecbfix.make_6e(), [day(STD, flatten_from=hm(10, 0))])
    assert intents(res) == decided(STD, "00:59", "07:14", "07:15")
    assert fills(res) == legs(STD)[:3] + [(STD, "10:01", "sell", "forced_flatten")]


def test_ecbfix_leg_1_open_at_a_synthetic_f_is_closed_and_nothing_follows() -> None:
    res = run(ecbfix.make_6e(), [day(STD, flatten_from=hm(3, 0))])
    assert intents(res) == decided(STD, "00:59")
    assert fills(res) == [(STD, "01:00", "sell", "strategy"),
                          (STD, "03:01", "buy", "forced_flatten")]


def test_ecbfix_d9_7_on_leg_1_ends_the_day_no_leg_2() -> None:
    """S0.7: after an engine close the member makes no further entry that trade date."""
    member = ecbfix.make_6e()
    days = [day(STD), day(NEXT)]
    res = run(member, days, rules=forced_limit_rules(member, days, [(STD, hm(3, 0))]))
    assert intents(res) == decided(STD, "00:59") + decided(NEXT, "00:59", "07:14", "07:15",
                                                           "15:04")
    assert fills(res) == [(STD, "01:00", "sell", "strategy"),
                          (STD, "03:01", "buy", "price_limit_exit")] + legs(NEXT)


def test_ecbfix_d9_7_on_leg_2_no_duplicate_exit() -> None:
    member = ecbfix.make_6e()
    days = [day(STD)]
    res = run(member, days, rules=forced_limit_rules(member, days, [(STD, hm(12, 0))]))
    assert intents(res) == decided(STD, "00:59", "07:14", "07:15")
    assert fills(res) == legs(STD)[:3] + [(STD, "12:01", "sell", "price_limit_exit")]


def test_ecbfix_d9_5a_a_release_at_t_e_holds_leg_1s_exit_and_so_removes_leg_2() -> None:
    """A release row at T_E (none exists in the frozen calendar) would guard [T_E, T_E + 2):
    leg 1's exit fills at T_E + 2, leg 1 is still open at the T_E bar, so no leg 2 (K3-L-05)."""
    res = run(ecbfix.make_6e(), [day(STD)], releases=release_at("6E", STD, hm(7, 15)))
    assert intents(res) == decided(STD, "00:59", "07:14")
    assert fills(res) == [(STD, "01:00", "sell", "strategy"), (STD, "07:17", "buy", "strategy")]


def test_ecbfix_d9_5a_defers_leg_2s_entry_and_leaves_nfp_alone() -> None:
    res = run(ecbfix.make_6e(), [day(STD)], releases=release_at("6E", STD, hm(7, 16)))
    assert fills(res) == legs(STD, leg2_entry="07:18")
    res = run(ecbfix.make_6e(), [day(STD)], releases=release_at("6E", STD, hm(7, 30)))  # NFP
    assert fills(res) == legs(STD)
    res = run(ecbfix.make_6e(), [day(STD)], releases=release_at("6E", STD, hm(1, 0)))
    assert fills(res) == [(STD, "01:02", "sell", "strategy")] + legs(STD)[1:]


def test_ecbfix_consecutive_days_trade_both_legs_each_day() -> None:
    res = run(ecbfix.make_6e(), [day(STD), day(NEXT)])
    assert fills(res) == legs(STD) + legs(NEXT)


def test_ecbfix_a_moved_or_dropped_row_moves_or_drops_the_trade() -> None:
    moved = tuple((d, "08:15" if d == STD.isoformat() else t) for d, t in clocks.T_E)
    res = run(ecbfix.EcbFix("6E", t_e=moved), [day(STD)])
    assert fills(res) == legs(STD, "08:15")
    full = tuple(d for d in cal_tables.FX_FULL_SESSIONS if d != STD.isoformat())
    res = run(ecbfix.EcbFix("6E", full_sessions=full), [day(STD)])
    assert intents(res) == [] and fills(res) == []
    tgt = (*cal_tables.TGT_CLOSING_DAYS, STD.isoformat())
    res = run(ecbfix.EcbFix("6E", tgt_closing_days=tgt), [day(STD)])
    assert intents(res) == [] and fills(res) == []


def test_ecbfix_direct_calls_no_leg_while_pending_and_one_chance_each() -> None:
    member = ecbfix.make_6e()
    leg1 = bar_at("6E", STD, hm(0, 59))
    assert member.on_minute(view_of("6E", leg1.ts_event_ns, leg1), account_of("6E",
                                                                           pending=1)) == ()
    assert member.on_minute(view_of("6E", leg1.ts_event_ns, leg1), account_of("6E")) == ()
    leg2 = bar_at("6E", STD, hm(7, 15))
    assert member.on_minute(view_of("6E", leg2.ts_event_ns, leg2), account_of("6E",
                                                                           pending=1)) == ()
    assert member.on_minute(view_of("6E", leg2.ts_event_ns, leg2), account_of("6E")) == ()
    fresh = ecbfix.make_6e()
    out = fresh.on_minute(view_of("6E", leg1.ts_event_ns, leg1), account_of("6E"))
    assert [(i.side, i.quantity) for i in out] == [("sell", 1)]
    early = bar_at("6E", STD, hm(7, 13))  # before T_E - 1: leg 1 is held, no exit yet
    assert fresh.on_minute(view_of("6E", early.ts_event_ns, early), account_of("6E", -1)) == ()
    exit1 = bar_at("6E", STD, hm(7, 14))
    out = fresh.on_minute(view_of("6E", exit1.ts_event_ns, exit1), account_of("6E", -1))
    assert [(i.side, i.quantity) for i in out] == [("buy", 1)]
    out = fresh.on_minute(view_of("6E", leg2.ts_event_ns, leg2), account_of("6E"))
    assert [(i.side, i.quantity) for i in out] == [("buy", 1)]
    exit2 = bar_at("6E", STD, hm(15, 4))
    assert fresh.on_minute(view_of("6E", exit2.ts_event_ns, exit2),
                           account_of("6E", 1, pending=-1)) == ()  # an exit is pending
    out = fresh.on_minute(view_of("6E", exit2.ts_event_ns, exit2), account_of("6E", 1))
    assert [(i.side, i.quantity) for i in out] == [("sell", 1)]
