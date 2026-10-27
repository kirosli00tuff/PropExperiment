"""E.32 Part P, P7/P8: the frozen thresholds for E.33's search (no data read).

    uv run python reports/stage_e32_briefs/protocol/p7_final.py --budget 300 --out FILE

Supersedes the bar sections of p7_thresholds.py (kept unchanged, reviewed by MathReviewer C): one
test bar is used everywhere (MathReview C-10). Inputs fixed by the protocol:

- N after E.33 = 538 + budget (literal N, V43).
- Discovery: 816 program trade dates 2020-12-01..2024-02-29, minus a 20-date feature burn-in
  -> T_disc = 796 OOF dates.
- Test: ZM MBO exists from trade date 2017-05-22 (Databento GLBX.MDP3: MBO from 2017-05-21);
  2017-05-22..2020-11-30 = 890 program trade dates, minus the same 20-date burn-in -> T_test = 870.
- Discovery gate G3: DSR >= 0.95 at N, V = 1/(T_disc - 1), the candidate's own moments.
- Test bar b_test (daily Sharpe): max(t > 3.0, DSR >= 0.95 at N with V = 1/(T_test - 1)); the
  program verdict's own DSR (pvariance over the tested Sharpes) is applied as well but is not
  known before the read.
- Power gate G4: SR_lo = SR_d - se(SR_d) >= b_test, se = sqrt((1 - g3 SR + (g4 - 1)/4 SR^2)/(T - 1))
  (Mertens; the DSR's own denominator), i.e. power >= 0.5 at the one-standard-error lower bound.
"""
from __future__ import annotations

import argparse
import math
import sys
from datetime import date
from pathlib import Path
from statistics import NormalDist

sys.path.insert(0, str(Path(__file__).resolve().parent))
from p7_thresholds import (N_PRIOR, SIGMA_1M_TICKS, required_sharpe,  # noqa: E402
                           trade_dates)
from funnel.multiple_comparisons import expected_max_sharpe  # noqa: E402

Z = NormalDist()
BURN_IN = 20
DISCOVERY = (date(2020, 12, 1), date(2024, 2, 29))
TEST_MBO = (date(2017, 5, 22), date(2020, 11, 30))
DECISION_MINUTES = {5: 273, 15: 263, 30: 248, 60: 218}  # grid 08:35..(13:12 - h), P3


def se_sharpe(sr: float, t: int, skew: float = 0.0, kurt: float = 3.0) -> float:
    return math.sqrt(max(1e-12, 1 - skew * sr + (kurt - 1) / 4 * sr * sr) / (t - 1))


def g4_threshold(b_test: float, t_disc: int, skew: float = 0.0, kurt: float = 3.0) -> float:
    """Smallest discovery daily Sharpe whose one-SE lower bound reaches b_test (bisection)."""
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if mid - se_sharpe(mid, t_disc, skew, kurt) >= b_test:
            hi = mid
        else:
            lo = mid
    return hi


def power(true_sr: float, bar: float, t: int) -> float:
    return Z.cdf((true_sr - bar) / se_sharpe(true_sr, t))


