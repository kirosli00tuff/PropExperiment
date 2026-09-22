"""Stage D.1d, Task 4: cumulative multiple-comparisons accounting, continued from D.1b.

Tooling, not a hypothesis. The denominator is the program's true trial count, carried
forward, never reset: Stage D.1's 23, C-H4 (24), Stage D.1d's 7 re-tests (RT1-RT7), and
every Family G hypothesis formalized under the declaration's rule. Every run goes through
the shared runner; nothing here builds an EngineConfig.

1. VERIFY CONTINUITY. Each of the prior 24 trials is re-run on the 289-day train union
   and must reproduce ``reports/stage_d1b_accounting.json``'s net P&L to the cent and its
   daily-series Sharpe to 1e-6, the discipline D.1b applied to D.1's 23.
2. ACCOUNT, cumulatively, with D.1b's own functions: DSR at N = cumulative trials, the
   Harvey/Liu/Zhu t > 3.0 hurdle, and CSCV PBO on 8 contiguous disjoint blocks.
3. CONTRAST: this session's trials alone, and a sensitivity with N widened by Family F's
   57 and this session's 28 declared EDA statistics.

    uv run python -m strategy.research._d1d_accounting

Writes reports/stage_d1d_accounting.json. Train dates only (the runner refuses others).
"""

from __future__ import annotations

import json
import multiprocessing as mp
from pathlib import Path

from screening.runner import _research_frame, screen_candidate, train_union_window
from strategy.research._d1b_accounting import (
    ALL_TRIALS as PRIOR_TRIALS,
)
from strategy.research._d1b_accounting import (
    F_EDA_STATISTICS,
    UNCONDITIONAL_LONGS,
    _dsr,
    _dsr_table,
    _moments,
    _pbo,
    _per_trial,
)
from strategy.research.g_timeframe.retests import RETESTS
from strategy.research.g_timeframe.trials import G_TRIALS

D1B_ACCOUNTING = Path("reports/stage_d1b_accounting.json")
OUTPUT_PATH = Path("reports/stage_d1d_accounting.json")
G_EDA_STATISTICS = 28  # this session's declared tested statistics (declaration section 3)

D1D_TRIALS = (*((label, factory) for label, _original, factory in RETESTS), *G_TRIALS)
ALL_TRIALS = (*PRIOR_TRIALS, *D1D_TRIALS)


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


def _verify_prior(runs: dict[str, dict]) -> list[str]:
    logged = json.loads(D1B_ACCOUNTING.read_text())
    problems = []
    for row in logged["runs"]:
        run = runs[row["label"]]
        if round(run["net_pnl_usd"], 2) != round(row["net_pnl_usd"], 2):
            problems.append(f"{row['label']}: net {run['net_pnl_usd']} != {row['net_pnl_usd']}")
        sharpe = _moments(run["daily_net_usd"])["sharpe"]
        want = logged["per_trial"][row["label"]]["sharpe"]
        if abs(sharpe - want) > 1e-6:
            problems.append(f"{row['label']}: daily Sharpe {sharpe:.6f} != {want:.6f}")
    return problems


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
    new = [label for label, _ in D1D_TRIALS]
    n_cum = len(labels)
    stats = {x: _moments(runs[x]["daily_net_usd"]) for x in labels}
    non_c = [x for x in labels if not x.startswith("C-H")]
    conditional = [x for x in labels if x not in UNCONDITIONAL_LONGS]
    problems = _verify_prior(runs)
    out = {
        "window": {"name": "train_union", "n_dates": len(train_union_window().trade_dates)},
        "n_trials_cumulative": n_cum,
        "n_trials_prior": len(PRIOR_TRIALS),
        "n_trials_this_session": len(new),
        "prior_continuity_problems": problems,
        "runs": [{k: v for k, v in r.items() if k != "daily_net_usd"} for r in results],
        "per_trial": _per_trial(stats),
        "dsr": {
            "cumulative": _dsr_table(stats, labels, n_cum),
            "cumulative_variance_excluding_family_c": _dsr_table(stats, non_c, n_cum),
            "this_session_only": _dsr_table(stats, new, len(new)) if len(new) > 1 else None,
            "this_session_uncorrected": {x: _dsr(stats[x], 1, 0.0) for x in new},
            "sensitivity_n_plus_f_and_g_eda": _dsr_table(
                stats, labels, n_cum + F_EDA_STATISTICS + G_EDA_STATISTICS),
        },
        "pbo": {
            "all_cumulative": _pbo(runs, labels),
            "excluding_family_c": _pbo(runs, non_c),
            "excluding_unconditional_longs": _pbo(runs, conditional),
            "this_session_only": _pbo(runs, new) if len(new) > 1 else None,
        },
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(f"wrote {OUTPUT_PATH}; N = {n_cum}; prior continuity problems: {len(problems)}")
    for p in problems:
        print("  PROBLEM", p)


if __name__ == "__main__":
    main()
