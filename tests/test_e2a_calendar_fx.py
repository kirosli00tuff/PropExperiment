"""Stage E.2a Task 6: the CME Globex calendar of the FX group (data/calendars/fx.py).

Known-answer tests on the module's own tables. No network, no scratch files, no market data; the
only file read is the repo's own source report (reports/stage_e2a_calendar_sources_fx.json),
which the module's citations must match. The verbatim check of each quote against the fetched
CME documents is done by the builder's one-off script, not here (the documents live outside the
repo); the report records its result per row.
"""

from __future__ import annotations

import json
from datetime import date, datetime, time, timedelta

import pytest

import data.cme_calendar as cme_calendar
from data.calendars import GROUP_OF_PRODUCT, SessionSpec
from data.calendars import fx as F
from data.cme_calendar import CalendarCoverageError, HolidayKind
from data.config import REPO_ROOT

REPORT = REPO_ROOT / "reports" / "stage_e2a_calendar_sources_fx.json"
STATUS_GRADES = {"cme", "secondary", "unverified"}
TIME_GRADES = {"cme", "secondary", "inferred", "unverified", "n/a"}
FIRST, LAST = date(2019, 5, 1), date(2026, 6, 19)
FULL, HALT = HolidayKind.FULL_CLOSURE, HolidayKind.EARLY_HALT

# Every entry, as CME's FX schedules state it: (day, kind, halt_ct).
KNOWN: list[tuple[date, HolidayKind, time | None]] = [
    (date(2019, 5, 27), HALT, time(12, 0)),
    (date(2019, 7, 4), HALT, time(12, 0)),
    (date(2019, 9, 2), HALT, time(12, 0)),
    (date(2019, 11, 28), HALT, time(12, 0)),
    (date(2019, 11, 29), HALT, time(12, 15)),
    (date(2019, 12, 24), HALT, time(12, 15)),
    (date(2019, 12, 25), FULL, None),
    (date(2020, 1, 1), FULL, None),
    (date(2020, 1, 20), HALT, time(12, 0)),
    (date(2020, 2, 17), HALT, time(12, 0)),
    (date(2020, 4, 10), FULL, None),
    (date(2020, 5, 25), HALT, time(12, 0)),
    (date(2020, 7, 3), HALT, time(12, 0)),
    (date(2020, 9, 7), HALT, time(12, 0)),
    (date(2020, 11, 26), HALT, time(12, 0)),
    (date(2020, 11, 27), HALT, time(12, 15)),
    (date(2020, 12, 24), HALT, time(12, 15)),
    (date(2020, 12, 25), FULL, None),
    (date(2021, 1, 1), FULL, None),
    (date(2021, 1, 18), HALT, time(12, 0)),
    (date(2021, 2, 15), HALT, time(12, 0)),
    (date(2021, 4, 2), HALT, time(10, 15)),
    (date(2021, 5, 31), HALT, time(12, 0)),
    (date(2021, 7, 5), HALT, time(12, 0)),
    (date(2021, 9, 6), HALT, time(12, 0)),
    (date(2021, 11, 25), HALT, time(12, 0)),
    (date(2021, 11, 26), HALT, time(12, 15)),
    (date(2021, 12, 24), FULL, None),
    (date(2022, 4, 15), FULL, None),
    (date(2022, 11, 25), HALT, time(12, 15)),
    (date(2022, 12, 26), FULL, None),
    (date(2023, 1, 2), FULL, None),
    (date(2023, 4, 7), HALT, time(10, 15)),
    (date(2023, 11, 24), HALT, time(12, 15)),
    (date(2023, 12, 25), FULL, None),
    (date(2024, 1, 1), FULL, None),
    (date(2024, 3, 29), FULL, None),
    (date(2024, 11, 29), HALT, time(13, 45)),
    (date(2024, 12, 24), HALT, time(12, 45)),
    (date(2024, 12, 25), FULL, None),
    (date(2025, 1, 1), FULL, None),
    (date(2025, 4, 18), FULL, None),
    (date(2025, 7, 4), HALT, time(12, 0)),
    (date(2025, 11, 28), HALT, time(13, 45)),
    (date(2025, 12, 24), HALT, time(12, 45)),
    (date(2025, 12, 25), FULL, None),
    (date(2026, 1, 1), FULL, None),
    (date(2026, 4, 3), HALT, time(10, 15)),
    (date(2026, 6, 19), HALT, time(12, 0)),
]


