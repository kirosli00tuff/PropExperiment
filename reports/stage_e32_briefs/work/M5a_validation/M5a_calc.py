"""M5a_validation worked-example calculator (Stage E.32, worker-written; no market data read).

Every number here is arithmetic on the brief's standard ZM numbers, published formulas, or
synthetic random numbers with fixed seeds. Prints a compact report to stdout.
"""
from __future__ import annotations

import math
from datetime import date, timedelta
from itertools import combinations
from statistics import NormalDist

import numpy as np

ND = NormalDist()
GAMMA = 0.5772156649015329
Z = ND.inv_cdf
PHI = ND.cdf


def emax_factor(n: float) -> float:
    """E[max of n iid N(0,1)] approx, BLdP 2014 eq. (1) without the sqrt(V) scale."""
    if n <= 1:
        return 0.0
    return (1 - GAMMA) * Z(1 - 1 / n) + GAMMA * Z(1 - 1 / (n * math.e))


def dsr(sr: float, t: int, n: float, v: float, g3: float = 0.0, g4: float = 3.0) -> tuple[float, float]:
    sr0 = math.sqrt(v) * emax_factor(n)
    d = 1 - g3 * sr + (g4 - 1) / 4 * sr * sr
    return PHI((sr - sr0) * math.sqrt(t - 1) / math.sqrt(d)), sr0


def sr_needed(t: int, n: float, v: float, g3: float, g4: float, conf: float = 0.95) -> float:
    """Smallest SR with DSR >= conf (bisection)."""
    lo, hi = 0.0, 5.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if dsr(mid, t, n, v, g3, g4)[0] >= conf:
            hi = mid
        else:
            lo = mid
    return hi


def section(title: str) -> None:
    print(f"\n=== {title}")


# ---------------------------------------------------------------- calendar (assumption) ----
HOLIDAYS = [  # CBOT grain full closures assumed (not read from any data or CME page)
    "2020-12-25", "2021-01-01", "2021-01-18", "2021-02-15", "2021-04-02", "2021-05-31",
    "2021-07-05", "2021-09-06", "2021-11-25", "2021-12-24", "2022-01-17", "2022-02-21",
    "2022-04-15", "2022-05-30", "2022-06-20", "2022-07-04", "2022-09-05", "2022-11-24",
    "2022-12-26", "2023-01-02", "2023-01-16", "2023-02-20", "2023-04-07", "2023-05-29",
    "2023-06-19", "2023-07-04", "2023-09-04", "2023-11-23", "2023-12-25", "2024-01-01",
    "2024-01-15", "2024-02-19",
]


def weekdays(a: date, b: date) -> int:
    n, d = 0, a
    while d <= b:
        n += d.weekday() < 5
        d += timedelta(days=1)
    return n


section("calendar")
wd = weekdays(date(2020, 12, 1), date(2024, 2, 29))
hol = sum(1 for h in HOLIDAYS if date(2020, 12, 1) <= date.fromisoformat(h) <= date(2024, 2, 29))
T_DAYS = wd - hol
print(f"discovery weekdays {wd}, assumed closures {hol}, trade dates ~{T_DAYS}")
wd_t = weekdays(date(2017, 5, 1), date(2020, 11, 30))
T_TEST = wd_t - 37  # ~10-11 closures a year x 3.58 years (assumption)
print(f"test window weekdays {wd_t}, trade dates ~{T_TEST} (assumed 37 closures)")
MIN_ON, MIN_DAY = 765, 290
print(f"minutes per trade date: overnight {MIN_ON} + day {MIN_DAY} = {MIN_ON + MIN_DAY}")
BARS = T_DAYS * (MIN_ON + MIN_DAY)
print(f"1-min bar slots over discovery ~{BARS}; AFML 0.01T = {0.01 * BARS:.0f} bars = "
      f"{0.01 * BARS / (MIN_ON + MIN_DAY):.2f} trade dates; 0.01 x {T_DAYS} days = {0.01 * T_DAYS:.2f}")

# ---------------------------------------------------------------- (a) purge / embargo ----
section("(a) sigma_h and purge overhead")
S1 = 3.15
for h in (5, 15, 30, 60, 120, 240):
    print(f"h={h:>3} min sigma_h = 3.15 x sqrt({h}) = {S1 * math.sqrt(h):.2f} ticks")
