"""MemberAuditor-K3 Task 6: recompute the K3 research screen from the runner's recorded outputs
and the frozen tables, in the auditor's own code. No bar file is opened, nothing is replayed.
Run: PYTHONPATH=. uv run python reports/stage_e4_briefs/audit_k3/recompute_screen.py
"""

from __future__ import annotations

import glob
import hashlib
import json
import math
import statistics
from collections import Counter, defaultdict
from datetime import UTC, date, datetime, timedelta
from fractions import Fraction
from pathlib import Path
from zoneinfo import ZoneInfo

from data.group_session import load_group_calendar, trade_dates_between
from strategy.members.k3 import _calendar as C
from strategy.members.k3 import _clocks as K
from strategy.members.k3 import _mehedge_signal as M

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "reports" / "stage_e4c_k3_screen"
CT = ZoneInfo("America/Chicago")
NS_MIN = 60 * 10**9
EVENT_WINDOW_NS = 30 * NS_MIN
FILL_GUARD_NS = 2 * NS_MIN
FREEZE_SHA = "c4fb5da41d69a6be54ea07d1ab35bd2b238d1fbeafaeb3008b886f8fc6888d95"
HARNESS_SHA = "82ae8536738ca43395f43356840c0b799a7925b7b75ddb4fc1353d3ab7491009"
RELEASE_SHA = "839f2437bedbeb7b3423d7058a9955a0d4ccd1aebc4b01c62be624ab11d7bcb8"
RESEARCH = (date(2025, 4, 1), date(2026, 6, 19))
verdicts: dict[str, list[str]] = defaultdict(list)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def cents(v) -> Fraction:
    return Fraction(v) if isinstance(v, str) else Fraction(int(v))


records = {}
trips = {}
for p in sorted(OUT.glob("K3_*_research.json")):
    r = json.loads(p.read_text())
    records[r["member"]] = (p, r)
    t = json.loads((OUT / (p.stem + "_trips.json")).read_text())
    trips[r["member"]] = t
cluster = json.loads((OUT / "K3_research_cluster.json").read_text())
freeze = json.loads((REPO / "reports" / "stage_e_k3_member_freeze.json").read_text())
print(f"records {len(records)}, trip lists {len(trips)}, cluster members {len(cluster['members'])}, "
      f"freeze members {len(freeze['members'])}")

# ------------------------------------------------------------------ item 0: hashes
print("== item 0")
same_hash = all(r["cluster_freeze_sha256"] == FREEZE_SHA and r["harness_sha256"] == HARNESS_SHA
                and r["release_calendar_sha256"] == RELEASE_SHA for _, r in records.values())
print(f"  every record: freeze {FREEZE_SHA[:8]}, harness {HARNESS_SHA[:8]}, release calendar "
      f"{RELEASE_SHA[:8]}: {same_hash}; freeze file sha256 == {FREEZE_SHA[:8]}: "
      f"{sha(REPO / 'reports' / 'stage_e_k3_member_freeze.json') == FREEZE_SHA}")
ft = {tuple(sorted(r["frozen_tables"].items())) for _, r in records.values()}
print(f"  frozen table hashes identical across records: {len(ft) == 1}: {dict(list(ft)[0])}")
labels_freeze = [m["label"] for m in freeze["members"]]
print(f"  record labels == freeze labels (order by ordinal): "
      f"{sorted(records) == sorted(labels_freeze)}; cluster.members == freeze order: "
      f"{cluster['members'] == labels_freeze}")
audited = dict(l.split("  ") for l in (REPO / "reports/stage_e4_briefs/k3_files_pre_audit.sha256").read_text().split("\n") if l)
audited = {v: k for k, v in audited.items()}  # path -> sha
nf = 0
for rel, entry in freeze["files"].items():
    s_frozen = entry["sha256"] if isinstance(entry, dict) else entry
    now = sha(REPO / rel) if (REPO / rel).exists() else None
    same_now = now == s_frozen
    same_audit = audited.get(rel) == s_frozen if rel in audited else (rel.endswith("__init__.py"))
    if not (same_now and same_audit):
        nf += 1
        print(f"  FREEZE FILE: {rel}: now equal {same_now}, audited equal {same_audit}")
