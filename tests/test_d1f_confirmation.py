"""Stage D.1f Task 7: the list runner, its decision rules and the freeze manifest (the hash,
git-anchor, build and holdout refusals are in tests/test_d1f_preflight.py).

SYNTHETIC ONLY (list 1.5 step 1, R-7): no trial, statistic or H module runs on real bars here.
Members are injected series, synthetic screening reports from a tmp_path parquet, or the
synthetic StatisticsRun of tests/test_d1f_statistics.py. The real repository is read only for
the hash checks, the freeze manifest's file set and the recorded facts files.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import pytest

import strategy.research._d1f_confirmation as conf
import strategy.research._d1f_preflight as pf
from data.config import REPO_ROOT
from screening.drift import bootstrap_mean_lower_bounds, build_drift_path
from screening.runner import confirmation_window, screen_candidate
from strategy.interface import AccountView, Bar, market_intent
from strategy.research._d1d_accounting import ALL_TRIALS
from strategy.research._d1f_decisions import (
    BOOTSTRAP_SEED,
    EPSILON_DAY_TICKS,
    LABEL_INACTIVITY,
    LABEL_PESSIMISTIC,
    Member,
    aligned_series,
    benjamini_hochberg,
    bootstrap,
    evaluate,
    gross_daily,
    holm,
    null_power,
    resampled_means,
    summarize_means,
)
from strategy.research._d1f_freeze import build_manifest, import_closure, write_manifest
from strategy.research._d1f_members import (
    CONFIRMATION_FACTORIES,
    TIER_A_STATISTICS,
    continuity_trials,
    forward_moves_ticks,
    halt_crossing_move_ticks,
    per_micro_daily,
    recorded_edges,
    statistic_composite,
    statistic_directions,
    statistic_member,
    tier_a_trials,
    trial_member,
)
from strategy.research._d1f_start_rule import (
    EXTENSION_MONTHS,
    REFERENCE_MONTHS,
    first_trade_date_by_month,
    reference_volume,
    rth_monthly_median_volume,
    start_rule,
)
from strategy.research._d1f_statistics import (
    StatisticEvents,
    compute_statistics,
    forward_mean_moves_ticks,
    select_statistic_bars,
)
from strategy.research.e_calendar_event._release_table_2019_2024 import RELEASE_TABLE_2019_2024
from strategy.research.e_calendar_event.h1_scheduled_macro_drift import (
    RELEASE_TABLE_ET,
    H1ScheduledMacroDrift,
)
from strategy.research.e_calendar_event.h2_post_release_momentum import H2PostReleaseMomentum

CT = ZoneInfo("America/Chicago")
UTC = ZoneInfo("UTC")
TICK = 0.25
FAST_B = 2000  # resamples for the synthetic decision tests (the production B is 10,000)


# ================================================================== bootstrap ====
def test_bootstrap_statistics_are_the_hand_computed_ones_on_a_known_means_array() -> None:
    daily = np.array([1.0, 2.0, 3.0])  # theta_hat = 2
    boot = summarize_means(daily, np.array([1.0, 2.0, 3.0, 4.0]))
    assert boot.theta_hat == 2.0
    assert boot.ucb95 == pytest.approx(3.85)  # linear: 3 + 0.85 x (4 - 3)
    assert boot.se_boot == pytest.approx(np.sqrt(1.25))  # ddof 0
    assert boot.p_upper == pytest.approx((1 + 1) / 5)  # #{m - 2 >= 2} = #{4}
    assert boot.p_lower == pytest.approx((1 + 4) / 5)  # #{m - 2 <= 2} = all four


def test_bootstrap_draws_are_the_drift_modules_draws_at_the_list_seed() -> None:
    """The same stationary-bootstrap stream screening.drift uses, at seed 20260921, fresh per
    member: its lower bounds are the (1 - c) quantiles of our means."""
    series = np.random.default_rng(3).normal(0.5, 4.0, 60)
    means = resampled_means(series, 500)
    bounds = bootstrap_mean_lower_bounds(series, (0.05, 0.5), 500, BOOTSTRAP_SEED)
    assert bounds[0.05] == pytest.approx(float(np.quantile(means, 0.95)), abs=0, rel=0)
    assert bounds[0.5] == float(np.quantile(means, 0.5))
    assert np.array_equal(means, resampled_means(series, 500))  # fresh generator each call


def test_bootstrap_hand_check_on_a_three_day_series() -> None:
    """Replays the generator by hand: two resamples of [10, 20, 40] at mean block 5."""
    daily = np.array([10.0, 20.0, 40.0])
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    expected = []
    for _ in range(2):
        starts = rng.integers(0, 3, size=3)
        renew = rng.random(3) < 1.0 / 5.0
        renew[0] = True
        idx, block_start = [], 0
        for i in range(3):
            if renew[i]:
                block_start = i
            idx.append((starts[block_start] + i - block_start) % 3)
        expected.append(daily[idx].mean())
    assert np.array_equal(resampled_means(daily, 2), np.array(expected))


def test_constant_series_has_zero_se_and_zero_power() -> None:
    boot = bootstrap(np.full(50, 5.0), 200)
    assert boot.se_boot == 0.0 and boot.ucb95 == 5.0
    assert null_power(0.0) == 0.0
    assert null_power(EPSILON_DAY_TICKS / 2.4865) == pytest.approx(0.80, abs=1e-3)


# ============================================================ Holm and BH ====
def test_holm_step_down_stops_at_the_first_failure() -> None:
    rows = holm({"a": 0.001, "b": 0.013, "c": 0.02, "d": 0.5})
    # thresholds 0.05/4, 0.05/3, 0.05/2, 0.05/1: a passes, b passes (0.013 <= 0.0167),
    # c passes (0.02 <= 0.025), d fails
    assert [rows[k]["reject"] for k in "abcd"] == [True, True, True, False]
    rows = holm({"a": 0.03, "b": 0.001, "c": 0.04})
    # b passes 0.05/3; a fails 0.05/2 = 0.025, so c is not rejected though 0.04 <= 0.05/1
    assert rows["b"]["reject"] and not rows["a"]["reject"] and not rows["c"]["reject"]


def test_benjamini_hochberg_step_up() -> None:
    rows = benjamini_hochberg({"a": 0.01, "b": 0.09, "c": 0.06, "d": 0.5}, 0.10)
    # sorted 0.01, 0.06, 0.09, 0.5 against 0.025, 0.05, 0.075, 0.1: largest k is 1
    assert [rows[k]["reject"] for k in "abcd"] == [True, False, False, False]
    rows = benjamini_hochberg({"a": 0.01, "b": 0.02, "c": 0.07}, 0.10)
    assert all(r["reject"] for r in rows.values())  # 0.07 <= 0.1: step-up rejects all


# ===================================================== decisions end to end ====
WINDOW = tuple(d.date() for d in pd.bdate_range("2020-01-01", periods=400))


def _m(mid: str, tier: str, klass: str, daily: np.ndarray, activity: np.ndarray,
       composite: str | None = "fail", kind: str = "trial",
       dates: tuple[date, ...] = WINDOW) -> Member:
    return Member(mid, tier, kind, klass, dates, np.asarray(daily, dtype=float),
                  np.asarray(activity, dtype=np.int64), composite if tier == "A" else None,
                  None if kind == "trial" else 1)


@pytest.fixture(scope="module")
def evaluation():
    rng = np.random.default_rng(11)
    ones = np.ones(len(WINDOW), dtype=np.int64)
    sparse = np.zeros(len(WINDOW), dtype=np.int64)
    sparse[::40] = 1  # 10 events
    stat_dates = WINDOW[5:]  # a statistic's own post-exclusion dates
    tier_a = [
        _m("edge", "A", "C3", 60 + rng.normal(0, 20, len(WINDOW)), ones, "pass"),
        _m("zero1", "A", "C1", rng.normal(0, 20, len(WINDOW)), ones),
        _m("zero2", "A", "C1", rng.normal(0, 20, len(WINDOW)), ones),
        _m("inactive", "A", "C1", np.where(sparse, rng.normal(0, 5, len(WINDOW)), 0.0),
           sparse, kind="statistic"),
        _m("no_events", "A", "C2", np.zeros(len(WINDOW)), np.zeros(len(WINDOW), np.int64)),
        _m("zero3", "A", "C2", rng.normal(0, 20, len(WINDOW)), ones),
        _m("constant", "A", "C5", np.full(len(WINDOW), 5.0), ones),
        _m("ch4", "A", "C6", rng.normal(0, 20, len(WINDOW)), ones * 90),
        _m("stat_own_dates", "A", "C3", rng.normal(0, 10, len(stat_dates)),
           np.ones(len(stat_dates), np.int64), kind="statistic", dates=stat_dates),
    ]
    tier_b = [
        _m("anomaly", "B", "C4", 50 + rng.normal(0, 10, len(stat_dates)),
           np.full(len(stat_dates), 5, np.int64), kind="statistic", dates=stat_dates),
        _m("reversal", "B", "C4", -30 + rng.normal(0, 10, len(stat_dates)),
           np.full(len(stat_dates), 5, np.int64), kind="statistic", dates=stat_dates),
        _m("quiet", "B", "C7", rng.normal(0, 10, len(stat_dates)),
           np.ones(len(stat_dates), np.int64), kind="statistic", dates=stat_dates),
    ]
    return evaluate(tier_a, tier_b, WINDOW, FAST_B)


def test_a_planted_edge_above_epsilon_passes_every_criterion(evaluation) -> None:
    row = evaluation.tier_a["edge"]
    assert row["theta_hat"] > EPSILON_DAY_TICKS and row["holm"]["reject"]
    assert row["edge_checks"] == {"holm_reject": True, "composite_pass": True,
                                  "dsr_above_0_95": True, "t_above_3": True,
                                  "pbo_below_0_5": True, "passes": True}
    assert row["status"] == "edge" and not row["null"]["meets"]
    assert evaluation.family["pbo_n58"]["pbo"] < 0.5
    assert evaluation.classes["C3"]["verdict"] == "no null statement"
    assert evaluation.classes["C3"]["passing_confirmation"] == ["edge"]


def test_a_member_at_zero_edge_is_null(evaluation) -> None:
    row = evaluation.tier_a["zero1"]
    assert row["status"] == "null" and row["null"]["meets"] and row["labels"] == []
    assert row["ucb95"] < EPSILON_DAY_TICKS and row["null"]["achieved_power"] >= 0.80
    assert not row["edge_checks"]["passes"]


def test_too_few_events_is_null_by_inactivity(evaluation) -> None:
    row = evaluation.tier_a["inactive"]
    assert row["n_activity"] == 10 and row["status"] == "null"
    assert LABEL_INACTIVITY in row["labels"]


def test_zero_events_is_inconclusive_not_null(evaluation) -> None:
    row = evaluation.tier_a["no_events"]
    assert row["status"] == "inconclusive" and row["null"]["no_evidence_n2"]
    assert not row["null"]["meets"]


def test_zero_se_boot_is_inconclusive(evaluation) -> None:
    row = evaluation.tier_a["constant"]
    assert row["se_boot"] == 0.0 and row["n_activity"] > 0
    assert row["status"] == "inconclusive" and row["null"]["achieved_power"] == 0.0


def test_a_class_with_one_inconclusive_member_gets_no_statement(evaluation) -> None:
    c2 = evaluation.classes["C2"]
    assert c2["verdict"] == "no null statement" and c2["inconclusive"] == ["no_events"]
    assert evaluation.classes["C5"]["verdict"] == "no null statement"


def test_a_null_class_carries_the_section_7_fields(evaluation) -> None:
    c1 = evaluation.classes["C1"]
    assert c1["verdict"] == "null"
    fields = c1["statement_fields"]
    assert fields["class_frequency_trades_per_day"] == 1.0  # median over the two trials
    assert fields["epsilon_per_trade"] == EPSILON_DAY_TICKS
    assert fields["least_active_member"] == {"id": "inactive", "count": 10}
    ucbs = {k: evaluation.tier_a[k]["per_trade"]["ucb95"] for k in ("zero1", "zero2", "inactive")}
    assert fields["largest_per_trade_ucb95"]["value"] == max(ucbs.values())
    assert fields["label"] == LABEL_INACTIVITY
    assert fields["null_by_inactivity_members"] == ["inactive"]


def test_c6_stays_inconclusive_under_the_trade_through_model(evaluation) -> None:
    row = evaluation.tier_a["ch4"]
    assert row["status"] == "null" and LABEL_PESSIMISTIC in row["labels"]
    assert evaluation.classes["C6"]["verdict"].startswith("inconclusive until Stage D.1g")


def test_tier_b_anomaly_and_sign_reversal_are_separate_bh_families(evaluation) -> None:
    anomaly, reversal = evaluation.tier_b["anomaly"], evaluation.tier_b["reversal"]
    assert anomaly["anomaly"]["flag"] and anomaly["anomaly"]["net_edge_per_event"] >= 2.11
    assert not anomaly["sign_reversal"]["flag"]
    assert reversal["sign_reversal"]["flag"] and not reversal["anomaly"]["flag"]
    assert all(r["edge_checks"] is None for r in evaluation.tier_b.values())
    assert evaluation.tier_b["quiet"]["status"] == "null"


def _statistic_from_events(mid: str, s: int, e_mean: float, dates: tuple[date, ...],
                           counts: np.ndarray, rng: np.random.Generator
                           ) -> tuple[Member, np.ndarray]:
    """A Tier B statistic built from explicit events: per event v = s x e - 2.11, d_t = the sum
    of v on the date. Returns the member and its gross series (the sum of s x e), by hand."""
    net, gross = np.zeros(len(dates)), np.zeros(len(dates))
    for i, n in enumerate(counts):
        s_times_e = s * rng.normal(s * e_mean, 2.0, int(n))  # mean s x e per event = e_mean
        gross[i] = s_times_e.sum()
        net[i] = (s_times_e - 2.11).sum()
    return Member(mid, "B", "statistic", "C3", dates, net, counts.astype(np.int64), None, s), gross


def test_tier_b_sign_reversal_is_tested_on_the_gross_series() -> None:
    """Lead ruling (c), revised: "a sign reversal versus the mined window" (2.2) is about the
    direction of s x e, so it is tested on the GROSS per-date series. A member whose gross
    effect is positive but whose net is negative (the 2.11-tick cost) is NOT a reversal; one
    whose gross is significantly negative is."""
    rng = np.random.default_rng(29)
    window = WINDOW[:160]
    own = window[3:]  # the statistics' own post-exclusion dates
    counts = rng.integers(0, 4, len(own))  # 0..3 events a date, dates without events included
    costly, costly_gross = _statistic_from_events("costly", -1, 1.0, own, counts, rng)
    reversed_, reversed_gross = _statistic_from_events("reversed", 1, -3.0, own, counts, rng)
    weak, _ = _statistic_from_events("weak", 1, 0.5, own, counts, rng)  # gross > 0, net < 0
    tier_a = [_m(f"a{k}", "A", "C1", rng.normal(0, 20, len(window)),
                 np.ones(len(window), np.int64), dates=window) for k in range(2)]
    ev = evaluate(tier_a, [costly, reversed_, weak], window, FAST_B)

    # The gross series is the per-date sum of s x e, 0 on a date without events.
    assert np.allclose(gross_daily(costly), costly_gross, rtol=0, atol=1e-9)
    assert np.allclose(gross_daily(reversed_), reversed_gross, rtol=0, atol=1e-9)
    assert (costly_gross[counts == 0] == 0).all() and (counts == 0).any()
    with pytest.raises(ValueError, match="only a statistic"):
        gross_daily(tier_a[0])

    row = ev.tier_b["costly"]  # gross > 0, net < 0: NOT a sign reversal
    assert row["sign_reversal"]["theta_hat_gross"] > 0 > row["theta_hat"]
    assert not row["sign_reversal"]["flag"] and not row["anomaly"]["flag"]
    assert bootstrap(costly.daily, FAST_B).p_lower < 0.01  # the NET series alone would flag it

    row = ev.tier_b["reversed"]  # gross significantly < 0: a sign reversal
    assert row["sign_reversal"]["flag"] and not row["anomaly"]["flag"]
    assert row["sign_reversal"]["theta_hat_gross"] == pytest.approx(reversed_gross.mean())
    means = resampled_means(reversed_gross, FAST_B)  # the same fresh generator at the list seed
    theta = reversed_gross.mean()
    p = (1 + int(np.sum(means - theta <= theta))) / (FAST_B + 1)
    assert row["sign_reversal"]["p_one_sided_gross_below_0"] == pytest.approx(p, abs=1e-12)
    assert row["sign_reversal"]["bh"]["rank"] == 1
    assert row["sign_reversal"]["bh"]["threshold"] == pytest.approx(0.10 / 3)  # within Tier B

    # The anomaly test is unchanged: net v, one-sided in direction s, p_upper on the net series.
    for key, member in (("costly", costly), ("reversed", reversed_), ("weak", weak)):
        assert ev.tier_b[key]["p_one_sided"] == bootstrap(member.daily, FAST_B).p_upper
    assert ev.tier_b["weak"]["sign_reversal"]["flag"] is False


def test_accounting_uses_own_series_for_dsr_and_aligned_series_for_pbo(evaluation) -> None:
    fam = evaluation.family
    assert fam["n_trials"] == {"prior": 31, "after_d1f": 9, "reported_101": 12,
                               "reported_186": 12 + 85}
    assert fam["dsr_n58"]["variance_over_n_members"] == 9
    assert fam["reported_dsr_n101"]["variance_over_n_members"] == 12
    assert fam["reported_dsr_n186"]["n_trials"] == 97
    n186, n101 = fam["reported_dsr_n186"], fam["reported_dsr_n101"]
    assert n186["sharpe_variance"] == n101["sharpe_variance"]
    assert fam["pbo_n58"]["n_days"] == len(WINDOW) and fam["pbo_n58"]["block_days"] == 50
    own = evaluation.tier_a["stat_own_dates"]
    assert own["n_days"] == len(WINDOW) - 5 == own["accounting"]["moments"]["n"]
    assert evaluation.tier_a["no_events"]["accounting"]["dsr_n58"] is None


def test_year_slices_bootstrap_each_year_on_its_own(evaluation) -> None:
    slices = evaluation.tier_a["zero1"]["year_slices"]
    assert set(slices) == {"2020", "2021"}
    daily = np.array(evaluation.tier_a["zero1"]["daily_ticks_per_micro"])
    in_2021 = np.array([d.startswith("2021") for d in evaluation.tier_a["zero1"]["dates"]])
    assert slices["2021"]["theta_hat"] == pytest.approx(daily[in_2021].mean())
    assert slices["2021"]["ucb95"] == pytest.approx(bootstrap(daily[in_2021], FAST_B).ucb95)


def test_aligned_series_puts_zeros_off_the_members_dates() -> None:
    member = _m("s", "A", "C3", np.array([1.0, 2.0]), np.array([1, 1]), kind="statistic",
                dates=(WINDOW[1], WINDOW[3]))
    assert aligned_series(member, WINDOW[:5]).tolist() == [0.0, 1.0, 0.0, 2.0, 0.0]
    with pytest.raises(ValueError, match="outside the window"):
        aligned_series(member, WINDOW[2:5])


# ============================================================== start rule ====
def _bars_at(day: date, clock: list[tuple[int, int]], volume: int) -> pd.DataFrame:
    ts = [int(datetime.combine(day, time(h, m), tzinfo=CT).timestamp()) * 10**9
          for h, m in clock]
    return pd.DataFrame({"ts_event": ts, "volume": volume, "trade_date": day.isoformat()})


def test_rth_median_uses_only_0830_to_1459_ct_bars_present() -> None:
    frame = pd.concat([_bars_at(date(2025, 4, 1), [(8, 29), (15, 0)], 10_000),
                       _bars_at(date(2025, 4, 1), [(8, 30), (14, 59)], 100),
                       _bars_at(date(2025, 4, 2), [(9, 0)], 400)])
    assert rth_monthly_median_volume(frame) == {"2025-04": 100.0}
    assert first_trade_date_by_month(frame) == {"2025-04": date(2025, 4, 1)}


def _first_dates() -> dict[str, date]:
    out = {m: date(int(m[:4]), int(m[5:]), 2) for m in EXTENSION_MONTHS}
    out["2019-05"] = date(2019, 5, 6)
    return out


def test_start_rule_picks_the_first_month_of_the_trailing_qualifying_run() -> None:
    research = {m: 100.0 + 10 * i for i, m in enumerate(REFERENCE_MONTHS)}
    v_ref = reference_volume(research)
    assert v_ref == pytest.approx((160.0 + 170.0) / 2)  # median of 14: mean of 7th and 8th
    ext = {m: 0.30 * v_ref for m in EXTENSION_MONTHS}
    ext["2019-06"] = 0.10 * v_ref  # a dip: 2019-05 cannot be M*, though it qualifies itself
    ext["2020-03"] = 0.20 * v_ref  # below 0.25, above 0.15
    record = start_rule(research, ext, _first_dates())
    assert record["binding"]["m_star"] == "2020-04" and record["S"] == "2020-04-02"
    sens = {s["fraction"]: s["m_star"] for s in record["sensitivity"]}
    assert sens == {0.15: "2019-07", 0.40: None}
    all_ok = start_rule(research, {m: v_ref for m in EXTENSION_MONTHS}, _first_dates())
    assert all_ok["S"] == "2019-05-06" and not all_ok["empty_window"]
    late = {**_first_dates(), "2019-05": date(2019, 5, 7)}  # contradicts 4.1's 2019-05-06
    with pytest.raises(ValueError, match="stop for the lead"):
        start_rule(research, {m: v_ref for m in EXTENSION_MONTHS}, late)


def test_start_rule_stops_when_no_month_qualifies() -> None:
    research = {m: 1000.0 for m in REFERENCE_MONTHS}
    ext = {m: 1000.0 for m in EXTENSION_MONTHS}
    ext["2024-02"] = 100.0  # the last month fails, so no trailing run exists
    record = start_rule(research, ext, _first_dates())
    assert record["S"] is None and record["empty_window"]
    missing = dict(ext, **{"2024-02": 1000.0})
    del missing["2023-12"]  # a month without a V_M cannot qualify
    assert start_rule(research, missing, _first_dates())["binding"]["m_star"] == "2024-01"
    with pytest.raises(ValueError, match="14 months"):
        reference_volume({m: 1.0 for m in REFERENCE_MONTHS[1:]})


# ====================================================== trials: per micro ====
def test_per_micro_partition_is_exact() -> None:
    trips = [12.50, 25.00, -6.25, 3.75]  # USD
    micros = [1, 2, 5, 3]  # 10, 10, -1 and 1 tick(s) per micro
    assert per_micro_daily(trips, micros, [2, 0, 1, 1]).tolist() == [20.0, 0.0, -1.0, 1.0]
    with pytest.raises(AssertionError, match="sum to"):
        per_micro_daily(trips, micros, [2, 0, 1])
    with pytest.raises(AssertionError, match="sizes"):
        per_micro_daily(trips, micros[:3], [2, 0, 1, 1])


@dataclass(frozen=True)
class _TwoMicroRth:
    """Synthetic: long 2 micros 08:30 -> 15:00 CT; exposes forced_exit_dates as H does."""

    name: str = "synthetic_two_micro"

    @property
    def forced_exit_dates(self) -> tuple[date, ...]:
        return (date(2021, 3, 2),)

    def on_bar(self, bar: Bar, account: AccountView) -> tuple:
        local = bar.open_ts_utc.astimezone(CT)
        if (local.hour, local.minute) == (8, 30) and account.position_micros == 0:
            return (market_intent(bar, "buy", 2),)
        if (local.hour, local.minute) == (15, 0) and account.position_micros:
            return (market_intent(bar, "sell", account.position_micros),)
        return ()


@pytest.fixture(scope="module")
def synthetic_window(tmp_path_factory: pytest.TempPathFactory):
    from tests.test_d1f_confirmation_window import SYN_DAYS, SYN_ROLL, _synthetic_bars
    from tests.test_d1f_confirmation_window import _write_like_the_builder as write

    path = write(_synthetic_bars(), tmp_path_factory.mktemp("conf") / "c.parquet", [SYN_ROLL])
    return confirmation_window(SYN_DAYS[0], path=path)


def test_trial_member_from_a_synthetic_screen_is_net_ticks_per_micro(synthetic_window) -> None:
    results = conf.run_screens([("two micro", _TwoMicroRth, "C7")], synthetic_window, 1)
    forced = results[0]["forced_exits"]  # the instance was kept; its ledger exits by strategy
    assert forced["forced_exit_dates_instance"] == ["2021-03-02"]
    assert forced["forced_exit_dates_ledger"] == [] and forced["n_forced_exits"] == 0
    assert forced["forced_exit_sets_differ"] and forced["only_in_instance"] == ["2021-03-02"]
    report = results[0]["report"]
    member = trial_member("two micro", "C7", report, synthetic_window.trade_dates)
    assert set(report["trip_micros"]) == {2}
    assert np.allclose(member.daily, np.array(report["daily_net_usd"]) / (1.25 * 2))
    assert member.n_activity == report["n_trips"] and member.composite == report["verdict"]
    screened = screen_candidate("two micro", _TwoMicroRth, synthetic_window)
    assert screened.to_dict()["daily_n_trips"] == report["daily_n_trips"]


def test_run_screens_refuses_on_any_error(synthetic_window) -> None:
    def broken():
        raise RuntimeError("boom")

    with pytest.raises(conf.StepRefused, match="boom"):
        conf.run_screens([("broken", broken, "C1")], synthetic_window, 1)


# ============================================================ statistics ====
@pytest.fixture(scope="module")
def synthetic_stats():
    from tests.test_d1f_statistics import SYN_DAYS, SYN_SPLICE, _synthetic_bars

    bars = _synthetic_bars()
    run = compute_statistics(bars, SYN_DAYS, (SYN_SPLICE,))
    return bars, run, select_statistic_bars(bars, run.dates)


def test_statistic_member_is_v_summed_on_its_own_dates(synthetic_stats) -> None:
    _, run, _ = synthetic_stats
    ev = run.directional["F4_1_rth_open_crossing"]
    member = statistic_member(ev, "B", "C2", -1, run.dates)
    assert member.dates == run.dates and member.n_activity == len(ev.values)
    assert member.daily.sum() == pytest.approx(float((-ev.values - 2.11).sum()))
    assert member.composite is None and member.direction == -1


def test_statistic_composite_runs_the_gate_and_both_drift_checks(synthetic_stats) -> None:
    _, run, stat_bars = synthetic_stats
    gate = REPO_ROOT / "reports" / "power_gate.json"
    ev = run.directional["F4_4_round_number_multiples_of_100"]
    assert ev.crosses_trade_date.sum() == 1  # the halt-crossing case of lead ruling (e)
    detail = statistic_composite(ev, -1, run.dates, stat_bars, gate)
    assert detail["verdict"] in ("pass", "fail") and detail["n_halt_crossing_events"] == 1
    drift_ok = detail["drift"]["passes"] and detail["drift_adjusted"]["robust"] == "pass"
    assert (detail["verdict"] == "pass") == (detail["zero_edge"]["robust"] == "pass"
                                             and drift_ok)
    v = -ev.values - 2.11
    assert detail["zero_edge"]["win_probability"] == pytest.approx(np.mean(v > 0))
    member = statistic_member(ev, "A", "C2", -1, run.dates, detail)
    assert member.composite == detail["verdict"]


def test_forward_moves_match_the_wrapper_on_one_trade_date(synthetic_stats) -> None:
    _, run, stat_bars = synthetic_stats
    path = build_drift_path(stat_bars, frozenset())
    ev = run.directional["F3_2_bucket07_bucket08"]
    assert np.array_equal(forward_moves_ticks(ev, path, stat_bars),
                          forward_mean_moves_ticks(ev, path))


def _halt_bars() -> pd.DataFrame:
    """Trade date 2030-01-07 ends 15:57..15:59 CT; 2030-01-08 opens 17:00, 17:01 CT (on the
    evening of 01-07). Prices in points; the halt gap 102 -> 110 must not be charged."""
    rows = [(date(2030, 1, 7), date(2030, 1, 7), (15, 57), 100, 101),
            (date(2030, 1, 7), date(2030, 1, 7), (15, 58), 101, 103),
            (date(2030, 1, 7), date(2030, 1, 7), (15, 59), 103, 102),
            (date(2030, 1, 8), date(2030, 1, 7), (17, 0), 110, 111),
            (date(2030, 1, 8), date(2030, 1, 7), (17, 1), 111, 115)]
    return pd.DataFrame([{
        "ts_event": int(datetime.combine(ct_day, time(*hm), tzinfo=CT).timestamp()) * 10**9,
        "open": float(o), "close": float(c), "trade_date": td.isoformat(), "instrument_id": 1}
        for td, ct_day, hm, o, c in rows])


def test_halt_crossing_drift_sums_per_minute_changes_with_the_halt_at_zero() -> None:
    bars = _halt_bars()
    path = build_drift_path(bars, frozenset())
    ts = bars["ts_event"].to_numpy(np.int64)
    got = halt_crossing_move_ticks(int(ts[1]), int(ts[4]), path, ts,
                                   bars["trade_date"].to_numpy())
    # (103-101) + (102-103) + (111-110) + (115-111) points = 6 points = 24 ticks, not 56
    assert got == pytest.approx(24.0)


def test_forward_moves_dispatch_crossing_events_to_the_ruling() -> None:
    bars = _halt_bars()
    path = build_drift_path(bars, frozenset())
    ts = bars["ts_event"].to_numpy(np.int64)
    d7, d8 = date(2030, 1, 7), date(2030, 1, 8)
    ev = StatisticEvents(
        stat_id="F4_4_round_number_multiples_of_100", source="F", family="F4.4",
        description="synthetic", keys=("round_ticks", "control_ticks"),
        values=np.array([4.0, 8.0]), trade_dates=(d7, d7),
        start_bar_ts_ns=np.array([ts[0], ts[1]]), start_price=("open", "open"),
        end_bar_ts_ns=np.array([ts[2], ts[4]]), end_price=("close", "close"),
        end_trade_dates=(d7, d8), estimate=None, n=2, implied_edge_ticks=None, extra={})
    moves = forward_moves_ticks(ev, path, bars)
    assert moves[0] == pytest.approx((102 - 100) / TICK)  # one date: the wrapper's two points
    assert moves[1] == pytest.approx(24.0)


# ======================================================== list definitions ====
def test_tier_a_trials_are_the_31_plus_h_with_the_confirmation_factories() -> None:
    trials = tier_a_trials()
    assert len(trials) == 37 and len({t[0] for t in trials}) == 37
    factories = {label: f for label, f, _ in trials}
    classes = {label: k for label, _, k in trials}
    assert classes["C-H4 passive-fill reversal"] == "C6"
    assert classes["RT5 C-H2 spike fade 5-min bars"] == "C3"
    for cls in (H1ScheduledMacroDrift, H2PostReleaseMomentum):
        label = next(label for label, f in ALL_TRIALS if f is cls)
        instance = factories[label]()
        assert factories[label] is CONFIRMATION_FACTORIES[cls] and isinstance(instance, cls)
        assert instance.release_table == RELEASE_TABLE_ET | RELEASE_TABLE_2019_2024
    runs = continuity_trials()
    assert len(runs) == 33 and sum(tag == "confirmation_factory" for *_, tag in runs) == 2


def test_statistic_directions_follow_the_table_and_the_recorded_edges() -> None:
    edges = recorded_edges()
    directions = statistic_directions(edges)
    assert sum(v[0] == "A" for v in directions.values()) == 21
    assert sum(v[0] == "B" for v in directions.values()) == 43
    for sid, klass, s in TIER_A_STATISTICS:
        assert directions[sid] == ("A", klass, s)
    assert directions["F1_1_h30_RTH"] == ("B", "C3", 1)
    assert directions["G3.RTH.5"] == ("B", "C2", 1)
    with pytest.raises(AssertionError, match="no sign"):
        statistic_directions({**edges, "G3.RTH.5": 0.0})
    with pytest.raises(AssertionError, match="disagree"):
        statistic_directions({**edges, "G3.RTH.15": 10.0})


# ================================================================ step 6 ====
def _recorded(label: str, net: float, trips: int, daily: list[float]) -> dict:
    from strategy.research._d1b_accounting import _moments

    return {"runs": [{"label": label, "net_pnl_usd": net, "n_trips": trips}],
            "per_trial": {label: {"sharpe": round(_moments(daily)["sharpe"], 6)}}}


def test_continuity_detects_a_cent_a_trip_and_a_sharpe(monkeypatch) -> None:
    monkeypatch.setattr(conf, "N_CONTINUITY_RUNS", 1)
    daily = [1.0, -2.0, 3.5]
    recorded = _recorded("X", 2.5, 3, daily)
    run = {"label": "X", "tag": "default",
           "report": {"net_pnl_usd": 2.5, "n_trips": 3, "daily_net_usd": daily}}
    assert conf.continuity_problems([run], recorded) == []
    for key, value, words in (("net_pnl_usd", 2.51, "net"), ("n_trips", 4, "trips"),
                              ("daily_net_usd", [1.0, -2.0, 3.6], "Sharpe")):
        bad = {**run, "report": {**run["report"], key: value}}
        assert any(words in p for p in conf.continuity_problems([bad], recorded))


def test_member_records_round_trip_through_json() -> None:
    member = _m("s", "A", "C3", np.array([1.5, -2.0]), np.array([1, 3]), "pass",
                kind="statistic", dates=WINDOW[:2])
    blob = json.loads(json.dumps(conf.plain(conf.member_record(member, "statistic"))))
    back = conf.member_from_record(blob, {"statistic": WINDOW[:2]})
    assert back.member_id == "s" and back.composite == "pass" and back.direction == 1
    assert np.array_equal(back.daily, member.daily) and back.n_activity == 4


# ========================================================= freeze manifest ====
@pytest.fixture(scope="module")
def manifest() -> dict:
    return build_manifest(REPO_ROOT)


def test_freeze_covers_every_required_file(manifest: dict) -> None:
    files = manifest["files"]
    assert list(files) == sorted(files) and manifest["file_count"] == len(files)
    root = REPO_ROOT
    required = set()
    for d in ("screening", "sim", "funnel", "rules"):
        required |= {p.relative_to(root).as_posix() for p in (root / d).rglob("*")
                     if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"}
    for d in ("strategy", "data", "screening", "sim", "funnel", "rules"):  # review F3
        required |= {p.relative_to(root).as_posix() for p in (root / d).rglob("*.py")
                     if "__pycache__" not in p.parts}
    required |= {p.relative_to(root).as_posix() for p in (root / "data").glob("*.py")}
    required |= {p.relative_to(root).as_posix()
                 for p in (root / "strategy/research/h_daily_bar").glob("*.py")}
    required |= {p.relative_to(root).as_posix()
                 for p in (root / "strategy/research").glob("_d1f_*.py")}
    required |= {e.path for e in pf.parse_section0((root / pf.LIST_PATH).read_text())}
    required |= {"sim/slippage_calibration.json", "reports/power_gate.json",
                 "strategy/interface.py", "pyproject.toml", "uv.lock", pf.LIST_PATH,
                 pf.CRITERIA_PATH, pf.DECLARATION_HASHES_PATH,
                 "strategy/research/e_calendar_event/_release_table_2019_2024.py",
                 "strategy/research/_d1f_confirmation.py", "strategy/research/_d1f_freeze.py",
                 "reports/stage_d1b_family_f_facts.json", "reports/stage_d1d_family_g_facts.json",
                 "strategy/research/__init__.py", "docs/HOLDOUT_MANIFEST.json"}  # F3, N6
    assert required <= set(files), sorted(required - set(files))
    assert set(manifest["sources"]["pinned_py_dirs"]) == pf.python_files_under(root)
    assert not any("__pycache__" in p or p.endswith(".pyc") or p.startswith("tests/")
                   for p in files)


def test_freeze_import_closure_reaches_the_trials_and_packages(manifest: dict) -> None:
    closure = set(manifest["sources"]["import_closure"])
    for rel in ("strategy/__init__.py", "strategy/research/__init__.py",
                "strategy/research/_d1b_accounting.py",
                "strategy/research/_lead_accounting.py", "data/holdout.py",
                "strategy/research/a_session_clock/h1_european_open_overnight_drift.py",
                "strategy/research/g_timeframe/retests.py", "screening/runner.py"):
        assert rel in closure, rel
    assert import_closure(REPO_ROOT, ["strategy/research/_d1f_start_rule.py"]) >= {
        "strategy/research/_d1f_start_rule.py", "sim/costs.py"}


def test_freeze_records_the_amendments_and_verifies_against_the_repository(
        manifest: dict, tmp_path: Path) -> None:
    section0 = {e.path: e.sha256 for e in
                pf.parse_section0((REPO_ROOT / pf.LIST_PATH).read_text())}
    for rel in pf.EH_AMENDED:
        record = manifest["declared_amendments"][rel]
        assert record["pre_amendment_sha256"] == section0[rel]
        assert record["post_amendment_sha256"] == manifest["files"][rel]
    stamp = datetime.fromisoformat(manifest["generated_local"])
    assert stamp.utcoffset() in (timedelta(hours=-7), timedelta(hours=-8))
    assert "own sha256" in manifest["note"]
    assert pf.check_manifest(REPO_ROOT, manifest) == []
    assert pf.check_section0(REPO_ROOT, manifest) == []
    out = tmp_path / "freeze.json"
    digest = write_manifest(REPO_ROOT, out)
    assert digest == pf.sha256_file(out) and json.loads(out.read_text())["files"] == \
        manifest["files"]
