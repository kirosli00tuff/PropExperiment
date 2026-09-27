"""K2-monthend-01: month-end, intraday slices (Stage E.3; reports/stage_e3_member_specs.md
section 8; catalog reports/stage_e0_catalog_K2.md lines 536-592).

Rule (O 07:20 comes from the frozen tables):
- Event set: N = the last EC-CAL trade date of each calendar month, N-1 = the EC-CAL trade date
  before it, from the literal table strategy/members/k2/_month_end.py (S0.11, L-16). Both are
  traded, each independently; a date C4 or the roll blackout excludes is dropped, not moved. A
  trade date not in the table is not traded.
- Entry: BUY, unconditional, market intent on the bar at O = 07:20 of CT date d (that exact bar,
  S0.6, L-04), filling at the 07:21 open.
- C4 exclusions: an early-halt date (the 07:20 bar carries early_halt_ct, S0.8, L-11); a missing
  07:20 bar; the instrument guard, which here covers only the entry decision bar (L-12), so it
  cannot fail. The roll blackout is the engine's (runner step 2).
- Exit: market intent on the bar at 15:04 (fills at the 15:05 open); a missing exit bar sends it
  on the first later bar; resent while refused (S0.7, L-22); or the engine's forced flatten at F.
One traded leg, q_c contracts (= 1).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date, time

from rules.xfa_rules import Refusal
from strategy.members.k2._month_end import MONTH_END
from strategy.members.k2._port_common import (
    LegFacts,
    ct_open,
    exit_if_due,
    is_flat,
    label,
    leg_facts,
    shift,
)
from strategy.stage_e.interface import (
    LegIntent,
    LegSpec,
    MemberAccountView,
    MinuteView,
    TradingInterval,
    leg_market_intent,
)

MEMBER_ID = "K2-monthend-01"
SIDE = "buy"  # unconditional (C 558)
EXIT_BAR_CT = time(15, 4)  # the bar at 15:04, filling at the 15:05 open (C 559)
# N-1 and N of every month in the table, each its own traded date
EVENT_DATES: frozenset[date] = frozenset(
    date.fromisoformat(day) for _, n_minus_1, n in MONTH_END for day in (n_minus_1, n))


@dataclass
class MonthEndSlice:
    """K2-monthend-01 on one exposure; state resets when the bar's trade date changes."""

    root: str
    name: str = field(init=False)
    legs: tuple[LegSpec, ...] = field(init=False)
    trading_windows: dict = field(init=False)
    _leg: LegFacts = field(init=False, repr=False)
    _day: date | None = field(default=None, init=False, repr=False)
    _entered: bool = field(default=False, init=False, repr=False)

    def __post_init__(self) -> None:
        self._leg = leg_facts(self.root)
        self.name = label(MEMBER_ID, self.root)
        self.legs = self._leg.legs
        # S0.12 / L-17: from the entry bar through the exit fill bar (15:05), i.e. [O, 15:06)
        self.trading_windows = {self.root: (TradingInterval(self._leg.o, shift(EXIT_BAR_CT, 2)),)}

    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> Sequence[LegIntent | Refusal]:
        bar = view.bar(self.root)
        if bar is None:  # no bar: no decision at this minute (never forward fill)
            return ()
        if bar.trade_date != self._day:
            self._day, self._entered = bar.trade_date, False
        day = bar.trade_date
        opened = ct_open(bar)
        if account.position(self.root):
            return exit_if_due(view, account, self.root, opened, day, EXIT_BAR_CT)
        if day not in EVENT_DATES or opened.date() != day or opened.time() != self._leg.o:
            return ()
        if bar.early_halt_ct is not None:
            return ()  # C4: an early-halt date is not traded
        if self._entered or not is_flat(account, self.root):
            return ()
        self._entered = True  # the one entry decision of the trade date
        return (leg_market_intent(view, self.root, SIDE, self._leg.q),)


def make_zt() -> MonthEndSlice:
    return MonthEndSlice("ZT")


def make_zf() -> MonthEndSlice:
    return MonthEndSlice("ZF")


def make_zn() -> MonthEndSlice:
    return MonthEndSlice("ZN")


def make_tn() -> MonthEndSlice:
    return MonthEndSlice("TN")


def make_zb() -> MonthEndSlice:
    return MonthEndSlice("ZB")


def make_ub() -> MonthEndSlice:
    return MonthEndSlice("UB")


__all__ = ["EVENT_DATES", "MEMBER_ID", "MonthEndSlice", "make_tn", "make_ub", "make_zb",
           "make_zf", "make_zn", "make_zt"]
