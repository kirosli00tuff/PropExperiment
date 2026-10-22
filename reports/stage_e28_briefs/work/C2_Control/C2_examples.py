"""C2_Control worked examples. Pure arithmetic on assumed parameters; reads no market data."""
import math
import numpy as np
from scipy.linalg import expm

def as_quotes(s, q, gamma, sigma, k, tau):
    r = s - q * gamma * sigma**2 * tau
    spread = gamma * sigma**2 * tau + (2 / gamma) * math.log(1 + gamma / k)
    return r, spread, r - spread / 2, r + spread / 2

print("== 1. A-S paper parameters (s=100,T=1,sigma=2,gamma=0.1,k=1.5,A=140), t=0")
for q in (0, 1, -2):
    r, sp, b, a = as_quotes(100, q, 0.1, 2, 1.5, 1.0)
    print(f"q={q:+d} r={r:.4f} spread={sp:.4f} bid={b:.4f} ask={a:.4f}")
print("spread terms: gamma*sigma^2*tau=%.4f ; (2/g)ln(1+g/k)=%.4f" % (0.1*4*1, 20*math.log(1+0.1/1.5)))

print("== 2. MES-like illustration (ticks, seconds): sigma=1.0 tick/sqrt(s), k=1.5 /tick, A=0.5 /s, gamma=0.01 /tick, tau=600 s")
sig, k, A, g, tau = 1.0, 1.5, 0.5, 0.01, 600
for q in (0, 1, -1):
    r, sp, b, a = as_quotes(0.0, q, g, sig, k, tau)
    print(f"q={q:+d} r-s={r:.3f} spread={sp:.3f} delta_b={-b:.3f} delta_a={a:.3f}")
print("1/k=%.4f  (1/g)ln(1+g/k)=%.4f" % (1/k, (1/g)*math.log(1+g/k)))

def glft_exact(A, k, gamma, sigma, Q, tau):
    alpha = k / 2 * gamma * sigma**2
    eta = A * (1 + gamma / k) ** (-(1 + k / gamma))
    n = 2 * Q + 1
    M = np.zeros((n, n))
    for i, q in enumerate(range(-Q, Q + 1)):
        M[i, i] = alpha * q * q
        if i > 0: M[i, i - 1] = -eta
        if i < n - 1: M[i, i + 1] = -eta
    v = expm(-M * tau) @ np.ones(n)
    out = {}
    for i, q in enumerate(range(-Q, Q + 1)):
        db = (1/k) * math.log(v[i] / v[i + 1]) + (1/gamma) * math.log(1 + gamma/k) if q < Q else float('nan')
        da = (1/k) * math.log(v[i] / v[i - 1]) + (1/gamma) * math.log(1 + gamma/k) if q > -Q else float('nan')
        out[q] = (db, da)
    return alpha, eta, out

def glft_approx(A, k, gamma, sigma, q):
    c1 = (1/gamma) * math.log(1 + gamma/k)
    c2 = math.sqrt(sigma**2 * gamma / (2*k*A) * (1 + gamma/k) ** (1 + k/gamma))
    return c1 + (2*q + 1)/2 * c2, c1 - (2*q - 1)/2 * c2, c1, c2

print("== 3. GLFT paper Fig.1 params: sigma=0.3 tick/sqrt(s), A=0.9/s, k=0.3/tick, gamma=0.01/tick, T=600 s, Q=10 (paper does not state Q in caption read)")
al, et, ex = glft_exact(0.9, 0.3, 0.01, 0.3, 10, 600)
print(f"alpha={al:.6f} eta={et:.6f}")
for q in (0, 1, 5):
    db, da = ex[q]; ab, aa, c1, c2 = glft_approx(0.9, 0.3, 0.01, 0.3, q)
    print(f"q={q} exact(t=0) db={db:.3f} da={da:.3f} | approx db={ab:.3f} da={aa:.3f} c1={c1:.3f} c2={c2:.3f}")

