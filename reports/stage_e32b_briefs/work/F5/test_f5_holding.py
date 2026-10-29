"""End-to-end tests for f5_holding on synthetic fixtures (no real facts): validation, refusals, band, verdicts."""
from __future__ import annotations

import copy
import json
import math
import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import f5_holding as fh  # noqa: E402

SHA = fh.FROZEN_SPEC_SHA256
SR80 = {"disc_G3": 0.2025, "disc_G3G4": 0.2309, "test": 0.1936}
H = (1, 2, 5, 15, 30, 60, 120, 240)


def f3_root(scale: float, l_main: int = 390, session=("06:30", "13:00"), tick=0.25) -> dict:
    """Random-walk sigma_h = scale sqrt(h), m_h = 0.8 sigma_h; OC over the whole session."""
    return {"status": "owned", "oc1_source": None, "tick_size": tick, "L_main": l_main,
            "main_session_pt": list(session),
            "h": {str(h): {"sigma": scale * math.sqrt(h), "m": 0.8 * scale * math.sqrt(h), "n": 1000} for h in H},
            "OC": {"sigma": scale * math.sqrt(l_main), "m": 0.8 * scale * math.sqrt(l_main), "n": 250},
            "overnight": {"cc": {"sigma": 80.0, "m": 64.0, "n": 249}, "on": {"sigma": 30.0, "m": 24.0, "n": 249}}}


def base_docs() -> dict:
    f3 = {"spec_sha256": SHA, "roots": {"AAA": f3_root(3.0), "BBB": f3_root(3.0, 290, ("06:30", "11:20"), 0.5)}}
    codes = {
        "AAA": {"tick_size": 0.25, "tick_value_usd": 0.5, "spread_S": {"value": 1.0, "sourced": True, "item": "x"},
                "pauses": [], "main_session_pt": ["06:30", "13:00"]},
        "BBB": {"tick_size": 0.5, "tick_value_usd": 0.5, "spread_S": {"value": None, "sourced": False, "item": None},
                "pauses": [{"start_pt": "05:45", "end_pt": "06:30", "what": "break"}], "main_session_pt": None},
    }
    firms = {
        "F1": {"dll_50k": 1000, "mll_50k": 2000, "mll_type": "trailing", "flat_by_close": "15:10 CT",
               "overnight": {"allowed": False}, "news_windows": [{"event": "FOMC", "before": 2, "after": 2}]},
        "F2": {"dll_50k": "none", "mll_50k": 2000, "mll_type": "eod", "flat_by_close": "09:30 CT",
               "overnight": {"allowed": False}, "news_windows": []},
        "F3": {"dll_50k": 10, "mll_50k": 2000, "mll_type": "eod", "flat_by_close": None,
               "overnight": {}, "news_windows": []},
    }
    pairs = {
        "F1|AAA": {"listed_50k": True, "fee_rt_usd": 1.0, "fee_kind": "stated", "news_window_items": []},
        "F2|AAA": {"listed_50k": True, "fee_rt_usd": 1.0, "fee_kind": "stated", "news_window_items": []},
        "F3|AAA": {"listed_50k": True, "fee_rt_usd": 1.0, "fee_kind": "RR-05 (u)", "news_window_items": []},
        "F1|BBB": {"listed_50k": True, "fee_rt_usd": 9.25, "fee_kind": "stated", "news_window_items": []},
    }
    f4 = {"spec_sha256": SHA, "codes": codes, "firms": firms, "pairs": pairs}
    sr80 = {"spec_sha256": SHA, "SR80": dict(SR80), "cross_check": {"pass": True}}
    sel = {"spec_sha256": SHA, "layer1_survivors": ["AAA", "BBB"],
           "top15": [{"rank": 1, "firm": "F1", "code": "AAA"}, {"rank": 2, "firm": "F2", "code": "AAA"},
                     {"rank": 3, "firm": "F3", "code": "AAA"}, {"rank": 4, "firm": "F1", "code": "BBB"}]}
    return {"f3": f3, "f4": f4, "sr80": sr80, "selection": sel}


