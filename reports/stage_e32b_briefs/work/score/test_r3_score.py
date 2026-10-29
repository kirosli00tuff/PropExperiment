"""Unit tests for r3_score (spec 8.3): Q4 to Q7 boundaries (to the higher score) and unknown handling, K_eff for
pools, the gates, C, the tie chain and the R4 selection. Inputs are synthetic."""
import copy
import json
from fractions import Fraction as F

import make_fixture
import pytest
import r3_score as R
from s32b_common import InputError, SpecHashError, to_jsonable


@pytest.mark.parametrize("c_f,sig,score", [(1, 40, 4), ("1.000001", 40, 3), (2, 40, 3), (4, 40, 2), (8, 40, 1),
                                           ("8.000001", 40, 0)])
def test_q4_boundaries(c_f, sig, score):
    assert R.q4_score(F(c_f), F(sig))[0] == score


@pytest.mark.parametrize("k,score", [(3480, 4), (3479, 3), (870, 3), (869, 2), (F("217.5"), 2), (217, 1),
                                     (F("54.375"), 1), (54, 0)])
def test_q5_boundaries_exact(k, score):
    # SR80 = 0.1: q = 0.1 sqrt(870 / K); K = 3480 gives q = 0.05 exactly, 870 gives 0.10, 217.5 gives 0.20 ...
    assert R.q5_score(F("0.1"), F(k))[0] == score


def test_n_cap_and_g():
    assert R.n_cap("OC", None) == 1 and R.n_cap("15", F(390)) == 20 and R.n_cap("60", F(390)) == 6
    assert R.n_cap("240", F(290)) == 1
    assert R.g_value(F(2), F(40), F("0.1"), 4) == pytest.approx(0.05 + 0.05)
    assert R.g_value(F(2), F(40), F("0.1"), 0) == float("inf")


def test_k_eff_and_pool_rho():
    assert R.k_eff(F(800), 2, F("0.9")) == F(800) / F("1.9")
    rho, notes = R.pool_rho([("MCL", "crude"), ("QM", "crude")], {})
    assert rho == F("0.5") and not notes
    rho, _ = R.pool_rho([("MCL", "crude"), ("MNQ", "equity")], {})
    assert rho == F("0.3")
    rho, notes = R.pool_rho([("MCL", "crude"), ("QM", "crude"), ("MNQ", "equity")],
                            {"QM|MCL": {"value": 0.9}})
    assert rho == (F("0.9") + F("0.3") + F("0.3")) / 3 and len(notes) == 1


def mem(**kw):
    base = {"code": "MCL", "sigma_hc_ticks": F(40), "tick_value_usd": F(10), "dll_usd": F(600), "mll_usd": F(2000),
            "payout_threshold_usd": F(100), "n_per_day": F(1), "news_stop_events_per_week": F(0)}
    return {**base, **kw}


@pytest.mark.parametrize("dll,ded", [(599, 2), (600, 1), (601, 1), (1199, 1), (1200, 0)])
def test_q6_prop_dll_boundaries(dll, ded):
    # sigma v = 40 x 10 = 400: ratio 1.5 at 600 (milder deduction 1), 3 at 1200 (no deduction)
    assert R.q6_prop(mem(dll_usd=F(dll)))[1]["dll"] == ded


def test_q6_prop_payout_news_unknowns_and_no_dll():
    assert R.q6_prop(mem(payout_threshold_usd=F(400)))[1]["payout"] == 0   # = sqrt(1) x 400: not exceeding
    assert R.q6_prop(mem(payout_threshold_usd=F(401)))[1]["payout"] == 1
    assert R.q6_prop(mem(payout_threshold_usd=F(800), n_per_day=F(4)))[1]["payout"] == 0   # sqrt(4) x 400
    assert R.q6_prop(mem(news_stop_events_per_week=F(2)))[1]["news"] == 1
    assert R.q6_prop(mem(news_stop_events_per_week=F(1)))[1]["news"] == 0
    s, deds, notes = R.q6_prop(mem(dll_usd=None, payout_threshold_usd=None, news_stop_events_per_week=None))
    assert deds == {"dll": 2, "payout": 1, "news": 1} and s == 0 and len(notes) == 3
    assert R.q6_prop(mem(dll_usd="none", mll_usd=F(1200)))[1]["dll"] == 0


