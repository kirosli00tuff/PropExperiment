"""Family H (Stage D.1f, class C7): the mechanics the six daily-bar modules share.

Specification, FROZEN: reports/stage_d1f_confirmation_list.md section 2.1 A3 ("Common
mechanics", the condition table and the look-ahead check list), 3.1 (q = 2 micros) and 5.5.
The six thin modules h1_* .. h6_* hold only their condition, lookback, guarded-bar count and
entry mode; everything below is written once and used by all six.

What one strategy instance does, bar by bar (it sees only the bars the engine hands it):

- Daily bar of trade date d, built from bars already seen: O = open of the 08:30 CT bar,
  H / L = max high / min low over CT [08:30, 15:00), C = close of the 14:59 bar. It is
  COMPLETE only if the 08:30 and 14:59 bars exist, the date has no early halt, and all its RTH
  bars carry one instrument_id. It is finalised when the first bar of a LATER trade date
  arrives, so day d's own bar can never enter day d's condition. Incomplete days are dropped:
  "d-1" is the most recent complete daily bar before d, "the last k" are the last k complete.
- Day d's condition is evaluated on day d's 08:30 bar from the complete bars of earlier trade
  dates only (the thin module's pure ``condition`` function), with the instrument guard H-1:
  the last ``guarded_bars`` complete bars (1 for H1, H2, H4, H5, H6; 2 for H3) must carry the
  08:30 bar's instrument_id. The earlier bars of H1 / H2 and the trailing 60 of H4 / H5 are
  exempt (NEW-9). Until the lookback is full the condition is None: no trade (warm-up runs
  from the window's own start because every screen builds a fresh instance).
- Opening range: max high / min low of day d's bars with CT time in [08:30, 09:00), valid only
  with the 08:30 bar and at least 25 of the 30 bars. Finalised on the first bar of the day
  with CT time >= 09:00, so that bar is never part of it.
- Entry, once per trade date, 2 micros, market_intent (the engine fills at the next bar's
  open): breakout (H1-H4) on the first bar with CT time in [09:00, 14:30) whose CLOSE is
  strictly above OR_high (buy) or strictly below OR_low (sell); fade (H5) the same trigger,
  opposite side; open (H6) on the 08:30 bar, side from the condition.
- Exit: a market_intent flattening the position on the first bar with CT time >= 14:58 and
  before the engine's no-new-positions time (``rules.xfa_rules.no_new_positions_time_ct``;
  15:08 CT on a normal day), which fills at the next open. If no such bar exists the engine's
  forced flatten closes the position; the strategy then records the day as a forced exit
  (``forced_exit_dates``) and logs it at WARNING (H-3). No stop, no target.
- A day whose bars carry early_halt_ct: no trade, and its daily bar is incomplete.

Readings taken where the specification is silent (each one makes a leak easier to see):
- Every "CT time" window is read on CT calendar date d: an RTH / OR / trigger / exit bar of
  trade date d is a bar of trade date d whose America/Chicago date is d.
- "The date has early_halt_ct null" is read from the bars of CT date d. data/bars.py attaches
  early_halt_ct per CT calendar date, so the ETH bars that open trade date d on the evening
  of d-1 carry d-1's halt (the Tuesday after a holiday Monday would otherwise be excluded).
- A forced exit is recorded when a bar at or after the no-new-positions time still shows the
  position open with no exit emitted, or when the day's last bar seen still shows it open.

This module never reads a file, a frame, a configuration or any hindsight field of a bar.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import date, time

import numpy as np

from rules.xfa_rules import CT, OrderIntent, Refusal, no_new_positions_time_ct
from strategy.interface import AccountView, Bar, market_intent

TICK_SIZE = 0.25  # MES tick; Range is measured in these
QUANTITY_MICROS = 2  # every H entry; pays the size-5 slippage bucket (R-8)
RTH_OPEN_CT = time(8, 30)  # daily O, OR start, H6 entry bar, instrument-guard reference
OR_END_CT = time(9, 0)  # OR over [08:30, 09:00): 30 one-minute bars
OR_MIN_BARS = 25  # of the 30
ENTRY_END_CT = time(14, 30)  # breakout triggers on bars in [09:00, 14:30): latest 14:29
EXIT_CT = time(14, 58)
CLOSE_BAR_CT = time(14, 59)  # daily C
RTH_END_CT = time(15, 0)  # daily H / L over [08:30, 15:00)
ENTRY_MODES = ("breakout", "fade", "open")

_LOG = logging.getLogger(__name__)


def to_ticks(price: float) -> int:
    """An on-grid price in whole ticks."""
    return round(price / TICK_SIZE)


@dataclass(frozen=True, slots=True)
class DailyBar:
    """One COMPLETE daily bar (the only kind that exists for a lookback)."""

    trade_date: date
    open: float
    high: float
    low: float
    close: float
    instrument_id: int

    @property
    def high_ticks(self) -> int:
        return to_ticks(self.high)

    @property
    def low_ticks(self) -> int:
        return to_ticks(self.low)

    @property
    def close_ticks(self) -> int:
        return to_ticks(self.close)

    @property
    def range_ticks(self) -> int:
        return self.high_ticks - self.low_ticks


@dataclass(frozen=True, slots=True)
class Condition:
    """Day d's condition value: whether it holds, the numbers its inequality compared (in the
    table's order, documented per module), and, for H6 only, the entry side it selects."""

    holds: bool
    values: tuple[float, ...]
    side: str | None = None


