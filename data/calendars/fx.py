"""CME Globex calendar for the FX group: 6E, M6E, E7, 6A, M6A, 6B, M6B, 6C, 6J, 6S and 6N,
2019-05-01..2026-06-19 (Stage E.2a Task 6; design D10 and D11.3).

Interface as data.cme_calendar, whose Holiday, HolidayKind, Citation and CalendarCoverageError are
imported, not redefined: HOLIDAYS, SOURCES, NO_ENTRY_FINDINGS, CALENDAR_COVERAGE and
assert_calendar_coverage, plus SESSIONS (data.calendars.SessionSpec) with SESSION_SOURCES. One
additive extension, which no existing caller needs to know about: LATE_OPENS (with
LATE_OPEN_SOURCES), trade dates whose Globex session did not trade from its regular start (one,
the unscheduled CME halt before 07:30 CT on 2025-11-28). It mirrors data.calendars.rates.

Sources (all CME Group except one secondary no-entry finding; cmegroup.com refuses automated
fetches, so every cmegroup.com file was read from a Wayback Machine copy):
- 2019-2022: CME's Globex holiday trading schedules (.xls), row "FX" of the compact schedule
  (2019-2021 from CME's yearly holiday-calendars.zip, 2022 one file per holiday; the full
  schedule's "FX Products" row where no compact file exists).
- 2023-01..2024-01: CME's holiday summary PDFs, row "FX" ("the most actively traded instruments
  for each asset class").
- 2023-09..2026-06: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html,
  product 58 (6E, Euro FX futures), captures of 2024-07-08, 2024-12-20, 2026-01-29 and 2026-06-19.
- Good Friday closures 2024 and 2025: notes on cmegroup.com/trading-hours.html. Good Friday 2026
  status: CME's clearing advisory. 2025-01-09: CME's National Day of Mourning schedule.
- Session hours and settlement: CME's Euro FX contract specifications (2014, 2019 captures), CME's
  6E service data, and CME's Client Systems Wiki settlement pages (read directly, 2026-09-25).
Verbatim quotes, capture URLs and file hashes per entry: reports/stage_e2a_calendar_sources_fx.json
and .md. CME states these hours for its FX asset class or for 6E; the other ten FX contracts are
taken to share them (the only FX exception row in the schedules read is New Zealand Spot FX, not a
futures contract of this group).

Grades as data.cme_calendar: status (``evidence``) "cme" | "secondary" | "unverified"; time
(``time_evidence``) "cme" | "secondary" | "inferred" | "unverified" | "n/a" ("empirical" is
reserved for the later bar check). Every HOLIDAYS status and time here is "cme". Two times rest
on CME documents that conflict: 2024-11-29 (13:45) and 2024-12-24 (12:45) follow CME's
2024-12-20 service capture; its 2024-07-08 capture gave 12:15 for both (see their notes).

How FX differs from the equity calendar:
- From 2022 (first seen MLK Day 2022-01-17), FX trades its regular session through Monday US
  holidays and Thanksgiving: CME's FX "halt" is at 16:00 CT, the regular daily close. Those
  holidays carry no entry (NO_ENTRY_FINDINGS); until 2021-11-25 the FX holiday halt was 12:00 CT.
- Friday holidays still close FX at 12:00 CT (2020-07-03, 2025-07-04, 2026-06-19).
- Pre-holiday days keep the regular 16:00 CT FX close (the eve of Independence Day, New Year's
  Eve), unlike equity's 12:15 CT.
- The day after Thanksgiving and Christmas Eve close at 12:15 CT through 2023, at 13:45 CT and
  12:45 CT respectively from 2024 (CME's 2024-12-20 and 2026-01-29 service captures).
- Jobs-report Good Fridays (2021-04-02, 2023-04-07, 2026-04-03) close FX at 10:15 CT (equity
  08:15 CT); other Good Fridays are full closures.
- The National Day of Mourning (2025-01-09) kept FX at normal hours.

Conventions: ``halt_ct`` is the CT minute trading stops, so the last one-minute bar starts at
halt_ct minus one minute; the reopen is the normal 17:00 CT (Sunday 17:00 when the halt day is a
Friday). CME books the Globex session that ends at a holiday halt to the next trade date; this
module keeps each halt day as its own short trade date, as data.cme_calendar does. Holdout-2
dates (2024-04-01..2025-03-31) and the 2019-05..2024-02 confirmation window rest on CME's
schedules alone until their bars are checked.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, time

from data.calendars import Segment, SessionSpec
from data.cme_calendar import CalendarCoverageError, Citation, Holiday, HolidayKind

FX_PRODUCTS = ("6E", "M6E", "E7", "6A", "M6A", "6B", "M6B", "6C", "6J", "6S", "6N")

_HC = "https://www.cmegroup.com/tools-information/holiday-calendar/files/"
_TH = "https://www.cmegroup.com/trading-hours/files/"
_FILES = "https://www.cmegroup.com/files/"
_TH_PAGE = "https://www.cmegroup.com/trading-hours.html"
_WIKI = "https://cmegroupclientsite.atlassian.net/wiki/display/EPICSANDBOX/"
_EURO_FX_SPECS = "https://www.cmegroup.com/trading/fx/g10/euro-fx_contract_specifications.html"
_AMP_MLK_2023 = (
    "https://www.ampfutures.com/hubfs/CME%20Holiday%20Trading%20Schedule%20-%20Dr.%20Martin%20"
    "Luther%20King%2c%20Jr.%20(2023).png"
)
_Z19, _Z20, _Z21 = (_HC + f"{y}-holiday-calendars.zip" for y in (2019, 2020, 2021))


def _svc(from_day: str, to_day: str, t: str) -> str:
    """CME's trading-hours-by-product request as captured by the Wayback Machine."""
    return ("https://www.cmegroup.com/services/trading-hours-by-product?id=316,133,425,300,58,437,"
            f"22,8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate={from_day}"
            f"&toEventDate={to_day}&isProtected&_t={t}")


def _closure(day: date, name: str, evidence: str = "cme") -> Holiday:
    return Holiday(day, name, HolidayKind.FULL_CLOSURE, None, evidence, "n/a")


def _halt(
    day: date, name: str, at: time, evidence: str = "cme", time_evidence: str = "cme"
) -> Holiday:
    return Holiday(day, name, HolidayKind.EARLY_HALT, at, evidence, time_evidence)



_ENTRIES: tuple[Holiday, ...] = (
    # ---- 2019
    _halt(date(2019, 5, 27), "Memorial Day", time(12, 0)),
    _halt(date(2019, 7, 4), "Independence Day", time(12, 0)),
    _halt(date(2019, 9, 2), "Labor Day", time(12, 0)),
    _halt(date(2019, 11, 28), "Thanksgiving Day", time(12, 0)),
    _halt(date(2019, 11, 29), "Day after Thanksgiving", time(12, 15)),
    _halt(date(2019, 12, 24), "Christmas Eve", time(12, 15)),
    _closure(date(2019, 12, 25), "Christmas Day"),
    # ---- 2020
    _closure(date(2020, 1, 1), "New Year's Day"),
    _halt(date(2020, 1, 20), "Martin Luther King Jr. Day", time(12, 0)),
    _halt(date(2020, 2, 17), "Presidents Day", time(12, 0)),
    _closure(date(2020, 4, 10), "Good Friday"),
    _halt(date(2020, 5, 25), "Memorial Day", time(12, 0)),
    _halt(date(2020, 7, 3), "Independence Day (observed)", time(12, 0)),
    _halt(date(2020, 9, 7), "Labor Day", time(12, 0)),
    _halt(date(2020, 11, 26), "Thanksgiving Day", time(12, 0)),
    _halt(date(2020, 11, 27), "Day after Thanksgiving", time(12, 15)),
    _halt(date(2020, 12, 24), "Christmas Eve", time(12, 15)),
    _closure(date(2020, 12, 25), "Christmas Day"),
    # ---- 2021
    _closure(date(2021, 1, 1), "New Year's Day"),
    _halt(date(2021, 1, 18), "Martin Luther King Jr. Day", time(12, 0)),
    _halt(date(2021, 2, 15), "Presidents Day", time(12, 0)),
    _halt(date(2021, 4, 2), "Good Friday (abbreviated, jobs report)", time(10, 15)),
    _halt(date(2021, 5, 31), "Memorial Day", time(12, 0)),
    _halt(date(2021, 7, 5), "Independence Day (observed)", time(12, 0)),
    _halt(date(2021, 9, 6), "Labor Day", time(12, 0)),
    _halt(date(2021, 11, 25), "Thanksgiving Day", time(12, 0)),
    _halt(date(2021, 11, 26), "Day after Thanksgiving", time(12, 15)),
    _closure(date(2021, 12, 24), "Christmas Day (observed)"),
    # ---- 2022
    _closure(date(2022, 4, 15), "Good Friday"),
    _halt(date(2022, 11, 25), "Day after Thanksgiving", time(12, 15)),
    _closure(date(2022, 12, 26), "Christmas Day (observed)"),
    # ---- 2023
    _closure(date(2023, 1, 2), "New Year's Day (observed)"),
    _halt(date(2023, 4, 7), "Good Friday (abbreviated, jobs report)", time(10, 15)),
    _halt(date(2023, 11, 24), "Day after Thanksgiving", time(12, 15)),
    _closure(date(2023, 12, 25), "Christmas Day"),
    # ---- 2024
    _closure(date(2024, 1, 1), "New Year's Day"),
    _closure(date(2024, 3, 29), "Good Friday"),
    _halt(date(2024, 11, 29), "Day after Thanksgiving", time(13, 45)),
    _halt(date(2024, 12, 24), "Christmas Eve", time(12, 45)),
    _closure(date(2024, 12, 25), "Christmas Day"),
    # ---- 2025
    _closure(date(2025, 1, 1), "New Year's Day"),
    _closure(date(2025, 4, 18), "Good Friday"),
    _halt(date(2025, 7, 4), "Independence Day", time(12, 0)),
    _halt(date(2025, 11, 28), "Day after Thanksgiving", time(13, 45)),
    _halt(date(2025, 12, 24), "Christmas Eve", time(12, 45)),
    _closure(date(2025, 12, 25), "Christmas Day"),
    # ---- 2026
    _closure(date(2026, 1, 1), "New Year's Day"),
    _halt(date(2026, 4, 3), "Good Friday (abbreviated, jobs report)", time(10, 15)),
    _halt(date(2026, 6, 19), "Juneteenth", time(12, 0)),
)

HOLIDAYS: dict[date, Holiday] = {h.day: h for h in _ENTRIES}
CALENDAR_COVERAGE = (date(2019, 5, 1), date(2026, 6, 19))


def assert_calendar_coverage(days: Iterable[date]) -> None:
    """Raise unless every date lies inside ``CALENDAR_COVERAGE`` (inclusive), with
    data.cme_calendar's semantics: the bar builder calls this for every built trade date."""
    first, last = CALENDAR_COVERAGE
    outside = sorted(d for d in set(days) if not first <= d <= last)
    if outside:
        raise CalendarCoverageError(
            f"{len(outside)} trade date(s) outside the FX calendar's coverage "
            f"{first}..{last}: {outside[0]} .. {outside[-1]}; extend data/calendars/fx.py first")


@dataclass(frozen=True)
class LateOpen:
    """A trade date whose Globex session did not trade from its regular start: trading stopped at
    ``halt_from_ct`` on the calendar day ``halt_from_offset_days`` from ``day`` (None: the stop
    time is not in any source retrieved) and resumed at ``open_ct`` CT on ``day``. Grades as for
    Holiday. Additive to the data.cme_calendar interface (same fields as data.calendars.rates)."""

    day: date
    name: str
    open_ct: time
    evidence: str
    time_evidence: str
    halt_from_ct: time | None = None
    halt_from_offset_days: int = -1


