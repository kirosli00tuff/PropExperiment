"""CME Globex calendar for the grains group: CBOT corn, wheat, soybean, soybean meal and soybean oil
futures ZC, ZW, ZS, ZM and ZL, 2019-05-01..2026-06-19 (Stage E.2a Task 6; design D10 and D11.3).

Interface as data.cme_calendar, whose Holiday, HolidayKind, Citation and CalendarCoverageError are
imported, not redefined: HOLIDAYS, SOURCES, NO_ENTRY_FINDINGS, CALENDAR_COVERAGE and
assert_calendar_coverage, plus SESSIONS (data.calendars.SessionSpec) with SESSION_SOURCES. One
additive extension, which no existing caller needs to know about:
- LATE_OPENS (with LATE_OPEN_SOURCES): trade dates with no overnight segment, whose first trading
  minute is the 08:30 CT day-session open: the day after Thanksgiving, and the day after most
  Independence Day, Christmas and New Year's Day closures (20 dates). The field names follow
  data.calendars.rates.LateOpen.

Sources (cmegroup.com refuses automated fetches, so every CME file was read from a Wayback Machine
copy; CME's client-systems wiki pages through its REST API):
- 2019-2022: CME's Globex holiday trading schedules (.xls), row "Grains and Oilseeds" (compact
  schedules: "Grain & Oilseed"); 2019-2021 from CME's yearly holiday-calendars.zip, 2022 and the
  New Year 2023 schedule one file per holiday.
- 2023 and New Year 2024: CME's holiday summary PDFs, row "GRAINS"; 2025-01-09: CME's National Day
  of Mourning trading schedule, row "CME AND CBOT AGS".
- 2024-01..2026-06: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html,
  product 300 (ZC, Corn Futures), captures from 2024-07-08 to 2026-07-22.
- MLK Day 2023 only: AMP Futures' image of CME's Globex schedule (secondary; no CME copy found).
- Regular hours and settlement: CME contract specifications (2019) and CME's settlement pages.
Verbatim quotes, capture URLs and file hashes per entry: reports/stage_e2a_calendar_sources_grains
.json and .md. CME states grain holiday hours for its grain asset class or for ZC, the most active
grain contract; ZW, ZS, ZM and ZL are taken to share them.

Grades as data.cme_calendar: status (``evidence``) "cme" | "secondary" | "unverified"; time
(``time_evidence``) "cme" | "secondary" | "inferred" | "unverified" | "n/a" ("empirical" is
reserved for the later bar check). Every status is "cme" except MLK Day 2023 ("secondary"); every
time is "cme" ("n/a" for closures).

How grains differ from the equity calendar: grains close FULLY on the US holidays on which equity
futures trade to a 12:00 CT halt (MLK, Presidents, Memorial, Juneteenth, Independence, Labor and
Thanksgiving Days) and on Good Friday also in jobs-report years (2021, 2023, 2026). The grain
early close is 12:05 CT (the day after Thanksgiving; Christmas Eve on 2019-12-24, 2020-12-24,
2024-12-24 and 2025-12-24; the eve of Independence Day only in 2019 and 2020), and 12:15 CT on the
2025-01-09 National Day of Mourning.

Conventions: ``halt_ct`` is the CT minute trading stops, so the last one-minute bar starts at
halt_ct minus one minute. A FULL_CLOSURE on D means trade date D does not exist: no overnight
segment from 19:00 CT on D-1 and no day session. After the MLK, Presidents, Memorial, Labor and
Juneteenth closures, and the observed Christmas 2022 and New Year 2023 Mondays, grain Globex
reopens at 19:00 CT the same evening for the next trade date (a regular session); after a closure
on a Friday it reopens Sunday 19:00 CT. After the other Independence Day, Thanksgiving, Christmas
and New Year's Day closures there is no evening session, and the next trade date opens at 08:30
CT (LATE_OPENS). Holdout-2 dates (2024-03..2025-03) and the 2019-05..2024-02 confirmation window
rest on CME's schedules alone until their bars are checked.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, time

from data.calendars import Segment, SessionSpec
from data.cme_calendar import CalendarCoverageError, Citation, Holiday, HolidayKind

GRAINS_PRODUCTS = ("ZC", "ZW", "ZS", "ZM", "ZL")

EARLY_CLOSE_1205 = time(12, 5)
DAY_OF_MOURNING_CLOSE = time(12, 15)
DAY_SESSION_OPEN = time(8, 30)

_HC = "https://www.cmegroup.com/tools-information/holiday-calendar/files/"
_TH = "https://www.cmegroup.com/trading-hours/files/"
_WIKI = "https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/"
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
    _closure(date(2019, 5, 27), "Memorial Day"),
    _halt(date(2019, 7, 3), "Day before Independence Day", EARLY_CLOSE_1205),
    _closure(date(2019, 7, 4), "Independence Day"),
    _closure(date(2019, 9, 2), "Labor Day"),
    _closure(date(2019, 11, 28), "Thanksgiving Day"),
    _halt(date(2019, 11, 29), "Day after Thanksgiving", EARLY_CLOSE_1205),
    _halt(date(2019, 12, 24), "Christmas Eve", EARLY_CLOSE_1205),
    _closure(date(2019, 12, 25), "Christmas Day"),
    # ---- 2020
    _closure(date(2020, 1, 1), "New Year's Day"),
    _closure(date(2020, 1, 20), "Martin Luther King Jr. Day"),
    _closure(date(2020, 2, 17), "Presidents Day"),
    _closure(date(2020, 4, 10), "Good Friday"),
    _closure(date(2020, 5, 25), "Memorial Day"),
    _halt(date(2020, 7, 2), "Day before Independence Day (observed)", EARLY_CLOSE_1205),
    _closure(date(2020, 7, 3), "Independence Day (observed)"),
    _closure(date(2020, 9, 7), "Labor Day"),
    _closure(date(2020, 11, 26), "Thanksgiving Day"),
    _halt(date(2020, 11, 27), "Day after Thanksgiving", EARLY_CLOSE_1205),
    _halt(date(2020, 12, 24), "Christmas Eve", EARLY_CLOSE_1205),
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
    _halt(date(2021, 11, 26), "Day after Thanksgiving", EARLY_CLOSE_1205),
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
    _halt(date(2022, 11, 25), "Day after Thanksgiving", EARLY_CLOSE_1205),
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
    _halt(date(2023, 11, 24), "Day after Thanksgiving", EARLY_CLOSE_1205),
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
    _halt(date(2024, 11, 29), "Day after Thanksgiving", EARLY_CLOSE_1205),
    _halt(date(2024, 12, 24), "Christmas Eve", EARLY_CLOSE_1205),
    _closure(date(2024, 12, 25), "Christmas Day"),
    # ---- 2025
    _closure(date(2025, 1, 1), "New Year's Day"),
    _halt(date(2025, 1, 9), "National Day of Mourning (Carter)", DAY_OF_MOURNING_CLOSE),
    _closure(date(2025, 1, 20), "Martin Luther King Jr. Day"),
    _closure(date(2025, 2, 17), "Presidents Day"),
    _closure(date(2025, 4, 18), "Good Friday"),
    _closure(date(2025, 5, 26), "Memorial Day"),
    _closure(date(2025, 6, 19), "Juneteenth"),
    _closure(date(2025, 7, 4), "Independence Day"),
    _closure(date(2025, 9, 1), "Labor Day"),
    _closure(date(2025, 11, 27), "Thanksgiving Day"),
    _halt(date(2025, 11, 28), "Day after Thanksgiving", EARLY_CLOSE_1205),
    _halt(date(2025, 12, 24), "Christmas Eve", EARLY_CLOSE_1205),
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
    data.cme_calendar.assert_calendar_coverage, for the grains group."""
    first, last = CALENDAR_COVERAGE
    outside = sorted(d for d in set(days) if not first <= d <= last)
    if outside:
        raise CalendarCoverageError(
            f"{len(outside)} trade date(s) outside the grains calendar's coverage "
            f"{first}..{last}: {outside[0]} .. {outside[-1]}; extend "
            "data/calendars/grains.py first"
        )


@dataclass(frozen=True)
class LateOpen:
    """A trade date with no overnight segment: its first trading minute is ``open_ct`` CT on
    ``day`` itself (the day-session open), not 19:00 CT the evening before. Grades as for
    Holiday. Additive to the data.cme_calendar interface; the field names match the first five
    fields of data.calendars.rates.LateOpen."""

    day: date
    name: str
    open_ct: time
    evidence: str
    time_evidence: str


LATE_OPENS: dict[date, LateOpen] = {
    date(2019, 7, 5): LateOpen(
        date(2019, 7, 5), "Day after Independence Day", DAY_SESSION_OPEN, "cme", "cme"
    ),
    date(2019, 11, 29): LateOpen(
        date(2019, 11, 29), "Day after Thanksgiving", DAY_SESSION_OPEN, "cme", "cme"
    ),
    date(2019, 12, 26): LateOpen(
        date(2019, 12, 26), "Day after Christmas", DAY_SESSION_OPEN, "cme", "cme"
    ),
    date(2020, 1, 2): LateOpen(
        date(2020, 1, 2), "Day after New Year's Day", DAY_SESSION_OPEN, "cme", "cme"
    ),
    date(2020, 11, 27): LateOpen(
        date(2020, 11, 27), "Day after Thanksgiving", DAY_SESSION_OPEN, "cme", "cme"
    ),
    date(2021, 7, 6): LateOpen(
        date(2021, 7, 6), "Day after Independence Day (observed)", DAY_SESSION_OPEN, "cme", "cme"
    ),
    date(2021, 11, 26): LateOpen(
        date(2021, 11, 26), "Day after Thanksgiving", DAY_SESSION_OPEN, "cme", "cme"
    ),
    date(2022, 7, 5): LateOpen(
        date(2022, 7, 5), "Day after Independence Day", DAY_SESSION_OPEN, "cme", "cme"
    ),
    date(2022, 11, 25): LateOpen(
        date(2022, 11, 25), "Day after Thanksgiving", DAY_SESSION_OPEN, "cme", "cme"
    ),
    date(2023, 7, 5): LateOpen(
        date(2023, 7, 5), "Day after Independence Day", DAY_SESSION_OPEN, "cme", "cme"
    ),
    date(2023, 11, 24): LateOpen(
        date(2023, 11, 24), "Day after Thanksgiving", DAY_SESSION_OPEN, "cme", "cme"
    ),
    date(2023, 12, 26): LateOpen(
        date(2023, 12, 26), "Day after Christmas", DAY_SESSION_OPEN, "cme", "cme"
    ),
    date(2024, 1, 2): LateOpen(
        date(2024, 1, 2), "Day after New Year's Day", DAY_SESSION_OPEN, "cme", "cme"
    ),
    date(2024, 7, 5): LateOpen(
        date(2024, 7, 5), "Day after Independence Day", DAY_SESSION_OPEN, "cme", "cme"
    ),
    date(2024, 11, 29): LateOpen(
        date(2024, 11, 29), "Day after Thanksgiving", DAY_SESSION_OPEN, "cme", "cme"
    ),
    date(2024, 12, 26): LateOpen(
        date(2024, 12, 26), "Day after Christmas", DAY_SESSION_OPEN, "cme", "cme"
    ),
    date(2025, 1, 2): LateOpen(
        date(2025, 1, 2), "Day after New Year's Day", DAY_SESSION_OPEN, "cme", "cme"
    ),
    date(2025, 11, 28): LateOpen(
        date(2025, 11, 28), "Day after Thanksgiving", DAY_SESSION_OPEN, "cme", "cme"
    ),
    date(2025, 12, 26): LateOpen(
        date(2025, 12, 26), "Day after Christmas", DAY_SESSION_OPEN, "cme", "cme"
    ),
    date(2026, 1, 2): LateOpen(
        date(2026, 1, 2), "Day after New Year's Day", DAY_SESSION_OPEN, "cme", "cme"
    ),
}

# One regime covers the whole window: no CME change to grain Globex hours was found.
SESSIONS: tuple[SessionSpec, ...] = (
    SessionSpec(
        valid_from=date(2019, 5, 1),
        valid_to=date(2026, 6, 19),
        segments=(
            Segment(-1, time(19, 0), 0, time(7, 45)),
            Segment(0, time(8, 30), 0, time(13, 20)),
        ),
        day_session_ct={p: (time(8, 30), time(13, 15)) for p in GRAINS_PRODUCTS},
        source="cme_grain_hours",
        note=(
            "Overnight 19:00 CT (prior evening; Sunday for Monday) to 07:45 CT, a pause "
            "07:45-08:30 CT (halt, pre-open from 08:00, no matching), day session 08:30-13:20 CT "
            "(13:20 pause, 13:30 close). day_session_ct is design D6's grains row (O 08:30, C "
            "13:15 CT; F 13:18 CT, session close 13:20, is applied by the rules engine). D6 "
            "confirmation: C 13:15 CT is the end of CME's settlement period 13:14:00-13:15:00 CT "
            "for ZC, ZW, ZS, ZM and ZL (SESSION_SOURCES settle_*); O 08:30 CT is CME's "
            "day-session open and 13:20 CT its close (cme_grain_hours, hours_*). No discrepancy. "
            "Holiday departures: HOLIDAYS and LATE_OPENS."
        ),
    ),
)

