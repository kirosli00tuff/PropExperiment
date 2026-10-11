"""H6's statistic and pass bar (prereg sections 4 and 5), from the engine's own fill records.

- Per trade i (a flat-to-flat run of fills, as screening.stage_e_runner.extract_trips groups
  them): gross_i = side_i x (exit fill price - entry fill price) in MNQ ticks, read as the trip's
  summed Fill.gross_realized_cents over MNQ's tick value (the engine's FIFO P&L; checked against
  the fill prices); c_i = the trip's summed commission_cents + slippage_cents in ticks (the D8
  round trip the engine charged); net_i = gross_i - c_i; dollars at $0.50 a tick, one MNQ.
- t_B and the one-sided p: ml_route_v2.gate0._b_test itself, on (trade_date, g_ticks = net_i,
  cost_ticks = c_i).
- Holm's step-down at family alpha 0.025 over the registered tests.
- The annualized net Sharpe: daily net dollars over every equity trade date of the window (zero
  on a date with no trade), mean / sd (ddof 1) x sqrt(252); NaN (which fails the bar) when there
  are fewer than 2 dates or the sd is 0.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from fractions import Fraction
from typing import Any

import numpy as np
import pandas as pd

from h6_rod import constants as K

EXIT_TYPES = {"strategy": "c2_exit", "price_limit_exit": "d97_price_limit_exit",
              "mll_liquidation": "mll_breach_flatten"}


@dataclass(frozen=True)
class Trade:
    trade_date: date
    side: str  # the entry side
    entry_ts_ns: int
    exit_ts_ns: int
    entry_price: float
    exit_price: float
    gross_cents: Fraction
    commission_cents: int
    slippage_cents: int
    slippage_ticks_by_fill: tuple[float, ...]  # per fill (entry first), per contract
    qty_by_fill: tuple[int, ...]
    exit_reason: str
    exit_type: str
    n_fills: int
    account_index: int
    event_window_by_fill: tuple[bool, ...]
    price_check_ok: bool  # gross == side x (exit - entry) in ticks (two-fill trips)

    @property
    def cost_cents(self) -> int:
        return self.commission_cents + self.slippage_cents

    @property
    def net_cents(self) -> Fraction:
        return self.gross_cents - self.cost_cents


def tick_value_cents(rules: Any) -> Fraction:
    return Fraction(rules.tick_value(K.VEHICLE))


def ticks(cents: Fraction | int, rules: Any) -> float:
    return float(Fraction(cents) / tick_value_cents(rules))


def exit_type(reason: str, shortened: bool) -> str:
    if reason == "forced_flatten":
        return "flatten_shortened_day" if shortened else "forced_flatten"
    return EXIT_TYPES.get(reason, reason)


def _price_ok(fills: Sequence[Any], gross: Fraction, rules: Any) -> bool:
    if len(fills) != 2:
        return True
    a, b = fills
    sign = 1 if a.side == "buy" else -1
    moved = sign * (rules.price_ticks(K.VEHICLE, b.price) - rules.price_ticks(K.VEHICLE, a.price))
    return Fraction(moved * a.qty) * tick_value_cents(rules) == gross


def trades_from(result: Any, rules: Any, shortened: Mapping[date, bool]) -> list[Trade]:
    """Flat-to-flat trips of the engine result's fills, in closing order."""
    from screening.stage_e_engine import Fill

    out: list[Trade] = []
    run: list[Any] = []
    for f in result.events(Fill):
        run.append(f)
        if f.position_after != 0:
            continue
        first, last = run[0], run[-1]
        gross = sum((Fraction(x.gross_realized_cents) for x in run), Fraction(0))
        day = first.trade_date
        out.append(Trade(
            trade_date=day, side=first.side, entry_ts_ns=first.fill_ts_ns,
            exit_ts_ns=last.fill_ts_ns, entry_price=first.price, exit_price=last.price,
            gross_cents=gross, commission_cents=sum(x.commission_cents for x in run),
            slippage_cents=sum(x.slippage_cents for x in run),
            slippage_ticks_by_fill=tuple(float(x.slippage_ticks) for x in run),
            qty_by_fill=tuple(int(x.qty) for x in run), exit_reason=last.reason,
            exit_type=exit_type(last.reason, bool(shortened.get(day, False))),
            n_fills=len(run), account_index=first.account_index,
            event_window_by_fill=tuple(bool(x.event_window) for x in run),
            price_check_ok=_price_ok(run, gross, rules)))
        run = []
    return out


def trade_frame(trades: Sequence[Trade], rules: Any) -> pd.DataFrame:
    """Per trade: trade_date (datetime64[D]), gross, c and net ticks (prereg section 4)."""
    rows = [{"trade_date": np.datetime64(t.trade_date, "D"),
             "gross_ticks": ticks(t.gross_cents, rules), "cost_ticks": ticks(t.cost_cents, rules),
             "net_ticks": ticks(t.net_cents, rules)} for t in trades]
    cols = ["trade_date", "gross_ticks", "cost_ticks", "net_ticks"]
    frame = pd.DataFrame(rows, columns=cols)
    frame["trade_date"] = frame["trade_date"].astype("datetime64[s]")
    return frame


