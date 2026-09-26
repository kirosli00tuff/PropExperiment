"""Stage E.2a Task 6: the CME Globex calendar of the grains group (data/calendars/grains.py).

Known-answer tests on the module's own tables. No network, no scratch files, no market data; the
only file read is the repo's own source report (reports/stage_e2a_calendar_sources_grains.json),
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
from data.calendars import grains as G
from data.cme_calendar import CalendarCoverageError, HolidayKind
from data.config import REPO_ROOT

REPORT = REPO_ROOT / "reports" / "stage_e2a_calendar_sources_grains.json"
STATUS_GRADES = {"cme", "secondary", "unverified"}
TIME_GRADES = {"cme", "secondary", "inferred", "unverified", "n/a"}
FIRST, LAST = date(2019, 5, 1), date(2026, 6, 19)
C1205, C1215, OPEN = time(12, 5), time(12, 15), time(8, 30)
FULL, HALT = HolidayKind.FULL_CLOSURE, HolidayKind.EARLY_HALT
PRODUCTS = ("ZC", "ZW", "ZS", "ZM", "ZL")


# ------------------------------------------------------------------ coverage ----
def test_coverage_is_the_design_window() -> None:
    assert G.CALENDAR_COVERAGE == (FIRST, LAST)


@pytest.mark.parametrize("day", [FIRST - timedelta(days=1), LAST + timedelta(days=1),
                                 date(2018, 12, 31), date(2027, 1, 4)])
def test_coverage_refuses_a_date_outside_the_range(day: date) -> None:
    with pytest.raises(CalendarCoverageError, match="grains calendar"):
        G.assert_calendar_coverage([FIRST, day])


def test_coverage_accepts_both_ends_and_an_empty_input() -> None:
    G.assert_calendar_coverage([FIRST, LAST, date(2022, 6, 15)])
    G.assert_calendar_coverage([])


def test_the_equity_interface_types_are_reused_not_redefined() -> None:
    assert G.Holiday is cme_calendar.Holiday
    assert G.HolidayKind is cme_calendar.HolidayKind
    assert G.Citation is cme_calendar.Citation
    assert G.CalendarCoverageError is cme_calendar.CalendarCoverageError


# ------------------------------------------------------------------ entries ----
def test_entries_are_unique_sorted_weekday_dates_inside_coverage() -> None:
    days = [h.day for h in G._ENTRIES]
    assert len(days) == len(set(days)) == len(G.HOLIDAYS) == 82
    assert days == sorted(days)
    for day, holiday in G.HOLIDAYS.items():
        assert holiday.day == day
        assert FIRST <= day <= LAST
        assert day.weekday() < 5, day


def test_entry_counts_by_kind() -> None:
    kinds = [h.kind for h in G.HOLIDAYS.values()]
    assert kinds.count(FULL) == 68
    assert kinds.count(HALT) == 14


KNOWN = [
    # one per holiday name (closures), then every early halt
    (date(2019, 5, 27), "Memorial Day", FULL, None),
    (date(2019, 7, 4), "Independence Day", FULL, None),
    (date(2020, 7, 3), "Independence Day (observed)", FULL, None),
    (date(2021, 7, 5), "Independence Day (observed)", FULL, None),
    (date(2019, 9, 2), "Labor Day", FULL, None),
    (date(2019, 11, 28), "Thanksgiving Day", FULL, None),
    (date(2019, 12, 25), "Christmas Day", FULL, None),
    (date(2021, 12, 24), "Christmas Day (observed)", FULL, None),
    (date(2022, 12, 26), "Christmas Day (observed)", FULL, None),
    (date(2020, 1, 1), "New Year's Day", FULL, None),
    (date(2021, 1, 1), "New Year's Day", FULL, None),
    (date(2023, 1, 2), "New Year's Day (observed)", FULL, None),
    (date(2020, 1, 20), "Martin Luther King Jr. Day", FULL, None),
    (date(2023, 1, 16), "Martin Luther King Jr. Day", FULL, None),
    (date(2020, 2, 17), "Presidents Day", FULL, None),
    (date(2020, 4, 10), "Good Friday", FULL, None),
    (date(2021, 4, 2), "Good Friday", FULL, None),
    (date(2023, 4, 7), "Good Friday", FULL, None),
    (date(2026, 4, 3), "Good Friday", FULL, None),
    (date(2022, 6, 20), "Juneteenth (observed)", FULL, None),
    (date(2023, 6, 19), "Juneteenth", FULL, None),
    (date(2024, 6, 19), "Juneteenth", FULL, None),
    (date(2026, 6, 19), "Juneteenth", FULL, None),
    (date(2024, 7, 4), "Independence Day", FULL, None),
    (date(2019, 7, 3), "Day before Independence Day", HALT, C1205),
    (date(2020, 7, 2), "Day before Independence Day (observed)", HALT, C1205),
    (date(2019, 11, 29), "Day after Thanksgiving", HALT, C1205),
    (date(2020, 11, 27), "Day after Thanksgiving", HALT, C1205),
    (date(2021, 11, 26), "Day after Thanksgiving", HALT, C1205),
    (date(2022, 11, 25), "Day after Thanksgiving", HALT, C1205),
    (date(2023, 11, 24), "Day after Thanksgiving", HALT, C1205),
    (date(2024, 11, 29), "Day after Thanksgiving", HALT, C1205),
    (date(2025, 11, 28), "Day after Thanksgiving", HALT, C1205),
    (date(2019, 12, 24), "Christmas Eve", HALT, C1205),
    (date(2020, 12, 24), "Christmas Eve", HALT, C1205),
    (date(2024, 12, 24), "Christmas Eve", HALT, C1205),
    (date(2025, 12, 24), "Christmas Eve", HALT, C1205),
    (date(2025, 1, 9), "National Day of Mourning (Carter)", HALT, C1215),
]


@pytest.mark.parametrize(("day", "name", "kind", "halt"), KNOWN)
def test_known_entries(day: date, name: str, kind: HolidayKind, halt: time | None) -> None:
    holiday = G.HOLIDAYS[day]
    assert (holiday.name, holiday.kind, holiday.halt_ct) == (name, kind, halt)


def test_every_early_halt_is_listed_in_the_known_answers() -> None:
    halts = {d for d, h in G.HOLIDAYS.items() if h.kind is HALT}
    assert halts == {d for d, _, k, _ in KNOWN if k is HALT}


@pytest.mark.parametrize("day", [date(2019, 12, 31), date(2021, 7, 2), date(2021, 12, 23),
                                 date(2022, 7, 1), date(2022, 12, 23), date(2023, 7, 3),
                                 date(2024, 7, 3), date(2025, 7, 3), date(2026, 4, 2)])
def test_pre_holiday_days_that_cme_shows_as_regular_carry_no_entry(day: date) -> None:
    assert day not in G.HOLIDAYS
    assert day not in G.LATE_OPENS
    assert day in G.NO_ENTRY_FINDINGS


@pytest.mark.parametrize("day", [date(2020, 1, 20), date(2021, 2, 15), date(2022, 5, 30),
                                 date(2022, 6, 20), date(2023, 9, 4), date(2019, 11, 28),
                                 date(2025, 7, 4), date(2026, 4, 3)])
def test_grains_close_fully_where_equities_trade_a_short_session(day: date) -> None:
    equity = cme_calendar.HOLIDAYS[day]
    assert equity.kind is HALT
    assert G.HOLIDAYS[day].kind is FULL


# ------------------------------------------------------------------ late opens ----
LATE_DAYS = [
    date(2019, 7, 5), date(2019, 11, 29), date(2019, 12, 26), date(2020, 1, 2),
    date(2020, 11, 27), date(2021, 7, 6), date(2021, 11, 26), date(2022, 7, 5),
    date(2022, 11, 25), date(2023, 7, 5), date(2023, 11, 24), date(2023, 12, 26),
    date(2024, 1, 2), date(2024, 7, 5), date(2024, 11, 29), date(2024, 12, 26),
    date(2025, 1, 2), date(2025, 11, 28), date(2025, 12, 26), date(2026, 1, 2),
]


def test_late_opens_are_the_known_dates_at_the_day_session_open() -> None:
    assert sorted(G.LATE_OPENS) == LATE_DAYS
    for day, late in G.LATE_OPENS.items():
        assert late.day == day
        assert late.open_ct == OPEN
        assert FIRST <= day <= LAST and day.weekday() < 5
        assert late.evidence in STATUS_GRADES and late.time_evidence in TIME_GRADES - {"n/a"}


def test_every_late_open_follows_a_full_closure_the_calendar_day_before() -> None:
    for day in G.LATE_OPENS:
        assert G.HOLIDAYS[day - timedelta(days=1)].kind is FULL, day


def test_thanksgiving_fridays_have_both_a_late_open_and_an_early_close() -> None:
    fridays = {d for d, h in G.HOLIDAYS.items() if h.name == "Day after Thanksgiving"}
    assert len(fridays) == 7
    assert fridays <= set(G.LATE_OPENS)


MONDAY_HOLIDAYS = ("Martin Luther King Jr. Day", "Presidents Day", "Memorial Day", "Labor Day",
                   "Juneteenth")


def test_mlk_presidents_memorial_labor_juneteenth_closures_reopen_that_evening() -> None:
    # CME reopens grains at 19:00 CT on these holidays, so the next trade date is regular; late
    # opens follow only Independence Day, Thanksgiving, Christmas and New Year's Day closures.
    checked = 0
    for day, holiday in G.HOLIDAYS.items():
        if holiday.kind is FULL and holiday.name.startswith(MONDAY_HOLIDAYS):
            assert day + timedelta(days=1) not in G.LATE_OPENS, day
            checked += 1
    assert checked == 34  # MLK 7, Presidents 7, Memorial 8, Labor 7, Juneteenth 5
    followers = {G.HOLIDAYS[d - timedelta(days=1)].name.split(" (")[0] for d in G.LATE_OPENS}
    assert followers == {"Independence Day", "Thanksgiving Day", "Christmas Day",
                         "New Year's Day"}


# ------------------------------------------------------------------ grades ----
def test_grades_are_in_the_allowed_sets_and_empirical_is_unused() -> None:
    for holiday in G.HOLIDAYS.values():
        assert holiday.evidence in STATUS_GRADES
        assert holiday.time_evidence in TIME_GRADES
        if holiday.kind is FULL:
            assert holiday.halt_ct is None and holiday.time_evidence == "n/a"
        else:
            assert holiday.halt_ct is not None and holiday.time_evidence != "n/a"


def test_the_only_non_cme_status_is_mlk_day_2023() -> None:
    graded = {d: h.evidence for d, h in G.HOLIDAYS.items() if h.evidence != "cme"}
    assert graded == {date(2023, 1, 16): "secondary"}
    assert all(late.evidence == "cme" for late in G.LATE_OPENS.values())


# ------------------------------------------------------------------ citations ----
def test_every_entry_has_a_citation_with_non_empty_quotes() -> None:
    assert set(G.SOURCES) == set(G.HOLIDAYS)
    for day, cite in G.SOURCES.items():
        assert cite.status_url and cite.status_quote.strip(), day
        if G.HOLIDAYS[day].kind is HALT:
            assert cite.time_url and cite.time_quote and cite.time_quote.strip(), day
    assert set(G.LATE_OPEN_SOURCES) == set(G.LATE_OPENS)
    for day, cite in G.LATE_OPEN_SOURCES.items():
        assert cite.status_url and cite.status_quote.strip(), day
        assert cite.time_url and cite.time_quote and cite.time_quote.strip(), day


def test_status_urls_are_cme_except_the_one_secondary_entry() -> None:
    for day, cite in {**G.SOURCES, **G.LATE_OPEN_SOURCES}.items():
        if day == date(2023, 1, 16) and day in G.SOURCES:
            assert "ampfutures.com" in G.SOURCES[day].status_url
            continue
        assert cite.status_url.startswith("https://www.cmegroup.com/"), day


def test_no_entry_findings_are_not_entries_and_are_cited() -> None:
    assert G.NO_ENTRY_FINDINGS
    for day, cite in G.NO_ENTRY_FINDINGS.items():
        assert FIRST <= day <= LAST
        assert day not in G.HOLIDAYS and day not in G.LATE_OPENS
        assert cite.status_url and cite.status_quote.strip() and cite.note


def test_module_citations_match_the_source_report() -> None:
    report = json.loads(REPORT.read_text())
    assert report["verbatim_failures"] == []
    rows = {date.fromisoformat(r["date"]): r for r in report["entries"]}
    assert set(rows) == set(G.HOLIDAYS)
    for day, row in rows.items():
        holiday, cite = G.HOLIDAYS[day], G.SOURCES[day]
        assert row["kind"] == holiday.kind.value and row["name"] == holiday.name
        assert row["halt_ct"] == (holiday.halt_ct.strftime("%H:%M") if holiday.halt_ct else None)
        assert (row["evidence"], row["time_evidence"]) == (holiday.evidence,
                                                           holiday.time_evidence)
        assert (row["status_url"], row["status_quote"]) == (cite.status_url, cite.status_quote)
        assert (row["time_url"], row["time_quote"]) == (cite.time_url, cite.time_quote)
        assert row["verbatim_check"] is (day != date(2023, 1, 16)), day
    late = {date.fromisoformat(r["date"]): r for r in report["late_opens"]}
    assert set(late) == set(G.LATE_OPENS)
    for day, row in late.items():
        assert row["verbatim_check"] is True
        assert row["status_quote"] == G.LATE_OPEN_SOURCES[day].status_quote


# ------------------------------------------------------------------ sessions ----
def test_sessions_cover_the_window_without_gap_or_overlap() -> None:
    specs = sorted(G.SESSIONS, key=lambda s: s.valid_from)
    assert all(isinstance(s, SessionSpec) for s in specs)
    assert specs[0].valid_from == FIRST
    assert specs[-1].valid_to == LAST
    for a, b in zip(specs, specs[1:], strict=False):
        assert a.valid_to is not None and b.valid_from == a.valid_to + timedelta(days=1)
    for s in specs:
        assert s.valid_to is None or s.valid_from <= s.valid_to


def _minutes(offset_days: int, at: time) -> int:
    return offset_days * 1440 + at.hour * 60 + at.minute


def test_segments_are_ordered_and_the_grain_session_is_as_cme_states() -> None:
    (spec,) = G.SESSIONS
    spans = [(_minutes(s.start_offset_days, s.start_ct), _minutes(s.end_offset_days, s.end_ct))
             for s in spec.segments]
    assert spans == [(_minutes(-1, time(19, 0)), _minutes(0, time(7, 45))),
                     (_minutes(0, time(8, 30)), _minutes(0, time(13, 20)))]
    assert all(lo < hi for lo, hi in spans)
    assert spans[0][1] < spans[1][0]  # the 07:45-08:30 CT pause
    assert spec.source in G.SESSION_SOURCES


def test_day_session_is_d6_and_lies_inside_a_trading_segment() -> None:
    (spec,) = G.SESSIONS
    assert set(spec.day_session_ct) == set(PRODUCTS)
    assert {p for p, g in GROUP_OF_PRODUCT.items() if g == "grains"} == set(PRODUCTS)
    for product, (o, c) in spec.day_session_ct.items():
        assert (o, c) == (time(8, 30), time(13, 15)), product
        lo, hi = _minutes(0, o), _minutes(0, c)
        assert any(_minutes(s.start_offset_days, s.start_ct) <= lo and
                   hi <= _minutes(s.end_offset_days, s.end_ct) for s in spec.segments), product


@pytest.mark.parametrize("key", ["settle_zc", "settle_zw", "settle_zs", "settle_zm", "settle_zl"])
def test_each_product_settlement_source_states_the_1314_1315_period(key: str) -> None:
    quote = G.SESSION_SOURCES[key].status_quote
    assert "between 13:14:00 and 13:15:00 Central Time (CT)" in quote
    assert f"({key[-2:].upper()})" in quote


# ------------------------------------------- how the tables combine (synthetic trade dates) ----
def _trade_minutes(day: date) -> int:
    """Scheduled one-minute bars of grain trade date ``day`` from SESSIONS, HOLIDAYS and
    LATE_OPENS: a full closure has none; a late open drops the overnight segment and starts at
    open_ct; an early halt ends the day session at halt_ct (last bar at halt_ct minus one)."""
    holiday = G.HOLIDAYS.get(day)
    if holiday is not None and holiday.kind is FULL:
        return 0
    (spec,) = G.SESSIONS
    total = 0
    for seg in spec.segments:
        lo, hi = _minutes(seg.start_offset_days, seg.start_ct), _minutes(seg.end_offset_days,
                                                                            seg.end_ct)
        if day in G.LATE_OPENS:
            lo = max(lo, _minutes(0, G.LATE_OPENS[day].open_ct))
        if holiday is not None and holiday.kind is HALT:
            hi = min(hi, _minutes(0, holiday.halt_ct))
        total += max(0, hi - lo)
    return total


@pytest.mark.parametrize(("day", "bars"), [
    (date(2024, 11, 26), 765 + 290),   # regular: 19:00-07:45 and 08:30-13:20
    (date(2024, 11, 28), 0),           # Thanksgiving: closed
    (date(2024, 11, 29), 215),         # late open 08:30, early close 12:05 (last bar 12:04)
    (date(2024, 12, 24), 765 + 215),   # overnight, then 08:30-12:05
    (date(2024, 12, 26), 290),         # late open: day session only
    (date(2025, 1, 9), 765 + 225),     # Day of Mourning: 08:30-12:15
    (date(2019, 7, 3), 765 + 215),
    (date(2019, 7, 5), 290),
    (date(2021, 7, 6), 290),
    (date(2022, 12, 27), 765 + 290),   # after a Monday closure the Monday 19:00 CT open is regular
])
def test_trade_date_minutes_follow_from_the_tables(day: date, bars: int) -> None:
    assert _trade_minutes(day) == bars
