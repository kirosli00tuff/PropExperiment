"""K5-cp1-01: core port CP1, intraday momentum (Stage E.4 Part 2; reports/stage_e4b_member_specs.md
section 1; catalog reports/stage_e0_catalog_K5.md lines 284-339; D6 line 364).

Rule, instantiated with the metals rows (the clock comes from the frozen tables: gold MGC O 07:20,
C 12:30; copper MHG O 07:10, C 12:00):
- Signal s = sign(close of the bar at O+29 minus open of the trade date's first bar), in vendor
  ticks: MGC 07:49, MHG 07:39. The first bar is the Globex open: the bar opening 17:00 CT on the
  calendar day before d, carrying trade_date d (E.3-L-05). If that bar is missing there is no
  trade.
- Both signal bars must be present and carry one instrument_id, else no trade (D6; E.3-L-06).
  Zero signal: no trade.
- Entry: market intent on the bar at C-31 (MGC 11:59, fills at 12:00; MHG 11:29, fills at 11:30),
  buy if s > 0, sell if s < 0; that exact bar only (S0.6, E.3-L-04).
- Exit: market intent on the first present bar at or after C-2 (MGC 12:28, fills nominally at
  12:29; MHG 11:58, fills at 11:59), resent while refused (S0.7, E.3-L-22). The engine's forced
  flatten at F and its D9.7 exit are the backstops; after either, the member sends nothing more
  that trade date.
- Early halts are not tested here (a port follows D6: the engine's F governs, S0.8).
- Release instants are not read: the engine's D9.5a guard moves a fill that meets one.
One traded leg, q_c contracts (MGC 1, MHG 2). No stop, no filter, no size rule beyond the spec.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict, dataclass, field
from datetime import date, time, timedelta
from decimal import Decimal
from typing import Any

from rules.xfa_rules import Refusal
from strategy.members.k5._port_common import (
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

MEMBER_ID = "K5-cp1-01"
GLOBEX_OPEN_CT = time(17, 0)  # the trade date's first bar, on the calendar day before d (L-05)
SIGNAL_AFTER_O_MIN = 29  # the bar at O+29 (MGC 07:49, MHG 07:39)
ENTRY_BEFORE_C_MIN = 31  # the bar at C-31 (MGC 11:59, MHG 11:29)
EXIT_BEFORE_C_MIN = 2  # the first bar at or after C-2 (MGC 12:28, MHG 11:58)
ONE_DAY = timedelta(days=1)


def _globex_open_ticks(bar: Any, tick: Decimal) -> int:
    """The Globex-open bar's open in vendor ticks; called on that one bar only."""
    # bar.open via asdict: the freeze's static check bans the name `open` (E.3 ruling R-T2-1)
    return to_ticks(asdict(bar)["open"], tick)


@dataclass
class Cp1Momentum:
    """K5-cp1-01 on one exposure; state resets when the bar's trade date changes."""

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
        # S0.12 / E.3-L-17: the Globex-open bar (day -1), the signal bar, and entry bar to C
        self.trading_windows = {self.root: (
            TradingInterval(GLOBEX_OPEN_CT, shift(GLOBEX_OPEN_CT, 1), -1, -1),
            TradingInterval(self._signal_at, shift(self._signal_at, 1)),
            TradingInterval(self._entry_at, self._leg.c),
        )}

    def _reset(self, day: date) -> None:
        self._day, self._first, self._signal, self._entered = day, None, None, False

    def _side(self) -> str | None:
        """D6's signal from the two recorded signal bars; None: no trade that date."""
        if self._first is None or self._signal is None:
            return None  # a signal bar is missing (E.3-L-05)
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
        if opened.date() == day - ONE_DAY and at == GLOBEX_OPEN_CT:
            self._first = (_globex_open_ticks(bar, self._leg.tick), bar.instrument_id)
            return ()
        if opened.date() != day:
            return ()
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


def make_mgc() -> Cp1Momentum:
    return Cp1Momentum("MGC")


def make_mhg() -> Cp1Momentum:
    return Cp1Momentum("MHG")


__all__ = ["MEMBER_ID", "Cp1Momentum", "make_mgc", "make_mhg"]
