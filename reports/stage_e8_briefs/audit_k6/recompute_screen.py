"""Auditor's recomputation of the K6 research screen (Stage E.8 Task 6, Part 2 items 1, 2, 4, 5, 6).

    PYTHONPATH=. uv run python reports/stage_e8_briefs/audit_k6/recompute_screen.py

Reads only the runner's records and trip lists under reports/stage_e8_k6_screen/, the frozen member
tables (strategy/members/k6/_calendar.py, _wasde.py, _limits.py), the cluster freeze and
rules.products. Opens no bar file. Prints counts and every difference; writes nothing.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from fractions import Fraction
from pathlib import Path
from zoneinfo import ZoneInfo

from rules.products import product
from strategy.members.k6 import _calendar as cal
from strategy.members.k6 import _limits as lim
from strategy.members.k6 import _wasde as wd

CT = ZoneInfo("America/Chicago")
OUT = Path("reports/stage_e8_k6_screen")
REL = 1e-9
problems: list[str] = []
notes: list[str] = []


def ct(utc_iso: str) -> datetime:
    return datetime.fromisoformat(utc_iso.replace("Z", "+00:00")).astimezone(CT)


def cents(v) -> Fraction:
    return Fraction(v) if isinstance(v, str) else Fraction(int(v))


def close(a: float, b: float) -> bool:
    return abs(a - b) <= REL * max(1.0, abs(a), abs(b))


def load() -> list[tuple[dict, dict]]:
    out = []
    for rec_path in sorted(OUT.glob("K6_*_research.json")):
        if rec_path.name.endswith("_trips.json"):
            continue
        rec = json.loads(rec_path.read_text())
        trips_path = OUT / rec_path.name.replace("_research.json", "_research_trips.json")
        trips = json.loads(trips_path.read_text())
        sha = hashlib.sha256(rec_path.read_bytes()).hexdigest()
        if trips["record_sha256"] != sha or trips["record_file"] != rec_path.name:
            problems.append(f"{rec['member']}: trip list record_sha256/record_file mismatch")
        if trips["n_trips"] != len(trips["trips"]):
            problems.append(f"{rec['member']}: n_trips {trips['n_trips']} != {len(trips['trips'])}")
        out.append((rec, trips))
    return out


def item1(rec: dict, trips: dict) -> str:
    """Mean and daily t from series.values; dates; daily sums from the trips."""
    m = rec["member"]
    root = rec["primary_vehicle"]
    s = rec["series"]
    vals, dates = s["values"], s["dates"]
    n = len(vals)
    mean = sum(vals) / n
    sd = math.sqrt(sum((v - mean) ** 2 for v in vals) / n)
    t = mean / (sd / math.sqrt(n)) if sd > 0 else None
    passes = (sd > 0 and mean > 0 and t >= 1.0) if sd > 0 else False
    scr = rec["screen"]
    ok = (close(mean, scr["mean_ticks"]) and close(sd, scr["sd_pop_ticks"]) and n == scr["n_days"]
          and ((t is None and scr["t_daily"] is None) or (t is not None and scr["t_daily"] is not None
                                                           and close(t, scr["t_daily"])))
          and passes == scr["passes"] and scr["n_trips"] == len(trips["trips"]) == s["n_trips"])
    # dates: the group's trade dates in [first, last] less the exclusions, one value each
    group = product(root).group
    table = cal.GRAIN_TRADE_DATES if group == "grains" else cal.LIVESTOCK_TRADE_DATES
    w = rec["window_dates"]
    excluded = set()
    for v in w["excluded"].values():
        excluded |= set(v)
    expected_dates = [d.isoformat() for d in table if w["first"] <= d.isoformat() <= w["last"]
                      and d.isoformat() not in excluded]
    dates_ok = dates == expected_dates and len(dates) == w["n"] == len(set(dates)) == len(rec["daily_net_usd"])
    # daily sums from trips, converted to ticks per contract
    tv = Fraction(str(product(root).tick_value_usd)) * 100
    per_day: dict[str, Fraction] = defaultdict(Fraction)
    for tr in trips["trips"]:
        per_day[tr["trade_date"]] += cents(tr["net_cents"])
    daily_ok = True
    for d, v, usd in zip(dates, vals, rec["daily_net_usd"], strict=True):
        c = per_day.get(d, Fraction(0))
        if not close(float(c / 100), usd) or not close(float(c / tv), v):
            daily_ok = False
    nonzero = [d for d, v in zip(dates, vals, strict=True) if v != 0]
    trip_dates = set(per_day)
    nz_ok = set(nonzero) <= trip_dates and trip_dates <= set(dates)
    verdict = "OK" if ok and dates_ok and daily_ok and nz_ok else "DIFF"
    if verdict != "OK":
        problems.append(f"{m}: item 1 screen={ok} dates={dates_ok} daily={daily_ok} nonzero={nz_ok}")
    tstr = "None" if t is None else f"{t:.6f}"
    return (f"{m:22s} n={n:3d} mean={mean:+.6f} sd={sd:.6f} t={tstr:>10s} passes={passes!s:5s} "
            f"trips={len(trips['trips']):3d} nonzero_days={len(nonzero):3d} {verdict}")


def item4(rec: dict, trips: dict) -> list[str]:
    m = rec["member"]
    member_id, root = m.split()
    group = product(root).group
    full = cal.GRAIN_FULL_SESSIONS if group == "grains" else cal.LIVESTOCK_FULL_SESSIONS
    w = rec["window_dates"]
    excluded = set()
    for v in w["excluded"].values():
        excluded |= set(v)
    window = set(rec["series"]["dates"])
    rows = trips["trips"]
    lines = []
    opens = Counter(ct(x["open_utc"]).strftime("%H:%M") for x in rows)
    closes_strategy = Counter(ct(x["close_utc"]).strftime("%H:%M") for x in rows if x["close_reason"] == "strategy")
    reasons = Counter(x["close_reason"] for x in rows)
    per_day = Counter(x["trade_date"] for x in rows)
    multi = [d for d, k in per_day.items() if k > 1]
    legs = [leg["root"] for leg in rec["legs"]]
    roots = Counter(x["root"] for x in rows)
    off_window = [x["trade_date"] for x in rows if x["trade_date"] not in window]
    if multi or off_window or set(roots) - {root}:
        problems.append(f"{m}: multi-entry dates {multi}; trips off window {off_window}; roots {dict(roots)}")
    rule = {"K6-cp1-01": ({"grains": "12:45", "livestock": "12:30"}[group], {"grains": "13:14", "livestock": "12:59"}[group]),
            "K6-cp3-01": ("08:31", {"grains": "13:14", "livestock": "12:59"}[group]),
            "K6-crushgap-01": ("08:31", "13:14"), "K6-limitcont-01": ("08:45", "12:59"),
            "K6-wasdepre-01": ("10:30", "11:15"), "K6-wasdepost-01": ("11:15", "13:14")}.get(member_id)
    if rule:
        bad_open = {k: v for k, v in opens.items() if k != rule[0]}
        bad_close = {k: v for k, v in closes_strategy.items() if k != rule[1]}
        # a strategy exit later than the rule minute is allowed only when the named bar was missing
        # (first later bar); report any such case for the lead
        if bad_open:
            problems.append(f"{m}: entry fills off the rule minute {bad_open}")
        if bad_close:
            notes.append(f"{m}: strategy exits off the rule minute {bad_close} (missing named bar or deferral; listed)")
        lines.append(f"  entries {dict(opens)} | strategy exits {dict(closes_strategy)} | reasons {dict(reasons)} | multi-entry dates {len(multi)} | off-window trips {len(off_window)} | roots {dict(roots)} legs {legs}")
    else:  # CP2: hold 75 or a deferral (76 with the close at release + 2), or an engine exit
        holds = Counter(x["hold_minutes"] for x in rows if x["close_reason"] == "strategy")
        odd = [(x["trade_date"], ct(x["open_utc"]).strftime("%H:%M"), ct(x["close_utc"]).strftime("%H:%M"), x["hold_minutes"])
               for x in rows if x["close_reason"] == "strategy" and x["hold_minutes"] != 75.0]
        bad_odd = [o for o in odd if o[2] not in ("11:02", "13:02")]
        if bad_odd:
            problems.append(f"{m}: CP2 strategy exits with hold != 75 not at a deferral minute {bad_odd}")
        lines.append(f"  CP2 strategy holds {dict(holds)} odd {odd} | reasons {dict(reasons)} | multi-entry dates {len(multi)} | off-window trips {len(off_window)} | roots {dict(roots)}")
        first_eligible = [x for x in rows if ct(x["open_utc"]).strftime("%H:%M") < "08:46"]
        if first_eligible:
            problems.append(f"{m}: CP2 entry fill before 08:46 {len(first_eligible)}")
    # new members: trips only on full-session dates
    if member_id in ("K6-crushgap-01", "K6-limitcont-01", "K6-wasdepre-01", "K6-wasdepost-01"):
        off_full = [x["trade_date"] for x in rows if date.fromisoformat(x["trade_date"]) not in full]
        if off_full:
            problems.append(f"{m}: trips on non-full-session dates {off_full}")
        lines.append(f"  trips on non-full-session dates: {off_full}")
    if member_id in ("K6-wasdepre-01", "K6-wasdepost-01"):
        events = sorted(d for d in wd.WASDE_DATES if w["first"] <= d.isoformat() <= w["last"] and d in full)
        in_window = [d for d in events if d.isoformat() in window]
        excluded_events = [d.isoformat() for d in events if d.isoformat() in excluded]
        trip_dates = {x["trade_date"] for x in rows}
        missing = [d.isoformat() for d in in_window if d.isoformat() not in trip_dates]
        extra = sorted(trip_dates - {d.isoformat() for d in in_window})
        counters = rec["engine"]["counters"]
        lines.append(f"  WASDE dates in [first,last] and full sessions: {len(events)}; excluded by the window {excluded_events}; "
                     f"event dates in window {len(in_window)}; trips {len(trip_dates)}; event dates without a trip {missing}; "
                     f"trips on non-event dates {extra}; counters {dict(counters)}")
        if extra:
            problems.append(f"{m}: trips on non-WASDE dates {extra}")
    if member_id == "K6-limitcont-01":
        table = cal.LIVESTOCK_TRADE_DATES
        first = date.fromisoformat(w["first"])
        dropped = set(lim.DROPPED_LIMIT_DATES.get(root, {}))
        for x in rows:
            d = date.fromisoformat(x["trade_date"])
            d1 = cal.previous_trade_date(table, d)
            d2 = cal.previous_trade_date(table, d1)
            d3 = cal.previous_trade_date(table, d2)
            seen_ok = d3 is not None and d3 >= first
            drop_ok = d1 not in dropped and d2 not in dropped
            lines.append(f"  trip {d}: d-1 {d1} d-2 {d2} d-3 {d3}; d-3 >= window first {seen_ok}; d-1,d-2 not dropped {drop_ok}; "
                         f"open {ct(x['open_utc']).strftime('%H:%M')} close {ct(x['close_utc']).strftime('%H:%M')} {x['close_reason']} "
                         f"gross {x['gross_cents']} net {x['net_cents']} hold {x['hold_minutes']}")
            if not (seen_ok and drop_ok):
                problems.append(f"{m}: trip {d} violates N-9 or R-1b-2")
        # dates inside the window whose d-1 or d-2 is a dropped date
        affected = []
        for d in table:
            if not (w["first"] <= d.isoformat() <= w["last"]):
                continue
            d1 = cal.previous_trade_date(table, d)
            d2 = cal.previous_trade_date(table, d1) if d1 else None
            if d1 in dropped or d2 in dropped:
                affected.append((d.isoformat(), d.isoformat() in window))
        lines.append(f"  dates whose d-1 or d-2 is a dropped {root} date (date, in window): {affected}")
    if member_id == "K6-crushgap-01":
        lines.append(f"  legs in the record {legs}; roots with a position {dict(roots)}")
        if set(roots) - {"ZS"}:
            problems.append(f"{m}: a position on a signal leg {dict(roots)}")
    # halt and late-open dates
    for d in ("2025-11-28", "2025-12-24", "2025-12-26", "2026-01-02"):
        if d in per_day:
            lines.append(f"  trades on {d}: {per_day[d]} ({[ (ct(x['open_utc']).strftime('%H:%M'), ct(x['close_utc']).strftime('%H:%M'), x['close_reason']) for x in rows if x['trade_date']==d]})")
    return lines


def item6(rec: dict, trips: dict) -> str:
    m = rec["member"]
    root = rec["primary_vehicle"]
    counters = rec["engine"]["counters"]
    mll = counters.get("mll_liquidation", 0)
    acct = rec["engine"]["accounts_started"]
    if mll != acct - 1:
        problems.append(f"{m}: mll_liquidation {mll} != accounts_started - 1 = {acct - 1}")
    rows = trips["trips"]
    mll_trips = [x for x in rows if x["close_reason"] == "mll_liquidation"]
    if len(mll_trips) != mll:
        problems.append(f"{m}: {len(mll_trips)} MLL-closed trips != counter {mll}")
    tv = Fraction(str(product(root).tick_value_usd)) * 100
    n = rec["screen"]["n_days"]
    total = sum((cents(x["net_cents"]) for x in rows), Fraction(0))
    without = sum((cents(x["net_cents"]) for x in rows if x["close_reason"] != "mll_liquidation"), Fraction(0))
    mean_all = float(total / tv / n)
    mean_wo = float(without / tv / n)
    flag = ""
    if rec["screen"]["mean_ticks"] <= 0 < mean_wo:
        flag = "  <-- mean would turn positive without the MLL-closed trips (a bound: the day's other outcome is unknown)"
    return (f"{m:22s} mll={mll} accounts={acct} mean_all={mean_all:+.4f} mean_without_mll_trips={mean_wo:+.4f} "
            f"mll_trip_net_cents={[str(x['net_cents']) for x in mll_trips]}{flag}")


def main() -> None:
    data = load()
    print(f"records: {len(data)}")
    print("\n== item 1: screen recomputation (mean, population sd, t = mean / (sd / sqrt n)); dates; daily sums ==")
    for rec, trips in data:
        print(item1(rec, trips))
    # single positive day arithmetic
    n = 273
    print(f"\n== item 2: one positive day among {n - 1} zeros: t = sqrt(n/(n-1)) = {math.sqrt(n / (n - 1)):.10f}; "
          f"runner's HE t = 1.0018365488382999")
    cluster = json.loads((OUT / "K6_research_cluster.json").read_text())
    tiers = {m["member_id"]: m for m in cluster["tiers"]["members"]}
    for rec, _ in data:
        scr = rec["screen"]
        cov_ok = all(c["passes"] for c in rec["coverage"].values())
        expected = "excluded" if (not cov_ok or rec["labels"]) else ("A" if scr["passes"] else "B")
        got = tiers[rec["member"]]["tier"]
        if expected != got or tiers[rec["member"]]["labels"] != rec["labels"]:
            problems.append(f"{rec['member']}: tier {got} != expected {expected}")
    print(f"tiers: {Counter(t['tier'] for t in tiers.values())}; members tiered {len(tiers)}; not_tiered {cluster['not_tiered']}; "
          f"refused {cluster['refused_members']}; power_check_undefined {cluster['power_check_undefined']}; "
          f"tier mismatches: {[p for p in problems if 'tier' in p] or 'none'}")
    print("\n== item 4: trade counts and fill minutes ==")
    for rec, trips in data:
        print(rec["member"])
        for ln in item4(rec, trips):
            print(ln)
    print("\n== item 5: program N ==")
    freeze = json.loads(Path("reports/stage_e_k6_member_freeze.json").read_text())
    declared = {d["label"] for d in freeze["members"]}
    recorded = {rec["member"] for rec, _ in data}
    screened = [rec["member"] for rec, _ in data if rec["status"] == "run" and rec["screen"] is not None]
    statuses = Counter(rec["status"] for rec, _ in data)
    print(f"statuses {dict(statuses)}; screened {len(screened)}; declared {len(declared)}; recorded == declared: {recorded == declared}; "
          f"undeclared records {sorted(recorded - declared)}; declared without record {sorted(declared - recorded)}; N = 167 + {len(screened)} = {167 + len(screened)}")
    if recorded != declared:
        problems.append("records do not match the declarations")
    print("\n== item 6: MLL liquidations ==")
    for rec, trips in data:
        print(item6(rec, trips))
    print("\nNOTES:", *notes, sep="\n  ")
    print("PROBLEMS:", problems if problems else "none")


if __name__ == "__main__":
    main()
