"""Tests for the R2 scripts (build_combos.py arithmetic, the combinations file schema, merge_q.py refusals, the
rating file's blinding). Synthetic ratings only; no market data, no outcome.

Run: uv run pytest -q -p no:cacheprovider reports/stage_e32b_briefs/work/R2/test_r2.py
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_combos as BC  # noqa: E402
import merge_q as MQ  # noqa: E402
from r2_common import (  # noqa: E402
    BAND_H, COMBOS_DETAIL, COMBOS_UNRATED, DOSSIERS_RATING_MD, SPEC_SHA256, T_TEST, VENUES, load,
)

REQ_POS = ("c_f_ticks", "sigma_hc_ticks", "tick_value_usd", "K_test", "L_main", "n_per_day")
GATES = ("news_window_covers_event_trade", "overnight_needed_but_prohibited", "holds_past_flat_by_close")


@pytest.fixture(scope="module")
def unrated():
    return load(COMBOS_UNRATED)


@pytest.fixture(scope="module")
def detail():
    return load(COMBOS_DETAIL)


# ------------------------------------------------------------------------------------------- arithmetic
def test_k_year_continuous_is_ncap_times_252():
    assert BC.k_year("F11", {"events_per_year": None, "trades_per_event": None}, 13) == 13 * 252


def test_k_year_event_is_events_times_trades():
    assert BC.k_year("F05", {"events_per_year": 8, "trades_per_event": 1}, 13) == 8.0
    assert BC.k_year("F01", {"events_per_year": 252, "trades_per_event": 1}, 13) == 252.0


def test_h_c_is_lowest_worst_member_g():
    a = {"rows": {"15": {"G": 0.10}, "30": {"G": 0.09}}}
    b = {"rows": {"15": {"G": 0.11}, "30": {"G": 0.12}}}
    h, worst = BC.h_c_of([a, b], ["15", "30"])
    assert h == "15" and worst == {"15": 0.11, "30": 0.12}


def test_continuous_e80_equals_f5(detail):
    for c in detail["combinations"]:
        for m in c["members"]:
            if m["family_kind"] == "continuous":
                assert m["e80_ticks"]["test"] == pytest.approx(m["f5_check_e80_test_continuous"], abs=1e-3)


def test_e80_formula_and_hit_rates(detail):
    sr = detail["SR80"]["test"]
    for c in detail["combinations"]:
        for m in c["members"]:
            e = sr * math.sqrt(T_TEST) * m["sigma_hc_ticks"] / math.sqrt(m["K_test"])
            assert m["e80_ticks"]["test"] == pytest.approx(e, rel=1e-3)
            assert m["p_be_emp"] == pytest.approx(0.5 + m["c_f_ticks"] / (2 * m["m_hc_ticks"]), abs=1e-3)
            assert m["K_test"] == pytest.approx(m["K_year"] * 870 / 252, abs=2e-3)


def test_queue_variant_only_on_rithmic_routes(detail):
    for c in detail["combinations"]:
        for m in c["members"]:
            has = "queue_limit_variant" in m
            assert has == (c["venue"] in BC.RITHMIC_ROUTES)
            if has:
                q = m["queue_limit_variant"]
                exp = m["c_f_ticks"] - (m["S"] / 2 + 0.25) + 0.970
                assert q["c_lim_passive_entry_market_exit_ticks"] == pytest.approx(exp, abs=1e-3)


# ------------------------------------------------------------------------------------------- schema
def test_combinations_schema(unrated):
    assert unrated["spec_sha256"] == SPEC_SHA256
    assert unrated["sr80_test"]["value"] > 0
    ids = [c["id"] for c in unrated["combinations"]]
    assert len(ids) == len(set(ids)) == 185
    for c in unrated["combinations"]:
        assert c["venue"] in VENUES
        assert (c["product"] is None) != (c["pool"] is None)
        assert c["band"] and all(h in BAND_H for h in c["band"]) and c["h_c"] in c["band"]
        assert not any(k in c for k in ("Q1", "Q2", "Q3"))
        codes = [m["code"] for m in c["members"]]
        if c["product"]:
            assert codes == [c["product"]]
        else:
            assert len(codes) >= 2 and sorted(codes) == sorted(c["pool"]["members"])
            assert not ({"YM", "MYM"} <= set(codes))
            assert "NQ" not in codes
        for m in c["members"]:
            for k in REQ_POS:
                assert isinstance(m[k], (int, float)) and m[k] > 0, (c["id"], k)
            assert set(m["gate"]) == set(GATES)
            if c["venue"] == "ibkr":
                assert m["initial_margin_usd"] > 0 and m["sigma_day_ticks"] > 0
            else:
                assert m["dll_usd"] == "none" or m["dll_usd"] > 0
                assert m["mll_usd"] > 0 and m["payout_threshold_usd"] is not None
                assert m["news_stop_events_per_week"] is not None
        d = c["data"]
        assert d["clean_test_window_months"] is not None and d["discovery_cost_usd"] is not None


def test_bands_are_f5_bands(unrated, detail):
    f5 = load(Path(BC.F5_PATH))
    for c in unrated["combinations"]:
        if c["product"] is None:
            continue
        row = (f5["own_broker"]["rows"][f"ibkr|{c['product']}"] if c["venue"] == "ibkr"
               else f5["pairs"][f"{c['venue']}|{c['product']}"])
        assert c["band"] == [h for h in BAND_H if h in row["band"]["members"]]


# ------------------------------------------------------------------------------------------- merge_q
def _ratings(unrated, **over):
    r = {c["id"]: {k: {"value": 2, "unknown": False, "reason": "synthetic"} for k in ("Q1", "Q2", "Q3")}
         for c in unrated["combinations"]}
    r.update(over)
    return {"rater": "test", "generated_pdt": "x", "ratings": r}


def test_merge_accepts_valid(unrated):
    out = MQ.merge(unrated, _ratings(unrated))
    assert all(c["Q1"]["value"] == 2 and c["Q3"]["unknown"] is False for c in out["combinations"])
    assert not any("Q1" in c for c in unrated["combinations"])          # input not mutated


@pytest.mark.parametrize("bad", [5, -1, 2.5, True, None, "3"])
def test_merge_refuses_out_of_scale(unrated, bad):
    cid = unrated["combinations"][0]["id"]
    rt = _ratings(unrated)
    rt["ratings"][cid]["Q2"] = {"value": bad, "unknown": False, "reason": "x"}
    with pytest.raises(MQ.Refused):
        MQ.merge(unrated, rt)


def test_merge_refuses_missing_and_extra(unrated):
    rt = _ratings(unrated)
    del rt["ratings"][unrated["combinations"][3]["id"]]
    with pytest.raises(MQ.Refused, match="no rating"):
        MQ.merge(unrated, rt)
    rt = _ratings(unrated)
    rt["ratings"]["C999"] = rt["ratings"][unrated["combinations"][0]["id"]]
    with pytest.raises(MQ.Refused, match="unknown ids"):
        MQ.merge(unrated, rt)


def test_merge_refuses_unknown_missing_reason_and_bad_unverified(unrated):
    cid = unrated["combinations"][1]["id"]
    for rec in ({"value": 2, "unknown": True, "reason": "x"}, {"value": 2, "unknown": False, "reason": ""},
                {"value": 2, "unknown": False, "reason": "x", "unverified": "yes"}):
        rt = _ratings(unrated)
        rt["ratings"][cid]["Q1"] = rec
        with pytest.raises(MQ.Refused):
            MQ.merge(unrated, rt)
    rt = _ratings(unrated)
    del rt["ratings"][cid]["Q3"]
    with pytest.raises(MQ.Refused):
        MQ.merge(unrated, rt)


def test_merge_cli_writes_nothing_on_refusal(unrated, tmp_path):
    rt = _ratings(unrated)
    rt["ratings"][unrated["combinations"][0]["id"]]["Q1"]["value"] = 7
    rp, op = tmp_path / "r.json", tmp_path / "out.json"
    rp.write_text(json.dumps(rt))
    assert MQ.main(["--ratings", str(rp), "--out", str(op)]) == 2 and not op.exists()
    rt = _ratings(unrated)
    rp.write_text(json.dumps(rt))
    assert MQ.main(["--ratings", str(rp), "--out", str(op)]) == 0
    assert len(json.loads(op.read_text())["combinations"]) == 185


# ------------------------------------------------------------------------------------------- blinding
def test_rating_file_lists_every_id_once_and_no_venue(unrated):
    text = Path(DOSSIERS_RATING_MD).read_text()
    for c in unrated["combinations"]:
        assert len(re.findall(rf"^\| {c['id']} \|", text, flags=re.M)) == 1, c["id"]
    body = text.split("## Evidence row catalog")[0]
    body = body[body.index("## Lead rulings"):]
    for word in ("bulenox", "topstep", "tradeify", "mffu", "lucid", "ibkr", "USD", "e80", "c_f"):
        assert not re.search(rf"\b{word}\b", body, flags=re.I), word
