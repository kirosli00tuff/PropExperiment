"""Stage E.7 K1 members of MemberCoder-B, part 2: K1-vwap-01 (reports/stage_e7_member_specs.md
sections 0, 5 and 8; readings K1-L-06..K1-L-10, K1-L-15). Reuses the synthetic kit of
tests/test_k1_members_vxnband.py.

Synthetic bars only, run through the real Stage E engine, with direct calls where the engine cannot
reach a case (an open position across an instrument change, a pending order held fixed). Bars
are O = H = L = C unless a test sets H or L, so VWAP is the volume-weighted mean close; a level step
moves the close across it.
"""

from __future__ import annotations

from datetime import date, time
from typing import Any

import pytest

from screening.stage_e_engine import Fill, IntentRecord, run_engine
from screening.stage_e_rules import load_release_calendar
from strategy.members.k1 import _event_common as common
from strategy.members.k1 import vwap
from strategy.stage_e.interface import LegSpec, StageEMember, TradingInterval
from tests.test_k1_members_vxnband import (
    D0,
    D1,
    EVENING,
    ID,
    OTHER_ID,
    ROOT,
    Day,
    ForcedLimitRules,
    at,
    bars,
    call,
    drive,
    fills,
    frame,
    hm,
    intents,
    ns_at,
    rules,
    run,
)

UP, DOWN = 40, -40  # level steps (ticks) far from the running VWAP


def buy(day: date, hhmm: str, accepted: bool = True) -> tuple[str, str, bool]:
    return (at(day, hhmm), "buy", accepted)


def sell(day: date, hhmm: str, accepted: bool = True) -> tuple[str, str, bool]:
    return (at(day, hhmm), "sell", accepted)


def filled(day: date, hhmm: str, side: str, reason: str = "strategy") -> tuple[str, str, str]:
    return (at(day, hhmm), side, reason)


def day1(**kw: Any) -> list[Day]:
    """A flat D0 (no sign, no intent; the engine's prior-settlement proxy for D1), then D1."""
    return [Day(D0), Day(D1, **kw)]


# ------------------------------------------------------------------ declaration ----
def test_declaration_label_leg_and_trading_window() -> None:
    m = vwap.make_mnq()
    assert isinstance(m, StageEMember)
    assert m.name == "K1-vwap-01 MNQ" == vwap.MEMBER_ID + " MNQ"
    assert m.legs == (LegSpec("MNQ", True),)
    assert m.trading_windows == {"MNQ": (TradingInterval(time(8, 30), time(15, 0)),)}
    assert vwap.MAX_ENTRIES == 20
    assert vwap.make_mnq() is not m


# ------------------------------------------------------------------ the sign ----
def test_no_sign_before_the_first_and_a_long_hold_to_the_final_exit() -> None:
    """Flat bars from 08:30 tie with VWAP: s = 0, no entry. +40 at 09:00 buys (fill 09:01); the
    close stays above VWAP, so the position is held to the final exit on 14:58 (fill 14:59)."""
    res = run(vwap.make_mnq(), day1(closes={hm(9, 0): UP}))
    assert intents(res) == [buy(D1, "09:00"), sell(D1, "14:58")]
    assert fills(res) == [filled(D1, "09:01", "buy"), filled(D1, "14:59", "sell")]
    assert intents(run(vwap.make_mnq(), day1())) == []


@pytest.mark.parametrize(("level", "first"), [(UP, "buy"), (DOWN, "sell")])
def test_a_flat_entry_goes_in_s_ts_direction(level: int, first: str) -> None:
    res = run(vwap.make_mnq(), day1(closes={hm(9, 0): level}))
    assert intents(res)[0] == (at(D1, "09:00"), first, True)


def test_a_close_exactly_at_vwap_keeps_the_previous_sign_and_the_minimum_hold() -> None:
    """Exact arithmetic in ticks (K1-L-06), offsets from BASE:
    - 08:30: C = H = +3, L = 0: 2C - H - L = +3 > 0, s = +1, buy (fill 08:31 = bar k);
    - 08:31: +0: 3 x 0 x 20 - (60 + 0) < 0, s = -1, but k = 08:31: the hold is not met;
    - 08:32: +1: 3 x 1 x 30 - (60 + 0 + 30) = 0, close = VWAP exactly: s stays -1 and the hold
      is met (08:32 >= k + 1), so the reversal pair goes on 08:32 (fills 08:33);
    - later bars at +1 keep the tie: the short is held to the final exit."""
    closes = {hm(8, 30): 3, hm(8, 31): 0, hm(8, 32): 1}
    days = day1(closes=closes, lows={hm(8, 30): 0})
    res = run(vwap.make_mnq(), days)
    assert intents(res) == [buy(D1, "08:30"), sell(D1, "08:32"), sell(D1, "08:32"),
                            buy(D1, "14:58")]
    assert fills(res) == [filled(D1, "08:31", "buy"), filled(D1, "08:33", "sell"),
                          filled(D1, "08:33", "sell"), filled(D1, "14:59", "buy")]


