"""Stage E.32b: write work/score/lead_variants.json (SCHEMA.md section 6) from the lead's four rulings.

Mechanical builder. Every value is decided by the lead (briefs/brief_wave_c.md, C4v); a case that would need a
judgment raises NeedsJudgment and the run stops with exit 2. Exit 3: the F4 patches are written but the econ files
do not exist yet (the RL-SMEAN econ patches are pending); the lead reruns the builder when both exist.

    uv run python reports/stage_e32b_briefs/work/score/build_lead_variants.py

Rulings: RL-SMEAN (LR-S, variant S_mean), RL-KZM (LR-D1, k_ZM), RL-PBRIEF (LR-D2, p_brief), RL-TRECENT (FT-2,
T_recent), then the rater sensitivities RS-* (the BlindScorer's own alternatives, patching the "blind" file).
Never edits an input file and never runs score32b.py.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BRIEFS = HERE.parents[0].parent  # reports/stage_e32b_briefs

DEFAULT_PATHS = {
    "f4": BRIEFS / "F4_facts_unmasked.json",
    "f4_smean": BRIEFS / "F4_smean.json",
    "f2_da": BRIEFS / "F2_data_access.json",
    "econ": BRIEFS / "econ32b.json",
    "econ_smean": BRIEFS / "econ32b_smean.json",
    "blind": BRIEFS / "F4_blind_unmasked.json",
    "mask_key": BRIEFS / "F4_mask_key.json",
    "flags_md": BRIEFS / "F4_blind_ratings_masked.md",
    "f4_smean_facts": BRIEFS / "work" / "econ_smean" / "F4_facts_smean.json",  # cross-check only (lead's file)
    "out": HERE / "lead_variants.json",
}

CLAUSE = "S_mean variant"
# Decided by the lead (brief C4v ruling 1): code -> (value, item). HG 1.55 is the whole-day all-hours average
# (METALS-50), confirmed by the lead's own work/econ_smean/F4_facts_smean.json.
SMEAN_SPREADS = {
    "HG": (1.55, "METALS-50"),
    "MNG": (2.414, "NATGAS-3"),
    "BTC": (4.72, "CRYPTO-2"),
    "10Y": (1.67, "RATES-5"),
}
SMEAN_ECON_PAIRS = ("lucid|HG", "tradeify|HG", "bulenox|HG", "topstep|MNG")

# RL-TRECENT: each sourced primary touch in F4 and the window it rests on, read from F4_facts_unmasked.json
# (touch.note), F4_facts.md rows 68-74 and F2_natgas.json / F2_metals.json (NATGAS-4..6: E.2a program measurement,
# 5 dates 2025-05..2026-04; METALS-3 and -4: Richards, Peters and Dunsmuir, 2010). pre2015 = window starts before
# 2015-01-01. A sourced touch missing from this table stops the run (the lead decides).
TOUCH_WINDOWS = {
    "MNG": ("NATGAS-6", "5 dates 2025-05..2026-04", False),
    "QG": ("NATGAS-5", "5 dates 2025-05..2026-04", False),
    "NG": ("NATGAS-4", "5 dates 2025-05..2026-04", False),
    "GC": ("METALS-3", "250 trading days of 2010", True),
    "SI": ("METALS-4", "2010", True),
}
TRECENT_CLAUSE = "T_recent: pre-2015 touch not counted"


class NeedsJudgment(Exception):
    """A case the brief does not decide: stop and report it to the lead."""


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def path_exists(doc, path) -> bool:
    node = doc
    for k in path:
        if isinstance(node, dict) and k in node:
            node = node[k]
        elif isinstance(node, list) and isinstance(k, int) and 0 <= k < len(node):
            node = node[k]
        else:
            return False
    return True


def patch(file, path, value, source):
    return {"file": file, "path": list(path), "value": value, "source": source}


def _num_eq(a, b) -> bool:
    if a is None or b is None:
        return a is b
    return abs(float(a) - float(b)) < 1e-12


# ------------------------------------------------------------------------------------------------ rulings
def smean_f4_patches(f4_smean: dict, cross: dict | None) -> tuple[list, list]:
    """(patches, soft notes). Spread patches follow the brief's table; touch patches follow F4_smean touch_mean."""
    src_sp = "briefs/F4_smean.json codes.{c}.spread_S_mean"
    out, notes = [], []
    for c, (val, item) in SMEAN_SPREADS.items():
        have = (((f4_smean.get("codes") or {}).get(c) or {}).get("spread_S_mean")) or {}
        if have and (not _num_eq(have.get("value"), val) or have.get("item") != item):
            raise NeedsJudgment(f"{c}: brief spread {val}/{item} != F4_smean {have.get('value')}/{have.get('item')}")
        if not have:
            notes.append(f"{c}: spread patch from the brief (value {val}, {item}); F4_smean spread_S_mean is null "
                         f"(primary S kept there)")
        out.append(patch("F4", ["codes", c, "spread_S"],
                         {"value": val, "sourced": True, "item": item, "clause": CLAUSE},
                         src_sp.format(c=c) if have else f"brief_wave_c.md C4v ruling 1 ({c} {val} {item})"))
    for c, rec in sorted((f4_smean.get("codes") or {}).items()):
        tm = rec.get("touch_mean")
        if not tm:
            continue
        out.append(patch("F4", ["codes", c, "touch"],
                         {"value": tm["value"], "sourced": True, "item": tm["item"], "clause": CLAUSE},
                         f"briefs/F4_smean.json codes.{c}.touch_mean"))
    if cross:
        for p in out:
            c, field = p["path"][1], p["path"][2]
            other = ((cross.get("codes") or {}).get(c) or {}).get(field) or {}
            if not _num_eq(other.get("value"), p["value"]["value"]):
                notes.append(f"{c}.{field}: patch {p['value']['value']} != work/econ_smean/F4_facts_smean.json "
                             f"{other.get('value')}")
    return out, notes