def write(tmp: Path, docs: dict) -> dict:
    paths = {}
    for k, doc in docs.items():
        paths[k] = tmp / f"{k}.json"
        paths[k].write_text(json.dumps(doc))
    paths["out"], paths["md"] = tmp / "out.json", tmp / "out.md"
    return paths


@pytest.fixture()
def result(tmp_path):
    return fh.build(write(tmp_path, base_docs()))


def g(c: float, sigma: float, ncap: int) -> float:
    return c / sigma + SR80["test"] / math.sqrt(ncap)


# ---------------------------------------------------------------- refusals

def test_refuses_when_spec_hash_differs(tmp_path):
    bad = tmp_path / "spec.md"
    shutil.copy(fh.SPEC, bad)
    bad.write_bytes(bad.read_bytes() + b"\n")
    with pytest.raises(fh.SpecHashError):
        fh.build(write(tmp_path, base_docs()), bad)


def test_main_returns_2_and_writes_nothing_on_refusal(tmp_path, capsys):
    docs = base_docs()
    docs["f3"]["spec_sha256"] = "0" * 64
    paths = write(tmp_path, docs)
    argv = ["f5"] + [x for k in ("f3", "f4", "sr80", "selection", "out", "md") for x in (f"--{k}", str(paths[k]))]
    assert fh.main(argv) == 2
    assert not paths["out"].exists()
    assert "refused" in capsys.readouterr().err


@pytest.mark.parametrize("doc", ["f3", "f4", "sr80", "selection"])
def test_refuses_input_without_frozen_hash(tmp_path, doc):
    docs = base_docs()
    del docs[doc]["spec_sha256"]
    with pytest.raises(fh.SpecHashError):
        fh.build(write(tmp_path, docs))


def test_refuses_sr80_without_passed_cross_check(tmp_path):
    docs = base_docs()
    docs["sr80"]["cross_check"]["pass"] = False
    with pytest.raises(fh.InputError):
        fh.build(write(tmp_path, docs))


@pytest.mark.parametrize("mutate", [
    lambda d: d["selection"]["top15"].__setitem__(1, {"rank": 3, "firm": "F2", "code": "AAA"}),
    lambda d: d["selection"]["top15"].append({"rank": 5, "firm": "F9", "code": "AAA"}),
    lambda d: d["selection"].__setitem__("layer1_survivors", ["AAA"]),
    lambda d: d["selection"].__setitem__("layer1_survivors", ["AAA", "BBB", "NQ"]),
    lambda d: d["selection"]["top15"].extend({"rank": i, "firm": "F1", "code": "AAA"} for i in range(5, 17)),
    lambda d: d["f4"]["pairs"]["F1|AAA"].__setitem__("listed_50k", False),
    lambda d: d["f4"]["codes"]["AAA"].__setitem__("tick_size", 0.5),
    lambda d: d["f4"]["pairs"]["F1|AAA"].__setitem__("fee_rt_usd", None),
    lambda d: d["f3"]["roots"]["AAA"]["h"]["60"].__setitem__("sigma", None),
    lambda d: d["f4"]["firms"]["F1"].__setitem__("flat_by_close", "15:10"),
])
def test_refuses_inconsistent_inputs(tmp_path, mutate):
    docs = copy.deepcopy(base_docs())
    mutate(docs)
    with pytest.raises(fh.InputError):
        fh.build(write(tmp_path, docs))


# ---------------------------------------------------------------- values

def test_survivor_rows_use_c_rt_and_unsourced_spread_is_one_tick(result):
    a, b = result["survivors"]["AAA"], result["survivors"]["BBB"]
    assert a["c_RT"] == 1.5 and a["S_unknown"] is False
    assert b["c_RT"] == 1.5 and b["S_unknown"] is True and b["u"]
    assert a["rows"]["60"]["G"] == pytest.approx(g(1.5, 3 * math.sqrt(60), 6))
    assert b["rows"]["240"]["n_max"] == 1 and b["rows"]["120"]["n_cap"] == 2
    assert b["pauses"][0]["relation_to_main_session"] == "adjacent"


