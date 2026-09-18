"""H3 -- Breakout-vs-fade horse race at the same opening-range level.

PRE-REGISTRATION (written before this strategy was ever run on any fold).

Mechanism: build the opening range from the first ``OPENING_RANGE_MINUTES``
minutes of RTH (the upper end of the family's stated 15-30 minute range,
deliberately different from H1's OR15 so this hypothesis is not just H1
re-run -- both are pre-registered once, not searched). Once the window
closes, on the FIRST bar whose close trades beyond the range high/low by at
least ``MIN_BREAK_TICKS`` ticks, run TWO mutually exclusive legs against the
SAME trigger and the SAME train folds:
  - ``H3BreakoutLeg``: enter in the breakout direction (continuation).
  - ``H3FadeLeg``: enter AGAINST the breakout direction (reversal back into
    the range) at the same bar and price.
Both hold a fixed ``hold_minutes`` and exit unconditionally. At most one
entry per session, per leg.

Rationale: this is the family's explicitly named "breakout-vs-fade
comparison at the same level" (Holmberg, Lonnbark & Lundstrom, citing
Crabel 1990's Contraction-Expansion framing; Mesfin 2026 Section 4.1's ORB
Pullback Entry, 80.7% stop-out rate, N=83, T=-1.27). The MNQ falsification
study's own pullback-entry result found the FADE to be a clear loser too --
so the honest pre-registered expectation is that both directions likely
fail net of MES's modelled cost, not that "the breakout fails, so the fade
must win". Running both legs on identical entries/exits isolates direction
as the only difference, so any gap between them is not confounded by
different triggers, holds or sizing.

Fixed (not gridded) parameters, chosen before any run:
    OPENING_RANGE_MINUTES = 30  (upper end of the stated 15-30 min range)
    HOLD_MINUTES = 30           (symmetric with the OR window; one setting,
                                  not searched)
    MIN_BREAK_TICKS = 4         (1.00 pt buffer past the range edge)
    QUANTITY_MICROS = 1
Two backtests (one per leg) are run per fold; this is the hypothesis's own
structure (a horse race needs both sides), not parameter tuning.

SUPPORT CONDITION (evaluated separately per leg, then compared): a leg is
"supported" under the same rule as H1/H2 -- the ROBUST verdict from
funnel.power_gate.screen(..., robust=True) is "pass" at the measured p/R/T,
the sign of the edge matches that leg's stated direction, and a fold-0 pass
holds up (does not swing to fail) across most of the 8 train folds. The
HORSE-RACE claim specifically is supported only if exactly one leg clears
this bar while the other does not, AND the winning leg's net P&L materially
exceeds the losing leg's (not a coin-flip-sized gap).

REFUTE CONDITION: the horse-race claim is refuted if EITHER (a) neither leg
clears the ROBUST verdict (both fail -- the modal, pre-registered
expectation per the MNQ study), or (b) both legs clear it (the trigger adds
edge regardless of direction, which is a different and unstated mechanism,
not evidence for "breakout vs fade"). As with H1/H2, fewer than ~30 closed
round trips for a leg makes its result UNDERPOWERED rather than a genuine
refutation, and must be reported as such.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from funnel.null_generator import RTH_OPEN_MINUTE_CT
from rules.xfa_rules import CT, MES_TICK_SIZE, OrderIntent, Refusal
from strategy.interface import AccountView, Bar, market_intent

OPENING_RANGE_MINUTES = 30
HOLD_MINUTES = 30
MIN_BREAK_TICKS = 4
QUANTITY_MICROS = 1


def ct_minute_of_day(ts_utc: datetime) -> int:
    """Minute of the CT calendar day (0..1439) for a UTC-aware timestamp."""
    local = ts_utc.astimezone(CT)
    return local.hour * 60 + local.minute


def _validate_common(
    hold_minutes: int, opening_range_minutes: int, min_break_ticks: int, quantity_micros: int
) -> None:
    if hold_minutes < 1:
        raise ValueError(f"hold_minutes {hold_minutes!r} must be >= 1")
    if opening_range_minutes < 1:
        raise ValueError(f"opening_range_minutes {opening_range_minutes!r} must be >= 1")
    if min_break_ticks < 0:
        raise ValueError(f"min_break_ticks {min_break_ticks!r} must be >= 0")
    bad_quantity = (
        isinstance(quantity_micros, bool)
        or not isinstance(quantity_micros, int)
        or quantity_micros <= 0
    )
    if bad_quantity:
        raise ValueError(f"quantity_micros {quantity_micros!r} must be a positive int")


@dataclass(frozen=True)
class H3BreakoutLeg:
    """Continuation leg of the horse race: trade WITH the OR30 breakout direction."""

    name: str = "h3_breakout_leg"
    opening_range_minutes: int = OPENING_RANGE_MINUTES
    hold_minutes: int = HOLD_MINUTES
    min_break_ticks: int = MIN_BREAK_TICKS
    quantity_micros: int = QUANTITY_MICROS
    _current_trade_date: list[object] = field(default_factory=lambda: [None])
    _or_high: list[float | None] = field(default_factory=lambda: [None])
    _or_low: list[float | None] = field(default_factory=lambda: [None])
    _triggered: list[bool] = field(default_factory=lambda: [False])
    _bars_since_entry: list[int] = field(default_factory=lambda: [-1])

    def __post_init__(self) -> None:
        _validate_common(
            self.hold_minutes, self.opening_range_minutes, self.min_break_ticks,
            self.quantity_micros,
        )

    def _reset_on_new_session(self, bar: Bar) -> None:
        if self._current_trade_date[0] != bar.trade_date:
            self._current_trade_date[0] = bar.trade_date
            self._or_high[0] = None
            self._or_low[0] = None
            self._triggered[0] = False
            self._bars_since_entry[0] = -1

    def _entry_side(self, breakout_direction: str) -> str:
        return breakout_direction

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

        if self._triggered[0] or self._or_high[0] is None:
            return ()
        if account.position_micros != 0 or account.pending_signed_micros != 0:
            return ()

        threshold = self.min_break_ticks * MES_TICK_SIZE
        if bar.close >= self._or_high[0] + threshold:
            self._triggered[0] = True
            self._bars_since_entry[0] = 0
            return (market_intent(bar, self._entry_side("buy"), self.quantity_micros),)
        if bar.close <= self._or_low[0] - threshold:
            self._triggered[0] = True
            self._bars_since_entry[0] = 0
            return (market_intent(bar, self._entry_side("sell"), self.quantity_micros),)
        return ()


@dataclass(frozen=True)
class H3FadeLeg(H3BreakoutLeg):
    """Reversal leg of the horse race: trade AGAINST the OR30 breakout direction.

    Identical trigger, hold and sizing to ``H3BreakoutLeg``; only the entry side
    is flipped, via ``_entry_side``, so a gap between the two legs' results is
    attributable to direction alone.
    """

    name: str = "h3_fade_leg"

    def _entry_side(self, breakout_direction: str) -> str:
        return "sell" if breakout_direction == "buy" else "buy"
