"""H6's per-test records and descriptive outputs (prereg sections 4-6), from engine runs.

Descriptive only (never in the verdict): per-year results (section 6's five buckets: n, means,
t_B, p, net dollars, Sharpe over the bucket's equity trade dates); the 1.5 x slippage stress (each
fill's slippage re-priced from its own cost components with the frozen rounding,
screening.stage_e_frozen.slippage_cents(qty, 1.5 x slippage ticks, tick value), commission
unchanged); gross and net per trade in bp of the entry fill price; trade counts by exit type; the
outcome of every scheduled entry (traded, or the engine's refusal or cancellation reason); MLL
breach dates; the overlap window, reported separately.
"""

from __future__ import annotations

import dataclasses
from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import UTC, date, datetime
from fractions import Fraction
from typing import Any

import numpy as np

from h6_rod import constants as K
from h6_rod import stats
from h6_rod.signal import Schedule

NS_PER_S = 1_000_000_000
NS_PER_BAR = 60 * NS_PER_S


def _iso(ns: int) -> str:
    return datetime.fromtimestamp(ns // NS_PER_S, tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _exact(value: Fraction | int) -> int | str:
    v = Fraction(value)
    return v.numerator if v.denominator == 1 else f"{v.numerator}/{v.denominator}"


def trade_rows(trades: Sequence[stats.Trade], rules: Any) -> list[dict[str, Any]]:
    return [{"trade_date": t.trade_date.isoformat(), "side": t.side,
             "entry_fill_utc": _iso(t.entry_ts_ns), "exit_fill_utc": _iso(t.exit_ts_ns),
             "entry_price": t.entry_price, "exit_price": t.exit_price,
             "gross_ticks": stats.ticks(t.gross_cents, rules),
             "cost_ticks": stats.ticks(t.cost_cents, rules),
             "net_ticks": stats.ticks(t.net_cents, rules),
             "gross_cents": _exact(t.gross_cents), "commission_cents": t.commission_cents,
             "slippage_cents": t.slippage_cents, "net_cents": _exact(t.net_cents),
             "slippage_ticks_by_fill": list(t.slippage_ticks_by_fill),
             "event_window_by_fill": list(t.event_window_by_fill),
             "exit_reason": t.exit_reason, "exit_type": t.exit_type, "n_fills": t.n_fills,
             "account_index": t.account_index, "price_check_ok": t.price_check_ok}
            for t in trades]


def entry_outcomes(result: Any, schedule: Schedule) -> dict[str, Any]:
    """Every scheduled entry's outcome: "traded", the engine's refusal reason of the intent, or
    "cancelled:<reason>" for an accepted order the engine cancelled at the fill."""
    from screening.stage_e_engine import Cancel, Fill, IntentRecord

    decision = {e.entry_bar_ns + NS_PER_BAR: d for d, e in schedule.entries.items()}
    intents = {r.decision_ts_ns: r for r in result.events(IntentRecord)
               if r.decision_ts_ns in decision and r.position_before == 0}
    opened = {f.decision_ts_ns: f for f in result.events(Fill) if f.opening}
    cancels = {c.decision_ts_ns: c for c in result.events(Cancel) if c.decision_ts_ns in decision}
    by_date: dict[str, str] = {}
    deferred = 0
    for ns, day in sorted(decision.items()):
        rec = intents.get(ns)
        if rec is None:
            outcome = "no_entry_intent"
        elif not rec.accepted:
            outcome = rec.refusal.reason if rec.refusal is not None else "refused"
        elif ns in opened:
            outcome = "traded"
            deferred += int(opened[ns].minutes_after_decision > 0)
        elif ns in cancels:
            outcome = f"cancelled:{cancels[ns].reason}"
        else:
            outcome = "accepted_unfilled"
        by_date[day.isoformat()] = outcome
    counts = Counter(by_date.values())
    return {"scheduled": len(decision), "counts": dict(sorted(counts.items())),
            "filled_after_deferral": deferred,
            "not_traded": {d: o for d, o in by_date.items() if o != "traded"}}


def mll_record(result: Any) -> dict[str, Any]:
    from screening.stage_e_engine import DayClose, Fill

    breaches = sorted({e.trade_date.isoformat() for e in result.events(DayClose)
                       if e.breach is not None})
    liquidations = sorted({f.trade_date.isoformat() for f in result.events(Fill)
                           if f.reason == "mll_liquidation" and f.trade_date is not None})
    return {"accounts_started": int(result.accounts_started), "breach_dates": breaches,
            "mll_liquidation_fill_dates": liquidations}


def _stressed(t: stats.Trade, rules: Any) -> stats.Trade:
    from screening.stage_e_frozen import slippage_cents

    tv = rules.tick_value(K.VEHICLE)
    slip = sum(slippage_cents(q, K.STRESS_SLIPPAGE_MULTIPLE * s, tv)
               for q, s in zip(t.qty_by_fill, t.slippage_ticks_by_fill, strict=True))
    return dataclasses.replace(t, slippage_cents=int(slip))


def stress(test_id: str, trades: Sequence[stats.Trade], days: Sequence[date], rules: Any
           ) -> dict[str, Any]:
    hit = [_stressed(t, rules) for t in trades]
    core = stats.core_numbers(f"{test_id}-stress", hit, days, rules)
    core["cost_bar_under_stress"] = bool(core["mean_gross_ticks"]
                                         >= K.COST_MULTIPLE * core["mean_cost_ticks"])
    core["multiple"] = K.STRESS_SLIPPAGE_MULTIPLE
    return core


def basis_points(trades: Sequence[stats.Trade], rules: Any) -> dict[str, float]:
    point = rules.ticks_price(K.VEHICLE, 1)  # MNQ vendor tick in index points
    gross = [stats.ticks(t.gross_cents, rules) * point / t.entry_price * K.BP_PER_UNIT
             for t in trades]
    net = [stats.ticks(t.net_cents, rules) * point / t.entry_price * K.BP_PER_UNIT
           for t in trades]

    def m(xs: list[float], f: Any) -> float:
        return float(f(xs)) if xs else float("nan")

    return {"mean_gross_bp": m(gross, np.mean), "median_gross_bp": m(gross, np.median),
            "mean_net_bp": m(net, np.mean), "median_net_bp": m(net, np.median)}


def per_year(test_id: str, trades: Sequence[stats.Trade], days: Sequence[date], rules: Any
             ) -> dict[str, Any]:
    out = {}
    for label, lo, hi in K.YEAR_BUCKETS:
        sub_days = [d for d in days if lo <= d <= hi]
        sub = [t for t in trades if lo <= t.trade_date <= hi]
        out[label] = stats.core_numbers(f"{test_id}-{label}", sub, sub_days, rules)
    return out


def window_record(test: str, run: Any, schedule: Schedule, days: Sequence[date],
                  shortened: Mapping[date, bool], *, verdict: bool) -> dict[str, Any]:
    """One test on one window: the numbers, the exclusions and the descriptive outputs."""
    test_id = K.TEST_IDS[test]
    trades = stats.trades_from(run.result, run.rules, shortened)
    rec: dict[str, Any] = {
        "test": test, "test_id": test_id, "window": [d.isoformat() for d in schedule.window],
        "lead_in_dates": [d.isoformat() for d in run.lead_in],
        **stats.core_numbers(test_id, trades, days, run.rules),
        "schedule_exclusions": schedule.reason_counts(),
        "scheduled_entries": len(schedule.entries),
        "entry_outcomes": entry_outcomes(run.result, schedule),
        "exit_types": dict(sorted(Counter(t.exit_type for t in trades).items())),
        "engine_counters": dict(sorted(run.result.counters.items())),
        "mll": mll_record(run.result),
        "basis_points": basis_points(trades, run.rules),
        "stress_1p5x_slippage": stress(test_id, trades, days, run.rules),
        "price_check_failures": sum(not t.price_check_ok for t in trades),
        "trades": trade_rows(trades, run.rules),
    }
    if verdict:
        rec["per_year"] = per_year(test_id, trades, days, run.rules)
    return rec


def stopped_record(test: str, exc: BaseException, schedule: Schedule) -> dict[str, Any]:
    return {"test": test, "test_id": K.TEST_IDS[test], "status": K.STOPPED,
            "window": [d.isoformat() for d in schedule.window],
            "reason": f"{type(exc).__name__}: {exc}",
            "rule_quoted": "prereg section 5: 'A test whose run cannot complete for a reason this "
                           "text names is STOPPED, with the rule quoted.' Section 3: 'Through the "
                           "frozen engine, unchanged'",
            "schedule_exclusions": schedule.reason_counts(),
            "scheduled_entries": len(schedule.entries)}


__all__ = ["basis_points", "entry_outcomes", "mll_record", "per_year", "stopped_record",
           "stress", "trade_rows", "window_record"]
