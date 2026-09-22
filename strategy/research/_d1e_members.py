"""Stage D.1e, Task 1b: the per-trade and per-day trip distributions of every recorded trial.

Tooling, not a hypothesis. No new hypothesis is screened here and no parameter is changed,
so the cumulative trial count stays at N = 31: this re-runs the SAME 31 trials
(``strategy.research._d1d_accounting.ALL_TRIALS``) on the same 289-day train union through
the same shared runner, and records the distribution figures the Stage D.1e power
calculation consumes but the D.1d accounting never wrote down.

What comes out, per trial: the per-trade net series (mean, SD, range, in dollars), the
per-day net series over all 289 dates including the $0 days, the lag-1 autocorrelation of
both the daily net and the daily trip count, and the cluster variance-inflation factor
var(daily) / (T * var(per-trade)) that says how far from independent the trades within a
day are.

UNITS. The per-micro series (``*_per_micro``, ``daily_net_ticks_per_micro``) divides EACH
round trip by its OWN contract quantity: trip net / ($1.25 x that trip's micros). 29 of the
31 trials, and C-H4, code a fixed 1 micro; D-H2 and RT7 size 1 to 5 micros by rule, so no
single divisor is right for the fleet. The older ``per_trade``/``per_day`` blocks keep their
original ``*_ticks_per_micro`` figures, computed at a flat $2.50 (2 micros), so the
correction stays visible; they are superseded, and nothing new should read them.

CONTINUITY. Every run must reproduce ``reports/stage_d1d_accounting.json``'s net P&L to the
cent and its trip count exactly. Anything else is a harness change, not a re-run: the
problems are written to the output's ``meta.continuity_problems`` and the module exits
non-zero without deleting the output.

    uv run python -m strategy.research._d1e_members

Writes reports/stage_d1e_members_trials.json. Train dates only (the runner refuses others);
nothing here builds an EngineConfig or calls run_backtest.
"""

from __future__ import annotations

import hashlib
import json
import multiprocessing as mp
import sys
import time
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from types import CodeType

import numpy as np

from screening.runner import _research_frame, screen_candidate, train_union_window
from strategy.research._d1d_accounting import ALL_TRIALS

D1D_ACCOUNTING = Path("reports/stage_d1d_accounting.json")
RUNNER_PATH = Path("screening/runner.py")
OUTPUT_PATH = Path("reports/stage_d1e_members_trials.json")

TICK_VALUE_USD = 1.25  # MES, one micro, one tick
# The superseded divisor. This module's first pass assumed every trial traded 2 micros, which
# the Stage D.1e adversarial review found to be wrong. It survives only so the ``per_trade``
# and ``per_day`` blocks keep the exact figures that pass wrote, next to the corrected
# ``*_per_micro`` blocks. Nothing new should use it.
LEGACY_USD_PER_TICK_AT_2_MICROS = TICK_VALUE_USD * 2
UNIT_NOTE = (
    "per-micro series divide EACH round trip by its OWN contract quantity "
    "(trip net / ($1.25 x trip_micros)), not by one assumed size: 29 trials and C-H4 code "
    "1 micro, D-H2 and RT7 size 1..5 micros by rule. The per_trade/per_day "
    "*_ticks_per_micro fields are the superseded flat-$2.50 figures, kept for comparison."
)
MAX_WORKERS = 12


# ----------------------------------------------------------- the coded size ----
def _referenced_names(cls: type) -> frozenset[str]:
    """Every global name the class's own methods mention, nested code objects included."""
    names: set[str] = set()
    stack = [f.__code__ for f in vars(cls).values() if callable(f) and hasattr(f, "__code__")]
    while stack:
        code = stack.pop()
        names.update(code.co_names)
        stack.extend(c for c in code.co_consts if isinstance(c, CodeType))
    return frozenset(names)


def _coded_micros(strategy: object) -> str:
    """The position size the strategy's CODE declares, read off the module's constants rather
    than assumed per label: its sizing field when it has one, else the ``QUANTITY_MICROS`` or
    ``MIN/MAX_QUANTITY_MICROS`` constant its own methods reference. ``mean_trip_micros`` is the
    observed counterpart, so a disagreement between the two is visible."""
    low, high = (getattr(strategy, "min_quantity_micros", None),
                 getattr(strategy, "max_quantity_micros", None))
    if low is not None and high is not None:
        return f"{low}..{high} by rule"
    fixed = getattr(strategy, "quantity_micros", None)
    if fixed is not None:
        return str(fixed)
    cls = type(strategy)
    names = _referenced_names(cls)
    constants = vars(sys.modules[cls.__module__])
    if {"MIN_QUANTITY_MICROS", "MAX_QUANTITY_MICROS"} <= names:
        return (f"{constants['MIN_QUANTITY_MICROS']}..{constants['MAX_QUANTITY_MICROS']} "
                f"by rule")
    if "QUANTITY_MICROS" in names:
        return str(constants["QUANTITY_MICROS"])
    return "unknown"


