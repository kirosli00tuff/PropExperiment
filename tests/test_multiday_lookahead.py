"""No look-ahead: changing every price after a decision instant, or planting a future bar, moves no
position, sigma, signal or divisor decided at or before it (T1, T2, T3)."""

from __future__ import annotations

from collections import Counter
from datetime import date

import numpy as np
import pytest

from multiday.book import process_root, t3_orders, t12_orders
from multiday.signals import divisor_su, divisor_table
from tests._base_rules_fixtures import make_bars, ns
from tests.test_multiday_world import all_cals, ctx_for, utc_midnight, walk_prices, window

QUARTER_ROLLS = [date(y, m, 14) for y in range(2012, 2022) for m in (3, 6, 9, 12)]


@pytest.fixture(scope="module")
def cals():  # noqa: ANN201
    return all_cals()


def _rows(root: str, days, seed: int, s: int) -> tuple[list[tuple], list[date]]:  # noqa: ANN001
    px = walk_prices(days, drift=0.0005, vol=0.01, seed=seed)
    rolls = [r for r in QUARTER_ROLLS if days[0] < r <= days[-1] and r in set(days)]

    def sym(d: date) -> str:
        return f"C{sum(1 for r in rolls if d >= r)}"

    rows = []
    for d in days:
        p = px[d]
        rows += [(d, s - 1, p, p + 3, sym(d)), (d, s, p + 4, p + 5, sym(d))]
    return rows, rolls


def _perturb(rows: list[tuple], cutoff_ns: int, extra: list[tuple]) -> list[tuple]:
    rng = np.random.default_rng(99)
    out = []
    for r in rows:
        if ns(r[0], r[1]) > cutoff_ns:
            f = 1.0 + 0.5 * rng.random()
            r = (r[0], r[1], int(r[2] * f), int(r[3] * f), r[4])
        out.append(r)
    return out + extra


def _build(cals, roots, days, rows_of, rolls_of):  # noqa: ANN001, ANN202
    bars = {r: make_bars(r, rows_of[r], [(utc_midnight(x), x) for x in rolls_of[r]])
            for r in roots}
    ctx = ctx_for(cals, bars, starts={r: days[r][0] for r in roots})
    return ctx, bars


@pytest.mark.parametrize("test", ["T1", "T2"])
def test_t1_t2_positions_sigma_signal_and_divisor_ignore_the_future(cals, test: str) -> None:
    roots = ("NQ", "ZN")
    s_min = {"NQ": 15 * 60, "ZN": 14 * 60}
    days = {r: window(cals[g], date(2012, 1, 3), date(2016, 12, 30))
            for r, g in (("NQ", "equity"), ("ZN", "rates"))}
    rows, rolls = {}, {}
    for k, r in enumerate(roots):
        rows[r], rolls[r] = _rows(r, days[r], 10 + k, s_min[r])
    ctx, bars = _build(cals, roots, days, rows, rolls)
    sm = divisor_table(ctx, roots)
    base = {r: process_root(ctx, bars[r], r) for r in roots}
    month = (2015, 6)
    rb = next(x for x in base["NQ"].rebalances if x.month == month)
    k = base["NQ"].path.index[rb.d_star]
    cutoff = int(bars["NQ"].ts[base["NQ"].path.marks[k].point[0]])  # the NQ fill bar's open
    planted = {r: [(rb.d_star, s_min[r] + 1, 10**7, 10**7, "C9")] for r in roots}
    rows2 = {r: _perturb(rows[r], cutoff, planted[r]) for r in roots}
    ctx2, bars2 = _build(cals, roots, days, rows2, rolls)
    assert divisor_table(ctx2, roots) == sm
    after = {r: process_root(ctx2, bars2[r], r) for r in roots}
    for r in roots:
        o1 = [o for o in t12_orders(base[r], test, sm, Counter()) if o.day <= rb.d_star]
        o2 = [o for o in t12_orders(after[r], test, sm, Counter()) if o.day <= rb.d_star]
        assert [(o.day, o.target, o.kind) for o in o1] == [(o.day, o.target, o.kind)
                                                          for o in o2]
        assert any(o.target != 0 for o in o1)
        for d, v in base[r].sigma.items():
            if d <= rb.d_star:
                assert after[r].sigma[d] == v
        for (m, kk), v in base[r].lookbacks.items():
            if m <= month:
                assert after[r].lookbacks[(m, kk)] == v
    # the later months do move (the perturbation is real)
    later = [o.target for o in t12_orders(after["NQ"], test, sm, Counter()) if o.day > rb.d_star]
    assert later != [o.target for o in t12_orders(base["NQ"], test, sm, Counter())
                     if o.day > rb.d_star]


def test_the_fill_bars_own_open_moves_only_the_notional(cals) -> None:
    days = window(cals["equity"], date(2012, 1, 3), date(2015, 12, 31))
    rows, rolls = _rows("NQ", days, 3, 15 * 60)
    ctx, bars = _build(cals, ("NQ",), {"NQ": days}, {"NQ": rows}, {"NQ": rolls})
    rd = process_root(ctx, bars["NQ"], "NQ")
    rb = next(x for x in rd.rebalances if x.month == (2015, 6))
    rows2 = [(r[0], r[1], r[2] * 2, r[3], r[4]) if (r[0], r[1]) == (rb.d_star, 15 * 60) else r
             for r in rows]
    ctx2, bars2 = _build(cals, ("NQ",), {"NQ": days}, {"NQ": rows2}, {"NQ": rolls})
    rd2 = process_root(ctx2, bars2["NQ"], "NQ")
    assert rd2.sigma[rb.d_star] == rd.sigma[rb.d_star]
    for kk in (1, 3, 12):
        assert rd2.lookbacks[((2015, 6), kk)] == rd.lookbacks[((2015, 6), kk)]


def test_t3_entry_ignores_the_future(cals) -> None:
    roots = ("NQ", "RTY")
    days = {r: window(cals["equity"], date(2019, 5, 6), date(2021, 6, 30)) for r in roots}
    rows, rolls = {}, {}
    for k, r in enumerate(roots):
        rows[r], rolls[r] = _rows(r, days[r], 20 + k, 15 * 60)
    ctx, bars = _build(cals, roots, days, rows, rolls)
    base = {r: process_root(ctx, bars[r], r, with_tom=True) for r in roots}
    su = divisor_su({r: base[r].tom for r in roots})
    entry = next(u.entry for u in base["NQ"].tom if u.month == (2020, 6))
    k = base["NQ"].path.index[entry]
    cutoff = int(bars["NQ"].ts[base["NQ"].path.marks[k].point[0]])
    rows2 = {r: _perturb(rows[r], cutoff, [(entry, 15 * 60 + 1, 10**7, 10**7, "C9")])
             for r in roots}
    ctx2, bars2 = _build(cals, roots, days, rows2, rolls)
    after = {r: process_root(ctx2, bars2[r], r, with_tom=True) for r in roots}
    assert divisor_su({r: after[r].tom for r in roots}) == su
    for r in roots:
        o1 = [(o.day, o.target) for o in t3_orders(base[r], su, Counter()) if o.day <= entry]
        o2 = [(o.day, o.target) for o in t3_orders(after[r], su, Counter()) if o.day <= entry]
        assert o1 == o2 and any(t > 0 for _, t in o1)
