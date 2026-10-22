#!/usr/bin/env python3
"""REV_G2 independent re-derivations for C2_Hawkes.md worked examples and formulas.
Prints each check as: label | claimed | recomputed | ok?  (no files written)."""
import math
import numpy as np
from scipy import stats
import sympy as sp

OUT = []


def chk(label, claimed, got, tol=2e-3, rel=True):
    if isinstance(claimed, (int, float)) and isinstance(got, (int, float)):
        err = abs(got - claimed) / (abs(claimed) if rel and claimed != 0 else 1.0)
        ok = err <= tol
        OUT.append(f"{'OK ' if ok else 'BAD'} | {label} | claimed {claimed} | got {got:.6g}")
    else:
        OUT.append(f"    | {label} | claimed {claimed} | got {got}")


# --- Section 1: Poisson fill probabilities, lambda = 2/s, 20 ahead -> need >= 21 arrivals
chk("S1 P(Poisson(20)>=21)", 0.441, stats.poisson.sf(20, 20))
chk("S1 P(Poisson(2)>=21)", 6e-15, stats.poisson.sf(20, 2), tol=0.05)
chk("S1 P(Poisson(120)>=21)", 1.000, stats.poisson.sf(20, 120))
# SE of lambda_hat = sqrt(M)/T from Fisher information M/lambda^2 at lambda=M/T
M, T, lam = sp.symbols("M T lambda", positive=True)
logL = M * sp.log(lam) - lam * T
info = -sp.diff(logL, lam, 2)
se = sp.sqrt(1 / info).subs(lam, M / T)
chk("S1 SE(lambda_hat) = sqrt(M)/T", "sqrt(M)/T", sp.simplify(se))

# --- Section 2: inhomogeneous Poisson example
chk("S2 P(no event | mean 6)", 0.0025, math.exp(-6), tol=0.01)
chk("S2 P(no event | mean 2)", 0.135, math.exp(-2), tol=0.01)
chk("S2 P(Poisson(6)>=4)", 0.849, stats.poisson.sf(3, 6))
chk("S2 P(Poisson(2)>=4)", 0.143, stats.poisson.sf(3, 2))

# --- Section 3: exponential and power-law kernel integrals, mean rate, cluster size
s_, n_, b_, a_, g_ = sp.symbols("s n beta alpha gamma", positive=True)
chk("S3 int n*beta*exp(-beta s) ds = n", "n", sp.simplify(sp.integrate(n_ * b_ * sp.exp(-b_ * s_), (s_, 0, sp.oo))))
chk("S3 int alpha*beta/(1+beta s)^(1+gamma) ds = alpha/gamma", "alpha/gamma",
    sp.simplify(sp.integrate(a_ * b_ / (1 + b_ * s_) ** (1 + g_), (s_, 0, sp.oo), conds="none")))
chk("S3 half-life ln2/beta (beta=1)", math.log(2), math.log(2))
chk("S3 Lambda = mu/(1-n), mu=0.5 n=0.8", 2.5, 0.5 / 0.2)
chk("S3 cluster size 1/(1-n)", 5, 1 / 0.2)
chk("S3 empirical rate 502398/200000", 2.512, 502398 / 200000)
chk("S3 (5b) mu = Lambda(1-n) = 2*0.3", 0.6, 2 * 0.3)
chk("S3 Fano limit 1/(1-0.7)^2", 11.1, 1 / 0.09, tol=0.01)
chk("S3 measured Fano 60 s 1265/119.5", 10.6, 1265.4476669375 / 119.50575, tol=0.01)
chk("S3 measured Fano 10 s", 7.8, 156.74257993749998 / 19.97225, tol=0.01)


# Exact finite-window variance for exponential Hawkes, to test the simulation numbers:
# Var N(W) = Lambda W + 2 K [W/a - (1 - e^{-aW})/a^2],  a = beta(1-n),  K = Lambda n (2-n) beta / (2 (1-n))
def var_exp_hawkes(Lam, n, beta, W):
    a = beta * (1 - n)
    K = Lam * n * (2 - n) * beta / (2 * (1 - n))
    return Lam * W + 2 * K * (W / a - (1 - math.exp(-a * W)) / a ** 2)


