"""K3-ldnmom-01, front-running into the London 4 p.m. fix (Stage E.4 Part 3; specs section 5;
C 479-554; the lead's 01:40 narrowing to EUR and JPY, C line 482).

6E, 6J (q_c 1 each). Event set: every trade date d in FX_FULL_SESSIONS that is not in
EW_BANK_HOLIDAYS (C 511-512). With T_L = the _clocks.T_L row of d (10:00 CT, or 11:00 CT in the C9
mismatch weeks):
- signal: S = ticks(close of the bar at T_L - 13) - ticks(open of the bar at T_L - 15), the trend
  over the three bars opening 15:45, 15:46 and 15:47 London (C 513-515); both bars present;
  S = 0: no trade;
- entry: BUY if S > 0, SELL if S < 0; market intent on the bar at T_L - 13 (the entry decision
  bar), filling at the T_L - 12 open (09:48 CT standard, 10:48 CT in the mismatch weeks)
  (C 516-517);
- guard: the T_L - 15 and T_L - 13 bars carry one instrument_id (S0.9);
- exit: market intent on the bar at T_L + 4, filling at the T_L + 5 open (10:05 CT standard);
  a missing exit bar: the first later present bar (C 518-519, S0.7).
A date not in the event set is not traded. The rule is _event_common.FixEvent's.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time

from rules.xfa_rules import Refusal
from strategy.members.k3._calendar import EW_BANK_HOLIDAYS, FX_FULL_SESSIONS
from strategy.members.k3._clocks import T_L
from strategy.members.k3._event_common import (
    BUY,
    CLOSE,
    OPEN,
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

MEMBER_ID = "K3-ldnmom-01"
EXPOSURES = ("6E", "6J")  # C 481-482 (narrowed by the lead, 01:40 PDT 2026-09-24)
SIGNAL_START_OFFSET_MIN = -15  # the open of the bar at T_L - 15 (15:45 London)
ENTRY_DECISION_OFFSET_MIN = -13  # the close of the bar at T_L - 13; fills at the T_L - 12 open
EXIT_DECISION_OFFSET_MIN = 4  # the bar at T_L + 4; fills at the T_L + 5 open
TRADING_WINDOWS = (TradingInterval(time(9, 45), time(10, 6)),  # S0.12: T_L 10:00 CT
                   TradingInterval(time(10, 45), time(11, 6)))  # T_L 11:00 CT (mismatch weeks)

Rows = tuple[tuple[str, str], ...]


def event_dates(full_sessions: tuple[str, ...], ew_holidays: tuple[str, ...]) -> list[date]:
    """Every full session that is not an E&W bank holiday, oldest first."""
    ew = iso_dates(ew_holidays)
    return [d for d in sorted(iso_dates(full_sessions)) if d not in ew]


def schedule(t_l: Rows, full_sessions: tuple[str, ...], ew_holidays: tuple[str, ...]
             ) -> dict[date, Plan]:
    """Event date -> its Plan on CT date d, from the date's T_L."""
    clock = clock_table(t_l)
    out: dict[date, Plan] = {}
    for d in event_dates(full_sessions, ew_holidays):
        if d not in clock:
            raise ValueError(f"{MEMBER_ID}: no T_L row for event date {d}")
        t = clock[d]
        entry_ns = ct_open_ns(d, t + ENTRY_DECISION_OFFSET_MIN)
        out[d] = Plan(((ct_open_ns(d, t + SIGNAL_START_OFFSET_MIN), OPEN), (entry_ns, CLOSE)),
                      entry_ns, ct_open_ns(d, t + EXIT_DECISION_OFFSET_MIN))
    return out


def momentum_side(ticks: tuple[int, ...]) -> str | None:
    """S = close(T_L - 13) - open(T_L - 15) in ticks: S > 0 BUY, S < 0 SELL, S = 0 None."""
    start_open, end_close = ticks
    s = end_close - start_open
    if s == 0:
        return None
    return BUY if s > 0 else SELL


@dataclass
class LdnMom:
    root: str
    t_l: Rows = T_L  # the frozen tables; a test may pass others
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
        plans = schedule(self.t_l, self.full_sessions, self.ew_holidays)
        self._core = FixEvent(self.root, plans, momentum_side)

    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> tuple[LegIntent | Refusal, ...]:
        return self._core.on_minute(view, account)


def make_6e() -> LdnMom:
    return LdnMom("6E")


def make_6j() -> LdnMom:
    return LdnMom("6J")


__all__ = ["LdnMom", "event_dates", "make_6e", "make_6j", "momentum_side", "schedule"]
