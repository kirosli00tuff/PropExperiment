"""REV_G4 independent re-derivation of the C2_StatsRMT.md worked examples (parts A-H).

Written by the G4 reviewer from the designs stated in C2_StatsRMT.md and the equations
verified against the saved sources. Own implementations throughout (the reader's script
was read, not imported). Synthetic data only, own seed; reads no market data.
Run: nice -n 10 uv run python -I REV_G4_statsrmt_check.py
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")
os.nice(10)

import math

import numpy as np
from scipy import stats
from scipy.spatial import cKDTree
from scipy.special import digamma
from sklearn.covariance import LedoitWolf

rng = np.random.default_rng(4242)
G = 0.5772156649
out = []


def p(*a):
    s = " ".join(str(x) for x in a)
    out.append(s)
    print(s, flush=True)


def emax(n, var):
    if n <= 1:
        return 0.0
    return math.sqrt(var) * ((1 - G) * stats.norm.ppf(1 - 1 / n) + G * stats.norm.ppf(1 - 1 / (n * math.e)))


# ------------------------------------------------------------------ A. MP edges
p("## A. MP edges (1 -/+ sqrt q)^2")
for name, N, T in (("laloux", 406, 1309), ("45roots", 45, 1000), ("538trials", 538, 1250), ("book40", 40, 84 * 23400)):
    q = N / T
    p(f"{name}: q={q:.4g} lam-={(1-math.sqrt(q))**2:.4f} lam+={(1+math.sqrt(q))**2:.4f}")
p(f"exact E[max of 200 iid N(0,1)] by quadrature vs BLdP formula: "
  f"{200*np.trapezoid(stats.norm.pdf(x:=np.linspace(-8,8,200001))*stats.norm.cdf(x)**199*x, x):.4f} vs {emax(200,1.0):.4f}")

# ------------------------------------------------------- B. effective trials
p("## B. effective number of trials: 200 null trials, 5 clusters of 40, rho_in 0.6, rho_all 0.1, T=750")
M, T, reps = 200, 750, 300
C = np.full((M, M), 0.1)
for k in range(5):
    C[k * 40:(k + 1) * 40, k * 40:(k + 1) * 40] = 0.6
np.fill_diagonal(C, 1.0)
true_eig = np.sort(np.linalg.eigvalsh(C))[::-1]
p(f"true top eigenvalues: {np.round(true_eig[:6], 3)}  (analytic: 1+39*0.6+160*0.1={1+39*0.6+160*0.1:.1f}, 1+39*0.6-40*0.1={1+39*0.6-40*0.1:.1f})")
L = np.linalg.cholesky(C)
mx, vr, effs = [], [], []
lam_plus = (1 + math.sqrt(M / T)) ** 2
for r in range(reps):
    x = rng.standard_normal((T, M)) @ L.T
    sr = x.mean(0) / x.std(0, ddof=0)
    mx.append(sr.max())
    vr.append(sr.var())
    if r < 20:
        ec = np.corrcoef(x, rowvar=False)
        e = np.linalg.eigvalsh(ec)
        pr = e / e.sum()
        rho_bar = (ec.sum() - M) / (M * (M - 1))
        effs.append((int((e > lam_plus).sum()), math.exp(-(pr * np.log(pr)).sum()),
                     e.sum() ** 2 / (e ** 2).sum(), rho_bar, rho_bar + (1 - rho_bar) * M))
mean_max, mean_var = np.mean(mx), np.mean(vr)
eff = np.mean(np.array(effs), axis=0)
p(f"MC mean max SR = {mean_max:.4f} (reader 0.0849); mean cross-sectional var = {mean_var:.6f}; sqrt = {math.sqrt(mean_var):.4f} (marginal 1/sqrt(T) = {1/math.sqrt(T):.4f})")
p(f"formula N=M=200: {emax(200, mean_var):.4f} (reader 0.0913, +7.6%); here +{100*(emax(200,mean_var)/mean_max-1):.1f}%")
grid = np.arange(1, M + 1)
implied = int(grid[np.argmin([abs(emax(n, mean_var) - mean_max) for n in grid])])
p(f"N implied by MC: {implied} (reader 112)")
p(f"MP edge {lam_plus:.3f}; n above edge {eff[0]:.1f}; entropy eff rank {eff[1]:.1f}; participation {eff[2]:.1f}; rho_bar {eff[3]:.4f}; N_hat {eff[4]:.1f}")
for name, n in (("MP count", eff[0]), ("entropy rank", eff[1]), ("participation", eff[2]), ("N_hat", eff[4])):
    p(f"  E[max] with N={n:.1f}: {emax(n, mean_var):.4f}")
# theoretical cross-sectional variance under correlation: approx (1 - rho_bar)/T
p(f"theory check: (1-rho_bar)/T = {(1-0.198)/T:.6f} vs measured {mean_var:.6f}")

# ------------------------------------------------------- C. cleaning race
p("## C. cleaning race p=100, n=200, population eigs 80x1, 15x3, 5x10, GMV OOS var / oracle")
pp, n, reps = 100, 200, 40
pop = np.concatenate([np.ones(80), 3 * np.ones(15), 10 * np.ones(5)])
Q, _ = np.linalg.qr(rng.standard_normal((pp, pp)))
Sig = (Q * pop) @ Q.T
Lc = np.linalg.cholesky(Sig)
ones = np.ones(pp)
oracle = 1.0 / (ones @ np.linalg.solve(Sig, ones))


def gmv(est):
    w = np.linalg.solve(est, ones)
    w /= w.sum()
    return w @ Sig @ w / oracle


def clip(S, n):
    d = np.sqrt(np.diag(S))
    Cm = S / np.outer(d, d)
    lam, U = np.linalg.eigh(Cm)
    lp = (1 + math.sqrt(len(lam) / n)) ** 2
    noise = lam < lp
    lam2 = lam.copy()
    lam2[noise] = lam[noise].mean()
    return ((U * lam2) @ U.T) * np.outer(d, d)


def rie(S, n):
    lam, U = np.linalg.eigh(S)
    N = len(lam)
    q = N / n
    z = lam - 1j * N ** -0.5
    g = np.mean(1.0 / (z[:, None] - lam[None, :]), axis=1)
    xi = lam / np.abs(1 - q + q * z * g) ** 2
    xi *= lam.sum() / xi.sum()
    return (U * xi) @ U.T


def nls(S, n):
    """Ledoit-Wolf 2020 analytical nonlinear shrinkage (p < n), own implementation of eqs 3.6, 4.5-4.9."""
    lam, U = np.linalg.eigh(S)
    N = len(lam)
    c = N / n
    h = n ** (-1 / 3)
    hj = h * lam[None, :]
    xx = (lam[:, None] - lam[None, :]) / hj
    k = (3 / (4 * math.sqrt(5))) * np.maximum(1 - xx ** 2 / 5, 0)
    f = np.mean(k / hj, axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        Hk = (-3 / (10 * math.pi)) * xx + (3 / (4 * math.sqrt(5) * math.pi)) * (1 - xx ** 2 / 5) * np.log(np.abs((math.sqrt(5) - xx) / (math.sqrt(5) + xx)))
    Hk = np.where(np.isfinite(Hk), Hk, (-3 / (10 * math.pi)) * xx)
    Hf = np.mean(Hk / hj, axis=1)
    d = lam / ((math.pi * c * lam * f) ** 2 + (1 - c - math.pi * c * lam * Hf) ** 2)
    return (U * d) @ U.T


res = {k: [] for k in ("sample", "clip", "lw_linear", "rie", "nls")}
for _ in range(reps):
    x = rng.standard_normal((n, pp)) @ Lc.T
    x -= x.mean(0)
    S = x.T @ x / n
    res["sample"].append(gmv(S))
    res["clip"].append(gmv(clip(S, n)))
    res["lw_linear"].append(gmv(LedoitWolf(assume_centered=True).fit(x).covariance_))
    res["rie"].append(gmv(rie(S, n)))
    res["nls"].append(gmv(nls(S, n)))
for k, v in res.items():
    p(f"{k:10s}: {np.mean(v):.3f} (se {np.std(v)/math.sqrt(reps):.3f})")
p("reader: sample 1.967, clip 1.283, LW 1.228, RIE 1.181, NLS 1.127; theory sample ~ (n-1)/(n-p-1) = %.3f" % ((n - 1) / (n - pp - 1)))

# -------------------------------------------------------- D. JS / EB on Sharpe
p("## D. James-Stein / EB on 12 annualized Sharpe ratios")
z = np.array([1.9, 1.2, 0.8, 0.5, 0.3, 0.1, -0.2, -0.4, -0.6, -0.9, -1.1, -1.5])
K = len(z)
zb = z.mean()
S2 = ((z - zb) ** 2).sum()
p(f"zbar={zb:.4f} S={S2:.3f}")
for T in (84, 1000):
    se2 = 252 / T
    B = min(1.0, (K - 3) * se2 / S2)
    tau2 = max(0.0, S2 / (K - 1) - se2)
    kap = tau2 / (tau2 + se2)
    p(f"T={T}: se^2={se2:.3f} B={B:.4f} JS winner={zb+(1-B)*(z[0]-zb):.4f} | tau2={tau2:.4f} kappa={kap:.4f} EB winner={zb+kap*(z[0]-zb):.4f} | E[max] K=12 = {emax(12, se2):.4f}")
p(f"PhiInv(1-1/12)={stats.norm.ppf(1-1/12):.4f}, PhiInv(1-1/(12e))={stats.norm.ppf(1-1/(12*math.e)):.4f}; (K-1)s^2 at T=84 = {11*3:.0f}")

p("## D2. two-level MoM: 3 families x 4, se 0.08")
fam = np.array([[0.30, 0.22, 0.18, 0.10], [0.05, 0.02, -0.04, -0.08], [-0.10, -0.12, -0.20, -0.25]])
se = 0.08
fm = fam.mean(1)
wss = ((fam - fm[:, None]) ** 2).sum()
tau_w2 = max(0.0, wss / (fam.size - 3) - se ** 2)
se_f = se / 2
tau_b2_gm = max(0.0, fm.var(ddof=1) - se_f ** 2)          # reader: variance about the grand mean
tau_b2_0 = max(0.0, (fm ** 2).mean() - se_f ** 2)           # consistent with prior mean 0
k_gm = tau_b2_gm / (tau_b2_gm + se_f ** 2)
k_0 = tau_b2_0 / (tau_b2_0 + se_f ** 2)
p(f"within SS={wss:.4f}, /9={wss/9:.4f} < se^2={se**2:.4f} -> tau_w2={tau_w2}; family means {np.round(fm,4)}")
p(f"reader's tau_b2 (about grand mean, ddof=1) = {tau_b2_gm:.4f}, kappa_b={k_gm:.3f}, posteriors toward 0: {np.round(k_gm*fm,4)}")
p(f"prior-mean-0 MoM tau_b2 = mean(zbar_i^2)-se_f^2 = {tau_b2_0:.4f}, kappa_b={k_0:.3f}, posteriors: {np.round(k_0*fm,4)}")
p(f"grand-mean-centred posteriors (shrink toward {fm.mean():.4f}): {np.round(fm.mean()+k_gm*(fm-fm.mean()),4)}")

# ------------------------------------------------------------------ E. BMA
p("## E. BIC weights from the reader's BIC values")
bic = np.array([1667.6398, 1664.5710, 1672.1719])
w = np.exp(-0.5 * (bic - bic.min()))
p(f"dBIC={np.round(bic-bic.min(),3)} raw w={np.round(w,4)} sum={w.sum():.4f} weights={np.round(w/w.sum(),3)}; BMA beta = {(w/w.sum())[1]*-0.19449+(w/w.sum())[2]*-0.19450:.4f}")

# -------------------------------------------------------------- F. entropy
p("## F. entropy of the bounce chain")
p3 = np.array([0.1, 0.8, 0.1])
p(f"iid H = {-(p3*np.log2(p3)).sum():.4f} bits; log2 3 = {math.log2(3):.3f}")
P = np.array([[0.05, 0.75, 0.20], [0.10, 0.80, 0.10], [0.20, 0.75, 0.05]])
ev, V = np.linalg.eig(P.T)
pi = np.real(V[:, np.argmin(abs(ev - 1))])
pi /= pi.sum()
h = -(pi[:, None] * P * np.log2(P)).sum()
p(f"stationary {np.round(pi,4)}; marginal H {-(pi*np.log2(pi)).sum():.4f}; rate {h:.4f}; gap {-(pi*np.log2(pi)).sum()-h:.4f}")


def chain(n):
    cum = np.cumsum(P, 1)
    u = rng.random(n)
    s = 1
    o = np.empty(n, dtype=np.int64)
    for t in range(n):
        s = int(np.searchsorted(cum[s], u[t]))
        o[t] = s
    return o


def Hk(sym, k):
    if k == 0:
        return 0.0
    codes = np.zeros(len(sym) - k + 1, dtype=np.int64)
    for j in range(k):
        codes = codes * 3 + sym[j:len(sym) - k + 1 + j]
    _, c = np.unique(codes, return_counts=True)
    pr = c / c.sum()
    return float(-(pr * np.log2(pr)).sum())


def lz(sym):
    s = bytes((sym + 65).astype(np.uint8))
    n = len(s)
    tot = 1
    lam = 1
    for i in range(1, n):
        lam = max(1, lam - 1)
        while i + lam <= n and s.find(s[i:i + lam], 0, i + lam - 1) != -1:
            lam += 1
        tot += lam
    return n * math.log2(n) / tot


for n in (2000, 20000):
    sym = chain(n)
    h4 = Hk(sym, 5) - Hk(sym, 4)
    h8 = Hk(sym, 9) - Hk(sym, 8)
    p(f"n={n}: block rate k=4 {h4:.4f} (bias {h-h4:+.4f}), k=8 {h8:.4f}, LZ {lz(sym):.4f}; MM scale (3^5-1)/(2n ln2)={(3**5-1)/(2*n*math.log(2)):.4f}, (3^5-3^4)/(2n ln2)={(3**5-3**4)/(2*n*math.log(2)):.4f}")
p(f"3^9 = {3**9}")

# SampEn theory for iid Gaussian, m=2, r=0.2 sd: -ln P(|x-y|<r), x-y ~ N(0,2)
p(f"theory SampEn iid Gaussian r=0.2sd: {-math.log(2*stats.norm.cdf(0.2/math.sqrt(2))-1):.4f} (reader measured 2.17-2.19)")

# ------------------------------------------------------------------ G. TE / MI
p("## G. TE null bias and power; Gaussian MI")
nu = 2 * 3 * 2
p(f"nu for k=l=1, alphabet 3: (3-1)*3*(3-1)={nu}; null E[TE] ~ nu/(2n): n=20000 -> {nu/(2*19999):.6f}")
for nu_ in (2, 12):
    crit = stats.chi2.isf(0.05, nu_)
    for te in (1e-4, 1e-3, 1e-2):
        lo, hi = 10, 10 ** 9
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if stats.ncx2.sf(crit, nu_, 2 * mid * te) >= 0.8:
                hi = mid
            else:
                lo = mid
        p(f"  nu={nu_} TE={te}: n for 80% power = {hi}")
p(f"Gaussian MI rho=0.3: {-0.5*math.log(1-0.09):.5f} nats")

# ------------------------------------------------------------------ H. sizing
p("## H. fills needed for a 0.1-tick effect, sd 1.5, two-sided, power 0.8")
for K_ in (1, 12, 50):
    za = stats.norm.ppf(1 - 0.05 / (2 * K_))
    p(f"K={K_}: n = {math.ceil(((za+stats.norm.ppf(0.8))*1.5/0.1)**2)} (z_a={za:.4f})")
p(f"I1 two-sample: 2*(2.8016*1.5/0.1)^2 = {2*((1.96+stats.norm.ppf(0.8))*15)**2:.0f} per tercile")
p(f"cloud: 4*0.89={4*0.89:.2f}, 4*1.79={4*1.79:.2f}, 4*1.99={4*1.99:.2f}")

with open(__file__.replace(".py", "_out.txt"), "w") as fh:
    fh.write("\n".join(out) + "\n")
