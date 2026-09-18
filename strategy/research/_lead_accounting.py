"""Stage D.1 lead accounting: independent re-run of every screened trial, plus Task 4.

Tooling, not a hypothesis. Owned by the lead, not a family subagent, because it
is where the program decides whether a result is real:

1. VERIFY. Re-runs all 23 trials on fold 0's train dates through the real engine
   and fill model, and records p / R / T / net so they can be compared against
   what each family's subagent reported. A mismatch means a subagent's number is
   not trustworthy, whatever its verdict said.
2. ACCOUNT. Re-runs every trial once over the union of all 8 folds' TRAIN dates
   (never a test-only date, never the holdout) to get a daily net-P&L series,
   then applies the three named corrections in ``funnel.multiple_comparisons``:
   Deflated Sharpe Ratio with N = every trial logged (not just passers), the
   Harvey/Liu/Zhu t > 3.0 hurdle, and CSCV probability of backtest overfitting.

PBO approximation, stated rather than hidden: CSCV assumes disjoint observation
blocks. The 8 walk-forward TRAIN windows overlap heavily (142-day windows
stepping 21 days), so they cannot be used as CSCV blocks directly. Instead the
train-date union is cut into 8 contiguous, equal-length, disjoint blocks.

    uv run python -m strategy.research._lead_accounting

Writes reports/stage_d1_accounting.json. Never touches test-only dates or the
sealed holdout: every date it loads comes from ``fold.train_dates``.
"""

from __future__ import annotations

import json
import math
import multiprocessing as mp
import statistics
from collections.abc import Callable
from pathlib import Path

import pandas as pd

from data.research_bars import RESEARCH_SERIES_PATH, load_research_bars
from data.splits import walk_forward_folds
from funnel.multiple_comparisons import (
    deflated_sharpe_ratio,
    harvey_liu_zhu_verdict,
    probability_of_backtest_overfitting,
)
from sim.costs import load_slippage_table
from sim.engine import (
    BAR_COLUMNS,
    EngineConfig,
    daily_net_pnl,
    iter_bars,
    roll_blackout_dates,
    run_backtest,
    splice_trade_dates_from_parquet,
)
from strategy.research.a_session_clock.h1_european_open_overnight_drift import (
    H1EuropeanOpenOvernightDrift,
)
from strategy.research.a_session_clock.h2_rth_close_window_session_position import (
    H2RthCloseWindowSessionPosition,
)
from strategy.research.a_session_clock.h3_weekend_effect import H3WeekendEffect
from strategy.research.a_session_clock.h4_eth_vs_rth_decomposition import H4EthVsRthDecomposition
from strategy.research.b_reference_breakout.h1_friction_aware_opening_range_breakout import (
    H1FrictionAwareOpeningRangeBreakout,
)
from strategy.research.b_reference_breakout.h2_prior_day_stop_cascade import H2PriorDayStopCascade
from strategy.research.b_reference_breakout.h3_breakout_vs_fade_horse_race import (
    H3BreakoutLeg,
    H3FadeLeg,
)
from strategy.research.b_reference_breakout.h4_narrow_range_contraction_breakout import (
    H4NarrowRangeContractionBreakout,
)
from strategy.research.c_short_horizon_reversal.h1_magnitude_conditioned_reversal import (
    H1MagnitudeConditionedReversal,
)
from strategy.research.c_short_horizon_reversal.h2_post_spike_exhaustion_fade import (
    H2PostSpikeExhaustionFade,
)
from strategy.research.c_short_horizon_reversal.h3_close_location_value_reversal import (
    H3CloseLocationValueReversal,
)
from strategy.research.d_volatility_state._metrics import measure
from strategy.research.d_volatility_state.h1_trailing_volatility_regime_gate import (
    H1TrailingVolatilityRegimeGate,
)
from strategy.research.d_volatility_state.h2_inverse_volatility_sizing import (
    H2InverseVolatilitySizing,
)
from strategy.research.d_volatility_state.h3_range_compression_gate import H3RangeCompressionGate
from strategy.research.d_volatility_state.h4_overnight_gap_fade import H4OvernightGapFade
from strategy.research.e_calendar_event.h1_scheduled_macro_drift import H1ScheduledMacroDrift
from strategy.research.e_calendar_event.h2_post_release_momentum import H2PostReleaseMomentum
from strategy.research.e_calendar_event.h3_quarterly_witching import H3QuarterlyWitchingShort
from strategy.research.e_calendar_event.h4_turn_of_month import H4TurnOfMonthLong

