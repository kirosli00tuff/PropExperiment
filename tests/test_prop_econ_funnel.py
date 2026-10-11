"""Stage E.19 funnel: hand-computed Combine and XFA paths pinned to the cent (sim_spec 2-4).

Every expected number below is worked out by hand in the comments. Fixtures:
tests/test_prop_econ_fixtures.py (hand rules, not Topstep's; the UNIT product turns a path of
dollars into exact P&Ls).
"""

from __future__ import annotations

import dataclasses

import numpy as np
import pytest

from prop_econ.funnel import (
    ATTEMPT_BREACH,
    ATTEMPT_PASS,
    ATTEMPT_TIMEOUT,
    XFA_BREACH,
    XFA_CALLUP,
    XFA_HORIZON,
    XFA_PAYOUT_LIMIT,
    FunnelError,
    Policy,
    UnsupportedRule,
    day_step,
    integer_contracts,
    run_attempt,
    run_xfa,
    tier_cap,
)
from prop_econ.rules import apply_readings, size_rules
from prop_econ.types import ProductSpec
from prop_econ.vec import simulate_attempts, simulate_xfas
from tests.test_prop_econ_fixtures import (
    NQ,
    ZN,
    hand_book,
    hand_rules,
    make_shocks,
    pad_shocks,
    unit_shocks,
)

CENT = 0.005


def xfa_policy(**kw) -> Policy:
    return Policy(**{"f": 0.25, "xfa_max_days": 6, **kw})


def attempt_policy(**kw) -> Policy:
    return Policy(**{"f": 0.25, "attempt_max_days": 6, **kw})


def both_xfa(shocks, rules, policy):
    """Scalar outcome with its day trace, after checking the vectorized pool agrees (the path is
    padded with zero days up to the horizon)."""
    shocks = pad_shocks(shocks, policy.xfa_max_days)
    out = run_xfa(shocks, 0, rules, policy, trace=True)
    pool = simulate_xfas(shocks, rules, policy)
    assert pool.n_payouts[0] == out.n_payouts and pool.end_day[0] == out.end_day
    assert pool.end_reason[0] == out.end_reason
    assert pool.end_balance[0] == pytest.approx(out.end_balance, abs=1e-9)
    assert list(pool.payout_days[0, :out.n_payouts]) == list(out.payout_days)
    return out


def both_attempt(shocks, rules, policy):
    shocks = pad_shocks(shocks, policy.attempt_max_days)
    out = run_attempt(shocks, 0, rules, policy, trace=True)
    pool = simulate_attempts(shocks, rules, policy)
    assert (bool(pool.passed[0]), int(pool.length[0]), int(pool.reason[0])) == \
        (out.passed, out.length, out.reason)
    return out


# ------------------------------------------------- (1) a Combine pass then an XFA payout ----
def test_combine_pass_then_xfa_payout_to_the_cent():
    rules = hand_rules()
    # Combine, f 0.25, NQ (full sigma 1000, micro sigma 100, micro RT 1), zero edge, k 1.
    # Days 0-2: D 2000 (the floor trails), s* 500 < 1000 -> micro, n 5:
    #   close = 5 x 100 x 2.0 - 5 x 1 = 995, worst = 5 x 100 x -0.5 - 5 = -255.
    #   B 995 / F -1005, B 1990 / F -10, B 2985 / F 0 (floor capped at the start balance).
    # Day 3: D 2985, s* 746.25, n 7.4625, close 746.25 x 1.0 - 7.4625 = 738.7875, B 3723.7875
    #   >= 3000 and best day 995 <= 0.5 x B: pass after 4 days.
    shocks = make_shocks([[2.0, 2.0, 2.0, 1.0, 0, 0]], [[-0.5] * 6])
    att = both_attempt(shocks, rules, attempt_policy())
    assert (att.passed, att.length, att.reason) == (True, 4, ATTEMPT_PASS)
    assert [d.pnl for d in att.days[:3]] == [995.0, 995.0, 995.0]
    assert [d.floor_close for d in att.days] == [-1005.0, -10.0, 0.0, 0.0]
    assert att.days[3].contracts == pytest.approx(7.4625, abs=1e-12)
    assert att.days[3].balance_close == pytest.approx(3723.7875, abs=1e-9)

    # XFA, standard path: days 0-4 at z 0.5: n 5 micros, close 5 x 50 - 5 = 245 (a winning day
    # >= 150); B 1225, F -775. Start of day 5: 5 winning days, B > 0 -> request
    # min(2000, 0.5 x 1225, 1225) = 612.50; B 612.50, floor -> 0 for good; user gets 551.25.
    # Day 5: D 612.5, s* 153.125, n 1.53125 micros, z 0: pnl -1.53125, B 610.96875; horizon 6.
    shocks = make_shocks([[0.5] * 5 + [0.0]], [[-0.1] * 6])
    out = both_xfa(shocks, rules, xfa_policy())
    assert out.payout_days == (5,) and out.payout_gross == (612.50,)
    assert out.total_gross == 612.50 and out.first_payout_day == 5
    assert rules.glob.profit_split_trader * out.payout_gross[0] == pytest.approx(551.25, abs=1e-12)
    day5 = out.days[5]
    assert (day5.balance_open, day5.floor_open, day5.cap_minis) == (612.5, 0.0, 2)
    assert day5.contracts == pytest.approx(1.53125, abs=1e-12)
    assert (out.end_reason, out.end_day) == (XFA_HORIZON, 6)
    assert out.end_balance == pytest.approx(610.96875, abs=1e-9)


