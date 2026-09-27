"""Stage E.2b G4 (MLTestCoder): M6's training-window DSR and PBO from the route's ledgers
(ml_route.accounting), with known answers, the pinned helpers' identity with D.1's, and the
refusals. Synthetic ledgers only."""

from __future__ import annotations

import json
import statistics
from datetime import date, timedelta
from itertools import combinations

import numpy as np
import pytest

from funnel.multiple_comparisons import deflated_sharpe_ratio, probability_of_backtest_overfitting
from ml_route import lgbm, lstm
from ml_route.accounting import (
    N_CONFIGURATIONS,
    AccountingError,
    ConfigSeries,
    aligned_matrix,
    configuration_series,
    contiguous_blocks,
    implied_independent_trials,
    moments,
    pbo,
    route_series,
    route_training_accounting,
    training_accounting,
)
from ml_route.blocks import cpcv_splits, cut_blocks
from ml_route.ledger import HashChainError, Ledger

DAYS = [date(2020, 1, 1) + timedelta(days=i) for i in range(36)]  # 6 blocks of 6 dates
CUT = cut_blocks(DAYS)
SPLITS = cpcv_splits(CUT)


def _records(ch: str, h: str, config: dict, cid: str, seed: int, drop: date | None = None,
             splits=SPLITS) -> list[dict]:
    rng = np.random.default_rng(seed)
    out = []
    for sp in splits:
        days = sorted(d for d in sp.validation_dates if d != drop)
        pnl = [[d.isoformat(), float(rng.normal(0.01, 1.0))] for d in days]
        out.append({"key": f"{cid}|{sp.label()}", "challenger": ch, "horizon": h,
                    "config": config, "split": sp.label(), "daily_pnl": pnl,
                    "score": statistics.fmean(v for _, v in pnl)})
    return out


class TestPinnedHelpers:
    def test_moments_and_blocks_are_d1s_line_for_line(self) -> None:
        from strategy.research._d1b_accounting import _blocks, _moments

        rng = np.random.default_rng(3)
        for n in (8, 17, 101):
            xs = list(rng.standard_t(4, size=n))
            assert moments(xs) == _moments(xs)
            assert contiguous_blocks(xs) == _blocks(xs)
        assert moments([0.0] * 5) == _moments([0.0] * 5)


class TestConfigurationSeries:
    def test_the_per_date_mean_over_the_four_validating_splits(self) -> None:
        recs = _records("lgbm", "h30", {"num_leaves": 7}, "c1", 1)
        (s,) = configuration_series(recs, "lgbm", "h30")
        day = DAYS[0].isoformat()  # block 1: validated by splits 12, 13, 14, 15
        want = statistics.fmean(v for r in recs for d, v in r["daily_pnl"] if d == day)
        assert s.daily[day] == want
        assert len([r for r in recs if any(d == day for d, _ in r["daily_pnl"])]) == 4
        assert len(s.daily) == 30 and s.config_id == "c1"  # blocks 1-5; block 6 is the pre-test
        assert statistics.fmean(s.split_scores.values()) == pytest.approx(
            statistics.fmean(s.daily.values()), abs=1e-12)  # equal splits: the ML-A01 score

    def test_the_refit_record_is_ignored(self) -> None:
        recs = _records("lgbm", "h30", {"num_leaves": 7}, "c1", 1)
        recs.append({"key": "c1|refit", "challenger": "lgbm", "horizon": "h30",
                     "config": {"num_leaves": 7}, "split": "refit_blocks_1_5"})
        assert len(configuration_series(recs, "lgbm", "h30")) == 1

    def test_a_missing_split_is_refused(self) -> None:
        recs = _records("lgbm", "h30", {"num_leaves": 7}, "c1", 1)[:-1]
        with pytest.raises(AccountingError, match="9 distinct splits"):
            configuration_series(recs, "lgbm", "h30")

    def test_a_date_missing_from_one_split_is_refused(self) -> None:
        recs = _records("lgbm", "h30", {"num_leaves": 7}, "c1", 1)
        recs[0]["daily_pnl"] = recs[0]["daily_pnl"][1:]
        with pytest.raises(AccountingError, match="exactly 4 splits"):
            configuration_series(recs, "lgbm", "h30")

    def test_a_record_of_another_ledger_is_refused(self) -> None:
        recs = _records("lgbm", "h120", {"num_leaves": 7}, "c1", 1)
        with pytest.raises(AccountingError, match="lgbm_h30 ledger"):
            configuration_series(recs, "lgbm", "h30")

    def test_splits_that_disagree_on_the_configuration_are_refused(self) -> None:
        recs = _records("lgbm", "h30", {"num_leaves": 7}, "c1", 1)
        recs[3]["config"] = {"num_leaves": 31}
        with pytest.raises(AccountingError, match="disagree"):
            configuration_series(recs, "lgbm", "h30")


