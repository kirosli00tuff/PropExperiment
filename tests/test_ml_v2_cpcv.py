"""ml_route_v2.cpcv: blocks, splits, purge, embargo, paths, nested CPCV, PBO and DSR (V2.9).

Synthetic data only. make_panel builds a small Panel-like object with the interfaces section 4
columns; stub_score is a simple selection metric (cost gate, net ticks per date, daily Sharpe).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, timedelta
from itertools import combinations

import numpy as np
import pandas as pd
import pytest

import ml_route_v2.cpcv as cpcv
from funnel.multiple_comparisons import deflated_sharpe_ratio
from ml_route_v2.configs import CONFIGS, CONFIGS_BY_ID, ConfigLedger, SplitScore, tie_break_key
from ml_route_v2.cpcv import (
    LeakageError,
    Split,
    StateMismatchError,
    assemble_paths,
    assert_fold,
    calendar_blocks,
    dsr_at_n,
    final_selection,
    inner_splits,
    nested_cpcv,
    outer_splits,
    pbo_cscv,
    split_masks,
)
from ml_route_v2.decide import cost_gate

NS_MIN = 60_000_000_000
HORIZON_MIN = {"h60": 60, "h120": 120, "hF": None}


@dataclass(frozen=True)
class FakePanel:
    frame: pd.DataFrame
    feature_cols: tuple[str, ...]
    signal_names: tuple[str, ...]
    horizons: tuple[str, ...]
    avail_max_ts_ns: np.ndarray


def make_panel(n_dates: int = 120, roots: tuple[str, ...] = ("AA", "BB"), n_signals: int = 3, *,
               seed: int = 0, edge: float = 0.0, sigma: float = 10.0, cost: float = 1.0,
               first: date = date(2020, 1, 6)) -> FakePanel:
    """Three decisions per (root, date); y_norm = edge x z_s0 + N(0, 1) per horizon."""
    rng = np.random.default_rng(seed)
    days = pd.bdate_range(first, periods=n_dates).values.astype("datetime64[ns]")
    per_day = len(roots) * 3
    n = n_dates * per_day
    trade_date = np.repeat(days, per_day)
    root = np.tile(np.repeat(np.array(roots), 3), n_dates)
    t_index = np.tile(np.array([1, 2, 3], dtype=np.int8), n_dates * len(roots))
    day_ns = trade_date.astype(np.int64)
    decision = day_ns + (14 * 60 + 30 * t_index.astype(np.int64)) * NS_MIN
    flatten = day_ns + 20 * 60 * NS_MIN
    cluster = np.array(["K1" if roots.index(r) % 2 == 0 else "K2" for r in root])
    cols: dict[str, np.ndarray] = {
        "root": root, "path_root": root, "cluster": cluster, "group": np.full(n, "equity"),
        "trade_date": trade_date, "t_index": t_index, "decision_ts_ns": decision,
        "flatten_ts_ns": flatten}
    signals = tuple(f"s{i}" for i in range(n_signals))
    z = rng.standard_normal((n, n_signals))
    for i, s in enumerate(signals):
        cols[f"z_{s}"] = z[:, i]
    for s in signals:
        cols[f"app_{s}"] = np.ones(n)
    for r in roots:
        cols[f"id_root_{r}"] = (root == r).astype(np.float64)
    for k in ("K1", "K2"):
        cols[f"id_cluster_{k}"] = (cluster == k).astype(np.float64)
    cols["entry_price"] = np.full(n, 100.0)
    # targets.py's release-window flag (V23 item 11): no releases in this fake panel
    cols["release_window"] = np.zeros(n, dtype=bool)
    cols["sigma_d"] = np.full(n, sigma)
    for h, minutes in HORIZON_MIN.items():
        y_norm = edge * z[:, 0] + rng.standard_normal(n)
        cols[f"y_gross_{h}"] = y_norm * sigma
        cols[f"cost_long_{h}"] = np.full(n, cost)
        cols[f"cost_short_{h}"] = np.full(n, cost)
        cols[f"exit_ts_ns_{h}"] = decision + minutes * NS_MIN if minutes else flatten
        cols[f"y_norm_{h}"] = y_norm
        cols[f"ok_{h}"] = np.ones(n, dtype=bool)
    frame = pd.DataFrame(cols)
    features = tuple([f"z_{s}" for s in signals] + [f"app_{s}" for s in signals]
                     + [f"id_root_{r}" for r in roots] + ["id_cluster_K1", "id_cluster_K2"])
    return FakePanel(frame, features, signals, tuple(HORIZON_MIN), decision.copy())


def stub_score(rows: pd.DataFrame, r_hat: np.ndarray, config) -> SplitScore:
    """Cost gate, net ticks per trade, summed per date; daily Sharpe (population sd)."""
    h = config.horizon
    cl = rows[f"cost_long_{h}"].to_numpy()
    cs = rows[f"cost_short_{h}"].to_numpy()
    side, _ = cost_gate(r_hat, cl, cs, config.k)
    gross = side * rows[f"y_gross_{h}"].to_numpy()
    pnl = np.where(side != 0, gross - np.where(side > 0, cl, cs), 0.0)
    daily = pd.Series(pnl, index=rows["trade_date"].to_numpy()).groupby(level=0).sum()
    sd = float(daily.std(ddof=0))
    sharpe = float(daily.mean()) / sd if sd > 0 else float("nan")
    return SplitScore(sharpe, int((side != 0).sum()), daily)


class CountingScore:
    """stub_score with a call counter and an optional simulated crash."""

    def __init__(self, crash_after: int | None = None) -> None:
        self.calls = 0
        self.crash_after = crash_after

    def __call__(self, rows, r_hat, config):
        if self.crash_after is not None and self.calls >= self.crash_after:
            raise RuntimeError("simulated crash")
        self.calls += 1
        return stub_score(rows, r_hat, config)


RIDGE_H60 = tuple(c for c in CONFIGS if c.model.kind == "ridge" and c.horizon == "h60")


def _dates(n: int) -> list[date]:
    return [date(2020, 1, 1) + timedelta(days=i) for i in range(n)]


# ------------------------------------------------------------------ blocks and splits ----
def test_calendar_blocks_floor_and_remainder_from_given_dates():
    dates = _dates(125)
    blocks = calendar_blocks(list(reversed(dates)) + dates[:10])  # unsorted, duplicated
    assert [len(b) for b in blocks] == [20, 20, 20, 20, 20, 25]
    assert blocks[0][0] == dates[0] and blocks[-1][-1] == dates[-1]
    assert [d for b in blocks for d in b] == dates
    with pytest.raises(cpcv.CPCVError):
        calendar_blocks(dates[:5])


def test_outer_splits_test_embargo_and_train_dates():
    dates = _dates(60)
    blocks = calendar_blocks(dates)
    splits = outer_splits(blocks)
    assert len(splits) == 15
    assert [s.test_blocks for s in splits] == list(combinations(range(6), 2))
    for s in splits:
        assert s.test_dates == {d for b in s.test_blocks for d in blocks[b]}
        assert not (s.train_dates & s.test_dates or s.train_dates & s.embargo_dates
                    or s.test_dates & s.embargo_dates)
        assert s.train_dates | s.test_dates | s.embargo_dates == set(dates)
    s01 = splits[0]  # blocks 0 and 1 adjacent: one embargo date, after block 1
    assert s01.embargo_dates == {blocks[2][0]}
    s24 = next(s for s in splits if s.test_blocks == (2, 4))
    assert s24.embargo_dates == {blocks[1][-1], blocks[3][0], blocks[3][-1], blocks[5][0]}


def test_assemble_paths_five_paths_each_block_once_each_unit_once():
    splits = outer_splits(calendar_blocks(_dates(60)))
    paths = assemble_paths(splits)
    assert len(paths) == 5
    used = set()
    for path in paths:
        assert sorted(path) == list(range(6))
        for b, s in path.items():
            assert b in splits[s].test_blocks
            used.add((b, s))
    assert len(used) == 30  # every (block, split) test unit appears in exactly one path
    assert paths[0][0] == 0 and paths[4][0] == 4 and paths[0][5] == 4


def test_inner_splits_stay_inside_the_outer_training_dates():
    blocks = calendar_blocks(_dates(60))
    for outer in outer_splits(blocks):
        folds = inner_splits(outer, blocks)
        assert len(folds) == 4
        assert sorted(b for f in folds for b in f.test_blocks) == sorted(
            set(range(6)) - set(outer.test_blocks))
        forbidden = outer.test_dates | outer.embargo_dates
        for f in folds:
            assert not ((f.train_dates | f.test_dates | f.embargo_dates) & forbidden)
            assert f.train_dates | f.test_dates <= outer.train_dates
            assert not f.train_dates & (f.test_dates | f.embargo_dates)


def test_planted_inner_fold_reading_an_outer_test_date_is_caught():
    blocks = calendar_blocks(_dates(60))
    outer = outer_splits(blocks)[3]
    good = inner_splits(outer, blocks)[0]
    leak = next(iter(outer.test_dates))
    bad = Split(good.index, good.test_blocks, good.train_dates | {leak}, good.test_dates,
                good.embargo_dates)
    with pytest.raises(LeakageError, match="outer test or embargo"):
        cpcv._assert_inner_isolated(outer, bad)
    leak_emb = next(iter(outer.embargo_dates))
    bad2 = Split(good.index, good.test_blocks, good.train_dates, good.test_dates | {leak_emb},
                 good.embargo_dates)
    with pytest.raises(LeakageError):
        cpcv._assert_inner_isolated(outer, bad2)


# ------------------------------------------------------------------ purge ----
def _row_table(dates: list[date]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    days = np.array(dates, dtype="datetime64[D]")
    t = days.astype("datetime64[ns]").astype(np.int64) + 15 * 60 * NS_MIN
    return days, t, t + 60 * NS_MIN


def test_purge_removes_a_label_overlapping_the_test_fold():
    dates = _dates(60)
    blocks = calendar_blocks(dates)
    split = outer_splits(blocks)[next(i for i, s in enumerate(outer_splits(blocks))
                                      if s.test_blocks == (2, 4))]
    days, t, x = _row_table(dates)
    # plant: a training row two dates before block 2 whose exit runs into block 2's first date
    i_plant = dates.index(blocks[2][0]) - 2
    x_planted = x.copy()
    x_planted[i_plant] = t[dates.index(blocks[2][0])] + NS_MIN
    train, test = split_masks(split, days, t, x_planted)
    assert days[i_plant].item() in split.train_dates
    assert not train[i_plant]  # purged
    assert train[i_plant - 1]  # its neighbour without overlap is kept
    assert test.sum() == len(split.test_dates)
    assert not train[[dates.index(d) for d in split.embargo_dates]].any()  # embargo
    assert_fold(split, days, t, x_planted, train, test)
    unpurged = np.isin(days, np.array(sorted(split.train_dates), dtype="datetime64[D]"))
    with pytest.raises(LeakageError, match="overlaps a test date"):
        assert_fold(split, days, t, x_planted, unpurged, test)


def test_purge_is_on_timestamps_not_dates():
    dates = _dates(60)
    split = outer_splits(calendar_blocks(dates))[0]
    days, t, x = _row_table(dates)
    train0, _ = split_masks(split, days, t, x)
    assert train0.sum() == len(split.train_dates)  # intraday holds: nothing purged


# ------------------------------------------------------------------ nested CPCV ----
def test_nested_cpcv_selects_registers_first_and_assembles_paths(tmp_path, monkeypatch):
    panel = make_panel(edge=0.5)
    ledger = ConfigLedger(tmp_path / "ledger.jsonl")
    seen = []
    real_fit = cpcv.fit_model

    def spy_fit(spec, X, y, **kw):
        seen.append(ledger.n_registered("config"))
        return real_fit(spec, X, y, **kw)

    monkeypatch.setattr(cpcv, "fit_model", spy_fit)
    res = nested_cpcv(panel, RIDGE_H60, stub_score, ledger=ledger, state_dir=tmp_path / "s")
    assert seen and min(seen) == len(RIDGE_H60)  # every config registered before the first fit
    assert len(seen) == 15 * (4 + 1) * 3  # one fit per (split, fold, model): k shares a fit
    assert len(res.selected) == 15 and all(s is not None for s in res.selected)
    assert all(sha is not None for sha in res.selected_sha256)
    n_dates = panel.frame["trade_date"].nunique()
    assert res.path_daily.shape == (n_dates, 5)
    assert res.config_daily.shape == (n_dates, len(RIDGE_H60))
    assert res.config_path_sharpes.shape == (len(RIDGE_H60), 5)
    assert len(res.outer_table) == 15 * len(RIDGE_H60)
    assert len(res.inner_table) == 15 * len(RIDGE_H60)
    assert res.path_daily.to_numpy().mean() > 0  # the planted edge survives net of cost
    # PBO matrix: a date's value is the mean over the 5 splits that test its block
    cid = RIDGE_H60[0].config_id
    d0 = res.blocks[0][3]
    vals = [res.outer_table.query("config_id == @cid and split == @s").shape[0]
            for s in range(15)]
    assert vals == [1] * 15
    units = [json.loads(line) for line in (tmp_path / "s" / cpcv.UNITS_FILE).read_text()
             .splitlines()[1:]]
    outer_vals = [u["daily"].get(d0.isoformat(), 0.0) for u in units
                  if u["unit"] == "outer" and u["config_id"] == cid
                  and 0 in res.splits[u["outer"]].test_blocks]
    assert len(outer_vals) == 5
    assert res.config_daily.loc[d0, cid] == pytest.approx(np.mean(outer_vals))


def test_nested_cpcv_is_deterministic(tmp_path):
    panel = make_panel(edge=0.3, seed=4)
    a = nested_cpcv(panel, RIDGE_H60, stub_score, ledger=ConfigLedger(tmp_path / "a.jsonl"),
                    state_dir=tmp_path / "a")
    b = nested_cpcv(panel, RIDGE_H60, stub_score, ledger=ConfigLedger(tmp_path / "b.jsonl"),
                    state_dir=tmp_path / "b")
    assert a.selected == b.selected and a.selected_sha256 == b.selected_sha256
    pd.testing.assert_frame_equal(a.path_daily, b.path_daily)
    pd.testing.assert_frame_equal(a.config_daily, b.config_daily)


def test_nested_cpcv_resumes_after_a_crash(tmp_path):
    panel = make_panel(edge=0.4, seed=2)
    fresh = CountingScore()
    want = nested_cpcv(panel, RIDGE_H60, fresh, ledger=ConfigLedger(tmp_path / "f.jsonl"),
                       state_dir=tmp_path / "fresh")
    score = CountingScore(crash_after=250)
    with pytest.raises(RuntimeError, match="simulated crash"):
        nested_cpcv(panel, RIDGE_H60, score, ledger=ConfigLedger(tmp_path / "l.jsonl"),
                    state_dir=tmp_path / "s")
    units = tmp_path / "s" / cpcv.UNITS_FILE
    done = len(units.read_text().splitlines()) - 1
    assert done == 250
    with units.open("a") as fh:  # a crash mid-line leaves a fragment
        fh.write('{"unit": "inner", "config_')
    score.crash_after, score.calls = None, 0
    got = nested_cpcv(panel, RIDGE_H60, score, ledger=ConfigLedger(tmp_path / "l.jsonl"),
                      state_dir=tmp_path / "s")
    assert score.calls == fresh.calls - done  # finished units are skipped
    assert got.selected == want.selected
    pd.testing.assert_frame_equal(got.path_daily, want.path_daily)
    pd.testing.assert_frame_equal(got.config_daily, want.config_daily)


def test_state_dir_from_other_inputs_is_refused(tmp_path):
    ledger = ConfigLedger(tmp_path / "l.jsonl")
    nested_cpcv(make_panel(seed=1), RIDGE_H60[:3], stub_score, ledger=ledger,
                state_dir=tmp_path / "s")
    with pytest.raises(StateMismatchError):
        nested_cpcv(make_panel(seed=2), RIDGE_H60[:3], stub_score, ledger=ledger,
                    state_dir=tmp_path / "s")


def test_planted_inner_split_leak_makes_nested_cpcv_raise(tmp_path, monkeypatch):
    real = cpcv.inner_splits

    def leaky(outer, blocks, *a, **kw):
        folds = real(outer, blocks, *a, **kw)
        f0 = folds[0]
        bad = Split(f0.index, f0.test_blocks, f0.train_dates | outer.embargo_dates,
                    f0.test_dates, f0.embargo_dates)
        return (bad,) + folds[1:]

    monkeypatch.setattr(cpcv, "inner_splits", leaky)
    with pytest.raises(LeakageError, match="outer test or embargo"):
        nested_cpcv(make_panel(), RIDGE_H60[:3], stub_score,
                    ledger=ConfigLedger(tmp_path / "l.jsonl"), state_dir=tmp_path / "s")


def test_row_level_isolation_guard_catches_an_overlapping_inner_label():
    panel = make_panel(n_dates=60)
    data = cpcv.horizon_data(panel, "h60")
    blocks = calendar_blocks(np.unique(data.days).tolist())
    outer = outer_splits(blocks)[0]
    otrain, otest = split_masks(outer, data.days, data.t_ns, data.x_ns)
    cpcv._assert_rows_isolated(outer, data, otest, otrain)
    with pytest.raises(LeakageError):
        cpcv._assert_rows_isolated(outer, data, otest, otrain | otest)


def test_a_score_fn_that_reads_the_test_block_is_detected(tmp_path):
    panel = make_panel(edge=0.5)

    def peeking(rows, r_hat, config):
        honest = stub_score(rows, r_hat, config)
        everything = panel.frame  # reads beyond the rows it was given
        daily = pd.Series(0.0, index=everything["trade_date"].unique())
        return SplitScore(honest.sharpe, honest.n_trades, daily)

    with pytest.raises(LeakageError, match="outside the validation set"):
        nested_cpcv(panel, RIDGE_H60[:3], peeking, ledger=ConfigLedger(tmp_path / "l.jsonl"),
                    state_dir=tmp_path / "s")

    def overcounting(rows, r_hat, config):
        honest = stub_score(rows, r_hat, config)
        return SplitScore(honest.sharpe, len(panel.frame), honest.daily)

    with pytest.raises(LeakageError, match="trades"):
        nested_cpcv(panel, RIDGE_H60[:3], overcounting,
                    ledger=ConfigLedger(tmp_path / "l2.jsonl"), state_dir=tmp_path / "s2")


def test_score_fn_gets_a_copy_of_validation_rows_only(tmp_path):
    panel = make_panel(n_dates=60)
    before = panel.frame.copy()
    sizes = []

    def mutating(rows, r_hat, config):
        sizes.append(len(rows))
        rows["y_gross_h60"] = 0.0  # must not reach the panel
        return stub_score(rows, r_hat, config)

    nested_cpcv(panel, RIDGE_H60[:3], mutating, ledger=ConfigLedger(tmp_path / "l.jsonl"),
                state_dir=tmp_path / "s")
    pd.testing.assert_frame_equal(panel.frame, before)
    assert max(sizes) < len(panel.frame) // 2


def test_ties_go_to_the_smaller_model_and_no_eligible_config_trades_nothing(tmp_path):
    panel = make_panel(n_dates=60)

    def constant(rows, r_hat, config):
        dates = rows["trade_date"].unique()
        return SplitScore(1.0, 40, pd.Series(1.0, index=dates))

    res = nested_cpcv(panel, RIDGE_H60, constant, ledger=ConfigLedger(tmp_path / "l.jsonl"),
                      state_dir=tmp_path / "s")
    winner = min(RIDGE_H60, key=tie_break_key).config_id
    assert winner == "ridge_l1_k3_h60"
    assert set(res.selected) == {winner}

    def thin(rows, r_hat, config):
        dates = rows["trade_date"].unique()
        return SplitScore(5.0, 29, pd.Series(1.0, index=dates))  # below MIN_TRADES

    res2 = nested_cpcv(panel, RIDGE_H60, thin, ledger=ConfigLedger(tmp_path / "l2.jsonl"),
                       state_dir=tmp_path / "s2")
    assert set(res2.selected) == {None}
    assert (res2.path_daily.to_numpy() == 0).all()
    assert not res2.inner_table["eligible"].any()


def test_final_selection_reuses_outer_units_and_refits_on_all_rows(tmp_path, monkeypatch):
    panel = make_panel(edge=0.5, seed=7)
    ledger = ConfigLedger(tmp_path / "l.jsonl")
    nested_cpcv(panel, RIDGE_H60, stub_score, ledger=ledger, state_dir=tmp_path / "s")
    calls = []
    real_fit = cpcv.fit_model
    monkeypatch.setattr(cpcv, "fit_model",
                        lambda spec, X, y, **kw: calls.append(X.shape[0]) or real_fit(spec, X, y))
    fin = final_selection(panel, RIDGE_H60, stub_score, ledger=ledger, state_dir=tmp_path / "s")
    assert calls == [len(panel.frame)]  # only the final refit, on every row
    assert fin.config is not None and fin.model is not None
    assert fin.n_train_rows == len(panel.frame)
    assert ledger.n_registered("config") == len(RIDGE_H60)
    row = fin.table.set_index("config_id").loc[fin.config.config_id]
    assert row["eligible"] and row["mean_score"] == fin.table["mean_score"].max()


def test_lightgbm_configs_run_through_nested_cpcv(tmp_path):
    panel = make_panel(n_dates=60)
    cfgs = tuple(c for c in CONFIGS if c.model.model_id == "lgbm_d2" and c.horizon == "hF")
    res = nested_cpcv(panel, cfgs, stub_score, ledger=ConfigLedger(tmp_path / "l.jsonl"),
                      state_dir=tmp_path / "s")
    assert len(res.selected) == 15
    assert res.outer_table["sha256"].notna().all()


def test_admissible_pairs_restrict_the_rows(tmp_path):
    panel = make_panel(n_dates=60, roots=("AA", "BB", "CC"))
    sizes = []

    def sizing(rows, r_hat, config):
        sizes.append(set(rows["root"]))
        return stub_score(rows, r_hat, config)

    nested_cpcv(panel, RIDGE_H60[:3], sizing, ledger=ConfigLedger(tmp_path / "l.jsonl"),
                state_dir=tmp_path / "s", admissible={("AA", "h60"), ("CC", "h60"),
                                                      ("BB", "h120")})
    assert set().union(*sizes) == {"AA", "CC"}


# ------------------------------------------------------------------ PBO and DSR ----
def test_pbo_orientation_noise_near_half_dominance_near_zero():
    vals = [pbo_cscv(np.random.default_rng(s).standard_normal((400, 10)), 8)["pbo"]
            for s in range(12)]
    assert 0.35 <= float(np.mean(vals)) <= 0.65
    rng = np.random.default_rng(0)
    perf = rng.standard_normal((400, 10))
    perf[:, 3] += 1.0  # one configuration truly dominates
    assert pbo_cscv(perf, 8)["pbo"] == 0.0
    full = pbo_cscv(np.random.default_rng(1).standard_normal((800, 45)))
    assert full["n_splits"] == 12870 and full["n_strategies"] == 45 and full["n_blocks"] == 16


def test_pbo_blocks_last_takes_remainder_and_bad_input_raises():
    res = pbo_cscv(np.random.default_rng(0).standard_normal((53, 4)), 8)
    assert res["block_dates"] == [6] * 7 + [11] and res["n_dates"] == 53
    with pytest.raises(cpcv.CPCVError):
        pbo_cscv(np.zeros((5, 3)), 8)
    with pytest.raises(cpcv.CPCVError):
        pbo_cscv(np.full((40, 3), np.nan), 8)


def test_dsr_at_n_wraps_the_funnel_function():
    daily = np.random.default_rng(5).standard_normal(500) * 100 + 12
    out = dsr_at_n(daily, 243, 0.002)
    xs = daily.tolist()
    mean, sd = np.mean(xs), np.std(xs)
    skew = np.mean((daily - mean) ** 3) / sd**3
    kurt = np.mean((daily - mean) ** 4) / sd**4
    ref = deflated_sharpe_ratio(mean / sd, 500, 243, 0.002, skew, kurt)
    assert out["status"] == "computed"
    assert out["deflated_sharpe_ratio"] == pytest.approx(ref["deflated_sharpe_ratio"], rel=1e-9)
    assert dsr_at_n(np.zeros(10), 5, 0.1)["status"] == "undefined"
    assert cpcv.sharpe_variance([0.1, 0.3]) == pytest.approx(0.01)


def test_config_ids_used_in_tests_exist():
    assert all(c.config_id in CONFIGS_BY_ID for c in RIDGE_H60)


# ---- design review D-04: the risk table per split ------------------------------------------------
def _recording_score(seen: list):
    def score(rows, r_hat, config, *, risk):
        days = frozenset(pd.to_datetime(rows["trade_date"]).dt.date)
        seen.append((days, risk))
        return stub_score(rows, r_hat, config)
    return score


def test_a_volatility_spike_in_a_test_block_never_sizes_that_block(tmp_path):
    """Plant a volatility spike (y_gross x 50) on block 5's dates. Every validation set holding
    block-5 dates (outer splits testing block 5, inner folds of the splits training on it that
    hold it out) gets the same risk table as without the spike; sets that train on block 5 see
    it. Each outer split's table is cost_filter.risk_table on that split's training dates."""
    import dataclasses

    from ml_route_v2.cost_filter import risk_table

    base = make_panel(n_dates=90, edge=0.3, seed=2)
    days = np.unique(base.frame["trade_date"].to_numpy().astype("datetime64[D]")).tolist()
    blocks = calendar_blocks(days)
    spike = set(blocks[5])
    frame = base.frame.copy()
    on = pd.to_datetime(frame["trade_date"]).dt.date.isin(spike).to_numpy()
    for h in HORIZON_MIN:
        frame.loc[on, f"y_gross_{h}"] = frame.loc[on, f"y_gross_{h}"] * 50.0
    spiked = dataclasses.replace(base, frame=frame)
    seen_a, seen_b = [], []
    res = nested_cpcv(base, RIDGE_H60[:3], _recording_score(seen_a),
                      ledger=ConfigLedger(tmp_path / "a.jsonl"), state_dir=tmp_path / "a",
                      risk_fn=risk_table)
    nested_cpcv(spiked, RIDGE_H60[:3], _recording_score(seen_b),
                ledger=ConfigLedger(tmp_path / "b.jsonl"), state_dir=tmp_path / "b",
                risk_fn=risk_table)
    assert len(seen_a) == len(seen_b) == 15 * 5 * 3  # (4 inner + 1 outer) x 3 configs a split
    same = changed = 0
    for (d_a, r_a), (d_b, r_b) in zip(seen_a, seen_b, strict=True):
        assert d_a == d_b
        if d_a & spike:
            pd.testing.assert_frame_equal(r_a, r_b)  # trained without the spiked block
            same += 1
        elif not r_a.equals(r_b):
            changed += 1  # this set's training rows hold block 5
    assert same > 0 and changed > 0
    outer = {s.test_dates: s for s in res.splits}
    checked = 0
    for d_a, r_a in seen_a:
        split = outer.get(d_a)
        if split is None:
            continue
        rows = base.frame.loc[pd.to_datetime(base.frame["trade_date"]).dt.date
                              .isin(split.train_dates).to_numpy()]
        pd.testing.assert_frame_equal(r_a, risk_table(rows))
        checked += 1
    assert checked == 15 * 3


def test_risk_fn_joins_the_state_fingerprint_and_none_keeps_the_old_contract(tmp_path):
    from ml_route_v2.cost_filter import risk_table

    ledger = ConfigLedger(tmp_path / "l.jsonl")
    panel = make_panel(n_dates=60, seed=3)
    seen: list = []
    nested_cpcv(panel, RIDGE_H60[:3], _recording_score(seen), ledger=ledger,
                state_dir=tmp_path / "s", risk_fn=risk_table)
    with pytest.raises(StateMismatchError):  # the same inputs without the per-split table
        nested_cpcv(panel, RIDGE_H60[:3], stub_score, ledger=ledger, state_dir=tmp_path / "s")
    # without risk_fn the three-argument ScoreFn is called as before
    nested_cpcv(panel, RIDGE_H60[:3], stub_score, ledger=ledger, state_dir=tmp_path / "t")


def _two_block_vehicle_panel():
    """Code review C-02's scenario: MNQ and MGC on every date, MCL listed late (rows on blocks 4
    and 5 only), so splits whose training rows hold no MCL row still validate on MCL."""
    import dataclasses

    base = make_panel(n_dates=90, roots=("MNQ", "MGC", "MCL"), edge=0.5, seed=11)
    days = np.unique(base.frame["trade_date"].to_numpy().astype("datetime64[D]")).tolist()
    late = set(calendar_blocks(days)[4]) | set(calendar_blocks(days)[5])
    on = pd.to_datetime(base.frame["trade_date"]).dt.date.isin(late).to_numpy()
    keep = (base.frame["root"] != "MCL").to_numpy() | on
    return dataclasses.replace(base, frame=base.frame.loc[keep].reset_index(drop=True),
                               avail_max_ts_ns=base.avail_max_ts_ns[keep]), late


def test_a_vehicle_planted_in_two_blocks_is_skipped_as_risk_unknown_not_fatal(tmp_path):
    """C-02: with the real selection metric and the pipeline's per-split table (every root of
    the panel listed, NaN where a split has fewer than two training rows), the nested run
    finishes; the skipped candidates are counted in the unit records. A table that leaves the
    pair out altogether (cost_filter.risk_table alone) is still a contract error."""
    from ml_route_v2.cost_filter import risk_table
    from ml_route_v2.pipeline import score_fn_for, split_risk_fn
    from ml_route_v2.portfolio import PortfolioInputError

    panel, late = _two_block_vehicle_panel()
    assert sorted(set(panel.frame["root"])) == ["MCL", "MGC", "MNQ"]
    score = score_fn_for(risk_table(panel.frame))
    res = nested_cpcv(panel, RIDGE_H60[:2], score, ledger=ConfigLedger(tmp_path / "a.jsonl"),
                      state_dir=tmp_path / "a", risk_fn=split_risk_fn(panel))
    assert len(res.splits) == 15
    recs = [json.loads(line) for line in
            (tmp_path / "a" / cpcv.UNITS_FILE).read_text().splitlines()[1:]]
    assert all("n_risk_unknown" in r for r in recs)
    unknown = [r for r in recs if r["n_risk_unknown"] > 0]
    assert unknown and all(r["n_trades"] >= 0 for r in unknown)
    # every set with skipped MCL candidates trained on no or one MCL row; sets that trained on
    # both late blocks skipped nothing
    outer_by_index = {s.index: s for s in res.splits}
    for r in recs:
        if r["unit"] == "outer" and late <= outer_by_index[r["outer"]].train_dates:
            assert r["n_risk_unknown"] == 0
    with pytest.raises(PortfolioInputError, match="risk_missing_pairs"):
        nested_cpcv(panel, RIDGE_H60[:2], score, ledger=ConfigLedger(tmp_path / "b.jsonl"),
                    state_dir=tmp_path / "b", risk_fn=risk_table)
