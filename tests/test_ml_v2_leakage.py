"""Stage E.11 Task 5: the leakage canaries of docs/STAGE_E_ML_V2_DESIGN.md V2.9 and Gate 0's canary
semantics (V2.2b), on synthetic worlds (ml_route_v2/synthetic.py). Each planted leak must be
caught: the guard raises, or the planted edge vanishes.

1. a future bar; 2. a future release; 3. a shuffled target; 4. a peeking normalizer; 5. a
selection step that sees the test block; 6. a label that overlaps the test fold; 7. a product
whose bars are shifted by one minute; 8. Gate 0's canaries (a)-(d); and the window canary.
The positive controls (the whole signal library passes the perturbation test, zscore_causal passes
the normalizer check, an unshifted world passes the session-grid guard) run beside them.

Gate 0 canaries (c) and (d) call Gate 0 on every pair (admissible=None) in a world whose 60-minute
sd is 3 round trips: at the c/sigma filter's tau (0.167, V23 item 1: sd >= 6 c), an edge at the
gross reading's lowest hurdle (1.5 c) is at most 0.25 sd, which needs roughly 200+ trades per pair
to reach Holm's t; a seconds-scale test cannot afford that. The filter itself is Task 2's
(tests/test_ml_v2_panel.py).

Canary (c) under the decided defaults (V23 item 1): an edge in [1.5 c, 2.5 c) passes Gate 0 and
the k = 1.5 cost gate trades it under the gross reading (the default); under the literal net
reading (COST_GATE_READING = "net", pinned by monkeypatch) the same edge is rejected at every k,
the old canary semantics.
"""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import pytest

import ml_route_v2.constants as v2c
from ml_route_v2 import cpcv
from ml_route_v2.configs import CONFIGS, ConfigLedger, SplitScore, ridge_spec
from ml_route_v2.constants import COST_GATE_KS, GATE0_COST_MULTIPLE, UNIVERSE
from ml_route_v2.cost_filter import c_sigma_table, risk_table
from ml_route_v2.cpcv import LeakageError, horizon_data, nested_cpcv
from ml_route_v2.decide import cost_gate
from ml_route_v2.gate0 import gate0_family_a, gate0_family_b, gate0_verdict
from ml_route_v2.models import fit_model, predict
from ml_route_v2.normalize import zscore_causal
from ml_route_v2.panel import WindowError, assert_window
from ml_route_v2.pipeline import (
    BarGridError,
    admissible_ok_panel,
    assert_bars_on_session_grid,
    build_world_panel,
    run_pipeline,
    score_fn_for,
)
from ml_route_v2.signals import REGISTRY, CausalityError, assert_causal, compute_signals
from ml_route_v2.synthetic import NS_MIN, nominal_cost_ticks
from tests.ml_v2_fixtures import (
    PerturbationLeak,
    cuts_of_date,
    normalizer_check,
    perturbation_check,
    raw_rows,
    world,
    world_rows,
    zscore_peek_future,
    zscore_peek_today,
)

SEED = 20261003
PERT_VEHICLES = ("MNQ", "MGC", "6E", "MCL", "ZN", "ZC", "MBT", "HE")
PERT_FIRST, PERT_LAST, PERT_DAY = date(2021, 3, 1), date(2021, 4, 15), date(2021, 4, 7)
G0_VEHICLES = ("MNQ", "MGC", "MCL")
G0_FIRST, G0_LAST = date(2021, 1, 4), date(2022, 2, 28)
STRONG_EDGE_C, MID_EDGE_C, SUB_EDGE_C = 10.0, 2.0, 0.5  # edges in round trips (c)
LOW_SIGMA_C = 3.0  # 60-minute sd in round trips for canaries (c) and (d)
SHUFFLE_CONFIGS = ("ridge_l0.1_k1.5_h60", "ridge_l1_k1.5_h60")


