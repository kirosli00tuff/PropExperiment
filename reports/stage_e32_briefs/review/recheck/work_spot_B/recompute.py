"""SpotCheck_B: recompute every number the P4-P10 hunks of protocol v0.4 state.

Reads no market data: only p7_thresholds (program calendars) and funnel.multiple_comparisons.
"""
from __future__ import annotations

import math
import sys
from datetime import date
from pathlib import Path
from statistics import NormalDist, pstdev

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "reports/stage_e32_briefs/protocol"))

from p7_final import BURN_IN, DISCOVERY, TEST_MBO, g4_threshold, se_sharpe  # noqa: E402
from p7_thresholds import N_PRIOR, required_sharpe, trade_dates  # noqa: E402
from funnel.multiple_comparisons import deflated_sharpe_ratio, expected_max_sharpe  # noqa: E402

Z = NormalDist()
N = N_PRIOR + 300
T_DISC = trade_dates(*DISCOVERY) - BURN_IN
T_TEST = trade_dates(*TEST_MBO) - BURN_IN
print(f"N={N} T_disc={T_DISC} T_test={T_TEST}")


def binom_tail(n: int, k: int, p: float) -> float:
    return sum(math.comb(n, j) * p**j * (1 - p) ** (n - j) for j in range(k, n + 1))


print(f"P(>=14 of 20 | 0.8) = {binom_tail(20, 14, 0.8):.4f}   (hunk: 0.91)")
print(f"P(>=2 of 20 | 0.05) = {binom_tail(20, 2, 0.05):.4f}")
print(f"1/sqrt(796) = {1 / math.sqrt(796):.6f}   (hunk: 0.0354)")

# P7.2 values, unrounded
v_d, v_t = 1 / (T_DISC - 1), 1 / (T_TEST - 1)
g3 = required_sharpe(N, T_DISC, v_d, 0.0, 3.0)
t_bar = 3.0 / math.sqrt(T_TEST)
dsr_test = required_sharpe(N, T_TEST, v_t, 0.0, 3.0)
b_test = max(t_bar, dsr_test)
g4 = g4_threshold(b_test, T_DISC)
g4_alt = g4_threshold(t_bar, T_DISC)
print(f"G3 = {g3:.6f}; t_bar = {t_bar:.6f}; b_test unrounded = {b_test:.6f} (hunk 0.164882)")
print(f"G4 = {g4:.6f} (hunk 0.2007 / W1 0.200703); G4 at 0.1649 = {g4_threshold(0.1649, T_DISC):.6f}")
print(f"drop branch: b_test {t_bar:.4f}, G4 {g4_alt:.4f} (hunk 0.1373), sel {max(g3, g4_alt):.4f} (hunk 0.1724)")
print(f"DSR at b_test unrounded: {deflated_sharpe_ratio(b_test, N, T_TEST, v_t, 0.0, 3.0)}; "
      f"at 0.1649: {deflated_sharpe_ratio(0.1649, N, T_TEST, v_t, 0.0, 3.0)}")

# selection alone and joint at s = 0.25
sel = max(g3, g4)
s = 0.25
p_sel = 1 - Z.cdf((sel - s) / se_sharpe(s, T_DISC))
p_pass = Z.cdf((s - b_test) / se_sharpe(s, T_TEST))
print(f"s=0.25: P(select) = {p_sel:.4f} (hunk 'about 0.92'); P(pass) = {p_pass:.4f}; joint = {p_sel * p_pass:.4f} (hunk 0.91)")

# AR-1: E[max] multiplier and companion cases at the test (T_test), V = pvariance of tested Sharpes
mult = expected_max_sharpe(N, 1.0)
print(f"E[max] multiplier at N {N}, V 1: {mult:.4f} (hunk 3.2045)")
for label, shs in (("one null", [0.25, 0.0]), ("two nulls", [0.25, 0.0, 0.0])):
    sd = pstdev(shs)
    print(f"  {label}: SR0/s = {mult * sd / 0.25:.3f}")


def needed(sr0: float, t: int) -> float:
    lo, hi = 0.0, 2.0
    for _ in range(200):
        mid = (lo + hi) / 2
        z = (mid - sr0) * math.sqrt(t - 1) / math.sqrt(1 + mid * mid / 2)
        if Z.cdf(z) > 0.95:
            hi = mid
        else:
            lo = mid
    return hi


for strong, weak in ((0.25, 0.15), (0.25, 0.10)):
    sr0 = mult * pstdev([strong, weak])
    need = needed(sr0, T_TEST)
    p = Z.cdf((strong - need) / se_sharpe(strong, T_TEST))
    print(f"  ({strong}, {weak}): SR0 = {sr0:.3f}, needs {need:.3f}, passes with {p:.2f}")

# compute figures in P5
logit_fits, lgbm_fits = 12 * 6 * 40, 8 * 6 * 40
print(f"proof fits: LOGIT {logit_fits}, LGBM {lgbm_fits}, total {logit_fits + lgbm_fits}; ratio to 1800 = {(logit_fits + lgbm_fits) / 1800:.2f}")
for name, (lo_l, hi_l), (lo_g, hi_g) in (("P5 guesses", (10, 60), (5, 30)), ("balanced probes", (2.4, 3.5), (8, 13))):
    lo = (logit_fits * lo_l + lgbm_fits * lo_g) / 3600
    hi = (logit_fits * hi_l + lgbm_fits * hi_g) / 3600
    print(f"  {name}: {lo:.1f}-{hi:.1f} CPU-h; at 7 procs {lo / 7:.1f}-{hi / 7:.1f} h wall")
print(f"search LOGIT 1080 fits x 10-60 s = {1080 * 10 / 3600:.0f}-{1080 * 60 / 3600:.0f} CPU-h; LGBM 720 x 5-30 s = {720 * 5 / 3600:.0f}-{720 * 30 / 3600:.0f}")

# calendar months in the two windows
def months(a: date, b: date) -> int:
    return (b.year - a.year) * 12 + b.month - a.month + 1


print(f"months discovery = {months(*DISCOVERY)} (39); months test = {months(*TEST_MBO)} (hunk 43)")
# fold 6 training set
blocks = [133, 133, 133, 133, 132, 132]
print(f"fold sizes: {[796 - b - (21 if k < 5 else 0) for k, b in enumerate(blocks)]} (hunk fold 6 = 664)")
