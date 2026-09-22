"""Stage D.1d re-tests RT1-RT7: seven flagged trials restated at their source's horizon.

Declaration: reports/stage_d1d_timeframe_declaration.md, section 2 (sha256
07a906328a2aae2097ae30ea02e5b547cf37247245e1cd91b63808809619c745). Only the
horizon-bearing parameters change (bar size, opening-range / baseline / estimator window,
hold); sides, thresholds, tick buffers, base entries and one-entry-per-session are the
originals'. Every coarse bar comes from ``resample.CoarseBarBuilder`` (rule R6), so a
strategy acts on a 5-minute bar only at the decision time of the 1-minute bar that
completes it, and a market order then fills at the next 1-minute open.

PRE-REGISTERED for every RT (declaration section 2), before any run:
  SUPPORT: fold-0 composite verdict "pass" (robust zero-edge AND both drift sub-checks),
           >= 30 trips, traded sign consistent with the mechanism, then a pass that does
           not swing to fail on most of folds 1-7.
  REFUTE:  the composite fails on fold 0, OR fold-0 net <= $0.

Implementation choices, logged here rather than hidden:
- RT1-RT4: the opening range needs all six 08:30-09:00 CT slots present; a day with a
  missing OR slot trades nothing. An entry is taken only if at least one further RTH slot
  exists (hold >= 1 needs a next bar); if fewer than ``hold_bars`` remain, the exit fires
  on the RTH segment's last slot, which is what "exiting earlier only if the RTH segment
  ends first" means.
- RT5: the 20-bar baseline is the trade date's own completed coarse bars (ETH then RTH),
  population standard deviation, appended AFTER the trigger check, as the original did.
- RT6/RT7: the first trade date of a window has no prior day, so its V is 0.0 and is
  appended to the regime history exactly as the original's first-day snapshot (sqrt of a
  zero EWMA) was. That reproduces the original's warm-up behaviour rather than improving
  on it.
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass, field

from rules.xfa_rules import MES_TICK_SIZE, OrderIntent, Refusal
from strategy.interface import AccountView, Bar, market_intent
from strategy.research.d_volatility_state.h1_trailing_volatility_regime_gate import (
    _percentile_rank,
)
from strategy.research.g_timeframe.resample import (
    CoarseBar,
    CoarseBarBuilder,
    bar_limit,
    slot_count,
)

RETEST_TF = 5
OR_SLOTS = 6  # Mesfin (2026) section 4.1: 09:30-09:55 ET, "the first six five-minute bars"
MIN_BREAK_TICKS = 4  # the originals' 1.00-point buffer
QUANTITY_MICROS = 1
BASELINE_BARS = 20  # Mesfin section 4.2: range vs "the rolling 20-bar average"
VOLUME_Z_THRESHOLD = 3.0  # C-H2's thresholds, unchanged
RANGE_RATIO_THRESHOLD = 3.0
EWMA_LAMBDA = 0.94  # the D-H1/D-H2 constant, now applied per trade date
REGIME_LOOKBACK_DAYS = 60
MIN_HISTORY_DAYS = 30
TERCILE_LOW_MAX = 1.0 / 3.0
ENTRY_BAR_OFFSET = 60
BASE_HOLD_MINUTES = 30
TARGET_RISK_USD = 75.0
MIN_QUANTITY_MICROS = 1
MAX_QUANTITY_MICROS = 5
SIZING_WARMUP_DAYS = 20
MES_TICK_VALUE_USD = 1.25
_EPS = 1e-9


def _flat(account: AccountView) -> bool:
    return account.position_micros == 0 and account.pending_signed_micros == 0


def _exit(bar: Bar, account: AccountView) -> tuple[OrderIntent | Refusal, ...]:
    side = "sell" if account.position_micros > 0 else "buy"
    return (market_intent(bar, side, abs(account.position_micros)),)


def _todays(completions: tuple[CoarseBar, ...], bar: Bar) -> tuple[CoarseBar, ...]:
    return tuple(c for c in completions if c.trade_date == bar.trade_date)


# ------------------------------------------------------------------ RT1-RT4 ----
@dataclass(frozen=True)
class OrbRetest:
    """B-H1 / B-H3 on 5-minute bars: OR = six 5-min bars, close-through trigger, N-bar hold."""

    hold_bars: int
    leg: str  # "breakout" (B-H1, B-H3 breakout leg) or "fade" (B-H3 fade leg)
    name: str = "rt_orb_5min"
    _builder: CoarseBarBuilder = field(default_factory=lambda: CoarseBarBuilder(RETEST_TF))
    _date: list[object] = field(default_factory=lambda: [None])
    _or: list[float | None] = field(default_factory=lambda: [None, None])
    _or_slots_seen: list[int] = field(default_factory=lambda: [0])
    _triggered: list[bool] = field(default_factory=lambda: [False])
    _bars_held: list[int] = field(default_factory=lambda: [-1])

    def __post_init__(self) -> None:
        if self.hold_bars < 1:
            raise ValueError(f"hold_bars {self.hold_bars!r} must be >= 1")
        if self.leg not in ("breakout", "fade"):
            raise ValueError(f"leg {self.leg!r} must be 'breakout' or 'fade'")

    def _reset(self, bar: Bar) -> None:
        if self._date[0] != bar.trade_date:
            self._date[0] = bar.trade_date
            self._or[0] = self._or[1] = None
            self._or_slots_seen[0] = 0
            self._triggered[0] = False
            self._bars_held[0] = -1

    def _side(self, coarse: CoarseBar) -> str | None:
        buffer = MIN_BREAK_TICKS * MES_TICK_SIZE
        if coarse.close >= self._or[0] + buffer:
            broke = "buy"
        elif coarse.close <= self._or[1] - buffer:
            broke = "sell"
        else:
            return None
        if self.leg == "breakout":
            return broke
        return "sell" if broke == "buy" else "buy"

    def on_bar(self, bar: Bar, account: AccountView) -> tuple[OrderIntent | Refusal, ...]:
        self._reset(bar)
        last_slot = slot_count("RTH", RETEST_TF, bar_limit(bar)) - 1
        intents: tuple[OrderIntent | Refusal, ...] = ()
        # A late completion (rule R6) can deliver two coarse bars in one push; every one of
        # them must be seen, so nothing returns from inside this loop.
        for coarse in _todays(self._builder.push(bar), bar):
            if coarse.segment != "RTH":
                continue
            if coarse.slot < OR_SLOTS:
                self._or[0] = coarse.high if self._or[0] is None else max(self._or[0], coarse.high)
                self._or[1] = coarse.low if self._or[1] is None else min(self._or[1], coarse.low)
                self._or_slots_seen[0] += 1
                continue
            if account.position_micros != 0 and self._bars_held[0] >= 0:
                self._bars_held[0] += 1
                if self._bars_held[0] >= self.hold_bars or coarse.slot >= last_slot:
                    self._bars_held[0] = -1
                    intents = _exit(bar, account)
                continue
            if self._triggered[0] or self._or_slots_seen[0] < OR_SLOTS or not _flat(account):
                continue
            if coarse.slot >= last_slot:
                continue  # no next bar to hold through
            side = self._side(coarse)
            if side is not None:
                self._triggered[0] = True
                self._bars_held[0] = 0
                intents = (market_intent(bar, side, QUANTITY_MICROS),)
        return intents


# ---------------------------------------------------------------------- RT5 ----
@dataclass(frozen=True)
class SpikeFadeRetest:
    """C-H2 on 5-minute bars: spike vs the day's trailing 20 coarse bars, fade, hold bar+1."""

    name: str = "rt5_post_spike_fade_5min"
    _builder: CoarseBarBuilder = field(default_factory=lambda: CoarseBarBuilder(RETEST_TF))
    _date: list[object] = field(default_factory=lambda: [None])
    _volumes: deque[float] = field(default_factory=lambda: deque(maxlen=BASELINE_BARS))
    _ranges: deque[float] = field(default_factory=lambda: deque(maxlen=BASELINE_BARS))
    _holding: list[bool] = field(default_factory=lambda: [False])
    _entry_decision_ns: list[int] = field(default_factory=lambda: [-1])

    def _reset(self, bar: Bar) -> None:
        if self._date[0] != bar.trade_date:
            self._date[0] = bar.trade_date
            self._volumes.clear()
            self._ranges.clear()
            self._holding[0] = False
            self._entry_decision_ns[0] = -1

    @staticmethod
    def _mean_std(values: deque[float]) -> tuple[float, float]:
        n = len(values)
        mean = sum(values) / n
        var = sum((v - mean) ** 2 for v in values) / n
        return mean, var**0.5

    def _is_spike(self, coarse: CoarseBar) -> bool:
        vol_mean, vol_std = self._mean_std(self._volumes)
        range_mean, _ = self._mean_std(self._ranges)
        volume_z = (coarse.volume - vol_mean) / vol_std if vol_std > _EPS else 0.0
        range_ratio = coarse.range / range_mean if range_mean > _EPS else 0.0
        return volume_z > VOLUME_Z_THRESHOLD or range_ratio > RANGE_RATIO_THRESHOLD

    @staticmethod
    def _next_slot_exists(coarse: CoarseBar, limit: int) -> bool:
        if coarse.slot + 1 < slot_count(coarse.segment, RETEST_TF, limit):
            return True
        # The last ETH slot hands off to RTH slot 0 at 08:30 (rule R5) if RTH exists.
        return coarse.segment == "ETH" and coarse.end == 930 and slot_count(
            "RTH", RETEST_TF, limit) > 0

    def on_bar(self, bar: Bar, account: AccountView) -> tuple[OrderIntent | Refusal, ...]:
        self._reset(bar)
        limit = bar_limit(bar)
        intents: tuple[OrderIntent | Refusal, ...] = ()
        for coarse in _todays(self._builder.push(bar), bar):
            if self._holding[0]:
                # The hold ends at the first completion AFTER the entry's decision bar at
                # which the fill is visible. A completion in the same push (rule R6's late
                # bar) predates the fill and is not the held bar; a flat account at a later
                # completion means the entry was refused, so the hold is simply cleared.
                if bar.decision_ts_ns > self._entry_decision_ns[0]:
                    if account.position_micros != 0:
                        intents = _exit(bar, account)
                        self._holding[0] = False
                    elif _flat(account):
                        self._holding[0] = False
            elif (_flat(account) and len(self._volumes) >= BASELINE_BARS
                  and self._is_spike(coarse) and coarse.close != coarse.open
                  and self._next_slot_exists(coarse, limit)):
                side = "sell" if coarse.close > coarse.open else "buy"
                intents = (market_intent(bar, side, QUANTITY_MICROS),)
                self._holding[0] = True
                self._entry_decision_ns[0] = bar.decision_ts_ns
            self._volumes.append(float(coarse.volume))
            self._ranges.append(coarse.range)
        return intents


