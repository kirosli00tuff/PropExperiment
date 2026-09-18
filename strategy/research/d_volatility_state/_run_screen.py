"""Stage D.1 screening runner for family D (volatility/liquidity state).

Tooling, not a hypothesis: runs each formalized module in this package
against train-fold-only MES bars, measures p/R/T from the ledger via
``_metrics.py``, and prints both the matched and robust ``funnel.power_gate``
verdicts. Any module whose ROBUST verdict is "pass" on fold 0 is re-run
across all 8 train folds and its per-fold spread is printed.

    uv run python -m strategy.research.d_volatility_state._run_screen

Never touches fold.test_dates or the sealed holdout.
"""

from __future__ import annotations

import json
import time

import pandas as pd

from data.research_bars import RESEARCH_SERIES_PATH, load_research_bars
from data.splits import walk_forward_folds
from funnel.power_gate import screen
from sim.costs import load_slippage_table
from sim.engine import (
    BAR_COLUMNS,
    EngineConfig,
    iter_bars,
    roll_blackout_dates,
    run_backtest,
    splice_trade_dates_from_parquet,
)
from strategy.research.d_volatility_state._metrics import measure, nearest_segments_per_day
from strategy.research.d_volatility_state.h1_trailing_volatility_regime_gate import (
    H1TrailingVolatilityRegimeGate,
)
from strategy.research.d_volatility_state.h2_inverse_volatility_sizing import (
    H2InverseVolatilitySizing,
)
from strategy.research.d_volatility_state.h3_range_compression_gate import (
    H3RangeCompressionGate,
)
from strategy.research.d_volatility_state.h4_overnight_gap_fade import H4OvernightGapFade

HYPOTHESES = {
    "H1": H1TrailingVolatilityRegimeGate,
    "H2": H2InverseVolatilitySizing,
    "H3": H3RangeCompressionGate,
    "H4": H4OvernightGapFade,
}


def _sub_for_dates(frame: pd.DataFrame, dates: set) -> pd.DataFrame:
    mask = frame["trade_date"].map(lambda d: pd.Timestamp(d).date() in dates)
    return frame[mask]


def _run_one(strategy_cls, sub: pd.DataFrame, n_dates: int, table, config) -> dict:
    strategy = strategy_cls()
    t0 = time.monotonic()
    result = run_backtest(iter_bars(sub), strategy, config, table)
    elapsed = time.monotonic() - t0
    m = measure(result, n_dates)
    out = {"elapsed_s": round(elapsed, 2), "n_trips": m.n_trips, "n_trade_dates": m.n_trade_dates,
           "win_probability": m.win_probability, "win_loss_ratio": m.win_loss_ratio,
           "trades_per_day": m.trades_per_day, "net_pnl_usd": round(m.net_pnl_usd, 2)}
    if m.win_probability is None or m.win_loss_ratio is None:
        out["matched_verdict"] = "no_measurable_edge_insufficient_wins_or_losses"
        out["robust_verdict"] = "no_measurable_edge_insufficient_wins_or_losses"
        out["segments_per_day_used"] = None
        return out
    t_used = nearest_segments_per_day(m.trades_per_day)
    out["segments_per_day_used"] = t_used
    out["segments_per_day_is_approximation"] = t_used != round(m.trades_per_day)
    matched = screen("standard", m.win_probability, m.win_loss_ratio, t_used)
    robust = screen("standard", m.win_probability, m.win_loss_ratio, t_used, robust=True)
    out["matched_verdict"] = matched["verdict"]
    out["robust_verdict"] = robust["verdict"]
    return out


def main() -> None:
    table = load_slippage_table()
    # A held position may not span a contract-roll splice (an engine invariant, not a
    # tunable choice); blackout the splice trade date plus the 2 sessions before it, the
    # same window tests/test_leakage_canaries.py uses.
    blackout = roll_blackout_dates(splice_trade_dates_from_parquet(RESEARCH_SERIES_PATH), 2)
    config = EngineConfig(restart_on_terminal=True, roll_blackout=blackout)
    frame = load_research_bars(BAR_COLUMNS)
    dates = sorted({pd.Timestamp(d).date() for d in frame["trade_date"].unique()})
    folds = walk_forward_folds(dates)

    report: dict = {"fold0_screen": {}, "extended_folds": {}}

    fold0_train = set(folds[0].train_dates)
    sub0 = _sub_for_dates(frame, fold0_train)
    for tag, cls in HYPOTHESES.items():
        print(f"=== {tag} :: fold 0 (train, {len(fold0_train)} dates) ===", flush=True)
        result = _run_one(cls, sub0, len(fold0_train), table, config)
        print(json.dumps(result, indent=2), flush=True)
        report["fold0_screen"][tag] = result

        if result["robust_verdict"] == "pass":
            print(f"--- {tag} cleared the ROBUST verdict on fold 0: extending to all 8 "
                  f"train folds ---", flush=True)
            per_fold = []
            for fold in folds:
                train_dates = set(fold.train_dates)
                sub = _sub_for_dates(frame, train_dates)
                r = _run_one(cls, sub, len(train_dates), table, config)
                r["fold_index"] = fold.index
                per_fold.append(r)
                print(json.dumps(r, indent=2), flush=True)
            report["extended_folds"][tag] = per_fold

    print("=== SUMMARY (JSON) ===", flush=True)
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
