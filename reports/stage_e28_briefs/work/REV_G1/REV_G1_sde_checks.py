"""REV_G1 independent re-derivations for C2_SDE.md. Synthetic numbers only.

Run: python3 -I REV_G1_sde_checks.py  (writes REV_G1_sde_checks_out.txt beside it)
"""
import math
import os
from pathlib import Path

import numpy as np
import sympy as sp
from scipy.stats import norm

os.nice(10)
OUT = Path(__file__).with_name("REV_G1_sde_checks_out.txt")
L: list[str] = []


def say(s: str = "") -> None:
    L.append(s)


TICK, TICK_USD, COMM = 0.25, 1.25, 1.22
P0, VOL, RTH = 5000.0, 0.15, 23400

# ---- S0: volatility ladder
sd_day_pts = P0 * VOL / math.sqrt(252)
sig1 = sd_day_pts / math.sqrt(RTH)
say(f"S0 daily sd {sd_day_pts:.3f} pts; per-sqrt-second {sig1:.4f} pts = {sig1/TICK:.4f} ticks; "
    f"10s {sig1*math.sqrt(10):.3f} pts ({sig1*math.sqrt(10)/TICK:.2f} t); 60s {sig1*math.sqrt(60):.3f} pts ({sig1*math.sqrt(60)/TICK:.2f} t)")

# ---- S1: Ito on log S (sympy) and the GBM mean gap
t, x, mu, sg = sp.symbols("t x mu sigma", positive=True)
f = sp.log(x)
drift = sp.simplify(mu * x * sp.diff(f, x) + sp.Rational(1, 2) * (sg * x) ** 2 * sp.diff(f, x, 2))
say(f"S1 Ito drift of log S for GBM: {drift}  (expect mu - sigma^2/2)")
s2_sec = (VOL / math.sqrt(252)) ** 2 / RTH
for h in (60, 3600):
    gap = P0 * (math.exp(0.5 * s2_sec * h) - 1)
    say(f"   GBM mean gap zero log-drift h={h}s: {gap:.6f} pts = {gap/TICK:.5f} ticks")

# ---- S2: Roll autocovariance (exact, symbolic over the 8 sign patterns) and eta example
s = sp.symbols("s", positive=True)
cov = 0
for q0 in (-1, 1):
    for q1 in (-1, 1):
        for q2 in (-1, 1):
            cov += sp.Rational(1, 8) * (s / 2) ** 2 * (q2 - q1) * (q1 - q0)
say(f"S2 Roll Cov(dp_t, dp_t-1) = {sp.simplify(cov)}; with s=0.25: {float(cov.subs(s, 0.25)):.5f} pts^2")
eta = 1200 / (2 * 2800)
say(f"   eta_hat={eta:.4f}; implicit spread {2*eta*TICK:.4f} pts = {2*eta:.3f} tick; "
    f"X_hat after up-tick to 5000.25: {5000.25-(0.5-eta)*TICK:.4f} ({(0.5-eta):.3f} tick below)")

# ---- S3: Kou moments and jump arithmetic
p, e1, e2 = 0.4, 1 / 0.002, 1 / 0.003
EY = p / e1 - (1 - p) / e2
EY2 = 2 * p / e1**2 + 2 * (1 - p) / e2**2
say(f"S3 Kou E[Y]={EY:.5f} E[Y^2]={EY2:.3e} RMS={math.sqrt(EY2):.5f} -> {math.sqrt(EY2)*P0:.2f} pts")
iv = sd_day_pts**2
for share in (0.01, 0.20):
    jv_total = share * iv                 # if 2232 is TOTAL QV
    jv_cont = share * iv / (1 - share)    # if 2232 is the CONTINUOUS part (reader's script)
    say(f"   share {share:.0%}: jump var {jv_total:.2f} (2232=total) or {jv_cont:.2f} (2232=continuous); "
        f"RMS lambda=1: {math.sqrt(jv_total):.3f} / {math.sqrt(jv_cont):.3f} pts; lambda=5: {math.sqrt(jv_cont/5):.3f} pts")
say(f"   19 ticks x $1.25 = ${19*1.25:.2f}; / $0.03 margin = {19*1.25/0.03:.0f} round turns")

