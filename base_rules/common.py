"""What the five runners share: the run context, the date exclusions of lead_spec section 2, the
risk-unit conversion and the output record."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import date, time
from fractions import Fraction
from typing import Any

from base_rules import constants as K
from base_rules.auctions import Auction
from base_rules.calendars import GroupCalendars
from base_rules.costs import ReleaseRules, VehicleCost, vehicle_cost
from base_rules.inputs import SettlementTable
from base_rules.limits import LockRule
from base_rules.scaling import TRADED, unit_sigmas
from base_rules.sim import NS_MIN, Point, SimResult
from base_rules.store import ProductBars
from data.session import ct_ns
from data.stage_e_bars import StageEBarRefusal


class InvariantError(RuntimeError):
    """A CODE invariant failed (never a data condition: those are excluded and counted, R-B3)."""


@dataclass
class RunContext:
    calendars: Mapping[str, GroupCalendars]  # group -> calendars
    settlement: SettlementTable
    starts: Mapping[str, date]  # product -> first window trade date (full or fallback)
    releases: ReleaseRules
    load_bars: Callable[[str], ProductBars]
    auctions: tuple[Auction, ...] = ()
    last: date = K.WINDOW_LAST
    _vc: dict = field(default_factory=dict, repr=False)

    def cal(self, product: str) -> GroupCalendars:
        return self.calendars[K.GROUP_OF[product]]

    def vc(self, product: str) -> VehicleCost:
        if product not in self._vc:
            self._vc[product] = vehicle_cost(product)
        return self._vc[product]

    def in_window(self, product: str, day: date) -> bool:
        return self.starts[product] <= day <= self.last

    def window_dates(self, product: str) -> list[date]:
        return [d for d in self.cal(product).trade_dates() if self.in_window(product, d)]

    def first_of_week(self, product: str, day: date) -> bool:
        """``day`` is the first trade date of its ISO week on the product's group calendar."""
        prev = self.cal(product).previous(day)
        return prev is None or prev.isocalendar()[:2] != day.isocalendar()[:2]

    def open_minute(self, product: str, day: date) -> int | None:
        """O_p (lead note 3: the period's first-business-day-of-week minute on the first trade
        date of the ISO week, LE and HE 2014-10-27..2016-02-28)."""
        return self.settlement.open_minute(product, day, self.first_of_week(product, day))

    def listed(self, product: str, day: date) -> bool:
        """S_p and O_p exist on ``day`` (lead note 1: else no unit of ANY test, "not listed")."""
        return self.settlement.listed(product, day) and self.open_minute(product, day) is not None

    # -- R-B1: the settlement minute at a scheduled closure ----------------------------------
    def in_session(self, product: str, day: date, minute: int) -> bool:
        """The bar opening at CT ``minute`` lies inside one of ``day``'s open intervals."""
        ts = ct_ns(day, time(minute // 60, minute % 60))
        return any(lo <= ts and ts + NS_MIN <= hi for lo, hi in self.cal(product).intervals(day))

    def closure_at(self, product: str, day: date, minute: int) -> bool:
        """A scheduled closure of ``day``'s session begins at CT ``minute`` (an open interval
        ends there: the session's close or a daily halt, e.g. equity 15:15 until 2021-06-27)."""
        ts = ct_ns(day, time(minute // 60, minute % 60))
        iv = self.cal(product).intervals(day)
        return not any(lo <= ts < hi for lo, hi in iv) and any(hi == ts for _lo, hi in iv)

    def reopen_ns(self, product: str, day: date, minute: int) -> int | None:
        """The first instant of ``day``'s session after the closure beginning at ``minute``."""
        ts = ct_ns(day, time(minute // 60, minute % 60))
        later = [lo for lo, _hi in self.cal(product).intervals(day) if lo > ts]
        return min(later) if later else None


def settle_point(ctx: RunContext, bars: ProductBars, product: str, day: date) -> Point | None:
    """An exit or a mark "at the settlement minute" (R-B1 a, d): the open of bar(S_p), or, when a
    scheduled closure begins at S_p, the close of bar(S_p - 1). None: the bar is absent."""
    s = ctx.settlement.settle_minute(product, day)
    if s is None:
        return None
    if ctx.closure_at(product, day, s):
        i = bars.bar(day, s - 1)
        return None if i is None else (i, True)
    i = bars.bar(day, s)
    return None if i is None else (i, False)


def entry_point(ctx: RunContext, bars: ProductBars, product: str, day: date, minute: int
                ) -> tuple[Point | None, str | None]:
    """An entry at the settlement or decision minute (R-B1 b): the open of bar(minute), or, when a
    scheduled closure begins there, the open of the first bar of the same trade date's session
    after the closure ("no entry bar" when the trade date has none)."""
    if ctx.closure_at(product, day, minute):
        ns = ctx.reopen_ns(product, day, minute)
        i = None if ns is None else bars.bar_ns(ns, day)
        return (None, "no entry bar") if i is None else ((i, False), None)
    i = bars.bar(day, minute)
    return (None, "missing bar") if i is None else ((i, False), None)


def lock_rule(ctx: RunContext, bars: ProductBars) -> LockRule:
    """F-07: the engine's limit-lock test for this product's fills (2019-on calendar)."""
    return LockRule(bars, ctx.cal(bars.root).frozen)


FLAT_DIAG = "diag: 2010-2019 fill bars with high == low"


def flat_fill_bars(bars: ProductBars, sim: SimResult) -> int:
    """F-07 diagnostic, 2010-2019 only (no limit table): fills on a bar whose high equals its
    low (a possibly locked market), never an exclusion."""
    if bars.high_t is None or bars.low_t is None:
        return 0
    return sum(1 for f in sim.fills if f.trade_date < K.FROZEN_CAL_FIRST and f.bar_index >= 0
               and int(bars.high_t[f.bar_index]) == int(bars.low_t[f.bar_index]))


def load_or_exclude(ctx: RunContext, product: str, counters: Counter, notes: dict
                    ) -> ProductBars | None:
    """R-B3: a store the loader refuses after reading its rows (a data condition: a booking, a
    holdout row, a duplicate or off-grid bar, a date in both stores) excludes the product, counted;
    input problems (paths, sha256s, metadata) were refused before the run-once marker."""
    try:
        return ctx.load_bars(product)
    except StageEBarRefusal as exc:
        counters["store refused"] += 1
        notes.setdefault("store_refused", {})[product] = f"{type(exc).__name__}: {exc}"
        return None


def action_exclusion(ctx: RunContext, bars: ProductBars | None, product: str, day: date
                     ) -> str | None:
    """Why ``day`` cannot be an action date of ``product`` (entry, exit, H1/H4 trade date)."""
    cal = ctx.cal(product)
    if not ctx.in_window(product, day):
        return "outside window"
    if not cal.is_trade_date(day):
        return "not a trade date"
    if cal.unsourced(day):
        return "unsourced calendar date"
    if bars is not None and day in bars.blackout:
        return "roll blackout"
    if cal.early_halt(day) is not None:
        return "early halt"
    return None


def reference_exclusion(ctx: RunContext, product: str, ref: date | None) -> str | None:
    """Section 2's reference date: in the window, a trade date, not an early-halt, halt or
    unsourced date (a roll-blackout date is allowed: a reference, not a trade)."""
    if ref is None:
        return "no reference (no prior trade date)"
    cal = ctx.cal(product)
    if not ctx.in_window(product, ref):
        return "no reference (outside window)"
    if cal.unsourced(ref):
        return "no reference (unsourced)"
    if cal.early_halt(ref) is not None:
        return "no reference (early halt)"
    return None


def top(reason: str) -> str:
    """The top-level counter name of a reason ("no reference (x)" -> "no reference")."""
    return reason.split(" (")[0]


@dataclass
class Unit:
    key: str  # product, leg or tenor
    unit_date: date
    direction: int
    sim: SimResult
    info: dict = field(default_factory=dict)
    status: str = ""
    sigma: float | None = None

    @property
    def g(self) -> float:
        return float(self.sim.gross_cents) / 100.0

    def net_ru(self, case: str) -> float:
        assert self.sigma is not None
        return float(Fraction(self.sim.net(case)) / 100) / self.sigma


def scale_units(units: list[Unit], counters: Counter) -> None:
    """Section 3 per key: statuses and sigmas, counted."""
    by_key: dict[str, list[Unit]] = {}
    for u in units:
        by_key.setdefault(u.key, []).append(u)
    for us in by_key.values():
        us.sort(key=lambda u: (u.sim.entry_date, u.unit_date))
        got = unit_sigmas([u.sim.entry_date for u in us], [u.sim.exit_date for u in us],
                          [u.g for u in us])
        for u, (status, sigma) in zip(us, got, strict=True):
            u.status, u.sigma = status, sigma
            counters[status] += 1


@dataclass
class RunOutput:
    test: str
    units: dict[str, list[tuple[date, float]]]  # case -> per-unit series (unit date, value)
    daily: dict[str, dict[date, float]]  # case -> H5 component series
    grid: set[date]
    counters: Counter
    per_product: dict[str, Counter]
    rows: list[dict]
    notes: dict[str, Any] = field(default_factory=dict)


def money(x: Any) -> str | int:
    return str(x) if isinstance(x, Fraction) and x.denominator != 1 else int(x)


def unit_row(u: Unit) -> dict:
    row = {"key": u.key, "date": str(u.unit_date), "direction": u.direction,
           "status": u.status, "sigma": u.sigma, "gross_cents": money(u.sim.gross_cents),
           "costs_cents": {c: money(v) for c, v in u.sim.costs.items()},
           "entry_date": str(u.sim.entry_date), "exit_date": str(u.sim.exit_date),
           "fills": [[f.ts_ns, f.kind, f.trade, f.price_ticks, f.event, f.at_close,
                      f.uncalibrated] for f in u.sim.fills],
           **u.info}
    if u.status == TRADED:
        row["net_ru"] = {c: u.net_ru(c) for c in K.COST_CASES}
    return row


__all__ = ["InvariantError", "RunContext", "RunOutput", "Unit", "action_exclusion",
           "FLAT_DIAG", "entry_point", "flat_fill_bars", "load_or_exclude", "lock_rule", "money",
           "reference_exclusion", "scale_units", "settle_point", "top", "unit_row"]
