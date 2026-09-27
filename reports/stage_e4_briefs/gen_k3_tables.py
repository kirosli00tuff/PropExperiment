"""One-off generator of strategy/members/k3/_calendar.py and strategy/members/k3/_clocks.py
(Stage E.4 Part 3, Task 2, MemberCoder-B).

Not imported by any member. Run from the repository root:

    uv run python reports/stage_e4_briefs/gen_k3_tables.py

Sources (reports/stage_e4c_member_specs.md S0.4, S0.11, K3-L-01..K3-L-11 and section 11):
- EC-CAL: data.group_session.load_group_calendar("fx") (data/calendars/fx.py), coverage
  2019-05-01..2026-06-19, and the engine's session rules, rules.sessions.flatten_time_ct (K3-L-11);
- the K3 check, reports/stage_e4c_release_check.json (sha256 c63c13a6...; its rows govern,
  section 11).

_calendar.py (S0.11):
- FX_FULL_SESSIONS: every EC-CAL FX trade date over the calendar's coverage (K4-L-13) whose
  early_halt_ct is None AND whose engine F (rules.sessions.flatten_time_ct) is the regular 15:08 CT
  for every K3 root (K3-L-11). FX_EARLY_F_DATES lists the dates the second condition removes.
- MONTH_ENDS: (YYYY-MM, ME(m)), ME(m) = the last EC-CAL FX trade date of month m, halted or not
  (K3-L-06), only for months whose last calendar day lies inside the coverage (section 11).
- EW_BANK_HOLIDAYS: the check's EC-EW rows (England and Wales, gov.uk).
- TGT_CLOSING_DAYS: the check's EC-TGT rows (distinct dates; six a year, the ECB rule).
- TOKYO_BUSINESS_DAYS: EC-JP (K3-L-08): weekdays that are not a CAO national holiday (the check's
  ec_jp_holidays) and not 31 December or 1-3 January, over 2019-04-01..2026-06-19.
- GOTOBI_OR_TOKYO_MONTH_END: the Tokyo business days of that range whose day of month is 5, 10,
  15, 20, 25 or 30, or that are the last Tokyo business day of their calendar month (no shift).
_clocks.py (S0.4, K3-L-02; C9's rules, computed here with zoneinfo, never at run time):
- T_L: per weekday d of 2019-04-01..2026-06-19, 16:00 Europe/London on d as CT "HH:MM" on d;
- T_E: per weekday d, 14:15 Europe/Berlin on d as CT "HH:MM" on d;
- T_T: per Tokyo business day d, 09:55 Asia/Tokyo on d as CT "HH:MM" on calendar day d-1.

Every table is checked against the release check's rows and C9's known-answer tests (catalog
reports/stage_e0_catalog_K3.md lines 158-194) before anything is written.
tests/test_e4_k3_members_b.py recomputes every table independently and asserts that both modules
are exactly this script's output (the pin), so the files and this script cannot drift apart.
"""

from __future__ import annotations

import calendar
import hashlib
import json
import sys
from collections import Counter
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from data.group_session import load_group_calendar, trade_dates_between  # noqa: E402
from rules import sessions  # noqa: E402
from rules.products import product  # noqa: E402