def test_the_sign_matches_exact_integer_vwap_arithmetic() -> None:
    """Direct calls on the tie bars: s after each bar."""
    member = vwap.make_mnq()
    closes = {hm(8, 30): 3, hm(8, 31): 0, hm(8, 32): 1}
    days = [Day(D1, start=hm(8, 30), end=hm(8, 34), closes=closes, lows={hm(8, 30): 0})]
    signs = []
    for bar in bars(days):
        call(member, bar, position=0, pending=1)  # pending: the rule sends nothing
        signs.append(member._s)
    assert signs == [1, -1, -1, -1]


def test_volume_weights_the_vwap() -> None:
    """Direct calls: A +10 (vol 1), B 0 (vol 9), C +2 (vol 10). Weighted VWAP after C is
    (10 + 0 + 20) / 20 = 1.5 < 2: s = +1 (the unweighted mean 4 would give -1)."""
    member = vwap.make_mnq()
    days = [Day(D1, start=hm(8, 30), end=hm(8, 33),
                closes={hm(8, 30): 10, hm(8, 31): 0, hm(8, 32): 2},
                volumes={hm(8, 30): 1, hm(8, 31): 9, hm(8, 32): 10})]
    signs = []
    for bar in bars(days):
        call(member, bar, position=0, pending=1)
        signs.append(member._s)
    assert signs == [0, -1, 1]


def test_zero_volume_bars_take_no_action() -> None:
    """sum(volume) = 0 from 08:30 through t: no action and no sign (no division either); the
    first bar with volume starts the sums."""
    vols = {hm(8, 30) + i: 0 for i in range(10)}
    days = day1(closes={hm(8, 30): UP, hm(8, 40): 2 * UP}, volumes=vols,
                lows={hm(8, 40): 0})
    res = run(vwap.make_mnq(), days)
    assert intents(res)[0] == buy(D1, "08:40")


def test_vwap_starts_at_0830() -> None:
    """Bars before 08:30 (+1000) do not enter VWAP: +4 at 09:00 is above the session VWAP."""
    days = day1(start=hm(7, 20), closes={hm(7, 20): 1000, hm(8, 30): 0, hm(9, 0): 4})
    assert intents(run(vwap.make_mnq(), days))[0] == buy(D1, "09:00")


# ------------------------------------------------------------------ reversal and hold ----
def test_the_reversal_pair_is_accepted_and_both_legs_fill_at_the_same_next_open() -> None:
    """Engine level: the exit and the new entry are two market intents on the 09:10 bar (never
    one 2 q_c order); both are accepted and fill at the 09:11 open; the position ends short."""
    res = run(vwap.make_mnq(), day1(closes={hm(9, 0): UP, hm(9, 10): DOWN}))
    recs = res.events(IntentRecord)[1:3]
    assert [(r.accepted, r.position_before, r.pending_before) for r in recs] == [
        (True, 1, 0), (True, 1, -1)]
    assert all("quantity=1" in r.received for r in recs)
    assert fills(res)[1:3] == [filled(D1, "09:11", "sell"), filled(D1, "09:11", "sell")]
    assert [f.position_after for f in res.events(Fill)][1:3] == [0, -1]


def test_no_exit_on_the_fill_bar_k_an_exit_on_k_plus_1() -> None:
    """Buy on 09:00, filled at the 09:01 open (k); the sign flips on 09:01 (hold not met: wait)
    and the reversal goes on 09:02 (fills 09:03)."""
    res = run(vwap.make_mnq(), day1(closes={hm(9, 0): UP, hm(9, 1): DOWN}))
    assert intents(res)[:3] == [buy(D1, "09:00"), sell(D1, "09:02"), sell(D1, "09:02")]
    assert fills(res)[:3] == [filled(D1, "09:01", "buy"), filled(D1, "09:03", "sell"),
                              filled(D1, "09:03", "sell")]


def test_the_hold_restarts_at_the_reversal_fill() -> None:
    """The reversal pair of 09:10 fills at 09:11 (the new k); a flip on 09:11 waits, and the
    reversal back goes on 09:12."""
    res = run(vwap.make_mnq(), day1(closes={hm(9, 0): UP, hm(9, 10): DOWN, hm(9, 11): 4 * UP}))
    assert intents(res)[:5] == [buy(D1, "09:00"), sell(D1, "09:10"), sell(D1, "09:10"),
                                buy(D1, "09:12"), buy(D1, "09:12")]


