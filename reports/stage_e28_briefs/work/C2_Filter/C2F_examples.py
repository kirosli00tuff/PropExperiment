"""C2_Filter worked examples (hand-sized numbers; no market data). Writes C2F_examples.json.
Run: uv run python -I C2F_examples.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import norm

OUT = Path(__file__).with_name("C2F_examples.json")


def ex_local_level() -> dict:
    """MES mid-prices in index points; q, r in points^2 per 1-second step."""
    q, r = 0.01, 0.015625
    ppred_ss = (q + math.sqrt(q * q + 4 * q * r)) / 2
    k_ss = ppred_ss / (ppred_ss + r)
    obs = [5000.25, 5000.25, 5000.00, 5000.50]
    x, p = 5000.00, 0.02  # prior mean and variance
    steps = []
    for z in obs:
        pp = p + q
        k = pp / (pp + r)
        v = z - x
        x_new = x + k * v
        p_new = (1 - k) * pp
        steps.append({"z": z, "x_prior": round(x, 5), "P_prior": round(pp, 6), "K": round(k, 5),
                      "innovation": round(v, 5), "x_post": round(x_new, 5), "P_post": round(p_new, 6)})
        x, p = x_new, p_new
    rho1 = -r / (q + 2 * r)
    return {"q": q, "r": r, "Ppred_ss": round(ppred_ss, 6), "K_ss": round(k_ss, 5), "steps": steps,
            "rho1_theory": round(rho1, 4), "var_dy": q + 2 * r}


def ex_hedge() -> dict:
    """Time-varying hedge ratio y1 = gamma_t * y2 + eps (mu fixed at 0 for clarity); random-walk gamma."""
    g, P = 2.0, 0.01
    s_g2, s_e2 = 1e-4, 1.0
    data = [(10.0, 21.0), (10.5, 21.5), (9.8, 19.0)]
    steps = []
    for y2, y1 in data:
        pp = P + s_g2
        f = y2 * pp * y2 + s_e2
        k = pp * y2 / f
        v = y1 - g * y2
        g_new = g + k * v
        P_new = (1 - k * y2) * pp
        steps.append({"y2": y2, "y1": y1, "gamma_prior": round(g, 5), "P_prior": round(pp, 6),
                      "F": round(f, 5), "K": round(k, 6), "innovation": round(v, 5),
                      "gamma_post": round(g_new, 5), "P_post": round(P_new, 6)})
        g, P = g_new, P_new
    return {"sigma_gamma2": s_g2, "sigma_eps2": s_e2, "steps": steps}


def ex_hamilton() -> dict:
    """2-state volatility regime on 10-second mid changes in ticks; zero mean in both states."""
    p11, p22 = 0.99, 0.95
    s = [0.5, 2.0]
    P = np.array([[p11, 1 - p11], [1 - p22, p22]])
    xi0 = np.array([(1 - p22) / (2 - p11 - p22), (1 - p11) / (2 - p11 - p22)])
    ys = [0.0, 2.0, 1.0, 0.0]
    prev = xi0
    steps = []
    for y in ys:
        pred = prev @ P
        eta = np.array([math.exp(-0.5 * (y / sj) ** 2) / (math.sqrt(2 * math.pi) * sj) for sj in s])
        joint = pred * eta
        f = joint.sum()
        post = joint / f
        steps.append({"y": y, "pred": [round(v, 5) for v in pred], "eta": [round(v, 5) for v in eta],
                      "f": round(f, 5), "xi": [round(v, 5) for v in post]})
        prev = post
    return {"p11": p11, "p22": p22, "sigmas": s, "xi0": [round(v, 5) for v in xi0], "steps": steps,
            "expected_durations": [1 / (1 - p11), 1 / (1 - p22)]}


def ex_viterbi_vs_filter() -> dict:
    """Same model; show that the smoothed / Viterbi label at t can change when data after t arrive."""
    p11, p22 = 0.99, 0.95
    s = [0.5, 2.0]
    P = np.array([[p11, 1 - p11], [1 - p22, p22]])
    xi0 = np.array([(1 - p22) / (2 - p11 - p22), (1 - p11) / (2 - p11 - p22)])

    def run(ys):
        eta = np.array([[math.exp(-0.5 * (y / sj) ** 2) / (math.sqrt(2 * math.pi) * sj) for sj in s] for y in ys])
        n = len(ys)
        xi = np.zeros((n, 2))
        prev = xi0
        for t in range(n):
            j = (prev @ P) * eta[t]
            xi[t] = j / j.sum()
            prev = xi[t]
        # Viterbi in logs
        d = np.log(xi0 @ P) + np.log(eta[0])
        bp = np.zeros((n, 2), dtype=int)
        for t in range(1, n):
            cand = d[:, None] + np.log(P)
            bp[t] = cand.argmax(axis=0)
            d = cand.max(axis=0) + np.log(eta[t])
        path = [int(d.argmax())]
        for t in range(n - 1, 0, -1):
            path.append(int(bp[t][path[-1]]))
        return xi, path[::-1]

    a = [0.0, 0.25, 1.5, 0.25]
    b = a + [2.5, 3.0]
    xi_a, vit_a = run(a)
    xi_b, vit_b = run(b)
    return {"obs_short": a, "filtered_high_prob_short": [round(v, 4) for v in xi_a[:, 1]], "viterbi_short": vit_a,
            "obs_long": b, "filtered_high_prob_long": [round(v, 4) for v in xi_b[:, 1]], "viterbi_long": vit_b}


def ex_particle() -> dict:
    """One bootstrap-filter step for the SV model with 5 particles."""
    alpha, sigma, beta = 0.98, 0.15, 1.0
    x_prev = np.array([-0.4, -0.1, 0.0, 0.2, 0.6])
    shocks = np.array([0.5, -1.0, 0.2, 1.2, -0.3])
    x = alpha * x_prev + sigma * shocks
    y = 2.2
    var = beta ** 2 * np.exp(x)
    w = np.exp(-0.5 * y * y / var) / np.sqrt(2 * np.pi * var)
    W = w / w.sum()
    ess = 1 / np.sum(W ** 2)
    lik = w.mean()
    u = 0.37
    cum = np.cumsum(W)
    pts = (u + np.arange(5)) / 5
    idx = np.searchsorted(cum, pts)
    return {"x_prev": x_prev.tolist(), "shocks": shocks.tolist(), "x_prop": [round(v, 4) for v in x],
            "y": y, "w_unnorm": [round(v, 5) for v in w], "W": [round(v, 4) for v in W],
            "ESS": round(float(ess), 3), "lik_increment": round(float(lik), 5),
            "systematic_points": [round(v, 3) for v in pts], "cumW": [round(v, 4) for v in cum],
            "resampled_idx": idx.tolist()}


def ex_ukf() -> dict:
    """E[exp(x/2)] for x ~ N(0,1): exact, EKF (linearise at mean), UT (alpha=1, beta=2, kappa=2)."""
    exact = math.exp(1 / 8)
    ekf = math.exp(0.0)
    L, alpha, kappa = 1, 1.0, 2.0
    lam = alpha ** 2 * (L + kappa) - L
    spread = math.sqrt(L + lam)
    pts = [0.0, spread, -spread]
    wm = [lam / (L + lam), 1 / (2 * (L + lam)), 1 / (2 * (L + lam))]
    ut = sum(w * math.exp(p / 2) for w, p in zip(wm, pts))
    return {"exact": round(exact, 5), "ekf": ekf, "ut": round(ut, 5), "lambda": lam,
            "sigma_points": [round(p, 4) for p in pts], "weights": [round(w, 4) for w in wm]}


def ex_power() -> dict:
    """Two-sample comparison of mean markout between gate-on and gate-off fills.
    n per group = 2 (z_a + z_b)^2 sigma^2 / d^2 with z_a = 3.0 (program bar t > 3.0), power 0.8."""
    za, zb = 3.0, norm.ppf(0.8)
    rows = []
    for sigma in (1.0, 1.5, 2.0):
        for d in (0.10, 0.25, 0.50):
            n = 2 * (za + zb) ** 2 * sigma ** 2 / d ** 2
            rows.append({"sigma_ticks": sigma, "d_ticks": d, "n_per_group": int(math.ceil(n))})
    one = []
    for sigma in (1.0, 1.5, 2.0):
        for d in (0.10, 0.25, 0.50):
            one.append({"sigma_ticks": sigma, "d_ticks": d,
                        "n_one_sample": int(math.ceil((za + zb) ** 2 * sigma ** 2 / d ** 2))})
    return {"z_alpha": za, "z_beta": round(float(zb), 4), "two_sample": rows, "one_sample": one}


def main() -> None:
    res = {"local_level": ex_local_level(), "hedge": ex_hedge(), "hamilton": ex_hamilton(),
           "viterbi_vs_filter": ex_viterbi_vs_filter(), "particle": ex_particle(), "ukf": ex_ukf(),
           "power": ex_power()}
    OUT.write_text(json.dumps(res, indent=1))
    print("wrote", OUT.name)


if __name__ == "__main__":
    main()
