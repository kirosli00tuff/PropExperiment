"""CME Globex calendar for the equity group: ES and MES (CME), NQ and MNQ, RTY and M2K (CME), YM
and MYM (CBOT), 2019-05-01..2026-06-19 (Stage E.2a Task 6; design D10, D11.3 and D14).

The holiday entries are data.cme_calendar's, re-exported here and not copied: HOLIDAYS,
CALENDAR_COVERAGE (2019-01-01..2026-12-31, wider than this stage's window and sourced across it),
assert_calendar_coverage, CalendarCoverageError, and the D.1f citations SOURCES_2019_2024 and
NO_ENTRY_FINDINGS_2019_2024. This module adds, without touching any entry:
- SOURCES_2025_2026: a CME citation for every 2025-01-01..2026-06-19 entry (the pinned 2025-2026
  block of data.cme_calendar carries grades but no citations). SOURCES merges both tables.
- NO_ENTRY_FINDINGS_E2A: CME-stated regular equity days next to holidays (NO_ENTRY_FINDINGS
  merges both tables).
- SESSIONS (data.calendars.SessionSpec), with SESSION_SOURCES: three regimes, split at the two
  dated CME changes found (below).
- PRODUCT_SOURCES: CME documents that put all eight products on one Globex schedule.
- LATE_OPENS (additive, the rates module's shape), with LATE_OPEN_SOURCES: the unscheduled CME
  Globex outage of 2025-11-28. data.group_session reads only HOLIDAYS and SESSIONS for the equity
  group, so this is information for the lead and the bar check; it changes no session.

Sources (all CME Group; cmegroup.com refuses automated fetches, so every CME file was read from a
Wayback Machine copy, except the CME client-wiki pages, read through their REST API, and a few
settlement notices read live through Firecrawl): the Globex holiday schedules (.xls, 2019-2022, row
"Equity Products" / "Equity"), the 2023 holiday summary PDFs (row "EQUITIES"), CME's
trading-hours-by-product service behind cmegroup.com/trading-hours.html (2023-2026, product 133
E-mini S&P 500 Futures; product 318 E-mini Dow for MLK Day 2026), contract-specification pages,
the CME Globex notice of 2021-06-21 and the CME/CBOT CFTC submission of 2021-06-11, Special
Executive Report SER-8591, the settlement-procedure pages of the CME client wiki, and CME's
price-limits page. Verbatim quotes, capture URLs, file hashes and the verbatim check per entry:
reports/stage_e2a_calendar_sources_equity.json and .md.

Grades as data.cme_calendar: status (``evidence``) "cme" | "secondary" | "unverified"; time
(``time_evidence``) "cme" | "secondary" | "inferred" | "unverified" | "n/a". The pinned 2025-2026
block also carries "empirical" (2025-07-04, 2026-04-03), which predates the rule reserving it for
the bar check; it is left byte-identical. Where a CME source found here would raise a grade that
the file may not change, the citation note says so and the report lists the proposal.

Session regimes (CT; every segment ends where trading stops, so a one-minute bar starting at
end - 1 minute is the last bar):
- 2019-05-01..2021-06-27: 17:00 (prior day) - 15:15 and 15:30 - 16:00, the 15:15-15:30 CT halt.
- 2021-06-28..2026-06-19: 17:00 (prior day) - 16:00. CME Globex notice 2021-06-21 and the CFTC
  submission of 2021-06-11: the halt was eliminated from trade date 2021-06-28 for all eight.
- The spec is also split at trade date 2020-10-26, when CME moved the daily settlement period of
  all eight products from 15:14:30-15:15:00 CT to 14:59:30-15:00:00 CT (SER-8591). The Globex
  hours did not change then; the split dates the D6 discrepancy below.

D6 confirmation (day_session_ct {"equity": (08:30, 15:00)}, D6's values, encoded unchanged): C
15:00 CT matches CME's daily settlement period (14:59:30-15:00:00 CT) from trade date 2020-10-26;
before it (2019-05-01..2020-10-23) CME settled all eight at 15:14:30-15:15:00 CT, so CME's C was
15:15 CT, not 15:00 (a discrepancy for the lead). O 08:30 CT is defined by no CME settlement
procedure; CME's price-limit rules use 8:30 a.m. CT as the start of the day-session limit regime
in every capture read (2019-2023).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time

from data.calendars import Segment, SessionSpec
from data.cme_calendar import (
    CALENDAR_COVERAGE,
    HOLIDAYS,
    NO_ENTRY_FINDINGS_2019_2024,
    SOURCES_2019_2024,
    CalendarCoverageError,
    Citation,
    Holiday,
    HolidayKind,
    assert_calendar_coverage,
)

__all__ = [
    "CALENDAR_COVERAGE", "EQUITY_PRODUCTS", "HOLIDAYS", "LATE_OPENS", "LATE_OPEN_SOURCES",
    "NO_ENTRY_FINDINGS", "NO_ENTRY_FINDINGS_2019_2024", "NO_ENTRY_FINDINGS_E2A", "PRODUCT_SOURCES",
    "SESSIONS", "SESSION_SOURCES", "SOURCES", "SOURCES_2019_2024", "SOURCES_2025_2026",
    "STAGE_WINDOW", "CalendarCoverageError", "Citation", "Holiday", "HolidayKind", "LateOpen",
    "assert_calendar_coverage",
]

EQUITY_PRODUCTS = ("ES", "MES", "NQ", "MNQ", "RTY", "M2K", "YM", "MYM")
STAGE_WINDOW = (date(2019, 5, 1), date(2026, 6, 19))  # design D10; SESSIONS cover exactly this

DAY_SESSION_CT = {"equity": (time(8, 30), time(15, 0))}  # design D6, encoded unchanged

# Globex segments (CT): with the 15:15-15:30 halt until trade date 2021-06-25, without it after.
_SEGMENTS_WITH_HALT = (Segment(-1, time(17, 0), 0, time(15, 15)),
                       Segment(0, time(15, 30), 0, time(16, 0)))
_SEGMENTS_NO_HALT = (Segment(-1, time(17, 0), 0, time(16, 0)),)

_WB = "https://web.archive.org/web/"
_CME = "https://www.cmegroup.com/"
_HC = _CME + "tools-information/holiday-calendar/files/"
_WIKI = "https://cmegroupclientsite.atlassian.net/wiki/rest/api/content/"


def _wb_svc(ts: str, from_day: str, to_day: str, t: str) -> str:
    """Wayback copy of CME's trading-hours-by-product request (the ten-product default set)."""
    return (f"{_WB}{ts}/{_CME}services/trading-hours-by-product?id=316,133,425,300,58,437,22,"
            f"8478,5201,10191&pageNumber=1&pageSize=999&sortAsc=true&fromEventDate={from_day}"
            f"&toEventDate={to_day}&isProtected&_t={t}")


