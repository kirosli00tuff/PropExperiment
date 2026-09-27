"""Known-answer tests for the Stage E D4 power check (screening/stage_e_stats_power.py).

The generalized code must (1) agree with the D.1e Task 3 inference core function for function,
(2) reproduce the recorded D.1e figures in reports/stage_d1e_power.json for MES at MES's
epsilon (34 net ticks per micro per day) from the recorded D.1e member series, and (3) apply
the 15% switch, the "inconclusive by design" label and the named refusals exactly.
"""

from __future__ import annotations

import json
import math
from datetime import date, timedelta
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pytest

from screening import stage_e_stats as es
from screening import stage_e_stats_power as sp
from strategy.research import _d1e_power_stats as d1e

REPO = Path(__file__).resolve().parents[1]
D1E_POWER = REPO / "reports" / "stage_d1e_power.json"
D1E_TRIALS = REPO / "reports" / "stage_d1e_members_trials.json"
D1E_EVENTS = REPO / "reports" / "stage_d1e_members_events.json"

MES_EPS_TICKS = 34.0  # docs/NULL_CRITERIA.md 2.2: MES's epsilon, net ticks per micro per day
D1E_GRID = (10, 15, 20, 30, 50, 75, 100, 150, 200, 300, 500, 750, 1000, 1500, 2000, 3000)
D1E_SEED_BASE = 20260922
D1E_MARKET_COST_TICKS = 2.11
Z_HOLM_58 = NormalDist().inv_cdf(1.0 - 0.05 / 58)


