"""Tests of the Stage E.19 grid runner and aggregator (prop_econ/grid.py, prop_econ/report.py)."""

from __future__ import annotations

import json
import math

import numpy as np
import pytest

from prop_econ import grid
from prop_econ.assemble import assemble_cycles, fee_terms
from prop_econ.funnel import ATTEMPT_PASS, XFA_BREACH, XFA_HORIZON
from prop_econ.grid import (
    HEADLINE,
    Job,
    Settings,
    ShockConfig,
    Wallet,
    api_periods_at,
    api_periods_cycle,
    cycle_metrics,
    draw_seed,
    enumerate_jobs,
    group_tasks,
    run_task,
    shock_seed,
)
from prop_econ.report import break_even, select_optimum
from prop_econ.rules import size_rules
from prop_econ.vec import AttemptPool, XfaPool

TINY = Settings(n_paths=48, horizon=30, max_payouts=8, attempt_cap=4, n_cycles=40, n_reps=12,
                purchase_cap=12, trace_rows=2)


# --------------------------------------------------------------------------- enumeration ----
def test_job_enumeration_counts():
    jobs = enumerate_jobs()
    fams: dict[str, int] = {}
    for j in jobs:
        fams[j.family] = fams.get(j.family, 0) + 1
    assert len(jobs) == 780
    assert fams["headline"] == 3 * 2 * 8 * 7  # size x dll x edge x f
    assert fams["tail_normal"] == 3 * 8 * 5
    assert fams["direction_long"] == 15 and fams["cost_wall"] == 30
    assert all(fams[f"integer_{p}"] == 30 for p in grid.PRODUCTS)
    assert fams["keep_d"] == 45 and fams["callup1"] == fams["callup3"] == 30
    assert fams["scaling_upper"] == fams["ccons_inclusive"] == 12
    assert sum(j.campaigns for j in jobs) == 3 * 2 * 8 * 5
    assert len({j.id for j in jobs}) == len(jobs)
    # sensitivities: DLL off only; Back2Funded on only in the headline
    assert all(not j.dll for j in jobs if j.family != "headline")
    assert all(j.b2f_set == (False,) for j in jobs if not j.is_headline)


def test_tasks_share_shocks_and_cover_every_job():
    jobs = enumerate_jobs()
    tasks = group_tasks(jobs)
    assert sum(len(t) for t in tasks) == len(jobs)
    assert all(len({j.task_key for j in t}) == 1 for t in tasks)
    assert len(tasks) == len({j.task_key for j in jobs})


def test_edge_policy_fields():
    assert grid.edge_policy_fields("zero_k3") == {"edge": "zero", "sharpe": 0.0, "k": 3}
    assert grid.edge_policy_fields("S0.15") == {"edge": "sharpe", "sharpe": 0.15, "k": 1}
    with pytest.raises(ValueError):
        grid.edge_policy_fields("S")


# -------------------------------------------------------------------------------- seeds ----
def test_seeds_depend_only_on_phase_size_and_shock_config():
    s = Settings()
    a = shock_seed(s, "attempt", "50K", HEADLINE)
    assert a == shock_seed(Settings(n_cycles=7), "attempt", "50K", HEADLINE)
    assert a != shock_seed(s, "xfa", "50K", HEADLINE)
    assert a != shock_seed(s, "attempt", "100K", HEADLINE)
    for other in (ShockConfig(tail="normal"), ShockConfig(direction="long"),
                  ShockConfig(cost="wall"), ShockConfig(products="NQ", mode="integer")):
        assert a != shock_seed(s, "attempt", "50K", other)
    assert draw_seed(s, "cycle", "50K", HEADLINE) != draw_seed(s, "campaign", "50K", HEADLINE)


def test_jobs_differing_in_f_edge_dll_variant_get_identical_seeds(tmp_path):
    jobs = [Job(HEADLINE, "50K", "zero_k1", 0.10, False, "base", "headline"),
            Job(HEADLINE, "50K", "zero_k1", 0.25, True, "base", "headline"),
            Job(HEADLINE, "50K", "zero_k1", 0.10, False, "callup1", "callup1")]
    run_task(jobs, TINY, tmp_path)
    jobs2 = [Job(HEADLINE, "50K", "S0.5", 0.10, False, "base", "headline")]
    run_task(jobs2, TINY, tmp_path)
    seeds = [json.loads((tmp_path / f"{j.id}.json").read_text())["seeds"] for j in jobs + jobs2]
    assert all(sd == seeds[0] for sd in seeds)


