"""M2_lead_lag worked examples (Stage E.32). No market data is read.

Every input is either a standard ZM number from the E.32 reader brief
(A0_contract_stats Table 1), a contract specification, or a labelled
assumption. Run: nice -n 10 python3 M2_examples.py  (writes M2_examples.json)
"""
import json
import math
import os

import numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "M2_examples.json")
res = {}

# ---------------------------------------------------------------- (a) HY toy
# ZS mids (ticks) observed at its own update times; ZM likewise (seconds).
zs_t = [0.0, 0.4, 1.3, 2.1, 2.6, 3.0]
zs_p = [0, 1, 1, 2, 1, 1]
zm_t = [0.0, 0.7, 1.6, 2.4, 3.0]
zm_p = [0, 0, 1, 1, 0]


def increments(t, p):
    return [((t[i - 1], t[i]), p[i] - p[i - 1]) for i in range(1, len(t))]


def overlap(a, b):
    return max(a[0], b[0]) < min(a[1], b[1])


def hy(tx, px, ty, py, lag=0.0):
    """HY sum; lag>0 shifts Y's intervals back by lag (X leads Y by lag)."""
    s, terms = 0.0, []
    for ix, dx in increments(tx, px):
        for iy, dy in increments(ty, py):
            iy_s = (iy[0] - lag, iy[1] - lag)
            if overlap(ix, iy_s) and dx * dy != 0:
                s += dx * dy
                terms.append([list(ix), list(iy), dx, dy])
    return s, terms


def prev_tick(t, p, grid):
    out = []
    for g in grid:
        k = max(i for i in range(len(t)) if t[i] <= g)
        out.append(p[k])
    return out


hy0, terms = hy(zs_t, zs_p, zm_t, zm_p)
res["a_hy_toy"] = {"zs_t": zs_t, "zs_p": zs_p, "zm_t": zm_t, "zm_p": zm_p,
                   "hy_sum_ticks2": hy0, "nonzero_terms": terms}
for step in (1.0, 0.5):
    grid = list(np.arange(0.0, 3.0 + 1e-9, step))
    a = prev_tick(zs_t, zs_p, grid)
    b = prev_tick(zm_t, zm_p, grid)
    rc = sum((a[i] - a[i - 1]) * (b[i] - b[i - 1]) for i in range(1, len(grid)))
    res["a_hy_toy"][f"prev_tick_rc_step_{step}"] = {"grid": grid, "zs": a, "zm": b, "rc": rc}

# ------------------------------------------- (a) Epps Monte Carlo (assumptions)
# Two Brownian mids in tick units, sigma_1m = 3.11 (ZS) and 3.15 (ZM) ticks,
# correlation RHO (ASSUMED), observed at independent Poisson times with mean
# gaps GAP_S (ASSUMED). No lead-lag in the truth. Day session of 290 min.
RHO = 0.6
GAPS = {"ZS": 3.0, "ZM": 6.0}  # seconds, assumed
rng = np.random.default_rng(32)
T = 290 * 60  # seconds
dt = 0.05
n = int(T / dt)
s1, s2 = 3.11 / math.sqrt(60.0), 3.15 / math.sqrt(60.0)  # ticks per sqrt(s)
REPS = 40
deltas = [1, 5, 15, 60, 300]
pt_corr = {d: [] for d in deltas}
hy_corr = []
for _ in range(REPS):
    z1 = rng.standard_normal(n)
    z2 = RHO * z1 + math.sqrt(1 - RHO ** 2) * rng.standard_normal(n)
    x = np.concatenate([[0.0], np.cumsum(s1 * math.sqrt(dt) * z1)])
    y = np.concatenate([[0.0], np.cumsum(s2 * math.sqrt(dt) * z2)])
    obs = {}
    for k, g in GAPS.items():
        m = rng.random(n + 1) < dt / g
        m[0] = True
        obs[k] = np.flatnonzero(m)
    ix, iy = obs["ZS"], obs["ZM"]
    for d in deltas:
        grid = np.arange(0, n + 1, int(d / dt))
        px = x[ix[np.searchsorted(ix, grid, side="right") - 1]]
        py = y[iy[np.searchsorted(iy, grid, side="right") - 1]]
        rx, ry = np.diff(px), np.diff(py)
        pt_corr[d].append(float(np.sum(rx * ry) / math.sqrt(np.sum(rx ** 2) * np.sum(ry ** 2))))
    # HY with interval overlap (vectorised two-pointer)
    rx, ry = np.diff(x[ix]), np.diff(y[iy])
    a0, a1 = ix[:-1], ix[1:]
    b0, b1 = iy[:-1], iy[1:]
    j_lo = np.searchsorted(b1, a0, side="right")
    j_hi = np.searchsorted(b0, a1, side="left")
    cs = np.concatenate([[0.0], np.cumsum(ry)])
    cov = float(np.sum(rx * (cs[j_hi] - cs[j_lo])))
    hy_corr.append(cov / math.sqrt(np.sum(rx ** 2) * np.sum(ry ** 2)))