for W, meas in ((1, 4.672046577500001), (10, 156.74257993749998), (60, 1265.4476669375)):
    chk(f"S3 theory Var N({W}s), Lambda=2 n=0.7 beta=1 vs measured", round(meas, 2), var_exp_hawkes(2, 0.7, 1, W), tol=0.03)
for W, meas in ((10, 380.91992399), (100, 6481.038399), (1000, 59795.189900000005)):
    chk(f"S7 theory Var N({W}s), Lambda=2.5 n=0.8 beta=1 vs measured", round(meas, 1), var_exp_hawkes(2.5, 0.8, 1, W), tol=0.10)

# --- Section 4: bivariate eigenvalues, mean rates, Psi, signature plot
A = np.array([[0.5, 0.2], [0.2, 0.5]])
ev = np.linalg.eigvals(A)
chk("S4 eigenvalues of [[.5,.2],[.2,.5]] = 0.7, 0.3", "0.7,0.3", f"{sorted(ev.real, reverse=True)}")
Lam = np.linalg.solve(np.eye(2) - A, np.array([0.3, 0.3]))
chk("S4 Lambda = (I-A)^-1 (0.3,0.3)", 1.0, float(Lam[0]))
inv = np.linalg.inv(np.eye(2) - A)
chk("S4 (I-A)^-1 [0,0]", 2.381, float(inv[0, 0]))
chk("S4 (I-A)^-1 [0,1]", 0.952, float(inv[0, 1]))
chk("S4 Psi_11 = 1.381", 1.381, float(inv[0, 0] - 1))
chk("S4 params D + D^2 + 1 at D=4", 21, 4 + 16 + 1)

mu, nrm, b = 0.2, 0.6, 2.0
a = nrm * b
gam = a + b
Lam_sig = 2 * mu / (1 - nrm)
kap = 1 / (1 + nrm)


def C(tau):
    return Lam_sig * (kap ** 2 + (1 - kap ** 2) * (1 - math.exp(-gam * tau)) / (gam * tau))


chk("S4 signature a = 1.2", 1.2, a)
chk("S4 signature gamma = 3.2", 3.2, gam)
chk("S4 signature Lambda = 1.0", 1.0, Lam_sig)
chk("S4 signature kappa = 0.625", 0.625, kap)
chk("S4 C(inf) = 0.391", 0.391, Lam_sig * kap ** 2)
chk("S4 C(1 s) = 0.573", 0.573, C(1.0))
chk("S4 C(0.1 s) = 0.912", 0.912, C(0.1))
chk("S4 C(10 s) = 0.410", 0.410, C(10.0))
chk("S4 C(60 s) = 0.394", 0.394, C(60.0))
chk("S4 1/gamma = 0.3 s", 0.3, 1 / gam, tol=0.05)

# Independent check of C(inf) = Lambda kappa^2 from the long-run covariance of a bivariate Hawkes
# with cross-excitation only: Sigma = (I-G)^-1 diag(lam) (I-G)^-T, lam_i = mu/(1-n), G = [[0,n],[n,0]].
G = np.array([[0, nrm], [nrm, 0]])
lam_i = mu / (1 - nrm)
Minv = np.linalg.inv(np.eye(2) - G)
Sig = Minv @ np.diag([lam_i, lam_i]) @ Minv.T
var_diff = Sig[0, 0] + Sig[1, 1] - 2 * Sig[0, 1]
chk("S4 long-run Var(N1-N2)/T equals Lambda kappa^2", Lam_sig * kap ** 2, float(var_diff))
# Relaxation rate of the antisymmetric mode = b (1 - (-n)) = b + a
chk("S4 gamma = b(1+n) = a + b", gam, b * (1 + nrm))

# --- Section 4 (7): compute extrapolation
chk("S4 2200 evals x 2.95 s in hours", 1.8, 2200 * 2.95 / 3600, tol=0.02)
chk("S4 16 B x 1e8 events = 1.6 GB", 1.6, 16 * 1e8 / 1e9)
chk("S4 10 h x $1.29", 12.9, 12.9)

