"""C2_AFML worked examples and timing probes. Synthetic data only; no market data is read.

Run: nice -n 10 uv run python reports/stage_e28_briefs/work/C2_AFML/C2_AFML_examples.py
Writes C2_AFML_examples.json next to this file and prints a short summary.
"""
import json
import math
import os
import time
from itertools import combinations
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "4")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "4")
import numpy as np  # noqa: E402
from scipy.signal import fftconvolve  # noqa: E402

OUT = Path(__file__).with_name("C2_AFML_examples.json")
RNG = np.random.default_rng(20261021)
RES = {}


# ---------- 1. fractional differencing ----------
def ffd_weights(d, tau):
    """AFML ch.5 recursion w_k = -w_{k-1} (d-k+1)/k, kept while |w_k| >= tau."""
    w = [1.0]
    k = 1
    while True:
        wk = -w[-1] * (d - k + 1) / k
        if abs(wk) < tau:
            break
        w.append(wk)
        k += 1
        if k > 10_000_000:
            break
    return np.array(w)


def ffd(x, d, tau):
    w = ffd_weights(d, tau)
    y = fftconvolve(x, w, mode="full")[: len(x)]
    return y[len(w) - 1:], w  # drop warm-up points (need full window)


def adf_t(x, lags=1):
    """ADF t-stat with constant: dx_t = a + b x_{t-1} + sum c_i dx_{t-i} + e."""
    dx = np.diff(x)
    yv = dx[lags:]
    cols = [np.ones_like(yv), x[lags:-1]]
    for i in range(1, lags + 1):
        cols.append(dx[lags - i:-i])
    X = np.column_stack(cols)
    beta, *_ = np.linalg.lstsq(X, yv, rcond=None)
    e = yv - X @ beta
    s2 = e @ e / (len(yv) - X.shape[1])
    cov = s2 * np.linalg.inv(X.T @ X)
    return float(beta[1] / math.sqrt(cov[1, 1]))


ex = {}
w04 = ffd_weights(0.4, 1e-4)
ex["weights_d0.4_first6"] = [round(v, 6) for v in w04[:6]]
for d in (0.2, 0.4, 0.6):
    for tau in (1e-3, 1e-4, 1e-5):
        w = ffd_weights(d, tau)
        ex[f"d{d}_tau{tau:g}"] = {"window_len": int(len(w)), "sum_w": round(float(w.sum()), 5),
                                 "approx_l^-d/Gamma(1-d)": round(len(w) ** (-d) / math.gamma(1 - d), 5)}
RES["ffd_weights"] = ex

# random walk with no predictability: "memory" vs predictability
T = 200_000
r = RNG.normal(0, 1e-4, T)          # i.i.d. log returns (pure random walk)
x = np.cumsum(r) + math.log(5000.0)  # log price level
grid = {}
for d in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0):
    if d == 0.0:
        y, w = x.copy(), np.array([1.0])
    else:
        y, w = ffd(x, d, 1e-4)
    xo = x[len(w) - 1:]
    nxt = np.append(r[len(w):], np.nan)[: len(y)]  # return from t to t+1
    ok = ~np.isnan(nxt)
    grid[str(d)] = {"window": int(len(w)), "sum_w": round(float(w.sum()), 5),
                    "adf_t": round(adf_t(y[::10]), 3),  # every 10th point, as AFML-style downsampling
                    "corr_with_level": round(float(np.corrcoef(y, xo)[0, 1]), 4),
                    "corr_with_next_return": round(float(np.corrcoef(y[ok], nxt[ok])[0, 1]), 4)}