for k in (5, 10):
    for h in (15, 60, 240):
        bar_overhead = k * (2 * h + 0) / (MIN_ON + MIN_DAY) / T_DAYS
        emb = k * 1 / T_DAYS
        print(f"k={k} H={h}: bar-level purge share k*2H/T = {bar_overhead:.4%}; "
              f"1-date embargo share k*1/T_days = {emb:.4%}; Li k(2H+h)/T with h=1 date: "
              f"{bar_overhead + emb:.4%}")

# ---------------------------------------------------------------- (b) CPCV ----
section("(b) CPCV splits/paths")
for ng, k in ((6, 2), (8, 2), (10, 2), (10, 3), (12, 2), (16, 2)):
    splits = math.comb(ng, k)
    paths = k * splits // ng
    print(f"N={ng} k={k}: splits {splits}, paths {paths} (=C({ng - 1},{k - 1})={math.comb(ng - 1, k - 1)}), "
          f"train frac {(ng - k) / ng:.3f}, group ~{T_DAYS / ng:.1f} dates")
for cfg in (200, 1000, 5000):
    for ng, k in ((6, 2), (10, 2)):
        fits = cfg * math.comb(ng, k)
        print(f"configs {cfg} N={ng},k={k}: fits {fits}; at 6 s = {fits * 6 / 3600:.1f} h; "
              f"at 0.5 s = {fits * 0.5 / 3600:.2f} h")
# Sharpe dispersion across paths when true SR=0: each path SR ~ N(0, 1/T_days) (daily basis)
rng = np.random.default_rng(32)
print(f"null path-SR sd (daily basis) ~ 1/sqrt({T_DAYS}) = {1 / math.sqrt(T_DAYS):.4f}; "
      f"annualised x sqrt(252) = {math.sqrt(252 / T_DAYS):.3f}")

# ---------------------------------------------------------------- (c) walk-forward ----
section("(c) walk-forward fold counts (39 months)")
for train, step in ((12, 3), (18, 3), (24, 3), (12, 6)):
    nf = (39 - train) // step
    print(f"anchored/rolling train {train} m, step {step} m: {nf} test folds, OOS months {nf * step}, "
          f"OOS share {nf * step / 39:.2f}")

# ---------------------------------------------------------------- (d) DSR ----
section("(d) BLdP 2014 numerical example replication")
V_ANN, T_EX, SR_ANN = 0.5, 1250, 2.5
v_d = V_ANN / 250
sr_d = SR_ANN / math.sqrt(250)
for n in (100, 46):
    p, sr0 = dsr(sr_d, T_EX, n, v_d, -3, 10)
    print(f"N={n}: SR0 daily {sr0:.4f} (annual {sr0 * math.sqrt(250):.4f}), DSR {p:.4f}")
for n in (87, 88, 89):
    p, _ = dsr(sr_d, T_EX, n, v_d, 0, 3)
    print(f"normal returns N={n}: DSR {p:.4f}")

section("(d) e(N) factor and Monte Carlo check")
rng = np.random.default_rng(7)
for n in (200, 538, 738, 1000, 1538, 5000, 5538):
    mc = np.mean(np.max(rng.standard_normal((4000, n)), axis=1)) if n <= 1538 else float("nan")
    print(f"N={n}: e(N)={emax_factor(n):.4f}  sqrt(2 ln N)={math.sqrt(2 * math.log(n)):.4f}  MC={mc:.4f}")

section("(d) ZM per-trade DSR thresholds (V = 1/T null calibration)")
C = 1.59
for h in (15, 60):
    sig = S1 * math.sqrt(h)
    for t in (408, T_DAYS, 4 * T_DAYS):
        for n in (738, 1538, 5538):
            for g3, g4 in ((0.0, 3.0), (0.0, 8.0), (-0.5, 8.0)):
                v = 1 / t
                srs = sr_needed(t, n, v, g3, g4)
                sr0 = math.sqrt(v) * emax_factor(n)
                mu = C + srs * sig
                tpy = t / (39 / 12)
                print(f"h={h} sig={sig:.2f} T={t} N={n} g3={g3} g4={g4}: SR0={sr0:.4f} SR*={srs:.4f} "
                      f"t*={srs * math.sqrt(t):.2f} gross edge*={mu:.2f} ticks (net {srs * sig:.2f}); "
                      f"annualised SR* = {srs * math.sqrt(tpy):.2f} at {tpy:.0f} trades/yr")

