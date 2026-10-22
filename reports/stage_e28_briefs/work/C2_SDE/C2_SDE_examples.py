"""C2_SDE worked examples. Synthetic numbers only: no market data is read.

Run: nice -n 10 uv run python reports/stage_e28_briefs/work/C2_SDE/C2_SDE_examples.py
Writes C2_SDE_examples_out.txt next to this script.
All price levels and volatilities are illustrative round numbers, not estimates.
"""
import math
import os
from pathlib import Path

import numpy as np
from scipy.stats import norm

os.nice(10)
OUT = Path(__file__).with_name("C2_SDE_examples_out.txt")
lines: list[str] = []


def say(s: str = "") -> None:
    lines.append(s)


TICK = 0.25          # MES tick in index points (rules/products.py)
TICK_USD = 1.25      # MES tick value in USD (rules/products.py)
COMM_RT = 1.22       # MES round-turn commission USD (rules/products.py, Topstep facts)
P0 = 5000.0          # illustrative index level
ANN_VOL = 0.15       # illustrative annualised volatility
RTH_SEC = 23400      # 6.5-hour regular session in seconds
RNG = np.random.default_rng(20261021)

# ---------------------------------------------------------------- E1 ABM vs GBM
say("E1 ABM vs GBM at tick scale")
sig_d = ANN_VOL / math.sqrt(252)               # daily log-vol
sig_d_pts = P0 * sig_d                          # daily vol in points
sig_1s = sig_d_pts / math.sqrt(RTH_SEC)         # per-second points, all variance in RTH
say(f"daily log-vol {sig_d:.5f}; daily points {sig_d_pts:.2f}; per-second points {sig_1s:.4f} = {sig_1s/TICK:.3f} ticks")
for h in (1, 10, 60):
    sd = sig_1s * math.sqrt(h)
    say(f"  h={h:>2}s sd={sd:.3f} pts = {sd/TICK:.2f} ticks")
s2_sec = (sig_d ** 2) / RTH_SEC                 # log-variance per second
for h in (60, 3600):
    gbm_mean_gap = P0 * (math.exp(0.5 * s2_sec * h) - 1)   # E[S_h]-S_0 when log drift is 0
    say(f"  GBM-vs-ABM mean gap over {h}s with zero log-drift: {gbm_mean_gap:.6f} pts = {gbm_mean_gap/TICK:.6f} ticks")

# ---------------------------------------------------------------- E2 touch probability
say("\nE2 Brownian touch probability P(max over [0,t] >= a) = 2(1-Phi(a/(sigma sqrt t)))")
for a_ticks in (1, 2, 4):
    a = a_ticks * TICK
    row = []
    for h in (1, 10, 60):
        p = 2 * (1 - norm.cdf(a / (sig_1s * math.sqrt(h))))
        row.append(f"h={h}s:{p:.3f}")
    say(f"  a={a_ticks} tick(s): " + "  ".join(row))

# ---------------------------------------------------------------- E3 markout arithmetic
say("\nE3 Martingale markout arithmetic for a 1-tick spread")
half = TICK / 2
say(f"  half-spread {half} pts = ${half*TICK_USD/TICK:.3f}; two passive fills (round turn) earn 1 tick = ${TICK_USD:.2f}")
say(f"  round-turn commission ${COMM_RT:.2f}; margin before adverse selection ${TICK_USD-COMM_RT:.2f} per round turn")
for adv_ticks in (0.0, 0.05, 0.1, 0.25):
    net = TICK_USD - COMM_RT - 2 * adv_ticks * TICK_USD
    say(f"  adverse selection {adv_ticks:.2f} tick per fill -> net ${net:+.3f} per round turn")
