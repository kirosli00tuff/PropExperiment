"""CME Globex calendar for the metals group: COMEX GC, MGC, SI, SIL, HG and MHG,
2019-05-01..2026-06-19 (Stage E.2a Task 6; design D10 and D11.3).

Interface as data.cme_calendar, whose Holiday, HolidayKind, Citation and CalendarCoverageError are
imported, not redefined: HOLIDAYS, SOURCES, NO_ENTRY_FINDINGS, CALENDAR_COVERAGE and
assert_calendar_coverage, plus SESSIONS (data.calendars.SessionSpec) with SESSION_SOURCES. One
additive extension, which no existing caller needs to know about: LATE_OPENS, trade dates whose
Globex session did not trade from its regular start (one, the unscheduled CME outage before the
2025-11-28 open), with LATE_OPEN_SOURCES. Its LateOpen type has the same fields as the rates and
energy groups' (data/calendars/rates.py, data/calendars/energy.py), so the groups read alike.

Sources (all CME Group, except the SEC copy of CME's 10-K; cmegroup.com refuses automated
fetches, so every cmegroup.com file was read from a Wayback Machine copy; the CME client wiki on
atlassian.net was read directly through its REST API):
- 2019-2021: CME's Globex holiday trading schedules (.xls) inside CME's yearly
  holiday-calendars.zip, compact sheets, row "Energy, Metals & DME".
- 2022 and New Year 2023: CME's per-holiday Globex schedules (.xls), same row.
- 2023: CME's holiday summary PDFs (cmegroup.com/trading-hours/files/ and the fixed names
  cmegroup.com/files/presidents-day.pdf and good-friday.pdf), row "METALS"; MLK Day 2023 from
  CME's settlement notice (status) and the METALS row of CME's Presidents Day 2023 PDF (time,
  inferred).
- 2023-09..2026-06: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html,
  product 437 (GC, Gold Futures), captures of 2024-07-08, 2024-12-20, 2026-01-29, 2026-06-10,
  2026-06-19 and 2026-07-22.
- 2025-11-28 late open: CME Group's 2025 Form 10-K (status) and the service record (time).
- Regular session and D6's C: CME contract specifications, fact card and FAQ (hours), CME client
  wiki settlement procedures for Gold, Silver and Copper and its Daily Settlement Time Details.
Verbatim quotes, capture URLs and file hashes per entry, and the script-run verbatim check:
reports/stage_e2a_calendar_sources_metals.json and .md. CME states these hours for its metals
asset class ("Energy, Metals & DME", "METALS") or for GC, the most active metals contract; MGC,
SI, SIL, HG and MHG are taken to share them (no COMEX metals exception row appears in the
schedules read; their only metals notes concern TAS).

Grades as data.cme_calendar: status (``evidence``) "cme" | "secondary" | "unverified"; time
(``time_evidence``) "cme" | "secondary" | "inferred" | "unverified" | "n/a" ("empirical" is
reserved for the later bar check). Every status here is "cme". Every time is "cme" except
2023-01-16 ("inferred": 13:30 CT from CME's own METALS row of Presidents Day 2023 and every COMEX
metals holiday halt of 2022-2026; no CME schedule with a metals row was retrievable for that day).

The metals calendar coincides entry for entry with the energy calendar (data/calendars/energy.py):
the two groups share one CME row in 2019-2022, and CME's METALS and ENERGY rows (2023) and its GC
and CL records (2023-09..2026-06) agree on every date. How metals differ from the equity calendar:
- Holiday halts (MLK, Presidents, Memorial, Juneteenth, Independence, Labor, Thanksgiving Day)
  are 12:00 CT in 2019-2021 and 13:30 CT from 2022-01-17 on. A holiday on a Friday (2020-07-03,
  2025-07-04, 2026-06-19) closes at 12:00 CT in both periods, with the Sunday 17:00 CT reopen.
- The day after Thanksgiving closes at 12:45 CT in 2019-2023 and at 13:45 CT from 2024; Christmas
  Eve closes at 12:45 CT.
- The eve of Independence Day, New Year's Eve and the days before observed Christmas / New Year
  keep the regular 16:00 CT close (NO_ENTRY_FINDINGS); metals traded normal hours on the
  2025-01-09 National Day of Mourning; Good Friday is a full closure every year, including the
  jobs-report Good Fridays (2021-04-02, 2023-04-07, 2026-04-03) on which equities traded.

Conventions: ``halt_ct`` is the CT minute trading stops, so the last one-minute bar starts at
halt_ct minus one minute; the reopen is the normal 17:00 CT (Sunday 17:00 when the halt day is a
Friday). CME books the Globex session that ends at a holiday halt to the next trade date; this
module keeps each halt day as its own short trade date, as data.cme_calendar does. Holdout-2
dates (2024-04-01..2025-03-31) and the 2019-05..2024-02 confirmation window rest on CME's
schedules alone until their bars are checked. Product listing dates are not calendar entries.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, time

from data.calendars import Segment, SessionSpec
from data.cme_calendar import CalendarCoverageError, Citation, Holiday, HolidayKind

METALS_PRODUCTS = ("GC", "MGC", "SI", "SIL", "HG", "MHG")
# design D6's metals sub-groups, the keys of SessionSpec.day_session_ct
SUBGROUP_OF_PRODUCT: dict[str, str] = {
    "GC": "gold", "MGC": "gold", "SI": "silver", "SIL": "silver", "HG": "copper", "MHG": "copper",
}

HALT_NOON = time(12, 0)  # holiday halt 2019-2021; Friday-holiday close in every year
HALT_1330 = time(13, 30)  # holiday halt from 2022-01-17
CLOSE_1245 = time(12, 45)  # Christmas Eve; day after Thanksgiving 2019-2023
CLOSE_1345 = time(13, 45)  # day after Thanksgiving from 2024

_HC = "https://www.cmegroup.com/tools-information/holiday-calendar/files/"
_TH = "https://www.cmegroup.com/trading-hours/files/"
_Z19, _Z20, _Z21 = (_HC + f"{y}-holiday-calendars.zip" for y in (2019, 2020, 2021))
_METALS = "https://www.cmegroup.com/trading/metals/"
_WIKI = "https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/"
_CONF = "https://www.cmegroup.com/confluence/display/EPICSANDBOX/"


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
    data.cme_calendar.assert_calendar_coverage, for the metals group."""
    first, last = CALENDAR_COVERAGE
    outside = sorted(d for d in set(days) if not first <= d <= last)
    if outside:
        raise CalendarCoverageError(
            f"{len(outside)} trade date(s) outside the metals calendar's coverage "
            f"{first}..{last}: {outside[0]} .. {outside[-1]}; extend data/calendars/metals.py "
            "first")


@dataclass(frozen=True)
class LateOpen:
    """A trade date whose Globex session did not trade from its regular start: trading stopped at
    ``halt_from_ct`` on the calendar day ``halt_from_offset_days`` from ``day`` (None: the stop
    time is not in any source retrieved) and resumed at ``open_ct`` CT on ``day``. Grades as for
    Holiday. Additive to the data.cme_calendar interface; same fields as the rates and energy
    groups'."""

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