SOURCES: dict[date, Citation] = {
    date(2019, 5, 27): Citation(
        _Z19,
        (
            "Updated 4/29/2019|CME Group Globex Memorial Day Holiday Schedule: May 24, 2019 - "
            "May 28, 2019 ... Trade Date|Friday, May 24||Tuesday, May 28 ... Calendar Date|"
            "Friday, May 24||Sunday, May 26|||||Monday, May 27|||||||Tuesday, May 28 ... All "
            "times are Central Time ET +1 UTC +5|Regular Fri. Close|PCP*|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening **|Open|Halt|"
            "Pre-opening**|Open|| ... Grains and Oilseeds |01:20:00 PM|14:30-16:00|04:00:00 PM|||"
            "|||||||07:00:00 PM||7:45 (H) 8:00|08:30:00 AM"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-memorial-day-schedule.xls. Next session: "
            "No grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no "
            "matching); grain Globex reopens 19:00 CT on 2019-05-27 for trade date 2019-05-28. "
            "CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, "
            "soybean meal and soybean oil share it)."
        ),
    ),
    date(2019, 7, 3): Citation(
        _Z19,
        (
            "Updated 6/6/2019|CME Group Globex Independence Day Holiday Schedule: July 3, 2019 "
            "to July 5, 2019 ... Trade Date|Wednesday, July 3||Friday, July 5 ... Calendar Date|"
            "Wednesday, July 3||||||||Thursday, July 4||||||||Friday, July 5 ... All times are "
            "Central Time ET +1 UTC +5|Regular Close|Early Close|PCP*|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|"
            "Open|Pre-opening**|Open|||| ... Grains and Oilseeds ||12:05:00 PM|12:30 - 16:00| |||"
            "||Markets Closed||||||||06:00:00 AM|08:30:00 AM"
        ),
        _Z19,
        (
            "Calendar Date|Wednesday, July 3||||||||Thursday, July 4||||||||Friday, July 5 ... "
            "All times are Central Time ET +1 UTC +5|Regular Close|Early Close|PCP*|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Halt|Pre-opening**|"
            "Open|Halt|Pre-opening**|Open|Pre-opening**|Open|||| ... Grains and Oilseeds ||"
            "12:05:00 PM|12:30 - 16:00| |||||Markets Closed||||||||06:00:00 AM|08:30:00 AM"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-independence-day-schedule.xls. Next "
            "session: No grain evening session (trade date 2019-07-04 is closed). CME Globex "
            "holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean "
            "meal and soybean oil share it). Early Close 12:05 CT; CME's 2019 notice settles "
            "agricultural products at 12:00 CT (extra_evidence)."
        ),
    ),
    date(2019, 7, 4): Citation(
        _Z19,
        (
            "Updated 6/6/2019|CME Group Globex Independence Day Holiday Schedule: July 3, 2019 "
            "to July 5, 2019 ... Trade Date|Wednesday, July 3||Friday, July 5 ... Calendar Date|"
            "Wednesday, July 3||||||||Thursday, July 4||||||||Friday, July 5 ... All times are "
            "Central Time ET +1 UTC +5|Regular Close|Early Close|PCP*|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|"
            "Open|Pre-opening**|Open|||| ... Grains and Oilseeds ||12:05:00 PM|12:30 - 16:00| |||"
            "||Markets Closed||||||||06:00:00 AM|08:30:00 AM"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-independence-day-schedule.xls. Next "
            "session: No grain evening session on 2019-07-03 or on 2019-07-04; trade date "
            "2019-07-05 has no overnight segment and opens 08:30 CT (LATE_OPENS). CME Globex "
            "holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean "
            "meal and soybean oil share it)."
        ),
    ),
    date(2019, 9, 2): Citation(
        _Z19,
        (
            "Updated 8/14/2019|CME Group Globex Labor Day Holiday Schedule: August 30, 2019 - "
            "September 3, 2019 ... Trade Date|Friday, August 30||Tuesday, September 3 ... "
            "Calendar Date|Friday, August 30||Sunday, September 1|||||Monday, September 2|||||||"
            "Tuesday, September 3 ... All times are Central Time ET +1 UTC +5|Regular Fri. Close|"
            "PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|| ... Grains and Oilseeds |01:20:00 PM|"
            "14:30-16:00|04:00:00 PM||||||||||07:00:00 PM||7:45 (H) 8:00|08:30:00 AM"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-labor-day-schedule.xls. Next session: No "
            "grain session on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no "
            "matching); grain Globex reopens 19:00 CT on 2019-09-02 for trade date 2019-09-03. "
            "CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, "
            "soybean meal and soybean oil share it)."
        ),
    ),
    date(2019, 11, 28): Citation(
        _Z19,
        (
            "Updated 10/07/2019|CME Group Globex Thanksgiving Holiday Schedule: November 27, "
            "2019 - November 29, 2019 ... Trade Date|Wednesday, November 27||Friday, November 29 "
            "... Calendar Date|Wednesday, November 27|||||||Thursday, November 28|||||||||Friday,"
            " November 29 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and "
            "Oilseeds |01:20:00 PM|14:30-16:00|04:45:00 PM|||||||||||||||08:30:00 AM|12:05:00 PM"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-thanksgiving-schedule.xls. Next session: "
            "No grain evening session on 2019-11-27 or on 2019-11-28; trade date 2019-11-29 has "
            "no overnight segment and opens 08:30 CT (LATE_OPENS). CME Globex holiday schedule, "
            "row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil "
            "share it). Wednesday 2019-11-27 closes at the regular 13:20 CT; its 16:45 CT "
            "pre-open is for trade date Friday."
        ),
    ),
    date(2019, 11, 29): Citation(
        _Z19,
        (
            "Updated 10/07/2019|CME Group Globex Thanksgiving Holiday Schedule: November 27, "
            "2019 - November 29, 2019 ... Trade Date|Wednesday, November 27||Friday, November 29 "
            "... Calendar Date|Wednesday, November 27|||||||Thursday, November 28|||||||||Friday,"
            " November 29 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and "
            "Oilseeds |01:20:00 PM|14:30-16:00|04:45:00 PM|||||||||||||||08:30:00 AM|12:05:00 PM"
        ),
        _Z19,
        (
            "Calendar Date|Wednesday, November 27|||||||Thursday, November 28|||||||||Friday, "
            "November 29 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and "
            "Oilseeds |01:20:00 PM|14:30-16:00|04:45:00 PM|||||||||||||||08:30:00 AM|12:05:00 PM"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-thanksgiving-schedule.xls. Next session: "
            "Weekend follows; the regular Sunday 19:00 CT reopen is assumed (not in the "
            "schedule). CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat,"
            " soybeans, soybean meal and soybean oil share it). The Friday session is the day "
            "session only: no Thursday-evening session, open 08:30 CT, close 12:05 CT (CME "
            "settles agricultural products at 12:00 CT that day)."
        ),
    ),
    date(2019, 12, 24): Citation(
        _Z19,
        (
            "Updated 10/01/2019|CME Group Globex Christmas Holiday Schedule: December 24, 2019 - "
            "December 26, 2019 ... Trade Date|Tuesday, December 24|Globex Closed|Thursday, "
            "December 26 ... Calendar Date|Tuesday, December 24|Wednesday, December 25|Wednesday,"
            " December 25||||||Thursday, December 26 ... All times are Central Time ET +1 UTC +6|"
            "Close|| Pre-opening**|Open|Pre opening**|Halt| Pre-opening**|Open|Pre-opening**|"
            "Open|Close|PCP* ... Grains and Oilseeds |12:05:00 PM|Globex Closed|||||||06:00:00 "
            "AM|08:30:00 AM|01:20:00 PM|14:30-16:00"
        ),
        _Z19,
        (
            "Calendar Date|Tuesday, December 24|Wednesday, December 25|Wednesday, December 25||||"
            "||Thursday, December 26 ... All times are Central Time ET +1 UTC +6|Close|| "
            "Pre-opening**|Open|Pre opening**|Halt| Pre-opening**|Open|Pre-opening**|Open|Close|"
            "PCP* ... Grains and Oilseeds |12:05:00 PM|Globex Closed|||||||06:00:00 AM|08:30:00 "
            "AM|01:20:00 PM|14:30-16:00"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-christmas-holiday-schedule.xls. Next "
            "session: No grain evening session (trade date 2019-12-25 is closed). CME Globex "
            "holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean "
            "meal and soybean oil share it)."
        ),
    ),
    date(2019, 12, 25): Citation(
        _Z19,
        (
            "Updated 10/01/2019|CME Group Globex Christmas Holiday Schedule: December 24, 2019 - "
            "December 26, 2019 ... Trade Date|Tuesday, December 24|Globex Closed|Thursday, "
            "December 26 ... Calendar Date|Tuesday, December 24|Wednesday, December 25|Wednesday,"
            " December 25||||||Thursday, December 26 ... All times are Central Time ET +1 UTC +6|"
            "Close|| Pre-opening**|Open|Pre opening**|Halt| Pre-opening**|Open|Pre-opening**|"
            "Open|Close|PCP* ... Grains and Oilseeds |12:05:00 PM|Globex Closed|||||||06:00:00 "
            "AM|08:30:00 AM|01:20:00 PM|14:30-16:00"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-christmas-holiday-schedule.xls. Next "
            "session: No grain evening session on 2019-12-24 or on 2019-12-25; trade date "
            "2019-12-26 has no overnight segment and opens 08:30 CT (LATE_OPENS). CME Globex "
            "holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean "
            "meal and soybean oil share it)."
        ),
    ),
    date(2020, 1, 1): Citation(
        _Z19,
        (
            "Updated 10/01/2019|CME Group Globex New Years Holiday Schedule: December 31, 2019 - "
            "January 2, 2020 ... Trade Date|Tuesday, December 31||Thursday, January 2 ... "
            "Calendar Date|Tuesday, December 31|Wednesday, January 1|Wednesday, January 1||||||"
            "Thursday, Jan 2 ... All times are Central Time ET +1 UTC +6| Close|| Pre-opening**|"
            "Open|Pre-opening**|halt| Pre-opening**|Open|Pre-opening**|Open|Close|PCP*|||||| ... "
            "Grains and Oilseeds |13:20 PCP: 14:30-16:00|Globex Closed|||||||06:00:00 AM|"
            "08:30:00 AM|01:20:00 PM|14:30-16:00"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-2020-new-years-holiday-schedule.xls. Next "
            "session: No grain evening session on 2019-12-31 or on 2020-01-01; trade date "
            "2020-01-02 has no overnight segment and opens 08:30 CT (LATE_OPENS). CME Globex "
            "holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean "
            "meal and soybean oil share it). New Year's Eve 2019-12-31 closes at the regular "
            "13:20 CT (NO_ENTRY_FINDINGS)."
        ),
    ),
    date(2020, 1, 20): Citation(
        _Z20,
        (
            "Updated 4/6/2020|CME Group Globex Martin Luther King Day Holiday Schedule: January "
            "17, 2020 - January 21, 2020 ... Trade Date|Friday, January 17||Tuesday, January 21 "
            "... Calendar Date|Friday, January 17||Sunday, January 19|||||Monday, January 20|||||"
            "||Tuesday, January 21 ... All times are Central Time ET +1 UTC +6|Regular Fri. "
            "Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening|Open|Halt|Pre-opening**|Open|| ... Grains and Oilseeds |01:20:00 PM|"
            "14:30-16:00|04:00:00 PM||||||||||07:00:00 PM||7:45 (H) 8:00|08:30:00 AM"
        ),
        note=(
            "Zip member 2020-mlk-day-schedule.xls. Next session: No grain session on the Sunday "
            "evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex "
            "reopens 19:00 CT on 2020-01-20 for trade date 2020-01-21. CME Globex holiday "
            "schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and "
            "soybean oil share it). Equities trade to a 12:00 CT halt that day "
            "(data/cme_calendar.py); grains close."
        ),
    ),
    date(2020, 2, 17): Citation(
        _Z20,
        (
            "Updated 4/6/2020|CME Group Globex Presidents Day Holiday Schedule: February 14, "
            "2020 - February 18, 2020 ... Trade Date|Friday, February 14||Tuesday, February 18 "
            "... Calendar Date|Friday, February 14||Sunday, February 16|||||Monday, February 17||"
            "|||||Tuesday, February 18 ... All times are Central Time ET +1 UTC +6|Regular Fri. "
            "Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening|Open|Halt|Pre-opening**|Open|| ... Grains and Oilseeds |01:20:00 PM|"
            "14:30-16:00|04:00:00 PM||||||||||07:00:00 PM||7:45 (H) 8:00|08:30:00 AM"
        ),
        note=(
            "Zip member 2020-presidents-day-schedule.xls. Next session: No grain session on the "
            "Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex "
            "reopens 19:00 CT on 2020-02-17 for trade date 2020-02-18. CME Globex holiday "
            "schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and "
            "soybean oil share it)."
        ),
    ),
    date(2020, 4, 10): Citation(
        _Z20,
        (
            "Updated 4/6/2020|CME Group Globex Good Friday Holiday Schedule: April 9, 2020 to "
            "April 13, 2020 ... Trade Date|Thursday, April 9|||Friday, April 10||||||Monday, "
            "April 13 ... Calendar Date|Thursday, April 9||||||Friday, April 10|||Sunday, April "
            "12|||||Monday, April 13 ... All times are Central Time ET +1 UTC +5|Regular Close|"
            "Early Thur. Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Close|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Close|Pre-opening**|Open| ... Grains and "
            "Oilseeds |01:20:00 PM||14:30-16:00||||Globex Closed|||04:00:00 PM|07:00:00 PM"
        ),
        note=(
            "Zip member 2020-good-friday-schedule.xls. Next session: No grain evening session on "
            "2020-04-09; grain Globex reopens Sunday 2020-04-12 19:00 CT for trade date "
            "2020-04-13. CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, "
            "wheat, soybeans, soybean meal and soybean oil share it)."
        ),
    ),
    date(2020, 5, 25): Citation(
        _Z20,
        (
            "Updated 4/21/2020|CME Group Globex Memorial Day Holiday Schedule: May 22, 2020 - "
            "May 26, 2020 ... Trade Date|Friday, May 22||Tuesday, May 26 ... Calendar Date|"
            "Friday, May 22||Sunday, May 24|||||Monday, May 25|||||||Tuesday, May 26 ... All "
            "times are Central Time ET +1 UTC +5|Regular Fri. Close|PCP*|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening **|Open|Halt|"
            "Pre-opening**|Open|| ... Grains and Oilseeds |01:20:00 PM|14:30-16:00|04:00:00 PM|||"
            "|||||||07:00:00 PM||7:45 (H) 8:00|08:30:00 AM"
        ),
        note=(
            "Zip member 2020-memorial-day-schedule.xls. Next session: No grain session on the "
            "Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex "
            "reopens 19:00 CT on 2020-05-25 for trade date 2020-05-26. CME Globex holiday "
            "schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and "
            "soybean oil share it)."
        ),
    ),
    date(2020, 7, 2): Citation(
        _Z20,
        (
            "Updated 6/26/2020|CME Group Globex Independence Day Holiday Schedule: July 2, 2020 "
            "to July 6, 2020 ... Trade Date|Thursday, July 2||Monday, July 6 ... Calendar Date|"
            "Thursday, July 2||||||||Friday, July 3|||Sunday, July 5|||||Monday, July 6 ... All "
            "times are Central Time ET +1 UTC +5|Regular Close|Early Close|PCP*|Pre-opening**|"
            "Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Pre-opening**|Open|||||| ... Grains and Oilseeds ||12:05:00 PM|"
            "12:30 - 16:00| |||||Markets Closed|||04:00:00 PM|07:00:00 PM||||08:00:00 AM|"
            "08:30:00 AM"
        ),
        _Z20,
        (
            "Calendar Date|Thursday, July 2||||||||Friday, July 3|||Sunday, July 5|||||Monday, "
            "July 6 ... All times are Central Time ET +1 UTC +5|Regular Close|Early Close|PCP*|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close|Pre-opening**|"
            "Open|Halt|Pre-opening**|Open|Pre-opening**|Open|||||| ... Grains and Oilseeds ||"
            "12:05:00 PM|12:30 - 16:00| |||||Markets Closed|||04:00:00 PM|07:00:00 PM||||"
            "08:00:00 AM|08:30:00 AM"
        ),
        note=(
            "Zip member 2020-independence-day-schedule.xls. Next session: No grain evening "
            "session (trade date 2020-07-03 is closed). CME Globex holiday schedule, row 'Grains "
            "and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it). "
            "Grains close early although equities settled normally that day "
            "(data/cme_calendar.py NO_ENTRY_FINDINGS_2019_2024 has 2020-07-02 as a normal equity "
            "day); CME's 2020 notice settles agricultural products at 12:00 CT (extra_evidence)."
        ),
    ),
    date(2020, 7, 3): Citation(
        _Z20,
        (
            "Updated 6/26/2020|CME Group Globex Independence Day Holiday Schedule: July 2, 2020 "
            "to July 6, 2020 ... Trade Date|Thursday, July 2||Monday, July 6 ... Calendar Date|"
            "Thursday, July 2||||||||Friday, July 3|||Sunday, July 5|||||Monday, July 6 ... All "
            "times are Central Time ET +1 UTC +5|Regular Close|Early Close|PCP*|Pre-opening**|"
            "Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Pre-opening**|Open|||||| ... Grains and Oilseeds ||12:05:00 PM|"
            "12:30 - 16:00| |||||Markets Closed|||04:00:00 PM|07:00:00 PM||||08:00:00 AM|"
            "08:30:00 AM"
        ),
        note=(
            "Zip member 2020-independence-day-schedule.xls. Next session: No grain evening "
            "session on 2020-07-02; grain Globex reopens Sunday 2020-07-05 19:00 CT for trade "
            "date 2020-07-06. CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, "
            "wheat, soybeans, soybean meal and soybean oil share it)."
        ),
    ),
    date(2020, 9, 7): Citation(
        _Z20,
        (
            "Updated 8/28/2020|CME Group Globex Labor Day Holiday Schedule: September 4, 2020 - "
            "September 8, 2020 ... Trade Date|Friday, September 4||Tuesday, September 8 ... "
            "Calendar Date|Friday, September 4||Sunday, September 6|||||Monday, September 7||||||"
            "|Tuesday, September 8 ... All times are Central Time ET +1 UTC +5|Regular Fri. "
            "Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|| ... Grains and Oilseeds |01:20:00 PM|"
            "14:30-16:00|04:00:00 PM||||||||||07:00:00 PM||7:45 (H) 8:00|08:30:00 AM"
        ),
        note=(
            "Zip member 2020-labor-day-schedule.xls. Next session: No grain session on the "
            "Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex "
            "reopens 19:00 CT on 2020-09-07 for trade date 2020-09-08. CME Globex holiday "
            "schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and "
            "soybean oil share it)."
        ),
    ),
    date(2020, 11, 26): Citation(
        _Z20,
        (
            "Updated 10/13/2020|CME Group Globex Thanksgiving Holiday Schedule: November 25, "
            "2020 - November 27, 2020 ... Trade Date|Wednesday, November 25||Friday, November 27 "
            "... Calendar Date|Wednesday, November 25|||||||Thursday, November 26|||||||||Friday,"
            " November 27 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and "
            "Oilseeds |01:20:00 PM|14:30-16:00|04:45:00 PM|||||||||||||||08:30:00 AM|12:05:00 PM"
        ),
        note=(
            "Zip member 2020-thanksgiving-schedule.xls. Next session: No grain evening session "
            "on 2020-11-25 or on 2020-11-26; trade date 2020-11-27 has no overnight segment and "
            "opens 08:30 CT (LATE_OPENS). CME Globex holiday schedule, row 'Grains and Oilseeds' "
            "(CBOT corn, wheat, soybeans, soybean meal and soybean oil share it)."
        ),
    ),
    date(2020, 11, 27): Citation(
        _Z20,
        (
            "Updated 10/13/2020|CME Group Globex Thanksgiving Holiday Schedule: November 25, "
            "2020 - November 27, 2020 ... Trade Date|Wednesday, November 25||Friday, November 27 "
            "... Calendar Date|Wednesday, November 25|||||||Thursday, November 26|||||||||Friday,"
            " November 27 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and "
            "Oilseeds |01:20:00 PM|14:30-16:00|04:45:00 PM|||||||||||||||08:30:00 AM|12:05:00 PM"
        ),
        _Z20,
        (
            "Calendar Date|Wednesday, November 25|||||||Thursday, November 26|||||||||Friday, "
            "November 27 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and "
            "Oilseeds |01:20:00 PM|14:30-16:00|04:45:00 PM|||||||||||||||08:30:00 AM|12:05:00 PM"
        ),
        note=(
            "Zip member 2020-thanksgiving-schedule.xls. Next session: Weekend follows; the "
            "regular Sunday 19:00 CT reopen is assumed (not in the schedule). CME Globex holiday "
            "schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and "
            "soybean oil share it). The Friday session is the day session only: no "
            "Thursday-evening session, open 08:30 CT, close 12:05 CT (CME settles agricultural "
            "products at 12:00 CT that day)."
        ),
    ),
    date(2020, 12, 24): Citation(
        _Z20,
        (
            "Updated 11/17/2020|CME Group Globex Christmas Holiday Schedule: December 24, 2020 - "
            "December 28, 2020 ... Trade Date|Thursday, December 24|Globex Closed|Monday, "
            "December 28 ... Calendar Date|Thursday, December 24|Friday, December 25|Sunday, "
            "December 27||||||Monday, December 28 ... All times are Central Time ET +1 UTC +6|"
            "Close|| Pre-opening**|Open|Pre opening**|Halt| Pre-opening**|Open|Pre-opening**|"
            "Open|Close|PCP* ... Grains and Oilseeds |12:05:00 PM|Globex Closed|04:00:00 PM|"
            "07:00:00 PM|||||08:00:00 AM|08:30:00 AM|01:20:00 PM|14:30-16:00"
        ),
        _Z20,
        (
            "Calendar Date|Thursday, December 24|Friday, December 25|Sunday, December 27||||||"
            "Monday, December 28 ... All times are Central Time ET +1 UTC +6|Close|| "
            "Pre-opening**|Open|Pre opening**|Halt| Pre-opening**|Open|Pre-opening**|Open|Close|"
            "PCP* ... Grains and Oilseeds |12:05:00 PM|Globex Closed|04:00:00 PM|07:00:00 PM|||||"
            "08:00:00 AM|08:30:00 AM|01:20:00 PM|14:30-16:00"
        ),
        note=(
            "Zip member 2020-christmas-holiday-schedule.xls. Next session: No grain evening "
            "session (trade date 2020-12-25 is closed). CME Globex holiday schedule, row 'Grains "
            "and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it)."
        ),
    ),
    date(2020, 12, 25): Citation(
        _Z20,
        (
            "Updated 11/17/2020|CME Group Globex Christmas Holiday Schedule: December 24, 2020 - "
            "December 28, 2020 ... Trade Date|Thursday, December 24|Globex Closed|Monday, "
            "December 28 ... Calendar Date|Thursday, December 24|Friday, December 25|Sunday, "
            "December 27||||||Monday, December 28 ... All times are Central Time ET +1 UTC +6|"
            "Close|| Pre-opening**|Open|Pre opening**|Halt| Pre-opening**|Open|Pre-opening**|"
            "Open|Close|PCP* ... Grains and Oilseeds |12:05:00 PM|Globex Closed|04:00:00 PM|"
            "07:00:00 PM|||||08:00:00 AM|08:30:00 AM|01:20:00 PM|14:30-16:00"
        ),
        note=(
            "Zip member 2020-christmas-holiday-schedule.xls. Next session: No grain evening "
            "session on 2020-12-24; grain Globex reopens Sunday 2020-12-27 19:00 CT for trade "
            "date 2020-12-28. CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, "
            "wheat, soybeans, soybean meal and soybean oil share it). Monday 2020-12-28 keeps "
            "its Sunday 19:00 CT overnight (not a late open)."
        ),
    ),
    date(2021, 1, 1): Citation(
        _Z20,
        (
            "Updated 12/09/2020|CME Group Globex New Years Holiday Schedule: December 31, 2020 - "
            "January 4, 2021 ... Trade Date|Thursday, December 31||Monday, January 4 ... "
            "Calendar Date|Thursday, December 31|Friday, January 1|Sunday, January 3||||||Monday,"
            " January 4 ... All times are Central Time ET +1 UTC +6| Close|| Pre-opening**|Open|"
            "Pre-opening**|halt| Pre-opening**|Open|Pre-opening**|Open|Close|PCP*|||||| ... "
            "Grains and Oilseeds |13:20 PCP: 14:30-16:00|Globex Closed|04:00:00 PM|07:00:00 PM|||"
            "||8:00|08:30:00 AM|01:20:00 PM|14:30-16:00"
        ),
        note=(
            "Zip member 2021-new-years-holiday-schedule.xls. Next session: No grain evening "
            "session on 2020-12-31; grain Globex reopens Sunday 2021-01-03 19:00 CT for trade "
            "date 2021-01-04. CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, "
            "wheat, soybeans, soybean meal and soybean oil share it). New Year's Eve 2020-12-31 "
            "closes at the regular 13:20 CT. D.1f graded the equity entry for this date "
            "unverified (not fetched); for grains CME's own schedule states it."
        ),
    ),
    date(2021, 1, 18): Citation(
        _Z21,
        (
            "Updated 12/23/2020|CME Group Globex Martin Luther King Day Holiday Schedule: "
            "January 15, 2021 - January 19, 2021 ... Trade Date|Friday, January 15||Tuesday, "
            "January 19 ... Calendar Date|Friday, January 15||Sunday, January 17|||||Monday, "
            "January 18|||||||Tuesday, January 19 ... All times are Central Time ET +1 UTC +6|"
            "Regular Fri. Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Halt|Pre-opening|Open|Halt|Pre-opening**|Open|| ... Grains and "
            "Oilseeds |01:20:00 PM|14:30-16:00|04:00:00 PM||||||||||07:00:00 PM||7:45 (H) 8:00|"
            "08:30:00 AM"
        ),
        note=(
            "Zip member 2021-mlk-day-holiday-schedule.xls. Next session: No grain session on the "
            "Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain Globex "
            "reopens 19:00 CT on 2021-01-18 for trade date 2021-01-19. CME Globex holiday "
            "schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and "
            "soybean oil share it)."
        ),
    ),
    date(2021, 2, 15): Citation(
        _Z21,
        (
            "Updated 2/11/2021|CME Group Globex Presidents Day Holiday Schedule: February 12, "
            "2021 - February 16, 2021 ... Trade Date|Friday, February 12||Tuesday, February 16 "
            "... Calendar Date|Friday, February 12||Sunday, February 14|||||Monday, February 15||"
            "|||||Tuesday, February 16 ... All times are Central Time ET +1 UTC +6|Regular Fri. "
            "Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening|Open|Halt|Pre-opening**|Open|| ... Grains and Oilseeds |01:20:00 PM|"
            "14:30-16:00|04:00:00 PM||||||||||07:00:00 PM||7:45 (H) 8:00|08:30:00 AM"
        ),
        note=(
            "Zip member 2021-presidents-day-holiday-schedule.xls. Next session: No grain session "
            "on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain "
            "Globex reopens 19:00 CT on 2021-02-15 for trade date 2021-02-16. CME Globex holiday "
            "schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and "
            "soybean oil share it)."
        ),
    ),
    date(2021, 4, 2): Citation(
        _Z21,
        (
            "Updated 3/31/2021|CME Group Globex Good Friday Holiday Schedule: April 1, 2021 to "
            "April 5, 2021 ... Trade Date|Thursday, April 1|||Friday, April 2||||||Monday, April "
            "5 ... Calendar Date|Thursday, April 1||||||Friday, April 2|||Sunday, April 4|||||"
            "Monday, April 5 ... All times are Central Time ET +1 UTC +5|Regular Close|Early "
            "Thur. Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Close|Pre-opening**|"
            "Open|Halt|Pre-opening**|Open|Close|Pre-opening**|Open| ... Grains and Oilseeds |"
            "01:20:00 PM||14:30-16:00||||Globex Closed|||04:00:00 PM|07:00:00 PM"
        ),
        note=(
            "Zip member 2021-good-friday-holiday-schedule.xls. Next session: No grain evening "
            "session on 2021-04-01; grain Globex reopens Sunday 2021-04-04 19:00 CT for trade "
            "date 2021-04-05. CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, "
            "wheat, soybeans, soybean meal and soybean oil share it). Jobs-report Good Friday: "
            "equities, rates and FX traded abbreviated sessions; grains stayed closed ('Globex "
            "Closed')."
        ),
    ),
    date(2021, 5, 31): Citation(
        _Z21,
        (
            "Updated 5/25/2021|CME Group Globex Memorial Day Holiday Schedule: May 28, 2021 - "
            "Jun 1, 2021 ... Trade Date|Friday, May 28||Tuesday, Jun 1 ... Calendar Date|Friday, "
            "May 28||Sunday, May 30|||||Monday, May 31|||||||Tuesday, Jun 1 ... All times are "
            "Central Time ET +1 UTC +5|Regular Fri. Close|PCP*|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening **|Open|Halt|"
            "Pre-opening**|Open|| ... Grains and Oilseeds |01:20:00 PM|14:30-16:00|04:00:00 PM|||"
            "|||||||07:00:00 PM||7:45 (H) 8:00|08:30:00 AM"
        ),
        note=(
            "Zip member 2021-memorial-day-holiday-schedule.xls. Next session: No grain session "
            "on the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain "
            "Globex reopens 19:00 CT on 2021-05-31 for trade date 2021-06-01. CME Globex holiday "
            "schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and "
            "soybean oil share it)."
        ),
    ),
    date(2021, 7, 5): Citation(
        _Z21,
        (
            "|CME Group Globex Independence Day Holiday Schedule: July 2, 2021 to July 6, 2021 "
            "... Trade Date|Friday, July 2|Tuesday, July 6 ... Calendar Date|Friday July 2|"
            "Sunday July 4|Monday July 5|Monday July 5 ... Product|CLOSE|OPEN|HALT|OPEN ... "
            "Grain & Oilseed |Regular Per Product|Markets Closed|Markets Closed|Tuesday July 6 "
            "Regular @ 0830 CT / 1330 UTC"
        ),
        note=(
            "Zip member 2021-independence-day-holiday-schedule-compact.xls. Next session: No "
            "grain session on Sunday 2021-07-04 or Monday 2021-07-05 ('Markets Closed'); trade "
            "date 2021-07-06 has no overnight segment and opens 08:30 CT (LATE_OPENS). CME "
            "Globex compact holiday schedule, row 'Grain & Oilseed' (the full schedule's grain "
            "row leaves the Sunday and Monday cells empty). Friday 2021-07-02 closes at the "
            "regular 13:20 CT (NO_ENTRY_FINDINGS)."
        ),
    ),
    date(2021, 9, 6): Citation(
        _Z21,
        (
            "Updated 8/12/2021|CME Group Globex Labor Day Holiday Schedule: September 3, 2021 - "
            "September 7, 2021 ... Trade Date|Friday, September 3||Tuesday, September 7 ... "
            "Calendar Date|Friday, September 3||Sunday, September 5|||||Monday, September 6||||||"
            "|Tuesday, September 7 ... All times are Central Time ET +1 UTC +5|Regular Fri. "
            "Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|| ... Grains and Oilseeds |01:20:00 PM|"
            "14:30-16:00|04:00:00 PM||||||||||07:00:00 PM||7:45 (H) 8:00|08:30:00 AM"
        ),
        note=(
            "Zip member 2021-labor-day-holiday-schedule.xls. Next session: No grain session on "
            "the Sunday evening (Sunday 16:00 CT is an extended pre-open, no matching); grain "
            "Globex reopens 19:00 CT on 2021-09-06 for trade date 2021-09-07. CME Globex holiday "
            "schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and "
            "soybean oil share it)."
        ),
    ),
    date(2021, 11, 25): Citation(
        _Z21,
        (
            "Updated 11/23/2021|CME Group Globex Thanksgiving Holiday Schedule: November 24, "
            "2021 - November 26, 2021 ... Trade Date|Wednesday, November 24||Friday, November 26 "
            "... Calendar Date|Wednesday, November 24|||||||Thursday, November 25|||||||||Friday,"
            " November 26 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and "
            "Oilseeds |01:20:00 PM|14:30-16:00|04:45:00 PM|||||||||||||||08:30:00 AM|12:05:00 PM"
        ),
        note=(
            "Zip member 2021-thanksgiving-holiday-schedule.xls. Next session: No grain evening "
            "session on 2021-11-24 or on 2021-11-25; trade date 2021-11-26 has no overnight "
            "segment and opens 08:30 CT (LATE_OPENS). CME Globex holiday schedule, row 'Grains "
            "and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it)."
        ),
    ),
    date(2021, 11, 26): Citation(
        _Z21,
        (
            "Updated 11/23/2021|CME Group Globex Thanksgiving Holiday Schedule: November 24, "
            "2021 - November 26, 2021 ... Trade Date|Wednesday, November 24||Friday, November 26 "
            "... Calendar Date|Wednesday, November 24|||||||Thursday, November 25|||||||||Friday,"
            " November 26 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and "
            "Oilseeds |01:20:00 PM|14:30-16:00|04:45:00 PM|||||||||||||||08:30:00 AM|12:05:00 PM"
        ),
        _Z21,
        (
            "Calendar Date|Wednesday, November 24|||||||Thursday, November 25|||||||||Friday, "
            "November 26 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and "
            "Oilseeds |01:20:00 PM|14:30-16:00|04:45:00 PM|||||||||||||||08:30:00 AM|12:05:00 PM"
        ),
        note=(
            "Zip member 2021-thanksgiving-holiday-schedule.xls. Next session: Weekend follows; "
            "the regular Sunday 19:00 CT reopen is assumed (not in the schedule). CME Globex "
            "holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean "
            "meal and soybean oil share it). The Friday session is the day session only: no "
            "Thursday-evening session, open 08:30 CT, close 12:05 CT (CME settles agricultural "
            "products at 12:00 CT that day)."
        ),
    ),
    date(2021, 12, 24): Citation(
        _Z21,
        (
            "Updated 12/01/2021|CME Group Globex Christmas Holiday Schedule: December 24, 2021 - "
            "December 27, 2021 ... Trade Date|Thursday, December 23||||||||||Monday, December 27 "
            "... Calendar Date|Thursday, December 23|||||||||||||Friday, December 24||||||||||"
            "Sunday, December 26||||||Monday, Dec 27 ... All times are Central Time ET +1 UTC +6|"
            "Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|"
            "Pre-opening**|Open|Close||Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Close| Pre-opening**|Open|Pre opening**|Halt| Pre-opening**|Open|"
            "Pre-opening**|Open|Close|PCP* ... Grains and Oilseeds |13:20 (**PCP 14:30-16:00)||||"
            "|||||||||Globex Closed||||||||||04:00:00 PM|07:00:00 PM|||||08:00:00 AM|08:30:00 AM|"
            "01:20:00 PM|14:30-16:00"
        ),
        note=(
            "Zip member 2021-christmas-holiday-schedule.xls. Next session: No grain evening "
            "session on 2021-12-23; grain Globex reopens Sunday 2021-12-26 19:00 CT for trade "
            "date 2021-12-27. CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, "
            "wheat, soybeans, soybean meal and soybean oil share it). Thursday 2021-12-23 closes "
            "at the regular 13:20 CT (NO_ENTRY_FINDINGS)."
        ),
    ),
    date(2022, 1, 17): Citation(
        _HC + "2022-mlk-day-holiday-schedule.xls",
        (
            "Updated 12/14/2021|CME Group Globex Martin Luther King Day Holiday Schedule: "
            "January 14, 2022 - January 18, 2022 ... Trade Date|Friday, January 14||Tuesday, "
            "January 18 ... Calendar Date|Friday, January 14|||||Sunday, January 16|||||Monday, "
            "January 17|||||||||Tuesday, January 18 ... All times are Central Time ET +1 UTC +6|"
            "Regular Fri. Close|PCP*|Pre-opening|Open|Close|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening|Open|Halt|Pre-opening|"
            "Open|Pre-opening**|Open|| ... Grains and Oilseeds |01:20:00 PM|14:30-16:00||||"
            "04:00:00 PM||||||||||07:00:00 PM||||7:45 (H) 8:00|08:30:00 AM"
        ),
        note=(
            "Next session: No grain session on the Sunday evening (Sunday 16:00 CT is an "
            "extended pre-open, no matching); grain Globex reopens 19:00 CT on 2022-01-17 for "
            "trade date 2022-01-18. CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT "
            "corn, wheat, soybeans, soybean meal and soybean oil share it)."
        ),
    ),
    date(2022, 2, 21): Citation(
        _HC + "2022-presidents-day-holiday-schedule.xls",
        (
            "Updated 1/24/2022|CME Group Globex Presidents Day Holiday Schedule: February 18, "
            "2022 - February 22, 2022 ... Trade Date|Friday, February 18||Tuesday, February 22 "
            "... Calendar Date|Friday, February 18|||||Sunday, February 20|||||Monday, February "
            "21||||||||||||Tuesday, February 22 ... All times are Central Time ET +1 UTC +6|"
            "Regular Fri. Close|PCP*|Pre-opening|Open|Close|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening|Open|Halt|Pre-opening|"
            "Open|Halt|Pre-opening|Open|Pre-opening**|Open|| ... Grains and Oilseeds |01:20:00 "
            "PM|14:30-16:00||||04:00:00 PM|||||||||||||07:00:00 PM||||7:45 (H) 8:00|08:30:00 AM"
        ),
        note=(
            "Next session: No grain session on the Sunday evening (Sunday 16:00 CT is an "
            "extended pre-open, no matching); grain Globex reopens 19:00 CT on 2022-02-21 for "
            "trade date 2022-02-22. CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT "
            "corn, wheat, soybeans, soybean meal and soybean oil share it)."
        ),
    ),
    date(2022, 4, 15): Citation(
        _HC + "2022-good-friday-holiday-schedule.xls",
        (
            "Updated 3/17/2022|CME Group Globex Good Friday Holiday Schedule: April 14, 2022 to "
            "April 18, 2022 ... Trade Date|Thursday, April 14||||||Monday, April 18 ... Calendar "
            "Date|Thursday, April 14|||||||||Friday, April 15|||Sunday, April 17|||||Monday, "
            "April 18 ... All times are Central Time ET +1 UTC +5|Regular Close|Early Thur. "
            "Close|PCP*|Pre-opening**|Open|Halt/Close|Pre-opening**|Open|Halt/Close|"
            "Pre-opening**|Open|Close|Pre-opening**|Open|Halt|Pre-opening**|Open|Close|"
            "Pre-opening**|Open| ... Grains and Oilseeds |01:20:00 PM||14:30-16:00|||||||Globex "
            "Closed|||04:00:00 PM|07:00:00 PM"
        ),
        note=(
            "Next session: No grain evening session on 2022-04-14; grain Globex reopens Sunday "
            "2022-04-17 19:00 CT for trade date 2022-04-18. CME Globex holiday schedule, row "
            "'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil "
            "share it)."
        ),
    ),
    date(2022, 5, 30): Citation(
        _HC + "2022-memorial-day-holiday-schedule.xls",
        (
            "Updated 5/18/2022|CME Group Globex Memorial Day Holiday Schedule: May 27, 2022 - "
            "May 31, 2022 ... Trade Date|Friday, May 27||Tuesday, May 31 ... Calendar Date|"
            "Friday, May 27|||||Sunday, May 29|||||Monday, May 30||||||||||Tuesday, May 31 ... "
            "All times are Central Time ET +1 UTC +5|Regular Fri. Close|PCP*|Pre-opening|Open|"
            "Close|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Halt|Pre-opening **|Open|Halt|Pre-opening**|Open|| ... Grains "
            "and Oilseeds |01:20:00 PM|14:30-16:00||||04:00:00 PM|||||||||||||07:00:00 PM||7:45 "
            "(H) 8:00|08:30:00 AM"
        ),
        note=(
            "Next session: No grain session on the Sunday evening (Sunday 16:00 CT is an "
            "extended pre-open, no matching); grain Globex reopens 19:00 CT on 2022-05-30 for "
            "trade date 2022-05-31. CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT "
            "corn, wheat, soybeans, soybean meal and soybean oil share it)."
        ),
    ),
    date(2022, 6, 20): Citation(
        _HC + "2022-juneteenth-holiday-schedule.xls",
        (
            "Updated 5/18/2022|CME Group Globex Juneteenth Holiday Schedule: June 17, 2022 - Jun "
            "21, 2022 ... Trade Date|Friday, June 17||Tuesday, Jun 21 ... Calendar Date|Friday, "
            "June 17|||||Sunday, June 19|||||Monday, June 20||||||||||Tuesday, Jun 21 ... All "
            "times are Central Time ET +1 UTC +5|Regular Fri. Close|PCP*| Pre-opening**|Open|"
            "Close|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Halt|Pre-opening **|Open|Halt|Pre-opening**|Open|| ... Grains "
            "and Oilseeds |01:20:00 PM|14:30-16:00||||04:00:00 PM|||||||||||||07:00:00 PM||7:45 "
            "(H) 8:00|08:30:00 AM"
        ),
        note=(
            "Next session: No grain session on the Sunday evening (Sunday 16:00 CT is an "
            "extended pre-open, no matching); grain Globex reopens 19:00 CT on 2022-06-20 for "
            "trade date 2022-06-21. CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT "
            "corn, wheat, soybeans, soybean meal and soybean oil share it). First Juneteenth "
            "closure: CME's 2021 schedules include no Juneteenth file."
        ),
    ),
    date(2022, 7, 4): Citation(
        _HC + "2022-independence-day-holiday-schedule-compact.xls",
        (
            "|CME Group Globex Independence Day Holiday Schedule: July 1, 2022 to July 5, 2022 "
            "... Trade Date|Friday, July 1|Tuesday, July 5 ... Calendar Date|Friday July 1|"
            "Sunday July 3|Monday July 4|Monday July 4 ... Product|CLOSE|OPEN|HALT|OPEN ... "
            "Grain & Oilseed |Regular Per Product|Markets Closed|Markets Closed|Tuesday July 5 "
            "Regular @ 0830 CT / 1330 UTC"
        ),
        note=(
            "Next session: No grain session on Sunday 2022-07-03 or Monday 2022-07-04 ('Markets "
            "Closed'); trade date 2022-07-05 has no overnight segment and opens 08:30 CT "
            "(LATE_OPENS). CME Globex compact holiday schedule, row 'Grain & Oilseed' (the full "
            "schedule's grain row leaves the Sunday and Monday cells empty). Friday 2022-07-01 "
            "closes at the regular 13:20 CT."
        ),
    ),
    date(2022, 9, 5): Citation(
        _HC + "2022-labor-day-holiday-schedule.xls",
        (
            "Updated 6/29/2022|CME Group Globex Labor Day Holiday Schedule: September 2, 2022 - "
            "September 6, 2022 ... Trade Date|Friday, September 2||Tuesday, September 6 ... "
            "Calendar Date|Friday, September 2|||||Sunday, September 4|||||Monday, September 5|||"
            "|||||||Tuesday, Sept. 6 ... All times are Central Time ET +1 UTC +5|Regular Fri. "
            "Close|PCP*| Pre-opening**|Open|Close|Pre-opening**|Open|Halt|Pre-opening**|Open|"
            "Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|| ... Grains and Oilseeds |01:20:00 PM|14:30-16:00||||04:00:00 "
            "PM|||||||||||||07:00:00 PM||7:45 (H) 8:00|08:30:00 AM"
        ),
        note=(
            "Next session: No grain session on the Sunday evening (Sunday 16:00 CT is an "
            "extended pre-open, no matching); grain Globex reopens 19:00 CT on 2022-09-05 for "
            "trade date 2022-09-06. CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT "
            "corn, wheat, soybeans, soybean meal and soybean oil share it)."
        ),
    ),
    date(2022, 11, 24): Citation(
        _HC + "2022-thanksgiving-holiday-schedule.xls",
        (
            "Updated 6/29/2022|CME Group Globex Thanksgiving Holiday Schedule: November 23, 2022 "
            "- November 25, 2022 ... Trade Date|Wednesday, November 23|||||Friday, November 25 "
            "... Calendar Date|Wednesday, November 23||||||||||Thursday, November 24||||||||||||"
            "Friday, November 25 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Halt|Halt|Pre-opening**|Open|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and Oilseeds |01:20:00 PM|"
            "14:30-16:00||||04:45:00 PM||||||||||||||||||08:30:00 AM|12:05:00 PM"
        ),
        note=(
            "Next session: No grain evening session on 2022-11-23 or on 2022-11-24; trade date "
            "2022-11-25 has no overnight segment and opens 08:30 CT (LATE_OPENS). CME Globex "
            "holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean "
            "meal and soybean oil share it)."
        ),
    ),
    date(2022, 11, 25): Citation(
        _HC + "2022-thanksgiving-holiday-schedule.xls",
        (
            "Updated 6/29/2022|CME Group Globex Thanksgiving Holiday Schedule: November 23, 2022 "
            "- November 25, 2022 ... Trade Date|Wednesday, November 23|||||Friday, November 25 "
            "... Calendar Date|Wednesday, November 23||||||||||Thursday, November 24||||||||||||"
            "Friday, November 25 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Halt|Halt|Pre-opening**|Open|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and Oilseeds |01:20:00 PM|"
            "14:30-16:00||||04:45:00 PM||||||||||||||||||08:30:00 AM|12:05:00 PM"
        ),
        _HC + "2022-thanksgiving-holiday-schedule.xls",
        (
            "Calendar Date|Wednesday, November 23||||||||||Thursday, November 24||||||||||||"
            "Friday, November 25 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Halt|Halt|Pre-opening**|Open|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and Oilseeds |01:20:00 PM|"
            "14:30-16:00||||04:45:00 PM||||||||||||||||||08:30:00 AM|12:05:00 PM"
        ),
        note=(
            "Next session: Weekend follows; the regular Sunday 19:00 CT reopen is assumed (not "
            "in the schedule). CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn,"
            " wheat, soybeans, soybean meal and soybean oil share it). The Friday session is the "
            "day session only: no Thursday-evening session, open 08:30 CT, close 12:05 CT (CME "
            "settles agricultural products at 12:00 CT that day)."
        ),
    ),
    date(2022, 12, 26): Citation(
        _HC + "2022-christmas-holiday-schedule.xls",
        (
            "Updated 6/29/2022|CME Group Globex Christmas Holiday Schedule: December 23, 2022 - "
            "December 27, 2022 ... Trade Date|Friday, December 23|||||Tuesday, December 27 ... "
            "Calendar Date|Friday, December 23||||||||Monday, December 26||||||||||||||||Tuesday,"
            " December 27 ... All times are Central Time ET +1 UTC +6|Close|PCP*|Pre-opening**|"
            "Open|Halt| Pre-opening**|Open|Close||Pre-opening**|Open|Halt|Pre-opening**|Open|"
            "Halt|Pre-opening**|Open|Close| Pre-opening**|Open|Pre opening**|Halt| Pre-opening**|"
            "Open|Pre-opening**|Open|Close|PCP* ... Grains and Oilseeds |13:20 (**PCP "
            "14:30-16:00)||||||||Globex Closed||||||||||04:00:00 PM|07:00:00 PM|||||08:00:00 AM|"
            "08:30:00 AM|01:20:00 PM|14:30-16:00"
        ),
        note=(
            "Next session: No grain session from Friday 2022-12-23 13:20 CT until the Monday "
            "2022-12-26 19:00 CT open (pre-open 16:00 CT) for trade date 2022-12-27, which is "
            "therefore regular. CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT "
            "corn, wheat, soybeans, soybean meal and soybean oil share it). The capture "
            "(2022-07-04) is CME's schedule 'Updated 6/29/2022', six months before the holiday; "
            "no later version was retrieved."
        ),
    ),
    date(2023, 1, 2): Citation(
        _HC + "2023-new-years-holiday-schedule.xls",
        (
            "Updated 6/29/22|CME Group Globex New Year's Holiday Schedule: December 30, 2022 - "
            "January 3, 2023 ... Trade Date|Friday, December 30|Tuesday, January 3 ... Calendar "
            "Date|Friday, December 30||||Monday, January 2|Monday, January 2||||||Tuesday, "
            "January 3 ... All times are Central Time ET +1 UTC +6| Close| Pre-opening**|Open|"
            "Close|| Pre-opening**|Open|Pre-opening**|halt| Pre-opening**|Open|Close|"
            "Pre-opening**|Open|Close|PCP* ... Grains and Oilseeds |13:20 PCP: 14:30-16:00||||"
            "Globex Closed|04:00:00 PM|07:00:00 PM|NORMAL|||||SCHEDULE"
        ),
        note=(
            "Next session: No grain session from Friday 2022-12-30 13:20 CT until the Monday "
            "2023-01-02 19:00 CT open (pre-open 16:00 CT) for trade date 2023-01-03 ('NORMAL "
            "SCHEDULE'). CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, "
            "wheat, soybeans, soybean meal and soybean oil share it). The capture (2022-07-04) "
            "is CME's schedule 'Updated 6/29/22'; no later version was retrieved."
        ),
    ),
    date(2023, 1, 16): Citation(
        "https://www.ampfutures.com/hubfs/CME%20Holiday%20Trading%20Schedule%20-%20Dr.%20Martin%20Luther%20King%2c%20Jr.%20(2023).png",
        (
            "CME Group Globex Dr. Martin Luther King, Jr. Holiday Schedule: 13 - 17 January 2023 "
            "... Calendar Trade | Friday, Jan 13 | Sunday, Jan 15 | Monday, Jan 16 | Monday, Jan "
            "16 | Tuesday, Jan 17 ... | CLOSE | OPEN | HALT | OPEN | CLOSE ... Grains | Regular "
            "per Product | Extended Pre Open @ 16:00 CST | > | 19:00 CST | Regular per Product"
        ),
        note=(
            "Next session: No grain session on the Sunday evening (Sunday 16:00 CT is an "
            "extended pre-open, no matching); grain Globex reopens 19:00 CT on 2023-01-16 for "
            "trade date 2023-01-17. SECONDARY: no CME grain-hours document for MLK Day 2023 was "
            "retrievable (CME's 2023 MLK xls covers only MGEX and DME products; CME's page "
            "linked the day to its trading-hours service, whose captures hold no 2023-01 "
            "events). AMP Futures' image of 'CME Group Globex Dr. Martin Luther King, Jr. "
            "Holiday Schedule' is transcribed; the image cannot be checked by script. CME's own "
            "MLK 2023 settlement notice says no CBOT settlement prices that day, and every other "
            "year (2020-2022, 2024-2026) CME's schedule closes grains on MLK Day."
        ),
    ),
    date(2023, 2, 20): Citation(
        "https://www.cmegroup.com/files/presidents-day.pdf",
        (
            "PRODUCT NAME Cleared As SUNDAY, 19 FEB 2023 MONDAY, 20 FEB 2023 TUESDAY, 21 FEB "
            "2023 ... 07:45 (PAUSED) 08:00 (PREOPEN) 08:30 (OPEN) 13:20 (PAUSED) TRADE DATE: "
            "TUES 21 FEB TRADE DATE: TUES 21 FEB 13:30 (CLOSED) GRAINS 16:00 (PREOPEN) 19:00 "
            "(OPEN) 14:30 (PCP) 16:00 (CLOSED) TRADE DATE: WED 22 FEB 16:45 (PREOPEN) 19:00 "
            "(OPEN)"
        ),
        note=(
            "Next session: No grain session on the Sunday evening (Sunday 16:00 CT is an "
            "extended pre-open, no matching); grain Globex reopens 19:00 CT on 2023-02-20 for "
            "trade date 2023-02-21. CME holiday summary PDF, row 'GRAINS' (the summary uses the "
            "most actively traded instrument of each asset class); the table's column for each "
            "calendar day was read from the pdftotext -layout column positions. Sunday column: "
            "16:00 PREOPEN; Monday column: 19:00 OPEN, both for trade date Tuesday 21 Feb."
        ),
    ),
    date(2023, 4, 7): Citation(
        "https://www.cmegroup.com/files/good-friday.pdf",
        (
            "PRODUCT NAME THURSDAY, 6 APR 2023 FRIDAY, 7 APR 2023 ... TRADE DATE: THURS 6 APR "
            "07:45 (PAUSED) Holiday hours outlined in yellow. 08:00 (PREOPEN) GRAINS 08:30 "
            "(OPEN) 13:20 (PAUSED) 13:30 (CLOSED) 14:30 (PCP) 16:00 (CLOSED)"
        ),
        note=(
            "Next session: No grain evening session on 2023-04-06; the retrieved document stops "
            "before Sunday 2023-04-09: the regular Sunday 19:00 CT reopen for trade date "
            "2023-04-10 is assumed (not in a source). CME holiday summary PDF, row 'GRAINS' (the "
            "summary uses the most actively traded instrument of each asset class); the table's "
            "column for each calendar day was read from the pdftotext -layout column positions. "
            "The GRAINS row has events only in the Thursday column (regular session ending 16:00 "
            "CLOSED, no 19:00 open) and none in the Friday column, while equities, rates and FX "
            "show Friday abbreviated sessions (jobs-report Good Friday). AMP Futures' image of "
            "CME's schedule shows Grains 'Closed for Good Friday' (extra_evidence)."
        ),
    ),
    date(2023, 5, 29): Citation(
        _TH + "memorial-day-2023.pdf",
        (
            "PRODUCT NAME SUNDAY, 28 MAY 2023 MONDAY, 29 MAY 2023 TUESDAY, 30 MAY 2023 ... TRADE "
            "DATE: TUES 30 MAY 07:45 (PAUSED) 08:00 (PREOPEN) 08:30 (OPEN) 13:20 (PAUSED) TRADE "
            "DATE: TUES 30 MAY TRADE DATE: TUES 30 MAY 13:30 (CLOSED) GRAINS 16:00 (PREOPEN) "
            "19:00 (OPEN) 14:30 (PCP) 16:00 (CLOSED) TRADE DATE: WED 31 MAY 16:45 (PREOPEN) "
            "19:00 (OPEN)"
        ),
        note=(
            "Next session: No grain session on the Sunday evening (Sunday 16:00 CT is an "
            "extended pre-open, no matching); grain Globex reopens 19:00 CT on 2023-05-29 for "
            "trade date 2023-05-30. CME holiday summary PDF, row 'GRAINS' (the summary uses the "
            "most actively traded instrument of each asset class); the table's column for each "
            "calendar day was read from the pdftotext -layout column positions."
        ),
    ),
    date(2023, 6, 19): Citation(
        _TH + "juneteenth-2023.pdf",
        (
            "PRODUCT NAME SUNDAY, 18 JUNE 2023 MONDAY, 19 JUNE 2023 TUESDAY, 20 JUNE 2023 ... "
            "TRADE DATE: TUES 20 JUNE 07:45 (PAUSED) 08:00 (PREOPEN) 08:30 (OPEN) 13:20 (PAUSED) "
            "TRADE DATE: TUES 20 JUNE TRADE DATE: TUES 20 JUNE 13:30 (CLOSED) GRAINS 16:00 "
            "(PREOPEN) 19:00 (OPEN) 14:30 (PCP) 16:00 (CLOSED) TRADE DATE: WED 21 JUNE 16:45 "
            "(PREOPEN) 19:00 (OPEN)"
        ),
        note=(
            "Next session: No grain session on the Sunday evening (Sunday 16:00 CT is an "
            "extended pre-open, no matching); grain Globex reopens 19:00 CT on 2023-06-19 for "
            "trade date 2023-06-20. CME holiday summary PDF, row 'GRAINS' (the summary uses the "
            "most actively traded instrument of each asset class); the table's column for each "
            "calendar day was read from the pdftotext -layout column positions."
        ),
    ),
    date(2023, 7, 4): Citation(
        _TH + "4th-of-july-2023.pdf",
        (
            "PRODUCT NAME MONDAY, 3 JULY 2023 TUESDAY, 4 JULY 2023 WEDNESDAY, 5 JULY 2023 ... "
            "TRADE DATE: WED 5 JULY TRADE DATE: MON 3 JULY 06:00 (PREOPEN) 07:45 (PAUSED) 08:30 "
            "(OPEN) 08:00 (PREOPEN) 13:20 (PAUSED) 08:30 (OPEN) 13:30 (CLOSED) GRAINS 14:30 "
            "(PCP) 13:20 (PAUSED) 13:30 (CLOSED) 16:00 (CLOSED) 14:30 (PCP) TRADE DATE: THUR 6 "
            "JULY 16:00 (CLOSED) 16:45 (PREOPEN) 19:00 (OPEN)"
        ),
        note=(
            "Next session: No grain evening session on 2023-07-03 or on 2023-07-04; trade date "
            "2023-07-05 has no overnight segment and opens 08:30 CT (LATE_OPENS). CME holiday "
            "summary PDF, row 'GRAINS' (the summary uses the most actively traded instrument of "
            "each asset class); the table's column for each calendar day was read from the "
            "pdftotext -layout column positions. Two columns interleave in the text: Monday 3 "
            "July (trade date MON 3 JULY: 07:45 PAUSED, 08:00 PREOPEN, 08:30 OPEN, 13:20 PAUSED, "
            "13:30 CLOSED, 14:30 PCP, 16:00 CLOSED, a regular day with no evening open) and "
            "Wednesday 5 July (trade date WED 5 JULY: 06:00 PREOPEN, 08:30 OPEN, ...; then TRADE "
            "DATE THUR 6 JULY 16:45 PREOPEN, 19:00 OPEN); the Tuesday 4 July column is empty for "
            "GRAINS."
        ),
    ),
    date(2023, 9, 4): Citation(
        _TH + "labor-day-2023.pdf",
        (
            "PRODUCT NAME SUNDAY, 3 SEPTEMBER 2023 MONDAY, 4 SEPTEMBER 2023 TUESDAY, 5 SEPTEMBER "
            "2023 ... TRADE DATE: TUES 5 SEP 07:45 (PAUSED) 08:00 (PREOPEN) 08:30 (OPEN) 13:20 "
            "(PAUSED) TRADE DATE: TUES 5 SEP TRADE DATE: TUES 5 SEP 13:30 (CLOSED) GRAINS 16:00 "
            "(PREOPEN) 19:00 (OPEN) 14:30 (PCP) 16:00 (CLOSED) TRADE DATE: WED 6 SEP 16:45 "
            "(PREOPEN) 19:00 (OPEN)"
        ),
        note=(
            "Next session: No grain session on the Sunday evening (Sunday 16:00 CT is an "
            "extended pre-open, no matching); grain Globex reopens 19:00 CT on 2023-09-04 for "
            "trade date 2023-09-05. CME holiday summary PDF, row 'GRAINS' (the summary uses the "
            "most actively traded instrument of each asset class); the table's column for each "
            "calendar day was read from the pdftotext -layout column positions. CME's ZC service "
            "record (captured 2024-07-08) agrees (extra_evidence)."
        ),
    ),
    date(2023, 11, 23): Citation(
        _TH + "thanksgiving-day-2023.pdf",
        (
            "PRODUCT NAME WEDNESDAY, 22 NOVEMBER 2023 THURSDAY, 23 NOVEMBER 2023 FRIDAY, 24 "
            "NOVEMBER 2023 ... TRADE DATE: WED 22 NOV 07:45 (PAUSED) 08:00 (PREOPEN) 08:30 "
            "(OPEN) 13:20 (PAUSED) TRADE DATE: FRI 24 NOV GRAINS 13:30 (CLOSED) 08:30 (OPEN) "
            "14:30 (PCP) 12:05 (CLOSED) 16:00 (CLOSED) TRADE DATE: FRI 24 NOV 16:45 (PREOPEN)"
        ),
        note=(
            "Next session: No grain evening session on 2023-11-22 or on 2023-11-23; trade date "
            "2023-11-24 has no overnight segment and opens 08:30 CT (LATE_OPENS). CME holiday "
            "summary PDF, row 'GRAINS' (the summary uses the most actively traded instrument of "
            "each asset class); the table's column for each calendar day was read from the "
            "pdftotext -layout column positions. Wednesday column: regular day, then 16:45 "
            "PREOPEN for trade date FRI 24 NOV; Thursday column empty; Friday column: 08:30 OPEN,"
            " 12:05 CLOSED."
        ),
    ),
    date(2023, 11, 24): Citation(
        _TH + "thanksgiving-day-2023.pdf",
        (
            "PRODUCT NAME WEDNESDAY, 22 NOVEMBER 2023 THURSDAY, 23 NOVEMBER 2023 FRIDAY, 24 "
            "NOVEMBER 2023 ... TRADE DATE: FRI 24 NOV GRAINS 13:30 (CLOSED) 08:30 (OPEN) 14:30 "
            "(PCP) 12:05 (CLOSED)"
        ),
        _TH + "thanksgiving-day-2023.pdf",
        "TRADE DATE: FRI 24 NOV GRAINS 13:30 (CLOSED) 08:30 (OPEN) 14:30 (PCP) 12:05 (CLOSED)",
        note=(
            "Next session: Weekend follows; the regular Sunday 19:00 CT reopen is assumed (not "
            "in the summary). CME holiday summary PDF, row 'GRAINS' (the summary uses the most "
            "actively traded instrument of each asset class); the table's column for each "
            "calendar day was read from the pdftotext -layout column positions. The Friday "
            "session is the day session only: no Thursday-evening session, open 08:30 CT, close "
            "12:05 CT (CME settles agricultural products at 12:00 CT that day)."
        ),
    ),
    date(2023, 12, 25): Citation(
        _TH + "christmas-day-2023.pdf",
        (
            "PRODUCT NAME MONDAY, 25 DECEMBER 2023 TUESDAY, 26 DECEMBER 2023 ... TRADE DATE: "
            "TUES 26 DEC 06:00 (PREOPEN) 08:30 (OPEN) 13:20 (PAUSED) 13:30 (CLOSED) GRAINS 14:30 "
            "(PCP) 16:00 (CLOSED) TRADE DATE: WED 27 DEC 16:45 (PREOPEN) 19:00 (OPEN)"
        ),
        note=(
            "Next session: No grain session on Sunday 2023-12-24 or Monday 2023-12-25; trade "
            "date 2023-12-26 has no overnight segment and opens 08:30 CT (LATE_OPENS). CME "
            "holiday summary PDF, row 'GRAINS' (the summary uses the most actively traded "
            "instrument of each asset class); the table's column for each calendar day was read "
            "from the pdftotext -layout column positions. The Monday column is empty for GRAINS; "
            "CME's ZC service record (captured 2024-07-08) shows no events on 2023-12-24 or "
            "2023-12-25 (extra_evidence). Friday 2023-12-22 has no grain Globex document (gaps; "
            "CME's settlement notice says only rates settle early)."
        ),
    ),
    date(2024, 1, 1): Citation(
        _TH + "new-years-day-2024.pdf",
        (
            "PRODUCT NAME MONDAY, 1 JANUARY 2024 TUESDAY, 2 JANUARY 2024 ... TRADE DATE: TUES 2 "
            "JAN 06:00 (PREOPEN) 08:30 (OPEN) 13:20 (PAUSED) 13:30 (CLOSED) GRAINS 14:30 (PCP) "
            "16:00 (CLOSED) TRADE DATE: WED 3 JAN 16:45 (PREOPEN) 19:00 (OPEN)"
        ),
        note=(
            "Next session: No grain session on Sunday 2023-12-31 or Monday 2024-01-01; trade "
            "date 2024-01-02 has no overnight segment and opens 08:30 CT (LATE_OPENS). CME "
            "holiday summary PDF, row 'GRAINS' (the summary uses the most actively traded "
            "instrument of each asset class); the table's column for each calendar day was read "
            "from the pdftotext -layout column positions. CME's ZC service record (captured "
            "2024-07-08) shows no events on 2023-12-31 or 2024-01-01 (extra_evidence). Friday "
            "2023-12-29 has no grain Globex document (gaps)."
        ),
    ),
    date(2024, 1, 15): Citation(
        _svc("2024-01-14", "2024-01-16", "1720455278663"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2024-01-14","events":[{"tradingDate":"2024-01-16","eventTime":"16:00",'
            '"marketEventType":"preopen"}]},{"groupCode":"ZC","eventDate":"2024-01-15",'
            '"events":[{"tradingDate":"2024-01-16","eventTime":"19:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "Next session: No grain session on the Sunday evening (Sunday 16:00 CT is an "
            "extended pre-open, no matching); grain Globex reopens 19:00 CT on 2024-01-15 for "
            "trade date 2024-01-16. CME's trading-hours service record for Corn (ZC, product id "
            "300), the most active grain contract; CME states the grain holiday hours per asset "
            "class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form "
            "CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules)."
        ),
    ),
    date(2024, 2, 19): Citation(
        _svc("2024-02-18", "2024-02-20", "1720455278669"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2024-02-18","events":[{"tradingDate":"2024-02-20","eventTime":"16:00",'
            '"marketEventType":"preopen"}]},{"groupCode":"ZC","eventDate":"2024-02-19",'
            '"events":[{"tradingDate":"2024-02-20","eventTime":"19:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "Next session: No grain session on the Sunday evening (Sunday 16:00 CT is an "
            "extended pre-open, no matching); grain Globex reopens 19:00 CT on 2024-02-19 for "
            "trade date 2024-02-20. CME's trading-hours service record for Corn (ZC, product id "
            "300), the most active grain contract; CME states the grain holiday hours per asset "
            "class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form "
            "CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules)."
        ),
    ),
    date(2024, 3, 29): Citation(
        _svc("2024-03-28", "2024-03-30", "1720455278672"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... '
            '{"tradingDate":"2024-03-28","eventTime":"16:00","marketEventType":"closed"}]},'
            '{"groupCode":"ZC","eventDate":"2024-03-29","events":[]},{"groupCode":"ZC",'
            '"eventDate":"2024-03-30","events":[]}'
        ),
        note=(
            "Next session: No grain evening session on 2024-03-28; the retrieved document stops "
            "before Sunday 2024-03-31: the regular Sunday 19:00 CT reopen for trade date "
            "2024-04-01 is assumed (not in a source). CME's trading-hours service record for "
            "Corn (ZC, product id 300), the most active grain contract; CME states the grain "
            "holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and "
            "ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex "
            "holiday schedules)."
        ),
    ),
    date(2024, 5, 27): Citation(
        _svc("2024-05-26", "2024-05-28", "1720455278675"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2024-05-26","events":[{"tradingDate":"2024-05-28","eventTime":"16:00",'
            '"marketEventType":"preopen"}]},{"groupCode":"ZC","eventDate":"2024-05-27",'
            '"events":[{"tradingDate":"2024-05-28","eventTime":"19:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "Next session: No grain session on the Sunday evening (Sunday 16:00 CT is an "
            "extended pre-open, no matching); grain Globex reopens 19:00 CT on 2024-05-27 for "
            "trade date 2024-05-28. CME's trading-hours service record for Corn (ZC, product id "
            "300), the most active grain contract; CME states the grain holiday hours per asset "
            "class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form "
            "CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules)."
        ),
    ),
    date(2024, 6, 19): Citation(
        _svc("2024-06-18", "2024-06-20", "1720455278677"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... '
            '{"tradingDate":"2024-06-18","eventTime":"16:00","marketEventType":"closed"},'
            '{"tradingDate":"2024-06-20","eventTime":"16:45","marketEventType":"preopen"}]},'
            '{"groupCode":"ZC","eventDate":"2024-06-19","events":[{"tradingDate":"2024-06-20",'
            '"eventTime":"19:00","marketEventType":"open"}]}'
        ),
        note=(
            "Next session: No grain evening session on 2024-06-18; grain Globex reopens 19:00 CT "
            "on 2024-06-19 for trade date 2024-06-20. CME's trading-hours service record for "
            "Corn (ZC, product id 300), the most active grain contract; CME states the grain "
            "holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and "
            "ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex "
            "holiday schedules)."
        ),
    ),
    date(2024, 7, 4): Citation(
        _svc("2024-07-03", "2024-07-05", "1720455278680"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... '
            '{"tradingDate":"2024-07-03","eventTime":"16:00","marketEventType":"closed"}]},'
            '{"groupCode":"ZC","eventDate":"2024-07-04","events":[]}'
        ),
        note=(
            "Next session: No grain evening session on 2024-07-03 or on 2024-07-04; trade date "
            "2024-07-05 has no overnight segment and opens 08:30 CT (LATE_OPENS). CME's "
            "trading-hours service record for Corn (ZC, product id 300), the most active grain "
            "contract; CME states the grain holiday hours per asset class or for its most active "
            "contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' "
            "row in the 2019-2022 Globex holiday schedules). Wednesday 2024-07-03 is a regular "
            "grain day (13:20 CT; NO_ENTRY_FINDINGS). data/cme_calendar.py carries 2024-07-04 as "
            "an equity full closure that design D10 says must be corrected to a 12:00 CT halt; "
            "for grains the full closure is right."
        ),
    ),
    date(2024, 9, 2): Citation(
        _svc("2024-09-01", "2024-09-03", "1734710019534"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2024-09-01","events":[{"tradingDate":"2024-09-03","eventTime":"16:00",'
            '"marketEventType":"preopen"}]},{"groupCode":"ZC","eventDate":"2024-09-02",'
            '"events":[{"tradingDate":"2024-09-03","eventTime":"19:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "Next session: No grain session on the Sunday evening (Sunday 16:00 CT is an "
            "extended pre-open, no matching); grain Globex reopens 19:00 CT on 2024-09-02 for "
            "trade date 2024-09-03. CME's trading-hours service record for Corn (ZC, product id "
            "300), the most active grain contract; CME states the grain holiday hours per asset "
            "class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form "
            "CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules)."
        ),
    ),
    date(2024, 11, 28): Citation(
        _svc("2024-11-27", "2024-11-29", "1734710019535"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... '
            '{"tradingDate":"2024-11-27","eventTime":"16:00","marketEventType":"closed"},'
            '{"tradingDate":"2024-11-29","eventTime":"16:45","marketEventType":"preopen"}]},'
            '{"groupCode":"ZC","eventDate":"2024-11-28","events":[]}'
        ),
        note=(
            "Next session: No grain evening session on 2024-11-27 or on 2024-11-28; trade date "
            "2024-11-29 has no overnight segment and opens 08:30 CT (LATE_OPENS). CME's "
            "trading-hours service record for Corn (ZC, product id 300), the most active grain "
            "contract; CME states the grain holiday hours per asset class or for its most active "
            "contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' "
            "row in the 2019-2022 Globex holiday schedules)."
        ),
    ),
    date(2024, 11, 29): Citation(
        _svc("2024-11-27", "2024-11-29", "1734710019535"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2024-11-28","events":[]},{"groupCode":"ZC","eventDate":"2024-11-29",'
            '"events":[{"tradingDate":"2024-11-29","eventTime":"08:30","marketEventType":"open"},'
            '{"tradingDate":"2024-11-29","eventTime":"12:05","marketEventType":"closed"}]}'
        ),
        _svc("2024-11-27", "2024-11-29", "1734710019535"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2024-11-29","events":[{"tradingDate":"2024-11-29","eventTime":"08:30",'
            '"marketEventType":"open"},{"tradingDate":"2024-11-29","eventTime":"12:05",'
            '"marketEventType":"closed"}]}'
        ),
        note=(
            "Next session: Weekend follows; the regular Sunday 19:00 CT reopen is assumed (not "
            "in the record). CME's trading-hours service record for Corn (ZC, product id 300), "
            "the most active grain contract; CME states the grain holiday hours per asset class "
            "or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's "
            "'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules). The Friday "
            "session is the day session only: no Thursday-evening session, open 08:30 CT, close "
            "12:05 CT (CME settles agricultural products at 12:00 CT that day)."
        ),
    ),
    date(2024, 12, 24): Citation(
        _svc("2024-12-24", "2024-12-26", "1734710019537"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2024-12-24","events":[{"tradingDate":"2024-12-24","eventTime":"07:45",'
            '"marketEventType":"paused"},{"tradingDate":"2024-12-24","eventTime":"08:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2024-12-24","eventTime":"08:30",'
            '"marketEventType":"open"},{"tradingDate":"2024-12-24","eventTime":"12:05",'
            '"marketEventType":"closed"}]}'
        ),
        _svc("2024-12-24", "2024-12-26", "1734710019537"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... '
            '{"tradingDate":"2024-12-24","eventTime":"08:30","marketEventType":"open"},'
            '{"tradingDate":"2024-12-24","eventTime":"12:05","marketEventType":"closed"}]}'
        ),
        note=(
            "Next session: No grain evening session (trade date 2024-12-25 is closed). CME's "
            "trading-hours service record for Corn (ZC, product id 300), the most active grain "
            "contract; CME states the grain holiday hours per asset class or for its most active "
            "contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' "
            "row in the 2019-2022 Globex holiday schedules). CME's notice settles agricultural "
            "products at 12:00 CT (extra_evidence)."
        ),
    ),
    date(2024, 12, 25): Citation(
        _svc("2024-12-24", "2024-12-26", "1734710019537"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... '
            '{"tradingDate":"2024-12-24","eventTime":"12:05","marketEventType":"closed"}]},'
            '{"groupCode":"ZC","eventDate":"2024-12-25","events":[]}'
        ),
        note=(
            "Next session: No grain evening session on 2024-12-24 or on 2024-12-25; trade date "
            "2024-12-26 has no overnight segment and opens 08:30 CT (LATE_OPENS). CME's "
            "trading-hours service record for Corn (ZC, product id 300), the most active grain "
            "contract; CME states the grain holiday hours per asset class or for its most active "
            "contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' "
            "row in the 2019-2022 Globex holiday schedules)."
        ),
    ),
    date(2025, 1, 1): Citation(
        _svc("2024-12-31", "2025-01-02", "1734710019538"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... '
            '{"tradingDate":"2024-12-31","eventTime":"16:00","marketEventType":"closed"}]},'
            '{"groupCode":"ZC","eventDate":"2025-01-01","events":[]}'
        ),
        note=(
            "Next session: No grain evening session on 2024-12-31 or on 2025-01-01; trade date "
            "2025-01-02 has no overnight segment and opens 08:30 CT (LATE_OPENS). CME's "
            "trading-hours service record for Corn (ZC, product id 300), the most active grain "
            "contract; CME states the grain holiday hours per asset class or for its most active "
            "contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' "
            "row in the 2019-2022 Globex holiday schedules)."
        ),
    ),
    date(2025, 1, 9): Citation(
        _TH + "day-of-mourning-january-9-2024.pdf",
        (
            "U.S. National Day of Mourning Trading Schedule for Globex, BrokerTec, EBS and "
            "Trading Floor ... PRODUCT NAME JANUARY 9, 2025 TRADING FLOOR CLEARPORT ... CME AND "
            "CBOT AGS* EARLY CLOSE – 12:15 PM CT N/A NORMAL HOURS"
        ),
        _TH + "day-of-mourning-january-9-2024.pdf",
        (
            "CME AND CBOT AGS* EARLY CLOSE – 12:15 PM CT N/A NORMAL HOURS ... *There is no "
            "change for products that have an earlier close than 12 PM CT"
        ),
        note=(
            "Next session: The schedule gives only the early close; the regular 19:00 CT reopen "
            "for trade date 2025-01-10 is assumed (not in the source). CME's U.S. National Day "
            "of Mourning trading schedule (the file name says 2024; the content is dated January "
            "9, 2025). The overnight session of 2025-01-09 (from 19:00 CT on 2025-01-08) is not "
            "affected by the schedule's wording. Grains close at 13:20 CT normally, so the "
            "footnote's exemption does not apply."
        ),
    ),
    date(2025, 1, 20): Citation(
        _svc("2025-01-19", "2025-01-21", "1734710019539"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2025-01-19","events":[{"tradingDate":"2025-01-21","eventTime":"16:00",'
            '"marketEventType":"preopen"}]},{"groupCode":"ZC","eventDate":"2025-01-20",'
            '"events":[{"tradingDate":"2025-01-21","eventTime":"19:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "Next session: No grain session on the Sunday evening (Sunday 16:00 CT is an "
            "extended pre-open, no matching); grain Globex reopens 19:00 CT on 2025-01-20 for "
            "trade date 2025-01-21. CME's trading-hours service record for Corn (ZC, product id "
            "300), the most active grain contract; CME states the grain holiday hours per asset "
            "class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form "
            "CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules)."
        ),
    ),
    date(2025, 2, 17): Citation(
        _svc("2025-02-16", "2025-02-18", "1734710019540"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2025-02-16","events":[{"tradingDate":"2025-02-18","eventTime":"16:00",'
            '"marketEventType":"preopen"}]},{"groupCode":"ZC","eventDate":"2025-02-17",'
            '"events":[{"tradingDate":"2025-02-18","eventTime":"19:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "Next session: No grain session on the Sunday evening (Sunday 16:00 CT is an "
            "extended pre-open, no matching); grain Globex reopens 19:00 CT on 2025-02-17 for "
            "trade date 2025-02-18. CME's trading-hours service record for Corn (ZC, product id "
            "300), the most active grain contract; CME states the grain holiday hours per asset "
            "class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form "
            "CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules)."
        ),
    ),
    date(2025, 4, 18): Citation(
        _svc("2025-04-17", "2025-04-19", "1734710019542"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... '
            '{"tradingDate":"2025-04-17","eventTime":"16:00","marketEventType":"closed"}]},'
            '{"groupCode":"ZC","eventDate":"2025-04-18","events":[]},{"groupCode":"ZC",'
            '"eventDate":"2025-04-19","events":[]}'
        ),
        note=(
            "Next session: No grain evening session on 2025-04-17; the retrieved document stops "
            "before Sunday 2025-04-20: the regular Sunday 19:00 CT reopen for trade date "
            "2025-04-21 is assumed (not in a source). CME's trading-hours service record for "
            "Corn (ZC, product id 300), the most active grain contract; CME states the grain "
            "holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and "
            "ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex "
            "holiday schedules)."
        ),
    ),
    date(2025, 5, 26): Citation(
        _svc("2025-05-25", "2025-05-27", "1734710019543"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2025-05-25","events":[{"tradingDate":"2025-05-27","eventTime":"16:00",'
            '"marketEventType":"preopen"}]},{"groupCode":"ZC","eventDate":"2025-05-26",'
            '"events":[{"tradingDate":"2025-05-27","eventTime":"19:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "Next session: No grain session on the Sunday evening (Sunday 16:00 CT is an "
            "extended pre-open, no matching); grain Globex reopens 19:00 CT on 2025-05-26 for "
            "trade date 2025-05-27. CME's trading-hours service record for Corn (ZC, product id "
            "300), the most active grain contract; CME states the grain holiday hours per asset "
            "class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form "
            "CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules)."
        ),
    ),
    date(2025, 6, 19): Citation(
        _svc("2025-06-18", "2025-06-20", "1734710019544"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... '
            '{"tradingDate":"2025-06-18","eventTime":"16:00","marketEventType":"closed"},'
            '{"tradingDate":"2025-06-20","eventTime":"16:45","marketEventType":"preopen"}]},'
            '{"groupCode":"ZC","eventDate":"2025-06-19","events":[{"tradingDate":"2025-06-20",'
            '"eventTime":"19:00","marketEventType":"open"}]}'
        ),
        note=(
            "Next session: No grain evening session on 2025-06-18; grain Globex reopens 19:00 CT "
            "on 2025-06-19 for trade date 2025-06-20. CME's trading-hours service record for "
            "Corn (ZC, product id 300), the most active grain contract; CME states the grain "
            "holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and "
            "ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex "
            "holiday schedules)."
        ),
    ),
    date(2025, 7, 4): Citation(
        _svc("2025-07-03", "2025-07-05", "1734710019545"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... '
            '{"tradingDate":"2025-07-03","eventTime":"16:00","marketEventType":"closed"}]},'
            '{"groupCode":"ZC","eventDate":"2025-07-04","events":[]},{"groupCode":"ZC",'
            '"eventDate":"2025-07-05","events":[]}'
        ),
        note=(
            "Next session: No grain evening session on 2025-07-03; the retrieved document stops "
            "before Sunday 2025-07-06: the regular Sunday 19:00 CT reopen for trade date "
            "2025-07-07 is assumed (not in a source). CME's trading-hours service record for "
            "Corn (ZC, product id 300), the most active grain contract; CME states the grain "
            "holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and "
            "ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex "
            "holiday schedules). Thursday 2025-07-03 is a regular grain day (13:20 CT; "
            "NO_ENTRY_FINDINGS)."
        ),
    ),
    date(2025, 9, 1): Citation(
        _svc("2025-08-31", "2025-09-02", "1734710019546"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2025-08-31","events":[{"tradingDate":"2025-09-02","eventTime":"16:00",'
            '"marketEventType":"preopen"}]},{"groupCode":"ZC","eventDate":"2025-09-01",'
            '"events":[{"tradingDate":"2025-09-02","eventTime":"19:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "Next session: No grain session on the Sunday evening (Sunday 16:00 CT is an "
            "extended pre-open, no matching); grain Globex reopens 19:00 CT on 2025-09-01 for "
            "trade date 2025-09-02. CME's trading-hours service record for Corn (ZC, product id "
            "300), the most active grain contract; CME states the grain holiday hours per asset "
            "class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form "
            "CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules)."
        ),
    ),
    date(2025, 11, 27): Citation(
        _svc("2025-11-26", "2025-11-28", "1769649703060"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... '
            '{"tradingDate":"2025-11-26","eventTime":"16:00","marketEventType":"closed"},'
            '{"tradingDate":"2025-11-28","eventTime":"16:45","marketEventType":"preopen"}]},'
            '{"groupCode":"ZC","eventDate":"2025-11-27","events":[]}'
        ),
        note=(
            "Next session: No grain evening session on 2025-11-26 or on 2025-11-27; trade date "
            "2025-11-28 has no overnight segment and opens 08:30 CT (LATE_OPENS). CME's "
            "trading-hours service record for Corn (ZC, product id 300), the most active grain "
            "contract; CME states the grain holiday hours per asset class or for its most active "
            "contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' "
            "row in the 2019-2022 Globex holiday schedules)."
        ),
    ),
    date(2025, 11, 28): Citation(
        _svc("2025-11-26", "2025-11-28", "1769649703060"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2025-11-27","events":[]},{"groupCode":"ZC","eventDate":"2025-11-28",'
            '"events":[{"tradingDate":"2025-11-28","eventTime":"07:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"08:30",'
            '"marketEventType":"open"},{"tradingDate":"2025-11-28","eventTime":"12:05",'
            '"marketEventType":"closed"}]}'
        ),
        _svc("2025-11-26", "2025-11-28", "1769649703060"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28","eventTime":"07:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"08:30",'
            '"marketEventType":"open"},{"tradingDate":"2025-11-28","eventTime":"12:05",'
            '"marketEventType":"closed"}]}'
        ),
        note=(
            "Next session: Weekend follows; the regular Sunday 19:00 CT reopen is assumed (not "
            "in the record). CME's trading-hours service record for Corn (ZC, product id 300), "
            "the most active grain contract; CME states the grain holiday hours per asset class "
            "or for its most active contract, and ZW, ZS, ZM and ZL share them (they form CME's "
            "'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules). The Friday "
            "session is the day session only: no Thursday-evening session, open 08:30 CT, close "
            "12:05 CT (CME settles agricultural products at 12:00 CT that day). The CME Globex "
            "outage of 2025-11-27/28 (data-center cooling failure; data/calendars/rates.py "
            "LATE_OPENS) fell while grains were already closed: this post-event capture "
            "(2026-01-29) adds a 07:00 CT pre-open before the scheduled 08:30 CT open and keeps "
            "the 12:05 CT close; the pre-event capture (2024-12-20) has 08:30 open and 12:05 "
            "closed only (extra_evidence). No grain entry changes."
        ),
    ),
    date(2025, 12, 24): Citation(
        _svc("2025-12-24", "2025-12-26", "1769649703064"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2025-12-24","events":[{"tradingDate":"2025-12-24","eventTime":"07:45",'
            '"marketEventType":"paused"},{"tradingDate":"2025-12-24","eventTime":"08:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2025-12-24","eventTime":"08:30",'
            '"marketEventType":"open"},{"tradingDate":"2025-12-24","eventTime":"12:05",'
            '"marketEventType":"closed"}]}'
        ),
        _svc("2025-12-24", "2025-12-26", "1769649703064"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... '
            '{"tradingDate":"2025-12-24","eventTime":"08:30","marketEventType":"open"},'
            '{"tradingDate":"2025-12-24","eventTime":"12:05","marketEventType":"closed"}]}'
        ),
        note=(
            "Next session: No grain evening session (trade date 2025-12-25 is closed). CME's "
            "trading-hours service record for Corn (ZC, product id 300), the most active grain "
            "contract; CME states the grain holiday hours per asset class or for its most active "
            "contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' "
            "row in the 2019-2022 Globex holiday schedules). CME's notice settles agricultural "
            "products at 12:00 CT (extra_evidence)."
        ),
    ),
    date(2025, 12, 25): Citation(
        _svc("2025-12-24", "2025-12-26", "1769649703064"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... '
            '{"tradingDate":"2025-12-24","eventTime":"12:05","marketEventType":"closed"}]},'
            '{"groupCode":"ZC","eventDate":"2025-12-25","events":[]}'
        ),
        note=(
            "Next session: No grain evening session on 2025-12-24 or on 2025-12-25; trade date "
            "2025-12-26 has no overnight segment and opens 08:30 CT (LATE_OPENS). CME's "
            "trading-hours service record for Corn (ZC, product id 300), the most active grain "
            "contract; CME states the grain holiday hours per asset class or for its most active "
            "contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' "
            "row in the 2019-2022 Globex holiday schedules)."
        ),
    ),
    date(2026, 1, 1): Citation(
        _svc("2025-12-31", "2026-01-02", "1769649703066"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... '
            '{"tradingDate":"2025-12-31","eventTime":"16:00","marketEventType":"closed"}]},'
            '{"groupCode":"ZC","eventDate":"2026-01-01","events":[]}'
        ),
        note=(
            "Next session: No grain evening session on 2025-12-31 or on 2026-01-01; trade date "
            "2026-01-02 has no overnight segment and opens 08:30 CT (LATE_OPENS). CME's "
            "trading-hours service record for Corn (ZC, product id 300), the most active grain "
            "contract; CME states the grain holiday hours per asset class or for its most active "
            "contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and Oilseeds' "
            "row in the 2019-2022 Globex holiday schedules)."
        ),
    ),
    date(2026, 1, 19): Citation(
        _svc("2026-01-18", "2026-01-20", "1769649703068"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2026-01-18","events":[{"tradingDate":"2026-01-20","eventTime":"16:00",'
            '"marketEventType":"preopen"}]},{"groupCode":"ZC","eventDate":"2026-01-19",'
            '"events":[{"tradingDate":"2026-01-20","eventTime":"19:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "Next session: No grain session on the Sunday evening (Sunday 16:00 CT is an "
            "extended pre-open, no matching); grain Globex reopens 19:00 CT on 2026-01-19 for "
            "trade date 2026-01-20. CME's trading-hours service record for Corn (ZC, product id "
            "300), the most active grain contract; CME states the grain holiday hours per asset "
            "class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form "
            "CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules)."
        ),
    ),
    date(2026, 2, 16): Citation(
        _svc("2026-02-15", "2026-02-17", "1743113432015"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2026-02-15","events":[{"tradingDate":"2026-02-17","eventTime":"16:00",'
            '"marketEventType":"preopen"}]},{"groupCode":"ZC","eventDate":"2026-02-16",'
            '"events":[{"tradingDate":"2026-02-17","eventTime":"19:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "Next session: No grain session on the Sunday evening (Sunday 16:00 CT is an "
            "extended pre-open, no matching); grain Globex reopens 19:00 CT on 2026-02-16 for "
            "trade date 2026-02-17. CME's trading-hours service record for Corn (ZC, product id "
            "300), the most active grain contract; CME states the grain holiday hours per asset "
            "class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form "
            "CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules)."
        ),
    ),
    date(2026, 4, 3): Citation(
        _svc("2026-04-01", "2026-04-03", "1743113432016"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... '
            '{"tradingDate":"2026-04-02","eventTime":"16:00","marketEventType":"closed"}]},'
            '{"groupCode":"ZC","eventDate":"2026-04-03","events":[]}'
        ),
        note=(
            "Next session: No grain evening session on 2026-04-02; the retrieved document stops "
            "before Sunday 2026-04-05: the regular Sunday 19:00 CT reopen for trade date "
            "2026-04-06 is assumed (not in a source). CME's trading-hours service record for "
            "Corn (ZC, product id 300), the most active grain contract; CME states the grain "
            "holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and "
            "ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex "
            "holiday schedules). Jobs-report Good Friday: equities traded an abbreviated "
            "session; grains closed."
        ),
    ),
    date(2026, 5, 25): Citation(
        _svc("2026-05-24", "2026-05-26", "1749141516014"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2026-05-24","events":[{"tradingDate":"2026-05-26","eventTime":"16:00",'
            '"marketEventType":"preopen"}]},{"groupCode":"ZC","eventDate":"2026-05-25",'
            '"events":[{"tradingDate":"2026-05-26","eventTime":"19:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "Next session: No grain session on the Sunday evening (Sunday 16:00 CT is an "
            "extended pre-open, no matching); grain Globex reopens 19:00 CT on 2026-05-25 for "
            "trade date 2026-05-26. CME's trading-hours service record for Corn (ZC, product id "
            "300), the most active grain contract; CME states the grain holiday hours per asset "
            "class or for its most active contract, and ZW, ZS, ZM and ZL share them (they form "
            "CME's 'Grains and Oilseeds' row in the 2019-2022 Globex holiday schedules)."
        ),
    ),
    date(2026, 6, 19): Citation(
        _svc("2026-06-18", "2026-06-20", "1784720540600"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... '
            '{"tradingDate":"2026-06-18","eventTime":"16:00","marketEventType":"closed"}]},'
            '{"groupCode":"ZC","eventDate":"2026-06-19","events":[]},{"groupCode":"ZC",'
            '"eventDate":"2026-06-20","events":[]}'
        ),
        note=(
            "Next session: No grain evening session on 2026-06-18; the next session (Sunday "
            "2026-06-21 19:00 CT) lies outside the coverage. CME's trading-hours service record "
            "for Corn (ZC, product id 300), the most active grain contract; CME states the grain "
            "holiday hours per asset class or for its most active contract, and ZW, ZS, ZM and "
            "ZL share them (they form CME's 'Grains and Oilseeds' row in the 2019-2022 Globex "
            "holiday schedules)."
        ),
    ),
}

