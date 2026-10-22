"""Compact print of masked contract sheets: one line per evidence record. Usage: A3_blind_compact.py C01 C02 ..."""
import json, sys
BASE = "/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/"
d = json.load(open(BASE + "A3_masked_contracts.json"))["contracts"]
for lab in sys.argv[1:]:
    print(f"######## {lab}")
    for sec in ("C1a_evidence", "C1b_evidence", "C6_evidence"):
        print(f"== {sec}")
        for i, r in enumerate(d[lab][sec]):
            parts = []
            for k, v in r.items():
                parts.append(f"{k}={json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v}")
            print(f" [{i}] " + " | ".join(parts))
