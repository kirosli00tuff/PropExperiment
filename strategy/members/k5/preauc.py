"""K5-preauc-01, short into the gold AM auction (Stage E.4 Part 2; specs section 4; C 443-537).

MGC only (q_c 1; silver has no vehicle, platinum is out). On every scheduled gold AM auction day of
_releases.GOLD_AM_AUCTIONS (section 11, K5-L-03: a PM-only no-auction day keeps its AM auction),
with T = the table's CT instant of the 10:30 London start (C10, K5-L-02: 04:30, or 05:30 in
5-hour weeks):
- entry: SELL, unconditional (K5-L-10), market intent on the bar at T - 31 (normally 03:59),
  filling at the T - 30 open (04:00); a missing entry bar: no trade that date (S0.6);
- exit: market intent on the bar at T - 2 (normally 04:28), filling at the T - 1 open (04:29); a
  missing exit bar: the first later present bar (S0.7). Hold 29 minutes;
- no entry when the entry bar carries early_halt_ct (S0.8). The only bar read at or before the
  entry is the entry bar, so C4's instrument guard holds by construction (S0.9). No return is
  computed, so no percent-return guard applies (S0.14).
A date not in the table is not traded.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date, time

from rules.xfa_rules import Refusal
from screening.stage_e_frozen import load_frozen_tables
from strategy.members.k5._event_common import (
    SELL,
    check_exposure,
    clock_minute,
    ct_open_ns,
    exit_items,
)
from strategy.members.k5._releases import GOLD_AM_AUCTIONS
from strategy.stage_e.interface import (
    LegIntent,
    LegSpec,
    MemberAccountView,
    MinuteView,
    TradingInterval,
    leg_market_intent,
)

MEMBER_ID = "K5-preauc-01"
EXPOSURES = ("MGC",)  # C 445-450, 536; vehicles: gold -> MGC
SIDE = SELL  # C 488-491: unconditional
ENTRY_DECISION_OFFSET_MIN = -31  # the bar at T - 31; fills at the T - 30 open (C 488-489)
EXIT_DECISION_OFFSET_MIN = -2  # the bar at T - 2; fills at the T - 1 open (C 492-493)
TRADING_WINDOWS = (TradingInterval(time(3, 59), time(4, 30)),  # S0.12: T 04:30 CT
                   TradingInterval(time(4, 59), time(5, 30)))  # T 05:30 CT (5-hour weeks)

# A trade date's plan: (entry decision minute, exit decision minute), CT clock minutes of date d.
DayPlan = tuple[int, int]


def schedule(auctions: tuple[tuple[str, str], ...]) -> dict[date, DayPlan]:
    """Auction date -> (T - 31, T - 2) in CT clock minutes, T = the row's CT auction start."""
    return {date.fromisoformat(day): (clock_minute(t_ct) + ENTRY_DECISION_OFFSET_MIN,
                                      clock_minute(t_ct) + EXIT_DECISION_OFFSET_MIN)
            for day, t_ct in auctions}


@dataclass
class PreAuc:
    root: str
    am_auctions: tuple[tuple[str, str], ...] = GOLD_AM_AUCTIONS  # the frozen table; a test may
    name: str = field(init=False)  # pass another
    legs: tuple[LegSpec, ...] = field(init=False)
    trading_windows: dict = field(init=False)
    _q: int = field(init=False)
    _plans: Mapping[date, DayPlan] = field(init=False)
    _day: date | None = field(default=None, init=False)
    _entry_ns: int | None = field(default=None, init=False)
    _exit_ns: int | None = field(default=None, init=False)
    _entry_done: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        check_exposure(self.root, EXPOSURES, MEMBER_ID)
        self.name = f"{MEMBER_ID} {self.root}"
        self.legs = (LegSpec(self.root, True),)
        self.trading_windows = {self.root: TRADING_WINDOWS}
        self._q = load_frozen_tables().vehicles[self.root].q_c  # S0.3
        self._plans = schedule(self.am_auctions)

    def _new_day(self, day: date) -> None:
        plan = self._plans.get(day)
        self._day = day
        self._entry_done = False
        self._entry_ns = None if plan is None else ct_open_ns(day, plan[0])
        self._exit_ns = None if plan is None else ct_open_ns(day, plan[1])

    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> tuple[LegIntent | Refusal, ...]:
        bar = view.bar(self.root)
        if bar is None:  # no bar: no decision at this minute (never forward fill)
            return ()
        if bar.trade_date != self._day:
            self._new_day(bar.trade_date)
        if account.position(self.root):
            return exit_items(view, account, self.root, self._exit_ns)
        if self._entry_done or bar.ts_event_ns != self._entry_ns:
            return ()
        self._entry_done = True  # the named entry bar is exact: one chance per trade date
        if account.pending.get(self.root, 0) or bar.early_halt_ct is not None:
            return ()
        return (leg_market_intent(view, self.root, SIDE, self._q),)


def make_mgc() -> PreAuc:
    return PreAuc("MGC")


__all__ = ["PreAuc", "make_mgc", "schedule"]
