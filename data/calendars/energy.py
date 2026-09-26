"""CME Globex calendar for the energy group: NYMEX CL, MCL, QM, NG, MNG, QG, RB and HO,
2019-05-01..2026-06-19 (Stage E.2a Task 6; design D10 and D11.3).

Interface as data.cme_calendar, whose Holiday, HolidayKind, Citation and CalendarCoverageError are
imported, not redefined: HOLIDAYS, SOURCES, NO_ENTRY_FINDINGS, CALENDAR_COVERAGE and
assert_calendar_coverage, plus SESSIONS (data.calendars.SessionSpec) with SESSION_SOURCES. One
additive extension, which no existing caller needs to know about: LATE_OPENS, trade dates whose
Globex session did not trade from its regular start (one, the unscheduled CME outage before the
2025-11-28 open), with LATE_OPEN_SOURCES. Its LateOpen type has the same fields as the rates
group's (data/calendars/rates.py), so the groups read alike.

Sources (all CME Group; cmegroup.com refuses automated fetches, so every cmegroup.com file was
read from a Wayback Machine copy; the CME client wiki on atlassian.net was read directly):
- 2019-2021: CME's Globex holiday trading schedules (.xls) inside CME's yearly
  holiday-calendars.zip, compact sheets, row "Energy, Metals & DME".
- 2022 and New Year 2023: CME's per-holiday Globex schedules (.xls), same row.
- 2023: CME's holiday summary PDFs (cmegroup.com/trading-hours/files/ and the fixed names
  cmegroup.com/files/presidents-day.pdf and good-friday.pdf), row "ENERGY"; MLK Day 2023 from
  CME's settlement notice (status) and CME's Globex MLK 2023 schedule for DME (time, inferred).
- 2023-09..2026-06: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html,
  product 425 (CL, Crude Oil Futures), captures of 2024-07-08, 2024-12-20, 2026-01-29,
  2026-06-10, 2026-06-19 and 2026-07-22.
- 2025-11-28 late open: CME Group's 2025 Form 10-K (status) and the service record (time).
- Regular session and D6's C: CME contract specifications and fact sheets (hours), CME client wiki
  settlement procedures (settlement period 14:28:00-14:30:00 ET).
Verbatim quotes, capture URLs and file hashes per entry, and the script-run verbatim check:
reports/stage_e2a_calendar_sources_energy.json and .md. CME states these hours for its energy asset
class ("Energy, Metals & DME", "ENERGY") or for CL, the most active energy contract; MCL, QM, NG,
MNG, QG, RB and HO are taken to share them (no energy exception row appears in the schedules
read).

Grades as data.cme_calendar: status (``evidence``) "cme" | "secondary" | "unverified"; time
(``time_evidence``) "cme" | "secondary" | "inferred" | "unverified" | "n/a" ("empirical" is
reserved for the later bar check). Every status here is "cme". Every time is "cme" except
2023-01-16 ("inferred": 13:30 CT from CME's own MLK 2023 Globex schedule row for DME, which CME
groups with NYMEX energy; no CME schedule with a NYMEX energy row was retrievable for that day).

How energy differs from the equity calendar:
- Holiday halts (MLK, Presidents, Memorial, Juneteenth, Independence, Labor, Thanksgiving Day)
  are 12:00 CT in 2019-2021 and 13:30 CT from 2022-01-17 on. A holiday on a Friday (2020-07-03,
  2025-07-04, 2026-06-19) closes at 12:00 CT in both periods, with the Sunday 17:00 CT reopen.
- The day after Thanksgiving closes at 12:45 CT in 2019-2023 and at 13:45 CT from 2024
  (energy settles at its normal time that day from 2024); Christmas Eve closes at 12:45 CT.
- The eve of Independence Day, New Year's Eve and the days before observed Christmas / New Year
  keep the regular 16:00 CT close (NO_ENTRY_FINDINGS); energy traded normal hours on the
  2025-01-09 National Day of Mourning; Good Friday is a full closure every year, including the
  jobs-report Good Fridays (2021-04-02, 2023-04-07, 2026-04-03) on which equities traded.

Conventions: ``halt_ct`` is the CT minute trading stops, so the last one-minute bar starts at
halt_ct minus one minute; the reopen is the normal 17:00 CT (Sunday 17:00 when the halt day is a
Friday). CME books the Globex session that ends at a holiday halt to the next trade date; this
module keeps each halt day as its own short trade date, as data.cme_calendar does. Holdout-2
dates (2024-04-01..2025-03-31) and the 2019-05..2024-02 confirmation window rest on CME's
schedules alone until their bars are checked. Product listing dates (MCL 2021-07, MNG 2023-11)
are not calendar entries.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, time

from data.calendars import Segment, SessionSpec
from data.cme_calendar import CalendarCoverageError, Citation, Holiday, HolidayKind

ENERGY_PRODUCTS = ("CL", "MCL", "QM", "NG", "MNG", "QG", "RB", "HO")

HALT_NOON = time(12, 0)  # holiday halt 2019-2021; Friday-holiday close in every year
HALT_1330 = time(13, 30)  # holiday halt from 2022-01-17
CLOSE_1245 = time(12, 45)  # Christmas Eve; day after Thanksgiving 2019-2023
CLOSE_1345 = time(13, 45)  # day after Thanksgiving from 2024

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
    _halt(date(2019, 11, 29), "Day after Thanksgiving", CLOSE_1245),
    _halt(date(2019, 12, 24), "Christmas Eve", CLOSE_1245),
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
    _halt(date(2020, 11, 27), "Day after Thanksgiving", CLOSE_1245),
    _halt(date(2020, 12, 24), "Christmas Eve", CLOSE_1245),
    _closure(date(2020, 12, 25), "Christmas Day"),
    # ---- 2021
    _closure(date(2021, 1, 1), "New Year's Day"),
    _halt(date(2021, 1, 18), "Martin Luther King Jr. Day", HALT_NOON),
    _halt(date(2021, 2, 15), "Presidents Day", HALT_NOON),
    _closure(date(2021, 4, 2), "Good Friday"),
    _halt(date(2021, 5, 31), "Memorial Day", HALT_NOON),
    _halt(date(2021, 7, 5), "Independence Day (observed)", HALT_NOON),
    _halt(date(2021, 9, 6), "Labor Day", HALT_NOON),
    _halt(date(2021, 11, 25), "Thanksgiving Day", HALT_NOON),
    _halt(date(2021, 11, 26), "Day after Thanksgiving", CLOSE_1245),
    _closure(date(2021, 12, 24), "Christmas Day (observed)"),
    # ---- 2022
    _halt(date(2022, 1, 17), "Martin Luther King Jr. Day", HALT_1330),
    _halt(date(2022, 2, 21), "Presidents Day", HALT_1330),
    _closure(date(2022, 4, 15), "Good Friday"),
    _halt(date(2022, 5, 30), "Memorial Day", HALT_1330),
    _halt(date(2022, 6, 20), "Juneteenth (observed)", HALT_1330),
    _halt(date(2022, 7, 4), "Independence Day", HALT_1330),
    _halt(date(2022, 9, 5), "Labor Day", HALT_1330),
    _halt(date(2022, 11, 24), "Thanksgiving Day", HALT_1330),
    _halt(date(2022, 11, 25), "Day after Thanksgiving", CLOSE_1245),
    _closure(date(2022, 12, 26), "Christmas Day (observed)"),
    # ---- 2023
    _closure(date(2023, 1, 2), "New Year's Day (observed)"),
    _halt(date(2023, 1, 16), "Martin Luther King Jr. Day", HALT_1330, time_evidence="inferred"),
    _halt(date(2023, 2, 20), "Presidents Day", HALT_1330),
    _closure(date(2023, 4, 7), "Good Friday"),
    _halt(date(2023, 5, 29), "Memorial Day", HALT_1330),
    _halt(date(2023, 6, 19), "Juneteenth", HALT_1330),
    _halt(date(2023, 7, 4), "Independence Day", HALT_1330),
    _halt(date(2023, 9, 4), "Labor Day", HALT_1330),
    _halt(date(2023, 11, 23), "Thanksgiving Day", HALT_1330),
    _halt(date(2023, 11, 24), "Day after Thanksgiving", CLOSE_1245),
    _closure(date(2023, 12, 25), "Christmas Day"),
    # ---- 2024
    _closure(date(2024, 1, 1), "New Year's Day (observed)"),
    _halt(date(2024, 1, 15), "Martin Luther King Jr. Day", HALT_1330),
    _halt(date(2024, 2, 19), "Presidents Day", HALT_1330),
    _closure(date(2024, 3, 29), "Good Friday"),
    _halt(date(2024, 5, 27), "Memorial Day", HALT_1330),
    _halt(date(2024, 6, 19), "Juneteenth", HALT_1330),
    _halt(date(2024, 7, 4), "Independence Day", HALT_1330),
    _halt(date(2024, 9, 2), "Labor Day", HALT_1330),
    _halt(date(2024, 11, 28), "Thanksgiving Day", HALT_1330),
    _halt(date(2024, 11, 29), "Day after Thanksgiving", CLOSE_1345),
    _halt(date(2024, 12, 24), "Christmas Eve", CLOSE_1245),
    _closure(date(2024, 12, 25), "Christmas Day"),
    # ---- 2025
    _closure(date(2025, 1, 1), "New Year's Day"),
    _halt(date(2025, 1, 20), "Martin Luther King Jr. Day", HALT_1330),
    _halt(date(2025, 2, 17), "Presidents Day", HALT_1330),
    _closure(date(2025, 4, 18), "Good Friday"),
    _halt(date(2025, 5, 26), "Memorial Day", HALT_1330),
    _halt(date(2025, 6, 19), "Juneteenth", HALT_1330),
    _halt(date(2025, 7, 4), "Independence Day", HALT_NOON),
    _halt(date(2025, 9, 1), "Labor Day", HALT_1330),
    _halt(date(2025, 11, 27), "Thanksgiving Day", HALT_1330),
    _halt(date(2025, 11, 28), "Day after Thanksgiving", CLOSE_1345),
    _halt(date(2025, 12, 24), "Christmas Eve", CLOSE_1245),
    _closure(date(2025, 12, 25), "Christmas Day"),
    # ---- 2026
    _closure(date(2026, 1, 1), "New Year's Day"),
    _halt(date(2026, 1, 19), "Martin Luther King Jr. Day", HALT_1330),
    _halt(date(2026, 2, 16), "Presidents Day", HALT_1330),
    _closure(date(2026, 4, 3), "Good Friday"),
    _halt(date(2026, 5, 25), "Memorial Day", HALT_1330),
    _halt(date(2026, 6, 19), "Juneteenth", HALT_NOON),
)

HOLIDAYS: dict[date, Holiday] = {h.day: h for h in _ENTRIES}
CALENDAR_COVERAGE = (date(2019, 5, 1), date(2026, 6, 19))


def assert_calendar_coverage(days: Iterable[date]) -> None:
    """Raise unless every date lies inside ``CALENDAR_COVERAGE`` (inclusive); the semantics of
    data.cme_calendar.assert_calendar_coverage, for the energy group."""
    first, last = CALENDAR_COVERAGE
    outside = sorted(d for d in set(days) if not first <= d <= last)
    if outside:
        raise CalendarCoverageError(
            f"{len(outside)} trade date(s) outside the energy calendar's coverage "
            f"{first}..{last}: {outside[0]} .. {outside[-1]}; extend data/calendars/energy.py "
            "first")


@dataclass(frozen=True)
class LateOpen:
    """A trade date whose Globex session did not trade from its regular start: trading stopped at
    ``halt_from_ct`` on the calendar day ``halt_from_offset_days`` from ``day`` (None: the stop
    time is not in any source retrieved) and resumed at ``open_ct`` CT on ``day``. Grades as for
    Holiday. Additive to the data.cme_calendar interface; same fields as the rates group's."""

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

# One regime covers the whole window: no CME change to NYMEX energy Globex hours was found.
SESSIONS: tuple[SessionSpec, ...] = (
    SessionSpec(
        valid_from=date(2019, 5, 1),
        valid_to=date(2026, 6, 19),
        segments=(Segment(-1, time(17, 0), 0, time(16, 0)),),
        day_session_ct={p: (time(8, 0), time(13, 30)) for p in ENERGY_PRODUCTS},
        source="cme_energy_hours",
        note=(
            "day_session_ct is design D6's energy row (O 08:00, C 13:30 CT; F 15:08 CT is "
            "applied by the rules engine and lies inside the 17:00-16:00 CT session), keyed by "
            "product. D6 confirmation: C 13:30 CT matches CME's daily settlement period "
            "14:28:00-14:30:00 ET (13:28:00-13:30:00 CT) for 'Energy Products' and for CL, NG, "
            "HO and RB by name, with QM and QG settled from CL and NG (SESSION_SOURCES keys "
            "'cme_energy_settlement', 'cme_cl_qm_settlement', 'cme_ng_qg_settlement', "
            "'cme_ho_settlement', 'cme_rb_settlement'), unchanged since the CL page of "
            "2019-05-08. O 08:00 CT is not a boundary CME publishes for NYMEX energy: the Globex "
            "session runs 17:00-16:00 CT and no CME settlement procedure or contract "
            "specification retrieved defines a day-session open. D6's value is encoded "
            "unchanged; the lead rules (reports/stage_e2a_calendar_sources_energy.md, D6 "
            "confirmation)."
        ),
    ),
)

