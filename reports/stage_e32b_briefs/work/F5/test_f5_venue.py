"""Tests for the own-broker venue rows (f5_venue.py and f5_holding --venue-file), synthetic inputs only.

Lead rulings under test (briefs/brief_wave_c.md C5a): LR-F5-IBKR (c_f with F_rt = 2 x per-side fee; band on G only;
overnight rows carry the overnight margin) and LR-Q6d (margin vs ceiling, sigma_day = sigma_cc x v vs 2% of it).
"""
from __future__ import annotations

import copy
import json
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import f5_core as core  # noqa: E402
import f5_holding as fh  # noqa: E402
import f5_venue as venue  # noqa: E402
from test_f5_holding import SHA, SR80, base_docs, write  # noqa: E402


def venue_doc() -> dict:
    return {"spec_sha256": SHA, "venue": "IBKR (synthetic)", "source": "synthetic", "fee_rule": "per side sum",
            "overnight_position_fee": {"usd_per_contract_per_night": {"meets margin requirements": 0.1}},
            "overnight_holds_allowed": True, "dll": None, "mll": None, "flat_by_close": None,
            "capital_ceiling_usd": None, "limits_note": "own account",
            "codes": {
                "AAA": {"fee_per_side_usd": 1.0, "fee_rt_usd": 2.0, "fee_status": "published",
                        "margin_intraday_initial_usd": 7000.0, "margin_overnight_initial_usd": 7000.0,
                        "margin_overnight_maintenance_usd": 5000.0},
                "BBB": {"fee_per_side_usd": 0.5, "fee_rt_usd": 1.0, "fee_status": "published",
                        "margin_intraday_initial_usd": 500.0, "margin_overnight_initial_usd": 600.0,
                        "margin_overnight_maintenance_usd": 400.0}}}


def run(tmp_path, docs=None, vdoc=None):
    docs = docs or base_docs()
    paths = write(tmp_path, docs)
    if vdoc is not None:
        paths["venue"] = tmp_path / "venue.json"
        paths["venue"].write_text(json.dumps(vdoc))
    return fh.build(paths)


@pytest.fixture()
def ob(tmp_path):
    return run(tmp_path, vdoc=venue_doc())["own_broker"]


def g_expected(c: float, sigma: float, ncap: int) -> float:
    return c / sigma + SR80["test"] / math.sqrt(ncap)


# ---------------------------------------------------------------- unchanged without the venue file

def test_no_venue_file_means_no_own_broker_block(tmp_path):
    res = run(tmp_path)
    assert "own_broker" not in res
    assert "venue" not in res["inputs"]
    assert "Own-broker" not in fh.render_md(res)


