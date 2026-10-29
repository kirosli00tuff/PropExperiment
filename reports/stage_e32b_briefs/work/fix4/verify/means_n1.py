"""FixVerifier (F4): RV1 N1. Recompute the ranked-pair means printed in reports/stage_e32b_ranking.md section 4 from
score32b_out.json (103 ranked pairs), half-up at 2 decimals, and compare with the sentence."""
import json
import re
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

B = Path(__file__).resolve().parents[3]
out = json.loads((B / "score32b_out.json").read_text())
pairs = out["primary"]["pairs"] if "pairs" in out["primary"] else out["primary"]["ranked"]
ranked = [r for r in pairs if r.get("rank") is not None]
print("ranked pairs:", len(ranked))
print("row keys sample:", [k for k in ranked[0].keys()][:60])
txt = (B.parent / "stage_e32b_ranking.md").read_text().splitlines()
sent = next((i, l) for i, l in enumerate(txt, 1) if "ranked-pair means are" in l)
line = sent[1] + " " + txt[sent[0]]
print("line", sent[0], ":", line[:400])
printed = dict(re.findall(r"\b(D1|D2|D3|D4|D5|D6|E|R|A|D|Rel|P|S) (\d\.\d\d)", line))
print("printed:", printed)


def mean_of(key):
    vals = []
    for r in ranked:
        v = r.get(key)
        if v is None and "layer1" in r:
            v = r["layer1"].get(key)
        if v is None:
            return None
        vals.append(Decimal(str(v)))
    return sum(vals) / len(vals)


# D1..D6 may sit in the pair row or in the layer1 block
l1 = out["primary"].get("layer1") or {}
for key in ("D1", "D2", "D3", "D4", "D5", "D6", "E", "R", "A", "D", "Rel", "P", "S"):
    m = mean_of(key)
    if m is None and l1:
        vals = []
        for r in ranked:
            blk = l1.get(r["code"]) or {}
            v = blk.get(key)
            if v is None:
                break
            vals.append(Decimal(str(v)))
        if len(vals) == len(ranked):
            m = sum(vals) / len(vals)
    if m is None:
        print(f"{key}: not found")
        continue
    r2 = m.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    flag = "" if printed.get(key) == str(r2) else "  <-- DIFFERS"
    print(f"{key}: exact {m:.4f} -> {r2} ; printed {printed.get(key)}{flag}")