# fills needed to detect a per-fill edge delta (ticks) over cost, one-sided 5%, power 80%, independent fills
say(f"  cost per fill = commission/2 = ${COMM_RT/2:.3f} = {COMM_RT/2/TICK_USD:.3f} tick; martingale markout vs fill = +0.5 tick")
zsum = norm.ppf(0.95) + norm.ppf(0.80)
for hh in (1, 10, 60):
    sd_t = sig_1s * math.sqrt(hh) / TICK
    ns = [f"delta={d}:{(zsum*sd_t/d)**2:,.0f}" for d in (0.05, 0.1, 0.25)]
    say(f"  h={hh}s per-fill markout sd {sd_t:.2f} ticks; fills needed " + "  ".join(ns))

# ---------------------------------------------------------------- E4 OU exact discretisation and bias
say("\nE4 OU exact AR(1): phi=exp(-kappa h), half-life=ln2/kappa; Kendall/Marriott-Pope bias -(1+3phi)/n")
h = 1.0
for phi, n in ((0.95, 600), (0.999, 600), (0.999, 23400)):
    kappa = -math.log(phi) / h
    hl = math.log(2) / kappa
    bias = -(1 + 3 * phi) / n
    phi_b = phi + bias
    kappa_b = -math.log(phi_b) / h
    say(f"  phi={phi} n={n}: kappa={kappa:.5f}/s half-life={hl:.1f}s; approx E[phi_hat]={phi_b:.5f} -> kappa={kappa_b:.5f}/s"
        f" (x{kappa_b/kappa:.2f}), half-life {math.log(2)/kappa_b:.1f}s")


def mc_ou(phi: float, n: int, reps: int) -> tuple[float, float, float]:
    sig_e = 1.0
    x0 = RNG.normal(0, sig_e / math.sqrt(1 - phi ** 2), size=reps)
    eps = RNG.normal(0, sig_e, size=(reps, n))
    x = np.empty((reps, n + 1))
    x[:, 0] = x0
    for t in range(n):
        x[:, t + 1] = phi * x[:, t] + eps[:, t]
    y, z = x[:, 1:], x[:, :-1]
    zc = z - z.mean(axis=1, keepdims=True)
    yc = y - y.mean(axis=1, keepdims=True)
    ph = (zc * yc).sum(axis=1) / (zc ** 2).sum(axis=1)
    ok = ph > 0
    kap = -np.log(ph[ok])
    return float(ph.mean()), float(np.median(kap)), float(ok.mean())


for phi, n in ((0.95, 600), (0.999, 600)):
    m, kmed, okfrac = mc_ou(phi, n, 4000)
    say(f"  Monte Carlo (4000 reps, unknown mean) phi={phi} n={n}: mean phi_hat={m:.5f} (bias {m-phi:+.5f}; formula {-(1+3*phi)/n:+.5f});"
        f" median kappa_hat={kmed:.5f} vs true {-math.log(phi):.5f}; P(phi_hat>0)={okfrac:.3f}")

# ---------------------------------------------------------------- E5 RV and TSRV under noise
say("\nE5 Realised variance vs TSRV on one synthetic day (efficient ABM, 1s grid)")
n = RTH_SEC
true_iv = sig_d_pts ** 2
x = np.concatenate([[P0], P0 + np.cumsum(RNG.normal(0, sig_1s, n))])
cases = {
    "iid noise sd 0.10 pt": x + RNG.normal(0, 0.10, n + 1),
    "rounded to 0.125 grid (mid of 1-tick book)": np.round(x / (TICK / 2)) * (TICK / 2),
}


def rv(p: np.ndarray, step: int, offset: int = 0) -> float:
    q = p[offset::step]
    return float(np.sum(np.diff(q) ** 2))


def tsrv(p: np.ndarray, K: int) -> float:
    nn = len(p) - 1
    avg = np.mean([rv(p, K, k) for k in range(K)])
    nbar = (nn - K + 1) / K
    return float(avg - (nbar / nn) * rv(p, 1))


