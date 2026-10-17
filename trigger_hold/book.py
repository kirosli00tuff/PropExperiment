"""Units -> the root's net position -> multiday.book orders -> multiday.book.simulate_book
(lead_spec sections 3 and 8; the frozen E.21 engine is reused, never edited).

- net(i, d) = clip(sum of u over the units active after the fill at MK(d), -1, +1), a unit
  being active from MK(d_e) to MK(d_x) (its P&L accrues on (d_e, d_x]). The book changes position
  only on a mark date where net changes value: 0 -> +-1 opens, +-1 -> 0 closes, +-1 -> -+1 flips.
- Size when net opens or flips on d: n = net x 0.40 / sigma(i, d) / (divisor x V(i, d)), the
  E.21 T1 per-root formula with signal = net and divisor 1 (``divisor_at`` exists for the T3
  reproduction test only); V = MK(d) price x the vehicle's tick value. Undefined or zero sigma, or
  a non-positive V: the opening is skipped (target 0), counted. n is held until net changes.
- Costs: ``E23VehicleCost`` returns, per side, base = the D8 cost (VehicleCost.fill_costs, the
  same Money) and stress = commission + 2 x the base case's one-side slippage cents (base -
  commission), the program's 2 x slippage construction (microbook S6, c1_replication); the
  slip150 key keeps base_rules' value and is not reported.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, fields, replace
from datetime import date

from base_rules.common import RunContext
from base_rules.costs import VehicleCost, vehicle_cost
from base_rules.store import ProductBars
from multiday import constants as MK
from multiday.book import BookResult, Order, RootData, process_root, simulate_book
from multiday.daily import fill_cost
from trigger_hold import constants as K
from trigger_hold.units import Unit


@dataclass
class E23VehicleCost(VehicleCost):
    """base_rules' VehicleCost with E.23's stress case (module docstring)."""

    def fill_costs(self, ts_ns: int, side: str, event: bool):  # noqa: ANN201
        got, uncal = super().fill_costs(ts_ns, side, event)
        base = got[MK.BASE]
        comm = self.costs.commission_side_cents
        stress = comm + K.STRESS_SLIPPAGE_MULTIPLE * (base - comm)
        return {MK.BASE: base, MK.STRESS: stress, MK.SLIP150: got[MK.SLIP150]}, uncal


def e23_vehicle_cost(root: str) -> E23VehicleCost:
    vc = vehicle_cost(root)
    return E23VehicleCost(**{f.name: getattr(vc, f.name) for f in fields(VehicleCost)
                             if f.name != "_cache"})


def prepare_root(ctx: RunContext, bars: ProductBars, root: str, *,
                 vc: VehicleCost | None = None, locks=None,  # noqa: ANN001
                 with_tom: bool = False) -> RootData:
    """multiday.book.process_root plus the fill cost of EVERY mark date (a unit book may trade
    on any of them); the RootData holds no bar."""
    vc = vc or e23_vehicle_cost(root)
    rd = process_root(ctx, bars, root, vc=vc, locks=locks, with_tom=with_tom)
    fills = dict(rd.fills)
    for mk in rd.path.marks:
        if mk.day not in fills:
            fills[mk.day] = fill_cost(bars, vc, ctx.releases, mk.point[0], mk.point[1], locks)
    return replace(rd, fills=fills)


def net_path(units: Sequence[Unit]) -> list[tuple[date, int, int]]:
    """(change date, net after the fill there, active units) at each date where net changes."""
    delta: dict[date, int] = {}
    count: dict[date, int] = {}
    for un in units:
        if un.d_x <= un.d_e:
            raise ValueError(f"unit exit {un.d_x} is not after its entry {un.d_e}")
        delta[un.d_e] = delta.get(un.d_e, 0) + un.u
        delta[un.d_x] = delta.get(un.d_x, 0) - un.u
        count[un.d_e] = count.get(un.d_e, 0) + 1
        count[un.d_x] = count.get(un.d_x, 0) - 1
    out = []
    total, active, net = 0, 0, 0
    for d in sorted(delta):
        total += delta[d]
        active += count[d]
        new = max(-1, min(1, total))
        if new != net:
            out.append((d, new, active))
            net = new
    return out


def _kind(old: int, new: int) -> str:
    if old == 0:
        return "open"
    if new == 0:
        return "close"
    return "flip"


def unit_orders(rd: RootData, units: Sequence[Unit], counters: Counter, *,
                divisor_at: Callable[[date], float] | None = None) -> list[Order]:
    """Section 3: one order per net change (module docstring)."""
    orders: list[Order] = []
    net = 0
    for d, new, active in net_path(units):
        if d not in rd.path.index:
            raise RuntimeError(f"{rd.root}: a unit date {d} is not a mark date (code invariant)")
        kind = _kind(net, new)
        counters[f"net changes: {kind}"] += 1
        info: dict = {"net": new, "active_units": active}
        target = 0.0
        if new != 0:
            target = _size(rd, d, new, info, counters, divisor_at)
        orders.append(Order(d, target, kind, info))
        net = new
    return orders


def _size(rd: RootData, d: date, net: int, info: dict, counters: Counter,
          divisor_at: Callable[[date], float] | None) -> float:
    sigma = rd.sigma.get(d)
    info["sigma"] = sigma
    if sigma is None or sigma <= 0:
        counters["opening skipped: sigma undefined (warm-up or zero)"] += 1
        return 0.0
    price = rd.path.marks[rd.path.index[d]].price
    v = float(price) * float(rd.tick_value_cents) / 100.0
    div = 1.0 if divisor_at is None else float(divisor_at(d))
    info.update({"V": v, "price_ticks": price, "divisor": div})
    if v <= 0:
        counters["opening skipped: non-positive notional (R-B3)"] += 1
        return 0.0
    if div <= 0:
        raise RuntimeError(f"{rd.root}: divisor {div} on {d} (code invariant)")
    counters["openings sized"] += 1
    return net * K.TARGET_VOL / sigma / (div * v)


def unit_book(rd: RootData, units: Sequence[Unit], *,
              divisor_at: Callable[[date], float] | None = None) -> BookResult:
    c: Counter = Counter()
    res = simulate_book(rd, unit_orders(rd, units, c, divisor_at=divisor_at))
    res.counters.update(c)
    return res


def daily_series(book: BookResult, days: Sequence[date], counters: Counter
                 ) -> dict[str, list[tuple[date, float]]]:
    """Per case, the book's daily net values on ``days`` (zero when flat); a value booked on a
    date outside ``days`` but inside their span adds that date, counted (E.21 assemble)."""
    grid = set(days)
    if days:
        lo, hi = min(days), max(days)
        booked = set(book.gross) | set().union(*(set(v) for v in book.cost.values()))
        extra = {d for d in booked if d not in grid and lo <= d <= hi}
        outside = {d for d in booked if d < lo or d > hi}
        if extra:
            counters["series dates added (value booked on a non-mark date)"] += len(extra)
        if outside:
            raise RuntimeError(f"values booked outside the window span: {sorted(outside)[:3]}")
        grid |= extra
    out = {}
    for c in K.CASES:
        net = book.net(c)
        out[c] = [(d, float(net.get(d, 0.0))) for d in sorted(grid)]
    return out


def book_summary(book: BookResult) -> dict:
    kinds: dict[str, dict] = {}
    diag: Counter = Counter()
    for f in book.fills:
        for kind in f["kind"].split("+"):
            row = kinds.setdefault(kind, {"fills": 0, "abs_contracts_per_capital": 0.0})
            row["fills"] += 1
            row["abs_contracts_per_capital"] += abs(f["trade"])
        diag["fills"] += 1
        diag["fills in an event window"] += int(f["event"])
        diag["fills in an uncalibrated bucket (R-B2)"] += int(f["uncalibrated"])
        diag["diag: fills the limit-lock test flags (not moved)"] += int(f["locked"])
        diag["diag: 2010-2019 fill bars with high == low"] += int(f["flat_bar"])
        diag["diag: forced fills inside a guard window"] += int(f["guard"])
    gross = float(sum(book.gross.values()))
    costs = {}
    for c in K.CASES:
        cost = float(sum(book.cost[c].values()))
        costs[c] = {"gross": gross, "costs": cost, "net": gross - cost,
                    "costs_share_of_gross": (cost / gross) if gross else None}
    return {"fills_by_kind": dict(sorted(kinds.items())), "fill_diagnostics": dict(diag),
            "gross_costs": costs}


def buy_hold_returns(rd: RootData, counters: Counter) -> dict[date, float]:
    """Section 4 addition (b), DESCRIPTIVE (alpha3 only, never a bar): the root's scale-free
    one-contract buy-and-hold daily return, the per-contract dollar move of each interval
    (multiday.daily's path: roll legs' price moves included, costs excluded) divided by the
    notional at the interval's opening mark, MK(previous mark) x the tick value, booked on each
    increment's own date (the book's daily attribution). A failed interval or a non-positive
    opening price contributes nothing (counted). The lead's fallback form; a long
    simulate_book hold was not used: one failed interval would exclude the whole hold (FR-1)."""
    out: dict[date, float] = {}
    tv = float(rd.tick_value_cents)
    for k, iv in enumerate(rd.path.intervals):
        if iv is None:
            continue
        if iv.fail:
            counters[f"buy-hold: interval skipped ({iv.fail})"] += 1
            continue
        p0 = float(rd.path.marks[k - 1].price)
        if p0 <= 0:
            counters["buy-hold: non-positive opening price"] += 1
            continue
        for day, cents in iv.increments:
            out[day] = out.get(day, 0.0) + float(cents) / (p0 * tv)
    return out


def regressor_on(values: Mapping[date, float], days: Sequence[date]) -> list[float]:
    """A per-root E.21 series on ``days`` (zero where nothing is booked: flat)."""
    return [float(values.get(d, 0.0)) for d in days]


__all__ = ["E23VehicleCost", "book_summary", "buy_hold_returns", "daily_series",
           "e23_vehicle_cost", "net_path", "prepare_root", "regressor_on", "unit_book",
           "unit_orders"]
