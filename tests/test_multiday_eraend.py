"""Freeze review FR-1 and FR-2: the forced close at each era end (April 2019, February 2024) when
the month's last six dates lack the settlement bar; the non-fatal backstop close; a hold excluded
for a missing roll bar and for roll bars all inside fill-guard windows (the opener zeroed, the
next order reopening, the counter, the per-contract None entry)."""

from __future__ import annotations

from collections import Counter
from datetime import date

import pytest

from base_rules.context import empty_release_rules
from base_rules.costs import vehicle_cost
from multiday import constants as K
from multiday.book import BACKSTOP, Order, process_root, simulate_book, t12_orders
from multiday.daily import fill_cost
from multiday.signals import divisor_table
from tests._base_rules_fixtures import (
    context,
    group_calendars,
    hist_payload,
    make_bars,
    ns,
    settlement,
)
from tests.test_multiday_world import all_cals, ctx_for, utc_midnight, walk_prices, window

S = 15 * 60


@pytest.fixture(scope="module")
def era_world():  # noqa: ANN201
    """NQ 2017-01..2024-02 trending up; no bar S on the last six trade dates of April 2019 and
    of February 2024 (PS present, MK absent)."""
    cals = all_cals()
    days = window(cals["equity"], date(2017, 1, 3), date(2019, 4, 30)) + window(
        cals["equity"], date(2019, 5, 6), date(2024, 2, 29))
    apr = [d for d in days if (d.year, d.month) == (2019, 4)]
    feb = [d for d in days if (d.year, d.month) == (2024, 2)]
    no_mark = set(apr[-6:]) | set(feb[-6:])
    px = walk_prices(days, drift=0.0015, vol=0.004, seed=12)
    rows = []
    for d in days:
        sym = "M9" if d <= date(2019, 4, 30) else "U9"
        rows.append((d, S - 1, px[d], px[d], sym))
        if d not in no_mark:
            rows.append((d, S, px[d], px[d], sym))
    bars = make_bars("NQ", rows)
    ctx = ctx_for(cals, {"NQ": bars}, starts={"NQ": days[0]})
    rd = process_root(ctx, bars, "NQ")
    return {"ctx": ctx, "bars": bars, "rd": rd, "apr": apr, "feb": feb}


def _add_fills(w, days) -> None:  # noqa: ANN001
    rd = w["rd"]
    for d in days:
        pt = rd.path.marks[rd.path.index[d]].point
        rd.fills.setdefault(d, fill_cost(w["bars"], vehicle_cost("NQ"), w["ctx"].releases,
                                         pt[0], pt[1], None))


def test_the_forced_close_at_each_era_end(era_world) -> None:
    rd, apr, feb = era_world["rd"], era_world["apr"], era_world["feb"]
    assert rd.era_last_mark == {"ext2010": apr[-7], "step2": feb[-7]}
    c: Counter = Counter()
    orders = t12_orders(rd, "T1", divisor_table(era_world["ctx"], ["NQ"]), c)
    assert c["no eligible rebalance date"] == 2
    assert c["forced close at the era's last mark"] == 2
    by_day = {o.day: o for o in orders}
    for day in (apr[-7], feb[-7]):
        assert "forced close (era end)" in by_day[day].kind and by_day[day].target == 0.0
    mar = next(o for o in orders if o.info.get("month") == "2019-03" and o.kind == "rebalance")
    jan = next(o for o in orders if o.info.get("month") == "2024-01" and o.kind == "rebalance")
    assert mar.target > 0 and jan.target > 0
    res = simulate_book(rd, orders)
    closes = [f for f in res.fills if "forced close (era end)" in f["kind"]]
    assert [f["date"] for f in closes] == [str(apr[-7]), str(feb[-7])]
    for f, held in zip(closes, (mar.target, jan.target), strict=True):
        assert f["trade"] == pytest.approx(-held) and f["side"] == "sell"
        per = float(rd.fills[date.fromisoformat(f["date"])].cost["sell"][K.BASE])
        assert f["cost"][K.BASE] == pytest.approx(held * per / 100) and per > 0
    assert res.counters[BACKSTOP] == 0
    assert res.holdings[-1]["target"] == 0.0


def test_the_backstop_closes_a_position_held_across_an_era_end_or_past_the_last_mark(
        era_world) -> None:
    rd, apr, feb = era_world["rd"], era_world["apr"], era_world["feb"]
    may = date(2019, 5, 31)
    _add_fills(era_world, [apr[-10], may, feb[-10]])
    res = simulate_book(rd, [Order(apr[-10], 1e-6, "rebalance"), Order(may, 0.0, "rebalance")])
    assert res.counters[BACKSTOP] == 1
    assert [(f["date"], f["kind"]) for f in res.fills] == [(str(apr[-10]), "rebalance"),
                                                          (str(apr[-7]), BACKSTOP)]
    res2 = simulate_book(rd, [Order(feb[-10], 1e-6, "rebalance")])  # never closed
    assert res2.counters[BACKSTOP] == 1
    assert [f["date"] for f in res2.fills] == [str(feb[-10]), str(feb[-7])]
    assert res2.fills[-1]["trade"] == pytest.approx(-1e-6)


