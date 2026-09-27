"""Auditor Task 6 items 1, 2, 5: recompute the D5 screen, check series shape, tiers and N. Counts only."""
import sys, json, glob, math, statistics; sys.path.insert(0, ".")
from datetime import date, timedelta
from data.group_session import load_group_calendar
from rules.products import product
cal = load_group_calendar("rates")
files = sorted(glob.glob("reports/stage_e3_k2_screen/K2_*_research.json"))
cluster = json.load(open("reports/stage_e3_k2_screen/K2_research_cluster.json"))
freeze = json.load(open("reports/stage_e_k2_member_freeze.json"))
tiers = {m["member_id"]: m for m in cluster["tiers"]["members"]}
TOL = 1e-9
verdicts = {}; notes = {}; rows = []
for f in files:
    r = json.load(open(f)); m = r["member"]; s = r["screen"]; ser = r["series"]
    vals = ser["values"]; dates = ser["dates"]; n = len(vals)
    problems = []; nn = []
    # window dates recomputed: calendar trade dates in [first, 2026-06-19] minus the record's exclusions
    a, b = date(2025, 4, 1), date(2026, 6, 19)
    excl = {x for v in r["window_dates"]["excluded"].values() for x in v}
    mine = [d.isoformat() for d in (a + timedelta(i) for i in range((b - a).days + 1)) if cal.is_trade_date(d) and d.isoformat() not in excl]
    if mine != dates: problems.append("dates differ from the calendar window")
    if len(dates) != len(set(dates)) or dates != sorted(dates): problems.append("dates not ascending/unique")
    nz = sum(1 for v in vals if v != 0.0)
    if nz > ser["n_trips"] or ser["n_trips"] != s["n_trips"] or ser["n_trips"] != r["trade_rate"]["n_trips"]: problems.append(f"nz {nz} > n_trips {ser['n_trips']}")
    mean = statistics.fmean(vals); sd = statistics.pstdev(vals)
    t = mean / (sd / math.sqrt(n)) if sd > 0 else None
    passes = bool(mean > 0 and t is not None and t >= 1.0)
    def rel(x, y): return abs(x - y) <= TOL * max(1.0, abs(x), abs(y))
    if not rel(mean, s["mean_ticks"]): problems.append(f"mean {mean} vs {s['mean_ticks']}")
    if not rel(sd, s["sd_pop_ticks"]): problems.append(f"sd {sd} vs {s['sd_pop_ticks']}")
    if (t is None) != (s["t_daily"] is None) or (t is not None and not rel(t, s["t_daily"])): problems.append(f"t {t} vs {s['t_daily']}")
    if passes != s["passes"]: problems.append("passes differs")
    if s["n_days"] != n or n != r["window_dates"]["n"]: problems.append("n_days")
    # daily_net_usd consistency: values * tick_value (q = contracts = 1 assumed; checked via trip max)
    tv = float(product(r["primary_vehicle"]).tick_value_usd)
    usd = r["daily_net_usd"]
    if len(usd) != n or any(not rel(v * tv, u) for v, u in zip(vals, usd)): nn.append("daily_net_usd != values x tick value (multi-contract trips?)")
    if not all(math.isfinite(v) for v in vals): problems.append("non-finite")
    # tiers (item 2): labels -> excluded; else passes -> A / B; coverage label -> excluded before screening
    labels = r["labels"]; cov = r["coverage"][r["primary_vehicle"]]
    exp_tier = "excluded" if labels else ("A" if passes else "B")
    if cov["ratio"] < 0.95 and "coverage_below_0.95" not in labels: problems.append("coverage < 0.95 without label")
    if r["status"] != "run": problems.append(f"status {r['status']}")
    trec = tiers.get(m)
    if trec is None or trec["tier"] != exp_tier or list(trec["labels"]) != labels: problems.append(f"tier {trec and trec['tier']} vs expected {exp_tier}")
    # floor labels recomputed from trade_rate
    tr = r["trade_rate"]; exp_labels = []
    if tr["entry_cap_refusals"] or tr["max_entries_per_product_day"] > 20: exp_labels.append("entries_above_20_per_day")
    if tr["min_hold_refusals"]: exp_labels.append("hold_below_2min")
    if tr["mean_hold_minutes"] is not None and tr["mean_hold_minutes"] < 10: exp_labels.append("mean_holding_below_10min")
    if exp_labels != labels: problems.append(f"labels {labels} vs recomputed {exp_labels}")
    if r["power"]["status"] != "run": nn.append(f"power {r['power']['status']}")
    if r["engine"]["counters"].get("mll_liquidation"): nn.append(f"mll_liquidation x{r['engine']['counters']['mll_liquidation']}, accounts_started {r['engine']['accounts_started']}")
    verdicts[m] = "DISCREPANCY" if problems else ("VERIFIED WITH NOTES" if nn else "VERIFIED"); notes[m] = problems + nn
    rows.append((r["ordinal"], m, n, ser["n_trips"], nz, round(mean, 6), None if t is None else round(t, 6), passes, exp_tier, verdicts[m], "; ".join(problems + nn)))
from collections import Counter
print("verdict counts", Counter(verdicts.values()))
for row in sorted(rows): print(row)
# item 5
labels_freeze = [m["label"] for m in sorted(freeze["members"], key=lambda x: x["ordinal"])]
recs = [json.load(open(f))["member"] for f in files]
print("freeze labels == record members (as sets)", set(labels_freeze) == set(recs), len(labels_freeze), len(recs))
print("cluster members list == freeze ordinal order", cluster["members"] == labels_freeze)
print("refused", cluster["refused_members"], "not_tiered", cluster["not_tiered"], "power undefined", cluster["power_check_undefined"])
screened = sum(1 for f in files if json.load(open(f))["status"] == "run")
print("screened", screened, "N = 58 +", screened, "=", 58 + screened)
print("tiers A/B/excluded", Counter(m["tier"] for m in cluster["tiers"]["members"]))
print("harness sha in cluster", cluster["harness_sha256"])
json.dump({"verdicts": verdicts, "notes": notes}, open("reports/stage_e3_briefs/audit/item1_verdicts.json", "w"), indent=1)
