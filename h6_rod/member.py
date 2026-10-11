"""The H6 engine member (prereg section 3), one per test and window: CP1's structure
(strategy/members/k1/cp1.py and _port_common.exit_if_due, copied, never imported) with the entry
date and side taken from a per-date schedule (h6_rod.signal.Schedule.entries).

- Entry: on the bar of trade date d opening at C(d)-31 (that exact bar only; it ends at C-30), a
  market intent for one MNQ in the scheduled side; the engine fills it at the next bar's open. The
  one entry decision of the trade date is spent whether or not the engine accepts it (a refused
  entry is never resent).
- Exit: while a position is open and nothing is pending on the leg, a market intent closing it on
  every present bar of the entry's trade date opening at or after C(d)-2 (an accepted exit, or an
  engine-forced one, is pending until it fills; a refused one is not, so it is sent again on the
  next present bar). The engine's forced flatten at F and its D9.7 exit are the backstops.
- A missing bar (None) is never a decision point.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, time

from h6_rod import constants as K
from h6_rod.signal import Entry
from rules.xfa_rules import Refusal
from strategy.stage_e.interface import (
    LegIntent,
    LegSpec,
    MemberAccountView,
    MinuteView,
    TradingInterval,
    leg_market_intent,
)

MEMBER_ID = "E20-H6"


@dataclass
class H6Member:
    """One test's member; ``schedule`` maps trade date -> Entry (h6_rod.signal)."""

    schedule: Mapping[date, Entry]
    test: str = "T1"
    root: str = K.VEHICLE
    name: str = field(init=False)
    legs: tuple[LegSpec, ...] = field(init=False)
    trading_windows: dict = field(init=False)
    _day: date | None = field(default=None, init=False, repr=False)
    _entered: bool = field(default=False, init=False, repr=False)
    _open_day: date | None = field(default=None, init=False, repr=False)
    _exit_from_ns: int | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self.name = f"{MEMBER_ID} {self.test} {self.root}"
        self.legs = (LegSpec(self.root, True),)
        # Nominal and unused on this path (review H6R-9): h6_rod.engine calls run_engine
        # directly, and only screening/stage_e_runner.py's D9 coverage check reads
        # trading_windows. The values sketch a normal day: the signal and entry bar at 14:29,
        # the hold to C (P(prior C) at 14:59 lies on the trade date before).
        self.trading_windows = {self.root: (TradingInterval(time(14, 29), time(15, 0)),)}

    def _exit(self, view: MinuteView, account: MemberAccountView, day: date, ts_ns: int
              ) -> Sequence[LegIntent | Refusal]:
        position = account.position(self.root)
        if position == 0 or account.pending.get(self.root, 0):
            return ()
        if self._exit_from_ns is None or day != self._open_day or ts_ns < self._exit_from_ns:
            return ()
        side = "sell" if position > 0 else "buy"
        return (leg_market_intent(view, self.root, side, abs(position)),)

    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> Sequence[LegIntent | Refusal]:
        bar = view.bar(self.root)
        if bar is None:  # no bar: no decision at this minute (never forward fill)
            return ()
        day = bar.trade_date
        if day != self._day:
            self._day, self._entered = day, False
        if account.position(self.root):
            return self._exit(view, account, day, bar.ts_event_ns)
        entry = self.schedule.get(day)
        if entry is None or self._entered or bar.ts_event_ns != entry.entry_bar_ns:
            return ()
        if account.pending.get(self.root, 0):
            return ()
        self._entered = True  # the one entry decision of the trade date
        self._open_day, self._exit_from_ns = day, entry.exit_from_ns
        return (leg_market_intent(view, self.root, entry.side, K.QUANTITY),)


__all__ = ["MEMBER_ID", "H6Member"]
