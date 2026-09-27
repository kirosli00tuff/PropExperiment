"""K5-pmfix-01, gold PM auction continuation (Stage E.4 Part 2; specs section 5; C 538-639).

MGC only (q_c 1). On every scheduled gold PM auction day of _releases.GOLD_PM_AUCTIONS (section 11,
K5-L-03: the 14 PM-only no-auction days are not in it), with T_P = the table's CT instant of the
15:00 London start (C10, K5-L-02: 09:00, or 10:00 in 5-hour weeks):
- signal: s = ticks(close of the bar at T_P + 1) - ticks(close of the bar at T_P - 1); both bars
  present with one instrument_id (S0.9; the T_P + 1 bar is the entry decision bar); s = 0: no
  trade;
- entry: s > 0 BUY, s < 0 SELL, market intent on the bar at T_P + 1, filling at the T_P + 2 open;
  a missing T_P + 1 bar: no trade (S0.6);
- exit: market intent on the bar at T_P + 11, filling at the T_P + 12 open; a missing exit bar:
  the first later present bar (S0.7). Hold 10 minutes (K5-L-09);
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
from strategy.members.k5._releases import GOLD_PM_AUCTIONS
from strategy.stage_e.interface import (
    LegIntent,
    LegSpec,
    MemberAccountView,
    MinuteView,
    TradingInterval,
)

MEMBER_ID = "K5-pmfix-01"
EXPOSURES = ("MGC",)  # C 540; vehicles: gold -> MGC
SIGNAL_START_OFFSET_MIN = -1  # the bar at T_P - 1, the last pre-auction minute (C 591-593)
ENTRY_DECISION_OFFSET_MIN = 1  # the bar at T_P + 1: signal end and entry; fills at T_P + 2
EXIT_DECISION_OFFSET_MIN = 11  # the bar at T_P + 11; fills at the T_P + 12 open (C 596)
TRADING_WINDOWS = (TradingInterval(time(8, 59), time(9, 13)),  # S0.12: T_P 09:00 CT
                   TradingInterval(time(9, 59), time(10, 13)))  # T_P 10:00 CT (5-hour weeks)


def schedule(auctions: tuple[tuple[str, str], ...]) -> dict[date, SignalPlan]:
    """Auction date -> (T_P - 1, T_P + 1, T_P + 11) in CT clock minutes, T_P = the row's CT
    auction start."""
    return {date.fromisoformat(day): (clock_minute(t_p) + SIGNAL_START_OFFSET_MIN,
                                      clock_minute(t_p) + ENTRY_DECISION_OFFSET_MIN,
                                      clock_minute(t_p) + EXIT_DECISION_OFFSET_MIN)
            for day, t_p in auctions}


@dataclass
class PmFix:
    root: str
    pm_auctions: tuple[tuple[str, str], ...] = GOLD_PM_AUCTIONS  # the frozen table; a test may
    name: str = field(init=False)  # pass another
    legs: tuple[LegSpec, ...] = field(init=False)
    trading_windows: dict = field(init=False)
    _core: SignedMoveEvent = field(init=False)

    def __post_init__(self) -> None:
        check_exposure(self.root, EXPOSURES, MEMBER_ID)
        self.name = f"{MEMBER_ID} {self.root}"
        self.legs = (LegSpec(self.root, True),)
        self.trading_windows = {self.root: TRADING_WINDOWS}
        self._core = SignedMoveEvent(self.root, schedule(self.pm_auctions))

    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> tuple[LegIntent | Refusal, ...]:
        return self._core.on_minute(view, account)


def make_mgc() -> PmFix:
    return PmFix("MGC")


__all__ = ["PmFix", "make_mgc", "schedule"]
