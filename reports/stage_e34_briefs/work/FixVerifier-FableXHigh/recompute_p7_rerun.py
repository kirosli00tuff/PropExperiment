"""ProtocolReviewer-FableXHigh: recompute the ZL protocol's P7.2, L.b, P9.4 and P10.2 numbers with the
frozen functions M4 names. Opens no market data: only p7_final / p7_thresholds (program calendars) and
funnel.multiple_comparisons are imported.

    nice -n 10 uv run python reports/stage_e34_briefs/work/ProtocolReviewer-FableXHigh/recompute_p7.py
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path
from statistics import NormalDist

os.nice(10)
REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "reports/stage_e32_briefs/protocol"))

from p7_final import g4_threshold, se_sharpe  # noqa: E402
from p7_thresholds import required_sharpe, trade_dates  # noqa: E402
from funnel.multiple_comparisons import deflated_sharpe_ratio, expected_max_sharpe  # noqa: E402
from datetime import date  # noqa: E402

Z = NormalDist()
Z80 = Z.inv_cdf(0.8)
T_DISC, T_TEST = 796, 870
SIGMA_H = {15: 20.37, 30: 28.10, 60: 38.21}
out = []


def p(s: str = "") -> None:
    out.append(s)
    print(s)


# calendars
td = trade_dates(date(2020, 12, 1), date(2024, 2, 29))
tt = trade_dates(date(2017, 5, 22), date(2020, 11, 30))
p(f"trade_dates discovery {td} (T_disc {td - 20}); test MBO {tt} (T_test {tt - 20})")

for n in (838, 1038):
    v_d, v_t = 1 / (T_DISC - 1), 1 / (T_TEST - 1)
    e_n = expected_max_sharpe(n, 1.0)
    sr0 = expected_max_sharpe(n, v_d)
    g3 = required_sharpe(n, T_DISC, v_d, 0.0, 3.0)
    g3_fat = required_sharpe(n, T_DISC, v_d, -0.5, 6.0)
    t_bar = 3.0 / math.sqrt(T_TEST)
    dsr_test = required_sharpe(n, T_TEST, v_t, 0.0, 3.0)
    b_test = max(t_bar, dsr_test)
    g4 = g4_threshold(b_test, T_DISC)
    binding = max(g3, g4)
    sr80_test = b_test + Z80 * se_sharpe(b_test, T_TEST)
    sr80_disc_bind = binding + Z80 * se_sharpe(binding, T_DISC)
    sr80_disc_g3 = g3 + Z80 * se_sharpe(g3, T_DISC)
    # check DSR at g3 and b_test
    d_g3 = deflated_sharpe_ratio(g3, T_DISC, n, v_d)["deflated_sharpe_ratio"]
    d_bt = deflated_sharpe_ratio(b_test, T_TEST, n, v_t)["deflated_sharpe_ratio"]
    p(f"\n== N {n}: e(N) {e_n:.4f}; SR0 {sr0:.4f}; G3 {g3:.4f} (t {g3 * math.sqrt(T_DISC):.2f}; DSR {d_g3:.4f}); "
      f"G3 fat {g3_fat:.4f}")
    p(f"   t_bar {t_bar:.4f}; dsr_test {dsr_test:.6f}; b_test {b_test:.6f} (t {b_test * math.sqrt(T_TEST):.2f}; "
      f"DSR {d_bt:.4f}); G4 {g4:.4f} (t {g4 * math.sqrt(T_DISC):.2f}); binding {binding:.4f}")
    p(f"   SR80_test {sr80_test:.4f}; SR80 disc G3 {sr80_disc_g3:.4f}; SR80 disc binding {sr80_disc_bind:.4f}")
    # e80 at the L.b caps 17/8/4 and at 1/2/4 trades at h 30
    caps = {15: 17, 30: 8, 60: 4}
    e80_caps = {h: sr80_test * SIGMA_H[h] / math.sqrt(caps[h]) for h in caps}
    p(f"   test e80 at caps 17/8/4: {e80_caps[15]:.3f} / {e80_caps[30]:.3f} / {e80_caps[60]:.3f}")
    e80_h30 = {k: sr80_test * SIGMA_H[30] / math.sqrt(k) for k in (1, 2, 4)}
    p(f"   test e80 h30 at n 1/2/4: {e80_h30[1]:.3f} / {e80_h30[2]:.3f} / {e80_h30[4]:.3f}")
    e80_disc = {h: sr80_disc_bind * SIGMA_H[h] / math.sqrt(caps[h]) for h in caps}
    p(f"   discovery e80 (G3+G4) at caps 17/8/4: {e80_disc[15]:.3f} / {e80_disc[30]:.3f} / {e80_disc[60]:.3f}")
    e80_19 = {19: sr80_test * SIGMA_H[15] / math.sqrt(19), 9: sr80_test * SIGMA_H[30] / 3}
    p(f"   test e80 at E.32b caps 19 (h15) / 9 (h30): {e80_19[19]:.3f} / {e80_19[9]:.3f}")
    # per-trade edge at the binding threshold vs the test e80 at the same rate (M4 d, G4 vs K2)
    p(f"   ratio binding/SR80_test = {binding / sr80_test:.4f} (K2 cannot bind iff > 1)")
    # Holm K = 9 z for m = 1..3
    zs = [Z.inv_cdf(1 - 0.05 / 9 / (m)) for m in (1, 2, 3)]
    p(f"   Holm K=9 first-step z m=1/2/3: {zs[0]:.3f} / {zs[1]:.3f} / {zs[2]:.3f}")
    # P9.4 multipliers: one member at s, nulls at 0
    for k_null in (1, 2):
        vals = [1.0] + [0.0] * k_null
        m = sum(vals) / len(vals)
        pv = sum((x - m) ** 2 for x in vals) / len(vals)
        p(f"   P9.4 multiplier SR0/s with {k_null} null(s): {e_n * math.sqrt(pv):.4f}")
    # select-and-pass at s = 0.25 (P4.2 planted proof reference)
    for s in (0.20, 0.25):
        p_sel = 1 - Z.cdf((binding - s) / se_sharpe(s, T_DISC))
        p_pass = Z.cdf((s - b_test) / se_sharpe(s, T_TEST))
        p(f"   s {s:.2f}: P(select) {p_sel:.3f}, P(pass b_test) {p_pass:.3f}, product {p_sel * p_pass:.3f}")
    # analytic null false-positive rate at binding
    p(f"   200 x P(Z > binding t {binding * math.sqrt(T_DISC):.2f}) = {200 * (1 - Z.cdf(binding * math.sqrt(T_DISC))):.2e}; "
      f"200 x P(Z > G3 t) = {200 * (1 - Z.cdf(g3 * math.sqrt(T_DISC))):.2e}")

# T_test sensitivity for K2 (when does K2 bind for a G4 passer at N 1038?)
n = 1038
g4_1038 = None
for t_test in (870, 850, 800, 750, 700, 650, 600):
    v_t = 1 / (t_test - 1)
    b = max(3.0 / math.sqrt(t_test), required_sharpe(n, t_test, v_t, 0.0, 3.0))
    sr80 = b + Z80 * se_sharpe(b, t_test)
    g4 = g4_threshold(max(3.0 / math.sqrt(870), required_sharpe(n, 870, 1 / 869, 0.0, 3.0)), T_DISC)
    p(f"K2 sensitivity: T_test {t_test}: b_test {b:.4f}, SR80_test {sr80:.4f}; G4 (pinned at T_test 870) {g4:.4f}; "
      f"K2 binds for a G4 passer iff SR80_test > G4: {sr80 > g4}")

# L.b entry maxima
for h in (15, 30, 60):
    p(f"n_max(h={h}) = floor((277 - {h})/({h} + 1)) + 1 = {(277 - h) // (h + 1) + 1}; latest entry index {277 - h} "
      f"-> {8 * 60 + 35 + 277 - h:d} min of day = {(8 * 60 + 35 + 277 - h) // 60:02d}:{(8 * 60 + 35 + 277 - h) % 60:02d} CT")

# grid minutes a date
for h in (5, 15, 30, 60):
    p(f"grid minutes h {h}: {277 - h + 1}")

# feature counts and clip lists
C, F09c, F09p, F10 = 14, 8, 9, 12
p(f"sets: S_crush {C + F09c}, S_prop {C + F09p}, S_book {C + F10}, S_pool {C + F09c + F09p + F10}; "
  f"sum n_s {4 * C + 2 * (F09c + F09p + F10)}")
p(f"P10.3 rescaling: R = B + 2372.6 + 38.53 x sum n_s = {1200 + 2372.6 + 38.53 * (4 * C + 2 * (F09c + F09p + F10)):.1f} s")

# DF34 shares
p(f"share of T outside day session: {3812647 / 16019898:.4f}; records in dates {158044028} vs total {158046466}: "
  f"outside {158046466 - 158044028}")
p(f"fee ticks ZL: 5.28/6.00 = {5.28 / 6.0:.4f}; c_f = 1.0 + 0.5 + 0.88 = {1.0 + 0.5 + 0.88:.2f}; "
  f"cost per sigma_30 {2.38 / 28.10:.4f}; ZM {1.59 / 17.25:.4f}")
p(f"break-even share s_L*, D=1, m=1: {2.38 * 0.11 / (1 * 0.5):.4f}; m=2: {2.38 * 0.11 / (1 * 0.75):.4f}")

(Path(__file__).parent / "recompute_p7.out").write_text("\n".join(out) + "\n")
