import json, glob
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
TD = json.loads((HERE / "trade_dates_e33rule.json").read_text())
res = {}
for root in ("ZL", "ZS", "ZM"):
    fs = sorted(glob.glob(str(HERE / "bars" / f"{root}_*.json")))
    day = {}; recs = 0; outside = 0; rt = {}; dec = 0; dup = 0; metas = set(); first = None
    for f in fs:
        r = json.load(open(f)); recs += r["records"]; outside += r["outside_trade_dates"]; dec += r["ts_event_decreases"]; dup += r["duplicate_ts_event_iid"]
        for k, v in r["rtypes"].items(): rt[k] = rt.get(k, 0) + v
        metas.add((r["metadata"]["schema"], r["metadata"]["dataset"], r["metadata"]["stype_in"], r["metadata"]["stype_out"], tuple(r["metadata"]["symbols"]), r["metadata"]["version"]))
        for d, v in r["per_day"].items():
            e = day.setdefault(d, {"bars": 0, "ses": 0, "iid": {}}); e["bars"] += v["bars"]; e["ses"] += v["ses"]
            for a, c in v["iid"].items(): e["iid"][a] = e["iid"].get(a, 0) + c
    missing = [d for d in TD if d not in day]
    b = np.array([day[d]["bars"] for d in TD if d in day]); s = np.array([day[d]["ses"] for d in TD if d in day])
    dom = {d: max(day[d]["iid"], key=day[d]["iid"].get) for d in day}
    changes = [(TD[i], dom[TD[i-1]], dom[TD[i]]) for i in range(1, len(TD)) if TD[i] in dom and TD[i-1] in dom and dom[TD[i]] != dom[TD[i-1]]]
    multi = {d: day[d]["iid"] for d in TD if d in day and len(day[d]["iid"]) > 1}
    res[root] = {"files": len(fs), "records": recs, "outside_trade_dates": outside, "rtypes": rt, "ts_event_decreases": dec,
                 "dup_ts_event_iid": dup, "metadata_variants": [list(m) for m in metas], "n_dates": len(day), "missing_dates": missing,
                 "bars_per_date": {"median": float(np.median(b)), "min": int(b.min()), "max": int(b.max()), "p5": float(np.percentile(b,5)), "p95": float(np.percentile(b,95))},
                 "day_session_bars": {"median": float(np.median(s)), "min": int(s.min()), "max": int(s.max()), "p5": float(np.percentile(s,5))},
                 "min_dates": [d for d in TD if d in day and day[d]["bars"] == b.min()][:5],
                 "max_dates": [d for d in TD if d in day and day[d]["bars"] == b.max()][:3],
                 "dominant_changes": [{"date": d, "from": a, "to": c} for d, a, c in changes],
                 "multi_id_dates": multi, "n_distinct_ids": len({a for d in day.values() for a in d["iid"]})}
    # by year
    res[root]["by_year"] = {y: {"median": float(np.median([day[d]["bars"] for d in TD if d.startswith(y) and d in day])),
        "min": min(day[d]["bars"] for d in TD if d.startswith(y) and d in day), "max": max(day[d]["bars"] for d in TD if d.startswith(y) and d in day)} for y in ("2020","2021","2022","2023","2024")}
    res[root]["_day"] = day if root == "ZL" else None
# cross-root date presence & ZL ohlcv vs mbp1 dominant ids
agg = json.load(open(HERE / "agg_zl.json"))
zl_days = res["ZL"].pop("_day"); res["ZS"].pop("_day"); res["ZM"].pop("_day")
same = sum(1 for d in TD if d in zl_days and max(zl_days[d]["iid"], key=zl_days[d]["iid"].get) in agg["dates_with_multiple_ids"].get(d, {}) or False)
(HERE / "agg_bars.json").write_text(json.dumps(res, indent=1))
for r in res:
    x = res[r]; print(r, x["files"], x["records"], x["outside_trade_dates"], x["rtypes"], "dec", x["ts_event_decreases"], "dup", x["dup_ts_event_iid"], "n_dates", x["n_dates"], "missing", x["missing_dates"][:3], len(x["missing_dates"]))
    print("  bars", x["bars_per_date"], "ses", x["day_session_bars"], "chg", len(x["dominant_changes"]), "multi", len(x["multi_id_dates"]), "ids", x["n_distinct_ids"])
    print("  meta", x["metadata_variants"], "min_dates", x["min_dates"], "max", x["max_dates"])