section("(d) DSR of a fixed candidate at the three N")
# candidate: h=15, one trade per trade date, gross 2.6 ticks/trade, sigma 12.20 -> net SR
sig15 = S1 * math.sqrt(15)
for gross in (2.6, 3.0, 3.5):
    sr = (gross - C) / sig15
    for n in (538, 738, 1538, 5538):
        p, sr0 = dsr(sr, T_DAYS, n, 1 / T_DAYS, 0, 8)
        print(f"gross {gross} net SR/trade {sr:.4f} t={sr * math.sqrt(T_DAYS):.2f}: N={n} SR0={sr0:.4f} DSR={p:.4f}")

section("(d) effective N: N_hat = rho + (1 - rho) M (BLdP 2014 eq. 9)")
for m in (200, 1000, 5000):
    for rho in (0.3, 0.5, 0.7, 0.9):
        nh = rho + (1 - rho) * m
        print(f"M={m} rho={rho}: N_hat={nh:.1f}; 538+N_hat={538 + nh:.1f}; e={emax_factor(538 + nh):.4f}")

section("(d) daily-with-zeros vs per-trade equivalence (synthetic)")
rng = np.random.default_rng(11)
p_trade, mu_t, sd_t = 0.5, 0.08, 1.0
days = T_DAYS
z_trade, z_daily = [], []
for _ in range(2000):
    on = rng.random(days) < p_trade
    x = np.where(on, rng.standard_t(5, days) / math.sqrt(5 / 3) * sd_t + mu_t, 0.0)
    tr = x[on]
    z_trade.append(tr.mean() / tr.std() * math.sqrt(tr.size))
    z_daily.append(x.mean() / x.std() * math.sqrt(x.size))
zt, zd = np.array(z_trade), np.array(z_daily)
print(f"p={p_trade}, per-trade SR {mu_t}: mean z per-trade {zt.mean():.3f}, mean z daily-with-zeros "
      f"{zd.mean():.3f}, corr {np.corrcoef(zt, zd)[0, 1]:.4f}")
print(f"daily SR ~ sqrt(p) x trade SR = {math.sqrt(p_trade) * mu_t:.4f}; kurtosis of zero-inflated "
      f"series ~ g4/p (t5: g4=9 -> {9 / p_trade:.1f})")

section("(d) MinBTL (BBLZ 2014 eq. 3.2) at E[max]=1 annualised")
for n in (45, 738, 1538, 5538):
    print(f"N={n}: MinBTL ~ {(emax_factor(n) / 1.0) ** 2:.2f} y; bound 2lnN = {2 * math.log(n):.2f} y")

# ---------------------------------------------------------------- (e) PBO ----
section("(e) PBO CSCV")
print(f"C(16,8) = {math.comb(16, 8)} (paper text prints 12,780); C(8,4)={math.comb(8, 4)}; "
      f"C(10,5)={math.comb(10, 5)}; C(12,6)={math.comb(12, 6)}")
toy = np.array([  # 4 configurations x 8 blocks, net ticks per block (made-up worked example)
    [5, -3, 4, -2, 6, -4, 3, -1],
    [2, 2, -1, 1, 0, 1, -2, 2],
    [-4, 6, -3, 5, -2, 4, -1, 3],
    [1, -1, 1, -1, 1, -1, 1, -1],
], dtype=float)
lams_paper, lams_prog, oos_best = [], [], []
nconf = toy.shape[0]
for tr in combinations(range(8), 4):
    te = [b for b in range(8) if b not in tr]
    ins = toy[:, list(tr)].sum(1)
    oos = toy[:, te].sum(1)
    best = int(np.argmax(ins))
    rank = 1 + int(np.sum(oos < oos[best]))  # 1 = worst ... N = best
    w = rank / (nconf + 1)
    lams_paper.append(math.log(w / (1 - w)))
    worse = int(np.sum(oos < oos[best]))
    r2 = (worse + 0.5) / nconf
    lams_prog.append(math.log(r2 / (1 - r2)))
    oos_best.append(oos[best])
lp, lq = np.array(lams_paper), np.array(lams_prog)
print(f"toy 4x8: splits {lp.size}; PBO paper (lambda<=0 with w=r/(N+1)) {np.mean(lp <= 0):.4f}; "
      f"PBO lambda<0 {np.mean(lp < 0):.4f}; program convention {np.mean(lq <= 0):.4f}; "
      f"P(OOS of IS-best < 0) {np.mean(np.array(oos_best) < 0):.4f}")