# ----------------------------------------------------------------- Combine rules ----
def test_combine_breach_is_a_fail_with_length_counting_the_breach_day():
    # +500 (B 500, F -1500), then worst -2000 <= -D_open = -(500 + 1500): breach on day 2
    out = both_attempt(unit_shocks([500, 300], [0, -2000]), hand_rules(), attempt_policy())
    assert (out.passed, out.length, out.reason) == (False, 2, ATTEMPT_BREACH)
    assert out.days[1].pnl == -2000.0 and out.days[1].breach


def test_combine_min_trading_days_and_timeout():
    rules = hand_rules()
    no_cons = dataclasses.replace(rules, combine=dataclasses.replace(rules.combine,
                                                                     consistency_type="none"))
    out = both_attempt(unit_shocks([3000, 0, 0]), no_cons, attempt_policy(attempt_max_days=3))
    assert (out.passed, out.length) == (True, 2)  # B 3000 on day 1 but only one day traded
    out = both_attempt(unit_shocks([100, 100, 100]), no_cons, attempt_policy(attempt_max_days=3))
    assert (out.passed, out.length, out.reason) == (False, 3, ATTEMPT_TIMEOUT)


@pytest.mark.parametrize("inclusive, length", [(True, 2), (False, 3)])
def test_combine_best_day_frac_of_profit_inclusive_and_strict(inclusive, length):
    # 1500, 1500: B 3000, best 1500 = 0.5 x 3000 -> passes only when inclusive; +1 -> 1500 < 1500.5
    rules = hand_rules(combine_consistency_inclusive=inclusive)
    out = both_attempt(unit_shocks([1500, 1500, 1, 0]), rules, attempt_policy())
    assert (out.passed, out.length) == (True, length)


@pytest.mark.parametrize("inclusive, length", [(True, 4), (False, 5)])
def test_combine_best_day_frac_of_target_raises_the_target(inclusive, length):
    # best day 2000 at frac 0.5 -> effective target max(3000, 4000) = 4000 (strict: B > 4000)
    base = hand_rules(combine_consistency_inclusive=inclusive)
    rules = dataclasses.replace(base, combine=dataclasses.replace(
        base.combine, consistency_type="best_day_max_frac_of_target"))
    out = both_attempt(unit_shocks([2000, 500, 500, 1000, 1, 0]), rules, attempt_policy())
    assert (out.passed, out.length) == (True, length)


def test_combine_floor_trails_to_the_start_balance_and_stays():
    # +1000 (F -1000), +1000 (F 0), +500 (F stays 0), -1500 (B 1000, F 0), worst -1000: breach
    out = both_attempt(unit_shocks([1000, 1000, 500, -1500, 200], [0, 0, 0, -1500, -1000]),
                       hand_rules(), attempt_policy())
    assert [d.floor_close for d in out.days[:4]] == [-1000.0, 0.0, 0.0, 0.0]
    assert (out.reason, out.length) == (ATTEMPT_BREACH, 5)
    assert out.days[4].pnl == -1000.0