res["a_epps_mc"] = {
    "assumptions": {"rho_true": RHO, "mean_gap_s": GAPS, "session_s": T, "dt_s": dt, "reps": REPS},
    "prev_tick_corr_mean": {str(d): round(float(np.mean(v)), 4) for d, v in pt_corr.items()},
    "hy_corr_mean": round(float(np.mean(hy_corr)), 4),
    "hy_corr_sd": round(float(np.std(hy_corr)), 4),
}

# ------------------------------------------------- (b) lead-lag bounds
sig = {"ZM": 3.15, "ZS": 3.11, "ZL": 5.52}
hurdle = 1.59  # ticks, topstep ZM mu*_mkt (stage_e28_ranking.md line 130)
beta_reg_rho1 = sig["ZM"] / sig["ZS"]
res["b_leadlag"] = {
    "zm_ticks_per_zs_tick_rho1": round(beta_reg_rho1, 4),
    "zm_ticks_per_zs_tick_crush_equiv": round(0.25 / 0.22, 4),
    "zs_ticks_needed_rho1": round(hurdle / beta_reg_rho1, 3),
    "remaining_fraction_exp_lag": {
        f"theta{th}_L{L}": round(math.exp(-L / th), 4) for th in (0.5, 1.0, 2.0) for L in (0.3, 1.0)
    },
}

# ------------------------------------------------- (c) crush units
S, Lc, M = 1400.0, 60.00, 420.0  # illustrative prices, NOT data
crush_cents = 11.0 * Lc + 2.2 * M - S
crush_usd = 0.11 * Lc + 0.022 * M - S / 100.0
res["c_units"] = {
    "prices": {"ZS_c_per_bu": S, "ZL_c_per_lb": Lc, "ZM_usd_per_ton": M},
    "crush_c_per_bu": round(crush_cents, 4), "crush_usd_per_bu": round(crush_usd, 4),
    "tick_value_c_per_bu": {"ZS": 0.25, "ZL": round(0.01 * 11, 4), "ZM": round(0.10 * 0.022 * 100, 4)},
    "10_11_9": {"bu": 10 * 5000, "meal_tons": 11 * 100, "meal_ton_per_bu": 11 * 100 / 50000,
                "oil_lb_per_bu": 9 * 60000 / 50000,
                "usd_per_1c_crush": 50000 * 0.01,
                "usd_11_zm_ticks": 11 * 10.0, "usd_50000bu_x_0.22c": 50000 * 0.0022},
}

# ------------------------------------------------- (d) half-life and bias
def hl(phi, h=1.0):
    return math.log(2) / (-math.log(phi) / h)


phi = 0.95
d = {"phi": phi, "kappa_per_min": -math.log(phi), "hl_min": hl(phi)}
for nobs in (60, 290, 5800):
    b = -(1 + 3 * phi) / nobs
    ph = phi + b
    d[f"n{nobs}"] = {"bias": b, "E_phi_hat": ph, "kappa_hat": -math.log(ph), "hl_hat_min": hl(ph)}
# asymptotic CI at n=290 around phi_hat=E_phi_hat (illustration)
nobs = 290
ph = d["n290"]["E_phi_hat"]
se = math.sqrt((1 - ph ** 2) / nobs)
lo, hi = ph - 1.96 * se, ph + 1.96 * se
d["ci_n290"] = {"phi_hat": ph, "se": se, "phi_lo": lo, "phi_hi": hi,
                "hl_lo": hl(lo), "hl_hi": hl(hi) if hi < 1 else float("inf")}
