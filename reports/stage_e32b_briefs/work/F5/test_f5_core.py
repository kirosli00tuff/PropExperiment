"""Unit tests for f5_core (spec section 7 formulas, band rule, verdicts), synthetic inputs only."""
from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import f5_core as core  # noqa: E402

SR80 = {"disc_G3": 0.2025, "disc_G3G4": 0.2309, "test": 0.1936}


# ---------------------------------------------------------------- costs, counts, hit rates

def test_c_rt_uses_sourced_spread_plus_half_tick():
    assert core.c_rt(0.25) == (0.75, False)
    assert core.c_rt(1.0) == (1.5, False)


def test_c_rt_unsourced_spread_is_one_tick_marked_unknown():
    assert core.c_rt(None) == (1.5, True)


def test_c_rt_rejects_negative_spread():
    with pytest.raises(core.InputError):
        core.c_rt(-0.1)


def test_c_firm_adds_fee_in_ticks():
    assert core.c_firm(1.5, 1.24, 0.5) == pytest.approx(1.5 + 2.48)


@pytest.mark.parametrize("fee,v", [(1.0, 0.0), (1.0, None), (-1.0, 0.5), (None, 0.5)])
def test_c_firm_rejects_bad_inputs(fee, v):
    with pytest.raises(core.InputError):
        core.c_firm(1.5, fee, v)


@pytest.mark.parametrize("key,l_main,nmax,ncap", [
    ("1", 390, 390, 20), ("15", 390, 26, 20), ("30", 390, 13, 13), ("60", 390, 6, 6), ("120", 390, 3, 3),
    ("240", 390, 1, 1), ("240", 290, 1, 1), ("120", 290, 2, 2), ("OC", 390, 1, 1), ("cc", None, 1, 1),
    ("on", 290, 1, 1), ("240", 200, 0, 0), ("60", None, None, None)])
def test_n_max_and_n_cap(key, l_main, nmax, ncap):
    assert core.n_max(key, l_main) == nmax
    assert core.n_cap(core.n_max(key, l_main)) == ncap


def test_hit_rates_empirical_and_normal():
    p_emp, p_norm = core.hit_rate(2.0, 8.0, 10.0)
    assert p_emp == pytest.approx(0.5 + 2.0 / 16.0)
    assert p_norm == pytest.approx(0.5 + 2.0 / 15.96)


def test_hit_rate_unknown_moments_and_values_above_one_kept():
    assert core.hit_rate(2.0, None, None) == (None, None)
    assert core.hit_rate(20.0, 4.0, 5.0)[0] == pytest.approx(3.0)


def test_horizon_row_formulas_by_hand():
    row = core.horizon_row("30", {"sigma": 12.0, "m": 9.0, "n": 1000}, 390, 3.5, 1.5, SR80)
    assert row["k"] == pytest.approx(3.5 / 12.0)
    assert row["k_RT"] == pytest.approx(1.5 / 12.0)
    assert row["g_be"] == 3.5 and row["g_1"] == 4.5
    assert row["p_1_emp"] == pytest.approx(0.5 + 4.5 / 18.0)
    assert (row["n_max"], row["n_cap"], row["trades_per_year"]) == (13, 13, 13 * 252)
    assert row["e80_test"] == pytest.approx(0.1936 * 12.0 / math.sqrt(13))
    assert row["e80_disc_G3G4"] == pytest.approx(0.2309 * 12.0 / math.sqrt(13))
    assert row["gross_detect_disc_G3"] == pytest.approx(3.5 + 0.2025 * 12.0 / math.sqrt(13))
    assert row["G"] == pytest.approx(3.5 / 12.0 + 0.1936 / math.sqrt(13))


def test_horizon_row_unknown_sigma_or_zero_trades_gives_no_G():
    assert core.horizon_row("30", {"sigma": None, "m": None}, 390, 3.5, 1.5, SR80)["G"] is None
    assert core.horizon_row("240", {"sigma": 40.0, "m": 30.0}, 200, 3.5, 1.5, SR80)["G"] is None
    assert core.horizon_row("60", {"sigma": 0.0, "m": 0.0}, 390, 3.5, 1.5, SR80)["G"] is None


# ---------------------------------------------------------------- flat-by-close and latest start

@pytest.mark.parametrize("raw,status,pt", [
    ("15:10 CT", "time", "13:10"), ("3:10 PM CT", "time", "13:10"), ("16:10 ET", "time", "13:10"),
    ("13:10 PT", "time", "13:10"), ({"time": "15:10", "tz": "America/Chicago"}, "time", "13:10"),
    ({"pt": "12:55"}, "time", "12:55"), ({"value": "4:10 PM ET", "source": "x"}, "time", "13:10"),
    (None, "unknown", None), ({"value": None}, "unknown", None), ({"unknown": True}, "unknown", None),
    ("none", "none", None), (False, "none", None), ({"none": True}, "none", None)])
