"""Stage E.2a Task 6, equity group: data/calendars/equity.py and the carried fixes to
data/cme_calendar.py (design D10, D11.3, D14). Known answers only: no network, no market data, no
scratch files. The verbatim check of every quote against the fetched CME documents is done by the
worker's one-off script (reports/stage_e2a_calendar_sources_equity.json), not here.
"""

from __future__ import annotations

import hashlib
from datetime import date, timedelta
from datetime import time as T

import pytest

import data.calendars.equity as E
import data.cme_calendar as cme
from data.calendars import GROUP_OF_PRODUCT, SessionSpec
from data.cme_calendar import CalendarCoverageError, HolidayKind
from data.config import REPO_ROOT
from data.group_session import load_group_calendar, session_intervals
from data.session import ct_ns

FULL, HALT = HolidayKind.FULL_CLOSURE, HolidayKind.EARLY_HALT
LO, HI = date(2019, 5, 1), date(2026, 6, 19)
STATUS_GRADES = {"cme", "secondary", "unverified"}
TIME_GRADES = {"cme", "secondary", "inferred", "unverified", "n/a"}
ES_2024_07 = ("https://web.archive.org/web/20240708161439/https://www.cmegroup.com/services/"
              "trading-hours-by-product?id=316,133,425,300,58,437,22,8478,5201,10191&pageNumber=1"
              "&pageSize=999&sortAsc=true&fromEventDate=2024-07-03&toEventDate=2024-07-05"
              "&isProtected&_t=1720455278680")