OUTPUT_PATH = Path("reports/stage_d1_accounting.json")
N_PBO_BLOCKS = 8
BLACKOUT_SESSIONS = 2  # same roll blackout family D's runner used

# Every trial any family ran, in the order the families reported them. C-H4 is
# absent on purpose: it was never runnable (no passive order type), so it is a
# logged hypothesis but not a trial.
TRIALS: tuple[tuple[str, Callable[[], object]], ...] = (
    ("A-H1 european-open overnight drift", H1EuropeanOpenOvernightDrift),
    ("A-H2 rth close window (buy)", lambda: H2RthCloseWindowSessionPosition(direction="buy")),
    ("A-H2 rth close window (sell)", lambda: H2RthCloseWindowSessionPosition(direction="sell")),
    ("A-H3 weekend effect", H3WeekendEffect),
    ("A-H4 eth leg", lambda: H4EthVsRthDecomposition(session="eth")),
    ("A-H4 rth leg", lambda: H4EthVsRthDecomposition(session="rth")),
    ("B-H1 opening-range breakout (hold 5)",
     lambda: H1FrictionAwareOpeningRangeBreakout(hold_minutes=5)),
    ("B-H1 opening-range breakout (hold 75)",
     lambda: H1FrictionAwareOpeningRangeBreakout(hold_minutes=75)),
    ("B-H2 prior-day stop cascade", H2PriorDayStopCascade),
    ("B-H3 breakout leg", H3BreakoutLeg),
    ("B-H3 fade leg", H3FadeLeg),
    ("B-H4 narrow-range breakout", H4NarrowRangeContractionBreakout),
    ("C-H1 magnitude-conditioned reversal", H1MagnitudeConditionedReversal),
    ("C-H2 post-spike exhaustion fade", H2PostSpikeExhaustionFade),
    ("C-H3 close-location-value reversal", H3CloseLocationValueReversal),
    ("D-H1 trailing-vol regime gate", H1TrailingVolatilityRegimeGate),
    ("D-H2 inverse-vol sizing", H2InverseVolatilitySizing),
    ("D-H3 range-compression gate", H3RangeCompressionGate),
    ("D-H4 overnight gap fade", H4OvernightGapFade),
    ("E-H1 scheduled macro drift", H1ScheduledMacroDrift),
    ("E-H2 post-release momentum", H2PostReleaseMomentum),
    ("E-H3 quarterly witching short", H3QuarterlyWitchingShort),
    ("E-H4 turn-of-month long", H4TurnOfMonthLong),
)

# Populated once in the parent and inherited by forked workers.
_FRAME: pd.DataFrame | None = None
_DATE_SETS: dict[str, tuple] = {}


def _as_date(value):
    return pd.Timestamp(value).date()


def _setup() -> None:
    global _FRAME
    _FRAME = load_research_bars(BAR_COLUMNS)
    dates = sorted({_as_date(d) for d in _FRAME["trade_date"].unique()})
    folds = walk_forward_folds(dates)
    _DATE_SETS["fold0_train"] = tuple(folds[0].train_dates)
    _DATE_SETS["train_union"] = tuple(sorted({d for f in folds for d in f.train_dates}))


def _run(job: tuple[int, str]) -> dict:
    index, window = job
    label, factory = TRIALS[index]
    wanted = set(_DATE_SETS[window])
    sub = _FRAME[_FRAME["trade_date"].map(lambda d: _as_date(d) in wanted)]
    blackout = roll_blackout_dates(splice_trade_dates_from_parquet(RESEARCH_SERIES_PATH),
                                   BLACKOUT_SESSIONS)
    config = EngineConfig(restart_on_terminal=True, roll_blackout=blackout)
    try:
        result = run_backtest(iter_bars(sub), factory(), config, load_slippage_table())
    except Exception as exc:  # recorded, never swallowed: the report shows it
        return {"index": index, "label": label, "window": window, "error": repr(exc)}
    m = measure(result, len(wanted))
    days = daily_net_pnl(result)
    by_date = days.groupby("trade_date")["day_net_cents"].sum() / 100.0
    series = [float(by_date.get(d, 0.0)) for d in _DATE_SETS[window]]
    return {"index": index, "label": label, "window": window, "n_trips": m.n_trips,
            "win_probability": m.win_probability, "win_loss_ratio": m.win_loss_ratio,
            "trades_per_day": m.trades_per_day, "net_pnl_usd": round(m.net_pnl_usd, 2),
            "daily_net_usd": series}


