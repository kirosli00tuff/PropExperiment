"""One-off generator of strategy/members/k5/_releases.py (Stage E.4 Part 2, MemberCoder-B).

Not imported by anything. Run from the repository root:

    uv run python reports/stage_e4_briefs/gen_k5_releases.py

Sources (read here, never by a member; a member can read no file, specs S0.11):
- reports/stage_e2b_release_calendar.json, the frozen release calendar (sha256 839f2437...);
- reports/stage_e4b_release_check.json, Task 1b's K5 release check (sha256 0715d01f...), whose rows
  govern the auction tables (reports/stage_e4b_member_specs.md section 11, K5-L-01..L-03).
- strategy/members/k2/_releases.py is read as TEXT (ast), never imported, to assert that
  FOMC_STATEMENT_DATES equals E.3's table (section 11).

Tables written (reports/stage_e4_briefs/coder_B_K5.md):
- GOLD_AM_AUCTIONS, GOLD_PM_AUCTIONS: (date ISO, T_CT "HH:MM") for every scheduled gold AM (10:30
  Europe/London) and PM (15:00 Europe/London) auction day in the check's range: the weekdays that
  are not England-and-Wales bank holidays (the check's uk_bank_holidays), less the NO_AUCTION_DAYS
  rows of that auction (K5-L-03). T_CT is computed here with zoneinfo (C10, K5-L-02) and must equal
  the check's auction_days row (am_ct, pm_ct) for every date; the recomputed day list must equal
  the check's auction_days dates.
- NO_AUCTION_DAYS: (date, "AM" | "PM" | "both", reason) from the check's no_auction_days rows
  (am_held, pm_held); reason = the check's reason and its notice date. Section 11: 14 rows, all PM.
- FOMC_STATEMENT_DATES: the dates of the calendar's FOMC rows whose instant is 13:00 CT; asserted
  equal to E.3's K2 table and to the check's fomc rows.

tests/test_e4_k5_members_b.py recomputes every table from the two JSON files and asserts equality
with the written module (the pin). This script prints counts only, never the files.
"""

from __future__ import annotations

import ast
import hashlib
import json
import textwrap
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

REPO_ROOT = Path(__file__).resolve().parents[2]
CALENDAR = REPO_ROOT / "reports" / "stage_e2b_release_calendar.json"
CHECK = REPO_ROOT / "reports" / "stage_e4b_release_check.json"
K2_RELEASES = REPO_ROOT / "strategy" / "members" / "k2" / "_releases.py"
OUT = REPO_ROOT / "strategy" / "members" / "k5" / "_releases.py"
CALENDAR_SHA256 = "839f2437bedbeb7b3423d7058a9955a0d4ccd1aebc4b01c62be624ab11d7bcb8"
CHECK_SHA256 = "0715d01f0ab7f9176a7d559e4f8bde151e656c29271a9a1de22bece3218789b7"
CT = ZoneInfo("America/Chicago")
LONDON = ZoneInfo("Europe/London")
AM_LONDON = time(10, 30)  # the LBMA Gold Price AM auction start (C 485-487; C10)
PM_LONDON = time(15, 0)  # the PM auction start (C 590; C10)
FOMC_CT = "13:00"  # the statement instant the members use (section 11; E.3-L-15)
SATURDAY = 5
HELD_TO_KIND = {(True, False): "PM", (False, True): "AM", (False, False): "both"}

# Section 11 (the lead's ruling, 05:40 PDT): the 14 days announced in advance with no PM auction.
SECTION11_PM_NOT_HELD = (
    "2019-12-24", "2019-12-31", "2020-12-24", "2020-12-31", "2021-12-24", "2021-12-31",
    "2022-12-23", "2022-12-30", "2023-12-22", "2023-12-29", "2024-12-24", "2024-12-31",
    "2025-12-24", "2025-12-31",
)
# Section 11's counts: (range weekdays, bank holidays, auction days, 5-hour-week days,
# window weekdays, window bank holidays, window auction days, FOMC rows, FOMC in window).
SECTION11_COUNTS = (1863, 61, 1802, 124, 319, 12, 307, 57, 10)
PER_LINE = {"auctions": 3, "dates": 6}
REASON_WIDTH = 86


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def t_ct(day: date, london: time) -> str:
    """C10: the America/Chicago wall time of the instant whose Europe/London wall time is
    ``london`` on ``day`` (zoneinfo, K5-L-02), as "HH:MM"; it must fall on the same date."""
    local = datetime.combine(day, london, tzinfo=LONDON).astimezone(CT)
    assert local.date() == day, (day, london)
    return local.strftime("%H:%M")


def weekdays(first: str, last: str) -> list[date]:
    day, end, out = date.fromisoformat(first), date.fromisoformat(last), []
    while day <= end:
        if day.weekday() < SATURDAY:
            out.append(day)
        day += timedelta(days=1)
    return out


def in_window(day: str, window: list[str]) -> bool:
    return window[0] <= day <= window[1]


