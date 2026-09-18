"""H3 -- Close-location-value extreme-bar reversal.

PRE-REGISTRATION (written before this strategy was ever run on any fold).

Mechanism: a bar whose close sits at an extreme of its own high-low range
(close-location-value, CLV, near +1 or -1) combined with an above-average
true range signals a transient one-sided liquidity/order-imbalance shock.
Expect partial retracement over the following bars as resting liquidity
replenishes and the imbalance clears -- an order-flow rationale for the
classic "key reversal bar" pattern, using only OHLCV-derived proxies
(nothing here is a chartist claim about a chart shape).

1. CLV_t = (2*close - high - low) / (high - low), in [-1, 1]. Undefined
   (high == low, a doji with zero range) is treated as CLV = 0, i.e. never a
   trigger.
2. Maintain a rolling mean of bar range (high - low) over BASELINE_WINDOW
   trailing bars (excluding the current bar).
3. A bar is a trigger if BOTH:
     |CLV_t| >= CLV_THRESHOLD, AND
     range_t / mean_range > RANGE_RATIO_THRESHOLD (above-average true range).
4. If flat at the close of a trigger bar, fade the extreme: sell if
   CLV_t >= CLV_THRESHOLD (close pinned to the high -- one-sided buying
   exhausted), buy if CLV_t <= -CLV_THRESHOLD (close pinned to the low).
5. Hold for HOLD_BARS bars after the fill, then exit unconditionally.

This is deliberately the WEAKEST-evidenced hypothesis in the family (stated
here, before any run, not added after a bad result): the strongest single
quantitative source available -- Mesfin (2026, arXiv:2605.04004) Sec. 4.6,
VVG classifier reversal-on-fade variant -- is a positive-signed but
statistically inconclusive near-miss (N=35 OOS trades, net +13.49 pts,
T=1.26; fails significance and year-stability on that small N). The classic
opening-reversal literature (Fung, Mok & Lam 2000; Grant, Wolf & Yu 2005)
could not be read past the abstract (ScienceDirect 403, no free mirror), so
only the qualitative direction -- reversal after large opening moves, itself
"sharply reduced" once transaction costs were applied per the one verified
Grant/Wolf/Yu abstract quote -- is trustworthy, not an effect size. Given how
many bar-derived variants (this one, and H2) are structurally similar (both
are "extreme bar -> fade" rules differing mainly in which proxy defines
"extreme"), this hypothesis should be screened with the strictest posture of
the three and its multiple-comparisons cost weighed accordingly by the lead.

Parameters (ONE setting, chosen before any backtest was run):
    BASELINE_WINDOW = 60            (1 trailing hour of 1-minute bars)
    CLV_THRESHOLD = 0.80             (close within the outer 10% of the bar's range)
    RANGE_RATIO_THRESHOLD = 1.50     (above-average true range)
    HOLD_BARS = 3                    ("the following few bars")

SUPPORT CONDITION: measured on TRAIN folds only, from the closed-round-trip
ledger, after the modelled $2.64/RT MES cost. Support requires ALL of:
  (a) the ROBUST verdict from funnel.power_gate.screen(..., robust=True) is
      "pass" at the nearest segments_per_day grid point to the measured T;
  (b) that pass uses the MEASURED p and R, not a hand-picked grid point;
  (c) the direction is consistent with fading extreme-CLV bars (net short
      after high-pinned closes, net long after low-pinned closes);
  (d) a first-fold pass survives re-running across all 8 train folds without
      the ROBUST verdict flipping to "fail" on most of them.
Because the best available quantitative evidence for this exact mechanism is
itself a statistically inconclusive near-miss on N=35 trades, a pass here
should be treated with MORE suspicion (not less) of being a false positive
from the number of structurally similar bar-derived variants tried across
this family, and reported to the lead with that caveat attached explicitly.

REFUTE CONDITION: ANY of the following is sufficient to refute, at the
modelled cost:
  (a) the ROBUST verdict is "fail" or "marginal";
  (b) net P&L over the closed round trips is <= $0 after cost;
  (c) the MATCHED verdict passes but the ROBUST verdict does not;
  (d) fewer than ~30 closed round trips over the sample (underpowered, not
      a clean refutation -- must be reported as such, not folded into a
      pass/fail count).
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from rules.xfa_rules import OrderIntent, Refusal
from strategy.interface import AccountView, Bar, market_intent

BASELINE_WINDOW = 60
CLV_THRESHOLD = 0.80
RANGE_RATIO_THRESHOLD = 1.50
HOLD_BARS = 3
QUANTITY_MICROS = 1
_EPS = 1e-9


def _close_location_value(bar: Bar) -> float:
    bar_range = bar.high - bar.low
    if bar_range <= _EPS:
        return 0.0
    return (2.0 * bar.close - bar.high - bar.low) / bar_range


@dataclass(frozen=True)
class H3CloseLocationValueReversal:
    """Fade an above-average-range bar whose close pins to an extreme of its own range."""

    name: str = "h3_close_location_value_reversal"
    baseline_window: int = BASELINE_WINDOW
    clv_threshold: float = CLV_THRESHOLD
    range_ratio_threshold: float = RANGE_RATIO_THRESHOLD
    hold_bars: int = HOLD_BARS
    quantity_micros: int = QUANTITY_MICROS
    _ranges: deque[float] = field(default_factory=deque)
    _bars_since_entry: list[int] = field(default_factory=lambda: [-1])
    _current_trade_date: list[object] = field(default_factory=lambda: [None])

    def __post_init__(self) -> None:
        if self.baseline_window < 2:
            raise ValueError(f"baseline_window {self.baseline_window!r} must be >= 2")
        if not (0.0 < self.clv_threshold <= 1.0):
            raise ValueError(f"clv_threshold {self.clv_threshold!r} must be in (0, 1]")
        if self.range_ratio_threshold <= 1.0:
            raise ValueError(f"range_ratio_threshold {self.range_ratio_threshold!r} must be > 1")
        if self.hold_bars < 1:
            raise ValueError(f"hold_bars {self.hold_bars!r} must be >= 1")
        if isinstance(self.quantity_micros, bool) or not isinstance(self.quantity_micros, int) \
                or self.quantity_micros <= 0:
            raise ValueError(f"quantity_micros {self.quantity_micros!r} must be a positive int")
        object.__setattr__(self, "_ranges", deque(maxlen=self.baseline_window))

    def _reset_on_new_session(self, bar: Bar) -> None:
        if self._current_trade_date[0] != bar.trade_date:
            self._current_trade_date[0] = bar.trade_date
            self._ranges.clear()
            self._bars_since_entry[0] = -1

    def on_bar(self, bar: Bar, account: AccountView) -> tuple[OrderIntent | Refusal, ...]:
        self._reset_on_new_session(bar)
        bar_range = bar.high - bar.low

        if account.position_micros != 0 and self._bars_since_entry[0] >= 0:
            self._bars_since_entry[0] += 1
            if self._bars_since_entry[0] >= self.hold_bars:
                side = "sell" if account.position_micros > 0 else "buy"
                self._bars_since_entry[0] = -1
                self._ranges.append(bar_range)
                return (market_intent(bar, side, abs(account.position_micros)),)

        flat = account.position_micros == 0 and account.pending_signed_micros == 0
        intents: tuple[OrderIntent | Refusal, ...] = ()

        if flat and len(self._ranges) >= self.baseline_window:
            mean_range = sum(self._ranges) / len(self._ranges)
            range_ratio = bar_range / mean_range if mean_range > _EPS else 0.0
            clv = _close_location_value(bar)
            if range_ratio > self.range_ratio_threshold and abs(clv) >= self.clv_threshold:
                side = "sell" if clv >= self.clv_threshold else "buy"
                intents = (market_intent(bar, side, self.quantity_micros),)
                self._bars_since_entry[0] = 0

        self._ranges.append(bar_range)
        return intents