# Every entry of the equity calendar inside the stage window, each checked against a CME document
# (reports/stage_e2a_calendar_sources_equity.md).
EXPECTED: list[tuple[date, str, HolidayKind, T | None]] = [
    (date(2019, 5, 27), 'Memorial Day', HALT, T(12, 0)),
    (date(2019, 7, 3), 'Day before Independence Day', HALT, T(12, 15)),
    (date(2019, 7, 4), 'Independence Day', HALT, T(12, 0)),
    (date(2019, 9, 2), 'Labor Day', HALT, T(12, 0)),
    (date(2019, 11, 28), 'Thanksgiving Day', HALT, T(12, 0)),
    (date(2019, 11, 29), 'Day after Thanksgiving', HALT, T(12, 15)),
    (date(2019, 12, 24), 'Christmas Eve', HALT, T(12, 15)),
    (date(2019, 12, 25), 'Christmas Day', FULL, None),
    (date(2020, 1, 1), "New Year's Day", FULL, None),
    (date(2020, 1, 20), 'Martin Luther King Jr. Day', HALT, T(12, 0)),
    (date(2020, 2, 17), 'Presidents Day', HALT, T(12, 0)),
    (date(2020, 4, 10), 'Good Friday', FULL, None),
    (date(2020, 5, 25), 'Memorial Day', HALT, T(12, 0)),
    (date(2020, 7, 3), 'Independence Day (observed)', HALT, T(12, 0)),
    (date(2020, 9, 7), 'Labor Day', HALT, T(12, 0)),
    (date(2020, 11, 26), 'Thanksgiving Day', HALT, T(12, 0)),
    (date(2020, 11, 27), 'Day after Thanksgiving', HALT, T(12, 15)),
    (date(2020, 12, 24), 'Christmas Eve', HALT, T(12, 15)),
    (date(2020, 12, 25), 'Christmas Day', FULL, None),
    (date(2021, 1, 1), "New Year's Day", FULL, None),
    (date(2021, 1, 18), 'Martin Luther King Jr. Day', HALT, T(12, 0)),
    (date(2021, 2, 15), 'Presidents Day', HALT, T(12, 0)),
    (date(2021, 4, 2), 'Good Friday (abbreviated, jobs report)', HALT, T(8, 15)),
    (date(2021, 5, 31), 'Memorial Day', HALT, T(12, 0)),
    (date(2021, 7, 5), 'Independence Day (observed)', HALT, T(12, 0)),
    (date(2021, 9, 6), 'Labor Day', HALT, T(12, 0)),
    (date(2021, 11, 25), 'Thanksgiving Day', HALT, T(12, 0)),
    (date(2021, 11, 26), 'Day after Thanksgiving', HALT, T(12, 15)),
    (date(2021, 12, 24), 'Christmas Day (observed)', FULL, None),
    (date(2022, 1, 17), 'Martin Luther King Jr. Day', HALT, T(12, 0)),
    (date(2022, 2, 21), 'Presidents Day', HALT, T(12, 0)),
    (date(2022, 4, 15), 'Good Friday', FULL, None),
    (date(2022, 5, 30), 'Memorial Day', HALT, T(12, 0)),
    (date(2022, 6, 20), 'Juneteenth (observed)', HALT, T(12, 0)),
    (date(2022, 7, 4), 'Independence Day', HALT, T(12, 0)),
    (date(2022, 9, 5), 'Labor Day', HALT, T(12, 0)),
    (date(2022, 11, 24), 'Thanksgiving Day', HALT, T(12, 0)),
    (date(2022, 11, 25), 'Day after Thanksgiving', HALT, T(12, 15)),
    (date(2022, 12, 26), 'Christmas Day (observed)', FULL, None),
    (date(2023, 1, 2), "New Year's Day (observed)", FULL, None),
    (date(2023, 1, 16), 'Martin Luther King Jr. Day', HALT, T(12, 0)),
    (date(2023, 2, 20), 'Presidents Day', HALT, T(12, 0)),
    (date(2023, 4, 7), 'Good Friday (abbreviated, jobs report)', HALT, T(8, 15)),
    (date(2023, 5, 29), 'Memorial Day', HALT, T(12, 0)),
    (date(2023, 6, 19), 'Juneteenth', HALT, T(12, 0)),
    (date(2023, 7, 3), 'Day before Independence Day', HALT, T(12, 15)),
    (date(2023, 7, 4), 'Independence Day', HALT, T(12, 0)),
    (date(2023, 9, 4), 'Labor Day', HALT, T(12, 0)),
    (date(2023, 11, 23), 'Thanksgiving Day', HALT, T(12, 0)),
    (date(2023, 11, 24), 'Day after Thanksgiving', HALT, T(12, 15)),
    (date(2023, 12, 25), 'Christmas Day', FULL, None),
    (date(2024, 1, 1), "New Year's Day (observed)", FULL, None),
    (date(2024, 1, 15), 'Martin Luther King Jr. Day', HALT, T(12, 0)),
    (date(2024, 2, 19), 'Presidents Day', HALT, T(12, 0)),
    (date(2024, 3, 29), 'Good Friday', FULL, None),
    (date(2024, 5, 27), 'Memorial Day', HALT, T(12, 0)),
    (date(2024, 6, 19), 'Juneteenth', HALT, T(12, 0)),
    (date(2024, 7, 3), 'Day before Independence Day', HALT, T(12, 15)),
    (date(2024, 7, 4), 'Independence Day', HALT, T(12, 0)),
    (date(2024, 9, 2), 'Labor Day', HALT, T(12, 0)),
    (date(2024, 11, 28), 'Thanksgiving Day', HALT, T(12, 0)),
    (date(2024, 11, 29), 'Day after Thanksgiving', HALT, T(12, 15)),
    (date(2024, 12, 24), 'Christmas Eve', HALT, T(12, 15)),
    (date(2024, 12, 25), 'Christmas Day', FULL, None),
    (date(2025, 1, 1), "New Year's Day", FULL, None),
    (date(2025, 1, 9), 'National Day of Mourning (Carter)', HALT, T(8, 30)),
    (date(2025, 1, 20), 'Martin Luther King Jr. Day', HALT, T(12, 0)),
    (date(2025, 2, 17), 'Presidents Day', HALT, T(12, 0)),
    (date(2025, 4, 18), 'Good Friday', FULL, None),
    (date(2025, 5, 26), 'Memorial Day', HALT, T(12, 0)),
    (date(2025, 6, 19), 'Juneteenth', HALT, T(12, 0)),
    (date(2025, 7, 3), 'Day before Independence Day', HALT, T(12, 15)),
    (date(2025, 7, 4), 'Independence Day', HALT, T(12, 0)),
    (date(2025, 9, 1), 'Labor Day', HALT, T(12, 0)),
    (date(2025, 11, 27), 'Thanksgiving', HALT, T(12, 0)),
    (date(2025, 11, 28), 'Day after Thanksgiving', HALT, T(12, 15)),
    (date(2025, 12, 24), 'Christmas Eve', HALT, T(12, 15)),
    (date(2025, 12, 25), 'Christmas Day', FULL, None),
    (date(2026, 1, 1), "New Year's Day", FULL, None),
    (date(2026, 1, 19), 'Martin Luther King Jr. Day', HALT, T(12, 0)),
    (date(2026, 2, 16), 'Presidents Day', HALT, T(12, 0)),
    (date(2026, 4, 3), 'Good Friday (abbreviated, jobs report)', HALT, T(8, 15)),
    (date(2026, 5, 25), 'Memorial Day', HALT, T(12, 0)),
    (date(2026, 6, 19), 'Juneteenth', HALT, T(12, 0)),
]


