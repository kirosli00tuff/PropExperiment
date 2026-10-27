"""M5b power, stability and Sharpe-SE calculations. Synthetic/arithmetic only: no market data is read."""
import math, numpy as np
from statistics import NormalDist
N = NormalDist(); z = N.inv_cdf; Phi = N.cdf
rng = np.random.default_rng(20261027)
S1 = 3.15                      # ZM sigma_1m, ticks (E.28 A0 Table 1)
T_TEST, T_DISC = 904, 816      # trade dates (M5b_days.py; M5a has 899 for test)
Z_BONF = z(1 - 0.05/3)         # one-sided alpha 0.05/3
Z_B = z(0.8)                   # power 0.8
CRIT = {"z(1-0.05/3)": Z_BONF, "t>3.0": 3.0, "z(0.95) ref": z(0.95)}
P = print
P("== constants"); P(f"z(1-0.05/3)={Z_BONF:.4f} z(0.8)={Z_B:.4f} z(0.95)={z(0.95):.4f} one-sided alpha of t>3: {1-Phi(3):.5f}")
sig = {h: S1*math.sqrt(h) for h in (5, 15, 60, 75)}
for h, s in sig.items(): P(f"sigma_{h} = 3.15 x sqrt({h}) = 3.15 x {math.sqrt(h):.4f} = {s:.3f} ticks")

P("\n== (c1) trades needed n = ((c + z_b) sigma / mu)^2, iid, and per-day rates")
P("crit | h | mu | n | per test day (904) | per disc day (816) | non-overlap cap/day all-sess 1055/h | day-sess 290/h")
for cn, c in list(CRIT.items())[:2]:
    for h in (5, 15, 60):
        for mu in (0.25, 0.5, 1.0):
            n = ((c + Z_B)*sig[h]/mu)**2
            P(f"{cn} | {h} | {mu} | {n:,.0f} | {n/T_TEST:.2f} | {n/T_DISC:.2f} | {1055/h:.1f} | {290/h:.1f}")

P("\n== (c2) minimum detectable net edge mu_min = (c+z_b) sigma / sqrt(k T), test window 904 days")
for cn, c in list(CRIT.items())[:2]:
    for h in (5, 15, 60):
        row = [f"{(c+Z_B)*sig[h]/math.sqrt(k*T_TEST):.3f}" for k in (1, 2, 5, 10, 20)]
        P(f"{cn} | h={h} | k=1,2,5,10,20/day: {row}")

P("\n== (c3) overlap: entries every Delta, hold h=m Delta, random walk -> rho_k = 1-k/m, D = 1+2 sum_{k<m}(1-k/m)")
for m in (2, 3, 4, 12):
    D = 1 + 2*sum(1 - k/m for k in range(1, m))
    P(f"m={m}: D={D:.3f}")
# simulation check: m=3 (hold 15 entry every 5), random-walk 5-min increments
inc = rng.standard_normal((2000, 600))   # 2000 reps, 600 five-minute steps
r = inc[:, 0:-2] + inc[:, 1:-1] + inc[:, 2:]  # overlapping 15-min returns, entry every 5 min
var_mean = r.mean(axis=1).var(); n = r.shape[1]
P(f"sim m=3: n={n}, var(mean)*n/var(r)={var_mean*n/3:.3f} (theory 3, minus end effect)")
P("within-day equicorrelation design effect D = 1 + (k-1) rho_w:")
for k in (5, 10, 20):
    P("  k=%d: " % k + ", ".join(f"rho_w={rw}: D={1+(k-1)*rw:.2f}" for rw in (0.01, 0.05, 0.1)))

P("\n== (c4) Newey-West Bartlett weights and long-run variance ratio for AR(1) daily P&L, phi")
for phi in (0.05, 0.1, 0.2):
    for L in (2, 5, 10):
        lr = 1 + 2*sum((1 - j/(L+1))*phi**j for j in range(1, L+1))
        P(f"phi={phi} L={L}: NW ratio {lr:.4f}; true LR ratio (1+phi)/(1-phi) = {(1+phi)/(1-phi):.4f}")
P("NW lag rules: floor(4 (T/100)^(2/9)): T=816 -> %d, T=904 -> %d" % (math.floor(4*(816/100)**(2/9)), math.floor(4*(904/100)**(2/9))))

P("\n== (b1) binomial null: months / quarters positive, p=0.5")
def tail(n, k, p=0.5): return sum(math.comb(n, j)*p**j*(1-p)**(n-j) for j in range(k, n+1))
for n in (39, 43, 13, 14):
    for share in (0.6, 2/3, 0.75):
        k = math.ceil(share*n - 1e-9)
        P(f"n={n} share>={share:.3f}: k={k}, P0={tail(n,k):.4f}")

P("\n== (b2) MC: blocks iid N(delta/sqrt(Q),1) [equal trades per block]; overall t = sum/sqrt(Q)")
R = 200_000
for Q, lab in ((13, "disc quarters"), (14, "test quarters"), (39, "disc months"), (43, "test months")):
    for delta in (0.0, 3.0, 3.84, 4.5, 5.0):
        x = rng.standard_normal((R, Q)) + delta/math.sqrt(Q)
        t = x.sum(1)/math.sqrt(Q); k23 = math.ceil(2*Q/3 - 1e-9)
        pos = (x > 0).sum(1)
        a = t > 3.0; b = pos >= k23
        P(f"{lab} Q={Q} delta={delta}: P(t>3)={a.mean():.3f} P(share>=2/3,k={k23})={b.mean():.3f} joint={np.mean(a&b):.3f} P(b|a)={np.mean(a&b)/max(a.mean(),1e-9):.3f} mean share pos={pos.mean()/Q:.3f}")

