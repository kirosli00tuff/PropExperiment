"""Stage E.6 Task 6 (MemberAuditor-K7-FableXHigh, Part 2): independent recomputation of the K7
research-window screen from the runner's recorded outputs and the frozen tables. No bar file is
read, nothing is replayed. Prints counts, comparisons and every difference.

Run: PYTHONPYCACHEPREFIX=<scratch> PYTHONPATH=. nice -n 10 uv run python \
    reports/stage_e6_briefs/audit_k7/recompute_screen.py
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

from data.group_session import load_group_calendar
from strategy.members.k7 import _calendar as CAL
from strategy.members.k7._event_common import ENTRY_DATES

CT = ZoneInfo("America/Chicago")
NS = 1_000_000_000
D = Path("reports/stage_e6_k7_screen")
MEMBERS = ("cp1", "cp2", "cp3", "expiry", "rev2h", "montrend")
COSTS = json.load(open("reports/stage_e2a_costs.json", encoding="utf-8"))["products"]["MBT"]
RELEASES = json.load(open("reports/stage_e2b_release_calendar.json", encoding="utf-8"))["releases"]
TICK_VALUE_CENTS = 50  # $0.50 per tick per contract (C7; costs table tick_value_usd 0.5)
COMMISSION_RT_CENTS = 282  # $2.82 round turn (F3)
EVENT_WINDOW_NS = 30 * 60 * NS  # D8: [release, release + 30 min)
Q_C = 1
SCREEN_T_MIN = 1.0
FREEZE_LABELS = ("K7-cp1-01 MBT", "K7-cp2-01 MBT", "K7-cp3-01 MBT", "K7-expiry-01 MBT",
                 "K7-rev2h-01 MBT", "K7-montrend-01 MBT")


def load(m: str):
    rf = D / f"K7_K7-{m}-01_MBT_research.json"
    tf = D / f"K7_K7-{m}-01_MBT_research_trips.json"
    return (json.load(open(rf, encoding="utf-8")), json.load(open(tf, encoding="utf-8")),
            hashlib.sha256(rf.read_bytes()).hexdigest())


def cents(v) -> Fraction:
    return Fraction(v) if isinstance(v, str) else Fraction(int(v))


def ct_of(ns: int) -> datetime:
    return datetime.fromtimestamp(ns // NS, tz=UTC).astimezone(CT)


# ------------------------------------------------------------------- item 1: the screen ----
def my_screen(values):
    n = len(values)
    mean = sum(values) / n
    sd = math.sqrt(sum((v - mean) ** 2 for v in values) / n)
    t = mean / (sd / math.sqrt(n)) if sd > 0 else None
    passes = mean > 0 and t is not None and t >= SCREEN_T_MIN
    return mean, sd, t, passes


def rel_close(a, b, tol=1e-9) -> bool:
    if a is None or b is None:
        return a is None and b is None
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


# ------------------------------------------------------------------ item 3: the costs ----
BUCKETS = [(b["start_min"], b["end_min"], b["side_ticks"], b["depth_ticks"]) for b in COSTS["buckets"]]
MAX_HALF = max(b["half_spread_ticks"] for b in COSTS["buckets"])
MBT_RELEASE_NS = sorted(int(datetime.fromisoformat(r["instant_utc"].replace("Z", "+00:00")).timestamp()) * NS
                        for r in RELEASES if "MBT" in r["products"])


def in_event_window(ts_ns: int) -> bool:
    # the latest release at or before ts, D8's half-open 30-minute window
    import bisect
    i = bisect.bisect_right(MBT_RELEASE_NS, ts_ns) - 1
    return i >= 0 and ts_ns < MBT_RELEASE_NS[i] + EVENT_WINDOW_NS


def side_slip_ticks(ts_ns: int, side: str) -> float:
    local = ct_of(ts_ns)
    minute = local.hour * 60 + local.minute
    found = [b for b in BUCKETS if b[0] <= minute < b[1]]
    assert len(found) == 1, (local, minute)
    _, _, side_ticks, depth = found[0]
    if in_event_window(ts_ns):
        return MAX_HALF + depth[side]
    return side_ticks[side]


def slip_cents(slip_ticks: float) -> int:
    """D8 as the frozen harness rounds it: ceil to the cent after stripping float noise."""
    return math.ceil(round(Q_C * slip_ticks * TICK_VALUE_CENTS, 6))


def rebuild(trips: list[dict]):
    """Per trip: net = gross - commission - slippage(entry side) - slippage(exit side); a trip's
    side is not recorded, so both candidates (long, short) are tried; MBT's table is symmetric."""
    rows = []
    for t in trips:
        gross = cents(t["gross_cents"])
        cands = {}
        for name, (s_in, s_out) in {"long": ("buy", "sell"), "short": ("sell", "buy")}.items():
            slip = slip_cents(side_slip_ticks(t["open_ts_ns"], s_in)) + slip_cents(
                side_slip_ticks(t["close_ts_ns"], s_out))
            cands[name] = gross - COMMISSION_RT_CENTS * t["contracts"] - slip * t["contracts"]
        rows.append((t, cands))
    return rows