print("== 4. GLFT with MES-like params, 1-lot limit Q=1 and Q=3, tau=600 s")
for Q in (1, 3):
    al, et, ex = glft_exact(A, k, g, sig, Q, tau)
    s = " ".join(f"q={q:+d}:(db={ex[q][0]:.3f},da={ex[q][1]:.3f})" for q in range(-Q, Q+1))
    print(f"Q={Q} alpha={al:.5f} eta={et:.5f} {s}")
ab, aa, c1, c2 = glft_approx(A, k, g, sig, 0)
print(f"approx q=0: db={ab:.3f} da={aa:.3f} c1={c1:.3f} c2={c2:.3f}; half-spread at touch on 1-tick book = 0.5")

print("== 5. Fee arithmetic (program table rules/products.py: MES 1.25 $/tick, RT 1.22 $; ES 12.50 $/tick, RT 3.78 $)")
for name, tv, rt in (("MES", 1.25, 1.22), ("ES", 12.50, 3.78)):
    half = 0.5 * tv; side = rt / 2
    print(f"{name}: half-spread ${half:.3f}, fee/side ${side:.3f}, net per fill before markout ${half-side:.3f} = {(half-side)/tv:.4f} tick; RT fee/tick = {rt/tv:.3f}")

print("== 6. Calibration of A,k from toy counts over T=3600 s")
d = np.array([0.5, 1.5, 2.5, 3.5]); N = np.array([1800, 400, 90, 20]); T = 3600.0
lam = N / T; se = np.sqrt(N) / T
w = N.astype(float)  # weights ~ 1/var(log lam) = N
X = np.vstack([np.ones_like(d), -d]).T
W = np.diag(w)
beta = np.linalg.solve(X.T @ W @ X, X.T @ W @ np.log(lam))
cov = np.linalg.inv(X.T @ W @ X)
print("lambda:", np.round(lam, 5), "se:", np.round(se, 5))
print(f"WLS logA={beta[0]:.4f} A={math.exp(beta[0]):.4f}/s k={beta[1]:.4f}/tick se(k)={math.sqrt(cov[1,1]):.4f}")
b_ols = np.polyfit(d, np.log(lam), 1)
print(f"OLS slope={b_ols[0]:.4f} -> k={-b_ols[0]:.4f}, A={math.exp(b_ols[1]):.4f}")

print("== 7. Sample size for mean net markout test, t>3 target")
for sd in (1.0, 2.0, 3.2):
    for edge in (0.02, 0.05, 0.10):
        n = (3 * sd / edge) ** 2
        print(f"sd={sd} tick, edge={edge} tick -> n={n:,.0f} fills")

print("== 8. Almgren-Chriss example (ticks, seconds)")
for lam_ra, sigma_ac, eta in ((0.1, 1.0, 0.05), (1e-4, 1.0, 0.05), (1e-4, 1.0, 5.0)):
    kap = math.sqrt(lam_ra * sigma_ac**2 / eta)
    print(f"lambda={lam_ra} sigma={sigma_ac} eta={eta} -> kappa={kap:.4f}/s half-life theta={1/kap:.2f}s")
X0, Tx, Nn = 20, 60.0, 6
lam_ra, sigma_ac, eta = 1e-3, 1.0, 5.0
tau_s = Tx / Nn
kt2 = lam_ra * sigma_ac**2 / eta
kap = math.acosh(1 + kt2 * tau_s**2 / 2) / tau_s
xs = [X0 * math.sinh(kap * (Tx - j * tau_s)) / math.sinh(kap * Tx) for j in range(Nn + 1)]
print(f"X={X0}, T={Tx}s, N={Nn}, lambda={lam_ra}, eta={eta}: kappa={kap:.4f}; holdings:", [round(x, 2) for x in xs])
print("trades:", [round(xs[j-1]-xs[j], 2) for j in range(1, Nn+1)])
