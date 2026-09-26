"""Known-answer tests for the energy-group CME calendar (data/calendars/energy.py, Stage E.2a).

Synthetic inputs only: no network, no scratch files, no market data. The verbatim check of each
quote against the fetched CME documents was run once by the build script and is recorded in
reports/stage_e2a_calendar_sources_energy.json (the fetched files live outside the repo).
"""

from __future__ import annotations

from datetime import date, time, timedelta

import pytest

import data.calendars.energy as energy
import data.cme_calendar as cme
from data.calendars import GROUP_OF_PRODUCT, SessionSpec
from data.cme_calendar import CalendarCoverageError, Citation, Holiday, HolidayKind

FULL = HolidayKind.FULL_CLOSURE
HALT = HolidayKind.EARLY_HALT
STATUS_GRADES = {"cme", "secondary", "unverified"}
TIME_GRADES = {"cme", "secondary", "inferred", "unverified", "n/a"}
FIRST, LAST = date(2019, 5, 1), date(2026, 6, 19)

# (date, name, kind, halt_ct, time_evidence): at least one entry per holiday name and every
# non-standard entry (regime boundaries, Friday closes, 13:45 closes, jobs-report Good Fridays,
# observed days, the inferred time).
KNOWN = [
    (date(2019, 5, 27), "Memorial Day", HALT, time(12, 0), "cme"),
    (date(2019, 7, 4), "Independence Day", HALT, time(12, 0), "cme"),
    (date(2019, 11, 29), "Day after Thanksgiving", HALT, time(12, 45), "cme"),
    (date(2019, 12, 24), "Christmas Eve", HALT, time(12, 45), "cme"),
    (date(2019, 12, 25), "Christmas Day", FULL, None, "n/a"),
    (date(2020, 1, 1), "New Year's Day", FULL, None, "n/a"),
    (date(2020, 1, 20), "Martin Luther King Jr. Day", HALT, time(12, 0), "cme"),
    (date(2020, 2, 17), "Presidents Day", HALT, time(12, 0), "cme"),
    (date(2020, 4, 10), "Good Friday", FULL, None, "n/a"),
    (date(2020, 7, 3), "Independence Day (observed)", HALT, time(12, 0), "cme"),
    (date(2020, 9, 7), "Labor Day", HALT, time(12, 0), "cme"),
    (date(2021, 4, 2), "Good Friday", FULL, None, "n/a"),
    (date(2021, 7, 5), "Independence Day (observed)", HALT, time(12, 0), "cme"),
    (date(2021, 11, 25), "Thanksgiving Day", HALT, time(12, 0), "cme"),
    (date(2021, 12, 24), "Christmas Day (observed)", FULL, None, "n/a"),
    (date(2022, 1, 17), "Martin Luther King Jr. Day", HALT, time(13, 30), "cme"),
    (date(2022, 6, 20), "Juneteenth (observed)", HALT, time(13, 30), "cme"),
    (date(2022, 11, 25), "Day after Thanksgiving", HALT, time(12, 45), "cme"),
    (date(2022, 12, 26), "Christmas Day (observed)", FULL, None, "n/a"),
    (date(2023, 1, 2), "New Year's Day (observed)", FULL, None, "n/a"),
    (date(2023, 1, 16), "Martin Luther King Jr. Day", HALT, time(13, 30), "inferred"),
    (date(2023, 4, 7), "Good Friday", FULL, None, "n/a"),
    (date(2023, 6, 19), "Juneteenth", HALT, time(13, 30), "cme"),
    (date(2023, 11, 24), "Day after Thanksgiving", HALT, time(12, 45), "cme"),
    (date(2024, 1, 1), "New Year's Day (observed)", FULL, None, "n/a"),
    (date(2024, 7, 4), "Independence Day", HALT, time(13, 30), "cme"),
    (date(2024, 11, 28), "Thanksgiving Day", HALT, time(13, 30), "cme"),
    (date(2024, 11, 29), "Day after Thanksgiving", HALT, time(13, 45), "cme"),
    (date(2024, 12, 24), "Christmas Eve", HALT, time(12, 45), "cme"),
    (date(2025, 7, 4), "Independence Day", HALT, time(12, 0), "cme"),
    (date(2025, 11, 28), "Day after Thanksgiving", HALT, time(13, 45), "cme"),
    (date(2025, 12, 25), "Christmas Day", FULL, None, "n/a"),
    (date(2026, 4, 3), "Good Friday", FULL, None, "n/a"),
    (date(2026, 5, 25), "Memorial Day", HALT, time(13, 30), "cme"),
    (date(2026, 6, 19), "Juneteenth", HALT, time(12, 0), "cme"),
]

# Days CME stated as regular for energy: no entry (equities or rates deviated on some of them).
NORMAL_DAYS = [date(2019, 7, 3), date(2019, 12, 31), date(2020, 7, 2), date(2021, 12, 23),
               date(2021, 12, 31), date(2022, 12, 23), date(2023, 7, 3), date(2023, 12, 22),
               date(2024, 7, 3), date(2025, 1, 9), date(2025, 7, 3), date(2026, 4, 2)]

