"""MathReview D: independent Brownian simulation of M6 sections 2.3 and 5.4a.
Model as stated in M6: mid X_t = mu t + sigma W_t (ticks, minutes), sigma = 3.15, H = 15 min, 1-second grid,
fill rules in the mid coordinate: TT fill iff running min <= -1.0 within tau; Q fill iff <= -0.5.
Own seed (20261028). Chunked to keep memory small. Prints results only."""
import numpy as np

SIG = 3.15
H = 15.0
DT = 1.0 / 60.0
NSTEP = int(H / DT)
rng = np.random.default_rng(20261028)
NPATH = 100_000
CHUNK = 10_000
TAUS = (0.5, 1.0, 2.0, 5.0)
ALPHAS = np.arange(0.0, 6.01, 0.5)
tgrid = np.arange(1, NSTEP + 1) * DT
FEES = {"Topstep": 0.528, "Lucid": 0.560, "Tradeify": 0.920, "MFFU": 0.612, "Bulenox": 0.572}

# accumulators: key (alpha_idx, tau, rule) -> [n_fill, sum_G_fill, n_nofill, sum_G_nofill, sum_rem_nofill]
acc = {}
sumG = np.zeros(len(ALPHAS))
# bracket accumulators for alpha=2 constant drift: (a, rule) -> [sum_pnl, n_tp]
br = {}
# front-loaded drift (alpha = 2): rate A exp(-t/3)
A = 2.0 / (3.0 * (1 - np.exp(-5.0)))
front_cum = A * 3.0 * (1 - np.exp(-tgrid / 3.0))
fl = {}
for c in range(NPATH // CHUNK):
    W = np.cumsum(rng.standard_normal((CHUNK, NSTEP)) * np.sqrt(DT), axis=1)
    base = SIG * W
    for ai, al in enumerate(ALPHAS):
        X = base + (al / H) * tgrid
        G = X[:, -1]
        sumG[ai] += G.sum()
        cummin = np.minimum.accumulate(X, axis=1)
        for tau in TAUS:
            k = int(tau / DT)
            mn = cummin[:, k - 1]
            Xtau = X[:, k - 1]
            for rule, lev in (("TT", -1.0), ("Q", -0.5)):
                f = mn <= lev
                key = (ai, tau, rule)
                a = acc.setdefault(key, np.zeros(5))
                a[0] += f.sum(); a[1] += G[f].sum(); a[2] += (~f).sum(); a[3] += G[~f].sum(); a[4] += (G[~f] - Xtau[~f]).sum()
        if abs(al - 2.0) < 1e-9:
            # bracket: market entry at ask (+0.5), stop when mid <= -6 (sell at bid: pnl -7), TP a: TT trigger mid >= a+1, Q trigger mid >= a+0.5, pnl = a; else time stop pnl = G - 1
            cummax = np.maximum.accumulate(X, axis=1)
            hit_stop = cummin <= -6.0
            t_stop = np.where(hit_stop.any(axis=1), hit_stop.argmax(axis=1), NSTEP + 1)
            for a_tp in (4, 6, 10):
                for rule, trig in (("TT", a_tp + 1.0), ("Q", a_tp + 0.5)):
                    hit_tp = cummax >= trig
                    t_tp = np.where(hit_tp.any(axis=1), hit_tp.argmax(axis=1), NSTEP + 1)
                    tp_first = (t_tp < t_stop) & (t_tp <= NSTEP)
                    stop_first = (t_stop < t_tp) & (t_stop <= NSTEP)
                    pnl = np.where(tp_first, float(a_tp), np.where(stop_first, -7.0, G - 1.0))
                    b = br.setdefault((a_tp, rule), np.zeros(2))
                    b[0] += pnl.sum(); b[1] += tp_first.sum()
    # front-loaded drift, alpha = 2
    Xf = base + front_cum
    Gf = Xf[:, -1]
    cmf = np.minimum.accumulate(Xf, axis=1)
    for tau in (1.0, 5.0):
        k = int(tau / DT)
        f = cmf[:, k - 1] <= -1.0
        a = fl.setdefault(tau, np.zeros(6))
        a[0] += f.sum(); a[1] += Gf[f].sum(); a[2] += (~f).sum(); a[3] += Gf[~f].sum(); a[4] += (Gf[~f] - Xf[~f, k - 1]).sum(); a[5] += Gf.sum()

alpha_sim = sumG / NPATH
print("N paths", NPATH, "; simulated alpha at nominal 2.0:", round(alpha_sim[4], 3), "(SE", round(12.2 / np.sqrt(NPATH), 3), ")")
print("\n== 2.3 table (constant drift alpha=2): rule tau p E[G|F] E[G|nF] V_L gross V_LC gross E[rem|nF] ==")
ai2 = 4
for rule in ("TT", "Q"):
    for tau in TAUS:
        a = acc[(ai2, tau, rule)]
        p = a[0] / NPATH; egf = a[1] / a[0]; egn = a[3] / a[2]; rem = a[4] / a[2]
        vl = p * (egf + 0.5); vlc = vl + (1 - p) * (rem - 0.5)
        print(f"{rule:2s} {tau:4.1f} {p:.3f} {egf:.3f} {egn:.3f} {vl:.3f} {vlc:.3f} {rem:.3f}  decomp={p*egf+(1-p)*egn:.3f}")
print("Market gross alpha-0.5:", round(alpha_sim[4] - 0.5, 3))
print("\n== front-loaded drift, TT: tau p E[G|F] E[G|nF] E[rem|nF] (chase value per unfilled = rem-0.5) alpha_sim ==")
for tau in (1.0, 5.0):
    a = fl[tau]
    print(f"{tau:3.0f} {a[0]/NPATH:.3f} {a[1]/a[0]:.3f} {a[3]/a[2]:.3f} {a[4]/a[2]:.3f} {a[4]/a[2]-0.5:.3f} {a[5]/NPATH:.3f}")
print("theoretical remaining drift after 5 min (front-loaded):", round(2.0 * (np.exp(-5/3) - np.exp(-5)) / (1 - np.exp(-5)), 3))
print("\n== brackets (alpha=2, stop -6 mid, time stop 15): a  E[pnl] TT  E[pnl] Q  P(TP) TT/Q ==")
for a_tp in (4, 6, 10):
    bt, bq = br[(a_tp, "TT")], br[(a_tp, "Q")]
    print(f"{a_tp:2d} {bt[0]/NPATH:.3f} {bq[0]/NPATH:.3f} {bt[1]/NPATH:.3f}/{bq[1]/NPATH:.3f}")
print("time stop alone gross (alpha_sim - 1):", round(alpha_sim[4] - 1, 3))

# 5.4a: break-even alphas by interpolation on the CRN grid, tau = 1
print("\n== 5.4a: alpha* (V=0) and alpha(1.0 per executed trade), tau=1, interpolated on alpha grid 0..6 step 0.5 ==")
def curves(rule, cal, F):
    VL, VT, VLC = [], [], []
    for ai in range(len(ALPHAS)):
        a = acc[(ai, 1.0, rule)]
        p = a[0] / NPATH; egf = a[1] / a[0]; rem = a[4] / a[2]
        vt = egf - cal - F
        VL.append(p * vt); VT.append(vt); VLC.append(p * vt + (1 - p) * (rem - 1.0 - F))
    return np.array(VL), np.array(VT), np.array(VLC)
def root(y, target=0.0):
    y = y - target
    for i in range(len(y) - 1):
        if y[i] <= 0 <= y[i + 1]:
            return ALPHAS[i] + (ALPHAS[i + 1] - ALPHAS[i]) * (-y[i]) / (y[i + 1] - y[i])
    return float("nan")
p1 = acc[(ai2, 1.0, "TT")][0] / NPATH; pq1 = acc[(ai2, 1.0, "Q")][0] / NPATH
print("p(TT,1 min, alpha 2) =", round(p1, 3), " p(Q) =", round(pq1, 3))
for firm, F in FEES.items():
    print(f"{firm}: market alpha*={1+F:.3f} alpha(1.0)={2+F:.3f}")
    for rule, cal, lab in (("TT", 0.470, "TT L cal"), ("TT", 0.0, "TT L BM"), ("Q", 0.287, "Q K cal"), ("Q", 0.252, "Q FIFO cal"), ("Q", 0.0, "Q BM")):
        VL, VT, VLC = curves(rule, cal, F)
        print(f"   {lab:10s} L: alpha*={root(VL):.3f} alpha(1.0/trade)={root(VT, 1.0):.3f} | LC: alpha*={root(VLC):.3f} alpha(1.0)={root(VLC, 1.0):.3f} | V/signal at alpha2: L {VL[4]:.3f} LC {VLC[4]:.3f} V/trade {VT[4]:.3f}")
