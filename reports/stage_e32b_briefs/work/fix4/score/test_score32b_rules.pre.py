"""Unit tests for the pure criterion rules of score32b (spec sections 3 and 4): every band boundary goes to the
higher score, and every unknown rule. Run: uv run pytest -q reports/stage_e32b_briefs/work/score/"""
from fractions import Fraction as F

import pytest
from s32b_common import (
    HALF,
    InputError,
    SpecHashError,
    apply_patches,
    blind_rated,
    cap_extreme_0_4,
    cap_s12,
    check_doc_hash,
    check_spec,
    q,
    round2,
)
from s32b_layer1 import (
    attention_count,
    attention_tiers,
    below_l1_min,
    d1_band,
    d1_score,
    d5_h,
    d5_k,
    d5_o,
    d5_p,
    j_score,
    l_score,
    sigma_gate,
)
from s32b_layer2 import d_score, e_score, p_score, rel_score, room_band


# ------------------------------------------------------------------------------------------- spec hash, numbers
def test_spec_hash_matches_frozen_file():
    assert check_spec().startswith("09ebe6970fcf0270")


def test_refuses_when_spec_differs(tmp_path):
    fake = tmp_path / "spec.md"
    fake.write_text("not the frozen spec\n")
    with pytest.raises(SpecHashError):
        check_spec(fake)
    with pytest.raises(SpecHashError):
        check_spec(tmp_path / "missing.md")


def test_refuses_input_recording_another_spec_hash():
    with pytest.raises(SpecHashError):
        check_doc_hash({"spec_sha256": "0" * 64}, "F3")
    check_doc_hash({"no_hash": 1}, "attention")   # no recorded hash: accepted


def test_q_is_exact_from_decimal_text():
    assert q(0.1) == F(1, 10)
    assert q("0.025") == F(1, 40)
    assert q(None) is None
    with pytest.raises(InputError):
        q(True)


@pytest.mark.parametrize("x,expected", [(2.345, F("2.35")), (2.344999, F("2.34")), (2.355, F("2.36")),
                                        (2.005, F("2.01")), (0, F(0))])
def test_round2_is_half_up_on_the_decimal_value(x, expected):
    # 2.355 as a float is 2.35499...; the decimal text rounds half-up to 2.36
    assert round2(q(x)) == expected


# ------------------------------------------------------------------------------------------- D1 and the gate
@pytest.mark.parametrize("r,score", [("0", 4), ("0.025", 4), ("0.0250001", 3), ("0.05", 3), ("0.0500001", 2),
                                     ("0.10", 2), ("0.1000001", 1), ("0.20", 1), ("0.2000001", 0), ("3", 0)])
def test_d1_band_boundaries_go_to_higher_score(r, score):
    assert d1_band(F(r)) == score


def test_d1_ratio_on_boundary_is_exact():
    # c_RT = 1 + 0.5 = 1.5 ticks, sigma = 60 ticks: r = 0.025 exactly -> 4 (float division could land above)
    assert d1_band((q(1.0) + HALF) / q(60.0)) == 4
    d1, bands, missing = d1_score(F(3, 2), {"30": q(30.0), "60": q(60.0), "120": q(15.0), "240": q(7.5)},
                                  ("30", "60", "120", "240"))
    # r = 0.05, 0.025, 0.10, 0.20: every one on a boundary, each taking the higher score
    assert bands == {"30": 3, "60": 4, "120": 2, "240": 1} and d1 == F(10, 4) and missing == []


def test_d1_unknown_sigma_gives_none():
    d1, bands, missing = d1_score(F(3, 2), {"30": q(30.0), "60": None, "120": q(15.0), "240": q(7.5)},
                                  ("30", "60", "120", "240"))
    assert d1 is None and missing == ["60"]


def test_sigma_gate_equality_passes_and_below_fails():
    fails, text = sigma_gate(q(3.0), F(1), HALF)
    assert not fails and text == "sigma_60 = 3.00 ticks vs 2 x (1 + 0.5) = 3.00 ticks"
    fails, text = sigma_gate(q(2.9), F(1), HALF)
    assert fails and text == "sigma_60 = 2.90 ticks vs 2 x (1 + 0.5) = 3.00 ticks"
    fails, text = sigma_gate(q(2.999), F(1), HALF)   # 2 decimals would hide the order: more digits shown
    assert fails and text == "sigma_60 = 2.9990 ticks vs 2 x (1 + 0.5) = 3.0000 ticks"


def test_sigma_gate_unknown_fails():
    fails, text = sigma_gate(None, F(1), HALF)
    assert fails and "unknown" in text


def test_sigma_gate_label_and_slip_in_text():
    fails, text = sigma_gate(q(4.0), q(1.5), F(1), "m_60")
    assert fails and text == "m_60 = 4.00 ticks vs 2 x (1.5 + 1) = 5.00 ticks"