first = list(combinations(range(8), 4))[0]
te0 = [b for b in range(8) if b not in first]
print(f"first split train {first}: IS sums {toy[:, list(first)].sum(1)}, OOS sums {toy[:, te0].sum(1)}")
# null simulation
rng = np.random.default_rng(5)
for ncfg, s in ((10, 8), (200, 16)):
    perf = rng.standard_normal((ncfg, T_DAYS))
    w = T_DAYS // s
    blk = np.stack([perf[:, i * w:(i + 1) * w].sum(1) for i in range(s)], 1)
    lam = []
    for tr in combinations(range(s), s // 2):
        mask = np.zeros(s, bool)
        mask[list(tr)] = True
        ins, oos = blk[:, mask].sum(1), blk[:, ~mask].sum(1)
        b = int(np.argmax(ins))
        r = 1 + int(np.sum(oos < oos[b]))
        ww = r / (ncfg + 1)
        lam.append(math.log(ww / (1 - ww)))
    lam = np.array(lam)
    print(f"null {ncfg} configs, S={s}: splits {lam.size}, PBO {np.mean(lam <= 0):.3f}, median lambda {np.median(lam):.3f}")

# ---------------------------------------------------------------- (f) thresholds ----
section("(f) FWER / FDR thresholds, one-sided alpha 0.05")
A = 0.05
for m in (3, 200, 738, 1000, 1538, 5000, 5538):
    lm = sum(1 / i for i in range(1, m + 1))
    print(f"m={m}: Bonferroni p {A / m:.3e} z {Z(1 - A / m):.3f}; BY first p {A / (m * lm):.3e} "
          f"z {Z(1 - A / (m * lm)):.3f} (L_m {lm:.3f}); BH at r=3 p {3 * A / m:.3e} z {Z(1 - 3 * A / m):.3f}")
print(f"HLZ t>3.0: one-sided p {1 - PHI(3.0):.5f}, two-sided {2 * (1 - PHI(3.0)):.5f}; "
      f"equivalent Bonferroni m one-sided {A / (1 - PHI(3.0)):.1f}, two-sided {A / (2 * (1 - PHI(3.0))):.1f}")
print("Holm over 3 (one-sided): " + ", ".join(f"p<={A / (3 - i):.4f} z>={Z(1 - A / (3 - i)):.3f}" for i in range(3)))
print("Bonferroni over 3 x K families: " + ", ".join(f"K={k}: z>={Z(1 - A / (3 * k)):.3f}" for k in (1, 4, 5)))
for k in (4, 5):
    for m in (200, 1000, 5000):
        print(f"planner: K={k} families, alpha_k={A / k:.4f}; within-family Bonferroni over m={m // k}: "
              f"z {Z(1 - A / k / (m // k)):.3f} vs global Bonferroni m={m}: z {Z(1 - A / m):.3f}")

section("(f) max-statistic critical values, equicorrelated one-factor normals (RC/RW logic)")
rng = np.random.default_rng(3)
R = 200000
for m in (738, 1538, 5538):
    for rho in (0.0, 0.5, 0.8):
        f = rng.standard_normal(R)
        u = rng.random(R)
        mx = Z_max = np.array([Z(x) for x in u ** (1 / m)]) if False else None
        # max of m iid N(0,1) via inverse CDF of U^(1/m)
        q = 1 - u ** (1 / m)  # upper-tail prob of the max
        from scipy.special import ndtri
        emax = -ndtri(np.clip(q, 1e-300, 1))
        maxz = math.sqrt(rho) * f + math.sqrt(1 - rho) * emax
        print(f"m={m} rho={rho}: 95% quantile of max z = {np.quantile(maxz, 0.95):.3f} "
              f"(Bonferroni {Z(1 - A / m):.3f})")

section("(f) per-trade SR implied by test thresholds over the test window")
for t in (T_TEST // 2, T_TEST):
    for zc in (1.645, 1.960, 2.128, 3.0):
        print(f"T_test={t}: z {zc} -> SR/trade {zc / math.sqrt(t):.4f}; at sigma_15 {sig15:.2f}: "
              f"net {zc / math.sqrt(t) * sig15:.2f} ticks, gross {C + zc / math.sqrt(t) * sig15:.2f}")
