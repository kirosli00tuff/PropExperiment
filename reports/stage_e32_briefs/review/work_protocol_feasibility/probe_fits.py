"""Timing probe for P5's fit-count arithmetic (synthetic data only; no market data).

Rows ~170,000 x 59 features, 3 classes with P3-like imbalance (most rows 0), sample weights in
(0, 1]. Measures wall seconds per fit for the LOGIT grid (saga, l1_ratio in {0, 0.5},
C in {0.01, 0.1, 1}) and the LGBM grid (depth 2/3, min_data_in_leaf 750/3000) with early
stopping on a weighted validation block, deterministic + force_row_wise, num_threads 8.
Prints only results. Runs at nice 10.
"""
from __future__ import annotations

import os
import time
import warnings

os.nice(10)
warnings.filterwarnings("ignore")

import numpy as np  # noqa: E402

N_ROWS = int(os.environ.get("PROBE_ROWS", "170000"))
N_FEAT = 59
SEED = 20261027
rng = np.random.default_rng(SEED)
X = rng.standard_normal((N_ROWS, N_FEAT)).astype(np.float64)
# weak signal so the fit is not degenerate; class imbalance like a cost-aware label
beta = rng.standard_normal(N_FEAT) * 0.05
score = X @ beta
y = np.where(score > 1.0, 1, np.where(score < -1.0, -1, 0))
w = rng.uniform(0.05, 1.0, N_ROWS)
print(f"rows={N_ROWS} feats={N_FEAT} class_counts={dict(zip(*np.unique(y, return_counts=True)))}")

from sklearn.linear_model import LogisticRegression  # noqa: E402

for C in (0.01, 0.1, 1.0):
    for rho in (0.0, 0.5):
        t0 = time.perf_counter()
        m = LogisticRegression(C=C, l1_ratio=rho, solver="saga", max_iter=2000, tol=1e-4,
                               random_state=SEED)
        with warnings.catch_warnings(record=True) as wl:
            warnings.simplefilter("always")
            m.fit(X, y, sample_weight=w)
            conv = not any("ConvergenceWarning" in str(x.category) for x in wl)
        dt = time.perf_counter() - t0
        print(f"LOGIT C={C} l1_ratio={rho} n_iter={int(np.max(m.n_iter_))} converged={conv} "
              f"wall_s={dt:.1f}")

import lightgbm as lgb  # noqa: E402

# inner validation: latest 15% of rows (stand-in for dates)
cut = int(N_ROWS * 0.85)
Xtr, ytr, wtr = X[:cut], y[:cut], w[:cut]
Xva, yva, wva = X[cut:], y[cut:], w[cut:]
ymap = {-1: 0, 0: 1, 1: 2}
ytr_c = np.vectorize(ymap.get)(ytr)
yva_c = np.vectorize(ymap.get)(yva)
h = 15
for d in (2, 3):
    for mdl in (50 * h, 200 * h):
        params = dict(objective="multiclass", num_class=3, boosting="gbdt", learning_rate=0.05,
                      max_depth=d, num_leaves=2 ** d, min_data_in_leaf=mdl, feature_fraction=0.8,
                      bagging_fraction=0.8, bagging_freq=1, lambda_l2=1.0, min_gain_to_split=0.0,
                      max_bin=255, seed=SEED, deterministic=True, force_row_wise=True,
                      num_threads=8, verbose=-1, metric="multi_logloss")
        t0 = time.perf_counter()
        dtr = lgb.Dataset(Xtr, label=ytr_c, weight=wtr, params={"max_bin": 255})
        dva = lgb.Dataset(Xva, label=yva_c, weight=wva, reference=dtr)
        bst = lgb.train(params, dtr, num_boost_round=500, valid_sets=[dva],
                        valid_names=["inner"],
                        callbacks=[lgb.early_stopping(50, first_metric_only=True, verbose=False)])
        dt = time.perf_counter() - t0
        print(f"LGBM depth={d} min_data_in_leaf={mdl} best_iter={bst.best_iteration} "
              f"wall_s={dt:.1f}")
print("done")
