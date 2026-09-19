"""Stage D.1b, Task 3: cumulative multiple-comparisons accounting over EVERY trial so far.

Tooling, not a hypothesis. Owned by the lead. The denominator is the program's true
trial count, carried forward, never reset: Stage D.1's 23 trials, plus C-H4 (trial 24),
plus every Family F hypothesis formalized in Task 2c. Every run goes through the shared
runner (``screening.screen_candidate``); nothing here builds an EngineConfig.

1. VERIFY CONTINUITY. Each of D.1's 23 trials is re-run on the 289-day train union and
   must reproduce ``reports/stage_d1_accounting.json``'s net P&L to the cent, and its
   daily-series Sharpe to 1e-6. Otherwise this is not the same accounting D.1 did.
2. ACCOUNT, cumulatively: DSR at N = cumulative trials (Sharpe variance across all of
   them), Harvey/Liu/Zhu t > 3.0, and CSCV PBO on 8 contiguous disjoint blocks of the
   train union (D.1's approximation, unchanged).
3. CONTRAST. The same numbers judged against this session's trials alone (N = 1 + k),
   so a candidate that only looks significant against the small count is visible as such,
   and a sensitivity with N widened by Family F's 57 declared EDA statistics.

    uv run python -m strategy.research._d1b_accounting

Writes reports/stage_d1b_accounting.json. Train dates only (the runner refuses others).
"""

from __future__ import annotations

import json
import multiprocessing as mp
import statistics
from collections.abc import Callable
from itertools import combinations
from pathlib import Path

from funnel.multiple_comparisons import (
    deflated_sharpe_ratio,
    harvey_liu_zhu_verdict,
    probability_of_backtest_overfitting,
)
from screening.runner import _research_frame, screen_candidate, train_union_window
from strategy.research._lead_accounting import TRIALS as D1_TRIALS
from strategy.research.c_short_horizon_reversal.h4_passive_fill_reversal import (
    H4PassiveFillReversal,
)
from strategy.research.f_data_native.trials import F_TRIALS

D1_ACCOUNTING = Path("reports/stage_d1_accounting.json")
OUTPUT_PATH = Path("reports/stage_d1b_accounting.json")
N_PBO_BLOCKS = 8
F_EDA_STATISTICS = 57  # Family F's declared tested statistics (Task 2a), for the sensitivity
UNCONDITIONAL_LONGS = ("A-H1 european-open overnight drift", "A-H2 rth close window (buy)",
                       "A-H4 eth leg", "A-H4 rth leg")

D1B_TRIALS: tuple[tuple[str, Callable[[], object]], ...] = (
    ("C-H4 passive-fill reversal", H4PassiveFillReversal),
    *F_TRIALS,
)
ALL_TRIALS = (*D1_TRIALS, *D1B_TRIALS)


def _run(index: int) -> dict:
    label, factory = ALL_TRIALS[index]
    try:
        report = screen_candidate(label, factory, train_union_window())
    except Exception as exc:  # recorded, never swallowed: main() refuses to account
        return {"index": index, "label": label, "error": repr(exc)}
    return {"index": index, "label": label, "n_trips": report.n_trips,
            "trades_per_day": report.trades_per_day, "net_pnl_usd": report.net_pnl_usd,
            "win_probability": report.zero_edge.win_probability,
            "win_loss_ratio": report.zero_edge.win_loss_ratio,
            "robust": report.zero_edge.robust, "drift_verdict": report.drift_verdict,
            "verdict": report.verdict, "reasons": list(report.reasons),
            "daily_net_usd": list(report.daily_net_usd)}


def _moments(xs: list[float]) -> dict:
    n = len(xs)
    mean = statistics.fmean(xs)
    sd = statistics.pstdev(xs)
    if sd == 0:
        return {"n": n, "mean": mean, "sd": 0.0, "skew": 0.0, "kurtosis": 3.0, "sharpe": 0.0}
    skew = sum((x - mean) ** 3 for x in xs) / n / sd**3
    kurt = sum((x - mean) ** 4 for x in xs) / n / sd**4
    return {"n": n, "mean": mean, "sd": sd, "skew": skew, "kurtosis": kurt, "sharpe": mean / sd}


def _dsr(s: dict, n_trials: int, sharpe_variance: float) -> float | None:
    if s["sd"] <= 0:
        return None
    return deflated_sharpe_ratio(s["sharpe"], s["n"], n_trials, sharpe_variance,
                                 s["skew"], s["kurtosis"])["deflated_sharpe_ratio"]


def _dsr_table(stats: dict[str, dict], labels: list[str], n_trials: int) -> dict:
    """DSR for ``labels``: Sharpe variance taken across ``labels``, trial count ``n_trials``."""
    variance = statistics.pvariance([stats[x]["sharpe"] for x in labels])
    benchmark = deflated_sharpe_ratio(0.0, 2, n_trials, variance)["expected_max_sharpe_under_null"]
    return {"n_trials": n_trials, "sharpe_variance": variance,
            "expected_max_daily_sharpe_under_null": benchmark,
            "dsr": {x: _dsr(stats[x], n_trials, variance) for x in labels}}


