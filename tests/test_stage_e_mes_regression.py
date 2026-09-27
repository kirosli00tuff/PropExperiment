"""MES regressions (Stage E.2b Task 1, item 9): the generalized Stage E path (the Stage E bar
loader, the group-calendar roll blackout, the generalized engine under MesRules and the Stage E
trip code) reproduces D.1's screening output bit for bit for three D.1 trials, one each of
classes C1, C2 and C4 (reports/stage_d1f_confirmation_list.md 2.1), on MES's own research bars:
against the unchanged screening.runner.screen_candidate (every series element, float for float)
and against the values D.1d recorded (reports/stage_d1d_accounting.json).

Reads MES's research parquet (the only real bars Task 1 may read); skipped where it is absent
(for example on the Windows compute backend). Heavy: run through reports/stage_e2b_briefs/heavy.sh.
"""

from __future__ import annotations

import json

import pytest

from data.config import PROCESSED_ROOT, REPO_ROOT
from data.research_bars import RESEARCH_SERIES_PATH
from screening.stage_e_mes_regression import REGRESSION_TRIALS, mes_new_path, regression_factory

pytestmark = pytest.mark.skipif(not RESEARCH_SERIES_PATH.is_file(),
                                reason="MES research parquet not on this machine")
RECORDED = REPO_ROOT / "reports" / "stage_d1d_accounting.json"


def _recorded(label: str) -> tuple[dict, dict]:
    doc = json.loads(RECORDED.read_text(encoding="utf-8"))
    run = next(r for r in doc["runs"] if r["label"] == label)
    return run, doc["per_trial"][label]


@pytest.fixture(scope="module")
def results() -> dict:
    from screening.runner import screen_candidate, train_union_window

    out = {}
    for label, _cls in REGRESSION_TRIALS:
        factory = regression_factory(label)
        out[label] = (mes_new_path(label, factory, PROCESSED_ROOT),
                      screen_candidate(label, factory, train_union_window()))
    return out


@pytest.mark.parametrize("label", [t[0] for t in REGRESSION_TRIALS])
def test_new_path_equals_the_unchanged_mes_runner_bit_for_bit(results: dict, label: str) -> None:
    new, old = results[label]
    assert new["n_dates"] == old.n_dates == 289
    assert new["daily_net_usd"] == old.daily_net_usd  # tuple of floats, exact
    assert new["trip_pnls_usd"] == old.trip_pnls_usd
    assert new["daily_n_trips"] == old.daily_n_trips
    assert new["trip_micros"] == old.trip_micros
    assert new["n_trips"] == old.n_trips and new["trades_per_day"] == old.trades_per_day
    assert new["net_pnl_usd"] == old.net_pnl_usd
    assert new["win_probability"] == old.zero_edge.win_probability
    assert new["win_loss_ratio"] == old.zero_edge.win_loss_ratio
    assert new["blackout_dates_in_window"] == old.blackout_dates_in_window


@pytest.mark.parametrize("label", [t[0] for t in REGRESSION_TRIALS])
def test_new_path_equals_d1s_recorded_output(results: dict, label: str) -> None:
    from strategy.research._d1b_accounting import _moments

    new, _old = results[label]
    run, per_trial = _recorded(label)
    assert new["n_trips"] == run["n_trips"]
    assert new["trades_per_day"] == run["trades_per_day"]
    assert new["net_pnl_usd"] == run["net_pnl_usd"]
    assert new["win_probability"] == run["win_probability"]
    assert new["win_loss_ratio"] == run["win_loss_ratio"]
    m = _moments(list(new["daily_net_usd"]))
    for key in ("n", "mean", "sd", "skew", "kurtosis", "sharpe"):
        assert round(m[key], 6) == per_trial[key], key
    from funnel.multiple_comparisons import harvey_liu_zhu_verdict

    t = harvey_liu_zhu_verdict(m["mean"], m["sd"], m["n"])["t_stat"]
    assert round(t, 4) == per_trial["t_stat"]


def test_the_three_trials_cover_classes_c1_c2_and_c4() -> None:
    text = (REPO_ROOT / "reports" / "stage_d1f_confirmation_list.md").read_text(encoding="utf-8")
    for label, cls in REGRESSION_TRIALS:
        assert any(line.startswith(f"| {label} | {cls} |") for line in text.splitlines()), label
