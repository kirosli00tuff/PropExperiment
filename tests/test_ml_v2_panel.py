"""ml_route_v2.panel and ml_route_v2.cost_filter on synthetic data (V2.2 filter, V2.3, V2.4)."""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import pytest

from ml_route_v2.clock import ROW_COLUMNS, decision_rows, trade_dates_of
from ml_route_v2.constants import (
    C_SIGMA_TAU,
    CLUSTERS,
    HORIZONS,
    LOSS_QUANTILE,
    SEED,
    UNIVERSE,
)
from ml_route_v2.cost_filter import COLUMNS, admissible_roots, c_sigma_table, risk_table
from ml_route_v2.panel import Panel, WindowError, assert_window, build_panel
from ml_route_v2.signals import REGISTRY, SignalContext, compute_signals
from ml_route_v2.signals.synthetic_bars import session_bars, synthetic_releases
from ml_route_v2.targets import build_targets, frozen_costs, sigma_d

FIRST, LAST = date(2021, 3, 1), date(2021, 11, 15)
VEHICLES = ("MNQ", "6C", "MGC", "ZS", "MBT", "HE")
ROOTS = ("NQ", "6C", "GC", "ZS", "MBT", "HE", "ZN", "6E", "CL", "ZC", "MES", "ZM", "ZL")


def _ctx_and_targets() -> tuple[SignalContext, pd.DataFrame]:
    bars = {r: session_bars(r, FIRST, LAST, seed=SEED + i) for i, r in enumerate(ROOTS)}
    rows = decision_rows(VEHICLES, {v: trade_dates_of(bars[UNIVERSE[v][1]]) for v in VEHICLES})
    rel = synthetic_releases(FIRST, LAST, SEED)
    ctx = SignalContext(rows, bars, rel, sigma_d(rows, bars))
    tg = build_targets(rows, bars, releases=rel, costs=frozen_costs(VEHICLES))
    return ctx, tg


@pytest.fixture(scope="module")
def built() -> tuple[SignalContext, pd.DataFrame, Panel]:
    ctx, tg = _ctx_and_targets()
    return ctx, tg, build_panel(ctx, tg)


def test_layout(built: tuple) -> None:
    ctx, tg, panel = built
    names = tuple(REGISTRY)
    cols = list(panel.frame.columns)
    z = [f"z_{n}" for n in names]
    a = [f"app_{n}" for n in names]
    ids = [f"id_root_{v}" for v in UNIVERSE] + [f"id_cluster_{k}" for k in CLUSTERS]
    assert cols == list(ROW_COLUMNS) + z + a + ids + list(tg.columns)
    assert panel.signal_names == names and panel.horizons == HORIZONS
    assert panel.feature_cols[:len(z)] == tuple(z)
    assert set(panel.feature_cols) <= set(cols)
    assert panel.feature_cols[-len(ids):] == tuple(ids)
    assert len(panel.avail_max_ts_ns) == len(panel.frame)


def test_rows_kept_are_complete_and_causal(built: tuple) -> None:
    ctx, _tg, panel = built
    f = panel.frame
    assert 0 < len(f) < len(ctx.rows)
    feats = f[list(panel.feature_cols)].to_numpy()
    assert np.isfinite(feats).all()
    assert (panel.avail_max_ts_ns <= f["decision_ts_ns"].to_numpy()).all()
    for n in REGISTRY:
        off = f[f"app_{n}"].to_numpy() == 0
        assert (f[f"z_{n}"].to_numpy()[off] == 0).all()
        if REGISTRY[n].normalize:
            assert (np.abs(f[f"z_{n}"].to_numpy()) <= 5.0).all()
    assert set(np.unique(f["z_g11_t_index"])) <= {1.0, 2.0, 3.0}
    root_ids = f[[f"id_root_{v}" for v in UNIVERSE]].to_numpy()
    assert (root_ids.sum(axis=1) == 1).all()
    assert (f[[f"id_cluster_{k}" for k in CLUSTERS]].to_numpy().sum(axis=1) == 1).all()
    assert panel.counts["rows_out"] == len(f) and panel.counts["rows_in"] == len(ctx.rows)


def test_dropped_rows_have_a_named_cause(built: tuple) -> None:
    ctx, _tg, panel = built
    sig = compute_signals(ctx)
    raw = sig[[c for c in sig.columns if c.startswith("raw_")]].to_numpy()
    app = sig[[c for c in sig.columns if c.startswith("app_")]].to_numpy() > 0
    missing = (app & ~np.isfinite(raw)).any(axis=1)
    kept = ctx.rows.index.isin(panel.frame.index)
    assert not (missing & kept).any()
    dropped = (~kept).sum()
    assert dropped == panel.counts["rows_dropped_missing_data"] + \
        panel.counts["rows_dropped_no_statistic_only"]


