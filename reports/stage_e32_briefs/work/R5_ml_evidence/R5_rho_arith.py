"""R5 arithmetic: rho -> gross edge per trade, sign and thresholded strategies, standard ZM numbers.
No data read. Inputs are the stage's standard numbers (A0 Table 1, E.28 ranking row 130)."""
from math import sqrt, pi, asin, sin, exp
from statistics import NormalDist
N = NormalDist()
phi = lambda x: exp(-x * x / 2) / sqrt(2 * pi)
SIG1 = 3.15          # ticks, ZM sigma_1m (A0 Table 1)
BE = 1.59            # ticks, E.28 ranking row 130 mu*_mkt (brief rounds to 1.6)
def sig(h): return SIG1 * sqrt(h)
def sel_factor(q):   # E|Z| given |Z|>c, trade fraction q
    c = N.inv_cdf(1 - q / 2)
    return c, 2 * phi(c) / q
print("sqrt(2/pi) =", round(sqrt(2 / pi), 5))
for h in (5, 15, 60):
    print(f"sigma_{h} = {sig(h):.3f}")
s15 = sig(15)
print("\n== sign-of-forecast, every non-overlapping 15-min bar ==")
for G in (1.59, 1.6, 2.4, 2.8):
    rho = G / (s15 * sqrt(2 / pi))
    print(f"G={G}: rho={rho:.4f} R2max={rho**2:.4f} hit={0.5+asin(rho)/pi:.4f}")
print("\n== thresholded, 4 trades/day ==")
for label, minutes in (("day 08:30-13:20 (290 min)", 290), ("full 17h35m (1055 min)", 1055)):
    nb = minutes / 15
    q = 4 / nb
    c, k = sel_factor(q)
    print(f"{label}: bars={nb:.3f} q={q:.4f} c={c:.4f} E|Z| | trade={k:.4f}")
    for G in (1.6, 2.4, 2.8):
        rho = G / (s15 * k)
        print(f"   G={G}: rho={rho:.4f} R2max={rho**2:.5f} hit(all bars)={0.5+asin(rho)/pi:.4f}")
print("\n== 8 trades/day, day session ==")
q = 8 / (290 / 15); c, k = sel_factor(q)
print(f"q={q:.4f} c={c:.4f} k={k:.4f}", [round(G / (s15 * k), 4) for G in (1.6, 2.4, 2.8)])
print("\n== what literature R2 implies (rho >= sqrt(R2)), gross edge, ZM ==")
for name, R2, h in (("Gao SPY OOS 1.2% (30m)", 0.012, 30), ("CRS 1996 5m 3.32%", 0.0332, 5),
                    ("CRS 2002 5m 0.54%", 0.0054, 5), ("Chinco dR2 1.2pt (1m)", 0.012, 1)):
    rho = sqrt(R2); s = sig(h)
    q = 4 / (290 / h); c, k = sel_factor(min(q, 1.0)) if q < 1 else (0, sqrt(2/pi))
    print(f"{name}: rho={rho:.4f} sign-every-bar G={rho*s*sqrt(2/pi):.3f} 4/day G={rho*s*k:.3f} (q={q:.4f})")
print("\n== hit rate -> rho ==")
for hit in (0.51, 0.52, 0.53, 0.55):
    print(hit, round(sin(pi * (hit - 0.5)), 4))
print("\n== daily Sharpe check: net 1.0 tick, 4-8 trades ==")
for n in (4, 5.5, 8):
    for net in (0.8, 1.0, 1.2):
        print(n, net, round(net / s15 * sqrt(n), 4))
print("\n== OOS R2 vs rho for overdispersed forecast: R2 = 2 rho k - k^2, k=sd_f/sd_r ==")
for rho in (0.05, 0.1):
    for k in (rho, 2 * rho, 3 * rho):
        print(rho, round(k, 3), round(2 * rho * k - k * k, 5))