def smean_econ_patches(econ: dict, econ_smean: dict) -> list:
    pairs = (econ_smean or {}).get("pairs") or {}
    if set(pairs) != set(SMEAN_ECON_PAIRS):
        raise NeedsJudgment(f"econ32b_smean pairs {sorted(pairs)} != expected {sorted(SMEAN_ECON_PAIRS)}")
    out = []
    for pair in SMEAN_ECON_PAIRS:
        prim = (pairs[pair] or {}).get("primary")
        if not isinstance(prim, dict):
            raise NeedsJudgment(f"econ32b_smean {pair}: no primary block")
        out.append(patch("econ", ["pairs", pair, "primary"], prim,
                         f"briefs/econ32b_smean.json pairs.{pair}.primary"))
    return out


def kzm_patches(f2_da: dict, f4: dict) -> list:
    out = []
    for c, rec in sorted((f2_da.get("codes") or {}).items()):
        kz = rec.get("k_ZM")
        if not kz:
            continue
        prim, new = rec.get("k_usd_month"), kz.get("k_usd_month")
        if _num_eq(prim, new):
            continue
        if new is None:
            raise NeedsJudgment(f"{c}: k_ZM k_usd_month is null while the primary is {prim}")
        f4_k = (((f4["codes"].get(c) or {}).get("data_access")) or {}).get("k_usd_month")
        if not _num_eq(f4_k, prim):
            raise NeedsJudgment(f"{c}: F4 k_usd_month {f4_k} != F2_data_access primary {prim}")
        out.append(patch("F4", ["codes", c, "data_access", "k_usd_month"], new,
                         f"briefs/F2_data_access.json codes.{c}.k_ZM.k_usd_month (primary {prim}; LR-D1)"))
    return out


def pbrief_patches(f2_da: dict, f4: dict) -> list:
    out = []
    for c, rec in sorted((f2_da.get("codes") or {}).items()):
        pb = rec.get("p_brief")
        if not isinstance(pb, dict) or pb.get("value") not in (0, 1):
            continue
        new = pb["value"] == 1  # D5 p = 1 means every window read; F4 stores p_all_read as that boolean
        da = ((f4["codes"].get(c) or {}).get("data_access")) or {}
        if da.get("p_all_read") is new:
            continue
        if "p_all_read" not in da:
            raise NeedsJudgment(f"{c}: F4 data_access has no p_all_read")
        out.append(patch("F4", ["codes", c, "data_access", "p_all_read"], new,
                         f"briefs/F2_data_access.json codes.{c}.p_brief.value = {pb['value']} "
                         f"(primary p {rec.get('p')}; LR-D2)"))
    return out


def trecent_patches(f4: dict) -> list:
    out = []
    for c, rec in sorted(f4["codes"].items()):
        t = rec.get("touch") or {}
        if not (t.get("sourced") is True and t.get("value") is not None):
            continue
        if c not in TOUCH_WINDOWS:
            raise NeedsJudgment(f"{c}: sourced touch {t.get('item')} has no window in the builder's table")
        item, window, pre2015 = TOUCH_WINDOWS[c]
        if t.get("item") != item:
            raise NeedsJudgment(f"{c}: F4 touch item {t.get('item')} != table item {item}")
        if pre2015:
            out.append(patch("F4", ["codes", c, "touch"],
                             {"value": None, "sourced": False, "item": item, "clause": TRECENT_CLAUSE},
                             f"briefs/F4_facts_unmasked.json codes.{c}.touch ({item}, window {window})"))
    return out