print(f"  freeze files: {len(freeze['files'])}; every one equals the current file and the audited hash: {nf == 0}")
bars = {}
for _, r in records.values():
    for root, b in r["bars"].items():
        bars.setdefault(root, set()).add((b["path"], b["sha256"], b["rows"]))
print(f"  one bar file per root across records: {all(len(v) == 1 for v in bars.values())}; roots "
      f"{sorted(bars)}")

# ------------------------------------------------------------------ item 1: screen
print("== item 1")
cal = load_group_calendar("fx")
research_td = trade_dates_between(cal, *RESEARCH)
bad1 = []
for label, (p, r) in records.items():
    if r["status"] != "run":
        continue
    s, sc, wd = r["series"], r["screen"], r["window_dates"]
    vals, dates = s["values"], [date.fromisoformat(d) for d in s["dates"]]
    excluded = {date.fromisoformat(d) for lst in wd["excluded"].values() for d in lst}
    expected_dates = [d for d in research_td if d not in excluded
                      and date.fromisoformat(wd["first"]) <= d <= date.fromisoformat(wd["last"])]
    n = len(vals)
    mean = statistics.fmean(vals)
    sd = statistics.pstdev(vals)
    t = mean / (sd / math.sqrt(n)) if sd > 0 else None
    passes = bool(mean > 0 and t is not None and t >= 1.0)
    trip_dates = {tr["trade_date"] for tr in trips[label]["trips"]}
    nonzero = {d for d, v in zip(s["dates"], vals) if v != 0.0}
    ok = (dates == expected_dates and n == wd["n"] == sc["n_days"] == len(r["daily_net_usd"])
          and math.isclose(mean, sc["mean_ticks"], rel_tol=1e-9, abs_tol=1e-12)
          and math.isclose(sd, sc["sd_pop_ticks"], rel_tol=1e-9, abs_tol=1e-12)
          and (t is None and sc["t_daily"] is None
               or math.isclose(t, sc["t_daily"], rel_tol=1e-9, abs_tol=1e-12))
          and passes == sc["passes"] and s["n_trips"] == sc["n_trips"] == len(trips[label]["trips"])
          and nonzero <= trip_dates and len(nonzero) <= s["n_trips"])
    if not ok:
        bad1.append(label)
        print(f"  MISMATCH {label}: n {n}/{wd['n']} dates_ok {dates == expected_dates} mean {mean} "
              f"vs {sc['mean_ticks']} sd {sd} vs {sc['sd_pop_ticks']} t {t} vs {sc['t_daily']}")
    verdicts["item1"].append(f"{label}: n {n}, mean {mean:+.6f}, t {t:+.4f}, passes {passes}")
print(f"  run records {sum(1 for _, r in records.values() if r['status'] == 'run')}; mismatches: "
      f"{bad1 or 'none'}")
print(f"  window: {len(research_td)} research trade dates; the run records' window_dates.n values: "
      f"{sorted({r['window_dates']['n'] for _, r in records.values() if r['status'] == 'run'})}")
excl_sets = {tuple(sorted((k, tuple(v)) for k, v in r["window_dates"]["excluded"].items()))
             for _, r in records.values()}
print(f"  distinct window-exclusion sets across the 30 records: {len(excl_sets)}")
for es in excl_sets:
    print("   ", {k: (len(v), v[:3]) for k, v in es})

