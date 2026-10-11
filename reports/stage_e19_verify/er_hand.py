"""EconReviewer Phase A item 3: hand-built deterministic paths against prop_econ's scalar reference.

Each path's expected values are derived by hand from sim_spec.md sections 2 to 5 and the FINAL 50K rules
(MLL 2000, target 3000, Combine consistency best < 0.55 B, XFA standard payout 5 winning days >= 150 and
cap 2000, consistency 3 traded days / best <= 0.4 net / cap 3000, 50% of balance, min request 125, floor
lock 0, floor 0 after the first payout, P = R = 49, activation 149, 21-day billing, split 0.9).
Hand product: sigma_full 1000, rt_full 10, micro sigma 100, rt 2 (a test fixture, not a Topstep number).
Sizing f = 0.10, zero edge, k = 1, mode continuous, DLL off.

Checks are to the cent (|diff| < 0.005) for dollars and exact for days and counts. Results go to
reports/stage_e19_verify/hand_paths.json and hand_paths.log.
"""
from __future__ import annotations

import json
import math
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
sys.path.insert(0, str(REPO))
from prop_econ.assemble import (  # noqa: E402
    KIND_ACTIVATION, KIND_REBILL, KIND_RESET, KIND_START, assemble_cycle, fee_terms)
from prop_econ.funnel import (  # noqa: E402
    ATTEMPT_PASS, XFA_BREACH, Policy, run_attempt, run_xfa)
from prop_econ.rules import load_rules, size_rules  # noqa: E402
from prop_econ.types import ProductSpec, ShockSet  # noqa: E402
from prop_econ.vec import AttemptPool, XfaPool  # noqa: E402

OUT = REPO / "reports" / "stage_e19_verify"
SPEC = ProductSpec("HAND", 1000.0, 10.0, "MHAND", 100.0, 2.0)
RULES = size_rules(load_rules(REPO / "reports" / "stage_e19_rules.json"), "50K")
F = 0.10
LOGL: list[str] = []
RESULTS: dict[str, dict] = {}


def shocks(days: list[tuple[float, float]]) -> ShockSet:
    z = np.array([[d[0] for d in days]]); w = np.array([[d[1] for d in days]])
    return ShockSet(z, w, np.zeros(z.shape, dtype=np.int16), (SPEC,))


def cent(a: float, b: float) -> bool:
    return abs(a - b) < 0.005


def record(name: str, checks: dict[str, tuple], trace=None) -> None:
    ok = all(c[0] for c in checks.values())
    RESULTS[name] = {"all_ok": ok, "checks": {k: {"ok": c[0], "expected": c[1], "got": c[2]}
                                              for k, c in checks.items()}}
    LOGL.append(f"== {name}: {'OK' if ok else 'FAIL'}")
    for k, c in checks.items():
        LOGL.append(f"   {'ok ' if c[0] else 'BAD'} {k}: expected {c[1]} got {c[2]}")
    if trace:
        for row in trace:
            LOGL.append("   trace " + json.dumps(asdict(row)))


def micro_pnl(d_open: float, z: float, n_floor_one: bool = True) -> tuple[float, float]:
    """Hand daily step for the micro vehicle: n = max(f D / 100, 1); close = n (100 z) - n 2."""
    n = max(F * d_open / 100.0, 1.0) if n_floor_one else F * d_open / 100.0
    return n, n * 100.0 * z - n * 2.0


