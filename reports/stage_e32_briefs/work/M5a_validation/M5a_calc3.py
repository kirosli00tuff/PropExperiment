"""M5a_validation add-on: which effective N goes with which V in the DSR benchmark (synthetic only)."""
from __future__ import annotations

import math
from statistics import NormalDist

import numpy as np

ND = NormalDist()
G = 0.5772156649015329


def e_n(n: float) -> float:
    return (1 - G) * ND.inv_cdf(1 - 1 / n) + G * ND.inv_cdf(1 - 1 / (n * math.e))


rng = np.random.default_rng(2032)
T, M, REPS = 816, 1000, 400
print("model | mean max SR | sqrt(Vemp)*e(M) | sqrt(Vemp)*e(Khat) | sqrt(1/T)*e(M) | K_eff participation")
# one-factor equicorrelation
for rho in (0.5, 0.8):
    mx, vv = [], []
    for _ in range(REPS):
        z = math.sqrt(rho) * rng.standard_normal() + math.sqrt(1 - rho) * rng.standard_normal(M)
        sr = z / math.sqrt(T)  # SR estimates ~ N(0, 1/T) marginally, equicorrelated
        mx.append(sr.max())
        vv.append(sr.var())
    keff = M / (1 + (M - 1) * rho * rho)
    print(f"one-factor rho={rho} | {np.mean(mx):.4f} | {math.sqrt(np.mean(vv)) * e_n(M):.4f} | "
          f"n/a | {math.sqrt(1 / T) * e_n(M):.4f} | {keff:.1f}")
# clusters of near-duplicates: K clusters, within-cluster corr r_in, between 0
for k, r_in in ((50, 0.95), (200, 0.9)):
    size = M // k
    mx, vv = [], []
    for _ in range(REPS):
        c = rng.standard_normal(k).repeat(size)
        z = math.sqrt(r_in) * c + math.sqrt(1 - r_in) * rng.standard_normal(M)
        sr = z / math.sqrt(T)
        mx.append(sr.max())
        vv.append(sr.var())
    fro2 = k * (size * size * r_in * r_in + size * (1 - r_in * r_in))  # sum of squared correlations
    keff = M * M / fro2
    print(f"clusters K={k} r_in={r_in} | {np.mean(mx):.4f} | {math.sqrt(np.mean(vv)) * e_n(M):.4f} | "
          f"{math.sqrt(np.mean(vv)) * e_n(k):.4f} | {math.sqrt(1 / T) * e_n(M):.4f} | {keff:.1f}")
