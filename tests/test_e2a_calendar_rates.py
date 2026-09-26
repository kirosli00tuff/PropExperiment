"""Stage E.2a Task 6: the CME Globex calendar of the rates group (data/calendars/rates.py).

Known-answer tests on the module's own tables. No network, no scratch files, no market data; the
only file read is the repo's own source report (reports/stage_e2a_calendar_sources_rates.json),
which the module's citations must match. The verbatim check of each quote against the fetched
CME documents is done by the builder's one-off script, not here (the documents live outside the
repo).
"""

from __future__ import annotations

import json
from datetime import date, time, timedelta

import pytest

import data.cme_calendar as cme_calendar
from data.calendars import GROUP_OF_PRODUCT, SessionSpec
from data.calendars import rates as R
from data.cme_calendar import CalendarCoverageError, HolidayKind
from data.config import REPO_ROOT

REPORT = REPO_ROOT / "reports" / "stage_e2a_calendar_sources_rates.json"
STATUS_GRADES = {"cme", "secondary", "unverified"}
TIME_GRADES = {"cme", "secondary", "inferred", "unverified", "n/a"}
FIRST, LAST = date(2019, 5, 1), date(2026, 6, 19)
NOON, CLOSE_1215, JOBS_GF = time(12, 0), time(12, 15), time(10, 15)
FULL, HALT = HolidayKind.FULL_CLOSURE, HolidayKind.EARLY_HALT


# ------------------------------------------------------------------ coverage ----
def test_coverage_is_the_design_window() -> None:
    assert R.CALENDAR_COVERAGE == (FIRST, LAST)


@pytest.mark.parametrize("day", [FIRST - timedelta(days=1), LAST + timedelta(days=1),
                                 date(2018, 12, 31), date(2027, 1, 4)])
def test_coverage_refuses_a_date_outside_the_range(day: date) -> None:
    with pytest.raises(CalendarCoverageError, match="rates calendar"):
        R.assert_calendar_coverage([FIRST, day])


def test_coverage_accepts_both_ends_and_an_empty_input() -> None:
    R.assert_calendar_coverage([FIRST, LAST, date(2022, 6, 15)])
    R.assert_calendar_coverage([])


def test_the_equity_interface_types_are_reused_not_redefined() -> None:
    assert R.Holiday is cme_calendar.Holiday
    assert R.HolidayKind is cme_calendar.HolidayKind
    assert R.Citation is cme_calendar.Citation
    assert R.CalendarCoverageError is cme_calendar.CalendarCoverageError


# ------------------------------------------------------------------ entries ----
def test_entries_are_unique_weekday_dates_inside_coverage() -> None:
    days = [h.day for h in R._ENTRIES]
    assert len(days) == len(set(days)) == len(R.HOLIDAYS)
    assert days == sorted(days)
    for day, holiday in R.HOLIDAYS.items():
        assert holiday.day == day
        assert FIRST <= day <= LAST
        assert day.weekday() < 5, day