# ------------------------------------------------------------------ the runs ----
def _run(index: int) -> dict:
    label, factory = ALL_TRIALS[index]
    try:
        report = screen_candidate(label, factory, train_union_window())
    except Exception as exc:  # recorded, never swallowed: main() refuses to write figures
        return {"index": index, "label": label, "error": repr(exc)}
    return {
        "index": index, "label": label,
        "n_trips": report.n_trips, "n_dates": report.n_dates,
        "trades_per_day": report.trades_per_day, "net_pnl_usd": report.net_pnl_usd,
        "win_probability": report.zero_edge.win_probability,
        "win_loss_ratio": report.zero_edge.win_loss_ratio,
        "exposure": report.exposure, "market_fills": report.market_fills,
        "passive_fills": report.passive_fills,
        "robust_verdict": report.zero_edge.robust, "drift_verdict": report.drift_verdict,
        "verdict": report.verdict,
        "coded_micros": _coded_micros(factory()),
        "daily_net_usd": list(report.daily_net_usd),
        "daily_n_trips": list(report.daily_n_trips),
        "trip_pnls_usd": list(report.trip_pnls_usd),
        "trip_micros": list(report.trip_micros),
    }


# ----------------------------------------------------------------- the stats ----
def _sd(values: Sequence[float]) -> float | None:
    """Sample SD (ddof=1); undefined on fewer than two observations."""
    return float(np.std(np.asarray(values, dtype=float), ddof=1)) if len(values) > 1 else None


def _var(values: Sequence[float]) -> float | None:
    return float(np.var(np.asarray(values, dtype=float), ddof=1)) if len(values) > 1 else None


def _lag1_autocorr(values: Sequence[float]) -> float | None:
    """Pearson correlation of the series with itself shifted one step. None when either leg is
    constant (a strategy that never traded, say): the correlation is not defined there."""
    x = np.asarray(values, dtype=float)
    if len(x) < 3:
        return None
    a, b = x[:-1], x[1:]
    if np.std(a) == 0.0 or np.std(b) == 0.0:
        return None
    return float(np.corrcoef(a, b)[0, 1])


def _legacy_ticks(usd: float | None) -> float | None:
    """SUPERSEDED: dollars at a flat $2.50/tick (2 micros). Kept so the ``per_trade`` and
    ``per_day`` blocks still report what the first pass reported. Use ``_trip_ticks_per_micro``,
    which divides each trip by its own quantity."""
    return None if usd is None else usd / LEGACY_USD_PER_TICK_AT_2_MICROS


def _trip_ticks_per_micro(trips: Sequence[float], micros: Sequence[int]) -> list[float]:
    """Each closed round trip's net in ticks PER MICRO: its dollars over $1.25 x its own
    contract quantity. The two series come from the same runner walk in the same order."""
    if len(trips) != len(micros):
        raise AssertionError(f"{len(trips)} trip P&Ls but {len(micros)} trip sizes")
    if any(q < 1 for q in micros):
        raise AssertionError(f"a trip reports {min(micros)} micros; every closed trip holds >= 1")
    return [pnl / (TICK_VALUE_USD * q) for pnl, q in zip(trips, micros, strict=True)]


def _daily_ticks_per_micro(trip_ticks: Sequence[float], daily_n_trips: Sequence[int]
                           ) -> list[float]:
    """Per window date, the sum of the per-micro nets of the trips that CLOSED that date, 0.0 on
    a date with no trip. ``daily_n_trips`` partitions the trip list in ledger order, exactly as
    the runner built the two series, so this is the per-micro twin of ``daily_net_usd``."""
    out: list[float] = []
    cut = 0
    for n in daily_n_trips:
        out.append(float(sum(trip_ticks[cut:cut + n])))
        cut += n
    if cut != len(trip_ticks):
        raise AssertionError(f"daily trip counts sum to {cut}, but the run holds "
                             f"{len(trip_ticks)} trips")
    return out


def _per_trade(trips: Sequence[float]) -> dict:
    mean = float(np.mean(trips)) if trips else None
    sd = _sd(trips)
    return {"mean_usd": mean, "sd_usd": sd,
            "mean_ticks_per_micro": _legacy_ticks(mean),
            "sd_ticks_per_micro": _legacy_ticks(sd),
            "min_usd": min(trips) if trips else None, "max_usd": max(trips) if trips else None,
            "n": len(trips)}


def _per_day(daily: Sequence[float], daily_trips: Sequence[int]) -> dict:
    mean = float(np.mean(daily)) if daily else None
    sd = _sd(daily)
    sharpe = (mean / sd) if (mean is not None and sd not in (None, 0.0)) else None
    return {"mean_usd": mean, "sd_usd": sd,
            "mean_ticks_per_micro": _legacy_ticks(mean),
            "sd_ticks_per_micro": _legacy_ticks(sd),
            "lag1_autocorr": _lag1_autocorr(daily),
            "lag1_autocorr_trips": _lag1_autocorr(daily_trips),
            "sharpe_daily": sharpe}


def _per_trade_per_micro(trip_ticks: Sequence[float]) -> dict:
    """The per-trade distribution in ticks per micro, each trip divided by its own quantity."""
    return {"mean_ticks_per_micro": float(np.mean(trip_ticks)) if trip_ticks else None,
            "sd_ticks_per_micro": _sd(trip_ticks), "n": len(trip_ticks)}


