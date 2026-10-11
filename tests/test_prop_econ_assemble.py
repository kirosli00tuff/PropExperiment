"""Stage E.19 fees, cycles and campaigns (prop_econ/assemble.py, sim_spec section 5).

Hand pools: attempts are (passed, length) rows, XFAs are hand payout lists. Fixture prices (hand
rules): P 50 standard / 100 no-activation-fee (DLL discount 10 there), R 40 / 90, activation
150 / 0, Back2Funded 600 (DLL discount 50), split 0.9, billing 30 calendar days = 21 trading days.
"""

from __future__ import annotations

import dataclasses

import numpy as np
import pytest

from prop_econ.assemble import (
    KIND_ACTIVATION,
    KIND_B2F,
    KIND_REBILL,
    KIND_RESET,
    KIND_START,
    CampaignResult,
    assemble_cycle,
    assemble_cycles,
    billing_period_days,
    campaign_quantiles,
    campaign_scalar,
    draw_cycles,
    fee_terms,
    run_campaign,
)
from prop_econ.funnel import ATTEMPT_BREACH, ATTEMPT_PASS, XFA_BREACH, XFA_HORIZON
from prop_econ.vec import AttemptPool, XfaPool
from tests.test_prop_econ_fixtures import hand_rules


def attempt_pool(rows: list[tuple[bool, int]]) -> AttemptPool:
    passed = np.array([p for p, _ in rows], dtype=bool)
    return AttemptPool(passed=passed, length=np.array([n for _, n in rows], dtype=np.int32),
                       reason=np.where(passed, ATTEMPT_PASS, ATTEMPT_BREACH).astype(np.int8))


def xfa_pool(rows: list[dict], max_payouts: int = 4) -> XfaPool:
    """rows: {"payouts": [(day, gross), ...], "end_day": int, "reason": int, "extra": float}
    ("extra" = unrecorded gross beyond max_payouts, which sets overflow)."""
    n = len(rows)
    days = np.full((n, max_payouts), -1, dtype=np.int32)
    gross = np.zeros((n, max_payouts))
    npay, total = np.zeros(n, dtype=np.int32), np.zeros(n)
    for i, row in enumerate(rows):
        pays = row["payouts"]
        for j, (d, g) in enumerate(pays[:max_payouts]):
            days[i, j], gross[i, j] = d, g
        npay[i] = len(pays) + row.get("n_extra", 0)
        total[i] = sum(g for _, g in pays) + row.get("extra", 0.0)
    return XfaPool(payout_days=days, payout_gross=gross, n_payouts=npay, total_gross=total,
                   first_payout_day=np.where(npay > 0, days[:, 0], -1).astype(np.int32),
                   end_day=np.array([r["end_day"] for r in rows], dtype=np.int32),
                   end_reason=np.array([r["reason"] for r in rows], dtype=np.int8),
                   end_balance=np.zeros(n), overflow=npay > max_payouts)


def terms(**kw):
    rules = hand_rules()
    base = fee_terms(rules, pricing_path=kw.pop("pricing_path", "standard"),
                     dll_chosen=kw.pop("dll_chosen", False), b2f_on=kw.pop("b2f_on", False),
                     attempt_cap=kw.pop("attempt_cap", 60))
    return dataclasses.replace(base, **kw)


def rows(att: list[int], xfa: list[int], t) -> tuple[list[int], list[int]]:
    att_row = att + [att[-1]] * (t.attempt_cap - len(att))
    return att_row, xfa + [xfa[-1]] * (1 + t.b2f_max - len(xfa))


def check_vec(att_rows, xfa_rows, attempts, xfas, t) -> None:
    """The vectorized batch equals the scalar cycles row for row."""
    batch = assemble_cycles(np.asarray(att_rows), np.asarray(xfa_rows), attempts, xfas, t)
    for c, (a, x) in enumerate(zip(att_rows, xfa_rows, strict=True)):
        ref = assemble_cycle(a, x, attempts, xfas, t)
        fm, cm = batch.fee_cycle == c, batch.cash_cycle == c
        fees = list(zip(batch.fee_time[fm].tolist(), batch.fee_usd[fm].tolist(),
                        batch.fee_kind[fm].tolist(), strict=True))
        assert fees == list(ref.fees), f"cycle {c}"
        assert batch.cash_time[cm].tolist() == [tm for tm, _ in ref.cash]
        np.testing.assert_allclose(batch.cash_usd[cm], [u for _, u in ref.cash], atol=1e-9)
        assert (batch.end[c], batch.n_attempts[c], bool(batch.passed[c])) == \
            (ref.end, ref.n_attempts, ref.passed)
        assert (batch.purchases[c], batch.credit_resets[c], batch.overflow_xfas[c]) == \
            (ref.purchases, ref.credit_resets, ref.overflow_xfas)
        assert batch.fees_total[c] == pytest.approx(ref.fees_total, abs=1e-9)
        assert batch.cash_total[c] == pytest.approx(ref.cash_total, abs=1e-9)
        assert [r for r in batch.xfa_row[c] if r >= 0] == [x for _, _, x in ref.xfas]
        assert [s for s in batch.xfa_start[c] if s >= 0] == [s for s, _, _ in ref.xfas]


