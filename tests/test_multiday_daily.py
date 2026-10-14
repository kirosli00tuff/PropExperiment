"""multiday.daily: chaining across a splice (daily return and lookback), the per-contract path
against base_rules.sim.simulate, roll costs, the EWMA sigma, the store boundary."""

from __future__ import annotations

from collections import Counter
from datetime import date

import numpy as np
import pandas as pd
import pytest

from base_rules import constants as BK
from base_rules.context import empty_release_rules
from base_rules.costs import vehicle_cost
from base_rules.h2 import chained_return
from base_rules.sim import simulate
from multiday import constants as K
from multiday.daily import (
    build_path,
    chained_point_return,
    daily_returns,
    ewma_sigma_before,
    ewma_sigma_direct,
    fill_cost,
    marks_of,
    with_boundary_splice,
)
from tests._base_rules_fixtures import make_bars
from tests.test_multiday_world import all_cals, ctx_for, utc_midnight, window

S = 15 * 60  # equity settlement minute in the synthetic settlement table


@pytest.fixture(scope="module")
def cals():  # noqa: ANN201
    return all_cals()


def _splice_world(cals):  # noqa: ANN001, ANN202
    """NQ on five 2016 trade dates; contract H6, then M6 from a splice at 00:00 UTC of d3 (a roll
    gap of about +90); bar S - 1 and bar S carry distinct opens and closes."""
    d = window(cals["equity"], date(2016, 3, 7), date(2016, 3, 11))
    rows = [
        (d[0], S - 1, 100, 101, "H6"), (d[0], S, 102, 103, "H6"),
        (d[1], S - 1, 108, 109, "H6"), (d[1], S, 110, 112, "H6"),
        (d[2], S - 1, 200, 204, "M6"), (d[2], S, 205, 206, "M6"),
        (d[3], S - 1, 209, 210, "M6"), (d[3], S, 211, 211, "M6"),
        (d[4], S - 1, 215, 216, "M6"), (d[4], S, 220, 221, "M6"),
    ]
    bars = make_bars("NQ", rows, [(utc_midnight(d[2]), d[2])])
    ctx = ctx_for(cals, {"NQ": bars}, starts={"NQ": d[0]})
    return d, bars, ctx


def test_point_return_equals_h2_chained_return_for_close_points(cals) -> None:
    d, bars, _ = _splice_world(cals)
    i, j = bars.bar(d[1], S - 1), bars.bar(d[3], S - 1)
    got, why = chained_point_return(bars, (i, True), (j, True))
    want, why2 = chained_return(bars, i, j)
    assert why == why2 == "" and got == want
    # by hand: old segment close(d1 S-1)=109 -> close of the last bar before the splice (112);
    # new segment open of the first bar at or after it (200) -> close(d3 S-1)=210
    assert got == pytest.approx(112 / 109 * 210 / 200 - 1)


def test_the_daily_return_chains_across_the_splice(cals) -> None:
    d, bars, ctx = _splice_world(cals)
    marks = marks_of(ctx, bars, "NQ")
    assert [m.day for m in marks] == d
    c: Counter = Counter()
    rets = dict(daily_returns(ctx, bars, "NQ", marks, c))
    # MK(d1) = open of bar S = 110; old segment to close 112; new from open 200 to MK(d2) 205
    assert rets[d[2]] == pytest.approx(112 / 110 * 205 / 200 - 1)
    assert rets[d[1]] == pytest.approx(110 / 102 - 1)  # same contract
    assert d[0] not in rets and c["return undefined: previous mark missing"] == 1


def test_a_contract_change_without_a_splice_makes_the_return_undefined(cals) -> None:
    d = window(cals["equity"], date(2016, 3, 7), date(2016, 3, 9))
    rows = [(x, m, 100, 100, "H6" if k < 2 else "M6") for k, x in enumerate(d)
            for m in (S - 1, S)]
    bars = make_bars("NQ", rows)
    ctx = ctx_for(cals, {"NQ": bars}, starts={"NQ": d[0]})
    c: Counter = Counter()
    rets = dict(daily_returns(ctx, bars, "NQ", marks_of(ctx, bars, "NQ"), c))
    assert d[2] not in rets and c["return undefined: contract change"] == 1
    path = build_path(ctx, bars, "NQ", vehicle_cost("NQ"))
    assert path.intervals[2].fail == "contract change"


