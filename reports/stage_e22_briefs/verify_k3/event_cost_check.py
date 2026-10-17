import json, math, collections
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT = Path("/home/kiros-li/Documents/GitHub/PropExperiment"); RUN = ROOT/"reports/stage_e22_confirm_k3"; CT = ZoneInfo("America/Chicago")
costs = json.loads((ROOT/"reports/stage_e2a_costs.json").read_text())
clist = json.loads((ROOT/"reports/stage_e22_k3_confirmation_list.json").read_text())
def bucket(buckets, ts_ns):
    dt = datetime.fromtimestamp(ts_ns/1e9, tz=timezone.utc).astimezone(CT); minute = dt.hour*60+dt.minute
    return [b for b in buckets if b["start_min"] <= minute < b["end_min"]][0]
res = {}
for t in clist["trials"]:
    name = f"K3_{t['member'].replace(' ','_')}_confirmation"
    rec = json.loads((RUN/f"{name}.json").read_text())
    if rec.get("series") is None: continue
    trips = json.loads((RUN/f"{name}_trips.json").read_text())["trips"]
    p = costs["products"][t["vehicle"]]; tv = float(p["tick_value_usd"]); comm = float(p["commission_rt_usd"])*100; ev = p["event_window_side_ticks"]
    cnt = collections.Counter()
    for x in trips:
        q = x["contracts"]; be, bx = bucket(p["buckets"], x["open_ts_ns"]), bucket(p["buckets"], x["close_ts_ns"])
        obs = x["gross_cents_float"] - x["net_cents_float"]; kind = None
        for es, xs in (("buy","sell"),("sell","buy")):
            for ein, eout in ((0,0),(1,0),(0,1),(1,1)):
                s_in = ev[es] if ein else be["side_ticks"][es]; s_out = ev[xs] if eout else bx["side_ticks"][xs]
                c = q*comm + math.ceil(round(q*s_in*tv*100, 6)) + math.ceil(round(q*s_out*tv*100, 6))
                if abs(c-obs) < 1e-6 and kind is None: kind = ("bucket" if not ein else "event") + "/" + ("bucket" if not eout else "event")
        cnt[kind or "UNMATCHED"] += 1
    res[t["member"]] = dict(cnt)
Path(ROOT/"reports/stage_e22_briefs/verify_k3/event_cost_check.json").write_text(json.dumps(res, indent=1))
tot = collections.Counter(); [tot.update(v) for v in res.values()]
print("all run trials, trips by cost kind:", dict(tot))
print("members with any non bucket/bucket:", {m: v for m, v in res.items() if set(v) - {"bucket/bucket"}})
