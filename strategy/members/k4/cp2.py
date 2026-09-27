"""K4-cp2-01: core port CP2, opening-range breakout (Stage E.4; reports/stage_e4_member_specs.md
section 2; catalog reports/stage_e0_catalog_K4.md lines 283-342; D6 line 365).

Rule, instantiated with the energy row (O 08:00, C 13:30; the clock comes from the frozen tables):
- Opening range: OR_high = max high, OR_low = min low of the present bars opening in
  [O, O+15) = [08:00, 08:15) of CT date d. No range bar: no trade (E.3-L-08). No minimum bar
  count and no instrument guard (D6 and B-H1 have none).
- Buffer: 4 vendor ticks of the vehicle (MCL 4 x 0.01 = 0.04, NG 4 x 0.001 = 0.004), equal to
  R-07's 4 ticks of the most active contract (K4-L-06). Compared in integer vendor ticks (S0.10).
- Eligible bars: those opening in [O+15, C) = [08:15, 13:30) of CT date d; no entry from 13:30 on.
- Entry: the first eligible bar whose close >= OR_high + 4 ticks buys, <= OR_low - 4 ticks sells;
  a market intent on that bar. The first qualifying bar uses the trade date's one entry, whatever
  the engine does with the intent (E.3-L-08).
- Exit: 75 minutes after the fill, counted as the MES module counts it (B-H1; E.3-L-07): the
  present bars seen while the position is non-zero, from the bar after the entry decision bar; on
  the 75th, a market intent closing the position (fills at the next open), resent while refused
  (E.3-L-22). Or the engine's forced flatten at F if earlier. There is NO exit at C-2: the
  template's C-2 exit is not part of CP2 (E.3-L-07). After an engine-forced exit (F, D9.7) the
  member sends nothing more that trade date.
- Early halts are not tested here (a port: the engine's F and entry skip govern, C line 85).
One traded leg, q_c contracts (MCL 4, NG 1).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date, time

from rules.xfa_rules import Refusal
from strategy.members.k4._port_common import (
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

MEMBER_ID = "K4-cp2-01"
RANGE_MINUTES = 15  # OR = [O, O+15)
BUFFER_TICKS = 4  # 4 vendor ticks of the vehicle (K4-L-06)
HOLD_BARS = 75  # present bars counted while the position is open (E.3-L-07)
F_REGULAR_CT = time(15, 8)  # F of a regular energy day (D line 395): the trading window's end


@dataclass
class Cp2Breakout:
    """K4-cp2-01 on one exposure; state resets when the bar's trade date changes."""

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


def make_mcl() -> Cp2Breakout:
    return Cp2Breakout("MCL")


def make_ng() -> Cp2Breakout:
    return Cp2Breakout("NG")


__all__ = ["BUFFER_TICKS", "MEMBER_ID", "Cp2Breakout", "make_mcl", "make_ng"]