LATE_OPENS: dict[date, LateOpen] = {
    date(2025, 11, 28): LateOpen(
        date(2025, 11, 28), "Unscheduled Globex halt, reopen 07:30 CT", time(7, 30), "cme", "cme"
    ),
}

# Design D6's FX row: day-session open O and close C (CT). F = 15:08 CT is the rules engine's.
D6_FX_DAY_SESSION_CT = (time(7, 20), time(14, 0))

# One regime covers the whole window: no CME change to FX futures Globex hours was found.
SESSIONS: tuple[SessionSpec, ...] = (
    SessionSpec(
        valid_from=date(2019, 5, 1),
        valid_to=date(2026, 6, 19),
        segments=(Segment(-1, time(17, 0), 0, time(16, 0)),),
        day_session_ct={p: D6_FX_DAY_SESSION_CT for p in FX_PRODUCTS},
        source="cme_fx_globex_hours",
        note=(
            "Regular FX Globex session: trade date D runs from 17:00 CT on the prior calendar day "
            "(Sunday for Monday) to 16:00 CT on D. day_session_ct is design D6's FX row (O 07:20, "
            "C 14:00 CT), keyed by product. D6 confirmation: C 14:00 CT matches CME's FX daily "
            "settlement time for every product (SESSION_SOURCES 'cme_fx_settlement' and "
            "'cme_settle_*'; the micro contracts settle to their full-size contract; E7 is "
            "covered by the group-level FX row only). O 07:20 CT is the start of CME's former "
            "Euro FX open-outcry regular trading hours ('cme_fx_rth_open'); it is not an event of "
            "the FX Globex session in 2019-2026 and no CME settlement procedure defines an open. "
            "D6's values are encoded unchanged; the lead rules (reports/"
            "stage_e2a_calendar_sources_fx.md, D6 confirmation). CME settled FX early on some "
            "days while Globex traded to 16:00 CT (for example 12:00 CT on 2019-12-31): "
            "NO_ENTRY_FINDINGS."
        ),
    ),
)


