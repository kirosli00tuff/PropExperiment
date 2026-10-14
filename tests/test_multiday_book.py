"""multiday.book: fractional holdings, fills, roll costs (each roll leg pays |n| x the
per-contract cost), resizing, a failed hold excluded, the daily series."""

from __future__ import annotations

from collections import Counter
from datetime import date

import pytest

from base_rules.costs import vehicle_cost
from multiday import constants as K
from multiday.book import Order, assemble, process_root, simulate_book
from multiday.daily import fill_cost
from tests._base_rules_fixtures import make_bars
from tests.test_multiday_world import all_cals, ctx_for, utc_midnight, window

S = 15 * 60


@pytest.fixture(scope="module")
def cals():  # noqa: ANN201
    return all_cals()


def _world(cals, *, splice: bool = True):  # noqa: ANN001, ANN202
    d = window(cals["equity"], date(2016, 3, 7), date(2016, 3, 11))
    rows = [(x, m, 100 + 10 * k + (90 if k >= 2 else 0), 101 + 10 * k + (90 if k >= 2 else 0),
             "H6" if k < 2 else "M6") for k, x in enumerate(d) for m in (S - 1, S)]
    bars = make_bars("NQ", rows, [(utc_midnight(d[2]), d[2])] if splice else [])
    ctx = ctx_for(cals, {"NQ": bars}, starts={"NQ": d[0]})
    rd = process_root(ctx, bars, "NQ")
    for x in d:  # every date a possible fill date in these tests
        k = rd.path.index[x]
        pt = rd.path.marks[k].point
        rd.fills[x] = fill_cost(bars, vehicle_cost("NQ"), ctx.releases, pt[0], pt[1], None)
    return d, rd


@pytest.mark.parametrize("n", [0.5, -0.5])
def test_each_roll_leg_pays_abs_n_times_the_per_contract_cost(cals, n: float) -> None:
    d, rd = _world(cals)
    res = simulate_book(rd, [Order(d[0], n, "entry"), Order(d[4], 0.0, "exit")])
    kinds = [f["kind"] for f in res.fills]
    assert kinds == ["entry", "roll_out", "roll_in", "exit"]
    legs = [leg for iv in rd.path.intervals[1:] for leg in iv.rolls]
    out_side = "sell" if n > 0 else "buy"
    in_side = "buy" if n > 0 else "sell"
    for c in K.COST_CASES:
        assert res.fills[1]["cost"][c] == pytest.approx(abs(n) * float(
            legs[0].fill.cost[out_side][c]) / 100)
        assert res.fills[2]["cost"][c] == pytest.approx(abs(n) * float(
            legs[1].fill.cost[in_side][c]) / 100)
        total = sum(f["cost"][c] for f in res.fills)
        assert sum(res.cost[c].values()) == pytest.approx(total)
    assert res.fills[1]["side"] == out_side and res.fills[2]["side"] == in_side
    # gross: n x the per-contract cents of every interval / 100
    cents = sum(float(v) for iv in rd.path.intervals[1:] for _, v in iv.increments)
    assert sum(res.gross.values()) == pytest.approx(n * cents / 100)


def test_a_resize_fills_the_difference_only(cals) -> None:
    d, rd = _world(cals)
    res = simulate_book(rd, [Order(d[0], 1.0, "rebalance"), Order(d[3], 0.25, "rebalance"),
                             Order(d[4], 0.0, "rebalance")])
    resize = [f for f in res.fills if f["date"] == str(d[3])]
    assert len(resize) == 1 and resize[0]["trade"] == pytest.approx(-0.75)
    assert resize[0]["cost"][K.BASE] == pytest.approx(
        0.75 * float(rd.fills[d[3]].cost["sell"][K.BASE]) / 100)
    tv = float(rd.tick_value_cents)
    # the move from MK(d3) to MK(d4) accrues to the new holding 0.25
    assert res.gross[d[4]] == pytest.approx(0.25 * (10 * tv) / 100)


def test_a_contract_change_without_a_splice_excludes_the_hold(cals) -> None:
    d, rd = _world(cals, splice=False)
    res = simulate_book(rd, [Order(d[0], 1.0, "rebalance"), Order(d[4], 0.0, "rebalance")])
    assert res.fills == [] and res.gross == {}
    assert res.counters["hold excluded: contract change"] == 1
    assert res.holdings[0]["excluded"] == "contract change"


def test_the_series_sums_roots_and_is_zero_when_flat(cals) -> None:
    d, rd = _world(cals)
    res = simulate_book(rd, [Order(d[1], 1.0, "entry"), Order(d[3], 0.0, "exit")])
    c: Counter = Counter()
    series, per_root = assemble({"NQ": res}, d, c)
    base = dict(series[K.BASE])
    assert set(base) == set(d) and base[d[0]] == 0.0 and base[d[4]] == 0.0
    net = res.net(K.BASE)
    assert sum(base.values()) == pytest.approx(sum(net.values()))
    assert per_root["NQ"]["net_base"] == dict(sorted(net.items()))


def test_an_excluded_hold_is_counted_in_the_results_exclusions(cals) -> None:
    from multiday.evaluate import TestOutput, _book_summary

    d, rd = _world(cals, splice=False)
    res = simulate_book(rd, [Order(d[0], 1.0, "rebalance"), Order(d[4], 0.0, "rebalance")])
    c: Counter = Counter()
    series, per_root = assemble({"NQ": res}, d, c)
    out = TestOutput("T1", series, c)
    _book_summary(out, {"NQ": res}, d, per_root)
    assert out.record()["exclusions"]["hold excluded: contract change"] == 1