# ------------------------------------------------------------------------------------------- D2 d terciles
def test_terciles_18_underlyings_six_each():
    counts = {f"u{i}": 100 - i for i in range(18)}
    tiers = attention_tiers(counts)
    assert [tiers[f"u{i}"][0] for i in range(18)] == [F(1)] * 6 + [HALF] * 6 + [F(0)] * 6


def test_terciles_equal_counts_take_higher_tier():
    counts = {f"u{i}": 100 - i for i in range(18)}
    counts["u6"] = counts["u5"]          # u6 ties the last top-tercile member
    counts["u12"] = counts["u11"]        # u12 ties the last middle member
    tiers = attention_tiers(counts)
    assert tiers["u6"][0] == F(1) and tiers["u12"][0] == HALF
    assert tiers["u7"][0] == HALF and tiers["u13"][0] == F(0)


def test_terciles_missing_count_is_half_u_and_excluded_from_split():
    counts = {"a": 300, "b": 200, "c": 120, "d": 120, "e": 40, "f": None}
    tiers = attention_tiers(counts)
    assert tiers["f"] == (HALF, True)
    assert [tiers[k][0] for k in "abcde"] == [F(1), F(1), HALF, HALF, F(0)]


def test_attention_count_needs_status_ok():
    assert attention_count({"count": 5, "status": 200}) == 5
    assert attention_count({"count": 5, "status": 503}) is None
    assert attention_count({"count": None, "status": 200}) is None


# ------------------------------------------------------------------------------------------- D4 L and J
@pytest.mark.parametrize("adv,lv", [(999, 2), (1000, 1), (9999, 1), (10000, 0), (250000, 0)])
def test_l_adv_boundaries(adv, lv):
    assert l_score(F(adv), None, None)[0] == lv


def test_l_unknown_adv_is_one_u_but_a_wide_spread_still_gives_two():
    lv, notes = l_score(None, None, None)
    assert lv == 1 and "(u)" in notes[0]
    assert l_score(None, F("2.5"), None)[0] == 2


@pytest.mark.parametrize("spread,lv", [("1", 0), ("1.01", 1), ("2", 1), ("2.01", 2)])
def test_l_spread_boundaries(spread, lv):
    assert l_score(F(50000), F(spread), None)[0] == lv


@pytest.mark.parametrize("touch,lv", [("1.99", 2), ("2", 1), ("4.99", 1), ("5", 0)])
def test_l_touch_boundaries(touch, lv):
    assert l_score(F(50000), None, F(touch))[0] == lv


def test_l_unsourced_spread_or_touch_does_not_count():
    assert l_score(F(50000), None, None)[0] == 0   # the caller passes None for unsourced values


def test_j_boundary_and_unknown():
    assert j_score(F(100), F(10))[0] == 0          # USD 1,000 exactly does not exceed DLL_ref
    assert j_score(F("100.001"), F(10))[0] == 1
    jv, notes = j_score(None, F(10))
    assert jv == 1 and "(u)" in notes[0]


# ------------------------------------------------------------------------------------------- D5
@pytest.mark.parametrize("start,hv", [("2017-06-30", 0), ("2017-07-01", 1), ("2020-12-31", 1), ("2021-01-01", 2),
                                      ("2017-06", 0), ("2021-01", 2)])
def test_d5_h_boundaries(start, hv):
    assert d5_h(start)[0] == hv


def test_d5_h_unknown_is_one():
    assert d5_h(None) == (1, "D5 h: MBO start unknown -> 1 (u)")
    with pytest.raises(InputError):
        d5_h("2017")


@pytest.mark.parametrize("k,kv", [(0, 0), (10, 0), (10.01, 1), (50, 1), (50.01, 2)])
def test_d5_k_boundaries(k, kv):
    assert d5_k(k, "ledger MBO")[0] == kv


def test_d5_k_unknown_is_one():
    assert d5_k(None, "unknown")[0] == 1
    assert d5_k(3.0, "unknown")[0] == 1


def test_d5_o_and_p_unknown_rules():
    assert d5_o(True)[0] == 0 and d5_o(False)[0] == 1 and d5_o(None)[0] == 1
    assert d5_p(True)[0] == 1 and d5_p(False)[0] == 0 and d5_p(None)[0] == 0


# ------------------------------------------------------------------------------------------- blind ratings
def test_blind_unknown_rules_per_criterion():
    assert blind_rated(None, 1, (0, 1), what="D2 a")[0] == 1               # D2 a unknown: 1
    assert blind_rated({"value": None, "unknown": True}, HALF, (0, HALF, 1))[0] == HALF   # D2 b: 0.5
    assert blind_rated({"value": 2, "unknown": True}, 0, (0, 1, 2))[0] == 0  # D3 items: 0 (unknown wins)
    assert blind_rated({"unknown": True}, 1, range(5))[0] == 1             # D6 unknown: 1
    with pytest.raises(InputError):
        blind_rated({"value": 3}, 0, (0, 1), what="Sat (iii)")


