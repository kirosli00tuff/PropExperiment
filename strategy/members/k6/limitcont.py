"""K6-limitcont-01, the day after a limit close (Stage E.8; specs section 5; C 496-594).

HE and LE (q_c 1 each). On trade date d in LIVESTOCK_FULL_SESSIONS (S0.8, K6-L-10):
- c = the instrument_id of d's 08:30 bar (O); the 08:30 bar must exist (K6-L-09);
- d-1, d-2, d-3 = the three LIVESTOCK_TRADE_DATES before d (K6-L-07, K6-L-09);
- S(c, x) = D9.7's settlement proxy of trade date x, computed exactly as the engine computes it
  (rules.price_limits.settlement_proxy over settlement_window_ct(root, x), fed as
  screening/stage_e_rules.py feeds it; K6-L-06): the window is SETTLEMENT_WINDOW_LIVESTOCK,
  [12:59:30, 13:00:00) CT, or on an early-halt date the window of the same length ending at the
  halt (LIVESTOCK_EARLY_HALT_CT, when the halt is at or before the regular end); S = the
  volume-weighted close of x's bars opening in [window start floored to its minute, window
  end) with volume > 0; with none, the close of x's last bar opening before the window end
  (fallback R-P2); no such bar: S undefined. Every bar S uses must carry c (K6-L-09);
- L(x) = the initial limit in force on x from LIMIT_PERIODS, in vendor ticks (amount x
  vendor_price_factor / vendor_tick, an integer; K6-L-07);
- event: S(c, d-1) - S(c, d-2) = +L(d-1) ticks (BUY) or -L(d-1) ticks (SELL), exactly (K6-L-08),
  and S(c, d-2) - S(c, d-3) is neither +L(d-2) nor -L(d-2) ticks (d-1's limit was the initial
  one, K6-L-07); any S undefined, or d-1 or d-2 in DROPPED_LIMIT_DATES[root] (R-1b-2): no trade;
- entry: market intent on the bar at 08:44 (fills at the 08:45 open); the 08:44 bar must exist and
  carry c (S0.6, S0.9);
- exit: market intent on the first bar at or after C - 2 = 12:58 (fills at the 12:59 open), or
  earlier by the engine's D9.7 forced exit (S0.7).
The member keeps, from every trade date whose bars it sees (every bar of its leg, in order), what
the proxy needs; a date it has not seen gives no trade. The engine's D9.7 entry guard, forced
exit and locked-market rule, the roll blackout and F are the engine's.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time
from decimal import Decimal

from rules.products import product
from rules.xfa_rules import Refusal
from screening.stage_e_frozen import load_frozen_tables
from strategy.members.k6._calendar import (
    LIVESTOCK_EARLY_HALT_CT,
    LIVESTOCK_FULL_SESSIONS,
    LIVESTOCK_TRADE_DATES,
    previous_trade_date,
)
from strategy.members.k6._event_common import (
    BUY,
    SELL,
    check_exposure,
    ct_open_ns,
    exit_items,
    minus_minutes,
)
from strategy.members.k6._limits import (
    DROPPED_LIMIT_DATES,
    LIMIT_PERIODS,
    SETTLEMENT_WINDOW_LIVESTOCK,
)
from strategy.stage_e.interface import (
    LegIntent,
    LegSpec,
    MemberAccountView,
    MinuteView,
    TradingInterval,
    leg_market_intent,
)

MEMBER_ID = "K6-limitcont-01"
EXPOSURES = ("HE", "LE")  # C 498
ENTRY_BAR = time(8, 44)  # C 540-541: fills at the 08:45 open
EXIT_LEAD_MINUTES = 2  # C 542-543: the exit decision bar is C - 2 (12:58), filling at 12:59
DAYS_BACK = 3  # d-1, d-2, d-3 (C 534)
TRADING_WINDOWS = (TradingInterval(time(8, 30), time(13, 0)),)  # S0.12


def settlement_window(day: date) -> tuple[time, time]:
    """[start, end) CT of trade date ``day``'s D9.7 proxy window (settlement_window_ct for a
    livestock root: the regular window, or the window of the same length ending at an early halt
    at or before the regular end)."""
    start, end = SETTLEMENT_WINDOW_LIVESTOCK
    halt = LIVESTOCK_EARLY_HALT_CT.get(day)
    if halt is None or halt > end:
        return start, end
    length = datetime.combine(day, end) - datetime.combine(day, start)
    return (datetime.combine(day, halt) - length).time(), halt


@dataclass
class ProxyInputs:
    """What D9.7's proxy of one trade date reads, collected as the date's bars stream: the
    volume-weighted close of the bars opening in [lo, end) with volume > 0, else the close of
    the last bar opening before end (rules.price_limits.settlement_proxy)."""

    lo_ns: int  # the window start floored to its minute (the bars whose minute overlaps it)
    end_ns: int  # the window end, exclusive
    num: Decimal = Decimal(0)
    den: int = 0
    vwap_ids: frozenset[int] = frozenset()  # instrument_ids of the bars the weighted close uses
    last_ns: int | None = None
    last_close: Decimal | None = None
    last_id: int | None = None

    def add(self, ts_ns: int, close: float, volume: int, instrument_id: int) -> None:
        if ts_ns >= self.end_ns:
            return
        price = Decimal(repr(close))  # as the engine converts a bar's close
        if self.last_ns is None or ts_ns > self.last_ns:
            self.last_ns, self.last_close, self.last_id = ts_ns, price, instrument_id
        if ts_ns >= self.lo_ns and volume > 0:
            self.num += price * volume
            self.den += volume
            self.vwap_ids = self.vwap_ids | {instrument_id}

    def value(self) -> tuple[Decimal | None, frozenset[int]]:
        """(S, the instrument_ids of the bars S uses); (None, empty) when S is undefined."""
        if self.den > 0:
            return self.num / self.den, self.vwap_ids
        if self.last_close is None or self.last_id is None:
            return None, frozenset()
        return self.last_close, frozenset({self.last_id})


def proxy_inputs_for(day: date) -> ProxyInputs:
    start, end = settlement_window(day)
    lo = time(start.hour, start.minute)
    return ProxyInputs(ct_open_ns(day, lo), ct_open_ns(day, end))


def limit_ticks(root: str, day: date) -> int | None:
    """L(root, day): the initial daily limit in force on ``day`` in vendor ticks, or None when no
    period of LIMIT_PERIODS covers the date."""
    p = product(root)
    for first, last, amount in LIMIT_PERIODS[root]:
        if first <= day <= last:
            ticks = Decimal(amount) * p.vendor_price_factor / p.vendor_tick
            if ticks != ticks.to_integral_value():
                raise ValueError(f"{root} {amount}: not an integer number of vendor ticks")
            return int(ticks)
    return None


def moved_exactly(new: Decimal, old: Decimal, ticks: int, tick: Decimal) -> bool:
    """new - old == ticks x tick, exactly (integer arithmetic on the exact ratios, K6-L-08)."""
    nn, nd = new.as_integer_ratio()
    on, od = old.as_integer_ratio()
    tn, td = tick.as_integer_ratio()
    return (nn * od - on * nd) * td == ticks * tn * nd * od


@dataclass
class LimitCont:
    root: str
    name: str = field(init=False)
    legs: tuple[LegSpec, ...] = field(init=False)
    trading_windows: dict = field(init=False)
    _q: int = field(init=False)
    _open: time = field(init=False)
    _exit: time = field(init=False)
    _tick: Decimal = field(init=False)
    _dropped: frozenset[date] = field(init=False)
    _proxies: dict[date, ProxyInputs] = field(default_factory=dict, init=False)
    _day: date | None = field(default=None, init=False)
    _c: int | None = field(default=None, init=False)
    _entry_done: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        check_exposure(self.root, EXPOSURES, MEMBER_ID)
        self.name = f"{MEMBER_ID} {self.root}"
        self.legs = (LegSpec(self.root, True),)
        self.trading_windows = {self.root: TRADING_WINDOWS}
        tables = load_frozen_tables()
        self._q = tables.vehicles[self.root].q_c
        self._open, close = tables.day_session_ct[self.root]  # O 08:30, C 13:00 (D line 401)
        self._exit = minus_minutes(close, EXIT_LEAD_MINUTES)
        self._tick = product(self.root).vendor_tick
        self._dropped = frozenset(DROPPED_LIMIT_DATES.get(self.root, {}))

    def _new_day(self, day: date) -> None:
        self._day, self._c, self._entry_done = day, None, False
        keep = sorted(self._proxies)[-DAYS_BACK:]  # d-1, d-2, d-3 at most
        self._proxies = {d: self._proxies[d] for d in keep}
        self._proxies[day] = proxy_inputs_for(day)

    def settlement(self, day: date) -> tuple[Decimal | None, frozenset[int]]:
        """S of a seen trade date and the instrument_ids of the bars it uses."""
        inputs = self._proxies.get(day)
        return (None, frozenset()) if inputs is None else inputs.value()

    def event_side(self, d: date, c: int) -> str | None:
        """BUY after a limit-up close of d-1, SELL after a limit-down close, else None."""
        days: list[date] = []
        x: date | None = d
        for _ in range(DAYS_BACK):
            x = None if x is None else previous_trade_date(LIVESTOCK_TRADE_DATES, x)
            if x is None:
                return None
            days.append(x)
        d1, d2, d3 = days
        if d1 in self._dropped or d2 in self._dropped:
            return None  # R-1b-2: L on a dropped date is not tested
        s = []
        for x in (d1, d2, d3):
            value, ids = self.settlement(x)
            if value is None or ids != {c}:
                return None  # S undefined, or a bar S uses carries another instrument_id
            s.append(value)
        s1, s2, s3 = s
        l1, l2 = limit_ticks(self.root, d1), limit_ticks(self.root, d2)
        if l1 is None or l2 is None:
            return None
        if moved_exactly(s2, s3, l2, self._tick) or moved_exactly(s2, s3, -l2, self._tick):
            return None  # d-2 was itself a limit close: d-1's limit was expanded (K6-L-07)
        if moved_exactly(s1, s2, l1, self._tick):
            return BUY
        if moved_exactly(s1, s2, -l1, self._tick):
            return SELL
        return None

    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> tuple[LegIntent | Refusal, ...]:
        bar = view.bar(self.root)
        if bar is None:  # no bar: no decision at this minute (never forward fill)
            return ()
        d = bar.trade_date
        if d != self._day:
            self._new_day(d)
        self._proxies[d].add(bar.ts_event_ns, bar.close, bar.volume, bar.instrument_id)
        if bar.ts_event_ns == ct_open_ns(d, self._open):
            self._c = bar.instrument_id
        if account.position(self.root):
            return exit_items(view, account, self.root, ct_open_ns(d, self._exit))
        if self._entry_done or bar.ts_event_ns != ct_open_ns(d, ENTRY_BAR):
            return ()
        self._entry_done = True  # the named entry bar is exact: one chance per trade date
        if account.pending.get(self.root, 0) or d not in LIVESTOCK_FULL_SESSIONS:
            return ()
        c = self._c
        if c is None or bar.instrument_id != c:
            return ()  # no 08:30 bar, or the entry bar carries another instrument_id
        side = self.event_side(d, c)
        if side is None:
            return ()
        return (leg_market_intent(view, self.root, side, self._q),)


def make_he() -> LimitCont:
    return LimitCont("HE")


def make_le() -> LimitCont:
    return LimitCont("LE")


__all__ = [
    "LimitCont", "ProxyInputs", "limit_ticks", "make_he", "make_le", "moved_exactly",
    "proxy_inputs_for", "settlement_window",
]
