"""H4 -- Overnight gap size/direction as a conditioning variable (inventory-risk
vs. informed-shock discrimination).

PRE-REGISTRATION (written before this strategy was ever run on any fold).

Mechanism: S&P 500 futures overnight returns carry a systematic,
statistically robust, inventory-risk-driven drift (Boyarchenko, Larsen &
Whelan 2020/2022, NY Fed Staff Report 917, verified full text): positive in
20/23 years, concentrated in a narrow overnight window, with an asymmetric
reversal larger after selloffs than after rallies, and NOT explained by
scheduled macro/earnings news. This motivates using the overnight gap size
(computable purely from this trade date's first bar open vs. the prior
trade date's last bar close -- no order-book/tick or second-instrument
dependency) as a STATE variable that discriminates two regimes:
  - small-to-moderate gaps: hypothesized to be dominated by the
    inventory-risk/reversal mechanism -> fade the gap (bet on reversion);
  - unusually large gaps: hypothesized to more often reflect a genuine
    information shock, where the fade mechanism should NOT apply.
The Fed paper's exact timing/magnitude was estimated on continuous S&P 500
futures data from 1998 onward (predating MES, and likely an ES-continuous
construction), so this module re-estimates the split points independently
on the 311-date MES sample via a rolling percentile rather than importing
the paper's numbers directly.

Simplification stated explicitly, not hidden: this formalization only
implements the "fade small/moderate gaps" branch. It does NOT implement an
invert-on-large-gaps branch (i.e., trading WITH large gaps as a shock
signal) -- that would be a second, independently falsifiable hypothesis
about shock continuation with its own literature search, out of scope for
this pass. On large-gap days this module simply does not trade.

State construction (fully causal, zero look-ahead):
1. At the first bar of each new trade date (a ``bar.trade_date`` change),
   gap = bar.open / prior_trade_date_last_close - 1, using the immediately
   preceding trade date's final processed bar close (known in full before
   this decision).
2. |gap| is percentile-ranked against a trailing deque of the last
   REGIME_LOOKBACK_DAYS |gap| values from STRICTLY EARLIER trade dates (the
   percentile is taken, then |gap| is appended -- same append-after-use
   order as every rolling-percentile module in this family).
3. Until MIN_HISTORY_DAYS prior gap observations exist, no entry is gated
   on (warm-up). The very first trade date processed has no prior close at
   all and is skipped outright.
4. BAND_LOW_PCTL <= percentile <= BAND_HIGH_PCTL => "small-to-moderate";
   outside that band => "large" (no trade, see simplification above).

Base entry (deliberately unoptimized scaffolding constituting the state
signal itself, per this family's explicit scope: "usable ... as a
directional signal in its own right"): on a small-to-moderate gap day, at
that trade date's first bar's decision time, go opposite the gap's sign
(sell after an up-gap, buy after a down-gap), QUANTITY_MICROS fixed, hold
HOLD_MINUTES bars, then flatten unconditionally. One parameterization only;
see constants below.

SUPPORT CONDITION: measured on TRAIN folds only, from the closed-round-trip
ledger, after modelled cost. Support requires ALL of:
  (a) the ROBUST verdict from funnel.power_gate.screen(..., robust=True) is
      "pass" at the nearest available segments_per_day grid point;
  (b) p and R are the MEASURED ledger figures, not a hand-picked grid point;
  (c) at least ~30 closed round trips over the sample;
  (d) a first-fold pass is confirmed across ALL 8 train folds with a spread
      report, not just one fold;
  (e) the sign check matches the mechanism: mean P&L on the SHORT trades
      (after up-gaps) should not be driven entirely by a handful of large
      losers offset by many small winners in a way that contradicts "fading
      small/moderate gaps wins on average" -- i.e. wins and losses should
      look like genuine mean-reversion, not a skewed/lottery-like payoff
      that happens to pass the gate's p/R combination by luck of the
      measured sample.

REFUTE CONDITION: ANY of the following is sufficient to refute, at modelled
cost:
  (a) the ROBUST verdict is "fail" or "marginal";
  (b) net P&L over the closed round trips is <= $0 after cost;
  (c) the MATCHED verdict passes but the ROBUST verdict does not;
  (d) fewer than ~30 closed round trips over the train fold -- UNDERPOWERED,
      reported as such rather than folded into a pass/fail count;
  (e) most trade dates in the fold never reach the band (e.g. because the
      MES sample's gap distribution is much tighter or wider than assumed)
      -- in that case trades/day is not a meaningfully estimated quantity
      either, and the run should be reported as underpowered by construction
      rather than screened at face value.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from rules.xfa_rules import OrderIntent, Refusal
from strategy.interface import AccountView, Bar, market_intent

REGIME_LOOKBACK_DAYS = 60
MIN_HISTORY_DAYS = 30
BAND_LOW_PCTL = 0.20
BAND_HIGH_PCTL = 0.80
HOLD_MINUTES = 30
QUANTITY_MICROS = 1


def _percentile_rank(window: deque[float], value: float) -> float:
    """Fraction of ``window`` strictly below ``value`` (ties count half)."""
    if not window:
        return 0.0
    below = sum(1 for x in window if x < value)
    equal = sum(1 for x in window if x == value)
    return (below + 0.5 * equal) / len(window)


@dataclass(frozen=True)
class H4OvernightGapFade:
    """Fade small-to-moderate overnight gaps; sit out large ones and the warm-up period."""

    name: str = "h4_overnight_gap_fade"
    regime_lookback_days: int = REGIME_LOOKBACK_DAYS
    min_history_days: int = MIN_HISTORY_DAYS
    band_low_pctl: float = BAND_LOW_PCTL
    band_high_pctl: float = BAND_HIGH_PCTL
    hold_minutes: int = HOLD_MINUTES
    quantity_micros: int = QUANTITY_MICROS
    # Mutable working state behind frozen fields; see H1 for the pattern.
    _gap_history: deque[float] = field(default_factory=deque)
    _last_close_prev_day: list[float | None] = field(default_factory=lambda: [None])
    _current_trade_date: list[object] = field(default_factory=lambda: [None])
    _today_should_fade: list[bool] = field(default_factory=lambda: [False])
    _today_gap_sign: list[int] = field(default_factory=lambda: [0])
    _entered_today: list[bool] = field(default_factory=lambda: [False])
    _bars_since_entry: list[int] = field(default_factory=lambda: [-1])

    def __post_init__(self) -> None:
        if self.regime_lookback_days < 2:
            raise ValueError(f"regime_lookback_days {self.regime_lookback_days!r} must be >= 2")
        if self.min_history_days < 1 or self.min_history_days > self.regime_lookback_days:
            raise ValueError(
                f"min_history_days {self.min_history_days!r} must be in "
                f"[1, regime_lookback_days]"
            )
        if not (0.0 <= self.band_low_pctl < self.band_high_pctl <= 1.0):
            raise ValueError(
                f"band [{self.band_low_pctl}, {self.band_high_pctl}] is not a valid range"
            )
        if self.hold_minutes < 1:
            raise ValueError(f"hold_minutes {self.hold_minutes!r} must be >= 1")
        bad_quantity = (
            isinstance(self.quantity_micros, bool)
            or not isinstance(self.quantity_micros, int)
            or self.quantity_micros <= 0
        )
        if bad_quantity:
            raise ValueError(f"quantity_micros {self.quantity_micros!r} must be a positive int")
        object.__setattr__(self, "_gap_history", deque(maxlen=self.regime_lookback_days))

    def _handle_new_session(self, bar: Bar) -> None:
        if self._current_trade_date[0] == bar.trade_date:
            return
        prev_close = self._last_close_prev_day[0]
        self._current_trade_date[0] = bar.trade_date
        self._entered_today[0] = False
        self._bars_since_entry[0] = -1
        self._today_should_fade[0] = False
        self._today_gap_sign[0] = 0
        if prev_close is None or prev_close <= 0.0:
            return  # first trade date ever processed: no prior close to gap from
        gap = bar.open / prev_close - 1.0
        abs_gap = abs(gap)
        if len(self._gap_history) >= self.min_history_days:
            percentile = _percentile_rank(self._gap_history, abs_gap)
            if self.band_low_pctl <= percentile <= self.band_high_pctl and gap != 0.0:
                self._today_should_fade[0] = True
                self._today_gap_sign[0] = 1 if gap > 0 else -1
        self._gap_history.append(abs_gap)

    def on_bar(self, bar: Bar, account: AccountView) -> tuple[OrderIntent | Refusal, ...]:
        self._handle_new_session(bar)
        intents: tuple[OrderIntent | Refusal, ...] = ()

        # Exit path: unconditional flatten after hold_minutes bars in the trade.
        if account.position_micros != 0 and self._bars_since_entry[0] >= 0:
            self._bars_since_entry[0] += 1
            if self._bars_since_entry[0] >= self.hold_minutes:
                side = "sell" if account.position_micros > 0 else "buy"
                intents = (market_intent(bar, side, abs(account.position_micros)),)
                self._bars_since_entry[0] = -1
                self._last_close_prev_day[0] = bar.close
                return intents

        flat = account.position_micros == 0 and account.pending_signed_micros == 0
        if (
            flat
            and self._today_should_fade[0]
            and not self._entered_today[0]
        ):
            side = "sell" if self._today_gap_sign[0] > 0 else "buy"
            intents = (market_intent(bar, side, self.quantity_micros),)
            self._entered_today[0] = True
            self._bars_since_entry[0] = 0

        self._last_close_prev_day[0] = bar.close
        return intents