# ------------------------------------------------------------------------ resumability ----
def test_run_task_is_resumable(tmp_path):
    jobs = [Job(HEADLINE, "100K", "S0.5", 0.05, False, "base", "headline"),
            Job(HEADLINE, "100K", "S0.5", 0.35, False, "base", "headline")]
    done = run_task(jobs, TINY, tmp_path)
    assert [d[0] for d in done] == [j.id for j in jobs]
    for j in jobs:
        doc = json.loads((tmp_path / f"{j.id}.json").read_text())
        assert doc["complete"] and (tmp_path / f"{j.id}.npz").exists()
        # headline: both payout paths x both pricing x B2F off / on
        assert len(doc["records"]) == 8
        has_campaigns = [("campaigns" in r) for r in doc["records"]]
        assert any(has_campaigns) == (j.f in grid.F_BAND)
    assert run_task(jobs, TINY, tmp_path) == []
    # a truncated JSON is redone, the other job is skipped
    (tmp_path / f"{jobs[1].id}.json").write_text('{"complete": tr')
    assert [d[0] for d in run_task(jobs, TINY, tmp_path)] == [jobs[1].id]
    # a missing nets file makes a headline job incomplete
    (tmp_path / f"{jobs[0].id}.npz").unlink()
    assert [d[0] for d in run_task(jobs, TINY, tmp_path)] == [jobs[0].id]
    # other settings -> other fingerprint -> rerun
    other = Settings(**{**TINY.__dict__, "n_cycles": 41})
    assert len(run_task(jobs, other, tmp_path)) == 2


def test_rerun_reproduces_results(tmp_path):
    job = Job(ShockConfig(tail="normal"), "50K", "zero_k3", 0.15, False, "base", "tail_normal")
    run_task([job], TINY, tmp_path / "a")
    run_task([job], TINY, tmp_path / "b")
    a = json.loads((tmp_path / "a" / f"{job.id}.json").read_text())
    b = json.loads((tmp_path / "b" / f"{job.id}.json").read_text())
    assert a["records"] == b["records"] and a["xfa"] == b["xfa"]
    assert len(a["records"]) == 4  # sensitivities: B2F off only
    assert "eff_sharpe" in a and a["eff_sharpe"]["pooled"]["risk_weighted"] < 0


# ---------------------------------------------------------------------------- derived ----
def test_break_even_interpolation():
    s = (0.0, 0.15, 0.3, 0.5, 0.75, 1.0)
    assert break_even(s, [-100, -50, 50, 100, 200, 300]) == pytest.approx(0.225)
    assert break_even(s, [10, 20, 30, 40, 50, 60]) == "< 0"
    assert break_even(s, [-10, -9, -8, -7, -6, -1]) == "> 1"
    assert break_even(s, [0, 5, 6, 7, 8, 9]) == 0.0
    assert break_even(s, [-100, -50, 0, 100, 200, 300]) == pytest.approx(0.3)
    # first upward crossing when the curve is not monotone
    assert break_even(s, [-10, 10, -5, 5, 6, 7]) == pytest.approx(0.075)


def test_select_optimum_with_paired_se():
    rng = np.random.default_rng(1)
    common = rng.normal(0, 100, 1000)
    nets = {0.05: common + 1.0, 0.10: common + 3.0, 0.15: common + 2.0 + rng.normal(0, 1, 1000)}
    out = select_optimum((0.05, 0.10, 0.15), nets)
    assert out["best_f"] == 0.10 and out["runner_up_f"] == 0.15
    assert out["mean"] == pytest.approx(np.mean(nets[0.10]))
    assert out["se"] == pytest.approx(np.std(nets[0.10], ddof=1) / math.sqrt(1000))
    d = nets[0.10] - nets[0.15]
    assert out["gap"] == pytest.approx(d.mean())
    assert out["gap_paired_se"] == pytest.approx(np.std(d, ddof=1) / math.sqrt(1000))
    assert out["gap_paired_se"] < 0.1 * out["se"]  # pairing removes the common noise