# ------------------------------------------------------------------ RT6-RT7 ----
class DailyVolEstimator:
    """V_d = sqrt of an EWMA (lambda 0.94) over trade dates of the mean squared 5-minute
    close-to-close log return; uses dates strictly before d (rule R5 adjacency)."""

    def __init__(self) -> None:
        self._builder = CoarseBarBuilder(RETEST_TF)
        self._date: object = None
        self._prev: CoarseBar | None = None
        self._squares: list[float] = []
        self._ewma: float | None = None
        self.days_folded = 0
        self.v_today = 0.0

    def start_day(self, bar: Bar) -> bool:
        """Fold the finished day into the EWMA on a trade-date change; True if a new day."""
        if self._date == bar.trade_date:
            return False
        if self._squares:
            m = sum(self._squares) / len(self._squares)
            self._ewma = m if self._ewma is None else (
                EWMA_LAMBDA * self._ewma + (1.0 - EWMA_LAMBDA) * m)
            self.days_folded += 1
        self._date = bar.trade_date
        self._squares = []
        self._prev = None
        self.v_today = math.sqrt(self._ewma) if self._ewma is not None else 0.0
        return True

    def push(self, bar: Bar) -> None:
        for coarse in _todays(self._builder.push(bar), bar):
            prev = self._prev
            if prev is not None and prev.end == coarse.start and prev.close > 0:
                ret = math.log(coarse.close / prev.close)
                self._squares.append(ret * ret)
            self._prev = coarse


