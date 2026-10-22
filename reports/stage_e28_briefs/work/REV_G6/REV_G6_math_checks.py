"""REV_G6 independent numeric re-derivations for C2_AFML.md and C2_Firms.md (synthetic data only).
Writes REV_G6_math_checks.json next to this file and prints a short summary.
Run: uv run python reports/stage_e28_briefs/work/REV_G6/REV_G6_math_checks.py
"""
import json
import math
import os
from itertools import combinations

import numpy as np
import sympy as sp
from scipy.signal import fftconvolve
from scipy.stats import norm as N01

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "REV_G6_math_checks.json")
R = {}

# ---------------- A. FFD weights, closed form, partial sums ----------------
def ffd_weights(d, tau):
    w = [1.0]; k = 1
    while True:
        wk = -w[-1] * (d - k + 1) / k
        if abs(wk) < tau:
            break
        w.append(wk); k += 1
    return np.array(w)

d_, k_, l_ = sp.symbols("d k l")
# symbolic: w_k = (-1)^k C(d,k) and w_k/w_{k-1} = -(d-k+1)/k ; S(l) = prod_{k=1}^l (1 - d/k)
wk = (-1) ** k_ * sp.binomial(d_, k_)
ratio = sp.simplify(sp.gammasimp(wk.subs(k_, 5) / wk.subs(k_, 4)))
R["A_sympy_ratio_w5_over_w4"] = str(ratio)  # expect -(d-4)/5
sym_ok = []
for L in range(0, 7):
    S = sum((-1) ** k * sp.binomial(d_, k) for k in range(L + 1))
    P = sp.prod([1 - d_ / k for k in range(1, L + 1)]) if L else sp.Integer(1)
    G = sp.gamma(L + 1 - d_) / (sp.gamma(1 - d_) * sp.gamma(L + 1))
    sym_ok.append(bool(sp.simplify(sp.expand_func(S - P)) == 0) and bool(sp.simplify(sp.gammasimp(G - P)) == 0))
R["A_sympy_partial_sum_identity_l0_6"] = sym_ok
# closed form Gamma(k-d)/(Gamma(k+1)Gamma(-d)) vs recursion, d=0.4, k<=50
w = ffd_weights(0.4, 1e-12)
kk = np.arange(len(w))
from scipy.special import gammaln
cf = np.exp(gammaln(kk - 0.4) - gammaln(kk + 1) - gammaln(0.6)) * (-1) / 0.4  # Gamma(-d) = Gamma(1-d)/(-d)
cf[0] = 1.0
R["A_closed_form_max_abs_dev_k_le_50"] = float(np.max(np.abs(w[:51] - cf[:51])))
R["A_first6_d0.4"] = [round(float(v), 6) for v in w[:6]]
tab = {}
for d in (0.2, 0.4, 0.6):
    for tau in (1e-3, 1e-4, 1e-5):
        ww = ffd_weights(d, tau); L = len(ww); lstar = L - 1
        tab[f"d{d}_tau{tau:g}"] = {"window_L": L, "sum_w": round(float(ww.sum()), 5),
                                   "asym_with_lstar": round(lstar ** (-d) / math.gamma(1 - d), 5),
                                   "asym_with_L": round(L ** (-d) / math.gamma(1 - d), 5),
                                   "exact_Gamma_formula_lstar": round(math.exp(gammaln(lstar + 1 - d) - gammaln(1 - d) - gammaln(lstar + 1)), 5)}
R["A_ffd_table"] = tab

# ---------------- C. random walk passes "minimum d" ADF: lag sensitivity + variance decomposition ----------------
def adf_t(x, lags):
    dx = np.diff(x); yv = dx[lags:]
    cols = [np.ones_like(yv), x[lags:-1]] + [dx[lags - i:-i] for i in range(1, lags + 1)]
    X = np.column_stack(cols)
    beta, *_ = np.linalg.lstsq(X, yv, rcond=None)
    e = yv - X @ beta; s2 = e @ e / (len(yv) - X.shape[1])
    cov = s2 * np.linalg.inv(X.T @ X)
    return float(beta[1] / math.sqrt(cov[1, 1]))

def ffd(x, d, tau):
    ww = ffd_weights(d, tau)
    y = fftconvolve(x, ww, mode="full")[: len(x)]
    return y[len(ww) - 1:], ww

