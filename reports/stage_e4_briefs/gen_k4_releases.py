"""One-off generator of strategy/members/k4/_releases.py (Stage E.4, MemberCoder-B).

Not imported by anything. Run from the repository root:

    uv run python reports/stage_e4_briefs/gen_k4_releases.py

Sources (read here, never by a member; a member can read no file, specs S0.11):
- reports/stage_e2b_release_calendar.json, the frozen release calendar (sha256 839f2437...);
- reports/stage_e4_release_check.json, Task 1b's research-window check (sha256 4c71d798... after R-T3-1),
  whose per-row verdicts the lead's section-11 ruling applies (reports/stage_e4_member_specs.md
  section 11, K4-L-01, K4-L-02, K4-L-04, K4-L-15).

Tables written (reports/stage_e4_briefs/coder_B.md):
- WPSR: (date, T_W "HH:MM" CT, weekday 0-6 Monday=0, standard) for every calendar WPSR row less
  DROPPED_WPSR; T_W = instant_utc in America/Chicago (K4-L-02); standard = a Wednesday at 10:30
  America/New_York.
- NGS: (date, T_N "HH:MM" CT) for every calendar NGS row less DROPPED_NGS.
- DROPPED_WPSR, DROPPED_NGS: (date, reason); reason = the check's verdict, then section 11's words.
  WPSR drops = the check's rows with a "drop_*" verdict; NGS drops = its rows with verdict
  "updated" or a "drop_*" verdict (section 11: the one "updated" row fails C9's second drop rule).
- API_DROPPED_WEEKS: WPSR dates of standard weeks whose API row is off its Tuesday 16:30 ET or
  whose Monday is a federal holiday per the check's api_weeks (K4-L-04; section 11: empty).
- FEDERAL_MONDAY_HOLIDAYS: the check's "federal_monday_holidays" dates.
- NYSE_NOT_FULL: every date of the check's nyse "full_closures" and "early_closes" (both windows).
- NGS_UNVERIFIED_IN_WINDOW: NGS dates the check labels "unverifiable" (kept, section 11).

tests/test_e4_k4_members_b.py recomputes every table from the two files and asserts equality with
the written module (the pin). It prints counts only, never the files.
"""

from __future__ import annotations

import hashlib
import json
import textwrap
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPO_ROOT = Path(__file__).resolve().parents[2]
CALENDAR = REPO_ROOT / "reports" / "stage_e2b_release_calendar.json"
CHECK = REPO_ROOT / "reports" / "stage_e4_release_check.json"
OUT = REPO_ROOT / "strategy" / "members" / "k4" / "_releases.py"
CALENDAR_SHA256 = "839f2437bedbeb7b3423d7058a9955a0d4ccd1aebc4b01c62be624ab11d7bcb8"
CHECK_SHA256 = "4c71d7985c3471a86cbbd88b613b9a2f81d1b08f7aa60eb442f3c77834a04896"  # after R-T3-1
CT = ZoneInfo("America/Chicago")
WEDNESDAY = 2
STANDARD_WPSR_ET = "10:30"
ET = "America/New_York"
API_TIME_ET = "16:30"

# Section 11's reasons (the lead's ruling, 02:50 PDT; 2025-07-16 restored by ruling R-T3-1, 04:35
# PDT), keyed by date; the dates must equal the check's drop verdicts exactly, or the generator
# stops.
SECTION11_WPSR = {
    "2025-12-29": "Monday, calendar 17:00 ET; the schedule row in the last capture before the "
                  "release (20251228152631 UTC) read Monday 10:30 a.m.; EIA's page carried We are "
                  "delaying today's release; the release came about 17:00 ET",
    "2026-05-28": "Thursday 12:00 ET exception; capture 20260528163711 UTC, 37 minutes after the "
                  "scheduled time, still shows the previous release",
}
SECTION11_NGS = {
    "2025-12-29": "Monday 12:00 ET (Updated); the row first appears in capture 20260126101407 "
                  "UTC; the latest capture before it (20251203063824 UTC) has no row for the "
                  "date, so no capture before the entry shows the update (C9 second drop rule)",
}
PER_LINE = {"WPSR": 2, "NGS": 3, "dates": 6}
REASON_WIDTH = 86


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ct_hhmm(instant_utc: str) -> tuple[str, str]:
    """(CT calendar date ISO, CT "HH:MM") of a calendar instant (K4-L-02)."""
    local = datetime.fromisoformat(instant_utc.replace("Z", "+00:00")).astimezone(CT)
    return local.date().isoformat(), local.strftime("%H:%M")


def is_drop(verdict: str, kind: str) -> bool:
    return verdict.startswith("drop") or (kind == "NGS" and verdict == "updated")


