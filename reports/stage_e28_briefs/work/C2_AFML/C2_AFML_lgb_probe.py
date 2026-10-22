"""Timing probe: one LightGBM fit on synthetic data, to size a CPCV run (synthetic only)."""
import time, json, os
import numpy as np, lightgbm as lgb
rng = np.random.default_rng(1)
out = {}
for n in (200_000, 1_000_000):
    X = rng.normal(size=(n, 30)).astype(np.float32)
    y = (X[:, 0] * 0.05 + rng.normal(size=n) > 0).astype(int)
    m = lgb.LGBMClassifier(n_estimators=200, num_leaves=31, learning_rate=0.05, n_jobs=8, verbose=-1)
    t0 = time.perf_counter(); m.fit(X, y); out[f"fit_{n}x30_200trees_8thr_s"] = round(time.perf_counter() - t0, 2)
p = os.path.join(os.path.dirname(__file__), "C2_AFML_lgb_probe.json")
json.dump(out, open(p, "w"), indent=1); print(out)
