"""Recompute the numbers stated in protocol v0.3 P4.2, P6.1, P8 G5(d) and the proofs' compute (W3 re-check)."""
from math import comb, erf, sqrt

def binom_tail(n: int, k: int, p: float) -> float:
    return sum(comb(n, j) * p**j * (1 - p) ** (n - j) for j in range(k, n + 1))

def phi_tail(z: float) -> float:
    return 0.5 * (1 - erf(z / sqrt(2)))

print("P(>=2 of 20 | 0.05) =", round(binom_tail(20, 2, 0.05), 4))
print("P(>=14 of 20 | 0.80) =", round(binom_tail(20, 14, 0.80), 4))
print("P(>=14 of 20 | 0.91) =", round(binom_tail(20, 14, 0.91), 4))
print("300 * P(Z>5.66) =", 300 * phi_tail(5.66))
print("300 * P(Z>4.86) =", 300 * phi_tail(4.86))
print("t at SR 0.1724, T 796 =", round(0.1724 * sqrt(796), 3))
print("t at SR 0.2007, T 796 =", round(0.2007 * sqrt(796), 3))
print("1/sqrt(796) =", round(1 / sqrt(796), 4))
# selection power alone at s = 0.25 (normal days, se = sqrt((1 + s^2/2)/T))
s, T = 0.25, 796
se = sqrt((1 + s * s / 2) / T)
print("P(select | s=0.25) =", round(1 - phi_tail((s - 0.2007) / se), 3))
# fit counts
subset_cfg = 1 * 2 * 10
print("subset configurations =", subset_cfg, "; fits a search =", subset_cfg * 6)
print("40 searches fits =", 40 * subset_cfg * 6, "; 40 full searches =", 40 * 300 * 6)
print("null Sharpes =", 20 * 20)
# terciles
print("terciles:", 265, 530 - 265, 796 - 530, "sum", 265 + (530 - 265) + (796 - 530))
# folds
print("folds sum:", 133 * 4 + 132 * 2)
# feature counts
C, F1, F2, F3, F4 = 15, 8, 11, 12, 13
print("S1..S5:", C + F1, C + F2, C + F3, C + F4, C + F1 + F2 + F3 + F4, "; SFI 59x6 =", 59 * 6)
clipped = 1 + 4 + 3 + 11 + 4 + 3 + 5 + 7
unclipped = 4 + 10 + 1 + 5 + 1
print("G4 clipped", clipped, "unclipped", unclipped, "total", clipped + unclipped)
# proofs compute from P5 per-fit figures (120 fits a search: 72 LOGIT, 48 LGBM; 40 searches)
logit_fits, lgbm_fits = 40 * 72, 40 * 48
print("proof fits: LOGIT", logit_fits, "LGBM", lgbm_fits)
for label, lo_l, hi_l, lo_g, hi_g in [("P5 guesses", 10, 60, 5, 30), ("FE probes balanced", 2.4, 3.5, 8, 13), ("FE probes 99% zero", 1.9, 65.6, 8, 13)]:
    lo = (logit_fits * lo_l + lgbm_fits * lo_g) / 3600
    hi = (logit_fits * hi_l + lgbm_fits * hi_g) / 3600
    print(f"  {label}: {lo:.1f}-{hi:.1f} CPU-h; at 7 workers {lo/7:.1f}-{hi/7:.1f} h wall")
search_lo = (1080 * 10 + 720 * 5) / 3600; search_hi = (1080 * 60 + 720 * 30) / 3600
print(f"real search at P5 guesses: {search_lo:.1f}-{search_hi:.1f} CPU-h; ratio proofs/search = {4800/1800:.2f}")
# DO-15: interval overlap for FH span [t, t+h min + 1.000 s], t on a minute mark
h = 15
overlaps = []
for m in range(0, h + 2):
    a, b = m * 60.0, (m + 1) * 60.0
    ov = max(0.0, min(b, h * 60 + 1.0) - max(a, 0.0))
    overlaps.append(ov)
print("FH15 intervals with overlap > 1 s:", sum(1 for o in overlaps if o > 1.0), "; == 1 s:", sum(1 for o in overlaps if o == 1.0))
# TB example: tau + L = t + 7 min 30 s: fully covered vs >1 s intersected
end = 7 * 60 + 30.0
full = sum(1 for m in range(0, 10) if (m + 1) * 60 <= end)
inter = sum(1 for m in range(0, 10) if max(0.0, min((m + 1) * 60, end) - m * 60) > 1.0)
print("TB span ending 7m30s: fully covered", full, "; intersected >1 s", inter)