def _walsh(n: int = 8) -> np.ndarray:
    h = np.array([[1.0]])
    while h.shape[0] < n:
        h = np.block([[h, h], [h, -h]])
    return h[1:]  # the zero-mean, mutually orthogonal rows


class TestImpliedIndependentTrials:
    def test_uncorrelated_trials_are_all_independent(self) -> None:
        got = implied_independent_trials(_walsh()[:3])
        assert got["average_correlation"] == pytest.approx(0.0, abs=1e-12)
        assert got["n_hat"] == pytest.approx(3.0, abs=1e-12)

    def test_pairwise_correlation_one_half_gives_two_of_three(self) -> None:
        w = _walsh()
        x = np.array([w[0] + w[1], w[0] + w[2], w[0] + w[3]])  # corr = 8 / 16 = 0.5
        got = implied_independent_trials(x)
        assert got["average_correlation"] == pytest.approx(0.5, abs=1e-12)
        assert got["n_hat"] == pytest.approx(0.5 + 0.5 * 3, abs=1e-12)
        assert got["status"] == "computed"

    def test_a_constant_series_or_a_singular_matrix_is_undefined_by_name(self) -> None:
        w = _walsh()
        const = implied_independent_trials(np.array([w[0], np.zeros(8)]))
        assert const["status"] == "undefined" and "constant" in const["reason"]
        singular = implied_independent_trials(np.array([w[0], 2 * w[0], w[1]]))
        assert singular["status"] == "undefined" and "positive-definite" in singular["reason"]
        assert implied_independent_trials(w[:1])["status"] == "undefined"


def _synthetic_series(seed: int = 5, n_dates: int = 80) -> list[ConfigSeries]:
    rng = np.random.default_rng(seed)
    days = [(date(2020, 1, 1) + timedelta(days=i)).isoformat() for i in range(n_dates)]
    out = []
    for ch, grid in (("lgbm", lgbm.grid()), ("lstm", lstm.grid())):
        for h in ("h30", "h120", "hF"):
            for k, cfg in enumerate(grid):
                cid = (lgbm if ch == "lgbm" else lstm).config_id(cfg)
                keep = days[k % 3:]  # some configurations have no rows on the first dates
                daily = {d: float(rng.normal(0.02, 1.0)) for d in keep}
                out.append(ConfigSeries(ch, h, cid, cfg, daily, {"split12": 0.0}))
    return out


