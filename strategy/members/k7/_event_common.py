"""Shared pieces of the three new K7 members (Stage E.6 Task 2, MemberCoder-B): K7-expiry-01,
K7-rev2h-01 and K7-montrend-01 on bitcoin MBT (reports/stage_e6_member_specs.md section 0,
sections 4-6, readings K7-L-01..K7-L-09). Structure copied from strategy/members/k4/
_event_common.py and _port_common.py (Stage E.4), never imported from them; nothing here is shared
with coder A's port helpers.

- Clock (S0.4, K7-L-01): "the bar at hh:mm" is identified by CT calendar date AND clock, through
  its exact UTC open instant (``ct_open_ns``), and by ``trade_date``. MBT bars carry CME's trade
  date (weekends from 2026-06-01 and the booked-forward holidays' sessions carry a later trade
  date), so a bar is never matched by trade_date and clock alone.
- Entry dates (S0.8): a trade date in CRYPTO_FULL_SESSIONS and not in VENDOR_DEGRADED.
- Size (S0.3): q_c from the frozen vehicle table; every exit closes the whole position.
- Prices (S0.10): integer vendor ticks, round(price / vendor_tick).
- Exits and flattens (S0.7, E.3-L-22): sent on a present bar while the position is non-zero and
  nothing is pending on the leg, so a refused one is sent again on the next present bar and an
  engine-forced one (pending until it fills) is never duplicated.
- ``DecisionBook``: the decision rule rev2h and montrend share (sections 5 and 6, K7-L-06..08).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict, dataclass, field
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from typing import Any
from zoneinfo import ZoneInfo

from rules.products import product
from rules.xfa_rules import Refusal
from screening.stage_e_frozen import load_frozen_tables
from strategy.members.k7._calendar import CRYPTO_FULL_SESSIONS, VENDOR_DEGRADED
from strategy.stage_e.interface import (
    LegIntent,
    LegSpec,
    MemberAccountView,
    MinuteView,
    leg_market_intent,
)

CT = ZoneInfo("America/Chicago")
ROOT = "MBT"  # S0.1: bitcoin's only vehicle
NS_PER_S = 1_000_000_000
MINUTES_PER_HOUR = 60
MINUTES_PER_DAY = 24 * MINUTES_PER_HOUR
BUY, SELL = "buy", "sell"
FILL_DELAY_MIN = 1  # C2: a market intent on the bar at X fills at the open of the bar at X + 1

# S0.8: the trade dates on which a new K7 member may enter
ENTRY_DATES: frozenset[date] = frozenset(
    date.fromisoformat(d) for d in CRYPTO_FULL_SESSIONS if d not in frozenset(VENDOR_DEGRADED))


@dataclass(frozen=True)
class LegFacts:
    """The frozen values of the one traded leg (S0.3, S0.4, S0.10)."""

    root: str
    o: time  # D6's O, from the frozen day_session_ct table
    c: time  # D6's C, from the frozen day_session_ct table
    q: int  # q_c of the vehicle, from the frozen vehicle table
    tick: Decimal  # rules.products vendor tick

    @property
    def legs(self) -> tuple[LegSpec, ...]:
        return (LegSpec(self.root, True),)


def leg_facts() -> LegFacts:
    tables = load_frozen_tables()
    o, c = tables.day_session_ct[ROOT]
    return LegFacts(ROOT, o, c, tables.vehicles[ROOT].q_c, product(ROOT).vendor_tick)


def label(member_id: str) -> str:
    """S0.2: the declaration label, which is also the member object's ``name``."""
    return f"{member_id} {ROOT}"


def is_entry_date(day: date) -> bool:
    return day in ENTRY_DATES


def clock_minute(at: time | str) -> int:
    """The CT clock minute of the day of a time or an "HH:MM" text."""
    if isinstance(at, str):
        hours, minutes = at.split(":")
        return int(hours) * MINUTES_PER_HOUR + int(minutes)
    return at.hour * MINUTES_PER_HOUR + at.minute