def test_the_per_contract_path_equals_sims_daily_attribution_with_a_roll(cals) -> None:
    d, bars, ctx = _splice_world(cals)
    vc = vehicle_cost("NQ")
    rel = empty_release_rules()
    path = build_path(ctx, bars, "NQ", vc)
    pts = [m.point for m in path.marks]
    sim = simulate(bars, vc, rel, [(pts[0], 1), (pts[-1], 0)], pts[1:-1])
    assert sim.ok
    mine: dict = {}
    for iv in path.intervals[1:]:
        for day, cents in iv.increments:
            mine[day] = mine.get(day, 0) + cents
    entry = fill_cost(bars, vc, rel, pts[0][0], pts[0][1], None)
    exit_ = fill_cost(bars, vc, rel, pts[-1][0], pts[-1][1], None)
    legs = [leg for iv in path.intervals[1:] for leg in iv.rolls]
    assert [leg.kind for leg in legs] == ["roll_out", "roll_in"]
    for c in K.COST_CASES:
        costs: dict = {}
        for day, v in ((entry.day, entry.cost["buy"][c]), (exit_.day, exit_.cost["sell"][c]),
                       (legs[0].fill.day, legs[0].fill.cost["sell"][c]),
                       (legs[1].fill.day, legs[1].fill.cost["buy"][c])):
            costs[day] = costs.get(day, 0) + v
        days = set(mine) | set(costs) | set(sim.daily[c])
        for day in days:
            assert mine.get(day, 0) - costs.get(day, 0) == sim.daily[c].get(day, 0), (c, day)
    # the per-fill cost equals VehicleCost.fill_costs and sim's fills
    sim_costs = [f.costs[K.BASE] for f in sim.fills]
    assert sim_costs == [entry.cost["buy"][K.BASE], legs[0].fill.cost["sell"][K.BASE],
                         legs[1].fill.cost["buy"][K.BASE], exit_.cost["sell"][K.BASE]]
    per_side, _ = vc.fill_costs(entry.ts, "buy", False)
    assert entry.cost["buy"] == dict(per_side)
    # roll gain by hand: out at the open of the last bar before the splice (110), in at 200
    assert path.intervals[2].increments == ((d[1], (110 - 110) * vc.tick_value_cents),
                                            (d[2], (205 - 200) * vc.tick_value_cents))


def test_a_roll_leg_in_a_guard_window_moves_to_the_nearest_unguarded_bar(cals) -> None:
    d = window(cals["equity"], date(2016, 3, 7), date(2016, 3, 9))
    rows = [(d[0], S, 100, 100, "H6"), (d[0], S + 1, 101, 101, "H6"),
            (d[0], S + 2, 102, 102, "H6"), (d[1], S - 1, 200, 200, "M6"),
            (d[1], S, 201, 201, "M6"), (d[2], S - 1, 205, 205, "M6"), (d[2], S, 206, 206, "M6")]
    bars = make_bars("NQ", rows, [(utc_midnight(d[1]), d[1])])
    guarded = int(bars.ts[bars.bar(d[0], S + 2)])
    base = empty_release_rules()

    class Rel:
        calendar, fallback, hist_types, record = base.calendar, {}, frozenset(), {}

        def event(self, root, ts):  # noqa: ANN001, ANN202
            return False

        def guard(self, root, ts):  # noqa: ANN001, ANN202
            return ts == guarded

    ctx = ctx_for(cals, {"NQ": bars}, starts={"NQ": d[0]}, releases=Rel())
    path = build_path(ctx, bars, "NQ", vehicle_cost("NQ"))
    leg = path.intervals[1].rolls[0]
    assert leg.moved and leg.fill.price == 101 and path.counters[
        "roll legs moved by the fill guard"] == 1