def test_parse_flat_by_close_forms(raw, status, pt):
    f = core.parse_flat_by_close(raw)
    assert f.status == status
    assert core.min_to_hhmm(f.pt_min) == pt


@pytest.mark.parametrize("raw", ["15:10", "25:00 CT", "15:10 XYZ", 1510, {"time": "15:10"}])
def test_parse_flat_by_close_rejects_ambiguous_or_bad(raw):
    with pytest.raises(core.InputError):
        core.parse_flat_by_close(raw)


MS, ME = 390, 780  # 06:30 and 13:00 PT


def flat(text):
    return core.parse_flat_by_close(text)


def test_latest_start_against_main_end_when_flat_is_later():
    assert core.latest_start("240", MS, ME, flat("15:10 CT")) == (ME - 240, True)


def test_latest_start_against_flat_by_close_when_flat_is_earlier():
    start, fits = core.latest_start("60", MS, ME, flat("11:00 CT"))   # 09:00 PT
    assert (start, fits) == (480, True)
    assert core.latest_start("240", MS, ME, flat("11:00 CT")) == (300, False)


def test_latest_start_exact_fit_at_main_start_is_inside():
    assert core.latest_start("60", MS, ME, flat("09:30 CT")) == (MS, True)   # 07:30 PT - 60 = 06:30
    assert core.latest_start("60", MS, ME, flat("09:29 CT"))[1] is False


def test_oc_fits_only_if_flat_not_before_main_end():
    assert core.latest_start("OC", MS, ME, flat("15:00 CT"))[1] is True     # 13:00 PT exactly
    assert core.latest_start("OC", MS, ME, flat("14:59 CT"))[1] is False
    assert core.latest_start("OC", MS, ME, flat("none"))[1] is True
    assert core.latest_start("OC", MS, ME, flat(None))[1] is None


def test_unknown_flat_by_close_leaves_fit_unknown_but_long_holds_still_bounded_by_session():
    assert core.latest_start("60", MS, ME, flat(None)) == (ME - 60, None)
    assert core.latest_start("60", 390, 420, flat(None)) == (360, False)


def test_with_prop_columns_ratios_and_does_not_mutate_inputs():
    rows, on = core.horizon_rows({"L_main": 390, "h": {"60": {"sigma": 20.0, "m": 15.0}},
                                  "OC": {"sigma": 50.0, "m": 40.0},
                                  "overnight": {"cc": {"sigma": 80.0, "m": 60.0}}}, 3.0, 1.5, SR80)
    snapshot = {k: dict(v) for k, v in rows.items()}
    r2, on2 = core.with_prop_columns(rows, on, 1000.0, 2000.0, 0.5, MS, ME, flat("15:10 CT"), False)
    assert rows == snapshot
    assert r2["60"]["dll_ratio"] == pytest.approx(1000 / (20 * 0.5))
    assert r2["60"]["mll_ratio"] == pytest.approx(2000 / (20 * 0.5))
    assert r2["60"]["latest_start_pt"] == "12:00"
    assert on2["cc"]["overnight_allowed"] is False and on2["cc"]["fits_flat_by_close"] is None
    assert r2["1"]["dll_ratio"] is None


# ---------------------------------------------------------------- band rule

def rows_with(g: dict, dll: dict | None = None, fits: dict | None = None) -> dict:
    rows = {}
    for key in core.ROW_ORDER:
        rows[key] = {"G": g.get(key), "dll_ratio": (dll or {}).get(key, 10.0),
                     "fits_flat_by_close": (fits or {}).get(key, True), "k": None,
                     "G_cost_term": None, "G_power_term": None}
    return rows


BASE_G = {"1": 1.0, "2": 0.8, "5": 0.5, "15": 0.35, "30": 0.25, "60": 0.20, "120": 0.21, "240": 0.30, "OC": 0.29}


def test_band_includes_exact_boundary_and_excludes_just_above():
    g = dict(BASE_G, **{"30": 0.20 * 1.10, "120": 0.20 * 1.10 * (1 + 1e-9)})
    b, rows = core.band(rows_with(g), 0.20)
    assert "30" in b["members"] and "120" not in b["members"]
    assert rows["30"]["in_band"] is True and rows["120"]["in_band"] is False
    assert rows["30"]["G_over_min"] == pytest.approx(1.10)


def test_band_dll_ratio_two_is_inside_and_below_two_is_out():
    b, _ = core.band(rows_with(BASE_G, dll={"60": 2.0, "120": 1.999}), 0.20)
    assert b["members"] == ["60"]
    assert "DLL_f / (sigma_h v) = 1.999 < 2" in b["excluded"]["120"][0]


