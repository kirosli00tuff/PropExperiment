"""Auditor Part 2 (Task 6): independent recomputation of K8's research-window screen from the
runner's recorded outputs and the frozen tables only. No bar file, no replay, no member call.

Items: 0 frozen files; 1 screen (mean, daily t, passes) per record; 2 tiers (D5, OC-H) and the
largest-day sensitivity; 3 daily series rebuilt from trips + the frozen cost table (HEOD, wkndbtc,
oilcad); 4 trade counts against the calendars and the rules; 5 program N; 6 MLL liquidations and
the counters. Prints a compact log only."""

from __future__ import annotations

import os

os.nice(10)

import bisect  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import statistics  # noqa: E402
import sys  # noqa: E402
from collections import Counter, defaultdict  # noqa: E402
from datetime import UTC, date, datetime, timedelta  # noqa: E402
from pathlib import Path  # noqa: E402
from zoneinfo import ZoneInfo  # noqa: E402

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
sys.path.insert(0, str(REPO))
SCREEN = REPO / "reports/stage_e9_k8_screen"
CT = ZoneInfo("America/Chicago")
NS = 1_000_000_000
MIN_NS = 60 * NS
EVENT_NS = 30 * MIN_NS
GUARD_NS = 2 * MIN_NS

MEMBERS = {
    "K8-flight-01 H30 MGC": ("K8_K8-flight-01_H30_MGC", "MGC"),
    "K8-flight-01 HEOD MGC": ("K8_K8-flight-01_HEOD_MGC", "MGC"),
    "K8-oilcad-01 6C": ("K8_K8-oilcad-01_6C", "6C"),
    "K8-wkndbtc-01 MNQ": ("K8_K8-wkndbtc-01_MNQ", "MNQ"),
}
PART1_SHA = {
    "strategy/members/k8/__init__.py": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "strategy/members/k8/_calendar.py": "1e10dc29234abd5fea8431404d3798b99a22b141298d7c45ab924dad35278f3c",
    "strategy/members/k8/_releases.py": "2acb8ab3fb2d230aaa482e25909a682338d266fe4d5e4336d6b4bb8735db8ea4",
    "strategy/members/k8/flight.py": "020056632df9eea78bcd60a869a5b71eba7083190ed89d969944a4acb1f81b92",
    "strategy/members/k8/oilcad.py": "b64db6b459c047dfba3ebb5ec94b91deba0cd0aace17a4e816ad911d0d5b910c",
    "strategy/members/k8/wkndbtc.py": "04847787d465c10f66e8250d860e9ac744cba5ee0c104c55bb3458ab3906a243",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ct(ns: int) -> datetime:
    return datetime.fromtimestamp(ns // NS, tz=UTC).astimezone(CT)


def hhmm(ns: int) -> str:
    return ct(ns).strftime("%H:%M")


def mod(ns: int) -> int:
    t = ct(ns)
    return t.hour * 60 + t.minute


def load(name: str) -> dict:
    return json.loads((SCREEN / name).read_text(encoding="utf-8"))


# ------------------------------------------------------------------ frozen inputs ----
costs = json.loads((REPO / "reports/stage_e2a_costs.json").read_text())
vehicles = json.loads((REPO / "reports/stage_e2a_vehicles.json").read_text())
cal = json.loads((REPO / "reports/stage_e2b_release_calendar.json").read_text())
INSTANTS: dict[str, list[int]] = defaultdict(list)
for row in cal["releases"]:
    ns = int(datetime.fromisoformat(row["instant_utc"].replace("Z", "+00:00")).timestamp()) * NS
    for r in row["products"]:
        INSTANTS[r].append(ns)
INSTANTS = {r: sorted(set(v)) for r, v in INSTANTS.items()}


def latest_at_or_before(root: str, ts: int) -> int | None:
    arr = INSTANTS[root]
    i = bisect.bisect_right(arr, ts) - 1
    return None if i < 0 else arr[i]


def in_event(root: str, ts: int) -> bool:
    r = latest_at_or_before(root, ts)
    return r is not None and ts < r + EVENT_NS


def in_guard(root: str, ts: int) -> bool:
    r = latest_at_or_before(root, ts)
    return r is not None and ts < r + GUARD_NS


class Cost:
    def __init__(self, root: str) -> None:
        p = costs["products"][root]
        assert p["calibrated"], root
        self.root = root
        self.tv_cents = round(float(p["tick_value_usd"]) * 100)
        self.comm_rt_cents = round(float(p["commission_rt_usd"]) * 100)
        assert self.comm_rt_cents % 2 == 0
        self.comm_side = self.comm_rt_cents // 2
        self.buckets = [(int(b["start_min"]), int(b["end_min"]), float(b["half_spread_ticks"]),
                         {s: float(b["depth_ticks"][s]) for s in ("buy", "sell")},
                         {s: float(b["side_ticks"][s]) for s in ("buy", "sell")}) for b in p["buckets"]]
        assert not any(b.get("fallback") for b in p["buckets"])
        self.max_half = max(b[2] for b in self.buckets)
        self.q_c = int(vehicles["contracts"][root]["q_c"])
        self.tick_value_usd = float(vehicles["contracts"][root]["tick_value_usd"])
        assert abs(self.tick_value_usd * 100 - self.tv_cents) < 1e-9

    def bucket(self, ts: int):  # noqa: ANN201
        m = mod(ts)
        found = [b for b in self.buckets if b[0] <= m < b[1]]
        assert len(found) == 1, (self.root, hhmm(ts), len(found))
        return found[0]

    def slip_cents(self, ts: int, side: str, force_event: bool) -> tuple[int, bool]:
        b = self.bucket(ts)
        event = force_event or in_event(self.root, ts)
        ticks = (self.max_half + b[3][side]) if event else b[4][side]
        return math.ceil(round(1 * ticks * self.tv_cents, 6)), event


COST = {r: Cost(r) for r in ("MGC", "6C", "MNQ")}
print("[inputs] q_c", {r: c.q_c for r, c in COST.items()}, "tick cents", {r: c.tv_cents for r, c in COST.items()},
      "commission side cents", {r: c.comm_side for r, c in COST.items()},
      "instants", {r: len(INSTANTS[r]) for r in COST})
side_symmetric = all(abs(b[4]["buy"] - b[4]["sell"]) < 1e-12 and abs(b[3]["buy"] - b[3]["sell"]) < 1e-12
                     for c in COST.values() for b in c.buckets)
print("[inputs] slippage side-symmetric in every bucket:", side_symmetric)

# ------------------------------------------------------------------ item 0: frozen files ----
freeze = json.loads((REPO / "reports/stage_e_k8_member_freeze.json").read_text())
print("[0] freeze file sha256", sha(REPO / "reports/stage_e_k8_member_freeze.json")[:16],
      "members", [(m["label"], m["ordinal"]) for m in freeze["members"]])
ok0 = True
for rel, info in freeze["files"].items():
    cur = sha(REPO / rel)
    p1 = PART1_SHA.get(rel)
    match = cur == info["sha256"] and (p1 is None or p1 == cur)
    ok0 &= match
    print(f"[0] {rel}: freeze {info['sha256'][:12]} current {cur[:12]} part1 {(p1 or 'n/a')[:12]} {'OK' if match else 'MISMATCH'}")
missing = set(PART1_SHA) - set(freeze["files"])
print("[0] part-1 files absent from the freeze:", sorted(missing), "| all match:", ok0)

# ------------------------------------------------------------------ records ----
records = {label: load(f"{stem}_research.json") for label, (stem, _) in MEMBERS.items()}
trips = {label: load(f"{stem}_research_trips.json") for label, (stem, _) in MEMBERS.items()}
cluster = load("K8_research_cluster.json")

# ------------------------------------------------------------------ item 1: the screen ----
my_screen = {}
for label, rec in records.items():
    root = MEMBERS[label][1]
    s = rec["series"]
    values = [float(v) for v in s["values"]]
    dates = [date.fromisoformat(d) for d in s["dates"]]
    n = len(values)
    mean = statistics.fmean(values)
    sd = statistics.pstdev(values)
    t = mean / (sd / math.sqrt(n))
    passes = mean > 0 and t >= 1.0
    sc = rec["screen"]
    rel = lambda a, b: abs(a - b) / max(abs(b), 1e-300)  # noqa: E731
    wd = rec["window_dates"]
    dn = rec["daily_net_usd"]
    c = COST[root]
    conv_ok = all(abs(dn[i] / (c.q_c * c.tick_value_usd) - values[i]) <= 1e-9 * max(1.0, abs(values[i]))
                  for i in range(n))
    trip_dates = {date.fromisoformat(tp["trade_date"]) for tp in trips[label]["trips"]}
    nonzero = {dates[i] for i in range(n) if values[i] != 0.0}
    excluded = {date.fromisoformat(x) for v in wd["excluded"].values() for x in v}
    my_screen[label] = (mean, sd, t, passes, n, len(trips[label]["trips"]))
    print(f"[1] {label}: n {n} (record {wd['n']}, screen {sc['n_days']}) mean {mean:.12f} (record {sc['mean_ticks']:.12f}, rel {rel(mean, sc['mean_ticks']):.1e}) "
          f"sd {sd:.9f} (rel {rel(sd, sc['sd_pop_ticks']):.1e}) t {t:.12f} (record {sc['t_daily']:.12f}, rel {rel(t, sc['t_daily']):.1e}) passes {passes} (record {sc['passes']}) "
          f"n_trips {sc['n_trips']}={len(trips[label]['trips'])}")
    print(f"    dates: sorted+unique {dates == sorted(set(dates))}, first/last {dates[0]}/{dates[-1]} = {wd['first']}/{wd['last']}, "
          f"weekdays only {all(d.weekday() < 5 for d in dates)}, no excluded date in series {not (set(dates) & excluded)}; "
          f"daily_net_usd/(q_c x tick) == values {conv_ok}; non-zero days {len(nonzero)} <= trip dates {len(trip_dates)}: {len(nonzero) <= len(trip_dates)}; "
          f"non-zero days all trip dates {nonzero <= trip_dates}; trip dates all in series {trip_dates <= set(dates)}; "
          f"trip dates with zero net {len(trip_dates - nonzero)}")

# ------------------------------------------------------------------ item 2: tiers ----
D9_LABELS = ("coverage_below_0.95", "mean_holding_below_10min", "entries_above_20_per_day", "hold_below_2min")
tiers = {m["member_id"]: m for m in cluster["tiers"]["members"]}
for label, rec in records.items():
    mean, sd, t, passes, n, ntr = my_screen[label]
    labels = tuple(rec["labels"])
    tr = rec["trade_rate"]
    my_labels = []
    if not all(v["passes"] for v in rec["coverage"].values()):
        my_labels.append("coverage_below_0.95")
    if tr["mean_hold_minutes"] is not None and tr["mean_hold_minutes"] < 10:
        my_labels.append("mean_holding_below_10min")
    if tr["max_entries_per_product_day"] > 20 or tr["entry_cap_refusals"] > 0:
        my_labels.append("entries_above_20_per_day")
    if tr["min_hold_minutes"] is not None and tr["min_hold_minutes"] < 2 or tr["min_hold_refusals"] > 0:
        my_labels.append("hold_below_2min")
    my_tier = "excluded" if (labels or my_labels) else ("A" if passes else "B")
    runner = tiers[label]
    print(f"[2] {label}: my tier {my_tier} (runner {runner['tier']}, note '{runner['note']}'); record labels {labels}, my D9 labels {my_labels}; "
          f"coverage {{{', '.join(f'{k}: {v['ratio']:.4f}' for k, v in rec['coverage'].items())}}}; trade_rate max/day {tr['max_entries_per_product_day']} min hold {tr['min_hold_minutes']} mean hold {tr['mean_hold_minutes']:.1f}")
    if my_tier == "A":
        values = [float(v) for v in rec["series"]["values"]]
        dates = rec["series"]["dates"]
        order = sorted(range(n), key=lambda i: values[i], reverse=True)
        for k in (1, 2, 3):
            rest = [values[i] for i in range(n) if i not in set(order[:k])]
            m2, s2 = statistics.fmean(rest), statistics.pstdev(rest)
            t2 = m2 / (s2 / math.sqrt(len(rest)))
            print(f"    sensitivity: without the top {k} day(s) {[(dates[i], round(values[i], 1)) for i in order[:k]]}: mean {m2:.3f} t {t2:.4f} ({'passes' if m2 > 0 and t2 >= 1 else 'fails'})")
        worst = min(range(n), key=lambda i: values[i])
        rest = [values[i] for i in range(n) if i != worst]
        m2, s2 = statistics.fmean(rest), statistics.pstdev(rest)
        print(f"    (without the worst day {dates[worst]} {values[worst]:.1f}: t {m2 / (s2 / math.sqrt(len(rest))):.4f})")
print("[2] cluster file: refused", cluster["refused_members"], "not_tiered", cluster["not_tiered"], "power_check_undefined", cluster["power_check_undefined"],
      "harness", cluster["harness_sha256"][:12], "records' harness all equal:", len({r["harness_sha256"] for r in records.values()} | {cluster["harness_sha256"]}) == 1)

# ------------------------------------------------------------------ item 3: trips -> series ----
for label in ("K8-flight-01 HEOD MGC", "K8-wkndbtc-01 MNQ", "K8-oilcad-01 6C"):
    stem, root = MEMBERS[label]
    tr, rec = trips[label], records[label]
    c = COST[root]
    rec_sha = sha(SCREEN / f"{stem}_research.json")
    print(f"[3] {label}: trips {tr['n_trips']}={len(tr['trips'])}; record_sha256 {tr['record_sha256'][:16]} == file {rec_sha[:16]}: {tr['record_sha256'] == rec_sha}; "
          f"status {tr['status']} schema {tr['schema']}")
    by_day: dict[str, int] = defaultdict(int)
    mism = []
    event_fills = Counter()
    for tp in tr["trips"]:
        assert tp["contracts"] == 1 and tp["gross_cents"] == tp["gross_cents_float"]
        side_in = "buy"  # side-symmetric costs: the side cannot change the figure (checked above)
        s_in, e_in = c.slip_cents(tp["open_ts_ns"], side_in, False)
        s_out, e_out = c.slip_cents(tp["close_ts_ns"], "sell", tp["close_reason"] == "price_limit_exit")
        net = tp["gross_cents"] - 2 * c.comm_side - s_in - s_out
        event_fills["entry_event"] += e_in
        event_fills["exit_event"] += e_out
        if net != tp["net_cents"]:
            mism.append((tp["trade_date"], hhmm(tp["open_ts_ns"]), hhmm(tp["close_ts_ns"]), tp["close_reason"], tp["gross_cents"], tp["net_cents"], net))
        by_day[tp["trade_date"]] += tp["net_cents"]
    dates = rec["series"]["dates"]
    values = rec["series"]["values"]
    dn = rec["daily_net_usd"]
    day_mism = []
    for i, d in enumerate(dates):
        cents = by_day.get(d, 0)
        if abs(cents / 100 - dn[i]) > 1e-9 or abs(cents / 100 / (c.q_c * c.tick_value_usd) - values[i]) > 1e-9 * max(1.0, abs(values[i])):
            day_mism.append((d, cents, dn[i], values[i]))
    extra_days = set(by_day) - set(dates)
    print(f"    net rebuilt = gross - 2 x {c.comm_side} c - slippage(entry bucket, event?) - slippage(exit bucket, event? or D9.7 forced): trips matching exactly {len(tr['trips']) - len(mism)}/{len(tr['trips'])}; "
          f"event-window fills entry {event_fills['entry_event']} exit {event_fills['exit_event']}; daily sums vs daily_net_usd and series: mismatching days {len(day_mism)}; trip days outside the series {sorted(extra_days)}")
    for m in mism[:8]:
        print("    MISMATCH", m)
    for m in day_mism[:5]:
        print("    DAY MISMATCH", m)
    print("    gross: not checkable without prices (the trip list carries no fill prices)")

# ------------------------------------------------------------------ item 4: trade counts ----
from strategy.members.k8._calendar import FLIGHT_DATES, OILCAD_DATES, WKNDBTC_DATES  # noqa: E402

rc = json.loads((REPO / "reports/stage_e9_release_check.json").read_text())
eligible = sorted(date.fromisoformat(r["monday"]) for r in rc["B"]["rows"] if r["eligible"])
rec = records["K8-wkndbtc-01 MNQ"]
excl = {k: {date.fromisoformat(x) for x in v} for k, v in rec["window_dates"]["excluded"].items()}
all_excl = set().union(*excl.values())
expected = [d for d in eligible if d not in all_excl]
wtrips = trips["K8-wkndbtc-01 MNQ"]["trips"]
wdates = sorted(date.fromisoformat(t["trade_date"]) for t in wtrips)
change = datetime(2026, 5, 29, 16, 0, tzinfo=CT)
print(f"[4w] eligible Mondays (1b B) {len(eligible)}; excluded among them: roll {len([d for d in eligible if d in excl['roll_blackout_any_leg']])}, "
      f"UR-1 {len([d for d in eligible if d in excl['unseen_roll_UR-1']])}, not-every-leg {len([d for d in eligible if d in excl['not_every_leg_trades']])}; expected trip Mondays {len(expected)}; trips {len(wtrips)} on {len(set(wdates))} dates")
print(f"    unexplained Mondays (expected, no trip): {[str(d) for d in expected if d not in set(wdates)]}; trips on unexpected dates: {[str(d) for d in wdates if d not in set(expected)]}; "
      f"duplicates {[str(d) for d, k in Counter(wdates).items() if k > 1]}; all trip dates in WKNDBTC_DATES and d-3 too: {all(d in set(WKNDBTC_DATES) and d - timedelta(days=3) in set(WKNDBTC_DATES) for d in wdates)}")
entry_ok = [t for t in wtrips if ct(t["open_ts_ns"]).strftime("%a %H:%M") == "Sun 18:00"]
exit_ok = [t for t in wtrips if ct(t["close_ts_ns"]).strftime("%a %H:%M") == "Mon 14:59" and t["close_reason"] == "strategy"]
dev = [(t["trade_date"], ct(t["open_ts_ns"]).strftime("%a %H:%M"), ct(t["close_ts_ns"]).strftime("%a %H:%M"), t["close_reason"], t["hold_minutes"], t["net_cents"]) for t in wtrips if t not in exit_ok]
print(f"    entry fills Sunday 18:00 CT: {len(entry_ok)}/{len(wtrips)}; exit fills Monday 14:59 (strategy): {len(exit_ok)}; deviations: {dev}")
print(f"    guard at any wkndbtc fill (MNQ): {sum(in_guard('MNQ', t['open_ts_ns']) or in_guard('MNQ', t['close_ts_ns']) for t in wtrips)}; "
      f"trips before the 24/7 change {sum(1 for t in wtrips if ct(t['open_ts_ns']) < change)}, after {sum(1 for t in wtrips if ct(t['open_ts_ns']) >= change)} "
      f"(after: {[t['trade_date'] for t in wtrips if ct(t['open_ts_ns']) >= change]})")

# flight
FGRID = {8 * 60 + 35 + 5 * k for k in range(77)}
fl = {v: trips[v]["trips"] for v in ("K8-flight-01 H30 MGC", "K8-flight-01 HEOD MGC")}
fset = set(FLIGHT_DATES)
for v, tl in fl.items():
    dts = [date.fromisoformat(t["trade_date"]) for t in tl]
    series_dates = {date.fromisoformat(d) for d in records[v]["series"]["dates"]}
    on_grid = all(mod(t["open_ts_ns"]) in FGRID for t in tl)
    guarded = [t["trade_date"] for t in tl if in_guard("MGC", t["open_ts_ns"])]
    at_1300 = [t["trade_date"] for t in tl if mod(t["open_ts_ns"]) == 13 * 60]
    fomc_1300 = [d for d in at_1300 if any(ct(i).date() == date.fromisoformat(d) and mod(i) == 13 * 60 for i in INSTANTS["MGC"])]
    print(f"[4f] {v}: trips {len(tl)}; all on FLIGHT_DATES {all(d in fset for d in dts)}; all in the series {all(d in series_dates for d in dts)}; <=1 per date {max(Counter(dts).values()) <= 1}; "
          f"entry fills on the grid 08:35..14:55 {on_grid}; entries inside an MGC guard {guarded}; entries at 13:00 {at_1300} of which on an FOMC date {fomc_1300}")
    if "H30" in v:
        bad = [(t["trade_date"], hhmm(t["open_ts_ns"]), hhmm(t["close_ts_ns"])) for t in tl
               if not (t["close_ts_ns"] == t["open_ts_ns"] + 30 * MIN_NS or (mod(t["close_ts_ns"]) == 15 * 60 + 5 and t["open_ts_ns"] + 30 * MIN_NS > t["close_ts_ns"]))]
        print(f"    exits at T_e + 30 or 15:05 (when T_e + 30 > 15:05): deviations {bad}; holds {sorted(Counter(t['hold_minutes'] for t in tl).items())}")
    else:
        bad = [(t["trade_date"], hhmm(t["open_ts_ns"]), hhmm(t["close_ts_ns"])) for t in tl if mod(t["close_ts_ns"]) != 15 * 60 + 5]
        print(f"    exits at 15:05: deviations {bad}; min hold {min(t['hold_minutes'] for t in tl)} max {max(t['hold_minutes'] for t in tl)}")
h30 = {(t["trade_date"], t["open_ts_ns"]) for t in fl["K8-flight-01 H30 MGC"]}
heod = {(t["trade_date"], t["open_ts_ns"]) for t in fl["K8-flight-01 HEOD MGC"]}
print(f"[4f] H30 and HEOD identical entry (date, fill instant): {h30 == heod} (sides: both BUY by construction; the trip list carries no side; the gross signs differ per trip as the exits differ)")
flight_event = Counter((in_event("MGC", t["open_ts_ns"]), in_event("MGC", t["close_ts_ns"])) for t in fl["K8-flight-01 HEOD MGC"])
print(f"[4f] HEOD (entry in event window, exit in event window) counts: {dict(flight_event)}")

# oilcad
OGRID = {8 * 60 + 5 + 5 * k for k in range(65)}
ol = trips["K8-oilcad-01 6C"]["trips"]
oset = set(OILCAD_DATES)
odts = [date.fromisoformat(t["trade_date"]) for t in ol]
off_grid = [(t["trade_date"], hhmm(t["open_ts_ns"]), in_guard("6C", t["open_ts_ns"])) for t in ol if mod(t["open_ts_ns"]) not in OGRID]
guarded_entries = [(t["trade_date"], hhmm(t["open_ts_ns"])) for t in ol if in_guard("6C", t["open_ts_ns"])]
per_day = Counter(odts)
spacing_bad = []
for d in set(odts):
    opens = sorted(t["open_ts_ns"] for t in ol if t["trade_date"] == d.isoformat())
    gaps = [(b - a) // MIN_NS for a, b in zip(opens, opens[1:], strict=False)]
    if any(g < 20 for g in gaps):
        spacing_bad.append((str(d), gaps))
print(f"[4o] oilcad trips {len(ol)} on {len(per_day)} dates; all on OILCAD_DATES {all(d in oset for d in odts)}; max per day {max(per_day.values())} (<= 17 {max(per_day.values()) <= 17}); "
      f"entries off the 08:05..13:25 grid {off_grid}; entries inside a 6C guard {guarded_entries}; days with entries < 20 min apart {spacing_bad}")
# guarded decision minutes never used as entry fills: 09:30 on 10:30-ET WPSR dates etc.
guard_minutes_by_date = defaultdict(set)
for i in INSTANTS["6C"]:
    d = ct(i).date()
    if date(2025, 4, 1) <= d <= date(2026, 6, 19):
        guard_minutes_by_date[d].update({mod(i), mod(i) + 1})
hits = [(t["trade_date"], hhmm(t["open_ts_ns"])) for t in ol if mod(t["open_ts_ns"]) in guard_minutes_by_date.get(date.fromisoformat(t["trade_date"]), set())]
print(f"    entry fills at a guarded minute of their date (R or R+1 for WPSR/NFP/FOMC rows naming 6C): {hits}")
exits_dev = []
deferral_counts = 0
for t in ol:
    nominal = t["open_ts_ns"] + 15 * MIN_NS
    if t["close_reason"] != "strategy":
        exits_dev.append((t["trade_date"], hhmm(t["open_ts_ns"]), hhmm(t["close_ts_ns"]), t["close_reason"], t["hold_minutes"], t["gross_cents"], t["net_cents"]))
        continue
    if t["close_ts_ns"] == nominal:
        continue
    r = latest_at_or_before("6C", nominal)
    if in_guard("6C", nominal):
        expected_fill = r + GUARD_NS
        kind = f"D9.5a exit deferral (nominal {hhmm(nominal)} in [R={hhmm(r)}, R+2); fill {hhmm(t['close_ts_ns'])} {'== R+2' if t['close_ts_ns'] == expected_fill else '!= R+2'})"
        deferral_counts += (expected_fill - nominal) // MIN_NS
    else:
        kind = f"not a guard: a missing 6C bar at the nominal minute {hhmm(nominal)} (fill {hhmm(t['close_ts_ns'])})"
    exits_dev.append((t["trade_date"], hhmm(t["open_ts_ns"]), t["hold_minutes"], kind))
print(f"[4o] exits not at T_e + 15: {len(exits_dev)}")
for e in exits_dev:
    print("    ", e)
entry_defer = sum((t["open_ts_ns"] - (latest_at_or_before("6C", t["open_ts_ns"]) or 0)) // MIN_NS for t in ol if False)
print(f"    implied fill_guard_deferral counts from exit deferrals: {deferral_counts} (record counter {records['K8-oilcad-01 6C']['engine']['counters'].get('fill_guard_deferral')}); "
      f"entry fills that are exactly R+2 of a 6C instant (a deferred entry would land there): {[(t['trade_date'], hhmm(t['open_ts_ns'])) for t in ol if (lambda r: r is not None and t['open_ts_ns'] == r + GUARD_NS)(latest_at_or_before('6C', t['open_ts_ns']))]}")
print(f"    oilcad event-window fills: entries {sum(in_event('6C', t['open_ts_ns']) for t in ol)}, exits {sum(in_event('6C', t['close_ts_ns']) for t in ol)}")

# ------------------------------------------------------------------ item 5: N ----
screened = [l for l, r in records.items() if r["status"] == "run" and r.get("screen")]
freeze_labels = [m["label"] for m in freeze["members"]]
print(f"[5] screened {len(screened)} {screened}; statuses {Counter(r['status'] for r in records.values())}; refused {cluster['refused_members']} not_tiered {cluster['not_tiered']}; "
      f"records == freeze declarations {sorted(screened) == sorted(freeze_labels)}; record ordinals {[(l, r['ordinal']) for l, r in records.items()]}; N = 194 + {len(screened)} = {194 + len(screened)}")
extra_files = sorted(p.name for p in SCREEN.glob("*.json") if not any(p.name.startswith(s) for s in [v[0] for v in MEMBERS.values()]) and p.name != "K8_research_cluster.json")
print(f"    files in the screen dir not belonging to a declared trial: {extra_files}")

# ------------------------------------------------------------------ item 6: MLL ----
for label, rec in records.items():
    e = rec["engine"]
    print(f"[6] {label}: accounts_started {e['accounts_started']} (MLL restarts {e['accounts_started'] - 1}); counters {e['counters']}; locked_trips {e['locked_trips']}")
mll = [t for t in ol if t["close_reason"] == "mll_liquidation"]
vals = [float(v) for v in records["K8-oilcad-01 6C"]["series"]["values"]]
c6 = COST["6C"]
total_ticks = sum(vals)
mll_ticks = sum(t["net_cents"] for t in mll) / c6.tv_cents
print(f"[6] oilcad MLL trips: {[(t['trade_date'], hhmm(t['open_ts_ns']), hhmm(t['close_ts_ns']), t['hold_minutes'], t['net_cents']) for t in mll]}; their net {mll_ticks:.2f} ticks of a series total {total_ticks:.2f} ticks over {len(vals)} days")
n = len(vals)
alt = list(vals)
dts = records["K8-oilcad-01 6C"]["series"]["dates"]
for t in mll:
    i = dts.index(t["trade_date"])
    alt[i] -= t["net_cents"] / c6.tv_cents
m2, s2 = statistics.fmean(alt), statistics.pstdev(alt)
print(f"    with the two MLL trips set to zero: mean {m2:.4f} t {m2 / (s2 / math.sqrt(n)):.4f} (still fails: mean < 0 {m2 < 0}); "
      f"refused intents while terminal (account_not_active) {records['K8-oilcad-01 6C']['engine']['counters'].get('account_not_active')}: to lift the mean to 0 they would need "
      f"{-total_ticks / max(1, records['K8-oilcad-01 6C']['engine']['counters'].get('account_not_active', 1)):.1f} net ticks each (6C tick 0.00005: {-total_ticks / 7 * 0.00005:.5f} USD/CAD per 15-minute trade); "
      f"to reach t = 1 with the same sd they would need a mean of {s2 / math.sqrt(n):.3f} ticks/day, i.e. a total of {s2 / math.sqrt(n) * n - total_ticks:.1f} ticks from 7 trades")
print("PART2 DONE")
