"""V2.9's leakage controls rerun on the synthetic 17-vehicle world with t4 rows and the rod features
(reports/stage_e20_plan.md section 13; review PR-4, PR-14), calling the frozen helpers
(tests/ml_v2_fixtures.perturb_after and _changed, cpcv.split_masks and assert_fold,
tests/test_ml_v2_leakage.shuffle_targets): the perturbation test with cuts at t1, t2 and every
group's t4, shown not vacuous by planted future-reading variants; the fold test on a horizon that
holds t4 rows; a planted-edge canary at t4 (a pattern_search-side plant on a copy of the
synthetic bars); the cross-date target-shuffle null on the composed panel."""

from __future__ import annotations

import dataclasses

import numpy as np
import pandas as pd
import pytest

from pattern_search import constants as K
from pattern_search.panel import build_search_panel, context, feature_frame
from tests._pattern_search_synth import configs_named, panel_small, rows_small, world_small
from tests.ml_v2_fixtures import _changed, perturb_after

NS_MIN = 60_000_000_000
CUT_DAY = pd.Timestamp("2021-06-16")


def _cuts(rows: pd.DataFrame) -> list[int]:
    """One cut per distinct (group, t_index) instant on CUT_DAY: t1 and t2 of two groups and t4
    of every group (14:08, 12:18, 12:03 CT)."""
    on = rows.loc[rows["trade_date"] == CUT_DAY]
    picks = on.loc[on["t_index"] == K.T4_INDEX, "decision_ts_ns"].unique().tolist()
    for g, k in (("equity", 1), ("rates", 2)):
        picks += on.loc[(on["group"] == g) & (on["t_index"] == k), "decision_ts_ns"].unique()[:1
                                                                                             ].tolist()
    return sorted(int(c) for c in picks)


def _perturbation(features, cuts: list[int], seed: int = 21) -> int:  # noqa: ANN001
    w, rows = world_small(), rows_small()
    base = features(context(w, rows))
    t = rows["decision_ts_ns"].to_numpy(np.int64)
    compared, leaks = 0, []
    for k, cut in enumerate(cuts):
        moved = perturb_after(w.bars, cut, seed=seed + k)
        got = features(context(dataclasses.replace(w, bars=moved), rows))
        mask = t <= cut
        compared += int(mask.sum())
        bad = _changed(base, got, mask)
        if bad:
            leaks.append(f"cut {cut}: {bad[:4]}")
    if leaks:
        raise AssertionError("features at t moved with bars after t: " + "; ".join(leaks))
    return compared


def test_the_cuts_include_every_groups_t4() -> None:
    from ml_route_v2.clock import minutes_after_midnight_ct

    mins = set(minutes_after_midnight_ct(np.asarray(_cuts(rows_small()))).tolist())
    assert {14 * 60 + 8, 12 * 60 + 18, 12 * 60 + 3} <= mins and len(mins) >= 5


def test_every_kept_feature_and_both_rod_features_pass_the_perturbation_test() -> None:
    compared = _perturbation(feature_frame, _cuts(rows_small()))
    assert compared > 5000


def _future_rod(ctx) -> pd.DataFrame:  # noqa: ANN001
    """A planted leak: rod_ret read from the bar 59 minutes after t."""
    from ml_route_v2.signals._core import bars_of, path_of, rows_of

    view = rows_of(ctx)
    out = np.full(view.n, np.nan)
    for v, rows in view.by_root().items():
        b = bars_of(ctx, path_of(v))
        i = b.at(view.t[rows] + 59 * NS_MIN)
        ok = i >= 0
        out[rows[ok]] = b.close[i[ok]]
    return pd.DataFrame({"raw_future": out}, index=ctx.rows.index)


def _centered_absratio(ctx) -> pd.DataFrame:  # noqa: ANN001
    """A planted peeking normalizer: |rod_ret| over a centered 61-row median (later dates)."""
    from pattern_search.features import rod_frame

    rod = rod_frame(ctx)
    r = rod["raw_rod_ret"].abs()
    out = pd.Series(np.nan, index=ctx.rows.index)
    for _key, idx in ctx.rows.groupby(["root", "t_index"]).groups.items():
        order = ctx.rows.loc[idx].sort_values("trade_date").index
        med = r.loc[order].rolling(61, center=True, min_periods=1).median()
        out.loc[order] = r.loc[order] / med
    return pd.DataFrame({"raw_peek": out.to_numpy()}, index=ctx.rows.index)


def test_the_perturbation_test_catches_a_future_bar_and_a_peeking_normalizer() -> None:
    cuts = _cuts(rows_small())[-2:]
    with pytest.raises(AssertionError, match="raw_future"):
        _perturbation(_future_rod, cuts)
    with pytest.raises(AssertionError, match="raw_peek"):
        _perturbation(_centered_absratio, cuts)


def test_the_fold_test_holds_on_a_horizon_with_t4_rows_and_catches_a_planted_overlap() -> None:
    from ml_route_v2.cpcv import (
        LeakageError,
        assert_fold,
        calendar_blocks,
        horizon_data,
        outer_splits,
        split_masks,
    )

    panel = panel_small()
    data = horizon_data(panel, "hF")
    t4 = data.rows["t_index"].to_numpy() == K.T4_INDEX
    assert t4.any() and (data.x_ns[t4] == data.rows["flatten_ts_ns"].to_numpy()[t4]).all()
    splits = outer_splits(calendar_blocks(world_small().calendar))
    assert len(splits) == 15
    for split in splits:
        train, test = split_masks(split, data.days, data.t_ns, data.x_ns)
        assert_fold(split, data.days, data.t_ns, data.x_ns, train, test)
        assert not (train & test).any()
    split = next(sp for sp in splits if min(sp.test_blocks) >= 2)  # training dates before it
    train, test = split_masks(split, data.days, data.t_ns, data.x_ns)
    first_test = min(split.test_dates)
    test_t = data.t_ns[test & (data.days == np.datetime64(first_test))].min()
    cand = np.flatnonzero(train & t4 & (data.t_ns < test_t))
    victim = int(cand[np.argmax(data.t_ns[cand])])
    x_bad = data.x_ns.copy()
    x_bad[victim] = test_t + 5 * NS_MIN  # its exit crosses into a test date
    train_bad, test_bad = split_masks(split, data.days, data.t_ns, x_bad)
    assert not train_bad[victim]  # the purge removes it
    leaked = train_bad.copy()
    leaked[victim] = True
    with pytest.raises(LeakageError):
        assert_fold(split, data.days, data.t_ns, x_bad, leaked, test_bad)