# --- Section 5: hand example of the O(N) recursion
t = [0.5, 1.0, 1.2, 3.0]
mu5, n5, beta5, T5 = 0.5, 0.6, 2.0, 4.0
Avals = [0.0]
for i in range(1, 4):
    Avals.append(math.exp(-beta5 * (t[i] - t[i - 1])) * (1 + Avals[-1]))
lams = [mu5 + n5 * beta5 * Ai for Ai in Avals]
chk("S5 A_2", 0.3679, Avals[1])
chk("S5 A_3", 0.9169, Avals[2])
chk("S5 A_4", 0.0524, Avals[3], tol=0.01)
chk("S5 lambda_2", 0.9415, lams[1])
chk("S5 lambda_3", 1.6003, lams[2])
chk("S5 lambda_4", 0.5629, lams[3])
sumlog = sum(math.log(l) for l in lams)
chk("S5 sum log lambda", -0.8579, sumlog)
kern = [n5 * (1 - math.exp(-beta5 * (T5 - ti))) for ti in t]
chk("S5 kernel compensator terms sum", 2.3146, sum(kern))
comp = mu5 * T5 + sum(kern)
chk("S5 compensator", 4.3145, comp)
chk("S5 log L", -5.1724, sumlog - comp)
# naive double sum check
naive = 0.0
for i in range(4):
    Ai = sum(math.exp(-beta5 * (t[i] - t[j])) for j in range(i))
    naive += math.log(mu5 + n5 * beta5 * Ai)
chk("S5 naive == recursion (sum log)", sumlog, naive, tol=1e-12)
chk("S5 code loglik -5.172567", -5.172567, sumlog - comp, tol=1e-5)

# --- Section 6: rescaled increments and KS band
B = [1 + Ai for Ai in Avals]
D = [t[0]] + [t[i] - t[i - 1] for i in range(1, 4)]
taus = [mu5 * D[0]] + [mu5 * D[k] + n5 * B[k - 1] * (1 - math.exp(-beta5 * D[k])) for k in range(1, 4)]
for k, (cl, got) in enumerate(zip([0.25, 0.6293, 0.3706, 2.0187], taus), 1):
    chk(f"S6 tau_{k}", cl, got)
z = [1 - math.exp(-x) for x in taus]
for k, (cl, got) in enumerate(zip([0.221, 0.467, 0.310, 0.867], z), 1):
    chk(f"S6 z_{k}", cl, got, tol=0.01)
# tau_k by direct integration of the intensity must equal the closed form
tt = sp.symbols("tt", positive=True)
for k in range(1, 4):
    lam_expr = mu5 + sum(n5 * beta5 * sp.exp(-beta5 * (tt - tj)) for tj in t[:k])
    direct = float(sp.integrate(lam_expr, (tt, t[k - 1], t[k])))
    chk(f"S6 tau_{k + 1} direct integral == closed form", taus[k], direct, tol=1e-9)
chk("S6 KS band 1.36/sqrt(4)", 0.68, 1.36 / 2)
# Engle-Russell: Var((X-1)^2) for X~Exp(1) equals 8
X = sp.symbols("X", positive=True)
pdf = sp.exp(-X)
m4 = sp.integrate((X - 1) ** 4 * pdf, (X, 0, sp.oo))
m2 = sp.integrate((X - 1) ** 2 * pdf, (X, 0, sp.oo))
chk("S6 Engle-Russell Var((X-1)^2) = 8", 8, float(m4 - m2 ** 2))
# spurious fit: implied mean rate mu/(1-n) vs observed 30335/20000
chk("S6 spurious fit implied rate mu/(1-n)", 30335 / 20000, 0.06656947054739133 / (1 - 0.956239070790222), tol=0.01)

# --- Section 7 (f): moment estimator
for W, mean, var, cl in ((10, 25.1199, 380.91992399, 0.743), (100, 251.199, 6481.038399, 0.803), (1000, 2511.99, 59795.1899, 0.795)):
    chk(f"S7 n_hat W={W}", cl, 1 - math.sqrt(mean / var))
