"""Stage E.6 Task 3 audit (MemberAuditor-K7-FableXHigh): independent recomputation of the K7
literal tables (item 5 of the brief) from their frozen sources, in the auditor's own code.

Run: PYTHONPYCACHEPREFIX=<scratch> PYTHONPATH=. nice -n 10 uv run python \
    reports/stage_e6_briefs/audit_k7/recompute_tables.py

Prints counts and every difference against strategy/members/k7/_calendar.py. Reads no bar file.
"""

from __future__ import annotations

import calendar
import json
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import numpy as np

from data.group_session import assign_trade_dates, load_group_calendar, open_intervals
from rules import sessions
from strategy.members.k7 import _calendar as M

CT = ZoneInfo("America/Chicago")
LONDON = ZoneInfo("Europe/London")
ROOT = "MBT"
FIRST, LAST = date(2019, 5, 1), date(2026, 6, 19)
RESEARCH = (date(2025, 4, 1), date(2026, 6, 19))
CONDITION_FILES = ("data/vendor/databento/condition/GLBX.MDP3_2019-04-01_2025-04-01.json",
                   "data/vendor/databento/condition/GLBX.MDP3_2025-04-01_2026-09-16.json")
EW_JSON = "reports/stage_e4c_release_check.json"
E6_JSON = "reports/stage_e6_release_check.json"
E2A_JSON = "reports/stage_e2a_bars.json"


def days(first: date, last: date):
    d = first
    while d <= last:
        yield d
        d += timedelta(days=1)


# ------------------------------------------------------------ CRYPTO_FULL_SESSIONS ----
def crypto_full_sessions():
    cal = load_group_calendar("crypto")
    full, halt_only, f_only, both, not_trade = [], [], [], [], 0
    for d in days(FIRST, LAST):
        if not cal.is_trade_date(d):
            not_trade += 1
            continue
        halt = cal.early_halt_ct(d)
        f = sessions.flatten_time_ct(ROOT, d)
        early_f = f != time(15, 8)
        if halt is None and not early_f:
            full.append(d.isoformat())
        elif halt is not None and not early_f:
            halt_only.append((d.isoformat(), str(halt), str(f)))
        elif early_f and halt is None:
            f_only.append((d.isoformat(), str(f)))
        else:
            both.append((d.isoformat(), str(halt), str(f)))
    booked = sorted(b.isoformat() for b in cal.booked_forward)
    return full, halt_only, f_only, both, booked, not_trade, cal


# ------------------------------------------------------------------ VENDOR_DEGRADED ----
def degraded_utc_dates():
    out = {}
    for rel in CONDITION_FILES:
        for r in json.load(open(rel, encoding="utf-8")):
            if r["condition"] != "available":
                out[r["date"]] = (rel.split("/")[-1], r["condition"])
    return out


def per_bar_trade_dates(cal, utc_dates: list[str]) -> dict[str, set[str]]:
    """The harness's own per-bar mapping (build_bars.py line 728 flags a bar by its UTC date):
    for each degraded UTC date, the crypto trade dates its open minutes are assigned to by
    data.group_session.assign_trade_dates."""
    opened = open_intervals(cal, FIRST - timedelta(days=7), LAST + timedelta(days=7))
    out = {}
    for u in utc_dates:
        d0 = datetime.combine(date.fromisoformat(u), time(0), tzinfo=UTC)
        ts = np.array([int((d0 + timedelta(minutes=m)).timestamp()) * 1_000_000_000
                       for m in range(1440)], dtype=np.int64)
        assigned = assign_trade_dates(opened, ts)
        tds = set()
        for d, closed in zip(assigned.as_dates(), assigned.in_closure.tolist()):
            if d is not None and not closed:
                tds.add(d.isoformat())
        out[u] = tds
    return out


# ---------------------------------------------------------------------------- MBTX ----
def easter(year: int) -> date:
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    ell = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * ell) // 451
    month, day = divmod(h + ell - 7 * m + 114, 31)
    return date(year, month, day + 1)


def nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    d = date(year, month, 1)
    while d.weekday() != weekday:
        d += timedelta(days=1)
    return d + timedelta(days=7 * (n - 1))


def last_weekday(year: int, month: int, weekday: int) -> date:
    d = date(year, month, calendar.monthrange(year, month)[1])
    while d.weekday() != weekday:
        d -= timedelta(days=1)
    return d


def observed(d: date) -> date:
    if d.weekday() == 5:
        return d - timedelta(days=1)
    if d.weekday() == 6:
        return d + timedelta(days=1)
    return d


