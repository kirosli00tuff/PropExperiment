"""Tests for build_lead_variants.py on synthetic inputs. Run: uv run pytest -q <this file>"""
import json

import pytest

import build_lead_variants as b
from s32b_common import apply_patches

SPEC = "x" * 64


def _code(touch=None, k=1.0, p=False):
    return {"spread_S": {"value": 1, "sourced": True, "item": "I"},
            "touch": touch or {"value": None, "sourced": False, "item": None},
            "data_access": {"k_usd_month": k, "k_kind": "estimate", "p_all_read": p}}


def _f4():
    codes = {c: _code() for c in ("HG", "MNG", "BTC", "10Y", "CL", "ZM", "ETH")}
    codes["GC"] = _code({"value": 4.62, "sourced": True, "item": "METALS-3"}, k=2.0, p=True)
    codes["NG"] = _code({"value": 5, "sourced": True, "item": "NATGAS-4"}, k=3.0)
    codes["ZM"]["data_access"]["k_usd_month"] = 1.671
    codes["ETH"]["data_access"].update(k_usd_month=None, k_kind="unknown")
    return {"spec_sha256": SPEC, "codes": codes}


def _f4_smean():
    return {"codes": {
        "HG": {"spread_S_mean": None, "touch_mean": {"value": 5.35, "item": "METALS-52"}},
        "MNG": {"spread_S_mean": {"value": 2.414, "item": "NATGAS-3"}, "touch_mean": None},
        "BTC": {"spread_S_mean": {"value": 4.72, "item": "CRYPTO-2"}, "touch_mean": None},
        "10Y": {"spread_S_mean": {"value": 1.67, "item": "RATES-5"}, "touch_mean": None},
        "CL": {"spread_S_mean": None, "touch_mean": {"value": 8, "item": "CRUDE-49"}},
    }}


def _f2():
    def rec(k, kz, p, pb):
        return {"k_usd_month": k, "k_ZM": {"k_usd_month": kz}, "p": p, "p_brief": {"value": pb}}
    return {"codes": {
        "HG": rec(1.0, 3.3, 0, 0), "GC": rec(2.0, 6.5, 1, 0), "CL": rec(1.0, 1.0, 0, 0),
        "ZM": rec(1.671, 1.671, 0, 0), "ETH": rec(None, None, 0, 0),
    }}


def _blind_world():
    """Synthetic blind file, mask key and flags md for the RS-* rulings (labels are the real ones, codes invented)."""
    labels = (b.D6_SPAN_UP + b.D6_SPAN_NULLS + ["K-YBWI", "K-SLBV", "K-OJGY", "K-ZXJD"] + b.D2B_IIP + b.S1_OWN
              + b.S2_OWN + b.S3_OWN + b.EQ_S2)
    labels = list(dict.fromkeys(labels))
    contracts = {lab: f"C{i}" for i, lab in enumerate(labels)}
    d6 = {}
    for lab in labels:
        d6[contracts[lab]] = 3 if lab in b.D6_SPAN_UP else 2
    for lab in ("K-OJGY", "K-ZXJD"):
        d6[contracts[lab]] = 4
    # the threshold flag lists some labels also in D6_SPAN_UP at 3 -> 2: keep them at 3, fine
    cell = lambda v, **kw: {"value": v, "unknown": False, "reason": "r", **kw}
    s2_own = {contracts[lab] for lab in b.S2_OWN}
    codes = {c: {"D6": cell(d6[c]), "D2b": cell(1), "s1": cell(2), "s2": cell(2 if c in s2_own else 1),
                 "s3": cell(1)} for c in d6}
    key = {"contracts": contracts, "firms": {"V-FRQI": "topstep", "V-PCDG": "lucid", "V-PCAN": "tradeify",
                                             "V-CXFO": "mffu", "V-OJVP": "bulenox"}}
    f4_codes = {"MCL": "crude", "ZC": "grains", "ES": "equity", "MBT": "crypto", "GOLD": "metals"}
    pairs, f4_pairs = {}, {}
    for fm in key["firms"].values():
        for c in f4_codes:
            pairs[f"{fm}|{c}"] = {"R": cell(4), "A": cell(2)}
            f4_pairs[f"{fm}|{c}"] = {"listed_50k": c != "GOLD"}
    firms = {fm: {x: cell(1 if x == "rel_age" else 0) for x in ("rel_age", "rel_payout", "rel_rules")}
             for fm in key["firms"].values()}
    md = "\n".join(["- D6 spanning samples. " + " ".join(b.D6_SPAN_UP + b.D6_SPAN_NULLS),
                     "- D6 in-sample threshold: K-YBWI K-SLBV K-IXHJ K-ASNW K-BMTO K-KQRO K-WSRZ",
                     "- D6 K-OJGY, K-ZXJD = 4", "- D6 K-YEPF = 3 (sibling OOS row); alt 0",
                     "- Sibling-tagged items for s1/s2/s3: " + " ".join(b.S1_OWN + b.S2_OWN + b.S3_OWN),
                     "- s2 equity (K-KVJD, K-FICQ) " + " ".join(b.EQ_S2) + " = 1. Alt 2",
                     "- D2b counted the International Incentive Program: " + " ".join(b.D2B_IIP),
                     "- V-CXFO listed pairs: R = 4. Alt 3, or 1 for K-SGKW",
                     "- Listed crypto pairs: R = 4. Alt 1 if",
                     "- A V-FRQI = 3. Alt 2", "- A V-PCDG and V-CXFO = 2. Alt 3", "- A V-PCAN = 2. Alt 1"])
    return ({"codes": codes, "pairs": pairs, "firms": firms}, key, md,
            {"codes": {c: {"family": f} for c, f in f4_codes.items()}, "pairs": f4_pairs})


