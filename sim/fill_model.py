"""Fill model: MES market orders (Stage C, Task 3) and resting limit orders (Stage D.1a, Task 2).

Passive/limit fills are documented, with what they do NOT model, at
``passive_fill_ticks`` below. The rest of this docstring is about market orders.

READ BEFORE QUOTING ANY NUMBER THIS PRODUCES. The slippage calibration behind
every fill (``sim/slippage_calibration.json``, built by
``sim/calibrate_slippage.py``) rests on TWO days of MES mbp-10 book data
(2026-07-15 and 2026-07-31). It measures the cost of walking the visible book
against the mid, and it EXCLUDES:
- latency: the book moves between decision and arrival;
- adverse selection: fills are likelier exactly when the price is about to move
  against you, which a strategy with any signal suffers systematically;
- queue position and hidden liquidity.
Both days fall inside what is now the sealed holdout period (cost-structure
information only, no price direction). This is the best model available, and
it is used. But a backtest cost built on it is a LOWER BOUND on real execution
cost, not a realistic estimate. Nothing downstream should present it as more.

Conventions (the engine's known-answer tests depend on these exactly):
- A market order decided at the close of bar N (decision time = bar N's open
  + 60 s) fills at the OPEN price of the first later bar, normally bar N+1.
  The bar open is a trade print, so it sits at the bid or the ask; as a proxy
  for the mid the calibration is measured against, it is unbiased but noisy.
- The fill price stays on the 0.25 tick grid: the rules engine marks positions
  only at on-grid prices. Slippage is booked as a separate cost in cents, not
  folded into the price.
- Slippage per side (cents) = ceil(qty * slip_ticks * 125), where slip_ticks =
  ``sim.costs.expected_slippage_ticks`` for the FILL time's 15-minute CT
  bucket and the smallest calibrated size >= qty. Rounding is up, never down.
- Commission per side = qty * 61 cents (half of the $1.22 round turn, which is
  exactly divisible). The commission figure still carries Stage A.1's blocking
  TODO to reconfirm it at Topstep checkout.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import UTC, datetime

from sim.costs import CT, MES_ROUND_TURN_COMMISSION_USD, SlippageTable, expected_slippage_ticks

MES_TICK_VALUE_CENTS = 125
_ROUND_TURN_CENTS = round(MES_ROUND_TURN_COMMISSION_USD * 100)
if _ROUND_TURN_CENTS % 2:
    raise ValueError("round-turn commission must split evenly into two sides")
COMMISSION_PER_SIDE_CENTS_PER_MICRO = _ROUND_TURN_CENTS // 2  # 61
_ANCHOR_CT_DATE = (2026, 1, 5)  # any weekday: only the CT wall-clock minute selects a bucket


@dataclass(frozen=True, slots=True)
class FillCost:
    """One side's execution cost for ``qty_micros``."""

    qty_micros: int
    commission_cents: int
    slippage_cents: int
    slippage_ticks_per_micro: float
    statistic: str

    @property
    def total_cents(self) -> int:
        return self.commission_cents + self.slippage_cents


def slippage_cents(qty_micros: int, slip_ticks: float) -> int:
    """ceil to the cent; the round() strips float noise such as 68.37500000000001."""
    return math.ceil(round(qty_micros * slip_ticks * MES_TICK_VALUE_CENTS, 6))


def side_cost(
    table: SlippageTable, fill_ts_utc: datetime, qty_micros: int, statistic: str = "mean"
) -> FillCost:
    """Commission + slippage for one side filled at ``fill_ts_utc``."""
    if isinstance(qty_micros, bool) or not isinstance(qty_micros, int) or qty_micros <= 0:
        raise ValueError(f"quantity {qty_micros!r} is not a positive integer")
    slip = expected_slippage_ticks(table, fill_ts_utc, qty_micros, statistic)
    return FillCost(
        qty_micros=qty_micros,
        commission_cents=qty_micros * COMMISSION_PER_SIDE_CENTS_PER_MICRO,
        slippage_cents=slippage_cents(qty_micros, slip),
        slippage_ticks_per_micro=slip,
        statistic=statistic,
    )


def side_cost_at_ct_minute(
    table: SlippageTable, minute_of_day_ct: int, qty_micros: int, statistic: str = "mean"
) -> FillCost:
    """Same as ``side_cost`` for a CT minute-of-day (the funnel has no real timestamps)."""
    if not 0 <= minute_of_day_ct < 24 * 60:
        raise ValueError(f"minute {minute_of_day_ct} is not a minute of the day")
    hour, minute = divmod(minute_of_day_ct, 60)
    local = datetime(*_ANCHOR_CT_DATE, hour, minute, tzinfo=CT)
    return side_cost(table, local.astimezone(UTC), qty_micros, statistic)


