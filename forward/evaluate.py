"""E22-F1's frozen evaluation bar (ForwardRunnerCoder, E.22).

The bar, computed ONLY on the full 36-month horizon:
- series: the daily net P&L (USD) of every ledger record dated in [clock_start, clock_start +
  36 months); missing-day records count as 0;
- one-sided Newey-West t of the mean (H1: mean > 0): lag 10, Bartlett kernel weights
  1 - l / (lag + 1), autocovariances with divisor T around the sample mean, se = sqrt(LRV / T);
- p = 1 - Phi(t), Phi the standard normal CDF;
- annualised net Sharpe = mean / sd x sqrt(252), sd with ddof = 1;
- PASS iff p <= 0.05 and Sharpe >= 0.3.

The horizon is complete only when the ledger holds a record dated on or after clock_start + 36
months (that record proves the window is closed; it and later records are outside the window).
Earlier calls are refused unless ``interim=True``, which returns descriptive figures only: no
t, no p, no pass/fail.
"""

from __future__ import annotations

import argparse
import calendar
import json
import math
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from forward.ledger import Ledger

HORIZON_MONTHS = 36
NW_LAG = 10
P_MAX = 0.05
SHARPE_MIN = 0.3
TRADING_DAYS = 252
FROZEN_BAR = {
    "horizon_months": HORIZON_MONTHS,
    "nw_lag": NW_LAG,
    "kernel": "Bartlett",
    "test": "one-sided, H1 mean daily net P&L > 0, p from the standard normal",
    "p_max": P_MAX,
    "sharpe_min": SHARPE_MIN,
    "annualisation": "sqrt(252)",
}


class EvaluationRefused(Exception):
    """The final evaluation was requested before the 36-month horizon closed."""


@dataclass(frozen=True)
class NeweyWest:
    mean: float
    lrv: float
    se: float
    t: float | None


def add_months(day: date, months: int) -> date:
    index = day.year * 12 + day.month - 1 + months
    year, month = index // 12, index % 12 + 1
    return date(year, month, min(day.day, calendar.monthrange(year, month)[1]))


def newey_west(x: Sequence[float], lag: int = NW_LAG) -> NeweyWest:
    """Newey-West (Bartlett) long-run variance of the mean of ``x`` and its t-statistic."""
    n = len(x)
    if n <= lag:
        raise ValueError(f"need more than {lag} observations, got {n}")
    mean = math.fsum(x) / n
    dev = [v - mean for v in x]
    lrv = math.fsum(d * d for d in dev) / n
    for k in range(1, lag + 1):
        gamma = math.fsum(dev[t] * dev[t - k] for t in range(k, n)) / n
        lrv += 2.0 * (1.0 - k / (lag + 1.0)) * gamma
    se = math.sqrt(lrv / n) if lrv > 0 else 0.0
    return NeweyWest(mean, lrv, se, mean / se if se > 0 else None)


def one_sided_p(t: float) -> float:
    """P(Z >= t) for a standard normal Z."""
    return 0.5 * math.erfc(t / math.sqrt(2.0))


def sample_sd(x: Sequence[float]) -> float:
    n = len(x)
    if n < 2:
        return 0.0
    mean = math.fsum(x) / n
    return math.sqrt(math.fsum((v - mean) ** 2 for v in x) / (n - 1))


def annualised_sharpe(x: Sequence[float]) -> float | None:
    sd = sample_sd(x)
    return None if sd == 0 else (math.fsum(x) / len(x)) / sd * math.sqrt(TRADING_DAYS)


def passes(p: float | None, sharpe: float | None) -> bool:
    return p is not None and sharpe is not None and p <= P_MAX and sharpe >= SHARPE_MIN