SOURCES: dict[date, Citation] = {
    date(2019, 5, 27): Citation(
        _Z19,
        (
            "CME Group Globex Memorial Day Holiday Schedule: May 24, 2019 - May 28, 2019 ... "
            "Calendar Date|Friday,May 24|Sunday,May 26 into Monday,May 27|Monday, May 27|Mon,May "
            "27 into Tues,May 28 ... Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME "
            "|Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT / 2200 UTC|1200 CT / 1700 UTC|Regular "
            "@ 1700 CT / 2200 UTC"
        ),
        _Z19,
        (
            "Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 "
            "UTC|Regular @ 1700 CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-memorial-day-holiday-schedule-compact.xls; "
            "the zip's sha256 is the document hash. CME's compact Globex holiday schedule states "
            "hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together "
            "with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named "
            "individually. The only energy exception rows in CME's full 2019-2022 schedules are "
            "DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes "
            "concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts "
            "close early at 12:30 CT / 1330 ET')."
        ),
    ),
    date(2019, 7, 4): Citation(
        _Z19,
        (
            "CME Group Globex Independence Day Holiday Schedule: July 3, 2019 to July 5, 2019 ... "
            "Calendar Date|Wednesday July 3 |Wednesday,July 3|Thursday July 4 |Thursday July 4 "
            "into Friday July 5 ... Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular "
            "@ 1600 CT / 2100 UTC|Regular @ 1700 CT/ 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT "
            "/ 2200 UTC"
        ),
        _Z19,
        (
            "Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 "
            "UTC|Regular @ 1700 CT/ 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-4th-of-july-holiday-schedule-compact.xls; "
            "the zip's sha256 is the document hash. CME's compact Globex holiday schedule states "
            "hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together "
            "with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named "
            "individually. The only energy exception rows in CME's full 2019-2022 schedules are "
            "DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes "
            "concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts "
            "close early at 12:30 CT / 1330 ET')."
        ),
    ),
    date(2019, 9, 2): Citation(
        _Z19,
        (
            "CME Group Globex Labor Day Holiday Schedule: August 30, 2019 - September 3, 2019 ... "
            "Calendar Date|Friday,August 30|Sunday,Sept 1 into Monday,Sept 2|Monday, Sept "
            "2|Monday, Sept 2 into Tuesday, Sept 3 ... Product|CLOSE|OPEN|HALT|OPEN ... Energy, "
            "Metals & DME |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT / 2200 UTC|1200 CT / "
            "1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        _Z19,
        (
            "Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 "
            "UTC|Regular @ 1700 CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-labor-day-holiday-schedule-compact.xls; the "
            "zip's sha256 is the document hash. CME's compact Globex holiday schedule states hours "
            "per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with "
            "COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named "
            "individually. The only energy exception rows in CME's full 2019-2022 schedules are "
            "DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes "
            "concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts "
            "close early at 12:30 CT / 1330 ET')."
        ),
    ),
    date(2019, 11, 28): Citation(
        _Z19,
        (
            "CME Group Globex Thanksgiving Holiday Schedule: November 27, 2019 - November 29, 2019 "
            "... Products|Wednesday ,November 27|Wednesday, November 27|Thursday ,November "
            "28|Thursday , November 28|Friday November 29|Friday November 29 ... "
            "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Energy, Metals & DME |Regular @ 1600 CT / 2200 "
            "UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| "
            "Early @ 1245 CT/ 1845 UTC"
        ),
        _Z19,
        (
            "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Energy, Metals & DME |Regular @ 1600 CT / 2200 "
            "UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| "
            "Early @ 1245 CT/ 1845 UTC"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-thanksgiving-holiday-schedule-compact.xls; "
            "the zip's sha256 is the document hash. CME's compact Globex holiday schedule states "
            "hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together "
            "with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named "
            "individually. The only energy exception rows in CME's full 2019-2022 schedules are "
            "DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes "
            "concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts "
            "close early at 12:30 CT / 1330 ET')."
        ),
    ),
    date(2019, 11, 29): Citation(
        _Z19,
        (
            "CME Group Globex Thanksgiving Holiday Schedule: November 27, 2019 - November 29, 2019 "
            "... Products|Wednesday ,November 27|Wednesday, November 27|Thursday ,November "
            "28|Thursday , November 28|Friday November 29|Friday November 29 ... "
            "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Energy, Metals & DME |Regular @ 1600 CT / 2200 "
            "UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| "
            "Early @ 1245 CT/ 1845 UTC"
        ),
        _Z19,
        (
            "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Energy, Metals & DME |Regular @ 1600 CT / 2200 "
            "UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| "
            "Early @ 1245 CT/ 1845 UTC"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-thanksgiving-holiday-schedule-compact.xls; "
            "the zip's sha256 is the document hash. CME's compact Globex holiday schedule states "
            "hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together "
            "with COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named "
            "individually. The only energy exception rows in CME's full 2019-2022 schedules are "
            "DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes "
            "concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts "
            "close early at 12:30 CT / 1330 ET')."
        ),
    ),
    date(2019, 12, 24): Citation(
        _Z19,
        (
            "CME Group Globex Christmas Holiday Schedule: December 24, 2019 - December 26, 2019 "
            "... Trade Date|Tuesday,December 24|Globex Closed|Thursday December 26 ... "
            "Products|Tuesday, Dec 24|Wednesday,Dec 25|Wednesday December 25|Thursday,Dec "
            "26|Thursday, Dec 26 ... Energy, Metals & DME |Early @ 1245 CT / 1845 UTC|Closed for "
            "Christmas|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
        ),
        _Z19,
        (
            "Products|Tuesday, Dec 24|Wednesday,Dec 25|Wednesday December 25|Thursday,Dec "
            "26|Thursday, Dec 26 ... Energy, Metals & DME |Early @ 1245 CT / 1845 UTC|Closed for "
            "Christmas|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-christmas-holiday-schedule-compact.xls; the "
            "zip's sha256 is the document hash. CME's compact Globex holiday schedule states hours "
            "per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with "
            "COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named "
            "individually. The only energy exception rows in CME's full 2019-2022 schedules are "
            "DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes "
            "concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts "
            "close early at 12:30 CT / 1330 ET')."
        ),
    ),
    date(2019, 12, 25): Citation(
        _Z19,
        (
            "CME Group Globex Christmas Holiday Schedule: December 24, 2019 - December 26, 2019 "
            "... Trade Date|Tuesday,December 24|Globex Closed|Thursday December 26 ... "
            "Products|Tuesday, Dec 24|Wednesday,Dec 25|Wednesday December 25|Thursday,Dec "
            "26|Thursday, Dec 26 ... Energy, Metals & DME |Early @ 1245 CT / 1845 UTC|Closed for "
            "Christmas|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-christmas-holiday-schedule-compact.xls; the "
            "zip's sha256 is the document hash. CME's compact Globex holiday schedule states hours "
            "per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with "
            "COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named "
            "individually. The only energy exception rows in CME's full 2019-2022 schedules are "
            "DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes "
            "concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts "
            "close early at 12:30 CT / 1330 ET')."
        ),
    ),
    date(2020, 1, 1): Citation(
        _Z19,
        (
            "CME Group Globex New Years Holiday Schedule: December 31, 2019 - January 2, 2020 ... "
            "Trade Date|Tuesday,Dec 31|Globex Closed|Thursday, January 2 ... Calendar "
            "Trade|Tuesday, Dec 31|Wednessday, Jan 1 |Wednesday, Jan 1|Thursday, Jan 2|Thursday, "
            "Jan 2 ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Closed for New "
            "Year's|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
        ),
        note=(
            "Zip member globex-trading-schedules/2019-new-years-holiday-schedule-compact.xls; the "
            "zip's sha256 is the document hash. CME's compact Globex holiday schedule states hours "
            "per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with "
            "COMEX metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named "
            "individually. The only energy exception rows in CME's full 2019-2022 schedules are "
            "DME Oman Crude TAM, Singapore TAM and EUA Daily Futures, and their energy notes "
            "concern TAS/TAM only (for example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts "
            "close early at 12:30 CT / 1330 ET'). The member file is named 2019-new-years but its "
            "title covers 2019-12-31 to 2020-01-02."
        ),
    ),
    date(2020, 1, 20): Citation(
        _Z20,
        (
            "CME Group Globex Martin Luther King Day Holiday Schedule: January 17, 2020 - January "
            "21, 2020 ... Calendar Date|Friday, Jan 17|Sunday, Jan 19 into Monday, Jan 20|Monday, "
            "Jan 20|Monday, Jan 20 into Tuesday, Jan 21 ... Products|CLOSE|OPEN|HALT|OPEN ... "
            "Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1200 "
            "CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC"
        ),
        _Z20,
        (
            "Products|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2200 "
            "UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC"
        ),
        note=(
            "Zip member 2020-martin-luther-king-holiday-schedule-compact.xls; the zip's sha256 is "
            "the document hash. CME's compact Globex holiday schedule states hours per asset-class "
            "row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and "
            "DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy "
            "exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore "
            "TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example "
            "'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET')."
        ),
    ),
    date(2020, 2, 17): Citation(
        _Z20,
        (
            "CME Group Globex Presidents Day Holiday Schedule: February 14, 2020 - February 18, "
            "2020 ... Calendar Date|Friday, Feb 14|Sunday, Feb 16 into Monday, Feb 17|Monday,Feb "
            "17|Monday, Feb 17 into Tuesday, Feb 18 ... Products|CLOSE|OPEN|HALT|OPEN ... Energy, "
            "Metals & DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / "
            "1800 UTC|Regular @ 1700 CT / 2300 UTC"
        ),
        _Z20,
        (
            "Products|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2200 "
            "UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC"
        ),
        note=(
            "Zip member 2020-presidents-day-holiday-schedule-compact.xls; the zip's sha256 is the "
            "document hash. CME's compact Globex holiday schedule states hours per asset-class "
            "row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and "
            "DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy "
            "exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore "
            "TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example "
            "'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET')."
        ),
    ),
    date(2020, 4, 10): Citation(
        _Z20,
        (
            "CME Group Globex Good Friday Holiday Schedule: April 9,2020 to April 13, 2020 ... "
            "Calendar Date|Thursday April 9|Friday April 10|Sunday, April 12 into Monday, April 13 "
            "... Product|CLOSE|CLOSED|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 "
            "UTC|Closed for Good Friday|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "Zip member 2020-good-friday-holiday-compact.xls; the zip's sha256 is the document "
            "hash. CME's compact Globex holiday schedule states hours per asset-class row; the row "
            "is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, "
            "QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows "
            "in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily "
            "Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating "
            "Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET')."
        ),
    ),
    date(2020, 5, 25): Citation(
        _Z20,
        (
            "CME Group Globex Memorial Day Holiday Schedule: May 22, 2020 - May 26, 2020 ... "
            "Calendar Date|Friday,May 22|Sunday,May 24 into Monday,May 25|Monday, May 25|Mon,May "
            "25 into Tues,May 26 ... Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME "
            "|Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT / 2200 UTC|1200 CT / 1700 UTC|Regular "
            "@ 1700 CT / 2200 UTC"
        ),
        _Z20,
        (
            "Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 "
            "UTC|Regular @ 1700 CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "Zip member 2020-memorial-day-holiday-schedule-compact.xls; the zip's sha256 is the "
            "document hash. CME's compact Globex holiday schedule states hours per asset-class "
            "row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and "
            "DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy "
            "exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore "
            "TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example "
            "'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET')."
        ),
    ),
    date(2020, 7, 3): Citation(
        _Z20,
        (
            "CME Group Globex Independence Day Holiday Schedule: July 2, 2020 to July 6, 2020 ... "
            "Calendar Date|Thursday July 2|Thursday , July 2|Friday July 3|Sunday July 5 into "
            "Monday July 6 ... Product|CLOSE|OPEN|ClOSE|OPEN ... Energy, Metals & DME |Regular @ "
            "1600 CT / 2100 UTC|Regular @ 1700 CT/ 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / "
            "2200 UTC"
        ),
        _Z20,
        (
            "Product|CLOSE|OPEN|ClOSE|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 "
            "UTC|Regular @ 1700 CT/ 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "Zip member 2020-4th-of-july-holiday-schedule-compact.xls; the zip's sha256 is the "
            "document hash. CME's compact Globex holiday schedule states hours per asset-class "
            "row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and "
            "DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy "
            "exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore "
            "TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example "
            "'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 "
            "ET'). Friday holiday: CME labels the 12:00 CT event a close (header 'ClOSE'), and the "
            "next open is Sunday July 5 at 17:00 CT."
        ),
    ),
    date(2020, 9, 7): Citation(
        _Z20,
        (
            "CME Group Globex Labor Day Holiday Schedule: September 4, 2020 - September 8, 2020 "
            "... Calendar Date|Friday,September 4|Sunday,Sept 6 into Monday,Sept 7|Monday, Sept "
            "7|Monday, Sept 7 into Tuesday, Sept 8 ... Product|CLOSE|OPEN|HALT|OPEN ... Energy, "
            "Metals & DME |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT / 2200 UTC|1200 CT / "
            "1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        _Z20,
        (
            "Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 "
            "UTC|Regular @ 1700 CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "Zip member 2020-labor-day-holiday-schedule-compact.xls; the zip's sha256 is the "
            "document hash. CME's compact Globex holiday schedule states hours per asset-class "
            "row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and "
            "DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy "
            "exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore "
            "TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example "
            "'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET')."
        ),
    ),
    date(2020, 11, 26): Citation(
        _Z20,
        (
            "CME Group Globex Thanksgiving Holiday Schedule: November 25, 2020 - November 27, 2020 "
            "... Products|Wednesday ,November 25|Wednesday, November 25|Thursday ,November "
            "26|Thursday , November 26|Friday November 27|Friday November 27 ... "
            "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Energy, Metals & DME |Regular @ 1600 CT / 2200 "
            "UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| "
            "Early @ 1245 CT/ 1845 UTC"
        ),
        _Z20,
        (
            "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Energy, Metals & DME |Regular @ 1600 CT / 2200 "
            "UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| "
            "Early @ 1245 CT/ 1845 UTC"
        ),
        note=(
            "Zip member 2020-thanksgiving-holiday-schedule-compact.xls; the zip's sha256 is the "
            "document hash. CME's compact Globex holiday schedule states hours per asset-class "
            "row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and "
            "DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy "
            "exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore "
            "TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example "
            "'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET')."
        ),
    ),
    date(2020, 11, 27): Citation(
        _Z20,
        (
            "CME Group Globex Thanksgiving Holiday Schedule: November 25, 2020 - November 27, 2020 "
            "... Products|Wednesday ,November 25|Wednesday, November 25|Thursday ,November "
            "26|Thursday , November 26|Friday November 27|Friday November 27 ... "
            "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Energy, Metals & DME |Regular @ 1600 CT / 2200 "
            "UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| "
            "Early @ 1245 CT/ 1845 UTC"
        ),
        _Z20,
        (
            "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Energy, Metals & DME |Regular @ 1600 CT / 2200 "
            "UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| "
            "Early @ 1245 CT/ 1845 UTC"
        ),
        note=(
            "Zip member 2020-thanksgiving-holiday-schedule-compact.xls; the zip's sha256 is the "
            "document hash. CME's compact Globex holiday schedule states hours per asset-class "
            "row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and "
            "DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy "
            "exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore "
            "TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example "
            "'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET')."
        ),
    ),
    date(2020, 12, 24): Citation(
        _Z20,
        (
            "CME Group Globex Christmas Holiday Schedule: December 24, 2020 - December 28, 2020 "
            "... Trade Date|Thursday,December 24|Globex Closed|Monday December 28 ... "
            "Products|Thursday, Dec 24|Friday,Dec 25|Sunday 27|Monday,Dec 28|Monday, Dec 28 ... "
            "Energy, Metals & DME |Early @ 1245 CT / 1845 UTC|Closed for Christmas|Regular @ 1700 "
            "CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
        ),
        _Z20,
        (
            "Products|Thursday, Dec 24|Friday,Dec 25|Sunday 27|Monday,Dec 28|Monday, Dec 28 ... "
            "Energy, Metals & DME |Early @ 1245 CT / 1845 UTC|Closed for Christmas|Regular @ 1700 "
            "CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
        ),
        note=(
            "Zip member 2020-christmas-holiday-schedule-compact.xls; the zip's sha256 is the "
            "document hash. CME's compact Globex holiday schedule states hours per asset-class "
            "row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and "
            "DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy "
            "exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore "
            "TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example "
            "'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET')."
        ),
    ),
    date(2020, 12, 25): Citation(
        _Z20,
        (
            "CME Group Globex Christmas Holiday Schedule: December 24, 2020 - December 28, 2020 "
            "... Trade Date|Thursday,December 24|Globex Closed|Monday December 28 ... "
            "Products|Thursday, Dec 24|Friday,Dec 25|Sunday 27|Monday,Dec 28|Monday, Dec 28 ... "
            "Energy, Metals & DME |Early @ 1245 CT / 1845 UTC|Closed for Christmas|Regular @ 1700 "
            "CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
        ),
        note=(
            "Zip member 2020-christmas-holiday-schedule-compact.xls; the zip's sha256 is the "
            "document hash. CME's compact Globex holiday schedule states hours per asset-class "
            "row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and "
            "DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy "
            "exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore "
            "TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example "
            "'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET')."
        ),
    ),
    date(2021, 1, 1): Citation(
        _Z20,
        (
            "CME Group Globex New Years Holiday Schedule: December 31, 2020 - January 4, 2021 ... "
            "Trade Date|Thursday,Dec 31|Globex Closed|Monday, January 4 ... Calendar "
            "Trade|Thursday,Dec 31|Friday,Jan 1|Sunday,Jan 3|Monday, Jan 4|Monday, Jan 4 ... "
            "Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Closed for New Year's|Regular @ "
            "1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
        ),
        note=(
            "Zip member 2021-new-years-holiday-schedule-compact.xls; the zip's sha256 is the "
            "document hash. CME's compact Globex holiday schedule states hours per asset-class "
            "row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and "
            "DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy "
            "exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore "
            "TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example "
            "'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 "
            "ET'). CME filed the 2021 New Year schedule in its 2020 zip."
        ),
    ),
    date(2021, 1, 18): Citation(
        _Z21,
        (
            "CME Group Globex Martin Luther King Day Holiday Schedule: January 15, 2021 - January "
            "19, 2021 ... Calendar Date|Friday, Jan 15|Sunday, Jan 17 into Monday, Jan 18|Monday, "
            "Jan 18|Monday, Jan 18 into Tuesday, Jan 19 ... Products|CLOSE|OPEN|HALT|OPEN ... "
            "Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1200 "
            "CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC"
        ),
        _Z21,
        (
            "Products|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2200 "
            "UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC"
        ),
        note=(
            "Zip member 2021-mlk-day-schedule-compact.xls; the zip's sha256 is the document hash. "
            "CME's compact Globex holiday schedule states hours per asset-class row; the row is "
            "'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, "
            "QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows "
            "in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily "
            "Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating "
            "Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET')."
        ),
    ),
    date(2021, 2, 15): Citation(
        _Z21,
        (
            "CME Group Globex Presidents Day Holiday Schedule: February 12, 2021 - February 16, "
            "2021 ... Calendar Date|Friday, Feb 12|Sunday, Feb 14 into Monday, Feb 15|Monday,Feb "
            "15|Monday, Feb 15 into Tuesday, Feb 16 ... Products|CLOSE|OPEN|HALT|OPEN ... Energy, "
            "Metals & DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / "
            "1800 UTC|Regular @ 1700 CT / 2300 UTC"
        ),
        _Z21,
        (
            "Products|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2200 "
            "UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC"
        ),
        note=(
            "Zip member 2021-presidents-day-holiday-schedule-compact.xls; the zip's sha256 is the "
            "document hash. CME's compact Globex holiday schedule states hours per asset-class "
            "row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and "
            "DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy "
            "exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore "
            "TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example "
            "'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET')."
        ),
    ),
    date(2021, 4, 2): Citation(
        _Z21,
        (
            "CME Group Globex Good Friday Holiday Schedule: April 1,2021 to April 5, 2021 ... "
            "Calendar Date|Thursday April 1|Thursday,April 1|Friday April 2|Sunday, April 4 into "
            "Monday, April 5 ... Product|CLOSE|OPEN|CLOSED|OPEN ... Energy, Metals & DME |Regular "
            "@ 1600 CT / 2100 UTC|Closed for Good Friday|Closed for Good Friday|Regular @ 1700 CT "
            "/ 2200 UTC"
        ),
        note=(
            "Zip member 2021-good-friday-holiday-schedule-compact.xls; the zip's sha256 is the "
            "document hash. CME's compact Globex holiday schedule states hours per asset-class "
            "row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and "
            "DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy "
            "exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore "
            "TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example "
            "'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 "
            "ET'). Jobs-report Good Friday: equities and rates traded an abbreviated session "
            "(equity calendar), energy did not open."
        ),
    ),
    date(2021, 5, 31): Citation(
        _Z21,
        (
            "CME Group Globex Memorial Day Holiday Schedule: May 28, 2021 - June 1st, 2021 ... "
            "Calendar Date|Friday,May 28|Sunday,May 30|Monday, May 31|Monday, May 31 into Tues, "
            "June 1 ... Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / "
            "2100 UTC|Regular @ 1700 CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        _Z21,
        (
            "Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 "
            "UTC|Regular @ 1700 CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "Zip member 2021-memorial-day-holiday-schedule-compact.xls; the zip's sha256 is the "
            "document hash. CME's compact Globex holiday schedule states hours per asset-class "
            "row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and "
            "DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy "
            "exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore "
            "TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example "
            "'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET')."
        ),
    ),
    date(2021, 7, 5): Citation(
        _Z21,
        (
            "CME Group Globex Independence Day Holiday Schedule: July 2, 2021 to July 6, 2021 ... "
            "Calendar Date|Friday July 2|Sunday July 4|Monday July 5|Monday July 5 ... "
            "Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 "
            "UTC|Regular @ 1700 CT/ 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        _Z21,
        (
            "Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 "
            "UTC|Regular @ 1700 CT/ 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "Zip member 2021-independence-day-holiday-schedule-compact.xls; the zip's sha256 is "
            "the document hash. CME's compact Globex holiday schedule states hours per asset-class "
            "row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and "
            "DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy "
            "exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore "
            "TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example "
            "'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET')."
        ),
    ),
    date(2021, 9, 6): Citation(
        _Z21,
        (
            "CME Group Globex Labor Day Holiday Schedule: September 3, 2021 - September 7, 2021 "
            "... Calendar Date|Friday,September 3|Sunday,Sept 5 into Monday,Sept 6|Monday, Sept "
            "6|Monday, Sept 6 into Tuesday, Sept 7 ... Product|CLOSE|OPEN|HALT|OPEN ... Energy, "
            "Metals & DME |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT / 2200 UTC|1200 CT / "
            "1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        _Z21,
        (
            "Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 "
            "UTC|Regular @ 1700 CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "Zip member 2021-labor-day-holiday-schedule-compact.xls; the zip's sha256 is the "
            "document hash. CME's compact Globex holiday schedule states hours per asset-class "
            "row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and "
            "DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy "
            "exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore "
            "TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example "
            "'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET')."
        ),
    ),
    date(2021, 11, 25): Citation(
        _Z21,
        (
            "CME Group Globex Thanksgiving Holiday Schedule: November 24, 2021 - November 26, 2021 "
            "... Products|Wednesday ,November 24|Wednesday, November 24|Thursday ,November "
            "25|Thursday , November 25|Friday November 26|Friday November 26 ... "
            "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Energy, Metals & DME |Regular @ 1600 CT / 2200 "
            "UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| "
            "Early @ 1245 CT/ 1845 UTC"
        ),
        _Z21,
        (
            "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Energy, Metals & DME |Regular @ 1600 CT / 2200 "
            "UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| "
            "Early @ 1245 CT/ 1845 UTC"
        ),
        note=(
            "Zip member 2021-thanksgiving-holiday-schedule-compact.xls; the zip's sha256 is the "
            "document hash. CME's compact Globex holiday schedule states hours per asset-class "
            "row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and "
            "DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy "
            "exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore "
            "TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example "
            "'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET')."
        ),
    ),
    date(2021, 11, 26): Citation(
        _Z21,
        (
            "CME Group Globex Thanksgiving Holiday Schedule: November 24, 2021 - November 26, 2021 "
            "... Products|Wednesday ,November 24|Wednesday, November 24|Thursday ,November "
            "25|Thursday , November 25|Friday November 26|Friday November 26 ... "
            "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Energy, Metals & DME |Regular @ 1600 CT / 2200 "
            "UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| "
            "Early @ 1245 CT/ 1845 UTC"
        ),
        _Z21,
        (
            "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Energy, Metals & DME |Regular @ 1600 CT / 2200 "
            "UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| "
            "Early @ 1245 CT/ 1845 UTC"
        ),
        note=(
            "Zip member 2021-thanksgiving-holiday-schedule-compact.xls; the zip's sha256 is the "
            "document hash. CME's compact Globex holiday schedule states hours per asset-class "
            "row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and "
            "DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy "
            "exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore "
            "TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example "
            "'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET')."
        ),
    ),
    date(2021, 12, 24): Citation(
        _Z21,
        (
            "CME Group Globex Christmas Holiday Schedule: December 23, 2021 - December 27, 2021 "
            "... Trade Date|Thursday,December 23|Globex Closed|Monday December 27 ... "
            "Products|Thursday, Dec 23|Friday,Dec 24|Sunday 26|Monday,Dec 27 ... Energy, Metals & "
            "DME |Regular per Product|Closed for Christmas|Regular @ 1700 CT / 2300 UTC|Regular @ "
            "1600 CT / 2200 UTC"
        ),
        note=(
            "Zip member 2021-christmas-holiday-schedule-compact.xls; the zip's sha256 is the "
            "document hash. CME's compact Globex holiday schedule states hours per asset-class "
            "row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and "
            "DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The only energy "
            "exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore "
            "TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for example "
            "'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET')."
        ),
    ),
    date(2022, 1, 17): Citation(
        _HC + "2022-mlk-day-holiday-schedule-compact.xls",
        (
            "CME Group Globex Martin Luther King Day Holiday Schedule: January 14, 2022 - January "
            "18, 2022 ... Calendar Date|Friday, Jan 14|Sunday, Jan 16 into Monday, Jan 17|Monday, "
            "Jan 17|Monday, Jan 17 into Tuesday, Jan 18 ... Energy, Metals & DME |Regular @ 1600 "
            "CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1330 CT / 1930 UTC|Regular @ 1700 CT / "
            "2300 UTC"
        ),
        _HC + "2022-mlk-day-holiday-schedule-compact.xls",
        (
            "Calendar Date|Friday, Jan 14|Sunday, Jan 16 into Monday, Jan 17|Monday, Jan "
            "17|Monday, Jan 17 into Tuesday, Jan 18 ... Energy, Metals & DME |Regular @ 1600 CT / "
            "2200 UTC|Regular @ 1700 CT / 2300 UTC|1330 CT / 1930 UTC|Regular @ 1700 CT / 2300 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule states hours per asset-class row; the row is "
            "'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, "
            "QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows "
            "in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily "
            "Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating "
            "Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET'). First 13:30 CT "
            "energy holiday halt found (2019-2021: 12:00 CT)."
        ),
    ),
    date(2022, 2, 21): Citation(
        _HC + "2022-presidents-day-holiday-schedule-compact.xls",
        (
            "CME Group Globex Presidents Day Holiday Schedule: February 18, 2022 - February 22, "
            "2022 ... Calendar Date|Friday, Feb 18|Sunday, Feb 20 into Monday, Feb 21|Monday,Feb "
            "21|Monday, Feb 21 into Tuesday, Feb 22 ... Energy, Metals & DME |Regular @ 1600 CT / "
            "2200 UTC|Regular @ 1700 CT / 2300 UTC|1330 CT / 1930 UTC|Regular @ 1700 CT / 2300 UTC"
        ),
        _HC + "2022-presidents-day-holiday-schedule-compact.xls",
        (
            "Calendar Date|Friday, Feb 18|Sunday, Feb 20 into Monday, Feb 21|Monday,Feb 21|Monday, "
            "Feb 21 into Tuesday, Feb 22 ... Energy, Metals & DME |Regular @ 1600 CT / 2200 "
            "UTC|Regular @ 1700 CT / 2300 UTC|1330 CT / 1930 UTC|Regular @ 1700 CT / 2300 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule states hours per asset-class row; the row is "
            "'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, "
            "QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows "
            "in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily "
            "Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating "
            "Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET')."
        ),
    ),
    date(2022, 4, 15): Citation(
        _HC + "2022-good-friday-holiday-schedule-compact.xls",
        (
            "CME Group Globex Good Friday Holiday Schedule: April 14,2022 to April 18, 2022 ... "
            "Calendar Date|Thursday April 14|Friday April 15|Sunday, April 17 into Monday, April "
            "18 ... Product|CLOSE|CLOSED|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 "
            "UTC|Closed for Good Friday|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule states hours per asset-class row; the row is "
            "'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, "
            "QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows "
            "in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily "
            "Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating "
            "Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET')."
        ),
    ),
    date(2022, 5, 30): Citation(
        _HC + "2022-memorial-day-holiday-schedule-compact.xls",
        (
            "CME Group Globex Memorial Day Holiday Schedule: May 27, 2022 - May 31 , 2022 ... "
            "Calendar Date|Friday,May 27|Sunday,May 29|Monday, May 30|Monday, May 30 into Tues, "
            "May31 ... Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / "
            "2100 UTC|Regular @ 1700 CT / 2200 UTC|1330 CT / 1830 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        _HC + "2022-memorial-day-holiday-schedule-compact.xls",
        (
            "Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 "
            "UTC|Regular @ 1700 CT / 2200 UTC|1330 CT / 1830 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule states hours per asset-class row; the row is "
            "'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, "
            "QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows "
            "in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily "
            "Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating "
            "Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET')."
        ),
    ),
    date(2022, 6, 20): Citation(
        _HC + "2022-juneteenth-holiday-schedule.xls",
        (
            "CME Group Globex Juneteenth Holiday Schedule: June 17, 2022 - Jun 21, 2022 ... "
            "Calendar Date|Friday, June 17|||||Sunday, June 19|||||Monday, June "
            "20||||||||||Tuesday, Jun 21 ... Energy, Metals & DME Products|04:00:00 "
            "PM|||||04:00:00 PM|05:00:00 PM|||||||01:30:00 PM||||01:30:00 PM|05:00:00 PM"
        ),
        _HC + "2022-juneteenth-holiday-schedule.xls",
        (
            "Energy, Metals & DME Products|04:00:00 PM|||||04:00:00 PM|05:00:00 PM|||||||01:30:00 "
            "PM||||01:30:00 PM|05:00:00 PM"
        ),
        note=(
            "CME's compact Globex holiday schedule states hours per asset-class row; the row is "
            "'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, "
            "QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows "
            "in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily "
            "Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating "
            "Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET'). Full schedule "
            "(no compact file captured). Column mapping read from the merged header cells with "
            "xlrd: Calendar Date 'Monday, June 20' spans columns 11-20; the energy row's 13:30 "
            "cells are columns 14 ('Halt') and 18, and 17:00 is column 19 ('Open')."
        ),
    ),
    date(2022, 7, 4): Citation(
        _HC + "2022-independence-day-holiday-schedule-compact.xls",
        (
            "CME Group Globex Independence Day Holiday Schedule: July 1, 2022 to July 5, 2022 ... "
            "Calendar Date|Friday July 1|Sunday July 3|Monday July 4|Monday July 4 ... "
            "Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 "
            "UTC|Regular @ 1700 CT/ 2200 UTC|1330 CT / 1830 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        _HC + "2022-independence-day-holiday-schedule-compact.xls",
        (
            "Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 "
            "UTC|Regular @ 1700 CT/ 2200 UTC|1330 CT / 1830 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule states hours per asset-class row; the row is "
            "'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, "
            "QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows "
            "in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily "
            "Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating "
            "Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET')."
        ),
    ),
    date(2022, 9, 5): Citation(
        _HC + "2022-labor-day-holiday-schedule-compact.xls",
        (
            "CME Group Globex Labor Day Holiday Schedule: September 2, 2022 - September 6, 2022 "
            "... Calendar Date|Friday, September 2|Sunday,Sept 4 into Monday, Sept 5|Monday, Sept "
            "5|Monday, Sept 5 into Tuesday, Sept 6 ... Product|CLOSE|OPEN|HALT|OPEN ... Energy, "
            "Metals & DME |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT / 2200 UTC|1330 CT / "
            "1830 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        _HC + "2022-labor-day-holiday-schedule-compact.xls",
        (
            "Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular @ 1600 CT / 2100 "
            "UTC|Regular @ 1700 CT / 2200 UTC|1330 CT / 1830 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule states hours per asset-class row; the row is "
            "'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, "
            "QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows "
            "in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily "
            "Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating "
            "Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET')."
        ),
    ),
    date(2022, 11, 24): Citation(
        _HC + "2022-thanksgiving-holiday-schedule-compact.xls",
        (
            "CME Group Globex Thanksgiving Holiday Schedule: November 23, 2022 - November 25, 2022 "
            "... Products|Wednesday ,November 23|Wednesday, November 23|Thursday ,November "
            "24|Thursday , November 24|Friday November 25|Friday November 25 ... "
            "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Energy, Metals & DME |Regular @ 1600 CT / 2200 "
            "UTC|Regular @ 1700 CT / 2300 UTC|1330 CT / 1930 UTC|Regular @ 1700 CT / 2300 UTC|| "
            "Early @ 1245 CT/ 1845 UTC"
        ),
        _HC + "2022-thanksgiving-holiday-schedule-compact.xls",
        (
            "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Energy, Metals & DME |Regular @ 1600 CT / 2200 "
            "UTC|Regular @ 1700 CT / 2300 UTC|1330 CT / 1930 UTC|Regular @ 1700 CT / 2300 UTC|| "
            "Early @ 1245 CT/ 1845 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule states hours per asset-class row; the row is "
            "'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, "
            "QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows "
            "in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily "
            "Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating "
            "Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET')."
        ),
    ),
    date(2022, 11, 25): Citation(
        _HC + "2022-thanksgiving-holiday-schedule-compact.xls",
        (
            "CME Group Globex Thanksgiving Holiday Schedule: November 23, 2022 - November 25, 2022 "
            "... Products|Wednesday ,November 23|Wednesday, November 23|Thursday ,November "
            "24|Thursday , November 24|Friday November 25|Friday November 25 ... "
            "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Energy, Metals & DME |Regular @ 1600 CT / 2200 "
            "UTC|Regular @ 1700 CT / 2300 UTC|1330 CT / 1930 UTC|Regular @ 1700 CT / 2300 UTC|| "
            "Early @ 1245 CT/ 1845 UTC"
        ),
        _HC + "2022-thanksgiving-holiday-schedule-compact.xls",
        (
            "|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Energy, Metals & DME |Regular @ 1600 CT / 2200 "
            "UTC|Regular @ 1700 CT / 2300 UTC|1330 CT / 1930 UTC|Regular @ 1700 CT / 2300 UTC|| "
            "Early @ 1245 CT/ 1845 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule states hours per asset-class row; the row is "
            "'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, "
            "QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows "
            "in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily "
            "Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating "
            "Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET')."
        ),
    ),
    date(2022, 12, 26): Citation(
        _HC + "2022-christmas-holiday-schedule.xls",
        (
            "CME Group Globex Christmas Holiday Schedule: December 23, 2022 - December 27, 2022 "
            "... Calendar Date|Friday, December 23||||||||Monday, December "
            "26||||||||||||||||Tuesday, December 27 ... Energy, Metals & DME products (see notes "
            "below)|04:00:00 PM||||||||Globex Closed||||||||||04:00:00 PM|05:00:00 "
            "PM|||||||04:00:00 PM"
        ),
        note=(
            "CME's compact Globex holiday schedule states hours per asset-class row; the row is "
            "'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, "
            "QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows "
            "in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily "
            "Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating "
            "Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET'). Full schedule, "
            "'Updated 6/29/2022' (captured 2022-07-04, before the holiday). Merged header cells "
            "(xlrd): 'Globex Closed' spans columns 9-18 under Calendar Date 'Monday, December 26' "
            "(columns 9-24); pre-open 16:00 and open 17:00 follow on the Monday. CME's 2022 "
            "Christmas settlement notice agrees: 'Note: Monday December 26, 2022 CME Group will "
            "not derive or disseminate settlement prices'."
        ),
    ),
    date(2023, 1, 2): Citation(
        _HC + "2023-new-years-holiday-schedule-compact.xls",
        (
            "CME Group Globex New Years Holiday Schedule: December 30, 2022 - January 3, 2023 ... "
            "Calendar Trade|Friday,Dec 30|Sunday, Jan 1 and Monday, Jan 2|Monday,Jan 2|Tuesday, "
            "Jan 3|Tuesday, Jan 3 ... |CLOSE|Closed|OPEN|OPEN|CLOSE ... Energy, Metals & DME "
            "|Regular @ 1600 CT / 2200 UTC|Globex Closed|Regular @ 1700 CT / 2300 UTC||Regular @ "
            "1600 CT / 2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule states hours per asset-class row; the row is "
            "'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, "
            "QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows "
            "in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily "
            "Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating "
            "Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET'). Captured "
            "2022-07-04, before the holiday (CME published it in advance)."
        ),
    ),
    date(2023, 1, 16): Citation(
        _HC + "mlk-day-holiday-settlement-times-2023.pdf",
        (
            "Note: Monday January 16, 2023 CME Group will not derive or disseminate settlement "
            "prices (other than the two LIBOR Settlements listed above) for CME, CBOT, NYMEX or "
            "COMEX"
        ),
        _HC + "2023-mlk-day-holiday-schedule-compact-mgex-dme.xls",
        (
            "CME Group Globex Martin Luther King Day Holiday Schedule: January 13, 2023 - January "
            "17, 2023 ... Calendar Date|Friday, Jan 13|Sunday, Jan 15 into Monday, Jan 16|Monday, "
            "Jan 16|Monday, Jan 16 into Tuesday, Jan 17 ... Products|CLOSE|OPEN|HALT|OPEN ... DME "
            "|Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|1330 CT / 1930 UTC|Regular "
            "@ 1700 CT / 2300 UTC"
        ),
        note=(
            "Time inferred, not cme: no CME Globex schedule with a NYMEX energy row was "
            "retrievable for MLK Day 2023 (the 2023 summary PDF was not archived; the service "
            "capture of 2024-07-08 has no events for that window). The CME Globex MLK 2023 "
            "schedule retrieved covers MGEX and DME only; its DME row (Dubai Mercantile Exchange "
            "crude on CME Globex, grouped with NYMEX energy as 'Energy, Metals & DME' in CME's "
            "2019-2022 schedules) halts at 13:30 CT. Consistent with every NYMEX energy holiday "
            "halt from 2022-01-17 to 2026-05-25 (13:30 CT). Secondary corroboration, not "
            "machine-checkable: AMP Futures' image of CME's table 'CME Group Globex Dr. Martin "
            "Luther King, Jr. Holiday Schedule: 13 - 17 January 2023' shows 'Energies' HALT '13:30 "
            "CST' on Monday Jan 16 (https://www.ampfutures.com/hubfs/CME%20Holiday%20Trading%20Sc"
            "hedule%20-%20Dr.%20Martin%20Luther%20King%2c%20Jr.%20(2023).png, cached by "
            "CalendarBuilder-Rates, read as an image)."
        ),
    ),
    date(2023, 2, 20): Citation(
        "https://www.cmegroup.com/files/presidents-day.pdf",
        (
            "PRODUCT NAME Cleared As SUNDAY, 19 FEB 2023 MONDAY, 20 FEB 2023 TUESDAY, 21 FEB 2023 "
            "... ENERGY 16:00 (PREOPEN) 13:30 (PREOPEN) HALT"
        ),
        "https://www.cmegroup.com/files/presidents-day.pdf",
        "ENERGY 16:00 (PREOPEN) 13:30 (PREOPEN) HALT",
        note=(
            "CME holiday summary PDF (cmegroup.com/trading-hours/files/): hours of 'the most "
            "actively traded instruments for each asset class', ENERGY row; text read with "
            "pdftotext -layout, so the ENERGY line carries the day columns left to right. "
            "cmegroup.com/files/presidents-day.pdf is the fixed name CME's trading-hours page "
            "linked as 'Download a summary view of the President's Day Holiday Hours' (page "
            "capture 2023-02-19); this capture (2023-03-29) holds the 2023 version."
        ),
    ),
    date(2023, 4, 7): Citation(
        "https://www.cmegroup.com/files/good-friday.pdf",
        "PRODUCT NAME THURSDAY, 6 APR 2023 FRIDAY, 7 APR 2023 ... ENERGY 16:00 ( CLOSED)",
        note=(
            "CME holiday summary PDF (cmegroup.com/trading-hours/files/): hours of 'the most "
            "actively traded instruments for each asset class', ENERGY row; text read with "
            "pdftotext -layout, so the ENERGY line carries the day columns left to right. The "
            "2024-07-08 capture of the fixed name cmegroup.com/files/good-friday.pdf still holds "
            "the 2023 version (6-7 APR 2023). The ENERGY row has only Thursday's 16:00 close and "
            "no Friday event, while INTEREST RATE, EQUITIES, FX and CRYPTOCURRENCIES carry Friday "
            "sessions. CME's 2023 Good Friday clearing advisory names only equities as open for an "
            "abbreviated session and FX and interest-rate markets as settled."
        ),
    ),
    date(2023, 5, 29): Citation(
        _TH + "memorial-day-2023.pdf",
        (
            "PRODUCT NAME SUNDAY, 28 MAY 2023 MONDAY, 29 MAY 2023 TUESDAY, 30 MAY 2023 ... ENERGY "
            "16:00 (PREOPEN) 13:30 (PREOPEN) HALT"
        ),
        _TH + "memorial-day-2023.pdf",
        "ENERGY 16:00 (PREOPEN) 13:30 (PREOPEN) HALT",
        note=(
            "CME holiday summary PDF (cmegroup.com/trading-hours/files/): hours of 'the most "
            "actively traded instruments for each asset class', ENERGY row; text read with "
            "pdftotext -layout, so the ENERGY line carries the day columns left to right."
        ),
    ),
    date(2023, 6, 19): Citation(
        _TH + "juneteenth-2023.pdf",
        (
            "PRODUCT NAME SUNDAY, 18 JUNE 2023 MONDAY, 19 JUNE 2023 TUESDAY, 20 JUNE 2023 ... "
            "ENERGY 16:00 (PREOPEN) 13:30 (PREOPEN) HALT"
        ),
        _TH + "juneteenth-2023.pdf",
        "ENERGY 16:00 (PREOPEN) 13:30 (PREOPEN) HALT",
        note=(
            "CME holiday summary PDF (cmegroup.com/trading-hours/files/): hours of 'the most "
            "actively traded instruments for each asset class', ENERGY row; text read with "
            "pdftotext -layout, so the ENERGY line carries the day columns left to right."
        ),
    ),
    date(2023, 7, 4): Citation(
        _TH + "4th-of-july-2023.pdf",
        (
            "PRODUCT NAME MONDAY, 3 JULY 2023 TUESDAY, 4 JULY 2023 WEDNESDAY, 5 JULY 2023 ... "
            "ENERGY TRADE DATE: WED 5 JULY 13:30 (PREOPEN) HALT"
        ),
        _TH + "4th-of-july-2023.pdf",
        "ENERGY TRADE DATE: WED 5 JULY 13:30 (PREOPEN) HALT",
        note=(
            "CME holiday summary PDF (cmegroup.com/trading-hours/files/): hours of 'the most "
            "actively traded instruments for each asset class', ENERGY row; text read with "
            "pdftotext -layout, so the ENERGY line carries the day columns left to right."
        ),
    ),
    date(2023, 9, 4): Citation(
        _TH + "labor-day-2023.pdf",
        (
            "PRODUCT NAME SUNDAY, 3 SEPTEMBER 2023 MONDAY, 4 SEPTEMBER 2023 TUESDAY, 5 SEPTEMBER "
            "2023 ... ENERGY 16:00 (PREOPEN) 13:30 (PREOPEN) HALT"
        ),
        _svc("2023-09-03", "2023-09-05", "1720455278654"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2023-09-04","events":[{"tradingDate":"2023-09-05","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2023-09-05","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME holiday summary PDF (cmegroup.com/trading-hours/files/): hours of 'the most "
            "actively traded instruments for each asset class', ENERGY row; text read with "
            "pdftotext -layout, so the ENERGY line carries the day columns left to right. CME's "
            "trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 "
            "'Crude Oil Futures' (CL), Wayback capture 20240708161439. CL stands for the group: "
            "CME's holiday schedules give energy hours per asset class. 'preopen' at a time = "
            "trading halts (order entry only) until the next 'open'; 'closed' = final close of the "
            "trade date."
        ),
    ),
    date(2023, 11, 23): Citation(
        _TH + "thanksgiving-day-2023.pdf",
        (
            "PRODUCT NAME WEDNESDAY, 22 NOVEMBER 2023 THURSDAY, 23 NOVEMBER 2023 FRIDAY, 24 "
            "NOVEMBER 2023 ... ENERGY TRADE DATE: FRI 24 NOV 13:30 (PREOPEN) HALT 12:45 (CLOSED)"
        ),
        _svc("2023-11-22", "2023-11-24", "1720455278656"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2023-11-23","events":[{"tradingDate":"2023-11-24","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2023-11-24","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME holiday summary PDF (cmegroup.com/trading-hours/files/): hours of 'the most "
            "actively traded instruments for each asset class', ENERGY row; text read with "
            "pdftotext -layout, so the ENERGY line carries the day columns left to right. CME's "
            "trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 "
            "'Crude Oil Futures' (CL), Wayback capture 20240708161439. CL stands for the group: "
            "CME's holiday schedules give energy hours per asset class. 'preopen' at a time = "
            "trading halts (order entry only) until the next 'open'; 'closed' = final close of the "
            "trade date."
        ),
    ),
    date(2023, 11, 24): Citation(
        _TH + "thanksgiving-day-2023.pdf",
        (
            "PRODUCT NAME WEDNESDAY, 22 NOVEMBER 2023 THURSDAY, 23 NOVEMBER 2023 FRIDAY, 24 "
            "NOVEMBER 2023 ... ENERGY TRADE DATE: FRI 24 NOV 13:30 (PREOPEN) HALT 12:45 (CLOSED)"
        ),
        _svc("2023-11-22", "2023-11-24", "1720455278656"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2023-11-24","events":[{"tradingDate":"2023-11-24","even'
            'tTime":"12:45","marketEventType":"closed"}]}'
        ),
        note=(
            "CME holiday summary PDF (cmegroup.com/trading-hours/files/): hours of 'the most "
            "actively traded instruments for each asset class', ENERGY row; text read with "
            "pdftotext -layout, so the ENERGY line carries the day columns left to right. CME's "
            "trading-hours-by-product service behind cmegroup.com/trading-hours.html, product 425 "
            "'Crude Oil Futures' (CL), Wayback capture 20240708161439. CL stands for the group: "
            "CME's holiday schedules give energy hours per asset class. 'preopen' at a time = "
            "trading halts (order entry only) until the next 'open'; 'closed' = final close of the "
            "trade date. CME's 2023 Thanksgiving settlement notice: 'Energy Products 13:30:00 ET' "
            "(12:30 CT) on Friday November 24."
        ),
    ),
    date(2023, 12, 25): Citation(
        _svc("2023-12-24", "2023-12-26", "1720455278659"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2023-12-24","events":[]} ... {"groupCode":"CL","event'
            'Date":"2023-12-25","events":[{"tradingDate":"2023-12-26","eventTime":"16:00","marketEv'
            'entType":"preopen"},{"tradingDate":"2023-12-26","eventTime":"17:00","marketEventType":'
            '"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 425 'Crude Oil Futures' (CL), Wayback capture 20240708161439. CL stands for "
            "the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a "
            "time = trading halts (order entry only) until the next 'open'; 'closed' = final close "
            "of the trade date. No event on Sunday 12-24 (no 17:00 CT reopen) and only the 16:00 "
            "pre-open and 17:00 open for trade date 12-26 on Monday 12-25. CME's summary PDF "
            "christmas-day-2023.pdf (ENERGY row, Monday 25 December: 16:00 PREOPEN, 17:00 OPEN) "
            "and its settlement notice ('Note: Monday December 25, 2023 CME Group will not derive "
            "or disseminate settlement prices') agree."
        ),
    ),
    date(2024, 1, 1): Citation(
        _svc("2023-12-31", "2024-01-02", "1720455278661"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2023-12-31","events":[]} ... {"groupCode":"CL","event'
            'Date":"2024-01-01","events":[{"tradingDate":"2024-01-02","eventTime":"16:00","marketEv'
            'entType":"preopen"},{"tradingDate":"2024-01-02","eventTime":"17:00","marketEventType":'
            '"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 425 'Crude Oil Futures' (CL), Wayback capture 20240708161439. CL stands for "
            "the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a "
            "time = trading halts (order entry only) until the next 'open'; 'closed' = final close "
            "of the trade date. CME's summary PDF new-years-day-2024.pdf (ENERGY, Monday 1 January "
            "2024: 16:00 PREOPEN, 17:00 OPEN) agrees."
        ),
    ),
    date(2024, 1, 15): Citation(
        _svc("2024-01-14", "2024-01-16", "1720455278663"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2024-01-15","events":[{"tradingDate":"2024-01-16","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2024-01-16","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        _svc("2024-01-14", "2024-01-16", "1720455278663"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2024-01-15","events":[{"tradingDate":"2024-01-16","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2024-01-16","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 425 'Crude Oil Futures' (CL), Wayback capture 20240708161439. CL stands for "
            "the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a "
            "time = trading halts (order entry only) until the next 'open'; 'closed' = final close "
            "of the trade date."
        ),
    ),
    date(2024, 2, 19): Citation(
        _svc("2024-02-18", "2024-02-20", "1720455278669"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2024-02-19","events":[{"tradingDate":"2024-02-20","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2024-02-20","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        _svc("2024-02-18", "2024-02-20", "1720455278669"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2024-02-19","events":[{"tradingDate":"2024-02-20","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2024-02-20","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 425 'Crude Oil Futures' (CL), Wayback capture 20240708161439. CL stands for "
            "the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a "
            "time = trading halts (order entry only) until the next 'open'; 'closed' = final close "
            "of the trade date."
        ),
    ),
    date(2024, 3, 29): Citation(
        _svc("2024-03-28", "2024-03-30", "1720455278672"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2024-03-28","events":[{"tradingDate":"2024-03-28","even'
            'tTime":"16:00","marketEventType":"closed"}]} ... '
            '{"groupCode":"CL","eventDate":"2024-03-29","events":[]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 425 'Crude Oil Futures' (CL), Wayback capture 20240708161439. CL stands for "
            "the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a "
            "time = trading halts (order entry only) until the next 'open'; 'closed' = final close "
            "of the trade date."
        ),
    ),
    date(2024, 5, 27): Citation(
        _svc("2024-05-26", "2024-05-28", "1720455278675"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2024-05-27","events":[{"tradingDate":"2024-05-28","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2024-05-28","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        _svc("2024-05-26", "2024-05-28", "1720455278675"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2024-05-27","events":[{"tradingDate":"2024-05-28","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2024-05-28","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 425 'Crude Oil Futures' (CL), Wayback capture 20240708161439. CL stands for "
            "the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a "
            "time = trading halts (order entry only) until the next 'open'; 'closed' = final close "
            "of the trade date."
        ),
    ),
    date(2024, 6, 19): Citation(
        _svc("2024-06-18", "2024-06-20", "1720455278677"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2024-06-19","events":[{"tradingDate":"2024-06-20","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2024-06-20","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        _svc("2024-06-18", "2024-06-20", "1720455278677"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2024-06-19","events":[{"tradingDate":"2024-06-20","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2024-06-20","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 425 'Crude Oil Futures' (CL), Wayback capture 20240708161439. CL stands for "
            "the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a "
            "time = trading halts (order entry only) until the next 'open'; 'closed' = final close "
            "of the trade date."
        ),
    ),
    date(2024, 7, 4): Citation(
        _svc("2024-07-03", "2024-07-05", "1720455278680"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2024-07-04","events":[{"tradingDate":"2024-07-05","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2024-07-05","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        _svc("2024-07-03", "2024-07-05", "1720455278680"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2024-07-04","events":[{"tradingDate":"2024-07-05","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2024-07-05","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 425 'Crude Oil Futures' (CL), Wayback capture 20240708161439. CL stands for "
            "the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a "
            "time = trading halts (order entry only) until the next 'open'; 'closed' = final close "
            "of the trade date."
        ),
    ),
    date(2024, 9, 2): Citation(
        _svc("2024-09-01", "2024-09-03", "1734710019534"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2024-09-02","events":[{"tradingDate":"2024-09-03","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2024-09-03","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        _svc("2024-09-01", "2024-09-03", "1734710019534"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2024-09-02","events":[{"tradingDate":"2024-09-03","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2024-09-03","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 425 'Crude Oil Futures' (CL), Wayback capture 20241220155340. CL stands for "
            "the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a "
            "time = trading halts (order entry only) until the next 'open'; 'closed' = final close "
            "of the trade date."
        ),
    ),
    date(2024, 11, 28): Citation(
        _svc("2024-11-27", "2024-11-29", "1734710019535"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2024-11-28","events":[{"tradingDate":"2024-11-29","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2024-11-29","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        _svc("2024-11-27", "2024-11-29", "1734710019535"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2024-11-28","events":[{"tradingDate":"2024-11-29","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2024-11-29","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 425 'Crude Oil Futures' (CL), Wayback capture 20241220155340. CL stands for "
            "the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a "
            "time = trading halts (order entry only) until the next 'open'; 'closed' = final close "
            "of the trade date."
        ),
    ),
    date(2024, 11, 29): Citation(
        _svc("2024-11-27", "2024-11-29", "1734710019535"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2024-11-29","events":[{"tradingDate":"2024-11-29","even'
            'tTime":"13:45","marketEventType":"closed"}]}'
        ),
        _svc("2024-11-27", "2024-11-29", "1734710019535"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2024-11-29","events":[{"tradingDate":"2024-11-29","even'
            'tTime":"13:45","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 425 'Crude Oil Futures' (CL), Wayback capture 20241220155340. CL stands for "
            "the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a "
            "time = trading halts (order entry only) until the next 'open'; 'closed' = final close "
            "of the trade date. Close moved from 12:45 CT (2019-2023) to 13:45 CT: CME's 2024 "
            "Thanksgiving settlement notice gives 'Energy Products Normal Settlement Schedule' for "
            "Friday November 29 (the 2023 notice had 'Energy Products 13:30:00 ET'). The "
            "2024-07-08 capture also gives 13:45."
        ),
    ),
    date(2024, 12, 24): Citation(
        _svc("2024-12-24", "2024-12-26", "1734710019537"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2024-12-24","events":[{"tradingDate":"2024-12-24","even'
            'tTime":"12:45","marketEventType":"closed"}]}'
        ),
        _svc("2024-12-24", "2024-12-26", "1734710019537"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2024-12-24","events":[{"tradingDate":"2024-12-24","even'
            'tTime":"12:45","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 425 'Crude Oil Futures' (CL), Wayback capture 20241220155340. CL stands for "
            "the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a "
            "time = trading halts (order entry only) until the next 'open'; 'closed' = final close "
            "of the trade date. Capture 2024-12-20, before the day (the 2024-07-08 capture "
            "agrees). CME's 2024 Christmas settlement notice: 'Energy Products Settlement Time: "
            "13:30:00 ET' (12:30 CT)."
        ),
    ),
    date(2024, 12, 25): Citation(
        _svc("2024-12-24", "2024-12-26", "1734710019537"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2024-12-24","events":[{"tradingDate":"2024-12-24","even'
            'tTime":"12:45","marketEventType":"closed"}]} ... {"groupCode":"CL","eventDate":"2024'
            '-12-25","events":[{"tradingDate":"2024-12-26","eventTime":"16:00","marketEventType":"p'
            'reopen"},{"tradingDate":"2024-12-26","eventTime":"17:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 425 'Crude Oil Futures' (CL), Wayback capture 20241220155340. CL stands for "
            "the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a "
            "time = trading halts (order entry only) until the next 'open'; 'closed' = final close "
            "of the trade date."
        ),
    ),
    date(2025, 1, 1): Citation(
        _svc("2024-12-31", "2025-01-02", "1734710019538"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2024-12-31","events":[{"tradingDate":"2024-12-31","even'
            'tTime":"16:00","marketEventType":"closed"}]} ... {"groupCode":"CL","eventDate":"2025'
            '-01-01","events":[{"tradingDate":"2025-01-02","eventTime":"16:00","marketEventType":"p'
            'reopen"},{"tradingDate":"2025-01-02","eventTime":"17:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 425 'Crude Oil Futures' (CL), Wayback capture 20241220155340. CL stands for "
            "the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a "
            "time = trading halts (order entry only) until the next 'open'; 'closed' = final close "
            "of the trade date. Capture 2024-12-20, before the holiday."
        ),
    ),
    date(2025, 1, 20): Citation(
        _svc("2025-01-19", "2025-01-21", "1734710019539"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2025-01-20","events":[{"tradingDate":"2025-01-21","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2025-01-21","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        _svc("2025-01-19", "2025-01-21", "1734710019539"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2025-01-20","events":[{"tradingDate":"2025-01-21","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2025-01-21","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 425 'Crude Oil Futures' (CL), Wayback capture 20241220155340. CL stands for "
            "the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a "
            "time = trading halts (order entry only) until the next 'open'; 'closed' = final close "
            "of the trade date. Capture 2024-12-20, the only one of this window: CME's schedule as "
            "planned."
        ),
    ),
    date(2025, 2, 17): Citation(
        _svc("2025-02-16", "2025-02-18", "1734710019540"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2025-02-17","events":[{"tradingDate":"2025-02-18","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2025-02-18","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        _svc("2025-02-16", "2025-02-18", "1734710019540"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2025-02-17","events":[{"tradingDate":"2025-02-18","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2025-02-18","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 425 'Crude Oil Futures' (CL), Wayback capture 20241220155340. CL stands for "
            "the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a "
            "time = trading halts (order entry only) until the next 'open'; 'closed' = final close "
            "of the trade date. Capture 2024-12-20, the only one of this window: CME's schedule as "
            "planned."
        ),
    ),
    date(2025, 4, 18): Citation(
        _svc("2025-04-17", "2025-04-19", "1734710019542"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2025-04-17","events":[{"tradingDate":"2025-04-17","even'
            'tTime":"16:00","marketEventType":"closed"}]} ... '
            '{"groupCode":"CL","eventDate":"2025-04-18","events":[]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 425 'Crude Oil Futures' (CL), Wayback capture 20241220155340. CL stands for "
            "the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a "
            "time = trading halts (order entry only) until the next 'open'; 'closed' = final close "
            "of the trade date. Capture 2024-12-20, the only one of this window: CME's schedule as "
            "planned."
        ),
    ),
    date(2025, 5, 26): Citation(
        _svc("2025-05-25", "2025-05-27", "1734710019543"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2025-05-26","events":[{"tradingDate":"2025-05-27","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2025-05-27","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        _svc("2025-05-25", "2025-05-27", "1734710019543"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2025-05-26","events":[{"tradingDate":"2025-05-27","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2025-05-27","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 425 'Crude Oil Futures' (CL), Wayback capture 20241220155340. CL stands for "
            "the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a "
            "time = trading halts (order entry only) until the next 'open'; 'closed' = final close "
            "of the trade date. Capture 2024-12-20, the only one of this window: CME's schedule as "
            "planned."
        ),
    ),
    date(2025, 6, 19): Citation(
        _svc("2025-06-18", "2025-06-20", "1734710019544"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2025-06-19","events":[{"tradingDate":"2025-06-20","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2025-06-20","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        _svc("2025-06-18", "2025-06-20", "1734710019544"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2025-06-19","events":[{"tradingDate":"2025-06-20","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2025-06-20","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 425 'Crude Oil Futures' (CL), Wayback capture 20241220155340. CL stands for "
            "the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a "
            "time = trading halts (order entry only) until the next 'open'; 'closed' = final close "
            "of the trade date. Capture 2024-12-20, the only one of this window: CME's schedule as "
            "planned."
        ),
    ),
    date(2025, 7, 4): Citation(
        _svc("2025-07-03", "2025-07-05", "1734710019545"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2025-07-03","events":[{"tradingDate":"2025-07-03","even'
            'tTime":"16:00","marketEventType":"closed"},{"tradingDate":"2025-07-04","eventTime":"16'
            ':45","marketEventType":"preopen"},{"tradingDate":"2025-07-04","eventTime":"17:00","mar'
            'ketEventType":"open"}]} ... {"groupCode":"CL","eventDate":"2025-07-04","events":[{"t'
            'radingDate":"2025-07-04","eventTime":"12:00","marketEventType":"closed"}]}'
        ),
        _svc("2025-07-03", "2025-07-05", "1734710019545"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2025-07-03","events":[{"tradingDate":"2025-07-03","even'
            'tTime":"16:00","marketEventType":"closed"},{"tradingDate":"2025-07-04","eventTime":"16'
            ':45","marketEventType":"preopen"},{"tradingDate":"2025-07-04","eventTime":"17:00","mar'
            'ketEventType":"open"}]} ... {"groupCode":"CL","eventDate":"2025-07-04","events":[{"t'
            'radingDate":"2025-07-04","eventTime":"12:00","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 425 'Crude Oil Futures' (CL), Wayback capture 20241220155340. CL stands for "
            "the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a "
            "time = trading halts (order entry only) until the next 'open'; 'closed' = final close "
            "of the trade date. Capture 2024-12-20, the only one of this window: CME's schedule as "
            "planned. Friday holiday: 12:00 CT 'closed' (not the 13:30 CT halt of Monday-Thursday "
            "holidays), next open Sunday 17:00 CT; the same pattern as Juneteenth 2026-06-19 "
            "(captures before and after the day). The equity calendar's bars confirmed a 12:00 CT "
            "stop for ES on this day; energy bars are checked in Task 7."
        ),
    ),
    date(2025, 9, 1): Citation(
        _svc("2025-08-31", "2025-09-02", "1734710019546"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2025-09-01","events":[{"tradingDate":"2025-09-02","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2025-09-02","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        _svc("2025-08-31", "2025-09-02", "1734710019546"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2025-09-01","events":[{"tradingDate":"2025-09-02","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2025-09-02","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 425 'Crude Oil Futures' (CL), Wayback capture 20241220155340. CL stands for "
            "the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a "
            "time = trading halts (order entry only) until the next 'open'; 'closed' = final close "
            "of the trade date. Capture 2024-12-20, the only one of this window: CME's schedule as "
            "planned."
        ),
    ),
    date(2025, 11, 27): Citation(
        _svc("2025-11-26", "2025-11-28", "1769649703060"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2025-11-27","events":[{"tradingDate":"2025-11-28","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        _svc("2025-11-26", "2025-11-28", "1769649703060"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2025-11-27","events":[{"tradingDate":"2025-11-28","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 425 'Crude Oil Futures' (CL), Wayback capture 20260129012143. CL stands for "
            "the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a "
            "time = trading halts (order entry only) until the next 'open'; 'closed' = final close "
            "of the trade date."
        ),
    ),
    date(2025, 11, 28): Citation(
        _svc("2025-11-26", "2025-11-28", "1769649703060"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28","even'
            'tTime":"07:00","marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"0'
            '7:30","marketEventType":"open"},{"tradingDate":"2025-11-28","eventTime":"13:45","marke'
            'tEventType":"closed"}]}'
        ),
        _svc("2025-11-26", "2025-11-28", "1769649703060"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28","even'
            'tTime":"07:00","marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"0'
            '7:30","marketEventType":"open"},{"tradingDate":"2025-11-28","eventTime":"13:45","marke'
            'tEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 425 'Crude Oil Futures' (CL), Wayback capture 20260129012143. CL stands for "
            "the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a "
            "time = trading halts (order entry only) until the next 'open'; 'closed' = final close "
            "of the trade date. The 13:45 CT close is the schedule (the 2024-12-20 capture has "
            "only '13:45 closed'); this later capture also records the delayed 07:30 CT open after "
            "the CME outage: LATE_OPENS. CME's 2025 Thanksgiving settlement notice: 'Energy "
            "Products Settlement Times: Normal Settlement Schedule'."
        ),
    ),
    date(2025, 12, 24): Citation(
        _svc("2025-12-24", "2025-12-26", "1769649703064"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2025-12-24","events":[{"tradingDate":"2025-12-24","even'
            'tTime":"12:45","marketEventType":"closed"}]}'
        ),
        _svc("2025-12-24", "2025-12-26", "1769649703064"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2025-12-24","events":[{"tradingDate":"2025-12-24","even'
            'tTime":"12:45","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 425 'Crude Oil Futures' (CL), Wayback capture 20260129012143. CL stands for "
            "the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a "
            "time = trading halts (order entry only) until the next 'open'; 'closed' = final close "
            "of the trade date. CME's 2025 Christmas settlement notice: 'Energy Products "
            "Settlement Time: 13:30:00 ET' (12:30 CT)."
        ),
    ),
    date(2025, 12, 25): Citation(
        _svc("2025-12-24", "2025-12-26", "1769649703064"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2025-12-24","events":[{"tradingDate":"2025-12-24","even'
            'tTime":"12:45","marketEventType":"closed"}]} ... {"groupCode":"CL","eventDate":"2025'
            '-12-25","events":[{"tradingDate":"2025-12-26","eventTime":"16:00","marketEventType":"p'
            'reopen"},{"tradingDate":"2025-12-26","eventTime":"17:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 425 'Crude Oil Futures' (CL), Wayback capture 20260129012143. CL stands for "
            "the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a "
            "time = trading halts (order entry only) until the next 'open'; 'closed' = final close "
            "of the trade date."
        ),
    ),
    date(2026, 1, 1): Citation(
        _svc("2025-12-31", "2026-01-02", "1769649703066"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2025-12-31","events":[{"tradingDate":"2025-12-31","even'
            'tTime":"16:00","marketEventType":"closed"}]} ... {"groupCode":"CL","eventDate":"2026'
            '-01-01","events":[{"tradingDate":"2026-01-02","eventTime":"16:00","marketEventType":"p'
            'reopen"},{"tradingDate":"2026-01-02","eventTime":"17:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 425 'Crude Oil Futures' (CL), Wayback capture 20260129012143. CL stands for "
            "the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a "
            "time = trading halts (order entry only) until the next 'open'; 'closed' = final close "
            "of the trade date."
        ),
    ),
    date(2026, 1, 19): Citation(
        _svc("2026-01-18", "2026-01-20", "1769649703068"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2026-01-19","events":[{"tradingDate":"2026-01-20","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2026-01-20","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        _svc("2026-01-18", "2026-01-20", "1769649703068"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2026-01-19","events":[{"tradingDate":"2026-01-20","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2026-01-20","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 425 'Crude Oil Futures' (CL), Wayback capture 20260129012143. CL stands for "
            "the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a "
            "time = trading halts (order entry only) until the next 'open'; 'closed' = final close "
            "of the trade date."
        ),
    ),
    date(2026, 2, 16): Citation(
        _svc("2026-02-15", "2026-02-17", "1743113432015"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2026-02-16","events":[{"tradingDate":"2026-02-17","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2026-02-17","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        _svc("2026-02-15", "2026-02-17", "1743113432015"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2026-02-16","events":[{"tradingDate":"2026-02-17","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2026-02-17","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 425 'Crude Oil Futures' (CL), Wayback capture 20260610104510. CL stands for "
            "the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a "
            "time = trading halts (order entry only) until the next 'open'; 'closed' = final close "
            "of the trade date."
        ),
    ),
    date(2026, 4, 3): Citation(
        _svc("2026-04-01", "2026-04-03", "1743113432016"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2026-04-02","events":[{"tradingDate":"2026-04-02","even'
            'tTime":"16:00","marketEventType":"closed"}]} ... '
            '{"groupCode":"CL","eventDate":"2026-04-03","events":[]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 425 'Crude Oil Futures' (CL), Wayback capture 20260610104510. CL stands for "
            "the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a "
            "time = trading halts (order entry only) until the next 'open'; 'closed' = final close "
            "of the trade date. Jobs-report Good Friday: equities, rates and FX traded (CME 2026 "
            "Good Friday clearing advisory); energy has no event on 04-03."
        ),
    ),
    date(2026, 5, 25): Citation(
        _svc("2026-05-24", "2026-05-26", "1749141516014"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2026-05-25","events":[{"tradingDate":"2026-05-26","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2026-05-26","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        _svc("2026-05-24", "2026-05-26", "1749141516014"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2026-05-25","events":[{"tradingDate":"2026-05-26","even'
            'tTime":"13:30","marketEventType":"preopen"},{"tradingDate":"2026-05-26","eventTime":"1'
            '7:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 425 'Crude Oil Futures' (CL), Wayback capture 20260619114105. CL stands for "
            "the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a "
            "time = trading halts (order entry only) until the next 'open'; 'closed' = final close "
            "of the trade date."
        ),
    ),
    date(2026, 6, 19): Citation(
        _svc("2026-06-18", "2026-06-20", "1784720540600"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2026-06-18","events":[{"tradingDate":"2026-06-18","even'
            'tTime":"16:00","marketEventType":"closed"},{"tradingDate":"2026-06-22","eventTime":"16'
            ':45","marketEventType":"preopen"},{"tradingDate":"2026-06-22","eventTime":"17:00","mar'
            'ketEventType":"open"}]} ... {"groupCode":"CL","eventDate":"2026-06-19","events":[{"t'
            'radingDate":"2026-06-22","eventTime":"12:00","marketEventType":"closed"}]}'
        ),
        _svc("2026-06-18", "2026-06-20", "1784720540600"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2026-06-18","events":[{"tradingDate":"2026-06-18","even'
            'tTime":"16:00","marketEventType":"closed"},{"tradingDate":"2026-06-22","eventTime":"16'
            ':45","marketEventType":"preopen"},{"tradingDate":"2026-06-22","eventTime":"17:00","mar'
            'ketEventType":"open"}]} ... {"groupCode":"CL","eventDate":"2026-06-19","events":[{"t'
            'radingDate":"2026-06-22","eventTime":"12:00","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 425 'Crude Oil Futures' (CL), Wayback capture 20260722114220. CL stands for "
            "the group: CME's holiday schedules give energy hours per asset class. 'preopen' at a "
            "time = trading halts (order entry only) until the next 'open'; 'closed' = final close "
            "of the trade date. Friday holiday: 12:00 CT 'closed', next open Sunday 17:00 CT "
            "(trade date 06-22). The 2026-01-29 and 2026-06-19 captures agree. The same capture "
            "shows Saturday 06-20 events ('05:00 open', '17:00 closed', trade date 06-22) for CL, "
            "ES and GC alike; 06-20 is outside the coverage and is not an entry."
        ),
    ),
}

LATE_OPEN_SOURCES: dict[date, Citation] = {
    date(2025, 11, 28): Citation(
        "https://www.sec.gov/Archives/edgar/data/1156375/000115637526000009/cme-20251231.htm",
        (
            "On November 27, 2025, our largest data center owned and operated by CyrusOne "
            "experienced a critical cooling failure caused by human error. In response to the "
            "critical cooling failure, we made the decision to temporarily halt our markets. Our "
            "markets opened the following day on a delayed basis."
        ),
        _svc("2025-11-26", "2025-11-28", "1769649703060"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28","even'
            'tTime":"07:00","marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"0'
            '7:30","marketEventType":"open"},{"tradingDate":"2025-11-28","eventTime":"13:45","marke'
            'tEventType":"closed"}]}'
        ),
        note=(
            "Unscheduled. Status: CME Group's 2025 Form 10-K (SEC EDGAR, read from its Wayback "
            "capture; sec.gov refused the direct fetch). Open time: CME's CL service record for "
            "eventDate 2025-11-28 in the 2026-01-29 capture adds '07:00 preopen' and '07:30 open' "
            "before the scheduled 13:45 close; the 2024-12-20 capture (the plan) has only the "
            "13:45 close. The time trading stopped on the evening of 2025-11-27 is in no CME "
            "document retrieved (halt_from_ct None). The outage hit every CME Globex group; "
            "data/cme_calendar.py does not record it."
        ),
    ),
}

# CME-stated regular energy days near holidays, kept so the absence of an entry is a recorded
# finding, not an oversight.
NO_ENTRY_FINDINGS: dict[date, Citation] = {
    date(2019, 7, 3): Citation(
        _Z19,
        (
            "Calendar Date|Wednesday July 3 |Wednesday,July 3|Thursday July 4 |Thursday July 4 "
            "into Friday July 5 ... Product|CLOSE|OPEN|HALT|OPEN ... Energy, Metals & DME |Regular "
            "@ 1600 CT / 2100 UTC|Regular @ 1700 CT/ 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT "
            "/ 2200 UTC"
        ),
        note=(
            "Day before Independence Day: regular close. Zip member "
            "globex-trading-schedules/2019-4th-of-july-holiday-schedule-compact.xls; the zip's "
            "sha256 is the document hash. CME's compact Globex holiday schedule states hours per "
            "asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX "
            "metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The "
            "only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, "
            "Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for "
            "example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / "
            "1330 ET'). Energy's Wednesday July 3 CLOSE is 'Regular @ 1600 CT' (equities closed "
            "early at 12:15 CT that day)."
        ),
    ),
    date(2019, 10, 14): Citation(
        _HC + "2019-columbus-day-holiday-settlement-times.pdf",
        "All products will settle at their normal times for the Columbus Day Holiday",
        note=(
            "Columbus Day: normal. Settlement notice; Columbus Day and Veterans Day are "
            "bond-market holidays that do not change NYMEX energy hours in any schedule read."
        ),
    ),
    date(2019, 12, 31): Citation(
        _Z19,
        (
            "Calendar Trade|Tuesday, Dec 31|Wednessday, Jan 1 |Wednesday, Jan 1|Thursday, Jan "
            "2|Thursday, Jan 2 ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Closed for "
            "New Year's|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
        ),
        note=(
            "New Year's Eve: regular close. Zip member "
            "globex-trading-schedules/2019-new-years-holiday-schedule-compact.xls; the zip's "
            "sha256 is the document hash. CME's compact Globex holiday schedule states hours per "
            "asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX "
            "metals and DME). CL, MCL, QM, NG, MNG, QG, RB and HO are not named individually. The "
            "only energy exception rows in CME's full 2019-2022 schedules are DME Oman Crude TAM, "
            "Singapore TAM and EUA Daily Futures, and their energy notes concern TAS/TAM only (for "
            "example 'Crude, Heating Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / "
            "1330 ET'). Tuesday Dec 31 CLOSE 'Regular @ 1600 CT'."
        ),
    ),
    date(2020, 7, 2): Citation(
        _Z20,
        (
            "Calendar Date|Thursday July 2|Thursday , July 2|Friday July 3|Sunday July 5 into "
            "Monday July 6 ... Energy, Metals & DME |Regular @ 1600 CT / 2100 UTC|Regular @ 1700 "
            "CT/ 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "Day before Independence Day (observed): regular close. Zip member "
            "2020-4th-of-july-holiday-schedule-compact.xls; the zip's sha256 is the document hash. "
            "CME's compact Globex holiday schedule states hours per asset-class row; the row is "
            "'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, "
            "QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows "
            "in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily "
            "Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating "
            "Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET'). Thursday July "
            "2 CLOSE 'Regular @ 1600 CT'."
        ),
    ),
    date(2020, 12, 31): Citation(
        _Z20,
        (
            "Calendar Trade|Thursday,Dec 31|Friday,Jan 1|Sunday,Jan 3|Monday, Jan 4|Monday, Jan 4 "
            "... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Closed for New Year's|Regular "
            "@ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
        ),
        note=(
            "New Year's Eve: regular close. Zip member "
            "2021-new-years-holiday-schedule-compact.xls; the zip's sha256 is the document hash. "
            "CME's compact Globex holiday schedule states hours per asset-class row; the row is "
            "'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, "
            "QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows "
            "in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily "
            "Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating "
            "Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET'). Thursday Dec "
            "31 CLOSE 'Regular @ 1600 CT'."
        ),
    ),
    date(2021, 12, 23): Citation(
        _Z21,
        (
            "Products|Thursday, Dec 23|Friday,Dec 24|Sunday 26|Monday,Dec 27 ... Energy, Metals & "
            "DME |Regular per Product|Closed for Christmas"
        ),
        note=(
            "Day before Christmas (observed): regular close. Zip member "
            "2021-christmas-holiday-schedule-compact.xls; the zip's sha256 is the document hash. "
            "CME's compact Globex holiday schedule states hours per asset-class row; the row is "
            "'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, "
            "QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows "
            "in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily "
            "Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating "
            "Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET'). Thursday Dec "
            "23: 'Regular per Product'."
        ),
    ),
    date(2021, 12, 31): Citation(
        _Z21,
        (
            "CME Group Globex New Years Holiday Schedule: December 30, 2021 - January 3, 2022 ... "
            "Calendar Trade|Thursday,Dec 30|Thursday,Dec 30|Friday,Dec 31|Friday,Dec 31|Sunday,Jan "
            "2|Monday, Jan 3 ... Energy, Metals & DME |Regular @ 1600 CT / 2200 UTC|Regular @ 1700 "
            "CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC"
        ),
        note=(
            "New Year's Eve (New Year's Day on Saturday): regular. Zip member "
            "2022-new-years-holiday-schedule-compact.xls; the zip's sha256 is the document hash. "
            "CME's compact Globex holiday schedule states hours per asset-class row; the row is "
            "'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). CL, MCL, "
            "QM, NG, MNG, QG, RB and HO are not named individually. The only energy exception rows "
            "in CME's full 2019-2022 schedules are DME Oman Crude TAM, Singapore TAM and EUA Daily "
            "Futures, and their energy notes concern TAS/TAM only (for example 'Crude, Heating "
            "Oil, RBOB & Nat Gas TAS contracts close early at 12:30 CT / 1330 ET'). January 1, "
            "2022 fell on a Saturday: Friday Dec 31 and Monday Jan 3 both regular for energy."
        ),
    ),
    date(2022, 7, 1): Citation(
        _HC + "2022-independence-day-holiday-schedule-compact.xls",
        (
            "Calendar Date|Friday July 1|Sunday July 3|Monday July 4|Monday July 4 ... Energy, "
            "Metals & DME |Regular @ 1600 CT / 2100 UTC"
        ),
        note="Friday before Independence Day: regular close.",
    ),
    date(2022, 12, 23): Citation(
        _HC + "2022-christmas-holiday-schedule.xls",
        (
            "Calendar Date|Friday, December 23||||||||Monday, December 26 ... Energy, Metals & DME "
            "products (see notes below)|04:00:00 PM||||||||Globex Closed"
        ),
        note=(
            "Friday before Christmas (observed): regular close. Column 1 (Friday December 23) "
            "close 16:00. The 2022 Christmas settlement notice moves only interest-rate products "
            "early on Dec 23."
        ),
    ),
    date(2022, 12, 30): Citation(
        _HC + "2023-new-years-holiday-schedule-compact.xls",
        (
            "Calendar Trade|Friday,Dec 30|Sunday, Jan 1 and Monday, Jan 2 ... Energy, Metals & DME "
            "|Regular @ 1600 CT / 2200 UTC|Globex Closed"
        ),
        note="Friday before New Year's Day (observed): regular close.",
    ),
    date(2023, 7, 3): Citation(
        _HC + "fourth-of-july-settlement-times-2023.pdf",
        (
            "Monday, July 3, 2023 ... All other products will settle at their normal times on "
            "Monday July 3rd"
        ),
        note=(
            "Day before Independence Day: regular. Settlement notice (only interest-rate and "
            "equity-index products settle early). CME's 4th-of-july-2023.pdf summary shows ENERGY "
            "'TRADE DATE: MON 3 JULY 16:00 (CLOSED)' in the Monday column (layout text interleaves "
            "columns)."
        ),
    ),
    date(2023, 12, 22): Citation(
        _HC + "christmas-holiday-settlement-times-2023.pdf",
        (
            "Friday, December 22, 2023 ... Interest Rate Products ... All other products will "
            "settle at their normal times"
        ),
        note=(
            "Friday before Christmas: regular. Settlement notice only; no Globex-hours document "
            "for 2023-12-22 was retrieved."
        ),
    ),
    date(2024, 7, 3): Citation(
        _svc("2024-07-03", "2024-07-05", "1720455278680"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2024-07-03","events":[{"tradingDate":"2024-07-03","even'
            'tTime":"16:00","marketEventType":"closed"},{"tradingDate":"2024-07-05","eventTime":"16'
            ':45","marketEventType":"preopen"},{"tradingDate":"2024-07-05","eventTime":"17:00","mar'
            'ketEventType":"open"}]}'
        ),
        note=(
            "Day before Independence Day: regular close. CME's trading-hours-by-product service "
            "behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback "
            "capture 20240708161439. CL stands for the group: CME's holiday schedules give energy "
            "hours per asset class. 'preopen' at a time = trading halts (order entry only) until "
            "the next 'open'; 'closed' = final close of the trade date."
        ),
    ),
    date(2024, 12, 31): Citation(
        _svc("2024-12-31", "2025-01-02", "1734710019538"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2024-12-31","events":[{"tradingDate":"2024-12-31","even'
            'tTime":"16:00","marketEventType":"closed"}]}'
        ),
        note=(
            "New Year's Eve: regular close. CME's trading-hours-by-product service behind "
            "cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback "
            "capture 20241220155340. CL stands for the group: CME's holiday schedules give energy "
            "hours per asset class. 'preopen' at a time = trading halts (order entry only) until "
            "the next 'open'; 'closed' = final close of the trade date."
        ),
    ),
    date(2025, 1, 9): Citation(
        _TH + "day-of-mourning-january-9-2024.pdf",
        "PRODUCT NAME JANUARY 9, 2025 ... CME GROUP ENERGY NORMAL HOURS",
        note=(
            "National Day of Mourning (Carter): energy normal hours. CME's trading schedule for "
            "January 9, 2025 (file name says 2024): equities closed at 08:30 CT and rates early, "
            "energy traded normal hours. The equity calendar has an 08:30 CT entry that day; "
            "energy has none."
        ),
    ),
    date(2025, 7, 3): Citation(
        _svc("2025-07-03", "2025-07-05", "1734710019545"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2025-07-03","events":[{"tradingDate":"2025-07-03","even'
            'tTime":"16:00","marketEventType":"closed"},{"tradingDate":"2025-07-04","eventTime":"16'
            ':45","marketEventType":"preopen"},{"tradingDate":"2025-07-04","eventTime":"17:00","mar'
            'ketEventType":"open"}]}'
        ),
        note=(
            "Day before Independence Day: regular close. CME's trading-hours-by-product service "
            "behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback "
            "capture 20241220155340. CL stands for the group: CME's holiday schedules give energy "
            "hours per asset class. 'preopen' at a time = trading halts (order entry only) until "
            "the next 'open'; 'closed' = final close of the trade date."
        ),
    ),
    date(2025, 12, 31): Citation(
        _svc("2025-12-31", "2026-01-02", "1769649703066"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2025-12-31","events":[{"tradingDate":"2025-12-31","even'
            'tTime":"16:00","marketEventType":"closed"}]}'
        ),
        note=(
            "New Year's Eve: regular close. CME's trading-hours-by-product service behind "
            "cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback "
            "capture 20260129012143. CL stands for the group: CME's holiday schedules give energy "
            "hours per asset class. 'preopen' at a time = trading halts (order entry only) until "
            "the next 'open'; 'closed' = final close of the trade date."
        ),
    ),
    date(2026, 4, 2): Citation(
        _svc("2026-04-01", "2026-04-03", "1743113432016"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2026-04-02","events":[{"tradingDate":"2026-04-02","even'
            'tTime":"16:00","marketEventType":"closed"}]}'
        ),
        note=(
            "Thursday before Good Friday: regular close. CME's trading-hours-by-product service "
            "behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback "
            "capture 20260610104510. CL stands for the group: CME's holiday schedules give energy "
            "hours per asset class. 'preopen' at a time = trading halts (order entry only) until "
            "the next 'open'; 'closed' = final close of the trade date."
        ),
    ),
    date(2026, 6, 18): Citation(
        _svc("2026-06-18", "2026-06-20", "1784720540600"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2026-06-18","events":[{"tradingDate":"2026-06-18","even'
            'tTime":"16:00","marketEventType":"closed"},{"tradingDate":"2026-06-22","eventTime":"16'
            ':45","marketEventType":"preopen"},{"tradingDate":"2026-06-22","eventTime":"17:00","mar'
            'ketEventType":"open"}]}'
        ),
        note=(
            "Thursday before Juneteenth: regular close. CME's trading-hours-by-product service "
            "behind cmegroup.com/trading-hours.html, product 425 'Crude Oil Futures' (CL), Wayback "
            "capture 20260722114220. CL stands for the group: CME's holiday schedules give energy "
            "hours per asset class. 'preopen' at a time = trading halts (order entry only) until "
            "the next 'open'; 'closed' = final close of the trade date."
        ),
    ),
}

SESSION_SOURCES: dict[str, Citation] = {
    "cme_energy_hours": Citation(
        "https://www.cmegroup.com/trading/energy/crude-oil/light-sweet-crude_contract_specifications.html",
        (
            "Trading Hours Sunday - Friday 6:00 p.m. - 5:00 p.m. (5:00 p.m. - 4:00 p.m. CT) with a "
            "60-minute break each day beginning at 5:00 p.m. (4:00 p.m. CT)"
        ),
        _svc("2026-01-18", "2026-01-20", "1769649703068"),
        (
            '"globex":"CL","prodGroup":"CL","name":"Crude Oil Futures","id":425 ... '
            '{"groupCode":"CL","eventDate":"2026-01-20","events":[{"tradingDate":"2026-01-20","even'
            'tTime":"16:00","marketEventType":"closed"},{"tradingDate":"2026-01-21","eventTime":"16'
            ':45","marketEventType":"preopen"},{"tradingDate":"2026-01-21","eventTime":"17:00","mar'
            'ketEventType":"open"}]}'
        ),
        note=(
            "Regular NYMEX energy Globex session, Sunday-Friday 17:00-16:00 CT with the daily "
            "16:00-17:00 CT halt: CME's CL contract specifications (capture 2019-08-06) and CME's "
            "2026 CL trading-hours record (16:00 closed, 16:45 pre-open, 17:00 open). The other "
            "SESSION_SOURCES keys give the same hours for NG, RB, HO (2019), MCL and QM (2021 fact "
            "card) and MNG (2025 FAQ). No CME notice of a change to NYMEX energy Globex hours in "
            "2019-2026 was found."
        ),
    ),
    "cme_ng_hours": Citation(
        "https://www.cmegroup.com/trading/energy/natural-gas/natural-gas_contract_specifications.html",
        (
            "Trading Hours Sunday - Friday 6:00 p.m. - 5:00 p.m. (5:00 p.m. - 4:00 p.m. /CT) with "
            "a 60-minute break each day beginning at 5:00 p.m. (4:00 p.m. CT)"
        ),
        note="NG contract specifications, capture 2019-09-15.",
    ),
    "cme_rb_hours": Citation(
        "https://www.cmegroup.com/trading/energy/refined-products/rbob-gasoline_contract_specifications.html",
        (
            "Trading Hours Sunday - Friday 6:00 p.m. - 5:00 p.m. (5:00 p.m. - 4:00 p.m. CT) with a "
            "60-minute break each day beginning at 5:00 p.m. (4:00 p.m. CT)"
        ),
        note="RB contract specifications, capture 2019-09-15.",
    ),
    "cme_ho_hours": Citation(
        "https://www.cmegroup.com/trading/energy/refined-products/heating-oil_contract_specifications.html",
        (
            "Trading Hours CME Globex: Sunday - Friday 6:00 p.m. - 5:00 p.m. (5:00 p.m. - 4:00 "
            "p.m. Chicago Time/CT) with a 60-minute break each day beginning at 5:00 p.m. (4:00 "
            "p.m. CT)"
        ),
        note="HO contract specifications, capture 2019-09-19.",
    ),
    "cme_mcl_qm_hours": Citation(
        "https://www.cmegroup.com/trading/energy/files/micro-wti-crude-oil-futures-fact-card.pdf",
        (
            "PRODUCT CODE MCL QM CL ... CME Globex: Sunday – Friday: 5:00 p.m. to 4:00 p.m. "
            "Central Time (CT) ... Monday – Friday: 60-minute daily trading halt beginning at 4:00 "
            "p.m. CT"
        ),
        note="Micro WTI fact card (capture 2021-10-16): one trading-hours line for MCL, QM and CL.",
    ),
    "cme_mng_hours": Citation(
        "https://www.cmegroup.com/articles/faqs/micro-henry-hub-natural-gas-futures-and-options-frequently-asked-questions.html",
        (
            "PRODUCT CODE MNG QG MNO ... TRADING SCHEDULE CME Globex: Sunday – Friday: 5:00 p.m. "
            "to 4:00 p.m. Central Time (CT) ... Monday – Friday: 60-minute daily trading halt "
            "beginning at 4:00 p.m. CT"
        ),
        note=(
            "Micro Henry Hub FAQ (capture 2025-01-14): MNG, QG and NG share the Globex schedule. "
            "The FAQ dates MNG's launch to November 2023."
        ),
    ),
    "cme_energy_settlement": Citation(
        "https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457085528/Daily+Settlement+Time+Details",
        "Energy Products 14:28:00-14:30:00 ET",
        "https://www.cmegroup.com/confluence/display/EPICSANDBOX/NYMEX+Crude+Oil",
        (
            "last modified by Confluence Admin on May 08, 2019 ... The settlement period is "
            "defined as: 14:28:00 to 14:30:00 ET for the Active Month and 14:28:00 to 14:30:00 ET "
            "for calendar spreads."
        ),
        note=(
            "D6 confirmation of C: CME's daily settlement time range for 'Energy Products' is "
            "14:28:00-14:30:00 ET = 13:28:00-13:30:00 CT (CME client wiki 'Daily Settlement Time "
            "Details', updated 2025-01-03, read directly). The CL procedure page as captured "
            "2021-12-02 (last modified 2019-05-08) gives the same period, so C = 13:30 CT held for "
            "the whole 2019-2026 window. MCL and MNG have no product page of their own; the "
            "'Energy Products' line covers them."
        ),
    ),
    "cme_cl_qm_settlement": Citation(
        "https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457218849/NYMEX+Crude+Oil",
        (
            "NYMEX Light Sweet Crude Oil (CL) futures are settled by CME Group staff based on "
            "trading activity on CME Globex during the settlement period. The settlement period is "
            "defined as: 14:28:00 to 14:30:00 ET for the Active Month ... The settlements in the "
            "E-mini Crude Oil (QM) futures contracts are derived directly from the settlements of "
            "the regular sized Crude Oil (CL) futures contracts"
        ),
        note="CME client wiki 'NYMEX Crude Oil' (updated 2025-08-27, read directly).",
    ),
    "cme_ng_qg_settlement": Citation(
        "https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457415061/Natural+Gas",
        (
            "NYMEX Natural Gas (NG) futures are settled by CME Group staff based on trading "
            "activity on CME Globex during the settlement period. The settlement period is defined "
            "as: 14:28:00 to 14:30:00 ET ... The settlements in the E-Mini Natural Gas (QG) "
            "futures contracts are derived directly from the settlements of the regular sized "
            "Natural Gas (NG) contracts"
        ),
        note="CME client wiki 'Natural Gas' (updated 2025-08-27, read directly).",
    ),
    "cme_ho_settlement": Citation(
        "https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457415161/NYMEX+Heating+Oil",
        (
            "NYMEX NY Harbor ULSD (HO) futures are settled by CME Group staff based on trading "
            "activity on CME Globex during the settlement period. The settlement period is defined "
            "as: 14:28:00 to 14:30:00 ET for the Active Month"
        ),
        note="CME client wiki 'NYMEX Heating Oil' (updated 2025-08-27, read directly).",
    ),
    "cme_rb_settlement": Citation(
        "https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457088078/NYMEX+RBOB+Gasoline",
        (
            "NYMEX RBOB Gasoline (RB) futures are settled by CME Group staff based on trading "
            "activity on CME Globex during the settlement period. The settlement period is defined "
            "as: 14:28:00 to 14:30:00 ET for the Active Month"
        ),
        note="CME client wiki 'NYMEX RBOB Gasoline' (updated 2025-08-27, read directly).",
    ),
}