# ------------------------------------------------------------------ coverage ----
def test_coverage_is_the_design_window() -> None:
    assert F.CALENDAR_COVERAGE == (FIRST, LAST)


@pytest.mark.parametrize("day", [FIRST - timedelta(days=1), LAST + timedelta(days=1),
                                 date(2019, 1, 21), date(2026, 12, 24)])
def test_coverage_refuses_a_date_outside_the_range(day: date) -> None:
    with pytest.raises(CalendarCoverageError, match="FX calendar"):
        F.assert_calendar_coverage([FIRST, day])


def test_coverage_error_names_the_count_and_the_extremes() -> None:
    with pytest.raises(CalendarCoverageError, match=r"2 trade date\(s\).*2019-04-01 .. 2027-01-04"):
        F.assert_calendar_coverage([date(2027, 1, 4), date(2020, 3, 3), date(2019, 4, 1)])


def test_coverage_accepts_both_ends_and_an_empty_input() -> None:
    F.assert_calendar_coverage([FIRST, LAST, date(2022, 6, 15)])
    F.assert_calendar_coverage([])


def test_the_equity_interface_types_are_reused_not_redefined() -> None:
    assert F.Holiday is cme_calendar.Holiday
    assert F.HolidayKind is cme_calendar.HolidayKind
    assert F.Citation is cme_calendar.Citation
    assert F.CalendarCoverageError is cme_calendar.CalendarCoverageError
    assert issubclass(F.CalendarCoverageError, ValueError)


# ------------------------------------------------------------------ entries ----
def test_every_entry_matches_the_known_answer_table() -> None:
    got = [(h.day, h.kind, h.halt_ct) for h in F._ENTRIES]
    assert got == KNOWN


def test_entries_are_unique_weekday_dates_inside_coverage() -> None:
    days = [h.day for h in F._ENTRIES]
    assert len(days) == len(set(days)) == len(F.HOLIDAYS) == 49
    assert days == sorted(days)
    for day, holiday in F.HOLIDAYS.items():
        assert holiday.day == day
        assert FIRST <= day <= LAST
        assert day.weekday() < 5, day


def test_counts_by_kind() -> None:
    kinds = [h.kind for h in F.HOLIDAYS.values()]
    assert kinds.count(FULL) == 17
    assert kinds.count(HALT) == 32


def test_closures_have_no_time_and_halts_have_one() -> None:
    for h in F.HOLIDAYS.values():
        if h.kind is FULL:
            assert h.halt_ct is None and h.time_evidence == "n/a", h
        else:
            assert h.halt_ct is not None and h.time_evidence != "n/a", h


@pytest.mark.parametrize(("name", "day", "kind", "halt"), [
    ("Memorial Day", date(2019, 5, 27), HALT, time(12, 0)),
    ("Independence Day", date(2019, 7, 4), HALT, time(12, 0)),
    ("Independence Day (observed)", date(2020, 7, 3), HALT, time(12, 0)),
    ("Labor Day", date(2021, 9, 6), HALT, time(12, 0)),
    ("Thanksgiving Day", date(2021, 11, 25), HALT, time(12, 0)),
    ("Day after Thanksgiving", date(2022, 11, 25), HALT, time(12, 15)),
    ("Christmas Eve", date(2020, 12, 24), HALT, time(12, 15)),
    ("Christmas Day", date(2023, 12, 25), FULL, None),
    ("Christmas Day (observed)", date(2021, 12, 24), FULL, None),
    ("New Year's Day", date(2021, 1, 1), FULL, None),
    ("New Year's Day (observed)", date(2023, 1, 2), FULL, None),
    ("Martin Luther King Jr. Day", date(2020, 1, 20), HALT, time(12, 0)),
    ("Presidents Day", date(2021, 2, 15), HALT, time(12, 0)),
    ("Good Friday", date(2024, 3, 29), FULL, None),
    ("Good Friday (abbreviated, jobs report)", date(2023, 4, 7), HALT, time(10, 15)),
    ("Juneteenth", date(2026, 6, 19), HALT, time(12, 0)),
])
def test_one_entry_per_holiday_name(name: str, day: date, kind: HolidayKind,
                                    halt: time | None) -> None:
    h = F.HOLIDAYS[day]
    assert (h.name, h.kind, h.halt_ct) == (name, kind, halt)