OUT_DIR = REPO_ROOT / "strategy" / "members" / "k3"
CALENDAR_OUT = "strategy/members/k3/_calendar.py"
CLOCKS_OUT = "strategy/members/k3/_clocks.py"
CHECK_FILE = "reports/stage_e4c_release_check.json"
CHECK_SHA256 = "c63c13a69559c90efdb72969e20244a261343839660436082fcaf44a35f931e9"
FX_CALENDAR_FILE = "data/calendars/fx.py"
SESSIONS_FILE = "rules/sessions.py"
K3_ROOTS = ("6E", "6A", "6B", "6C", "6J", "6S", "6N")
REGULAR_F = time(15, 8)  # D6 FX row, rules.sessions.REGULAR_FLATTEN_CT["fx"]
CAL_FIRST, CAL_LAST = date(2019, 5, 1), date(2026, 6, 19)  # EC-CAL FX coverage (K4-L-13)
CLOCK_FIRST, CLOCK_LAST = date(2019, 4, 1), date(2026, 6, 19)  # K3-L-01, the brief's range
TOKYO_CLOSED_MONTH_DAYS = frozenset({(12, 31), (1, 1), (1, 2), (1, 3)})  # EC-JP year-end rule
GOTOBI_DAYS = frozenset({5, 10, 15, 20, 25, 30})
CT = ZoneInfo("America/Chicago")
LONDON, BERLIN, TOKYO = "Europe/London", "Europe/Berlin", "Asia/Tokyo"
# C9's known-answer tests and computed examples (catalog lines 158-194), as literals.
C9_T_L = {"2025-03-10": "11:00", "2025-03-31": "10:00", "2025-10-27": "11:00",
          "2025-11-03": "10:00", "2021-11-01": "11:00", "2021-11-02": "11:00",
          "2021-11-03": "11:00", "2021-11-04": "11:00", "2021-11-05": "11:00"}
C9_T_E = {"2025-03-10": "08:15", "2025-04-01": "07:15"}
C9_T_T = {"2025-11-04": ("2025-11-03", "18:55"), "2025-01-10": ("2025-01-09", "18:55"),
          "2025-03-10": ("2025-03-09", "19:55"), "2025-07-10": ("2025-07-09", "19:55")}
C9_T_L_1100_RANGES = (
    "2019-03-11..2019-03-29", "2019-10-28..2019-11-01", "2020-03-09..2020-03-27",
    "2020-10-26..2020-10-30", "2021-03-15..2021-03-26", "2021-11-01..2021-11-05",
    "2022-03-14..2022-03-25", "2022-10-31..2022-11-04", "2023-03-13..2023-03-24",
    "2023-10-30..2023-11-03", "2024-03-11..2024-03-29", "2024-10-28..2024-11-01",
    "2025-03-10..2025-03-28", "2025-10-27..2025-10-31", "2026-03-09..2026-03-27")
DATES_PER_LINE = 5
PAIRS_PER_LINE = 3


# ------------------------------------------------------------------------ helpers ----
def sha256_of(rel: str) -> str:
    return hashlib.sha256((REPO_ROOT / rel).read_bytes()).hexdigest()


def load_check() -> dict:
    data = (REPO_ROOT / CHECK_FILE).read_bytes()
    assert hashlib.sha256(data).hexdigest() == CHECK_SHA256, "release check changed"
    return json.loads(data)


def days_between(first: date, last: date) -> list[date]:
    return [first + timedelta(days=n) for n in range((last - first).days + 1)]


def weekdays(first: date, last: date) -> list[date]:
    return [d for d in days_between(first, last) if d.weekday() < 5]


def expand_ranges(ranges: list[str] | tuple[str, ...], first: date, last: date) -> list[str]:
    """Weekdays of "YYYY-MM-DD..YYYY-MM-DD" ranges that lie in [first, last]."""
    out: list[str] = []
    for text in ranges:
        lo, hi = (date.fromisoformat(x) for x in text.split(".."))
        out += [d.isoformat() for d in weekdays(max(lo, first), min(hi, last))]
    return sorted(out)


def ct_of(day: date, hh: int, mm: int, zone: str) -> tuple[date, str]:
    """The CT calendar date and "HH:MM" of hh:mm local time in ``zone`` on ``day``."""
    local = datetime.combine(day, time(hh, mm), tzinfo=ZoneInfo(zone)).astimezone(CT)
    return local.date(), f"{local:%H:%M}"


def easter(year: int) -> date:
    """Gregorian Easter Sunday (anonymous Gregorian computus)."""
    a, b, c = year % 19, year // 100, year % 100
    d, e = b // 4, b % 4
    g = (8 * b + 13) // 25
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    lx = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * lx) // 451
    month, day = divmod(h + lx - 7 * m + 114, 31)
    return date(year, month, day + 1)