rw = {}
for seed in (0, 1, 2):
    rng = np.random.default_rng(seed)
    T = 200_000
    r = rng.normal(0, 1e-4, T); x = np.cumsum(r) + math.log(5000.0)
    for d in (0.2, 0.3, 0.4, 0.6, 1.0):
        y, ww = ffd(x, d, 1e-4); ys = y[::10]
        n = len(ys); schwert = int(12 * (n / 100) ** 0.25)
        row = {f"adf_lags{p}": round(adf_t(ys, p), 2) for p in (1, 4, 12, schwert)}
        row["schwert_lags"] = schwert
        # variance decomposition of y = S x_t + MA(returns)
        S = float(ww.sum()); xo = x[len(ww) - 1:]
        lev = S * xo; ma = y - lev
        row["sd_level_part"] = float(np.std(lev)); row["sd_MA_part"] = float(np.std(ma))
        row["share_var_level_part"] = round(float(np.var(lev) / np.var(y)), 3)
        row["sum_w_lags_ge1"] = round(S - 1.0, 3)
        rw[f"seed{seed}_d{d}"] = row
R["C_random_walk_adf_by_lags"] = rw

# ---------------- D. uniqueness at pilot scale: mean u_bar for 60-s labels at one order per 41.4 s ----------------
rng = np.random.default_rng(7)
def mean_ubar(starts, H):
    starts = np.sort(starts); n = len(starts)
    # concurrency on a 1-s grid
    tmax = int(starts[-1] + H + 2); c = np.zeros(tmax + 1)
    s0 = np.floor(starts).astype(int)
    for s in s0:
        c[s:s + H] += 1
    ub = np.empty(n)
    for i, s in enumerate(s0):
        ub[i] = np.mean(1.0 / c[s:s + H])
    return float(ub.mean())
span = 20_000 * 41.4
pois = np.cumsum(rng.exponential(41.4, 20_000)); reg = np.arange(20_000) * 41.4 + 0.5
R["D_ubar_poisson_arrivals"] = round(mean_ubar(pois, 60), 3)
R["D_ubar_regular_arrivals"] = round(mean_ubar(reg, 60), 3)
R["D_ubar_formula_1_over_1_plus_2.9"] = round(1 / (1 + 2.9), 3)
R["D_ubar_formula_1_over_1_plus_1.45"] = round(1 / 1.45, 3)
R["D_ubar_poisson_closed_form_(1-e^-m)/m_m1.45"] = round((1 - math.exp(-1.45)) / 1.45, 3)
R["D_other_labels_overlapping_a_label_2H/spacing"] = round(120 / 41.4, 2)

# ---------------- E. CPCV ----------------
cp = {}
for Nn, k in ((6, 2), (10, 2), (10, 3), (12, 2), (16, 4)):
    splits = math.comb(Nn, k); phi = k * splits // Nn
    cp[f"N{Nn}_k{k}"] = {"splits": splits, "phi": phi, "phi_identity_C(N-1,k-1)": math.comb(Nn - 1, k - 1),
                        "train_frac": round((Nn - k) / Nn, 3)}
cnt = {g: 0 for g in range(6)}
for c in combinations(range(6), 2):
    for g in c: cnt[g] += 1
cp["N6_k2_group_test_counts"] = cnt
R["E_cpcv"] = cp

# ---------------- F. Haar MODWT J=2 on X=(4,6,10,12,8,6,5,5): forward, energy, MRA, causality ----------------
def modwt_haar(X, J):
    Nn = len(X); h = np.array([0.5, -0.5]); g = np.array([0.5, 0.5])
    V = X.astype(float).copy(); Ws = []
    for j in range(1, J + 1):
        W = np.zeros(Nn); Vn = np.zeros(Nn)
        for t in range(Nn):
            for l in range(2):
                idx = (t - 2 ** (j - 1) * l) % Nn
                W[t] += h[l] * V[idx]; Vn[t] += g[l] * V[idx]
        Ws.append(W); V = Vn
    return Ws, V

def imodwt_haar_level(W, V, j):
    Nn = len(W); h = np.array([0.5, -0.5]); g = np.array([0.5, 0.5]); Vp = np.zeros(Nn)
    for t in range(Nn):
        for l in range(2):
            idx = (t + 2 ** (j - 1) * l) % Nn
            Vp[t] += h[l] * W[idx] + g[l] * V[idx]
    return Vp

def mra_haar(X, J):
    Ws, VJ = modwt_haar(X, J); Nn = len(X); D = []
    for j in range(1, J + 1):
        V = np.zeros(Nn); Wj = Ws[j - 1]
        for jj in range(j, 0, -1):
            V = imodwt_haar_level(Wj if jj == j else np.zeros(Nn), V, jj)
        D.append(V)
    S = VJ.copy()
    for jj in range(J, 0, -1):
        S = imodwt_haar_level(np.zeros(Nn), S, jj)
    return Ws, VJ, D, S

