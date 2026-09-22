"""Known-answer tests for Stage D.1e Task 3 (strategy/research/_d1e_power.py).

Every test is deterministic: fixed seeds, fixed series, expectations computed in
the test from the normal quantiles rather than copied from a run.
"""

from __future__ import annotations

import math
from datetime import date, timedelta
from statistics import NormalDist

import numpy as np
import pytest

from strategy.research import _d1e_calendar as cal
from strategy.research import _d1e_power as power
from strategy.research import _d1e_power_stats as stats

ND = NormalDist()
Z_POWER = ND.inv_cdf(0.80)
Z_UCB = ND.inv_cdf(0.95)
Z_HOLM = ND.inv_cdf(1.0 - 0.05 / 58)

IID_SIGMA = 10.0
# 50,000 days, not 5,000: the VIF estimator is unbiased but its sampling sd is
# about 0.047 at n = 5,000, so a +/-0.05 band there is barely one sd wide and
# most seeds miss it. At 50,000 the sd is about 0.015 and the band is a real
# test of the estimator rather than of the seed (lead ruling, Stage D.1e).
IID_DAYS = 50000
IID_SEED = 20260922
EPS_TEST = 2.0
AR_PHI = 0.3
AR_DAYS = 20000
AR_SEED = 4242
REPS = 2000


def _iid_series() -> np.ndarray:
    return np.random.default_rng(IID_SEED).normal(0.0, IID_SIGMA, IID_DAYS)


def _ar1_series() -> np.ndarray:
    """AR(1) with phi = 0.3, scaled so the marginal sd is about IID_SIGMA."""
    rng = np.random.default_rng(AR_SEED)
    innovation_sd = IID_SIGMA * math.sqrt(1.0 - AR_PHI**2)
    shocks = rng.normal(0.0, innovation_sd, AR_DAYS)
    out = np.empty(AR_DAYS)
    out[0] = shocks[0]
    for t in range(1, AR_DAYS):
        out[t] = AR_PHI * out[t - 1] + shocks[t]
    return out


def _expected_n(z_level: float, series: np.ndarray, vif: float, eps: float) -> int:
    sd = float(np.std(series, ddof=1))
    return int(math.ceil((((z_level + Z_POWER) * sd * math.sqrt(vif)) / eps) ** 2))


def _power_at(series: np.ndarray, n: int, seed: int) -> dict[str, float]:
    centred = series - series.mean()
    curve, _floor, _degenerate = stats.simulate_powers(centred, EPS_TEST, [n], seed, REPS)
    return curve[n]


# --------------------------------------------------------------- tests 1-3 ----


def test_iid_series_has_unit_vif_and_textbook_null_sample_size():
    """1. iid normal: VIF ~ 1, n_b matches the closed form, simulated power ~ 0.80.

    The closed form is recomputed here from ``statistics.NormalDist`` quantiles,
    not read off the module's constants (scipy is not a project dependency).
    """
    series = _iid_series()
    vif, floored = stats.variance_inflation(series)

    assert not floored
    assert vif == pytest.approx(1.0, abs=0.05)

    sd = float(np.std(series, ddof=1))
    expected = _expected_n(Z_UCB, series, vif, EPS_TEST)
    # sd ~ 10 and vif ~ 1 put this at about 155 days.
    assert 140 <= expected <= 175
    assert stats.analytic_sample_size(Z_UCB, sd, vif, EPS_TEST) == expected

    assert _power_at(series, expected, seed=1)["power_b"] == pytest.approx(0.80, abs=0.03)


def test_iid_series_detection_sample_size_matches_the_textbook_value():
    """2. Same series: n_a at the Holm-corrected level, simulated power ~ 0.80."""
    series = _iid_series()
    vif, _floored = stats.variance_inflation(series)
    sd = float(np.std(series, ddof=1))

    expected = _expected_n(Z_HOLM, series, vif, EPS_TEST)
    # The Holm level 0.05/58 puts this at about 396 days.
    assert 360 <= expected <= 440
    assert stats.analytic_sample_size(Z_HOLM, sd, vif, EPS_TEST) == expected

    assert _power_at(series, expected, seed=2)["power_a"] == pytest.approx(0.80, abs=0.03)


