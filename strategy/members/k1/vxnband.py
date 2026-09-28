"""K1-vxnband-01: fade a breach of the VXN/16 band around the prior close, only at VXN extremes
(Stage E.7; reports/stage_e7_member_specs.md section 4; catalog reports/stage_e0_catalog_K1.md
lines 403-500; readings K1-L-01..K1-L-05 and K1-L-10).

Rule (every clock time CT; the bars of trade date d on CT date d, S0.4):
- Dates: d in EQUITY_FULL_SESSIONS (no early halt, engine F 15:08; S0.8, K1-L-10). Other trade
  dates are not traded; their bars still build daily closes. Roll blackouts are the engine's.
- C_prev (K1-L-03): the close of the 14:59 bar of the most recent COMPLETE trade date before d.
  Complete (Family H, as CP3): the 08:30 and 14:59 bars exist, no bar of CT date d carries
  early_halt_ct, and every bar in [08:30, 15:00) carries one instrument_id; a date is finalised
  when a bar of a later trade date arrives. No complete earlier date yet: no trade.
- Instrument guard: C_prev's instrument_id equals that of d's 08:30 bar, else no trade on d; d's
  08:30 bar missing: no trade on d.
- V (K1-L-01, K1-L-02): VXN_CLOSE of the calendar date of the EQUITY_TRADE_DATES entry
  immediately before d (never d's own close), read on d's 08:30 bar (at its close, 08:31 CT) and
  never before; no row: no trade on d.
- Regime: V < 20 (strict) or V >= 30 (non-strict), exact Decimal compares; else no trade on d.
- Band (K1-L-04): sell iff 1600 x (close_t - C_prev) > C_prev x V, buy iff 1600 x (close_t -
  C_prev) < -(C_prev x V), strict; prices in integer vendor ticks, V as its exact integer ratio.
- Scan: the bars of CT date d opening in [08:30, 14:29), in order. A minute of [08:30, t] with no
  bar, or a scan bar whose instrument_id differs from the 08:30 bar's, seen before the first
  breach, ends the day's search. The first breach on either side uses the day's one entry, even
  if the engine refuses it: market intent q_c on that bar (fills at the next open).
- Exit (K1-L-05): market intent on the first present bar of CT date d opening at or after the
  entry-intent bar + 30 minutes, while the position is non-zero and nothing is pending; resent
  while refused (S0.7). The latest entry-intent bar is 14:28, so the latest exit intent bar is
  14:58 (fill 14:59). The engine's flatten at F is the backstop; after an engine closure the
  member sends nothing more that date.
One traded leg, q_c contracts (MNQ 1). No release instant is read.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date, time
from decimal import Decimal
from typing import Any

from rules.xfa_rules import Refusal
from strategy.members.k1._event_common import (
    BUY,
    PREVIOUS_TRADE_DATE,
    ROOT,
    SELL,
    ClockRun,
    LegFacts,
    clock_minute,
    close_items,
    ct_open,
    is_flat,
    is_full_session,
    label,
    leg_facts,
    to_ticks,
)
from strategy.members.k1._vxn import VXN_CLOSE
from strategy.stage_e.interface import (
    LegIntent,
    LegSpec,
    MemberAccountView,
    MinuteView,
    TradingInterval,
    leg_market_intent,
)

MEMBER_ID = "K1-vxnband-01"
BAND_DIVISOR = 1600  # 100 x 16: VXN in percentage points, /16 for one daily sd (P-K1-005-a)
VXN_LOW_CUT = Decimal(20)  # trade when V < 20 (strict) ...
VXN_HIGH_CUT = Decimal(30)  # ... or V >= 30 (non-strict), P-K1-005-b
SCAN_END_CT = time(14, 29)  # entry-intent bars open in [08:30, 14:29)
HOLD_MINUTES = 30  # the exit intent goes on the bar at entry-intent bar + 30 min
CLOSE_BEFORE_C_MIN = 1  # C_prev = the close of the bar at C-1 = 14:59

# K1-L-02: calendar date -> the Cboe VXN close, exact
_VXN: dict[date, Decimal] = {date.fromisoformat(d): Decimal(v) for d, v in VXN_CLOSE}


def vxn_for(day: date) -> Decimal | None:
    """V of trade date ``day``: the VXN close of the calendar date of the EC-CAL trade date
    immediately before ``day`` (None: no earlier trade date, or no VXN row for it)."""
    prior = PREVIOUS_TRADE_DATE.get(day)
    return None if prior is None else _VXN.get(prior)


def in_regime(v: Decimal) -> bool:
    return v < VXN_LOW_CUT or v >= VXN_HIGH_CUT


def breach_side(close_ticks: int, prev_ticks: int, v: Decimal) -> str | None:
    """The band test in integers: with V = n / m, sell iff 1600 m (close - C_prev) > C_prev n,
    buy iff 1600 m (close - C_prev) < -(C_prev n); a close on the band is no breach."""
    n, m = v.as_integer_ratio()
    move = BAND_DIVISOR * m * (close_ticks - prev_ticks)
    width = prev_ticks * n
    if move > width:
        return SELL
    if move < -width:
        return BUY
    return None


@dataclass(frozen=True)
class PriorClose:
    """A COMPLETE trade date's 14:59 close in vendor ticks, with its one instrument_id."""

    trade_date: date
    close: int
    instrument_id: int


