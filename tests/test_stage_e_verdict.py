"""Known-answer and equality tests for screening/stage_e_verdict.py (Stage E.5, harness v5).

(1) The restated D.1f functions equal strategy/research/_d1f_decisions.py and _d1b_accounting.py
function for function (lead ruling L-E5-4); (2) known answers for every item of
reports/stage_e5_harness_plan.md 3b: estimates, the null branches, Holm at K = 9, the DSR variance
switch (V14 c), t, PBO with the switch (L-E5-3) and unequal window dates, the wording, the null
statement and the resolution table; (3) every refusal; (4) the CLI (preflight first, written once).
Fixtures are confirmation records in the runner's shape (window "confirmation", screen and power
null, an s_x map; screening/stage_e_runner.py).
"""

from __future__ import annotations

import ast
import json
import math
import statistics
from datetime import date, timedelta
from pathlib import Path
from statistics import NormalDist
from typing import Any

import numpy as np
import pytest

from data import stage_e_bars
from funnel.multiple_comparisons import (
    deflated_sharpe_ratio,
    probability_of_backtest_overfitting,
)
from screening import harness_freeze
from screening import stage_e_runner as runner
from screening import stage_e_verdict as V
from screening.stage_e_stats import holm_tier_a
from screening.stage_e_stats_units import frozen_epsilon
from strategy.research import _d1b_accounting as d1b
from strategy.research import _d1f_decisions as d1f

REPO = Path(__file__).resolve().parents[1]
HARNESS = "ab" * 32
FREEZE = "cd" * 32
CLUSTER = "K4"
START = date(2019, 5, 6)
B_FAST = 400  # resamples for tests that do not depend on B


# ------------------------------------------------------------------ fixtures ----
def weekdays(n: int, start: date = START) -> list[date]:
    out, day = [], start
    while len(out) < n:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


def alternating(mean: float, n: int, amplitude: float = 1.0) -> np.ndarray:
    return mean + amplitude * np.array([(-1.0) ** i for i in range(n)])


def list_trial(ordinal: int, member: str, *, vehicle: str = "NG", tier: str = "A",
               run: bool | None = None, labels: tuple[str, ...] = ()) -> dict:
    eps = frozen_epsilon(vehicle)
    return {"ordinal": ordinal, "member": member, "vehicle": vehicle, "q_c": eps.q_c,
            "eps_ticks": eps.eps_ticks, "eps_usd_per_day_at_q": eps.eps_usd_per_day_at_q,
            "tier": tier, "run": (tier != "excluded") if run is None else run,
            "labels": list(labels), "bootstrap_seed": V.BOOTSTRAP_SEED_BASE + ordinal,
            "power": None}


def conf_list(trials: list[dict], **over: Any) -> dict:
    payload = {"schema": V.LIST_SCHEMA, "cluster": CLUSTER, "harness_sha256": HARNESS,
               "cluster_freeze_sha256": FREEZE, "k_holm": 9, "program_n": 150,
               "bootstrap": {"seed_base": 20260923, "resamples": 10000, "mean_block": 5.0,
                             "ucb_quantile": 0.95},
               "start_dates": {"NG": START.isoformat(), "MCL": "2021-06-01",
                               "MGC": START.isoformat()},
               "trials": trials}
    payload.update(over)
    return payload


def record(trial: dict, values: np.ndarray | list[float], n_trips: int, *,
           dates: list[date] | None = None, status: str = "run", **over: Any) -> dict:
    """A confirmation member record in the runner's shape (stage_e_runner.screen_member)."""
    vehicle = trial["vehicle"]
    values = [float(v) for v in values]
    s_x = date.fromisoformat(conf_list([])["start_dates"][vehicle])
    dates = dates or weekdays(len(values), start=s_x)  # the window starts at the vehicle's S_X
    rec: dict[str, Any] = {
        "schema": "stage_e_member_record/1", "cluster": CLUSTER, "member": trial["member"],
        "ordinal": trial["ordinal"], "window": "confirmation",
        "legs": [{"root": vehicle, "traded": True}], "primary_vehicle": vehicle,
        "harness_sha256": HARNESS, "cluster_freeze_sha256": FREEZE,
        "frozen_tables": {}, "release_calendar_sha256": "ef" * 32, "bars": {},
        "window_dates": {"n": len(dates), "first": dates[0].isoformat(),
                         "last": dates[-1].isoformat(), "excluded": {}},
        "coverage": {}, "created_utc": "2026-09-27T20:00:00+00:00",
        "start_rule": {}, "s_x": {vehicle: conf_list([])["start_dates"][vehicle]},
        "status": status, "labels": [], "screen": None, "power": None,
        "series": {"unit": "net ticks per contract per day", "vehicle": vehicle,
                   "dates": [d.isoformat() for d in dates], "values": values,
                   "n_trips": n_trips},
        "daily_net_usd": values, "trade_rate": {"n_trips": n_trips}}
    if status != "run":
        rec["series"] = None
    rec.update(over)
    return rec


def run_verdict(trials: list[dict], records: dict[str, dict], b: int = B_FAST,
                **list_over: Any) -> dict:
    return V.evaluate(conf_list(trials, **list_over), records, n_resamples=b)


def by_member(verdict: dict) -> dict[str, dict]:
    return {row["member"]: row for row in verdict["trials"]}