SOURCES: dict[date, Citation] = {
    date(2019, 5, 27): Citation(
        _Z19,
        (
            "CME Group Globex Memorial Day Holiday Schedule: May 24, 2019 - May 28, 2019 ... "
            "Calendar Date|Friday,May 24|Sunday,May 26 into Monday,May 27|Monday, May 27|Mon,May "
            "27 into Tues,May 28 ... Product|CLOSE|OPEN|HALT|OPEN ... FX |Regular @ 1600 CT / 2100 "
            "UTC|Regular @ 1700 CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        _Z19,
        (
            "Product|CLOSE|OPEN|HALT|OPEN ... FX |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT / "
            "2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-memorial-day-holiday-schedule-compact.xls. "
            "CME books this Globex session to the next trade date; the module keeps the day as its "
            "own short trade date (data.cme_calendar convention)."
        ),
    ),
    date(2019, 7, 4): Citation(
        _Z19,
        (
            "CME Group Globex Independence Day Holiday Schedule: July 3, 2019 to July 5, 2019 ... "
            "Calendar Date|Wednesday July 3 |Wednesday,July 3|Thursday July 4 |Thursday July 4 "
            "into Friday July 5 ... Product|CLOSE|OPEN|HALT|OPEN ... FX |Regular @ 1600 CT / 2100 "
            "UTC|Regular @ 1700 CT/ 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        _Z19,
        (
            "Product|CLOSE|OPEN|HALT|OPEN ... FX |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT/ "
            "2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-4th-of-july-holiday-schedule-compact.xls. "
            "CME books this Globex session to the next trade date; the module keeps the day as its "
            "own short trade date (data.cme_calendar convention)."
        ),
    ),
    date(2019, 9, 2): Citation(
        _Z19,
        (
            "CME Group Globex Labor Day Holiday Schedule: August 30, 2019 - September 3, 2019 ... "
            "Calendar Date|Friday,August 30|Sunday,Sept 1 into Monday,Sept 2|Monday, Sept 2|Monday,"
            " Sept 2 into Tuesday, Sept 3 ... Product|CLOSE|OPEN|HALT|OPEN ... FX |Regular @ 1600 "
            "CT / 2100 UTC|Regular @ 1700 CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / "
            "2200 UTC"
        ),
        _Z19,
        (
            "Product|CLOSE|OPEN|HALT|OPEN ... FX |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT / "
            "2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-labor-day-holiday-schedule-compact.xls. CME "
            "books this Globex session to the next trade date; the module keeps the day as its own "
            "short trade date (data.cme_calendar convention)."
        ),
    ),
    date(2019, 11, 28): Citation(
        _Z19,
        (
            "CME Group Globex Thanksgiving Holiday Schedule: November 27, 2019 - November 29, 2019 "
            "... Products|Wednesday ,November 27|Wednesday, November 27|Thursday ,November "
            "28|Thursday , November 28|Friday November 29|Friday November 29 ... "
            "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... FX |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 "
            "CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1215 CT/ 1815 "
            "UTC"
        ),
        _Z19,
        (
            "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... FX |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 "
            "CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1215 CT/ 1815 "
            "UTC"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-thanksgiving-holiday-schedule-compact.xls. "
            "HALT column (Thursday, November 28) 1200 CT. CME books this Globex session to the "
            "next trade date; the module keeps the day as its own short trade date "
            "(data.cme_calendar convention)."
        ),
    ),
    date(2019, 11, 29): Citation(
        _Z19,
        (
            "CME Group Globex Thanksgiving Holiday Schedule: November 27, 2019 - November 29, 2019 "
            "... Products|Wednesday ,November 27|Wednesday, November 27|Thursday ,November "
            "28|Thursday , November 28|Friday November 29|Friday November 29 ... "
            "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... FX |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 "
            "CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1215 CT/ 1815 "
            "UTC"
        ),
        _Z19,
        (
            "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... FX |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 "
            "CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1215 CT/ 1815 "
            "UTC"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-thanksgiving-holiday-schedule-compact.xls. "
            "CLOSE column (Friday November 29) Early @ 1215 CT; reopen Sunday 17:00 CT."
        ),
    ),
    date(2019, 12, 24): Citation(
        _Z19,
        (
            "CME Group Globex Christmas Holiday Schedule: December 24, 2019 - December 26, 2019 "
            "... Products|Tuesday, Dec 24|Wednesday,Dec 25|Wednesday December 25|Thursday,Dec "
            "26|Thursday, Dec 26 ... | Early Closes|CLOSED|OPEN|Open|CLOSED ... FX |Early @ 1215 "
            "CT / 1815 UTC|Closed for Christmas|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / "
            "2200 UTC"
        ),
        _Z19,
        (
            "| Early Closes|CLOSED|OPEN|Open|CLOSED ... FX |Early @ 1215 CT / 1815 UTC|Closed for "
            "Christmas|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-christmas-holiday-schedule-compact.xls. No "
            "17:00 CT reopen on December 24."
        ),
    ),
    date(2019, 12, 25): Citation(
        _Z19,
        (
            "CME Group Globex Christmas Holiday Schedule: December 24, 2019 - December 26, 2019 "
            "... Products|Tuesday, Dec 24|Wednesday,Dec 25|Wednesday December 25|Thursday,Dec "
            "26|Thursday, Dec 26 ... | Early Closes|CLOSED|OPEN|Open|CLOSED ... FX |Early @ 1215 "
            "CT / 1815 UTC|Closed for Christmas|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / "
            "2200 UTC"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-christmas-holiday-schedule-compact.xls. "
            "Closed for Christmas; reopen Wednesday December 25 17:00 CT."
        ),
    ),
    date(2020, 1, 1): Citation(
        _Z19,
        (
            "CME Group Globex New Years Holiday Schedule: December 31, 2019 - January 2, 2020 ... "
            "Calendar Trade|Tuesday, Dec 31|Wednessday, Jan 1 |Wednesday, Jan 1|Thursday, Jan "
            "2|Thursday, Jan 2 ... |CLOSE|CLOSED |OPEN|Open|CLOSE ... FX |Regular @ 1600 CT / 2200 "
            "UTC|Closed for New Year's|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-new-years-holiday-schedule-compact.xls. "
            "Closed for New Year's; reopen Wednesday January 1 17:00 CT."
        ),
    ),
    date(2020, 1, 20): Citation(
        _Z20,
        (
            "CME Group Globex Martin Luther King Day Holiday Schedule: January 17, 2020 - January "
            "21, 2020 ... Calendar Date|Friday, Jan 17|Sunday, Jan 19 into Monday, Jan 20|Monday, "
            "Jan 20|Monday, Jan 20 into Tuesday, Jan 21 ... Products|CLOSE|OPEN|HALT|OPEN ... FX "
            "|Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular "
            "@ 1700 CT / 2300 UTC"
        ),
        _Z20,
        (
            "Products|CLOSE|OPEN|HALT|OPEN ... FX |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT "
            "/ 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC"
        ),
        note=(
            "Zip member 2020-martin-luther-king-holiday-schedule-compact.xls. CME books this "
            "Globex session to the next trade date; the module keeps the day as its own short "
            "trade date (data.cme_calendar convention)."
        ),
    ),
    date(2020, 2, 17): Citation(
        _Z20,
        (
            "CME Group Globex Presidents Day Holiday Schedule: February 14, 2020 - February 18, "
            "2020 ... Calendar Date|Friday, Feb 14|Sunday, Feb 16 into Monday, Feb 17|Monday,Feb "
            "17|Monday, Feb 17 into Tuesday, Feb 18 ... Products|CLOSE|OPEN|HALT|OPEN ... FX "
            "|Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular "
            "@ 1700 CT / 2300 UTC"
        ),
        _Z20,
        (
            "Products|CLOSE|OPEN|HALT|OPEN ... FX |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT "
            "/ 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC"
        ),
        note=(
            "Zip member 2020-presidents-day-holiday-schedule-compact.xls. CME books this Globex "
            "session to the next trade date; the module keeps the day as its own short trade date "
            "(data.cme_calendar convention)."
        ),
    ),
    date(2020, 4, 10): Citation(
        _Z20,
        (
            "CME Group Globex Good Friday Holiday Schedule: April 9,2020 to April 13, 2020 ... "
            "Calendar Date|Thursday April 9|Friday April 10|Sunday, April 12 into Monday, April 13 "
            "... Product|CLOSE|CLOSED|OPEN ... FX |Regular @ 1600 CT / 2100 UTC|Closed for Good "
            "Friday|Regular @ 1700 CT / 2200 UTC"
        ),
        note="Zip member 2020-good-friday-holiday-compact.xls.",
    ),
    date(2020, 5, 25): Citation(
        _Z20,
        (
            "CME Group Globex Memorial Day Holiday Schedule: May 22, 2020 - May 26, 2020 ... "
            "Calendar Date|Friday,May 22|Sunday,May 24 into Monday,May 25|Monday, May 25|Mon,May "
            "25 into Tues,May 26 ... Product|CLOSE|OPEN|HALT|OPEN ... FX |Regular @ 1600 CT / 2100 "
            "UTC|Regular @ 1700 CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        _Z20,
        (
            "Product|CLOSE|OPEN|HALT|OPEN ... FX |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT / "
            "2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "Zip member 2020-memorial-day-holiday-schedule-compact.xls. CME books this Globex "
            "session to the next trade date; the module keeps the day as its own short trade date "
            "(data.cme_calendar convention)."
        ),
    ),
    date(2020, 7, 3): Citation(
        _Z20,
        (
            "CME Group Globex Independence Day Holiday Schedule: July 2, 2020 to July 6, 2020 ... "
            "Calendar Date|Thursday July 2|Thursday , July 2|Friday July 3|Sunday July 5 into "
            "Monday July 6 ... Product|CLOSE|OPEN|ClOSE|OPEN ... FX |Regular @ 1600 CT / 2100 "
            "UTC|Regular @ 1700 CT/ 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        _Z20,
        (
            "Product|CLOSE|OPEN|ClOSE|OPEN ... FX |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT/ "
            "2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "Zip member 2020-4th-of-july-holiday-schedule-compact.xls. Column labelled ClOSE "
            "(Friday July 3) 1200 CT; next open Sunday July 5 17:00 CT. CME books this Globex "
            "session to the next trade date; the module keeps the day as its own short trade date "
            "(data.cme_calendar convention)."
        ),
    ),
    date(2020, 9, 7): Citation(
        _Z20,
        (
            "CME Group Globex Labor Day Holiday Schedule: September 4, 2020 - September 8, 2020 "
            "... Calendar Date|Friday,September 4|Sunday,Sept 6 into Monday,Sept 7|Monday, Sept "
            "7|Monday, Sept 7 into Tuesday, Sept 8 ... Product|CLOSE|OPEN|HALT|OPEN ... FX "
            "|Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT / 2200 UTC|1200 CT / 1700 UTC|Regular "
            "@ 1700 CT / 2200 UTC"
        ),
        _Z20,
        (
            "Product|CLOSE|OPEN|HALT|OPEN ... FX |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT / "
            "2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "Zip member 2020-labor-day-holiday-schedule-compact.xls. CME books this Globex session "
            "to the next trade date; the module keeps the day as its own short trade date "
            "(data.cme_calendar convention)."
        ),
    ),
    date(2020, 11, 26): Citation(
        _Z20,
        (
            "CME Group Globex Thanksgiving Holiday Schedule: November 25, 2020 - November 27, 2020 "
            "... Products|Wednesday ,November 25|Wednesday, November 25|Thursday ,November "
            "26|Thursday , November 26|Friday November 27|Friday November 27 ... "
            "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... FX |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 "
            "CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1215 CT/ 1815 "
            "UTC"
        ),
        _Z20,
        (
            "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... FX |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 "
            "CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1215 CT/ 1815 "
            "UTC"
        ),
        note=(
            "Zip member 2020-thanksgiving-holiday-schedule-compact.xls. HALT column (Thursday, "
            "November 26) 1200 CT. CME books this Globex session to the next trade date; the "
            "module keeps the day as its own short trade date (data.cme_calendar convention)."
        ),
    ),
    date(2020, 11, 27): Citation(
        _Z20,
        (
            "CME Group Globex Thanksgiving Holiday Schedule: November 25, 2020 - November 27, 2020 "
            "... Products|Wednesday ,November 25|Wednesday, November 25|Thursday ,November "
            "26|Thursday , November 26|Friday November 27|Friday November 27 ... "
            "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... FX |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 "
            "CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1215 CT/ 1815 "
            "UTC"
        ),
        _Z20,
        (
            "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... FX |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 "
            "CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1215 CT/ 1815 "
            "UTC"
        ),
        note=(
            "Zip member 2020-thanksgiving-holiday-schedule-compact.xls. CLOSE column (Friday "
            "November 27) Early @ 1215 CT; reopen Sunday 17:00 CT."
        ),
    ),
    date(2020, 12, 24): Citation(
        _Z20,
        (
            "CME Group Globex Christmas Holiday Schedule: December 24, 2020 - December 28, 2020 "
            "... Products|Thursday, Dec 24|Friday,Dec 25|Sunday 27|Monday,Dec 28|Monday, Dec 28 "
            "... | Early Closes|CLOSED|OPEN|Open|CLOSED ... FX |Early @ 1215 CT / 1815 UTC|Closed "
            "for Christmas|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
        ),
        _Z20,
        (
            "| Early Closes|CLOSED|OPEN|Open|CLOSED ... FX |Early @ 1215 CT / 1815 UTC|Closed for "
            "Christmas|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
        ),
        note=(
            "Zip member 2020-christmas-holiday-schedule-compact.xls. No 17:00 CT reopen on "
            "December 24."
        ),
    ),
    date(2020, 12, 25): Citation(
        _Z20,
        (
            "CME Group Globex Christmas Holiday Schedule: December 24, 2020 - December 28, 2020 "
            "... Products|Thursday, Dec 24|Friday,Dec 25|Sunday 27|Monday,Dec 28|Monday, Dec 28 "
            "... | Early Closes|CLOSED|OPEN|Open|CLOSED ... FX |Early @ 1215 CT / 1815 UTC|Closed "
            "for Christmas|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
        ),
        note=(
            "Zip member 2020-christmas-holiday-schedule-compact.xls. Closed for Christmas; reopen "
            "Sunday December 27 17:00 CT."
        ),
    ),
    date(2021, 1, 1): Citation(
        _Z20,
        (
            "CME Group Globex New Years Holiday Schedule: December 31, 2020 - January 4, 2021 ... "
            "Calendar Trade|Thursday,Dec 31|Friday,Jan 1|Sunday,Jan 3|Monday, Jan 4|Monday, Jan 4 "
            "... |CLOSE|CLOSED |OPEN|OPEN|CLOSE ... FX |Regular @ 1600 CT / 2200 UTC|Closed for "
            "New Year's|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
        ),
        note=(
            "Zip member 2021-new-years-holiday-schedule-compact.xls. Closed for New Year's; reopen "
            "Sunday January 3 17:00 CT."
        ),
    ),
    date(2021, 1, 18): Citation(
        _Z21,
        (
            "CME Group Globex Martin Luther King Day Holiday Schedule: January 15, 2021 - January "
            "19, 2021 ... Calendar Date|Friday, Jan 15|Sunday, Jan 17 into Monday, Jan 18|Monday, "
            "Jan 18|Monday, Jan 18 into Tuesday, Jan 19 ... Products|CLOSE|OPEN|HALT|OPEN ... FX "
            "|Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular "
            "@ 1700 CT / 2300 UTC"
        ),
        _Z21,
        (
            "Products|CLOSE|OPEN|HALT|OPEN ... FX |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT "
            "/ 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC"
        ),
        note=(
            "Zip member 2021-mlk-day-schedule-compact.xls. CME books this Globex session to the "
            "next trade date; the module keeps the day as its own short trade date "
            "(data.cme_calendar convention)."
        ),
    ),
    date(2021, 2, 15): Citation(
        _Z21,
        (
            "CME Group Globex Presidents Day Holiday Schedule: February 12, 2021 - February 16, "
            "2021 ... Calendar Date|Friday, Feb 12|Sunday, Feb 14 into Monday, Feb 15|Monday,Feb "
            "15|Monday, Feb 15 into Tuesday, Feb 16 ... Products|CLOSE|OPEN|HALT|OPEN ... FX "
            "|Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular "
            "@ 1700 CT / 2300 UTC"
        ),
        _Z21,
        (
            "Products|CLOSE|OPEN|HALT|OPEN ... FX |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT "
            "/ 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC"
        ),
        note=(
            "Zip member 2021-presidents-day-holiday-schedule-compact.xls. CME books this Globex "
            "session to the next trade date; the module keeps the day as its own short trade date "
            "(data.cme_calendar convention)."
        ),
    ),
    date(2021, 4, 2): Citation(
        _Z21,
        (
            "CME Group Globex Good Friday Holiday Schedule: April 1,2021 to April 5, 2021 ... "
            "Trade Date|Thursday,April 1|Friday, April 2|Friday, April 2|Monday, April 5 ... "
            "Calendar Date|Thursday April 1|Thursday,April 1|Friday April 2|Sunday, April 4 into "
            "Monday, April 5 ... Product|CLOSE|OPEN|CLOSED|OPEN ... FX |Regular @ 1600 CT / 2100 "
            "UTC|Regular @ 1700 CT / 2200 UTC|Closed @ 1015 CT / 1515 UTC|Regular @ 1700 CT / 2200 "
            "UTC"
        ),
        _Z21,
        (
            "Product|CLOSE|OPEN|CLOSED|OPEN ... FX |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT "
            "/ 2200 UTC|Closed @ 1015 CT / 1515 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "Zip member 2021-good-friday-holiday-schedule-compact.xls. FX traded Thursday 17:00 CT "
            "to Friday 10:15 CT for trade date Friday April 2 (equity closed 08:15 CT); reopen "
            "Sunday 17:00 CT."
        ),
    ),
    date(2021, 5, 31): Citation(
        _Z21,
        (
            "CME Group Globex Memorial Day Holiday Schedule: May 28, 2021 - June 1st, 2021 ... "
            "Calendar Date|Friday,May 28|Sunday,May 30|Monday, May 31|Monday, May 31 into Tues, "
            "June 1 ... Product|CLOSE|OPEN|HALT|OPEN ... FX |Regular @ 1600 CT / 2100 UTC|Regular "
            "@ 1700 CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        _Z21,
        (
            "Product|CLOSE|OPEN|HALT|OPEN ... FX |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT / "
            "2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "Zip member 2021-memorial-day-holiday-schedule-compact.xls. CME books this Globex "
            "session to the next trade date; the module keeps the day as its own short trade date "
            "(data.cme_calendar convention)."
        ),
    ),
    date(2021, 7, 5): Citation(
        _Z21,
        (
            "CME Group Globex Independence Day Holiday Schedule: July 2, 2021 to July 6, 2021 ... "
            "Calendar Date|Friday July 2|Sunday July 4|Monday July 5|Monday July 5 ... "
            "Product|CLOSE|OPEN|HALT|OPEN ... FX |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT/ "
            "2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        _Z21,
        (
            "Product|CLOSE|OPEN|HALT|OPEN ... FX |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT/ "
            "2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "Zip member 2021-independence-day-holiday-schedule-compact.xls. CME books this Globex "
            "session to the next trade date; the module keeps the day as its own short trade date "
            "(data.cme_calendar convention)."
        ),
    ),
    date(2021, 9, 6): Citation(
        _Z21,
        (
            "CME Group Globex Labor Day Holiday Schedule: September 3, 2021 - September 7, 2021 "
            "... Calendar Date|Friday,September 3|Sunday,Sept 5 into Monday,Sept 6|Monday, Sept "
            "6|Monday, Sept 6 into Tuesday, Sept 7 ... Product|CLOSE|OPEN|HALT|OPEN ... FX "
            "|Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT / 2200 UTC|1200 CT / 1700 UTC|Regular "
            "@ 1700 CT / 2200 UTC"
        ),
        _Z21,
        (
            "Product|CLOSE|OPEN|HALT|OPEN ... FX |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT / "
            "2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "Zip member 2021-labor-day-holiday-schedule-compact.xls. CME books this Globex session "
            "to the next trade date; the module keeps the day as its own short trade date "
            "(data.cme_calendar convention)."
        ),
    ),
    date(2021, 11, 25): Citation(
        _Z21,
        (
            "CME Group Globex Thanksgiving Holiday Schedule: November 24, 2021 - November 26, 2021 "
            "... Products|Wednesday ,November 24|Wednesday, November 24|Thursday ,November "
            "25|Thursday , November 25|Friday November 26|Friday November 26 ... "
            "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... FX |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 "
            "CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1215 CT/ 1815 "
            "UTC"
        ),
        _Z21,
        (
            "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... FX |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 "
            "CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1215 CT/ 1815 "
            "UTC"
        ),
        note=(
            "Zip member 2021-thanksgiving-holiday-schedule-compact.xls. HALT column (Thursday, "
            "November 25) 1200 CT. CME books this Globex session to the next trade date; the "
            "module keeps the day as its own short trade date (data.cme_calendar convention)."
        ),
    ),
    date(2021, 11, 26): Citation(
        _Z21,
        (
            "CME Group Globex Thanksgiving Holiday Schedule: November 24, 2021 - November 26, 2021 "
            "... Products|Wednesday ,November 24|Wednesday, November 24|Thursday ,November "
            "25|Thursday , November 25|Friday November 26|Friday November 26 ... "
            "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... FX |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 "
            "CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1215 CT/ 1815 "
            "UTC"
        ),
        _Z21,
        (
            "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... FX |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 "
            "CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1215 CT/ 1815 "
            "UTC"
        ),
        note=(
            "Zip member 2021-thanksgiving-holiday-schedule-compact.xls. CLOSE column (Friday "
            "November 26) Early @ 1215 CT; reopen Sunday 17:00 CT."
        ),
    ),
    date(2021, 12, 24): Citation(
        _Z21,
        (
            "CME Group Globex Christmas Holiday Schedule: December 23, 2021 - December 27, 2021 "
            "... Products|Thursday, Dec 23|Friday,Dec 24|Sunday 26|Monday,Dec 27 ... | "
            "Close|CLOSED|OPEN|Close ... FX |Regular per Product|Closed for Christmas|Regular @ "
            "1700 CT / 2300 UTC|Regular @ 1600 CT / 2200 UTC"
        ),
        note=(
            "Zip member 2021-christmas-holiday-schedule-compact.xls. Thursday December 23 regular "
            "close; Friday December 24 closed; reopen Sunday December 26 17:00 CT."
        ),
    ),
    date(2022, 4, 15): Citation(
        _HC + "2022-good-friday-holiday-schedule-compact.xls",
        (
            "CME Group Globex Good Friday Holiday Schedule: April 14,2022 to April 18, 2022 ... "
            "Calendar Date|Thursday April 14|Friday April 15|Sunday, April 17 into Monday, April "
            "18 ... Product|CLOSE|CLOSED|OPEN ... FX |Regular @ 1600 CT / 2100 UTC|Closed for Good "
            "Friday|Regular @ 1700 CT / 2200 UTC"
        ),
    ),
    date(2022, 11, 25): Citation(
        _HC + "2022-thanksgiving-holiday-schedule-compact.xls",
        (
            "CME Group Globex Thanksgiving Holiday Schedule: November 23, 2022 - November 25, 2022 "
            "... Products|Wednesday ,November 23|Wednesday, November 23|Thursday ,November "
            "24|Thursday , November 24|Friday November 25|Friday November 25 ... "
            "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... FX |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 "
            "CT / 2300 UTC|1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1215 CT/ 1815 "
            "UTC"
        ),
        _HC + "2022-thanksgiving-holiday-schedule-compact.xls",
        (
            "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... FX |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 "
            "CT / 2300 UTC|1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1215 CT/ 1815 "
            "UTC"
        ),
        note=(
            "CLOSE column (Friday November 25) Early @ 1215 CT; reopen Sunday 17:00 CT. "
            "Thanksgiving Day itself (HALT 1600 CT) is a regular-hours FX session: "
            "NO_ENTRY_FINDINGS."
        ),
    ),
    date(2022, 12, 26): Citation(
        _HC + "2022-christmas-holiday-schedule.xls",
        (
            "Updated 6/29/2022|CME Group Globex Christmas Holiday Schedule: December 23, 2022 - "
            "December 27, 2022 ... Calendar Date|Friday, December 23||||||||Monday, December "
            "26||||||||||||||||Tuesday, December 27 ... FX Products|04:00:00 PM||||||||Globex "
            "Closed||||||||||04:00:00 PM|05:00:00 PM|||||||04:00:00 PM"
        ),
        note=(
            "Full schedule (merged headers read with xlrd): Friday December 23 close 16:00, "
            "'Globex Closed' under Monday December 26, pre-open 16:00 and open 17:00 Monday "
            "December 26 for trade date Tuesday December 27; no Sunday open."
        ),
    ),
    date(2023, 1, 2): Citation(
        _HC + "2023-new-years-holiday-schedule-compact.xls",
        (
            "CME Group Globex New Years Holiday Schedule: December 30, 2022 - January 3, 2023 ... "
            "Calendar Trade|Friday,Dec 30|Sunday, Jan 1 and Monday, Jan 2|Monday,Jan 2|Tuesday, "
            "Jan 3|Tuesday, Jan 3 ... |CLOSE|Closed|OPEN|OPEN|CLOSE ... FX |Regular @ 1600 CT / "
            "2200 UTC|Globex Closed|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
        ),
        note=(
            "Friday December 30 regular close; Globex closed Sunday January 1 and Monday January "
            "2; reopen Monday January 2 17:00 CT."
        ),
    ),
    date(2023, 4, 7): Citation(
        _FILES + "good-friday.pdf",
        (
            "PRODUCT NAME THURSDAY, 6 APR 2023 FRIDAY, 7 APR 2023 ... FX TRADE DATE: FRI 7 APR "
            "10:15 (CLOSED)"
        ),
        _FILES + "good-friday.pdf",
        "FX TRADE DATE: FRI 7 APR 10:15 (CLOSED)",
        note=(
            "cmegroup.com/files/good-friday.pdf (captured 2024-07-08; content dated 6-7 April "
            "2023). CME's clearing advisory: 'FX & Interest Rate markets will be settled on April "
            "7th'."
        ),
    ),
    date(2023, 11, 24): Citation(
        _TH + "thanksgiving-day-2023.pdf",
        (
            "PRODUCT NAME WEDNESDAY, 22 NOVEMBER 2023 THURSDAY, 23 NOVEMBER 2023 FRIDAY, 24 "
            "NOVEMBER 2023 ... FX TRADE DATE: FRI 24 NOV 16:00 (PREOPEN) HALT ... 12:15 (CLOSED)"
        ),
        _svc("2023-11-22", "2023-11-24", "1720455278656"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2023-11-24","events":[{"tradingDate":"2023-11-24","eventTime":"12:15",'
            '"marketEventType":"closed"}]}'
        ),
        note="Time part: CME's trading-hours service, 6E, capture 2024-07-08 (after the date).",
    ),
    date(2023, 12, 25): Citation(
        _TH + "christmas-day-2023.pdf",
        (
            "PRODUCT NAME MONDAY, 25 DECEMBER 2023 TUESDAY, 26 DECEMBER 2023 ... TRADE DATE: TUES "
            "26 DEC TRADE DATE: TUES 26 DEC 16:00 (CLOSED) ... FX 16:00 (PREOPEN) TRADE DATE: WED "
            "27 DEC"
        ),
        note=(
            "Monday 25 December: FX pre-open 16:00 and open 17:00 for trade date Tuesday 26 "
            "December only (no Sunday open). The 6E service capture of 2024-07-08 agrees."
        ),
    ),
    date(2024, 1, 1): Citation(
        _TH + "new-years-day-2024.pdf",
        (
            "PRODUCT NAME MONDAY, 1 JANUARY 2024 TUESDAY, 2 JANUARY 2024 ... FX 16:00 (PREOPEN) "
            "TRADE DATE: WED 3 JAN"
        ),
        note=(
            "Monday 1 January: FX pre-open 16:00, open 17:00 for trade date Tuesday 2 January "
            "only. The 6E service capture of 2024-07-08 agrees."
        ),
    ),
    date(2024, 3, 29): Citation(
        _TH_PAGE,
        (
            "Thursday March 28 all markets have a regular close. No trading for Friday March 29 "
            "trade date in observance of Good Friday."
        ),
        note=(
            "cmegroup.com/trading-hours.html capture 2024-02-22. The 6E service capture of "
            "2024-07-08 agrees (2024-03-28 16:00 closed, no events on 2024-03-29)."
        ),
    ),
    date(2024, 11, 29): Citation(
        _svc("2024-11-27", "2024-11-29", "1734710019535"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2024-11-28","events":[{"tradingDate":"2024-11-29","eventTime":"16:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2024-11-29","eventTime":"17:00",'
            '"marketEventType":"open"}]} ... {"groupCode":"6E","eventDate":"2024-11-29",'
            '"events":[{"tradingDate":"2024-11-29","eventTime":"13:45",'
            '"marketEventType":"closed"}]}'
        ),
        _svc("2024-11-27", "2024-11-29", "1734710019535"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2024-11-29","events":[{"tradingDate":"2024-11-29","eventTime":"13:45",'
            '"marketEventType":"closed"}]}'
        ),
        note=(
            "CONFLICT: CME's own capture of 2024-07-08 (_svc('2024-11-27', '2024-11-29', "
            "'1720455278685')) gave 12:15 closed; the later capture of 2024-12-20 (after the date, "
            "cited) gives 13:45. CME changed the FX early close on the day after Thanksgiving "
            "(12:15 -> 13:45 CT) and on Christmas Eve (12:15 -> 12:45 CT) between its 2024-07-08 "
            "and 2024-12-20 service captures; 2023 and earlier FX closed at 12:15 CT on both days. "
            "Holdout-2 date: never checked against bars. A secondary source (Insignia Futures, "
            "2024-11-26) says 12:15."
        ),
    ),
    date(2024, 12, 24): Citation(
        _svc("2024-12-24", "2024-12-26", "1734710019537"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2024-12-24","events":[{"tradingDate":"2024-12-24","eventTime":"12:45",'
            '"marketEventType":"closed"}]} ... {"groupCode":"6E","eventDate":"2024-12-25",'
            '"events":[{"tradingDate":"2024-12-26","eventTime":"16:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2024-12-26","eventTime":"17:00",'
            '"marketEventType":"open"}]}'
        ),
        _svc("2024-12-24", "2024-12-26", "1734710019537"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2024-12-24","events":[{"tradingDate":"2024-12-24","eventTime":"12:45",'
            '"marketEventType":"closed"}]}'
        ),
        note=(
            "CONFLICT: CME's capture of 2024-07-08 (_svc('2024-12-24', '2024-12-26', "
            "'1720455278686')) gave 12:15 closed; the capture of 2024-12-20 (four days before, "
            "cited) gives 12:45. CME changed the FX early close on the day after Thanksgiving "
            "(12:15 -> 13:45 CT) and on Christmas Eve (12:15 -> 12:45 CT) between its 2024-07-08 "
            "and 2024-12-20 service captures; 2023 and earlier FX closed at 12:15 CT on both days. "
            "A secondary source (Insignia Futures) also gives 12:45 for FX. Holdout-2 date: never "
            "checked against bars."
        ),
    ),
    date(2024, 12, 25): Citation(
        _svc("2024-12-24", "2024-12-26", "1734710019537"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2024-12-24","events":[{"tradingDate":"2024-12-24","eventTime":"12:45",'
            '"marketEventType":"closed"}]} ... {"groupCode":"6E","eventDate":"2024-12-25",'
            '"events":[{"tradingDate":"2024-12-26","eventTime":"16:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2024-12-26","eventTime":"17:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "No reopen on December 24 after the early close; pre-open 16:00 and open 17:00 on "
            "December 25 for trade date December 26."
        ),
    ),
    date(2025, 1, 1): Citation(
        _svc("2024-12-31", "2025-01-02", "1720455278688"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2024-12-31","events":[{"tradingDate":"2024-12-31","eventTime":"16:00",'
            '"marketEventType":"closed"}]} ... {"groupCode":"6E","eventDate":"2025-01-01",'
            '"events":[{"tradingDate":"2025-01-02","eventTime":"16:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2025-01-02","eventTime":"17:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "December 31 16:00 closed with no reopen; January 1 pre-open 16:00, open 17:00 for "
            "trade date January 2."
        ),
    ),
    date(2025, 4, 18): Citation(
        _TH_PAGE,
        (
            "Thursday April 17th all markets have a regular close. No trading for Friday, April "
            "18th trade date in observance of Good Friday."
        ),
        note=(
            "cmegroup.com/trading-hours.html capture 2024-11-12. The 6E service capture of "
            "2024-12-20 agrees (2025-04-17 16:00 closed, no events on 2025-04-18)."
        ),
    ),
    date(2025, 7, 4): Citation(
        _svc("2025-07-03", "2025-07-05", "1734710019545"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2025-07-03","events":[{"tradingDate":"2025-07-03","eventTime":"16:00",'
            '"marketEventType":"closed"},{"tradingDate":"2025-07-04","eventTime":"16:45",'
            '"marketEventType":"preopen"},{"tradingDate":"2025-07-04","eventTime":"17:00",'
            '"marketEventType":"open"}]} ... {"groupCode":"6E","eventDate":"2025-07-04",'
            '"events":[{"tradingDate":"2025-07-04","eventTime":"12:00",'
            '"marketEventType":"closed"}]}'
        ),
        _svc("2025-07-03", "2025-07-05", "1734710019545"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2025-07-04","events":[{"tradingDate":"2025-07-04","eventTime":"12:00",'
            '"marketEventType":"closed"}]}'
        ),
        note=(
            "Friday holiday: 6E 12:00 closed for trade date 2025-07-04, reopen Sunday 17:00 CT. "
            "Capture 2024-12-20 (before the date). July 3 kept the regular 16:00 close."
        ),
    ),
    date(2025, 11, 28): Citation(
        _svc("2025-11-26", "2025-11-28", "1769649703060"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2025-11-27","events":[{"tradingDate":"2025-11-28","eventTime":"16:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"17:00",'
            '"marketEventType":"open"}]} ... {"groupCode":"6E","eventDate":"2025-11-28",'
            '"events":[{"tradingDate":"2025-11-28","eventTime":"07:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"07:30",'
            '"marketEventType":"open"},{"tradingDate":"2025-11-28","eventTime":"13:45",'
            '"marketEventType":"closed"}]}'
        ),
        _svc("2025-11-26", "2025-11-28", "1769649703060"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28","eventTime":"07:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"07:30",'
            '"marketEventType":"open"},{"tradingDate":"2025-11-28","eventTime":"13:45",'
            '"marketEventType":"closed"}]}'
        ),
        note=(
            "Capture 2026-01-29 (after the date); the capture of 2024-12-20 (_svc('2025-11-26', "
            "'2025-11-28', '1734710019547')) also gives 13:45. CME changed the FX early close on "
            "the day after Thanksgiving (12:15 -> 13:45 CT) and on Christmas Eve (12:15 -> 12:45 "
            "CT) between its 2024-07-08 and 2024-12-20 service captures; 2023 and earlier FX "
            "closed at 12:15 CT on both days. The 07:00 pre-open and 07:30 open on 2025-11-28 "
            "record the reopen after an unscheduled Globex halt: LATE_OPENS. CME's 2025 settlement "
            "notice (captured 2024-12-14) gives an FX settlement at 12:00 CT that day."
        ),
    ),
    date(2025, 12, 24): Citation(
        _svc("2025-12-24", "2025-12-26", "1769649703064"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2025-12-24","events":[{"tradingDate":"2025-12-24","eventTime":"12:45",'
            '"marketEventType":"closed"}]} ... {"groupCode":"6E","eventDate":"2025-12-25",'
            '"events":[{"tradingDate":"2025-12-26","eventTime":"16:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2025-12-26","eventTime":"17:00",'
            '"marketEventType":"open"}]}'
        ),
        _svc("2025-12-24", "2025-12-26", "1769649703064"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2025-12-24","events":[{"tradingDate":"2025-12-24","eventTime":"12:45",'
            '"marketEventType":"closed"}]}'
        ),
        note=(
            "Capture 2026-01-29 (after the date). CME changed the FX early close on the day after "
            "Thanksgiving (12:15 -> 13:45 CT) and on Christmas Eve (12:15 -> 12:45 CT) between its "
            "2024-07-08 and 2024-12-20 service captures; 2023 and earlier FX closed at 12:15 CT on "
            "both days. CME's 2025 settlement notice (captured 2024-12-14) gives an FX settlement "
            "at 12:00 CT that day."
        ),
    ),
    date(2025, 12, 25): Citation(
        _svc("2025-12-24", "2025-12-26", "1769649703064"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2025-12-24","events":[{"tradingDate":"2025-12-24","eventTime":"12:45",'
            '"marketEventType":"closed"}]} ... {"groupCode":"6E","eventDate":"2025-12-25",'
            '"events":[{"tradingDate":"2025-12-26","eventTime":"16:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2025-12-26","eventTime":"17:00",'
            '"marketEventType":"open"}]}'
        ),
    ),
    date(2026, 1, 1): Citation(
        _svc("2025-12-31", "2026-01-02", "1769649703066"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2025-12-31","events":[{"tradingDate":"2025-12-31","eventTime":"16:00",'
            '"marketEventType":"closed"}]} ... {"groupCode":"6E","eventDate":"2026-01-01",'
            '"events":[{"tradingDate":"2026-01-02","eventTime":"16:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2026-01-02","eventTime":"17:00",'
            '"marketEventType":"open"}]}'
        ),
    ),
    date(2026, 4, 3): Citation(
        _HC + "2026/2026-good-friday-clearing-advisory.pdf",
        "FX & Interest Rate markets will be settled on April 3rd",
        _svc("2026-04-01", "2026-04-03", "1769649703072"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2026-04-02","events":[{"tradingDate":"2026-04-02","eventTime":"16:00",'
            '"marketEventType":"closed"},{"tradingDate":"2026-04-03","eventTime":"16:45",'
            '"marketEventType":"preopen"},{"tradingDate":"2026-04-03","eventTime":"17:00",'
            '"marketEventType":"open"}]} ... {"groupCode":"6E","eventDate":"2026-04-03",'
            '"events":[{"tradingDate":"2026-04-03","eventTime":"10:15",'
            '"marketEventType":"closed"}]}'
        ),
        note=(
            "Time part: 6E service capture 2026-01-29 (before the date): 10:15 closed for trade "
            "date 2026-04-03 (equity 08:15 in the same capture)."
        ),
    ),
    date(2026, 6, 19): Citation(
        _svc("2026-06-17", "2026-06-19", "1769649703075"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2026-06-18","events":[{"tradingDate":"2026-06-18","eventTime":"16:00",'
            '"marketEventType":"closed"},{"tradingDate":"2026-06-22","eventTime":"16:45",'
            '"marketEventType":"preopen"},{"tradingDate":"2026-06-22","eventTime":"17:00",'
            '"marketEventType":"open"}]} ... {"groupCode":"6E","eventDate":"2026-06-19",'
            '"events":[{"tradingDate":"2026-06-22","eventTime":"12:00",'
            '"marketEventType":"closed"}]}'
        ),
        _svc("2026-06-17", "2026-06-19", "1769649703075"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2026-06-19","events":[{"tradingDate":"2026-06-22","eventTime":"12:00",'
            '"marketEventType":"closed"}]}'
        ),
        note=(
            "Friday holiday: 6E 12:00 closed, trade date 2026-06-22 (CME books it to Monday); "
            "reopen Sunday 17:00 CT. Captures 2026-01-29 (cited) and 2026-06-19 agree."
        ),
    ),
}

LATE_OPEN_SOURCES: dict[date, Citation] = {
    date(2025, 11, 28): Citation(
        _svc("2025-11-26", "2025-11-28", "1769649703060"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28","eventTime":"07:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"07:30",'
            '"marketEventType":"open"},{"tradingDate":"2025-11-28","eventTime":"13:45",'
            '"marketEventType":"closed"}]}'
        ),
        _svc("2025-11-26", "2025-11-28", "1769649703060"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28","eventTime":"07:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"07:30",'
            '"marketEventType":"open"},{"tradingDate":"2025-11-28","eventTime":"13:45",'
            '"marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours service (6E, capture 2026-01-29, after the date) records a 07:00 "
            "pre-open and 07:30 open on 2025-11-28, events absent from the capture of 2024-12-20 "
            "(the scheduled day after Thanksgiving had no morning open). The time trading stopped "
            "(on the evening of 2025-11-27 or later) is not in any source retrieved; the cause is "
            "not stated in this document. Unscheduled: the lead decides whether the bar builder "
            "uses it."
        ),
    ),
}

# Days CME states as regular FX sessions (US holidays with regular FX hours from 2022, eves of
# holidays, the 2025 Day of Mourning): no entry, kept with their evidence so the absence is a
# recorded finding.
NO_ENTRY_FINDINGS: dict[date, Citation] = {
    date(2019, 7, 3): Citation(
        _Z19,
        (
            "CME Group Globex Independence Day Holiday Schedule: July 3, 2019 to July 5, 2019 ... "
            "Calendar Date|Wednesday July 3 |Wednesday,July 3|Thursday July 4 |Thursday July 4 "
            "into Friday July 5 ... Product|CLOSE|OPEN|HALT|OPEN ... FX |Regular @ 1600 CT / 2100 "
            "UTC|Regular @ 1700 CT/ 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-4th-of-july-holiday-schedule-compact.xls. "
            "Eve of Independence Day: FX CLOSE Regular @ 1600 CT (equity closed early at 12:15 "
            "CT). No entry."
        ),
    ),
    date(2019, 12, 31): Citation(
        _Z19,
        (
            "CME Group Globex New Years Holiday Schedule: December 31, 2019 - January 2, 2020 ... "
            "Calendar Trade|Tuesday, Dec 31|Wednessday, Jan 1 |Wednesday, Jan 1|Thursday, Jan "
            "2|Thursday, Jan 2 ... |CLOSE|CLOSED |OPEN|Open|CLOSE ... FX |Regular @ 1600 CT / 2200 "
            "UTC|Closed for New Year's|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
        ),
        _Z19,
        "New Year’s Eve 2019 Holiday Settlement Times ... CME Group FX Products 12:00:00 CT",
        note=(
            "Zip member globex-trading-schedules/2019-new-years-holiday-schedule-compact.xls. "
            "Time: zip member settlement-notices/2019-new-years-eve-holiday-settlement-times.pdf. "
            "New Year's Eve: FX CLOSE Regular @ 1600 CT. Time part: CME's settlement notice gives "
            "an early FX SETTLEMENT at 12:00 CT; the Globex session is regular. No entry."
        ),
    ),
    date(2020, 7, 2): Citation(
        _Z20,
        (
            "CME Group Globex Independence Day Holiday Schedule: July 2, 2020 to July 6, 2020 ... "
            "Calendar Date|Thursday July 2|Thursday , July 2|Friday July 3|Sunday July 5 into "
            "Monday July 6 ... Product|CLOSE|OPEN|ClOSE|OPEN ... FX |Regular @ 1600 CT / 2100 "
            "UTC|Regular @ 1700 CT/ 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "Zip member 2020-4th-of-july-holiday-schedule-compact.xls. Thursday before the "
            "observed holiday: FX CLOSE Regular @ 1600 CT. No entry."
        ),
    ),
    date(2020, 12, 31): Citation(
        _Z20,
        (
            "CME Group Globex New Years Holiday Schedule: December 31, 2020 - January 4, 2021 ... "
            "Calendar Trade|Thursday,Dec 31|Friday,Jan 1|Sunday,Jan 3|Monday, Jan 4|Monday, Jan 4 "
            "... |CLOSE|CLOSED |OPEN|OPEN|CLOSE ... FX |Regular @ 1600 CT / 2200 UTC|Closed for "
            "New Year's|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
        ),
        note=(
            "Zip member 2021-new-years-holiday-schedule-compact.xls. New Year's Eve: FX CLOSE "
            "Regular @ 1600 CT. No entry."
        ),
    ),
    date(2021, 7, 2): Citation(
        _Z21,
        (
            "CME Group Globex Independence Day Holiday Schedule: July 2, 2021 to July 6, 2021 ... "
            "Calendar Date|Friday July 2|Sunday July 4|Monday July 5|Monday July 5 ... "
            "Product|CLOSE|OPEN|HALT|OPEN ... FX |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT/ "
            "2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "Zip member 2021-independence-day-holiday-schedule-compact.xls. Friday before the "
            "observed holiday: FX CLOSE Regular @ 1600 CT. No entry."
        ),
    ),
    date(2021, 12, 23): Citation(
        _Z21,
        (
            "CME Group Globex Christmas Holiday Schedule: December 23, 2021 - December 27, 2021 "
            "... Products|Thursday, Dec 23|Friday,Dec 24|Sunday 26|Monday,Dec 27 ... | "
            "Close|CLOSED|OPEN|Close ... FX |Regular per Product|Closed for Christmas|Regular @ "
            "1700 CT / 2300 UTC|Regular @ 1600 CT / 2200 UTC"
        ),
        note=(
            "Zip member 2021-christmas-holiday-schedule-compact.xls. Thursday before the observed "
            "Christmas: FX Close 'Regular per Product'. No entry."
        ),
    ),
    date(2021, 12, 31): Citation(
        _Z21,
        (
            "CME Group Globex New Years Holiday Schedule: December 30, 2021 - January 3, 2022 ... "
            "Calendar Trade|Thursday,Dec 30|Thursday,Dec 30|Friday,Dec 31|Friday,Dec 31|Sunday,Jan "
            "2|Monday, Jan 3 ... |CLOSE|OPEN |OPEN |Close|OPEN|OPEN ... FX |Regular @ 1600 CT / "
            "2200 UTC|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT "
            "/ 2300 UTC"
        ),
        note=(
            "Zip member 2022-new-years-holiday-schedule-compact.xls. New Year's Day 2022 fell on a "
            "Saturday: Friday December 31 FX Close Regular @ 1600 CT, reopen Sunday January 2 "
            "17:00 CT. No entry."
        ),
    ),
    date(2022, 1, 3): Citation(
        _Z21,
        (
            "CME Group Globex New Years Holiday Schedule: December 30, 2021 - January 3, 2022 ... "
            "Calendar Trade|Thursday,Dec 30|Thursday,Dec 30|Friday,Dec 31|Friday,Dec 31|Sunday,Jan "
            "2|Monday, Jan 3 ... |CLOSE|OPEN |OPEN |Close|OPEN|OPEN ... FX |Regular @ 1600 CT / "
            "2200 UTC|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT "
            "/ 2300 UTC"
        ),
        note=(
            "Zip member 2022-new-years-holiday-schedule-compact.xls. Monday January 3, 2022: "
            "regular session (opened Sunday January 2 17:00 CT). No entry."
        ),
    ),
    date(2022, 1, 17): Citation(
        _HC + "2022-mlk-day-holiday-schedule-compact.xls",
        (
            "CME Group Globex Martin Luther King Day Holiday Schedule: January 14, 2022 - January "
            "18, 2022 ... Calendar Date|Friday, Jan 14|Sunday, Jan 16 into Monday, Jan 17|Monday, "
            "Jan 17|Monday, Jan 17 into Tuesday, Jan 18 ... Products|CLOSE|OPEN|HALT|OPEN ... FX "
            "|Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1600 CT / 2200 UTC|Regular "
            "@ 1700 CT / 2300 UTC"
        ),
        note=(
            "US holiday with regular FX Globex hours: CME's FX halt is 16:00 CT, the regular daily "
            "close, with the 17:00 CT reopen; no settlement that day and CME books the session to "
            "the next trade date. Same session clock as a regular day: no entry. First holiday "
            "found with the 16:00 CT FX halt (2021-11-25 was still 12:00 CT)."
        ),
    ),
    date(2022, 2, 21): Citation(
        _HC + "2022-presidents-day-holiday-schedule-compact.xls",
        (
            "CME Group Globex Presidents Day Holiday Schedule: February 18, 2022 - February 22, "
            "2022 ... Calendar Date|Friday, Feb 18|Sunday, Feb 20 into Monday, Feb 21|Monday,Feb "
            "21|Monday, Feb 21 into Tuesday, Feb 22 ... Products|CLOSE|OPEN|HALT|OPEN ... FX "
            "|Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1600 CT / 2200 UTC|Regular "
            "@ 1700 CT / 2300 UTC"
        ),
        note=(
            "US holiday with regular FX Globex hours: CME's FX halt is 16:00 CT, the regular daily "
            "close, with the 17:00 CT reopen; no settlement that day and CME books the session to "
            "the next trade date. Same session clock as a regular day: no entry."
        ),
    ),
    date(2022, 5, 30): Citation(
        _HC + "2022-memorial-day-holiday-schedule-compact.xls",
        (
            "CME Group Globex Memorial Day Holiday Schedule: May 27, 2022 - May 31 , 2022 ... "
            "Calendar Date|Friday,May 27|Sunday,May 29|Monday, May 30|Monday, May 30 into Tues, "
            "May31 ... Product|CLOSE|OPEN|HALT|OPEN ... FX |Regular @ 1600 CT / 2100 UTC|Regular @ "
            "1700 CT / 2200 UTC|1600 CT / 2100 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "US holiday with regular FX Globex hours: CME's FX halt is 16:00 CT, the regular daily "
            "close, with the 17:00 CT reopen; no settlement that day and CME books the session to "
            "the next trade date. Same session clock as a regular day: no entry."
        ),
    ),
    date(2022, 6, 20): Citation(
        _HC + "2022-juneteenth-holiday-schedule.xls",
        (
            "Updated 5/18/2022|CME Group Globex Juneteenth Holiday Schedule: June 17, 2022 - Jun "
            "21, 2022 ... Calendar Date|Friday, June 17|||||Sunday, June 19|||||Monday, June "
            "20||||||||||Tuesday, Jun 21 ... FX Products|04:00:00 PM|||||04:00:00 PM|05:00:00 PM| "
            "||||||04:00:00 PM||||04:00:00 PM|05:00:00 PM"
        ),
        note=(
            "US holiday with regular FX Globex hours: CME's FX halt is 16:00 CT, the regular daily "
            "close, with the 17:00 CT reopen; no settlement that day and CME books the session to "
            "the next trade date. Same session clock as a regular day: no entry. Full schedule: FX "
            "Products Halt 16:00 under Monday, June 20 (merged headers read with xlrd)."
        ),
    ),
    date(2022, 7, 1): Citation(
        _HC + "2022-independence-day-holiday-schedule-compact.xls",
        (
            "CME Group Globex Independence Day Holiday Schedule: July 1, 2022 to July 5, 2022 ... "
            "Calendar Date|Friday July 1|Sunday July 3|Monday July 4|Monday July 4 ... "
            "Product|CLOSE|OPEN|HALT|OPEN ... FX |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT/ "
            "2200 UTC|1600 CT / 2100 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note="Friday before Independence Day: FX CLOSE Regular @ 1600 CT. No entry.",
    ),
    date(2022, 7, 4): Citation(
        _HC + "2022-independence-day-holiday-schedule-compact.xls",
        (
            "CME Group Globex Independence Day Holiday Schedule: July 1, 2022 to July 5, 2022 ... "
            "Calendar Date|Friday July 1|Sunday July 3|Monday July 4|Monday July 4 ... "
            "Product|CLOSE|OPEN|HALT|OPEN ... FX |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT/ "
            "2200 UTC|1600 CT / 2100 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "US holiday with regular FX Globex hours: CME's FX halt is 16:00 CT, the regular daily "
            "close, with the 17:00 CT reopen; no settlement that day and CME books the session to "
            "the next trade date. Same session clock as a regular day: no entry."
        ),
    ),
    date(2022, 9, 5): Citation(
        _HC + "2022-labor-day-holiday-schedule-compact.xls",
        (
            "CME Group Globex Labor Day Holiday Schedule: September 2, 2022 - September 6, 2022 "
            "... Calendar Date|Friday, September 2|Sunday,Sept 4 into Monday, Sept 5|Monday, Sept "
            "5|Monday, Sept 5 into Tuesday, Sept 6 ... Product|CLOSE|OPEN|HALT|OPEN ... FX "
            "|Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT / 2200 UTC|1600 CT / 2100 UTC|Regular "
            "@ 1700 CT / 2200 UTC"
        ),
        note=(
            "US holiday with regular FX Globex hours: CME's FX halt is 16:00 CT, the regular daily "
            "close, with the 17:00 CT reopen; no settlement that day and CME books the session to "
            "the next trade date. Same session clock as a regular day: no entry."
        ),
    ),
    date(2022, 11, 24): Citation(
        _HC + "2022-thanksgiving-holiday-schedule-compact.xls",
        (
            "CME Group Globex Thanksgiving Holiday Schedule: November 23, 2022 - November 25, 2022 "
            "... Products|Wednesday ,November 23|Wednesday, November 23|Thursday ,November "
            "24|Thursday , November 24|Friday November 25|Friday November 25 ... "
            "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... FX |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 "
            "CT / 2300 UTC|1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1215 CT/ 1815 "
            "UTC"
        ),
        note=(
            "US holiday with regular FX Globex hours: CME's FX halt is 16:00 CT, the regular daily "
            "close, with the 17:00 CT reopen; no settlement that day and CME books the session to "
            "the next trade date. Same session clock as a regular day: no entry."
        ),
    ),
    date(2022, 12, 23): Citation(
        _HC + "2022-christmas-holiday-schedule.xls",
        (
            "Updated 6/29/2022|CME Group Globex Christmas Holiday Schedule: December 23, 2022 - "
            "December 27, 2022 ... Calendar Date|Friday, December 23||||||||Monday, December "
            "26||||||||||||||||Tuesday, December 27 ... FX Products|04:00:00 PM||||||||Globex "
            "Closed||||||||||04:00:00 PM|05:00:00 PM|||||||04:00:00 PM"
        ),
        note="Friday before the observed Christmas: FX close 16:00 (04:00:00 PM). No entry.",
    ),
    date(2022, 12, 30): Citation(
        _HC + "2023-new-years-holiday-schedule-compact.xls",
        (
            "CME Group Globex New Years Holiday Schedule: December 30, 2022 - January 3, 2023 ... "
            "Calendar Trade|Friday,Dec 30|Sunday, Jan 1 and Monday, Jan 2|Monday,Jan 2|Tuesday, "
            "Jan 3|Tuesday, Jan 3 ... |CLOSE|Closed|OPEN|OPEN|CLOSE ... FX |Regular @ 1600 CT / "
            "2200 UTC|Globex Closed|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
        ),
        note="Friday before the observed New Year's Day: FX CLOSE Regular @ 1600 CT. No entry.",
    ),
    date(2023, 1, 16): Citation(
        _AMP_MLK_2023,
        (
            "CME Group Globex Dr. Martin Luther King, Jr. Holiday Schedule: 13 - 17 January 2023 "
            "... FX | Regular @ 16:00 CST | Regular @ 17:00 CST | 16:00 CST | 17:00 CST | Regular "
            "@ 16:00 CST"
        ),
        note=(
            "SECONDARY and transcribed from an image: AMP Futures' copy of CME's MLK 2023 Globex "
            "schedule (columns Friday Jan 13 CLOSE, Sunday Jan 15 OPEN, Monday Jan 16 HALT, Monday "
            "Jan 16 OPEN, Tuesday Jan 17 CLOSE). No CME-direct Globex-hours document for MLK 2023 "
            "was retrievable (the 6E service capture of 2024-07-08 has empty events for "
            "2023-01-15..17). US holiday with regular FX Globex hours: CME's FX halt is 16:00 CT, "
            "the regular daily close, with the 17:00 CT reopen; no settlement that day and CME "
            "books the session to the next trade date. Same session clock as a regular day: no "
            "entry."
        ),
    ),
    date(2023, 2, 20): Citation(
        _FILES + "presidents-day.pdf",
        (
            "Cleared As SUNDAY, 19 FEB 2023 MONDAY, 20 FEB 2023 TUESDAY, 21 FEB 2023 ... FX 16:00 "
            "(PREOPEN) 16:00 (PREOPEN) HALT"
        ),
        note=(
            "cmegroup.com/files/presidents-day.pdf, capture 2023-03-29. US holiday with regular FX "
            "Globex hours: CME's FX halt is 16:00 CT, the regular daily close, with the 17:00 CT "
            "reopen; no settlement that day and CME books the session to the next trade date. Same "
            "session clock as a regular day: no entry."
        ),
    ),
    date(2023, 5, 29): Citation(
        _TH + "memorial-day-2023.pdf",
        (
            "PRODUCT NAME SUNDAY, 28 MAY 2023 MONDAY, 29 MAY 2023 TUESDAY, 30 MAY 2023 ... FX "
            "16:00 (PREOPEN) 16:00 (PREOPEN) HALT TRADE DATE: WED 31 MAY"
        ),
        note=(
            "US holiday with regular FX Globex hours: CME's FX halt is 16:00 CT, the regular daily "
            "close, with the 17:00 CT reopen; no settlement that day and CME books the session to "
            "the next trade date. Same session clock as a regular day: no entry."
        ),
    ),
    date(2023, 6, 19): Citation(
        _TH + "juneteenth-2023.pdf",
        (
            "PRODUCT NAME SUNDAY, 18 JUNE 2023 MONDAY, 19 JUNE 2023 TUESDAY, 20 JUNE 2023 ... FX "
            "16:00 (PREOPEN) 16:00 (PREOPEN) HALT TRADE DATE: WED 21 JUNE"
        ),
        note=(
            "US holiday with regular FX Globex hours: CME's FX halt is 16:00 CT, the regular daily "
            "close, with the 17:00 CT reopen; no settlement that day and CME books the session to "
            "the next trade date. Same session clock as a regular day: no entry."
        ),
    ),
    date(2023, 7, 3): Citation(
        _TH + "4th-of-july-2023.pdf",
        (
            "PRODUCT NAME MONDAY, 3 JULY 2023 TUESDAY, 4 JULY 2023 WEDNESDAY, 5 JULY 2023 ... "
            "TRADE DATE: MON 3 JULY TRADE DATE: WED 5 JULY ... 16:00 (CLOSED) TRADE DATE: WED 5 "
            "JULY 16:00 (CLOSED) ... FX TRADE DATE: WED 5 JULY 16:00 (PREOPEN) HALT TRADE DATE: "
            "THUR 6 JULY"
        ),
        note=(
            "Eve of Independence Day: FX 16:00 (CLOSED) for trade date Monday 3 July (equity "
            "closed 12:15). No entry."
        ),
    ),
    date(2023, 7, 4): Citation(
        _TH + "4th-of-july-2023.pdf",
        (
            "PRODUCT NAME MONDAY, 3 JULY 2023 TUESDAY, 4 JULY 2023 WEDNESDAY, 5 JULY 2023 ... FX "
            "TRADE DATE: WED 5 JULY 16:00 (PREOPEN) HALT TRADE DATE: THUR 6 JULY"
        ),
        note=(
            "US holiday with regular FX Globex hours: CME's FX halt is 16:00 CT, the regular daily "
            "close, with the 17:00 CT reopen; no settlement that day and CME books the session to "
            "the next trade date. Same session clock as a regular day: no entry."
        ),
    ),
    date(2023, 9, 4): Citation(
        _TH + "labor-day-2023.pdf",
        (
            "PRODUCT NAME SUNDAY, 3 SEPTEMBER 2023 MONDAY, 4 SEPTEMBER 2023 TUESDAY, 5 SEPTEMBER "
            "2023 ... FX 16:00 (PREOPEN) 16:00 (PREOPEN) HALT TRADE DATE: WED 6 SEP"
        ),
        _svc("2023-09-03", "2023-09-05", "1720455278654"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2023-09-04","events":[{"tradingDate":"2023-09-05","eventTime":"16:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2023-09-05","eventTime":"17:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "US holiday with regular FX Globex hours: CME's FX halt is 16:00 CT, the regular daily "
            "close, with the 17:00 CT reopen; no settlement that day and CME books the session to "
            "the next trade date. Same session clock as a regular day: no entry."
        ),
    ),
    date(2023, 11, 23): Citation(
        _TH + "thanksgiving-day-2023.pdf",
        (
            "PRODUCT NAME WEDNESDAY, 22 NOVEMBER 2023 THURSDAY, 23 NOVEMBER 2023 FRIDAY, 24 "
            "NOVEMBER 2023 ... FX TRADE DATE: FRI 24 NOV 16:00 (PREOPEN) HALT"
        ),
        _svc("2023-11-22", "2023-11-24", "1720455278656"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2023-11-23","events":[{"tradingDate":"2023-11-24","eventTime":"16:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2023-11-24","eventTime":"17:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "US holiday with regular FX Globex hours: CME's FX halt is 16:00 CT, the regular daily "
            "close, with the 17:00 CT reopen; no settlement that day and CME books the session to "
            "the next trade date. Same session clock as a regular day: no entry."
        ),
    ),
    date(2023, 12, 22): Citation(
        _HC + "christmas-holiday-settlement-times-2023.pdf",
        (
            "Christmas Day Holiday 12/25/2023 Settlement Times ... Friday, December 22, 2023 ... "
            "Interest Rate Products 12:00:00 CT ... All other products will settle at their normal "
            "times"
        ),
        note=(
            "Friday before Christmas 2023: CME states FX settles at its normal time. No CME "
            "Globex-hours document for this day was retrieved (the Christmas 2023 summary PDF and "
            "the 6E service window start on Monday 25 December); modeled as a regular session. In "
            "2021 and 2022 the same Friday kept the regular 16:00 CT FX close."
        ),
    ),
    date(2023, 12, 29): Citation(
        _HC + "new-years-eve-holiday-settlement-times-2024.pdf",
        (
            "New Year’s Eve Holiday 12/29/2023 Settlement Times ... Friday, December 29, 2023 ... "
            "CME Group Interest Rate Products Settlement Time: 12:00:00 CT ... All other products "
            "will settle at their normal times"
        ),
        note=(
            "Friday before New Year's Day 2024: CME states FX settles at its normal time. No CME "
            "Globex-hours document for this day was retrieved (the New Year 2024 summary PDF and "
            "the 6E service window start on 2023-12-31/2024-01-01); modeled as a regular session. "
            "In 2019-2022 and 2024-2025 New Year's Eve kept the regular 16:00 CT FX close."
        ),
    ),
    date(2024, 1, 15): Citation(
        _svc("2024-01-14", "2024-01-16", "1720455278663"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2024-01-15","events":[{"tradingDate":"2024-01-16","eventTime":"16:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2024-01-16","eventTime":"17:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "US holiday with regular FX Globex hours: CME's FX halt is 16:00 CT, the regular daily "
            "close, with the 17:00 CT reopen; no settlement that day and CME books the session to "
            "the next trade date. Same session clock as a regular day: no entry."
        ),
    ),
    date(2024, 2, 19): Citation(
        _svc("2024-02-18", "2024-02-20", "1720455278669"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2024-02-19","events":[{"tradingDate":"2024-02-20","eventTime":"16:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2024-02-20","eventTime":"17:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "US holiday with regular FX Globex hours: CME's FX halt is 16:00 CT, the regular daily "
            "close, with the 17:00 CT reopen; no settlement that day and CME books the session to "
            "the next trade date. Same session clock as a regular day: no entry."
        ),
    ),
    date(2024, 5, 27): Citation(
        _svc("2024-05-26", "2024-05-28", "1720455278675"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2024-05-27","events":[{"tradingDate":"2024-05-28","eventTime":"16:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2024-05-28","eventTime":"17:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "US holiday with regular FX Globex hours: CME's FX halt is 16:00 CT, the regular daily "
            "close, with the 17:00 CT reopen; no settlement that day and CME books the session to "
            "the next trade date. Same session clock as a regular day: no entry."
        ),
    ),
    date(2024, 6, 19): Citation(
        _svc("2024-06-18", "2024-06-20", "1720455278677"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2024-06-19","events":[{"tradingDate":"2024-06-20","eventTime":"16:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2024-06-20","eventTime":"17:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "US holiday with regular FX Globex hours: CME's FX halt is 16:00 CT, the regular daily "
            "close, with the 17:00 CT reopen; no settlement that day and CME books the session to "
            "the next trade date. Same session clock as a regular day: no entry."
        ),
    ),
    date(2024, 7, 3): Citation(
        _svc("2024-07-03", "2024-07-05", "1720455278680"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2024-07-03","events":[{"tradingDate":"2024-07-03","eventTime":"16:00",'
            '"marketEventType":"closed"},{"tradingDate":"2024-07-05","eventTime":"16:45",'
            '"marketEventType":"preopen"},{"tradingDate":"2024-07-05","eventTime":"17:00",'
            '"marketEventType":"open"}]}'
        ),
        note="Eve of Independence Day: 6E 16:00 closed (regular; equity 12:15). No entry.",
    ),
    date(2024, 7, 4): Citation(
        _svc("2024-07-03", "2024-07-05", "1720455278680"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2024-07-04","events":[{"tradingDate":"2024-07-05","eventTime":"16:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2024-07-05","eventTime":"17:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "US holiday with regular FX Globex hours: CME's FX halt is 16:00 CT, the regular daily "
            "close, with the 17:00 CT reopen; no settlement that day and CME books the session to "
            "the next trade date. Same session clock as a regular day: no entry."
        ),
    ),
    date(2024, 9, 2): Citation(
        _svc("2024-09-01", "2024-09-03", "1720455278683"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2024-09-02","events":[{"tradingDate":"2024-09-03","eventTime":"16:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2024-09-03","eventTime":"17:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "US holiday with regular FX Globex hours: CME's FX halt is 16:00 CT, the regular daily "
            "close, with the 17:00 CT reopen; no settlement that day and CME books the session to "
            "the next trade date. Same session clock as a regular day: no entry."
        ),
    ),
    date(2024, 11, 28): Citation(
        _svc("2024-11-27", "2024-11-29", "1734710019535"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2024-11-28","events":[{"tradingDate":"2024-11-29","eventTime":"16:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2024-11-29","eventTime":"17:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "US holiday with regular FX Globex hours: CME's FX halt is 16:00 CT, the regular daily "
            "close, with the 17:00 CT reopen; no settlement that day and CME books the session to "
            "the next trade date. Same session clock as a regular day: no entry."
        ),
    ),
    date(2024, 12, 31): Citation(
        _svc("2024-12-31", "2025-01-02", "1720455278688"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2024-12-31","events":[{"tradingDate":"2024-12-31","eventTime":"16:00",'
            '"marketEventType":"closed"}]}'
        ),
        note=(
            "New Year's Eve: 6E 16:00 closed (regular close; no reopen that evening, January 1 is "
            "a closure). No entry."
        ),
    ),
    date(2025, 1, 9): Citation(
        _TH + "day-of-mourning-january-9-2024.pdf",
        (
            "U.S. National Day of Mourning Trading Schedule ... PRODUCT NAME JANUARY 9, 2025 "
            "TRADING FLOOR CLEARPORT ... CME GROUP FX NORMAL HOURS N/A NORMAL HOURS"
        ),
        note=(
            "National Day of Mourning (Carter): FX normal hours (equity closed 08:30, rates "
            "12:15). No entry. The PDF's file name says 2024; its table is dated January 9, 2025."
        ),
    ),
    date(2025, 1, 20): Citation(
        _svc("2025-01-19", "2025-01-21", "1734710019539"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2025-01-20","events":[{"tradingDate":"2025-01-21","eventTime":"16:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2025-01-21","eventTime":"17:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "US holiday with regular FX Globex hours: CME's FX halt is 16:00 CT, the regular daily "
            "close, with the 17:00 CT reopen; no settlement that day and CME books the session to "
            "the next trade date. Same session clock as a regular day: no entry."
        ),
    ),
    date(2025, 2, 17): Citation(
        _svc("2025-02-16", "2025-02-18", "1734710019540"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2025-02-17","events":[{"tradingDate":"2025-02-18","eventTime":"16:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2025-02-18","eventTime":"17:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "US holiday with regular FX Globex hours: CME's FX halt is 16:00 CT, the regular daily "
            "close, with the 17:00 CT reopen; no settlement that day and CME books the session to "
            "the next trade date. Same session clock as a regular day: no entry."
        ),
    ),
    date(2025, 5, 26): Citation(
        _svc("2025-05-25", "2025-05-27", "1734710019543"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2025-05-26","events":[{"tradingDate":"2025-05-27","eventTime":"16:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2025-05-27","eventTime":"17:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "US holiday with regular FX Globex hours: CME's FX halt is 16:00 CT, the regular daily "
            "close, with the 17:00 CT reopen; no settlement that day and CME books the session to "
            "the next trade date. Same session clock as a regular day: no entry."
        ),
    ),
    date(2025, 6, 19): Citation(
        _svc("2025-06-18", "2025-06-20", "1734710019544"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2025-06-19","events":[{"tradingDate":"2025-06-20","eventTime":"16:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2025-06-20","eventTime":"17:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "US holiday with regular FX Globex hours: CME's FX halt is 16:00 CT, the regular daily "
            "close, with the 17:00 CT reopen; no settlement that day and CME books the session to "
            "the next trade date. Same session clock as a regular day: no entry."
        ),
    ),
    date(2025, 7, 3): Citation(
        _svc("2025-07-03", "2025-07-05", "1734710019545"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2025-07-03","events":[{"tradingDate":"2025-07-03","eventTime":"16:00",'
            '"marketEventType":"closed"},{"tradingDate":"2025-07-04","eventTime":"16:45",'
            '"marketEventType":"preopen"},{"tradingDate":"2025-07-04","eventTime":"17:00",'
            '"marketEventType":"open"}]}'
        ),
        note="Eve of Independence Day: 6E 16:00 closed (regular; equity 12:15). No entry.",
    ),
    date(2025, 9, 1): Citation(
        _svc("2025-08-31", "2025-09-02", "1734710019546"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2025-09-01","events":[{"tradingDate":"2025-09-02","eventTime":"16:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2025-09-02","eventTime":"17:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "US holiday with regular FX Globex hours: CME's FX halt is 16:00 CT, the regular daily "
            "close, with the 17:00 CT reopen; no settlement that day and CME books the session to "
            "the next trade date. Same session clock as a regular day: no entry."
        ),
    ),
    date(2025, 11, 27): Citation(
        _svc("2025-11-26", "2025-11-28", "1769649703060"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2025-11-27","events":[{"tradingDate":"2025-11-28","eventTime":"16:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"17:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "US holiday with regular FX Globex hours: CME's FX halt is 16:00 CT, the regular daily "
            "close, with the 17:00 CT reopen; no settlement that day and CME books the session to "
            "the next trade date. Same session clock as a regular day: no entry."
        ),
    ),
    date(2025, 12, 31): Citation(
        _svc("2025-12-31", "2026-01-02", "1769649703066"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2025-12-31","events":[{"tradingDate":"2025-12-31","eventTime":"16:00",'
            '"marketEventType":"closed"}]}'
        ),
        note="New Year's Eve: 6E 16:00 closed (regular close). No entry.",
    ),
    date(2026, 1, 19): Citation(
        _svc("2026-01-18", "2026-01-20", "1769649703068"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2026-01-19","events":[{"tradingDate":"2026-01-20","eventTime":"16:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2026-01-20","eventTime":"17:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "US holiday with regular FX Globex hours: CME's FX halt is 16:00 CT, the regular daily "
            "close, with the 17:00 CT reopen; no settlement that day and CME books the session to "
            "the next trade date. Same session clock as a regular day: no entry."
        ),
    ),
    date(2026, 2, 16): Citation(
        _svc("2026-02-15", "2026-02-17", "1769649703070"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2026-02-16","events":[{"tradingDate":"2026-02-17","eventTime":"16:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2026-02-17","eventTime":"17:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "US holiday with regular FX Globex hours: CME's FX halt is 16:00 CT, the regular daily "
            "close, with the 17:00 CT reopen; no settlement that day and CME books the session to "
            "the next trade date. Same session clock as a regular day: no entry."
        ),
    ),
    date(2026, 4, 2): Citation(
        _svc("2026-04-01", "2026-04-03", "1769649703072"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2026-04-02","events":[{"tradingDate":"2026-04-02","eventTime":"16:00",'
            '"marketEventType":"closed"},{"tradingDate":"2026-04-03","eventTime":"16:45",'
            '"marketEventType":"preopen"},{"tradingDate":"2026-04-03","eventTime":"17:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "Thursday before Good Friday: 6E 16:00 closed, reopen 17:00 for trade date 2026-04-03 "
            "(regular). No entry."
        ),
    ),
    date(2026, 5, 25): Citation(
        _svc("2026-05-24", "2026-05-26", "1769649703074"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2026-05-25","events":[{"tradingDate":"2026-05-26","eventTime":"16:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2026-05-26","eventTime":"17:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "US holiday with regular FX Globex hours: CME's FX halt is 16:00 CT, the regular daily "
            "close, with the 17:00 CT reopen; no settlement that day and CME books the session to "
            "the next trade date. Same session clock as a regular day: no entry."
        ),
    ),
}

SESSION_SOURCES: dict[str, Citation] = {
    "cme_fx_globex_hours": Citation(
        _EURO_FX_SPECS,
        (
            "Trading Hours Sunday - Friday 6:00 p.m. - 5:00 p.m. (5:00 p.m. - 4:00 p.m. Chicago "
            "Time/CT) with a 60-minute break each day beginning at 5:00 p.m. (4:00 p.m. CT)"
        ),
        _svc("2026-06-17", "2026-06-19", "1769649703075"),
        (
            '"globex":"6E","prodGroup":"6E","name":"Euro FX Futures","id":58 ... {"groupCode":"6E",'
            '"eventDate":"2026-06-17","events":[{"tradingDate":"2026-06-17","eventTime":"16:00",'
            '"marketEventType":"closed"},{"tradingDate":"2026-06-18","eventTime":"16:45",'
            '"marketEventType":"preopen"},{"tradingDate":"2026-06-18","eventTime":"17:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "Regular FX session Sunday-Friday 17:00-16:00 CT with a 60-minute break from 16:00 CT. "
            "Status part: CME's Euro FX contract specifications, capture 2019-07-01. Time part: a "
            "regular Wednesday in CME's 6E service data, 2026-06-17 (16:00 closed, 16:45 pre-open, "
            "17:00 open for the next trade date), capture 2026-01-29. Every CME holiday schedule "
            "read for 2019-2026 lists FX regular closes at 16:00 CT and opens at 17:00 CT (Sunday "
            "17:00 CT after a weekend). No CME notice of a change to FX futures Globex hours in "
            "2019-05..2026-06 was found. CME states hours for its FX asset class ('FX' / 'FX "
            "Products' rows, the only exception row being New Zealand Spot FX) or for 6E; the "
            "other ten FX contracts are taken to share them."
        ),
    ),
    "cme_fx_settlement": Citation(
        _WIKI + "Daily+Settlement+Time+Details",
        (
            "This topic details product settlement time ranges. ... FX 13:59:30-14:00:00 CT 12:00 "
            "a.m. CT"
        ),
        note=(
            "CME's daily settlement time range for FX (CME Group Client Systems Wiki, 'Daily "
            "Settlement Time Details', read 2026-09-25): the 14:00 CT close of D6's FX row. This "
            "is the group-level statement used for E7 (E-mini Euro FX), for which no product page "
            "was found."
        ),
    ),
    "cme_settle_6E": Citation(
        _WIKI + "Euro",
        (
            "CME Group staff determines the daily settlement of EUR/USD futures (6E) at 14:00 "
            "Central Time (CT) based on trading activity on CME Globex."
        ),
    ),
    "cme_settle_M6E": Citation(
        _WIKI + "Euro",
        (
            "The settlement in the Micro EUR/USD (M6E) futures contract is derived directly from "
            "the settlement in the regular sized EUR/USD (6E) futures contract."
        ),
    ),
    "cme_settle_6A": Citation(
        _WIKI + "Australian+Dollar",
        (
            "CME Group staff determines the daily settlement of AUD/USD futures (6A) at 14:00 "
            "Central Time (CT), the settlement period, based on trading activity on CME Globex."
        ),
    ),
    "cme_settle_M6A": Citation(
        _WIKI + "Australian+Dollar",
        (
            "The settlement in the Micro AUD/USD (M6A) futures contract is derived directly from "
            "the settlement in the regular sized AUD/USD (6A) futures contract."
        ),
    ),
    "cme_settle_6B": Citation(
        _WIKI + "British+Pound",
        (
            "CME Group staff determines the daily settlement of GBP/USD futures (6B) at 14:00 "
            "Central Time (CT) based on trading activity on CME Globex."
        ),
    ),
    "cme_settle_M6B": Citation(
        _WIKI + "British+Pound",
        (
            "The settlement in the Micro GBP/USD (M6B) futures contract is derived directly from "
            "the settlement in the regular sized GBP/USD (6B) futures contract."
        ),
    ),
    "cme_settle_6C": Citation(
        _WIKI + "Canadian+Dollar",
        (
            "CME Group staff determines the daily settlement of CAD/USD futures (6C) at 14:00 "
            "Central Time (CT) based on trading activity on CME Globex."
        ),
    ),
    "cme_settle_6J": Citation(
        _WIKI + "Japanese+Yen",
        (
            "CME Group staff determines the daily settlement of JPY/USD futures (6J) at 14:00 "
            "Central Time (CT) based on trading activity on CME Globex."
        ),
    ),
    "cme_settle_6S": Citation(
        _WIKI + "Swiss+Franc",
        (
            "CME Group staff determines the daily settlement of CHF/USD futures (6S) at 14:00 "
            "Central Time (CT) based on trading activity on CME Globex."
        ),
    ),
    "cme_settle_6N": Citation(
        _WIKI + "New+Zealand+Dollar",
        (
            "Daily settlement of NZD/USD futures (6N) is determined by CME Group staff based on "
            "trading activity on CME Globex. ... Tier 1: If three or more contracts trade in the "
            "lead month occur on CME Globex between 13:59:30 and 14:00:00 CT, the settlement period"
        ),
    ),
    "cme_fx_rth_open": Citation(
        _EURO_FX_SPECS,
        (
            "Trading Hours CME Globex (ETH) Sundays: 5:00 p.m. – 4:00 p.m. Central Time (CT) next "
            "day. ... Open Outcry (RTH) 7:20 a.m. – 2:00 p.m. Central Time (CT)"
        ),
        _EURO_FX_SPECS,
        (
            "Trading Hours Sunday - Friday 6:00 p.m. - 5:00 p.m. (5:00 p.m. - 4:00 p.m. Chicago "
            "Time/CT)"
        ),
        note=(
            "D6's O = 07:20 CT is the start of CME's former Euro FX open-outcry regular trading "
            "hours (RTH 07:20-14:00 CT; contract specifications, capture 2014-02-09). The 2019 "
            "specifications list only the Globex session: 07:20 CT is not an event of the Globex "
            "FX session in 2019-2026."
        ),
    ),
}
