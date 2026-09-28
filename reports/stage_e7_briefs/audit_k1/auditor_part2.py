"""Stage E.7 Task 6 (MemberAuditor-K1-FableXHigh, Part 2): independent recomputation of the K1
research-window screen from the runner's recorded outputs and the frozen tables only.

Reads: reports/stage_e7_k1_screen/*.json, reports/stage_e_k1_member_freeze.json, reports/stage_e2a_costs.json,
reports/stage_e2b_release_calendar.json, strategy/members/k1/_calendar.py, _event_common.py, vxnband.py (tables),
reports/stage_e7_briefs/audit_k1/auditor_sha256_at_start.txt. No bar file, no engine, no member run.
Writes auditor_part2.json next to this script and prints a summary.
Run: PYTHONPATH=. PYTHONPYCACHEPREFIX=<fresh> uv run python reports/stage_e7_briefs/audit_k1/auditor_part2.py
"""

from __future__ import annotations

import hashlib
import json
import math
import statistics
from collections import Counter, defaultdict
from datetime import UTC, date, datetime
from fractions import Fraction
from pathlib import Path
from zoneinfo import ZoneInfo

from strategy.members.k1 import _event_common as common
from strategy.members.k1 import vxnband
from strategy.members.k1._calendar import EQUITY_FULL_SESSIONS, EQUITY_TRADE_DATES

REPO = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SCREEN = REPO / "reports/stage_e7_k1_screen"
CT = ZoneInfo("America/Chicago")
NS = 1_000_000_000
NS_MIN = 60 * NS
EVENT_NS = 30 * NS_MIN
RESEARCH_FIRST, RESEARCH_LAST = "2025-04-01", "2026-06-19"
FREEZE_SHA = "cf48f514dcf26490fa79a4322f764af991ee2555f2147354f12a31621fbe7ce2"
HARNESS_SHA = "9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87"
D9_LABELS = ("coverage_below_0.95", "mean_holding_below_10min", "entries_above_20_per_day",
             "hold_below_2min")
Q_C = {"MNQ": 1, "M2K": 3, "MYM": 3}
TICK_VALUE_CENTS = 50
N_BEFORE = 156


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def cents(v) -> Fraction:
    return Fraction(v) if isinstance(v, str) else Fraction(int(v))


def ct_of(ns: int) -> datetime:
    return datetime.fromtimestamp(ns / NS, tz=UTC).astimezone(CT)


def hhmm(ns: int) -> str:
    return f"{ct_of(ns):%H:%M}"


out: dict = {}
records = {}
trips = {}
for p in sorted(SCREEN.glob("K1_K1-*_research.json")):
    r = json.loads(p.read_text())
    records[r["member"]] = (p, r)
    t = json.loads((SCREEN / p.name.replace("_research.json", "_research_trips.json")).read_text())
    trips[r["member"]] = t
cluster = json.loads((SCREEN / "K1_research_cluster.json").read_text())

# ---------------------------------------------------------------- item 0: frozen files ----
freeze = json.loads((REPO / "reports/stage_e_k1_member_freeze.json").read_text())
start_hashes = dict(line.split()[::-1] for line in
                    (HERE / "auditor_sha256_at_start.txt").read_text().splitlines() if line.strip())
files0 = {}
for rel, info in freeze["files"].items():
    p = REPO / rel
    files0[rel] = {"repo_sha_equals_freeze": sha(p) == info["sha256"], "bytes_equal": p.stat().st_size == info["bytes"],
                   "equals_part1_hash": start_hashes.get(rel) == info["sha256"] if rel in start_hashes else "not in part 1 list"}
tests0 = {}
for p in sorted((REPO / "tests").glob("test_k1_members*.py")):
    rel = p.relative_to(REPO).as_posix()
    tests0[rel] = "unchanged" if start_hashes.get(rel) == sha(p) else "CHANGED since Part 1"
out["item0"] = {
    "freeze_file_sha256_equals_lead": sha(REPO / "reports/stage_e_k1_member_freeze.json") == FREEZE_SHA,
    "freeze_members": [(m["ordinal"], m["label"], m["module"], m["factory"], m["legs"]) for m in freeze["members"]],
    "files": files0, "tests": tests0,
    "records_cluster_freeze_sha": {m: r["cluster_freeze_sha256"] == FREEZE_SHA for m, (_, r) in records.items()},
    "records_harness_sha": {m: r["harness_sha256"] == HARNESS_SHA for m, (_, r) in records.items()},
    "record_sha256_in_trip_lists": {m: trips[m]["record_sha256"] == sha(p) for m, (p, _) in records.items()},
}

