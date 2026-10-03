"""Stage E.11 Task 4: sizing.contracts (docs/STAGE_E_ML_V2_DESIGN.md V2.8), hand-computed.

b = 0.10 x D_open / sqrt(3). At D_open = $2,000: b = 200 / 1.7320508 = $115.4700538;
2b = $230.9401077. At D_open = $1,500 (a balance after a payout, floor $0): b = $86.6025404.
"""

from __future__ import annotations

from math import sqrt

import pytest

from ml_route_v2.constants import RISK_ROUND_UP_RATIO
from ml_route_v2.sizing import (
    budget_contracts,
    budget_use,
    contracts,
    daily_variance_budget,
    excess_cost_ticks,
    risk_budget_usd,
)


def n(**kw) -> int:
    base = dict(d_open=2000.0, d_now=2000.0, sigma_ticks=70.0, loss_ticks=100.0, cost_ticks=3.0,
                tick_value_usd=0.5, product_cap=10, capacity_contracts=19)
    return contracts(**{**base, **kw})


def test_budget_is_a_tenth_of_d_over_root_three() -> None:
    assert risk_budget_usd(2000.0) == pytest.approx(115.47005383792515, abs=1e-12)
    assert risk_budget_usd(1500.0) == pytest.approx(86.60254037844386, abs=1e-12)


def test_risk_count_binds() -> None:
    # one sigma = 70 x 0.5 = $35 -> 115.47 / 35 = 3.299 -> 3
    # loss: 0.25 x 2000 = 500 / ((100 + 3) x 0.5 = 51.5) = 9.71 -> 9; caps 10, 19 -> n = 3
    assert n() == 3


def test_loss_cap_binds() -> None:
    # one sigma = 10 x 0.5 = $5 -> 23.09 -> 23; loss 500 / ((200 + 4) x 0.5 = 102) = 4.90 -> 4
    assert n(sigma_ticks=10.0, loss_ticks=200.0, cost_ticks=4.0) == 4


def test_product_cap_binds() -> None:
    # n_risk 23; loss 500 / ((20 + 2) x 0.5 = 11) = 45.45 -> 45; product cap 10
    assert n(sigma_ticks=10.0, loss_ticks=20.0, cost_ticks=2.0) == 10


def test_capacity_binds() -> None:
    assert n(sigma_ticks=10.0, loss_ticks=20.0, cost_ticks=2.0, capacity_contracts=6) == 6


def test_d_after_a_payout_sizes_down() -> None:
    # balance $1,500 after a payout, floor reset to $0: D = 1500. b = 86.60 / 35 = 2.47 -> 2;
    # loss 0.25 x 1500 = 375 / 51.5 = 7.28 -> 7 -> n = 2 (3 at D = 2000)
    assert n(d_open=1500.0, d_now=1500.0) == 2
    assert n() == 3


def test_d_now_below_d_open_tightens_the_loss_cap() -> None:
    # loss 0.25 x 400 = 100 / 51.5 = 1.94 -> 1; n_risk still 3 from D_open
    assert n(d_now=400.0) == 1


def test_ks2_multiplier_halves_the_budget() -> None:
    # budget 57.735 / 35 = 1.65 -> 1
    assert n(multiplier=0.5) == 1


@pytest.mark.parametrize("kw", [dict(d_open=0.0), dict(d_now=0.0), dict(d_now=-5.0),
                                dict(product_cap=0), dict(capacity_contracts=0),
                                dict(multiplier=0.0)])
def test_no_trade_cases(kw) -> None:
    assert n(**kw) == 0


# ---- the rounding band (lead amendment to V2.8: RISK_ROUND_UP_RATIO = 2.0) ----------------
def test_band_ratio_is_two() -> None:
    assert RISK_ROUND_UP_RATIO == 2.0


@pytest.mark.parametrize("sigma,expected", [
    (23.0, 1),  # $230.00 <= 2b = $230.94 -> n_risk 0 lifted to 1
    (23.1, 0),  # $231.00 > $230.94 -> stays 0
    (11.6, 1),  # $116.00: just above b ($115.47, floor 0.995 -> 0) and <= 2b -> 1
    (11.5, 1),  # $115.00 <= b: n_risk = floor(1.004) = 1 without the band
])
def test_band_on_both_sides_of_two_b(sigma: float, expected: int) -> None:
    # a $10.00-tick vehicle; loss 500 / ((10 + 2) x 10 = 120) = 4.17 -> 4, caps 10
    assert n(sigma_ticks=sigma, tick_value_usd=10.0, loss_ticks=10.0, cost_ticks=2.0) == expected


@pytest.mark.parametrize("sigma,expected", [(11.5, 1), (11.6, 0)])
def test_band_scales_with_the_ks2_multiplier(sigma: float, expected: int) -> None:
    # budget = 0.5 x 115.47 = 57.735; 2 x budget = $115.47: $115 -> 1, $116 -> 0
    assert n(sigma_ticks=sigma, tick_value_usd=10.0, loss_ticks=10.0, cost_ticks=2.0,
             multiplier=0.5) == expected


def test_band_still_obeys_the_loss_cap() -> None:
    # band lifts n_risk to 1, but loss 0.25 x 400 = 100 / 120 = 0.83 -> 0
    assert n(sigma_ticks=23.0, tick_value_usd=10.0, loss_ticks=10.0, cost_ticks=2.0,
             d_now=400.0) == 0