class TestTrainingAccounting:
    def test_dsr_and_pbo_by_hand(self) -> None:
        series = _synthetic_series()
        selected = {f"{s.challenger}_{s.horizon}": {"config": s.config}
                    for s in series if s.config in (lgbm.grid()[3], lstm.grid()[1])}
        counts = {"candidate_leaves": 11, "pretest_survivors": 4}
        got = training_accounting(series, selected, counts)
        dates, matrix = aligned_matrix(series)
        assert matrix.shape == (36, 80) and matrix[1, 0] == 0.0  # zero-filled (RA-2)
        stats = [moments(list(r)) for r in matrix]
        var = statistics.pvariance([s["sharpe"] for s in stats])
        assert got["sharpe_variance_over_configurations"] == var
        i = next(k for k, s in enumerate(series)
                 if s.challenger == "lgbm" and s.horizon == "h120" and s.config == lgbm.grid()[3])
        sel = got["selected"]["lgbm_h120"]
        for name, n in (("configurations", 36.0), ("full_search", 51.0)):
            want = deflated_sharpe_ratio(stats[i]["sharpe"], stats[i]["n"], n, var,
                                         stats[i]["skew"], stats[i]["kurtosis"])
            assert sel["dsr"][name]["deflated_sharpe_ratio"] == want["deflated_sharpe_ratio"]
        n_hat = got["implied_independent_trials"]["n_hat"]
        corr = np.corrcoef(matrix)
        assert n_hat == pytest.approx((corr.sum() - 36) / (36 * 35) * (1 - 36) + 36, rel=1e-12)
        want = deflated_sharpe_ratio(stats[i]["sharpe"], stats[i]["n"], n_hat, var,
                                     stats[i]["skew"], stats[i]["kurtosis"])
        assert sel["dsr"]["implied_independent"]["deflated_sharpe_ratio"] == pytest.approx(
            want["deflated_sharpe_ratio"], rel=1e-12)
        blocks = [[sum(r[b * 10:(b + 1) * 10]) for b in range(8)] for r in matrix]
        assert got["pbo"]["pbo"] == probability_of_backtest_overfitting(blocks, 8).pbo
        assert got["pbo"]["n_splits"] == 70 and got["pbo"]["days_left_out"] == 0
        assert set(got["selected"]) == set(selected) and len(selected) == 6
        assert got["n_configurations"] == N_CONFIGURATIONS == 36

    def test_pbo_leaves_out_the_remainder_dates_as_d1_does(self) -> None:
        m = np.random.default_rng(1).normal(size=(3, 19))
        got = pbo(m)
        assert got["block_days"] == 2 and got["days_left_out"] == 3
        with pytest.raises(AccountingError, match="cannot form"):
            pbo(m[:, :7])

    def test_a_selected_configuration_not_in_the_ledgers_is_refused(self) -> None:
        series = _synthetic_series()
        with pytest.raises(AccountingError, match="matches 0"):
            training_accounting(series, {"lgbm_h30": {"config": {"num_leaves": 99}}})

    def test_fewer_than_36_configurations_are_refused(self) -> None:
        with pytest.raises(AccountingError, match="35 configurations"):
            training_accounting(_synthetic_series()[:-1], {})

    def test_an_undefined_n_hat_leaves_the_other_counts(self) -> None:
        series = _synthetic_series()
        flat = series[5]
        series[5] = ConfigSeries(flat.challenger, flat.horizon, flat.config_id, flat.config,
                                 {d: 0.0 for d in flat.daily}, flat.split_scores)
        got = training_accounting(series, {"lgbm_h30": {"config": series[0].config}})
        dsr = got["selected"]["lgbm_h30"]["dsr"]
        assert dsr["implied_independent"]["status"] == "undefined"
        assert dsr["configurations"]["status"] == "computed"


def _write_route(route_dir, seed: int = 9) -> dict:  # noqa: ANN001
    selected = {}
    for ch, mod in (("lgbm", lgbm), ("lstm", lstm)):
        for h in ("h30", "h120", "hF"):
            ledger = Ledger(route_dir / "ledger" / f"{ch}_{h}.jsonl")
            for k, cfg in enumerate(mod.grid()):
                for rec in _records(ch, h, cfg, mod.config_id(cfg), seed + k):
                    ledger.append(rec)
            ledger.append({"key": f"{mod.config_id(mod.grid()[0])}|refit", "challenger": ch,
                           "horizon": h, "config": mod.grid()[0], "split": "refit_blocks_1_5"})
            selected[f"{ch}_{h}"] = {"config": mod.grid()[0]}
    return {"selected": selected,
            "trial_counts": {"candidate_leaves": 3, "pretest_survivors": 1}}


class TestFromLedgers:
    def test_the_six_ledgers_give_36_series_and_the_accounting(self, tmp_path) -> None:
        manifest = _write_route(tmp_path)
        assert len(route_series(tmp_path)) == 36
        got = route_training_accounting(tmp_path, manifest)
        assert got["n_dates"] == 30 and got["counts"]["full_search"] == 40.0
        assert json.loads(json.dumps(got))["schema"] == "ml_route_training_accounting/1"

    def test_a_missing_ledger_or_a_broken_chain_is_refused(self, tmp_path) -> None:
        _write_route(tmp_path)
        path = tmp_path / "ledger" / "lstm_hF.jsonl"
        lines = path.read_text(encoding="utf-8").splitlines()
        edited = json.loads(lines[2])
        edited["score"] = 99.0
        lines[2] = json.dumps(edited, sort_keys=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        with pytest.raises(HashChainError):
            route_series(tmp_path)
        path.unlink()
        with pytest.raises(AccountingError, match="lstm_hF.jsonl is missing"):
            route_series(tmp_path)

    def test_an_incomplete_grid_is_refused(self, tmp_path) -> None:
        ledger = Ledger(tmp_path / "ledger" / "lgbm_h30.jsonl")
        cfg = lgbm.grid()[0]
        for rec in _records("lgbm", "h30", cfg, lgbm.config_id(cfg), 1):
            ledger.append(rec)
        with pytest.raises(AccountingError, match="1 configurations, the grid has 8"):
            route_series(tmp_path)


def test_every_block_pair_is_a_split() -> None:
    assert [sp.test_blocks for sp in SPLITS] == list(combinations((1, 2, 3, 4, 5), 2))