LATE_OPEN_SOURCES: dict[date, Citation] = {
    date(2019, 7, 5): Citation(
        _Z19,
        (
            "Updated 6/6/2019|CME Group Globex Independence Day Holiday Schedule: July 3, 2019 "
            "to July 5, 2019 ... Trade Date|Wednesday, July 3||Friday, July 5 ... Calendar Date|"
            "Wednesday, July 3||||||||Thursday, July 4||||||||Friday, July 5 ... All times are "
            "Central Time ET +1 UTC +5|Regular Close|Early Close|PCP*|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|"
            "Open|Pre-opening**|Open|||| ... Grains and Oilseeds ||12:05:00 PM|12:30 - 16:00| |||"
            "||Markets Closed||||||||06:00:00 AM|08:30:00 AM"
        ),
        _Z19,
        (
            "Calendar Date|Wednesday, July 3||||||||Thursday, July 4||||||||Friday, July 5 ... "
            "All times are Central Time ET +1 UTC +5|Regular Close|Early Close|PCP*|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Halt|Pre-opening**|"
            "Open|Halt|Pre-opening**|Open|Pre-opening**|Open|||| ... Grains and Oilseeds ||"
            "12:05:00 PM|12:30 - 16:00| |||||Markets Closed||||||||06:00:00 AM|08:30:00 AM"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-independence-day-schedule.xls. CME Globex "
            "holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean "
            "meal and soybean oil share it). Friday July 5: Pre-opening 06:00, Open 08:30 (no "
            "Thursday-evening session)."
        ),
    ),
    date(2019, 11, 29): Citation(
        _Z19,
        (
            "Updated 10/07/2019|CME Group Globex Thanksgiving Holiday Schedule: November 27, "
            "2019 - November 29, 2019 ... Trade Date|Wednesday, November 27||Friday, November 29 "
            "... Calendar Date|Wednesday, November 27|||||||Thursday, November 28|||||||||Friday,"
            " November 29 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and "
            "Oilseeds |01:20:00 PM|14:30-16:00|04:45:00 PM|||||||||||||||08:30:00 AM|12:05:00 PM"
        ),
        _Z19,
        (
            "Calendar Date|Wednesday, November 27|||||||Thursday, November 28|||||||||Friday, "
            "November 29 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and "
            "Oilseeds |01:20:00 PM|14:30-16:00|04:45:00 PM|||||||||||||||08:30:00 AM|12:05:00 PM"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-thanksgiving-schedule.xls. CME Globex "
            "holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean "
            "meal and soybean oil share it). Pre-opening 16:45 on Wednesday for trade date "
            "Friday; Friday Open 08:30."
        ),
    ),
    date(2019, 12, 26): Citation(
        _Z19,
        (
            "Updated 10/01/2019|CME Group Globex Christmas Holiday Schedule: December 24, 2019 - "
            "December 26, 2019 ... Trade Date|Tuesday, December 24|Globex Closed|Thursday, "
            "December 26 ... Calendar Date|Tuesday, December 24|Wednesday, December 25|Wednesday,"
            " December 25||||||Thursday, December 26 ... All times are Central Time ET +1 UTC +6|"
            "Close|| Pre-opening**|Open|Pre opening**|Halt| Pre-opening**|Open|Pre-opening**|"
            "Open|Close|PCP* ... Grains and Oilseeds |12:05:00 PM|Globex Closed|||||||06:00:00 "
            "AM|08:30:00 AM|01:20:00 PM|14:30-16:00"
        ),
        _Z19,
        (
            "Calendar Date|Tuesday, December 24|Wednesday, December 25|Wednesday, December 25||||"
            "||Thursday, December 26 ... All times are Central Time ET +1 UTC +6|Close|| "
            "Pre-opening**|Open|Pre opening**|Halt| Pre-opening**|Open|Pre-opening**|Open|Close|"
            "PCP* ... Grains and Oilseeds |12:05:00 PM|Globex Closed|||||||06:00:00 AM|08:30:00 "
            "AM|01:20:00 PM|14:30-16:00"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-christmas-holiday-schedule.xls. CME Globex "
            "holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean "
            "meal and soybean oil share it). Thursday December 26: Pre-opening 06:00, Open 08:30."
        ),
    ),
    date(2020, 1, 2): Citation(
        _Z19,
        (
            "Updated 10/01/2019|CME Group Globex New Years Holiday Schedule: December 31, 2019 - "
            "January 2, 2020 ... Trade Date|Tuesday, December 31||Thursday, January 2 ... "
            "Calendar Date|Tuesday, December 31|Wednesday, January 1|Wednesday, January 1||||||"
            "Thursday, Jan 2 ... All times are Central Time ET +1 UTC +6| Close|| Pre-opening**|"
            "Open|Pre-opening**|halt| Pre-opening**|Open|Pre-opening**|Open|Close|PCP*|||||| ... "
            "Grains and Oilseeds |13:20 PCP: 14:30-16:00|Globex Closed|||||||06:00:00 AM|"
            "08:30:00 AM|01:20:00 PM|14:30-16:00"
        ),
        _Z19,
        (
            "Calendar Date|Tuesday, December 31|Wednesday, January 1|Wednesday, January 1||||||"
            "Thursday, Jan 2 ... All times are Central Time ET +1 UTC +6| Close|| Pre-opening**|"
            "Open|Pre-opening**|halt| Pre-opening**|Open|Pre-opening**|Open|Close|PCP*|||||| ... "
            "Grains and Oilseeds |13:20 PCP: 14:30-16:00|Globex Closed|||||||06:00:00 AM|"
            "08:30:00 AM|01:20:00 PM|14:30-16:00"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-2020-new-years-holiday-schedule.xls. CME "
            "Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, "
            "soybean meal and soybean oil share it). Thursday January 2: Pre-opening 06:00, Open "
            "08:30."
        ),
    ),
    date(2020, 11, 27): Citation(
        _Z20,
        (
            "Updated 10/13/2020|CME Group Globex Thanksgiving Holiday Schedule: November 25, "
            "2020 - November 27, 2020 ... Trade Date|Wednesday, November 25||Friday, November 27 "
            "... Calendar Date|Wednesday, November 25|||||||Thursday, November 26|||||||||Friday,"
            " November 27 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and "
            "Oilseeds |01:20:00 PM|14:30-16:00|04:45:00 PM|||||||||||||||08:30:00 AM|12:05:00 PM"
        ),
        _Z20,
        (
            "Calendar Date|Wednesday, November 25|||||||Thursday, November 26|||||||||Friday, "
            "November 27 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and "
            "Oilseeds |01:20:00 PM|14:30-16:00|04:45:00 PM|||||||||||||||08:30:00 AM|12:05:00 PM"
        ),
        note=(
            "Zip member 2020-thanksgiving-schedule.xls. CME Globex holiday schedule, row 'Grains "
            "and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil share it)."
        ),
    ),
    date(2021, 7, 6): Citation(
        _Z21,
        (
            "|CME Group Globex Independence Day Holiday Schedule: July 2, 2021 to July 6, 2021 "
            "... Trade Date|Friday, July 2|Tuesday, July 6 ... Calendar Date|Friday July 2|"
            "Sunday July 4|Monday July 5|Monday July 5 ... Product|CLOSE|OPEN|HALT|OPEN ... "
            "Grain & Oilseed |Regular Per Product|Markets Closed|Markets Closed|Tuesday July 6 "
            "Regular @ 0830 CT / 1330 UTC"
        ),
        _Z21,
        (
            "Calendar Date|Friday, July 2||Sunday, July 4|||||Monday, July 5||||||Tuesday, July "
            "6 ... All times are Central Time ET +1 UTC +5|Regular Close|PCP*|Pre-opening**|Open|"
            "Halt|Pre-opening**|Open|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|||||| ... Grains and Oilseeds |01:20:00 PM|14:30 - 16:00| |||||||"
            "||||06:00:00 AM|08:30:00 AM"
        ),
        note=(
            "Zip member 2021-independence-day-holiday-schedule-compact.xls. Time: zip member "
            "2021-independence-day-holiday-schedule.xls. Compact schedule: 'Tuesday July 6 "
            "Regular @ 0830 CT'; full schedule: Tuesday Pre-opening 06:00, Open 08:30."
        ),
    ),
    date(2021, 11, 26): Citation(
        _Z21,
        (
            "Updated 11/23/2021|CME Group Globex Thanksgiving Holiday Schedule: November 24, "
            "2021 - November 26, 2021 ... Trade Date|Wednesday, November 24||Friday, November 26 "
            "... Calendar Date|Wednesday, November 24|||||||Thursday, November 25|||||||||Friday,"
            " November 26 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and "
            "Oilseeds |01:20:00 PM|14:30-16:00|04:45:00 PM|||||||||||||||08:30:00 AM|12:05:00 PM"
        ),
        _Z21,
        (
            "Calendar Date|Wednesday, November 24|||||||Thursday, November 25|||||||||Friday, "
            "November 26 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and "
            "Oilseeds |01:20:00 PM|14:30-16:00|04:45:00 PM|||||||||||||||08:30:00 AM|12:05:00 PM"
        ),
        note=(
            "Zip member 2021-thanksgiving-holiday-schedule.xls. CME Globex holiday schedule, row "
            "'Grains and Oilseeds' (CBOT corn, wheat, soybeans, soybean meal and soybean oil "
            "share it)."
        ),
    ),
    date(2022, 7, 5): Citation(
        _HC + "2022-independence-day-holiday-schedule-compact.xls",
        (
            "|CME Group Globex Independence Day Holiday Schedule: July 1, 2022 to July 5, 2022 "
            "... Trade Date|Friday, July 1|Tuesday, July 5 ... Calendar Date|Friday July 1|"
            "Sunday July 3|Monday July 4|Monday July 4 ... Product|CLOSE|OPEN|HALT|OPEN ... "
            "Grain & Oilseed |Regular Per Product|Markets Closed|Markets Closed|Tuesday July 5 "
            "Regular @ 0830 CT / 1330 UTC"
        ),
        _HC + "2022-independence-day-holiday-schedule.xls",
        (
            "Calendar Date|Friday, July 1|||||Sunday, July 3|||||Monday, July 4|||||||||||"
            "Tuesday, July 5 ... All times are Central Time ET +1 UTC +5|Regular Close|PCP*| "
            "Pre-opening**|Open|Close|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|"
            "Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|"
            "Pre-opening**|Open|||||| ... Grains and Oilseeds |01:20:00 PM|14:30 - 16:00|||| ||||"
            "||||||||||||06:00:00 AM|08:30:00 AM"
        ),
        note=(
            "Compact schedule: 'Tuesday July 5 Regular @ 0830 CT'; full schedule: Tuesday "
            "Pre-opening 06:00, Open 08:30."
        ),
    ),
    date(2022, 11, 25): Citation(
        _HC + "2022-thanksgiving-holiday-schedule.xls",
        (
            "Updated 6/29/2022|CME Group Globex Thanksgiving Holiday Schedule: November 23, 2022 "
            "- November 25, 2022 ... Trade Date|Wednesday, November 23|||||Friday, November 25 "
            "... Calendar Date|Wednesday, November 23||||||||||Thursday, November 24||||||||||||"
            "Friday, November 25 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Halt|Halt|Pre-opening**|Open|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and Oilseeds |01:20:00 PM|"
            "14:30-16:00||||04:45:00 PM||||||||||||||||||08:30:00 AM|12:05:00 PM"
        ),
        _HC + "2022-thanksgiving-holiday-schedule.xls",
        (
            "Calendar Date|Wednesday, November 23||||||||||Thursday, November 24||||||||||||"
            "Friday, November 25 ... All times are Central Time ET +1 UTC +6|Regular Close|PCP*|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Halt|Halt|Pre-opening**|Open|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Pre-opening**|Open|Close ... Grains and Oilseeds |01:20:00 PM|"
            "14:30-16:00||||04:45:00 PM||||||||||||||||||08:30:00 AM|12:05:00 PM"
        ),
        note=(
            "CME Globex holiday schedule, row 'Grains and Oilseeds' (CBOT corn, wheat, soybeans, "
            "soybean meal and soybean oil share it)."
        ),
    ),
    date(2023, 7, 5): Citation(
        _TH + "4th-of-july-2023.pdf",
        (
            "PRODUCT NAME MONDAY, 3 JULY 2023 TUESDAY, 4 JULY 2023 WEDNESDAY, 5 JULY 2023 ... "
            "TRADE DATE: WED 5 JULY TRADE DATE: MON 3 JULY 06:00 (PREOPEN) 07:45 (PAUSED) 08:30 "
            "(OPEN)"
        ),
        _TH + "4th-of-july-2023.pdf",
        (
            "TRADE DATE: WED 5 JULY TRADE DATE: MON 3 JULY 06:00 (PREOPEN) 07:45 (PAUSED) 08:30 "
            "(OPEN)"
        ),
        note=(
            "CME holiday summary PDF, row 'GRAINS' (the summary uses the most actively traded "
            "instrument of each asset class); the table's column for each calendar day was read "
            "from the pdftotext -layout column positions. Wednesday column: TRADE DATE WED 5 "
            "JULY 06:00 PREOPEN, 08:30 OPEN (the 07:45 PAUSED between them belongs to the Monday "
            "column)."
        ),
    ),
    date(2023, 11, 24): Citation(
        _TH + "thanksgiving-day-2023.pdf",
        (
            "PRODUCT NAME WEDNESDAY, 22 NOVEMBER 2023 THURSDAY, 23 NOVEMBER 2023 FRIDAY, 24 "
            "NOVEMBER 2023 ... TRADE DATE: FRI 24 NOV GRAINS 13:30 (CLOSED) 08:30 (OPEN)"
        ),
        _TH + "thanksgiving-day-2023.pdf",
        "TRADE DATE: FRI 24 NOV GRAINS 13:30 (CLOSED) 08:30 (OPEN)",
        note=(
            "CME holiday summary PDF, row 'GRAINS' (the summary uses the most actively traded "
            "instrument of each asset class); the table's column for each calendar day was read "
            "from the pdftotext -layout column positions."
        ),
    ),
    date(2023, 12, 26): Citation(
        _TH + "christmas-day-2023.pdf",
        (
            "PRODUCT NAME MONDAY, 25 DECEMBER 2023 TUESDAY, 26 DECEMBER 2023 ... TRADE DATE: "
            "TUES 26 DEC 06:00 (PREOPEN) 08:30 (OPEN) 13:20 (PAUSED) 13:30 (CLOSED) GRAINS"
        ),
        _TH + "christmas-day-2023.pdf",
        (
            "TRADE DATE: TUES 26 DEC 06:00 (PREOPEN) 08:30 (OPEN) 13:20 (PAUSED) 13:30 (CLOSED) "
            "GRAINS"
        ),
        note=(
            "CME holiday summary PDF, row 'GRAINS' (the summary uses the most actively traded "
            "instrument of each asset class); the table's column for each calendar day was read "
            "from the pdftotext -layout column positions."
        ),
    ),
    date(2024, 1, 2): Citation(
        _TH + "new-years-day-2024.pdf",
        (
            "PRODUCT NAME MONDAY, 1 JANUARY 2024 TUESDAY, 2 JANUARY 2024 ... TRADE DATE: TUES 2 "
            "JAN 06:00 (PREOPEN) 08:30 (OPEN) 13:20 (PAUSED) 13:30 (CLOSED) GRAINS"
        ),
        _TH + "new-years-day-2024.pdf",
        "TRADE DATE: TUES 2 JAN 06:00 (PREOPEN) 08:30 (OPEN) 13:20 (PAUSED) 13:30 (CLOSED) GRAINS",
        note=(
            "CME holiday summary PDF, row 'GRAINS' (the summary uses the most actively traded "
            "instrument of each asset class); the table's column for each calendar day was read "
            "from the pdftotext -layout column positions."
        ),
    ),
    date(2024, 7, 5): Citation(
        _svc("2024-07-03", "2024-07-05", "1720455278680"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2024-07-04","events":[]},{"groupCode":"ZC","eventDate":"2024-07-05",'
            '"events":[{"tradingDate":"2024-07-05","eventTime":"06:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2024-07-05","eventTime":"08:30",'
            '"marketEventType":"open"}'
        ),
        _svc("2024-07-03", "2024-07-05", "1720455278680"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2024-07-05","events":[{"tradingDate":"2024-07-05","eventTime":"06:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2024-07-05","eventTime":"08:30",'
            '"marketEventType":"open"}'
        ),
        note=(
            "CME's trading-hours service record for Corn (ZC, product id 300), the most active "
            "grain contract; CME states the grain holiday hours per asset class or for its most "
            "active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and "
            "Oilseeds' row in the 2019-2022 Globex holiday schedules)."
        ),
    ),
    date(2024, 11, 29): Citation(
        _svc("2024-11-27", "2024-11-29", "1734710019535"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2024-11-28","events":[]},{"groupCode":"ZC","eventDate":"2024-11-29",'
            '"events":[{"tradingDate":"2024-11-29","eventTime":"08:30","marketEventType":"open"},'
            '{"tradingDate":"2024-11-29","eventTime":"12:05","marketEventType":"closed"}]}'
        ),
        _svc("2024-11-27", "2024-11-29", "1734710019535"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2024-11-29","events":[{"tradingDate":"2024-11-29","eventTime":"08:30",'
            '"marketEventType":"open"},{"tradingDate":"2024-11-29","eventTime":"12:05",'
            '"marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours service record for Corn (ZC, product id 300), the most active "
            "grain contract; CME states the grain holiday hours per asset class or for its most "
            "active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and "
            "Oilseeds' row in the 2019-2022 Globex holiday schedules)."
        ),
    ),
    date(2024, 12, 26): Citation(
        _svc("2024-12-24", "2024-12-26", "1734710019537"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2024-12-25","events":[]},{"groupCode":"ZC","eventDate":"2024-12-26",'
            '"events":[{"tradingDate":"2024-12-26","eventTime":"06:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2024-12-26","eventTime":"08:30",'
            '"marketEventType":"open"}'
        ),
        _svc("2024-12-24", "2024-12-26", "1734710019537"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2024-12-26","events":[{"tradingDate":"2024-12-26","eventTime":"06:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2024-12-26","eventTime":"08:30",'
            '"marketEventType":"open"}'
        ),
        note=(
            "CME's trading-hours service record for Corn (ZC, product id 300), the most active "
            "grain contract; CME states the grain holiday hours per asset class or for its most "
            "active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and "
            "Oilseeds' row in the 2019-2022 Globex holiday schedules)."
        ),
    ),
    date(2025, 1, 2): Citation(
        _svc("2024-12-31", "2025-01-02", "1734710019538"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2025-01-01","events":[]},{"groupCode":"ZC","eventDate":"2025-01-02",'
            '"events":[{"tradingDate":"2025-01-02","eventTime":"06:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2025-01-02","eventTime":"08:30",'
            '"marketEventType":"open"}'
        ),
        _svc("2024-12-31", "2025-01-02", "1734710019538"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2025-01-02","events":[{"tradingDate":"2025-01-02","eventTime":"06:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2025-01-02","eventTime":"08:30",'
            '"marketEventType":"open"}'
        ),
        note=(
            "CME's trading-hours service record for Corn (ZC, product id 300), the most active "
            "grain contract; CME states the grain holiday hours per asset class or for its most "
            "active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and "
            "Oilseeds' row in the 2019-2022 Globex holiday schedules)."
        ),
    ),
    date(2025, 11, 28): Citation(
        _svc("2025-11-26", "2025-11-28", "1769649703060"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2025-11-27","events":[]},{"groupCode":"ZC","eventDate":"2025-11-28",'
            '"events":[{"tradingDate":"2025-11-28","eventTime":"07:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"08:30",'
            '"marketEventType":"open"},{"tradingDate":"2025-11-28","eventTime":"12:05",'
            '"marketEventType":"closed"}]}'
        ),
        _svc("2025-11-26", "2025-11-28", "1769649703060"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28","eventTime":"07:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"08:30",'
            '"marketEventType":"open"},{"tradingDate":"2025-11-28","eventTime":"12:05",'
            '"marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours service record for Corn (ZC, product id 300), the most active "
            "grain contract; CME states the grain holiday hours per asset class or for its most "
            "active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and "
            "Oilseeds' row in the 2019-2022 Globex holiday schedules). The 07:00 CT pre-open in "
            "this post-event record follows the 2025-11-27/28 CME Globex outage; the 08:30 CT "
            "open is the scheduled one."
        ),
    ),
    date(2025, 12, 26): Citation(
        _svc("2025-12-24", "2025-12-26", "1769649703064"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2025-12-25","events":[]},{"groupCode":"ZC","eventDate":"2025-12-26",'
            '"events":[{"tradingDate":"2025-12-26","eventTime":"06:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2025-12-26","eventTime":"08:30",'
            '"marketEventType":"open"}'
        ),
        _svc("2025-12-24", "2025-12-26", "1769649703064"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2025-12-26","events":[{"tradingDate":"2025-12-26","eventTime":"06:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2025-12-26","eventTime":"08:30",'
            '"marketEventType":"open"}'
        ),
        note=(
            "CME's trading-hours service record for Corn (ZC, product id 300), the most active "
            "grain contract; CME states the grain holiday hours per asset class or for its most "
            "active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and "
            "Oilseeds' row in the 2019-2022 Globex holiday schedules)."
        ),
    ),
    date(2026, 1, 2): Citation(
        _svc("2025-12-31", "2026-01-02", "1769649703066"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2026-01-01","events":[]},{"groupCode":"ZC","eventDate":"2026-01-02",'
            '"events":[{"tradingDate":"2026-01-02","eventTime":"06:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2026-01-02","eventTime":"08:30",'
            '"marketEventType":"open"}'
        ),
        _svc("2025-12-31", "2026-01-02", "1769649703066"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2026-01-02","events":[{"tradingDate":"2026-01-02","eventTime":"06:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2026-01-02","eventTime":"08:30",'
            '"marketEventType":"open"}'
        ),
        note=(
            "CME's trading-hours service record for Corn (ZC, product id 300), the most active "
            "grain contract; CME states the grain holiday hours per asset class or for its most "
            "active contract, and ZW, ZS, ZM and ZL share them (they form CME's 'Grains and "
            "Oilseeds' row in the 2019-2022 Globex holiday schedules)."
        ),
    ),
}

