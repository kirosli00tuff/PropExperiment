"""K8-oilcad-01: crude leads the Canadian dollar by one 5-minute step, traded on 6C with MCL as
the signal leg (Stage E.9; reports/stage_e9_member_specs.md section 2; catalog
reports/stage_e0_catalog_K8.md lines 373-488; readings K8-L-04..K8-L-11).

Rule (every clock time CT; a leg's "bar at hh:mm" on trade date d opens at hh:mm on CT date d and
carries trade_date d, S0.4, K8-L-02):
- Decision times T = {08:05, 08:10, ..., 13:25}, 65 a day; t covers the block [t - 5, t).
- Block return r_t = (c1 - c6) / c6, a Python float from the integer vendor ticks of the closes of
  the MCL bars at t - 1 (c1) and t - 6 (c6) (K4-L-05, K8-L-09). Both bars present with one
  instrument_id and c6 > 0, else r_t is undefined (K8-L-05, K8-L-10). Every defined r_t is a
  reference value of its trade date, traded or not.
- Reference dates: the 20 most recent OILCAD_DATES strictly before d (roll-blackout dates included,
  K8-L-04). s(d) = statistics.stdev (n - 1) of every defined r_t on them; n >= 1,000, else no trade
  on d; s(d) = 0: no trade on d. Warm-up (K4-L-09): no trade while a reference date precedes the
  trade date of the first bar this member received in the run.
- Entry at t: d in OILCAD_DATES; the account flat on 6C (no position, no pending order, K8-L-11);
  r_t defined; the 6C bar at t - 1 present (S0.6); z_t = r_t / s(d) with |z_t| >= 2.0 (float);
  and the fill minute t not in a 6C guarded interval (C6 skip, S0.10, K8-L-08). Market intent of
  q_c on the 6C bar at t - 1 (fills at the open of the 6C bar at t): BUY if c1 > c6, SELL if
  c1 < c6. A missing bar or an undefined r_t blocks that t only (K8-L-06).
- Exit: T_e = the CT open of the 6C bar at which the account first shows the position (K8-L-07);
  market intent closing the whole position on the first present 6C bar at or after T_e + 14 (fills
  nominally at T_e + 15), resent while refused (S0.7, E.3-L-22). The engine's flatten, D9.7 exit
  and MLL close are the backstops: the account is then flat and later decisions apply (K7-L-07).
- Never an intent on MCL. The engine refuses opens on a roll-blackout date of either leg (D4,
  V16(a)) and when any leg lacks the bar at that minute (D11.5); the member repeats neither.
One traded leg, q_c contracts of 6C (1).
"""

from __future__ import annotations

import statistics
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from typing import Any
from zoneinfo import ZoneInfo

from rules.products import product
from rules.xfa_rules import Refusal
from screening.stage_e_frozen import load_frozen_tables
from strategy.members.k8._calendar import OILCAD_DATES, previous_dates
from strategy.members.k8._releases import in_guard
from strategy.stage_e.interface import (
    LegIntent,
    LegSpec,
    MemberAccountView,
    MinuteView,
    TradingInterval,
    leg_market_intent,
)

MEMBER_ID = "K8-oilcad-01"
TRADED = "6C"  # the one traded leg (C lines 375-378, S0.1)
SIGNAL = "MCL"  # the crude signal leg, read only (V16(c))
CT = ZoneInfo("America/Chicago")
NS_PER_S = 1_000_000_000
NS_PER_MIN = 60 * NS_PER_S
_ANCHOR_DAY = date(2000, 1, 3)  # any date: clock arithmetic on a time of day

FIRST_DECISION_CT = time(8, 5)  # T = {08:05, ..., 13:25} (C line 401)
LAST_DECISION_CT = time(13, 25)
STEP_MIN = 5  # the block length and the decision step
LAST_BAR_BEFORE_T_MIN = 1  # c1: the MCL bar at t - 1; also the 6C entry bar
FIRST_BAR_BEFORE_T_MIN = 6  # c6: the MCL bar at t - 6
REFERENCE_DATES = 20  # the 20 most recent OILCAD_DATES strictly before d
MIN_VALUES = 1000  # n >= 1,000 (max 1,300)
Z_THRESHOLD = 2.0  # |z_t| >= 2.0
EXIT_AFTER_FILL_MIN = 14  # exit intent on the 6C bar at T_e + 14, fill at T_e + 15

_OILCAD_SET: frozenset[date] = frozenset(OILCAD_DATES)


def shift(at: time, minutes: int) -> time:
    """A clock time ``minutes`` later (negative: earlier) on the same CT day."""
    return (datetime.combine(_ANCHOR_DAY, at) + timedelta(minutes=minutes)).time()


