"""microbook.book: next-settlement fill timing, no look-ahead, rolls (two fills per contract),
per-side costs and the stress case (synthetic data only)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from microbook import book as B
from microbook.config_build import build_config, extension_cost_row
from microbook.universe import BY_CODE, MICROS, per_side_extension_cents


def _cfg():
    rows = {m.code: extension_cost_row(m) for m in MICROS}
    return build_config(fdm=1.0, fdm_corr=None, idm=1.0, idm_corr=None, idm_codes=None,
                        cost_rows=rows)


def _grid(F, V, d, *, mult=10.0, n_rolls=None, cost=(100.0, 100.0), slip=(50.0, 50.0),
          roll=(400.0, 400.0), roll_slip=(200.0, 200.0)) -> B.Grid:
    T = len(F)
    one = lambda x: np.full((T, 1), float(x))  # noqa: E731
    dates = pd.bdate_range("2020-01-01", periods=T)
    nr = np.zeros((T, 1)) if n_rolls is None else np.asarray(n_rolls, dtype=float)[:, None]
    has_roll = nr > 0
    return B.Grid(dates, ["X"], np.array([mult]), np.ones((T, 1), bool), np.ones((T, 1), bool),
                  np.asarray(F, float)[:, None], np.asarray(V, float)[:, None],
                  np.asarray(d, float)[:, None],
                  {"cost_buy": one(cost[0]), "cost_sell": one(cost[1]), "slip_buy": one(slip[0]),
                   "slip_sell": one(slip[1]), "roll_long": np.where(has_roll, roll[0], 0.0),
                   "roll_short": np.where(has_roll, roll[1], 0.0),
                   "roll_slip_long": np.where(has_roll, roll_slip[0], 0.0),
                   "roll_slip_short": np.where(has_roll, roll_slip[1], 0.0)},
                  nr, np.zeros((T, 1)), np.arange(T, dtype=np.int64))


def test_signal_from_settle_t_fills_at_t_plus_1_and_first_earns_at_t_plus_2():
    # Arrange: forecast 0 until the settlement of date 3, then +10
    F = [0, 0, 0, 10, 10, 10, 10]
    d = [5.0, -3.0, 7.0, 11.0, 13.0, -2.0, 4.0]
    g = _grid(F, [1000.0] * 7, d)
    # Act
    run = B.simulate(g, _cfg(), "unrounded", 25_000, np.ones(7))
    p = B.pnl(g, run)
    # Assert: N* = 1 x 25,000 x 0.2 x 1 x 1 / 1,000 = 5 contracts
    assert run.targets[3, 0] == pytest.approx(5.0)
    assert run.pos[3, 0] == 0.0 and run.pos[4, 0] == pytest.approx(5.0)
    assert p["gross"][3, 0] == 0.0  # the signal of settle(3) earns nothing at 3
    assert p["gross"][4, 0] == 0.0  # nor over (3, 4]: the fill is at settle(4)
    assert p["gross"][5, 0] == pytest.approx(5.0 * 10.0 * -2.0)
    assert p["trade"][4, 0] == pytest.approx(5.0)


def test_a_mark_free_grid_date_carries_position_and_books_nothing():
    g = _grid([10] * 5, [1000.0] * 5, [1.0] * 5)
    g.has_mark[2, 0] = False
    g.d[2, 0] = 0.0
    run = B.simulate(g, _cfg(), "unrounded", 25_000, np.ones(5))
    assert run.pos[2, 0] == run.pos[1, 0]
    assert B.pnl(g, run)["trade"][2, 0] == 0.0


def test_roll_pays_two_fills_per_contract_held():
    F = [10] * 6
    n_rolls = [0, 0, 0, 1, 0, 0]
    g = _grid(F, [1000.0] * 6, [0.0] * 6, n_rolls=n_rolls, roll=(400.0, 300.0))
    run = B.simulate(g, _cfg(), "unrounded", 25_000, np.ones(6))
    p = B.pnl(g, run)
    held = p["held"][3, 0]
    assert held == pytest.approx(5.0)
    assert p["roll_cost"][3, 0] == pytest.approx(held * 400.0 / 100.0)
    assert p["roll_cost"][[0, 1, 2, 4, 5], 0].sum() == 0.0


def test_extension_roll_cost_is_two_fills_of_the_per_side_cost():
    m = BY_CODE["MZC"]
    frame = _cache_frame(30, n_rolls_at=10)
    ins, _ = B.prepare(m, frame, _cfg())
    side = per_side_extension_cents(m)
    assert ins.frame["roll_long"].iloc[10] == pytest.approx(2.0 * side)
    assert ins.frame["roll_long"].drop(ins.frame.index[10]).sum() == 0.0


def test_trade_cost_uses_the_side_and_stress_doubles_slippage():
    F = [0, 10, 10, 0, 0]
    g = _grid(F, [1000.0] * 5, [0.0] * 5, cost=(100.0, 120.0), slip=(40.0, 60.0))
    run = B.simulate(g, _cfg(), "unrounded", 25_000, np.ones(5))
    base = B.pnl(g, run)
    stress = B.pnl(g, run, slip_mult=2.0)
    # buy 5 at date 2 (100 c per side), sell 5 at date 4 (120 c per side)
    assert base["trade_cost"][2, 0] == pytest.approx(5.0)
    assert base["trade_cost"][4, 0] == pytest.approx(6.0)
    assert stress["trade_cost"][2, 0] == pytest.approx(5 * 1.40)
    assert stress["trade_cost"][4, 0] == pytest.approx(5 * 1.80)


def test_per_side_extension_cost_arithmetic():
    assert per_side_extension_cents(BY_CODE["MNG"]) == pytest.approx(96.0 + 100.0)
    assert per_side_extension_cents(BY_CODE["MZL"]) == pytest.approx(96.0 + 120.0)
    assert per_side_extension_cents(BY_CODE["M6E"]) == pytest.approx(50.0 + 125.0)
    assert per_side_extension_cents(BY_CODE["2YY"], 2.0) == pytest.approx(96.0 + 200.0)


def test_simple_rounding_book_holds_integers_and_buffers():
    F = [10, 10, 11, 9, 10, 30]
    g = _grid(F, [1000.0] * 6, [0.0] * 6)
    run = B.simulate(g, _cfg(), "simple", 10_000, np.ones(6))
    assert np.all(run.targets == np.round(run.targets))
    # N* = 2.0 at F 10 (buffer 0.2): 2; F 11 -> 2.2 inside [2, 2]; F 30 -> 6
    assert run.targets[:5, 0].tolist() == [2.0, 2.0, 2.0, 2.0, 2.0]
    assert run.targets[5, 0] == 6.0


def _cache_frame(n: int, *, n_rolls_at: int | None = None, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dp = rng.normal(0, 1, n)
    dp[0] = np.nan
    price = 100 + np.nancumsum(np.nan_to_num(dp))
    nr = np.zeros(n, dtype=int)
    if n_rolls_at is not None:
        nr[n_rolls_at] = 1
    return pd.DataFrame({"date": pd.bdate_range("2015-01-01", periods=n), "contract": "A",
                         "price": price, "dp": dp, "fail": "", "n_rolls": nr,
                         "roll_long_c": 0.0, "roll_short_c": 0.0, "cost_buy_c": np.nan,
                         "cost_sell_c": np.nan, "comm_side_c": np.nan, "event": False})


def test_prepare_uses_only_data_through_each_date():
    cfg = _cfg()
    cfg["warmup_diffs"]["value"] = 50
    a = _cache_frame(400, seed=1)
    b = a.copy()
    b.loc[300:, "dp"] = b.loc[300:, "dp"] * 5 + 3  # change the future only
    ia, _ = B.prepare(BY_CODE["MNG"], a, cfg)
    ib, _ = B.prepare(BY_CODE["MNG"], b, cfg)
    for c in ["vol", "V", "live"] + B.speed_columns(cfg):
        pd.testing.assert_series_equal(ia.frame[c].iloc[:300], ib.frame[c].iloc[:300])


def test_prepare_live_after_warmup_diffs():
    cfg = _cfg()
    cfg["warmup_diffs"]["value"] = 50
    ins, _ = B.prepare(BY_CODE["MNG"], _cache_frame(120), cfg)
    assert not ins.frame["live"].iloc[49]  # 49 defined differences
    assert ins.frame["live"].iloc[50]


def test_prepare_yield_proxy_series_in_bp():
    cfg = _cfg()
    frame = _cache_frame(20)
    ins, _ = B.prepare(BY_CODE["10Y"], frame, cfg)
    k = 5
    expect = -frame["dp"].iloc[k] / (frame["price"].iloc[k] * 6.5 / 10_000)
    assert ins.frame["d"].iloc[k] == pytest.approx(expect)
    assert ins.micro.multiplier == 10.0  # $10 per bp
