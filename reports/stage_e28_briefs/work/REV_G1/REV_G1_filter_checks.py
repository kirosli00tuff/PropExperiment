"""REV_G1 independent re-derivations for C2_Filter.md. Synthetic numbers only.

Run: python3 -I REV_G1_filter_checks.py  (writes REV_G1_filter_checks_out.txt beside it)
"""
import math
import os
from pathlib import Path

import numpy as np
import sympy as sp
from scipy.stats import norm

os.nice(10)
OUT = Path(__file__).with_name("REV_G1_filter_checks_out.txt")
L: list[str] = []


def say(s: str = "") -> None:
    L.append(s)


# ---- F1: local-level steady state (sympy) and the 4-step table
q, r, P = sp.symbols("q r P", positive=True)
sol = sp.solve(sp.Eq(P, P * r / (P + r) + q), P)
say(f"F1 steady-state roots: {sol}")
qv, rv = 0.01, 0.015625
Ps = (qv + math.sqrt(qv**2 + 4 * qv * rv)) / 2
Ks = Ps / (Ps + rv)
hl = math.log(0.5) / math.log(1 - Ks)
say(f"   P={Ps:.6f} K={Ks:.4f} EWMA half-life {hl:.3f} steps; rho1={-rv/(qv+2*rv):.4f}")
x, Pp = 5000.0, 0.02
for t, y in enumerate((5000.25, 5000.25, 5000.00, 5000.50), 1):
    Pprior = Pp + qv
    K = Pprior / (Pprior + rv)
    innov = y - x
    x = x + K * innov
    Pp = (1 - K) * Pprior
    say(f"   t={t} y={y} Pprior={Pprior:.6f} K={K:.5f} innov={innov:+.5f} x={x:.5f} Ppost={Pp:.6f}")
# MA(1) moments of dy under the local level model
say(f"   Var(dy)=q+2r={qv+2*rv:.6f}; Cov1=-r={-rv}; rho1={-rv/(qv+2*rv):.4f}")

# ---- F2: hedge-ratio filter, 3 steps
g, Pg = 2.0, 0.01
for t, (y2, y1) in enumerate(((10.0, 21.0), (10.5, 21.5), (9.8, 19.0)), 1):
    Pprior = Pg + 0.0001
    F = y2**2 * Pprior + 1.0
    K = Pprior * y2 / F
    innov = y1 - g * y2
    g = g + K * innov
    Pg = (1 - K * y2) * Pprior
    say(f"F2 t={t} Pprior={Pprior:.6f} F={F:.5f} K={K:.6f} innov={innov:+.5f} gamma={g:.5f} Ppost={Pg:.6f} z={innov/math.sqrt(F):+.3f}")

# ---- F3: power numbers (two-sample, one-sided z=3.0, power 0.8)
zs = 3.0 + norm.ppf(0.8)
say(f"F3 (z_a+z_b)^2={zs**2:.3f}; 2x={2*zs**2:.2f}")
for d in (0.25, 0.10, 0.5):
    say(f"   d={d}: n per group = {2*zs**2*(1.5/d)**2:,.0f}")
say(f"   paired days: d = {zs}/sqrt(80) s_D = {zs/math.sqrt(80):.3f} s_D; configs 2x2x3={2*2*3}, 2x3x3={2*3*3}")

# ---- F4: unscented transform example
exact = math.exp(1 / 8)
Lam = 1**2 * (1 + 2) - 1
pts = [0.0, math.sqrt((1 + Lam) * 1.0), -math.sqrt((1 + Lam) * 1.0)]
w = [Lam / (1 + Lam), 1 / (2 * (1 + Lam)), 1 / (2 * (1 + Lam))]
ut = sum(wi * math.exp(p / 2) for wi, p in zip(w, pts))
say(f"F4 exact={exact:.6f} EKF=1 (err {1-1/exact:.4%}) lambda={Lam} pts={[round(p,4) for p in pts]} w={[round(a,4) for a in w]} UT={ut:.6f} rel err={abs(ut-exact)/exact:.4%}")