# ---------------------------------------------------------------- item 1: the screen ----
window = [d for d in EQUITY_TRADE_DATES if RESEARCH_FIRST <= d <= RESEARCH_LAST]
item1 = {}
for m, (p, r) in records.items():
    excl = set()
    for v in r["window_dates"]["excluded"].values():
        excl |= set(v)
    my_dates = [d for d in window if d not in excl]
    vals = [float(v) for v in r["series"]["values"]]
    n = len(vals)
    mean = statistics.fmean(vals)
    sd = statistics.pstdev(vals)
    t = mean / (sd / math.sqrt(n)) if sd > 0 else None
    passes = bool(mean > 0 and t is not None and t >= 1.0)
    s = r["screen"]
    rel = lambda a, b: abs(a - b) <= 1e-9 * max(1.0, abs(a), abs(b))  # noqa: E731
    tl = trips[m]["trips"]
    per_day = defaultdict(Fraction)
    for tr in tl:
        per_day[tr["trade_date"]] += cents(tr["net_cents"]) / (tr["contracts"] * TICK_VALUE_CENTS)
    rebuilt = [float(per_day.get(d, 0)) for d in my_dates]
    nz = sum(1 for v in vals if v != 0.0)
    item1[m] = {
        "dates_equal_window": r["series"]["dates"] == my_dates, "n": n, "n_window_mine": len(my_dates),
        "mean_ok": rel(mean, s["mean_ticks"]), "sd_ok": rel(sd, s["sd_pop_ticks"]),
        "t_ok": (t is None and s["t_daily"] is None) or (t is not None and s["t_daily"] is not None and rel(t, s["t_daily"])),
        "passes_ok": passes == s["passes"], "mine": (mean, sd, t, passes),
        "nonzero_days": nz, "trip_dates": len(per_day), "nonzero_le_trip_dates": nz <= len(per_day),
        "values_rebuilt_from_trips_max_abs_diff": max(abs(a - b) for a, b in zip(vals, rebuilt, strict=True)),
        "daily_net_usd_rebuilt_max_abs_diff": max(abs(float(sum(cents(tr["net_cents"]) for tr in tl if tr["trade_date"] == d) / 100) - u)
                                                  for d, u in zip(my_dates, r["daily_net_usd"], strict=True)),
        "n_trips_ok": s["n_trips"] == len(tl) == r["series"]["n_trips"] == trips[m]["n_trips"],
        "trips_outside_window": sorted({tr["trade_date"] for tr in tl} - set(my_dates)),
    }
out["item1"] = item1
out["window"] = {"trade_dates_in_research": len(window), "excluded": sorted(excl), "n_after": len(my_dates),
                 "first": my_dates[0], "last": my_dates[-1]}

# ---------------------------------------------------------------- item 2: tiers ----
item2 = {}
for tm in cluster["tiers"]["members"]:
    m = tm["member_id"]
    _, r = records[m]
    tr = r["trade_rate"]
    my_labels = []
    if any(not c["passes"] or c["ratio"] < 0.95 for c in r["coverage"].values()):
        my_labels.append("coverage_below_0.95")
    if tr["entry_cap_refusals"] or tr["max_entries_per_product_day"] > 20:
        my_labels.append("entries_above_20_per_day")
    if tr["min_hold_refusals"]:
        my_labels.append("hold_below_2min")
    if tr["mean_hold_minutes"] is not None and tr["mean_hold_minutes"] < 10:
        my_labels.append("mean_holding_below_10min")
    expected = "excluded" if any(lb in D9_LABELS for lb in tm["labels"]) else ("A" if tm["screen"]["passes"] else "B")
    item2[m] = {"tier": tm["tier"], "expected_from_labels_and_screen": expected, "tier_ok": tm["tier"] == expected,
                "labels_record": r["labels"], "labels_tier": tm["labels"], "labels_mine_from_trade_rate": my_labels,
                "labels_ok": tm["labels"] == r["labels"] == my_labels,
                "screen_equals_record": tm["screen"] == r["screen"], "note": tm["note"], "status": r["status"]}