_SVC_20241231_20241220 = _wb_svc("20241220155340", "2024-12-31", "2025-01-02", "1734710019538")
_SVC_20250119_20241220 = _wb_svc("20241220155340", "2025-01-19", "2025-01-21", "1734710019539")
_SVC_20250216_20241220 = _wb_svc("20241220155340", "2025-02-16", "2025-02-18", "1734710019540")
_SVC_20250417_20241220 = _wb_svc("20241220155340", "2025-04-17", "2025-04-19", "1734710019542")
_SVC_20250525_20241220 = _wb_svc("20241220155340", "2025-05-25", "2025-05-27", "1734710019543")
_SVC_20250618_20241220 = _wb_svc("20241220155340", "2025-06-18", "2025-06-20", "1734710019544")
_SVC_20250703_20241220 = _wb_svc("20241220155340", "2025-07-03", "2025-07-05", "1734710019545")
_SVC_20250831_20241220 = _wb_svc("20241220155340", "2025-08-31", "2025-09-02", "1734710019546")
_SVC_20251126_20241220 = _wb_svc("20241220155340", "2025-11-26", "2025-11-28", "1734710019547")
_SVC_20251224_20260129 = _wb_svc("20260129012143", "2025-12-24", "2025-12-26", "1769649703064")
_SVC_20251231_20260129 = _wb_svc("20260129012143", "2025-12-31", "2026-01-02", "1769649703066")
_SVC_20260118_20260129 = _wb_svc("20260129012143", "2026-01-18", "2026-01-20", "1769649703068")
_SVC_20260215_20260129 = _wb_svc("20260129012143", "2026-02-15", "2026-02-17", "1769649703070")
_SVC_20260401_20260129 = _wb_svc("20260129012143", "2026-04-01", "2026-04-03", "1769649703072")
_SVC_20260524_20260129 = _wb_svc("20260129012143", "2026-05-24", "2026-05-26", "1769649703074")
_SVC_20260617_20260129 = _wb_svc("20260129012143", "2026-06-17", "2026-06-19", "1769649703075")

_SVC_20251126_20260129 = _wb_svc("20260129012143", "2025-11-26", "2025-11-28", "1769649703060")
_MOURNING_2025 = f"{_WB}20250218194143/{_CME}trading-hours/files/day-of-mourning-january-9-2024.pdf"
_Z19 = f"{_WB}20210126094837/{_HC}2019-holiday-calendars.zip"
_Z20 = f"{_WB}20260730111834/{_HC}2020-holiday-calendars.zip"
_Z21 = f"{_WB}20260830100327/{_HC}2021-holiday-calendars.zip"

_PLAN = ("CME's trading-hours-by-product service (the data behind cmegroup.com/trading-hours."
         "html), record for product 133 'E-mini S&P 500 Futures' (ES), which stands for the "
         "equity group; 'preopen' is CME's halt state (order entry, no matching).")
_KEEP = ("The entry lies in data.cme_calendar's pinned 2025-2026 block (commit 9cbd815, "
         "byte-identical), so its grades are left as they are")


def _note(what: str, proposal: str = "") -> str:
    tail = f"; proposed: {proposal}" if proposal else ""
    return f"{_PLAN} {what} {_KEEP}{tail}."


_NOTES_2526: dict[date, str] = {
    date(2025, 1, 1): _note("Closed 2024-12-31 16:00 CT, no event on 2025-01-01 before the "
                            "17:00 CT open for trade date 2025-01-02: a full closure."),
    date(2025, 1, 20): _note("12:00 CT halt, 17:00 CT reopen.",
                             "time_evidence 'cme' (file: secondary)"),
    date(2025, 2, 17): _note("12:00 CT halt, 17:00 CT reopen.",
                             "time_evidence 'cme' (file: secondary)"),
    date(2025, 4, 18): _note("Closed 2025-04-17 16:00 CT and no event on 2025-04-18 (Good "
                             "Friday): a full closure."),
    date(2025, 5, 26): _note("12:00 CT halt, 17:00 CT reopen.",
                             "time_evidence 'cme' (file: secondary)"),
    date(2025, 6, 19): _note("12:00 CT halt, 17:00 CT reopen.",
                             "time_evidence 'cme' (file: secondary)"),
    date(2025, 7, 3): _note("'closed' at 12:15 CT, reopen 17:00 CT for trade date 2025-07-04.",
                            "time_evidence 'cme' (file: inferred)"),
    date(2025, 7, 4): _note("'closed' at 12:00 CT for trade date 2025-07-04 (a Friday; next "
                            "open Sunday 17:00 CT).",
                            "time_evidence 'cme' (file: empirical, from the MES bars)"),
    date(2025, 9, 1): _note("12:00 CT halt, 17:00 CT reopen.",
                            "time_evidence 'cme' (file: secondary)"),
    date(2025, 11, 27): _note("12:00 CT halt, 17:00 CT reopen.",
                              "time_evidence 'cme' (file: secondary)"),
    date(2025, 11, 28): _note("The plan (capture 2024-12-20) has only the 12:15 CT close; the "
                              "2026-01-29 capture adds the unscheduled outage (LATE_OPENS).",
                              "time_evidence 'cme' (file: inferred)"),
    date(2025, 12, 24): _note("'closed' at 12:15 CT (capture 2026-01-29; the 2024-12-20 "
                              "capture had no events for these dates).",
                              "time_evidence 'cme' (file: inferred)"),
    date(2025, 12, 25): _note("Closed 2025-12-24 12:15 CT, reopen 2025-12-25 17:00 CT for trade "
                              "date 2025-12-26: a full closure."),
    date(2026, 1, 1): _note("Closed 2025-12-31 16:00 CT, reopen 2026-01-01 17:00 CT for trade "
                            "date 2026-01-02: a full closure."),
    date(2026, 1, 19): _note("12:00 CT halt, 17:00 CT reopen. CME's record for product 318, the "
                             "E-mini Dow (YM, CBOT), gives the same events (PRODUCT_SOURCES).",
                             "time_evidence 'cme' (file: secondary)"),
    date(2026, 2, 16): _note("12:00 CT halt, 17:00 CT reopen.",
                             "time_evidence 'cme' (file: secondary)"),
    date(2026, 4, 3): _note("'closed' at 08:15 CT (jobs-report Good Friday) after the Thursday "
                            "17:00 CT open for trade date 2026-04-03.",
                            "time_evidence 'cme' (file: empirical, from the MES bars)"),
    date(2026, 5, 25): _note("12:00 CT halt, 17:00 CT reopen.",
                             "time_evidence 'cme' (file: secondary)"),
    date(2026, 6, 19): _note("'closed' at 12:00 CT (a Friday; trade date 2026-06-22 per CME, "
                             "which books the holiday to the next trade date).",
                             "time_evidence 'cme' (file: secondary)"),
}

