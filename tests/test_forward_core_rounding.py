"""forward.core rounding: half away from zero, Carver's buffered rounding, the greedy optimiser
and the November 2021 tracking-error buffer (synthetic data only)."""

from __future__ import annotations

import numpy as np
import pytest

from forward import core


@pytest.mark.parametrize("x, expected", [(0.5, 1.0), (1.5, 2.0), (2.5, 3.0), (-0.5, -1.0),
                                         (-1.5, -2.0), (-2.5, -3.0), (0.49, 0.0), (-0.49, 0.0),
                                         (1.2, 1.0), (-1.7, -2.0), (0.0, 0.0)])
def test_round_half_away_from_zero(x, expected):
    assert core.round_half_away(x) == expected


def test_round_half_away_arrays_and_no_negative_zero():
    out = core.round_half_away(np.array([-0.4, 0.5, -2.5]))
    assert out.tolist() == [0.0, 1.0, -3.0]
    assert not np.signbit(out[0])


def test_buffered_round_holds_inside_and_trades_to_the_edge():
    # optimal 2.3, average position 10 -> buffer 1.0: top round(3.3)=3, bottom round(1.3)=1
    assert core.buffered_round(2.3, 10.0, 2.0) == 2.0  # inside: hold
    assert core.buffered_round(2.3, 10.0, 0.0) == 1.0  # below: up to the bottom edge
    assert core.buffered_round(2.3, 10.0, 5.0) == 3.0  # above: down to the top edge
    assert core.buffered_round(-2.3, 10.0, 0.0) == -1.0  # negatives mirror
    assert core.buffered_round(-2.3, 10.0, -5.0) == -3.0
    # halves away from zero at the edges: optimal 0.5, buffer 0 -> 1; -0.5 -> -1
    assert core.buffered_round(0.5, 0.0, 0.0) == 1.0
    assert core.buffered_round(-0.5, 0.0, 0.0) == -1.0


def test_buffered_round_vectorised():
    out = core.buffered_round(np.array([2.3, -2.3]), np.array([10.0, 10.0]), np.array([0.0, 0.0]))
    assert out.tolist() == [1.0, -1.0]


