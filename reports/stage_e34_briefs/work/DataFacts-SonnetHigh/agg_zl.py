"""Aggregate counts/zl_*.json into agg_zl.json (summary stats only; counts, no prices)."""
import json, glob
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
TD = json.loads((HERE / "trade_dates_e33rule.json").read_text())
files = sorted(glob.glob(str(HERE / "counts" / "zl_*.json")))
day = {}      # D -> {action:[rest,ses]}
iid = {}
tot = {}; flags = {}; side = {}; act = {}; outside = 0; recs = 0; secs = 0
for f in files:
    r = json.load(open(f)); recs += r["records"]; secs += r["seconds"]
    for d, v in r["per_day_action_by_seg"].items():
        assert d not in day or True
        for a, (x, y) in v.items():
            e = day.setdefault(d, {}).setdefault(a, [0, 0]); e[0] += x; e[1] += y
    for d, v in r["per_day_instrument"].items():
        for k, c in v.items():
            iid.setdefault(d, {}); iid[d][k] = iid[d].get(k, 0) + c
    for src, dst in ((r["tot"], tot), (r["flags"], flags), (r["side"], side), (r["action_total"], act)):
        for k, c in src.items(): dst[k] = dst.get(k, 0) + c
missing = [d for d in TD if d not in day]
stored = sum(sum(sum(v) for v in day[d].values()) for d in TD if d in day)
def row(d, key):
    a = day.get(d, {})
    if key == "all": return sum(sum(v) for v in a.values())
    if key == "T": return sum(a.get("T", [0, 0]))
    if key == "A": return sum(a.get("A", [0, 0]))
    if key == "C": return sum(a.get("C", [0, 0]))
    if key == "M": return sum(a.get("M", [0, 0]))
    if key == "other": return sum(sum(v) for k, v in a.items() if k not in "TACM")
    if key == "ses": return sum(v[1] for v in a.values())
    if key == "rest": return sum(v[0] for v in a.values())
def stats(dates, key):
    x = np.array([row(d, key) for d in dates], dtype=float)
    if len(x) == 0: return None
    return {"n_dates": len(x), "median": float(np.median(x)), "p5": float(np.percentile(x, 5)),
            "p95": float(np.percentile(x, 95)), "min": float(x.min()), "max": float(x.max()), "sum": float(x.sum())}
groups = {"all_816": TD, "2020-12": [d for d in TD if d.startswith("2020")]}
for y in ("2021", "2022", "2023", "2024"):
    groups[y] = [d for d in TD if d.startswith(y)]
groups["OOF_796"] = TD[20:]
keys = ["all", "T", "A", "C", "M", "other", "ses", "rest"]
out = {"files": len(files), "records_read": recs, "stored_in_816_dates": stored, "missing_dates": missing,
       "tot": tot, "flags": flags, "side": side, "action_total": act, "decode_seconds_sum": round(secs, 1),
       "stats": {g: {k: stats(ds, k) for k in keys} for g, ds in groups.items()}}
# action share in day session vs rest, T share
sess = {a: [sum(day[d].get(a, [0, 0])[0] for d in TD if d in day), sum(day[d].get(a, [0, 0])[1] for d in TD if d in day)] for a in "ACMTRFN"}
out["action_by_segment_total"] = sess
# instrument ids
dates_iid = {d: iid.get(d, {}) for d in TD}
dom = {d: max(v, key=v.get) if v else None for d, v in dates_iid.items()}
changes = [(TD[i], dom[TD[i - 1]], dom[TD[i]]) for i in range(1, len(TD)) if dom[TD[i]] != dom[TD[i - 1]]]
multi = {d: v for d, v in dates_iid.items() if len(v) > 1}
out["dominant_id_changes"] = [{"date": d, "from": a, "to": b} for d, a, b in changes]
out["dates_with_multiple_ids"] = {d: v for d, v in multi.items()}
out["distinct_instrument_ids"] = sorted({k for v in dates_iid.values() for k in v})
(HERE / "agg_zl.json").write_text(json.dumps(out, indent=1))
print("files", len(files), "read", recs, "stored", stored, "missing", len(missing), "outside", tot.get("outside_trade_dates"))
print("changes", len(changes), "multi-id dates", len(multi), "distinct ids", len(out["distinct_instrument_ids"]))
for g in groups: print(g, {k: (out["stats"][g]["all"][k]) for k in ("n_dates","median","p5","p95","min","max")})
print(tot); print(flags); print(side); print(act)
