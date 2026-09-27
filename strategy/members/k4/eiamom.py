"""K4-eiamom-01, WPSR-day release half-hour predicts the last NYSE half-hour (Stage E.4; specs
section 7; C 660-722).

MCL only (q_c 4). Event set: the standard WPSR rows of _releases.WPSR (a Wednesday at 10:30 ET,
T_W = 09:30 CT; section 11's drops already out) whose date is not in _releases.NYSE_NOT_FULL
(EC-NYSE full closures and early closes); an early-halt date (EC-CAL) is not traded (S0.8).
- signal: r3 = ticks(close of the bar at 09:59) - ticks(close of the bar at 09:29); r3 = 0: no
  trade;
- guard (S0.9): the 09:29, 09:59 and 14:29 bars present and carrying one instrument_id;
- entry: market intent on the bar at 14:29, side sign(r3), filling at the 14:30 open; no entry
  when that bar is missing (S0.6) or carries early_halt_ct (S0.8);
- exit: market intent on the first present bar at or after 14:58, filling nominally at the 14:59
  open (S0.7), 9 minutes before F.
No return is computed, so C10 does not apply. A date not in the table is not traded.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date, time
from decimal import Decimal

from rules.products import product
from rules.xfa_rules import Refusal
from screening.stage_e_frozen import load_frozen_tables
from strategy.members.k4._event_common import (
    BUY,
    SELL,
    check_exposure,
    clock_minute,
    ct_open_ns,
    exit_items,
    price_ticks,
)
from strategy.members.k4._releases import NYSE_NOT_FULL, WPSR
from strategy.stage_e.interface import (
    LegIntent,
    LegSpec,
    MemberAccountView,
    MinuteView,
    TradingInterval,
    leg_market_intent,
)

MEMBER_ID = "K4-eiamom-01"
EXPOSURES = ("MCL",)  # C 664-665; vehicles: crude -> MCL
SIGNAL_START_CT = time(9, 29)  # 10:30 ET, the release (C 688-690, 699-701)
SIGNAL_END_CT = time(9, 59)  # 11:00 ET, the end of the third NYSE half-hour
ENTRY_DECISION_CT = time(14, 29)  # fills at the 14:30 open, 15:30 ET (C 691-692)
EXIT_DECISION_CT = time(14, 58)  # the first bar at or after 14:58; fills at 14:59 (C 693-694)
TRADING_WINDOWS = (TradingInterval(time(9, 29), time(10, 0)),  # S0.12
                   TradingInterval(time(14, 29), time(15, 0)))

# One captured signal bar: (close in integer ticks, instrument_id).
Capture = tuple[int, int]


def event_dates(wpsr: Sequence[tuple[str, str, int, bool]], nyse_not_full: Sequence[str]
                ) -> frozenset[date]:
    """The standard WPSR Wednesdays that are NYSE full sessions (section 7 event set)."""
    not_full = frozenset(nyse_not_full)
    return frozenset(date.fromisoformat(day) for day, _t_w, _weekday, standard in wpsr
                     if standard and day not in not_full)


@dataclass
class EiaMom:
    root: str
    wpsr: tuple[tuple[str, str, int, bool], ...] = WPSR  # the frozen tables; a test may pass
    nyse_not_full: tuple[str, ...] = NYSE_NOT_FULL  # others
    name: str = field(init=False)
    legs: tuple[LegSpec, ...] = field(init=False)
    trading_windows: dict = field(init=False)
    _q: int = field(init=False)
    _tick: Decimal = field(init=False)
    _events: frozenset[date] = field(init=False)
    _day: date | None = field(default=None, init=False)
    _start_ns: int | None = field(default=None, init=False)
    _end_ns: int | None = field(default=None, init=False)
    _entry_ns: int | None = field(default=None, init=False)
    _exit_ns: int | None = field(default=None, init=False)
    _start: Capture | None = field(default=None, init=False)
    _end: Capture | None = field(default=None, init=False)
    _entry_done: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        check_exposure(self.root, EXPOSURES, MEMBER_ID)
        self.name = f"{MEMBER_ID} {self.root}"
        self.legs = (LegSpec(self.root, True),)
        self.trading_windows = {self.root: TRADING_WINDOWS}
        self._q = load_frozen_tables().vehicles[self.root].q_c
        self._tick = product(self.root).vendor_tick
        self._events = event_dates(self.wpsr, self.nyse_not_full)

    def _new_day(self, day: date) -> None:
        event = day in self._events
        self._day = day
        self._entry_done = False
        self._start = self._end = None
        self._start_ns = ct_open_ns(day, clock_minute(SIGNAL_START_CT)) if event else None
        self._end_ns = ct_open_ns(day, clock_minute(SIGNAL_END_CT)) if event else None
        self._entry_ns = ct_open_ns(day, clock_minute(ENTRY_DECISION_CT)) if event else None
        self._exit_ns = ct_open_ns(day, clock_minute(EXIT_DECISION_CT)) if event else None

    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> tuple[LegIntent | Refusal, ...]:
        bar = view.bar(self.root)
        if bar is None:  # no bar: no decision at this minute (never forward fill)
            return ()
        if bar.trade_date != self._day:
            self._new_day(bar.trade_date)
        if bar.ts_event_ns == self._start_ns:
            self._start = (price_ticks(bar.close, self._tick), bar.instrument_id)
        elif bar.ts_event_ns == self._end_ns:
            self._end = (price_ticks(bar.close, self._tick), bar.instrument_id)
        if account.position(self.root):
            return exit_items(view, account, self.root, self._exit_ns)
        if self._entry_done or bar.ts_event_ns != self._entry_ns:
            return ()
        self._entry_done = True  # the named entry bar is exact: one chance per trade date
        if account.pending.get(self.root, 0) or bar.early_halt_ct is not None:
            return ()
        start, end = self._start, self._end
        if start is None or end is None:
            return ()  # a signal bar is missing
        if not start[1] == end[1] == bar.instrument_id:
            return ()  # the 09:29, 09:59 and 14:29 bars span two contracts (C4 guard)
        r3 = end[0] - start[0]
        if r3 == 0:
            return ()  # r3 = 0: no trade
        return (leg_market_intent(view, self.root, BUY if r3 > 0 else SELL, self._q),)


def make_mcl() -> EiaMom:
    return EiaMom("MCL")


__all__ = ["EiaMom", "event_dates", "make_mcl"]
