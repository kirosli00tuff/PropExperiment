"""Shared pieces of K1's two new members (Stage E.7 Task 2, MemberCoder-B): K1-vxnband-01 and
K1-vwap-01 on Nasdaq-100 MNQ (reports/stage_e7_member_specs.md section 0, sections 4-5, readings
K1-L-01..K1-L-11). Structure copied from strategy/members/k7/_event_common.py (Stage E.6), never
imported from it; nothing here is shared with coder A's port helpers.

- Clock (S0.4, K7-L-01): "the bar at hh:mm" of trade date d is the bar with trade_date d whose
  open (ts_event_ns) is hh:mm:00 CT on CT calendar date d; a member reads only bars of CT date d.
  In the equity calendar this agrees with the bars' trade_date.
- Entry dates (S0.8, K1-L-10): a trade date in EQUITY_FULL_SESSIONS. "Trade date d-1"
  (K1-L-02): the EQUITY_TRADE_DATES entry immediately before d.
- Size (S0.3): q_c from the frozen vehicle table; every exit closes the whole position.
- Prices (S0.10): integer vendor ticks, round(price / vendor_tick), in Decimal.
- Missing bars (S0.4, C4): detected by clock, from the previous present bar's open (``ClockRun``),
  never from the call sequence.
- Exits (S0.7, E.3-L-22): sent on a present bar while the position is non-zero and nothing is
  pending on the leg, so a refused one is sent again on the next present bar and an
  engine-forced one (pending until it fills) is never duplicated.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time
from decimal import Decimal
from typing import Any
from zoneinfo import ZoneInfo

from rules.products import product
from rules.xfa_rules import Refusal
from screening.stage_e_frozen import load_frozen_tables
from strategy.members.k1._calendar import EQUITY_FULL_SESSIONS, EQUITY_TRADE_DATES
from strategy.stage_e.interface import (
    LegIntent,
    LegSpec,
    MemberAccountView,
    MinuteView,
    leg_market_intent,
)

CT = ZoneInfo("America/Chicago")
ROOT = "MNQ"  # S0.1: K1-vxnband-01 and K1-vwap-01 trade the Nasdaq-100 vehicle only
NS_PER_S = 1_000_000_000
NS_PER_MINUTE = 60 * NS_PER_S
MINUTES_PER_HOUR = 60
BUY, SELL = "buy", "sell"

# S0.8 / K1-L-10: the trade dates on which the two new members may enter
FULL_SESSIONS: frozenset[date] = frozenset(date.fromisoformat(d) for d in EQUITY_FULL_SESSIONS)
_TRADE_DATES: tuple[date, ...] = tuple(date.fromisoformat(d) for d in EQUITY_TRADE_DATES)
# K1-L-02: trade date d -> the EQUITY_TRADE_DATES entry immediately before it
PREVIOUS_TRADE_DATE: dict[date, date] = dict(zip(_TRADE_DATES[1:], _TRADE_DATES[:-1],
                                                 strict=True))


@dataclass(frozen=True)
class LegFacts:
    """The frozen values of the one traded leg (S0.3, S0.4, S0.10)."""

    root: str
    o: time  # D6's O, from the frozen day_session_ct table (MNQ 08:30)
    c: time  # D6's C, from the frozen day_session_ct table (MNQ 15:00)
    q: int  # q_c of the vehicle, from the frozen vehicle table (MNQ 1)
    tick: Decimal  # rules.products vendor tick (MNQ 0.25)

    @property
    def legs(self) -> tuple[LegSpec, ...]:
        return (LegSpec(self.root, True),)  # S0.1: one traded leg, no signal legs


def leg_facts() -> LegFacts:
    tables = load_frozen_tables()
    o, c = tables.day_session_ct[ROOT]
    return LegFacts(ROOT, o, c, tables.vehicles[ROOT].q_c, product(ROOT).vendor_tick)


def label(member_id: str) -> str:
    """S0.2: the declaration label, which is also the member object's ``name``."""
    return f"{member_id} {ROOT}"


def is_full_session(day: date) -> bool:
    return day in FULL_SESSIONS


def ct_open(bar: Any) -> datetime:
    """The bar's open (``ts_event_ns``, integer seconds: bars sit on the minute) in CT."""
    return datetime.fromtimestamp(bar.ts_event_ns // NS_PER_S, tz=UTC).astimezone(CT)


def clock_minute(at: time) -> int:
    """The CT clock minute of the day of a time (08:30 -> 510)."""
    return at.hour * MINUTES_PER_HOUR + at.minute


def to_ticks(price: float, tick: Decimal) -> int:
    """S0.10: round(price / vendor_tick), computed exactly in Decimal."""
    return round(Decimal(repr(price)) / tick)


def sign(value: int) -> int:
    return (value > 0) - (value < 0)


def is_flat(account: MemberAccountView, root: str) -> bool:
    return account.position(root) == 0 and not account.pending.get(root, 0)


def close_items(view: MinuteView, account: MemberAccountView, root: str
                ) -> tuple[LegIntent | Refusal, ...]:
    """One market intent closing the whole position, unless flat or an order is pending."""
    position = account.position(root)
    if position == 0 or account.pending.get(root, 0):
        return ()
    return (leg_market_intent(view, root, SELL if position > 0 else BUY, abs(position)),)


@dataclass
class ClockRun:
    """C4 by clock: whether every CT minute from ``start`` through the latest present bar of the
    day has a bar. Feed it the minute of each present bar at or after ``start``, in order."""

    start: int
    _last: int | None = field(default=None, init=False)
    _broken: bool = field(default=False, init=False)

    def see(self, minute: int) -> bool:
        """Record the present bar at ``minute``; True while no minute of [start, minute] lacks a
        bar (a first bar later than ``start`` is a gap at the start)."""
        expected = self.start if self._last is None else self._last + 1
        if minute != expected:
            self._broken = True
        self._last = minute
        return not self._broken


__all__ = [
    "BUY", "CT", "FULL_SESSIONS", "NS_PER_MINUTE", "NS_PER_S", "PREVIOUS_TRADE_DATE", "ROOT",
    "SELL", "ClockRun", "LegFacts", "clock_minute", "close_items", "ct_open", "is_flat",
    "is_full_session", "label", "leg_facts", "sign", "to_ticks",
]
