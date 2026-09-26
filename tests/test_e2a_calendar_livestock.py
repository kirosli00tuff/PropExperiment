"""Known-answer tests for the livestock-group CME calendar (data/calendars/livestock.py,
Stage E.2a).

Synthetic inputs only: no network, no scratch files, no market data. The verbatim check of each
quote against the fetched CME documents was run once by the build script and is recorded in
reports/stage_e2a_calendar_sources_livestock.json (the fetched files live outside the repo).
"""

from __future__ import annotations

from datetime import date, time, timedelta

import pytest

import data.calendars.livestock as livestock
import data.cme_calendar as cme
from data.calendars import GROUP_OF_PRODUCT, SessionSpec
from data.cme_calendar import CalendarCoverageError, Citation, Holiday, HolidayKind

FULL = HolidayKind.FULL_CLOSURE
HALT = HolidayKind.EARLY_HALT
STATUS_GRADES = {"cme", "secondary", "unverified"}
TIME_GRADES = {"cme", "secondary", "inferred", "unverified", "n/a"}
FIRST, LAST = date(2019, 5, 1), date(2026, 6, 19)
T1215, T1205 = time(12, 15), time(12, 5)

# (date, name, kind, halt_ct, evidence, time_evidence): at least one entry per holiday name and
# every non-standard entry (every early close, the secondary entry, observed days, jobs-report
# Good Fridays, the Day of Mourning, the coverage boundary).
KNOWN = [
    (date(2019, 5, 27), "Memorial Day", FULL, None, "cme", "n/a"),
    (date(2019, 7, 3), "Day before Independence Day", HALT, T1215, "cme", "cme"),
    (date(2019, 7, 4), "Independence Day", FULL, None, "cme", "n/a"),
    (date(2019, 9, 2), "Labor Day", FULL, None, "cme", "n/a"),
    (date(2019, 11, 28), "Thanksgiving Day", FULL, None, "cme", "n/a"),
    (date(2019, 11, 29), "Day after Thanksgiving", HALT, T1215, "cme", "cme"),
    (date(2019, 12, 24), "Christmas Eve", HALT, T1215, "cme", "cme"),
    (date(2019, 12, 25), "Christmas Day", FULL, None, "cme", "n/a"),
    (date(2020, 1, 1), "New Year's Day", FULL, None, "cme", "n/a"),
    (date(2020, 1, 20), "Martin Luther King Jr. Day", FULL, None, "cme", "n/a"),
    (date(2020, 2, 17), "Presidents Day", FULL, None, "cme", "n/a"),
    (date(2020, 4, 10), "Good Friday", FULL, None, "cme", "n/a"),
    (date(2020, 7, 2), "Day before Independence Day (observed)", HALT, T1215, "cme", "cme"),
    (date(2020, 7, 3), "Independence Day (observed)", FULL, None, "cme", "n/a"),
    (date(2020, 11, 27), "Day after Thanksgiving", HALT, T1205, "cme", "cme"),
    (date(2020, 12, 24), "Christmas Eve", HALT, T1205, "cme", "cme"),
    (date(2021, 4, 2), "Good Friday", FULL, None, "cme", "n/a"),
    (date(2021, 7, 5), "Independence Day (observed)", FULL, None, "cme", "n/a"),
    (date(2021, 11, 26), "Day after Thanksgiving", HALT, T1205, "cme", "cme"),
    (date(2021, 12, 24), "Christmas Day (observed)", FULL, None, "cme", "n/a"),
    (date(2022, 6, 20), "Juneteenth (observed)", FULL, None, "cme", "n/a"),
    (date(2022, 11, 25), "Day after Thanksgiving", HALT, T1205, "cme", "cme"),
    (date(2022, 12, 26), "Christmas Day (observed)", FULL, None, "cme", "n/a"),
    (date(2023, 1, 2), "New Year's Day (observed)", FULL, None, "cme", "n/a"),
    (date(2023, 1, 16), "Martin Luther King Jr. Day", FULL, None, "secondary", "n/a"),
    (date(2023, 4, 7), "Good Friday", FULL, None, "cme", "n/a"),
    (date(2023, 6, 19), "Juneteenth", FULL, None, "cme", "n/a"),
    (date(2023, 11, 24), "Day after Thanksgiving", HALT, T1205, "cme", "cme"),
    (date(2024, 1, 1), "New Year's Day", FULL, None, "cme", "n/a"),
    (date(2024, 7, 4), "Independence Day", FULL, None, "cme", "n/a"),
    (date(2024, 11, 29), "Day after Thanksgiving", HALT, T1205, "cme", "cme"),
    (date(2024, 12, 24), "Christmas Eve", HALT, T1215, "cme", "cme"),
    (date(2025, 1, 9), "National Day of Mourning (Carter)", HALT, T1215, "cme", "cme"),
    (date(2025, 4, 18), "Good Friday", FULL, None, "cme", "n/a"),
    (date(2025, 11, 27), "Thanksgiving Day", FULL, None, "cme", "n/a"),
    (date(2025, 11, 28), "Day after Thanksgiving", HALT, T1205, "cme", "cme"),
    (date(2025, 12, 24), "Christmas Eve", HALT, T1215, "cme", "cme"),
    (date(2025, 12, 25), "Christmas Day", FULL, None, "cme", "n/a"),
    (date(2026, 4, 3), "Good Friday", FULL, None, "cme", "n/a"),
    (date(2026, 6, 19), "Juneteenth", FULL, None, "cme", "n/a"),
]

