"""Shared pieces of the three K5 event members (Stage E.4 Part 2 Task 2, MemberCoder-B).

Imported only by strategy.members.k5.preauc, pmfix and fomc. Specs:
reports/stage_e4b_member_specs.md S0.3-S0.10 and sections 4-6 (structure copied from K4's event
helpers, never imported from them).

- The clock (S0.4, E.3-L-03): "the bar at hh:mm" of trade date d is the bar with trade_date d
  whose open is hh:mm:00 CT on CT calendar date d. Every named bar is found by its exact UTC open
  instant.
- Entries (S0.6, E.3-L-04): only on the named entry decision bar; if it is missing, no entry that
  day; at most one entry per trade date, never while a position or a pending order exists.
- Exits (S0.7, E.3-L-22): on the first present bar at or after the named exit bar, while the
  position is open and no exit is pending; a refused exit is sent again on the next present bar.
  If the engine closes the position itself (D9.7, the flatten), the member sees a flat account
  and sends nothing more that trade date.
- Early halt (S0.8, E.3-L-11): no entry when the entry decision bar carries early_halt_ct.
- Size (S0.3): q_c from the frozen vehicle table; every exit closes the whole position.
- Prices (S0.10, E.3-L-19): integer vendor ticks, round(price / vendor_tick).
- SignedMoveEvent: the one rule K5-pmfix-01 and K5-fomc-01 share (sections 5 and 6): s = ticks of
  the close of the entry decision bar minus ticks of the close of an earlier signal bar, both
  present with one instrument_id (S0.9); s > 0 BUY, s < 0 SELL, s = 0 no trade; market intent on
  the entry decision bar; exit on the first present bar at or after the named exit bar.
A single-leg member is called only at minutes where its leg has a bar (the engine's grid is the
union of the member's legs' bar minutes); a None bar is still handled (no decision, no fill-in).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time
from decimal import Decimal
from zoneinfo import ZoneInfo

from rules.products import product
from rules.xfa_rules import Refusal
from screening.stage_e_frozen import load_frozen_tables
from strategy.stage_e.interface import (
    LegIntent,
    MemberAccountView,
    MinuteView,
    leg_market_intent,
)

CT = ZoneInfo("America/Chicago")
NS_PER_S = 1_000_000_000
MINUTES_PER_HOUR = 60
MINUTES_PER_DAY = 24 * MINUTES_PER_HOUR
BUY, SELL = "buy", "sell"

# A signed-move trade date's plan, CT clock minutes of date d: (the earlier signal bar, the entry
# decision bar = the later signal bar, the named exit decision bar).
SignalPlan = tuple[int, int, int]
# One captured signal bar: (close in integer ticks, instrument_id).
Capture = tuple[int, int]


def clock_minute(at: time | str) -> int:
    """The CT clock minute of the day of a time or an "HH:MM" text."""
    if isinstance(at, str):
        hours, minutes = at.split(":")
        return int(hours) * MINUTES_PER_HOUR + int(minutes)
    return at.hour * MINUTES_PER_HOUR + at.minute


def ct_open_ns(day: date, minute: int) -> int:
    """UTC ns of the open of the bar at CT clock minute ``minute`` of CT calendar date ``day``."""
    if not 0 <= minute < MINUTES_PER_DAY:
        raise ValueError(f"clock minute {minute} is not on CT date {day}")
    local = datetime.combine(day, time(minute // MINUTES_PER_HOUR, minute % MINUTES_PER_HOUR),
                             tzinfo=CT)
    return int(local.astimezone(UTC).timestamp()) * NS_PER_S


def price_ticks(price: float, tick: Decimal) -> int:
    """A vendor price in integer vendor ticks (S0.10)."""
    return round(Decimal(repr(price)) / tick)


def exit_items(view: MinuteView, account: MemberAccountView, root: str, exit_ns: int | None
               ) -> tuple[LegIntent | Refusal, ...]:
    """S0.7 and E.3-L-22: one market intent closing the whole position on the first present bar
    at or after the named exit bar, while the position is open and no exit is pending."""
    bar = view.bar(root)
    position = account.position(root)
    if bar is None or not position or exit_ns is None or bar.ts_event_ns < exit_ns:
        return ()
    pending = account.pending.get(root, 0)
    if pending and (pending > 0) != (position > 0):
        return ()  # an exit (or the engine's own flatten or D9.7 exit) is already pending
    side = SELL if position > 0 else BUY
    return (leg_market_intent(view, root, side, abs(position)),)


def check_exposure(root: str, allowed: Sequence[str], member_id: str) -> None:
    if root not in allowed:
        raise ValueError(f"{member_id} does not trade {root!r} (exposures {tuple(allowed)})")


@dataclass
class SignedMoveEvent:
    """The shared rule of K5-pmfix-01 and K5-fomc-01 on one traded leg, one plan per event date
    (a date without a plan is not traded)."""

    root: str
    plans: Mapping[date, SignalPlan]
    _q: int = field(init=False)
    _tick: Decimal = field(init=False)
    _day: date | None = field(default=None, init=False)
    _start_ns: int | None = field(default=None, init=False)
    _entry_ns: int | None = field(default=None, init=False)
    _exit_ns: int | None = field(default=None, init=False)
    _start: Capture | None = field(default=None, init=False)
    _entry_done: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        self._q = load_frozen_tables().vehicles[self.root].q_c  # S0.3
        self._tick = product(self.root).vendor_tick  # S0.10

    def _new_day(self, day: date) -> None:
        plan = self.plans.get(day)
        self._day = day
        self._entry_done = False
        self._start = None
        self._start_ns = None if plan is None else ct_open_ns(day, plan[0])
        self._entry_ns = None if plan is None else ct_open_ns(day, plan[1])
        self._exit_ns = None if plan is None else ct_open_ns(day, plan[2])

    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> tuple[LegIntent | Refusal, ...]:
        bar = view.bar(self.root)
        if bar is None:  # no bar: no decision at this minute (never forward fill)
            return ()
        if bar.trade_date != self._day:
            self._new_day(bar.trade_date)
        if bar.ts_event_ns == self._start_ns:
            self._start = (price_ticks(bar.close, self._tick), bar.instrument_id)
        if account.position(self.root):
            return exit_items(view, account, self.root, self._exit_ns)
        if self._entry_done or bar.ts_event_ns != self._entry_ns:
            return ()
        self._entry_done = True  # the named entry bar is exact: one chance per trade date
        if account.pending.get(self.root, 0) or bar.early_halt_ct is not None:
            return ()
        start = self._start
        if start is None:
            return ()  # the earlier signal bar is missing
        if start[1] != bar.instrument_id:
            return ()  # the two signal bars span two contracts (S0.9)
        s = price_ticks(bar.close, self._tick) - start[0]
        if s == 0:
            return ()  # s = 0: no trade
        return (leg_market_intent(view, self.root, BUY if s > 0 else SELL, self._q),)


__all__ = [
    "BUY", "CT", "MINUTES_PER_DAY", "NS_PER_S", "SELL", "Capture", "SignalPlan",
    "SignedMoveEvent", "check_exposure", "clock_minute", "ct_open_ns", "exit_items",
    "price_ticks",
]