# ---- S4: Lee-Mykland constants, K, and LM12-type check of the reader's E6
c = math.sqrt(2 / math.pi)
beta = -math.log(-math.log(0.99))
for n in (23400, 390, 23400 * 80):
    l2 = math.sqrt(2 * math.log(n))
    Cn = l2 / c - (math.log(math.pi) + math.log(math.log(n))) / (2 * c * l2)
    Sn = 1 / (c * l2)
    say(f"S4 n={n}: Cn={Cn:.4f} Sn={Sn:.4f} crit={Cn+beta*Sn:.3f}")
say(f"   beta*={beta:.4f}; K_min(23400/day)={math.sqrt(252*23400):.1f}; mu1^2={2/math.pi:.4f}; "
    f"vartheta={math.pi**2/4+math.pi-5:.4f}; 5% x 23400 = {0.05*23400:.0f}")

# ---- S5: OU: sympy check of the e^{kt}x trick, exact step variance, bias algebra, MC with a new seed
k, m, h = sp.symbols("kappa mu h", positive=True)
# d(e^{kt} x) = k e^{kt} x dt + e^{kt} dx = k e^{kt} x dt + e^{kt}(k(mu-x)dt + sg dB) = k mu e^{kt} dt + sg e^{kt} dB
xx = sp.Function("x")(t)
lhs = sp.diff(sp.exp(k * t) * xx, t) - sp.exp(k * t) * sp.diff(xx, t)   # the x-dependent dt part
say(f"S5 d(e^kt x) dt-part minus e^kt dx = {sp.simplify(lhs)} (expect kappa e^kt x); "
    f"adding e^kt*kappa(mu-x) gives {sp.simplify(lhs + sp.exp(k*t)*k*(m-xx))}")
var_step = sp.integrate(sg**2 * sp.exp(2 * k * (sp.Symbol('u') - h)), (sp.Symbol('u'), 0, h))
say(f"   Var of one-step stochastic integral = {sp.simplify(var_step)} (expect sigma^2(1-e^-2kh)/(2k))")
phi = sp.symbols("phi", positive=True)
dk = sp.diff(-sp.log(phi) / h, phi)
say(f"   d kappa/d phi = {dk}; Delta kappa for Delta phi = -(1+3phi)/n: {sp.simplify(-dk*(1+3*phi)/sp.Symbol('n'))}")
say(f"   relative bias 4/(kappa T) = 4 HL/(ln2 T) -> factor {4/math.log(2):.3f}; 10% needs T/HL = {4/math.log(2)/0.1:.1f}")
for ph, n in ((0.95, 600), (0.999, 600), (0.999, 23400)):
    kap = -math.log(ph)
    b = -(1 + 3 * ph) / n
    kb = -math.log(ph + b)
    say(f"   phi={ph} n={n}: kappa={kap:.5f} HL={math.log(2)/kap:.1f}s bias_phi={b:.5f} kappa_b={kb:.5f} x{kb/kap:.2f} HL_b={math.log(2)/kb:.1f}s")
say(f"   asymptotic sd sqrt(2 kappa/T) at kappa=0.05, T=2e6: {math.sqrt(2*0.05/2e6):.5f}")
rng = np.random.default_rng(7)


def mc(ph: float, n: int, reps: int) -> tuple[float, float]:
    x0 = rng.normal(0, 1 / math.sqrt(1 - ph**2), reps)
    e = rng.normal(0, 1, (reps, n))
    xs = np.empty((reps, n + 1))
    xs[:, 0] = x0
    for i in range(n):
        xs[:, i + 1] = ph * xs[:, i] + e[:, i]
    y, z = xs[:, 1:], xs[:, :-1]
    zc = z - z.mean(1, keepdims=True)
    yc = y - y.mean(1, keepdims=True)
    phat = (zc * yc).sum(1) / (zc**2).sum(1)
    return float(phat.mean() - ph), float(np.median(-np.log(phat[phat > 0])))


for ph, n in ((0.95, 600), (0.999, 600)):
    bias, kmed = mc(ph, n, 4000)
    say(f"   MC seed 7 phi={ph} n={n}: bias {bias:+.5f} (formula {-(1+3*ph)/n:+.5f}); median kappa_hat {kmed:.5f} (x{kmed/(-math.log(ph)):.2f})")