EARLY_CLOSES = {
    date(2019, 7, 3): T1215, date(2019, 11, 29): T1215, date(2019, 12, 24): T1215,
    date(2020, 7, 2): T1215, date(2020, 11, 27): T1205, date(2020, 12, 24): T1205,
    date(2021, 11, 26): T1205, date(2022, 11, 25): T1205, date(2023, 11, 24): T1205,
    date(2024, 11, 29): T1205, date(2024, 12, 24): T1215, date(2025, 1, 9): T1215,
    date(2025, 11, 28): T1205, date(2025, 12, 24): T1215,
}

# Days CME stated as regular for livestock: no entry (equities or rates deviated on several).
NORMAL_DAYS = [date(2019, 12, 31), date(2020, 12, 31), date(2021, 4, 1), date(2021, 7, 2),
               date(2021, 12, 23), date(2021, 12, 31), date(2022, 1, 3), date(2022, 7, 1),
               date(2022, 12, 23), date(2022, 12, 30), date(2023, 4, 6), date(2023, 7, 3),
               date(2023, 12, 22), date(2023, 12, 29), date(2024, 7, 3), date(2024, 12, 31),
               date(2025, 7, 3), date(2025, 12, 31), date(2026, 4, 2)]

EXCHANGE_HOLIDAY_NAMES = {
    "New Year's Day", "New Year's Day (observed)", "Martin Luther King Jr. Day", "Presidents Day",
    "Good Friday", "Memorial Day", "Juneteenth", "Juneteenth (observed)", "Independence Day",
    "Independence Day (observed)", "Labor Day", "Thanksgiving Day", "Christmas Day",
    "Christmas Day (observed)",
}


def _minutes(offset_days: int, at: time) -> int:
    return offset_days * 1440 + at.hour * 60 + at.minute


# ---- interface ----

def test_types_are_imported_from_the_equity_module_not_redefined():
    assert livestock.Holiday is Holiday
    assert livestock.HolidayKind is HolidayKind
    assert livestock.Citation is Citation
    assert livestock.CalendarCoverageError is cme.CalendarCoverageError


def test_products_are_the_livestock_group():
    group = {p for p, g in GROUP_OF_PRODUCT.items() if g == "livestock"}
    assert set(livestock.LIVESTOCK_PRODUCTS) == group == {"HE", "LE"}


def test_module_adds_no_late_open_extension():
    """No late open or abbreviated livestock session exists in the window: interface unchanged."""
    assert not hasattr(livestock, "LATE_OPENS")


# ---- coverage ----

def test_coverage_is_the_design_window():
    assert livestock.CALENDAR_COVERAGE == (FIRST, LAST)


@pytest.mark.parametrize("outside", [date(2019, 4, 30), date(2026, 6, 20), date(2018, 1, 2)])
def test_coverage_refuses_a_date_outside_the_range(outside):
    with pytest.raises(CalendarCoverageError, match="outside the livestock calendar's coverage"):
        livestock.assert_calendar_coverage([FIRST, outside])


def test_coverage_accepts_the_boundaries_and_empty_input():
    livestock.assert_calendar_coverage([FIRST, LAST, date(2022, 3, 15)])
    livestock.assert_calendar_coverage([])


def test_coverage_error_reports_the_count_and_the_extremes():
    with pytest.raises(CalendarCoverageError, match=r"2 trade date\(s\).*2019-04-29 .. 2026-06-22"):
        livestock.assert_calendar_coverage(
            [date(2026, 6, 22), date(2019, 4, 29), date(2020, 1, 2)])


