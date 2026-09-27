"""K2-fomcpost-01, post-FOMC drift (Stage E.3; specs section 6; catalog C lines 405-463).

On each scheduled FOMC statement date whose statement is released at 13:00 CT
(_releases.FOMC_STATEMENT_DATES, L-15):
- BUY q_c: market intent on the bar at 13:29 (fills at the 13:30 open);
- exit: market intent on the bar at 15:04 (fills at the 15:05 open); a missing exit bar: the first
  later bar; the engine's flatten at F if earlier.
No entry when the 13:29 bar is missing or carries early_halt_ct (C4). Hold 95 minutes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time

from rules.xfa_rules import Refusal
from strategy.members.k2._event_common import (
    BUY,
    RATES_EXPOSURES,
    FixedSideEvent,
    check_exposure,
    fixed_schedule,
)
from strategy.members.k2._releases import FOMC_STATEMENT_DATES
from strategy.stage_e.interface import (
    LegIntent,
    LegSpec,
    MemberAccountView,
    MinuteView,
    TradingInterval,
)

MEMBER_ID = "K2-fomcpost-01"
SIDE = BUY  # C 415, 429: unconditional
ENTRY_DECISION_CT = time(13, 29)  # fills at the 13:30 open (C 429)
EXIT_DECISION_CT = time(15, 4)  # fills at the 15:05 open (C 430)
WINDOW_START_CT = time(13, 29)  # S0.12
WINDOW_END_CT = time(15, 6)


@dataclass
class FomcPost:
    root: str
    name: str = field(init=False)
    legs: tuple[LegSpec, ...] = field(init=False)
    trading_windows: dict = field(init=False)
    _core: FixedSideEvent = field(init=False)

    def __post_init__(self) -> None:
        check_exposure(self.root, RATES_EXPOSURES, MEMBER_ID)
        self.name = f"{MEMBER_ID} {self.root}"
        self.legs = (LegSpec(self.root, True),)
        self.trading_windows = {self.root: (TradingInterval(WINDOW_START_CT, WINDOW_END_CT),)}
        self._core = FixedSideEvent(self.root, SIDE, fixed_schedule(
            FOMC_STATEMENT_DATES, ENTRY_DECISION_CT, EXIT_DECISION_CT))

    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> tuple[LegIntent | Refusal, ...]:
        return self._core.on_minute(view, account)


def make_zt() -> FomcPost:
    return FomcPost("ZT")


def make_zf() -> FomcPost:
    return FomcPost("ZF")


def make_zn() -> FomcPost:
    return FomcPost("ZN")


def make_tn() -> FomcPost:
    return FomcPost("TN")


def make_zb() -> FomcPost:
    return FomcPost("ZB")


def make_ub() -> FomcPost:
    return FomcPost("UB")


__all__ = ["FomcPost", "make_tn", "make_ub", "make_zb", "make_zf", "make_zn", "make_zt"]
