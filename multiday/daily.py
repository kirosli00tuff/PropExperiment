"""Marks, the per-contract path, daily returns and the EWMA sigma (lead_spec sections 1, 2, 7, 8).

- MK(i, d) = base_rules.common.settle_point (the open of bar S, or under R-B1 the close of bar
  S - 1); PS(i, d) = the close of bar S - 1. Mark dates: window trade dates on which the product
  is listed and MK exists. A missing MK carries the P&L to the next mark.
- The per-contract path: between consecutive marks, the same-contract dollar move of ONE vehicle
  contract, rolled at each recorded splice as base_rules.sim does (closed at the open of the last
  usable bar before the splice, reopened at the open of the first usable bar at or after it), each
  increment booked on its bar's trade date (sim's daily attribution). A roll leg inside a D9.5a
  guard window moves to the nearest usable bar of its contract outside every guard window (the old
  leg earlier, the new leg later; spec 7). Every roll leg carries its per-contract cost per side and
  case (VehicleCost.fill_costs). An interval across the store boundary, a contract change without a
  splice or a missing roll bar is a failed interval (a hold across it is excluded, counted).
- r(i, d): the chained return from MK(d_prev) to MK(d), d_prev the trade date immediately before d
  on the group calendar, split at each splice as base_rules.h2.chained_return does; undefined when a
  mark is missing, the eras differ or the contract changes without a splice.
- sigma(i, d): sqrt(261 x EWMA variance, centre of mass 60, adjust=True, bias=True) of the defined
  returns dated strictly before d; defined from 60 such returns on (spec 2).
"""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field, replace
from datetime import date

import numpy as np

from base_rules.common import FLAT_DIAG, RunContext, settle_point
from base_rules.costs import ReleaseRules, VehicleCost
from base_rules.sim import Money, Point, price_at
from base_rules.store import EXT2010, STEP2_ERA, ProductBars, Splice
from multiday import constants as K

SIDES = ("buy", "sell")


def era_of(day: date) -> str | None:
    """The store era a trade date belongs to (None: 2019-05-01..05-05, in neither store)."""
    if day <= K.HIST_LAST:
        return EXT2010
    if day >= K.STEP2_FIRST:
        return STEP2_ERA
    return None


@dataclass(frozen=True)
class FillCost:
    """Per-contract cost of a fill at one bar: side -> case -> cents, and the diagnostics."""

    ts: int
    day: date
    price: int
    cost: dict  # side -> {case: Money}
    event: bool
    uncal: dict  # side -> bool
    guard: bool
    locked: dict  # side -> bool (F-07 diagnostic only, spec 7)
    flat_bar: bool  # 2010-2019 fill bar with high == low (diagnostic)


@dataclass(frozen=True)
class Mark:
    day: date
    point: Point
    price: int  # ticks (open, or close under R-B1)
    ts: int  # the bar's open (cost and guard lookup instant)
    contract: str


@dataclass(frozen=True)
class RollLeg:
    kind: str  # roll_out | roll_in
    fill: FillCost
    moved: bool  # moved out of a guard window


@dataclass(frozen=True)
class Interval:
    """(previous mark, this mark]: per-contract increments (date, cents) and roll legs."""

    increments: tuple[tuple[date, Money], ...]
    rolls: tuple[RollLeg, ...]
    fail: str | None = None


@dataclass
class RootPath:
    root: str
    tick_value_cents: Money
    marks: list[Mark]
    intervals: list[Interval | None]  # intervals[k] ends at marks[k]; intervals[0] is None
    index: dict[date, int] = field(default_factory=dict)
    counters: Counter = field(default_factory=Counter)

    def __post_init__(self) -> None:
        self.index = {m.day: k for k, m in enumerate(self.marks)}

    def per_contract_daily(self) -> dict[date, Money | None]:
        """The per-contract dollar-cent P&L of one vehicle contract held throughout, roll legs'
        price moves included (costs excluded), per booking date; None on a failed interval's end
        date (F8 input)."""
        out: dict[date, Money | None] = {}
        for k, iv in enumerate(self.intervals):
            if iv is None:
                continue
            if iv.fail:
                out[self.marks[k].day] = None
                continue
            for day, cents in iv.increments:
                if out.get(day, 0) is not None:
                    out[day] = out.get(day, 0) + cents
        return out


