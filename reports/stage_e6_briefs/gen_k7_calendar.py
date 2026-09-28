"""One-off generator of strategy/members/k7/_calendar.py (Stage E.6 Task 2, MemberCoder-B).

Not imported by any member. Run from the repository root:

    uv run python reports/stage_e6_briefs/gen_k7_calendar.py

Sources (reports/stage_e6_member_specs.md S0.8, S0.11, K7-L-02, K7-L-03, K7-L-04):
- EC-CAL, the D10 crypto calendar: data.group_session.load_group_calendar("crypto")
  (data/calendars/crypto.py), coverage 2019-05-01..2026-06-19 (K4-L-13), and the engine's F,
  rules.sessions.flatten_time_ct("MBT", d) (K3-L-11);
- the two Databento GLBX.MDP3 condition files under data/vendor/databento/condition/, read with
  data/build_bars.py's filter (degraded_days: every entry whose condition is not "available")
  and its trade-date mapping (lines 685-687 and 728: a trade date whose ISO date is a degraded
  UTC date); the research-window result is checked against reports/stage_e2a_bars.json
  products/MBT/degraded/on_research_trade_dates;
- England-and-Wales bank holidays: the ec_ew rows of reports/stage_e4c_release_check.json (K3's
  EW_BANK_HOLIDAYS source);
- US federal holidays by the OPM rules (5 U.S.C. 6103: fixed-date holidays observed on the Friday
  before a Saturday and the Monday after a Sunday; Juneteenth from 2021), plus Good Friday
  (catalog C9 lines 183-184);
- zoneinfo for T_exp = 16:00 Europe/London on d, in America/Chicago (C9 lines 181-182).

Tables written (S0.11):
- CRYPTO_FULL_SESSIONS: EC-CAL crypto trade dates 2019-05-01..2026-06-19 with no early halt AND
  the regular engine F (15:08 CT) on CT date d (K7-L-02). CRYPTO_EARLY_F_DATES lists the dates the
  F test alone removes.
- VENDOR_DEGRADED: EC-CAL crypto trade dates 2019-05-01..2026-06-19 whose ISO date is a degraded
  UTC date of either condition file (K7-L-03).
- MBTX: (d, T_exp "HH:MM" CT) for every MBT last trading day 2021-05..2026-06, by the rule quoted
  in C9 lines 176-180 (K7-L-04), less the two rows lead ruling R-1b-1 drops (22:00 PDT, from
  reports/stage_e6_release_check.md item A): 2021-12-30 and 2025-12-24, where CME's calendar gives
  2021-12-31 and 2025-12-26; dropped, not replaced. MBTX_UNVERIFIED lists, for the record only, the
  research-window rows the check could not verify (its "unverifiable" verdicts); no member reads it.
- the Task 1b check itself, reports/stage_e6_release_check.json (sha256 pinned): its rule rows
  (item A) must equal this script's, and its CME mismatches must be exactly the two drops.

Every table is checked against the catalog's C9 known answers and the E.2a bar report before
anything is written. tests/test_k7_members_events.py recomputes every table from the sources and
asserts that the module is exactly this script's output.
"""

from __future__ import annotations

import calendar
import hashlib
import json
import sys
import textwrap
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from data.build_bars import degraded_days  # noqa: E402
from data.group_session import load_group_calendar, trade_dates_between  # noqa: E402
from rules import sessions  # noqa: E402
from rules.products import product  # noqa: E402

