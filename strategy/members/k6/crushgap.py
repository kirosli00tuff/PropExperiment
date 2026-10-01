"""K6-crushgap-01: soybean crush gap, traded on ZS only, with ZM and ZL as signal legs (Stage E.8;
reports/stage_e8_member_specs.md section 4; catalog reports/stage_e0_catalog_K6.md lines 380-494;
readings K6-L-03, K6-L-04, K6-L-05, K6-L-10).

Rule (grains clock from the frozen tables: O 08:30, C 13:15, F 13:18 on all three legs):
- GPM = 0.022 x P_ZM + 11 x P_ZL - P_ZS in USD per bushel (C lines 425-434), with P_ZM in USD per
  short ton, P_ZL in USD per pound and P_ZS in USD per bushel, each the vendor price divided by
  the product's vendor_price_factor (ZM 1, ZL 100, ZS 100). Computed exactly in integer units of
  0.0001 USD/bu (K6-L-03): a leg's units per vendor tick are weight x vendor_tick /
  vendor_price_factor / 0.0001, derived here from rules.products and the weights (ZM 22, ZL 11,
  ZS -25), and must be integers; the 0.02 USD/bu filter is 200 units.
- d-1 = the EC-CAL grain trade date before d (previous_trade_date(GRAIN_TRADE_DATES, d); K6-L-04),
  not the most recent complete date. GPM_close(d-1) from the closes of the three legs' bars at
  C-1 = 13:14 of CT date d-1; GPM_open(d) from the opens of the three legs' bars at O = 08:30 of
  CT date d. G(d) = GPM_open(d) - GPM_close(d-1).
- Guard, per leg (K6-L-05): its 13:14 bar of d-1 and its 08:30 bar of d exist and carry the same
  instrument_id; otherwise no trade on d. An early-halt d-1 (2025-11-28, 2025-12-24) has no 13:14
  bars, so the next trade date is not traded. Contract months may differ across legs.
- d must be in GRAIN_FULL_SESSIONS (S0.8, K6-L-10); otherwise no trade.
- Entry: G <= -0.02 USD/bu sells ZS; G >= +0.02 buys ZS (non-strict); otherwise no trade. Market
  intent on the 08:30 ZS bar of CT date d (that exact bar, S0.6), filling at the 08:31 open.
  Never an intent on ZM or ZL.
- Exit: market intent on the first ZS bar of CT date d at or after C-2 = 13:13 (fills nominally
  at the 13:14 open), resent while refused (S0.7, E.3-L-22). The engine's forced flatten at F and
  its D9.7 exit are the backstops; after either, nothing more that trade date.
- The engine refuses an open when any of the three legs lacks the bar at that minute (D11.5) and
  on a roll-blackout date of any leg (D4); the member does not repeat either test.
One traded leg, q_c contracts of ZS (1).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict, dataclass, field
from datetime import date, time
from decimal import Decimal
from typing import Any

from rules.products import product
from rules.xfa_rules import Refusal
from strategy.members.k6._calendar import (
    GRAIN_FULL_SESSIONS,
    GRAIN_TRADE_DATES,
    previous_trade_date,
)
from strategy.members.k6._port_common import (
    LegFacts,
    ct_open,
    exit_if_due,
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

MEMBER_ID = "K6-crushgap-01"
TRADED = "ZS"  # the one traded leg (C line 382, S0.1)
SIGNAL_LEGS: tuple[str, ...] = ("ZM", "ZL")  # read only
LEGS: tuple[str, ...] = (TRADED, *SIGNAL_LEGS)
# GPM = 0.022 x P_ZM + 11 x P_ZL - P_ZS, USD per bushel (C lines 425-426)
GPM_WEIGHTS = {"ZM": Decimal("0.022"), "ZL": Decimal("11"), "ZS": Decimal("-1")}
GPM_UNIT_USD_PER_BU = Decimal("0.0001")  # the exact integer unit of K6-L-03
FILTER_USD_PER_BU = Decimal("0.02")  # G <= -0.02 sells, G >= +0.02 buys (non-strict)
CLOSE_BEFORE_C_MIN = 1  # the bars at C-1 = 13:14 of d-1
EXIT_BEFORE_C_MIN = 2  # the first ZS bar at or after C-2 = 13:13


def _exact_units(value: Decimal, what: str) -> int:
    units = value / GPM_UNIT_USD_PER_BU
    if units != units.to_integral_value():
        raise ValueError(f"{what} is not an integer number of {GPM_UNIT_USD_PER_BU} USD/bu")
    return int(units)


def gpm_units_per_tick(root: str) -> int:
    """K6-L-03: one vendor tick of ``root``'s price, weighted, in 0.0001 USD/bu (ZM 22, ZL 11,
    ZS -25): weight x vendor_tick / vendor_price_factor / 0.0001."""
    p = product(root)
    usd = GPM_WEIGHTS[root] * p.vendor_tick / Decimal(p.vendor_price_factor)
    return _exact_units(usd, f"{root}'s weighted tick")


FILTER_UNITS = _exact_units(FILTER_USD_PER_BU, "the filter")  # 200


def _open_ticks(bar: Any, tick: Decimal) -> int:
    """An 08:30 bar's open in vendor ticks."""
    # bar.open via asdict: the freeze's static check bans the name `open` (E.3 ruling R-T2-1)
    return to_ticks(asdict(bar)["open"], tick)