def test_a_flip_on_k_and_back_on_k_plus_1_does_not_reverse() -> None:
    res = run(vwap.make_mnq(), day1(closes={hm(9, 0): UP, hm(9, 1): DOWN, hm(9, 2): UP}))
    assert intents(res) == [buy(D1, "09:00"), sell(D1, "14:58")]


def test_no_intent_while_an_order_is_pending() -> None:
    """Direct calls: flat with a pending order, s = +1: nothing; long with a pending exit and
    s = -1 (hold met): nothing. Controls without the pending order."""
    days = [Day(D1, start=hm(8, 30), end=hm(9, 30), closes={hm(9, 0): UP, hm(9, 10): DOWN})]
    assert drive(vwap.make_mnq(), days, lambda b: (0, 1)) == []
    assert drive(vwap.make_mnq(), days, lambda b: (1, -1)) == []
    flat = drive(vwap.make_mnq(), days, lambda b: (0, 0))
    assert flat[0][0] == at(D1, "09:00") and flat[0][1][0].side == "buy"
    long_ = drive(vwap.make_mnq(), days, lambda b: (1, 0))
    assert long_[0][0] == at(D1, "09:10")
    assert [(i.side, i.quantity) for i in long_[0][1]] == [("sell", 1), ("sell", 1)]


# ------------------------------------------------------------------ the entry cap ----
def alternating(first: int, count: int, step: int = 2) -> dict[int, int]:
    return {first + step * i: (UP if i % 2 == 0 else DOWN) for i in range(count)}


def test_twenty_entry_intents_reversal_legs_included_then_an_exit_to_flat() -> None:
    """Entry 1 on 09:00, reversals on 09:02, 09:04, ..., 09:38 (entries 2..20); the next opposite
    signal (09:40) exits to flat; later signals send nothing."""
    res = run(vwap.make_mnq(), day1(closes=alternating(hm(9, 0), 30)))
    got = intents(res)
    assert got[0] == buy(D1, "09:00")
    pairs = got[1:39]
    for i in range(19):
        hhmm = f"09:{2 + 2 * i:02d}"
        side = "sell" if i % 2 == 0 else "buy"
        assert pairs[2 * i:2 * i + 2] == [(at(D1, hhmm), side, True)] * 2
    assert got[39:] == [buy(D1, "09:40")]
    assert all(ok for _, _, ok in got)
    assert fills(res)[-1] == filled(D1, "09:41", "buy")
    assert res.events(Fill)[-1].position_after == 0


def test_a_refused_entry_intent_counts_toward_the_cap() -> None:
    """K1-L-08: on a roll-blackout date every entry is refused; the member sends 20 (09:00..09:19)
    and nothing after."""
    res = run(vwap.make_mnq(), day1(closes={hm(9, 0): UP}), blackout=[D1])
    got = intents(res)
    assert got == [buy(D1, f"09:{m:02d}", False) for m in range(20)]


# ------------------------------------------------------------------ the clock ----
@pytest.mark.parametrize(("step_at", "expected"), [
    (hm(14, 56), ["buy 14:56", "sell 14:58"]),
    (hm(14, 57), []),
])
def test_no_entry_from_the_1457_bar(step_at: int, expected: list[str]) -> None:
    res = run(vwap.make_mnq(), day1(closes={step_at: UP}))
    assert [f"{s} {t[-5:]}" for t, s, _ in intents(res)] == expected
    if expected:
        assert fills(res) == [filled(D1, "14:57", "buy"), filled(D1, "14:59", "sell")]


def test_no_reversal_on_the_1457_bar() -> None:
    res = run(vwap.make_mnq(), day1(closes={hm(9, 0): UP, hm(14, 57): 2 * DOWN}))
    assert intents(res) == [buy(D1, "09:00"), sell(D1, "14:58")]


def test_a_missing_1458_bar_sends_the_final_exit_on_the_1459_bar() -> None:
    res = run(vwap.make_mnq(), day1(closes={hm(9, 0): UP}, skip=frozenset({hm(14, 58)})))
    assert intents(res) == [buy(D1, "09:00"), sell(D1, "14:59")]
    assert fills(res)[-1] == filled(D1, "15:00", "sell")


