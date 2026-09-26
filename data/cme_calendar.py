"""CME Globex holiday calendar for equity index futures (MES/ES), 2019-2026.

2019-2024 (Stage D.1f Task 3b) comes first in ``_ENTRIES``; the 2025-2026 entry lines below
it are byte-identical to commit 9cbd815 (``ENTRIES_2025_2026_SHA256``). Each 2019-2024 entry
cites its source verbatim in ``SOURCES_2019_2024`` (from reports/stage_d1f_calendar_sources.json,
71 extracted rows: 68 entries plus 3 CME-direct NORMAL days in
``NO_ENTRY_FINDINGS_2019_2024``). 2019-2024 grades:
- status (``evidence``): ``cme`` (a CME settlement-times PDF or clearing advisory),
  ``secondary`` (Thanksgiving Day 2019-2021: a generic 2026 broker page), ``unverified``
  (New Year's Day 2021: not fetched, assumed from the pattern of the other years).
- time (``time_evidence``): holiday 12:00 CT halts are ``secondary`` (the generic 2026
  crosstrade.io page; CME's PDFs say only that no settlement is derived); every 12:15 CT
  early close is ``inferred`` from CME's 12:00 CT equity settlement line, the convention the
  2025 entries use and the 2025 bars confirmed (07-03, 11-28, 12-24); Good Friday 2023 08:15
  CT is ``secondary`` (AMP); Good Friday 2021 08:15 CT is ``unverified``.
Every 2019-2024 entry inside the confirmation bars is tested by the step-4b validator
(``data.validate.validate_calendar_step4b``) in the run session, before step 5; the calendar
is immutable once step 7 starts (reports/stage_d1f_confirmation_list.md 1.5, 5.3).

The notes below describe the 2025-2026 compilation (unchanged).

Closes the gap documented in MLCryptoEngine's session calendar, which had no
holiday handling. Compiled 2026-09-16 from CME Group's own publications, NOT
from the NYSE calendar — CME differs: most US holidays keep equity futures
trading on Globex with an early 12:00 CT halt, Good Friday 2026 had an
abbreviated session for the jobs report, and the day before/after some
holidays closes at 12:15 CT.

Evidence grades per entry (``evidence``):
- ``cme``: the day's status (closure / no settlement / early equity
  settlement) is stated by a CME-direct source: the holiday settlement-times
  PDFs at cmegroup.com/tools-information/holiday-calendar/files/{2025,2026}/,
  CME press release 2024-12-30 (Day of Mourning), clearing notice 25-012,
  and the 2026 Good Friday clearing advisory. cmegroup.com blocks automated
  fetches, so these were read through Wayback Machine copies.
- ``secondary``: the exact halt/close clock time comes from broker schedules
  (AMP Futures, CrossTrade, DiscountTrading) quoting CME; CME's own Globex
  hours table was not retrievable. Topstep's holiday article (2026-09-01)
  independently implies the same 12:00 / 12:15 CT times for Nov 26-27 and
  Dec 24 2026 (its flatten times are 15 minutes earlier).
- ``inferred``: 12:15 CT close inferred from CME's 12:00 CT equity
  settlement on that date, consistent with brokers.

Every entry inside the pulled bar window (2025-04-01..2026-09-16) is
additionally checked EMPIRICALLY against the MES 1-minute bars by
``data.validate`` (last traded minute before the halt, no bars inside the
closure); results are in reports/bar_validation.md. Unconfirmed items are
listed there too — notably the Good Friday 2026 close time (08:15 CT per AMP,
~09:15 CT per another secondary source).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, time
from enum import Enum

EARLY_HALT_NOON = time(12, 0)
EARLY_CLOSE_1215 = time(12, 15)


class HolidayKind(Enum):
    FULL_CLOSURE = "full_closure"  # no Globex session for this calendar day
    EARLY_HALT = "early_halt"  # trading stops at halt_ct; normal 17:00 CT reopen


@dataclass(frozen=True)
class Holiday:
    day: date
    name: str
    kind: HolidayKind
    halt_ct: time | None
    evidence: str  # status grade: "cme" (all 2025-2026) | "secondary" | "unverified"
    time_evidence: str  # "cme" | "empirical" | "secondary" | "inferred" | "unverified" | "n/a"


def _closure(day: date, name: str) -> Holiday:
    return Holiday(day, name, HolidayKind.FULL_CLOSURE, None, "cme", "n/a")


def _halt(day: date, name: str, at: time, time_evidence: str) -> Holiday:
    return Holiday(day, name, HolidayKind.EARLY_HALT, at, "cme", time_evidence)


def _closure_graded(day: date, name: str, evidence: str) -> Holiday:
    """A 2019-2024 closure whose status grade is not necessarily ``cme``."""
    return Holiday(day, name, HolidayKind.FULL_CLOSURE, None, evidence, "n/a")


def _halt_graded(day: date, name: str, at: time, evidence: str, time_evidence: str) -> Holiday:
    """A 2019-2024 early halt with its own status and time grades."""
    return Holiday(day, name, HolidayKind.EARLY_HALT, at, evidence, time_evidence)


_ENTRIES: tuple[Holiday, ...] = (
    # ---- 2019 (sources: SOURCES_2019_2024)
    _closure_graded(date(2019, 1, 1), "New Year's Day", "cme"),
    _halt_graded(
        date(2019, 1, 21), "Martin Luther King Jr. Day", EARLY_HALT_NOON, "cme", "secondary"
    ),
    _halt_graded(date(2019, 2, 18), "Presidents Day", EARLY_HALT_NOON, "cme", "secondary"),
    _closure_graded(date(2019, 4, 19), "Good Friday", "cme"),
    _halt_graded(date(2019, 5, 27), "Memorial Day", EARLY_HALT_NOON, "cme", "secondary"),
    # Time upgraded to cme 2026-09-25, Stage E.2a (design D14): CME Globex schedule, 12:15 CT.
    _halt_graded(
        date(2019, 7, 3), "Day before Independence Day", EARLY_CLOSE_1215, "cme", "cme"
    ),
    # Corrected 2026-09-23, Stage D.1f run step 4b: CME Globex schedule, 12:00 CT halt.
    _halt_graded(date(2019, 7, 4), "Independence Day", EARLY_HALT_NOON, "cme", "cme"),
    _halt_graded(date(2019, 9, 2), "Labor Day", EARLY_HALT_NOON, "cme", "secondary"),
    _halt_graded(date(2019, 11, 28), "Thanksgiving Day", EARLY_HALT_NOON, "secondary", "secondary"),
    _halt_graded(date(2019, 11, 29), "Day after Thanksgiving", EARLY_CLOSE_1215, "cme", "inferred"),
    _halt_graded(date(2019, 12, 24), "Christmas Eve", EARLY_CLOSE_1215, "cme", "inferred"),
    _closure_graded(date(2019, 12, 25), "Christmas Day", "cme"),
    # ---- 2020 (sources: SOURCES_2019_2024)
    _closure_graded(date(2020, 1, 1), "New Year's Day", "cme"),
    _halt_graded(
        date(2020, 1, 20), "Martin Luther King Jr. Day", EARLY_HALT_NOON, "cme", "secondary"
    ),
    _halt_graded(date(2020, 2, 17), "Presidents Day", EARLY_HALT_NOON, "cme", "secondary"),
    _closure_graded(date(2020, 4, 10), "Good Friday", "cme"),
    _halt_graded(date(2020, 5, 25), "Memorial Day", EARLY_HALT_NOON, "cme", "secondary"),
    # Corrected 2026-09-23, Stage D.1f run step 4b: CME Globex schedule, 12:00 CT halt.
    _halt_graded(date(2020, 7, 3), "Independence Day (observed)", EARLY_HALT_NOON, "cme", "cme"),
    _halt_graded(date(2020, 9, 7), "Labor Day", EARLY_HALT_NOON, "cme", "secondary"),
    _halt_graded(date(2020, 11, 26), "Thanksgiving Day", EARLY_HALT_NOON, "secondary", "secondary"),
    _halt_graded(date(2020, 11, 27), "Day after Thanksgiving", EARLY_CLOSE_1215, "cme", "inferred"),
    _halt_graded(date(2020, 12, 24), "Christmas Eve", EARLY_CLOSE_1215, "cme", "inferred"),
    _closure_graded(date(2020, 12, 25), "Christmas Day", "cme"),
    # ---- 2021 (sources: SOURCES_2019_2024)
    _closure_graded(date(2021, 1, 1), "New Year's Day", "unverified"),
    _halt_graded(
        date(2021, 1, 18), "Martin Luther King Jr. Day", EARLY_HALT_NOON, "cme", "secondary"
    ),
    _halt_graded(date(2021, 2, 15), "Presidents Day", EARLY_HALT_NOON, "cme", "secondary"),
    _halt_graded(
        date(2021, 4, 2), "Good Friday (abbreviated, jobs report)", time(8, 15), "cme", "unverified"
    ),
    _halt_graded(date(2021, 5, 31), "Memorial Day", EARLY_HALT_NOON, "cme", "secondary"),
    # Corrected 2026-09-23, Stage D.1f run step 4b: CME Globex schedule, 12:00 CT halt.
    _halt_graded(date(2021, 7, 5), "Independence Day (observed)", EARLY_HALT_NOON, "cme", "cme"),
    _halt_graded(date(2021, 9, 6), "Labor Day", EARLY_HALT_NOON, "cme", "secondary"),
    _halt_graded(date(2021, 11, 25), "Thanksgiving Day", EARLY_HALT_NOON, "secondary", "secondary"),
    _halt_graded(date(2021, 11, 26), "Day after Thanksgiving", EARLY_CLOSE_1215, "cme", "inferred"),
    _closure_graded(date(2021, 12, 24), "Christmas Day (observed)", "cme"),
    # ---- 2022 (sources: SOURCES_2019_2024)
    _halt_graded(
        date(2022, 1, 17), "Martin Luther King Jr. Day", EARLY_HALT_NOON, "cme", "secondary"
    ),
    _halt_graded(date(2022, 2, 21), "Presidents Day", EARLY_HALT_NOON, "cme", "secondary"),
    _closure_graded(date(2022, 4, 15), "Good Friday", "cme"),
    _halt_graded(date(2022, 5, 30), "Memorial Day", EARLY_HALT_NOON, "cme", "secondary"),
    _halt_graded(date(2022, 6, 20), "Juneteenth (observed)", EARLY_HALT_NOON, "cme", "secondary"),
    # Corrected 2026-09-23, Stage D.1f run step 4b: CME Globex schedule, 12:00 CT halt.
    _halt_graded(date(2022, 7, 4), "Independence Day", EARLY_HALT_NOON, "cme", "cme"),
    _halt_graded(date(2022, 9, 5), "Labor Day", EARLY_HALT_NOON, "cme", "secondary"),
    _halt_graded(date(2022, 11, 24), "Thanksgiving Day", EARLY_HALT_NOON, "cme", "secondary"),
    _halt_graded(date(2022, 11, 25), "Day after Thanksgiving", EARLY_CLOSE_1215, "cme", "inferred"),
    _closure_graded(date(2022, 12, 26), "Christmas Day (observed)", "cme"),
    # ---- 2023 (sources: SOURCES_2019_2024)
    _closure_graded(date(2023, 1, 2), "New Year's Day (observed)", "cme"),
    _halt_graded(
        date(2023, 1, 16), "Martin Luther King Jr. Day", EARLY_HALT_NOON, "cme", "secondary"
    ),
    _halt_graded(date(2023, 2, 20), "Presidents Day", EARLY_HALT_NOON, "cme", "secondary"),
    _halt_graded(
        date(2023, 4, 7), "Good Friday (abbreviated, jobs report)", time(8, 15), "cme", "secondary"
    ),
    _halt_graded(date(2023, 5, 29), "Memorial Day", EARLY_HALT_NOON, "cme", "secondary"),
    _halt_graded(date(2023, 6, 19), "Juneteenth", EARLY_HALT_NOON, "cme", "secondary"),
    # Time upgraded to cme 2026-09-25, Stage E.2a (design D14): CME holiday summary, 12:15 CT.
    _halt_graded(
        date(2023, 7, 3), "Day before Independence Day", EARLY_CLOSE_1215, "cme", "cme"
    ),
    # Corrected 2026-09-23, Stage D.1f run step 4b: CME Globex schedule, 12:00 CT halt.
    _halt_graded(date(2023, 7, 4), "Independence Day", EARLY_HALT_NOON, "cme", "cme"),
    _halt_graded(date(2023, 9, 4), "Labor Day", EARLY_HALT_NOON, "cme", "secondary"),
    _halt_graded(date(2023, 11, 23), "Thanksgiving Day", EARLY_HALT_NOON, "cme", "secondary"),
    _halt_graded(date(2023, 11, 24), "Day after Thanksgiving", EARLY_CLOSE_1215, "cme", "inferred"),
    _closure_graded(date(2023, 12, 25), "Christmas Day", "cme"),
    # ---- 2024 (sources: SOURCES_2019_2024)
    _closure_graded(date(2024, 1, 1), "New Year's Day (observed)", "cme"),
    _halt_graded(
        date(2024, 1, 15), "Martin Luther King Jr. Day", EARLY_HALT_NOON, "cme", "secondary"
    ),
    _halt_graded(date(2024, 2, 19), "Presidents Day", EARLY_HALT_NOON, "cme", "secondary"),
    _closure_graded(date(2024, 3, 29), "Good Friday", "cme"),
    _halt_graded(date(2024, 5, 27), "Memorial Day", EARLY_HALT_NOON, "cme", "secondary"),
    _halt_graded(date(2024, 6, 19), "Juneteenth", EARLY_HALT_NOON, "cme", "secondary"),
    _halt_graded(
        date(2024, 7, 3), "Day before Independence Day", EARLY_CLOSE_1215, "cme", "inferred"
    ),
    # Corrected 2026-09-25, Stage E.2a (design D10, D14): CME trading-hours service, 12:00 CT halt.
    _halt_graded(date(2024, 7, 4), "Independence Day", EARLY_HALT_NOON, "cme", "cme"),
    _halt_graded(date(2024, 9, 2), "Labor Day", EARLY_HALT_NOON, "cme", "secondary"),
    _halt_graded(date(2024, 11, 28), "Thanksgiving Day", EARLY_HALT_NOON, "cme", "secondary"),
    _halt_graded(date(2024, 11, 29), "Day after Thanksgiving", EARLY_CLOSE_1215, "cme", "inferred"),
    _halt_graded(date(2024, 12, 24), "Christmas Eve", EARLY_CLOSE_1215, "cme", "inferred"),
    _closure_graded(date(2024, 12, 25), "Christmas Day", "cme"),
    # ---- 2025
    _closure(date(2025, 1, 1), "New Year's Day"),
    _halt(date(2025, 1, 9), "National Day of Mourning (Carter)", time(8, 30), "cme"),
    _halt(date(2025, 1, 20), "Martin Luther King Jr. Day", EARLY_HALT_NOON, "secondary"),
    _halt(date(2025, 2, 17), "Presidents Day", EARLY_HALT_NOON, "secondary"),
    _closure(date(2025, 4, 18), "Good Friday"),
    _halt(date(2025, 5, 26), "Memorial Day", EARLY_HALT_NOON, "secondary"),
    _halt(date(2025, 6, 19), "Juneteenth", EARLY_HALT_NOON, "secondary"),
    _halt(date(2025, 7, 3), "Day before Independence Day", EARLY_CLOSE_1215, "inferred"),
    # Corrected 2026-09-16 from the bars: CME publishes "no settlement" for
    # 2025-07-04, which research first read as a full closure. MES 1-minute
    # bars show Globex trading Thu 17:00 CT -> Fri 11:59 CT (1,140 bars), i.e.
    # an early 12:00 CT halt with the trade date combined, like other holidays.
    _halt(date(2025, 7, 4), "Independence Day", EARLY_HALT_NOON, "empirical"),
    _halt(date(2025, 9, 1), "Labor Day", EARLY_HALT_NOON, "secondary"),
    _halt(date(2025, 11, 27), "Thanksgiving", EARLY_HALT_NOON, "secondary"),
    _halt(date(2025, 11, 28), "Day after Thanksgiving", EARLY_CLOSE_1215, "inferred"),
    _halt(date(2025, 12, 24), "Christmas Eve", EARLY_CLOSE_1215, "inferred"),
    _closure(date(2025, 12, 25), "Christmas Day"),
    # ---- 2026
    _closure(date(2026, 1, 1), "New Year's Day"),
    _halt(date(2026, 1, 19), "Martin Luther King Jr. Day", EARLY_HALT_NOON, "secondary"),
    _halt(date(2026, 2, 16), "Presidents Day", EARLY_HALT_NOON, "secondary"),
    # CME 2026 Good Friday clearing advisory: "Equities are open for an
    # abbreviated session on April 3rd, but will not be settled". Close time
    # not published CME-direct: 08:15 CT per AMP Futures (checked in bars).
    # 08:15 CT per AMP Futures; ~09:15 per another secondary source. The bars
    # settle it: last traded minute 08:14 CT, next bar Sunday 17:00 CT.
    _halt(date(2026, 4, 3), "Good Friday (abbreviated, jobs report)", time(8, 15), "empirical"),
    _halt(date(2026, 5, 25), "Memorial Day", EARLY_HALT_NOON, "secondary"),
    _halt(date(2026, 6, 19), "Juneteenth", EARLY_HALT_NOON, "secondary"),
    _halt(date(2026, 7, 3), "Independence Day (observed)", EARLY_HALT_NOON, "secondary"),
    _halt(date(2026, 9, 7), "Labor Day", EARLY_HALT_NOON, "secondary"),
    _halt(date(2026, 11, 26), "Thanksgiving", EARLY_HALT_NOON, "secondary"),
    _halt(date(2026, 11, 27), "Day after Thanksgiving", EARLY_CLOSE_1215, "inferred"),
    _halt(date(2026, 12, 24), "Christmas Eve", EARLY_CLOSE_1215, "inferred"),
    _closure(date(2026, 12, 25), "Christmas Day"),
)

HOLIDAYS: dict[date, Holiday] = {h.day: h for h in _ENTRIES}
CALENDAR_COVERAGE = (date(2019, 1, 1), date(2026, 12, 31))


class CalendarCoverageError(ValueError):
    """A bar's trade date lies outside the calendar's coverage: its holidays are unknown."""


def assert_calendar_coverage(days: Iterable[date]) -> None:
    """Raise unless every date lies inside ``CALENDAR_COVERAGE`` (inclusive). The bar builder
    calls this for every built trade date (reports/stage_d1f_confirmation_list.md 5.3)."""
    first, last = CALENDAR_COVERAGE
    outside = sorted(d for d in set(days) if not first <= d <= last)
    if outside:
        raise CalendarCoverageError(
            f"{len(outside)} trade date(s) outside the CME calendar's coverage "
            f"{first}..{last}: {outside[0]} .. {outside[-1]}; extend data/cme_calendar.py first")


# ---- the 2025-2026 entry lines are pinned (confirmation list section 0 and 5.3) ----
# sha256 of the 2025-2026 entry lines exactly as at commit 9cbd815 (whose whole file hashed to
# 5f24edda...). The extended file must keep them byte-identical; the whole-file hash changes.
ENTRIES_2025_2026_SHA256 = "8752f8370c90a5d6a105fdf9929af880355150a54f7e7196a7fa035b067b9538"
_BLOCK_START = "    # ---- 2025\n"
_BLOCK_END = '    _closure(date(2026, 12, 25), "Christmas Day"),\n'


def entries_2025_2026_block(source: str) -> str:
    """The 2025-2026 entry lines of a cme_calendar.py source text, from the ``# ---- 2025``
    line through the 2026 Christmas Day line inclusive (their sha256 is pinned above)."""
    if source.count(_BLOCK_START) != 1 or source.count(_BLOCK_END) != 1:
        raise ValueError("cannot locate exactly one 2025-2026 entry block")
    start = source.index(_BLOCK_START)
    return source[start: source.index(_BLOCK_END) + len(_BLOCK_END)]


# ---- 2019-2024 citations (Stage D.1f Task 3b) ----
@dataclass(frozen=True)
class Citation:
    """Where a 2019-2024 entry comes from. Quotes are verbatim from the page fetched in the
    D.1f extraction (reports/stage_d1f_calendar_sources.json); ``None`` URL = not fetched.
    Exception: the time quotes of the five 2019-2023 Independence Day entries come from the
    D.1f run's step-4b source check (reports/stage_d1f_calendar_check.json)."""

    status_url: str | None
    status_quote: str
    time_url: str | None = None
    time_quote: str | None = None
    note: str = ""