def test_ar1_series_vif_matches_the_bootstrap_implied_factor_not_the_true_one():
    """3. AR(1), phi = 0.3: VIF_boot is the BLOCK-5 factor, which under-corrects.

    The stationary bootstrap with p = 1/5 weights gamma_k by (1-p)^k, so for an
    AR(1) it converges to 1 + 2 * sum_{k=1..K} ((1-p)*phi)^k = 1.632 here. The
    TRUE long-run factor is (1+phi)/(1-phi) = 1.857, which is larger: the
    program's block-5 inference under-covers an AR(1) with phi = 0.3 by that
    much, by design. This test pins the bootstrap-implied factor, which is what
    the program's own sample sizes are built on.

    The final assertion is also the regression test for the simulation SE. A
    replicate's own lag-k autocovariance is already about (1-p)^k times the
    source's, so a V_B computed from the replicate attenuates the dependence
    term twice; that version measured power_b = 0.848 here, outside the band.
    ``simulate_powers`` takes gamma_0 from the replicate and the inflation
    factor from the source, which puts an autocorrelated member back on 0.80.
    """
    series = _ar1_series()
    vif, floored = stats.variance_inflation(series)

    weight = (1.0 - stats.BOOTSTRAP_RENEWAL_P) * AR_PHI
    bootstrap_implied = 1.0 + 2.0 * sum(weight**k for k in range(1, stats.MAX_LAG_K + 1))
    true_long_run = (1.0 + AR_PHI) / (1.0 - AR_PHI)

    assert not floored
    assert bootstrap_implied == pytest.approx(1.6316, abs=1e-3)
    assert true_long_run == pytest.approx(1.8571, abs=1e-3)
    assert bootstrap_implied < true_long_run
    assert vif == pytest.approx(bootstrap_implied, rel=0.10)

    expected = _expected_n(Z_UCB, series, vif, EPS_TEST)
    assert _power_at(series, expected, seed=3)["power_b"] == pytest.approx(0.80, abs=0.04)


# ----------------------------------------------------------------- test 4 ----


def test_unit_conversions_for_trials_and_statistics():
    """4. A trial series passes through per-micro; a statistic is signed sum minus cost.

    R-1 (reports/stage_d1e_adjudication.md): the trial series arrives already
    divided per micro - each round trip by its OWN contract quantity, so a day
    holding one trip of $5.00 on 2 micros is 5.00 / (1.25 * 2) = 2.0 ticks per
    micro - and this module must not rescale it by any assumed position size.
    """
    per_micro = [2.0, -2.0, 0.0]
    assert per_micro[0] == 5.0 / (1.25 * 2)  # one trip, $5.00, 2 micros
    trial = power.trial_series({"daily_net_ticks_per_micro": per_micro})
    assert trial.tolist() == per_micro  # taken as is, no 2-micro assumption
    assert not hasattr(power, "USD_PER_TICK_2_MICROS")

    statistic = power.statistic_series(
        {"recorded_direction": -1, "daily_sum_ticks": [10.0, -4.0], "daily_count": [2, 1]}
    )
    assert statistic == pytest.approx([-10.0 - 4.22, 4.0 - 2.11])


# ----------------------------------------------------------------- test 5 ----


def test_threshold_interpolation_is_log_linear_and_reports_a_curve_that_never_crosses():
    """5. Log-linear interpolation, and the chosen-figure rule around it.

    The chosen figure is max(analytic, simulated) once the two differ by more
    than 15%: the simulation may only ADD days, because a simulated size below
    the analytic one comes from a right-skewed replicate variance at short
    lengths and would plan on an anti-conservative test (lead ruling).
    """
    ns = [10, 20, 40]
    powers = [0.50, 0.70, 0.90]
    fraction = (0.80 - 0.70) / (0.90 - 0.70)
    expected = math.exp(math.log(20.0) + fraction * (math.log(40.0) - math.log(20.0)))

    assert stats.interpolate_threshold(ns, powers) == pytest.approx(expected)
    assert expected == pytest.approx(20.0 * math.sqrt(2.0))
    assert not stats.threshold_is_censored(ns, powers)

    never = [0.10, 0.30, 0.55]
    assert stats.interpolate_threshold(ns, never) is None
    assert not stats.threshold_is_censored(ns, never)

    censored = [0.85, 0.90, 0.95]
    assert stats.interpolate_threshold(ns, censored) == pytest.approx(10.0)
    assert stats.threshold_is_censored(ns, censored)
    kept, diff, flags = power._chosen(40, 10.0, True, "b")
    assert kept == 40  # a censored figure never overrides the analytic size
    assert diff == pytest.approx(-75.0)
    assert flags == ["sim_censored_below_grid_b"]

    # more days than the closed form asks for, by more than 15%: the simulation wins
    larger, diff_larger, flags_larger = power._chosen(40, 60.0, False, "a")
    assert larger == 60
    assert diff_larger == pytest.approx(50.0)
    assert flags_larger == ["sim_used_larger_a"]

    # fewer days, by more than 15%: recorded, ignored, analytic kept
    smaller, diff_smaller, flags_smaller = power._chosen(40, 20.0, False, "b")
    assert smaller == 40
    assert diff_smaller == pytest.approx(-50.0)
    assert flags_smaller == ["sim_smaller_ignored_b"]

    # inside the 15% band: analytic kept, unflagged, either way
    assert power._chosen(40, 42.0, False, "b") == (40, pytest.approx(5.0), [])
    assert power._chosen(40, 36.0, False, "b") == (40, pytest.approx(-10.0), [])