def _per_day_per_micro(daily_ticks: Sequence[float]) -> dict:
    """The per-day distribution in ticks per micro, over every window date including $0 days."""
    return {"mean_ticks_per_micro": float(np.mean(daily_ticks)) if daily_ticks else None,
            "sd_ticks_per_micro": _sd(daily_ticks),
            "lag1_autocorr": _lag1_autocorr(daily_ticks)}


def _cluster_vif(daily: Sequence[float], trips: Sequence[float], trades_per_day: float
                 ) -> float | None:
    """var(daily net) / (T * var(per-trade net)): 1.0 when the trades inside a day are
    independent, above 1.0 when they move together (the power calculation's cluster penalty)."""
    if len(trips) < 2:
        return None
    var_day, var_trade = _var(daily), _var(trips)
    if var_day is None or var_trade in (None, 0.0) or trades_per_day == 0.0:
        return None
    return var_day / (trades_per_day * var_trade)


def _member(run: dict) -> dict:
    daily, trips, micros = run["daily_net_usd"], run["trip_pnls_usd"], run["trip_micros"]
    trip_ticks = _trip_ticks_per_micro(trips, micros)
    daily_ticks = _daily_ticks_per_micro(trip_ticks, run["daily_n_trips"])
    return {
        "n_trips": run["n_trips"], "n_dates": run["n_dates"],
        "trades_per_day": run["trades_per_day"],
        "n_days_with_trades": sum(1 for n in run["daily_n_trips"] if n),
        "coded_micros": run["coded_micros"],
        "mean_trip_micros": float(np.mean(micros)) if micros else None,
        "win_probability": run["win_probability"], "win_loss_ratio": run["win_loss_ratio"],
        "net_pnl_usd": run["net_pnl_usd"],
        "per_trade": _per_trade(trips),
        "per_day": _per_day(daily, run["daily_n_trips"]),
        "per_trade_per_micro": _per_trade_per_micro(trip_ticks),
        "per_day_per_micro": _per_day_per_micro(daily_ticks),
        "cluster_vif": _cluster_vif(daily, trips, run["trades_per_day"]),
        "exposure": run["exposure"], "market_fills": run["market_fills"],
        "passive_fills": run["passive_fills"],
        "robust_verdict": run["robust_verdict"], "drift_verdict": run["drift_verdict"],
        "verdict": run["verdict"],
        "daily_net_usd": daily, "daily_n_trips": run["daily_n_trips"], "trip_pnls_usd": trips,
        "trip_micros": micros, "daily_net_ticks_per_micro": daily_ticks,
    }


# ------------------------------------------------------------- the continuity ----
def _continuity_problems(runs: dict[str, dict]) -> list[str]:
    """Every re-run must reproduce D.1d's recorded net to the cent and its trip count exactly."""
    logged = json.loads(D1D_ACCOUNTING.read_text())
    problems = []
    for row in logged["runs"]:
        run = runs.get(row["label"])
        if run is None:
            problems.append(f"{row['label']}: recorded in D.1d but not re-run here")
            continue
        if round(run["net_pnl_usd"], 2) != round(row["net_pnl_usd"], 2):
            problems.append(f"{row['label']}: net {run['net_pnl_usd']} != {row['net_pnl_usd']}")
        if run["n_trips"] != row["n_trips"]:
            problems.append(f"{row['label']}: n_trips {run['n_trips']} != {row['n_trips']}")
    return problems


def main() -> None:
    started = time.monotonic()
    window = train_union_window()
    _research_frame()  # load once in the parent; forked workers inherit the cache
    with mp.get_context("fork").Pool(processes=min(MAX_WORKERS, len(ALL_TRIALS))) as pool:
        results = pool.map(_run, range(len(ALL_TRIALS)), chunksize=1)
    errors = [r for r in results if "error" in r]
    if errors:
        raise SystemExit("runs errored: " + "; ".join(f"{r['label']}: {r['error']}"
                                                      for r in errors))
    runs = {r["label"]: r for r in results}
    problems = _continuity_problems(runs)
    out = {
        "meta": {
            "generated_utc": datetime.now(UTC).isoformat(timespec="seconds"),
            "window": {"name": window.name, "n_dates": len(window.trade_dates),
                       "first_date": str(window.trade_dates[0]),
                       "last_date": str(window.trade_dates[-1])},
            "n_trials": len(ALL_TRIALS),
            "tick_value_usd": TICK_VALUE_USD, "unit_note": UNIT_NOTE,
            "runtime_seconds": round(time.monotonic() - started, 1),
            "runner_sha256": hashlib.sha256(RUNNER_PATH.read_bytes()).hexdigest(),
            "continuity_problems": problems,
        },
        "members": {label: _member(runs[label]) for label, _ in ALL_TRIALS},
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(f"wrote {OUTPUT_PATH}; {len(ALL_TRIALS)} trials in "
          f"{out['meta']['runtime_seconds']} s; continuity problems: {len(problems)}")
    for p in problems:
        print("  PROBLEM", p)
    if problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