# Monte Carlo: per-hour segments with segment means vs one global mean
rng = np.random.default_rng(7)
REP = 400
seg_len, nseg = 60, 20
est_seg, est_glob, est_day = [], [], []
for _ in range(REP):
    x = np.empty(seg_len * nseg)
    x[0] = rng.standard_normal() / math.sqrt(1 - phi ** 2)
    e = rng.standard_normal(x.size)
    for t in range(1, x.size):
        x[t] = phi * x[t - 1] + e[t]
    X = x.reshape(nseg, seg_len)
    # segment-demeaned pooled OLS (hour fixed effects)
    y1 = X[:, 1:] - X[:, 1:].mean(axis=1, keepdims=True)
    y0 = X[:, :-1] - X[:, :-1].mean(axis=1, keepdims=True)
    est_seg.append(float(np.sum(y1 * y0) / np.sum(y0 * y0)))
    # pooled with one global mean (no cross-segment pairs)
    a1, a0 = X[:, 1:].ravel(), X[:, :-1].ravel()
    est_glob.append(float(np.sum((a1 - a1.mean()) * (a0 - a0.mean())) / np.sum((a0 - a0.mean()) ** 2)))
    # one segment of 290 (a day session)
    z = x[:290]
    est_day.append(float(np.polyfit(z[:-1], z[1:], 1)[0]))
d["mc_segment_effects"] = {
    "reps": REP, "seg_len": seg_len, "nseg": nseg,
    "mean_phi_hourFE": round(float(np.mean(est_seg)), 5),
    "mean_phi_globalmean": round(float(np.mean(est_glob)), 5),
    "mean_phi_one_day_290": round(float(np.mean(est_day)), 5),
    "kendall_pred_hourFE": round(phi - (1 + 3 * phi) / seg_len, 5),
}
res["d_halflife"] = d

# ------------------------------------------------- (e) VECM shares (hypothetical alpha)
beta = np.array([1.0, -0.11, -0.22])  # on (ZS cents, ZL ticks, ZM ticks)
alpha = np.array([-0.02, 0.05, 0.06])  # per minute, HYPOTHETICAL
ba = float(beta @ alpha)
shares = (beta * alpha) / ba
res["e_vecm"] = {
    "beta": beta.tolist(), "alpha_hyp": alpha.tolist(), "beta_alpha": ba,
    "kappa_z_per_min": -math.log(1 + ba), "hl_z_min": math.log(2) / -math.log(1 + ba),
    "shares": [round(float(s), 4) for s in shares],
    "zm_ticks_total_per_1c": alpha[2] / -ba,
    "check_share_over_bM": float(shares[2] / 0.22),
}
# simulate deterministic error correction from z0 = 1 cent to verify
P = np.zeros(3)
z = 1.0
P0 = P.copy()
# construct P so that beta'P = 1: put it all in ZS
P = np.array([1.0, 0.0, 0.0])
for _ in range(5000):
    zt = float(beta @ P)
    P = P + alpha * zt
res["e_vecm"]["sim_final_move"] = (P - np.array([1.0, 0.0, 0.0])).round(4).tolist()
res["e_vecm"]["sim_final_z"] = float(beta @ P)

# ------------------------------------------------- (f) trading a ZM-only dislocation
f = {}
for bM in (0.22, 0.19):
    f[f"zm_alone_ticks_per_1c_bM{bM}"] = round(1 / bM, 4)
tab = []
for bM in (0.22, 0.19):
    for sM in (1.0, 0.5, 0.341, 0.25):
        for D in (1.0, 2.0, 3.0):
            for m in (1, 2):  # time stop in half-lives
                frac = 1 - 2 ** (-m)
                g = D * sM / bM * frac
                tab.append({"bM": bM, "sM": sM, "D_c": D, "stop_HL": m, "frac": frac,
                            "gross_ticks": round(g, 3), "net_ticks": round(g - hurdle, 3)})
f["table"] = tab
f["breakeven_sM"] = {f"bM{bM}_D{D}_m{m}": round(hurdle * bM / (D * (1 - 2 ** (-m))), 4)
                     for bM in (0.22, 0.19) for D in (1.0, 2.0, 3.0) for m in (1, 2)}
# per-trade noise and trades needed: ZM sd over the holding time (random-walk assumption)
for hold in (5, 15, 30):
    sd = 3.15 * math.sqrt(hold)
    for edge in (0.5, 1.0):
        sr = edge / sd
        f[f"hold{hold}_edge{edge}"] = {"sd_ticks": round(sd, 3), "per_trade_sr": round(sr, 4),
                                       "trades_for_t3": math.ceil((3 / sr) ** 2)}
res["f_trade"] = f

with open(OUT, "w") as fh:
    json.dump(res, fh, indent=1, default=float)
print("ok", OUT)