def _paths(tmp_path, with_econ):
    def w(name, doc):
        p = tmp_path / name
        p.write_text(json.dumps(doc))
        return str(p)
    econ = {"spec_sha256": SPEC, "pairs": {pr: {"primary": {"mu_star_mkt": 1}} for pr in b.SMEAN_ECON_PAIRS}}
    smean = {"pairs": {pr: {"primary": {"mu_star_mkt": 2}} for pr in b.SMEAN_ECON_PAIRS}}
    blind, key, md, f4rs = _blind_world()
    f4 = _f4()
    f4["codes"].update({c: {**f4["codes"].get(c, _code()), **v} for c, v in f4rs["codes"].items()})
    f4["pairs"] = f4rs["pairs"]
    (tmp_path / "flags.md").write_text(md)
    paths = {"f4": w("f4.json", f4), "blind": w("blind.json", blind), "mask_key": w("key.json", key),
             "flags_md": str(tmp_path / "flags.md"), "f4_smean": w("f4s.json", _f4_smean()), "f2_da": w("f2.json", _f2()),
             "econ": str(tmp_path / "econ.json"), "econ_smean": str(tmp_path / "econs.json"),
             "f4_smean_facts": str(tmp_path / "absent.json"), "out": str(tmp_path / "out.json")}
    if with_econ:
        w("econ.json", econ)
        w("econs.json", smean)
    return paths


def test_all_rulings_built_with_expected_counts(tmp_path):
    doc, rep = b.build(_paths(tmp_path, True))
    assert {k: v for k, v in rep["counts"].items() if k.startswith("RL-")} == {
        "RL-SMEAN": 4 + 2 + 4, "RL-KZM": 2, "RL-PBRIEF": 1, "RL-TRECENT": 1}
    assert rep["codes"]["RL-KZM"] == ["GC", "HG"]
    assert rep["codes"]["RL-PBRIEF"] == ["GC"]
    assert rep["codes"]["RL-TRECENT"] == ["GC"]
    assert not rep["pending"]
    assert [r["name"] for r in doc["rulings"]][:4] == ["RL-SMEAN", "RL-KZM", "RL-PBRIEF", "RL-TRECENT"]


