"""H3 -- Day-of-week return-distribution effect (classic "weekend effect"), with an
explicit regime-instability prior.

PRE-REGISTRATION (written before this strategy was ever run on any fold).

Mechanism: weekend non-trading creates an information/positioning
discontinuity: risk-reduction ahead of the close-out period and reopening
adjustments concentrate directional bias on specific weekdays, independent
of price level. The classic form of this finding (French 1980 and the
broader "weekend effect" literature) is that Monday RTH returns run
systematically negative while Friday RTH returns run systematically
positive, relative to the other three weekdays.

Source cited by the research stage: Johnston, Kracaw & McConnell,
"Day-of-the-Week Effects in Financial Futures," Journal of Financial and
Quantitative Analysis 26(1) 1991 -- GNMA/T-bond/T-note/T-bill futures,
showing the Monday seasonal existed only pre-1982 and the Tuesday seasonal
only post-1984. That paper is itself a warning about regime instability, not
a confirmation that Monday/Friday is the right pair for MES in 2025-2026;
the classic equity-market Monday/Friday pattern (not JKM's own T-bond
finding) is what is formalized and tested here, because it is the pattern
the family's research stage judged most likely to plausibly transfer to an
equity-index product, while JKM's own result is cited specifically as the
reason this must be screened as exploratory rather than trusted at face
value.

Why ONE combined pre-registered trial, not a five-way weekday sweep: with
311 MES research days (~62 weeks), any day-of-week finding is low-power by
construction. Testing all five weekdays independently before looking at any
result would multiply the number of trials without a corresponding increase
in evidence per trial, and IS exactly the kind of undisciplined grid this
research program's cost-and-power discipline exists to prevent. This file
therefore formalizes and screens exactly the ONE pre-specified classic
pattern -- short Monday, long Friday, flat every other weekday -- as a
SINGLE combined strategy (one ledger, one p/R/T reading). A five-way weekday
sweep is explicitly NOT run in this pass; if this single pre-registered test
clears the robust bar, a wider weekday sweep becomes necessary future work
and must be run through funnel/multiple_comparisons.py (already present in
the repo) before being taken seriously -- that is a LIMITATION of this pass,
not a gap silently papered over.

Formalization: day-of-week comes from ``bar.trade_date.weekday()`` (Monday=0
.. Friday=4), never from a UTC/ET wall-clock date (see
``strategy.research.a_session_clock._clock`` module docstring for why). Once
per trade date, at the first RTH bar (09:30 ET) on a Monday, if flat, SELL
QUANTITY_MICROS; on a Friday, if flat, BUY QUANTITY_MICROS. On Tuesday,
Wednesday and Thursday, take no position. Exit unconditionally at the first
bar whose decision time reaches 16:00 ET (RTH close).

Parameters (ONE setting; the RTH open/close window is shared with H2/H4's
09:30-16:00 ET convention, not independently chosen here):
    RTH_OPEN_ET, RTH_CLOSE_ET = 09:30, 16:00
    MONDAY_SIDE = "sell"
    FRIDAY_SIDE = "buy"
    QUANTITY_MICROS = 1

SUPPORT CONDITION: measured on TRAIN folds only, from the closed-round-trip
ledger, after the modelled $2.64/RT MES cost. Support requires ALL of:
  (a) the ROBUST verdict from funnel.power_gate.screen(..., robust=True) is
      "pass" at the nearest available segments_per_day grid point to the
      measured trades/day T (this strategy trades at most twice a week --
      once on Monday, once on Friday -- so T will be well below 1/day; the
      nearest grid point is T=1 and that approximation must be flagged, not
      silently assumed correct);
  (b) the realized win probability p and win/loss ratio R that produced that
      pass are the MEASURED figures from the combined Monday+Friday ledger;
  (c) the pass replicates across all 8 train folds, per the task's re-run
      requirement, WITHOUT large swings in verdict across folds -- given
      the source paper's own explicit regime-instability finding, an
      unstable pass (verdict flips fold to fold) should be read as
      confirming that instability prior, not as support;
  (d) the strategy is run through
      funnel.multiple_comparisons.harvey_liu_zhu_verdict and
      funnel.multiple_comparisons.deflated_sharpe_ratio before being reported
      as a candidate, with the trial count set to at least the 6 trials run
      across this whole family (H1: 1, H2: 2, H3: 1, H4: 2), and the pass
      must survive the HLZ t > 3.0 hurdle, not just the conventional t > 2.0.
A pass here, even a robust one, should be read with active suspicion given
n_train_days ~= 142 (~28 weeks -- only ~28 Mondays and ~28 Fridays per fold).

REFUTE CONDITION: ANY of the following is sufficient to refute, at the
modelled cost:
  (a) the ROBUST verdict is "fail" or "marginal" on the first fold tested;
  (b) net P&L over the closed round trips is <= $0 after cost;
  (c) the MATCHED verdict passes but the ROBUST verdict does not;
  (d) fewer than ~30 closed round trips over a fold's train window (highly
      likely, given ~28 Mondays + ~28 Fridays per 142-day train window, many
      of which will be refused by roll-blackout/holiday/flatten-window
      logic) -- this makes the measurement UNDERPOWERED, which must be
      reported as such, not folded into a pass/fail count;
  (e) the verdict is unstable across the 8 train folds (flips between pass
      and fail) -- per JKM's own finding, THIS is the single most likely
      outcome, and is itself the headline finding for this hypothesis if it
      occurs, not a footnote.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from rules.xfa_rules import OrderIntent, Refusal
from strategy.interface import AccountView, Bar, market_intent
from strategy.research.a_session_clock._clock import (
    FRIDAY,
    MONDAY,
    RTH_CLOSE_ET,
    RTH_OPEN_ET,
    et_time,
)

MONDAY_SIDE = "sell"
FRIDAY_SIDE = "buy"
QUANTITY_MICROS = 1


@dataclass(frozen=True)
class H3WeekendEffect:
    """Short Monday RTH, long Friday RTH, flat every other weekday. One combined ledger."""

    name: str = "h3_weekend_effect"
    monday_side: str = MONDAY_SIDE
    friday_side: str = FRIDAY_SIDE
    quantity_micros: int = QUANTITY_MICROS
    _current_trade_date: list[date | None] = field(default_factory=lambda: [None])
    _traded_today: list[bool] = field(default_factory=lambda: [False])

    def __post_init__(self) -> None:
        if self.monday_side not in ("buy", "sell"):
            raise ValueError(f"monday_side {self.monday_side!r} must be 'buy' or 'sell'")
        if self.friday_side not in ("buy", "sell"):
            raise ValueError(f"friday_side {self.friday_side!r} must be 'buy' or 'sell'")
        if isinstance(self.quantity_micros, bool) or not isinstance(self.quantity_micros, int) \
                or self.quantity_micros <= 0:
            raise ValueError(f"quantity_micros {self.quantity_micros!r} must be a positive int")

    def _reset_on_new_session(self, bar: Bar) -> None:
        if self._current_trade_date[0] != bar.trade_date:
            self._current_trade_date[0] = bar.trade_date
            self._traded_today[0] = False

    def _entry_side(self, bar: Bar) -> str | None:
        weekday = bar.trade_date.weekday()
        if weekday == MONDAY:
            return self.monday_side
        if weekday == FRIDAY:
            return self.friday_side
        return None

    def on_bar(self, bar: Bar, account: AccountView) -> tuple[OrderIntent | Refusal, ...]:
        self._reset_on_new_session(bar)
        t = et_time(bar.decision_ts_utc)
        flat = account.position_micros == 0 and account.pending_signed_micros == 0

        if account.position_micros != 0 and t >= RTH_CLOSE_ET:
            side = "sell" if account.position_micros > 0 else "buy"
            return (market_intent(bar, side, abs(account.position_micros)),)

        entry_side = self._entry_side(bar)
        if flat and not self._traded_today[0] and entry_side is not None and (
            RTH_OPEN_ET <= t < RTH_CLOSE_ET
        ):
            self._traded_today[0] = True
            return (market_intent(bar, entry_side, self.quantity_micros),)

        return ()