# ------------------------------------------------------------------ marks ----
def ps_index(ctx: RunContext, bars: ProductBars, root: str, day: date) -> int | None:
    """PS(i, d): the bar S - 1 (its close is the signal price); None when absent."""
    s = ctx.settlement.settle_minute(root, day)
    return None if s is None else bars.bar(day, s - 1)


def marks_of(ctx: RunContext, bars: ProductBars, root: str) -> list[Mark]:
    out = []
    for d in ctx.window_dates(root):
        if not ctx.listed(root, d):
            continue
        pt = settle_point(ctx, bars, root, d)
        if pt is None:
            continue
        i = pt[0]
        out.append(Mark(d, pt, price_at(bars, pt), int(bars.ts[i]), bars.contract(i)))
    return out


# ------------------------------------------------------------------ fill costs ----
def fill_cost(bars: ProductBars, vc: VehicleCost, rel: ReleaseRules, i: int, pt_close: bool,
              locks: Callable[[int, int], bool] | None) -> FillCost:
    ts = int(bars.ts[i])
    event = rel.event(bars.root, ts)
    cost, uncal = {}, {}
    for side in SIDES:
        per_side, unc = vc.fill_costs(ts, side, event)
        cost[side], uncal[side] = dict(per_side), bool(unc)
    locked = {s: bool(locks(i, 1 if s == "buy" else -1)) if locks is not None else False
              for s in SIDES}
    day = date.fromordinal(int(bars.td[i]))
    flat = bool(day < K.STEP2_FIRST and bars.high_t is not None and bars.low_t is not None
                and int(bars.high_t[i]) == int(bars.low_t[i]))
    price = int(bars.close_t[i] if pt_close else bars.open_t[i])
    return FillCost(ts, day, price, cost, bool(event), uncal, bool(rel.guard(bars.root, ts)),
                    locked, flat)


# ------------------------------------------------------------------ the per-contract path ----
def _guard_move(bars: ProductBars, rel: ReleaseRules, i: int, step: int, lo: int, hi: int
                ) -> tuple[int | None, bool]:
    """The nearest usable bar of bar i's contract outside every guard window, moving by
    ``step`` (-1 earlier, +1 later), staying strictly inside (lo, hi) bar indices."""
    contract, moved = bars.contract(i), False
    while rel.guard(bars.root, int(bars.ts[i])):
        moved = True
        i += step
        while lo < i < hi and not bars.usable[i]:
            i += step
        if not lo < i < hi or bars.contract(i) != contract:
            return None, moved
    return i, moved


def build_path(ctx: RunContext, bars: ProductBars, root: str, vc: VehicleCost,
               locks: Callable[[int, int], bool] | None = None,
               marks: Sequence[Mark] | None = None) -> RootPath:
    """The per-contract path of ``root`` over its mark dates (module docstring)."""
    marks = list(marks_of(ctx, bars, root) if marks is None else marks)
    rel, tv = ctx.releases, vc.tick_value_cents
    path = RootPath(root, tv, marks, [None])
    for k in range(1, len(marks)):
        path.intervals.append(_interval(bars, vc, rel, marks[k - 1], marks[k], tv, locks,
                                        path.counters))
    return path