KNOWN = [
    # one per holiday name, plus every entry that differs from the plain 12:00 CT holiday halt
    (date(2019, 5, 27), "Memorial Day", HALT, NOON),
    (date(2019, 7, 4), "Independence Day", HALT, NOON),
    (date(2020, 7, 3), "Independence Day (observed)", HALT, NOON),
    (date(2021, 7, 5), "Independence Day (observed)", HALT, NOON),
    (date(2019, 9, 2), "Labor Day", HALT, NOON),
    (date(2019, 11, 28), "Thanksgiving Day", HALT, NOON),
    (date(2020, 1, 20), "Martin Luther King Jr. Day", HALT, NOON),
    (date(2020, 2, 17), "Presidents Day", HALT, NOON),
    (date(2022, 6, 20), "Juneteenth (observed)", HALT, NOON),
    (date(2023, 6, 19), "Juneteenth", HALT, NOON),
    (date(2026, 6, 19), "Juneteenth", HALT, NOON),
    (date(2019, 11, 29), "Day after Thanksgiving", HALT, CLOSE_1215),
    (date(2020, 11, 27), "Day after Thanksgiving", HALT, CLOSE_1215),
    (date(2021, 11, 26), "Day after Thanksgiving", HALT, CLOSE_1215),
    (date(2022, 11, 25), "Day after Thanksgiving", HALT, CLOSE_1215),
    (date(2023, 11, 24), "Day after Thanksgiving", HALT, CLOSE_1215),
    (date(2024, 11, 29), "Day after Thanksgiving", HALT, CLOSE_1215),
    (date(2025, 11, 28), "Day after Thanksgiving", HALT, CLOSE_1215),
    (date(2019, 12, 24), "Christmas Eve", HALT, CLOSE_1215),
    (date(2020, 12, 24), "Christmas Eve", HALT, CLOSE_1215),
    (date(2024, 12, 24), "Christmas Eve", HALT, CLOSE_1215),
    (date(2025, 12, 24), "Christmas Eve", HALT, CLOSE_1215),
    (date(2025, 1, 9), "National Day of Mourning (Carter)", HALT, CLOSE_1215),
    (date(2021, 4, 2), "Good Friday (abbreviated, jobs report)", HALT, JOBS_GF),
    (date(2023, 4, 7), "Good Friday (abbreviated, jobs report)", HALT, JOBS_GF),
    (date(2026, 4, 3), "Good Friday (abbreviated, jobs report)", HALT, JOBS_GF),
    (date(2020, 4, 10), "Good Friday", FULL, None),
    (date(2022, 4, 15), "Good Friday", FULL, None),
    (date(2024, 3, 29), "Good Friday", FULL, None),
    (date(2025, 4, 18), "Good Friday", FULL, None),
    (date(2019, 12, 25), "Christmas Day", FULL, None),
    (date(2021, 12, 24), "Christmas Day (observed)", FULL, None),
    (date(2022, 12, 26), "Christmas Day (observed)", FULL, None),
    (date(2020, 1, 1), "New Year's Day", FULL, None),
    (date(2023, 1, 2), "New Year's Day (observed)", FULL, None),
    (date(2026, 1, 1), "New Year's Day", FULL, None),
]


@pytest.mark.parametrize(("day", "name", "kind", "halt"), KNOWN)
def test_known_entry(day: date, name: str, kind: HolidayKind, halt: time | None) -> None:
    holiday = R.HOLIDAYS[day]
    assert (holiday.name, holiday.kind, holiday.halt_ct) == (name, kind, halt)


def test_every_holiday_name_has_a_known_answer_test() -> None:
    assert {h.name for h in R._ENTRIES} == {name for _, name, _, _ in KNOWN}


def test_every_entry_off_the_noon_halt_pattern_is_in_the_known_answers() -> None:
    odd = {h.day for h in R._ENTRIES if h.kind is HALT and h.halt_ct != NOON}
    assert odd <= {day for day, *_ in KNOWN}


@pytest.mark.parametrize("day", [
    date(2019, 5, 24), date(2019, 7, 3), date(2019, 12, 31), date(2021, 4, 1), date(2021, 7, 2),
    date(2021, 12, 23), date(2021, 12, 31), date(2022, 1, 3), date(2022, 7, 1), date(2022, 12, 23),
    date(2023, 7, 3), date(2024, 7, 3), date(2024, 12, 31), date(2025, 7, 3), date(2025, 12, 31),
    date(2019, 10, 14), date(2019, 11, 11),
])
def test_cme_stated_regular_days_carry_no_entry(day: date) -> None:
    assert day not in R.HOLIDAYS
    assert day in R.NO_ENTRY_FINDINGS


def test_no_entry_findings_never_collide_with_entries() -> None:
    assert not set(R.NO_ENTRY_FINDINGS) & set(R.HOLIDAYS)


def test_grades_are_in_the_allowed_sets() -> None:
    for h in R._ENTRIES:
        assert h.evidence in STATUS_GRADES, h
        assert h.time_evidence in TIME_GRADES, h
        assert h.time_evidence != "empirical"  # reserved for the later bar check
        if h.kind is FULL:
            assert h.halt_ct is None and h.time_evidence == "n/a", h
        else:
            assert h.halt_ct is not None and h.time_evidence != "n/a", h
            assert time(8, 0) <= h.halt_ct <= time(16, 0), h