def _in_window() -> dict[date, cme.Holiday]:
    return {d: h for d, h in E.HOLIDAYS.items() if LO <= d <= HI}


# ------------------------------------------------------------------ interface ----
def test_equity_module_reexports_data_cme_calendar_without_copies() -> None:
    assert E.HOLIDAYS is cme.HOLIDAYS
    assert E.CALENDAR_COVERAGE == cme.CALENDAR_COVERAGE == (date(2019, 1, 1), date(2026, 12, 31))
    assert E.assert_calendar_coverage is cme.assert_calendar_coverage
    assert E.CalendarCoverageError is cme.CalendarCoverageError
    assert E.Citation is cme.Citation and E.Holiday is cme.Holiday
    assert E.SOURCES_2019_2024 is cme.SOURCES_2019_2024
    assert E.NO_ENTRY_FINDINGS_2019_2024 is cme.NO_ENTRY_FINDINGS_2019_2024
    assert set(E.EQUITY_PRODUCTS) == {p for p, g in GROUP_OF_PRODUCT.items() if g == "equity"}
    assert E.STAGE_WINDOW == (LO, HI)


def test_coverage_refuses_dates_outside_the_calendar() -> None:
    E.assert_calendar_coverage([LO, HI, date(2019, 1, 1), date(2026, 12, 31)])
    with pytest.raises(CalendarCoverageError, match="2018-12-31"):
        E.assert_calendar_coverage([date(2020, 3, 2), date(2018, 12, 31)])
    with pytest.raises(CalendarCoverageError, match="2027-01-04"):
        E.assert_calendar_coverage([date(2027, 1, 4)])


# ------------------------------------------------------------------ the carried fixes ----
def test_2024_07_04_is_a_12_00_ct_halt_with_a_cme_citation() -> None:
    hol = E.HOLIDAYS[date(2024, 7, 4)]
    assert (hol.kind, hol.halt_ct, hol.evidence, hol.time_evidence) == (HALT, T(12, 0), "cme",
                                                                        "cme")
    cite = E.SOURCES[date(2024, 7, 4)]
    assert cite.status_url == cite.time_url == ES_2024_07
    assert '"eventDate":"2024-07-04"' in cite.status_quote
    assert '"id":133' in cite.status_quote  # the ES record
    assert '"eventTime":"12:00","marketEventType":"preopen"' in cite.time_quote
    assert '"eventTime":"17:00","marketEventType":"open"' in cite.time_quote


def test_the_eves_of_2019_and_2023_are_cme_graded_12_15_closes() -> None:
    for day, doc in ((date(2019, 7, 3), "2019-4th-of-july-holiday-schedule-compact.xls"),
                     (date(2023, 7, 3), "trading-hours/files/4th-of-july-2023.pdf")):
        hol = E.HOLIDAYS[day]
        assert (hol.kind, hol.halt_ct, hol.evidence, hol.time_evidence) == (HALT, T(12, 15),
                                                                            "cme", "cme"), day
        cite = E.SOURCES[day]
        assert cite.time_url.startswith("https://web.archive.org/web/") and doc in cite.time_url
        assert "1215" in cite.time_quote or "12:15 (CLOSED)" in cite.time_quote


def test_the_2025_2026_block_keeps_its_pinned_hash() -> None:
    source = (REPO_ROOT / "data" / "cme_calendar.py").read_text()
    block = cme.entries_2025_2026_block(source)
    assert hashlib.sha256(block.encode()).hexdigest() == cme.ENTRIES_2025_2026_SHA256


def test_mes_holdout_2_has_259_calendar_trade_dates() -> None:
    days = [date(2024, 4, 1) + timedelta(days=n) for n in range(365)]
    assert days[-1] == date(2025, 3, 31)
    weekdays = [d for d in days if d.weekday() < 5]
    trade = [d for d in weekdays if not (d in E.HOLIDAYS and E.HOLIDAYS[d].kind is FULL)]
    assert (len(weekdays), len(trade)) == (261, 259)
    assert [d for d in weekdays if d not in trade] == [date(2024, 12, 25), date(2025, 1, 1)]


# ------------------------------------------------------------------ entries ----
def test_every_entry_in_the_window_is_the_expected_one() -> None:
    got = [(d, h.name, h.kind, h.halt_ct) for d, h in sorted(_in_window().items())]
    assert got == EXPECTED
    assert len(EXPECTED) == 84


