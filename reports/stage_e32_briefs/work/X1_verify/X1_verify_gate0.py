"""Print Gate 0 summary fields and the soy/K6 test rows only (no series)."""
import json, collections
d = json.load(open("reports/stage_e12_gate0.json"))
print("top keys", sorted(d.keys()))
for k in ("verdict", "n_a", "n_b", "n_holm_family", "n_pass", "passing_pairs"):
    if k in d: print(k, str(d[k])[:120])
T = d["tests"]; print("tests", len(T))
fam = collections.Counter(t.get("family") for t in T); print("families", fam)
print("test fields", sorted(T[0].keys()))
B = [t for t in T if t.get("family") == "B"]
nd = [t.get("n_dates") for t in B]; print("family B n_dates min/max", min(nd), max(nd))
soyB = [t for t in B if any(r in t["test_id"] for r in ("_ZS_", "_ZL_", "_ZM_"))]
soyBnd = [t["n_dates"] for t in soyB]; print("soy B n_dates min/max", min(soyBnd), max(soyBnd))
cols = ["test_id","horizon","n_obs","n_dates","n_trades","mean_gross_ticks","cost_ticks","gross_cost_multiple","t_B","p","holm_rank","holm_threshold","decision"]
for t in sorted(soyB, key=lambda x: x["test_id"]):
    print("B|" + "|".join(str(t.get(c)) for c in cols))
A = [t for t in T if t.get("family") == "A"]
colsA = ["test_id","horizon","n_obs","n_dates","mean","t","p","holm_rank","holm_threshold","ic_spearman","decision"]
for t in A:
    if "k6_" in t["test_id"]:
        print("A|" + "|".join(str(t.get(c)) for c in colsA))
print("A n_dates set", sorted(set(t.get("n_dates") for t in A)))
print("A non-k6 count", sum(1 for t in A if "k6_" not in t["test_id"]))
sig = sorted(set(t["test_id"].replace("gate0A_","").rsplit("_h",1)[0] for t in A)); print("A signals", len(sig), sig)
