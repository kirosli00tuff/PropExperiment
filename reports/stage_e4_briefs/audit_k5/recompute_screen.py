"""MemberAuditor-K5 (Task 6): recompute K5's research-window screen figures from the runner's recorded
outputs and the frozen tables, in code independent of screening/stage_e_stats.py and the engine.
No bar file is opened; no member or runner is run. Prints counts and differences only.

Frozen definitions computed against:
- series value on a window date = sum over that date's trips of net_cents / contracts / tick value
  cents (runner docstring item 5, one traded leg); zeros on dates without a trip;
- mean = arithmetic mean; sd = population sd (ddof 0); t = mean / (sd / sqrt(n));
  passes = mean > 0 and t >= 1.0 (D5 lines 305-306);
- trip net = gross - commission (round turn per contract) - slippage(open side) - slippage(close side),
  slippage per side = ceil(round(contracts x ticks x tick value cents, 6)) with ticks = the fill bucket's
  side_ticks, or, inside [release, release + 30 min) of a release concerning the product, the product's
  largest half spread + the bucket's depth term (screening/stage_e_frozen.py, stage_e_rules.py);
- tiers: coverage label -> excluded (screen None); any other D9 label -> excluded with its screen;
  otherwise A iff passes, else B (ruling OC-H; stage_e_stats._tier_one).
"""
from __future__ import annotations

import hashlib
import json
import math
import statistics
from collections import Counter, defaultdict
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from data.group_session import load_group_calendar, trade_dates_between
from strategy.members.k5._calendar import METALS_FULL_SESSIONS
from strategy.members.k5._releases import FOMC_STATEMENT_DATES, GOLD_AM_AUCTIONS, GOLD_PM_AUCTIONS

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "reports/stage_e4b_k5_screen"
CT = ZoneInfo("America/Chicago")
NS = 1_000_000_000
WIN0, WIN1 = date(2025, 4, 1), date(2026, 6, 19)
EVENT_NS = 30 * 60 * NS
GUARD_NS = 2 * 60 * NS
TICK_VALUE_CENTS = {"MGC": 100, "MHG": 125}
COMMISSION_RT_CENTS = {"MGC": 192, "MHG": 192}
Q_C = {"MGC": 1, "MHG": 2}
DAY_SESSION = {"MGC": ("07:20", "12:30"), "MHG": ("07:10", "12:00")}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def hm(text: str) -> int:
    h, m = text.split(":")
    return int(h) * 60 + int(m)


def ct_of(ns: int) -> datetime:
    return datetime.fromtimestamp(ns / NS, tz=UTC).astimezone(CT)


def ct_hm(ns: int) -> str:
    return f"{ct_of(ns):%H:%M}"


def ct_minute(ns: int) -> int:
    c = ct_of(ns)
    return c.hour * 60 + c.minute


# ------------------------------------------------------------------ frozen inputs ----
def cost_table() -> dict:
    j = json.loads((REPO / "reports/stage_e2a_costs.json").read_text())
    out = {}
    for root in ("MGC", "MHG"):
        e = j["products"][root]
        assert e["calibrated"], root
        assert round(float(e["commission_rt_usd"]) * 100) == COMMISSION_RT_CENTS[root], e["commission_rt_usd"]
        assert round(float(e["tick_value_usd"]) * 100) == TICK_VALUE_CENTS[root]
        buckets = []
        for b in e["buckets"]:
            assert not b.get("fallback"), (root, b["key"])
            buckets.append((int(b["start_min"]), int(b["end_min"]), float(b["half_spread_ticks"]),
                            {s: float(b["depth_ticks"][s]) for s in ("buy", "sell")},
                            {s: float(b["side_ticks"][s]) for s in ("buy", "sell")}))
        out[root] = {"buckets": buckets, "max_half": max(b[2] for b in buckets)}
    return out


def release_instants() -> dict[str, list[int]]:
    j = json.loads((REPO / "reports/stage_e2b_release_calendar.json").read_text())
    import ast
    by_root: dict[str, list[int]] = defaultdict(list)
    for r in j["releases"]:
        ps = r["products"]
        if isinstance(ps, str):
            ps = ast.literal_eval(ps)
        inst = int(datetime.fromisoformat(r["instant_utc"].replace("Z", "+00:00")).timestamp()) * NS
        for p in ps:
            by_root[p].append(inst)
    return {k: sorted(v) for k, v in by_root.items()}