def test_every_holiday_name_and_every_non_standard_entry() -> None:
    names = {name for _, name, _, _ in EXPECTED}
    for needed in ("New Year's Day", "Martin Luther King Jr. Day", "Presidents Day", "Good Friday",
                   "Memorial Day", "Juneteenth", "Independence Day", "Labor Day",
                   "Thanksgiving Day", "Thanksgiving", "Day after Thanksgiving", "Christmas Eve",
                   "Christmas Day", "Day before Independence Day"):
        assert needed in names, needed
    special = {
        date(2021, 4, 2): (HALT, T(8, 15)), date(2023, 4, 7): (HALT, T(8, 15)),
        date(2026, 4, 3): (HALT, T(8, 15)), date(2025, 1, 9): (HALT, T(8, 30)),
        date(2020, 7, 3): (HALT, T(12, 0)), date(2021, 7, 5): (HALT, T(12, 0)),
        date(2022, 6, 20): (HALT, T(12, 0)), date(2021, 12, 24): (FULL, None),
        date(2022, 12, 26): (FULL, None), date(2023, 1, 2): (FULL, None),
        date(2024, 1, 1): (FULL, None), date(2025, 7, 4): (HALT, T(12, 0)),
        date(2026, 6, 19): (HALT, T(12, 0)),
    }
    for day, (kind, halt) in special.items():
        assert (E.HOLIDAYS[day].kind, E.HOLIDAYS[day].halt_ct) == (kind, halt), day
    # Good Friday is a full closure unless it is a jobs-report Friday.
    for day in (date(2020, 4, 10), date(2022, 4, 15), date(2024, 3, 29), date(2025, 4, 18)):
        assert E.HOLIDAYS[day].kind is FULL, day


def test_no_duplicate_dates_and_kinds_are_consistent() -> None:
    assert len(cme._ENTRIES) == len({h.day for h in cme._ENTRIES}) == len(E.HOLIDAYS)
    for day, hol in E.HOLIDAYS.items():
        assert hol.day == day and day.weekday() < 5, day
        assert (hol.halt_ct is None) == (hol.kind is FULL), day


def test_grades_are_in_the_allowed_sets() -> None:
    empirical = set()
    for day, hol in _in_window().items():
        assert hol.evidence in STATUS_GRADES, day
        if hol.time_evidence == "empirical":  # only in the pinned 2025-2026 block
            empirical.add(day)
            continue
        assert hol.time_evidence in TIME_GRADES, day
        if hol.kind is FULL:
            assert hol.time_evidence == "n/a", day
    assert empirical == {date(2025, 7, 4), date(2026, 4, 3)}


def test_every_entry_in_the_window_has_a_citation_with_quotes() -> None:
    for day, hol in _in_window().items():
        cite = E.SOURCES[day]
        assert cite.status_quote.strip(), day
        if hol.evidence == "unverified":
            assert "[unverified]" in cite.status_quote + cite.note, day
            continue
        assert cite.status_url and cite.status_url.startswith("https://"), day
        if hol.kind is HALT:
            assert cite.time_url and cite.time_quote and cite.time_quote.strip(), day
    assert set(E.SOURCES) == set(cme.SOURCES_2019_2024) | set(E.SOURCES_2025_2026)
    assert {d for d in E.SOURCES_2025_2026} == {d for d in _in_window() if d.year >= 2025}


def test_2025_2026_citations_quote_the_es_record_of_their_date() -> None:
    for day, cite in E.SOURCES_2025_2026.items():
        if day == date(2025, 1, 9):
            assert "EQUITIES CLOSE at 8:30 AM CT" in cite.time_quote
            continue
        assert cite.status_url == cite.time_url, day
        assert "trading-hours-by-product" in cite.status_url and "id=316,133" in cite.status_url
        assert '"id":133' in cite.status_quote, day
        assert f'"eventDate":"{day.isoformat()}"' in cite.time_quote, day
        assert cite.note, day


def test_no_entry_findings_are_regular_weekdays_without_entries() -> None:
    assert set(E.NO_ENTRY_FINDINGS) == (set(E.NO_ENTRY_FINDINGS_2019_2024)
                                        | set(E.NO_ENTRY_FINDINGS_E2A))
    for day, cite in E.NO_ENTRY_FINDINGS.items():
        assert day not in E.HOLIDAYS and day.weekday() < 5, day
        assert cite.status_url and cite.status_quote.strip(), day


def test_the_2025_11_28_outage_is_recorded_as_a_late_open_only() -> None:
    late = E.LATE_OPENS[date(2025, 11, 28)]
    assert (late.open_ct, late.halt_from_ct, late.evidence, late.time_evidence) == (
        T(7, 30), None, "cme", "cme")
    assert '"eventTime":"07:30","marketEventType":"open"' in E.LATE_OPEN_SOURCES[
        date(2025, 11, 28)].time_quote
    # The calendar entry itself is the scheduled 12:15 CT close, unchanged.
    assert E.HOLIDAYS[date(2025, 11, 28)].halt_ct == T(12, 15)


