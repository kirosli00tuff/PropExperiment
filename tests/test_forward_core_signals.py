"""forward.core: EWMAC, caps, vol, diversification multipliers, positions, yield proxy
(synthetic data only; hand-computed references)."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from forward import core


def test_ewmac_raw_matches_hand_computed_adjusted_ewmas():
    # Arrange: span 2 -> alpha 2/3 (decay 1/3); span 4 -> alpha 0.4 (decay 0.6); adjust=True
    price = pd.Series([1.0, 2.0, 3.0])
    vol = pd.Series([0.5, 0.5, 0.5])
    # Act
    raw = core.ewmac_raw(price, vol, 2, 4)
    # Assert: t=1 fast (2 + 1/3)/(4/3) = 1.75, slow (2 + 0.6)/1.6 = 1.625
    assert raw.iloc[1] == pytest.approx((1.75 - 1.625) / 0.5)
    # t=2 fast (3 + 2/3 + 1/9)/(13/9) = 34/13, slow (3 + 1.2 + 0.36)/1.96
    assert raw.iloc[2] == pytest.approx((34 / 13 - 4.56 / 1.96) / 0.5)
    assert raw.iloc[0] == 0.0


def test_ewmac_uses_vol_forward_filled():
    price = pd.Series([1.0, 2.0, 3.0])
    vol = pd.Series([0.5, np.nan, np.nan])
    assert core.ewmac_raw(price, vol, 2, 4).iloc[2] == pytest.approx((34 / 13 - 4.56 / 1.96) / 0.5)


def test_speed_forecast_is_scaled_then_capped_at_20():
    price = pd.Series(np.arange(300, dtype=float))  # a steady trend: large raw forecasts
    vol = pd.Series(np.full(300, 0.01))
    sp = core.speed_forecasts(price, vol, [(2, 4)], [2.0], 20.0)
    assert sp.iloc[-1, 0] == 20.0
    sp_neg = core.speed_forecasts(-price, vol, [(2, 4)], [2.0], 20.0)
    assert sp_neg.iloc[-1, 0] == -20.0
    small = core.speed_forecasts(price, pd.Series(np.full(300, 1e6)), [(2, 4)], [2.0], 20.0)
    assert 0 < small.iloc[-1, 0] < 20.0


def test_combined_forecast_is_mean_times_fdm_capped():
    sp = pd.DataFrame({"a": [4.0, 20.0], "b": [8.0, 20.0]})
    out = core.combine_forecasts(sp, 1.5, 20.0)
    assert out.iloc[0] == pytest.approx(9.0)  # mean 6 x 1.5
    assert out.iloc[1] == 20.0  # 20 x 1.5 = 30, capped


def test_mixed_vol_blends_recent_and_slow_as_carver():
    rng = np.random.default_rng(1)
    d = pd.Series(rng.normal(0, 1, 400))
    out = core.mixed_vol(d, days=35, min_periods=10, slow_vol_years=10, business_days=256.0,
                         proportion_of_slow_vol=0.3)
    recent = d.ewm(adjust=True, span=35, min_periods=10).std()
    slow = recent.ewm(span=2560).mean()
    expect = 0.3 * slow + 0.7 * recent
    pd.testing.assert_series_equal(out, expect, check_names=False)
    assert out.iloc[:9].isna().all() and out.iloc[9:].notna().all()


def test_mixed_vol_uses_only_past_data():
    rng = np.random.default_rng(2)
    d = pd.Series(rng.normal(0, 1, 300))
    a = core.mixed_vol(d)
    d2 = d.copy()
    d2.iloc[200:] *= 10.0
    b = core.mixed_vol(d2)
    pd.testing.assert_series_equal(a.iloc[:200], b.iloc[:200])


def test_annual_dollar_vol_is_multiplier_times_16_times_daily_price_vol():
    assert core.annual_dollar_vol(2.5, 10.0) == pytest.approx(400.0)


@pytest.mark.parametrize("corr, w, expected", [
    ([[1.0, 0.5], [0.5, 1.0]], [0.5, 0.5], 1 / math.sqrt(0.75)),
    ([[1.0, -0.5], [-0.5, 1.0]], [0.5, 0.5], 1 / math.sqrt(0.5)),  # negative floored at 0
    ([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]], [1 / 3] * 3, math.sqrt(3.0)),
    ([[1.0, 0.2, 0.2], [0.2, 1.0, 0.2], [0.2, 0.2, 1.0]], [1 / 3] * 3,
     1 / math.sqrt(1 / 3 + 6 / 9 * 0.2)),
])
def test_div_multiplier_formula(corr, w, expected):
    assert core.div_multiplier(np.array(corr), np.array(w)) == pytest.approx(expected)


def test_div_multiplier_capped_at_2_5():
    n = 10
    assert core.div_multiplier(np.eye(n), np.full(n, 1 / n)) == 2.5


def test_idm_for_live_uses_live_submatrix_equal_weights():
    corr = np.array([[1.0, 0.5, 0.0], [0.5, 1.0, 0.0], [0.0, 0.0, 1.0]])
    live = np.array([True, True, False])
    assert core.idm_for_live(corr, live) == pytest.approx(1 / math.sqrt(0.75))
    assert core.idm_for_live(corr, np.array([False, False, False])) == 0.0


def test_unrounded_position_formula():
    # N = (F/10) x C x tau x IDM x w / V = 1 x 25000 x 0.2 x 2 x 0.25 / 1000
    assert core.unrounded_position(10.0, 25_000, 0.2, 2.0, 0.25, 1000.0) == pytest.approx(2.5)
    assert core.unrounded_position(-5.0, 25_000, 0.2, 2.0, 0.25, 1000.0) == pytest.approx(-1.25)
    assert core.average_position(25_000, 0.2, 2.0, 0.25, 1000.0) == pytest.approx(2.5)


def test_yield_proxy_conversion():
    # PVBP = 125 x 6.5 / 10,000 = 0.08125 points per bp; dP +0.5 -> yields fall 6.1538 bp
    dy = core.yield_proxy_diffs([0.5, -0.25], [125.0, 125.0], 6.5)
    assert dy[0] == pytest.approx(-0.5 / 0.08125)
    assert dy[1] == pytest.approx(0.25 / 0.08125)


def test_ew_corr_pairwise_recovers_perfect_and_clips():
    rng = np.random.default_rng(3)
    x = rng.normal(size=200)
    r = np.column_stack([x, 2 * x + 1, -x, rng.normal(size=200)])
    c = core.ew_corr_pairwise(r, span=75, min_periods=10, clip=0.99)
    assert c[0, 1] == pytest.approx(0.99)
    assert c[0, 2] == pytest.approx(-0.99)
    assert abs(c[0, 3]) < 0.3
    assert np.allclose(np.diag(c), 1.0)


def test_ew_corr_pairwise_offdiag_when_too_few_common_rows():
    r = np.array([[1.0, np.nan], [2.0, np.nan], [3.0, 1.0]])
    c = core.ew_corr_pairwise(r, span=75, min_periods=10, clip=0.99, offdiag=0.0)
    assert c[0, 1] == 0.0


def test_ew_corr_weights_match_pandas_ewm_corr():
    rng = np.random.default_rng(4)
    df = pd.DataFrame(rng.normal(size=(120, 2)))
    expect = df[0].ewm(span=20).corr(df[1]).iloc[-1]
    got = core.ew_corr_pairwise(df.to_numpy(), span=20, min_periods=10, clip=1.0)[0, 1]
    assert got == pytest.approx(expect, rel=1e-9)


def test_sampled_returns_windows_end_on_decision_day_and_carry_forward():
    days = np.array([10, 11, 12, 20, 25], dtype=np.int64)
    cum = np.array([[0.0], [1.0], [2.0], [5.0], [7.0]])
    r = core.sampled_returns(cum, days, decision_day=25, step_days=7, n_steps=2)
    # sample points 11, 18, 25 -> values 1.0, 2.0 (carried from day 12), 7.0
    assert r[:, 0].tolist() == [1.0, 5.0]
