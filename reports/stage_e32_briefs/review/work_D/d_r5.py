"""MathReview D: independent recomputation of R5_ml_evidence.md section B and the section E horizon table.
Closed forms under the bivariate-normal model, plus a Monte Carlo check of (B1), (B2) and (B5). Prints results only."""
import math
import numpy as np

def Phi(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))
def phi(x: float) -> float:
    return math.exp(-x * x / 2) / math.sqrt(2 * math.pi)
def Phiinv(p: float) -> float:
    lo, hi = -10.0, 10.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if Phi(mid) < p: lo = mid
        else: hi = mid
    return (lo + hi) / 2

SQ = math.sqrt(2 / math.pi)
SIG1 = 3.15
print("sqrt(2/pi) =", SQ)
print("\n== B2 hit -> rho = sin(pi(hit-1/2)) ==")
for hit in (0.51, 0.52, 0.53, 0.55):
    print(hit, round(math.sin(math.pi * (hit - 0.5)), 4))
print("B3 example rho 0.10 k 0.30: R2 =", 2 * 0.10 * 0.30 - 0.30 ** 2)

print("\n== B2 worked example (every bar, h=15): rho = G/(sigma_15 sqrt(2/pi)) ==")
s15 = SIG1 * math.sqrt(15)
for G in (1.59, 1.6, 2.8, 1.528):
    rho = G / (s15 * SQ)
    print(f"G={G}: rho={rho:.4f} R2max={rho*rho:.4f} hit={0.5 + math.asin(rho)/math.pi:.4f}")
print("check 0.2876 x 12.2 x 0.79788 =", 0.2876 * 12.2 * 0.79788, "; 290/15 =", 290 / 15)

print("\n== B3 table: h=15, 4 trades/day ==")
def thresh(h, ntr, minutes):
    sh = SIG1 * math.sqrt(h)
    nb = minutes / h
    q = ntr / nb
    c = Phiinv(1 - q / 2)
    fac = 2 * phi(c) / q
    return sh, nb, q, c, fac
for lab, minutes in (("day 290", 290), ("globex 1055", 1055)):
    sh, nb, q, c, fac = thresh(15, 4, minutes)
    print(f"{lab}: N_bars={nb:.3f} q={q:.4f} c={c:.4f} factor={fac:.4f} rho(1.6)={1.6/(sh*fac):.4f} rho(2.4)={2.4/(sh*fac):.4f} rho(2.8)={2.8/(sh*fac):.4f} rho(1.59)={1.59/(sh*fac):.4f} rho(1.528)={1.528/(sh*fac):.4f}")
print("hand: phi(1.2621) =", phi(1.2621), " 2phi/q =", 2 * phi(1.2621) / 0.2069, " 12.2 x 1.7390 =", 12.2 * 1.7390)
sh, nb, q, c, fac = thresh(15, 8, 290)
print(f"8 trades/day: q={q:.4f} c={c:.4f} factor={fac:.4f} rho: {1.6/(sh*fac):.3f} {2.4/(sh*fac):.3f} {2.8/(sh*fac):.3f}")
print("ratio every-bar/thresholded rho at 1.6:", (1.6 / (s15 * SQ)) / (1.6 / (s15 * 1.7389)))
print("top-4-of-290 one-minute points: q =", 4 / 290, " c =", Phiinv(1 - 2 / 290), " factor =", 2 * phi(Phiinv(1 - 2 / 290)) / (4 / 290))
print("R2 = rho^2 for rho 0.10, 0.13:", 0.10 ** 2, 0.13 ** 2)
print("Sharpe: 1.0/12.2*sqrt(5.5) =", 1.0 / 12.2 * math.sqrt(5.5), " 0.8/12.2*2 =", 0.8 / 12.2 * 2, " 1.2/12.2*sqrt(8) =", 1.2 / 12.2 * math.sqrt(8))

print("\n== B4 ==")
for lab, R2, h, extra in (("Gao 1.2% 30min", 0.012, 30, None), ("CRS96 3.32% 5min", 0.0332, 5, 4), ("CRS02 0.54% 5min", 0.0054, 5, 4)):
    rho = math.sqrt(R2); sh = SIG1 * math.sqrt(h)
    line = f"{lab}: rho={rho:.4f} gross every bar={rho*sh*SQ:.3f}"
    if extra:
        _, nb, q, c, fac = thresh(h, extra, 290)
        line += f" top-{extra}-of-{nb:.0f}: {rho*sh*fac:.3f}"
    print(line)

print("\n== section E horizon table: 4 trades/day in 290 min ==")
print("h sigma bars q c factor rho(1.59) rho(2.4) rho(2.8) | gross at rho .03/.05/.08/.10")
for h in (5, 15, 30, 60):
    sh, nb, q, c, fac = thresh(h, 4, 290)
    g = [rho * sh * fac for rho in (0.03, 0.05, 0.08, 0.10)]
    print(f"{h:3d} {sh:7.3f} {nb:5.2f} {q:.4f} {c:.4f} {fac:.4f} {1.59/(sh*fac):.3f} {2.4/(sh*fac):.3f} {2.8/(sh*fac):.3f} | " + " ".join(f"{x:.2f}" for x in g))
print("fine grid of h for the minimum rho(1.59) at 4 trades/day (q capped at 1):")
best = None
for h in range(5, 121, 5):
    sh = SIG1 * math.sqrt(h); nb = 290 / h; q = min(4 / nb, 1.0)
    if q >= 1.0:
        fac = SQ
    else:
        c = Phiinv(1 - q / 2); fac = 2 * phi(c) / q
    r = 1.59 / (sh * fac)
    if best is None or r < best[1]: best = (h, r)
    if h in (5, 10, 15, 20, 30, 40, 45, 50, 60, 72, 90, 120): print(f"  h={h:3d} q={q:.3f} factor={fac:.3f} rho={r:.4f}")
print("minimum at h =", best)
print("check h=30: 2.8/(17.253 x 1.3808) =", 2.8 / (17.253 * 1.3808))

print("\n== Monte Carlo check of B1, B2, B5 (rho=0.10, sigma_h=12.2, 4e6 draws) ==")
rng = np.random.default_rng(20261028)
rho = 0.10; N = 4_000_000
z = rng.standard_normal(N); e = rng.standard_normal(N)
r = 12.2 * (rho * z + math.sqrt(1 - rho * rho) * e)
print("E[r sign z] MC:", round(float(np.mean(r * np.sign(z))), 4), " formula:", round(rho * 12.2 * SQ, 4))
print("hit MC:", round(float(np.mean(np.sign(r) == np.sign(z))), 4), " formula:", round(0.5 + math.asin(rho) / math.pi, 4))
c = 1.2621; sel = np.abs(z) > c
print("q MC:", round(float(sel.mean()), 4), " E[r sign z | |z|>c] MC:", round(float(np.mean((r * np.sign(z))[sel])), 4), " formula:", round(rho * 12.2 * 2 * phi(c) / (2 * (1 - Phi(c))), 4))
print("per-trade SD given trade (MC):", round(float(np.std((r * np.sign(z))[sel])), 3))
