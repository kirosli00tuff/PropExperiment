"""Helpers shared by MemberCoder-A's three K1 ports: K1-cp1-01, K1-cp2-01 and K1-cp3-01, each on
MNQ, M2K and MYM (Stage E.7; reports/stage_e7_member_specs.md section 0).

Copied in structure from strategy/members/k7/_port_common.py (Stage E.6), never imported from it.
The rules live in the member modules (cp1, cp2, cp3); this module holds only clock, tick and
order plumbing that none of them may vary:

- ``leg_facts``: the frozen values of the traded root a member reads (O and C from
  ``load_frozen_tables().day_session_ct``, q_c from the vehicle table, the vendor tick from
  rules.products), never literals (S0.3, S0.4, S0.10): O 08:30 and C 15:00 on all three roots;
  q_c MNQ 1, M2K 3, MYM 3; vendor tick MNQ 0.25, M2K 0.10, MYM 1.00 index points;
- ``ct_open``: a bar's open instant in America/Chicago. "The bar at hh:mm" of trade date d is
  identified by its CT calendar date AND its clock (S0.4, E.3-L-03, K7-L-01 adopted). In the D10
  equity calendar a trade date d runs [d-1 17:00, d 16:00) CT (C3); an exchange holiday on which
  the equity session halts early is its own trade date, and there are no booked-forward dates,
  so the bars' trade_date and C3 agree;
- ``to_ticks``: a price in integer vendor ticks, round(price / vendor_tick) (S0.10, E.3-L-19);
- ``exit_if_due``: S0.7's exit, sent on every present bar of CT date d at or after the named exit
  bar while the position is non-zero and nothing is pending on the leg (so a refused exit is
  resent, E.3-L-22, and an engine-forced exit, which is pending, is never duplicated).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from typing import Any
from zoneinfo import ZoneInfo

from rules.products import product
from rules.xfa_rules import Refusal
from screening.stage_e_frozen import load_frozen_tables
from strategy.stage_e.interface import (
    LegIntent,
    LegSpec,
    MemberAccountView,
    MinuteView,
    leg_market_intent,
)

CT = ZoneInfo("America/Chicago")
NS_PER_S = 1_000_000_000
# S0.1 / S0.2: the three K1 exposures on their own micro vehicles, in the declaration order
# Nasdaq-100 MNQ, Russell 2000 M2K, Dow MYM (no full-size contract, ES or MES is read)
EXPOSURES: tuple[str, ...] = ("MNQ", "M2K", "MYM")
_ANCHOR_DAY = date(2000, 1, 3)  # any date: clock arithmetic on a time of day


@dataclass(frozen=True)
class LegFacts:
    """The frozen values of one traded leg (S0.3, S0.4, S0.10)."""

    root: str
    o: time  # D6's O, from the frozen day_session_ct table (08:30 on all three)
    c: time  # D6's C, from the frozen day_session_ct table (15:00 on all three)
    q: int  # q_c of the vehicle, from the frozen vehicle table (MNQ 1, M2K 3, MYM 3)
    tick: Decimal  # rules.products vendor tick (MNQ 0.25, M2K 0.10, MYM 1.00)

    @property
    def legs(self) -> tuple[LegSpec, ...]:
        return (LegSpec(self.root, True),)  # S0.1: one traded leg, no signal legs


def leg_facts(root: str) -> LegFacts:
    if root not in EXPOSURES:
        raise ValueError(f"{root!r} is not a K1 exposure {EXPOSURES}")
    tables = load_frozen_tables()
    o, c = tables.day_session_ct[root]
    return LegFacts(root, o, c, tables.vehicles[root].q_c, product(root).vendor_tick)


def label(member_id: str, root: str) -> str:
    """S0.2: the declaration label, which is also the member object's ``name``."""
    return f"{member_id} {root}"


def shift(at: time, minutes: int) -> time:
    """A clock time ``minutes`` later (negative: earlier) on the same CT day."""
    return (datetime.combine(_ANCHOR_DAY, at) + timedelta(minutes=minutes)).time()


def ct_open(bar: Any) -> datetime:
    """The bar's open (``ts_event_ns``, integer seconds: bars sit on the minute) in CT."""
    return datetime.fromtimestamp(bar.ts_event_ns // NS_PER_S, tz=UTC).astimezone(CT)


def to_ticks(price: float, tick: Decimal) -> int:
    """S0.10: round(price / vendor_tick), computed exactly in Decimal."""
    return round(Decimal(repr(price)) / tick)


def is_flat(account: MemberAccountView, root: str) -> bool:
    return account.position(root) == 0 and not account.pending.get(root, 0)


def exit_if_due(view: MinuteView, account: MemberAccountView, root: str, opened: datetime,
                day: date, exit_at: time) -> Sequence[LegIntent | Refusal]:
    """S0.7 and E.3-L-22: a market intent closing the whole position on a present bar of CT date
    ``day`` opening at or after ``exit_at``, while the position is non-zero and nothing is
    pending on the leg (an accepted exit, or an engine-forced one, is pending until it fills; a
    refused one is not, so it is sent again on the next present bar)."""
    position = account.position(root)
    if position == 0 or account.pending.get(root, 0):
        return ()
    if opened.date() != day or opened.time() < exit_at:
        return ()
    side = "sell" if position > 0 else "buy"
    return (leg_market_intent(view, root, side, abs(position)),)


__all__ = [
    "CT", "EXPOSURES", "LegFacts", "ct_open", "exit_if_due", "is_flat", "label",
    "leg_facts", "shift", "to_ticks",
]
