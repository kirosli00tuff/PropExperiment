"""Fixture-level tests for score32b: satellites and leaders, the Layer 1 and Layer 2 gates, NQ, ranking and the tie
chain, each declared variant flipping only its one thing, the lead-ruling hook, moves against E.28, validation, CLI.
All inputs are the synthetic fixture (make_fixture.py)."""
import json
from dataclasses import fields, replace
from fractions import Fraction as F

import make_fixture
import pytest
import score32b as S
from s32b_common import DECLARED_VARIANTS, HALF, INF, InputError, Params, to_jsonable
from s32b_layer1 import Layer1, layer1_rows
from s32b_layer2 import W_L2


def row(docs, code, params=None):
    return Layer1(docs, params or Params()).row(code)


# ------------------------------------------------------------------------------------------- Layer 1 on the fixture
def test_fixture_layer1_hand_values(docs):
    cl = row(docs, "CL")
    assert (cl["D1"], cl["D2"], cl["D3"], cl["D4"], cl["D5"], cl["D6"]) == (F(7, 2), HALF, 4, 3, 4, 3)
    assert cl["L1"] == F("3.025") and cl["gate_pass"]
    ym = row(docs, "YM")
    assert ym["D1_bands"]["60"] == 4 and ym["r"]["60"] == F(1, 40)     # r_60 = 1.5 / 60 = 0.025 exactly
    assert ym["D2_parts"]["b"] == HALF                                 # D2 b unknown: 0.5


def test_r5_r15_rOC_reported_not_scored(docs):
    cl = row(docs, "CL")
    assert cl["r_5"] is not None and cl["r_OC"] is not None
    assert set(cl["D1_bands"]) == {"30", "60", "120", "240"}


def test_unsourced_spread_is_one_tick_u(docs):
    mcl = row(docs, "MCL")
    assert mcl["S"] == 1 and not mcl["S_sourced"] and any(n.startswith("S: no sourced spread") for n in mcl["u"])


def test_sat_i_ratio_at_least_five_inclusive(docs):
    docs["F4"]["codes"]["MCL"]["adv"]["value"] = 500000      # CL 250000 x 1000 = 5 x (500000 x 100)
    assert row(docs, "MCL")["D4_parts"]["sat_i"] is True
    docs["F4"]["codes"]["MCL"]["adv"]["value"] = 500001
    assert row(docs, "MCL")["D4_parts"]["sat_i"] is False


def test_sat_i_unknown_ratio_larger_sibling_holds_u(docs):
    mzm = row(docs, "MZM")                                   # MZM ADV unknown, ZM is the larger-size sibling
    assert mzm["D4_parts"]["sat_i"] is True and any("larger-size sibling ZM unknown" in n for n in mzm["u"])
    zm = row(docs, "ZM")                                     # ratio unknown, but MZM is smaller: no satellite
    assert zm["D4_parts"]["Sat"] == 0


def test_sat_i_size_undeterminable_goes_to_lead(docs):
    f3, f4 = docs["F3"]["roots"], docs["F4"]["codes"]
    f3["10Y"] = make_fixture._root("unknown", 0.001, None, None, None, None)
    f3["ZN"] = make_fixture._root("owned", 0.015625, 20.0, 110.0, 40, 90)
    base = make_fixture._code("CL", 0.001, 1000, 30000, sibs=("ZN",), leader="ZN")
    f4["10Y"] = {**base, "family": "rates", "underlying": "10-year Treasury", "tick_size": 0.001}
    f4["ZN"] = {**make_fixture._code("CL", 0.015625, 1000, 1500000, sibs=("10Y",), leader="ZN"), "family": "rates",
                "tick_size": 0.015625, "tick_value_usd": 15.625}
    r = row(docs, "10Y")
    assert r["D4_parts"]["sat_i"] is True and any("relative size" in n for n in r["lead"])
    assert not r["gate_pass"] and r["D1"] is None