_CME = "https://www.cmegroup.com/tools-information/holiday-calendar/files/"
_CME_DAM = "https://www.cmegroup.com/content/dam/cmegroup/tools-information/holiday-calendar/files/"
_XT = "https://crosstrade.io/blog/cme-trading-hours-2026"
_XT_MLK = "Martin Luther King Jr. Day ... Monday: Early halt around 12:00 PM CT"
_XT_PRESIDENTS = "Presidents Day ... Monday: Early halt around 12:00 PM CT"
_XT_MEMORIAL = "Memorial Day ... Monday: Early halt"
_XT_LABOR = "Labor Day ... Monday: Early halt"
_XT_JUNETEENTH = "Juneteenth ... Early halt"
_XT_THANKSGIVING = "Thursday: Day session closed"
_NOTE_SETTLE_SPLIT = (
    "Time graded inferred, not cme: the CME line is a SETTLEMENT time split by bucket; ES/MES "
    "settle at 15:00 CT, so their early settlement is 12:00 CT, and the 12:15 CT halt follows "
    "this file's 2025-2026 convention (12:00 CT settlement -> 12:15 CT close, confirmed in the "
    "2025 bars on 07-03, 11-28 and 12-24). The extraction recorded 12:15 graded cme.")
_ES_HOURS_2024_07 = (
    "https://web.archive.org/web/20240708161439/https://www.cmegroup.com/services/"
    "trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1"
    "&pageSize=999&sortAsc=true&fromEventDate=2024-07-03&toEventDate=2024-07-05&isProtected"
    "&_t=1720455278680")
