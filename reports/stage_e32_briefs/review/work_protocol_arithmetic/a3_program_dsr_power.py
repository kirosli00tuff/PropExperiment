"""ArithmeticReviewer: power of the one-shot test INCLUDING the program verdict's own DSR (V14 c: the
population variance of the tested Sharpes as the DSR's V), which P7.2's power table leaves out.
Monte Carlo on the sampling distribution of daily Sharpes (normal days, T_test 870, N 838): the observed
Sharpe vector of the tested list is N(mu, Sigma), Sigma_ij = rho_ij (1 + 0.5 mu_i mu_j) / (T - 1), with
rho the correlation of the daily series. No data is read.

    uv run python reports/stage_e32_briefs/review/work_protocol_arithmetic/a3_program_dsr_power.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path
from statistics import NormalDist

import numpy as np

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))
from funnel.multiple_comparisons import deflated_sharpe_ratio, expected_max_sharpe  # noqa: E402

Z = NormalDist()
N, T = 838, 870
B_TEST = 0.16488  # protocol-added DSR bar, V = 1/(T - 1)
T_BAR = 3.0 / math.sqrt(T)
RNG = np.random.default_rng(20261027)
DRAWS = 20_000


def passes_program_dsr(sr: np.ndarray, i: int) -> bool:
    var = float(np.var(sr))  # population variance over the tested list (V14 c; statistics.pvariance)
    d = deflated_sharpe_ratio(float(sr[i]), T, N, var)["deflated_sharpe_ratio"]
    return d > 0.95


def run(label: str, mu: list[float], rho: float) -> None:
    k = len(mu)
    mu_a = np.array(mu)
    corr = np.full((k, k), rho) + (1 - rho) * np.eye(k)
    sd = np.sqrt((1 + 0.5 * mu_a**2) / (T - 1))
    cov = corr * np.outer(sd, sd)
    draws = RNG.multivariate_normal(mu_a, cov, size=DRAWS)
    prog = prot = both = 0
    sr0 = []
    for sr in draws:
        p_prog = passes_program_dsr(sr, 0)
        p_prot = sr[0] >= B_TEST and sr[0] * math.sqrt(T) > 3.0
        prog += p_prog
        prot += p_prot
        both += p_prog and p_prot
        sr0.append(expected_max_sharpe(N, float(np.var(sr))))
    print(f"{label:48s} rho {rho:.2f}: P(program DSR) {prog / DRAWS:.3f}  P(t>3 & protocol DSR) {prot / DRAWS:.3f}  "
          f"P(both) {both / DRAWS:.3f}  median SR0_program {np.median(sr0):.3f} (SR0 at V=1/(T-1): "
          f"{expected_max_sharpe(N, 1 / (T - 1)):.3f})")


print("Candidate 0 is the member under test; the others are the rest of the tested list (Tier A, or Tier B when "
      "Tier A has one member). True daily Sharpes in the test window as listed.")
for rho in (0.0, 0.5):
    run("Tier A 3: [0.25, 0.25, 0.25] (all real)", [0.25, 0.25, 0.25], rho)
    run("Tier A 3: [0.25, 0.25, 0.00]", [0.25, 0.25, 0.0], rho)
    run("Tier A 3: [0.25, 0.00, 0.00] (two false positives)", [0.25, 0.0, 0.0], rho)
    run("Tier A 3: [0.20, 0.00, 0.00]", [0.20, 0.0, 0.0], rho)
    run("Tier A 2: [0.25, 0.00]", [0.25, 0.0], rho)
run("Tier A 1 + Tier B 2 near-duplicates: [0.25, 0.25, 0.25]", [0.25, 0.25, 0.25], 0.9)
run("Tier A 1 + Tier B 2 nulls: [0.25, 0.00, 0.00]", [0.25, 0.0, 0.0], 0.3)
run("Tier A 1 + Tier B 2 nulls: [0.30, 0.00, 0.00]", [0.30, 0.0, 0.0], 0.3)
print("\nClosed form: with k tested Sharpes whose true values are s and 0 (k-1 of them), the population variance "
      "is about s^2 (k-1)/k^2 + noise, so SR0_program ~ 3.205 x s x sqrt(k-1)/k:")
for k in (2, 3):
    for s in (0.20, 0.25, 0.30):
        sr0 = 3.205 * s * math.sqrt(k - 1) / k
        print(f"  k={k}, s={s:.2f}: SR0_program ~ {sr0:.3f}; the member needs SR >= {sr0 + 1.645 / math.sqrt(T - 1):.3f}")
