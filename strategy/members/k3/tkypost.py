"""K3-tkypost-01, dollar weakness after the Tokyo 9:55 fix (Stage E.4 Part 3; specs section 9;
C 801-855).

6J only (q_c 1). Event set: every trade date d in FX_FULL_SESSIONS that, as a Tokyo date, is a
Tokyo business day (_calendar.TOKYO_BUSINESS_DAYS, EC-JP; C 821-822, K3-L-08). The early-halt test
is trade date d's (FX_FULL_SESSIONS, K3-L-04), never the CT-evening bar's field. With T_T = the
_clocks.T_T row of d (CT "HH:MM" on calendar day d-1: 18:55 CST or 19:55 CDT):
- entry: BUY (dollar weakness is a rise in 6J); market intent on the bar at T_T on d-1, filling at
  the T_T + 1 open (18:56 CST or 19:56 CDT on d-1) (C 823-824); a missing T_T bar: no trade;
- guard: the entry bar is the only bar read (S0.9);
- exit: market intent on the bar at 00:59 CT on d, filling at the 01:00 open (C 825-826); a
  missing exit bar: the first later present bar (S0.7).
No signal. A date not in the event set is not traded. The rule is _event_common.FixEvent's.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time

from rules.xfa_rules import Refusal
from strategy.members.k3._calendar import FX_FULL_SESSIONS, TOKYO_BUSINESS_DAYS
from strategy.members.k3._clocks import T_T
from strategy.members.k3._event_common import (
    BUY,
    ONE_DAY,
    FixEvent,
    Plan,
    check_exposure,
    clock_minute,
    clock_table,
    ct_open_ns,
    iso_dates,
)
from strategy.stage_e.interface import (
    LegIntent,
    LegSpec,
    MemberAccountView,
    MinuteView,
    TradingInterval,
)

MEMBER_ID = "K3-tkypost-01"
EXPOSURES = ("6J",)  # C 803
EXIT_DECISION_CT = "00:59"  # on d; fills at the 01:00 open (C 825-826)
TRADING_WINDOWS = (TradingInterval(time(18, 55), time(1, 1), -1, 0),)  # S0.12: d-1 to d

Rows = tuple[tuple[str, str], ...]


def event_dates(business_days: tuple[str, ...], full_sessions: tuple[str, ...]) -> list[date]:
    """The Tokyo business days that are full FX sessions, oldest first."""
    full = iso_dates(full_sessions)
    return [d for d in sorted(iso_dates(business_days)) if d in full]


def schedule(business_days: tuple[str, ...], t_t: Rows, full_sessions: tuple[str, ...]
             ) -> dict[date, Plan]:
    """Event date d -> its Plan: entry on CT calendar day d-1, exit on d."""
    clock = clock_table(t_t)
    out: dict[date, Plan] = {}
    for d in event_dates(business_days, full_sessions):
        if d not in clock:
            raise ValueError(f"{MEMBER_ID}: no T_T row for event date {d}")
        out[d] = Plan((), ct_open_ns(d - ONE_DAY, clock[d]),
                      ct_open_ns(d, clock_minute(EXIT_DECISION_CT)))
    return out


def always_buy(ticks: tuple[int, ...]) -> str:
    """No signal: every event date is a BUY."""
    assert ticks == ()
    return BUY


@dataclass
class TkyPost:
    root: str
    business_days: tuple[str, ...] = TOKYO_BUSINESS_DAYS  # the frozen tables; a test may
    t_t: Rows = T_T  # pass others
    full_sessions: tuple[str, ...] = FX_FULL_SESSIONS
    name: str = field(init=False)
    legs: tuple[LegSpec, ...] = field(init=False)
    trading_windows: dict = field(init=False)
    _core: FixEvent = field(init=False)

    def __post_init__(self) -> None:
        check_exposure(self.root, EXPOSURES, MEMBER_ID)
        self.name = f"{MEMBER_ID} {self.root}"
        self.legs = (LegSpec(self.root, True),)
        self.trading_windows = {self.root: TRADING_WINDOWS}
        plans = schedule(self.business_days, self.t_t, self.full_sessions)
        self._core = FixEvent(self.root, plans, always_buy)

    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> tuple[LegIntent | Refusal, ...]:
        return self._core.on_minute(view, account)


def make_6j() -> TkyPost:
    return TkyPost("6J")


__all__ = ["TkyPost", "always_buy", "event_dates", "make_6j", "schedule"]