def us_holidays(year: int) -> set[date]:
    """5 U.S.C. 6103 holidays on their OPM-observed dates, plus Good Friday (C9 lines 183-184).
    The auditor's own list; Inauguration Day is excluded (DC-area only)."""
    fixed = [date(year, 1, 1), date(year, 7, 4), date(year, 11, 11), date(year, 12, 25)]
    if year >= 2021:
        fixed.append(date(year, 6, 19))
    out = {observed(d) for d in fixed}
    out |= {nth_weekday(year, 1, 0, 3), nth_weekday(year, 2, 0, 3), last_weekday(year, 5, 0),
            nth_weekday(year, 9, 0, 1), nth_weekday(year, 10, 0, 2), nth_weekday(year, 11, 3, 4)}
    out.add(easter(year) - timedelta(days=2))
    # New Year's Day of year+1 observed on Dec 31 of this year (Saturday Jan 1)
    nxt = observed(date(year + 1, 1, 1))
    if nxt.year == year:
        out.add(nxt)
    return out


def mbtx_rule(ew: set[str], us: set[str], wording: str) -> list[tuple[str, str]]:
    """C9 lines 176-182. wording 'both': the last Friday if a business day in both the UK and
    the US, else the preceding day that is a business day for both. wording 'either' (CME's
    current text, R-1b-1): the last Friday if a business day in either, else the preceding day
    that is a business day in either."""
    rows = []
    for y in range(2021, 2027):
        for m in range(1, 13):
            if not (2021, 5) <= (y, m) <= (2026, 6):
                continue
            d = last_weekday(y, m, 4)
            while True:
                iso = d.isoformat()
                weekend = d.weekday() > 4
                uk_ok = not weekend and iso not in ew
                us_ok = not weekend and iso not in us
                ok = (uk_ok and us_ok) if wording == "both" else (uk_ok or us_ok)
                if ok:
                    break
                d -= timedelta(days=1)
            london = datetime(d.year, d.month, d.day, 16, 0, tzinfo=LONDON)
            local = london.astimezone(CT)
            assert local.date() == d, (d, local)
            rows.append((d.isoformat(), f"{local:%H:%M}"))
    return rows