def _ar1(n: int, phi: float, seed: int, scale: float = 10.0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    shocks = rng.standard_t(4, size=n) * scale
    out = np.empty(n)
    out[0] = shocks[0]
    for i in range(1, n):
        out[i] = phi * out[i - 1] + shocks[i]
    return out


def _legs(vehicle: str, dates: tuple[date, ...], usd: np.ndarray) -> es.DailySeries:
    daily = dict(zip(dates, usd, strict=True))
    return es.daily_series_from_leg_dollars("m", vehicle, daily, dates, len(dates))


def _window(n: int) -> tuple[date, ...]:
    start = date(2025, 4, 1)
    return tuple(start + timedelta(days=i) for i in range(n))


# ------------------------------------------------ the core agrees with D.1e's ----


@pytest.mark.parametrize("phi,seed", [(0.0, 1), (0.3, 2), (-0.4, 3), (0.8, 4)])
def test_variance_functions_equal_d1e(phi: float, seed: int) -> None:
    x = _ar1(400, phi, seed)
    np.testing.assert_array_equal(sp.sample_autocovariances(x), d1e.sample_autocovariances(x))
    assert sp.variance_inflation(x) == d1e.variance_inflation(x)
    assert sp.lag1_autocorrelation(x) == d1e.lag1_autocorrelation(x)


def test_analytic_sample_size_equals_d1e_and_the_closed_form() -> None:
    for sd, vif, eps in [(33.9, 0.89, 34.0), (120.0, 1.7, 5.0), (8.0, 1.0, 71.0)]:
        expected = math.ceil(((sp.Z_UCB + sp.Z_POWER) * sd * math.sqrt(vif) / eps) ** 2)
        assert sp.analytic_sample_size(sp.Z_UCB, sd, vif, eps) == expected
        assert sp.analytic_sample_size(sp.Z_UCB, sd, vif, eps) == d1e.analytic_sample_size(
            d1e.Z_UCB, sd, vif, eps
        )


def test_interpolation_and_censoring_equal_d1e() -> None:
    ns = [10, 20, 50, 100]
    for powers in ([0.1, 0.5, 0.79, 0.95], [0.85, 0.9, 0.95, 0.99], [0.1, 0.2, 0.3, 0.4]):
        assert sp.interpolate_threshold(ns, powers) == d1e.interpolate_threshold(ns, powers)
        assert sp.threshold_is_censored(ns, powers) == d1e.threshold_is_censored(ns, powers)


def test_simulated_curve_equals_d1e_simulate_powers() -> None:
    e = _ar1(250, 0.3, 7)
    e = e - e.mean()
    lengths = [6, 10, 30, 100, 300]
    ours, floored, degenerate = sp.simulate_power_curve(
        e, 12.0, lengths, seed=99, replications=300, z_detect=d1e.Z_HOLM
    )
    theirs, t_floored, t_degenerate = d1e.simulate_powers(e, 12.0, lengths, 99, 300)
    assert (floored, degenerate) == (t_floored, t_degenerate)
    for n in lengths:
        assert ours[n]["power_b"] == theirs[n]["power_b"]
        assert ours[n]["se_b"] == theirs[n]["se_b"]
        assert ours[n]["power_a"] == theirs[n]["power_a"]


# ------------------------------------------- D.1e figures reproduced for MES ----


def _d1e_series_in_order() -> list[tuple[str, np.ndarray]]:
    """D.1e's member order (trials, Tier A statistics, Tier B statistics): its seed index."""
    trials = json.loads(D1E_TRIALS.read_text(encoding="utf-8"))
    events = json.loads(D1E_EVENTS.read_text(encoding="utf-8"))
    out: list[tuple[str, np.ndarray]] = []
    for label, record in trials["members"].items():
        out.append((label, np.asarray(record["daily_net_ticks_per_micro"], dtype=float)))
    for key in ("statistics", "coverage_statistics"):
        for stat_id, record in events[key].items():
            side = float(record["recorded_direction"])
            sums = np.asarray(record["daily_sum_ticks"], dtype=float)
            counts = np.asarray(record["daily_count"], dtype=float)
            out.append((stat_id, side * sums - D1E_MARKET_COST_TICKS * counts))
    return out


@pytest.fixture(scope="module")
def d1e_rows() -> dict[str, dict]:
    payload = json.loads(D1E_POWER.read_text(encoding="utf-8"))
    return {row["id"]: row for row in payload["members"]}


@pytest.fixture(scope="module")
def d1e_series() -> list[tuple[str, np.ndarray]]:
    return _d1e_series_in_order()


def test_every_measured_d1e_member_analytic_figures_reproduced(d1e_rows, d1e_series) -> None:
    assert len(d1e_series) == 95
    for member_id, daily in d1e_series:
        row = d1e_rows[member_id]
        stats = sp.series_statistics(daily)
        assert stats.sd_day == pytest.approx(row["sd_day"], rel=1e-12)
        assert stats.vif_boot == pytest.approx(row["vif_boot"], rel=1e-12)
        n_b = sp.analytic_sample_size(sp.Z_UCB, stats.sd_day, stats.vif_boot, MES_EPS_TICKS)
        assert n_b == row["n_b_analytic"], member_id


def _pick(d1e_rows: dict[str, dict], flag: str, count: int) -> list[str]:
    return [mid for mid, row in d1e_rows.items() if flag in row["flags"]][:count]


def _assert_threshold_fields(figures, row, tag: str) -> None:
    member_id = row["id"]
    simulated = getattr(figures, f"n_{tag}_sim")
    if row[f"n_{tag}_sim"] is None:
        assert simulated is None
    else:
        assert simulated == pytest.approx(row[f"n_{tag}_sim"], rel=1e-12), member_id
    assert getattr(figures, f"n_{tag}_chosen") == row[f"chosen_{tag}"], member_id
    diff = getattr(figures, f"diff_{tag}_pct")
    if row[f"diff_{tag}_pct"] is None:
        assert diff is None
    else:
        assert diff == pytest.approx(row[f"diff_{tag}_pct"], rel=1e-12), member_id
    recorded = sorted(f for f in row["flags"] if f.endswith(f"_{tag}"))
    assert sorted(f for f in figures.flags if f.endswith(f"_{tag}")) == recorded, member_id


def test_d1e_simulated_days_reproduced_for_mes(d1e_rows, d1e_series) -> None:
    """Seed = 20260922 + D.1e's member index, D.1e's lengths (grid plus n_a and n_b), n_a at
    D.1e's own level 0.05 / 58: every curve point and every n_a / n_b figure bit-equal."""
    index = {mid: i for i, (mid, _) in enumerate(d1e_series)}
    series = dict(d1e_series)
    picks = (
        _pick(d1e_rows, "sim_used_larger_b", 3)
        + _pick(d1e_rows, "sim_smaller_ignored_b", 1)
        + _pick(d1e_rows, "sim_censored_below_grid_b", 1)
        + _pick(d1e_rows, "sim_used_larger_a", 2)
        + _pick(d1e_rows, "sim_smaller_ignored_a", 1)
        + _pick(d1e_rows, "sim_censored_below_grid_a", 1)
    )
    plain = [
        mid for mid, row in d1e_rows.items()
        if row["kind"] != "projected" and not any(f.endswith(("_a", "_b")) for f in row["flags"])
    ]
    chosen_ids = list(dict.fromkeys(picks + plain[:1]))
    assert len(chosen_ids) >= 8
    for member_id in chosen_ids:
        row = d1e_rows[member_id]
        n_a, n_b = row["n_a_analytic"], row["n_b_analytic"]
        lengths = sorted(n for n in set(D1E_GRID) | {max(n_a, 2), max(n_b, 2)} if n >= 2)
        assert [str(n) for n in lengths] == list(row["curve"].keys())
        # the Stage E default lengths are D.1e's rule: grid plus n_a plus n_b (OC-I)
        assert list(sp._default_lengths([n_a, n_b])) == lengths
        figures = sp.null_power_figures(
            series[member_id], MES_EPS_TICKS, seed=D1E_SEED_BASE + index[member_id],
            lengths=lengths, z_detect=Z_HOLM_58,
        )
        assert figures.n_b_analytic == n_b and figures.n_a_analytic == n_a
        for n in lengths:
            assert figures.curve_power_b(n) == row["curve"][str(n)]["power_b"], (member_id, n)
            assert figures.curve_power_a(n) == row["curve"][str(n)]["power_a"], (member_id, n)
        _assert_threshold_fields(figures, row, "b")
        _assert_threshold_fields(figures, row, "a")


def test_d1e_sim_used_larger_rows_exist_so_the_switch_is_exercised(d1e_rows) -> None:
    rows = [r for r in d1e_rows.values() if "sim_used_larger_b" in r["flags"]]
    assert len(rows) == 3
    for row in rows:
        assert row["chosen_b"] == math.ceil(row["n_b_sim"]) > row["n_b_analytic"]
        assert abs(row["diff_b_pct"]) > 15.0


# ------------------------------------------------------------ the 15% switch ----


@pytest.mark.parametrize(
    "analytic,simulated,censored,chosen,flags",
    [
        (100, 115.0, False, 100, ()),                         # exactly 15%: not more than 15%
        (100, 115.5, False, 116, ("sim_used_larger_b",)),     # larger by > 15%: simulation governs
        (100, 84.0, False, 100, ("sim_smaller_ignored_b",)),  # smaller by > 15%: analytic kept
        (100, 90.0, False, 100, ()),                          # within 15%: analytic
        (100, 300.0, True, 100, ("sim_censored_below_grid_b",)),
        (100, None, False, None, ("power_b_never_reaches_target",)),
    ],
)
def test_switch_rule(analytic, simulated, censored, chosen, flags) -> None:
    got, _diff, got_flags = sp.choose_null_days(analytic, simulated, censored)
    assert got == chosen
    assert got_flags == flags
    got_a, _diff_a, flags_a = sp.choose_null_days(analytic, simulated, censored, tag="a")
    assert got_a == chosen
    assert flags_a == tuple(f[:-1] + "a" if f.endswith("_b") else f.replace("_b_", "_a_")
                            for f in flags)


def test_switch_rule_rejects_an_unknown_tag() -> None:
    with pytest.raises(ValueError, match="tag"):
        sp.choose_null_days(100, 120.0, False, tag="c")


# ------------------------------------------------- the inconclusive label ----


def test_label_boundary_n_b_equal_to_supply_is_sufficient() -> None:
    assert sp.label_power(n_b_chosen=500, n_b_analytic=480, max_length=3000, supply_days=500) == (
        False, sp.LABEL_SUFFICIENT,
    )
    assert sp.label_power(n_b_chosen=501, n_b_analytic=480, max_length=3000, supply_days=500) == (
        True, sp.LABEL_INCONCLUSIVE,
    )


def test_label_when_the_simulation_never_reaches_80_percent() -> None:
    # analytic already above supply: inconclusive whatever the simulation says
    assert sp.label_power(None, 900, 3000, 800)[0] is True
    # analytic within supply, but the threshold lies beyond a grid that covers both supply and
    # 1.15 x analytic: the simulated figure governs and exceeds supply
    assert sp.label_power(None, 700, 3000, 800)[0] is True
    # grid too short to decide: refused by name
    with pytest.raises(sp.PowerCheckUndefined, match="cannot be decided"):
        sp.label_power(None, 2700, 3000, 2900)


def test_power_check_labels_a_noisy_member_inconclusive_and_a_quiet_one_sufficient() -> None:
    dates = _window(300)
    rng = np.random.default_rng(5)
    # MGC: eps 71 ticks per contract per day, q_c 1, tick $1.00 (frozen E.2a table)
    noisy_usd = rng.normal(0.0, 4000.0, size=300)
    quiet_usd = rng.normal(0.0, 60.0, size=300)
    noisy = es.daily_series_from_leg_dollars(
        "noisy", "MGC", dict(zip(dates, noisy_usd, strict=True)), dates, 300
    )
    quiet = es.daily_series_from_leg_dollars(
        "quiet", "MGC", dict(zip(dates, quiet_usd, strict=True)), dates, 300
    )
    loud = sp.power_check(noisy, "K5", ordinal=3, supply_days=1000)
    calm = sp.power_check(quiet, "K5", ordinal=4, supply_days=1000)
    assert loud.eps_ticks == 71 and loud.seed == sp.POWER_SEED_BASE + 3
    assert loud.n_b_analytic > 1000
    assert loud.inconclusive_by_design is True and loud.label == sp.LABEL_INCONCLUSIVE
    assert calm.n_b_chosen is not None and calm.n_b_chosen <= 1000
    assert calm.inconclusive_by_design is False and calm.label == sp.LABEL_SUFFICIENT
    expected = math.ceil(
        ((sp.Z_UCB + sp.Z_POWER) * calm.sd_day_ticks * math.sqrt(calm.vif_boot) / 71.0) ** 2
    )
    assert calm.n_b_analytic == expected


def test_power_check_is_deterministic_per_ordinal() -> None:
    dates = _window(120)
    usd = _ar1(120, 0.2, 11, scale=40.0)
    series = _legs("MCL", dates, usd)
    first = sp.power_check(series, "K4", ordinal=7, supply_days=900)
    again = sp.power_check(series, "K4", ordinal=7, supply_days=900)
    assert first == again


def test_power_check_units_follow_the_frozen_epsilon() -> None:
    # MCL: q_c 4, tick $1.00, eps 21 ticks per contract per day = $84.00 a day at q_c
    dates = _window(60)
    usd = _ar1(60, 0.0, 13, scale=100.0)
    series = _legs("MCL", dates, usd)
    check = sp.power_check(series, "K4", ordinal=0, supply_days=900)
    assert check.eps_ticks == 21
    assert check.eps_usd_per_day_at_q == pytest.approx(84.0)
    np.testing.assert_allclose(series.array(), usd / (4 * 1.0))
    assert check.sd_day_ticks == pytest.approx(float(np.std(usd / 4.0, ddof=1)))


# ------------------------------------------------------------ refusals ----


def test_zero_variance_series_is_refused_by_name() -> None:
    dates = _window(50)
    series = es.daily_series_from_trips("idle", "MGC", [], dates)
    with pytest.raises(sp.PowerCheckUndefined, match="zero variance"):
        sp.power_check(series, "K5", ordinal=0, supply_days=900)


@pytest.mark.parametrize("ordinal,supply", [(-1, 10), (0, -5), (True, 10), (0, 10.0)])
def test_bad_ordinal_or_supply_is_refused(ordinal, supply) -> None:
    dates = _window(30)
    usd = _ar1(30, 0.0, 17)
    series = _legs("MGC", dates, usd)
    with pytest.raises(ValueError):
        sp.power_check(series, "K5", ordinal=ordinal, supply_days=supply)


def test_non_finite_or_short_series_is_refused() -> None:
    with pytest.raises(sp.PowerCheckUndefined):
        sp.null_power_figures(np.array([1.0]), 10.0, seed=1)
    with pytest.raises(sp.PowerCheckUndefined):
        sp.null_power_figures(np.array([1.0, np.nan, 2.0]), 10.0, seed=1)
    with pytest.raises(ValueError):
        sp.null_power_figures(np.array([1.0, 2.0, 3.0]), 0.0, seed=1)


def test_analytic_n_b_above_the_grid_is_not_simulated_at_its_own_length() -> None:
    rng = np.random.default_rng(3)
    daily = rng.normal(0.0, 500.0, size=200)
    figures = sp.null_power_figures(daily, 2.0, seed=1, replications=50)
    assert figures.n_b_analytic > max(sp.POWER_GRID)
    assert max(figures.lengths) == max(sp.POWER_GRID)
    assert "n_b_analytic_above_grid" in figures.flags


# ------------------------------------------------------------ n_a (OC-I) ----


def test_cluster_member_counts_are_the_frozen_e1_recount() -> None:
    assert dict(sp.CLUSTER_MEMBER_COUNTS) == {
        "K1": 5, "K2": 8, "K3": 9, "K4": 8, "K5": 7, "K6": 7, "K7": 6, "K8": 3,
    }
    assert sum(sp.CLUSTER_MEMBER_COUNTS.values()) == 53  # D5: "Total: 53 members"
    with pytest.raises(TypeError):
        sp.CLUSTER_MEMBER_COUNTS["K1"] = 6  # type: ignore[index]


@pytest.mark.parametrize("cluster,m_c", [("K1", 5), ("K3", 9), ("K8", 3)])
def test_detection_level_is_the_most_stringent_step_over_nine_families(cluster, m_c) -> None:
    alpha = sp.detection_alpha(cluster)
    assert alpha == 0.05 / (9 * m_c)
    assert sp.detection_z(alpha) == NormalDist().inv_cdf(1.0 - 0.05 / (9 * m_c))


def test_unknown_cluster_is_refused() -> None:
    dates = _window(30)
    series = _legs("MGC", dates, _ar1(30, 0.0, 19))
    with pytest.raises(ValueError, match="unknown cluster"):
        sp.power_check(series, "K9", ordinal=0, supply_days=900)


def test_power_check_computes_n_a_descriptively_and_labels_on_n_b_alone() -> None:
    # MGC, eps 71: sd ~ 90 ticks gives n_b ~ 10 and n_a (K2: alpha 0.05 / 72) ~ 29
    dates = _window(300)
    usd = np.random.default_rng(23).normal(0.0, 90.0, size=300)
    series = _legs("MGC", dates, usd)
    check = sp.power_check(series, "K2", ordinal=2, supply_days=20)
    z_a = NormalDist().inv_cdf(1.0 - 0.05 / 72)
    assert check.cluster_members == 8 and check.alpha_a == 0.05 / 72 and check.z_a == z_a
    assert check.n_a_analytic == math.ceil(
        ((z_a + sp.Z_POWER) * check.sd_day_ticks * math.sqrt(check.vif_boot) / 71.0) ** 2
    )
    assert check.n_a_analytic in check.lengths and check.n_b_analytic in check.lengths
    assert check.n_a_chosen is not None and check.n_a_chosen > 20  # n_a exceeds supply ...
    assert check.n_b_chosen is not None and check.n_b_chosen <= 20
    assert check.inconclusive_by_design is False  # ... but the label reads n_b alone
    point = check.curve[0]
    assert point.power_a is not None and point.se_a is not None