def test_sat_ii_needs_a_source_and_sat_iii_blind(docs):
    assert row(docs, "QM")["D4_parts"]["sat_ii"] is True
    docs["F4"]["codes"]["QM"]["settles_off_sibling"]["item"] = None
    qm = row(docs, "QM")
    assert qm["D4_parts"]["sat_ii"] is False and any("not sourced" in n for n in qm["u"])
    docs["blind"]["codes"]["YM"]["sat_iii"] = {"value": 1}
    ym = row(docs, "YM")
    assert ym["D4_parts"]["sat_iii"] and ym["D4"] == 1          # 4 - L 0 - J 1 - 2
    docs["blind"]["codes"]["YM"]["sat_iii"] = {"value": None, "unknown": True}
    assert row(docs, "YM")["D4_parts"]["sat_iii"] is False      # unknown: 0


def test_satellite_d2_uses_leader_facts_and_d2_own_its_own(docs):
    mnq = row(docs, "MNQ")
    assert mnq["D4_parts"]["leader"] == "NQ" and mnq["D2_parts"]["facts_of"] == "NQ"
    assert (mnq["D2_parts"]["a"], mnq["D2_parts"]["b"], mnq["D2_parts"]["c"]) == (1, 1, 1) and mnq["D2"] == 0
    own = row(docs, "MNQ", Params(d2_own=True))
    assert own["D2_parts"]["facts_of"] == "MNQ" and own["D2"] == 2   # 4 - 1 - 0 - 0 - d 1
    assert own["D6"] == mnq["D6"] == 4                               # D6 keeps the leader's evidence


def test_d6_satellite_takes_leader_evidence_with_cap(docs):
    assert row(docs, "MCL")["D6"] == 3 and row(docs, "MCL")["D6_parts"]["evidence_of"] == "CL"
    assert row(docs, "ZM")["D6"] == 2                                # 4 rated on a snippet only: capped at 2
    assert row(docs, "SI")["D6"] == 1                                # unknown: 1


def test_d2_c_family_max_includes_nq(docs):
    assert Layer1(docs, Params()).family_c("MNQ")[0] == 0           # NQ's notional is the equity maximum
    assert Layer1(docs, Params()).family_c("NQ") == (1, None)
    docs["F4"]["codes"]["NQ"]["adv"]["value"] = None                 # NQ unknown: MNQ max among known, provisional
    c, note = Layer1(docs, Params()).family_c("MNQ")
    assert c == 1 and "provisional" in note


def test_d2_c_tie_gives_both_one(docs):
    docs["F4"]["codes"]["YM"]["adv"]["value"] = 600000 * 20 * 15000 / (5 * 34000)
    assert row(docs, "YM")["D2_parts"]["c"] == 1


def test_d2_d_unknown_count_and_missing_underlying(docs):
    assert row(docs, "ZM")["D2_parts"]["d"] == HALF                  # soybean meal call failed: 0.5 (u)
    del docs["attention"]["underlyings"]["Dow"]
    ym = row(docs, "YM")
    assert ym["D2_parts"]["d"] == HALF and any("no underlying" in n for n in ym["u"])


def test_d3_unknown_items_score_zero_and_cap(docs):
    docs["blind"]["codes"]["CL"]["s1"] = {"value": None, "unknown": True}
    assert row(docs, "CL")["D3"] == 2                                 # 0 + 1 + 1
    docs["blind"]["codes"]["CL"]["s1"] = {"value": 2}
    docs["blind"]["codes"]["CL"]["s2"] = {"value": 2}
    assert row(docs, "CL")["D3"] == 4                                 # min(4, 2 + 2 + 1)


def test_gates_d4_zero_sigma_and_unknown(docs):
    assert row(docs, "QM")["gate_reasons"] == ["D4 = 0"]
    mzm = row(docs, "MZM")
    assert mzm["gate_reasons"] == ["sigma_60 = 2.90 ticks vs 2 x (1 + 0.5) = 3.00 ticks"]
    si = row(docs, "SI")
    assert not si["gate_pass"] and si["L1"] is None and "unknown" in si["gate_reasons"][0]


def test_gate_partial_sigma_unknown_fails_and_tells_lead(docs):
    docs["F3"]["roots"]["CL"]["h"]["240"]["sigma"] = None
    cl = row(docs, "CL")
    assert not cl["gate_pass"] and cl["D1"] is None and any("240" in n for n in cl["lead"])


