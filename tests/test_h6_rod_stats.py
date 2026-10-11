"""h6_rod.stats and h6_rod.report's descriptive numbers (prereg sections 4-6), hand-computed."""

from __future__ import annotations

import math
from datetime import date
from fractions import Fraction
from types import SimpleNamespace

import numpy as np
import pytest
from scipy.stats import t as student_t

from h6_rod import constants as K
from h6_rod import report, stats

RULES = SimpleNamespace(tick_value=lambda root: 50, ticks_price=lambda root, n: 0.25 * n,
                        price_ticks=lambda root, p: round(p / 0.25))


def _trade(day: date, gross_ticks: int, *, side: str = "buy", entry: float = 15000.0,
           slip_ticks: tuple[float, float] = (0.8174194479295556, 0.8174194479295556),
           reason: str = "strategy") -> stats.Trade:
    slip = sum(math.ceil(round(s * 50, 6)) for s in slip_ticks)
    move = gross_ticks * 0.25 * (1 if side == "buy" else -1)
    return stats.Trade(day, side, 0, 1, entry, entry + move, Fraction(gross_ticks * 50), 122, slip,
                       slip_ticks, (1, 1), reason, stats.exit_type(reason, False), 2, 0,
                       (False, False), True)


# ------------------------------------------------------------------ the b test ----
def test_b_test_wrapper_gives_the_hand_computed_date_t_on_net_ticks() -> None:
    days = [date(2022, 3, 14), date(2022, 3, 15), date(2022, 3, 16), date(2022, 3, 17)]
    trades = [_trade(d, g) for d, g in zip(days, (10, -2, 7, 3), strict=True)]
    net = np.array([g - 4.08 for g in (10, -2, 7, 3)])  # c = 204 cents = 4.08 ticks each
    t_hand = net.mean() / (net.std(ddof=1) / math.sqrt(4))
    bt = stats.b_test("E20-H6-T1", trades, RULES)
    assert bt.t == pytest.approx(t_hand)
    assert bt.p == pytest.approx(float(student_t.sf(t_hand, 3)))
    assert bt.mean == pytest.approx(net.mean()) and bt.cost_ticks == pytest.approx(4.08)
    assert bt.n_dates == 4 and bt.n_trades == 4 and bt.family == "B"


def test_b_test_with_one_trade_has_no_t_and_p_one() -> None:
    bt = stats.b_test("x", [_trade(date(2022, 3, 14), 5)], RULES)
    assert math.isnan(bt.t) and bt.p == 1.0


# ------------------------------------------------------------------ Holm ----
@pytest.mark.parametrize(("pvals", "rejected"), [
    ({"T1": 0.01, "T2": 0.02}, {"T1": True, "T2": True}),
    ({"T1": 0.013, "T2": 0.001}, {"T1": True, "T2": True}),
    ({"T1": 0.02, "T2": 0.013}, {"T1": False, "T2": False}),  # 0.013 > 0.0125: stops at k = 1
    ({"T1": 0.012, "T2": 0.3}, {"T1": True, "T2": False}),
    ({"T1": 0.008, "T2": 0.012, "T3": 0.03}, {"T1": True, "T2": True, "T3": False}),
    ({"T1": 0.009, "T2": 0.001, "T3": 0.02}, {"T1": True, "T2": True, "T3": True}),
    ({"T1": 0.0084, "T2": 0.001, "T3": 0.002}, {"T1": True, "T2": True, "T3": True}),
    ({"T1": 0.009, "T2": 0.02, "T3": 0.001}, {"T1": True, "T2": True, "T3": True}),
    ({"T1": 0.0125, "T2": 0.0125, "T3": 0.0}, {"T1": True, "T2": True, "T3": True}),
    ({"T1": 0.0126, "T2": 0.0126, "T3": 0.0}, {"T1": False, "T2": False, "T3": True}),
])
def test_holm_step_down(pvals: dict, rejected: dict) -> None:
    h = stats.holm(pvals, 0.025)
    assert h["rejected"] == rejected and h["m"] == len(pvals)
    bounds = [s["bound"] for s in h["steps"]]
    assert bounds == pytest.approx([0.025 / (len(pvals) - k) for k in range(len(pvals))])


