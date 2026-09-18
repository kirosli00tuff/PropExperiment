"""H2 -- Post-volume-spike / post-range-expansion exhaustion fade.

PRE-REGISTRATION (written before this strategy was ever run on any fold).

Mechanism: after a bar whose volume and/or range is far above its own rolling
baseline (a volume or range "spike"/"expansion" bar), fade that bar's
direction over the following bars, on the theory that aggressive/informed
flow exhausts within the triggering bar and liquidity providers push price
back as the book re-forms.

1. Maintain rolling means/stdevs of 1-minute volume and 1-minute range
   (high - low) over BASELINE_WINDOW trailing bars (excluding the current
   bar, so the trigger bar is compared to what came strictly before it).
2. A bar is a trigger if EITHER:
     volume_zscore = (volume - mean) / stdev > VOLUME_Z_THRESHOLD, OR
     range_ratio  = range / mean_range > RANGE_RATIO_THRESHOLD.
3. If flat at the close of a trigger bar, fade its direction: sell if the
   trigger bar closed above its open (an up bar), buy if it closed below its
   open (a down bar). A trigger bar with close == open is not faded (no
   direction to fade).
4. Hold for HOLD_BARS bars after the fill, then exit unconditionally.

ENTRY-TIMING LIMITATION (stated up front, not discovered after a bad
result): Mesfin (2026, arXiv:2605.04004) Sec. 4.5 reports that a naive
next-bar-close entry on a single-bar volume spike signal already fails net
of cost on MNQ, and that entry timing (intra-bar vs. next-bar-open vs.
next-bar-close) matters to whether the exhaustion window is captured at all.
``strategy/interface.py`` gives this project exactly ONE fill model: an
accepted market intent fills at the NEXT bar's open, never intra-bar and
never at a later bar's close. That is the ENTRY TIMING THIS FILE TESTS, and
it is also the exact "naive" timing the cited evidence says already failed
on a comparable micro equity-index contract at a coarser (5-minute)
resolution. Testing intra-bar or delayed-close entry timing would need a
capability (partial-bar fill, or an order type beyond ``market_intent``)
that ``strategy/interface.py`` and ``sim/fill_model.py`` do not provide and
that this task explicitly prohibits building around
(ABSOLUTE PROHIBITIONS #4). That is recorded as a LIMITATION of this run,
not worked around.

Parameters (ONE setting, chosen before any backtest was run):
    BASELINE_WINDOW = 60           (1 trailing hour of 1-minute bars)
    VOLUME_Z_THRESHOLD = 3.0       ("far above" baseline)
    RANGE_RATIO_THRESHOLD = 3.0    ("far above" baseline)
    HOLD_BARS = 2                  (midpoint of the mechanism's "next 1-3 bars")

SUPPORT CONDITION: measured on TRAIN folds only, from the closed-round-trip
ledger, after the modelled $2.64/RT MES cost. Support requires ALL of:
  (a) the ROBUST verdict from funnel.power_gate.screen(..., robust=True) is
      "pass" at the nearest segments_per_day grid point to the measured T;
  (b) that pass uses the MEASURED p and R, not a hand-picked grid point;
  (c) the direction is consistent with fading (net short after up-spikes,
      net long after down-spikes), not some other artifact;
  (d) if a first-fold pass occurs, it must survive re-running across all 8
      train folds without the ROBUST verdict flipping to "fail" on most of
      them -- a single lucky fold is not support.
Given that Mesfin's T=-11.52 exhaustion finding is real and strong on MNQ
while the naive single-bar volume-spike signal (T=-2.21/-3.08) already fails
net of cost on the SAME instrument class, this hypothesis is explicitly
flagged HIGH RISK of failing at modelled MES cost -- the entry-timing
limitation above means this file can only test the version of H2 closest to
the one Mesfin already showed fails, not the one that showed the strong
T=-11.52 result.

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
VOLUME_Z_THRESHOLD = 3.0
RANGE_RATIO_THRESHOLD = 3.0
HOLD_BARS = 2
QUANTITY_MICROS = 1
_EPS = 1e-9


@dataclass(frozen=True)
class H2PostSpikeExhaustionFade:
    """Fade a 1-minute volume or range spike bar for HOLD_BARS bars."""

    name: str = "h2_post_spike_exhaustion_fade"
    baseline_window: int = BASELINE_WINDOW
    volume_z_threshold: float = VOLUME_Z_THRESHOLD
    range_ratio_threshold: float = RANGE_RATIO_THRESHOLD
    hold_bars: int = HOLD_BARS
    quantity_micros: int = QUANTITY_MICROS
    _volumes: deque[float] = field(default_factory=deque)
    _ranges: deque[float] = field(default_factory=deque)
    _bars_since_entry: list[int] = field(default_factory=lambda: [-1])
    _current_trade_date: list[object] = field(default_factory=lambda: [None])

    def __post_init__(self) -> None:
        if self.baseline_window < 2:
            raise ValueError(f"baseline_window {self.baseline_window!r} must be >= 2")
        if self.volume_z_threshold <= 0:
            raise ValueError(f"volume_z_threshold {self.volume_z_threshold!r} must be > 0")
        if self.range_ratio_threshold <= 1.0:
            raise ValueError(f"range_ratio_threshold {self.range_ratio_threshold!r} must be > 1")
        if self.hold_bars < 1:
            raise ValueError(f"hold_bars {self.hold_bars!r} must be >= 1")
        if isinstance(self.quantity_micros, bool) or not isinstance(self.quantity_micros, int) \
                or self.quantity_micros <= 0:
            raise ValueError(f"quantity_micros {self.quantity_micros!r} must be a positive int")
        object.__setattr__(self, "_volumes", deque(maxlen=self.baseline_window))
        object.__setattr__(self, "_ranges", deque(maxlen=self.baseline_window))

    def _reset_on_new_session(self, bar: Bar) -> None:
        if self._current_trade_date[0] != bar.trade_date:
            self._current_trade_date[0] = bar.trade_date
            self._volumes.clear()
            self._ranges.clear()
            self._bars_since_entry[0] = -1

    @staticmethod
    def _mean_std(values: deque[float]) -> tuple[float, float]:
        n = len(values)
        mean = sum(values) / n
        var = sum((v - mean) ** 2 for v in values) / n
        return mean, var**0.5

    def on_bar(self, bar: Bar, account: AccountView) -> tuple[OrderIntent | Refusal, ...]:
        self._reset_on_new_session(bar)
        bar_range = bar.high - bar.low

        # Exit path first: count bars since entry, flatten after hold_bars.
        if account.position_micros != 0 and self._bars_since_entry[0] >= 0:
            self._bars_since_entry[0] += 1
            if self._bars_since_entry[0] >= self.hold_bars:
                side = "sell" if account.position_micros > 0 else "buy"
                self._bars_since_entry[0] = -1
                self._volumes.append(bar.volume)
                self._ranges.append(bar_range)
                return (market_intent(bar, side, abs(account.position_micros)),)

        flat = account.position_micros == 0 and account.pending_signed_micros == 0
        intents: tuple[OrderIntent | Refusal, ...] = ()

        if flat and len(self._volumes) >= self.baseline_window:
            vol_mean, vol_std = self._mean_std(self._volumes)
            range_mean, _ = self._mean_std(self._ranges)
            volume_z = (bar.volume - vol_mean) / vol_std if vol_std > _EPS else 0.0
            range_ratio = bar_range / range_mean if range_mean > _EPS else 0.0
            is_trigger = (volume_z > self.volume_z_threshold
                          or range_ratio > self.range_ratio_threshold)
            if is_trigger and bar.close != bar.open:
                side = "sell" if bar.close > bar.open else "buy"
                intents = (market_intent(bar, side, self.quantity_micros),)
                self._bars_since_entry[0] = 0

        self._volumes.append(bar.volume)
        self._ranges.append(bar_range)
        return intents
