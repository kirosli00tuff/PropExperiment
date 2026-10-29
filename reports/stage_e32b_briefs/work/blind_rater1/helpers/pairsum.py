"""Summarise pair R_facts per firm: unique rules with the contracts they apply to.

Usage: python3 -I pairsum.py <firm label> [maxlen]
"""
import json
import sys
from collections import defaultdict

SHEET = "/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/F4_masked_firms.json"


def main():
    firm = sys.argv[1]
    maxlen = int(sys.argv[2]) if len(sys.argv) > 2 else 260
    pairs = json.load(open(SHEET))["pairs"]
    rules = defaultdict(list)
    unlisted = []
    item_keys = set()
    for key, entry in pairs.items():
        f_label, c_label = key.split("|")
        if f_label != firm:
            continue
        if not entry.get("listed_on_modelled_plan"):
            unlisted.append(f"{c_label}={entry.get('listed_on_modelled_plan')}")
        for item in entry.get("R_facts", []):
            item_keys.update(item.keys())
            rule = item.get("rule")
            text = rule if isinstance(rule, str) else json.dumps(rule, ensure_ascii=False)
            extra = {k: v for k, v in item.items() if k not in ("id", "what", "rule", "binds")}
            sig = f"{item.get('what')} :: {text[:maxlen]}" + (f" :: {json.dumps(extra, ensure_ascii=False)[:maxlen]}" if extra else "")
            rules[sig].append(c_label)
    print("item keys:", sorted(item_keys))
    print("NOT LISTED:", unlisted)
    for sig, labels in rules.items():
        print(f"[{len(labels)}] {sig}\n     -> {','.join(labels)}")


if __name__ == "__main__":
    main()
