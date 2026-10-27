"""E.17 H1/H4 result files: per_product entries for ZS, ZL, ZM, scalar fields only; lists/dicts shown
as type and length; traded_units_per_key_and_year shown as year -> count (yearly counts, not a series of prices)."""
import json
for h in ("H1", "H4"):
    d = json.load(open(f"reports/stage_e17_runs/{h}_result.json"))
    pp = d["per_product"]
    print(h, "per_product keys", sorted(pp))
    for r in ("ZS", "ZL", "ZM"):
        v = pp.get(r)
        if isinstance(v, dict):
            print(" ", r, {k: (x if not isinstance(x, (list, dict)) else f"<{type(x).__name__} {len(x)}>") for k, x in v.items()})
        else:
            print(" ", r, str(v)[:200])
        t = d["traded_units_per_key_and_year"].get(r)
        print("   units/yr", r, (t if not isinstance(t, dict) or len(str(t)) < 400 else str(t)[:400]))
    print("  exclusions keys", sorted(d["exclusions"])[:30])
    for r in ("ZS", "ZL", "ZM"):
        if r in d["exclusions"]:
            print("   excl", r, str(d["exclusions"][r])[:300])
    print("  notes", {k: str(v)[:250] for k, v in d["notes"].items()})
    print("  stats", {k: (v if not isinstance(v,(list,dict)) else f"<{type(v).__name__} {len(v)}>") for k, v in d["stats"].items()})
