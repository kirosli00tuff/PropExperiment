"""K3-ecbfix-01, euro: dollar strength into the ECB fix, dollar weakness after it (Stage E.4 Part 3;
specs section 7; C 648-725).

6E only (q_c 1). Event set: every trade date d in FX_FULL_SESSIONS that is not in TGT_CLOSING_DAYS
(C 684-685). With T_E = the _clocks.T_E row of d (07:15 CT, or 08:15 CT in the C9 mismatch weeks),
two legs, sequential, at most one position (C 686-693, K3-L-05):
- leg 1 (SELL): market intent on the bar at 00:59 CT on d, filling at the 01:00 open; a missing
  00:59 bar: no leg 1 (S0.6). Exit: market intent on the bar at T_E - 1, filling at the T_E open;
  a missing exit bar: the first later present bar (S0.7).
- leg 2 (BUY): market intent on the bar at T_E, filling at the T_E + 1 open, only when the account
  is flat with no pending order at that bar (K3-L-05: if leg 1's exit is still pending or leg 1 is
  still open at T_E, there is no leg 2 that day) AND leg 1 opened that trade date and was closed by
  the member's own exit (K3-L-12: a missing 00:59 bar or a refused leg 1 intent means the pair
  never started, so no leg 2); a missing T_E bar: no leg 2. Exit: market intent on the bar at
  15:04 CT, filling at the 15:05 open; a missing exit bar: the first later present bar (the
  engine's F at 15:08 is the backstop).
- guard: each leg reads only its own entry bar (S0.9).
- an engine-closed leg 1 (D9.7 or any engine close before the member's own exit) ends the day: no
  leg 2 (S0.7: "makes no further entry that trade date").
The legs are told apart by the position's sign: leg 1 is short, leg 2 long.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time

from rules.xfa_rules import Refusal
from screening.stage_e_frozen import load_frozen_tables
from strategy.members.k3._calendar import FX_FULL_SESSIONS, TGT_CLOSING_DAYS
from strategy.members.k3._clocks import T_E
from strategy.members.k3._event_common import (
    BUY,
    SELL,
    check_exposure,
    clock_minute,
    clock_table,
    ct_open_ns,
    exit_items,
    iso_dates,
)
from strategy.stage_e.interface import (
    LegIntent,
    LegSpec,
    MemberAccountView,
    MinuteView,
    TradingInterval,
    leg_market_intent,
)

MEMBER_ID = "K3-ecbfix-01"
EXPOSURES = ("6E",)  # C 650-651
LEG1_ENTRY_DECISION_CT = "00:59"  # fills at the 01:00 open (C 687)
LEG1_EXIT_DECISION_OFFSET_MIN = -1  # the bar at T_E - 1; fills at the T_E open (C 688-690)
LEG2_ENTRY_DECISION_OFFSET_MIN = 0  # the bar at T_E; fills at the T_E + 1 open (C 691)
LEG2_EXIT_DECISION_CT = "15:04"  # fills at the 15:05 open (C 692-693)
TRADING_WINDOWS = (TradingInterval(time(0, 59), time(15, 6)),)  # S0.12

Rows = tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class EcbPlan:
    """One event date's four decision bars, as UTC ns of the bars' opens (CT date d)."""

    leg1_entry_ns: int
    leg1_exit_ns: int
    leg2_entry_ns: int
    leg2_exit_ns: int


def event_dates(full_sessions: tuple[str, ...], tgt_closing_days: tuple[str, ...]) -> list[date]:
    """Every full session that is not a TARGET closing day, oldest first."""
    tgt = iso_dates(tgt_closing_days)
    return [d for d in sorted(iso_dates(full_sessions)) if d not in tgt]


def schedule(t_e: Rows, full_sessions: tuple[str, ...], tgt_closing_days: tuple[str, ...]
             ) -> dict[date, EcbPlan]:
    """Event date -> its EcbPlan on CT date d, from the date's T_E."""
    clock = clock_table(t_e)
    out: dict[date, EcbPlan] = {}
    for d in event_dates(full_sessions, tgt_closing_days):
        if d not in clock:
            raise ValueError(f"{MEMBER_ID}: no T_E row for event date {d}")
        t = clock[d]
        out[d] = EcbPlan(ct_open_ns(d, clock_minute(LEG1_ENTRY_DECISION_CT)),
                         ct_open_ns(d, t + LEG1_EXIT_DECISION_OFFSET_MIN),
                         ct_open_ns(d, t + LEG2_ENTRY_DECISION_OFFSET_MIN),
                         ct_open_ns(d, clock_minute(LEG2_EXIT_DECISION_CT)))
    return out


