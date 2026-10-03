"""ml_route_v2.normalize.zscore_causal: strictly earlier trade dates, warm-up, clip (V2.4)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ml_route_v2.normalize import zscore_causal


def _frame(n_dates: int = 120, per_day: int = 3, roots: tuple[str, ...] = ("ZN", "6E"),
           seed: int = 1) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    days = pd.bdate_range("2021-01-04", periods=n_dates)
    recs = [(r, d, k) for d in days for r in roots for k in range(per_day)]
    rows = pd.DataFrame(recs, columns=["root", "trade_date", "t_index"])
    rows["trade_date"] = rows["trade_date"].astype("datetime64[ns]")
    raw = pd.DataFrame({"a": rng.normal(5.0, 2.0, len(rows)),
                        "b": rng.standard_t(3, len(rows))}, index=rows.index)
    return raw, rows


def test_rows_before_a_date_do_not_see_later_changes() -> None:
    raw, rows = _frame()
    z0 = zscore_causal(raw, rows, ["a", "b"], window_dates=40, min_dates=10)
    cut = pd.Timestamp(rows["trade_date"].unique()[70])
    changed = raw.copy()
    later = rows["trade_date"] >= cut
    changed.loc[later, :] = np.random.default_rng(9).normal(100, 50, (int(later.sum()), 2))
    z1 = zscore_causal(changed, rows, ["a", "b"], window_dates=40, min_dates=10)
    before = ~later.to_numpy()
    np.testing.assert_array_equal(z0.to_numpy()[before], z1.to_numpy()[before])
    assert not np.allclose(z0.to_numpy()[~before][:50], z1.to_numpy()[~before][:50],
                           equal_nan=True)


def test_same_date_rows_do_not_use_each_other() -> None:
    raw, rows = _frame()
    z0 = zscore_causal(raw, rows, ["a"], window_dates=40, min_dates=10)
    day = pd.Timestamp(rows["trade_date"].unique()[50])
    on_day = np.flatnonzero((rows["trade_date"] == day).to_numpy())
    changed = raw.copy()
    changed.iloc[on_day[0], 0] = 1e6
    z1 = zscore_causal(changed, rows, ["a"], window_dates=40, min_dates=10)
    np.testing.assert_array_equal(z0["a"].to_numpy()[on_day[1:]], z1["a"].to_numpy()[on_day[1:]])


def test_roots_are_separate() -> None:
    raw, rows = _frame()
    z0 = zscore_causal(raw, rows, ["a"], window_dates=40, min_dates=10)
    changed = raw.copy()
    changed.loc[rows["root"] == "6E", "a"] *= 50
    z1 = zscore_causal(changed, rows, ["a"], window_dates=40, min_dates=10)
    zn = (rows["root"] == "ZN").to_numpy()
    np.testing.assert_array_equal(z0["a"].to_numpy()[zn], z1["a"].to_numpy()[zn])


def test_warm_up_and_hand_computed_value() -> None:
    raw, rows = _frame(n_dates=30, roots=("ZN",))
    z = zscore_causal(raw, rows, ["a"], window_dates=5, min_dates=4, clip=50.0)
    days = rows["trade_date"].unique()
    first4 = rows["trade_date"].isin(days[:4]).to_numpy()
    assert np.isnan(z["a"].to_numpy()[first4]).all()
    target_day = days[10]
    window = rows["trade_date"].isin(days[5:10]).to_numpy()
    vals = raw["a"].to_numpy()[window]
    i = int(np.flatnonzero((rows["trade_date"] == target_day).to_numpy())[1])
    want = (raw["a"].iloc[i] - vals.mean()) / vals.std(ddof=1)
    assert z["a"].iloc[i] == pytest.approx(want)


def test_missing_values_do_not_enter_the_statistics() -> None:
    raw, rows = _frame(n_dates=30, roots=("ZN",))
    masked = raw.copy()
    days = rows["trade_date"].unique()
    hole = rows["trade_date"].isin(days[5:8]).to_numpy()
    masked.loc[hole, "a"] = np.nan
    z = zscore_causal(masked, rows, ["a"], window_dates=6, min_dates=4, clip=50.0)
    assert np.isnan(z["a"].to_numpy()[hole]).all()
    i = int(np.flatnonzero((rows["trade_date"] == days[10]).to_numpy())[0])
    window = rows["trade_date"].isin(days[4:10]).to_numpy() & ~hole
    vals = raw["a"].to_numpy()[window]
    assert z["a"].iloc[i] == pytest.approx((raw["a"].iloc[i] - vals.mean()) / vals.std(ddof=1))


def test_clip_and_degenerate_statistics() -> None:
    raw, rows = _frame(n_dates=30, roots=("ZN",))
    spike = raw.copy()
    last_day = rows["trade_date"] == rows["trade_date"].max()
    spike.loc[last_day, "a"] = 1e9
    z = zscore_causal(spike, rows, ["a"], window_dates=10, min_dates=5, clip=5.0)
    assert (z.loc[last_day, "a"] == 5.0).all()
    flat = raw.copy()
    flat["a"] = 3.0
    later = rows["trade_date"] == rows["trade_date"].unique()[20]
    flat.loc[later.to_numpy().nonzero()[0][0], "a"] = 4.0
    zf = zscore_causal(flat, rows, ["a"], window_dates=10, min_dates=5)
    warm = rows["trade_date"].isin(rows["trade_date"].unique()[:5]).to_numpy()
    assert np.isnan(zf["a"].to_numpy()[warm]).all()
    at = later.to_numpy().nonzero()[0]
    assert zf["a"].iloc[at[0]] == 5.0  # away from a constant window: the clip
    assert (zf["a"].iloc[at[1:]] == 0.0).all()  # at the constant: 0, never missing
    sparse = raw.copy()
    sparse["a"] = np.nan
    sparse.loc[rows.index[-1], "a"] = 1.0
    zs = zscore_causal(sparse, rows, ["a"], window_dates=10, min_dates=5)
    assert np.isnan(zs["a"]).all()  # fewer than two values: no statistic


def test_misaligned_input_raises() -> None:
    raw, rows = _frame(n_dates=10)
    with pytest.raises(ValueError):
        zscore_causal(raw.iloc[::-1], rows, ["a"])


def test_deterministic() -> None:
    raw, rows = _frame()
    pd.testing.assert_frame_equal(zscore_causal(raw, rows, ["a", "b"]),
                                  zscore_causal(raw, rows, ["a", "b"]))


def test_a_feature_of_mean_1e6_and_sd_1_keeps_its_z_scores() -> None:
    """Code review C-12: the sums are taken about a shifted origin, so a feature of mean 1e6 and
    sd 1 gets the z-scores of the same feature centred at 0 (no cancellation of order
    1e-16 x mean^2 / var, and no false "flat window")."""
    _raw, rows = _frame(n_dates=90, seed=8)
    rng = np.random.default_rng(8)
    centred = pd.DataFrame({"a": rng.standard_normal(len(rows))}, index=rows.index)
    far = centred + 1e6
    z0 = zscore_causal(centred, rows, ["a"], window_dates=20, min_dates=10)
    z1 = zscore_causal(far, rows, ["a"], window_dates=20, min_dates=10)
    assert z0["a"].notna().sum() > 0
    np.testing.assert_array_equal(z0["a"].isna().to_numpy(), z1["a"].isna().to_numpy())
    np.testing.assert_allclose(z1["a"].to_numpy(), z0["a"].to_numpy(), rtol=0, atol=1e-6,
                               equal_nan=True)
    assert (z1["a"].dropna().abs() < 5.0).mean() > 0.9  # real z-scores, not +-clip
