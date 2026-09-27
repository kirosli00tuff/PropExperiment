"""Task 6 audit: recompute K4's research-window screen figures from the runner's recorded outputs
and the frozen tables, in code independent of screening/stage_e_stats.py and the runner.
Read-only. No bar file is opened. Run: PYTHONPATH=. uv run python reports/stage_e4_briefs/audit/recompute_screen.py
"""
from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import UTC, date, datetime, timedelta
from fractions import Fraction
from pathlib import Path
from zoneinfo import ZoneInfo

from data.group_session import load_group_calendar, trade_dates_between
from strategy.members.k4._calendar import ENERGY_FULL_SESSIONS
from strategy.members.k4._releases import FEDERAL_MONDAY_HOLIDAYS, NGS, NYSE_NOT_FULL, WPSR

CT = ZoneInfo("America/Chicago")
OUT = Path("reports/stage_e4_k4_screen")
W0, W1 = date(2025, 4, 1), date(2026, 6, 19)
NS_MIN = 60_000_000_000
EVENT_WINDOW_MIN = 30
REL_TOL = 1e-9
SCREEN_T_MIN = 1.0
COVERAGE_MIN = 0.95


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cents(value) -> Fraction:
    return Fraction(value) if isinstance(value, str) else Fraction(int(value))


def rel_eq(a: float, b: float) -> bool:
    return abs(a - b) <= REL_TOL * max(1.0, abs(a), abs(b))


def ct_of(ns: int) -> datetime:
    return datetime.fromtimestamp(ns / 1e9, tz=UTC).astimezone(CT)


def hhmm(ns: int) -> str:
    return ct_of(ns).strftime("%H:%M")


def minute_of_day(ns: int) -> int:
    t = ct_of(ns)
    return t.hour * 60 + t.minute


# ------------------------------------------------------------------ load ----
records = {}
trips = {}
for p in sorted(OUT.glob("K4_*_research.json")):
    r = json.loads(p.read_text())
    records[r["member"]] = (r, p)
for p in sorted(OUT.glob("K4_*_research_trips.json")):
    t = json.loads(p.read_text())
    trips[t["member"]] = (t, p)
cluster = json.loads((OUT / "K4_research_cluster.json").read_text())
freeze = json.loads(Path("reports/stage_e_k4_member_freeze.json").read_text())
costs = json.loads(Path("reports/stage_e2a_costs.json").read_text())["products"]
calendar = json.loads(Path("reports/stage_e2b_release_calendar.json").read_text())
ecal = load_group_calendar("energy")
all_trade_dates = list(trade_dates_between(ecal, W0, W1))
print(f"records {len(records)}, trip lists {len(trips)}, energy trade dates in window {len(all_trade_dates)}")

release_ns: dict[str, list[int]] = defaultdict(list)
for r in calendar["releases"]:
    inst = int(datetime.fromisoformat(r["instant_utc"].replace("Z", "+00:00")).timestamp()) * 10**9
    for root in r["products"]:
        release_ns[root].append(inst)


def in_event_window(root: str, fill_ns: int) -> bool:
    return any(rel <= fill_ns < rel + EVENT_WINDOW_MIN * NS_MIN for rel in release_ns[root])