# ---------------------------------------------------------------------------- main ----
def main() -> None:
    cal = load_group_calendar("crypto")
    cluster = json.load(open(D / "K7_research_cluster.json", encoding="utf-8"))
    tiers = {m["member_id"]: m for m in cluster["tiers"]["members"]}
    print("== ITEM 1: screen recomputation and series shape")
    all_trade = [d for d in (date(2025, 4, 1) + timedelta(days=i) for i in range(500))
                 if d <= date(2026, 6, 19) and cal.is_trade_date(d)]
    records = {}
    for m in MEMBERS:
        rec, trips, sha = load(m)
        records[m] = (rec, trips, sha)
        vals = rec["series"]["values"]
        dates = [date.fromisoformat(d) for d in rec["series"]["dates"]]
        mean, sd, t, passes = my_screen(vals)
        s = rec["screen"]
        ok = (rel_close(mean, s["mean_ticks"]) and rel_close(sd, s["sd_pop_ticks"])
              and rel_close(t, s["t_daily"]) and passes == s["passes"] and s["n_days"] == len(vals)
              and s["n_trips"] == rec["series"]["n_trips"] == trips["n_trips"] == len(trips["trips"]))
        ex = rec["window_dates"]["excluded"]
        excluded = {date.fromisoformat(d) for v in ex.values() for d in v}
        first, last = date.fromisoformat(rec["window_dates"]["first"]), date.fromisoformat(rec["window_dates"]["last"])
        expected_dates = [d for d in all_trade if first <= d <= last and d not in excluded]
        # also: no trade date of the research window beyond `last` except the excluded ones
        beyond = [d for d in all_trade if d > last and d not in excluded]
        nonzero = sum(1 for v in vals if v != 0)
        by_day = defaultdict(Fraction)
        for tr in trips["trips"]:
            by_day[date.fromisoformat(tr["trade_date"])] += cents(tr["net_cents"])
        day_ok = all(rel_close(v, float(by_day.get(d, 0)) / (Q_C * TICK_VALUE_CENTS)) for d, v in zip(dates, vals))
        usd_ok = all(rel_close(u, float(by_day.get(d, 0)) / 100) for d, u in zip(dates, rec["daily_net_usd"]))
        trips_on_window = all(date.fromisoformat(tr["trade_date"]) in set(dates) for tr in trips["trips"])
        print(f"{rec['member']}: n={len(vals)} mean={mean:.9f} sd={sd:.9f} t={t if t is None else round(t, 9)} passes={passes} "
              f"| record equal(1e-9)={ok} | dates==trade dates less exclusions={dates == expected_dates} "
              f"(beyond last: {beyond}) | nonzero days {nonzero} <= trips {len(trips['trips'])} | "
              f"values==sum(trip net)/50 per day: {day_ok} | daily_net_usd==sum/100: {usd_ok} | "
              f"trip dates in window: {trips_on_window} | record_sha256 in trips == file: {trips['record_sha256'] == sha} "
              f"| status={rec['status']} labels={rec['labels']}")
        assert rec["series"]["unit"] == "net ticks per contract per day"

    print("== ITEM 2: tiers")
    for m in MEMBERS:
        rec, _, _ = records[m]
        cov = rec["coverage"]["MBT"]
        cov_pass = cov["ratio"] >= 0.95
        my_tier = ("excluded" if (rec["labels"] or not cov_pass) else ("A" if rec["screen"]["passes"] else "B"))
        got = tiers[rec["member"]]
        print(f"{rec['member']}: coverage {cov['present']}/{cov['expected']}={cov['ratio']:.6f} passes={cov['passes']} (>=0.95: {cov_pass}) "
              f"labels={rec['labels']} -> my tier {my_tier}; cluster file tier {got['tier']} note '{got['note']}' "
              f"screen equal to record: {got['screen'] == rec['screen']} | agree={my_tier == got['tier']}")
    print("not_tiered:", cluster["not_tiered"], "refused:", cluster["refused_members"],
          "power_check_undefined:", cluster["power_check_undefined"], "members:", cluster["members"] == list(FREEZE_LABELS))

    print("== ITEM 3: cost rebuild from the trip lists (cp2 and montrend)")
    for m in ("cp2", "montrend"):
        rec, trips, _ = records[m]
        rows = rebuild(trips["trips"])
        exact, ambiguous, mism = 0, 0, []
        event_fills = 0
        for t, c in rows:
            net = cents(t["net_cents"])
            hits = [k for k, v in c.items() if v == net]
            if hits:
                exact += 1
                if len(hits) == 2:
                    ambiguous += 1
            else:
                mism.append((t["trade_date"], ct_of(t["open_ts_ns"]).strftime("%H:%M"), ct_of(t["close_ts_ns"]).strftime("%H:%M"), str(net), {k: str(v) for k, v in c.items()}))
            event_fills += in_event_window(t["open_ts_ns"]) + in_event_window(t["close_ts_ns"])
        by_day = defaultdict(Fraction)
        for t, c in rows:
            by_day[date.fromisoformat(t["trade_date"])] += c["long"]  # symmetric table: long == short
        dates = [date.fromisoformat(d) for d in rec["series"]["dates"]]
        ser_ok = all(rel_close(v, float(by_day.get(d, 0)) / (Q_C * TICK_VALUE_CENTS)) for d, v in zip(dates, rec["series"]["values"]))
        usd_ok = all(rel_close(u, float(by_day.get(d, 0)) / 100) for d, u in zip(dates, rec["daily_net_usd"]))
        reasons = Counter(t["close_reason"] for t in trips["trips"])
        print(f"{rec['member']}: trips {len(rows)}, net exact matches {exact} (side-ambiguous {ambiguous}: MBT's per-side slippage is symmetric), "
              f"mismatches {len(mism)}; fills inside a D8 event window: {event_fills}; rebuilt series == record: {ser_ok}; "
              f"daily_net_usd == rebuilt: {usd_ok}; close reasons {dict(reasons)}; locked {sum(t['locked'] for t in trips['trips'])}")
        for x in mism[:10]:
            print("   MISMATCH", x)
        # which event windows were met
        met = Counter()
        for t, _ in rows:
            for ts in (t["open_ts_ns"], t["close_ts_ns"]):
                if in_event_window(ts):
                    met[ct_of(ts).strftime("%H:%M")] += 1
        print("   event-window fill minutes (CT):", dict(met))
    print("   gross_cents cannot be checked without prices (no bar file is read): not checked.")

    print("== ITEM 4: trade counts and fill minutes")
    research_mbtx = [(d, t) for d, t in CAL.MBTX if "2025-04-01" <= d <= "2026-06-19"]
    rec, trips, _ = records["expiry"]
    blackout = set(rec["window_dates"]["excluded"]["roll_blackout_any_leg"])
    ur1 = set(rec["window_dates"]["excluded"]["unseen_roll_UR-1"])
    print(f"expiry: trips {len(trips['trips'])}; counters {rec['engine']['counters']}")
    n_elig = 0
    for d, texp in research_mbtx + [("2025-12-24", "10:00 (dropped R-1b-1)"), ("2025-12-26", "10:00 (CME date, not added)")]:
        dd = date.fromisoformat(d)
        why = []
        if d not in dict(CAL.MBTX):
            why.append("not in MBTX")
        if d not in CAL.CRYPTO_FULL_SESSIONS:
            why.append(f"not a full session (halt {cal.early_halt_ct(dd)})")
        if d in CAL.VENDOR_DEGRADED:
            why.append("vendor-degraded")
        if d in blackout:
            why.append("roll blackout (not a window date -> engine_not_a_window_date on any intent)")
        if d in ur1:
            why.append("UR-1")
        eligible = dd in ENTRY_DATES and d in dict(CAL.MBTX)
        n_elig += eligible
        print(f"   {d} T_exp {texp}: member-eligible={eligible}; {'; '.join(why) or 'TRADABLE (unexplained)'}")
    print(f"   member-eligible research dates: {n_elig}; all in the roll blackout: {all(d in blackout for d, _ in research_mbtx if date.fromisoformat(d) in ENTRY_DATES)}; "
          f"intents refused by name: {rec['engine']['counters'].get('engine_not_a_window_date', 0)} -> on the other "
          f"{n_elig - rec['engine']['counters'].get('engine_not_a_window_date', 0)} eligible dates no intent was emitted, "
          f"which under the audited code (expiry.py:102-104) means the bar at T_exp - 301 min was absent; the record does not name them.")

    for m in MEMBERS:
        rec, trips, _ = records[m]
        window = set(date.fromisoformat(d) for d in rec["series"]["dates"])
        per_day = Counter(t["trade_date"] for t in trips["trips"])
        entry_min = Counter(ct_of(t["open_ts_ns"]).strftime("%H:%M") for t in trips["trips"])
        exit_min = Counter(ct_of(t["close_ts_ns"]).strftime("%H:%M") for t in trips["trips"])
        reasons = Counter(t["close_reason"] for t in trips["trips"])
        days_traded = len(per_day)
        line = f"{rec['member']}: trips {len(trips['trips'])} on {days_traded} dates, max/day {max(per_day.values()) if per_day else 0}; close reasons {dict(reasons)}"
        if m == "montrend":
            elig = sorted(d for d in window if d.weekday() == 0 and d in ENTRY_DATES)
            bad_dates = sorted(set(per_day) - {d.isoformat() for d in elig})
            line += f"; eligible window Mondays {len(elig)}, traded {days_traded}, trips on non-eligible dates {bad_dates}"
            untraded = [d.isoformat() for d in elig if d.isoformat() not in per_day]
            line += f"; eligible Mondays without a trip {untraded}"
            odd_entry = {k: v for k, v in entry_min.items() if not k.endswith(":01")}
            odd_exit = {k: v for k, v in exit_min.items() if not (k.endswith(":00"))}
            line += f"; entry minutes not hh:01 {odd_entry}; exit minutes not hh:00 {odd_exit}; max entries/day {max(per_day.values())} <= 20"
        elif m == "rev2h":
            elig = sorted(d for d in window if d in ENTRY_DATES)
            bad_dates = sorted(set(per_day) - {d.isoformat() for d in elig})
            line += f"; eligible window dates {len(elig)}, traded {days_traded}, trips on non-eligible dates {bad_dates}; max/day <= 2: {max(per_day.values()) <= 2}"
            odd_entry = {k: v for k, v in entry_min.items() if k not in ('10:31', '12:31')}
            odd_exit = {k: v for k, v in exit_min.items() if k not in ('12:30', '14:30')}
            line += f"; entry minutes not 10:31/12:31 {odd_entry}; exit minutes not 12:30/14:30 {odd_exit}"
            odd = [(t['trade_date'], ct_of(t['open_ts_ns']).strftime('%H:%M'), ct_of(t['close_ts_ns']).strftime('%H:%M'), t['close_reason'], t['hold_minutes']) for t in trips['trips'] if ct_of(t['open_ts_ns']).strftime('%H:%M') not in ('10:31', '12:31') or ct_of(t['close_ts_ns']).strftime('%H:%M') not in ('12:30', '14:30')]
            line += f"; deviating trips {odd}"
        elif m == "cp1":
            line += f"; entry minutes {dict(entry_min)}; exit minutes {dict(exit_min)}"
        elif m == "cp3":
            line += f"; entry minutes {dict(entry_min)}; exit minutes {dict(exit_min)}"
        elif m == "cp2":
            e_first, e_last = min(entry_min), max(entry_min)
            holds = Counter(t["hold_minutes"] for t in trips["trips"])
            non75 = {k: v for k, v in holds.items() if k != 75.0}
            forced = [(t['trade_date'], ct_of(t['open_ts_ns']).strftime('%H:%M'), ct_of(t['close_ts_ns']).strftime('%H:%M'), t['close_reason'], t['hold_minutes']) for t in trips['trips'] if t['close_reason'] != 'strategy']
            line += f"; entry minutes in [{e_first}, {e_last}] (rule [08:46, 15:00]); holds != 75 min: {non75}; non-strategy closes {forced}"
            late = [(t['trade_date'], ct_of(t['open_ts_ns']).strftime('%H:%M'), ct_of(t['close_ts_ns']).strftime('%H:%M'), t['hold_minutes']) for t in trips['trips'] if t['close_reason'] == 'strategy' and t['hold_minutes'] != 75.0]
            line += f"; strategy closes with hold != 75 (missing bars inside the hold or a deferred fill) {late[:12]}"
        print("  ", line)
        # every trip's trade date is a window date; contracts == q_c
        print(f"      all trip dates in window: {all(date.fromisoformat(t['trade_date']) in window for t in trips['trips'])}; contracts all {Q_C}: {all(t['contracts'] == Q_C for t in trips['trips'])}; locked trips {sum(t['locked'] for t in trips['trips'])}")

    print("== ITEM 5: program N")
    screened = [records[m][0]["member"] for m in MEMBERS if records[m][0]["status"] == "run" and records[m][0]["screen"] is not None]
    files = sorted(p.name for p in D.iterdir())
    print(f"records with status run and a screen: {len(screened)} {screened}; refused {cluster['refused_members']}; excluded before screening: "
          f"{[records[m][0]['member'] for m in MEMBERS if records[m][0]['status'] != 'run']}; "
          f"every record's member declared in the freeze: {set(screened) == set(FREEZE_LABELS)}; files {len(files)}; N = 150 + {len(screened)} = {150 + len(screened)}")

    print("== ITEM 6: MLL liquidations")
    for m in MEMBERS:
        rec, trips, _ = records[m]
        n_mll = rec["engine"]["accounts_started"] - 1
        c_mll = rec["engine"]["counters"].get("mll_liquidation", 0)
        liq = [t for t in trips["trips"] if t["close_reason"] == "mll_liquidation"]
        vals = list(rec["series"]["values"])
        dates = rec["series"]["dates"]
        liq_days = {t["trade_date"] for t in liq}
        zeroed = [0.0 if d in liq_days else v for d, v in zip(dates, vals)]
        mean0, sd0, t0, pass0 = my_screen(zeroed)
        # bound: even crediting every liquidation day with zero, does the screen pass?
        print(f"{rec['member']}: accounts_started-1 = {n_mll}, counter {c_mll}, liquidation-closed trips {len(liq)} on {sorted(liq_days)} "
              f"net {[str(cents(t['net_cents'])) for t in liq]} cents; screen with those days set to 0: mean {mean0:.4f} t {None if t0 is None else round(t0, 4)} passes {pass0}")


if __name__ == "__main__":
    main()