# ---- S6: TSRV expectation algebra and a new-seed replicate of E5b
nn = RTH
for K in (60, 300, 818):
    nbar = (nn - K + 1) / K
    say(f"S6 K={K}: nbar={nbar:.1f}; E[TSRV]/IV under iid noise = 1 - nbar/n = {1-nbar/nn:.4f}; "
        f"n^(2/3)={nn**(2/3):.1f}")
say(f"   RV1s bias 2nEe2: iid 0.1^2 -> {2*nn*0.01:.0f} ({2*nn*0.01/iv:.3f}); rounding var 0.125^2/12={0.125**2/12:.6f} -> {2*nn*0.125**2/12:.1f} ({2*nn*0.125**2/12/iv:.4f})")
say(f"   noise estimator at 1s: (IV+468)/(2n) = {(iv+468)/(2*nn):.4f}; 0.978/(1-1/60) = {0.978/(1-1/60):.4f}")


def rv(pp: np.ndarray, step: int, off: int = 0) -> float:
    q = pp[off::step]
    return float(np.sum(np.diff(q) ** 2))


def tsrv(pp: np.ndarray, K: int) -> float:
    n_ = len(pp) - 1
    avg = np.mean([rv(pp, K, kk) for kk in range(K)])
    return float(avg - ((n_ - K + 1) / K / n_) * rv(pp, 1))


rng2 = np.random.default_rng(99)
acc = {kk: {"RV1": [], "RV60": [], "TSRV60": [], "TSRV300": [], "TSRV818": []} for kk in ("iid", "round")}
for _ in range(200):
    xd = np.concatenate([[P0], P0 + np.cumsum(rng2.normal(0, sig1, nn))])
    for key, yd in (("iid", xd + rng2.normal(0, 0.10, nn + 1)), ("round", np.round(xd / 0.125) * 0.125)):
        a = acc[key]
        a["RV1"].append(rv(yd, 1) / iv)
        a["RV60"].append(rv(yd, 60) / iv)
        for K in (60, 300, 818):
            a[f"TSRV{K}"].append(tsrv(yd, K) / iv)
for key, a in acc.items():
    say(f"   E5b replicate seed 99 {key}: " + "  ".join(f"{kk}={np.mean(v):.3f}({np.std(v):.3f})" for kk, v in a.items()))

# ---- S7: markout budget, touch probabilities, sample sizes
say(f"S7 margin ${TICK_USD-COMM:.2f}/RT = {(TICK_USD-COMM)/TICK_USD/2:.4f} tick per fill; comm per fill {COMM/2/TICK_USD:.3f} tick")
for adv in (0.05, 0.10, 0.25):
    say(f"   adverse {adv}: net ${TICK_USD-COMM-2*adv*TICK_USD:+.3f}")
for a_t in (1, 2, 4):
    say("   touch a=%d: " % a_t + "  ".join(f"t={hh}:{2*(1-norm.cdf(a_t*TICK/(sig1*math.sqrt(hh)))):.3f}" for hh in (1, 10, 60)))
z = norm.ppf(0.95) + norm.ppf(0.80)
for hh in (1, 10, 60):
    sd_t = sig1 * math.sqrt(hh) / TICK
    say(f"   n fills h={hh}: " + "  ".join(f"d={d}:{(z*sd_t/d)**2:,.0f}" for d in (0.05, 0.10, 0.25)))
say(f"   fills 50..200 x 85 = {50*85:,}..{200*85:,}; 0.25/0.012 = {0.25/0.012:.1f}")

# ---- S8: MBP-10 record size from the docs' field types
hdr = 8 + 8 + 1 + 2 + 4 + 1 + 1 + 1 + 8 + 4 + 1 + 4 + 4
lvl = 10 * (8 + 8 + 4 + 4 + 4 + 4)
say(f"S8 listed fields {hdr} + levels {lvl} = {hdr+lvl}; +1 (DBN hd.length) = {hdr+lvl+1}; "
    f"2e6 recs -> {2e6*368/1e9:.2f} GB; 10e6 -> {10e6*368/1e9:.2f} GB; x85 -> {85*2e6*368/1e9:.0f}..{85*10e6*368/1e9:.0f} GB")

OUT.write_text("\n".join(L) + "\n")
print("\n".join(L))
