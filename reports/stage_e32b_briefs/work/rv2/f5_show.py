"""RV2 helper: print one F5 pair or own-broker row compactly."""
import json, sys
d = json.load(open("F5_holding.json"))
key = sys.argv[1]
r = d["pairs"].get(key) or d["own_broker"]["rows"].get(key)
if r is None: print("no row", key); sys.exit(1)
print("== ", key, "keys:", list(r.keys()))
for k, v in r.items():
    if k in ("rows", "by_h", "horizons"): continue
    s = json.dumps(v); print(" ", k, ":", s[:700])
for k in ("rows", "by_h", "horizons"):
    if k in r:
        v = r[k]
        print(" ", k, "type", type(v).__name__, "len", len(v))
        items = v.items() if isinstance(v, dict) else enumerate(v)
        for hk, hv in items:
            print("    ", hk, json.dumps(hv)[:600])
