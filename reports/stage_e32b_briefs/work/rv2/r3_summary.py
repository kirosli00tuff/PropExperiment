"""RV2 helper: print R4 lists and top rows of an r3_out file without loading its rows into context."""
import json, sys
from fractions import Fraction as F
p = sys.argv[1]
d = json.load(open(p))
print("==", p, "| generated", d.get("generated_pdt"), "| combos", d["inputs"].get("combos", {}).get("path"))
print("sr80_test", d["sr80_test"], "ceiling", d["capital_ceiling_usd"], "u", d["capital_ceiling_u"])
for key in ("R4", "R4_prop_only"):
    r4 = d[key]
    print(key, "n_reaching_2", r4["n_reaching_2"], "fewer_than_3", r4["fewer_than_3_reach_2"])
    for c in r4["candidates"]:
        print("  ", c["rank"], c["id"], c["product_or_pool"], c["family"][:28], c["best_venue"], c["band"], "h_c", c["h_c"], "C", c["C"], "Cr", c["C_rounded"], "weak", c["weak"])
bo = d["best_own_broker"]
print("best_own_broker", bo and (bo["id"], bo["name"], bo["family"][:28], bo["venue"], bo["band"], bo["h_c"], bo["C"], bo["C_rounded"]))
rows = d["combinations"]
elig = [r for r in rows if r["status"] == "eligible"]
excl = [r for r in rows if r["status"] != "eligible"]
print("rows", len(rows), "eligible", len(elig), "excluded", len(excl))
n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
print("rank id name venue family | Q1..Q7 | C Cr | x q K_used G")
for r in elig[:n]:
    print(r["rank"], r["id"], r["name"], r["venue"], r["family"][:22], "|", *[r[k] for k in ("Q1","Q2","Q3","Q4","Q5","Q6","Q7")], "|", r["C"], r["C_rounded"], "| x", round(float(F(r["x"])),4) if r["x"] is not None else None, "q", round(r["q"],4), "K", round(float(F(r["K_used"])),1), "G", round(r["G_hc"],4))
print("ties:", [(t["C_rounded"], t["ids"], [s["decided_by"] for s in t["steps"]]) for t in d["ties"][:8]])
print("excluded ids:", [(r["id"], r["name"], r["venue"], r["family"][:12], r["gate_reasons"][:1]) for r in excl])
print("for_lead n", len(d["for_lead"]), "distinct notes:", sorted({x["note"][:70] for x in d["for_lead"]})[:12])