# ------------------------------------------------------------------ worlds ----
def pert_world():
    return world(PERT_VEHICLES, PERT_FIRST, PERT_LAST, seed=SEED,
                 plant={"kind": "leak", "roots": ("NQ",), "minutes": 60})


def g0_world(edge_c: float | None, sigma_c: float = 20.0):
    plant = None if edge_c is None else {"kind": "sign", "edge_cost_multiple": edge_c}
    return world(G0_VEHICLES, G0_FIRST, G0_LAST, seed=SEED + 1, plant=plant,
                 sigma_cost_multiple=sigma_c)


_PANELS: dict = {}


def g0_panel(edge_c: float | None, sigma_c: float = 20.0):
    key = (edge_c, sigma_c)
    if key not in _PANELS:
        _PANELS[key] = build_world_panel(g0_world(edge_c, sigma_c))
    return _PANELS[key]


def run_gate0(panel, tmp, *, filtered: bool):
    ledger = ConfigLedger(tmp / "ledger.jsonl")
    adm = None
    if filtered:
        table = c_sigma_table(panel)
        adm = tuple((r, h) for r, h, ok in zip(table["root"], table["horizon"],
                                               table["admissible"], strict=True) if ok)
    a_panel = admissible_ok_panel(panel, adm) if adm else panel
    tests = [*gate0_family_a(a_panel, ledger=ledger),
             *gate0_family_b(panel, ledger=ledger, state_dir=tmp / "g0", admissible=adm)]
    return tests, gate0_verdict(tests)


# ------------------------------------------------------------------ test-only signals ----
def _frame(rows: pd.DataFrame, value: np.ndarray, app: np.ndarray, avail: np.ndarray
           ) -> pd.DataFrame:
    app = np.asarray(app, dtype=bool)
    return pd.DataFrame({"value": np.where(app, value, 0.0), "applicable": app.astype(float),
                         "avail_ts_ns": np.where(app, avail, rows["decision_ts_ns"]).astype(
                             np.int64)}, index=rows.index)