HOLIDAY_HALT_NAMES = {
    "Martin Luther King Jr. Day", "Presidents Day", "Memorial Day", "Juneteenth",
    "Juneteenth (observed)", "Independence Day", "Independence Day (observed)", "Labor Day",
    "Thanksgiving Day",
}


def _minutes(offset_days: int, at: time) -> int:
    return offset_days * 1440 + at.hour * 60 + at.minute


# ---- interface ----

def test_types_are_imported_from_the_equity_module_not_redefined():
    assert energy.Holiday is Holiday
    assert energy.HolidayKind is HolidayKind
    assert energy.Citation is Citation
    assert energy.CalendarCoverageError is cme.CalendarCoverageError


def test_products_are_the_energy_group():
    assert set(energy.ENERGY_PRODUCTS) == {p for p, g in GROUP_OF_PRODUCT.items() if g == "energy"}


# ---- coverage ----

def test_coverage_is_the_design_window():
    assert energy.CALENDAR_COVERAGE == (FIRST, LAST)


@pytest.mark.parametrize("outside", [date(2019, 4, 30), date(2026, 6, 20), date(2018, 1, 2)])
def test_coverage_refuses_a_date_outside_the_range(outside):
    with pytest.raises(CalendarCoverageError, match="outside the energy calendar's coverage"):
        energy.assert_calendar_coverage([FIRST, outside])


def test_coverage_accepts_the_boundaries_and_empty_input():
    energy.assert_calendar_coverage([FIRST, LAST, date(2022, 3, 15)])
    energy.assert_calendar_coverage([])


def test_coverage_error_reports_the_count_and_the_extremes():
    with pytest.raises(CalendarCoverageError, match=r"2 trade date\(s\).*2019-04-29 .. 2026-06-22"):
        energy.assert_calendar_coverage([date(2026, 6, 22), date(2019, 4, 29), date(2020, 1, 2)])


# ---- entries ----

@pytest.mark.parametrize(("day", "name", "kind", "halt", "time_evidence"), KNOWN)
def test_known_entry(day, name, kind, halt, time_evidence):
    h = energy.HOLIDAYS[day]
    assert (h.day, h.name, h.kind, h.halt_ct, h.time_evidence) == (
        day, name, kind, halt, time_evidence)
    assert h.evidence == "cme"


def test_known_answers_cover_every_holiday_name():
    names = {h.name for h in energy.HOLIDAYS.values()}
    assert names == {k[1] for k in KNOWN}


@pytest.mark.parametrize("day", NORMAL_DAYS)
def test_cme_stated_normal_days_carry_no_entry(day):
    assert day not in energy.HOLIDAYS
    assert day in energy.NO_ENTRY_FINDINGS


def test_holiday_halt_time_regime():
    """12:00 CT in 2019-2021, 13:30 CT from 2022; a Friday holiday closes at 12:00 CT."""
    for h in energy.HOLIDAYS.values():
        if h.kind is not HALT or h.name not in HOLIDAY_HALT_NAMES:
            continue
        expected = time(12, 0) if h.day.year <= 2021 or h.day.weekday() == 4 else time(13, 30)
        assert h.halt_ct == expected, h


def test_early_closes_are_christmas_eve_and_the_day_after_thanksgiving():
    early = {h.day: h.halt_ct for h in energy.HOLIDAYS.values()
             if h.kind is HALT and h.name not in HOLIDAY_HALT_NAMES}
    for day, at in early.items():
        name = energy.HOLIDAYS[day].name
        assert name in {"Christmas Eve", "Day after Thanksgiving"}, day
        if name == "Day after Thanksgiving" and day.year >= 2024:
            assert at == time(13, 45)
        else:
            assert at == time(12, 45)


def test_entry_counts_by_year_and_kind():
    by_year: dict[int, int] = {}
    for d in energy.HOLIDAYS:
        by_year[d.year] = by_year.get(d.year, 0) + 1
    assert by_year == {2019: 7, 2020: 11, 2021: 10, 2022: 10, 2023: 11, 2024: 12, 2025: 12,
                       2026: 6}
    kinds = [h.kind for h in energy.HOLIDAYS.values()]
    assert (kinds.count(FULL), kinds.count(HALT)) == (20, 59)


def test_no_duplicate_dates_and_keys_match_days():
    days = [h.day for h in energy._ENTRIES]
    assert len(days) == len(set(days)) == len(energy.HOLIDAYS)
    assert all(k == h.day for k, h in energy.HOLIDAYS.items())
    assert days == sorted(days)


def test_every_entry_is_a_weekday_inside_the_coverage():
    for d in energy.HOLIDAYS:
        assert FIRST <= d <= LAST
        assert d.weekday() < 5


def test_kind_and_time_fields_agree():
    for h in energy.HOLIDAYS.values():
        if h.kind is FULL:
            assert h.halt_ct is None and h.time_evidence == "n/a"
        else:
            assert h.halt_ct is not None and h.time_evidence != "n/a"