def test_no_final_exit_while_an_order_is_pending() -> None:
    """Direct calls (S0.7): long; on 14:58 an order is pending: nothing; on 14:59 the exit."""
    days = [Day(D1, start=hm(8, 30), end=hm(15, 0), closes={hm(9, 0): UP})]

    def account(bar: Any) -> tuple[int, int]:
        if bar.ts_event_ns < ns_at(D1, hm(9, 1)):
            return (0, 0)
        return (1, -1 if bar.ts_event_ns == ns_at(D1, hm(14, 58)) else 0)

    got = drive(vwap.make_mnq(), days, account)
    assert [(t, [i.side for i in items]) for t, items in got] == [
        (at(D1, "09:00"), ["buy"]), (at(D1, "14:59"), ["sell"])]


# ------------------------------------------------------------------ missing bars ----
def test_a_gap_ends_new_entries_an_open_position_keeps_the_opposite_signal_exit() -> None:
    """Long from 09:00; the 10:00 bar is missing; the 10:05 flip exits to flat without a new leg;
    the 11:00 flip sends nothing."""
    days = day1(closes={hm(9, 0): UP, hm(10, 5): 2 * DOWN, hm(11, 0): 4 * UP},
                skip=frozenset({hm(10, 0)}))
    res = run(vwap.make_mnq(), days)
    assert intents(res) == [buy(D1, "09:00"), sell(D1, "10:05")]
    assert fills(res) == [filled(D1, "09:01", "buy"), filled(D1, "10:06", "sell")]


def test_a_gap_keeps_the_final_exit() -> None:
    days = day1(closes={hm(9, 0): UP}, skip=frozenset({hm(10, 0)}))
    assert intents(run(vwap.make_mnq(), days)) == [buy(D1, "09:00"), sell(D1, "14:58")]


@pytest.mark.parametrize("missing", [hm(8, 30), hm(8, 45)])
def test_a_gap_before_any_entry_means_no_trade(missing: int) -> None:
    days = day1(closes={hm(9, 0): UP}, skip=frozenset({missing}))
    assert intents(run(vwap.make_mnq(), days)) == []


# ------------------------------------------------------------------ instrument change ----
def test_an_instrument_change_sends_an_exit_and_ends_new_entries() -> None:
    """Direct calls (the engine never carries a position across a splice): long, the 10:00 bar
    carries another id: an exit on 10:00, resent on 10:01 while the position stays open; once
    flat, no new entry although s = +1."""
    days = [Day(D1, start=hm(8, 30), end=hm(10, 30), closes={hm(9, 0): UP},
                ids={hm(10, 0): OTHER_ID})]
    member = vwap.make_mnq()
    got = drive(member, days, lambda b: (1 if b.ts_event_ns <= ns_at(D1, hm(10, 1)) else 0, 0)
                if b.ts_event_ns >= ns_at(D1, hm(9, 1)) else (0, 0))
    assert [(t, [(i.side, i.quantity) for i in items]) for t, items in got] == [
        (at(D1, "09:00"), [("buy", 1)]), (at(D1, "10:00"), [("sell", 1)]),
        (at(D1, "10:01"), [("sell", 1)])]


def test_an_instrument_change_while_flat_ends_new_entries() -> None:
    days = day1(closes={hm(9, 0): UP}, ids={hm(8, 50): OTHER_ID})
    assert intents(run(vwap.make_mnq(), days)) == []
    control = day1(closes={hm(9, 0): UP}, ids={hm(8, 30): OTHER_ID})  # one id from 08:30
    assert intents(run(vwap.make_mnq(), control))[0] == buy(D1, "09:00")
    # the reference is the 08:30 bar's id: another id on 08:30 alone is a change from 08:31
    first_only = day1(closes={hm(9, 0): UP}, ids={hm(8, 30): OTHER_ID, hm(8, 31): ID})
    assert intents(run(vwap.make_mnq(), first_only)) == []


# ------------------------------------------------------------------ engine closure ----
def test_after_an_engine_closure_the_rule_continues() -> None:
    """K1-L-09 / K7-L-07: the engine closes the long at the 09:11 open (D9.7 queued on 09:10); the
    member sees a flat account with s = +1 and buys again on 09:11."""
    days = day1(closes={hm(9, 0): UP})
    res = run_engine({ROOT: frame(days)}, vwap.make_mnq(), (LegSpec(ROOT, True),),
                     rules(days, cls=ForcedLimitRules,
                           force_at_ns=frozenset({ns_at(D1, hm(9, 10))})))
    assert intents(res) == [buy(D1, "09:00"), buy(D1, "09:11"), sell(D1, "14:58")]
    assert fills(res) == [filled(D1, "09:01", "buy"), filled(D1, "09:11", "sell",
                                                             "price_limit_exit"),
                          filled(D1, "09:12", "buy"), filled(D1, "14:59", "sell")]