def test_non_cme_time_grades_are_exactly_the_three_2023_days() -> None:
    graded = {h.day: h.time_evidence for h in R._ENTRIES if h.time_evidence not in ("cme", "n/a")}
    assert graded == {date(2023, 1, 16): "secondary", date(2023, 2, 20): "secondary",
                      date(2023, 4, 7): "inferred"}
    assert all(h.evidence == "cme" for h in R._ENTRIES)


# ------------------------------------------------------------------ citations ----
def _check_citation(c: R.Citation, needs_time: bool) -> None:
    assert c.status_url and c.status_url.startswith("https://")
    assert c.status_quote.strip()
    if needs_time:
        assert c.time_url and c.time_url.startswith("https://")
        assert c.time_quote and c.time_quote.strip()


def test_every_entry_has_a_citation_with_non_empty_quotes() -> None:
    assert set(R.SOURCES) == set(R.HOLIDAYS)
    for day, c in R.SOURCES.items():
        _check_citation(c, needs_time=R.HOLIDAYS[day].kind is HALT)


def test_every_side_table_has_a_citation() -> None:
    assert set(R.LATE_OPEN_SOURCES) == set(R.LATE_OPENS)
    assert set(R.EARLY_SETTLEMENT_SOURCES) == set(R.EARLY_SETTLEMENT_CT)
    for c in [*R.LATE_OPEN_SOURCES.values(), *R.NO_ENTRY_FINDINGS.values(),
              *R.EARLY_SETTLEMENT_SOURCES.values()]:
        _check_citation(c, needs_time=False)
    for c in R.SESSION_SOURCES.values():
        _check_citation(c, needs_time=True)


def test_cme_status_grades_cite_cme_documents() -> None:
    for day, c in R.SOURCES.items():
        if R.HOLIDAYS[day].evidence == "cme":
            assert "cmegroup.com" in c.status_url, day
        if R.HOLIDAYS[day].time_evidence in ("cme", "inferred"):
            assert "cmegroup.com" in (c.time_url or ""), day


# ------------------------------------------------------------------ side tables ----
def test_the_2025_11_28_outage_is_a_late_open_on_a_planned_early_close() -> None:
    late = R.LATE_OPENS[date(2025, 11, 28)]
    assert (late.open_ct, late.evidence, late.time_evidence) == (time(7, 30), "cme", "cme")
    assert late.halt_from_ct is None  # the stop time is in no source retrieved
    assert R.HOLIDAYS[date(2025, 11, 28)].halt_ct == CLOSE_1215
    assert set(R.LATE_OPENS) == {date(2025, 11, 28)}


def test_early_settlements_fall_before_14_00_on_regular_or_early_close_days() -> None:
    assert R.EARLY_SETTLEMENT_CT
    for day, settle in R.EARLY_SETTLEMENT_CT.items():
        assert FIRST <= day <= LAST
        assert settle < time(14, 0)
        holiday = R.HOLIDAYS.get(day)
        if holiday is None:  # Globex traded its regular hours, or no CME hours document exists
            assert (day in R.NO_ENTRY_FINDINGS) != (day in R.GLOBEX_HOURS_UNDOCUMENTED), day
        else:
            assert holiday.kind is HALT and holiday.halt_ct > settle, day


def test_undocumented_days_are_flagged_not_entered() -> None:
    assert set(R.GLOBEX_HOURS_UNDOCUMENTED) == {
        date(2023, 5, 26), date(2023, 12, 22), date(2023, 12, 29), date(2024, 5, 24),
        date(2025, 5, 23), date(2026, 5, 22)}
    for day, note in R.GLOBEX_HOURS_UNDOCUMENTED.items():
        assert day not in R.HOLIDAYS and day not in R.NO_ENTRY_FINDINGS
        assert day in R.EARLY_SETTLEMENT_CT and note


