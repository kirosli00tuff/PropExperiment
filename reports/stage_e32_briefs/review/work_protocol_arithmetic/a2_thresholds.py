"""ArithmeticReviewer (E.32 ProtocolReview, arithmetic lens): every number of P0.4, P3.1, P4.2, P7 and P8
recomputed from first principles (own closed forms with statistics.NormalDist) and, where the protocol
names the program's function, with funnel.multiple_comparisons as well. No data is read.

    uv run python reports/stage_e32_briefs/review/work_protocol_arithmetic/a2_thresholds.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path
from statistics import NormalDist

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))

from funnel.multiple_comparisons import deflated_sharpe_ratio, expected_max_sharpe  # noqa: E402

Z = NormalDist()
GAMMA = 0.5772156649015329
N_PRIOR, BUDGET = 538, 300
N = N_PRIOR + BUDGET
T_DISC, T_TEST = 796, 870
SIG1 = 3.15
FEE = 0.528


def section(title: str) -> None:
    print(f"\n== {title}")


def emax_own(n: int, v: float) -> float:
    """Bailey & Lopez de Prado eq. 3, own implementation."""
    return math.sqrt(v) * ((1 - GAMMA) * Z.inv_cdf(1 - 1 / n) + GAMMA * Z.inv_cdf(1 - 1 / (n * math.e)))


def dsr_own(sr: float, t: int, n: int, v: float, g3: float = 0.0, g4: float = 3.0) -> float:
    den = math.sqrt(1 - g3 * sr + (g4 - 1) / 4 * sr * sr)
    return Z.cdf((sr - emax_own(n, v)) * math.sqrt(t - 1) / den)


def se_sr(sr: float, t: int, g3: float = 0.0, g4: float = 3.0) -> float:
    return math.sqrt((1 - g3 * sr + (g4 - 1) / 4 * sr * sr) / (t - 1))


def required_sr(t: int, n: int, v: float, g3: float = 0.0, g4: float = 3.0, fn=dsr_own) -> float:
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if fn(mid, t, n, v, g3, g4) >= 0.95:
            hi = mid
        else:
            lo = mid
    return hi


def dsr_prog(sr, t, n, v, g3=0.0, g4=3.0):
    return deflated_sharpe_ratio(sr, t, n, v, g3, g4)["deflated_sharpe_ratio"]


def g4_threshold(b: float, t: int, g3: float = 0.0, g4: float = 3.0) -> float:
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if mid - se_sr(mid, t, g3, g4) >= b:
            hi = mid
        else:
            lo = mid
    return hi


def binom_tail(n: int, p: float, k: int) -> float:
    return sum(math.comb(n, j) * p**j * (1 - p) ** (n - j) for j in range(k, n + 1))


# ---------------------------------------------------------------- P7.2 discovery ----
section("P7.2 discovery thresholds, N = %d, T_disc = %d" % (N, T_DISC))
v_d = 1 / (T_DISC - 1)
sr0_own, sr0_prog = emax_own(N, v_d), expected_max_sharpe(N, v_d)
print(f"SR0 own {sr0_own:.5f}  program {sr0_prog:.5f}  (z1 {Z.inv_cdf(1 - 1 / N):.4f}, z2 {Z.inv_cdf(1 - 1 / (N * math.e)):.4f})")
g3_own = required_sr(T_DISC, N, v_d)
g3_prog = required_sr(T_DISC, N, v_d, fn=dsr_prog)
print(f"G3 normal: own {g3_own:.5f} program {g3_prog:.5f}; t = SR sqrt(T) = {g3_own * math.sqrt(T_DISC):.3f}; "
      f"annualised {g3_own * math.sqrt(252):.3f}")
closed = sr0_own + Z.inv_cdf(0.95) / math.sqrt(T_DISC - 1)
print(f"closed form ignoring the SR^2 term: {closed:.5f} (shows the denominator adds {g3_own - closed:.5f})")
g3_fat_own = required_sr(T_DISC, N, v_d, -0.5, 6.0)
g3_fat_prog = required_sr(T_DISC, N, v_d, -0.5, 6.0, fn=dsr_prog)
print(f"G3 skew -0.5 kurt 6 (raw): own {g3_fat_own:.5f} program {g3_fat_prog:.5f}")
g3_fat_excess = required_sr(T_DISC, N, v_d, -0.5, 9.0, fn=dsr_prog)
print(f"  (if 6 were read as EXCESS kurtosis, raw 9: {g3_fat_excess:.5f})")
print(f"DSR of the discovery series at exactly SR = 0.1724: program {dsr_prog(0.1724, T_DISC, N, v_d):.5f}, "
      f"0.1723: {dsr_prog(0.1723, T_DISC, N, v_d):.5f}")

# ---------------------------------------------------------------- P7.2 test bar ----
section("P7.2 test bar, T_test = %d" % T_TEST)
v_t = 1 / (T_TEST - 1)
t_bar = 3.0 / math.sqrt(T_TEST)
sr0_t = emax_own(N, v_t)
dsr_t_own = required_sr(T_TEST, N, v_t)
dsr_t_prog = required_sr(T_TEST, N, v_t, fn=dsr_prog)
b_test = max(t_bar, dsr_t_own)
print(f"t > 3.0 bar {t_bar:.5f}; SR0_test {sr0_t:.5f}; DSR bar own {dsr_t_own:.5f} program {dsr_t_prog:.5f} "
      f"(t {dsr_t_own * math.sqrt(T_TEST):.3f}); b_test {b_test:.5f}; annualised {b_test * math.sqrt(252):.3f}")
s80 = b_test + Z.inv_cdf(0.8) * se_sr(b_test, T_TEST)
print(f"80% power true SR at b_test: {s80:.5f} (se at b_test {se_sr(b_test, T_TEST):.5f})")
# power as the protocol computes it (se at the TRUE s) versus se at the bar
print("power check: P(SR_hat >= b_test | s = 0.1936) =",
      f"{Z.cdf((0.1936 - b_test) / se_sr(0.1936, T_TEST)):.4f}")

# ---------------------------------------------------------------- G4 ----
section("G4 power gate")
g4 = g4_threshold(b_test, T_DISC)
print(f"G4 threshold {g4:.5f}; check SR - se = {g4 - se_sr(g4, T_DISC):.5f}; t {g4 * math.sqrt(T_DISC):.3f}; "
      f"annualised {g4 * math.sqrt(252):.3f}; se at G4 {se_sr(g4, T_DISC):.5f}")
g4_alt = g4_threshold(t_bar, T_DISC)
print(f"if the test DSR is dropped: b_test {t_bar:.5f}, G4 {g4_alt:.5f}, selection max(G3, G4) {max(g3_own, g4_alt):.5f}")
print(f"G4 with skew -0.5, kurt 6 moments: {g4_threshold(b_test, T_DISC, -0.5, 6.0):.5f}")
sel = max(g3_own, g4)
print(f"binding selection threshold {sel:.5f}")

# ---------------------------------------------------------------- power tables ----
section("power tables (normal days)")
print("true s | P(pass t>3) | P(pass b_test) | P(select) | product")
for s in (0.10, 0.12, 0.15, 0.17, 0.20, 0.25, 0.30):
    p_t = Z.cdf((s - t_bar) / se_sr(s, T_TEST))
    p_b = Z.cdf((s - b_test) / se_sr(s, T_TEST))
    p_sel = 1 - Z.cdf((sel - s) / se_sr(s, T_DISC))
    print(f"{s:.2f} | {p_t:.3f} | {p_b:.3f} | {p_sel:.3f} | {p_sel * p_b:.3f}")

# ---------------------------------------------------------------- per-trade edge ----
section("per-trade net edge mu = s sigma_h / sqrt(n), sigma_h = 3.15 sqrt(h)")
grid = {5: 273, 15: 263, 30: 248, 60: 218}
for h in (5, 15, 30, 60):
    sig = SIG1 * math.sqrt(h)
    row = []
    for n in (1, 2, 4, 8, 12):
        if n > grid[h] // h:
            continue
        row.append(f"n={n}: {sel * sig / math.sqrt(n):.2f} / {s80 * sig / math.sqrt(n):.2f}")
    print(f"h={h} sigma_h {sig:.2f}: " + "; ".join(row))
print(f"P4.2 planted size: s 0.25, h 15, 4 trades: mu = {0.25 * SIG1 * math.sqrt(15) / 2:.3f} ticks")
print(f"at the G1 floor (trades on 50% of dates, n on those): mu scales by 1/sqrt(0.5) = {1 / math.sqrt(0.5):.3f}")

# ---------------------------------------------------------------- reference z ----
section("reference thresholds over 300 (one-sided 0.05)")
c300 = sum(1 / j for j in range(1, 301))
for name, a in (("Bonferroni/Holm step 1, m=300", 0.05 / 300), ("Bonferroni m=838", 0.05 / N),
                (f"BY rank 1, c(300)={c300:.4f}", 0.05 / (300 * c300)), ("Holm K=9", 0.05 / 9),
                ("HLZ t>3", 1 - Z.cdf(3.0))):
    print(f"{name}: alpha {a:.3e} z {Z.inv_cdf(1 - a):.4f}")

# ---------------------------------------------------------------- P4.2 ----
section("P4.2 synthetic-proof numbers")
z_g3 = g3_own * math.sqrt(T_DISC)
p_one = 1 - Z.cdf(z_g3)
print(f"P(Z > {z_g3:.3f}) = {p_one:.3e}; x 300 = {300 * p_one:.3e}; exact null P(DSR >= 0.95) one config = "
      f"{1 - Z.cdf(sr0_own * math.sqrt(T_DISC - 1) + Z.inv_cdf(0.95)):.3e}")
print(f"P(>= 2 of 20 | 0.05) = {binom_tail(20, 0.05, 2):.4f}; P(>= 14 of 20 | 0.8) = {binom_tail(20, 0.8, 14):.4f}; "
      f"P(>= 14 of 20 | 0.91) = {binom_tail(20, 0.91, 14):.4f}")
print("what the null proof can rule out: P(<= 1 of 20 non-empty | true rate r):",
      ", ".join(f"r={r}: {1 - binom_tail(20, r, 2):.3f}" for r in (0.05, 0.10, 0.15, 0.20)))
print("exact-binomial 95% upper bound on the rate after 1 of 20:",
      f"{max(r / 1000 for r in range(1, 1000) if 1 - binom_tail(20, r / 1000, 2) >= 0.05):.3f}")

# ---------------------------------------------------------------- misc P0/P2/P3/P8 ----
section("P0.4, P2, P3.1, P8 figures")
print(f"1.59 = 0.528 + 1.000 + 0.062: {0.528 + 1.0 + 0.062:.3f}")
for h in (1, 5, 15):
    e_abs = SIG1 * math.sqrt(h) * math.sqrt(2 / math.pi)
    print(f"M3 f.3 sign-classifier hit rate at h={h}: 0.5 + 1.59/(2 E|dM|) = {0.5 + 1.59 / (2 * e_abs):.4f}")
print(f"crush: 2.2 = 44/2000 x 100 = {44 / 2000 * 100}; ZM tick 0.10 USD/ton x 2.2 = {0.10 * 2.2:.2f} c/bu; "
      f"1 c of crush = {1 / 0.22:.3f} ZM ticks; 70% rule: 1.59 / 4.545 / (1 - 0.5) = {1.59 / (1 / 0.22) / 0.5:.3f}")
print(f"G2 margin: 0.920 - 0.528 = {0.920 - 0.528:.3f}; 0.50 - 0.392 = {0.50 - 0.392:.3f}")
print("fees in ticks from USD/10:", {k: v / 10 for k, v in
                                     {"Topstep": 5.28, "Lucid": 5.60, "Lucid-u": 9.20, "Bulenox": 5.72,
                                      "MFFU": 6.12, "Tradeify": 9.20}.items()})
print(f"R4: 24.4/sqrt(24) = {24.4 / math.sqrt(24):.2f} SE -> 2 SE = {2 * 24.4 / math.sqrt(24):.1f} ticks; "
      f"R3a: (2 x 24.40 / 1.59)^2 = {(2 * 24.40 / 1.59) ** 2:.0f} events")
print(f"P6.4 limit timeout min(60 s, h/5 min): " + ", ".join(f"h={h}: {min(60, h / 5 * 60):.0f} s" for h in (5, 15, 30, 60)))

# ---------------------------------------------------------------- SD convention ----
section("sample vs population SD (P6.2 says sample; moments() uses population)")
ratio = math.sqrt((T_DISC - 1) / T_DISC)
print(f"SR_sample = SR_pop x sqrt((T-1)/T) = SR_pop x {ratio:.6f}; at SR_pop = G4 {g4:.5f}: SR_sample = {g4 * ratio:.5f} "
      f"(gap {g4 - g4 * ratio:.2e}, against the tie tolerance 1e-4 and G7's 1e-9)")
print(f"program t = mean/(pstdev/sqrt(n)) = SR_pop sqrt(n); with the sample SD t = SR_pop sqrt(n-1): "
      f"3.0 bar in SR_pop units 3/sqrt(870) = {3 / math.sqrt(870):.5f} vs 3/sqrt(869) x sqrt(869/870)... "
      f"(the t > 3.0 bar itself is unchanged; only the SR label moves)")

# ---------------------------------------------------------------- se convention vs DSR ----
section("G4 se versus the DSR denominator (program convention)")
for sr, g3s, g4s in ((0.2007, 0.0, 3.0), (0.2007, -0.5, 6.0)):
    d = deflated_sharpe_ratio(sr, T_DISC, N, v_d, g3s, g4s)
    den_from_z = (sr - d["expected_max_sharpe_under_null"]) * math.sqrt(T_DISC - 1) / d["z"]
    print(f"SR {sr} skew {g3s} kurt {g4s}: program denominator {den_from_z:.6f}; "
          f"se formula x sqrt(T-1) = {se_sr(sr, T_DISC, g3s, g4s) * math.sqrt(T_DISC - 1):.6f}")