# ---------------------------------------------------------------- A: a pass, then a payout
def path_a() -> None:
    # Combine: day 1 z 8.0 -> n 2, pnl 2*800 - 4 = 1596; day 2 z 7.5 -> n 2 (D back to 2000), pnl 1496
    att = run_attempt(shocks([(8.0, -0.5), (7.5, 0.0)]), 0,
                      RULES, Policy(f=F, attempt_max_days=2), trace=True)
    b2 = 1596.0 + 1496.0  # 3092 >= 3000; best 1596 < 0.55 x 3092 = 1700.6; days 2 >= 2 -> pass
    record("A1_combine_pass", {
        "passed": (att.passed is True, True, att.passed),
        "length": (att.length == 2, 2, att.length),
        "reason_pass": (att.reason == ATTEMPT_PASS, ATTEMPT_PASS, att.reason),
        "day1_pnl": (cent(att.days[0].pnl, 1596.0), 1596.0, att.days[0].pnl),
        "day1_floor_close": (cent(att.days[0].floor_close, -404.0), -404.0, att.days[0].floor_close),
        "day2_balance_close": (cent(att.days[1].balance_close, b2), b2, att.days[1].balance_close),
        "day2_contracts": (cent(att.days[1].contracts, 2.0), 2.0, att.days[1].contracts),
    }, att.days)
    # XFA standard: days 1-5 z 1.0 w -0.5 -> pnl 196 each (D stays 2000: F trails to B - 2000);
    # day 6 start: 5 winning days, B 980 > 0 -> payout floor_cent(min(2000, 490, 980)) = 490; F -> 0;
    # day 6: D 490, n = max(0.49, 1) = 1, z -0.3 -> pnl -30 - 2 = -32 -> B 458 (request day: not in window)
    # day 7: z -5, w -5: worst = -500 - 2 = -502 <= -458 -> breach, pnl -458, B 0
    days = [(1.0, -0.5)] * 5 + [(-0.3, -0.6), (-5.0, -5.0)]
    x = run_xfa(shocks(days), 0, RULES, Policy(f=F, payout_path="standard", xfa_max_days=7), trace=True)
    record("A2_xfa_payout_then_breach", {
        "n_payouts": (x.n_payouts == 1, 1, x.n_payouts),
        "payout_day_index0": (tuple(x.payout_days) == (5,), (5,), tuple(x.payout_days)),
        "payout_gross": (len(x.payout_gross) == 1 and cent(x.payout_gross[0], 490.0), (490.0,), tuple(x.payout_gross)),
        "total_gross": (cent(x.total_gross, 490.0), 490.0, x.total_gross),
        "first_payout_day": (x.first_payout_day == 5, 5, x.first_payout_day),
        "end_day": (x.end_day == 7, 7, x.end_day),
        "end_reason_breach": (x.end_reason == XFA_BREACH, XFA_BREACH, x.end_reason),
        "end_balance": (cent(x.end_balance, 0.0), 0.0, x.end_balance),
        "day5_floor_close": (cent(x.days[4].floor_close, -1020.0), -1020.0, x.days[4].floor_close),
        "day6_balance_open_after_payout": (cent(x.days[5].balance_open, 490.0), 490.0, x.days[5].balance_open),
        "day6_floor_open": (cent(x.days[5].floor_open, 0.0), 0.0, x.days[5].floor_open),
        "day6_contracts_min_one": (cent(x.days[5].contracts, 1.0), 1.0, x.days[5].contracts),
        "day6_pnl": (cent(x.days[5].pnl, -32.0), -32.0, x.days[5].pnl),
        "day7_pnl_breach": (cent(x.days[6].pnl, -458.0), -458.0, x.days[6].pnl),
        "day7_cap_minis_tier_below_1500": (x.days[6].cap_minis == 2, 2, x.days[6].cap_minis),
    }, x.days)


# ---------------------------------------------------------------- B: fail, rebill, reset (credit)
def pools(passed, length, xfa_days=(5,), xfa_gross=(490.0,), end_day=7) -> tuple[AttemptPool, XfaPool]:
    att = AttemptPool(np.array(passed), np.array(length, dtype=np.int32),
                      np.array([ATTEMPT_PASS if p else 0 for p in passed], dtype=np.int8))
    mp = 4
    pd = np.full((1, mp), -1, dtype=np.int32); pg = np.zeros((1, mp))
    pd[0, :len(xfa_days)] = xfa_days; pg[0, :len(xfa_gross)] = xfa_gross
    xfa = XfaPool(pd, pg, np.array([len(xfa_days)], dtype=np.int32), np.array([sum(xfa_gross)]),
                  np.array([xfa_days[0] if xfa_days else -1], dtype=np.int32),
                  np.array([end_day], dtype=np.int32), np.array([XFA_BREACH], dtype=np.int8),
                  np.array([0.0]), np.array([False]))
    return att, xfa


