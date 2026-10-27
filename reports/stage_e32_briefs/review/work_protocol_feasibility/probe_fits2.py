"""Second timing probe (synthetic data only; no market data).

Differences from probe_fits.py: correlated features (block AR structure, like z-scores at nested
look-backs), classes about 45/10/45 (the P3.3 dead zone at h = 15 under sigma_h = 12.2 ticks),
and only the worst-case grid points: LOGIT C = 1.0 x rho in {0, 0.5} (plus C = 0.1 rho 0.5 for
scale) and LGBM depth 3 with min_data_in_leaf 750 (h = 15, 50h) and 12,000 (h = 60, 200h) at
num_threads 5. Prints results only. Runs at nice 10. Rows default 170,000 x 59.
"""
from __future__ import annotations

import os
import time
import warnings

os.nice(10)
os.environ.setdefault("OMP_NUM_THREADS", "1")
warnings.filterwarnings("ignore")

import numpy as np  # noqa: E402

N_ROWS = int(os.environ.get("PROBE_ROWS", "170000"))
N_FEAT = 59
SEED = 20261027
rng = np.random.default_rng(SEED)
# 6 latent factors, each feature a noisy copy of one factor -> correlations 0.6-0.9 inside blocks
latent = rng.standard_normal((N_ROWS, 6))
X = np.empty((N_ROWS, N_FEAT))
for j in range(N_FEAT):
    k = j % 6
    rho = 0.6 + 0.3 * rng.random()
    X[:, j] = rho * latent[:, k] + np.sqrt(1 - rho * rho) * rng.standard_normal(N_ROWS)
X = np.clip(X, -5, 5)
beta = rng.standard_normal(N_FEAT) * 0.03
move = X @ beta + rng.standard_normal(N_ROWS) * 1.0  # standardised move
cut = 0.125  # ~ 1.5 ticks / 12.2 ticks
y = np.where(move > cut, 1, np.where(move < -cut, -1, 0))
w = rng.uniform(0.05, 1.0, N_ROWS)
counts = dict(zip(*np.unique(y, return_counts=True)))
print(f"rows={N_ROWS} feats={N_FEAT} class_counts={ {int(k): int(v) for k, v in counts.items()} }")
Xs = (X - np.average(X, axis=0, weights=w)) / X.std(axis=0)

from sklearn.linear_model import LogisticRegression  # noqa: E402

for C, rho in ((0.1, 0.5), (1.0, 0.0), (1.0, 0.5)):
    t0 = time.perf_counter()
    m = LogisticRegression(C=C, l1_ratio=rho, solver="saga", max_iter=2000, tol=1e-4,
                           random_state=SEED)
    with warnings.catch_warnings(record=True) as wl:
        warnings.simplefilter("always")
        m.fit(Xs, y, sample_weight=w)
        conv = not any("ConvergenceWarning" in str(x.category) for x in wl)
    dt = time.perf_counter() - t0
    print(f"LOGIT C={C} l1_ratio={rho} n_iter={int(np.max(m.n_iter_))} converged={conv} "
          f"coef_shape={m.coef_.shape} wall_s={dt:.1f} s_per_epoch={dt / max(1, int(np.max(m.n_iter_))):.3f}")

import lightgbm as lgb  # noqa: E402

split = int(N_ROWS * 0.85)
Xtr, ytr, wtr = X[:split], y[:split], w[:split]
Xva, yva, wva = X[split:], y[split:], w[split:]
ymap = {-1: 0, 0: 1, 1: 2}
ytr_c = np.vectorize(ymap.get)(ytr)
yva_c = np.vectorize(ymap.get)(yva)
for d, mdl in ((3, 750), (3, 12000), (2, 12000)):
    params = dict(objective="multiclass", num_class=3, boosting="gbdt", learning_rate=0.05,
                  max_depth=d, num_leaves=2 ** d, min_data_in_leaf=mdl, feature_fraction=0.8,
                  bagging_fraction=0.8, bagging_freq=1, lambda_l2=1.0, min_gain_to_split=0.0,
                  max_bin=255, seed=SEED, deterministic=True, force_row_wise=True,
                  num_threads=5, verbose=-1, metric="multi_logloss")
    t0 = time.perf_counter()
    dtr = lgb.Dataset(Xtr, label=ytr_c, weight=wtr, params={"max_bin": 255})
    dva = lgb.Dataset(Xva, label=yva_c, weight=wva, reference=dtr)
    bst = lgb.train(params, dtr, num_boost_round=500, valid_sets=[dva], valid_names=["inner"],
                    callbacks=[lgb.early_stopping(50, first_metric_only=True, verbose=False)])
    dt = time.perf_counter() - t0
    leaves = [t["num_leaves"] for t in bst.dump_model()["tree_info"][:3]]
    print(f"LGBM depth={d} min_data_in_leaf={mdl} best_iter={bst.best_iteration} "
          f"first3_tree_leaves={leaves} wall_s={dt:.1f}")
    # calibrator as P5 writes it (C = 1e4, lbfgs) on raw scores of the inner block
    raw = bst.predict(Xva, raw_score=True)
    t0 = time.perf_counter()
    cal = LogisticRegression(C=1e4, solver="lbfgs")
    with warnings.catch_warnings(record=True) as wl:
        warnings.simplefilter("always")
        cal.fit(raw, yva_c, sample_weight=wva)
        conv = not any("ConvergenceWarning" in str(x.category) for x in wl)
    print(f"  calibrator max_iter=default n_iter={int(np.max(cal.n_iter_))} converged={conv} "
          f"wall_s={time.perf_counter() - t0:.2f}")
print("done")
