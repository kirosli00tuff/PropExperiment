"""K8-wkndbtc-01: the weekend bitcoin move predicts the Monday Nasdaq-100 trade date, traded on
MNQ with MBT as the signal leg (Stage E.9; reports/stage_e9_member_specs.md section 3; catalog
reports/stage_e0_catalog_K8.md lines 490-608; readings K8-L-02, K8-L-03, K8-L-09, K8-L-12).

Rule (every clock time CT; bars are identified per leg by CT date and clock, and trade_date is
checked to equal the trade date the rule names; S0.4, K8-L-02, K7-L-01):
- Dates: Monday trade dates d (weekday 0) with d and its Friday d - 3 both in WKNDBTC_DATES
  (EQUITY and CRYPTO full sessions; S0.8, K8-L-03, K8-L-12).
- P_F = the close of the MBT bar at 14:59 on CT date d - 3 (trade_date d - 3); P_S = the close
  of the MBT bar at 17:59 on CT date d - 1, the Sunday (trade_date d, in both MBT regimes). Both
  present with one instrument_id, else no trade on d. No other MBT bar is read: not 14:58 or
  15:00 on Friday, not 17:58 on Sunday, never a Saturday bar.
- G = P_S / P_F - 1, signed as the integer vendor-tick difference P_S - P_F (exact, K8-L-09):
  G > 0 BUYS q_c of MNQ, G < 0 SELLS, G = 0 is no trade.
- Entry: on the view at Sunday 17:59 (decision 18:00), a market intent on the MNQ bar at 17:59 on
  CT date d - 1 with trade_date d (that exact bar, S0.6; missing: no trade on d), filling at the
  open of its 18:00 bar; only with no position and no pending order; skipped (not deferred) when
  the fill minute 18:00 is in an MNQ guarded interval (C6, S0.10, K8-L-08).
- Exit: market intent closing the whole position on the first present MNQ bar at or after 14:58
  on CT date d (fills nominally at 14:59), resent while refused (S0.7, E.3-L-22). The engine's
  flatten at F, its D9.7 exit and MLL close are the backstops.
- Never an intent on MBT. The engine refuses opens on a roll-blackout date of either leg (D4,
  V16(a)) and when any leg lacks the bar at that minute (D11.5); the member repeats neither.
One traded leg, q_c contracts of MNQ (1).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from typing import Any
from zoneinfo import ZoneInfo

from rules.products import product
from rules.xfa_rules import Refusal
from screening.stage_e_frozen import load_frozen_tables
from strategy.members.k8._calendar import WKNDBTC_DATES
from strategy.members.k8._releases import in_guard
from strategy.stage_e.interface import (
    LegIntent,
    LegSpec,
    MemberAccountView,
    MinuteView,
    TradingInterval,
    leg_market_intent,
)

MEMBER_ID = "K8-wkndbtc-01"
TRADED = "MNQ"  # the one traded leg (C lines 492-495, S0.1)
SIGNAL = "MBT"  # the bitcoin signal leg, read only
CT = ZoneInfo("America/Chicago")
NS_PER_S = 1_000_000_000
NS_PER_MIN = 60 * NS_PER_S

MONDAY = 0  # date.weekday()
FRIDAY_OFFSET_DAYS = -3  # the Friday immediately before the Monday d is CT date d - 3
SUNDAY_OFFSET_DAYS = -1  # the Sunday is CT date d - 1
FRIDAY_BAR_CT = time(14, 59)  # P_F: the MBT bar at 14:59 on CT date d - 3
SUNDAY_BAR_CT = time(17, 59)  # P_S and the MNQ entry bar: 17:59 on CT date d - 1
EXIT_BAR_CT = time(14, 58)  # the exit intent on the MNQ bar at 14:58 on d (fill 14:59)

_WKNDBTC_SET: frozenset[date] = frozenset(WKNDBTC_DATES)


def ct_open(bar: Any) -> datetime:
    """The bar's open (``ts_event_ns``, whole seconds: bars sit on the minute) in CT."""
    return datetime.fromtimestamp(bar.ts_event_ns // NS_PER_S, tz=UTC).astimezone(CT)


def ct_ns(day: date, at: time) -> int:
    """UTC ns of the CT clock ``at`` on CT calendar date ``day``."""
    return int(datetime.combine(day, at, tzinfo=CT).astimezone(UTC).timestamp()) * NS_PER_S


def to_ticks(price: float, tick: Decimal) -> int:
    """round(price / vendor_tick), computed exactly in Decimal."""
    return round(Decimal(repr(price)) / tick)


def is_trade_monday(day: date) -> bool:
    """d is a Monday and both d and d - 3 are in WKNDBTC_DATES (K8-L-12)."""
    friday = day + timedelta(days=FRIDAY_OFFSET_DAYS)
    return day.weekday() == MONDAY and day in _WKNDBTC_SET and friday in _WKNDBTC_SET


def side_of(g_ticks: int) -> str | None:
    """The sign of G as the integer tick difference P_S - P_F; 0 is no trade."""
    if g_ticks > 0:
        return "buy"
    if g_ticks < 0:
        return "sell"
    return None


@dataclass
class WeekendBitcoin:
    """K8-wkndbtc-01: MNQ traded, MBT read. Keeps the latest MBT 14:59 bar of its own trade date
    (CT date = trade date) and the exit instant of the position it opened."""

    root: str = TRADED
    name: str = field(init=False)
    legs: tuple[LegSpec, ...] = field(init=False)
    trading_windows: dict = field(init=False)
    _q: int = field(init=False, repr=False)
    _mbt_tick: Decimal = field(init=False, repr=False)
    _friday: tuple | None = field(default=None, init=False, repr=False)  # (CT date, ticks, id)
    _exit_ns: int | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.root != TRADED:
            raise ValueError(f"{MEMBER_ID} trades {TRADED} only, not {self.root!r}")
        self._q = load_frozen_tables().vehicles[TRADED].q_c
        self._mbt_tick = product(SIGNAL).vendor_tick
        self.name = f"{MEMBER_ID} {TRADED}"
        self.legs = (LegSpec(TRADED, True), LegSpec(SIGNAL, False))
        # S0.12, [start, end) of bar opens: MNQ the Sunday entry bar and its fill bar, the Monday
        # exit bar and its fill bar; MBT the Sunday 17:59 bar and the 14:59 bar of each date
        self.trading_windows = {
            TRADED: (TradingInterval(time(17, 59), time(18, 1), SUNDAY_OFFSET_DAYS,
                                     SUNDAY_OFFSET_DAYS),
                     TradingInterval(EXIT_BAR_CT, time(15, 0))),
            SIGNAL: (TradingInterval(SUNDAY_BAR_CT, time(18, 0), SUNDAY_OFFSET_DAYS,
                                     SUNDAY_OFFSET_DAYS),
                     TradingInterval(FRIDAY_BAR_CT, time(15, 0))),
        }

    def _record_friday(self, bar: Any) -> None:
        """Keep the MBT bar at 14:59 whose CT date is its trade date (P_F candidates)."""
        opened = ct_open(bar)
        if opened.time() == FRIDAY_BAR_CT and opened.date() == bar.trade_date:
            self._friday = (opened.date(), to_ticks(bar.close, self._mbt_tick),
                            bar.instrument_id)

    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> Sequence[LegIntent | Refusal]:
        mbt = view.bar(SIGNAL)
        if mbt is not None:
            self._record_friday(mbt)
        mnq = view.bar(TRADED)
        if mnq is None:  # no MNQ bar: no entry and no exit at this minute
            return ()
        position = account.position(TRADED)
        if position:
            return self._exit(view, account, mnq, position)
        if account.pending.get(TRADED, 0):
            return ()  # S0.6: never an entry while an order is pending
        return self._entry(view, mnq, mbt)

    def _exit(self, view: MinuteView, account: MemberAccountView, bar: Any, position: int
              ) -> Sequence[LegIntent | Refusal]:
        """S0.7: on the first present MNQ bar at or after 14:58 of d, nothing pending."""
        if account.pending.get(TRADED, 0) or self._exit_ns is None:
            return ()
        if bar.ts_event_ns < self._exit_ns:
            return ()
        side = "sell" if position > 0 else "buy"
        return (leg_market_intent(view, TRADED, side, abs(position)),)

    def _entry(self, view: MinuteView, mnq: Any, mbt: Any) -> Sequence[LegIntent | Refusal]:
        opened = ct_open(mnq)
        day = mnq.trade_date
        sunday = day + timedelta(days=SUNDAY_OFFSET_DAYS)
        if opened.time() != SUNDAY_BAR_CT:
            return ()  # not the MNQ bar at 17:59 of CT date d - 1 with trade_date d
        if not is_trade_monday(day):
            return ()
        if mbt is None or mbt.trade_date != day:
            return ()  # P_S: the MBT bar at 17:59 of CT date d - 1 (this minute), trade_date d
        friday = day + timedelta(days=FRIDAY_OFFSET_DAYS)
        if self._friday is None or self._friday[0] != friday:
            return ()  # P_F: the MBT bar at 14:59 of CT date d - 3 is missing
        _, p_f, p_f_id = self._friday
        if p_f_id != mbt.instrument_id:
            return ()  # one instrument_id across P_F and P_S (C line 526)
        side = side_of(to_ticks(mbt.close, self._mbt_tick) - p_f)
        if side is None:
            return ()  # G = 0
        if in_guard(TRADED, mnq.ts_event_ns + NS_PER_MIN):
            return ()  # C6: the 18:00 fill minute is in an MNQ guarded interval: skipped
        self._exit_ns = ct_ns(day, EXIT_BAR_CT)
        return (leg_market_intent(view, TRADED, side, self._q),)


def make_mnq() -> WeekendBitcoin:
    return WeekendBitcoin(TRADED)


__all__ = ["MEMBER_ID", "SIGNAL", "TRADED", "WeekendBitcoin", "is_trade_monday", "make_mnq",
           "side_of"]