# ============================================== (1) equality with D.1f ====
@pytest.mark.parametrize("seed_offset", [0, 3, 11])
def test_bootstrap_means_and_summary_equal_d1f(seed_offset: int) -> None:
    rng = np.random.default_rng(7 + seed_offset)
    daily = rng.standard_t(4, size=90) * 3.0 + 0.4
    seed = V.BOOTSTRAP_SEED_BASE + seed_offset
    ours = V.resampled_means(daily, 500, seed)
    theirs = d1f.resampled_means(daily, 500, seed, 5.0)
    assert np.array_equal(ours, theirs)
    mine, d1f_boot = V.summarize_means(daily, ours), d1f.summarize_means(daily, theirs)
    assert (mine.n_days, mine.theta_hat, mine.ucb95, mine.se_boot, mine.p_upper,
            mine.p_lower) == (d1f_boot.n_days, d1f_boot.theta_hat, d1f_boot.ucb95,
                              d1f_boot.se_boot, d1f_boot.p_upper, d1f_boot.p_lower)


def test_full_size_bootstrap_equals_d1f_at_10000_resamples() -> None:
    daily = alternating(0.3, 40, 2.0)
    assert np.array_equal(V.resampled_means(daily, 10_000, 20260923 + 5),
                          d1f.resampled_means(daily, 10_000, 20260923 + 5))


@pytest.mark.parametrize(("se", "eps"), [(0.0, 8.0), (1.0, 8.0), (3.2, 8.0), (10.0, 16.45),
                                         (7.5, 21.0), (1e-9, 71.0)])
def test_null_power_equals_d1f(se: float, eps: float) -> None:
    assert V.null_power(se, eps) == d1f.null_power(se, eps)


@pytest.mark.parametrize("xs", [[1.0, 2.0, 4.0, -3.0, 0.5], [2.0] * 6, [0.0, 0.0, 1.0],
                                list(np.random.default_rng(3).normal(0, 2, 64))])
def test_moments_and_blocks_equal_d1b(xs: list[float]) -> None:
    assert V.moments(xs) == d1b._moments([float(x) for x in xs])
    assert V.blocks(xs) == d1b._blocks(xs)


def test_dsr_t_and_the_dsr_table_equal_d1f() -> None:
    rng = np.random.default_rng(5)
    series = {f"m{i}": list(rng.normal(0.3 * i, 1.0 + i, 120)) for i in range(4)}
    series["flat"] = [1.0] * 120
    moms = {k: V.moments(v) for k, v in series.items()}
    for key, mom in moms.items():
        assert V.dsr(mom, 150, 0.02) == d1f._dsr(mom, 150, 0.02), key
        assert V.t_stat(mom) == d1f._t_stat(mom), key
    members = list(series)
    assert V.dsr_table(moms, members[:3], 150, members) == d1f.dsr_table(
        moms, members[:3], 150, members)


def test_pbo_and_alignment_equal_d1f() -> None:
    rng = np.random.default_rng(9)
    window = weekdays(100)
    own = {"a": window[::2], "b": window[5:], "c": window}
    vals = {k: rng.normal(0.1, 1.0, len(d)) for k, d in own.items()}
    aligned = {}
    for k, dates in own.items():
        member = d1f.Member(k, "A", "trial", "C1", tuple(dates), vals[k],
                            np.ones(len(dates)), composite="pass")
        aligned[k] = V.aligned_series(dates, vals[k], window)
        assert np.array_equal(aligned[k], d1f.aligned_series(member, window))
    assert V.pbo(aligned) == d1f.pbo(aligned)


@pytest.mark.parametrize("pvals", [(0.001,), (0.001, 0.002, 0.004), (0.001, 0.003, 0.004),
                                   (0.2, 0.0001, 0.01, 0.004)])
def test_holm_at_k9_equals_d1f_holm_at_the_same_alpha(pvals: tuple[float, ...]) -> None:
    p = {f"m{i}": v for i, v in enumerate(pvals)}
    ours = holm_tier_a(p, V.HOLM_K)
    theirs = d1f.holm(p, alpha=0.05 / 9)
    assert {r.member_id: r.reject for r in ours.rows} == {k: v["reject"]
                                                         for k, v in theirs.items()}


def test_constants_are_d1f_s_but_the_seed_base_is_stage_e_s() -> None:
    assert (V.BOOTSTRAP_RESAMPLES, V.MEAN_BLOCK_DAYS, V.UCB_QUANTILE, V.NULL_Z,
            V.NULL_POWER_MIN, V.INACTIVITY_MIN, V.DSR_MIN, V.T_MIN, V.PBO_MAX,
            V.N_PBO_BLOCKS) == (d1f.BOOTSTRAP_RESAMPLES, d1f.MEAN_BLOCK_DAYS,
                                d1f.UCB_QUANTILE, d1f.NULL_Z, d1f.NULL_POWER_MIN,
                                d1f.INACTIVITY_MIN, d1f.DSR_MIN, d1f.T_MIN, d1f.PBO_MAX,
                                d1f.N_PBO_BLOCKS)
    assert (V.BOOTSTRAP_SEED_BASE, d1f.BOOTSTRAP_SEED) == (20260923, 20260921)
    assert (V.HOLM_K, V.T_MIN) == (9, 3.0)
    assert V.LABEL_INACTIVITY == d1f.LABEL_INACTIVITY
    assert V.LABEL_INCONCLUSIVE_BY_DESIGN == "inconclusive by design"


