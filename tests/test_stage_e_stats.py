"""Known-answer tests for screening/stage_e_stats.py: units, the D5 screen, tiers and Holm.

Every expectation is hand-computable or taken from a frozen table or a textbook example.
"""

from __future__ import annotations

import json
import math
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pytest

from funnel.multiple_comparisons import harvey_liu_zhu_verdict
from screening import stage_e_stats as es
from strategy.research import _d1f_decisions as d1f

REPO = Path(__file__).resolve().parents[1]
D1E_TRIALS = REPO / "reports" / "stage_d1e_members_trials.json"


def _window(n: int, start: date = date(2025, 4, 1)) -> tuple[date, ...]:
    return tuple(start + timedelta(days=i) for i in range(n))


# ---------------------------------------------------------------- units ----


def test_frozen_epsilon_reads_the_e2a_table() -> None:
    mgc = es.frozen_epsilon("MGC")
    assert (mgc.eps_ticks, mgc.q_c, mgc.tick_value_usd) == (71, 1, 1.0)
    assert mgc.eps_usd_per_day_at_q == pytest.approx(71.0)
    mcl = es.frozen_epsilon("MCL")
    # D3's worked example: floor(85 / (4 x $1.00)) = 21 ticks per contract per day
    assert (mcl.eps_ticks, mcl.q_c, mcl.tick_value_usd) == (21, 4, 1.0)
    assert mcl.eps_ticks == math.floor(85.0 / (4 * 1.0))
    assert mcl.eps_usd_per_day_at_q == pytest.approx(84.0)
    mnq = es.frozen_epsilon("MNQ")
    assert mnq.eps_usd_per_day_at_q == pytest.approx(170 * 1 * 0.5)
    assert len(mgc.source_sha256) == 64


def test_frozen_epsilon_refuses_an_unknown_vehicle() -> None:
    with pytest.raises(KeyError, match="MES"):
        es.frozen_epsilon("MES")


def test_ticks_to_usd_per_day() -> None:
    assert es.ticks_to_usd_per_day(21.0, 4, 1.0) == pytest.approx(84.0)
    assert es.ticks_to_usd_per_day(2.0, 1, 31.25) == pytest.approx(62.5)
    with pytest.raises(ValueError):
        es.ticks_to_usd_per_day(1.0, 0, 1.0)


def test_trips_become_ticks_per_contract_with_zeros_on_no_trade_days() -> None:
    dates = _window(5)
    trips = [
        es.Trip(dates[1], net_usd=8.0, contracts=4),    # MCL, $1 tick: 8 / (4 x 1) = 2 ticks
        es.Trip(dates[1], net_usd=-3.0, contracts=1),   # same date: -3 ticks, summed
        es.Trip(dates[3], net_usd=10.0, contracts=2),   # 5 ticks
    ]
    series = es.daily_series_from_trips("m", "MCL", trips, dates)
    assert series.values == (0.0, -1.0, 0.0, 5.0, 0.0)
    assert series.dates == dates
    assert series.n_trips == 3
    assert series.vehicle == "MCL"


def test_trip_conversion_reproduces_d1e_per_micro_series_for_mes() -> None:
    """D.1e's daily_net_ticks_per_micro = sum over the day's trips of pnl / ($1.25 x micros)."""
    trials = json.loads(D1E_TRIALS.read_text(encoding="utf-8"))["members"]
    for label in list(trials)[:6]:
        record = trials[label]
        n_days = len(record["daily_net_ticks_per_micro"])
        dates = _window(n_days, date(2021, 1, 1))
        trips, k = [], 0
        for day, count in zip(dates, record["daily_n_trips"], strict=True):
            for _ in range(int(count)):
                pnl, micros = record["trip_pnls_usd"][k], int(record["trip_micros"][k])
                trips.append(es.Trip(day, pnl, micros))
                k += 1
        assert k == len(record["trip_pnls_usd"])
        values = es._aggregate_trips(trips, dates, tick_value_usd=1.25)
        np.testing.assert_allclose(values, record["daily_net_ticks_per_micro"], rtol=0, atol=1e-9)


def test_leg_dollars_use_the_primary_legs_q_and_tick() -> None:
    dates = _window(3)
    series = es.daily_series_from_leg_dollars(
        "k8", "MCL", {dates[0]: 80.0, dates[2]: -8.0}, dates, n_trips=2
    )
    assert series.values == (20.0, 0.0, -2.0)  # $ / (q_c 4 x $1.00)