def latest_release_before(rel: list[int], ts: int) -> int | None:
    import bisect
    i = bisect.bisect_right(rel, ts) - 1
    return None if i < 0 else rel[i]


def in_event_window(rel: list[int], ts: int) -> bool:
    r = latest_release_before(rel, ts)
    return r is not None and ts < r + EVENT_NS


def in_fill_guard(rel: list[int], ts: int) -> bool:
    r = latest_release_before(rel, ts)
    return r is not None and ts < r + GUARD_NS


def side_ticks(costs: dict, root: str, ts: int, side: str, event: bool) -> float:
    minute = ct_minute(ts)
    found = [b for b in costs[root]["buckets"] if b[0] <= minute < b[1]]
    assert len(found) == 1, (root, minute)
    b = found[0]
    return costs[root]["max_half"] + b[3][side] if event else b[4][side]


def slippage_cents(qty: int, ticks: float, tick_value_cents: int) -> int:
    return math.ceil(round(qty * ticks * tick_value_cents, 6))


# ------------------------------------------------------------------ records ----
def load() -> tuple[list[dict], dict[str, dict], dict]:
    recs, trips = [], {}
    for p in sorted(OUT.glob("K5_K5-*_research.json")):
        r = json.loads(p.read_text())
        r["_path"] = p
        recs.append(r)
        tp = OUT / (p.name.replace("_research.json", "_research_trips.json"))
        t = json.loads(tp.read_text())
        t["_record_sha_ok"] = (t["record_sha256"] == sha(p)) and t["record_file"] == p.name
        trips[r["member"]] = t
    cluster = json.loads((OUT / "K5_research_cluster.json").read_text())
    return recs, trips, cluster


