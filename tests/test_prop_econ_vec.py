"""Stage E.19: the vectorized funnel (prop_econ/vec.py) equals the scalar reference, path for
path."""

from __future__ import annotations

import dataclasses
import itertools
from pathlib import Path

import numpy as np
import pytest

from prop_econ.funnel import Policy, run_attempt, run_xfa
from prop_econ.rules import apply_readings, load_rules, size_rules
from prop_econ.vec import AttemptPool, XfaPool, simulate_attempts, simulate_xfas
from tests.test_prop_econ_fixtures import hand_book, hand_rules, random_shocks

FINAL_RULES = Path(__file__).resolve().parents[1] / "reports" / "stage_e19_rules.json"
DAYS = 80


def assert_attempts_match(shocks, rules, policy, pool: AttemptPool) -> None:
    for i in range(shocks.n_paths):
        ref = run_attempt(shocks, i, rules, policy)
        got = (bool(pool.passed[i]), int(pool.length[i]), int(pool.reason[i]))
        assert got == (ref.passed, ref.length, ref.reason), f"attempt row {i}"


def assert_xfas_match(shocks, rules, policy, pool: XfaPool) -> None:
    for i in range(shocks.n_paths):
        ref = run_xfa(shocks, i, rules, policy)
        k = len(ref.payout_days)
        assert int(pool.n_payouts[i]) == ref.n_payouts, f"xfa row {i}"
        assert list(pool.payout_days[i, :k]) == list(ref.payout_days)
        assert np.all(pool.payout_days[i, k:] == -1)
        np.testing.assert_allclose(pool.payout_gross[i, :k], ref.payout_gross, atol=1e-9, rtol=0)
        assert pool.total_gross[i] == pytest.approx(ref.total_gross, abs=1e-9)
        assert int(pool.first_payout_day[i]) == ref.first_payout_day
        assert (int(pool.end_day[i]), int(pool.end_reason[i])) == (ref.end_day, ref.end_reason)
        assert pool.end_balance[i] == pytest.approx(ref.end_balance, abs=1e-9)
        assert bool(pool.overflow[i]) == ref.overflow


GRID = [
    {"payout_path": path, "dll_chosen": dll, "mode": mode, "edge": edge, "sharpe": s, "k": k,
     "f": f}
    for (path, dll, mode, (edge, s, k)), f in zip(
        itertools.product(("standard", "consistency"), (False, True), ("continuous", "integer"),
                          (("zero", 0.0, 1), ("zero", 0.0, 3), ("sharpe", 0.5, 1))),
        itertools.cycle((0.05, 0.25, 0.5)), strict=False)
]


@pytest.mark.parametrize("kw", GRID, ids=lambda kw: "-".join(str(v) for v in kw.values()))
def test_vectorized_equals_scalar_over_the_grid(kw):
    shocks = random_shocks(40, DAYS, seed=GRID.index(kw))  # fixed seed per grid point
    rules = hand_rules()
    policy = Policy(attempt_max_days=DAYS, xfa_max_days=DAYS, max_payouts=3, **kw)
    assert_attempts_match(shocks, rules, policy, simulate_attempts(shocks, rules, policy, chunk=13))
    assert_xfas_match(shocks, rules, policy, simulate_xfas(shocks, rules, policy, chunk=13))


def _variant_rules(name: str):
    base = hand_rules()
    if name == "upper_boundary":
        return size_rules(apply_readings(hand_book(), {"sizes.50K.xfa.scaling_boundary": "upper"}),
                          "50K")
    if name == "strict_consistency":
        return hand_rules(combine_consistency_inclusive=False, xfa_consistency_inclusive=False)
    if name == "request_day_counts":
        return hand_rules(payout_day_counts_toward_next_window=True)
    if name == "callup_after_2":
        book = apply_readings(hand_book(), {"global.callup.type": "after_n_payouts",
                                            "global.callup.n": 2}, allow_unlisted=True)
        return size_rules(book, "50K")
    if name == "floor_keeps_trailing":
        return dataclasses.replace(base, xfa=dataclasses.replace(
            base.xfa, mll_after_first_payout_usd=None))
    if name == "frac_of_target_and_no_net_rule":
        std = dataclasses.replace(base.xfa.payout_standard, net_positive_since_last=False)
        return dataclasses.replace(
            base, combine=dataclasses.replace(base.combine,
                                              consistency_type="best_day_max_frac_of_target"),
            xfa=dataclasses.replace(base.xfa, payout_standard=std))
    raise AssertionError(name)


@pytest.mark.parametrize("name", ["upper_boundary", "strict_consistency", "request_day_counts",
                                  "callup_after_2", "floor_keeps_trailing",
                                  "frac_of_target_and_no_net_rule"])
@pytest.mark.parametrize("path", ["standard", "consistency"])
def test_vectorized_equals_scalar_on_rule_variants(name, path):
    rules = _variant_rules(name)
    shocks = random_shocks(40, DAYS, seed=7)
    for f, keep_d, dll in ((0.25, 0.0, False), (0.5, 0.5, True)):
        policy = Policy(f=f, edge="sharpe", sharpe=1.0, keep_d=keep_d, dll_chosen=dll,
                        payout_path=path, attempt_max_days=DAYS, xfa_max_days=DAYS)
        assert_attempts_match(shocks, rules, policy, simulate_attempts(shocks, rules, policy))
        assert_xfas_match(shocks, rules, policy, simulate_xfas(shocks, rules, policy))


def test_chunking_does_not_change_results():
    shocks = random_shocks(50, DAYS, seed=3)
    rules = hand_rules()
    policy = Policy(f=0.25, edge="sharpe", sharpe=0.75, attempt_max_days=DAYS, xfa_max_days=DAYS)
    a1, a2 = (simulate_attempts(shocks, rules, policy, chunk=c) for c in (7, 1000))
    x1, x2 = (simulate_xfas(shocks, rules, policy, chunk=c) for c in (7, 1000))
    for field in dataclasses.fields(AttemptPool):
        np.testing.assert_array_equal(getattr(a1, field.name), getattr(a2, field.name))
    for field in dataclasses.fields(XfaPool):
        np.testing.assert_array_equal(getattr(x1, field.name), getattr(x2, field.name))


@pytest.mark.skipif(not FINAL_RULES.exists(), reason="FINAL rules file not written yet")
@pytest.mark.parametrize("size", ["50K", "100K", "150K"])
def test_final_rules_smoke_both_phases(size):
    """Load reports/stage_e19_rules.json and run a few paths through both phases (DLL on and off,
    both payout paths), vectorized against the scalar reference."""
    rules = size_rules(load_rules(FINAL_RULES), size)
    shocks = random_shocks(12, 60, seed=11)
    for path, dll in itertools.product(("standard", "consistency"), (False, True)):
        policy = Policy(f=0.25, edge="sharpe", sharpe=0.5, dll_chosen=dll, payout_path=path,
                        attempt_max_days=60, xfa_max_days=60)
        assert_attempts_match(shocks, rules, policy, simulate_attempts(shocks, rules, policy))
        assert_xfas_match(shocks, rules, policy, simulate_xfas(shocks, rules, policy))
