"""The Stage E member contract (Stage E.2b Task 1). Read strategy/stage_e/_template.py first.

A Stage E member is a zero-argument factory returning an object with ``name`` and
``on_minute(view, account)``. The generalized runner (screening/stage_e_runner.py) calls it once
per minute of the member's shared UTC grid (design D11.5):

- ``view.bars`` maps EVERY leg the member reads (its signal legs and its traded legs) to that
  leg's completed one-minute bar opening at ``view.ts_event_ns``, or to None when the leg has no
  bar at that minute. Nothing is forward filled: a None is a missing bar, and a member must not
  treat it as a price. Hindsight fields (``vendor_degraded_day``) arrive masked (False).
- The call happens at the minute's decision time (``view.decision_ts_utc`` = bar open + 60 s);
  an order fills at the open of a LATER bar of its own leg, never at a price the member saw.
- ``account`` is a frozen snapshot: positions and pending quantities per traded leg, in
  contracts, the XFA balance and floor, and the entries already made today per leg.

Orders are ``LegIntent``s built with ``leg_market_intent`` / ``leg_limit_intent`` below (stamped
with the view's decision time). The engine refuses, by name, and never trades, any intent that:
opens exposure when any leg the member reads has no bar at this minute (D11.5); is not on a
traded leg; would exceed the member cap (D9.5, D9.11: 1 lot-equivalent across legs, the per-product
volatility caps) or open a second leg's position while another is held; would be the 21st entry of
the product on its trade date (D9.3a); would exit less than 2 full minutes after the position's
last opening fill (D9.3b); opens after F or inside a session's no-open time (rules/sessions.py);
opens on a date outside the member's window or on a roll-blackout date of any leg (D4); opens
while the price is beyond a Topstep price-limit stop level (D9.7); or opens inside the CPI window
of a CPI-restricted product (D9.12). Refusal counts are reported per member; attempts at (a) or
(b) label the member (D9 floor), they do not drop it.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, time
from typing import Protocol, runtime_checkable

from rules.xfa_rules import Phase, Refusal, Status
from strategy.interface import NS_PER_BAR, NS_PER_S, Bar

SIDES = ("buy", "sell")
MEMBER_INTERFACE_VERSION = 1


@dataclass(frozen=True, slots=True)
class LegSpec:
    """One leg of a member: ``traded`` False is a signal leg (read only, never a position)."""

    root: str
    traded: bool


@dataclass(frozen=True, slots=True)
class TradingInterval:
    """A CT clock interval of a trade date in which a member reads or trades one leg, for D9's
    member-level coverage check: [start, end), each end on the calendar day ``offset_days``
    from the trade date (-1 = the prior evening). Example: CP2 on an equity product reads
    [08:30, 15:08): ``TradingInterval(time(8, 30), time(15, 8))``."""

    start_ct: time
    end_ct: time
    start_offset_days: int = 0
    end_offset_days: int = 0


@dataclass(frozen=True, slots=True)
class MinuteView:
    """Every leg's bar at one grid minute (None: no bar). Built only by the engine."""

    ts_event_ns: int  # the minute's bar OPEN, UTC ns
    bars: Mapping[str, Bar | None]

    @property
    def decision_ts_ns(self) -> int:
        return self.ts_event_ns + NS_PER_BAR

    @property
    def decision_ts_utc(self) -> datetime:
        return datetime.fromtimestamp(self.decision_ts_ns / NS_PER_S, tz=UTC)

    def bar(self, root: str) -> Bar | None:
        return self.bars[root]

    def all_present(self) -> bool:
        return all(b is not None for b in self.bars.values())


@dataclass(frozen=True, slots=True)
class MemberAccountView:
    """Point-in-time account snapshot at the view's decision time. Built only by the engine."""

    phase: Phase
    status: Status
    trade_date: date | None  # the traded legs' trade date of the last traded-leg bar seen
    balance_cents: int | float
    mll_floor_cents: int | float
    positions: Mapping[str, int]  # traded leg -> signed contracts (long > 0)
    pending: Mapping[str, int]  # traded leg -> signed contracts accepted, not yet filled
    avg_entry_price: Mapping[str, float | None]
    entries_today: Mapping[str, int]  # traded leg -> opening fills on the current trade date

    def position(self, root: str) -> int:
        return self.positions.get(root, 0)

    def is_flat(self) -> bool:
        return not any(self.positions.values()) and not any(self.pending.values())


@dataclass(frozen=True, slots=True)
class LegIntent:
    """One order on one traded leg. Build it with ``leg_market_intent`` / ``leg_limit_intent``."""

    root: str
    side: str
    quantity: int  # contracts, > 0
    ts_utc: datetime  # the decision time of the view it answers
    limit_price: float | None = None  # set: a resting limit order, filled only on trade-through
    ttl_bars: int | None = None  # minutes after the decision at which a limit order expires

    @property
    def signed_quantity(self) -> int:
        return self.quantity if self.side == "buy" else -self.quantity

    @property
    def is_limit(self) -> bool:
        return self.limit_price is not None


def leg_market_intent(view: MinuteView, root: str, side: str, quantity: int
                      ) -> LegIntent | Refusal:
    """A market order on ``root`` stamped with the view's decision time."""
    if side not in SIDES:
        return Refusal("intent_bad_side", f"side {side!r} is not one of {SIDES}")
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
        return Refusal("intent_bad_quantity", f"quantity {quantity!r} is not a positive integer")
    if root not in view.bars:
        return Refusal("intent_unknown_leg", f"{root!r} is not a leg of this member")
    return LegIntent(root, side, quantity, view.decision_ts_utc)


def leg_limit_intent(view: MinuteView, root: str, side: str, quantity: int,
                     limit_price: float, ttl_bars: int) -> LegIntent | Refusal:
    """A resting limit order (trade-through fills, D9.2). The engine checks the price grid and
    that it is not marketable against the decision bar's close."""
    base = leg_market_intent(view, root, side, quantity)
    if isinstance(base, Refusal):
        return base
    if isinstance(ttl_bars, bool) or not isinstance(ttl_bars, int) or ttl_bars <= 0:
        return Refusal("limit_bad_ttl", f"ttl_bars {ttl_bars!r} is not a positive integer")
    bad_type = isinstance(limit_price, bool) or not isinstance(limit_price, float | int)
    if bad_type or limit_price <= 0:
        return Refusal("limit_bad_price", f"limit price {limit_price!r} is not positive")
    return LegIntent(root, side, quantity, view.decision_ts_utc, float(limit_price), ttl_bars)


@runtime_checkable
class StageEMember(Protocol):
    """The whole member contract, frozen at MEMBER_INTERFACE_VERSION. ``trading_windows`` maps
    every leg the member reads to the intervals the coverage check (D9) measures on it."""

    name: str
    trading_windows: Mapping[str, tuple[TradingInterval, ...]]

    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> Sequence[LegIntent | Refusal]: ...


__all__ = [
    "MEMBER_INTERFACE_VERSION", "LegIntent", "LegSpec", "MemberAccountView", "MinuteView",
    "StageEMember", "TradingInterval", "leg_limit_intent", "leg_market_intent",
]
