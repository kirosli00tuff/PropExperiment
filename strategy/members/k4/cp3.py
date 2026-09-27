"""K4-cp3-01: core port CP3, prior-close location (Stage E.4; reports/stage_e4_member_specs.md
section 3; catalog reports/stage_e0_catalog_K4.md lines 343-382; D6 line 366; Family H by
reference, as E.3 read it: E.3-L-09, E.3-L-10, E.3-L-11).

Rule, instantiated with the energy row (O 08:00, C 13:30; the clock comes from the frozen tables):
- Daily bar of trade date d, from its bars on CT date d opening in [O, C) = [08:00, 13:30):
  H / L = max high / min low over the present bars, C_d = close of the bar at C-1 = 13:29.
  (O_d, the 08:00 open, enters no condition and is not read; the 08:00 bar must exist.)
- Complete day (Family H): the 08:00 and 13:29 bars exist, no bar of CT date d carries
  early_halt_ct, and all bars in [08:00, 13:30) carry one instrument_id. It is finalised when a
  bar of a later trade date arrives, so day d's own bar never enters day d's condition.
- d-1 = the most recent COMPLETE daily bar of an earlier trade date; incomplete days are dropped
  (E.3-L-09). None yet (warm-up, the window's start): no trade.
- On the bar at O = 08:00 of CT date d (that exact bar, S0.6): no trade if it carries
  early_halt_ct (E.3-L-09, E.3-L-11); instrument guard: d-1's instrument_id must be the 08:00
  bar's; Range = H - L of d-1 in ticks must be > 0; CLV = (C - L) / (H - L) in ticks,
  CLV >= 0.8 buys, CLV <= 0.2 sells (non-strict), else no trade. The cuts are compared exactly in
  integers (E.3-L-19). Market intent on the 08:00 bar (fills at the 08:01 open).
- Exit: market intent on the first present bar at or after C-2 = 13:28 (fills nominally at the
  13:29 open), resent while refused (S0.7, E.3-L-10, E.3-L-22). The engine's forced flatten at F
  and its D9.7 exit are the backstops; after either, nothing more that trade date.
One traded leg, q_c contracts (MCL 4, NG 1).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date, time
from decimal import Decimal
from typing import Any

from rules.xfa_rules import Refusal
from strategy.members.k4._port_common import (
    LegFacts,
    ct_open,
    exit_if_due,
    is_flat,
    label,
    leg_facts,
    shift,
    to_ticks,
)
from strategy.stage_e.interface import (
    LegIntent,
    LegSpec,
    MemberAccountView,
    MinuteView,
    TradingInterval,
    leg_market_intent,
)

MEMBER_ID = "K4-cp3-01"
CLV_BUY_AT_OR_ABOVE = Decimal("0.8")  # CP3 / H6
CLV_SELL_AT_OR_BELOW = Decimal("0.2")  # CP3 / H6
LOOKBACK = 1  # d-1 only; the instrument guard is on that one daily bar
CLOSE_BEFORE_C_MIN = 1  # C_d = close of the bar at C-1 = 13:29
EXIT_BEFORE_C_MIN = 2  # the first bar at or after C-2 = 13:28


@dataclass(frozen=True)
class DailyBar:
    """A COMPLETE daily bar of one trade date, in vendor ticks."""

    trade_date: date
    high: int
    low: int
    close: int
    instrument_id: int


def clv_side(prior: DailyBar) -> str | None:
    """CP3's condition on d-1: Range > 0, then CLV >= 0.8 buys, CLV <= 0.2 sells (non-strict);
    compared as integer cross-products, so no rounding can move a cut."""
    span = prior.high - prior.low
    if span <= 0:
        return None
    num = prior.close - prior.low  # CLV = num / span
    buy_n, buy_d = CLV_BUY_AT_OR_ABOVE.as_integer_ratio()
    sell_n, sell_d = CLV_SELL_AT_OR_BELOW.as_integer_ratio()
    if num * buy_d >= buy_n * span:
        return "buy"
    if num * sell_d <= sell_n * span:
        return "sell"
    return None


@dataclass
class Cp3CloseLocation:
    """K4-cp3-01 on one exposure. Day accumulators reset when the bar's trade date changes; the
    last complete daily bar carries over."""

    root: str
    name: str = field(init=False)
    legs: tuple[LegSpec, ...] = field(init=False)
    trading_windows: dict = field(init=False)
    _leg: LegFacts = field(init=False, repr=False)
    _close_at: time = field(init=False, repr=False)
    _exit_at: time = field(init=False, repr=False)
    _prior: DailyBar | None = field(default=None, init=False, repr=False)  # d-1 (complete)
    _day: date | None = field(default=None, init=False, repr=False)
    _halt: bool = field(default=False, init=False, repr=False)
    _has_open_bar: bool = field(default=False, init=False, repr=False)
    _hi: float | None = field(default=None, init=False, repr=False)
    _lo: float | None = field(default=None, init=False, repr=False)
    _close: float | None = field(default=None, init=False, repr=False)
    _ids: frozenset[int] = field(default=frozenset(), init=False, repr=False)
    _entered: bool = field(default=False, init=False, repr=False)

    def __post_init__(self) -> None:
        self._leg = leg_facts(self.root)
        self.name = label(MEMBER_ID, self.root)
        self.legs = self._leg.legs
        self._close_at = shift(self._leg.c, -CLOSE_BEFORE_C_MIN)
        self._exit_at = shift(self._leg.c, -EXIT_BEFORE_C_MIN)
        # S0.12 / E.3-L-17: the daily bar's [O, C), which also holds the position
        self.trading_windows = {self.root: (TradingInterval(self._leg.o, self._leg.c),)}

    # -- per trade date ----------------------------------------------------------------
    def _complete_bar(self) -> DailyBar | None:
        complete = (self._has_open_bar and self._close is not None and not self._halt
                    and len(self._ids) == 1)
        if not complete or self._day is None or self._hi is None or self._lo is None:
            return None
        tick = self._leg.tick
        (only_id,) = self._ids
        return DailyBar(self._day, to_ticks(self._hi, tick), to_ticks(self._lo, tick),
                        to_ticks(self._close, tick), only_id)

    def _roll(self, day: date) -> None:
        """Finalise the ending trade date (complete bars replace d-1), then start ``day``."""
        finished = self._complete_bar()
        if finished is not None:
            self._prior = finished
        self._day, self._halt, self._has_open_bar, self._entered = day, False, False, False
        self._hi, self._lo, self._close, self._ids = None, None, None, frozenset()

    def _accumulate(self, bar: Any, at: time) -> None:
        if bar.early_halt_ct is not None:  # any bar of CT date d (Family H)
            self._halt = True
        if not self._leg.o <= at < self._leg.c:
            return
        self._ids = self._ids | {bar.instrument_id}
        self._hi = bar.high if self._hi is None else max(self._hi, bar.high)
        self._lo = bar.low if self._lo is None else min(self._lo, bar.low)
        if at == self._leg.o:
            self._has_open_bar = True
        if at == self._close_at:
            self._close = bar.close

    def _entry_side(self, bar: Any) -> str | None:
        """Day d's decision on its 08:00 bar, from d-1 only."""
        if bar.early_halt_ct is not None:
            return None  # an early-halt day d is not traded (E.3-L-09, E.3-L-11)
        prior = self._prior
        if prior is None:
            return None  # warm-up: no complete earlier daily bar
        if prior.instrument_id != bar.instrument_id:
            return None  # instrument guard: d-1 against day d's 08:00 bar
        return clv_side(prior)

    # -- the member contract -----------------------------------------------------------
    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> Sequence[LegIntent | Refusal]:
        bar = view.bar(self.root)
        if bar is None:  # no bar: no decision at this minute (never forward fill)
            return ()
        if bar.trade_date != self._day:
            self._roll(bar.trade_date)
        day = bar.trade_date
        opened = ct_open(bar)
        if opened.date() != day:
            return ()  # the previous CT evening's bars: nothing of day d happens there
        at = opened.time()
        self._accumulate(bar, at)
        if account.position(self.root):
            return exit_if_due(view, account, self.root, opened, day, self._exit_at)
        if at != self._leg.o or self._entered or not is_flat(account, self.root):
            return ()
        self._entered = True  # the one entry decision of the trade date
        side = self._entry_side(bar)
        if side is None:
            return ()
        return (leg_market_intent(view, self.root, side, self._leg.q),)


def make_mcl() -> Cp3CloseLocation:
    return Cp3CloseLocation("MCL")


def make_ng() -> Cp3CloseLocation:
    return Cp3CloseLocation("NG")


__all__ = ["MEMBER_ID", "Cp3CloseLocation", "DailyBar", "clv_side", "make_mcl", "make_ng"]
