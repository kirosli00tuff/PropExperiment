"""Stage E.32 Part P7/P8: deflated-Sharpe, multiple-testing and power thresholds at the search's N.

    uv run python reports/stage_e32_briefs/protocol/p7_thresholds.py --budget 432 [--out FILE]

Pure arithmetic. No market data is read: trade-date counts come from the program's grains holiday
calendars (data.calendars.grains for 2019-05-01 onward, the hist2010 grains calendar before), and
the deflated Sharpe ratio from the program's own funnel.multiple_comparisons (Bailey and Lopez de
Prado 2014, eq. 3 for the expected maximum), so E.33 computes its thresholds with the same code.

Assumptions, each stated where it is used:
- sigma_1m = 3.15 ZM ticks (reports/stage_e28_briefs/A0_contract_stats.md, Table 1) and random-walk
  scaling sigma_h = sigma_1m * sqrt(h) for a trade held h minutes;
- the cross-trial variance V of daily Sharpe estimates is c / (T - 1), c in {0.5, 1, 2}: c = 1 is
  the null with every trial's true Sharpe 0 (Var of a Sharpe estimate from T normal days is about
  1 / (T - 1)); c < 1 when trials are strongly correlated, c > 1 when true Sharpes differ.
"""

from __future__ import annotations

import argparse
import math
import sys
from datetime import date, timedelta
from pathlib import Path
from statistics import NormalDist

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from data.calendars import grains  # noqa: E402
from data.cme_calendar import HolidayKind  # noqa: E402
from data.hist_calendar import load_hist_group_calendar  # noqa: E402
from funnel.multiple_comparisons import deflated_sharpe_ratio, expected_max_sharpe  # noqa: E402

N_PRIOR = 538
SIGMA_1M_TICKS = 3.15
DAY_SESSION_MINUTES = 290  # 08:30-13:20 CT
DISCOVERY = (date(2020, 12, 1), date(2024, 2, 29))
TEST = (date(2017, 5, 1), date(2020, 11, 30))
Z = NormalDist()


def full_closures(first: date, last: date) -> set[date]:
    """Grain full-closure dates in [first, last] from the program's calendars."""
    days: set[date] = set()
    hist = load_hist_group_calendar("grains")
    for day, holiday in hist.holidays.items():
        if day < grains.CALENDAR_COVERAGE[0] and holiday.kind is HolidayKind.FULL_CLOSURE:
            days.add(day)
    days |= {h.day for h in grains.HOLIDAYS.values() if h.kind is HolidayKind.FULL_CLOSURE}
    return {d for d in days if first <= d <= last}


def trade_dates(first: date, last: date) -> int:
    """Weekdays in [first, last] minus grain full closures. Coverage must reach both ends."""
    hist = load_hist_group_calendar("grains")
    if first < hist.coverage[0] or last > grains.CALENDAR_COVERAGE[1]:
        raise ValueError(f"{first}..{last} is outside the calendars' coverage")
    closed = full_closures(first, last)
    n, day = 0, first
    while day <= last:
        if day.weekday() < 5 and day not in closed:
            n += 1
        day += timedelta(days=1)
    return n


def required_sharpe(n_trials: int, t_obs: int, variance: float, skew: float, kurt: float,
                    target: float = 0.95) -> float:
    """Smallest observed daily Sharpe whose DSR reaches ``target`` (bisection on the program's
    deflated_sharpe_ratio, which is increasing in the observed Sharpe on [0, 1])."""
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if deflated_sharpe_ratio(mid, t_obs, n_trials, variance, skew, kurt)[
                "deflated_sharpe_ratio"] >= target:
            hi = mid
        else:
            lo = mid
    return hi


def one_sided_z(alpha: float) -> float:
    return Z.inv_cdf(1 - alpha)


def trades_needed(mu: float, sigma: float, alpha: float, power: float) -> float:
    """One-sided test of a mean net edge mu > 0 with per-trade SD sigma (independent trades)."""
    return ((one_sided_z(alpha) + Z.inv_cdf(power)) * sigma / mu) ** 2


