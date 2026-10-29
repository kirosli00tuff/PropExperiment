"""FixVerifier-FableXHigh: extra recomputations with the frozen functions (no market data)."""
from __future__ import annotations
import math, os, sys
from pathlib import Path
from statistics import NormalDist
os.nice(10)
REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "reports/stage_e32_briefs/protocol"))
from p7_final import g4_threshold, se_sharpe
from p7_thresholds import required_sharpe
from funnel.multiple_comparisons import expected_max_sharpe
Z = NormalDist(); Z80 = Z.inv_cdf(0.8)
T_DISC, T_TEST = 796, 870
def thresholds(n, t_test=T_TEST, skew=0.0, kurt=3.0):
    v_d, v_t = 1/(T_DISC-1), 1/(t_test-1)
    g3 = required_sharpe(n, T_DISC, v_d, skew, kurt)
    b_test = max(3.0/math.sqrt(t_test), required_sharpe(n, t_test, v_t, skew, kurt))
    g4 = g4_threshold(b_test, T_DISC, skew, kurt)
    sr80 = b_test + Z80*se_sharpe(b_test, t_test, skew, kurt)
    return g3, b_test, g4, max(g3, g4), sr80
for n in (838, 1038):
    g3, b, g4, binding, sr80 = thresholds(n)
    print(f"N {n}: G3 {g3:.4f} b_test {b:.6f} G4 {g4:.4f} binding {binding:.4f} SR80_test {sr80:.4f}; z binding {binding*math.sqrt(T_DISC):.3f}")
    # exact SR80 by bisection: s - z80 se(s,T) = b
    lo, hi = b, 1.0
    for _ in range(200):
        mid = (lo+hi)/2
        if mid - Z80*se_sharpe(mid, T_TEST) >= b: hi = mid
        else: lo = mid
    print(f"   exact SR80 (bisection) {hi:.4f} vs bar-se form {sr80:.4f}")
    # select-and-pass at s = 0.25 (independent formula)
    s = 0.25
    p_sel = 1 - Z.cdf((binding - s)/se_sharpe(s, T_DISC)); p_pass = Z.cdf((s - b)/se_sharpe(s, T_TEST))
    print(f"   s 0.25: P(select) {p_sel:.4f} P(pass) {p_pass:.4f} product {p_sel*p_pass:.4f}")
    # fat tails vs normal
    for (sk, ku) in ((-0.5, 6.0), (0.0, 10.0), (0.0, 20.0), (-2.0, 30.0)):
        g3f, bf, g4f, bindf, sr80f = thresholds(n, skew=sk, kurt=ku)
        print(f"   tails skew {sk} kurt {ku}: binding {bindf:.4f} ({100*(bindf/binding-1):+.1f}%), SR80_test {sr80f:.4f} ({100*(sr80f/sr80-1):+.1f}%)")
# exact K2 trigger at N 1038: smallest T_test at which SR80_test(T) <= G4 (pinned at T_test 870)
n = 1038
_, _, g4_pin, _, _ = thresholds(n)
first_nonbind = None
for t in range(600, 871):
    _, _, _, _, sr80_t = thresholds(n, t_test=t)
    if sr80_t <= g4_pin and first_nonbind is None: first_nonbind = t
print(f"K2 at N 1038: G4 pinned {g4_pin:.4f}; SR80_test(T) <= G4 first at T_test = {first_nonbind} (binds for T_test <= {first_nonbind-1}); 870 x (0.1957/0.2028)^2 = {870*(0.1957/0.2028)**2:.1f}")
for t in (805, 809, 810, 811, 815):
    print(f"   T_test {t}: SR80_test {thresholds(n, t_test=t)[4]:.4f}")