X = np.array([4, 6, 10, 12, 8, 6, 5, 5], float)
Ws, V2, D, S2 = mra_haar(X, 2)
R["F_W1"] = Ws[0].tolist(); R["F_W2"] = Ws[1].tolist(); R["F_V2"] = V2.tolist()
R["F_D1"] = D[0].tolist(); R["F_D2"] = D[1].tolist(); R["F_S2"] = S2.tolist()
R["F_energy_X"] = float((X ** 2).sum())
R["F_energy_W1+W2+V2"] = float((Ws[0] ** 2).sum() + (Ws[1] ** 2).sum() + (V2 ** 2).sum())
R["F_mra_max_abs_err"] = float(np.max(np.abs(D[0] + D[1] + S2 - X)))
X2 = X.copy(); X2[7] = 9.0
Ws2, V22, D2_, S22 = mra_haar(X2, 2)
chg = lambda a, b: [int(i) for i in np.where(np.abs(a - b) > 1e-12)[0]]
R["F_causality_changed_idx"] = {"W1": chg(Ws[0], Ws2[0]), "W2": chg(Ws[1], Ws2[1]), "D1": chg(D[0], D2_[0]),
                                "D2": chg(D[1], D2_[1]), "S2": chg(S2, S22)}

# ---------------- G. soft threshold toy ----------------
c = np.array([0.1, -0.3, 2.5, 0.2, -0.05, -1.8, 0.4, 0.0])
sig = np.median(np.abs(c)) / 0.6745; t = sig * math.sqrt(2 * math.log(8))
R["G_soft"] = {"median_abs": float(np.median(np.abs(c))), "sigma": round(sig, 4), "t": round(t, 4),
               "soft": [round(float(np.sign(v) * max(abs(v) - t, 0)), 4) for v in c]}

# ---------------- H. periodogram toy ----------------
xp = np.array([1, 0, -1, 0, 1, 0, -1, 0], float); Xk = np.fft.fft(xp)
R["H_periodogram"] = {"I_k2": float(abs(Xk[2]) ** 2 / 8), "abs_X6": float(abs(Xk[6])),
                      "parseval_lhs": float((xp ** 2).sum()), "parseval_rhs": float((abs(Xk) ** 2).sum() / 8),
                      "other_bins_max": float(np.max(np.abs(np.delete(Xk, [2, 6]))))}

# ---------------- I. power ----------------
za, zb = N01.ppf(0.975), N01.ppf(0.80)
def n1(delta, sd, z=za): return ((z + zb) * sd / delta) ** 2
R["I_power"] = {"z_alpha": round(za, 4), "z_beta": round(zb, 4),
                "one_sample_0.25_2": round(n1(0.25, 2), 1), "one_sample_0.25_4": round(n1(0.25, 4), 1),
                "one_sample_0.10_2": round(n1(0.10, 2), 1),
                "z_bonf_0.05_over_20": round(N01.ppf(1 - 0.0025 / 2), 4),
                "one_sample_bonf_0.25_2": round(n1(0.25, 2, N01.ppf(1 - 0.0025 / 2)), 1),
                "two_sample_per_arm_0.25_2": round(2 * n1(0.25, 2), 1)}

# ---------------- J. meta-label toy ----------------
p, a, b = 0.55, 1.0, 1.2
m = p * a - (1 - p) * b; var = p * a ** 2 + (1 - p) * b ** 2 - m ** 2
R["J_metalabel"] = {"primary_per_fill": round(0.45 * a - 0.55 * b, 3), "breakeven": round(b / (a + b), 4),
                    "secondary_per_fill": round(m, 4), "sd": round(math.sqrt(var), 4), "se_400": round(math.sqrt(var / 400), 4),
                    "t": round(m / math.sqrt(var / 400), 3), "recall": round(220 / 450, 4),
                    "F1": round(2 * 0.55 * (220 / 450) / (0.55 + 220 / 450), 4)}

# ---------------- K. uniqueness toy ----------------
r6 = np.array([0.002, -0.001, 0.003, 0.001, -0.002, 0.004]); spans = {"A": (0, 2), "B": (1, 3), "C": (4, 5)}
cc = np.zeros(6)
for s, e in spans.values(): cc[s:e + 1] += 1
ub = {k: float(np.mean(1 / cc[s:e + 1])) for k, (s, e) in spans.items()}
wt = {k: float(abs(np.sum(r6[s:e + 1] / cc[s:e + 1]))) for k, (s, e) in spans.items()}
tot = sum(wt.values())
R["K_uniqueness"] = {"c": cc.tolist(), "ubar": {k: round(v, 4) for k, v in ub.items()}, "wtilde": {k: round(v, 5) for k, v in wt.items()},
                     "w_norm": {k: round(3 * v / tot, 4) for k, v in wt.items()}, "n_eff": round(sum(ub.values()), 3)}