OUT = "strategy/members/k7/_calendar.py"
CRYPTO_CALENDAR_FILE = "data/calendars/crypto.py"
SESSIONS_FILE = "rules/sessions.py"
CONDITION_FILES = (
    "data/vendor/databento/condition/GLBX.MDP3_2019-04-01_2025-04-01.json",
    "data/vendor/databento/condition/GLBX.MDP3_2025-04-01_2026-09-16.json",
)
EW_CHECK_FILE = "reports/stage_e4c_release_check.json"
EW_CHECK_SHA256 = "c63c13a69559c90efdb72969e20244a261343839660436082fcaf44a35f931e9"
E2A_BARS_FILE = "reports/stage_e2a_bars.json"
ROOT = "MBT"
REGULAR_F = time(15, 8)  # D6 crypto row; rules.sessions.REGULAR_FLATTEN_CT["crypto"]
CAL_FIRST, CAL_LAST = date(2019, 5, 1), date(2026, 6, 19)  # EC-CAL crypto coverage (K4-L-13)
RESEARCH_FIRST, RESEARCH_LAST = date(2025, 4, 1), date(2026, 6, 19)  # the research window
MBTX_FIRST_MONTH, MBTX_LAST_MONTH = (2021, 5), (2026, 6)  # K7-L-04
CONFIRMATION_FIRST, CONFIRMATION_LAST = date(2021, 5, 3), date(2024, 2, 29)  # C9
FRIDAY = 4
MONDAY, THURSDAY = 0, 3
SATURDAY, SUNDAY = 5, 6
JUNETEENTH_FROM = 2021  # 5 U.S.C. 6103 as amended 17 June 2021
LONDON, CHICAGO = ZoneInfo("Europe/London"), ZoneInfo("America/Chicago")
T_EXP_LONDON = time(16, 0)
# Spec (reports/stage_e6_member_specs.md) header: EC-CAL research-window early halts.
SPEC_RESEARCH_HALTS = ("2025-07-04", "2025-11-28", "2025-12-24", "2026-04-03")
# C9 lines 186-190: the research-window dates by the rule and the two 11:00 CT rows.
C9_RESEARCH_MBTX = (
    "2025-04-25", "2025-05-30", "2025-06-27", "2025-07-25", "2025-08-29", "2025-09-26",
    "2025-10-31", "2025-11-28", "2025-12-24", "2026-01-30", "2026-02-27", "2026-03-27",
    "2026-04-24", "2026-05-29")
C9_RESEARCH_1100 = ("2025-10-31", "2026-03-27")
C9_CONFIRMATION = {"count": 34, "first": "2021-05-28", "last": "2024-02-23",
                   "thursday": "2021-12-30", "at_1100": "2022-03-25"}
# Lead ruling R-1b-1 (spec section 9): rule rows dropped, not replaced -> CME's date.
MBTX_DROPS: dict[str, str] = {"2021-12-30": "2021-12-31", "2025-12-24": "2025-12-26"}
CHECK_FILE = "reports/stage_e6_release_check.json"
CHECK_SHA256 = "6481913c3c8ed4651327c1f90fdf15a72843c5341560495f91786a4103135aee"
UNVERIFIED_COUNT = 10  # R-1b-1: "the 10 unverifiable research rows"
DATES_PER_LINE = 5
PAIRS_PER_LINE = 3
COMMENT_WIDTH = 96


# ------------------------------------------------------------------------ helpers ----
def sha256_of(rel: str) -> str:
    return hashlib.sha256((REPO_ROOT / rel).read_bytes()).hexdigest()


def load_json(rel: str) -> object:
    return json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))


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


def nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    first = date(year, month, 1)
    return first + timedelta(days=(weekday - first.weekday()) % 7 + 7 * (n - 1))


def last_weekday(year: int, month: int, weekday: int) -> date:
    last = date(year, month, calendar.monthrange(year, month)[1])
    return last - timedelta(days=(last.weekday() - weekday) % 7)


def observed(day: date) -> date:
    """OPM: a Saturday holiday is observed the Friday before, a Sunday one the Monday after."""
    if day.weekday() == SATURDAY:
        return day - timedelta(days=1)
    if day.weekday() == SUNDAY:
        return day + timedelta(days=1)
    return day


def us_federal_holidays(year: int) -> set[date]:
    """The observed dates of the year's 5 U.S.C. 6103 holidays (New Year's Day of ``year``
    may be observed on 31 December of ``year - 1``)."""
    fixed = [date(year, 1, 1), date(year, 7, 4), date(year, 11, 11), date(year, 12, 25)]
    if year >= JUNETEENTH_FROM:
        fixed.append(date(year, 6, 19))
    floating = [nth_weekday(year, 1, MONDAY, 3), nth_weekday(year, 2, MONDAY, 3),
                last_weekday(year, 5, MONDAY), nth_weekday(year, 9, MONDAY, 1),
                nth_weekday(year, 10, MONDAY, 2), nth_weekday(year, 11, THURSDAY, 4)]
    return {observed(d) for d in fixed} | set(floating)


def months(first: tuple[int, int], last: tuple[int, int]) -> list[tuple[int, int]]:
    out, (y, m) = [], first
    while (y, m) <= last:
        out.append((y, m))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