# ------------------------------------------------------------------ item 2: tiers
print("== item 2")
tier_rows = {m["member_id"]: m for m in cluster["tiers"]["members"]}
bad2 = []
counts = Counter()
for label, (p, r) in records.items():
    labs = r["labels"]
    if "coverage_below_0.95" in labs:
        want = "excluded"
        assert r["screen"] is None and r["series"] is None and r["status"] == "excluded_before_screening"
        assert trips[label]["n_trips"] == 0 and trips[label]["trips"] == []
        cov = list(r["coverage"].values())[0]
        assert cov["ratio"] < 0.95 and not cov["passes"]
        assert math.isclose(cov["ratio"], cov["present"] / cov["expected"], rel_tol=1e-12)
    elif labs:
        want = "excluded"
    else:
        want = "A" if r["screen"]["passes"] else "B"
    got = tier_rows[label]["tier"]
    counts[got] += 1
    if got != want or tier_rows[label]["labels"] != labs:
        bad2.append((label, want, got))
    if want != "excluded":
        cov = list(r["coverage"].values())[0]
        assert cov["ratio"] >= 0.95 and cov["passes"]
        assert math.isclose(cov["ratio"], cov["present"] / cov["expected"], rel_tol=1e-12)
print(f"  tiers: {dict(counts)}; mismatches: {bad2 or 'none'}; not_tiered "
      f"{cluster['not_tiered']}, refused {cluster['refused_members']}, "
      f"power_check_undefined {cluster['power_check_undefined']}")
print("  Tier A:", [m for m, x in tier_rows.items() if x["tier"] == "A"])
print("  excluded:", [(m, r["coverage"][r["primary_vehicle"]]["ratio"]) for m, (p, r) in records.items()
                      if "coverage_below_0.95" in r["labels"]])
exp_by_member = defaultdict(set)
for label, (p, r) in records.items():
    exp_by_member[label.split()[0]].add(list(r["coverage"].values())[0]["expected"])
print(f"  coverage 'expected' identical across a member's roots: "
      f"{all(len(v) == 1 for v in exp_by_member.values())} {dict(exp_by_member)}")
floor = {label: r["trade_rate"] for label, (p, r) in records.items() if r["status"] == "run"}
print(f"  floor: max entries/day {max(v['max_entries_per_product_day'] for v in floor.values())}, "
      f"min hold {min(v['min_hold_minutes'] for v in floor.values())}, min mean hold "
      f"{min(v['mean_hold_minutes'] for v in floor.values()):.2f}, entry-cap refusals "
      f"{sum(v['entry_cap_refusals'] for v in floor.values())}, min-hold refusals "
      f"{sum(v['min_hold_refusals'] for v in floor.values())}; labels on run records: "
      f"{[r['labels'] for _, r in records.values() if r['status'] == 'run' and r['labels']] or 'none'}")

# ------------------------------------------------------------------ item 3: two trials from trips
print("== item 3")
costs = json.loads((REPO / "reports" / "stage_e2a_costs.json").read_text())
rel = json.loads((REPO / "reports" / "stage_e2b_release_calendar.json").read_text())
print(f"  cost table sha {sha(REPO / 'reports' / 'stage_e2a_costs.json')[:8]}, release calendar sha "
      f"{sha(REPO / 'reports' / 'stage_e2b_release_calendar.json')[:8]} == record {RELEASE_SHA[:8]}")


def product_costs(root: str):
    entry = costs["products"][root] if isinstance(costs["products"], dict) else next(
        x for x in costs["products"] if x["product"] == root)
    rt = round(float(entry["commission_rt_usd"]) * 100)
    assert rt % 2 == 0
    tick_value_cents = Fraction(str(entry["tick_value_usd"])) * 100
    buckets = [(int(b["start_min"]), int(b["end_min"]), float(b["half_spread_ticks"]),
                {s: float(b["depth_ticks"][s]) for s in ("buy", "sell")},
                {s: float(b["side_ticks"][s]) for s in ("buy", "sell")}) for b in entry["buckets"]]
    assert not any(b.get("fallback") for b in entry["buckets"])
    return rt // 2, tick_value_cents, buckets, max(b[2] for b in buckets), int(entry["q_c"])


