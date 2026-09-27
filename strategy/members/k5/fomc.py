"""K5-fomc-01, gold post-FOMC continuation (Stage E.4 Part 2; specs section 6; C 640-712).

MGC only (q_c 1). On every date of _releases.FOMC_STATEMENT_DATES (the frozen calendar's FOMC rows
at 13:00 CT, E.3-L-15):
- signal: s = ticks(close of the bar at 13:04) - ticks(close of the bar at 12:59); both bars
  present with one instrument_id (S0.9; the 13:04 bar is the entry decision bar); s = 0: no
  trade;
- entry: s > 0 BUY, s < 0 SELL, market intent on the bar at 13:04, filling at the 13:05 open; a
  missing 13:04 bar: no trade (S0.6);
- exit: market intent on the bar at 13:14, filling at the 13:15 open; a missing exit bar: the
  first later present bar (S0.7). Hold 10 minutes (K5-L-09);
- no entry when the entry bar carries early_halt_ct (S0.8). No percent return (S0.14).
A date not in the table is not traded. The rule is _event_common.SignedMoveEvent's.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time

from rules.xfa_rules import Refusal
from strategy.members.k5._event_common import (
    SignalPlan,
    SignedMoveEvent,
    check_exposure,
    clock_minute,
)
from strategy.members.k5._releases import FOMC_STATEMENT_DATES
from strategy.stage_e.interface import (
    LegIntent,
    LegSpec,
    MemberAccountView,
    MinuteView,
    TradingInterval,
)

MEMBER_ID = "K5-fomc-01"
EXPOSURES = ("MGC",)  # C 644; vehicles: gold -> MGC
SIGNAL_START_CT = time(12, 59)  # the bar before the 13:00 CT statement (C 673-674)
ENTRY_DECISION_CT = time(13, 4)  # signal end and entry; fills at the 13:05 open (C 675-676)
EXIT_DECISION_CT = time(13, 14)  # fills at the 13:15 open (C 677)
TRADING_WINDOWS = (TradingInterval(time(12, 59), time(13, 16)),)  # S0.12


def schedule(dates: tuple[str, ...]) -> dict[date, SignalPlan]:
    """Statement date -> (12:59, 13:04, 13:14) in CT clock minutes."""
    plan = (clock_minute(SIGNAL_START_CT), clock_minute(ENTRY_DECISION_CT),
            clock_minute(EXIT_DECISION_CT))
    return {date.fromisoformat(day): plan for day in dates}


@dataclass
class Fomc:
    root: str
    statement_dates: tuple[str, ...] = FOMC_STATEMENT_DATES  # the frozen table; a test may
    name: str = field(init=False)  # pass another
    legs: tuple[LegSpec, ...] = field(init=False)
    trading_windows: dict = field(init=False)
    _core: SignedMoveEvent = field(init=False)

    def __post_init__(self) -> None:
        check_exposure(self.root, EXPOSURES, MEMBER_ID)
        self.name = f"{MEMBER_ID} {self.root}"
        self.legs = (LegSpec(self.root, True),)
        self.trading_windows = {self.root: TRADING_WINDOWS}
        self._core = SignedMoveEvent(self.root, schedule(self.statement_dates))

    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> tuple[LegIntent | Refusal, ...]:
        return self._core.on_minute(view, account)


def make_mgc() -> Fomc:
    return Fomc("MGC")


__all__ = ["Fomc", "make_mgc", "schedule"]
