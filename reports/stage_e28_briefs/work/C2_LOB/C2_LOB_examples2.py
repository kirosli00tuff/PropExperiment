"""Worked examples for C2_LOB sections 3-7 (numbers from cited papers or labelled hypothetical)."""
import math, time
import numpy as np
# --- QR estimator arithmetic (hypothetical counts) ---
n_ev, mean_dt, nL, nC, nM = 2000, 0.25, 900, 700, 400
Lam = 1 / mean_dt
print("QR: Lambda=%.2f/s lamL=%.2f lamC=%.2f lamM=%.2f" % (Lam, Lam*nL/n_ev, Lam*nC/n_ev, Lam*nM/n_ev))
q, n0 = 10, 1
print("QR Assumption 4: cancel intensity hitting others = %.3f" % (Lam*nC/n_ev*(q-n0)/q))
# --- Gould-Bonart logistic ---
for name, x0, x1 in [("MSFT", 0.01, 2.49), ("GOOG", 0.03, 0.54)]:
    for I in (0.0, 0.5, 0.9):
        print(f"GB {name} I={I}: p_up={1/(1+math.exp(-(x0+x1*I))):.3f}")
# AUC null SE (Hanley-McNeil style approx for AUC=0.5): sqrt((n1+n2+1)/(12 n1 n2))
for n1 in (500, 5000, 50000):
    print(f"AUC null SE n1=n2={n1}: {math.sqrt((2*n1+1)/(12*n1*n1)):.4f}")
# --- microprice under CdL with symmetric reset: G* = delta*(2*phi-1), phi ~ (2/pi) arctan(n/p)
for n, p in [(300, 100), (100, 100), (150, 50), (60, 240)]:
    phi = 2/math.pi*math.atan(n/p); I_st = n/(n+p)
    print(f"microprice CdL n={n} p={p}: phi={phi:.3f} G*={2*phi-1:+.3f} tick ; weighted-mid adj={I_st-0.5:+.3f} tick")
# --- Moallemi-Yuan Theorem 3 boundary and limits, BAC 8/9/13 (mu=1.65, gamma=0.71 per min, Jbar=0.91 tick, pJ=0.5 assumed)
mu, gam, pJ, Jm = 1.65, 0.71, 0.5, 0.91
a0 = (mu*0.5 + gam*pJ)/(mu*0.5 + gam)
print(f"MY alpha(0)={a0:.3f}, alpha(inf)={pJ}, beta(inf)=Jbar+={pJ*Jm:.3f} tick")
for d0 in (0.8, 0.5):
    print(f"MY delta0={d0}: V(inf)=alpha*delta-beta = {pJ*d0 - pJ*Jm:+.3f} tick")
# Table 3 decomposition check: value = fill prob * (delta0 - AS)
for sym, fp, AS in [("BAC", 0.62, 0.57), ("CSCO", 0.63, 0.68), ("PBR", 0.57, 0.85)]:
    print(f"MY {sym}: with rebate {fp*(0.8-AS):+.3f}; without rebate {fp*(0.5-AS):+.3f} tick")
# MES dollar conversion: 1 tick = $1.25
print("MES: -0.043 tick = $%.4f; -0.5 tick = $%.3f" % (-0.043*1.25, -0.5*1.25))
# --- LMZ generalized gamma survival: S(t) for p>0, AFT scaling example (hypothetical parameters)
from scipy.special import gammainc  # regularized lower incomplete gamma P(a,x)
def gg_surv(t, lam, p, kappa):
    return 1 - gammainc(kappa, (lam*t)**p * kappa)
for kappa, p in [(1, 1), (1, 0.7), (2, 0.5)]:
    print(f"GG kappa={kappa} p={p}: S(10s)={gg_surv(10, 1/30, p, kappa):.3f} S(60s)={gg_surv(60, 1/30, p, kappa):.3f}")
# AFT: T = exp(x'b) T0 ; one tick more aggressive with b=-1.0 scales time by e^-1
print("AFT time scale for x'b=-1: %.3f" % math.exp(-1))
# Kaplan-Meier toy (fill=event, cancel/horizon=censored)
times = [3, 5, 5, 8, 12, 15, 20, 30, 45, 60]; event = [1, 1, 0, 1, 1, 0, 1, 0, 1, 0]
S = 1.0; at_risk = len(times)
for t, e in sorted(zip(times, event), key=lambda z: (z[0], -z[1])):
    if e: S *= (at_risk - 1)/at_risk
    at_risk -= 1
    print(f" KM t={t} event={e} S={S:.3f}")