def _blocks(series: list[float]) -> list[float]:
    width = len(series) // N_PBO_BLOCKS
    return [sum(series[b * width:(b + 1) * width]) for b in range(N_PBO_BLOCKS)]


def _pbo(runs: dict[str, dict], labels: list[str]) -> dict:
    matrix = [_blocks(runs[x]["daily_net_usd"]) for x in labels]
    result = probability_of_backtest_overfitting(matrix, N_PBO_BLOCKS)
    oos = []  # the in-sample winner's out-of-sample net, over the same splits CSCV forms
    for train in combinations(range(N_PBO_BLOCKS), N_PBO_BLOCKS // 2):
        test = [b for b in range(N_PBO_BLOCKS) if b not in train]
        best = max(range(len(labels)), key=lambda s: sum(matrix[s][b] for b in train))
        oos.append(sum(matrix[best][b] for b in test))
    return {"n_strategies": len(labels), "pbo": result.pbo, "n_splits": result.n_splits,
            "winner_mean_oos_net_usd": statistics.fmean(oos),
            "p_winner_positive_oos": sum(x > 0 for x in oos) / len(oos)}


def _verify_d1(runs: dict[str, dict]) -> list[str]:
    logged = json.loads(D1_ACCOUNTING.read_text())
    problems = []
    for row in logged["train_union_run"]:
        run = runs[row["label"]]
        if round(run["net_pnl_usd"], 2) != round(row["net_pnl_usd"], 2):
            problems.append(f"{row['label']}: net {run['net_pnl_usd']} != {row['net_pnl_usd']}")
        sharpe = _moments(run["daily_net_usd"])["sharpe"]
        want = logged["accounting"]["per_trial"][row["label"]]["sharpe"]
        if abs(sharpe - want) > 1e-6:
            problems.append(f"{row['label']}: daily Sharpe {sharpe:.6f} != {want:.6f}")
    return problems


def _per_trial(stats: dict[str, dict]) -> dict:
    out = {}
    for label, s in stats.items():
        entry = {k: round(v, 6) for k, v in s.items()}
        if s["sd"] > 0:
            hlz = harvey_liu_zhu_verdict(s["mean"], s["sd"], s["n"])
            entry |= {"t_stat": round(hlz["t_stat"], 4),
                      "passes_conventional_t2": hlz["passes_conventional"],
                      "passes_hlz_t3": hlz["passes_hlz"]}
        out[label] = entry
    return out


def main() -> None:
    _research_frame()  # load once in the parent; forked workers inherit the cache
    with mp.get_context("fork").Pool(processes=min(12, len(ALL_TRIALS))) as pool:
        results = pool.map(_run, range(len(ALL_TRIALS)), chunksize=1)
    errors = [r for r in results if "error" in r]
    if errors:
        raise SystemExit("runs errored: " + "; ".join(f"{r['label']}: {r['error']}"
                                                      for r in errors))
    runs = {r["label"]: r for r in results}
    labels = [label for label, _ in ALL_TRIALS]
    new = [label for label, _ in D1B_TRIALS]
    n_cum = len(labels)
    stats = {x: _moments(runs[x]["daily_net_usd"]) for x in labels}
    non_c = [x for x in labels if not x.startswith("C-H")]
    conditional = [x for x in labels if x not in UNCONDITIONAL_LONGS]
    problems = _verify_d1(runs)
    out = {
        "window": {"name": "train_union", "n_dates": len(train_union_window().trade_dates)},
        "n_trials_cumulative": n_cum,
        "d1_continuity_problems": problems,
        "runs": [{k: v for k, v in r.items() if k != "daily_net_usd"} for r in results],
        "per_trial": _per_trial(stats),
        "dsr": {
            "cumulative": _dsr_table(stats, labels, n_cum),
            "cumulative_variance_excluding_family_c": _dsr_table(stats, non_c, n_cum),
            "this_session_only": _dsr_table(stats, new, len(new)) if len(new) > 1 else None,
            "this_session_uncorrected": {x: _dsr(stats[x], 1, 0.0) for x in new},
            "sensitivity_n_plus_family_f_eda": _dsr_table(stats, labels,
                                                          n_cum + F_EDA_STATISTICS),
        },
        "pbo": {
            "all_cumulative": _pbo(runs, labels),
            "excluding_family_c": _pbo(runs, non_c),
            "excluding_unconditional_longs": _pbo(runs, conditional),
            "this_session_only": _pbo(runs, new) if len(new) > 1 else None,
        },
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(f"wrote {OUTPUT_PATH}; N = {n_cum}; D.1 continuity problems: {len(problems)}")
    for p in problems:
        print("  PROBLEM", p)


if __name__ == "__main__":
    main()