# theory for the finite-window estimator at W=10 and 100 (exponential kernel)
for W in (10, 100, 1000):
    v = var_exp_hawkes(2.5, 0.8, 1, W)
    OUT.append(f"    | S7 theory n_hat W={W} (exp kernel) | {1 - math.sqrt(2.5 * W / v):.4f}")

# --- Section 8 (5)
chk("S8 n=0.95 rate", 10, 0.5 / 0.05)

# --- Section 9a: conditional mean intensity
chk("S9a Lambda = 0.5/0.4", 1.25, 0.5 / 0.4)
chk("S9a decay rate (1-n)beta", 0.8, 0.4 * 2)
chk("S9a E lambda after 1 s", 2.49, 1.25 + 2.75 * math.exp(-0.8), tol=0.01)
chk("S9a E lambda after 5 s", 1.30, 1.25 + 2.75 * math.exp(-4), tol=0.01)
chk("S9a expected events next 1 s", 3.14, 1.25 + 2.75 * (1 - math.exp(-0.8)) / 0.8, tol=0.01)
# ODE check: d E[lambda]/dt = -beta(E lambda - mu) + n beta E lambda  ->  rate beta(1-n), fixed point mu/(1-n)
El = sp.Function("El")
tsym = sp.symbols("t")
beta_s, n_s, mu_s = sp.symbols("beta n mu", positive=True)
ode = sp.Eq(El(tsym).diff(tsym), -beta_s * (El(tsym) - mu_s) + n_s * beta_s * El(tsym))
sol = sp.dsolve(ode, El(tsym))
OUT.append(f"    | S9a ODE solution | {sp.simplify(sol.rhs)}")

# --- Section 9b (7)
chk("S9b 30 vCPU x 24 h x $1.29", 31, 24 * 1.29, tol=0.01)

# --- Section 9c
chk("S9c two-type Poisson rates 1,2 accuracy", 2 / 3, 2 / 3)

# --- Section 11: sample size
for zc, cl in ((1.96, 1570), (3.0, 2952)):
    chk(f"S11 n per group z={zc}", cl, 2 * (zc + 0.8416) ** 2 / 0.1 ** 2, tol=0.001)
chk("S11 z_0.8", 0.8416, stats.norm.ppf(0.8), tol=1e-3)
# configuration count from the section 11 table
mins = {"H0": 0, "H1": 1, "H2": 3, "H3": 1, "H4": 1, "H5": 2}
maxs = {"H0": 0, "H1": 1, "H2": 6, "H3": 3, "H4": 1, "H5": 2}
OUT.append(f"    | S11 configs if ALL six are run | min {sum(mins.values())} max {sum(maxs.values())} (text says 7 to 12)")
OUT.append(f"    | S11 configs without H-C2-4 | min {sum(mins.values()) - 1} max {sum(maxs.values()) - 1}")

# --- C3 arithmetic on MES fees (C2_SDE 7.1 as quoted by C3)
chk("C3 1 tick $1.25 - $1.22 commission", 0.03, 1.25 - 1.22, tol=1e-9)
chk("C3 $0.03 per RT = 0.012 tick per fill", 0.012, (0.03 / 2) / 1.25, tol=0.01)
chk("C3 adverse 0.05 tick per fill -> net", -0.095, 0.03 - 2 * 0.05 * 1.25, tol=1e-9)

# --- C4 N arithmetic
OUT.append(f"    | C4 N = 538 + 20..40 | OFI 5..11 + Hawkes 7..12 (or 8..13) + ladder 5 rungs x 2 horizons = 10 -> {5 + 7 + 10}..{11 + 12 + 10} (or {5 + 8 + 10}..{11 + 13 + 10})")

print("\n".join(OUT))
bad = [o for o in OUT if o.startswith("BAD")]
print(f"\n{len([o for o in OUT if o.startswith('OK ')])} OK, {len(bad)} BAD")
