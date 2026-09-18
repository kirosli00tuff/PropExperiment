"""H4 -- Narrow-range (contraction) conditioned opening-range breakout.

PRE-REGISTRATION (written before this strategy was ever run on any fold).

Mechanism: build the opening range exactly as in H1 (first
``OPENING_RANGE_MINUTES`` minutes of RTH). At the moment the window closes,
compute today's OR width (``or_high - or_low``) and compare it, via a
percentile rank, against a trailing baseline of the last ``LOOKBACK_DAYS``
sessions' own OR widths (today's width is never included in its own
baseline). Only take the breakout signal -- otherwise identical to H1's
trigger and exit -- if today's OR width sits at or below the
``CONTRACTION_PERCENTILE`` of that trailing baseline (an unusually narrow
range). A day whose OR width is not narrow is skipped entirely: no trade,
win or loss, is recorded for it under this hypothesis.

Rationale (Crabel 1990's Contraction-Expansion principle, via Holmberg,
Lonnbark & Lundstrom; Carver 2016 for a continuous range-position framing
that this discretizes into a percentile filter): a break out of an
abnormally tight range is hypothesized to more often reflect a genuine
liquidity vacuum (few resting orders were needed to compress the range,
so a level break has less standing size to absorb it) than a break out of
an already-wide range, where a similar-looking break may just be
continued chop. This session has NO order-book data (two mbp-10 days used
to calibrate the cost model both fall inside the sealed holdout -- see
Stage D.1 task's KNOWN LIMITATIONS), so range width is a bar-derived PROXY
for contraction, not a measurement of it; this hypothesis tests the proxy's
value, not the order-flow mechanism itself.

Fixed (not gridded) parameters, chosen before any run:
    OPENING_RANGE_MINUTES = 15  (same convention as H1, for comparability)
    LOOKBACK_DAYS = 20          (one trading month of trailing sessions)
    CONTRACTION_PERCENTILE = 0.40  (below the 40th percentile counts as
                                     "narrow"; a single round-number choice)
    MIN_BREAK_TICKS = 4         (1.00 pt buffer past the range edge)
    HOLD_MINUTES = 30           (fixed exit; one setting, not searched)
    QUANTITY_MICROS = 1
A minimum of ``LOOKBACK_DAYS`` prior sessions with a built OR is required
before the filter can fire; days before that warm-up trade nothing.

SUPPORT CONDITION: measured on TRAIN folds only, from the closed
round-trip ledger, after the modelled $2.64/RT MES cost. Support requires
ALL of:
  (a) the ROBUST verdict from funnel.power_gate.screen(..., robust=True) is
      "pass" at the nearest segments_per_day grid point to the MEASURED
      trades/day T, using the measured p and R;
  (b) the contraction-filtered result is compared, on the SAME train fold,
      to H1's unfiltered OR15/hold-30-equivalent result (H1 itself is run
      at hold_minutes=5 and 75, not 30 -- so this is a qualitative
      direction check, not a like-for-like number): the filter should not
      simply be trading a rarer subset of the same losing population --
      the filtered p/R must be reported alongside H1's for that contrast;
  (c) a fold-0 pass is re-run across all 8 train folds and the ROBUST
      verdict does not swing from pass to fail across most of them.

REFUTE CONDITION: ANY of the following is sufficient to refute, at the
modelled cost:
  (a) the ROBUST verdict is "fail" or "marginal";
  (b) net P&L over the closed round trips is <= $0 after cost;
  (c) the MATCHED verdict passes but the ROBUST verdict does not;
  (d) fewer than ~30 closed round trips over the train fold (UNDERPOWERED,
      not a genuine refutation -- report as such; the contraction filter
      itself deliberately reduces trade count, so this is a real risk);
  (e) the filter fires on so few days that the measured p/R is not
      meaningfully different from H1's unfiltered figures within noise --
      i.e. the bar-derived contraction proxy adds nothing measurable.
The prior going in: this is explicitly framed as testing a bar-derived
proxy for a mechanism this session cannot observe directly, so a clean
pass is not expected; the more likely outcomes are FAIL or UNDERPOWERED.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime

from funnel.null_generator import RTH_OPEN_MINUTE_CT
from rules.xfa_rules import CT, MES_TICK_SIZE, OrderIntent, Refusal
from strategy.interface import AccountView, Bar, market_intent

OPENING_RANGE_MINUTES = 15
LOOKBACK_DAYS = 20
CONTRACTION_PERCENTILE = 0.40
MIN_BREAK_TICKS = 4
HOLD_MINUTES = 30
QUANTITY_MICROS = 1


def ct_minute_of_day(ts_utc: datetime) -> int:
    """Minute of the CT calendar day (0..1439) for a UTC-aware timestamp."""
    local = ts_utc.astimezone(CT)
    return local.hour * 60 + local.minute


def _percentile_rank(window: deque[float], value: float) -> float:
    """Fraction of ``window`` strictly below ``value`` (ties count half)."""
    if not window:
        return 1.0  # no baseline yet: nothing counts as "narrow"
    below = sum(1 for x in window if x < value)
    equal = sum(1 for x in window if x == value)
    return (below + 0.5 * equal) / len(window)


@dataclass(frozen=True)
class H4NarrowRangeContractionBreakout:
    """OR15 breakout gated on today's range being narrow vs. a trailing baseline."""

    name: str = "h4_narrow_range_contraction_breakout"
    opening_range_minutes: int = OPENING_RANGE_MINUTES
    lookback_days: int = LOOKBACK_DAYS
    contraction_percentile: float = CONTRACTION_PERCENTILE
    min_break_ticks: int = MIN_BREAK_TICKS
    hold_minutes: int = HOLD_MINUTES
    quantity_micros: int = QUANTITY_MICROS
    # Mutable working state behind frozen fields (never reassigned, only mutated in place).
    _current_trade_date: list[object] = field(default_factory=lambda: [None])
    _or_high: list[float | None] = field(default_factory=lambda: [None])
    _or_low: list[float | None] = field(default_factory=lambda: [None])
    _or_finalized: list[bool] = field(default_factory=lambda: [False])
    _eligible_today: list[bool] = field(default_factory=lambda: [False])
    _triggered: list[bool] = field(default_factory=lambda: [False])
    _bars_since_entry: list[int] = field(default_factory=lambda: [-1])
    _width_baseline: deque[float] = field(default_factory=deque)

    def __post_init__(self) -> None:
        if self.opening_range_minutes < 1:
            raise ValueError(
                f"opening_range_minutes {self.opening_range_minutes!r} must be >= 1"
            )
        if self.lookback_days < 1:
            raise ValueError(f"lookback_days {self.lookback_days!r} must be >= 1")
        if not (0.0 < self.contraction_percentile <= 1.0):
            raise ValueError(
                f"contraction_percentile {self.contraction_percentile!r} must be in (0, 1]"
            )
        if self.min_break_ticks < 0:
            raise ValueError(f"min_break_ticks {self.min_break_ticks!r} must be >= 0")
        if self.hold_minutes < 1:
            raise ValueError(f"hold_minutes {self.hold_minutes!r} must be >= 1")
        bad_quantity = (
            isinstance(self.quantity_micros, bool)
            or not isinstance(self.quantity_micros, int)
            or self.quantity_micros <= 0
        )
        if bad_quantity:
            raise ValueError(f"quantity_micros {self.quantity_micros!r} must be a positive int")
        object.__setattr__(self, "_width_baseline", deque(maxlen=self.lookback_days))

    def _reset_on_new_session(self, bar: Bar) -> None:
        if self._current_trade_date[0] != bar.trade_date:
            self._current_trade_date[0] = bar.trade_date
            self._or_high[0] = None
            self._or_low[0] = None
            self._or_finalized[0] = False
            self._eligible_today[0] = False
            self._triggered[0] = False
            self._bars_since_entry[0] = -1

    def on_bar(self, bar: Bar, account: AccountView) -> tuple[OrderIntent | Refusal, ...]:
        self._reset_on_new_session(bar)

        if account.position_micros != 0 and self._bars_since_entry[0] >= 0:
            self._bars_since_entry[0] += 1
            if self._bars_since_entry[0] >= self.hold_minutes:
                side = "sell" if account.position_micros > 0 else "buy"
                self._bars_since_entry[0] = -1
                return (market_intent(bar, side, abs(account.position_micros)),)
            return ()

        minute = ct_minute_of_day(bar.open_ts_utc)
        in_or_window = (
            RTH_OPEN_MINUTE_CT <= minute < RTH_OPEN_MINUTE_CT + self.opening_range_minutes
        )
        if in_or_window:
            self._or_high[0] = bar.high if self._or_high[0] is None else max(
                self._or_high[0], bar.high
            )
            self._or_low[0] = bar.low if self._or_low[0] is None else min(
                self._or_low[0], bar.low
            )
            return ()

        if self._or_high[0] is None:
            return ()

        # First bar after the OR window closes: decide eligibility against the
        # PRE-EXISTING baseline (today's own width is never in its own baseline),
        # then append today's width for future days.
        if not self._or_finalized[0]:
            self._or_finalized[0] = True
            width = self._or_high[0] - self._or_low[0]
            warm = len(self._width_baseline) >= self.lookback_days
            percentile = _percentile_rank(self._width_baseline, width)
            self._eligible_today[0] = warm and percentile <= self.contraction_percentile
            self._width_baseline.append(width)

        if self._triggered[0] or not self._eligible_today[0]:
            return ()
        if account.position_micros != 0 or account.pending_signed_micros != 0:
            return ()

        threshold = self.min_break_ticks * MES_TICK_SIZE
        if bar.close >= self._or_high[0] + threshold:
            self._triggered[0] = True
            self._bars_since_entry[0] = 0
            return (market_intent(bar, "buy", self.quantity_micros),)
        if bar.close <= self._or_low[0] - threshold:
            self._triggered[0] = True
            self._bars_since_entry[0] = 0
            return (market_intent(bar, "sell", self.quantity_micros),)
        return ()