@dataclass
class EcbFix:
    root: str
    t_e: Rows = T_E  # the frozen tables; a test may pass others
    full_sessions: tuple[str, ...] = FX_FULL_SESSIONS
    tgt_closing_days: tuple[str, ...] = TGT_CLOSING_DAYS
    name: str = field(init=False)
    legs: tuple[LegSpec, ...] = field(init=False)
    trading_windows: dict = field(init=False)
    _plans: dict[date, EcbPlan] = field(init=False)
    _q: int = field(init=False)
    _day: date | None = field(default=None, init=False)
    _plan: EcbPlan | None = field(default=None, init=False)
    _leg1_done: bool = field(default=False, init=False)  # the 00:59 decision has passed
    _leg1_held: bool = field(default=False, init=False)  # a leg 1 short was seen open
    _leg1_exit_sent: bool = field(default=False, init=False)  # the member sent leg 1's exit
    _leg2_done: bool = field(default=False, init=False)  # the T_E decision has passed

    def __post_init__(self) -> None:
        check_exposure(self.root, EXPOSURES, MEMBER_ID)
        self.name = f"{MEMBER_ID} {self.root}"
        self.legs = (LegSpec(self.root, True),)
        self.trading_windows = {self.root: TRADING_WINDOWS}
        self._plans = schedule(self.t_e, self.full_sessions, self.tgt_closing_days)
        self._q = load_frozen_tables().vehicles[self.root].q_c  # S0.3

    def _new_day(self, day: date) -> None:
        self._day = day
        self._plan = self._plans.get(day)
        self._leg1_done = self._leg1_held = self._leg1_exit_sent = self._leg2_done = False

    def _exit(self, view: MinuteView, account: MemberAccountView, plan: EcbPlan, position: int
              ) -> tuple[LegIntent | Refusal, ...]:
        """S0.7 for the open leg: leg 1 (short) at T_E - 1, leg 2 (long) at 15:04."""
        if position < 0:
            self._leg1_held = True
            items = exit_items(view, account, self.root, plan.leg1_exit_ns)
            self._leg1_exit_sent = self._leg1_exit_sent or bool(items)
            return items
        return exit_items(view, account, self.root, plan.leg2_exit_ns)

    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> tuple[LegIntent | Refusal, ...]:
        bar = view.bar(self.root)
        if bar is None:  # no bar: no decision at this minute (never forward fill)
            return ()
        if bar.trade_date != self._day:
            self._new_day(bar.trade_date)
        plan = self._plan
        if plan is None:
            return ()  # not an event date
        position = account.position(self.root)
        if position:
            return self._exit(view, account, plan, position)
        flat = not account.pending.get(self.root, 0)
        if not self._leg1_done and bar.ts_event_ns == plan.leg1_entry_ns:
            self._leg1_done = True  # the named entry bar is exact: one chance
            return (leg_market_intent(view, self.root, SELL, self._q),) if flat else ()
        if not self._leg2_done and bar.ts_event_ns == plan.leg2_entry_ns:
            self._leg2_done = True  # the named entry bar is exact: one chance
            leg1_closed_by_member = self._leg1_held and self._leg1_exit_sent  # K3-L-12, S0.7
            if flat and leg1_closed_by_member:
                return (leg_market_intent(view, self.root, BUY, self._q),)
        return ()


def make_6e() -> EcbFix:
    return EcbFix("6E")


__all__ = ["EcbFix", "EcbPlan", "event_dates", "make_6e", "schedule"]
