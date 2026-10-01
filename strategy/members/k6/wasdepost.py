"""K6-wasdepost-01, WASDE-day post-release continuation (Stage E.8; specs section 7; C 682-743).

ZC only (q_c 1). On trade date d with is_wasde_date(d) (EC-WASDE after C9a's drop rule, K6-L-11)
and d in GRAIN_FULL_SESSIONS (S0.8, K6-L-10); T = 11:00 CT is fixed:
- signal: R = close of the bar at 11:14 minus close of the bar at 10:59, in integer vendor ticks;
  both bars present and carrying one instrument_id (S0.9); R = 0: no trade;
- entry: market intent on the bar at 11:14 (fills at the 11:15 open) in the direction of sign(R)
  (S0.6: the 11:14 bar is the entry bar; missing, no trade);
- exit: market intent on the first bar at or after 13:13 (fills at the 13:14 open; S0.7).
The event-window cost of the 11:15 entry, the fill guard, D9.7's entry guard and forced exit and
F are the engine's.
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

MEMBER_ID = "K6-wasdepost-01"
EXPOSURES = ("ZC",)  # C 684-685
SIGNAL_BAR = time(10, 59)  # C 707-708: the close of the bar at 10:59
ENTRY_BAR = time(11, 14)  # C 707-710: the close of the bar at 11:14; fills at the 11:15 open
EXIT_BAR = time(13, 13)  # C 711: fills at the 13:14 open
TRADING_WINDOWS = (TradingInterval(time(10, 59), time(13, 15)),)  # S0.12


@dataclass
class WasdePost:
    root: str
    name: str = field(init=False)
    legs: tuple[LegSpec, ...] = field(init=False)
    trading_windows: dict = field(init=False)
    _q: int = field(init=False)
    _tick: Decimal = field(init=False)
    _day: date | None = field(default=None, init=False)
    _signal: tuple[int, int] | None = field(default=None, init=False)  # (close ticks, id), 10:59
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
            self._day, self._signal, self._entry_done = d, None, False
        if bar.ts_event_ns == ct_open_ns(d, SIGNAL_BAR):
            self._signal = (price_ticks(bar.close, self._tick), bar.instrument_id)
        if account.position(self.root):
            return exit_items(view, account, self.root, ct_open_ns(d, EXIT_BAR))
        if self._entry_done or bar.ts_event_ns != ct_open_ns(d, ENTRY_BAR):
            return ()
        self._entry_done = True  # the named entry bar is exact: one chance per trade date
        if account.pending.get(self.root, 0) or self._signal is None:
            return ()
        if not _wasde.is_wasde_date(d) or d not in GRAIN_FULL_SESSIONS:
            return ()
        signal_ticks, signal_id = self._signal
        if bar.instrument_id != signal_id:
            return ()  # C4: the bars of one computation carry different instrument_ids
        response = price_ticks(bar.close, self._tick) - signal_ticks
        if response == 0:
            return ()
        side = BUY if response > 0 else SELL
        return (leg_market_intent(view, self.root, side, self._q),)


def make_zc() -> WasdePost:
    return WasdePost("ZC")


__all__ = ["WasdePost", "make_zc"]
