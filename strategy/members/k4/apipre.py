"""K4-apipre-01, API-to-EIA continuation (Stage E.4; specs section 5; C 514-587).

MCL only (q_c 4). Event set (K4-L-04): the Wednesdays W of the standard WPSR rows of
_releases.WPSR (a Wednesday at 10:30 ET, not an exception; section 11's drops already out) whose
Tuesday W-1 is in _calendar.ENERGY_FULL_SESSIONS (K4-L-13: a Tuesday outside that table is not a
full session), whose Monday W-2 is not in _releases.FEDERAL_MONDAY_HOLIDAYS, and that are not in
_releases.API_DROPPED_WEEKS. The API bulletin and the calendar's API rows are never read.
- signal: R_API = ticks(close of the 15:39 bar) - ticks(close of the 15:24 bar), both on CT date
  W-1 (the Tuesday's trade date, after F and the 13:30 settlement); R_API = 0: no trade;
- guard (S0.9): the 15:24 and 15:39 bars of W-1 and the 07:29 bar of W present and carrying one
  instrument_id, else no trade;
- entry: market intent on the bar at 07:29 of W, side sign(R_API), filling at the 07:30 open;
  no entry when that bar is missing (S0.6) or carries early_halt_ct (S0.8);
- exit: market intent on the bar at 09:28 of W, filling at the 09:29 open, before the 09:30
  release; a missing exit bar: the first later present bar (S0.7).
The Tuesday's two closes are the only state carried across a trade-date change; they are used
only on the trade date that follows that Tuesday on the calendar (W = W-1 + 1 day).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date, time, timedelta
from decimal import Decimal

from rules.products import product
from rules.xfa_rules import Refusal
from screening.stage_e_frozen import load_frozen_tables
from strategy.members.k4._calendar import ENERGY_FULL_SESSIONS
from strategy.members.k4._event_common import (
    BUY,
    SELL,
    check_exposure,
    clock_minute,
    ct_open_ns,
    exit_items,
    price_ticks,
)
from strategy.members.k4._releases import API_DROPPED_WEEKS, FEDERAL_MONDAY_HOLIDAYS, WPSR
from strategy.stage_e.interface import (
    LegIntent,
    LegSpec,
    MemberAccountView,
    MinuteView,
    TradingInterval,
    leg_market_intent,
)

MEMBER_ID = "K4-apipre-01"
EXPOSURES = ("MCL",)  # C 518-519; vehicles: crude -> MCL
SIGNAL_START_CT = time(15, 24)  # Tuesday W-1 (C 540-543, 561-566)
SIGNAL_END_CT = time(15, 39)
ENTRY_DECISION_CT = time(7, 29)  # Wednesday W; fills at the 07:30 open (C 544-545)
EXIT_DECISION_CT = time(9, 28)  # fills at the 09:29 open (C 546-547)
ONE_DAY = timedelta(days=1)
TRADING_WINDOWS = (TradingInterval(time(15, 24), time(15, 25)),  # S0.12, K4-L-07: offset 0
                   TradingInterval(time(15, 39), time(15, 40)),
                   TradingInterval(time(7, 29), time(9, 30)))

# One captured signal bar: (close in integer ticks, instrument_id).
Capture = tuple[int, int]


def event_wednesdays(wpsr: Sequence[tuple[str, str, int, bool]], full_sessions: Sequence[str],
                     monday_holidays: Sequence[str], api_dropped: Sequence[str]
                     ) -> frozenset[date]:
    """The standard weeks' Wednesdays W (section 5 event set; K4-L-04, K4-L-13)."""
    full, holidays, dropped = frozenset(full_sessions), frozenset(monday_holidays), frozenset(
        api_dropped)
    return frozenset(
        w for w in (date.fromisoformat(day) for day, _t_w, _weekday, standard in wpsr if standard)
        if (w - ONE_DAY).isoformat() in full and (w - 2 * ONE_DAY).isoformat() not in holidays
        and w.isoformat() not in dropped)