def test_pair_holds_with_band_60_120(result):
    p = result["pairs"]["F1|AAA"]
    assert p["c_f"] == pytest.approx(1.5 + 1.0 / 0.5)
    assert p["rows"]["120"]["G"] == pytest.approx(g(3.5, 3 * math.sqrt(120), 3))
    assert p["G_argmin"] == ["120"]
    assert p["band"]["members"] == ["60", "120"]
    assert p["verdict"]["value"] == "holds"
    assert p["rows"]["240"]["latest_start_pt"] == "09:00"
    assert p["rows"]["60"]["dll_ratio"] == pytest.approx(1000 / (3 * math.sqrt(60) * 0.5))
    assert p["flat_minus_main_end_min"] == 10
    assert p["overnight_rows"]["cc"]["overnight_allowed"] is False


def test_pair_flat_by_close_cuts_the_band_and_no_dll_uses_mll(result):
    p = result["pairs"]["F2|AAA"]          # flat 09:30 CT = 07:30 PT: one hour after the 06:30 PT open
    assert p["DLL_f"] == 2000 and p["dll_source"].startswith("mll_50k")
    assert p["rows"]["60"]["fits_flat_by_close"] is True and p["rows"]["60"]["latest_start_pt"] == "06:30"
    assert p["rows"]["120"]["fits_flat_by_close"] is False
    assert p["band"]["members"] == ["60"]
    assert p["band"]["excluded"]["120"] == ["hold does not fit before flat-by-close"]
    assert p["verdict"]["value"] == "holds"


def test_pair_empty_band_fails_and_unknowns_are_listed(result):
    p = result["pairs"]["F3|AAA"]          # DLL 10 USD: ratio < 2 at every candidate inside 1.10 min G
    assert p["band"]["members"] == []
    assert p["verdict"]["value"] == "fails"
    assert any("flat-by-close unknown" in x for x in p["u"]) and any("RR-05" in x for x in p["u"])
    assert any("overnight allowed" in x for x in p["u"])


def test_pair_min_at_overnight_fails(result):
    p = result["pairs"]["F1|BBB"]          # c_f = 1.5 + 18.5 = 20 ticks: cc (sigma 80) gives the lowest G
    assert p["c_f"] == pytest.approx(20.0)
    assert p["G_argmin"] == ["cc"]
    assert p["verdict"]["value"] == "fails" and "only at cc" in p["verdict"]["reason"]


def test_main_writes_json_and_markdown(tmp_path, capsys):
    paths = write(tmp_path, base_docs())
    argv = ["f5"] + [x for k in ("f3", "f4", "sr80", "selection", "out", "md") for x in (f"--{k}", str(paths[k]))]
    assert fh.main(argv) == 0
    out = json.loads(paths["out"].read_text())
    assert set(out["pairs"]) == {"F1|AAA", "F2|AAA", "F3|AAA", "F1|BBB"}
    assert out["inputs"]["f4"]["sha256"] == fh.sha256_of(paths["f4"])
    md = paths["md"].read_text()
    assert "### 1. F1|AAA: B = 60, 120; prior holds" in md
    assert "holds 2, partly 0, fails 2" in capsys.readouterr().out


def test_accepts_score_output_handoff_as_selection(tmp_path):
    docs = base_docs()
    sel = docs.pop("selection")
    docs["selection"] = {"spec_sha256": SHA, "primary": {"f5_handoff": {
        "layer1_survivors": [{"code": c, "family": "x", "f3_status": "owned"} for c in sel["layer1_survivors"]],
        "top15": [{**e, "S": 3.1, "S_rounded": 3.1, "L1": 3.0, "L2": 3.2} for e in sel["top15"]]}}}
    res = fh.build(write(tmp_path, docs))
    assert res["inputs"]["selection_form"] == "score output primary.f5_handoff"
    assert list(res["pairs"]) == ["F1|AAA", "F2|AAA", "F3|AAA", "F1|BBB"]


def test_refuses_handoff_with_non_object_pairs(tmp_path):
    docs = base_docs()
    docs["selection"]["top15"] = ["F1|AAA"]
    with pytest.raises(fh.InputError):
        fh.build(write(tmp_path, docs))
