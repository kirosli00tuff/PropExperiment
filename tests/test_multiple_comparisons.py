"""Known-answer tests for funnel.multiple_comparisons. Expected values hand-computed."""

import math

import pytest

from funnel.multiple_comparisons import (
    EULER_MASCHERONI,
    _norm_cdf,
    _norm_ppf,
    deflated_sharpe_ratio,
    expected_max_sharpe,
    harvey_liu_zhu_verdict,
    probability_of_backtest_overfitting,
)

# ----------------------------------------------------------------- normals ----


def test_norm_cdf_at_zero_is_one_half():
    assert _norm_cdf(0.0) == pytest.approx(0.5, abs=1e-12)


def test_norm_ppf_at_half_is_zero():
    assert _norm_ppf(0.5) == pytest.approx(0.0, abs=1e-9)


def test_norm_ppf_matches_the_textbook_975_quantile():
    # The 97.5th percentile of the standard normal is 1.959963985...
    assert _norm_ppf(0.975) == pytest.approx(1.959963985, abs=1e-6)


def test_norm_ppf_and_cdf_are_inverses_across_all_three_branches():
    # 0.01 and 0.99 exercise the two tail branches, the rest the central one.
    for p in (0.01, 0.2, 0.5, 0.8, 0.99):
        assert _norm_cdf(_norm_ppf(p)) == pytest.approx(p, abs=1e-8)


def test_norm_ppf_refuses_values_outside_the_open_unit_interval():
    with pytest.raises(ValueError):
        _norm_ppf(0.0)
    with pytest.raises(ValueError):
        _norm_ppf(1.0)


# ------------------------------------------------- expected maximum Sharpe ----


def test_a_single_trial_has_no_selection_benefit():
    # One trial means nothing was selected, so E[max SR] is exactly 0.
    assert expected_max_sharpe(1, 0.25) == 0.0


def test_zero_variance_across_trials_leaves_nothing_to_select_on():
    assert expected_max_sharpe(50, 0.0) == 0.0


def test_expected_max_sharpe_hand_computed_for_ten_trials():
    # sqrt(1) * [(1-g)*Phi^-1(0.9) + g*Phi^-1(1 - 1/(10e))]
    # = 0.42278 * 1.28155 + 0.57722 * 1.78962 ~= 0.54183 + 1.03300 = 1.5748
    got = expected_max_sharpe(10, 1.0)
    expected = ((1 - EULER_MASCHERONI) * _norm_ppf(0.9)
                + EULER_MASCHERONI * _norm_ppf(1 - 1 / (10 * math.e)))
    assert got == pytest.approx(expected, abs=1e-12)
    assert got == pytest.approx(1.5748, abs=1e-3)


def test_more_trials_raise_the_bar():
    many, some, few = (expected_max_sharpe(n, 1.0) for n in (100, 10, 2))
    assert many > some > few


def test_expected_max_sharpe_refuses_bad_inputs():
    with pytest.raises(ValueError):
        expected_max_sharpe(0, 1.0)
    with pytest.raises(ValueError):
        expected_max_sharpe(5, -0.1)


# ------------------------------------------------------ deflated Sharpe -------


def test_observed_equal_to_the_null_maximum_gives_exactly_one_half():
    # z = 0 by construction and Phi(0) = 0.5: the observed Sharpe is exactly what
    # selection alone would have produced, so it carries no evidence.
    benchmark = expected_max_sharpe(20, 0.04)
    out = deflated_sharpe_ratio(benchmark, n_observations=142, n_trials=20, sharpe_variance=0.04)
    assert out["z"] == pytest.approx(0.0, abs=1e-12)
    assert out["deflated_sharpe_ratio"] == pytest.approx(0.5, abs=1e-12)


def test_a_single_trial_with_zero_sharpe_is_a_coin_flip():
    out = deflated_sharpe_ratio(0.0, n_observations=142, n_trials=1, sharpe_variance=0.04)
    assert out["expected_max_sharpe_under_null"] == 0.0
    assert out["deflated_sharpe_ratio"] == pytest.approx(0.5, abs=1e-12)


def test_trying_more_hypotheses_deflates_the_same_observed_sharpe():
    kw = dict(observed_sharpe=0.20, n_observations=142, sharpe_variance=0.04)
    few = deflated_sharpe_ratio(n_trials=2, **kw)["deflated_sharpe_ratio"]
    many = deflated_sharpe_ratio(n_trials=200, **kw)["deflated_sharpe_ratio"]
    assert many < few


def test_negative_skew_and_fat_tails_deflate_a_promising_sharpe():
    # benchmark = expected_max_sharpe(20, 0.04) ~= 0.380, so 0.60 is above it.
    kw = dict(observed_sharpe=0.60, n_observations=142, n_trials=20, sharpe_variance=0.04)
    normal = deflated_sharpe_ratio(skewness=0.0, kurtosis=3.0, **kw)["deflated_sharpe_ratio"]
    ugly = deflated_sharpe_ratio(skewness=-1.5, kurtosis=9.0, **kw)["deflated_sharpe_ratio"]
    assert ugly < normal


