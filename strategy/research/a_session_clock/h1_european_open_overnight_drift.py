"""H1 -- European-open overnight-drift regime check (02:00-03:00am ET clock window).

PRE-REGISTRATION (written before this strategy was ever run on any fold).

Mechanism: prior-day RTH closing order imbalance is absorbed by risk-averse
dealers overnight; the imbalance resolves deterministically at a fixed clock
time (European equity-market open, ~08:00-09:00 London / 02:00-03:00 ET),
producing a historically large, statistically robust positive return
concentrated in exactly that hour -- a pure flow-timing effect keyed to the
clock, not to any price level.

Source: Boyarchenko, Larsen & Whelan, "The Overnight Drift," NY Fed Staff
Report 917 (rev. 2022) -- S&P 500 futures, 1998-2019, ~3.7%/yr in the window,
20/23 years positive. Updated by Liberty Street Economics (2026), which
reports the effect had decayed to approximately zero by 2021-2025.

Why this is a REGIME CHECK, not an edge hunt: MES's research window
(2025-04-01 .. 2026-06-12) sits entirely inside the NY Fed's own 2021-2025
"disappeared" sample. The honest prior going in is that this window shows
little or no residual drift. Testing it anyway is still worthwhile -- it is
a direct, cheap, fully clock-based check of whether the well-known historical
effect has any residual presence on the exact instrument and sample on disk.

Formalization: a single long-only position, taken once per trade date. Flat
before the window; at the first bar whose decision time falls in
[02:00, 03:00) ET, if flat and not already traded today, buy QUANTITY_MICROS.
Exit unconditionally at the first bar whose decision time reaches 03:00 ET
(or earlier, if the engine's own MLL/roll-blackout machinery forces it). No
price, range or volatility conditioning anywhere in this logic -- the entry
and exit triggers are pure ET clock comparisons against ``bar.trade_date``
and ``bar.decision_ts_utc``.

Parameters (ONE setting, taken directly from the source paper's own stated
window -- no grid, no tuning):
    WINDOW_START_ET = 02:00
    WINDOW_END_ET   = 03:00
    QUANTITY_MICROS = 1

SUPPORT CONDITION: measured on TRAIN folds only, from the closed-round-trip
ledger, after the modelled $2.64/RT MES cost. Support requires ALL of:
  (a) the ROBUST verdict from funnel.power_gate.screen(..., robust=True) is
      "pass" (not "marginal", not "fail") at the nearest available
      segments_per_day grid point to the measured trades/day T (this
      strategy trades at most once per day, so T will be screened at the
      T=1 grid point regardless of the exact measured value, with that
      approximation flagged);
  (b) the realized win probability p and win/loss ratio R that produced that
      pass are the MEASURED figures from the ledger, not a hand-picked grid
      point;
  (c) the position is net LONG in the window (matching the mechanism's
      stated sign -- a positive drift). A profitable SHORT-biased result
      would falsify the mechanism even if some statistic looked favorable;
  (d) the pass replicates across all 8 train folds (not just the first one
      tested), per the task's re-run requirement, without the ROBUST verdict
      flipping to fail/marginal on more than one or two folds.
Given the regime-decay prior above, genuine support here would itself be a
notable, surprising finding that should be reported prominently rather than
waved through.

REFUTE CONDITION: ANY of the following is sufficient to refute, at the
modelled cost:
  (a) the ROBUST verdict is "fail" or "marginal" on the first fold tested;
  (b) net P&L over the closed round trips is <= $0 after cost;
  (c) the MATCHED verdict passes but the ROBUST verdict does not (apparent
      edge explained by size/activity against a favorable null, not signal);
  (d) trades per day is necessarily ~1 by construction (one window per
      trading day), so with ~142 train days this gives at most ~142 closed
      round trips per fold -- fewer than that (due to refused/blackout days)
      would need to be flagged as underpowered rather than folded into a
      pass/fail count, but is not on its own a refutation as long as the
      measured n is reported honestly.
The prior, stated up front: refutation (a null-ish result) is the EXPECTED
and, per the cited follow-up research, the more scientifically credible
outcome for this hypothesis on this sample.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time

from rules.xfa_rules import OrderIntent, Refusal
from strategy.interface import AccountView, Bar, market_intent
from strategy.research.a_session_clock._clock import et_time

WINDOW_START_ET = time(2, 0)
WINDOW_END_ET = time(3, 0)
QUANTITY_MICROS = 1


@dataclass(frozen=True)
class H1EuropeanOpenOvernightDrift:
    """Long-only, once per trade date, exactly the 02:00-03:00 ET clock window."""

    name: str = "h1_european_open_overnight_drift"
    window_start_et: time = WINDOW_START_ET
    window_end_et: time = WINDOW_END_ET
    quantity_micros: int = QUANTITY_MICROS
    # Mutable working state behind frozen fields, list-wrapped so it can be mutated in
    # place without reassigning a frozen attribute (same pattern as the sibling families).
    _current_trade_date: list[date | None] = field(default_factory=lambda: [None])
    _traded_today: list[bool] = field(default_factory=lambda: [False])

    def __post_init__(self) -> None:
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
            return (market_intent(bar, "buy", self.quantity_micros),)

        return ()
