"""Print masked sheets compactly. Usage: A3_blind_show.py contracts C01 C02 ... | firms F01 [section]"""
import json, sys
BASE = "/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/"
kind = sys.argv[1]
fn = BASE + ("A3_masked_contracts.json" if kind == "contracts" else "A3_masked_firms.json")
d = json.load(open(fn))[kind]

def emit(v, ind=0):
    p = "  " * ind
    if isinstance(v, dict):
        for k, x in v.items():
            if isinstance(x, (dict, list)):
                print(f"{p}{k}:")
                emit(x, ind + 1)
            else:
                print(f"{p}{k}: {x}")
    elif isinstance(v, list):
        for i, x in enumerate(v):
            if isinstance(x, (dict, list)):
                print(f"{p}- [{i}]")
                emit(x, ind + 1)
            else:
                print(f"{p}- {x}")
    else:
        print(f"{p}{v}")

args = sys.argv[2:]
if kind == "firms" and len(args) == 2 and args[1] not in d:
    emit(d[args[0]][args[1]])
else:
    for lab in args:
        print(f"######## {lab}")
        emit(d[lab])