out["item2"] = {"members": item2, "cluster_members": cluster["members"], "not_tiered": cluster["not_tiered"],
                "refused": cluster["refused_members"], "power_undefined": cluster["power_check_undefined"],
                "tier_A": [m for m, v in item2.items() if v["tier"] == "A"], "all_B": all(v["tier"] == "B" for v in item2.values())}

# ---------------------------------------------------------------- item 3: costs ----
costs = json.loads((REPO / "reports/stage_e2a_costs.json").read_text())["products"]["MNQ"]
assert costs["calibrated"] and not costs["fallback_buckets"] and float(costs["tick_value_usd"]) == 0.5
rt_cents = round(float(costs["commission_rt_usd"]) * 100)
assert rt_cents == 122 and rt_cents % 2 == 0
COMM_SIDE = rt_cents // 2
buckets = [(b["start_min"], b["end_min"], float(b["half_spread_ticks"]),
            {s: float(b["depth_ticks"][s]) for s in ("buy", "sell")},
            {s: float(b["side_ticks"][s]) for s in ("buy", "sell")}) for b in costs["buckets"] if not b["fallback"]]
MAX_HALF = max(b[2] for b in buckets)
rel_cal = json.loads((REPO / "reports/stage_e2b_release_calendar.json").read_text())
releases_mnq = sorted({int(datetime.fromisoformat(e["instant_utc"].replace("Z", "+00:00")).timestamp()) * NS
                       for e in rel_cal["releases"] if "MNQ" in e["products"]})


def in_event(ns: int) -> bool:
    import bisect
    i = bisect.bisect_right(releases_mnq, ns) - 1
    return i >= 0 and ns < releases_mnq[i] + EVENT_NS


def slip_cents(ns: int, side: str, qty: int, force_event: bool) -> int:
    minute = ct_of(ns).hour * 60 + ct_of(ns).minute
    found = [b for b in buckets if b[0] <= minute < b[1]]
    assert len(found) == 1, (hhmm(ns), len(found))
    _, _, half, depth, side_t = found[0]
    ticks = MAX_HALF + depth[side] if (force_event or in_event(ns)) else side_t[side]
    return math.ceil(round(qty * ticks * TICK_VALUE_CENTS, 6))


item3 = {}
for m in ("K1-cp2-01 MNQ", "K1-vwap-01 MNQ"):
    tl = trips[m]["trips"]
    matched = ambiguous = unmatched = 0
    event_fills = 0
    examples = []
    sides_seen = Counter()
    for tr in tl:
        q = tr["contracts"]
        gross, net = cents(tr["gross_cents"]), cents(tr["net_cents"])
        force_close = tr["close_reason"] == "price_limit_exit"
        cands = {}
        for entry_side, exit_side in (("buy", "sell"), ("sell", "buy")):
            c = gross - 2 * COMM_SIDE * q - slip_cents(tr["open_ts_ns"], entry_side, q, False) \
                - slip_cents(tr["close_ts_ns"], exit_side, q, force_close)
            cands[entry_side] = c
        hits = [s for s, c in cands.items() if c == net]
        if len(hits) == 1:
            matched += 1
            sides_seen[hits[0]] += 1
        elif len(hits) == 2:
            ambiguous += 1
        else:
            unmatched += 1
            if len(examples) < 5:
                examples.append((tr["trade_date"], hhmm(tr["open_ts_ns"]), hhmm(tr["close_ts_ns"]), tr["close_reason"],
                                 str(gross), str(net), {k: str(v) for k, v in cands.items()}))
        if in_event(tr["open_ts_ns"]) or in_event(tr["close_ts_ns"]) or force_close:
            event_fills += 1
    item3[m] = {"trips": len(tl), "net_matched_one_side": matched, "matched_both_sides": ambiguous, "unmatched": unmatched,
                "entry_sides_inferred": dict(sides_seen), "trips_with_an_event_window_or_forced_event_fill": event_fills,
                "unmatched_examples": examples, "close_reasons": dict(Counter(t["close_reason"] for t in tl)),
                "gross_checkable": False}
