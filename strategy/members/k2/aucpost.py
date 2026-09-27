"""K2-aucpost-01, post-auction recovery (Stage E.3; specs section 5; catalog C lines 351-403).

On each tenor-matched Treasury auction date (the event set and T_a of K2-aucpre-01):
- BUY q_c: market intent on the bar at T_a + 4 min (fills at the T_a + 5 open);
- exit: market intent on the bar at T_a + 184 min (fills at the T_a + 185 open); a missing exit
  bar: the first later bar; the engine's flatten at F if earlier.
No entry when the entry decision bar is missing or carries early_halt_ct (C4). No results field is
read. Hold 180 minutes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time

from rules.xfa_rules import Refusal
from strategy.members.k2._event_common import (
    BUY,
    RATES_EXPOSURES,
    FixedSideEvent,
    auction_schedule,
    check_exposure,
)
from strategy.stage_e.interface import (
    LegIntent,
    LegSpec,
    MemberAccountView,
    MinuteView,
    TradingInterval,
)

MEMBER_ID = "K2-aucpost-01"
SIDE = BUY  # C 367: unconditional
ENTRY_DECISION_OFFSET_MIN = 4  # the bar at T_a + 4 min (C 367-368)
EXIT_DECISION_OFFSET_MIN = 184  # the bar at T_a + 184 min, or the first later bar (C 369-370)
WINDOW_START_CT = time(10, 34)  # S0.12: the union over T_a 10:30 and 12:00
WINDOW_END_CT = time(15, 6)


@dataclass
class AucPost:
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
        self._core = FixedSideEvent(self.root, SIDE, auction_schedule(
            self.root, ENTRY_DECISION_OFFSET_MIN, EXIT_DECISION_OFFSET_MIN))

    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> tuple[LegIntent | Refusal, ...]:
        return self._core.on_minute(view, account)


def make_zt() -> AucPost:
    return AucPost("ZT")


def make_zf() -> AucPost:
    return AucPost("ZF")


def make_zn() -> AucPost:
    return AucPost("ZN")


def make_tn() -> AucPost:
    return AucPost("TN")


def make_zb() -> AucPost:
    return AucPost("ZB")


def make_ub() -> AucPost:
    return AucPost("UB")


__all__ = ["AucPost", "make_tn", "make_ub", "make_zb", "make_zf", "make_zn", "make_zt"]