# ----------------------------------------------------------------------- calendar ----
def fx_full_sessions() -> tuple[list[str], list[str]]:
    """(FX_FULL_SESSIONS, the dates K3-L-11's second condition removes)."""
    cal = load_group_calendar("fx")
    assert tuple(cal.coverage) == (CAL_FIRST, CAL_LAST), cal.coverage  # K4-L-13
    assert all(product(r).group == "fx" for r in K3_ROOTS)
    full: list[str] = []
    early_f: list[str] = []
    for d in trade_dates_between(cal, CAL_FIRST, CAL_LAST):
        if cal.early_halt_ct(d) is not None:
            continue
        if all(sessions.flatten_time_ct(r, d) == REGULAR_F for r in K3_ROOTS):
            full.append(d.isoformat())
        else:
            early_f.append(d.isoformat())
    return full, early_f


def month_ends(check: dict) -> list[tuple[str, str]]:
    """(YYYY-MM, ME(m)) for the months whose last day lies in the EC-CAL coverage."""
    cal = load_group_calendar("fx")
    last_of: dict[tuple[int, int], date] = {}
    for d in trade_dates_between(cal, CAL_FIRST, CAL_LAST):
        last_of[(d.year, d.month)] = d  # ascending: the last trade date of the month wins
    rows = []
    for (y, m), d in sorted(last_of.items()):
        month_last_day = date(y, m, calendar.monthrange(y, m)[1])
        if CAL_FIRST <= month_last_day <= CAL_LAST:
            rows.append((f"{y:04d}-{m:02d}", d.isoformat()))
    expected = [(r["month"], r["me_date"]) for r in check["month_ends"]
                if r["in_ec_cal_coverage"]]
    assert rows == expected, "MONTH_ENDS differ from the release check"
    for r in check["month_ends"]:
        if r["in_ec_cal_coverage"]:
            halt = cal.early_halt_ct(date.fromisoformat(r["me_date"]))
            assert (None if halt is None else halt.isoformat()) == r["early_halt_ct"], r
    return rows


def ew_bank_holidays(check: dict) -> list[str]:
    days = sorted({r["date"] for r in check["ec_ew"]})
    assert len(days) == len(check["ec_ew"]) == 63  # section 11
    assert all(date.fromisoformat(d).weekday() < 5 for d in days)
    return days


def tgt_closing_days(check: dict) -> list[str]:
    days = sorted({r["date"] for r in check["ec_tgt"]})
    years = sorted({int(d[:4]) for d in days})
    assert years == list(range(2019, 2027)), years
    rule = sorted(x.isoformat() for y in years for x in (
        date(y, 1, 1), easter(y) - timedelta(days=2), easter(y) + timedelta(days=1),
        date(y, 5, 1), date(y, 12, 25), date(y, 12, 26)))
    assert days == rule, "EC-TGT rows differ from the six-day ECB rule"  # section 11
    return days


def jp_holidays(check: dict) -> frozenset[str]:
    days = frozenset(r["date"] for r in check["ec_jp_holidays"])
    assert len(days) == len(check["ec_jp_holidays"]) == 148  # section 11
    return days


def is_tokyo_business_day(d: date, holidays: frozenset[str]) -> bool:
    return (d.weekday() < 5 and d.isoformat() not in holidays
            and (d.month, d.day) not in TOKYO_CLOSED_MONTH_DAYS)


def tokyo_business_days(check: dict) -> list[str]:
    holidays = jp_holidays(check)
    counts = Counter(d.year for d in days_between(date(2019, 1, 1), date(2026, 12, 31))
                     if is_tokyo_business_day(d, holidays))
    assert {str(y): n for y, n in sorted(counts.items())} == check["tokyo_business_days_count"]
    year_end = check["tokyo_year_end_check"]
    assert year_end["dates_with_ttm_but_not_tokyo_business_day"] == []
    assert year_end["tokyo_business_days_without_ttm"] == []
    return [d.isoformat() for d in days_between(CLOCK_FIRST, CLOCK_LAST)
            if is_tokyo_business_day(d, holidays)]


