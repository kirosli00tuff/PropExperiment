"""base_rules runners on synthetic worlds: a planted edge each runner detects (Holm at 0.05/5,
n >= 30, year stability) and a pure-noise world each rejects; causality of every signal and of the
risk scaling (perturbing every bar at or after a decision instant changes neither)."""

from __future__ import annotations

from dataclasses import replace
from datetime import date

import numpy as np
import pytest

from base_rules import constants as K
from base_rules.auctions import Auction
from base_rules.h2 import _leg, months, run_h2
from base_rules.h3 import run_h3
from base_rules.h5 import Component, combine
from base_rules.intraday import candidate, product_units, run_intraday
from base_rules.scaling import TRADED, trailing_sigma, unit_sigmas
from base_rules.stats import stats_for_test
from tests._base_rules_fixtures import (
    SM,
    calendars,
    context,
    intraday_world,
    make_bars,
    ns,
    trade_dates,
)

FIRST, LAST = date(2014, 1, 2), date(2018, 12, 31)
STARTS = {p: date(2014, 1, 1) for p in K.PRODUCTS}


def passes(test: str, series) -> bool:  # noqa: ANN001
    s = stats_for_test(test, series)[K.BASE]
    return (s["p"] is not None and s["p"] <= K.HOLM_ALPHA / 5 and s["mean"] > 0
            and s["n"] >= K.MIN_UNITS and s["year_stability"]["passes"])


@pytest.fixture(scope="module")
def cals():  # noqa: ANN201
    return calendars(("equity", "rates"))


def _intraday_ctx(cals, h1: float, h4: float, seed: int):  # noqa: ANN001, ANN202
    bars = {p: intraday_world(p, trade_dates(cals[K.GROUP_OF[p]], FIRST, LAST), h1_edge=h1,
                              h4_edge=h4, noise=4.0, seed=seed + i)
            for i, p in enumerate(("NQ", "ZN"))}
    return context(cals, bars, starts=STARTS), bars


@pytest.mark.parametrize("test,edge", [("H1", (12.0, 0.0)), ("H4", (0.0, 12.0))])
def test_intraday_runner_detects_a_planted_edge_and_rejects_noise(cals, test, edge) -> None:
    ctx, _ = _intraday_ctx(cals, *edge, seed=11)
    out = run_intraday(test, ctx, ("NQ", "ZN"))
    assert passes(test, out.units), stats_for_test(test, out.units)[K.BASE]
    assert out.counters["warmup"] == 2 * K.WARMUP_UNITS
    ctx, _ = _intraday_ctx(cals, 0.0, 0.0, seed=11)
    noise = run_intraday(test, ctx, ("NQ", "ZN"))
    assert not passes(test, noise.units)
    assert len(noise.units[K.BASE]) >= K.MIN_UNITS


def test_h1_and_h4_decisions_ignore_every_bar_at_or_after_the_entry(cals) -> None:
    ctx, bars = _intraday_ctx(cals, 12.0, 12.0, seed=3)
    rng = np.random.default_rng(0)
    for test in ("H1", "H4"):
        for d in trade_dates(cals["equity"], date(2016, 3, 1), date(2016, 3, 31)):
            why, cand = candidate(test, ctx, bars["NQ"], "NQ", d)
            assert why is None and cand is not None
            cut = int(bars["NQ"].ts[cand[1][0]])
            late = bars["NQ"].ts >= cut
            noisy = replace(bars["NQ"], open_t=np.where(late, rng.integers(1, 10**6, late.size),
                                                        bars["NQ"].open_t),
                            close_t=np.where(late, rng.integers(1, 10**6, late.size),
                                             bars["NQ"].close_t))
            _, again = candidate(test, ctx, noisy, "NQ", d)
            assert again is not None and again[0] == cand[0]


def test_risk_scaling_sigma_ignores_every_bar_at_or_after_the_entry(cals) -> None:
    from collections import Counter

    ctx, bars = _intraday_ctx(cals, 12.0, 0.0, seed=5)
    units = product_units("H1", ctx, "ZN", bars["ZN"], Counter(), set())
    got = unit_sigmas([u.sim.entry_date for u in units], [u.sim.exit_date for u in units],
                      [u.g for u in units])
    k = 60
    assert got[k][0] == TRADED
    cut = int(bars["ZN"].ts[np.searchsorted(bars["ZN"].ts, units[k].sim.fills[0].ts_ns)])
    late = bars["ZN"].ts >= cut
    noisy = replace(bars["ZN"], open_t=np.where(late, bars["ZN"].open_t * 3, bars["ZN"].open_t))
    units2 = product_units("H1", ctx, "ZN", noisy, Counter(), set())
    got2 = unit_sigmas([u.sim.entry_date for u in units2], [u.sim.exit_date for u in units2],
                       [u.g for u in units2])
    assert got2[k] == got[k]
    assert [u.g for u in units2[:k]] == [u.g for u in units[:k]]


