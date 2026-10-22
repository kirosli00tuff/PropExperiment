"""REV_G3: (A) CST Table 4 under 'own order cancels at rate theta, probability conditioned on no own
cancellation' (rejection conditioning, as a simulation would do); (B) Cont-de Larrard eqs (3)-(4)
evaluated numerically at lambda=12, mu+theta=13, (a,b)=(4,5) to test the paper's eq (5) claim of a
t^-2 tail against the exponential tail implied by the Bessel asymptotics.
Run: python -I REV_G3_cst_cond_cdl_tail.py"""
import numpy as np
from scipy import integrate, special, sparse
from scipy.sparse.linalg import spsolve

LAM, MU, TH = 1.85, 0.94, 0.71
NMAX = 160
TAB4 = {(1, 1): .497, (1, 2): .641, (1, 3): .709, (1, 4): .749, (1, 5): .776,
        (2, 1): .302, (3, 1): .206, (4, 1): .152, (5, 1): .118, (5, 5): .393, (2, 3): .535}


def cond_fill(a, b, own_cancel, others_cancel=True):
    """Three absorbing outcomes: fill (F), ask hits 0 (A), own cancel (C). Returns F/(F+A)."""
    n = NMAX * b
    idx = lambda i, j: (i - 1) * b + j  # noqa: E731
    rows, cols, vals = [], [], []
    rhsF, rhsA = np.zeros(n), np.zeros(n)
    for i in range(1, NMAX + 1):
        d = MU + i * TH
        up = LAM if i < NMAX else 0.0
        for j in range(b):
            ahead = b - 1 - j
            r = MU + (TH * ahead if others_cancel else 0.0)
            tot = d + up + r + own_cancel
            k = idx(i, j)
            rows.append(k); cols.append(k); vals.append(tot)
            if j + 1 < b:
                rows.append(k); cols.append(idx(i, j + 1)); vals.append(-r)
            else:
                rhsF[k] += r
            if i > 1:
                rows.append(k); cols.append(idx(i - 1, j)); vals.append(-d)
            else:
                rhsA[k] += d
            if up > 0:
                rows.append(k); cols.append(idx(i + 1, j)); vals.append(-up)
    A = sparse.csr_matrix((vals, (rows, cols)), shape=(n, n))
    pF = spsolve(A, rhsF)[idx(a, 0)]
    pA = spsolve(A, rhsA)[idx(a, 0)]
    return float(pF / (pF + pA)), float(pF), float(pA)


def psi(n, t, lam, mup):
    f = lambda u: (n / u) * special.ive(n, 2 * np.sqrt(lam * mup) * u) * np.exp(  # noqa: E731
        2 * np.sqrt(lam * mup) * u - u * (lam + mup))
    v, _ = integrate.quad(f, t, np.inf, limit=500)
    return v


def cdl_survival(a, b, t, lam, mup):
    return (mup / lam) ** ((a + b) / 2) * psi(a, t, lam, mup) * psi(b, t, lam, mup)


if __name__ == "__main__":
    print("(A) CST Table 4, own order cancels at theta, conditioned on no own cancel: (b,a) mine/paper")
    for (b, a), paper in TAB4.items():
        p, pF, pA = cond_fill(a, b, TH)
        print(f"  ({b},{a}) {p:.3f}/{paper}   [P(fill)={pF:.3f} P(ask0)={pA:.3f} P(own cancel)={1 - pF - pA:.3f}]")
    print("  same but others ahead do not cancel:")
    for (b, a), paper in [((2, 1), .302), ((3, 1), .206), ((5, 1), .118), ((5, 5), .393), ((2, 3), .535)]:
        p, _, _ = cond_fill(a, b, TH, others_cancel=False)
        print(f"  ({b},{a}) {p:.3f}/{paper}")

    print("\n(B) CdL eqs (3)-(4): P[tau>t | a=4, b=5], lambda=12, mu+theta=13; eq (5) prediction; log-slope")
    lam, mup, a, b = 12.0, 13.0, 4, 5
    ts = [1, 5, 10, 20, 50, 100, 200, 400, 800]
    prev = None
    for t in ts:
        s = cdl_survival(a, b, t, lam, mup)
        eq5 = a * b * (lam + mup) ** 2 / (lam ** 2 * (mup - lam) ** 2 * 4 * t ** 2)
        slope = "" if prev is None else f" local exponent d ln P/d ln t = {np.log(s / prev[1]) / np.log(t / prev[0]):.2f}"
        print(f"  t={t:4d}: P={s:.3e}  eq5={eq5:.3e}{slope}")
        prev = (t, s)
    print(f"  Bessel asymptotic decay rate (sqrt(mu')-sqrt(lam))^2 = {(np.sqrt(mup) - np.sqrt(lam)) ** 2:.4f} per unit time")
    # mean of sigma from state 1: 1/(mu'-lam) by d/ds of alpha(s); paper's coefficient (lam+mu')/(2 lam (mu'-lam))
    print(f"  E[sigma_1]: exact 1/(mu'-lam) = {1 / (mup - lam):.4f}; paper's small-s coefficient (lam+mu')/(2 lam (mu'-lam)) = {(lam + mup) / (2 * lam * (mup - lam)):.4f}")
    # numeric check of the mean from the survival function of one queue from x=1
    m, _ = integrate.quad(lambda t: (mup / lam) ** 0.5 * psi(1, t, lam, mup), 0, np.inf, limit=500)
    print(f"  numeric E[sigma_1] from eqs (3)-(4) = {m:.4f}")
