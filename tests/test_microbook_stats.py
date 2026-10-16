"""microbook.stats and microbook.data helpers (synthetic data only)."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from base_rules.store import ProductBars, Splice
from microbook import stats as S
from microbook.data import merge_adjacent_splices


def test_bootstrap_same_seed_same_draws():
    x = np.random.default_rng(0).normal(10, 100, 2000)
    a = S.block_bootstrap_mdd(x, draws=500)
    b = S.block_bootstrap_mdd(x, draws=500)
    assert np.array_equal(a, b)
    c = S.block_bootstrap_mdd(x, draws=500, seed=S.BOOT_SEED + 1)
    assert not np.array_equal(a, c)


def test_bootstrap_draws_do_not_depend_on_chunking():
    x = np.random.default_rng(1).normal(0, 1, 500)
    assert np.array_equal(S.block_bootstrap_mdd(x, draws=300, chunk=7),
                          S.block_bootstrap_mdd(x, draws=300, chunk=1000))


def test_bootstrap_constant_loss_path_drawdown():
    x = np.full(100, -1.0)
    mdd = S.block_bootstrap_mdd(x, draws=50)
    assert np.allclose(mdd, 252.0)


def test_bootstrap_defaults_are_the_spec():
    assert (S.BOOT_BLOCK, S.BOOT_DRAWS, S.BOOT_LENGTH, S.BOOT_SEED) == (21, 10_000, 252, 20261016)


def test_max_drawdown_and_dates():
    x = np.array([1.0, 2.0, -4.0, -1.0, 3.0])
    dates = pd.bdate_range("2021-01-04", periods=5)
    dd = S.max_drawdown(x, dates)
    assert dd["max_dd"] == pytest.approx(5.0)
    assert dd["peak_date"] == "2021-01-05" and dd["trough_date"] == "2021-01-07"


def test_sharpe_annualised_with_252():
    x = np.array([1.0, -1.0, 2.0, 0.0])
    assert S.sharpe(x) == pytest.approx(x.mean() / x.std(ddof=1) * math.sqrt(252))
    assert S.sharpe(np.ones(5)) is None


def _bars(contracts: list[str], ts: list[int], splices: list[int]) -> ProductBars:
    symbols = tuple(sorted(set(contracts)))
    n = len(ts)
    return ProductBars(root="ZC", ts=np.array(ts, dtype=np.int64),
                       open_t=np.arange(n, dtype=np.int64), close_t=np.arange(n, dtype=np.int64),
                       sym=np.array([symbols.index(c) for c in contracts], dtype=np.int32),
                       symbols=symbols, usable=np.ones(n, bool),
                       td=np.arange(n, dtype=np.int64) + 730_000,
                       splices=tuple(Splice(s, None) for s in splices), blackout=frozenset(),
                       records=())


def test_adjacent_splices_with_no_bar_between_become_the_last_one():
    bars = _bars(["A", "A", "B", "B"], [10, 20, 40, 50], [30, 35])
    out, removed = merge_adjacent_splices(bars)
    assert removed == 1
    assert [s.ts_ns for s in out.splices] == [35]


def test_a_roll_away_and_back_with_no_bar_between_is_dropped():
    bars = _bars(["A", "A", "A", "A"], [10, 20, 40, 50], [30, 35])
    out, removed = merge_adjacent_splices(bars)
    assert removed == 2
    assert out.splices == ()


def test_separate_splices_are_kept():
    bars = _bars(["A", "B", "B", "C"], [10, 20, 40, 50], [15, 45])
    out, removed = merge_adjacent_splices(bars)
    assert removed == 0 and out is bars