def path_b() -> None:
    terms = fee_terms(RULES, pricing_path="standard", dll_chosen=False, b2f_on=False)
    record("B0_fee_terms", {
        "P": (cent(terms.monthly_usd, 49.0), 49.0, terms.monthly_usd),
        "R": (cent(terms.reset_usd, 49.0), 49.0, terms.reset_usd),
        "activation": (cent(terms.activation_usd, 149.0), 149.0, terms.activation_usd),
        "period_days": (terms.period_days == 21, 21, terms.period_days),
        "split": (cent(terms.split, 0.9), 0.9, terms.split),
        "attempt_cap": (terms.attempt_cap == 60, 60, terms.attempt_cap),
    })
    # B1: attempt 1 fails after 25 days (rebill on its 22nd day adds a credit); reset the next day
    # uses the credit; attempt 2 passes in 10 days (no rebill: 21 days after the reset not reached);
    # activation the day after the pass; XFA pays 490 gross at the start of its 6th day, breaches day 7.
    att, xfa = pools([False, True], [25, 10])
    cyc = assemble_cycle([0, 1] + [1] * 58, [0], att, xfa, terms)
    exp_fees = ((0, 49.0, KIND_START), (21, 49.0, KIND_REBILL), (35, 149.0, KIND_ACTIVATION))
    record("B1_fail_rebill_credit_reset_pass", {
        "fees": (cyc.fees == exp_fees, exp_fees, cyc.fees),
        "credit_resets": (cyc.credit_resets == 1, 1, cyc.credit_resets),
        "purchases": (cyc.purchases == 2, 2, cyc.purchases),
        "fees_total": (cent(cyc.fees_total, 247.0), 247.0, cyc.fees_total),
        "cash": (len(cyc.cash) == 1 and cyc.cash[0][0] == 40 and cent(cyc.cash[0][1], 441.0), ((40, 441.0),), cyc.cash),
        "net": (cent(cyc.net, 194.0), 194.0, cyc.net),
        "end": (cyc.end == 42, 42, cyc.end),
        "n_attempts": (cyc.n_attempts == 2, 2, cyc.n_attempts),
    })
    # B2: attempt 1 fails after 10 days (no rebill, no credit): the reset is paid (R); attempt 2 passes
    # after 25 days: a rebill 21 days after the reset (time 31 < 35) adds a credit that is lost at the pass.
    att, xfa = pools([False, True], [10, 25])
    cyc = assemble_cycle([0, 1] + [1] * 58, [0], att, xfa, terms)
    exp_fees = ((0, 49.0, KIND_START), (10, 49.0, KIND_RESET), (31, 49.0, KIND_REBILL), (35, 149.0, KIND_ACTIVATION))
    record("B2_fail_paid_reset_rebill_pass", {
        "fees": (cyc.fees == exp_fees, exp_fees, cyc.fees),
        "credit_resets": (cyc.credit_resets == 0, 0, cyc.credit_resets),
        "purchases": (cyc.purchases == 3, 3, cyc.purchases),
        "fees_total": (cent(cyc.fees_total, 296.0), 296.0, cyc.fees_total),
        "net": (cent(cyc.net, 145.0), 145.0, cyc.net),
        "end": (cyc.end == 42, 42, cyc.end),
    })
    # B3: the fail's reset day is exactly a rebill day (attempt 1 lasts 21 days): the rebill is paid first
    # and its credit pays the reset (L-17); the clock restarts at the reset.
    att, xfa = pools([False, True], [21, 10])
    cyc = assemble_cycle([0, 1] + [1] * 58, [0], att, xfa, terms)
    exp_fees = ((0, 49.0, KIND_START), (21, 49.0, KIND_REBILL), (31, 149.0, KIND_ACTIVATION))
    record("B3_rebill_on_reset_day", {
        "fees": (cyc.fees == exp_fees, exp_fees, cyc.fees),
        "credit_resets": (cyc.credit_resets == 1, 1, cyc.credit_resets),
        "purchases": (cyc.purchases == 2, 2, cyc.purchases),
        "cash_time": (cyc.cash[0][0] == 36, 36, cyc.cash[0][0]),
        "end": (cyc.end == 38, 38, cyc.end),
    })
    # B4: 60 fails -> the cycle ends with no XFA and no reset after the last fail; each attempt 5 days.
    att, xfa = pools([False], [5])
    cyc = assemble_cycle([0] * 60, [0], att, xfa, terms)
    # resets at 5, 10, ..., 295 (59 of them); rebills: after each reset the clock restarts, so none
    # (every attempt is shorter than 21 days) -> 59 paid resets, 0 credits
    record("B4_attempt_cap", {
        "passed": (cyc.passed is False, False, cyc.passed),
        "n_attempts": (cyc.n_attempts == 60, 60, cyc.n_attempts),
        "purchases": (cyc.purchases == 60, 60, cyc.purchases),
        "fees_total": (cent(cyc.fees_total, 60 * 49.0), 60 * 49.0, cyc.fees_total),
        "cash": (cyc.cash == (), (), cyc.cash),
        "end": (cyc.end == 300, 300, cyc.end),
    })


