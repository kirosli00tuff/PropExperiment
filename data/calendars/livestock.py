"""CME Globex calendar for the livestock group: CME HE (Lean Hogs) and LE (Live Cattle),
2019-05-01..2026-06-19 (Stage E.2a Task 6; design D10 and D11.3).

Interface as data.cme_calendar, whose Holiday, HolidayKind, Citation and CalendarCoverageError are
imported, not redefined: HOLIDAYS, SOURCES, NO_ENTRY_FINDINGS, CALENDAR_COVERAGE and
assert_calendar_coverage, plus SESSIONS (data.calendars.SessionSpec) with SESSION_SOURCES. No
extension of the interface: livestock has no late open or abbreviated session in the window (on
2025-11-28, after the Globex outage, CME's record keeps the regular 08:30 CT livestock open), so
this module has no LATE_OPENS.

Livestock trades one day session, Monday-Friday 08:30-13:05 CT, with no overnight session; the
trade date is the calendar day. A FULL_CLOSURE entry means no trade date that day. An EARLY_HALT
entry is an early close of that day session at ``halt_ct`` (the last one-minute bar starts at
halt_ct minus one minute); the next session opens at the regular 08:30 CT on the next trade date.

Sources (all CME Group except one entry; cmegroup.com refuses automated fetches, so every
cmegroup.com file was read from a Wayback Machine copy; the CME client wiki on atlassian.net was
read directly):
- 2019-2021: CME's Globex holiday trading schedules (.xls) in CME's yearly holiday-calendars.zip,
  compact sheets, row "Livestock"; the full sheets confirm each early-close time.
- 2022 and New Year 2023: CME's per-holiday Globex schedules (.xls), same row.
- 2023-02..2023-07: CME's holiday summary PDFs, row "LIVESTOCK".
- 2023-09..2026-06: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html,
  product 22 (LE, Live Cattle Futures). HE is not in any captured request and is taken to share
  LE's hours: CME's schedules through 2023 state one livestock row for both.
- 2025-01-09 (National Day of Mourning): CME's trading schedule, "CME AND CBOT AGS" 12:15 CT.
- 2023-01-16 (MLK Day): the one secondary entry, an AMP Futures image of CME's compact MLK 2023
  Globex schedule (Livestock "Closed for MLK Day", read by OCR), with CME's no-settlement notice.
- Sessions: CME's HE and LE contract specifications (2019-2026) and CME Clearing's livestock
  settlement procedure (settlement period 12:59:30-13:00:00 CT).
Verbatim quotes, capture URLs and file hashes per entry, and the script-run verbatim check:
reports/stage_e2a_calendar_sources_livestock.json and .md.

Grades as data.cme_calendar: status (``evidence``) "cme" | "secondary" | "unverified"; time
(``time_evidence``) "cme" | "secondary" | "inferred" | "unverified" | "n/a" ("empirical" is
reserved for the later bar check). Every status is "cme" except 2023-01-16 ("secondary"); every
early-close time is "cme".

How livestock differs from the other groups:
- Every exchange holiday (New Year's Day, MLK, Presidents, Good Friday, Memorial, Juneteenth,
  Independence, Labor, Thanksgiving and Christmas Days) is a full closure: livestock has no
  holiday halt session. Good Friday is closed in the jobs-report years too (2021-04-02,
  2023-04-07, 2026-04-03), when equities traded.
- Early closes: 12:15 CT in 2019 (07-03, 11-29, 12-24) and on 2020-07-02; 12:05 CT on the day
  after Thanksgiving from 2020-11-27 and on Christmas Eve 2020; 12:15 CT on Christmas Eve 2024
  and 2025 and on the 2025-01-09 Day of Mourning.
- From 2021 the eve of Independence Day is a regular session; New Year's Eve and the days before
  an observed Christmas or New Year's Day are regular (NO_ENTRY_FINDINGS).

Holdout-2 dates (2024-04-01..2025-03-31) and the 2019-05..2024-02 confirmation window rest on
CME's schedules alone until their bars are checked.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date, time

from data.calendars import Segment, SessionSpec
from data.cme_calendar import CalendarCoverageError, Citation, Holiday, HolidayKind

LIVESTOCK_PRODUCTS = ("HE", "LE")

SESSION_OPEN = time(8, 30)  # CME Globex livestock open, Monday-Friday
SESSION_CLOSE = time(13, 5)  # CME Globex livestock close
SETTLEMENT_CT = time(13, 0)  # end of the 12:59:30-13:00:00 CT settlement period
CLOSE_1215 = time(12, 15)  # early close 2019 to 2020-07-02; Christmas Eve 2024-2025
CLOSE_1205 = time(12, 5)  # early close from 2020-11-27 (day after Thanksgiving)

_HC = "https://www.cmegroup.com/tools-information/holiday-calendar/files/"
_TH = "https://www.cmegroup.com/trading-hours/files/"
_Z19, _Z20, _Z21 = (_HC + f"{y}-holiday-calendars.zip" for y in (2019, 2020, 2021))
_AMP_MLK_2023 = (
    "https://www.ampfutures.com/hubfs/CME%20Holiday%20Trading%20Schedule%20-%20Dr.%20"
    "Martin%20Luther%20King%2c%20Jr.%20(2023).png"
)
_SPEC_OLD = "https://www.cmegroup.com/trading/agricultural/livestock/"
_SPEC_NEW = "https://www.cmegroup.com/markets/agriculture/livestock/"
_WIKI = "https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/"
_WIKI_OLD = "https://www.cmegroup.com/confluence/display/EPICSANDBOX/"


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
    _closure(date(2019, 5, 27), "Memorial Day"),
    _halt(date(2019, 7, 3), "Day before Independence Day", CLOSE_1215),
    _closure(date(2019, 7, 4), "Independence Day"),
    _closure(date(2019, 9, 2), "Labor Day"),
    _closure(date(2019, 11, 28), "Thanksgiving Day"),
    _halt(date(2019, 11, 29), "Day after Thanksgiving", CLOSE_1215),
    _halt(date(2019, 12, 24), "Christmas Eve", CLOSE_1215),
    _closure(date(2019, 12, 25), "Christmas Day"),
    # ---- 2020
    _closure(date(2020, 1, 1), "New Year's Day"),
    _closure(date(2020, 1, 20), "Martin Luther King Jr. Day"),
    _closure(date(2020, 2, 17), "Presidents Day"),
    _closure(date(2020, 4, 10), "Good Friday"),
    _closure(date(2020, 5, 25), "Memorial Day"),
    _halt(date(2020, 7, 2), "Day before Independence Day (observed)", CLOSE_1215),
    _closure(date(2020, 7, 3), "Independence Day (observed)"),
    _closure(date(2020, 9, 7), "Labor Day"),
    _closure(date(2020, 11, 26), "Thanksgiving Day"),
    _halt(date(2020, 11, 27), "Day after Thanksgiving", CLOSE_1205),
    _halt(date(2020, 12, 24), "Christmas Eve", CLOSE_1205),
    _closure(date(2020, 12, 25), "Christmas Day"),
    # ---- 2021
    _closure(date(2021, 1, 1), "New Year's Day"),
    _closure(date(2021, 1, 18), "Martin Luther King Jr. Day"),
    _closure(date(2021, 2, 15), "Presidents Day"),
    _closure(date(2021, 4, 2), "Good Friday"),
    _closure(date(2021, 5, 31), "Memorial Day"),
    _closure(date(2021, 7, 5), "Independence Day (observed)"),
    _closure(date(2021, 9, 6), "Labor Day"),
    _closure(date(2021, 11, 25), "Thanksgiving Day"),
    _halt(date(2021, 11, 26), "Day after Thanksgiving", CLOSE_1205),
    _closure(date(2021, 12, 24), "Christmas Day (observed)"),
    # ---- 2022
    _closure(date(2022, 1, 17), "Martin Luther King Jr. Day"),
    _closure(date(2022, 2, 21), "Presidents Day"),
    _closure(date(2022, 4, 15), "Good Friday"),
    _closure(date(2022, 5, 30), "Memorial Day"),
    _closure(date(2022, 6, 20), "Juneteenth (observed)"),
    _closure(date(2022, 7, 4), "Independence Day"),
    _closure(date(2022, 9, 5), "Labor Day"),
    _closure(date(2022, 11, 24), "Thanksgiving Day"),
    _halt(date(2022, 11, 25), "Day after Thanksgiving", CLOSE_1205),
    _closure(date(2022, 12, 26), "Christmas Day (observed)"),
    # ---- 2023
    _closure(date(2023, 1, 2), "New Year's Day (observed)"),
    _closure(date(2023, 1, 16), "Martin Luther King Jr. Day", evidence="secondary"),
    _closure(date(2023, 2, 20), "Presidents Day"),
    _closure(date(2023, 4, 7), "Good Friday"),
    _closure(date(2023, 5, 29), "Memorial Day"),
    _closure(date(2023, 6, 19), "Juneteenth"),
    _closure(date(2023, 7, 4), "Independence Day"),
    _closure(date(2023, 9, 4), "Labor Day"),
    _closure(date(2023, 11, 23), "Thanksgiving Day"),
    _halt(date(2023, 11, 24), "Day after Thanksgiving", CLOSE_1205),
    _closure(date(2023, 12, 25), "Christmas Day"),
    # ---- 2024
    _closure(date(2024, 1, 1), "New Year's Day"),
    _closure(date(2024, 1, 15), "Martin Luther King Jr. Day"),
    _closure(date(2024, 2, 19), "Presidents Day"),
    _closure(date(2024, 3, 29), "Good Friday"),
    _closure(date(2024, 5, 27), "Memorial Day"),
    _closure(date(2024, 6, 19), "Juneteenth"),
    _closure(date(2024, 7, 4), "Independence Day"),
    _closure(date(2024, 9, 2), "Labor Day"),
    _closure(date(2024, 11, 28), "Thanksgiving Day"),
    _halt(date(2024, 11, 29), "Day after Thanksgiving", CLOSE_1205),
    _halt(date(2024, 12, 24), "Christmas Eve", CLOSE_1215),
    _closure(date(2024, 12, 25), "Christmas Day"),
    # ---- 2025
    _closure(date(2025, 1, 1), "New Year's Day"),
    _halt(date(2025, 1, 9), "National Day of Mourning (Carter)", CLOSE_1215),
    _closure(date(2025, 1, 20), "Martin Luther King Jr. Day"),
    _closure(date(2025, 2, 17), "Presidents Day"),
    _closure(date(2025, 4, 18), "Good Friday"),
    _closure(date(2025, 5, 26), "Memorial Day"),
    _closure(date(2025, 6, 19), "Juneteenth"),
    _closure(date(2025, 7, 4), "Independence Day"),
    _closure(date(2025, 9, 1), "Labor Day"),
    _closure(date(2025, 11, 27), "Thanksgiving Day"),
    _halt(date(2025, 11, 28), "Day after Thanksgiving", CLOSE_1205),
    _halt(date(2025, 12, 24), "Christmas Eve", CLOSE_1215),
    _closure(date(2025, 12, 25), "Christmas Day"),
    # ---- 2026
    _closure(date(2026, 1, 1), "New Year's Day"),
    _closure(date(2026, 1, 19), "Martin Luther King Jr. Day"),
    _closure(date(2026, 2, 16), "Presidents Day"),
    _closure(date(2026, 4, 3), "Good Friday"),
    _closure(date(2026, 5, 25), "Memorial Day"),
    _closure(date(2026, 6, 19), "Juneteenth"),
)

HOLIDAYS: dict[date, Holiday] = {h.day: h for h in _ENTRIES}
CALENDAR_COVERAGE = (date(2019, 5, 1), date(2026, 6, 19))


def assert_calendar_coverage(days: Iterable[date]) -> None:
    """Raise unless every date lies inside ``CALENDAR_COVERAGE`` (inclusive); the semantics of
    data.cme_calendar.assert_calendar_coverage, for the livestock group."""
    first, last = CALENDAR_COVERAGE
    outside = sorted(d for d in set(days) if not first <= d <= last)
    if outside:
        raise CalendarCoverageError(
            f"{len(outside)} trade date(s) outside the livestock calendar's coverage "
            f"{first}..{last}: {outside[0]} .. {outside[-1]}; extend data/calendars/livestock.py "
            "first")


# One regime covers the whole window: no CME change to livestock Globex hours was found.
SESSIONS: tuple[SessionSpec, ...] = (
    SessionSpec(
        valid_from=date(2019, 5, 1),
        valid_to=date(2026, 6, 19),
        segments=(Segment(0, SESSION_OPEN, 0, SESSION_CLOSE),),
        day_session_ct={p: (time(8, 30), time(13, 0)) for p in LIVESTOCK_PRODUCTS},
        source="cme_livestock_hours",
        note=(
            "day_session_ct is design D6's livestock row (O 08:30, C 13:00 CT; F 13:03 CT with the "
            "session close 13:05 CT is applied by the rules engine), keyed by product. D6 "
            "confirmation: C 13:00 CT is the end of CME's daily settlement period "
            "12:59:30-13:00:00 CT, stated for HE and LE by name ('cme_livestock_settlement', and "
            "unchanged in the 2018 and 2020 versions of the page); O 08:30 CT and the 13:05 CT "
            "close are the CME Globex livestock hours in the HE and LE contract specifications of "
            "every capture 2019-2026 ('cme_livestock_hours' and the cme_*_hours keys). D6's values "
            "agree with CME: no correction. The segment is the regular 08:30-13:05 CT day session; "
            "there is no overnight livestock session."
        ),
    ),
)

SOURCES: dict[date, Citation] = {
    date(2019, 5, 27): Citation(
        _Z19,
        (
            "CME Group Globex Memorial Day Holiday Schedule: May 24, 2019 - May 28, 2019 ... Trade "
            "Date|Friday, May 24|Tuesday, May 28|Tuesday, May 28|Tuesday, May 28 ... Calendar "
            "Date|Friday,May 24|Sunday,May 26 into Monday,May 27|Monday, May 27|Mon,May 27 into "
            "Tues,May 28 ... Product|CLOSE|OPEN|HALT|OPEN ... Livestock|Regular per Product|Closed "
            "for Memorial Day|Closed for Memorial Day|Tuesday @ 0830 CT/1330 UTC"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-memorial-day-holiday-schedule-compact.xls of "
            "CME's yearly holiday-calendars zip (Wayback capture 2021-01-26); the zip's sha256 is "
            "the document hash. CME's compact Globex holiday schedule gives one row per asset "
            "class; the 'Livestock' row covers CME livestock futures (LE and HE are not named "
            "individually)."
        ),
    ),
    date(2019, 7, 3): Citation(
        _Z19,
        (
            "CME Group Globex Independence Day Holiday Schedule: July 3, 2019 to July 5, 2019 ... "
            "Trade Date|Wednesday July 3 | Friday July 5| Friday July 5| Friday July 5 ... "
            "Calendar Date|Wednesday July 3 |Wednesday,July 3|Thursday July 4 |Thursday July 4 "
            "into Friday July 5 ... Product|CLOSE|OPEN|HALT|OPEN ... Livestock|Early @ 1215 CT / "
            "1715 UTC|Markets Closed|Markets Closed|Friday @ 0830 / 1330 UTC"
        ),
        _Z19,
        (
            "Livestock|Early @ 1215 CT / 1715 UTC|Markets Closed|Markets Closed|Friday @ 0830 / "
            "1330 UTC"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-4th-of-july-holiday-schedule-compact.xls of "
            "CME's yearly holiday-calendars zip (Wayback capture 2021-01-26); the zip's sha256 is "
            "the document hash. CME's compact Globex holiday schedule gives one row per asset "
            "class; the 'Livestock' row covers CME livestock futures (LE and HE are not named "
            "individually). Full schedule "
            "globex-trading-schedules/2019-independence-day-schedule.xls (same zip): Livestock "
            "'12:15' under Calendar Date 'Wednesday, July 3', column 'Early Close' (column headers "
            "read with xlrd, merged header cells expanded). Early close 12:15 CT as CME states it "
            "for livestock in 2019 and on 2020-07-02; from 2020-11-27 CME's livestock early close "
            "on the day after Thanksgiving is 12:05 CT."
        ),
    ),
    date(2019, 7, 4): Citation(
        _Z19,
        (
            "CME Group Globex Independence Day Holiday Schedule: July 3, 2019 to July 5, 2019 ... "
            "Trade Date|Wednesday July 3 | Friday July 5| Friday July 5| Friday July 5 ... "
            "Calendar Date|Wednesday July 3 |Wednesday,July 3|Thursday July 4 |Thursday July 4 "
            "into Friday July 5 ... Product|CLOSE|OPEN|HALT|OPEN ... Livestock|Early @ 1215 CT / "
            "1715 UTC|Markets Closed|Markets Closed|Friday @ 0830 / 1330 UTC"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-4th-of-july-holiday-schedule-compact.xls of "
            "CME's yearly holiday-calendars zip (Wayback capture 2021-01-26); the zip's sha256 is "
            "the document hash. CME's compact Globex holiday schedule gives one row per asset "
            "class; the 'Livestock' row covers CME livestock futures (LE and HE are not named "
            "individually)."
        ),
    ),
    date(2019, 9, 2): Citation(
        _Z19,
        (
            "CME Group Globex Labor Day Holiday Schedule: August 30, 2019 - September 3, 2019 ... "
            "Trade Date|Friday, August 30|Tuesday, September 3|Tuesday, September 3|Tuesday, "
            "September 3 ... Calendar Date|Friday,August 30|Sunday,Sept 1 into Monday,Sept "
            "2|Monday, Sept 2|Monday, Sept 2 into Tuesday, Sept 3 ... Product|CLOSE|OPEN|HALT|OPEN "
            "... Livestock|Regular per Product|Closed for Labor Day|Closed for Labor Day| Tuesday "
            "@ 0830 CT/1330 UTC"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-labor-day-holiday-schedule-compact.xls of "
            "CME's yearly holiday-calendars zip (Wayback capture 2021-01-26); the zip's sha256 is "
            "the document hash. CME's compact Globex holiday schedule gives one row per asset "
            "class; the 'Livestock' row covers CME livestock futures (LE and HE are not named "
            "individually)."
        ),
    ),
    date(2019, 11, 28): Citation(
        _Z19,
        (
            "CME Group Globex Thanksgiving Holiday Schedule: November 27, 2019 - November 29, 2019 "
            "... Trade Date|Wednesday ,November 27|| Friday, November 29 ... Products|Wednesday "
            ",November 27|Wednesday, November 27|Thursday ,November 28|Thursday , November "
            "28|Friday November 29|Friday November 29 ... Livestock|Regular per Product|Closed for "
            "Thanksgiving|Closed for Thanksgiving|Closed for Thanksgiving| Regular per Product| "
            "Early @ 1215 CT/ 1815 UTC"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-thanksgiving-holiday-schedule-compact.xls of "
            "CME's yearly holiday-calendars zip (Wayback capture 2021-01-26); the zip's sha256 is "
            "the document hash. CME's compact Globex holiday schedule gives one row per asset "
            "class; the 'Livestock' row covers CME livestock futures (LE and HE are not named "
            "individually)."
        ),
    ),
    date(2019, 11, 29): Citation(
        _Z19,
        (
            "CME Group Globex Thanksgiving Holiday Schedule: November 27, 2019 - November 29, 2019 "
            "... Trade Date|Wednesday ,November 27|| Friday, November 29 ... Products|Wednesday "
            ",November 27|Wednesday, November 27|Thursday ,November 28|Thursday , November "
            "28|Friday November 29|Friday November 29 ... Livestock|Regular per Product|Closed for "
            "Thanksgiving|Closed for Thanksgiving|Closed for Thanksgiving| Regular per Product| "
            "Early @ 1215 CT/ 1815 UTC"
        ),
        _Z19,
        (
            "Livestock|Regular per Product|Closed for Thanksgiving|Closed for Thanksgiving|Closed "
            "for Thanksgiving| Regular per Product| Early @ 1215 CT/ 1815 UTC"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-thanksgiving-holiday-schedule-compact.xls of "
            "CME's yearly holiday-calendars zip (Wayback capture 2021-01-26); the zip's sha256 is "
            "the document hash. CME's compact Globex holiday schedule gives one row per asset "
            "class; the 'Livestock' row covers CME livestock futures (LE and HE are not named "
            "individually). Full schedule globex-trading-schedules/2019-thanksgiving-schedule.xls "
            "(same zip): Livestock '12:15' under Calendar Date 'Friday, November 29', column "
            "'Close' (column headers read with xlrd, merged header cells expanded). Early close "
            "12:15 CT as CME states it for livestock in 2019 and on 2020-07-02; from 2020-11-27 "
            "CME's livestock early close on the day after Thanksgiving is 12:05 CT."
        ),
    ),
    date(2019, 12, 24): Citation(
        _Z19,
        (
            "CME Group Globex Christmas Holiday Schedule: December 24, 2019 - December 26, 2019 "
            "... Trade Date|Tuesday,December 24|Globex Closed|Thursday December 26|Thursday "
            "December 26|Thursday December 26 ... Products|Tuesday, Dec 24|Wednesday,Dec "
            "25|Wednesday December 25|Thursday,Dec 26|Thursday, Dec 26 ... Livestock|Early @ 1215 "
            "CT / 1815 UTC|Closed for Christmas|Closed for Christmas|Pre-open 6:00CT /12:00 UTC "
            "Open 8:30 CT /14:30 UTC|Regular per Product"
        ),
        _Z19,
        (
            "Livestock|Early @ 1215 CT / 1815 UTC|Closed for Christmas|Closed for "
            "Christmas|Pre-open 6:00CT /12:00 UTC Open 8:30 CT /14:30 UTC|Regular per Product"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-christmas-holiday-schedule-compact.xls of "
            "CME's yearly holiday-calendars zip (Wayback capture 2021-01-26); the zip's sha256 is "
            "the document hash. CME's compact Globex holiday schedule gives one row per asset "
            "class; the 'Livestock' row covers CME livestock futures (LE and HE are not named "
            "individually). Full schedule "
            "globex-trading-schedules/2019-christmas-holiday-schedule.xls (same zip): Livestock "
            "'12:15' under Calendar Date 'Tuesday, December 24', column 'Close' (column headers "
            "read with xlrd, merged header cells expanded). Early close 12:15 CT as CME states it "
            "for livestock in 2019 and on 2020-07-02; from 2020-11-27 CME's livestock early close "
            "on the day after Thanksgiving is 12:05 CT."
        ),
    ),
    date(2019, 12, 25): Citation(
        _Z19,
        (
            "CME Group Globex Christmas Holiday Schedule: December 24, 2019 - December 26, 2019 "
            "... Trade Date|Tuesday,December 24|Globex Closed|Thursday December 26|Thursday "
            "December 26|Thursday December 26 ... Products|Tuesday, Dec 24|Wednesday,Dec "
            "25|Wednesday December 25|Thursday,Dec 26|Thursday, Dec 26 ... Livestock|Early @ 1215 "
            "CT / 1815 UTC|Closed for Christmas|Closed for Christmas|Pre-open 6:00CT /12:00 UTC "
            "Open 8:30 CT /14:30 UTC|Regular per Product"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-christmas-holiday-schedule-compact.xls of "
            "CME's yearly holiday-calendars zip (Wayback capture 2021-01-26); the zip's sha256 is "
            "the document hash. CME's compact Globex holiday schedule gives one row per asset "
            "class; the 'Livestock' row covers CME livestock futures (LE and HE are not named "
            "individually)."
        ),
    ),
    date(2020, 1, 1): Citation(
        _Z19,
        (
            "CME Group Globex New Years Holiday Schedule: December 31, 2019 - January 2, 2020 ... "
            "Trade Date|Tuesday,Dec 31|Globex Closed|Thursday, January 2|Thursday, January "
            "2|Thursday, January 2 ... Calendar Trade|Tuesday, Dec 31|Wednessday, Jan 1 "
            "|Wednesday, Jan 1|Thursday, Jan 2|Thursday, Jan 2 ... Livestock|Regular close|Closed "
            "for New Year's|Closed for New Year's|Pre-open 6:00CT /12:00 UTC Open 8:30 CT /14:30 "
            "UTC|Regular Open and Close"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-new-years-holiday-schedule-compact.xls of "
            "CME's yearly holiday-calendars zip (Wayback capture 2021-01-26); the zip's sha256 is "
            "the document hash. CME's compact Globex holiday schedule gives one row per asset "
            "class; the 'Livestock' row covers CME livestock futures (LE and HE are not named "
            "individually). Full schedule "
            "globex-trading-schedules/2019-2020-new-years-holiday-schedule.xls (same zip): "
            "Livestock 'Globex Closed' under Calendar Date 'Wednesday, January 1' (column headers "
            "read with xlrd, merged header cells expanded)."
        ),
    ),
    date(2020, 1, 20): Citation(
        _Z20,
        (
            "CME Group Globex Martin Luther King Day Holiday Schedule: January 17, 2020 - January "
            "21, 2020 ... Trade Date|Friday, Jan 17|Tuesday, Jan 21|Tuesday, Jan 21|Tuesday, Jan "
            "21 ... Calendar Date|Friday, Jan 17|Sunday, Jan 19 into Monday, Jan 20|Monday, Jan "
            "20|Monday, Jan 20 into Tuesday, Jan 21 ... Products|CLOSE|OPEN|HALT|OPEN ... "
            "Livestock|Regular per Product|Closed for MLK Day|Closed for MLK Day|Tuesday @ 0830 "
            "CT/1430 UTC"
        ),
        note=(
            "Zip member 2020-martin-luther-king-holiday-schedule-compact.xls of CME's yearly "
            "holiday-calendars zip (Wayback capture 2026-07-30); the zip's sha256 is the document "
            "hash. CME's compact Globex holiday schedule gives one row per asset class; the "
            "'Livestock' row covers CME livestock futures (LE and HE are not named individually)."
        ),
    ),
    date(2020, 2, 17): Citation(
        _Z20,
        (
            "CME Group Globex Presidents Day Holiday Schedule: February 14, 2020 - February 18, "
            "2020 ... Trade Date|Friday, Feb 14||Tuesday, February 18 ... Calendar Date|Friday, "
            "Feb 14|Sunday, Feb 16 into Monday, Feb 17|Monday,Feb 17|Monday, Feb 17 into Tuesday, "
            "Feb 18 ... Products|CLOSE|OPEN|HALT|OPEN ... Livestock|Regular per Product|Closed for "
            "President's Day|Closed for President's Day|Tuesday @ 0830 CT/1430 UTC"
        ),
        note=(
            "Zip member 2020-presidents-day-holiday-schedule-compact.xls of CME's yearly "
            "holiday-calendars zip (Wayback capture 2026-07-30); the zip's sha256 is the document "
            "hash. CME's compact Globex holiday schedule gives one row per asset class; the "
            "'Livestock' row covers CME livestock futures (LE and HE are not named individually)."
        ),
    ),
    date(2020, 4, 10): Citation(
        _Z20,
        (
            "CME Group Globex Good Friday Holiday Schedule: April 9,2020 to April 13, 2020 ... "
            "Trade Date|Thursday,April 9|Friday, April 10|Monday, April 13 ... Calendar "
            "Date|Thursday April 9|Friday April 10|Sunday, April 12 into Monday, April 13 ... "
            "Product|CLOSE|CLOSED|OPEN ... Livestock|Regular per Product|Closed for Good "
            "Friday|Monday @ 0830/ 1330 UTC"
        ),
        note=(
            "Zip member 2020-good-friday-holiday-compact.xls of CME's yearly holiday-calendars zip "
            "(Wayback capture 2026-07-30); the zip's sha256 is the document hash. CME's compact "
            "Globex holiday schedule gives one row per asset class; the 'Livestock' row covers CME "
            "livestock futures (LE and HE are not named individually)."
        ),
    ),
    date(2020, 5, 25): Citation(
        _Z20,
        (
            "CME Group Globex Memorial Day Holiday Schedule: May 22, 2020 - May 26, 2020 ... Trade "
            "Date|Friday, May 22|Tuesday, May 26|Tuesday, May 26|Tuesday, May 26 ... Calendar "
            "Date|Friday,May 22|Sunday,May 24 into Monday,May 25|Monday, May 25|Mon,May 25 into "
            "Tues,May 26 ... Product|CLOSE|OPEN|HALT|OPEN ... Livestock|Regular per Product|Closed "
            "for Memorial Day|Closed for Memorial Day|Tuesday @ 0830 CT/1330 UTC"
        ),
        note=(
            "Zip member 2020-memorial-day-holiday-schedule-compact.xls of CME's yearly "
            "holiday-calendars zip (Wayback capture 2026-07-30); the zip's sha256 is the document "
            "hash. CME's compact Globex holiday schedule gives one row per asset class; the "
            "'Livestock' row covers CME livestock futures (LE and HE are not named individually)."
        ),
    ),
    date(2020, 7, 2): Citation(
        _Z20,
        (
            "CME Group Globex Independence Day Holiday Schedule: July 2, 2020 to July 6, 2020 ... "
            "Trade Date|Thursday, July 2|Monday, July 6|Monday, July 6|Monday, July 6 ... Calendar "
            "Date|Thursday July 2|Thursday , July 2|Friday July 3|Sunday July 5 into Monday July 6 "
            "... Product|CLOSE|OPEN|ClOSE|OPEN ... Livestock|Early @ 1215 CT / 1715 UTC|Markets "
            "Closed|Markets Closed|Monday @ 0830 / 1330 UTC"
        ),
        _Z20,
        (
            "Livestock|Early @ 1215 CT / 1715 UTC|Markets Closed|Markets Closed|Monday @ 0830 / "
            "1330 UTC"
        ),
        note=(
            "Zip member 2020-4th-of-july-holiday-schedule-compact.xls of CME's yearly "
            "holiday-calendars zip (Wayback capture 2026-07-30); the zip's sha256 is the document "
            "hash. CME's compact Globex holiday schedule gives one row per asset class; the "
            "'Livestock' row covers CME livestock futures (LE and HE are not named individually). "
            "Full schedule 2020-independence-day-schedule.xls (same zip): Livestock '12:15' under "
            "Calendar Date 'Thursday, July 2', column 'Early Close' (column headers read with "
            "xlrd, merged header cells expanded). Early close 12:15 CT as CME states it for "
            "livestock in 2019 and on 2020-07-02; from 2020-11-27 CME's livestock early close on "
            "the day after Thanksgiving is 12:05 CT. Unlike equities (which settled normally on "
            "2020-07-02), livestock closed early."
        ),
    ),
    date(2020, 7, 3): Citation(
        _Z20,
        (
            "CME Group Globex Independence Day Holiday Schedule: July 2, 2020 to July 6, 2020 ... "
            "Trade Date|Thursday, July 2|Monday, July 6|Monday, July 6|Monday, July 6 ... Calendar "
            "Date|Thursday July 2|Thursday , July 2|Friday July 3|Sunday July 5 into Monday July 6 "
            "... Product|CLOSE|OPEN|ClOSE|OPEN ... Livestock|Early @ 1215 CT / 1715 UTC|Markets "
            "Closed|Markets Closed|Monday @ 0830 / 1330 UTC"
        ),
        note=(
            "Zip member 2020-4th-of-july-holiday-schedule-compact.xls of CME's yearly "
            "holiday-calendars zip (Wayback capture 2026-07-30); the zip's sha256 is the document "
            "hash. CME's compact Globex holiday schedule gives one row per asset class; the "
            "'Livestock' row covers CME livestock futures (LE and HE are not named individually)."
        ),
    ),
    date(2020, 9, 7): Citation(
        _Z20,
        (
            "CME Group Globex Labor Day Holiday Schedule: September 4, 2020 - September 8, 2020 "
            "... Trade Date|Friday, September 4|Tuesday, September 8|Tuesday, September 8|Tuesday, "
            "September 8 ... Calendar Date|Friday,September 4|Sunday,Sept 6 into Monday,Sept "
            "7|Monday, Sept 7|Monday, Sept 7 into Tuesday, Sept 8 ... Product|CLOSE|OPEN|HALT|OPEN "
            "... Livestock|Regular per Product|Closed for Labor Day|Closed for Labor Day| Tuesday "
            "@ 0830 CT/1330 UTC"
        ),
        note=(
            "Zip member 2020-labor-day-holiday-schedule-compact.xls of CME's yearly "
            "holiday-calendars zip (Wayback capture 2026-07-30); the zip's sha256 is the document "
            "hash. CME's compact Globex holiday schedule gives one row per asset class; the "
            "'Livestock' row covers CME livestock futures (LE and HE are not named individually)."
        ),
    ),
    date(2020, 11, 26): Citation(
        _Z20,
        (
            "CME Group Globex Thanksgiving Holiday Schedule: November 25, 2020 - November 27, 2020 "
            "... Trade Date|Wednesday ,November 25|| Friday, November 27 ... Products|Wednesday "
            ",November 25|Wednesday, November 25|Thursday ,November 26|Thursday , November "
            "26|Friday November 27|Friday November 27 ... Livestock|Regular per Product|Closed for "
            "Thanksgiving|Closed for Thanksgiving|Closed for Thanksgiving| Regular per Product| "
            "Early @ 1205 CT/ 1805 UTC"
        ),
        note=(
            "Zip member 2020-thanksgiving-holiday-schedule-compact.xls of CME's yearly "
            "holiday-calendars zip (Wayback capture 2026-07-30); the zip's sha256 is the document "
            "hash. CME's compact Globex holiday schedule gives one row per asset class; the "
            "'Livestock' row covers CME livestock futures (LE and HE are not named individually)."
        ),
    ),
    date(2020, 11, 27): Citation(
        _Z20,
        (
            "CME Group Globex Thanksgiving Holiday Schedule: November 25, 2020 - November 27, 2020 "
            "... Trade Date|Wednesday ,November 25|| Friday, November 27 ... Products|Wednesday "
            ",November 25|Wednesday, November 25|Thursday ,November 26|Thursday , November "
            "26|Friday November 27|Friday November 27 ... Livestock|Regular per Product|Closed for "
            "Thanksgiving|Closed for Thanksgiving|Closed for Thanksgiving| Regular per Product| "
            "Early @ 1205 CT/ 1805 UTC"
        ),
        _Z20,
        (
            "Livestock|Regular per Product|Closed for Thanksgiving|Closed for Thanksgiving|Closed "
            "for Thanksgiving| Regular per Product| Early @ 1205 CT/ 1805 UTC"
        ),
        note=(
            "Zip member 2020-thanksgiving-holiday-schedule-compact.xls of CME's yearly "
            "holiday-calendars zip (Wayback capture 2026-07-30); the zip's sha256 is the document "
            "hash. CME's compact Globex holiday schedule gives one row per asset class; the "
            "'Livestock' row covers CME livestock futures (LE and HE are not named individually). "
            "Full schedule 2020-thanksgiving-schedule.xls (same zip): Livestock '12:05' under "
            "Calendar Date 'Friday, November 27', column 'Close' (column headers read with xlrd, "
            "merged header cells expanded)."
        ),
    ),
    date(2020, 12, 24): Citation(
        _Z20,
        (
            "CME Group Globex Christmas Holiday Schedule: December 24, 2020 - December 28, 2020 "
            "... Trade Date|Thursday,December 24|Globex Closed|Monday December 28|Monday December "
            "28|Monday December 28 ... Products|Thursday, Dec 24|Friday,Dec 25|Sunday "
            "27|Monday,Dec 28|Monday, Dec 28 ... Livestock|Early @ 1205 CT / 1805 UTC|Closed for "
            "Christmas|Closed for Christmas|Pre-open 8:00CT /14:00 UTC Open 8:30 CT /14:00 "
            "UTC|Regular per Product"
        ),
        _Z20,
        (
            "Livestock|Early @ 1205 CT / 1805 UTC|Closed for Christmas|Closed for "
            "Christmas|Pre-open 8:00CT /14:00 UTC Open 8:30 CT /14:00 UTC|Regular per Product"
        ),
        note=(
            "Zip member 2020-christmas-holiday-schedule-compact.xls of CME's yearly "
            "holiday-calendars zip (Wayback capture 2026-07-30); the zip's sha256 is the document "
            "hash. CME's compact Globex holiday schedule gives one row per asset class; the "
            "'Livestock' row covers CME livestock futures (LE and HE are not named individually). "
            "Full schedule 2020-christmas-holiday-schedule.xls (same zip): Livestock '12:05' under "
            "Calendar Date 'Thursday, December 24', column 'Close' (column headers read with xlrd, "
            "merged header cells expanded)."
        ),
    ),
    date(2020, 12, 25): Citation(
        _Z20,
        (
            "CME Group Globex Christmas Holiday Schedule: December 24, 2020 - December 28, 2020 "
            "... Trade Date|Thursday,December 24|Globex Closed|Monday December 28|Monday December "
            "28|Monday December 28 ... Products|Thursday, Dec 24|Friday,Dec 25|Sunday "
            "27|Monday,Dec 28|Monday, Dec 28 ... Livestock|Early @ 1205 CT / 1805 UTC|Closed for "
            "Christmas|Closed for Christmas|Pre-open 8:00CT /14:00 UTC Open 8:30 CT /14:00 "
            "UTC|Regular per Product"
        ),
        note=(
            "Zip member 2020-christmas-holiday-schedule-compact.xls of CME's yearly "
            "holiday-calendars zip (Wayback capture 2026-07-30); the zip's sha256 is the document "
            "hash. CME's compact Globex holiday schedule gives one row per asset class; the "
            "'Livestock' row covers CME livestock futures (LE and HE are not named individually)."
        ),
    ),
    date(2021, 1, 1): Citation(
        _Z20,
        (
            "CME Group Globex New Years Holiday Schedule: December 31, 2020 - January 4, 2021 ... "
            "Trade Date|Thursday,Dec 31|Globex Closed|Monday, January 4|Monday, January 4|Monday, "
            "January 4 ... Calendar Trade|Thursday,Dec 31|Friday,Jan 1|Sunday,Jan 3|Monday, Jan "
            "4|Monday, Jan 4 ... Livestock|Regular close|Closed for New Year's|Closed for New "
            "Year's|Pre-open 8:00CT /14:00 UTC Open 8:30 CT /14:30 UTC|Regular Open and Close"
        ),
        note=(
            "Zip member 2021-new-years-holiday-schedule-compact.xls of CME's yearly "
            "holiday-calendars zip (Wayback capture 2026-07-30); the zip's sha256 is the document "
            "hash. CME's compact Globex holiday schedule gives one row per asset class; the "
            "'Livestock' row covers CME livestock futures (LE and HE are not named individually)."
        ),
    ),
    date(2021, 1, 18): Citation(
        _Z21,
        (
            "CME Group Globex Martin Luther King Day Holiday Schedule: January 15, 2021 - January "
            "19, 2021 ... Trade Date|Friday, Jan 15|Tuesday, Jan 19|Tuesday, Jan 19|Tuesday, Jan "
            "19 ... Calendar Date|Friday, Jan 15|Sunday, Jan 17 into Monday, Jan 18|Monday, Jan "
            "18|Monday, Jan 18 into Tuesday, Jan 19 ... Products|CLOSE|OPEN|HALT|OPEN ... "
            "Livestock|Regular per Product|Closed for MLK Day|Closed for MLK Day|Tuesday @ 0830 "
            "CT/1430 UTC"
        ),
        note=(
            "Zip member 2021-mlk-day-schedule-compact.xls of CME's yearly holiday-calendars zip "
            "(Wayback capture 2026-08-30); the zip's sha256 is the document hash. CME's compact "
            "Globex holiday schedule gives one row per asset class; the 'Livestock' row covers CME "
            "livestock futures (LE and HE are not named individually)."
        ),
    ),
    date(2021, 2, 15): Citation(
        _Z21,
        (
            "CME Group Globex Presidents Day Holiday Schedule: February 12, 2021 - February 16, "
            "2021 ... Trade Date|Friday, Feb 12||Tuesday, February 16 ... Calendar Date|Friday, "
            "Feb 12|Sunday, Feb 14 into Monday, Feb 15|Monday,Feb 15|Monday, Feb 15 into Tuesday, "
            "Feb 16 ... Products|CLOSE|OPEN|HALT|OPEN ... Livestock|Regular per Product|Closed for "
            "President's Day|Closed for President's Day|Tuesday @ 0830 CT/1430 UTC"
        ),
        note=(
            "Zip member 2021-presidents-day-holiday-schedule-compact.xls of CME's yearly "
            "holiday-calendars zip (Wayback capture 2026-08-30); the zip's sha256 is the document "
            "hash. CME's compact Globex holiday schedule gives one row per asset class; the "
            "'Livestock' row covers CME livestock futures (LE and HE are not named individually)."
        ),
    ),
    date(2021, 4, 2): Citation(
        _Z21,
        (
            "CME Group Globex Good Friday Holiday Schedule: April 1,2021 to April 5, 2021 ... "
            "Trade Date|Thursday,April 1|Friday, April 2|Friday, April 2|Monday, April 5 ... "
            "Calendar Date|Thursday April 1|Thursday,April 1|Friday April 2|Sunday, April 4 into "
            "Monday, April 5 ... Product|CLOSE|OPEN|CLOSED|OPEN ... Livestock|Regular per "
            "Product|Closed for Good Friday|Closed for Good Friday|Monday @ 0830 CT/ 1330 UTC"
        ),
        note=(
            "Zip member 2021-good-friday-holiday-schedule-compact.xls of CME's yearly "
            "holiday-calendars zip (Wayback capture 2026-08-30); the zip's sha256 is the document "
            "hash. CME's compact Globex holiday schedule gives one row per asset class; the "
            "'Livestock' row covers CME livestock futures (LE and HE are not named individually). "
            "Jobs-report Good Friday: equities traded an abbreviated session; livestock was closed."
        ),
    ),
    date(2021, 5, 31): Citation(
        _Z21,
        (
            "CME Group Globex Memorial Day Holiday Schedule: May 28, 2021 - June 1st, 2021 ... "
            "Trade Date|Friday, May 28|Tuesday, June 1|Tuesday, June 1|Tuesday, June 1 ... "
            "Calendar Date|Friday,May 28|Sunday,May 30|Monday, May 31|Monday, May 31 into Tues, "
            "June 1 ... Product|CLOSE|OPEN|HALT|OPEN ... Livestock|Regular per Product|Closed for "
            "Memorial Day|Closed for Memorial Day|Tuesday @ 0830 CT/1330 UTC"
        ),
        note=(
            "Zip member 2021-memorial-day-holiday-schedule-compact.xls of CME's yearly "
            "holiday-calendars zip (Wayback capture 2026-08-30); the zip's sha256 is the document "
            "hash. CME's compact Globex holiday schedule gives one row per asset class; the "
            "'Livestock' row covers CME livestock futures (LE and HE are not named individually)."
        ),
    ),
    date(2021, 7, 5): Citation(
        _Z21,
        (
            "CME Group Globex Independence Day Holiday Schedule: July 2, 2021 to July 6, 2021 ... "
            "Trade Date|Friday, July 2|Tuesday, July 6|Tuesday, July 6|Tuesday, July 6 ... "
            "Calendar Date|Friday July 2|Sunday July 4|Monday July 5|Monday July 5 ... "
            "Product|CLOSE|OPEN|HALT|OPEN ... Livestock|Regular Per Product|Markets Closed|Markets "
            "Closed|Tuesday July 6 Regular @ 0830 / 1330 UTC"
        ),
        note=(
            "Zip member 2021-independence-day-holiday-schedule-compact.xls of CME's yearly "
            "holiday-calendars zip (Wayback capture 2026-08-30); the zip's sha256 is the document "
            "hash. CME's compact Globex holiday schedule gives one row per asset class; the "
            "'Livestock' row covers CME livestock futures (LE and HE are not named individually)."
        ),
    ),
    date(2021, 9, 6): Citation(
        _Z21,
        (
            "CME Group Globex Labor Day Holiday Schedule: September 3, 2021 - September 7, 2021 "
            "... Trade Date|Friday, September 3|Tuesday, September 7|Tuesday, September 7|Tuesday, "
            "September 7 ... Calendar Date|Friday,September 3|Sunday,Sept 5 into Monday,Sept "
            "6|Monday, Sept 6|Monday, Sept 6 into Tuesday, Sept 7 ... Product|CLOSE|OPEN|HALT|OPEN "
            "... Livestock|Regular per Product|Closed for Labor Day|Closed for Labor Day| Tuesday "
            "@ 0830 CT/1330 UTC"
        ),
        note=(
            "Zip member 2021-labor-day-holiday-schedule-compact.xls of CME's yearly "
            "holiday-calendars zip (Wayback capture 2026-08-30); the zip's sha256 is the document "
            "hash. CME's compact Globex holiday schedule gives one row per asset class; the "
            "'Livestock' row covers CME livestock futures (LE and HE are not named individually)."
        ),
    ),
    date(2021, 11, 25): Citation(
        _Z21,
        (
            "CME Group Globex Thanksgiving Holiday Schedule: November 24, 2021 - November 26, 2021 "
            "... Trade Date|Wednesday ,November 24|| Friday, November 26 ... Products|Wednesday "
            ",November 24|Wednesday, November 24|Thursday ,November 25|Thursday , November "
            "25|Friday November 26|Friday November 26 ... Livestock|Regular per Product|Closed for "
            "Thanksgiving|Closed for Thanksgiving|Closed for Thanksgiving| Regular @ 8:30 CT/ 1430 "
            "UTC| Early @ 1205 CT/ 1805 UTC"
        ),
        note=(
            "Zip member 2021-thanksgiving-holiday-schedule-compact.xls of CME's yearly "
            "holiday-calendars zip (Wayback capture 2026-08-30); the zip's sha256 is the document "
            "hash. CME's compact Globex holiday schedule gives one row per asset class; the "
            "'Livestock' row covers CME livestock futures (LE and HE are not named individually)."
        ),
    ),
    date(2021, 11, 26): Citation(
        _Z21,
        (
            "CME Group Globex Thanksgiving Holiday Schedule: November 24, 2021 - November 26, 2021 "
            "... Trade Date|Wednesday ,November 24|| Friday, November 26 ... Products|Wednesday "
            ",November 24|Wednesday, November 24|Thursday ,November 25|Thursday , November "
            "25|Friday November 26|Friday November 26 ... Livestock|Regular per Product|Closed for "
            "Thanksgiving|Closed for Thanksgiving|Closed for Thanksgiving| Regular @ 8:30 CT/ 1430 "
            "UTC| Early @ 1205 CT/ 1805 UTC"
        ),
        _Z21,
        (
            "Livestock|Regular per Product|Closed for Thanksgiving|Closed for Thanksgiving|Closed "
            "for Thanksgiving| Regular @ 8:30 CT/ 1430 UTC| Early @ 1205 CT/ 1805 UTC"
        ),
        note=(
            "Zip member 2021-thanksgiving-holiday-schedule-compact.xls of CME's yearly "
            "holiday-calendars zip (Wayback capture 2026-08-30); the zip's sha256 is the document "
            "hash. CME's compact Globex holiday schedule gives one row per asset class; the "
            "'Livestock' row covers CME livestock futures (LE and HE are not named individually). "
            "Full schedule 2021-thanksgiving-holiday-schedule.xls (same zip): Livestock '12:05' "
            "under Calendar Date 'Friday, November 26', column 'Close' (column headers read with "
            "xlrd, merged header cells expanded)."
        ),
    ),
    date(2021, 12, 24): Citation(
        _Z21,
        (
            "CME Group Globex Christmas Holiday Schedule: December 23, 2021 - December 27, 2021 "
            "... Trade Date|Thursday,December 23|Globex Closed|Monday December 27|Monday December "
            "27 ... Products|Thursday, Dec 23|Friday,Dec 24|Sunday 26|Monday,Dec 27 ... "
            "Livestock|Regular per Product|Closed for Christmas|Closed for Christmas|Pre-open "
            "8:00CT /14:00 UTC Open 8:30 CT /14:30 UTC"
        ),
        note=(
            "Zip member 2021-christmas-holiday-schedule-compact.xls of CME's yearly "
            "holiday-calendars zip (Wayback capture 2026-08-30); the zip's sha256 is the document "
            "hash. CME's compact Globex holiday schedule gives one row per asset class; the "
            "'Livestock' row covers CME livestock futures (LE and HE are not named individually)."
        ),
    ),
    date(2022, 1, 17): Citation(
        _HC + "2022-mlk-day-holiday-schedule-compact.xls",
        (
            "CME Group Globex Martin Luther King Day Holiday Schedule: January 14, 2022 - January "
            "18, 2022 ... Trade Date|Friday, Jan 14|Tuesday, Jan 18|Tuesday, Jan 18|Tuesday, Jan "
            "18 ... Calendar Date|Friday, Jan 14|Sunday, Jan 16 into Monday, Jan 17|Monday, Jan "
            "17|Monday, Jan 17 into Tuesday, Jan 18 ... Products|CLOSE|OPEN|HALT|OPEN ... "
            "Livestock|Regular per Product|Closed for MLK Day|Closed for MLK Day|Tuesday @ 0830 "
            "CT/1430 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule (Wayback capture 2022-07-04); one row per asset "
            "class, the 'Livestock' row covers CME livestock futures (LE and HE are not named "
            "individually)."
        ),
    ),
    date(2022, 2, 21): Citation(
        _HC + "2022-presidents-day-holiday-schedule-compact.xls",
        (
            "CME Group Globex Presidents Day Holiday Schedule: February 18, 2022 - February 22, "
            "2022 ... Trade Date|Friday, Feb 18||Tuesday, February 22 ... Calendar Date|Friday, "
            "Feb 18|Sunday, Feb 20 into Monday, Feb 21|Monday,Feb 21|Monday, Feb 21 into Tuesday, "
            "Feb 22 ... Products|CLOSE|OPEN|HALT|OPEN ... Livestock|Regular per Product|Closed for "
            "President's Day|Closed for President's Day|Tuesday @ 0830 CT/1430 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule (Wayback capture 2022-02-17); one row per asset "
            "class, the 'Livestock' row covers CME livestock futures (LE and HE are not named "
            "individually)."
        ),
    ),
    date(2022, 4, 15): Citation(
        _HC + "2022-good-friday-holiday-schedule-compact.xls",
        (
            "CME Group Globex Good Friday Holiday Schedule: April 14,2022 to April 18, 2022 ... "
            "Trade Date|Thursday,April 14|Friday, April 15|Monday, April 18 ... Calendar "
            "Date|Thursday April 14|Friday April 15|Sunday, April 17 into Monday, April 18 ... "
            "Product|CLOSE|CLOSED|OPEN ... Livestock|Regular per Product|Closed for Good "
            "Friday|Monday @ 0830 CT/ 1330 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule (Wayback capture 2022-04-12); one row per asset "
            "class, the 'Livestock' row covers CME livestock futures (LE and HE are not named "
            "individually)."
        ),
    ),
    date(2022, 5, 30): Citation(
        _HC + "2022-memorial-day-holiday-schedule-compact.xls",
        (
            "CME Group Globex Memorial Day Holiday Schedule: May 27, 2022 - May 31 , 2022 ... "
            "Trade Date|Friday, May 27|Tuesday, May 31|Tuesday, May 31|Tuesday, May 31 ... "
            "Calendar Date|Friday,May 27|Sunday,May 29|Monday, May 30|Monday, May 30 into Tues, "
            "May31 ... Product|CLOSE|OPEN|HALT|OPEN ... Livestock|Regular per Product|Closed for "
            "Memorial Day|Closed for Memorial Day|Tuesday @ 0830 CT/1330 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule (Wayback capture 2022-07-04); one row per asset "
            "class, the 'Livestock' row covers CME livestock futures (LE and HE are not named "
            "individually)."
        ),
    ),
    date(2022, 6, 20): Citation(
        _HC + "2022-juneteenth-holiday-schedule.xls",
        (
            "CME Group Globex Juneteenth Holiday Schedule: June 17, 2022 - Jun 21, 2022 ... "
            "Livestock|13:05|14:30-16:00|||||||||||||||||||08:00|08:30"
        ),
        note=(
            "CME's full Globex Juneteenth schedule ('Updated 5/18/2022'; Wayback capture "
            "2022-06-20; no compact version was captured). Livestock row, columns read with xlrd: "
            "'13:05' and '14:30-16:00' under Calendar Date 'Friday, June 17' (Regular Fri. Close, "
            "PCP), then '08:00' and '08:30' under 'Tuesday, Jun 21' (Pre-opening, Open); no "
            "livestock cell under Sunday June 19 or Monday June 20. CME's Juneteenth 2022 "
            "settlement notice: no settlement prices for CME products on Monday June 20."
        ),
    ),
    date(2022, 7, 4): Citation(
        _HC + "2022-independence-day-holiday-schedule-compact.xls",
        (
            "CME Group Globex Independence Day Holiday Schedule: July 1, 2022 to July 5, 2022 ... "
            "Trade Date|Friday, July 1|Tuesday, July 5|Tuesday, July 5|Tuesday, July 5 ... "
            "Calendar Date|Friday July 1|Sunday July 3|Monday July 4|Monday July 4 ... "
            "Product|CLOSE|OPEN|HALT|OPEN ... Livestock|Regular Per Product|Markets Closed|Markets "
            "Closed|Tuesday July 5 Regular @ 0830 / 1330 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule (Wayback capture 2022-07-04); one row per asset "
            "class, the 'Livestock' row covers CME livestock futures (LE and HE are not named "
            "individually)."
        ),
    ),
    date(2022, 9, 5): Citation(
        _HC + "2022-labor-day-holiday-schedule-compact.xls",
        (
            "CME Group Globex Labor Day Holiday Schedule: September 2, 2022 - September 6, 2022 "
            "... Trade Date|Friday, September 2|Tuesday, September 6|Tuesday, September 6|Tuesday, "
            "September 6 ... Calendar Date|Friday, September 2|Sunday,Sept 4 into Monday, Sept "
            "5|Monday, Sept 5|Monday, Sept 5 into Tuesday, Sept 6 ... Product|CLOSE|OPEN|HALT|OPEN "
            "... Livestock|Regular per Product|Closed for Labor Day|Closed for Labor Day| Tuesday "
            "@ 0830 CT/1330 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule (Wayback capture 2022-07-04); one row per asset "
            "class, the 'Livestock' row covers CME livestock futures (LE and HE are not named "
            "individually). The capture predates the holiday by two months; no later capture "
            "exists."
        ),
    ),
    date(2022, 11, 24): Citation(
        _HC + "2022-thanksgiving-holiday-schedule-compact.xls",
        (
            "CME Group Globex Thanksgiving Holiday Schedule: November 23, 2022 - November 25, 2022 "
            "... Trade Date|Wednesday ,November 23|| Friday, November 25 ... Products|Wednesday "
            ",November 23|Wednesday, November 23|Thursday ,November 24|Thursday , November "
            "24|Friday November 25|Friday November 25 ... Livestock|Regular per Product|Closed for "
            "Thanksgiving|Closed for Thanksgiving|Closed for Thanksgiving| Regular @ 8:30 CT/ 1430 "
            "UTC| Early @ 1205 CT/ 1805 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule (Wayback capture 2022-07-04); one row per asset "
            "class, the 'Livestock' row covers CME livestock futures (LE and HE are not named "
            "individually). The compact capture predates the holiday; the full schedule captured "
            "2022-11-22 (saved by CME 2022-11-11) has no livestock cell on Thursday November 24."
        ),
    ),
    date(2022, 11, 25): Citation(
        _HC + "2022-thanksgiving-holiday-schedule-compact.xls",
        (
            "CME Group Globex Thanksgiving Holiday Schedule: November 23, 2022 - November 25, 2022 "
            "... Trade Date|Wednesday ,November 23|| Friday, November 25 ... Products|Wednesday "
            ",November 23|Wednesday, November 23|Thursday ,November 24|Thursday , November "
            "24|Friday November 25|Friday November 25 ... Livestock|Regular per Product|Closed for "
            "Thanksgiving|Closed for Thanksgiving|Closed for Thanksgiving| Regular @ 8:30 CT/ 1430 "
            "UTC| Early @ 1205 CT/ 1805 UTC"
        ),
        _HC + "2022-thanksgiving-holiday-schedule.xls",
        (
            "CME Group Globex Thanksgiving Holiday Schedule: November 23, 2022 - November 25, 2022 "
            "... Livestock|13:05|14:30-16:00|||||||||||||||||||||08:00|08:30|12:05"
        ),
        note=(
            "CME's compact Globex holiday schedule (Wayback capture 2022-07-04); one row per asset "
            "class, the 'Livestock' row covers CME livestock futures (LE and HE are not named "
            "individually). Time from CME's full Thanksgiving schedule captured 2022-11-22 (file "
            "saved by CME 2022-11-11): Livestock '08:00', '08:30', '12:05' under Calendar Date "
            "'Friday, November 25', columns Pre-opening, Open, Close (column headers read with "
            "xlrd); the July compact gives 'Early @ 1205 CT'."
        ),
    ),
    date(2022, 12, 26): Citation(
        _HC + "2022-christmas-holiday-schedule.xls",
        (
            "CME Group Globex Christmas Holiday Schedule: December 23, 2022 - December 27, 2022 "
            "... Livestock|13:05 (*PCP 14:30-16:00)||||||||Globex Closed|Globex Closed|Globex "
            "Closed|Globex Closed|Globex Closed|Globex Closed|Globex Closed|Globex Closed|Globex "
            "Closed|Globex Closed|||||||08:00|08:30|13:05|14:30-16:00"
        ),
        note=(
            "CME's full Globex Christmas schedule ('Updated 6/29/2022'; Wayback capture "
            "2022-07-04, the only capture). Livestock row, columns read with xlrd: '13:05 (*PCP "
            "14:30-16:00)' under Calendar Date 'Friday, December 23'; 'Globex Closed' in every "
            "column under 'Monday, December 26'; '08:00', '08:30', '13:05' under 'Tuesday, "
            "December 27'. CME's Christmas 2022 settlement notice: no settlement prices on Monday "
            "December 26."
        ),
    ),
    date(2023, 1, 2): Citation(
        _HC + "2023-new-years-holiday-schedule-compact.xls",
        (
            "CME Group Globex New Years Holiday Schedule: December 30, 2022 - January 3, 2023 ... "
            "Trade Date|Friday,Dec 30|Sunday, January 1 and Monday, January 2|Sunday, January 1 "
            "and Monday, January 2| Tuesday, January 3 ... Calendar Trade|Friday,Dec 30|Sunday, "
            "Jan 1 and Monday, Jan 2|Monday,Jan 2|Tuesday, Jan 3|Tuesday, Jan 3 ... "
            "Livestock|Regular @ 1305 CT/1905 UTC|Globex Closed||Pre-open 8:00CT /14:00 UTC Open "
            "8:30CT /14:30 UTC|Regular @ 1305 CT/1905 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule (Wayback capture 2022-07-04); one row per asset "
            "class, the 'Livestock' row covers CME livestock futures (LE and HE are not named "
            "individually). The only capture (2022-07-04) predates the holiday by six months."
        ),
    ),
    date(2023, 1, 16): Citation(
        _AMP_MLK_2023,
        (
            "CME Group Globex Dr. Martin Luther King, Jr. Holiday Schedule: 13 - 17 January 2023 "
            "... Livestock Regular per Product Closed for MLK Day Closed for MLK Day Closed for "
            "MLK Day Regular per Product"
        ),
        note=(
            "SECONDARY: no CME-hosted Globex schedule naming livestock for MLK Day 2023 was "
            "retrievable (CME moved 2023 holiday hours into the trading-hours service, whose "
            "Wayback captures hold no events for January 2023; CME's 2023 MLK xls covers only MGEX "
            "and DME). The quote is from an image of CME's compact 'CME Group Globex' MLK 2023 "
            "schedule posted by AMP Futures (a broker) on "
            "ampfutures.com/news/holiday-trading-schedule-martin-luther-king-day-2023; the text "
            "was read by OCR (rapidocr) and the verbatim check runs on the OCR text. The Livestock "
            "row reads 'Closed for MLK Day' under Sunday Jan 15 (OPEN), Monday Jan 16 (HALT) and "
            "Monday Jan 16 (OPEN). CME's own MLK 2023 settlement notice says no settlement prices "
            "were derived for CME products on January 16."
        ),
    ),
    date(2023, 2, 20): Citation(
        "https://www.cmegroup.com/files/presidents-day.pdf",
        (
            "PRODUCT NAME Cleared As SUNDAY, 19 FEB 2023 MONDAY, 20 FEB 2023 TUESDAY, 21 FEB 2023 "
            "... TRADE DATE: TUES 21 FEB 08:00 (PREOPEN) 08:30 (OPEN) LIVESTOCK 13:05 (CLOSED) "
            "14:30 (PCP)"
        ),
        note=(
            "CME's holiday summary PDF ('the most actively traded instruments for each asset "
            "class'; Wayback capture 2023-03-29). The LIVESTOCK row lists session events only "
            "under Tuesday 21 Feb; no livestock event is listed under Monday 20 Feb (pdftotext "
            "-layout places them in the Tuesday 21 Feb column)."
        ),
    ),
    date(2023, 4, 7): Citation(
        "https://www.cmegroup.com/files/good-friday.pdf",
        (
            "PRODUCT NAME THURSDAY, 6 APR 2023 FRIDAY, 7 APR 2023 ... TRADE DATE: THURS 6 APR "
            "08:00 (PREOPEN) LIVESTOCK 08:30 (OPEN) 13:05 (CLOSED) 14:30 (PCP) 16:00 (CLOSED)"
        ),
        note=(
            "CME's holiday summary PDF ('the most actively traded instruments for each asset "
            "class'; Wayback capture 2024-07-08). The LIVESTOCK row lists session events only "
            "under Thursday 6 Apr; no livestock event is listed under Friday 7 Apr (pdftotext "
            "-layout places them in the Thursday 6 Apr column). Jobs-report Good Friday: equities "
            "traded until 08:15 CT; livestock was closed."
        ),
    ),
    date(2023, 5, 29): Citation(
        _TH + "memorial-day-2023.pdf",
        (
            "PRODUCT NAME SUNDAY, 28 MAY 2023 MONDAY, 29 MAY 2023 TUESDAY, 30 MAY 2023 ... TRADE "
            "DATE: TUES 30 MAY 08:00 (PREOPEN) 08:30 (OPEN) LIVESTOCK 13:05 (CLOSED) 14:30 (PCP) "
            "16:00 (CLOSED)"
        ),
        note=(
            "CME's holiday summary PDF ('the most actively traded instruments for each asset "
            "class'; Wayback capture 2023-04-20). The LIVESTOCK row lists session events only "
            "under Tuesday 30 May; no livestock event is listed under Monday 29 May (pdftotext "
            "-layout places them in the Tuesday 30 May column)."
        ),
    ),
    date(2023, 6, 19): Citation(
        _TH + "juneteenth-2023.pdf",
        (
            "PRODUCT NAME SUNDAY, 18 JUNE 2023 MONDAY, 19 JUNE 2023 TUESDAY, 20 JUNE 2023 ... "
            "TRADE DATE: TUES 20 JUNE 08:00 (PREOPEN) 08:30 (OPEN) LIVESTOCK 13:05 (CLOSED) 14:30 "
            "(PCP) 16:00 (CLOSED)"
        ),
        note=(
            "CME's holiday summary PDF ('the most actively traded instruments for each asset "
            "class'; Wayback capture 2023-06-13). The LIVESTOCK row lists session events only "
            "under Tuesday 20 June; no livestock event is listed under Monday 19 June (pdftotext "
            "-layout places them in the Tuesday 20 June column)."
        ),
    ),
    date(2023, 7, 4): Citation(
        _TH + "4th-of-july-2023.pdf",
        (
            "PRODUCT NAME MONDAY, 3 JULY 2023 TUESDAY, 4 JULY 2023 WEDNESDAY, 5 JULY 2023 ... "
            "TRADE DATE: MON 3 JULY TRADE DATE: WED 5 JULY 08:00 (PREOPEN) 08:00 (PREOPEN) 08:30 "
            "(OPEN) 08:30 (OPEN) LIVESTOCK 13:05 (CLOSED) 13:05 (CLOSED)"
        ),
        note=(
            "CME's holiday summary PDF ('the most actively traded instruments for each asset "
            "class'; Wayback capture 2023-06-27). The LIVESTOCK row lists session events only "
            "under Monday 3 July and Wednesday 5 July; no livestock event is listed under Tuesday "
            "4 July (pdftotext -layout places them in the Monday 3 July and Wednesday 5 July "
            "column)."
        ),
    ),
    date(2023, 9, 4): Citation(
        _svc("2023-09-03", "2023-09-05", "1720455278654"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2023-09-03","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2023-09-04","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2023-09-05","events":[{"tradingDate":"2023-09-05",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2023-09-05",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2023-09-05",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2023-09-05",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2023-09-05",'
            '"eventTime":"16:00","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2024-07-08. eventDate 2023-09-04 has an empty event list (no livestock "
            "session) while the adjacent weekday(s) in the same record carry the regular 08:00 "
            "preopen, 08:30 open and 13:05 close. HE (Lean Hogs) is not in the captured request "
            "and is taken to share LE's livestock hours, as the Livestock / LIVESTOCK rows of "
            "CME's 2019-2023 schedules state for both. CME's Labor Day 2023 summary PDF agrees "
            "(LIVESTOCK events only under Tuesday 5 Sep)."
        ),
    ),
    date(2023, 11, 23): Citation(
        _svc("2023-11-22", "2023-11-24", "1720455278656"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2023-11-22","events":[{"tradingDate":"2023-11-22",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2023-11-22",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2023-11-22",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2023-11-22",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2023-11-22",'
            '"eventTime":"16:00","marketEventType":"closed"}]} ... '
            '{"groupCode":"LE","eventDate":"2023-11-23","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2023-11-24","events":[{"tradingDate":"2023-11-24",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2023-11-24",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2023-11-24",'
            '"eventTime":"12:05","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2024-07-08. eventDate 2023-11-23 has an empty event list (no livestock "
            "session) while the adjacent weekday(s) in the same record carry the regular 08:00 "
            "preopen, 08:30 open and 13:05 close. HE (Lean Hogs) is not in the captured request "
            "and is taken to share LE's livestock hours, as the Livestock / LIVESTOCK rows of "
            "CME's 2019-2023 schedules state for both. CME's Thanksgiving 2023 summary PDF agrees; "
            "there the livestock row is labelled AGRICULTURE (grains have their own GRAINS row)."
        ),
    ),
    date(2023, 11, 24): Citation(
        _svc("2023-11-22", "2023-11-24", "1720455278656"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2023-11-22","events":[{"tradingDate":"2023-11-22",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2023-11-22",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2023-11-22",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2023-11-22",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2023-11-22",'
            '"eventTime":"16:00","marketEventType":"closed"}]} ... '
            '{"groupCode":"LE","eventDate":"2023-11-23","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2023-11-24","events":[{"tradingDate":"2023-11-24",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2023-11-24",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2023-11-24",'
            '"eventTime":"12:05","marketEventType":"closed"}]}'
        ),
        _svc("2023-11-22", "2023-11-24", "1720455278656"),
        (
            '{"groupCode":"LE","eventDate":"2023-11-24","events":[{"tradingDate":"2023-11-24",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2023-11-24",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2023-11-24",'
            '"eventTime":"12:05","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2024-07-08. eventDate 2023-11-24 lists 08:00 preopen, 08:30 open and a 12:05 "
            "close (the regular close is 13:05). HE (Lean Hogs) is not in the captured request and "
            "is taken to share LE's livestock hours, as the Livestock / LIVESTOCK rows of CME's "
            "2019-2023 schedules state for both. CME's Thanksgiving 2023 summary PDF agrees: "
            "AGRICULTURE row (livestock hours; grains have their own row) '08:30 (OPEN)' and "
            "'12:05 (CLOSED)' under Friday 24 November."
        ),
    ),
    date(2023, 12, 25): Citation(
        _svc("2023-12-24", "2023-12-26", "1720455278659"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2023-12-24","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2023-12-25","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2023-12-26","events":[{"tradingDate":"2023-12-26",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2023-12-26",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2023-12-26",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2023-12-26",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2023-12-26",'
            '"eventTime":"16:00","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2024-07-08. eventDate 2023-12-25 has an empty event list (no livestock "
            "session) while the adjacent weekday(s) in the same record carry the regular 08:00 "
            "preopen, 08:30 open and 13:05 close. HE (Lean Hogs) is not in the captured request "
            "and is taken to share LE's livestock hours, as the Livestock / LIVESTOCK rows of "
            "CME's 2019-2023 schedules state for both. CME's Christmas 2023 summary PDF agrees "
            "(LIVESTOCK events only under Tuesday 26 Dec)."
        ),
    ),
    date(2024, 1, 1): Citation(
        _svc("2023-12-31", "2024-01-02", "1720455278661"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2023-12-31","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2024-01-01","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2024-01-02","events":[{"tradingDate":"2024-01-02",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2024-01-02",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2024-01-02",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2024-01-02",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2024-01-02",'
            '"eventTime":"16:00","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2024-07-08. eventDate 2024-01-01 has an empty event list (no livestock "
            "session) while the adjacent weekday(s) in the same record carry the regular 08:00 "
            "preopen, 08:30 open and 13:05 close. HE (Lean Hogs) is not in the captured request "
            "and is taken to share LE's livestock hours, as the Livestock / LIVESTOCK rows of "
            "CME's 2019-2023 schedules state for both. CME's New Year's Day 2024 summary PDF "
            "agrees (LIVESTOCK events only under Tuesday 2 Jan)."
        ),
    ),
    date(2024, 1, 15): Citation(
        _svc("2024-01-14", "2024-01-16", "1734710019526"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2024-01-14","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2024-01-15","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2024-01-16","events":[{"tradingDate":"2024-01-16",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2024-01-16",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2024-01-16",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2024-01-16",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2024-01-16",'
            '"eventTime":"16:00","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2024-12-20. eventDate 2024-01-15 has an empty event list (no livestock "
            "session) while the adjacent weekday(s) in the same record carry the regular 08:00 "
            "preopen, 08:30 open and 13:05 close. HE (Lean Hogs) is not in the captured request "
            "and is taken to share LE's livestock hours, as the Livestock / LIVESTOCK rows of "
            "CME's 2019-2023 schedules state for both."
        ),
    ),
    date(2024, 2, 19): Citation(
        _svc("2024-02-18", "2024-02-20", "1720455278669"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2024-02-18","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2024-02-19","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2024-02-20","events":[{"tradingDate":"2024-02-20",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2024-02-20",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2024-02-20",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2024-02-20",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2024-02-20",'
            '"eventTime":"16:00","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2024-07-08. eventDate 2024-02-19 has an empty event list (no livestock "
            "session) while the adjacent weekday(s) in the same record carry the regular 08:00 "
            "preopen, 08:30 open and 13:05 close. HE (Lean Hogs) is not in the captured request "
            "and is taken to share LE's livestock hours, as the Livestock / LIVESTOCK rows of "
            "CME's 2019-2023 schedules state for both."
        ),
    ),
    date(2024, 3, 29): Citation(
        _svc("2024-03-28", "2024-03-30", "1720455278672"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2024-03-28","events":[{"tradingDate":"2024-03-28",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2024-03-28",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2024-03-28",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2024-03-28",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2024-03-28",'
            '"eventTime":"16:00","marketEventType":"closed"}]} ... '
            '{"groupCode":"LE","eventDate":"2024-03-29","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2024-03-30","events":[]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2024-07-08. eventDate 2024-03-29 has an empty event list (no livestock "
            "session) while the adjacent weekday(s) in the same record carry the regular 08:00 "
            "preopen, 08:30 open and 13:05 close. HE (Lean Hogs) is not in the captured request "
            "and is taken to share LE's livestock hours, as the Livestock / LIVESTOCK rows of "
            "CME's 2019-2023 schedules state for both."
        ),
    ),
    date(2024, 5, 27): Citation(
        _svc("2024-05-26", "2024-05-28", "1720455278675"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2024-05-26","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2024-05-27","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2024-05-28","events":[{"tradingDate":"2024-05-28",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2024-05-28",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2024-05-28",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2024-05-28",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2024-05-28",'
            '"eventTime":"16:00","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2024-07-08. eventDate 2024-05-27 has an empty event list (no livestock "
            "session) while the adjacent weekday(s) in the same record carry the regular 08:00 "
            "preopen, 08:30 open and 13:05 close. HE (Lean Hogs) is not in the captured request "
            "and is taken to share LE's livestock hours, as the Livestock / LIVESTOCK rows of "
            "CME's 2019-2023 schedules state for both."
        ),
    ),
    date(2024, 6, 19): Citation(
        _svc("2024-06-18", "2024-06-20", "1720455278677"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2024-06-18","events":[{"tradingDate":"2024-06-18",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2024-06-18",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2024-06-18",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2024-06-18",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2024-06-18",'
            '"eventTime":"16:00","marketEventType":"closed"}]} ... '
            '{"groupCode":"LE","eventDate":"2024-06-19","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2024-06-20","events":[{"tradingDate":"2024-06-20",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2024-06-20",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2024-06-20",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2024-06-20",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2024-06-20",'
            '"eventTime":"16:00","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2024-07-08. eventDate 2024-06-19 has an empty event list (no livestock "
            "session) while the adjacent weekday(s) in the same record carry the regular 08:00 "
            "preopen, 08:30 open and 13:05 close. HE (Lean Hogs) is not in the captured request "
            "and is taken to share LE's livestock hours, as the Livestock / LIVESTOCK rows of "
            "CME's 2019-2023 schedules state for both."
        ),
    ),
    date(2024, 7, 4): Citation(
        _svc("2024-07-03", "2024-07-05", "1720455278680"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2024-07-03","events":[{"tradingDate":"2024-07-03",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2024-07-03",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2024-07-03",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2024-07-03",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2024-07-03",'
            '"eventTime":"16:00","marketEventType":"closed"}]} ... '
            '{"groupCode":"LE","eventDate":"2024-07-04","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2024-07-05","events":[{"tradingDate":"2024-07-05",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2024-07-05",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2024-07-05",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2024-07-05",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2024-07-05",'
            '"eventTime":"16:00","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2024-07-08. eventDate 2024-07-04 has an empty event list (no livestock "
            "session) while the adjacent weekday(s) in the same record carry the regular 08:00 "
            "preopen, 08:30 open and 13:05 close. HE (Lean Hogs) is not in the captured request "
            "and is taken to share LE's livestock hours, as the Livestock / LIVESTOCK rows of "
            "CME's 2019-2023 schedules state for both."
        ),
    ),
    date(2024, 9, 2): Citation(
        _svc("2024-09-01", "2024-09-03", "1734710019534"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2024-09-01","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2024-09-02","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2024-09-03","events":[{"tradingDate":"2024-09-03",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2024-09-03",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2024-09-03",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2024-09-03",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2024-09-03",'
            '"eventTime":"16:00","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2024-12-20. eventDate 2024-09-02 has an empty event list (no livestock "
            "session) while the adjacent weekday(s) in the same record carry the regular 08:00 "
            "preopen, 08:30 open and 13:05 close. HE (Lean Hogs) is not in the captured request "
            "and is taken to share LE's livestock hours, as the Livestock / LIVESTOCK rows of "
            "CME's 2019-2023 schedules state for both."
        ),
    ),
    date(2024, 11, 28): Citation(
        _svc("2024-11-27", "2024-11-29", "1734710019535"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2024-11-27","events":[{"tradingDate":"2024-11-27",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2024-11-27",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2024-11-27",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2024-11-27",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2024-11-27",'
            '"eventTime":"16:00","marketEventType":"closed"}]} ... '
            '{"groupCode":"LE","eventDate":"2024-11-28","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2024-11-29","events":[{"tradingDate":"2024-11-29",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2024-11-29",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2024-11-29",'
            '"eventTime":"12:05","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2024-12-20. eventDate 2024-11-28 has an empty event list (no livestock "
            "session) while the adjacent weekday(s) in the same record carry the regular 08:00 "
            "preopen, 08:30 open and 13:05 close. HE (Lean Hogs) is not in the captured request "
            "and is taken to share LE's livestock hours, as the Livestock / LIVESTOCK rows of "
            "CME's 2019-2023 schedules state for both."
        ),
    ),
    date(2024, 11, 29): Citation(
        _svc("2024-11-27", "2024-11-29", "1734710019535"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2024-11-27","events":[{"tradingDate":"2024-11-27",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2024-11-27",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2024-11-27",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2024-11-27",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2024-11-27",'
            '"eventTime":"16:00","marketEventType":"closed"}]} ... '
            '{"groupCode":"LE","eventDate":"2024-11-28","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2024-11-29","events":[{"tradingDate":"2024-11-29",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2024-11-29",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2024-11-29",'
            '"eventTime":"12:05","marketEventType":"closed"}]}'
        ),
        _svc("2024-11-27", "2024-11-29", "1734710019535"),
        (
            '{"groupCode":"LE","eventDate":"2024-11-29","events":[{"tradingDate":"2024-11-29",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2024-11-29",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2024-11-29",'
            '"eventTime":"12:05","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2024-12-20. eventDate 2024-11-29 lists 08:00 preopen, 08:30 open and a 12:05 "
            "close (the regular close is 13:05). HE (Lean Hogs) is not in the captured request and "
            "is taken to share LE's livestock hours, as the Livestock / LIVESTOCK rows of CME's "
            "2019-2023 schedules state for both. Secondary corroboration: Insignia Futures (a "
            "broker) gives livestock the same 12:05 PM CT close."
        ),
    ),
    date(2024, 12, 24): Citation(
        _svc("2024-12-24", "2024-12-26", "1734710019537"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2024-12-24","events":[{"tradingDate":"2024-12-24",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2024-12-24",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2024-12-24",'
            '"eventTime":"12:15","marketEventType":"closed"}]} ... '
            '{"groupCode":"LE","eventDate":"2024-12-25","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2024-12-26","events":[{"tradingDate":"2024-12-26",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2024-12-26",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2024-12-26",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2024-12-26",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2024-12-26",'
            '"eventTime":"16:00","marketEventType":"closed"}]}'
        ),
        _svc("2024-12-24", "2024-12-26", "1734710019537"),
        (
            '{"groupCode":"LE","eventDate":"2024-12-24","events":[{"tradingDate":"2024-12-24",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2024-12-24",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2024-12-24",'
            '"eventTime":"12:15","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2024-12-20, 4 days before the date (CME's published plan). eventDate "
            "2024-12-24 lists 08:00 preopen, 08:30 open and a 12:15 close (the regular close is "
            "13:05). HE (Lean Hogs) is not in the captured request and is taken to share LE's "
            "livestock hours, as the Livestock / LIVESTOCK rows of CME's 2019-2023 schedules state "
            "for both. CME states 12:15 CT for the livestock close on Christmas Eve 2024 and 2025 "
            "(12:05 CT on the day after Thanksgiving in the same years, and 12:05 CT for Christmas "
            "Eve 2026 in the capture of 2026-08-30); CME's Christmas settlement notice gives "
            "agricultural products a 12:00:00 CT settlement that day. Insignia Futures (a broker) "
            "also gives livestock 12:15 PM CT for Christmas Eve 2024 (grains 12:05 PM CT). The "
            "12:15 CT value is encoded as CME states it; the bar check should confirm it."
        ),
    ),
    date(2024, 12, 25): Citation(
        _svc("2024-12-24", "2024-12-26", "1734710019537"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2024-12-24","events":[{"tradingDate":"2024-12-24",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2024-12-24",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2024-12-24",'
            '"eventTime":"12:15","marketEventType":"closed"}]} ... '
            '{"groupCode":"LE","eventDate":"2024-12-25","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2024-12-26","events":[{"tradingDate":"2024-12-26",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2024-12-26",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2024-12-26",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2024-12-26",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2024-12-26",'
            '"eventTime":"16:00","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2024-12-20, 5 days before the date (CME's published plan). eventDate "
            "2024-12-25 has an empty event list (no livestock session) while the adjacent "
            "weekday(s) in the same record carry the regular 08:00 preopen, 08:30 open and 13:05 "
            "close. HE (Lean Hogs) is not in the captured request and is taken to share LE's "
            "livestock hours, as the Livestock / LIVESTOCK rows of CME's 2019-2023 schedules state "
            "for both."
        ),
    ),
    date(2025, 1, 1): Citation(
        _svc("2024-12-31", "2025-01-02", "1734710019538"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2024-12-31","events":[{"tradingDate":"2024-12-31",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2024-12-31",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2024-12-31",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2024-12-31",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2024-12-31",'
            '"eventTime":"16:00","marketEventType":"closed"}]} ... '
            '{"groupCode":"LE","eventDate":"2025-01-01","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2025-01-02","events":[{"tradingDate":"2025-01-02",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2025-01-02",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2025-01-02",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2025-01-02",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2025-01-02",'
            '"eventTime":"16:00","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2024-12-20, 12 days before the date (CME's published plan). eventDate "
            "2025-01-01 has an empty event list (no livestock session) while the adjacent "
            "weekday(s) in the same record carry the regular 08:00 preopen, 08:30 open and 13:05 "
            "close. HE (Lean Hogs) is not in the captured request and is taken to share LE's "
            "livestock hours, as the Livestock / LIVESTOCK rows of CME's 2019-2023 schedules state "
            "for both."
        ),
    ),
    date(2025, 1, 9): Citation(
        _TH + "day-of-mourning-january-9-2024.pdf",
        (
            "U.S. National Day of Mourning Trading Schedule for Globex, BrokerTec, EBS and Trading "
            "Floor ... PRODUCT NAME JANUARY 9, 2025 TRADING FLOOR CLEARPORT ... CME AND CBOT AGS* "
            "EARLY CLOSE – 12:15 PM CT N/A NORMAL HOURS ... *There is no change for products that "
            "have an earlier close than 12 PM CT"
        ),
        _TH + "day-of-mourning-january-9-2024.pdf",
        "CME AND CBOT AGS* EARLY CLOSE – 12:15 PM CT N/A NORMAL HOURS",
        note=(
            "Unscheduled closure day (President Carter's National Day of Mourning). CME's trading "
            "schedule (file name says 2024, content 9 January 2025; Wayback capture 2025-02-18): "
            "'CME AND CBOT AGS' close early at 12:15 PM CT on Globex, and the footnote exempts "
            "only products whose close is earlier than 12 PM CT. Livestock (CME ags, regular close "
            "13:05 CT) therefore closed at 12:15 CT. Equities closed at 08:30 CT; livestock is not "
            "named individually."
        ),
    ),
    date(2025, 1, 20): Citation(
        _svc("2025-01-19", "2025-01-21", "1734710019539"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2025-01-19","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2025-01-20","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2025-01-21","events":[{"tradingDate":"2025-01-21",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2025-01-21",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2025-01-21",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2025-01-21",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2025-01-21",'
            '"eventTime":"16:00","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2024-12-20, 31 days before the date (CME's published plan). eventDate "
            "2025-01-20 has an empty event list (no livestock session) while the adjacent "
            "weekday(s) in the same record carry the regular 08:00 preopen, 08:30 open and 13:05 "
            "close. HE (Lean Hogs) is not in the captured request and is taken to share LE's "
            "livestock hours, as the Livestock / LIVESTOCK rows of CME's 2019-2023 schedules state "
            "for both."
        ),
    ),
    date(2025, 2, 17): Citation(
        _svc("2025-02-16", "2025-02-18", "1734710019540"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2025-02-16","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2025-02-17","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2025-02-18","events":[{"tradingDate":"2025-02-18",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2025-02-18",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2025-02-18",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2025-02-18",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2025-02-18",'
            '"eventTime":"16:00","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2024-12-20, 59 days before the date (CME's published plan). eventDate "
            "2025-02-17 has an empty event list (no livestock session) while the adjacent "
            "weekday(s) in the same record carry the regular 08:00 preopen, 08:30 open and 13:05 "
            "close. HE (Lean Hogs) is not in the captured request and is taken to share LE's "
            "livestock hours, as the Livestock / LIVESTOCK rows of CME's 2019-2023 schedules state "
            "for both."
        ),
    ),
    date(2025, 4, 18): Citation(
        _svc("2025-04-17", "2025-04-19", "1734710019542"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2025-04-17","events":[{"tradingDate":"2025-04-17",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2025-04-17",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2025-04-17",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2025-04-17",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2025-04-17",'
            '"eventTime":"16:00","marketEventType":"closed"}]} ... '
            '{"groupCode":"LE","eventDate":"2025-04-18","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2025-04-19","events":[]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2024-12-20, 119 days before the date (CME's published plan). eventDate "
            "2025-04-18 has an empty event list (no livestock session) while the adjacent "
            "weekday(s) in the same record carry the regular 08:00 preopen, 08:30 open and 13:05 "
            "close. HE (Lean Hogs) is not in the captured request and is taken to share LE's "
            "livestock hours, as the Livestock / LIVESTOCK rows of CME's 2019-2023 schedules state "
            "for both."
        ),
    ),
    date(2025, 5, 26): Citation(
        _svc("2025-05-25", "2025-05-27", "1734710019543"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2025-05-25","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2025-05-26","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2025-05-27","events":[{"tradingDate":"2025-05-27",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2025-05-27",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2025-05-27",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2025-05-27",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2025-05-27",'
            '"eventTime":"16:00","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2024-12-20, 157 days before the date (CME's published plan). eventDate "
            "2025-05-26 has an empty event list (no livestock session) while the adjacent "
            "weekday(s) in the same record carry the regular 08:00 preopen, 08:30 open and 13:05 "
            "close. HE (Lean Hogs) is not in the captured request and is taken to share LE's "
            "livestock hours, as the Livestock / LIVESTOCK rows of CME's 2019-2023 schedules state "
            "for both."
        ),
    ),
    date(2025, 6, 19): Citation(
        _svc("2025-06-18", "2025-06-20", "1734710019544"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2025-06-18","events":[{"tradingDate":"2025-06-18",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2025-06-18",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2025-06-18",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2025-06-18",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2025-06-18",'
            '"eventTime":"16:00","marketEventType":"closed"}]} ... '
            '{"groupCode":"LE","eventDate":"2025-06-19","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2025-06-20","events":[{"tradingDate":"2025-06-20",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2025-06-20",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2025-06-20",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2025-06-20",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2025-06-20",'
            '"eventTime":"16:00","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2024-12-20, 181 days before the date (CME's published plan). eventDate "
            "2025-06-19 has an empty event list (no livestock session) while the adjacent "
            "weekday(s) in the same record carry the regular 08:00 preopen, 08:30 open and 13:05 "
            "close. HE (Lean Hogs) is not in the captured request and is taken to share LE's "
            "livestock hours, as the Livestock / LIVESTOCK rows of CME's 2019-2023 schedules state "
            "for both."
        ),
    ),
    date(2025, 7, 4): Citation(
        _svc("2025-07-03", "2025-07-05", "1734710019545"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2025-07-03","events":[{"tradingDate":"2025-07-03",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2025-07-03",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2025-07-03",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2025-07-03",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2025-07-03",'
            '"eventTime":"16:00","marketEventType":"closed"}]} ... '
            '{"groupCode":"LE","eventDate":"2025-07-04","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2025-07-05","events":[]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2024-12-20, 196 days before the date (CME's published plan). eventDate "
            "2025-07-04 has an empty event list (no livestock session) while the adjacent "
            "weekday(s) in the same record carry the regular 08:00 preopen, 08:30 open and 13:05 "
            "close. HE (Lean Hogs) is not in the captured request and is taken to share LE's "
            "livestock hours, as the Livestock / LIVESTOCK rows of CME's 2019-2023 schedules state "
            "for both."
        ),
    ),
    date(2025, 9, 1): Citation(
        _svc("2025-08-31", "2025-09-02", "1734710019546"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2025-08-31","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2025-09-01","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2025-09-02","events":[{"tradingDate":"2025-09-02",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2025-09-02",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2025-09-02",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2025-09-02",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2025-09-02",'
            '"eventTime":"16:00","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2024-12-20, 255 days before the date (CME's published plan). eventDate "
            "2025-09-01 has an empty event list (no livestock session) while the adjacent "
            "weekday(s) in the same record carry the regular 08:00 preopen, 08:30 open and 13:05 "
            "close. HE (Lean Hogs) is not in the captured request and is taken to share LE's "
            "livestock hours, as the Livestock / LIVESTOCK rows of CME's 2019-2023 schedules state "
            "for both."
        ),
    ),
    date(2025, 11, 27): Citation(
        _svc("2025-11-26", "2025-11-28", "1769649703060"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2025-11-26","events":[{"tradingDate":"2025-11-26",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2025-11-26",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2025-11-26",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2025-11-26",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2025-11-26",'
            '"eventTime":"16:00","marketEventType":"closed"}]} ... '
            '{"groupCode":"LE","eventDate":"2025-11-27","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2025-11-28",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2025-11-28",'
            '"eventTime":"12:05","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2026-01-29. eventDate 2025-11-27 has an empty event list (no livestock "
            "session) while the adjacent weekday(s) in the same record carry the regular 08:00 "
            "preopen, 08:30 open and 13:05 close. HE (Lean Hogs) is not in the captured request "
            "and is taken to share LE's livestock hours, as the Livestock / LIVESTOCK rows of "
            "CME's 2019-2023 schedules state for both."
        ),
    ),
    date(2025, 11, 28): Citation(
        _svc("2025-11-26", "2025-11-28", "1769649703060"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2025-11-26","events":[{"tradingDate":"2025-11-26",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2025-11-26",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2025-11-26",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2025-11-26",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2025-11-26",'
            '"eventTime":"16:00","marketEventType":"closed"}]} ... '
            '{"groupCode":"LE","eventDate":"2025-11-27","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2025-11-28",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2025-11-28",'
            '"eventTime":"12:05","marketEventType":"closed"}]}'
        ),
        _svc("2025-11-26", "2025-11-28", "1769649703060"),
        (
            '{"groupCode":"LE","eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2025-11-28",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2025-11-28",'
            '"eventTime":"12:05","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2026-01-29. eventDate 2025-11-28 lists 08:00 preopen, 08:30 open and a 12:05 "
            "close (the regular close is 13:05). HE (Lean Hogs) is not in the captured request and "
            "is taken to share LE's livestock hours, as the Livestock / LIVESTOCK rows of CME's "
            "2019-2023 schedules state for both. Globex outage: CME halted its markets on "
            "2025-11-27 after a data-center cooling failure and reopened on 2025-11-28 on a "
            "delayed basis (the energy and rates modules record a 07:30 CT open). This capture was "
            "taken after the outage and keeps LE's regular 08:00 preopen and 08:30 open, so no "
            "late open is recorded for livestock; the bar check should confirm the 08:30 open."
        ),
    ),
    date(2025, 12, 24): Citation(
        _svc("2025-12-24", "2025-12-26", "1769649703064"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2025-12-24","events":[{"tradingDate":"2025-12-24",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2025-12-24",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2025-12-24",'
            '"eventTime":"12:15","marketEventType":"closed"}]} ... '
            '{"groupCode":"LE","eventDate":"2025-12-25","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2025-12-26","events":[{"tradingDate":"2025-12-26",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2025-12-26",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2025-12-26",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2025-12-26",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2025-12-26",'
            '"eventTime":"16:00","marketEventType":"closed"}]}'
        ),
        _svc("2025-12-24", "2025-12-26", "1769649703064"),
        (
            '{"groupCode":"LE","eventDate":"2025-12-24","events":[{"tradingDate":"2025-12-24",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2025-12-24",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2025-12-24",'
            '"eventTime":"12:15","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2026-01-29. eventDate 2025-12-24 lists 08:00 preopen, 08:30 open and a 12:15 "
            "close (the regular close is 13:05). HE (Lean Hogs) is not in the captured request and "
            "is taken to share LE's livestock hours, as the Livestock / LIVESTOCK rows of CME's "
            "2019-2023 schedules state for both. CME states 12:15 CT for the livestock close on "
            "Christmas Eve 2024 and 2025 (12:05 CT on the day after Thanksgiving in the same "
            "years, and 12:05 CT for Christmas Eve 2026 in the capture of 2026-08-30); CME's "
            "Christmas settlement notice gives agricultural products a 12:00:00 CT settlement that "
            "day. Insignia Futures (a broker) also gives livestock 12:15 PM CT for Christmas Eve "
            "2024 (grains 12:05 PM CT). The 12:15 CT value is encoded as CME states it; the bar "
            "check should confirm it."
        ),
    ),
    date(2025, 12, 25): Citation(
        _svc("2025-12-24", "2025-12-26", "1769649703064"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2025-12-24","events":[{"tradingDate":"2025-12-24",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2025-12-24",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2025-12-24",'
            '"eventTime":"12:15","marketEventType":"closed"}]} ... '
            '{"groupCode":"LE","eventDate":"2025-12-25","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2025-12-26","events":[{"tradingDate":"2025-12-26",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2025-12-26",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2025-12-26",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2025-12-26",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2025-12-26",'
            '"eventTime":"16:00","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2026-01-29. eventDate 2025-12-25 has an empty event list (no livestock "
            "session) while the adjacent weekday(s) in the same record carry the regular 08:00 "
            "preopen, 08:30 open and 13:05 close. HE (Lean Hogs) is not in the captured request "
            "and is taken to share LE's livestock hours, as the Livestock / LIVESTOCK rows of "
            "CME's 2019-2023 schedules state for both."
        ),
    ),
    date(2026, 1, 1): Citation(
        _svc("2025-12-31", "2026-01-02", "1769649703066"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2025-12-31","events":[{"tradingDate":"2025-12-31",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2025-12-31",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2025-12-31",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2025-12-31",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2025-12-31",'
            '"eventTime":"16:00","marketEventType":"closed"}]} ... '
            '{"groupCode":"LE","eventDate":"2026-01-01","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2026-01-02","events":[{"tradingDate":"2026-01-02",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2026-01-02",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2026-01-02",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2026-01-02",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2026-01-02",'
            '"eventTime":"16:00","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2026-01-29. eventDate 2026-01-01 has an empty event list (no livestock "
            "session) while the adjacent weekday(s) in the same record carry the regular 08:00 "
            "preopen, 08:30 open and 13:05 close. HE (Lean Hogs) is not in the captured request "
            "and is taken to share LE's livestock hours, as the Livestock / LIVESTOCK rows of "
            "CME's 2019-2023 schedules state for both."
        ),
    ),
    date(2026, 1, 19): Citation(
        _svc("2026-01-18", "2026-01-20", "1769649703068"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2026-01-18","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2026-01-19","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2026-01-20","events":[{"tradingDate":"2026-01-20",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2026-01-20",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2026-01-20",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2026-01-20",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2026-01-20",'
            '"eventTime":"16:00","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2026-01-29. eventDate 2026-01-19 has an empty event list (no livestock "
            "session) while the adjacent weekday(s) in the same record carry the regular 08:00 "
            "preopen, 08:30 open and 13:05 close. HE (Lean Hogs) is not in the captured request "
            "and is taken to share LE's livestock hours, as the Livestock / LIVESTOCK rows of "
            "CME's 2019-2023 schedules state for both."
        ),
    ),
    date(2026, 2, 16): Citation(
        _svc("2026-02-15", "2026-02-17", "1743113432015"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2026-02-15","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2026-02-16","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2026-02-17","events":[{"tradingDate":"2026-02-17",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2026-02-17",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2026-02-17",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2026-02-17",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2026-02-17",'
            '"eventTime":"16:00","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2026-06-10. eventDate 2026-02-16 has an empty event list (no livestock "
            "session) while the adjacent weekday(s) in the same record carry the regular 08:00 "
            "preopen, 08:30 open and 13:05 close. HE (Lean Hogs) is not in the captured request "
            "and is taken to share LE's livestock hours, as the Livestock / LIVESTOCK rows of "
            "CME's 2019-2023 schedules state for both."
        ),
    ),
    date(2026, 4, 3): Citation(
        _svc("2026-04-01", "2026-04-03", "1743113432016"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2026-04-01","events":[{"tradingDate":"2026-04-01",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2026-04-01",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2026-04-01",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2026-04-01",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2026-04-01",'
            '"eventTime":"16:00","marketEventType":"closed"}]} ... '
            '{"groupCode":"LE","eventDate":"2026-04-02","events":[{"tradingDate":"2026-04-02",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2026-04-02",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2026-04-02",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2026-04-02",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2026-04-02",'
            '"eventTime":"16:00","marketEventType":"closed"}]} ... '
            '{"groupCode":"LE","eventDate":"2026-04-03","events":[]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2026-06-10. eventDate 2026-04-03 has an empty event list (no livestock "
            "session) while the adjacent weekday(s) in the same record carry the regular 08:00 "
            "preopen, 08:30 open and 13:05 close. HE (Lean Hogs) is not in the captured request "
            "and is taken to share LE's livestock hours, as the Livestock / LIVESTOCK rows of "
            "CME's 2019-2023 schedules state for both. Jobs-report Good Friday: equities traded an "
            "abbreviated session; livestock was closed."
        ),
    ),
    date(2026, 5, 25): Citation(
        _svc("2026-05-24", "2026-05-26", "1749141516014"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2026-05-24","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2026-05-25","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2026-05-26","events":[{"tradingDate":"2026-05-26",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2026-05-26",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2026-05-26",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2026-05-26",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2026-05-26",'
            '"eventTime":"16:00","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2026-06-19. eventDate 2026-05-25 has an empty event list (no livestock "
            "session) while the adjacent weekday(s) in the same record carry the regular 08:00 "
            "preopen, 08:30 open and 13:05 close. HE (Lean Hogs) is not in the captured request "
            "and is taken to share LE's livestock hours, as the Livestock / LIVESTOCK rows of "
            "CME's 2019-2023 schedules state for both."
        ),
    ),
    date(2026, 6, 19): Citation(
        _svc("2026-06-18", "2026-06-20", "1784720540600"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2026-06-18","events":[{"tradingDate":"2026-06-18",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2026-06-18",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2026-06-18",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2026-06-18",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2026-06-18",'
            '"eventTime":"16:00","marketEventType":"closed"}]} ... '
            '{"groupCode":"LE","eventDate":"2026-06-19","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2026-06-20","events":[]}'
        ),
        note=(
            "CME's trading-hours-by-product service record (the data behind "
            "cmegroup.com/trading-hours.html) for product 22, LE Live Cattle Futures, Wayback "
            "capture 2026-07-22. eventDate 2026-06-19 has an empty event list (no livestock "
            "session) while the adjacent weekday(s) in the same record carry the regular 08:00 "
            "preopen, 08:30 open and 13:05 close. HE (Lean Hogs) is not in the captured request "
            "and is taken to share LE's livestock hours, as the Livestock / LIVESTOCK rows of "
            "CME's 2019-2023 schedules state for both."
        ),
    ),
}

# CME-stated regular livestock days near holidays, kept so the absence of an entry is a recorded
# finding, not an oversight.
NO_ENTRY_FINDINGS: dict[date, Citation] = {
    date(2019, 12, 31): Citation(
        _Z19,
        (
            "CME Group Globex New Years Holiday Schedule: December 31, 2019 - January 2, 2020 ... "
            "Trade Date|Tuesday,Dec 31|Globex Closed|Thursday, January 2|Thursday, January "
            "2|Thursday, January 2 ... Calendar Trade|Tuesday, Dec 31|Wednessday, Jan 1 "
            "|Wednesday, Jan 1|Thursday, Jan 2|Thursday, Jan 2 ... Livestock|Regular close|Closed "
            "for New Year's|Closed for New Year's|Pre-open 6:00CT /12:00 UTC Open 8:30 CT /14:30 "
            "UTC|Regular Open and Close"
        ),
        note=(
            "NORMAL livestock session stated by CME: no entry. New Year's Eve 2019: Livestock "
            "'Regular close' (compact, 2019 zip); CME's New Year's Eve 2019 settlement notice "
            "moves only interest-rate and FX settlements."
        ),
    ),
    date(2020, 12, 31): Citation(
        _Z20,
        (
            "CME Group Globex New Years Holiday Schedule: December 31, 2020 - January 4, 2021 ... "
            "Trade Date|Thursday,Dec 31|Globex Closed|Monday, January 4|Monday, January 4|Monday, "
            "January 4 ... Calendar Trade|Thursday,Dec 31|Friday,Jan 1|Sunday,Jan 3|Monday, Jan "
            "4|Monday, Jan 4 ... Livestock|Regular close|Closed for New Year's|Closed for New "
            "Year's|Pre-open 8:00CT /14:00 UTC Open 8:30 CT /14:30 UTC|Regular Open and Close"
        ),
        note=(
            "NORMAL livestock session stated by CME: no entry. New Year's Eve 2020: Livestock "
            "'Regular close' (compact, 2020 zip)."
        ),
    ),
    date(2021, 4, 1): Citation(
        _Z21,
        (
            "CME Group Globex Good Friday Holiday Schedule: April 1,2021 to April 5, 2021 ... "
            "Trade Date|Thursday,April 1|Friday, April 2|Friday, April 2|Monday, April 5 ... "
            "Calendar Date|Thursday April 1|Thursday,April 1|Friday April 2|Sunday, April 4 into "
            "Monday, April 5 ... Product|CLOSE|OPEN|CLOSED|OPEN ... Livestock|Regular per "
            "Product|Closed for Good Friday|Closed for Good Friday|Monday @ 0830 CT/ 1330 UTC"
        ),
        note=(
            "NORMAL livestock session stated by CME: no entry. Thursday before Good Friday 2021: "
            "Livestock 'Regular per Product'."
        ),
    ),
    date(2021, 7, 2): Citation(
        _Z21,
        (
            "CME Group Globex Independence Day Holiday Schedule: July 2, 2021 to July 6, 2021 ... "
            "Trade Date|Friday, July 2|Tuesday, July 6|Tuesday, July 6|Tuesday, July 6 ... "
            "Calendar Date|Friday July 2|Sunday July 4|Monday July 5|Monday July 5 ... "
            "Product|CLOSE|OPEN|HALT|OPEN ... Livestock|Regular Per Product|Markets Closed|Markets "
            "Closed|Tuesday July 6 Regular @ 0830 / 1330 UTC"
        ),
        note=(
            "NORMAL livestock session stated by CME: no entry. Friday before the observed "
            "Independence Day 2021: Livestock 'Regular Per Product' (no early close, unlike "
            "2019-07-03 and 2020-07-02)."
        ),
    ),
    date(2021, 12, 23): Citation(
        _Z21,
        (
            "CME Group Globex Christmas Holiday Schedule: December 23, 2021 - December 27, 2021 "
            "... Trade Date|Thursday,December 23|Globex Closed|Monday December 27|Monday December "
            "27 ... Products|Thursday, Dec 23|Friday,Dec 24|Sunday 26|Monday,Dec 27 ... "
            "Livestock|Regular per Product|Closed for Christmas|Closed for Christmas|Pre-open "
            "8:00CT /14:00 UTC Open 8:30 CT /14:30 UTC"
        ),
        note=(
            "NORMAL livestock session stated by CME: no entry. Thursday before the observed "
            "Christmas 2021: Livestock 'Regular per Product'. CME's settlement notice captured "
            "2021-12-22 agrees ('Agricultural Products (Grains, Livestock, Dairy, Commodity Index) "
            "Normal Settlement Times'); its January 2021 capture had listed a 12:00:00 CT "
            "settlement, a preliminary version superseded before the day."
        ),
    ),
    date(2021, 12, 31): Citation(
        _Z21,
        (
            "CME Group Globex New Years Holiday Schedule: December 30, 2021 - January 3, 2022 ... "
            "Trade Date|Thursday,Dec 30|Thursday,Dec 30|Friday,Dec 31|Friday,Dec 31|Monday, "
            "January 3|Monday, January 3 ... Calendar Trade|Thursday,Dec 30|Thursday,Dec "
            "30|Friday,Dec 31|Friday,Dec 31|Sunday,Jan 2|Monday, Jan 3 ... Livestock|Regular @ "
            "1305 CT/1905 UTC||Pre-open 8:00CT /14:00 UTC Open 8:30CT /14:30 UTC|Regular @ 1305 "
            "CT/1905 UTC||Pre-open 8:00CT /14:00 UTC Open 8:30CT /14:30 UTC"
        ),
        note=(
            "NORMAL livestock session stated by CME: no entry. New Year's Eve 2021 (New Year's Day "
            "2022 fell on a Saturday and was not observed): Livestock opens 08:30 and closes "
            "'Regular @ 1305 CT' on Friday Dec 31."
        ),
    ),
    date(2022, 1, 3): Citation(
        _Z21,
        (
            "CME Group Globex New Years Holiday Schedule: December 30, 2021 - January 3, 2022 ... "
            "Trade Date|Thursday,Dec 30|Thursday,Dec 30|Friday,Dec 31|Friday,Dec 31|Monday, "
            "January 3|Monday, January 3 ... Calendar Trade|Thursday,Dec 30|Thursday,Dec "
            "30|Friday,Dec 31|Friday,Dec 31|Sunday,Jan 2|Monday, Jan 3 ... Livestock|Regular @ "
            "1305 CT/1905 UTC||Pre-open 8:00CT /14:00 UTC Open 8:30CT /14:30 UTC|Regular @ 1305 "
            "CT/1905 UTC||Pre-open 8:00CT /14:00 UTC Open 8:30CT /14:30 UTC"
        ),
        note=(
            "NORMAL livestock session stated by CME: no entry. Monday January 3, 2022: Livestock "
            "'Pre-open 8:00CT ... Open 8:30CT' for trade date Monday, January 3; no holiday "
            "observed."
        ),
    ),
    date(2022, 7, 1): Citation(
        _HC + "2022-independence-day-holiday-schedule-compact.xls",
        (
            "CME Group Globex Independence Day Holiday Schedule: July 1, 2022 to July 5, 2022 ... "
            "Trade Date|Friday, July 1|Tuesday, July 5|Tuesday, July 5|Tuesday, July 5 ... "
            "Calendar Date|Friday July 1|Sunday July 3|Monday July 4|Monday July 4 ... "
            "Product|CLOSE|OPEN|HALT|OPEN ... Livestock|Regular Per Product|Markets Closed|Markets "
            "Closed|Tuesday July 5 Regular @ 0830 / 1330 UTC"
        ),
        note=(
            "NORMAL livestock session stated by CME: no entry. Friday before Independence Day "
            "2022: Livestock 'Regular Per Product'."
        ),
    ),
    date(2022, 12, 23): Citation(
        _HC + "2022-christmas-holiday-schedule.xls",
        (
            "CME Group Globex Christmas Holiday Schedule: December 23, 2022 - December 27, 2022 "
            "... Livestock|13:05 (*PCP 14:30-16:00)||||||||Globex Closed|Globex Closed|Globex "
            "Closed|Globex Closed|Globex Closed|Globex Closed|Globex Closed|Globex Closed|Globex "
            "Closed|Globex Closed|||||||08:00|08:30|13:05|14:30-16:00"
        ),
        note=(
            "NORMAL livestock session stated by CME: no entry. Friday before the observed "
            "Christmas 2022: Livestock '13:05 (*PCP 14:30-16:00)' under Calendar Date 'Friday, "
            "December 23' (full schedule 'Updated 6/29/2022', the only capture). CME's Christmas "
            "2022 settlement notice (captured 2022-01-28) moves only interest-rate settlements "
            "that day."
        ),
    ),
    date(2022, 12, 30): Citation(
        _HC + "2023-new-years-holiday-schedule-compact.xls",
        (
            "CME Group Globex New Years Holiday Schedule: December 30, 2022 - January 3, 2023 ... "
            "Trade Date|Friday,Dec 30|Sunday, January 1 and Monday, January 2|Sunday, January 1 "
            "and Monday, January 2| Tuesday, January 3 ... Calendar Trade|Friday,Dec 30|Sunday, "
            "Jan 1 and Monday, Jan 2|Monday,Jan 2|Tuesday, Jan 3|Tuesday, Jan 3 ... "
            "Livestock|Regular @ 1305 CT/1905 UTC|Globex Closed||Pre-open 8:00CT /14:00 UTC Open "
            "8:30CT /14:30 UTC|Regular @ 1305 CT/1905 UTC"
        ),
        note=(
            "NORMAL livestock session stated by CME: no entry. Friday before the observed New Year "
            "2023: Livestock 'Regular @ 1305 CT/1905 UTC' (compact, captured 2022-07-04)."
        ),
    ),
    date(2023, 4, 6): Citation(
        "https://www.cmegroup.com/files/good-friday.pdf",
        (
            "PRODUCT NAME THURSDAY, 6 APR 2023 FRIDAY, 7 APR 2023 ... TRADE DATE: THURS 6 APR "
            "08:00 (PREOPEN) LIVESTOCK 08:30 (OPEN) 13:05 (CLOSED) 14:30 (PCP) 16:00 (CLOSED)"
        ),
        note=(
            "NORMAL livestock session stated by CME: no entry. Thursday before Good Friday 2023: "
            "LIVESTOCK 08:30 open, 13:05 close."
        ),
    ),
    date(2023, 7, 3): Citation(
        _TH + "4th-of-july-2023.pdf",
        (
            "PRODUCT NAME MONDAY, 3 JULY 2023 TUESDAY, 4 JULY 2023 WEDNESDAY, 5 JULY 2023 ... "
            "TRADE DATE: MON 3 JULY TRADE DATE: WED 5 JULY 08:00 (PREOPEN) 08:00 (PREOPEN) 08:30 "
            "(OPEN) 08:30 (OPEN) LIVESTOCK 13:05 (CLOSED) 13:05 (CLOSED)"
        ),
        note=(
            "NORMAL livestock session stated by CME: no entry. Monday July 3, 2023: LIVESTOCK "
            "08:30 open, 13:05 close (the equity and interest-rate groups closed early that day)."
        ),
    ),
    date(2023, 12, 22): Citation(
        _HC + "christmas-holiday-settlement-times-2023.pdf",
        (
            "Christmas Day Holiday 12/25/2023 Settlement Times Friday, December 22, 2023 Interest "
            "Rate Products 12:00:00 CT All other products will settle at their normal times"
        ),
        note=(
            "NORMAL livestock session stated by CME: no entry. Friday before Christmas 2023: CME's "
            "settlement notice (captured 2023-02-03) moves only interest-rate settlements; "
            "livestock settles at its normal 13:00 CT. This is a settlement statement, not a "
            "Globex hours statement; no CME Globex schedule for 2023-12-22 was retrievable."
        ),
    ),
    date(2023, 12, 29): Citation(
        _HC + "new-years-eve-holiday-settlement-times-2024.pdf",
        (
            "New Year’s Eve Holiday 12/29/2023 Settlement Times Friday, December 29, 2023 CME "
            "Group Interest Rate Products ... All other products will settle at their normal times"
        ),
        note=(
            "NORMAL livestock session stated by CME: no entry. Friday before New Year's Day 2024: "
            "CME's settlement notice (captured 2023-02-03) moves only interest-rate settlements. A "
            "settlement statement, not a Globex hours statement."
        ),
    ),
    date(2024, 7, 3): Citation(
        _svc("2024-07-03", "2024-07-05", "1720455278680"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2024-07-03","events":[{"tradingDate":"2024-07-03",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2024-07-03",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2024-07-03",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2024-07-03",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2024-07-03",'
            '"eventTime":"16:00","marketEventType":"closed"}]} ... '
            '{"groupCode":"LE","eventDate":"2024-07-04","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2024-07-05","events":[{"tradingDate":"2024-07-05",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2024-07-05",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2024-07-05",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2024-07-05",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2024-07-05",'
            '"eventTime":"16:00","marketEventType":"closed"}]}'
        ),
        note=(
            "NORMAL livestock session stated by CME: no entry. Wednesday before Independence Day "
            "2024: LE 08:30 open, 13:05 close (service record captured 2024-07-08)."
        ),
    ),
    date(2024, 12, 31): Citation(
        _svc("2024-12-31", "2025-01-02", "1734710019538"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2024-12-31","events":[{"tradingDate":"2024-12-31",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2024-12-31",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2024-12-31",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2024-12-31",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2024-12-31",'
            '"eventTime":"16:00","marketEventType":"closed"}]} ... '
            '{"groupCode":"LE","eventDate":"2025-01-01","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2025-01-02","events":[{"tradingDate":"2025-01-02",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2025-01-02",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2025-01-02",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2025-01-02",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2025-01-02",'
            '"eventTime":"16:00","marketEventType":"closed"}]}'
        ),
        note=(
            "NORMAL livestock session stated by CME: no entry. New Year's Eve 2024: LE 08:30 open, "
            "13:05 close (service record captured 2024-12-20)."
        ),
    ),
    date(2025, 7, 3): Citation(
        _svc("2025-07-03", "2025-07-05", "1734710019545"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2025-07-03","events":[{"tradingDate":"2025-07-03",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2025-07-03",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2025-07-03",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2025-07-03",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2025-07-03",'
            '"eventTime":"16:00","marketEventType":"closed"}]} ... '
            '{"groupCode":"LE","eventDate":"2025-07-04","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2025-07-05","events":[]}'
        ),
        note=(
            "NORMAL livestock session stated by CME: no entry. Thursday before Independence Day "
            "2025: LE 08:30 open, 13:05 close (service record captured 2024-12-20, CME's plan)."
        ),
    ),
    date(2025, 12, 31): Citation(
        _svc("2025-12-31", "2026-01-02", "1769649703066"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2025-12-31","events":[{"tradingDate":"2025-12-31",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2025-12-31",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2025-12-31",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2025-12-31",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2025-12-31",'
            '"eventTime":"16:00","marketEventType":"closed"}]} ... '
            '{"groupCode":"LE","eventDate":"2026-01-01","events":[]} ... '
            '{"groupCode":"LE","eventDate":"2026-01-02","events":[{"tradingDate":"2026-01-02",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2026-01-02",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2026-01-02",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2026-01-02",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2026-01-02",'
            '"eventTime":"16:00","marketEventType":"closed"}]}'
        ),
        note=(
            "NORMAL livestock session stated by CME: no entry. New Year's Eve 2025: LE 08:30 open, "
            "13:05 close (service record captured 2026-01-29)."
        ),
    ),
    date(2026, 4, 2): Citation(
        _svc("2026-04-01", "2026-04-03", "1743113432016"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2026-04-01","events":[{"tradingDate":"2026-04-01",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2026-04-01",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2026-04-01",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2026-04-01",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2026-04-01",'
            '"eventTime":"16:00","marketEventType":"closed"}]} ... '
            '{"groupCode":"LE","eventDate":"2026-04-02","events":[{"tradingDate":"2026-04-02",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2026-04-02",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2026-04-02",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2026-04-02",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2026-04-02",'
            '"eventTime":"16:00","marketEventType":"closed"}]} ... '
            '{"groupCode":"LE","eventDate":"2026-04-03","events":[]}'
        ),
        note=(
            "NORMAL livestock session stated by CME: no entry. Thursday before Good Friday 2026: "
            "LE 08:30 open, 13:05 close."
        ),
    ),
}

SESSION_SOURCES: dict[str, Citation] = {
    "cme_livestock_hours": Citation(
        _SPEC_OLD + "live-cattle_contract_specifications.html",
        "Trading Hours CME Globex: Monday - Friday: 8:30 a.m. - 1:05 p.m. CT",
        _svc("2026-06-18", "2026-06-20", "1784720540600"),
        (
            '"globex":"LE","prodGroup":"LE","name":"Live Cattle Futures","id":22 ... '
            '{"groupCode":"LE","eventDate":"2026-06-18","events":[{"tradingDate":"2026-06-18",'
            '"eventTime":"08:00","marketEventType":"preopen"},{"tradingDate":"2026-06-18",'
            '"eventTime":"08:30","marketEventType":"open"},{"tradingDate":"2026-06-18",'
            '"eventTime":"13:05","marketEventType":"closed"},{"tradingDate":"2026-06-18",'
            '"eventTime":"14:30","marketEventType":"pcp"},{"tradingDate":"2026-06-18",'
            '"eventTime":"16:00","marketEventType":"closed"}]}'
        ),
        note=(
            "Regular livestock Globex session, Monday-Friday 08:30-13:05 CT, no overnight session: "
            "CME's Live Cattle contract specifications (capture 2020-09-23) and CME's LE "
            "trading-hours record for 2026-06-18 (08:00 preopen, 08:30 open, 13:05 close; capture "
            "2026-07-22). The other cme_*_hours keys give the same hours for HE and LE in every "
            "capture from 2019-08-06 to 2026-05-09. No CME notice of a change to livestock Globex "
            "hours in 2019-2026 was found."
        ),
    ),
    "cme_he_hours_2019": Citation(
        _SPEC_OLD + "lean-hogs_contract_specifications.html",
        "Trading Hours Monday - Friday: 8:30 a.m. - 1:05 p.m. CT",
        note="Lean Hog contract specifications, capture 2019-08-06.",
    ),
    "cme_he_hours_2020": Citation(
        _SPEC_OLD + "lean-hogs_contract_specifications.html",
        (
            "Trading Hours CME Globex: Monday - Friday: 8:30 a.m. - 1:05 p.m. CT (9:30 a.m - 2:05 "
            "p.m. ET)"
        ),
        note="Lean Hog contract specifications, capture 2020-12-03.",
    ),
    "cme_le_hours_2022": Citation(
        _SPEC_NEW + "live-cattle.contractSpecs.html",
        "Trading Hours CME Globex: Monday - Friday: 8:30 a.m. - 1:05 p.m. CT",
        note="Live Cattle contract specifications, capture 2022-11-14.",
    ),
    "cme_he_hours_2023": Citation(
        _SPEC_NEW + "lean-hogs.contractSpecs.html",
        (
            "Trading Hours CME Globex: Monday - Friday: 8:30 a.m. - 1:05 p.m. CT (9:30 a.m - 2:05 "
            "p.m. ET)"
        ),
        note="Lean Hog contract specifications, capture 2023-06-07.",
    ),
    "cme_le_hours_2026": Citation(
        _SPEC_NEW + "live-cattle.contractSpecs.html",
        "Trading Hours CME Globex: Monday - Friday: 8:30 a.m. - 1:05 p.m. CT",
        note="Live Cattle contract specifications, capture 2026-05-09.",
    ),
    "cme_he_hours_2026": Citation(
        _SPEC_NEW + "lean-hogs.contractSpecs.html",
        (
            "Trading Hours CME Globex: Monday - Friday: 8:30 a.m. - 1:05 p.m. CT (9:30 a.m - 2:05 "
            "p.m. ET)"
        ),
        note="Lean Hog contract specifications, capture 2026-04-13.",
    ),
    "cme_livestock_settlement": Citation(
        _WIKI + "457317920/Livestock",
        (
            "CME Group staff determines the daily settlements for Feeder Cattle (GF), Lean Hogs "
            "(HE), Live Cattle (LE), and Pork Cutout (PRK) futures based on trading activity on "
            "CME Globex between 12:59:30 and 13:00:00 Central Time (CT), the settlement period."
        ),
        _WIKI + "457085528/Daily+Settlement+Time+Details",
        "Livestock 12:59:30-13:00:00 CT",
        note=(
            "CME Clearing's settlement procedures (CME client wiki, fetched directly; page version "
            "of 2026-07-15) and CME's Daily Settlement Time Details table."
        ),
    ),
    "cme_livestock_settlement_2018": Citation(
        _WIKI_OLD + "Livestock",
        (
            "last modified by Confluence Admin on Oct 01, 2018 ... CME Group staff determines the "
            "daily settlements for Feeder Cattle (GF), Lean Hogs (HE), and Live Cattle (LE) "
            "futures based on trading activity on CME Globex between 12:59:30 and 13:00:00 Central "
            "Time (CT), the settlement period."
        ),
        _WIKI_OLD + "Daily+Settlement+Time+Details",
        "last modified by Confluence Admin on Aug 02, 2018 ... Livestock 12:59:30-13:00:00 CT",
        note=(
            "The same settlement period in CME's earlier wiki (cmegroup.com/confluence): Livestock "
            "page last modified 2018-10-01 (Wayback capture 2020-09-29) and Daily Settlement Time "
            "Details last modified 2018-08-02 (capture 2022-05-25), so it held through 2019-2020."
        ),
    ),
    "cme_livestock_settlement_2020": Citation(
        _WIKI_OLD + "Livestock",
        (
            "last modified by Confluence Admin on Dec 18, 2020 ... CME Group staff determines the "
            "daily settlements for Feeder Cattle (GF), Lean Hogs (HE), Live Cattle (LE), and Pork "
            "Cutout (PRK) futures based on trading activity on CME Globex between 12:59:30 and "
            "13:00:00 Central Time (CT), the settlement period."
        ),
        note="Livestock settlement page last modified 2020-12-18 (Wayback capture 2023-12-11).",
    ),
}
