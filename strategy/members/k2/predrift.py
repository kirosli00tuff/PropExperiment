"""K2-predrift-01, pre-release drift into ISM Services (Stage E.3; specs section 7; C 465-534).

ZN and ZB only. On each ISM Services release date (_releases.ISM_SERVICES_DATES, release T = 09:00
CT = 10:00 ET, L-15):
- s = sign(close of the bar at T - 11 = 08:49 minus open of the bar at T - 30 = 08:30), in ticks;
  s = 0: no trade;
- guard (C4, L-12): the 08:30 and 08:49 bars present and carrying one instrument_id, else no
  trade;
- entry: market intent on the bar at 08:49 in direction s, q_c (fills at the 08:50 open);
- exit: market intent on the bar at 09:04 (fills at the 09:05 open, T + 5); a missing exit bar:
  the first later bar.
No entry when the 08:49 bar is missing or carries early_halt_ct (C4). Hold 15 minutes, through the
release by design. The index value is never read.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time
from decimal import Decimal

from rules.products import product
from rules.xfa_rules import Refusal
from screening.stage_e_frozen import load_frozen_tables
from strategy.members.k2._event_common import (
    BUY,
    SELL,
    bar_open_price,
    check_exposure,
    clock_minute,
    ct_open_ns,
    exit_items,
    price_ticks,
)
from strategy.members.k2._releases import ISM_SERVICES_DATES
from strategy.stage_e.interface import (
    LegIntent,
    LegSpec,
    MemberAccountView,
    MinuteView,
    TradingInterval,
    leg_market_intent,
)

MEMBER_ID = "K2-predrift-01"
EXPOSURES = ("ZN", "ZB")  # C 466-469
RELEASE_CT = time(9, 0)  # T: ISM Services at 10:00 ET = 09:00 CT (C 488; L-15)
SIGNAL_START_OFFSET_MIN = -30  # the open of the bar at T - 30 = 08:30 (C 490)
ENTRY_DECISION_OFFSET_MIN = -11  # the close of the bar at T - 11 = 08:49; fills at T - 10 (C 492)
EXIT_DECISION_OFFSET_MIN = 4  # the bar at T + 4 = 09:04; fills at the T + 5 open (C 493)
WINDOW_START_CT = time(8, 30)  # S0.12
WINDOW_END_CT = time(9, 6)


@dataclass
class PreDrift:
    root: str
    name: str = field(init=False)
    legs: tuple[LegSpec, ...] = field(init=False)
    trading_windows: dict = field(init=False)
    _q: int = field(init=False)
    _tick: Decimal = field(init=False)
    _events: frozenset[date] = field(init=False)
    _day: date | None = field(default=None, init=False)
    _start_ns: int | None = field(default=None, init=False)
    _entry_ns: int | None = field(default=None, init=False)
    _exit_ns: int | None = field(default=None, init=False)
    _start_ticks: int | None = field(default=None, init=False)
    _start_instrument: int | None = field(default=None, init=False)
    _entry_done: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        check_exposure(self.root, EXPOSURES, MEMBER_ID)
        self.name = f"{MEMBER_ID} {self.root}"
        self.legs = (LegSpec(self.root, True),)
        self.trading_windows = {self.root: (TradingInterval(WINDOW_START_CT, WINDOW_END_CT),)}
        self._q = load_frozen_tables().vehicles[self.root].q_c
        self._tick = product(self.root).vendor_tick
        self._events = frozenset(date.fromisoformat(d) for d in ISM_SERVICES_DATES)

    def _new_day(self, day: date) -> None:
        t = clock_minute(RELEASE_CT)
        event = day in self._events
        self._day = day
        self._entry_done = False
        self._start_ticks = None
        self._start_instrument = None
        self._start_ns = ct_open_ns(day, t + SIGNAL_START_OFFSET_MIN) if event else None
        self._entry_ns = ct_open_ns(day, t + ENTRY_DECISION_OFFSET_MIN) if event else None
        self._exit_ns = ct_open_ns(day, t + EXIT_DECISION_OFFSET_MIN) if event else None

    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> tuple[LegIntent | Refusal, ...]:
        bar = view.bar(self.root)
        if bar is None:  # no bar: no decision at this minute (never forward fill)
            return ()
        if bar.trade_date != self._day:
            self._new_day(bar.trade_date)
        if bar.ts_event_ns == self._start_ns:
            self._start_ticks = price_ticks(bar_open_price(bar), self._tick)
            self._start_instrument = bar.instrument_id
        if account.position(self.root):
            return exit_items(view, account, self.root, self._exit_ns)
        if self._entry_done or bar.ts_event_ns != self._entry_ns:
            return ()
        self._entry_done = True  # the named entry bar is exact: one chance per trade date
        if account.pending.get(self.root, 0) or bar.early_halt_ct is not None:
            return ()
        if self._start_ticks is None or self._start_instrument != bar.instrument_id:
            return ()  # the 08:30 bar is missing or on another instrument (C4 guard)
        move = price_ticks(bar.close, self._tick) - self._start_ticks
        if move == 0:
            return ()  # s = 0: no trade
        return (leg_market_intent(view, self.root, BUY if move > 0 else SELL, self._q),)


def make_zn() -> PreDrift:
    return PreDrift("ZN")


def make_zb() -> PreDrift:
    return PreDrift("ZB")


__all__ = ["PreDrift", "make_zb", "make_zn"]
