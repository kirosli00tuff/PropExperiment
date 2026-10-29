"""Build F4_blind_ratings_masked.json incrementally and validate cited ids.

Usage: python3 -I build.py <stage: codes|pairs|firms> "<generated_pdt>"
"""
import json
import os
import re
import sys

BASE = "/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs"
OUT = os.path.join(BASE, "F4_blind_ratings_masked.json")
sys.path.insert(0, os.path.join(BASE, "work", "blind"))

SCALES = {
    "D2a": {0, 1}, "D2b": {0, 0.5, 1}, "s1": {0, 1, 2}, "s2": {0, 1, 2},
    "s3": {0, 1}, "sat_iii": {0, 1}, "D6": {0, 1, 2, 3, 4},
    "R": {1, 2, 3, 4}, "A": {0, 1, 2, 3, 4},
    "rel_age": {0, 1}, "rel_payout": {0, 1}, "rel_rules": {0, 1}, "rel_regulatory": {0, 2},
}
ID_RE = re.compile(r"I-\d{7}")


def ids_by_contract():
    contracts = json.load(open(os.path.join(BASE, "F4_masked_contracts.json")))["contracts"]
    out = {}
    for label, entry in contracts.items():
        found = set()
        for val in entry.values():
            if isinstance(val, list):
                found.update(item["id"] for item in val)
        out[label] = found
    return out


def rating(value, unknown, reason, unverified=None):
    entry = {"value": value, "unknown": unknown, "reason": reason}
    if unverified is not None:
        entry["unverified"] = unverified
    return entry


def build_codes():
    from codes_data import D2A, D2B, S1, S2, S3
    from codes_data2 import SAT, D6
    tables = {"D2a": D2A, "D2b": D2B, "s1": S1, "s2": S2, "s3": S3, "sat_iii": SAT, "D6": D6}
    valid_ids = ids_by_contract()
    labels = list(valid_ids)
    errors = []
    codes = {}
    for label in labels:
        codes[label] = {}
        for crit, table in tables.items():
            if label not in table:
                errors.append(f"missing {crit} for {label}")
                continue
            tup = table[label]
            value, unknown, reason = tup[0], tup[1], tup[2]
            unverified = tup[3] if len(tup) > 3 else None
            if value not in SCALES[crit]:
                errors.append(f"{label} {crit} value {value} off scale")
            for cited in ID_RE.findall(reason):
                if cited not in valid_ids[label]:
                    errors.append(f"{label} {crit} cites {cited} not in its sheet")
            # D3 s1/s2 and D6 always carry an explicit unverified flag
            if crit in ("s1", "s2", "D6") and unverified is None:
                unverified = False
            codes[label][crit] = rating(value, unknown, reason, unverified)
    extra = [k for t in tables.values() for k in t if k not in valid_ids]
    errors.extend(f"rating for unknown label {k}" for k in extra)
    return codes, errors


def main():
    stage = sys.argv[1]
    stamp = sys.argv[2]
    doc = json.load(open(OUT)) if os.path.exists(OUT) else {}
    doc["rater"] = "BlindScorer-OpusXHigh"
    doc["generated_pdt"] = stamp
    if stage == "codes":
        codes, errors = build_codes()
        doc["codes"] = codes
    elif stage == "pairs":
        from pairs_data import build_pairs
        doc["pairs"], errors = build_pairs()
    elif stage == "firms":
        from firms_data import FIRMS
        doc["firms"], errors = {}, []
        for label, crits in FIRMS.items():
            doc["firms"][label] = {}
            for crit, tup in crits.items():
                if tup[0] not in SCALES[crit]:
                    errors.append(f"{label} {crit} off scale")
                doc["firms"][label][crit] = rating(tup[0], tup[1], tup[2])
    else:
        raise SystemExit("unknown stage")
    if errors:
        print("ERRORS:", len(errors))
        for err in errors[:40]:
            print(" ", err)
        raise SystemExit(1)
    ordered = {k: doc[k] for k in ("rater", "generated_pdt", "codes", "pairs", "firms") if k in doc}
    with open(OUT, "w") as fh:
        json.dump(ordered, fh, indent=1, ensure_ascii=False)
    print("wrote", stage, {k: len(v) for k, v in ordered.items() if isinstance(v, dict)})


if __name__ == "__main__":
    main()