def test_select_optimum_tie_takes_the_smaller_f():
    x = np.array([1.0, 2.0, 3.0])
    out = select_optimum((0.05, 0.10), {0.05: x, 0.10: x.copy()})
    assert out["best_f"] == 0.05 and out["gap"] == 0.0


# ----------------------------------------------------------------------------- wallet ----
def test_api_periods():
    assert api_periods_cycle(np.array([1, 21, 22, 42, 43]), 21).tolist() == [1, 1, 2, 2, 3]
    assert api_periods_at(np.array([0, 20, 21, 42]), 21).tolist() == [1, 1, 2, 3]


def _wallet() -> Wallet:
    return Wallet(api_usd=14.5, period_days=21, payout_fee_usd=30.0, split=0.9, close_frac=0.5,
                  close_cap_usd=5000.0, start_balance=0.0, copies=5)


def test_wallet_accounting_on_a_hand_cycle():
    rules = size_rules(grid.headline_book(), "50K")
    terms = fee_terms(rules, pricing_path="standard", dll_chosen=False, b2f_on=False,
                      attempt_cap=3)
    attempts = AttemptPool(passed=np.array([True]), length=np.array([5], dtype=np.int32),
                           reason=np.array([ATTEMPT_PASS], dtype=np.int8))
    days = np.array([[10, 30, -1], [-1, -1, -1]], dtype=np.int32)
    gross = np.array([[1000.0, 500.0, 0.0], [0.0, 0.0, 0.0]])
    xfas = XfaPool(payout_days=days, payout_gross=gross,
                   n_payouts=np.array([2, 0], dtype=np.int32), total_gross=np.array([1500., 0.]),
                   first_payout_day=np.array([10, -1], dtype=np.int32),
                   end_day=np.array([40, 3], dtype=np.int32),
                   end_reason=np.array([XFA_HORIZON, XFA_BREACH], dtype=np.int8),
                   end_balance=np.array([4000.0, -2000.0]), overflow=np.zeros(2, dtype=bool))
    att_idx = np.zeros((2, 3), dtype=np.int64)
    xfa_idx = np.array([[0, 0, 0], [1, 1, 1]], dtype=np.int64)
    batch = assemble_cycles(att_idx, xfa_idx, attempts, xfas, terms)
    rec, net = cycle_metrics(batch, xfas, _wallet(), attempts, att_idx)
    # cycle 0: pass at day 5, XFA 5..45: 46 days... end = 45 -> 3 API periods
    assert batch.end.tolist() == [45, 8]
    api = 14.5 * np.array([3, 1])
    fees = terms.monthly_usd + terms.activation_usd
    assert net.tolist() == pytest.approx([0.9 * 1500 - fees - api[0], -fees - api[1]])
    assert rec["mean_fees_by_type"]["api"] == pytest.approx(api.mean())
    assert rec["net_ex_api"]["mean"] == pytest.approx(np.mean(net + api))
    assert rec["post_hoc"]["payout_fee_ach"]["mean"] == pytest.approx(np.mean(net) - 30.0)
    close = 0.9 * min(0.5 * 4000.0, 5000.0)
    assert rec["post_hoc"]["voluntary_close"]["mean"] == pytest.approx(np.mean(net) + close / 2)
    assert rec["post_hoc"]["copy_traded"]["mean"] == pytest.approx(np.mean(5 * (net + api) - api))
    assert rec["p_no_payout"] == 0.5 and rec["mean_days_to_first_payout"] == 15.0
    assert rec["mean_purchases"] == 1.0
    ch = rec["churn"]
    assert ch["combine_days_mean"] == 5.0 and ch["combine_breaches_mean"] == 0.0
    assert ch["xfa_days_mean"] == (40 + 3) / 2 and ch["xfa_breaches_mean"] == 0.5


def test_wallet_values_come_from_the_rules_file():
    book = grid.headline_book()
    w = grid.wallet_from(book, size_rules(book, "50K"))
    assert w.api_usd == book.value("global.api_access_monthly_usd")
    assert w.payout_fee_usd == book.value("global.payout_fee_usd.ach")
    assert w.period_days == 21 and w.copies == book.value("global.max_active_xfas")


