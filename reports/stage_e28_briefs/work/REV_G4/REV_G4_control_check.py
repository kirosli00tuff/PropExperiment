"""REV_G4 independent re-derivation of the C2_Control.md worked examples.

Written by the G4 reviewer from the equations as verified against the saved sources
(A-S 2006 draft eqs 2.6-2.7, 3.17-3.18; GLFT 2013 Prop. 1-2, Thm 1, asymptotic display;
Almgren-Chriss 2000 discrete solution). Does not import the reader's script.
Pure arithmetic on the reader's assumed parameters; reads no market data.
"""
import math

import numpy as np
from scipy.linalg import expm
from scipy.optimize import brentq

out = []


def p(*a):
    s = " ".join(str(x) for x in a)
    out.append(s)
    print(s)


# ---------------------------------------------------------------- A-S section 3.5
p("## A-S 3.5(a): s=100, T=1, sigma=2, gamma=0.1, k=1.5, t=0")
g, sig, k, tau = 0.1, 2.0, 1.5, 1.0
inv = g * sig**2 * tau
const = (2 / g) * math.log(1 + g / k)
p(f"inventory term {inv:.4f}, constant term {const:.5f}, spread {inv+const:.5f}")
for q in (0, 1):
    r = 100 - q * inv
    p(f"q={q}: r={r:.4f} bid={r-(inv+const)/2:.4f} ask={r+(inv+const)/2:.4f}")
p(f"Table spreads: gamma=0.01 -> {200*math.log(1+0.01/1.5):.4f}; gamma=0.5 -> {4*math.log(1+0.5/1.5):.4f}")

p("## A-S 3.5(b): sigma=1, k=1.5, gamma=0.01, tau=600 (ticks)")
g, sig, k, tau = 0.01, 1.0, 1.5, 600.0
inv = g * sig**2 * tau
const = (2 / g) * math.log(1 + g / k)
p(f"inventory {inv:.3f}, constant {const:.4f}, spread {inv+const:.3f}; q=+1 delta_a = {-inv + (inv+const)/2:.4f}")

p("## A-S 3.6 sample size: sd = sigma*sqrt(10), edge 0.25, t=3")
sd_exact = math.sqrt(10)
p(f"sd exact {sd_exact:.4f}: n = {(3*sd_exact/0.25)**2:.1f};  sd rounded 3.2: n = {(3*3.2/0.25)**2:.1f}")


# ---------------------------------------------------------------- GLFT section 4.5
def glft_exact(A, k, gamma, sigma, Q, tau):
    alpha = (k / 2) * gamma * sigma**2
    eta = A * (1 + gamma / k) ** (-(1 + k / gamma))
    n = 2 * Q + 1
    M = np.diag([alpha * q * q for q in range(-Q, Q + 1)]).astype(float)
    for i in range(n - 1):
        M[i, i + 1] = -eta
        M[i + 1, i] = -eta
    v = expm(-M * tau) @ np.ones(n)
    c = (1 / gamma) * math.log(1 + gamma / k)
    quotes = {}
    for i, q in enumerate(range(-Q, Q + 1)):
        db = (1 / k) * math.log(v[i] / v[i + 1]) + c if q < Q else float("nan")
        da = (1 / k) * math.log(v[i] / v[i - 1]) + c if q > -Q else float("nan")
        quotes[q] = (db, da)
    return alpha, eta, quotes


def glft_approx(A, k, gamma, sigma, q):
    c1 = (1 / gamma) * math.log(1 + gamma / k)
    root = math.sqrt(sigma**2 * gamma / (2 * k * A) * (1 + gamma / k) ** (1 + k / gamma))
    return c1 + (2 * q + 1) / 2 * root, c1 - (2 * q - 1) / 2 * root, c1, root


p("## GLFT 4.5(a): sigma=0.3, A=0.9, k=0.3, gamma=0.01, T=600, Q=10")
al, et, ex = glft_exact(0.9, 0.3, 0.01, 0.3, 10, 600)
p(f"alpha={al:.6f} eta={et:.5f} (reader: 0.000135, 0.3257)")
for q in (0, 5):
    ab, aa, c1, root = glft_approx(0.9, 0.3, 0.01, 0.3, q)
    p(f"q={q}: exact db={ex[q][0]:.3f} da={ex[q][1]:.3f}; approx db={ab:.3f} da={aa:.3f}; c1={c1:.3f} root={root:.4f}")
# sensitivity of the 'exact' numbers to the assumed Q
for Q in (5, 10, 20, 30):
    _, _, exq = glft_exact(0.9, 0.3, 0.01, 0.3, Q, 600)
    p(f"  Q={Q}: exact q=0 db={exq[0][0]:.3f}; q=5 (db,da)=({exq[5][0]:.3f},{exq[5][1]:.3f})")

p("## GLFT 4.5(b): sigma=1, A=0.5, k=1.5, gamma=0.01, T=600")
for Q in (1, 3):
    al, et, ex = glft_exact(0.5, 1.5, 0.01, 1.0, Q, 600)
    p(f"Q={Q}: alpha={al:.4f} eta={et:.4f} " + " ".join(f"q={q:+d}:({ex[q][0]:.3f},{ex[q][1]:.3f})" for q in range(0, Q + 1)))
ab, aa, c1, root = glft_approx(0.5, 1.5, 0.01, 1.0, 0)
p(f"approx q=0: {ab:.3f}; c1={c1:.4f}; 1/k={1/1.5:.4f}")