def test_l1_below_two_flagged_not_gated(docs):
    zm = row(docs, "ZM")
    assert zm["L1_below_2"] and zm["gate_pass"]
    assert not row(docs, "ZM", Params(l1min2=True))["gate_pass"]


def test_nq_excluded_never_scored(docs):
    assert row(docs, "NQ")["status"] == "excluded (V49)"
    res = S.run_variant(docs, Params())
    nq = [r for r in res["pairs"] if r["code"] == "NQ"]
    assert nq and all(r["status"] == "excluded (V49)" and r["rank"] is None for r in nq)


# ------------------------------------------------------------------------------------------- Layer 2 and ranking
def pair(res, key):
    return next(r for r in res["pairs"] if r["key"] == key)


def test_layer2_gates_and_unknowns(docs):
    res = S.run_variant(docs, Params())
    assert pair(res, "lucid|MNQ")["gate_reasons"] == ["A = 0"]
    assert "not listed for the 50K plan" in pair(res, "lucid|QM")["gate_reasons"]
    assert pair(res, "bulenox|ZM")["gate_reasons"] == ["50K listing unknown"]
    assert pair(res, "bulenox|CL")["R"] == 1                           # R unknown: 1
    docs["F4"]["firms"]["bulenox"]["bc_accepts"] = False
    res = S.run_variant(docs, Params())
    assert all("British Columbia residents not accepted" in r["gate_reasons"]
               for r in res["pairs"] if r["firm"] == "bulenox" and r["code"] != "NQ")
    docs["blind"]["pairs"]["topstep|CL"]["A"] = {"value": None, "unknown": True}
    assert pair(S.run_variant(docs, Params()), "topstep|CL")["A"] == 1   # A unknown: 1


def test_l2_and_s_exact(docs):
    r = pair(S.run_variant(docs, Params()), "bulenox|MNQ")
    l2 = sum(W_L2[k] * r[k] for k in W_L2)
    assert r["L2"] == l2 and r["S"] == (r["L1"] + l2) / 2


def test_rank_key_chain_order():
    base = {"S": F("2.345"), "m_star": F("0.1"), "L1": F(2), "cost_per_attempt": F(10), "code": "CL",
            "firm": "topstep"}
    variants = [
        {**base, "S": F("2.354999"), "firm": "lucid"},    # same 2.35: tie, decided by later levels
        {**base, "m_star": F("0.09")},                     # lower m* first
        {**base, "L1": F(3)},                              # higher L1 first
        {**base, "cost_per_attempt": F(9)},                # lower cost first
        {**base, "code": "BTC"},                           # code alphabetical
        {**base, "firm": "bulenox"},                       # firm name: Bulenox < Topstep
        {**base, "m_star": INF},                           # above cap: last on m*
    ]
    order = sorted([base] + variants, key=S.rank_key)
    assert order[0]["m_star"] == F("0.09") and order[-1]["m_star"] == INF
    assert [r["firm"] for r in order if r["code"] == "CL" and r["m_star"] == F("0.1") and r["L1"] == 2
            and r["cost_per_attempt"] == 10] == ["bulenox", "lucid", "topstep"]


def test_ties_report_deciding_level(docs):
    res = S.run_variant(docs, Params())
    assert res["ties"] and res["ties"][0]["pairs"] == ["topstep|YM", "topstep|MYM"]
    assert res["ties"][0]["steps"][0]["decided_by"] == "m*"


def test_missing_econ_for_rankable_pair_refused(docs):
    del docs["econ"]["pairs"]["topstep|CL"]["E_dir60"]
    with pytest.raises(InputError):
        S.validate(docs, allow_partial=True)