# ---------------------------------------------------------------- C: floor lock, then floor at 0 after a payout
def path_c() -> None:
    # day 1: z 25, w 0 -> n 2, pnl 4996; F = max(-2000, min(2996, 0)) = 0 (locked at the start balance)
    # day 2: z -2.0, w -2.5 -> n 4.996, pnl -1009.192; F stays 0
    # days 3-6: z 1.0, w -0.1 (four winning days; day 1 was the first) -> 5 winning days after day 6
    # day 7 start: payout floor_cent(min(2000, 0.5 B, B)) = 2000.00; F = 0 (after first payout)
    # day 7: z -12, w -12 -> breach at the floor 0: pnl = -B, end balance 0
    b = 4996.0
    pnls = [4996.0, -1009.192]
    b += -1009.192
    for _ in range(4):
        n, p = micro_pnl(b, 1.0)
        pnls.append(p); b += p
    b_before_payout = b
    b_after = b - 2000.0
    days = [(25.0, 0.0), (-2.0, -2.5)] + [(1.0, -0.1)] * 4 + [(-12.0, -12.0)]
    x = run_xfa(shocks(days), 0, RULES, Policy(f=F, payout_path="standard", xfa_max_days=7), trace=True)
    record("C_floor_lock_then_zero_after_payout", {
        "day1_floor_close_locked_0": (cent(x.days[0].floor_close, 0.0), 0.0, x.days[0].floor_close),
        "day2_pnl": (cent(x.days[1].pnl, -1009.192), -1009.192, x.days[1].pnl),
        "day2_floor_close": (cent(x.days[1].floor_close, 0.0), 0.0, x.days[1].floor_close),
        "day6_balance_close": (cent(x.days[5].balance_close, b_before_payout), b_before_payout, x.days[5].balance_close),
        "day2_cap_minis_tier_top": (x.days[1].cap_minis == 5, 5, x.days[1].cap_minis),
        "payout": (tuple(x.payout_days) == (6,) and cent(x.payout_gross[0], 2000.0), ((6,), 2000.0),
                   (tuple(x.payout_days), tuple(x.payout_gross))),
        "day7_balance_open": (cent(x.days[6].balance_open, b_after), b_after, x.days[6].balance_open),
        "day7_floor_open_0": (cent(x.days[6].floor_open, 0.0), 0.0, x.days[6].floor_open),
        "day7_pnl_breach": (cent(x.days[6].pnl, -b_after), -b_after, x.days[6].pnl),
        "end_balance_0": (cent(x.end_balance, 0.0), 0.0, x.end_balance),
        "end_day": (x.end_day == 7, 7, x.end_day),
        "end_reason_breach": (x.end_reason == XFA_BREACH, XFA_BREACH, x.end_reason),
    }, x.days)


