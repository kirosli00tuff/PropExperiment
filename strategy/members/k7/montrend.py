"""K7-montrend-01: Sunday-evening hourly time-series momentum on the Monday trade date
(Stage E.6; reports/stage_e6_member_specs.md section 6; catalog reports/stage_e0_catalog_K7.md
lines 595-694; readings K7-L-01, K7-L-03, K7-L-06, K7-L-07).

Rule (every clock time CT; S0.4, K7-L-01):
- Dates: trade dates d that are Mondays, in CRYPTO_FULL_SESSIONS and not in VENDOR_DEGRADED
  (S0.8). A booked-forward Monday is not a trade date (its bars carry Tuesday's trade date) and
  does not trade.
- Bars read: only bars with trade_date d opening at or after Sunday (CT date d-1) 17:00 and at or
  before Monday (CT date d) 13:59, each identified by CT date and clock. Weekend bars that carry
  Monday's trade date (from 2026-06-01) are never read.
- 20 decision times t: Sunday 18:00, 19:00, ..., 23:00; Monday 00:00, 01:00, ..., 13:00.
- Signal: s_t = sign(close of the bar at t - 1 min - open of the bar at t - 60 min), in ticks;
  0 if either bar is missing or they carry different instrument_ids.
- Flatten: at the close of the bar at t - 1 min, if a position is open and its sign differs from
  s_t (s_t = 0 included), a flatten intent on that bar (fills at the open of t); if that bar is
  missing, on the first later present bar, with s_t = 0. Hold if the signs are equal.
- Entry: on the bar at t, if s_t is nonzero, the account is flat (no position, no pending order)
  and the bar at t exists and carries the signal bars' instrument_id, an entry intent of q in
  direction s_t (fills at t + 1 min) (S0.6, S0.9, K7-L-06).
- Final exit: market intent on Monday's 13:59 bar, filling at the 14:00 open; if missing, the
  first later present bar (S0.7).
- A position the engine closes leaves the account flat; later decisions apply as written
  (K7-L-07). At most 20 entries a trade date.
The rule itself is strategy.members.k7._event_common.DecisionBook with direction +1.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date, time
from decimal import Decimal

from rules.xfa_rules import Refusal
from strategy.members.k7._event_common import (
    MINUTES_PER_DAY,
    ROOT,
    DaySchedule,
    Decision,
    DecisionBook,
    clock_minute,
    clock_of,
    ct_open_ns,
    is_entry_date,
    label,
    leg_facts,
)
from strategy.stage_e.interface import (
    LegIntent,
    LegSpec,
    MemberAccountView,
    MinuteView,
    TradingInterval,
)

MEMBER_ID = "K7-montrend-01"
MONDAY = 0  # date.weekday()
SUNDAY_OFFSET_DAYS = -1  # Sunday is CT date d-1 of the Monday trade date d
FIRST_DECISION = (SUNDAY_OFFSET_DAYS, time(18, 0))  # Sunday 18:00
LAST_DECISION = (0, time(13, 0))  # Monday 13:00
STEP_MINUTES = 60
LOOKBACK_MINUTES = 60  # the signal opens at the bar at t - 60
SIGNAL_END_BEFORE_T_MIN = 1  # the signal closes at, and orders are decided on, the bar at t - 1
FLAT_AT = (0, time(14, 0))  # Monday 14:00: the final exit fills at this open
FINAL_EXIT_BEFORE_FLAT_MIN = 1  # the final exit goes on the 13:59 bar
DIRECTION = 1  # momentum: the target is s_t


def _minute(offset_days: int, at: time) -> int:
    """Minutes from 00:00 of CT date d (negative: CT date d-1)."""
    return offset_days * MINUTES_PER_DAY + clock_minute(at)


def decision_minutes() -> tuple[int, ...]:
    """The 20 decision times t, as minutes from 00:00 of CT date d, in time order."""
    return tuple(range(_minute(*FIRST_DECISION), _minute(*LAST_DECISION) + 1, STEP_MINUTES))


def day_schedule(day: date) -> DaySchedule:
    """The decisions and the final exit bar of the Monday trade date ``day``."""
    decisions = tuple(Decision(ct_open_ns(day, t - LOOKBACK_MINUTES),
                               ct_open_ns(day, t - SIGNAL_END_BEFORE_T_MIN),
                               ct_open_ns(day, t)) for t in decision_minutes())
    return DaySchedule(decisions,
                       ct_open_ns(day, _minute(*FLAT_AT) - FINAL_EXIT_BEFORE_FLAT_MIN))


def is_trade_day(day: date) -> bool:
    return day.weekday() == MONDAY and is_entry_date(day)


@dataclass
class MondayTrend:
    """K7-montrend-01 on MBT. Day state resets when the bar's trade date changes."""

    root: str = field(default=ROOT, init=False)
    name: str = field(init=False)
    legs: tuple[LegSpec, ...] = field(init=False)
    trading_windows: dict = field(init=False)
    _q: int = field(init=False, repr=False)
    _tick: Decimal = field(init=False, repr=False)
    _day: date | None = field(default=None, init=False, repr=False)
    _book: DecisionBook | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        leg = leg_facts()
        self._q, self._tick = leg.q, leg.tick
        self.name = label(MEMBER_ID)
        self.legs = leg.legs
        start = decision_minutes()[0] - LOOKBACK_MINUTES  # Sunday 17:00
        self.trading_windows = {self.root: (TradingInterval(
            clock_of(start % MINUTES_PER_DAY), FLAT_AT[1], start // MINUTES_PER_DAY, FLAT_AT[0]),)}

    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> Sequence[LegIntent | Refusal]:
        bar = view.bar(self.root)
        if bar is None:  # no bar: no decision at this minute (never forward fill)
            return ()
        if bar.trade_date != self._day:
            self._day = bar.trade_date
            self._book = None
            if is_trade_day(self._day):
                self._book = DecisionBook(day_schedule(self._day), DIRECTION, self._q,
                                          self._tick, self.root)
        if self._book is None:
            return ()
        # The book reads prices only of the bars at its named instants, all at or after Sunday
        # 17:00 CT; an earlier bar (a weekend bar with Monday's trade date) is never read.
        return self._book.on_bar(view, account, bar)


def make_mbt() -> MondayTrend:
    return MondayTrend()


__all__ = ["MEMBER_ID", "MondayTrend", "day_schedule", "decision_minutes", "is_trade_day",
           "make_mbt"]