# ------------------------------------------------------------------------------------------------ RS-* rater sensitivities
FLAGS_MD = "briefs/F4_blind_ratings_masked.md, Flags for the lead"
D6_SPAN_UP = ("K-YJXE K-LIRS K-DLUC K-LGJM K-NYZZ K-AAUT K-OEVC K-LTAT K-QIUI K-KVJD K-YEPF K-FICQ K-RISF K-QAJV "
              "K-DNXQ K-AIIW K-HIOT K-TATP K-UPOR K-EXGX K-DCJJ K-NUPE K-LWIK K-OQCY K-JCID K-AMNJ K-IXHJ K-ASNW "
              "K-BMTO K-KQRO K-WSRZ").split()
D6_SPAN_NULLS = "K-LRVK K-ASSS K-AJZH K-ODAS".split()
D2B_IIP = "K-PXYN K-DLUC K-NYZZ K-ASSS K-LTAT K-FICQ K-AIIW K-HIOT K-TATP K-UPOR K-AMNJ K-BMTO K-CSTX".split()
S1_OWN = "K-NYZZ K-OEVC K-RISF K-YEPF K-ASNW K-GOMC K-WSRZ K-BMTO".split()
S2_OWN = "K-NYZZ K-OEVC K-SLBV K-JCID K-ASNW K-AMNJ K-BMTO".split()
S3_OWN = "K-SGKW K-PXYN K-LIRS K-DLUC K-NYZZ K-OEVC K-JCID K-ASNW K-AMNJ K-BMTO".split()
EQ_S2 = "K-KVJD K-FICQ K-QAJV K-RISF K-YEPF K-DNXQ".split()
# (ruling, md marker that must be on the flag's line, groups, flag text); group = (md labels, new value,
# current values allowed, rating cell). Every label must appear on a marker line of the rater's flags file.
CODE_SENS = [
    ("RS-D6SPAN", "D6 spanning samples", [(D6_SPAN_UP, 4, {3}, "D6"), (D6_SPAN_NULLS, 0, {2}, "D6")],
     "D6 spanning samples: 31 contracts 3 -> 4, four own-contract nulls 2 -> 0"),
    ("RS-D6THRESH", "D6 in-sample threshold",
     [(["K-YBWI", "K-SLBV"], 3, {2}, "D6"), (["K-IXHJ", "K-ASNW", "K-BMTO", "K-KQRO", "K-WSRZ"], 2, {3}, "D6")],
     "D6 in-sample threshold"),
    ("RS-D6CRYPTO", "D6 K-OJGY, K-ZXJD", [(["K-OJGY", "K-ZXJD"], 3, {4}, "D6")], "D6 K-OJGY, K-ZXJD"),
    ("RS-D2BIIP", "D2b counted the International Incentive Program", [(D2B_IIP, 0.5, {0, 1}, "D2b")],
     "D2b International Incentive Program only basis"),
    ("RS-MNQD6", "D6 K-YEPF = 3", [(["K-YEPF"], 0, {3}, "D6")], "D6 K-YEPF at 3, own preprint finds no signal net of costs"),
    ("RS-OWNONLY", "Sibling-tagged items for s1/s2/s3",
     [(S1_OWN, 1, {2}, "s1"), (S2_OWN, 1, {2}, "s2"), (S3_OWN, 0, {1}, "s3")],
     "this-contract-only reading of sibling-tagged s1 (2 -> 1), s2 (2 -> 1) and s3 (1 -> 0) items"),
    ("RS-EQS2", "s2 equity (K-KVJD", [(EQ_S2, 2, {1}, "s2")], "s2 equity = 1, alt 2 if cousin evidence counts"),
]
CRUDE = ("MCL", "QM", "CL")
CRYPTO = ("MBT", "MET", "BTC", "ETH")
FIRM_A = [("RS-ATOP2", ["V-FRQI"], 2, "A V-FRQI = 3, alt 2"),
          ("RS-A3P", ["V-PCDG", "V-CXFO", "V-OJVP"], 3, "A V-PCDG and V-CXFO = 2, alt 3; A V-OJVP = 2, alt 3"),
          ("RS-ATRAD1", ["V-PCAN"], 1, "A V-PCAN = 2, alt 1")]