p("## GLFT 4.5(c) threshold: gamma at which the flat quote crosses 1.0 tick")
p("reader used the asymptotic approximation c1 + root/2 (C2_threshold.py); here also the EXACT bounded solution")
for A, k, s in ((0.5, 1.5, 1.0), (0.5, 1.5, 0.5), (0.1, 1.5, 1.0)):
    f_approx = lambda gm: glft_approx(A, k, gm, s, 0)[0] - 1.0
    try:
        g_approx = brentq(f_approx, 1e-6, 50)
    except ValueError:
        g_approx = float("nan")
    row = f"A={A} k={k} sigma={s}: approx gamma*={g_approx:.4f}"
    for Q in (1, 2, 3):
        f_exact = lambda gm: glft_exact(A, k, gm, s, Q, 600)[2][0][0] - 1.0
        try:
            g_ex = brentq(f_exact, 1e-6, 50)
        except ValueError:
            g_ex = float("nan")
        row += f" | exact Q={Q}: gamma*={g_ex:.4f}"
    p(row)
# how far is the exact flat quote from the touch/behind boundary at the reader's gamma=0.01?
for Q in (1, 2, 3):
    _, _, exq = glft_exact(0.5, 1.5, 0.01, 1.0, Q, 600)
    p(f"  gamma=0.01, Q={Q}: exact flat quote {exq[0][0]:.3f} (rounds to {'0.5 (touch)' if exq[0][0] < 1.0 else '1.5 (behind)'})")

# ---------------------------------------------------------------- 4.6 fee arithmetic
p("## 4.6 arithmetic")
p(f"3/sqrt(80) = {3/math.sqrt(80):.4f}; x sqrt(252) = {3/math.sqrt(80)*math.sqrt(252):.3f}")
for name, tv, rt in (("MES", 1.25, 1.22), ("ES", 12.50, 3.78)):
    net = tv / 2 - rt / 2
    p(f"{name}: net per fill ${net:.4f} = {net/tv:.4f} tick; RT/tick = {rt/tv:.4f}")
p(f"ES/MES margin ratio in ticks: {(6.25-1.89)/12.5 / ((0.625-0.61)/1.25):.1f}")

# ---------------------------------------------------------------- 7.5 Almgren-Chriss
p("## A-C 7.5: kappa and trajectory")
for lam, s_, eta in ((0.1, 1.0, 0.05), (1e-4, 1.0, 0.05), (1e-4, 1.0, 5.0)):
    kap = math.sqrt(lam * s_**2 / eta)
    p(f"lambda={lam} eta={eta}: kappa={kap:.4f}/s, 1/kappa={1/kap:.2f}s, ln2/kappa (true half-life)={math.log(2)/kap:.2f}s")
X0, T, N = 20, 60.0, 6
lam, s_, eta = 1e-3, 1.0, 5.0
tau = T / N
kt2 = lam * s_**2 / eta
kap = math.acosh(1 + kt2 * tau**2 / 2) / tau
xs = [X0 * math.sinh(kap * (T - j * tau)) / math.sinh(kap * T) for j in range(N + 1)]
p(f"kappa={kap:.5f}; holdings {[round(x,2) for x in xs]}; trades {[round(xs[j-1]-xs[j],2) for j in range(1,N+1)]}")
p(f"continuous-time kappa sqrt(lam sig^2/eta)={math.sqrt(kt2):.5f}")

# ---------------------------------------------------------------- 9.3 calibration
p("## 9.3 toy calibration: counts (1800,400,90,20) at d=(0.5,1.5,2.5,3.5), T=3600")
d = np.array([0.5, 1.5, 2.5, 3.5])
Nc = np.array([1800, 400, 90, 20], float)
T = 3600.0
lam = Nc / T
X = np.vstack([np.ones_like(d), -d]).T
W = np.diag(Nc)
beta = np.linalg.solve(X.T @ W @ X, X.T @ W @ np.log(lam))
cov = np.linalg.inv(X.T @ W @ X)
p(f"lambda={np.round(lam,5)} se={np.round(np.sqrt(Nc)/T,5)}")
p(f"WLS: A={math.exp(beta[0]):.4f} k={beta[1]:.4f} se(k)={math.sqrt(cov[1,1]):.4f}")
# Poisson MLE for exponential intensity (same model): solve score equations directly
from scipy.optimize import fsolve


def score(th):
    lA, kk = th
    mu = T * np.exp(lA - kk * d)
    return [np.sum(Nc - mu), np.sum(-d * (Nc - mu))]


lA, kk = fsolve(score, [0.0, 1.5])
p(f"Poisson MLE: A={math.exp(lA):.4f} k={kk:.4f}")
# true generating values if counts were exact: N = T*A*exp(-k d)
p(f"check: with A=1, k=1.5 expected counts = {np.round(T*np.exp(-1.5*d),1)}")
# Fisher s.e. of k from Poisson MLE
mu = T * np.exp(lA - kk * d)
I = np.array([[np.sum(mu), -np.sum(d * mu)], [-np.sum(d * mu), np.sum(d * d * mu)]])
p(f"Poisson MLE se(k) = {math.sqrt(np.linalg.inv(I)[1,1]):.4f}")

with open(__file__.replace(".py", "_out.txt"), "w") as fh:
    fh.write("\n".join(out) + "\n")
