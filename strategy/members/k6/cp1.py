"""K6-cp1-01: core port CP1, intraday momentum, on ZC, ZW, ZS, ZM, ZL, HE and LE (Stage E.8;
reports/stage_e8_member_specs.md section 1; catalog reports/stage_e0_catalog_K6.md lines 235-286;
D6 line 364).

Copied in structure from strategy/members/k1/cp1.py (E.7), never imported from it.
Rule, instantiated with the grains row (O 08:30, C 13:15, F 13:18) and the livestock row (O 08:30,
C 13:00, F 13:03); the clock comes from the frozen tables:
- Signal s = sign(close of the bar at O+29 = 08:59 minus open of the trade date's first bar), in
  vendor ticks.
- The trade date's first bar, grains (K6-L-01): the earliest bar carrying trade_date d whose CT
  open is at or after 19:00 CT on the calendar day before d. Normally the 19:00 bar (Sunday 19:00
  for a Monday); a missing 19:00 bar: the first later bar; a date with no evening session (a
  scheduled late open such as 2025-12-26) has no bar before 08:30 of d, so it is the 08:30 bar.
- The trade date's first bar, livestock (K6-L-02, R-03's (b) form): the bar at 08:30 of CT date d
  exactly; missing: no trade.
- Both signal bars must be present and carry one instrument_id, else no trade (D6; E.3-L-06).
  Zero signal: no trade.
- Entry: market intent on the bar at C-31 of CT date d (grains 12:44, fills 12:45; livestock
  12:29, fills 12:30), buy if s > 0, sell if s < 0; that exact bar only (S0.6, E.3-L-04).
- Exit: market intent on the first present bar of CT date d at or after C-2 (grains 13:13, fills
  nominally 13:14; livestock 12:58, fills 12:59), resent while refused (S0.7, E.3-L-22). The
  engine's forced flatten at F and its D9.7 exit are the backstops; after either, the member
  sends nothing more that trade date.
- Early halts are not tested here (a port follows D6: the engine's F governs, C line 89;
  K6-L-18). No release instant is read (C lines 279-282).
One traded leg, q_c contracts (1 on every root). No stop, no filter, no size rule beyond the spec.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Any

from rules.xfa_rules import Refusal
from strategy.members.k6._port_common import (
    CT,
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

MEMBER_ID = "K6-cp1-01"
GRAIN_EVENING_OPEN_CT = time(19, 0)  # grains: first bar at or after 19:00 CT on d-1 (K6-L-01)
SIGNAL_AFTER_O_MIN = 29  # the bar at O+29 = 08:59
ENTRY_BEFORE_C_MIN = 31  # the bar at C-31: grains 12:44, livestock 12:29
EXIT_BEFORE_C_MIN = 2  # the first bar at or after C-2: grains 13:13, livestock 12:58
ONE_DAY = timedelta(days=1)


def _first_bar_open_ticks(bar: Any, tick: Decimal) -> int:
    """The first bar's open in vendor ticks; called on that one bar only."""
    # bar.open via asdict: the freeze's static check bans the name `open` (E.3 ruling R-T2-1)
    return to_ticks(asdict(bar)["open"], tick)