@pytest.mark.parametrize(
    "trips_dates,window,message",
    [
        (["2025-05-01"], ["2025-04-01", "2025-04-02"], "outside"),
        ([], ["2025-04-02", "2025-04-01"], "ascending"),
        ([], ["2025-04-01", "2025-04-01"], "ascending"),
        ([], [], "empty"),
    ],
)
def test_series_construction_refusals(trips_dates, window, message) -> None:
    trips = [es.Trip(date.fromisoformat(d), 1.0, 1) for d in trips_dates]
    with pytest.raises(ValueError, match=message):
        es.daily_series_from_trips("m", "MGC", trips, [date.fromisoformat(d) for d in window])


def test_trip_with_bad_contracts_or_value_is_refused() -> None:
    dates = _window(2)
    with pytest.raises(ValueError, match="contracts"):
        es.daily_series_from_trips("m", "MGC", [es.Trip(dates[0], 1.0, 0)], dates)
    with pytest.raises(ValueError, match="finite"):
        es.daily_series_from_trips("m", "MGC", [es.Trip(dates[0], float("nan"), 1)], dates)
    with pytest.raises(ValueError, match="outside"):
        es.daily_series_from_leg_dollars("m", "MGC", {date(2020, 1, 1): 1.0}, dates, 1)
    with pytest.raises(ValueError, match="n_trips"):
        es.daily_series_from_leg_dollars("m", "MGC", {}, dates, -1)


# --------------------------------------------------------------- screen ----


def _series(values: list[float], vehicle: str = "MGC", member_id: str = "m") -> es.DailySeries:
    dates = _window(len(values))
    tick = es.frozen_epsilon(vehicle).tick_value_usd
    q = es.frozen_epsilon(vehicle).q_c
    usd = {d: v * q * tick for d, v in zip(dates, values, strict=True) if v != 0.0}
    return es.daily_series_from_leg_dollars(member_id, vehicle, usd, dates, n_trips=len(usd))


def test_screen_t_exactly_one_passes() -> None:
    # mean 1, population sd 2, n 4: t = 1 / (2 / sqrt(4)) = 1.0 exactly
    result = es.screen(_series([3.0, -1.0, 3.0, -1.0]))
    assert result.mean_ticks == 1.0
    assert result.sd_pop_ticks == 2.0
    assert result.t_daily == 1.0
    assert result.passes is True


def test_screen_t_just_below_one_fails() -> None:
    result = es.screen(_series([3.0, -1.0, 3.0, -1.0 - 1e-9]))
    assert result.mean_ticks > 0.0
    assert result.t_daily < 1.0
    assert result.passes is False


def test_screen_t_is_the_programs_pinned_daily_t() -> None:
    values = [5.0, -2.0, 0.0, 7.5, -1.0, 0.0, 3.0]
    result = es.screen(_series(values))
    mean = sum(values) / len(values)
    sd = math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))
    assert result.t_daily == pytest.approx(harvey_liu_zhu_verdict(mean, sd, 7)["t_stat"], rel=1e-15)
    assert result.t_daily == pytest.approx(mean / (sd / math.sqrt(7)), rel=1e-12)


def test_screen_counts_zeros_on_no_trade_days() -> None:
    # the same two trades over 2 window days pass (t = inf is not allowed: use unequal wins)
    busy = es.screen(_series([4.0, 2.0]))
    # ... and over 10 window days the mean is diluted by the eight zero days
    sparse = es.screen(_series([4.0, 2.0] + [0.0] * 8))
    assert busy.mean_ticks == 3.0
    assert sparse.mean_ticks == pytest.approx(0.6)
    assert sparse.n_days == 10
    sd = math.sqrt((3.4**2 + 1.4**2 + 8 * 0.6**2) / 10)
    assert sparse.t_daily == pytest.approx(0.6 / (sd / math.sqrt(10)))


def test_screen_negative_mean_fails_and_idle_member_fails() -> None:
    assert es.screen(_series([-3.0, 1.0, -2.0])).passes is False
    idle = es.screen(_series([0.0, 0.0, 0.0]))
    assert idle.passes is False and idle.t_daily is None and idle.n_trips == 0


def test_screen_refuses_constant_positive_series_and_one_day() -> None:
    with pytest.raises(es.ScreenUndefined, match="sd = 0"):
        es.screen(_series([2.0, 2.0, 2.0]))
    with pytest.raises(es.ScreenUndefined, match="two"):
        es.screen(_series([2.0]))