# ----------------------------------------------------------------------- calendar ----
def crypto_full_sessions() -> tuple[list[str], list[str]]:
    """(CRYPTO_FULL_SESSIONS, the dates the F test alone removes)."""
    cal = load_group_calendar("crypto")
    assert tuple(cal.coverage) == (CAL_FIRST, CAL_LAST), cal.coverage  # K4-L-13
    assert product(ROOT).group == "crypto"
    assert sessions.REGULAR_FLATTEN_CT["crypto"] == REGULAR_F
    full: list[str] = []
    early_f: list[str] = []
    for d in trade_dates_between(cal, CAL_FIRST, CAL_LAST):
        if cal.early_halt_ct(d) is not None:
            continue
        (full if sessions.flatten_time_ct(ROOT, d) == REGULAR_F else early_f).append(d.isoformat())
    halts = [d.isoformat() for d in trade_dates_between(cal, RESEARCH_FIRST, RESEARCH_LAST)
             if cal.early_halt_ct(d) is not None]
    assert tuple(halts) == SPEC_RESEARCH_HALTS, halts
    # S0.8: in the research window the two tests agree on every trade date
    assert not [d for d in early_f if RESEARCH_FIRST.isoformat() <= d <= RESEARCH_LAST.isoformat()]
    return full, early_f


def vendor_degraded() -> tuple[list[str], list[str]]:
    """(VENDOR_DEGRADED, the degraded UTC dates that are not crypto trade dates)."""
    degraded: set[str] = set()
    for rel in CONDITION_FILES:
        rows = load_json(rel)
        assert isinstance(rows, list)
        mine = [r for r in rows if r["condition"] != "available"]
        assert mine == degraded_days(REPO_ROOT / rel)  # build_bars.py's filter
        degraded |= {str(r["date"]) for r in mine}
    cal = load_group_calendar("crypto")
    trade_iso = {d.isoformat() for d in trade_dates_between(cal, CAL_FIRST, CAL_LAST)}
    table = sorted(trade_iso & degraded)  # build_bars.py lines 685-687
    in_range = {d for d in degraded if CAL_FIRST.isoformat() <= d <= CAL_LAST.isoformat()}
    not_trade = sorted(in_range - trade_iso)
    bars = load_json(E2A_BARS_FILE)
    assert isinstance(bars, dict)
    mbt = bars["products"][ROOT]["degraded"]
    assert mbt["condition_file"] == CONDITION_FILES[1]
    research = [d for d in table if RESEARCH_FIRST.isoformat() <= d <= RESEARCH_LAST.isoformat()]
    assert research == mbt["on_research_trade_dates"], research
    return table, not_trade


def ew_bank_holidays() -> set[date]:
    data = (REPO_ROOT / EW_CHECK_FILE).read_bytes()
    assert hashlib.sha256(data).hexdigest() == EW_CHECK_SHA256, "EW source changed"
    rows = json.loads(data)["ec_ew"]
    days = {date.fromisoformat(r["date"]) for r in rows}
    assert len(days) == len(rows) == 63 and all(d.weekday() < SATURDAY for d in days)
    return days


def mbtx() -> tuple[list[tuple[str, str]], list[str]]:
    """(the rule's rows, the rows not on the last Friday of their month), before R-1b-1."""
    ew = ew_bank_holidays()
    years = range(MBTX_FIRST_MONTH[0], MBTX_LAST_MONTH[0] + 2)
    us = set().union(*(us_federal_holidays(y) for y in years))
    good_fridays = {easter(y) - timedelta(days=2) for y in years}
    assert min(ew) <= date(*MBTX_FIRST_MONTH, 1) and max(ew).year == MBTX_LAST_MONTH[0]

    def business_both(d: date) -> bool:
        return d.weekday() < SATURDAY and d not in ew and d not in us and d not in good_fridays

    rows: list[tuple[str, str]] = []
    moved: list[str] = []
    for y, m in months(MBTX_FIRST_MONTH, MBTX_LAST_MONTH):
        d = last_weekday(y, m, FRIDAY)
        last_friday = d
        while not business_both(d):
            d -= timedelta(days=1)
        local = datetime.combine(d, T_EXP_LONDON, tzinfo=LONDON).astimezone(CHICAGO)
        assert local.date() == d
        rows.append((d.isoformat(), f"{local:%H:%M}"))
        if d != last_friday:
            moved.append(d.isoformat())
    assert {t for _, t in rows} == {"10:00", "11:00"}
    research = [r for r in rows if RESEARCH_FIRST.isoformat() <= r[0] <= RESEARCH_LAST.isoformat()]
    assert tuple(d for d, _ in research) == C9_RESEARCH_MBTX, research
    assert tuple(d for d, t in research if t == "11:00") == C9_RESEARCH_1100
    conf = [r for r in rows
            if CONFIRMATION_FIRST.isoformat() <= r[0] <= CONFIRMATION_LAST.isoformat()]
    assert len(conf) == C9_CONFIRMATION["count"]
    assert (conf[0][0], conf[-1][0]) == (C9_CONFIRMATION["first"], C9_CONFIRMATION["last"])
    by_day = dict(rows)
    assert date.fromisoformat(C9_CONFIRMATION["thursday"]).weekday() == THURSDAY
    assert C9_CONFIRMATION["thursday"] in by_day and by_day[C9_CONFIRMATION["at_1100"]] == "11:00"
    return rows, moved


