"""RV2 helper: print selected combination records from a combinations file, compactly."""
import json, sys
p = sys.argv[1]; ids = sys.argv[2].split(",")
d = json.load(open(p))
top = {k: v for k, v in d.items() if k != "combinations"}
print("top-level keys:", list(d.keys()))
for k in ("sr80_test", "own_account_capital_ceiling_usd", "rho_measured", "lead_patch", "lead_patch_v2", "spec_sha256", "generated_pdt"):
    if k in top: print(k, "=", json.dumps(top[k])[:600])
by = {c["id"]: c for c in d["combinations"]}
for i in ids:
    c = by[i]
    print("\n=== ", i, {k: v for k, v in c.items() if k not in ("members", "data", "Q1", "Q2", "Q3", "Q3_rater", "dossier", "notes", "sources")})
    for k in ("Q1", "Q2", "Q3", "Q3_rater"):
        if k in c: print("  ", k, json.dumps(c[k])[:300])
    print("   data:", json.dumps(c.get("data"))[:900])
    for m in c["members"]:
        print("   member:", json.dumps(m)[:1500])
    for k in c:
        if k not in ("members","data","Q1","Q2","Q3","Q3_rater","id","product","pool","venue","family","band","h_c"):
            print("   other key:", k, json.dumps(c[k])[:400])