def test_screen_is_unit_free_per_micro_or_per_contract() -> None:
    values = [5.0, -2.0, 0.0, 7.5, -1.0]
    a = es.screen(_series(values, "MGC"))
    b = es.screen(_series([v * 3.0 for v in values], "MGC"))
    assert a.passes == b.passes
    assert a.t_daily == pytest.approx(b.t_daily, rel=1e-12)


# ---------------------------------------------------------------- tiers ----


def _screened(member_id: str, values: list[float]) -> es.ScreenResult:
    return es.screen(_series(values, member_id=member_id))


PASS = [3.0, -1.0, 3.0, 1.0]
FAIL = [-3.0, 1.0, -2.0, 0.5]


def test_tiers_a_b_and_excluded_per_lead_ruling_oc_h() -> None:
    tiers = es.assign_tiers(
        "K5",
        [
            es.TierInput("a1", _screened("a1", PASS)),
            es.TierInput("b1", _screened("b1", FAIL)),
            es.TierInput("cov", None, ("coverage_below_0.95",)),
            es.TierInput("hold", _screened("hold", PASS), ("mean_holding_below_10min",)),
            es.TierInput("rate", _screened("rate", FAIL), ("entries_above_20_per_day",)),
            es.TierInput("quick", _screened("quick", PASS), ("hold_below_2min",)),
        ],
    )
    assert tiers.tier_a == ("a1",)
    assert tiers.tier_b == ("b1",)
    assert tiers.excluded == ("cov", "hold", "rate", "quick")
    assert tiers.has_tier_a is True
    by_id = {m.member_id: m for m in tiers.members}
    assert by_id["cov"].screen is None and by_id["cov"].tier == "excluded"
    assert by_id["hold"].screen is not None and by_id["hold"].screen.passes is True
    assert by_id["hold"].tier == "excluded"
    assert by_id["hold"].labels == ("mean_holding_below_10min",)


def test_cluster_with_only_excluded_passers_has_no_tier_a() -> None:
    tiers = es.assign_tiers(
        "K7",
        [
            es.TierInput("x", _screened("x", PASS), ("mean_holding_below_10min",)),
            es.TierInput("y", _screened("y", FAIL)),
        ],
    )
    assert tiers.tier_a == () and tiers.has_tier_a is False
    assert tiers.tier_b == ("y",)


@pytest.mark.parametrize(
    "members,message",
    [
        ([es.TierInput("a", None)], "unlabelled"),
        ([es.TierInput("a", None, ("mean_holding_below_10min",))], "keeps its screen"),
        ([es.TierInput("a", _screened("a", PASS), ("coverage_below_0.95",))], "not screened"),
        ([es.TierInput("a", None, ("made_up",))], "unknown"),
        ([es.TierInput("a", _screened("b", PASS))], "screen belongs"),
        ([es.TierInput("a", _screened("a", PASS)), es.TierInput("a", _screened("a", FAIL))],
         "twice"),
        ([], "no members"),
    ],
)
def test_tier_refusals(members, message) -> None:
    with pytest.raises(ValueError, match=message):
        es.assign_tiers("K1", members)


def test_k_counts_clusters_with_a_non_empty_tier_a() -> None:
    with_a = es.assign_tiers("K1", [es.TierInput("a", _screened("a", PASS))])
    without = es.assign_tiers("K2", [es.TierInput("b", _screened("b", FAIL))])
    also = es.assign_tiers("K3", [es.TierInput("c", _screened("c", PASS))])
    assert es.k_from_tiers([with_a, without, also], route_tested=False) == 2
    with pytest.raises(ValueError, match="twice"):
        es.k_from_tiers([with_a, with_a], route_tested=False)
    with pytest.raises(ValueError, match="K = 0"):
        es.k_from_tiers([without], route_tested=False)


def _cluster(name: str, passes: bool) -> es.ClusterTiers:
    member = f"{name}-m"
    screened = _screened(member, PASS if passes else FAIL)
    return es.assign_tiers(name, [es.TierInput(member, screened)])