def test_evidence_caps_spec_section_1():
    assert cap_extreme_0_4(F(4)) == 2 and cap_extreme_0_4(F(3)) == 2 and cap_extreme_0_4(F(0)) == 1
    assert cap_extreme_0_4(F(2)) == 2 and cap_s12(F(2)) == 1 and cap_s12(F(1)) == 1
    v, note = blind_rated({"value": 4, "unverified": True}, 1, range(5), cap_extreme_0_4, "D6")
    assert v == 2 and "capped" in note
    v, note = blind_rated({"value": 4}, 1, range(5), cap_extreme_0_4, "D6")
    assert v == 4 and note is None


def test_l1_min_boundary():
    assert not below_l1_min(F(2)) and below_l1_min(F(199, 100)) and not below_l1_min(None)


# ------------------------------------------------------------------------------------------- Layer 2 rules
def _blk(m, m10, cap1=False, cap2=False, cost=10.0):
    return {"m_star": m, "m10K": m10, "above_cap": {"mu_star": cap1, "mu10K": cap2}, "cost_per_attempt": cost}


def test_e_score_formula_and_ends():
    e, m, m10, cost = e_score(_blk(0.10, 0.15))
    assert e == F(2) and m == F(1, 10) and cost == 10
    assert e_score(_blk(0.0, 0.0))[0] == 4
    assert e_score(_blk(0.20, 0.30))[0] == 0
    assert e_score(_blk(0.25, 0.45))[0] == 0          # beyond x0: floor 0


def test_e_score_above_grid_cap_scores_zero_and_infinite_m_star():
    e, m, m10, _ = e_score(_blk(None, 0.15, cap1=True))
    assert e == F("0.25") * 2 and m == float("inf")
    with pytest.raises(InputError):
        e_score(_blk(None, 0.15))


@pytest.mark.parametrize("room,band", [("4", 4), ("3.999", 3), ("3", 3), ("2", 2), ("1", 1), ("0.999", 0)])
def test_room_band_boundaries(room, band):
    assert room_band(F(room)) == band


def test_d_score_rooms_and_unknowns():
    d, ra, rb, u, lead = d_score(F(1000), F(2000), F(100), F(50), F(5))   # 1000/500 = 2, 2000/250 = 8
    assert d == F(2 + 4, 2) and ra == 2 and rb == 8
    d, _, _, u, _ = d_score(F(1000), F(2000), None, None, F(5))
    assert d == 1 and len(u) == 2                                         # unknown sigma_240 and R_d: 1 each
    d, ra, _, _, _ = d_score("none", F(2000), F(100), F(50), F(5))        # no DLL: the MLL
    assert ra == 4
    d, _, _, _, lead = d_score(None, None, F(100), F(50), F(5))
    assert d == 1 and len(lead) == 2


def test_rel_score_deductions_floor_and_unknown():
    r = lambda v: {"value": v}  # noqa: E731
    assert rel_score({"rel_age": r(0), "rel_payout": r(0), "rel_rules": r(0), "rel_regulatory": r(0)})[0] == 4
    assert rel_score({"rel_age": r(1), "rel_payout": r(1), "rel_rules": r(1), "rel_regulatory": r(2)})[0] == 0
    v, deds, lead = rel_score({"rel_age": r(1), "rel_payout": {"unknown": True}, "rel_rules": r(0),
                               "rel_regulatory": r(0)})
    assert v == 3 and deds["rel_payout"] == 0 and len(lead) == 1
    with pytest.raises(InputError):
        rel_score({"rel_regulatory": r(1)})


@pytest.mark.parametrize("pin,score", [
    ({"native_api": True, "oco_api": True, "vps_chicago": "allowed", "api_rate_limit_per_s": 10}, 4),
    ({"native_api": True, "oco_api": True, "vps_chicago": "allowed", "api_rate_limit_per_s": 9.99}, 3),
    ({"native_api": True, "oco_api": True, "vps_chicago": "allowed", "api_rate_limit_per_s": "no_limit"}, 4),
    ({"native_api": True, "oco_api": True, "vps_chicago": "prohibited", "api_rate_limit_per_s": 50}, 3),
    ({"native_api": True, "oco_api": None, "vps_chicago": "unknown", "api_rate_limit_per_s": None}, 1),
    ({}, 0),
])
def test_p_score_items_and_unknowns(pin, score):
    assert p_score(pin)[0] == score


def test_apply_patches_copies_and_validates():
    docs = {"F4": {"codes": {"CL": {"spread_S": {"value": 1}}}}}
    out = apply_patches(docs, [{"file": "F4", "path": ["codes", "CL", "spread_S"], "value": {"value": 2}}])
    assert out["F4"]["codes"]["CL"]["spread_S"]["value"] == 2
    assert docs["F4"]["codes"]["CL"]["spread_S"]["value"] == 1
    with pytest.raises(InputError):
        apply_patches(docs, [{"file": "F4", "path": ["codes", "XX", "a"], "value": 1}])
    with pytest.raises(InputError):
        apply_patches(docs, [{"file": "F9", "path": ["a"], "value": 1}])