# ---------------- L. Harvey-Liu example: Lo (2002) autocorrelation correction, haircut ----------------
q, rho = 12, 0.1
den = q + 2 * sum((q - k) * rho ** k for k in range(1, q))
R["L_HL_example"] = {"SR_autocorr_corrected": round(1.0 * math.sqrt(q / den), 4), "haircut_1-0.438/0.912": round(1 - 0.438 / 0.912, 4)}

# ---------------- M. Firms EV toy ----------------
R["M_firms_ev"] = {"EV_p0.52_c0.04": round(2 * 0.52 - 1 - 0.04, 6), "pstar_c0.04": (1 + 0.04) / 2}

# ---------------- N. misc arithmetic ----------------
R["N_misc"] = {"84x23x3600": 84 * 23 * 3600, "1458/6955200_pct": round(100 * 1458 / 6955200, 4),
               "9x7.2Mx8B_GB": round(9 * 7.2e6 * 8 / 1e9, 3), "13x7.2Mx8B_GB": round(13 * 7.2e6 * 8 / 1e9, 3),
               "18x0.89": round(18 * 0.89, 2), "45x5.6s_min": round(45 * 5.6 / 60, 2), "4500x5.6s_h": round(4500 * 5.6 / 3600, 2),
               "270x6s_min": 270 * 6 / 60, "10920x6s_h": round(10920 * 6 / 3600, 2),
               "E_log_z2_gaussian": round(-np.euler_gamma - math.log(2), 4), "2^12_s_min": 2 ** 12 / 60,
               "84x1380": 84 * 1380, "60/41.4": round(60 / 41.4, 3), "0.01x168000": 0.01 * 168000, "1680/2000": 0.84,
               "23h*3600/2000": 23 * 3600 / 2000, "20x1380": 20 * 1380}

# ---------------- O. gambler's ruin check P(up first) = b/(a+b) ----------------
rng = np.random.default_rng(3); a_, b_ = 3, 1; ups = 0; Nsim = 20000
for _ in range(Nsim):
    s = 0
    while -b_ < s < a_:
        s += rng.choice([-1, 1])
    ups += s >= a_
R["O_gamblers_ruin"] = {"a": a_, "b": b_, "sim_P_up_first": round(ups / Nsim, 3), "formula_b/(a+b)": round(b_ / (a_ + b_), 3)}

# ---------------- Q. triple-barrier toy by hand ----------------
path = [100.25, 100.00, 99.75, 100.25, 100.50, 100.75]
def tb(path, up, lo):
    for i, p_ in enumerate(path, 1):
        if p_ >= up: return i, 1
        if p_ <= lo: return i, -1
    return len(path), 0
R["Q_triple_barrier"] = {"pm0.50": tb(path, 100.5, 99.5), "pm0.75": tb(path, 100.75, 99.25)}

json.dump(R, open(OUT, "w"), indent=1, default=float)
print("wrote", OUT)
for k in ("A_sympy_ratio_w5_over_w4", "A_sympy_partial_sum_identity_l0_6", "A_closed_form_max_abs_dev_k_le_50", "A_first6_d0.4"):
    print(k, R[k])
for k, v in R["A_ffd_table"].items(): print(k, v)
for k, v in R["C_random_walk_adf_by_lags"].items(): print(k, v)
for k in ("D_ubar_poisson_arrivals", "D_ubar_regular_arrivals", "D_ubar_formula_1_over_1_plus_2.9", "D_ubar_formula_1_over_1_plus_1.45",
          "D_ubar_poisson_closed_form_(1-e^-m)/m_m1.45"): print(k, R[k])
print("E", R["E_cpcv"])
print("F W1", R["F_W1"]); print("F W2", R["F_W2"]); print("F V2", R["F_V2"]); print("F D1", R["F_D1"]); print("F D2", R["F_D2"]); print("F S2", R["F_S2"])
print("F energy", R["F_energy_X"], R["F_energy_W1+W2+V2"], "mra err", R["F_mra_max_abs_err"]); print("F causality", R["F_causality_changed_idx"])
for k in ("G_soft", "H_periodogram", "I_power", "J_metalabel", "K_uniqueness", "L_HL_example", "M_firms_ev", "N_misc", "O_gamblers_ruin", "Q_triple_barrier"):
    print(k, R[k])