def test_every_holiday_name_is_covered_by_the_named_test() -> None:
    names = {h.name for h in F.HOLIDAYS.values()}
    assert names == {
        "Memorial Day", "Independence Day", "Independence Day (observed)", "Labor Day",
        "Thanksgiving Day", "Day after Thanksgiving", "Christmas Eve", "Christmas Day",
        "Christmas Day (observed)", "New Year's Day", "New Year's Day (observed)",
        "Martin Luther King Jr. Day", "Presidents Day", "Good Friday",
        "Good Friday (abbreviated, jobs report)", "Juneteenth"}


def test_non_standard_times_are_exactly_the_documented_ones() -> None:
    """Every halt other than the 12:00 holiday halt and the 12:15 early close."""
    odd = {d: h.halt_ct for d, h in F.HOLIDAYS.items()
           if h.halt_ct not in (None, time(12, 0), time(12, 15))}
    assert odd == {
        date(2021, 4, 2): time(10, 15), date(2023, 4, 7): time(10, 15),
        date(2026, 4, 3): time(10, 15),
        date(2024, 11, 29): time(13, 45), date(2025, 11, 28): time(13, 45),
        date(2024, 12, 24): time(12, 45), date(2025, 12, 24): time(12, 45)}


def test_monday_holidays_from_2022_are_regular_fx_sessions() -> None:
    """From MLK Day 2022 CME halts FX at 16:00 CT on Monday holidays and Thanksgiving: no entry."""
    regular = [date(2022, 1, 17), date(2022, 2, 21), date(2022, 5, 30), date(2022, 6, 20),
               date(2022, 7, 4), date(2022, 9, 5), date(2022, 11, 24), date(2023, 2, 20),
               date(2023, 5, 29), date(2023, 6, 19), date(2023, 7, 4), date(2023, 9, 4),
               date(2023, 11, 23), date(2024, 1, 15), date(2024, 2, 19), date(2024, 5, 27),
               date(2024, 6, 19), date(2024, 7, 4), date(2024, 9, 2), date(2024, 11, 28),
               date(2025, 1, 20), date(2025, 2, 17), date(2025, 5, 26), date(2025, 6, 19),
               date(2025, 9, 1), date(2025, 11, 27), date(2026, 1, 19), date(2026, 2, 16),
               date(2026, 5, 25)]
    for day in regular:
        assert day not in F.HOLIDAYS, day
        assert day in F.NO_ENTRY_FINDINGS, day
    # the last 12:00 CT Monday/Thursday FX halt before the change
    assert F.HOLIDAYS[date(2021, 11, 25)].halt_ct == time(12, 0)


def test_fx_eves_keep_the_regular_close_unlike_equity() -> None:
    for day in (date(2019, 7, 3), date(2023, 7, 3), date(2024, 7, 3), date(2025, 7, 3),
                date(2019, 12, 31), date(2024, 12, 31), date(2025, 12, 31)):
        assert day not in F.HOLIDAYS, day
        assert day in F.NO_ENTRY_FINDINGS, day
    assert date(2025, 1, 9) in F.NO_ENTRY_FINDINGS  # Day of Mourning: FX normal hours
    assert date(2025, 1, 9) not in F.HOLIDAYS


# ------------------------------------------------------------------ grades and citations ----
def test_grades_are_in_the_allowed_sets() -> None:
    for h in F.HOLIDAYS.values():
        assert h.evidence in STATUS_GRADES, h
        assert h.time_evidence in TIME_GRADES, h
        assert h.time_evidence != "empirical"
    for lo in F.LATE_OPENS.values():
        assert lo.evidence in STATUS_GRADES and lo.time_evidence in TIME_GRADES


def test_every_entry_has_a_citation_with_non_empty_quotes() -> None:
    assert set(F.SOURCES) == set(F.HOLIDAYS)
    for day, h in F.HOLIDAYS.items():
        c = F.SOURCES[day]
        assert c.status_url and c.status_url.startswith("https://www.cmegroup.com/"), day
        assert c.status_quote.strip(), day
        if h.kind is HALT:
            assert c.time_url and c.time_url.startswith("https://www.cmegroup.com/"), day
            assert c.time_quote and c.time_quote.strip(), day
        else:
            assert c.time_url is None and c.time_quote is None, day


def test_findings_and_late_opens_are_cited_and_disjoint_from_entries() -> None:
    assert not set(F.NO_ENTRY_FINDINGS) & set(F.HOLIDAYS)
    for day, c in F.NO_ENTRY_FINDINGS.items():
        assert FIRST <= day <= LAST
        assert c.status_url and c.status_quote.strip() and c.note, day
    assert set(F.LATE_OPEN_SOURCES) == set(F.LATE_OPENS)
    for c in F.LATE_OPEN_SOURCES.values():
        assert c.status_quote.strip() and c.time_quote and c.time_quote.strip()


