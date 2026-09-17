"""Strategy interface: the frozen contract Stage D.1 builds against (Stage C, Task 1).

A strategy sees exactly two things per bar, both frozen: the COMPLETED bar
(``Bar``) and a point-in-time snapshot of its account (``AccountView``). It
returns zero or more ``rules.xfa_rules.OrderIntent``. That is the same frozen,
refuse-at-construction type the rules gate consumes, so no translation layer
sits between a strategy and ``rules.xfa_rules.check_order``. A strategy may
also pass back the ``Refusal`` that ``construct_intent`` returned; the engine
logs it and drops it.

Shape follows ``rules/xfa_rules.py``: frozen dataclasses, a single blessed
constructor that returns the object or a named ``Refusal`` (``construct_bar``),
and no mutable state crossing the boundary.

Timing contract. ``sim/engine.py`` enforces every line of this; none of it is
taken on trust:
1. ``on_bar(bar N)`` runs only after bar N has closed, at
   ``bar.decision_ts_utc`` = bar open + 60 s. The engine pulls bars from a
   one-way iterator and never has bar N+1 in hand at that moment.
2. Every intent must carry ``ts_utc == bar.decision_ts_utc`` exactly. Use
   ``market_intent``. Backdated or future-dated intents are refused.
3. An accepted intent is a market order. It fills at the NEXT bar's open
   (``sim/fill_model.py``), never at a price the strategy has already seen.
4. The engine structurally refuses intents on bars ``in_scheduled_closure`` or
   ``in_flatten_window``, and in roll-blackout sessions. The rules gate refuses
   new exposure from 15:08 CT and above the Scaling Plan limit.

Field availability (point-in-time audit). Every ``Bar`` field is classified in
``BAR_FIELD_AVAILABILITY``, and ``tests/test_leakage_canaries.py`` fails if a
field is added without a class:
- ``bar_close``: known once this bar has closed.
- ``calendar``: known in advance from the exchange/Topstep calendar.
  ``is_roll_session`` comes from the vendor's volume-ranked roll schedule.
  Databento's live API serves volume-ranked continuous symbols, so the mapping
  resolves in real time, but its docs do not state the ranking inputs; a live
  bot would use its own published roll calendar instead.
- ``hindsight``: NOT knowable in real time. ``vendor_degraded_day`` is
  Databento's after-the-fact data-quality verdict (the 2025-11-28 entry was
  last modified 2026-08-27). The field stays on ``Bar`` because the engine and
  the reports use it, but ``sim.engine`` BLANKS every hindsight field in the
  copy a strategy receives (``EngineConfig.mask_hindsight_fields``, on by
  default), so a strategy cannot condition on it even by accident. The engine
  never gates trading on it either: that would silently delete the CME outage
  day of 2025-11-28 from every backtest.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, time
from typing import Protocol, runtime_checkable

from rules.xfa_rules import (
    MES_SYMBOL,
    MES_TICK_SIZE,
    OrderIntent,
    Phase,
    Refusal,
    Status,
    construct_intent,
)

INTERFACE_VERSION = 1
NS_PER_S = 1_000_000_000
BAR_SECONDS = 60
NS_PER_BAR = BAR_SECONDS * NS_PER_S


@dataclass(frozen=True, slots=True)
class Bar:
    """One completed 1-minute MES bar with its Stage A.1 flag columns."""

    ts_event_ns: int  # bar OPEN, UTC ns, on Databento's receive clock (ts_recv buckets)
    open: float
    high: float
    low: float
    close: float
    volume: int
    instrument_id: int
    raw_symbol: str
    trade_date: date
    in_flatten_window: bool
    in_no_new_positions_window: bool
    early_halt_ct: time | None
    in_scheduled_closure: bool
    is_roll_session: bool
    gap_before_minutes: int
    vendor_degraded_day: bool

    @property
    def decision_ts_ns(self) -> int:
        """The instant the bar is complete; the earliest a strategy may act on it."""
        return self.ts_event_ns + NS_PER_BAR

    @property
    def open_ts_utc(self) -> datetime:
        return datetime.fromtimestamp(self.ts_event_ns / NS_PER_S, tz=UTC)

    @property
    def decision_ts_utc(self) -> datetime:
        return datetime.fromtimestamp(self.decision_ts_ns / NS_PER_S, tz=UTC)


BAR_FIELD_AVAILABILITY: dict[str, str] = {
    "ts_event_ns": "bar_close",
    "open": "bar_close",
    "high": "bar_close",
    "low": "bar_close",
    "close": "bar_close",
    "volume": "bar_close",
    "instrument_id": "bar_close",
    "raw_symbol": "bar_close",
    "trade_date": "calendar",
    "in_flatten_window": "calendar",
    "in_no_new_positions_window": "calendar",
    "early_halt_ct": "calendar",
    "in_scheduled_closure": "calendar",
    "is_roll_session": "calendar",
    "gap_before_minutes": "bar_close",  # counts missing minutes BEFORE this bar only
    "vendor_degraded_day": "hindsight",
}
HINDSIGHT_FIELDS = tuple(k for k, v in BAR_FIELD_AVAILABILITY.items() if v == "hindsight")


def _on_grid(price: float) -> bool:
    ticks = round(price / MES_TICK_SIZE)
    return abs(ticks * MES_TICK_SIZE - price) <= 1e-9


def construct_bar(
    *,
    ts_event_ns: int,
    open: float,  # noqa: A002 — mirrors the bar column name
    high: float,
    low: float,
    close: float,
    volume: int,
    instrument_id: int,
    raw_symbol: str,
    trade_date: date,
    in_flatten_window: bool,
    in_no_new_positions_window: bool,
    early_halt_ct: time | None,
    in_scheduled_closure: bool,
    is_roll_session: bool,
    gap_before_minutes: int,
    vendor_degraded_day: bool,
) -> Bar | Refusal:
    """A bar, or the named construction refusal. Nothing malformed reaches a strategy."""
    if isinstance(ts_event_ns, bool) or not isinstance(ts_event_ns, int) or ts_event_ns <= 0:
        return Refusal("bar_bad_timestamp", f"ts_event_ns {ts_event_ns!r} is not a positive int")
    if ts_event_ns % NS_PER_BAR:
        return Refusal("bar_bad_timestamp", f"ts_event_ns {ts_event_ns} is not on a minute")
    prices = (open, high, low, close)
    if not all(isinstance(p, float | int) and not isinstance(p, bool) for p in prices):
        return Refusal("bar_bad_price", f"prices {prices!r} are not numbers")
    if not all(_on_grid(float(p)) for p in prices):
        return Refusal("bar_off_tick", f"prices {prices!r} are not on the {MES_TICK_SIZE} grid")
    if not (low <= min(open, close) and high >= max(open, close) and low <= high):
        return Refusal("bar_ohlc_inconsistent", f"O/H/L/C {prices!r} are inconsistent")
    if isinstance(volume, bool) or not isinstance(volume, int) or volume < 0:
        return Refusal("bar_bad_volume", f"volume {volume!r} is not a non-negative int")
    if not isinstance(trade_date, date) or isinstance(trade_date, datetime):
        return Refusal("bar_bad_trade_date", f"trade_date {trade_date!r} is not a date")
    if early_halt_ct is not None and not isinstance(early_halt_ct, time):
        return Refusal("bar_bad_early_halt", f"early_halt_ct {early_halt_ct!r} is not a time")
    flags = (in_flatten_window, in_no_new_positions_window, in_scheduled_closure,
             is_roll_session, vendor_degraded_day)
    if not all(isinstance(f, bool) for f in flags):
        return Refusal("bar_bad_flag", f"flags {flags!r} are not all bool")
    if in_flatten_window and not in_no_new_positions_window:
        return Refusal("bar_bad_flag", "in_flatten_window without in_no_new_positions_window")
    if isinstance(gap_before_minutes, bool) or not isinstance(gap_before_minutes, int) or (
        gap_before_minutes < 0
    ):
        return Refusal("bar_bad_gap", f"gap_before_minutes {gap_before_minutes!r} is invalid")
    return Bar(
        ts_event_ns, float(open), float(high), float(low), float(close), volume,
        int(instrument_id), str(raw_symbol), trade_date, in_flatten_window,
        in_no_new_positions_window, early_halt_ct, in_scheduled_closure, is_roll_session,
        gap_before_minutes, vendor_degraded_day,
    )


@dataclass(frozen=True, slots=True)
class AccountView:
    """Point-in-time account snapshot at ``bar.decision_ts_utc``. Built only by the engine."""

    phase: Phase
    status: Status
    trade_date: date
    balance_cents: int  # realized, after every cost booked so far
    mll_floor_cents: int
    prior_session_balance_cents: int  # the Scaling Plan input
    max_position_micros: int
    position_micros: int  # filled, signed (long > 0)
    pending_signed_micros: int  # accepted orders not yet filled
    avg_entry_price: float | None
    unrealized_at_close_cents: int  # open position marked at this bar's close


@runtime_checkable
class Strategy(Protocol):
    """The whole contract. Frozen at ``INTERFACE_VERSION``; change it only with a version bump."""

    name: str

    def on_bar(self, bar: Bar, account: AccountView) -> Sequence[OrderIntent | Refusal]: ...


def market_intent(bar: Bar, side: str, quantity_micros: int) -> OrderIntent | Refusal:
    """The intended way to build an intent: stamped with the bar's decision time."""
    return construct_intent(
        symbol=MES_SYMBOL, side=side, quantity_micros=quantity_micros, ts_utc=bar.decision_ts_utc
    )