def test_k_adds_one_for_a_tested_route_rule_v6() -> None:
    """V6 (audit ML-A14, review F-4): the route is one more family once it has a tested rule."""
    tiers = [_cluster("K1", True), _cluster("K2", False), _cluster("K3", True)]
    k = es.k_from_tiers(tiers, route_tested=True)
    assert k == 3
    # every family then tests at 0.05 / (K_clusters + 1) = 0.05 / 3, by hand 0.0166666...
    assert es.holm_alpha_k(k) == pytest.approx(0.016666666666666666, rel=1e-15)
    # the route alone is a family: K = 1
    assert es.k_from_tiers([_cluster("K2", False)], route_tested=True) == 1


def test_k_reaches_nine_with_eight_clusters_and_the_route() -> None:
    tiers = [_cluster(f"K{i}", True) for i in range(1, 9)]
    assert es.k_from_tiers(tiers, route_tested=False) == 8
    k = es.k_from_tiers(tiers, route_tested=True)
    assert k == 9 == es.MAX_FAMILIES
    assert es.holm_alpha_k(9) == pytest.approx(0.005555555555555556, rel=1e-15)
    result = es.holm_tier_a({"r1": 0.005, "r2": 0.02}, k_clusters=9)
    assert result.alpha_k == 0.05 / 9
    assert result.rows[0].threshold == pytest.approx(0.05 / 9 / 2)
    assert result.rejected == ()  # 0.005 > 0.00278


def test_k_route_tested_is_a_required_bool_keyword() -> None:
    tiers = [_cluster("K1", True)]
    with pytest.raises(TypeError):
        es.k_from_tiers(tiers)  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        es.k_from_tiers(tiers, True)  # type: ignore[misc]
    with pytest.raises(ValueError, match="route_tested"):
        es.k_from_tiers(tiers, route_tested=1)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="at most 8"):
        es.k_from_tiers([_cluster(f"X{i}", True) for i in range(9)], route_tested=False)


# ----------------------------------------------------------------- Holm ----


def test_holm_textbook_example() -> None:
    """Holm (1979) as taught (e.g. Wikipedia, Holm-Bonferroni method): p = .01, .04, .03, .005
    at alpha 0.05 rejects H4 (.005 <= .0125) and H1 (.01 <= .0167), then stops at H3
    (.03 > .025); H2 is not rejected."""
    result = es.holm_tier_a({"H1": 0.01, "H2": 0.04, "H3": 0.03, "H4": 0.005}, k_clusters=1)
    assert result.alpha_k == 0.05 and result.m == 4
    assert [r.member_id for r in result.rows] == ["H4", "H1", "H3", "H2"]
    assert [r.threshold for r in result.rows] == pytest.approx([0.0125, 0.05 / 3, 0.025, 0.05])
    assert result.rejected == ("H4", "H1")


def test_holm_at_alpha_k_splits_alpha_over_clusters() -> None:
    result = es.holm_tier_a({"H1": 0.01, "H2": 0.04, "H3": 0.03, "H4": 0.005}, k_clusters=2)
    assert result.alpha_k == 0.025
    assert result.rows[0].threshold == pytest.approx(0.00625)
    assert result.rejected == ("H4",)
    assert es.holm_alpha_k(8) == 0.05 / 8
    assert es.holm_alpha_k(9) == 0.05 / 9


def test_holm_step_down_stops_at_the_first_failure() -> None:
    # the third p passes its own threshold but Holm stops at the second
    result = es.holm_tier_a({"a": 0.001, "b": 0.03, "c": 0.04}, k_clusters=1)
    assert [r.reject for r in result.rows] == [True, False, False]


def test_holm_matches_d1f_holm_on_random_families() -> None:
    rng = np.random.default_rng(20260926)
    for k in range(1, 10):
        p = {f"m{i}": float(v) for i, v in enumerate(rng.uniform(0, 0.02, size=12))}
        ours = es.holm_tier_a(p, k_clusters=k)
        theirs = d1f.holm(p, alpha=0.05 / k)
        assert {r.member_id: r.reject for r in ours.rows} == {
            key: row["reject"] for key, row in theirs.items()
        }


@pytest.mark.parametrize("k", [0, 10, -1, 1.0, True, "2"])
def test_holm_k_is_validated(k) -> None:
    with pytest.raises(ValueError, match="K"):
        es.holm_alpha_k(k)


@pytest.mark.parametrize("p", [{}, {"a": -0.1}, {"a": 1.5}, {"a": float("nan")}])
def test_holm_p_values_are_validated(p) -> None:
    with pytest.raises(ValueError):
        es.holm_tier_a(p, k_clusters=1)