# ---- F5: particle step
a, s = 0.98, 0.15
xs = np.array([-0.4, -0.1, 0.0, 0.2, 0.6])
sh = np.array([0.5, -1.0, 0.2, 1.2, -0.3])
xp = a * xs + s * sh
y = 2.2
wts = np.exp(-0.5 * y**2 / np.exp(xp)) / np.sqrt(2 * np.pi * np.exp(xp))
W = wts / wts.sum()
ess = 1 / np.sum(W**2)
cum = np.cumsum(W)
u = 0.37
picks = [int(np.searchsorted(cum, (u + k) / 5)) + 1 for k in range(5)]
say(f"F5 x'={np.round(xp,3).tolist()} w={np.round(wts,5).tolist()} sum={wts.sum():.5f} W={np.round(W,4).tolist()}")
say(f"   lik inc={wts.mean():.4f} ESS={ess:.3f} cum={np.round(cum,4).tolist()} systematic picks (u=0.37)={picks} "
    f"filtered mean={float(W@xp):.4f} unweighted mean={xp.mean():.4f}")

# ---- F6: Hamilton filter examples (a) and (b), Viterbi, ergodic start
s1, s2, p11, p22 = 0.5, 2.0, 0.99, 0.95
Pm = np.array([[p11, 1 - p11], [1 - p22, p22]])
pi0 = np.array([(1 - p22) / (2 - p11 - p22), (1 - p11) / (2 - p11 - p22)])
say(f"F6 ergodic start {np.round(pi0,5).tolist()}; durations {1/(1-p11):.0f} steps ({10/(1-p11)/60:.1f} min), {1/(1-p22):.0f} steps ({10/(1-p22)/60:.1f} min)")


def dens(yv: float) -> np.ndarray:
    return np.array([norm.pdf(yv, 0, s1), norm.pdf(yv, 0, s2)])


def hfilter(obs: list[float]) -> list[np.ndarray]:
    xi = pi0.copy()
    out = []
    for t, yv in enumerate(obs, 1):
        pred = Pm.T @ xi if t > 1 else xi      # start distribution is the t=1 predicted
        eta = dens(yv)
        f = float(pred @ eta)
        xi = pred * eta / f
        out.append(xi.copy())
        say(f"   t={t} y={yv} pred={np.round(pred,5).tolist()} eta={np.round(eta,5).tolist()} f={f:.5f} filt={np.round(xi,5).tolist()}")
    return out


say("   example (a):")
hfilter([0.0, 2.0, 1.0, 0.0])


def viterbi(obs: list[float]) -> list[str]:
    lp = np.log(Pm)
    v = np.log(pi0) + np.log(dens(obs[0]))
    back = []
    for yv in obs[1:]:
        cand = v[:, None] + lp
        bp = cand.argmax(0)
        v = cand.max(0) + np.log(dens(yv))
        back.append(bp)
    path = [int(v.argmax())]
    for bp in reversed(back):
        path.append(int(bp[path[-1]]))
    return ["calm" if k == 0 else "turb" for k in reversed(path)]


say("   example (b), 4 obs:")
f4 = hfilter([0.0, 0.25, 1.5, 0.25])
say(f"   filtered turbulent: {[round(float(z[1]),3) for z in f4]}; Viterbi: {viterbi([0.0, 0.25, 1.5, 0.25])}")
say("   example (b), 6 obs:")
f6 = hfilter([0.0, 0.25, 1.5, 0.25, 2.5, 3.0])
say(f"   filtered turbulent: {[round(float(z[1]),4) for z in f6]}; Viterbi: {viterbi([0.0, 0.25, 1.5, 0.25, 2.5, 3.0])}")

# ---- F7: compute scaling arithmetic
say(f"F7 1.87M steps x 5.39 s/100k = {1.872e6/1e5*5.39:.0f} s; 1e4 iter x 100 s = {1e4*100/86400:.1f} days; "
    f"S-J rate: 187,200/70,500 = {187200/70500:.2f} -> {12*187200/70500:.0f}-{25*187200/70500:.0f} min; "
    f"27.3 s x 1.872e6/2e5 = {27.3*1.872e6/2e5/60:.1f} min; 80x2340={80*2340:,}; 80x23400={80*23400:,}")

OUT.write_text("\n".join(L) + "\n")
print("\n".join(L))
