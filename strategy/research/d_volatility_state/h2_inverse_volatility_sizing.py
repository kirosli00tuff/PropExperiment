"""H2 -- Inverse-volatility position sizing, cost-aware (vol targeting).

PRE-REGISTRATION (written before this strategy was ever run on any fold).

Mechanism: scale trade SIZE (not entry/exit timing) inversely to a trailing
realized-volatility estimate, so each trade targets roughly constant dollar
risk rather than a constant contract count. Carver (qoppac.blogspot.com,
2018, verified full text) reports dynamic vol targeting lifting Sharpe from
0.569 (static) to 0.92 across 37 futures markets -- a 37% improvement from
sizing alone, no entry-signal change. Separately, Fett & Haynes (CFTC OCE
2017, verified full text, E-mini-specific) find order-book depth and average
trade size shrink specifically during high-volatility periods in E-mini
markets. Those two verified findings point the same direction for an
inverse-vol sizing rule: smaller size when trailing vol is high should (a)
reduce dollar risk per trade when risk is highest, AND (b) reduce size
exactly when the CFTC finding says the book is thinnest and costs are
worst -- so the rule may help for both reasons, or the second effect may be
small/absent once real modelled cost is applied. This hypothesis does NOT
assume the risk-parity win is real; it is tested against
``sim/fill_model.py`` like everything else in this program, per the
project's cost-discipline prior (ORBExperiment: measured slippage ran
11.27x the assumed model on a sibling project).

Base entry (deliberately unoptimized scaffolding, NOT this family's
contribution, and deliberately UNGATED by regime -- unlike H1, so sizing is
the only mechanism under test, isolated from H1's filter): go long at a
fixed bar offset ENTRY_BAR_OFFSET from each trade date's first bar in the
on-disk series, every trade date (no filter), hold HOLD_MINUTES bars, then
flatten unconditionally.

Sizing rule: an EWMA variance of 1-minute bar-over-bar log returns (same
RiskMetrics lambda = 0.94 as H1, not fit on this data) gives a trailing
volatility estimate V (updated causally, bar by bar -- unlike H1 this is a
continuously-updated estimate, not a once-per-day snapshot, because sizing
a specific trade should use the most recent information available at that
decision, not yesterday's close-of-day value). At the entry bar:
  expected_move_price = bar.close * V * sqrt(HOLD_MINUTES)      # random-walk scaling
  expected_move_ticks = expected_move_price / MES_TICK_SIZE
  risk_usd_per_contract = expected_move_ticks * MES_TICK_VALUE_USD
  quantity_micros = round(TARGET_RISK_USD / risk_usd_per_contract),
                     clipped to [MIN_QUANTITY_MICROS, MAX_QUANTITY_MICROS]
TARGET_RISK_USD = 75.0, chosen ex ante as roughly 28x the modelled $2.64/RT
MES cost floor -- large enough that the target is not swamped by cost noise,
small enough to stay far under the XFA base position cap (20 micros) even
at the smallest plausible V. One parameterization only; see constants below.
During WARMUP_BARS at the very start of the series the EWMA has not
stabilized, so the strategy does not trade.

SUPPORT CONDITION: measured on TRAIN folds only, from the closed-round-trip
ledger, after the modelled cost. Support requires ALL of:
  (a) the ROBUST verdict from funnel.power_gate.screen(..., robust=True) is
      "pass" at the nearest available segments_per_day grid point;
  (b) p and R are the MEASURED ledger figures (dollars per trip, which now
      vary trade to trade because quantity varies -- R is still mean win $
      / mean loss $ over the trip P&L series, exactly as for a fixed-size
      strategy);
  (c) at least ~30 closed round trips over the sample;
  (d) a first-fold pass is confirmed across ALL 8 train folds with a spread
      report;
  (e) measured average quantity_micros is visibly LOWER on days the H1
      module (same package) would classify high-vol than on days it would
      classify low-vol -- i.e., the sizing rule is actually behaving
      inversely to vol on this data, not accidentally flat or inverted by
      an implementation bug.

REFUTE CONDITION: ANY of the following is sufficient to refute, at modelled
cost:
  (a) the ROBUST verdict is "fail" or "marginal";
  (b) net P&L over the closed round trips is <= $0 after cost;
  (c) the MATCHED verdict passes but the ROBUST verdict does not;
  (d) fewer than ~30 closed round trips over the train fold -- UNDERPOWERED,
      reported as such rather than folded into a pass/fail count;
  (e) condition (e) above fails (sizing is flat or inverted relative to
      trailing vol) -- in that case any pass/fail verdict is not evidence
      about vol-targeting at all, only about the fixed base entry, and must
      be reported as an implementation problem, not a result.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from rules.xfa_rules import MES_TICK_SIZE, OrderIntent, Refusal
from strategy.interface import AccountView, Bar, market_intent

MES_TICK_VALUE_USD = 1.25
EWMA_LAMBDA = 0.94  # RiskMetrics standard decay, not fit on this data
ENTRY_BAR_OFFSET = 60  # bars after this trade date's first bar in the series
HOLD_MINUTES = 30
TARGET_RISK_USD = 75.0
MIN_QUANTITY_MICROS = 1
MAX_QUANTITY_MICROS = 5
WARMUP_BARS = 200


@dataclass(frozen=True)
class H2InverseVolatilitySizing:
    """Fixed-offset long, every day, sized inversely to a continuously-updated EWMA vol."""

    name: str = "h2_inverse_volatility_sizing"
    ewma_lambda: float = EWMA_LAMBDA
    entry_bar_offset: int = ENTRY_BAR_OFFSET
    hold_minutes: int = HOLD_MINUTES
    target_risk_usd: float = TARGET_RISK_USD
    min_quantity_micros: int = MIN_QUANTITY_MICROS
    max_quantity_micros: int = MAX_QUANTITY_MICROS
    warmup_bars: int = WARMUP_BARS
    # Mutable working state behind frozen fields; see sibling H1 for the pattern.
    _ewma_var: list[float] = field(default_factory=lambda: [0.0])
    _last_close: list[float | None] = field(default_factory=lambda: [None])
    _bars_seen: list[int] = field(default_factory=lambda: [0])
    _current_trade_date: list[object] = field(default_factory=lambda: [None])
    _bar_index_today: list[int] = field(default_factory=lambda: [-1])
    _bars_since_entry: list[int] = field(default_factory=lambda: [-1])
    _sized_quantities: list[int] = field(default_factory=list)  # for reporting/inspection only

    def __post_init__(self) -> None:
        if not (0.0 < self.ewma_lambda < 1.0):
            raise ValueError(f"ewma_lambda {self.ewma_lambda!r} must be in (0, 1)")
        if self.entry_bar_offset < 0:
            raise ValueError(f"entry_bar_offset {self.entry_bar_offset!r} must be >= 0")
        if self.hold_minutes < 1:
            raise ValueError(f"hold_minutes {self.hold_minutes!r} must be >= 1")
        if self.target_risk_usd <= 0.0:
            raise ValueError(f"target_risk_usd {self.target_risk_usd!r} must be positive")
        if self.min_quantity_micros < 1:
            raise ValueError(
                f"min_quantity_micros {self.min_quantity_micros!r} must be >= 1"
            )
        if self.max_quantity_micros < self.min_quantity_micros:
            raise ValueError("max_quantity_micros must be >= min_quantity_micros")
        if self.warmup_bars < 1:
            raise ValueError(f"warmup_bars {self.warmup_bars!r} must be >= 1")

    def _update_ewma(self, bar: Bar) -> None:
        prev = self._last_close[0]
        if prev is not None and prev > 0.0:
            ret = math.log(bar.close / prev)
            self._ewma_var[0] = (
                self.ewma_lambda * self._ewma_var[0] + (1.0 - self.ewma_lambda) * ret * ret
            )
        self._last_close[0] = bar.close
        self._bars_seen[0] += 1

    def _sized_quantity(self, bar: Bar) -> int:
        vol = math.sqrt(max(self._ewma_var[0], 0.0))
        if vol <= 0.0:
            return self.max_quantity_micros
        expected_move_price = bar.close * vol * math.sqrt(self.hold_minutes)
        expected_move_ticks = expected_move_price / MES_TICK_SIZE
        risk_usd_per_contract = expected_move_ticks * MES_TICK_VALUE_USD
        if risk_usd_per_contract <= 0.0:
            return self.max_quantity_micros
        raw = round(self.target_risk_usd / risk_usd_per_contract)
        return max(self.min_quantity_micros, min(self.max_quantity_micros, raw))

    def on_bar(self, bar: Bar, account: AccountView) -> tuple[OrderIntent | Refusal, ...]:
        if self._current_trade_date[0] != bar.trade_date:
            self._current_trade_date[0] = bar.trade_date
            self._bar_index_today[0] = -1
            self._bars_since_entry[0] = -1
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
        ready = self._bars_seen[0] >= self.warmup_bars
        if flat and ready and self._bar_index_today[0] == self.entry_bar_offset:
            qty = self._sized_quantity(bar)
            self._sized_quantities.append(qty)
            intents = (market_intent(bar, "buy", qty),)
            self._bars_since_entry[0] = 0

        self._update_ewma(bar)
        return intents