def test_the_module_imports_nothing_from_strategy() -> None:
    tree = ast.parse((REPO / "screening" / "stage_e_verdict.py").read_text(encoding="utf-8"))
    names = [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
    names += [n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
    assert not [n for n in names if n.startswith("strategy")]


def test_record_names_schema_and_labels_match_the_runner() -> None:
    assert V.RECORD_SCHEMA == runner.RECORD_SCHEMA
    source = (REPO / "screening" / "stage_e_runner.py").read_text(encoding="utf-8")
    assert f'series={{"unit": "{V.SERIES_UNIT}"' in source  # the runner's literal, verbatim
    assert V.CONFIRMATION_LAST == stage_e_bars.CONFIRMATION_LAST_TRADE_DATE
    assert V.CONFIRMATION_WINDOW == runner.CONFIRMATION_WINDOW
    assert set(V.RUNNER_LABELS) == {runner.LABEL_COVERAGE, runner.LABEL_MEAN_HOLD,
                                    runner.LABEL_ENTRIES, runner.LABEL_MIN_HOLD}
    for member in ("K4-ngpre-01 NG", "K5-pmfix-02 MGC/SIL", "odd name!"):
        name = f"{CLUSTER}_{member}_{runner.CONFIRMATION_WINDOW}"
        assert V.record_name(CLUSTER, member) == f"{runner._safe(name)}.json"


# ================================================= (2) known answers ====
def test_summary_known_answer_on_a_given_means_array() -> None:
    daily = np.array([40.0, 60.0])  # theta_hat = 50
    means = np.arange(1.0, 101.0)
    boot = V.summarize_means(daily, means)
    assert boot.theta_hat == 50.0 and boot.ucb95 == pytest.approx(95.05)
    assert boot.se_boot == pytest.approx(math.sqrt((100**2 - 1) / 12))
    assert boot.p_upper == pytest.approx(2 / 101)  # only 100 - 50 >= 50


def test_null_power_known_answers() -> None:
    assert V.null_power(10.0, 16.45) == pytest.approx(0.5)
    z80 = NormalDist().inv_cdf(0.80)
    assert V.null_power(10.0, 10.0 * (1.645 + z80)) == pytest.approx(0.80)
    assert V.null_power(0.0, 8.0) == 0.0


def test_constant_series_has_se_zero_and_is_inconclusive() -> None:
    fig = V.trial_figures(V.Series(tuple(weekdays(50)), np.full(50, 2.5), 40), 8.0, 1, B_FAST)
    assert (fig["theta_hat"], fig["ucb95"], fig["se_boot"]) == (2.5, 2.5, 0.0)
    assert fig["p_upper"] == pytest.approx(1 / (B_FAST + 1))
    assert fig["status"] == "inconclusive" and fig["reasons"] == ["SE_boot = 0",
                                                                  "null power < 0.80"]


def test_zero_trips_is_inconclusive_not_null() -> None:
    fig = V.trial_figures(V.Series(tuple(weekdays(60)), np.zeros(60), 0), 8.0, 1, B_FAST)
    assert fig["status"] == "inconclusive"
    assert fig["reasons"][:2] == ["zero trips", "SE_boot = 0"]
    assert fig["theta_per_trade"] is None and fig["ucb95_per_trade"] is None
    assert fig["p_upper"] == 1.0


@pytest.mark.parametrize(("n_trips", "status"), [(40, "null"), (30, "null"),
                                                 (29, "null by inactivity")])
def test_null_and_null_by_inactivity(n_trips: int, status: str) -> None:
    values = alternating(0.0, 200)
    fig = V.trial_figures(V.Series(tuple(weekdays(200)), values, n_trips), 8.0, 20260923, B_FAST)
    assert fig["ucb_below_eps"] and fig["power_ok"] and fig["status"] == status
    assert fig["theta_hat"] == 0.0 and fig["trips_per_day"] == n_trips / 200
    assert fig["ucb95_per_trade"] == pytest.approx(fig["ucb95"] / (n_trips / 200))


def test_ucb_at_or_above_eps_is_inconclusive() -> None:
    fig = V.trial_figures(V.Series(tuple(weekdays(100)), alternating(10.0, 100), 80), 8.0, 1,
                          B_FAST)
    assert fig["ucb95"] >= 8.0 and fig["power_ok"]
    assert fig["status"] == "inconclusive" and fig["reasons"] == ["UCB95 >= eps_X"]
    assert fig["theta_per_trade"] == pytest.approx(10.0 / 0.8)


def test_low_power_alone_is_inconclusive() -> None:
    rng = np.random.default_rng(1)
    values = rng.normal(0.0, 100.0, 100)
    values = values - values.mean() - 20.0  # theta_hat = -20 exactly, SE_boot about 10
    fig = V.trial_figures(V.Series(tuple(weekdays(100)), values, 90), 8.0, 1, B_FAST)
    assert fig["theta_hat"] == pytest.approx(-20.0)
    assert fig["ucb_below_eps"] and not fig["power_ok"]
    assert fig["null_power"] == pytest.approx(V.null_power(fig["se_boot"], 8.0))
    assert fig["status"] == "inconclusive" and fig["reasons"] == ["null power < 0.80"]


def test_the_trial_seed_is_base_plus_ordinal_and_b_is_10000_by_default() -> None:
    t = list_trial(4, "K4-a")
    values = alternating(0.0, 60)
    verdict = V.evaluate(conf_list([t]), {"K4-a": record(t, values, 40)})
    row = verdict["trials"][0]
    assert (row["seed"], row["resamples"]) == (20260927, 10_000)
    boot = V.summarize_means(values, V.resampled_means(values, 10_000, 20260927))
    assert (row["ucb95"], row["se_boot"], row["p_upper"]) == (boot.ucb95, boot.se_boot,
                                                               boot.p_upper)


def test_holm_with_one_tier_a_trial_at_k9() -> None:
    t = list_trial(1, "K4-a")
    verdict = run_verdict([t], {"K4-a": record(t, alternating(12.0, 120), 100)}, b=1000)
    holm = verdict["edge_chain"]["holm"]
    assert (holm["k"], holm["m"]) == (9, 1)
    assert holm["alpha_k"] == pytest.approx(0.05 / 9)
    assert holm["rows"][0]["p_value"] == pytest.approx(1 / 1001) and holm["rows"][0]["reject"]


def test_holm_with_three_tier_a_trials_at_k9() -> None:
    trials = [list_trial(i, f"K4-{c}") for i, c in enumerate("abc", start=1)]
    records = {"K4-a": record(trials[0], alternating(12.0, 120), 100),
               "K4-b": record(trials[1], alternating(11.0, 120), 100),
               "K4-c": record(trials[2], alternating(0.0, 120, 3.0), 100)}
    holm = run_verdict(trials, records, b=1000)["edge_chain"]["holm"]
    rows = {r["member"]: r for r in holm["rows"]}
    assert [r["member"] for r in holm["rows"]] == ["K4-a", "K4-b", "K4-c"]
    assert rows["K4-a"]["threshold"] == pytest.approx(0.05 / 9 / 3)
    assert rows["K4-b"]["threshold"] == pytest.approx(0.05 / 9 / 2)
    assert rows["K4-a"]["reject"] and rows["K4-b"]["reject"] and not rows["K4-c"]["reject"]
    # the thresholds alone, on given p-values
    assert holm_tier_a({"x": 0.001, "y": 0.002, "z": 0.004}, 9).rejected == ("x", "y", "z")
    assert holm_tier_a({"x": 0.001, "y": 0.003, "z": 0.004}, 9).rejected == ("x",)


def _three_trials(tiers: tuple[str, str, str]) -> tuple[list[dict], dict[str, dict]]:
    rng = np.random.default_rng(21)
    trials = [list_trial(i + 1, f"K4-{c}", tier=t) for i, (c, t) in enumerate(zip("abc", tiers,
                                                                                    strict=True))]
    series = {"K4-a": rng.normal(0.8, 2.0, 160), "K4-b": rng.normal(0.2, 1.5, 160),
              "K4-c": rng.normal(-0.1, 3.0, 160)}
    return trials, {t["member"]: record(t, series[t["member"]], 90) for t in trials}


def test_dsr_variance_with_one_tier_a_trial_is_over_every_run_trial() -> None:
    trials, records = _three_trials(("A", "B", "B"))
    verdict = run_verdict(trials, records)
    dsr = verdict["edge_chain"]["dsr"]
    sharpes = {m: V.moments(records[m]["series"]["values"])["sharpe"] for m in records}
    assert dsr["variance_over"] == ["K4-a", "K4-b", "K4-c"]
    assert dsr["sharpe_variance"] == statistics.pvariance(list(sharpes.values()))
    mom = V.moments(records["K4-a"]["series"]["values"])
    expected = deflated_sharpe_ratio(mom["sharpe"], mom["n"], 150, dsr["sharpe_variance"],
                                     mom["skew"], mom["kurtosis"])["deflated_sharpe_ratio"]
    assert verdict["edge_chain"]["trials"]["K4-a"]["dsr"] == expected
    assert dsr["n_trials"] == 150


def test_dsr_variance_with_two_tier_a_trials_is_over_tier_a() -> None:
    trials, records = _three_trials(("A", "A", "B"))
    dsr = run_verdict(trials, records)["edge_chain"]["dsr"]
    sharpes = [V.moments(records[m]["series"]["values"])["sharpe"] for m in ("K4-a", "K4-b")]
    assert dsr["variance_over"] == ["K4-a", "K4-b"]
    assert dsr["sharpe_variance"] == statistics.pvariance(sharpes)


def test_t_is_the_hlz_t_on_the_population_sd() -> None:
    trials, records = _three_trials(("A", "B", "B"))
    t_value = run_verdict(trials, records)["edge_chain"]["trials"]["K4-a"]["t_stat"]
    xs = records["K4-a"]["series"]["values"]
    assert t_value == pytest.approx(statistics.fmean(xs) / (statistics.pstdev(xs)
                                                            / math.sqrt(len(xs))))


def _hand_pbo(members: list[str], records: dict[str, dict]) -> float:
    by_date: dict[str, dict[str, float]] = {}
    for m, rec in records.items():
        for d, v in zip(rec["series"]["dates"], rec["series"]["values"], strict=True):
            by_date.setdefault(d, {})[m] = v
    union = sorted(by_date)
    width = len(union) // 8
    matrix = []
    for m in members:
        col = [by_date[d].get(m, 0.0) for d in union]
        matrix.append([sum(col[b * width:(b + 1) * width]) for b in range(8)])
    return probability_of_backtest_overfitting(matrix, 8).pbo


def _unequal_windows(tiers: tuple[str, str, str]) -> tuple[list[dict], dict[str, dict]]:
    rng = np.random.default_rng(33)
    days = weekdays(260)
    windows = {"K4-a": days[:200], "K4-b": days[40:], "K4-c": days[::2]}
    trials = [list_trial(i + 1, f"K4-{c}", tier=t) for i, (c, t) in enumerate(zip("abc", tiers,
                                                                                    strict=True))]
    records = {t["member"]: record(t, rng.normal(0.2, 2.0, len(windows[t["member"]])), 70,
                                   dates=windows[t["member"]]) for t in trials}
    return trials, records


def test_pbo_with_one_tier_a_trial_is_over_every_run_series_on_the_union_of_dates() -> None:
    trials, records = _unequal_windows(("A", "B", "B"))
    pbo = run_verdict(trials, records)["edge_chain"]["pbo"]
    assert pbo["over"] == ["K4-a", "K4-b", "K4-c"] and pbo["window_days"] == 260
    assert pbo["block_days"] == 260 // 8
    assert pbo["pbo"] == _hand_pbo(["K4-a", "K4-b", "K4-c"], records)


def test_pbo_with_two_tier_a_trials_is_over_tier_a_aligned_on_every_run_trial() -> None:
    trials, records = _unequal_windows(("A", "A", "B"))
    pbo = run_verdict(trials, records)["edge_chain"]["pbo"]
    assert pbo["over"] == ["K4-a", "K4-b"] and pbo["window_days"] == 260
    assert pbo["pbo"] == _hand_pbo(["K4-a", "K4-b"], records)


def test_a_single_series_cluster_has_no_dsr_the_variance_is_undefined() -> None:
    """Review SF-1: with one run series the V14 (c) variance set has one member; DSR is undefined
    (never pvariance of one value, which would give 0.0 and an undeflated DSR) and the trial fails
    the DSR step, reading "no edge (dsr undefined)" (review N-4)."""
    # Arrange: one strong Tier A trial, and a Tier B trial whose record has no series
    t = list_trial(1, "K4-a")
    b = list_trial(2, "K4-b", tier="B")
    values = alternating(12.0, 120)
    records = {"K4-a": record(t, values, 100), "K4-b": record(b, [0.0], 0, status="refused_case")}

    # Act
    chain = run_verdict([t, b], records, b=1000)["edge_chain"]

    # Assert
    assert chain["dsr"] == {"variance_over": ["K4-a"],
                            "undefined": "variance over fewer than 2 series (V14 c)"}
    verdict = chain["trials"]["K4-a"]
    assert verdict["passes"]["holm"] and verdict["passes"]["t"] and not verdict["passes"]["dsr"]
    assert verdict["dsr"] is None
    assert verdict["dsr_undefined"] == "variance over fewer than 2 series (V14 c)"
    assert (verdict["verdict"], verdict["first_failing_step"]) == ("no edge (dsr undefined)",
                                                                   "dsr")
    # the trap avoided: a one-value pvariance is 0.0 and the "DSR" would pass undeflated
    mom = V.moments(values.tolist())
    assert statistics.pvariance([mom["sharpe"]]) == 0.0
    assert deflated_sharpe_ratio(mom["sharpe"], mom["n"], 150, 0.0, mom["skew"],
                                 mom["kurtosis"])["deflated_sharpe_ratio"] > 0.95
    # PBO is undefined too (one series), reported beside it
    assert chain["pbo"]["pbo"] is None and "fewer than 2" in chain["pbo"]["undefined"]
    assert verdict["pbo_undefined"] == chain["pbo"]["undefined"]


def test_an_undefined_pbo_reads_no_edge_pbo_undefined() -> None:
    """Review N-4: two strong Tier A trials on 6 window days: Holm, DSR and t pass, but 6 days
    cannot form 8 blocks, so PBO is undefined and the verdict says so."""
    a, b = list_trial(1, "K4-a"), list_trial(2, "K4-b")
    records = {"K4-a": record(a, alternating(12.0, 6), 6),
               "K4-b": record(b, alternating(11.0, 6), 6)}
    chain = run_verdict([a, b], records, b=1000)["edge_chain"]
    assert chain["pbo"]["pbo"] is None and chain["pbo"]["undefined"] == \
        "6 days cannot form 8 blocks"
    for m in ("K4-a", "K4-b"):
        verdict = chain["trials"][m]
        assert verdict["passes"]["holm"] and verdict["passes"]["dsr"] and verdict["passes"]["t"]
        assert (verdict["verdict"], verdict["first_failing_step"]) == (
            "no edge (pbo undefined)", "pbo")
        assert verdict["pbo_undefined"] == "6 days cannot form 8 blocks"
        assert verdict["dsr_undefined"] is None
    assert chain["dsr"]["undefined"] is None and chain["dsr"]["variance_over"] == ["K4-a", "K4-b"]


def test_a_defined_failing_dsr_reads_plain_no_edge() -> None:
    trials, records = _three_trials(("A", "A", "B"))
    chain = run_verdict(trials, records)["edge_chain"]
    for verdict in chain["trials"].values():
        if verdict["first_failing_step"] == "dsr":
            assert verdict["dsr"] is not None and verdict["verdict"] == "no edge"
    assert all(v["verdict"] in ("no edge", "no edge (dsr undefined)", "no edge (pbo undefined)",
                                "edge candidate, composite pending")
               for v in chain["trials"].values())


def test_the_passing_wording_the_source_overlap_wording_and_never_edge_alone() -> None:
    a = list_trial(1, "K4-a", labels=("source-overlap",))
    b = list_trial(2, "K4-b")
    records = {"K4-a": record(a, alternating(12.0, 160), 150),
               "K4-b": record(b, alternating(11.0, 160), 150)}
    verdict = run_verdict([a, b], records, b=1000)
    chain = verdict["edge_chain"]["trials"]
    assert chain["K4-b"]["verdict"] == "edge candidate, composite pending"
    assert chain["K4-a"]["verdict"] == ("edge candidate, composite pending; source-overlap: no "
                                        "edge claim without a registered holdout read")
    assert all(v["passes"]["composite"] == "pending" for v in chain.values())
    assert verdict["edge_chain"]["composite"] == "pending"
    words = [v["verdict"] for v in chain.values()] + [verdict["statement"]["verdict"]]
    assert "edge" not in words
    # both are above eps (8 ticks): they block the null statement, carrying their chain verdict
    blocking = {r["member"]: r for r in verdict["statement"]["blocking"]}
    assert blocking["K4-b"]["edge_chain"] == "edge candidate, composite pending"
    assert verdict["statement"]["verdict"] == "no statement"


def test_a_failing_chain_names_its_first_failing_step() -> None:
    trials, records = _three_trials(("A", "B", "B"))
    verdict = run_verdict(trials, records)["edge_chain"]["trials"]["K4-a"]
    assert verdict["verdict"] == "no edge"
    first = next(k for k in ("holm", "dsr", "t", "pbo") if not verdict["passes"][k])
    assert verdict["first_failing_step"] == first


# ----------------------------------------------------- statement and table ----
def _null_values(n: int = 200) -> np.ndarray:
    return alternating(0.0, n)


def test_an_all_null_cluster_gets_the_statement_and_the_resolution_table() -> None:
    trials = [list_trial(1, "K4-a"), list_trial(2, "K4-b", tier="B"),
              list_trial(3, "K4-c", vehicle="MCL", tier="B")]
    records = {"K4-a": record(trials[0], _null_values(), 50),
               "K4-b": record(trials[1], _null_values(), 12),
               "K4-c": record(trials[2], alternating(0.0, 150, 2.0), 45)}
    verdict = run_verdict(trials, records)
    st = verdict["statement"]
    assert st["verdict"] == "null" and st["blocking"] == [] and st["not_covered"] == []
    assert st["covered"] == ["K4-a", "K4-b", "K4-c"] and st["null_by_inactivity"] == ["K4-b"]
    rows = by_member(verdict)
    table = {r["vehicle"]: r for r in verdict["resolution"]}
    ng = table["NG"]
    assert (ng["eps_ticks"], ng["q_c"], ng["eps_usd_per_day_at_q"]) == (8.0, 1, 80.0)
    assert ng["fewest_trips"] == {"member": "K4-b", "n_trips": 12}
    largest = max(("K4-a", "K4-b"), key=lambda m: rows[m]["ucb95_per_trade"])
    assert ng["largest_ucb95_per_trade"] == {"member": largest,
                                             "ticks": rows[largest]["ucb95_per_trade"]}
    assert ng["null_by_inactivity"] == ["K4-b"] and ng["not_covered"] == []
    assert table["MCL"]["fewest_trips"] == {"member": "K4-c", "n_trips": 45}
    assert (table["MCL"]["eps_ticks"], table["MCL"]["q_c"]) == (21.0, 4)


def test_inconclusive_by_design_and_excluded_trials_are_not_covered_and_block_nothing() -> None:
    trials = [list_trial(1, "K4-a"), list_trial(2, "K4-b", tier="B",
                                                labels=("inconclusive by design",)),
              list_trial(3, "K4-c", tier="excluded", labels=("coverage_below_0.95",))]
    records = {"K4-a": record(trials[0], _null_values(), 50),
               "K4-b": record(trials[1], alternating(30.0, 100, 50.0), 40)}
    verdict = run_verdict(trials, records)
    rows, st = by_member(verdict), verdict["statement"]
    assert rows["K4-b"]["status"] == "inconclusive" and not rows["K4-b"]["covered"]
    assert "ucb95" in rows["K4-b"]  # keeps its figures
    assert rows["K4-c"]["status"] == "not run" and rows["K4-c"]["record_status"] is None
    assert st["verdict"] == "null" and st["covered"] == ["K4-a"]
    assert st["not_covered"] == [
        {"member": "K4-b", "reason": "inconclusive by design",
         "labels": ["inconclusive by design"]},
        {"member": "K4-c", "reason": "not run: excluded (not Tier A or B)",
         "labels": ["coverage_below_0.95"]}]
    assert verdict["resolution"][0]["not_covered"] == ["K4-b", "K4-c"]


def test_an_inconclusive_trial_keeps_the_cluster_out_of_the_statement() -> None:
    trials = [list_trial(1, "K4-a"), list_trial(2, "K4-b", tier="B")]
    records = {"K4-a": record(trials[0], _null_values(), 50),
               "K4-b": record(trials[1], alternating(9.0, 100), 40)}
    st = run_verdict(trials, records)["statement"]
    assert st["verdict"] == "no statement"
    assert st["blocking"] == [{"member": "K4-b", "status": "inconclusive",
                               "reasons": ["UCB95 >= eps_X"], "edge_chain": None}]


def test_a_run_record_without_a_series_is_inconclusive_and_blocks() -> None:
    trials = [list_trial(1, "K4-a"), list_trial(2, "K4-b")]
    records = {"K4-a": record(trials[0], _null_values(), 50),
               "K4-b": record(trials[1], [0.0], 0, status="refused_case")}
    verdict = run_verdict(trials, records)
    row = by_member(verdict)["K4-b"]
    assert row["status"] == "inconclusive" and row["record_status"] == "refused_case"
    assert verdict["statement"]["verdict"] == "no statement"
    holm = {r["member"]: r for r in verdict["edge_chain"]["holm"]["rows"]}
    assert holm["K4-b"]["p_value"] == 1.0 and verdict["edge_chain"]["holm"]["m"] == 2
    assert verdict["edge_chain"]["trials"]["K4-b"]["dsr_undefined"] == "no series"


def test_the_verdict_carries_the_constants_and_the_hashes() -> None:
    t = list_trial(1, "K4-a")
    verdict = run_verdict([t], {"K4-a": record(t, _null_values(), 50)})
    assert (verdict["schema"], verdict["harness_sha256"], verdict["cluster_freeze_sha256"],
            verdict["program_n"], verdict["k_holm"]) == (V.VERDICT_SCHEMA, HARNESS, FREEZE,
                                                         150, 9)
    assert verdict["constants"]["seed_base"] == 20260923


# ============================================================ (3) refusals ====
def _one() -> tuple[dict, dict]:
    t = list_trial(1, "K4-a")
    return t, record(t, _null_values(60), 40)


@pytest.mark.parametrize(("field", "value", "match"), [
    ("harness_sha256", "ee" * 32, "harness_sha256"),
    ("cluster_freeze_sha256", "ee" * 32, "cluster_freeze_sha256"),
    ("member", "K4-z", "member"),
    ("ordinal", 2, "ordinal"),
    ("window", "research", "window"),
    ("cluster", "K5", "cluster"),
    ("schema", "stage_e_member_record/0", "schema"),
    ("s_x", {"NG": "2019-05-07"}, "S_X"),
    ("s_x", {"CL": "2019-05-06"}, "S_X"),
    ("s_x", {}, "S_X"),
])
def test_a_record_that_differs_from_the_list_is_refused(field: str, value: Any,
                                                        match: str) -> None:
    t, rec = _one()
    rec[field] = value
    with pytest.raises(V.VerdictRefusal, match=match):
        run_verdict([t], {"K4-a": rec})


def test_a_run_trial_without_a_record_and_a_record_not_in_the_list_are_refused() -> None:
    t, rec = _one()
    with pytest.raises(V.VerdictRefusal, match="no record"):
        run_verdict([t], {})
    with pytest.raises(V.VerdictRefusal, match="not in the list"):
        run_verdict([t], {"K4-a": rec, "K4-z": rec})



def test_an_excluded_trials_record_is_checked_and_never_used() -> None:
    # the runner's --all runs every frozen member, so an excluded trial may have a record
    t, rec = _one()
    ex = list_trial(2, "K4-x", tier="excluded", labels=("coverage_below_0.95",))
    ex_rec = record(ex, alternating(30.0, 60, 50.0), 40)
    verdict = run_verdict([t, ex], {"K4-a": rec, "K4-x": ex_rec})
    row = by_member(verdict)["K4-x"]
    assert row["status"] == "not run" and "ucb95" not in row and not row["covered"]
    assert "present and not used" in row["reasons"][0]
    assert verdict["statement"]["verdict"] == "null"
    assert verdict["edge_chain"]["pbo"]["over"] == ["K4-a"]  # not in any run set
    ex_rec["harness_sha256"] = "ee" * 32
    with pytest.raises(V.VerdictRefusal, match="harness_sha256"):
        run_verdict([t, ex], {"K4-a": rec, "K4-x": ex_rec})


@pytest.mark.parametrize("mutate", ["dates", "values", "nan", "length", "vehicle", "n_trips",
                                    "unit", "before_s_x", "after_2024_02_29"])
def test_a_bad_series_is_refused(mutate: str) -> None:
    t, rec = _one()
    series = rec["series"]
    if mutate == "dates":
        series["dates"][5], series["dates"][6] = series["dates"][6], series["dates"][5]
    elif mutate == "values":
        series["dates"][7] = series["dates"][6]
    elif mutate == "nan":
        series["values"][3] = float("inf")
    elif mutate == "length":
        series["values"] = series["values"][:-1]
    elif mutate == "vehicle":
        series["vehicle"] = "MCL"
    elif mutate == "unit":  # review N-6
        series["unit"] = "net ticks per micro per day"
    elif mutate == "before_s_x":
        series["dates"] = [d.isoformat() for d in weekdays(60, start=START - timedelta(days=7))]
    elif mutate == "after_2024_02_29":
        series["dates"] = [d.isoformat() for d in weekdays(60, start=date(2024, 1, 2))]
    else:
        series["n_trips"] = -1
    match = {"dates": "strictly increasing", "values": "strictly increasing",
             "nan": "non-finite", "length": "align", "vehicle": "vehicle",
             "n_trips": "n_trips", "unit": "unit", "before_s_x": "before the list's S_X",
             "after_2024_02_29": "after 2024-02-29"}[mutate]
    with pytest.raises(V.VerdictRefusal, match=match):
        run_verdict([t], {"K4-a": rec})


@pytest.mark.parametrize(("over", "match"), [
    ({"k_holm": 8}, "K 8 is not 9"),
    ({"k_holm": True}, "is not 9"),
    ({"bootstrap": {"seed_base": 20260921, "resamples": 10000, "mean_block": 5.0,
                    "ucb_quantile": 0.95}}, "seed base"),
    ({"bootstrap": {"seed_base": 20260923, "resamples": 2000, "mean_block": 5.0,
                    "ucb_quantile": 0.95}}, "bootstrap"),
    ({"schema": "stage_e_confirmation_list/0"}, "schema"),
    ({"program_n": 0}, "program_n"),
    ({"start_dates": {}}, "start_dates"),
    ({"trials": []}, "no trials"),
])
def test_a_bad_list_is_refused(over: dict, match: str) -> None:
    t, rec = _one()
    payload = {**conf_list([t]), **over}
    with pytest.raises(V.VerdictRefusal, match=match):
        V.evaluate(payload, {"K4-a": rec}, n_resamples=B_FAST)


@pytest.mark.parametrize(("field", "value", "match"), [
    ("bootstrap_seed", 20260923, "bootstrap_seed"),
    ("eps_ticks", 9, "frozen E.2a epsilon"),
    ("q_c", 2, "frozen E.2a epsilon"),
    ("eps_usd_per_day_at_q", 81.0, "frozen E.2a epsilon"),
    ("labels", ["inconclusive-by-design"], "unknown labels"),
    ("tier", "C", "disagree"),
    ("run", False, "disagree"),
])
def test_a_bad_list_trial_is_refused(field: str, value: Any, match: str) -> None:
    t, rec = _one()
    t[field] = value
    with pytest.raises(V.VerdictRefusal, match=match):
        run_verdict([t], {"K4-a": rec})


def test_duplicate_list_trials_are_refused() -> None:
    t, rec = _one()
    with pytest.raises(V.VerdictRefusal, match="repeats"):
        run_verdict([t, dict(t)], {"K4-a": rec})


# =================================================================== (4) CLI ====
def _write_inputs(tmp_path: Path) -> tuple[Path, Path, dict]:
    trials = [list_trial(1, "K4-ngpre-01 NG"), list_trial(2, "K4-b", tier="B")]
    payload = conf_list(trials)
    list_path = tmp_path / "K4_list.json"
    list_path.write_text(json.dumps(payload), encoding="utf-8")
    rec_dir = tmp_path / "records"
    rec_dir.mkdir()
    for t in trials:
        name = V.record_name(CLUSTER, t["member"])
        (rec_dir / name).write_text(json.dumps(record(t, _null_values(80), 40)),
                                    encoding="utf-8")
        (rec_dir / name.replace(".json", "_trips.json")).write_text("not json: never read")
    other = record(list_trial(1, "K5-x", vehicle="MGC"), _null_values(80), 40)
    (rec_dir / "K5_K5-x_confirmation.json").write_text(json.dumps(other), encoding="utf-8")
    return list_path, rec_dir, payload


def test_cli_runs_the_preflight_first_and_writes_the_verdict_once(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    seen: list[str] = []
    monkeypatch.setattr(harness_freeze, "preflight", lambda e, root=None: seen.append(e) or e)
    list_path, rec_dir, _payload = _write_inputs(tmp_path)
    out = tmp_path / "verdict.json"
    argv = ["--harness-sha256", HARNESS, "--list", str(list_path), "--records", str(rec_dir),
            "--out", str(out)]

    # Act
    rc = V.main(argv)
    again = V.main(argv)

    # Assert
    assert rc == 0 and again == 2 and seen == [HARNESS, HARNESS]
    verdict = json.loads(out.read_text(encoding="utf-8"))
    assert verdict["harness_sha256"] == HARNESS and verdict["list_file"] == "K4_list.json"
    assert verdict["list_sha256"] == harness_freeze.sha256_bytes(list_path.read_bytes())
    assert [r["resamples"] for r in verdict["trials"]] == [10_000, 10_000]
    assert verdict["statement"]["verdict"] == "null"


def test_cli_refuses_before_reading_anything_when_the_preflight_fails(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> None:
    def refuse(expected: str, root: Path | None = None) -> str:
        raise harness_freeze.HarnessFreezeError("planted: manifest mismatch")

    monkeypatch.setattr(harness_freeze, "preflight", refuse)
    rc = V.main(["--harness-sha256", HARNESS, "--list", str(tmp_path / "missing.json"),
                 "--records", str(tmp_path), "--out", str(tmp_path / "v.json")])
    assert rc == 2 and "planted" in capsys.readouterr().err
    assert not (tmp_path / "v.json").exists()


def test_cli_refuses_an_unknown_vehicle_by_name(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                                               capsys: pytest.CaptureFixture) -> None:
    """Review N-5: a vehicle absent from the frozen E.2a table is a named refusal (rc 2)."""
    monkeypatch.setattr(harness_freeze, "preflight", lambda e, root=None: e)
    list_path, rec_dir, payload = _write_inputs(tmp_path)
    payload["trials"][1]["vehicle"] = "ES"
    list_path.write_text(json.dumps(payload), encoding="utf-8")
    rc = V.main(["--harness-sha256", HARNESS, "--list", str(list_path), "--records",
                 str(rec_dir), "--out", str(tmp_path / "v.json")])
    err = capsys.readouterr().err
    assert rc == 2 and "REFUSED (VerdictRefusal)" in err and "'ES'" in err
    assert not (tmp_path / "v.json").exists()


def test_cli_refuses_a_list_for_another_harness(tmp_path: Path,
                                                monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(harness_freeze, "preflight", lambda e, root=None: "ee" * 32)
    list_path, rec_dir, _ = _write_inputs(tmp_path)
    rc = V.main(["--harness-sha256", "ee" * 32, "--list", str(list_path), "--records",
                 str(rec_dir), "--out", str(tmp_path / "v.json")])
    assert rc == 2 and not (tmp_path / "v.json").exists()


def test_load_records_refuses_a_cluster_record_not_in_the_list(tmp_path: Path) -> None:
    _list_path, rec_dir, payload = _write_inputs(tmp_path)
    assert set(V.load_records(rec_dir, payload)) == {"K4-ngpre-01 NG", "K4-b"}
    (rec_dir / "K4_K4-z_confirmation.json").write_text("{}", encoding="utf-8")
    with pytest.raises(V.VerdictRefusal, match="K4_K4-z_confirmation.json"):
        V.load_records(rec_dir, payload)