# ------------------------------------------------------------------ Sharpe ----
def test_sharpe_counts_every_window_trade_date_with_zeros() -> None:
    days = [date(2022, 3, d) for d in (14, 15, 16, 17, 18)]
    trades = [_trade(days[1], 20), _trade(days[3], -6)]
    daily = stats.daily_net_usd(trades, days)
    expected = np.array([0.0, (20 * 50 - 204) / 100, 0.0, (-6 * 50 - 204) / 100, 0.0])
    assert daily.to_numpy() == pytest.approx(expected)
    want = expected.mean() / expected.std(ddof=1) * math.sqrt(252)
    assert stats.annualized_sharpe(daily) == pytest.approx(want)
    assert math.isnan(stats.annualized_sharpe([0.0, 0.0, 0.0]))
    assert math.isnan(stats.annualized_sharpe([1.0]))
    with pytest.raises(ValueError, match="outside"):
        stats.daily_net_usd([_trade(date(2022, 3, 21), 1)], days)


# ------------------------------------------------------------------ the pass bar ----
def test_pass_bar_needs_all_four_items() -> None:
    ok = {"holm_rejected": True, "mean_gross": 6.2, "mean_cost": 4.08, "n_trades": 100,
          "sharpe": 0.5}
    assert stats.pass_bar("T1", **ok)["verdict"] == K.PASS
    for key, bad in (("holm_rejected", False), ("mean_gross", 6.11), ("n_trades", 99),
                     ("sharpe", 0.4999), ("sharpe", float("nan"))):
        assert stats.pass_bar("T1", **{**ok, key: bad})["verdict"] == K.FAIL, key
    assert stats.pass_bar("T3", **{**ok, "n_trades": 30})["verdict"] == K.PASS
    assert stats.pass_bar("T3", **{**ok, "n_trades": 29})["verdict"] == K.FAIL
    assert stats.pass_bar("T1", **{**ok, "mean_gross": float("nan")})["verdict"] == K.FAIL


def test_core_numbers_on_trades() -> None:
    days = [date(2022, 3, d) for d in (14, 15, 16)]
    trades = [_trade(days[0], 10), _trade(days[2], 2, side="sell")]
    core = stats.core_numbers("x", trades, days, RULES)
    assert core["n_trades"] == 2 and core["window_trade_dates"] == 3
    assert core["mean_gross_ticks"] == pytest.approx(6.0)
    assert core["mean_cost_ticks"] == pytest.approx(4.08)
    assert core["mean_net_ticks"] == pytest.approx(6.0 - 4.08)
    assert core["net_usd_total"] == pytest.approx((12 * 50 - 2 * 204) / 100)


# ------------------------------------------------------------------ descriptive ----
def test_stress_reprices_each_sides_slippage_at_one_and_a_half_with_the_frozen_rounding() -> None:
    days = [date(2022, 3, 14)]
    trades = [_trade(days[0], 10, slip_ticks=(0.8174194479295556, 0.8717006751787222))]
    s = report.stress("x", trades, days, RULES)
    side = [math.ceil(round(1.5 * x * 50, 6)) for x in (0.8174194479295556, 0.8717006751787222)]
    assert side == [62, 66]
    assert s["mean_cost_ticks"] == pytest.approx((122 + 62 + 66) / 50)
    assert s["multiple"] == 1.5


def test_basis_points_of_the_entry_fill_price() -> None:
    trades = [_trade(date(2022, 3, 14), 40, entry=10000.0)]  # 10 points on 10000
    bp = report.basis_points(trades, RULES)
    assert bp["mean_gross_bp"] == pytest.approx(10.0)
    assert bp["mean_net_bp"] == pytest.approx((40 - 4.08) * 0.25 / 10000 * 1e4)


def test_exit_types_name_the_flatten_on_a_shortened_day() -> None:
    assert stats.exit_type("forced_flatten", True) == "flatten_shortened_day"
    assert stats.exit_type("forced_flatten", False) == "forced_flatten"
    assert stats.exit_type("strategy", False) == "c2_exit"
    assert stats.exit_type("price_limit_exit", False) == "d97_price_limit_exit"
    assert stats.exit_type("mll_liquidation", False) == "mll_breach_flatten"
    assert stats.exit_type("end_of_data", False) == "end_of_data"


def test_per_year_buckets_split_the_verdict_window() -> None:
    days = [date(2020, 6, 1), date(2021, 1, 4), date(2024, 2, 29)]
    trades = [_trade(days[0], 8), _trade(days[1], -3), _trade(days[2], 1)]
    py = report.per_year("x", trades, days, RULES)
    assert list(py) == ["2020-06..12", "2021", "2022", "2023", "2024-01..02"]
    assert [py[k]["n_trades"] for k in py] == [1, 1, 0, 0, 1]