# Days CME's documents show as regular grain days near holidays, so they carry no entry. Two
# (2023-12-22, 2023-12-29) rest on settlement notices only (see their notes).
NO_ENTRY_FINDINGS: dict[date, Citation] = {
    date(2019, 12, 31): Citation(
        _Z19,
        (
            "Updated 10/01/2019|CME Group Globex New Years Holiday Schedule: December 31, 2019 - "
            "January 2, 2020 ... Trade Date|Tuesday, December 31||Thursday, January 2 ... "
            "Calendar Date|Tuesday, December 31|Wednesday, January 1|Wednesday, January 1||||||"
            "Thursday, Jan 2 ... All times are Central Time ET +1 UTC +6| Close|| Pre-opening**|"
            "Open|Pre-opening**|halt| Pre-opening**|Open|Pre-opening**|Open|Close|PCP*|||||| ... "
            "Grains and Oilseeds |13:20 PCP: 14:30-16:00|Globex Closed|||||||06:00:00 AM|"
            "08:30:00 AM|01:20:00 PM|14:30-16:00"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-2020-new-years-holiday-schedule.xls. New "
            "Year's Eve: CME's schedule gives the grain 'Close 13:20 PCP: 14:30-16:00' "
            "(regular); the evening session is absent because 2020-01-01 is closed."
        ),
    ),
    date(2020, 7, 6): Citation(
        _Z20,
        (
            "Updated 6/26/2020|CME Group Globex Independence Day Holiday Schedule: July 2, 2020 "
            "to July 6, 2020 ... Trade Date|Thursday, July 2||Monday, July 6 ... Calendar Date|"
            "Thursday, July 2||||||||Friday, July 3|||Sunday, July 5|||||Monday, July 6 ... All "
            "times are Central Time ET +1 UTC +5|Regular Close|Early Close|PCP*|Pre-opening**|"
            "Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Close|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Pre-opening**|Open|||||| ... Grains and Oilseeds ||12:05:00 PM|"
            "12:30 - 16:00| |||||Markets Closed|||04:00:00 PM|07:00:00 PM||||08:00:00 AM|"
            "08:30:00 AM"
        ),
        note=(
            "Zip member 2020-independence-day-schedule.xls. Monday after the observed "
            "Independence Day: grain Globex opens Sunday July 5 at 19:00 CT (regular overnight), "
            "not a late open."
        ),
    ),
    date(2020, 12, 28): Citation(
        _Z20,
        (
            "Updated 11/17/2020|CME Group Globex Christmas Holiday Schedule: December 24, 2020 - "
            "December 28, 2020 ... Trade Date|Thursday, December 24|Globex Closed|Monday, "
            "December 28 ... Calendar Date|Thursday, December 24|Friday, December 25|Sunday, "
            "December 27||||||Monday, December 28 ... All times are Central Time ET +1 UTC +6|"
            "Close|| Pre-opening**|Open|Pre opening**|Halt| Pre-opening**|Open|Pre-opening**|"
            "Open|Close|PCP* ... Grains and Oilseeds |12:05:00 PM|Globex Closed|04:00:00 PM|"
            "07:00:00 PM|||||08:00:00 AM|08:30:00 AM|01:20:00 PM|14:30-16:00"
        ),
        note=(
            "Zip member 2020-christmas-holiday-schedule.xls. Monday after Christmas: Sunday "
            "December 27 19:00 CT open, Monday pre-open 08:00 and open 08:30 (the regular "
            "morning pause), not a late open."
        ),
    ),
    date(2020, 12, 31): Citation(
        _Z20,
        (
            "Updated 12/09/2020|CME Group Globex New Years Holiday Schedule: December 31, 2020 - "
            "January 4, 2021 ... Trade Date|Thursday, December 31||Monday, January 4 ... "
            "Calendar Date|Thursday, December 31|Friday, January 1|Sunday, January 3||||||Monday,"
            " January 4 ... All times are Central Time ET +1 UTC +6| Close|| Pre-opening**|Open|"
            "Pre-opening**|halt| Pre-opening**|Open|Pre-opening**|Open|Close|PCP*|||||| ... "
            "Grains and Oilseeds |13:20 PCP: 14:30-16:00|Globex Closed|04:00:00 PM|07:00:00 PM|||"
            "||8:00|08:30:00 AM|01:20:00 PM|14:30-16:00"
        ),
        note=(
            "Zip member 2021-new-years-holiday-schedule.xls. New Year's Eve: regular 13:20 CT "
            "grain close."
        ),
    ),
    date(2021, 1, 4): Citation(
        _Z20,
        (
            "Updated 12/09/2020|CME Group Globex New Years Holiday Schedule: December 31, 2020 - "
            "January 4, 2021 ... Trade Date|Thursday, December 31||Monday, January 4 ... "
            "Calendar Date|Thursday, December 31|Friday, January 1|Sunday, January 3||||||Monday,"
            " January 4 ... All times are Central Time ET +1 UTC +6| Close|| Pre-opening**|Open|"
            "Pre-opening**|halt| Pre-opening**|Open|Pre-opening**|Open|Close|PCP*|||||| ... "
            "Grains and Oilseeds |13:20 PCP: 14:30-16:00|Globex Closed|04:00:00 PM|07:00:00 PM|||"
            "||8:00|08:30:00 AM|01:20:00 PM|14:30-16:00"
        ),
        note=(
            "Zip member 2021-new-years-holiday-schedule.xls. Monday after New Year's Day: Sunday "
            "January 3 19:00 CT open (regular)."
        ),
    ),
    date(2021, 7, 2): Citation(
        _Z21,
        (
            "Updated 7/1/2021|CME Group Globex Independence Day Holiday Schedule: July 2, 2021 "
            "to July 6, 2021 ... Trade Date|Friday, July 2||Tuesday, July 6 ... Calendar Date|"
            "Friday, July 2||Sunday, July 4|||||Monday, July 5||||||Tuesday, July 6 ... All "
            "times are Central Time ET +1 UTC +5|Regular Close|PCP*|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|"
            "Open|||||| ... Grains and Oilseeds |01:20:00 PM|14:30 - 16:00| |||||||||||06:00:00 "
            "AM|08:30:00 AM"
        ),
        note=(
            "Zip member 2021-independence-day-holiday-schedule.xls. Friday before the observed "
            "Independence Day: 'Regular Close' 13:20 CT. CME's FINAL settlement notice (capture "
            "2024-07-22) says 'Agricultural Products (Grains, Livestock, Dairy, Commodity Index) "
            "Normal Settlement Times'; its January 2021 draft (capture 2021-01-15, the copy in "
            "the shared cache) had 'Agricultural Products 12:00:00 CT' (superseded; "
            "extra_evidence)."
        ),
    ),
    date(2021, 12, 23): Citation(
        _Z21,
        (
            "Updated 12/01/2021|CME Group Globex Christmas Holiday Schedule: December 24, 2021 - "
            "December 27, 2021 ... Trade Date|Thursday, December 23||||||||||Monday, December 27 "
            "... Calendar Date|Thursday, December 23|||||||||||||Friday, December 24||||||||||"
            "Sunday, December 26||||||Monday, Dec 27 ... All times are Central Time ET +1 UTC +6|"
            "Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|"
            "Pre-opening**|Open|Close||Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Close| Pre-opening**|Open|Pre opening**|Halt| Pre-opening**|Open|"
            "Pre-opening**|Open|Close|PCP* ... Grains and Oilseeds |13:20 (**PCP 14:30-16:00)||||"
            "|||||||||Globex Closed||||||||||04:00:00 PM|07:00:00 PM|||||08:00:00 AM|08:30:00 AM|"
            "01:20:00 PM|14:30-16:00"
        ),
        note=(
            "Zip member 2021-christmas-holiday-schedule.xls. Thursday before the observed "
            "Christmas: grain close '13:20 (**PCP 14:30-16:00)'. CME's FINAL settlement notice "
            "(capture 2021-12-22) says agricultural products settle at normal times; the January "
            "2021 draft (capture 2021-01-15) had 12:00:00 CT (superseded; extra_evidence)."
        ),
    ),
    date(2021, 12, 27): Citation(
        _Z21,
        (
            "Updated 12/01/2021|CME Group Globex Christmas Holiday Schedule: December 24, 2021 - "
            "December 27, 2021 ... Trade Date|Thursday, December 23||||||||||Monday, December 27 "
            "... Calendar Date|Thursday, December 23|||||||||||||Friday, December 24||||||||||"
            "Sunday, December 26||||||Monday, Dec 27 ... All times are Central Time ET +1 UTC +6|"
            "Close|PCP*|Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|"
            "Pre-opening**|Open|Close||Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Close| Pre-opening**|Open|Pre opening**|Halt| Pre-opening**|Open|"
            "Pre-opening**|Open|Close|PCP* ... Grains and Oilseeds |13:20 (**PCP 14:30-16:00)||||"
            "|||||||||Globex Closed||||||||||04:00:00 PM|07:00:00 PM|||||08:00:00 AM|08:30:00 AM|"
            "01:20:00 PM|14:30-16:00"
        ),
        note=(
            "Zip member 2021-christmas-holiday-schedule.xls. Monday after the observed "
            "Christmas: Sunday December 26 19:00 CT open (regular)."
        ),
    ),
    date(2021, 12, 31): Citation(
        _Z21,
        (
            "Updated 12/28/2021|CME Group Globex New Year's Holiday Schedule: December 30, 2021 "
            "- January 3, 2022 ... Trade Date|Thurs, Dec. 30|Friday, December 31||||||||||||||"
            "Monday, January 3 ... Calendar Date|Thursday, December 30||||||||||Friday, December "
            "31||||||||Sunday, January 2||||||Monday, January 3 ... All times are Central Time "
            "ET +1 UTC +6| Close| Pre-opening**|Open|Pre-opening**|halt| Pre-opening**|Open|halt|"
            " Pre-opening**|Open|halt|Pre-opening**|Open|Close|PCP*|Pre-opening**|Open|Close| "
            "Pre-opening**|Open|Pre-opening**|halt| Pre-opening**|Open|Pre-opening**|Open ... "
            "Grains and Oilseeds |13:20 PCP: 14:30-16:00|04:45:00 PM|07:00:00 PM|||||||||8:00|"
            "08:30:00 AM|01:20:00 PM|14:30-16:00||||04:00:00 PM|07:00:00 PM|NORMAL||||SCHEDULE"
        ),
        note=(
            "Zip member 2022-new-years-holiday-schedule.xls. New Year's Eve 2021 (New Year's Day "
            "fell on a Saturday): Thursday 19:00 CT open, Friday 08:30-13:20 CT; a regular grain "
            "day."
        ),
    ),
    date(2022, 1, 3): Citation(
        _Z21,
        (
            "Updated 12/28/2021|CME Group Globex New Year's Holiday Schedule: December 30, 2021 "
            "- January 3, 2022 ... Trade Date|Thurs, Dec. 30|Friday, December 31||||||||||||||"
            "Monday, January 3 ... Calendar Date|Thursday, December 30||||||||||Friday, December "
            "31||||||||Sunday, January 2||||||Monday, January 3 ... All times are Central Time "
            "ET +1 UTC +6| Close| Pre-opening**|Open|Pre-opening**|halt| Pre-opening**|Open|halt|"
            " Pre-opening**|Open|halt|Pre-opening**|Open|Close|PCP*|Pre-opening**|Open|Close| "
            "Pre-opening**|Open|Pre-opening**|halt| Pre-opening**|Open|Pre-opening**|Open ... "
            "Grains and Oilseeds |13:20 PCP: 14:30-16:00|04:45:00 PM|07:00:00 PM|||||||||8:00|"
            "08:30:00 AM|01:20:00 PM|14:30-16:00||||04:00:00 PM|07:00:00 PM|NORMAL||||SCHEDULE"
        ),
        note=(
            "Zip member 2022-new-years-holiday-schedule.xls. Monday after New Year's Day on a "
            "Saturday: Sunday January 2 19:00 CT open, 'NORMAL SCHEDULE' (no closure; the equity "
            "D.1f finding agrees)."
        ),
    ),
    date(2022, 7, 1): Citation(
        _HC + "2022-independence-day-holiday-schedule.xls",
        (
            "Updated 6/29/2022|CME Group Globex Independence Day Holiday Schedule: July 1, 2022 "
            "to July 5, 2022 ... Trade Date|Friday, July 1||Tuesday, July 5 ... Calendar Date|"
            "Friday, July 1|||||Sunday, July 3|||||Monday, July 4|||||||||||Tuesday, July 5 ... "
            "All times are Central Time ET +1 UTC +5|Regular Close|PCP*| Pre-opening**|Open|"
            "Close|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|Open|Halt|"
            "Pre-opening**|Open|Halt|Pre-opening**|Open|Halt|Pre-opening**|Open|Pre-opening**|"
            "Open|||||| ... Grains and Oilseeds |01:20:00 PM|14:30 - 16:00|||| ||||||||||||||||"
            "06:00:00 AM|08:30:00 AM"
        ),
        note="Friday before Independence Day: 'Regular Close' 13:20 CT.",
    ),
    date(2022, 12, 23): Citation(
        _HC + "2022-christmas-holiday-schedule.xls",
        (
            "Updated 6/29/2022|CME Group Globex Christmas Holiday Schedule: December 23, 2022 - "
            "December 27, 2022 ... Trade Date|Friday, December 23|||||Tuesday, December 27 ... "
            "Calendar Date|Friday, December 23||||||||Monday, December 26||||||||||||||||Tuesday,"
            " December 27 ... All times are Central Time ET +1 UTC +6|Close|PCP*|Pre-opening**|"
            "Open|Halt| Pre-opening**|Open|Close||Pre-opening**|Open|Halt|Pre-opening**|Open|"
            "Halt|Pre-opening**|Open|Close| Pre-opening**|Open|Pre opening**|Halt| Pre-opening**|"
            "Open|Pre-opening**|Open|Close|PCP* ... Grains and Oilseeds |13:20 (**PCP "
            "14:30-16:00)||||||||Globex Closed||||||||||04:00:00 PM|07:00:00 PM|||||08:00:00 AM|"
            "08:30:00 AM|01:20:00 PM|14:30-16:00"
        ),
        note="Friday before the observed Christmas: grain close '13:20 (**PCP 14:30-16:00)'.",
    ),
    date(2022, 12, 27): Citation(
        _HC + "2022-christmas-holiday-schedule.xls",
        (
            "Updated 6/29/2022|CME Group Globex Christmas Holiday Schedule: December 23, 2022 - "
            "December 27, 2022 ... Trade Date|Friday, December 23|||||Tuesday, December 27 ... "
            "Calendar Date|Friday, December 23||||||||Monday, December 26||||||||||||||||Tuesday,"
            " December 27 ... All times are Central Time ET +1 UTC +6|Close|PCP*|Pre-opening**|"
            "Open|Halt| Pre-opening**|Open|Close||Pre-opening**|Open|Halt|Pre-opening**|Open|"
            "Halt|Pre-opening**|Open|Close| Pre-opening**|Open|Pre opening**|Halt| Pre-opening**|"
            "Open|Pre-opening**|Open|Close|PCP* ... Grains and Oilseeds |13:20 (**PCP "
            "14:30-16:00)||||||||Globex Closed||||||||||04:00:00 PM|07:00:00 PM|||||08:00:00 AM|"
            "08:30:00 AM|01:20:00 PM|14:30-16:00"
        ),
        note="Tuesday after the observed Christmas: Monday 19:00 CT open (regular overnight).",
    ),
    date(2023, 1, 3): Citation(
        _HC + "2023-new-years-holiday-schedule.xls",
        (
            "Updated 6/29/22|CME Group Globex New Year's Holiday Schedule: December 30, 2022 - "
            "January 3, 2023 ... Trade Date|Friday, December 30|Tuesday, January 3 ... Calendar "
            "Date|Friday, December 30||||Monday, January 2|Monday, January 2||||||Tuesday, "
            "January 3 ... All times are Central Time ET +1 UTC +6| Close| Pre-opening**|Open|"
            "Close|| Pre-opening**|Open|Pre-opening**|halt| Pre-opening**|Open|Close|"
            "Pre-opening**|Open|Close|PCP* ... Grains and Oilseeds |13:20 PCP: 14:30-16:00||||"
            "Globex Closed|04:00:00 PM|07:00:00 PM|NORMAL|||||SCHEDULE"
        ),
        note="Tuesday after the observed New Year's Day: Monday 19:00 CT open, 'NORMAL SCHEDULE'.",
    ),
    date(2023, 7, 3): Citation(
        _TH + "4th-of-july-2023.pdf",
        (
            "PRODUCT NAME MONDAY, 3 JULY 2023 TUESDAY, 4 JULY 2023 WEDNESDAY, 5 JULY 2023 ... "
            "TRADE DATE: WED 5 JULY TRADE DATE: MON 3 JULY 06:00 (PREOPEN) 07:45 (PAUSED) 08:30 "
            "(OPEN) 08:00 (PREOPEN) 13:20 (PAUSED) 08:30 (OPEN) 13:30 (CLOSED) GRAINS 14:30 "
            "(PCP) 13:20 (PAUSED) 13:30 (CLOSED) 16:00 (CLOSED)"
        ),
        note=(
            "Monday before Independence Day: the GRAINS Monday column is a regular day (07:45 "
            "PAUSED, 08:00 PREOPEN, 08:30 OPEN, 13:20 PAUSED, 13:30 CLOSED, 14:30 PCP, 16:00 "
            "CLOSED); unlike 2019-07-03 and 2020-07-02 there is no 12:05 CT early close."
        ),
    ),
    date(2023, 12, 22): Citation(
        _HC + "christmas-holiday-settlement-times-2023.pdf",
        (
            "Christmas Day Holiday 12/25/2023 Settlement Times Friday, December 22, 2023 "
            "Interest Rate Products 12:00:00 CT All other products will settle at their normal "
            "times"
        ),
        note=(
            "Friday before Christmas (Monday): SETTLEMENT NOTICE ONLY (capture 2023-02-03): "
            "agricultural products settle at their normal time; no CME grain Globex schedule for "
            "this day was retrieved. Regular session assumed; listed under gaps."
        ),
    ),
    date(2023, 12, 29): Citation(
        _HC + "new-years-eve-holiday-settlement-times-2024.pdf",
        (
            "New Year’s Eve Holiday 12/29/2023 Settlement Times Friday, December 29, 2023 ... "
            "All other products will settle at their normal times"
        ),
        note=(
            "Friday before New Year's Day (Monday): SETTLEMENT NOTICE ONLY (capture 2023-02-03): "
            "only rates settle early; no CME grain Globex schedule for this day was retrieved. "
            "Regular session assumed; listed under gaps."
        ),
    ),
    date(2024, 7, 3): Citation(
        _svc("2024-07-03", "2024-07-05", "1720455278680"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2024-07-03","events":[{"tradingDate":"2024-07-03","eventTime":"07:45",'
            '"marketEventType":"paused"},{"tradingDate":"2024-07-03","eventTime":"08:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2024-07-03","eventTime":"08:30",'
            '"marketEventType":"open"},{"tradingDate":"2024-07-03","eventTime":"13:20",'
            '"marketEventType":"paused"},{"tradingDate":"2024-07-03","eventTime":"13:30",'
            '"marketEventType":"closed"},{"tradingDate":"2024-07-03","eventTime":"14:30",'
            '"marketEventType":"pcp"},{"tradingDate":"2024-07-03","eventTime":"16:00",'
            '"marketEventType":"closed"}]}'
        ),
        note=(
            "Wednesday before Independence Day: regular grain events (07:45 paused, 08:30 open, "
            "13:20 paused, 13:30 closed ...), no 12:05 CT early close; no evening open "
            "(2024-07-04 closed)."
        ),
    ),
    date(2024, 12, 31): Citation(
        _svc("2024-12-31", "2025-01-02", "1734710019538"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2024-12-31","events":[{"tradingDate":"2024-12-31","eventTime":"07:45",'
            '"marketEventType":"paused"},{"tradingDate":"2024-12-31","eventTime":"08:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2024-12-31","eventTime":"08:30",'
            '"marketEventType":"open"},{"tradingDate":"2024-12-31","eventTime":"13:20",'
            '"marketEventType":"paused"},{"tradingDate":"2024-12-31","eventTime":"13:30",'
            '"marketEventType":"closed"},{"tradingDate":"2024-12-31","eventTime":"14:30",'
            '"marketEventType":"pcp"},{"tradingDate":"2024-12-31","eventTime":"16:00",'
            '"marketEventType":"closed"}]}'
        ),
        note="New Year's Eve: regular grain day (13:20 CT).",
    ),
    date(2025, 7, 3): Citation(
        _svc("2025-07-03", "2025-07-05", "1734710019545"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2025-07-03","events":[{"tradingDate":"2025-07-03","eventTime":"07:45",'
            '"marketEventType":"paused"},{"tradingDate":"2025-07-03","eventTime":"08:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2025-07-03","eventTime":"08:30",'
            '"marketEventType":"open"},{"tradingDate":"2025-07-03","eventTime":"13:20",'
            '"marketEventType":"paused"},{"tradingDate":"2025-07-03","eventTime":"13:30",'
            '"marketEventType":"closed"},{"tradingDate":"2025-07-03","eventTime":"14:30",'
            '"marketEventType":"pcp"},{"tradingDate":"2025-07-03","eventTime":"16:00",'
            '"marketEventType":"closed"}]}'
        ),
        note="Thursday before Independence Day: regular grain day (13:20 CT), no early close.",
    ),
    date(2025, 12, 31): Citation(
        _svc("2025-12-31", "2026-01-02", "1769649703066"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2025-12-31","events":[{"tradingDate":"2025-12-31","eventTime":"07:45",'
            '"marketEventType":"paused"},{"tradingDate":"2025-12-31","eventTime":"08:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2025-12-31","eventTime":"08:30",'
            '"marketEventType":"open"},{"tradingDate":"2025-12-31","eventTime":"13:20",'
            '"marketEventType":"paused"},{"tradingDate":"2025-12-31","eventTime":"13:30",'
            '"marketEventType":"closed"},{"tradingDate":"2025-12-31","eventTime":"14:30",'
            '"marketEventType":"pcp"},{"tradingDate":"2025-12-31","eventTime":"16:00",'
            '"marketEventType":"closed"}]}'
        ),
        note="New Year's Eve: regular grain day (13:20 CT).",
    ),
    date(2026, 4, 2): Citation(
        _svc("2026-04-01", "2026-04-03", "1743113432016"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2026-04-02","events":[{"tradingDate":"2026-04-02","eventTime":"07:45",'
            '"marketEventType":"paused"},{"tradingDate":"2026-04-02","eventTime":"08:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2026-04-02","eventTime":"08:30",'
            '"marketEventType":"open"},{"tradingDate":"2026-04-02","eventTime":"13:20",'
            '"marketEventType":"paused"},{"tradingDate":"2026-04-02","eventTime":"13:30",'
            '"marketEventType":"closed"},{"tradingDate":"2026-04-02","eventTime":"14:30",'
            '"marketEventType":"pcp"},{"tradingDate":"2026-04-02","eventTime":"16:00",'
            '"marketEventType":"closed"}]}'
        ),
        note="Thursday before Good Friday: regular grain day (13:20 CT); no evening open.",
    ),
}