# ----------------------------------------------------------------- test 6 ----


def test_supplied_days_calendar_for_january_2023():
    """6. January 2023: weekdays minus the two CME full closures.

    NOTE ON THE BRIEF. The stage brief states "21 weekdays minus 2 closures =
    19". January 2023 in fact contains 22 weekdays (1 Jan 2023 was a Sunday, so
    the month holds five Mondays-to-Fridays runs of 5, 5, 5, 5 and then Mon 30 /
    Tue 31), which makes the answer 20, not 19. The two closures named in the
    brief are the ones this estimator removes: Mon 2 Jan (New Year's Day
    observed, 1 Jan being a Sunday) and Mon 16 Jan (Martin Luther King Day).
    The one-day discrepancy is in the brief's weekday count, not in the closure
    rule, and has been reported to the lead.
    """
    start, end = date(2023, 1, 1), date(2023, 1, 31)
    all_days = [start + timedelta(days=i) for i in range((end - start).days + 1)]
    assert len([d for d in all_days if d.weekday() < 5]) == 22

    open_dates = cal.weekday_open_dates(start, end)
    assert date(2023, 1, 2) not in open_dates  # New Year's Day, observed Monday
    assert date(2023, 1, 16) not in open_dates  # Martin Luther King Day
    assert len(open_dates) == 20


def test_holiday_observance_rules():
    """Sunday holidays move to Monday; Saturday ones close no weekday."""
    closures_2022 = cal.cme_full_closures(2022)
    assert date(2022, 1, 1).weekday() == 5  # Saturday New Year
    assert date(2022, 1, 3) not in closures_2022  # no weekday closes
    assert date(2022, 6, 20) in closures_2022  # Juneteenth (Sun 19) observed Monday
    assert date(2022, 4, 15) in closures_2022  # Good Friday
    assert date(2021, 6, 18) not in cal.cme_full_closures(2021)  # Juneteenth from 2022


# ----------------------------------------------------------------- test 7 ----


def test_family_h_projection_uses_the_coverage_map_proxy_rule():
    """7. H1: per-trade SD 200 and f = 0.225 give SD_day = 200*sqrt(f) and r = f."""
    projected = power.projected_member("H1 NR4 opening-range breakout", 200.0, 0.225)

    assert projected.sd_day == pytest.approx(200.0 * math.sqrt(0.225))
    assert projected.r == pytest.approx(0.225)
    assert projected.vif_boot == 1.0
    assert projected.lag1 == 0.0
    assert projected.kind == "projected"
    assert projected.klass == "C7"
    assert projected.daily is None

    # Per-trade SD proxies corrected with R-1: the 100/115 figures were read off
    # the half-scale trial table. Firing fractions are unchanged.
    declared = dict((name, (sd, f)) for name, sd, f in power.FAMILY_H)
    assert declared["H1 NR4 opening-range breakout"] == (200.0, 0.225)
    assert declared["H6 prior-close location follow-through"] == (230.0, 0.4)


# ------------------------------------------------------------ extra guards ----


def test_bootstrap_variance_floors_a_strongly_alternating_series():
    """A +/-1 alternating series has V_B below 0.2*gamma_0 and is floored."""
    alternating = np.array([1.0, -1.0] * 200)
    v_b, gamma0, hit_floor = stats.bootstrap_variance(alternating)

    assert bool(hit_floor)
    assert float(v_b) == pytest.approx(stats.VIF_FLOOR_FRACTION * float(gamma0))
    vif, floored = stats.variance_inflation(alternating)
    assert floored
    assert vif == pytest.approx(stats.VIF_FLOOR_FRACTION)


def test_normal_quantiles_match_the_published_values():
    """The module's z constants, recomputed here with NormalDist (no scipy)."""
    z_power, z_ucb, z_holm = stats.Z_POWER, stats.Z_UCB, stats.Z_HOLM
    assert z_power == pytest.approx(Z_POWER, abs=1e-15)
    assert z_ucb == pytest.approx(Z_UCB, abs=1e-15)
    assert z_holm == pytest.approx(Z_HOLM, abs=1e-15)
    assert z_power == pytest.approx(0.8416212335729143, abs=1e-12)
    assert z_ucb == pytest.approx(1.6448536269514722, abs=1e-12)
    assert z_holm == pytest.approx(3.1340460549238425, abs=1e-12)
    alpha_holm = stats.ALPHA_HOLM
    assert alpha_holm == pytest.approx(0.05 / 58)
    assert stats.HOLM_FAMILY_SIZE == 58
