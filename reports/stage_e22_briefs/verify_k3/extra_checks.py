"""Extra checks for VerdictVerifier-K3: per-side ceil cost rule, flattened-date trips, coverage, timing."""
import json, math, collections
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
RUN = ROOT / "reports/stage_e22_confirm_k3"
CT = ZoneInfo("America/Chicago")
F14 = {"2022-01-17","2022-02-21","2022-05-30","2022-06-20","2022-07-04","2022-09-05","2022-11-24",
       "2023-01-16","2023-02-20","2023-05-29","2023-06-19","2023-07-04","2023-09-04","2023-11-23"}
costs = json.loads((ROOT/"reports/stage_e2a_costs.json").read_text())
clist = json.loads((ROOT/"reports/stage_e22_k3_confirmation_list.json").read_text())
marker = json.loads((ROOT/"reports/stage_e22_K3_RUN_ONCE.json").read_text())
out = {}
# 1. cost rule: commission + per-side ceil(slippage cents) for every trip of every run trial
def bucket(buckets, ts_ns):
    dt = datetime.fromtimestamp(ts_ns/1e9, tz=timezone.utc).astimezone(CT)
    minute = dt.hour*60+dt.minute
    f = [b for b in buckets if b["start_min"] <= minute < b["end_min"]]
    assert len(f) == 1
    return f[0]
cost_rule = {}
f14_rows = {}
cov = {}
times = {}
for t in clist["trials"]:
    name = f"K3_{t['member'].replace(' ','_')}_confirmation"
    rec = json.loads((RUN/f"{name}.json").read_text())
    times[t["member"]] = rec["created_utc"]
    if t["vehicle"] in ("6S","6N"):
        cov[t["member"]] = (rec["status"], rec["coverage"][t["vehicle"]])
    if rec.get("series") is None:
        continue
    trips = json.loads((RUN/f"{name}_trips.json").read_text())["trips"]
    p = costs["products"][t["vehicle"]]
    tv = float(p["tick_value_usd"]); comm = float(p["commission_rt_usd"])*100
    exact = 0; ceil_ok = 0; other = []
    for x in trips:
        q = x["contracts"]
        be, bx = bucket(p["buckets"], x["open_ts_ns"]), bucket(p["buckets"], x["close_ts_ns"])
        obs = x["gross_cents_float"] - x["net_cents_float"]
        matched = False
        for es, xs in (("buy","sell"),("sell","buy")):
            s_in, s_out = be["side_ticks"][es], bx["side_ticks"][xs]
            c_ceil = q*comm + math.ceil(round(q*s_in*tv*100, 6)) + math.ceil(round(q*s_out*tv*100, 6))
            c_exact = q*(comm + (s_in+s_out)*tv*100)
            if abs(c_ceil - obs) < 1e-6: matched = True
            if abs(c_exact - obs) < 1e-6: exact += 1
        if matched: ceil_ok += 1
        else: other.append((x["trade_date"], obs))
    cost_rule[t["member"]] = {"n": len(trips), "per_side_ceil_matches": ceil_ok, "exact_matches": exact, "unmatched": other[:3]}
    on = [x for x in trips if x["trade_date"] in F14]
    if on:
        ct_close = collections.Counter(datetime.fromtimestamp(x["close_ts_ns"]/1e9, tz=timezone.utc).astimezone(CT).strftime("%H:%M") for x in on if x["close_reason"]=="forced_flatten")
        f14_rows[t["member"]] = {"trips": len(on), "dates": len({x["trade_date"] for x in on}),
                                 "close_reasons": dict(collections.Counter(x["close_reason"] for x in on)),
                                 "forced_flatten_close_ct": dict(ct_close)}
out["cost_rule"] = cost_rule
out["cost_rule_all_per_side_ceil"] = all(v["per_side_ceil_matches"] == v["n"] for v in cost_rule.values())
out["f14"] = f14_rows
out["coverage_6S_6N"] = cov
first = min(times.values()); last = max(times.values())
out["timing"] = {"marker_created": marker["created_utc"], "first_record": first, "last_record": last,
                 "all_records_after_marker": all(v >= marker["created_utc"] for v in times.values())}
Path(ROOT/"reports/stage_e22_briefs/verify_k3/extra_checks.json").write_text(json.dumps(out, indent=1))
print("cost rule per-side ceil for every trip of every run trial:", out["cost_rule_all_per_side_ceil"],
      "trips total", sum(v["n"] for v in cost_rule.values()), "exact-match trips", sum(v["exact_matches"] for v in cost_rule.values()))
print("unmatched:", {k: v["unmatched"] for k, v in cost_rule.items() if v["unmatched"]})
print("F14:"); [print("  ", k, v) for k, v in f14_rows.items()]
print("coverage 6S/6N:"); [print("  ", k, v) for k, v in cov.items()]
print("timing:", out["timing"])