# ------------------------------------------------------------------ sessions ----
def test_sessions_cover_the_window_without_gap_or_overlap() -> None:
    specs = E.SESSIONS
    assert all(isinstance(s, SessionSpec) for s in specs)
    assert specs[0].valid_from == LO and specs[-1].valid_to == HI
    for a, b in zip(specs, specs[1:], strict=False):
        assert a.valid_to is not None and a.valid_to + timedelta(days=1) == b.valid_from
    assert [s.valid_from for s in specs] == [LO, date(2020, 10, 26), date(2021, 6, 28)]
    day = LO
    while day <= HI:  # exactly one spec per date
        assert sum(s.valid_from <= day <= s.valid_to for s in specs) == 1, day
        day += timedelta(days=1)


def _minutes(offset: int, at: T) -> int:
    return offset * 1440 + at.hour * 60 + at.minute


def test_segments_are_ordered_and_the_halt_ends_on_2021_06_25() -> None:
    for spec in E.SESSIONS:
        spans = [(_minutes(s.start_offset_days, s.start_ct), _minutes(s.end_offset_days, s.end_ct))
                 for s in spec.segments]
        assert all(lo < hi for lo, hi in spans)
        assert all(a[1] <= b[0] for a, b in zip(spans, spans[1:], strict=False))
        assert spans[0][0] == _minutes(-1, T(17, 0)) and spans[-1][1] == _minutes(0, T(16, 0))
    with_halt = [s for s in E.SESSIONS if len(s.segments) == 2]
    assert [s.valid_to for s in with_halt] == [date(2020, 10, 25), date(2021, 6, 27)]
    for spec in with_halt:
        assert (spec.segments[0].end_ct, spec.segments[1].start_ct) == (T(15, 15), T(15, 30))
    assert len(E.SESSIONS[-1].segments) == 1


def test_each_day_session_lies_inside_one_trading_segment() -> None:
    for spec in E.SESSIONS:
        assert spec.day_session_ct == {"equity": (T(8, 30), T(15, 0))}  # D6, unchanged
        for opening, closing in spec.day_session_ct.values():
            inside = [s for s in spec.segments
                      if _minutes(s.start_offset_days, s.start_ct) <= _minutes(0, opening)
                      and _minutes(0, closing) <= _minutes(s.end_offset_days, s.end_ct)]
            assert len(inside) == 1, spec.valid_from
    # The D6 discrepancy (CME settled at 15:15 CT before 2020-10-26) is recorded, not encoded.
    assert "15:15" in E.SESSIONS[0].note and "DISCREPANCY" in E.SESSIONS[0].note
    for spec in E.SESSIONS:
        assert spec.source in E.SESSION_SOURCES


def test_group_session_uses_the_equity_sessions() -> None:
    cal = load_group_calendar("equity")
    assert cal.sessions == E.SESSIONS
    assert "data/calendars/equity.py" in {str(p.relative_to(REPO_ROOT)) for p in cal.module_paths}
    before, after = date(2021, 6, 25), date(2021, 6, 28)
    assert session_intervals(cal, before) == [
        (ct_ns(date(2021, 6, 24), T(17, 0)), ct_ns(before, T(15, 15))),
        (ct_ns(before, T(15, 30)), ct_ns(before, T(16, 0)))]
    assert session_intervals(cal, after) == [(ct_ns(date(2021, 6, 27), T(17, 0)),
                                              ct_ns(after, T(16, 0)))]
    # A listed early halt cuts the session; the 15:30 segment disappears before 2021-06-28.
    assert session_intervals(cal, date(2019, 11, 29)) == [
        (ct_ns(date(2019, 11, 28), T(17, 0)), ct_ns(date(2019, 11, 29), T(12, 15)))]
    assert session_intervals(cal, date(2024, 7, 4)) == [
        (ct_ns(date(2024, 7, 3), T(17, 0)), ct_ns(date(2024, 7, 4), T(12, 0)))]
    assert session_intervals(cal, date(2024, 12, 25)) == []


def test_every_source_table_entry_carries_quotes() -> None:
    for table in (E.SESSION_SOURCES, E.PRODUCT_SOURCES, E.LATE_OPEN_SOURCES):
        for key, cite in table.items():
            assert cite.status_url and cite.status_url.startswith("https://"), key
            assert cite.status_quote.strip(), key
            assert (cite.time_url is None) == (cite.time_quote is None), key
