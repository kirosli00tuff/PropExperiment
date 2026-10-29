"""Unit tests for the E.32b economics code (synthetic inputs only; no market data, no real E.32b facts).

Run: uv run pytest -q reports/stage_e32b_briefs/work/econ/test_econ32b.py
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

WORK = Path(__file__).resolve().parent
sys.path.insert(0, str(WORK))

import econ32b as D  # noqa: E402
import econ32b_core as C  # noqa: E402
import econ32b_inputs as I  # noqa: E402
import econ32b_regress as RG  # noqa: E402

FIRMS = {"topstep", "lucid", "tradeify", "mffu", "bulenox"}


# ------------------------------------------------------------------------------- synthetic curves ----
def make_eval(ev_fn, p_fn=None, se: float = 1.0):
    def evaluate(d: float) -> dict[str, Any]:
        return {"ev": ev_fn(d), "se": se, "p10k": (p_fn or (lambda x: 0.0))(d),
                "stats": {"eval_fees_per_attempt": 100.0 + 10.0 * d}}
    return evaluate


def test_monotone_threshold_is_smallest_grid_point_with_f_ge_0():
    curve = C.Curve(make_eval(lambda d: 1000.0 * (d - 1.234)))
    r = C.threshold(curve, c=0.5, what="ev", k_max=400)
    # d = 0.01 k - 0.5 >= 1.234  ->  k >= 173.4  ->  174
    assert (r["k"], r["k_bisection"], r["mu"], r["above_cap"]) == (174, 174, 1.74, False)
    assert r["f_at_k"] >= 0 > r["f_at_k_minus_1"]
    assert r["confirmation"]["confirmed"]


def test_boundary_values_count_as_reached():
    curve = C.Curve(make_eval(lambda d: 0.0 if d >= 1.0 else -500.0, lambda d: 0.5 if d >= 2.0 else 0.1))
    assert C.threshold(curve, 0.0, "ev", 400)["k"] == 100  # EV = 0 exactly is >= 0
    assert C.threshold(curve, 0.0, "p10k", 400)["k"] == 200  # P10K = 0.5 exactly is >= 0.5


def test_above_cap_gives_none_and_checks_the_whole_grid():
    curve = C.Curve(make_eval(lambda d: -5000.0))
    r = C.threshold(curve, 1.0, "ev", 400)
    assert r["k"] is None and r["mu"] is None and r["above_cap"]
    assert r["confirmation"]["n_checked"] >= 41  # every 0.10 tick on [0, 4]


def test_zero_threshold_when_f_ge_0_at_mu_0():
    curve = C.Curve(make_eval(lambda d: 10.0))
    assert C.threshold(curve, 2.0, "ev", 400)["k"] == 0


def _island(d: float) -> float:
    if 0.45 <= d <= 0.65:
        return 10.0 if 0.53 <= d <= 0.55 else -50.0  # near (>= -100): the gap is filled densely
    return 1000.0 * (d - 2.0)


def test_confirmation_corrects_a_near_island_below_the_bisection_value():
    curve = C.Curve(make_eval(_island))
    r = C.threshold(curve, 0.0, "ev", 400)
    assert r["k_bisection"] == 200
    assert r["k"] == 53 and not r["confirmation"]["confirmed"] and 53 in r["confirmation"]["violations"]


def test_far_island_inside_one_subgrid_gap_is_not_seen_e28_assumption():
    def ev(d: float) -> float:
        return 10.0 if 0.53 <= d <= 0.55 else 1000.0 * (d - 2.0)  # coarse neighbours at -1500, -1400: far
    r = C.threshold(C.Curve(make_eval(ev)), 0.0, "ev", 400)
    assert r["k"] == 200 and r["confirmation"]["confirmed"]


def test_market_threshold_is_limit_threshold_plus_spread_on_shared_draws():
    curve = C.Curve(make_eval(lambda d: 1000.0 * (d - 0.7)))
    lim = C.threshold(curve, 0.9, "ev", 500)["k"]
    mkt = C.threshold(curve, 1.9, "ev", 500)["k"]
    assert mkt - lim == 100


def test_primary_and_spread1_share_the_curve_cache():
    curve = C.Curve(make_eval(lambda d: 1000.0 * (d - 0.7), lambda d: 0.6 if d > 1.1 else 0.2))
    C.evaluate_case(curve, C.CostCase("primary", 2.0, 0.5, 2.0), 600, 30.0)
    n1 = curve.n_evals
    C.evaluate_case(curve, C.CostCase("spread1", 2.0, 0.5, 1.0), 600, 30.0)
    alone = C.Curve(make_eval(lambda d: 1000.0 * (d - 0.7), lambda d: 0.6 if d > 1.1 else 0.2))
    C.evaluate_case(alone, C.CostCase("spread1", 2.0, 0.5, 1.0), 600, 30.0)
    assert curve.n_evals - n1 < alone.n_evals / 2  # lattices offset by exactly 100 grid steps


def test_evaluate_case_has_the_contract_fields_and_sigma60_units():
    curve = C.Curve(make_eval(lambda d: 1000.0 * (d - 0.7), lambda d: 0.6 if d > 1.1 else 0.2))
    r = C.evaluate_case(curve, C.CostCase("primary", 1.5, 0.5, 1.0), 1200, 40.0)
    for k in ("mu_star_mkt", "mu10K_mkt", "above_cap", "cost_per_attempt", "sigma60", "m_star", "m10K", "grid_cap"):
        assert k in r
    assert r["c_mkt_ticks"] == pytest.approx(4.0) and r["c_lim_ticks"] == pytest.approx(3.0)
    assert r["mu_star_mkt"] == pytest.approx(4.70)
    assert r["m_star"] == pytest.approx(4.70 / 40.0) and r["m10K"] == pytest.approx(r["mu10K_mkt"] / 40.0)
    assert r["grid_cap"] == 12.0 and r["above_cap"] == {"mu_star": False, "mu10K": False}
    assert r["cost_per_attempt"] == pytest.approx(100.0 + 10.0 * (-3.0))  # mu = 0, limit case
    assert r["cost_per_attempt_mkt_mu0"] == pytest.approx(100.0 + 10.0 * (-4.0))


# ------------------------------------------------------------------------------ grid and T rules ----
@pytest.mark.parametrize("sigma60,cap", [(5.0, 4), (10.0, 4), (13.3334, 5), (20.0, 6), (100.0, 30), (215.3, 65)])
def test_grid_cap_is_max_4_and_ceil_030_sigma60(sigma60, cap):
    assert C.grid_cap_ticks(sigma60) == cap and C.grid_cap_k(sigma60) == 100 * cap


@pytest.mark.parametrize("bad", [None, 0.0, -1.0, float("nan")])
def test_grid_cap_rejects_bad_sigma(bad):
    with pytest.raises(ValueError):
        C.grid_cap_ticks(bad)


@pytest.mark.parametrize("l_main,h,t", [(390, 1, 20), (390, 30, 13), (390, 60, 6), (390, 120, 3), (390, 240, 1),
                                        (1380, 60, 20), (290, 60, 4), (200, 240, 0), (60, 60, 1)])
def test_trades_per_day_min_20_floor_lmain_over_h(l_main, h, t):
    assert C.trades_per_day(l_main, h) == t


# --------------------------------------------------------------------------------- inputs (F3/F4) ----
def _root(sig1: float, l_main: int = 390, status: str = "owned", tick: float = 0.25) -> dict[str, Any]:
    h = {str(x): {"sigma": sig1 * math.sqrt(x), "m": 0.0, "median_abs": 0.0, "p99_abs": 0.0, "n": 100}
         for x in (1, 2, 5, 15, 30, 60, 120, 240)}
    return {"status": status, "tick_size": tick, "L_main": l_main, "h": h}


def _code(v: float, s: float | None = None, tick: float = 0.25) -> dict[str, Any]:
    return {"tick_size": tick, "tick_value_usd": v, "excluded": False,
            "spread_S": {"value": s, "sourced": s is not None, "item": "x" if s else None}}


@pytest.fixture()
def facts() -> tuple[dict[str, Any], dict[str, Any]]:
    f3 = {"spec_sha256": D.SPEC_SHA256, "roots": {"MNQ": _root(28.0), "ZN": _root(2.0, tick=0.015625),
                                                  "GC": _root(5.0, l_main=200, tick=0.1), "SI": _root(1.0, status="unknown"),
                                                  "NQ": _root(28.0)}}
    f4 = {"spec_sha256": D.SPEC_SHA256,
          "codes": {"MNQ": _code(0.5), "ZN": _code(15.625, 1.0, 0.015625), "GC": _code(10.0, 1.5, 0.1),
                    "SI": _code(25.0, None, 0.005), "NQ": _code(5.0)},
          "pairs": {"topstep|MNQ": {"listed_50k": True, "fee_rt_usd": 1.0, "fee_kind": "stated"},
                    "Lucid|GC": {"listed_50k": True, "fee_rt_usd": 4.0, "fee_kind": "stated"},
                    "mffu|ZN": {"listed_50k": True, "fee_rt_usd": None, "fee_kind": "stated"},
                    "bulenox|ZN": {"listed_50k": False, "fee_rt_usd": 3.0, "fee_kind": "stated"},
                    "topstep|SI": {"listed_50k": True, "fee_rt_usd": 3.0, "fee_kind": "stated"},
                    "topstep|NQ": {"listed_50k": True, "fee_rt_usd": 3.0, "fee_kind": "stated"}},
          "firms": {}}
    return f3, f4


def test_jobs_from_facts_skip_rules(facts):
    jobs, meta, skipped = I.jobs_from_facts(*facts, FIRMS)
    assert set(meta) == {"topstep|MNQ", "Lucid|GC"}  # F4's own key is kept; the model firm is normalised
    assert {j["firm"] for j in jobs if j["pair"] == "Lucid|GC"} == {"lucid"}
    assert skipped["topstep|NQ"] == "excluded (V49)"
    assert skipped["mffu|ZN"] == "fee unknown"
    assert skipped["bulenox|ZN"] == "not listed for the 50K plan"
    assert skipped["topstep|SI"].startswith("sigma unknown")


def test_jobs_from_facts_primary_spread1_and_dir60(facts):
    jobs, meta, _ = I.jobs_from_facts(*facts, FIRMS)
    by = {(j["pair"], j["curve"]): j for j in jobs}
    prim = by[("Lucid|GC", "primary")]
    assert prim["T"] == 20 and prim["sigma_T"] == pytest.approx(5.0)
    assert {c["name"]: c["s_rt_ticks"] for c in prim["cases"]} == {"primary": 1.5, "spread1": 1.0}
    d60 = by[("Lucid|GC", "dir60")]
    assert d60["T"] == 3 and d60["sigma_T"] == pytest.approx(5.0 * math.sqrt(60))  # floor(200 / 60) = 3
    assert d60["cases"][0]["name"] == "E_dir60" and d60["cases"][0]["s_rt_ticks"] == 1.5
    assert prim["k_max"] == d60["k_max"] == 100 * C.grid_cap_ticks(5.0 * math.sqrt(60))
    mnq = by[("topstep|MNQ", "primary")]
    assert mnq["cases"][0]["s_rt_ticks"] == 1.0 and meta["topstep|MNQ"]["S_rt_status"] == "u"
    assert mnq["k_max"] == 100 * math.ceil(0.30 * 28.0 * math.sqrt(60))


def test_edir_pairs_get_30_120_240_and_t0_is_reported(facts):
    jobs, meta, _ = I.jobs_from_facts(*facts, FIRMS, edir_pairs=["topstep|MNQ", "lucid|GC"])
    curves = {(j["pair"], j["curve"]): j["T"] for j in jobs}
    assert curves[("topstep|MNQ", "dir30")] == 13 and curves[("topstep|MNQ", "dir120")] == 3
    assert curves[("topstep|MNQ", "dir240")] == 1
    assert ("Lucid|GC", "dir240") not in curves  # L_main 200 < 240: T = 0
    assert ("Lucid|GC", "dir30") in curves  # the E_dir list matches F4 keys case-insensitively on the firm
    assert any("T = 0" in n for n in meta["Lucid|GC"]["notes"])


def test_only_filter_and_edir_for_a_pair_not_computed(facts):
    jobs, meta, skipped = I.jobs_from_facts(*facts, FIRMS, edir_pairs=["mffu|ZN"], only=["lucid|GC", "mffu|ZN"])
    assert set(meta) == {"Lucid|GC"} and {j["pair"] for j in jobs} == {"Lucid|GC"}
    assert skipped["mffu|ZN"] == "fee unknown"  # the first reason is kept


def test_tick_size_disagreement_between_f3_and_f4_is_refused(facts):
    f3, f4 = facts
    f4["codes"]["GC"]["tick_size"] = 0.2
    with pytest.raises(ValueError, match="tick_size"):
        I.jobs_from_facts(f3, f4, FIRMS)


def test_unknown_firm_is_refused(facts):
    f3, f4 = facts
    f4["pairs"]["apex|MNQ"] = {"listed_50k": True, "fee_rt_usd": 1.0}
    with pytest.raises(ValueError, match="no E.28 firm model"):
        I.jobs_from_facts(f3, f4, FIRMS)


def test_spread_rt_rules():
    assert I.spread_rt({"spread_S": {"value": 1.5, "sourced": True}}) == (1.5, "sourced")
    assert I.spread_rt({"spread_S": {"value": None, "sourced": False}}) == (1.0, "u")
    assert I.spread_rt({"spread_S": {"value": 2.0, "sourced": False}}) == (1.0, "u")
    assert I.spread_rt({}) == (1.0, "u")


def test_firm_check_reports_mismatch_match_and_unverifiable():
    limits = {"topstep": {"plan": "p", "mll_usd": 2000.0, "dll_usd": None},
              "lucid": {"plan": "q", "mll_usd": 2000.0, "dll_usd": 1200.0}}
    f4 = {"firms": {"topstep": {"mll_50k": 2000, "dll_50k": None},
                    "Lucid": {"mll_50k": {"value": 2500, "item": "x"}, "dll_50k": "soft 1,200"}}}
    fc = I.firm_check(f4, limits)
    assert fc["rows"]["topstep"]["mll_50k"]["status"] == "match"
    assert fc["rows"]["topstep"]["dll_50k"]["status"] == "match (none)"
    assert fc["rows"]["lucid"]["mll_50k"]["status"] == "MISMATCH"
    assert fc["rows"]["lucid"]["dll_50k"]["status"].startswith("unverifiable")
    assert len(fc["mismatches"]) == 1


def test_regression_jobs_from_e28_inputs():
    jobs, skipped = I.jobs_from_e28(json.loads((WORK / "A3_inputs.json").read_text()))
    assert len(jobs) == 121 and len(skipped) == 11
    assert all(j["T"] == 20 and j["k_max"] == 500 and j["cases"][0]["s_rt_ticks"] == 1.0 for j in jobs)


# ---------------------------------------------------------------------------- model binding (light) ----
def test_evaluator_law_is_e28s_at_t20_and_scales_with_t_and_sigma(monkeypatch):
    import A3_funnel as F
    import econ32b_model as M

    seen = []
    monkeypatch.setattr(F, "simulate_pools", lambda model, law, a, b: seen.append(law) or "pools")
    monkeypatch.setattr(F, "cycle_stats", lambda *a, **k: SimpleNamespace(ev=1.0, se=0.1, ev_ex_api=1.0))
    monkeypatch.setattr(F, "campaign_p_reach", lambda *a, **k: 0.25)
    state = {"models": {"x": None}, "draws": {"x": (None, None)}, "idx": (None, None)}
    d, v, sig = 0.37, 0.5, 27.8
    M.make_evaluator(state, "x", 20, sig, v)(d)
    assert seen[-1].m == F.T_RT * d * v and seen[-1].s == math.sqrt(F.T_RT) * sig * v
    M.make_evaluator(state, "x", 6, 215.0, v)(d)
    assert seen[-1].m == pytest.approx(6 * d * v) and seen[-1].s == pytest.approx(math.sqrt(6) * 215.0 * v)
    with pytest.raises(ValueError):
        M.make_evaluator(state, "x", 0, sig, v)


def test_spec_hash_is_checked(monkeypatch):
    D.check_spec()
    monkeypatch.setattr(D, "SPEC_SHA256", "0" * 64)
    with pytest.raises(SystemExit):
        D.check_spec()


def test_build_doc_layout_nests_edir_and_keeps_contract_blocks():
    blk = {"mu_star_mkt": 1.0, "mu10K_mkt": None, "search": {
        "mu_star_mkt": {"k_bisection": 100, "f_at_k": 1.0, "f_at_k_minus_1": -1.0,
                        "confirmation": {"confirmed": True, "violations": [], "n_checked": 3, "max_below": {}}}}}
    parts = {"a": {"job": {"pair": "topstep|MNQ"}, "cases": {"primary": blk, "spread1": blk}},
             "b": {"job": {"pair": "topstep|MNQ"}, "cases": {"E_dir60": blk}},
             "c": {"job": {"pair": "topstep|MNQ"}, "cases": {"E_dir30": blk}}}
    doc = D.build_doc(parts, {"topstep|MNQ": {}}, {"topstep|NQ": "excluded (V49)"}, {})
    p = doc["pairs"]["topstep|MNQ"]
    assert set(p) >= {"primary", "spread1", "E_dir60", "E_dir", "inputs"} and set(p["E_dir"]) == {"30"}
    assert doc["spec_sha256"] == D.SPEC_SHA256 and doc["not_computed"]["topstep|NQ"] == "excluded (V49)"


# --------------------------------------------------------------------------------- regression rules ----
@pytest.mark.parametrize("e28,new,ok", [(2.21, 2.21, True), (2.21, 2.22, True), (2.21, 2.23, False),
                                        ("> 4", None, True), ("> 4", 4.37, True), ("> 4", 3.9, False),
                                        (3.0, None, False)])
def test_regression_rule_mu_star(e28, new, ok):
    assert RG._check_star(e28, new)[0] is ok


@pytest.mark.parametrize("e28,new,ok", [(2.75, 3.75, True), (3.6, 4.6, True), (2.75, 3.77, False),
                                        ("> 4", None, True), ("> 4", 4.9, False), (3.9, None, False)])
def test_regression_rule_mu10k(e28, new, ok):
    assert RG._check_10k(e28, new)[0] is ok
