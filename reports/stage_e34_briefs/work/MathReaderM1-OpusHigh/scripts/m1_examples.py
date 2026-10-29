"""M1 worked-example arithmetic (no market data read). Inputs: shared ZL facts and E.32 data facts counts."""
import math
from statistics import NormalDist
nd = NormalDist()
z90 = nd.inv_cdf(0.95)
k_all = math.sqrt(2 / math.pi)
k_top = nd.pdf(z90) / 0.05
print(f"z90={z90:.4f} E|Z|={k_all:.4f} topdecile={k_top:.4f}")
sig = {15: 20.37, 30: 28.10, 60: 38.21}
e80t = {15: 0.90, 30: 1.81, 60: 3.70}
cf = 2.38
for h, s in sig.items():
    r_all = (cf / (s * k_all)) ** 2
    r_top = (cf / (s * k_top)) ** 2
    r_top80 = ((cf + e80t[h]) / (s * k_top)) ** 2
    print(f"h{h} sigma {s} R2_all {r_all:.5f} R2_top {r_top:.5f} R2_top(c_f+e80_test {cf+e80t[h]:.2f}) {r_top80:.5f}")
# OFI forward bound R2_pred = rho^2 R2_c
for rho in (0.05, 0.1, 0.2):
    print(f"rho {rho} R2_pred {rho**2*0.65:.5f}")
# message rates: per-date medians/min of whole trade-date window (E.32 data facts 3.1)
T = {"min": 6998, "median": 19195, "p90": 25760, "max": 40543}
E = {"min": 54999, "median": 168917, "p90": 225487, "max": 448862}
for s in (0.70, 0.83, 1.00):
    print(f"day share {s}: T/min " + " ".join(f"{k} {v*s/290:.1f}" for k, v in T.items())
          + " | events/s " + " ".join(f"{k} {v*s/290/60:.2f}" for k, v in E.items()))
# trade-sign imbalance noise: iid SE = 1/sqrt(n); long memory N_e(n) = 1 + C0/(1-g) n^(1-g)
def ne(n, c0, g):
    """Var(sum of n signs)/n for sign autocorrelation c0 * l^-g: 1 + 2 sum_{l<n} (1 - l/n) c0 l^-g."""
    return 1 + 2 * sum(c0 * (1 - l / n) * l ** (-g) for l in range(1, n))
for kmin in (1, 5, 15, 30, 60):
    row = []
    for label, rate in (("quiet", 6998 * 0.83 / 290), ("median", 19195 * 0.83 / 290)):
        n = max(1, round(rate * kmin))
        se_iid = 1 / math.sqrt(n)
        se_lm = math.sqrt(ne(n, 0.2, 0.5) / n)
        p0 = math.exp(-n)
        row.append(f"{label} n {n} SEiid {se_iid:.3f} SElm {se_lm:.3f} P(empty) {p0:.1e}")
    print(f"k {kmin}: " + " ; ".join(row))
# side-N share of ZL T records (E.32 data facts 3.2)
a, b, nn = 7250840, 7160339, 1608719
print(f"ZL T total {a+b+nn} side N share {nn/(a+b+nn):.4f}")
print(f"records per event ZL {158046466/142061153:.3f}")
# costs
print(f"MBO both {19.48+21.48:.2f} MBP1 both {0+23.36:.2f} diff {19.48+21.48-23.36:.2f} mixed {21.48:.2f}")
# OFI stylized example: D=30 per side
D = 30
print(f"one tick needs OFI {2*D}; OFI +120 -> {120/(2*D):.2f} ticks = USD {120/(2*D)*6:.2f}")
print(f"sigma30 USD {28.10*6:.2f}; c_f USD {2.38*6:.2f}")