# ------------------------------------------------------------------ t4 canary, shuffle null ----
def plant_t4(world, edge_cost_multiple: float):  # noqa: ANN001, ANN201
    """A copy of the world whose bars carry, after every t4 entry bar, a jump of edge x sign(the
    trailing 60-minute return at t4) that persists (so the exit at F_X keeps it)."""
    from ml_route_v2.signals._core import per_unit
    from ml_route_v2.synthetic import nominal_cost_ticks
    from pattern_search.rows import search_rows

    rows = search_rows(world)
    t4 = rows.loc[rows["t_index"] == K.T4_INDEX]
    bars = dict(world.bars)
    for v, grp in t4.groupby("root"):
        path = K.VEHICLE_PATHS[v]
        f = bars[path]
        ts = f["ts_event"].to_numpy(np.int64)
        close = f["close"].to_numpy(np.float64)
        t = np.sort(grp["decision_ts_ns"].to_numpy(np.int64))
        i1 = np.searchsorted(ts, t - NS_MIN)
        i0 = np.searchsorted(ts, t - 61 * NS_MIN)
        ok = (i1 < len(ts)) & (i0 < len(ts))
        ok &= (ts[np.clip(i1, 0, len(ts) - 1)] == t - NS_MIN) & \
            (ts[np.clip(i0, 0, len(ts) - 1)] == t - 61 * NS_MIN)
        x = np.where(ok, close[np.clip(i1, 0, None)] - close[np.clip(i0, 0, None)], 0.0)
        edge = edge_cost_multiple * nominal_cost_ticks(v) / per_unit(v)
        jumps = edge * np.sign(x)
        cum = np.cumsum(jumps)
        k = np.searchsorted(t + NS_MIN, ts, side="right") - 1
        offset = np.where(k >= 0, cum[np.clip(k, 0, None)], 0.0)
        g = f.copy()
        for c in ("open", "high", "low", "close"):
            g[c] = f[c].to_numpy(np.float64) + offset
        bars[path] = g
    return dataclasses.replace(world, bars=bars)


def _median_t(panel, tmp, configs):  # noqa: ANN001, ANN202
    from pattern_search.oos import Refits, final_record
    from pattern_search.search import admissibility, run_final, run_nested

    filt = admissibility(panel)
    cal = world_small().calendar
    nested = run_nested(panel, filt, cal, tmp, configs)
    final = run_final(panel, filt, cal, tmp, configs)
    from ml_route_v2.pipeline import _daily_t, split_risk_fn

    ts = [_daily_t(nested.path_daily[c].to_numpy()) for c in nested.path_daily.columns]
    fin = final_record(Refits(panel, nested, filt["admissible"], split_risk_fn(panel)),
                       final.config) if final.config is not None else {}
    return float(np.median(ts)), fin


@pytest.fixture(scope="module")
def planted_panels():  # noqa: ANN201
    """(t1-t4 planted, t1-t3 planted): the frozen sign plant (t1..t3, synthetic.py) with and
    without the pattern_search t4 plant on a copy of the bars."""
    from pattern_search.world import synthetic_world
    from tests._pattern_search_synth import SEED, SMALL_FIRST, SMALL_LAST

    w = synthetic_world(SMALL_FIRST, SMALL_LAST, seed=SEED,
                        plant={"kind": "sign", "edge_cost_multiple": 10.0})
    return build_search_panel(plant_t4(w, 10.0)), build_search_panel(w)


CANARY = ("ridge_l0.1_k1.5_h60",)


def test_a_planted_edge_at_t4_is_found_and_attributed_to_t4(planted_panels, tmp_path) -> None:
    both, t13 = planted_panels
    t_both, fin_both = _median_t(both, tmp_path / "both", configs_named(*CANARY))
    t_t13, fin_t13 = _median_t(t13, tmp_path / "t13", configs_named(*CANARY))
    assert t_both >= 3.0, t_both
    assert fin_both["pnl_t4_15_splits_usd"] > 0, fin_both
    assert fin_both["pnl_t4_15_splits_usd"] > fin_t13["pnl_t4_15_splits_usd"] + 1000.0, (
        fin_both, fin_t13)
    assert fin_both["t4_share"] > fin_t13["t4_share"]  # t4 carries the t4 plant's P&L


def test_the_cross_date_target_shuffle_leaves_no_nested_edge(planted_panels, tmp_path) -> None:
    from tests.test_ml_v2_leakage import shuffle_targets

    shuffled = shuffle_targets(planted_panels[0], seed=7)
    t_shuffled, _fin = _median_t(shuffled, tmp_path, configs_named(*CANARY))
    assert abs(t_shuffled) < 2.0, t_shuffled


def test_the_unplanted_world_shows_no_edge_either(tmp_path) -> None:
    t_noise, _fin = _median_t(panel_small(), tmp_path, configs_named(*CANARY))
    assert abs(t_noise) < 2.0, t_noise