def drops(check: dict, kind: str, words: dict[str, str]) -> list[tuple[str, str]]:
    rows = check[kind.lower()]
    found = {r["date"]: r["verdict"] for r in rows if is_drop(r["verdict"], kind)}
    assert set(found) == set(words), (kind, sorted(found), sorted(words))
    return [(day, f"{found[day]}: {words[day]}") for day in sorted(found)]


def wpsr_rows(calendar: dict, dropped: set[str]) -> list[tuple[str, str, int, bool]]:
    out = []
    for r in calendar["releases"]:
        if r["release"] != "WPSR" or r["date"] in dropped:
            continue
        ct_day, t_w = ct_hhmm(r["instant_utc"])
        assert ct_day == r["date"] and r["tz"] == ET, r["id"]
        weekday = date.fromisoformat(r["date"]).weekday()
        standard = weekday == WEDNESDAY and r["time_local"] == STANDARD_WPSR_ET
        out.append((r["date"], t_w, weekday, standard))
    out.sort()
    assert len({row[0] for row in out}) == len(out), "two WPSR rows on one date"
    return out


def ngs_rows(calendar: dict, dropped: set[str]) -> list[tuple[str, str]]:
    out = []
    for r in calendar["releases"]:
        if r["release"] != "NGS" or r["date"] in dropped:
            continue
        ct_day, t_n = ct_hhmm(r["instant_utc"])
        assert ct_day == r["date"] and r["tz"] == ET, r["id"]
        out.append((r["date"], t_n))
    out.sort()
    assert len({row[0] for row in out}) == len(out), "two NGS rows on one date"
    return out


def api_dropped(check: dict) -> list[str]:
    return sorted(w["wpsr_date"] for w in check["api_weeks"]
                  if w["monday_federal_holiday"] or w["api_row_date"] != w["tuesday"]
                  or w["api_row_time_et"] != API_TIME_ET)


def federal_mondays(check: dict) -> list[str]:
    days = sorted({h["date"] for h in check["federal_monday_holidays"]})
    assert all(date.fromisoformat(d).weekday() == 0 for d in days), "a holiday not on a Monday"
    return days


def nyse_not_full(check: dict) -> list[str]:
    nyse = check["nyse"]
    return sorted({x["date"] for x in nyse["full_closures"]} | {x["date"] for x in
                                                                 nyse["early_closes"]})


def unverified_ngs(check: dict) -> list[str]:
    return sorted(r["date"] for r in check["ngs"] if r["verdict"] == "unverifiable")


def check_window_rows(calendar: dict, check: dict) -> None:
    """The check's rows are the calendar's research-window rows, one for one (date and ET time)."""
    first, last = check["window"]
    for kind in ("WPSR", "NGS"):
        cal = sorted((r["date"], r["time_local"]) for r in calendar["releases"]
                     if r["release"] == kind and first <= r["date"] <= last)
        chk = sorted((r["date"], r["time_et"]) for r in check[kind.lower()])
        assert cal == chk, kind


def fmt_tuple_lines(items: list[str], per_line: int) -> str:
    lines = []
    for i in range(0, len(items), per_line):
        lines.append("    " + " ".join(f"{x}," for x in items[i:i + per_line]))
    return "\n".join(lines)


def render_dates(name: str, days: list[str]) -> str:
    if not days:
        return f"{name}: tuple[str, ...] = ()\n"
    body = fmt_tuple_lines([f'"{d}"' for d in days], PER_LINE["dates"])
    return f"{name}: tuple[str, ...] = (\n{body}\n)\n"


def render_drops(name: str, rows: list[tuple[str, str]]) -> str:
    items = []
    for d, reason in rows:
        chunks = textwrap.wrap(reason, REASON_WIDTH, drop_whitespace=False)
        text = "\n".join(f'     "{c}"' for c in chunks)
        items.append(f'    ("{d}",\n{text}),')
    body = "\n".join(items)
    return f"{name}: tuple[tuple[str, str], ...] = (\n{body}\n)\n"