def _moments(xs: list[float]) -> dict:
    n = len(xs)
    mean = statistics.fmean(xs)
    sd = statistics.pstdev(xs)
    if sd == 0:
        return {"n": n, "mean": mean, "sd": 0.0, "skew": 0.0, "kurtosis": 3.0, "sharpe": 0.0}
    skew = sum((x - mean) ** 3 for x in xs) / n / sd**3
    kurt = sum((x - mean) ** 4 for x in xs) / n / sd**4
    return {"n": n, "mean": mean, "sd": sd, "skew": skew, "kurtosis": kurt, "sharpe": mean / sd}


def _per_trial_entry(s: dict, n_trials: int, sharpe_variance: float) -> dict:
    entry = {k: round(v, 6) for k, v in s.items()}
    if s["sd"] <= 0:
        return entry
    try:
        dsr = deflated_sharpe_ratio(s["sharpe"], s["n"], n_trials, sharpe_variance,
                                    s["skew"], s["kurtosis"])
        entry["dsr"] = round(dsr["deflated_sharpe_ratio"], 6)
        entry["dsr_null_max_sharpe"] = round(dsr["expected_max_sharpe_under_null"], 6)
    except ValueError as exc:
        entry["dsr_error"] = str(exc)
    hlz = harvey_liu_zhu_verdict(s["mean"], s["sd"], s["n"])
    entry["t_stat"] = round(hlz["t_stat"], 4)
    entry["passes_conventional_t2"] = hlz["passes_conventional"]
    entry["passes_hlz_t3"] = hlz["passes_hlz"]
    return entry


def _account(union_runs: list[dict]) -> dict:
    ok = [r for r in union_runs if "error" not in r]
    n_trials = len(TRIALS)
    stats = {r["label"]: _moments(r["daily_net_usd"]) for r in ok}
    sharpes = [s["sharpe"] for s in stats.values()]
    sharpe_variance = statistics.pvariance(sharpes) if len(sharpes) > 1 else 0.0
    per_trial = {label: _per_trial_entry(s, n_trials, sharpe_variance)
                 for label, s in stats.items()}

    n_days = len(ok[0]["daily_net_usd"]) if ok else 0
    block_len = n_days // N_PBO_BLOCKS
    matrix = [[sum(r["daily_net_usd"][b * block_len:(b + 1) * block_len])
               for b in range(N_PBO_BLOCKS)] for r in ok]
    pbo = probability_of_backtest_overfitting(matrix, N_PBO_BLOCKS)
    return {
        "n_trials_logged": n_trials,
        "n_trials_run_ok": len(ok),
        "sharpe_variance_across_trials": sharpe_variance,
        "per_trial": per_trial,
        "pbo": {"value": pbo.pbo, "n_splits": pbo.n_splits, "n_strategies": pbo.n_strategies,
                "degenerate": pbo.degenerate, "block_length_days": block_len,
                "dropped_trailing_days": n_days - block_len * N_PBO_BLOCKS, "note": pbo.note},
        "pbo_block_net_usd": {r["label"]: [round(x, 2) for x in row]
                              for r, row in zip(ok, matrix, strict=True)},
    }


def main() -> None:
    _setup()
    jobs = [(i, w) for w in ("fold0_train", "train_union") for i in range(len(TRIALS))]
    with mp.get_context("fork").Pool(processes=min(12, len(jobs))) as pool:
        runs = pool.map(_run, jobs, chunksize=1)
    fold0 = [r for r in runs if r["window"] == "fold0_train"]
    union = [r for r in runs if r["window"] == "train_union"]
    out = {
        "windows": {k: {"n_dates": len(v), "first": str(v[0]), "last": str(v[-1])}
                    for k, v in _DATE_SETS.items()},
        "fold0_rerun": [{k: v for k, v in r.items() if k != "daily_net_usd"} for r in fold0],
        "train_union_run": [{k: v for k, v in r.items() if k != "daily_net_usd"} for r in union],
        "accounting": _account(union),
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(f"wrote {OUTPUT_PATH}")
    bad = [r for r in runs if "error" in r]
    if bad:
        print(f"{len(bad)} runs errored: " + "; ".join(f"{r['label']}/{r['window']}" for r in bad))
    if not math.isnan(out["accounting"]["pbo"]["value"]):
        print(f"PBO = {out['accounting']['pbo']['value']:.3f}")


if __name__ == "__main__":
    main()