SOURCES_2025_2026: dict[date, Citation] = {
    date(2025, 1, 9): Citation(
        _MOURNING_2025,
        "U.S. National Day of Mourning Trading Schedule ... PRODUCT NAME JANUARY 9, 2025 "
        "TRADING FLOOR CLEARPORT ... CME GROUP US EQUITIES CLOSE at 8:30 AM CT",
        _MOURNING_2025,
        "CME GROUP US EQUITIES CLOSE at 8:30 AM CT",
        note="CME's National Day of Mourning (President Carter) trading schedule, file named "
             "'...january-9-2024.pdf' by CME but dated January 9, 2025 in its table. Equities "
             "closed at 08:30 CT; the calendar keeps the 17:00 CT reopen of the next trade date. "
             "Grades cme / cme as in the file."),
    date(2025, 1, 1): Citation(
        _SVC_20241231_20241220,
        '"globex":"ES","prodGroup":"ES","name":"E-mini S&P 500 Futures",'
        '"id":133 ... {"groupCode":"ES","eventDate":"2024-12-31",'
        '"events":[{"tradingDate":"2024-12-31","eventTime":"16:00",'
        '"marketEventType":"closed"}]} ... {"groupCode":"ES","eventDate":"2025-01-01",'
        '"events":[{"tradingDate":"2025-01-02","eventTime":"16:00","marketEventType":"preopen"},'
        '{"tradingDate":"2025-01-02","eventTime":"17:00","marketEventType":"open"}]}',
        _SVC_20241231_20241220,
        '{"groupCode":"ES","eventDate":"2025-01-01","events":[{"tradingDate":"2025-01-02",'
        '"eventTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2025-01-02",'
        '"eventTime":"17:00","marketEventType":"open"}]}',
        note=_NOTES_2526[date(2025, 1, 1)]),
    date(2025, 1, 20): Citation(
        _SVC_20250119_20241220,
        '"globex":"ES","prodGroup":"ES","name":"E-mini S&P 500 Futures",'
        '"id":133 ... {"groupCode":"ES","eventDate":"2025-01-19",'
        '"events":[{"tradingDate":"2025-01-21","eventTime":"16:00","marketEventType":"preopen"},'
        '{"tradingDate":"2025-01-21","eventTime":"17:00",'
        '"marketEventType":"open"}]} ... {"groupCode":"ES","eventDate":"2025-01-20",'
        '"events":[{"tradingDate":"2025-01-21","eventTime":"12:00","marketEventType":"preopen"},'
        '{"tradingDate":"2025-01-21","eventTime":"17:00","marketEventType":"open"}]}',
        _SVC_20250119_20241220,
        '{"groupCode":"ES","eventDate":"2025-01-20","events":[{"tradingDate":"2025-01-21",'
        '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2025-01-21",'
        '"eventTime":"17:00","marketEventType":"open"}]}',
        note=_NOTES_2526[date(2025, 1, 20)]),
    date(2025, 2, 17): Citation(
        _SVC_20250216_20241220,
        '"globex":"ES","prodGroup":"ES","name":"E-mini S&P 500 Futures",'
        '"id":133 ... {"groupCode":"ES","eventDate":"2025-02-16",'
        '"events":[{"tradingDate":"2025-02-18","eventTime":"16:00","marketEventType":"preopen"},'
        '{"tradingDate":"2025-02-18","eventTime":"17:00",'
        '"marketEventType":"open"}]} ... {"groupCode":"ES","eventDate":"2025-02-17",'
        '"events":[{"tradingDate":"2025-02-18","eventTime":"12:00","marketEventType":"preopen"},'
        '{"tradingDate":"2025-02-18","eventTime":"17:00","marketEventType":"open"}]}',
        _SVC_20250216_20241220,
        '{"groupCode":"ES","eventDate":"2025-02-17","events":[{"tradingDate":"2025-02-18",'
        '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2025-02-18",'
        '"eventTime":"17:00","marketEventType":"open"}]}',
        note=_NOTES_2526[date(2025, 2, 17)]),
    date(2025, 4, 18): Citation(
        _SVC_20250417_20241220,
        '"globex":"ES","prodGroup":"ES","name":"E-mini S&P 500 Futures",'
        '"id":133 ... {"groupCode":"ES","eventDate":"2025-04-17",'
        '"events":[{"tradingDate":"2025-04-17","eventTime":"16:00",'
        '"marketEventType":"closed"}]} ... {"groupCode":"ES","eventDate":"2025-04-18","events":[]}',
        _SVC_20250417_20241220,
        '{"groupCode":"ES","eventDate":"2025-04-18","events":[]}',
        note=_NOTES_2526[date(2025, 4, 18)]),
    date(2025, 5, 26): Citation(
        _SVC_20250525_20241220,
        '"globex":"ES","prodGroup":"ES","name":"E-mini S&P 500 Futures",'
        '"id":133 ... {"groupCode":"ES","eventDate":"2025-05-25",'
        '"events":[{"tradingDate":"2025-05-27","eventTime":"16:00","marketEventType":"preopen"},'
        '{"tradingDate":"2025-05-27","eventTime":"17:00",'
        '"marketEventType":"open"}]} ... {"groupCode":"ES","eventDate":"2025-05-26",'
        '"events":[{"tradingDate":"2025-05-27","eventTime":"12:00","marketEventType":"preopen"},'
        '{"tradingDate":"2025-05-27","eventTime":"17:00","marketEventType":"open"}]}',
        _SVC_20250525_20241220,
        '{"groupCode":"ES","eventDate":"2025-05-26","events":[{"tradingDate":"2025-05-27",'
        '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2025-05-27",'
        '"eventTime":"17:00","marketEventType":"open"}]}',
        note=_NOTES_2526[date(2025, 5, 26)]),
    date(2025, 6, 19): Citation(
        _SVC_20250618_20241220,
        '"globex":"ES","prodGroup":"ES","name":"E-mini S&P 500 Futures",'
        '"id":133 ... {"groupCode":"ES","eventDate":"2025-06-18",'
        '"events":[{"tradingDate":"2025-06-18","eventTime":"16:00","marketEventType":"closed"},'
        '{"tradingDate":"2025-06-20","eventTime":"16:45","marketEventType":"preopen"},'
        '{"tradingDate":"2025-06-20","eventTime":"17:00",'
        '"marketEventType":"open"}]} ... {"groupCode":"ES","eventDate":"2025-06-19",'
        '"events":[{"tradingDate":"2025-06-20","eventTime":"12:00","marketEventType":"preopen"},'
        '{"tradingDate":"2025-06-20","eventTime":"17:00","marketEventType":"open"}]}',
        _SVC_20250618_20241220,
        '{"groupCode":"ES","eventDate":"2025-06-19","events":[{"tradingDate":"2025-06-20",'
        '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2025-06-20",'
        '"eventTime":"17:00","marketEventType":"open"}]}',
        note=_NOTES_2526[date(2025, 6, 19)]),
    date(2025, 7, 3): Citation(
        _SVC_20250703_20241220,
        '"globex":"ES","prodGroup":"ES","name":"E-mini S&P 500 Futures",'
        '"id":133 ... {"groupCode":"ES","eventDate":"2025-07-03",'
        '"events":[{"tradingDate":"2025-07-03","eventTime":"12:15","marketEventType":"closed"},'
        '{"tradingDate":"2025-07-04","eventTime":"16:45","marketEventType":"preopen"},'
        '{"tradingDate":"2025-07-04","eventTime":"17:00","marketEventType":"open"}]}',
        _SVC_20250703_20241220,
        '{"groupCode":"ES","eventDate":"2025-07-03","events":[{"tradingDate":"2025-07-03",'
        '"eventTime":"12:15","marketEventType":"closed"},{"tradingDate":"2025-07-04",'
        '"eventTime":"16:45","marketEventType":"preopen"},{"tradingDate":"2025-07-04",'
        '"eventTime":"17:00","marketEventType":"open"}]}',
        note=_NOTES_2526[date(2025, 7, 3)]),
    date(2025, 7, 4): Citation(
        _SVC_20250703_20241220,
        '"globex":"ES","prodGroup":"ES","name":"E-mini S&P 500 Futures",'
        '"id":133 ... {"groupCode":"ES","eventDate":"2025-07-03",'
        '"events":[{"tradingDate":"2025-07-03","eventTime":"12:15","marketEventType":"closed"},'
        '{"tradingDate":"2025-07-04","eventTime":"16:45","marketEventType":"preopen"},'
        '{"tradingDate":"2025-07-04","eventTime":"17:00",'
        '"marketEventType":"open"}]} ... {"groupCode":"ES","eventDate":"2025-07-04",'
        '"events":[{"tradingDate":"2025-07-04","eventTime":"12:00","marketEventType":"closed"}]}',
        _SVC_20250703_20241220,
        '{"groupCode":"ES","eventDate":"2025-07-04","events":[{"tradingDate":"2025-07-04",'
        '"eventTime":"12:00","marketEventType":"closed"}]}',
        note=_NOTES_2526[date(2025, 7, 4)]),
    date(2025, 9, 1): Citation(
        _SVC_20250831_20241220,
        '"globex":"ES","prodGroup":"ES","name":"E-mini S&P 500 Futures",'
        '"id":133 ... {"groupCode":"ES","eventDate":"2025-08-31",'
        '"events":[{"tradingDate":"2025-09-02","eventTime":"16:00","marketEventType":"preopen"},'
        '{"tradingDate":"2025-09-02","eventTime":"17:00",'
        '"marketEventType":"open"}]} ... {"groupCode":"ES","eventDate":"2025-09-01",'
        '"events":[{"tradingDate":"2025-09-02","eventTime":"12:00","marketEventType":"preopen"},'
        '{"tradingDate":"2025-09-02","eventTime":"17:00","marketEventType":"open"}]}',
        _SVC_20250831_20241220,
        '{"groupCode":"ES","eventDate":"2025-09-01","events":[{"tradingDate":"2025-09-02",'
        '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2025-09-02",'
        '"eventTime":"17:00","marketEventType":"open"}]}',
        note=_NOTES_2526[date(2025, 9, 1)]),
    date(2025, 11, 27): Citation(
        _SVC_20251126_20241220,
        '"globex":"ES","prodGroup":"ES","name":"E-mini S&P 500 Futures",'
        '"id":133 ... {"groupCode":"ES","eventDate":"2025-11-26",'
        '"events":[{"tradingDate":"2025-11-26","eventTime":"16:00","marketEventType":"closed"},'
        '{"tradingDate":"2025-11-28","eventTime":"16:45","marketEventType":"preopen"},'
        '{"tradingDate":"2025-11-28","eventTime":"17:00",'
        '"marketEventType":"open"}]} ... {"groupCode":"ES","eventDate":"2025-11-27",'
        '"events":[{"tradingDate":"2025-11-28","eventTime":"12:00","marketEventType":"preopen"},'
        '{"tradingDate":"2025-11-28","eventTime":"17:00","marketEventType":"open"}]}',
        _SVC_20251126_20241220,
        '{"groupCode":"ES","eventDate":"2025-11-27","events":[{"tradingDate":"2025-11-28",'
        '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2025-11-28",'
        '"eventTime":"17:00","marketEventType":"open"}]}',
        note=_NOTES_2526[date(2025, 11, 27)]),
    date(2025, 11, 28): Citation(
        _SVC_20251126_20241220,
        '"globex":"ES","prodGroup":"ES","name":"E-mini S&P 500 Futures",'
        '"id":133 ... {"groupCode":"ES","eventDate":"2025-11-27",'
        '"events":[{"tradingDate":"2025-11-28","eventTime":"12:00","marketEventType":"preopen"},'
        '{"tradingDate":"2025-11-28","eventTime":"17:00",'
        '"marketEventType":"open"}]} ... {"groupCode":"ES","eventDate":"2025-11-28",'
        '"events":[{"tradingDate":"2025-11-28","eventTime":"12:15","marketEventType":"closed"}]}',
        _SVC_20251126_20241220,
        '{"groupCode":"ES","eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28",'
        '"eventTime":"12:15","marketEventType":"closed"}]}',
        note=_NOTES_2526[date(2025, 11, 28)]),
    date(2025, 12, 24): Citation(
        _SVC_20251224_20260129,
        '"globex":"ES","prodGroup":"ES","name":"E-mini S&P 500 Futures",'
        '"id":133 ... {"groupCode":"ES","eventDate":"2025-12-24",'
        '"events":[{"tradingDate":"2025-12-24","eventTime":"12:15","marketEventType":"closed"}]}',
        _SVC_20251224_20260129,
        '{"groupCode":"ES","eventDate":"2025-12-24","events":[{"tradingDate":"2025-12-24",'
        '"eventTime":"12:15","marketEventType":"closed"}]}',
        note=_NOTES_2526[date(2025, 12, 24)]),
    date(2025, 12, 25): Citation(
        _SVC_20251224_20260129,
        '"globex":"ES","prodGroup":"ES","name":"E-mini S&P 500 Futures",'
        '"id":133 ... {"groupCode":"ES","eventDate":"2025-12-24",'
        '"events":[{"tradingDate":"2025-12-24","eventTime":"12:15",'
        '"marketEventType":"closed"}]} ... {"groupCode":"ES","eventDate":"2025-12-25",'
        '"events":[{"tradingDate":"2025-12-26","eventTime":"16:00","marketEventType":"preopen"},'
        '{"tradingDate":"2025-12-26","eventTime":"17:00","marketEventType":"open"}]}',
        _SVC_20251224_20260129,
        '{"groupCode":"ES","eventDate":"2025-12-25","events":[{"tradingDate":"2025-12-26",'
        '"eventTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2025-12-26",'
        '"eventTime":"17:00","marketEventType":"open"}]}',
        note=_NOTES_2526[date(2025, 12, 25)]),
    date(2026, 1, 1): Citation(
        _SVC_20251231_20260129,
        '"globex":"ES","prodGroup":"ES","name":"E-mini S&P 500 Futures",'
        '"id":133 ... {"groupCode":"ES","eventDate":"2025-12-31",'
        '"events":[{"tradingDate":"2025-12-31","eventTime":"16:00",'
        '"marketEventType":"closed"}]} ... {"groupCode":"ES","eventDate":"2026-01-01",'
        '"events":[{"tradingDate":"2026-01-02","eventTime":"16:00","marketEventType":"preopen"},'
        '{"tradingDate":"2026-01-02","eventTime":"17:00","marketEventType":"open"}]}',
        _SVC_20251231_20260129,
        '{"groupCode":"ES","eventDate":"2026-01-01","events":[{"tradingDate":"2026-01-02",'
        '"eventTime":"16:00","marketEventType":"preopen"},{"tradingDate":"2026-01-02",'
        '"eventTime":"17:00","marketEventType":"open"}]}',
        note=_NOTES_2526[date(2026, 1, 1)]),
    date(2026, 1, 19): Citation(
        _SVC_20260118_20260129,
        '"globex":"ES","prodGroup":"ES","name":"E-mini S&P 500 Futures",'
        '"id":133 ... {"groupCode":"ES","eventDate":"2026-01-18",'
        '"events":[{"tradingDate":"2026-01-20","eventTime":"16:00","marketEventType":"preopen"},'
        '{"tradingDate":"2026-01-20","eventTime":"17:00",'
        '"marketEventType":"open"}]} ... {"groupCode":"ES","eventDate":"2026-01-19",'
        '"events":[{"tradingDate":"2026-01-20","eventTime":"12:00","marketEventType":"preopen"},'
        '{"tradingDate":"2026-01-20","eventTime":"17:00","marketEventType":"open"}]}',
        _SVC_20260118_20260129,
        '{"groupCode":"ES","eventDate":"2026-01-19","events":[{"tradingDate":"2026-01-20",'
        '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2026-01-20",'
        '"eventTime":"17:00","marketEventType":"open"}]}',
        note=_NOTES_2526[date(2026, 1, 19)]),
    date(2026, 2, 16): Citation(
        _SVC_20260215_20260129,
        '"globex":"ES","prodGroup":"ES","name":"E-mini S&P 500 Futures",'
        '"id":133 ... {"groupCode":"ES","eventDate":"2026-02-15",'
        '"events":[{"tradingDate":"2026-02-17","eventTime":"16:00","marketEventType":"preopen"},'
        '{"tradingDate":"2026-02-17","eventTime":"17:00",'
        '"marketEventType":"open"}]} ... {"groupCode":"ES","eventDate":"2026-02-16",'
        '"events":[{"tradingDate":"2026-02-17","eventTime":"12:00","marketEventType":"preopen"},'
        '{"tradingDate":"2026-02-17","eventTime":"17:00","marketEventType":"open"}]}',
        _SVC_20260215_20260129,
        '{"groupCode":"ES","eventDate":"2026-02-16","events":[{"tradingDate":"2026-02-17",'
        '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2026-02-17",'
        '"eventTime":"17:00","marketEventType":"open"}]}',
        note=_NOTES_2526[date(2026, 2, 16)]),
    date(2026, 4, 3): Citation(
        _SVC_20260401_20260129,
        '"globex":"ES","prodGroup":"ES","name":"E-mini S&P 500 Futures",'
        '"id":133 ... {"groupCode":"ES","eventDate":"2026-04-02",'
        '"events":[{"tradingDate":"2026-04-02","eventTime":"16:00","marketEventType":"closed"},'
        '{"tradingDate":"2026-04-03","eventTime":"16:45","marketEventType":"preopen"},'
        '{"tradingDate":"2026-04-03","eventTime":"17:00",'
        '"marketEventType":"open"}]} ... {"groupCode":"ES","eventDate":"2026-04-03",'
        '"events":[{"tradingDate":"2026-04-03","eventTime":"08:15","marketEventType":"closed"}]}',
        _SVC_20260401_20260129,
        '{"groupCode":"ES","eventDate":"2026-04-03","events":[{"tradingDate":"2026-04-03",'
        '"eventTime":"08:15","marketEventType":"closed"}]}',
        note=_NOTES_2526[date(2026, 4, 3)]),
    date(2026, 5, 25): Citation(
        _SVC_20260524_20260129,
        '"globex":"ES","prodGroup":"ES","name":"E-mini S&P 500 Futures",'
        '"id":133 ... {"groupCode":"ES","eventDate":"2026-05-24",'
        '"events":[{"tradingDate":"2026-05-26","eventTime":"16:00","marketEventType":"preopen"},'
        '{"tradingDate":"2026-05-26","eventTime":"17:00",'
        '"marketEventType":"open"}]} ... {"groupCode":"ES","eventDate":"2026-05-25",'
        '"events":[{"tradingDate":"2026-05-26","eventTime":"12:00","marketEventType":"preopen"},'
        '{"tradingDate":"2026-05-26","eventTime":"17:00","marketEventType":"open"}]}',
        _SVC_20260524_20260129,
        '{"groupCode":"ES","eventDate":"2026-05-25","events":[{"tradingDate":"2026-05-26",'
        '"eventTime":"12:00","marketEventType":"preopen"},{"tradingDate":"2026-05-26",'
        '"eventTime":"17:00","marketEventType":"open"}]}',
        note=_NOTES_2526[date(2026, 5, 25)]),
    date(2026, 6, 19): Citation(
        _SVC_20260617_20260129,
        '"globex":"ES","prodGroup":"ES","name":"E-mini S&P 500 Futures",'
        '"id":133 ... {"groupCode":"ES","eventDate":"2026-06-18",'
        '"events":[{"tradingDate":"2026-06-18","eventTime":"16:00","marketEventType":"closed"},'
        '{"tradingDate":"2026-06-22","eventTime":"16:45","marketEventType":"preopen"},'
        '{"tradingDate":"2026-06-22","eventTime":"17:00",'
        '"marketEventType":"open"}]} ... {"groupCode":"ES","eventDate":"2026-06-19",'
        '"events":[{"tradingDate":"2026-06-22","eventTime":"12:00","marketEventType":"closed"}]}',
        _SVC_20260617_20260129,
        '{"groupCode":"ES","eventDate":"2026-06-19","events":[{"tradingDate":"2026-06-22",'
        '"eventTime":"12:00","marketEventType":"closed"}]}',
        note=_NOTES_2526[date(2026, 6, 19)]),
}

