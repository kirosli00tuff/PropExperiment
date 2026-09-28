"""K7-expiry-01: long MBT before the BRR final-settlement time on MBT's last trading day
(Stage E.6; reports/stage_e6_member_specs.md section 4; catalog reports/stage_e0_catalog_K7.md
lines 420-516; readings K7-L-01, K7-L-03, K7-L-04, K7-L-05).

Rule (every clock time CT; bars of trade date d on CT date d, S0.4):
- Event set: each MBTX date d (strategy.members.k7._calendar, after lead ruling R-1b-1) that is in
  CRYPTO_FULL_SESSIONS and not in VENDOR_DEGRADED (S0.8).
- T_exp(d) from the MBTX table: 16:00 Europe/London in CT (10:00, or 11:00 in the UK/US clock
  mismatch weeks).
- Entry: market intent BUY of q_c on the bar at T_exp - 301 min (04:59 or 05:59), filling at the
  open of the bar at T_exp - 300 min; that exact bar (S0.6): if it is missing, no trade. Long only.
  At most one entry per trade date, only when flat with nothing pending. The rule reads no signal,
  so the entry bar alone meets the instrument guard (S0.9).
- Exit: market intent closing the position on the bar at T_exp - 2 min (09:58 or 10:58), filling
  at T_exp - 1 min; if that bar is missing, on the first later present bar; resent while refused
  (S0.7, E.3-L-22). The engine's F is the backstop; after an engine-forced exit the member does
  nothing more that trade date.
Research window: every MBTX date is a roll-blackout date (E.2a L-11), so the engine refuses every
open and the expected trade count is 0 (K7-L-05). The member is coded as frozen regardless.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date, time

from rules.xfa_rules import Refusal
from strategy.members.k7._calendar import MBTX
from strategy.members.k7._event_common import (
    BUY,
    FILL_DELAY_MIN,
    ROOT,
    LegFacts,
    clock_minute,
    close_items,
    ct_open_ns,
    is_entry_date,
    is_flat,
    label,
    leg_facts,
)
from strategy.stage_e.interface import (
    LegIntent,
    LegSpec,
    MemberAccountView,
    MinuteView,
    TradingInterval,
    leg_market_intent,
)

MEMBER_ID = "K7-expiry-01"
ENTRY_FILL_BEFORE_T_MIN = 300  # the window starts (the entry fills) at T_exp - 300 min
EXIT_FILL_BEFORE_T_MIN = 1  # the exit fills at T_exp - 1 min
T_EXP_SLOTS: tuple[str, ...] = ("10:00", "11:00")  # S0.12: both clock slots
WINDOW_START_CT = time(5, 0)  # S0.12: [T_exp - 300, T_exp - 1] over both slots = [05:00, 11:00)
WINDOW_END_CT = time(11, 0)


def event_schedule() -> dict[date, tuple[int, int]]:
    """trade date d -> (UTC ns of the entry bar T_exp - 301, of the exit bar T_exp - 2) for every
    MBTX date that is an entry date (S0.8)."""
    out: dict[date, tuple[int, int]] = {}
    for text, t_exp in MBTX:
        day = date.fromisoformat(text)
        if not is_entry_date(day):
            continue
        t = clock_minute(t_exp)
        out[day] = (ct_open_ns(day, t - ENTRY_FILL_BEFORE_T_MIN - FILL_DELAY_MIN),
                    ct_open_ns(day, t - EXIT_FILL_BEFORE_T_MIN - FILL_DELAY_MIN))
    return out


@dataclass
class ExpiryLong:
    """K7-expiry-01 on MBT."""

    root: str = field(default=ROOT, init=False)
    name: str = field(init=False)
    legs: tuple[LegSpec, ...] = field(init=False)
    trading_windows: dict = field(init=False)
    _leg: LegFacts = field(init=False, repr=False)
    _events: dict = field(init=False, repr=False)
    _exit_ns: int = field(default=0, init=False, repr=False)  # set by the entry

    def __post_init__(self) -> None:
        self._leg = leg_facts()
        self.name = label(MEMBER_ID)
        self.legs = self._leg.legs
        self.trading_windows = {self.root: (TradingInterval(WINDOW_START_CT, WINDOW_END_CT),)}
        self._events = event_schedule()

    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> Sequence[LegIntent | Refusal]:
        bar = view.bar(self.root)
        if bar is None:  # no bar: no decision at this minute (never forward fill)
            return ()
        if account.position(self.root):
            if bar.ts_event_ns < self._exit_ns:
                return ()
            return close_items(view, account, self.root)
        times = self._events.get(bar.trade_date)
        if times is None or bar.ts_event_ns != times[0] or not is_flat(account, self.root):
            return ()  # only the exact entry bar of an event date: one entry per date (S0.6)
        self._exit_ns = times[1]
        return (leg_market_intent(view, self.root, BUY, self._leg.q),)


def make_mbt() -> ExpiryLong:
    return ExpiryLong()


__all__ = ["ENTRY_FILL_BEFORE_T_MIN", "EXIT_FILL_BEFORE_T_MIN", "MEMBER_ID", "T_EXP_SLOTS",
           "ExpiryLong", "event_schedule", "make_mbt"]
