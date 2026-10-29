"""Print one evidence list for several contracts, selected fields only.

Usage: python3 -I sec.py <section alias> <fields comma list> <maxlen> [labels comma list|all] [applies filter substrings, comma]
"""
import json
import sys

SHEET = "/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/F4_masked_contracts.json"
ALIASES = {
    "d2a": "D2a_automated_share",
    "d2b": "D2b_programs",
    "s1": "D3_s1_relationships",
    "s2": "D3_s2_scheduled_releases",
    "s3": "D3_s3_session_structure",
    "sat": "Sat_iii_price_discovery",
    "d6": "D6_directional_evidence",
}
APPLIES_SHORT = {
    "this contract": "THIS",
    "a same-underlying sibling": "SIB",
    "the product group": "GROUP",
    "a close cousin (same asset class on CME Globex)": "COUSIN",
    "the asset class broadly or a multi-asset study": "CLASS",
    "another venue of the same underlying": "OTHERVENUE",
}
VERIFIED_SHORT = {
    "full text": "FT",
    "abstract [unverified]": "ABS",
    "snippet [unverified]": "SNIP",
}


def short(val, maxlen):
    text = val if isinstance(val, str) else json.dumps(val)
    return text if len(text) <= maxlen else text[:maxlen] + "..."


def fmt_item(item, fields, maxlen):
    applies = APPLIES_SHORT.get(item.get("applies_to"), item.get("applies_to"))
    ver = item.get("verified", "")
    ver = VERIFIED_SHORT.get(ver, "REUSED" if ver.startswith("reused") else ver)
    flags = [k for k in ("pointer_only", "negative_finding") if item.get(k)]
    head = f"{item.get('id')} [{applies}|{ver}{'|' + ','.join(flags) if flags else ''}]"
    parts = [head]
    for f in fields:
        val = item.get(f)
        if val is None or val == "":
            continue
        parts.append(f"{f}={short(val, maxlen)}")
    return " ".join(parts)


def main():
    name = ALIASES.get(sys.argv[1].lower(), sys.argv[1])
    fields = [f for f in sys.argv[2].split(",") if f]
    maxlen = int(sys.argv[3])
    labels = sys.argv[4] if len(sys.argv) > 4 else "all"
    applies_filter = sys.argv[5].split(",") if len(sys.argv) > 5 else None
    contracts = json.load(open(SHEET))["contracts"]
    keys = list(contracts) if labels == "all" else labels.split(",")
    for label in keys:
        entry = contracts[label]
        items = entry.get(name, [])
        print(f"== {label} n={len(items)}")
        note = entry.get(name + "_note")
        if note:
            print("  NOTE:", short(note, maxlen))
        for item in items:
            applies = APPLIES_SHORT.get(item.get("applies_to"), item.get("applies_to"))
            if applies_filter and applies not in applies_filter:
                continue
            print("  " + fmt_item(item, fields, maxlen))


if __name__ == "__main__":
    main()
