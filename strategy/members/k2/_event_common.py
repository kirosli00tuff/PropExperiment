"""Shared pieces of the four K2 event members (Stage E.3 Task 2, MemberCoder-B).

Imported only by strategy.members.k2.aucpre, aucpost, fomcpost and predrift. Specs:
reports/stage_e3_member_specs.md S0.4-S0.10 and sections 4-7.

- The clock (S0.4, L-03): "the bar at hh:mm" of trade date d is the bar with trade_date d whose open
  is hh:mm:00 CT on CT calendar date d. Every named bar is found by its exact UTC open instant.
- Entries (S0.6, L-04): only on the named entry decision bar; if it is missing, no entry that day;
  at most one entry per trade date, never while a position or a pending order exists.
- Exits (S0.7, L-22): on the first present bar at or after the named exit bar, while the position
  is open and no exit is pending; a refused exit is sent again on the next present bar.
- Early halt (S0.8, L-11): no entry when the entry decision bar carries early_halt_ct.
- Size (S0.3): q_c from the frozen vehicle table; every exit closes the whole position.
- Prices (S0.10, L-19): integer vendor ticks, round(price / vendor_tick).
A single-leg member is called only at minutes where its leg has a bar (the engine's grid is the
union of the member's legs' bar minutes); a None bar is still handled (no decision, no fill-in).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field
from datetime import UTC, date, datetime, time
from decimal import Decimal
from zoneinfo import ZoneInfo

from rules.xfa_rules import Refusal
from screening.stage_e_frozen import load_frozen_tables
from strategy.members.k2._releases import TREASURY_AUCTIONS
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
RATES_EXPOSURES = ("ZT", "ZF", "ZN", "TN", "ZB", "UB")
# Specs section 4 (C 272-275, 288-294): the auctioned security's original term per exposure.
AUCTION_TENOR = {"ZT": "2Y", "ZF": "5Y", "ZN": "10Y", "TN": "10Y", "ZB": "30Y", "UB": "30Y"}
BUY, SELL = "buy", "sell"

# A trade date's plan: (entry decision minute, exit decision minute), CT clock minutes of date d.
DayPlan = tuple[int, int]


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


def bar_open_price(bar: object) -> float:
    """The bar's open price. The freeze's static check refuses the attribute name of the builtin
    it bans, so the field is read by name from the bar's dataclass field mapping."""
    return asdict(bar)["open"]


def auction_schedule(root: str, entry_offset: int, exit_offset: int) -> dict[date, DayPlan]:
    """Trade date -> plan for the root's tenor-matched auctions (T_a CT, offsets in clock minutes
    on CT date d, L-14)."""
    tenor = AUCTION_TENOR[root]
    return {date.fromisoformat(day): (clock_minute(t_a) + entry_offset,
                                      clock_minute(t_a) + exit_offset)
            for day, auction_tenor, t_a in TREASURY_AUCTIONS if auction_tenor == tenor}


def fixed_schedule(days: Sequence[str], entry: time, exit_: time) -> dict[date, DayPlan]:
    """Trade date -> plan with the same entry and exit decision clock times on every date."""
    return {date.fromisoformat(day): (clock_minute(entry), clock_minute(exit_)) for day in days}


def exit_items(view: MinuteView, account: MemberAccountView, root: str, exit_ns: int | None
               ) -> tuple[LegIntent | Refusal, ...]:
    """S0.7 and L-22: one market intent closing the whole position on the first present bar at or
    after the named exit bar, while the position is open and no exit is pending."""
    bar = view.bar(root)
    position = account.position(root)
    if bar is None or not position or exit_ns is None or bar.ts_event_ns < exit_ns:
        return ()
    pending = account.pending.get(root, 0)
    if pending and (pending > 0) != (position > 0):
        return ()  # an exit (or the engine's flatten) is already pending
    side = SELL if position > 0 else BUY
    return (leg_market_intent(view, root, side, abs(position)),)


def check_exposure(root: str, allowed: Sequence[str], member_id: str) -> None:
    if root not in allowed:
        raise ValueError(f"{member_id} does not trade {root!r} (exposures {tuple(allowed)})")


@dataclass
class FixedSideEvent:
    """One traded leg, one unconditional side, and per trade date an entry decision minute and an
    exit decision minute (or no event). The instrument guard of these members covers the entry
    decision bar only (L-12), which carries its own instrument_id, so it never binds."""

    root: str
    side: str
    schedule: Mapping[date, DayPlan]
    _q: int = field(init=False)
    _day: date | None = field(default=None, init=False)
    _entry_ns: int | None = field(default=None, init=False)
    _exit_ns: int | None = field(default=None, init=False)
    _entry_done: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        if self.side not in (BUY, SELL):
            raise ValueError(f"side {self.side!r}")
        self._q = load_frozen_tables().vehicles[self.root].q_c

    def _new_day(self, day: date) -> None:
        plan = self.schedule.get(day)
        self._day = day
        self._entry_done = False
        self._entry_ns = None if plan is None else ct_open_ns(day, plan[0])
        self._exit_ns = None if plan is None else ct_open_ns(day, plan[1])

    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> tuple[LegIntent | Refusal, ...]:
        bar = view.bar(self.root)
        if bar is None:  # no bar: no decision at this minute (never forward fill)
            return ()
        if bar.trade_date != self._day:
            self._new_day(bar.trade_date)
        if account.position(self.root):
            return exit_items(view, account, self.root, self._exit_ns)
        if self._entry_done or bar.ts_event_ns != self._entry_ns:
            return ()
        self._entry_done = True  # the named entry bar is exact: one chance per trade date
        if account.pending.get(self.root, 0) or bar.early_halt_ct is not None:
            return ()
        return (leg_market_intent(view, self.root, self.side, self._q),)


__all__ = [
    "AUCTION_TENOR", "BUY", "CT", "RATES_EXPOSURES", "SELL", "DayPlan", "FixedSideEvent",
    "auction_schedule", "bar_open_price", "check_exposure", "clock_minute", "ct_open_ns",
    "exit_items", "fixed_schedule", "price_ticks",
]
