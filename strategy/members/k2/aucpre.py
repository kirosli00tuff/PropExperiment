"""K2-aucpre-01, pre-auction concession (Stage E.3; specs section 4; catalog C lines 268-349).

On each tenor-matched Treasury auction date (ZT 2-year, ZF 5-year, ZN and TN 10-year, ZB and UB
30-year; _releases.TREASURY_AUCTIONS, T_a = the competitive close - 1 h in CT):
- SELL q_c: market intent on the bar at T_a - 181 min (fills at the T_a - 180 open);
- exit: market intent on the first bar at or after T_a - 2 min (fills nominally at T_a - 1).
No entry when the entry decision bar is missing or carries early_halt_ct (C4). Roll blackout, F,
the fill guard and costs are the engine's. Hold 179 minutes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time

from rules.xfa_rules import Refusal
from strategy.members.k2._event_common import (
    RATES_EXPOSURES,
    SELL,
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

MEMBER_ID = "K2-aucpre-01"
SIDE = SELL  # C 296, 317: unconditional
ENTRY_DECISION_OFFSET_MIN = -181  # the bar at T_a - 181 min (C 296-297)
EXIT_DECISION_OFFSET_MIN = -2  # the first bar at or after T_a - 2 min (C 298-299)
WINDOW_START_CT = time(7, 29)  # S0.12: the union over T_a 10:30 and 12:00
WINDOW_END_CT = time(12, 0)


@dataclass
class AucPre:
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


def make_zt() -> AucPre:
    return AucPre("ZT")


def make_zf() -> AucPre:
    return AucPre("ZF")


def make_zn() -> AucPre:
    return AucPre("ZN")


def make_tn() -> AucPre:
    return AucPre("TN")


def make_zb() -> AucPre:
    return AucPre("ZB")


def make_ub() -> AucPre:
    return AucPre("UB")


__all__ = ["AucPre", "make_tn", "make_ub", "make_zb", "make_zf", "make_zn", "make_zt"]
