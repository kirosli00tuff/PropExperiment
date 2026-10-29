"""E.34 M4: power and N for the ZL program (pure arithmetic; no market data is read).

    uv run python reports/stage_e34_briefs/work/MathReaderM4-OpusHigh/m4_power.py > .../m4_out.md

Uses the frozen E.32 functions exactly as E.32b's hurdles.py did:
p7_final.se_sharpe / g4_threshold, p7_thresholds.required_sharpe / trade_dates (holiday
calendars only), funnel.multiple_comparisons.expected_max_sharpe / deflated_sharpe_ratio.
"""
from __future__ import annotations

import math
import random
import statistics
import sys
from datetime import date, timedelta
from pathlib import Path
from statistics import NormalDist

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "reports/stage_e32_briefs/protocol"))
from p7_thresholds import required_sharpe, trade_dates  # noqa: E402
from p7_final import se_sharpe, g4_threshold  # noqa: E402
from funnel.multiple_comparisons import expected_max_sharpe, deflated_sharpe_ratio  # noqa: E402

Z = NormalDist()
Z80 = Z.inv_cdf(0.8)
N_NOW = 838
BUDGETS = (0, 40, 62, 100, 150, 200, 250, 300)
BURN_IN = 20
DISC = (date(2020, 12, 1), date(2024, 2, 29))
TEST_MBO = (date(2017, 5, 22), date(2020, 11, 30))
TEST_MBP1 = (date(2017, 5, 1), date(2020, 11, 30))
SIGMA = {15: 20.37, 30: 28.10, 60: 38.21}  # ZL day-session sigma_h, ticks (E.32b holding scope 15)
N_CAP = {15: 19, 30: 9, 60: 4}
RATES = (1, 2, 4)


def weekdays(a: date, b: date) -> int:
    n, d = 0, a
    while d <= b:
        n += d.weekday() < 5
        d += timedelta(days=1)
    return n


def row(n: int, t_disc: int, t_test: int, skew: float = 0.0, kurt: float = 3.0) -> dict:
    v_d, v_t = 1 / (t_disc - 1), 1 / (t_test - 1)
    sr0 = expected_max_sharpe(n, v_d)
    g3 = required_sharpe(n, t_disc, v_d, skew, kurt)
    dsr_t = required_sharpe(n, t_test, v_t, skew, kurt)
    t_bar = 3.0 / math.sqrt(t_test)
    b = max(t_bar, dsr_t)
    g4 = g4_threshold(b, t_disc, skew, kurt)
    sel = max(g3, g4)
    s80_t = b + Z80 * se_sharpe(b, t_test, skew, kurt)
    s80_g3 = g3 + Z80 * se_sharpe(g3, t_disc, skew, kurt)
    s80_sel = sel + Z80 * se_sharpe(sel, t_disc, skew, kurt)
    return dict(n=n, sr0=sr0, g3=g3, t_bar=t_bar, dsr_t=dsr_t, b=b, g4=g4, sel=sel,
                s80_t=s80_t, s80_g3=s80_g3, s80_sel=s80_sel, td=t_disc, tt=t_test)


