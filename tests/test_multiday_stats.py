"""multiday.stats and multiday.combine: t, Newey-West at the fixed lags, the p = max rule, Holm's
step-down at 0.025 (including a stop at the second test), the Sharpe annualization, the circular
block bootstrap (construction and seed determinism), and T4 equal to base_rules.h5.combine."""

from __future__ import annotations

import math
from datetime import date, timedelta

import numpy as np
import pytest
from scipy.stats import t as student_t

from base_rules import constants as BK
from base_rules.h5 import Component as H5Component
from base_rules.h5 import combine as h5_combine
from base_rules.stats import newey_west_se
from multiday import constants as K
from multiday.combine import Component, combine
from multiday.stats import (
    block_indices,
    bootstrap_sharpe,
    case_stats,
    holm_025,
    per_year,
    sharpe,
    verdict,
)


def test_the_fixed_lags_and_constants() -> None:
    assert dict(K.NW_LAGS) == {"T1": 21, "T2": 21, "T3": 5, "T4": 21}
    assert K.HOLM_ALPHA == 0.025 and K.SHARPE_BAR == 0.3
    assert (K.BOOT_BLOCK, K.BOOT_DRAWS, K.BOOT_SEED) == (21, 10_000, 20261014)
    assert K.TEST_IDS == {"T1": "E21-T1", "T2": "E21-T2", "T3": "E21-T3", "T4": "E21-T4"}


def test_t_newey_west_and_the_larger_p() -> None:
    rng = np.random.default_rng(1)
    x = rng.normal(0.02, 1.0, 500) + 0.5 * np.sin(np.arange(500) / 3)
    s = case_stats(list(x), 21)
    n, mean, sd = len(x), float(x.mean()), float(x.std(ddof=1))
    assert s["t"] == pytest.approx(mean / (sd / math.sqrt(n)))
    se = newey_west_se(x, 21)
    assert s["t_nw"] == pytest.approx(mean / se)
    assert s["p_t"] == pytest.approx(float(student_t.sf(s["t"], n - 1)))
    assert s["p_nw"] == pytest.approx(0.5 * math.erfc(s["t_nw"] / math.sqrt(2)))
    assert s["p"] == max(s["p_t"], s["p_nw"]) and s["nw_lags"] == 21
    assert s["sharpe_annualized"] == pytest.approx(mean / sd * math.sqrt(252))


def test_holm_at_0025_steps_down_and_stops_at_the_first_failure() -> None:
    # sorted: 0.001 <= 0.025/4; 0.009 > 0.025/3 -> stop; 0.010 would pass 0.025/2 but is not
    # reached; 0.02 not reached either
    got = holm_025({"T1": 0.009, "T2": 0.001, "T3": 0.010, "T4": 0.02})
    assert got == {"T1": False, "T2": True, "T3": False, "T4": False}
    assert holm_025({"T1": 0.006, "T2": 0.008, "T3": 0.012, "T4": 0.025}) == {
        "T1": True, "T2": True, "T3": True, "T4": True}
    assert holm_025({"T1": None, "T2": 0.001, "T3": 0.5, "T4": 0.5})["T2"] is True


def test_the_pass_bar_needs_holm_and_sharpe() -> None:
    base = {"T1": {"p": 0.001, "sharpe_annualized": 0.29}, "T2": {"p": 0.002,
                                                                  "sharpe_annualized": 0.8},
            "T3": {"p": 0.6, "sharpe_annualized": 1.0}, "T4": {"p": 0.003,
                                                               "sharpe_annualized": 0.3}}
    v = verdict(base, {})
    assert [v["tests"][t]["pass"] for t in K.TESTS] == [False, True, False, True]


def test_the_circular_block_construction_and_seed_determinism() -> None:
    rng = np.random.default_rng(0)
    idx = block_indices(rng, 50, 4, 21)
    assert idx.shape == (4, 50)
    for row in idx:
        for b in range(0, 42, 21):  # within a block: consecutive modulo n
            blk = row[b:b + 21]
            assert all((blk[j + 1] - blk[j]) % 50 == 1 for j in range(20))
    rng = np.random.default_rng(K.BOOT_SEED)
    starts = rng.integers(0, 50, size=(4, 3))
    assert (idx[0, :21] >= 0).all() and starts.shape == (4, 3)
    x = list(np.random.default_rng(2).normal(0.05, 1, 400))
    a, b = bootstrap_sharpe(x), bootstrap_sharpe(x)
    assert a == b and a["lo"] < sharpe(x) < a["hi"]
    assert bootstrap_sharpe(x, chunk=137) == a  # chunking does not change the draws
    assert bootstrap_sharpe(x, seed=1) != a


def test_per_year_tables() -> None:
    d0 = date(2015, 12, 30)
    series = [(d0 + timedelta(days=k), float(k)) for k in range(4)]
    py = per_year(series)
    assert py["2015"]["n"] == 2 and py["2016"]["n"] == 2 and py["2016"]["mean"] == 2.5


def test_t4_equals_base_rules_h5_combine_on_renamed_components() -> None:
    rng = np.random.default_rng(5)
    days = [date(2016, 1, 4) + timedelta(days=k) for k in range(250)]

    def comp(name: str, sub: list[date], scale: float) -> tuple[dict, frozenset]:
        daily = {c: {d: float(rng.normal(0, scale)) for d in sub} for c in K.COST_CASES}
        return daily, frozenset(sub)

    t2, g2 = comp("T2", days[::1], 1.0)
    t3, g3 = comp("T3", days[10::3], 0.3)
    h2, g2h = comp("H2", days[40::2], 2.0)
    mine, counters, _ = combine({"T2": Component("T2", t2, g2), "T3": Component("T3", t3, g3),
                                 "H2": Component("H2", h2, g2h)})
    ref = h5_combine({"H1": H5Component("H1", t2, g2), "H2": H5Component("H2", t3, g3),
                      "H3": H5Component("H3", h2, g2h)})
    for c in BK.COST_CASES:
        assert len(mine[c]) == len(ref.units[c])
        for (d1, v1), (d2, v2) in zip(mine[c], ref.units[c], strict=True):
            assert d1 == d2 and v1 == pytest.approx(v2, rel=1e-12, abs=1e-15)
    assert counters["warmup"] == K.T4_WARMUP and mine[K.BASE][0][0] == days[K.T4_WARMUP]