ONE_XFA = xfa_pool([{"payouts": [(5, 612.50)], "end_day": 6, "reason": XFA_HORIZON}])


def test_billing_period_and_fee_terms():
    assert billing_period_days(30) == 21  # 30 x 252 / 365 = 20.7
    t = terms()
    assert (t.monthly_usd, t.reset_usd, t.activation_usd, t.b2f_usd, t.period_days) == \
        (50.0, 40.0, 150.0, 600.0, 21)
    t = terms(pricing_path="no_activation_fee", dll_chosen=True)
    assert (t.monthly_usd, t.reset_usd, t.activation_usd, t.b2f_usd) == (90.0, 90.0, 0.0, 550.0)
    assert terms(dll_chosen=True).monthly_usd == 50.0  # no DLL discount on the standard path


# ------------------------------------------------- (2) a fail and reset, with fees ----
def test_fees_start_rebill_credit_reset_by_credit_and_in_cash():
    # Attempts: fail 30 days, fail 5, fail 10, pass 8; one XFA paying 612.50 on its day 5.
    #   t 0  P 50 (start)            next rebill 21
    #   t 21 P 50 (rebill) +1 credit next 42; attempt 1 ends at 30
    #   t 30 reset paid by the credit; reset pushes the rebill to 51; attempt 2 ends at 35
    #   t 35 reset in cash R 40, rebill -> 56; attempt 3 ends at 45
    #   t 45 reset in cash R 40, rebill -> 66; attempt 4 passes at 53 (no rebill before 53)
    #   t 53 activation 150; XFA payout at 53 + 5 = 58: 0.9 x 612.50 = 551.25; XFA ends at 59
    attempts = attempt_pool([(False, 30), (False, 5), (False, 10), (True, 8)])
    t = terms()
    a, x = rows([0, 1, 2, 3], [0], t)
    cyc = assemble_cycle(a, x, attempts, ONE_XFA, t)
    assert cyc.fees == ((0, 50.0, KIND_START), (21, 50.0, KIND_REBILL), (35, 40.0, KIND_RESET),
                        (45, 40.0, KIND_RESET), (53, 150.0, KIND_ACTIVATION))
    assert (cyc.purchases, cyc.credit_resets, cyc.n_attempts) == (4, 1, 4)
    assert cyc.cash == ((58, pytest.approx(551.25, abs=1e-12)),)
    assert (cyc.end, cyc.fees_total) == (59, 330.0)
    assert cyc.net == pytest.approx(221.25, abs=1e-9)
    check_vec([a], [x], attempts, ONE_XFA, t)


@pytest.mark.parametrize("pushes, times", [(True, [0, 21, 51, 81]), (False, [0, 21, 42, 63, 84])])
def test_rebill_clock_with_and_without_reset_push(pushes, times):
    # fail 30, fail 30, pass 30; every reset is paid by a rebill credit
    attempts = attempt_pool([(False, 30), (True, 30)])
    t = terms(reset_pushes_rebill=pushes)
    a, x = rows([0, 0, 1], [0], t)
    cyc = assemble_cycle(a, x, attempts, ONE_XFA, t)
    assert [tm for tm, _, kind in cyc.fees if kind != KIND_ACTIVATION] == times
    assert cyc.credit_resets == 2 and cyc.purchases == len(times)
    check_vec([a], [x], attempts, ONE_XFA, t)


def test_rebill_due_on_the_reset_day_comes_first_and_its_credit_pays_the_reset():
    attempts = attempt_pool([(False, 21), (True, 5)])
    t = terms()
    a, x = rows([0, 1], [0], t)
    cyc = assemble_cycle(a, x, attempts, ONE_XFA, t)
    assert cyc.fees[:2] == ((0, 50.0, KIND_START), (21, 50.0, KIND_REBILL))
    assert (cyc.credit_resets, cyc.purchases) == (1, 2)
    check_vec([a], [x], attempts, ONE_XFA, t)


