"""FactAuditor (E.32b C1v): completeness and relation checks of the masked contract sheet.

For a sample of codes: every F2 item (all F2 files) of topics T2a, T2b, T3, T4, T5 (info_share), T6, T7 that lists
the code must appear under the code's label in the right section, via the key. Also: verified-level mapping for every
masked item, window carried, listed_on_modelled_plan vs F4, and a stratified sample of applies_to relations.
Read-only; writes nothing.
"""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

B = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
BR = B / "reports/stage_e32b_briefs"
SECTIONS = {"T2a": "D2a_automated_share", "T2b": "D2b_programs", "T3": "D3_s1_relationships",
            "T4": "D3_s2_scheduled_releases", "T7": "D3_s3_session_structure", "T5": "Sat_iii_price_discovery",
            "T6": "D6_directional_evidence"}
SAMPLE = ["NQ", "ZM", "ZL", "QM", "MGC", "10Y", "MCL", "MNG", "HG", "6E", "MBT", "M2K", "ZN", "ETH", "RTY", "XC"]
VER_MAP = {"full_text": "full text", "abstract": "abstract [unverified]", "snippet": "snippet [unverified]",
           "reused": "reused"}


def load_items() -> dict:
    items = {}
    for f in sorted(glob.glob(str(BR / "F2_*.json"))):
        d = json.loads(Path(f).read_text())
        for it in d.get("items", []):
            items[it["id"]] = it
    return items


def main() -> int:
    items = load_items()
    key = json.loads((BR / "F4_mask_key.json").read_text())
    mc = json.loads((BR / "F4_masked_contracts.json").read_text())["contracts"]
    mf = json.loads((BR / "F4_masked_firms.json").read_text())
    f4 = json.loads((BR / "F4_facts_unmasked.json").read_text())
    lab_of = {v: k for k, v in key["contracts"].items()}
    # masked id -> (source, for)
    k_items = key["items"]
    # index masked sheet: code -> section -> {masked id: rec}
    sheet = {}
    for lab, c in mc.items():
        code = key["contracts"][lab]
        sheet[code] = {sec: {r["id"]: r for r in c.get(sec, [])} for sec in SECTIONS.values()}
    print("== completeness sample")
    tot_exp = tot_ok = 0
    for code in SAMPLE:
        exp = [it for it in items.values() if code in (it.get("codes") or []) and it.get("topic") in SECTIONS
               and not (it.get("topic") == "T5" and it.get("field") != "info_share")]
        ok = 0; missing = []
        for it in exp:
            sec = SECTIONS[it["topic"]]
            found = [mid for mid, rec in sheet[code][sec].items()
                     if k_items.get(mid, {}).get("source_item") == it["id"] and k_items[mid].get("for") == code]
            if found:
                ok += 1
            else:
                # maybe placed in another section
                other = [s for s in SECTIONS.values() for mid in sheet[code][s]
                         if k_items.get(mid, {}).get("source_item") == it["id"] and k_items[mid].get("for") == code]
                missing.append((it["id"], it["topic"], it.get("field"), "in " + ",".join(other) if other else "absent"))
        tot_exp += len(exp); tot_ok += ok
        print(f"  {code:4} ({lab_of[code]}): expected {len(exp)}, present {ok}" + (f", missing {missing}" if missing else ""))
    print(f"  total expected {tot_exp}, present {tot_ok}")
    # T5 settlement_basis items must NOT be in the sheet (settlement method excluded)
    leak_t5 = 0
    for code, secs in sheet.items():
        for sec, recs in secs.items():
            for mid in recs:
                src = items.get(k_items.get(mid, {}).get("source_item"))
                if src and src.get("topic") == "T5" and src.get("field") != "info_share":
                    leak_t5 += 1
    print("  T5 settlement_basis items present in any sheet (should be 0):", leak_t5)
    # verified mapping and window carried, all items
    print("== verified level and window, all masked contract items")
    n = bad_v = bad_w = 0
    for code, secs in sheet.items():
        for sec, recs in secs.items():
            for mid, rec in recs.items():
                src = items.get(k_items.get(mid, {}).get("source_item"))
                if not src:
                    print("  masked item without source:", code, mid); continue
                n += 1
                v = str(rec.get("verified", ""))
                want = VER_MAP.get(src.get("verified"), src.get("verified"))
                if want not in v:
                    bad_v += 1
                    if bad_v <= 8:
                        print(f"  verified mismatch {code} {mid} <- {src['id']}: F2 {src.get('verified')!r} masked {v!r}")
                if bool(src.get("window")) != bool(rec.get("window")):
                    bad_w += 1
    print(f"  items {n}, verified mismatches {bad_v}, window presence mismatches {bad_w}")
    # pairs listed flag
    print("== pairs: listed_on_modelled_plan vs F4 listed_50k")
    bad = 0
    for plab, p in mf["pairs"].items():
        pair = key["pairs"][plab]
        if p.get("listed_on_modelled_plan") != f4["pairs"][pair]["listed_50k"]:
            bad += 1; print("  mismatch", pair, p.get("listed_on_modelled_plan"), f4["pairs"][pair]["listed_50k"])
    print(f"  pairs {len(mf['pairs'])}, mismatches {bad}")
    # relations sample
    print("== applies_to sample (stratified: per family, several scopes)")
    fam = {c: v["family"] for c, v in f4["codes"].items()}
    seen = set(); rows = []
    for code, rels in key["relations"].items():
        for r in rels:
            k = (fam[code], r["scope"], r["applies_to"])
            if k in seen:
                continue
            seen.add(k)
            src = items[r["source"]]
            rows.append((code, r["source"], src.get("topic"), r["scope"], r["applies_to"], src.get("codes"),
                         str(src.get("value"))[:70].replace("\n", " "), str(src.get("detail"))[:110].replace("\n", " ")))
    print(f"  distinct (family, scope, applies_to) combinations: {len(rows)}")
    for row in rows:
        print("  ", row)
    return 0


if __name__ == "__main__":
    sys.exit(main())