# ------------------------------------------------------------ item 1 + 2 ----
print("\n=== Item 1: screen recomputation and window dates ===")
tier_expected = {}
verdicts1 = []
for label, (rec, path) in records.items():
    root = rec["primary_vehicle"]
    values = rec["series"]["values"]
    dates = [date.fromisoformat(d) for d in rec["series"]["dates"]]
    n = len(values)
    mean = math.fsum(values) / n
    sd = math.sqrt(math.fsum((v - mean) ** 2 for v in values) / n)
    t = mean / (sd / math.sqrt(n)) if sd > 0 else None
    passes = bool(mean > 0 and t is not None and t >= SCREEN_T_MIN)
    s = rec["screen"]
    ok = (rel_eq(mean, s["mean_ticks"]) and rel_eq(sd, s["sd_pop_ticks"]) and rel_eq(t, s["t_daily"])
          and passes == s["passes"] and n == s["n_days"] and s["n_trips"] == rec["series"]["n_trips"]
          == rec["trade_rate"]["n_trips"] == len(trips[label][0]["trips"]) == trips[label][0]["n_trips"])
    # window dates
    ex = rec["window_dates"]["excluded"]
    excluded = {date.fromisoformat(d) for k in ex for d in ex[k]}
    expected_dates = [d for d in all_trade_dates if d not in excluded]
    dates_ok = (dates == expected_dates and rec["window_dates"]["n"] == n == len(rec["daily_net_usd"])
                and date(2026, 6, 18) not in dates and date(2026, 6, 19) not in dates
                and dates[0].isoformat() == rec["window_dates"]["first"] and dates[-1].isoformat() == rec["window_dates"]["last"])
    trip_dates = Counter(x["trade_date"] for x in trips[label][0]["trips"])
    nonzero = [d for d, v in zip(rec["series"]["dates"], values) if v != 0.0]
    nz_ok = all(d in trip_dates for d in nonzero) and len(nonzero) <= s["n_trips"] and all(
        date.fromisoformat(d) in set(dates) for d in trip_dates)
    # values from trips: each trip's net divided by its own contracts, in ticks of the vehicle
    tv_cents = Fraction(str(costs[root]["tick_value_usd"])) * 100
    by_day_ticks: dict[str, Fraction] = defaultdict(Fraction)
    by_day_cents: dict[str, Fraction] = defaultdict(Fraction)
    for x in trips[label][0]["trips"]:
        by_day_ticks[x["trade_date"]] += cents(x["net_cents"]) / x["contracts"] / tv_cents
        by_day_cents[x["trade_date"]] += cents(x["net_cents"])
    vals_ok = all(rel_eq(float(by_day_ticks.get(d, 0)), v) for d, v in zip(rec["series"]["dates"], values))
    usd_ok = all(rel_eq(float(by_day_cents.get(d, 0) / 100), v) for d, v in zip(rec["series"]["dates"], rec["daily_net_usd"]))
    rec_sha_ok = trips[label][0]["record_sha256"] == sha(path) and trips[label][0]["record_file"] == path.name
    tier_expected[label] = ("excluded" if rec["labels"] else ("A" if passes else "B"))
    cov = rec["coverage"][root]
    cov_ok = cov["passes"] == (cov["ratio"] >= COVERAGE_MIN) and rel_eq(cov["ratio"], cov["present"] / cov["expected"])
    verdict = "VERIFIED" if all((ok, dates_ok, nz_ok, vals_ok, usd_ok, rec_sha_ok, cov_ok)) else "DISCREPANCY"
    verdicts1.append(verdict)
    print(f"{label:18s} n={n} trips={s['n_trips']:3d} mean={mean:+.6f} sd={sd:.6f} t={t:+.6f} passes={passes} "
          f"| screen {ok} dates {dates_ok} nonzero {nz_ok} values-from-trips {vals_ok} usd {usd_ok} "
          f"rec_sha {rec_sha_ok} cov {cov['ratio']:.5f} {cov_ok} | {verdict}")
    if not dates_ok:
        print("   dates differ:", len(dates), len(expected_dates), sorted(set(dates) ^ set(expected_dates))[:10])
print("item 1 verdicts:", Counter(verdicts1))

print("\n=== Item 2: tiers ===")
tier_rows = {m["member_id"]: m for m in cluster["tiers"]["members"]}
ok_all = True
for label, (rec, _) in records.items():
    m = tier_rows[label]
    tr = rec["trade_rate"]
    # the frozen D9 labels (runner docstring item 6): entries_above_20_per_day / hold_below_2min are set on a
    # REFUSED member attempt (entry_cap_refusals, min_hold_refusals), mean_holding_below_10min on the mean hold
    floor_ok = (tr["max_entries_per_product_day"] <= 20 and tr["mean_hold_minutes"] >= 10
                and tr["entry_cap_refusals"] == 0 and tr["min_hold_refusals"] == 0)
    same_screen = m["screen"] == rec["screen"]
    ok = m["tier"] == tier_expected[label] and m["labels"] == rec["labels"] == [] and same_screen and floor_ok
    ok_all &= ok
    print(f"{label:18s} tier {m['tier']} expected {tier_expected[label]} labels {m['labels']} screen==record {same_screen} "
          f"floor(max/day {tr['max_entries_per_product_day']}, min hold {tr['min_hold_minutes']:.0f}, mean hold {tr['mean_hold_minutes']:.1f}) {floor_ok} note='{m['note']}' -> {'VERIFIED' if ok else 'DISCREPANCY'}")
