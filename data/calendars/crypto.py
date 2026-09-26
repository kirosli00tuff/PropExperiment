"""CME Globex calendar for the crypto group: CME Micro Bitcoin futures (MBT), 2019-05-01..2026-06-19
(Stage E.2a Task 6; design D10 and D11.3).

Interface as data.cme_calendar, whose Holiday, HolidayKind, Citation and CalendarCoverageError are
imported, not redefined: HOLIDAYS, SOURCES, NO_ENTRY_FINDINGS, CALENDAR_COVERAGE and
assert_calendar_coverage, plus SESSIONS (data.calendars.SessionSpec) with SESSION_SOURCES.
Additive extensions, which no existing caller needs to know about:
- LATE_OPENS (with LATE_OPEN_SOURCES): trade dates whose session did not trade from its regular
  start, with the rates and energy groups' meaning (one entry, the 2025-11-28 CME outage).
  LateOpen has their fields plus ``open_offset_days`` (default 0, their meaning).
- EXTENDED_MAINTENANCE (with EXTENDED_MAINTENANCE_SOURCES): a scheduled maintenance extension
  that delayed a trade date's start on an earlier calendar day: the first 24/7 trade date
  (2026-06-01) opened Friday 2026-05-29 at 16:30 CT, not 16:02 CT (``open_offset_days`` -3). Kept
  out of LATE_OPENS, which data.group_session reads as opening on the trade date itself.
- WEEKEND_TO_NEXT_TRADE_DATE_FROM: the first trade date from which CME assigns weekend (and
  holiday) trading to the next business day (2026-06-01), read by data.group_session.
- GLOBEX_HOURS_UNDOCUMENTED: days with no CME document of crypto hours and no entry, listed for
  the bar check (the rates group's attribute): MLK Day 2023.
- BOOKED_FORWARD (with BOOKED_FORWARD_SOURCES): US holidays on which crypto traded its regular
  Globex hours while CME set no trade date that day and booked the day's trading to the next
  business day. Not HOLIDAYS entries (the clock session is regular); recorded so the trade-date
  assignment is on file. How the bar builder treats them is the lead's ruling (see 2026-06-19).
- SEGMENTS_AFTER_WEEKEND_24_7: the session shape of the first business day after a weekend in
  the 24/7 regime, which a SessionSpec's single segments tuple cannot carry.

Sources (all CME Group; cmegroup.com refuses automated fetches, so every cmegroup.com file was
read from a Wayback Machine copy; the CME client wiki on atlassian.net was read directly):
- 2019-2021: CME's compact Globex holiday schedules (.xls) in CME's yearly holiday-calendars.zip,
  row "Bitcoin".
- 2022 and New Year 2023: CME's per-holiday Globex schedules (.xls), row "Cryptocurrency".
- 2023: CME's holiday trading-hours summary PDFs, row "CRYPTOCURRENCIES".
- 2023-12..2026-06: CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html,
  product 8478 (BTC, Bitcoin Futures), captures of 2024-07-08, 2024-12-20, 2026-01-29, 2026-06-10
  and 2026-06-19.
- Good Friday 2026 status: CME's 2026 Good Friday clearing advisory. 2025-11-28 outage: CME
  Group's 2025 Form 10-K.
- SESSIONS: CME contract specifications and FAQs (5-day hours); CME press releases of 2026-02-19
  and 2026-06-01, CME's cryptocurrency FAQ and client-wiki migration page (24/7 hours and the
  weekend and holiday trade-date rule); CME client-wiki settlement procedures (D6's C).
MBT is taken to share BTC's hours: CME derives MBT's daily settlement from BTC, and its holiday
schedules carry one crypto row ("Bitcoin", from 2022 "Cryptocurrency") for its crypto futures.
MBT listed 2021-05-03; the calendar covers 2019-05-01 onward from the same row. Verbatim quotes,
capture URLs, file hashes and the script-run verbatim check:
reports/stage_e2a_calendar_sources_crypto.json and .md.

Grades as data.cme_calendar: status (``evidence``) "cme" | "secondary" | "unverified"; time
(``time_evidence``) "cme" | "secondary" | "inferred" | "unverified" | "n/a" ("empirical" is
reserved for the later bar check). Every HOLIDAYS entry is status "cme", time "cme" (closures
"n/a"). One BOOKED_FORWARD record is "unverified": MLK Day 2023 (no CME document with a crypto
row was found; pattern-assumed).

How crypto differs from the equity calendar (data/cme_calendar.py):
- 2019-2021: crypto halts with equities (12:00 CT holiday halts; 12:15 CT early closes), except
  the day after Thanksgiving 2021 (12:45 CT). Good Friday 2021: abbreviated session to 08:15 CT.
- From 2022-01-17 crypto trades its regular hours on the US holidays on which equities halt at
  12:00 CT (MLK, Presidents, Memorial, Juneteenth, Independence, Labor, Thanksgiving Day):
  BOOKED_FORWARD. Exception: Friday 2025-07-04 (12:00 CT close). New Year's Day, Christmas and the
  non-jobs-report Good Fridays stay full closures. Day after Thanksgiving: 12:45 CT (2021-2023),
  13:45 CT (2024-2025); Christmas Eve: 12:45 CT (2024-2025). The eve of Independence Day and New
  Year's Eve close at the regular 16:00 CT (NO_ENTRY_FINDINGS).
- Jobs-report Good Fridays close 08:15 CT (2021) and 10:15 CT (2023, 2026; equities 08:15 CT).
- 2025-01-09 (National Day of Mourning): crypto normal hours (equities closed 08:30 CT).
- From Friday 2026-05-29 16:00 CT crypto trades 24/7 (SESSIONS; frozen design D10).

Conventions: ``halt_ct`` is the CT minute trading stops, so the last one-minute bar starts at
halt_ct minus one minute; the reopen is the normal 17:00 CT (Sunday 17:00 when the halt day is a
Friday). CME books the Globex session that ends at a holiday halt to the next trade date (not on
2025-07-04); this module keeps each halt day as its own short trade date, as data.cme_calendar
does. Holdout-2 dates (2024-04-01..2025-03-31) and the 2019-05..2024-02 confirmation window rest on
CME's schedules alone until their bars are checked.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, time

from data.calendars import Segment, SessionSpec
from data.cme_calendar import CalendarCoverageError, Citation, Holiday, HolidayKind

CRYPTO_PRODUCTS = ("MBT",)

HALT_NOON = time(12, 0)  # holiday halt 2019-2021; Friday 2025-07-04 close
CLOSE_1215 = time(12, 15)  # early close 2019-2020 (eve of July 4, day after Thanksgiving, Dec 24)
CLOSE_1245 = time(12, 45)  # day after Thanksgiving 2021-2023; Christmas Eve 2024-2025
CLOSE_1345 = time(13, 45)  # day after Thanksgiving 2024-2025
GOOD_FRIDAY_0815 = time(8, 15)  # jobs-report Good Friday 2021
GOOD_FRIDAY_1015 = time(10, 15)  # jobs-report Good Fridays 2023 and 2026

LAST_5DAY_TRADE_DATE = date(2026, 5, 29)  # 24/7 trading starts after its 16:00 CT close
FIRST_24_7_TRADE_DATE = date(2026, 6, 1)

_HC = "https://www.cmegroup.com/tools-information/holiday-calendar/files/"
_TH = "https://www.cmegroup.com/trading-hours/files/"
_FILES = "https://www.cmegroup.com/files/"
_Z19, _Z20, _Z21 = (_HC + f"{y}-holiday-calendars.zip" for y in (2019, 2020, 2021))
_WIKI = "https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/"
_WIKI_247 = _WIKI + "1283194884/Cryptocurrency+Futures+and+Options+Migration+to+24-7+Trading"
_WIKI_BITCOIN = _WIKI + "457318016/Bitcoin"
_WIKI_SETTLE_TIMES = _WIKI + "457085528/Daily+Settlement+Time+Details"
_WIKI_BITCOIN_OLD = "https://www.cmegroup.com/confluence/display/EPICSANDBOX/Bitcoin"
_PR = "https://www.cmegroup.com/media-room/press-releases/2026/"
_PR_2026_02_19 = _PR + "2/19/cme_group_to_launch247cryptocurrencyfuturesandoptionstradingonma.html"
_PR_2026_06_01 = _PR + "6/01/cme_group_announceslaunchof247cryptocurrencyfuturesandoptionstra.html"
_ARTICLE_247 = (
    "https://www.cmegroup.com/articles/2026/aligning-cryptocurrency-derivatives-with-spot-markets-"
    "measuring-the-247-trading-opportunity.html"
)
_FAQ_CRYPTO = (
    "https://www.cmegroup.com/articles/faqs/frequently-asked-questions-cryptocurrency-futures.html"
)
_BTC_SPECS = (
    "https://www.cmegroup.com/trading/equity-index/us-index/bitcoin_contract_specifications.html"
)
_MBT_FAQ = (
    "https://www.cmegroup.com/education/articles-and-reports/"
    "micro-bitcoin-futures-frequently-asked-questions.html"
)
_CME_10K = "https://www.sec.gov/Archives/edgar/data/1156375/000115637526000009/cme-20251231.htm"


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
    _halt(date(2019, 7, 3), "Day before Independence Day", CLOSE_1215),
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
    _halt(date(2021, 4, 2), "Good Friday (abbreviated, jobs report)", GOOD_FRIDAY_0815),
    _halt(date(2021, 5, 31), "Memorial Day", HALT_NOON),
    _halt(date(2021, 7, 5), "Independence Day (observed)", HALT_NOON),
    _halt(date(2021, 9, 6), "Labor Day", HALT_NOON),
    _halt(date(2021, 11, 25), "Thanksgiving Day", HALT_NOON),
    _halt(date(2021, 11, 26), "Day after Thanksgiving", CLOSE_1245),
    _closure(date(2021, 12, 24), "Christmas Day (observed)"),
    # ---- 2022
    _closure(date(2022, 4, 15), "Good Friday"),
    _halt(date(2022, 11, 25), "Day after Thanksgiving", CLOSE_1245),
    _closure(date(2022, 12, 26), "Christmas Day (observed)"),
    # ---- 2023
    _closure(date(2023, 1, 2), "New Year's Day (observed)"),
    _halt(date(2023, 4, 7), "Good Friday (abbreviated, jobs report)", GOOD_FRIDAY_1015),
    _halt(date(2023, 11, 24), "Day after Thanksgiving", CLOSE_1245),
    _closure(date(2023, 12, 25), "Christmas Day"),
    # ---- 2024
    _closure(date(2024, 1, 1), "New Year's Day"),
    _closure(date(2024, 3, 29), "Good Friday"),
    _halt(date(2024, 11, 29), "Day after Thanksgiving", CLOSE_1345),
    _halt(date(2024, 12, 24), "Christmas Eve", CLOSE_1245),
    _closure(date(2024, 12, 25), "Christmas Day"),
    # ---- 2025
    _closure(date(2025, 1, 1), "New Year's Day"),
    _closure(date(2025, 4, 18), "Good Friday"),
    _halt(date(2025, 7, 4), "Independence Day", HALT_NOON),
    _halt(date(2025, 11, 28), "Day after Thanksgiving", CLOSE_1345),
    _halt(date(2025, 12, 24), "Christmas Eve", CLOSE_1245),
    _closure(date(2025, 12, 25), "Christmas Day"),
    # ---- 2026
    _closure(date(2026, 1, 1), "New Year's Day"),
    _halt(date(2026, 4, 3), "Good Friday (abbreviated, jobs report)", GOOD_FRIDAY_1015),
)

HOLIDAYS: dict[date, Holiday] = {h.day: h for h in _ENTRIES}
CALENDAR_COVERAGE = (date(2019, 5, 1), date(2026, 6, 19))


def assert_calendar_coverage(days: Iterable[date]) -> None:
    """Raise unless every date lies inside ``CALENDAR_COVERAGE`` (inclusive); the semantics of
    data.cme_calendar.assert_calendar_coverage, for the crypto group."""
    first, last = CALENDAR_COVERAGE
    outside = sorted(d for d in set(days) if not first <= d <= last)
    if outside:
        raise CalendarCoverageError(
            f"{len(outside)} trade date(s) outside the crypto calendar's coverage "
            f"{first}..{last}: {outside[0]} .. {outside[-1]}; extend data/calendars/crypto.py "
            "first")


@dataclass(frozen=True)
class LateOpen:
    """A trade date whose Globex session did not trade from its regular start: trading stopped at
    ``halt_from_ct`` on the calendar day ``halt_from_offset_days`` from ``day`` (None: the stop
    time is not in any source retrieved) and resumed at ``open_ct`` CT on the calendar day
    ``open_offset_days`` from ``day`` (0: on ``day`` itself, the rates and energy groups'
    meaning). Grades as for Holiday. Additive to the data.cme_calendar interface."""

    day: date
    name: str
    open_ct: time
    evidence: str
    time_evidence: str
    halt_from_ct: time | None = None
    halt_from_offset_days: int = -1
    open_offset_days: int = 0


@dataclass(frozen=True)
class BookedForward:
    """A weekday on which crypto traded its regular Globex hours but CME set no trade date:
    CME booked that day's trading to ``cme_trade_date`` (no settlement on ``day``). Not a
    HOLIDAYS entry, because the clock session is regular. ``evidence`` graded as
    Holiday.evidence. Additive to the data.cme_calendar interface."""

    day: date
    name: str
    cme_trade_date: date
    evidence: str


def _fwd(day: date, name: str, cme_trade_date: date, evidence: str = "cme") -> BookedForward:
    return BookedForward(day, name, cme_trade_date, evidence)


LATE_OPENS: dict[date, LateOpen] = {
    date(2025, 11, 28): LateOpen(
        date(2025, 11, 28),
        "Globex outage (data-center cooling failure)",
        time(7, 30),
        "cme",
        "cme",
    ),
}

# Scheduled maintenance extensions that delayed a trade date's start on an earlier calendar day
# (open_offset_days < 0). Not LATE_OPENS: data.group_session reads LATE_OPENS as opening on
# the trade date itself.
EXTENDED_MAINTENANCE: dict[date, LateOpen] = {
    date(2026, 6, 1): LateOpen(
        date(2026, 6, 1),
        "First 24/7 session: day-one extended maintenance",
        time(16, 30),
        "cme",
        "cme",
        halt_from_ct=time(16, 0),
        halt_from_offset_days=-3,
        open_offset_days=-3,
    ),
}

BOOKED_FORWARD: dict[date, BookedForward] = {
    f.day: f
    for f in (
        _fwd(date(2022, 1, 17), "Martin Luther King Jr. Day", date(2022, 1, 18)),
        _fwd(date(2022, 2, 21), "Presidents Day", date(2022, 2, 22)),
        _fwd(date(2022, 5, 30), "Memorial Day", date(2022, 5, 31)),
        _fwd(date(2022, 6, 20), "Juneteenth (observed)", date(2022, 6, 21)),
        _fwd(date(2022, 7, 4), "Independence Day", date(2022, 7, 5)),
        _fwd(date(2022, 9, 5), "Labor Day", date(2022, 9, 6)),
        _fwd(date(2022, 11, 24), "Thanksgiving Day", date(2022, 11, 25)),
        _fwd(date(2023, 1, 16), "Martin Luther King Jr. Day", date(2023, 1, 17), "unverified"),
        _fwd(date(2023, 2, 20), "Presidents Day", date(2023, 2, 21)),
        _fwd(date(2023, 5, 29), "Memorial Day", date(2023, 5, 30)),
        _fwd(date(2023, 6, 19), "Juneteenth", date(2023, 6, 20)),
        _fwd(date(2023, 7, 4), "Independence Day", date(2023, 7, 5)),
        _fwd(date(2023, 9, 4), "Labor Day", date(2023, 9, 5)),
        _fwd(date(2023, 11, 23), "Thanksgiving Day", date(2023, 11, 24)),
        _fwd(date(2024, 1, 15), "Martin Luther King Jr. Day", date(2024, 1, 16)),
        _fwd(date(2024, 2, 19), "Presidents Day", date(2024, 2, 20)),
        _fwd(date(2024, 5, 27), "Memorial Day", date(2024, 5, 28)),
        _fwd(date(2024, 6, 19), "Juneteenth", date(2024, 6, 20)),
        _fwd(date(2024, 7, 4), "Independence Day", date(2024, 7, 5)),
        _fwd(date(2024, 9, 2), "Labor Day", date(2024, 9, 3)),
        _fwd(date(2024, 11, 28), "Thanksgiving Day", date(2024, 11, 29)),
        _fwd(date(2025, 1, 20), "Martin Luther King Jr. Day", date(2025, 1, 21)),
        _fwd(date(2025, 2, 17), "Presidents Day", date(2025, 2, 18)),
        _fwd(date(2025, 5, 26), "Memorial Day", date(2025, 5, 27)),
        _fwd(date(2025, 6, 19), "Juneteenth", date(2025, 6, 20)),
        _fwd(date(2025, 9, 1), "Labor Day", date(2025, 9, 2)),
        _fwd(date(2025, 11, 27), "Thanksgiving Day", date(2025, 11, 28)),
        _fwd(date(2026, 1, 19), "Martin Luther King Jr. Day", date(2026, 1, 20)),
        _fwd(date(2026, 2, 16), "Presidents Day", date(2026, 2, 17)),
        _fwd(date(2026, 5, 25), "Memorial Day", date(2026, 5, 26)),
        _fwd(date(2026, 6, 19), "Juneteenth (24/7 regime)", date(2026, 6, 22)),
    )
}

# CME assigns weekend and holiday trading to the next business day from the first 24/7 trade date
# on (SESSION_SOURCES 'cme_crypto_24_7_launch', 'cme_crypto_24_7_hours'); data.group_session
# reads this attribute. Before it, the weekend is closed (Friday 16:00 to Sunday 17:00 CT).
WEEKEND_TO_NEXT_TRADE_DATE_FROM = FIRST_24_7_TRADE_DATE

# Days with no CME document of crypto Globex hours and no entry (regular hours assumed), listed
# for the bar check, as the rates group does (data.group_session reads this attribute).
GLOBEX_HOURS_UNDOCUMENTED: dict[date, str] = {
    date(2023, 1, 16): (
        "MLK Day 2023: no CME schedule with a crypto row was retrieved; regular hours assumed "
        "from the crypto rows of MLK 2022 and Presidents Day 2023 (BOOKED_FORWARD, graded "
        "unverified). A 12:00 CT halt here would mean a missing EARLY_HALT entry."
    ),
}

# The Monday (first business day after a weekend) session in the 24/7 regime: Friday 16:02 CT to
# Saturday 02:00 CT, then Saturday 04:00 CT to Monday 16:00 CT (CME's weekly Saturday 02:00-04:00
# CT maintenance). Tuesday-Friday trade dates use the 24/7 SessionSpec's segments. A holiday
# extends the span to the next business day (CME's rule; BOOKED_FORWARD 2026-06-19).
SEGMENTS_AFTER_WEEKEND_24_7: tuple[Segment, ...] = (
    Segment(-3, time(16, 2), -2, time(2, 0)),
    Segment(-2, time(4, 0), 0, time(16, 0)),
)

_D6_NOTE = (
    "day_session_ct is design D6's crypto row (O 08:30, C 15:00 CT; F 15:08 CT is applied by the "
    "rules engine), keyed by product. D6 confirmation: C 15:00 CT matches CME's daily settlement "
    "period for Bitcoin futures, 14:59:00-15:00:00 CT, from which MBT's settlement is copied "
    "(SESSION_SOURCES 'cme_btc_settlement_2026', 'cme_settlement_time_details', "
    "'cme_btc_settlement_2020', 'cme_mbt_settlement_2021': unchanged 2020-2026, and unchanged by "
    "the 24/7 launch). O 08:30 CT is not a boundary CME publishes for its crypto futures: the "
    "Globex session runs 17:00-16:00 CT (24/7 from 2026-05-29) and no CME settlement procedure, "
    "contract specification or FAQ retrieved defines a crypto day-session open. D6's value is "
    "encoded unchanged; the lead rules (reports/stage_e2a_calendar_sources_crypto.md, D6 "
    "confirmation)."
)

SESSIONS: tuple[SessionSpec, ...] = (
    SessionSpec(
        valid_from=date(2019, 5, 1),
        valid_to=LAST_5DAY_TRADE_DATE,
        segments=(Segment(-1, time(17, 0), 0, time(16, 0)),),
        day_session_ct={p: (time(8, 30), time(15, 0)) for p in CRYPTO_PRODUCTS},
        source="cme_crypto_hours_5day",
        note=(
            "5-day regime: Sunday 17:00 CT open, daily 16:00-17:00 CT break, Friday 16:00 CT "
            "close; a Monday trade date opens Sunday 17:00 CT (offset -1). Unchanged 2019-05-01.."
            "2026-05-29 (SESSION_SOURCES 'cme_crypto_hours_5day', 'cme_crypto_hours_5day_2026'). "
            + _D6_NOTE
        ),
    ),
    SessionSpec(
        valid_from=FIRST_24_7_TRADE_DATE,
        valid_to=date(2026, 6, 19),
        segments=(Segment(-1, time(16, 2), 0, time(16, 0)),),
        day_session_ct={p: (time(8, 30), time(15, 0)) for p in CRYPTO_PRODUCTS},
        source="cme_crypto_24_7_hours",
        note=(
            "24/7 regime from Friday 2026-05-29 16:00 CT (CME press releases of 2026-02-19 and "
            "2026-06-01; the release of 2026-06-01: 'The expanded trading hours, which went live "
            "on Friday, May 29'). Maintenance windows as CME states them: 'Monday through Friday: "
            "4:00 p.m. to 4:02 p.m. CT (pre-open: 4:01 p.m. to 4:02 p.m. CT) Saturday: 2:00 a.m. "
            "to 4:00 a.m. CT (pre-open: 3:45 a.m. to 4:00 a.m. CT)'. Weekend and holiday rule as "
            "CME states it: 'All holiday or weekend trading from Friday evening through Sunday "
            "evening will have a trade date of the following business day, with clearing, "
            "settlement and regulatory reporting processed the following business day as well.' "
            "The segments here are a Tuesday-Friday trade date (prior day 16:02 CT to 16:00 CT); "
            "a Monday trade date runs Friday 16:02 CT to Monday 16:00 CT less the Saturday "
            "02:00-04:00 CT maintenance (SEGMENTS_AFTER_WEEKEND_24_7), and after a Friday holiday "
            "from Thursday 16:02 CT ('Friday is a holiday. Therefore, the trade date after the "
            "Thursday maintenance is Monday.'). Day one: the Monday 2026-06-01 session opened "
            "16:30 CT Friday 05-29 (EXTENDED_MAINTENANCE). TopstepX's own session is unchanged "
            "(frozen design D10). " + _D6_NOTE
        ),
    ),
)

SOURCES: dict[date, Citation] = {
    date(2019, 5, 27): Citation(
        _Z19,
        (
            "CME Group Globex Memorial Day Holiday Schedule: May 24, 2019 - May 28, 2019 ... "
            "Trade Date|Friday, May 24|Tuesday, May 28 ... Calendar Date|Friday,May 24|Sunday,May "
            "26 into Monday,May 27|Monday, May 27|Mon,May 27 into Tues,May 28 ... "
            "Product|CLOSE|OPEN|HALT|OPEN ... Bitcoin|Regular @ 1600 CT / 2100 UTC|Regular @ 1700 "
            "CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        _Z19,
        (
            "Product|CLOSE|OPEN|HALT|OPEN ... Bitcoin|Regular @ 1600 CT / 2100 UTC|Regular @ 1700 "
            "CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member "
            "globex-trading-schedules/2019-memorial-day-holiday-schedule-compact.xls of CME's "
            "2019 holiday-calendars.zip (the hash is the zip's). The schedule gives hours per "
            "asset-class row; the crypto row is 'Bitcoin'. Reading: trading halts at 12:00 CT on "
            "Monday May 27 and reopens at the normal 17:00 CT. CME books the halt day's Globex "
            "trading to trade date Tuesday May 28; this module keeps each halt day as its own "
            "short trade date, as data.cme_calendar does."
        ),
    ),
    date(2019, 7, 3): Citation(
        _Z19,
        (
            "CME Group Globex Independence Day Holiday Schedule: July 3, 2019 to July 5, 2019 ... "
            "Trade Date|Wednesday July 3 | Friday July 5 ... Calendar Date|Wednesday July 3 "
            "|Wednesday,July 3|Thursday July 4 |Thursday July 4 into Friday July 5 ... "
            "Product|CLOSE|OPEN|HALT|OPEN ... Bitcoin|Early @ 1215 CT / 1715 UTC|Regular @ 1700 "
            "CT/ 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        _Z19,
        (
            "Product|CLOSE|OPEN|HALT|OPEN ... Bitcoin|Early @ 1215 CT / 1715 UTC|Regular @ 1700 "
            "CT/ 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member "
            "globex-trading-schedules/2019-4th-of-july-holiday-schedule-compact.xls of CME's 2019 "
            "holiday-calendars.zip (the hash is the zip's). The schedule gives hours per "
            "asset-class row; the crypto row is 'Bitcoin'. Reading: early close 12:15 CT on "
            "Wednesday July 3 (the Bitcoin row's CLOSE cell, 'Early @ 1215 CT'), reopen 17:00 CT "
            "for trade date Friday July 5."
        ),
    ),
    date(2019, 7, 4): Citation(
        _Z19,
        (
            "CME Group Globex Independence Day Holiday Schedule: July 3, 2019 to July 5, 2019 ... "
            "Trade Date|Wednesday July 3 | Friday July 5 ... Calendar Date|Wednesday July 3 "
            "|Wednesday,July 3|Thursday July 4 |Thursday July 4 into Friday July 5 ... "
            "Product|CLOSE|OPEN|HALT|OPEN ... Bitcoin|Early @ 1215 CT / 1715 UTC|Regular @ 1700 "
            "CT/ 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        _Z19,
        (
            "Product|CLOSE|OPEN|HALT|OPEN ... Bitcoin|Early @ 1215 CT / 1715 UTC|Regular @ 1700 "
            "CT/ 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member "
            "globex-trading-schedules/2019-4th-of-july-holiday-schedule-compact.xls of CME's 2019 "
            "holiday-calendars.zip (the hash is the zip's). The schedule gives hours per "
            "asset-class row; the crypto row is 'Bitcoin'. Reading: trading halts at 12:00 CT on "
            "Thursday July 4 and reopens at the normal 17:00 CT. Trade date: Friday July 5 per "
            "CME; kept as its own short trade date here."
        ),
    ),
    date(2019, 9, 2): Citation(
        _Z19,
        (
            "CME Group Globex Labor Day Holiday Schedule: August 30, 2019 - September 3, 2019 ... "
            "Trade Date|Friday, August 30|Tuesday, September 3 ... Calendar Date|Friday,August "
            "30|Sunday,Sept 1 into Monday,Sept 2|Monday, Sept 2|Monday, Sept 2 into Tuesday, Sept "
            "3 ... Product|CLOSE|OPEN|HALT|OPEN ... Bitcoin|Regular @ 1600 CT / 2100 UTC|Regular "
            "@ 1700 CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        _Z19,
        (
            "Product|CLOSE|OPEN|HALT|OPEN ... Bitcoin|Regular @ 1600 CT / 2100 UTC|Regular @ 1700 "
            "CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member "
            "globex-trading-schedules/2019-labor-day-holiday-schedule-compact.xls of CME's 2019 "
            "holiday-calendars.zip (the hash is the zip's). The schedule gives hours per "
            "asset-class row; the crypto row is 'Bitcoin'. Reading: trading halts at 12:00 CT on "
            "Monday Sept 2 and reopens at the normal 17:00 CT. Trade date: Tuesday Sept 3 per "
            "CME; kept as its own short trade date here."
        ),
    ),
    date(2019, 11, 28): Citation(
        _Z19,
        (
            "CME Group Globex Thanksgiving Holiday Schedule: November 27, 2019 - November 29, "
            "2019 ... Trade Date|Wednesday ,November 27|| Friday, November 29 ... "
            "Products|Wednesday ,November 27|Wednesday, November 27|Thursday ,November "
            "28|Thursday , November 28|Friday November 29|Friday November 29 ... "
            "CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Bitcoin|Regular @ 1600 CT / 2200 UTC|Regular @ "
            "1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1215 "
            "CT/ 1815 UTC"
        ),
        _Z19,
        (
            "CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Bitcoin|Regular @ 1600 CT / 2200 UTC|Regular @ "
            "1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1215 "
            "CT/ 1815 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member "
            "globex-trading-schedules/2019-thanksgiving-holiday-schedule-compact.xls of CME's "
            "2019 holiday-calendars.zip (the hash is the zip's). The schedule gives hours per "
            "asset-class row; the crypto row is 'Bitcoin'. Reading: trading halts at 12:00 CT on "
            "Thursday November 28 and reopens at the normal 17:00 CT. The third cell of the "
            "Bitcoin row sits under the HALT column (header row "
            "'|CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE')."
        ),
    ),
    date(2019, 11, 29): Citation(
        _Z19,
        (
            "CME Group Globex Thanksgiving Holiday Schedule: November 27, 2019 - November 29, "
            "2019 ... Trade Date|Wednesday ,November 27|| Friday, November 29 ... "
            "Products|Wednesday ,November 27|Wednesday, November 27|Thursday ,November "
            "28|Thursday , November 28|Friday November 29|Friday November 29 ... "
            "CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Bitcoin|Regular @ 1600 CT / 2200 UTC|Regular @ "
            "1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1215 "
            "CT/ 1815 UTC"
        ),
        _Z19,
        (
            "CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Bitcoin|Regular @ 1600 CT / 2200 UTC|Regular @ "
            "1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1215 "
            "CT/ 1815 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member "
            "globex-trading-schedules/2019-thanksgiving-holiday-schedule-compact.xls of CME's "
            "2019 holiday-calendars.zip (the hash is the zip's). The schedule gives hours per "
            "asset-class row; the crypto row is 'Bitcoin'. Reading: early close 12:15 CT on "
            "Friday November 29 (last cell of the Bitcoin row, under the final CLOSE column), "
            "reopen Sunday 17:00 CT."
        ),
    ),
    date(2019, 12, 24): Citation(
        _Z19,
        (
            "CME Group Globex Christmas Holiday Schedule: December 24, 2019 - December 26, 2019 "
            "... Trade Date|Tuesday,December 24|Globex Closed|Thursday December 26 ... "
            "Products|Tuesday, Dec 24|Wednesday,Dec 25|Wednesday December 25|Thursday,Dec "
            "26|Thursday, Dec 26 ... Bitcoin|Early @ 1215 CT / 1815 UTC|Closed for "
            "Christmas|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
        ),
        _Z19,
        (
            "Early Closes|CLOSED|OPEN|Open|CLOSED ... Bitcoin|Early @ 1215 CT / 1815 UTC|Closed "
            "for Christmas|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member "
            "globex-trading-schedules/2019-christmas-holiday-schedule-compact.xls of CME's 2019 "
            "holiday-calendars.zip (the hash is the zip's). The schedule gives hours per "
            "asset-class row; the crypto row is 'Bitcoin'. Reading: early close 12:15 CT on "
            "Tuesday Dec 24 ('Early Closes' column); Globex closed Wednesday Dec 25 until the "
            "17:00 CT reopen."
        ),
    ),
    date(2019, 12, 25): Citation(
        _Z19,
        (
            "CME Group Globex Christmas Holiday Schedule: December 24, 2019 - December 26, 2019 "
            "... Trade Date|Tuesday,December 24|Globex Closed|Thursday December 26 ... "
            "Products|Tuesday, Dec 24|Wednesday,Dec 25|Wednesday December 25|Thursday,Dec "
            "26|Thursday, Dec 26 ... Bitcoin|Early @ 1215 CT / 1815 UTC|Closed for "
            "Christmas|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member "
            "globex-trading-schedules/2019-christmas-holiday-schedule-compact.xls of CME's 2019 "
            "holiday-calendars.zip (the hash is the zip's). The schedule gives hours per "
            "asset-class row; the crypto row is 'Bitcoin'. Reading: 'Closed for Christmas' on "
            "Wednesday Dec 25; reopen 17:00 CT Dec 25 for trade date Thursday Dec 26."
        ),
    ),
    date(2020, 1, 1): Citation(
        _Z19,
        (
            "CME Group Globex New Years Holiday Schedule: December 31, 2019 - January 2, 2020 ... "
            "Trade Date|Tuesday,Dec 31|Globex Closed|Thursday, January 2 ... Calendar "
            "Trade|Tuesday, Dec 31|Wednessday, Jan 1 |Wednesday, Jan 1|Thursday, Jan 2|Thursday, "
            "Jan 2 ... CLOSE|CLOSED |OPEN|Open|CLOSE ... Bitcoin|Regular @ 1600 CT / 2200 "
            "UTC|Closed for New Year's|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member "
            "globex-trading-schedules/2019-new-years-holiday-schedule-compact.xls of CME's 2019 "
            "holiday-calendars.zip (the hash is the zip's). The schedule gives hours per "
            "asset-class row; the crypto row is 'Bitcoin'. Reading: regular 16:00 CT close on "
            "Tuesday Dec 31, 2019; 'Closed for New Year's' on Wednesday Jan 1; reopen 17:00 CT "
            "Jan 1 for trade date Thursday Jan 2."
        ),
    ),
    date(2020, 1, 20): Citation(
        _Z20,
        (
            "CME Group Globex Martin Luther King Day Holiday Schedule: January 17, 2020 - January "
            "21, 2020 ... Trade Date|Friday, Jan 17|Tuesday, Jan 21 ... Calendar Date|Friday, Jan "
            "17|Sunday, Jan 19 into Monday, Jan 20|Monday, Jan 20|Monday, Jan 20 into Tuesday, "
            "Jan 21 ... Products|CLOSE|OPEN|HALT|OPEN ... Bitcoin|Regular @ 1600 CT / 2200 "
            "UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC"
        ),
        _Z20,
        (
            "Products|CLOSE|OPEN|HALT|OPEN ... Bitcoin|Regular @ 1600 CT / 2200 UTC|Regular @ "
            "1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member "
            "2020-martin-luther-king-holiday-schedule-compact.xls of CME's 2020 "
            "holiday-calendars.zip (the hash is the zip's). The schedule gives hours per "
            "asset-class row; the crypto row is 'Bitcoin'. Reading: trading halts at 12:00 CT on "
            "Monday Jan 20 and reopens at the normal 17:00 CT. Trade date: Tuesday Jan 21 per "
            "CME; kept as its own short trade date here."
        ),
    ),
    date(2020, 2, 17): Citation(
        _Z20,
        (
            "CME Group Globex Presidents Day Holiday Schedule: February 14, 2020 - February 18, "
            "2020 ... Trade Date|Friday, Feb 14||Tuesday, February 18 ... Calendar Date|Friday, "
            "Feb 14|Sunday, Feb 16 into Monday, Feb 17|Monday,Feb 17|Monday, Feb 17 into Tuesday, "
            "Feb 18 ... Products|CLOSE|OPEN|HALT|OPEN ... Bitcoin|Regular @ 1600 CT / 2200 "
            "UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC"
        ),
        _Z20,
        (
            "Products|CLOSE|OPEN|HALT|OPEN ... Bitcoin|Regular @ 1600 CT / 2200 UTC|Regular @ "
            "1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member "
            "2020-presidents-day-holiday-schedule-compact.xls of CME's 2020 holiday-calendars.zip "
            "(the hash is the zip's). The schedule gives hours per asset-class row; the crypto "
            "row is 'Bitcoin'. Reading: trading halts at 12:00 CT on Monday Feb 17 and reopens at "
            "the normal 17:00 CT. Trade date: Tuesday Feb 18 per CME; kept as its own short trade "
            "date here."
        ),
    ),
    date(2020, 4, 10): Citation(
        _Z20,
        (
            "CME Group Globex Good Friday Holiday Schedule: April 9,2020 to April 13, 2020 ... "
            "Trade Date|Thursday,April 9|Friday, April 10|Monday, April 13 ... Calendar "
            "Date|Thursday April 9|Friday April 10|Sunday, April 12 into Monday, April 13 ... "
            "Product|CLOSE|CLOSED|OPEN ... Bitcoin|Regular @ 1600 CT / 2100 UTC|Closed for Good "
            "Friday|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member 2020-good-friday-holiday-compact.xls "
            "of CME's 2020 holiday-calendars.zip (the hash is the zip's). The schedule gives "
            "hours per asset-class row; the crypto row is 'Bitcoin'. Reading: regular 16:00 CT "
            "close Thursday April 9; 'Closed for Good Friday' Friday April 10; reopen Sunday "
            "April 12 17:00 CT."
        ),
    ),
    date(2020, 5, 25): Citation(
        _Z20,
        (
            "CME Group Globex Memorial Day Holiday Schedule: May 22, 2020 - May 26, 2020 ... "
            "Trade Date|Friday, May 22|Tuesday, May 26 ... Calendar Date|Friday,May 22|Sunday,May "
            "24 into Monday,May 25|Monday, May 25|Mon,May 25 into Tues,May 26 ... "
            "Product|CLOSE|OPEN|HALT|OPEN ... Bitcoin|Regular @ 1600 CT / 2100 UTC|Regular @ 1700 "
            "CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        _Z20,
        (
            "Product|CLOSE|OPEN|HALT|OPEN ... Bitcoin|Regular @ 1600 CT / 2100 UTC|Regular @ 1700 "
            "CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member "
            "2020-memorial-day-holiday-schedule-compact.xls of CME's 2020 holiday-calendars.zip "
            "(the hash is the zip's). The schedule gives hours per asset-class row; the crypto "
            "row is 'Bitcoin'. Reading: trading halts at 12:00 CT on Monday May 25 and reopens at "
            "the normal 17:00 CT. Trade date: Tuesday May 26 per CME; kept as its own short trade "
            "date here."
        ),
    ),
    date(2020, 7, 3): Citation(
        _Z20,
        (
            "CME Group Globex Independence Day Holiday Schedule: July 2, 2020 to July 6, 2020 ... "
            "Trade Date|Thursday, July 2|Monday, July 6 ... Calendar Date|Thursday July "
            "2|Thursday , July 2|Friday July 3|Sunday July 5 into Monday July 6 ... "
            "Product|CLOSE|OPEN|ClOSE|OPEN ... Bitcoin|Regular @ 1600 CT / 2100 UTC|Regular @ "
            "1700 CT/ 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        _Z20,
        (
            "Product|CLOSE|OPEN|ClOSE|OPEN ... Bitcoin|Regular @ 1600 CT / 2100 UTC|Regular @ "
            "1700 CT/ 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member "
            "2020-4th-of-july-holiday-schedule-compact.xls of CME's 2020 holiday-calendars.zip "
            "(the hash is the zip's). The schedule gives hours per asset-class row; the crypto "
            "row is 'Bitcoin'. Reading: regular close Thursday July 2 16:00 CT, reopen 17:00 CT; "
            "trading stops 12:00 CT Friday July 3 (header cell 'ClOSE' under 'Friday July 3'); "
            "reopen Sunday July 5 17:00 CT. CME books the session to trade date Monday July 6; "
            "kept as its own short trade date here."
        ),
    ),
    date(2020, 9, 7): Citation(
        _Z20,
        (
            "CME Group Globex Labor Day Holiday Schedule: September 4, 2020 - September 8, 2020 "
            "... Trade Date|Friday, September 4|Tuesday, September 8 ... Calendar "
            "Date|Friday,September 4|Sunday,Sept 6 into Monday,Sept 7|Monday, Sept 7|Monday, Sept "
            "7 into Tuesday, Sept 8 ... Product|CLOSE|OPEN|HALT|OPEN ... Bitcoin|Regular @ 1600 "
            "CT / 2100 UTC|Regular @ 1700 CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / "
            "2200 UTC"
        ),
        _Z20,
        (
            "Product|CLOSE|OPEN|HALT|OPEN ... Bitcoin|Regular @ 1600 CT / 2100 UTC|Regular @ 1700 "
            "CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member "
            "2020-labor-day-holiday-schedule-compact.xls of CME's 2020 holiday-calendars.zip (the "
            "hash is the zip's). The schedule gives hours per asset-class row; the crypto row is "
            "'Bitcoin'. Reading: trading halts at 12:00 CT on Monday Sept 7 and reopens at the "
            "normal 17:00 CT. Trade date: Tuesday Sept 8 per CME; kept as its own short trade "
            "date here."
        ),
    ),
    date(2020, 11, 26): Citation(
        _Z20,
        (
            "CME Group Globex Thanksgiving Holiday Schedule: November 25, 2020 - November 27, "
            "2020 ... Trade Date|Wednesday ,November 25|| Friday, November 27 ... "
            "Products|Wednesday ,November 25|Wednesday, November 25|Thursday ,November "
            "26|Thursday , November 26|Friday November 27|Friday November 27 ... "
            "CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Bitcoin|Regular @ 1600 CT / 2200 UTC|Regular @ "
            "1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1215 "
            "CT/ 1815 UTC"
        ),
        _Z20,
        (
            "CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Bitcoin|Regular @ 1600 CT / 2200 UTC|Regular @ "
            "1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1215 "
            "CT/ 1815 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member "
            "2020-thanksgiving-holiday-schedule-compact.xls of CME's 2020 holiday-calendars.zip "
            "(the hash is the zip's). The schedule gives hours per asset-class row; the crypto "
            "row is 'Bitcoin'. Reading: trading halts at 12:00 CT on Thursday November 26 and "
            "reopens at the normal 17:00 CT. Third cell of the Bitcoin row, under HALT."
        ),
    ),
    date(2020, 11, 27): Citation(
        _Z20,
        (
            "CME Group Globex Thanksgiving Holiday Schedule: November 25, 2020 - November 27, "
            "2020 ... Trade Date|Wednesday ,November 25|| Friday, November 27 ... "
            "Products|Wednesday ,November 25|Wednesday, November 25|Thursday ,November "
            "26|Thursday , November 26|Friday November 27|Friday November 27 ... "
            "CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Bitcoin|Regular @ 1600 CT / 2200 UTC|Regular @ "
            "1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1215 "
            "CT/ 1815 UTC"
        ),
        _Z20,
        (
            "CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Bitcoin|Regular @ 1600 CT / 2200 UTC|Regular @ "
            "1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1215 "
            "CT/ 1815 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member "
            "2020-thanksgiving-holiday-schedule-compact.xls of CME's 2020 holiday-calendars.zip "
            "(the hash is the zip's). The schedule gives hours per asset-class row; the crypto "
            "row is 'Bitcoin'. Reading: early close 12:15 CT Friday November 27 (last cell, final "
            "CLOSE column), reopen Sunday 17:00 CT."
        ),
    ),
    date(2020, 12, 24): Citation(
        _Z20,
        (
            "CME Group Globex Christmas Holiday Schedule: December 24, 2020 - December 28, 2020 "
            "... Trade Date|Thursday,December 24|Globex Closed|Monday December 28 ... "
            "Products|Thursday, Dec 24|Friday,Dec 25|Sunday 27|Monday,Dec 28|Monday, Dec 28 ... "
            "Bitcoin|Early @ 1215 CT / 1815 UTC|Closed for Christmas|Regular @ 1700 CT / 2300 "
            "UTC||Regular @ 1600 CT / 2200 UTC"
        ),
        _Z20,
        (
            "Early Closes|CLOSED|OPEN|Open|CLOSED ... Bitcoin|Early @ 1215 CT / 1815 UTC|Closed "
            "for Christmas|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member "
            "2020-christmas-holiday-schedule-compact.xls of CME's 2020 holiday-calendars.zip (the "
            "hash is the zip's). The schedule gives hours per asset-class row; the crypto row is "
            "'Bitcoin'. Reading: early close 12:15 CT Thursday Dec 24; closed Friday Dec 25; "
            "reopen Sunday Dec 27 17:00 CT."
        ),
    ),
    date(2020, 12, 25): Citation(
        _Z20,
        (
            "CME Group Globex Christmas Holiday Schedule: December 24, 2020 - December 28, 2020 "
            "... Trade Date|Thursday,December 24|Globex Closed|Monday December 28 ... "
            "Products|Thursday, Dec 24|Friday,Dec 25|Sunday 27|Monday,Dec 28|Monday, Dec 28 ... "
            "Bitcoin|Early @ 1215 CT / 1815 UTC|Closed for Christmas|Regular @ 1700 CT / 2300 "
            "UTC||Regular @ 1600 CT / 2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member "
            "2020-christmas-holiday-schedule-compact.xls of CME's 2020 holiday-calendars.zip (the "
            "hash is the zip's). The schedule gives hours per asset-class row; the crypto row is "
            "'Bitcoin'. Reading: 'Closed for Christmas' Friday Dec 25; reopen Sunday Dec 27 17:00 "
            "CT for trade date Monday Dec 28."
        ),
    ),
    date(2021, 1, 1): Citation(
        _Z20,
        (
            "CME Group Globex New Years Holiday Schedule: December 31, 2020 - January 4, 2021 ... "
            "Trade Date|Thursday,Dec 31|Globex Closed|Monday, January 4 ... Calendar "
            "Trade|Thursday,Dec 31|Friday,Jan 1|Sunday,Jan 3|Monday, Jan 4|Monday, Jan 4 ... "
            "CLOSE|CLOSED |OPEN|OPEN|CLOSE ... Bitcoin|Regular @ 1600 CT / 2200 UTC|Closed for "
            "New Year's|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member "
            "2021-new-years-holiday-schedule-compact.xls of CME's 2020 holiday-calendars.zip (the "
            "hash is the zip's). The schedule gives hours per asset-class row; the crypto row is "
            "'Bitcoin'. Reading: regular 16:00 CT close Thursday Dec 31, 2020; 'Closed for New "
            "Year's' Friday Jan 1; reopen Sunday Jan 3 17:00 CT. (data.cme_calendar grades the "
            "equity entry for this day unverified; this CME schedule covers it for both rows.)"
        ),
    ),
    date(2021, 1, 18): Citation(
        _Z21,
        (
            "CME Group Globex Martin Luther King Day Holiday Schedule: January 15, 2021 - January "
            "19, 2021 ... Trade Date|Friday, Jan 15|Tuesday, Jan 19 ... Calendar Date|Friday, Jan "
            "15|Sunday, Jan 17 into Monday, Jan 18|Monday, Jan 18|Monday, Jan 18 into Tuesday, "
            "Jan 19 ... Products|CLOSE|OPEN|HALT|OPEN ... Bitcoin|Regular @ 1600 CT / 2200 "
            "UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC"
        ),
        _Z21,
        (
            "Products|CLOSE|OPEN|HALT|OPEN ... Bitcoin|Regular @ 1600 CT / 2200 UTC|Regular @ "
            "1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member 2021-mlk-day-schedule-compact.xls of "
            "CME's 2021 holiday-calendars.zip (the hash is the zip's). The schedule gives hours "
            "per asset-class row; the crypto row is 'Bitcoin'. Reading: trading halts at 12:00 CT "
            "on Monday Jan 18 and reopens at the normal 17:00 CT. Trade date: Tuesday Jan 19 per "
            "CME; kept as its own short trade date here."
        ),
    ),
    date(2021, 2, 15): Citation(
        _Z21,
        (
            "CME Group Globex Presidents Day Holiday Schedule: February 12, 2021 - February 16, "
            "2021 ... Trade Date|Friday, Feb 12||Tuesday, February 16 ... Calendar Date|Friday, "
            "Feb 12|Sunday, Feb 14 into Monday, Feb 15|Monday,Feb 15|Monday, Feb 15 into Tuesday, "
            "Feb 16 ... Products|CLOSE|OPEN|HALT|OPEN ... Bitcoin|Regular @ 1600 CT / 2200 "
            "UTC|Regular @ 1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC"
        ),
        _Z21,
        (
            "Products|CLOSE|OPEN|HALT|OPEN ... Bitcoin|Regular @ 1600 CT / 2200 UTC|Regular @ "
            "1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member "
            "2021-presidents-day-holiday-schedule-compact.xls of CME's 2021 holiday-calendars.zip "
            "(the hash is the zip's). The schedule gives hours per asset-class row; the crypto "
            "row is 'Bitcoin'. Reading: trading halts at 12:00 CT on Monday Feb 15 and reopens at "
            "the normal 17:00 CT. Trade date: Tuesday Feb 16 per CME; kept as its own short trade "
            "date here."
        ),
    ),
    date(2021, 4, 2): Citation(
        _Z21,
        (
            "CME Group Globex Good Friday Holiday Schedule: April 1,2021 to April 5, 2021 ... "
            "Trade Date|Thursday,April 1|Friday, April 2|Friday, April 2|Monday, April 5 ... "
            "Calendar Date|Thursday April 1|Thursday,April 1|Friday April 2|Sunday, April 4 into "
            "Monday, April 5 ... Product|CLOSE|OPEN|CLOSED|OPEN ... Bitcoin|Regular @ 1600 CT / "
            "2100 UTC|Regular @ 1700 CT / 2200 UTC|Closed @ 0815 CT / 1315 UTC|Regular @ 1700 CT "
            "/ 2200 UTC"
        ),
        _Z21,
        (
            "Product|CLOSE|OPEN|CLOSED|OPEN ... Bitcoin|Regular @ 1600 CT / 2100 UTC|Regular @ "
            "1700 CT / 2200 UTC|Closed @ 0815 CT / 1315 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member "
            "2021-good-friday-holiday-schedule-compact.xls of CME's 2021 holiday-calendars.zip "
            "(the hash is the zip's). The schedule gives hours per asset-class row; the crypto "
            "row is 'Bitcoin'. Reading: regular close Thursday April 1 16:00 CT, reopen 17:00 CT "
            "for trade date Friday April 2; 'Closed @ 0815 CT' Friday April 2; reopen Sunday "
            "April 4 17:00 CT. CME's 2021 Good Friday clearing advisory: 'Equities (including "
            "Bitcoin and Ether) are open for an abbreviated session on April 2nd, but will not be "
            "settled'."
        ),
    ),
    date(2021, 5, 31): Citation(
        _Z21,
        (
            "CME Group Globex Memorial Day Holiday Schedule: May 28, 2021 - June 1st, 2021 ... "
            "Trade Date|Friday, May 28|Tuesday, June 1 ... Calendar Date|Friday,May 28|Sunday,May "
            "30|Monday, May 31|Monday, May 31 into Tues, June 1 ... Product|CLOSE|OPEN|HALT|OPEN "
            "... Bitcoin|Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT / 2200 UTC|1200 CT / 1700 "
            "UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        _Z21,
        (
            "Product|CLOSE|OPEN|HALT|OPEN ... Bitcoin|Regular @ 1600 CT / 2100 UTC|Regular @ 1700 "
            "CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member "
            "2021-memorial-day-holiday-schedule-compact.xls of CME's 2021 holiday-calendars.zip "
            "(the hash is the zip's). The schedule gives hours per asset-class row; the crypto "
            "row is 'Bitcoin'. Reading: trading halts at 12:00 CT on Monday May 31 and reopens at "
            "the normal 17:00 CT. Trade date: Tuesday June 1 per CME; kept as its own short trade "
            "date here. MBT was listed 2021-05-03, so this is MBT's first holiday."
        ),
    ),
    date(2021, 7, 5): Citation(
        _Z21,
        (
            "CME Group Globex Independence Day Holiday Schedule: July 2, 2021 to July 6, 2021 ... "
            "Trade Date|Friday, July 2|Tuesday, July 6 ... Calendar Date|Friday July 2|Sunday "
            "July 4|Monday July 5|Monday July 5 ... Product|CLOSE|OPEN|HALT|OPEN ... "
            "Bitcoin|Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT/ 2200 UTC|1200 CT / 1700 "
            "UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        _Z21,
        (
            "Product|CLOSE|OPEN|HALT|OPEN ... Bitcoin|Regular @ 1600 CT / 2100 UTC|Regular @ 1700 "
            "CT/ 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member "
            "2021-independence-day-holiday-schedule-compact.xls of CME's 2021 "
            "holiday-calendars.zip (the hash is the zip's). The schedule gives hours per "
            "asset-class row; the crypto row is 'Bitcoin'. Reading: trading halts at 12:00 CT on "
            "Monday July 5 and reopens at the normal 17:00 CT. Trade date: Tuesday July 6 per "
            "CME; kept as its own short trade date here."
        ),
    ),
    date(2021, 9, 6): Citation(
        _Z21,
        (
            "CME Group Globex Labor Day Holiday Schedule: September 3, 2021 - September 7, 2021 "
            "... Trade Date|Friday, September 3|Tuesday, September 7 ... Calendar "
            "Date|Friday,September 3|Sunday,Sept 5 into Monday,Sept 6|Monday, Sept 6|Monday, Sept "
            "6 into Tuesday, Sept 7 ... Product|CLOSE|OPEN|HALT|OPEN ... Bitcoin|Regular @ 1600 "
            "CT / 2100 UTC|Regular @ 1700 CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / "
            "2200 UTC"
        ),
        _Z21,
        (
            "Product|CLOSE|OPEN|HALT|OPEN ... Bitcoin|Regular @ 1600 CT / 2100 UTC|Regular @ 1700 "
            "CT / 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member "
            "2021-labor-day-holiday-schedule-compact.xls of CME's 2021 holiday-calendars.zip (the "
            "hash is the zip's). The schedule gives hours per asset-class row; the crypto row is "
            "'Bitcoin'. Reading: trading halts at 12:00 CT on Monday Sept 6 and reopens at the "
            "normal 17:00 CT. Trade date: Tuesday Sept 7 per CME; kept as its own short trade "
            "date here."
        ),
    ),
    date(2021, 11, 25): Citation(
        _Z21,
        (
            "CME Group Globex Thanksgiving Holiday Schedule: November 24, 2021 - November 26, "
            "2021 ... Trade Date|Wednesday ,November 24|| Friday, November 26 ... "
            "Products|Wednesday ,November 24|Wednesday, November 24|Thursday ,November "
            "25|Thursday , November 25|Friday November 26|Friday November 26 ... "
            "CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Bitcoin|Regular @ 1600 CT / 2200 UTC|Regular @ "
            "1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1245 "
            "CT/ 1845 UTC"
        ),
        _Z21,
        (
            "CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Bitcoin|Regular @ 1600 CT / 2200 UTC|Regular @ "
            "1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1245 "
            "CT/ 1845 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member "
            "2021-thanksgiving-holiday-schedule-compact.xls of CME's 2021 holiday-calendars.zip "
            "(the hash is the zip's). The schedule gives hours per asset-class row; the crypto "
            "row is 'Bitcoin'. Reading: trading halts at 12:00 CT on Thursday November 25 and "
            "reopens at the normal 17:00 CT. Third cell of the Bitcoin row, under HALT."
        ),
    ),
    date(2021, 11, 26): Citation(
        _Z21,
        (
            "CME Group Globex Thanksgiving Holiday Schedule: November 24, 2021 - November 26, "
            "2021 ... Trade Date|Wednesday ,November 24|| Friday, November 26 ... "
            "Products|Wednesday ,November 24|Wednesday, November 24|Thursday ,November "
            "25|Thursday , November 25|Friday November 26|Friday November 26 ... "
            "CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Bitcoin|Regular @ 1600 CT / 2200 UTC|Regular @ "
            "1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1245 "
            "CT/ 1845 UTC"
        ),
        _Z21,
        (
            "CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Bitcoin|Regular @ 1600 CT / 2200 UTC|Regular @ "
            "1700 CT / 2300 UTC|1200 CT / 1800 UTC|Regular @ 1700 CT / 2300 UTC|| Early @ 1245 "
            "CT/ 1845 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member "
            "2021-thanksgiving-holiday-schedule-compact.xls of CME's 2021 holiday-calendars.zip "
            "(the hash is the zip's). The schedule gives hours per asset-class row; the crypto "
            "row is 'Bitcoin'. Reading: early close 12:45 CT Friday November 26 (last cell, final "
            "CLOSE column; the Equity row closes 12:15 CT that day), reopen Sunday 17:00 CT. "
            "First year the crypto early close differs from equity's."
        ),
    ),
    date(2021, 12, 24): Citation(
        _Z21,
        (
            "CME Group Globex Christmas Holiday Schedule: December 23, 2021 - December 27, 2021 "
            "... Trade Date|Thursday,December 23|Globex Closed|Monday December 27 ... "
            "Products|Thursday, Dec 23|Friday,Dec 24|Sunday 26|Monday,Dec 27 ... Bitcoin|Regular "
            "per Product|Closed for Christmas|Regular @ 1700 CT / 2300 UTC|Regular @ 1600 CT / "
            "2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member "
            "2021-christmas-holiday-schedule-compact.xls of CME's 2021 holiday-calendars.zip (the "
            "hash is the zip's). The schedule gives hours per asset-class row; the crypto row is "
            "'Bitcoin'. Reading: Thursday Dec 23 'Regular per Product' close; 'Closed for "
            "Christmas' Friday Dec 24; reopen Sunday Dec 26 17:00 CT for trade date Monday Dec 27."
        ),
    ),
    date(2022, 4, 15): Citation(
        _HC + "2022-good-friday-holiday-schedule-compact.xls",
        (
            "CME Group Globex Good Friday Holiday Schedule: April 14,2022 to April 18, 2022 ... "
            "Trade Date|Thursday,April 14|Friday, April 15|Monday, April 18 ... Calendar "
            "Date|Thursday April 14|Friday April 15|Sunday, April 17 into Monday, April 18 ... "
            "Product|CLOSE|CLOSED|OPEN ... Cryptocurrency|Regular @ 1600 CT / 2100 UTC|Closed for "
            "Good Friday|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule (.xls). The schedule gives hours per "
            "asset-class row; the crypto row is 'Cryptocurrency'. Reading: regular 16:00 CT close "
            "Thursday April 14; 'Closed for Good Friday' Friday April 15; reopen Sunday April 17 "
            "17:00 CT."
        ),
    ),
    date(2022, 11, 25): Citation(
        _HC + "2022-thanksgiving-holiday-schedule-compact.xls",
        (
            "CME Group Globex Thanksgiving Holiday Schedule: November 23, 2022 - November 25, "
            "2022 ... Trade Date|Wednesday ,November 23|| Friday, November 25 ... "
            "Products|Wednesday ,November 23|Wednesday, November 23|Thursday ,November "
            "24|Thursday , November 24|Friday November 25|Friday November 25 ... "
            "CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Cryptocurrency |Regular @ 1600 CT / 2200 "
            "UTC|Regular @ 1700 CT / 2300 UTC|1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|| "
            "Early @ 1245 CT/ 1845 UTC"
        ),
        _HC + "2022-thanksgiving-holiday-schedule-compact.xls",
        (
            "CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Cryptocurrency |Regular @ 1600 CT / 2200 "
            "UTC|Regular @ 1700 CT / 2300 UTC|1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|| "
            "Early @ 1245 CT/ 1845 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule (.xls). The schedule gives hours per "
            "asset-class row; the crypto row is 'Cryptocurrency'. Reading: early close 12:45 CT "
            "Friday November 25 (last cell of the Cryptocurrency row, final CLOSE column), reopen "
            "Sunday 17:00 CT."
        ),
    ),
    date(2022, 12, 26): Citation(
        _HC + "2022-christmas-holiday-schedule.xls",
        (
            "Updated 6/29/2022|CME Group Globex Christmas Holiday Schedule: December 23, 2022 - "
            "December 27, 2022 ... Trade Date|Friday, December 23|||||Tuesday, December 27 ... "
            "Calendar Date|Friday, December 23||||||||Monday, December 26||||||||||||||||Tuesday, "
            "December 27 ... Cryptocurrency|04:00:00 PM||||||||Globex Closed||||||||||04:00:00 "
            "PM|05:00:00 PM|||||||04:00:00 PM"
        ),
        note=(
            "CME's full Globex holiday schedule (.xls). The schedule gives hours per asset-class "
            "row; the crypto row is 'Cryptocurrency'. Reading: Friday Dec 23 close 04:00:00 PM "
            "(16:00 CT, the regular close); 'Globex Closed' in the Monday December 26 block; "
            "reopen Monday Dec 26 05:00:00 PM (17:00 CT) for trade date Tuesday Dec 27. Cells are "
            "LibreOffice's rendering of the sheet's time values."
        ),
    ),
    date(2023, 1, 2): Citation(
        _HC + "2023-new-years-holiday-schedule-compact.xls",
        (
            "CME Group Globex New Years Holiday Schedule: December 30, 2022 - January 3, 2023 ... "
            "Trade Date|Friday,Dec 30|Sunday, January 1 and Monday, January 2|| Tuesday, January "
            "3 ... Calendar Trade|Friday,Dec 30|Sunday, Jan 1 and Monday, Jan 2|Monday,Jan "
            "2|Tuesday, Jan 3|Tuesday, Jan 3 ... CLOSE|Closed|OPEN|OPEN|CLOSE ... "
            "Cryptocurrency|Regular @ 1600 CT / 2200 UTC|Globex Closed|Regular @ 1700 CT / 2300 "
            "UTC||Regular @ 1600 CT / 2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule (.xls). The schedule gives hours per "
            "asset-class row; the crypto row is 'Cryptocurrency'. Reading: regular 16:00 CT close "
            "Friday Dec 30, 2022; 'Globex Closed' Sunday Jan 1 and Monday Jan 2; reopen Monday "
            "Jan 2 17:00 CT for trade date Tuesday Jan 3."
        ),
    ),
    date(2023, 4, 7): Citation(
        _FILES + "good-friday.pdf",
        (
            "PRODUCT NAME THURSDAY, 6 APR 2023 FRIDAY, 7 APR 2023 ... TRADE DATE: THURS 6 APR "
            "16:00 ( CLOSED) TRADE DATE: FRI 7 APR CRYPTOCURRENCIES TRADE DATE: FRI 7 APR 10:00 "
            "(TAS CLOSE) 16:45 (PREOPEN) 10:15 (CLOSED) 17:00 (OPEN)"
        ),
        _FILES + "good-friday.pdf",
        (
            "CRYPTOCURRENCIES TRADE DATE: FRI 7 APR 10:00 (TAS CLOSE) 16:45 (PREOPEN) 10:15 "
            "(CLOSED)"
        ),
        note=(
            "CME's holiday trading-hours summary PDF, row CRYPTOCURRENCIES ('the most actively "
            "traded instruments for each asset class'); pdftotext -layout interleaves the table "
            "columns, so each quoted run mixes cells of adjacent columns. Original "
            "https://www.cmegroup.com/files/good-friday.pdf (CME's Good Friday 2023 summary). "
            "Reading: Thursday April 6 close 16:00 CT, pre-open 16:45, open 17:00 CT for trade "
            "date Friday April 7; TAS closes 10:00 CT and the market closes 10:15 CT Friday; "
            "reopen Sunday 17:00 CT. The Equities row closes 08:15 CT the same day. CME's 2023 "
            "Good Friday clearing advisory: 'Equities (including Bitcoin and Ether) are open for "
            "an abbreviated session on April 7th'; its settlement notice gives 'CME Group FX and "
            "Cryptocurrency Products 10:00 am CT'."
        ),
    ),
    date(2023, 11, 24): Citation(
        _TH + "thanksgiving-day-2023.pdf",
        (
            "PRODUCT NAME WEDNESDAY, 22 NOVEMBER 2023 THURSDAY, 23 NOVEMBER 2023 FRIDAY, 24 "
            "NOVEMBER 2023 ... CRYPTOCURRENCIES TRADE DATE: FRI 24 NOV 16:00 (PREOPEN) 12:45 "
            "(CLOSED) 16:45 (PREOPEN) 17:00 (OPEN) 17:00 (OPEN)"
        ),
        _TH + "thanksgiving-day-2023.pdf",
        "CRYPTOCURRENCIES TRADE DATE: FRI 24 NOV 16:00 (PREOPEN) 12:45 (CLOSED)",
        note=(
            "CME's holiday trading-hours summary PDF, row CRYPTOCURRENCIES ('the most actively "
            "traded instruments for each asset class'); pdftotext -layout interleaves the table "
            "columns, so each quoted run mixes cells of adjacent columns. Reading: Wednesday Nov "
            "22 close 16:00, open 17:00 CT for trade date Friday Nov 24; Thursday Nov 23 halt at "
            "the regular 16:00 CT ('16:00 (PREOPEN)') and reopen 17:00 CT; Friday Nov 24 closes "
            "12:45 CT. The service capture of 2024-07-08 (fromEventDate 2023-11-22) gives the "
            "same 12:45 close."
        ),
    ),
    date(2023, 12, 25): Citation(
        _svc("2023-12-24", "2023-12-26", "1720455278659"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2023-12-24","events":[]} ... '
            '{"groupCode":"BF","eventDate":"2023-12-25","events":[{"tradingDate":"2023-12-26","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2023-12-26","eventTime":'
            '"17:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20240708. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "Reading: no Sunday Dec 24 open; Monday Dec 25 pre-open 16:00 and open 17:00 CT for "
            "trade date Dec 26, so Globex is closed until 17:00 CT Dec 25. CME's Christmas 2023 "
            "summary PDF (trading-hours/files/christmas-day-2023.pdf) shows the same "
            "CRYPTOCURRENCIES '16:00 (PREOPEN) ... 17:00 (OPEN)' for Monday Dec 25."
        ),
    ),
    date(2024, 1, 1): Citation(
        _svc("2023-12-31", "2024-01-02", "1720455278661"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2023-12-31","events":[]} ... '
            '{"groupCode":"BF","eventDate":"2024-01-01","events":[{"tradingDate":"2024-01-02","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2024-01-02","eventTime":'
            '"17:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20240708. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "Reading: no Sunday Dec 31 open; Monday Jan 1 pre-open 16:00 and open 17:00 CT for "
            "trade date Jan 2, so Globex is closed until 17:00 CT Jan 1. CME's New Year 2024 "
            "summary PDF (trading-hours/files/new-years-day-2024.pdf) shows the same."
        ),
    ),
    date(2024, 3, 29): Citation(
        _svc("2024-03-28", "2024-03-30", "1720455278672"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2024-03-28","events":[{"tradingDate":"2024-03-28","eve'
            'ntTime":"16:00","marketEventType":"closed"}]} ... '
            '{"groupCode":"BF","eventDate":"2024-03-29","events":[]} ... '
            '{"groupCode":"BF","eventDate":"2024-03-30","events":[]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20240708. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "Reading: Thursday March 28 final close 16:00 CT with no 17:00 reopen; no events on "
            "Friday March 29 or Saturday; Globex closed on Good Friday."
        ),
    ),
    date(2024, 11, 29): Citation(
        _svc("2024-11-27", "2024-11-29", "1734710019535"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2024-11-27","events":[{"tradingDate":"2024-11-27","eve'
            'ntTime":"16:00","marketEventType":"closed"},{"tradingDate":"2024-11-29","eventTime":"'
            '16:45","marketEventType":"preopen"},{"tradingDate":"2024-11-29","eventTime":"17:00","'
            'marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2024-11-28","events":[{"tradingDate":"2024-11-29","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2024-11-29","eventTime":'
            '"17:00","marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2024-11-29","events":[{"tradingDate":"2024-11-29","eve'
            'ntTime":"13:45","marketEventType":"closed"}]}'
        ),
        _svc("2024-11-27", "2024-11-29", "1734710019535"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2024-11-29","events":[{"tradingDate":"2024-11-29","eve'
            'ntTime":"13:45","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20241220. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "Reading: Wed Nov 27 close 16:00, open 17:00 CT for trade date Nov 29; Thanksgiving "
            "Nov 28 halts at the regular 16:00 CT and reopens 17:00 CT; Friday Nov 29 closes "
            "13:45 CT. CONFLICT: the earlier capture of 2024-07-08 (same request, "
            "_t=1720455278685) gave '12:45' for BTC on 2024-11-29; this capture (2024-12-20, "
            "after the date) gives '13:45', and CL, GC and 6E moved from 12:45/12:15 to 13:45 "
            "between the two captures. The later capture is encoded. CME's 2024 Thanksgiving "
            "settlement notice gives 'Equity & Crypto Products Settlement Time: 12:00:00 CT' for "
            "that Friday. Holdout-2 date: never checkable against bars; 2025-11-28 (same 13:45) "
            "is checked in Task 7."
        ),
    ),
    date(2024, 12, 24): Citation(
        _svc("2024-12-24", "2024-12-26", "1734710019537"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2024-12-24","events":[{"tradingDate":"2024-12-24","eve'
            'ntTime":"12:45","marketEventType":"closed"}]}'
        ),
        _svc("2024-12-24", "2024-12-26", "1734710019537"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2024-12-24","events":[{"tradingDate":"2024-12-24","eve'
            'ntTime":"12:45","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20241220. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "Reading: Tuesday Dec 24 final close 12:45 CT (the 2024-07-08 capture agrees); Globex "
            "closed until 17:00 CT Dec 25."
        ),
    ),
    date(2024, 12, 25): Citation(
        _svc("2024-12-24", "2024-12-26", "1734710019537"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2024-12-24","events":[{"tradingDate":"2024-12-24","eve'
            'ntTime":"12:45","marketEventType":"closed"}]} ... '
            '{"groupCode":"BF","eventDate":"2024-12-25","events":[{"tradingDate":"2024-12-26","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2024-12-26","eventTime":'
            '"17:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20241220. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "Reading: Dec 24 closes 12:45 CT with no reopen that evening; Wednesday Dec 25 "
            "pre-open 16:00 and open 17:00 CT for trade date Dec 26."
        ),
    ),
    date(2025, 1, 1): Citation(
        _svc("2024-12-31", "2025-01-02", "1734710019538"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2024-12-31","events":[{"tradingDate":"2024-12-31","eve'
            'ntTime":"16:00","marketEventType":"closed"}]} ... '
            '{"groupCode":"BF","eventDate":"2025-01-01","events":[{"tradingDate":"2025-01-02","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2025-01-02","eventTime":'
            '"17:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20241220. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "Reading: Tuesday Dec 31 final close 16:00 CT with no reopen; Wednesday Jan 1 "
            "pre-open 16:00 and open 17:00 CT for trade date Jan 2."
        ),
    ),
    date(2025, 4, 18): Citation(
        _svc("2025-04-17", "2025-04-19", "1734710019542"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2025-04-17","events":[{"tradingDate":"2025-04-17","eve'
            'ntTime":"16:00","marketEventType":"closed"}]} ... '
            '{"groupCode":"BF","eventDate":"2025-04-18","events":[]} ... '
            '{"groupCode":"BF","eventDate":"2025-04-19","events":[]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20241220. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "Reading: Thursday April 17 final close 16:00 CT with no reopen; no events Friday "
            "April 18 or Saturday; Globex closed on Good Friday."
        ),
    ),
    date(2025, 7, 4): Citation(
        _svc("2025-07-03", "2025-07-05", "1734710019545"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2025-07-03","events":[{"tradingDate":"2025-07-03","eve'
            'ntTime":"16:00","marketEventType":"closed"},{"tradingDate":"2025-07-04","eventTime":"'
            '16:45","marketEventType":"preopen"},{"tradingDate":"2025-07-04","eventTime":"17:00","'
            'marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2025-07-04","events":[{"tradingDate":"2025-07-04","eve'
            'ntTime":"12:00","marketEventType":"closed"}]}'
        ),
        _svc("2025-07-03", "2025-07-05", "1734710019545"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2025-07-04","events":[{"tradingDate":"2025-07-04","eve'
            'ntTime":"12:00","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20241220. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "Reading: Thursday July 3 close 16:00 CT (regular), open 17:00 CT for trade date July "
            "4; Friday July 4 final close 12:00 CT; reopen Sunday 17:00 CT. Here CME keeps July 4 "
            "as its own trade date. Capture of 2024-12-20 (the published plan)."
        ),
    ),
    date(2025, 11, 28): Citation(
        _svc("2025-11-26", "2025-11-28", "1769649703060"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2025-11-26","events":[{"tradingDate":"2025-11-26","eve'
            'ntTime":"16:00","marketEventType":"closed"},{"tradingDate":"2025-11-28","eventTime":"'
            '16:45","marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"17:00","'
            'marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2025-11-27","events":[{"tradingDate":"2025-11-28","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":'
            '"17:00","marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28","eve'
            'ntTime":"07:00","marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":'
            '"07:30","marketEventType":"open"},{"tradingDate":"2025-11-28","eventTime":"13:45","ma'
            'rketEventType":"closed"}]}'
        ),
        _svc("2025-11-26", "2025-11-28", "1769649703060"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28","eve'
            'ntTime":"07:00","marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":'
            '"07:30","marketEventType":"open"},{"tradingDate":"2025-11-28","eventTime":"13:45","ma'
            'rketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20260129. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "Reading: Wed Nov 26 close 16:00, open 17:00 CT for trade date Nov 28; Thanksgiving "
            "Nov 27 halts at the regular 16:00 CT and reopens 17:00 CT; Friday Nov 28 closes "
            "13:45 CT (the 2024-12-20 capture, the plan, has only '13:45 closed'). This capture "
            "also records the delayed 07:30 CT open after the CME outage: LATE_OPENS. CME's 2025 "
            "Thanksgiving settlement notice: 'Equity & Crypto Products Settlement Time: 12:00:00 "
            "CT'."
        ),
    ),
    date(2025, 12, 24): Citation(
        _svc("2025-12-24", "2025-12-26", "1769649703064"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2025-12-24","events":[{"tradingDate":"2025-12-24","eve'
            'ntTime":"12:45","marketEventType":"closed"}]}'
        ),
        _svc("2025-12-24", "2025-12-26", "1769649703064"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2025-12-24","events":[{"tradingDate":"2025-12-24","eve'
            'ntTime":"12:45","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20260129. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "Reading: Wednesday Dec 24 final close 12:45 CT; Globex closed until 17:00 CT Dec 25. "
            "(The 2024-12-20 capture had no events yet for these dates.)"
        ),
    ),
    date(2025, 12, 25): Citation(
        _svc("2025-12-24", "2025-12-26", "1769649703064"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2025-12-24","events":[{"tradingDate":"2025-12-24","eve'
            'ntTime":"12:45","marketEventType":"closed"}]} ... '
            '{"groupCode":"BF","eventDate":"2025-12-25","events":[{"tradingDate":"2025-12-26","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2025-12-26","eventTime":'
            '"17:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20260129. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "Reading: Dec 24 closes 12:45 CT with no reopen that evening; Thursday Dec 25 "
            "pre-open 16:00 and open 17:00 CT for trade date Dec 26."
        ),
    ),
    date(2026, 1, 1): Citation(
        _svc("2025-12-31", "2026-01-02", "1769649703066"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2025-12-31","events":[{"tradingDate":"2025-12-31","eve'
            'ntTime":"16:00","marketEventType":"closed"}]} ... '
            '{"groupCode":"BF","eventDate":"2026-01-01","events":[{"tradingDate":"2026-01-02","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2026-01-02","eventTime":'
            '"17:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20260129. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "Reading: Wednesday Dec 31 final close 16:00 CT with no reopen; Thursday Jan 1 "
            "pre-open 16:00 and open 17:00 CT for trade date Jan 2."
        ),
    ),
    date(2026, 4, 3): Citation(
        _HC + "2026/2026-good-friday-clearing-advisory.pdf",
        (
            "Equities (including Bitcoin and Ether) are open for an abbreviated session on April "
            "3rd, but will not be settled and will use the April 2nd end of day settlement for "
            "mark to market."
        ),
        _svc("2026-04-01", "2026-04-03", "1743113432016"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2026-04-02","events":[{"tradingDate":"2026-04-02","eve'
            'ntTime":"16:00","marketEventType":"closed"},{"tradingDate":"2026-04-03","eventTime":"'
            '16:45","marketEventType":"preopen"},{"tradingDate":"2026-04-03","eventTime":"17:00","'
            'marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2026-04-03","events":[{"tradingDate":"2026-04-03","eve'
            'ntTime":"10:15","marketEventType":"closed"}]}'
        ),
        note=(
            "Status: CME's 2026 Good Friday clearing advisory (the zero-width characters in the "
            "PDF text are removed by the normalization). Time: CME's trading-hours-by-product "
            "service behind cmegroup.com/trading-hours.html, product 8478 'Bitcoin Futures' "
            "(groupCode BF), Wayback capture 20260610. BTC stands for MBT: CME derives MBT's "
            "daily settlement from BTC and its holiday schedules list one crypto row. 'preopen' "
            "at a time = trading stops (order entry only) until the next 'open'; 'closed' = final "
            "close of a trade date; tradingDate = CME trade date. Reading: Thursday April 2 close "
            "16:00, open 17:00 CT for trade date April 3; Friday April 3 final close 10:15 CT (ES "
            "closes 08:15 CT in the same record); reopen Sunday 17:00 CT. The 2026-01-29 capture "
            "gives the same 10:15."
        ),
    ),
}

LATE_OPEN_SOURCES: dict[date, Citation] = {
    date(2025, 11, 28): Citation(
        _CME_10K,
        (
            "On November 27, 2025, our largest data center owned and operated by CyrusOne "
            "experienced a critical cooling failure caused by human error. In response to the "
            "critical cooling failure, we made the decision to temporarily halt our markets. Our "
            "markets opened the following day on a delayed basis."
        ),
        _svc("2025-11-26", "2025-11-28", "1769649703060"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28","eve'
            'ntTime":"07:00","marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":'
            '"07:30","marketEventType":"open"},{"tradingDate":"2025-11-28","eventTime":"13:45","ma'
            'rketEventType":"closed"}]}'
        ),
        note=(
            "Unscheduled. Status: CME Group's 2025 Form 10-K (SEC EDGAR, Wayback capture; file "
            "shared with the energy builder). Open time: CME's trading-hours-by-product service "
            "behind cmegroup.com/trading-hours.html, product 8478 'Bitcoin Futures' (groupCode "
            "BF), Wayback capture 20260129. BTC stands for MBT: CME derives MBT's daily "
            "settlement from BTC and its holiday schedules list one crypto row. 'preopen' at a "
            "time = trading stops (order entry only) until the next 'open'; 'closed' = final "
            "close of a trade date; tradingDate = CME trade date. The 2026-01-29 capture adds "
            "'07:00 preopen' and '07:30 open' on 2025-11-28 before the 13:45 close; the "
            "2024-12-20 capture (the plan) has only the close. The time trading stopped on the "
            "evening of 2025-11-27 is in no CME document retrieved (halt_from_ct None)."
        ),
    ),
}

EXTENDED_MAINTENANCE_SOURCES: dict[date, Citation] = {
    date(2026, 6, 1): Citation(
        _WIKI_247,
        (
            "For the first day of 24/7 cryptocurrency futures and options trading (Friday, May "
            "29, 2026) the standard daily maintenance of two minutes will be extended to 30 "
            "minutes (4:00 p.m. to 4:30:00 p.m. CT)."
        ),
        _WIKI_247,
        (
            "Friday, May 29, 2026 Day One Extended Maintenance Close: 4:00 p.m. to 4:02 p.m. CT "
            "Pre-open: Following the Close and concluded with a 30 second No Cancel period. No "
            "cancel: 4:29:30 p.m. to 4:30:00 p.m. CT Open: 4:30 p.m. CT"
        ),
        note=(
            "CME client systems wiki page 'Cryptocurrency Futures and Options Migration to 24-7 "
            "Trading' (page 1283194884, version of 2026-08-14, read through the Confluence REST "
            "API). Trade date Monday 2026-06-01 is the first 24/7 trade date: its session starts "
            "after the Friday 2026-05-29 16:00 CT close of trade date 05-29 (offset -3 days). The "
            "regular 24/7 restart is 16:02 CT; on day one it was 16:30 CT. open_offset_days = -3 "
            "(Friday)."
        ),
    ),
}

BOOKED_FORWARD_SOURCES: dict[date, Citation] = {
    date(2022, 1, 17): Citation(
        _HC + "2022-mlk-day-holiday-schedule-compact.xls",
        (
            "CME Group Globex Martin Luther King Day Holiday Schedule: January 14, 2022 - January "
            "18, 2022 ... Trade Date|Friday, Jan 14|Tuesday, Jan 18 ... Calendar Date|Friday, Jan "
            "14|Sunday, Jan 16 into Monday, Jan 17|Monday, Jan 17|Monday, Jan 17 into Tuesday, "
            "Jan 18 ... Products|CLOSE|OPEN|HALT|OPEN ... Cryptocurrency|Regular @ 1600 CT / 2200 "
            "UTC|Regular @ 1700 CT / 2300 UTC|1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule (.xls). The schedule gives hours per "
            "asset-class row; the crypto row is 'Cryptocurrency'. Reading: crypto trades its "
            "regular hours on Monday Jan 17 (halt only at the regular 16:00 CT break, reopen "
            "17:00 CT); CME books the day's Globex trading to trade date Tuesday Jan 18 (no "
            "Monday Jan 17 settlement). Not a HOLIDAYS entry: the clock session is regular. The "
            "HALT cell of the Cryptocurrency row is '1600 CT' where the Equity and Interest Rate "
            "rows halt at '1200 CT'."
        ),
    ),
    date(2022, 2, 21): Citation(
        _HC + "2022-presidents-day-holiday-schedule-compact.xls",
        (
            "CME Group Globex Presidents Day Holiday Schedule: February 18, 2022 - February 22, "
            "2022 ... Trade Date|Friday, Feb 18||Tuesday, February 22 ... Calendar Date|Friday, "
            "Feb 18|Sunday, Feb 20 into Monday, Feb 21|Monday,Feb 21|Monday, Feb 21 into Tuesday, "
            "Feb 22 ... Products|CLOSE|OPEN|HALT|OPEN ... Cryptocurrency|Regular @ 1600 CT / 2200 "
            "UTC|Regular @ 1700 CT / 2300 UTC|1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule (.xls). The schedule gives hours per "
            "asset-class row; the crypto row is 'Cryptocurrency'. Reading: crypto trades its "
            "regular hours on Monday Feb 21 (halt only at the regular 16:00 CT break, reopen "
            "17:00 CT); CME books the day's Globex trading to trade date Tuesday Feb 22 (no "
            "Monday Feb 21 settlement). Not a HOLIDAYS entry: the clock session is regular. The "
            "HALT cell of the Cryptocurrency row is '1600 CT' where the Equity and Interest Rate "
            "rows halt at '1200 CT'."
        ),
    ),
    date(2022, 5, 30): Citation(
        _HC + "2022-memorial-day-holiday-schedule.xls",
        (
            "Updated 5/18/2022|CME Group Globex Memorial Day Holiday Schedule: May 27, 2022 - May "
            "31, 2022 ... Trade Date|Friday, May 27||Tuesday, May 31 ... Calendar Date|Friday, "
            "May 27|||||Sunday, May 29|||||Monday, May 30||||||||||Tuesday, May 31 ... Equity "
            "Products|04:00:00 PM|||||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM||||12:00:00 "
            "PM|05:00:00 PM ... Cryptocurrency|04:00:00 PM|||||04:00:00 PM|05:00:00 "
            "PM|||||||04:00:00 PM||||04:00:00 PM|05:00:00 PM"
        ),
        note=(
            "CME's full Globex holiday schedule (.xls). The schedule gives hours per asset-class "
            "row; the crypto row is 'Cryptocurrency'. Reading: crypto trades its regular hours on "
            "Monday May 30 (halt only at the regular 16:00 CT break, reopen 17:00 CT); CME books "
            "the day's Globex trading to trade date Tuesday May 31 (no Monday May 30 settlement). "
            "Not a HOLIDAYS entry: the clock session is regular. In the Monday block the "
            "Cryptocurrency row has 04:00:00 PM (16:00 CT) where the Equity Products row has "
            "12:00:00 PM, and both reopen 05:00:00 PM (17:00 CT). Cells are LibreOffice's "
            "rendering of the sheet's time values."
        ),
    ),
    date(2022, 6, 20): Citation(
        _HC + "2022-juneteenth-holiday-schedule.xls",
        (
            "Updated 5/18/2022|CME Group Globex Juneteenth Holiday Schedule: June 17, 2022 - Jun "
            "21, 2022 ... Trade Date|Friday, June 17||Tuesday, Jun 21 ... Calendar Date|Friday, "
            "June 17|||||Sunday, June 19|||||Monday, June 20||||||||||Tuesday, Jun 21 ... Equity "
            "Products|04:00:00 PM|||||04:00:00 PM|05:00:00 PM|||||||12:00:00 PM|12:00:00 "
            "PM||||05:00:00 PM ... Cryptocurrency|04:00:00 PM|||||04:00:00 PM|05:00:00 "
            "PM||||||||||04:00:00 PM|04:00:00 PM|05:00:00 PM"
        ),
        note=(
            "CME's full Globex holiday schedule (.xls). The schedule gives hours per asset-class "
            "row; the crypto row is 'Cryptocurrency'. Reading: crypto trades its regular hours on "
            "Monday June 20 (halt only at the regular 16:00 CT break, reopen 17:00 CT); CME books "
            "the day's Globex trading to trade date Tuesday Jun 21 (no Monday June 20 "
            "settlement). Not a HOLIDAYS entry: the clock session is regular. In the Monday block "
            "the Cryptocurrency row has 04:00:00 PM (16:00 CT) where the Equity Products row has "
            "12:00:00 PM, and both reopen 05:00:00 PM (17:00 CT). Cells are LibreOffice's "
            "rendering of the sheet's time values."
        ),
    ),
    date(2022, 7, 4): Citation(
        _HC + "2022-independence-day-holiday-schedule-compact.xls",
        (
            "CME Group Globex Independence Day Holiday Schedule: July 1, 2022 to July 5, 2022 ... "
            "Trade Date|Friday, July 1|Tuesday, July 5 ... Calendar Date|Friday July 1|Sunday "
            "July 3|Monday July 4|Monday July 4 ... Product|CLOSE|OPEN|HALT|OPEN ... "
            "Cryptocurrency|Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT/ 2200 UTC|1600 CT / "
            "2100 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule (.xls). The schedule gives hours per "
            "asset-class row; the crypto row is 'Cryptocurrency'. Reading: crypto trades its "
            "regular hours on Monday July 4 (halt only at the regular 16:00 CT break, reopen "
            "17:00 CT); CME books the day's Globex trading to trade date Tuesday July 5 (no "
            "Monday July 4 settlement). Not a HOLIDAYS entry: the clock session is regular. The "
            "HALT cell of the Cryptocurrency row is '1600 CT' where the Equity and Interest Rate "
            "rows halt at '1200 CT'."
        ),
    ),
    date(2022, 9, 5): Citation(
        _HC + "2022-labor-day-holiday-schedule-compact.xls",
        (
            "CME Group Globex Labor Day Holiday Schedule: September 2, 2022 - September 6, 2022 "
            "... Trade Date|Friday, September 2|Tuesday, September 6 ... Calendar Date|Friday, "
            "September 2|Sunday,Sept 4 into Monday, Sept 5|Monday, Sept 5|Monday, Sept 5 into "
            "Tuesday, Sept 6 ... Product|CLOSE|OPEN|HALT|OPEN ... Cryptocurrency|Regular @ 1600 "
            "CT / 2100 UTC|Regular @ 1700 CT / 2200 UTC|1600 CT / 2100 UTC|Regular @ 1700 CT / "
            "2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule (.xls). The schedule gives hours per "
            "asset-class row; the crypto row is 'Cryptocurrency'. Reading: crypto trades its "
            "regular hours on Monday Sept 5 (halt only at the regular 16:00 CT break, reopen "
            "17:00 CT); CME books the day's Globex trading to trade date Tuesday Sept 6 (no "
            "Monday Sept 5 settlement). Not a HOLIDAYS entry: the clock session is regular. The "
            "HALT cell of the Cryptocurrency row is '1600 CT' where the Equity and Interest Rate "
            "rows halt at '1200 CT'."
        ),
    ),
    date(2022, 11, 24): Citation(
        _HC + "2022-thanksgiving-holiday-schedule-compact.xls",
        (
            "CME Group Globex Thanksgiving Holiday Schedule: November 23, 2022 - November 25, "
            "2022 ... Trade Date|Wednesday ,November 23|| Friday, November 25 ... "
            "Products|Wednesday ,November 23|Wednesday, November 23|Thursday ,November "
            "24|Thursday , November 24|Friday November 25|Friday November 25 ... "
            "CLOSE|OPEN|HALT|OPEN|OPEN|CLOSE ... Cryptocurrency |Regular @ 1600 CT / 2200 "
            "UTC|Regular @ 1700 CT / 2300 UTC|1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC|| "
            "Early @ 1245 CT/ 1845 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule (.xls). The schedule gives hours per "
            "asset-class row; the crypto row is 'Cryptocurrency'. Reading: crypto trades its "
            "regular hours on Thursday Nov 24 (halt only at the regular 16:00 CT break, reopen "
            "17:00 CT); CME books the day's Globex trading to trade date Friday Nov 25 (no "
            "Thursday Nov 24 settlement). Not a HOLIDAYS entry: the clock session is regular. The "
            "HALT cell of the Cryptocurrency row is '1600 CT' where the Equity and Interest Rate "
            "rows halt at '1200 CT'."
        ),
    ),
    date(2023, 1, 16): Citation(
        None,
        "[unverified]",
        note=(
            "[unverified] No CME document with a crypto row for MLK Day 2023 was retrieved: CME's "
            "MLK 2023 Globex schedule on Wayback is the MGEX/DME sheet only "
            "(2023-mlk-day-holiday-schedule-compact-mgex-dme.xls, no crypto row); no "
            "trading-hours summary PDF exists for it (Wayback 404s for mlk-day-2023.pdf, "
            "martin-luther-king-day-2023.pdf, martin-luther-king-jr-day-2023.pdf, "
            "files/mlk-day.pdf); the service captures of 2024-07-08 hold no events for any "
            "product before 2023-09; AMP Futures' image of CME's MLK 2023 schedule (cached by the "
            "rates builder) has no crypto row; CME's settlement notice and clearing advisory give "
            "no hours. Assumed from the pattern: CME's crypto row trades regular hours on every "
            "Monday holiday from 2022-01-17 (MLK 2022) to 2023-02-20 (Presidents Day 2023, CME "
            "PDF). If crypto instead halted at 12:00 CT, HOLIDAYS lacks an EARLY_HALT here. "
            "Confirmation window: the bar check after the step 2 purchase settles it."
        ),
    ),
    date(2023, 2, 20): Citation(
        _FILES + "presidents-day.pdf",
        (
            "PRODUCT NAME Cleared As SUNDAY, 19 FEB 2023 MONDAY, 20 FEB 2023 TUESDAY, 21 FEB 2023 "
            "... TRADE DATE: TUES 21 FEB TRADE DATE: TUES 21 FEB CRYPTOCURRENCIES 16:00 (PREOPEN) "
            "16:00 (PREOPEN) HALT TRADE DATE: WED 22 FEB 17:00 (OPEN) 17:00 (OPEN) 16:45 "
            "(PREOPEN) 17:00 (OPEN)"
        ),
        note=(
            "CME's holiday trading-hours summary PDF, row CRYPTOCURRENCIES ('the most actively "
            "traded instruments for each asset class'); pdftotext -layout interleaves the table "
            "columns, so each quoted run mixes cells of adjacent columns. Reading: crypto trades "
            "its regular hours on 2023-02-20 (halt only at the regular 16:00 CT break, reopen "
            "17:00 CT); CME books the day's Globex trading to trade date 2023-02-21 (no "
            "2023-02-20 settlement). Not a HOLIDAYS entry: the clock session is regular. The "
            "holiday column of the CRYPTOCURRENCIES row reads '16:00 (PREOPEN) HALT ... 17:00 "
            "(OPEN)' under 'TRADE DATE: TUES' (the Equities row halts at 12:00 CT)."
        ),
    ),
    date(2023, 5, 29): Citation(
        _TH + "memorial-day-2023.pdf",
        (
            "PRODUCT NAME SUNDAY, 28 MAY 2023 MONDAY, 29 MAY 2023 TUESDAY, 30 MAY 2023 ... TRADE "
            "DATE: TUES 30 MAY TRADE DATE: TUES 30 MAY TRADE DATE: TUES 30 MAY 16:00 (CLOSED) "
            "CRYPTOCURRENCIES 16:00 (PREOPEN) 16:00 (PREOPEN) HALT TRADE DATE: WED 31 MAY 17:00 "
            "(OPEN) 17:00 (OPEN) 16:45 (PREOPEN) 17:00 (OPEN)"
        ),
        note=(
            "CME's holiday trading-hours summary PDF, row CRYPTOCURRENCIES ('the most actively "
            "traded instruments for each asset class'); pdftotext -layout interleaves the table "
            "columns, so each quoted run mixes cells of adjacent columns. Reading: crypto trades "
            "its regular hours on 2023-05-29 (halt only at the regular 16:00 CT break, reopen "
            "17:00 CT); CME books the day's Globex trading to trade date 2023-05-30 (no "
            "2023-05-29 settlement). Not a HOLIDAYS entry: the clock session is regular. The "
            "holiday column of the CRYPTOCURRENCIES row reads '16:00 (PREOPEN) HALT ... 17:00 "
            "(OPEN)' under 'TRADE DATE: TUES' (the Equities row halts at 12:00 CT)."
        ),
    ),
    date(2023, 6, 19): Citation(
        _TH + "juneteenth-2023.pdf",
        (
            "PRODUCT NAME SUNDAY, 18 JUNE 2023 MONDAY, 19 JUNE 2023 TUESDAY, 20 JUNE 2023 ... "
            "TRADE DATE: TUES 20 JUNE TRADE DATE: TUES 20 JUNE TRADE DATE: TUES 20 JUNE 16:00 "
            "(CLOSED) CRYPTOCURRENCIES 16:00 (PREOPEN) 16:00 (PREOPEN) HALT TRADE DATE: WED 21 "
            "JUNE 17:00 (OPEN) 17:00 (OPEN) 16:45 (PREOPEN) 17:00 (OPEN)"
        ),
        note=(
            "CME's holiday trading-hours summary PDF, row CRYPTOCURRENCIES ('the most actively "
            "traded instruments for each asset class'); pdftotext -layout interleaves the table "
            "columns, so each quoted run mixes cells of adjacent columns. Reading: crypto trades "
            "its regular hours on 2023-06-19 (halt only at the regular 16:00 CT break, reopen "
            "17:00 CT); CME books the day's Globex trading to trade date 2023-06-20 (no "
            "2023-06-19 settlement). Not a HOLIDAYS entry: the clock session is regular. The "
            "holiday column of the CRYPTOCURRENCIES row reads '16:00 (PREOPEN) HALT ... 17:00 "
            "(OPEN)' under 'TRADE DATE: TUES' (the Equities row halts at 12:00 CT)."
        ),
    ),
    date(2023, 7, 4): Citation(
        _TH + "4th-of-july-2023.pdf",
        (
            "PRODUCT NAME MONDAY, 3 JULY 2023 TUESDAY, 4 JULY 2023 WEDNESDAY, 5 JULY 2023 ... "
            "TRADE DATE: MON 3 JULY TRADE DATE: WED 5 JULY 16:00 (CLOSED) TRADE DATE: WED 5 JULY "
            "16:00 (CLOSED) CRYPTOCURRENCIES TRADE DATE: WED 5 JULY 16:00 (PREOPEN) HALT TRADE "
            "DATE: THUR 6 JULY 16:45 (PREOPEN) 17:00 (OPEN) 16:45 (PREOPEN) 17:00 (OPEN) 17:00 "
            "(OPEN)"
        ),
        note=(
            "CME's holiday trading-hours summary PDF, row CRYPTOCURRENCIES ('the most actively "
            "traded instruments for each asset class'); pdftotext -layout interleaves the table "
            "columns, so each quoted run mixes cells of adjacent columns. Reading: crypto trades "
            "its regular hours on 2023-07-04 (halt only at the regular 16:00 CT break, reopen "
            "17:00 CT); CME books the day's Globex trading to trade date 2023-07-05 (no "
            "2023-07-04 settlement). Not a HOLIDAYS entry: the clock session is regular. The "
            "holiday column of the CRYPTOCURRENCIES row reads '16:00 (PREOPEN) HALT ... 17:00 "
            "(OPEN)' under 'TRADE DATE: WED' (the Equities row halts at 12:00 CT)."
        ),
    ),
    date(2023, 9, 4): Citation(
        _TH + "labor-day-2023.pdf",
        (
            "PRODUCT NAME SUNDAY, 3 SEPTEMBER 2023 MONDAY, 4 SEPTEMBER 2023 TUESDAY, 5 SEPTEMBER "
            "2023 ... TRADE DATE: TUES 5 SEP TRADE DATE: TUES 5 SEP TRADE DATE: TUES 5 SEP 16:00 "
            "(CLOSED) CRYPTOCURRENCIES 16:00 (PREOPEN) 16:00 (PREOPEN) HALT TRADE DATE: WED 6 SEP "
            "17:00 (OPEN) 17:00 (OPEN) 16:45 (PREOPEN) 17:00 (OPEN)"
        ),
        note=(
            "CME's holiday trading-hours summary PDF, row CRYPTOCURRENCIES ('the most actively "
            "traded instruments for each asset class'); pdftotext -layout interleaves the table "
            "columns, so each quoted run mixes cells of adjacent columns. Reading: crypto trades "
            "its regular hours on 2023-09-04 (halt only at the regular 16:00 CT break, reopen "
            "17:00 CT); CME books the day's Globex trading to trade date 2023-09-05 (no "
            "2023-09-04 settlement). Not a HOLIDAYS entry: the clock session is regular. The "
            "holiday column of the CRYPTOCURRENCIES row reads '16:00 (PREOPEN) HALT ... 17:00 "
            "(OPEN)' under 'TRADE DATE: TUES' (the Equities row halts at 12:00 CT)."
        ),
    ),
    date(2023, 11, 23): Citation(
        _TH + "thanksgiving-day-2023.pdf",
        (
            "PRODUCT NAME WEDNESDAY, 22 NOVEMBER 2023 THURSDAY, 23 NOVEMBER 2023 FRIDAY, 24 "
            "NOVEMBER 2023 ... CRYPTOCURRENCIES TRADE DATE: FRI 24 NOV 16:00 (PREOPEN) 12:45 "
            "(CLOSED) 16:45 (PREOPEN) 17:00 (OPEN) 17:00 (OPEN)"
        ),
        note=(
            "CME's holiday trading-hours summary PDF, row CRYPTOCURRENCIES ('the most actively "
            "traded instruments for each asset class'); pdftotext -layout interleaves the table "
            "columns, so each quoted run mixes cells of adjacent columns. Reading: crypto trades "
            "its regular hours on 2023-11-23 (halt only at the regular 16:00 CT break, reopen "
            "17:00 CT); CME books the day's Globex trading to trade date 2023-11-24 (no "
            "2023-11-23 settlement). Not a HOLIDAYS entry: the clock session is regular. The "
            "holiday column of the CRYPTOCURRENCIES row reads '16:00 (PREOPEN) HALT ... 17:00 "
            "(OPEN)' under 'TRADE DATE: FRI' (the Equities row halts at 12:00 CT)."
        ),
    ),
    date(2024, 1, 15): Citation(
        _svc("2024-01-14", "2024-01-16", "1734710019526"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2024-01-14","events":[{"tradingDate":"2024-01-16","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2024-01-16","eventTime":'
            '"17:00","marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2024-01-15","events":[{"tradingDate":"2024-01-16","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2024-01-16","eventTime":'
            '"17:00","marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2024-01-16","events":[{"tradingDate":"2024-01-16","eve'
            'ntTime":"16:00","marketEventType":"closed"},{"tradingDate":"2024-01-17","eventTime":"'
            '16:45","marketEventType":"preopen"},{"tradingDate":"2024-01-17","eventTime":"17:00","'
            'marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20241220. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "Reading: crypto trades its regular hours on 2024-01-15 (halt only at the regular "
            "16:00 CT break, reopen 17:00 CT); CME books the day's Globex trading to trade date "
            "2024-01-16 (no 2024-01-15 settlement). Not a HOLIDAYS entry: the clock session is "
            "regular. Record: the holiday's events are '16:00 preopen' and '17:00 open' with "
            "tradingDate 2024-01-16 (a halt at the regular break only), and the trade date before "
            "it closes 16:00 CT with its 17:00 reopen already booked to 2024-01-16."
        ),
    ),
    date(2024, 2, 19): Citation(
        _svc("2024-02-18", "2024-02-20", "1720455278669"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2024-02-18","events":[{"tradingDate":"2024-02-20","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2024-02-20","eventTime":'
            '"17:00","marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2024-02-19","events":[{"tradingDate":"2024-02-20","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2024-02-20","eventTime":'
            '"17:00","marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2024-02-20","events":[{"tradingDate":"2024-02-20","eve'
            'ntTime":"16:00","marketEventType":"closed"},{"tradingDate":"2024-02-21","eventTime":"'
            '16:45","marketEventType":"preopen"},{"tradingDate":"2024-02-21","eventTime":"17:00","'
            'marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20240708. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "Reading: crypto trades its regular hours on 2024-02-19 (halt only at the regular "
            "16:00 CT break, reopen 17:00 CT); CME books the day's Globex trading to trade date "
            "2024-02-20 (no 2024-02-19 settlement). Not a HOLIDAYS entry: the clock session is "
            "regular. Record: the holiday's events are '16:00 preopen' and '17:00 open' with "
            "tradingDate 2024-02-20 (a halt at the regular break only), and the trade date before "
            "it closes 16:00 CT with its 17:00 reopen already booked to 2024-02-20."
        ),
    ),
    date(2024, 5, 27): Citation(
        _svc("2024-05-26", "2024-05-28", "1720455278675"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2024-05-26","events":[{"tradingDate":"2024-05-28","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2024-05-28","eventTime":'
            '"17:00","marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2024-05-27","events":[{"tradingDate":"2024-05-28","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2024-05-28","eventTime":'
            '"17:00","marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2024-05-28","events":[{"tradingDate":"2024-05-28","eve'
            'ntTime":"16:00","marketEventType":"closed"},{"tradingDate":"2024-05-29","eventTime":"'
            '16:45","marketEventType":"preopen"},{"tradingDate":"2024-05-29","eventTime":"17:00","'
            'marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20240708. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "Reading: crypto trades its regular hours on 2024-05-27 (halt only at the regular "
            "16:00 CT break, reopen 17:00 CT); CME books the day's Globex trading to trade date "
            "2024-05-28 (no 2024-05-27 settlement). Not a HOLIDAYS entry: the clock session is "
            "regular. Record: the holiday's events are '16:00 preopen' and '17:00 open' with "
            "tradingDate 2024-05-28 (a halt at the regular break only), and the trade date before "
            "it closes 16:00 CT with its 17:00 reopen already booked to 2024-05-28."
        ),
    ),
    date(2024, 6, 19): Citation(
        _svc("2024-06-18", "2024-06-20", "1720455278677"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2024-06-18","events":[{"tradingDate":"2024-06-18","eve'
            'ntTime":"16:00","marketEventType":"closed"},{"tradingDate":"2024-06-20","eventTime":"'
            '16:45","marketEventType":"preopen"},{"tradingDate":"2024-06-20","eventTime":"17:00","'
            'marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2024-06-19","events":[{"tradingDate":"2024-06-20","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2024-06-20","eventTime":'
            '"17:00","marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2024-06-20","events":[{"tradingDate":"2024-06-20","eve'
            'ntTime":"16:00","marketEventType":"closed"},{"tradingDate":"2024-06-21","eventTime":"'
            '16:45","marketEventType":"preopen"},{"tradingDate":"2024-06-21","eventTime":"17:00","'
            'marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20240708. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "Reading: crypto trades its regular hours on 2024-06-19 (halt only at the regular "
            "16:00 CT break, reopen 17:00 CT); CME books the day's Globex trading to trade date "
            "2024-06-20 (no 2024-06-19 settlement). Not a HOLIDAYS entry: the clock session is "
            "regular. Record: the holiday's events are '16:00 preopen' and '17:00 open' with "
            "tradingDate 2024-06-20 (a halt at the regular break only), and the trade date before "
            "it closes 16:00 CT with its 17:00 reopen already booked to 2024-06-20."
        ),
    ),
    date(2024, 7, 4): Citation(
        _svc("2024-07-03", "2024-07-05", "1720455278680"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2024-07-03","events":[{"tradingDate":"2024-07-03","eve'
            'ntTime":"16:00","marketEventType":"closed"},{"tradingDate":"2024-07-05","eventTime":"'
            '16:45","marketEventType":"preopen"},{"tradingDate":"2024-07-05","eventTime":"17:00","'
            'marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2024-07-04","events":[{"tradingDate":"2024-07-05","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2024-07-05","eventTime":'
            '"17:00","marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2024-07-05","events":[{"tradingDate":"2024-07-05","eve'
            'ntTime":"16:00","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20240708. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "Reading: crypto trades its regular hours on 2024-07-04 (halt only at the regular "
            "16:00 CT break, reopen 17:00 CT); CME books the day's Globex trading to trade date "
            "2024-07-05 (no 2024-07-04 settlement). Not a HOLIDAYS entry: the clock session is "
            "regular. Record: the holiday's events are '16:00 preopen' and '17:00 open' with "
            "tradingDate 2024-07-05 (a halt at the regular break only), and the trade date before "
            "it closes 16:00 CT with its 17:00 reopen already booked to 2024-07-05."
        ),
    ),
    date(2024, 9, 2): Citation(
        _svc("2024-09-01", "2024-09-03", "1734710019534"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2024-09-01","events":[{"tradingDate":"2024-09-03","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2024-09-03","eventTime":'
            '"17:00","marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2024-09-02","events":[{"tradingDate":"2024-09-03","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2024-09-03","eventTime":'
            '"17:00","marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2024-09-03","events":[{"tradingDate":"2024-09-03","eve'
            'ntTime":"16:00","marketEventType":"closed"},{"tradingDate":"2024-09-04","eventTime":"'
            '16:45","marketEventType":"preopen"},{"tradingDate":"2024-09-04","eventTime":"17:00","'
            'marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20241220. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "Reading: crypto trades its regular hours on 2024-09-02 (halt only at the regular "
            "16:00 CT break, reopen 17:00 CT); CME books the day's Globex trading to trade date "
            "2024-09-03 (no 2024-09-02 settlement). Not a HOLIDAYS entry: the clock session is "
            "regular. Record: the holiday's events are '16:00 preopen' and '17:00 open' with "
            "tradingDate 2024-09-03 (a halt at the regular break only), and the trade date before "
            "it closes 16:00 CT with its 17:00 reopen already booked to 2024-09-03."
        ),
    ),
    date(2024, 11, 28): Citation(
        _svc("2024-11-27", "2024-11-29", "1734710019535"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2024-11-27","events":[{"tradingDate":"2024-11-27","eve'
            'ntTime":"16:00","marketEventType":"closed"},{"tradingDate":"2024-11-29","eventTime":"'
            '16:45","marketEventType":"preopen"},{"tradingDate":"2024-11-29","eventTime":"17:00","'
            'marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2024-11-28","events":[{"tradingDate":"2024-11-29","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2024-11-29","eventTime":'
            '"17:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20241220. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "Reading: crypto trades its regular hours on 2024-11-28 (halt only at the regular "
            "16:00 CT break, reopen 17:00 CT); CME books the day's Globex trading to trade date "
            "2024-11-29 (no 2024-11-28 settlement). Not a HOLIDAYS entry: the clock session is "
            "regular. Record: the holiday's events are '16:00 preopen' and '17:00 open' with "
            "tradingDate 2024-11-29 (a halt at the regular break only), and the trade date before "
            "it closes 16:00 CT with its 17:00 reopen already booked to 2024-11-29."
        ),
    ),
    date(2025, 1, 20): Citation(
        _svc("2025-01-19", "2025-01-21", "1734710019539"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2025-01-19","events":[{"tradingDate":"2025-01-21","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2025-01-21","eventTime":'
            '"17:00","marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2025-01-20","events":[{"tradingDate":"2025-01-21","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2025-01-21","eventTime":'
            '"17:00","marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2025-01-21","events":[{"tradingDate":"2025-01-21","eve'
            'ntTime":"16:00","marketEventType":"closed"},{"tradingDate":"2025-01-22","eventTime":"'
            '16:45","marketEventType":"preopen"},{"tradingDate":"2025-01-22","eventTime":"17:00","'
            'marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20241220. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "Reading: crypto trades its regular hours on 2025-01-20 (halt only at the regular "
            "16:00 CT break, reopen 17:00 CT); CME books the day's Globex trading to trade date "
            "2025-01-21 (no 2025-01-20 settlement). Not a HOLIDAYS entry: the clock session is "
            "regular. Record: the holiday's events are '16:00 preopen' and '17:00 open' with "
            "tradingDate 2025-01-21 (a halt at the regular break only), and the trade date before "
            "it closes 16:00 CT with its 17:00 reopen already booked to 2025-01-21."
        ),
    ),
    date(2025, 2, 17): Citation(
        _svc("2025-02-16", "2025-02-18", "1734710019540"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2025-02-16","events":[{"tradingDate":"2025-02-18","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2025-02-18","eventTime":'
            '"17:00","marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2025-02-17","events":[{"tradingDate":"2025-02-18","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2025-02-18","eventTime":'
            '"17:00","marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2025-02-18","events":[{"tradingDate":"2025-02-18","eve'
            'ntTime":"16:00","marketEventType":"closed"},{"tradingDate":"2025-02-19","eventTime":"'
            '16:45","marketEventType":"preopen"},{"tradingDate":"2025-02-19","eventTime":"17:00","'
            'marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20241220. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "Reading: crypto trades its regular hours on 2025-02-17 (halt only at the regular "
            "16:00 CT break, reopen 17:00 CT); CME books the day's Globex trading to trade date "
            "2025-02-18 (no 2025-02-17 settlement). Not a HOLIDAYS entry: the clock session is "
            "regular. Record: the holiday's events are '16:00 preopen' and '17:00 open' with "
            "tradingDate 2025-02-18 (a halt at the regular break only), and the trade date before "
            "it closes 16:00 CT with its 17:00 reopen already booked to 2025-02-18."
        ),
    ),
    date(2025, 5, 26): Citation(
        _svc("2025-05-25", "2025-05-27", "1734710019543"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2025-05-25","events":[{"tradingDate":"2025-05-27","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2025-05-27","eventTime":'
            '"17:00","marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2025-05-26","events":[{"tradingDate":"2025-05-27","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2025-05-27","eventTime":'
            '"17:00","marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2025-05-27","events":[{"tradingDate":"2025-05-27","eve'
            'ntTime":"16:00","marketEventType":"closed"},{"tradingDate":"2025-05-28","eventTime":"'
            '16:45","marketEventType":"preopen"},{"tradingDate":"2025-05-28","eventTime":"17:00","'
            'marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20241220. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "Reading: crypto trades its regular hours on 2025-05-26 (halt only at the regular "
            "16:00 CT break, reopen 17:00 CT); CME books the day's Globex trading to trade date "
            "2025-05-27 (no 2025-05-26 settlement). Not a HOLIDAYS entry: the clock session is "
            "regular. Record: the holiday's events are '16:00 preopen' and '17:00 open' with "
            "tradingDate 2025-05-27 (a halt at the regular break only), and the trade date before "
            "it closes 16:00 CT with its 17:00 reopen already booked to 2025-05-27."
        ),
    ),
    date(2025, 6, 19): Citation(
        _svc("2025-06-18", "2025-06-20", "1734710019544"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2025-06-18","events":[{"tradingDate":"2025-06-18","eve'
            'ntTime":"16:00","marketEventType":"closed"},{"tradingDate":"2025-06-20","eventTime":"'
            '16:45","marketEventType":"preopen"},{"tradingDate":"2025-06-20","eventTime":"17:00","'
            'marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2025-06-19","events":[{"tradingDate":"2025-06-20","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2025-06-20","eventTime":'
            '"17:00","marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2025-06-20","events":[{"tradingDate":"2025-06-20","eve'
            'ntTime":"16:00","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20241220. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "Reading: crypto trades its regular hours on 2025-06-19 (halt only at the regular "
            "16:00 CT break, reopen 17:00 CT); CME books the day's Globex trading to trade date "
            "2025-06-20 (no 2025-06-19 settlement). Not a HOLIDAYS entry: the clock session is "
            "regular. Record: the holiday's events are '16:00 preopen' and '17:00 open' with "
            "tradingDate 2025-06-20 (a halt at the regular break only), and the trade date before "
            "it closes 16:00 CT with its 17:00 reopen already booked to 2025-06-20."
        ),
    ),
    date(2025, 9, 1): Citation(
        _svc("2025-08-31", "2025-09-02", "1734710019546"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2025-08-31","events":[{"tradingDate":"2025-09-02","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2025-09-02","eventTime":'
            '"17:00","marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2025-09-01","events":[{"tradingDate":"2025-09-02","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2025-09-02","eventTime":'
            '"17:00","marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2025-09-02","events":[{"tradingDate":"2025-09-02","eve'
            'ntTime":"16:00","marketEventType":"closed"},{"tradingDate":"2025-09-03","eventTime":"'
            '16:45","marketEventType":"preopen"},{"tradingDate":"2025-09-03","eventTime":"17:00","'
            'marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20241220. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "Reading: crypto trades its regular hours on 2025-09-01 (halt only at the regular "
            "16:00 CT break, reopen 17:00 CT); CME books the day's Globex trading to trade date "
            "2025-09-02 (no 2025-09-01 settlement). Not a HOLIDAYS entry: the clock session is "
            "regular. Record: the holiday's events are '16:00 preopen' and '17:00 open' with "
            "tradingDate 2025-09-02 (a halt at the regular break only), and the trade date before "
            "it closes 16:00 CT with its 17:00 reopen already booked to 2025-09-02."
        ),
    ),
    date(2025, 11, 27): Citation(
        _svc("2025-11-26", "2025-11-28", "1769649703060"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2025-11-26","events":[{"tradingDate":"2025-11-26","eve'
            'ntTime":"16:00","marketEventType":"closed"},{"tradingDate":"2025-11-28","eventTime":"'
            '16:45","marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":"17:00","'
            'marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2025-11-27","events":[{"tradingDate":"2025-11-28","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2025-11-28","eventTime":'
            '"17:00","marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20260129. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "Reading: crypto trades its regular hours on 2025-11-27 (halt only at the regular "
            "16:00 CT break, reopen 17:00 CT); CME books the day's Globex trading to trade date "
            "2025-11-28 (no 2025-11-27 settlement). Not a HOLIDAYS entry: the clock session is "
            "regular. Record: the holiday's events are '16:00 preopen' and '17:00 open' with "
            "tradingDate 2025-11-28 (a halt at the regular break only), and the trade date before "
            "it closes 16:00 CT with its 17:00 reopen already booked to 2025-11-28."
        ),
    ),
    date(2026, 1, 19): Citation(
        _svc("2026-01-18", "2026-01-20", "1769649703068"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2026-01-18","events":[{"tradingDate":"2026-01-20","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2026-01-20","eventTime":'
            '"17:00","marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2026-01-19","events":[{"tradingDate":"2026-01-20","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2026-01-20","eventTime":'
            '"17:00","marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2026-01-20","events":[{"tradingDate":"2026-01-20","eve'
            'ntTime":"16:00","marketEventType":"closed"},{"tradingDate":"2026-01-21","eventTime":"'
            '16:45","marketEventType":"preopen"},{"tradingDate":"2026-01-21","eventTime":"17:00","'
            'marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20260129. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "Reading: crypto trades its regular hours on 2026-01-19 (halt only at the regular "
            "16:00 CT break, reopen 17:00 CT); CME books the day's Globex trading to trade date "
            "2026-01-20 (no 2026-01-19 settlement). Not a HOLIDAYS entry: the clock session is "
            "regular. Record: the holiday's events are '16:00 preopen' and '17:00 open' with "
            "tradingDate 2026-01-20 (a halt at the regular break only), and the trade date before "
            "it closes 16:00 CT with its 17:00 reopen already booked to 2026-01-20."
        ),
    ),
    date(2026, 2, 16): Citation(
        _svc("2026-02-15", "2026-02-17", "1769649703070"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2026-02-15","events":[{"tradingDate":"2026-02-17","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2026-02-17","eventTime":'
            '"17:00","marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2026-02-16","events":[{"tradingDate":"2026-02-17","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2026-02-17","eventTime":'
            '"17:00","marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2026-02-17","events":[{"tradingDate":"2026-02-17","eve'
            'ntTime":"16:00","marketEventType":"closed"},{"tradingDate":"2026-02-18","eventTime":"'
            '16:45","marketEventType":"preopen"},{"tradingDate":"2026-02-18","eventTime":"17:00","'
            'marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20260129. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "Reading: crypto trades its regular hours on 2026-02-16 (halt only at the regular "
            "16:00 CT break, reopen 17:00 CT); CME books the day's Globex trading to trade date "
            "2026-02-17 (no 2026-02-16 settlement). Not a HOLIDAYS entry: the clock session is "
            "regular. Record: the holiday's events are '16:00 preopen' and '17:00 open' with "
            "tradingDate 2026-02-17 (a halt at the regular break only), and the trade date before "
            "it closes 16:00 CT with its 17:00 reopen already booked to 2026-02-17."
        ),
    ),
    date(2026, 5, 25): Citation(
        _svc("2026-05-24", "2026-05-26", "1749141516014"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2026-05-24","events":[{"tradingDate":"2026-05-26","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2026-05-26","eventTime":'
            '"17:00","marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2026-05-25","events":[{"tradingDate":"2026-05-26","eve'
            'ntTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2026-05-26","eventTime":'
            '"17:00","marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2026-05-26","events":[{"tradingDate":"2026-05-26","eve'
            'ntTime":"16:00","marketEventType":"closed"},{"tradingDate":"2026-05-27","eventTime":"'
            '16:45","marketEventType":"preopen"},{"tradingDate":"2026-05-27","eventTime":"17:00","'
            'marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20260619. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "Reading: crypto trades its regular hours on 2026-05-25 (halt only at the regular "
            "16:00 CT break, reopen 17:00 CT); CME books the day's Globex trading to trade date "
            "2026-05-26 (no 2026-05-25 settlement). Not a HOLIDAYS entry: the clock session is "
            "regular. Record: the holiday's events are '16:00 preopen' and '17:00 open' with "
            "tradingDate 2026-05-26 (a halt at the regular break only), and the trade date before "
            "it closes 16:00 CT with its 17:00 reopen already booked to 2026-05-26."
        ),
    ),
    date(2026, 6, 19): Citation(
        _svc("2026-06-18", "2026-06-20", "1749141523693"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2026-06-18","events":[{"tradingDate":"2026-06-18","eve'
            'ntTime":"16:00","marketEventType":"closed"},{"tradingDate":"2026-06-22","eventTime":"'
            '16:01","marketEventType":"preopen"},{"tradingDate":"2026-06-22","eventTime":"16:02","'
            'marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2026-06-19","events":[{"tradingDate":"2026-06-22","eve'
            'ntTime":"16:00","marketEventType":"closed"},{"tradingDate":"2026-06-22","eventTime":"'
            '16:01","marketEventType":"preopen"},{"tradingDate":"2026-06-22","eventTime":"16:02","'
            'marketEventType":"open"}]} ... '
            '{"groupCode":"BF","eventDate":"2026-06-20","events":[{"tradingDate":"2026-06-22","eve'
            'ntTime":"02:00","marketEventType":"closed"},{"tradingDate":"2026-06-22","eventTime":"'
            '03:45","marketEventType":"preopen"},{"tradingDate":"2026-06-22","eventTime":"04:00","'
            'marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20260619. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "24/7 regime (from 2026-05-29 16:00 CT). Reading: Thursday June 18 trade date closes "
            "16:00 CT, pre-open 16:01, open 16:02 CT with tradingDate 2026-06-22; Friday June 19 "
            "(the holiday) trades continuously to the 16:00-16:02 CT maintenance, still "
            "tradingDate 06-22; Saturday June 20 closes 02:00-04:00 CT (weekly maintenance), "
            "still 06-22. CME thus books Thu 16:02 CT through Mon 16:00 CT to trade date "
            "2026-06-22, per its rule 'All holiday or weekend trading from Friday evening through "
            "Sunday evening will have a trade date of the following business day' and the wiki's "
            "'Example 3 - Friday Holiday Trading Schedule': 'Friday is a holiday. Therefore, the "
            "trade date after the Thursday maintenance is Monday.' The pre-24/7 plan (capture "
            "2026-01-29) had a 12:00 CT close for BTC on 06-19, superseded; the capture of "
            "2026-07-22 (after the date) repeats this record. FLAG FOR THE LEAD: under the 02:10 "
            "PDT ruling (the bar builder follows CME's weekend assignment in the 24/7 regime) "
            "2026-06-19 has no crypto trade date and its bars belong to 2026-06-22, outside the "
            "calendar coverage and the research window; under the data.session convention (each "
            "calendar day its own trade date) 2026-06-19 is a regular 24/7 weekday, Thu 16:02 to "
            "Fri 16:00 CT."
        ),
    ),
}

# CME-stated regular crypto days near holidays, kept so the absence of an entry is a recorded
# finding, not an oversight.
NO_ENTRY_FINDINGS: dict[date, Citation] = {
    date(2019, 12, 31): Citation(
        _Z19,
        (
            "CME Group Globex New Years Holiday Schedule: December 31, 2019 - January 2, 2020 ... "
            "Trade Date|Tuesday,Dec 31|Globex Closed|Thursday, January 2 ... Calendar "
            "Trade|Tuesday, Dec 31|Wednessday, Jan 1 |Wednesday, Jan 1|Thursday, Jan 2|Thursday, "
            "Jan 2 ... CLOSE|CLOSED |OPEN|Open|CLOSE ... Bitcoin|Regular @ 1600 CT / 2200 "
            "UTC|Closed for New Year's|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member "
            "globex-trading-schedules/2019-new-years-holiday-schedule-compact.xls of CME's 2019 "
            "holiday-calendars.zip (the hash is the zip's). The schedule gives hours per "
            "asset-class row; the crypto row is 'Bitcoin'. NORMAL: regular 16:00 CT close on New "
            "Year's Eve (Tuesday Dec 31, 2019)."
        ),
    ),
    date(2020, 7, 2): Citation(
        _Z20,
        (
            "CME Group Globex Independence Day Holiday Schedule: July 2, 2020 to July 6, 2020 ... "
            "Trade Date|Thursday, July 2|Monday, July 6 ... Calendar Date|Thursday July "
            "2|Thursday , July 2|Friday July 3|Sunday July 5 into Monday July 6 ... "
            "Product|CLOSE|OPEN|ClOSE|OPEN ... Bitcoin|Regular @ 1600 CT / 2100 UTC|Regular @ "
            "1700 CT/ 2200 UTC|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member "
            "2020-4th-of-july-holiday-schedule-compact.xls of CME's 2020 holiday-calendars.zip "
            "(the hash is the zip's). The schedule gives hours per asset-class row; the crypto "
            "row is 'Bitcoin'. NORMAL: Thursday July 2, 2020 closes at the regular 16:00 CT (no "
            "early close before the observed holiday)."
        ),
    ),
    date(2020, 12, 31): Citation(
        _Z20,
        (
            "CME Group Globex New Years Holiday Schedule: December 31, 2020 - January 4, 2021 ... "
            "Trade Date|Thursday,Dec 31|Globex Closed|Monday, January 4 ... Calendar "
            "Trade|Thursday,Dec 31|Friday,Jan 1|Sunday,Jan 3|Monday, Jan 4|Monday, Jan 4 ... "
            "CLOSE|CLOSED |OPEN|OPEN|CLOSE ... Bitcoin|Regular @ 1600 CT / 2200 UTC|Closed for "
            "New Year's|Regular @ 1700 CT / 2300 UTC||Regular @ 1600 CT / 2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member "
            "2021-new-years-holiday-schedule-compact.xls of CME's 2020 holiday-calendars.zip (the "
            "hash is the zip's). The schedule gives hours per asset-class row; the crypto row is "
            "'Bitcoin'. NORMAL: regular 16:00 CT close on Thursday Dec 31, 2020."
        ),
    ),
    date(2021, 7, 2): Citation(
        _Z21,
        (
            "CME Group Globex Independence Day Holiday Schedule: July 2, 2021 to July 6, 2021 ... "
            "Trade Date|Friday, July 2|Tuesday, July 6 ... Calendar Date|Friday July 2|Sunday "
            "July 4|Monday July 5|Monday July 5 ... Product|CLOSE|OPEN|HALT|OPEN ... "
            "Bitcoin|Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT/ 2200 UTC|1200 CT / 1700 "
            "UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member "
            "2021-independence-day-holiday-schedule-compact.xls of CME's 2021 "
            "holiday-calendars.zip (the hash is the zip's). The schedule gives hours per "
            "asset-class row; the crypto row is 'Bitcoin'. NORMAL: Friday July 2, 2021 closes at "
            "the regular 16:00 CT."
        ),
    ),
    date(2021, 12, 23): Citation(
        _Z21,
        (
            "CME Group Globex Christmas Holiday Schedule: December 23, 2021 - December 27, 2021 "
            "... Trade Date|Thursday,December 23|Globex Closed|Monday December 27 ... "
            "Products|Thursday, Dec 23|Friday,Dec 24|Sunday 26|Monday,Dec 27 ... Bitcoin|Regular "
            "per Product|Closed for Christmas|Regular @ 1700 CT / 2300 UTC|Regular @ 1600 CT / "
            "2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member "
            "2021-christmas-holiday-schedule-compact.xls of CME's 2021 holiday-calendars.zip (the "
            "hash is the zip's). The schedule gives hours per asset-class row; the crypto row is "
            "'Bitcoin'. NORMAL: Thursday Dec 23, 2021 'Regular per Product' close before the "
            "observed Christmas closure of Friday Dec 24."
        ),
    ),
    date(2021, 12, 31): Citation(
        _Z21,
        (
            "CME Group Globex New Years Holiday Schedule: December 30, 2021 - January 3, 2022 ... "
            "Trade Date|Thursday,Dec 30|Thursday,Dec 30|Friday,Dec 31|Friday,Dec 31|Monday, "
            "January 3 ... Calendar Trade|Thursday,Dec 30|Thursday,Dec 30|Friday,Dec "
            "31|Friday,Dec 31|Sunday,Jan 2|Monday, Jan 3 ... CLOSE|OPEN |OPEN |Close|OPEN|OPEN "
            "... Bitcoin|Regular @ 1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC||Regular @ "
            "1600 CT / 2200 UTC|Regular @ 1700 CT / 2300 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule, member "
            "2022-new-years-holiday-schedule-compact.xls of CME's 2021 holiday-calendars.zip (the "
            "hash is the zip's). The schedule gives hours per asset-class row; the crypto row is "
            "'Bitcoin'. NORMAL: January 1, 2022 fell on a Saturday and CME observed no crypto "
            "closure: Friday Dec 31, 2021 trades Thursday 17:00 to the regular Friday 16:00 CT "
            "close, and Globex reopens Sunday Jan 2 17:00 CT for trade date Monday Jan 3 (also "
            "normal)."
        ),
    ),
    date(2022, 7, 1): Citation(
        _HC + "2022-independence-day-holiday-schedule-compact.xls",
        (
            "CME Group Globex Independence Day Holiday Schedule: July 1, 2022 to July 5, 2022 ... "
            "Trade Date|Friday, July 1|Tuesday, July 5 ... Calendar Date|Friday July 1|Sunday "
            "July 3|Monday July 4|Monday July 4 ... Product|CLOSE|OPEN|HALT|OPEN ... "
            "Cryptocurrency|Regular @ 1600 CT / 2100 UTC|Regular @ 1700 CT/ 2200 UTC|1600 CT / "
            "2100 UTC|Regular @ 1700 CT / 2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule (.xls). The schedule gives hours per "
            "asset-class row; the crypto row is 'Cryptocurrency'. NORMAL: Friday July 1, 2022 "
            "closes at the regular 16:00 CT."
        ),
    ),
    date(2022, 12, 23): Citation(
        _HC + "2022-christmas-holiday-schedule.xls",
        (
            "Calendar Date|Friday, December 23||||||||Monday, December 26||||||||||||||||Tuesday, "
            "December 27 ... Cryptocurrency|04:00:00 PM||||||||Globex Closed||||||||||04:00:00 "
            "PM|05:00:00 PM|||||||04:00:00 PM"
        ),
        note=(
            "CME's full Globex holiday schedule (.xls). The schedule gives hours per asset-class "
            "row; the crypto row is 'Cryptocurrency'. NORMAL: Friday Dec 23, 2022 closes 04:00:00 "
            "PM (16:00 CT, regular) before the observed Christmas closure of Monday Dec 26."
        ),
    ),
    date(2022, 12, 30): Citation(
        _HC + "2023-new-years-holiday-schedule-compact.xls",
        (
            "CME Group Globex New Years Holiday Schedule: December 30, 2022 - January 3, 2023 ... "
            "Trade Date|Friday,Dec 30|Sunday, January 1 and Monday, January 2|| Tuesday, January "
            "3 ... Calendar Trade|Friday,Dec 30|Sunday, Jan 1 and Monday, Jan 2|Monday,Jan "
            "2|Tuesday, Jan 3|Tuesday, Jan 3 ... CLOSE|Closed|OPEN|OPEN|CLOSE ... "
            "Cryptocurrency|Regular @ 1600 CT / 2200 UTC|Globex Closed|Regular @ 1700 CT / 2300 "
            "UTC||Regular @ 1600 CT / 2200 UTC"
        ),
        note=(
            "CME's compact Globex holiday schedule (.xls). The schedule gives hours per "
            "asset-class row; the crypto row is 'Cryptocurrency'. NORMAL: Friday Dec 30, 2022 "
            "closes at the regular 16:00 CT."
        ),
    ),
    date(2023, 7, 3): Citation(
        _TH + "4th-of-july-2023.pdf",
        (
            "PRODUCT NAME MONDAY, 3 JULY 2023 TUESDAY, 4 JULY 2023 WEDNESDAY, 5 JULY 2023 ... "
            "CRYPTOCURRENCIES TRADE DATE: WED 5 JULY 16:00 (PREOPEN) HALT TRADE DATE: THUR 6 JULY "
            "16:45 (PREOPEN) 17:00 (OPEN) 16:45 (PREOPEN) 17:00 (OPEN) 17:00 (OPEN) TRADE DATE: "
            "WED 5 JULY TRADE DATE: MON 3 JULY 16:00 (CLOSED)"
        ),
        note=(
            "CME's holiday trading-hours summary PDF, row CRYPTOCURRENCIES ('the most actively "
            "traded instruments for each asset class'); pdftotext -layout interleaves the table "
            "columns, so each quoted run mixes cells of adjacent columns. NORMAL: the Monday 3 "
            "July column of the CRYPTOCURRENCIES row reads 'TRADE DATE: MON 3 JULY 16:00 "
            "(CLOSED)' then '16:45 (PREOPEN) 17:00 (OPEN)' for trade date Wed 5 July: a regular "
            "16:00 CT close (the Equities row closes 12:15 CT that day)."
        ),
    ),
    date(2024, 7, 3): Citation(
        _svc("2024-07-03", "2024-07-05", "1720455278680"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2024-07-03","events":[{"tradingDate":"2024-07-03","eve'
            'ntTime":"16:00","marketEventType":"closed"},{"tradingDate":"2024-07-05","eventTime":"'
            '16:45","marketEventType":"preopen"},{"tradingDate":"2024-07-05","eventTime":"17:00","'
            'marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20240708. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "NORMAL: Wednesday July 3, 2024 closes 16:00 CT (regular; ES closes 12:15 CT)."
        ),
    ),
    date(2024, 12, 31): Citation(
        _svc("2024-12-31", "2025-01-02", "1734710019538"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2024-12-31","events":[{"tradingDate":"2024-12-31","eve'
            'ntTime":"16:00","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20241220. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "NORMAL: New Year's Eve 2024 closes at the regular 16:00 CT."
        ),
    ),
    date(2025, 7, 3): Citation(
        _svc("2025-07-03", "2025-07-05", "1734710019545"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2025-07-03","events":[{"tradingDate":"2025-07-03","eve'
            'ntTime":"16:00","marketEventType":"closed"},{"tradingDate":"2025-07-04","eventTime":"'
            '16:45","marketEventType":"preopen"},{"tradingDate":"2025-07-04","eventTime":"17:00","'
            'marketEventType":"open"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20241220. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "NORMAL: Thursday July 3, 2025 closes 16:00 CT (regular; ES closes 12:15 CT)."
        ),
    ),
    date(2025, 12, 31): Citation(
        _svc("2025-12-31", "2026-01-02", "1769649703066"),
        (
            '"globex":"BTC","prodGroup":"BF","name":"Bitcoin Futures","id":8478 ... '
            '{"groupCode":"BF","eventDate":"2025-12-31","events":[{"tradingDate":"2025-12-31","eve'
            'ntTime":"16:00","marketEventType":"closed"}]}'
        ),
        note=(
            "CME's trading-hours-by-product service behind cmegroup.com/trading-hours.html, "
            "product 8478 'Bitcoin Futures' (groupCode BF), Wayback capture 20260129. BTC stands "
            "for MBT: CME derives MBT's daily settlement from BTC and its holiday schedules list "
            "one crypto row. 'preopen' at a time = trading stops (order entry only) until the "
            "next 'open'; 'closed' = final close of a trade date; tradingDate = CME trade date. "
            "NORMAL: New Year's Eve 2025 closes at the regular 16:00 CT."
        ),
    ),
    date(2025, 1, 9): Citation(
        _TH + "day-of-mourning-january-9-2024.pdf",
        (
            "PRODUCT NAME JANUARY 9, 2025 TRADING FLOOR CLEARPORT ... CME GROUP US EQUITIES CLOSE "
            "at 8:30 AM CT ... CRYPTO NORMAL HOURS N/A NORMAL HOURS"
        ),
        note=(
            "CME's trading-hours summary for the National Day of Mourning (President Carter), "
            "file trading-hours/files/day-of-mourning-january-9-2024.pdf (the file name says "
            "2024; the document is for January 9, 2025). NORMAL: CRYPTO 'NORMAL HOURS' while US "
            "equities close at 8:30 AM CT (data.cme_calendar's 08:30 halt for MES does not apply "
            "to crypto)."
        ),
    ),
    date(2026, 5, 29): Citation(
        _WIKI_247,
        (
            "Starting at 4 p.m. Central Time on Friday, May 29, 2026, CME Group will expand "
            "cryptocurrency futures and options to 24/7 trading."
        ),
        note=(
            "CME client systems wiki page 1283194884. NORMAL: trade date Friday 2026-05-29 is the "
            "last trade date of the 5-day regime (Thursday 17:00 CT to Friday 16:00 CT); 24/7 "
            "trading starts after its 16:00 CT close. SESSIONS splits here."
        ),
    ),
}

SESSION_SOURCES: dict[str, Citation] = {
    "cme_crypto_hours_5day": Citation(
        _BTC_SPECS,
        (
            "Trading Hours Sunday - Friday 6:00 p.m. - 5:00 p.m. (5:00 p.m. - 4:00 p.m/ CT) with "
            "a 60-minute break each day beginning at 5:00 p.m. (4:00 p.m. CT)"
        ),
        _MBT_FAQ,
        (
            "CME Globex: Sunday - Friday 6:00 p.m. - 5:00 p.m. ET (5:00 p.m. - 4:00 p.m. CT) with "
            "a 60-minute break each day beginning at 5:00 p.m. ET (4:00 p.m. CT)"
        ),
        note=(
            "Status: CME's Bitcoin futures contract specifications (Wayback 2019-06-03). Time: "
            "CME's Micro Bitcoin futures FAQ (Wayback 2021-03-30). The same 17:00-16:00 CT week "
            "is CME's 'Current Cryptocurrency Futures and Options Schedule' in the 2026 24/7 "
            "migration page (key 'cme_crypto_hours_5day_2026'), and every 2019-2023 holiday "
            "schedule's crypto row closes 'Regular @ 1600 CT' and opens 'Regular @ 1700 CT'."
        ),
    ),
    "cme_crypto_hours_5day_2026": Citation(
        _WIKI_247,
        (
            "Current Cryptocurrency Futures and Options Schedule Day Type Close Pre-Open/Open "
            "Sunday Sunday startup - 4:00 to 5:00 p.m. CT Monday through Friday Daily Maintenance "
            "Window (with Trade Date roll) 4:00 to 4:45 p.m. CT 4:45 to 5:00 p.m. CT"
        ),
        note=(
            "CME client systems wiki page 1283194884 (version 2026-08-14): the schedule before "
            "24/7."
        ),
    ),
    "cme_crypto_24_7_launch": Citation(
        _PR_2026_02_19,
        (
            "Beginning Friday, May 29 at 4:00 p.m. CT , CME Group Cryptocurrency futures and "
            "options will trade continuously on CME Globex with at least a two-hour weekly "
            "maintenance period over the weekend. All holiday or weekend trading from Friday "
            "evening through Sunday evening will have a trade date of the following business day, "
            "with clearing, settlement and regulatory reporting processed the following business "
            "day as well."
        ),
        _PR_2026_06_01,
        (
            "CME Group, the world's leading derivatives marketplace, today announced it launched "
            "24/7 trading for Cryptocurrency futures and options. The expanded trading hours, "
            "which went live on Friday, May 29, mark a significant milestone"
        ),
        note=(
            "CME Group press releases of 2026-02-19 (announcement, 'pending regulatory review') "
            "and 2026-06-01 (launch confirmed). The space in 'CT ,' is the page's own markup (a "
            "link or span boundary), kept verbatim."
        ),
    ),
    "cme_crypto_24_7_article_k7_036": Citation(
        _ARTICLE_247,
        (
            "Starting on May 29, 2026, pending regulatory review, we are transitioning our "
            "Cryptocurrency futures and options to 24/7 trading."
        ),
        note=(
            "CME Group article 'Aligning Cryptocurrency Derivatives with Spot Markets: Measuring "
            "the 24/7 Trading Opportunity' (source K7-036 of the Stage E.0 registry), Wayback "
            "capture 2026-05-13. K7-036 is this article; the launch itself is confirmed by CME's "
            "press release of 2026-06-01 (key 'cme_crypto_24_7_launch')."
        ),
    ),
    "cme_crypto_24_7_hours": Citation(
        _FAQ_CRYPTO,
        (
            "Globex 24/7 with the exception of the following maintenance windows: Monday through "
            "Friday: 4:00 p.m. to 4:02 p.m. CT (pre-open: 4:01 p.m. to 4:02 p.m. CT) Saturday: "
            "2:00 a.m. to 4:00 a.m. CT (pre-open: 3:45 a.m. to 4:00 a.m. CT)"
        ),
        _FAQ_CRYPTO,
        (
            "Cryptocurrency futures and options trade continuously on Globex. All holiday or "
            "weekend trading from Friday evening through Sunday evening has a trade date of the "
            "following business day, with clearing, settlement and regulatory reporting processed "
            "the following business day as well."
        ),
        note="CME's 'FAQ: Cryptocurrency Futures' (Wayback 2026-08-20), questions 4 and 6.",
    ),
    "cme_crypto_24_7_wiki": Citation(
        _WIKI_247,
        (
            "Future Cryptocurrency Futures and Options Schedule Day Type Close/Pause "
            "Pre-Open/Open Saturday Extended Maintenance Window Close: 2:00 a.m. to 3:45 a.m. CT "
            "Pre-open: 3:45 a.m. to 4:00 a.m. CT No cancel: 3:59:30 a.m. to 4:00:00 a.m. CT Open: "
            "4:00 a.m. CT Monday through Friday Daily Maintenance Window (with Trade Date roll) "
            "Close: 4:00:00 p.m. to 4:01:00 p.m. CT Pre-open: 4:01:00 p.m. to 4:01:30 p.m. CT No "
            "cancel: 4:01:30 p.m. to 4:02:00 p.m. CT Open: 4:02:00 p.m. CT"
        ),
        _WIKI_247,
        (
            "Example 3 - Friday Holiday Trading Schedule In the below example, Friday is a "
            "holiday. Therefore, the trade date after the Thursday maintenance is Monday."
        ),
        note="CME client systems wiki page 1283194884 (version 2026-08-14).",
    ),
    "cme_btc_settlement_2026": Citation(
        _WIKI_BITCOIN,
        (
            "CME Group determines the daily settlements for Bitcoin (BTC) futures based on CME "
            "Globex trading activity between 14:59:00 and 15:00:00 Central Time (CT), the "
            "settlement period."
        ),
        _WIKI_BITCOIN,
        (
            "The daily settlements in the Micro Bitcoin (MBT) futures contracts are derived "
            "directly from settlements in the Bitcoin (BTC) futures contracts. Daily settlements "
            "derived from the BTC will be copied directly to the MBT for each contract listing."
        ),
        note=(
            "CME client systems wiki, 'Bitcoin' settlement procedures (page 457318016, version of "
            "2026-02-12, still current when read on 2026-09-25, i.e. unchanged by the 24/7 "
            "launch)."
        ),
    ),
    "cme_settlement_time_details": Citation(
        _WIKI_SETTLE_TIMES,
        "Bitcoin 14:59:00-15:00:00 CT",
        note=(
            "CME client systems wiki, 'Daily Settlement Time Details' (page 457085528), read "
            "directly (file shared with the energy builder)."
        ),
    ),
    "cme_btc_settlement_2020": Citation(
        _WIKI_BITCOIN_OLD,
        (
            "CME Group staff determines the daily settlements for Bitcoin futures based on "
            "trading activity on CME Globex between 14:59:00 and 15:00:00 Central Time, the "
            "settlement period."
        ),
        note=(
            "CME's Bitcoin settlement procedure page as captured 2020-08-09 (page 'last modified "
            "on Jul 28, 2020')."
        ),
    ),
    "cme_mbt_settlement_2021": Citation(
        _MBT_FAQ,
        (
            "Daily settlement for Micro Bitcoin futures will be the same as Bitcoin futures. The "
            "daily settlement of the Bitcoin futures contract is based on the volume-weighted "
            "average price (VWAP) of CME Globex trades between 3:59:00 p.m. and 4:00:00 p.m. "
            "Eastern Time."
        ),
        note=(
            "CME's Micro Bitcoin futures FAQ (Wayback 2021-03-30): 3:59-4:00 p.m. ET = "
            "14:59-15:00 CT."
        ),
    ),
}
