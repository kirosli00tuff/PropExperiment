"""K5-ovr-01: hourly overreaction reversal (Stage E.4 Part 2; reports/stage_e4b_member_specs.md
section 7; catalog reports/stage_e0_catalog_K5.md lines 713-804; readings K4-L-05, K4-L-08,
K4-L-09, K4-L-10, K5-L-05, K5-L-06). The same rule text as K4-ovr-01 with K5's decision clock
(E.1 F-7): copied from strategy/members/k4/ovr.py, never imported from it; it differs only in the
clock, the calendar table and the value floor.

Rule (every clock time CT, bars of trade date d on CT date d; S0.4):
- Decision times t = O + 60k for k = 1, 2, ... while t <= C, from the frozen O and C: MGC 08:20,
  09:20, 10:20, 11:20, 12:20 (five); MHG 08:10, 09:10, 10:10, 11:10 (four).
- Signal r(t) = (close of the bar at t-1 - open of the bar at t-60) / open of the bar at t-60, as
  the Python float (tc - to) / to of integer vendor ticks (K4-L-05). Both bars must be present
  with one instrument_id (the per-decision-time guard, S0.9) and to > 0 (C10), else no trade at t.
- Reference dates: the 20 most recent METALS_FULL_SESSIONS dates strictly before d (EC-CAL: a
  roll-blackout date counts, an early-halt date is not in the table; K5-L-05, K4-L-08).
- Reference values: r(tau) at the same decision clock times on those dates, each counted only
  when its two bars are present with one instrument_id and its open is > 0. A reference date
  without bars keeps its slot and contributes fewer values (K4-L-08). Fewer than 80% of the
  possible values (MGC 80 of 100, MHG 64 of 80; K5-L-06): no trade at t.
- Warm-up: no trade while any reference date precedes the trade date of the first bar this
  member received in the run (K4-L-09).
- Cuts: P10, P90 = numpy.percentile(values, [10, 90], method="linear") on the floats.
- Entry: r(t) <= P10 buys, r(t) >= P90 sells; both at once (P10 = P90 = r) is no trade
  (K4-L-10); otherwise no trade. Market intent on the bar at t-1 (that exact bar, S0.6), only
  when flat with no pending order (so positions never overlap), filling at the open of t.
- Exit: market intent on the first present bar at or after t+58 (fills nominally at t+59),
  resent while refused (S0.7, E.3-L-22). The engine's forced flatten at F and its D9.7 exit are
  the backstops: after an engine-forced exit the member sends no exit of its own, cannot re-enter
  at that decision time (its entry bar has passed), and later decision times proceed as usual.
- Early halts: a decision bar carrying early_halt_ct means no trade at that t (S0.8), so an
  early-halt trade date is not traded at any t.
One traded leg, q_c contracts (MGC 1, MHG 2). No stop, no filter, no size rule beyond the spec.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict, dataclass, field
from datetime import date, time
from typing import Any

import numpy as np

from rules.xfa_rules import Refusal
from strategy.members.k5._calendar import METALS_FULL_SESSIONS
from strategy.members.k5._port_common import (
    LegFacts,
    ct_open,
    exit_if_due,
    is_flat,
    label,
    leg_facts,
    shift,
    to_ticks,
)
from strategy.stage_e.interface import (
    LegIntent,
    LegSpec,
    MemberAccountView,
    MinuteView,
    TradingInterval,
    leg_market_intent,
)

MEMBER_ID = "K5-ovr-01"
DECISION_STEP_MIN = 60  # t = O + 60k for k = 1, 2, ... while t <= C (C lines 745-747)
SIGNAL_MINUTES = 60  # the signal opens at the bar at t-60
DECISION_BAR_BEFORE_T_MIN = 1  # the signal closes at, and the entry is sent on, the bar at t-1
EXIT_AFTER_T_MIN = 58  # the exit is sent on the first bar at or after t+58 (fill t+59)
REFERENCE_DATES = 20  # the 20 most recent full sessions strictly before d
VALUE_FLOOR_PERCENT = 80  # at least 80% of the possible values (K5-L-06): 80 of 100, 64 of 80
LOW_PERCENTILE, HIGH_PERCENTILE = 10, 90  # deciles
PERCENTILE_METHOD = "linear"
WINDOW_END_AFTER_LAST_T_MIN = 60  # S0.12: (O, last t + 60); the last exit fill is t+59

_FULL_SESSIONS: tuple[date, ...] = tuple(date.fromisoformat(s) for s in METALS_FULL_SESSIONS)
_FULL_ORDINALS = np.array([d.toordinal() for d in _FULL_SESSIONS], dtype=np.int64)


def _minute_of_day(at: time) -> int:
    return at.hour * 60 + at.minute


def decision_times(o: time, c: time) -> tuple[time, ...]:
    """t = O + 60k for k = 1, 2, ... while t <= C (C lines 745-747): MGC (07:20, 12:30) gives
    08:20..12:20 (five), MHG (07:10, 12:00) gives 08:10..11:10 (four)."""
    span = _minute_of_day(c) - _minute_of_day(o)
    return tuple(shift(o, m) for m in range(DECISION_STEP_MIN, span + 1, DECISION_STEP_MIN))


def min_values(n_times: int) -> int:
    """The value floor: at least VALUE_FLOOR_PERCENT % of the possible values, n_times x
    REFERENCE_DATES, rounded up (K5-L-06): 80 of 100 on MGC, 64 of 80 on MHG."""
    possible = n_times * REFERENCE_DATES
    return -((-possible * VALUE_FLOOR_PERCENT) // 100)


def reference_dates(day: date) -> tuple[date, ...]:
    """The REFERENCE_DATES most recent METALS_FULL_SESSIONS dates strictly before ``day``,
    oldest first (fewer only at the table's start)."""
    i = int(np.searchsorted(_FULL_ORDINALS, day.toordinal(), side="left"))
    return _FULL_SESSIONS[max(0, i - REFERENCE_DATES):i]


def hourly_return(open_ticks: int, close_ticks: int) -> float | None:
    """r = (tc - to) / to from integer ticks (K4-L-05); None when to <= 0 (C10)."""
    if open_ticks <= 0:
        return None
    return (close_ticks - open_ticks) / open_ticks


def percentile_side(r: float, values: Sequence[float]) -> str | None:
    """The entry side from r(t) and the reference values: r <= P10 buys, r >= P90 sells, both
    (the tie P10 = P90 = r) or neither is no trade (K4-L-10)."""
    p_low, p_high = np.percentile(np.asarray(values, dtype=float),
                                  [LOW_PERCENTILE, HIGH_PERCENTILE], method=PERCENTILE_METHOD)
    at_low, at_high = r <= float(p_low), r >= float(p_high)
    if at_low == at_high:
        return None
    return "buy" if at_low else "sell"


@dataclass
class HourlyOverreaction:
    """K5-ovr-01 on one exposure. Day state resets when the bar's trade date changes; the valid
    r values of earlier trade dates carry over (only those a later reference set can use)."""

    root: str
    name: str = field(init=False)
    legs: tuple[LegSpec, ...] = field(init=False)
    trading_windows: dict = field(init=False)
    _leg: LegFacts = field(init=False, repr=False)
    _times: tuple[time, ...] = field(init=False, repr=False)  # the decision times t
    _min_values: int = field(init=False, repr=False)  # the value floor (K5-L-06)
    _t_of_open_bar: dict = field(init=False, repr=False)  # the bar at t-60 -> t
    _t_of_decision_bar: dict = field(init=False, repr=False)  # the bar at t-1 -> t
    _first_day: date | None = field(default=None, init=False, repr=False)
    _day: date | None = field(default=None, init=False, repr=False)
    _opens: dict = field(default_factory=dict, init=False, repr=False)  # t -> (to, id)
    _today: tuple[float, ...] = field(default=(), init=False, repr=False)
    _history: dict = field(default_factory=dict, init=False, repr=False)  # date -> values
    _exit_at: time | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self._leg = leg_facts(self.root)
        self.name = label(MEMBER_ID, self.root)
        self.legs = self._leg.legs
        self._times = decision_times(self._leg.o, self._leg.c)
        self._min_values = min_values(len(self._times))
        self._t_of_open_bar = {shift(t, -SIGNAL_MINUTES): t for t in self._times}
        self._t_of_decision_bar = {shift(t, -DECISION_BAR_BEFORE_T_MIN): t
                                   for t in self._times}
        # S0.12: from O (the first t-60 bar) to the last t + 60 (MGC 13:20, MHG 12:10)
        window_end = shift(self._times[-1], WINDOW_END_AFTER_LAST_T_MIN)
        self.trading_windows = {self.root: (TradingInterval(self._leg.o, window_end),)}

    # -- per trade date ----------------------------------------------------------------
    def _roll(self, day: date) -> None:
        """File the ending trade date's values, keep only dates a reference set can still
        use (reference sets only move forward), then start ``day``."""
        if self._first_day is None:
            self._first_day = day  # K4-L-09: the first bar this member received in the run
        merged = (self._history if self._day is None
                  else {**self._history, self._day: self._today})
        refs = reference_dates(day)
        oldest = refs[0] if refs else day
        self._history = {d: v for d, v in merged.items() if d >= oldest}
        self._day, self._opens, self._today, self._exit_at = day, {}, (), None

    def _signal(self, t: time, bar: Any) -> float | None:
        """r(t) from the recorded bar at t-60 and ``bar``, the bar at t-1; None when the bar at
        t-60 is missing, the two carry different instrument_ids, or its open is <= 0 (C10)."""
        first = self._opens.get(t)
        if first is None:
            return None
        open_ticks, open_id = first
        if open_id != bar.instrument_id:
            return None
        return hourly_return(open_ticks, to_ticks(bar.close, self._leg.tick))

    def _entry_side(self, r: float | None, bar: Any) -> str | None:
        if bar.early_halt_ct is not None:
            return None  # an early-halt trade date is not traded (S0.8)
        if r is None:
            return None  # the signal bars fail (missing, two ids, C10)
        refs = reference_dates(self._day)
        if len(refs) < REFERENCE_DATES or self._first_day is None or refs[0] < self._first_day:
            return None  # warm-up (K4-L-09)
        values = [v for d in refs for v in self._history.get(d, ())]
        if len(values) < self._min_values:
            return None  # too few reference values (K4-L-08, K5-L-06)
        return percentile_side(r, values)

    # -- the member contract -----------------------------------------------------------
    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> Sequence[LegIntent | Refusal]:
        bar = view.bar(self.root)
        if bar is None:  # no bar: no decision at this minute (never forward fill)
            return ()
        if bar.trade_date != self._day:
            self._roll(bar.trade_date)
        day = bar.trade_date
        opened = ct_open(bar)
        if opened.date() != day:
            return ()  # the previous CT evening's bars: nothing of day d happens there
        at = opened.time()
        t_open = self._t_of_open_bar.get(at)
        if t_open is not None:  # the bar at t-60: its open, in ticks (name `open` is banned)
            first = (to_ticks(asdict(bar)["open"], self._leg.tick), bar.instrument_id)
            self._opens = {**self._opens, t_open: first}
        t = self._t_of_decision_bar.get(at)
        r = None if t is None else self._signal(t, bar)
        if r is not None:  # every valid r(t) is a future reference value, traded or not
            self._today = (*self._today, r)
        if account.position(self.root):
            if self._exit_at is None:
                return ()
            return exit_if_due(view, account, self.root, opened, day, self._exit_at)
        if t is None or not is_flat(account, self.root):
            return ()
        side = self._entry_side(r, bar)
        if side is None:
            return ()
        self._exit_at = shift(t, EXIT_AFTER_T_MIN)
        return (leg_market_intent(view, self.root, side, self._leg.q),)


def make_mgc() -> HourlyOverreaction:
    return HourlyOverreaction("MGC")


def make_mhg() -> HourlyOverreaction:
    return HourlyOverreaction("MHG")


__all__ = ["MEMBER_ID", "HourlyOverreaction", "decision_times", "hourly_return", "make_mgc",
           "make_mhg", "min_values", "percentile_side", "reference_dates"]