def test_combine_dll_applies_when_chosen():
    # Lead 17:30: the DLL chosen at checkout applies in the Combine at combine.dll_option_usd.
    shocks = unit_shocks([500, 0], [-1200, 0])
    on = both_attempt(shocks, hand_rules(), attempt_policy(dll_chosen=True, attempt_max_days=2))
    off = both_attempt(shocks, hand_rules(), attempt_policy(attempt_max_days=2))
    assert on.days[0].dll_stop and on.days[0].pnl == -1000.0
    assert not off.days[0].dll_stop and off.days[0].pnl == 500.0


# ---------------------------------------------------------------- daily step ----
def test_intraday_mll_breach_through_w_with_a_positive_close():
    rules = hand_rules()
    breach = both_xfa(unit_shocks([800, 0], [-2000, 0]), rules, xfa_policy(xfa_max_days=2))
    assert (breach.end_reason, breach.end_day, breach.end_balance) == (XFA_BREACH, 1, -2000.0)
    assert breach.days[0].pnl == -2000.0  # liquidated at the floor despite the +800 close
    alive = both_xfa(unit_shocks([800, 0], [-1999.99, 0]), rules, xfa_policy(xfa_max_days=2))
    assert alive.days[0].pnl == 800.0 and alive.end_reason == XFA_HORIZON


def test_dll_stop_is_flat_not_a_breach_and_yields_to_the_mll_when_dll_ge_d():
    rules = hand_rules()
    # day 0: worst -1200 <= -1000 < D 2000 -> DLL stop at -1000 (B -1000, F -2000)
    # day 1: D 1000, DLL 1000 not < D -> no DLL; worst -999 > -1000 -> close +100 (B -900)
    # day 2: D 1100, worst -1050 -> DLL stop (B -1900); day 3: D 100, worst -150 -> MLL breach
    shocks = unit_shocks([500, 100, 300, 50], [-1200, -999, -1050, -150])
    out = both_xfa(shocks, rules, xfa_policy(dll_chosen=True, xfa_max_days=4))
    assert [d.pnl for d in out.days] == [-1000.0, 100.0, -1000.0, -100.0]
    assert [d.dll_stop for d in out.days] == [True, False, True, False]
    assert (out.end_reason, out.end_day, out.end_balance) == (XFA_BREACH, 4, -2000.0)
    no_dll = both_xfa(shocks, rules, xfa_policy(xfa_max_days=4))
    assert no_dll.days[0].pnl == 500.0  # same day without the DLL: worst -1200 > -2000


def test_vehicle_switch_lot_cap_and_minimum_one_contract():
    pol = Policy(f=0.5)
    full = day_step(0.0, -2000.0, NQ, 1.0, -0.5, pol, 5, None)  # s* 1000 >= 1000: full, n 1
    assert (full.full_size, full.contracts, full.pnl) == (True, 1.0, 1000.0 - 4.0)
    micro = day_step(0.0, -2000.0, NQ, 1.0, -0.5, Policy(f=0.4), 5, None)  # s* 800: 8 micros
    assert (micro.full_size, micro.contracts, micro.pnl) == (False, 8.0, 800.0 - 8.0)
    tiny = day_step(0.0, -2000.0, NQ, 1.0, -0.5, Policy(f=0.04), 5, None)  # s* 80: n 0.8 -> 1
    assert (tiny.full_size, tiny.contracts) == (False, 1.0)
    no_micro = day_step(0.0, -2000.0, ZN, 1.0, -0.5, Policy(f=0.1), 5, None)  # ZN: full, n 1
    assert (no_micro.full_size, no_micro.contracts) == (True, 1.0)
    capped = day_step(0.0, -20000.0, NQ, 1.0, -0.1, Policy(f=0.5), 3, None)  # s* 10000: n 10 -> 3
    assert (capped.full_size, capped.contracts) == (True, 3.0)


def test_integer_mode_floors_and_strips_float_noise():
    pol = Policy(f=0.37, mode="integer")
    out = day_step(0.0, -2000.0, NQ, 1.0, -0.5, pol, 5, None)  # s* 740 -> 7.4 micros -> 7
    assert out.contracts == 7.0 and out.pnl == 7 * 100.0 - 7 * 1.0
    assert integer_contracts(2.9999999999999996) == 3.0
    assert integer_contracts(2.99999) == 2.0
    low = day_step(0.0, -2000.0, NQ, 1.0, -0.5, Policy(f=0.04, mode="integer"), 5, None)
    assert low.contracts == 1.0  # floor 0 -> n >= 1