def _reopen_check(rd, d, why: str, none_day: date) -> None:  # noqa: ANN001
    res = simulate_book(rd, [Order(d[0], 1.0, "rebalance"), Order(d[-2], 0.5, "rebalance"),
                             Order(d[-1], 0.0, "rebalance")])
    assert res.counters[f"hold excluded: {why}"] == 1
    assert sum(v for k, v in res.counters.items() if k.startswith("hold excluded")) == 1
    assert res.holdings[0]["target"] == 0.0 and res.holdings[0]["excluded"] == why
    assert [(f["date"], f["trade"]) for f in res.fills] == [(str(d[-2]), 0.5),
                                                           (str(d[-1]), -0.5)]
    assert rd.path.per_contract_daily()[none_day] is None


def test_a_missing_roll_bar_excludes_the_hold_and_the_next_order_reopens() -> None:
    """A splice at the 15:15 closure instant of an R-B1 mark (the close of bar 15:14): no
    new-contract bar inside the interval -> "missing roll bar"."""
    seg = [{"start_offset_days": -1, "start_ct": "17:00", "end_offset_days": 0,
            "end_ct": "15:15"}]
    cals = {**all_cals(), "equity": group_calendars("equity", hist_payload("equity",
                                                                           segments=seg))}
    over = {"NQ": [{"from": "2010-06-07", "to": "2024-02-29", "minute_ct": "15:15",
                    "grade": "primary", "lead_grade": "primary"}]}
    d = window(cals["equity"], date(2016, 3, 7), date(2016, 3, 11))
    rows = [(x, 914, 100 + k, 101 + k, "H6" if k < 3 else "M6") for k, x in enumerate(d)]
    bars = make_bars("NQ", rows, [(ns(d[2], 915), d[2])])
    ctx = context(cals, {"NQ": bars}, st=settlement(overrides=over), starts={"NQ": d[0]},
                  releases=empty_release_rules())
    assert ctx.closure_at("NQ", d[2], 915)
    rd = process_root(ctx, bars, "NQ")
    assert rd.path.intervals[2].fail == "missing roll bar"
    _add_fills({"rd": rd, "bars": bars, "ctx": ctx}, d)
    _reopen_check(rd, [d[0], d[3], d[4]], "missing roll bar", d[2])


def test_roll_bars_all_in_guard_windows_exclude_the_hold() -> None:
    cals = all_cals()
    d = window(cals["equity"], date(2016, 3, 7), date(2016, 3, 10))
    rows = [(d[0], S, 100, 100, "H6"), (d[0], S + 1, 101, 101, "H6"),
            (d[0], S + 2, 102, 102, "H6"), (d[1], S - 1, 200, 200, "M6"),
            (d[1], S, 201, 201, "M6"), (d[2], S, 205, 205, "M6"), (d[3], S, 207, 207, "M6")]
    bars = make_bars("NQ", rows, [(utc_midnight(d[1]), d[1])])
    guarded = {int(bars.ts[bars.bar(d[0], m)]) for m in (S + 1, S + 2)}
    base = empty_release_rules()

    class Rel:
        calendar, fallback, hist_types, record = base.calendar, {}, frozenset(), {}

        def event(self, root, ts):  # noqa: ANN001, ANN202
            return False

        def guard(self, root, ts):  # noqa: ANN001, ANN202
            return ts in guarded

    ctx = ctx_for(cals, {"NQ": bars}, starts={"NQ": d[0]}, releases=Rel())
    rd = process_root(ctx, bars, "NQ")
    assert rd.path.intervals[1].fail == "missing roll bar (fill guard)"
    _add_fills({"rd": rd, "bars": bars, "ctx": ctx}, d)
    _reopen_check(rd, [d[0], d[2], d[3]], "missing roll bar (fill guard)", d[1])


def test_a_mark_in_neither_era_has_a_precomputed_fill_and_the_backstop_never_raises() -> None:
    """FR-9: a mark on 2019-05-03 (era None) beside the store boundary."""
    cals = all_cals()
    days = [date(2019, 4, 29), date(2019, 4, 30), date(2019, 5, 3), date(2019, 5, 6),
            date(2019, 5, 7)]
    rows = [(d, m, 100 + k, 100 + k, "M9") for k, d in enumerate(days) for m in (S - 1, S)]
    bars = make_bars("NQ", rows)
    ctx = ctx_for(cals, {"NQ": bars}, starts={"NQ": days[0]})
    rd = process_root(ctx, bars, "NQ")
    assert [m.day for m in rd.path.marks] == days
    assert {date(2019, 4, 30), date(2019, 5, 3), date(2019, 5, 6)} <= set(rd.fills)
    _add_fills({"rd": rd, "bars": bars, "ctx": ctx}, [days[0], days[-1]])
    res = simulate_book(rd, [Order(days[0], 1.0, "rebalance"), Order(days[-1], 0.0, "rebalance")])
    assert res.counters[BACKSTOP] == 1
    assert [(f["date"], f["kind"]) for f in res.fills] == [(str(days[0]), "rebalance"),
                                                          (str(days[1]), BACKSTOP)]
    res2 = simulate_book(rd, [Order(days[2], 1.0, "rebalance"), Order(days[-1], 0.0,
                                                                       "rebalance")])
    assert res2.counters[BACKSTOP] == 1 and res2.fills == []  # merged: never opened