_NOTE_SETTLE_SINGLE = (
    "Halt 12:15 CT, time graded inferred: the CME line is the 12:00 CT equity SETTLEMENT time; "
    "the halt follows this file's 2025-2026 convention (12:00 CT settlement -> 12:15 CT close, "
    "confirmed in the 2025 bars on 07-03, 11-28 and 12-24). The extraction recorded the "
    "settlement time 12:00 as the halt.")

SOURCES_2019_2024: dict[date, Citation] = {
    date(2019, 1, 1): Citation(
        _CME + "2019-new-years-advisory.pdf",
        "Please reference the holiday processing schedule below for Tuesday, January 1st in "
        "observance of New Year's Day. ... There will be no MOSA processing on January 1, 2019."),
    date(2019, 1, 21): Citation(
        _CME + "2019-mlk-day-holiday-settlement-times.pdf",
        "Monday, January 21, 2019 Holiday No settlements for CME/CBOT/NYMEX/COMEX",
        _XT, _XT_MLK),
    date(2019, 2, 18): Citation(
        _CME + "2019-presidents-day-holiday-settlement-times.pdf",
        "Monday, February 18, 2019 Final Settlement at 5 am CT for Eurodollar and 1 Month "
        "Eurodollar futures No other CME/CBOT/NYMEX/COMEX settlements occur",
        _XT, _XT_PRESIDENTS),
    date(2019, 4, 19): Citation(
        _CME + "2019-good-friday-holiday-settlement-times.pdf",
        "Due to the Good Friday Holiday in the U.S. there will be no settlements for CME Group "
        "on Friday 4/19/2019"),
    date(2019, 5, 27): Citation(
        _CME + "2019-memorial-day-holiday-settlement-times.pdf",
        "Note: Monday May 27, 2019 CME Group will not derive or disseminate settlement prices "
        "for CME, CBOT, NYMEX or COMEX",
        _XT, _XT_MEMORIAL),
    date(2019, 7, 3): Citation(
        _CME + "2019-fourth-of-july-holiday-settlement-times.pdf",
        "Wednesday, July 3, 2019 Settlement Times ... Equity Products 12:00:00 CT (for futures "
        "that currently settle at 15:00 CT) 12:15:00 CT (for futures that currently settle at "
        "15:15 CT)",
        "https://web.archive.org/web/20220920142350/https://www.cmegroup.com/tools-information/"
        "holiday-calendar/files/2019/2019-4th-of-july-holiday-schedule-compact.xls",
        "Calendar Date|Wednesday July 3 |Wednesday,July 3|Thursday July 4 |Thursday July 4 into "
        " Friday July 5 ... Product|CLOSE|OPEN|HALT|OPEN ... Equity |Early  @ 1215 CT / 1715 "
        "UTC|Regular @ 1700 CT/ 2200 UTC",
        note="Time upgraded from inferred to cme in Stage E.2a (2026-09-25, design D14): CME's "
             "own Globex holiday schedule gives Equity an early CLOSE at 12:15 CT on Calendar "
             "Date 'Wednesday July 3' and the regular 17:00 CT reopen the same evening. Original "
             "https://www.cmegroup.com/tools-information/holiday-calendar/files/2019/"
             "2019-4th-of-july-holiday-schedule-compact.xls, read from the Wayback copy in "
             "time_url (cmegroup.com refuses automated fetches); found by the D.1f run's source "
             "check (reports/stage_d1f_calendar_check.json). The status line stays the CME "
             "settlement-times line of the build extraction."),
    date(2019, 7, 4): Citation(
        _CME + "2019-fourth-of-july-holiday-settlement-times.pdf",
        "Note: Thursday, July 4, 2019 CME Group will not derive or disseminate settlement "
        "prices for CME, CBOT, NYMEX or COMEX",
        "https://web.archive.org/web/20220920142350/https://www.cmegroup.com/tools-information/"
        "holiday-calendar/files/2019/2019-4th-of-july-holiday-schedule-compact.xls",
        "Calendar Date|Wednesday July 3 |Wednesday,July 3|Thursday July 4 |Thursday July 4 into "
        " Friday July 5 ... Product|CLOSE|OPEN|HALT|OPEN ... Equity |Early  @ 1215 CT / 1715 "
        "UTC|Regular @ 1700 CT/ 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC",
        note="Corrected in the Stage D.1f run (Task 3, step 4b, 2026-09-23): the status line is "
             "a CME SETTLEMENT note (no settlement that day), which the build extraction read "
             "as a full closure. CME's own Globex holiday schedule gives Equity a 12:00 CT halt "
             "and a 17:00 CT reopen: the HALT column is Calendar Date 'Thursday July 4'. "
             "Original https://www.cmegroup.com/tools-information/holiday-calendar/files/2019/"
             "2019-4th-of-july-holiday-schedule-compact.xls, read from the Wayback copy in "
             "time_url (cmegroup.com refuses automated fetches); reports/"
             "stage_d1f_calendar_check.json. The bars agree: last bar 11:59 CT, next bar 17:00 "
             "CT. CME books the holiday's Globex trades to the next trade date; this file "
             "models every holiday halt as its own short trade date (the 2025-2026 convention)."),
    date(2019, 9, 2): Citation(
        _CME + "2019-labor-day-holiday-settlement-times.pdf",
        "*Note: Monday, September 2, 2019 CME Group will not derive or disseminate settlement "
        "prices for CME, CBOT, NYMEX or COMEX",
        _XT, _XT_LABOR),
    date(2019, 11, 28): Citation(
        _XT,
        "Thanksgiving - Thursday, November 26, 2026 ... Thursday: Day session closed",
        _XT, _XT_THANKSGIVING,
        note=(
            "Status and time secondary (generic 2026 broker page): no CME-direct 2019 line for "
            "the Thanksgiving Day session itself.")),
    date(2019, 11, 29): Citation(
        _CME + "2019-thanksgiving-holiday-settlement-times.pdf",
        "Friday, 11/29/2019 (the day after Thanksgiving) Settlement Times ... Equity Products "
        "12:00:00 CT (for futures that currently settle at 15:00 CT) 12:15:00 CT (for futures "
        "that currently settle at 15:15 CT)",
        _CME + "2019-thanksgiving-holiday-settlement-times.pdf",
        "Equity Products 12:00:00 CT (for futures that currently settle at 15:00 CT) 12:15:00 "
        "CT (for futures that currently settle at 15:15 CT)",
        note=_NOTE_SETTLE_SPLIT),
    date(2019, 12, 24): Citation(
        _CME + "2019-christmas-holiday-settlement-times.pdf",
        "Christmas Day (12/25/2019) Holiday Settlement Times Tuesday, 12/24/2019 ... Equity "
        "Products 12:00:00 CT (for futures that currently settle at 15:00 CT) 12:15:00 CT (for "
        "futures that currently settle at 15:15 CT)",
        _CME + "2019-christmas-holiday-settlement-times.pdf",
        "Equity Products 12:00:00 CT (for futures that currently settle at 15:00 CT) 12:15:00 "
        "CT (for futures that currently settle at 15:15 CT)",
        note=_NOTE_SETTLE_SPLIT),
    date(2019, 12, 25): Citation(
        _CME + "2019-christmas-holiday-settlement-times.pdf",
        "Christmas Day (12/25/2019) Holiday Settlement Times"),
    date(2020, 1, 1): Citation(
        _CME + "2020-new-years-advisory.pdf",
        "SUBJECT: HOLIDAY SCHEDULE – January 01, 2020 ... There will be no MOSA processing on "
        "January 1, 2020."),
    date(2020, 1, 20): Citation(
        _CME + "mlk-day-holiday-settlement-times-2020.pdf",
        "Monday, January 20, 2020 Holiday No settlements for CME/CBOT/NYMEX/COMEX",
        _XT, _XT_MLK),
    date(2020, 2, 17): Citation(
        _CME + "presidents-day-holiday-settlement-times-2020.pdf",
        "Monday, February 17, 2020 Final Settlement at 5 am CT for February Eurodollar and 1 "
        "Month Eurodollar futures No other CME/CBOT/NYMEX/COMEX settlements occur",
        _XT, _XT_PRESIDENTS),
    date(2020, 4, 10): Citation(
        _CME + "good-friday-holiday-settlement-times-2020.pdf",
        "Due to the Good Friday Holiday in the U.S. there will be no settlements for CME Group "
        "on Friday 4/10/2020"),
    date(2020, 5, 25): Citation(
        _CME + "memorial-day-holiday-settlement-times-2020.pdf",
        "Note: Monday May 25, 2020 CME Group will not derive or disseminate settlement prices "
        "for CME, CBOT, NYMEX or COMEX",
        _XT, _XT_MEMORIAL),
    date(2020, 7, 3): Citation(
        _CME + "fourth-of-july-settlement-times-2020.pdf",
        "Fourth of July (7/4/2020) will be observed on 7/3/2020 ... NOTE: Friday, July 3, 2020 "
        "CME Group will not derive or disseminate settlement prices for CME, CBOT, NYMEX or "
        "COMEX",
        "https://web.archive.org/web/20220707015539/https://www.cmegroup.com/tools-information/"
        "holiday-calendar/files/2020-independence-day-schedule.xls",
        "Calendar Date|Thursday, July 2||||||||Friday, July 3|||Sunday, July 5|||||Monday, July "
        "6 ... |Regular Close|Early Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|"
        "Pre-opening**|Open|Close|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open "
        "... Equity Products|16:00|||16:45|17:00||||||12:00|16:00|17:00 ... * Day Orders "
        "entered for Friday's trading session will be eliminated at 12:00 CT",
        note="Corrected in the Stage D.1f run (Task 3, step 4b, 2026-09-23): the status line is "
             "a CME SETTLEMENT note (no settlement that day), which the build extraction read "
             "as a full closure. CME's own Globex holiday schedule gives Equity a 12:00 CT halt "
             "and a 17:00 CT reopen: the 12:00 'Close' cell sits under Calendar Date 'Friday, "
             "July 3' and the next 17:00 'Open' under 'Sunday, July 5' (merged header cells "
             "read with xlrd). Original https://www.cmegroup.com/tools-information/"
             "holiday-calendar/files/2020-independence-day-schedule.xls, read from the Wayback "
             "copy in time_url (cmegroup.com refuses automated fetches); reports/"
             "stage_d1f_calendar_check.json. The bars agree: last bar 11:59 CT, next bar 17:00 "
             "CT. CME books the holiday's Globex trades to the next trade date; this file "
             "models every holiday halt as its own short trade date (the 2025-2026 convention)."),
    date(2020, 9, 7): Citation(
        _CME + "labor-day-holiday-settlement-times-2020.pdf",
        "*Note: Monday, September 7, 2020 CME Group will not derive or disseminate settlement "
        "prices for CME, CBOT, NYMEX or COMEX",
        _XT, _XT_LABOR),
    date(2020, 11, 26): Citation(
        _XT,
        _XT_THANKSGIVING,
        _XT, _XT_THANKSGIVING,
        note=(
            "Status and time secondary (generic 2026 broker page): no CME-direct 2020 line for "
            "the Thanksgiving Day session itself.")),
    date(2020, 11, 27): Citation(
        _CME + "thanksgiving-holiday-settlement-times-2020.pdf",
        "Friday, 11/27/2020 (the day after Thanksgiving) Settlement Times ... Equity Products "
        "12:00:00 CT",
        _CME + "thanksgiving-holiday-settlement-times-2020.pdf", "Equity Products 12:00:00 CT",
        note=_NOTE_SETTLE_SINGLE),
    date(2020, 12, 24): Citation(
        _CME + "christmas-holiday-settlement-times-2020.pdf",
        "Thursday, 12/24/2020 ... Equity Products 12:00:00 CT (for futures that currently "
        "settle at 15:00 CT) 12:15:00 CT (for futures that currently settle at 15:15 CT)",
        _CME + "christmas-holiday-settlement-times-2020.pdf",
        "Equity Products 12:00:00 CT (for futures that currently settle at 15:00 CT) 12:15:00 "
        "CT (for futures that currently settle at 15:15 CT)",
        note=_NOTE_SETTLE_SPLIT),
    date(2020, 12, 25): Citation(
        _CME + "christmas-holiday-settlement-times-2020.pdf",
        "Christmas Day (12/25/2020) Holiday Settlement Times"),
    date(2021, 1, 1): Citation(
        None,
        "[unverified]",
        note=(
            "[unverified] status: the 2021 New Year's advisory was not fetched; assumed from "
            "the identical full-closure pattern of 2019, 2020, 2023 and 2024. Step 4b tests it.")),
    date(2021, 1, 18): Citation(
        _CME + "mlk-day-holiday-settlement-times-2021.pdf",
        "Monday, January 18, 2021 Holiday Final Settlement at 5 am CT for January Eurodollar "
        "and 1 Month Eurodollar futures No settlements for CME/CBOT/NYMEX/COMEX",
        _XT, _XT_MLK),
    date(2021, 2, 15): Citation(
        _CME + "presidents-day-holiday-settlement-times-2021.pdf",
        "Monday, February 15, 2021 Final Settlement at 5 am CT for February Eurodollar and 1 "
        "Month Eurodollar futures No other CME/CBOT/NYMEX/COMEX settlements occur",
        _XT, _XT_PRESIDENTS),
    date(2021, 4, 2): Citation(
        _CME + "2021-good-friday-advisory.pdf",
        "Equities (including Bitcoin and Ether) are open for an abbreviated session on April "
        "2, but will not be settled and will use the April 1st end of day settlement for mark "
        "to market.",
        "https://www.ampfutures.com/news/holiday-trading-schedule-good-friday-2021",
        "From the CME Globex Control Center, here is the summary of KEY changes, per CME "
        "market segment ... *Any open positions must meet Exchange Maintenance Margin 15 "
        "Minutes before CLOSE (CST - Chicago).",
        note=(
            "[unverified] close time: no year-specific source gives it (AMP's 2021 page has "
            "the schedule only as an image). 08:15 CT is the jobs-report Good Friday close of "
            "2023 (AMP, secondary) and 2026 (bars, empirical); step 4b tests it against the "
            "bars.")),
    date(2021, 5, 31): Citation(
        _CME + "memorial-day-holiday-settlement-times-2021.pdf",
        "Note: Monday May 31, 2021 CME Group will not derive or disseminate settlement prices "
        "for CME, CBOT, NYMEX or COMEX",
        _XT, _XT_MEMORIAL),
    date(2021, 7, 5): Citation(
        _CME + "fourth-of-july-settlement-times-2021.pdf",
        "U.S. Independence Day (7/4/2021) will be observed on 7/5/2021 ... NOTE: Monday, July "
        "5, 2021 CME Group will not derive or disseminate settlement prices for CME, CBOT, "
        "NYMEX or COMEX",
        "https://web.archive.org/web/20210702051538/https://www.cmegroup.com/tools-information/"
        "holiday-calendar/files/2021-independence-day-holiday-schedule-compact.xls",
        "Calendar Date|Friday July 2|Sunday July 4|Monday July 5|Monday July 5 ... Product|"
        "CLOSE|OPEN|HALT|OPEN ... Equity |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT/ 2200 "
        "UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC",
        note="Corrected in the Stage D.1f run (Task 3, step 4b, 2026-09-23): the status line is "
             "a CME SETTLEMENT note (no settlement that day), which the build extraction read "
             "as a full closure. CME's own Globex holiday schedule gives Equity a 12:00 CT halt "
             "and a 17:00 CT reopen: the HALT column is Calendar Date 'Monday July 5'. Original "
             "https://www.cmegroup.com/tools-information/holiday-calendar/files/"
             "2021-independence-day-holiday-schedule-compact.xls, read from the Wayback copy in "
             "time_url (cmegroup.com refuses automated fetches); reports/"
             "stage_d1f_calendar_check.json. The bars agree: last bar 11:59 CT, next bar 17:00 "
             "CT. CME books the holiday's Globex trades to the next trade date; this file "
             "models every holiday halt as its own short trade date (the 2025-2026 convention)."),
    date(2021, 9, 6): Citation(
        _CME + "labor-day-holiday-settlement-times-2021.pdf",
        "*Note: Monday, September 6, 2021 CME Group will not derive or disseminate settlement "
        "prices for CME, CBOT, NYMEX or COMEX",
        _XT, _XT_LABOR),
    date(2021, 11, 25): Citation(
        _XT,
        _XT_THANKSGIVING,
        _XT, _XT_THANKSGIVING,
        note=(
            "Status and time secondary (generic 2026 broker page): no CME-direct 2021 line for "
            "the Thanksgiving Day session itself.")),
    date(2021, 11, 26): Citation(
        _CME + "thanksgiving-holiday-settlement-times-2021.pdf",
        "Friday, 11/26/2021 (the day after Thanksgiving) Settlement Times ... Equity Products "
        "12:00:00 CT",
        _CME + "thanksgiving-holiday-settlement-times-2021.pdf", "Equity Products 12:00:00 CT",
        note=_NOTE_SETTLE_SINGLE),
    date(2021, 12, 24): Citation(
        _CME + "christmas-holiday-settlement-times-2021.pdf",
        "Christmas Day Holiday (12/25/2021) will be observed on 12/24/2021."),
    date(2022, 1, 17): Citation(
        _CME + "mlk-day-holiday-settlement-times-2022.pdf",
        "Monday, January 17, 2022 Holiday Final Settlement at 5 am CT for January Eurodollar "
        "and 1 Month Eurodollar futures No other settlements for CME/CBOT/NYMEX/COMEX will be "
        "published on Monday January 17, 2022.",
        _XT, _XT_MLK),
    date(2022, 2, 21): Citation(
        _CME + "presidents-day-holiday-settlement-times-2022.pdf",
        "Monday February 21, 2022 CME Group will not derive or disseminate settlement prices "
        "for CME, CBOT, NYMEX or COMEX",
        _XT, _XT_PRESIDENTS),
    date(2022, 4, 15): Citation(
        _CME + "good-friday-holiday-settlement-times-2022.pdf",
        "Note: Friday April 15, 2022 CME Group will not derive or disseminate settlement "
        "prices for CME, CBOT, NYMEX or COMEX"),
    date(2022, 5, 30): Citation(
        _CME + "memorial-day-holiday-settlement-times-2022.pdf",
        "Note: Monday May 30, 2022 CME Group will not derive or disseminate settlement prices "
        "for CME, CBOT, NYMEX or COMEX",
        _XT, _XT_MEMORIAL),
    date(2022, 6, 20): Citation(
        _CME + "juneteenth-day-holiday-settlement-times-2022.pdf",
        "Juneteenth Holiday (6/19/2022) will be observed on 6/20/2022 ... Note: Monday June "
        "20, 2022 CME Group will not derive or disseminate settlement prices for CME, CBOT, "
        "NYMEX or COMEX",
        _XT, _XT_JUNETEENTH),
    date(2022, 7, 4): Citation(
        _CME + "fourth-of-july-settlement-times-2022.pdf",
        "NOTE: Note: Monday, July 4, 2022 CME Group will not derive or disseminate settlement "
        "prices for CME, CBOT, NYMEX or COMEX",
        "https://web.archive.org/web/20220704065431/https://www.cmegroup.com/tools-information/"
        "holiday-calendar/files/2022-independence-day-holiday-schedule-compact.xls",
        "Calendar Date|Friday July 1|Sunday July 3|Monday July 4|Monday July 4 ... Product|"
        "CLOSE|OPEN|HALT|OPEN ... Equity |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT/ 2200 "
        "UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC",
        note="Corrected in the Stage D.1f run (Task 3, step 4b, 2026-09-23): the status line is "
             "a CME SETTLEMENT note (no settlement that day), which the build extraction read "
             "as a full closure. CME's own Globex holiday schedule gives Equity a 12:00 CT halt "
             "and a 17:00 CT reopen: the HALT column is Calendar Date 'Monday July 4'. Original "
             "https://www.cmegroup.com/tools-information/holiday-calendar/files/"
             "2022-independence-day-holiday-schedule-compact.xls, read from the Wayback copy in "
             "time_url (cmegroup.com refuses automated fetches); reports/"
             "stage_d1f_calendar_check.json. The bars agree: last bar 11:59 CT, next bar 17:00 "
             "CT. CME books the holiday's Globex trades to the next trade date; this file "
             "models every holiday halt as its own short trade date (the 2025-2026 convention)."),
    date(2022, 9, 5): Citation(
        _CME + "labor-day-holiday-settlement-times-2022.pdf",
        "*Note: Monday, September 5, 2022 CME Group will not derive or disseminate settlement "
        "prices for CME, CBOT, NYMEX or COMEX",
        _XT, _XT_LABOR),
    date(2022, 11, 24): Citation(
        _CME + "thanksgiving-holiday-settlement-times-2022.pdf",
        "Note: Thursday November 24, 2022 CME Group will not derive or disseminate settlement "
        "prices for CME, CBOT, NYMEX or COMEX",
        _XT, _XT_THANKSGIVING),
    date(2022, 11, 25): Citation(
        _CME + "thanksgiving-holiday-settlement-times-2022.pdf",
        "Friday, November 25, 2022 (the day after Thanksgiving) Settlement Times ... Equity "
        "Products 12:00:00 CT",
        _CME + "thanksgiving-holiday-settlement-times-2022.pdf", "Equity Products 12:00:00 CT",
        note=_NOTE_SETTLE_SINGLE),
    date(2022, 12, 26): Citation(
        _CME + "christmas-holiday-settlement-times-2022.pdf",
        "Christmas Day Holiday 12/25/2022 will be observed on 12/26/2022. ... Note: Monday "
        "December 26, 2022 CME Group will not derive or disseminate settlement prices for CME, "
        "CBOT, NYMEX or COMEX"),
    date(2023, 1, 2): Citation(
        _CME + "2023-new-years-advisory.pdf",
        "SUBJECT: HOLIDAY SCHEDULE – New Year's Day January 2, 2023 (Observed) ... Intraday "
        "Cycle (ITD) | No ITD Cycle | No ITD Cycle | No settle file | No SPAN file | No reports"),
    date(2023, 1, 16): Citation(
        _CME + "mlk-day-holiday-settlement-times-2023.pdf",
        "Note: Monday January 16, 2023 CME Group will not derive or disseminate settlement "
        "prices (other than the two LIBOR Settlements listed above) for CME, CBOT, NYMEX or "
        "COMEX",
        _XT, _XT_MLK),
    date(2023, 2, 20): Citation(
        _CME + "presidents-day-holiday-settlement-times-2023.pdf",
        "Note: Monday February 20, 2023 CME Group will not derive or disseminate settlement "
        "prices for CME, CBOT, NYMEX or COMEX",
        _XT, _XT_PRESIDENTS),
    date(2023, 4, 7): Citation(
        _CME + "2023-good-friday-advisory.pdf",
        "Equities are open for an abbreviated session on April 7th but will not be settled and "
        "will use the April 6th end of day settlement for mark to market.",
        "https://www.ampfutures.com/news/holiday-trading-schedule-good-friday-2023",
        'Friday, April 7, 2023 - Early Market "CLOSE" - 8:15 am CST (Chicago)'),
    date(2023, 5, 29): Citation(
        _CME + "memorial-day-holiday-settlement-times-2023.pdf",
        "Note: Monday May 29, 2023 CME Group will not derive or disseminate settlement prices "
        "for CME, CBOT, NYMEX or COMEX",
        _XT, _XT_MEMORIAL),
    date(2023, 6, 19): Citation(
        _CME + "juneteenth-day-holiday-settlement-times-2023.pdf",
        "Note: Monday June 19, 2023 CME Group will not derive or disseminate settlement prices "
        "(other than the two LIBOR Settlements listed above) for CME, CBOT, NYMEX or COMEX",
        _XT, _XT_JUNETEENTH),
    date(2023, 7, 3): Citation(
        _CME + "fourth-of-july-settlement-times-2023.pdf",
        "Monday, July 3, 2023 ... Equity Index Products 12:00:00 CT",
        "https://web.archive.org/web/20230627125057/https://www.cmegroup.com/trading-hours/"
        "files/4th-of-july-2023.pdf",
        "PRODUCT NAME MONDAY, 3 JULY 2023 TUESDAY, 4 JULY 2023 WEDNESDAY, 5 JULY 2023 ... "
        "EQUITIES ... TRADE DATE: MON 3 JULY ... 12:15 (CLOSED) ... TRADE DATE: WED 5 JULY ... "
        "16:45 (PREOPEN) ... 17:00 (OPEN)",
        note="Time upgraded from inferred to cme in Stage E.2a (2026-09-25, design D14): CME's "
             "own 4th of July 2023 holiday summary gives the EQUITIES row, Monday 3 July column, "
             "'TRADE DATE: MON 3 JULY 12:15 (CLOSED)' and then '16:45 (PREOPEN) 17:00 (OPEN)' "
             "for trade date Wed 5 July (PDF layout; the summary uses the most actively traded "
             "instrument of each asset class). Original https://www.cmegroup.com/trading-hours/"
             "files/4th-of-july-2023.pdf, read from the Wayback copy in time_url (cmegroup.com "
             "refuses automated fetches); found by the D.1f run's source check (reports/"
             "stage_d1f_calendar_check.json). The status line stays the CME settlement-times "
             "line of the build extraction."),
    date(2023, 7, 4): Citation(
        _CME + "fourth-of-july-settlement-times-2023.pdf",
        "Note: Tuesday, July 4, 2023 CME Group will not derive or disseminate settlement "
        "prices for CME, CBOT, NYMEX or COMEX",
        "https://web.archive.org/web/20230627125057/https://www.cmegroup.com/trading-hours/"
        "files/4th-of-july-2023.pdf",
        "PRODUCT NAME MONDAY, 3 JULY 2023 TUESDAY, 4 JULY 2023 WEDNESDAY, 5 JULY 2023 ... "
        "EQUITIES ... 12:00 (PREOPEN) HALT ... 17:00 (OPEN) ... PREOPEN (HALT): Order Entry, "
        "modification, and cancel are allowed. No order matching.",
        note="Corrected in the Stage D.1f run (Task 3, step 4b, 2026-09-23): the status line is "
             "a CME SETTLEMENT note (no settlement that day), which the build extraction read "
             "as a full closure. CME's own Globex holiday schedule gives Equity a 12:00 CT halt "
             "and a 17:00 CT reopen: the '12:00 (PREOPEN) HALT' cell is the EQUITIES row's "
             "Tuesday 4 July column (PDF layout; the summary uses the most actively traded "
             "instrument of each asset class). Original https://www.cmegroup.com/trading-hours/"
             "files/4th-of-july-2023.pdf, read from the Wayback copy in time_url (cmegroup.com "
             "refuses automated fetches); reports/stage_d1f_calendar_check.json. The bars "
             "agree: last bar 11:59 CT, next bar 17:00 CT. CME books the holiday's Globex "
             "trades to the next trade date; this file models every holiday halt as its own "
             "short trade date (the 2025-2026 convention)."),
    date(2023, 9, 4): Citation(
        _CME + "labor-day-holiday-settlement-times-2023.pdf",
        "Note: Monday, September 4, 2023 CME Group will not derive or disseminate settlement "
        "prices for CME, CBOT, NYMEX or COMEX",
        _XT, _XT_LABOR),
    date(2023, 11, 23): Citation(
        _CME + "thanksgiving-holiday-settlement-times-2023.pdf",
        "Note: Thursday November 23, 2023 CME Group will not derive or disseminate settlement "
        "prices for CME, CBOT, NYMEX or COMEX",
        _XT, _XT_THANKSGIVING),
    date(2023, 11, 24): Citation(
        _CME + "thanksgiving-holiday-settlement-times-2023.pdf",
        "Friday, November 24, 2023 (the day after Thanksgiving) ... Equity & Crypto Products "
        "12:00:00 CT",
        _CME + "thanksgiving-holiday-settlement-times-2023.pdf",
        "Equity & Crypto Products 12:00:00 CT",
        note=_NOTE_SETTLE_SINGLE),
    date(2023, 12, 25): Citation(
        _CME + "christmas-holiday-settlement-times-2023.pdf",
        "Note: Monday December 25, 2023 CME Group will not derive or disseminate settlement "
        "prices for CME, CBOT, NYMEX or COMEX"),
    date(2024, 1, 1): Citation(
        _CME + "2024-new-years-advisory.pdf",
        "SUBJECT: HOLIDAY SCHEDULE – New Year's Day January 1, 2024 (Observed) ... Intraday "
        "Cycle (ITD) | No ITD Cycle | No ITD Cycle | No settle file | No SPAN file | No reports"),
    date(2024, 1, 15): Citation(
        _CME + "mlk-day-holiday-settlement-times-2024.pdf",
        "Note: Monday January 15, 2024 CME Group will not derive or disseminate settlement "
        "prices for CME, CBOT, NYMEX or COMEX",
        _XT, _XT_MLK),
    date(2024, 2, 19): Citation(
        _CME + "presidents-day-holiday-settlement-times-2024.pdf",
        "Note: Monday February 19, 2024 CME Group will not derive or disseminate settlement "
        "prices for CME, CBOT, NYMEX or COMEX",
        _XT, _XT_PRESIDENTS),
    date(2024, 3, 29): Citation(
        _CME + "good-friday-holiday-settlement-times-2024.pdf",
        "Note: Good Friday March 29, 2024 CME Group will not derive or disseminate settlement "
        "prices for CME, CBOT, NYMEX or COMEX"),
    date(2024, 5, 27): Citation(
        _CME + "memorial-day-holiday-settlement-times-2024.pdf",
        "Note: Monday May 27, 2024 CME Group will not derive or disseminate settlement prices "
        "for CME, CBOT, NYMEX or COMEX",
        _XT, _XT_MEMORIAL),
    date(2024, 6, 19): Citation(
        _CME + "juneteenth-day-settlement-times-2024.pdf",
        "Note: Wednesday June 19, 2024 CME Group will not derive or disseminate settlement "
        "prices for CME, CBOT, NYMEX or COMEX",
        _XT, _XT_JUNETEENTH),
    date(2024, 7, 3): Citation(
        _CME_DAM + "us-independence-day-settlement-times-2024.pdf",
        "Wednesday, July 3, 2024 ... Equity Index Products Settlement Time: 12:00:00 CT",
        _CME_DAM + "us-independence-day-settlement-times-2024.pdf",
        "Equity Index Products Settlement Time: 12:00:00 CT",
        note=_NOTE_SETTLE_SINGLE),
    date(2024, 7, 4): Citation(
        _ES_HOURS_2024_07,
        '"globex":"ES","prodGroup":"ES","name":"E-mini S&P 500 Futures","id":133 ... '
        '{"groupCode":"ES","eventDate":"2024-07-03","events":[{"tradingDate":"2024-07-03",'
        '"eventTime":"12:15","marketEventType":"closed"},{"tradingDate":"2024-07-05",'
        '"eventTime":"16:45","marketEventType":"preopen"},{"tradingDate":"2024-07-05",'
        '"eventTime":"17:00","marketEventType":"open"}]},{"groupCode":"ES","eventDate":'
        '"2024-07-04","events":[{"tradingDate":"2024-07-05","eventTime":"12:00",'
        '"marketEventType":"preopen"}',
        _ES_HOURS_2024_07,
        '{"groupCode":"ES","eventDate":"2024-07-04","events":[{"tradingDate":"2024-07-05",'
        '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2024-07-05",'
        '"eventTime":"17:00","marketEventType":"open"}]}',
        note="Corrected in Stage E.2a (2026-09-25, design D10 and D14) from FULL_CLOSURE to a "
             "12:00 CT halt, graded cme / cme from CME's trading-hours-by-product service (the "
             "data behind cmegroup.com/trading-hours.html), record for product 133 'E-mini S&P "
             "500 Futures' (ES), Wayback capture 2024-07-08 16:14:39 UTC, found by the D.1f "
             "run's source check (reports/stage_d1f_calendar_check.json): Globex opened Wed "
             "2024-07-03 17:00 CT for trade date 2024-07-05 and went to 'preopen' (the halt: "
             "order entry, no matching) at 12:00 CT on Thu 2024-07-04, reopening at 17:00 CT. "
             "The build extraction's status line, CME's settlement note 'Note: Thursday, July 4, "
             "2024 CME Group will not derive or disseminate settlement prices for CME, CBOT, "
             "NYMEX or COMEX' (" + _CME_DAM + "us-independence-day-settlement-times-2024.pdf), "
             "says only that no settlement was derived; it was read as a full closure, the same "
             "error the D.1f run corrected for 2019-2023. MES is not in the captured product "
             "set; ES stands for the equity group. A holdout-2 date: never checked against bars. "
             "CME books the holiday's Globex trades to the next trade date; this file models "
             "every holiday halt as its own short trade date (the 2025-2026 convention)."),
    date(2024, 9, 2): Citation(
        _CME + "labor-day-holiday-settlement-times-2024.pdf",
        "Note: Monday, September 2, 2024 CME Group will not derive or disseminate settlement "
        "prices for CME, CBOT, NYMEX or COMEX",
        _XT, _XT_LABOR),
    date(2024, 11, 28): Citation(
        _CME + "thanksgiving-holiday-settlement-times-2024.pdf",
        "Note: Thursday November 28, 2024 CME Group will not derive or disseminate settlement "
        "prices for CME, CBOT, NYMEX or COMEX",
        _XT, _XT_THANKSGIVING),
    date(2024, 11, 29): Citation(
        _CME + "thanksgiving-holiday-settlement-times-2024.pdf",
        "Friday, November 29, 2024 (the day after Thanksgiving) ... Equity & Crypto Products "
        "Settlement Time: 12:00:00 CT",
        _CME + "thanksgiving-holiday-settlement-times-2024.pdf",
        "Equity & Crypto Products Settlement Time: 12:00:00 CT",
        note=_NOTE_SETTLE_SINGLE),
    date(2024, 12, 24): Citation(
        _CME + "christmas-holiday-settlement-times-2024.pdf",
        "Tuesday, December 24, 2024 ... Equity & Crypto Products Settlement Time: 12:00:00 CT",
        _CME + "christmas-holiday-settlement-times-2024.pdf",
        "Equity & Crypto Products Settlement Time: 12:00:00 CT",
        note=_NOTE_SETTLE_SINGLE),
    date(2024, 12, 25): Citation(
        _CME + "christmas-holiday-settlement-times-2024.pdf",
        "Christmas Day Holiday 12/25/2024 Settlement Times"),
}