def report(budget: int) -> str:
    n = N_PRIOR + budget
    t_disc = trade_dates(*DISCOVERY) - BURN_IN
    t_test = trade_dates(*TEST_MBO) - BURN_IN
    v_d, v_t = 1 / (t_disc - 1), 1 / (t_test - 1)
    sr0_d = expected_max_sharpe(n, v_d)
    g3 = required_sharpe(n, t_disc, v_d, 0.0, 3.0)
    g3_fat = required_sharpe(n, t_disc, v_d, -0.5, 6.0)
    t_bar = 3.0 / math.sqrt(t_test)
    dsr_test = required_sharpe(n, t_test, v_t, 0.0, 3.0)
    b_test = max(t_bar, dsr_test)
    g4 = g4_threshold(b_test, t_disc)
    g4_alt = g4_threshold(t_bar, t_disc)
    sel = max(g3, g4)
    o = [f"# P7/P8 frozen thresholds (budget {budget}; N after E.33 = {N_PRIOR} + {budget} = {n})", "",
         f"- T_disc = {t_disc} OOF dates ({trade_dates(*DISCOVERY)} program trade dates "
         f"{DISCOVERY[0]}..{DISCOVERY[1]} minus a {BURN_IN}-date burn-in)",
         f"- T_test = {t_test} ({trade_dates(*TEST_MBO)} program trade dates {TEST_MBO[0]}..{TEST_MBO[1]} "
         f"minus the {BURN_IN}-date burn-in; ZM MBO starts 2017-05-21)", "",
         "## Discovery gate G3 (DSR >= 0.95, V = 1/(T_disc - 1), literal N)", "",
         f"- E[max SR] under the null, SR0 = {sr0_d:.4f} daily",
         f"- SR_d needed, normal moments: {g3:.4f} daily (t = {g3 * math.sqrt(t_disc):.2f}; "
         f"annualised x sqrt 252 = {g3 * math.sqrt(252):.2f})",
         f"- SR_d needed, skew -0.5, kurtosis 6: {g3_fat:.4f} daily", "",
         "## The one-shot test's bar b_test (daily Sharpe on T_test dates)", "",
         f"- daily t > 3.0: {t_bar:.4f}",
         f"- DSR >= 0.95 at N = {n}, V = 1/(T_test - 1), normal moments: {dsr_test:.4f} "
         f"(t = {dsr_test * math.sqrt(t_test):.2f})",
         f"- b_test = max = {b_test:.4f} (annualised {b_test * math.sqrt(252):.2f})", "",
         "## Power gate G4 (SR_d - se(SR_d) >= b_test) and the selection threshold", "",
         f"- G4 threshold on discovery SR_d: {g4:.4f} (t = {g4 * math.sqrt(t_disc):.2f}); "
         f"binding selection threshold max(G3, G4) = {sel:.4f} "
         f"(annualised {sel * math.sqrt(252):.2f})",
         f"- (if the user drops the protocol-added test DSR: b_test = {t_bar:.4f}, G4 = {g4_alt:.4f}, "
         f"selection threshold = {max(g3, g4_alt):.4f})", "",
         "## Test power at true daily Sharpe s (normal days)", "",
         "| true s | annualised | P(pass t > 3.0) | P(pass b_test) |", "|---|---|---|---|"]
    for s in (0.10, 0.12, 0.15, 0.17, 0.20, 0.25, 0.30):
        o.append(f"| {s:.2f} | {s * math.sqrt(252):.2f} | {power(s, t_bar, t_test):.3f} | "
                 f"{power(s, b_test, t_test):.3f} |")
    o += ["", "## P(a configuration with true daily Sharpe s, same in both windows, is selected) "
          "x P(it passes the test)", "",
          "| true s | P(select: SR_d >= max(G3, G4)) | P(pass b_test) | product |", "|---|---|---|---|"]
    for s in (0.10, 0.12, 0.15, 0.17, 0.20, 0.25, 0.30):
        p_sel = 1 - Z.cdf((sel - s) / se_sharpe(s, t_disc))
        p_pass = power(s, b_test, t_test)
        o.append(f"| {s:.2f} | {p_sel:.3f} | {p_pass:.3f} | {p_sel * p_pass:.3f} |")
    o += ["", "## Net edge per trade implied (random walk sigma_h = 3.15 sqrt(h) ticks, stated "
          "assumption; n independent trades every date; daily SR = mu sqrt(n) / sigma_h)", "",
          "| hold h (min) | sigma_h | trades/date n | mu at selection threshold | mu for 80% test "
          "power at b_test |", "|---|---|---|---|---|"]
    s80 = b_test + Z.inv_cdf(0.8) * se_sharpe(b_test, t_test)
    for h in (5, 15, 30, 60):
        sig = SIGMA_1M_TICKS * math.sqrt(h)
        for k in (1, 2, 4, 8, 12):
            if k > DECISION_MINUTES[h] // h:
                continue
            o.append(f"| {h} | {sig:.2f} | {k} | {sel * sig / math.sqrt(k):.2f} | "
                     f"{s80 * sig / math.sqrt(k):.2f} |")
    o += ["", f"(80%-power true daily Sharpe at b_test: {s80:.4f}.)", "",
          "## Multiple-testing reference thresholds (one-sided, alpha 0.05)", "",
          "| Rule | alpha per test (first step) | z |", "|---|---|---|"]
    by_c = sum(1 / j for j in range(1, budget + 1))
    for name, a in ((f"Bonferroni / Holm step 1 at m = {budget}", 0.05 / budget),
                    (f"Bonferroni at m = N = {n}", 0.05 / n),
                    (f"BH q = 0.05, rank 1 (= Bonferroni at m = {budget})", 0.05 / budget),
                    (f"BY q = 0.05, rank 1 (c(m) = {by_c:.3f})", 0.05 / (budget * by_c)),
                    ("Holm step 1 at K = 9 (V14 b, the test)", 0.05 / 9),
                    ("Harvey-Liu-Zhu t > 3.0", 1 - Z.cdf(3.0))):
        o.append(f"| {name} | {a:.3g} | {Z.inv_cdf(1 - a):.3f} |")
    return "\n".join(o) + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--budget", type=int, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv[1:])
    text = report(args.budget)
    if args.out:
        args.out.write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