FIRM_REL = [("RS-RELTOP0", "V-FRQI", {"rel_payout": 0, "rel_rules": 0}, "V-FRQI rel_payout and rel_rules alt 0"),
            ("RS-RELTRAD1", "V-PCAN", {"rel_age": 1, "rel_rules": 1}, "V-PCAN rel_age and rel_rules alt 1")]


def rater_cell(value, flag, current=None):
    """The R shape; the unverified key is carried over when the rating being replaced has one."""
    out = {"value": value, "unknown": False, "reason": f"rater alternative (flag {flag})"}
    if isinstance(current, dict) and "unverified" in current:
        out["unverified"] = current["unverified"]
    return out


def _check_md(md_text: str, marker: str, labels: list) -> None:
    lines = [ln for ln in md_text.splitlines() if marker in ln]
    if not lines:
        raise NeedsJudgment(f"flag '{marker}' not found in the rater's flags file")
    missing = [lab for lab in labels if not any(lab in ln for ln in lines)]
    if missing:
        raise NeedsJudgment(f"flag '{marker}': labels {missing} not in the rater's flags file")


def _code_patches(blind: dict, key: dict, md_text: str) -> list:
    out = []
    for name, marker, groups, flag in CODE_SENS:
        patches = []
        _check_md(md_text, marker, [lab for labs, _, _, _ in groups for lab in labs])
        for labels, new, allowed, cell in groups:
            for lab in labels:
                code = key["contracts"][lab]
                cur = (blind["codes"].get(code) or {}).get(cell)
                if not isinstance(cur, dict) or cur.get("value") not in allowed:
                    raise NeedsJudgment(f"{name}: {lab}={code} {cell} is {cur and cur.get('value')}, "
                                        f"expected one of {sorted(allowed)}")
                patches.append(patch("blind", ["codes", code, cell], rater_cell(new, flag, cur),
                                     f"{FLAGS_MD}: {flag} ({lab}={code})"))
        out.append(ruling(name, "rater sensitivity", f"rater alternative: {flag}", patches))
    return out


def _listed(f4: dict, pair: str) -> bool:
    return (f4["pairs"].get(pair) or {}).get("listed_50k") is True


def _pair_cell_patch(blind, pair, cell, new, flag, expect=None):
    cur = (blind["pairs"].get(pair) or {}).get(cell)
    if not isinstance(cur, dict) or (expect is not None and cur.get("value") != expect):
        raise NeedsJudgment(f"{flag}: {pair} {cell} is {cur and cur.get('value')}, expected {expect}")
    return patch("blind", ["pairs", pair, cell], rater_cell(new, flag, cur), f"{FLAGS_MD}: {flag} ({pair})")


def _pair_patches(blind: dict, key: dict, f4: dict, md_text: str) -> list:
    firms = key["firms"]
    grains = {c for c, rec in f4["codes"].items() if rec.get("family") == "grains"}
    out = []
    _check_md(md_text, "V-CXFO listed pairs", ["V-CXFO", "Alt 3", "1 for K-SGKW"])
    mffu = firms["V-CXFO"]
    patches = []
    for pair in sorted(blind["pairs"]):
        firm, code = pair.split("|")
        if firm != mffu or not _listed(f4, pair):
            continue
        new = 1 if (code in CRUDE or code in grains) else 3
        patches.append(_pair_cell_patch(blind, pair, "R", new, "V-CXFO listed pairs R alt 3, crude and grains 1", 4))
    out.append(ruling("RS-MFFUR", "rater sensitivity", "rater alternative: V-CXFO listed pairs R = 3, crude and "
                      "grain pairs R = 1", patches))
    _check_md(md_text, "Listed crypto pairs", ["Alt 1"])
    patches = [_pair_cell_patch(blind, pair, "R", 1, "listed crypto pairs R alt 1", 4)
               for pair in sorted(blind["pairs"]) if pair.split("|")[1] in CRYPTO and _listed(f4, pair)]
    out.append(ruling("RS-CRYPTOR", "rater sensitivity", "rater alternative: R = 1 for every listed crypto pair",
                      patches))
    for name, labels, new, flag in FIRM_A:
        _check_md(md_text, flag.split(",")[0].split(" = ")[0], [])
        names = {firms[lab] for lab in labels}
        patches = [_pair_cell_patch(blind, pair, "A", new, flag) for pair in sorted(blind["pairs"])
                   if pair.split("|")[0] in names]
        out.append(ruling(name, "rater sensitivity", f"rater alternative: {flag}; A = {new} for every pair of "
                          f"{', '.join(labels)}", patches))
    for name, label, cells, flag in FIRM_REL:
        firm = firms[label]
        patches = []
        for cell, new in cells.items():
            cur = (blind["firms"].get(firm) or {}).get(cell)
            if not isinstance(cur, dict):
                raise NeedsJudgment(f"{name}: {firm} {cell} missing")
            patches.append(patch("blind", ["firms", firm, cell], rater_cell(new, flag, cur),
                                 f"{FLAGS_MD}: {flag} ({firm})"))
        out.append(ruling(name, "rater sensitivity", f"rater alternative: {flag}", patches))
    return out