# ---------------------------------------------------------------- D/E: Consistency refusal and acceptance
def path_d() -> None:
    # D: day 1 z 1 -> 196; day 2 z 10 -> 1996 (B 2192, F -> 0); day 3 z 1 -> n 2.192, 214.816 (B 2406.816)
    # day 4 start: traded 3, net 2406.816 > 0, best 1996 > 0.4 x 2406.816 = 962.73 -> REFUSED
    # day 4 z 1 -> n 2.406816, pnl 235.867968 (B 2642.683968); day 5 start refused (best 1996 > 1057.07)
    # day 5 z 12 -> n 2.642683968, pnl 3165.935393664 (B 5808.619361664); day 6 start refused (3165.9 > 2323.4)
    # day 6 z -40 -> breach at F 0: pnl -5808.619361664
    b = 196.0 + 1996.0
    n3, p3 = micro_pnl(b, 1.0); b += p3
    n4, p4 = micro_pnl(b, 1.0); b += p4
    n5, p5 = micro_pnl(b, 12.0); b += p5
    days = [(1.0, -0.5), (10.0, 0.0), (1.0, -0.5), (1.0, -0.5), (12.0, 0.0), (-40.0, -40.0)]
    x = run_xfa(shocks(days), 0, RULES, Policy(f=F, payout_path="consistency", xfa_max_days=6), trace=True)
    record("D_consistency_refusal", {
        "n_payouts_0": (x.n_payouts == 0, 0, x.n_payouts),
        "first_payout_day_-1": (x.first_payout_day == -1, -1, x.first_payout_day),
        "day3_pnl": (cent(x.days[2].pnl, p3), p3, x.days[2].pnl),
        "day4_balance_open_no_payout": (cent(x.days[3].balance_open, 196.0 + 1996.0 + p3), 196.0 + 1996.0 + p3,
                                        x.days[3].balance_open),
        "day5_pnl": (cent(x.days[4].pnl, p5), p5, x.days[4].pnl),
        "day6_pnl_breach": (cent(x.days[5].pnl, -b), -b, x.days[5].pnl),
        "end_day": (x.end_day == 6, 6, x.end_day),
        "end_reason_breach": (x.end_reason == XFA_BREACH, XFA_BREACH, x.end_reason),
        "end_balance_0": (cent(x.end_balance, 0.0), 0.0, x.end_balance),
    }, x.days)
    # E: three equal winning days 196 (best 196 <= 0.4 x 588 = 235.2) -> day 4 payout min(3000, 294, 588) = 294
    # day 4: D 294, n 1, z -3 w -3: worst -302 <= -294 -> breach, pnl -294
    days = [(1.0, -0.5)] * 3 + [(-3.0, -3.0)]
    x = run_xfa(shocks(days), 0, RULES, Policy(f=F, payout_path="consistency", xfa_max_days=4), trace=True)
    record("E_consistency_acceptance", {
        "payout": (tuple(x.payout_days) == (3,) and cent(x.payout_gross[0], 294.0), ((3,), 294.0),
                   (tuple(x.payout_days), tuple(x.payout_gross))),
        "day4_balance_open": (cent(x.days[3].balance_open, 294.0), 294.0, x.days[3].balance_open),
        "day4_floor_open_0": (cent(x.days[3].floor_open, 0.0), 0.0, x.days[3].floor_open),
        "day4_pnl_breach": (cent(x.days[3].pnl, -294.0), -294.0, x.days[3].pnl),
        "end_balance_0": (cent(x.end_balance, 0.0), 0.0, x.end_balance),
        "end_day": (x.end_day == 4, 4, x.end_day),
    }, x.days)
    # E2: the same three days on the STANDARD path must refuse (3 < 5 winning days) and keep trading
    days = [(1.0, -0.5)] * 3 + [(-3.0, -3.0)]
    x = run_xfa(shocks(days), 0, RULES, Policy(f=F, payout_path="standard", xfa_max_days=4), trace=True)
    # day 4: D 2000 (F -1412), n 2, z -3: close -600 - 4 = -604; worst -604 > -2000 -> B = 588 - 604 = -16
    record("E2_standard_refuses_three_days", {
        "n_payouts_0": (x.n_payouts == 0, 0, x.n_payouts),
        "day4_pnl": (cent(x.days[3].pnl, -604.0), -604.0, x.days[3].pnl),
        "end_reason_horizon": (x.end_reason == 3, 3, x.end_reason),
        "end_balance": (cent(x.end_balance, -16.0), -16.0, x.end_balance),
    }, x.days)


def main() -> None:
    path_a(); path_b(); path_c(); path_d()
    n_ok = sum(r["all_ok"] for r in RESULTS.values())
    summary = {"paths": RESULTS, "n_paths": len(RESULTS), "n_ok": n_ok, "all_ok": n_ok == len(RESULTS),
               "rules_file": "reports/stage_e19_rules.json (FINAL, 50K)", "hand_product": asdict(SPEC)}
    (OUT / "hand_paths.json").write_text(json.dumps(summary, indent=1, default=str))
    (OUT / "hand_paths.log").write_text("\n".join(LOGL) + "\n")
    print(f"hand paths: {n_ok}/{len(RESULTS)} OK")
    for name, r in RESULTS.items():
        bad = [k for k, c in r["checks"].items() if not c["ok"]]
        print(f"  {name}: {'OK' if r['all_ok'] else 'FAIL ' + str(bad)}")


if __name__ == "__main__":
    main()
