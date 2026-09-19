"""Stage D.1b: screen C-H4 (passive-fill magnitude-conditioned reversal) on fold 0's
train window. One call, per docs/SCREENING.md -- this is trial #24.

    uv run python -m strategy.research._d1b_ch4_fold0

Writes reports/stage_d1b_ch4_fold0.json and prints the key figures the lead reviews.
"""

from __future__ import annotations

import json
from pathlib import Path

from screening import fold_train_window, screen_candidate
from strategy.research.c_short_horizon_reversal.h4_passive_fill_reversal import (
    H4PassiveFillReversal,
)

OUTPUT_PATH = Path("reports/stage_d1b_ch4_fold0.json")


def main() -> None:
    report = screen_candidate(
        "C-H4 passive-fill reversal", H4PassiveFillReversal, fold_train_window(0)
    )
    OUTPUT_PATH.write_text(json.dumps(report.to_dict(), indent=1, default=str) + "\n")

    zero_edge = report.zero_edge
    print(f"wrote {OUTPUT_PATH}")
    print(f"n_trips: {report.n_trips}")
    print(f"trades_per_day: {report.trades_per_day}")
    print(f"net_pnl_usd: {report.net_pnl_usd}")
    print(f"p/R: {zero_edge.win_probability} / {zero_edge.win_loss_ratio}")
    print(f"zero_edge.robust: {zero_edge.robust}")
    print(f"drift_verdict: {report.drift_verdict}")
    print(f"verdict: {report.verdict}")
    print(f"reasons: {report.reasons}")
    print(f"market_fills: {report.market_fills}")
    print(f"passive_fills: {report.passive_fills}")
    print(f"passive_orders_placed: {report.passive_orders_placed}")
    print(f"exposure: {report.exposure}")


if __name__ == "__main__":
    main()