def test_the_one_secondary_finding_is_flagged() -> None:
    secondary = {d for d, c in F.NO_ENTRY_FINDINGS.items()
                 if not c.status_url.startswith(("https://www.cmegroup.com/",
                                                 "https://cmegroupclientsite"))}
    assert secondary == {date(2023, 1, 16)}
    assert "SECONDARY" in F.NO_ENTRY_FINDINGS[date(2023, 1, 16)].note


def test_conflicting_cme_captures_are_named_in_the_notes() -> None:
    for day in (date(2024, 11, 29), date(2024, 12, 24)):
        assert "CONFLICT" in F.SOURCES[day].note, day


def test_late_open_is_the_2025_outage_on_an_early_close_day() -> None:
    lo = F.LATE_OPENS[date(2025, 11, 28)]
    assert lo.open_ct == time(7, 30) and lo.halt_from_ct is None
    assert F.HOLIDAYS[date(2025, 11, 28)].halt_ct == time(13, 45)
    assert lo.open_ct < F.HOLIDAYS[date(2025, 11, 28)].halt_ct


# ------------------------------------------------------------------ sessions ----
def _ct_minutes(offset_days: int, at: time) -> int:
    return offset_days * 1440 + at.hour * 60 + at.minute


def test_sessions_cover_the_range_without_gap_or_overlap() -> None:
    specs = F.SESSIONS
    assert specs and all(isinstance(s, SessionSpec) for s in specs)
    assert specs[0].valid_from == FIRST
    assert specs[-1].valid_to == LAST
    for a, b in zip(specs, specs[1:], strict=False):
        assert a.valid_to is not None
        assert b.valid_from == a.valid_to + timedelta(days=1)
    for s in specs:
        assert s.valid_to is None or s.valid_from <= s.valid_to


def test_each_day_session_lies_inside_a_trading_segment() -> None:
    fx_products = {p for p, g in GROUP_OF_PRODUCT.items() if g == "fx"}
    for s in F.SESSIONS:
        assert set(s.day_session_ct) == fx_products == set(F.FX_PRODUCTS)
        spans = [(_ct_minutes(g.start_offset_days, g.start_ct),
                  _ct_minutes(g.end_offset_days, g.end_ct)) for g in s.segments]
        assert all(lo < hi for lo, hi in spans)
        for product, (o, c) in s.day_session_ct.items():
            o_m, c_m = _ct_minutes(0, o), _ct_minutes(0, c)
            assert o_m < c_m, product
            assert any(lo <= o_m and c_m <= hi for lo, hi in spans), product


def test_regular_segment_and_d6_values() -> None:
    (spec,) = F.SESSIONS
    (seg,) = spec.segments
    assert (seg.start_offset_days, seg.start_ct, seg.end_offset_days, seg.end_ct) == (
        -1, time(17, 0), 0, time(16, 0))
    assert all(v == (time(7, 20), time(14, 0)) for v in spec.day_session_ct.values())
    assert spec.source in F.SESSION_SOURCES
    for key in ("cme_fx_settlement", "cme_fx_rth_open", "cme_settle_6E", "cme_settle_6N"):
        assert F.SESSION_SOURCES[key].status_quote.strip(), key


def test_halts_fall_inside_the_regular_segment() -> None:
    (spec,) = F.SESSIONS
    end = spec.segments[0].end_ct
    for h in F.HOLIDAYS.values():
        if h.halt_ct is not None:
            assert datetime.combine(h.day, h.halt_ct) < datetime.combine(h.day, end), h


# ------------------------------------------------------------------ report ----
def test_report_rows_match_the_module() -> None:
    rows = json.loads(REPORT.read_text())["entries"]
    assert [r["date"] for r in rows] == [d.isoformat() for d in sorted(F.HOLIDAYS)]
    for r in rows:
        day = date.fromisoformat(r["date"])
        h, c = F.HOLIDAYS[day], F.SOURCES[day]
        assert r["kind"] == h.kind.value and r["name"] == h.name
        assert r["halt_ct"] == (h.halt_ct.strftime("%H:%M") if h.halt_ct else None)
        assert (r["evidence"], r["time_evidence"]) == (h.evidence, h.time_evidence)
        assert r["status_quote"] == c.status_quote and r["time_quote"] == c.time_quote
        assert r["verbatim_check"] is True, r["date"]
        assert r["bar_check_status"]
