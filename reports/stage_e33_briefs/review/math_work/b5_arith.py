"""Own recomputation of the P7.2 thresholds at N = 838 and the P4.2 figures (no import of p7_final or funnel)."""
import math
from statistics import NormalDist
Z = NormalDist()
G = 0.5772156649015329  # Euler-Mascheroni
def sr0(n, V):  # Bailey & Lopez de Prado E[max SR] of n null trials with Sharpe variance V
    return math.sqrt(V) * ((1 - G) * Z.inv_cdf(1 - 1 / n) + G * Z.inv_cdf(1 - 1 / (n * math.e)))
def dsr_z(sr, sr0_, T, skew=0.0, kurt=3.0):
    return (sr - sr0_) * math.sqrt(T - 1) / math.sqrt(1 - skew * sr + (kurt - 1) / 4 * sr * sr)
def solve(f, lo=0.0, hi=1.0):
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) >= 0: hi = mid
        else: lo = mid
    return hi
N, Td, Tt = 838, 796, 870
Vd, Vt = 1 / (Td - 1), 1 / (Tt - 1)
s0d = sr0(N, Vd); s0t = sr0(N, Vt)
z95 = Z.inv_cdf(0.95)
g3 = solve(lambda s: dsr_z(s, s0d, Td) - z95)
g3fat = solve(lambda s: dsr_z(s, s0d, Td, -0.5, 6.0) - z95)
tbar = 3.0 / math.sqrt(Tt)
dsr_t = solve(lambda s: dsr_z(s, s0t, Tt) - z95)
btest = max(tbar, dsr_t)
se = lambda s, T: math.sqrt((1 + 0.5 * s * s) / (T - 1))
g4 = solve(lambda s: s - se(s, Td) - btest)
g4alt = solve(lambda s: s - se(s, Td) - tbar)
print(f"SR0 multiplier (E[max]/sqrt V) at N {N}: {s0d / math.sqrt(Vd):.4f}")
print(f"SR0_disc {s0d:.6f}  (protocol 0.1137)")
print(f"G3 {g3:.6f} t {g3 * math.sqrt(Td):.3f} ann {g3 * math.sqrt(252):.3f} (protocol 0.1724, 4.86, 2.74); fat-tailed {g3fat:.6f} (0.1756)")
print(f"t>3 bar {tbar:.6f} (0.1017); test DSR bar {dsr_t:.6f} t {dsr_t * math.sqrt(Tt):.3f} (0.1649, 4.86); b_test {btest:.6f} (0.164882) ann {btest * math.sqrt(252):.3f} (2.62)")
print(f"G4 {g4:.6f} t {g4 * math.sqrt(Td):.3f} ann {g4 * math.sqrt(252):.3f} (0.2007, 5.66, 3.19); G4 if DSR dropped {g4alt:.6f} (0.1373)")
s80 = solve(lambda s: Z.cdf((s - btest) / se(s, Tt)) - 0.8)
print(f"80% power true Sharpe at b_test {s80:.6f} (0.1936)")
sel = max(g3, g4)
for s in (0.15, 0.17, 0.20, 0.25):
    psel = 1 - Z.cdf((sel - s) / se(s, Td)); ppass = Z.cdf((s - btest) / se(s, Tt))
    print(f"  s {s}: P(select) {psel:.4f} P(pass) {ppass:.4f} product {psel * ppass:.4f}")
# per-trade edges: daily SR = mu sqrt(n)/sigma_h, sigma_h = 3.15 sqrt(h)
for h, n in ((5, 4), (5, 8), (15, 4), (15, 8), (30, 4), (60, 2)):
    print(f"  h {h} n {n}: mu at selection {sel * 3.15 * math.sqrt(h) / math.sqrt(n):.3f} ticks")
# P4.2 binomials and analytic rates
from math import comb
p2 = sum(comb(20, k) * 0.05 ** k * 0.95 ** (20 - k) for k in range(2, 21))
p14 = sum(comb(20, k) * 0.8 ** k * 0.2 ** (20 - k) for k in range(14, 21))
print(f"P(>=2 of 20 | 0.05) {p2:.4f} (0.26); P(>=14 of 20 | 0.8) {p14:.4f} (0.91)")
print(f"300 P(Z>5.66) {300 * (1 - Z.cdf(5.66)):.3e} (2e-6); 300 P(Z>4.86) {300 * (1 - Z.cdf(4.86)):.3e} (2e-4); exact z of G4: {g4 * math.sqrt(Td):.4f}, of G3: {g3 * math.sqrt(Td):.4f}")
print(f"300 P(Z>z_G4 exact) {300 * (1 - Z.cdf(g4 * math.sqrt(Td))):.3e}; 300 P(Z>z_G3 exact) {300 * (1 - Z.cdf(g3 * math.sqrt(Td))):.3e}")
print(f"1/sqrt(796) {1 / math.sqrt(796):.6f} (0.0354)")
# per-seed power implied by the selection threshold alone at a realised Sharpe s: solve P(select) = 0.8
s_pow80 = solve(lambda s: (1 - Z.cdf((sel - s) / se(s, Td))) - 0.8)
print(f"realised daily Sharpe giving P(SR_d >= {sel:.4f}) = 0.8: {s_pow80:.4f}; at s = 0.25: {1 - Z.cdf((sel - 0.25) / se(0.25, Td)):.4f}")
# reference z's
byc = sum(1 / j for j in range(1, 301))
for name, a in (("Bonf/Holm 300", 0.05 / 300), ("Bonf 838", 0.05 / 838), ("BY 300", 0.05 / (300 * byc)), ("Holm K=9 m=1", 0.05 / 9), ("Holm K=9 m=2", 0.05 / 18), ("Holm K=9 m=3", 0.05 / 27), ("HLZ", 1 - Z.cdf(3.0))):
    print(f"  {name}: z {Z.inv_cdf(1 - a):.3f}")
print(f"c(300) {byc:.3f}")
# V14(c) remark: SR0 = 3.2045 x pstdev of the tested Sharpes; with one null companion: pstdev of (S, 0) = S/2 -> SR0 = 1.602 S; two nulls (S,0,0): pstdev = S sqrt(2)/3 -> {:.3f} S
print(f"one null companion: SR0/S = {s0d / math.sqrt(Vd) / 2:.3f} (1.60); two nulls: {s0d / math.sqrt(Vd) * math.sqrt(2) / 3:.3f} (1.51)")