out["item3"] = {"members": item3, "commission_side_cents": COMM_SIDE, "max_half_spread_ticks": MAX_HALF,
                "n_buckets": len(buckets), "releases_mnq_in_window": sum(1 for r in releases_mnq if
                                                                       RESEARCH_FIRST <= ct_of(r).date().isoformat() <= RESEARCH_LAST)}

# ---------------------------------------------------------------- item 4: trade counts ----
full = set(EQUITY_FULL_SESSIONS)
item4 = {}
# vxnband
_, r = records["K1-vxnband-01 MNQ"]
tl = trips["K1-vxnband-01 MNQ"]["trips"]
w = r["series"]["dates"]
eligible = []
for d in w:
    if d not in full:
        continue
    v = vxnband.vxn_for(date.fromisoformat(d))
    if v is not None and vxnband.in_regime(v):
        eligible.append(d)
trip_dates = [t["trade_date"] for t in tl]
fills4 = []
for t in tl:
    o, c = ct_of(t["open_ts_ns"]), ct_of(t["close_ts_ns"])
    hold = (t["close_ts_ns"] - t["open_ts_ns"]) / NS_MIN
    deviation = None
    if hold != 30:
        if t["close_reason"] != "strategy":
            deviation = t["close_reason"]
        elif in_event_guard := any(rr <= t["open_ts_ns"] - 2 * NS_MIN < rr + 2 * NS_MIN or rr <= t["open_ts_ns"] - NS_MIN < rr + 2 * NS_MIN for rr in releases_mnq):
            deviation = "D9.5a entry deferral (fill 2 min after a release)" if in_event_guard else None
        else:
            deviation = "UNEXPLAINED"
    fills4.append((t["trade_date"], f"{o:%H:%M}", f"{c:%H:%M}", hold, t["close_reason"], deviation,
                   str(vxnband.vxn_for(date.fromisoformat(t["trade_date"])))))
item4["vxnband"] = {
    "window_dates": len(w), "full_session_window_dates": sum(1 for d in w if d in full),
    "eligible_dates_V_in_regime": len(eligible), "trips": len(tl),
    "trip_dates_outside_eligible": sorted(set(trip_dates) - set(eligible)),
    "eligible_dates_without_trip": len(set(eligible) - set(trip_dates)),
    "max_trips_per_date": max(Counter(trip_dates).values()),
    "entry_fill_minutes_in_0831_1429": all("08:31" <= f[1] <= "14:29" for f in fills4),
    "exit_fill_le_1459": all(f[2] <= "14:59" for f in fills4),
    "holds": Counter(f[3] for f in fills4), "deviations": [f for f in fills4 if f[5] is not None],
    "engine_counters": r["engine"]["counters"],
    "regimes_of_trips": Counter("V<20" if float(f[6]) < 20 else "V>=30" for f in fills4),
}
# vwap
_, r = records["K1-vwap-01 MNQ"]
tl = trips["K1-vwap-01 MNQ"]["trips"]
per_date = Counter(t["trade_date"] for t in tl)
holds = [(t["close_ts_ns"] - t["open_ts_ns"]) / NS_MIN for t in tl]
short = [(t["trade_date"], hhmm(t["open_ts_ns"]), hhmm(t["close_ts_ns"]), t["close_reason"]) for t in tl
         if (t["close_ts_ns"] - t["open_ts_ns"]) / NS_MIN < 2]
