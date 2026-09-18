"""H2 -- Post-release liquidity-withdrawal / volatility-expansion momentum continuation.

PRE-REGISTRATION (written before this strategy was ever run on any fold).

Mechanism: around the exact minute of a known scheduled release (8:30am ET
for CPI/NFP, 2:00pm ET for FOMC), watch the ENTRY_WINDOW_MINUTES immediately
after the release. If the realized 1-minute range over that reaction window
expands well beyond its own pre-release baseline (a bar-derived proxy for
the price-discovery/re-pricing burst the microstructure literature
documents), enter in the direction of the reaction window's net return
(momentum continuation, on the theory that price discovery is still
concentrated and incomplete) and hold for HOLD_MINUTES bars, then exit
unconditionally.

Source citation: Haynes & Roberts (2015, CFTC Office of Chief Economist)
measure, directly on E-mini S&P 500 futures transaction data around BLS
employment reports, that automated liquidity provision drops immediately
pre-release and price discovery concentrates within roughly the first
minute, normalizing over 5-15 minutes. Takahashi (2025, arXiv:2508.06788)
corroborates with a structural-VAR on the same instrument: macro news
announcements raise price impact and return volatility while lowering flow
impact and flow volatility. Both are microstructure-level findings on the
exact instrument class this research program trades.

DEGRADATION FROM THE CITED METHODOLOGY (stated up front): both anchor papers
use order-flow-imbalance and liquidity-provision measures built from
book/trade-level data. This session has NO order-book or tick data on disk
(the two mbp-10 book days the cost model was calibrated from both fall
inside the sealed holdout). The only available proxy is the one implemented
here -- a 1-minute-bar realized-range expansion trigger around the known
release minute. That is a real methodological downgrade from Haynes &
Roberts' and Takahashi's own measures, not an equivalent replication, and any
result below must be read with that in mind.

TWO MECHANISMS WERE POSED IN THE RESEARCH STAGE; ONLY ONE IS FORMALIZED
HERE: option (a) was a defensive no-new-position/flatten rule in the minutes
immediately before a release (avoid adverse selection). That is a risk
overlay, not a standalone signal -- it produces no round-trip trades of its
own to measure p/R/T from, so it cannot be run through funnel.power_gate.screen
the way this task's screening step requires. Only option (b), the
post-release momentum-continuation rule, is formalized and screened. Option
(a) is recorded as an unimplemented variant, not silently dropped: it would
need to be evaluated by its effect on OTHER strategies' fills near release
minutes (a cross-hypothesis interaction), which is out of scope for
formalizing this family's own hypotheses in isolation.

Same calendar table as H1 (identical sourcing; see that file's docstring for
the full citation of every date). Release trade_date is assumed to equal the
release's own calendar date, in both CT and ET (true for all releases here:
8:30am ET / 2:00pm ET are both well inside the session day, not near a
midnight boundary).

Parameters (ONE setting, chosen before any backtest was run):
    BASELINE_WINDOW = 60          (1 trailing hour of 1-minute bars, pre-release)
    ENTRY_WINDOW_MINUTES = 5      (Haynes & Roberts' "first minute" concentrated-
                                    discovery window, widened to 5 min for a
                                    1-minute-bar-only proxy; see mechanism above)
    RANGE_EXPANSION_THRESHOLD = 2.0  (reaction-window range vs. baseline-scaled range)
    HOLD_MINUTES = 10             (within Haynes & Roberts' 5-15 min normalization window)
    QUANTITY_MICROS = 1

SUPPORT CONDITION: measured on TRAIN folds only, from the closed-round-trip
ledger, after the modelled $2.64/RT MES cost. Support requires ALL of:
  (a) the ROBUST verdict from funnel.power_gate.screen(..., robust=True) is
      "pass" at the nearest segments_per_day grid point to the measured T;
  (b) that pass uses the MEASURED p and R, not a hand-picked grid point;
  (c) a first-fold pass is re-run across all 8 train folds and the ROBUST
      verdict does not flip to "fail" on most of them;
  (d) at least ~15 closed round trips over the sample -- with only ~9-14
      release events of each type in the whole research window and a
      selective range-expansion trigger on top, this hypothesis can easily
      be underpowered, and that must be reported as such rather than
      counted as a clean pass or fail.

REFUTE CONDITION: ANY of the following is sufficient to refute, at the
modelled cost:
  (a) the ROBUST verdict is "fail" or "marginal";
  (b) net P&L over the closed round trips is <= $0 after cost;
  (c) the MATCHED verdict passes but the ROBUST verdict does not;
  (d) fewer than ~10 closed round trips (too few to say anything; report as
      underpowered, not as a clean refutation).
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import UTC

from rules.xfa_rules import OrderIntent, Refusal
from strategy.interface import AccountView, Bar, market_intent
from strategy.research.e_calendar_event.h1_scheduled_macro_drift import RELEASE_TABLE_ET

BASELINE_WINDOW = 60
ENTRY_WINDOW_MINUTES = 5
RANGE_EXPANSION_THRESHOLD = 2.0
HOLD_MINUTES = 10
QUANTITY_MICROS = 1
_EPS = 1e-9


@dataclass(frozen=True)
class H2PostReleaseMomentum:
    """Range-expansion-triggered momentum continuation after a known macro release."""

    name: str = "h2_post_release_momentum"
    baseline_window: int = BASELINE_WINDOW
    entry_window_minutes: int = ENTRY_WINDOW_MINUTES
    range_expansion_threshold: float = RANGE_EXPANSION_THRESHOLD
    hold_minutes: int = HOLD_MINUTES
    quantity_micros: int = QUANTITY_MICROS
    _ranges: deque[float] = field(default_factory=deque)
    _current_trade_date: list[object] = field(default_factory=lambda: [None])
    _consumed_release_date: list[object] = field(default_factory=lambda: [None])
    # watch state: [baseline_mean_range_or_None, anchor_price, watch_bars_elapsed,
    #               watch_high, watch_low]
    _watch: list[object] = field(default_factory=lambda: [None, None, 0, None, None])
    _hold_bars_elapsed: list[int] = field(default_factory=lambda: [-1])

    def __post_init__(self) -> None:
        if self.baseline_window < 2:
            raise ValueError(f"baseline_window {self.baseline_window!r} must be >= 2")
        if self.entry_window_minutes < 1:
            raise ValueError(f"entry_window_minutes {self.entry_window_minutes!r} must be >= 1")
        if self.range_expansion_threshold <= 1.0:
            raise ValueError(
                f"range_expansion_threshold {self.range_expansion_threshold!r} must be > 1"
            )
        if self.hold_minutes < 1:
            raise ValueError(f"hold_minutes {self.hold_minutes!r} must be >= 1")
        if isinstance(self.quantity_micros, bool) or not isinstance(self.quantity_micros, int) \
                or self.quantity_micros <= 0:
            raise ValueError(f"quantity_micros {self.quantity_micros!r} must be a positive int")
        object.__setattr__(self, "_ranges", deque(maxlen=self.baseline_window))

    def _reset_on_new_session(self, bar: Bar) -> None:
        if self._current_trade_date[0] != bar.trade_date:
            self._current_trade_date[0] = bar.trade_date
            self._ranges.clear()
            self._consumed_release_date[0] = None
            self._watch[:] = [None, None, 0, None, None]
            self._hold_bars_elapsed[0] = -1

    def on_bar(self, bar: Bar, account: AccountView) -> tuple[OrderIntent | Refusal, ...]:
        self._reset_on_new_session(bar)
        bar_range = bar.high - bar.low

        # --- exit path: hold-timer expiry closes any open position first. ---
        if account.position_micros != 0 and self._hold_bars_elapsed[0] >= 0:
            self._hold_bars_elapsed[0] += 1
            if self._hold_bars_elapsed[0] >= self.hold_minutes:
                side = "sell" if account.position_micros > 0 else "buy"
                self._hold_bars_elapsed[0] = -1
                self._ranges.append(bar_range)
                return (market_intent(bar, side, abs(account.position_micros)),)

        release_et = RELEASE_TABLE_ET.get(bar.trade_date)
        flat = account.position_micros == 0 and account.pending_signed_micros == 0
        already_consumed = self._consumed_release_date[0] == bar.trade_date
        is_release_window = (
            release_et is not None and not already_consumed
            and bar.decision_ts_utc >= release_et.astimezone(UTC)
        )

        intents: tuple[OrderIntent | Refusal, ...] = ()
        if is_release_window and flat:
            if self._watch[1] is None:  # start the reaction watch on the first post-release bar
                baseline_mean = sum(self._ranges) / len(self._ranges) if self._ranges else None
                self._watch[:] = [baseline_mean, bar.close, 1, bar.high, bar.low]
            else:
                self._watch[2] += 1
                self._watch[3] = max(self._watch[3], bar.high)
                self._watch[4] = min(self._watch[4], bar.low)

            baseline_mean, anchor_price, elapsed, watch_high, watch_low = self._watch
            if elapsed >= self.entry_window_minutes:
                self._consumed_release_date[0] = bar.trade_date
                reaction_range = watch_high - watch_low
                threshold = (
                    baseline_mean * self.entry_window_minutes * self.range_expansion_threshold
                    if baseline_mean and baseline_mean > _EPS else None
                )
                net_return = bar.close - anchor_price
                if threshold is not None and reaction_range > threshold and net_return != 0:
                    side = "buy" if net_return > 0 else "sell"
                    intents = (market_intent(bar, side, self.quantity_micros),)
                    self._hold_bars_elapsed[0] = 0
                self._watch[:] = [None, None, 0, None, None]

        self._ranges.append(bar_range)
        return intents