# Regular hours (cme_grain_hours: the hours_* keys) and settlement periods (settle_*) behind
# SESSIONS.
SESSION_SOURCES: dict[str, Citation] = {
    "cme_grain_hours": Citation(
        "https://www.cmegroup.com/trading/agricultural/grain-and-oilseed/corn_contract_specifications.html",
        (
            "Trading Hours Sunday – Friday, 7:00 p.m. – 7:45 a.m. CT and Monday – Friday, 8:30 "
            "a.m. – 1:20 p.m. CT ... CME Globex: ZC"
        ),
        note=(
            "Primary citation of SESSIONS: CME contract specifications, Corn (capture "
            "2019-04-06). The same hours for ZW, ZS, ZM, ZL: hours_2019_zw..hours_2019_zl; "
            "unchanged in CME's ZC service records 2024 and 2026: hours_2024_zc, hours_2026_zc; "
            "no later change in CME's grain advisory list: hours_history."
        ),
    ),
    "hours_2019_zc": Citation(
        "https://www.cmegroup.com/trading/agricultural/grain-and-oilseed/corn_contract_specifications.html",
        (
            "Trading Hours Sunday – Friday, 7:00 p.m. – 7:45 a.m. CT and Monday – Friday, 8:30 "
            "a.m. – 1:20 p.m. CT ... CME Globex: ZC"
        ),
        note="CME contract specifications, Corn (capture 2019-04-06).",
    ),
    "hours_2019_zw": Citation(
        "https://www.cmegroup.com/trading/agricultural/grain-and-oilseed/wheat_contract_specifications.html",
        (
            "Trading Hours Sunday – Friday: 7:00 p.m. – 7:45 a.m. CT and Monday – Friday: 8:30 "
            "a.m. – 1:20 p.m. CT ... CME Globex: ZW"
        ),
        note="CME contract specifications, Chicago SRW Wheat (capture 2019-07-20).",
    ),
    "hours_2019_zs": Citation(
        "https://www.cmegroup.com/trading/agricultural/grain-and-oilseed/soybean_contract_specifications.html",
        (
            "Trading Hours Sunday – Friday, 7:00 p.m. – 7:45 a.m. CT and Monday – Friday, 8:30 "
            "a.m. – 1:20 p.m. CT ... CME Globex: ZS"
        ),
        note="CME contract specifications, Soybean (capture 2019-03-28).",
    ),
    "hours_2019_zm": Citation(
        "https://www.cmegroup.com/trading/agricultural/grain-and-oilseed/soybean-meal_contract_specifications.html",
        (
            "Trading Hours Sunday – Friday, 7:00 p.m. – 7:45 a.m. CT and Monday – Friday, 8:30 "
            "a.m. – 1:20 p.m. CT ... CME Globex: ZM"
        ),
        note="CME contract specifications, Soybean Meal (capture 2019-07-18).",
    ),
    "hours_2019_zl": Citation(
        "https://www.cmegroup.com/trading/agricultural/grain-and-oilseed/soybean-oil_contract_specifications.html",
        (
            "Trading Hours Sunday – Friday: 7:00 p.m. – 7:45 a.m. CT and Monday – Friday: 8:30 "
            "a.m. – 1:20 p.m. CT ... CME Globex: ZL"
        ),
        note="CME contract specifications, Soybean Oil (capture 2019-07-21).",
    ),
    "hours_2024_zc": Citation(
        _svc("2024-11-27", "2024-11-29", "1734710019535"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2024-11-27","events":[{"tradingDate":"2024-11-27","eventTime":"07:45",'
            '"marketEventType":"paused"},{"tradingDate":"2024-11-27","eventTime":"08:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2024-11-27","eventTime":"08:30",'
            '"marketEventType":"open"},{"tradingDate":"2024-11-27","eventTime":"13:20",'
            '"marketEventType":"paused"},{"tradingDate":"2024-11-27","eventTime":"13:30",'
            '"marketEventType":"closed"},{"tradingDate":"2024-11-27","eventTime":"14:30",'
            '"marketEventType":"pcp"},{"tradingDate":"2024-11-27","eventTime":"16:00",'
            '"marketEventType":"closed"},{"tradingDate":"2024-11-29","eventTime":"16:45",'
            '"marketEventType":"preopen"}]}'
        ),
        note=(
            "A regular grain day in CME's ZC service record (2024-11-27): 07:45 paused, 08:00 "
            "preopen, 08:30 open, 13:20 paused, 13:30 closed; the regular day also carries a "
            "19:00 CT open for the next trade date (for example 2024-01-16 in the MLK record)."
        ),
    ),
    "hours_2026_zc": Citation(
        _svc("2026-04-01", "2026-04-03", "1743113432016"),
        (
            '"globex":"ZC","prodGroup":"ZC","name":"Corn Futures","id":300 ... {"groupCode":"ZC",'
            '"eventDate":"2026-04-01","events":[{"tradingDate":"2026-04-01","eventTime":"07:45",'
            '"marketEventType":"paused"},{"tradingDate":"2026-04-01","eventTime":"08:00",'
            '"marketEventType":"preopen"},{"tradingDate":"2026-04-01","eventTime":"08:30",'
            '"marketEventType":"open"},{"tradingDate":"2026-04-01","eventTime":"13:20",'
            '"marketEventType":"paused"},{"tradingDate":"2026-04-01","eventTime":"13:30",'
            '"marketEventType":"closed"},{"tradingDate":"2026-04-01","eventTime":"14:30",'
            '"marketEventType":"pcp"},{"tradingDate":"2026-04-01","eventTime":"16:00",'
            '"marketEventType":"closed"},{"tradingDate":"2026-04-02","eventTime":"16:45",'
            '"marketEventType":"preopen"},{"tradingDate":"2026-04-02","eventTime":"19:00",'
            '"marketEventType":"open"}]}'
        ),
        note=(
            "A regular grain day in CME's ZC service record (2026-04-01): the same events, and "
            "the 16:45 preopen and 19:00 open for trade date 2026-04-02."
        ),
    ),
    "hours_history": Citation(
        _WIKI + "457414829/Grains",
        (
            "Agriculture Advisories Changes in Trading Hours for CBOT Grain and Oilseed and KCBT "
            "Markets 04/01/2013"
        ),
        note=(
            "CME client-systems wiki, Grains settlement page (version 2026-08-20): its advisory "
            "list names no grain trading-hours change after 04/01/2013."
        ),
    ),
    "settle_grains": Citation(
        _WIKI + "457414829/Grains",
        (
            "CME Group staff determines the daily settlements in CBOT Corn (ZC), Wheat (ZW), "
            "Rice (ZR), Oats (ZO), Soybean (ZS), Soybean Meal (ZM), Soybean Oil (ZL) and KC HRW "
            "Wheat (KE) futures based on trading activity on CME Globex between 13:14:00 and "
            "13:15:00 Central Time (CT), the settlement period."
        ),
        note="CME client-systems wiki, Grains (page 457414829, version 2026-08-20).",
    ),
    "settle_zc": Citation(
        _WIKI + "457090243/Corn",
        (
            "CME Group staff determines the daily settlements in CBOT Corn (ZC) futures on "
            "trading activity on CME Globex between 13:14:00 and 13:15:00 Central Time (CT), the "
            "settlement period."
        ),
        note="CME client-systems wiki, Corn (page 457090243, version 2025-02-14).",
    ),
    "settle_zw": Citation(
        _WIKI + "457321091/Wheat",
        (
            "CME Group staff determines the daily settlements in CBOT Wheat (ZW) futures based "
            "on trading activity on CME Globex between 13:14:00 and 13:15:00 Central Time (CT), "
            "the settlement period."
        ),
        note="CME client-systems wiki, Wheat (page 457321091, version 2025-12-31).",
    ),
    "settle_zs": Citation(
        _WIKI + "457090434/Soybeans",
        (
            "CME Group staff determines the daily settlements in CBOT Soybeans (ZS) futures "
            "based on trading activity on CME Globex between 13:14:00 and 13:15:00 Central Time "
            "(CT), the settlement period."
        ),
        note="CME client-systems wiki, Soybeans (page 457090434, version 2025-12-31).",
    ),
    "settle_zm": Citation(
        _WIKI + "457321181/Soybean+Meal",
        (
            "CME Group staff determines the daily settlements in CBOT Soybean Meal (ZM) futures "
            "on trading activity on CME Globex between 13:14:00 and 13:15:00 Central Time (CT), "
            "the settlement period."
        ),
        note="CME client-systems wiki, Soybean Meal (page 457321181, version 2025-12-31).",
    ),
    "settle_zl": Citation(
        _WIKI + "457090469/Soybean+Oil",
        (
            "CME Group staff determines the daily settlements in CBOT Soybean Oil (ZL) futures "
            "based on trading activity on CME Globex between 13:14:00 and 13:15:00 Central Time "
            "(CT), the settlement period."
        ),
        note="CME client-systems wiki, Soybean Oil (page 457090469, version 2025-12-31).",
    ),
    "settle_times": Citation(
        _WIKI + "457085528/Daily+Settlement+Time+Details",
        "Grains/Oilseeds 13:14:00-13:15:00 CT",
        note=(
            "CME client-systems wiki, Daily Settlement Time Details (fetched by "
            "CalendarBuilder-Energy)."
        ),
    ),
}