def release_instants(root: str) -> list[int]:
    out = []
    for e in rel["releases"]:
        if root in e["products"]:
            dt = datetime.fromisoformat(e["instant_utc"].replace("Z", "+00:00"))
            out.append(int(dt.timestamp()) * 10**9)
    return sorted(out)


def ct_minute(ts_ns: int) -> int:
    d = datetime.fromtimestamp(ts_ns // 10**9, tz=UTC).astimezone(CT)
    return d.hour * 60 + d.minute


def in_window(instants: list[int], ts_ns: int, width: int) -> bool:
    import bisect
    i = bisect.bisect_right(instants, ts_ns) - 1
    return i >= 0 and ts_ns < instants[i] + width


def slip_cents(qty: int, ticks: float, tick_value_cents: Fraction) -> int:
    return math.ceil(round(qty * ticks * float(tick_value_cents), 6))


def rebuild(label: str) -> None:
    p, r = records[label]
    t = trips[label]
    root = r["primary_vehicle"]
    com_side, tv, buckets, max_half, q_c = product_costs(root)
    instants = release_instants(root)
    assert t["record_sha256"] == sha(p), "record_sha256"
    assert t["record_file"] == p.name and t["n_trips"] == len(t["trips"]) == r["series"]["n_trips"]
    daily = defaultdict(Fraction)
    net_ok = 0
    events = 0
    side_symmetric = all(b[3]["buy"] == b[3]["sell"] and b[4]["buy"] == b[4]["sell"] for b in buckets)
    for tr in t["trips"]:
        qty = tr["contracts"]
        gross = cents(tr["gross_cents"])
        net_rec = cents(tr["net_cents"])
        slips = 0
        for ts in (tr["open_ts_ns"], tr["close_ts_ns"]):
            m = ct_minute(ts)
            b = [x for x in buckets if x[0] <= m < x[1]]
            assert len(b) == 1, (label, ts, m)
            event = in_window(instants, ts, EVENT_WINDOW_NS)
            events += event
            ticks = (max_half + b[0][3]["buy"]) if event else b[0][4]["buy"]  # sides symmetric
            slips += slip_cents(qty, ticks, tv)
        net = gross - 2 * qty * com_side - slips
        net_ok += (net == net_rec)
        daily[tr["trade_date"]] += net
    usd_ok = sum(1 for d, v in zip(r["series"]["dates"], r["daily_net_usd"])
                 if float(daily.get(d, 0)) / 100 == v)
    tick_ok = sum(1 for d, v in zip(r["series"]["dates"], r["series"]["values"])
                  if math.isclose(float(daily.get(d, 0) / (tv * q_c)), v, rel_tol=1e-12, abs_tol=1e-12))
    print(f"  {label}: trips {len(t['trips'])}, net == gross - 2x{com_side}c - slippage on "
          f"{net_ok}/{len(t['trips'])}; event-window fills {events}; daily_net_usd matches "
          f"{usd_ok}/{len(r['daily_net_usd'])} days; series.values (cents / {tv} / q_c {q_c}) matches "
          f"{tick_ok}/{len(r['series']['values'])}; sides symmetric in the table: {side_symmetric}; "
          f"record_sha256 ok; close reasons {Counter(x['close_reason'] for x in t['trips'])}")
    verdicts["item3"].append(label)


for label in ("K3-cp1-01 6E", "K3-ldnmom-01 6J"):
    rebuild(label)

# ------------------------------------------------------------------ item 4: event members
print("== item 4")
full = set(C.FX_FULL_SESSIONS)
ew = set(C.EW_BANK_HOLIDAYS)
tgt = set(C.TGT_CLOSING_DAYS)
t_l, t_e, t_t = dict(K.T_L), dict(K.T_E), dict(K.T_T)
r_eq = {me: r for _, me, r in M.MEHEDGE_R_EQ_6J}
lo, hi = RESEARCH[0].isoformat(), RESEARCH[1].isoformat()
event_sets = {
    "K3-ldnrev-01": [d for _, d in C.MONTH_ENDS if d in full and d not in ew and lo <= d <= hi],
    "K3-ldnmom-01": [d for d in C.FX_FULL_SESSIONS if d not in ew and lo <= d <= hi],
    "K3-mehedge-01": [d for _, d in C.MONTH_ENDS if d in full and d not in ew and lo <= d <= hi
                      and r_eq.get(d) not in (None, 0)],
    "K3-ecbfix-01": [d for d in C.FX_FULL_SESSIONS if d not in tgt and lo <= d <= hi],
    "K3-tkypre-01": [d for d in C.GOTOBI_OR_TOKYO_MONTH_END if d in full and lo <= d <= hi],
    "K3-tkypost-01": [d for d in C.TOKYO_BUSINESS_DAYS if d in full and lo <= d <= hi],
}


def hhmm(m: int) -> str:
    return f"{m // 60:02d}:{m % 60:02d}"


def expected_minutes(member: str, d: str) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    """[(open CT minute, day offset)], [(close CT minute, day offset)] of the nominal fills."""
    def hm(s):
        h, m = s.split(":")
        return int(h) * 60 + int(m)
    if member == "K3-ldnrev-01":
        t = hm(t_l[d]); return [(t + 5, 0)], [(t + 20, 0)]
    if member == "K3-ldnmom-01":
        t = hm(t_l[d]); return [(t - 12, 0)], [(t + 5, 0)]
    if member == "K3-mehedge-01":
        t = hm(t_l[d]); return [(t - 60, 0)], [(t - 3, 0)]
    if member == "K3-ecbfix-01":
        t = hm(t_e[d]); return [(60, 0), (t + 1, 0)], [(t, 0), (15 * 60 + 5, 0)]
    if member == "K3-tkypre-01":
        t = hm(t_t[d]); return [(17 * 60 + 30, -1)], [(t, -1)]
    if member == "K3-tkypost-01":
        t = hm(t_t[d]); return [(t + 1, -1)], [(60, 0)]
    raise ValueError(member)


def ct_of(ts_ns: int, trade_date: str) -> tuple[int, int]:
    d = datetime.fromtimestamp(ts_ns // 10**9, tz=UTC).astimezone(CT)
    return d.hour * 60 + d.minute, (d.date() - date.fromisoformat(trade_date)).days


for member, ev in event_sets.items():
    labels = [l for l in records if l.startswith(member + " ")]
    for label in labels:
        p, r = records[label]
        root = r["primary_vehicle"]
        wd = r["window_dates"]
        excluded = {d: k for k, lst in wd["excluded"].items() for d in lst}
        window = {d.isoformat() for d in research_td} - set(excluded)
        window = {d for d in window if wd["first"] <= d <= wd["last"]}
        ev_in = [d for d in ev if d in window]
        ev_out = {d: excluded.get(d, "outside first..last") for d in ev if d not in window}
        legs = 2 if member == "K3-ecbfix-01" else 1
        by_date = defaultdict(list)
        for tr in trips[label]["trips"]:
            by_date[tr["trade_date"]].append(tr)
        off_event = sorted(set(by_date) - set(ev))
        untraded = [d for d in ev_in if d not in by_date]
        partial = [d for d in ev_in if d in by_date and len(by_date[d]) != legs]
        counters = r["engine"]["counters"]
        instants = release_instants(root)
        # fill minutes
        cls = Counter()
        odd = []
        for d, trs in by_date.items():
            if d not in ev:
                continue
            opens, closes = expected_minutes(member, d)
            for i, tr in enumerate(sorted(trs, key=lambda x: x["open_ts_ns"])):
                om, od = ct_of(tr["open_ts_ns"], d)
                cm, cd = ct_of(tr["close_ts_ns"], d)
                eo = opens[min(i, len(opens) - 1)]
                ec = closes[min(i, len(closes) - 1)]
                o_ok = (om, od) == eo
                c_ok = (cm, cd) == ec
                if o_ok and c_ok:
                    cls["nominal"] += 1
                    continue
                why = []
                if not o_ok:
                    if in_window(instants, tr["open_ts_ns"] - NS_MIN * (om - eo[0]) if (om - eo[0]) > 0 else tr["open_ts_ns"], FILL_GUARD_NS) or any(
                            in_window(instants, tr["open_ts_ns"] - k * NS_MIN, FILL_GUARD_NS) for k in range(0, 3)):
                        why.append(f"open {hhmm(om)} vs {hhmm(eo[0])}: D9.5a guard")
                    elif om > eo[0] and od == eo[1]:
                        why.append(f"open {hhmm(om)} vs {hhmm(eo[0])}: later fill (missing bar)")
                    else:
                        why.append(f"open {hhmm(om)}/{od} vs {hhmm(eo[0])}/{eo[1]}: UNEXPLAINED")
                if not c_ok:
                    if tr["close_reason"] == "forced_flatten":
                        why.append(f"close {hhmm(cm)}: F (forced_flatten)")
                    elif tr["close_reason"] == "mll_liquidation":
                        why.append(f"close {hhmm(cm)}: MLL")
                    elif any(in_window(instants, tr["close_ts_ns"] - k * NS_MIN, FILL_GUARD_NS) for k in range(0, 3)):
                        why.append(f"close {hhmm(cm)} vs {hhmm(ec[0])}: D9.5a guard")
                    elif cm > ec[0] and cd == ec[1]:
                        why.append(f"close {hhmm(cm)} vs {hhmm(ec[0])}: later fill (missing bar)")
                    else:
                        why.append(f"close {hhmm(cm)}/{cd} vs {hhmm(ec[0])}/{ec[1]}: UNEXPLAINED")
                for w in why:
                    cls[w.split(":")[-1].strip()] += 1
                if any("UNEXPLAINED" in w for w in why) or not any(x in " ".join(why) for x in ("guard", "missing", "F (", "MLL")):
                    odd.append((d, why))
        print(f"  {label}: events in research {len(ev)}, in window {len(ev_in)}, outside window "
              f"{len(ev_out)} {Counter(ev_out.values())}; traded dates {len(by_date)}, trips "
              f"{len(trips[label]['trips'])}; untraded in-window events {len(untraded)}; partial "
              f"(fewer legs) {len(partial)}; trips off the event set {len(off_event)}; counters {counters}")
        if untraded:
            print(f"     untraded dates: {untraded}")
        if partial:
            print(f"     partial dates: {[(d, len(by_date[d])) for d in partial]}")
        if off_event:
            print(f"     OFF-EVENT TRIPS: {off_event[:10]}")
        print(f"     fill minutes: {dict(cls)}")
        for d, why in odd[:12]:
            print(f"     {d}: {why}")
        verdicts["item4"].append(label)

# ------------------------------------------------------------------ item 5: N
print("== item 5")
screened = [l for l, (p, r) in records.items() if r["status"] == "run" and r["screen"] is not None]
excluded = [l for l, (p, r) in records.items() if r["status"] != "run"]
undeclared = [l for l in records if l not in labels_freeze]
print(f"  screened {len(screened)}; excluded {len(excluded)} {excluded}; refused "
      f"{cluster['refused_members']}; records not in the freeze: {undeclared or 'none'}; "
      f"N = 123 + {len(screened)} = {123 + len(screened)}")

# ------------------------------------------------------------------ item 6: MLL
print("== item 6")
for label, (p, r) in records.items():
    if r["status"] != "run":
        continue
    liq = r["engine"]["accounts_started"] - 1
    cnt = r["engine"]["counters"].get("mll_liquidation", 0)
    tl = sum(1 for x in trips[label]["trips"] if x["close_reason"] == "mll_liquidation")
    tier = tier_rows[label]["tier"]
    if liq or cnt or tl:
        sc = r["screen"]
        print(f"  {label}: accounts_started-1 {liq}, counter {cnt}, liquidation trips {tl}; tier {tier}; "
              f"mean {sc['mean_ticks']:+.4f} t {sc['t_daily']:+.3f}")
    verdicts["item6"].append(label)
print("  Tier A record:", {l: (r['engine']['accounts_started'], r['engine']['counters'])
                           for l, (p, r) in records.items() if tier_rows[l]['tier'] == 'A'})


# ------------------------------------------------------------------ extras
print("== extras")
for label, (p, r) in records.items():
    if r["status"] != "run":
        continue
    tr_ = r["trade_rate"]
    if tr_["min_hold_minutes"] < 10:
        short = [(x["trade_date"], hhmm(ct_of(x["open_ts_ns"], x["trade_date"])[0]), hhmm(ct_of(x["close_ts_ns"], x["trade_date"])[0]), x["close_reason"], x["hold_minutes"]) for x in trips[label]["trips"] if x["hold_minutes"] < 10]
        print(f"  short holds {label}: min {tr_['min_hold_minutes']} mean {tr_['mean_hold_minutes']:.2f}: {short}")
# later fills and MLL legs of the event members
for label in ("K3-ecbfix-01 6E", "K3-tkypre-01 6J", "K3-tkypost-01 6J", "K3-ldnmom-01 6E", "K3-ldnmom-01 6J"):
    member = label.split()[0]
    for x in sorted(trips[label]["trips"], key=lambda z: z["open_ts_ns"]):
        d = x["trade_date"]
        opens, closes = expected_minutes(member, d)
        om, od = ct_of(x["open_ts_ns"], d); cm, cd = ct_of(x["close_ts_ns"], d)
        leg = 0 if member != "K3-ecbfix-01" else (0 if om < 6 * 60 else 1)
        nominal = (om, od) == opens[leg] and (cm, cd) == closes[leg]
        if not nominal:
            print(f"  {label} {d}: open d{od:+d} {hhmm(om)} (nominal {hhmm(opens[leg][0])}), close d{cd:+d} {hhmm(cm)} (nominal {hhmm(closes[leg][0])}), {x['close_reason']}, hold {x['hold_minutes']}")
# cp1 6E fill minutes
cls = Counter()
for x in trips["K3-cp1-01 6E"]["trips"]:
    om, od = ct_of(x["open_ts_ns"], x["trade_date"]); cm, cd = ct_of(x["close_ts_ns"], x["trade_date"])
    cls[(hhmm(om), hhmm(cm), x["close_reason"])] += 1
print("  cp1 6E (open, close, reason) counts:", dict(cls))
# MLL sensitivity: re-screen each trial with its liquidation trips' net removed
print("  liquidation sensitivity (net of MLL trips set to 0):")
for label, (p, r) in records.items():
    if r["status"] != "run":
        continue
    liq = [x for x in trips[label]["trips"] if x["close_reason"] == "mll_liquidation"]
    if not liq:
        continue
    tv = product_costs(r["primary_vehicle"])[1]
    adj = dict(zip(r["series"]["dates"], r["series"]["values"]))
    for x in liq:
        adj[x["trade_date"]] -= float(cents(x["net_cents"]) / tv)
    vals = list(adj.values()); n = len(vals)
    mean = statistics.fmean(vals); sd = statistics.pstdev(vals)
    t = mean / (sd / math.sqrt(n))
    liq_net = sum(float(cents(x["net_cents"]) / tv) for x in liq)
    print(f"    {label}: {len(liq)} liquidations, their net {liq_net:+.1f} ticks; screen without them: mean {mean:+.4f}, t {t:+.3f}, passes {mean > 0 and t >= 1.0}")
