"""The position simulator of the base-rule tests (lead_spec sections 0-2; one vehicle contract).

A unit is a list of target positions at fill POINTS plus the daily mark points. A point is a bar
and a side of it: the bar's OPEN (every ordinary fill: a decision at a bar's close fills at a
later bar's open, the engine's clock) or, ruling R-B1, the bar's CLOSE (an exit or a mark "at the
settlement minute" when a scheduled closure begins at S_p: the close of bar(S_p - 1), the frozen
engine's own fill for a position meeting a closure). A close point happens at the bar's open + 60 s;
its cost bucket, event window and fill guard are looked up at the bar's open, as the engine's
close_cost does. The simulator walks the events in time order (fills before marks at the same
instant, rolls after both):
- a position held across a splice instant s of its leg's store (lo < s <= hi) is rolled: closed at
  the open of the last usable bar before s (old contract) and reopened at the open of the first
  usable bar at or after s (new contract), two fills that pay the cost rule;
- a mark applies only while a position is open; a missing mark (None) carries the P&L to the next;
- every price used must be the position's contract (raw symbol), else the unit is excluded
  ("contract change"); a fill inside a D9.5a guard excludes it ("fill guard"); a roll bar absent
  ("missing roll bar"); a fill the engine's limit-lock test refuses (F-07, base_rules.limits)
  excludes it ("limit locked"). A fill in an uncalibrated D8 bucket pays the product's largest
  per-side slippage (R-B2) and is flagged.
Money: exact cents (ticks x the vehicle's tick value in cents, int or Fraction), every fill paying
|trade| x the per-side cost of its case. The daily attribution books each P&L increment and each
cost to the trade date of the bar it happens on, so a unit's daily values sum to its net P&L.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import date
from fractions import Fraction

from base_rules import constants as K
from base_rules.costs import ReleaseRules, VehicleCost
from base_rules.store import ProductBars

Money = int | Fraction
Point = tuple[int, bool]  # (bar index, at the bar's close)
NS_MIN = 60_000_000_000
FILL, MARK, ROLL = 0, 1, 2  # order of events at the same instant


@dataclass(frozen=True)
class SimFill:
    ts_ns: int  # the bar's open (the cost lookup instant)
    trade_date: date
    price_ticks: int
    trade: int  # signed contracts (buy > 0)
    kind: str  # entry | exit | flip | roll_out | roll_in
    event: bool
    costs: dict
    at_close: bool = False
    uncalibrated: bool = False
    fill_ns: int = 0  # the fill instant: the bar's open, or its open + 60 s for a close fill
    bar_index: int = -1


@dataclass
class SimResult:
    ok: bool
    reason: str | None = None
    fills: list[SimFill] = field(default_factory=list)
    gross_cents: Money = 0
    costs: dict = field(default_factory=lambda: {c: 0 for c in K.COST_CASES})
    daily: dict = field(default_factory=lambda: {c: {} for c in K.COST_CASES})
    entry_date: date | None = None
    exit_date: date | None = None

    def net(self, case: str) -> Money:
        return self.gross_cents - self.costs[case]

    @property
    def uncalibrated(self) -> bool:
        return any(f.uncalibrated for f in self.fills)


def point(x: Point | int) -> Point:
    return (int(x[0]), bool(x[1])) if isinstance(x, tuple) else (int(x), False)


def price_at(bars: ProductBars, pt: Point) -> int:
    return int(bars.close_t[pt[0]] if pt[1] else bars.open_t[pt[0]])


def _time(bars: ProductBars, pt: Point) -> int:
    return int(bars.ts[pt[0]]) + (NS_MIN if pt[1] else 0)


def _add(book: dict, day: date, value: Money) -> None:
    book[day] = book.get(day, 0) + value


def _fill(bars: ProductBars, vc: VehicleCost, rel: ReleaseRules, pt: Point, trade: int,
          kind: str, locks: Callable[[int, int], bool] | None) -> SimFill | str:
    i = pt[0]
    ts = int(bars.ts[i])
    if rel.guard(bars.root, ts):
        return "fill guard"
    if locks is not None and locks(i, trade):
        return "limit locked"
    event = rel.event(bars.root, ts)
    per_side, uncal = vc.fill_costs(ts, "buy" if trade > 0 else "sell", event)
    costs = {c: abs(trade) * v for c, v in per_side.items()}
    return SimFill(ts, date.fromordinal(int(bars.td[i])), price_at(bars, pt), trade, kind,
                   event, costs, pt[1], uncal, _time(bars, pt), i)


def simulate(bars: ProductBars, vc: VehicleCost, rel: ReleaseRules,
             changes: Sequence[tuple[Point | int, int]],
             marks: Sequence[Point | int | None] = (),
             locks: Callable[[int, int], bool] | None = None) -> SimResult:
    """``changes``: (fill point, target position) in time order, the last target 0; ``marks``:
    mark points (None = missing). Returns the unit's fills, gross, costs and daily values."""
    out = SimResult(ok=True)
    if not changes or changes[-1][1] != 0:
        raise ValueError("a unit must end flat")
    pts = [(point(p), target) for p, target in changes]
    events: list[tuple[int, int, int, object]] = []
    for k, (pt, _target) in enumerate(pts):
        events.append((_time(bars, pt), FILL, k, pt))
    for m in marks:
        if m is not None:
            pt = point(m)
            events.append((_time(bars, pt), MARK, -1, pt))
    first_ts, last_ts = _time(bars, pts[0][0]), _time(bars, pts[-1][0])
    for s in bars.splices_between(first_ts, last_ts):
        i_out, i_in = bars.last_before(s.ts_ns), bars.first_at_or_after(s.ts_ns)
        events.append((s.ts_ns, ROLL, -2, (-1 if i_out is None else i_out,
                                           -1 if i_in is None else i_in)))
    events.sort(key=lambda e: (e[0], e[1]))
    pos, contract, ref = 0, None, 0
    tv = vc.tick_value_cents

    def gain(price: int, day: date) -> None:
        inc = pos * (price - ref) * tv
        out.gross_cents += inc
        for c in K.COST_CASES:
            _add(out.daily[c], day, inc)

    for _t, kind_code, k, payload in events:
        if kind_code == ROLL:
            if pos == 0:
                continue
            i_out, i_in = payload  # type: ignore[misc]
            if i_out < 0 or i_in < 0:
                return SimResult(ok=False, reason="missing roll bar")
            if bars.contract(i_out) != contract or bars.contract(i_in) == contract:
                return SimResult(ok=False, reason="contract change")
            for i, trade, kind in ((i_out, -pos, "roll_out"), (i_in, pos, "roll_in")):
                f = _fill(bars, vc, rel, (i, False), trade, kind, locks)
                if isinstance(f, str):
                    return SimResult(ok=False, reason=f)
                if kind == "roll_out":
                    gain(f.price_ticks, f.trade_date)
                contract, ref = bars.contract(i), f.price_ticks
                _book_costs(out, f)
            continue
        pt: Point = payload  # type: ignore[assignment]
        if kind_code == MARK:
            if pos == 0:
                continue
            if bars.contract(pt[0]) != contract:
                return SimResult(ok=False, reason="contract change")
            gain(price_at(bars, pt), date.fromordinal(int(bars.td[pt[0]])))
            ref = price_at(bars, pt)
            continue
        target = pts[k][1]
        trade = target - pos
        if trade == 0:
            continue
        if pos != 0 and bars.contract(pt[0]) != contract:
            return SimResult(ok=False, reason="contract change")
        kind = "entry" if pos == 0 else ("exit" if target == 0 else "flip")
        f = _fill(bars, vc, rel, pt, trade, kind, locks)
        if isinstance(f, str):
            return SimResult(ok=False, reason=f)
        if pos != 0:
            gain(f.price_ticks, f.trade_date)
        pos, contract, ref = target, bars.contract(pt[0]), f.price_ticks
        if out.entry_date is None:
            out.entry_date = f.trade_date
        if target == 0:
            out.exit_date = f.trade_date
        _book_costs(out, f)
    return out


def _book_costs(out: SimResult, f: SimFill) -> None:
    out.fills.append(f)
    for c in K.COST_CASES:
        out.costs[c] += f.costs[c]
        _add(out.daily[c], f.trade_date, -f.costs[c])


__all__ = ["NS_MIN", "Point", "SimFill", "SimResult", "point", "price_at", "simulate"]
