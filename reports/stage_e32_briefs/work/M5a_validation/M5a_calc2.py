"""M5a_validation add-on: PBO null distribution, DSR family-wise size, correlated-trial V (synthetic only)."""
from __future__ import annotations

import math
from itertools import combinations
from statistics import NormalDist

import numpy as np

ND = NormalDist()
GAMMA = 0.5772156649015329
T_DAYS = 816


def e_n(n: float) -> float:
    return (1 - GAMMA) * ND.inv_cdf(1 - 1 / n) + GAMMA * ND.inv_cdf(1 - 1 / (n * math.e))


def pbo_once(perf: np.ndarray, s: int, splits: list[tuple[int, ...]]) -> float:
    n = perf.shape[0]
    w = perf.shape[1] // s
    blk = np.stack([perf[:, i * w:(i + 1) * w].sum(1) for i in range(s)], 1)
    hits = 0
    for tr in splits:
        mask = np.zeros(s, bool)
        mask[list(tr)] = True
        ins, oos = blk[:, mask].sum(1), blk[:, ~mask].sum(1)
        b = int(np.argmax(ins))
        r = 1 + int(np.sum(oos < oos[b]))
        hits += (r / (n + 1)) <= 0.5
    return hits / len(splits)


print("=== PBO under the null (iid N(0,1) daily P&L, 816 days)")
rng = np.random.default_rng(101)
for ncfg, s, reps in ((10, 8, 200), (50, 8, 200), (200, 16, 12)):
    splits = list(combinations(range(s), s // 2))
    vals = np.array([pbo_once(rng.standard_normal((ncfg, T_DAYS)), s, splits) for _ in range(reps)])
    print(f"configs {ncfg} S={s} reps {reps}: mean PBO {vals.mean():.3f}, sd {vals.std():.3f}, "
          f"5-95% [{np.quantile(vals, .05):.3f}, {np.quantile(vals, .95):.3f}]")

print("=== PBO with one true edge among noise (daily mean 0.10 sd, i.e. annual SR ~1.6)")
for ncfg, s, reps in ((50, 8, 200),):
    splits = list(combinations(range(s), s // 2))
    vals = []
    for _ in range(reps):
        perf = rng.standard_normal((ncfg, T_DAYS))
        perf[0] += 0.10
        vals.append(pbo_once(perf, s, splits))
    vals = np.array(vals)
    print(f"configs {ncfg} S={s}: mean PBO {vals.mean():.3f}, 5-95% [{np.quantile(vals, .05):.3f}, "
          f"{np.quantile(vals, .95):.3f}]")

print("=== family-wise size of 'DSR >= 0.95' with V = 1/T, iid null trials, g3=0 g4=3")
for n in (738, 1538, 5538):
    tstar = e_n(n) + 1.6449
    fw = 1 - ND.cdf(tstar) ** n
    print(f"N={n}: t* ~ e(N)+1.645 = {tstar:.3f}; P(any null trial passes) = {fw:.2e}")

print("=== cross-sectional variance of SR estimates under a one-factor correlation (rho)")
rng = np.random.default_rng(9)
T = T_DAYS
for rho in (0.0, 0.5, 0.8):
    vs = []
    for _ in range(20):
        f = rng.standard_normal(T)
        x = math.sqrt(rho) * f[None, :] + math.sqrt(1 - rho) * rng.standard_normal((300, T))
        sr = x.mean(1) / x.std(1)
        vs.append(sr.var())
    print(f"rho={rho}: mean cross-trial V[SR] = {np.mean(vs):.6f}; (1-rho)/T = {(1 - rho) / T:.6f}; 1/T = {1 / T:.6f}")
