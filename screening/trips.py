"""Round-trip measurement for screening: p / R / T from a backtest ledger.

Written for family D in Stage D.1 (``strategy/research/d_volatility_state/_metrics.py``,
now a re-export of this module) and promoted here in Stage D.1a so every screen
measures trades the same way. Tooling, not a hypothesis.
It turns a ``sim.engine.BacktestResult`` ledger into the three figures
``funnel.power_gate.screen`` needs (win probability p, win/loss ratio R, trades
per day T), plus the per-trade dollar series those figures are computed from.

Round-trip definition. A "closed round-trip trade" is the maximal run of
``FillEvent`` rows for one account between two flat states (``position_after
== 0``), in ledger order. Its net P&L is the sum, over every fill in that run,
of ``gross_realized_cents - commission_cents - slippage_cents``. This is exact
under FIFO ``apply_fill``: an opening fill has ``gross_realized_cents == 0``
(nothing closes) but still pays commission/slippage; a closing fill carries the
realized P&L on the lots it closes. Summing both terms over the run attributes
the full round-trip cost (both sides) and the full realized gain/loss to one
number, in dollars. The engine always flattens any position still open at the
end of a replay (``_Run.finish``), so no trip is left dangling.

Win probability p = fraction of trips with net P&L > 0 (ties are not wins).
Win/loss ratio R = mean(winning trip P&L) / mean(abs(losing trip P&L)); ties
(net P&L == 0) are excluded from both the win set and the loss set. Trades per
day T = trip count / number of distinct trade dates the strategy was run over
(the fold's train-date count, or the sub-frame's date count for a shorter run),
not the count of days that actually traded.
"""

from __future__ import annotations

from dataclasses import dataclass

from sim.engine import BacktestResult, FillEvent


@dataclass(frozen=True)
class TradeMeasurement:
    """Everything a screening report needs for one strategy/fold run."""

    n_trips: int
    n_trade_dates: int
    win_probability: float | None
    win_loss_ratio: float | None
    trades_per_day: float
    net_pnl_usd: float
    trip_pnls_usd: tuple[float, ...]


def round_trip_pnls_usd(result: BacktestResult) -> tuple[float, ...]:
    """Net dollar P&L of every closed round-trip trade, in ledger (time) order."""
    fills = result.events(FillEvent)
    trips: list[float] = []
    running_cents = 0
    in_trip = False
    for fill in fills:
        running_cents += fill.gross_realized_cents - fill.commission_cents - fill.slippage_cents
        in_trip = True
        if fill.position_after == 0:
            trips.append(running_cents / 100.0)
            running_cents = 0
            in_trip = False
    if in_trip:
        # Should not happen: the engine flattens everything before finish() returns.
        raise AssertionError("round_trip_pnls_usd: a trip never closed -- engine invariant broken")
    return tuple(trips)


def measure(result: BacktestResult, n_trade_dates: int) -> TradeMeasurement:
    """The p / R / T figures for ``screen()``, computed from the ledger, not guessed."""
    if n_trade_dates <= 0:
        raise ValueError(f"n_trade_dates {n_trade_dates!r} must be positive")
    trips = round_trip_pnls_usd(result)
    n = len(trips)
    wins = [x for x in trips if x > 0.0]
    losses = [x for x in trips if x < 0.0]
    win_probability = (len(wins) / n) if n else None
    if wins and losses:
        mean_win = sum(wins) / len(wins)
        mean_loss = abs(sum(losses) / len(losses))
        win_loss_ratio = (mean_win / mean_loss) if mean_loss > 0 else None
    else:
        win_loss_ratio = None
    return TradeMeasurement(
        n_trips=n,
        n_trade_dates=n_trade_dates,
        win_probability=win_probability,
        win_loss_ratio=win_loss_ratio,
        trades_per_day=n / n_trade_dates,
        net_pnl_usd=sum(trips),
        trip_pnls_usd=trips,
    )


def nearest_segments_per_day(trades_per_day: float, grid: tuple[int, ...] = (1, 2, 4)) -> int:
    """``screen()`` only accepts T in {1,2,4}; snap to the nearest and let the caller flag it."""
    return min(grid, key=lambda g: abs(g - trades_per_day))