def test_patches_apply_with_scorer_apply_patches(tmp_path):
    paths = _paths(tmp_path, True)
    doc, _ = b.build(paths)
    docs = {"F4": json.load(open(paths["f4"])), "econ": json.load(open(paths["econ"]))}
    smean = apply_patches(docs, doc["rulings"][0]["patches"])
    assert smean["F4"]["codes"]["HG"]["spread_S"] == {"value": 1.55, "sourced": True, "item": "METALS-50",
                                                      "clause": "S_mean variant"}
    assert smean["F4"]["codes"]["CL"]["touch"]["value"] == 8
    assert smean["econ"]["pairs"]["topstep|MNG"]["primary"] == {"mu_star_mkt": 2}
    tr = apply_patches(docs, doc["rulings"][3]["patches"])
    assert tr["F4"]["codes"]["GC"]["touch"]["value"] is None and tr["F4"]["codes"]["GC"]["touch"]["sourced"] is False
    assert tr["F4"]["codes"]["NG"]["touch"]["value"] == 5  # 2025-26 window kept
    pb = apply_patches(docs, doc["rulings"][2]["patches"])
    assert pb["F4"]["codes"]["GC"]["data_access"]["p_all_read"] is False
    assert docs["F4"]["codes"]["GC"]["data_access"]["p_all_read"] is True  # input untouched


def test_zm_and_unknown_k_codes_get_no_k_patch(tmp_path):
    doc, _ = b.build(_paths(tmp_path, True))
    codes = {p["path"][1] for p in doc["rulings"][1]["patches"]}
    assert "ZM" not in codes and "ETH" not in codes


def test_missing_econ_files_leave_econ_patches_pending_and_exit_3(tmp_path):
    paths = _paths(tmp_path, False)
    doc, rep = b.build(paths)
    assert rep["counts"]["RL-SMEAN"] == 10 - 4 and rep["pending"][0]["missing"] == ["econ", "econ_smean"]
    argv = [f"--{k.replace('_', '-')}={v}" for k, v in paths.items()]
    assert b.main(argv) == 3
    assert json.load(open(paths["out"]))["rulings"][0]["name"] == "RL-SMEAN"


def test_main_exit_0_when_everything_present(tmp_path):
    paths = _paths(tmp_path, True)
    assert b.main([f"--{k.replace('_', '-')}={v}" for k, v in paths.items()]) == 0


def test_missing_patch_path_stops(tmp_path):
    paths = _paths(tmp_path, True)
    f4 = json.load(open(paths["f4"]))
    del f4["codes"]["MNG"]
    open(paths["f4"], "w").write(json.dumps(f4))
    with pytest.raises(b.NeedsJudgment):
        b.build(paths)
    assert b.main([f"--{k.replace('_', '-')}={v}" for k, v in paths.items()]) == 2


def test_unlisted_sourced_touch_stops(tmp_path):
    paths = _paths(tmp_path, True)
    f4 = json.load(open(paths["f4"]))
    f4["codes"]["CL"]["touch"] = {"value": 9, "sourced": True, "item": "CRUDE-1"}
    open(paths["f4"], "w").write(json.dumps(f4))
    with pytest.raises(b.NeedsJudgment):
        b.build(paths)


def test_brief_spread_conflicting_with_f4_smean_stops(tmp_path):
    paths = _paths(tmp_path, True)
    s = _f4_smean()
    s["codes"]["MNG"]["spread_S_mean"]["value"] = 9.9
    open(paths["f4_smean"], "w").write(json.dumps(s))
    with pytest.raises(b.NeedsJudgment):
        b.build(paths)