say(f"  true integrated variance {true_iv:.1f} pts^2")
for name, y in cases.items():
    zero_frac = float(np.mean(np.diff(y) == 0))
    parts = [f"RV{s}s={rv(y, s):.1f}" for s in (1, 10, 60, 300)]
    K = int(round(n ** (2 / 3)))
    say(f"  {name}: zero 1s returns {zero_frac:.3f}; " + " ".join(parts) + f"; TSRV(K={K})={tsrv(y, K):.1f}")
    say(f"    implied noise var from RV1s/(2n) = {rv(y,1)/(2*n):.5f} pts^2")

# ---------------------------------------------------------------- E6 Lee-Mykland constants
say("\nE6 Lee-Mykland threshold constants (c=sqrt(2/pi))")
c = math.sqrt(2 / math.pi)
beta = -math.log(-math.log(0.99))
for nobs, label in ((23400, "1s, one RTH day"), (390, "1min, one RTH day"), (23400 * 80, "1s, 80 RTH days pooled")):
    L2 = math.sqrt(2 * math.log(nobs))
    Cn = L2 / c - (math.log(math.pi) + math.log(math.log(nobs))) / (2 * c * L2)
    Sn = 1 / (c * L2)
    say(f"  n={nobs} ({label}): Cn={Cn:.3f} Sn={Sn:.4f} critical |L|={Cn + beta*Sn:.2f}")
say(f"  beta*(1%)={beta:.4f}")
for nobs in (23400, 390):
    say(f"  window K range for nobs/day={nobs}: sqrt(252*n)={math.sqrt(252*nobs):.0f} .. 252*n={252*nobs}")
say(f"  naive per-observation 5% test on 23400 1s returns: {0.05*23400:.0f} false flags per day")

# ---------------------------------------------------------------- E7 jump variance share
say("\nE7 Jump share of quadratic variation")
qv = true_iv
for share in (0.01, 0.05, 0.20):
    jv = share * qv / (1 - share)
    for lam in (1.0, 5.0):
        rms = math.sqrt(jv / lam)
        say(f"  share {share:.0%}: jump var {jv:.1f} pts^2/day; lambda={lam}/day -> RMS jump {rms:.2f} pts = {rms/TICK:.1f} ticks")
# Kou moments
p_up, eta1, eta2 = 0.4, 1 / 0.002, 1 / 0.003     # mean up jump 0.2%, mean down 0.3% (log)
ey = p_up / eta1 - (1 - p_up) / eta2
ey2 = 2 * p_up / eta1 ** 2 + 2 * (1 - p_up) / eta2 ** 2
say(f"  Kou p={p_up}, 1/eta1=0.002, 1/eta2=0.003: E[Y]={ey:.5f}, E[Y^2]={ey2:.3e}, RMS={math.sqrt(ey2):.5f} = {math.sqrt(ey2)*P0:.2f} pts at P0")

# ---------------------------------------------------------------- E5b Monte Carlo over synthetic days
say("\nE5b Monte Carlo, 200 synthetic days, 1s grid: mean (sd) of estimator / true IV")
DAYS = 200
ests = {k: {"RV1": [], "RV60": [], "RV300": [], "TSRV60": [], "TSRV300": [], "TSRV818": []} for k in ("iid", "round")}
for _ in range(DAYS):
    xd = np.concatenate([[P0], P0 + np.cumsum(RNG.normal(0, sig_1s, n))])
    iv_d = true_iv
    for key, yd in (("iid", xd + RNG.normal(0, 0.10, n + 1)), ("round", np.round(xd / (TICK / 2)) * (TICK / 2))):
        e = ests[key]
        e["RV1"].append(rv(yd, 1) / iv_d)
        e["RV60"].append(rv(yd, 60) / iv_d)
        e["RV300"].append(rv(yd, 300) / iv_d)
        for K in (60, 300, 818):
            e[f"TSRV{K}"].append(tsrv(yd, K) / iv_d)
for key, e in ests.items():
    say(f"  {key}: " + "  ".join(f"{k}={np.mean(v):.3f}({np.std(v):.3f})" for k, v in e.items()))

OUT.write_text("\n".join(lines) + "\n")
print(f"wrote {OUT} ({len(lines)} lines)")
