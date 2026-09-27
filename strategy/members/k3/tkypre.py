"""K3-tkypre-01, gotobi dollar demand into the Tokyo 9:55 fix (Stage E.4 Part 3; specs section 8;
C 726-800).

6J only (q_c 1). Event set: trade dates d in FX_FULL_SESSIONS that, as Tokyo dates, are in
_calendar.GOTOBI_OR_TOKYO_MONTH_END: a Tokyo business day (EC-JP) whose day of month is 5, 10, 15,
20, 25 or 30, or the last Tokyo business day of its month; no shift (C 751-756, K3-L-08). The
early-halt test is trade date d's (FX_FULL_SESSIONS, K3-L-04), never the CT-evening bar's field.
With T_T = the _clocks.T_T row of d (CT "HH:MM" on calendar day d-1: 18:55 CST or 19:55 CDT):
- entry: SELL (a rise in USD/JPY is a fall in 6J, C8); market intent on the bar at 17:29 CT on
  calendar day d-1, filling at the 17:30 open (C 757-759); a missing 17:29 bar: no trade (S0.6);
- guard: the entry bar is the only bar read (S0.9);
- exit: market intent on the bar at T_T - 1 on d-1, filling at the T_T open (C 760-762); a missing
  exit bar: the first later present bar (S0.7).
No signal. A date not in the event set is not traded. The rule is _event_common.FixEvent's.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time

from rules.xfa_rules import Refusal
from strategy.members.k3._calendar import FX_FULL_SESSIONS, GOTOBI_OR_TOKYO_MONTH_END
from strategy.members.k3._clocks import T_T
from strategy.members.k3._event_common import (
    ONE_DAY,
    SELL,
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

MEMBER_ID = "K3-tkypre-01"
EXPOSURES = ("6J",)  # C 728
ENTRY_DECISION_CT = "17:29"  # on calendar day d-1; fills at the 17:30 open (C 757-759)
EXIT_DECISION_OFFSET_MIN = -1  # the bar at T_T - 1 on d-1; fills at the T_T open (C 760-762)
TRADING_WINDOWS = (TradingInterval(time(17, 29), time(19, 56), -1, -1),)  # S0.12, day -1

Rows = tuple[tuple[str, str], ...]


def event_dates(event_days: tuple[str, ...], full_sessions: tuple[str, ...]) -> list[date]:
    """The gotobi or Tokyo month-end dates that are full FX sessions, oldest first."""
    full = iso_dates(full_sessions)
    return [d for d in sorted(iso_dates(event_days)) if d in full]


def schedule(event_days: tuple[str, ...], t_t: Rows, full_sessions: tuple[str, ...]
             ) -> dict[date, Plan]:
    """Event date d -> its Plan on CT calendar day d-1."""
    clock = clock_table(t_t)
    out: dict[date, Plan] = {}
    for d in event_dates(event_days, full_sessions):
        if d not in clock:
            raise ValueError(f"{MEMBER_ID}: no T_T row for event date {d}")
        eve = d - ONE_DAY
        out[d] = Plan((), ct_open_ns(eve, clock_minute(ENTRY_DECISION_CT)),
                      ct_open_ns(eve, clock[d] + EXIT_DECISION_OFFSET_MIN))
    return out


def always_sell(ticks: tuple[int, ...]) -> str:
    """No signal: every event date is a SELL."""
    assert ticks == ()
    return SELL


@dataclass
class TkyPre:
    root: str
    event_days: tuple[str, ...] = GOTOBI_OR_TOKYO_MONTH_END  # the frozen tables; a test may
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
        plans = schedule(self.event_days, self.t_t, self.full_sessions)
        self._core = FixEvent(self.root, plans, always_sell)

    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> tuple[LegIntent | Refusal, ...]:
        return self._core.on_minute(view, account)


def make_6j() -> TkyPre:
    return TkyPre("6J")


__all__ = ["TkyPre", "always_sell", "event_dates", "make_6j", "schedule"]
