"""FixVerifier (F4) item 3: R2_combinations.json against work/R2/R2_combinations_q3bleg.json: Q3 = 1 with Q3_rater kept
for C112-C116 and C138-C139, no other difference apart from lead_patch_v2; and the same against the v1 file."""
import json
from pathlib import Path

B = Path(__file__).resolve().parents[3]
prim = json.loads((B / "R2_combinations.json").read_text())
leg = json.loads((B / "work/R2/R2_combinations_q3bleg.json").read_text())


def flat(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from flat(v, f"{p}/{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from flat(v, f"{p}/{i}")
    else:
        yield p, o


ids = [c["id"] for c in prim["combinations"]]
assert ids == [c["id"] for c in leg["combinations"]], "different combination order"
a, b = dict(flat(prim)), dict(flat(leg))
diff = sorted(set(k for k in set(a) | set(b) if a.get(k, "<absent>") != b.get(k, "<absent>")))
by_combo = {}
for k in diff:
    parts = k.split("/")
    if parts[1] == "combinations":
        cid = ids[int(parts[2])]
        by_combo.setdefault(cid, []).append("/".join(parts[3:]))
    else:
        by_combo.setdefault("<top>", []).append(k)
for cid, ks in sorted(by_combo.items()):
    print(cid, ks)
print("combos differing:", sorted(c for c in by_combo if c != "<top>"))
for c in prim["combinations"]:
    if c["id"] in ("C112", "C113", "C114", "C115", "C116", "C138", "C139"):
        print(c["id"], c.get("product"), c["venue"], c["family"][:28], "Q3", c["Q3"]["value"], "| Q3_rater",
              (c.get("Q3_rater") or {}).get("value"), "| reason:", c["Q3"]["reason"][:60])
print("lead_patch_v2 primary:", prim.get("lead_patch_v2"))
print("lead_patch_v2 q3bleg :", leg.get("lead_patch_v2"))
# every F09 combination on RTY/ZL carries Q3 1 in the primary?
f09 = [(c["id"], c.get("product"), c["venue"], c["Q3"]["value"]) for c in prim["combinations"]
       if c["family"].startswith("F09") and {m["code"] for m in c["members"]} & {"RTY", "ZL"}]
print("F09 RTY/ZL combos in primary:", f09)