@dataclass(frozen=True)
class DaySetup:
    """Day d's band inputs, fixed on its 08:30 bar."""

    prev: int  # C_prev, ticks
    v: Decimal
    instrument_id: int  # the 08:30 bar's (the scan's reference)


@dataclass
class VxnBand:
    """K1-vxnband-01 on MNQ. Day state resets when the bar's trade date changes; the last complete
    daily close carries over."""

    root: str = field(default=ROOT, init=False)
    name: str = field(init=False)
    legs: tuple[LegSpec, ...] = field(init=False)
    trading_windows: dict = field(init=False)
    _leg: LegFacts = field(init=False, repr=False)
    _o: int = field(init=False, repr=False)  # clock minutes of O, C, C-1 and the scan's end
    _c: int = field(init=False, repr=False)
    _close_at: int = field(init=False, repr=False)
    _scan_end: int = field(init=False, repr=False)
    _prior: PriorClose | None = field(default=None, init=False, repr=False)
    _day: date | None = field(default=None, init=False, repr=False)
    # day d as a future C_prev (Family H)
    _halt: bool = field(default=False, init=False, repr=False)
    _has_open_bar: bool = field(default=False, init=False, repr=False)
    _close: int | None = field(default=None, init=False, repr=False)
    _ids: frozenset[int] = field(default=frozenset(), init=False, repr=False)
    # day d's entry search and exit
    _searching: bool = field(default=False, init=False, repr=False)
    _run: ClockRun | None = field(default=None, init=False, repr=False)
    _setup: DaySetup | None = field(default=None, init=False, repr=False)
    _exit_at: int | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self._leg = leg_facts()
        self.name = label(MEMBER_ID)
        self.legs = self._leg.legs
        self._o, self._c = clock_minute(self._leg.o), clock_minute(self._leg.c)
        self._close_at = self._c - CLOSE_BEFORE_C_MIN
        self._scan_end = clock_minute(SCAN_END_CT)
        # S0.12: the C_prev bar (14:59), the scan [08:30, 14:29) and the 14:59 exit fill bar
        self.trading_windows = {self.root: (TradingInterval(self._leg.o, self._leg.c),)}

    # -- per trade date ----------------------------------------------------------------
    def _complete(self) -> PriorClose | None:
        if (self._day is None or not self._has_open_bar or self._close is None or self._halt
                or len(self._ids) != 1):
            return None
        (only_id,) = self._ids
        return PriorClose(self._day, self._close, only_id)

    def _roll(self, day: date) -> None:
        """Finalise the ending trade date (a complete one becomes C_prev), then start ``day``."""
        finished = self._complete()
        if finished is not None:
            self._prior = finished
        self._day, self._halt, self._has_open_bar = day, False, False
        self._close, self._ids = None, frozenset()
        self._searching = is_full_session(day)
        self._run, self._setup, self._exit_at = ClockRun(self._o), None, None

    def _accumulate(self, bar: Any, minute: int) -> None:
        """Day d's Family H facts, from its bars of CT date d."""
        if bar.early_halt_ct is not None:
            self._halt = True
        if not self._o <= minute < self._c:
            return
        self._ids = self._ids | {bar.instrument_id}
        if minute == self._o:
            self._has_open_bar = True
        if minute == self._close_at:
            self._close = to_ticks(bar.close, self._leg.tick)

    def _day_setup(self, bar: Any) -> DaySetup | None:
        """On d's 08:30 bar: the instrument guard, V and the regime (V is read here only)."""
        prior = self._prior
        if prior is None or prior.instrument_id != bar.instrument_id:
            return None
        v = vxn_for(self._day)
        if v is None or not in_regime(v):
            return None
        return DaySetup(prior.close, v, bar.instrument_id)

    def _scan(self, bar: Any, minute: int) -> str | None:
        """The breach side on a scan bar, or None; the first breach, a gap or an instrument
        change ends the day's search."""
        if not self._searching or not self._o <= minute < self._scan_end:
            return None
        if self._run is None or not self._run.see(minute):
            self._searching = False  # a minute of [08:30, t] without a bar (C4)
            return None
        if minute == self._o:
            self._setup = self._day_setup(bar)
        setup = self._setup
        if setup is None or bar.instrument_id != setup.instrument_id:
            self._searching = False  # no trade on d, or an instrument change (C4)
            return None
        side = breach_side(to_ticks(bar.close, self._leg.tick), setup.prev, setup.v)
        if side is not None:
            self._searching = False  # the first breach uses the day's one entry
        return side

    # -- the member contract -----------------------------------------------------------
    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> Sequence[LegIntent | Refusal]:
        bar = view.bar(self.root)
        if bar is None:  # no bar: no decision at this minute (never forward fill)
            return ()
        if bar.trade_date != self._day:
            self._roll(bar.trade_date)
        opened = ct_open(bar)
        if opened.date() != self._day:
            return ()  # the previous CT evening: nothing of day d is read there
        minute = clock_minute(opened.time())
        self._accumulate(bar, minute)
        side = self._scan(bar, minute)
        if account.position(self.root):
            if self._exit_at is None or minute < self._exit_at:
                return ()
            return close_items(view, account, self.root)
        if side is None or not is_flat(account, self.root):
            return ()
        self._exit_at = minute + HOLD_MINUTES
        return (leg_market_intent(view, self.root, side, self._leg.q),)


def make_mnq() -> VxnBand:
    return VxnBand()


__all__ = ["MEMBER_ID", "DaySetup", "PriorClose", "VxnBand", "breach_side", "in_regime",
           "make_mnq", "vxn_for"]
