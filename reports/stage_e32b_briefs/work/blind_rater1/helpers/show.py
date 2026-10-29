"""Print one section of the masked contract sheet compactly.

Usage: python3 -I show.py <contract label> <list name or prefix> [maxlen]
       python3 -I show.py <contract label> keys
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


def short(val, maxlen):
    text = val if isinstance(val, str) else json.dumps(val)
    return text if len(text) <= maxlen else text[:maxlen] + "..."


def main():
    label = sys.argv[1]
    section = sys.argv[2]
    maxlen = int(sys.argv[3]) if len(sys.argv) > 3 else 300
    contracts = json.load(open(SHEET))["contracts"]
    entry = contracts[label]
    if section == "keys":
        for key, val in entry.items():
            print(key, short(val, maxlen) if not isinstance(val, list) else len(val))
        return
    name = ALIASES.get(section.lower(), section)
    items = entry.get(name, [])
    print(f"== {label} {name} n={len(items)}")
    note = entry.get(name + "_note")
    if note:
        print("NOTE:", short(note, maxlen))
    for item in items:
        parts = []
        for key, val in item.items():
            if val is None or val == "" or val is False:
                continue
            parts.append(f"{key}={short(val, maxlen)}")
        print(" | ".join(parts))
        print("--")


if __name__ == "__main__":
    main()
