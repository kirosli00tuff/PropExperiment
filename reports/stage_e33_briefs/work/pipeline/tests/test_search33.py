"""Tests for search33 / run_search33 (Stage E.33 SearchCoder). Synthetic tables only.

Run: uv run pytest -q reports/stage_e33_briefs/work/pipeline/tests/test_search33.py
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

HERE = Path(__file__).resolve().parent
PIPE = HERE.parent
for _p in (str(PIPE), str(HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import search33 as s  # noqa: E402
import synth_search33 as g  # noqa: E402

from screening.stage_e_verdict import moments  # noqa: E402

N_SMALL = 60
RUNNER = PIPE / "run_search33.py"


# ---------------------------------------------------------------- fixtures
@pytest.fixture(scope="module")
def small_root(tmp_path_factory):
    root = tmp_path_factory.mktemp("search33_small")
    g.write_tables(root, g.synth_dates(N_SMALL), ("F15", "T30"), seed=3, beta=2.0, excluded_every=13)
    return root


@pytest.fixture(scope="module")
def tables_f15(small_root):
    return s.load_tables(small_root, "F15", expected_n=None)


def folds_of(tables):
    return s.make_folds(tables.dates, expected_n=None)


def run_config(root, cid, threads=1):
    for k in range(1, 7):
        res = s.run_fold(root, cid, k, threads=threads, expected_n=None)
        assert res["status"] == "done", res
    return s.finalize_config(root, cid, expected_n=None)


# ---------------------------------------------------------------- P6.1 folds and ids
def test_folds_796_sizes_training_counts_and_embargo():
    dates = g.synth_dates(796)
    folds = s.make_folds(dates)
    assert [len(f.eval_dates) for f in folds] == [133, 133, 133, 133, 132, 132]
    assert [len(f.train_dates) for f in folds] == [642, 642, 642, 642, 643, 664]
    covered = [d for f in folds for d in f.eval_dates]
    assert covered == dates  # contiguous blocks, in order, each date evaluated once
    for f in folds:
        last = dates.index(f.eval_dates[-1])
        assert list(f.embargo_dates) == dates[last + 1:last + 22]
        assert not set(f.train_dates) & (set(f.eval_dates) | set(f.embargo_dates))
        first = dates.index(f.eval_dates[0])
        assert set(dates[:first]) <= set(f.train_dates)  # no date before block k is removed
        assert list(f.train_dates) == sorted(f.train_dates)
    assert folds[5].embargo_dates == ()
    with pytest.raises(ValueError):
        s.make_folds(dates[:-1])


def test_inner_split_is_latest_15_percent_rounded_up():
    for n, n_val in ((642, 97), (643, 97), (664, 100), (29, 5), (20, 3)):
        dates = g.synth_dates(n)
        tr, val = s.inner_split(dates)
        assert len(val) == n_val and list(val) == dates[-n_val:] and list(tr) == dates[:-n_val]


def test_config_ids_and_run_order():
    ids = s.all_config_ids()
    assert len(ids) == 300 and len(set(ids)) == 300
    assert ids[:3] == ["E33-S5F15L001A", "E33-S5F15L001E", "E33-S5F15L010A"]
    assert ids[9] == "E33-S5F15G3200" and ids[10] == "E33-S5F30L001A" and ids[60] == "E33-S1F15L001A"
    cfg = s.parse_config_id("E33-S2T30G3200")
    assert (cfg.set_name, cfg.label, cfg.h, cfg.family, cfg.params) == (
        "S2", "T30", 30, "LGBM", {"depth": 3, "leaf_mult": 200})
    assert len(cfg.columns) == 26 and s.parse_config_id("E33A-S5F05L100E").params == {"C": 1.0, "rho": 0.5}
    assert len(s.FEATURE_COLUMNS) == 59 and len(s.SETS["S1"]) == 23
    for bad in ("E33-S6F15L001A", "E34-S5F15L001A", "E33-S5F15L001X", "E33-S5F15L001"):
        with pytest.raises(ValueError):
            s.parse_config_id(bad)


# ---------------------------------------------------------------- LOGIT is P5's objective
def _p5_objective(B, b0, X, y, w, C, rho):
    logits = X @ B.T + b0
    logits = logits - logits.max(axis=1, keepdims=True)
    logp = logits - np.log(np.exp(logits).sum(axis=1, keepdims=True))
    nll = -logp[np.arange(len(y)), np.searchsorted([-1, 0, 1], y)]
    return C * np.sum(w * nll) + (1 - rho) / 2 * np.sum(B ** 2) + rho * np.sum(np.abs(B))


def _independent_min(X, y, w, C, rho, intercept_pen=0.0, loss_scale=1.0):
    """min over (B, b0) of loss_scale C sum w l + (1-rho)/2 |B|^2 + rho |B|_1 [+ intercept_pen/2 |b0|^2],
    by L-BFGS-B on the split B = Bp - Bn (Bp, Bn >= 0): an exact reformulation of the L1 term."""
    from scipy.optimize import minimize
    n, p = X.shape
    Y = (y[:, None] == np.array([-1, 0, 1])[None, :]).astype(float)

    def fun(v):
        Bp, Bn, b0 = v[:3 * p].reshape(3, p), v[3 * p:6 * p].reshape(3, p), v[6 * p:]
        B = Bp - Bn
        z = X @ B.T + b0
        z = z - z.max(axis=1, keepdims=True)
        P = np.exp(z)
        P /= P.sum(axis=1, keepdims=True)
        nll = -np.log(np.sum(P * Y, axis=1))
        f = loss_scale * C * np.sum(w * nll) + (1 - rho) / 2 * np.sum(B ** 2) + rho * np.sum(Bp + Bn) \
            + intercept_pen / 2 * np.sum(b0 ** 2)
        G = loss_scale * C * ((P - Y) * w[:, None]).T @ X + (1 - rho) * B
        gb = loss_scale * C * ((P - Y) * w[:, None]).sum(axis=0) + intercept_pen * b0
        return f, np.concatenate([(G + rho).ravel(), (-G + rho).ravel(), gb])

    bounds = [(0, None)] * (6 * p) + [(None, None)] * 3
    res = minimize(fun, np.zeros(6 * p + 3), jac=True, method="L-BFGS-B", bounds=bounds,
                   options={"maxiter": 20000, "ftol": 1e-15, "gtol": 1e-11})
    v = res.x
    return v[:3 * p].reshape(3, p) - v[3 * p:6 * p].reshape(3, p), v[6 * p:], res.fun


@pytest.mark.parametrize("C,rho", [(0.1, 0.5), (1.0, 0.0), (0.01, 0.5)])
def test_logit_minimises_p5_objective(C, rho):
    rng = np.random.default_rng(5)
    n, p = 400, 4
    X = rng.standard_normal((n, p))
    logits = X @ rng.standard_normal((3, p)).T + np.array([-1.5, 1.5, -0.5])
    P = np.exp(logits) / np.exp(logits).sum(axis=1, keepdims=True)
    y = np.array([-1, 0, 1])[[rng.choice(3, p=row) for row in P]]
    w = rng.uniform(0.2, 1.5, n)
    est = s.make_logit(C, rho, max_iter=200000, tol=1e-10)
    with warnings.catch_warnings():
        warnings.simplefilter("error")  # no deprecation or future warning from the spelling we use
        est.fit(X, y, sample_weight=w)
    assert list(est.classes_) == [-1, 0, 1]
    f_sk = _p5_objective(est.coef_, est.intercept_, X, y, w, C, rho)
    B, b0, f_ind = _independent_min(X, y, w, C, rho)
    assert abs(f_sk - f_ind) <= 1e-7 * max(1.0, abs(f_ind)), (f_sk, f_ind)
    P_sk = est.predict_proba(X)
    z = X @ B.T + b0
    P_ind = np.exp(z - z.max(1, keepdims=True))
    P_ind /= P_ind.sum(1, keepdims=True)
    assert np.max(np.abs(P_sk - P_ind)) < 1e-4
    # multinomial link: probabilities are the softmax of the decision function (not one-vs-rest)
    d = est.decision_function(X)
    sm = np.exp(d - d.max(1, keepdims=True))
    assert np.allclose(P_sk, sm / sm.sum(1, keepdims=True), atol=1e-12)
    # discrimination: sklearn's solution is NOT the minimiser of nearby wrong objectives
    for kw in ({"intercept_pen": 1.0 - rho if rho < 1 else 1.0}, {"loss_scale": 1.0 / np.sum(w)}):
        B2, b02, f_alt_min = _independent_min(X, y, w, C, rho, **kw)
        f_alt_at_sk = _independent_value(est.coef_, est.intercept_, X, y, w, C, rho, **kw)
        assert f_alt_at_sk > f_alt_min + 1e-4 * max(1.0, abs(f_alt_min)), kw


def _independent_value(B, b0, X, y, w, C, rho, intercept_pen=0.0, loss_scale=1.0):
    base = _p5_objective(B, b0, X, y, w, loss_scale * C, rho)
    return base + intercept_pen / 2 * np.sum(b0 ** 2)


# ---------------------------------------------------------------- scaler, mu_k, weights
def test_weighted_scaler_population_sd_and_constant_columns():
    rng = np.random.default_rng(1)
    X = rng.standard_normal((50, 3))
    X[:, 1] = 0.1  # constant: floating weighted mean != 0.1 exactly, still SD 0
    w = rng.uniform(0.1, 2, 50)
    mean, sd = s.weighted_scaler(X, w)
    m0 = np.sum(w * X[:, 0]) / np.sum(w)
    assert np.isclose(mean[0], m0) and np.isclose(sd[0], np.sqrt(np.sum(w * (X[:, 0] - m0) ** 2) / np.sum(w)))
    assert sd[1] == 0.0
    Z = s.standardise(np.vstack([X, [[1, 7, 1]]]), mean, sd)
    assert np.all(Z[:, 1] == 0.0)  # the feature is 0 in the fold, evaluation rows included


def test_class_means_weighted_and_missing_class_fails():
    y = np.array([-1, 0, 1, 1, 0])
    w = np.array([1.0, 2.0, 1.0, 3.0, 2.0])
    nl = np.array([-3.0, -1.0, 2.0, 4.0, -2.0])
    ns = np.array([2.0, -1.0, -3.0, -5.0, 0.5])
    mu_l, mu_s = s.class_means(y, w, nl, ns)
    assert mu_l == [-3.0, (2 * -1 + 2 * -2) / 4, (2 + 12) / 4] and mu_s[2] == (-3 - 15) / 4
    with pytest.raises(s.FitError):
        s.class_means(np.array([0, 1]), np.ones(2), np.zeros(2), np.zeros(2))


def test_training_rows_and_weights_passed_unchanged(tables_f15, monkeypatch):
    fold = folds_of(tables_f15)[2]
    m = s.training_mask(tables_f15, fold)
    dates = {tables_f15.dates[j] for j in np.unique(tables_f15.date_idx[m])}
    assert dates <= set(fold.train_dates) and not dates & (set(fold.eval_dates) | set(fold.embargo_dates))
    assert np.all(tables_f15.lab["row_ok"][m])
    seen = {}
    orig = s._fit_recorded

    def spy(est, X, y, w):
        seen["w"], seen["y"] = w.copy(), y.copy()
        return orig(est, X, y, w)

    monkeypatch.setattr(s, "_fit_recorded", spy)
    s.fit_fold(s.parse_config_id("E33-S1F15L010A"), tables_f15, fold)
    # the label table's per-date weights reach the fit unchanged (no cross-date renormalisation)
    assert np.array_equal(seen["w"], tables_f15.lab["w"][m]) and np.array_equal(seen["y"], tables_f15.lab["y"][m])


def test_lgbm_datasets_use_inner_blocks_and_table_weights(tables_f15, monkeypatch):
    import lightgbm
    fold = folds_of(tables_f15)[0]
    made = []
    real = lightgbm.Dataset

    def spy(data, *a, **kw):
        made.append({"n": len(data), "weight": kw.get("weight"), "reference": kw.get("reference")})
        return real(data, *a, **kw)

    monkeypatch.setattr(lightgbm, "Dataset", spy)
    s.fit_fold(s.parse_config_id("E33-S1F15G2050"), tables_f15, fold, threads=2)
    tr_dates, val_dates = s.inner_split(fold.train_dates)
    ok = tables_f15.lab["row_ok"]
    m_tr = s.date_mask(tables_f15, tr_dates) & ok
    m_val = s.date_mask(tables_f15, val_dates) & ok
    assert made[0]["n"] == m_tr.sum() and np.array_equal(made[0]["weight"], tables_f15.lab["w"][m_tr])
    assert made[1]["n"] == m_val.sum() and np.array_equal(made[1]["weight"], tables_f15.lab["w"][m_val])
    assert made[0]["reference"] is None and made[1]["reference"] is not None  # bins from inner-train


# ---------------------------------------------------------------- LT3 fold hygiene (functional)
def _perturbed(tables, row_mask, seed, features=True, labels=True):
    rng = np.random.default_rng(seed)
    X = tables.X.copy()
    lab = {k: v.copy() for k, v in tables.lab.items()}
    n = int(row_mask.sum())
    if features:
        X[row_mask] = X[row_mask] * 3.0 + 50.0 + rng.standard_normal((n, X.shape[1]))
    if labels:
        ok = row_mask & lab["row_ok"]
        lab["y"][ok] = rng.choice([-1, 0, 1], int(ok.sum()))
        lab["n_long"][ok] += 100.0
        lab["n_short"][ok] -= 100.0
        lab["w"][ok] *= 7.0
    return dataclasses.replace(tables, X=X, lab=lab)


@pytest.mark.parametrize("cid", ["E33-S5F15L001E", "E33-S5F15G3050"])
@pytest.mark.parametrize("k", [1, 3, 6])
def test_lt3_models_use_training_rows_only(tables_f15, cid, k):
    """Scaler, calibrator, booster, mu_k and coefficients are identical when every row of the
    evaluation block and its embargo, and every non-row on training dates, is changed."""
    cfg = s.parse_config_id(cid)
    fold = folds_of(tables_f15)[k - 1]
    base_model, _ = s.fit_fold(cfg, tables_f15, fold, threads=2)
    outside = s.date_mask(tables_f15, fold.eval_dates + fold.embargo_dates)
    nonrows = s.date_mask(tables_f15, fold.train_dates) & ~tables_f15.lab["row_ok"]
    pert = _perturbed(tables_f15, outside, seed=k)
    pert = _perturbed(pert, nonrows, seed=k + 10, labels=False)
    model, _ = s.fit_fold(cfg, pert, fold, threads=2)
    assert s.model_bytes(model) == s.model_bytes(base_model)


def _trees(model_str, n_iter):
    import lightgbm as lgb
    info = lgb.Booster(model_str=model_str).dump_model()["tree_info"]
    return json.dumps(info[:3 * n_iter], sort_keys=True)


def test_lgbm_bins_from_inner_train_only(tables_f15):
    """Changing inner-validation features (far outside the training range) changes no tree: the
    validation Dataset shares the inner-training bins (reference=) and only steers the stopping point."""
    cfg = s.parse_config_id("E33-S5F15G3050")
    fold = folds_of(tables_f15)[5]
    _, val_dates = s.inner_split(fold.train_dates)
    m0, _ = s.fit_lgbm(cfg, tables_f15, fold, threads=2)
    val_rows = s.date_mask(tables_f15, val_dates)
    m1, _ = s.fit_lgbm(cfg, _perturbed(tables_f15, val_rows, seed=4, labels=False), fold, threads=2)
    n = min(m0["best_iteration"], m1["best_iteration"])
    assert _trees(m0["booster"], n) == _trees(m1["booster"], n)
    tr_dates, _ = s.inner_split(fold.train_dates)  # power check: inner-train features do change trees
    m2, _ = s.fit_lgbm(cfg, _perturbed(tables_f15, s.date_mask(tables_f15, tr_dates[:5]), seed=4,
                                       labels=False), fold, threads=2)
    assert _trees(m0["booster"], 1) != _trees(m2["booster"], 1)


def test_lgbm_early_stopping_on_weighted_inner_block_loss(tables_f15):
    import lightgbm as lgb
    cfg = s.parse_config_id("E33-S5F15G2050")
    fold = folds_of(tables_f15)[0]
    model, meta = s.fit_lgbm(cfg, tables_f15, fold, threads=2)
    tr_dates, val_dates = s.inner_split(fold.train_dates)
    ok = tables_f15.lab["row_ok"]
    m_tr, m_val = s.date_mask(tables_f15, tr_dates) & ok, s.date_mask(tables_f15, val_dates) & ok
    X = tables_f15.cols(cfg.columns)
    y, w = tables_f15.lab["y"].astype(int) + 1, tables_f15.lab["w"]
    params = s.lgbm_params(2, 50, 15, 2)
    full = lgb.train(params, lgb.Dataset(X[m_tr], label=y[m_tr], weight=w[m_tr], params=params),
                     num_boost_round=s.LGBM_ROUNDS)
    losses = []
    for it in range(1, s.LGBM_ROUNDS + 1):
        P = np.clip(full.predict(X[m_val], num_iteration=it), 1e-15, 1)
        losses.append(np.sum(w[m_val] * -np.log(P[np.arange(m_val.sum()), y[m_val]])) / np.sum(w[m_val]))
        best = int(np.argmin(losses)) + 1  # first minimum (strict improvement)
        if it - best >= s.LGBM_STOP:
            break
    assert meta["best_iteration"] == best == model["best_iteration"]
    assert np.allclose(meta["inner_val_logloss"], losses[:len(meta["inner_val_logloss"])], rtol=1e-12)
    # the feval is LightGBM's weighted multi_logloss up to LightGBM's float32 storage of the weights
    p_lgb = dict(params, metric="multi_logloss")
    hist: dict = {}
    dtr = lgb.Dataset(X[m_tr], label=y[m_tr], weight=w[m_tr], params=p_lgb)
    lgb.train(p_lgb, dtr, num_boost_round=20, valid_sets=[lgb.Dataset(X[m_val], label=y[m_val], weight=w[m_val],
                                                                      reference=dtr, params=p_lgb)],
              valid_names=["v"], feval=s.weighted_mlogloss_feval(y[m_val], w[m_val]),
              callbacks=[lgb.record_evaluation(hist)])
    assert np.allclose(hist["v"]["multi_logloss"], hist["v"]["w_multi_logloss"], rtol=1e-6)
    assert np.allclose(hist["v"]["w_multi_logloss"], losses[:20], rtol=1e-12)


def test_lgbm_repeat_fits_identical_when_splits_run_out(tables_f15):
    """G3200 on the small table cannot split after a few trees; LightGBM keeps evaluating the same
    model. Repeated fits (several thread counts) must keep the same model and a best iteration that
    exists."""
    cfg = s.parse_config_id("E33-S5F15G3200")
    fold = folds_of(tables_f15)[0]
    trees = set()
    for thr in (4, 4, 3, 1, 4):
        model, meta = s.fit_lgbm(cfg, tables_f15, fold, thr)
        assert 1 <= meta["best_iteration"] <= meta["iterations_built"]
        trees.add((meta["trees_sha256"], meta["best_iteration"], json.dumps(model["cal_coef"])))
    assert len(trees) == 1


# ---------------------------------------------------------------- persisted models reproduce the OOF p
@pytest.mark.parametrize("cid", ["E33-S3F15L100E", "E33-S3T30G2200"])
def test_fold_model_roundtrip_bit_for_bit(small_root, cid):
    cfg = s.parse_config_id(cid)
    res = s.run_fold(small_root, cid, 4, threads=2, expected_n=None)
    assert res["status"] == "done"
    paths = s.fold_paths(small_root, cid, 4)
    done = json.loads(paths["done"].read_text())
    assert done["model_sha256"] == s.sha256_file(paths["model"])
    pay = s.load_fold_payload(small_root, cid, 4)
    assert pay["meta"]["model_sha256"] == done["model_sha256"]
    model = s.load_fold_model(paths["model"])
    assert model["mu_long"] == pay["mu_long"].tolist() and model["mu_short"] == pay["mu_short"].tolist()
    tables = s.load_tables(small_root, cfg.label, expected_n=None)
    fold = folds_of(tables)[3]
    X = tables.cols(cfg.columns)[s.date_mask(tables, fold.eval_dates)]
    assert np.array_equal(s.predict_proba(model, X), pay["p"])
    assert pay["p"].shape == (len(fold.eval_dates) * s.grid_size(cfg.h), 3)  # every grid minute
    # a fresh process with another thread count reproduces the same bytes
    code = ("import sys,hashlib,numpy as np;sys.path[:0]=[%r,%r];import search33 as s;"
            "t=s.load_tables(%r,%r,expected_n=None);f=s.make_folds(t.dates,expected_n=None)[3];"
            "X=t.cols(%r)[s.date_mask(t,f.eval_dates)];m=s.load_fold_model(%r);"
            "print(hashlib.sha256(np.ascontiguousarray(s.predict_proba(m,X,threads=3)).tobytes()).hexdigest())"
            % (str(PIPE), str(HERE), str(small_root), cfg.label, list(cfg.columns), str(paths["model"])))
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True,
                         cwd=s.REPO).stdout.strip()
    assert out == hashlib.sha256(np.ascontiguousarray(pay["p"]).tobytes()).hexdigest()


# ---------------------------------------------------------------- P3.5 EV rule
def test_decide_rule_and_exact_ties():
    assert s.decide(1.0, 0.5) == 1 and s.decide(0.5, 1.0) == -1
    assert s.decide(0.7, 0.7) == 0           # exact tie above 0: no trade
    assert s.decide(0.0, 0.0) == 0 and s.decide(0.0, -1.0) == 0 and s.decide(-1.0, 0.0) == 0
    assert s.decide(-0.1, -0.2) == 0 and s.decide(1e-300, -1.0) == 1 and s.decide(-0.0, 0.0) == 0
    with pytest.raises(ValueError):
        s.decide(float("nan"), 0.1)
    p = np.array([[0.2, 0.5, 0.3]])
    ev_l, ev_s = s.expected_values(p, [-3.0, -1.0, 2.0], [2.0, -1.0, -3.0])
    assert ev_l[0] == 0.2 * -3.0 + 0.5 * -1.0 + 0.3 * 2.0 and ev_s[0] == 0.2 * 2.0 + 0.5 * -1.0 + 0.3 * -3.0


# ---------------------------------------------------------------- P3.8 simulator
def _day(n=40, exit_min=5.0):
    t = np.arange(n, dtype=np.int64) * g.MIN_NS + 10**15
    side = {"made": np.ones(n, bool), "net": np.arange(n, dtype=float), "entry_ns": t + g.L_NS,
            "exit_ns": t + int(exit_min * g.MIN_NS) + g.L_NS, "flags": np.zeros(n, np.int16)}
    return t, {"long": {k: v.copy() for k, v in side.items()},
               "short": {k: (-v if k == "net" else v.copy()) for k, v in side.items()}}


def test_sim_one_position_and_next_decision_after_exit():
    t, out = _day()
    ok = np.ones(40, bool)
    trades, nm = s.simulate_date(t, ok, np.ones(40), np.zeros(40), out)
    assert [tr[0] for tr in trades] == [0, 6, 12, 18, 24, 30, 36] and nm == []  # exit t+5m+1s -> t+6m
    out["long"]["exit_ns"] = t + 3 * g.MIN_NS  # exit exactly on a grid minute: that minute decides
    trades, _ = s.simulate_date(t, ok, np.ones(40), np.zeros(40), out)
    assert [tr[0] for tr in trades][:3] == [0, 3, 6]


def test_sim_cap_entries_not_made_ties_and_short_side():
    t, out = _day(exit_min=0.01)
    ok = np.ones(40, bool)
    trades, _ = s.simulate_date(t, ok, np.ones(40), np.zeros(40), out)
    assert len(trades) == 20 and [tr[0] for tr in trades] == list(range(20))  # cap of 20
    out["long"]["made"][:3] = False
    out["long"]["flags"][:3] = 16
    trades, nm = s.simulate_date(t, ok, np.ones(40), np.zeros(40), out)
    assert [x[0] for x in nm] == [0, 1, 2] and [tr[0] for tr in trades] == list(range(3, 23))
    ok[3] = False
    trades, _ = s.simulate_date(t, ok, np.ones(40), np.zeros(40), out)
    assert trades[0][0] == 4  # entry rules gate the decision
    trades, _ = s.simulate_date(t, np.ones(40, bool), np.full(40, 0.5), np.full(40, 0.5), out)
    assert trades == []  # exact tie
    trades, _ = s.simulate_date(t, np.ones(40, bool), np.zeros(40), np.ones(40), out)
    assert trades[0][1] == -1 and trades[0][2] == -0.0 and trades[1][2] == -1.0  # short outcome fields


# ---------------------------------------------------------------- end to end: outputs, stats, determinism
def _outputs(root, cid):
    base = s.config_dir(root, cid)
    out = {"daily": pd.read_parquet(base / "daily.parquet"), "trades": pd.read_parquet(base / "trades.parquet"),
           "stats": json.loads((base / "stats.json").read_text())}
    for k in range(1, 7):
        with np.load(base / f"fold{k}.npz") as z:
            out[f"p{k}"] = z["p"].copy()
            out[f"mu{k}"] = (z["mu_long"].copy(), z["mu_short"].copy())
            out[f"trees{k}"] = json.loads(str(z["meta"])).get("trees_sha256")
        out[f"model{k}"] = (base / f"fold{k}.model.json").read_bytes()
    for drop in ("versions", "time", "folds"):
        out["stats"].pop(drop, None)
    return out


def test_zero_trade_configuration_is_well_formed(small_root):
    """C = 0.01 shrinks every coefficient to 0 on the small table: p = class priors, both EVs are the
    (negative) cost-laden mean nets, so no trade. The series is all zeros, not a failure."""
    stats = run_config(small_root, "E33-S1F15L001E")
    daily = pd.read_parquet(s.config_dir(small_root, "E33-S1F15L001E") / "daily.parquet")
    assert stats["trade_count"] == 0 and (daily["X_D"] == 0).all() and not stats["failed"]
    assert stats["mean_net_per_trade"] is None and stats["hit_rate"] is None and stats["t_stat"] is None
    assert stats["moments"]["sd"] == 0.0 and stats["share_dates_with_trade"] == 0.0


@pytest.mark.parametrize("cid", ["E33-S5F15L100E", "E33-S5T30G3050"])
def test_end_to_end_determinism_and_series(tmp_path, cid):
    roots = []
    for name in ("a", "b"):
        root = tmp_path / name
        g.write_tables(root, g.synth_dates(N_SMALL), ("F15", "T30"), seed=3, beta=2.0, excluded_every=13)
        run_config(root, cid, threads=2 if name == "a" else 3)
        roots.append(root)
    a, b = _outputs(roots[0], cid), _outputs(roots[1], cid)
    for k in range(1, 7):
        assert np.array_equal(a[f"p{k}"], b[f"p{k}"])
        assert np.array_equal(a[f"mu{k}"][0], b[f"mu{k}"][0]) and np.array_equal(a[f"mu{k}"][1], b[f"mu{k}"][1])
        if s.parse_config_id(cid).family == "LOGIT":
            assert a[f"model{k}"] == b[f"model{k}"]
        else:  # the model string's parameter block records num_threads (2 vs 3); the trees do not
            assert a[f"trees{k}"] == b[f"trees{k}"] is not None
    pd.testing.assert_frame_equal(a["daily"], b["daily"])
    pd.testing.assert_frame_equal(a["trades"], b["trades"])
    assert a["stats"] == b["stats"]
    daily, trades, stats = a["daily"], a["trades"], a["stats"]
    assert len(daily) == N_SMALL and list(daily["date"]) == g.synth_dates(N_SMALL)
    assert len(trades) > 50  # the planted signal (beta 2) gives trades
    sums = trades.groupby("date")["net"].sum().astype(float)  # pandas 3: object dtype on string keys
    assert np.allclose(daily.set_index("date")["X_D"].reindex(sums.index).to_numpy(dtype=float),
                       sums.to_numpy(dtype=float))
    assert (daily.set_index("date")["X_D"].drop(sums.index) == 0).all()  # no trade -> X_D = 0
    excl = [d for j, d in enumerate(g.synth_dates(N_SMALL)) if j % 13 == 12]
    assert (daily.set_index("date").loc[excl, "X_D"] == 0).all()  # excluded dates: X_D = 0
    assert trades.groupby("date").size().max() <= 20
    assert stats["moments"] == moments(daily["X_D"].tolist())
    assert stats["trade_count"] == len(trades)
    assert np.isclose(stats["mean_net_per_trade"], trades["net"].mean())
    assert np.isclose(stats["hit_rate"], (trades["net"] > 0).mean())
    assert np.isclose(stats["share_dates_with_trade"], (daily["n_trades"] > 0).mean())
    assert np.isclose(sum(v["sum"] for v in stats["per_month"].values()), daily["X_D"].sum())
    assert sum(v["n_dates"] for v in stats["vol_terciles"].values()) == N_SMALL
    assert stats["reported_only"]["mid_sign_hit_rate"] == "not available"  # no mid_move column


def test_mid_sign_hit_rule_excludes_nan_and_zero_moves():
    mv = [2.0, -1.0, 0.0, float("nan"), -3.0, 0.5]
    side = [1, 1, -1, 1, -1, -1]
    out = s.mid_sign_hit(mv, side)
    assert (out["hit_rate"], out["n_used"], out["n_nan"], out["n_zero"]) == (0.5, 4, 1, 1)
    assert s.mid_sign_hit([0.0, float("nan")], [1, -1])["hit_rate"] is None
    assert s.mid_sign_hit([], [])["n_used"] == 0


def test_mid_sign_hit_rate_end_to_end(tmp_path):
    dates = g.synth_dates(N_SMALL)
    g.write_tables(tmp_path, dates, ("F15",), seed=31, beta=2.0, with_mid_move=True)
    cid = "E33-S5F15L100E"
    stats = run_config(tmp_path, cid)
    trades = pd.read_parquet(s.config_dir(tmp_path, cid) / "trades.parquet")
    ldir = tmp_path / "labels" / g.LABEL_SHA / "F15"
    lab = {d: pd.read_parquet(ldir / f"{d}.parquet").set_index("i")["mid_move"] for d in set(trades["date"])}
    mv = np.array([lab[d].loc[i] for d, i in zip(trades["date"], trades["i"], strict=True)], dtype=float)
    side = trades["side"].to_numpy()
    used = np.isfinite(mv) & (mv != 0)
    got = stats["reported_only"]["mid_sign"]
    assert len(trades) > 50 and (got["n_nan"], got["n_zero"]) == (int(np.isnan(mv).sum()), int((mv == 0).sum()))
    assert got["n_nan"] + got["n_zero"] > 0 and got["n_used"] + got["n_nan"] + got["n_zero"] == len(trades)
    assert got["hit_rate"] == stats["reported_only"]["mid_sign_hit_rate"] == float(
        np.mean(np.sign(mv[used]) == side[used]))
    # a column present on some dates only stops the load
    frame = pd.read_parquet(ldir / f"{dates[7]}.parquet").drop(columns="mid_move")
    frame.to_parquet(ldir / f"{dates[7]}.parquet", index=False)
    s._TABLE_CACHE.clear()
    with pytest.raises(ValueError, match="some dates only"):
        s.load_tables(tmp_path, "F15", expected_n=None)


def test_vol_terciles_ties_by_date_and_quarters():
    dates = [f"2021-01-{d:02d}" for d in range(1, 10)]
    sigma = [3.0, 1.0, 2.0, 2.0, 1.0, 5.0, 2.0, 4.0, 1.0]
    x = list(range(9))
    t = s.vol_terciles(dates, sigma, x)
    # ascending sigma, ties by date: 2,5,9 | 3,4,7 | 1,8,6 (1-based day numbers)
    assert t["1"]["mean"] == np.mean([1, 4, 8]) and t["2"]["mean"] == np.mean([2, 3, 6])
    assert t["3"]["mean"] == np.mean([0, 7, 5])
    keys = [s._quarter_key(d) for d in ("2020-12-30", "2021-01-04", "2021-02-26", "2021-03-01",
                                        "2021-05-31", "2021-06-01", "2021-11-30", "2023-12-01", "2024-02-29")]
    assert keys == ["2020-12", "2020-12", "2020-12", "2021-03", "2021-03", "2021-06", "2021-09", "2023-12",
                    "2023-12"]


def test_failed_fit_fails_the_configuration(tmp_path):
    g.write_tables(tmp_path, g.synth_dates(N_SMALL), ("F15",), seed=8, no_class=1)
    cid = "E33-S1F15L010A"
    res = s.run_fold(tmp_path, cid, 2, expected_n=None)
    assert res["status"] == "failed" and "class 1" in res["error"]
    for k in (1, 3, 4, 5, 6):
        s.run_fold(tmp_path, cid, k, expected_n=None)
    stats = s.finalize_config(tmp_path, cid, expected_n=None)
    base = s.config_dir(tmp_path, cid)
    assert stats["failed"] and json.loads((base / "DONE").read_text())["status"] == "failed"
    assert not (base / "daily.parquet").exists()


# ---------------------------------------------------------------- runner: resume, kill, interruptions
def _runner(root, ids, *extra, popen=False):
    cmd = [sys.executable, str(RUNNER), "--root", str(root), "--ids", *ids, "--expected-n", "0",
           "--no-window-pause", *extra]
    if popen:
        return subprocess.Popen(cmd, cwd=s.REPO, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                start_new_session=True)
    return subprocess.run(cmd, cwd=s.REPO, capture_output=True, text=True)


def test_runner_resume_after_killed_run_matches_uninterrupted(tmp_path):
    cid = "E33-S5F15G3200"
    ref, cut = tmp_path / "ref", tmp_path / "cut"
    for root in (ref, cut):
        g.write_tables(root, g.synth_dates(N_SMALL), ("F15",), seed=11, beta=2.0)
    assert _runner(ref, [cid], "--max-procs", "1").returncode == 0
    proc = _runner(cut, [cid], "--max-procs", "1", popen=True)
    att = s.fold_paths(cut, cid, 1)["attempts"]
    t0 = time.time()
    while not att.exists() and time.time() - t0 < 60:
        time.sleep(0.005)
    os.killpg(proc.pid, signal.SIGKILL)  # the runner and its pool, mid-run
    proc.wait()
    assert not (s.config_dir(cut, cid) / "DONE").exists()
    r = _runner(cut, [cid], "--max-procs", "1")
    assert r.returncode == 0, r.stderr[-2000:]
    a, b = _outputs(ref, cid), _outputs(cut, cid)
    for k in range(1, 7):
        assert np.array_equal(a[f"p{k}"], b[f"p{k}"]) and a[f"model{k}"] == b[f"model{k}"]
    pd.testing.assert_frame_equal(a["trades"], b["trades"])
    assert a["stats"] == b["stats"]
    assert s.read_attempts(cut, cid, 1) in (1, 2)


def test_runner_skips_done_folds_and_fails_twice_interrupted_fold(tmp_path):
    g.write_tables(tmp_path, g.synth_dates(N_SMALL), ("F15",), seed=12, beta=2.0)
    cid, cid2 = "E33-S1F15L001A", "E33-S1F15L100A"
    s.run_fold(tmp_path, cid, 1, expected_n=None)
    before = s.fold_paths(tmp_path, cid, 1)["npz"].stat().st_mtime_ns
    s.fold_paths(tmp_path, cid2, 3)["npz"].parent.mkdir(parents=True)
    rec = json.dumps({"start": "x", "pipeline_sha": s.PIPELINE_SHA})
    s.fold_paths(tmp_path, cid2, 3)["attempts"].write_text(rec + "\n" + rec + "\n")
    r = _runner(tmp_path, [cid, cid2], "--max-procs", "2")
    assert r.returncode == 0, r.stderr[-2000:]
    assert s.fold_paths(tmp_path, cid, 1)["npz"].stat().st_mtime_ns == before  # not refitted
    assert s.read_attempts(tmp_path, cid, 1) == 1
    assert json.loads((s.config_dir(tmp_path, cid) / "DONE").read_text())["status"] == "ok"
    done2 = json.loads((s.config_dir(tmp_path, cid2) / "DONE").read_text())
    assert done2["status"] == "failed"
    assert "interrupted twice" in json.loads(s.fold_paths(tmp_path, cid2, 3)["failed"].read_text())["error"]
    r = _runner(tmp_path, [cid, cid2])  # a rerun of finished configurations does nothing
    assert r.returncode == 0 and "0 fold tasks" in r.stderr


def test_guard_consulted_for_derived_roots(tmp_path, monkeypatch):
    assert s.guard_for(tmp_path) is None
    assert s.guard_for(s.DERIVED_E33 / "proofs" / "seed1").__name__ == "guard33"
    dates = g.synth_dates(N_SMALL)
    g.write_tables(tmp_path, dates, ("F15",), seed=21)
    link = tmp_path / "labels" / g.LABEL_SHA / "F15" / f"{dates[5]}.parquet"
    real = link.with_name("real.bin")
    link.rename(real)
    link.symlink_to(real)

    class FakeGuard:
        paths, dates_seen = [], []

        @classmethod
        def check_path(cls, p):
            cls.paths.append(Path(p))

        @classmethod
        def check_date(cls, d, where=""):
            cls.dates_seen.append(d)

    monkeypatch.setattr(s, "guard_for", lambda root: FakeGuard)
    s.load_tables(tmp_path, "F15", expected_n=None)
    assert FakeGuard.dates_seen == dates
    assert {p.name for p in FakeGuard.paths} == {g.FEAT_SHA, "F15", "_day", link.name}
    FakeGuard.check_path = classmethod(lambda cls, p: (_ for _ in ()).throw(RuntimeError("refused")))
    s._TABLE_CACHE.clear()
    with pytest.raises(RuntimeError, match="refused"):
        s.load_tables(tmp_path, "F15", expected_n=None)


def test_runner_refuses_real_root_without_registration():
    if not s.REPO.exists():
        pytest.skip("no repo")
    import run_search33 as rs
    real = rs.REAL_ROOT
    if not real.exists():
        pytest.skip("real DERIVED root not created yet")
    r = subprocess.run([sys.executable, str(RUNNER), "--root", str(real), "--ids", "E33-S5F15L001A"],
                       cwd=s.REPO, capture_output=True, text=True)
    assert r.returncode != 0 and "refused" in (r.stderr + r.stdout)


# ---------------------------------------------------------------- review fixes SF1-SF4
SF3_CID = "E33-S1F15L010A"


def _wait_for(path, timeout=60.0):
    t0 = time.time()
    while not Path(path).exists() and time.time() - t0 < timeout:
        time.sleep(0.005)
    return Path(path).exists()


def sf3_fold_fn(root, cid, k, **kw):
    """SF3 test task: fold 2 kills its own worker right after fold 1 (beside it) has started."""
    if (cid, k) == (SF3_CID, 2):
        s.record_attempt(root, cid, k)
        _wait_for(s.fold_paths(root, cid, 1)["attempts"])
        os.kill(os.getpid(), signal.SIGKILL)
    if (cid, k) == (SF3_CID, 1):
        _wait_for(s.fold_paths(root, cid, 2)["attempts"])
    return s.run_fold(root, cid, k, **kw)


def typeerror_fold_fn(root, cid, k, **kw):
    s.record_attempt(root, cid, k)
    raise TypeError("injected code bug")


def _args(root, cid, procs=2):
    import run_search33 as rs
    return rs, rs.parse_args(["--root", str(root), "--ids", cid, "--max-procs", str(procs), "--expected-n", "0",
                              "--no-window-pause"])


def test_sf1_markers_carry_pipeline_sha_and_stale_ones_are_refused(tmp_path, monkeypatch):
    names = {p.name for p in s.pipeline_files()}
    assert {"search33.py", "run_search33.py", "guard33.py"} <= names and "synth_search33.py" not in names
    g.write_tables(tmp_path, g.synth_dates(N_SMALL), ("F15",), seed=41, beta=2.0)
    cid = "E33-S1F15L100A"
    stats = run_config(tmp_path, cid)
    base = s.config_dir(tmp_path, cid)
    for marker in [base / "DONE"] + [s.fold_paths(tmp_path, cid, k)["done"] for k in range(1, 7)]:
        assert json.loads(marker.read_text())["pipeline_sha"] == s.PIPELINE_SHA
    assert stats["pipeline_sha"] == s.PIPELINE_SHA and len(stats["tables_fingerprint"]) == 64
    s.check_markers(tmp_path, cid)  # current code: accepted
    rs, args = _args(tmp_path, cid)
    assert len(rs.plan(tmp_path, [cid], 4)) == 0
    monkeypatch.setattr(s, "PIPELINE_SHA", "0" * 64)  # the code changed
    with pytest.raises(s.StaleMarkerError, match="another pipeline version"):
        rs.plan(tmp_path, [cid], 4)
    with pytest.raises(s.StaleMarkerError):
        s.finalize_config(tmp_path, cid, expected_n=None)
    with pytest.raises(s.StaleMarkerError):
        s.load_fold_payload(tmp_path, cid, 1)


def test_sf1_runner_refuses_stale_markers_with_rc6(tmp_path):
    g.write_tables(tmp_path, g.synth_dates(N_SMALL), ("F15",), seed=42)
    cid = "E33-S1F15L001A"
    s.config_dir(tmp_path, cid).mkdir(parents=True)
    s.atomic_write_json(s.fold_paths(tmp_path, cid, 1)["done"], {"pipeline_sha": "f" * 64})
    r = _runner(tmp_path, [cid])
    assert r.returncode == 6 and "REFUSED" in r.stderr and "another pipeline version" in r.stderr
    assert s.read_attempts(tmp_path, cid, 2) == 0  # nothing ran


def test_sf1_changed_tables_are_refused_at_finalize(tmp_path):
    dates = g.synth_dates(N_SMALL)
    g.write_tables(tmp_path, dates, ("F15",), seed=43, beta=2.0)
    cid = "E33-S1F15L010E"
    for k in range(1, 7):
        assert s.run_fold(tmp_path, cid, k, expected_n=None)["status"] == "done"
    path = tmp_path / "labels" / g.LABEL_SHA / "F15" / f"{dates[3]}.parquet"
    frame = pd.read_parquet(path)
    frame.loc[frame["row_ok"], "w"] = frame.loc[frame["row_ok"], "w"] * 0.5  # a rebuilt store, same name
    frame.to_parquet(path, index=False)
    s._TABLE_CACHE.clear()
    with pytest.raises(s.StaleMarkerError, match="other tables"):
        s.finalize_config(tmp_path, cid, expected_n=None)


@pytest.fixture()
def sf2_root(tmp_path):
    g.write_tables(tmp_path, g.synth_dates(N_SMALL), ("F15",), seed=44, beta=2.0)
    s._TABLE_CACHE.clear()
    return tmp_path


def _no_failed_marker(root, cid, k):
    return s.fold_state(root, cid, k) == "pending" and s.read_attempts(root, cid, k) == 1


def test_sf2_write_error_is_an_interruption(sf2_root, monkeypatch):
    real = s.atomic_write_bytes

    def eio(path, data):
        if path.name.endswith("model.json"):
            raise OSError(5, "Input/output error (injected)")
        return real(path, data)

    monkeypatch.setattr(s, "atomic_write_bytes", eio)
    with pytest.raises(OSError):
        s.run_fold(sf2_root, "E33-S1F15L001A", 1, expected_n=None)
    assert _no_failed_marker(sf2_root, "E33-S1F15L001A", 1)


def test_sf2_code_bug_and_load_error_propagate(sf2_root, monkeypatch):
    with pytest.raises(ValueError, match="OOF dates"):  # load/validation error: not a failed fit
        s.run_fold(sf2_root, "E33-S1F15L001A", 1, expected_n=796)
    assert _no_failed_marker(sf2_root, "E33-S1F15L001A", 1)
    monkeypatch.setattr(s, "fit_lgbm", lambda *a, **k: (_ for _ in ()).throw(TypeError("injected bug")))
    with pytest.raises(TypeError):
        s.run_fold(sf2_root, "E33-S1F15G2050", 1, expected_n=None)
    assert _no_failed_marker(sf2_root, "E33-S1F15G2050", 1)


def test_sf2_lightgbm_errors_classified(sf2_root, monkeypatch):
    import lightgbm
    monkeypatch.setattr(lightgbm, "train", lambda *a, **k: (_ for _ in ()).throw(
        lightgbm.basic.LightGBMError("std::bad_alloc")))
    with pytest.raises(MemoryError):  # out of memory inside LightGBM: an interruption
        s.run_fold(sf2_root, "E33-S1F15G2050", 2, expected_n=None)
    assert _no_failed_marker(sf2_root, "E33-S1F15G2050", 2)
    monkeypatch.setattr(lightgbm, "train", lambda *a, **k: (_ for _ in ()).throw(
        lightgbm.basic.LightGBMError("Check failed: numerical")))
    res = s.run_fold(sf2_root, "E33-S1F15G2050", 3, expected_n=None)
    assert res["status"] == "failed" and s.fold_state(sf2_root, "E33-S1F15G2050", 3) == "failed"


def test_sf2_fit_errors_and_nonfinite_probabilities_fail(sf2_root, monkeypatch):
    import sklearn.linear_model
    monkeypatch.setattr(sklearn.linear_model.LogisticRegression, "fit",
                        lambda *a, **k: (_ for _ in ()).throw(ValueError("solver failed (injected)")))
    res = s.run_fold(sf2_root, "E33-S1F15L001A", 4, expected_n=None)
    assert res["status"] == "failed" and "LogisticRegression.fit" in res["error"]
    monkeypatch.undo()
    monkeypatch.setattr(s, "predict_proba", lambda model, X, threads=1: np.full((len(X), 3), np.nan))
    res = s.run_fold(sf2_root, "E33-S1F15L001A", 5, expected_n=None)
    assert res["status"] == "failed" and "non-finite" in res["error"]
    failed = json.loads(s.fold_paths(sf2_root, "E33-S1F15L001A", 5)["failed"].read_text())
    assert failed["pipeline_sha"] == s.PIPELINE_SHA


def test_sf2_runner_stops_on_code_bug_without_failing(sf2_root):
    rs, args = _args(sf2_root, "E33-S1F15L001E", procs=1)
    rc = rs.run_search(sf2_root, ["E33-S1F15L001E"], args, fold_fn=typeerror_fold_fn)
    assert rc == 5 and s.fold_state(sf2_root, "E33-S1F15L001E", 1) == "pending"
    assert not (s.config_dir(sf2_root, "E33-S1F15L001E") / "DONE").exists()


def test_sf3_dead_worker_charges_only_its_own_fold(tmp_path):
    g.write_tables(tmp_path, g.synth_dates(N_SMALL), ("F15",), seed=45, beta=2.0)
    rs, args = _args(tmp_path, SF3_CID, procs=2)
    rc = rs.run_search(tmp_path, [SF3_CID], args, fold_fn=sf3_fold_fn)
    assert rc == 4
    assert s.fold_state(tmp_path, SF3_CID, 2) == "pending" and s.read_attempts(tmp_path, SF3_CID, 2) == 1
    assert s.fold_state(tmp_path, SF3_CID, 1) == "done" and s.read_attempts(tmp_path, SF3_CID, 1) == 1
    assert all(s.read_attempts(tmp_path, SF3_CID, k) == 0 for k in range(3, 7))  # stopped after the death
    rc = rs.run_search(tmp_path, [SF3_CID], args)  # the relaunch: the one rerun of fold 2
    assert rc == 0 and json.loads((s.config_dir(tmp_path, SF3_CID) / "DONE").read_text())["status"] == "ok"
    assert s.read_attempts(tmp_path, SF3_CID, 1) == 1 and s.read_attempts(tmp_path, SF3_CID, 2) == 2


def test_sf4_fold_killed_while_loading_is_charged(tmp_path):
    dates = g.synth_dates(N_SMALL)
    g.write_tables(tmp_path, dates, ("F15",), seed=46)
    cid = "E33-S1F15L001A"
    feat = tmp_path / "features" / g.FEAT_SHA / f"{dates[30]}.parquet"
    keep = feat.with_name("keep.bin")
    feat.rename(keep)
    os.mkfifo(feat)  # reading it blocks: the worker is stuck inside load_tables
    code = (f"import sys; sys.path[:0] = [{str(PIPE)!r}]; import search33 as s; "
            f"s.run_fold({str(tmp_path)!r}, {cid!r}, 1, expected_n=None)")
    proc = subprocess.Popen([sys.executable, "-c", code], cwd=s.REPO, start_new_session=True,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        assert _wait_for(s.fold_paths(tmp_path, cid, 1)["attempts"])
        time.sleep(0.5)
        assert proc.poll() is None  # still loading
    finally:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait()
    assert s.read_attempts(tmp_path, cid, 1) == 1 and s.fold_state(tmp_path, cid, 1) == "pending"
    feat.unlink()
    keep.rename(feat)
    s._TABLE_CACHE.clear()
    assert s.run_fold(tmp_path, cid, 1, expected_n=None)["status"] == "done"
    assert s.read_attempts(tmp_path, cid, 1) == 2
