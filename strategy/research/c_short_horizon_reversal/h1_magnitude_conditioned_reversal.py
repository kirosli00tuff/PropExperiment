"""H1 -- Magnitude-conditioned minute-scale reversal (non-monotonic fade).

PRE-REGISTRATION (written before this strategy was ever run on any fold).

Mechanism: fade an n-minute MES return, but ONLY when its absolute magnitude
sits in a small-to-moderate band of its own recent (trailing) distribution.
Large moves are deliberately NOT faded, because Safari & Schmidhuber (2025,
arXiv:2501.16772) report reversion strongest for weak trend strength and
weakening (or flipping toward persistence) as trend strength grows -- a
non-monotonic relationship, not a blanket "fade every move" rule. Concretely:

1. At every bar close, compute the trailing N_MINUTES return
   r_t = close[t] / close[t - N_MINUTES] - 1.
2. Maintain a rolling window of the last MAGNITUDE_WINDOW absolute returns
   and rank the current |r_t| against it (a percentile in [0, 1]).
3. If flat (no open position, no pending order) and the percentile lands in
   [BAND_LOW, BAND_HIGH] (small-to-moderate; excludes near-zero noise below
   BAND_LOW and large trending moves above BAND_HIGH), enter opposite the
   sign of r_t: sell after a positive return, buy after a negative one.
4. Hold exactly K_MINUTES bars, then exit unconditionally (flat market exit).
   The engine's forced-flatten / MLL / roll-blackout machinery can also close
   the position early; that is not a strategy decision.

Parameters (ONE setting, chosen from the source paper's stated horizon range
before any backtest was run -- this is the only combination tested in Stage
D.1; extending the grid is future work and must be counted in the
multiple-comparisons accounting if it happens):
    N_MINUTES = 5           (paper's horizon range is ~2-30 minutes)
    K_MINUTES = 5            (symmetric with the fade horizon)
    MAGNITUDE_WINDOW = 120  (2 trailing hours of 1-minute bars)
    BAND_LOW, BAND_HIGH = 0.20, 0.60  (small-to-moderate magnitude band)

SUPPORT CONDITION: measured on TRAIN folds only, from the closed-round-trip
ledger, after the modelled $2.64/RT MES cost. Support requires ALL of:
  (a) the ROBUST verdict from funnel.power_gate.screen(..., robust=True) is
      "pass" (not "marginal", not "fail") at the nearest available
      segments_per_day grid point to the measured trades/day T;
  (b) the realized win probability p and win/loss ratio R that produced that
      pass are the MEASURED figures from the ledger, not a hand-picked grid
      point;
  (c) the sign of the edge matches the mechanism (the strategy is net short
      after up-moves and net long after down-moves within the qualifying
      band -- i.e. it is actually fading, not accidentally profiting from a
      momentum leak in the fill/cost model).
A pass on ONE fold is not itself sufficient to "support" the hypothesis for
Stage D.1's purposes -- the task calls for re-running any first-fold pass
across all 8 train folds and reporting the per-fold spread. Genuine support
additionally requires that spread to not be dominated by one or two lucky
folds (i.e. the ROBUST verdict should not swing from pass to fail across
folds on materially the same parameterisation).

REFUTE CONDITION: ANY of the following is sufficient to refute, at the
modelled cost:
  (a) the ROBUST verdict is "fail" or "marginal";
  (b) net P&L over the closed round trips is <= $0 after cost;
  (c) the MATCHED verdict passes but the ROBUST verdict does not -- i.e. the
      apparent edge is explained by size/activity against a favorable null,
      not a real signal (this is exactly the failure mode the robust column
      exists to catch, per funnel/power_gate.py);
  (d) trades per day is too low for the measured p/R to be a meaningfully
      estimated quantity (fewer than ~30 closed round trips over the sample)
      -- in that case the result is UNDERPOWERED, not a genuine refutation,
      and must be reported as such rather than folded into a pass/fail count.
The source paper itself is explicit that this effect is "difficult to
profitably exploit... in the face of trading costs"; the prior going in is
that (d)/(b)/(c) are more likely than a clean pass.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from rules.xfa_rules import OrderIntent, Refusal
from strategy.interface import AccountView, Bar, market_intent

N_MINUTES = 5
K_MINUTES = 5
MAGNITUDE_WINDOW = 120
BAND_LOW = 0.20
BAND_HIGH = 0.60
QUANTITY_MICROS = 1


def _percentile_rank(window: deque[float], value: float) -> float:
    """Fraction of ``window`` strictly below ``value`` (ties count half)."""
    if not window:
        return 0.0
    below = sum(1 for x in window if x < value)
    equal = sum(1 for x in window if x == value)
    return (below + 0.5 * equal) / len(window)


@dataclass(frozen=True)
class H1MagnitudeConditionedReversal:
    """Fade a 5-minute return only when its |magnitude| is small-to-moderate."""

    name: str = "h1_magnitude_conditioned_reversal"
    n_minutes: int = N_MINUTES
    k_minutes: int = K_MINUTES
    magnitude_window: int = MAGNITUDE_WINDOW
    band_low: float = BAND_LOW
    band_high: float = BAND_HIGH
    quantity_micros: int = QUANTITY_MICROS
    # Mutable working state held behind frozen fields (never reassigned, only
    # mutated in place -- the same pattern the engine itself uses for
    # deque/list-backed rolling buffers). Sized in __post_init__ from the
    # INSTANCE's own parameters, not the module defaults, so a differently
    # parameterised instance never inherits another instance's window sizes.
    _closes: deque[float] = field(default_factory=deque)
    _abs_returns: deque[float] = field(default_factory=deque)
    _bars_since_entry: list[int] = field(default_factory=lambda: [-1])
    _current_trade_date: list[object] = field(default_factory=lambda: [None])

    def __post_init__(self) -> None:
        if self.n_minutes < 1:
            raise ValueError(f"n_minutes {self.n_minutes!r} must be >= 1")
        if self.k_minutes < 1:
            raise ValueError(f"k_minutes {self.k_minutes!r} must be >= 1")
        if self.magnitude_window < self.n_minutes:
            raise ValueError("magnitude_window must be >= n_minutes")
        if not (0.0 <= self.band_low < self.band_high <= 1.0):
            raise ValueError(f"band [{self.band_low}, {self.band_high}] is not a valid range")
        if isinstance(self.quantity_micros, bool) or not isinstance(self.quantity_micros, int) \
                or self.quantity_micros <= 0:
            raise ValueError(f"quantity_micros {self.quantity_micros!r} must be a positive int")
        object.__setattr__(self, "_closes", deque(maxlen=self.n_minutes + 1))
        object.__setattr__(self, "_abs_returns", deque(maxlen=self.magnitude_window))

    def _reset_on_new_session(self, bar: Bar) -> None:
        # A new trade date starts a fresh rolling window: an overnight gap is not a
        # same-regime 5-minute return, and the engine already flattens any open
        # position before the session boundary, so no held trade crosses this reset.
        if self._current_trade_date[0] != bar.trade_date:
            self._current_trade_date[0] = bar.trade_date
            self._closes.clear()
            self._abs_returns.clear()
            self._bars_since_entry[0] = -1

    def on_bar(self, bar: Bar, account: AccountView) -> tuple[OrderIntent | Refusal, ...]:
        self._reset_on_new_session(bar)
        self._closes.append(bar.close)

        flat = account.position_micros == 0 and account.pending_signed_micros == 0
        intents: tuple[OrderIntent | Refusal, ...] = ()

        # Exit path: count bars since a strategy entry and flatten after k_minutes.
        if account.position_micros != 0 and self._bars_since_entry[0] >= 0:
            self._bars_since_entry[0] += 1
            if self._bars_since_entry[0] >= self.k_minutes:
                side = "sell" if account.position_micros > 0 else "buy"
                intents = (market_intent(bar, side, abs(account.position_micros)),)
                self._bars_since_entry[0] = -1
                return intents

        if not flat:
            return intents

        if len(self._closes) <= self.n_minutes:
            return intents

        oldest = self._closes[0]
        ret = bar.close / oldest - 1.0
        abs_ret = abs(ret)

        if len(self._abs_returns) >= self.magnitude_window // 2:
            percentile = _percentile_rank(self._abs_returns, abs_ret)
            if self.band_low <= percentile <= self.band_high and ret != 0.0:
                side = "sell" if ret > 0 else "buy"
                intents = (market_intent(bar, side, self.quantity_micros),)
                self._bars_since_entry[0] = 0

        self._abs_returns.append(abs_ret)
        return intents