def max_drawdown(dates: Sequence[str], pnl: Sequence[float]) -> dict[str, Any]:
    """Largest fall of cumulative P&L from a running peak (the start counts as a peak of 0)."""
    cum = peak = 0.0
    peak_date = trough_date = best_peak = None
    worst = 0.0
    for day, value in zip(dates, pnl, strict=True):
        cum += value
        if cum > peak:
            peak, peak_date = cum, day
        if peak - cum > worst:
            worst, trough_date, best_peak = peak - cum, day, peak_date
    return {"max_drawdown_usd": worst, "peak_date": best_peak, "trough_date": trough_date}


def window(records: Sequence[Mapping[str, Any]], start: date, end: date) -> list[Mapping[str, Any]]:
    """Records dated in [start, end)."""
    return [r for r in records if start <= date.fromisoformat(r["date"]) < end]


def resolve_clock_start(records: Sequence[Mapping[str, Any]], clock_start: date | None) -> date:
    if not records:
        raise EvaluationRefused("the ledger is empty")
    first = date.fromisoformat(records[0]["date"])
    start = clock_start or first
    if start > first:
        raise ValueError(f"records exist before the declared clock start {start}")
    return start


def descriptive(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    dates = [r["date"] for r in rows]
    net = [float(r["net_pnl"]) for r in rows]
    n = len(net)
    return {
        "n_days": n,
        "first_date": dates[0] if dates else None,
        "last_date": dates[-1] if dates else None,
        "mean_daily_net_usd": math.fsum(net) / n if n else None,
        "sd_daily_net_usd": sample_sd(net) if n > 1 else None,
        "sharpe_annualised_net": annualised_sharpe(net) if n > 1 else None,
        "total_net_usd": math.fsum(net),
        "days_flagged": sum(1 for r in rows if r.get("flags")),
        **max_drawdown(dates, net),
    }


def evaluate(
    records: Sequence[Mapping[str, Any]], *, clock_start: date | None = None, interim: bool = False
) -> dict[str, Any]:
    """E22-F1's bar on the full horizon, or (interim=True) descriptive figures without p."""
    start = resolve_clock_start(records, clock_start)
    end = add_months(start, HORIZON_MONTHS)
    complete = date.fromisoformat(records[-1]["date"]) >= end
    rows = window(records, start, end)
    base = {
        "clock_start": start.isoformat(),
        "horizon_end_exclusive": end.isoformat(),
        "horizon_complete": complete,
        "frozen_bar": FROZEN_BAR,
    }
    if interim:
        return {
            **base,
            "interim": True,
            **descriptive(rows),
            "note": "interim look: descriptive only; no t, no p, no pass/fail",
        }
    if not complete:
        raise EvaluationRefused(
            f"the 36-month horizon closes at {end}; the ledger ends at "
            f"{records[-1]['date']}. Pass interim=True for descriptive figures."
        )
    net = [float(r["net_pnl"]) for r in rows]
    nw = newey_west(net, NW_LAG)
    p = one_sided_p(nw.t) if nw.t is not None else None
    sharpe = annualised_sharpe(net)
    return {
        **base,
        "interim": False,
        **descriptive(rows),
        "nw_lag": NW_LAG,
        "nw_lrv": nw.lrv,
        "nw_se": nw.se,
        "nw_t": nw.t,
        "p_one_sided": p,
        "sharpe_annualised_net": sharpe,
        "pass": passes(p, sharpe),
    }


def evaluate_ledger(path: Path | str, **kwargs: Any) -> dict[str, Any]:
    """Verify the ledger chain, then evaluate it."""
    return evaluate(Ledger(path).records(), **kwargs)


def _main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m forward.evaluate")
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--clock-start", help="declared clock start YYYY-MM-DD (default: first record)")
    ap.add_argument("--interim", action="store_true", help="descriptive figures only, no p")
    args = ap.parse_args(argv)
    start = date.fromisoformat(args.clock_start) if args.clock_start else None
    print(
        json.dumps(
            evaluate_ledger(args.ledger, clock_start=start, interim=args.interim),
            indent=1,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(_main())