SOURCES: dict[date, Citation] = {**SOURCES_2019_2024, **SOURCES_2025_2026}

# CME-stated regular equity days next to holidays: no entry, and the absence is a finding.
NO_ENTRY_FINDINGS_E2A: dict[date, Citation] = {
    date(2019, 12, 31): Citation(
        _Z19,
        "Trade Date|Tuesday, December 31||Thursday,  January 2 ... Calendar Date|Tuesday, "
        "December 31|Wednesday, January 1|Wednesday, January 1||||||Thursday, Jan 2 ... Equity "
        "Products|16:00|Globex Closed|16:00|17:00|||||||16:00",
        note="globex-trading-schedules/2019-2020-new-years-holiday-schedule.xls in CME's 2019 "
             "zip: New Year's Eve 2019 closes at the regular 16:00 CT."),
    date(2020, 12, 31): Citation(
        _Z20,
        "Trade Date|Thursday, December 31||Monday,  January 4 ... Calendar Date|Thursday, "
        "December 31|Friday, January 1|Sunday, January 3||||||Monday, January 4 ... Equity "
        "Products|16:00|Globex Closed|16:00|17:00|||||||16:00",
        note="2021-new-years-holiday-schedule.xls in CME's 2020 zip: New Year's Eve 2020 closes "
             "at the regular 16:00 CT (and 2021-01-01 is 'Globex Closed', the CME source for "
             "the entry the file grades unverified)."),
    date(2021, 12, 23): Citation(
        _Z21,
        "Trade Date|Thursday,December 23|Globex Closed|Monday December 27 ... Equity |Regular "
        "per Product|Closed for Christmas|Regular @ 1700 CT / 2300 UTC|Regular @ 1600 CT / "
        "2200 UTC",
        note="2021-christmas-holiday-schedule-compact.xls in CME's 2021 zip: Thursday "
             "2021-12-23 (before the Friday 2021-12-24 closure) is a regular day."),
    date(2021, 12, 31): Citation(
        f"{_WB}20220102130655/{_HC}2022-new-years-holiday-schedule.xls",
        "Calendar Date|Thursday, December 30||||||||||Friday, December 31||||||||Sunday, "
        "January 2||||||Monday, January 3 ... Equity Products|16:00|16:45|17:00|||||||||||16:00"
        "|||||16:00|17:00|NORMAL||||SCHEDULE",
        note="New Year's Eve 2021 closes at the regular 16:00 CT; Monday 2022-01-03 is a NORMAL "
             "SCHEDULE day (matches NO_ENTRY_FINDINGS_2019_2024's 2022-01-03)."),
    date(2022, 7, 1): Citation(
        f"{_WB}20220704065431/{_HC}2022-independence-day-holiday-schedule-compact.xls",
        "Calendar Date|Friday July 1|Sunday July 3|Monday July 4|Monday July 4 ... Product|CLOSE"
        "|OPEN|HALT|OPEN ... Equity |Regular @ 1600 CT / 2100 UTC",
        note="Friday 2022-07-01 before the Monday Independence Day halt: regular 16:00 CT close, "
             "no early close."),
    date(2022, 12, 23): Citation(
        f"{_WB}20220704065430/{_HC}2022-christmas-holiday-schedule.xls",
        "Calendar Date|Friday, December 23||||||||Monday, December 26||||||||||||||||Tuesday, "
        "December 27 ... Equity Products|16:00||||||||Globex Closed||||||||||16:00|17:00|||||||"
        "16:00",
        note="Friday 2022-12-23 before the Monday Christmas closure: regular 16:00 CT close."),
    date(2022, 12, 30): Citation(
        f"{_WB}20220704065501/{_HC}2023-new-years-holiday-schedule.xls",
        "Calendar Date|Friday, December 30||||Monday, January 2|Monday, January 2||||||Tuesday, "
        "January 3 ... Equity Products|16:00||||Globex Closed|16:00|17:00||||||||16:00",
        note="Friday 2022-12-30 before the Monday New Year's closure: regular 16:00 CT close."),
    date(2024, 12, 31): Citation(
        _SVC_20241231_20241220,
        '{"groupCode":"ES","eventDate":"2024-12-31","events":[{"tradingDate":"2024-12-31",'
        '"eventTime":"16:00","marketEventType":"closed"}]}',
        note="ES closes at the regular 16:00 CT on New Year's Eve 2024 (a holdout-2 date)."),
    date(2025, 12, 31): Citation(
        _SVC_20251231_20260129,
        '{"groupCode":"ES","eventDate":"2025-12-31","events":[{"tradingDate":"2025-12-31",'
        '"eventTime":"16:00","marketEventType":"closed"}]}',
        note="ES closes at the regular 16:00 CT on New Year's Eve 2025."),
    date(2026, 4, 2): Citation(
        _SVC_20260401_20260129,
        '{"groupCode":"ES","eventDate":"2026-04-02","events":[{"tradingDate":"2026-04-02",'
        '"eventTime":"16:00","marketEventType":"closed"},{"tradingDate":"2026-04-03",'
        '"eventTime":"16:45","marketEventType":"preopen"},{"tradingDate":"2026-04-03",'
        '"eventTime":"17:00","marketEventType":"open"}]}',
        note="Thursday before the jobs-report Good Friday 2026: regular 16:00 CT close and 17:00 "
             "CT open for the abbreviated 2026-04-03 session."),
}