def load_check() -> dict:
    data = (REPO_ROOT / CHECK_FILE).read_bytes()
    assert hashlib.sha256(data).hexdigest() == CHECK_SHA256, "Task 1b check changed"
    return json.loads(data)


def apply_rulings(rows: list[tuple[str, str]]) -> tuple[list[tuple[str, str]],
                                                         list[tuple[str, str]]]:
    """R-1b-1: (MBTX less the two drops, MBTX_UNVERIFIED). The check's rule rows must be this
    script's rule rows, and its CME mismatches exactly the two drops."""
    check = load_check()
    theirs = [(r["month"], r["rule_both_date"], r["texp_ct_both"])
              for r in check["rule_rows_2021_05_2026_06"]]
    assert theirs == [(d[:7], d, t) for d, t in rows], "the check's rule rows differ"
    assert all(check["rule_reproduction_of_catalog"][k] for k in (
        "research_matches_catalog", "has_2021_12_30", "has_2022_03_25"))
    mismatches = {m["rule_both_date"]: m["cme_lastTrade"]
                  for m in check["A_all_cme_points_2021_05_2026_06_record_only"]["mismatches"]}
    assert mismatches == MBTX_DROPS, mismatches
    research = check["A_ec_mbtx_research"]["rows"]
    drops = {r["rule_date"]: r["cme_date"] for r in research if r["verdict"] == "drop"}
    assert drops == {d: c for d, c in MBTX_DROPS.items() if d >= RESEARCH_FIRST.isoformat()}
    unverified = [(r["rule_date"], r["texp_ct"]) for r in research
                  if r["verdict"] == "unverifiable" and not r["after_window_record_only"]]
    assert len(unverified) == UNVERIFIED_COUNT == check["A_ec_mbtx_research"]["counts"][
        "unverifiable"]
    kept = [(d, t) for d, t in rows if d not in MBTX_DROPS]
    assert len(kept) == len(rows) - len(MBTX_DROPS) and set(unverified) <= set(kept)
    return kept, unverified


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


DOC = '''"""K7 calendar tables (literal; reports/stage_e6_member_specs.md S0.8, S0.11, K7-L-02,
K7-L-03, K7-L-04).

GENERATED by reports/stage_e6_briefs/gen_k7_calendar.py. Do not edit by hand:
tests/test_k7_members_events.py recomputes every table from its sources and asserts this file is
the generator's output. Members read these tuples; nothing here is computed at run time.

- CRYPTO_FULL_SESSIONS (K7-L-02): EC-CAL crypto trade dates (data.group_session.
  load_group_calendar("crypto"), data/calendars/crypto.py) of the coverage 2019-05-01..2026-06-19
  (K4-L-13) with no early halt AND the regular engine F of 15:08 CT on CT date d
  (rules.sessions.flatten_time_ct("MBT", d); K3-L-11). A booked-forward weekday is not a trade
  date and is not listed.
- CRYPTO_EARLY_F_DATES: the trade dates without an early halt whose engine F is early; the F test
  alone removes them from CRYPTO_FULL_SESSIONS (information only).
- VENDOR_DEGRADED (K7-L-03): the crypto trade dates of the same range whose ISO date is a
  degraded UTC date (condition not "available") of either Databento GLBX.MDP3 condition file,
  by data/build_bars.py's mapping.
- MBTX (K7-L-04): (d, T_exp as CT "HH:MM") for every MBT last trading day 2021-05..2026-06: the
  last Friday of the month, or the preceding day that is a business day in both the UK
  (England-and-Wales bank holidays, reports/stage_e4c_release_check.json ec_ew) and the US (US
  federal holidays, observed dates by the OPM rules, plus Good Friday); T_exp = 16:00
  Europe/London on d in America/Chicago (zoneinfo, at generation), less the two rows lead
  ruling R-1b-1 drops (2021-12-30, 2025-12-24: CME's calendar gives another day). Other rows
  before the research window are the rule's output, unchecked (K4-L-01).
- MBTX_UNVERIFIED: the research-window MBTX rows the Task 1b check (reports/
  stage_e6_release_check.json) could not verify against CME; for the record only, no member
  reads it.
"""'''


