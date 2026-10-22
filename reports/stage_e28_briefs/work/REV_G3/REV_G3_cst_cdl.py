"""REV_G3 independent re-derivation of C2_LOB sections 1-2 numbers.
(1) CST Result A (mid up first, S=1) and Result B (fill before move) by exact absorbing-chain
    solve, compared with the paper's Table 3 / Table 4 Laplace values.
(2) Diagnostic: what fill rate r would reproduce Table 4 for (b=1,a) if the ask dynamics are as read.
(3) CdL eq. (7) by quadrature vs (2/pi) arctan(n/p) vs a direct discrete-Dirichlet solve.
Run: python -I REV_G3_cst_cdl.py   (prints a short summary only)."""
import numpy as np
from scipy import integrate, optimize, sparse
from scipy.sparse.linalg import spsolve

LAM, MU, TH = 1.85, 0.94, 0.71  # CST Table 2, per minute, sizes in units of S_l
NMAX = 150


def ask_hit_before_fill_prob(a: int, fill_rates: list[float]) -> float:
    """P[sum of independent Exp(fill_rates) < sigma_A], sigma_A = hitting time of 0 by a
    birth-death chain with birth LAM and death MU + i*TH from state a. Exact via a 2-D
    absorbing chain over (ask state i in 1..NMAX, stage j in 0..b-1)."""
    b = len(fill_rates)
    n = NMAX * b
    idx = lambda i, j: (i - 1) * b + j  # noqa: E731
    rows, cols, vals, rhs = [], [], [], np.zeros(n)
    for i in range(1, NMAX + 1):
        d = MU + i * TH
        up = LAM if i < NMAX else 0.0
        for j in range(b):
            r = fill_rates[j]
            tot = d + up + r
            k = idx(i, j)
            rows.append(k); cols.append(k); vals.append(tot)
            if j + 1 < b:
                rows.append(k); cols.append(idx(i, j + 1)); vals.append(-r)
            else:
                rhs[k] += r  # final fill: success
            if i > 1:
                rows.append(k); cols.append(idx(i - 1, j)); vals.append(-d)
            # i == 1 death -> ask hits 0 -> failure (contributes 0)
            if up > 0:
                rows.append(k); cols.append(idx(i + 1, j)); vals.append(-up)
    A = sparse.csr_matrix((vals, (rows, cols)), shape=(n, n))
    p = spsolve(A, rhs)
    return float(p[idx(a, 0)])


def mid_up_prob(b: int, a: int) -> float:
    """P[ask hits 0 before bid hits 0], both birth-death(LAM, MU + i*TH), S=1."""
    N = NMAX
    n = N * N
    idx = lambda i, j: (i - 1) * N + (j - 1)  # noqa: E731
    rows, cols, vals, rhs = [], [], [], np.zeros(n)
    for i in range(1, N + 1):  # ask
        for j in range(1, N + 1):  # bid
            da, db = MU + i * TH, MU + j * TH
            ua = LAM if i < N else 0.0
            ub = LAM if j < N else 0.0
            tot = da + db + ua + ub
            k = idx(i, j)
            rows.append(k); cols.append(k); vals.append(tot)
            if i > 1:
                rows.append(k); cols.append(idx(i - 1, j)); vals.append(-da)
            else:
                rhs[k] += da  # ask hits 0 -> up move
            if j > 1:
                rows.append(k); cols.append(idx(i, j - 1)); vals.append(-db)
            if ua:
                rows.append(k); cols.append(idx(i + 1, j)); vals.append(-ua)
            if ub:
                rows.append(k); cols.append(idx(i, j + 1)); vals.append(-ub)
    A = sparse.csr_matrix((vals, (rows, cols)), shape=(n, n))
    p = spsolve(A, rhs)
    return float(p[idx(a, b)])


def cdl_phi_quad(n: int, p: int) -> float:
    f = lambda t: (2 - np.cos(t) - np.sqrt((2 - np.cos(t)) ** 2 - 1)) ** p * np.sin(n * t) * np.cos(t / 2) / np.sin(t / 2)  # noqa: E731
    v, _ = integrate.quad(f, 1e-12, np.pi, limit=400)
    return v / np.pi


def cdl_phi_dirichlet(n: int, p: int, N: int = 400) -> float:
    """Solve 4 phi = sum of 4 neighbours on [1..N]^2 with phi(0,p)=0, phi(n,0)=1 and a
    far boundary set to the arctan continuum value (negligible effect near the origin)."""
    idx = lambda i, j: (i - 1) * N + (j - 1)  # noqa: E731
    size = N * N
    rows, cols, vals, rhs = [], [], [], np.zeros(size)
    for i in range(1, N + 1):  # bid n
        for j in range(1, N + 1):  # ask p
            k = idx(i, j)
            rows.append(k); cols.append(k); vals.append(4.0)
            for (ii, jj) in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)):
                if ii == 0:
                    continue  # phi = 0
                if jj == 0:
                    rhs[k] += 1.0  # phi = 1
                    continue
                if ii > N or jj > N:
                    rhs[k] += (2 / np.pi) * np.arctan(ii / jj)
                    continue
                rows.append(k); cols.append(idx(ii, jj)); vals.append(-1.0)
    A = sparse.csr_matrix((vals, (rows, cols)), shape=(size, size))
    phi = spsolve(A, rhs)
    return float(phi[idx(n, p)])


if __name__ == "__main__":
    print("CST Result A (mid up), mine vs paper Table 3 Laplace:")
    for (b, a, paper) in [(2, 1, .664), (3, 1, .741), (5, 1, .812), (1, 2, .336), (1, 5, .188)]:
        print(f"  b={b} a={a}: {mid_up_prob(b, a):.4f} vs {paper}")
    print("CST Result B (fill before move), b orders at bid incl. ours (rates MU+TH*(i-1)), vs Table 4 Laplace:")
    tab4 = {(1, 1): .497, (1, 5): .776, (3, 1): .206, (5, 5): .393, (1, 2): .641, (2, 1): .302, (5, 1): .118}
    for (b, a), paper in tab4.items():
        rates = [MU + TH * (i - 1) for i in range(1, b + 1)]
        print(f"  b={b} a={a}: {ask_hit_before_fill_prob(a, rates):.4f} vs {paper}")
    print("Variant: b others AHEAD of ours (b+1 total):")
    for (b, a), paper in tab4.items():
        rates = [MU + TH * (i - 1) for i in range(1, b + 2)]
        print(f"  b={b} a={a}: {ask_hit_before_fill_prob(a, rates):.4f} vs {paper}")
    print("Diagnostic: single fill rate r reproducing Table 4 row b=1 for each a:")
    for a, paper in [(1, .497), (2, .641), (3, .709), (4, .749), (5, .776)]:
        g = lambda r: ask_hit_before_fill_prob(a, [r]) - paper  # noqa: E731
        try:
            r = optimize.brentq(g, 0.05, 5.0)
            print(f"  a={a}: r={r:.3f}")
        except ValueError:
            print(f"  a={a}: no root in [0.05, 5]")
    print("CdL eq. 7 quadrature vs arctan vs Dirichlet solve:")
    for (n, p) in [(2, 1), (5, 2), (3, 10), (300, 100), (50, 450), (1, 1), (10, 10)]:
        q = cdl_phi_quad(n, p)
        at = (2 / np.pi) * np.arctan(n / p)
        d = cdl_phi_dirichlet(n, p) if max(n, p) <= 60 else float("nan")
        print(f"  phi({n},{p}): quad {q:.4f}  arctan {at:.4f}  dirichlet {d:.4f}")