def render(wpsr: list, ngs: list, dropped_wpsr: list, dropped_ngs: list, api: list[str],
           holidays: list[str], nyse: list[str], unverified: list[str], window: list[str]) -> str:
    wpsr_items = [f'("{d}", "{t}", {w}, {s})' for d, t, w, s in wpsr]
    ngs_items = [f'("{d}", "{t}")' for d, t in ngs]
    n_std = sum(1 for row in wpsr if row[3])
    head = f'''"""K4 event and calendar tables (Stage E.4; specs S0.11, K4-L-01/02/04, section 11).

GENERATED by reports/stage_e4_briefs/gen_k4_releases.py from the frozen release calendar
reports/stage_e2b_release_calendar.json (sha256 RELEASE_CALENDAR_SHA256) and Task 1b's release check
reports/stage_e4_release_check.json (sha256 RELEASE_CHECK_SHA256). Do not edit by hand:
tests/test_e4_k4_members_b.py recomputes every table from those two files and asserts equality.

- WPSR: (date, T_W "HH:MM" CT, weekday 0-6 with Monday 0, standard) for every calendar WPSR row
  2019-05-01..2026-06-17 less DROPPED_WPSR. T_W = the row's instant_utc in America/Chicago
  (K4-L-02); standard = a Wednesday at 10:30 America/New_York.
- NGS: (date, T_N "HH:MM" CT) for every calendar NGS row less DROPPED_NGS.
- Research-window drops ({window[0]}..{window[1]}, section 11; C9's drop rules are applied only
  there, K4-L-01): DROPPED_WPSR 2025-12-29, 2026-05-28 (K4-L-15 for the latter; 2025-07-16 is
  kept by ruling R-T3-1); DROPPED_NGS 2025-12-29. API_DROPPED_WEEKS (K4-L-04) is empty.
- NGS_UNVERIFIED_IN_WINDOW: storage releases kept with the calendar's value, labelled
  "unverifiable" (the return's "calendar partly unverified" label for K4-ngpre-01).
- FEDERAL_MONDAY_HOLIDAYS: US federal holidays on a Monday, 2019-05-01..2026-06-19 (OPM, Task 1b).
- NYSE_NOT_FULL: NYSE full closures and early closes, 2019-05-01..2026-06-19 (Task 1b).
Counts: {len(wpsr)} WPSR rows ({n_std} standard), {len(ngs)} NGS rows,
{len(holidays)} federal Monday holidays, {len(nyse)} NYSE dates.
"""

from __future__ import annotations

RELEASE_CALENDAR_SHA256 = "{CALENDAR_SHA256}"
RELEASE_CHECK_SHA256 = "{CHECK_SHA256}"
RESEARCH_CHECK_WINDOW = ("{window[0]}", "{window[1]}")

'''
    parts = [
        head,
        render_drops("DROPPED_WPSR", dropped_wpsr), "\n",
        render_drops("DROPPED_NGS", dropped_ngs), "\n",
        render_dates("API_DROPPED_WEEKS", api), "\n",
        render_dates("NGS_UNVERIFIED_IN_WINDOW", unverified), "\n",
        "# (date, T_W CT, weekday, standard)\n",
        "WPSR: tuple[tuple[str, str, int, bool], ...] = (\n",
        fmt_tuple_lines(wpsr_items, PER_LINE["WPSR"]), "\n)\n\n",
        "# (date, T_N CT)\n",
        "NGS: tuple[tuple[str, str], ...] = (\n",
        fmt_tuple_lines(ngs_items, PER_LINE["NGS"]), "\n)\n\n",
        render_dates("FEDERAL_MONDAY_HOLIDAYS", holidays), "\n",
        render_dates("NYSE_NOT_FULL", nyse), "\n",
        '__all__ = [\n    "API_DROPPED_WEEKS", "DROPPED_NGS", "DROPPED_WPSR", '
        '"FEDERAL_MONDAY_HOLIDAYS", "NGS",\n    "NGS_UNVERIFIED_IN_WINDOW", "NYSE_NOT_FULL", '
        '"RELEASE_CALENDAR_SHA256", "RELEASE_CHECK_SHA256",\n    "RESEARCH_CHECK_WINDOW", '
        '"WPSR",\n]\n',
    ]
    return "".join(parts)


def main() -> None:
    assert sha256_file(CALENDAR) == CALENDAR_SHA256, "release calendar changed"
    assert sha256_file(CHECK) == CHECK_SHA256, "release check changed"
    calendar = json.loads(CALENDAR.read_text())
    check = json.loads(CHECK.read_text())
    check_window_rows(calendar, check)
    dropped_wpsr = drops(check, "WPSR", SECTION11_WPSR)
    dropped_ngs = drops(check, "NGS", SECTION11_NGS)
    wpsr = wpsr_rows(calendar, {d for d, _ in dropped_wpsr})
    ngs = ngs_rows(calendar, {d for d, _ in dropped_ngs})
    api = api_dropped(check)
    holidays = federal_mondays(check)
    nyse = nyse_not_full(check)
    unverified = unverified_ngs(check)
    OUT.write_text(render(wpsr, ngs, dropped_wpsr, dropped_ngs, api, holidays, nyse, unverified,
                          check["window"]))
    print(f"wrote {OUT.relative_to(REPO_ROOT)}: WPSR {len(wpsr)} "
          f"(standard {sum(1 for r in wpsr if r[3])}), NGS {len(ngs)}, dropped WPSR "
          f"{len(dropped_wpsr)}, dropped NGS {len(dropped_ngs)}, API dropped {len(api)}, "
          f"holidays {len(holidays)}, NYSE {len(nyse)}, unverified NGS {len(unverified)}; "
          f"sha256 {sha256_file(OUT)}")


if __name__ == "__main__":
    main()