def _interval(bars: ProductBars, vc: VehicleCost, rel: ReleaseRules, a: Mark, b: Mark,
              tv: Money, locks, counters: Counter) -> Interval:
    if era_of(a.day) != era_of(b.day):
        return Interval((), (), "store boundary")
    ia, ib = a.point[0], b.point[0]
    t_a = int(bars.ts[ia]) + (60_000_000_000 if a.point[1] else 0)
    t_b = int(bars.ts[ib]) + (60_000_000_000 if b.point[1] else 0)
    contract, ref = a.contract, a.price
    incs: list[tuple[date, Money]] = []
    legs: list[RollLeg] = []
    for s in bars.splices_between(t_a, t_b):
        i_out, i_in = bars.last_before(s.ts_ns), bars.first_at_or_after(s.ts_ns)
        if i_out is None or i_in is None or i_out < ia or i_in > ib:
            return Interval((), (), "missing roll bar")
        if bars.contract(i_out) != contract or bars.contract(i_in) == contract:
            return Interval((), (), "contract change")
        i_out, m_out = _guard_move(bars, rel, i_out, -1, ia, ib + 1)
        i_in2, m_in = (None, False) if i_out is None else _guard_move(bars, rel, i_in, 1,
                                                                      i_out, ib + 1)
        if i_out is None or i_in2 is None:
            return Interval((), (), "missing roll bar (fill guard)")
        counters["roll legs moved by the fill guard"] += int(m_out) + int(m_in)
        f_out = fill_cost(bars, vc, rel, i_out, False, locks)
        incs.append((f_out.day, (f_out.price - ref) * tv))
        f_in = fill_cost(bars, vc, rel, i_in2, False, locks)
        legs += [RollLeg("roll_out", f_out, m_out), RollLeg("roll_in", f_in, m_in)]
        contract, ref = bars.contract(i_in2), f_in.price
    if b.contract != contract:
        return Interval((), (), "contract change")
    incs.append((b.day, (b.price - ref) * tv))
    return Interval(tuple(incs), tuple(legs), None)


# ------------------------------------------------------------------ returns ----
def chain_prices(bars: ProductBars, a: Point, b: Point) -> list[int]:
    """Every price a chained return from ``a`` to ``b`` divides by or multiplies with (the start,
    each splice's old-segment close and new-segment open, the end), for the R-B3 guard."""
    out = [price_at(bars, a), price_at(bars, b)]
    for s in bars.splices_between(int(bars.ts[a[0]]), int(bars.ts[b[0]])):
        i_out, i_in = bars.last_before(s.ts_ns), bars.first_at_or_after(s.ts_ns)
        if i_out is not None:
            out.append(int(bars.close_t[i_out]))
        if i_in is not None:
            out.append(int(bars.open_t[i_in]))
    return out


def chained_point_return(bars: ProductBars, a: Point, b: Point) -> tuple[float | None, str]:
    """The same-contract chained return from point ``a``'s price to point ``b``'s price, split at
    each splice exactly as base_rules.h2.chained_return (which is the close-to-close case). A
    non-positive price on the chain makes it undefined (R-B3: counted, never raised)."""
    if min(chain_prices(bars, a, b)) <= 0:
        return None, "non-positive price"
    i_start, i_end = a[0], b[0]
    lo, hi = int(bars.ts[i_start]), int(bars.ts[i_end])
    start_price, start_i, ratio = price_at(bars, a), i_start, 1.0
    for s in bars.splices_between(lo, hi):
        i_out, i_in = bars.last_before(s.ts_ns), bars.first_at_or_after(s.ts_ns)
        if i_out is None or i_in is None or i_out < start_i:
            return None, "missing bar"
        if bars.contract(i_out) != bars.contract(start_i):
            return None, "contract change"
        ratio *= int(bars.close_t[i_out]) / start_price
        start_price, start_i = int(bars.open_t[i_in]), i_in
    if bars.contract(i_end) != bars.contract(start_i):
        return None, "contract change"
    return ratio * price_at(bars, b) / start_price - 1.0, ""