def main() -> None:
    recs, trips, cluster = load()
    freeze = json.loads((REPO / "reports/stage_e_k5_member_freeze.json").read_text())
    costs = cost_table()
    rel = release_instants()
    cal = load_group_calendar("metals")
    cal_dates = trade_dates_between(cal, WIN0, WIN1)
    print(f"records {len(recs)}, EC-CAL metals window trade dates {len(cal_dates)}")

    # ---- item 0: declarations vs records
    decl = {m["label"]: int(m["ordinal"]) for m in freeze["members"]}
    rec_ord = {r["member"]: r["ordinal"] for r in recs}
    print("item0 records == freeze declarations:", rec_ord == decl, "| cluster members == :",
          cluster["members"] == [m["label"] for m in freeze["members"]])
    ffiles = freeze["files"]
    bad = [f for f, v in ffiles.items() if sha(REPO / f) != v["sha256"]]
    print("item0 freeze file hashes == current files:", not bad, bad)

    # ---- item 1: screen from series.values
    print("\n== item 1: screen ==")
    tier_mine = {}
    for r in recs:
        m = r["member"]
        t = trips[m]
        if r["status"] != "run":
            print(f"{m}: status {r['status']}, screen {r['screen']}, series {r['series']}, trips {t['n_trips']}, sha ok {t['_record_sha_ok']}")
            continue
        vals = r["series"]["values"]
        dates = [date.fromisoformat(s) for s in r["series"]["dates"]]
        n = len(vals)
        mean = statistics.fmean(vals)
        sd = math.sqrt(sum((v - mean) ** 2 for v in vals) / n)
        tstat = mean / (sd / math.sqrt(n))
        passes = mean > 0 and tstat >= 1.0
        s = r["screen"]
        rel_err = max(abs(mean - s["mean_ticks"]) / max(abs(s["mean_ticks"]), 1e-300),
                      abs(sd - s["sd_pop_ticks"]) / abs(s["sd_pop_ticks"]),
                      abs(tstat - s["t_daily"]) / abs(s["t_daily"]))
        wd = r["window_dates"]
        excl = set()
        for v in wd["excluded"].values():
            excl |= {date.fromisoformat(x) for x in v}
        expect_dates = [d for d in cal_dates if d not in excl]
        tl = t["trips"]
        by_day: dict[str, list] = defaultdict(list)
        for x in tl:
            by_day[x["trade_date"]].append(x)
        nonzero = sum(1 for v in vals if v != 0.0)
        trip_dates_in = all(date.fromisoformat(k) in set(dates) for k in by_day)
        # rebuild values and daily_net_usd from trips
        tv = TICK_VALUE_CENTS[r["primary_vehicle"]]
        rebuilt = [sum(x["net_cents_float"] / x["contracts"] / tv for x in by_day.get(d.isoformat(), []))
                   for d in dates]
        rebuilt_usd = [sum(x["net_cents_float"] for x in by_day.get(d.isoformat(), [])) / 100 for d in dates]
        v_ok = max(abs(a - b) for a, b in zip(rebuilt, vals)) < 1e-9
        u_ok = max(abs(a - b) for a, b in zip(rebuilt_usd, r["daily_net_usd"])) < 1e-9
        ok = (rel_err < 1e-9 and passes == s["passes"] and n == s["n_days"] == wd["n"] == len(dates)
              == len(r["daily_net_usd"]) and dates == expect_dates and len(set(dates)) == n
              and nonzero <= t["n_trips"] == s["n_trips"] == r["series"]["n_trips"]
              == r["trade_rate"]["n_trips"] == len(tl) and trip_dates_in and v_ok and u_ok
              and t["_record_sha_ok"])
        tier_mine[m] = "A" if passes else "B"
        print(f"{m}: n {n} trips {len(tl)} mean {mean:+.6f} sd {sd:.6f} t {tstat:+.6f} passes {passes} "
              f"| rel err {rel_err:.1e} dates==EC-CAL-less-excl {dates == expect_dates} nonzero {nonzero} "
              f"values-from-trips {v_ok} usd {u_ok} sha {t['_record_sha_ok']} -> {'OK' if ok else 'MISMATCH'}")

    # ---- item 2: tiers
    print("\n== item 2: tiers ==")
    cl = {x["member_id"]: x for x in cluster["tiers"]["members"]}
    for r in recs:
        m = r["member"]
        labels = r["labels"]
        if "coverage_below_0.95" in labels:
            mine = "excluded"
        elif labels:
            mine = "excluded"
        else:
            mine = tier_mine[m]
        c = cl[m]
        same_screen = (c["screen"] == r["screen"])
        cov = r["coverage"][r["primary_vehicle"]]
        ratio_ok = abs(cov["ratio"] - cov["present"] / cov["expected"]) < 1e-12 and cov["passes"] == (cov["ratio"] >= 0.95)
        print(f"{m}: labels {labels} runner tier {c['tier']} mine {mine} {'OK' if mine == c['tier'] else 'MISMATCH'} "
              f"| screen same {same_screen} | coverage {cov['present']}/{cov['expected']}={cov['ratio']:.5f} arithmetic ok {ratio_ok}")
    print("not_tiered", cluster["not_tiered"], "refused", cluster["refused_members"], "power_undef", cluster["power_check_undefined"])

    # ---- item 3: trips rebuilt from the frozen cost table
    print("\n== item 3: trip nets from gross, commission and bucket slippage ==")
    for r in recs:
        if r["status"] != "run":
            continue
        m, root = r["member"], r["primary_vehicle"]
        tv, rt = TICK_VALUE_CENTS[root], COMMISSION_RT_CENTS[root]
        n_ok = n_amb = n_bad = n_event = 0
        bad_list = []
        for x in trips[m]["trips"]:
            q = x["contracts"]
            gross = x["gross_cents_float"]
            matches = []
            for oside, cside in (("buy", "sell"), ("sell", "buy")):
                ev_o = in_event_window(rel[root], x["open_ts_ns"])
                ev_c = in_event_window(rel[root], x["close_ts_ns"])
                so = slippage_cents(q, side_ticks(costs, root, x["open_ts_ns"], oside, ev_o), tv)
                sc = slippage_cents(q, side_ticks(costs, root, x["close_ts_ns"], cside, ev_c), tv)
                net = gross - rt * q - so - sc
                matches.append(abs(net - x["net_cents_float"]) < 1e-6)
            if in_event_window(rel[root], x["open_ts_ns"]) or in_event_window(rel[root], x["close_ts_ns"]):
                n_event += 1
            if all(matches):
                n_amb += 1
            elif any(matches):
                n_ok += 1
            else:
                n_bad += 1
                bad_list.append((x["trade_date"], ct_hm(x["open_ts_ns"]), ct_hm(x["close_ts_ns"]), x["close_reason"], x["net_cents_float"]))
        print(f"{m}: trips {n_ok + n_amb + n_bad}: side-determined match {n_ok}, both sides match {n_amb}, "
              f"no match {n_bad}, event-window fills (trips) {n_event}; contracts {Counter(x['contracts'] for x in trips[m]['trips'])}"
              + (f" BAD {bad_list[:5]}" if bad_list else ""))

    # ---- item 4: events, fill minutes, ovr limits
    print("\n== item 4: event reconciliation and fill minutes ==")
    am = {d: t for d, t in GOLD_AM_AUCTIONS if WIN0.isoformat() <= d <= WIN1.isoformat()}
    pm = {d: t for d, t in GOLD_PM_AUCTIONS if WIN0.isoformat() <= d <= WIN1.isoformat()}
    fomc = [d for d in FOMC_STATEMENT_DATES if WIN0.isoformat() <= d <= WIN1.isoformat()]
    halts = {d.isoformat() for d in cal_dates if cal.early_halt_ct(d) is not None}
    cal_set = {d.isoformat() for d in cal_dates}
    full = set(METALS_FULL_SESSIONS)
    for r in recs:
        if r["status"] != "run":
            continue
        m, root = r["member"], r["primary_vehicle"]
        tl = trips[m]["trips"]
        wd = r["window_dates"]
        blackout = set(wd["excluded"]["roll_blackout_any_leg"])
        ur1 = set(wd["excluded"]["unseen_roll_UR-1"])
        counters = r["engine"]["counters"]
        traded_dates = Counter(x["trade_date"] for x in tl)
        o, c = DAY_SESSION[root]

        def nominal(x: dict) -> tuple[str, str]:
            d = x["trade_date"]
            if m.startswith("K5-preauc"):
                t = hm(am[d]); return f"{(t-30)//60:02d}:{(t-30)%60:02d}", f"{(t-1)//60:02d}:{(t-1)%60:02d}"
            if m.startswith("K5-pmfix"):
                t = hm(pm[d]); return f"{(t+2)//60:02d}:{(t+2)%60:02d}", f"{(t+12)//60:02d}:{(t+12)%60:02d}"
            if m.startswith("K5-fomc"):
                return "13:05", "13:15"
            if m.startswith("K5-cp1"):
                return f"{hm(c)-30:02d}"[:0] + f"{(hm(c)-30)//60:02d}:{(hm(c)-30)%60:02d}", f"{(hm(c)-1)//60:02d}:{(hm(c)-1)%60:02d}"
            if m.startswith("K5-cp3"):
                return f"{(hm(o)+1)//60:02d}:{(hm(o)+1)%60:02d}", f"{(hm(c)-1)//60:02d}:{(hm(c)-1)%60:02d}"
            if m.startswith("K5-ovr"):
                om = ct_minute(x["open_ts_ns"])
                return f"{om//60:02d}:{om%60:02d}", f"{(om+59)//60:02d}:{(om+59)%60:02d}"
            return "", ""  # cp2: entry any eligible minute; exit 75 present bars after the fill

        classes: Counter = Counter()
        odd = []
        for x in tl:
            oc, cc = ct_hm(x["open_ts_ns"]), ct_hm(x["close_ts_ns"])
            no, nc = nominal(x)
            reason = x["close_reason"]
            entry_cls = "exact"
            if m.startswith("K5-cp2"):
                em = ct_minute(x["open_ts_ns"])
                entry_cls = "eligible" if hm(o) + 16 <= em <= hm(c) else "OUTSIDE"
                if hm(o) + 16 <= em <= hm(c) + 2 and in_fill_guard(rel[root], x["open_ts_ns"] - 2 * 60 * NS):
                    entry_cls = "d95a-deferred?"
            elif no != oc:
                # nominal fill instant one or two minutes earlier hit a guard?
                nom_ns = x["open_ts_ns"] - (ct_minute(x["open_ts_ns"]) - hm(no)) * 60 * NS
                entry_cls = "d95a" if (in_fill_guard(rel[root], nom_ns) and ct_minute(x["open_ts_ns"]) - hm(no) == 2) else f"late+{ct_minute(x['open_ts_ns']) - hm(no)}"
            if reason == "mll_liquidation":
                exit_cls = "mll"
            elif reason == "forced_flatten":
                exit_cls = "forced_flatten"
            elif reason != "strategy":
                exit_cls = reason
            elif m.startswith("K5-cp2"):
                h = x["hold_minutes"]
                exit_cls = "hold75" if h == 75 else (f"hold{h:g}")
            elif nc == cc:
                exit_cls = "exact"
            else:
                nom_ns = x["close_ts_ns"] - (ct_minute(x["close_ts_ns"]) - hm(nc)) * 60 * NS
                dlt = ct_minute(x["close_ts_ns"]) - hm(nc)
                exit_cls = "d95a" if (in_fill_guard(rel[root], nom_ns) and dlt == 2) else f"late+{dlt}"
            classes[(entry_cls, exit_cls)] += 1
            if entry_cls not in ("exact", "eligible") or exit_cls not in ("exact", "hold75"):
                odd.append((x["trade_date"], oc, cc, entry_cls, exit_cls, x["hold_minutes"]))
        print(f"\n{m}: trips {len(tl)}, dates traded {len(traded_dates)}, max trips/day {max(traded_dates.values())}, "
              f"counters {counters}, holds {sorted(Counter(x['hold_minutes'] for x in tl).items())[:8]}")
        print("   fill classes:", dict(classes))
        if odd:
            print("   deviations:", odd[:40])
        # event reconciliation
        if m.startswith("K5-preauc") or m.startswith("K5-pmfix") or m.startswith("K5-fomc"):
            events = set(am) if m.startswith("K5-preauc") else (set(pm) if m.startswith("K5-pmfix") else set(fomc))
            traded = set(traded_dates)
            outside = sorted(traded - events)
            un = sorted(events - traded)
            ex_halt = [d for d in un if d in halts]
            ex_black = [d for d in un if d in blackout and d not in halts]
            ex_ur1 = [d for d in un if d in ur1 and d not in halts and d not in blackout]
            ex_noncal = [d for d in un if d not in cal_set and d not in halts]
            rest = [d for d in un if d not in ex_halt and d not in ex_black and d not in ex_ur1 and d not in ex_noncal]
            print(f"   events in window {len(events)}, traded {len(traded)}, outside events {outside}, untraded {len(un)}: "
                  f"halts {len(ex_halt)} {ex_halt}, blackout {len(ex_black)}, UR-1 {len(ex_ur1)} {ex_ur1}, non-trade-date {ex_noncal}, "
                  f"unexplained (silent: missing bar or s=0) {len(rest)} {rest}")
            print(f"   blackout+UR-1 dates that are events: {len([d for d in (blackout | ur1) if d in events])}, "
                  f"engine_not_a_window_date {counters.get('engine_not_a_window_date', 0)}")
        if m.startswith("K5-ovr"):
            cap = 5 if root == "MGC" else 4
            per_day = Counter(x["trade_date"] for x in tl)
            overlaps = 0
            by_d = defaultdict(list)
            for x in tl:
                by_d[x["trade_date"]].append((x["open_ts_ns"], x["close_ts_ns"]))
            for d, iv in by_d.items():
                iv.sort()
                for (a1, b1), (a2, b2) in zip(iv, iv[1:]):
                    if a2 < b1:
                        overlaps += 1
            ents = Counter(ct_hm(x["open_ts_ns"]) for x in tl)
            print(f"   ovr: max entries/day {max(per_day.values())} (cap {cap}), overlaps {overlaps}, entry minutes {dict(ents)}, "
                  f"traded on early-halt date: {sorted(set(per_day) & halts)}, traded non-full-session: {sorted(set(per_day) - full)}")
        if m.startswith("K5-cp1") or m.startswith("K5-cp3"):
            print(f"   traded on early-halt dates: {sorted(set(traded_dates) & halts)}; blackout dates traded: {sorted(set(traded_dates) & blackout)}")
        if m.startswith("K5-cp2"):
            ents = Counter(ct_hm(x["open_ts_ns"]) for x in tl)
            print(f"   cp2: earliest entry {min(ents)}, latest {max(ents)}, on halts {sorted(set(traded_dates) & halts)}")

    # ---- item 5: N
    print("\n== item 5: N ==")
    screened = [r["member"] for r in recs if r["status"] == "run" and r["screen"] is not None]
    excluded_pre = [r["member"] for r in recs if r["screen"] is None]
    undeclared = [r["member"] for r in recs if r["member"] not in decl]
    print(f"screened (status run with a screen) {len(screened)}: {screened}")
    print(f"no screen {len(excluded_pre)}: {excluded_pre}; undeclared {undeclared}; refused {cluster['refused_members']}")
    print(f"N = 114 + {len(screened)} = {114 + len(screened)}")

    # ---- item 6: MLL liquidations and sensitivity
    print("\n== item 6: MLL ==")
    for r in recs:
        if r["status"] != "run":
            continue
        m = r["member"]
        tl = trips[m]["trips"]
        mll_trips = [x for x in tl if x["close_reason"] == "mll_liquidation"]
        cnt = r["engine"]["counters"].get("mll_liquidation", 0)
        acct = r["engine"]["accounts_started"] - 1
        vals = r["series"]["values"]
        dates = r["series"]["dates"]
        mll_days = {x["trade_date"] for x in mll_trips}

        def stats(v: list[float]) -> tuple[float, float, bool]:
            n = len(v); mu = statistics.fmean(v); sd = math.sqrt(sum((a - mu) ** 2 for a in v) / n)
            t = mu / (sd / math.sqrt(n)) if sd > 0 else float("nan")
            return mu, t, mu > 0 and t >= 1.0

        base = stats(vals)
        zero = stats([0.0 if d in mll_days else v for d, v in zip(dates, vals)])
        drop = stats([v for d, v in zip(dates, vals) if d not in mll_days])
        print(f"{m}: accounts-1 {acct} counter {cnt} trips {len(mll_trips)} {'OK' if acct == cnt == len(mll_trips) else 'MISMATCH'} "
              f"days {sorted(mll_days)} | base t {base[1]:+.4f} pass {base[2]} | zeroed t {zero[1]:+.4f} pass {zero[2]} | dropped t {drop[1]:+.4f} pass {drop[2]}")
    # Tier A sensitivity: fomc
    r = next(r for r in recs if r["member"] == "K5-fomc-01 MGC")
    vals, dates = r["series"]["values"], r["series"]["dates"]
    nz = sorted(((v, d) for v, d in zip(vals, dates) if v != 0.0), reverse=True)
    print("fomc trade days (ticks/contract):", [(d, round(v, 2)) for v, d in nz])
    best = nz[0][1]
    def st(v):
        n = len(v); mu = statistics.fmean(v); sd = math.sqrt(sum((a - mu) ** 2 for a in v) / n)
        return round(mu, 4), round(mu / (sd / math.sqrt(n)), 4)
    print("fomc base", st(vals), "| without best day (zeroed)", st([0.0 if d == best else v for v, d in zip(vals, dates)]),
          "| best day dropped", st([v for v, d in zip(vals, dates) if d != best]),
          "| worst day zeroed", st([0.0 if d == nz[-1][1] else v for v, d in zip(vals, dates)]))
    fomc_trips = trips["K5-fomc-01 MGC"]["trips"]
    print("fomc trips:", [(x["trade_date"], ct_hm(x["open_ts_ns"]), ct_hm(x["close_ts_ns"]), x["close_reason"], x["net_cents_float"]) for x in fomc_trips])


if __name__ == "__main__":
    main()