def rater_sensitivities(blind: dict, key: dict, f4: dict, md_text: str) -> list:
    return _code_patches(blind, key, md_text) + _pair_patches(blind, key, f4, md_text)


# ------------------------------------------------------------------------------------------------ assembly
def ruling(name, ruling_id, description, patches):
    return {"name": name, "ruling": ruling_id, "description": description, "params": {}, "patches": patches}


def build(paths: dict) -> tuple[dict, dict]:
    """(variants doc, report). report: counts, codes, pending (list of rulings), notes."""
    f4, f2_da, f4_smean = load(paths["f4"]), load(paths["f2_da"]), load(paths["f4_smean"])
    cross = load(paths["f4_smean_facts"]) if Path(paths["f4_smean_facts"]).exists() else None
    notes = []
    if cross is None:
        notes.append("cross-check file work/econ_smean/F4_facts_smean.json absent: not compared")

    f4_part, n = smean_f4_patches(f4_smean, cross)
    notes += n
    econ_part, pending = [], []
    if Path(paths["econ"]).exists() and Path(paths["econ_smean"]).exists():
        econ_part = smean_econ_patches(load(paths["econ"]), load(paths["econ_smean"]))
    else:
        pending.append({"ruling": "RL-SMEAN", "what": "econ patches (" + ", ".join(SMEAN_ECON_PAIRS) + ")",
                        "missing": [k for k in ("econ", "econ_smean") if not Path(paths[k]).exists()]})
    rulings = [
        ruling("RL-SMEAN", "LR-S", "variant S_mean: sourced mean or average spread and touch where no qualifying "
               "median exists (F4 spread_S and touch; econ primary blocks of the pairs rerun with the S_mean "
               "spreads)", f4_part + econ_part),
        ruling("RL-KZM", "LR-D1", "variant k_ZM: D5 k from the ZM ratio r = 3.06 where it differs from the primary",
               kzm_patches(f2_da, f4)),
        ruling("RL-PBRIEF", "LR-D2", "variant p_brief: D5 p counts the holdout-2 seal as unread, as the brief "
               "reads it", pbrief_patches(f2_da, f4)),
        ruling("RL-TRECENT", "FT-2", "variant T_recent: a touch figure whose window starts before 2015-01-01 is "
               "not counted", trecent_patches(f4)),
    ]
    blind = load(paths["blind"])
    rulings += rater_sensitivities(blind, load(paths["mask_key"]), f4,
                                   Path(paths["flags_md"]).read_text(encoding="utf-8"))
    docs = {"F4": f4, "blind": blind, "econ": load(paths["econ"]) if Path(paths["econ"]).exists() else {}}
    for rv in rulings:  # every patch path must exist in its target file
        for p in rv["patches"]:
            target = docs.get(p["file"])
            if target is None or not path_exists(target, p["path"]):
                raise NeedsJudgment(f"{rv['name']}: patch path {p['path']} not found in {p['file']}")
    report = {"counts": {rv["name"]: len(rv["patches"]) for rv in rulings},
              "codes": {rv["name"]: sorted({p["path"][1] for p in rv["patches"]}) for rv in rulings},
              "pending": pending, "notes": notes}
    return {"rulings": rulings}, report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    for k, v in DEFAULT_PATHS.items():
        ap.add_argument(f"--{k.replace('_', '-')}", default=str(v))
    args = ap.parse_args(argv)
    paths = {k: getattr(args, k) for k in DEFAULT_PATHS}
    try:
        doc, rep = build(paths)
    except NeedsJudgment as exc:
        print(f"STOP, needs the lead: {exc}", file=sys.stderr)
        return 2
    out = Path(paths["out"])
    out.write_text(json.dumps(copy.deepcopy(doc), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    for name, n in rep["counts"].items():
        codes = rep["codes"][name]
        shown = ", ".join(codes) if len(codes) <= 12 else f"{len(codes)} codes/keys"
        print(f"{name}: {n} patches; codes: {shown or '-'}")
    for note in rep["notes"]:
        print("note:", note)
    for pend in rep["pending"]:
        print("PENDING:", pend)
    print(f"wrote {out}")
    return 3 if rep["pending"] else 0


if __name__ == "__main__":
    sys.exit(main())