def gotobi_or_tokyo_month_end(check: dict) -> list[str]:
    holidays = jp_holidays(check)
    whole = [d for d in days_between(CLOCK_FIRST.replace(day=1), date(2026, 6, 30))
             if is_tokyo_business_day(d, holidays)]  # whole months, for the month-end test
    last_of: dict[tuple[int, int], date] = {}
    for d in whole:
        last_of[(d.year, d.month)] = d
    month_end = sorted(d.isoformat() for d in last_of.values())
    assert month_end == check["tokyo_month_end"], "Tokyo month-ends differ from the check"
    in_range = [d for d in whole if CLOCK_FIRST <= d <= CLOCK_LAST]
    gotobi = [d.isoformat() for d in in_range if d.day in GOTOBI_DAYS]
    assert tuple(check["gotobi_window"]) == (CLOCK_FIRST.isoformat(), CLOCK_LAST.isoformat())
    assert gotobi == check["gotobi"] and len(gotobi) == 350, "gotobi dates differ from the check"
    ends = set(month_end)
    return [d.isoformat() for d in in_range if d.day in GOTOBI_DAYS or d.isoformat() in ends]


# ------------------------------------------------------------------------- clocks ----
def clock_t_l(check: dict) -> list[tuple[str, str]]:
    rows = []
    for d in weekdays(CLOCK_FIRST, CLOCK_LAST):
        ct_day, hhmm = ct_of(d, 16, 0, LONDON)
        assert ct_day == d
        rows.append((d.isoformat(), hhmm))
    at_1100 = [d for d, t in rows if t == "11:00"]
    assert {t for _, t in rows} == set(check["t_l"]["ct_times_seen"]) == {"10:00", "11:00"}
    assert at_1100 == expand_ranges(C9_T_L_1100_RANGES, CLOCK_FIRST, CLOCK_LAST)  # C9's list
    by_year = [r for year in check["t_l"]["weekdays_at_1100_by_year"].values() for r in year]
    assert at_1100 == expand_ranges(by_year, CLOCK_FIRST, CLOCK_LAST)
    assert check["t_l"]["matches_c9_list"] and check["t_l"]["known_answer_all_pass"]
    table = dict(rows)
    for day, hhmm in C9_T_L.items():
        assert table[day] == hhmm, day
    for ka in check["t_l"]["known_answer"]:
        assert table[ka["date"]] == ka["computed_ct"] == ka["expected_ct"], ka
    return rows


def clock_t_e(check: dict, t_l: list[tuple[str, str]]) -> list[tuple[str, str]]:
    rows = []
    for d in weekdays(CLOCK_FIRST, CLOCK_LAST):
        ct_day, hhmm = ct_of(d, 14, 15, BERLIN)
        assert ct_day == d
        rows.append((d.isoformat(), hhmm))
    at_0815 = [d for d, t in rows if t == "08:15"]
    assert {t for _, t in rows} == set(check["t_e"]["ct_times_seen"]) == {"07:15", "08:15"}
    assert at_0815 == [d for d, t in t_l if t == "11:00"]  # the same mismatch weeks (C9)
    by_year = [r for year in check["t_e"]["weekdays_at_0815_by_year"].values() for r in year]
    assert at_0815 == expand_ranges(by_year, CLOCK_FIRST, CLOCK_LAST)
    assert check["t_e"]["same_weeks_as_t_l_1100"] and check["t_e"]["known_answer_all_pass"]
    table = dict(rows)
    for day, hhmm in C9_T_E.items():
        assert table[day] == hhmm, day
    for ka in check["t_e"]["known_answer"]:
        assert table[ka["date"]] == ka["computed_ct"] == ka["expected_ct"], ka
    return rows


def clock_t_t(check: dict, business_days: list[str]) -> list[tuple[str, str]]:
    rows = []
    for text in business_days:
        d = date.fromisoformat(text)
        ct_day, hhmm = ct_of(d, 9, 55, TOKYO)
        assert ct_day == d - timedelta(days=1)  # always the CT evening of d-1 (C9)
        rows.append((text, hhmm))
    assert {t for _, t in rows} == set(check["t_t"]["ct_times_seen"]) == {"18:55", "19:55"}
    assert check["t_t"]["always_on_ct_day_d_minus_1"] and check["t_t"]["known_answer_all_pass"]
    table = dict(rows)
    for day, (prev, hhmm) in C9_T_T.items():
        assert (date.fromisoformat(day) - timedelta(days=1)).isoformat() == prev
        assert table[day] == hhmm, day
    for ka in check["t_t"]["known_answer"]:
        prev, hhmm, _zone = ka["computed"].split(" ")
        assert (date.fromisoformat(ka["d"]) - timedelta(days=1)).isoformat() == prev
        assert table[ka["d"]] == hhmm, ka
    return rows


