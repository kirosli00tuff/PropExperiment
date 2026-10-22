"""REV_G3: more readings of CST (2010) Result B against the paper's Table 4, and a check of the
reader's queue-length illustration (C2_LOB.md section 1.5). Run: python -I REV_G3_cst_variants.py"""
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve

LAM, MU, TH = 1.85, 0.94, 0.71
NMAX = 160
TAB4 = {(1, 1): .497, (1, 2): .641, (1, 5): .776, (2, 1): .302, (3, 1): .206, (5, 1): .118, (5, 5): .393}


def fill_before_ask_hits_zero(a, fill_rates, ask_birth, ask_death, own_cancel=0.0):
    """P[sum Exp(fill_rates) < sigma_A] where the ask queue has birth ask_birth(i), death ask_death(i)
    from state a; own_cancel is an extra absorbing failure rate (our order cancelled)."""
    b = len(fill_rates)
    n = NMAX * b
    idx = lambda i, j: (i - 1) * b + j  # noqa: E731
    rows, cols, vals, rhs = [], [], [], np.zeros(n)
    for i in range(1, NMAX + 1):
        d = ask_death(i)
        up = ask_birth(i) if i < NMAX else 0.0
        for j in range(b):
            r = fill_rates[j]
            tot = d + up + r + own_cancel
            k = idx(i, j)
            rows.append(k); cols.append(k); vals.append(tot)
            if j + 1 < b:
                rows.append(k); cols.append(idx(i, j + 1)); vals.append(-r)
            else:
                rhs[k] += r
            if i > 1:
                rows.append(k); cols.append(idx(i - 1, j)); vals.append(-d)
            if up > 0:
                rows.append(k); cols.append(idx(i + 1, j)); vals.append(-up)
    A = sparse.csr_matrix((vals, (rows, cols)), shape=(n, n))
    return float(spsolve(A, rhs)[idx(a, 0)])


def report(name, fn):
    out = []
    for (b, a), paper in TAB4.items():
        out.append(f"({b},{a}) {fn(b, a):.3f}/{paper}")
    print(f"{name:40s} " + "  ".join(out))


if __name__ == "__main__":
    base_rates = lambda b: [MU + TH * (i - 1) for i in range(1, b + 1)]  # noqa: E731
    print("Format: (b,a) mine/paper")
    report("V0 as read (b incl. ours)", lambda b, a: fill_before_ask_hits_zero(
        a, base_rates(b), lambda i: LAM, lambda i: MU + i * TH))
    report("V1 ask death const mu+theta", lambda b, a: fill_before_ask_hits_zero(
        a, base_rates(b), lambda i: LAM, lambda i: MU + TH))
    report("V2 ask no births", lambda b, a: fill_before_ask_hits_zero(
        a, base_rates(b), lambda i: 0.0, lambda i: MU + i * TH))
    report("V3 bid others cancel, no mkt until last", lambda b, a: fill_before_ask_hits_zero(
        a, [MU] + [TH * (i - 1) for i in range(2, b + 1)], lambda i: LAM, lambda i: MU + i * TH))
    report("V4 ask death mu+i*theta, bid rates mu+i*theta", lambda b, a: fill_before_ask_hits_zero(
        a, [MU + TH * i for i in range(1, b + 1)], lambda i: LAM, lambda i: MU + i * TH))
    report("V5 b AHEAD of ours (b+1 total)", lambda b, a: fill_before_ask_hits_zero(
        a, base_rates(b + 1), lambda i: LAM, lambda i: MU + i * TH))
    report("V6 own cancel theta -> failure", lambda b, a: fill_before_ask_hits_zero(
        a, base_rates(b), lambda i: LAM, lambda i: MU + i * TH, own_cancel=TH))
    report("V7 ask death mu + theta*i, bid fill only mu (no cancels ahead)", lambda b, a: fill_before_ask_hits_zero(
        a, [MU] * b, lambda i: LAM, lambda i: MU + i * TH))
    print("\nReader's queue-length table (b incl. ours; a = 1, 5, 10, 20), V0 reading:")
    for b in (1, 5, 20):
        vals = [fill_before_ask_hits_zero(a, base_rates(b), lambda i: LAM, lambda i: MU + i * TH) for a in (1, 5, 10, 20)]
        print(f"  b={b}: " + ", ".join(f"{v:.2f}" for v in vals))