def test_sharpe_edge_adds_drift_net_of_costs_and_k_round_trips():
    s = 0.5
    pol = Policy(f=0.4, edge="sharpe", sharpe=s, k=3)
    out = day_step(0.0, -2000.0, NQ, 0.0, -0.5, pol, 5, None)  # 8 micros
    # net close = n x sigma x (z + S/sqrt(252)); worst = n x sigma x w - n x k x rt
    assert out.pnl == pytest.approx(8 * 100.0 * s / np.sqrt(252.0), abs=1e-9)
    zero = day_step(0.0, -2000.0, NQ, 0.0, -0.5, Policy(f=0.4, k=3), 5, None)
    assert zero.pnl == -8 * 3 * 1.0


@pytest.mark.parametrize("boundary, cap", [("lower", 2), ("upper", 3)])
def test_lot_cap_reads_the_prior_close_tier_with_each_boundary_reading(boundary, cap):
    book = hand_book()
    if boundary == "upper":
        book = apply_readings(book, {"sizes.50K.xfa.scaling_boundary": "upper"})
    rules = size_rules(book, "50K")
    s_prod = ProductSpec("S", 100.0, 0.0, None, None, None)
    # f 0.5, D 2000 -> s* 1000 -> n 10, cut to the tier: 2 minis below 1500
    # z 3.75: 2 x 375 = 750 a day -> close 1500 exactly after day 1
    shocks = make_shocks([[3.75, 3.75, 0.0]], [[0.0, 0.0, -0.01]], products=(s_prod,))
    out = both_xfa(shocks, rules, xfa_policy(f=0.5, xfa_max_days=3))
    assert [d.cap_minis for d in out.days] == [2, 2, cap]
    assert out.days[2].contracts == float(cap)
    assert tier_cap(1500.0, rules.xfa.scaling, boundary) == cap


def test_tier_uses_the_balance_at_the_prior_close_not_after_a_morning_payout():
    # five +480 days: close 2400 (tier 5); payout 1200 at the start of day 5 leaves 1200 (tier 2)
    out = both_xfa(unit_shocks([480] * 5 + [0]), hand_rules(), xfa_policy())
    assert out.payout_gross == (1200.0,)
    assert (out.days[5].balance_open, out.days[5].cap_minis) == (1200.0, 5)


# ----------------------------------------------------------- (3) drawdown lock ----
def test_xfa_floor_trails_to_the_lock_and_stays():
    out = both_xfa(unit_shocks([1000, 1000, 500, -1500, 200], [0, 0, 0, -1500, -1000]),
                   hand_rules(), xfa_policy(xfa_max_days=5))
    assert [d.floor_close for d in out.days[:4]] == [-1000.0, 0.0, 0.0, 0.0]
    assert (out.end_reason, out.end_day, out.end_balance) == (XFA_BREACH, 5, 0.0)


@pytest.mark.parametrize("after_first, breached", [(0.0, True), (None, False)])
def test_floor_after_the_first_payout(after_first, breached):
    # five +200 days: B 1000, F -1000; payout min(2000, 500, 1000) = 500 -> B 500.
    # floor set to 0 for good: D 500 and worst -500 breaches; null keeps F -1000 (D 1500).
    base = hand_rules()
    rules = dataclasses.replace(base, xfa=dataclasses.replace(
        base.xfa, mll_after_first_payout_usd=after_first))
    out = both_xfa(unit_shocks([200] * 5 + [100], [0] * 5 + [-500]), rules, xfa_policy())
    assert out.payout_gross == (500.0,)
    assert out.days[5].floor_open == (0.0 if after_first is not None else -1000.0)
    assert (out.end_reason == XFA_BREACH) is breached
    assert out.end_balance == (0.0 if breached else 600.0)


# --------------------------------------------------- (4) payouts and refusals ----
def test_standard_refusal_too_few_winning_days_then_payout():
    # 200, 150 (counts: >= 150), 200, 200, 100 (does not), 200: 4 winning days at the start of
    # day 5, 5 at the start of day 6 -> min(2000, 0.5 x 1050, 1050) = 525.00
    out = both_xfa(unit_shocks([200, 150, 200, 200, 100, 200, 0]), hand_rules(),
                   xfa_policy(xfa_max_days=7))
    assert (out.payout_days, out.payout_gross) == ((6,), (525.0,))