# ------------------------------------------------------------------------------------------- variants
ALLOWED_L1_CHANGES = {
    "slip0": {"slip", "c_RT", "r", "r_5", "r_15", "r_OC", "D1", "D1_bands", "L1", "L1_below_2", "gate_pass",
              "gate_reasons", "gate_arithmetic"},
    "mad": {"dispersion", "disp", "r", "r_5", "r_15", "r_OC", "D1", "D1_bands", "L1", "L1_below_2", "gate_pass",
            "gate_reasons", "gate_arithmetic"},
    "D1_all": {"D1_horizons", "D1_bands", "D1", "L1", "L1_below_2", "gate_pass", "gate_reasons"},
    "sat1": {"D4", "D4_parts", "L1", "L1_below_2", "gate_pass", "gate_reasons"},
    "D2_own": {"D2", "D2_parts", "L1", "L1_below_2", "gate_pass", "gate_reasons"},
    "L1min2": {"gate_pass", "gate_reasons"},
    "spread1": {"S", "S_sourced", "c_RT", "r", "r_5", "r_15", "r_OC", "D1", "D1_bands", "D4", "D4_parts", "L1",
                "L1_below_2", "gate_pass", "gate_reasons", "gate_arithmetic"},
    "E_dir60": set(),
}
ALLOWED_L1_CHANGES["slip1"] = ALLOWED_L1_CHANGES["slip0"]


def test_each_declared_variant_flips_exactly_one_param():
    base = Params()
    for name, ov in DECLARED_VARIANTS.items():
        p = replace(base, **ov)
        changed = [f.name for f in fields(Params) if getattr(p, f.name) != getattr(base, f.name)]
        assert changed == list(ov), name


@pytest.mark.parametrize("name", sorted(ALLOWED_L1_CHANGES))
def test_variant_changes_only_its_criteria(docs, name):
    prim = layer1_rows(docs, Params())
    var = layer1_rows(docs, replace(Params(), **DECLARED_VARIANTS[name]))
    changed = set()
    for c in prim:
        changed |= {k for k in prim[c] if prim[c][k] != var[c][k] and k not in ("u", "lead")}
    assert changed <= ALLOWED_L1_CHANGES[name], (name, changed - ALLOWED_L1_CHANGES[name])
    assert changed or name == "E_dir60", f"{name} had no effect on the fixture"


def test_oc1_off_changes_only_transferred_codes(docs):
    prim = layer1_rows(docs, Params())
    var = layer1_rows(docs, Params(oc1_off=True))
    moved = {c for c in prim if prim[c] != var[c]}
    assert moved == {"QM", "MNQ", "MYM", "MZM"}
    assert all("OC1_off" in var[c]["gate_reasons"][0] for c in moved)


def test_e_dir60_changes_only_e_side_of_pairs(docs):
    prim = S.run_variant(docs, Params())
    var = S.run_variant(docs, Params(e_dir60=True))
    allowed = {"E", "m_star", "m10K", "cost_per_attempt", "econ_block", "L2", "S", "S_rounded", "rank"}
    for a in prim["pairs"]:
        b = pair(var, a["key"])
        assert {k for k in a if a[k] != b[k]} <= allowed


def test_spread1_uses_spread1_econ_block(docs):
    docs["F4"]["codes"]["ZM"]["touch"] = {"value": None, "sourced": False, "item": None}
    prim = S.run_variant(docs, Params())
    var = S.run_variant(docs, Params(spread1=True))
    assert pair(var, "lucid|ZM")["econ_block"] == "spread1"
    assert prim["layer1"]["ZM"]["D4_parts"]["L"] == 1                # sourced spread 1.5 ticks: L 1
    assert var["layer1"]["ZM"]["S"] == 1 and var["layer1"]["ZM"]["c_RT"] == F(3, 2)
    assert var["layer1"]["ZM"]["D4_parts"]["L"] == 0                 # S = 1 everywhere: no spread deduction


def test_sat1_lets_qm_pass(docs):
    assert not layer1_rows(docs, Params())["QM"]["gate_pass"]
    assert layer1_rows(docs, Params(sat_deduction=1))["QM"]["gate_pass"]


# ------------------------------------------------------------------------------------------- run_all, hook, moves
def fake_e28():
    def p(firm, code, rank, s):
        return {"firm": firm, "code": code, "rank": rank, "S": s, "L1": 2.0, "E": 2.0, "D": 1, "R": 4, "A": 2,
                "F": 1, "P": 2, "Rel": 3, "L1_gate_pass": True, "L2_gate_reasons": []}
    # S = 0.5 x 2.0 + 0.5 x (0.4 x 2 + 0.1 x 1 + 0.1 x 4 + 0.15 x 2 + 0.1 x 1 + 0.05 x 2 + 0.1 x 3) = 2.05
    return {"variants": {"primary": {"pairs": [p("topstep", "MNQ", 14, 2.05), p("lucid", "SI", 3, 2.05),
                                               {**p("lucid", "QM", None, 2.05), "L1_gate_pass": False}]}}}


