"""Independent recomputation for MathReview_A (Stage E.32, group A).

Caller: the MathReviewer-A worker only, via `uv run python <this path>`.
Inputs: none (no data files; constants typed in from the standard numbers).
Output: recompute_A.json beside this file, a flat dict of named results.
Written BEFORE reading the reader's M2_examples.py/.json, as the brief requires.
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np

OUT = Path(__file__).with_name("recompute_A.json")
R: dict[str, object] = {}

# ---------------------------------------------------------------- constants
TICK_USD = {"ZM": 10.0, "ZS": 12.5, "ZL": 6.0}
SIG1M = {"ZM": 3.15, "ZS": 3.11, "ZL": 5.52}  # ticks per sqrt(minute), standard numbers
BE_MKT = 1.59  # Topstep ZM market-order break-even, ticks (E.28 ranking row 6)
FEE_USD = 5.28
LN2 = math.log(2.0)


# ------------------------------------------------------------- HY estimator
def hy_cov(t1, p1, t2, p2):
    """Hayashi-Yoshida sum over overlapping half-open intervals (a,b] x (c,d]: overlap iff a<d and c<b."""
    t1 = np.asarray(t1, float); p1 = np.asarray(p1, float)
    t2 = np.asarray(t2, float); p2 = np.asarray(p2, float)
    d1 = np.diff(p1); d2 = np.diff(p2)
    starts1, ends1 = t1[:-1], t1[1:]
    starts2, ends2 = t2[:-1], t2[1:]
    cs = np.concatenate([[0.0], np.cumsum(d2)])
    # j_lo: first interval j with end2[j] > start1[i]
    j_lo = np.searchsorted(ends2, starts1, side="right")
    # j_hi (exclusive): first interval j with start2[j] >= end1[i]
    j_hi = np.searchsorted(starts2, ends1, side="left")
    j_hi = np.maximum(j_hi, j_lo)
    return float(np.sum(d1 * (cs[j_hi] - cs[j_lo])))


def prev_tick(tgrid, t, p):
    idx = np.searchsorted(t, tgrid, side="right") - 1
    return np.asarray(p, float)[idx]


def rc_cov(tgrid, t1, p1, t2, p2):
    a = np.diff(prev_tick(tgrid, t1, p1)); b = np.diff(prev_tick(tgrid, t2, p2))
    return float(np.sum(a * b)), float(np.sum(a * a)), float(np.sum(b * b))


# (a)(i) toy
tS = [0, 0.4, 1.3, 2.1, 2.6, 3.0]; pS = [0, 1, 1, 2, 1, 1]
tM = [0, 0.7, 1.6, 2.4, 3.0]; pM = [0, 0, 1, 1, 0]
R["a_toy_hy"] = hy_cov(tS, pS, tM, pM)
R["a_toy_rc_1s"] = rc_cov(np.arange(0, 3.01, 1.0), tS, pS, tM, pM)[0]
R["a_toy_rc_0p5s"] = rc_cov(np.arange(0, 3.01, 0.5), tS, pS, tM, pM)[0]

# (a)(ii) Epps Monte Carlo, my own seed and implementation
rng = np.random.default_rng(20261027)
T_s = 290 * 60.0
rho_true = 0.6
grids = [1, 5, 15, 60, 300]
reps = 40
pt_corr = {g: [] for g in grids}; hy_corr = []; beta_att = {g: [] for g in grids}
for _ in range(reps):
    nS = rng.poisson(T_s / 3.0); nM = rng.poisson(T_s / 6.0)
    tS_ = np.sort(rng.uniform(0, T_s, nS)); tM_ = np.sort(rng.uniform(0, T_s, nM))
    tS_ = np.concatenate([[0.0], tS_]); tM_ = np.concatenate([[0.0], tM_])
    tu = np.unique(np.concatenate([tS_, tM_]))
    dt = np.diff(tu)
    z1 = rng.standard_normal(dt.size); z2 = rng.standard_normal(dt.size)
    sS = SIG1M["ZS"] / math.sqrt(60); sM = SIG1M["ZM"] / math.sqrt(60)
    incS = sS * np.sqrt(dt) * z1
    incM = sM * np.sqrt(dt) * (rho_true * z1 + math.sqrt(1 - rho_true**2) * z2)
    BS = np.concatenate([[0.0], np.cumsum(incS)]); BM = np.concatenate([[0.0], np.cumsum(incM)])
    pS_ = BS[np.searchsorted(tu, tS_)]; pM_ = BM[np.searchsorted(tu, tM_)]
    U = hy_cov(tS_, pS_, tM_, pM_)
    rvS = float(np.sum(np.diff(pS_) ** 2)); rvM = float(np.sum(np.diff(pM_) ** 2))
    hy_corr.append(U / math.sqrt(rvS * rvM))
    for g in grids:
        tg = np.arange(0, T_s + 1e-9, g)
        c, vS, vM = rc_cov(tg, tS_, pS_, tM_, pM_)
        pt_corr[g].append(c / math.sqrt(vS * vM))
        beta_att[g].append((c / vS) / (rho_true * sM / sS))  # OLS beta of ZM on ZS vs true beta
R["a_epps_pt_corr_mean"] = {str(g): round(float(np.mean(v)), 4) for g, v in pt_corr.items()}
R["a_epps_pt_corr_sd"] = {str(g): round(float(np.std(v, ddof=1)), 4) for g, v in pt_corr.items()}
R["a_epps_hy_mean_sd"] = (round(float(np.mean(hy_corr)), 4), round(float(np.std(hy_corr, ddof=1)), 4))
R["a_epps_beta_attenuation_mean"] = {str(g): round(float(np.mean(v)), 4) for g, v in beta_att.items()}
R["a_epps_corr_ratio_60_300"] = (round(float(np.mean(pt_corr[60])) / rho_true, 4), round(float(np.mean(pt_corr[300])) / rho_true, 4))
# analytic staleness approximation: E|U1-U2| for independent exponentials with means 3 s and 6 s
e_abs = 3 + 6 - 2 * (1 / (1 / 3 + 1 / 6))
R["a_epps_analytic_1_minus_EabsU_over_delta"] = {str(g): round(1 - e_abs / g, 4) for g in (60, 300)}

# ------------------------------------------------------------- (b) shift model
sig1s = {k: v / math.sqrt(60) for k, v in SIG1M.items()}
R["b_sigma_1s_ticks"] = {k: round(v, 4) for k, v in sig1s.items()}
def sd_pred(theta, L, rho):
    return rho * sig1s["ZM"] * math.sqrt(max(theta - L, 0.0))
R["b_case1_sd"] = round(sd_pred(1.0, 0.3, 0.6), 4)
R["b_case1_sds_needed"] = round(BE_MKT / sd_pred(1.0, 0.3, 0.6), 2)
R["b_case2_sd"] = round(sd_pred(2.0, 0.3, 1.0), 4)
R["b_case2_sds_needed"] = round(BE_MKT / sd_pred(2.0, 0.3, 1.0), 2)
slope = SIG1M["ZM"] / SIG1M["ZS"]
R["b_static_slope_zm_per_zs_tick"] = round(slope, 4)
R["b_static_zs_ticks_needed"] = round(BE_MKT / slope, 3)
R["b_static_zs_1s_sds_needed"] = round(BE_MKT / slope / sig1s["ZS"], 2)
R["b_crush_ratio_zm_per_zs_tick"] = round(0.25 / 0.22, 4)
R["b_crush_zs_ticks_needed"] = round(BE_MKT / (0.25 / 0.22), 3)
R["b_grid_points"] = (len(np.arange(-60, 61, 1)), len(np.round(np.arange(-5, 5.0001, 0.1), 3)))
R["b_compute_steps"] = 222 * 4e5 * 815

# ------------------------------------------------------------- (c) units
ZS, ZL, ZM = 1400.0, 60.0, 420.0
C = 11 * ZL + 2.2 * ZM - ZS
R["c_crush_example_cents"] = C
R["c_cents_per_tick"] = {"ZL": 11 * 0.01, "ZM": 2.2 * 0.10, "ZS": 0.25}
R["c_zm_ticks_per_cent_physical"] = round(1 / 0.22, 4)
R["c_zm_ticks_per_cent_zhou019"] = round(1 / 0.19, 4)
R["c_usd_per_zm_lot_per_cent"] = round(10 / 0.22, 3)
R["c_1100ton_check_usd"] = round(1100 * (1 / 0.22) * 0.10, 2)  # 11 lots x 4.545 ticks x 10 USD
R["c_zm_shock_4p545_on_median_resid_cents"] = round(0.19 / 0.22, 4)
R["c_10_11_9_oil_lb_per_bu"] = 9 * 60000 / 50000
R["c_10_11_9_oil_shortfall"] = round(1 - 10.8 / 11, 4)
R["c_mackinnon_T290"] = round(-3.74066 - 8.5631 / 290 - 10.852 / 290**2 + 27.982 / 290**3, 5)
R["c_mackinnon_T5800"] = round(-3.74066 - 8.5631 / 5800 - 10.852 / 5800**2 + 27.982 / 5800**3, 5)
R["c_minutes_per_day"] = (12 * 60 + 45) + (4 * 60 + 50)
R["c_rows_3roots"] = 3 * 1055 * 815
R["c_mb_float64_one_col"] = round(3 * 1055 * 815 * 8 / 1e6, 1)

# ------------------------------------------------------------- (d) half-life
b = 0.95
R["d_kappa"] = round(-math.log(b), 5)
R["d_HL_true"] = round(LN2 / -math.log(b), 3)
def kendall(bt, T):
    return bt - (1 + 3 * bt) / T
def HL(bb):
    return float("inf") if bb >= 1 else LN2 / -math.log(bb)
for T in (60, 290, 5800):
    bh = kendall(b, T)
    R[f"d_bhat_T{T}"] = round(bh, 5)
    R[f"d_HLhat_T{T}"] = round(HL(bh), 3)
    R[f"d_HL_short_frac_T{T}"] = round(1 - HL(bh) / HL(b), 3)
    R[f"d_corrected_T{T}"] = round((T * bh + 1) / (T - 3), 6)
    se = math.sqrt((1 - bh**2) / T)
    lo, hi = bh - 1.96 * se, bh + 1.96 * se
    R[f"d_se_T{T}"] = round(se, 5)
    R[f"d_b_ci_T{T}"] = (round(lo, 5), round(hi, 5))
    R[f"d_HL_ci_T{T}"] = (round(HL(lo), 2), (round(HL(hi), 2) if hi < 1 else "inf"))

# by-hour Monte Carlo, own seed
rng = np.random.default_rng(7)
nrep, nseg, L = 400, 20, 60
res = {"seg_demean_common": [], "lsdv": [], "global_mean": [], "single290": []}
for _ in range(nrep):
    n = nseg * L + 200
    e = rng.standard_normal(n); z = np.empty(n); z[0] = e[0] / math.sqrt(1 - b * b)
    for t in range(1, n):
        z[t] = b * z[t - 1] + e[t]
    z = z[200:].reshape(nseg, L)
    x = z[:, :-1]; y = z[:, 1:]
    # (A) each segment's own (single) mean removed from both x and y, pooled OLS through origin
    m = z.mean(axis=1, keepdims=True)
    xa = (x - m).ravel(); ya = (y - m).ravel()
    res["seg_demean_common"].append(float(xa @ ya / (xa @ xa)))
    # (A') LSDV: separate means of x and y per segment
    xb = (x - x.mean(axis=1, keepdims=True)).ravel(); yb = (y - y.mean(axis=1, keepdims=True)).ravel()
    res["lsdv"].append(float(xb @ yb / (xb @ xb)))
    # (B) one global mean, within-segment pairs only
    xg = x.ravel() - x.mean(); yg = y.ravel() - y.mean()
    res["global_mean"].append(float(xg @ yg / (xg @ xg)))
    # (C) one 290-minute series
    n2 = 290 + 200
    e2 = rng.standard_normal(n2); w = np.empty(n2); w[0] = e2[0] / math.sqrt(1 - b * b)
    for t in range(1, n2):
        w[t] = b * w[t - 1] + e2[t]
    w = w[200:]
    xs = w[:-1] - w[:-1].mean(); ys = w[1:] - w[1:].mean()
    res["single290"].append(float(xs @ ys / (xs @ xs)))
for k, v in res.items():
    R[f"d_mc_{k}_mean"] = round(float(np.mean(v)), 5)
    R[f"d_mc_{k}_se"] = round(float(np.std(v, ddof=1) / math.sqrt(nrep)), 5)
R["d_mc_HL_seg_demean"] = round(HL(float(np.mean(res["seg_demean_common"]))), 3)
R["d_mc_HL_lsdv"] = round(HL(float(np.mean(res["lsdv"]))), 3)
# Nickell (1981) LSDV bias for comparison, T = 60 observations per unit
Tn = 60
A = 1 - (1 / Tn) * (1 - b**Tn) / (1 - b)
num = -(1 + b) / (Tn - 1) * A
den = 1 - 2 * b / ((1 - b) * (Tn - 1)) * A
R["d_nickell_bias_T60"] = round(num / den, 5)
R["d_nickell_bhat_T60"] = round(b + num / den, 5)
R["d_hansen_steps"] = 200 * 1999 * 290
R["d_intervals"] = 24 * 2 * 40

# ------------------------------------------------------------- (e) shares
alpha = np.array([-0.02, 0.05, 0.06])
def shares(beta):
    beta = np.array(beta, float)
    ba = float(beta @ alpha)
    s = beta * alpha / ba
    bb = 1 + ba
    out = {"beta_alpha": round(ba, 5), "b": round(bb, 5), "HL_min": round(HL(bb), 3),
           "shares": [round(float(v), 4) for v in s], "sum": round(float(s.sum()), 6),
           "zm_ticks_per_cent": round(float(alpha[2] / -ba), 4),
           "zm_check_s_over_b": round(float(s[2] / -beta[2]), 4)}
    # deterministic iteration from z0 = 1 c (ZS shock)
    P = np.array([1.0, 0.0, 0.0]); P0 = P.copy()
    for _ in range(5000):
        z = float(beta @ P)
        P = P + alpha * z
    mv = P - P0
    out["iter_moves"] = [round(float(v), 4) for v in mv]
    out["iter_final_z"] = float(beta @ P)
    return out
R["e_physical"] = shares([1, -0.11, -0.22])
R["e_median"] = shares([1, -0.11, -0.19])
R["e_rows_1s_day"] = 290 * 60

# ------------------------------------------------------------- (f) trade
def G(sM, D, m, bM):
    return sM * D * (1 - 2.0 ** (-m)) / bM
def sM_star(D, m, bM):
    return BE_MKT * bM / (D * (1 - 2.0 ** (-m)))
sMm = R["e_median"]["shares"][2]; sMp = R["e_physical"]["shares"][2]
R["f_G_median_D1"] = {f"m{m}": round(G(sMm, 1, m, 0.19), 3) for m in (1, 2, 3)}
R["f_D_needed_median"] = {f"m{m}": round(BE_MKT / G(sMm, 1, m, 0.19), 3) for m in (1, 2, 3)}
R["f_D_needed_physical"] = {f"m{m}": round(BE_MKT / G(sMp, 1, m, 0.22), 3) for m in (1, 2, 3)}
R["f_check_m2_D1p304"] = round(G(sMm, 1.304, 2, 0.19), 3)
tab = {}
for bM in (0.22, 0.19):
    for D in (0.5, 1, 2, 3):
        tab[f"bM{bM}_D{D}"] = {"sM_star": [round(sM_star(D, m, bM), 4) for m in (1, 2, 3)],
                               "gross_at_sM1": [round(G(1, D, m, bM), 3) for m in (1, 2, 3)]}
R["f_table"] = tab
R["f_bottom_line_sM_star_D1_m1_bM022"] = round(sM_star(1, 1, 0.22), 4)
R["f_bottom_line_sM_star_D2_m1_bM022"] = round(sM_star(2, 1, 0.22), 4)
R["f_sM_star_D1_range_m1to3_bM022"] = [round(sM_star(1, m, 0.22), 3) for m in (1, 2, 3)]
for hold in (36, 15):
    sd = SIG1M["ZM"] * math.sqrt(hold)
    sh = 1.0 / sd
    R[f"f_noise_hold{hold}"] = {"sd": round(sd, 2), "sharpe_1tick": round(sh, 4), "n_t3": round((3 / sh) ** 2), "per_session": round((3 / sh) ** 2 / 815, 2)}
R["f_fee_ticks"] = FEE_USD / 10

# ------------------------------------------------------------- R3a arithmetic
R["r_contract_sizes"] = {"ZM_tons": 10 / 0.10, "ZS_bu": 12.5 / 0.0025, "ZL_lb": 6 / 0.0001}
R["r_meal_44_tons_11zm"] = (50000 * 44 / 2000, 50000 * 44 / 2000 / 100)
R["r_meal_48_tons"] = (50000 * 48 / 2000, 50000 * 48 / 2000 / 100)
R["r_oil_lots"] = round(50000 * 11 / 60000, 3)
R["r_husks_10_11_9"] = 3_000_000 - 2_200_000 - 540_000
R["r_husks_10_12_9"] = 3_000_000 - 2_400_000 - 540_000
R["r_usd_per_cent_10lot"] = 50000 * 0.01
R["r_zm_tick_cents_44"] = round(0.022 * 0.10 * 100, 4)
R["r_zm_tick_cents_48"] = round(0.024 * 0.10 * 100, 4)
R["r_ticks_per_cent_48"] = round(1 / 0.24, 3)
R["r_rp_cost_check"] = (2 * 0.25, round(2 * 0.10 * 0.024 * 100, 4), round(2 * 0.01 * 10.8, 4), round(0.5 + 0.48 + 0.216, 4))
R["r_leg_vol_cents"] = {"ZM": round(3.15 * 0.22, 4), "ZS": round(3.11 * 0.25, 4), "ZL": round(5.52 * 0.11, 4), "sum": round(3.15 * 0.22 + 3.11 * 0.25 + 5.52 * 0.11, 3)}
meal48 = 0.024 * 312.90; oil = 0.11 * 58.62
R["r_oilshare_oct21_48"] = {"meal": round(meal48, 4), "oil": round(oil, 4), "OS": round(oil / (meal48 + oil), 4), "margin": round(meal48 + oil - 11.88, 4)}
meal44 = 0.022 * 312.90
R["r_oilshare_oct21_44"] = {"meal": round(meal44, 4), "OS": round(oil / (meal44 + oil), 4), "margin": round(meal44 + oil - 11.88, 4)}
m2 = 0.024 * 417.60; o2 = 0.11 * 44.62
R["r_oilshare_jan21_48"] = {"meal": round(m2, 4), "oil": round(o2, 4), "OS": round(o2 / (m2 + o2), 4)}
R["r_residual_for_one_breakeven_cents"] = round(BE_MKT / (1 / 0.22), 4)
R["r_2p3"] = {"oil_drop": round(0.232 - 0.070, 3), "oil_ratio": round(0.070 / 0.232, 4), "meal_drop": round(0.511 - 0.451, 3), "meal_ratio": round(0.451 / 0.511, 4)}
R["r_3p2_shares"] = {"180/243": round(180 / 243, 4), "229/243": round(229 / 243, 4), "52/243": round(52 / 243, 4), "64/243": round(64 / 243, 4), "70/243": round(70 / 243, 4), "0.03/0.22": round(0.03 / 0.22, 4), "0.28/0.19": round(0.28 / 0.19, 3)}
# Zhou vector units: which scalings give (1, -0.11, -0.22)?
R["r_3p2_units"] = {
    "A_ZScents_ZLticks_ZMticks": [1, round(11 * 0.01, 3), round(2.2 * 0.10, 3)],
    "B_ZSusd_ZLcents_ZM10usd": [1, round(0.11, 3), round(0.022 * 10, 3)],
    "R3a_claim_ZSusd_ZL0p01c_ZM0p1usd": [1, round(0.11 * 0.01, 5), round(0.022 * 0.10, 5)],
    "quote_units_ZScents_ZLcents_ZMusd": [1, 11, 2.2],
}
R["r_4p2a"] = {"gross0": round(-0.36 + 1.50, 2), "gross3": round(1.74 + 1.50, 2)}
R["r_4p2b"] = {"b_7887": round(-0.49 * 2.837 / 2.727, 4), "b_8791": round(-0.43 * 3.133 / 3.241, 4)}
theta_d = LN2 / 3; theta_m = theta_d / 290
R["r_4p2c"] = {"theta_day": round(theta_d, 4), "theta_min": round(theta_m, 7), "frac_60min": round(1 - math.exp(-60 * theta_m), 4), "zm_ticks": round((1 - math.exp(-60 * theta_m)) / 0.22, 3)}
R["r_4p2d"] = {"H1": round(math.log(0.5) / math.log(1 - 0.0256), 2), "H2": round(math.log(0.5) / math.log(1 - 0.0251), 2), "profit": 0.0018 * 600000,
               "net": [1080 - 1125, 1380 - 1125, 2040 - 1125, 865 - 1125], "lbs": [2 * 300000, 3 * 200000, 10 * 60000], "per_lot": round(1080 / 15, 1), "cost_per_lot": 1125 / 15}
R["r_6p2"] = {"pct": 3 * -0.30, "usd_per_ton": round(0.009 * 300, 2), "ticks": round(0.009 * 300 / 0.10, 1), "usd_per_lot": round(300 * 100 * 0.009, 1)}
adv = 36690
R["r_7p2a"] = {"day_per_min": round(0.83 * adv / 290, 2), "night_per_min": round(0.17 * adv / 765, 3), "ratio_ZM": round((0.83 / 0.17) * (765 / 290), 2),
               "ratio_ZS": round((0.78 / 0.22) * (765 / 290), 2), "ratio_ZL": round((0.82 / 0.18) * (765 / 290), 2), "overnight_min": 12 * 60 + 45}
R["r_7p2b"] = {"giveback_cents": round(0.510 * 2.727, 3), "zm_ticks": round(0.510 * 2.727 / 0.22, 2)}
R["r_7p2c"] = {"52+191": 52 + 191, "180+63": 180 + 63}
s60 = 3.15 * math.sqrt(60)
R["r_8p2"] = {"sigma60": round(s60, 2), "se_n39": round(s60 / math.sqrt(39), 2), "n_t2": round((2 * s60 / BE_MKT) ** 2, 1), "years": round((2 * s60 / BE_MKT) ** 2 / 12, 1),
              "min_after_open": 150, "min_before_close": 140, "months": 1 + 12 + 12 + 12 + 2}

OUT.write_text(json.dumps(R, indent=1, default=str))
print("wrote", OUT, "keys", len(R))