# ------------------------------------------------------------------------- render ----
def render_dates(name: str, days: list[str], comment: str) -> str:
    lines = [f"# {comment} ({len(days)} dates)", f"{name}: tuple[str, ...] = ("]
    for i in range(0, len(days), DATES_PER_LINE):
        lines.append("    " + " ".join(f'"{d}",' for d in days[i:i + DATES_PER_LINE]))
    lines.append(")")
    return "\n".join(lines)


def render_pairs(name: str, rows: list[tuple[str, str]], comment: str) -> str:
    lines = [f"# {comment} ({len(rows)} rows)", f"{name}: tuple[tuple[str, str], ...] = ("]
    for i in range(0, len(rows), PAIRS_PER_LINE):
        lines.append("    " + " ".join(f'("{a}", "{b}"),' for a, b in rows[i:i + PAIRS_PER_LINE]))
    lines.append(")")
    return "\n".join(lines)


def render_sources(pairs: list[tuple[str, str]]) -> str:
    body = "\n".join(f'    ("{p}",\n     "{s}"),' for p, s in pairs)
    return f"SOURCE_SHA256: tuple[tuple[str, str], ...] = (\n{body}\n)"


CALENDAR_DOC = '''"""K3 calendar tables (literal; reports/stage_e4c_member_specs.md S0.11,
K3-L-04, K3-L-06, K3-L-08, K3-L-11 and section 11).

GENERATED by reports/stage_e4_briefs/gen_k3_tables.py from EC-CAL (data.group_session.
load_group_calendar("fx"), data/calendars/fx.py), the engine's session rules (rules/sessions.py,
flatten_time_ct) and the K3 check (reports/stage_e4c_release_check.json). Do not edit by hand:
tests/test_e4_k3_members_b.py recomputes every table and asserts this file is the generator's
output. Members read these tuples; nothing here is computed at run time.

- FX_FULL_SESSIONS: EC-CAL FX trade dates of the coverage 2019-05-01..2026-06-19 (K4-L-13) with no
  early halt AND the regular engine F of 15:08 CT for every K3 root (K3-L-11). The early-halt test
  of every new K3 member reads trade date d here (K3-L-04), never a bar's early_halt_ct.
- FX_EARLY_F_DATES: the trade dates without an early_halt_ct whose engine F is early (K3-L-11's
  second condition removes them; information only).
- MONTH_ENDS: (YYYY-MM, ME(m)), ME(m) the last EC-CAL FX trade date of month m, halted or not
  (K3-L-06), for the months whose last day lies inside the coverage (section 11).
- EW_BANK_HOLIDAYS: England-and-Wales bank holidays (EC-EW, gov.uk), 2019-04..2026-06.
- TGT_CLOSING_DAYS: TARGET closing days (EC-TGT), six a year 2019-2026.
- TOKYO_BUSINESS_DAYS: EC-JP (K3-L-08), 2019-04-01..2026-06-19: weekdays that are not a CAO
  national holiday and not 31 December or 1-3 January.
- GOTOBI_OR_TOKYO_MONTH_END: those Tokyo business days whose day of month is 5, 10, 15, 20, 25 or
  30, or that are the last Tokyo business day of their calendar month (no shift; C9, section 8).
"""'''