def test_consistency_payout():
    # 3 traded days, net 900, best 300 <= 0.4 x 900 -> min(3000, 450, 900) = 450 at day 3
    out = both_xfa(unit_shocks([300, 300, 300, 0]), hand_rules(),
                   xfa_policy(payout_path="consistency", xfa_max_days=4))
    assert (out.payout_days, out.payout_gross) == ((3,), (450.0,))


def test_consistency_refusal_on_the_40_percent_rule():
    # 500, 200, 200: best 500 > 0.4 x 900; +200: 500 > 440; +300: 500 <= 560 -> 700 at day 5
    out = both_xfa(unit_shocks([500, 200, 200, 200, 300, 0]), hand_rules(),
                   xfa_policy(payout_path="consistency"))
    assert (out.payout_days, out.payout_gross) == ((5,), (700.0,))


@pytest.mark.parametrize("inclusive, paid", [(True, True), (False, False)])
def test_consistency_boundary_inclusive_or_strict(inclusive, paid):
    # best 400 = 0.4 x 1000 exactly: <= pays, < refuses (global.xfa_consistency_inclusive)
    out = both_xfa(unit_shocks([400, 300, 300, 0]), hand_rules(xfa_consistency_inclusive=inclusive),
                   xfa_policy(payout_path="consistency", xfa_max_days=4))
    assert out.payout_days == ((3,) if paid else ())


def test_refusal_below_the_minimum_request_then_payout():
    # keep-D 0.5: five +220 days, B 1100 -> min(2000, 550, 1100 - 1000) = 100 < 125: refused;
    # +100 -> B 1200 -> min(2000, 600, 200) = 200 requested at day 6
    out = both_xfa(unit_shocks([220] * 5 + [100, 0]), hand_rules(),
                   xfa_policy(keep_d=0.5, xfa_max_days=7))
    assert (out.payout_days, out.payout_gross) == ((6,), (200.0,))


@pytest.mark.parametrize("counts, second", [(False, (7, 825.0)), (True, (6, 675.0))])
def test_request_day_counts_toward_the_next_window_or_not(counts, second):
    # consistency, +300 a day: payout 450 at day 3 (B 450, F 0). Days 3.. close 750, 1050, 1350,
    # 1650. Not counted: window 4-6 -> 0.5 x 1650 = 825 at day 7; counted: 3-5 -> 675 at day 6.
    rules = hand_rules(payout_day_counts_toward_next_window=counts)
    out = both_xfa(unit_shocks([300] * 8), rules,
                   xfa_policy(payout_path="consistency", xfa_max_days=8))
    assert (out.payout_days[0], out.payout_gross[0]) == (3, 450.0)
    assert (out.payout_days[1], out.payout_gross[1]) == second


def test_dll_doubles_the_payout_cap():
    # five +2000 days: B 10000; standard cap 2000, with the DLL chosen 4000 (0.5 x B = 5000)
    shocks = unit_shocks([2000] * 5 + [0])
    plain = both_xfa(shocks, hand_rules(), xfa_policy())
    dll = both_xfa(shocks, hand_rules(), xfa_policy(dll_chosen=True))
    assert plain.payout_gross[0] == 2000.0 and dll.payout_gross[0] == 4000.0


# ------------------------------------------------------------- ends of an XFA ----
def test_callup_after_n_payouts_ends_right_after_the_payout():
    book = apply_readings(hand_book(), {"global.callup.type": "after_n_payouts",
                                        "global.callup.n": 1}, allow_unlisted=True)
    assert book.unlisted == ("global.callup.n",)
    rules = size_rules(book, "50K")
    out = both_xfa(unit_shocks([200] * 5 + [100]), rules, xfa_policy())
    assert (out.payout_days, out.end_day, out.end_reason, out.end_balance) == \
        ((5,), 5, XFA_CALLUP, 500.0)
    assert len(out.days) == 5  # no trading on the payout day


def test_discretionary_callup_has_no_automatic_trigger():
    doc_callup = {"type": "discretionary", "n": None, "usd": None, "closes_all_xfas": True,
                  "xfa_balance_on_callup": "fixture"}
    out = both_xfa(unit_shocks([200] * 5 + [100]), hand_rules(callup=doc_callup), xfa_policy())
    assert out.end_reason == XFA_HORIZON and out.n_payouts == 1


