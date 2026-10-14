"""Per-root processing, the schedules of T1, T2 and T3, fractional holdings, fills, costs and the
daily series (lead_spec sections 3-5, 7, 8, 10).

``process_root`` does everything that needs a root's bars (marks, the per-contract path, returns,
sigma, rebalance dates, references, lookbacks, T3 unit eligibility, the per-contract cost of every
candidate fill) and returns a ``RootData`` that holds no bar, so roots are loaded one at a time.
The books are then assembled from the RootData alone: holdings n per unit of capital change only
at fill points (MK of a fill date); between fills the holding is constant; the value booked on a
date is n x the per-contract cents booked on it / 100 minus |delta n| x the per-contract cost of
each fill on it / 100 (roll legs pay |n| x their cost). A hold whose interval fails (a contract
change without a splice, a missing roll bar) is excluded: its opening order's target becomes 0,
counted (R-B3).
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field, replace
from datetime import date

from base_rules.common import RunContext
from base_rules.costs import VehicleCost
from base_rules.store import EXT2010, STEP2_ERA, ProductBars
from multiday import constants as K
from multiday.daily import (
    FillCost,
    RootPath,
    build_path,
    daily_returns,
    era_of,
    ewma_sigma_before,
    fill_cost,
    marks_of,
    with_boundary_splice,
)
from multiday.signals import (
    BarOracle,
    Month,
    Rebalance,
    TomUnit,
    first_eligible_after,
    lookback,
    rebalances,
    sign,
    t1_signal,
    t2_signal,
    tom_units,
)


@dataclass
class RootData:
    root: str
    vehicle: str
    tick_value_cents: object
    path: RootPath
    sigma: dict[date, float | None]
    rebalances: list[Rebalance]
    lookbacks: dict[tuple[Month, int], float | None]
    lookback_why: dict[tuple[Month, int], str]
    closeouts: dict[Month, date | None]
    era_last_mark: dict[str, date]
    tom: list[TomUnit]
    fills: dict[date, FillCost]
    counters: Counter = field(default_factory=Counter)

    @property
    def mark_days(self) -> list[date]:
        return [m.day for m in self.path.marks]


def process_root(ctx: RunContext, bars: ProductBars, root: str, *, vc: VehicleCost | None = None,
                 locks: Callable[[int, int], bool] | None = None, with_tom: bool = False
                 ) -> RootData:
    vc = vc or ctx.vc(root)
    counters: Counter = Counter()
    marks = marks_of(ctx, bars, root)
    path = build_path(ctx, bars, root, vc, locks, marks)
    counters.update(path.counters)
    rets = daily_returns(ctx, bars, root, marks, counters)
    counters["daily returns defined"] += len(rets)
    sigma = ewma_sigma_before(rets, [m.day for m in marks])
    oracle = BarOracle(ctx, bars, root, marks)
    rbs = rebalances(ctx, oracle, root)
    chain_bars, boundary_ts = with_boundary_splice(bars)
    looks: dict[tuple[Month, int], float | None] = {}
    why_l: dict[tuple[Month, int], str] = {}
    closeouts: dict[Month, date | None] = {}
    for rb in rbs:
        if rb.d_star is None:
            closeouts[rb.month] = first_eligible_after(ctx, oracle, root, rb.e)
            continue
        for k in K.LOOKBACKS:
            ref = rb.refs.get(k)
            if ref is None:
                looks[(rb.month, k)] = None
                why_l[(rb.month, k)] = rb.ref_why.get(k, "no reference")
                continue
            r, why = lookback(ctx, chain_bars, root, ref, rb.d_star, boundary_ts, counters)
            looks[(rb.month, k)] = r
            if r is None:
                why_l[(rb.month, k)] = f"lookback: {why}"
    del chain_bars
    era_last: dict[str, date] = {}
    for m in marks:
        era = era_of(m.day)
        if era is not None:
            era_last[era] = m.day
    tom = tom_sigma(tom_units(ctx, oracle, root), sigma) if with_tom else []
    wanted = {rb.d_star for rb in rbs if rb.d_star} | {d for d in closeouts.values() if d}
    wanted |= set(era_last.values())
    wanted |= {m.day for k in range(1, len(marks)) if era_of(marks[k - 1].day)  # FR-9: every
               != era_of(marks[k].day) for m in (marks[k - 1], marks[k])}  # backstop date
    wanted |= {d for u in tom if u.why is None for d in (u.entry, u.exit) if d}
    fills = {}
    for d in sorted(wanted):
        k = path.index.get(d)
        if k is None:
            continue
        pt = marks[k].point
        fills[d] = fill_cost(bars, vc, ctx.releases, pt[0], pt[1], locks)
    return RootData(root, vc.vehicle, vc.tick_value_cents, path, sigma, rbs, looks, why_l,
                    closeouts, era_last, tom, fills, counters)


def tom_sigma(units: list[TomUnit], sigma: Mapping[date, float | None]) -> list[TomUnit]:
    """Lead ruling Q2: a date-eligible T3 unit whose sigma at day -2 is undefined (warm-up) or
    zero is EXCLUDED and not counted in S_u (S_u counts roots with an ELIGIBLE unit; both roots
    enter at the same equity settlement, so no other root's future is used)."""
    out = []
    for u in units:
        if u.why is None:
            sg = sigma.get(u.entry) if u.entry is not None else None
            if sg is None:
                u = replace(u, why="sigma warm-up")
            elif sg <= 0:
                u = replace(u, why="sigma zero")
        out.append(u)
    return out


# ------------------------------------------------------------------ orders ----
@dataclass
class Order:
    day: date
    target: float
    kind: str
    info: dict = field(default_factory=dict)


def _notional_dollars(rd: RootData, day: date) -> float:
    price = rd.path.marks[rd.path.index[day]].price
    return float(price) * float(rd.tick_value_cents) / 100.0


def _merge(orders: list[Order]) -> list[Order]:
    """Orders sorted by date; on one date the last order's target wins (one fill)."""
    out: dict[date, Order] = {}
    for o in sorted(orders, key=lambda o: o.day):
        prev = out.get(o.day)
        if prev is not None:
            kinds = list(dict.fromkeys([*prev.kind.split("+"), *o.kind.split("+")]))
            o = Order(o.day, o.target, "+".join(kinds), {**prev.info, **o.info})
        out[o.day] = o
    return [out[d] for d in sorted(out)]


def t12_orders(rd: RootData, test: str, sm: Mapping[Month, int], counters: Counter
               ) -> list[Order]:
    """T1 (TSMOM-12) or T2 (trend blend) orders of one root (spec 3, 4, 7)."""
    orders: list[Order] = []
    for rb in rd.rebalances:
        if rb.d_star is None:
            counters["no eligible rebalance date"] += 1
            close = rd.closeouts.get(rb.month)
            if close is not None:
                counters["closed at the first eligible date after month end"] += 1
                orders.append(Order(close, 0.0, "close (no eligible rebalance date)",
                                    {"month": _m(rb.month)}))
            else:
                era = era_of(rb.e)
                last = rd.era_last_mark.get(era) if era else None
                if last is not None:
                    counters["forced close at the era's last mark"] += 1
                    day = max([last, *[o.day for o in orders]])
                    orders.append(Order(day, 0.0, "forced close (era end)",
                                        {"month": _m(rb.month)}))
            continue
        if rb.skipped:
            counters["rebalance moved earlier"] += 1
            for _d, why in rb.skipped:
                counters[f"rebalance moved: {why.split(' (')[0]}"] += 1
        info = {"month": _m(rb.month), "e": str(rb.e)}
        target, why = _t12_target(rd, test, rb, sm, info)
        if why:
            counters[why] += 1
        orders.append(Order(rb.d_star, target, "rebalance", info))
    return _merge(orders)


def _m(m: Month) -> str:
    return f"{m[0]}-{m[1]:02d}"


def _t12_target(rd: RootData, test: str, rb: Rebalance, sm: Mapping[Month, int], info: dict
                ) -> tuple[float, str | None]:
    assert rb.d_star is not None
    if rb.month in K.FLAT_MONTHS:
        return 0.0, f"flat month {_m(rb.month)} (store boundary or window end)"
    looks = {k: rd.lookbacks.get((rb.month, k)) for k in K.LOOKBACKS}
    if test == "T1":
        s = t1_signal(looks[K.T1_LOOKBACK])
        missing = [K.T1_LOOKBACK] if s is None else []
    else:
        s = t2_signal(looks[1], looks[3], looks[12])
        missing = [k for k in K.LOOKBACKS if looks[k] is None]
    info.update({"lookbacks": {str(k): v for k, v in looks.items()}, "signal": s})
    if s is None:
        k = missing[0]
        return 0.0, f"no signal ({rd.lookback_why.get((rb.month, k), 'lookback undefined')})"
    sigma = rd.sigma.get(rb.d_star)
    info["sigma"] = sigma
    if sigma is None or sigma <= 0:
        return 0.0, "sigma undefined (warm-up or zero)"
    s_m = int(sm.get(rb.month, 0))
    info["S_M"] = s_m
    if s_m <= 0:
        return 0.0, "divisor zero"
    v = _notional_dollars(rd, rb.d_star)
    info.update({"V": v, "price_ticks": rd.path.marks[rd.path.index[rb.d_star]].price,
                 "weight": s * K.TARGET_VOL / sigma})
    if v <= 0:
        return 0.0, "non-positive notional (R-B3)"
    if s == 0:
        return 0.0, "zero signal"
    return s * K.TARGET_VOL / sigma / (s_m * v), None


def t3_orders(rd: RootData, su: Mapping[Month, int], counters: Counter) -> list[Order]:
    """T3 orders of one root: long from MK(day -2) to MK(day +3), w = 0.40 / sigma(day -2),
    n = w / (S_u x V at the entry fill) (spec 5)."""
    orders: list[Order] = []
    for u in rd.tom:
        if u.why is not None:
            counters[f"T3 unit excluded: {u.why}"] += 1
            continue
        assert u.entry is not None and u.exit is not None
        sigma = rd.sigma.get(u.entry)
        if sigma is None or sigma <= 0:
            raise RuntimeError("an eligible T3 unit without a sigma (code invariant)")
        s_u = int(su.get(u.month, 0))
        if s_u <= 0:
            raise RuntimeError("an eligible T3 unit outside S_u (code invariant)")
        v = _notional_dollars(rd, u.entry)
        if v <= 0:
            counters["T3 unit excluded: non-positive notional (R-B3)"] += 1
            continue
        n = K.TARGET_VOL / sigma / (s_u * v)
        counters["T3 units traded"] += 1
        info = {"month": _m(u.month), "sigma": sigma, "S_u": s_u, "V": v,
                "price_ticks": rd.path.marks[rd.path.index[u.entry]].price}
        orders += [Order(u.entry, n, "entry", info), Order(u.exit, 0.0, "exit",
                                                            {"month": _m(u.month)})]
    return _merge(orders)


# ------------------------------------------------------------------ the book ----
@dataclass
class BookResult:
    gross: dict[date, float]
    cost: dict[str, dict[date, float]]
    fills: list[dict]
    holdings: list[dict]
    counters: Counter

    def net(self, case: str) -> dict[date, float]:
        days = set(self.gross) | set(self.cost[case])
        return {d: self.gross.get(d, 0.0) - self.cost[case].get(d, 0.0) for d in days}


BACKSTOP = "forced close (backstop)"


def simulate_book(rd: RootData, orders: Sequence[Order]) -> BookResult:
    """The root's book under ``orders``. A failed hold is excluded (its opening order's target
    becomes 0) and the book rerun. FR-1 (R-B3 backstop, never fatal after the marker): a position
    still held at an era end (an interval across the store boundary) or after the last mark is
    force-closed at the last mark of that era (an order of target 0 merged on that date, counted
    "forced close (backstop)") and the book rerun."""
    orders = _merge(list(orders))
    excluded: dict[date, str] = {}
    backstops = 0
    while True:
        res, fail = _run(rd, orders, excluded)
        if fail is None:
            for why in excluded.values():
                res.counters[f"hold excluded: {why}"] += 1
            res.counters[BACKSTOP] += backstops
            return res
        kind, day, why = fail
        if kind == "backstop":
            backstops += 1
            orders = _merge([*orders, Order(day, 0.0, BACKSTOP)])
            continue
        excluded[day] = why


def _side(trade: float) -> str:
    return "buy" if trade > 0 else "sell"


def _fill_row(day: date, kind: str, trade: float, fc: FillCost, side: str, held: float) -> dict:
    per = {c: fc.cost[side][c] for c in K.COST_CASES}
    return {"date": str(day), "kind": kind, "trade": trade, "held_after": held, "side": side,
            "price_ticks": fc.price, "ts": fc.ts, "cost_per_contract_cents":
            {c: str(v) if not isinstance(v, int) else v for c, v in per.items()},
            "cost": {c: abs(trade) * float(per[c]) / 100.0 for c in K.COST_CASES},
            "event": fc.event, "uncalibrated": fc.uncal[side], "locked": fc.locked[side],
            "flat_bar": fc.flat_bar, "guard": fc.guard}


def _run(rd: RootData, orders: list[Order], excluded: Mapping[date, str]
         ) -> tuple[BookResult, tuple[str, date, str] | None]:
    path = rd.path
    at: dict[int, int] = {}
    for j, o in enumerate(orders):
        k = path.index.get(o.day)
        if k is None:
            raise RuntimeError(f"{rd.root}: order on {o.day} is not a mark date (code invariant)")
        at[k] = j
    res = BookResult({}, {c: {} for c in K.COST_CASES}, [], [], Counter())
    n, last_j = 0.0, None

    def book_cost(day: date, row: dict) -> None:
        for c in K.COST_CASES:
            res.cost[c][day] = res.cost[c].get(day, 0.0) + row["cost"][c]
        res.fills.append(row)

    for k in range(len(path.marks)):
        iv = path.intervals[k]
        if n != 0.0 and iv is not None:
            if iv.fail == "store boundary":  # an era end: the backstop close (FR-1)
                return res, ("backstop", path.marks[k - 1].day, iv.fail)
            if iv.fail:
                assert last_j is not None
                return res, ("hold", orders[last_j].day, iv.fail)
            for day, cents in iv.increments:
                res.gross[day] = res.gross.get(day, 0.0) + n * float(cents) / 100.0
            for leg in iv.rolls:
                side = ("sell" if n > 0 else "buy") if leg.kind == "roll_out" else \
                    ("buy" if n > 0 else "sell")
                trade = -n if leg.kind == "roll_out" else n
                book_cost(leg.fill.day, _fill_row(leg.fill.day, leg.kind, trade, leg.fill, side,
                                                  0.0 if leg.kind == "roll_out" else n))
        j = at.get(k)
        if j is None:
            continue
        o = orders[j]
        target = 0.0 if o.day in excluded else o.target
        res.holdings.append({"date": str(o.day), "kind": o.kind, "target": target,
                             "excluded": excluded.get(o.day), "vehicle": rd.vehicle,
                             "mark_price_ticks": path.marks[k].price, **o.info})
        trade = target - n
        if trade != 0.0:
            fc = rd.fills[o.day]
            book_cost(o.day, _fill_row(o.day, o.kind, trade, fc, _side(trade), target))
        n, last_j = target, j
    if n != 0.0:  # held after the last mark: the backstop close at the last mark (FR-1)
        if not path.marks:
            raise RuntimeError(f"{rd.root}: a position with no mark at all (code invariant)")
        return res, ("backstop", path.marks[-1].day, "window end")
    return res, None


# ------------------------------------------------------------------ series ----
def series_dates(mark_days: Iterable[Iterable[date]], first: date | None,
                 last: date = K.WINDOW_LAST) -> list[date]:
    if first is None:
        return []
    days: set[date] = set()
    for ds in mark_days:
        days.update(d for d in ds if first <= d <= last)
    return sorted(days)


def assemble(books: Mapping[str, BookResult], dates: Sequence[date], counters: Counter
             ) -> tuple[dict[str, list[tuple[date, float]]], dict[str, dict[str, dict]]]:
    """The test's daily net series per case on ``dates`` (zero when flat; a booked value on a
    date outside them adds that date, counted) and the per-root daily base-case net values."""
    grid = set(dates)
    extra = set()
    for b in books.values():
        for d in set(b.gross) | set().union(*(set(v) for v in b.cost.values())):
            if d not in grid:
                extra.add(d)
    if extra:
        counters["series dates added (value booked on a non-series date)"] += len(extra)
    grid |= extra
    out: dict[str, list[tuple[date, float]]] = {}
    for c in K.COST_CASES:
        tot = dict.fromkeys(grid, 0.0)
        for b in books.values():
            for d, v in b.net(c).items():
                tot[d] += v
        out[c] = sorted(tot.items())
    per_root = {r: {"net_base": dict(sorted(b.net(K.BASE).items())), "gross": b.gross,
                    "cost": b.cost} for r, b in books.items()}
    return out, per_root


__all__ = ["BookResult", "Order", "RootData", "assemble", "process_root", "series_dates",
           "simulate_book", "t12_orders", "t3_orders", "tom_sigma", "EXT2010", "STEP2_ERA", "sign"]
