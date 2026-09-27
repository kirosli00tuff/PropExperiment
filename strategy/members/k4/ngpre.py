"""K4-ngpre-01, storage-report day short (Stage E.4; specs section 4; C 384-439).

NG only (q_c 1). On every EC-NGS release date of _releases.NGS (every calendar NGS row less
section 11's drops, K4-L-03), with T = the release instant in CT (K4-L-02: 09:30 for 10:30 ET,
Thursday standard or Friday exception; 11:00 for 12:00 ET, Wednesday or Monday exception):
- entry: SELL, market intent on the bar at T - 91 (standard 07:59), filling at the T - 90 open
  (08:00); a missing entry bar: no trade that date (S0.6);
- exit: market intent on the bar at T + 29 (standard 09:59), filling at the T + 30 open (10:00);
  a missing exit bar: the first later present bar (S0.7);
- no entry when the entry bar carries early_halt_ct (S0.8). The only bar read at or before the
  entry is the entry bar, so C4's instrument guard holds by construction (S0.9). No return is
  computed, so C10 does not apply.
A date not in the table is not traded.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date, time

from rules.xfa_rules import Refusal
from screening.stage_e_frozen import load_frozen_tables
from strategy.members.k4._event_common import (
    SELL,
    check_exposure,
    clock_minute,
    ct_open_ns,
    exit_items,
)
from strategy.members.k4._releases import NGS
from strategy.stage_e.interface import (
    LegIntent,
    LegSpec,
    MemberAccountView,
    MinuteView,
    TradingInterval,
    leg_market_intent,
)

MEMBER_ID = "K4-ngpre-01"
EXPOSURES = ("NG",)  # C 386-387; vehicles: gas -> NG
SIDE = SELL  # C 405-406, 415-416
ENTRY_DECISION_OFFSET_MIN = -91  # the bar at T - 91; fills at the T - 90 open (C 405-406)
EXIT_DECISION_OFFSET_MIN = 29  # the bar at T + 29; fills at the T + 30 open (C 407)
TRADING_WINDOWS = (TradingInterval(time(7, 59), time(10, 1)),  # S0.12: the 09:30 slot
                   TradingInterval(time(9, 29), time(11, 31)))  # the 11:00 CT slot

# A trade date's plan: (entry decision minute, exit decision minute), CT clock minutes of date d.
DayPlan = tuple[int, int]


def schedule(ngs_rows: tuple[tuple[str, str], ...]) -> dict[date, DayPlan]:
    """Release date -> (T - 91, T + 29) in CT clock minutes, T = the row's CT release time."""
    return {date.fromisoformat(day): (clock_minute(t_n) + ENTRY_DECISION_OFFSET_MIN,
                                      clock_minute(t_n) + EXIT_DECISION_OFFSET_MIN)
            for day, t_n in ngs_rows}


@dataclass
class NgPre:
    root: str
    ngs: tuple[tuple[str, str], ...] = NGS  # the frozen table; a test may pass another
    name: str = field(init=False)
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
        self._q = load_frozen_tables().vehicles[self.root].q_c
        self._plans = schedule(self.ngs)

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


def make_ng() -> NgPre:
    return NgPre("NG")


__all__ = ["NgPre", "make_ng", "schedule"]