print("cluster: not_tiered", cluster["not_tiered"], "refused", cluster["refused_members"], "power_check_undefined", cluster["power_check_undefined"],
      "tier A:", [k for k, v in tier_rows.items() if v["tier"] == "A"], "| item 2:", "VERIFIED" if ok_all else "DISCREPANCY")

# ---------------------------------------------------------------- item 3 ----
print("\n=== Item 3: trips rebuilt from the frozen cost table (no replay) ===")


def product_costs(root: str):
    p = costs[root]
    buckets = p["buckets"]
    for b in buckets:
        assert not b["fallback"], (root, b["key"])
    max_hs = max(b["half_spread_ticks"] for b in buckets)
    rt_cents = int(Fraction(str(p["commission_rt_usd"])) * 100)
    assert rt_cents % 2 == 0
    tv_cents = Fraction(str(p["tick_value_usd"])) * 100
    return buckets, max_hs, rt_cents, tv_cents


def bucket_at(buckets, minute: int):
    found = [b for b in buckets if b["start_min"] <= minute < b["end_min"]]
    assert len(found) == 1, (minute, [b["key"] for b in found])
    return found[0]


def slippage_cents(qty: int, ticks: float, tv_cents: Fraction) -> int:
    return math.ceil(round(qty * ticks * float(tv_cents), 6))


for label in ("K4-cp1-01 MCL", "K4-ngpre-01 NG", *[l for l in records if l not in ("K4-cp1-01 MCL", "K4-ngpre-01 NG")]):
    rec, _ = records[label]
    root = rec["primary_vehicle"]
    buckets, max_hs, rt_cents, tv_cents = product_costs(root)
    bad = []
    n_event = 0
    asym = set()
    by_day: dict[str, Fraction] = defaultdict(Fraction)
    by_day_ticks: dict[str, Fraction] = defaultdict(Fraction)
    for x in trips[label][0]["trips"]:
        q = x["contracts"]
        slip = 0
        for fill_ns, side in ((x["open_ts_ns"], "open"), (x["close_ts_ns"], "close")):
            b = bucket_at(buckets, minute_of_day(fill_ns))
            # the trip list carries no side; the buckets K4 fills land in must be side-symmetric
            if b["side_ticks"]["buy"] != b["side_ticks"]["sell"] or b["depth_ticks"]["buy"] != b["depth_ticks"]["sell"]:
                asym.add(b["key"])
            ev = in_event_window(root, fill_ns)
            n_event += ev
            ticks = (max_hs + b["depth_ticks"]["buy"]) if ev else b["side_ticks"]["buy"]
            slip += slippage_cents(q, ticks, tv_cents)
        net = cents(x["gross_cents"]) - rt_cents * q - slip
        if net != cents(x["net_cents"]):
            bad.append((x["trade_date"], hhmm(x["open_ts_ns"]), hhmm(x["close_ts_ns"]), str(cents(x["net_cents"])), str(net)))
        by_day[x["trade_date"]] += net
        by_day_ticks[x["trade_date"]] += net / q / tv_cents
    vals_ok = all(rel_eq(float(by_day_ticks.get(d, 0)), v) for d, v in zip(rec["series"]["dates"], rec["series"]["values"]))
    usd_ok = all(rel_eq(float(by_day.get(d, 0) / 100), v) for d, v in zip(rec["series"]["dates"], rec["daily_net_usd"]))
    print(f"{label:18s}: {len(trips[label][0]['trips']):3d} trips, commission rt {rt_cents} c/contract, max half-spread {max_hs:.4f} ticks, "
          f"event-window fills {n_event:3d}, asymmetric buckets hit {sorted(asym)}, net mismatches {len(bad)}, series match {vals_ok}, "
          f"daily_net_usd match {usd_ok} -> {'VERIFIED' if not bad and vals_ok and usd_ok and not asym else 'DISCREPANCY'}")
    for b in bad[:10]:
        print("   mismatch", b)

# ---------------------------------------------------------------- item 4 ----
print("\n=== Item 4: event reconciliation, fill minutes, ovr limits ===")
wpsr = {d: (t, wd, std) for d, t, wd, std in WPSR}
ngs = dict(NGS)
nyse = set(NYSE_NOT_FULL)
full = set(ENERGY_FULL_SESSIONS)


def cm(hhmm_text: str) -> int:
    h, m = hhmm_text.split(":")
    return int(h) * 60 + int(m)


def fmt(minute: int) -> str:
    return f"{minute // 60:02d}:{minute % 60:02d}"


