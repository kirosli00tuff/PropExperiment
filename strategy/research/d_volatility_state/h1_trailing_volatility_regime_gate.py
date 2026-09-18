"""H1 -- Trailing realized-volatility regime as an entry filter (vol-clustering /
long-memory gate).

PRE-REGISTRATION (written before this strategy was ever run on any fold).

Mechanism: realized volatility in equity-index futures is strongly persistent
(long memory) -- a high- or low-vol state today predicts a similar state
tomorrow more than a random walk would (Andersen, Bondarenko, Kyle & Obizhaeva
2018, verified full text; the specific lag-1 RV autocorrelation figure from
Brown 2026 SSRN 6847024 is [unverified], not relied on for any number here).
This module computes a trailing, purely causal realized-volatility estimate
directly from the on-disk MES 1-minute bars, buckets each trade date into a
rolling tercile of that estimate's own trailing history, and gates a
deliberately simple, NON-OWNED base entry (a fixed bar-offset long, held a
fixed number of minutes, then flattened -- no breakout/reversal logic; that is
family A/B/C's territory) so it only fires when today is classified into the
LOW-vol tercile.

Why LOW vol, chosen ex ante and not by peeking at results: the base entry
below carries no directional edge of its own (it is an unconditional long at
a fixed clock offset), so its realized win/loss ratio is driven almost
entirely by how much the position whips around during the hold window. A
low-vol trailing regime should shrink the SIZE of adverse excursions (the
denominator of R) relative to a high-vol regime, without an obvious reason to
also shrink win size by the same amount -- so R should rise in the low-vol
bucket even though p is not expected to move much off ~0.5. This is the
regime this hypothesis is staked on before any backtest is run; a result
where the HIGH-vol tercile does better and LOW does not is a refutation of
the mechanism as stated here, not grounds to silently retarget the bucket.

State construction (fully causal, zero look-ahead):
1. An EWMA variance of consecutive 1-minute bar-over-bar log returns is
   updated on every bar, RiskMetrics-style (lambda = 0.94, a fixed, widely
   used constant -- not fit on this data).
2. At the FIRST bar of every new trade date (a ``bar.trade_date`` change),
   BEFORE that date's own bars have touched the EWMA, its current value is
   snapshotted as sqrt(EWMA variance) = V_d, "the trailing vol going into
   day d." V_d uses only bars strictly before day d -- it is known in full
   before day d's first decision.
3. V_d is percentile-ranked against a trailing deque of the last
   REGIME_LOOKBACK_DAYS such snapshots (days strictly before d only -- V_d
   itself is appended to the deque AFTER the percentile rank is taken, the
   same order used by the sibling family's H1 magnitude-conditioned
   reversal). Below TERCILE_LOW_MAX percentile => "low" regime.
4. Until MIN_HISTORY_DAYS prior snapshots exist, the classifier is
   undefined and the strategy does not trade (warm-up).

Base entry (deliberately unoptimized scaffolding, not this family's
contribution): on a day classified "low," go long 1 micro at bar offset
ENTRY_BAR_OFFSET counted from that trade date's first bar in the on-disk
series (this is NOT necessarily the cash-market open; trade-date sessions in
this dataset run from ~17:00 CT the prior evening), hold HOLD_MINUTES bars,
then flatten unconditionally. One parameterization only; see constants below.

SUPPORT CONDITION: measured on TRAIN folds only, from the closed-round-trip
ledger (``strategy/research/d_volatility_state/_metrics.py``), after the
modelled $2.64/RT MES cost. Support requires ALL of:
  (a) the ROBUST verdict from funnel.power_gate.screen(..., robust=True) is
      "pass" at the nearest available segments_per_day grid point to the
      measured trades/day T;
  (b) p and R are the MEASURED ledger figures, not a hand-picked grid point;
  (c) the pass is not an artifact of a handful of trades: at least ~30 closed
      round trips over the sample (see REFUTE (d));
  (d) a first-fold pass is confirmed across ALL 8 train folds with a spread
      report, not just one fold -- a verdict that swings pass/fail across
      folds on the same parameterization is NOT genuine support, it is
      instability, and must be reported as such.

REFUTE CONDITION: ANY of the following is sufficient to refute, at modelled
cost:
  (a) the ROBUST verdict is "fail" or "marginal";
  (b) net P&L over the closed round trips is <= $0 after cost;
  (c) the MATCHED verdict passes but the ROBUST verdict does not (apparent
      edge explained by size/activity against a favorable null, not signal);
  (d) fewer than ~30 closed round trips over the train fold -- UNDERPOWERED,
      reported as such rather than folded into a pass/fail count;
  (e) the HIGH-vol tercile (not tested for screening but inspectable from the
      same ledger via a second run) shows an equal or better R than LOW --
      contradicts the stated mechanism even if LOW alone screens.
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass, field

from rules.xfa_rules import OrderIntent, Refusal
from strategy.interface import AccountView, Bar, market_intent

EWMA_LAMBDA = 0.94  # RiskMetrics standard decay, not fit on this data
REGIME_LOOKBACK_DAYS = 60
MIN_HISTORY_DAYS = 30
TERCILE_LOW_MAX = 1.0 / 3.0  # bottom third of the trailing distribution
TARGET_REGIME = "low"
ENTRY_BAR_OFFSET = 60  # bars after this trade date's first bar in the series
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
class H1TrailingVolatilityRegimeGate:
    """Fixed-offset long, only on days a trailing-vol tercile classifier calls LOW."""

    name: str = "h1_trailing_volatility_regime_gate"
    ewma_lambda: float = EWMA_LAMBDA
    regime_lookback_days: int = REGIME_LOOKBACK_DAYS
    min_history_days: int = MIN_HISTORY_DAYS
    tercile_low_max: float = TERCILE_LOW_MAX
    entry_bar_offset: int = ENTRY_BAR_OFFSET
    hold_minutes: int = HOLD_MINUTES
    quantity_micros: int = QUANTITY_MICROS
    # Mutable working state behind frozen fields, sized in __post_init__ from this
    # instance's own parameters (never module defaults), mirroring the sibling
    # family's pattern for rolling-buffer strategies.
    _vol_history: deque[float] = field(default_factory=deque)
    _ewma_var: list[float] = field(default_factory=lambda: [0.0])
    _last_close: list[float | None] = field(default_factory=lambda: [None])
    _current_trade_date: list[object] = field(default_factory=lambda: [None])
    _bar_index_today: list[int] = field(default_factory=lambda: [-1])
    _today_is_low_regime: list[bool] = field(default_factory=lambda: [False])
    _bars_since_entry: list[int] = field(default_factory=lambda: [-1])

    def __post_init__(self) -> None:
        if not (0.0 < self.ewma_lambda < 1.0):
            raise ValueError(f"ewma_lambda {self.ewma_lambda!r} must be in (0, 1)")
        if self.regime_lookback_days < 2:
            raise ValueError(f"regime_lookback_days {self.regime_lookback_days!r} must be >= 2")
        if self.min_history_days < 1 or self.min_history_days > self.regime_lookback_days:
            raise ValueError(
                f"min_history_days {self.min_history_days!r} must be in "
                f"[1, regime_lookback_days]"
            )
        if not (0.0 < self.tercile_low_max < 1.0):
            raise ValueError(f"tercile_low_max {self.tercile_low_max!r} must be in (0, 1)")
        if self.entry_bar_offset < 0:
            raise ValueError(f"entry_bar_offset {self.entry_bar_offset!r} must be >= 0")
        if self.hold_minutes < 1:
            raise ValueError(f"hold_minutes {self.hold_minutes!r} must be >= 1")
        bad_quantity = (
            isinstance(self.quantity_micros, bool)
            or not isinstance(self.quantity_micros, int)
            or self.quantity_micros <= 0
        )
        if bad_quantity:
            raise ValueError(f"quantity_micros {self.quantity_micros!r} must be a positive int")
        object.__setattr__(self, "_vol_history", deque(maxlen=self.regime_lookback_days))

    def _snapshot_new_session(self, bar: Bar) -> None:
        if self._current_trade_date[0] == bar.trade_date:
            return
        self._current_trade_date[0] = bar.trade_date
        self._bar_index_today[0] = -1
        self._bars_since_entry[0] = -1
        v_today = math.sqrt(max(self._ewma_var[0], 0.0))
        if len(self._vol_history) >= self.min_history_days:
            percentile = _percentile_rank(self._vol_history, v_today)
            self._today_is_low_regime[0] = percentile <= self.tercile_low_max
        else:
            self._today_is_low_regime[0] = False
        self._vol_history.append(v_today)

    def _update_ewma(self, bar: Bar) -> None:
        prev = self._last_close[0]
        if prev is not None and prev > 0.0:
            ret = math.log(bar.close / prev)
            self._ewma_var[0] = (
                self.ewma_lambda * self._ewma_var[0] + (1.0 - self.ewma_lambda) * ret * ret
            )
        self._last_close[0] = bar.close

    def on_bar(self, bar: Bar, account: AccountView) -> tuple[OrderIntent | Refusal, ...]:
        self._snapshot_new_session(bar)
        self._bar_index_today[0] += 1
        intents: tuple[OrderIntent | Refusal, ...] = ()

        # Exit path: unconditional flatten after hold_minutes bars in the trade.
        if account.position_micros != 0 and self._bars_since_entry[0] >= 0:
            self._bars_since_entry[0] += 1
            if self._bars_since_entry[0] >= self.hold_minutes:
                side = "sell" if account.position_micros > 0 else "buy"
                intents = (market_intent(bar, side, abs(account.position_micros)),)
                self._bars_since_entry[0] = -1
                self._update_ewma(bar)
                return intents

        flat = account.position_micros == 0 and account.pending_signed_micros == 0
        if (
            flat
            and self._today_is_low_regime[0]
            and self._bar_index_today[0] == self.entry_bar_offset
        ):
            intents = (market_intent(bar, "buy", self.quantity_micros),)
            self._bars_since_entry[0] = 0

        self._update_ewma(bar)
        return intents