def report(budget: int, k_test: int = 3, alpha: float = 0.05, power: float = 0.8) -> str:
    n_after = N_PRIOR + budget
    t_disc, t_test = trade_dates(*DISCOVERY), trade_dates(*TEST)
    out = [f"# P7/P8 thresholds (budget {budget}, N after E.33 = {N_PRIOR} + {budget} = {n_after})",
           "", f"- Discovery trade dates {DISCOVERY[0]}..{DISCOVERY[1]}: {t_disc} "
           f"(weekdays minus grain full closures; before E.33's own exclusions)",
           f"- Test trade dates {TEST[0]}..{TEST[1]}: {t_test}", ""]

    out += ["## Deflated Sharpe at N (daily Sharpe, T = discovery trade dates)", "",
            "| c in V = c/(T-1) | V | E[max SR] daily | SR for DSR>=0.95, normal | annualised x sqrt(252) "
            "| SR for DSR>=0.95, skew -0.5 kurt 6 | annualised |", "|---|---|---|---|---|---|---|"]
    for c in (0.5, 1.0, 2.0):
        v = c / (t_disc - 1)
        emax = expected_max_sharpe(n_after, v)
        s_n = required_sharpe(n_after, t_disc, v, 0.0, 3.0)
        s_f = required_sharpe(n_after, t_disc, v, -0.5, 6.0)
        out.append(f"| {c} | {v:.6f} | {emax:.4f} | {s_n:.4f} | {s_n * math.sqrt(252):.2f} | "
                   f"{s_f:.4f} | {s_f * math.sqrt(252):.2f} |")

    out += ["", f"## Multiple testing over the search's {budget} configurations (one-sided)", "",
            "| Rule | alpha per test (first step) | z | t equivalent (large n) |", "|---|---|---|---|"]
    for name, a in (("Bonferroni / Holm step 1 at m = budget", alpha / budget),
                    ("Bonferroni at m = N after E.33", alpha / n_after),
                    ("BH q = 0.05, rank 1 (same as Bonferroni)", alpha / budget),
                    ("BH q = 0.05, rank 10", 10 * alpha / budget),
                    (f"Holm step 1 over the {k_test} test candidates", alpha / k_test),
                    ("Harvey-Liu-Zhu hurdle t > 3.0", 1 - Z.cdf(3.0))):
        out.append(f"| {name} | {a:.3g} | {one_sided_z(a):.3f} | {one_sided_z(a):.2f} |")

    a_test = alpha / k_test
    out += ["", f"## Power of the one-shot test ({t_test} trade dates, alpha {a_test:.4f} one-sided "
            f"= Holm step 1 over {k_test}, power {power})", "",
            "sigma per trade = 3.15 * sqrt(h) ticks (random walk, stated assumption); trades per day "
            f"capped by non-overlapping holds in the {DAY_SESSION_MINUTES}-minute day session.", "",
            "| hold h (min) | sigma/trade (ticks) | max trades/day | mu net (ticks) | trades needed "
            "| trades/day needed | feasible |", "|---|---|---|---|---|---|---|"]
    for h in (5, 15, 30, 60, 120, 240):
        sig = SIGMA_1M_TICKS * math.sqrt(h)
        cap = DAY_SESSION_MINUTES // h
        for mu in (0.25, 0.5, 1.0, 1.5, 2.0):
            n = trades_needed(mu, sig, a_test, power)
            per_day = n / t_test
            out.append(f"| {h} | {sig:.2f} | {cap} | {mu} | {n:,.0f} | {per_day:.2f} | "
                       f"{'yes' if per_day <= cap else 'no'} |")
    out += test_bars(n_after, t_test, power)
    return "\n".join(out) + "\n"


def test_bars(n_after: int, t_test: int, power: float) -> list[str]:
    """The one-shot test's binding daily-Sharpe bar and the net edge per trade it implies.

    The program's verdict (screening.stage_e_verdict) needs, on the test window's daily series, a
    daily t > 3.0 and DSR > 0.95 at the program N (plus Holm and PBO, which bind less). The DSR's
    Sharpe variance V is unknown before the read, so V = c / (T - 1) is tabulated. With a true daily
    Sharpe s, the observed Sharpe is about N(s, 1 / sqrt(T)) (normal days), so a pass with
    probability ``power`` needs s = bar + z_power / sqrt(T). Daily P&L of n independent trades a
    day, each with mean mu and SD sigma_h, has Sharpe mu * sqrt(n) / sigma_h, so
    mu = s * sigma_h / sqrt(n).
    """
    t_bar = 3.0 / math.sqrt(t_test)
    z_pow = Z.inv_cdf(power)
    out = ["", f"## The one-shot test's bar on daily Sharpe (T = {t_test} test trade dates, N = {n_after})",
           "", "| bar | daily SR at the bar | true daily SR for "
           f"{power:.0%} power | annualised (x sqrt 252) |", "|---|---|---|---|"]
    bars = {"daily t > 3.0": t_bar}
    for c in (0.25, 0.5, 1.0, 2.0):
        v = c / (t_test - 1)
        bars[f"DSR > 0.95, V = {c}/(T-1)"] = required_sharpe(n_after, t_test, v, 0.0, 3.0)
    for name, bar in bars.items():
        s = bar + z_pow / math.sqrt(t_test)
        out.append(f"| {name} | {bar:.4f} | {s:.4f} | {s * math.sqrt(252):.2f} |")
    s_req = max(bars["daily t > 3.0"], bars["DSR > 0.95, V = 1.0/(T-1)"]) + z_pow / math.sqrt(t_test)
    out += ["", f"## Net edge per trade for {power:.0%} power at the binding bar (c = 1): true daily "
            f"SR {s_req:.4f}", "", "| hold h (min) | sigma/trade (ticks) | trades/day n | mu net "
            "(ticks/trade) | mu x n (ticks/day) |", "|---|---|---|---|---|"]
    for h in (5, 15, 30, 60):
        sig = SIGMA_1M_TICKS * math.sqrt(h)
        for n in (1, 2, 4, 8, 12):
            if n > DAY_SESSION_MINUTES // h:
                continue
            mu = s_req * sig / math.sqrt(n)
            out.append(f"| {h} | {sig:.2f} | {n} | {mu:.2f} | {mu * n:.2f} |")
    return out


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
