"""Shared pieces of K6-limitcont-01, K6-wasdepre-01 and K6-wasdepost-01 (Stage E.8 Task 2,
MemberCoder-B). Imported only by strategy.members.k6.limitcont, wasdepre and wasdepost. Specs:
reports/stage_e8_member_specs.md S0.3-S0.10 and sections 5-7 (structure copied from the K4
event helpers, never imported from them).

- The clock (S0.4, E.3-L-03, K7-L-01): "the bar at hh:mm" of trade date d is the bar with
  trade_date d whose open is hh:mm:00 CT on CT calendar date d. Every named bar is found by its
  exact UTC open instant, so a missing bar is detected by clock, never by the call sequence.
- Entries (S0.6, E.3-L-04): only on the named entry bar; if it is missing, no entry that day; at
  most one entry per trade date, never while a position or a pending order exists.
- Exits (S0.7, E.3-L-22): on the first present bar at or after the named exit bar, while the
  position is open and no exit is pending; a refused exit is sent again on the next present bar.
  If the engine closes the position itself (D9.7, the flatten), the member sees a flat account
  and sends nothing more that trade date.
- Size (S0.3): q_c from the frozen vehicle table; every exit closes the whole position.
- Prices (S0.10, E.3-L-19): integer vendor ticks, round(price / vendor_tick).
A single-leg member is called only at minutes where its leg has a bar (the engine's grid is the
union of the member's legs' bar minutes); a None bar is still handled (no decision, no fill-in).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from typing import Any
from zoneinfo import ZoneInfo

from rules.xfa_rules import Refusal
from strategy.stage_e.interface import (
    LegIntent,
    MemberAccountView,
    MinuteView,
    leg_market_intent,
)

CT = ZoneInfo("America/Chicago")
NS_PER_S = 1_000_000_000
BUY, SELL = "buy", "sell"


def ct_open_ns(day: date, at: time) -> int:
    """UTC ns of the instant ``at`` (CT clock, seconds kept) on CT calendar date ``day``: for a
    whole minute, the open of the bar at that minute."""
    local = datetime.combine(day, at, tzinfo=CT)
    return int(local.astimezone(UTC).timestamp()) * NS_PER_S


def minus_minutes(at: time, minutes: int) -> time:
    """A CT clock time ``minutes`` earlier on the same day."""
    return (datetime.combine(date(2000, 1, 3), at) - timedelta(minutes=minutes)).time()


def bar_open(bar: Any) -> float:  # noqa: ANN401 - a strategy.interface.Bar
    """The bar's open price. The freeze's static check refuses the attribute name of the builtin,
    so it is read as dataclasses.asdict(bar)["open"] (the K2/K3 precedent, R-T2-1)."""
    return asdict(bar)["open"]


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


__all__ = [
    "BUY", "CT", "NS_PER_S", "SELL", "bar_open", "check_exposure", "ct_open_ns", "exit_items",
    "minus_minutes", "price_ticks",
]