@dataclass
class ApiPre:
    root: str
    wpsr: tuple[tuple[str, str, int, bool], ...] = WPSR  # the frozen tables; a test may pass
    full_sessions: tuple[str, ...] = ENERGY_FULL_SESSIONS  # others
    monday_holidays: tuple[str, ...] = FEDERAL_MONDAY_HOLIDAYS
    api_dropped: tuple[str, ...] = API_DROPPED_WEEKS
    name: str = field(init=False)
    legs: tuple[LegSpec, ...] = field(init=False)
    trading_windows: dict = field(init=False)
    _q: int = field(init=False)
    _tick: Decimal = field(init=False)
    _events: frozenset[date] = field(init=False)
    _day: date | None = field(default=None, init=False)
    _entry_ns: int | None = field(default=None, init=False)
    _exit_ns: int | None = field(default=None, init=False)
    _entry_done: bool = field(default=False, init=False)
    _r_api: int | None = field(default=None, init=False)
    _signal_id: int | None = field(default=None, init=False)
    _tue_day: date | None = field(default=None, init=False)
    _tue_start_ns: int | None = field(default=None, init=False)
    _tue_end_ns: int | None = field(default=None, init=False)
    _tue_start: Capture | None = field(default=None, init=False)
    _tue_end: Capture | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        check_exposure(self.root, EXPOSURES, MEMBER_ID)
        self.name = f"{MEMBER_ID} {self.root}"
        self.legs = (LegSpec(self.root, True),)
        self.trading_windows = {self.root: TRADING_WINDOWS}
        self._q = load_frozen_tables().vehicles[self.root].q_c
        self._tick = product(self.root).vendor_tick
        self._events = event_wednesdays(self.wpsr, self.full_sessions, self.monday_holidays,
                                        self.api_dropped)

    def _signal_for(self, wednesday: date) -> tuple[int | None, int | None]:
        """(R_API, instrument_id) from the captures of the Tuesday W-1, or (None, None) when that
        Tuesday was not captured, a signal bar is missing or the two carry two instrument_ids."""
        start, end = self._tue_start, self._tue_end
        if self._tue_day != wednesday - ONE_DAY or start is None or end is None:
            return None, None
        if start[1] != end[1]:
            return None, None
        return end[0] - start[0], start[1]

    def _new_day(self, day: date) -> None:
        self._day = day
        self._entry_done = False
        event = day in self._events
        self._entry_ns = ct_open_ns(day, clock_minute(ENTRY_DECISION_CT)) if event else None
        self._exit_ns = ct_open_ns(day, clock_minute(EXIT_DECISION_CT)) if event else None
        self._r_api, self._signal_id = self._signal_for(day) if event else (None, None)
        if day + ONE_DAY in self._events:  # day is the Tuesday W-1 of an event Wednesday
            self._tue_day = day
            self._tue_start_ns = ct_open_ns(day, clock_minute(SIGNAL_START_CT))
            self._tue_end_ns = ct_open_ns(day, clock_minute(SIGNAL_END_CT))
            self._tue_start = self._tue_end = None

    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> tuple[LegIntent | Refusal, ...]:
        bar = view.bar(self.root)
        if bar is None:  # no bar: no decision at this minute (never forward fill)
            return ()
        if bar.trade_date != self._day:
            self._new_day(bar.trade_date)
        if bar.ts_event_ns == self._tue_start_ns:
            self._tue_start = (price_ticks(bar.close, self._tick), bar.instrument_id)
        elif bar.ts_event_ns == self._tue_end_ns:
            self._tue_end = (price_ticks(bar.close, self._tick), bar.instrument_id)
        if account.position(self.root):
            return exit_items(view, account, self.root, self._exit_ns)
        if self._entry_done or bar.ts_event_ns != self._entry_ns:
            return ()
        self._entry_done = True  # the named entry bar is exact: one chance per trade date
        if account.pending.get(self.root, 0) or bar.early_halt_ct is not None:
            return ()
        if self._r_api is None or self._signal_id != bar.instrument_id:
            return ()  # a Tuesday signal bar is missing, or the three bars span two contracts
        if self._r_api == 0:
            return ()  # R_API = 0: no trade
        side = BUY if self._r_api > 0 else SELL
        return (leg_market_intent(view, self.root, side, self._q),)


def make_mcl() -> ApiPre:
    return ApiPre("MCL")


__all__ = ["ApiPre", "event_wednesdays", "make_mcl"]