# ---- entries ----

@pytest.mark.parametrize(("day", "name", "kind", "halt", "evidence", "time_evidence"), KNOWN)
def test_known_entry(day, name, kind, halt, evidence, time_evidence):
    h = livestock.HOLIDAYS[day]
    assert (h.day, h.name, h.kind, h.halt_ct, h.evidence, h.time_evidence) == (
        day, name, kind, halt, evidence, time_evidence)


def test_known_answers_cover_every_holiday_name():
    names = {h.name for h in livestock.HOLIDAYS.values()}
    assert names == {k[1] for k in KNOWN}


@pytest.mark.parametrize("day", NORMAL_DAYS)
def test_cme_stated_normal_days_carry_no_entry(day):
    assert day not in livestock.HOLIDAYS
    assert day in livestock.NO_ENTRY_FINDINGS


def test_every_exchange_holiday_is_a_full_closure():
    """Livestock has no holiday halt session: each named exchange holiday closes the day."""
    for h in livestock.HOLIDAYS.values():
        if h.name in EXCHANGE_HOLIDAY_NAMES:
            assert h.kind is FULL, h
    for day in (date(2021, 4, 2), date(2023, 4, 7), date(2026, 4, 3)):  # jobs-report Good Fridays
        assert livestock.HOLIDAYS[day].kind is FULL


def test_early_closes_are_exactly_the_known_days_and_times():
    early = {h.day: h.halt_ct for h in livestock.HOLIDAYS.values() if h.kind is HALT}
    assert early == EARLY_CLOSES


def test_early_close_time_regime():
    """12:15 CT through 2020-07-02; 12:05 CT after, except Christmas Eve 2024-25 and 2025-01-09."""
    late_1215 = (date(2024, 12, 24), date(2025, 12, 24), date(2025, 1, 9))
    for day, at in EARLY_CLOSES.items():
        expected = T1215 if day <= date(2020, 7, 2) or day in late_1215 else T1205
        assert at == expected, day
        assert livestock.SESSION_OPEN < at < livestock.SESSION_CLOSE


def test_last_bar_of_an_early_close_starts_one_minute_before_the_halt():
    """Synthetic: the last one-minute bar of 2025-11-28 starts at 12:04 CT."""
    h = livestock.HOLIDAYS[date(2025, 11, 28)]
    last_bar = _minutes(0, h.halt_ct) - 1
    assert last_bar == 12 * 60 + 4


def test_entry_counts_by_year_and_kind():
    by_year: dict[int, int] = {}
    for d in livestock.HOLIDAYS:
        by_year[d.year] = by_year.get(d.year, 0) + 1
    assert by_year == {2019: 8, 2020: 12, 2021: 10, 2022: 10, 2023: 11, 2024: 12, 2025: 13,
                       2026: 6}
    kinds = [h.kind for h in livestock.HOLIDAYS.values()]
    assert (kinds.count(FULL), kinds.count(HALT)) == (68, 14)


def test_no_duplicate_dates_and_keys_match_days():
    days = [h.day for h in livestock._ENTRIES]
    assert len(days) == len(set(days)) == len(livestock.HOLIDAYS)
    assert all(k == h.day for k, h in livestock.HOLIDAYS.items())
    assert days == sorted(days)


def test_every_entry_is_a_weekday_inside_the_coverage():
    for d in livestock.HOLIDAYS:
        assert FIRST <= d <= LAST
        assert d.weekday() < 5


def test_kind_and_time_fields_agree():
    for h in livestock.HOLIDAYS.values():
        if h.kind is FULL:
            assert h.halt_ct is None and h.time_evidence == "n/a"
        else:
            assert h.halt_ct is not None and h.time_evidence != "n/a"


def test_grades_are_in_the_allowed_sets():
    for h in livestock.HOLIDAYS.values():
        assert h.evidence in STATUS_GRADES
        assert h.time_evidence in TIME_GRADES  # never "empirical": reserved for the bar check
    graded = {d: h.evidence for d, h in livestock.HOLIDAYS.items() if h.evidence != "cme"}
    assert graded == {date(2023, 1, 16): "secondary"}


# ---- citations ----

def test_every_entry_has_a_citation_with_non_empty_quotes():
    assert set(livestock.SOURCES) == set(livestock.HOLIDAYS)
    for d, h in livestock.HOLIDAYS.items():
        c = livestock.SOURCES[d]
        assert isinstance(c, Citation)
        assert c.status_url and c.status_url.startswith("https://")
        assert c.status_quote.strip()
        assert c.note.strip()
        if h.kind is HALT:
            assert c.time_url and c.time_url.startswith("https://")
            assert c.time_quote and c.time_quote.strip()