def test_rater_sensitivity_counts_and_values(tmp_path):
    paths = _paths(tmp_path, True)
    doc, rep = b.build(paths)
    by = {r["name"]: r for r in doc["rulings"]}
    assert [n for n in by if n.startswith("RS-")] == [
        "RS-D6SPAN", "RS-D6THRESH", "RS-D6CRYPTO", "RS-D2BIIP", "RS-MNQD6", "RS-OWNONLY", "RS-EQS2", "RS-MFFUR", "RS-CRYPTOR", "RS-ATOP2", "RS-A3P",
        "RS-ATRAD1", "RS-RELTOP0", "RS-RELTRAD1"]
    c = rep["counts"]
    assert (c["RS-D6SPAN"], c["RS-D6THRESH"], c["RS-D6CRYPTO"], c["RS-D2BIIP"]) == (35, 7, 2, 13)
    assert (c["RS-MNQD6"], c["RS-OWNONLY"], c["RS-EQS2"]) == (1, 25, 6)
    assert (c["RS-MFFUR"], c["RS-CRYPTOR"]) == (4, 5)  # mffu listed pairs MCL, ZC, MBT, ES (GOLD unlisted); MBT at five firms
    assert (c["RS-ATOP2"], c["RS-A3P"], c["RS-ATRAD1"], c["RS-RELTOP0"], c["RS-RELTRAD1"]) == (5, 15, 5, 2, 2)
    mffu = {p["path"][1]: p["value"]["value"] for p in by["RS-MFFUR"]["patches"]}
    assert mffu["mffu|MCL"] == 1 and mffu["mffu|ZC"] == 1 and mffu["mffu|ES"] == 3 and mffu["mffu|MBT"] == 3
    assert all(p["value"]["unknown"] is False and p["value"]["reason"].startswith("rater alternative (flag")
               for r in doc["rulings"] if r["name"].startswith("RS-") for p in r["patches"])
    assert all(p["file"] == "blind" for r in doc["rulings"] if r["name"].startswith("RS-") for p in r["patches"])


def test_rater_patches_apply_and_leave_input_untouched(tmp_path):
    paths = _paths(tmp_path, True)
    doc, _ = b.build(paths)
    blind = json.load(open(paths["blind"]))
    by = {r["name"]: r for r in doc["rulings"]}
    out = apply_patches({"blind": blind}, by["RS-D6CRYPTO"]["patches"] + by["RS-RELTOP0"]["patches"])["blind"]
    assert [v["D6"]["value"] for k, v in out["codes"].items() if v["D6"]["value"] == 3]
    assert out["firms"]["topstep"]["rel_payout"]["value"] == 0 and out["firms"]["tradeify"]["rel_age"]["value"] == 1
    assert blind["codes"]["C0"]["D6"]["value"] == 3


def test_rater_stops_on_unexpected_current_value(tmp_path):
    paths = _paths(tmp_path, True)
    blind = json.load(open(paths["blind"]))
    blind["codes"]["C0"]["D6"]["value"] = 1  # K-YJXE should be 3
    open(paths["blind"], "w").write(json.dumps(blind))
    with pytest.raises(b.NeedsJudgment):
        b.build(paths)


def test_rater_stops_when_label_missing_from_flags_md(tmp_path):
    paths = _paths(tmp_path, True)
    md = open(paths["flags_md"]).read().replace("K-CSTX", "K-XXXX")
    open(paths["flags_md"], "w").write(md)
    with pytest.raises(b.NeedsJudgment):
        b.build(paths)


def test_ownonly_and_eqs2_values(tmp_path):
    paths = _paths(tmp_path, True)
    doc, _ = b.build(paths)
    by = {r["name"]: r for r in doc["rulings"]}
    own = {(p["path"][1], p["path"][2]): p["value"]["value"] for p in by["RS-OWNONLY"]["patches"]}
    assert sum(1 for (_, cell), v in own.items() if cell == "s1" and v == 1) == 8
    assert sum(1 for (_, cell), v in own.items() if cell == "s2" and v == 1) == 7
    assert sum(1 for (_, cell), v in own.items() if cell == "s3" and v == 0) == 10
    assert all(p["path"][2] == "s2" and p["value"]["value"] == 2 for p in by["RS-EQS2"]["patches"])
    assert by["RS-MNQD6"]["patches"][0]["value"]["value"] == 0


def test_eqs2_stops_when_flag_missing(tmp_path):
    paths = _paths(tmp_path, True)
    md = open(paths["flags_md"]).read().replace("s2 equity (K-KVJD", "s2 xx (K-KVJD")
    open(paths["flags_md"], "w").write(md)
    with pytest.raises(b.NeedsJudgment):
        b.build(paths)
