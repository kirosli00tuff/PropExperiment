"""K3-cp2-01: core port CP2, opening-range breakout (Stage E.4 Part 3;
reports/stage_e4c_member_specs.md sections 0-3; catalog reports/stage_e0_catalog_K3.md lines
285-339; D6 line 365, amended).

Copied from strategy/members/k2/cp2.py (E.3, the same 07:20 / 14:00 clock), never imported from it.
Rule, instantiated with the FX row (O 07:20, C 14:00, F 15:08; the clock comes from the frozen
tables, the same on all seven roots):
- Opening range: OR_high = max high, OR_low = min low of the present bars opening in
  [O, O+15) = [07:20, 07:35) of CT date d. No range bar: no trade (E.3-L-08). No minimum bar count
  and no instrument guard (D6 and B-H1 have none).
- Buffer: 4 vendor ticks of the vehicle (K4-L-06): 0.0002 on 6E, 6A, 6C, 6S, 6N; 0.0004 on 6B;
  0.000002 on 6J; equal to the catalog's table of 4 ticks of the exposure's most active contract
  (C lines 305-314). Compared in integer vendor ticks (S0.10).
- Eligible bars: those opening in [O+15, C) = [07:35, 14:00) of CT date d; no entry from 14:00 on.
- Entry: the first eligible bar whose close >= OR_high + 4 ticks buys, <= OR_low - 4 ticks sells;
  a market intent on that bar. The first qualifying bar uses the trade date's one entry, whatever
  the engine does with the intent (E.3-L-08).
- Exit: 75 minutes after the fill, counted as the MES module counts it (B-H1,
  strategy/research/b_reference_breakout/h1_friction_aware_opening_range_breakout.py lines
  147-152; E.3-L-07): the present bars seen while the position is non-zero, from the bar after the
  entry decision bar; on the 75th, a market intent closing the position (fills at the next open),
  resent while refused (E.3-L-22). Or the engine's forced flatten at F if earlier. There is NO exit
  at C-2: the template's C-2 exit is not part of CP2 (E.3-L-07). After an engine-forced exit (F,
  D9.7) the member sends nothing more that trade date.
- Early halts are not tested here (a port: the engine's F and entry skip govern, C lines 49-50).
One traded leg, q_c contracts (= 1 on all seven).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date, time

from rules.xfa_rules import Refusal
from strategy.members.k3._port_common import (
    LegFacts,
    ct_open,
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

MEMBER_ID = "K3-cp2-01"
RANGE_MINUTES = 15  # OR = [O, O+15)
BUFFER_TICKS = 4  # 4 vendor ticks of the vehicle (K4-L-06)
HOLD_BARS = 75  # present bars counted while the position is open (E.3-L-07)
F_REGULAR_CT = time(15, 8)  # F of a regular FX day (D line 394): the trading window's end


@dataclass
class Cp2Breakout:
    """K3-cp2-01 on one exposure; state resets when the bar's trade date changes."""

    root: str
    name: str = field(init=False)
    legs: tuple[LegSpec, ...] = field(init=False)
    trading_windows: dict = field(init=False)
    _leg: LegFacts = field(init=False, repr=False)
    _range_end: time = field(init=False, repr=False)
    _day: date | None = field(default=None, init=False, repr=False)
    _hi: float | None = field(default=None, init=False, repr=False)
    _lo: float | None = field(default=None, init=False, repr=False)
    _triggered: bool = field(default=False, init=False, repr=False)
    _held: int = field(default=0, init=False, repr=False)

    def __post_init__(self) -> None:
        self._leg = leg_facts(self.root)
        self.name = label(MEMBER_ID, self.root)
        self.legs = self._leg.legs
        self._range_end = shift(self._leg.o, RANGE_MINUTES)
        # S0.12 / E.3-L-17: range, eligible bars and the hold, up to F
        self.trading_windows = {self.root: (TradingInterval(self._leg.o, F_REGULAR_CT),)}

    def _reset(self, day: date) -> None:
        self._day, self._hi, self._lo, self._triggered, self._held = day, None, None, False, 0

    def _hold_exit(self, view: MinuteView, account: MemberAccountView
                   ) -> Sequence[LegIntent | Refusal]:
        """B-H1's count: one per present bar with the position open; exit from the 75th on
        while nothing is pending (E.3-L-07, E.3-L-22)."""
        self._held += 1
        position = account.position(self.root)
        if self._held < HOLD_BARS or account.pending.get(self.root, 0):
            return ()
        side = "sell" if position > 0 else "buy"
        return (leg_market_intent(view, self.root, side, abs(position)),)

    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> Sequence[LegIntent | Refusal]:
        bar = view.bar(self.root)
        if bar is None:  # no bar: no decision at this minute (never forward fill)
            return ()
        if bar.trade_date != self._day:
            self._reset(bar.trade_date)
        if self._triggered and account.position(self.root):
            return self._hold_exit(view, account)
        opened = ct_open(bar)
        if opened.date() != bar.trade_date:
            return ()
        at = opened.time()
        if self._leg.o <= at < self._range_end:
            self._hi = bar.high if self._hi is None else max(self._hi, bar.high)
            self._lo = bar.low if self._lo is None else min(self._lo, bar.low)
            return ()
        if self._triggered or self._hi is None or self._lo is None:
            return ()  # the day's entry is used, or no range bar (E.3-L-08)
        if not self._range_end <= at < self._leg.c or not is_flat(account, self.root):
            return ()
        close = to_ticks(bar.close, self._leg.tick)
        if close >= to_ticks(self._hi, self._leg.tick) + BUFFER_TICKS:
            side = "buy"
        elif close <= to_ticks(self._lo, self._leg.tick) - BUFFER_TICKS:
            side = "sell"
        else:
            return ()
        self._triggered = True  # one entry per trade date, even if the engine refuses it
        return (leg_market_intent(view, self.root, side, self._leg.q),)


def make_6e() -> Cp2Breakout:
    return Cp2Breakout("6E")


def make_6a() -> Cp2Breakout:
    return Cp2Breakout("6A")


def make_6b() -> Cp2Breakout:
    return Cp2Breakout("6B")


def make_6c() -> Cp2Breakout:
    return Cp2Breakout("6C")


def make_6j() -> Cp2Breakout:
    return Cp2Breakout("6J")


def make_6s() -> Cp2Breakout:
    return Cp2Breakout("6S")


def make_6n() -> Cp2Breakout:
    return Cp2Breakout("6N")


__all__ = ["BUFFER_TICKS", "MEMBER_ID", "RANGE_MINUTES", "Cp2Breakout", "make_6a", "make_6b",
           "make_6c", "make_6e", "make_6j", "make_6n", "make_6s"]