def test_panel_is_deterministic(built: tuple) -> None:
    ctx, tg, panel = built
    ctx2 = SignalContext(ctx.rows, ctx.bars, ctx.releases, ctx.sigma_d)
    again = build_panel(ctx2, tg)
    pd.testing.assert_frame_equal(panel.frame, again.frame)


def test_window_guard_refuses_a_planted_date(built: tuple) -> None:
    ctx, tg, panel = built
    assert_window(panel)
    planted = ctx.rows.copy()
    planted.loc[planted.index[-1], "trade_date"] = pd.Timestamp("2024-03-01")
    with pytest.raises(WindowError):
        assert_window(planted)
    assert_window(planted, "eval")
    with pytest.raises(WindowError):
        build_panel(SignalContext(planted, ctx.bars, ctx.releases, ctx.sigma_d), tg)
    with pytest.raises(ValueError):
        assert_window(planted, "holdout")


# ------------------------------------------------------------------ cost filter ----
def _filter_frame(n: int = 4000, seed: int = 3) -> tuple[pd.DataFrame, dict[str, float]]:
    rng = np.random.default_rng(seed)
    sd = {"ZN": 20.0, "6E": 2.0}
    parts = []
    for root, s in sd.items():
        f = pd.DataFrame({"root": root, "trade_date": pd.Timestamp("2022-06-01")}, index=range(n))
        for h in HORIZONS:
            f[f"y_gross_{h}"] = rng.normal(0.0, s, n)
            f[f"cost_long_{h}"] = 1.0
            f[f"cost_short_{h}"] = 1.2
            ok = np.ones(n, dtype=bool)
            ok[:10] = False
            f[f"ok_{h}"] = ok
            f.loc[:9, f"y_gross_{h}"] = 1e6  # not formed: never read
        parts.append(f)
    return pd.concat(parts, ignore_index=True), sd


def test_c_sigma_table_on_known_volatility() -> None:
    frame, sd = _filter_frame()
    table = c_sigma_table(frame)
    assert tuple(table.columns) == COLUMNS and len(table) == 2 * len(HORIZONS)
    for _, r in table.iterrows():
        y = frame.loc[(frame["root"] == r["root"]) & frame[f"ok_{r['horizon']}"],
                      f"y_gross_{r['horizon']}"].to_numpy()
        assert r["n_rows"] == len(y) == 3990
        assert r["c_ticks"] == pytest.approx(1.2)
        assert r["sigma_ticks"] == pytest.approx(np.std(y, ddof=1))
        assert r["sigma_ticks"] == pytest.approx(sd[r["root"]], rel=0.05)
        assert r["ratio"] == pytest.approx(1.2 / r["sigma_ticks"])
        assert r["admissible"] == (r["ratio"] <= C_SIGMA_TAU)
        assert r["loss_ticks"] == pytest.approx(np.quantile(np.abs(y), LOSS_QUANTILE))
    assert admissible_roots(table) == ("ZN",)
    pd.testing.assert_frame_equal(risk_table(frame), table)


def test_filter_refuses_forbidden_dates() -> None:
    frame, _ = _filter_frame(n=50)
    frame.loc[0, "trade_date"] = pd.Timestamp("2024-03-04")
    with pytest.raises(WindowError):
        c_sigma_table(frame)
    with pytest.raises(WindowError):
        risk_table(frame)


def test_filter_reads_a_panel(built: tuple) -> None:
    _ctx, _tg, panel = built
    table = c_sigma_table(panel)
    assert set(table["root"]) == set(panel.frame["root"])
    assert (table["n_rows"] > 0).all()


def test_rows_that_lose_their_cost_are_counted_in_panel_counts(built: tuple) -> None:
    """Code review C-05: rows whose fill minute has no calibrated cost bucket leave training
    through ok_<h> = False; Panel.counts now counts them per (root, horizon)."""
    from ml_route_v2.targets import cost_missing_counts

    ctx, tg, panel = built
    assert {k: v for k, v in panel.counts.items() if k.startswith("cost_missing_")} == \
        cost_missing_counts(panel.frame)
    kept = panel.frame.index
    mgc = kept[(panel.frame["root"] == "MGC").to_numpy()
               & np.isfinite(panel.frame["y_gross_h60"].to_numpy())
               & np.isfinite(panel.frame["cost_long_h60"].to_numpy())
               & np.isfinite(panel.frame["cost_short_h60"].to_numpy())][:7]
    assert len(mgc) == 7
    planted = tg.copy()  # as build_targets leaves an uncovered minute: cost NaN, ok False
    planted.loc[mgc, "cost_short_h60"] = np.nan
    planted.loc[mgc, "ok_h60"] = False
    again = build_panel(ctx, planted)
    key = "cost_missing_MGC_h60"
    assert again.counts[key] == panel.counts.get(key, 0) + 7
    assert again.counts["rows_out"] == panel.counts["rows_out"]  # counted, not dropped here
