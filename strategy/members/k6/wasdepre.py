"""K6-wasdepre-01, WASDE-day pre-release drift through the release (Stage E.8; specs section 6;
C 596-680).

ZC and ZS (q_c 1 each). On trade date d with is_wasde_date(d) (EC-WASDE after C9a's drop rule,
K6-L-11) and d in GRAIN_FULL_SESSIONS (S0.8, K6-L-10); T = 11:00 CT is fixed:
- signal: Dr = close of the bar at 10:29 minus open of the bar at 08:30, in integer vendor ticks;
  both bars present and carrying one instrument_id (S0.9); Dr = 0: no trade;
- entry: market intent on the bar at 10:29 (fills at the 10:30 open) in the direction of sign(Dr)
  (S0.6: the 10:29 bar is the entry bar; missing, no trade);
- exit: market intent on the bar at 11:14 (fills at the 11:15 open); if the 11:14 bar is missing,
  on the first later bar (K6-L-12, S0.7).
No fill can land in [11:00, 11:02) by construction; the event-window cost of the 11:15 exit, the
fill guard, D9.7 and F are the engine's.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time
from decimal import Decimal

from rules.products import product
from rules.xfa_rules import Refusal
from screening.stage_e_frozen import load_frozen_tables
from strategy.members.k6 import _wasde
from strategy.members.k6._calendar import GRAIN_FULL_SESSIONS
from strategy.members.k6._event_common import (
    BUY,
    SELL,
    bar_open,
    check_exposure,
    ct_open_ns,
    exit_items,
    price_ticks,
)
from strategy.stage_e.interface import (
    LegIntent,
    LegSpec,
    MemberAccountView,
    MinuteView,
    TradingInterval,
    leg_market_intent,
)

MEMBER_ID = "K6-wasdepre-01"
EXPOSURES = ("ZC", "ZS")  # C 600-602
DRIFT_START_BAR = time(8, 30)  # C 631-632: the open of the bar at 08:30
ENTRY_BAR = time(10, 29)  # C 631-634: the close of the bar at 10:29; fills at the 10:30 open
EXIT_BAR = time(11, 14)  # C 635: fills at the 11:15 open
TRADING_WINDOWS = (TradingInterval(time(8, 30), time(8, 31)),  # S0.12
                   TradingInterval(time(10, 29), time(11, 16)))


@dataclass
class WasdePre:
    root: str
    name: str = field(init=False)
    legs: tuple[LegSpec, ...] = field(init=False)
    trading_windows: dict = field(init=False)
    _q: int = field(init=False)
    _tick: Decimal = field(init=False)
    _day: date | None = field(default=None, init=False)
    _start: tuple[int, int] | None = field(default=None, init=False)  # (open ticks, id) at 08:30
    _entry_done: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        check_exposure(self.root, EXPOSURES, MEMBER_ID)
        self.name = f"{MEMBER_ID} {self.root}"
        self.legs = (LegSpec(self.root, True),)
        self.trading_windows = {self.root: TRADING_WINDOWS}
        self._q = load_frozen_tables().vehicles[self.root].q_c
        self._tick = product(self.root).vendor_tick

    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> tuple[LegIntent | Refusal, ...]:
        bar = view.bar(self.root)
        if bar is None:  # no bar: no decision at this minute (never forward fill)
            return ()
        d = bar.trade_date
        if d != self._day:
            self._day, self._start, self._entry_done = d, None, False
        if bar.ts_event_ns == ct_open_ns(d, DRIFT_START_BAR):
            self._start = (price_ticks(bar_open(bar), self._tick), bar.instrument_id)
        if account.position(self.root):
            return exit_items(view, account, self.root, ct_open_ns(d, EXIT_BAR))
        if self._entry_done or bar.ts_event_ns != ct_open_ns(d, ENTRY_BAR):
            return ()
        self._entry_done = True  # the named entry bar is exact: one chance per trade date
        if account.pending.get(self.root, 0) or self._start is None:
            return ()
        if not _wasde.is_wasde_date(d) or d not in GRAIN_FULL_SESSIONS:
            return ()
        start_ticks, start_id = self._start
        if bar.instrument_id != start_id:
            return ()  # C4: the bars of one computation carry different instrument_ids
        drift = price_ticks(bar.close, self._tick) - start_ticks
        if drift == 0:
            return ()
        side = BUY if drift > 0 else SELL
        return (leg_market_intent(view, self.root, side, self._q),)


def make_zc() -> WasdePre:
    return WasdePre("ZC")


def make_zs() -> WasdePre:
    return WasdePre("ZS")


__all__ = ["WasdePre", "make_zc", "make_zs"]