def test_grades_are_in_the_allowed_sets():
    for h in energy.HOLIDAYS.values():
        assert h.evidence in STATUS_GRADES
        assert h.time_evidence in TIME_GRADES  # never "empirical": reserved for the bar check
    for lo in energy.LATE_OPENS.values():
        assert lo.evidence in STATUS_GRADES and lo.time_evidence in TIME_GRADES


# ---- citations ----

def test_every_entry_has_a_citation_with_non_empty_quotes():
    assert set(energy.SOURCES) == set(energy.HOLIDAYS)
    for d, h in energy.HOLIDAYS.items():
        c = energy.SOURCES[d]
        assert isinstance(c, Citation)
        assert c.status_url and c.status_url.startswith("https://")
        assert c.status_quote.strip()
        if h.kind is HALT:
            assert c.time_url and c.time_url.startswith("https://")
            assert c.time_quote and c.time_quote.strip()


def test_citations_are_cme_documents():
    for c in list(energy.SOURCES.values()) + list(energy.NO_ENTRY_FINDINGS.values()):
        assert c.status_url.startswith("https://www.cmegroup.com/")
        assert c.time_url is None or c.time_url.startswith("https://www.cmegroup.com/")


def test_quoted_halt_time_appears_in_the_time_quote():
    """Each halt's clock time is written in its time quote, in the notation of that source."""
    for d, h in energy.HOLIDAYS.items():
        if h.kind is not HALT:
            continue
        q = energy.SOURCES[d].time_quote
        hhmm = h.halt_ct.strftime("%H%M")
        pm = h.halt_ct.strftime("%I:%M:00 %p")
        assert any(s in q for s in (hhmm, h.halt_ct.strftime("%H:%M"), pm)), d


def test_no_entry_findings_and_late_opens_are_cited_and_disjoint():
    assert not set(energy.NO_ENTRY_FINDINGS) & set(energy.HOLIDAYS)
    for c in energy.NO_ENTRY_FINDINGS.values():
        assert c.status_quote.strip()
    assert set(energy.LATE_OPEN_SOURCES) == set(energy.LATE_OPENS)
    for d, c in energy.LATE_OPEN_SOURCES.items():
        assert c.status_quote.strip() and c.time_quote and c.time_quote.strip()
        assert FIRST <= d <= LAST


# ---- late open (additive extension) ----

def test_outage_late_open_on_the_day_after_thanksgiving_2025():
    lo = energy.LATE_OPENS[date(2025, 11, 28)]
    assert lo.open_ct == time(7, 30)
    assert lo.halt_from_ct is None and lo.halt_from_offset_days == -1
    assert (lo.evidence, lo.time_evidence) == ("cme", "cme")
    # the same day keeps its scheduled 13:45 CT close
    assert energy.HOLIDAYS[date(2025, 11, 28)].halt_ct == time(13, 45)
    assert lo.open_ct < energy.HOLIDAYS[date(2025, 11, 28)].halt_ct


# ---- sessions ----

def test_sessions_cover_the_range_without_gap_or_overlap():
    specs = energy.SESSIONS
    assert specs and all(isinstance(s, SessionSpec) for s in specs)
    assert specs[0].valid_from == FIRST
    assert specs[-1].valid_to == LAST
    for prev, nxt in zip(specs, specs[1:], strict=False):
        assert prev.valid_to is not None
        assert nxt.valid_from == prev.valid_to + timedelta(days=1)
    for s in specs:
        assert s.valid_to is None or s.valid_from <= s.valid_to


def test_regular_session_is_17_to_16_ct_with_the_daily_halt():
    for s in energy.SESSIONS:
        assert [(g.start_offset_days, g.start_ct, g.end_offset_days, g.end_ct)
                for g in s.segments] == [(-1, time(17, 0), 0, time(16, 0))]


def test_day_session_is_d6_value_for_every_product():
    for s in energy.SESSIONS:
        assert set(s.day_session_ct) == set(energy.ENERGY_PRODUCTS)
        assert all(v == (time(8, 0), time(13, 30)) for v in s.day_session_ct.values())
        assert s.source in energy.SESSION_SOURCES
        assert "D6 confirmation" in s.note


def test_each_day_session_lies_inside_a_trading_segment():
    for s in energy.SESSIONS:
        for o, c in s.day_session_ct.values():
            lo, hi = _minutes(0, o), _minutes(0, c)
            assert lo < hi
            assert any(_minutes(g.start_offset_days, g.start_ct) <= lo
                       and hi <= _minutes(g.end_offset_days, g.end_ct) for g in s.segments)


def test_d6_flatten_time_lies_inside_the_session():
    f = _minutes(0, time(15, 8))
    for s in energy.SESSIONS:
        assert any(_minutes(g.start_offset_days, g.start_ct) <= f
                   < _minutes(g.end_offset_days, g.end_ct) for g in s.segments)


def test_holiday_halts_fall_inside_the_regular_session():
    seg = energy.SESSIONS[0].segments[0]
    for h in energy.HOLIDAYS.values():
        if h.kind is HALT:
            assert _minutes(0, h.halt_ct) < _minutes(seg.end_offset_days, seg.end_ct)


def test_session_sources_have_quotes():
    for c in energy.SESSION_SOURCES.values():
        assert c.status_url and c.status_quote.strip()