def test_firm_rows_identical_with_and_without_venue(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    a = run(tmp_path / "a")
    b = run(tmp_path / "b", vdoc=venue_doc())
    assert a["pairs"] == b["pairs"]
    assert a["survivors"] == b["survivors"]
    assert b["inputs"]["venue"]["sha256"] == fh.sha256_of(tmp_path / "b" / "venue.json")


# ---------------------------------------------------------------- costs (LR-F5-IBKR)

def test_rows_for_every_selected_code(ob):
    assert list(ob["rows"]) == ["ibkr|AAA", "ibkr|BBB"]
    assert ob["not_computed"] == {}


def test_c_f_uses_twice_the_per_side_fee(ob):
    a, b = ob["rows"]["ibkr|AAA"], ob["rows"]["ibkr|BBB"]
    assert a["c_RT"] == pytest.approx(1.5) and a["fee_rt_usd"] == pytest.approx(2.0)
    assert a["c_f"] == pytest.approx(1.5 + 2 * 1.0 / 0.5)
    assert a["fee_ticks"] == pytest.approx(4.0)
    assert b["S_unknown"] is True and b["c_f"] == pytest.approx(1.5 + 2 * 0.5 / 0.5)
    assert a["DLL_f"] is None and a["MLL_f"] is None and a["flat_by_close"] == "none (own account)"


def test_g_rows_use_venue_cost(ob):
    a = ob["rows"]["ibkr|AAA"]
    assert a["rows"]["60"]["G"] == pytest.approx(g_expected(5.5, 3 * math.sqrt(60), 6))
    assert a["rows"]["OC"]["G"] == pytest.approx(g_expected(5.5, 3 * math.sqrt(390), 1))
    assert a["overnight_rows"]["cc"]["G"] == pytest.approx(g_expected(5.5, 80.0, 1))


def test_fee_rt_inconsistent_with_per_side_is_refused(tmp_path):
    v = venue_doc()
    v["codes"]["AAA"]["fee_rt_usd"] = 3.0
    with pytest.raises(fh.InputError, match="2 x fee_per_side_usd"):
        run(tmp_path, vdoc=v)


def test_unpublished_fee_is_listed_not_computed(tmp_path):
    v = venue_doc()
    v["codes"]["AAA"].update({"fee_per_side_usd": None, "fee_rt_usd": None, "fee_status": "not published"})
    obk = run(tmp_path, vdoc=v)["own_broker"]
    assert list(obk["rows"]) == ["ibkr|BBB"]
    assert "not published" in obk["not_computed"]["AAA"]


def test_code_missing_from_venue_file_is_listed(tmp_path):
    v = venue_doc()
    del v["codes"]["BBB"]
    obk = run(tmp_path, vdoc=v)["own_broker"]
    assert obk["not_computed"] == {"BBB": "code not in the venue file"}


# ---------------------------------------------------------------- refusals

def test_venue_without_frozen_hash_is_refused(tmp_path):
    v = venue_doc()
    del v["spec_sha256"]
    with pytest.raises(fh.SpecHashError):
        run(tmp_path, vdoc=v)


@pytest.mark.parametrize("key,val", [("dll", 1000), ("mll", 2000), ("flat_by_close", "15:10 CT")])
def test_venue_stating_a_prop_limit_is_refused(tmp_path, key, val):
    v = venue_doc()
    v[key] = val
    with pytest.raises(fh.InputError, match="LR-F5-IBKR"):
        run(tmp_path, vdoc=v)


def test_venue_without_codes_is_refused(tmp_path):
    v = venue_doc()
    del v["codes"]
    with pytest.raises(fh.InputError, match="codes"):
        run(tmp_path, vdoc=v)


def test_negative_margin_is_refused(tmp_path):
    v = venue_doc()
    v["codes"]["BBB"]["margin_intraday_initial_usd"] = -1
    with pytest.raises(fh.InputError):
        run(tmp_path, vdoc=v)


# ---------------------------------------------------------------- band on G only, verdict

def test_band_is_g_only_and_matches_independent_computation(ob):
    a = ob["rows"]["ibkr|AAA"]
    allg = {k: r["G"] for k, r in list(a["rows"].items()) + list(a["overnight_rows"].items())}
    gmin = min(allg.values())
    expect = [k for k in core.BAND_CANDIDATES if allg[k] <= 1.10 * gmin]
    assert a["G_min"] == pytest.approx(gmin)
    assert a["G_argmin"] == ["cc"]
    assert a["band"]["members"] == expect == ["120", "OC"]
    assert a["band"]["contiguous"] is False
    assert a["band"]["rule"] == venue.BAND_RULE
    assert all(not any("DLL" in w or "flat" in w for w in why) for why in a["band"]["excluded"].values())


def test_verdict_uses_spec7_rule(ob):
    assert ob["rows"]["ibkr|AAA"]["verdict"] == {"value": "fails", "reason": "min G lies only at cc"}


def test_band_boundary_is_inclusive():
    rows = {k: {"G": 2.0} for k in core.ROW_ORDER}
    rows["5"] = {"G": 1.0}
    rows["15"] = {"G": 1.10}
    rows["30"] = {"G": 1.10 * (1 + 1e-9)}
    b, out = venue.band_g_only(rows, 1.0)
    assert b["members"] == ["5", "15"]
    assert out["15"]["in_band"] is True and out["30"]["in_band"] is False
    assert out["30"]["G_over_min"] == pytest.approx(1.10)


def test_band_with_unknown_g_excludes_that_h():
    rows = {k: {"G": 1.0} for k in core.ROW_ORDER}
    rows["OC"] = {"G": None}
    b, _ = venue.band_g_only(rows, 1.0)
    assert "OC" not in b["members"] and "G unknown" in b["excluded"]["OC"][0]
    assert venue.band_g_only(rows, None)[0]["members"] == []


def test_overnight_rows_carry_overnight_margin_and_never_enter_band(ob):
    a = ob["rows"]["ibkr|AAA"]
    for key in ("cc", "on"):
        r = a["overnight_rows"][key]
        assert r["margin_overnight_initial_usd"] == 7000.0
        assert r["margin_overnight_maintenance_usd"] == 5000.0
        assert r["overnight_allowed"] is True
        assert key not in a["band"]["members"]


def test_session_columns_and_flag_when_band_member_does_not_fit(tmp_path):
    # L_main 390 inside a 120-minute session window: a 240-minute hold cannot fit; make 240 the G minimum.
    root = {"status": "owned", "tick_size": 0.25, "L_main": 390, "main_session_pt": ["06:30", "08:30"],
            "h": {str(h): {"sigma": (1000.0 if h == 240 else 0.1), "m": 0.1, "n": 10} for h in core.INTRADAY_H},
            "OC": {"sigma": 0.1, "m": 0.1, "n": 10},
            "overnight": {"cc": {"sigma": 0.1, "m": 0.1, "n": 10}, "on": {"sigma": 0.1, "m": 0.1, "n": 10}}}
    entry = venue_doc()["codes"]["AAA"]
    blk = venue.venue_block("ZZZ", root, 0.5, 1.5, False, entry, (1.0, 2.0), SR80, 390, 510, 6000.0, True, True,
                            None)
    assert blk["band"]["members"] == ["240"]
    assert blk["rows"]["240"]["fits_main_session"] is False
    assert blk["rows"]["60"]["fits_main_session"] is True and blk["rows"]["60"]["latest_start_pt"] == "07:30"
    assert blk["rows"]["OC"]["latest_start_pt"] == "06:30"
    assert any("does not fit inside the main session" in n for n in blk["u"])


# ---------------------------------------------------------------- Q6 inputs (LR-Q6d)

def test_q6_inputs_default_ceiling(ob):
    a, b = ob["rows"]["ibkr|AAA"]["Q6_inputs"], ob["rows"]["ibkr|BBB"]["Q6_inputs"]
    assert ob["capital_ceiling_usd"] == 6000.0 and ob["capital_ceiling_u"] is True
    assert a["margin_intraday_exceeds_ceiling"] is True and a["margin_overnight_exceeds_ceiling"] is True
    assert b["margin_intraday_exceeds_ceiling"] is False and b["margin_overnight_exceeds_ceiling"] is False
    assert a["sigma_day_usd"] == pytest.approx(80.0 * 0.5) and a["sigma_day_limit_usd"] == pytest.approx(120.0)
    assert a["sigma_day_exceeds_limit"] is False
    assert a["sigma_OC_usd"] == pytest.approx(3 * math.sqrt(390) * 0.5)
    assert any("capital ceiling" in n for n in ob["rows"]["ibkr|AAA"]["u"])


def test_q6_inputs_with_stated_ceiling(tmp_path):
    v = venue_doc()
    v["capital_ceiling_usd"] = 400.0
    obk = run(tmp_path, vdoc=v)["own_broker"]
    b = obk["rows"]["ibkr|BBB"]["Q6_inputs"]
    assert obk["capital_ceiling_u"] is False and b["capital_ceiling_u"] is False
    assert b["margin_intraday_exceeds_ceiling"] is True
    assert b["sigma_day_limit_usd"] == pytest.approx(8.0) and b["sigma_day_exceeds_limit"] is True
    assert not any("capital ceiling" in n for n in obk["rows"]["ibkr|BBB"]["u"])


def test_q6_equality_does_not_exceed():
    root = {"overnight": {"cc": {"sigma": 240.0}}, "OC": {"sigma": None}}
    mg = {"margin_intraday_initial_usd": 6000.0, "margin_overnight_initial_usd": None,
          "margin_overnight_maintenance_usd": None}
    q = venue.q6_inputs(root, 0.5, mg, 6000.0, True)
    assert q["margin_intraday_exceeds_ceiling"] is False and q["margin_overnight_exceeds_ceiling"] is None
    assert q["sigma_day_usd"] == pytest.approx(120.0) and q["sigma_day_exceeds_limit"] is False
    assert q["sigma_OC_usd"] is None


def test_unknown_margin_and_overnight_permission_are_marked(tmp_path):
    v = venue_doc()
    v["codes"]["BBB"]["margin_overnight_initial_usd"] = None
    v["overnight_holds_allowed"] = None
    obk = run(tmp_path, vdoc=v)["own_broker"]
    u = obk["rows"]["ibkr|BBB"]["u"]
    assert "margin_overnight_initial_usd unknown (u)" in u and "overnight allowed: unknown (u)" in u
    assert obk["rows"]["ibkr|BBB"]["Q6_inputs"]["margin_overnight_exceeds_ceiling"] is None


def test_capital_ceiling_must_be_positive():
    with pytest.raises(core.InputError):
        venue.capital_ceiling({"capital_ceiling_usd": 0})


# ---------------------------------------------------------------- CLI

def test_cli_with_venue_file_writes_own_broker_section(tmp_path, capsys):
    paths = write(tmp_path, base_docs())
    vpath = tmp_path / "venue.json"
    vpath.write_text(json.dumps(venue_doc()))
    argv = ["f5"] + [x for k in ("f3", "f4", "sr80", "selection", "out", "md") for x in (f"--{k}", str(paths[k]))]
    assert fh.main(argv + ["--venue-file", str(vpath)]) == 0
    out = json.loads(paths["out"].read_text())
    assert sorted(out["own_broker"]["rows"]) == ["ibkr|AAA", "ibkr|BBB"]
    md = paths["md"].read_text()
    assert "## Own-broker venue" in md and "### ibkr|AAA" in md
    assert "F5 own broker: 2 rows" in capsys.readouterr().out


def test_cli_venue_refusal_writes_nothing(tmp_path):
    paths = write(tmp_path, base_docs())
    v = venue_doc()
    v["dll"] = 500
    vpath = tmp_path / "venue.json"
    vpath.write_text(json.dumps(v))
    argv = ["f5"] + [x for k in ("f3", "f4", "sr80", "selection", "out", "md") for x in (f"--{k}", str(paths[k]))]
    assert fh.main(argv + ["--venue-file", str(vpath)]) == 2
    assert not paths["out"].exists()


def test_selected_codes_are_survivors_then_top15_codes(tmp_path):
    docs = copy.deepcopy(base_docs())
    docs["selection"]["layer1_survivors"] = ["BBB", "AAA"]
    obk = run(tmp_path, docs=docs, vdoc=venue_doc())["own_broker"]
    assert list(obk["rows"]) == ["ibkr|BBB", "ibkr|AAA"]