def test_the_ewma_equals_a_direct_summation_and_pandas() -> None:
    rng = np.random.default_rng(7)
    r = list(rng.normal(0, 0.01, 300))
    days = [date(2015, 1, 1).fromordinal(date(2015, 1, 1).toordinal() + k) for k in range(301)]
    got = ewma_sigma_before(list(zip(days[:300], r, strict=True)), [days[300]])[days[300]]
    assert got == pytest.approx(ewma_sigma_direct(r), rel=1e-10)
    pd_var = pd.Series(r).ewm(com=K.EWMA_COM, adjust=True).var(bias=True).iloc[-1]
    assert got == pytest.approx(float(np.sqrt(pd_var * K.ANNUALIZATION)), rel=1e-10)
    assert pytest.approx(60 / 61) == K.EWMA_DELTA


def test_sigma_uses_returns_strictly_before_d_and_needs_sixty() -> None:
    days = [date.fromordinal(date(2015, 1, 1).toordinal() + k) for k in range(80)]
    rets = [(x, 0.01 * ((k % 5) - 2)) for k, x in enumerate(days)]
    sig = ewma_sigma_before(rets, days)
    assert sig[days[59]] is None and sig[days[60]] is not None  # 60 returns dated before
    moved = [(x, v if x < days[70] else 9.0) for x, v in rets]  # change d and later
    assert ewma_sigma_before(moved, [days[70]])[days[70]] == sig[days[70]]


def test_the_store_boundary_splits_a_lookback_only_on_a_contract_change() -> None:
    rows_a = [(date(2019, 4, 29), S - 1, 100, 100, "M9"), (date(2019, 4, 30), S - 1, 102, 104,
                                                            "M9"),
              (date(2019, 5, 6), S - 1, 300, 303, "U9"), (date(2019, 5, 7), S - 1, 306, 309, "U9")]
    bars = make_bars("NQ", rows_a)
    i, j = bars.bar(date(2019, 4, 29), S - 1), bars.bar(date(2019, 5, 7), S - 1)
    assert chained_return(bars, i, j)[0] is None  # raw: a contract change
    split, ts = with_boundary_splice(bars)
    assert ts == int(bars.ts[bars.bar(date(2019, 5, 6), S - 1)])
    got, _ = chained_return(split, i, j)
    assert got == pytest.approx(104 / 100 * 309 / 300 - 1)
    same = make_bars("NQ", [(x[0], x[1], x[2], x[3], "M9") for x in rows_a])
    assert with_boundary_splice(same)[1] is None
    assert BK.HIST_LAST == K.HIST_LAST == date(2019, 4, 30)


def test_a_non_positive_price_makes_returns_and_lookbacks_undefined_never_raises(cals) -> None:
    """R-B3 (CL traded below zero in April 2020): counted, never a ZeroDivisionError."""
    from multiday.signals import lookback

    d = window(cals["equity"], date(2016, 3, 7), date(2016, 3, 10))
    rows = [(d[0], S - 1, 10, 10, "H6"), (d[0], S, 0, 0, "H6"), (d[1], S - 1, -5, -5, "H6"),
            (d[1], S, -4, -4, "H6"), (d[2], S - 1, 3, 3, "H6"), (d[2], S, 4, 4, "H6"),
            (d[3], S - 1, 5, 5, "H6"), (d[3], S, 6, 6, "H6")]
    bars = make_bars("NQ", rows)
    ctx = ctx_for(cals, {"NQ": bars}, starts={"NQ": d[0]})
    c: Counter = Counter()
    rets = dict(daily_returns(ctx, bars, "NQ", marks_of(ctx, bars, "NQ"), c))
    assert set(rets) == {d[3]} and c["return undefined: non-positive price"] == 2
    assert lookback(ctx, bars, "NQ", d[1], d[3], None, c) == (None, "non-positive price")
    assert lookback(ctx, bars, "NQ", d[0], d[2], None, c)[0] == pytest.approx(3 / 10 - 1)
    assert lookback(ctx, bars, "NQ", d[2], d[3], None, c)[0] == pytest.approx(5 / 3 - 1)
