"""K6-cp2-01: core port CP2, opening-range breakout, on ZC, ZW, ZS, ZM, ZL, HE and LE (Stage E.8;
reports/stage_e8_member_specs.md section 2; catalog reports/stage_e0_catalog_K6.md lines 288-334;
D6 line 365 and the "4 ticks of P" paragraph, lines 368-372).

Copied in structure from strategy/members/k1/cp2.py (E.7), never imported from it.
Rule, instantiated with the grains row (O 08:30, C 13:15, F 13:18) and the livestock row (O 08:30,
C 13:00, F 13:03); the clock comes from the frozen tables. Only bars of CT date d are read
(K7-L-01): the grain evening bars of trade date d (CT date d-1, from 19:00) never enter the range
or trigger.
- Opening range: OR_high = max high, OR_low = min low of the present bars opening in
  [O, O+15) = [08:30, 08:45) of CT date d. No range bar: no trade (E.3-L-08). No minimum bar
  count and no instrument guard.
- Buffer: 4 vendor ticks of the traded vehicle (K4-L-06): ZC, ZW, ZS 4 x 0.25 = 1.00 cents/bu;
  ZM 4 x 0.10 = 0.40 USD/short ton; ZL 4 x 0.01 = 0.04 cents/lb; HE, LE 4 x 0.025 = 0.100
  cents/lb. Compared in integer vendor ticks (S0.10).
- Eligible bars: those opening in [O+15, C) of CT date d: grains [08:45, 13:15), livestock
  [08:45, 13:00); no entry from C on.
- Entry: the first eligible bar whose close >= OR_high + 4 ticks buys, <= OR_low - 4 ticks sells
  (non-strict); a market intent on that bar. The first qualifying bar uses the trade date's one
  entry, whatever the engine does with the intent (E.3-L-08).
- Exit: 75 minutes after the fill, counted as the MES module counts it (E.3-L-07): the present
  bars seen while the position is non-zero, from the bar after the entry decision bar; on the
  75th, a market intent closing the position (fills at the next open), resent while refused
  (E.3-L-22). Or the engine's forced flatten at F if earlier. There is NO exit at C-2. After an
  engine-forced exit (F, D9.7) the member sends nothing more that trade date.
- Early halts are not tested here (a port: the engine's F governs, C line 89; K6-L-18). No
  release instant is read (the engine's D9.5a guard and D9.3 skip, C lines 319-331).
One traded leg, q_c contracts (1 on every root).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date, time

from rules.xfa_rules import Refusal
from strategy.members.k6._port_common import (
    GRAINS,
    LIVESTOCK,
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

MEMBER_ID = "K6-cp2-01"
RANGE_MINUTES = 15  # OR = [O, O+15)
BUFFER_TICKS = 4  # 4 vendor ticks of the vehicle (K4-L-06)
HOLD_BARS = 75  # present bars counted while the position is open (E.3-L-07)
# F of a regular day per group (D lines 400-401; rules/sessions.py): the trading window's end
F_REGULAR_CT = {GRAINS: time(13, 18), LIVESTOCK: time(13, 3)}


@dataclass
class Cp2Breakout:
    """K6-cp2-01 on one root; state resets when the bar's trade date changes."""

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
        self.trading_windows = {self.root: (
            TradingInterval(self._leg.o, F_REGULAR_CT[self._leg.group]),)}

    def _reset(self, day: date) -> None:
        self._day, self._hi, self._lo, self._triggered, self._held = day, None, None, False, 0

    def _hold_exit(self, view: MinuteView, account: MemberAccountView
                   ) -> Sequence[LegIntent | Refusal]:
        """The MES count: one per present bar with the position open; exit from the 75th on
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
            return ()  # the grain evening of trade date d (CT date d-1)
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


def make_zc() -> Cp2Breakout:
    return Cp2Breakout("ZC")


def make_zw() -> Cp2Breakout:
    return Cp2Breakout("ZW")


def make_zs() -> Cp2Breakout:
    return Cp2Breakout("ZS")


def make_zm() -> Cp2Breakout:
    return Cp2Breakout("ZM")


def make_zl() -> Cp2Breakout:
    return Cp2Breakout("ZL")


def make_he() -> Cp2Breakout:
    return Cp2Breakout("HE")


def make_le() -> Cp2Breakout:
    return Cp2Breakout("LE")


__all__ = ["BUFFER_TICKS", "F_REGULAR_CT", "MEMBER_ID", "Cp2Breakout", "make_he", "make_le",
           "make_zc", "make_zl", "make_zm", "make_zs", "make_zw"]