def test_citations_are_cme_documents_except_the_secondary_entry():
    for d, c in livestock.SOURCES.items():
        if livestock.HOLIDAYS[d].evidence == "secondary":
            assert not c.status_url.startswith("https://www.cmegroup.com/")
            assert "SECONDARY" in c.note
            continue
        assert c.status_url.startswith("https://www.cmegroup.com/")
        assert c.time_url is None or c.time_url.startswith("https://www.cmegroup.com/")
    for c in livestock.NO_ENTRY_FINDINGS.values():
        assert c.status_url.startswith("https://www.cmegroup.com/")


def test_quoted_halt_time_appears_in_the_time_quote():
    """Each early close's clock time is written in its time quote, in that source's notation."""
    for d, h in livestock.HOLIDAYS.items():
        if h.kind is not HALT:
            continue
        q = livestock.SOURCES[d].time_quote
        assert any(s in q for s in (h.halt_ct.strftime("%H%M"), h.halt_ct.strftime("%H:%M"))), d


def test_quoted_status_names_livestock():
    """Every status quote names the livestock row, LE, or CME's ag group for the one-off day."""
    for d, c in livestock.SOURCES.items():
        q = c.status_quote
        assert any(s in q for s in ("Livestock", "LIVESTOCK", '"globex":"LE"', "AGS")), d


def test_no_entry_findings_are_cited_and_disjoint():
    assert not set(livestock.NO_ENTRY_FINDINGS) & set(livestock.HOLIDAYS)
    for d, c in livestock.NO_ENTRY_FINDINGS.items():
        assert c.status_quote.strip() and c.note.startswith("NORMAL")
        assert FIRST <= d <= LAST and d.weekday() < 5


# ---- sessions ----

def test_sessions_cover_the_range_without_gap_or_overlap():
    specs = livestock.SESSIONS
    assert specs and all(isinstance(s, SessionSpec) for s in specs)
    assert specs[0].valid_from == FIRST
    assert specs[-1].valid_to == LAST
    for prev, nxt in zip(specs, specs[1:], strict=False):
        assert prev.valid_to is not None
        assert nxt.valid_from == prev.valid_to + timedelta(days=1)
    for s in specs:
        assert s.valid_to is None or s.valid_from <= s.valid_to


def test_session_is_the_day_session_only():
    for s in livestock.SESSIONS:
        assert len(s.segments) == 1
        seg = s.segments[0]
        assert (seg.start_offset_days, seg.start_ct, seg.end_offset_days, seg.end_ct) == (
            0, time(8, 30), 0, time(13, 5))


def test_day_session_is_design_d6_and_inside_a_trading_segment():
    for s in livestock.SESSIONS:
        assert set(s.day_session_ct) == set(livestock.LIVESTOCK_PRODUCTS)
        for o, c in s.day_session_ct.values():
            assert (o, c) == (time(8, 30), time(13, 0))
            assert (o, c) == (livestock.SESSION_OPEN, livestock.SETTLEMENT_CT)
            assert any(
                _minutes(seg.start_offset_days, seg.start_ct) <= _minutes(0, o)
                < _minutes(0, c) <= _minutes(seg.end_offset_days, seg.end_ct)
                for seg in s.segments
            )


def test_every_early_close_lies_inside_the_day_session():
    seg = livestock.SESSIONS[0].segments[0]
    for at in EARLY_CLOSES.values():
        assert _minutes(0, seg.start_ct) < _minutes(0, at) < _minutes(0, seg.end_ct)


def test_session_sources_are_cited():
    for s in livestock.SESSIONS:
        assert s.source in livestock.SESSION_SOURCES
        assert "D6 confirmation" in s.note
    for c in livestock.SESSION_SOURCES.values():
        assert c.status_quote.strip() and c.note.strip()
        assert c.status_url.startswith(
            ("https://www.cmegroup.com/", "https://cmegroupclientsite.atlassian.net/"))
    settle = livestock.SESSION_SOURCES["cme_livestock_settlement"]
    assert "12:59:30 and 13:00:00" in settle.status_quote
    hours = livestock.SESSION_SOURCES["cme_livestock_hours"]
    assert "8:30 a.m. - 1:05 p.m. CT" in hours.status_quote