def explain_untraded(label: str, events: list[str]) -> None:
    rec, _ = records[label]
    ex = rec["window_dates"]["excluded"]
    blackout = set(ex["roll_blackout_any_leg"])
    ur1 = set(ex["unseen_roll_UR-1"])
    traded = {x["trade_date"] for x in trips[label][0]["trips"]}
    halts = {d for d in events if ecal.early_halt_ct(date.fromisoformat(d)) is not None}
    untraded = [d for d in events if d not in traded]
    reasons = Counter()
    silent = []
    for d in untraded:
        if d in blackout:
            reasons["roll blackout (not a window date; an emitted entry is refused engine_not_a_window_date)"] += 1
        elif d in ur1:
            reasons["UR-1 (2026-06-18/19)"] += 1
        elif d in halts:
            reasons["early halt"] += 1
        elif date.fromisoformat(d) > date.fromisoformat(rec["window_dates"]["last"]):
            reasons["after the window's last date"] += 1
        else:
            reasons["silent no-trade (rule condition or missing bar; no counter)"] += 1
            silent.append(d)
    counters = rec["engine"]["counters"]
    print(f"{label}: events {len(events)}, traded {len(traded)} (trips {len(trips[label][0]['trips'])}), untraded {len(untraded)}: {dict(reasons)}; "
          f"engine counters {counters}")
    if silent:
        print(f"   silent dates: {silent}")
    extra = sorted(traded - set(events))
    if extra:
        print(f"   TRADED OUTSIDE THE EVENT SET: {extra}")


win = lambda d: W0.isoformat() <= d <= W1.isoformat()  # noqa: E731
ngs_events = [d for d in ngs if win(d)]
apipre_events = [d for d, (t, wd, std) in wpsr.items() if win(d) and std
                 and (date.fromisoformat(d) - timedelta(days=1)).isoformat() in full
                 and (date.fromisoformat(d) - timedelta(days=2)).isoformat() not in set(FEDERAL_MONDAY_HOLIDAYS)]
eiafade_events = [d for d, (t, wd, std) in wpsr.items() if win(d) and cm(t) + 15 <= cm("13:13")]
eiamom_events = [d for d, (t, wd, std) in wpsr.items() if win(d) and std and d not in nyse]
explain_untraded("K4-ngpre-01 NG", ngs_events)
explain_untraded("K4-apipre-01 MCL", apipre_events)
explain_untraded("K4-eiafade-01 MCL", eiafade_events)
explain_untraded("K4-eiamom-01 MCL", eiamom_events)

print("\n-- fill minutes against the rule --")


def rule_minutes(label: str, x: dict) -> tuple[int | None, int | None]:
    """(entry fill minute, exit fill minute) the rule names, CT; None when the rule fixes no single minute."""
    d = x["trade_date"]
    mid = label.split()[0]
    if mid == "K4-cp1-01":
        return cm("13:00"), cm("13:29")
    if mid == "K4-cp3-01":
        return cm("08:01"), cm("13:29")
    if mid == "K4-ngpre-01":
        t = cm(ngs[d]); return t - 90, t + 30
    if mid == "K4-apipre-01":
        return cm("07:30"), cm("09:29")
    if mid == "K4-eiafade-01":
        return cm(wpsr[d][0]) + 15, cm("13:29")
    if mid == "K4-eiamom-01":
        return cm("14:30"), cm("14:59")
    if mid == "K4-cp2-01":
        o = minute_of_day(x["open_ts_ns"]); return None, None
    if mid == "K4-ovr-01":
        o = minute_of_day(x["open_ts_ns"]); return None, None
    raise KeyError(mid)