def threshold_table(t_disc: int, t_test: int, title: str) -> list[str]:
    o = [f"### {title} (T_disc {t_disc}, T_test {t_test}; normal moments)", "",
         "| B | N | e(N) | SR0 disc | G3 SR_d (t) | b_test (t) | G4 SR_d (t) | binding | SR80_test | "
         "SR80 disc G3 | SR80 disc binding | b_test unrounded |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for bb in BUDGETS:
        r = row(N_NOW + bb, t_disc, t_test)
        en = expected_max_sharpe(r["n"], 1.0)
        o.append(f"| {bb} | {r['n']} | {en:.4f} | {r['sr0']:.4f} | {r['g3']:.4f} ({r['g3']*math.sqrt(t_disc):.2f}) | "
                 f"{r['b']:.4f} ({r['b']*math.sqrt(t_test):.2f}) | {r['g4']:.4f} ({r['g4']*math.sqrt(t_disc):.2f}) | "
                 f"{r['sel']:.4f} | {r['s80_t']:.4f} | {r['s80_g3']:.4f} | {r['s80_sel']:.4f} | {r['b']:.6f} |")
    return o + [""]


def e80_table(t_disc: int, t_test: int, budgets=(0, 62, 150, 300)) -> list[str]:
    o = [f"### e80, ticks a trade net (T_disc {t_disc}, T_test {t_test}): e80 = SR80 x sigma_h / sqrt(n)", "",
         "| B | N | h | sigma_h | n/day | disc G3 | disc binding (G3+G4) | test | selection threshold itself "
         "(about 50% power) |", "|---|---|---|---|---|---|---|---|---|"]
    for bb in budgets:
        r = row(N_NOW + bb, t_disc, t_test)
        for h, sig in SIGMA.items():
            for n in sorted({N_CAP[h], *[k for k in RATES if k <= N_CAP[h]]}, reverse=True):
                tag = f"{n} (cap)" if n == N_CAP[h] else str(n)
                f = sig / math.sqrt(n)
                o.append(f"| {bb} | {r['n']} | {h} | {sig:.2f} | {tag} | {r['s80_g3']*f:.2f} | "
                         f"{r['s80_sel']*f:.2f} | {r['s80_t']*f:.2f} | {r['sel']*f:.2f} |")
    return o + [""]


def fat_table(t_disc: int, t_test: int) -> list[str]:
    o = [f"### Moment sensitivity at N 838 (T_disc {t_disc}, T_test {t_test})", "",
         "| skew | raw kurtosis | G3 | b_test | G4 | binding | SR80_test | SR80 disc binding | "
         "e80 test h30 n9 | e80 test h30 n1 |", "|---|---|---|---|---|---|---|---|---|---|"]
    for sk, ku in ((0.0, 3.0), (-0.5, 6.0), (0.0, 10.0), (-1.0, 10.0), (0.0, 20.0), (-2.0, 30.0)):
        r = row(N_NOW, t_disc, t_test, sk, ku)
        o.append(f"| {sk} | {ku} | {r['g3']:.4f} | {r['b']:.4f} | {r['g4']:.4f} | {r['sel']:.4f} | "
                 f"{r['s80_t']:.4f} | {r['s80_sel']:.4f} | {r['s80_t']*SIGMA[30]/3:.2f} | "
                 f"{r['s80_t']*SIGMA[30]:.2f} |")
    return o + [""]


def holm_table() -> list[str]:
    o = ["### Holm at the test: first-step one-sided alpha 0.05/(K m) and its z", "",
         "| K (families) | m = 1 | m = 2 | m = 3 |", "|---|---|---|---|"]
    for k in (1, 2, 9):
        cells = []
        for m in (1, 2, 3):
            a = 0.05 / k / m
            cells.append(f"{a:.5f} (z {Z.inv_cdf(1 - a):.3f})")
        o.append(f"| {k} | " + " | ".join(cells) + " |")
    o += ["", "Holm steps for m = 3 (thresholds alpha_K/3, alpha_K/2, alpha_K/1), z:", ""]
    for k in (1, 2, 9):
        zs = [Z.inv_cdf(1 - 0.05 / k / j) for j in (3, 2, 1)]
        o.append(f"- K {k}: " + ", ".join(f"{x:.3f}" for x in zs))
    o.append(f"- bootstrap p floor 1/(B+1), B 10,000: {1/10001:.6f} (z {Z.inv_cdf(1 - 1/10001):.3f})")
    return o + [""]


def d2_table(t_test: int) -> list[str]:
    o = ["### D2: V14 (c) SR0 multipliers (SR0 = e(N) x pop SD of the tested Sharpes)", "",
         "| B | N | e(N) | 1 member + 1 null: SR0/s | 1 member + 2 nulls: SR0/s |", "|---|---|---|---|---|"]
    for bb in BUDGETS:
        en = expected_max_sharpe(N_NOW + bb, 1.0)
        o.append(f"| {bb} | {N_NOW+bb} | {en:.4f} | {en*0.5:.3f} | {en*math.sqrt(2)/3:.3f} |")
    return o + [""]


def d2_sim(t_test: int, n_trials: int, reps: int = 4000, seed: int = 20261029) -> list[str]:
    """Synthetic normal Sharpe draws only (no data): pass probability of check (1)'s DSR part
    under V14 (c) as coded versus amended (V = 1/(T_test - 1)), plus check (2) and t > 3."""
    rng = random.Random(seed)
    se = lambda s: se_sharpe(s, t_test)  # noqa: E731
    v_am = 1 / (t_test - 1)
    o = [f"### D2 simulation (synthetic normal Sharpe estimates, {reps} reps, N {n_trials}, T_test {t_test})", "",
         "| case: true Sharpes (first = finalist) | P(DSR V14c > 0.95) | P(amended DSR > 0.95) | "
         "P(t > 3) | P(all of V14c-DSR, amended DSR, t) | P(amended DSR and t) |",
         "|---|---|---|---|---|---|"]
    cases = [(0.20, 0.0, 0.0), (0.25, 0.0, 0.0), (0.30, 0.0, 0.0), (0.40, 0.0, 0.0),
             (0.20, 0.0), (0.25, 0.0), (0.25, 0.15), (0.25, 0.10), (0.20, 0.15), (0.20, 0.10),
             (0.25, 0.20, 0.15), (0.25, 0.15, 0.0)]
    for case in cases:
        c1 = c2 = ct = call = c23 = 0
        for _ in range(reps):
            sh = [rng.gauss(s, se(s)) for s in case]
            var = statistics.pvariance(sh)
            x = sh[0]
            d1 = deflated_sharpe_ratio(x, t_test, n_trials, var)["deflated_sharpe_ratio"] > 0.95
            d2 = deflated_sharpe_ratio(x, t_test, n_trials, v_am)["deflated_sharpe_ratio"] > 0.95
            tt = x * math.sqrt(t_test) > 3.0
            c1 += d1; c2 += d2; ct += tt; call += d1 and d2 and tt; c23 += d2 and tt
        o.append(f"| {case} | {c1/reps:.3f} | {c2/reps:.3f} | {ct/reps:.3f} | {call/reps:.3f} | {c23/reps:.3f} |")
    return o + [""]


def main() -> None:
    nd = trade_dates(*DISC)
    nt_mbo = trade_dates(*TEST_MBO)
    nt_mbp = trade_dates(*TEST_MBP1)
    o = ["# M4 power arithmetic output", "",
         f"- trade_dates discovery {DISC}: {nd} (weekdays {weekdays(*DISC)})",
         f"- trade_dates test MBO {TEST_MBO}: {nt_mbo} (weekdays {weekdays(*TEST_MBO)})",
         f"- trade_dates test MBP-1 {TEST_MBP1}: {nt_mbp} (weekdays {weekdays(*TEST_MBP1)})",
         f"- burn-in {BURN_IN}: T_disc {nd-BURN_IN}, T_test MBO {nt_mbo-BURN_IN}, T_test MBP-1 {nt_mbp-BURN_IN}", ""]
    td, tm, tp = nd - BURN_IN, nt_mbo - BURN_IN, nt_mbp - BURN_IN
    o += threshold_table(td, tm, "Thresholds, test on MBO")
    o += threshold_table(td, tp, "Thresholds, test on MBP-1")
    o += threshold_table(td - 20, tm - 20, "Sensitivity: 40-date burn-in, test on MBO")
    o += e80_table(td, tm)
    o += e80_table(td, tp, budgets=(0, 300))
    o += fat_table(td, tm)
    o += holm_table()
    o += d2_table(tm)
    o += d2_sim(tm, N_NOW)
    o += d2_sim(tm, N_NOW + 300, reps=2000, seed=20261030)
    print("\n".join(o))


if __name__ == "__main__":
    main()