# ------------------------------------------------------------------ sessions ----
def test_sessions_cover_the_window_with_no_gap_or_overlap() -> None:
    specs = sorted(R.SESSIONS, key=lambda s: s.valid_from)
    assert all(isinstance(s, SessionSpec) for s in specs)
    assert specs[0].valid_from == FIRST
    for prev, nxt in zip(specs, specs[1:], strict=False):
        assert prev.valid_to is not None
        assert prev.valid_to + timedelta(days=1) == nxt.valid_from
    assert specs[-1].valid_to in (LAST, None)
    for s in specs:
        assert s.valid_to is None or s.valid_from <= s.valid_to


def _minutes(offset_days: int, at: time) -> int:
    return offset_days * 1440 + at.hour * 60 + at.minute


def test_each_day_session_lies_inside_a_trading_segment() -> None:
    for s in R.SESSIONS:
        for product, (open_ct, close_ct) in s.day_session_ct.items():
            o, c = _minutes(0, open_ct), _minutes(0, close_ct)
            assert o < c, product
            assert any(_minutes(g.start_offset_days, g.start_ct) <= o
                       and c <= _minutes(g.end_offset_days, g.end_ct) for g in s.segments), product


def test_session_is_the_globex_week_and_d6_values_for_every_rates_product() -> None:
    (spec,) = R.SESSIONS
    assert [(g.start_offset_days, g.start_ct, g.end_offset_days, g.end_ct) for g in spec.segments] \
        == [(-1, time(17, 0), 0, time(16, 0))]
    rates = {p for p, g in GROUP_OF_PRODUCT.items() if g == "rates"}
    assert set(spec.day_session_ct) == rates == set(R.RATES_PRODUCTS)
    assert set(spec.day_session_ct.values()) == {(time(7, 20), time(14, 0))}
    assert spec.source in R.SESSION_SOURCES


# ------------------------------------------------------------------ report agreement ----
@pytest.fixture(scope="module")
def report() -> dict:
    return json.loads(REPORT.read_text())


def test_report_rows_match_the_module_entries(report: dict) -> None:
    rows = {date.fromisoformat(r["date"]): r for r in report["entries"]}
    assert set(rows) == set(R.HOLIDAYS)
    for day, h in R.HOLIDAYS.items():
        r, c = rows[day], R.SOURCES[day]
        assert (r["name"], r["kind"], r["evidence"], r["time_evidence"]) == \
            (h.name, h.kind.value, h.evidence, h.time_evidence)
        assert r["halt_ct"] == (h.halt_ct.strftime("%H:%M") if h.halt_ct else None)
        assert (r["status_url"], r["status_quote"]) == (c.status_url, c.status_quote)
        assert (r["time_url"], r["time_quote"]) == (c.time_url, c.time_quote)
        assert r["verbatim_check"] is True, day
        assert r["bar_check_status"]


def test_report_side_tables_match_and_pass_the_verbatim_check(report: dict) -> None:
    assert report["verbatim_failures"] == []
    for key, table in (("no_entry_findings", R.NO_ENTRY_FINDINGS),
                       ("early_settlements", R.EARLY_SETTLEMENT_SOURCES),
                       ("late_opens", R.LATE_OPEN_SOURCES)):
        rows = {date.fromisoformat(r["date"]): r for r in report[key]}
        assert set(rows) == set(table), key
        for day, c in table.items():
            assert rows[day]["status_quote"] == c.status_quote
            assert rows[day]["verbatim_check"] is True


@pytest.mark.parametrize(("first", "last", "label"), [
    (date(2019, 5, 1), date(2024, 2, 29), "bar check pending the step 2 purchase"),
    (date(2024, 3, 1), date(2025, 3, 31), "never checked against bars"),
    (date(2025, 4, 1), date(2026, 6, 19), "pending Task 7"),
])
def test_report_bar_check_status_follows_the_windows(report: dict, first: date, last: date,
                                                     label: str) -> None:
    for r in report["entries"]:
        if first <= date.fromisoformat(r["date"]) <= last:
            assert label in r["bar_check_status"], r["date"]
