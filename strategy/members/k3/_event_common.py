"""Shared pieces of the five K3 fix members of MemberCoder-B (Stage E.4 Part 3, Task 2).

Imported only by strategy.members.k3.ldnrev, ldnmom, ecbfix, tkypre and tkypost. Specs:
reports/stage_e4c_member_specs.md S0.3-S0.14, sections 4, 5, 7, 8, 9 and 10 (structure copied from
K5's event helpers, never imported from them).

- The clock (S0.4, E.3-L-03): "the bar at hh:mm" on CT calendar date D is the bar whose open is
  hh:mm:00 CT on D (D is trade date d, or d-1 for the CT evening of d-1). Every named bar is found
  by its exact UTC open instant. The fix instants T_L, T_E and T_T are read from the literal
  tables of strategy.members.k3._clocks (K3-L-02); only the CT clock itself (America/Chicago, as in
  the template) turns a CT wall time into UTC. No other time zone is used at run time.
- Event sets (S0.8', K3-L-04): built from the literal tables of strategy.members.k3._calendar on
  trade date d; FX_FULL_SESSIONS carries the early-halt and early-F test (K3-L-11). No bar's
  early_halt_ct is read.
- Entries (S0.6, E.3-L-04): only on the named entry decision bar; if it is missing, no entry at
  that time; at most one entry per trade date (ecbfix: one per leg), never while a position or a
  pending order exists.
- Exits (S0.7, E.3-L-22): on the first present bar at or after the named exit bar, while the
  position is open and no exit is pending; a refused exit is sent again on the next present bar.
  If the engine closes the position itself (D9.7, the flatten), the member sees a flat account and
  makes no further entry that trade date.
- Instrument guard (S0.9, E.3-L-12, K3-L-03): every bar the rule reads at or before the entry
  decision carries the entry decision bar's instrument_id, else no trade; exit bars are not
  guarded.
- Size (S0.3): q_c from the frozen vehicle table; every exit closes the whole position.
- Prices (S0.10, E.3-L-19): integer vendor ticks, round(price / vendor_tick). A bar's open is read
  as dataclasses.asdict(bar)["open"] (the freeze's static check bans the name; R-T2-1).
- FixEvent: the one rule ldnrev, ldnmom, tkypre and tkypost share: per event date a Plan (the
  signal bars read, the entry decision bar, the named exit bar); the side is the member's function
  of the signal bars' integer ticks (None: no trade).
A single-leg member is called only at minutes where its leg has a bar (the engine's grid is the
union of the member's legs' bar minutes); a None bar is still handled (no decision, no fill-in).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass, field
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from typing import Any
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
ONE_DAY = timedelta(days=1)
BUY, SELL = "buy", "sell"
OPEN, CLOSE = "open", "close"  # the bar fields a signal reads

# One signal bar of a plan: (UTC ns of the bar's open, the field read: OPEN or CLOSE).
Read = tuple[int, str]
# The member's side rule: the signal bars' integer ticks, in plan order -> BUY, SELL or None.
SideRule = Callable[[tuple[int, ...]], str | None]


@dataclass(frozen=True)
class Plan:
    """One event date's decision bars, as UTC ns of the bars' opens."""

    reads: tuple[Read, ...]  # the signal bars read at or before the entry decision
    entry_ns: int  # the entry decision bar ("market intent on the bar at X")
    exit_ns: int  # the named exit decision bar


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


def field_ticks(bar: Any, name: str, tick: Decimal) -> int:  # noqa: ANN401 (a Bar)
    """The bar's OPEN or CLOSE in integer vendor ticks (asdict: R-T2-1)."""
    if name not in (OPEN, CLOSE):
        raise ValueError(f"a signal reads a bar's open or close, not {name!r}")
    return price_ticks(asdict(bar)[name], tick)


def iso_dates(days: Sequence[str]) -> frozenset[date]:
    return frozenset(date.fromisoformat(d) for d in days)


def clock_table(rows: Sequence[tuple[str, str]]) -> dict[date, int]:
    """A literal clock table's rows (ISO date, CT "HH:MM") as date -> CT clock minute."""
    return {date.fromisoformat(d): clock_minute(t) for d, t in rows}


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
class FixEvent:
    """The shared rule of ldnrev, ldnmom, tkypre and tkypost on one traded leg, one Plan per
    event date (a trade date without a plan is not traded)."""

    root: str
    plans: Mapping[date, Plan]
    side_of: SideRule
    _q: int = field(init=False)
    _tick: Decimal = field(init=False)
    _day: date | None = field(default=None, init=False)
    _plan: Plan | None = field(default=None, init=False)
    _captured: tuple[tuple[int, int] | None, ...] = field(default=(), init=False)
    _entry_done: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        self._q = load_frozen_tables().vehicles[self.root].q_c  # S0.3
        self._tick = product(self.root).vendor_tick  # S0.10

    def _new_day(self, day: date) -> None:
        self._day = day
        self._plan = self.plans.get(day)
        self._captured = () if self._plan is None else (None,) * len(self._plan.reads)
        self._entry_done = False

    def _capture(self, plan: Plan, bar: Any) -> None:  # noqa: ANN401 (a strategy.interface.Bar)
        """Keep (ticks, instrument_id) of every signal read of ``bar``."""
        self._captured = tuple(
            (field_ticks(bar, name, self._tick), bar.instrument_id)
            if ns == bar.ts_event_ns else got
            for (ns, name), got in zip(plan.reads, self._captured, strict=True))

    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> tuple[LegIntent | Refusal, ...]:
        bar = view.bar(self.root)
        if bar is None:  # no bar: no decision at this minute (never forward fill)
            return ()
        if bar.trade_date != self._day:
            self._new_day(bar.trade_date)
        plan = self._plan
        if plan is None:
            return ()  # not an event date: no entry (and no position can be open)
        if any(ns == bar.ts_event_ns for ns, _ in plan.reads):
            self._capture(plan, bar)
        if account.position(self.root):
            return exit_items(view, account, self.root, plan.exit_ns)
        if self._entry_done or bar.ts_event_ns != plan.entry_ns:
            return ()
        self._entry_done = True  # the named entry bar is exact: one chance per trade date
        if account.pending.get(self.root, 0):
            return ()
        if any(got is None for got in self._captured):
            return ()  # a signal bar is missing (C4)
        if any(got[1] != bar.instrument_id for got in self._captured if got is not None):
            return ()  # the bars read span two contracts (S0.9)
        side = self.side_of(tuple(got[0] for got in self._captured if got is not None))
        if side is None:
            return ()  # a zero signal: no trade
        return (leg_market_intent(view, self.root, side, self._q),)


__all__ = [
    "BUY", "CLOSE", "CT", "MINUTES_PER_DAY", "NS_PER_S", "ONE_DAY", "OPEN", "SELL", "FixEvent",
    "Plan", "Read", "SideRule", "check_exposure", "clock_minute", "clock_table", "ct_open_ns",
    "exit_items", "field_ticks", "iso_dates", "price_ticks",
]
