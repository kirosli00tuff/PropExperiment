"""H3 -- Range-compression-precedes-expansion as a gating filter for a simple
breakout base entry.

PRE-REGISTRATION (written before this strategy was ever run on any fold).
EXPLICITLY THE WEAKEST-EVIDENCED HYPOTHESIS IN THIS FAMILY -- held to a
higher bar than H1/H2/H4, per the research-stage limitation note.

Mechanism: a trailing N-bar range in a low percentile of its own rolling
distribution ("compression") is hypothesized to precede a range-expansion
episode, gating (not constituting) a deliberately simple base entry -- break
of the prior BREAKOUT_LOOKBACK-bar high/low. The only full-text source
making this SPECIFIC compression -> expansion transition claim (Bookmap
blog) is vendor narrative content with zero empirical backing: no backtest,
no citations. The more rigorous support available (H1's long-memory /
regime-persistence sources) is a related but genuinely WEAKER claim --
"the current regime tends to persist," not "compression specifically
predicts the next move is a breakout in either direction." This module
formalizes the hypothesis anyway, exactly as instructed, but the screening
bar below is set higher than the other three modules in this package for
that reason.

State construction (fully causal, zero look-ahead, no trade-date reset --
compression/expansion is treated as a continuous-time process here, a
deliberate design choice since this dataset's sessions run close to
back-to-back rather than resetting at a cash-market midnight):
1. range_t = max(high) - min(low) over the trailing RANGE_WINDOW bars,
   INCLUSIVE of the current bar (both known once this bar has closed).
2. range_t is percentile-ranked against a trailing deque of the last
   COMPRESSION_LOOKBACK such values from bars BEFORE the current one (the
   percentile is taken, THEN range_t is appended to the deque -- same
   append-after-use order as every rolling-percentile module in this
   family). Below COMPRESSION_PCTL => "compressed."
3. Until MIN_HISTORY_BARS prior range_t values exist, compression is
   undefined and no entry is gated on (warm-up).

Base entry (deliberately unoptimized scaffolding, NOT this family's
contribution): if flat AND the current bar is compressed, and
bar.close > max(high) over the trailing BREAKOUT_LOOKBACK bars BEFORE this
one, go long; if bar.close < min(low) over that same trailing window, go
short. Otherwise no entry regardless of compression. Hold HOLD_MINUTES bars,
then flatten unconditionally -- no trailing stop, no scale-out; any of that
would be entry-design research this family does not own. One
parameterization only; see constants below.

SUPPORT CONDITION -- HELD TO A HIGHER BAR THAN H1/H2/H4 given the sourcing
gap above. Measured on TRAIN folds only, from the closed-round-trip ledger,
after modelled cost. Support requires ALL of:
  (a) the ROBUST verdict from funnel.power_gate.screen(..., robust=True) is
      "pass" at the nearest available segments_per_day grid point;
  (b) p and R are the MEASURED ledger figures, not a hand-picked grid point;
  (c) at least ~50 closed round trips over the sample (raised from the ~30
      used elsewhere in this family, because a thin sample on the
      weakest-evidenced hypothesis is even less trustworthy);
  (d) a first-fold pass is confirmed across ALL 8 train folds, AND the
      ROBUST verdict is "pass" (not merely non-fail) on at least 6 of the 8
      -- a bare majority is not enough given the sourcing gap;
  (e) the direction of trades roughly balances long/short (the compression
      story has no directional prior) -- a strategy that is overwhelmingly
      one-sided suggests it is picking up a drift artifact of the base
      entry, not a compression-expansion effect.

REFUTE CONDITION: ANY of the following is sufficient to refute, at modelled
cost:
  (a) the ROBUST verdict is "fail" or "marginal";
  (b) net P&L over the closed round trips is <= $0 after cost;
  (c) the MATCHED verdict passes but the ROBUST verdict does not;
  (d) fewer than ~50 closed round trips over the train fold -- UNDERPOWERED,
      reported as such rather than folded into a pass/fail count;
  (e) condition (d) [support] fails, i.e. the robust pass does not hold on
      at least 6 of 8 folds -- treated as a refutation for this hypothesis
      specifically (unlike H1/H2/H4, where fold instability is reported as
      a separate finding rather than an automatic refute), because the thin
      sourcing means this hypothesis gets no benefit of the doubt on
      stability.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from rules.xfa_rules import OrderIntent, Refusal
from strategy.interface import AccountView, Bar, market_intent

RANGE_WINDOW = 20
COMPRESSION_LOOKBACK = 250
MIN_HISTORY_BARS = 125
COMPRESSION_PCTL = 0.20
BREAKOUT_LOOKBACK = 20
HOLD_MINUTES = 15
QUANTITY_MICROS = 1


def _percentile_rank(window: deque[float], value: float) -> float:
    """Fraction of ``window`` strictly below ``value`` (ties count half)."""
    if not window:
        return 0.0
    below = sum(1 for x in window if x < value)
    equal = sum(1 for x in window if x == value)
    return (below + 0.5 * equal) / len(window)


@dataclass(frozen=True)
class H3RangeCompressionGate:
    """Break of the prior N-bar high/low, gated to only fire when trailing range is compressed."""

    name: str = "h3_range_compression_gate"
    range_window: int = RANGE_WINDOW
    compression_lookback: int = COMPRESSION_LOOKBACK
    min_history_bars: int = MIN_HISTORY_BARS
    compression_pctl: float = COMPRESSION_PCTL
    breakout_lookback: int = BREAKOUT_LOOKBACK
    hold_minutes: int = HOLD_MINUTES
    quantity_micros: int = QUANTITY_MICROS
    # Mutable working state behind frozen fields; see H1 for the pattern.
    _range_highs: deque[float] = field(default_factory=deque)
    _range_lows: deque[float] = field(default_factory=deque)
    _breakout_highs: deque[float] = field(default_factory=deque)
    _breakout_lows: deque[float] = field(default_factory=deque)
    _range_history: deque[float] = field(default_factory=deque)
    _bars_since_entry: list[int] = field(default_factory=lambda: [-1])

    def __post_init__(self) -> None:
        if self.range_window < 2:
            raise ValueError(f"range_window {self.range_window!r} must be >= 2")
        if self.compression_lookback < 2:
            raise ValueError(f"compression_lookback {self.compression_lookback!r} must be >= 2")
        if not (1 <= self.min_history_bars <= self.compression_lookback):
            raise ValueError(
                f"min_history_bars {self.min_history_bars!r} must be in "
                f"[1, compression_lookback]"
            )
        if not (0.0 < self.compression_pctl < 1.0):
            raise ValueError(f"compression_pctl {self.compression_pctl!r} must be in (0, 1)")
        if self.breakout_lookback < 1:
            raise ValueError(f"breakout_lookback {self.breakout_lookback!r} must be >= 1")
        if self.hold_minutes < 1:
            raise ValueError(f"hold_minutes {self.hold_minutes!r} must be >= 1")
        bad_quantity = (
            isinstance(self.quantity_micros, bool)
            or not isinstance(self.quantity_micros, int)
            or self.quantity_micros <= 0
        )
        if bad_quantity:
            raise ValueError(f"quantity_micros {self.quantity_micros!r} must be a positive int")
        object.__setattr__(self, "_range_highs", deque(maxlen=self.range_window))
        object.__setattr__(self, "_range_lows", deque(maxlen=self.range_window))
        object.__setattr__(self, "_breakout_highs", deque(maxlen=self.breakout_lookback))
        object.__setattr__(self, "_breakout_lows", deque(maxlen=self.breakout_lookback))
        object.__setattr__(self, "_range_history", deque(maxlen=self.compression_lookback))

    def on_bar(self, bar: Bar, account: AccountView) -> tuple[OrderIntent | Refusal, ...]:
        intents: tuple[OrderIntent | Refusal, ...] = ()

        # Exit path: unconditional flatten after hold_minutes bars in the trade.
        if account.position_micros != 0 and self._bars_since_entry[0] >= 0:
            self._bars_since_entry[0] += 1
            if self._bars_since_entry[0] >= self.hold_minutes:
                side = "sell" if account.position_micros > 0 else "buy"
                intents = (market_intent(bar, side, abs(account.position_micros)),)
                self._bars_since_entry[0] = -1
                self._advance_state(bar)
                return intents

        flat = account.position_micros == 0 and account.pending_signed_micros == 0
        if flat:
            trailing_high = max(self._breakout_highs) if self._breakout_highs else None
            trailing_low = min(self._breakout_lows) if self._breakout_lows else None

            self._range_highs.append(bar.high)
            self._range_lows.append(bar.low)
            range_t = max(self._range_highs) - min(self._range_lows)

            if len(self._range_history) >= self.min_history_bars:
                percentile = _percentile_rank(self._range_history, range_t)
                compressed = percentile <= self.compression_pctl
                if compressed and trailing_high is not None and bar.close > trailing_high:
                    intents = (market_intent(bar, "buy", self.quantity_micros),)
                    self._bars_since_entry[0] = 0
                elif compressed and trailing_low is not None and bar.close < trailing_low:
                    intents = (market_intent(bar, "sell", self.quantity_micros),)
                    self._bars_since_entry[0] = 0

            self._range_history.append(range_t)
            self._breakout_highs.append(bar.high)
            self._breakout_lows.append(bar.low)
            return intents

        self._advance_state(bar)
        return intents

    def _advance_state(self, bar: Bar) -> None:
        """Keep the rolling windows moving on bars where the entry branch did not run
        (e.g. while a position from a prior entry is still open and about to exit)."""
        self._range_highs.append(bar.high)
        self._range_lows.append(bar.low)
        range_t = max(self._range_highs) - min(self._range_lows)
        self._range_history.append(range_t)
        self._breakout_highs.append(bar.high)
        self._breakout_lows.append(bar.low)