def test_the_shape_adjustment_is_asymmetric_about_the_null_maximum():
    """Recorded because it is counter-intuitive and would otherwise look like a bug.

    The skew/kurtosis term only ever WIDENS the estimator's variance. Above the
    null maximum that pulls z toward zero and deflates the result. BELOW it the
    numerator is already negative, so the same widening pulls z UP and the
    deflated ratio RISES. Neither is a rescue: both stay below 0.5.
    """
    kw = dict(n_observations=142, n_trials=20, sharpe_variance=0.04)
    assert expected_max_sharpe(20, 0.04) == pytest.approx(0.380, abs=0.005)
    normal = deflated_sharpe_ratio(0.20, skewness=0.0, kurtosis=3.0, **kw)["deflated_sharpe_ratio"]
    ugly = deflated_sharpe_ratio(0.20, skewness=-1.5, kurtosis=9.0, **kw)["deflated_sharpe_ratio"]
    assert ugly > normal
    assert ugly < 0.5


def test_deflated_sharpe_refuses_too_few_observations_and_degenerate_shape():
    with pytest.raises(ValueError):
        deflated_sharpe_ratio(0.2, n_observations=1, n_trials=5, sharpe_variance=0.04)
    # 1 - 5*1 + 0 < 0 -> impossible variance term
    with pytest.raises(ValueError):
        deflated_sharpe_ratio(1.0, n_observations=50, n_trials=5, sharpe_variance=0.04,
                              skewness=5.0, kurtosis=1.0)


# ---------------------------------------------------------- Harvey/Liu/Zhu ----


def test_the_gap_between_the_conventional_and_hlz_hurdles_is_real():
    # mean 0.25, sd 1.0, n 100 -> t = 0.25 / (1.0/10) = 2.5 exactly.
    # Clears the conventional 2.0, fails HLZ's 3.0 -- the whole point.
    out = harvey_liu_zhu_verdict(mean=0.25, stdev=1.0, n_observations=100)
    assert out["t_stat"] == pytest.approx(2.5, abs=1e-12)
    assert out["passes_conventional"] is True
    assert out["passes_hlz"] is False


def test_a_strong_result_clears_both_hurdles():
    # mean 0.5, sd 1.0, n 144 -> t = 0.5 / (1/12) = 6.0 exactly.
    out = harvey_liu_zhu_verdict(mean=0.5, stdev=1.0, n_observations=144)
    assert out["t_stat"] == pytest.approx(6.0, abs=1e-12)
    assert out["passes_hlz"] is True


def test_hlz_refuses_zero_dispersion_and_too_few_observations():
    with pytest.raises(ValueError):
        harvey_liu_zhu_verdict(mean=1.0, stdev=0.0, n_observations=10)
    with pytest.raises(ValueError):
        harvey_liu_zhu_verdict(mean=1.0, stdev=1.0, n_observations=1)


# -------------------------------------------------------------------- PBO ----


def test_pbo_is_undefined_with_a_single_candidate():
    out = probability_of_backtest_overfitting([[1.0, 2.0, 3.0, 4.0]], n_blocks=4)
    assert out.degenerate is True
    assert math.isnan(out.pbo)


def test_a_uniformly_dominant_strategy_has_zero_overfitting():
    # A beats B in every block, so the IS winner is always the OOS winner.
    out = probability_of_backtest_overfitting([[10.0] * 4, [1.0] * 4], n_blocks=4)
    assert out.pbo == 0.0
    assert out.n_splits == 6  # C(4,2)


def test_perfectly_regime_split_strategies_are_fully_overfit():
    # A wins blocks 0-1 and loses 2-3; B mirrors it. The in-sample winner is
    # exactly the OOS loser, and tied splits land on the median. PBO = 1.0.
    a = [10.0, 10.0, -10.0, -10.0]
    b = [-10.0, -10.0, 10.0, 10.0]
    out = probability_of_backtest_overfitting([a, b], n_blocks=4)
    assert out.n_splits == 6
    assert out.pbo == 1.0


def test_eight_blocks_give_seventy_balanced_splits():
    # C(8,4) = 70, matching the 8 walk-forward folds.
    out = probability_of_backtest_overfitting([[float(i) for i in range(8)], [0.0] * 8])
    assert out.n_splits == 70


def test_pbo_refuses_odd_blocks_and_ragged_rows():
    with pytest.raises(ValueError):
        probability_of_backtest_overfitting([[1.0] * 5, [2.0] * 5], n_blocks=5)
    with pytest.raises(ValueError):
        probability_of_backtest_overfitting([[1.0] * 4, [1.0, 2.0]], n_blocks=4)