def test_floor_guard_keeps_an_exact_integer_ratio() -> None:
    # D_open = 1500 sqrt(3): b = 0.1 x 1500 sqrt(3) / sqrt(3) = 150 (float noise near 150);
    # one sigma = 50 x $1 -> exactly 3 in exact arithmetic
    assert n(d_open=1500.0 * sqrt(3), d_now=2000.0, sigma_ticks=50.0, tick_value_usd=1.0,
             loss_ticks=10.0, cost_ticks=0.0) == 3


@pytest.mark.parametrize("kw", [dict(sigma_ticks=0.0), dict(sigma_ticks=float("nan")),
                                dict(tick_value_usd=0.0), dict(loss_ticks=-1.0),
                                dict(cost_ticks=float("inf")), dict(d_open=float("nan")),
                                dict(loss_ticks=0.0, cost_ticks=0.0)])
def test_bad_inputs_raise_by_name(kw) -> None:
    with pytest.raises(ValueError, match="sizing_bad_input"):
        n(**kw)


# ---- design review D-03: the daily risk budget ---------------------------------------------------
def test_daily_budget_is_sigma_target_squared() -> None:
    assert daily_variance_budget(2000.0) == pytest.approx(40_000.0, abs=1e-9)  # (0.10 x 2000)^2
    assert daily_variance_budget(1500.0) == pytest.approx(22_500.0, abs=1e-9)
    assert budget_use(3, 70.0, 0.5) == pytest.approx(11_025.0, abs=1e-9)  # (3 x $35)^2
    assert budget_contracts(40_000.0, 70.0, 0.5) == 5  # floor(200 / 35)
    assert budget_contracts(35.0 ** 2, 70.0, 0.5) == 1  # exactly one contract's use fits
    assert budget_contracts(0.0, 70.0, 0.5) == 0 and budget_contracts(-1.0, 70.0, 0.5) == 0


def test_budget_consumption_over_a_day_of_nine_candidates_hand_computed() -> None:
    """One trade date at D_open = $2,000 (budget 40,000), loss cap and caps never binding; each
    candidate is (one sigma in $ at tick value $1 or $0.50) -> its n_risk, then the budget."""
    one_sigma = [35.0, 50.0, 60.0, 100.0, 80.0, 20.0, 35.0, 20.0, 20.0]
    remaining = daily_variance_budget(2000.0)
    sizes = []
    for usd in one_sigma:
        k = n(sigma_ticks=usd, tick_value_usd=1.0, loss_ticks=1.0, cost_ticks=0.0,
              budget_var=remaining)
        sizes.append(k)
        remaining -= budget_use(k, usd, 1.0)
    # $35: n_risk 3, budget floor(200 / 35) = 5 -> 3; 40,000 - 105^2 = 28,975
    # $50: n_risk 2, floor(170.22 / 50) = 3 -> 2; - 100^2 -> 18,975
    # $60: n_risk 1, floor(137.75 / 60) = 2 -> 1; - 3,600 -> 15,375
    # $100: n_risk 1, floor(124.00 / 100) = 1 -> 1; - 10,000 -> 5,375
    # $80: n_risk 1, floor(73.31 / 80) = 0 -> 0 (refused; nothing consumed)
    # $20: n_risk 5, floor(73.31 / 20) = 3 -> 3; - 60^2 -> 1,775
    # $35: n_risk 3, floor(42.13 / 35) = 1 -> 1; - 1,225 -> 550
    # $20: floor(23.45 / 20) = 1 -> 1; - 400 -> 150
    # $20: floor(12.25 / 20) = 0 -> 0: the budget is spent for every further entry of this size
    assert sizes == [3, 2, 1, 1, 0, 3, 1, 1, 0]
    assert remaining == pytest.approx(150.0, abs=1e-9)


def test_a_spent_budget_refuses_every_entry() -> None:
    assert n(budget_var=0.0) == 0
    assert n(sigma_ticks=1.0, budget_var=0.0) == 0  # however small the trade
    assert n(budget_var=None) == n() == 3  # no budget given: the single-trade size


def test_the_budget_clips_the_band_at_sigma_target() -> None:
    # band: one sigma $200 <= 2b = $230.94 -> n_risk 1; a fresh budget fits 200^2 exactly
    assert n(sigma_ticks=200.0, tick_value_usd=1.0, loss_ticks=1.0, budget_var=40_000.0) == 1
    # $201: still inside the band without the budget, but 201^2 > 200^2: refused
    assert n(sigma_ticks=201.0, tick_value_usd=1.0, loss_ticks=1.0) == 1
    assert n(sigma_ticks=201.0, tick_value_usd=1.0, loss_ticks=1.0, budget_var=40_000.0) == 0


def test_ks2_multiplier_scales_b_not_the_daily_budget() -> None:
    # KS2: b = 57.74 -> $35 one sigma -> 1; the budget (40,000) would allow 5
    assert n(multiplier=0.5, budget_var=40_000.0) == 1


def test_bad_budget_raises_by_name() -> None:
    with pytest.raises(ValueError, match="sizing_bad_input"):
        n(budget_var=float("nan"))


# ---- design review D-08a: the surcharge beyond q_c ----------------------------------------------
@pytest.mark.parametrize("k,q_c,expected", [
    (1, 1, 0.0), (3, 1, 4 / 3), (4, 1, 1.5), (2, 4, 0.0), (5, None, 0.0), (0, 1, 0.0),
    (10, 4, 1.2)])
def test_excess_cost_is_one_tick_a_side_per_contract_beyond_q_c(k: int, q_c, expected) -> None:
    assert excess_cost_ticks(k, q_c) == pytest.approx(expected, abs=1e-15)