def clock_of(minute: int) -> time:
    """The clock time of a minute of the day (0 <= minute < 1440; time() refuses others)."""
    return time(minute // MINUTES_PER_HOUR, minute % MINUTES_PER_HOUR)


def ct_open_ns(day: date, minute: int) -> int:
    """UTC ns of the open of the bar at CT minute ``minute`` counted from 00:00 of CT calendar
    date ``day``; a negative minute is on the previous CT calendar date (-420 = 17:00 of d-1)."""
    if not -MINUTES_PER_DAY <= minute < MINUTES_PER_DAY:
        raise ValueError(f"minute {minute} is not on CT date {day} or the day before")
    on = day + timedelta(days=minute // MINUTES_PER_DAY)
    m = minute % MINUTES_PER_DAY
    local = datetime.combine(on, time(m // MINUTES_PER_HOUR, m % MINUTES_PER_HOUR), tzinfo=CT)
    return int(local.astimezone(UTC).timestamp()) * NS_PER_S


def to_ticks(price: float, tick: Decimal) -> int:
    """S0.10: round(price / vendor_tick), computed exactly in Decimal."""
    return round(Decimal(repr(price)) / tick)


def open_ticks(bar: Any, tick: Decimal) -> int:
    """The bar's open in ticks (the attribute's name is a banned name for member code)."""
    return to_ticks(asdict(bar)["open"], tick)


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


# ------------------------------------------------------------- the decision book ----
@dataclass(frozen=True)
class Decision:
    """One decision time t: the signal runs from the open of the bar at ``start_ns`` to the close
    of the bar at ``end_ns`` (t - 1 min); orders are decided at that close; the entry intent goes
    on the decision-time bar at ``entry_ns`` (t)."""

    start_ns: int
    end_ns: int
    entry_ns: int


@dataclass(frozen=True)
class DaySchedule:
    """One trade date's decisions (in time order) and its final exit bar."""

    decisions: tuple[Decision, ...]
    final_exit_ns: int  # the final exit is sent on the first present bar at or after this bar


@dataclass
class DecisionBook:
    """The rule rev2h (section 5) and montrend (section 6) share, for one trade date.

    ``direction`` +1 follows the signal (montrend: s_t), -1 reverses it (rev2h: -sign(r)). At the
    close of the bar at t - 1 min the decision's target sign is fixed: 0 when that bar or the
    start bar is missing or the two carry different instrument_ids (S0.9), else direction x
    sign(close - open) in ticks. A decision whose t - 1 bar is missing is taken, with target 0, at
    the first later present bar (K7-L-08). From then on the position is flattened on every present
    bar where it is open with another sign than the target (hold when equal; S0.7), and on the
    decision-time bar an entry of q in the target's direction is sent only if the target is
    nonzero, the account is flat and that bar carries the signal bars' instrument_id (S0.6, S0.9,
    K7-L-06; the entry bar's id gates only the entry: flattens and holds are unguarded). The
    final exit closes the position on the first present bar at or after the final exit bar."""

    schedule: DaySchedule
    direction: int
    q: int
    tick: Decimal
    root: str
    _start_index: dict = field(default_factory=dict, init=False)  # start bar ns -> index
    _starts: dict = field(default_factory=dict, init=False)  # decision index -> (ticks, id)
    _next: int = field(default=0, init=False)  # the first decision not yet taken
    _target: int = field(default=0, init=False)  # the last decision's target sign (flat before)
    _entry: tuple[int, int, int] | None = field(default=None, init=False)  # (index, sign, id)

    def __post_init__(self) -> None:
        self._start_index = {d.start_ns: i for i, d in enumerate(self.schedule.decisions)}

    def _take_missed(self, ts: int) -> None:
        decisions = self.schedule.decisions
        while self._next < len(decisions) and decisions[self._next].end_ns < ts:
            self._target = 0  # its t - 1 bar is missing: target 0 (and no entry, below)
            self._next += 1

    def _observe(self, bar: Any) -> None:
        ts = bar.ts_event_ns
        i = self._start_index.get(ts)
        if i is not None and i >= self._next:
            self._starts = {**self._starts, i: (open_ticks(bar, self.tick), bar.instrument_id)}
        if self._next >= len(self.schedule.decisions):
            return
        if self.schedule.decisions[self._next].end_ns != ts:
            return
        start = self._starts.get(self._next)
        if start is None or start[1] != bar.instrument_id:
            target = 0
        else:
            target = self.direction * sign(to_ticks(bar.close, self.tick) - start[0])
        self._target = target
        self._entry = (self._next, target, bar.instrument_id)
        self._next += 1

    def on_bar(self, view: MinuteView, account: MemberAccountView, bar: Any
               ) -> Sequence[LegIntent | Refusal]:
        ts = bar.ts_event_ns
        self._take_missed(ts)
        self._observe(bar)
        position = account.position(self.root)
        if position:
            if ts >= self.schedule.final_exit_ns or sign(position) != self._target:
                return close_items(view, account, self.root)
            return ()
        if self._entry is None:
            return ()
        index, target, signal_id = self._entry  # the last decision taken at its t - 1 bar
        if (target == 0 or ts != self.schedule.decisions[index].entry_ns
                or bar.instrument_id != signal_id or not is_flat(account, self.root)):
            return ()  # the entry goes on that decision's exact t bar only: once (S0.6)
        return (leg_market_intent(view, self.root, BUY if target > 0 else SELL, self.q),)


__all__ = [
    "BUY", "CT", "ENTRY_DATES", "FILL_DELAY_MIN", "MINUTES_PER_DAY", "NS_PER_S", "ROOT", "SELL",
    "DaySchedule", "Decision", "DecisionBook", "LegFacts", "clock_minute", "clock_of",
    "close_items",
    "ct_open_ns", "is_entry_date", "is_flat", "label", "leg_facts", "open_ticks", "sign",
    "to_ticks",
]