RES["ffd_random_walk_T200k_tau1e-4"] = grid
# d* on halves of the sample: is the minimum d stable?
dstar = {}
for name, seg in (("first_half", x[: T // 2]), ("second_half", x[T // 2:]), ("full", x)):
    found = None
    for d in np.round(np.arange(0.05, 1.01, 0.05), 2):
        y, _ = ffd(seg, float(d), 1e-4)
        if adf_t(y[::10]) < -2.8623:
            found = float(d)
            break
    dstar[name] = found
RES["ffd_dstar_by_segment"] = dstar

# timing: FFD of 7.2M points (about 4 months of 1-second bars, 23 h a day)
n_big = 7_200_000
xb = np.cumsum(RNG.normal(0, 1e-4, n_big))
t0 = time.perf_counter()
yb, wb = ffd(xb, 0.4, 1e-5)
RES["timing_ffd_7.2M_d0.4_tau1e-5_s"] = round(time.perf_counter() - t0, 3)
RES["timing_ffd_window"] = int(len(wb))
del xb, yb

# ---------- 2. triple barrier on a toy path ----------
path = [100.00, 100.25, 100.00, 99.75, 100.25, 100.50, 100.75]  # MES-like prices, 0.25 tick
sigma = 0.002  # assumed daily-style vol scale for the toy example
pt_mult, sl_mult, h = 1.0, 1.0, 6
p0 = path[0]
up, dn = p0 * (1 + pt_mult * sigma * 1.0), p0 * (1 - sl_mult * sigma * 1.0)
lab, t1 = None, None
for i, p in enumerate(path[1: h + 1], start=1):
    if p >= up:
        lab, t1 = 1, i
        break
    if p <= dn:
        lab, t1 = -1, i
        break
if lab is None:
    t1 = h
    lab = int(np.sign(path[h] - p0))
RES["triple_barrier_toy"] = {"path": path, "upper": round(up, 4), "lower": round(dn, 4),
                             "label": lab, "t1_index": t1}

# ---------- 3. uniqueness weights ----------
# three labels on 6 return bars: label A spans bars 1-3, B spans 2-4, C spans 5-6
spans = {"A": (1, 3), "B": (2, 4), "C": (5, 6)}
bars = range(1, 7)
rets = {1: 0.002, 2: -0.001, 3: 0.003, 4: 0.001, 5: -0.002, 6: 0.004}
c = {t: sum(1 for s in spans.values() if s[0] <= t <= s[1]) for t in bars}
ubar, wt = {}, {}
for k, (a, b) in spans.items():
    ts = [t for t in bars if a <= t <= b]
    ubar[k] = round(sum(1 / c[t] for t in ts) / len(ts), 4)
    wt[k] = abs(sum(rets[t] / c[t] for t in ts))
tot = sum(wt.values())
RES["uniqueness_toy"] = {"concurrency": c, "avg_uniqueness": ubar,
                         "w_tilde": {k: round(v, 5) for k, v in wt.items()},
                         "w_normalised_to_I": {k: round(v * len(wt) / tot, 4) for k, v in wt.items()}}

# ---------- 4. CPCV counts ----------
cp = {}
for N, k in ((6, 2), (10, 2), (10, 3), (12, 2), (16, 4)):
    splits = math.comb(N, k)
    cp[f"N{N}_k{k}"] = {"splits": splits, "paths": splits * k // N,
                        "train_frac": round((N - k) / N, 3)}
# check path assignment for N=6,k=2: each group appears in phi splits
N, k = 6, 2
cnt = {g: 0 for g in range(N)}
for comb in combinations(range(N), k):
    for g in comb:
        cnt[g] += 1
cp["N6_k2_group_test_counts"] = cnt
RES["cpcv"] = cp

# purge/embargo cost for a 1-lot passive-order dataset (assumed numbers, stated in the brief)
events_per_day, days, horizon_s, session_s = 2000, 84, 60, 23 * 3600
spacing = session_s / events_per_day
RES["purge_toy"] = {"events_per_day": events_per_day, "days": days, "mean_spacing_s": round(spacing, 1),
                    "labels_overlapping_each_label_60s": round(2 * horizon_s / spacing, 2),
                    "N_groups": 6, "k": 2,
                    "purged_per_boundary_events": round(horizon_s / spacing, 2),
                    "embargo_1pct_events": round(0.01 * events_per_day * days, 0)}


# ---------- 5. Haar MODWT, MRA and causality ----------
def modwt_haar(xv, J):
    """MODWT pyramid (Percival & Walden) with Haar filters h~=(1/2,-1/2), g~=(1/2,1/2), circular."""
    V = xv.astype(float)
    W = []
    for j in range(1, J + 1):
        s = 2 ** (j - 1)
        Vl = np.roll(V, s)  # V_{t - 2^{j-1}}
        W.append(0.5 * V - 0.5 * Vl)
        V = 0.5 * V + 0.5 * Vl
    return W, V


def imodwt_haar_level(Wj, Vj, j):
    s = 2 ** (j - 1)
    return 0.5 * Wj + 0.5 * Vj - 0.5 * np.roll(Wj, -s) + 0.5 * np.roll(Vj, -s)


def mra_haar(xv, J):
    W, VJ = modwt_haar(xv, J)
    D = []
    z = np.zeros_like(xv, dtype=float)
    for j in range(1, J + 1):
        cur = imodwt_haar_level(W[j - 1], z, j)  # level j: wavelet coefs only
        for jj in range(j - 1, 0, -1):
            cur = imodwt_haar_level(z, cur, jj)  # lower levels: pass through scaling path
        D.append(cur)
    S = VJ.copy()
    for jj in range(J, 0, -1):
        S = imodwt_haar_level(np.zeros_like(S), S, jj)
    return W, VJ, D, S


x8 = np.array([4.0, 6.0, 10.0, 12.0, 8.0, 6.0, 5.0, 5.0])
W, VJ, D, S = mra_haar(x8, 2)
RES["haar_modwt_x8"] = {"x": x8.tolist(), "W1": W[0].tolist(), "W2": W[1].tolist(), "V2": VJ.tolist(),
                        "D1": np.round(D[0], 4).tolist(), "D2": np.round(D[1], 4).tolist(),
                        "S2": np.round(S, 4).tolist(),
                        "mra_sum_error": float(np.abs(D[0] + D[1] + S - x8).max()),
                        "energy_x": float(x8 @ x8),
                        "energy_W1+W2+V2": float(W[0] @ W[0] + W[1] @ W[1] + VJ @ VJ)}
# causality: change the last value, see which earlier outputs move
x8b = x8.copy()
x8b[-1] = 9.0
Wb, VJb, Db, Sb = mra_haar(x8b, 2)
RES["haar_causality"] = {
    "W1_changed_idx": np.nonzero(np.abs(Wb[0] - W[0]) > 1e-12)[0].tolist(),
    "W2_changed_idx": np.nonzero(np.abs(Wb[1] - W[1]) > 1e-12)[0].tolist(),
    "D1_changed_idx": np.nonzero(np.abs(Db[0] - D[0]) > 1e-12)[0].tolist(),
    "S2_changed_idx": np.nonzero(np.abs(Sb - S) > 1e-12)[0].tolist()}

# soft threshold toy (Donoho): sigma from MAD of level-1 coefficients
coef = np.array([0.1, -0.3, 2.5, 0.2, -0.05, -1.8, 0.4, 0.0])
sig = float(np.median(np.abs(coef)) / 0.6745)
thr = sig * math.sqrt(2 * math.log(len(coef)))
soft = np.sign(coef) * np.maximum(np.abs(coef) - thr, 0)
RES["soft_threshold_toy"] = {"coef": coef.tolist(), "sigma_mad": round(sig, 4), "threshold": round(thr, 4),
                             "soft": np.round(soft, 4).tolist()}

# timing: Haar MODWT J=8 on 7.2M points (Db4 roughly 4x the multiplies)
xb = RNG.normal(size=n_big)
t0 = time.perf_counter()
Wbig, Vbig = modwt_haar(xb, 8)
RES["timing_haar_modwt_7.2M_J8_s"] = round(time.perf_counter() - t0, 3)
RES["modwt_7.2M_J8_memory_GB"] = round(9 * n_big * 8 / 1e9, 3)
del Wbig, Vbig, xb

# ---------- 6. periodogram and FFF on synthetic intraday volatility ----------
N_day, days_p = 1380, 60  # 1-minute bars, 23-hour session
n = np.arange(N_day)
u_shape = 1.0 + 0.8 * np.cos(2 * np.pi * n / N_day) + 0.3 * np.cos(4 * np.pi * n / N_day)  # assumed shape
s_n = np.sqrt(u_shape / u_shape.mean())
z = RNG.standard_t(5, size=(days_p, N_day)) / math.sqrt(5 / 3)
sig_day = np.exp(RNG.normal(0, 0.25, days_p))[:, None]
ret = (sig_day * s_n[None, :] * z / math.sqrt(N_day)) * 0.01
a = np.abs(ret).ravel()
a = a - a.mean()
I = np.abs(np.fft.rfft(a)) ** 2 / len(a)
freqs = np.fft.rfftfreq(len(a), d=1.0)  # cycles per minute
top = np.argsort(I[1:])[-3:][::-1] + 1
RES["periodogram_top3"] = [{"freq_cpm": float(freqs[i]), "period_min": round(1 / freqs[i], 1),
                            "I": float(I[i])} for i in top]
# FFF regression on log squared standardised returns (A&B-style), P = 2 cos/sin pairs
xr = np.log((np.abs(ret) / (sig_day / math.sqrt(N_day) * 0.01)) ** 2 + 1e-12).ravel()
nn = np.tile(n, days_p)
cols = [np.ones_like(xr, dtype=float), nn / N_day, (nn / N_day) ** 2]
for p in (1, 2):
    cols += [np.cos(2 * np.pi * p * nn / N_day), np.sin(2 * np.pi * p * nn / N_day)]
X = np.column_stack(cols)
beta, *_ = np.linalg.lstsq(X, xr, rcond=None)
fit = X @ beta
s_hat = np.exp(fit[:N_day] / 2)
s_hat = s_hat / math.sqrt((s_hat ** 2).mean())
RES["fff_fit"] = {"corr_s_hat_vs_true": round(float(np.corrcoef(s_hat, s_n)[0, 1]), 4),
                  "max_abs_err_s": round(float(np.abs(s_hat - s_n).max()), 4),
                  "n_obs": int(len(xr)), "n_params": int(X.shape[1])}

# power: observations needed to detect a mean markout difference (assumed sd)
def n_needed(delta, sd, alpha_z=1.96, beta_z=0.8416):
    return math.ceil(((alpha_z + beta_z) * sd / delta) ** 2)


RES["power_examples"] = {
    "one_sample_delta0.25tick_sd2tick": n_needed(0.25, 2.0),
    "one_sample_delta0.25tick_sd4tick": n_needed(0.25, 4.0),
    "one_sample_delta0.10tick_sd2tick": n_needed(0.10, 2.0),
    "two_sample_delta0.25_sd2_each_group": 2 * n_needed(0.25, 2.0),
    "holm_bonferroni_z_for_m20_alpha0.05": 3.023}

OUT.write_text(json.dumps(RES, indent=1, default=str))
print("wrote", OUT, "keys", len(RES))
print("ffd grid", {k: (v["adf_t"], v["corr_with_level"], v["corr_with_next_return"]) for k, v in grid.items()})
print("dstar", dstar, "timing ffd", RES["timing_ffd_7.2M_d0.4_tau1e-5_s"], "modwt", RES["timing_haar_modwt_7.2M_J8_s"])
print("haar causality", RES["haar_causality"], "mra err", RES["haar_modwt_x8"]["mra_sum_error"])
print("fff", RES["fff_fit"], "pgram", RES["periodogram_top3"][:2])
