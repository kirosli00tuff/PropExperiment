"""MathReviewer C addendum: (1) M5a d.2 item 4 'basis invariance' of the DSR z under annualisation;
(2) trades/day implied by p7's binding test bar vs its alpha=0.05/3 power table; (3) M5b d.2 item 6 ratio."""
import math
from statistics import NormalDist
N = NormalDist(); PHI, PPF = N.cdf, N.inv_cdf
G = 0.5772156649015329
def e_n(n): return (1-G)*PPF(1-1/n) + G*PPF(1-1/(n*math.e))
def z_dsr(sr, T, v, n, g3, g4):
    sr0 = math.sqrt(v)*e_n(n); d = 1 - g3*sr + (g4-1)/4*sr*sr
    return (sr-sr0)*math.sqrt(T-1)/math.sqrt(d)
T, n, q = 816, 738, 816/3.25
sr = 0.1689
print("(1) per-trade basis: z =", round(z_dsr(sr, T, 1/T, n, 0, 3), 3), "DSR =", round(PHI(z_dsr(sr, T, 1/T, n, 0, 3)), 3))
# annualise: SR*sqrt(q), V*q, T -> years; normal returns keep g3=0,g4=3 under aggregation
za = z_dsr(sr*math.sqrt(q), T/q, q/T, n, 0, 3)
print("    annual basis (same inputs rescaled): SR_ann =", round(sr*math.sqrt(q), 3), "T =", round(T/q, 2), "years; z =", round(za, 3), "DSR =", round(PHI(za), 3))
# daily basis with 1 trade/day is identical to per-trade here; monthly basis q=12:
zm = z_dsr(sr*math.sqrt(q/12), T/(q/12), (q/12)/T, n, 0, 3)
print("    monthly basis: z =", round(zm, 3), "DSR =", round(PHI(zm), 3))
print("(2) p7 binding bar true daily SR 0.1917 -> trades/day for h=15 at mu=0.5:", round((0.1917*12.2/0.5)**2, 1),
      "; at mu=1.0:", round((0.1917*12.2/1.0)**2, 2), "; p7 power table (alpha .05/3) says 5.80 and 1.45")
print("    ratio of trades needed, bar t~4.92 vs t 3.0:", round(((4.92+0.8416)/(3.0+0.8416))**2, 2), "; vs z 2.128:", round(((4.92+0.8416)/(2.128+0.8416))**2, 2))
print("(3) ((c+0.8416)/c)^2: c=3 ->", round(((3+0.8416)/3)**2, 3), "c=2.128 ->", round(((2.128+0.8416)/2.128)**2, 3))