@dataclass(frozen=True)
class DailyVolRegimeGateRetest:
    """D-H1 with the vol state measured per trade date instead of per minute."""

    name: str = "rt6_daily_vol_regime_gate"
    _vol: DailyVolEstimator = field(default_factory=DailyVolEstimator)
    _history: deque[float] = field(default_factory=lambda: deque(maxlen=REGIME_LOOKBACK_DAYS))
    _bar_index_today: list[int] = field(default_factory=lambda: [-1])
    _low_regime: list[bool] = field(default_factory=lambda: [False])
    _bars_since_entry: list[int] = field(default_factory=lambda: [-1])

    def _new_day(self, bar: Bar) -> None:
        if not self._vol.start_day(bar):
            return
        self._bar_index_today[0] = -1
        self._bars_since_entry[0] = -1
        v_today = self._vol.v_today
        if len(self._history) >= MIN_HISTORY_DAYS:
            self._low_regime[0] = _percentile_rank(self._history, v_today) <= TERCILE_LOW_MAX
        else:
            self._low_regime[0] = False
        self._history.append(v_today)

    def on_bar(self, bar: Bar, account: AccountView) -> tuple[OrderIntent | Refusal, ...]:
        self._new_day(bar)
        self._bar_index_today[0] += 1
        self._vol.push(bar)
        if account.position_micros != 0 and self._bars_since_entry[0] >= 0:
            self._bars_since_entry[0] += 1
            if self._bars_since_entry[0] >= BASE_HOLD_MINUTES:
                self._bars_since_entry[0] = -1
                return _exit(bar, account)
            return ()
        if (_flat(account) and self._low_regime[0]
                and self._bar_index_today[0] == ENTRY_BAR_OFFSET):
            self._bars_since_entry[0] = 0
            return (market_intent(bar, "buy", QUANTITY_MICROS),)
        return ()