# ------------------------------------------------------------ passive fills ----
# Stage D.1a, Task 2. A resting limit order, priced from 1-minute OHLC bars.
#
# WHAT THIS MODELS. Whether and when a resting limit order at a given price would
# have filled, given the historical bar sequence:
# - The order rests from the bar AFTER its decision bar (the point-in-time rule
#   market orders follow); a price the strategy has already seen can never fill it.
# - TRADE-THROUGH, not touch. A buy limit at L fills only on a bar whose low is at
#   least one tick BELOW L (a sell: high at least one tick above L). Under price-time
#   priority the market cannot trade below L until every bid resting at L has been
#   filled, so a trade-through makes the fill close to certain wherever the order
#   sat in the queue. A bar that only TOUCHES L is treated as NO fill.
# - The fill price is exactly L: never better (no price improvement), never worse.
#   No spread is paid, so slippage is 0; commission is the market-order 61 cents per
#   micro per side.
#
# ADVERSE-SELECTION DECISION: no extra per-fill price penalty is applied, for two reasons:
# 1. The trade-through rule already IS the adverse-selection model. The fills it keeps
#    are exactly the ones where price went through the level against the position.
#    The fills it drops, touch-and-bounce, are disproportionately the ones that would
#    have won.
# 2. What happens after the fill comes from the real subsequent bars, so price
#    continuing against the order is already in the P&L. A flat penalty on top would
#    count it twice.
# The net bias of the rule on fill count and P&L is PESSIMISTIC, which is the side a
# screen should err on.
#
# WHAT THIS DOES NOT MODEL, to be carried as caveats on any result that used it:
# - QUEUE POSITION. The data are OHLCV bars plus two book days, so where a resting
#   order sat in the level's queue is unknowable. Trade-through sidesteps the question
#   by giving up every touch-only fill, which rests on an ASSUMPTION: that a level is
#   exhausted before price trades through it. Implied, hidden or cancelled liquidity can
#   break that assumption.
# - MARKET IMPACT OF THE ORDER'S PRESENCE. A resting order changes the book it sits in.
#   The model replays the historical path as if the order had never been there.
# - SIZE AGAINST VOLUME AT THE LEVEL. A 1-minute bar says nothing about how much traded
#   at L, so a multi-micro order is filled in full on any trade-through.
# - LATENCY. The order is assumed to rest from the instant of its decision.
# - WITHIN-BAR SEQUENCING against the order's own later exit: the engine books a passive
#   fill before the bar's MLL mark, and marks the new position at the bar's adverse
#   extreme, which is the conservative reading.
PASSIVE_THROUGH_TICKS = 1
PASSIVE_FILL_CAVEATS = (
    "passive fills use a trade-through rule on 1-minute OHLC bars: a limit fills only when "
    "price trades at least one tick through it, at exactly the limit price",
    "queue position is NOT modelled; touch-only fills are dropped instead, which assumes a "
    "level is exhausted before price trades through it",
    "the order's own effect on the market's subsequent path is NOT modelled",
    "volume available at the limit price is NOT checked: any trade-through fills the full size",
    "no extra adverse-selection penalty is applied: the trade-through rule plus the real "
    "post-fill path carry it; dropped touch-only fills bias results pessimistically",
)


def passive_fill_ticks(
    signed_qty: int, limit_ticks: int, bar_low_ticks: int, bar_high_ticks: int
) -> int | None:
    """The fill price (ticks) of a resting limit on one bar, or None if it does not fill."""
    if signed_qty == 0:
        raise ValueError("a passive order must have a non-zero quantity")
    if signed_qty > 0:
        return limit_ticks if bar_low_ticks <= limit_ticks - PASSIVE_THROUGH_TICKS else None
    return limit_ticks if bar_high_ticks >= limit_ticks + PASSIVE_THROUGH_TICKS else None


def passive_side_cost(qty_micros: int) -> FillCost:
    """Commission only: a resting limit fills at its own price, so no spread is crossed."""
    if isinstance(qty_micros, bool) or not isinstance(qty_micros, int) or qty_micros <= 0:
        raise ValueError(f"quantity {qty_micros!r} is not a positive integer")
    return FillCost(
        qty_micros=qty_micros,
        commission_cents=qty_micros * COMMISSION_PER_SIDE_CENTS_PER_MICRO,
        slippage_cents=0,
        slippage_ticks_per_micro=0.0,
        statistic="passive",
    )