NO_ENTRY_FINDINGS: dict[date, Citation] = {**NO_ENTRY_FINDINGS_2019_2024, **NO_ENTRY_FINDINGS_E2A}


@dataclass(frozen=True)
class LateOpen:
    """A trade date whose Globex session did not trade from its regular start: trading stopped at
    ``halt_from_ct`` on the calendar day ``halt_from_offset_days`` from ``day`` (None: the stop
    time is in no source retrieved) and resumed at ``open_ct`` CT on ``day``. Grades as for
    Holiday. Same fields as data.calendars.rates.LateOpen; additive to the interface."""

    day: date
    name: str
    open_ct: time
    evidence: str
    time_evidence: str
    halt_from_ct: time | None = None
    halt_from_offset_days: int = -1


LATE_OPENS: dict[date, LateOpen] = {
    date(2025, 11, 28): LateOpen(
        date(2025, 11, 28), "Globex outage (data-center cooling failure)", time(7, 30), "cme",
        "cme"),
}

LATE_OPEN_SOURCES: dict[date, Citation] = {
    date(2025, 11, 28): Citation(
        _SVC_20251126_20260129,
        '"globex":"ES","prodGroup":"ES","name":"E-mini S&P 500 Futures","id":133 ... '
        '{"groupCode":"ES","eventDate":"2025-11-28","events":[{"tradingDate":"2025-11-28",'
        '"eventTime":"07:00","marketEventType":"preopen"},{"tradingDate":"2025-11-28",'
        '"eventTime":"07:30","marketEventType":"open"},{"tradingDate":"2025-11-28",'
        '"eventTime":"12:15","marketEventType":"closed"}]}',
        _SVC_20251126_20260129,
        '{"tradingDate":"2025-11-28","eventTime":"07:30","marketEventType":"open"}',
        note="Unscheduled. CME's ES record for eventDate 2025-11-28 in the 2026-01-29 capture "
             "adds 'preopen' 07:00 and 'open' 07:30 CT before the scheduled 12:15 CT close; the "
             "2024-12-20 capture (the plan) has only the close. The time trading stopped after "
             "the Thursday 2025-11-27 17:00 CT reopen is in no CME document retrieved "
             "(halt_from_ct None). The rates, energy and metals calendars record the same outage "
             "for their groups. data.cme_calendar does not record it and may not be changed "
             "here; the report proposes it to the lead. A research-window date: the bar check "
             "(Task 7) sees it."),
}