ConditionFn = Callable[[Sequence[DailyBar]], Condition | None]


def narrowest_range(prior: Sequence[DailyBar], k: int) -> Condition | None:
    """Range[d-1] strictly smaller than each of Range[d-2] .. Range[d-k]; values are
    (Range[d-1], Range[d-2], ..., Range[d-k]) in ticks. None until k complete bars exist."""
    if len(prior) < k:
        return None
    ranges = tuple(float(b.range_ticks) for b in reversed(prior[-k:]))
    return Condition(holds=all(ranges[0] < r for r in ranges[1:]), values=ranges)


def range_and_percentile(
    prior: Sequence[DailyBar], lookback: int, q: float
) -> tuple[float, float] | None:
    """(Range[d-1], np.percentile(ranges, q, method="linear")) where ranges are the
    ``lookback - 1`` complete ranges before d-1 (d-1 excluded). None until ``lookback``."""
    if len(prior) < lookback:
        return None
    window = prior[-lookback:]
    baseline = np.array([b.range_ticks for b in window[:-1]], dtype=float)
    cut = float(np.percentile(baseline, q, method="linear"))
    return float(window[-1].range_ticks), cut


@dataclass(frozen=True, slots=True)
class DayRecord:
    """What the strategy saw and did on one trade date (an audit snapshot, never an input)."""

    trade_date: date
    daily_bar: DailyBar | None  # None: incomplete, or the day is still in progress
    condition: Condition | None  # None: not evaluated (no 08:30 bar, early halt) or warm-up
    guard_ok: bool | None
    or_high: float | None
    or_low: float | None
    or_bars: int
    entry_side: str | None
    entry_decision_ns: int | None
    exit_decision_ns: int | None
    forced_exit: bool
    skip_reason: str | None  # None when an entry was emitted


class _Day:
    """Mutable per-trade-date accumulator; only ``DayRecord`` snapshots leave the class."""

    __slots__ = (
        "trade_date", "early_halt", "open", "high", "low", "close", "instruments",
        "has_open_bar", "condition", "guard_ok", "eligible", "or_high", "or_low", "or_bars",
        "or_final", "or_ok", "entry_side", "entry_decision_ns", "exit_decision_ns",
        "last_position", "forced_exit",
    )

    def __init__(self, trade_date: date) -> None:
        self.trade_date = trade_date
        self.early_halt = False
        self.open: float | None = None
        self.high: float | None = None
        self.low: float | None = None
        self.close: float | None = None
        self.instruments: set[int] = set()
        self.has_open_bar = False
        self.condition: Condition | None = None
        self.guard_ok: bool | None = None
        self.eligible = False
        self.or_high: float | None = None
        self.or_low: float | None = None
        self.or_bars = 0
        self.or_final = False
        self.or_ok = False
        self.entry_side: str | None = None
        self.entry_decision_ns: int | None = None
        self.exit_decision_ns: int | None = None
        self.last_position = 0
        self.forced_exit = False

    def daily_bar(self) -> DailyBar | None:
        complete = (self.has_open_bar and self.close is not None and not self.early_halt
                    and len(self.instruments) == 1)
        if not complete:
            return None
        assert self.open is not None and self.high is not None and self.low is not None
        assert self.close is not None
        return DailyBar(self.trade_date, self.open, self.high, self.low, self.close,
                        next(iter(self.instruments)))


