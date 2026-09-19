"""H4 -- Passive-fill magnitude-conditioned reversal (Stage D.1b, trial #24).

PRE-REGISTRATION (written before this strategy was ever run on any fold).

Mechanism and source lineage: this is H1's signal (Safari & Schmidhuber 2025,
arXiv:2501.16772: fade a short-horizon return only when its magnitude sits in
a small-to-moderate band of its own trailing distribution -- large trending
moves are deliberately NOT faded), re-specified with resting/limit-style
fills instead of aggressive market-order fades, per Stage D.1 family C item
C7 (Robert Carver, qoppac.blogspot.com, "Very... slow... mean reversion...":
"There is no possibility that you would be able to overcome trading costs
unless you were passively filled, with all that implies"). The logged D.1
mechanism (``h4_passive_fill_wrapper.py``) named "any of H1-H3, but specified
from the start to require resting/limit-style fills"; the lead has chosen H1
because it is the variant whose source paper Carver's post directly cites.
Stage D.1a added a passive-order capability (``limit_intent``,
``strategy.interface`` version 2) that did not exist when H4 was logged, so
this is now implementable without touching the harness.

This is ONE pre-chosen parameter setting -- no grid, no tuning. The signal
parameters (N_MINUTES, K_MINUTES, MAGNITUDE_WINDOW, BAND_LOW, BAND_HIGH) are
copied unchanged from H1. The only new choices are the fill mechanics below,
and those were fixed before any backtest: the entry is passive (a limit left
at the nearest non-marketable price to the signal bar's close), and the exit
is ALSO passive first, with a market fallback only if the passive exit
expires unfilled. The lead chose passive-first-then-market-fallback so that
the whole round turn is passive where possible -- Carver's claim is about
what "overcomes trading costs," which requires BOTH legs to avoid paying the
spread when the harness makes that avoidable, not just the entry.

Mechanics, exactly as specified (differences from H1 are 1-4; the signal
itself, 5-6, is identical to H1):

1. ENTRY is passive. When flat (position 0 AND pending 0) and the signal
   fires, submit a limit order to open, priced at the nearest non-marketable
   tick to the signal bar's close: close + 1 tick for a sell (fading a
   positive return), close - 1 tick for a buy (fading a negative return). A
   limit AT the close is marketable and refused by the engine, so this is
   the closest resting price to "at the signal bar's close" that the engine
   will accept. ttl_bars = ENTRY_TTL_BARS = 5 (= K_MINUTES: if the fade is
   not filled within the horizon it was conditioned on, the signal has
   lapsed). While the entry order rests (pending != 0, position 0), the
   strategy does nothing -- no new order is stacked.
2. HOLD. Once filled (position != 0), the strategy counts bars from the
   first bar at which it observes the position open. After K_MINUTES = 5
   such bars, it begins the exit.
3. EXIT is passive first, then a market fallback. At the exit decision, the
   strategy submits a limit order to flatten the full position, priced at
   close + 1 tick (selling a long) or close - 1 tick (covering a short),
   ttl_bars = EXIT_TTL_BARS = 5. If that passive exit expires unfilled (the
   strategy observes position still open and pending back at 0, having
   already placed the passive exit), it submits a market order to flatten
   immediately. The strategy never stacks a second order while one is
   pending.
4. The engine's forced flatten, session change, and MLL/roll-blackout
   machinery can close the position or cancel a resting order outside the
   strategy's control. Arriving on a new trade date always resets every
   rolling buffer and counter, exactly as H1 does, since an overnight gap is
   not a same-regime return and no held trade can have crossed the session
   boundary. Because a ``limit_intent`` call can come back as a ``Refusal``
   (e.g. if a structural window blocks the intent), the strategy passes any
   ``Refusal`` straight through, the same as H1 does for ``market_intent``,
   and derives its state (whether an order is resting, whether a position is
   open) from ``AccountView`` on the NEXT bar rather than from an assumption
   that its own order was accepted. The one piece of information
   ``AccountView`` cannot supply is "has a passive exit already been tried
   and lapsed" versus "the exit point was just reached" -- both look like
   position open, pending 0 -- so that one bit is tracked internally and
   reset whenever the position returns to flat.
5. Same signal as H1: at every bar close, the trailing N_MINUTES return
   r_t = close[t] / close[t - N_MINUTES] - 1, ranked as a percentile against
   the last MAGNITUDE_WINDOW absolute returns (rolling, per-trade-date reset,
   half-window warm-up before any signal can fire). If the percentile lands
   in [BAND_LOW, BAND_HIGH], fade: sell after a positive return, buy after a
   negative one. Quantity 1 micro.
6. Parameters (identical to H1, one setting, no grid):
       N_MINUTES = 5            (paper's horizon range is ~2-30 minutes)
       K_MINUTES = 5             (symmetric with the fade horizon)
       MAGNITUDE_WINDOW = 120   (2 trailing hours of 1-minute bars)
       BAND_LOW, BAND_HIGH = 0.20, 0.60
       ENTRY_TTL_BARS = EXIT_TTL_BARS = 5

SUPPORT CONDITION: measured on TRAIN folds only, from the closed round-trip
ledger the shared screening runner produces. Support requires the composite
``screen_candidate`` verdict to be "pass" on fold 0's train window -- i.e.
BOTH: the robust zero-edge null (``funnel.power_gate.screen(..., robust=
True)`` on the measured p/R/T) passes, AND the drift benchmark passes (its
daily excess over its own unconditional, exposure-matched counterpart is
significant at one-sided 95%, and its drift-adjusted p/R still clears the
robust gate) -- with at least one passive fill recorded (``passive_fills >
0``, confirming the passive path was actually exercised and not silently
reduced to an all-market-fallback strategy), at least 30 closed round trips,
and the realized position sign matching the fade direction (net short after
up-moves, net long after down-moves, within the qualifying band). A pass on
fold 0 train alone is not itself sufficient: the task calls for re-running
any fold-0 pass across all 8 train folds and checking that the composite
verdict does not swing from pass to fail across folds on the same
parameterisation (i.e. the result is not dominated by one or two folds). That
re-run is the lead's decision, not this session's -- this session screens
fold 0 only.

REFUTE CONDITION: any ONE of the following is sufficient to refute, at the
modelled cost:
  (a) the composite ``verdict`` is "fail";
  (b) net P&L over the closed round trips is <= $0 after cost;
  (c) net P&L per closed trip is not better than C-H1's market-fill figure
      measured on the SAME window -- fold 0: C-H1 made -$55,495 over 19,893
      trips, -$2.79/trip. This specific comparison is the one that refutes
      Carver's claim as applied here: if passive fills do not improve on the
      market-fill per-trip economics on the identical window, passive fills
      are not what rescues this reversal, regardless of what the gate says
      in isolation.
Fewer than 30 closed round trips is UNDERPOWERED, not refuted, and must be
reported as such rather than folded into a pass/fail count.

CAVEATS (plain words, carried on the report regardless of the composite
verdict, whenever any passive fill occurs -- ``screening.runner`` attaches
these automatically from ``sim.fill_model.PASSIVE_FILL_CAVEATS``, restated
here because a write-up of this result must say them, not point at a
runner):
  - Fills use a TRADE-THROUGH rule on 1-minute OHLC bars: a resting limit
    fills only when a later bar's price trades AT LEAST ONE TICK THROUGH the
    limit, and then at exactly the limit price -- never a merely-touched
    level.
  - Queue position is NOT modelled. Trade-through instead assumes a price
    level is exhausted before the market trades through it; hidden, implied
    or cancelled liquidity ahead of this order in the queue could break that
    assumption. Dropping every touch-only fill this way biases results
    PESSIMISTICALLY (touch-and-bounce fills are disproportionately the ones
    that would have won), which is the direction a screen should err on, but
    it is still not a queue simulation.
  - The order's own market impact is NOT modelled: the historical path is
    replayed as if the resting order had never been there.
  - Volume available at the limit price is NOT checked: any qualifying
    trade-through fills the full order size, regardless of how much actually
    traded at that level.
  - Latency is NOT modelled: an order is assumed to rest from the instant of
    its decision.
  - No separate adverse-selection penalty is added on top of the
    trade-through rule. The trade-through rule IS the adverse-selection
    model (the fills it keeps are exactly the ones where price went through
    the level against the position), and the real subsequent bars already
    carry whatever happens after the fill; a flat penalty on top would
    double-count it. Combined with the touch-only drop above, the net bias
    is pessimistic.
  - The market-fallback exit (when a passive exit expires) still prices
    against the SAME two-day slippage calibration used everywhere else in
    this project, which is itself a lower bound on cost (rests on two days
    of book data, excludes latency, adverse selection and queue position,
    and the $1.22/round-turn commission still needs Topstep checkout
    confirmation).
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from rules.xfa_rules import MES_TICK_SIZE, OrderIntent, Refusal
from strategy.interface import AccountView, Bar, PassiveIntent, limit_intent, market_intent
from strategy.research.c_short_horizon_reversal.h1_magnitude_conditioned_reversal import (
    BAND_HIGH,
    BAND_LOW,
    K_MINUTES,
    MAGNITUDE_WINDOW,
    N_MINUTES,
    QUANTITY_MICROS,
    _percentile_rank,
)

ENTRY_TTL_BARS = K_MINUTES  # 5: unfilled beyond the fade horizon means the signal has lapsed
EXIT_TTL_BARS = K_MINUTES  # 5: same horizon for the resting exit


def _fade_limit_price(close: float, side: str) -> float:
    """The nearest non-marketable tick to ``close`` on ``side``.

    A sell must rest strictly above the close (close + 1 tick); a buy must rest
    strictly below it (close - 1 tick). Rounded through integer ticks so float
    arithmetic on 0.25 increments cannot drift off the MES grid.
    """
    close_ticks = round(close / MES_TICK_SIZE)
    ticks = close_ticks + 1 if side == "sell" else close_ticks - 1
    return round(ticks * MES_TICK_SIZE, 2)


@dataclass(frozen=True)
class H4PassiveFillReversal:
    """H1's magnitude-conditioned reversal, entered and exited with resting limit orders."""

    name: str = "h4_passive_fill_reversal"
    n_minutes: int = N_MINUTES
    k_minutes: int = K_MINUTES
    magnitude_window: int = MAGNITUDE_WINDOW
    band_low: float = BAND_LOW
    band_high: float = BAND_HIGH
    quantity_micros: int = QUANTITY_MICROS
    entry_ttl_bars: int = ENTRY_TTL_BARS
    exit_ttl_bars: int = EXIT_TTL_BARS
    # Mutable working state held behind frozen fields, mutated in place only -- the
    # same pattern H1 uses. Sized in __post_init__ from the INSTANCE's own
    # parameters, not the module defaults.
    _closes: deque[float] = field(default_factory=deque)
    _abs_returns: deque[float] = field(default_factory=deque)
    _bars_since_fill: list[int] = field(default_factory=lambda: [-1])  # -1: not holding
    _exit_attempted: list[bool] = field(default_factory=lambda: [False])
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
        if isinstance(self.entry_ttl_bars, bool) or not isinstance(self.entry_ttl_bars, int) \
                or self.entry_ttl_bars <= 0:
            raise ValueError(f"entry_ttl_bars {self.entry_ttl_bars!r} must be a positive int")
        if isinstance(self.exit_ttl_bars, bool) or not isinstance(self.exit_ttl_bars, int) \
                or self.exit_ttl_bars <= 0:
            raise ValueError(f"exit_ttl_bars {self.exit_ttl_bars!r} must be a positive int")
        object.__setattr__(self, "_closes", deque(maxlen=self.n_minutes + 1))
        object.__setattr__(self, "_abs_returns", deque(maxlen=self.magnitude_window))

    def _reset_on_new_session(self, bar: Bar) -> None:
        # A new trade date starts fresh: an overnight gap is not a same-regime return,
        # and the engine flattens any open position and cancels resting orders before
        # the session boundary, so no held trade or resting order carries across it.
        if self._current_trade_date[0] != bar.trade_date:
            self._current_trade_date[0] = bar.trade_date
            self._closes.clear()
            self._abs_returns.clear()
            self._bars_since_fill[0] = -1
            self._exit_attempted[0] = False

    def _hold_and_exit(
        self, bar: Bar, account: AccountView
    ) -> tuple[OrderIntent | PassiveIntent | Refusal, ...]:
        """Position is open. Count hold bars; once due, exit passive-first-then-market."""
        if self._bars_since_fill[0] < 0:
            self._bars_since_fill[0] = 0  # first bar this position was observed open
            self._exit_attempted[0] = False
        else:
            self._bars_since_fill[0] += 1

        if account.pending_signed_micros != 0:
            return ()  # an exit order is already resting: never stack a second one

        if self._bars_since_fill[0] < self.k_minutes:
            return ()  # still inside the hold window

        side = "sell" if account.position_micros > 0 else "buy"
        qty = abs(account.position_micros)
        if not self._exit_attempted[0]:
            self._exit_attempted[0] = True
            price = _fade_limit_price(bar.close, side)
            return (limit_intent(bar, side, qty, price, self.exit_ttl_bars),)
        # The passive exit was already tried and is no longer resting (expired, or was
        # refused outright): fall back to an immediate market flatten.
        return (market_intent(bar, side, qty),)

    def _try_entry(self, bar: Bar) -> tuple[OrderIntent | PassiveIntent | Refusal, ...]:
        if len(self._closes) <= self.n_minutes:
            return ()

        oldest = self._closes[0]
        ret = bar.close / oldest - 1.0
        abs_ret = abs(ret)
        intents: tuple[OrderIntent | PassiveIntent | Refusal, ...] = ()

        if len(self._abs_returns) >= self.magnitude_window // 2:
            percentile = _percentile_rank(self._abs_returns, abs_ret)
            if self.band_low <= percentile <= self.band_high and ret != 0.0:
                side = "sell" if ret > 0 else "buy"
                price = _fade_limit_price(bar.close, side)
                intents = (limit_intent(bar, side, self.quantity_micros, price,
                                        self.entry_ttl_bars),)

        self._abs_returns.append(abs_ret)
        return intents

    def on_bar(
        self, bar: Bar, account: AccountView
    ) -> tuple[OrderIntent | PassiveIntent | Refusal, ...]:
        self._reset_on_new_session(bar)
        self._closes.append(bar.close)

        if account.position_micros != 0:
            return self._hold_and_exit(bar, account)

        # Flat of filled position. Reset hold-tracking so a future fill starts clean.
        self._bars_since_fill[0] = -1
        self._exit_attempted[0] = False

        if account.pending_signed_micros != 0:
            return ()  # an entry order is already resting: never stack a second one

        return self._try_entry(bar)
