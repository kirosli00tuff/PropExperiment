"""Task 3 audit: recompute every literal table of strategy/members/k4/_releases.py and _calendar.py
from its frozen sources, independently of reports/stage_e4_briefs/gen_k4_*.py, and print counts
and differences only. Read-only. Run: PYTHONPATH=. uv run python reports/stage_e4_briefs/audit/recompute_tables.py
"""
from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from data.group_session import load_group_calendar, trade_dates_between
from strategy.members.k4 import _calendar as cal_mod
from strategy.members.k4 import _releases as rel

CT = ZoneInfo("America/Chicago")
ET = ZoneInfo("America/New_York")
CAL_PATH = "reports/stage_e2b_release_calendar.json"
CHECK_PATH = "reports/stage_e4_release_check.json"


def sha(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def report(name: str, mine, theirs) -> None:
    mine_t, theirs_t = tuple(mine), tuple(theirs)
    same = mine_t == theirs_t
    print(f"{name}: recomputed {len(mine_t)} rows, module {len(theirs_t)} rows, "
          f"{'EQUAL' if same else 'DIFFERENT'}")
    if not same:
        ms, ts = set(mine_t), set(theirs_t)
        print("  only in recomputed:", sorted(ms - ts)[:20])
        print("  only in module:", sorted(ts - ms)[:20])
        if ms == ts:
            print("  same set, different order")


def main() -> None:
    print("sha256 calendar", sha(CAL_PATH), "== pinned", sha(CAL_PATH) == rel.RELEASE_CALENDAR_SHA256)
    print("sha256 check   ", sha(CHECK_PATH), "== pinned", sha(CHECK_PATH) == rel.RELEASE_CHECK_SHA256)
    with open(CAL_PATH) as fh:
        cal = json.load(fh)
    with open(CHECK_PATH) as fh:
        chk = json.load(fh)
    print("calendar coverage", cal["coverage"], "cancellations", len(cal["cancellations"]))
    canc = [c for c in cal["cancellations"] if c.get("release") in ("WPSR", "NGS", "API_WSB")]
    print("cancellations naming WPSR/NGS/API_WSB:", len(canc))

    rows = {k: [] for k in ("WPSR", "NGS", "API_WSB")}
    for r in cal["releases"]:
        if r["release"] in rows:
            rows[r["release"]].append(r)
    for k, v in rows.items():
        v.sort(key=lambda r: r["instant_utc"])
        dates = [r["date"] for r in v]
        print(f"calendar {k}: {len(v)} rows, {dates[0]}..{dates[-1]}, unique dates {len(set(dates))}, "
              f"evidence {sorted({r['evidence'] for r in v})}, tz {sorted({r['tz'] for r in v})}, "
              f"products {sorted({tuple(r['products']) for r in v})}")

    # --- instant -> CT and ET; consistency with time_local/tz -------------------------------
    def ct_time(r) -> str:
        inst = datetime.fromisoformat(r["instant_utc"].replace("Z", "+00:00"))
        return inst.astimezone(CT).strftime("%H:%M")

    def et_time(r) -> str:
        inst = datetime.fromisoformat(r["instant_utc"].replace("Z", "+00:00"))
        return inst.astimezone(ET).strftime("%H:%M")

    def ct_date_ok(r) -> bool:
        inst = datetime.fromisoformat(r["instant_utc"].replace("Z", "+00:00"))
        return inst.astimezone(CT).date().isoformat() == r["date"]

    bad_local = [(r["id"], r["time_local"], r["tz"], et_time(r)) for k in rows for r in rows[k]
                 if not (r["tz"] in ("America/New_York", "US/Eastern", "ET") and r["time_local"] == et_time(r))]
    print("rows whose time_local/tz disagree with instant_utc in ET:", len(bad_local), bad_local[:5])
    bad_date = [r["id"] for k in rows for r in rows[k] if not ct_date_ok(r)]
    print("rows whose CT date of instant != date:", bad_date)

    # --- research-window check rows one-for-one with the calendar --------------------------
    w0, w1 = chk["window"]
    print("check window", w0, w1, "module RESEARCH_CHECK_WINDOW", rel.RESEARCH_CHECK_WINDOW)
    for k, key in (("WPSR", "wpsr"), ("NGS", "ngs")):
        cal_win = [r for r in rows[k] if w0 <= r["date"] <= w1]
        chk_rows = chk[key]
        cal_pairs = [(r["date"], et_time(r)) for r in cal_win]
        chk_pairs = [(r["date"], r["time_et"]) for r in chk_rows]
        print(f"{k} research window: calendar {len(cal_win)} rows, check {len(chk_rows)} rows, "
              f"(date,time_et) pairs equal: {cal_pairs == chk_pairs}")
        verdicts = {}
        for r in chk_rows:
            verdicts.setdefault(r["verdict"], []).append(r["date"])
        print(f"  verdict counts: {{k: len(v) for k, v in verdicts.items()}}")
        for vk, vd in verdicts.items():
            if vk != "keep":
                print(f"  {vk}: {vd}")
        # check's own date/actual consistency for drops
        for r in chk_rows:
            if r["verdict"] != "keep":
                print(f"  {r['id']}: sched {r.get('schedule_date')} {r.get('schedule_time_et')} "
                      f"actual {r.get('actual_date')} {r.get('actual_time_et')} basis {r.get('time_basis')} "
                      f"updated_marker {r.get('updated_marker')} first_seen {r.get('earliest_capture_showing_update')}")

    # --- WPSR table ---------------------------------------------------------------------
    wpsr_drops = {d for d, _ in rel.DROPPED_WPSR}
    chk_wpsr_nonkeep = {r["date"] for r in chk["wpsr"] if r["verdict"] != "keep"}
    print("DROPPED_WPSR == check non-keep:", wpsr_drops == chk_wpsr_nonkeep, sorted(wpsr_drops), sorted(chk_wpsr_nonkeep))
    mine_wpsr = []
    for r in rows["WPSR"]:
        if r["date"] in wpsr_drops:
            continue
        d = date.fromisoformat(r["date"])
        standard = d.weekday() == 2 and et_time(r) == "10:30"
        mine_wpsr.append((r["date"], ct_time(r), d.weekday(), standard))
    report("WPSR", mine_wpsr, rel.WPSR)
    print("  WPSR standard count:", sum(1 for x in mine_wpsr if x[3]),
          "CT slots:", sorted({x[1] for x in mine_wpsr}),
          "weekday x slot:", sorted({(x[2], x[1]) for x in mine_wpsr}))
    win_wpsr = [x for x in mine_wpsr if w0 <= x[0] <= w1]
    print("  WPSR research window rows:", len(win_wpsr), "standard:", sum(1 for x in win_wpsr if x[3]))
    # rows with the standard flag but not Wednesday 10:30 by another route (time_local)
    mism = [(r["date"], r["time_local"], et_time(r)) for r in rows["WPSR"]
            if (date.fromisoformat(r["date"]).weekday() == 2 and r["time_local"] == "10:30")
            != (date.fromisoformat(r["date"]).weekday() == 2 and et_time(r) == "10:30")]
    print("  standard flag by time_local vs by instant differ on:", mism)

    # --- NGS table ----------------------------------------------------------------------
    ngs_drops = {d for d, _ in rel.DROPPED_NGS}
    chk_ngs_nonkeep = {r["date"]: r["verdict"] for r in chk["ngs"] if r["verdict"] != "keep"}
    print("check NGS non-keep:", chk_ngs_nonkeep)
    print("DROPPED_NGS:", sorted(ngs_drops), "NGS_UNVERIFIED_IN_WINDOW:", rel.NGS_UNVERIFIED_IN_WINDOW)
    print("  drops+unverified == non-keep:", ngs_drops | set(rel.NGS_UNVERIFIED_IN_WINDOW) == set(chk_ngs_nonkeep))
    mine_ngs = [(r["date"], ct_time(r)) for r in rows["NGS"] if r["date"] not in ngs_drops]
    report("NGS", mine_ngs, rel.NGS)
    print("  NGS CT slots:", sorted({x[1] for x in mine_ngs}),
          "weekday x slot:", sorted({(date.fromisoformat(x[0]).weekday(), x[1]) for x in mine_ngs}))
    print("  NGS research window rows:", sum(1 for x in mine_ngs if w0 <= x[0] <= w1))

    # --- API_DROPPED_WEEKS ----------------------------------------------------------------
    api = chk["api_weeks"]
    bad = [w["wpsr_date"] for w in api
           if w["monday_federal_holiday"] or w["api_row_date"] != w["tuesday"] or w["api_row_time_et"] != "16:30"]
    print("api_weeks:", len(api), "recomputed API_DROPPED_WEEKS:", bad, "module:", rel.API_DROPPED_WEEKS)
    # cross-check api_weeks against my standard rows in the window
    std_win = {x[0] for x in win_wpsr if x[3]} | ({"2025-07-16"} if "2025-07-16" in wpsr_drops else set())
    api_dates = {w["wpsr_date"] for w in api}
    print("  api_weeks wpsr dates == calendar standard Wednesdays in window (before drops):", api_dates == std_win,
          sorted(api_dates ^ std_win))
    print("  api_rows_not_on_tuesday:", [str(r)[:80] for r in chk["api_rows_not_on_tuesday"]][:10])
    # API_WSB calendar rows: which are not Tuesday 16:30 ET
    api_cal = rows["API_WSB"]
    off = [(r["date"], date.fromisoformat(r["date"]).strftime("%a"), et_time(r)) for r in api_cal
           if date.fromisoformat(r["date"]).weekday() != 1 or et_time(r) != "16:30"]
    print("  calendar API_WSB rows:", len(api_cal), "off Tuesday 16:30 ET:", len(off), off[:12])

    # --- FEDERAL_MONDAY_HOLIDAYS ----------------------------------------------------------
    fed = chk["federal_monday_holidays"]
    fed_dates = sorted({h["date"] for h in fed})
    not_monday = [h["date"] for h in fed if date.fromisoformat(h["date"]).weekday() != 0]
    print("federal_monday_holidays entries:", len(fed), "distinct:", len(fed_dates), "not Monday:", not_monday)
    report("FEDERAL_MONDAY_HOLIDAYS", fed_dates, rel.FEDERAL_MONDAY_HOLIDAYS)
    print("  window:", fed_dates[0], fed_dates[-1])

    # --- NYSE_NOT_FULL -------------------------------------------------------------------
    ny = chk["nyse"]
    full = [x["date"] for x in ny["full_closures"]]
    early = [x["date"] for x in ny["early_closes"]]
    print("nyse full", len(full), "early", len(early), "early close times", sorted({x["close_time_et"] for x in ny["early_closes"]}))
    both = sorted(set(full) | set(early))
    print("  overlap full/early:", sorted(set(full) & set(early)))
    report("NYSE_NOT_FULL", both, rel.NYSE_NOT_FULL)
    print("  window:", both[0], both[-1], "in research window:",
          sum(1 for d in full if w0 <= d <= w1), "closures,", sum(1 for d in early if w0 <= d <= w1), "early")

    # --- ENERGY_FULL_SESSIONS --------------------------------------------------------------
    ecal = load_group_calendar("energy")
    cov = getattr(ecal, "coverage", None)
    print("energy calendar coverage:", cov, "sha256 data/calendars/energy.py", sha("data/calendars/energy.py"),
          "== pinned", sha("data/calendars/energy.py") == cal_mod.ENERGY_FULL_SESSIONS_SOURCE_SHA256)
    d0, d1 = date(2019, 5, 1), date(2026, 6, 19)
    tds = list(trade_dates_between(ecal, d0, d1))
    mine_full = [d.isoformat() for d in tds if ecal.early_halt_ct(d) is None]
    halts = [d.isoformat() for d in tds if ecal.early_halt_ct(d) is not None]
    print("energy trade dates in range:", len(tds), "early halts:", len(halts))
    report("ENERGY_FULL_SESSIONS", mine_full, cal_mod.ENERGY_FULL_SESSIONS)
    print("  first/last:", mine_full[0], mine_full[-1], "sorted+unique:",
          mine_full == sorted(set(mine_full)))
    # independent re-derivation from is_trade_date over every calendar day
    alt = []
    d = d0
    while d <= d1:
        if ecal.is_trade_date(d) and ecal.early_halt_ct(d) is None:
            alt.append(d.isoformat())
        d += timedelta(days=1)
    print("  is_trade_date walk equals trade_dates_between:", alt == mine_full)
    win_halts = [h for h in halts if w0 <= h <= w1]
    print("  research-window early halts:", win_halts)

    # --- cross-checks the members rely on ----------------------------------------------------
    full_set = set(mine_full)
    wpsr_not_td = [x[0] for x in mine_wpsr if not ecal.is_trade_date(date.fromisoformat(x[0]))]
    wpsr_halt = [x[0] for x in mine_wpsr if ecal.early_halt_ct(date.fromisoformat(x[0])) is not None]
    ngs_not_td = [x[0] for x in mine_ngs if not ecal.is_trade_date(date.fromisoformat(x[0]))]
    ngs_halt = [x[0] for x in mine_ngs if ecal.early_halt_ct(date.fromisoformat(x[0])) is not None]
    print("WPSR rows not energy trade dates:", wpsr_not_td, "on early halts:", wpsr_halt)
    print("NGS rows not energy trade dates:", ngs_not_td, "on early halts:", ngs_halt)
    # eiafade filter: rows with T_W + 15 > 13:13
    late = [(x[0], x[1]) for x in mine_wpsr if int(x[1][:2]) * 60 + int(x[1][3:]) + 15 > 13 * 60 + 13]
    print("WPSR rows failing eiafade's T_W+15 <= 13:13 (after drops):", late)
    # apipre event set
    fed_set = set(fed_dates)
    apipre = [x[0] for x in mine_wpsr if x[3]
              and (date.fromisoformat(x[0]) - timedelta(days=1)).isoformat() in full_set
              and (date.fromisoformat(x[0]) - timedelta(days=2)).isoformat() not in fed_set
              and x[0] not in rel.API_DROPPED_WEEKS]
    excl_tue = [x[0] for x in mine_wpsr if x[3]
                and (date.fromisoformat(x[0]) - timedelta(days=1)).isoformat() not in full_set]
    excl_mon = [x[0] for x in mine_wpsr if x[3]
                and (date.fromisoformat(x[0]) - timedelta(days=2)).isoformat() in fed_set]
    print("apipre events:", len(apipre), "research window:", sum(1 for d in apipre if w0 <= d <= w1),
          "standard rows excluded by Tuesday not full:", excl_tue, "by holiday Monday:", excl_mon)
    # eiamom event set
    ny_set = set(both)
    eiamom = [x[0] for x in mine_wpsr if x[3] and x[0] not in ny_set]
    print("eiamom events:", len(eiamom), "research window:", sum(1 for d in eiamom if w0 <= d <= w1),
          "standard rows in NYSE_NOT_FULL:", [x[0] for x in mine_wpsr if x[3] and x[0] in ny_set])
    # ngpre: research-window rows and the Wednesday 11:00 CT ones
    print("ngpre research rows:", sum(1 for x in mine_ngs if w0 <= x[0] <= w1),
          "11:00 CT rows in window:", [x for x in mine_ngs if w0 <= x[0] <= w1 and x[1] == "11:00"],
          "Friday rows in window:", [x for x in mine_ngs if w0 <= x[0] <= w1 and date.fromisoformat(x[0]).weekday() == 4])
    # WPSR shared instants with NG products on Wednesday 12:00 ET NGS days (coder B note 1)
    wed_ngs = [x[0] for x in mine_ngs if date.fromisoformat(x[0]).weekday() == 2]
    for d in wed_ngs:
        w = [r for r in rows["WPSR"] if r["date"] == d]
        print("  Wed NGS", d, "WPSR same day:", [(ct_time(r), r["products"]) for r in w])
    # updated markers in the check
    print("updated_markers:", {k: list(v.keys()) for k, v in chk["updated_markers"].items()})


if __name__ == "__main__":
    main()
