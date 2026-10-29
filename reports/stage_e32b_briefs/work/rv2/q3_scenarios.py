"""RV2: R4 under alternative Q3 readings for the F09 candidates (in memory; no file changed)."""
import json, math, sys
from fractions import Fraction as F
src = json.load(open("R2_combinations.json"))
W = {"Q1": F("0.20"), "Q2": F("0.10"), "Q3": F("0.10"), "Q4": F("0.15"), "Q5": F("0.15"), "Q6": F("0.15"), "Q7": F("0.15")}
out = {r["id"]: r for r in json.load(open("r3_out.json"))["combinations"]}
def run(label, q3_override):
    rows = []
    for c in src["combinations"]:
        o = out[c["id"]]
        if o["status"] != "eligible": continue
        q = {k: F(str(o[k])) for k in W}
        key = (c["product"] or c["pool"]["name"], c["family"][:3])
        if key in q3_override: q["Q3"] = F(q3_override[key])
        C = sum(W[k] * q[k] for k in W); Cr = F(math.floor(C * 100 + F(1, 2)), 100)
        rows.append((-Cr, -q["Q1"], o["G_hc"], o["name"], o["venue"], c["family"], c["id"], c["venue"] == "ibkr"))
    rows.sort()
    picks, seen = [], set()
    for r in rows:
        k = (r[3], r[5])
        if k in seen: continue
        seen.add(k); picks.append((r[6], r[3], r[5][:3], r[4], float(-r[0])))
        if len(picks) == 5: break
    own = next(r for r in rows if r[7])
    print(label, "R4:", picks, "| best own:", own[6], float(-own[0]))
run("primary        ", {})
run("RTY F09 Q3=1   ", {("RTY", "F09"): 1})
run("RTY+ZL F09 Q3=1", {("RTY", "F09"): 1, ("ZL", "F09"): 1})