@dataclass
class CrushGap:
    """K6-crushgap-01: ZS traded, ZM and ZL read. The entry flag resets when the ZS bar's trade
    date changes; each leg's last 13:14 bar carries over."""

    root: str = TRADED
    name: str = field(init=False)
    legs: tuple[LegSpec, ...] = field(init=False)
    trading_windows: dict = field(init=False)
    _facts: dict = field(init=False, repr=False)  # root -> LegFacts
    _units: dict = field(init=False, repr=False)  # root -> GPM units per vendor tick
    _close_at: dict = field(init=False, repr=False)  # root -> C-1 clock (13:14)
    _exit_at: time = field(init=False, repr=False)
    _day: date | None = field(default=None, init=False, repr=False)
    _entered: bool = field(default=False, init=False, repr=False)
    # root -> (CT date = trade date, close in ticks, instrument_id) of its latest 13:14 bar
    _closes: dict = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.root != TRADED:
            raise ValueError(f"{MEMBER_ID} trades {TRADED} only, not {self.root!r}")
        self._facts = {r: leg_facts(r) for r in LEGS}
        self._units = {r: gpm_units_per_tick(r) for r in LEGS}
        self._close_at = {r: shift(f.c, -CLOSE_BEFORE_C_MIN) for r, f in self._facts.items()}
        zs: LegFacts = self._facts[TRADED]
        self._exit_at = shift(zs.c, -EXIT_BEFORE_C_MIN)
        self.name = label(MEMBER_ID, TRADED)
        self.legs = (LegSpec(TRADED, True), *(LegSpec(r, False) for r in SIGNAL_LEGS))
        # S0.12: ZS from the 08:30 entry bar to the 13:14 exit fill bar (also its 13:14 bar of
        # d-1, on d-1's own date); ZM and ZL: the 08:30 bar of d and the 13:14 bar
        windows = {TRADED: (TradingInterval(zs.o, zs.c),)}
        for r in SIGNAL_LEGS:
            f = self._facts[r]
            windows[r] = (TradingInterval(f.o, shift(f.o, 1)),
                          TradingInterval(self._close_at[r], f.c))
        self.trading_windows = windows

    def _record_closes(self, view: MinuteView) -> None:
        """Each leg's bar at C-1 = 13:14 of its own trade date (CT date = trade date)."""
        for r in LEGS:
            bar = view.bar(r)
            if bar is None:
                continue
            opened = ct_open(bar)
            if opened.date() == bar.trade_date and opened.time() == self._close_at[r]:
                close = to_ticks(bar.close, self._facts[r].tick)
                self._closes = {**self._closes, r: (bar.trade_date, close, bar.instrument_id)}

    def _side(self, view: MinuteView, day: date) -> str | None:
        """The decision on the 08:30 ZS bar of d; None: no trade on d."""
        if day not in GRAIN_FULL_SESSIONS:
            return None  # S0.8, K6-L-10
        prev = previous_trade_date(GRAIN_TRADE_DATES, day)
        if prev is None:
            return None  # K6-L-04: no grain trade date before d
        g_units = 0
        for r in LEGS:
            bar = view.bar(r)  # the leg's 08:30 bar of CT date d (the ZS bar's minute)
            if bar is None:
                return None  # K6-L-05: a missing 08:30 bar on any leg
            last = self._closes.get(r)
            if last is None or last[0] != prev:
                return None  # K6-L-05: the leg's 13:14 bar of d-1 is missing
            _, close, close_id = last
            if close_id != bar.instrument_id:
                return None  # K6-L-05: the leg's two bars carry different instrument_ids
            g_units += self._units[r] * (_open_ticks(bar, self._facts[r].tick) - close)
        if g_units >= FILTER_UNITS:
            return "buy"
        if g_units <= -FILTER_UNITS:
            return "sell"
        return None

    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> Sequence[LegIntent | Refusal]:
        self._record_closes(view)
        bar = view.bar(TRADED)
        if bar is None:  # no ZS bar: no decision at this minute (never forward fill)
            return ()
        if bar.trade_date != self._day:
            self._day, self._entered = bar.trade_date, False
        day = bar.trade_date
        opened = ct_open(bar)
        if account.position(TRADED):
            return exit_if_due(view, account, TRADED, opened, day, self._exit_at)
        zs: LegFacts = self._facts[TRADED]
        if opened.date() != day or opened.time() != zs.o:
            return ()
        if self._entered or not is_flat(account, TRADED):
            return ()
        self._entered = True  # the one entry decision of the trade date
        side = self._side(view, day)
        if side is None:
            return ()
        return (leg_market_intent(view, TRADED, side, zs.q),)


def make_zs() -> CrushGap:
    return CrushGap(TRADED)


__all__ = ["FILTER_UNITS", "LEGS", "MEMBER_ID", "SIGNAL_LEGS", "TRADED", "CrushGap",
           "gpm_units_per_tick", "make_zs"]