P("\n== (b3) MC months: max single-month share of total P&L and leave-one-month-out (LOMO) min t, conditional on t>3")
for M in (39, 43):
    for delta in (3.0, 3.84, 5.0):
        x = rng.standard_normal((R, M)) + delta/math.sqrt(M)
        tot = x.sum(1); t = tot/math.sqrt(M); ok = t > 3.0
        share = x.max(1)/tot
        lomo = (tot[:, None] - x)/math.sqrt(M-1)
        lmin = lomo.min(1)
        qs = np.quantile(share[ok], [0.5, 0.9, 0.99]); ql = np.quantile(lmin[ok], [0.01, 0.1, 0.5])
        P(f"M={M} delta={delta}: P(t>3)={ok.mean():.3f}; max-month share | t>3: median {qs[0]:.3f}, p90 {qs[1]:.3f}, p99 {qs[2]:.3f}; P(share<=0.25|t>3)={np.mean(share[ok]<=0.25):.3f}; LOMO min t | t>3: p1 {ql[0]:.2f}, p10 {ql[1]:.2f}, median {ql[2]:.2f}; P(LOMO min t>2.5|t>3)={np.mean(lmin[ok]>2.5):.3f}")
# under the null, distribution of max share is ill-defined (total near 0); report a one-month-spike example
P("spike example: 43 months, 42 months N(0,1) noise, 1 month +6 sd: P(t>3)=", round(float(np.mean((rng.standard_normal((R,42)).sum(1)+6)/math.sqrt(43) > 3)), 4))

P("\n== (b4) regime terciles: each tercile carries 1/3 of trades -> z_i = delta/sqrt(3)")
for delta in (3.0, 3.84, 5.0):
    zi = delta/math.sqrt(3)
    P(f"delta={delta}: z_i={zi:.3f}, P(all 3 positive)={Phi(zi)**3:.3f}, P(all 3 z>1.645)={Phi(zi-1.645)**3:.3f}, P(all 3 z>1.0)={Phi(zi-1.0)**3:.3f}")

P("\n== (b5) stationary bootstrap expected block length, AR(1) daily series: b = n^(1/3) (2 phi/(1-phi^2))^(2/3)")
for n in (816, 904):
    for phi in (0.05, 0.1, 0.2, 0.3):
        g = 2*sum(k*phi**k for k in range(1, 400)); s2 = 1 + 2*sum(phi**k for k in range(1, 400))
        b_num = (2*g**2/(2*s2**2)*n)**(1/3); b_cf = n**(1/3)*(2*phi/(1-phi**2))**(2/3)
        P(f"n={n} phi={phi}: b_SB numeric {b_num:.3f}, closed form {b_cf:.3f}, p=1/b={1/b_cf:.3f}")

P("\n== (d1) Sharpe SE per trade: Lo IID sqrt((1+SR^2/2)/T); Mertens sqrt((1+SR^2/2-g3 SR+(g4-3)/4 SR^2)/T)")
for h, mu in ((15, 1.0), (60, 1.0), (5, 0.5)):
    SR = mu/sig[h]
    for T in (5000, 20000):
        lo = math.sqrt((1+SR**2/2)/T)
        out = [f"g3={g3},g4={g4}: {math.sqrt((1+SR**2/2-g3*SR+(g4-3)/4*SR**2)/T):.6f}" for g3, g4 in ((0, 3), (-0.5, 8), (-1.0, 20))]
        P(f"h={h} mu={mu} SR={SR:.5f} T={T}: naive 1/sqrt(T)={1/math.sqrt(T):.6f} Lo={lo:.6f} Mertens " + "; ".join(out))

P("\n== (d2) MinTRL = 1 + (1 - g3 SR + (g4-1)/4 SR^2) (z_a/(SR - SR*))^2, SR*=0; and 80%-power n")
for h, mu in ((5, 0.5), (15, 1.0), (60, 1.0), (15, 0.5)):
    SR = mu/sig[h]
    for cn, c in (("z(1-0.05/3)", Z_BONF), ("t>3.0", 3.0)):
        r = []
        for g3, g4 in ((0, 3), (-0.5, 8)):
            r.append(f"g3={g3},g4={g4}: MinTRL={1+(1-g3*SR+(g4-1)/4*SR**2)*(c/SR)**2:,.0f}")
        P(f"h={h} mu={mu} SR={SR:.5f} {cn}: " + "; ".join(r) + f"; power-0.8 n={((c+Z_B)/SR)**2:,.0f}")
# daily-annualised illustration (BLdP style): one trade per day h=15 mu=1
SR = 1/sig[15]; P(f"annualised SR at 1 trade/day, 251 days/yr: {SR*math.sqrt(251):.3f}")

P("\n== (c5) event family power: n events, one trade each, hold up to 75 min (15-90 after release)")
for nev in (24, 40, 49, 54):
    for kev in (1.0, 1.5, 2.0):
        s = sig[75]*kev
        for cn, c in (("z(0.95)", z(0.95)), ("z(1-0.05/3)", Z_BONF), ("t>3.0", 3.0)):
            mde = (c+Z_B)*s/math.sqrt(nev)
            pw = {mu: 1-Phi(c - mu*math.sqrt(nev)/s) for mu in (1, 2, 5)}
            P(f"n_ev={nev} k_ev={kev} sigma={s:.2f} {cn}: MDE80={mde:.2f} ticks; power at mu=1,2,5: {pw[1]:.3f},{pw[2]:.3f},{pw[5]:.3f}")
P("events per year 15 -> test 43 months: %.2f, discovery 39: %.2f" % (15*43/12, 15*39/12))
