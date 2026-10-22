"""Worked examples for C2_LOB: CST (2010) S=1 probabilities by exact absorbing-chain solve,
and Cont-de Larrard (2013) eq (7) vs a Brownian-quadrant approximation."""
import numpy as np
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve
from scipy.integrate import quad

def cst_mid_up(a, b, lam, mu, th, N=80):
    """P[ask queue hits 0 before bid queue], both independent birth-death: birth lam, death mu+i*th."""
    idx = lambda i, j: (i - 1) * N + (j - 1)   # i=ask 1..N, j=bid 1..N
    A = lil_matrix((N * N, N * N)); r = np.zeros(N * N)
    for i in range(1, N + 1):
        for j in range(1, N + 1):
            k = idx(i, j)
            rates = []
            if i < N: rates.append(((i + 1, j), lam))
            rates.append(((i - 1, j), mu + i * th))
            if j < N: rates.append(((i, j + 1), lam))
            rates.append(((i, j - 1), mu + j * th))
            tot = sum(q for _, q in rates); A[k, k] = tot
            for (ii, jj), q in rates:
                if ii == 0: r[k] += q          # ask depleted first: success
                elif jj == 0: pass             # bid depleted: fail
                else: A[k, idx(ii, jj)] -= q
    x = spsolve(A.tocsr(), r); return x[idx(a, b)]

def cst_exec_before_move(a, b, lam, mu, th, N=80):
    """P[our bid order (last of b, never cancels) fills before ask queue hits 0], S=1 (CST Prop 5)."""
    idx = lambda i, j: (i - 1) * b + (j - 1)   # i=ask 1..N, j=orders ahead incl. ours 1..b
    A = lil_matrix((N * b, N * b)); r = np.zeros(N * b)
    for i in range(1, N + 1):
        for j in range(1, b + 1):
            k = idx(i, j); rates = []
            if i < N: rates.append(((i + 1, j), lam))
            rates.append(((i - 1, j), mu + i * th))
            rates.append(((i, j - 1), mu + (j - 1) * th))
            tot = sum(q for _, q in rates); A[k, k] = tot
            for (ii, jj), q in rates:
                if jj == 0: r[k] += q
                elif ii == 0: pass
                else: A[k, idx(ii, jj)] -= q
    x = spsolve(A.tocsr(), r); return x[idx(a, b)]

def cdl_phi(n, p):
    """Cont-de Larrard eq (7): P(next move up | bid n, ask p), balanced flow."""
    f = lambda t: (2 - np.cos(t) - np.sqrt((2 - np.cos(t))**2 - 1))**p * np.sin(n*t) * np.cos(t/2) / np.sin(t/2)
    return quad(f, 1e-12, np.pi, limit=2000)[0] / np.pi

if __name__ == "__main__":
    lam, mu, th = 1.85, 0.94, 0.71   # CST Table 2, Sky Perfect, S=1 uses lambda(1), theta(1)
    print("CST mid-up (exact chain), paper Table 3 Laplace bottom block in brackets")
    paper3 = {(1,2): .336, (2,1): .664, (3,1): .741, (5,1): .812, (2,2): .500, (1,5): .188}
    for (b, a), pv in paper3.items():
        print(f" b={b} a={a}: {cst_mid_up(a, b, lam, mu, th):.3f} [{pv}]")
    print("CST exec-before-move, paper Table 4 Laplace block in brackets")
    paper4 = {(1,1): .497, (1,5): .776, (3,1): .206, (5,5): .393, (2,3): .535}
    for (b, a), pv in paper4.items():
        print(f" b={b} a={a}: {cst_exec_before_move(a, b, lam, mu, th):.3f} [{pv}]")
    print("CdL phi(n=bid,p=ask) eq(7) vs (2/pi)*arctan(n/p)")
    for n, p in [(1,1),(2,1),(1,2),(5,2),(3,10),(300,100),(100,300),(50,450)]:
        print(f" n={n} p={p}: eq7={cdl_phi(n,p):.4f} approx={2/np.pi*np.arctan(n/p):.4f}")