item4["vwap"] = {
    "trips": len(tl), "max_trips_per_date": max(per_date.values()), "dates_with_20": sum(1 for v in per_date.values() if v == 20),
    "dates_over_20": sum(1 for v in per_date.values() if v > 20),
    "trip_dates_not_full_session": sorted({t["trade_date"] for t in tl} - full),
    "trip_dates_outside_window": sorted({t["trade_date"] for t in tl} - set(r["series"]["dates"])),
    "holds_under_2min": short, "holds_under_2min_reasons": Counter(s[3] for s in short),
    "last_close_fill_max": max(hhmm(t["close_ts_ns"]) for t in tl),
    "first_open_fill_min": min(hhmm(t["open_ts_ns"]) for t in tl),
    "close_reasons": dict(Counter(t["close_reason"] for t in tl)),
    "strategy_closes_after_1459": [(t["trade_date"], hhmm(t["close_ts_ns"])) for t in tl if t["close_reason"] == "strategy" and hhmm(t["close_ts_ns"]) > "14:59"],
    "engine_counters": r["engine"]["counters"],
}
# ports
ports = {}
for m, (_, r) in records.items():
    if not m.startswith("K1-cp"):
        continue
    tl = trips[m]["trips"]
    per_date = Counter(t["trade_date"] for t in tl)
    opens = Counter(hhmm(t["open_ts_ns"]) for t in tl)
    closes = Counter((hhmm(t["close_ts_ns"]), t["close_reason"]) for t in tl)
    dev = []
    for t in tl:
        o, c, hold = hhmm(t["open_ts_ns"]), hhmm(t["close_ts_ns"]), (t["close_ts_ns"] - t["open_ts_ns"]) / NS_MIN
        ok = False
        if m.startswith("K1-cp1"):
            ok = o == "14:30" and c == "14:59" and t["close_reason"] == "strategy"
        elif m.startswith("K1-cp3"):
            ok = o == "08:31" and c == "14:59" and t["close_reason"] == "strategy"
        else:
            ok = ("08:46" <= o <= "15:00") and ((hold == 75 and t["close_reason"] == "strategy") or t["close_reason"] == "forced_flatten")
        if not ok:
            reason = t["close_reason"] if t["close_reason"] != "strategy" else "strategy: see minutes"
            dev.append((t["trade_date"], o, c, hold, reason))
    ports[m] = {"trips": len(tl), "max_per_date": max(per_date.values()), "opens": dict(opens) if len(opens) <= 6 else f"{len(opens)} distinct",
                "closes": {f"{k[0]} {k[1]}": n for k, n in closes.items()} if len(closes) <= 8 else f"{len(closes)} distinct",
                "deviations": dev,
                "n_deviations": len(dev), "counters": r["engine"]["counters"]}
item4["ports"] = ports
out["item4"] = item4

# ---------------------------------------------------------------- item 5: N ----
screened = [m for m, (_, r) in records.items() if r["status"] == "run" and r.get("screen")]
declared = [m["label"] for m in freeze["members"]]
out["item5"] = {"screened": len(screened), "refused": cluster["refused_members"], "not_tiered": cluster["not_tiered"],
                "records_not_declared": sorted(set(records) - set(declared)), "declared_without_record": sorted(set(declared) - set(records)),
                "N": N_BEFORE + len(screened)}

# ---------------------------------------------------------------- item 6: MLL ----
item6 = {}
for m, (_, r) in records.items():
    tl = trips[m]["trips"]
    mll_trips = [t for t in tl if t["close_reason"] == "mll_liquidation"]
    vals = [float(v) for v in r["series"]["values"]]
    dates = r["series"]["dates"]
    idx = {d: i for i, d in enumerate(dates)}
    q = Q_C[m.split()[-1]]
    adj = list(vals)
    for t in mll_trips:
        adj[idx[t["trade_date"]]] -= float(cents(t["net_cents"])) / (t["contracts"] * TICK_VALUE_CENTS)
    mean_adj = statistics.fmean(adj)
    sd_adj = statistics.pstdev(adj)
    t_adj = mean_adj / (sd_adj / math.sqrt(len(adj))) if sd_adj > 0 else None
    item6[m] = {"accounts_started_minus_1": r["engine"]["accounts_started"] - 1,
                "counter_mll": r["engine"]["counters"].get("mll_liquidation", 0),
                "mll_trips": len(mll_trips), "mll_net_usd_total": float(sum(cents(t["net_cents"]) for t in mll_trips) / 100),
                "account_not_active_refusals": r["engine"]["counters"].get("account_not_active", 0),
                "screen_with_mll_trips_zeroed": (mean_adj, t_adj, bool(mean_adj > 0 and t_adj is not None and t_adj >= 1.0))}
out["item6"] = item6

(HERE / "auditor_part2.json").write_text(json.dumps(out, indent=1, default=str))
# ---------------------------------------------------------------- print ----
print("ITEM0 freeze sha ok:", out["item0"]["freeze_file_sha256_equals_lead"], "| files:",
      all(v["repo_sha_equals_freeze"] and v["bytes_equal"] for v in files0.values()), "| part1 equal:",
      {k: v["equals_part1_hash"] for k, v in files0.items() if v["equals_part1_hash"] is not True})