def comments(early_f: list[str], not_trade: list[str], moved: list[str]) -> str:
    drops = ", ".join(f"{d} (CME {c})" for d, c in sorted(MBTX_DROPS.items()))
    paragraphs = [
        f"The F test alone removes: {', '.join(early_f) or 'none'} (no early halt, engine F "
        "earlier than 15:08 CT; outside the research window, where the two tests agree).",
        "Degraded UTC dates in the coverage that are not crypto trade dates (not listed): "
        f"{', '.join(not_trade)}.",
        f"MBTX rows the holiday test moves off the month's last Friday: {', '.join(moved)}.",
        "R-1b-1: CME's rule now reads 'either', the catalog's 'both' wording gives a non-final "
        f"day; dropped, not replaced: {drops}. Every other row is the rule's output; "
        "MBTX_UNVERIFIED (record only, read by no member) lists the research-window rows the "
        "Task 1b check could not verify.",
    ]
    return "\n".join("# " + line for text in paragraphs
                     for line in textwrap.wrap(text, COMMENT_WIDTH))


def build() -> dict[str, str]:
    """{repository path: module text} of the generated module."""
    full, early_f = crypto_full_sessions()
    degraded, not_trade = vendor_degraded()
    rule_rows, moved = mbtx()
    rows, unverified = apply_rulings(rule_rows)
    sources = [(CRYPTO_CALENDAR_FILE, sha256_of(CRYPTO_CALENDAR_FILE)),
               (SESSIONS_FILE, sha256_of(SESSIONS_FILE)),
               *((rel, sha256_of(rel)) for rel in CONDITION_FILES),
               (EW_CHECK_FILE, EW_CHECK_SHA256),
               (CHECK_FILE, CHECK_SHA256),
               (E2A_BARS_FILE, sha256_of(E2A_BARS_FILE))]
    text = "\n\n".join([
        DOC, "from __future__ import annotations",
        "# sha256 of each source file when the tables were generated\n" + render_sources(sources),
        f'EC_CAL_COVERAGE = ("{CAL_FIRST.isoformat()}", "{CAL_LAST.isoformat()}")\n'
        f'MBTX_MONTHS = ("{MBTX_FIRST_MONTH[0]:04d}-{MBTX_FIRST_MONTH[1]:02d}", '
        f'"{MBTX_LAST_MONTH[0]:04d}-{MBTX_LAST_MONTH[1]:02d}")',
        comments(early_f, not_trade, moved),
        render_dates("CRYPTO_FULL_SESSIONS", full, "ISO trade dates, oldest first"),
        render_dates("CRYPTO_EARLY_F_DATES", early_f, "no early halt, engine F before 15:08 CT"),
        render_dates("VENDOR_DEGRADED", degraded, "ISO trade dates, oldest first"),
        render_pairs("MBTX", rows, "(last trading day d, T_exp CT HH:MM on d), oldest first"),
        render_pairs("MBTX_UNVERIFIED", unverified,
                     "research-window MBTX rows the Task 1b check could not verify; record only"),
    ]) + "\n"
    return {OUT: text}


def main() -> None:
    for rel, text in build().items():
        (REPO_ROOT / rel).write_text(text, encoding="utf-8")
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        print(f"wrote {rel}: {text.count(chr(10))} lines, sha256 {digest[:12]}")


if __name__ == "__main__":
    main()
