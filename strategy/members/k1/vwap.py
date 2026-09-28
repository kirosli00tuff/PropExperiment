"""K1-vwap-01: stop-and-reverse around the session VWAP, rewritten to D9's floor (Stage E.7;
reports/stage_e7_member_specs.md section 5; catalog reports/stage_e0_catalog_K1.md lines
502-593; readings K1-L-06..K1-L-10).

Rule (every clock time CT; the bars of trade date d on CT date d, S0.4):
- Dates: d in EQUITY_FULL_SESSIONS (S0.8, K1-L-10); other trade dates are not traded.
- VWAP (K1-L-06): over the present bars b of CT date d opening from 08:30 through bar t,
  sum((H_b + L_b + C_b) x vol_b) and sum(vol_b), prices in integer vendor ticks; known at t's
  close. Sign: s_t = sign(3 x C_t x sum(vol) - sum((H + L + C) x vol)) when nonzero, else
  s_(t-1) (0 before the first sign of the day). sum(vol) = 0: no action on that bar and s is
  not updated.
- Rule window: every bar t opening in [08:30, 14:57), while no order is pending on the leg:
  - flat, s_t != 0, fewer than 20 entry intents today: a market intent of q_c in direction s_t;
  - position opposite to s_t (s_t != 0) and the minimum hold met: an exit intent closing the
    position, then, if fewer than 20 entry intents today, an entry intent of q_c in direction
    s_t, both on bar t (both fill at the next open; never one 2 q_c order, S0.3);
  - otherwise nothing.
- Minimum hold (K1-L-09): a position first seen at the call of bar k (it filled at k's open) is
  exited or reversed only by an intent on a bar opening at or after k + 1 minute.
- Entry cap (K1-L-08): entry intents sent on d, reversal legs included, counted when sent (a
  refused one counts), at most 20; after the 20th, the next opposite signal with the hold met
  exits to flat.
- Missing bar (K1-L-07): from the first bar after a minute of [08:30, t] with no bar (by clock),
  no new entry (flat entries and reversal legs) for the rest of d; an open position keeps the
  rule's exits. A missing 08:30 bar is a gap at the start: no trade on d.
- Instrument change (K1-L-07, C lines 558-559): reference = d's 08:30 bar's instrument_id; from
  the first bar with another id, no new entry for the rest of d, and an open position gets an
  exit intent (on that bar; resent while refused, S0.7).
- Final exit: a market intent on the first present bar at or after C-2 = 14:58 (fills at the
  14:59 open), resent while refused; no rule intent from the 14:57 bar on.
- A position the engine closes leaves the account flat; the rule applies as written at later
  bars (K1-L-09, K7-L-07).
One traded leg, q_c contracts (MNQ 1). No release instant is read.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date, time
from typing import Any

from rules.xfa_rules import Refusal
from strategy.members.k1._event_common import (
    BUY,
    NS_PER_MINUTE,
    ROOT,
    SELL,
    ClockRun,
    LegFacts,
    clock_minute,
    close_items,
    ct_open,
    is_full_session,
    label,
    leg_facts,
    sign,
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

MEMBER_ID = "K1-vwap-01"
TP_PARTS = 3  # TP = (H + L + C) / 3
RULE_END_CT = time(14, 57)  # the rule is evaluated on bars opening in [08:30, 14:57)
EXIT_BEFORE_C_MIN = 2  # the final exit goes on the first bar at or after C-2 = 14:58
MAX_ENTRIES = 20  # D9.3(a): entry intents per trade date, reversal legs included
MIN_HOLD_MINUTES = 1  # D9.3(b): exit intents from the bar at k + 1 min (fill k + 2 or later)


@dataclass
class SessionVwap:
    """K1-vwap-01 on MNQ. Every piece of state is of the current trade date; it resets when the
    bar's trade date changes."""

    root: str = field(default=ROOT, init=False)
    name: str = field(init=False)
    legs: tuple[LegSpec, ...] = field(init=False)
    trading_windows: dict = field(init=False)
    _leg: LegFacts = field(init=False, repr=False)
    _o: int = field(init=False, repr=False)  # clock minutes of O, the rule end and C-2
    _rule_end: int = field(init=False, repr=False)
    _final_exit: int = field(init=False, repr=False)
    _day: date | None = field(default=None, init=False, repr=False)
    _active: bool = field(default=False, init=False, repr=False)
    _run: ClockRun | None = field(default=None, init=False, repr=False)
    _gap: bool = field(default=False, init=False, repr=False)
    _ref_id: int | None = field(default=None, init=False, repr=False)
    _id_changed: bool = field(default=False, init=False, repr=False)
    _sum_vol: int = field(default=0, init=False, repr=False)
    _sum_hlc_vol: int = field(default=0, init=False, repr=False)  # sum((H + L + C) x vol), ticks
    _s: int = field(default=0, init=False, repr=False)
    _entries: int = field(default=0, init=False, repr=False)
    _seen_position: int = field(default=0, init=False, repr=False)
    _held_from_ns: int | None = field(default=None, init=False, repr=False)  # bar k's open

    def __post_init__(self) -> None:
        self._leg = leg_facts()
        self.name = label(MEMBER_ID)
        self.legs = self._leg.legs
        self._o = clock_minute(self._leg.o)
        self._rule_end = clock_minute(RULE_END_CT)
        self._final_exit = clock_minute(self._leg.c) - EXIT_BEFORE_C_MIN
        # S0.12: the VWAP bars from 08:30, the rule window and the 14:59 exit fill bar
        self.trading_windows = {self.root: (TradingInterval(self._leg.o, self._leg.c),)}

    # -- per trade date ----------------------------------------------------------------
    def _roll(self, day: date) -> None:
        self._day, self._active = day, is_full_session(day)
        self._run, self._gap = ClockRun(self._o), False
        self._ref_id, self._id_changed = None, False
        self._sum_vol, self._sum_hlc_vol, self._s, self._entries = 0, 0, 0, 0
        self._seen_position, self._held_from_ns = 0, None

    def _see_position(self, position: int, ts_ns: int) -> None:
        """K1-L-09: the bar at whose call a new position is first seen is its fill bar k."""
        if position != self._seen_position:
            self._seen_position = position
            self._held_from_ns = ts_ns if position else None

    def _observe(self, bar: Any, minute: int) -> None:
        """The clock gap, the instrument reference and the VWAP sums through bar t, then s_t."""
        if self._run is None or not self._run.see(minute):
            self._gap = True
        if minute == self._o:
            self._ref_id = bar.instrument_id
        elif self._ref_id is not None and bar.instrument_id != self._ref_id:
            self._id_changed = True
        tick = self._leg.tick
        close = to_ticks(bar.close, tick)
        hlc = to_ticks(bar.high, tick) + to_ticks(bar.low, tick) + close
        self._sum_vol += bar.volume
        self._sum_hlc_vol += hlc * bar.volume
        if self._sum_vol == 0:
            return  # no action on this bar: s is not updated
        side = sign(TP_PARTS * close * self._sum_vol - self._sum_hlc_vol)
        if side != 0:
            self._s = side  # a tie keeps the previous sign

    def _entry(self, view: MinuteView, direction: int) -> LegIntent | Refusal:
        self._entries += 1  # counted when sent (K1-L-08)
        return leg_market_intent(view, self.root, BUY if direction > 0 else SELL, self._leg.q)

    def _rule(self, view: MinuteView, account: MemberAccountView, position: int, bar: Any
              ) -> Sequence[LegIntent | Refusal]:
        if account.pending.get(self.root, 0):
            return ()  # no intent while an order is pending (K1-L-09)
        s = self._s
        can_enter = self._entries < MAX_ENTRIES and not self._gap and not self._id_changed
        if position == 0:
            if s == 0 or not can_enter:
                return ()
            return (self._entry(view, s),)
        if s == 0 or sign(position) == s:
            return ()
        if (self._held_from_ns is None
                or bar.ts_event_ns < self._held_from_ns + MIN_HOLD_MINUTES * NS_PER_MINUTE):
            return ()  # the minimum hold is not met: wait
        exit_item = leg_market_intent(view, self.root, SELL if position > 0 else BUY,
                                      abs(position))
        if not can_enter:
            return (exit_item,)  # to flat: the cap is reached, or a gap or id change was seen
        return (exit_item, self._entry(view, s))

    # -- the member contract -----------------------------------------------------------
    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> Sequence[LegIntent | Refusal]:
        bar = view.bar(self.root)
        if bar is None:  # no bar: no decision at this minute (never forward fill)
            return ()
        if bar.trade_date != self._day:
            self._roll(bar.trade_date)
        opened = ct_open(bar)
        if not self._active or opened.date() != self._day:
            return ()  # not a full session, or the previous CT evening
        minute = clock_minute(opened.time())
        if minute < self._o:
            return ()
        position = account.position(self.root)
        self._see_position(position, bar.ts_event_ns)
        self._observe(bar, minute)
        if position and (self._id_changed or minute >= self._final_exit):
            return close_items(view, account, self.root)
        if minute >= self._rule_end or self._sum_vol == 0:
            return ()
        return self._rule(view, account, position, bar)


def make_mnq() -> SessionVwap:
    return SessionVwap()


__all__ = ["MAX_ENTRIES", "MEMBER_ID", "SessionVwap", "make_mnq"]
