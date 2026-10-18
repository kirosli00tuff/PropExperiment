"""E22-F2's verdict and interim looks (reports/stage_e24_prereg_F2.md DRAFT 1, sections 6-9).

The verdict (section 8), computed once at the end of the horizon on the E22-F2 ledger:
- start = the date of the first ledger record; the window is [start, start + 36 calendar months);
  there is no clock-start option: the first record IS the start (section 7);
- series = net_pnl of every ledger record dated in the window (the zero days before the first fill
  and the missing days included; declared exchange-closed days have no record and are not in it);
- one-sided Newey-West t of the mean (Bartlett, lag 10), p from the standard normal: p <= 0.05;
- annualised net Sharpe = mean / sd x sqrt(252): >= 0.3;
- PASS iff both hold, otherwise FAIL; forward/evaluate.py's functions compute every figure.
The window is complete only when the ledger holds a record dated on or after its end; before
that the verdict is refused.

Abandoned, no verdict (section 6): a broken chain, a rewrite or an out-of-order date (the ledger
refuses to parse), or records made under different configuration or warm-up fingerprints or with
different data feeds (the feed is fixed before the first record).

Interim looks (section 9): every 6 months, descriptive figures only (mean, sd, Sharpe, drawdown,
turnover, costs, flagged days, days the cap bound). No t and no p-value at a look.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections.abc import Mapping, Sequence
from datetime import date
from pathlib import Path
from typing import Any

from forward.evaluate import (
    FROZEN_BAR,
    HORIZON_MONTHS,
    NW_LAG,
    EvaluationRefused,
    add_months,
    annualised_sharpe,
    max_drawdown,
    newey_west,
    one_sided_p,
    passes,
    sample_sd,
)
from forward.ledger import Ledger, LedgerIntegrityError

SCHEMA = "E22-F2-ledger/1"
TEST_ID = "E22-F2"
LOOK_MONTHS = 6
ABANDONED = "abandoned, no verdict"


def integrity_problem(records: Sequence[Mapping[str, Any]]) -> str | None:
    """A reason the test is abandoned (section 6), or None. The chain itself is checked by
    forward.ledger when the records are read."""
    if not records:
        return None
    for r in records:
        if r.get("schema") != SCHEMA:
            return f"record {r.get('date')} is not an {SCHEMA} record"
    for key in ("config_sha256", "warmup_sha256", "feed"):
        values = {r.get(key) for r in records}
        if len(values) != 1 or None in values:
            return f"records carry {len(values)} different {key} values"
    return None


def window(records: Sequence[Mapping[str, Any]], start: date, end: date) -> list[Mapping[str, Any]]:
    return [r for r in records if start <= date.fromisoformat(r["date"]) < end]


def _base(records: Sequence[Mapping[str, Any]], months: int) -> tuple[date, date, bool]:
    if not records:
        raise EvaluationRefused("the ledger is empty")
    start = date.fromisoformat(records[0]["date"])
    end = add_months(start, months)
    return start, end, date.fromisoformat(records[-1]["date"]) >= end


def verdict(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Section 8 on verified records (forward.ledger.Ledger.records())."""
    problem = integrity_problem(records)
    if problem:
        return {"test_id": TEST_ID, "status": ABANDONED, "reason": problem}
    start, end, complete = _base(records, HORIZON_MONTHS)
    if not complete:
        raise EvaluationRefused(
            f"the 36-month horizon closes at {end}; the ledger ends at {records[-1]['date']}. "
            "Use an interim look (descriptive only) before then."
        )
    rows = window(records, start, end)
    net = [float(r["net_pnl"]) for r in rows]
    nw = newey_west(net, NW_LAG)
    p = one_sided_p(nw.t) if nw.t is not None else None
    sharpe = annualised_sharpe(net)
    ok = passes(p, sharpe)
    return {
        "test_id": TEST_ID,
        "status": "PASS" if ok else "FAIL",
        "pass": ok,
        "start": start.isoformat(),
        "horizon_end_exclusive": end.isoformat(),
        "n_days": len(net),
        "n_missing_days": sum(1 for r in rows if r.get("missing_day")),
        "mean_daily_net_usd": math.fsum(net) / len(net),
        "sd_daily_net_usd": sample_sd(net),
        "nw_lag": NW_LAG,
        "nw_lrv": nw.lrv,
        "nw_se": nw.se,
        "nw_t": nw.t,
        "p_one_sided": p,
        "sharpe_annualised_net": sharpe,
        "frozen_bar": FROZEN_BAR,
    }


