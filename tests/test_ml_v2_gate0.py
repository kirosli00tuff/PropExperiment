"""ml_route_v2.gate0: families A and B, Holm, the pass bar, registration (V2.2b). Synthetic only.

Gate 0's canaries under the decided defaults (V23 item 1: gross mean >= 1.5 c on the top-20%
confident trades, t >= 3, Holm 0.05 with family A, at least 30 trades): pure noise fails; a
planted gross edge well above cost passes; an edge between 1.0 c and 1.5 c fails (bar 1 binds);
an edge in [1.5 c, 2.5 c) passes. The cost gate's side of the [1.5 c, 2.5 c) edge (traded by the
k = 1.5 gate under the gross reading, rejected at every k under the literal net reading) is in
tests/test_ml_v2_leakage.py, canary (c).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import ml_route_v2.gate0 as g0
from ml_route_v2.configs import ConfigLedger
from ml_route_v2.constants import GATE0_COST_MULTIPLE, N_PROGRAM_AT_FREEZE
from ml_route_v2.gate0 import (
    Gate0Rule,
    Gate0Test,
    date_t,
    gate0_b_pooled,
    gate0_b_trades,
    gate0_family_a,
    gate0_family_b,
    gate0_verdict,
    holm,
    p_value,
)
from tests.test_ml_v2_cpcv import FakePanel, make_panel


def _run(panel, tmp_path, name, **kw):
    ledger = ConfigLedger(tmp_path / f"{name}.jsonl")
    a = gate0_family_a(panel, ledger=ledger, admissible=kw.get("admissible"))
    b = gate0_family_b(panel, ledger=ledger, state_dir=tmp_path / name, **kw)
    return ledger, a, b


def test_pure_noise_fails_gate0(tmp_path):
    panel = make_panel(n_dates=300, seed=11, edge=0.0, cost=0.5)
    _, a, b = _run(panel, tmp_path, "noise")
    verdict = gate0_verdict(a + b)
    assert not verdict.passed and verdict.passing == ()
    assert max(t.t for t in b) < 3.0


def test_planted_gross_edge_well_above_cost_passes(tmp_path):
    panel = make_panel(n_dates=300, seed=12, edge=0.5, cost=0.5)
    ledger, a, b = _run(panel, tmp_path, "edge")
    verdict = gate0_verdict(a + b)
    assert verdict.passed
    assert set(verdict.passing) == {t.test_id for t in b}
    for t in b:
        assert t.n_trades == 180  # floor(0.2 x 900) rows of the pair
        assert t.mean >= 1.5 * t.cost_ticks and t.t >= 3.0 and t.p < 1e-6
    s0 = [t for t in a if t.signal == "s0"]
    assert all(t.t > 3.0 and t.ic_spearman > 0.2 and t.gross_ticks_sign > 0 for t in s0)


def test_edge_above_cost_but_below_one_and_a_half_costs_fails(tmp_path):
    # same draw as the passing canary: the six pairs' mean g run 7.95..10.16 ticks
    panel = make_panel(n_dates=300, seed=12, edge=0.5, cost=7.3)
    _, a, b = _run(panel, tmp_path, "sub")
    for t in b:  # the confident quintile clears the cost but not 1.5 x cost
        assert t.cost_ticks < t.mean < 1.5 * t.cost_ticks
        assert t.t >= 3.0
    assert not gate0_verdict(a + b).passed
    assert gate0_verdict(a + b, Gate0Rule(cost_multiple=1.0)).passed  # bar 1 is what binds


def test_edge_between_one_and_a_half_and_two_and_a_half_costs_passes(tmp_path):
    """V23 item 1: Gate 0's bar is a gross mean of 1.5 c, so an edge in [1.5 c, 2.5 c) passes
    (the same draw: mean g 7.95..10.16 ticks against a 4.6-tick round trip, 1.73..2.21 c). Under
    the old literal reading such an edge passed Gate 0 and was then rejected by every cost gate;
    under the gross reading the k = 1.5 gate trades it (tests/test_ml_v2_leakage.py, (c))."""
    panel = make_panel(n_dates=300, seed=12, edge=0.5, cost=4.6)
    _, a, b = _run(panel, tmp_path, "mid")
    for t in b:
        assert GATE0_COST_MULTIPLE * t.cost_ticks <= t.mean < 2.5 * t.cost_ticks
        assert t.t >= 3.0 and t.n_trades >= 30
    verdict = gate0_verdict(a + b)
    assert verdict.passed
    assert set(verdict.passing) == {t.test_id for t in b}


def test_every_test_is_registered_before_it_is_computed(tmp_path, monkeypatch):
    panel = make_panel(n_dates=60, seed=1)
    ledger = ConfigLedger(tmp_path / "l.jsonl")
    seen_a, seen_b = [], []
    real_means, real_fit = g0._per_date_means, g0.fit_model

    def spy_means(days, values):
        seen_a.append(ledger.n_registered("gate0_A"))
        return real_means(days, values)

    def spy_fit(spec, X, y, **kw):
        seen_b.append(ledger.n_registered("gate0_B"))
        return real_fit(spec, X, y, **kw)

    monkeypatch.setattr(g0, "_per_date_means", spy_means)
    monkeypatch.setattr(g0, "fit_model", spy_fit)
    a = gate0_family_a(panel, ledger=ledger)
    assert min(seen_a) == 9
    seen_a.clear()
    b = gate0_family_b(panel, ledger=ledger, state_dir=tmp_path / "s")
    assert seen_b and min(seen_b) == 6
    assert len(seen_b) == 3 * 15  # one ridge per (horizon, outer split)
    verdict = gate0_verdict(a + b)
    assert verdict.n_tests == len(a) + len(b) == 9 + 6
    assert ledger.n_registered("gate0_A") == 9 and ledger.n_registered("gate0_B") == 6
    assert ledger.n_total() == N_PROGRAM_AT_FREEZE + 15
    assert len(verdict.holm) == 15
    assert len(gate0_verdict(a + b, Gate0Rule(holm_includes_a=False)).holm) == 6


def test_family_b_resumes_from_cached_oof_predictions(tmp_path, monkeypatch):
    panel = make_panel(n_dates=60, seed=3, edge=0.3)
    first = gate0_family_b(panel, ledger=ConfigLedger(tmp_path / "l.jsonl"),
                           state_dir=tmp_path / "s")

    def boom(*a, **k):
        raise AssertionError("refit on resume")

    monkeypatch.setattr(g0, "fit_model", boom)
    again = gate0_family_b(panel, ledger=ConfigLedger(tmp_path / "l.jsonl"),
                           state_dir=tmp_path / "s")
    assert again == first
    with pytest.raises(g0.StateMismatchError):
        gate0_family_b(make_panel(n_dates=60, seed=4), ledger=ConfigLedger(tmp_path / "m.jsonl"),
                       state_dir=tmp_path / "s")


def test_family_b_admissible_pairs_and_trade_rule(tmp_path):
    panel = make_panel(n_dates=60, seed=5, edge=0.4, roots=("AA", "BB", "CC"))
    adm = {("AA", "h60"), ("CC", "hF")}
    ledger = ConfigLedger(tmp_path / "l.jsonl")
    b = gate0_family_b(panel, ledger=ledger, state_dir=tmp_path / "s", admissible=adm)
    assert sorted((t.root, t.horizon) for t in b) == sorted(adm)
    trades = gate0_b_trades(panel, ledger=ledger, state_dir=tmp_path / "s", admissible=adm)
    for (r, h), sub in trades.groupby(["root", "horizon"]):
        assert len(sub) == int(np.floor(0.2 * 180 + 1e-9))  # 60 dates x 3 decisions
        gross = panel.frame.set_index(["root", "decision_ts_ns"])[f"y_gross_{h}"]
        y = gross.loc[list(zip(sub["root"], sub["decision_ts_ns"], strict=True))].to_numpy()
        np.testing.assert_allclose(sub["g_ticks"].to_numpy(),
                                   np.sign(sub["r_hat"].to_numpy()) * y)
        assert (sub["r_hat"].abs().min() > 0) and (r, h) in adm
    assert set(trades["side"]) <= {-1, 1}
    pooled = gate0_b_pooled(trades)
    assert pooled["n_trades"] == len(trades)
    assert pooled["mean_g_ticks"] == pytest.approx(trades["g_ticks"].mean())


def test_top_fraction_reads_predictions_only_with_stable_ties():
    r_hat = np.array([0.1, -0.5, 0.3, 0.0, 0.9, -0.2, 0.4, 0.05, -0.6, 0.7])
    assert g0._top_trades(r_hat, 0.2).tolist() == [4, 9]
    assert g0._top_trades(r_hat, 0.3).tolist() == [4, 8, 9]
    assert g0._top_trades(np.array([1.0, -1.0, 1.0, 1.0, 0.5]), 0.4).tolist() == [0, 1]
    assert g0._top_trades(np.array([0.0, 0.0, 3.0, 0.0, 0.0]), 0.4).tolist() == [2]


def test_family_a_statistic_hand_computed(tmp_path):
    frame = pd.DataFrame({
        "root": ["AA"] * 6,
        "trade_date": pd.to_datetime(["2020-01-06"] * 2 + ["2020-01-07"] * 2
                                     + ["2020-01-08"] * 2),
        "z_s0": [1.0, 2.0, 1.0, -1.0, 0.0, 1.0],
        "y_norm_h60": [1.0, 1.0, 2.0, 0.0, 5.0, 3.0],
        "ok_h60": [True] * 6,
    })
    frame["y_gross_h60"] = frame["y_norm_h60"] * 10.0
    panel = FakePanel(frame, ("z_s0",), ("s0",), ("h60",), np.zeros(6))
    (t,) = gate0_family_a(panel, ledger=ConfigLedger(tmp_path / "l.jsonl"))
    # m_d = [1.5, 1.0, 1.5]: mean 4/3, sd sqrt(1/12), t = (4/3) / (sqrt(1/12) / sqrt(3)) = 8
    assert t.n_dates == 3 and t.n_obs == 6
    assert t.mean == pytest.approx(4 / 3) and t.t == pytest.approx(8.0)
    from scipy.stats import t as student_t
    assert t.p == pytest.approx(2 * student_t.sf(8.0, 2))
    assert t.gross_ticks_sign == pytest.approx(14.0)
    assert t.ic_spearman == pytest.approx(frame["z_s0"].corr(frame["y_norm_h60"],
                                                             method="spearman"))


def _t(test_id, family, p, **kw):
    base = dict(signal=None, root=None, horizon="h60", n_dates=100, n_obs=100, mean=10.0,
                t=5.0, cost_ticks=1.0, n_trades=50)
    base.update(kw)
    return Gate0Test(test_id=test_id, family=family, p=p, **base)


def test_holm_step_down_hand_computed():
    rows = holm([_t("a", "A", 0.01), _t("b", "B", 0.02), _t("c", "B", 0.04)], 0.05)
    assert [r["rejected"] for r in rows] == [True, True, True]
    assert [r["threshold"] for r in rows] == pytest.approx([0.05 / 3, 0.05 / 2, 0.05])
    rows = holm([_t("a", "A", 0.01), _t("b", "B", 0.03), _t("c", "B", 0.04)], 0.05)
    assert [r["rejected"] for r in rows] == [True, False, False]


def test_verdict_bars_each_bind():
    good = _t("b1", "B", 1e-8)
    assert gate0_verdict([good]).passed
    assert not gate0_verdict([_t("b1", "B", 1e-8, mean=1.4, cost_ticks=1.0)]).passed
    assert not gate0_verdict([_t("b1", "B", 1e-8, t=2.99)]).passed
    assert not gate0_verdict([_t("b1", "B", 1e-8, n_trades=29)]).passed
    assert not gate0_verdict([_t("b1", "B", 0.2)]).passed
    many_a = [_t(f"a{i}", "A", 0.01) for i in range(50)]
    # 51 tests: B's p = 0.004 is not below 0.05 / 51 when A counts, and passes when it does not
    assert not gate0_verdict(many_a + [_t("b1", "B", 0.004)]).passed
    assert gate0_verdict(many_a + [_t("b1", "B", 0.004)], Gate0Rule(holm_includes_a=False)).passed
    assert not gate0_verdict([_t("a1", "A", 1e-9)]).passed  # family A alone never passes
    with pytest.raises(g0.Gate0Error):
        gate0_verdict([good, good])


def test_date_t_and_p_value_helpers():
    assert date_t(np.array([1.0, 1.0, 1.0])) == np.inf
    assert np.isnan(date_t(np.array([1.0])))
    assert p_value(float("nan"), 10, two_sided=True) == 1.0
    assert p_value(3.0, 1000, two_sided=False) == pytest.approx(0.00138, rel=0.05)
