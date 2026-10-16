"""E22-F1's 6-monthly descriptive look (ForwardRunnerCoder, E.22). No p-value, ever.

Look k (k = 1..6) covers the period [clock_start + 6(k-1) months, clock_start + 6k months) and
the cumulative span [clock_start, clock_start + 6k months). A look is due only when the ledger
holds a record dated on or after the period's end. Figures: mean, sd, annualised Sharpe (all
descriptive), drawdown, turnover, costs, days flagged. Every look states that it changes nothing.
"""

from __future__ import annotations

import argparse
import math
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import date
from pathlib import Path
from typing import Any

from forward.evaluate import TRADING_DAYS, add_months, descriptive, resolve_clock_start, window
from forward.ledger import Ledger

LOOK_MONTHS = 6
MAX_LOOK = 6
NO_P_LINE = "No p-value or t-statistic is computed at this look."
NOTHING_LINE = (
    "Note: this look changes nothing. The rule, the costs, the roll schedule, the "
    "horizon and the E22-F1 bar stay as registered."
)


class LookNotDue(Exception):
    """The requested look's period has not closed in the ledger."""


def turnover(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    fill_sides = sum(abs(int(f["qty"])) for r in rows for f in r.get("fills", []))
    roll_sides = sum(2 * abs(int(x["qty"])) for r in rows for x in r.get("rolls", []))
    years = len(rows) / TRADING_DAYS if rows else 0.0
    sides = fill_sides + roll_sides
    return {
        "contracts_traded_fills": fill_sides,
        "contracts_traded_rolls": roll_sides,
        "round_turns": sides / 2,
        "contracts_per_year": sides / years if years else None,
        "round_turns_per_year": sides / 2 / years if years else None,
    }


def costs(rows: Sequence[Mapping[str, Any]]) -> dict[str, float]:
    fills = math.fsum(float(r["costs"]["fills"]) for r in rows)
    rolls = math.fsum(float(r["costs"]["rolls"]) for r in rows)
    return {
        "cost_fills_usd": fills,
        "cost_rolls_usd": rolls,
        "cost_total_usd": fills + rolls,
        "gross_total_usd": math.fsum(float(r["gross_pnl"]) for r in rows),
    }


def flag_counts(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    kinds = Counter(f.split(":")[0] for r in rows for f in set(r.get("flags", [])))
    return dict(sorted(kinds.items()))


def summarise(rows: Sequence[Mapping[str, Any]], capital: float | None) -> dict[str, Any]:
    out = {**descriptive(rows), **turnover(rows), **costs(rows), "flag_counts": flag_counts(rows)}
    if capital:
        out["max_drawdown_pct_capital"] = 100.0 * out["max_drawdown_usd"] / capital
        out["cost_pct_capital"] = 100.0 * out["cost_total_usd"] / capital
    return out


def six_month_look(
    records: Sequence[Mapping[str, Any]],
    look: int,
    *,
    clock_start: date | None = None,
    capital: float | None = None,
) -> dict[str, Any]:
    if not 1 <= look <= MAX_LOOK:
        raise ValueError(f"look must be 1..{MAX_LOOK}")
    start = resolve_clock_start(records, clock_start)
    period_start = add_months(start, LOOK_MONTHS * (look - 1))
    end = add_months(start, LOOK_MONTHS * look)
    if date.fromisoformat(records[-1]["date"]) < end:
        raise LookNotDue(f"look {look} closes at {end}; the ledger ends at {records[-1]['date']}")
    return {
        "look": look,
        "clock_start": start.isoformat(),
        "period": [period_start.isoformat(), end.isoformat()],
        "period_figures": summarise(window(records, period_start, end), capital),
        "cumulative_figures": summarise(window(records, start, end), capital),
        "capital_usd": capital,
        "lines": [NO_P_LINE, NOTHING_LINE],
    }


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:,.2f}"
    return "n/a" if value is None else str(value)


def render_markdown(look: Mapping[str, Any]) -> str:
    keys = [k for k in look["period_figures"] if k != "flag_counts"]
    lines = [
        f"# E22-F1 descriptive look {look['look']} (period {look['period'][0]} to "
        f"{look['period'][1]}, end exclusive)",
        "",
        "| Figure | Period | Cumulative |",
        "|---|---|---|",
    ]
    for k in keys:
        lines.append(
            f"| {k} | {_fmt(look['period_figures'][k])} | {_fmt(look['cumulative_figures'][k])} |"
        )
    lines.append(
        f"| flag_counts | {look['period_figures']['flag_counts']} | "
        f"{look['cumulative_figures']['flag_counts']} |"
    )
    lines += ["", "The Sharpe ratios above are descriptive.", *look["lines"], ""]
    return "\n".join(lines)


def _main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m forward.report")
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--look", type=int, required=True)
    ap.add_argument("--capital", type=float)
    ap.add_argument("--clock-start")
    ap.add_argument("--out", help="write the markdown here instead of stdout")
    args = ap.parse_args(argv)
    start = date.fromisoformat(args.clock_start) if args.clock_start else None
    text = render_markdown(
        six_month_look(
            Ledger(args.ledger).records(), args.look, clock_start=start, capital=args.capital
        )
    )
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(_main())