def test_q6_own_broker_boundaries():
    m = mem(initial_margin_usd=F(6000), sigma_day_ticks=F(12))           # 12 x 10 = 120 = 2% of 6,000
    assert R.q6_own(m, F(6000))[0] == 4
    assert R.q6_own(mem(initial_margin_usd=F(6001), sigma_day_ticks=F("12.1")), F(6000))[0] == 1
    s, deds, notes = R.q6_own(mem(initial_margin_usd=None, sigma_day_ticks=None), F(6000))
    assert s == 1 and len(notes) == 2


@pytest.mark.parametrize("data,score", [
    ({"discovery_cost_usd": 50, "all_data_cost_usd": 200, "clean_test_window_months": 36}, 4),
    ({"discovery_cost_usd": 50.01, "all_data_cost_usd": 200, "clean_test_window_months": 36}, 3),
    ({"discovery_cost_usd": 0, "all_data_cost_usd": 200.01, "clean_test_window_months": 36}, 3),
    ({"discovery_cost_usd": 0, "all_data_cost_usd": 0, "clean_test_window_months": 35}, 3),
    ({"discovery_cost_usd": 0, "all_data_cost_usd": 0, "clean_test_window_months": 24}, 3),
    ({"discovery_cost_usd": 0, "all_data_cost_usd": 0, "clean_test_window_months": 23}, 2),
    ({"discovery_cost_usd": 99, "all_data_cost_usd": 999, "clean_test_window_months": 0}, 0),
    ({}, 0),
])
def test_q7_boundaries_and_unknowns(data, score):
    assert R.q7_score(data)[0] == score


def run(doc):
    return R.run_r3(doc)


def test_fixture_run_and_gates():
    out = run(make_fixture.combos_doc())
    by = {r["id"]: r for r in out["combinations"]}
    assert by["C05"]["status"] == "excluded" and "Q3 = 0" in by["C05"]["gate_reasons"][0]
    assert by["C06"]["status"] == "excluded" and "news_window_covers_event_trade" in by["C06"]["gate_reasons"][0]
    c01 = by["C01"]
    w = R.W_C
    assert c01["C"] == sum(w[k] * c01[k] for k in w)
    assert out["capital_ceiling_usd"] == 6000 and out["capital_ceiling_u"]
    assert any("6,000 (u)" in n for n in by["C02"]["u"])
    json.dumps(to_jsonable(out))


def test_pool_uses_k_eff_worst_q4_and_worst_q6():
    out = run(make_fixture.combos_doc())
    c03 = next(r for r in out["combinations"] if r["id"] == "C03")
    assert c03["K_used"] == F(800) / F("1.9") and c03["rho"] == F("0.9")
    x_mcl, x_qm = F("2.3") / 44, F("1.8") / F("17.6")
    assert c03["x"] == max(x_mcl, x_qm) and c03["Q4"] == 1
    assert c03["Q6"] == min(v["Q6"] for v in c03["Q6_by_member"].values())


def test_pool_gated_if_a_member_is():
    doc = make_fixture.combos_doc()
    doc["combinations"][2]["members"][1]["gate"] = {"holds_past_flat_by_close": True}
    c03 = next(r for r in run(doc)["combinations"] if r["id"] == "C03")
    assert c03["status"] == "excluded" and c03["gate_reasons"] == ["QM: holds_past_flat_by_close"]


