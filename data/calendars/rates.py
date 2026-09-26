"""CME Globex calendar for the rates group: CBOT Treasury futures ZT, ZF, ZN, TN, ZB and UB,
2019-05-01..2026-06-19 (Stage E.2a Task 6; design D10 and D11.3).

Interface as data.cme_calendar, whose Holiday, HolidayKind, Citation and CalendarCoverageError are
imported, not redefined: HOLIDAYS, SOURCES, NO_ENTRY_FINDINGS, CALENDAR_COVERAGE and
assert_calendar_coverage, plus SESSIONS (data.calendars.SessionSpec) with SESSION_SOURCES. Two
additive extensions, which no existing caller needs to know about:
- LATE_OPENS: trade dates whose Globex session did not trade from its regular start (one, the
  unscheduled CME outage of 2025-11-28), with LATE_OPEN_SOURCES.
- EARLY_SETTLEMENT_CT: CME-published rates settlement times other than 14:00 CT, with
  EARLY_SETTLEMENT_SOURCES. Information for the lead's ruling on design D6's C; nothing reads it.
- GLOBEX_HOURS_UNDOCUMENTED: days CME settled rates early but for which no CME Globex-hours
  document was retrievable; no entry (regular session assumed), listed for the bar check.

Sources (all CME Group; cmegroup.com refuses automated fetches, so every CME file was read from a
Wayback Machine copy, except the CME client-wiki page read through its REST API):
- 2019-2022: CME's Globex holiday trading schedules (.xls), row "Interest Rate Products"
  (2019-2021 from CME's yearly holiday-calendars.zip, 2022 one file per holiday).
- 2023: CME's holiday summary PDFs (cmegroup.com/trading-hours/files/), row "INTEREST RATE".
- 2023-09..2026-06: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html,
  product 316 (ZN, 10-Year T-Note futures), captures of 2024-07-08, 2024-12-20 and 2026-01-29.
- 2025-01-09: CME's National Day of Mourning trading schedule.
- Settlement notices and clearing advisories under cmegroup.com/tools-information/holiday-calendar/.
Verbatim quotes, capture URLs and file hashes per entry: reports/stage_e2a_calendar_sources_rates
.json and .md. CME states these hours for its interest-rate asset class or for ZN, the most active
rates contract; ZT, ZF, TN, ZB and UB are taken to share them (the only rates exception row in the
schedules read is "Treasuries TAS").

Grades as data.cme_calendar: status (``evidence``) "cme" | "secondary" | "unverified"; time
(``time_evidence``) "cme" | "secondary" | "inferred" | "unverified" | "n/a" ("empirical" is
reserved for the later bar check). Every status here is "cme". Every time is "cme" except
2023-01-16 and 2023-02-20 ("secondary": AMP Futures quoting the CME Globex Control Center; no CME
Globex-hours document for those dates was retrievable) and 2023-04-07 ("inferred" from CME's
10:00 CT rates settlement that day, as the 2021 and 2026 jobs-report Good Fridays settled/closed).

How rates differ from the equity calendar: the day after Thanksgiving and Christmas Eve close at
12:15 CT; the eve of Independence Day, New Year's Eve, the Thursday before Good Friday and the
Friday before Memorial Day keep the regular 16:00 CT Globex close wherever CME documents the day
(CME settled rates at 12:00 CT on those days: EARLY_SETTLEMENT_CT); jobs-report Good Fridays
(2021-04-02, 2023-04-07, 2026-04-03) close at 10:15 CT.

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

RATES_PRODUCTS = ("ZT", "ZF", "ZN", "TN", "ZB", "UB")

HALT_NOON = time(12, 0)
CLOSE_1215 = time(12, 15)
GOOD_FRIDAY_JOBS_CLOSE = time(10, 15)

_HC = "https://www.cmegroup.com/tools-information/holiday-calendar/files/"
_TH = "https://www.cmegroup.com/trading-hours/files/"
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
    _halt(date(2019, 5, 27), "Memorial Day", HALT_NOON),
    _halt(date(2019, 7, 4), "Independence Day", HALT_NOON),
    _halt(date(2019, 9, 2), "Labor Day", HALT_NOON),
    _halt(date(2019, 11, 28), "Thanksgiving Day", HALT_NOON),
    _halt(date(2019, 11, 29), "Day after Thanksgiving", CLOSE_1215),
    _halt(date(2019, 12, 24), "Christmas Eve", CLOSE_1215),
    _closure(date(2019, 12, 25), "Christmas Day"),
    # ---- 2020
    _closure(date(2020, 1, 1), "New Year's Day"),
    _halt(date(2020, 1, 20), "Martin Luther King Jr. Day", HALT_NOON),
    _halt(date(2020, 2, 17), "Presidents Day", HALT_NOON),
    _closure(date(2020, 4, 10), "Good Friday"),
    _halt(date(2020, 5, 25), "Memorial Day", HALT_NOON),
    _halt(date(2020, 7, 3), "Independence Day (observed)", HALT_NOON),
    _halt(date(2020, 9, 7), "Labor Day", HALT_NOON),
    _halt(date(2020, 11, 26), "Thanksgiving Day", HALT_NOON),
    _halt(date(2020, 11, 27), "Day after Thanksgiving", CLOSE_1215),
    _halt(date(2020, 12, 24), "Christmas Eve", CLOSE_1215),
    _closure(date(2020, 12, 25), "Christmas Day"),
    # ---- 2021
    _closure(date(2021, 1, 1), "New Year's Day"),
    _halt(date(2021, 1, 18), "Martin Luther King Jr. Day", HALT_NOON),
    _halt(date(2021, 2, 15), "Presidents Day", HALT_NOON),
    _halt(date(2021, 4, 2), "Good Friday (abbreviated, jobs report)", GOOD_FRIDAY_JOBS_CLOSE),
    _halt(date(2021, 5, 31), "Memorial Day", HALT_NOON),
    _halt(date(2021, 7, 5), "Independence Day (observed)", HALT_NOON),
    _halt(date(2021, 9, 6), "Labor Day", HALT_NOON),
    _halt(date(2021, 11, 25), "Thanksgiving Day", HALT_NOON),
    _halt(date(2021, 11, 26), "Day after Thanksgiving", CLOSE_1215),
    _closure(date(2021, 12, 24), "Christmas Day (observed)"),
    # ---- 2022
    _halt(date(2022, 1, 17), "Martin Luther King Jr. Day", HALT_NOON),
    _halt(date(2022, 2, 21), "Presidents Day", HALT_NOON),
    _closure(date(2022, 4, 15), "Good Friday"),
    _halt(date(2022, 5, 30), "Memorial Day", HALT_NOON),
    _halt(date(2022, 6, 20), "Juneteenth (observed)", HALT_NOON),
    _halt(date(2022, 7, 4), "Independence Day", HALT_NOON),
    _halt(date(2022, 9, 5), "Labor Day", HALT_NOON),
    _halt(date(2022, 11, 24), "Thanksgiving Day", HALT_NOON),
    _halt(date(2022, 11, 25), "Day after Thanksgiving", CLOSE_1215),
    _closure(date(2022, 12, 26), "Christmas Day (observed)"),
    # ---- 2023
    _closure(date(2023, 1, 2), "New Year's Day (observed)"),
    _halt(date(2023, 1, 16), "Martin Luther King Jr. Day", HALT_NOON, time_evidence="secondary"),
    _halt(date(2023, 2, 20), "Presidents Day", HALT_NOON, time_evidence="secondary"),
    _halt(
        date(2023, 4, 7), "Good Friday (abbreviated, jobs report)", GOOD_FRIDAY_JOBS_CLOSE,
        time_evidence="inferred",
    ),
    _halt(date(2023, 5, 29), "Memorial Day", HALT_NOON),
    _halt(date(2023, 6, 19), "Juneteenth", HALT_NOON),
    _halt(date(2023, 7, 4), "Independence Day", HALT_NOON),
    _halt(date(2023, 9, 4), "Labor Day", HALT_NOON),
    _halt(date(2023, 11, 23), "Thanksgiving Day", HALT_NOON),
    _halt(date(2023, 11, 24), "Day after Thanksgiving", CLOSE_1215),
    _closure(date(2023, 12, 25), "Christmas Day"),
    # ---- 2024
    _closure(date(2024, 1, 1), "New Year's Day"),
    _halt(date(2024, 1, 15), "Martin Luther King Jr. Day", HALT_NOON),
    _halt(date(2024, 2, 19), "Presidents Day", HALT_NOON),
    _closure(date(2024, 3, 29), "Good Friday"),
    _halt(date(2024, 5, 27), "Memorial Day", HALT_NOON),
    _halt(date(2024, 6, 19), "Juneteenth", HALT_NOON),
    _halt(date(2024, 7, 4), "Independence Day", HALT_NOON),
    _halt(date(2024, 9, 2), "Labor Day", HALT_NOON),
    _halt(date(2024, 11, 28), "Thanksgiving Day", HALT_NOON),
    _halt(date(2024, 11, 29), "Day after Thanksgiving", CLOSE_1215),
    _halt(date(2024, 12, 24), "Christmas Eve", CLOSE_1215),
    _closure(date(2024, 12, 25), "Christmas Day"),
    # ---- 2025
    _closure(date(2025, 1, 1), "New Year's Day"),
    _halt(date(2025, 1, 9), "National Day of Mourning (Carter)", CLOSE_1215),
    _halt(date(2025, 1, 20), "Martin Luther King Jr. Day", HALT_NOON),
    _halt(date(2025, 2, 17), "Presidents Day", HALT_NOON),
    _closure(date(2025, 4, 18), "Good Friday"),
    _halt(date(2025, 5, 26), "Memorial Day", HALT_NOON),
    _halt(date(2025, 6, 19), "Juneteenth", HALT_NOON),
    _halt(date(2025, 7, 4), "Independence Day", HALT_NOON),
    _halt(date(2025, 9, 1), "Labor Day", HALT_NOON),
    _halt(date(2025, 11, 27), "Thanksgiving Day", HALT_NOON),
    _halt(date(2025, 11, 28), "Day after Thanksgiving", CLOSE_1215),
    _halt(date(2025, 12, 24), "Christmas Eve", CLOSE_1215),
    _closure(date(2025, 12, 25), "Christmas Day"),
    # ---- 2026
    _closure(date(2026, 1, 1), "New Year's Day"),
    _halt(date(2026, 1, 19), "Martin Luther King Jr. Day", HALT_NOON),
    _halt(date(2026, 2, 16), "Presidents Day", HALT_NOON),
    _halt(date(2026, 4, 3), "Good Friday (abbreviated, jobs report)", GOOD_FRIDAY_JOBS_CLOSE),
    _halt(date(2026, 5, 25), "Memorial Day", HALT_NOON),
    _halt(date(2026, 6, 19), "Juneteenth", HALT_NOON),
)

HOLIDAYS: dict[date, Holiday] = {h.day: h for h in _ENTRIES}
CALENDAR_COVERAGE = (date(2019, 5, 1), date(2026, 6, 19))


def assert_calendar_coverage(days: Iterable[date]) -> None:
    """Raise unless every date lies inside ``CALENDAR_COVERAGE`` (inclusive); the semantics of
    data.cme_calendar.assert_calendar_coverage, for the rates group."""
    first, last = CALENDAR_COVERAGE
    outside = sorted(d for d in set(days) if not first <= d <= last)
    if outside:
        raise CalendarCoverageError(
            f"{len(outside)} trade date(s) outside the rates calendar's coverage "
            f"{first}..{last}: {outside[0]} .. {outside[-1]}; extend data/calendars/rates.py first")


@dataclass(frozen=True)
class LateOpen:
    """A trade date whose Globex session did not trade from its regular start: trading stopped at
    ``halt_from_ct`` on the calendar day ``halt_from_offset_days`` from ``day`` (None: the stop
    time is not in any source retrieved) and resumed at ``open_ct`` CT on ``day``. Grades as for
    Holiday. Additive to the data.cme_calendar interface."""

    day: date
    name: str
    open_ct: time
    evidence: str
    time_evidence: str
    halt_from_ct: time | None = None
    halt_from_offset_days: int = -1


LATE_OPENS: dict[date, LateOpen] = {
    date(2025, 11, 28): LateOpen(
        date(2025, 11, 28), "Globex outage (data-center cooling failure)", time(7, 30), "cme", "cme"
    ),
}

# One regime covers the whole window: no CME change to Treasury futures Globex hours was found.
SESSIONS: tuple[SessionSpec, ...] = (
    SessionSpec(
        valid_from=date(2019, 5, 1),
        valid_to=date(2026, 6, 19),
        segments=(Segment(-1, time(17, 0), 0, time(16, 0)),),
        day_session_ct={p: (time(7, 20), time(14, 0)) for p in RATES_PRODUCTS},
        source="cme_treasury_hours",
        note=(
            "day_session_ct is design D6's rates row (O 07:20, C 14:00 CT; F 15:08 CT is applied "
            "by the rules engine), keyed by product. D6 confirmation: C 14:00 CT matches CME's "
            "Treasury settlement period 13:59:30-14:00:00 CT (SESSION_SOURCES key "
            "'cme_treasury_settlement'). O 07:20 CT is not a CME-published boundary of the "
            "Treasury futures Globex session (17:00-16:00 CT), and no CME settlement procedure "
            "defines an open. D6's value is encoded unchanged; the lead rules (reports/"
            "stage_e2a_calendar_sources_rates.md, D6 confirmation). CME settled rates early on "
            "some pre-holiday days while Globex traded to 16:00 CT: EARLY_SETTLEMENT_CT."
        ),
    ),
)

SOURCES: dict[date, Citation] = {
    date(2019, 5, 27): Citation(
        _Z19,
        (
            "Updated 4/29/2019|CME Group Globex Memorial Day Holiday Schedule: May 24, 2019 - "
            "May 28, 2019 ... Calendar Date|Friday, May 24||Sunday, May 26|||||Monday, May "
            "27|||||||Tuesday, May 28 ... Interest Rate Products|04:00:00 PM||04:00:00 "
            "PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
        ),
        _Z19,
        (
            "Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 "
            "PM|12:00:00 PM|05:00:00 PM"
        ),
        note="Zip member globex-trading-schedules/2019-memorial-day-schedule.xls.",
    ),
    date(2019, 7, 4): Citation(
        _Z19,
        (
            "Updated 6/6/2019|CME Group Globex Independence Day Holiday Schedule: July 3, 2019 "
            "to July 5, 2019 ... Calendar Date|Wednesday, July 3||||||||Thursday, July "
            "4||||||||Friday, July 5 ... Interest Rate Products|04:00:00 PM|||04:45:00 "
            "PM|05:00:00 PM||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
        ),
        _Z19,
        (
            "Interest Rate Products|04:00:00 PM|||04:45:00 PM|05:00:00 PM||||||12:00:00 "
            "PM|12:00:00 PM|05:00:00 PM"
        ),
        note="Zip member globex-trading-schedules/2019-independence-day-schedule.xls.",
    ),
    date(2019, 9, 2): Citation(
        _Z19,
        (
            "Updated 8/14/2019|CME Group Globex Labor Day Holiday Schedule: August 30, 2019 - "
            "September 3, 2019 ... Calendar Date|Friday, August 30||Sunday, September "
            "1|||||Monday, September 2|||||||Tuesday, September 3 ... Interest Rate "
            "Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 "
            "PM|05:00:00 PM"
        ),
        _Z19,
        (
            "Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 "
            "PM|12:00:00 PM|05:00:00 PM"
        ),
        note="Zip member globex-trading-schedules/2019-labor-day-schedule.xls.",
    ),
    date(2019, 11, 28): Citation(
        _Z19,
        (
            "Updated 10/07/2019|CME Group Globex Thanksgiving Holiday Schedule: November 27, "
            "2019 - November 29, 2019 ... Calendar Date|Wednesday, November 27|||||||Thursday, "
            "November 28|||||||||Friday, November 29 ... Interest Rate Products|04:00:00 "
            "PM||04:45:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 "
            "PM||||||12:15:00 PM"
        ),
        _Z19,
        (
            "Interest Rate Products|04:00:00 PM||04:45:00 PM|05:00:00 PM|||||||12:00:00 "
            "PM|12:00:00 PM|05:00:00 PM||||||12:15:00 PM"
        ),
        note="Zip member globex-trading-schedules/2019-thanksgiving-schedule.xls.",
    ),
    date(2019, 11, 29): Citation(
        _Z19,
        (
            "Updated 10/07/2019|CME Group Globex Thanksgiving Holiday Schedule: November 27, "
            "2019 - November 29, 2019 ... Calendar Date|Wednesday, November 27|||||||Thursday, "
            "November 28|||||||||Friday, November 29 ... Interest Rate Products|04:00:00 "
            "PM||04:45:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 "
            "PM||||||12:15:00 PM"
        ),
        _Z19,
        (
            "Interest Rate Products|04:00:00 PM||04:45:00 PM|05:00:00 PM|||||||12:00:00 "
            "PM|12:00:00 PM|05:00:00 PM||||||12:15:00 PM"
        ),
        note="Zip member globex-trading-schedules/2019-thanksgiving-schedule.xls.",
    ),
    date(2019, 12, 24): Citation(
        _Z19,
        (
            "Updated 10/01/2019|CME Group Globex Christmas Holiday Schedule: December 24, 2019 "
            "- December 26, 2019 ... Calendar Date|Tuesday, December 24|Wednesday, December "
            "25|Wednesday, December 25||||||Thursday, December 26 ... Interest Rate "
            "Products|12:15:00 PM|Globex Closed|04:00:00 PM|05:00:00 PM|||||||04:00:00 PM"
        ),
        _Z19,
        (
            "Interest Rate Products|12:15:00 PM|Globex Closed|04:00:00 PM|05:00:00 "
            "PM|||||||04:00:00 PM"
        ),
        note="Zip member globex-trading-schedules/2019-christmas-holiday-schedule.xls.",
    ),
    date(2019, 12, 25): Citation(
        _Z19,
        (
            "Updated 10/01/2019|CME Group Globex Christmas Holiday Schedule: December 24, 2019 "
            "- December 26, 2019 ... Calendar Date|Tuesday, December 24|Wednesday, December "
            "25|Wednesday, December 25||||||Thursday, December 26 ... Interest Rate "
            "Products|12:15:00 PM|Globex Closed|04:00:00 PM|05:00:00 PM|||||||04:00:00 PM"
        ),
        note="Zip member globex-trading-schedules/2019-christmas-holiday-schedule.xls.",
    ),
    date(2020, 1, 1): Citation(
        _Z19,
        (
            "Updated 10/01/2019|CME Group Globex New Years Holiday Schedule: December 31, 2019 "
            "- January 2, 2020 ... Calendar Date|Tuesday, December 31|Wednesday, January "
            "1|Wednesday, January 1||||||Thursday, Jan 2 ... Interest Rate Products|04:00:00 "
            "PM|Globex Closed|04:00:00 PM|05:00:00 PM|||||||04:00:00 PM"
        ),
        note="Zip member globex-trading-schedules/2019-2020-new-years-holiday-schedule.xls.",
    ),
    date(2020, 1, 20): Citation(
        _Z20,
        (
            "Updated 4/6/2020|CME Group Globex Martin Luther King Day Holiday Schedule: January "
            "17, 2020 - January 21, 2020 ... Calendar Date|Friday, January 17||Sunday, January "
            "19|||||Monday, January 20|||||||Tuesday, January 21 ... Interest Rate "
            "Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 "
            "PM|05:00:00 PM"
        ),
        _Z20,
        (
            "Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 "
            "PM|12:00:00 PM|05:00:00 PM"
        ),
        note="Zip member 2020-mlk-day-schedule.xls.",
    ),
    date(2020, 2, 17): Citation(
        _Z20,
        (
            "Updated 4/6/2020|CME Group Globex Presidents Day Holiday Schedule: February 14, "
            "2020 - February 18, 2020 ... Calendar Date|Friday, February 14||Sunday, February "
            "16|||||Monday, February 17|||||||Tuesday, February 18 ... Interest Rate "
            "Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 "
            "PM|05:00:00 PM"
        ),
        _Z20,
        (
            "Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 "
            "PM|12:00:00 PM|05:00:00 PM"
        ),
        note="Zip member 2020-presidents-day-schedule.xls.",
    ),
    date(2020, 4, 10): Citation(
        _Z20,
        (
            "Updated 4/6/2020|CME Group Globex Good Friday Holiday Schedule: April 9, 2020 to "
            "April 13, 2020 ... Calendar Date|Thursday, April 9||||||Friday, April 10|||Sunday, "
            "April 12|||||Monday, April 13 ... Interest Rate Products|04:00:00 PM||||||Globex "
            "Closed|||04:00:00 PM|05:00:00 PM"
        ),
        note="Zip member 2020-good-friday-schedule.xls.",
    ),
    date(2020, 5, 25): Citation(
        _Z20,
        (
            "Updated 4/21/2020|CME Group Globex Memorial Day Holiday Schedule: May 22, 2020 - "
            "May 26, 2020 ... Calendar Date|Friday, May 22||Sunday, May 24|||||Monday, May "
            "25|||||||Tuesday, May 26 ... Interest Rate Products|04:00:00 PM||04:00:00 "
            "PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
        ),
        _Z20,
        (
            "Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 "
            "PM|12:00:00 PM|05:00:00 PM"
        ),
        note="Zip member 2020-memorial-day-schedule.xls.",
    ),
    date(2020, 7, 3): Citation(
        _Z20,
        (
            "Updated 6/26/2020|CME Group Globex Independence Day Holiday Schedule: July 2, 2020 "
            "to July 6, 2020 ... Calendar Date|Thursday, July 2||||||||Friday, July 3|||Sunday, "
            "July 5|||||Monday, July 6 ... Interest Rate Products|04:00:00 PM|||04:45:00 "
            "PM|05:00:00 PM||||||12:00:00 PM|04:00:00 PM|05:00:00 PM"
        ),
        _Z20,
        (
            "Interest Rate Products|04:00:00 PM|||04:45:00 PM|05:00:00 PM||||||12:00:00 "
            "PM|04:00:00 PM|05:00:00 PM"
        ),
        note=(
            "Zip member 2020-independence-day-schedule.xls. CME labels the Friday 12:00 CT "
            "event 'Close'; the next open is Sunday 17:00 CT."
        ),
    ),
    date(2020, 9, 7): Citation(
        _Z20,
        (
            "Updated 8/28/2020|CME Group Globex Labor Day Holiday Schedule: September 4, 2020 - "
            "September 8, 2020 ... Calendar Date|Friday, September 4||Sunday, September "
            "6|||||Monday, September 7|||||||Tuesday, September 8 ... Interest Rate "
            "Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 "
            "PM|05:00:00 PM"
        ),
        _Z20,
        (
            "Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 "
            "PM|12:00:00 PM|05:00:00 PM"
        ),
        note="Zip member 2020-labor-day-schedule.xls.",
    ),
    date(2020, 11, 26): Citation(
        _Z20,
        (
            "Updated 10/13/2020|CME Group Globex Thanksgiving Holiday Schedule: November 25, "
            "2020 - November 27, 2020 ... Calendar Date|Wednesday, November 25|||||||Thursday, "
            "November 26|||||||||Friday, November 27 ... Interest Rate Products|04:00:00 "
            "PM||04:45:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 "
            "PM||||||12:15:00 PM"
        ),
        _Z20,
        (
            "Interest Rate Products|04:00:00 PM||04:45:00 PM|05:00:00 PM|||||||12:00:00 "
            "PM|12:00:00 PM|05:00:00 PM||||||12:15:00 PM"
        ),
        note="Zip member 2020-thanksgiving-schedule.xls.",
    ),
    date(2020, 11, 27): Citation(
        _Z20,
        (
            "Updated 10/13/2020|CME Group Globex Thanksgiving Holiday Schedule: November 25, "
            "2020 - November 27, 2020 ... Calendar Date|Wednesday, November 25|||||||Thursday, "
            "November 26|||||||||Friday, November 27 ... Interest Rate Products|04:00:00 "
            "PM||04:45:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 "
            "PM||||||12:15:00 PM"
        ),
        _Z20,
        (
            "Interest Rate Products|04:00:00 PM||04:45:00 PM|05:00:00 PM|||||||12:00:00 "
            "PM|12:00:00 PM|05:00:00 PM||||||12:15:00 PM"
        ),
        note="Zip member 2020-thanksgiving-schedule.xls.",
    ),
    date(2020, 12, 24): Citation(
        _Z20,
        (
            "Updated 11/17/2020|CME Group Globex Christmas Holiday Schedule: December 24, 2020 "
            "- December 28, 2020 ... Calendar Date|Thursday, December 24|Friday, December "
            "25|Sunday, December 27||||||Monday, December 28 ... Interest Rate "
            "Products|12:15:00 PM|Globex Closed|04:00:00 PM|05:00:00 PM|||||||04:00:00 PM"
        ),
        _Z20,
        (
            "Interest Rate Products|12:15:00 PM|Globex Closed|04:00:00 PM|05:00:00 "
            "PM|||||||04:00:00 PM"
        ),
        note="Zip member 2020-christmas-holiday-schedule.xls.",
    ),
    date(2020, 12, 25): Citation(
        _Z20,
        (
            "Updated 11/17/2020|CME Group Globex Christmas Holiday Schedule: December 24, 2020 "
            "- December 28, 2020 ... Calendar Date|Thursday, December 24|Friday, December "
            "25|Sunday, December 27||||||Monday, December 28 ... Interest Rate "
            "Products|12:15:00 PM|Globex Closed|04:00:00 PM|05:00:00 PM|||||||04:00:00 PM"
        ),
        note="Zip member 2020-christmas-holiday-schedule.xls.",
    ),
    date(2021, 1, 1): Citation(
        _Z20,
        (
            "Updated 12/09/2020|CME Group Globex New Years Holiday Schedule: December 31, 2020 "
            "- January 4, 2021 ... Calendar Date|Thursday, December 31|Friday, January 1|Sunday,"
            " January 3||||||Monday, January 4 ... Interest Rate Products|04:00:00 PM|Globex "
            "Closed|04:00:00 PM|05:00:00 PM|||||||04:00:00 PM"
        ),
        note="Zip member 2021-new-years-holiday-schedule.xls.",
    ),
    date(2021, 1, 18): Citation(
        _Z21,
        (
            "Updated 12/23/2020|CME Group Globex Martin Luther King Day Holiday Schedule: "
            "January 15, 2021 - January 19, 2021 ... Calendar Date|Friday, January 15||Sunday, "
            "January 17|||||Monday, January 18|||||||Tuesday, January 19 ... Interest Rate "
            "Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 "
            "PM|05:00:00 PM"
        ),
        _Z21,
        (
            "Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 "
            "PM|12:00:00 PM|05:00:00 PM"
        ),
        note="Zip member 2021-mlk-day-holiday-schedule.xls.",
    ),
    date(2021, 2, 15): Citation(
        _Z21,
        (
            "Updated 2/11/2021|CME Group Globex Presidents Day Holiday Schedule: February 12, "
            "2021 - February 16, 2021 ... Calendar Date|Friday, February 12||Sunday, February "
            "14|||||Monday, February 15|||||||Tuesday, February 16 ... Interest Rate "
            "Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 "
            "PM|05:00:00 PM"
        ),
        _Z21,
        (
            "Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 "
            "PM|12:00:00 PM|05:00:00 PM"
        ),
        note="Zip member 2021-presidents-day-holiday-schedule.xls.",
    ),
    date(2021, 4, 2): Citation(
        _Z21,
        (
            "Updated 3/31/2021|CME Group Globex Good Friday Holiday Schedule: April 1, 2021 to "
            "April 5, 2021 ... Calendar Date|Thursday, April 1||||||Friday, April 2|||Sunday, "
            "April 4|||||Monday, April 5 ... Interest Rate Products|04:00:00 PM|||04:45:00 "
            "PM|05:00:00 PM||||10:15:00 AM|04:00:00 PM|05:00:00 PM"
        ),
        _Z21,
        (
            "Interest Rate Products|04:00:00 PM|||04:45:00 PM|05:00:00 PM||||10:15:00 "
            "AM|04:00:00 PM|05:00:00 PM"
        ),
        note=(
            "Zip member 2021-good-friday-holiday-schedule.xls. Jobs-report Good Friday: "
            "Thursday 17:00 CT reopen for this trade date, close 10:15 CT."
        ),
    ),
    date(2021, 5, 31): Citation(
        _Z21,
        (
            "Updated 5/25/2021|CME Group Globex Memorial Day Holiday Schedule: May 28, 2021 - "
            "Jun 1, 2021 ... Calendar Date|Friday, May 28||Sunday, May 30|||||Monday, May "
            "31|||||||Tuesday, Jun 1 ... Interest Rate Products|04:00:00 PM||04:00:00 "
            "PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
        ),
        _Z21,
        (
            "Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 "
            "PM|12:00:00 PM|05:00:00 PM"
        ),
        note="Zip member 2021-memorial-day-holiday-schedule.xls.",
    ),
    date(2021, 7, 5): Citation(
        _Z21,
        (
            "Updated 7/1/2021|CME Group Globex Independence Day Holiday Schedule: July 2, 2021 "
            "to July 6, 2021 ... Calendar Date|Friday, July 2||Sunday, July 4|||||Monday, July "
            "5||||||Tuesday, July 6 ... Interest Rate Products|04:00:00 PM||04:00:00 "
            "PM|05:00:00 PM||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
        ),
        _Z21,
        (
            "Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM||||||12:00:00 "
            "PM|12:00:00 PM|05:00:00 PM"
        ),
        note="Zip member 2021-independence-day-holiday-schedule.xls.",
    ),
    date(2021, 9, 6): Citation(
        _Z21,
        (
            "Updated 8/12/2021|CME Group Globex Labor Day Holiday Schedule: September 3, 2021 - "
            "September 7, 2021 ... Calendar Date|Friday, September 3||Sunday, September "
            "5|||||Monday, September 6|||||||Tuesday, September 7 ... Interest Rate "
            "Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 "
            "PM|05:00:00 PM"
        ),
        _Z21,
        (
            "Interest Rate Products|04:00:00 PM||04:00:00 PM|05:00:00 PM|||||||12:00:00 "
            "PM|12:00:00 PM|05:00:00 PM"
        ),
        note="Zip member 2021-labor-day-holiday-schedule.xls.",
    ),
    date(2021, 11, 25): Citation(
        _Z21,
        (
            "Updated 11/23/2021|CME Group Globex Thanksgiving Holiday Schedule: November 24, "
            "2021 - November 26, 2021 ... Calendar Date|Wednesday, November 24|||||||Thursday, "
            "November 25|||||||||Friday, November 26 ... Interest Rate Products|04:00:00 "
            "PM||04:45:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 "
            "PM||||||12:15:00 PM"
        ),
        _Z21,
        (
            "Interest Rate Products|04:00:00 PM||04:45:00 PM|05:00:00 PM|||||||12:00:00 "
            "PM|12:00:00 PM|05:00:00 PM||||||12:15:00 PM"
        ),
        note="Zip member 2021-thanksgiving-holiday-schedule.xls.",
    ),
    date(2021, 11, 26): Citation(
        _Z21,
        (
            "Updated 11/23/2021|CME Group Globex Thanksgiving Holiday Schedule: November 24, "
            "2021 - November 26, 2021 ... Calendar Date|Wednesday, November 24|||||||Thursday, "
            "November 25|||||||||Friday, November 26 ... Interest Rate Products|04:00:00 "
            "PM||04:45:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 "
            "PM||||||12:15:00 PM"
        ),
        _Z21,
        (
            "Interest Rate Products|04:00:00 PM||04:45:00 PM|05:00:00 PM|||||||12:00:00 "
            "PM|12:00:00 PM|05:00:00 PM||||||12:15:00 PM"
        ),
        note="Zip member 2021-thanksgiving-holiday-schedule.xls.",
    ),
    date(2021, 12, 24): Citation(
        _Z21,
        (
            "Updated 12/01/2021|CME Group Globex Christmas Holiday Schedule: December 24, 2021 "
            "- December 27, 2021 ... Calendar Date|Thursday, December 23|||||||||||||Friday, "
            "December 24||||||||||Sunday, December 26||||||Monday, Dec 27 ... Interest Rate "
            "Products|04:00:00 PM|||||||||||||Globex Closed||||||||||04:00:00 PM|05:00:00 "
            "PM|||||||04:00:00 PM"
        ),
        note="Zip member 2021-christmas-holiday-schedule.xls.",
    ),
    date(2022, 1, 17): Citation(
        _HC + "2022-mlk-day-holiday-schedule.xls",
        (
            "Updated 12/14/2021|CME Group Globex Martin Luther King Day Holiday Schedule: "
            "January 14, 2022 - January 18, 2022 ... Calendar Date|Friday, January "
            "14|||||Sunday, January 16|||||Monday, January 17|||||||||Tuesday, January 18 ... "
            "Interest Rate Products|04:00:00 PM|||||04:00:00 PM|05:00:00 PM|||||||12:00:00 "
            "PM|12:00:00 PM|05:00:00 PM"
        ),
        _HC + "2022-mlk-day-holiday-schedule.xls",
        (
            "Interest Rate Products|04:00:00 PM|||||04:00:00 PM|05:00:00 PM|||||||12:00:00 "
            "PM|12:00:00 PM|05:00:00 PM"
        ),
    ),
    date(2022, 2, 21): Citation(
        _HC + "2022-presidents-day-holiday-schedule.xls",
        (
            "Updated 1/24/2022|CME Group Globex Presidents Day Holiday Schedule: February 18, "
            "2022 - February 22, 2022 ... Calendar Date|Friday, February 18|||||Sunday, "
            "February 20|||||Monday, February 21||||||||||||Tuesday, February 22 ... Interest "
            "Rate Products|04:00:00 PM|||||04:00:00 PM|05:00:00 PM|||||||12:00:00 "
            "PM||||12:00:00 PM|05:00:00 PM"
        ),
        _HC + "2022-presidents-day-holiday-schedule.xls",
        (
            "Interest Rate Products|04:00:00 PM|||||04:00:00 PM|05:00:00 PM|||||||12:00:00 "
            "PM||||12:00:00 PM|05:00:00 PM"
        ),
    ),
    date(2022, 4, 15): Citation(
        _HC + "2022-good-friday-holiday-schedule.xls",
        (
            "Updated 3/17/2022|CME Group Globex Good Friday Holiday Schedule: April 14, 2022 to "
            "April 18, 2022 ... Calendar Date|Thursday, April 14|||||||||Friday, April "
            "15|||Sunday, April 17|||||Monday, April 18 ... Interest Rate Products|04:00:00 "
            "PM|||||||||Globex Closed|||04:00:00 PM|05:00:00 PM"
        ),
    ),
    date(2022, 5, 30): Citation(
        _HC + "2022-memorial-day-holiday-schedule.xls",
        (
            "Updated 5/18/2022|CME Group Globex Memorial Day Holiday Schedule: May 27, 2022 - "
            "May 31, 2022 ... Calendar Date|Friday, May 27|||||Sunday, May 29|||||Monday, May "
            "30||||||||||Tuesday, May 31 ... Interest Rate Products|04:00:00 PM|||||04:00:00 "
            "PM|05:00:00 PM|||||||12:00:00 PM||||12:00:00 PM|05:00:00 PM"
        ),
        _HC + "2022-memorial-day-holiday-schedule.xls",
        (
            "Interest Rate Products|04:00:00 PM|||||04:00:00 PM|05:00:00 PM|||||||12:00:00 "
            "PM||||12:00:00 PM|05:00:00 PM"
        ),
    ),
    date(2022, 6, 20): Citation(
        _HC + "2022-juneteenth-holiday-schedule.xls",
        (
            "Updated 5/18/2022|CME Group Globex Juneteenth Holiday Schedule: June 17, 2022 - "
            "Jun 21, 2022 ... Calendar Date|Friday, June 17|||||Sunday, June 19|||||Monday, "
            "June 20||||||||||Tuesday, Jun 21 ... Interest Rate Products|04:00:00 "
            "PM|||||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM||||12:00:00 PM|05:00:00 PM"
        ),
        _HC + "2022-juneteenth-holiday-schedule.xls",
        (
            "Interest Rate Products|04:00:00 PM|||||04:00:00 PM|05:00:00 PM|||||||12:00:00 "
            "PM||||12:00:00 PM|05:00:00 PM"
        ),
    ),
    date(2022, 7, 4): Citation(
        _HC + "2022-independence-day-holiday-schedule.xls",
        (
            "Updated 6/29/2022|CME Group Globex Independence Day Holiday Schedule: July 1, 2022 "
            "to July 5, 2022 ... Calendar Date|Friday, July 1|||||Sunday, July 3|||||Monday, "
            "July 4|||||||||||Tuesday, July 5 ... Interest Rate Products|04:00:00 "
            "PM|||||04:00:00 PM|05:00:00 PM||||||12:00:00 PM||||12:00:00 PM|05:00:00 PM"
        ),
        _HC + "2022-independence-day-holiday-schedule.xls",
        (
            "Interest Rate Products|04:00:00 PM|||||04:00:00 PM|05:00:00 PM||||||12:00:00 "
            "PM||||12:00:00 PM|05:00:00 PM"
        ),
    ),
    date(2022, 9, 5): Citation(
        _HC + "2022-labor-day-holiday-schedule.xls",
        (
            "Updated 6/29/2022|CME Group Globex Labor Day Holiday Schedule: September 2, 2022 - "
            "September 6, 2022 ... Calendar Date|Friday, September 2|||||Sunday, September "
            "4|||||Monday, September 5||||||||||Tuesday, Sept. 6 ... Interest Rate "
            "Products|04:00:00 PM|||||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM||||12:00:00 "
            "PM|05:00:00 PM"
        ),
        _HC + "2022-labor-day-holiday-schedule.xls",
        (
            "Interest Rate Products|04:00:00 PM|||||04:00:00 PM|05:00:00 PM|||||||12:00:00 "
            "PM||||12:00:00 PM|05:00:00 PM"
        ),
        note=(
            "CME sheet 'Updated 6/29/2022', captured 2022-07-04; a later CME revision cannot be "
            "excluded."
        ),
    ),
    date(2022, 11, 24): Citation(
        _HC + "2022-thanksgiving-holiday-schedule.xls",
        (
            "Updated 6/29/2022|CME Group Globex Thanksgiving Holiday Schedule: November 23, "
            "2022 - November 25, 2022 ... Calendar Date|Wednesday, November "
            "23||||||||||Thursday, November 24||||||||||||Friday, November 25 ... Interest Rate "
            "Products|04:00:00 PM|||||04:45:00 PM|05:00:00 PM|||||||12:00:00 PM||||12:00:00 "
            "PM|05:00:00 PM||||||12:15:00 PM"
        ),
        _HC + "2022-thanksgiving-holiday-schedule.xls",
        (
            "Interest Rate Products|04:00:00 PM|||||04:45:00 PM|05:00:00 PM|||||||12:00:00 "
            "PM||||12:00:00 PM|05:00:00 PM||||||12:15:00 PM"
        ),
        note=(
            "CME sheet 'Updated 6/29/2022', captured 2022-07-04; a later CME revision cannot be "
            "excluded."
        ),
    ),
    date(2022, 11, 25): Citation(
        _HC + "2022-thanksgiving-holiday-schedule.xls",
        (
            "Updated 6/29/2022|CME Group Globex Thanksgiving Holiday Schedule: November 23, "
            "2022 - November 25, 2022 ... Calendar Date|Wednesday, November "
            "23||||||||||Thursday, November 24||||||||||||Friday, November 25 ... Interest Rate "
            "Products|04:00:00 PM|||||04:45:00 PM|05:00:00 PM|||||||12:00:00 PM||||12:00:00 "
            "PM|05:00:00 PM||||||12:15:00 PM"
        ),
        _HC + "2022-thanksgiving-holiday-schedule.xls",
        (
            "Interest Rate Products|04:00:00 PM|||||04:45:00 PM|05:00:00 PM|||||||12:00:00 "
            "PM||||12:00:00 PM|05:00:00 PM||||||12:15:00 PM"
        ),
        note=(
            "CME sheet 'Updated 6/29/2022', captured 2022-07-04; a later CME revision cannot be "
            "excluded."
        ),
    ),
    date(2022, 12, 26): Citation(
        _HC + "2022-christmas-holiday-schedule.xls",
        (
            "Updated 6/29/2022|CME Group Globex Christmas Holiday Schedule: December 23, 2022 - "
            "December 27, 2022 ... Calendar Date|Friday, December 23||||||||Monday, December "
            "26||||||||||||||||Tuesday, December 27 ... Interest Rate Products|04:00:00 "
            "PM||||||||Globex Closed||||||||||04:00:00 PM|05:00:00 PM|||||||04:00:00 PM"
        ),
        note=(
            "CME sheet 'Updated 6/29/2022', captured 2022-07-04; a later CME revision cannot be "
            "excluded."
        ),
    ),
    date(2023, 1, 2): Citation(
        _HC + "2023-new-years-holiday-schedule.xls",
        (
            "Updated 6/29/22|CME Group Globex New Year's Holiday Schedule: December 30, 2022 - "
            "January 3, 2023 ... Calendar Date|Friday, December 30||||Monday, January 2|Monday, "
            "January 2||||||Tuesday, January 3 ... Interest Rate Products|04:00:00 PM||||Globex "
            "Closed|04:00:00 PM|05:00:00 PM"
        ),
        note=(
            "CME sheet 'Updated 6/29/22', captured 2022-07-04; a later CME revision cannot be "
            "excluded."
        ),
    ),
    date(2023, 1, 16): Citation(
        _HC + "mlk-day-holiday-settlement-times-2023.pdf",
        (
            "Martin Luther King Holiday 1/16/2023 Settlement Times ... Monday, January 16, 2023 "
            "Holiday ... Note: Monday January 16, 2023 CME Group will not derive or disseminate "
            "settlement prices (other than the two LIBOR Settlements listed above) for CME, "
            "CBOT, NYMEX or COMEX"
        ),
        "https://www.ampfutures.com/news/holiday-trading-schedule-martin-luther-king-day-2023",
        (
            'Monday, January 16, 2023 - Early Market "HALT" - Noon CST (Chicago) > then reopens '
            "normal times."
        ),
        note=(
            "Time secondary: AMP Futures quoting CME's Globex Control Center (its image of "
            "CME's schedule shows the Interest Rate row HALT 12:00 CST); no CME Globex-hours "
            "document was retrievable."
        ),
    ),
    date(2023, 2, 20): Citation(
        _HC + "presidents-day-holiday-settlement-times-2023.pdf",
        (
            "Presidents’ Day Holiday 2/20/2023 Settlement Times ... Note: Monday February 20, "
            "2023 CME Group will not derive or disseminate settlement prices for CME, CBOT, "
            "NYMEX or COMEX"
        ),
        "https://www.ampfutures.com/news/holiday-trading-schedule-presidents-day-2023",
        (
            'Monday, February 20, 2023 - Early Market "HALT" - Noon CST (Chicago) > then '
            "reopens normal times."
        ),
        note=(
            "Time secondary: AMP Futures quoting CME's Globex Control Center (its image of "
            "CME's schedule shows the Interest Rate row HALT 12:00 CST); no CME Globex-hours "
            "document was retrievable."
        ),
    ),
    date(2023, 4, 7): Citation(
        _HC + "good-friday-holiday-settlement-times-2023.pdf",
        (
            "Good Friday 4/7/2023 Settlement Times Friday, April 7, 2023 ... CME Group Interest "
            "Rate Products 10:00 am CT Good Friday, 4/7/2023 Due to the BLS Employment "
            "Situation Release on April 7, 2023 CME Group FX, Cryptocurrency and Interest rate "
            "products will have unique settlements for trade date April 7th."
        ),
        _HC + "good-friday-holiday-settlement-times-2023.pdf",
        "CME Group Interest Rate Products 10:00 am CT",
        note=(
            "Close 10:15 CT inferred from CME's 10:00 CT rates settlement that day (CME closed "
            "rates at 10:15 CT on the 2021-04-02 and 2026-04-03 jobs-report Good Fridays)."
        ),
    ),
    date(2023, 5, 29): Citation(
        _TH + "memorial-day-2023.pdf",
        (
            "PRODUCT NAME SUNDAY, 28 MAY 2023 MONDAY, 29 MAY 2023 TUESDAY, 30 MAY 2023 ... "
            "TRADE DATE: TUES 30 MAY TRADE DATE: TUES 30 MAY INTEREST RATE 16:00 (PREOPEN) "
            "12:00 (PREOPEN) HALT TRADE DATE: WED 31 MAY"
        ),
        _TH + "memorial-day-2023.pdf",
        (
            "INTEREST RATE 16:00 (PREOPEN) 12:00 (PREOPEN) HALT TRADE DATE: WED 31 MAY ... "
            "OPEN: Start of continuous trading 17:00 (OPEN) 17:00 (OPEN) 16:45 (PREOPEN)"
        ),
    ),
    date(2023, 6, 19): Citation(
        _TH + "juneteenth-2023.pdf",
        (
            "PRODUCT NAME SUNDAY, 18 JUNE 2023 MONDAY, 19 JUNE 2023 TUESDAY, 20 JUNE 2023 ... "
            "TRADE DATE: TUES 20 JUNE TRADE DATE: TUES 20 JUNE INTEREST RATE 16:00 (PREOPEN) "
            "12:00 (PREOPEN) HALT TRADE DATE: WED 21 JUNE"
        ),
        _TH + "juneteenth-2023.pdf",
        (
            "INTEREST RATE 16:00 (PREOPEN) 12:00 (PREOPEN) HALT TRADE DATE: WED 21 JUNE ... "
            "OPEN: Start of continuous trading 17:00 (OPEN) 17:00 (OPEN) 16:45 (PREOPEN)"
        ),
    ),
    date(2023, 7, 4): Citation(
        _TH + "4th-of-july-2023.pdf",
        (
            "PRODUCT NAME MONDAY, 3 JULY 2023 TUESDAY, 4 JULY 2023 WEDNESDAY, 5 JULY 2023 ... "
            "TRADE DATE: WED 5 JULY INTEREST RATE TRADE DATE: WED 5 JULY 12:00 (PREOPEN) HALT "
            "TRADE DATE: THUR 6 JULY"
        ),
        _TH + "4th-of-july-2023.pdf",
        (
            "INTEREST RATE TRADE DATE: WED 5 JULY 12:00 (PREOPEN) HALT TRADE DATE: THUR 6 JULY "
            "... OPEN: Start of continuous trading 16:45 (PREOPEN) 17:00 (OPEN)"
        ),
    ),
    date(2023, 9, 4): Citation(
        _TH + "labor-day-2023.pdf",
        (
            "PRODUCT NAME SUNDAY, 3 SEPTEMBER 2023 MONDAY, 4 SEPTEMBER 2023 TUESDAY, 5 "
            "SEPTEMBER 2023 ... TRADE DATE: TUES 5 SEP TRADE DATE: TUES 5 SEP INTEREST RATE "
            "16:00 (PREOPEN) 12:00 (PREOPEN) HALT TRADE DATE: WED 6 SEP"
        ),
        _svc("2023-09-03", "2023-09-05", "1720455278654"),
        (
            '{"groupCode":"ZN","eventDate":"2023-09-04","events":[{"tradingDate":"2023-09-05",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2023-09-05",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
    ),
    date(2023, 11, 23): Citation(
        _TH + "thanksgiving-day-2023.pdf",
        (
            "PRODUCT NAME WEDNESDAY, 22 NOVEMBER 2023 THURSDAY, 23 NOVEMBER 2023 FRIDAY, 24 "
            "NOVEMBER 2023 ... INTEREST RATE TRADE DATE: FRI 24 NOV 12:00 (PREOPEN) HALT 12:15 "
            "(CLOSED)"
        ),
        _svc("2023-11-22", "2023-11-24", "1720455278656"),
        (
            '{"groupCode":"ZN","eventDate":"2023-11-23","events":[{"tradingDate":"2023-11-24",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2023-11-24",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
    ),
    date(2023, 11, 24): Citation(
        _TH + "thanksgiving-day-2023.pdf",
        (
            "PRODUCT NAME WEDNESDAY, 22 NOVEMBER 2023 THURSDAY, 23 NOVEMBER 2023 FRIDAY, 24 "
            "NOVEMBER 2023 ... INTEREST RATE TRADE DATE: FRI 24 NOV 12:00 (PREOPEN) HALT 12:15 "
            "(CLOSED)"
        ),
        _svc("2023-11-22", "2023-11-24", "1720455278656"),
        (
            '{"groupCode":"ZN","eventDate":"2023-11-24","events":[{"tradingDate":"2023-11-24",'
            '"eventTime":"12:15","marketEventType":"closed"}]}'
        ),
    ),
    date(2023, 12, 25): Citation(
        _TH + "christmas-day-2023.pdf",
        (
            "PRODUCT NAME MONDAY, 25 DECEMBER 2023 TUESDAY, 26 DECEMBER 2023 TRADE DATE: TUES "
            "26 DEC TRADE DATE: TUES 26 DEC 16:00 (CLOSED) INTEREST RATE 16:00 (PREOPEN) TRADE "
            "DATE: WED 27 DEC 17:00 (OPEN)"
        ),
        note=(
            "The preceding Friday's (2023-12-22) rates close is not in any CME document "
            "retrieved."
        ),
    ),
    date(2024, 1, 1): Citation(
        _TH + "new-years-day-2024.pdf",
        (
            "PRODUCT NAME MONDAY, 1 JANUARY 2024 TUESDAY, 2 JANUARY 2024 TRADE DATE: TUES 2 JAN "
            "TRADE DATE: TUES 2 JAN 16:00 (CLOSED) INTEREST RATE 16:00 (PREOPEN) TRADE DATE: "
            "WED 3 JAN 17:00 (OPEN)"
        ),
        note=(
            "The preceding Friday's (2023-12-29) rates close is not in any CME document "
            "retrieved."
        ),
    ),
    date(2024, 1, 15): Citation(
        _svc("2024-01-14", "2024-01-16", "1720455278663"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2024-01-15","events":[{"tradingDate":"2024-01-16",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2024-01-16",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
        _svc("2024-01-14", "2024-01-16", "1720455278663"),
        (
            '{"groupCode":"ZN","eventDate":"2024-01-15","events":[{"tradingDate":"2024-01-16",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2024-01-16",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
    ),
    date(2024, 2, 19): Citation(
        _svc("2024-02-18", "2024-02-20", "1720455278669"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2024-02-19","events":[{"tradingDate":"2024-02-20",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2024-02-20",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
        _svc("2024-02-18", "2024-02-20", "1720455278669"),
        (
            '{"groupCode":"ZN","eventDate":"2024-02-19","events":[{"tradingDate":"2024-02-20",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2024-02-20",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
    ),
    date(2024, 3, 29): Citation(
        _svc("2024-03-28", "2024-03-30", "1720455278672"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2024-03-28","events":[{"tradingDate":"2024-03-28",'
            '"eventTime":"16:00","marketEventType":"closed"}]} ... {"groupCode":"ZN",'
            '"eventDate":"2024-03-29","events":[]}'
        ),
        note="ZN record: 2024-03-28 closed 16:00 with no evening reopen; no events on 2024-03-29.",
    ),
    date(2024, 5, 27): Citation(
        _svc("2024-05-26", "2024-05-28", "1720455278675"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2024-05-27","events":[{"tradingDate":"2024-05-28",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2024-05-28",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
        _svc("2024-05-26", "2024-05-28", "1720455278675"),
        (
            '{"groupCode":"ZN","eventDate":"2024-05-27","events":[{"tradingDate":"2024-05-28",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2024-05-28",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
    ),
    date(2024, 6, 19): Citation(
        _svc("2024-06-18", "2024-06-20", "1720455278677"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2024-06-19","events":[{"tradingDate":"2024-06-20",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2024-06-20",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
        _svc("2024-06-18", "2024-06-20", "1720455278677"),
        (
            '{"groupCode":"ZN","eventDate":"2024-06-19","events":[{"tradingDate":"2024-06-20",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2024-06-20",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
    ),
    date(2024, 7, 4): Citation(
        _svc("2024-07-03", "2024-07-05", "1720455278680"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2024-07-04","events":[{"tradingDate":"2024-07-05",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2024-07-05",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
        _svc("2024-07-03", "2024-07-05", "1720455278680"),
        (
            '{"groupCode":"ZN","eventDate":"2024-07-04","events":[{"tradingDate":"2024-07-05",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2024-07-05",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
    ),
    date(2024, 9, 2): Citation(
        _svc("2024-09-01", "2024-09-03", "1720455278683"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2024-09-02","events":[{"tradingDate":"2024-09-03",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2024-09-03",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
        _svc("2024-09-01", "2024-09-03", "1720455278683"),
        (
            '{"groupCode":"ZN","eventDate":"2024-09-02","events":[{"tradingDate":"2024-09-03",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2024-09-03",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
    ),
    date(2024, 11, 28): Citation(
        _svc("2024-11-27", "2024-11-29", "1720455278685"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2024-11-28","events":[{"tradingDate":"2024-11-29",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2024-11-29",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
        _svc("2024-11-27", "2024-11-29", "1720455278685"),
        (
            '{"groupCode":"ZN","eventDate":"2024-11-28","events":[{"tradingDate":"2024-11-29",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2024-11-29",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
    ),
    date(2024, 11, 29): Citation(
        _svc("2024-11-27", "2024-11-29", "1720455278685"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2024-11-29","events":[{"tradingDate":"2024-11-29",'
            '"eventTime":"12:15","marketEventType":"closed"}]}'
        ),
        _svc("2024-11-27", "2024-11-29", "1720455278685"),
        (
            '{"groupCode":"ZN","eventDate":"2024-11-29","events":[{"tradingDate":"2024-11-29",'
            '"eventTime":"12:15","marketEventType":"closed"}]}'
        ),
    ),
    date(2024, 12, 24): Citation(
        _svc("2024-12-24", "2024-12-26", "1720455278686"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2024-12-24","events":[{"tradingDate":"2024-12-24",'
            '"eventTime":"12:15","marketEventType":"closed"}]}'
        ),
        _svc("2024-12-24", "2024-12-26", "1720455278686"),
        (
            '{"groupCode":"ZN","eventDate":"2024-12-24","events":[{"tradingDate":"2024-12-24",'
            '"eventTime":"12:15","marketEventType":"closed"}]}'
        ),
    ),
    date(2024, 12, 25): Citation(
        _svc("2024-12-24", "2024-12-26", "1720455278686"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2024-12-24","events":[{"tradingDate":"2024-12-24",'
            '"eventTime":"12:15","marketEventType":"closed"}]} ... {"groupCode":"ZN",'
            '"eventDate":"2024-12-25","events":[{"tradingDate":"2024-12-26","eventTime":"16:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2024-12-26","eventTime":"17:00",'
            '"marketEventType":"open"}]}'
        ),
    ),
    date(2025, 1, 1): Citation(
        _svc("2024-12-31", "2025-01-02", "1720455278688"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2024-12-31","events":[{"tradingDate":"2024-12-31",'
            '"eventTime":"16:00","marketEventType":"closed"}]} ... {"groupCode":"ZN",'
            '"eventDate":"2025-01-01","events":[{"tradingDate":"2025-01-02","eventTime":"16:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2025-01-02","eventTime":"17:00",'
            '"marketEventType":"open"}]}'
        ),
    ),
    date(2025, 1, 9): Citation(
        _TH + "day-of-mourning-january-9-2024.pdf",
        (
            "U.S. National Day of Mourning Trading Schedule for Globex, BrokerTec, EBS and "
            "Trading Floor ... PRODUCT NAME JANUARY 9, 2025 TRADING FLOOR CLEARPORT ... CME "
            "GROUP INTEREST RATE EARLY CLOSE – 12:15 PM CT EARLY CLOSE – 12:00 PM CT NORMAL "
            "HOURS"
        ),
        _TH + "day-of-mourning-january-9-2024.pdf",
        "CME GROUP INTEREST RATE EARLY CLOSE – 12:15 PM CT EARLY CLOSE – 12:00 PM CT NORMAL HOURS",
        note=(
            "CME's schedule: Globex rates 'EARLY CLOSE – 12:15 PM CT' (12:00 PM CT is the "
            "trading floor column); the 17:00 CT reopen is not stated (regular reopen assumed)."
        ),
    ),
    date(2025, 1, 20): Citation(
        _svc("2025-01-19", "2025-01-21", "1734710019539"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2025-01-20","events":[{"tradingDate":"2025-01-21",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2025-01-21",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
        _svc("2025-01-19", "2025-01-21", "1734710019539"),
        (
            '{"groupCode":"ZN","eventDate":"2025-01-20","events":[{"tradingDate":"2025-01-21",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2025-01-21",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
    ),
    date(2025, 2, 17): Citation(
        _svc("2025-02-16", "2025-02-18", "1734710019540"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2025-02-17","events":[{"tradingDate":"2025-02-18",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2025-02-18",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
        _svc("2025-02-16", "2025-02-18", "1734710019540"),
        (
            '{"groupCode":"ZN","eventDate":"2025-02-17","events":[{"tradingDate":"2025-02-18",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2025-02-18",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
    ),
    date(2025, 4, 18): Citation(
        _svc("2025-04-17", "2025-04-19", "1734710019542"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2025-04-17","events":[{"tradingDate":"2025-04-17",'
            '"eventTime":"16:00","marketEventType":"closed"}]} ... {"groupCode":"ZN",'
            '"eventDate":"2025-04-18","events":[]}'
        ),
        note="ZN record: 2025-04-17 closed 16:00 with no evening reopen; no events on 2025-04-18.",
    ),
    date(2025, 5, 26): Citation(
        _svc("2025-05-25", "2025-05-27", "1734710019543"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2025-05-26","events":[{"tradingDate":"2025-05-27",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2025-05-27",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
        _svc("2025-05-25", "2025-05-27", "1734710019543"),
        (
            '{"groupCode":"ZN","eventDate":"2025-05-26","events":[{"tradingDate":"2025-05-27",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2025-05-27",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
    ),
    date(2025, 6, 19): Citation(
        _svc("2025-06-18", "2025-06-20", "1734710019544"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2025-06-19","events":[{"tradingDate":"2025-06-20",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2025-06-20",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
        _svc("2025-06-18", "2025-06-20", "1734710019544"),
        (
            '{"groupCode":"ZN","eventDate":"2025-06-19","events":[{"tradingDate":"2025-06-20",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2025-06-20",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
    ),
    date(2025, 7, 4): Citation(
        _svc("2025-07-03", "2025-07-05", "1734710019545"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2025-07-03","events":[{"tradingDate":"2025-07-03",'
            '"eventTime":"16:00","marketEventType":"closed"},{"tradingDate":"2025-07-04",'
            '"eventTime":"16:45","marketEventType":"preopen"},{"tradingDate":"2025-07-04",'
            '"eventTime":"17:00","marketEventType":"open"}]} ... {"groupCode":"ZN",'
            '"eventDate":"2025-07-04","events":[{"tradingDate":"2025-07-04","eventTime":"12:00",'
            '"marketEventType":"closed"}]}'
        ),
        _svc("2025-07-03", "2025-07-05", "1734710019545"),
        (
            '{"groupCode":"ZN","eventDate":"2025-07-04","events":[{"tradingDate":"2025-07-04",'
            '"eventTime":"12:00","marketEventType":"closed"}]}'
        ),
        note="A Friday: the next open is Sunday 17:00 CT.",
    ),
    date(2025, 9, 1): Citation(
        _svc("2025-08-31", "2025-09-02", "1734710019546"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2025-09-01","events":[{"tradingDate":"2025-09-02",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2025-09-02",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
        _svc("2025-08-31", "2025-09-02", "1734710019546"),
        (
            '{"groupCode":"ZN","eventDate":"2025-09-01","events":[{"tradingDate":"2025-09-02",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2025-09-02",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
    ),
    date(2025, 11, 27): Citation(
        _svc("2025-11-26", "2025-11-28", "1734710019547"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2025-11-27","events":[{"tradingDate":"2025-11-28",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2025-11-28",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
        _svc("2025-11-26", "2025-11-28", "1734710019547"),
        (
            '{"groupCode":"ZN","eventDate":"2025-11-27","events":[{"tradingDate":"2025-11-28",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2025-11-28",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
    ),
    date(2025, 11, 28): Citation(
        _svc("2025-11-26", "2025-11-28", "1734710019547"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28",'
            '"eventTime":"12:15","marketEventType":"closed"}]}'
        ),
        _svc("2025-11-26", "2025-11-28", "1734710019547"),
        (
            '{"groupCode":"ZN","eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28",'
            '"eventTime":"12:15","marketEventType":"closed"}]}'
        ),
        note=(
            "Planned schedule (capture 2024-12-20). An unscheduled outage stopped trading until "
            "07:30 CT this trade date: LATE_OPENS."
        ),
    ),
    date(2025, 12, 24): Citation(
        _svc("2025-12-24", "2025-12-26", "1769649703064"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2025-12-24","events":[{"tradingDate":"2025-12-24",'
            '"eventTime":"12:15","marketEventType":"closed"}]}'
        ),
        _svc("2025-12-24", "2025-12-26", "1769649703064"),
        (
            '{"groupCode":"ZN","eventDate":"2025-12-24","events":[{"tradingDate":"2025-12-24",'
            '"eventTime":"12:15","marketEventType":"closed"}]}'
        ),
        note=(
            "ZN record captured 2026-01-29, after the date (the 2024-12-20 capture had no "
            "events yet)."
        ),
    ),
    date(2025, 12, 25): Citation(
        _svc("2025-12-24", "2025-12-26", "1769649703064"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2025-12-24","events":[{"tradingDate":"2025-12-24",'
            '"eventTime":"12:15","marketEventType":"closed"}]} ... {"groupCode":"ZN",'
            '"eventDate":"2025-12-25","events":[{"tradingDate":"2025-12-26","eventTime":"16:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2025-12-26","eventTime":"17:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "ZN record captured 2026-01-29, after the date (the 2024-12-20 capture had no "
            "events yet)."
        ),
    ),
    date(2026, 1, 1): Citation(
        _svc("2025-12-31", "2026-01-02", "1769649703066"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2025-12-31","events":[{"tradingDate":"2025-12-31",'
            '"eventTime":"16:00","marketEventType":"closed"}]} ... {"groupCode":"ZN",'
            '"eventDate":"2026-01-01","events":[{"tradingDate":"2026-01-02","eventTime":"16:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2026-01-02","eventTime":"17:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "ZN record captured 2026-01-29, after the date (the 2024-12-20 capture had no "
            "events yet)."
        ),
    ),
    date(2026, 1, 19): Citation(
        _svc("2026-01-18", "2026-01-20", "1769649703068"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2026-01-19","events":[{"tradingDate":"2026-01-20",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2026-01-20",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
        _svc("2026-01-18", "2026-01-20", "1769649703068"),
        (
            '{"groupCode":"ZN","eventDate":"2026-01-19","events":[{"tradingDate":"2026-01-20",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2026-01-20",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
    ),
    date(2026, 2, 16): Citation(
        _svc("2026-02-15", "2026-02-17", "1769649703070"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2026-02-16","events":[{"tradingDate":"2026-02-17",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2026-02-17",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
        _svc("2026-02-15", "2026-02-17", "1769649703070"),
        (
            '{"groupCode":"ZN","eventDate":"2026-02-16","events":[{"tradingDate":"2026-02-17",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2026-02-17",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
    ),
    date(2026, 4, 3): Citation(
        _svc("2026-04-01", "2026-04-03", "1769649703072"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2026-04-02","events":[{"tradingDate":"2026-04-02",'
            '"eventTime":"16:00","marketEventType":"closed"},{"tradingDate":"2026-04-03",'
            '"eventTime":"16:45","marketEventType":"preopen"},{"tradingDate":"2026-04-03",'
            '"eventTime":"17:00","marketEventType":"open"}]} ... {"groupCode":"ZN",'
            '"eventDate":"2026-04-03","events":[{"tradingDate":"2026-04-03","eventTime":"10:15",'
            '"marketEventType":"closed"}]}'
        ),
        _svc("2026-04-01", "2026-04-03", "1769649703072"),
        (
            '{"groupCode":"ZN","eventDate":"2026-04-03","events":[{"tradingDate":"2026-04-03",'
            '"eventTime":"10:15","marketEventType":"closed"}]}'
        ),
        note=(
            "Jobs-report Good Friday: Thursday 17:00 CT reopen for this trade date, close 10:15 "
            "CT."
        ),
    ),
    date(2026, 5, 25): Citation(
        _svc("2026-05-24", "2026-05-26", "1769649703074"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2026-05-25","events":[{"tradingDate":"2026-05-26",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2026-05-26",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
        _svc("2026-05-24", "2026-05-26", "1769649703074"),
        (
            '{"groupCode":"ZN","eventDate":"2026-05-25","events":[{"tradingDate":"2026-05-26",'
            '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2026-05-26",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
    ),
    date(2026, 6, 19): Citation(
        _svc("2026-06-17", "2026-06-19", "1769649703075"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2026-06-18","events":[{"tradingDate":"2026-06-18",'
            '"eventTime":"16:00","marketEventType":"closed"},{"tradingDate":"2026-06-22",'
            '"eventTime":"16:45","marketEventType":"preopen"},{"tradingDate":"2026-06-22",'
            '"eventTime":"17:00","marketEventType":"open"}]} ... {"groupCode":"ZN",'
            '"eventDate":"2026-06-19","events":[{"tradingDate":"2026-06-22","eventTime":"12:00",'
            '"marketEventType":"closed"}]}'
        ),
        _svc("2026-06-17", "2026-06-19", "1769649703075"),
        (
            '{"groupCode":"ZN","eventDate":"2026-06-19","events":[{"tradingDate":"2026-06-22",'
            '"eventTime":"12:00","marketEventType":"closed"}]}'
        ),
        note="CME books this session to trade date 2026-06-22; kept as its own trade date here.",
    ),
}

LATE_OPEN_SOURCES: dict[date, Citation] = {
    date(2025, 11, 28): Citation(
        _svc("2025-11-26", "2025-11-28", "1769649703060"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28",'
            '"eventTime":"07:00","marketEventType":"preopen"},{"tradingDate":"2025-11-28",'
            '"eventTime":"07:30","marketEventType":"open"},{"tradingDate":"2025-11-28",'
            '"eventTime":"12:15","marketEventType":"closed"}]}'
        ),
        note=(
            "Unscheduled: CME Globex outage (data-center cooling failure at CyrusOne) after the "
            "Thursday 2025-11-27 17:00 CT reopen. CME's ZN service record for eventDate "
            "2025-11-28 in the 2026-01-29 capture adds 'preopen' 07:00 and 'open' 07:30 before "
            "the scheduled 12:15 close; the 2024-12-20 capture (the planned schedule, used for "
            "the HOLIDAYS entry) has only the 12:15 close. The halt start is not in any CME "
            "document retrieved: CNBC reports CME saying markets 'were halted due to a cooling "
            "issue' (secondary, see extra_evidence). The same outage hit every CME Globex group,"
            " including equities (data/cme_calendar.py does not record it)."
        ),
    ),
}

# CME-stated regular Globex days near holidays, kept so the absence of an entry is a recorded
# finding, not an oversight.
NO_ENTRY_FINDINGS: dict[date, Citation] = {
    date(2019, 5, 24): Citation(
        _Z19,
        (
            "Updated 4/29/2019|CME Group Globex Memorial Day Holiday Schedule: May 24, 2019 - "
            "May 28, 2019 ... Calendar Date|Friday, May 24||Sunday, May 26|||||Monday, May "
            "27|||||||Tuesday, May 28 ... Interest Rate Products|04:00:00 PM||04:00:00 "
            "PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-memorial-day-schedule.xls. Interest Rate "
            "Products 'Regular Fri. Close' 16:00 on Friday May 24. CME's settlement notice "
            "gives 'CME Group Interest Rate Products 12:00:00 CT' that day (see "
            "EARLY_SETTLEMENT_CT)."
        ),
    ),
    date(2019, 7, 3): Citation(
        _Z19,
        (
            "Updated 6/6/2019|CME Group Globex Independence Day Holiday Schedule: July 3, 2019 "
            "to July 5, 2019 ... Calendar Date|Wednesday, July 3||||||||Thursday, July "
            "4||||||||Friday, July 5 ... Interest Rate Products|04:00:00 PM|||04:45:00 "
            "PM|05:00:00 PM||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-independence-day-schedule.xls. Interest "
            "Rate Products 'Regular Close' 16:00 on Wednesday July 3 (equities closed early at "
            "12:15). CME's settlement notice for the day gives 'Interest Rate Products 12:00:00 "
            "CT' (see EARLY_SETTLEMENT_CT)."
        ),
    ),
    date(2019, 10, 14): Citation(
        _Z19,
        (
            "Monday, October 14, 2019 Settlement Times All products will settle at their normal "
            "times for the Columbus Day Holiday"
        ),
        note=(
            "Zip member settlement-notices/2019-columbus-day-holiday-settlement-times.pdf. "
            "Columbus Day is a bond-market (SIFMA) holiday but not a CME holiday: CME settles "
            "every product at its normal time and published no Globex holiday schedule for it. "
            "Later years not re-fetched."
        ),
    ),
    date(2019, 11, 11): Citation(
        _Z19,
        (
            "Monday, November 11, 2019 Settlement Times All products will settle at their "
            "normal times for the Veterans Day Holiday"
        ),
        note=(
            "Zip member settlement-notices/2019-veterans-day-holiday-settlement-times.pdf. "
            "Veterans Day is a bond-market (SIFMA) holiday but not a CME holiday: CME settles "
            "every product at its normal time and published no Globex holiday schedule for it. "
            "Later years not re-fetched."
        ),
    ),
    date(2019, 12, 31): Citation(
        _Z19,
        (
            "Updated 10/01/2019|CME Group Globex New Years Holiday Schedule: December 31, 2019 "
            "- January 2, 2020 ... Calendar Date|Tuesday, December 31|Wednesday, January "
            "1|Wednesday, January 1||||||Thursday, Jan 2 ... Interest Rate Products|04:00:00 "
            "PM|Globex Closed|04:00:00 PM|05:00:00 PM|||||||04:00:00 PM"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-2020-new-years-holiday-schedule.xls. "
            "Interest Rate Products 'Close' 16:00 on Tuesday December 31. CME's settlement "
            "notice gives 'CME Group Interest Rate Products 12:00:00 CT' (see "
            "EARLY_SETTLEMENT_CT)."
        ),
    ),
    date(2020, 4, 9): Citation(
        _Z20,
        (
            "Updated 4/6/2020|CME Group Globex Good Friday Holiday Schedule: April 9, 2020 to "
            "April 13, 2020 ... Calendar Date|Thursday, April 9||||||Friday, April 10|||Sunday, "
            "April 12|||||Monday, April 13 ... Interest Rate Products|04:00:00 PM||||||Globex "
            "Closed|||04:00:00 PM|05:00:00 PM"
        ),
        note=(
            "Zip member 2020-good-friday-schedule.xls. Interest Rate Products 'Regular Close' "
            "16:00 on Thursday April 9, before the Good Friday closure."
        ),
    ),
    date(2020, 5, 22): Citation(
        _Z20,
        (
            "Updated 4/21/2020|CME Group Globex Memorial Day Holiday Schedule: May 22, 2020 - "
            "May 26, 2020 ... Calendar Date|Friday, May 22||Sunday, May 24|||||Monday, May "
            "25|||||||Tuesday, May 26 ... Interest Rate Products|04:00:00 PM||04:00:00 "
            "PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
        ),
        note=(
            "Zip member 2020-memorial-day-schedule.xls. Interest Rate Products 'Regular Fri. "
            "Close' 16:00 on Friday May 22."
        ),
    ),
    date(2020, 7, 2): Citation(
        _Z20,
        (
            "Updated 6/26/2020|CME Group Globex Independence Day Holiday Schedule: July 2, 2020 "
            "to July 6, 2020 ... Calendar Date|Thursday, July 2||||||||Friday, July 3|||Sunday, "
            "July 5|||||Monday, July 6 ... Interest Rate Products|04:00:00 PM|||04:45:00 "
            "PM|05:00:00 PM||||||12:00:00 PM|04:00:00 PM|05:00:00 PM"
        ),
        note=(
            "Zip member 2020-independence-day-schedule.xls. Interest Rate Products 'Regular "
            "Close' 16:00 on Thursday July 2."
        ),
    ),
    date(2020, 12, 31): Citation(
        _Z20,
        (
            "Updated 12/09/2020|CME Group Globex New Years Holiday Schedule: December 31, 2020 "
            "- January 4, 2021 ... Calendar Date|Thursday, December 31|Friday, January 1|Sunday,"
            " January 3||||||Monday, January 4 ... Interest Rate Products|04:00:00 PM|Globex "
            "Closed|04:00:00 PM|05:00:00 PM|||||||04:00:00 PM"
        ),
        note=(
            "Zip member 2021-new-years-holiday-schedule.xls. Interest Rate Products 'Close' "
            "16:00 on Thursday December 31."
        ),
    ),
    date(2021, 4, 1): Citation(
        _Z21,
        (
            "Updated 3/31/2021|CME Group Globex Good Friday Holiday Schedule: April 1, 2021 to "
            "April 5, 2021 ... Calendar Date|Thursday, April 1||||||Friday, April 2|||Sunday, "
            "April 4|||||Monday, April 5 ... Interest Rate Products|04:00:00 PM|||04:45:00 "
            "PM|05:00:00 PM||||10:15:00 AM|04:00:00 PM|05:00:00 PM"
        ),
        note=(
            "Zip member 2021-good-friday-holiday-schedule.xls. Interest Rate Products 'Regular "
            "Close' 16:00 on Thursday April 1 (then reopen 17:00 for the abbreviated Friday "
            "April 2 session)."
        ),
    ),
    date(2021, 5, 28): Citation(
        _Z21,
        (
            "Updated 5/25/2021|CME Group Globex Memorial Day Holiday Schedule: May 28, 2021 - "
            "Jun 1, 2021 ... Calendar Date|Friday, May 28||Sunday, May 30|||||Monday, May "
            "31|||||||Tuesday, Jun 1 ... Interest Rate Products|04:00:00 PM||04:00:00 "
            "PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
        ),
        note=(
            "Zip member 2021-memorial-day-holiday-schedule.xls. Interest Rate Products 'Regular "
            "Fri. Close' 16:00 on Friday May 28."
        ),
    ),
    date(2021, 7, 2): Citation(
        _Z21,
        (
            "Updated 7/1/2021|CME Group Globex Independence Day Holiday Schedule: July 2, 2021 "
            "to July 6, 2021 ... Calendar Date|Friday, July 2||Sunday, July 4|||||Monday, July "
            "5||||||Tuesday, July 6 ... Interest Rate Products|04:00:00 PM||04:00:00 "
            "PM|05:00:00 PM||||||12:00:00 PM|12:00:00 PM|05:00:00 PM"
        ),
        note=(
            "Zip member 2021-independence-day-holiday-schedule.xls. Interest Rate Products "
            "'Regular Close' 16:00 on Friday July 2."
        ),
    ),
    date(2021, 12, 23): Citation(
        _Z21,
        (
            "Updated 12/01/2021|CME Group Globex Christmas Holiday Schedule: December 24, 2021 "
            "- December 27, 2021 ... Calendar Date|Thursday, December 23|||||||||||||Friday, "
            "December 24||||||||||Sunday, December 26||||||Monday, Dec 27 ... Interest Rate "
            "Products|04:00:00 PM|||||||||||||Globex Closed||||||||||04:00:00 PM|05:00:00 "
            "PM|||||||04:00:00 PM"
        ),
        note=(
            "Zip member 2021-christmas-holiday-schedule.xls. Globex 'Interest Rate Products' "
            "regular close 16:00; the sheet's 'Treasuries TAS' exception closes at 12:00, i.e. "
            "CME's Treasury settlement was early that day."
        ),
    ),
    date(2021, 12, 31): Citation(
        _Z21,
        (
            "Updated 12/28/2021|CME Group Globex New Year's Holiday Schedule: December 30, 2021 "
            "- January 3, 2022 ... Calendar Date|Thursday, December 30||||||||||Friday, "
            "December 31||||||||Sunday, January 2||||||Monday, January 3 ... Interest Rate "
            "Products|04:00:00 PM|04:45:00 PM|05:00:00 PM|||||||||||04:00:00 PM|||||04:00:00 "
            "PM|05:00:00 PM|NORMAL||||SCHEDULE"
        ),
        note=(
            "Zip member 2022-new-years-holiday-schedule.xls. Globex 'Interest Rate Products' "
            "regular close 16:00; the sheet's 'Treasuries TAS' exception closes at 12:00, i.e. "
            "CME's Treasury settlement was early that day."
        ),
    ),
    date(2022, 1, 3): Citation(
        _Z21,
        (
            "Updated 12/28/2021|CME Group Globex New Year's Holiday Schedule: December 30, 2021 "
            "- January 3, 2022 ... Calendar Date|Thursday, December 30||||||||||Friday, "
            "December 31||||||||Sunday, January 2||||||Monday, January 3 ... Interest Rate "
            "Products|04:00:00 PM|04:45:00 PM|05:00:00 PM|||||||||||04:00:00 PM|||||04:00:00 "
            "PM|05:00:00 PM|NORMAL||||SCHEDULE"
        ),
        note=(
            "Zip member 2022-new-years-holiday-schedule.xls. January 1, 2022 fell on a "
            "Saturday; the sheet shows 'NORMAL' 'SCHEDULE' for Monday January 3 (no weekday "
            "closure)."
        ),
    ),
    date(2022, 4, 14): Citation(
        _HC + "2022-good-friday-holiday-schedule.xls",
        (
            "Updated 3/17/2022|CME Group Globex Good Friday Holiday Schedule: April 14, 2022 to "
            "April 18, 2022 ... Calendar Date|Thursday, April 14|||||||||Friday, April "
            "15|||Sunday, April 17|||||Monday, April 18 ... Interest Rate Products|04:00:00 "
            "PM|||||||||Globex Closed|||04:00:00 PM|05:00:00 PM"
        ),
        note=(
            "Globex 'Interest Rate Products' regular close 16:00; the sheet's 'Treasuries TAS' "
            "exception closes at 12:00, i.e. CME's Treasury settlement was early that day."
        ),
    ),
    date(2022, 5, 27): Citation(
        _HC + "2022-memorial-day-holiday-schedule.xls",
        (
            "Updated 5/18/2022|CME Group Globex Memorial Day Holiday Schedule: May 27, 2022 - "
            "May 31, 2022 ... Calendar Date|Friday, May 27|||||Sunday, May 29|||||Monday, May "
            "30||||||||||Tuesday, May 31 ... Interest Rate Products|04:00:00 PM|||||04:00:00 "
            "PM|05:00:00 PM|||||||12:00:00 PM||||12:00:00 PM|05:00:00 PM"
        ),
        note=(
            "Globex 'Interest Rate Products' regular close 16:00; the sheet's 'Treasuries TAS' "
            "exception closes at 12:00, i.e. CME's Treasury settlement was early that day."
        ),
    ),
    date(2022, 7, 1): Citation(
        _HC + "2022-independence-day-holiday-schedule.xls",
        (
            "Updated 6/29/2022|CME Group Globex Independence Day Holiday Schedule: July 1, 2022 "
            "to July 5, 2022 ... Calendar Date|Friday, July 1|||||Sunday, July 3|||||Monday, "
            "July 4|||||||||||Tuesday, July 5 ... Interest Rate Products|04:00:00 "
            "PM|||||04:00:00 PM|05:00:00 PM||||||12:00:00 PM||||12:00:00 PM|05:00:00 PM"
        ),
        note=(
            "Globex 'Interest Rate Products' regular close 16:00; the sheet's 'Treasuries TAS' "
            "exception closes at 12:00, i.e. CME's Treasury settlement was early that day."
        ),
    ),
    date(2022, 12, 23): Citation(
        _HC + "2022-christmas-holiday-schedule.xls",
        (
            "Updated 6/29/2022|CME Group Globex Christmas Holiday Schedule: December 23, 2022 - "
            "December 27, 2022 ... Calendar Date|Friday, December 23||||||||Monday, December "
            "26||||||||||||||||Tuesday, December 27 ... Interest Rate Products|04:00:00 "
            "PM||||||||Globex Closed||||||||||04:00:00 PM|05:00:00 PM|||||||04:00:00 PM"
        ),
        note=(
            "Globex 'Interest Rate Products' regular close 16:00; the sheet's 'Treasuries TAS' "
            "exception closes at 12:00, i.e. CME's Treasury settlement was early that day. "
            "Schedule sheet 'Updated 6/29/2022', Wayback capture 2022-07-04, months before the "
            "holiday; no later capture was retrieved, so a later CME revision cannot be "
            "excluded."
        ),
    ),
    date(2022, 12, 30): Citation(
        _HC + "2023-new-years-holiday-schedule.xls",
        (
            "Updated 6/29/22|CME Group Globex New Year's Holiday Schedule: December 30, 2022 - "
            "January 3, 2023 ... Calendar Date|Friday, December 30||||Monday, January 2|Monday, "
            "January 2||||||Tuesday, January 3 ... Interest Rate Products|04:00:00 PM||||Globex "
            "Closed|04:00:00 PM|05:00:00 PM"
        ),
        note=(
            "Globex 'Interest Rate Products' regular close 16:00; the sheet's 'Treasuries TAS' "
            "exception closes at 12:00, i.e. CME's Treasury settlement was early that day. "
            "Schedule sheet 'Updated 6/29/22', Wayback capture 2022-07-04, months before the "
            "holiday; no later capture was retrieved, so a later CME revision cannot be "
            "excluded."
        ),
    ),
    date(2023, 7, 3): Citation(
        _TH + "4th-of-july-2023.pdf",
        (
            "PRODUCT NAME MONDAY, 3 JULY 2023 TUESDAY, 4 JULY 2023 WEDNESDAY, 5 JULY 2023 ... "
            "PREOPEN (HALT): Order Entry, TRADE DATE: MON 3 JULY TRADE DATE: WED 5 JULY "
            "modification, and cancel are allowed. 16:00 (CLOSED) 16:00 (CLOSED)"
        ),
        note=(
            "Layout read: the INTEREST RATE row's Monday 3 July cell is 'TRADE DATE: MON 3 JULY "
            "16:00 (CLOSED)', then 'TRADE DATE: WED 5 JULY 16:45 (PREOPEN) 17:00 (OPEN)'; the "
            "EQUITIES row's Monday cell is '12:15 (CLOSED)'. Interest rates closed at their "
            "regular 16:00."
        ),
    ),
    date(2024, 3, 28): Citation(
        _svc("2024-03-28", "2024-03-30", "1720455278672"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2024-03-28","events":[{"tradingDate":"2024-03-28",'
            '"eventTime":"16:00","marketEventType":"closed"}]}'
        ),
        note="ZN closed 16:00 (regular) on Thursday March 28, before the Good Friday closure.",
    ),
    date(2024, 7, 3): Citation(
        _svc("2024-07-03", "2024-07-05", "1720455278680"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2024-07-03","events":[{"tradingDate":"2024-07-03",'
            '"eventTime":"16:00","marketEventType":"closed"},{"tradingDate":"2024-07-05",'
            '"eventTime":"16:45","marketEventType":"preopen"},{"tradingDate":"2024-07-05",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
        note=(
            "ZN closed 16:00 (regular) on Wednesday July 3 and reopened 17:00 for trade date "
            "July 5 (equities closed early at 12:15)."
        ),
    ),
    date(2024, 12, 31): Citation(
        _svc("2024-12-31", "2025-01-02", "1720455278688"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2024-12-31","events":[{"tradingDate":"2024-12-31",'
            '"eventTime":"16:00","marketEventType":"closed"}]}'
        ),
        note="ZN closed 16:00 (regular) on Tuesday December 31.",
    ),
    date(2025, 4, 17): Citation(
        _svc("2025-04-17", "2025-04-19", "1734710019542"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2025-04-17","events":[{"tradingDate":"2025-04-17",'
            '"eventTime":"16:00","marketEventType":"closed"}]}'
        ),
        note="ZN closed 16:00 (regular) on Thursday April 17, before the Good Friday closure.",
    ),
    date(2025, 7, 3): Citation(
        _svc("2025-07-03", "2025-07-05", "1734710019545"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2025-07-03","events":[{"tradingDate":"2025-07-03",'
            '"eventTime":"16:00","marketEventType":"closed"},{"tradingDate":"2025-07-04",'
            '"eventTime":"16:45","marketEventType":"preopen"},{"tradingDate":"2025-07-04",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
        note=(
            "ZN closed 16:00 (regular) on Thursday July 3 and reopened 17:00 for trade date "
            "July 4."
        ),
    ),
    date(2025, 12, 31): Citation(
        _svc("2025-12-31", "2026-01-02", "1769649703066"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2025-12-31","events":[{"tradingDate":"2025-12-31",'
            '"eventTime":"16:00","marketEventType":"closed"}]}'
        ),
        note=(
            "ZN closed 16:00 (regular) on Wednesday December 31. ZN service capture 2026-01-29 "
            "(after the date); the 2024-12-20 capture of the same range returned no events yet."
        ),
    ),
    date(2026, 4, 2): Citation(
        _svc("2026-04-01", "2026-04-03", "1769649703072"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2026-04-02","events":[{"tradingDate":"2026-04-02",'
            '"eventTime":"16:00","marketEventType":"closed"},{"tradingDate":"2026-04-03",'
            '"eventTime":"16:45","marketEventType":"preopen"},{"tradingDate":"2026-04-03",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
        note=(
            "ZN closed 16:00 (regular) on Thursday April 2 and reopened 17:00 for the "
            "abbreviated Good Friday session."
        ),
    ),
    date(2026, 6, 18): Citation(
        _svc("2026-06-17", "2026-06-19", "1769649703075"),
        (
            '"globex":"ZN","prodGroup":"ZN","name":"10-Year T-Note Futures","id":316 ... '
            '{"groupCode":"ZN","eventDate":"2026-06-18","events":[{"tradingDate":"2026-06-18",'
            '"eventTime":"16:00","marketEventType":"closed"},{"tradingDate":"2026-06-22",'
            '"eventTime":"16:45","marketEventType":"preopen"},{"tradingDate":"2026-06-22",'
            '"eventTime":"17:00","marketEventType":"open"}]}'
        ),
        note=(
            "ZN closed 16:00 (regular) on Thursday June 18 and reopened 17:00 (trading date "
            "2026-06-22)."
        ),
    ),
}

# CME-published rates settlement times other than the regular 14:00 CT (for the lead's D6
# ruling; Globex hours on these days are in HOLIDAYS or NO_ENTRY_FINDINGS).
EARLY_SETTLEMENT_CT: dict[date, time] = {
    date(2019, 5, 24): time(12, 0),
    date(2019, 7, 3): time(12, 0),
    date(2019, 11, 29): time(12, 0),
    date(2019, 12, 24): time(12, 0),
    date(2019, 12, 31): time(12, 0),
    date(2020, 4, 9): time(12, 0),
    date(2020, 5, 22): time(12, 0),
    date(2020, 7, 2): time(12, 0),
    date(2020, 11, 27): time(12, 0),
    date(2020, 12, 31): time(12, 0),
    date(2021, 4, 2): time(10, 0),
    date(2021, 5, 28): time(12, 0),
    date(2021, 7, 2): time(12, 0),
    date(2021, 11, 26): time(12, 0),
    date(2021, 12, 23): time(12, 0),
    date(2021, 12, 31): time(12, 0),
    date(2022, 4, 14): time(12, 0),
    date(2022, 5, 27): time(12, 0),
    date(2022, 7, 1): time(12, 0),
    date(2022, 11, 25): time(12, 0),
    date(2022, 12, 23): time(12, 0),
    date(2022, 12, 30): time(12, 0),
    date(2023, 4, 7): time(10, 0),
    date(2023, 5, 26): time(12, 0),
    date(2023, 7, 3): time(12, 0),
    date(2023, 11, 24): time(12, 0),
    date(2023, 12, 22): time(12, 0),
    date(2023, 12, 29): time(12, 0),
    date(2024, 3, 28): time(12, 0),
    date(2024, 5, 24): time(12, 0),
    date(2024, 7, 3): time(12, 0),
    date(2024, 11, 29): time(12, 0),
    date(2024, 12, 24): time(12, 0),
    date(2024, 12, 31): time(12, 0),
    date(2025, 4, 17): time(12, 0),
    date(2025, 5, 23): time(12, 0),
    date(2025, 7, 3): time(12, 0),
    date(2025, 11, 28): time(12, 0),
    date(2025, 12, 24): time(12, 0),
    date(2025, 12, 31): time(12, 0),
    date(2026, 5, 22): time(12, 0),
}
EARLY_SETTLEMENT_SOURCES: dict[date, Citation] = {
    date(2019, 5, 24): Citation(
        _Z19,
        (
            "Memorial Day (5/27/2019) Settlement Times Friday, May 24, 2019 CME Group Interest "
            "Rate Products 12:00:00 CT"
        ),
        note=(
            "Zip member settlement-notices/2019-memorial-day-holiday-settlement-times.pdf. "
            "Globex regular close 16:00 (no entry)."
        ),
    ),
    date(2019, 7, 3): Citation(
        _Z19,
        "Wednesday, July 3, 2019 Settlement Times ... Interest Rate Products 12:00:00 CT",
        note=(
            "Zip member settlement-notices/2019-fourth-of-july-holiday-settlement-times.pdf. "
            "Globex regular close 16:00 (no entry)."
        ),
    ),
    date(2019, 11, 29): Citation(
        _Z19,
        (
            "Friday, 11/29/2019 (the day after Thanksgiving) Settlement Times ... Interest Rate "
            "Products 12:00:00 CT"
        ),
        note=(
            "Zip member settlement-notices/2019-thanksgiving-holiday-settlement-times.pdf. "
            "Early close 12:15 (HOLIDAYS)."
        ),
    ),
    date(2019, 12, 24): Citation(
        _Z19,
        "Tuesday, 12/24/2019 ... Interest Rate Products 12:00:00 CT",
        note=(
            "Zip member settlement-notices/2019-christmas-holiday-settlement-times.pdf. Early "
            "close 12:15 (HOLIDAYS)."
        ),
    ),
    date(2019, 12, 31): Citation(
        _Z19,
        "Tuesday, 12/31/2019 CME Group Interest Rate Products 12:00:00 CT",
        note=(
            "Zip member settlement-notices/2019-new-years-eve-holiday-settlement-times.pdf. "
            "Globex regular close 16:00 (no entry). The same notice gives 12:01 CT for the "
            "expiring December 2-year and 5-year contracts."
        ),
    ),
    date(2020, 4, 9): Citation(
        _HC + "good-friday-holiday-settlement-times-2020.pdf",
        (
            "Thursday, 4/9/2020 Settlement Times CME Group FX Products 12:00 pm CT CME Group "
            "Interest Rate Products 12:00 pm CT"
        ),
        note="Globex regular close 16:00 (no entry).",
    ),
    date(2020, 5, 22): Citation(
        _HC + "memorial-day-holiday-settlement-times-2020.pdf",
        "Friday, May 22, 2020 CME Group Interest Rate Products 12:00:00 CT",
        note="Globex regular close 16:00 (no entry).",
    ),
    date(2020, 7, 2): Citation(
        _HC + "fourth-of-july-settlement-times-2020.pdf",
        (
            "Thursday, July 2, 2020 Settlement Times Agricultural Products 12:00:00 CT Interest "
            "Rate Products 12:00:00 CT"
        ),
        note="Globex regular close 16:00 (no entry).",
    ),
    date(2020, 11, 27): Citation(
        _HC + "thanksgiving-holiday-settlement-times-2020.pdf",
        (
            "Friday, 11/27/2020 (the day after Thanksgiving) Settlement Times ... Interest Rate "
            "Products 12:00:00 CT"
        ),
        note="Early close 12:15 (HOLIDAYS).",
    ),
    date(2020, 12, 31): Citation(
        _HC + "new-years-eve-holiday-settlement-times-2020.pdf",
        "Thursday, 12/31/2020 CME Group Interest Rate Products 12:00:00 CT",
        note="Globex regular close 16:00 (no entry).",
    ),
    date(2021, 4, 2): Citation(
        _HC + "good-friday-holiday-settlement-times-2021.pdf",
        (
            "Friday, 4/2/2021 Settlement Times CME Group FX Products 10:00 am CT CME Group "
            "Interest Rate Products 10:00 am CT"
        ),
        note="Jobs-report Good Friday, close 10:15 (HOLIDAYS).",
    ),
    date(2021, 5, 28): Citation(
        _HC + "memorial-day-holiday-settlement-times-2021.pdf",
        "Friday, May 28, 2021 CME Group Interest Rate Products 12:00:00 CT",
        note="Globex regular close 16:00 (no entry).",
    ),
    date(2021, 7, 2): Citation(
        _HC + "fourth-of-july-settlement-times-2021.pdf",
        (
            "Friday, July 2, 2021 Settlement Times Agricultural Products 12:00:00 CT Interest "
            "Rate Products 12:00:00 CT"
        ),
        note="Globex regular close 16:00 (no entry).",
    ),
    date(2021, 11, 26): Citation(
        _HC + "thanksgiving-holiday-settlement-times-2021.pdf",
        (
            "Friday, 11/26/2021 (the day after Thanksgiving) Settlement Times ... Interest Rate "
            "Products 12:00:00 CT"
        ),
        note="Early close 12:15 (HOLIDAYS).",
    ),
    date(2021, 12, 23): Citation(
        _HC + "christmas-holiday-settlement-times-2021.pdf",
        (
            "Thursday, 12/23/2021 Agricultural Products (Grains, Livestock, Dairy, Commodity "
            "Index) 12:00:00 CT Interest Rate Products 12:00:00 CT"
        ),
        note="Globex regular close 16:00 (no entry).",
    ),
    date(2021, 12, 31): Citation(
        _HC + "new-years-eve-holiday-settlement-times-2022.pdf",
        "Friday, 12/31/2021 CME Group Interest Rate Products 12:00:00 CT",
        note="Globex regular close 16:00 (no entry).",
    ),
    date(2022, 4, 14): Citation(
        _HC + "good-friday-holiday-settlement-times-2022.pdf",
        "Thursday, April 14, 2022 CME Group Interest Rate Products 12:00:00 CT",
        note="Globex regular close 16:00 (no entry).",
    ),
    date(2022, 5, 27): Citation(
        _HC + "memorial-day-holiday-settlement-times-2022.pdf",
        "Friday May 27, 2022 CME Group Interest Rate Products 12:00:00 CT",
        note="Globex regular close 16:00 (no entry).",
    ),
    date(2022, 7, 1): Citation(
        _HC + "fourth-of-july-settlement-times-2022.pdf",
        "Friday, July 1, 2022 Settlement Times Interest Rate Products 12:00:00 CT",
        note="Globex regular close 16:00 (no entry).",
    ),
    date(2022, 11, 25): Citation(
        _HC + "thanksgiving-holiday-settlement-times-2022.pdf",
        (
            "Friday, November 25, 2022 (the day after Thanksgiving) Settlement Times ... "
            "Interest Rate Products 12:00:00 CT"
        ),
        note="Early close 12:15 (HOLIDAYS).",
    ),
    date(2022, 12, 23): Citation(
        _HC + "christmas-holiday-settlement-times-2022.pdf",
        "Friday, December 23, 2022 Interest Rate Products 12:00:00 CT",
        note="Globex regular close 16:00 (no entry).",
    ),
    date(2022, 12, 30): Citation(
        _HC + "new-years-eve-holiday-settlement-times-2023.pdf",
        "Friday, December 30, 2022 CME Group Interest Rate Products 12:00:00 CT",
        note="Globex regular close 16:00 (no entry).",
    ),
    date(2023, 4, 7): Citation(
        _HC + "good-friday-holiday-settlement-times-2023.pdf",
        "Friday, April 7, 2023 ... CME Group Interest Rate Products 10:00 am CT",
        note="Abbreviated jobs-report Good Friday (HOLIDAYS, close 10:15 inferred).",
    ),
    date(2023, 5, 26): Citation(
        _HC + "memorial-day-holiday-settlement-times-2023.pdf",
        "Friday, May 26, 2023 CME Group Interest Rate Products 12:00:00 CT",
        note="Globex hours not in any CME document retrieved (GLOBEX_HOURS_UNDOCUMENTED).",
    ),
    date(2023, 7, 3): Citation(
        _HC + "fourth-of-july-settlement-times-2023.pdf",
        "Monday, July 3, 2023 Interest Rate Products 12:00:00 CT",
        note="Globex regular close 16:00 (no entry).",
    ),
    date(2023, 11, 24): Citation(
        _HC + "thanksgiving-holiday-settlement-times-2023.pdf",
        (
            "Friday, November 24, 2023 (the day after Thanksgiving) ... Interest Rate Products "
            "12:00:00 CT"
        ),
        note="Early close 12:15 (HOLIDAYS).",
    ),
    date(2023, 12, 22): Citation(
        _HC + "christmas-holiday-settlement-times-2023.pdf",
        "Friday, December 22, 2023 Interest Rate Products 12:00:00 CT",
        note="Globex hours not in any CME document retrieved (GLOBEX_HOURS_UNDOCUMENTED).",
    ),
    date(2023, 12, 29): Citation(
        _HC + "new-years-eve-holiday-settlement-times-2024.pdf",
        "Friday, December 29, 2023 CME Group Interest Rate Products Settlement Time: 12:00:00 CT",
        note="Globex hours not in any CME document retrieved (GLOBEX_HOURS_UNDOCUMENTED).",
    ),
    date(2024, 3, 28): Citation(
        _HC + "good-friday-holiday-settlement-times-2024.pdf",
        "Thursday, March 28, 2024 CME Group Interest Rate Products Settlement Time: 12:00:00 CT",
        note="Globex regular close 16:00 (no entry).",
    ),
    date(2024, 5, 24): Citation(
        _HC + "memorial-day-holiday-settlement-times-2024.pdf",
        "Friday, May 24, 2024 CME Group Interest Rate Products Settlement Time: 12:00:00 CT",
        note="Globex hours not in any CME document retrieved (GLOBEX_HOURS_UNDOCUMENTED).",
    ),
    date(2024, 7, 3): Citation(
        _HC + "us-independence-day-settlement-times-2024.pdf",
        "Wednesday, July 3, 2024 Interest Rate Products Settlement Time: 12:00:00 CT",
        note="Globex regular close 16:00 (no entry).",
    ),
    date(2024, 11, 29): Citation(
        _HC + "thanksgiving-holiday-settlement-times-2024.pdf",
        (
            "Friday, November 29, 2024 (the day after Thanksgiving) ... Interest Rate Products "
            "Settlement Time: 12:00:00 CT"
        ),
        note="Early close 12:15 (HOLIDAYS).",
    ),
    date(2024, 12, 24): Citation(
        _HC + "christmas-holiday-settlement-times-2024.pdf",
        "Tuesday, December 24, 2024 ... Interest Rate Products Settlement Time: 12:00:00 CT",
        note="Early close 12:15 (HOLIDAYS).",
    ),
    date(2024, 12, 31): Citation(
        _HC + "new-years-eve-holiday-settlement-times-2025.pdf",
        "Tuesday, December 31, 2024 CME Group Interest Rate Products Settlement Time: 12:00:00 CT",
        note="Globex regular close 16:00 (no entry).",
    ),
    date(2025, 4, 17): Citation(
        _HC + "2025/good-friday-holiday-settlement-times-2025.pdf",
        "Thursday, April 17, 2025 CME Group Interest Rate Products Settlement Time: 12:00:00 CT",
        note="Globex regular close 16:00 (no entry).",
    ),
    date(2025, 5, 23): Citation(
        _HC + "2025/memorial-day-holiday-settlement-times-2025.pdf",
        "Friday, May 23, 2025 CME Group Interest Rate Products Settlement Time: 12:00:00 CT",
        note="Globex hours not in any CME document retrieved (GLOBEX_HOURS_UNDOCUMENTED).",
    ),
    date(2025, 7, 3): Citation(
        _HC + "2025/us-independence-day-settlement-times-2025.pdf",
        "Thursday, July 3, 2025 Interest Rate Products Settlement Time: 12:00:00 CT",
        note="Globex regular close 16:00 (no entry).",
    ),
    date(2025, 11, 28): Citation(
        _HC + "2025/thanksgiving-holiday-settlement-times-2025.pdf",
        (
            "Friday, November 28, 2025 (the day after Thanksgiving) ... Interest Rate Products "
            "Settlement Time: 12:00:00 CT"
        ),
        note="Early close 12:15 (HOLIDAYS).",
    ),
    date(2025, 12, 24): Citation(
        _HC + "2025/christmas-holiday-settlement-times-2025.pdf",
        "Wednesday, December 24, 2025 ... Interest Rate Products Settlement Time: 12:00:00 CT",
        note="Early close 12:15 (HOLIDAYS).",
    ),
    date(2025, 12, 31): Citation(
        _HC + "2025/new-years-eve-holiday-settlement-times-2026.pdf",
        (
            "Wednesday, December 31, 2025 CME Group Interest Rate Products Settlement Time: "
            "12:00:00 CT"
        ),
        note="Globex regular close 16:00 (no entry).",
    ),
    date(2026, 5, 22): Citation(
        _HC + "2026/memorial-day-holiday-settlement-times-2026.pdf",
        "Friday, May 22, 2026 CME Group Interest Rate Products Settlement Time: 12:00:00 CT",
        note="Globex hours not in any CME document retrieved (GLOBEX_HOURS_UNDOCUMENTED).",
    ),
}

# Days near holidays on which CME settled rates early but no CME Globex-hours document was
# retrieved: no entry (modeled as regular sessions), listed for the bar check.
GLOBEX_HOURS_UNDOCUMENTED: dict[date, str] = {
    date(2023, 5, 26): (
        "Friday before Memorial Day: CME settled rates at 12:00 CT (EARLY_SETTLEMENT_CT); CME's "
        "summary PDF and the ZN service range for the holiday start on the Sunday. In 2019-2022 "
        "CME's schedules show the regular 16:00 CT rates close on this Friday."
    ),
    date(2023, 12, 22): (
        "Friday before Christmas 2023: CME settled rates at 12:00 CT (EARLY_SETTLEMENT_CT). "
        "CME's Christmas 2023 summary PDF and the ZN service range start on Monday 2023-12-25. "
        "In 2021 and 2022 the same day kept the regular 16:00 CT rates close."
    ),
    date(2023, 12, 29): (
        "Friday before New Year's Day 2024: CME settled rates at 12:00 CT "
        "(EARLY_SETTLEMENT_CT). CME's New Year 2024 summary PDF and the ZN service range start "
        "on 2023-12-31/2024-01-01. In 2019-2022 and 2024-2025 New Year's Eve kept the regular "
        "16:00 CT rates close."
    ),
    date(2024, 5, 24): (
        "Friday before Memorial Day: CME settled rates at 12:00 CT (EARLY_SETTLEMENT_CT); CME's "
        "summary PDF and the ZN service range for the holiday start on the Sunday. In 2019-2022 "
        "CME's schedules show the regular 16:00 CT rates close on this Friday."
    ),
    date(2025, 5, 23): (
        "Friday before Memorial Day: CME settled rates at 12:00 CT (EARLY_SETTLEMENT_CT); CME's "
        "summary PDF and the ZN service range for the holiday start on the Sunday. In 2019-2022 "
        "CME's schedules show the regular 16:00 CT rates close on this Friday."
    ),
    date(2026, 5, 22): (
        "Friday before Memorial Day: CME settled rates at 12:00 CT (EARLY_SETTLEMENT_CT); CME's "
        "summary PDF and the ZN service range for the holiday start on the Sunday. In 2019-2022 "
        "CME's schedules show the regular 16:00 CT rates close on this Friday."
    ),
}

SESSION_SOURCES: dict[str, Citation] = {
    "cme_treasury_hours": Citation(
        "https://www.cmegroup.com/trading/interest-rates/us-treasury/10-year-us-treasury-note_contract_specifications.html",
        (
            "Trading Hours Sunday - Friday 6:00 p.m. - 5:00 p.m. (5:00 p.m. - 4:00 p.m. CT) "
            "with a 60-minute break each day beginning at 5:00 p.m. (4:00 p.m. CT)"
        ),
        "https://www.cmegroup.com/markets/interest-rates/us-treasury/10-year-us-treasury-note.contractSpecs.html",
        "Trading Hours CME Globex: Sunday - Friday 6:00 p.m. - 5:00 p.m.ET",
        note=(
            "Regular session Sunday-Friday 17:00-16:00 CT with a 60-minute break from 16:00 CT: "
            "CME's ZN contract specifications, status part the 2019-07-19 capture (Globex hours "
            "only, no open-outcry session listed), time part the 2026-04-12 capture (ET). No "
            "CME notice of a change to Treasury futures Globex hours in 2019-2026 was found."
        ),
    ),
    "cme_treasury_settlement": Citation(
        "https://www.cmegroup.com/confluence/display/EPICSANDBOX/Treasuries",
        (
            "last modified by Confluence Admin on Aug 02, 2018 ... Daily settlement of 2-Year "
            "U.S. Treasury Note futures (ZT), 3-Year U.S. Treasury Note futures (Z3N), 5-Year "
            "U.S. Treasury Note futures (ZF), 10-Year U.S. Treasury Note futures (ZN), U.S. "
            "Treasury Bond futures (ZB), Ultra 10-Year U.S. Treasury Note futures (TN) and "
            "Ultra T-Bond futures (UB) is determined by CME Group staff based on trading "
            "activity on CME Globex. ... Tier 1: If the lead month contract trades on Globex "
            "between 13:59:30 and 14:00:00 Central Time (CT), the settlement period, then the "
            "lead month settles to the volume-weighted average price (VWAP) of those trade(s)."
        ),
        "https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/457219006?expand=body.storage,version,history",
        (
            "Daily settlement of 2-Year U.S. Treasury Note futures (ZT), 3-Year U.S. Treasury "
            "Note futures (Z3N), 5-Year U.S. Treasury Note futures (ZF), 10-Year U.S. Treasury "
            "Note futures (ZN), U.S. Treasury Bond futures (ZB), Ultra 10-Year U.S. Treasury "
            "Note futures (TN) 20-Year U.S. Treasury Bond futures (TWE) and Ultra T-Bond "
            "futures (UB) is determined by CME Group staff based on trading activity on CME "
            "Globex. ... If the lead month contract trades on Globex between 13:59:30 and "
            "14:00:00 Central Time (CT), the settlement period"
        ),
        note=(
            "Daily settlement of ZT, ZF, ZN, TN, ZB and UB uses Globex trades between 13:59:30 "
            "and 14:00:00 CT: CME client wiki 'Treasuries', status part the 2019-10-19 Wayback "
            "capture of the page last modified 2018-08-02, time part the page's 2025-10-21 "
            "version (REST API, read 2026-09-25)."
        ),
    ),
}