CLOCKS_DOC = '''"""K3 fix clocks (literal; reports/stage_e4c_member_specs.md S0.4, S0.11, K3-L-02).

GENERATED by reports/stage_e4_briefs/gen_k3_tables.py with zoneinfo (C9's rules) and checked there
against the K3 check (reports/stage_e4c_release_check.json) and C9's known-answer tests. Do not edit
by hand: tests/test_e4_k3_members_b.py recomputes every row. No member computes a fix instant at
run time; members read these tuples.

- T_L: per weekday d of 2019-04-01..2026-06-19, (d, CT "HH:MM" on d) of 16:00 Europe/London on d,
  the WM/Reuters London 4 p.m. fix: 10:00, or 11:00 in the C9 mismatch weeks.
- T_E: per weekday d of the same range, (d, CT "HH:MM" on d) of 14:15 Europe/Berlin on d, the ECB
  fix: 07:15, or 08:15 in the same mismatch weeks.
- T_T: per Tokyo business day d of the same range (EC-JP), (d, CT "HH:MM" on calendar day d-1) of
  09:55 Asia/Tokyo on d, the Tokyo fix: 18:55 (CST) or 19:55 (CDT).
"""'''


def build() -> dict[str, str]:
    """{repository path: module text} of both generated modules."""
    check = load_check()
    full, early_f = fx_full_sessions()
    ends = month_ends(check)
    ew = ew_bank_holidays(check)
    tgt = tgt_closing_days(check)
    tokyo = tokyo_business_days(check)
    events = gotobi_or_tokyo_month_end(check)
    t_l = clock_t_l(check)
    t_e = clock_t_e(check, t_l)
    t_t = clock_t_t(check, tokyo)
    assert set(full) <= {d for d, _ in t_l}  # every full session has its clocks
    cal_sources = [(FX_CALENDAR_FILE, sha256_of(FX_CALENDAR_FILE)),
                   (SESSIONS_FILE, sha256_of(SESSIONS_FILE)), (CHECK_FILE, CHECK_SHA256)]
    calendar_text = "\n\n".join([
        CALENDAR_DOC, "from __future__ import annotations",
        "# sha256 of each source file when the tables were generated\n"
        + render_sources(cal_sources),
        f'EC_CAL_COVERAGE = ("{CAL_FIRST.isoformat()}", "{CAL_LAST.isoformat()}")\n'
        f'TOKYO_RANGE = ("{CLOCK_FIRST.isoformat()}", "{CLOCK_LAST.isoformat()}")',
        render_dates("FX_FULL_SESSIONS", full, "ISO trade dates, oldest first"),
        render_dates("FX_EARLY_F_DATES", early_f, "no early_halt_ct, engine F before 15:08 CT"),
        render_pairs("MONTH_ENDS", ends, "(YYYY-MM, ME(m)), oldest first"),
        render_dates("EW_BANK_HOLIDAYS", ew, "England and Wales"),
        render_dates("TGT_CLOSING_DAYS", tgt, "TARGET closing days"),
        render_dates("TOKYO_BUSINESS_DAYS", tokyo, "EC-JP"),
        render_dates("GOTOBI_OR_TOKYO_MONTH_END", events, "the tkypre event dates before C4"),
    ]) + "\n"
    clocks_text = "\n\n".join([
        CLOCKS_DOC, "from __future__ import annotations",
        "# sha256 of each source file when the tables were generated\n"
        + render_sources([(CHECK_FILE, CHECK_SHA256)]),
        f'CLOCK_RANGE = ("{CLOCK_FIRST.isoformat()}", "{CLOCK_LAST.isoformat()}")',
        render_pairs("T_L", t_l, "(weekday d, CT HH:MM on d)"),
        render_pairs("T_E", t_e, "(weekday d, CT HH:MM on d)"),
        render_pairs("T_T", t_t, "(Tokyo business day d, CT HH:MM on calendar day d-1)"),
    ]) + "\n"
    return {CALENDAR_OUT: calendar_text, CLOCKS_OUT: clocks_text}


def main() -> None:
    texts = build()
    for rel, text in texts.items():
        (REPO_ROOT / rel).write_text(text, encoding="utf-8")
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        print(f"wrote {rel}: {text.count(chr(10))} lines, sha256 {digest[:12]}")
    _full, early_f = fx_full_sessions()
    print(f"K3-L-11 removes {len(early_f)} dates: {', '.join(early_f)}")


if __name__ == "__main__":
    main()