def scheduled_days(check: dict) -> list[date]:
    """Weekdays of the check's range less its England-and-Wales bank holidays (K5-L-03, C9),
    asserted equal to the check's auction_days rows, date and both CT instants."""
    first, last = check["range"]
    all_weekdays = weekdays(first, last)
    holidays = {h["date"] for h in check["uk_bank_holidays"]}
    assert all(first <= d <= last and date.fromisoformat(d).weekday() < SATURDAY
               for d in holidays), "a bank holiday outside the range or on a weekend"
    days = [d for d in all_weekdays if d.isoformat() not in holidays]
    rows = check["auction_days"]
    assert [r["date"] for r in rows] == [d.isoformat() for d in days], "auction days differ"
    for d, r in zip(days, rows, strict=True):
        am, pm = t_ct(d, AM_LONDON), t_ct(d, PM_LONDON)
        assert (r["am_ct"], r["pm_ct"]) == (am, pm), (d, r)
        assert r["five_hour_week"] == (am == "05:30") == (pm == "10:00"), (d, r)
    window = check["window"]
    counts = (len(all_weekdays), len(holidays), len(days),
              sum(1 for r in rows if r["five_hour_week"]),
              sum(1 for d in all_weekdays if in_window(d.isoformat(), window)),
              sum(1 for d in holidays if in_window(d, window)),
              sum(1 for d in days if in_window(d.isoformat(), window)))
    assert counts == SECTION11_COUNTS[:7], counts
    return days


def no_auction_rows(check: dict, days: list[date]) -> list[tuple[str, str, str]]:
    """(date, "AM" | "PM" | "both", reason) of the check's no_auction_days rows."""
    scheduled = {d.isoformat() for d in days}
    out = []
    for r in check["no_auction_days"]:
        kind = HELD_TO_KIND[(r["am_held"], r["pm_held"])]
        assert r["date"] in scheduled, r["date"]  # a weekday that is not a bank holiday
        assert r["notice_date"] < r["date"], r["date"]  # announced in advance (K5-L-03)
        out.append((r["date"], kind, f"{r['reason']}; LBMA notice {r['notice_date']}"))
    out.sort()
    assert tuple(d for d, _, _ in out) == SECTION11_PM_NOT_HELD, "not section 11's 14 days"
    assert {kind for _, kind, _ in out} == {"PM"}, "section 11: all PM only"
    return out


def auction_table(days: list[date], no_auction: list[tuple[str, str, str]], session: str,
                  london: time) -> list[tuple[str, str]]:
    """(date, T_CT) of every scheduled day of one auction (session "AM" or "PM")."""
    skip = {d for d, kind, _ in no_auction if kind in (session, "both")}
    return [(d.isoformat(), t_ct(d, london)) for d in days if d.isoformat() not in skip]


def k2_fomc_dates() -> tuple[str, ...]:
    """E.3's FOMC_STATEMENT_DATES, read from strategy/members/k2/_releases.py as text."""
    tree = ast.parse(K2_RELEASES.read_text(encoding="utf-8"))
    for node in tree.body:
        if (isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
                and node.target.id == "FOMC_STATEMENT_DATES" and node.value is not None):
            return tuple(ast.literal_eval(node.value))
    raise AssertionError("FOMC_STATEMENT_DATES not found in the K2 table")


def fomc_dates(calendar: dict, check: dict) -> list[str]:
    rows = [r for r in calendar["releases"] if r["release"] == "FOMC"]
    out = []
    for r in rows:
        local = datetime.fromisoformat(r["instant_utc"].replace("Z", "+00:00")).astimezone(CT)
        if local.strftime("%H:%M") == FOMC_CT:
            assert local.date().isoformat() == r["date"], r["id"]
            out.append(r["date"])
    out.sort()
    assert len(set(out)) == len(out) == len(rows) == SECTION11_COUNTS[7], "FOMC rows"
    assert tuple(out) == k2_fomc_dates(), "not equal to E.3's K2 table"
    assert out == sorted(r["date"] for r in check["fomc"]["rows"]), "not the check's rows"
    assert {r["instant_ct"] for r in check["fomc"]["rows"]} == {FOMC_CT}
    assert sum(1 for d in out if in_window(d, check["window"])) == SECTION11_COUNTS[8]
    assert [d for d in out if in_window(d, check["window"])] == check["fomc"]["research_window"]
    return out


def fmt_tuple_lines(items: list[str], per_line: int) -> str:
    lines = []
    for i in range(0, len(items), per_line):
        lines.append("    " + " ".join(f"{x}," for x in items[i:i + per_line]))
    return "\n".join(lines)


def render_auctions(name: str, rows: list[tuple[str, str]]) -> str:
    body = fmt_tuple_lines([f'("{d}", "{t}")' for d, t in rows], PER_LINE["auctions"])
    return f"{name}: tuple[tuple[str, str], ...] = (\n{body}\n)\n"