def test_payout_count_limit_ends_after_that_payout():
    base = hand_rules()
    rules = dataclasses.replace(base, xfa=dataclasses.replace(base.xfa, payout_count_limit=1))
    out = both_xfa(unit_shocks([200] * 5 + [100]), rules, xfa_policy())
    assert (out.end_day, out.end_reason) == (5, XFA_PAYOUT_LIMIT)


def test_horizon_and_payout_overflow_flag():
    # consistency path, +300 a day: payouts at the start of days 3, 7, 11, 15, 19 (3 window
    # days each, the request day excluded); max_payouts 2 keeps the first two
    rules = hand_rules()
    out = both_xfa(unit_shocks([300] * 20), rules,
                   xfa_policy(payout_path="consistency", xfa_max_days=20, max_payouts=2))
    assert out.n_payouts == 5 and out.overflow and len(out.payout_days) == 2
    assert out.payout_days == (3, 7) and (out.end_reason, out.end_day) == (XFA_HORIZON, 20)
    pool = simulate_xfas(unit_shocks([300] * 20), rules,
                         xfa_policy(payout_path="consistency", xfa_max_days=20, max_payouts=2))
    assert pool.overflow[0] and pool.total_gross[0] == pytest.approx(out.total_gross, abs=1e-9)


def test_d_open_not_positive_after_a_payout_raises():
    # frac_of_balance 1.0 and keep-D 0: the payout leaves B 0 = floor (spec: D_open > 0 alive)
    base = hand_rules()
    std = dataclasses.replace(base.xfa.payout_standard, frac_of_balance=1.0)
    rules = dataclasses.replace(base, xfa=dataclasses.replace(base.xfa, payout_standard=std))
    with pytest.raises(FunnelError):
        run_xfa(unit_shocks([200] * 6), 0, rules, xfa_policy())
    with pytest.raises(FunnelError):
        simulate_xfas(unit_shocks([200] * 6), rules, xfa_policy())


def test_unsupported_rules_raise():
    base = hand_rules()
    intraday = dataclasses.replace(base, xfa=dataclasses.replace(base.xfa, mll_trail="intraday"))
    with pytest.raises(UnsupportedRule):
        run_xfa(unit_shocks([0] * 6), 0, intraday, xfa_policy())
    callup = {"type": "payout_total_usd", "n": None, "usd": 5000.0, "closes_all_xfas": None,
              "xfa_balance_on_callup": "fixture"}
    with pytest.raises(UnsupportedRule):
        run_xfa(unit_shocks([0] * 6), 0, hand_rules(callup=callup), xfa_policy())
    limit = dataclasses.replace(base, glob=dataclasses.replace(base.glob,
                                                               combine_time_limit_days=30))
    with pytest.raises(UnsupportedRule):
        run_attempt(unit_shocks([0] * 6), 0, limit, attempt_policy())


def test_policy_validation():
    for bad in ({"f": 0.0}, {"f": 0.1, "mode": "x"}, {"f": 0.1, "edge": "zero", "sharpe": 0.5},
                {"f": 0.1, "k": 0}, {"f": 0.1, "keep_d": -1.0}, {"f": 0.1, "xfa_max_days": 0}):
        with pytest.raises(ValueError):
            Policy(**bad)
    with pytest.raises(ValueError):
        run_xfa(unit_shocks([0] * 3), 0, hand_rules(), xfa_policy())  # 3 days < horizon 6


def test_dll_equal_to_d_open_is_a_tie_read_as_mll_despite_float_noise():
    # Found by the vec-vs-scalar grid: after a DLL stop from the trailing peak, D_open = MLL - DLL
    # = 1000 = DLL in exact arithmetic but 1000.0000000000001 in floats. The MLL must govern.
    peak = 123.456  # close balance at the peak; the floor trailed to peak - 2000
    balance, floor = peak - 1000.0, peak - 2000.0  # then a DLL stop
    assert balance - floor > 1000.0  # 1000.0000000000001: the float noise this test is about
    out = day_step(balance, floor, NQ, 0.1, -3.0, Policy(f=0.5, dll_chosen=True), 2, 1000.0)
    assert out.breach and not out.dll_stop and out.pnl == -(balance - floor)
