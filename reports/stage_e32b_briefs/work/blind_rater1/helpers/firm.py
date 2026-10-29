"""Print one section of one firm in the masked firm sheet, compactly.

Usage: python3 -I firm.py <firm label> <section|keys> [maxlen]
       python3 -I firm.py pair <firm|contract> [maxlen]
       python3 -I firm.py pairkeys
"""
import json
import sys

SHEET = "/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/F4_masked_firms.json"


def short(val, maxlen):
    text = val if isinstance(val, str) else json.dumps(val, ensure_ascii=False)
    return text if len(text) <= maxlen else text[:maxlen] + "..."


def show_items(items, maxlen):
    if not isinstance(items, list):
        print(short(items, maxlen))
        return
    for item in items:
        if isinstance(item, dict):
            print(" | ".join(f"{k}={short(v, maxlen)}" for k, v in item.items() if v not in (None, "", False)))
        else:
            print(short(item, maxlen))
        print("--")


def main():
    doc = json.load(open(SHEET))
    maxlen = int(sys.argv[3]) if len(sys.argv) > 3 else 300
    if sys.argv[1] == "pairkeys":
        sample = next(iter(doc["pairs"].values()))
        print(list(sample.keys()))
        return
    if sys.argv[1] == "pair":
        entry = doc["pairs"][sys.argv[2]]
        for key, val in entry.items():
            print(f"[{key}]")
            show_items(val, maxlen)
        return
    firm = doc["firms"][sys.argv[1]]
    section = sys.argv[2]
    if section == "keys":
        for key, val in firm.items():
            print(key, "=", short(val, maxlen) if not isinstance(val, list) else f"list[{len(val)}]")
        return
    show_items(firm[section], maxlen)


if __name__ == "__main__":
    main()