def test_q2_cap_when_unverified():
    doc = make_fixture.combos_doc()
    doc["combinations"][0]["Q2"] = {"value": 4, "unverified": True}
    doc["combinations"][1]["Q2"] = {"value": 0, "unverified": True}
    by = {r["id"]: r for r in run(doc)["combinations"]}
    assert by["C01"]["Q2"] == 2 and by["C02"]["Q2"] == 1


def _tie_doc():
    doc = make_fixture.combos_doc()
    base = copy.deepcopy(doc["combinations"][0])
    a = {**copy.deepcopy(base), "id": "T1", "family": "fam_a"}
    b = {**copy.deepcopy(base), "id": "T2", "family": "fam_b", "Q1": {"value": 4}, "Q2": {"value": 0}}
    doc["combinations"] = [a, b]
    return doc


def test_ties_higher_q1_first_then_g():
    out = run(_tie_doc())
    t1, t2 = out["combinations"][0], out["combinations"][1]
    assert t1["C_rounded"] == t2["C_rounded"] and t1["id"] == "T2"     # 0.2 x 1 = 0.1 x 2: tie, higher Q1 first
    assert out["ties"][0]["steps"][0]["decided_by"] == "Q1"
    doc = _tie_doc()
    doc["combinations"][1]["Q1"], doc["combinations"][1]["Q2"] = {"value": 3}, {"value": 2}
    doc["combinations"][1]["members"][0]["c_f_ticks"] = 2.25                # same Q4 band (x 0.051), lower G
    out = run(doc)
    assert out["combinations"][0]["id"] == "T2" and out["ties"][0]["steps"][0]["decided_by"] == "G(h_c)"


def test_r4_distinct_best_weak_and_own_broker():
    out = run(make_fixture.combos_doc())
    cands = out["R4"]["candidates"]
    keys = [(c["product_or_pool"], c["family"]) for c in cands]
    assert len(keys) == len(set(keys))
    mcl = next(c for c in cands if c["product_or_pool"] == "MCL")
    assert mcl["best_venue"] == "ibkr"                                    # best C for (MCL, eia_drift)
    prop = out["R4_prop_only"]["candidates"]
    assert all(c["best_venue"] != "ibkr" for c in prop)
    assert out["best_own_broker"]["id"] == "C02"
    assert all(c["weak"] == (c["C"] < 2) for c in cands)
    doc = make_fixture.combos_doc()
    for c in doc["combinations"]:
        c["Q1"], c["Q2"], c["Q3"] = {"value": 1}, {"value": 0}, {"value": 1}
        c["data"] = {}
    out = run(doc)
    assert out["R4"]["fewer_than_3_reach_2"] and all(c["weak"] for c in out["R4"]["candidates"])


def test_validation_and_refusals(tmp_path):
    doc = make_fixture.combos_doc()
    with pytest.raises(SpecHashError):
        R.run_r3({**doc, "spec_sha256": "0" * 64})
    bad = tmp_path / "spec.md"
    bad.write_text("x")
    with pytest.raises(SpecHashError):
        R.run_r3(doc, spec_path=bad)
    for mutate in (lambda d: d.pop("sr80_test"),
                   lambda d: d["combinations"][0].update(venue="ftmo"),
                   lambda d: d["combinations"][0].update(h_c="5"),
                   lambda d: d["combinations"][0].pop("Q1"),
                   lambda d: d["combinations"][0]["members"][0].pop("K_test"),
                   lambda d: d["combinations"][1].update(id="C01")):
        d = make_fixture.combos_doc()
        mutate(d)
        with pytest.raises(InputError):
            R.run_r3(d)


def test_cli(tmp_path):
    paths = make_fixture.write_all(str(tmp_path / "fx"))
    assert R.main(["--combos", paths["combos"], "--out", str(tmp_path / "r3.json")]) == 0
    assert json.loads((tmp_path / "r3.json").read_text())["R4"]["candidates"]
    bad = tmp_path / "spec.md"
    bad.write_text("x")
    assert R.main(["--combos", paths["combos"], "--out", str(tmp_path / "r.json"), "--spec", str(bad)]) == 2
