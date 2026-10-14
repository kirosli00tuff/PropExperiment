"""multiday.evaluate end to end on synthetic bars: a planted trend that T1 detects, pure noise that
it does not."""

from __future__ import annotations

from datetime import date

import pytest

from multiday import constants as K
from multiday.evaluate import evaluate
from multiday.stats import case_stats
from tests.test_multiday_world import all_cals, ctx_for, walk_prices, window, world_bars

ROOTS = ("NQ", "ZN", "GC")
GROUP = {"NQ": "equity", "ZN": "rates", "GC": "metals"}


def _run(drift: float, seed: int):  # noqa: ANN202
    cals = all_cals()
    bars = {}
    for k, r in enumerate(ROOTS):
        days = window(cals[GROUP[r]], date(2011, 1, 3), date(2018, 12, 31))
        sign = 1 if k % 2 == 0 else -1  # trends up and down
        px = walk_prices(days, drift=sign * drift, vol=0.006, seed=seed + k)
        bars[r] = world_bars(r, days, px.__getitem__)
    ctx = ctx_for(cals, bars, starts={r: date(2011, 1, 3) for r in ROOTS})
    return evaluate(ctx, None, roots=ROOTS, use_locks=False)


@pytest.fixture(scope="module")
def trend():  # noqa: ANN201
    return _run(0.0008, 31)


@pytest.fixture(scope="module")
def noise():  # noqa: ANN201
    return _run(0.0, 41)


def test_t1_detects_a_planted_trend(trend) -> None:
    s = case_stats([v for _, v in trend.tests["T1"].series[K.BASE]], K.NW_LAGS["T1"])
    assert s["t"] > 3.0 and s["p"] < 0.001 and s["sharpe_annualized"] > 1.0
    assert trend.tests["T1"].counters["no eligible rebalance date"] >= 1  # after the data end
    fk = trend.tests["T1"].fills_by_kind
    assert fk["rebalance"]["fills"] > 50
    ex = trend.tests["T1"].record()["exclusions"]  # FR-6: total and per root
    assert ex["return undefined: previous mark missing"] == len(ROOTS)
    assert all(ex[f"{r}: return undefined: previous mark missing"] == 1 for r in ROOTS)
    assert trend.tests["T3"].counters["NQ: return undefined: previous mark missing"] == 1
    t2 = case_stats([v for _, v in trend.tests["T2"].series[K.BASE]], K.NW_LAGS["T2"])
    assert t2["t"] > 3.0


def test_t1_finds_nothing_in_pure_noise(noise) -> None:
    s = case_stats([v for _, v in noise.tests["T1"].series[K.BASE]], K.NW_LAGS["T1"])
    assert s["p"] > K.HOLM_ALPHA


def test_costs_lower_net_and_the_cases_are_ordered(trend) -> None:
    gc = trend.tests["T1"].gross_costs
    assert 0 < gc[K.BASE]["costs"] < gc[K.STRESS]["costs"]
    assert gc[K.BASE]["costs"] <= gc[K.SLIP150]["costs"]
    assert trend.tests["T4"].series[K.BASE] and trend.tests["T3"].series[K.BASE]
    assert set(trend.roots) == set(ROOTS)
    assert trend.roots["NQ"]["per_contract_daily_dollars"]