def test_after_the_engines_flatten_at_a_synthetic_f_the_rule_continues() -> None:
    """Audit finding 4 (R-T3-1): a synthetic F from 10:00; the engine's forced flatten fills at
    10:01. The member sends no exit of its own; flat with s = +1, it sends the rule's flat entries
    (refused: engine_flatten_window) until its 20 entry intents are used (K1-L-08, K1-L-09)."""
    days = [Day(D0), Day(D1, closes={hm(9, 0): UP}, flatten_from=hm(10, 0))]
    res = run(vwap.make_mnq(), days)
    assert intents(res) == [buy(D1, "09:00")] + [buy(D1, f"10:{m:02d}", False)
                                                 for m in range(1, 20)]
    assert {r.refusal.reason for r in res.events(IntentRecord)[1:]} == {"engine_flatten_window"}
    assert fills(res) == [filled(D1, "09:01", "buy"), filled(D1, "10:01", "sell",
                                                             "forced_flatten")]


def test_evening_bars_do_not_enter_the_vwap_or_the_0830_clock_run() -> None:
    """Audit finding 1 (R-T3-1): the trade date opens at 17:00 CT the evening before, at +1000.
    Only bars of CT date d from 08:30 are read: the 09:00 step to +4 is above the session VWAP
    (it would be below a VWAP holding the evening) and the evening leaves no gap in the 08:30
    run (a gap would stop every entry). The normal round trip follows."""
    days = [Day(D0), Day(D1, start=EVENING, closes={EVENING: 1000, 0: 0, hm(9, 0): 4})]
    res = run(vwap.make_mnq(), days)
    assert intents(res) == [buy(D1, "09:00"), sell(D1, "14:58")]
    assert fills(res) == [filled(D1, "09:01", "buy"), filled(D1, "14:59", "sell")]


# ------------------------------------------------------------------ dates ----
def test_a_not_full_session_date_is_not_traded() -> None:
    wed, thu = date(2025, 7, 2), date(2025, 7, 3)
    assert not common.is_full_session(thu)
    res = run(vwap.make_mnq(), [Day(date(2025, 7, 1)), Day(wed, closes={hm(9, 0): UP}),
                                Day(thu, end=hm(11, 0), closes={hm(9, 0): UP})])
    assert intents(res) == [buy(wed, "09:00"), sell(wed, "14:58")]


# ------------------------------------------------------------------ releases ----
def test_the_cpi_window_bars_send_nothing() -> None:
    """K1-L-15: CPI date 2025-05-13 (07:30 CT): steps on the 07:25-07:35 bars send nothing."""
    tue = date(2025, 5, 13)
    days = [Day(date(2025, 5, 12)),
            Day(tue, start=hm(7, 20), closes={hm(7, 25): UP, hm(7, 36): 0, hm(9, 0): UP})]
    res = run(vwap.make_mnq(), days, releases=load_release_calendar())
    assert intents(res) == [buy(tue, "09:00"), sell(tue, "14:58")]


def test_event_minutes_ism_0900_and_fomc_1300() -> None:
    """The member reads no release. ISM Services 2025-05-05: the 08:59 buy fills at 09:02
    (D9.5a); the 09:00 flip waits while the order is pending (09:00, 09:01) and for the hold (k =
    09:02), then reverses on 09:03. FOMC 2025-05-07: the 13:00 flip reverses on 13:00 as the rule
    says; both legs fill at 13:02."""
    cal = load_release_calendar()
    mon, wed = date(2025, 5, 5), date(2025, 5, 7)
    res = run(vwap.make_mnq(), [Day(date(2025, 5, 2)),
                                Day(mon, closes={hm(8, 59): UP, hm(9, 0): 2 * DOWN})],
              releases=cal)
    assert intents(res)[:3] == [buy(mon, "08:59"), sell(mon, "09:03"), sell(mon, "09:03")]
    assert fills(res)[:3] == [filled(mon, "09:02", "buy"), filled(mon, "09:04", "sell"),
                              filled(mon, "09:04", "sell")]
    res = run(vwap.make_mnq(), [Day(date(2025, 5, 6)),
                                Day(wed, closes={hm(12, 0): UP, hm(13, 0): 2 * DOWN})],
              releases=cal)
    assert intents(res)[:3] == [buy(wed, "12:00"), sell(wed, "13:00"), sell(wed, "13:00")]
    assert fills(res)[:3] == [filled(wed, "12:01", "buy"), filled(wed, "13:02", "sell"),
                              filled(wed, "13:02", "sell")]

