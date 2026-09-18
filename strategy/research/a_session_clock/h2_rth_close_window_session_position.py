"""H2 -- RTH close-window (last ~30 minutes) session-position effect.

PRE-REGISTRATION (written before this strategy was ever run on any fold).

Mechanism (source paper): options and leveraged-ETF market makers running
short-gamma books must trade in the direction of the day's price move to
stay delta-neutral; this hedging flow concentrates deterministically into
the final ~30 minutes before the 16:00 ET cash close -- a clock-timed
flow-concentration event independent of any specific price level.

Source: Baltussen, Da, Lammers & Martens, "Hedging Demand and Market
Intraday Momentum," Journal of Financial Economics 142 (2021) 377-403 --
60+ futures 1974-2020, explicitly including the S&P E-mini traded
09:30-16:00 ET.

Reframing for this family's scope: the source paper's actual tradeable
signal fades or extends the day's REALIZED return-so-far (a price-conditioned
signal) into the close -- that belongs to families B/C/D, not this one. What
IS in this family's scope, and is what this file tests, is the UNCONDITIONAL
question: does the last-30-minute RTH window (15:30-16:00 ET) show a
distinguishable-from-zero average directional return, independent of that
day's own price path? This is directly computable from the clock alone.

Why BOTH directions are pre-registered together: the hedging-flow mechanism
is directionally SYMMETRIC by construction -- short-gamma dealers amplify
whichever direction the day already moved, so nothing in the mechanism
implies a net-long or net-short bias for the unconditional (not
return-conditioned) window. Rather than picking a sign after looking at the
data (which would be exactly the kind of post-hoc directional pick this
whole program is designed to catch), this hypothesis is formalized as TWO
pre-specified, equally-weighted trials -- ``direction="buy"`` and
``direction="sell"`` -- run and reported together. That is 2 trials, not 1,
and both count toward the family's multiple-comparisons denominator whether
or not either passes.

Formalization: once per trade date, at the first bar whose decision time
enters [15:30, 16:00) ET, if flat and not already traded today, enter
QUANTITY_MICROS in ``direction``. Exit unconditionally at the first bar
whose decision time reaches 16:00 ET.

Parameters (ONE window, taken directly from the source paper's stated
"last 30 minutes" horizon -- no grid, no tuning of the window width):
    WINDOW_START_ET = 15:30
    WINDOW_END_ET   = 16:00
    QUANTITY_MICROS = 1
    direction in {"buy", "sell"}  -- both pre-specified, both run

SUPPORT CONDITION: measured on TRAIN folds only, from the closed-round-trip
ledger, after the modelled $2.64/RT MES cost. Support requires ALL of:
  (a) at least ONE of the two pre-registered directions clears the ROBUST
      verdict from funnel.power_gate.screen(..., robust=True) as "pass" at
      the nearest available segments_per_day grid point (T=1, by
      construction -- at most one round trip per trade date);
  (b) the realized win probability p and win/loss ratio R that produced that
      pass are the MEASURED figures from the ledger, not a hand-picked grid
      point;
  (c) the pass replicates across all 8 train folds for that direction, per
      the task's re-run requirement, without the ROBUST verdict flipping to
      fail/marginal on more than one or two folds;
  (d) BOTH directions are reported regardless of outcome -- a pass in one
      direction and a fail in the other is itself the finding (a directional
      last-30-minute drift exists), not evidence to discard the losing side.

REFUTE CONDITION: ANY of the following is sufficient to refute, at the
modelled cost:
  (a) NEITHER direction clears the ROBUST verdict on its first fold;
  (b) net P&L over the closed round trips is <= $0 after cost, in both
      directions;
  (c) the MATCHED verdict passes but the ROBUST verdict does not, in both
      directions (apparent edge explained by size/activity against a
      favorable null, not signal);
  (d) trades per day is necessarily ~1 by construction, so fewer than ~30
      closed round trips over a fold's train window is UNDERPOWERED and must
      be reported as such rather than folded into a pass/fail count.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time

from rules.xfa_rules import OrderIntent, Refusal
from strategy.interface import AccountView, Bar, market_intent
from strategy.research.a_session_clock._clock import et_time

WINDOW_START_ET = time(15, 30)
WINDOW_END_ET = time(16, 0)
QUANTITY_MICROS = 1
SIDES = ("buy", "sell")


def _opposite(side: str) -> str:
    return "sell" if side == "buy" else "buy"


@dataclass(frozen=True)
class H2RthCloseWindowSessionPosition:
    """Directional bet in the last 30 minutes of RTH (15:30-16:00 ET), once per day.

    ``direction`` is a pre-registered strategy parameter, not a tuned one -- see the
    module docstring: both "buy" and "sell" are formalized and screened together.
    """

    direction: str
    name: str = "h2_rth_close_window_session_position"
    window_start_et: time = WINDOW_START_ET
    window_end_et: time = WINDOW_END_ET
    quantity_micros: int = QUANTITY_MICROS
    _current_trade_date: list[date | None] = field(default_factory=lambda: [None])
    _traded_today: list[bool] = field(default_factory=lambda: [False])

    def __post_init__(self) -> None:
        if self.direction not in SIDES:
            raise ValueError(f"direction {self.direction!r} must be one of {SIDES}")
        if self.window_start_et >= self.window_end_et:
            raise ValueError(
                f"window [{self.window_start_et}, {self.window_end_et}) is not a valid "
                "half-open ET window"
            )
        if isinstance(self.quantity_micros, bool) or not isinstance(self.quantity_micros, int) \
                or self.quantity_micros <= 0:
            raise ValueError(f"quantity_micros {self.quantity_micros!r} must be a positive int")

    def _reset_on_new_session(self, bar: Bar) -> None:
        if self._current_trade_date[0] != bar.trade_date:
            self._current_trade_date[0] = bar.trade_date
            self._traded_today[0] = False

    def on_bar(self, bar: Bar, account: AccountView) -> tuple[OrderIntent | Refusal, ...]:
        self._reset_on_new_session(bar)
        t = et_time(bar.decision_ts_utc)
        flat = account.position_micros == 0 and account.pending_signed_micros == 0

        if account.position_micros != 0 and t >= self.window_end_et:
            side = "sell" if account.position_micros > 0 else "buy"
            return (market_intent(bar, side, abs(account.position_micros)),)

        if flat and not self._traded_today[0] and self.window_start_et <= t < self.window_end_et:
            self._traded_today[0] = True
            return (market_intent(bar, self.direction, self.quantity_micros),)

        return ()