# One regime covers the whole window: no CME change to COMEX metals Globex hours or to the gold,
# silver or copper settlement periods was found.
SESSIONS: tuple[SessionSpec, ...] = (
    SessionSpec(
        valid_from=date(2019, 5, 1),
        valid_to=date(2026, 6, 19),
        segments=(Segment(-1, time(17, 0), 0, time(16, 0)),),
        day_session_ct={
            "gold": (time(7, 20), time(12, 30)),
            "silver": (time(7, 20), time(12, 25)),
            "copper": (time(7, 10), time(12, 0)),
        },
        source="cme_metals_hours",
        note=(
            "day_session_ct is design D6's metals rows keyed by sub-group (gold: GC, MGC; "
            "silver: SI, SIL; copper: HG, MHG; SUBGROUP_OF_PRODUCT); F 15:08 CT is applied by "
            "the rules engine and lies inside the 17:00-16:00 CT session. D6 confirmation: every "
            "C matches the end of CME's daily settlement period, unchanged 2019-2026: gold "
            "13:29:00-13:30:00 ET = 12:29-12:30 CT (C 12:30), silver 12:24:00-12:25:00 CT "
            "(13:24-13:25 ET; C 12:25), copper 12:59:00-13:00:00 ET = 11:59-12:00 CT (C 12:00); "
            "MGC, SIL and MHG settle to GC, SI and HG (SESSION_SOURCES keys "
            "'cme_metals_settlement', 'cme_gc_mgc_settlement', 'cme_si_sil_settlement', "
            "'cme_hg_mhg_settlement'). O (07:20 gold and silver, 07:10 copper) is not a boundary "
            "CME publishes for COMEX metals: the Globex session runs 17:00-16:00 CT and no CME "
            "settlement procedure or contract specification retrieved defines a day-session "
            "open. CME's holiday settlement notices move metals settlement one hour earlier on "
            "early-close days (for example Christmas Eve 2019, 2024 and 2025: Gold 12:30:00 ET, "
            "Silver 12:25:00 ET, Copper 12:00:00 ET); its 2025 day-after-Thanksgiving notice "
            "keeps the normal schedule. D6's values are encoded unchanged; the lead rules "
            "(reports/stage_e2a_calendar_sources_metals.md, D6 confirmation)."
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
            "with COMEX metals and DME). GC, MGC, SI, SIL, HG and MHG are not named individually. "
            "CME's full 2019-2022 schedules carry the row 'Energy, Metals, Softs & DME Products' "
            "(2022: 'Energy, Metals & DME Products') whose only exception rows are DME Oman Crude "
            "TAM, Singapore TAM and EUA Daily Futures; their only COMEX metals notes concern TAS "
            "(for example 'Gold TAS – Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the "
            "full sheets belongs to Bursa Malaysia Derivatives, not COMEX."
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
            "with COMEX metals and DME). GC, MGC, SI, SIL, HG and MHG are not named individually. "
            "CME's full 2019-2022 schedules carry the row 'Energy, Metals, Softs & DME Products' "
            "(2022: 'Energy, Metals & DME Products') whose only exception rows are DME Oman Crude "
            "TAM, Singapore TAM and EUA Daily Futures; their only COMEX metals notes concern TAS "
            "(for example 'Gold TAS – Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the "
            "full sheets belongs to Bursa Malaysia Derivatives, not COMEX."
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
            "COMEX metals and DME). GC, MGC, SI, SIL, HG and MHG are not named individually. CME's "
            "full 2019-2022 schedules carry the row 'Energy, Metals, Softs & DME Products' (2022: "
            "'Energy, Metals & DME Products') whose only exception rows are DME Oman Crude TAM, "
            "Singapore TAM and EUA Daily Futures; their only COMEX metals notes concern TAS (for "
            "example 'Gold TAS – Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full "
            "sheets belongs to Bursa Malaysia Derivatives, not COMEX."
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
            "with COMEX metals and DME). GC, MGC, SI, SIL, HG and MHG are not named individually. "
            "CME's full 2019-2022 schedules carry the row 'Energy, Metals, Softs & DME Products' "
            "(2022: 'Energy, Metals & DME Products') whose only exception rows are DME Oman Crude "
            "TAM, Singapore TAM and EUA Daily Futures; their only COMEX metals notes concern TAS "
            "(for example 'Gold TAS – Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the "
            "full sheets belongs to Bursa Malaysia Derivatives, not COMEX."
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
            "with COMEX metals and DME). GC, MGC, SI, SIL, HG and MHG are not named individually. "
            "CME's full 2019-2022 schedules carry the row 'Energy, Metals, Softs & DME Products' "
            "(2022: 'Energy, Metals & DME Products') whose only exception rows are DME Oman Crude "
            "TAM, Singapore TAM and EUA Daily Futures; their only COMEX metals notes concern TAS "
            "(for example 'Gold TAS – Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the "
            "full sheets belongs to Bursa Malaysia Derivatives, not COMEX."
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
            "COMEX metals and DME). GC, MGC, SI, SIL, HG and MHG are not named individually. CME's "
            "full 2019-2022 schedules carry the row 'Energy, Metals, Softs & DME Products' (2022: "
            "'Energy, Metals & DME Products') whose only exception rows are DME Oman Crude TAM, "
            "Singapore TAM and EUA Daily Futures; their only COMEX metals notes concern TAS (for "
            "example 'Gold TAS – Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full "
            "sheets belongs to Bursa Malaysia Derivatives, not COMEX."
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
            "COMEX metals and DME). GC, MGC, SI, SIL, HG and MHG are not named individually. CME's "
            "full 2019-2022 schedules carry the row 'Energy, Metals, Softs & DME Products' (2022: "
            "'Energy, Metals & DME Products') whose only exception rows are DME Oman Crude TAM, "
            "Singapore TAM and EUA Daily Futures; their only COMEX metals notes concern TAS (for "
            "example 'Gold TAS – Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full "
            "sheets belongs to Bursa Malaysia Derivatives, not COMEX."
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
            "COMEX metals and DME). GC, MGC, SI, SIL, HG and MHG are not named individually. CME's "
            "full 2019-2022 schedules carry the row 'Energy, Metals, Softs & DME Products' (2022: "
            "'Energy, Metals & DME Products') whose only exception rows are DME Oman Crude TAM, "
            "Singapore TAM and EUA Daily Futures; their only COMEX metals notes concern TAS (for "
            "example 'Gold TAS – Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full "
            "sheets belongs to Bursa Malaysia Derivatives, not COMEX. The member file is named "
            "2019-new-years but its title covers 2019-12-31 to 2020-01-02."
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
            "DME). GC, MGC, SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 "
            "schedules carry the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals "
            "& DME Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and "
            "EUA Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX."
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
            "DME). GC, MGC, SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 "
            "schedules carry the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals "
            "& DME Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and "
            "EUA Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX."
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
            "is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). GC, MGC, "
            "SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 schedules carry "
            "the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals & DME "
            "Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and EUA "
            "Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX."
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
            "DME). GC, MGC, SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 "
            "schedules carry the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals "
            "& DME Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and "
            "EUA Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX."
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
            "DME). GC, MGC, SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 "
            "schedules carry the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals "
            "& DME Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and "
            "EUA Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX. Friday holiday: CME labels the 12:00 CT event "
            "a close (header 'ClOSE'), and the next open is Sunday July 5 at 17:00 CT."
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
            "DME). GC, MGC, SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 "
            "schedules carry the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals "
            "& DME Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and "
            "EUA Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX."
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
            "DME). GC, MGC, SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 "
            "schedules carry the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals "
            "& DME Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and "
            "EUA Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX."
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
            "DME). GC, MGC, SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 "
            "schedules carry the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals "
            "& DME Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and "
            "EUA Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX."
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
            "DME). GC, MGC, SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 "
            "schedules carry the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals "
            "& DME Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and "
            "EUA Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX."
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
            "DME). GC, MGC, SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 "
            "schedules carry the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals "
            "& DME Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and "
            "EUA Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX."
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
            "DME). GC, MGC, SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 "
            "schedules carry the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals "
            "& DME Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and "
            "EUA Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX. CME filed the 2021 New Year schedule in its "
            "2020 zip."
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
            "'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). GC, MGC, "
            "SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 schedules carry "
            "the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals & DME "
            "Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and EUA "
            "Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX."
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
            "DME). GC, MGC, SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 "
            "schedules carry the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals "
            "& DME Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and "
            "EUA Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX."
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
            "DME). GC, MGC, SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 "
            "schedules carry the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals "
            "& DME Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and "
            "EUA Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX. Jobs-report Good Friday: equities and rates "
            "traded an abbreviated session (equity calendar); COMEX metals did not open."
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
            "DME). GC, MGC, SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 "
            "schedules carry the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals "
            "& DME Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and "
            "EUA Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX."
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
            "DME). GC, MGC, SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 "
            "schedules carry the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals "
            "& DME Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and "
            "EUA Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX."
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
            "DME). GC, MGC, SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 "
            "schedules carry the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals "
            "& DME Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and "
            "EUA Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX."
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
            "DME). GC, MGC, SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 "
            "schedules carry the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals "
            "& DME Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and "
            "EUA Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX."
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
            "DME). GC, MGC, SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 "
            "schedules carry the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals "
            "& DME Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and "
            "EUA Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX."
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
            "DME). GC, MGC, SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 "
            "schedules carry the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals "
            "& DME Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and "
            "EUA Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX."
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
            "'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). GC, MGC, "
            "SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 schedules carry "
            "the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals & DME "
            "Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and EUA "
            "Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX. First 13:30 CT metals holiday halt found "
            "(2019-2021: 12:00 CT)."
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
            "'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). GC, MGC, "
            "SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 schedules carry "
            "the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals & DME "
            "Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and EUA "
            "Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX."
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
            "'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). GC, MGC, "
            "SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 schedules carry "
            "the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals & DME "
            "Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and EUA "
            "Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX."
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
            "'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). GC, MGC, "
            "SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 schedules carry "
            "the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals & DME "
            "Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and EUA "
            "Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX."
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
            "'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). GC, MGC, "
            "SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 schedules carry "
            "the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals & DME "
            "Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and EUA "
            "Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX. Full schedule (no compact file captured). "
            "Column mapping as read by CalendarBuilder-Energy from the merged header cells (xlrd): "
            "Calendar Date 'Monday, June 20' spans columns 11-20; the row's 13:30 cells are "
            "columns 14 ('Halt') and 18, and 17:00 is column 19 ('Open')."
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
            "'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). GC, MGC, "
            "SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 schedules carry "
            "the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals & DME "
            "Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and EUA "
            "Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX."
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
            "'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). GC, MGC, "
            "SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 schedules carry "
            "the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals & DME "
            "Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and EUA "
            "Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX."
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
            "'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). GC, MGC, "
            "SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 schedules carry "
            "the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals & DME "
            "Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and EUA "
            "Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX."
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
            "'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). GC, MGC, "
            "SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 schedules carry "
            "the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals & DME "
            "Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and EUA "
            "Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX."
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
            "'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). GC, MGC, "
            "SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 schedules carry "
            "the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals & DME "
            "Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and EUA "
            "Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX. Full schedule, 'Updated 6/29/2022' (captured "
            "2022-07-04, before the holiday). Merged header cells (xlrd, as read by "
            "CalendarBuilder-Energy): 'Globex Closed' spans columns 9-18 under Calendar Date "
            "'Monday, December 26' (columns 9-24); pre-open 16:00 and open 17:00 follow on the "
            "Monday. CME's 2022 Christmas settlement notice agrees: 'Note: Monday December 26, "
            "2022 CME Group will not derive or disseminate settlement prices'."
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
            "'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). GC, MGC, "
            "SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 schedules carry "
            "the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals & DME "
            "Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and EUA "
            "Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX. Captured 2022-07-04, before the holiday (CME "
            "published it in advance)."
        ),
    ),
    date(2023, 1, 16): Citation(
        _HC + "mlk-day-holiday-settlement-times-2023.pdf",
        (
            "Note: Monday January 16, 2023 CME Group will not derive or disseminate settlement "
            "prices (other than the two LIBOR Settlements listed above) for CME, CBOT, NYMEX or "
            "COMEX"
        ),
        "https://www.cmegroup.com/files/presidents-day.pdf",
        (
            "PRODUCT NAME Cleared As SUNDAY, 19 FEB 2023 MONDAY, 20 FEB 2023 TUESDAY, 21 FEB 2023 "
            "... METALS 16:00 (PREOPEN) 13:30 (PREOPEN) HALT"
        ),
        note=(
            "Status cme: CME's MLK 2023 settlement notice (no COMEX settlement that day; a "
            "no-settlement note alone does not prove a closure, but no CME source retrieved closes "
            "COMEX metals on any MLK Day and every 2019-2022 and 2024-2026 MLK Day is a halt). "
            "Time inferred, not cme: no CME Globex schedule with a COMEX metals row was "
            "retrievable for MLK Day 2023 (no 2023 MLK summary PDF was archived under the names "
            "tried, the CME trading-hours service capture of 2024-07-08 has no events for "
            "2023-01-15..17, and the only CME MLK 2023 Globex schedule retrieved covers MGEX and "
            "DME). 13:30 CT is taken from CME's own METALS row five weeks later (Presidents Day "
            "2023, time_url) and from every COMEX metals holiday halt from 2022-01-17 to "
            "2026-05-25 (13:30 CT). Secondary corroboration, not machine-checkable: AMP Futures' "
            "image of CME's table 'CME Group Globex Dr. Martin Luther King, Jr. Holiday Schedule: "
            "13 - 17 January 2023' shows 'Metals' HALT '13:30 CST' on Monday Jan 16 and 'Regular @ "
            "17:00 CST' reopen (https://www.ampfutures.com/hubfs/CME%20Holiday%20Trading%20Schedu"
            "le%20-%20Dr.%20Martin%20Luther%20King%2c%20Jr.%20(2023).png, sha256 "
            "09e7f123df0f99e6..., cached by CalendarBuilder-Rates, read as an image by "
            "CalendarBuilder-Metals)."
        ),
    ),
    date(2023, 2, 20): Citation(
        "https://www.cmegroup.com/files/presidents-day.pdf",
        (
            "PRODUCT NAME Cleared As SUNDAY, 19 FEB 2023 MONDAY, 20 FEB 2023 TUESDAY, 21 FEB 2023 "
            "... METALS 16:00 (PREOPEN) 13:30 (PREOPEN) HALT"
        ),
        "https://www.cmegroup.com/files/presidents-day.pdf",
        "METALS 16:00 (PREOPEN) 13:30 (PREOPEN) HALT",
        note=(
            "CME holiday summary PDF: hours of 'the most actively traded instruments for each "
            "asset class', METALS row; text read with pdftotext -layout, so the METALS line "
            "carries the day columns left to right (a cell printed on the line above or below the "
            "row label belongs to the same row). cmegroup.com/files/presidents-day.pdf is the "
            "fixed name CME's trading-hours page linked for the Presidents Day holiday summary; "
            "this capture (2023-03-29) holds the 2023 version (19-21 FEB 2023)."
        ),
    ),
    date(2023, 4, 7): Citation(
        "https://www.cmegroup.com/files/good-friday.pdf",
        (
            "PRODUCT NAME THURSDAY, 6 APR 2023 FRIDAY, 7 APR 2023 ... TRADE DATE: THURS 6 APR "
            "METALS 16:00 ( CLOSED)"
        ),
        note=(
            "CME holiday summary PDF: hours of 'the most actively traded instruments for each "
            "asset class', METALS row; text read with pdftotext -layout, so the METALS line "
            "carries the day columns left to right (a cell printed on the line above or below the "
            "row label belongs to the same row). The 2024-07-08 capture of the fixed name "
            "cmegroup.com/files/good-friday.pdf still holds the 2023 version (6-7 APR 2023). The "
            "METALS row has only Thursday's 16:00 close and no Friday event, while INTEREST RATE, "
            "EQUITIES and FX carry Friday sessions (jobs-report Good Friday). CME's 2023 Good "
            "Friday settlement notice: COMEX products 'will have their settlements copied from "
            "April 6th to April 7th'."
        ),
    ),
    date(2023, 5, 29): Citation(
        _TH + "memorial-day-2023.pdf",
        (
            "PRODUCT NAME SUNDAY, 28 MAY 2023 MONDAY, 29 MAY 2023 TUESDAY, 30 MAY 2023 ... METALS "
            "16:00 (PREOPEN) 13:30 (PREOPEN) HALT"
        ),
        _TH + "memorial-day-2023.pdf",
        "METALS 16:00 (PREOPEN) 13:30 (PREOPEN) HALT",
        note=(
            "CME holiday summary PDF: hours of 'the most actively traded instruments for each "
            "asset class', METALS row; text read with pdftotext -layout, so the METALS line "
            "carries the day columns left to right (a cell printed on the line above or below the "
            "row label belongs to the same row)."
        ),
    ),
    date(2023, 6, 19): Citation(
        _TH + "juneteenth-2023.pdf",
        (
            "PRODUCT NAME SUNDAY, 18 JUNE 2023 MONDAY, 19 JUNE 2023 TUESDAY, 20 JUNE 2023 ... "
            "METALS 16:00 (PREOPEN) 13:30 (PREOPEN) HALT"
        ),
        _TH + "juneteenth-2023.pdf",
        "METALS 16:00 (PREOPEN) 13:30 (PREOPEN) HALT",
        note=(
            "CME holiday summary PDF: hours of 'the most actively traded instruments for each "
            "asset class', METALS row; text read with pdftotext -layout, so the METALS line "
            "carries the day columns left to right (a cell printed on the line above or below the "
            "row label belongs to the same row)."
        ),
    ),
    date(2023, 7, 4): Citation(
        _TH + "4th-of-july-2023.pdf",
        (
            "PRODUCT NAME MONDAY, 3 JULY 2023 TUESDAY, 4 JULY 2023 WEDNESDAY, 5 JULY 2023 ... "
            "METALS TRADE DATE: WED 5 JULY 13:30 (PREOPEN) HALT"
        ),
        _TH + "4th-of-july-2023.pdf",
        "METALS TRADE DATE: WED 5 JULY 13:30 (PREOPEN) HALT",
        note=(
            "CME holiday summary PDF: hours of 'the most actively traded instruments for each "
            "asset class', METALS row; text read with pdftotext -layout, so the METALS line "
            "carries the day columns left to right (a cell printed on the line above or below the "
            "row label belongs to the same row)."
        ),
    ),
    date(2023, 9, 4): Citation(
        _TH + "labor-day-2023.pdf",
        (
            "PRODUCT NAME SUNDAY, 3 SEPTEMBER 2023 MONDAY, 4 SEPTEMBER 2023 TUESDAY, 5 SEPTEMBER "
            "2023 ... METALS 16:00 (PREOPEN) 13:30 (PREOPEN) HALT"
        ),
        _svc("2023-09-03", "2023-09-05", "1720455278654"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2023-09-04","events":[{"tradingDate":"2023-09-05","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2023-09-05","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        note=(
            "CME holiday summary PDF: hours of 'the most actively traded instruments for each "
            "asset class', METALS row; text read with pdftotext -layout, so the METALS line "
            "carries the day columns left to right (a cell printed on the line above or below the "
            "row label belongs to the same row). CME's trading-hours-by-product service behind "
            "cmegroup.com/trading-hours.html, product 437 'Gold Futures' (GC), Wayback capture "
            "20240708161439. GC stands for the group: CME's holiday schedules give COMEX metals "
            "hours per asset class (row METALS), and the service's only metals product is GC (no "
            "SI or HG record was captured). 'preopen' at a time = trading halts (order entry only) "
            "until the next 'open'; 'closed' = final close of the trade date."
        ),
    ),
    date(2023, 11, 23): Citation(
        _TH + "thanksgiving-day-2023.pdf",
        (
            "PRODUCT NAME WEDNESDAY, 22 NOVEMBER 2023 THURSDAY, 23 NOVEMBER 2023 FRIDAY, 24 "
            "NOVEMBER 2023 ... METALS TRADE DATE: FRI 24 NOV 13:30 (PREOPEN) HALT 12:45 (CLOSED)"
        ),
        _svc("2023-11-22", "2023-11-24", "1720455278656"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2023-11-23","events":[{"tradingDate":"2023-11-24","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2023-11-24","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        note=(
            "CME holiday summary PDF: hours of 'the most actively traded instruments for each "
            "asset class', METALS row; text read with pdftotext -layout, so the METALS line "
            "carries the day columns left to right (a cell printed on the line above or below the "
            "row label belongs to the same row). CME's trading-hours-by-product service behind "
            "cmegroup.com/trading-hours.html, product 437 'Gold Futures' (GC), Wayback capture "
            "20240708161439. GC stands for the group: CME's holiday schedules give COMEX metals "
            "hours per asset class (row METALS), and the service's only metals product is GC (no "
            "SI or HG record was captured). 'preopen' at a time = trading halts (order entry only) "
            "until the next 'open'; 'closed' = final close of the trade date."
        ),
    ),
    date(2023, 11, 24): Citation(
        _TH + "thanksgiving-day-2023.pdf",
        (
            "PRODUCT NAME WEDNESDAY, 22 NOVEMBER 2023 THURSDAY, 23 NOVEMBER 2023 FRIDAY, 24 "
            "NOVEMBER 2023 ... METALS TRADE DATE: FRI 24 NOV 13:30 (PREOPEN) HALT 12:45 (CLOSED)"
        ),
        _svc("2023-11-22", "2023-11-24", "1720455278656"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2023-11-24","events":[{"tradingDate":"2023-11-24","eventTime":"12:45","ma'
            'rketEventType":"closed"}]}'
        ),
        note=(
            "CME holiday summary PDF: hours of 'the most actively traded instruments for each "
            "asset class', METALS row; text read with pdftotext -layout, so the METALS line "
            "carries the day columns left to right (a cell printed on the line above or below the "
            "row label belongs to the same row). CME's trading-hours-by-product service behind "
            "cmegroup.com/trading-hours.html, product 437 'Gold Futures' (GC), Wayback capture "
            "20240708161439. GC stands for the group: CME's holiday schedules give COMEX metals "
            "hours per asset class (row METALS), and the service's only metals product is GC (no "
            "SI or HG record was captured). 'preopen' at a time = trading halts (order entry only) "
            "until the next 'open'; 'closed' = final close of the trade date. CME's 2023 "
            "Thanksgiving settlement notice moves metals settlement one hour early on Friday "
            "November 24 ('Gold 12:30:00 ET', 'Silver 12:25:00 ET', 'Copper 12:00:00 ET')."
        ),
    ),
    date(2023, 12, 25): Citation(
        _svc("2023-12-24", "2023-12-26", "1720455278659"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... '
            '{"groupCode":"GC","eventDate":"2023-12-24","events":[]} ... {"groupCode":"GC","event'
            'Date":"2023-12-25","events":[{"tradingDate":"2023-12-26","eventTime":"16:00","marketEv'
            'entType":"preopen"},{"tradingDate":"2023-12-26","eventTime":"17:00","marketEventType":'
            '"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 437 'Gold Futures' (GC), Wayback capture 20240708161439. GC stands for the "
            "group: CME's holiday schedules give COMEX metals hours per asset class (row METALS), "
            "and the service's only metals product is GC (no SI or HG record was captured). "
            "'preopen' at a time = trading halts (order entry only) until the next 'open'; "
            "'closed' = final close of the trade date. No event on Sunday 12-24 (no 17:00 CT "
            "reopen) and only the 16:00 pre-open and 17:00 open for trade date 12-26 on Monday "
            "12-25. CME's summary PDF christmas-day-2023.pdf (METALS row, Monday 25 December: "
            "16:00 PREOPEN, 17:00 OPEN) and its settlement notice ('Note: Monday December 25, 2023 "
            "CME Group will not derive or disseminate settlement prices') agree."
        ),
    ),
    date(2024, 1, 1): Citation(
        _svc("2023-12-31", "2024-01-02", "1720455278661"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... '
            '{"groupCode":"GC","eventDate":"2023-12-31","events":[]} ... {"groupCode":"GC","event'
            'Date":"2024-01-01","events":[{"tradingDate":"2024-01-02","eventTime":"16:00","marketEv'
            'entType":"preopen"},{"tradingDate":"2024-01-02","eventTime":"17:00","marketEventType":'
            '"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 437 'Gold Futures' (GC), Wayback capture 20240708161439. GC stands for the "
            "group: CME's holiday schedules give COMEX metals hours per asset class (row METALS), "
            "and the service's only metals product is GC (no SI or HG record was captured). "
            "'preopen' at a time = trading halts (order entry only) until the next 'open'; "
            "'closed' = final close of the trade date. No event on Sunday 12-31 and only the 16:00 "
            "pre-open and 17:00 open on Monday 01-01. CME's summary PDF new-years-day-2024.pdf "
            "(METALS row) agrees."
        ),
    ),
    date(2024, 1, 15): Citation(
        _svc("2024-01-14", "2024-01-16", "1720455278663"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2024-01-15","events":[{"tradingDate":"2024-01-16","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2024-01-16","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        _svc("2024-01-14", "2024-01-16", "1720455278663"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2024-01-15","events":[{"tradingDate":"2024-01-16","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2024-01-16","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 437 'Gold Futures' (GC), Wayback capture 20240708161439. GC stands for the "
            "group: CME's holiday schedules give COMEX metals hours per asset class (row METALS), "
            "and the service's only metals product is GC (no SI or HG record was captured). "
            "'preopen' at a time = trading halts (order entry only) until the next 'open'; "
            "'closed' = final close of the trade date."
        ),
    ),
    date(2024, 2, 19): Citation(
        _svc("2024-02-18", "2024-02-20", "1720455278669"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2024-02-19","events":[{"tradingDate":"2024-02-20","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2024-02-20","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        _svc("2024-02-18", "2024-02-20", "1720455278669"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2024-02-19","events":[{"tradingDate":"2024-02-20","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2024-02-20","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 437 'Gold Futures' (GC), Wayback capture 20240708161439. GC stands for the "
            "group: CME's holiday schedules give COMEX metals hours per asset class (row METALS), "
            "and the service's only metals product is GC (no SI or HG record was captured). "
            "'preopen' at a time = trading halts (order entry only) until the next 'open'; "
            "'closed' = final close of the trade date."
        ),
    ),
    date(2024, 3, 29): Citation(
        _svc("2024-03-28", "2024-03-30", "1720455278672"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2024-03-28","events":[{"tradingDate":"2024-03-28","eventTime":"16:00","ma'
            'rketEventType":"closed"}]} ... {"groupCode":"GC","eventDate":"2024-03-29","events":[]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 437 'Gold Futures' (GC), Wayback capture 20240708161439. GC stands for the "
            "group: CME's holiday schedules give COMEX metals hours per asset class (row METALS), "
            "and the service's only metals product is GC (no SI or HG record was captured). "
            "'preopen' at a time = trading halts (order entry only) until the next 'open'; "
            "'closed' = final close of the trade date. Thursday 03-28 16:00 close with no reopen; "
            "no event on Friday 03-29."
        ),
    ),
    date(2024, 5, 27): Citation(
        _svc("2024-05-26", "2024-05-28", "1720455278675"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2024-05-27","events":[{"tradingDate":"2024-05-28","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2024-05-28","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        _svc("2024-05-26", "2024-05-28", "1720455278675"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2024-05-27","events":[{"tradingDate":"2024-05-28","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2024-05-28","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 437 'Gold Futures' (GC), Wayback capture 20240708161439. GC stands for the "
            "group: CME's holiday schedules give COMEX metals hours per asset class (row METALS), "
            "and the service's only metals product is GC (no SI or HG record was captured). "
            "'preopen' at a time = trading halts (order entry only) until the next 'open'; "
            "'closed' = final close of the trade date."
        ),
    ),
    date(2024, 6, 19): Citation(
        _svc("2024-06-18", "2024-06-20", "1720455278677"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2024-06-19","events":[{"tradingDate":"2024-06-20","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2024-06-20","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        _svc("2024-06-18", "2024-06-20", "1720455278677"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2024-06-19","events":[{"tradingDate":"2024-06-20","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2024-06-20","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 437 'Gold Futures' (GC), Wayback capture 20240708161439. GC stands for the "
            "group: CME's holiday schedules give COMEX metals hours per asset class (row METALS), "
            "and the service's only metals product is GC (no SI or HG record was captured). "
            "'preopen' at a time = trading halts (order entry only) until the next 'open'; "
            "'closed' = final close of the trade date."
        ),
    ),
    date(2024, 7, 4): Citation(
        _svc("2024-07-03", "2024-07-05", "1720455278680"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2024-07-04","events":[{"tradingDate":"2024-07-05","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2024-07-05","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        _svc("2024-07-03", "2024-07-05", "1720455278680"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2024-07-04","events":[{"tradingDate":"2024-07-05","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2024-07-05","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 437 'Gold Futures' (GC), Wayback capture 20240708161439. GC stands for the "
            "group: CME's holiday schedules give COMEX metals hours per asset class (row METALS), "
            "and the service's only metals product is GC (no SI or HG record was captured). "
            "'preopen' at a time = trading halts (order entry only) until the next 'open'; "
            "'closed' = final close of the trade date."
        ),
    ),
    date(2024, 9, 2): Citation(
        _svc("2024-09-01", "2024-09-03", "1734710019534"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2024-09-02","events":[{"tradingDate":"2024-09-03","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2024-09-03","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        _svc("2024-09-01", "2024-09-03", "1734710019534"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2024-09-02","events":[{"tradingDate":"2024-09-03","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2024-09-03","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 437 'Gold Futures' (GC), Wayback capture 20241220155340. GC stands for the "
            "group: CME's holiday schedules give COMEX metals hours per asset class (row METALS), "
            "and the service's only metals product is GC (no SI or HG record was captured). "
            "'preopen' at a time = trading halts (order entry only) until the next 'open'; "
            "'closed' = final close of the trade date."
        ),
    ),
    date(2024, 11, 28): Citation(
        _svc("2024-11-27", "2024-11-29", "1734710019535"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2024-11-28","events":[{"tradingDate":"2024-11-29","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2024-11-29","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        _svc("2024-11-27", "2024-11-29", "1734710019535"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2024-11-28","events":[{"tradingDate":"2024-11-29","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2024-11-29","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 437 'Gold Futures' (GC), Wayback capture 20241220155340. GC stands for the "
            "group: CME's holiday schedules give COMEX metals hours per asset class (row METALS), "
            "and the service's only metals product is GC (no SI or HG record was captured). "
            "'preopen' at a time = trading halts (order entry only) until the next 'open'; "
            "'closed' = final close of the trade date."
        ),
    ),
    date(2024, 11, 29): Citation(
        _svc("2024-11-27", "2024-11-29", "1734710019535"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2024-11-29","events":[{"tradingDate":"2024-11-29","eventTime":"13:45","ma'
            'rketEventType":"closed"}]}'
        ),
        _svc("2024-11-27", "2024-11-29", "1734710019535"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2024-11-29","events":[{"tradingDate":"2024-11-29","eventTime":"13:45","ma'
            'rketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 437 'Gold Futures' (GC), Wayback capture 20241220155340. GC stands for the "
            "group: CME's holiday schedules give COMEX metals hours per asset class (row METALS), "
            "and the service's only metals product is GC (no SI or HG record was captured). "
            "'preopen' at a time = trading halts (order entry only) until the next 'open'; "
            "'closed' = final close of the trade date. From 2024 the day-after-Thanksgiving close "
            "is 13:45 CT (2019-2023: 12:45 CT). CME's 2024 Thanksgiving settlement notice as "
            "captured 2023-12-09 (before the day) still listed early metals settlement times "
            "('Gold 12:30:00 ET'); the 2025 notice gives metals a 'Normal Settlement Schedule' on "
            "the Friday. The Globex close is unaffected."
        ),
    ),
    date(2024, 12, 24): Citation(
        _svc("2024-12-24", "2024-12-26", "1734710019537"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2024-12-24","events":[{"tradingDate":"2024-12-24","eventTime":"12:45","ma'
            'rketEventType":"closed"}]}'
        ),
        _svc("2024-12-24", "2024-12-26", "1734710019537"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2024-12-24","events":[{"tradingDate":"2024-12-24","eventTime":"12:45","ma'
            'rketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 437 'Gold Futures' (GC), Wayback capture 20241220155340. GC stands for the "
            "group: CME's holiday schedules give COMEX metals hours per asset class (row METALS), "
            "and the service's only metals product is GC (no SI or HG record was captured). "
            "'preopen' at a time = trading halts (order entry only) until the next 'open'; "
            "'closed' = final close of the trade date."
        ),
    ),
    date(2024, 12, 25): Citation(
        _svc("2024-12-24", "2024-12-26", "1734710019537"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2024-12-24","events":[{"tradingDate":"2024-12-24","eventTime":"12:45","ma'
            'rketEventType":"closed"}]} ... {"groupCode":"GC","eventDate":"2024-12-25","events":['
            '{"tradingDate":"2024-12-26","eventTime":"16:00","marketEventType":"preopen"},{"trading'
            'Date":"2024-12-26","eventTime":"17:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 437 'Gold Futures' (GC), Wayback capture 20241220155340. GC stands for the "
            "group: CME's holiday schedules give COMEX metals hours per asset class (row METALS), "
            "and the service's only metals product is GC (no SI or HG record was captured). "
            "'preopen' at a time = trading halts (order entry only) until the next 'open'; "
            "'closed' = final close of the trade date. Tuesday 12-24 closes at 12:45 with no "
            "reopen that evening; Wednesday 12-25 carries only the 16:00 pre-open and 17:00 open "
            "for trade date 12-26."
        ),
    ),
    date(2025, 1, 1): Citation(
        _svc("2024-12-31", "2025-01-02", "1734710019538"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2024-12-31","events":[{"tradingDate":"2024-12-31","eventTime":"16:00","ma'
            'rketEventType":"closed"}]} ... {"groupCode":"GC","eventDate":"2025-01-01","events":['
            '{"tradingDate":"2025-01-02","eventTime":"16:00","marketEventType":"preopen"},{"trading'
            'Date":"2025-01-02","eventTime":"17:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 437 'Gold Futures' (GC), Wayback capture 20241220155340. GC stands for the "
            "group: CME's holiday schedules give COMEX metals hours per asset class (row METALS), "
            "and the service's only metals product is GC (no SI or HG record was captured). "
            "'preopen' at a time = trading halts (order entry only) until the next 'open'; "
            "'closed' = final close of the trade date."
        ),
    ),
    date(2025, 1, 20): Citation(
        _svc("2025-01-19", "2025-01-21", "1734710019539"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2025-01-20","events":[{"tradingDate":"2025-01-21","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2025-01-21","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        _svc("2025-01-19", "2025-01-21", "1734710019539"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2025-01-20","events":[{"tradingDate":"2025-01-21","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2025-01-21","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 437 'Gold Futures' (GC), Wayback capture 20241220155340. GC stands for the "
            "group: CME's holiday schedules give COMEX metals hours per asset class (row METALS), "
            "and the service's only metals product is GC (no SI or HG record was captured). "
            "'preopen' at a time = trading halts (order entry only) until the next 'open'; "
            "'closed' = final close of the trade date."
        ),
    ),
    date(2025, 2, 17): Citation(
        _svc("2025-02-16", "2025-02-18", "1734710019540"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2025-02-17","events":[{"tradingDate":"2025-02-18","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2025-02-18","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        _svc("2025-02-16", "2025-02-18", "1734710019540"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2025-02-17","events":[{"tradingDate":"2025-02-18","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2025-02-18","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 437 'Gold Futures' (GC), Wayback capture 20241220155340. GC stands for the "
            "group: CME's holiday schedules give COMEX metals hours per asset class (row METALS), "
            "and the service's only metals product is GC (no SI or HG record was captured). "
            "'preopen' at a time = trading halts (order entry only) until the next 'open'; "
            "'closed' = final close of the trade date."
        ),
    ),
    date(2025, 4, 18): Citation(
        _svc("2025-04-17", "2025-04-19", "1734710019542"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2025-04-17","events":[{"tradingDate":"2025-04-17","eventTime":"16:00","ma'
            'rketEventType":"closed"}]} ... {"groupCode":"GC","eventDate":"2025-04-18","events":[]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 437 'Gold Futures' (GC), Wayback capture 20241220155340. GC stands for the "
            "group: CME's holiday schedules give COMEX metals hours per asset class (row METALS), "
            "and the service's only metals product is GC (no SI or HG record was captured). "
            "'preopen' at a time = trading halts (order entry only) until the next 'open'; "
            "'closed' = final close of the trade date."
        ),
    ),
    date(2025, 5, 26): Citation(
        _svc("2025-05-25", "2025-05-27", "1734710019543"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2025-05-26","events":[{"tradingDate":"2025-05-27","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2025-05-27","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        _svc("2025-05-25", "2025-05-27", "1734710019543"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2025-05-26","events":[{"tradingDate":"2025-05-27","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2025-05-27","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 437 'Gold Futures' (GC), Wayback capture 20241220155340. GC stands for the "
            "group: CME's holiday schedules give COMEX metals hours per asset class (row METALS), "
            "and the service's only metals product is GC (no SI or HG record was captured). "
            "'preopen' at a time = trading halts (order entry only) until the next 'open'; "
            "'closed' = final close of the trade date."
        ),
    ),
    date(2025, 6, 19): Citation(
        _svc("2025-06-18", "2025-06-20", "1734710019544"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2025-06-19","events":[{"tradingDate":"2025-06-20","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2025-06-20","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        _svc("2025-06-18", "2025-06-20", "1734710019544"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2025-06-19","events":[{"tradingDate":"2025-06-20","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2025-06-20","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 437 'Gold Futures' (GC), Wayback capture 20241220155340. GC stands for the "
            "group: CME's holiday schedules give COMEX metals hours per asset class (row METALS), "
            "and the service's only metals product is GC (no SI or HG record was captured). "
            "'preopen' at a time = trading halts (order entry only) until the next 'open'; "
            "'closed' = final close of the trade date."
        ),
    ),
    date(2025, 7, 4): Citation(
        _svc("2025-07-03", "2025-07-05", "1734710019545"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2025-07-03","events":[{"tradingDate":"2025-07-03","eventTime":"16:00","ma'
            'rketEventType":"closed"},{"tradingDate":"2025-07-04","eventTime":"16:45","marketEventT'
            'ype":"preopen"},{"tradingDate":"2025-07-04","eventTime":"17:00","marketEventType":"ope'
            'n"}]} ... {"groupCode":"GC","eventDate":"2025-07-04","events":[{"tradingDate":"2025-'
            '07-04","eventTime":"12:00","marketEventType":"closed"}]}'
        ),
        _svc("2025-07-03", "2025-07-05", "1734710019545"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2025-07-03","events":[{"tradingDate":"2025-07-03","eventTime":"16:00","ma'
            'rketEventType":"closed"},{"tradingDate":"2025-07-04","eventTime":"16:45","marketEventT'
            'ype":"preopen"},{"tradingDate":"2025-07-04","eventTime":"17:00","marketEventType":"ope'
            'n"}]} ... {"groupCode":"GC","eventDate":"2025-07-04","events":[{"tradingDate":"2025-'
            '07-04","eventTime":"12:00","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 437 'Gold Futures' (GC), Wayback capture 20241220155340. GC stands for the "
            "group: CME's holiday schedules give COMEX metals hours per asset class (row METALS), "
            "and the service's only metals product is GC (no SI or HG record was captured). "
            "'preopen' at a time = trading halts (order entry only) until the next 'open'; "
            "'closed' = final close of the trade date. Friday holiday: the Thursday 17:00 CT open "
            "is for trade date 07-04 and the Friday session ends with a 12:00 'closed'; the next "
            "open is Sunday 17:00 CT."
        ),
    ),
    date(2025, 9, 1): Citation(
        _svc("2025-08-31", "2025-09-02", "1734710019546"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2025-09-01","events":[{"tradingDate":"2025-09-02","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2025-09-02","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        _svc("2025-08-31", "2025-09-02", "1734710019546"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2025-09-01","events":[{"tradingDate":"2025-09-02","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2025-09-02","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 437 'Gold Futures' (GC), Wayback capture 20241220155340. GC stands for the "
            "group: CME's holiday schedules give COMEX metals hours per asset class (row METALS), "
            "and the service's only metals product is GC (no SI or HG record was captured). "
            "'preopen' at a time = trading halts (order entry only) until the next 'open'; "
            "'closed' = final close of the trade date."
        ),
    ),
    date(2025, 11, 27): Citation(
        _svc("2025-11-26", "2025-11-28", "1769649703060"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2025-11-27","events":[{"tradingDate":"2025-11-28","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        _svc("2025-11-26", "2025-11-28", "1769649703060"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2025-11-27","events":[{"tradingDate":"2025-11-28","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 437 'Gold Futures' (GC), Wayback capture 20260129012143. GC stands for the "
            "group: CME's holiday schedules give COMEX metals hours per asset class (row METALS), "
            "and the service's only metals product is GC (no SI or HG record was captured). "
            "'preopen' at a time = trading halts (order entry only) until the next 'open'; "
            "'closed' = final close of the trade date."
        ),
    ),
    date(2025, 11, 28): Citation(
        _svc("2025-11-26", "2025-11-28", "1769649703060"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28","eventTime":"07:00","ma'
            'rketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"07:30","marketEvent'
            'Type":"open"},{"tradingDate":"2025-11-28","eventTime":"13:45","marketEventType":"close'
            'd"}]}'
        ),
        _svc("2025-11-26", "2025-11-28", "1769649703060"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28","eventTime":"07:00","ma'
            'rketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"07:30","marketEvent'
            'Type":"open"},{"tradingDate":"2025-11-28","eventTime":"13:45","marketEventType":"close'
            'd"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 437 'Gold Futures' (GC), Wayback capture 20260129012143. GC stands for the "
            "group: CME's holiday schedules give COMEX metals hours per asset class (row METALS), "
            "and the service's only metals product is GC (no SI or HG record was captured). "
            "'preopen' at a time = trading halts (order entry only) until the next 'open'; "
            "'closed' = final close of the trade date. The 2026-01-29 capture also records the "
            "unscheduled late open of 2025-11-28 (07:00 pre-open, 07:30 open) before the scheduled "
            "13:45 close: LATE_OPENS. The 2024-12-20 capture (the plan) has only the 13:45 close. "
            "CME's 2025 Thanksgiving settlement notice: 'Metal Products Settlement Times: Normal "
            "Settlement Schedule' that Friday."
        ),
    ),
    date(2025, 12, 24): Citation(
        _svc("2025-12-24", "2025-12-26", "1769649703064"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2025-12-24","events":[{"tradingDate":"2025-12-24","eventTime":"12:45","ma'
            'rketEventType":"closed"}]}'
        ),
        _svc("2025-12-24", "2025-12-26", "1769649703064"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2025-12-24","events":[{"tradingDate":"2025-12-24","eventTime":"12:45","ma'
            'rketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 437 'Gold Futures' (GC), Wayback capture 20260129012143. GC stands for the "
            "group: CME's holiday schedules give COMEX metals hours per asset class (row METALS), "
            "and the service's only metals product is GC (no SI or HG record was captured). "
            "'preopen' at a time = trading halts (order entry only) until the next 'open'; "
            "'closed' = final close of the trade date."
        ),
    ),
    date(2025, 12, 25): Citation(
        _svc("2025-12-24", "2025-12-26", "1769649703064"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2025-12-24","events":[{"tradingDate":"2025-12-24","eventTime":"12:45","ma'
            'rketEventType":"closed"}]} ... {"groupCode":"GC","eventDate":"2025-12-25","events":['
            '{"tradingDate":"2025-12-26","eventTime":"16:00","marketEventType":"preopen"},{"trading'
            'Date":"2025-12-26","eventTime":"17:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 437 'Gold Futures' (GC), Wayback capture 20260129012143. GC stands for the "
            "group: CME's holiday schedules give COMEX metals hours per asset class (row METALS), "
            "and the service's only metals product is GC (no SI or HG record was captured). "
            "'preopen' at a time = trading halts (order entry only) until the next 'open'; "
            "'closed' = final close of the trade date."
        ),
    ),
    date(2026, 1, 1): Citation(
        _svc("2025-12-31", "2026-01-02", "1769649703066"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2025-12-31","events":[{"tradingDate":"2025-12-31","eventTime":"16:00","ma'
            'rketEventType":"closed"}]} ... {"groupCode":"GC","eventDate":"2026-01-01","events":['
            '{"tradingDate":"2026-01-02","eventTime":"16:00","marketEventType":"preopen"},{"trading'
            'Date":"2026-01-02","eventTime":"17:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 437 'Gold Futures' (GC), Wayback capture 20260129012143. GC stands for the "
            "group: CME's holiday schedules give COMEX metals hours per asset class (row METALS), "
            "and the service's only metals product is GC (no SI or HG record was captured). "
            "'preopen' at a time = trading halts (order entry only) until the next 'open'; "
            "'closed' = final close of the trade date."
        ),
    ),
    date(2026, 1, 19): Citation(
        _svc("2026-01-18", "2026-01-20", "1769649703068"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2026-01-19","events":[{"tradingDate":"2026-01-20","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2026-01-20","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        _svc("2026-01-18", "2026-01-20", "1769649703068"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2026-01-19","events":[{"tradingDate":"2026-01-20","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2026-01-20","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 437 'Gold Futures' (GC), Wayback capture 20260129012143. GC stands for the "
            "group: CME's holiday schedules give COMEX metals hours per asset class (row METALS), "
            "and the service's only metals product is GC (no SI or HG record was captured). "
            "'preopen' at a time = trading halts (order entry only) until the next 'open'; "
            "'closed' = final close of the trade date."
        ),
    ),
    date(2026, 2, 16): Citation(
        _svc("2026-02-15", "2026-02-17", "1743113432015"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2026-02-16","events":[{"tradingDate":"2026-02-17","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2026-02-17","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        _svc("2026-02-15", "2026-02-17", "1743113432015"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2026-02-16","events":[{"tradingDate":"2026-02-17","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2026-02-17","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 437 'Gold Futures' (GC), Wayback capture 20260610104510. GC stands for the "
            "group: CME's holiday schedules give COMEX metals hours per asset class (row METALS), "
            "and the service's only metals product is GC (no SI or HG record was captured). "
            "'preopen' at a time = trading halts (order entry only) until the next 'open'; "
            "'closed' = final close of the trade date."
        ),
    ),
    date(2026, 4, 3): Citation(
        _svc("2026-04-01", "2026-04-03", "1743113432016"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2026-04-02","events":[{"tradingDate":"2026-04-02","eventTime":"16:00","ma'
            'rketEventType":"closed"}]} ... {"groupCode":"GC","eventDate":"2026-04-03","events":[]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 437 'Gold Futures' (GC), Wayback capture 20260610104510. GC stands for the "
            "group: CME's holiday schedules give COMEX metals hours per asset class (row METALS), "
            "and the service's only metals product is GC (no SI or HG record was captured). "
            "'preopen' at a time = trading halts (order entry only) until the next 'open'; "
            "'closed' = final close of the trade date. Thursday 04-02 16:00 close with no reopen; "
            "no event on Friday 04-03 (a jobs-report Good Friday on which equities traded an "
            "abbreviated session; COMEX metals stayed closed)."
        ),
    ),
    date(2026, 5, 25): Citation(
        _svc("2026-05-24", "2026-05-26", "1749141516014"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2026-05-25","events":[{"tradingDate":"2026-05-26","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2026-05-26","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        _svc("2026-05-24", "2026-05-26", "1749141516014"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2026-05-25","events":[{"tradingDate":"2026-05-26","eventTime":"13:30","ma'
            'rketEventType":"preopen"},{"tradingDate":"2026-05-26","eventTime":"17:00","marketEvent'
            'Type":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 437 'Gold Futures' (GC), Wayback capture 20260619114105. GC stands for the "
            "group: CME's holiday schedules give COMEX metals hours per asset class (row METALS), "
            "and the service's only metals product is GC (no SI or HG record was captured). "
            "'preopen' at a time = trading halts (order entry only) until the next 'open'; "
            "'closed' = final close of the trade date."
        ),
    ),
    date(2026, 6, 19): Citation(
        _svc("2026-06-18", "2026-06-20", "1784720540600"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2026-06-18","events":[{"tradingDate":"2026-06-18","eventTime":"16:00","ma'
            'rketEventType":"closed"},{"tradingDate":"2026-06-22","eventTime":"16:45","marketEventT'
            'ype":"preopen"},{"tradingDate":"2026-06-22","eventTime":"17:00","marketEventType":"ope'
            'n"}]} ... {"groupCode":"GC","eventDate":"2026-06-19","events":[{"tradingDate":"2026-'
            '06-22","eventTime":"12:00","marketEventType":"closed"}]}'
        ),
        _svc("2026-06-18", "2026-06-20", "1784720540600"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2026-06-18","events":[{"tradingDate":"2026-06-18","eventTime":"16:00","ma'
            'rketEventType":"closed"},{"tradingDate":"2026-06-22","eventTime":"16:45","marketEventT'
            'ype":"preopen"},{"tradingDate":"2026-06-22","eventTime":"17:00","marketEventType":"ope'
            'n"}]} ... {"groupCode":"GC","eventDate":"2026-06-19","events":[{"tradingDate":"2026-'
            '06-22","eventTime":"12:00","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 437 'Gold Futures' (GC), Wayback capture 20260722114220. GC stands for the "
            "group: CME's holiday schedules give COMEX metals hours per asset class (row METALS), "
            "and the service's only metals product is GC (no SI or HG record was captured). "
            "'preopen' at a time = trading halts (order entry only) until the next 'open'; "
            "'closed' = final close of the trade date. Friday holiday: the Thursday 17:00 CT open "
            "is booked to trade date 06-22 and the Friday session ends with a 12:00 'closed' "
            "(trade date 06-22); the next open is Sunday 17:00 CT. This module keeps 06-19 as its "
            "own short trade date (module convention). The capture also shows Saturday 06-20 "
            "events ('05:00 open', '17:00 closed', trade date 06-22) for GC, CL and ES alike; "
            "06-20 is outside the coverage and is not an entry."
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
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28","eventTime":"07:00","ma'
            'rketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"07:30","marketEvent'
            'Type":"open"},{"tradingDate":"2025-11-28","eventTime":"13:45","marketEventType":"close'
            'd"}]}'
        ),
        note=(
            "Unscheduled. Status: CME Group's 2025 Form 10-K (SEC EDGAR, read from the Wayback "
            "capture cached by CalendarBuilder-Energy; sec.gov refused the direct fetch). Open "
            "time: CME's GC service record for eventDate 2025-11-28 in the 2026-01-29 capture adds "
            "'07:00 preopen' and '07:30 open' before the scheduled 13:45 close; the 2024-12-20 "
            "capture (the plan) has only the 13:45 close. The time trading stopped on the evening "
            "of 2025-11-27 is in no CME document retrieved (halt_from_ct None). The outage hit "
            "every CME Globex group; data/cme_calendar.py does not record it."
        ),
    ),
}

# CME-stated regular metals days near holidays, kept so the absence of an entry is a recorded
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
            "metals and DME). GC, MGC, SI, SIL, HG and MHG are not named individually. CME's full "
            "2019-2022 schedules carry the row 'Energy, Metals, Softs & DME Products' (2022: "
            "'Energy, Metals & DME Products') whose only exception rows are DME Oman Crude TAM, "
            "Singapore TAM and EUA Daily Futures; their only COMEX metals notes concern TAS (for "
            "example 'Gold TAS – Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full "
            "sheets belongs to Bursa Malaysia Derivatives, not COMEX. Wednesday July 3 CLOSE "
            "'Regular @ 1600 CT' (equities closed early at 12:15 CT that day)."
        ),
    ),
    date(2019, 10, 14): Citation(
        _HC + "2019-columbus-day-holiday-settlement-times.pdf",
        "All products will settle at their normal times for the Columbus Day Holiday",
        note=(
            "Columbus Day: normal. Settlement notice; Columbus Day and Veterans Day are "
            "bond-market holidays that do not change COMEX metals hours in any schedule read."
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
            "metals and DME). GC, MGC, SI, SIL, HG and MHG are not named individually. CME's full "
            "2019-2022 schedules carry the row 'Energy, Metals, Softs & DME Products' (2022: "
            "'Energy, Metals & DME Products') whose only exception rows are DME Oman Crude TAM, "
            "Singapore TAM and EUA Daily Futures; their only COMEX metals notes concern TAS (for "
            "example 'Gold TAS – Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full "
            "sheets belongs to Bursa Malaysia Derivatives, not COMEX. Tuesday Dec 31 CLOSE "
            "'Regular @ 1600 CT'."
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
            "'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). GC, MGC, "
            "SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 schedules carry "
            "the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals & DME "
            "Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and EUA "
            "Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX. Thursday July 2 CLOSE 'Regular @ 1600 CT'."
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
            "'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). GC, MGC, "
            "SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 schedules carry "
            "the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals & DME "
            "Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and EUA "
            "Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX. Thursday Dec 31 CLOSE 'Regular @ 1600 CT'."
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
            "'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). GC, MGC, "
            "SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 schedules carry "
            "the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals & DME "
            "Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and EUA "
            "Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX. Thursday Dec 23: 'Regular per Product'."
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
            "'Energy, Metals & DME' (NYMEX energy together with COMEX metals and DME). GC, MGC, "
            "SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 schedules carry "
            "the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals & DME "
            "Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and EUA "
            "Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX. January 1, 2022 fell on a Saturday: Friday Dec "
            "31 and Monday Jan 3 both regular for COMEX metals (D.1f found the same for equities "
            "on Jan 3)."
        ),
    ),
    date(2022, 7, 1): Citation(
        _HC + "2022-independence-day-holiday-schedule-compact.xls",
        (
            "Calendar Date|Friday July 1|Sunday July 3|Monday July 4|Monday July 4 ... Energy, "
            "Metals & DME |Regular @ 1600 CT / 2100 UTC"
        ),
        note=(
            "Friday before Independence Day: regular close. CME's compact Globex holiday schedule "
            "states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX energy "
            "together with COMEX metals and DME). GC, MGC, SI, SIL, HG and MHG are not named "
            "individually. CME's full 2019-2022 schedules carry the row 'Energy, Metals, Softs & "
            "DME Products' (2022: 'Energy, Metals & DME Products') whose only exception rows are "
            "DME Oman Crude TAM, Singapore TAM and EUA Daily Futures; their only COMEX metals "
            "notes concern TAS (for example 'Gold TAS – Early close 1130 CT / 1230 ET'). The "
            "'Gold' row lower in the full sheets belongs to Bursa Malaysia Derivatives, not COMEX."
        ),
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
            "early on Dec 23. CME's compact Globex holiday schedule states hours per asset-class "
            "row; the row is 'Energy, Metals & DME' (NYMEX energy together with COMEX metals and "
            "DME). GC, MGC, SI, SIL, HG and MHG are not named individually. CME's full 2019-2022 "
            "schedules carry the row 'Energy, Metals, Softs & DME Products' (2022: 'Energy, Metals "
            "& DME Products') whose only exception rows are DME Oman Crude TAM, Singapore TAM and "
            "EUA Daily Futures; their only COMEX metals notes concern TAS (for example 'Gold TAS – "
            "Early close 1130 CT / 1230 ET'). The 'Gold' row lower in the full sheets belongs to "
            "Bursa Malaysia Derivatives, not COMEX."
        ),
    ),
    date(2022, 12, 30): Citation(
        _HC + "2023-new-years-holiday-schedule-compact.xls",
        (
            "Calendar Trade|Friday,Dec 30|Sunday, Jan 1 and Monday, Jan 2 ... Energy, Metals & DME "
            "|Regular @ 1600 CT / 2200 UTC|Globex Closed"
        ),
        note=(
            "Friday before New Year's Day (observed): regular close. CME's compact Globex holiday "
            "schedule states hours per asset-class row; the row is 'Energy, Metals & DME' (NYMEX "
            "energy together with COMEX metals and DME). GC, MGC, SI, SIL, HG and MHG are not "
            "named individually. CME's full 2019-2022 schedules carry the row 'Energy, Metals, "
            "Softs & DME Products' (2022: 'Energy, Metals & DME Products') whose only exception "
            "rows are DME Oman Crude TAM, Singapore TAM and EUA Daily Futures; their only COMEX "
            "metals notes concern TAS (for example 'Gold TAS – Early close 1130 CT / 1230 ET'). "
            "The 'Gold' row lower in the full sheets belongs to Bursa Malaysia Derivatives, not "
            "COMEX."
        ),
    ),
    date(2023, 7, 3): Citation(
        _TH + "4th-of-july-2023.pdf",
        (
            "PRODUCT NAME MONDAY, 3 JULY 2023 TUESDAY, 4 JULY 2023 WEDNESDAY, 5 JULY 2023 ... "
            "TRADE DATE: MON 3 JULY TRADE DATE: WED 5 JULY 16:00 (CLOSED) TRADE DATE: WED 5 JULY "
            "16:00 (CLOSED) METALS TRADE DATE: WED 5 JULY 13:30 (PREOPEN) HALT"
        ),
        note=(
            "Day before Independence Day: regular close. CME holiday summary PDF: hours of 'the "
            "most actively traded instruments for each asset class', METALS row; text read with "
            "pdftotext -layout, so the METALS line carries the day columns left to right (a cell "
            "printed on the line above or below the row label belongs to the same row). The Monday "
            "3 July column of the METALS row reads 'TRADE DATE: MON 3 JULY 16:00 (CLOSED)' then "
            "'TRADE DATE: WED 5 JULY 16:45 (PREOPEN) 17:00 (OPEN)': the regular close. CME's 2023 "
            "July 4 settlement notice settles only interest-rate and equity-index products early "
            "that Monday."
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
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2024-07-03","events":[{"tradingDate":"2024-07-03","eventTime":"16:00","ma'
            'rketEventType":"closed"},{"tradingDate":"2024-07-05","eventTime":"16:45","marketEventT'
            'ype":"preopen"},{"tradingDate":"2024-07-05","eventTime":"17:00","marketEventType":"ope'
            'n"}]}'
        ),
        note=(
            "Day before Independence Day: regular close. CME's trading-hours-by-product service "
            "behind cmegroup.com/trading-hours.html, product 437 'Gold Futures' (GC), Wayback "
            "capture 20240708161439. GC stands for the group: CME's holiday schedules give COMEX "
            "metals hours per asset class (row METALS), and the service's only metals product is "
            "GC (no SI or HG record was captured). 'preopen' at a time = trading halts (order "
            "entry only) until the next 'open'; 'closed' = final close of the trade date."
        ),
    ),
    date(2024, 12, 31): Citation(
        _svc("2024-12-31", "2025-01-02", "1734710019538"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2024-12-31","events":[{"tradingDate":"2024-12-31","eventTime":"16:00","ma'
            'rketEventType":"closed"}]}'
        ),
        note=(
            "New Year's Eve: regular close. CME's trading-hours-by-product service behind "
            "cmegroup.com/trading-hours.html, product 437 'Gold Futures' (GC), Wayback capture "
            "20241220155340. GC stands for the group: CME's holiday schedules give COMEX metals "
            "hours per asset class (row METALS), and the service's only metals product is GC (no "
            "SI or HG record was captured). 'preopen' at a time = trading halts (order entry only) "
            "until the next 'open'; 'closed' = final close of the trade date."
        ),
    ),
    date(2025, 1, 9): Citation(
        _TH + "day-of-mourning-january-9-2024.pdf",
        "PRODUCT NAME JANUARY 9, 2025 ... CME GROUP METALS NORMAL HOURS",
        note=(
            "National Day of Mourning (Carter): metals normal hours. CME's trading schedule for "
            "January 9, 2025 (file name says 2024): equities closed at 08:30 CT and rates early, "
            "metals traded normal hours. The equity calendar has an 08:30 CT entry that day; the "
            "metals calendar has none."
        ),
    ),
    date(2025, 7, 3): Citation(
        _svc("2025-07-03", "2025-07-05", "1734710019545"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2025-07-03","events":[{"tradingDate":"2025-07-03","eventTime":"16:00","ma'
            'rketEventType":"closed"},{"tradingDate":"2025-07-04","eventTime":"16:45","marketEventT'
            'ype":"preopen"},{"tradingDate":"2025-07-04","eventTime":"17:00","marketEventType":"ope'
            'n"}]}'
        ),
        note=(
            "Day before Independence Day: regular close. CME's trading-hours-by-product service "
            "behind cmegroup.com/trading-hours.html, product 437 'Gold Futures' (GC), Wayback "
            "capture 20241220155340. GC stands for the group: CME's holiday schedules give COMEX "
            "metals hours per asset class (row METALS), and the service's only metals product is "
            "GC (no SI or HG record was captured). 'preopen' at a time = trading halts (order "
            "entry only) until the next 'open'; 'closed' = final close of the trade date."
        ),
    ),
    date(2025, 12, 31): Citation(
        _svc("2025-12-31", "2026-01-02", "1769649703066"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2025-12-31","events":[{"tradingDate":"2025-12-31","eventTime":"16:00","ma'
            'rketEventType":"closed"}]}'
        ),
        note=(
            "New Year's Eve: regular close. CME's trading-hours-by-product service behind "
            "cmegroup.com/trading-hours.html, product 437 'Gold Futures' (GC), Wayback capture "
            "20260129012143. GC stands for the group: CME's holiday schedules give COMEX metals "
            "hours per asset class (row METALS), and the service's only metals product is GC (no "
            "SI or HG record was captured). 'preopen' at a time = trading halts (order entry only) "
            "until the next 'open'; 'closed' = final close of the trade date."
        ),
    ),
    date(2026, 4, 2): Citation(
        _svc("2026-04-01", "2026-04-03", "1743113432016"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2026-04-02","events":[{"tradingDate":"2026-04-02","eventTime":"16:00","ma'
            'rketEventType":"closed"}]}'
        ),
        note=(
            "Thursday before Good Friday: regular close. CME's trading-hours-by-product service "
            "behind cmegroup.com/trading-hours.html, product 437 'Gold Futures' (GC), Wayback "
            "capture 20260610104510. GC stands for the group: CME's holiday schedules give COMEX "
            "metals hours per asset class (row METALS), and the service's only metals product is "
            "GC (no SI or HG record was captured). 'preopen' at a time = trading halts (order "
            "entry only) until the next 'open'; 'closed' = final close of the trade date."
        ),
    ),
    date(2026, 6, 18): Citation(
        _svc("2026-06-18", "2026-06-20", "1784720540600"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2026-06-18","events":[{"tradingDate":"2026-06-18","eventTime":"16:00","ma'
            'rketEventType":"closed"},{"tradingDate":"2026-06-22","eventTime":"16:45","marketEventT'
            'ype":"preopen"},{"tradingDate":"2026-06-22","eventTime":"17:00","marketEventType":"ope'
            'n"}]}'
        ),
        note=(
            "Thursday before Juneteenth: regular close. CME's trading-hours-by-product service "
            "behind cmegroup.com/trading-hours.html, product 437 'Gold Futures' (GC), Wayback "
            "capture 20260722114220. GC stands for the group: CME's holiday schedules give COMEX "
            "metals hours per asset class (row METALS), and the service's only metals product is "
            "GC (no SI or HG record was captured). 'preopen' at a time = trading halts (order "
            "entry only) until the next 'open'; 'closed' = final close of the trade date."
        ),
    ),
}

SESSION_SOURCES: dict[str, Citation] = {
    "cme_metals_hours": Citation(
        _METALS + "precious/gold_contract_specifications.html",
        (
            "Trading Hours Sunday - Friday 6:00 p.m. - 5:00 p.m. (5:00 p.m. - 4:00 p.m. /CT) with "
            "a 60-minute break each day beginning at 5:00 p.m. (4:00 p.m. CT)"
        ),
        _svc("2026-01-18", "2026-01-20", "1769649703068"),
        (
            '"globex":"GC","prodGroup":"GC","name":"Gold Futures","id":437 ... {"groupCode":"GC",'
            '"eventDate":"2026-01-20","events":[{"tradingDate":"2026-01-20","eventTime":"16:00","ma'
            'rketEventType":"closed"},{"tradingDate":"2026-01-21","eventTime":"16:45","marketEventT'
            'ype":"preopen"},{"tradingDate":"2026-01-21","eventTime":"17:00","marketEventType":"ope'
            'n"}]}'
        ),
        note=(
            "Regular COMEX metals Globex session, Sunday-Friday 17:00-16:00 CT with the daily "
            "16:00-17:00 CT halt: CME's GC contract specifications (capture 2019-07-23) and CME's "
            "2026 GC trading-hours record (16:00 closed, 16:45 pre-open, 17:00 open). The other "
            "SESSION_SOURCES keys give the same hours for SI and HG (2019), MGC and SIL (2020 fact "
            "card) and MHG (2022 FAQ). No CME notice of a change to COMEX metals Globex hours in "
            "2019-2026 was found."
        ),
    ),
    "cme_si_hours": Citation(
        _METALS + "precious/silver_contract_specifications.html",
        (
            "Trading Hours Sunday - Friday 6:00 p.m. - 5:00 p.m. (5:00 p.m. - 4:00 p.m. CT) with a "
            "60-minute break each day beginning at 5:00 p.m. (4:00 p.m. CT)"
        ),
        note="SI contract specifications, capture 2019-07-17.",
    ),
    "cme_hg_hours": Citation(
        _METALS + "base/copper_contract_specifications.html",
        (
            "Trading Hours CME Globex: Sunday - Friday 6:00 p.m. - 5:00 p.m. (5:00 p.m. - 4:00 "
            "p.m. CT) with a 60-minute break each day beginning at 5:00 p.m. (4:00 p.m. CT)"
        ),
        note="HG contract specifications, capture 2019-07-20.",
    ),
    "cme_mgc_sil_hours": Citation(
        _METALS + "files/PM264-e-micro-gold-and-silver-futures.pdf",
        (
            "E-MICRO GOLD AND 1,000 OZ. SILVER FUTURES ... Product Symbols CME Globex, CME "
            "ClearPort and Clearing: MGC CME Globex, CME ClearPort and Clearing: SIL Venue and "
            "Hours CME ClearPort and CME Globex: Sunday – Friday CME ClearPort and CME Globex: "
            "Sunday – Friday 6:00 p.m. – 5:00 p.m. (5:00 p.m.– 4:00 p.m. Central 6:00 p.m. – 5:00 "
            "p.m. (5:00 p.m.– 4:00 p.m. Central Time/CT) with a 60-minute break each day Time/CT) "
            "with a 60-minute break each day beginning at 5:00 p.m. (4:00 p.m. CT) beginning at "
            "5:00 p.m. (4:00 p.m. CT)"
        ),
        note=(
            "E-micro Gold and 1,000-oz. Silver fact card (capture 2020-09-29); its two columns "
            "(MGC, SIL) interleave in the pdftotext layout text, each giving the same hours."
        ),
    ),
    "cme_mhg_hours": Citation(
        "https://www.cmegroup.com/articles/faqs/micro-copper-futures-faq.html",
        (
            "The contract symbol is MHG ... Trading and Clearing Hours CME Globex: Sunday - Friday "
            "5:00 p.m. Central Time/CT with a daily maintenance period from 4:00 p.m. - 5:00 p.m. "
            "CT"
        ),
        note=(
            "Micro Copper futures FAQ (capture 2022-05-28). The page reads 'Sunday - Friday 5:00 "
            "p.m. Central Time/CT' with no end time; with the stated 16:00-17:00 CT maintenance "
            "period it is the 17:00-16:00 CT session of HG."
        ),
    ),
    "cme_metals_settlement": Citation(
        _WIKI + "457085528/Daily+Settlement+Time+Details",
        (
            "Metals *Daily Settlement Time Ranges ... Copper 12:59:00-13:00:00 ET ... Silver "
            "13:24:00-13:25:00 ET ... Gold 13:29:00-13:30:00 ET"
        ),
        note=(
            "D6 confirmation of C: CME's daily settlement time ranges for COMEX metals (CME client "
            "wiki 'Daily Settlement Time Details', cached by CalendarBuilder-Energy, read "
            "directly): Gold 13:29:00-13:30:00 ET = 12:29-12:30 CT (D6 gold C 12:30), Silver "
            "13:24:00-13:25:00 ET = 12:24-12:25 CT (D6 silver C 12:25), Copper 12:59:00-13:00:00 "
            "ET = 11:59-12:00 CT (D6 copper C 12:00)."
        ),
    ),
    "cme_gc_mgc_settlement": Citation(
        _WIKI + "457088147/Gold",
        (
            "Gold futures (GC) are settled by CME Group staff based on trading activity on CME "
            "Globex during the settlement period. The settlement period is defined as: 13:29:00 to "
            "13:30:00 ET for the active month ... The settlements in the Micro Gold (MGC) Futures "
            "contracts are derived directly from the settlements of the regular sized Gold (GC) "
            "Futures contracts."
        ),
        _CONF + "Gold",
        (
            "last modified by Confluence Admin on Aug 02, 2018 ... The settlement period is "
            "defined as: 13:29:00 to 13:30:00 ET for the Active Month"
        ),
        note=(
            "CME client wiki 'Gold' (version 2026-04-15, read through its REST API); the CME Gold "
            "procedure page as captured 2019-04-11 (last modified 2018-08-02) gives the same "
            "period, and the captures of 2022-06-30 and 2024-05-20 do too, so C = 12:30 CT held "
            "for the whole 2019-2026 window. MGC settles to GC."
        ),
    ),
    "cme_si_sil_settlement": Citation(
        _WIKI + "457415360/Silver",
        (
            "Silver futures (SI) are settled by CME Group staff based on trading activity on CME "
            "Globex during the settlement period. The settlement period is defined as: 12:24:00 to "
            "12:25:00 CT for the active month ... The settlements in the Micro Silver futures "
            "(SIL) are derived directly from the settlements of the full-sized Silver futures (SI)."
        ),
        _CONF + "Silver",
        (
            "The settlement period is defined as: 13:24:00 to 13:25:00 ET for the Active Month ... "
            "The settlements in the Micro Silver (SIL) Futures contracts are derived directly from "
            "the settlements of the regular sized (5,000-oz.) Silver (SI) Futures contracts."
        ),
        note=(
            "CME client wiki 'Silver' (version 2026-02-10, read through its REST API; states the "
            "period in CT); the CME Silver procedure page as captured 2020-11-11 gives 13:24:00 to "
            "13:25:00 ET (= 12:24-12:25 CT), as do the captures of 2018-01-02 and 2022-06-25: C = "
            "12:25 CT for the whole window. SIL settles to SI."
        ),
    ),
    "cme_hg_mhg_settlement": Citation(
        _WIKI + "457415464/Copper",
        (
            "Copper futures (HG) are settled by CME Group staff based on trading activity on CME "
            "Globex during the settlement period. The settlement period is defined as: 12:59:00 to "
            "13:00:00 ET for the active month ... Micro Copper futures (MHG) daily settlements are "
            "equal to the daily settlement price of the Copper futures (HG)."
        ),
        _CONF + "Copper",
        "The settlement period is defined as: 12:59:00 to 13:00:00 ET for the Active Month",
        note=(
            "CME client wiki 'Copper' (version 2025-10-13, read through its REST API); the CME "
            "Copper procedure page as captured 2019-07-21 gives the same period, as does the "
            "capture of 2022-12-24: C = 12:00 CT for the whole window. MHG settles to HG."
        ),
    ),
}