def test_rebill_without_credit_leaves_the_reset_in_cash():
    attempts = attempt_pool([(False, 30), (True, 5)])
    t = terms(rebill_adds_credit=False)
    a, x = rows([0, 1], [0], t)
    cyc = assemble_cycle(a, x, attempts, ONE_XFA, t)
    assert [k for _, _, k in cyc.fees] == [KIND_START, KIND_REBILL, KIND_RESET, KIND_ACTIVATION]
    check_vec([a], [x], attempts, ONE_XFA, t)


def test_attempt_cap_ends_the_cycle_with_no_xfa():
    attempts = attempt_pool([(False, 10)])
    t = terms(attempt_cap=3)
    a, x = rows([0], [0], t)
    cyc = assemble_cycle(a, x, attempts, ONE_XFA, t)
    # P at 0, cash resets at 10 and 20, no reset after the third fail; ends at 30
    assert cyc.fees == ((0, 50.0, KIND_START), (10, 40.0, KIND_RESET), (20, 40.0, KIND_RESET))
    assert (cyc.passed, cyc.end, cyc.xfas, cyc.cash, cyc.n_attempts) == (False, 30, (), (), 3)
    check_vec([a], [x], attempts, ONE_XFA, t)


# ------------------------------------------------------------------ Back2Funded ----
B2F_XFAS = xfa_pool([
    {"payouts": [], "end_day": 10, "reason": XFA_BREACH},  # breach before any payout
    {"payouts": [(5, 1000.0)], "end_day": 8, "reason": XFA_BREACH},  # breach after a payout
    {"payouts": [(3, 500.0)], "end_day": 20, "reason": XFA_HORIZON},
])
PASS_10 = attempt_pool([(True, 10)])


@pytest.mark.parametrize("xfa_ids, b2f_on, dll, expect", [
    # breach before a payout -> reactivated at most twice; activation at 10, B2F at 20 and 30
    ([0, 0, 0], True, False, {"n_xfas": 3, "end": 40, "b2f": [(20, 600.0), (30, 600.0)]}),
    ([0, 0, 0], True, True, {"n_xfas": 3, "end": 40, "b2f": [(20, 550.0), (30, 550.0)]}),
    ([0, 0, 0], False, False, {"n_xfas": 1, "end": 20, "b2f": []}),
    # the reactivated XFA breaches after a payout -> no further Back2Funded
    ([0, 1, 0], True, False, {"n_xfas": 2, "end": 28, "b2f": [(20, 600.0)]}),
    ([2, 0, 0], True, False, {"n_xfas": 1, "end": 30, "b2f": []}),
])
def test_back2funded(xfa_ids, b2f_on, dll, expect):
    t = terms(b2f_on=b2f_on, dll_chosen=dll)
    a, x = rows([0], xfa_ids, t)
    cyc = assemble_cycle(a, x, PASS_10, B2F_XFAS, t)
    assert (len(cyc.xfas), cyc.end) == (expect["n_xfas"], expect["end"])
    assert [(tm, usd) for tm, usd, k in cyc.fees if k == KIND_B2F] == expect["b2f"]
    check_vec([a], [x], PASS_10, B2F_XFAS, t)


def test_back2funded_after_a_payout_when_the_rule_allows_it():
    t = terms(b2f_on=True, b2f_before_first_only=False)
    a, x = rows([0], [1, 0, 0], t)
    cyc = assemble_cycle(a, x, PASS_10, B2F_XFAS, t)
    assert [xf for _, _, xf in cyc.xfas] == [1, 0, 0]
    check_vec([a], [x], PASS_10, B2F_XFAS, t)


def test_payout_overflow_remainder_is_credited_at_the_xfa_end():
    xfas = xfa_pool([{"payouts": [(3, 100.0), (7, 200.0)], "n_extra": 1, "extra": 300.0,
                      "end_day": 12, "reason": XFA_HORIZON}], max_payouts=2)
    t = terms()
    a, x = rows([0], [0], t)
    cyc = assemble_cycle(a, x, PASS_10, xfas, t)
    assert [(tm, round(u, 9)) for tm, u in cyc.cash] == [(13, 90.0), (17, 180.0), (22, 270.0)]
    assert cyc.overflow_xfas == 1
    check_vec([a], [x], PASS_10, xfas, t)


