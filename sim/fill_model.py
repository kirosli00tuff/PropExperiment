"""Fill model: MES market orders, priced with the Stage A.1 cost model (Stage C, Task 3).

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
