"""H1 -- Friction-aware opening-range breakout with a minimum-hold filter.

PRE-REGISTRATION (written before this strategy was ever run on any fold).

Mechanism: build the opening range from the first ``OPENING_RANGE_MINUTES``
minutes of RTH (bar opens at CT minute 510..524, i.e. 08:30-08:45 CT).
Once that window closes, on the FIRST bar whose close trades beyond the
range high/low by at least ``MIN_BREAK_TICKS`` ticks, enter one unit in the
breakout direction (long above the range high, short below the range low).
Hold for a fixed, pre-registered horizon, then exit unconditionally. At most
one entry per session (the range only breaks once per day for this
strategy's purposes -- re-entering on a second break is a different,
untested idea).

Rationale (Fett & McPhail 2017; Kirilenko et al. 2014/2017): stop orders
cluster at round reference levels and their forced execution creates a
short-lived liquidity vacuum (a "hot potato" immediacy-demand burst) once a
level is taken out. The hypothesis under test is that this burst is large
enough to matter net of MES's modelled friction only over a MULTI-BAR hold,
not a single bar. Two hold horizons are pre-registered as the ONLY
combinations tested in Stage D.1 (extending this grid later must be counted
in the multiple-comparisons accounting):
    HOLD_MINUTES = 5   -- the "bar+1"-style short hold. The MNQ falsification
                          study (Mesfin 2026, Table 4) found this did NOT
                          clear friction (T=-0.82). Expected here: FAIL.
    HOLD_MINUTES = 75  -- the horizon the same study found cleared friction
                          on the point estimate (T=0.88) for MNQ's lower cost
                          structure. Expected here: marginal at best, likely
                          still FAIL once MES's higher modelled $2.64/RT cost
                          (a lower bound; see module KNOWN LIMITATIONS in the
                          Stage D.1 task) is applied.
Both are formalized as the same strategy class parameterised by
``hold_minutes``; running both is not parameter tuning after a look at
results, it is the pre-registered comparison the hypothesis itself proposes.

Fixed (not gridded) parameters, chosen before any run:
    OPENING_RANGE_MINUTES = 15  (the lower end of the stated 15-30 minute
                                  range; "OR15" is the standard convention)
    MIN_BREAK_TICKS = 4          (1.00 pt buffer past the range edge, to
                                  filter noise-level penetrations; a single
                                  round-number choice, not searched)
    QUANTITY_MICROS = 1

SUPPORT CONDITION: measured on TRAIN folds only, from the closed
round-trip ledger, after the modelled $2.64/RT MES cost. Support requires
ALL of:
  (a) the ROBUST verdict from funnel.power_gate.screen(..., robust=True) is
      "pass" (not "marginal", not "fail") at the nearest available
      segments_per_day grid point to the measured trades/day T, using the
      MEASURED p and R from the ledger (never a hand-picked grid point);
  (b) the sign of the measured edge matches the mechanism: net long trades
      profit more often after upside breaks and net short trades profit
      more often after downside breaks (i.e. the edge is not an artifact of
      the cost/fill model applied asymmetrically);
  (c) a pass on fold 0 is re-run across all 8 train folds and the ROBUST
      verdict does not swing from pass to fail across most of them -- an
      unstable spread is itself a finding, not support.

REFUTE CONDITION: ANY of the following is sufficient to refute, at the
modelled cost, for a given ``hold_minutes`` setting:
  (a) the ROBUST verdict is "fail" or "marginal";
  (b) net P&L over the closed round trips is <= $0 after cost;
  (c) the MATCHED verdict passes but the ROBUST verdict does not (apparent
      edge explained by size/activity against a favorable null, not signal);
  (d) fewer than ~30 closed round trips over the train fold -- in that case
      the result is UNDERPOWERED, not a genuine refutation, and must be
      reported as such rather than folded into a pass/fail count.
The prior going in, stated explicitly by the sourced MNQ study and by the
family's own DATA REALITY limitations (no order-book data this session, so
the liquidity-vacuum mechanism is tested only via a bar-derived proxy), is
that HOLD_MINUTES=5 fails outright and HOLD_MINUTES=75 is marginal-to-fail
once MES's higher, still-lower-bound cost is applied.

DATA REALITY note: no resting-order or queue-position data is available this
session (see Stage D.1 task's KNOWN LIMITATIONS). This strategy tests a
bar-derived proxy for the stop-cascade mechanism (price closing beyond a
prior-window level), never the mechanism itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from funnel.null_generator import RTH_OPEN_MINUTE_CT
from rules.xfa_rules import CT, MES_TICK_SIZE, OrderIntent, Refusal
from strategy.interface import AccountView, Bar, market_intent

OPENING_RANGE_MINUTES = 15
MIN_BREAK_TICKS = 4
QUANTITY_MICROS = 1


def ct_minute_of_day(ts_utc: datetime) -> int:
    """Minute of the CT calendar day (0..1439) for a UTC-aware timestamp."""
    local = ts_utc.astimezone(CT)
    return local.hour * 60 + local.minute


@dataclass(frozen=True)
class H1FrictionAwareOpeningRangeBreakout:
    """Enter on the first OR15 close-through, hold ``hold_minutes``, exit flat."""

    hold_minutes: int
    name: str = "h1_friction_aware_opening_range_breakout"
    opening_range_minutes: int = OPENING_RANGE_MINUTES
    min_break_ticks: int = MIN_BREAK_TICKS
    quantity_micros: int = QUANTITY_MICROS
    # Mutable working state behind frozen fields (never reassigned, only mutated in
    # place), sized/reset from the instance's own parameters -- same pattern as the
    # c_short_horizon_reversal family.
    _current_trade_date: list[object] = field(default_factory=lambda: [None])
    _or_high: list[float | None] = field(default_factory=lambda: [None])
    _or_low: list[float | None] = field(default_factory=lambda: [None])
    _triggered: list[bool] = field(default_factory=lambda: [False])
    _bars_since_entry: list[int] = field(default_factory=lambda: [-1])

    def __post_init__(self) -> None:
        if self.hold_minutes < 1:
            raise ValueError(f"hold_minutes {self.hold_minutes!r} must be >= 1")
        if self.opening_range_minutes < 1:
            raise ValueError(
                f"opening_range_minutes {self.opening_range_minutes!r} must be >= 1"
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

    def _reset_on_new_session(self, bar: Bar) -> None:
        if self._current_trade_date[0] != bar.trade_date:
            self._current_trade_date[0] = bar.trade_date
            self._or_high[0] = None
            self._or_low[0] = None
            self._triggered[0] = False
            self._bars_since_entry[0] = -1

    def on_bar(self, bar: Bar, account: AccountView) -> tuple[OrderIntent | Refusal, ...]:
        self._reset_on_new_session(bar)

        # Exit path: a fixed hold, counted in bars since the strategy's own entry.
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

        if self._triggered[0] or self._or_high[0] is None:
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