def test_churn_counts_breaches_and_window_purchases():
    rules = size_rules(grid.headline_book(), "50K")
    terms = fee_terms(rules, pricing_path="standard", dll_chosen=False, b2f_on=False,
                      attempt_cap=4)
    # row 0 breaches after 10 days, row 1 passes after 30 days
    attempts = AttemptPool(passed=np.array([False, True]),
                           length=np.array([10, 30], dtype=np.int32),
                           reason=np.array([0, ATTEMPT_PASS], dtype=np.int8))
    xfas = XfaPool(payout_days=np.full((1, 2), -1, dtype=np.int32), payout_gross=np.zeros((1, 2)),
                   n_payouts=np.zeros(1, dtype=np.int32), total_gross=np.zeros(1),
                   first_payout_day=np.array([-1], dtype=np.int32),
                   end_day=np.array([200], dtype=np.int32),
                   end_reason=np.array([XFA_BREACH], dtype=np.int8),
                   end_balance=np.zeros(1), overflow=np.zeros(1, dtype=bool))
    att_idx = np.array([[0, 0, 1, 1]] * 3, dtype=np.int64)  # two breaches, then a pass
    xfa_idx = np.zeros((3, 3), dtype=np.int64)
    batch = assemble_cycles(att_idx, xfa_idx, attempts, xfas, terms)
    ch = grid.churn_metrics(batch, xfas, attempts, att_idx)
    assert batch.end.tolist() == [250, 250, 250]
    assert ch["combine_breaches_mean"] == 2.0 and ch["combine_days_mean"] == 50.0
    assert ch["xfa_breaches_mean"] == 1.0 and ch["xfa_days_mean"] == 200.0
    # slots: cycles 0+1 cover 500 >= 252 days -> one complete slot; cycle 2 alone is dropped
    win = grid.slot_window_purchases(batch, 252)
    fee_t = batch.fee_time[(batch.fee_cycle <= 1) & np.isin(batch.fee_kind, (0, 1, 2))]
    off = np.where(batch.fee_cycle[(batch.fee_cycle <= 1)
                                   & np.isin(batch.fee_kind, (0, 1, 2))] == 1, 250, 0)
    assert win.tolist() == [int(((fee_t + off) < 252).sum())]


# ----------------------------------------------------------------------- report (RR-1) ----
def test_churn_label_thresholds():
    from prop_econ.report import churn_label

    assert churn_label(2.0) == "low" and churn_label(2.01) == "medium"
    assert churn_label(4.0) == "medium" and churn_label(4.01) == "high"
    assert churn_label(None) is None


def test_report_builds_on_a_tiny_partial_grid(tmp_path):
    from prop_econ import report

    jobs = [Job(HEADLINE, "50K", e, f, False, "base", "headline")
            for e in ("zero_k1", "S0.5") for f in grid.F_ALL]
    for e in ("zero_k1", "S0.5"):
        run_task([j for j in jobs if j.edge == e], TINY, tmp_path)
    res = report.build(tmp_path)
    assert res["n_jobs_found"] == len(jobs)
    assert len(res["missing"]) == len(enumerate_jobs()) - len(jobs)
    rec = next(r for r in res["records"] if not r["b2f"])
    rate = 21 * rec["mean_purchases"] / rec["churn_combine_days_mean"]
    assert rec["purchases_per_21_combine_days"] == pytest.approx(rate)
    assert rec["churn_label"] == report.churn_label(rate)
    assert rec["forfeiture_net"] == -rec["mean_fees_total"]
    opt = [r for r in res["derived"]["optimum_band"] if r["size"] == "50K" and not r["dll"]
           and r["edge"] in ("zero_k1", "S0.5")]
    assert opt and all(not r.get("missing") and r["best_f"] in grid.F_BAND for r in opt)
    md = report.tables(res)
    for t in ("## T1", "## T2", "## T3", "## T4", "## T5", "## T6", "## T7", "## T8"):
        assert t in md
    json.dumps(res, allow_nan=False, default=list)