def main() -> None:
    full, halt_only, f_only, both, booked, not_trade, cal = crypto_full_sessions()
    print("== CRYPTO_FULL_SESSIONS")
    print(f"recomputed {len(full)}; module {len(M.CRYPTO_FULL_SESSIONS)}; "
          f"equal={tuple(full) == M.CRYPTO_FULL_SESSIONS}")
    print("  only in module:", sorted(set(M.CRYPTO_FULL_SESSIONS) - set(full)))
    print("  only in recomputed:", sorted(set(full) - set(M.CRYPTO_FULL_SESSIONS)))
    print(f"  removed by the halt test alone ({len(halt_only)}):", halt_only)
    print(f"  removed by the F test alone ({len(f_only)}):", f_only, "module:",
          M.CRYPTO_EARLY_F_DATES)
    print(f"  removed by both ({len(both)}):", both)
    print(f"  booked-forward dates ({len(booked)}), none in the table:",
          not set(booked) & set(full), booked)
    research_full = [d for d in full if RESEARCH[0].isoformat() <= d <= RESEARCH[1].isoformat()]
    print(f"  research-window full sessions: {len(research_full)}")

    print("== VENDOR_DEGRADED")
    deg = degraded_utc_dates()
    in_cov = sorted(u for u in deg if FIRST.isoformat() <= u <= LAST.isoformat())
    trade = {d.isoformat() for d in days(FIRST, LAST) if cal.is_trade_date(d)}
    iso_map = tuple(sorted(u for u in in_cov if u in trade))
    print(f"degraded UTC dates in the files {len(deg)}, in coverage {len(in_cov)}: {in_cov}")
    print(f"ISO mapping (trade date == degraded UTC date): {len(iso_map)}; module "
          f"{len(M.VENDOR_DEGRADED)}; equal={iso_map == M.VENDOR_DEGRADED}")
    print("  only in module:", sorted(set(M.VENDOR_DEGRADED) - set(iso_map)))
    print("  only in recomputed:", sorted(set(iso_map) - set(M.VENDOR_DEGRADED)))
    print("  degraded UTC dates that are not trade dates:", [u for u in in_cov if u not in trade])
    e2a = json.load(open(E2A_JSON, encoding="utf-8"))["products"][ROOT]["degraded"]
    research_iso = [u for u in iso_map if RESEARCH[0].isoformat() <= u <= RESEARCH[1].isoformat()]
    print("  research rows:", research_iso, "e2a on_research_trade_dates equal:",
          research_iso == e2a["on_research_trade_dates"])
    per_bar = per_bar_trade_dates(cal, in_cov)
    alt = sorted(set().union(*per_bar.values()))
    print(f"  ALTERNATIVE per-bar mapping (any bar on a degraded UTC date, build_bars.py:728): "
          f"{len(alt)} trade dates")
    print("  per-bar-only (would be excluded under the per-bar reading, not under ISO):",
          sorted(set(alt) - set(iso_map)))
    print("  ISO-only:", sorted(set(iso_map) - set(alt)))
    print("  per UTC date -> trade dates:", {u: sorted(v) for u, v in per_bar.items()})

    print("== MBTX")
    ew = {r["date"] for r in json.load(open(EW_JSON, encoding="utf-8"))["ec_ew"]}
    us = {d.isoformat() for y in range(2020, 2028) for d in us_holidays(y)}
    both_rows = mbtx_rule(ew, us, "both")
    either_rows = mbtx_rule(ew, us, "either")
    print(f"rule 'both' rows {len(both_rows)}; 'either' rows {len(either_rows)}")
    print("  both vs either differences:",
          [(b, e) for b, e in zip(both_rows, either_rows) if b != e])
    print("  rows off the last Friday under 'both':",
          [r for r in both_rows if date.fromisoformat(r[0]).weekday() != 4])
    drops = {"2021-12-30", "2025-12-24"}
    expected = tuple(r for r in both_rows if r[0] not in drops)
    print(f"  expected module rows (rule less R-1b-1 drops) {len(expected)}; module "
          f"{len(M.MBTX)}; equal={expected == M.MBTX}")
    print("  only in module:", sorted(set(M.MBTX) - set(expected)))
    print("  only in recomputed:", sorted(set(expected) - set(M.MBTX)))
    print("  11:00 rows:", [d for d, t in M.MBTX if t == "11:00"])
    research_rows = [r for r in both_rows if RESEARCH[0].isoformat() <= r[0] <= "2026-05-31"]
    print(f"  research rows by the rule ({len(research_rows)}):", research_rows)
    e6 = json.load(open(E6_JSON, encoding="utf-8"))
    rows = e6["A_ec_mbtx_research"]["rows"]
    verdicts = {r["rule_date"]: r["verdict"] for r in rows}
    print("  Task 1b verdicts:", verdicts)
    unv = tuple((r["rule_date"], r["texp_ct"]) for r in rows
                if r["verdict"] == "unverifiable" and not r["after_window_record_only"])
    print(f"  unverifiable research rows {len(unv)} == module MBTX_UNVERIFIED: "
          f"{unv == M.MBTX_UNVERIFIED}")
    kept = [r for r in rows if r["verdict"] == "keep"]
    print("  keep rows:", [(r["rule_date"], r["texp_ct"]) for r in kept])
    # T_exp CT of every module row recomputed straight from zoneinfo (independent of the rule)
    bad = []
    for d, t in M.MBTX:
        dd = date.fromisoformat(d)
        local = datetime(dd.year, dd.month, dd.day, 16, 0, tzinfo=LONDON).astimezone(CT)
        if f"{local:%H:%M}" != t:
            bad.append((d, t, f"{local:%H:%M}"))
    print("  T_exp mismatches (zoneinfo):", bad)
    # US holiday list check against the Task 1b record
    print("  auditor US holidays 2021-2026 (count):",
          len([d for d in us if "2021" <= d[:4] <= "2026"]))

    print("== ENTRY_DATES and the research-window effect")
    from strategy.members.k7._event_common import ENTRY_DATES
    from strategy.members.k7 import expiry, montrend
    ent = {d.isoformat() for d in ENTRY_DATES}
    print(f"ENTRY_DATES {len(ent)} == full - degraded: "
          f"{ent == set(M.CRYPTO_FULL_SESSIONS) - set(M.VENDOR_DEGRADED)}")
    rw = lambda s: [d for d in sorted(s) if RESEARCH[0].isoformat() <= d <= RESEARCH[1].isoformat()]
    r_full = set(rw(M.CRYPTO_FULL_SESSIONS))
    r_ent = set(rw(ent))
    print("  research: full sessions", len(r_full), "entry dates", len(r_ent),
          "removed by VENDOR_DEGRADED:", sorted(r_full - r_ent))
    mondays = [d for d in rw(trade) if date.fromisoformat(d).weekday() == 0]
    mon_trade = [d for d in mondays if montrend.is_trade_day(date.fromisoformat(d))]
    print("  research Mondays that are trade dates", len(mondays), "montrend trade days",
          len(mon_trade), "removed:", sorted(set(mondays) - set(mon_trade)))
    all_mondays = [d for d in days(*RESEARCH) if d.weekday() == 0]
    print("  research Mondays (calendar)", len(all_mondays), "not trade dates:",
          [d.isoformat() for d in all_mondays if d.isoformat() not in trade])
    ev = expiry.event_schedule()
    r_ev = sorted(d.isoformat() for d in ev if RESEARCH[0] <= d <= RESEARCH[1])
    print("  expiry events total", len(ev), "research", len(r_ev), r_ev)
    print("  MBTX research rows not events:", [d for d, _ in M.MBTX
                                               if RESEARCH[0].isoformat() <= d <= RESEARCH[1].isoformat()
                                               and d not in r_ev])


if __name__ == "__main__":
    main()