def b_test(test_id: str, trades: Sequence[Trade], rules: Any) -> Any:
    """gate0._b_test on (trade_date, g_ticks = net_i, cost_ticks = c_i)."""
    from ml_route_v2.gate0 import _b_test

    tf = trade_frame(trades, rules)
    frame = pd.DataFrame({"trade_date": tf["trade_date"], "g_ticks": tf["net_ticks"],
                          "cost_ticks": tf["cost_ticks"]})
    return _b_test(test_id, K.VEHICLE, K.B_TEST_HORIZON, frame, len(frame))


def daily_net_usd(trades: Sequence[Trade], days: Sequence[date]) -> pd.Series:
    """Net dollars per equity trade date of ``days``, zero on a date with no trade. A trade dated
    outside ``days`` raises (one schedule, one window)."""
    series = pd.Series(0.0, index=pd.Index(list(days), name="trade_date"), dtype=float)
    for t in trades:
        if t.trade_date not in series.index:
            raise ValueError(f"trade dated {t.trade_date} is outside the window's trade dates")
        series[t.trade_date] += float(t.net_cents) / 100.0
    return series


def annualized_sharpe(daily: Sequence[float] | pd.Series) -> float:
    x = np.asarray(daily, dtype=np.float64)
    if x.size < 2:
        return float("nan")
    sd = float(x.std(ddof=1))
    if sd == 0:
        return float("nan")
    return float(x.mean()) / sd * math.sqrt(K.ANNUALIZATION_DAYS)


def holm(pvalues: Mapping[str, float], alpha: float = K.HOLM_ALPHA) -> dict[str, Any]:
    """Holm's step-down: sort ascending, reject p_(k) <= alpha / (m - k + 1) for k = 1, 2, ...
    until the first non-rejection. Returns {"rejected": {test: bool}, "steps": [...]}."""
    order = sorted(pvalues, key=lambda t: (pvalues[t], t))
    m = len(order)
    rejected = {t: False for t in order}
    steps = []
    stopped = False
    for k, test in enumerate(order, start=1):
        bound = alpha / (m - k + 1)
        p = pvalues[test]
        reject = (not stopped) and p <= bound
        steps.append({"k": k, "test": test, "p": p, "bound": bound, "rejected": reject})
        if reject:
            rejected[test] = True
        else:
            stopped = True
    return {"m": m, "alpha": alpha, "rejected": rejected, "steps": steps}


def _mean(values: Sequence[float]) -> float:
    return float(np.mean(values)) if len(values) else float("nan")


def pass_bar(test: str, *, holm_rejected: bool, mean_gross: float, mean_cost: float,
             n_trades: int, sharpe: float) -> dict[str, Any]:
    """Section 5: every item and the verdict (NaN fails every comparison)."""
    items = {
        "holm_rejected": bool(holm_rejected),
        "cost_bar": bool(mean_gross >= K.COST_MULTIPLE * mean_cost),
        "min_trades": bool(n_trades >= K.MIN_TRADES[test]),
        "sharpe_bar": bool(sharpe >= K.SHARPE_BAR),
    }
    return {"items": items, "min_trades_required": K.MIN_TRADES[test],
            "verdict": K.PASS if all(items.values()) else K.FAIL}


def core_numbers(test_id: str, trades: Sequence[Trade], days: Sequence[date], rules: Any
                 ) -> dict[str, Any]:
    """t_B, p, means, counts and the Sharpe of one test on one window."""
    tf = trade_frame(trades, rules)
    bt = b_test(test_id, trades, rules)
    daily = daily_net_usd(trades, days)
    return {
        "n_trades": int(len(trades)), "n_dates_with_trade": int(bt.n_dates),
        "t_b": float(bt.t), "p_one_sided": float(bt.p),
        "mean_gross_ticks": _mean(tf["gross_ticks"].tolist()),
        "mean_cost_ticks": _mean(tf["cost_ticks"].tolist()),
        "mean_net_ticks": _mean(tf["net_ticks"].tolist()),
        "b_test_mean_g_ticks": float(bt.mean), "b_test_cost_ticks": bt.cost_ticks,
        "net_usd_total": float(daily.sum()), "window_trade_dates": int(len(daily)),
        "annualized_net_sharpe": annualized_sharpe(daily),
    }


__all__ = ["EXIT_TYPES", "Trade", "annualized_sharpe", "b_test", "core_numbers",
           "daily_net_usd", "exit_type", "holm", "pass_bar", "trade_frame", "trades_from"]