@dataclass
class Cp1Momentum:
    """K6-cp1-01 on one root; state resets when the bar's trade date changes."""

    root: str
    name: str = field(init=False)
    legs: tuple[LegSpec, ...] = field(init=False)
    trading_windows: dict = field(init=False)
    _leg: LegFacts = field(init=False, repr=False)
    _signal_at: time = field(init=False, repr=False)
    _entry_at: time = field(init=False, repr=False)
    _exit_at: time = field(init=False, repr=False)
    _day: date | None = field(default=None, init=False, repr=False)
    _first: tuple[int, int] | None = field(default=None, init=False, repr=False)  # (open, id)
    _signal: tuple[int, int] | None = field(default=None, init=False, repr=False)  # (close, id)
    _entered: bool = field(default=False, init=False, repr=False)

    def __post_init__(self) -> None:
        self._leg = leg_facts(self.root)
        self.name = label(MEMBER_ID, self.root)
        self.legs = self._leg.legs
        self._signal_at = shift(self._leg.o, SIGNAL_AFTER_O_MIN)
        self._entry_at = shift(self._leg.c, -ENTRY_BEFORE_C_MIN)
        self._exit_at = shift(self._leg.c, -EXIT_BEFORE_C_MIN)
        # S0.12 / E.3-L-17: the first bar, the signal bar, and entry bar to C
        if self._leg.is_grain:
            first = TradingInterval(GRAIN_EVENING_OPEN_CT, shift(GRAIN_EVENING_OPEN_CT, 1),
                                    -1, -1)
        else:
            first = TradingInterval(self._leg.o, shift(self._leg.o, 1))
        self.trading_windows = {self.root: (
            first,
            TradingInterval(self._signal_at, shift(self._signal_at, 1)),
            TradingInterval(self._entry_at, self._leg.c),
        )}

    def _reset(self, day: date) -> None:
        self._day, self._first, self._signal, self._entered = day, None, None, False

    def _is_first_bar(self, opened: datetime, day: date) -> bool:
        """The trade date's first bar: grains K6-L-01, livestock K6-L-02."""
        if self._first is not None:
            return False  # already found: only the earliest bar is the first bar
        if self._leg.is_grain:
            return opened >= datetime.combine(day - ONE_DAY, GRAIN_EVENING_OPEN_CT, tzinfo=CT)
        return opened.date() == day and opened.time() == self._leg.o

    def _side(self) -> str | None:
        """D6's signal from the two recorded signal bars; None: no trade that date."""
        if self._first is None or self._signal is None:
            return None  # a signal bar is missing
        (first_open, first_id), (signal_close, signal_id) = self._first, self._signal
        if first_id != signal_id:
            return None  # the two signal bars carry different instrument_ids (E.3-L-06)
        s = signal_close - first_open
        if s == 0:
            return None  # zero signal
        return "buy" if s > 0 else "sell"

    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> Sequence[LegIntent | Refusal]:
        bar = view.bar(self.root)
        if bar is None:  # no bar: no decision at this minute (never forward fill)
            return ()
        if bar.trade_date != self._day:
            self._reset(bar.trade_date)
        day = bar.trade_date
        opened = ct_open(bar)
        at = opened.time()
        if account.position(self.root):
            return exit_if_due(view, account, self.root, opened, day, self._exit_at)
        if self._is_first_bar(opened, day):
            # no return: if every earlier bar is missing, the first bar may be the 08:59 bar
            self._first = (_first_bar_open_ticks(bar, self._leg.tick), bar.instrument_id)
        if opened.date() != day:
            return ()  # the rest of the grain evening (CT date d-1): never a signal or entry bar
        if at == self._signal_at:
            self._signal = (to_ticks(bar.close, self._leg.tick), bar.instrument_id)
            return ()
        if at != self._entry_at or self._entered or not is_flat(account, self.root):
            return ()
        self._entered = True  # the one entry decision of the trade date
        side = self._side()
        if side is None:
            return ()
        return (leg_market_intent(view, self.root, side, self._leg.q),)


def make_zc() -> Cp1Momentum:
    return Cp1Momentum("ZC")


def make_zw() -> Cp1Momentum:
    return Cp1Momentum("ZW")


def make_zs() -> Cp1Momentum:
    return Cp1Momentum("ZS")


def make_zm() -> Cp1Momentum:
    return Cp1Momentum("ZM")


def make_zl() -> Cp1Momentum:
    return Cp1Momentum("ZL")


def make_he() -> Cp1Momentum:
    return Cp1Momentum("HE")


def make_le() -> Cp1Momentum:
    return Cp1Momentum("LE")


__all__ = ["MEMBER_ID", "Cp1Momentum", "make_he", "make_le", "make_zc", "make_zl", "make_zm",
           "make_zs", "make_zw"]
