"""K3-mehedge-01: month-end equity-hedge rebalancing in the hour before the London fix, on 6J
(Stage E.4 Part 3; reports/stage_e4c_member_specs.md section 6 and section 11; catalog
reports/stage_e0_catalog_K3.md lines 555-647; K3-L-06, K3-L-07).

Only 6J is traded, with the Nikkei 225: the EURO STOXX 50's free history was not obtained, so the
6E trial is not declared and has no factory (specs section 11; C lines 619-620).

Rule:
- Event set: ME(m), the month's last EC-CAL FX trade date (MONTH_ENDS), traded only if ME(m) is in
  FX_FULL_SESSIONS (no early halt and the regular F, K3-L-04, K3-L-11) and not an
  England-and-Wales bank holiday
  (EW_BANK_HOLIDAYS); a month whose ME(m) fails is skipped, never shifted (K3-L-06).
- Signal: R_eq(m) = ln(P_a / P_b) from the literal table _mehedge_signal.MEHEDGE_R_EQ_6J
  (K3-L-07: P_a the Nikkei's last official close on a Tokyo date strictly before ME(m)'s calendar
  date, P_b its last official close in month m-1). No trade if R_eq = 0 or None (a missing close).
  The table's row must name the same ME(m) as MONTH_ENDS (the tests pin that they agree).
- Entry: SELL if R_eq > 0, BUY if R_eq < 0; market intent on the bar at T_L - 61 of CT date ME(m)
  exactly (fills at the T_L - 60 open: 09:00 CT when T_L is 10:00, 10:00 CT in the mismatch weeks
  when T_L is 11:00). T_L is the literal per-date table _clocks.T_L (K3-L-02). A missing T_L - 61
  bar: no trade (E.3-L-04). The only bar read before the entry is that bar (S0.9): no guard.
- Exit: market intent on the first present bar at or after T_L - 4 (fills nominally at the T_L - 3
  open: 09:57 or 10:57 CT), resent while refused (S0.7, E.3-L-22); sent whatever the bar's
  instrument_id (K3-L-03). The engine's forced flatten at F and its D9.7 exit are the backstops;
  after either, the member sends nothing more that date.
One traded leg, q_c contracts (= 1). One entry per month-end. No stop, no filter, no size rule.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, time

from rules.xfa_rules import Refusal
from strategy.members.k3._calendar import EW_BANK_HOLIDAYS, FX_FULL_SESSIONS, MONTH_ENDS
from strategy.members.k3._clocks import T_L
from strategy.members.k3._mehedge_signal import MEHEDGE_R_EQ_6J
from strategy.members.k3._port_common import (
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

MEMBER_ID = "K3-mehedge-01"
ENTRY_BEFORE_TL_MIN = 61  # the bar at T_L - 61; fills at the T_L - 60 open (C 598-600)
EXIT_BEFORE_TL_MIN = 4  # the first bar at or after T_L - 4; fills at T_L - 3 (C 601-602)
WINDOW_END_BEFORE_TL_MIN = 2  # the window ends after the T_L - 3 exit-fill bar (S0.12)


def _hh_mm(text: str) -> time:
    hh, mm = text.split(":")
    return time(int(hh), int(mm))


def hedge_side(r_eq: float | None) -> str | None:
    """C 598-600: SELL if R_eq > 0 (the currency is predicted to depreciate), BUY if R_eq < 0;
    no trade if R_eq = 0 or a close is missing (None)."""
    if r_eq is None or r_eq == 0:
        return None
    return "sell" if r_eq > 0 else "buy"


def event_sides() -> dict[date, str]:
    """ME(m) -> side, for the month-ends that are traded: in FX_FULL_SESSIONS, not an E&W bank
    holiday, with a signal row for the same ME(m) and a non-zero R_eq."""
    full = frozenset(FX_FULL_SESSIONS)
    bank_holidays = frozenset(EW_BANK_HOLIDAYS)
    signal = {month: (me, r_eq) for month, me, r_eq in MEHEDGE_R_EQ_6J}
    out: dict[date, str] = {}
    for month, me in MONTH_ENDS:
        if me not in full or me in bank_holidays or month not in signal:
            continue
        signal_me, r_eq = signal[month]
        side = hedge_side(r_eq) if signal_me == me else None
        if side is not None:
            key = date.fromisoformat(me)
            out[key] = side
    return out


def fix_minutes(day: date) -> tuple[time, time] | None:
    """(entry decision bar T_L - 61, exit bar T_L - 4) on CT date ``day``; None without T_L."""
    t_l = dict(T_L).get(day.isoformat())
    if t_l is None:
        return None
    at = _hh_mm(t_l)
    return shift(at, -ENTRY_BEFORE_TL_MIN), shift(at, -EXIT_BEFORE_TL_MIN)


def trading_windows_for(root: str) -> dict:
    """S0.12: [T_L - 61, T_L - 2) for each CT value T_L takes (10:00 and 11:00)."""
    slots = sorted({_hh_mm(t) for _, t in T_L})
    return {root: tuple(TradingInterval(shift(t, -ENTRY_BEFORE_TL_MIN),
                                        shift(t, -WINDOW_END_BEFORE_TL_MIN)) for t in slots)}


@dataclass
class MonthEndHedge:
    """K3-mehedge-01 on one exposure; state resets when the bar's trade date changes."""

    root: str
    name: str = field(init=False)
    legs: tuple[LegSpec, ...] = field(init=False)
    trading_windows: dict = field(init=False)
    _leg: LegFacts = field(init=False, repr=False)
    _events: Mapping[date, str] = field(init=False, repr=False)
    _day: date | None = field(default=None, init=False, repr=False)
    _side: str | None = field(default=None, init=False, repr=False)
    _entry_at: time | None = field(default=None, init=False, repr=False)
    _exit_at: time | None = field(default=None, init=False, repr=False)
    _entered: bool = field(default=False, init=False, repr=False)

    def __post_init__(self) -> None:
        self._leg = leg_facts(self.root)
        self.name = label(MEMBER_ID, self.root)
        self.legs = self._leg.legs
        self._events = event_sides()
        self.trading_windows = trading_windows_for(self.root)

    def _reset(self, day: date) -> None:
        self._day, self._entered = day, False
        side = self._events.get(day)
        minutes = fix_minutes(day) if side is not None else None
        if minutes is None:
            self._side, self._entry_at, self._exit_at = None, None, None
        else:
            self._side, (self._entry_at, self._exit_at) = side, minutes

    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> Sequence[LegIntent | Refusal]:
        bar = view.bar(self.root)
        if bar is None:  # no bar: no decision at this minute (never forward fill)
            return ()
        if bar.trade_date != self._day:
            self._reset(bar.trade_date)
        if self._side is None or self._entry_at is None or self._exit_at is None:
            return ()  # not a traded month-end
        day = bar.trade_date
        opened = ct_open(bar)
        if account.position(self.root):
            return exit_if_due(view, account, self.root, opened, day, self._exit_at)
        if opened.date() != day or opened.time() != self._entry_at:
            return ()
        if self._entered or not is_flat(account, self.root):
            return ()
        self._entered = True  # the one entry decision of the month-end
        return (leg_market_intent(view, self.root, self._side, self._leg.q),)


def make_6j() -> MonthEndHedge:
    return MonthEndHedge("6J")


__all__ = ["MEMBER_ID", "MonthEndHedge", "event_sides", "fix_minutes", "hedge_side", "make_6j",
           "trading_windows_for"]