def render_dates(name: str, days: list[str]) -> str:
    body = fmt_tuple_lines([f'"{d}"' for d in days], PER_LINE["dates"])
    return f"{name}: tuple[str, ...] = (\n{body}\n)\n"


def render_no_auction(rows: list[tuple[str, str, str]]) -> str:
    items = []
    for d, kind, reason in rows:
        chunks = textwrap.wrap(reason, REASON_WIDTH, drop_whitespace=False)
        text = "\n".join(f'     "{c}"' for c in chunks)
        items.append(f'    ("{d}", "{kind}",\n{text}),')
    body = "\n".join(items)
    return f"NO_AUCTION_DAYS: tuple[tuple[str, str, str], ...] = (\n{body}\n)\n"


def render(am: list[tuple[str, str]], pm: list[tuple[str, str]],
           no_auction: list[tuple[str, str, str]], fomc: list[str], check: dict) -> str:
    first, last = check["range"]
    window = check["window"]
    five = sum(1 for _, t in am if t == "05:30")
    head = f'''"""K5 event tables (Stage E.4b; specs S0.11, K5-L-01..L-03, section 11). GENERATED.

Generated by reports/stage_e4_briefs/gen_k5_releases.py from the frozen release calendar
reports/stage_e2b_release_calendar.json (sha256 RELEASE_CALENDAR_SHA256) and Task 1b's K5 release
check reports/stage_e4b_release_check.json (sha256 RELEASE_CHECK_SHA256). Do not edit by hand:
tests/test_e4_k5_members_b.py recomputes every table from those two files and asserts equality.

- GOLD_AM_AUCTIONS: (date, T_CT "HH:MM") for every scheduled gold AM auction day (10:30
  Europe/London), {first}..{last}: the weekdays that are not England-and-Wales bank holidays,
  less the NO_AUCTION_DAYS rows of the AM auction (K5-L-03; none). T_CT = the America/Chicago wall
  time of the instant whose Europe/London wall time is 10:30 on the date (C10, K5-L-02): 04:30, or
  05:30 in 5-hour weeks.
- GOLD_PM_AUCTIONS: the same for the PM auction (15:00 Europe/London): 09:00, or 10:00 in 5-hour
  weeks, less the NO_AUCTION_DAYS rows of the PM auction (all 14).
- NO_AUCTION_DAYS: (date, "AM" | "PM" | "both", reason) for the days announced in advance with no
  such auction (section 11: the Christmas and New Year half days, PM only).
- FOMC_STATEMENT_DATES: the dates of the calendar's FOMC rows whose instant is 13:00 CT (equal to
  E.3's K2 table, section 11).
Counts: {len(am)} AM days ({five} at 05:30 CT), {len(pm)} PM days, {len(no_auction)} no-auction \
rows, {len(fomc)} FOMC dates.
"""

from __future__ import annotations

RELEASE_CALENDAR_SHA256 = "{CALENDAR_SHA256}"
RELEASE_CHECK_SHA256 = "{CHECK_SHA256}"
TABLE_RANGE = ("{first}", "{last}")
RESEARCH_CHECK_WINDOW = ("{window[0]}", "{window[1]}")

'''
    parts = [
        head,
        render_no_auction(no_auction), "\n",
        "# (date, T_CT of the 10:30 London AM auction)\n",
        render_auctions("GOLD_AM_AUCTIONS", am), "\n",
        "# (date, T_CT of the 15:00 London PM auction)\n",
        render_auctions("GOLD_PM_AUCTIONS", pm), "\n",
        render_dates("FOMC_STATEMENT_DATES", fomc), "\n",
        '__all__ = [\n    "FOMC_STATEMENT_DATES", "GOLD_AM_AUCTIONS", "GOLD_PM_AUCTIONS", '
        '"NO_AUCTION_DAYS",\n    "RELEASE_CALENDAR_SHA256", "RELEASE_CHECK_SHA256", '
        '"RESEARCH_CHECK_WINDOW", "TABLE_RANGE",\n]\n',
    ]
    return "".join(parts)


def build(calendar: dict, check: dict) -> str:
    days = scheduled_days(check)
    no_auction = no_auction_rows(check, days)
    am = auction_table(days, no_auction, "AM", AM_LONDON)
    pm = auction_table(days, no_auction, "PM", PM_LONDON)
    assert len(am) == SECTION11_COUNTS[2] and len(pm) == SECTION11_COUNTS[2] - 14
    return render(am, pm, no_auction, fomc_dates(calendar, check), check)


def main() -> None:
    assert sha256_file(CALENDAR) == CALENDAR_SHA256, "release calendar changed"
    assert sha256_file(CHECK) == CHECK_SHA256, "release check changed"
    calendar = json.loads(CALENDAR.read_text(encoding="utf-8"))
    check = json.loads(CHECK.read_text(encoding="utf-8"))
    OUT.write_text(build(calendar, check), encoding="utf-8")
    print(f"wrote {OUT.relative_to(REPO_ROOT)}: sha256 {sha256_file(OUT)}")


if __name__ == "__main__":
    main()
