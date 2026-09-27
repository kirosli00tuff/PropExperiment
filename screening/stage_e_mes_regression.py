"""MES regressions of the generalized Stage E path (Stage E.2b Task 1, item 9).

``mes_new_path(label, factory, research_root)`` screens one D.1 trial through the Stage E code:
the Stage E bar loader (data.stage_e_bars: MES's research parquet, sha256-checked, every row booked
by the equity group calendar), D.1's own window (screening.runner.train_union_window, 289 dates),
the roll blackout from the group calendar, the generalized engine (screening.stage_e_engine) under
``MesRules`` and the Stage E trip and series code (screening.stage_e_runner.extract_trips). It
returns the fields D.1 recorded, so they can be compared bit for bit with D.1's output
(reports/stage_d1d_accounting.json) and with the unchanged screening.runner.screen_candidate.

A harness regression, not a Stage E entry point: it runs no Stage E member and needs no preflight.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from data.stage_e_bars import load_research_leg, restrict
from screening.stage_e_engine import DayClose, run_engine
from screening.stage_e_frozen import MES_RESEARCH_SHA256
from screening.stage_e_mes_rules import MesRules
from screening.stage_e_runner import extract_trips
from strategy.stage_e.interface import LegSpec

MES_LEGS = (LegSpec("MES", True),)
# (label, class, factory module attribute path) of the three regression trials, one per class,
# as reports/stage_d1f_confirmation_list.md 2.1 names them.
REGRESSION_TRIALS = (
    ("A-H2 rth close window (buy)", "C1"),
    ("B-H1 opening-range breakout (hold 75)", "C2"),
    ("D-H2 inverse-vol sizing", "C4"),
)


def regression_factory(label: str) -> Callable[[], Any]:
    """The D.1 factory of a regression trial, exactly as the lead's accounting built it."""
    from strategy.research._lead_accounting import TRIALS

    for name, factory in TRIALS:
        if name == label:
            return factory
    raise KeyError(f"{label!r} is not a D.1 trial")


def mes_new_path(label: str, factory: Callable[[], Any], research_root: Path) -> dict:
    from screening.runner import train_union_window
    from sim.costs import load_slippage_table

    window = train_union_window()
    leg = load_research_leg("MES", Path(research_root), expected_sha256=MES_RESEARCH_SHA256)
    missing = set(window.trade_dates) - set(leg.trade_dates)
    if missing:
        raise ValueError(f"no MES bars for {len(missing)} window dates, e.g. {min(missing)}")
    frame = restrict(leg, window.trade_dates)
    rules = MesRules(table=load_slippage_table(), roll_blackout=leg.roll_blackout)
    result = run_engine({"MES": frame}, factory(), MES_LEGS, rules)
    trips = extract_trips(result)
    by_date: dict = {}
    for d in result.events(DayClose):
        by_date[d.trade_date] = by_date.get(d.trade_date, 0) + d.day_net_cents
    dates = window.trade_dates
    daily_net_usd = tuple(float(by_date.get(d, 0) / 100.0) for d in dates)
    trip_pnls = tuple(t.net_cents / 100.0 for t in trips)
    counts: dict = {}
    for t in trips:
        counts[t.trade_date] = counts.get(t.trade_date, 0) + 1
    wins = [x for x in trip_pnls if x > 0.0]
    losses = [x for x in trip_pnls if x < 0.0]
    n = len(trip_pnls)
    mean_loss = abs(sum(losses) / len(losses)) if losses else 0.0
    return {
        "label": label, "n_dates": len(dates), "n_trips": n, "trades_per_day": n / len(dates),
        "net_pnl_usd": round(sum(trip_pnls), 2),
        "win_probability": (len(wins) / n) if n else None,
        "win_loss_ratio": ((sum(wins) / len(wins)) / mean_loss
                           if wins and losses and mean_loss > 0 else None),
        "daily_net_usd": daily_net_usd, "trip_pnls_usd": trip_pnls,
        "daily_n_trips": tuple(counts.get(d, 0) for d in dates),
        "trip_micros": tuple(t.contracts for t in trips),
        "blackout_dates_in_window": len(leg.roll_blackout & set(dates)),
        "bars_sha256": leg.sha256,
    }


__all__ = ["MES_LEGS", "REGRESSION_TRIALS", "mes_new_path", "regression_factory"]