print("  tests:", {k.split('/')[-1]: v for k, v in tests0.items()})
print("  records freeze/harness/record_sha ok:", all(out["item0"]["records_cluster_freeze_sha"].values()),
      all(out["item0"]["records_harness_sha"].values()), all(out["item0"]["record_sha256_in_trip_lists"].values()))
print("WINDOW:", out["window"]["trade_dates_in_research"], "-", len(out["window"]["excluded"]), "=", out["window"]["n_after"],
      out["window"]["first"], out["window"]["last"])
for m, v in item1.items():
    print(f"ITEM1 {m:20s} dates={v['dates_equal_window']} n={v['n']} mean={v['mean_ok']} sd={v['sd_ok']} t={v['t_ok']} pass={v['passes_ok']} "
          f"nz={v['nonzero_days']}<=tripdates={v['trip_dates']} rebuilt_diff={v['values_rebuilt_from_trips_max_abs_diff']:.2e} "
          f"usd_diff={v['daily_net_usd_rebuilt_max_abs_diff']:.2e} ntrips={v['n_trips_ok']} outside={v['trips_outside_window']}")
for m, v in item2.items():
    print(f"ITEM2 {m:20s} tier={v['tier']} ok={v['tier_ok']} labels_ok={v['labels_ok']} mine={v['labels_mine_from_trade_rate']} screen_eq={v['screen_equals_record']}")
print("ITEM2 tier A:", out["item2"]["tier_A"], "all B:", out["item2"]["all_B"], "not_tiered/refused:", cluster["not_tiered"], cluster["refused_members"])
print("ITEM3 comm/side", COMM_SIDE, "max_half", round(MAX_HALF, 4), "buckets", len(buckets), "MNQ releases in window", out["item3"]["releases_mnq_in_window"])
for m, v in item3.items():
    print(f"ITEM3 {m}: trips {v['trips']} matched {v['net_matched_one_side']} both {v['matched_both_sides']} unmatched {v['unmatched']} "
          f"sides {v['entry_sides_inferred']} event_or_forced {v['trips_with_an_event_window_or_forced_event_fill']} reasons {v['close_reasons']}")
    for e in v["unmatched_examples"]:
        print("   unmatched:", e)
v = item4["vxnband"]
print(f"ITEM4 vxnband: window {v['window_dates']} full {v['full_session_window_dates']} eligible {v['eligible_dates_V_in_regime']} trips {v['trips']} "
      f"outside_eligible {v['trip_dates_outside_eligible']} eligible_no_trip {v['eligible_dates_without_trip']} max/date {v['max_trips_per_date']} "
      f"entry_in_window {v['entry_fill_minutes_in_0831_1429']} exit<=14:59 {v['exit_fill_le_1459']} holds {dict(v['holds'])} regimes {dict(v['regimes_of_trips'])} counters {v['engine_counters']}")
for d in v["deviations"]:
    print("   deviation:", d)
v = item4["vwap"]
print(f"ITEM4 vwap: trips {v['trips']} max/date {v['max_trips_per_date']} dates_with_20 {v['dates_with_20']} over20 {v['dates_over_20']} "
      f"not_full {v['trip_dates_not_full_session']} outside {v['trip_dates_outside_window']} holds<2 {len(v['holds_under_2min'])} {dict(v['holds_under_2min_reasons'])} "
      f"first_open {v['first_open_fill_min']} last_close {v['last_close_fill_max']} strategy_after_1459 {v['strategy_closes_after_1459']} reasons {v['close_reasons']}")
for m, p in ports.items():
    print(f"ITEM4 {m:20s} trips {p['trips']} max/date {p['max_per_date']} opens {p['opens']} closes {p['closes']} deviations {p['n_deviations']}")
    for d in p["deviations"][:12]:
        print("   ", d)
print("ITEM5:", out["item5"])
for m, v in item6.items():
    print(f"ITEM6 {m:20s} acct-1={v['accounts_started_minus_1']} ctr={v['counter_mll']} mll_trips={v['mll_trips']} mll_usd={v['mll_net_usd_total']:.2f} "
          f"not_active={v['account_not_active_refusals']} zeroed=(mean {v['screen_with_mll_trips_zeroed'][0]:.4f}, t {v['screen_with_mll_trips_zeroed'][1]}, pass {v['screen_with_mll_trips_zeroed'][2]})")