# Days the extraction checked and found NORMAL (CME-direct), so they carry no entry. Kept
# with their evidence so the absence is a recorded finding, not an oversight.
NO_ENTRY_FINDINGS_2019_2024: dict[date, Citation] = {
    date(2020, 7, 2): Citation(
        _CME + "fourth-of-july-settlement-times-2020.pdf",
        "Thursday, July 2, 2020 Settlement Times ... Equity Products Normal Settlement Times",
        note=(
            "NEGATIVE FINDING: in 2020 (July 4 fell on Saturday, observed Friday July 3) "
            "equity products settled at their NORMAL time on Thursday July 2 -- no early close "
            "that day. Included so the lead does not assume a 12:15 CT close exists for every "
            "pre-holiday day.")),
    date(2021, 7, 2): Citation(
        _CME + "fourth-of-july-settlement-times-2021.pdf",
        "Friday, July 2, 2021 Settlement Times ... Equity Products Normal Settlement Times",
        note=(
            "NEGATIVE FINDING: July 4, 2021 fell on a Sunday, observed Monday July 5; equities "
            "settled NORMALLY on Friday July 2 -- no early close that day.")),
    date(2022, 1, 3): Citation(
        _CME + "2021-new-years-advisory.pdf",
        "SUBJECT: HOLIDAY SCHEDULE – January 3, 2022 (New Year's Day) ... Intraday Cycle (ITD) "
        "| Normal Processing | Normal Processing | Normal Processing | Normal Processing | "
        "Normal Processing",
        note=(
            "NEGATIVE FINDING flagged for the lead's judgment: January 1, 2022 fell on a "
            "Saturday. The CME advisory is titled for 'January 3, 2022 (New Year's Day)' but "
            "its own processing tables show NORMAL settlement/clearing cycles for that Monday "
            "-- i.e. CME did NOT treat Jan 3, 2022 as a closed/no-settlement day. No separate "
            "New Year's Day closure entry is recorded for 2022; this is a candidate case for "
            "the lead to double check against bar data.")),
}