SESSIONS: tuple[SessionSpec, ...] = (
    SessionSpec(
        valid_from=date(2019, 5, 1),
        valid_to=date(2020, 10, 25),
        segments=_SEGMENTS_WITH_HALT,
        day_session_ct=DAY_SESSION_CT,
        source="cme_hours_with_halt",
        note=(
            "Globex 17:00 CT (prior day) to 16:00 CT with the 15:15-15:30 CT halt, all eight "
            "products (SESSION_SOURCES 'cme_hours_with_halt', 'cme_halt_removal_notice'). D6 "
            "confirmation: DISCREPANCY. CME's daily settlement period for ES, MES, NQ, MNQ, RTY, "
            "M2K, YM and MYM in this span was 15:14:30-15:15:00 CT, so CME's C was 15:15 CT "
            "(SESSION_SOURCES 'cme_settlement_1515', 'cme_settlement_moved_to_1500'); D6's C "
            "15:00 CT is encoded unchanged and the lead rules. O 08:30 CT: no CME settlement "
            "procedure defines it; CME's price limits used 8:30 a.m.-3:00 p.m. CT as the day "
            "regime ('cme_price_limit_day_regime'). MES's first trade date in the D.1f "
            "confirmation build is 2019-05-06 (a listing date, not a session change)."),
    ),
    SessionSpec(
        valid_from=date(2020, 10, 26),
        valid_to=date(2021, 6, 27),
        segments=_SEGMENTS_WITH_HALT,
        day_session_ct=DAY_SESSION_CT,
        source="cme_hours_with_halt",
        note=(
            "Same Globex hours as before (15:15-15:30 CT halt). From trade date 2020-10-26 CME's "
            "daily settlement period for all eight products is 14:59:30-15:00:00 CT (SER-8591, "
            "'cme_settlement_moved_to_1500'): D6's C 15:00 CT is confirmed; O 08:30 CT as in "
            "the previous spec. The last trade date of this regime is Friday 2021-06-25."),
    ),
    SessionSpec(
        valid_from=date(2021, 6, 28),
        valid_to=date(2026, 6, 19),
        segments=_SEGMENTS_NO_HALT,
        day_session_ct=DAY_SESSION_CT,
        source="cme_halt_removal_notice",
        note=(
            "CME eliminated the 15:15-15:30 CT halt from trade date 2021-06-28: 'the affected "
            "equity futures and options products will trade from Sunday-Friday, 5pm-4pm CT, "
            "daily, with a 4pm-5pm CT maintenance period' (all eight listed). No later CME change "
            "to these hours was found; CME's trading-hours service shows the regular 16:00 CT "
            "close and 17:00 CT open around every holiday of 2023-2026. D6 confirmation: C 15:00 "
            "CT matches the settlement period 14:59:30-15:00:00 CT ('cme_settlement_1500'); O "
            "08:30 CT is not a CME settlement boundary ('cme_price_limit_day_regime'). Outside "
            "this window: CME captures of 2026-06-19 show Saturday '05:00 open' / '17:00 closed' "
            "events on 2026-06-20 and 2026-07-04 for ES; unexplained, not encoded."),
    ),
)