# ------------------------------------------------- vectorized equals scalar, seeds ----
def random_pools(seed: int, n_att: int = 300, n_xfa: int = 200, mp: int = 4):
    rng = np.random.default_rng(seed)
    attempts = attempt_pool([(bool(rng.random() < 0.3), int(rng.integers(1, 50)))
                             for _ in range(n_att)])
    xrows = []
    for _ in range(n_xfa):
        k = int(rng.integers(0, mp + 3))
        days = np.sort(rng.choice(np.arange(1, 150), size=k, replace=False))
        pays = [(int(d), float(rng.integers(125, 3000)) + 0.25) for d in days]
        rec, extra = pays[:mp], pays[mp:]
        xrows.append({"payouts": rec, "n_extra": len(extra), "extra": sum(g for _, g in extra),
                      "end_day": int((days.max() if k else 0) + rng.integers(1, 40)),
                      "reason": int(rng.choice([XFA_BREACH, XFA_HORIZON]))})
    return attempts, xfa_pool(xrows, max_payouts=mp)


@pytest.mark.parametrize("variant", [
    {}, {"b2f_on": True}, {"pricing_path": "no_activation_fee", "dll_chosen": True, "b2f_on": True},
    {"reset_pushes_rebill": False}, {"rebill_adds_credit": False, "attempt_cap": 7},
])
def test_vectorized_cycles_equal_scalar_on_random_pools(variant):
    attempts, xfas = random_pools(seed=len(variant))
    t = terms(**variant)
    batch, att, xfa = draw_cycles(np.random.Generator(np.random.PCG64(9)), 400, attempts, xfas, t)
    check_vec(att, xfa, attempts, xfas, t)
    assert batch.n == 400


def test_draws_are_deterministic_by_seed():
    attempts, xfas = random_pools(seed=1)
    t = terms(b2f_on=True)

    def draw(seed):
        return draw_cycles(np.random.Generator(np.random.PCG64(seed)), 200, attempts, xfas, t)

    (b1, a1, x1), (b2, a2, x2), (_, a3, _) = draw(5), draw(5), draw(6)
    np.testing.assert_array_equal(a1, a2)
    np.testing.assert_array_equal(x1, x2)
    np.testing.assert_array_equal(b1.net, b2.net)
    assert not np.array_equal(a1, a3)
    r1, r2 = (run_campaign(attempts, xfas, t, slots=5, max_active_xfas=5, n_reps=50, seed=8)
              for _ in range(2))
    for name in ("reached", "purchases", "days"):
        np.testing.assert_array_equal(getattr(r1, name), getattr(r2, name))
    np.testing.assert_array_equal(r1.fees, r2.fees)


# ------------------------------------------------------------------- campaigns ----
TWO_PAYOUTS = xfa_pool([{"payouts": [(5, 3000.0), (10, 3000.0)], "end_day": 12,
                         "reason": XFA_HORIZON}])


def test_campaign_one_slot_hand_case():
    # cycle 1: P at 0, pass at 10 (activation 150), cash 2700 at 15 and 20, ends at 22;
    # cycle 2: P at 22, activation at 32, cash at 37 and 42.
    # $5,000 at day 20 (1 purchase, fees 200); $10,000 at day 42 (2 purchases, fees 400)
    res = run_campaign(PASS_10, TWO_PAYOUTS, terms(), slots=1, max_active_xfas=5, n_reps=3, seed=1)
    assert res.reached.all()
    assert res.purchases[:, 0].tolist() == [1, 2] and res.fees[:, 0].tolist() == [200.0, 400.0]
    assert res.days[:, 0].tolist() == [20, 42]


def test_campaign_five_slots_hand_case_counts_same_day_purchases():
    # five identical slots: at day 15 five 2700 cash events; 5000 and 10000 are both crossed at
    # day 15 with all five start purchases and activations paid (5 x 200 = 1000)
    res = run_campaign(PASS_10, TWO_PAYOUTS, terms(), slots=5, max_active_xfas=5, n_reps=2, seed=1)
    assert res.purchases[:, 0].tolist() == [5, 5] and res.days[:, 0].tolist() == [15, 15]
    assert res.fees[:, 0].tolist() == [1000.0, 1000.0]