def as_signal_frame(name: str, frame: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({f"raw_{name}": frame["value"], f"app_{name}": frame["applicable"],
                         f"avail_{name}": frame["avail_ts_ns"]}, index=frame.index)


def _bar_index(bars: pd.DataFrame, when: np.ndarray) -> np.ndarray:
    ts = bars["ts_event"].to_numpy(np.int64)
    i = np.searchsorted(ts, when)
    ok = i < len(ts)
    ok[ok] = ts[i[ok]] == when[ok]
    return np.where(ok, i, -1)


def future_bar_signal(ctx, *, honest: bool) -> pd.DataFrame:
    """LEAKS: the move of the bar opening AT t (it closes at t + 1 min)."""
    rows = ctx.rows
    t = rows["decision_ts_ns"].to_numpy(np.int64)
    value = np.full(len(rows), np.nan)
    for v in pd.unique(rows["root"]):
        sel = np.flatnonzero(rows["root"].to_numpy() == v)
        b = ctx.bars[UNIVERSE[v][1]]
        close = b["close"].to_numpy(np.float64)
        i_now, i_prev = _bar_index(b, t[sel]), _bar_index(b, t[sel] - NS_MIN)
        ok = (i_now >= 0) & (i_prev >= 0)
        value[sel[ok]] = close[i_now[ok]] - close[i_prev[ok]]
    app = np.isfinite(value)
    return _frame(rows, value, app, t + NS_MIN if honest else t)


def leak_column_signal(ctx) -> pd.DataFrame:
    """LEAKS: the planted leak_fwd column of the bar closed by t, stamped available at t."""
    rows = ctx.rows
    t = rows["decision_ts_ns"].to_numpy(np.int64)
    value = np.full(len(rows), np.nan)
    sel = np.flatnonzero(rows["root"].to_numpy() == "MNQ")
    b = ctx.bars["NQ"]
    i = _bar_index(b, t[sel] - NS_MIN)
    ok = i >= 0
    value[sel[ok]] = b["leak_fwd"].to_numpy(np.float64)[i[ok]]
    return _frame(rows, value, np.isfinite(value), t)


def future_release_signal(ctx, *, honest: bool) -> pd.DataFrame:
    """LEAKS: the 5-minute move after the vehicle's next release later on the same trade date
    (as K5-fomc-01's s, which the library excludes); honest stamps it at release + 5 min."""
    from ml_route_v2.signals._core import release_times

    rows = ctx.rows
    t = rows["decision_ts_ns"].to_numpy(np.int64)
    flat = rows["flatten_ts_ns"].to_numpy(np.int64)
    value, avail = np.full(len(rows), np.nan), t.copy()
    for v in pd.unique(rows["root"]):
        sel = np.flatnonzero(rows["root"].to_numpy() == v)
        rel = release_times(ctx.releases, str(v))
        k = np.searchsorted(rel, t[sel], side="right")
        has = k < len(rel)
        nxt = np.where(has, rel[np.clip(k, 0, len(rel) - 1)], -1)
        has &= nxt < flat[sel]
        b = ctx.bars[UNIVERSE[v][1]]
        close = b["close"].to_numpy(np.float64)
        i_after = _bar_index(b, nxt + 4 * NS_MIN)
        i_before = _bar_index(b, nxt - NS_MIN)
        ok = has & (i_after >= 0) & (i_before >= 0)
        value[sel[ok]] = close[i_after[ok]] - close[i_before[ok]]
        avail[sel[ok]] = nxt[ok] + 5 * NS_MIN
    return _frame(rows, value, np.isfinite(value), avail if honest else t)


def registry_features(ctx) -> pd.DataFrame:
    """Every library signal's raw value and applicability, and the panel's z-scores."""
    sig = compute_signals(ctx)
    names = [n for n in REGISTRY if REGISTRY[n].normalize]
    app = sig[[f"app_{n}" for n in names]].to_numpy() > 0
    masked = pd.DataFrame(np.where(app, sig[[f"raw_{n}" for n in names]].to_numpy(), np.nan),
                          index=ctx.rows.index, columns=names)
    z = zscore_causal(masked, ctx.rows, names).add_prefix("z_")
    keep = [c for c in sig.columns if not c.startswith("avail_")]
    return pd.concat([sig[keep], z], axis=1)


def one_signal(fn, **kw):
    return lambda ctx: fn(ctx, **kw)[["value"]]


# ------------------------------------------------------------------ 1. future bar ----
def test_control_every_library_signal_passes_the_perturbation_test() -> None:
    w = pert_world()
    compared = perturbation_check(w, registry_features, cuts_of_date(w, PERT_DAY), seed=11)
    assert compared > 1000


def test_future_bar_with_its_true_timestamp_fails_assert_causal() -> None:
    w = pert_world()
    ctx_rows = world_rows(w)
    from tests.ml_v2_fixtures import context

    frame = future_bar_signal(context(ctx_rows, w.bars, w.releases), honest=True)
    assert frame["applicable"].sum() > 100
    with pytest.raises(CausalityError, match="late"):
        assert_causal(as_signal_frame("fut_bar", frame), ctx_rows)


def test_future_bar_stamped_at_t_fails_the_perturbation_test() -> None:
    w = pert_world()
    with pytest.raises(PerturbationLeak, match="value"):
        perturbation_check(w, one_signal(future_bar_signal, honest=False),
                           cuts_of_date(w, PERT_DAY), seed=12)


def test_future_leaking_column_fails_the_perturbation_test() -> None:
    w = pert_world()
    with pytest.raises(PerturbationLeak, match="value"):
        perturbation_check(w, lambda ctx: leak_column_signal(ctx)[["value"]],
                           cuts_of_date(w, PERT_DAY), seed=13)


# ------------------------------------------------------------------ 2. future release ----
def _release_cut(w) -> int:
    """A decision time of MGC (gold, t1 07:50 CT) with a release later that trade date."""
    from tests.ml_v2_fixtures import context

    rows = world_rows(w)
    frame = future_release_signal(context(rows, w.bars, w.releases), honest=True)
    mgc = (rows["root"] == "MGC").to_numpy() & (frame["applicable"].to_numpy() > 0)
    days = pd.to_datetime(rows["trade_date"]).dt.date.to_numpy()
    pick = np.flatnonzero(mgc & (days >= PERT_FIRST))
    assert pick.size, "no MGC row with a later release in the window"
    return int(rows["decision_ts_ns"].iloc[pick[0]])


def test_future_release_with_its_true_timestamp_fails_assert_causal() -> None:
    w = pert_world()
    rows = world_rows(w)
    from tests.ml_v2_fixtures import context

    frame = future_release_signal(context(rows, w.bars, w.releases), honest=True)
    assert frame["applicable"].sum() > 10
    with pytest.raises(CausalityError, match="late"):
        assert_causal(as_signal_frame("fut_rel", frame), rows)


def test_future_release_stamped_at_t_fails_the_perturbation_test() -> None:
    w = pert_world()
    with pytest.raises(PerturbationLeak, match="value"):
        perturbation_check(w, one_signal(future_release_signal, honest=False),
                           [_release_cut(w)], seed=14)


# ------------------------------------------------------------------ 3. shuffled target ----
def shuffle_targets(panel, seed: int, *, within_dates: bool = False):
    """y_gross permuted among the usable rows of each horizon (across dates, or within each
    date), y_norm recomputed from the row's own sigma_X,d."""
    import dataclasses

    rng = np.random.default_rng(seed)
    frame = panel.frame.copy()
    days = frame["trade_date"].to_numpy()
    sig = frame["sigma_d"].to_numpy(np.float64)
    for h in panel.horizons:
        ok = frame[f"ok_{h}"].to_numpy(bool)
        y = frame[f"y_gross_{h}"].to_numpy(np.float64).copy()
        groups = [np.flatnonzero(ok & (days == d)) for d in np.unique(days[ok])] \
            if within_dates else [np.flatnonzero(ok)]
        for idx in groups:
            y[idx] = y[rng.permutation(idx)]
        frame[f"y_gross_{h}"] = y
        frame[f"y_norm_{h}"] = np.where(ok, y / sig, np.nan)
    return dataclasses.replace(panel, frame=frame)


def _nested_median_t(panel, tmp) -> tuple[float, tuple]:
    from ml_route_v2.pipeline import _daily_t

    cfgs = [c for c in CONFIGS if c.config_id in SHUFFLE_CONFIGS]
    res = nested_cpcv(panel, cfgs, score_fn_for(risk_table(panel)),
                      ledger=ConfigLedger(tmp / "ledger.jsonl"), state_dir=tmp / "cpcv")
    ts = [_daily_t(res.path_daily[c].to_numpy()) for c in res.path_daily.columns]
    return float(np.median(ts)), res.selected


def test_shuffled_target_fails_gate0_and_has_no_nested_edge(tmp_path) -> None:
    panel = g0_panel(STRONG_EDGE_C)
    _tests, verdict = run_gate0(panel, tmp_path / "control", filtered=True)
    t_control, _ = _nested_median_t(panel, tmp_path / "control")
    assert verdict.passed and t_control >= 3.0  # the planted edge is found when y is intact
    shuffled = shuffle_targets(panel, seed=SEED)
    _tests, verdict = run_gate0(shuffled, tmp_path / "shuffled", filtered=True)
    t_shuffled, _selected = _nested_median_t(shuffled, tmp_path / "shuffled")
    assert not verdict.passed
    assert abs(t_shuffled) < 2.0, t_shuffled


def test_within_date_shuffle_is_not_a_null_here_finding(tmp_path) -> None:
    """Reported to the lead (S-1): with cross-product lead features (G17), a WITHIN-DATE shuffle
    hands a row the target of another product's earlier decision on the same date, a move that
    ended before the row's own decision time and that its lagged lead returns read causally. The
    planted edge then survives the shuffle, so the canary uses the across-date shuffle above."""
    shuffled = shuffle_targets(g0_panel(STRONG_EDGE_C), seed=SEED, within_dates=True)
    _tests, verdict = run_gate0(shuffled, tmp_path, filtered=True)
    assert verdict.passed  # documents the observation; not a leak in the pipeline


# ------------------------------------------------------------------ 4. peeking normalizer ----
def _perturbed_from(raw: pd.DataFrame, rows: pd.DataFrame, mask: np.ndarray) -> pd.DataFrame:
    moved = raw.copy()
    moved.loc[mask, :] = moved.loc[mask, :].to_numpy() * 7.0 + 50.0
    return moved


def test_peeking_normalizers_are_caught_and_zscore_causal_is_not() -> None:
    rows, raw = raw_rows()
    kw = {"window_dates": 40, "min_dates": 10}
    days = rows["trade_date"].to_numpy()
    cut = np.unique(days)[60]
    later = days >= cut
    compare = days < cut  # rows whose statistics read only dates before ``cut``
    moved = _perturbed_from(raw, rows, later)
    normalizer_check(zscore_causal, raw, rows, ["f1", "f2"], moved, compare, **kw)
    with pytest.raises(PerturbationLeak):
        normalizer_check(zscore_peek_future, raw, rows, ["f1", "f2"], moved, compare)
    # current date: move the t3 rows of one date; that date's t1 rows must not move
    t3 = (days == cut) & (rows["t_index"].to_numpy() == 3)
    t1 = (days == cut) & (rows["t_index"].to_numpy() == 1)
    moved_today = _perturbed_from(raw, rows, t3)
    normalizer_check(zscore_causal, raw, rows, ["f1", "f2"], moved_today, t1, **kw)
    with pytest.raises(PerturbationLeak):
        normalizer_check(zscore_peek_today, raw, rows, ["f1", "f2"], moved_today, t1)


# ------------------------------------------------------------------ 5. selection sees test ----
def _small_cpcv_inputs():
    panel = g0_panel(STRONG_EDGE_C)
    cfgs = [c for c in CONFIGS if c.config_id == "ridge_l0.1_k1.5_h60"]
    return panel, cfgs


def test_score_fn_returning_test_block_pnl_is_refused(tmp_path) -> None:
    panel, cfgs = _small_cpcv_inputs()
    all_dates = pd.DatetimeIndex(pd.to_datetime(panel.frame["trade_date"]).unique())

    def leaky(rows, r_hat, config):  # reads the whole panel: every date, the test block too
        return SplitScore(1.0, len(rows), pd.Series(1.0, index=all_dates))

    with pytest.raises(LeakageError, match="outside the validation set"):
        nested_cpcv(panel, cfgs, leaky, ledger=ConfigLedger(tmp_path / "l.jsonl"),
                    state_dir=tmp_path / "cpcv")


def test_score_fn_counting_rows_it_was_not_given_is_refused(tmp_path) -> None:
    panel, cfgs = _small_cpcv_inputs()
    n_all = len(panel.frame)

    def leaky(rows, r_hat, config):
        days = pd.DatetimeIndex(pd.to_datetime(rows["trade_date"]).unique())
        return SplitScore(1.0, n_all, pd.Series(0.0, index=days))

    with pytest.raises(LeakageError, match="trades on"):
        nested_cpcv(panel, cfgs, leaky, ledger=ConfigLedger(tmp_path / "l.jsonl"),
                    state_dir=tmp_path / "cpcv")


def test_inner_fold_handed_an_outer_test_block_is_refused(tmp_path, monkeypatch) -> None:
    panel, cfgs = _small_cpcv_inputs()

    def leaky_inner(outer, blocks, embargo=1):
        b = outer.test_blocks[0]  # the selection step's fold tests an OUTER test block
        test = frozenset(blocks[b])
        train = frozenset(outer.train_dates)
        return (cpcv.Split(0, (b,), train, test, frozenset()),)

    monkeypatch.setattr(cpcv, "inner_splits", leaky_inner)
    with pytest.raises(LeakageError, match="outer test or embargo"):
        nested_cpcv(panel, cfgs, score_fn_for(risk_table(panel)),
                    ledger=ConfigLedger(tmp_path / "l.jsonl"), state_dir=tmp_path / "cpcv")


# ------------------------------------------------------------------ 6. label overlap ----
def test_purge_removes_a_training_label_that_crosses_into_a_test_date() -> None:
    dates = list(pd.bdate_range("2021-06-01", periods=12).date)
    blocks = cpcv.calendar_blocks(dates)
    split = next(s for s in cpcv.outer_splits(blocks) if s.test_blocks == (2, 3))
    hour = 3_600_000_000_000
    td = np.array(dates, dtype="datetime64[D]")
    t_ns = td.astype("datetime64[ns]").astype(np.int64) + 15 * hour
    x_ns = t_ns + hour
    planted = 1  # date index 1: a training date, not an embargo date
    assert dates[planted] in split.train_dates
    train, _test = cpcv.split_masks(split, td, t_ns, x_ns)
    assert train[planted]  # control: an intraday label stays in training
    x_bad = x_ns.copy()
    x_bad[planted] = t_ns[5] + 30 * 60_000_000_000  # its exit crosses into test date index 5
    assert dates[5] in split.test_dates
    train_bad, test_bad = cpcv.split_masks(split, td, t_ns, x_bad)
    assert not train_bad[planted]
    leaked = train_bad.copy()
    leaked[planted] = True
    with pytest.raises(LeakageError, match="overlaps a test date"):
        cpcv.assert_fold(split, td, t_ns, x_bad, leaked, test_bad)


# ------------------------------------------------------------------ 7. one-minute shift ----
def shifted_world():
    return world(("MNQ",), PERT_FIRST, PERT_LAST, seed=SEED + 2,
                 plant={"kind": "shift", "roots": ("NQ",), "minutes": -1})


def mnq_features(ctx) -> pd.DataFrame:
    sig = compute_signals(ctx, ["g01_ret30", "g02_ret60", "g03_ret120", "g04_ret_day"])
    return sig[[c for c in sig.columns if c.startswith("raw_")]]


def test_shifted_product_leaks_into_features_and_the_perturbation_test_catches_it() -> None:
    w = shifted_world()
    cuts = cuts_of_date(w, PERT_DAY)
    with pytest.raises(PerturbationLeak, match="raw_g0"):
        perturbation_check(w, mnq_features, cuts, seed=15, shift_minutes={"NQ": -1})


def test_shifted_product_fails_the_session_grid_guard_and_the_pipeline_refuses(tmp_path) -> None:
    w = shifted_world()
    with pytest.raises(BarGridError, match="NQ"):
        assert_bars_on_session_grid(w.bars)
    with pytest.raises(BarGridError):
        run_pipeline(w, state_dir=tmp_path, configs=CONFIGS[:1], timing=False)


def test_control_unshifted_bars_pass_the_session_grid_guard() -> None:
    w = pert_world()
    assert_bars_on_session_grid(w.bars)
    perturbation_check(w, mnq_features, cuts_of_date(w, PERT_DAY)[:2], seed=16)


# ------------------------------------------------------------------ 8. Gate 0 canaries ----
def test_gate0_a_pure_noise_fails(tmp_path) -> None:
    _tests, verdict = run_gate0(g0_panel(None), tmp_path, filtered=True)
    assert not verdict.passed
    assert verdict.n_tests > 3 * len(REGISTRY)


def _b_tests(tests):
    return [t for t in tests if t.family == "B"]


def _ridge_rhat(panel, horizon: str = "h60"):
    data = horizon_data(panel, horizon)
    model = fit_model(ridge_spec(0.1), data.X, data.y)
    return data, predict(model, data.X) * data.sigma


def _trades_per_k(data, r_hat, horizon: str = "h60") -> dict[float, int]:
    cl = data.rows[f"cost_long_{horizon}"].to_numpy(np.float64)
    cs = data.rows[f"cost_short_{horizon}"].to_numpy(np.float64)
    return {k: int((cost_gate(r_hat, cl, cs, k)[0] != 0).sum()) for k in COST_GATE_KS}


def _oracle_rhat(data, edge_c: float) -> np.ndarray:
    """E[r | x] = edge x sign(x): the planted conditional mean (sign of the 60-minute return)."""
    edge = np.array([edge_c * nominal_cost_ticks(r) for r in data.rows["root"]])
    return edge * np.sign(data.rows["z_g02_ret60"].to_numpy(np.float64))


def test_gate0_b_planted_gross_edge_passes_and_the_cost_gate_trades_it(tmp_path) -> None:
    panel = g0_panel(STRONG_EDGE_C)
    tests, verdict = run_gate0(panel, tmp_path, filtered=True)
    assert verdict.passed
    passing = [t for t in _b_tests(tests) if t.test_id in verdict.passing]
    assert any(t.horizon == "h60" and t.mean >= 2.5 * t.cost_ticks for t in passing)
    data, r_hat = _ridge_rhat(panel)
    trades = _trades_per_k(data, r_hat)
    assert trades[COST_GATE_KS[0]] > 100, trades


def test_gate0_c_binary_edge_between_bars_passes_gate0(tmp_path) -> None:
    panel = g0_panel(MID_EDGE_C, LOW_SIGMA_C)
    tests, verdict = run_gate0(panel, tmp_path, filtered=False)
    assert verdict.passed
    h60 = [t for t in _b_tests(tests) if t.horizon == "h60"]
    assert h60 and all(GATE0_COST_MULTIPLE * t.cost_ticks <= t.mean < 2.5 * t.cost_ticks
                       for t in h60), [(t.root, t.mean, t.cost_ticks) for t in h60]
    assert any(t.test_id in verdict.passing for t in h60)


def _mid_edge_oracle():
    panel = g0_panel(MID_EDGE_C, LOW_SIGMA_C)
    data = horizon_data(panel, "h60")
    oracle = _oracle_rhat(data, MID_EDGE_C)
    side_cost = np.where(oracle > 0, data.rows["cost_long_h60"], data.rows["cost_short_h60"])
    return data, oracle, np.abs(oracle) / side_cost


def test_gate0_c_binary_edge_is_rejected_at_every_k_under_the_net_reading(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """The literal F7 reading (selectable, no longer the default): |r_hat| - c > k c needs a
    predicted gross above 2.5 c, so an edge in [1.5 c, 2.5 c) is never traded."""
    monkeypatch.setattr(v2c, "COST_GATE_READING", "net")
    data, oracle, ratio = _mid_edge_oracle()
    assert np.mean((ratio >= GATE0_COST_MULTIPLE) & (ratio < 2.5)) > 0.95  # a sub-hurdle edge
    assert _trades_per_k(data, oracle) == dict.fromkeys(COST_GATE_KS, 0)


def test_gate0_c_binary_edge_is_traded_by_the_k15_gate_under_the_gross_reading() -> None:
    """V23 item 1 (the default): |r_hat| > k c. The same [1.5 c, 2.5 c) edge is NOT rejected by
    the k = 1.5 gate where the predictions exceed 1.5 c: each k trades exactly the rows whose
    predicted gross exceeds k round trips, nearly every row at k = 1.5."""
    assert v2c.COST_GATE_READING == "gross"
    data, oracle, ratio = _mid_edge_oracle()
    trades = _trades_per_k(data, oracle)
    assert trades == {k: int((ratio > k).sum()) for k in COST_GATE_KS}
    assert trades[COST_GATE_KS[0]] > 0.95 * len(ratio)
    assert trades[COST_GATE_KS[0]] > trades[COST_GATE_KS[1]] >= trades[COST_GATE_KS[2]]


@pytest.mark.xfail(strict=True, reason="reported to lead: C-1 ridge extrapolates a bounded "
                   "(sign) edge linearly in z, so its predicted gross passes 2.5 c on large-|z| "
                   "rows although the true edge is 2 c; canary (c) under the net reading holds "
                   "for the true conditional mean and bounded predictions only")
def test_gate0_c_binary_edge_ridge_predictions_are_rejected_at_every_k_under_net(
        monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(v2c, "COST_GATE_READING", "net")
    panel = g0_panel(MID_EDGE_C, LOW_SIGMA_C)
    data, r_hat = _ridge_rhat(panel)
    assert _trades_per_k(data, r_hat) == dict.fromkeys(COST_GATE_KS, 0)


def test_gate0_d_sub_cost_edge_fails_gate0_and_the_cost_gate_rejects_it(tmp_path) -> None:
    """Under the gross default (V23 item 1): Gate 0 fails and the true conditional mean (0.5 c)
    is rejected at every k. The ridge predictions' side of this canary is split below: rejected
    at every k under the net reading; under the gross reading see the strict xfail (C-1)."""
    assert v2c.COST_GATE_READING == "gross"
    panel = g0_panel(SUB_EDGE_C, LOW_SIGMA_C)
    tests, verdict = run_gate0(panel, tmp_path, filtered=False)
    assert not verdict.passed
    h60 = [t for t in _b_tests(tests) if t.horizon == "h60"]
    assert h60 and all(t.mean < GATE0_COST_MULTIPLE * t.cost_ticks for t in h60)
    data = horizon_data(panel, "h60")
    assert _trades_per_k(data, _oracle_rhat(data, SUB_EDGE_C)) == \
        dict.fromkeys(COST_GATE_KS, 0)


def test_gate0_d_sub_cost_edge_ridge_predictions_rejected_at_every_k_under_net(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """The literal net reading (hurdle 2.5 c at k = 1.5): the ridge predictions of a 0.5 c edge,
    bypassing Gate 0, are rejected at every k (the E.11 canary, pinned)."""
    monkeypatch.setattr(v2c, "COST_GATE_READING", "net")
    data, r_hat = _ridge_rhat(g0_panel(SUB_EDGE_C, LOW_SIGMA_C))
    assert _trades_per_k(data, r_hat) == dict.fromkeys(COST_GATE_KS, 0)


@pytest.mark.xfail(strict=True, reason="reported to lead (E.12, V23Coder): under the gross "
                   "reading's 1.5 c hurdle, ridge's linear extrapolation of a bounded 0.5 c "
                   "edge (C-1) passes the k = 1.5 gate on a few large-|z| rows (4 in this "
                   "world); Gate 0 still fails the edge and the true conditional mean is "
                   "rejected at every k")
def test_gate0_d_sub_cost_edge_ridge_predictions_rejected_at_every_k_under_gross() -> None:
    assert v2c.COST_GATE_READING == "gross"
    data, r_hat = _ridge_rhat(g0_panel(SUB_EDGE_C, LOW_SIGMA_C))
    assert _trades_per_k(data, r_hat) == dict.fromkeys(COST_GATE_KS, 0)


# ------------------------------------------------------------------ window canary ----
def test_window_guard_refuses_a_planted_row_on_or_after_2024_03_01() -> None:
    panel = g0_panel(None)
    assert_window(panel, "train")
    planted = panel.frame.iloc[[0]].copy()
    planted["trade_date"] = pd.Timestamp("2024-03-01")
    with pytest.raises(WindowError):
        assert_window(pd.concat([panel.frame, planted]), "train")


def test_pipeline_refuses_a_world_that_reaches_2024_03_01(tmp_path) -> None:
    w = world(("MNQ",), date(2024, 2, 20), date(2024, 3, 5), seed=SEED, warmup_dates=5)
    with pytest.raises(WindowError):
        run_pipeline(w, state_dir=tmp_path, configs=CONFIGS[:1], timing=False)