SESSION_SOURCES: dict[str, Citation] = {
    "cme_hours_with_halt": Citation(
        f"{_WB}20190607125912/{_CME}trading/equity-index/us-index/"
        "e-mini-sandp500_contract_specifications.html",
        "Trading Hours CME Globex: Sunday - Friday 6:00 p.m. - 5:00 p.m. Eastern Time (ET) with "
        "trading halt 4:15 p.m. - 4:30 p.m.",
        note="E-mini S&P 500 contract specifications, capture 2019-06-07 (the 2021-06-10 "
             "capture reads the same): 17:00-16:00 CT with a 15:15-15:30 CT halt. The same text "
             "is on the 2019 specification pages of NQ, RTY, YM, MES, MNQ, M2K and MYM "
             "(PRODUCT_SOURCES). CME's Christmas 2019 and 2020 Globex schedules show the regular "
             "equity day after the holiday as '15:15|15:30|16:00' (halt, reopen, close)."),
    "cme_halt_removal_notice": Citation(
        f"{_WB}20260208051545/{_CME}notices/electronic-trading/2021/06/20210621.html",
        "Elimination of CME Equity Futures and Options Market Pause - This Week Effective this "
        "Sunday, June 27 (trade date Monday, June 28), CME Group will eliminate the 15 minute "
        "market pause from 3:15-3:30 ... With this change, the affected equity futures and "
        "options products will trade from Sunday-Friday, 5pm-4pm CT, daily, with a 4pm-5pm CT "
        "maintenance period.",
        f"{_WB}20220118235156/https://www.cftc.gov/sites/default/files/filings/orgrules/21/06/"
        "rule061421cmedcm001.pdf",
        "the elimination of: (1) the CME Globex trading halt for certain CME and CBOT equity "
        "futures and options contracts as provided in Exhibit A attached ... effective on "
        "Sunday, June 27, 2021 for trade date Monday, June 28, 2021. ... CME and CBOT will "
        "eliminate the 3:15 p.m. – 3:30 p.m. Central Time (CT) trading halt on CME Globex which "
        "currently exists for certain Equity futures and options contracts.",
        note="CME Globex notice of 2021-06-21 (capture of the notice page) and the CME/CBOT "
             "submission to the CFTC of 2021-06-11 (CME's own letter, hosted by the CFTC). "
             "Exhibit A of the submission and the notice's product list name ES, MES, NQ, MNQ, "
             "RTY, M2K (CME) and YM, MYM (CBOT): PRODUCT_SOURCES."),
    "cme_settlement_1515": Citation(
        f"{_WB}20190824091841/{_CME}confluence/display/EPICSANDBOX/Dow+Jones+Futures",
        "Daily settlements of the CME Equity Index futures are determined by CME Group staff "
        "based on trading and market activity on CME Globex. These include: RTY, NQ, YM, NIY, "
        "NK and ENY . Daily settlement of the Micro E-Mini Dow (MYM) is equal to the daily "
        "settlement price of the E-Mini Dow (YM) futures. ... Tier 1: If the lead month "
        "contract trades on Globex between 15:14:30 and 15:15:00 Central Time (CT), the "
        "settlement period",
        f"{_WB}20191120084353/{_CME}confluence/display/EPICSANDBOX/Nasdaq-100",
        "CME Group staff determines the daily settlements in the E-Mini Nasdaq-100 (NQ) futures "
        "based on trading activity on CME Globex between 15:14:30 – 15:15:00 Central Time (CT), "
        "the settlement period. Daily settlement of the Micro E-Mini NASDAQ (MNQ) is equal to "
        "the daily settlement price of the E-Mini NASDAQ-100 (NQ) futures.",
        note="CME client-wiki settlement pages as captured in 2019 (Dow Jones Futures page, "
             "2019-08-24; Nasdaq-100 page, 2019-11-20). ES and MES: SER-8591's blackline "
             "('cme_settlement_moved_to_1500') strikes their 15:14:30 - 15:15:00 period."),
    "cme_settlement_moved_to_1500": Citation(
        f"{_WB}20241220125115/{_CME}notices/ser/2020/09/SER-8591.pdf",
        "Effective Sunday, October 25, 2020 for trade date Monday, October 26, 2020 ... "
        "E-mini S&P 500, S&P 500 and Micro E-mini S&P 500 index futures and options on futures "
        "... E-mini Nasdaq 100 and Micro E-mini Nasdaq 100 index futures and options on futures "
        "... E-mini Dow Jones Industrial Average and Micro E-mini Dow Jones Industrial Average "
        "futures and ... E-mini Russell 2000 and Micro E-mini Russell 2000 index futures and "
        "options on futures ... Specifically, the Exchanges are implementing amendments to "
        "change the daily settlement price determination period of the Contracts from 3:15 p.m. "
        "Central Time (CT) to 3:00 p.m. CT.",
        f"{_WB}20241220125115/{_CME}notices/ser/2020/09/SER-8591.pdf",
        "the designated lead month contract from 15:14:30 – 15:15:00 14:59:30 to 15:00:00 "
        "Central Time",
        note="CME Special Executive Report SER-8591 (2020-09-22). The time quote is Exhibit B's "
             "blackline of the ES/MES settlement procedure (deleted period, then the added one)."),
    "cme_settlement_1500": Citation(
        _WIKI + "457418067?expand=body.storage,version,history",
        "Daily settlement of the E-Mini S&P 500 (ES) ,Micro E-mini S&P 500 (MES), and E-Nano S&P "
        "500 (NES) futures are derived according to the procedure below. ... The "
        "volume-weighted average price (“VWAP”) of all trades executed on CME Globex between "
        "14:59:30 and 15:00:00 CT, the settlement period",
        _WIKI + "457222172?expand=body.storage,version,history",
        "Daily settlements of the CME Equity Index futures E-mini Nasdaq 100 (NQ), Micro E-mini "
        "Nasdaq (MNQ), E-Nano NASDAQ-100 (NNQ),E-mini Dow (YM), Micro E-mini Dow (MYM), E-Nano "
        "Dow (NDOW), E-mini Russell 2000 (RTY), Micro E-mini Russell 2000 (M2K) ... Tier 1: If "
        "the lead month contract trades on Globex between 14:59:30 and 15:00:00 Central Time "
        "(CT), the settlement period",
        note="CME client-wiki settlement procedures read live through the REST API on "
             "2026-09-25 (E-Mini S&P 500 page version 4 of 2026-08-20; Nasdaq-100 page version 5 "
             "of 2026-08-20; the E-mini Russell 2000 and Dow Jones pages, read the same way, "
             "carry the same period). The cmegroup.com wiki captures of 2021-09-23 (Nasdaq-100) "
             "and 2021-12-02 (Dow Jones Futures) already read 14:59:30 and 15:00:00 CT."),
    "cme_price_limit_day_regime": Citation(
        f"{_WB}20190823172618/{_CME}trading/price-limits.html",
        "7%, 13%, and 20% price limits are applied to the futures fixing price and are "
        "effective from 8:30 a.m. CT – 3:00 p.m. CT. Mondays through Fridays.",
        f"{_WB}20230604080601/{_CME}trading/price-limits.html",
        "7%, 13%, and 20% price limits are applied to the futures fixing price and are "
        "effective from 8:30 a.m. CT – 2:25 p.m. CT. Mondays through Fridays. From 2:25 p.m. "
        "to 3:00 p.m. CT, only the 20% price limit will be applied to the futures price fixing.",
        note="CME's price-limits page (captures 2019-08-23 and 2023-06-04): the equity-index "
             "day regime of price limits runs from 8:30 a.m. CT to 3:00 p.m. CT. Support for "
             "D6's O 08:30 CT; not a settlement procedure."),
}