@dataclass(frozen=True)
class DailyVolSizingRetest:
    """D-H2 with the sizing vol measured per trade date instead of per minute."""

    name: str = "rt7_daily_vol_sizing"
    _vol: DailyVolEstimator = field(default_factory=DailyVolEstimator)
    _bar_index_today: list[int] = field(default_factory=lambda: [-1])
    _bars_since_entry: list[int] = field(default_factory=lambda: [-1])
    _sized_quantities: list[int] = field(default_factory=list)

    def _sized_quantity(self, bar: Bar) -> int:
        vol = self._vol.v_today  # per 5-minute return
        if vol <= 0.0:
            return MAX_QUANTITY_MICROS
        expected_move_price = bar.close * vol * math.sqrt(BASE_HOLD_MINUTES / RETEST_TF)
        risk_usd = expected_move_price / MES_TICK_SIZE * MES_TICK_VALUE_USD
        if risk_usd <= 0.0:
            return MAX_QUANTITY_MICROS
        raw = round(TARGET_RISK_USD / risk_usd)
        return max(MIN_QUANTITY_MICROS, min(MAX_QUANTITY_MICROS, raw))

    def on_bar(self, bar: Bar, account: AccountView) -> tuple[OrderIntent | Refusal, ...]:
        if self._vol.start_day(bar):
            self._bar_index_today[0] = -1
            self._bars_since_entry[0] = -1
        self._bar_index_today[0] += 1
        self._vol.push(bar)
        if account.position_micros != 0 and self._bars_since_entry[0] >= 0:
            self._bars_since_entry[0] += 1
            if self._bars_since_entry[0] >= BASE_HOLD_MINUTES:
                self._bars_since_entry[0] = -1
                return _exit(bar, account)
            return ()
        ready = self._vol.days_folded >= SIZING_WARMUP_DAYS
        if _flat(account) and ready and self._bar_index_today[0] == ENTRY_BAR_OFFSET:
            qty = self._sized_quantity(bar)
            self._sized_quantities.append(qty)
            self._bars_since_entry[0] = 0
            return (market_intent(bar, "buy", qty),)
        return ()


RETESTS: tuple[tuple[str, str, object], ...] = (
    # (label, original D.1 label, factory)
    ("RT1 B-H1 ORB 5-min bars (hold 1 bar)", "B-H1 opening-range breakout (hold 5)",
     lambda: OrbRetest(hold_bars=1, leg="breakout", name="rt1_orb_5min_hold1")),
    ("RT2 B-H1 ORB 5-min bars (hold 15 bars)", "B-H1 opening-range breakout (hold 75)",
     lambda: OrbRetest(hold_bars=15, leg="breakout", name="rt2_orb_5min_hold15")),
    ("RT3 B-H3 breakout leg 5-min bars", "B-H3 breakout leg",
     lambda: OrbRetest(hold_bars=6, leg="breakout", name="rt3_orb_5min_breakout_hold6")),
    ("RT4 B-H3 fade leg 5-min bars", "B-H3 fade leg",
     lambda: OrbRetest(hold_bars=6, leg="fade", name="rt4_orb_5min_fade_hold6")),
    ("RT5 C-H2 spike fade 5-min bars", "C-H2 post-spike exhaustion fade", SpikeFadeRetest),
    ("RT6 D-H1 daily-vol regime gate", "D-H1 trailing-vol regime gate", DailyVolRegimeGateRetest),
    ("RT7 D-H2 daily-vol sizing", "D-H2 inverse-vol sizing", DailyVolSizingRetest),
)