def _is_flat(account: AccountView) -> bool:
    return account.position_micros == 0 and account.pending_signed_micros == 0


class DailyBarStrategy:
    """The shared Family H strategy. Built only by the six thin modules, which pass their
    module-level literals; see the module docstring for the mechanics."""

    def __init__(self, *, name: str, condition: ConditionFn, lookback: int,
                 guarded_bars: int, entry: str) -> None:
        if isinstance(lookback, bool) or not isinstance(lookback, int) or lookback < 1:
            raise ValueError(f"lookback {lookback!r} must be a positive int")
        if not isinstance(guarded_bars, int) or not 1 <= guarded_bars <= lookback:
            raise ValueError(f"guarded_bars {guarded_bars!r} must be in 1..{lookback}")
        if entry not in ENTRY_MODES:
            raise ValueError(f"entry {entry!r} must be one of {ENTRY_MODES}")
        self.name = name
        self._condition = condition
        self._lookback = lookback
        self._guarded_bars = guarded_bars
        self._entry = entry
        self._history: tuple[DailyBar, ...] = ()  # complete bars of EARLIER trade dates
        self._records: tuple[DayRecord, ...] = ()
        self._day: _Day | None = None

    # -- read-only views (audit and tests; the engine never reads them) -------------------
    @property
    def lookback(self) -> int:
        return self._lookback

    @property
    def guarded_bars(self) -> int:
        return self._guarded_bars

    @property
    def entry(self) -> str:
        return self._entry

    @property
    def day_records(self) -> tuple[DayRecord, ...]:
        current = () if self._day is None else (self._snapshot(self._day, None),)
        return (*self._records, *current)

    @property
    def forced_exit_dates(self) -> tuple[date, ...]:
        return tuple(r.trade_date for r in self.day_records if r.forced_exit)

    # -- the Strategy contract ------------------------------------------------------------
    def on_bar(self, bar: Bar, account: AccountView) -> tuple[OrderIntent | Refusal, ...]:
        self._roll_if_new_date(bar)
        day = self._day
        assert day is not None
        local = bar.open_ts_utc.astimezone(CT)
        if local.date() != day.trade_date:
            return ()  # ETH bars of the previous CT evening: nothing of day d happens there
        at = local.time()
        self._accumulate(day, bar, at)
        day.last_position = account.position_micros
        if day.entry_side is not None:
            return self._exit(day, bar, account, at)
        if at == RTH_OPEN_CT:
            self._evaluate(day, bar)
            if self._entry == "open":
                return self._enter(day, bar, account, day.condition.side if day.eligible
                                   and day.condition is not None else None)
            return ()
        if self._entry == "open" or at < OR_END_CT:
            return ()
        return self._breakout(day, bar, account, at)

    # -- per-date bookkeeping -------------------------------------------------------------
    def _roll_if_new_date(self, bar: Bar) -> None:
        if self._day is not None and bar.trade_date == self._day.trade_date:
            return
        if self._day is not None:
            if bar.trade_date < self._day.trade_date:
                raise ValueError(f"trade date went backwards: {bar.trade_date} after "
                                 f"{self._day.trade_date}")
            self._close_day(self._day)
        self._day = _Day(bar.trade_date)

    def _close_day(self, day: _Day) -> None:
        if day.entry_side is not None and day.exit_decision_ns is None and day.last_position:
            self._mark_forced(day, "the session ended with the position open")
        daily = day.daily_bar()
        if daily is not None:
            self._history = (*self._history, daily)[-self._lookback:]
        self._records = (*self._records, self._snapshot(day, daily))

    def _accumulate(self, day: _Day, bar: Bar, at: time) -> None:
        if bar.early_halt_ct is not None:
            day.early_halt = True
        if not RTH_OPEN_CT <= at < RTH_END_CT:
            return
        day.instruments.add(bar.instrument_id)
        day.high = bar.high if day.high is None else max(day.high, bar.high)
        day.low = bar.low if day.low is None else min(day.low, bar.low)
        if at == RTH_OPEN_CT:
            day.has_open_bar = True
            day.open = bar.open
        if at == CLOSE_BAR_CT:
            day.close = bar.close
        if at < OR_END_CT:
            day.or_high = bar.high if day.or_high is None else max(day.or_high, bar.high)
            day.or_low = bar.low if day.or_low is None else min(day.or_low, bar.low)
            day.or_bars += 1

    def _evaluate(self, day: _Day, bar: Bar) -> None:
        """Day d's condition and guard on its 08:30 bar, from earlier complete bars only."""
        if day.early_halt:
            return
        day.condition = self._condition(self._history)
        if day.condition is None:
            return
        guarded = self._history[-self._guarded_bars:]
        day.guard_ok = all(b.instrument_id == bar.instrument_id for b in guarded)
        day.eligible = day.condition.holds and day.guard_ok

    # -- orders ---------------------------------------------------------------------------
    def _breakout(self, day: _Day, bar: Bar, account: AccountView, at: time
                  ) -> tuple[OrderIntent | Refusal, ...]:
        if not day.or_final:
            day.or_final = True
            day.or_ok = day.has_open_bar and day.or_bars >= OR_MIN_BARS
        if not (day.eligible and day.or_ok) or day.early_halt or at >= ENTRY_END_CT:
            return ()
        assert day.or_high is not None and day.or_low is not None
        if bar.close > day.or_high:
            breakout = "buy"
        elif bar.close < day.or_low:
            breakout = "sell"
        else:
            return ()
        if self._entry == "fade":
            breakout = "sell" if breakout == "buy" else "buy"
        return self._enter(day, bar, account, breakout)

    def _enter(self, day: _Day, bar: Bar, account: AccountView, side: str | None
               ) -> tuple[OrderIntent | Refusal, ...]:
        if side is None or day.early_halt or not _is_flat(account):
            return ()
        day.entry_side = side
        day.entry_decision_ns = bar.decision_ts_ns
        return (market_intent(bar, side, QUANTITY_MICROS),)

    def _exit(self, day: _Day, bar: Bar, account: AccountView, at: time
              ) -> tuple[OrderIntent | Refusal, ...]:
        position = account.position_micros
        if day.exit_decision_ns is not None or position == 0 or at < EXIT_CT:
            return ()
        before_cutoff = (at < no_new_positions_time_ct(bar.early_halt_ct)
                         and not bar.in_no_new_positions_window)
        if not before_cutoff:
            self._mark_forced(day, f"no bar in [{EXIT_CT:%H:%M}, no-new-positions time) CT")
            return ()
        day.exit_decision_ns = bar.decision_ts_ns
        return (market_intent(bar, "sell" if position > 0 else "buy", abs(position)),)

    def _mark_forced(self, day: _Day, why: str) -> None:
        if day.forced_exit:
            return
        day.forced_exit = True
        _LOG.warning("%s: forced exit on %s (%s); the engine's flatten closes the position",
                     self.name, day.trade_date, why)

    # -- audit ----------------------------------------------------------------------------
    def _snapshot(self, day: _Day, daily: DailyBar | None) -> DayRecord:
        return DayRecord(
            trade_date=day.trade_date, daily_bar=daily, condition=day.condition,
            guard_ok=day.guard_ok, or_high=day.or_high, or_low=day.or_low,
            or_bars=day.or_bars, entry_side=day.entry_side,
            entry_decision_ns=day.entry_decision_ns, exit_decision_ns=day.exit_decision_ns,
            forced_exit=day.forced_exit, skip_reason=self._skip_reason(day),
        )

    def _skip_reason(self, day: _Day) -> str | None:
        if day.entry_side is not None:
            return None
        if day.early_halt:
            return "early_halt"
        if not day.has_open_bar:
            return "missing_0830_bar"
        if day.condition is None:
            return "warm_up"
        if not day.guard_ok:
            return "instrument_guard"
        if not day.condition.holds:
            return "condition_false"
        if self._entry != "open" and day.or_final and not day.or_ok:
            return "or_coverage"
        return "no_trigger"