def test_campaign_purchase_cap():
    # cap 1: $5,000 is reached with 1 purchase, $10,000 needs a 2nd -> not reached
    res = run_campaign(PASS_10, TWO_PAYOUTS, terms(), slots=1, max_active_xfas=5, n_reps=2, seed=1,
                       purchase_cap=1)
    assert res.reached[:, 0].tolist() == [True, False]
    assert (res.purchases[1, 0], res.days[1, 0]) == (-1, -1) and np.isnan(res.fees[1, 0])
    # a Combine that never passes: every replication stops at the cap
    never = attempt_pool([(False, 1)])
    res = run_campaign(never, TWO_PAYOUTS, terms(), slots=5, max_active_xfas=5, n_reps=4, seed=2,
                       purchase_cap=100)
    assert not res.reached.any()
    q = campaign_quantiles(res)
    assert q[5000.0]["share_reached"] == 0.0 and q[10000.0]["purchases_p50"] == np.inf


def _max_live(starts: np.ndarray, ends: np.ndarray) -> int:
    events = sorted([(int(e), -1) for e in ends] + [(int(s), 1) for s in starts])
    live = peak = 0
    for _, step in events:  # an XFA ending at t frees its slot before one starting at t
        live += step
        peak = max(peak, live)
    return peak


def test_five_account_cap_in_a_five_slot_campaign():
    attempts = attempt_pool([(True, 3), (False, 4), (True, 6)])
    xfas = xfa_pool([{"payouts": [(5, 4000.0)], "end_day": 200, "reason": XFA_HORIZON},
                     {"payouts": [], "end_day": 30, "reason": XFA_BREACH}])
    t = terms(b2f_on=True)
    res = run_campaign(attempts, xfas, t, slots=5, max_active_xfas=5, n_reps=40, seed=3,
                       targets=(50_000.0,), trace=True)
    tr = res.trace
    peaks = []
    for rep in range(40):
        m = tr.rep == rep
        live = tr.xfa_start[m] >= 0
        peaks.append(_max_live(tr.xfa_start[m][live], tr.xfa_end[m][live]))
        for s in range(5):  # each slot runs its cycles back to back
            ms = m & (tr.slot == s)
            order = np.argsort(tr.order[ms])
            st, en = tr.start[ms][order], tr.end[ms][order]
            assert st[0] == 0 and np.array_equal(st[1:], en[:-1])
    assert max(peaks) == 5 and all(p <= 5 for p in peaks)
    with pytest.raises(ValueError):
        run_campaign(attempts, xfas, t, slots=6, max_active_xfas=5, n_reps=1, seed=1)


@pytest.mark.parametrize("slots", [1, 5])
def test_campaign_equals_the_scalar_reference_on_its_trace(slots):
    attempts, xfas = random_pools(seed=4)
    t = terms(b2f_on=True)
    res = run_campaign(attempts, xfas, t, slots=slots, max_active_xfas=5, n_reps=40, seed=6,
                       rep_chunk=16, trace=True, purchase_cap=60)
    tr = res.trace
    for rep in range(40):
        per_slot = []
        for s in range(slots):
            idx = np.flatnonzero((tr.rep == rep) & (tr.slot == s))
            idx = idx[np.argsort(tr.order[idx])]
            per_slot.append([assemble_cycle(tr.att_idx[i], tr.xfa_idx[i], attempts, xfas, t)
                             for i in idx])
        for ti, (reached, purchases, fees, days) in enumerate(
                campaign_scalar(per_slot, res.targets, res.purchase_cap)):
            assert bool(res.reached[ti, rep]) == reached, (rep, ti)
            assert (int(res.purchases[ti, rep]), int(res.days[ti, rep])) == (purchases, days)
            if reached:
                assert res.fees[ti, rep] == pytest.approx(fees, abs=1e-9)


def test_campaign_quantiles_inverted_cdf_with_not_reached_as_infinite():
    res = CampaignResult(targets=(5000.0,), slots=1, purchase_cap=400,
                         reached=np.array([[True, True, False, True]]),
                         purchases=np.array([[3, 5, -1, 7]]),
                         fees=np.array([[100.0, 200.0, np.nan, 300.0]]),
                         days=np.array([[10, 20, -1, 30]]), cycles_drawn=0, overflow_xfas=0)
    q = campaign_quantiles(res)[5000.0]
    assert q["share_reached"] == 0.75
    assert (q["purchases_p50"], q["fees_p50"], q["days_p50"]) == (5.0, 200.0, 20.0)
    assert q["purchases_p80"] == np.inf
