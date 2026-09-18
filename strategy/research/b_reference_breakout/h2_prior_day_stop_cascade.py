"""H2 -- Prior-day-high/low stop-cascade capture with a short, decaying hold.

PRE-REGISTRATION (written before this strategy was ever run on any fold).

Mechanism: track the running high/low of each COMPLETED session (all bars
stamped with that trade date, overnight plus RTH -- "the prior completed
session", not just its RTH slice). On the first RTH bar of the NEXT session
whose close trades through that prior session's high or low by at least
``MIN_BREAK_TICKS`` ticks, enter one unit in the breakout direction. Exit at
the first of:
  (a) ``MAX_HOLD_MINUTES`` bars since entry (a short, fixed cap -- this
      strategy targets the burst itself, not a sustained trend), or
  (b) a volume-decay signal: ``DECAY_LOOKBACK`` consecutive bars whose
      volume is below ``DECAY_VOLUME_RATIO`` of the entry bar's volume,
      read as the post-trigger liquidity burst fading.
At most one entry per session.

Rationale (Fett & McPhail 2017 CFTC OCE Staff Paper 2017-009): ES stop
orders cluster and their forced execution is a burst of liquidity
concentrated at the trigger moment (0.9% of ES volume, ~22.8M contracts
2014-2016), not a persistent edge -- hence the short cap and the explicit
decay exit, rather than a trend-following hold. Kirilenko et al.'s
"hot-potato" effect (rapid inventory passing among high-frequency traders
after a shock) is the archetype for why the burst should fade quickly.

Fixed (not gridded) parameters, chosen before any run:
    MAX_HOLD_MINUTES = 15     (short cap; matches the "burst, not a trend"
                               framing -- no other horizon is tested)
    DECAY_LOOKBACK = 2        (two consecutive thin bars)
    DECAY_VOLUME_RATIO = 0.5  (volume below half the entry bar's volume)
    MIN_BREAK_TICKS = 4       (1.00 pt buffer past the level)
    QUANTITY_MICROS = 1
Entries are restricted to RTH (08:30-16:00 CT bar opens) for tradability;
the reference level itself (prior session high/low) still includes the
overnight portion of the prior session, per the mechanism above.

SUPPORT CONDITION: measured on TRAIN folds only, from the closed
round-trip ledger, after the modelled $2.64/RT MES cost. Support requires
ALL of:
  (a) the ROBUST verdict from funnel.power_gate.screen(..., robust=True) is
      "pass" at the nearest segments_per_day grid point to the MEASURED
      trades/day T, using the measured p and R (never a hand-picked point);
  (b) the sign of the measured edge matches the mechanism (net long after
      upside breaks, net short after downside breaks);
  (c) a fold-0 pass is re-run across all 8 train folds and the ROBUST
      verdict does not swing from pass to fail across most of them.

REFUTE CONDITION: ANY of the following is sufficient to refute, at the
modelled cost:
  (a) the ROBUST verdict is "fail" or "marginal";
  (b) net P&L over the closed round trips is <= $0 after cost;
  (c) the MATCHED verdict passes but the ROBUST verdict does not;
  (d) fewer than ~30 closed round trips over the train fold (UNDERPOWERED,
      not a genuine refutation -- report as such).
The prior going in: the CFTC evidence quantifies stop-order clustering as
real, but this strategy can only observe its bar-derived aftermath (price
and volume), never the resting orders themselves (no order-book data this
session -- see Stage D.1 task's KNOWN LIMITATIONS), so a clean pass is not
expected; a fade of the burst before it clears cost is the modal outcome
under this prior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from funnel.null_generator import DAILY_HALT_MINUTE_CT, RTH_OPEN_MINUTE_CT
from rules.xfa_rules import CT, MES_TICK_SIZE, OrderIntent, Refusal
from strategy.interface import AccountView, Bar, market_intent

MAX_HOLD_MINUTES = 15
DECAY_LOOKBACK = 2
DECAY_VOLUME_RATIO = 0.5
MIN_BREAK_TICKS = 4
QUANTITY_MICROS = 1


def ct_minute_of_day(ts_utc: datetime) -> int:
    """Minute of the CT calendar day (0..1439) for a UTC-aware timestamp."""
    local = ts_utc.astimezone(CT)
    return local.hour * 60 + local.minute


@dataclass(frozen=True)
class H2PriorDayStopCascade:
    """Break the prior session's high/low in RTH; hold short, exit on cap or decay."""

    name: str = "h2_prior_day_stop_cascade"
    max_hold_minutes: int = MAX_HOLD_MINUTES
    decay_lookback: int = DECAY_LOOKBACK
    decay_volume_ratio: float = DECAY_VOLUME_RATIO
    min_break_ticks: int = MIN_BREAK_TICKS
    quantity_micros: int = QUANTITY_MICROS
    # Mutable working state behind frozen fields (never reassigned, only mutated in place).
    _current_trade_date: list[object] = field(default_factory=lambda: [None])
    _prior_day_high: list[float | None] = field(default_factory=lambda: [None])
    _prior_day_low: list[float | None] = field(default_factory=lambda: [None])
    _day_high: list[float | None] = field(default_factory=lambda: [None])
    _day_low: list[float | None] = field(default_factory=lambda: [None])
    _triggered: list[bool] = field(default_factory=lambda: [False])
    _bars_since_entry: list[int] = field(default_factory=lambda: [-1])
    _entry_volume: list[int] = field(default_factory=lambda: [0])
    _decay_streak: list[int] = field(default_factory=lambda: [0])

    def __post_init__(self) -> None:
        if self.max_hold_minutes < 1:
            raise ValueError(f"max_hold_minutes {self.max_hold_minutes!r} must be >= 1")
        if self.decay_lookback < 1:
            raise ValueError(f"decay_lookback {self.decay_lookback!r} must be >= 1")
        if not (0.0 < self.decay_volume_ratio < 1.0):
            raise ValueError(
                f"decay_volume_ratio {self.decay_volume_ratio!r} must be in (0, 1)"
            )
        if self.min_break_ticks < 0:
            raise ValueError(f"min_break_ticks {self.min_break_ticks!r} must be >= 0")
        bad_quantity = (
            isinstance(self.quantity_micros, bool)
            or not isinstance(self.quantity_micros, int)
            or self.quantity_micros <= 0
        )
        if bad_quantity:
            raise ValueError(f"quantity_micros {self.quantity_micros!r} must be a positive int")

    def _roll_session(self, bar: Bar) -> None:
        """On a new trade date, snapshot the just-completed session's high/low as the
        reference for today, then start a fresh running high/low for today."""
        if self._current_trade_date[0] != bar.trade_date:
            if self._day_high[0] is not None:
                self._prior_day_high[0] = self._day_high[0]
                self._prior_day_low[0] = self._day_low[0]
            self._current_trade_date[0] = bar.trade_date
            self._day_high[0] = None
            self._day_low[0] = None
            self._triggered[0] = False
            self._bars_since_entry[0] = -1
            self._decay_streak[0] = 0

    def on_bar(self, bar: Bar, account: AccountView) -> tuple[OrderIntent | Refusal, ...]:
        self._roll_session(bar)
        self._day_high[0] = bar.high if self._day_high[0] is None else max(
            self._day_high[0], bar.high
        )
        self._day_low[0] = bar.low if self._day_low[0] is None else min(
            self._day_low[0], bar.low
        )

        # Exit path: hold cap or volume-decay signal, whichever comes first.
        if account.position_micros != 0 and self._bars_since_entry[0] >= 0:
            self._bars_since_entry[0] += 1
            if bar.volume < self.decay_volume_ratio * self._entry_volume[0]:
                self._decay_streak[0] += 1
            else:
                self._decay_streak[0] = 0
            hit_cap = self._bars_since_entry[0] >= self.max_hold_minutes
            hit_decay = self._decay_streak[0] >= self.decay_lookback
            if hit_cap or hit_decay:
                side = "sell" if account.position_micros > 0 else "buy"
                self._bars_since_entry[0] = -1
                self._decay_streak[0] = 0
                return (market_intent(bar, side, abs(account.position_micros)),)
            return ()

        if self._triggered[0] or self._prior_day_high[0] is None:
            return ()
        if account.position_micros != 0 or account.pending_signed_micros != 0:
            return ()
        minute = ct_minute_of_day(bar.open_ts_utc)
        if not (RTH_OPEN_MINUTE_CT <= minute < DAILY_HALT_MINUTE_CT):
            return ()

        threshold = self.min_break_ticks * MES_TICK_SIZE
        if bar.close >= self._prior_day_high[0] + threshold:
            self._triggered[0] = True
            self._bars_since_entry[0] = 0
            self._entry_volume[0] = max(bar.volume, 1)
            return (market_intent(bar, "buy", self.quantity_micros),)
        if bar.close <= self._prior_day_low[0] - threshold:
            self._triggered[0] = True
            self._bars_since_entry[0] = 0
            self._entry_volume[0] = max(bar.volume, 1)
            return (market_intent(bar, "sell", self.quantity_micros),)
        return ()