def test_e28_weights_reproduce_every_e28_s():
    e28 = S.load_json(S.E28_TABLE)
    rows = [r for r in e28["variants"]["primary"]["pairs"]
            if all(isinstance(r.get(k), (int, float)) for k in ("S", "L1", "E", "D", "R", "A", "F", "P", "Rel"))]
    assert len(rows) > 60
    for r in rows:
        s = 0.5 * r["L1"] + 0.5 * sum(w * r[k] for k, w in S.W_L2_E28.items())
        assert abs(s - r["S"]) < 1e-9, (r["firm"], r["code"])


def test_run_all_variants_hook_and_moves(docs):
    out = S.run_all(docs, make_fixture.rulings_doc(), fake_e28(), allow_partial=True)
    assert set(DECLARED_VARIANTS) < set(out["variants"])
    rv = out["variants"]["RL-SYN-CL-spread2"]
    assert rv["kind"] == "lead ruling" and len(rv["top5"]) == 5 and "topstep" in rv["MNQ_ranks"]
    assert docs["F4"]["codes"]["CL"]["spread_S"]["value"] == 1          # the hook never touches the primary
    rows = {(r["firm"], r["code"]): r for r in out["moves_vs_e28"]["rows"]}
    mnq = rows[("topstep", "MNQ")]
    assert mnq["rank_e28"] == 14 and mnq["rank_here"] == 2 and mnq["rank_change"] == 12
    assert abs(sum(mnq["contrib"].values()) - (mnq["S_here"] - mnq["S_e28"])) < 1e-12
    assert mnq["moved_by"] and rows[("lucid", "SI")]["status_here"] == "Layer 1 gate"
    json.dumps(to_jsonable(out))                                          # serialisable


def test_ruling_hook_rejects_bad_params_and_names(docs):
    bad = {"rulings": [{"name": "X", "params": {"nope": 1}, "patches": []}]}
    with pytest.raises(InputError):
        S.run_all(docs, bad, None, allow_partial=True)
    clash = {"rulings": [{"name": "slip0", "params": {}, "patches": []}]}
    with pytest.raises(InputError):
        S.run_all(docs, clash, None, allow_partial=True)


def test_validate_universe_family_and_exclusion(docs):
    with pytest.raises(InputError):
        S.validate(docs, allow_partial=False)                              # 36 codes missing
    docs["F4"]["codes"]["CL"]["family"] = "natgas"
    with pytest.raises(InputError):
        S.validate(docs, allow_partial=True)
    docs["F4"]["codes"]["CL"]["family"] = "crude"
    docs["F4"]["codes"]["CL"]["excluded"] = True
    with pytest.raises(InputError):
        S.validate(docs, allow_partial=True)


def test_cross_checks_are_soft(docs):
    docs["F3"]["roots"]["CL"]["tick_size"] = 0.02
    docs["data_access"]["codes"]["CL"]["k_usd_month"] = 99
    checks = S.validate(docs, allow_partial=True)
    assert any("tick_size" in c for c in checks) and any("k_usd_month" in c for c in checks)


def test_cli_writes_output_and_refuses_bad_spec(tmp_path):
    paths = make_fixture.write_all(str(tmp_path / "fx"))
    args = ["--f3", paths["F3"], "--f4", paths["F4"], "--blind", paths["blind"], "--econ", paths["econ"],
            "--attention", paths["attention"], "--data-access", paths["data_access"], "--rulings", paths["rulings"],
            "--out", str(tmp_path / "o.json"), "--md", str(tmp_path / "o.md"), "--allow-partial-universe"]
    assert S.main(args) == 0
    out = json.loads((tmp_path / "o.json").read_text())
    assert out["primary"]["n_ranked"] == 16 and out["primary"]["top15"][0]["code"] == "MNQ"
    bad = tmp_path / "bad_spec.md"
    bad.write_text("x")
    assert S.main(args + ["--spec", str(bad)]) == 2
