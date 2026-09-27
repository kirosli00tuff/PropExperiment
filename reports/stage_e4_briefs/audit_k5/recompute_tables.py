"""MemberAuditor-K5 (Task 3, item 5): recompute K5's literal tables from their sources, independently
of reports/stage_e4_briefs/gen_k5_*.py, and diff them against strategy/members/k5/_releases.py and
_calendar.py. Read-only. Prints counts and differences only.

Sources read: data/vendor/release_pages/e4b/govuk_bank-holidays.json (the saved gov.uk file),
reports/stage_e4b_release_check.json (no-auction rows only), reports/stage_e2b_release_calendar.json
(FOMC rows), strategy/members/k2/_releases.py (as text, ast), data.group_session (EC-CAL metals).
"""
from __future__ import annotations

import ast
import hashlib
import json
from collections import Counter
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from data.group_session import load_group_calendar, sha256_file, trade_dates_between
from strategy.members.k5 import _calendar as cal_mod
from strategy.members.k5 import _releases as rel

REPO = Path(__file__).resolve().parents[3]
LONDON, CHICAGO = ZoneInfo("Europe/London"), ZoneInfo("America/Chicago")
FIRST, LAST = date(2019, 5, 1), date(2026, 6, 19)
WIN0, WIN1 = date(2025, 4, 1), date(2026, 6, 19)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def t_ct(day: date, hh: int, mm: int) -> str:
    inst = datetime.combine(day, time(hh, mm), tzinfo=LONDON).astimezone(CHICAGO)
    assert inst.date() == day, (day, inst)
    return f"{inst:%H:%M}"


def weekdays(first: date, last: date) -> list[date]:
    out, d = [], first
    while d <= last:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