def _cov(n: int, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    a = rng.normal(size=(n, n))
    corr = np.corrcoef(a @ a.T + n * np.eye(n))
    vol = rng.uniform(500, 3000, n)
    return core.covariance(corr, vol)


def test_greedy_output_is_integer():
    rng = np.random.default_rng(5)
    for seed in range(5):
        cov = _cov(6, seed)
        opt = rng.normal(0, 2, 6)
        res = core.greedy_integer(opt, np.zeros(6), cov, np.full(6, 1.0), 25_000, 250.0)
        assert np.all(res.positions == np.round(res.positions))


def test_greedy_never_worse_tracking_error_than_all_zero():
    rng = np.random.default_rng(6)
    for seed in range(10):
        cov = _cov(5, seed)
        opt = rng.normal(0, 1.5, 5)
        res = core.greedy_integer(opt, np.zeros(5), cov, np.full(5, 2.0), 25_000, 250.0)
        te = core.tracking_error(res.positions - opt, cov, 25_000)
        assert te <= core.tracking_error(-opt, cov, 25_000) + 1e-12


def test_greedy_reproduces_an_integer_unrounded_position():
    cov = _cov(4, 1)
    opt = np.array([2.0, -1.0, 3.0, 0.0])
    res = core.greedy_integer(opt, np.zeros(4), cov, np.zeros(4), 25_000, 0.0)
    assert res.positions.tolist() == opt.tolist()


def test_greedy_moves_only_in_the_sign_of_the_optimum():
    cov = _cov(3, 2)
    opt = np.array([1.6, -2.4, 0.2])
    res = core.greedy_integer(opt, np.zeros(3), cov, np.zeros(3), 25_000, 0.0)
    assert res.positions[0] >= 0 and res.positions[1] <= 0 and res.positions[2] >= 0


def test_cost_penalty_reduces_trading():
    cov = _cov(5, 3)
    rng = np.random.default_rng(7)
    prior = np.array([1.0, -1.0, 0.0, 2.0, 0.0])
    opt = prior + rng.normal(0, 1.2, 5)
    cheap = core.greedy_integer(opt, prior, cov, np.full(5, 5.0), 25_000, 0.0)
    dear = core.greedy_integer(opt, prior, cov, np.full(5, 5.0), 25_000, 5000.0)
    assert np.abs(dear.positions - prior).sum() < np.abs(cheap.positions - prior).sum()


def test_dynamic_optimise_no_trade_inside_the_buffer():
    cov = core.covariance(np.eye(2), np.array([100.0, 100.0]))
    prior = np.array([1.0, 0.0])
    opt = np.array([1.2, 0.1])  # TE = sqrt(0.2^2 + 0.1^2) x 100 / 25,000 << 0.0125
    res = core.dynamic_optimise(opt, prior, cov, np.ones(2), 25_000, shadow_cost=250.0,
                                te_buffer=0.0125)
    assert res.stage == "inside buffer"
    assert res.positions.tolist() == prior.tolist()


def test_dynamic_optimise_trades_a_fraction_to_the_buffer_edge():
    # one instrument, $ vol 2,500 per contract at $25K: 1 contract = 10% TE
    cov = core.covariance(np.eye(1), np.array([2500.0]))
    res = core.dynamic_optimise(np.array([4.0]), np.array([0.0]), cov, np.zeros(1), 25_000,
                                shadow_cost=0.0, te_buffer=0.0125)
    # greedy -> 4; x = 0.40; adj = (0.40 - 0.0125) / 0.40 = 0.96875; 3.875 -> 4
    assert res.stage == "traded"
    assert res.adjustment == pytest.approx((0.40 - 0.0125) / 0.40)
    assert res.positions.tolist() == [4.0]


def test_dynamic_optimise_small_trade_rounds_to_zero():
    # $ vol 400 at $25K: one contract is 1.6% TE; adj = (0.016 - 0.0125) / 0.016 = 0.22 -> 0
    cov = core.covariance(np.eye(1), np.array([400.0]))
    res = core.dynamic_optimise(np.array([1.0]), np.array([0.0]), cov, np.zeros(1), 25_000,
                                shadow_cost=0.0, te_buffer=0.0125)
    assert res.stage == "no trade (trades round to 0)"
    assert res.positions.tolist() == [0.0]


def test_dynamic_optimise_accepts_an_all_zero_result():
    cov = core.covariance(np.eye(2), np.array([3000.0, 3000.0]))
    res = core.dynamic_optimise(np.array([0.2, -0.2]), np.array([2.0, -2.0]), cov, np.zeros(2),
                                25_000, shadow_cost=0.0, te_buffer=0.0125)
    assert res.greedy_all_zero
    assert res.positions.tolist() == [0.0, 0.0]


def test_tracking_error_units():
    cov = core.covariance(np.eye(1), np.array([2500.0]))
    assert core.tracking_error(np.array([2.0]), cov, 25_000) == pytest.approx(0.2)


def test_tracking_error_units_match_carvers_weight_space_by_hand():
    # Two instruments, capital 25,000. A: multiplier 2, price 15,000, daily price-difference vol 150
    # (annual % vol 16 x 150 / 15,000 = 0.16); B: multiplier 100, price 80, daily vol 1.6 (0.32);
    # correlation 0.3. Trade gap: +1 A, -2 B.
    # Weight space (the post): dw = contracts x multiplier x price / capital = [1.2, -0.64];
    # Sigma% = [[0.0256, 0.01536], [0.01536, 0.1024]];
    # dw' Sigma% dw = 0.036864 - 0.0235930 + 0.04194304 = 0.05521408 -> TE 0.2349768 (a fraction
    # of capital, annualised), the same units as the buffer b = 0.0125.
    expected = 0.05521408 ** 0.5
    dollar_vol = core.annual_dollar_vol(np.array([150.0, 1.6]), np.array([2.0, 100.0]))
    assert dollar_vol.tolist() == [4800.0, 2560.0]
    cov = core.covariance(np.array([[1.0, 0.3], [0.3, 1.0]]), dollar_vol)
    te = core.tracking_error(np.array([1.0, -2.0]), cov, 25_000)
    assert te == pytest.approx(expected, rel=1e-12)
    # the same through Carver's weights and percentage covariance
    dw = np.array([1.0 * 2 * 15_000, -2.0 * 100 * 80]) / 25_000
    pv = np.array([0.16, 0.32])
    cov_pct = np.array([[1.0, 0.3], [0.3, 1.0]]) * np.outer(pv, pv)
    assert float(np.sqrt(dw @ cov_pct @ dw)) == pytest.approx(expected, rel=1e-12)
    # step 3 uses x in these units: adjustment = (x - b) / x
    res = core.dynamic_optimise(np.array([1.0, -2.0]), np.zeros(2), cov, np.zeros(2), 25_000,
                                shadow_cost=0.0, te_buffer=0.0125)
    assert res.te_prior_rounded == pytest.approx(expected, rel=1e-12)
    assert res.adjustment == pytest.approx((expected - 0.0125) / expected)


def test_dynamic_optimise_labels_integer_optimum_equal_to_current():
    # prior 1 contract, optimum 1.4: TE(prior vs optimum) = 0.4 x 2,500 / 25,000 = 4% > buffer,
    # the greedy's integer optimum is the prior itself (x = 0): no trade
    cov = core.covariance(np.eye(1), np.array([2500.0]))
    res = core.dynamic_optimise(np.array([1.4]), np.array([1.0]), cov, np.zeros(1), 25_000,
                                shadow_cost=0.0, te_buffer=0.0125)
    assert res.stage == "no trade (integer optimum = current)"
    assert res.te_prior_rounded == 0.0 and res.positions.tolist() == [1.0]