for label, (rec, _) in records.items():
    root = rec["primary_vehicle"]
    mid = label.split()[0]
    exact = 0
    devs = []
    for x in trips[label][0]["trips"]:
        o, c = minute_of_day(x["open_ts_ns"]), minute_of_day(x["close_ts_ns"])
        eo, ec = rule_minutes(label, x)
        if mid == "K4-cp2-01":
            eo_ok = cm("08:16") <= o <= cm("13:30")
            ec_ok = c == o + 75
            eo, ec = (o if eo_ok else None), o + 75
        elif mid == "K4-ovr-01":
            eo_ok = o in {cm("09:00"), cm("10:00"), cm("11:00"), cm("12:00"), cm("13:00")}
            ec_ok = c == o + 59
            eo, ec = (o if eo_ok else None), o + 59
        else:
            eo_ok, ec_ok = o == eo, c == ec
        if eo_ok and ec_ok and x["close_reason"] == "strategy":
            exact += 1
        else:
            kind = []
            if not eo_ok:
                kind.append(f"entry {fmt(o)} vs {fmt(eo) if eo is not None else '?'}" + (" [release+2: D9.5a]" if eo is not None and o - eo == 2 and in_event_window(root, x["open_ts_ns"]) else ""))
            if not ec_ok:
                kind.append(f"exit {fmt(c)} vs {fmt(ec)}" + (" [release+2: D9.5a]" if c - ec == 2 and in_event_window(root, x["close_ts_ns"]) else ""))
            if x["close_reason"] != "strategy":
                kind.append(f"close_reason {x['close_reason']}")
            devs.append((x["trade_date"], "; ".join(kind)))
    print(f"{label:18s} trips {len(trips[label][0]['trips']):3d} exact {exact:3d} deviations {len(devs)}")
    for d in devs:
        print("   ", d)

print("\n-- ovr: entries per day and overlap --")
for label in ("K4-ovr-01 MCL", "K4-ovr-01 NG"):
    ts = sorted(trips[label][0]["trips"], key=lambda x: x["open_ts_ns"])
    per_day = Counter(x["trade_date"] for x in ts)
    overlaps = sum(1 for a, b in zip(ts, ts[1:]) if b["open_ts_ns"] < a["close_ts_ns"])
    print(f"{label}: trips {len(ts)}, max entries/day {max(per_day.values())}, days with 5 {sum(1 for v in per_day.values() if v == 5)}, "
          f"overlaps {overlaps}, holds {Counter(x['hold_minutes'] for x in ts).most_common(3)}, "
          f"entry minutes {sorted(Counter(hhmm(x['open_ts_ns']) for x in ts).items())}")

# ---------------------------------------------------------------- item 5 ----
print("\n=== Item 5: program N ===")
frozen_labels = [m["label"] for m in freeze["members"]]
statuses = Counter(rec["status"] for rec, _ in records.values())
screened = [l for l, (rec, _) in records.items() if rec["status"] == "run" and rec.get("screen")]
undeclared = [l for l in records if l not in frozen_labels]
missing = [l for l in frozen_labels if l not in records]
print(f"statuses {dict(statuses)}, screened {len(screened)}, refused {cluster['refused_members']}, not_tiered {cluster['not_tiered']}, "
      f"undeclared records {undeclared}, frozen members without a record {missing}, ordinals match "
      f"{all(records[m['label']][0]['ordinal'] == m['ordinal'] for m in freeze['members'])}, "
      f"cluster_freeze_sha256 in records {set(rec['cluster_freeze_sha256'] for rec, _ in records.values())}, "
      f"harness {set(rec['harness_sha256'] for rec, _ in records.values())}, N = 102 + {len(screened)} = {102 + len(screened)}")

# ---------------------------------------------------------------- item 6 ----
print("\n=== Item 6: MLL liquidations ===")
for label, (rec, _) in records.items():
    n_mll = rec["engine"]["accounts_started"] - 1
    c_mll = rec["engine"]["counters"].get("mll_liquidation", 0)
    mll_trips = [x for x in trips[label][0]["trips"] if x["close_reason"] == "mll_liquidation"]
    values = rec["series"]["values"]
    dates = rec["series"]["dates"]
    mll_days = {x["trade_date"] for x in mll_trips}

    def scr(vs):
        n = len(vs); m = math.fsum(vs) / n; sd = math.sqrt(math.fsum((v - m) ** 2 for v in vs) / n)
        t = m / (sd / math.sqrt(n)) if sd > 0 else None
        return m, t, bool(m > 0 and t is not None and t >= SCREEN_T_MIN)

    base = scr(values)
    zeroed = scr([0.0 if d in mll_days else v for d, v in zip(dates, values)]) if mll_days else base
    dropped = scr([v for d, v in zip(dates, values) if d not in mll_days]) if mll_days else base
    print(f"{label:18s} MLL {n_mll} (counter {c_mll}, trips {len(mll_trips)}) days {sorted(mll_days)} "
          f"values {[round(v, 2) for d, v in zip(dates, values) if d in mll_days]} | passes {base[2]}; "
          f"zeroed -> {zeroed[2]} (t {zeroed[1]:+.3f}); dropped -> {dropped[2]} (t {dropped[1]:+.3f})")