def _traded_notional(rows: Sequence[Mapping[str, Any]]) -> float:
    return math.fsum(float(f["notional_usd"]) for r in rows for f in r.get("fills", []))


def look(
    records: Sequence[Mapping[str, Any]], k: int, capital_usd: float = 25000.0
) -> dict[str, Any]:
    """Interim look k (k = 1..6): records in [start, start + 6k months). Descriptive only."""
    if not 1 <= k <= HORIZON_MONTHS // LOOK_MONTHS:
        raise ValueError(f"look must be 1..{HORIZON_MONTHS // LOOK_MONTHS}, got {k}")
    problem = integrity_problem(records)
    if problem:
        return {"test_id": TEST_ID, "status": ABANDONED, "reason": problem}
    start, end, complete = _base(records, LOOK_MONTHS * k)
    rows = window(records, start, end)
    dates = [r["date"] for r in rows]
    net = [float(r["net_pnl"]) for r in rows]
    n = len(net)
    traded = _traded_notional(rows)
    years = n / 252.0
    return {
        "test_id": TEST_ID,
        "look": k,
        "interim": True,
        "note": "descriptive only: no t, no p-value, no pass/fail (prereg section 9)",
        "start": start.isoformat(),
        "window_end_exclusive": end.isoformat(),
        "window_complete": complete,
        "n_days": n,
        "first_date": dates[0] if dates else None,
        "last_date": dates[-1] if dates else None,
        "mean_daily_net_usd": math.fsum(net) / n if n else None,
        "sd_daily_net_usd": sample_sd(net) if n > 1 else None,
        "sharpe_annualised_net": annualised_sharpe(net) if n > 1 else None,
        "total_net_usd": math.fsum(net),
        **max_drawdown(dates, net),
        "traded_notional_usd": traded,
        "turnover_capital_per_year": traded / capital_usd / years if years > 0 else None,
        "costs_usd": math.fsum(float(r["costs"]["total"]) for r in rows),
        "late_ca_usd": math.fsum(float(r.get("pnl", {}).get("late_ca", 0.0)) for r in rows),
        "days_late_ca": sum(1 for r in rows if r.get("late_ca")),
        "days_flagged": sum(1 for r in rows if r.get("flags")),
        "days_missing": sum(1 for r in rows if r.get("missing_day")),
        "days_cap_bound": sum(1 for r in rows if r.get("exposure", {}).get("cap_bound")),
        "days_second_cap_check": sum(
            1 for r in rows if (r.get("exposure", {}).get("second_check") or {}).get("applied")
        ),
    }


def _records_or_abandoned(path: Path | str) -> list[dict[str, Any]] | dict[str, Any]:
    try:
        return Ledger(path).records()
    except LedgerIntegrityError as exc:
        return {"test_id": TEST_ID, "status": ABANDONED, "reason": f"ledger chain: {exc}"}


def verdict_ledger(path: Path | str) -> dict[str, Any]:
    """Verify the ledger chain, then compute the verdict (or abandoned, no verdict)."""
    records = _records_or_abandoned(path)
    return records if isinstance(records, dict) else verdict(records)


def look_ledger(path: Path | str, k: int, capital_usd: float = 25000.0) -> dict[str, Any]:
    records = _records_or_abandoned(path)
    return records if isinstance(records, dict) else look(records, k, capital_usd)


def _main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="python -m forward.evaluate_f2",
        description="E22-F2 verdict (section 8) or interim look (section 9)",
    )
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--look", type=int, help="interim look k = 1..6 (descriptive only, no p)")
    args = ap.parse_args(argv)
    out = look_ledger(args.ledger, args.look) if args.look else verdict_ledger(args.ledger)
    print(json.dumps(out, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(_main())


__all__ = [
    "ABANDONED",
    "HORIZON_MONTHS",
    "SCHEMA",
    "TEST_ID",
    "integrity_problem",
    "look",
    "look_ledger",
    "verdict",
    "verdict_ledger",
    "window",
]