def decision_times() -> tuple[time, ...]:
    """T: FIRST_DECISION_CT to LAST_DECISION_CT every STEP_MIN minutes (65 a day)."""
    first = datetime.combine(_ANCHOR_DAY, FIRST_DECISION_CT)
    last = datetime.combine(_ANCHOR_DAY, LAST_DECISION_CT)
    span = int((last - first).total_seconds()) // 60
    return tuple(shift(FIRST_DECISION_CT, k) for k in range(0, span + 1, STEP_MIN))


DECISION_TIMES_CT: tuple[time, ...] = decision_times()


def ct_open(bar: Any) -> datetime:
    """The bar's open (``ts_event_ns``, whole seconds: bars sit on the minute) in CT."""
    return datetime.fromtimestamp(bar.ts_event_ns // NS_PER_S, tz=UTC).astimezone(CT)


def to_ticks(price: float, tick: Decimal) -> int:
    """round(price / vendor_tick), computed exactly in Decimal."""
    return round(Decimal(repr(price)) / tick)


def block_return(c1: int, c6: int) -> float | None:
    """r_t = (c1 - c6) / c6 from integer ticks as a Python float; None when c6 <= 0 (C10)."""
    if c6 < 0:
        return None
    return (c1 - c6) / c6


def scale(values: Sequence[float]) -> float | None:
    """s(d): the sample standard deviation (n - 1) of the reference values; None (no trade on d)
    when there are fewer than MIN_VALUES of them or the deviation is 0."""
    if len(values) < MIN_VALUES:
        return None
    s = statistics.stdev(values)
    if s <= 0:
        return None
    return s


def passes_threshold(r: float, s: float) -> bool:
    """|z_t| >= Z_THRESHOLD with z_t = r_t / s(d) in float (K8-L-09)."""
    return abs(r / s) >= Z_THRESHOLD


@dataclass
class OilCad:
    """K8-oilcad-01: 6C traded, MCL read. Each MCL trade date's defined r_t values are kept while
    a later reference set can still use them."""

    root: str = TRADED
    name: str = field(init=False)
    legs: tuple[LegSpec, ...] = field(init=False)
    trading_windows: dict = field(init=False)
    _q: int = field(init=False, repr=False)
    _mcl_tick: Decimal = field(init=False, repr=False)
    _t_of_last_bar: dict = field(init=False, repr=False)  # clock t - 1 -> t
    _t_of_first_bar: dict = field(init=False, repr=False)  # clock t - 6 -> t
    _first_day: date | None = field(default=None, init=False, repr=False)
    _mcl_day: date | None = field(default=None, init=False, repr=False)
    _firsts: dict = field(default_factory=dict, init=False, repr=False)  # t -> (c6, id)
    _history: dict = field(default_factory=dict, init=False, repr=False)  # date -> r values
    _scale_day: date | None = field(default=None, init=False, repr=False)
    _scale: float | None = field(default=None, init=False, repr=False)
    _te_ns: int | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.root != TRADED:
            raise ValueError(f"{MEMBER_ID} trades {TRADED} only, not {self.root!r}")
        self._q = load_frozen_tables().vehicles[TRADED].q_c
        self._mcl_tick = product(SIGNAL).vendor_tick
        self.name = f"{MEMBER_ID} {TRADED}"
        self.legs = (LegSpec(TRADED, True), LegSpec(SIGNAL, False))
        self._t_of_last_bar = {shift(t, -LAST_BAR_BEFORE_T_MIN): t for t in DECISION_TIMES_CT}
        self._t_of_first_bar = {shift(t, -FIRST_BAR_BEFORE_T_MIN): t for t in DECISION_TIMES_CT}
        first, last = DECISION_TIMES_CT[0], DECISION_TIMES_CT[-1]
        # S0.12, [start, end) of bar opens: 6C from the first entry bar (08:04) to the last exit
        # fill bar (13:25 + 15 = 13:40) inclusive; MCL from the first t - 6 bar (07:59) to the
        # last t - 1 bar (13:24) inclusive
        last_exit_fill = shift(last, EXIT_AFTER_FILL_MIN + 1)
        self.trading_windows = {
            TRADED: (TradingInterval(shift(first, -LAST_BAR_BEFORE_T_MIN),
                                     shift(last_exit_fill, 1)),),
            SIGNAL: (TradingInterval(shift(first, -FIRST_BAR_BEFORE_T_MIN), last),),
        }

    # -- the MCL signal ------------------------------------------------------------------
    def _new_mcl_day(self, day: date) -> None:
        """Start ``day``'s blocks; keep only the values a reference set from ``day`` on can use."""
        refs = previous_dates(OILCAD_DATES, day, REFERENCE_DATES)
        oldest = refs[0] if refs else day
        self._history = {d: v for d, v in self._history.items() if d >= oldest}
        self._mcl_day, self._firsts = day, {}

    def _signal(self, view: MinuteView) -> tuple[float, int] | None:
        """Read this minute's MCL bar: (r_t, c1 - c6) when it is the bar at t - 1 (on its own
        CT date) of a defined r_t; records the bar if it is a bar at t - 6; files every defined
        r_t under its trade date."""
        bar = view.bar(SIGNAL)
        if bar is None:
            return None  # never forward filled
        opened = ct_open(bar)
        day = bar.trade_date
        if opened.date() != day:
            return None  # the previous CT evening's bars hold no block
        if day != self._mcl_day:
            self._new_mcl_day(day)
        at = opened.time()
        close = to_ticks(bar.close, self._mcl_tick)
        out = None
        t = self._t_of_last_bar.get(at)
        first = None if t is None else self._firsts.get(t)
        if first is not None and first[1] == bar.instrument_id:
            r = block_return(close, first[0])
            if r is not None:
                self._history = {**self._history, day: (*self._history.get(day, ()), r)}
                out = (r, close - first[0])
        t_next = self._t_of_first_bar.get(at)
        if t_next is not None:
            self._firsts = {**self._firsts, t_next: (close, bar.instrument_id)}
        return out

    def _scale_of(self, day: date) -> float | None:
        """s(d), once per trade date; None: no trade on d (warm-up, too few values, s = 0)."""
        if day == self._scale_day:
            return self._scale
        refs = previous_dates(OILCAD_DATES, day, REFERENCE_DATES)
        warm = (len(refs) == REFERENCE_DATES and self._first_day is not None
                and refs[0] >= self._first_day)
        s = scale([v for d in refs for v in self._history.get(d, ())]) if warm else None
        self._scale_day, self._scale = day, s
        return s

    # -- the member contract -------------------------------------------------------------
    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> Sequence[LegIntent | Refusal]:
        if self._first_day is None:  # K4-L-09: the first bar this member received in the run
            days = [b.trade_date for b in view.bars.values() if b is not None]
            self._first_day = min(days) if days else None
        signal = self._signal(view)
        position = account.position(TRADED)
        if position == 0:
            self._te_ns = None
        elif self._te_ns is None:  # K8-L-07: the account first shows the position here
            self._te_ns = view.ts_event_ns
        bar = view.bar(TRADED)
        if bar is None:  # no 6C bar: no entry and no exit at this minute
            return ()
        if position:
            return self._exit(view, account, bar, position)
        if account.pending.get(TRADED, 0):
            return ()  # K8-L-11: a pending order is not flat
        return self._entry(view, bar, signal)

    def _exit(self, view: MinuteView, account: MemberAccountView, bar: Any, position: int
              ) -> Sequence[LegIntent | Refusal]:
        """S0.7: on the first present 6C bar at or after T_e + 14, nothing pending."""
        if account.pending.get(TRADED, 0) or self._te_ns is None:
            return ()
        if bar.ts_event_ns < self._te_ns + EXIT_AFTER_FILL_MIN * NS_PER_MIN:
            return ()
        side = "sell" if position > 0 else "buy"
        return (leg_market_intent(view, TRADED, side, abs(position)),)

    def _entry(self, view: MinuteView, bar: Any, signal: tuple[float, int] | None
               ) -> Sequence[LegIntent | Refusal]:
        if signal is None:
            return ()  # not a t - 1 minute, or r_t undefined at t (K8-L-05, K8-L-06)
        # ``signal`` comes from the MCL bar of this same minute, a bar at t - 1 on its own CT
        # date, so this 6C bar opens at t - 1 too; it must carry that CT date (S0.4, K7-L-01)
        day = bar.trade_date
        if ct_open(bar).date() != day:
            return ()
        if day not in _OILCAD_SET:
            return ()  # S0.8
        s = self._scale_of(day)
        if s is None:
            return ()
        r, diff = signal
        if not passes_threshold(r, s):
            return ()
        if in_guard(TRADED, bar.ts_event_ns + NS_PER_MIN):
            return ()  # C6: the fill minute t is in a 6C guarded interval: skipped
        side = "buy" if diff > 0 else "sell"
        return (leg_market_intent(view, TRADED, side, self._q),)


def make_6c() -> OilCad:
    return OilCad(TRADED)


__all__ = ["DECISION_TIMES_CT", "MEMBER_ID", "SIGNAL", "TRADED", "OilCad", "block_return",
           "make_6c", "passes_threshold", "scale"]