# ------------------------------------------------------------------ H2 ----
def _h2_world(cals, edge: float, seed: int):  # noqa: ANN001, ANN202
    rng = np.random.default_rng(seed)
    ctx0 = context(cals, {}, starts=STARTS)
    plan = {}
    for _ref, d5, d_last in months(ctx0):
        if d5 >= FIRST and d_last <= LAST:
            plan[d5] = d_last
    days = trade_dates(cals["equity"], FIRST, LAST)
    lv = {"NQ": 40000.0, "ZN": 8000.0}
    levels = {"NQ": {}, "ZN": {}}
    month_start = {}
    drift = {"NQ": 0.0, "ZN": 0.0}
    active_until = None
    for d in days:
        if d.month != (days[days.index(d) - 1].month if days.index(d) else 0):
            month_start = {x: levels[x].get(days[days.index(d) - 1], lv[x]) for x in lv}
        if d in plan:
            mtd = {x: lv[x] / month_start[x] - 1 for x in lv}
            sign_eq = -1 if mtd["NQ"] > mtd["ZN"] else 1
            n = sum(1 for x in days if d < x <= plan[d])
            drift = {"NQ": sign_eq * edge * 4 / n, "ZN": -sign_eq * edge / n}
            active_until = plan[d]
        elif active_until is not None and d > active_until:
            drift, active_until = {"NQ": 0.0, "ZN": 0.0}, None
        for x in lv:
            if d not in plan:
                lv[x] += drift[x] * (active_until is not None) + rng.normal(0, 6 if x == "NQ"
                                                                            else 3)
            levels[x][d] = int(round(lv[x]))
    bars = {}
    for x in lv:
        s = SM[K.GROUP_OF[x]][0]
        rows = [(d, m, v, v, "C1") for d, v in levels[x].items() for m in {s - 1, s, 900}]
        bars[x] = make_bars(x, rows)
    return context(cals, bars, starts=STARTS), bars


def test_h2_runner_detects_a_planted_month_end_reversal_and_rejects_noise(cals) -> None:
    ctx, _ = _h2_world(cals, 40.0, seed=2)
    out = run_h2(ctx)
    assert passes("H2", out.units), stats_for_test("H2", out.units)[K.BASE]
    ctx, _ = _h2_world(cals, 0.0, seed=2)
    noise = run_h2(ctx)
    assert not passes("H2", noise.units) and len(noise.units[K.BASE]) >= K.MIN_UNITS


def test_h2_decision_ignores_every_bar_at_or_after_the_decision(cals) -> None:
    ctx, bars = _h2_world(cals, 40.0, seed=4)
    for ref, d5, d_last in [m for m in months(ctx) if m[1].year == 2016]:
        cut = ns(d5, 900)
        base = {x: _leg(ctx, bars[x], x, ref, d5, d_last, 900)[1]["mtd"] for x in K.H2_LEGS}
        noisy = {}
        for x in K.H2_LEGS:
            late = bars[x].ts >= cut
            noisy[x] = replace(bars[x], close_t=np.where(late, bars[x].close_t * 2,
                                                         bars[x].close_t))
        again = {x: _leg(ctx, noisy[x], x, ref, d5, d_last, 900)[1]["mtd"] for x in K.H2_LEGS}
        assert again == base


# ------------------------------------------------------------------ H3 ----
def _h3_world(cals, edge: float, seed: int):  # noqa: ANN001, ANN202
    rng = np.random.default_rng(seed)
    days = trade_dates(cals["rates"], FIRST, LAST)
    auctions = [Auction(f"A{i}", "10Y", "ZN", days[i], "", days[i - 6])  # announced before t-3
                for i in range(10, len(days) - 10, 12)]
    move = {}
    for a in auctions:
        i = days.index(a.day)
        for k in range(i - 2, i + 1):
            move[days[k]] = -edge / 3
        for k in range(i + 1, i + 6):
            move[days[k]] = edge / 5
    lv, rows = 8000.0, []
    for d in days:
        lv += move.get(d, 0.0) + rng.normal(0, 3)
        rows.append((d, 840, int(round(lv)), int(round(lv)), "C1"))
    bars = {"ZN": make_bars("ZN", rows)}
    return context(cals, bars, starts=STARTS, auctions=auctions)


def test_h3_runner_detects_a_planted_auction_cycle_and_rejects_noise(cals) -> None:
    out = run_h3(_h3_world(cals, 12.0, seed=8))
    assert passes("H3", out.units), stats_for_test("H3", out.units)[K.BASE]
    assert out.counters["same-tenor overlap"] == 0
    noise = run_h3(_h3_world(cals, 0.0, seed=8))
    assert not passes("H3", noise.units) and len(noise.units[K.BASE]) >= K.MIN_UNITS


# ------------------------------------------------------------------ H5 ----
def _components(edge: float, seed: int) -> dict[str, Component]:
    rng = np.random.default_rng(seed)
    grid = [d for d in trade_dates(calendars(("rates",))["rates"], FIRST, LAST)]
    out = {}
    for i, name in enumerate(K.H5_COMPONENTS):
        x = rng.normal(edge, 1.0 + i, len(grid))
        daily = {c: dict(zip(grid, x - (0.01 if c != K.BASE else 0.0), strict=True))
                 for c in K.COST_CASES}
        out[name] = Component(name, daily, frozenset(grid))
    return out


def test_h5_combination_detects_planted_components_and_rejects_noise() -> None:
    out = combine(_components(0.12, 1))
    assert passes("H5", out.units)
    assert out.counters["warmup"] == K.H5_WARMUP
    assert not passes("H5", combine(_components(0.0, 1)).units)


def test_h5_scaling_ignores_every_value_at_or_after_the_date() -> None:
    x = list(np.random.default_rng(2).normal(0, 1, 200))
    k = 120
    sig = trailing_sigma(x)
    y = x[:k] + [v * 50 for v in x[k:]]
    assert trailing_sigma(y)[k] == sig[k]
    assert sig[k] == pytest.approx(float(np.std(x[k - 60:k], ddof=1)))