def test_band_unknown_dll_or_fit_does_not_exclude_but_is_marked():
    b, _ = core.band(rows_with(BASE_G, dll={"60": None}, fits={"120": None}), 0.20)
    assert b["members"] == ["60", "120"]
    assert b["unknown_conditions"] == {"60": ["DLL_f / (sigma_h v) unknown"], "120": ["flat-by-close fit unknown"]}


def test_band_flat_by_close_excludes_long_holds():
    b, _ = core.band(rows_with(BASE_G, fits={"120": False, "240": False, "OC": False}), 0.20)
    assert b["members"] == ["60"]
    assert b["excluded"]["120"] == ["hold does not fit before flat-by-close"]


def test_band_non_contiguous_reports_all_members():
    g = dict(BASE_G, **{"15": 0.21, "30": 0.30, "60": 0.20, "120": 0.35, "240": 0.36, "OC": 0.21})
    b, _ = core.band(rows_with(g), 0.20)
    assert b["members"] == ["15", "60", "OC"]
    assert (b["shortest"], b["longest"], b["contiguous"]) == ("15", "OC", False)


def test_band_contiguous_run():
    b, _ = core.band(rows_with(BASE_G), 0.20)
    assert b["members"] == ["60", "120"] and b["contiguous"] is True


def test_band_empty_when_every_candidate_fails_a_condition():
    b, _ = core.band(rows_with(BASE_G, dll={k: 1.0 for k in core.BAND_CANDIDATES}), 0.20)
    assert b["members"] == [] and b["shortest"] is None and b["contiguous"] is False
    assert set(b["excluded"]) == set(core.BAND_CANDIDATES)


def test_band_with_unknown_g_minimum_is_empty():
    b, _ = core.band(rows_with({}), None)
    assert b["members"] == []


def test_g_minimum_spans_short_oc_and_overnight_rows_with_ties():
    rows = rows_with(dict(BASE_G, **{"240": 0.20}))
    gmin, argmin = core.g_minimum(rows, {"cc": {"G": 0.25}, "on": {"G": None}})
    assert gmin == 0.20 and argmin == ["60", "240"]
    gmin, argmin = core.g_minimum(rows, {"cc": {"G": 0.15}, "on": {"G": 0.15}})
    assert argmin == ["cc", "on"]


def test_band_context_power_crossover_and_k_steps():
    rows = rows_with(BASE_G)
    for key, (k, cost, power) in {"1": (2.0, 1.0, 0.04), "2": (1.5, 0.8, 0.04), "5": (1.0, 0.5, 0.04),
                                  "15": (0.6, 0.3, 0.04), "30": (0.4, 0.2, 0.05), "60": (0.3, 0.12, 0.08),
                                  "120": (0.2, 0.1, 0.11), "240": (0.15, 0.07, 0.19),
                                  "OC": (0.1, 0.05, 0.19)}.items():
        rows[key] = {**rows[key], "k": k, "G_cost_term": cost, "G_power_term": power}
    ctx = core.band_context(rows)
    assert ctx["power_term_exceeds_cost_from"] == "120"
    assert ctx["k_step_ratios"]["1->2"] == pytest.approx(0.75)


# ---------------------------------------------------------------- verdicts

def test_verdict_holds():
    v = core.verdict(["30", "60", "120"], ["60"])
    assert v["value"] == "holds"


def test_verdict_partly_when_band_also_contains_oc():
    assert core.verdict(["120", "240", "OC"], ["240"])["value"] == "partly"


def test_verdict_partly_when_oc_is_the_only_member_but_min_is_intraday():
    v = core.verdict(["OC"], ["60"])
    assert v["value"] == "partly" and v["reason"] == "B contains only OC"


def test_verdict_fails_on_empty_band():
    v = core.verdict([], ["60"])
    assert v["value"] == "fails" and "B is empty" in v["reason"]


def test_verdict_fails_when_min_at_one_or_two_minutes_even_with_a_band():
    assert core.verdict(["5"], ["1"])["value"] == "fails"
    assert core.verdict(["5", "15"], ["2", "5"])["value"] == "fails"


def test_verdict_fails_when_min_only_at_oc_or_overnight():
    assert core.verdict(["240", "OC"], ["OC"])["value"] == "fails"
    assert core.verdict(["240"], ["cc"])["value"] == "fails"
    assert core.verdict(["240", "OC"], ["OC", "on"])["value"] == "fails"


def test_verdict_tie_between_intraday_and_oc_is_not_only_oc():
    assert core.verdict(["240", "OC"], ["240", "OC"])["value"] == "partly"


def test_verdict_fails_without_any_g():
    assert core.verdict([], [])["value"] == "fails"