def daily_returns(ctx: RunContext, bars: ProductBars, root: str, marks: Sequence[Mark],
                  counters: Counter) -> list[tuple[date, float]]:
    """(d, r(i, d)) for every mark date d with a defined return (module docstring)."""
    cal = ctx.cal(root)
    by_day = {m.day: m for m in marks}
    out = []
    for m in marks:
        prev = cal.previous(m.day)
        pm = by_day.get(prev) if prev is not None else None
        if pm is None:
            counters["return undefined: previous mark missing"] += 1
            continue
        if era_of(prev) != era_of(m.day):
            counters["return undefined: store boundary"] += 1
            continue
        r, why = chained_point_return(bars, pm.point, m.point)
        if r is None:
            counters[f"return undefined: {why}"] += 1
            continue
        out.append((m.day, r))
    return out


# ------------------------------------------------------------------ EWMA sigma ----
def ewma_sigma_before(returns: Sequence[tuple[date, float]], days: Iterable[date], *,
                      com: float = K.EWMA_COM, ann: float = K.ANNUALIZATION,
                      warmup: int = K.SIGMA_WARMUP_RETURNS) -> dict[date, float | None]:
    """sigma(i, d) for each d in ``days``: the annualized EWMA volatility of the returns dated
    strictly before d (weights delta^k on the k-th most recent, delta = com / (com + 1),
    normalized; weighted mean removed; spec 2). None before ``warmup`` returns."""
    delta = com / (com + 1.0)
    rs = sorted(returns)
    out: dict[date, float | None] = {}
    s0 = s1 = s2 = 0.0
    n, j = 0, 0
    for d in sorted(set(days)):
        while j < len(rs) and rs[j][0] < d:
            r = float(rs[j][1])
            s0, s1, s2 = delta * s0 + 1.0, delta * s1 + r, delta * s2 + r * r
            n, j = n + 1, j + 1
        if n < warmup:
            out[d] = None
            continue
        mean = s1 / s0
        var = max(s2 / s0 - mean * mean, 0.0)
        out[d] = math.sqrt(ann * var)
    return out


def ewma_sigma_direct(returns: Sequence[float], *, com: float = K.EWMA_COM,
                      ann: float = K.ANNUALIZATION) -> float:
    """The direct summation of spec 2 over ``returns`` (oldest first): the test's reference."""
    delta = com / (com + 1.0)
    r = np.asarray(returns, dtype=float)[::-1]  # k = 0 the most recent
    w = (1.0 - delta) * delta ** np.arange(len(r))
    mean = float((w * r).sum() / w.sum())
    return math.sqrt(ann * float((w * (r - mean) ** 2).sum() / w.sum()))


# ------------------------------------------------------------------ store boundary ----
def with_boundary_splice(bars: ProductBars) -> tuple[ProductBars, int | None]:
    """Lookbacks (spec 1, [LEAD]): when the last ext2010 bar and the first step 2 bar carry
    different contracts and no splice is recorded between them, a splice is added there (the
    chain is split as at a splice); same contract: the chain runs through. Returns the bars to
    chain on and the added splice instant (None when none was added)."""
    td, use = bars.td, bars.usable
    hist = np.flatnonzero((td <= K.HIST_LAST.toordinal()) & use)
    step = np.flatnonzero((td >= K.STEP2_FIRST.toordinal()) & use)
    if not len(hist) or not len(step):
        return bars, None
    i_last, i_first = int(hist[-1]), int(step[0])
    t_last, t_first = int(bars.ts[i_last]), int(bars.ts[i_first])
    if bars.contract(i_last) == bars.contract(i_first):
        return bars, None
    if any(t_last < s.ts_ns <= t_first for s in bars.splices):
        return bars, None
    added = Splice(t_first, date.fromordinal(int(td[i_first])))
    return replace(bars, splices=tuple(sorted((*bars.splices, added),
                                              key=lambda s: s.ts_ns))), t_first


__all__ = ["FLAT_DIAG", "FillCost", "Interval", "Mark", "RollLeg", "RootPath", "SIDES",
           "build_path", "chain_prices", "chained_point_return", "daily_returns", "era_of",
           "ewma_sigma_before", "ewma_sigma_direct", "fill_cost", "marks_of", "ps_index",
           "with_boundary_splice"]
