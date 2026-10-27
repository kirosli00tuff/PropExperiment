"""MathReview D: Monte Carlo standard error of the 5.4a break-even alphas (tau = 1 min).
Four independent batches of 100,000 CRN paths; alpha grid 1.0..3.5 step 0.5; alpha* by linear interpolation
against nominal alpha and against the batch's simulated alpha (the reader's convention). Prints results only."""
import numpy as np

SIG, H, DT = 3.15, 15.0, 1.0 / 60.0
NSTEP = int(H / DT); tgrid = np.arange(1, NSTEP + 1) * DT
ALPHAS = np.arange(1.0, 3.51, 0.5)
K = 60  # tau = 1 min
CASES = [("TT L cal Topstep", "TT", 0.470, 0.528), ("TT L BM Topstep", "TT", 0.0, 0.528), ("TT L cal Tradeify", "TT", 0.470, 0.920),
         ("Q K cal Bulenox", "Q", 0.287, 0.572), ("Q FIFO cal Bulenox", "Q", 0.252, 0.572), ("Q BM Bulenox", "Q", 0.0, 0.572),
         ("Q K cal Lucid", "Q", 0.287, 0.560), ("Q FIFO cal Lucid", "Q", 0.252, 0.560)]
rng = np.random.default_rng(777)

def root(x, y):
    for i in range(len(y) - 1):
        if y[i] <= 0 <= y[i + 1]:
            return x[i] + (x[i + 1] - x[i]) * (-y[i]) / (y[i + 1] - y[i])
    return float("nan")

res = {c[0]: ([], []) for c in CASES}
res_lc = {c[0]: ([], []) for c in CASES}
for b in range(4):
    acc = {}
    sumG = np.zeros(len(ALPHAS))
    for ch in range(10):
        W = np.cumsum(rng.standard_normal((10000, NSTEP)) * np.sqrt(DT), axis=1) * SIG
        for ai, al in enumerate(ALPHAS):
            X = W + (al / H) * tgrid
            G = X[:, -1]; sumG[ai] += G.sum()
            mn = np.minimum.accumulate(X[:, :K], axis=1)[:, -1]
            Xt = X[:, K - 1]
            for rule, lev in (("TT", -1.0), ("Q", -0.5)):
                f = mn <= lev
                a = acc.setdefault((ai, rule), np.zeros(5))
                a[0] += f.sum(); a[1] += G[f].sum(); a[2] += (~f).sum(); a[4] += (G[~f] - Xt[~f]).sum()
    asim = sumG / 100000
    for name, rule, cal, F in CASES:
        VL, VLC = [], []
        for ai in range(len(ALPHAS)):
            a = acc[(ai, rule)]
            p = a[0] / 100000; egf = a[1] / a[0]; rem = a[4] / a[2]
            VL.append(p * (egf - cal - F)); VLC.append(p * (egf - cal - F) + (1 - p) * (rem - 1 - F))
        VL, VLC = np.array(VL), np.array(VLC)
        res[name][0].append(root(ALPHAS, VL)); res[name][1].append(root(asim, VL))
        res_lc[name][0].append(root(ALPHAS, VLC)); res_lc[name][1].append(root(asim, VLC))
    print(f"batch {b}: alpha_sim at nominal 2.0 = {asim[2]:.3f}")
print("\ncase | L alpha* vs nominal: mean (SD over 4 batches) | vs alpha_sim: mean (SD) | LC vs nominal | LC vs alpha_sim")
for name, *_ in CASES:
    n0, n1 = np.array(res[name][0]), np.array(res[name][1]); l0, l1 = np.array(res_lc[name][0]), np.array(res_lc[name][1])
    print(f"{name:20s} {n0.mean():.3f} ({n0.std(ddof=1):.3f}) | {n1.mean():.3f} ({n1.std(ddof=1):.3f}) | {l0.mean():.3f} ({l0.std(ddof=1):.3f}) | {l1.mean():.3f} ({l1.std(ddof=1):.3f})")
print("market alpha*: Topstep 1.528, Tradeify 1.920, Bulenox 1.572, Lucid 1.560")