def main() -> None:
    # ---- sources and hashes ----
    check_p = REPO / "reports/stage_e4b_release_check.json"
    calj_p = REPO / "reports/stage_e2b_release_calendar.json"
    govuk_p = REPO / "data/vendor/release_pages/e4b/govuk_bank-holidays.json"
    print("check sha ok:", sha(check_p) == rel.RELEASE_CHECK_SHA256)
    print("calendar sha ok:", sha(calj_p) == rel.RELEASE_CALENDAR_SHA256)
    check = json.loads(check_p.read_text())
    govuk = json.loads(govuk_p.read_text())
    manifest = [json.loads(l) for l in (REPO / "data/vendor/release_pages/e4b/manifest.jsonl")
                .read_text().splitlines() if l.strip()]
    m_gov = [m for m in manifest if m["file"] == "govuk_bank-holidays.json"][0]
    print("govuk saved file sha matches manifest:", sha(govuk_p) == m_gov["sha256"])

    # ---- EC-UKBH from the saved gov.uk file (England and Wales) ----
    ew = govuk["england-and-wales"]["events"]
    bh_all = sorted(date.fromisoformat(e["date"]) for e in ew)
    print("govuk E&W span:", bh_all[0], bh_all[-1], "n", len(bh_all))
    bh = sorted(d for d in bh_all if FIRST <= d <= LAST)
    bh_names = {date.fromisoformat(e["date"]): e["title"] for e in ew}
    print("E&W bank holidays in range:", len(bh), "on weekdays:", sum(d.weekday() < 5 for d in bh))
    check_bh = sorted(date.fromisoformat(r["date"]) for r in check["uk_bank_holidays"])
    print("check's bank holidays == govuk's:", check_bh == bh,
          "diff:", sorted(set(check_bh) ^ set(bh)))
    for d in bh:
        if d.weekday() >= 5:
            print("  WEEKEND bank holiday?", d, bh_names[d])

    # ---- scheduled auction days and instants ----
    wd = weekdays(FIRST, LAST)
    sched = [d for d in wd if d not in set(bh)]
    print("weekdays:", len(wd), "scheduled:", len(sched))
    am = tuple((d.isoformat(), t_ct(d, 10, 30)) for d in sched)
    pm_all = {d.isoformat(): t_ct(d, 15, 0) for d in sched}
    no_auc = check["no_auction_days"]
    no_pm = sorted(r["date"] for r in no_auc if not r["pm_held"])
    no_am = sorted(r["date"] for r in no_auc if not r["am_held"])
    print("no-auction rows:", len(no_auc), "PM-not-held:", len(no_pm), "AM-not-held:", len(no_am))
    for r in no_auc:
        assert r["notice_date"] < r["date"], r
        d = date.fromisoformat(r["date"])
        assert d.weekday() < 5 and d not in set(bh), r
    am = tuple(row for row in am if row[0] not in set(no_am))
    pm = tuple((d, t) for d, t in pm_all.items() if d not in set(no_pm))
    print("AM rows:", len(am), "PM rows:", len(pm))
    print("AM == module:", am == rel.GOLD_AM_AUCTIONS,
          "PM == module:", pm == rel.GOLD_PM_AUCTIONS)
    if am != rel.GOLD_AM_AUCTIONS:
        print("  AM diff:", sorted(set(am) ^ set(rel.GOLD_AM_AUCTIONS))[:10])
    if pm != rel.GOLD_PM_AUCTIONS:
        print("  PM diff:", sorted(set(pm) ^ set(rel.GOLD_PM_AUCTIONS))[:10])
    print("AM instants:", Counter(t for _, t in am))
    print("PM instants:", Counter(t for _, t in pm))
    five = [date.fromisoformat(d) for d, t in am if t == "05:30"]
    by_year: dict[int, list[date]] = {}
    for d in five:
        by_year.setdefault(d.year, []).append(d)
    def span(ds: list[date]) -> str:
        return f"{ds[0]}..{ds[-1]} ({len(ds)})" if ds else "(none in table)"

    for y, ds in sorted(by_year.items()):
        spring = [d for d in ds if d.month <= 6]
        autumn = [d for d in ds if d.month > 6]
        print(f"  5h {y} (table rows, bank holidays removed): spring {span(spring)} "
              f"autumn {span(autumn)}")
    # C10's frozen table (weekday ranges) from catalog lines 208-215
    c10 = {2019: ("03-11", "03-29", 15, "10-28", "11-01", 5),
           2020: ("03-09", "03-27", 15, "10-26", "10-30", 5),
           2021: ("03-15", "03-26", 10, "11-01", "11-05", 5),
           2022: ("03-14", "03-25", 10, "10-31", "11-04", 5),
           2023: ("03-13", "03-24", 10, "10-30", "11-03", 5),
           2024: ("03-11", "03-29", 15, "10-28", "11-01", 5),
           2025: ("03-10", "03-28", 15, "10-27", "10-31", 5),
           2026: ("03-09", "03-27", 15, "10-26", "10-30", 5)}
    # recompute 5-hour weekdays from zoneinfo alone (no bank-holiday removal) per year
    for y, (s0, s1, ns, a0, a1, na) in c10.items():
        ys = [d for d in weekdays(date(y, 1, 1), date(y, 12, 31))
              if t_ct(d, 10, 30) == "05:30"]
        sp = [d for d in ys if d.month <= 6]
        au = [d for d in ys if d.month > 6]
        ok = (f"{sp[0]:%m-%d}", f"{sp[-1]:%m-%d}", len(sp), f"{au[0]:%m-%d}", f"{au[-1]:%m-%d}",
              len(au)) == (s0, s1, ns, a0, a1, na)
        print(f"  C10 {y} matches: {ok}")
    # research window
    win_am = [r for r in am if WIN0.isoformat() <= r[0] <= WIN1.isoformat()]
    win_pm = [r for r in pm if WIN0.isoformat() <= r[0] <= WIN1.isoformat()]
    win_wd = [d for d in wd if WIN0 <= d <= WIN1]
    win_bh = [d for d in bh if WIN0 <= d <= WIN1]
    print("window: weekdays", len(win_wd), "bank holidays", len(win_bh), "AM", len(win_am),
          "PM", len(win_pm), "AM at 05:30", sum(t == "05:30" for _, t in win_am))
    print("window PM-not-held:", [d for d in no_pm if WIN0.isoformat() <= d <= WIN1.isoformat()])
    # the check's own auction_days list vs mine
    chk_days = {r["date"]: (r["am_ct"], r["pm_ct"], r["five_hour_week"]) for r in check["auction_days"]}
    mine = {d: (t_ct(date.fromisoformat(d), 10, 30), t_ct(date.fromisoformat(d), 15, 0))
            for d, _ in am}
    print("check auction_days == mine (dates):", set(chk_days) == set(mine))
    bad = [d for d in mine if chk_days.get(d, (None, None))[:2] != mine[d]]
    print("check instants mismatches:", len(bad), bad[:5])
    # NO_AUCTION_DAYS module table
    mod_na = rel.NO_AUCTION_DAYS
    print("NO_AUCTION_DAYS n:", len(mod_na), "dates == check's:",
          [r[0] for r in mod_na] == sorted(r["date"] for r in no_auc),
          "kinds:", Counter(r[1] for r in mod_na))
    # ---- FOMC ----
    calj = json.loads(calj_p.read_text())
    rows = calj["releases"]
    for r in rows:  # products is stored as the repr of a list
        if isinstance(r.get("products"), str):
            r["products"] = ast.literal_eval(r["products"])
    fomc_rows = [r for r in rows if r.get("release") == "FOMC"]
    print("FOMC rows with products naming MGC:", sum("MGC" in r["products"] for r in fomc_rows))
    print("calendar cancellations naming FOMC:",
          [(c["release"], c["originally_scheduled"]) for c in calj["cancellations"]
           if c["release"] == "FOMC"])
    inst = []
    for r in fomc_rows:
        utc = datetime.fromisoformat(r["instant_utc"].replace("Z", "+00:00"))
        ct = utc.astimezone(CHICAGO)
        inst.append((ct.date().isoformat(), f"{ct:%H:%M}"))
    print("FOMC rows:", len(fomc_rows), "CT instants:", Counter(t for _, t in inst))
    fomc_dates = tuple(d for d, t in sorted(inst) if t == "13:00")
    print("FOMC dates == module:", fomc_dates == rel.FOMC_STATEMENT_DATES, len(fomc_dates))
    k2_src = (REPO / "strategy/members/k2/_releases.py").read_text()
    k2 = None
    for node in ast.parse(k2_src).body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            tgt = node.targets[0] if isinstance(node, ast.Assign) else node.target
            if getattr(tgt, "id", None) == "FOMC_STATEMENT_DATES":
                k2 = tuple(ast.literal_eval(node.value))
    print("FOMC == E.3 K2 table:", k2 == rel.FOMC_STATEMENT_DATES, None if k2 is None else len(k2))
    win_f = [d for d in fomc_dates if WIN0.isoformat() <= d <= WIN1.isoformat()]
    print("FOMC in window:", len(win_f), win_f)
    # ---- K5-L-04: rows for MGC / MHG in the frozen calendar ----
    prods: Counter = Counter()
    for r in rows:
        ps = r["products"]
        if "MGC" in ps or "MHG" in ps:
            utc = datetime.fromisoformat(r["instant_utc"].replace("Z", "+00:00"))
            ct = utc.astimezone(CHICAGO)
            prods[(r.get("release"), f"{ct:%H:%M}", "MGC" in ps, "MHG" in ps)] += 1
    print("frozen calendar rows naming MGC/MHG (release, CT, MGC?, MHG?):")
    for k, v in sorted(prods.items()):
        print("  ", k, v)
    print("distinct releases in calendar:", Counter(r.get("release") for r in rows))
    # ---- METALS_FULL_SESSIONS ----
    cal = load_group_calendar("metals")
    src_sha = sha256_file(REPO / "data/calendars/metals.py")
    print("metals.py sha == module's:", src_sha == cal_mod.METALS_FULL_SESSIONS_SOURCE_SHA256)
    tds = trade_dates_between(cal, FIRST, LAST)
    full = tuple(d.isoformat() for d in tds if cal.early_halt_ct(d) is None)
    halts = [d for d in tds if cal.early_halt_ct(d) is not None]
    print("metals trade dates:", len(tds), "full:", len(full), "halts:", len(halts))
    print("FULL == module:", full == cal_mod.METALS_FULL_SESSIONS, len(cal_mod.METALS_FULL_SESSIONS))
    if full != cal_mod.METALS_FULL_SESSIONS:
        print("  diff:", sorted(set(full) ^ set(cal_mod.METALS_FULL_SESSIONS))[:10])
    print("first/last:", full[0], full[-1])
    print("booked_forward:", dict(cal.booked_forward))
    win_td = [d for d in tds if WIN0 <= d <= WIN1]
    win_halts = [d.isoformat() for d in halts if WIN0 <= d <= WIN1]
    print("window trade dates:", len(win_td), "window halts:", win_halts)
    win_wd_non_td = [d.isoformat() for d in win_wd if d not in set(tds)]
    print("window weekday non-trade dates:", win_wd_non_td)
    # FOMC dates vs EC-CAL
    off = [d for d in fomc_dates if date.fromisoformat(d) not in set(tds)]
    fh = [d for d in fomc_dates if cal.early_halt_ct(date.fromisoformat(d)) is not None]
    print("FOMC dates not EC-CAL trade dates:", off, "on early-halt dates:", fh)
    # auction days that are not EC-CAL trade dates / early halts (info)
    am_dates = {d for d, _ in am}
    not_td = sorted(d for d in am_dates if date.fromisoformat(d) not in set(tds))
    halt_am = sorted(d for d in am_dates if cal.early_halt_ct(date.fromisoformat(d)) is not None)
    print("AM auction days that are not EC-CAL trade dates:", len(not_td),
          [d for d in not_td if d >= WIN0.isoformat()])
    print("AM auction days on EC-CAL early halts:", len(halt_am),
          [d for d in halt_am if d >= WIN0.isoformat()])
    # UK-only holidays that are CME trade dates (traded by nothing): info
    bh_td = [d.isoformat() for d in bh if d in set(tds)]
    print("bank holidays that are CME trade dates (no auction):", len(bh_td),
          [d for d in bh_td if d >= WIN0.isoformat()])


if __name__ == "__main__":
    main()
