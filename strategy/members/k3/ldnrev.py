"""K3-ldnrev-01, month-end London 4 p.m. fix, contrarian (Stage E.4 Part 3; specs section 4;
C 380-478; lead ruling R-05, C line 382).

6E, 6J, 6S (q_c 1 each). Event set: ME(m) of each month m (_calendar.MONTH_ENDS) when ME(m) is in
FX_FULL_SESSIONS and not in EW_BANK_HOLIDAYS; a month whose ME(m) is excluded is not traded and not
shifted (C 425, C9 lines 196-201, K3-L-06). With T_L = the _clocks.T_L row of ME(m) (10:00 CT, or
11:00 CT in the C9 mismatch weeks):
- signal: M = ticks(close of the bar at T_L - 1) - ticks(close of the bar at T_L - 11) (R-05: the
  10-minute pre-fix move; the text's T_L - 16 is superseded); both bars present; M = 0: no trade;
- entry: BUY if M < 0, SELL if M > 0 (contrarian in the futures' own quote, C 429-433); market
  intent on the bar at T_L + 4, filling at the T_L + 5 open (10:05 CT, or 11:05 CT); a missing
  T_L + 4 bar: no trade (S0.6);
- guard: the T_L - 11, T_L - 1 and T_L + 4 bars carry one instrument_id (S0.9);
- exit: market intent on the bar at T_L + 19, filling at the T_L + 20 open; a missing exit bar:
  the first later present bar (C 434-435, S0.7).
A date not in the event set is not traded. The rule is _event_common.FixEvent's.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time

from rules.xfa_rules import Refusal
from strategy.members.k3._calendar import EW_BANK_HOLIDAYS, FX_FULL_SESSIONS, MONTH_ENDS
from strategy.members.k3._clocks import T_L
from strategy.members.k3._event_common import (
    BUY,
    CLOSE,
    SELL,
    FixEvent,
    Plan,
    check_exposure,
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

MEMBER_ID = "K3-ldnrev-01"
EXPOSURES = ("6E", "6J", "6S")  # C 384-386; vehicles 6E, 6J, 6S
SIGNAL_START_OFFSET_MIN = -11  # the bar at T_L - 11 (R-05)
SIGNAL_END_OFFSET_MIN = -1  # the bar at T_L - 1
ENTRY_DECISION_OFFSET_MIN = 4  # the bar at T_L + 4; fills at the T_L + 5 open
EXIT_DECISION_OFFSET_MIN = 19  # the bar at T_L + 19; fills at the T_L + 20 open
TRADING_WINDOWS = (TradingInterval(time(9, 49), time(10, 21)),  # S0.12: T_L 10:00 CT
                   TradingInterval(time(10, 49), time(11, 21)))  # T_L 11:00 CT (mismatch weeks)

Rows = tuple[tuple[str, str], ...]


def event_dates(month_ends: Rows, full_sessions: tuple[str, ...],
                ew_holidays: tuple[str, ...]) -> list[date]:
    """ME(m) of every month m whose ME(m) is a full session and not an E&W bank holiday."""
    full, ew = iso_dates(full_sessions), iso_dates(ew_holidays)
    days = (date.fromisoformat(me) for _, me in month_ends)
    return [d for d in days if d in full and d not in ew]


def schedule(month_ends: Rows, t_l: Rows, full_sessions: tuple[str, ...],
             ew_holidays: tuple[str, ...]) -> dict[date, Plan]:
    """Event date -> its Plan on CT date d, from the date's T_L."""
    clock = clock_table(t_l)
    out: dict[date, Plan] = {}
    for d in event_dates(month_ends, full_sessions, ew_holidays):
        if d not in clock:
            raise ValueError(f"{MEMBER_ID}: no T_L row for event date {d}")
        t = clock[d]
        out[d] = Plan(((ct_open_ns(d, t + SIGNAL_START_OFFSET_MIN), CLOSE),
                       (ct_open_ns(d, t + SIGNAL_END_OFFSET_MIN), CLOSE)),
                      ct_open_ns(d, t + ENTRY_DECISION_OFFSET_MIN),
                      ct_open_ns(d, t + EXIT_DECISION_OFFSET_MIN))
    return out


def contrarian_side(ticks: tuple[int, ...]) -> str | None:
    """M = close(T_L - 1) - close(T_L - 11) in ticks: M < 0 BUY, M > 0 SELL, M = 0 None."""
    start, end = ticks
    m = end - start
    if m == 0:
        return None
    return BUY if m < 0 else SELL


@dataclass
class LdnRev:
    root: str
    month_ends: Rows = MONTH_ENDS  # the frozen tables; a test may pass others
    t_l: Rows = T_L
    full_sessions: tuple[str, ...] = FX_FULL_SESSIONS
    ew_holidays: tuple[str, ...] = EW_BANK_HOLIDAYS
    name: str = field(init=False)
    legs: tuple[LegSpec, ...] = field(init=False)
    trading_windows: dict = field(init=False)
    _core: FixEvent = field(init=False)

    def __post_init__(self) -> None:
        check_exposure(self.root, EXPOSURES, MEMBER_ID)
        self.name = f"{MEMBER_ID} {self.root}"
        self.legs = (LegSpec(self.root, True),)
        self.trading_windows = {self.root: TRADING_WINDOWS}
        plans = schedule(self.month_ends, self.t_l, self.full_sessions, self.ew_holidays)
        self._core = FixEvent(self.root, plans, contrarian_side)

    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> tuple[LegIntent | Refusal, ...]:
        return self._core.on_minute(view, account)


def make_6e() -> LdnRev:
    return LdnRev("6E")


def make_6j() -> LdnRev:
    return LdnRev("6J")


def make_6s() -> LdnRev:
    return LdnRev("6S")


__all__ = ["LdnRev", "contrarian_side", "event_dates", "make_6e", "make_6j", "make_6s",
           "schedule"]