PRODUCT_SOURCES: dict[str, Citation] = {
    "halt_removal_product_list": Citation(
        f"{_WB}20260310213155/{_CME}content/dam/cmegroup/notices/electronic-trading/2021/06/"
        "cme-equity-index-futures-options.pdf",
        "Elimination of CME Equity Futures and Options Market Pause ... E-MINI NASDAQ 100 "
        "FUTURES NQ NQ ... EMINI RUSSELL 2000 INDEX FUTURES RTY RY ... E-MINI S&P 500 FUTURES "
        "ES ES ... MICRO E-MINI NASDAQ 100 FUTURE MNQ NQ ... MICRO E-MINI RUSSELL 2000 INDEX FUT "
        "M2K RY ... MICRO E-MINI S&P 500 FUTURES MES MS ... E-MINI DOW ($5) FUTURES YM YM ... "
        "MICRO E-MINI DOW JONES AVE FUTURE MYM YM",
        note="The product list linked from CME's Globex notice of 2021-06-21: all eight share "
             "the Globex schedule change of trade date 2021-06-28."),
    "cftc_exhibit_a": Citation(
        f"{_WB}20220118235156/https://www.cftc.gov/sites/default/files/filings/orgrules/21/06/"
        "rule061421cmedcm001.pdf",
        "Exhibit A: CME and CBOT Equity Futures and Options Contracts ... E-mini Standard and "
        "Poor's 500 Stock Price Index Futures 358 ES ... Micro E-mini Russell 2000 Index Futures "
        "363 M2K ... Micro E-mini Standard and Poor’s 500 Stock Price Index Futures 353 MES ... "
        "Micro E-mini Nasdaq 100 Index Futures 361 MNQ ... E-mini NASDAQ 100 Index Futures 359 "
        "NQ ... E-mini® Russell 2000® Index Futures 393 RTY ... Micro E-mini Dow Jones "
        "Industrial Average Index Futures 28 MYM ... CBOT E-mini Dow Jones Industrial Average "
        "Index Futures ($5 Multiplier) 27 YM",
        note="CME/CBOT submission 2021-06-11, Exhibit A (CME rows then CBOT rows)."),
    "ym_mlk_2026": Citation(
        f"{_WB}20260714154118/{_CME}services/trading-hours-by-product?id=318&pageNumber=1"
        "&pageSize=999&sortAsc=true&fromEventDate=2026-01-18&toEventDate=2026-01-20",
        '"globex":"YM","prodGroup":"YM","name":"E-mini Dow Jones Industrial Average Index '
        'Futures","id":318 ... {"groupCode":"YM","eventDate":"2026-01-19","events":[{'
        '"tradingDate":"2026-01-20","eventTime":"12:00","marketEventType":"preopen"},{'
        '"tradingDate":"2026-01-20","eventTime":"17:00","marketEventType":"open"}]}',
        note="CME's trading-hours service for the E-mini Dow (YM, CBOT) on MLK Day 2026: the "
             "same 12:00 CT halt and 17:00 CT reopen as ES (SOURCES_2025_2026)."),
    "specs_2019": Citation(
        f"{_WB}20191019063718/{_CME}trading/equity-index/us-index/"
        "e-mini-nasdaq-100_contract_specifications.html",
        "Trading Hours CME Globex: Sunday - Friday 6:00 p.m. - 5:00 p.m. Eastern Time (ET) with "
        "trading halt 4:15 p.m. - 4:30 p.m.",
        note="The same sentence is on the 2019 contract-specification pages of RTY (capture "
             "20190720175051), YM (20190922074805), MES (20190923064822), MNQ (20190923080501), "
             "M2K (20190720032725) and MYM (20190923064639), all under www.cmegroup.com/trading/"
             "equity-index/us-index/, and on ES's (SESSION_SOURCES 'cme_hours_with_halt')."),
    "holiday_schedule_row": Citation(
        f"{_WB}20220704065438/{_HC}2022-memorial-day-holiday-schedule.xls",
        "Equity Products|16:00|||||16:00|17:00|||||||12:00||||12:00|17:00 ... Exceptions ... "
        "US Equity BTIC's & FTSE Emerging BTIC ... TACO:E-mini S&P, E-mini Nasdaq 100, E-mini "
        "Russell 2000",
        note="CME's Globex holiday schedules give one 'Equity Products' row; the listed "
             "exceptions are BTIC, TACO, FTSE and Nikkei/TOPIX instruments (2019: also 'Big "
             "Equities', by its name the full-size contracts), none of the eight products here."),
}
