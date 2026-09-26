"""Known-answer tests for the crypto-group CME calendar (data/calendars/crypto.py, Stage E.2a).

Synthetic inputs only: no network, no scratch files, no market data. The verbatim check of each
quote against the fetched CME documents was run once by the build script and is recorded in
reports/stage_e2a_calendar_sources_crypto.json (the fetched files live outside the repo).
"""

from __future__ import annotations

from datetime import date, time, timedelta

import pytest

import data.calendars.crypto as crypto
import data.cme_calendar as cme
from data.calendars import GROUP_OF_PRODUCT, Segment, SessionSpec
from data.cme_calendar import CalendarCoverageError, Citation, Holiday, HolidayKind

FULL = HolidayKind.FULL_CLOSURE
HALT = HolidayKind.EARLY_HALT
STATUS_GRADES = {"cme", "secondary", "unverified"}
TIME_GRADES = {"cme", "secondary", "inferred", "unverified", "n/a"}
FIRST, LAST = date(2019, 5, 1), date(2026, 6, 19)
SWITCH_DAY = date(2026, 5, 29)  # 24/7 trading from 16:00 CT that Friday

# Every HOLIDAYS entry: (date, name, kind, halt_ct). All are graded status "cme"; time "cme"
# for halts and "n/a" for closures (test_grades_by_kind).
KNOWN = [
    (date(2019, 5, 27), "Memorial Day", HALT, time(12, 0)),
    (date(2019, 7, 3), "Day before Independence Day", HALT, time(12, 15)),
    (date(2019, 7, 4), "Independence Day", HALT, time(12, 0)),
    (date(2019, 9, 2), "Labor Day", HALT, time(12, 0)),
    (date(2019, 11, 28), "Thanksgiving Day", HALT, time(12, 0)),
    (date(2019, 11, 29), "Day after Thanksgiving", HALT, time(12, 15)),
    (date(2019, 12, 24), "Christmas Eve", HALT, time(12, 15)),
    (date(2019, 12, 25), "Christmas Day", FULL, None),
    (date(2020, 1, 1), "New Year's Day", FULL, None),
    (date(2020, 1, 20), "Martin Luther King Jr. Day", HALT, time(12, 0)),
    (date(2020, 2, 17), "Presidents Day", HALT, time(12, 0)),
    (date(2020, 4, 10), "Good Friday", FULL, None),
    (date(2020, 5, 25), "Memorial Day", HALT, time(12, 0)),
    (date(2020, 7, 3), "Independence Day (observed)", HALT, time(12, 0)),
    (date(2020, 9, 7), "Labor Day", HALT, time(12, 0)),
    (date(2020, 11, 26), "Thanksgiving Day", HALT, time(12, 0)),
    (date(2020, 11, 27), "Day after Thanksgiving", HALT, time(12, 15)),
    (date(2020, 12, 24), "Christmas Eve", HALT, time(12, 15)),
    (date(2020, 12, 25), "Christmas Day", FULL, None),
    (date(2021, 1, 1), "New Year's Day", FULL, None),
    (date(2021, 1, 18), "Martin Luther King Jr. Day", HALT, time(12, 0)),
    (date(2021, 2, 15), "Presidents Day", HALT, time(12, 0)),
    (date(2021, 4, 2), "Good Friday (abbreviated, jobs report)", HALT, time(8, 15)),
    (date(2021, 5, 31), "Memorial Day", HALT, time(12, 0)),
    (date(2021, 7, 5), "Independence Day (observed)", HALT, time(12, 0)),
    (date(2021, 9, 6), "Labor Day", HALT, time(12, 0)),
    (date(2021, 11, 25), "Thanksgiving Day", HALT, time(12, 0)),
    (date(2021, 11, 26), "Day after Thanksgiving", HALT, time(12, 45)),
    (date(2021, 12, 24), "Christmas Day (observed)", FULL, None),
    (date(2022, 4, 15), "Good Friday", FULL, None),
    (date(2022, 11, 25), "Day after Thanksgiving", HALT, time(12, 45)),
    (date(2022, 12, 26), "Christmas Day (observed)", FULL, None),
    (date(2023, 1, 2), "New Year's Day (observed)", FULL, None),
    (date(2023, 4, 7), "Good Friday (abbreviated, jobs report)", HALT, time(10, 15)),
    (date(2023, 11, 24), "Day after Thanksgiving", HALT, time(12, 45)),
    (date(2023, 12, 25), "Christmas Day", FULL, None),
    (date(2024, 1, 1), "New Year's Day", FULL, None),
    (date(2024, 3, 29), "Good Friday", FULL, None),
    (date(2024, 11, 29), "Day after Thanksgiving", HALT, time(13, 45)),
    (date(2024, 12, 24), "Christmas Eve", HALT, time(12, 45)),
    (date(2024, 12, 25), "Christmas Day", FULL, None),
    (date(2025, 1, 1), "New Year's Day", FULL, None),
    (date(2025, 4, 18), "Good Friday", FULL, None),
    (date(2025, 7, 4), "Independence Day", HALT, time(12, 0)),
    (date(2025, 11, 28), "Day after Thanksgiving", HALT, time(13, 45)),
    (date(2025, 12, 24), "Christmas Eve", HALT, time(12, 45)),
    (date(2025, 12, 25), "Christmas Day", FULL, None),
    (date(2026, 1, 1), "New Year's Day", FULL, None),
    (date(2026, 4, 3), "Good Friday (abbreviated, jobs report)", HALT, time(10, 15)),
]

# US holidays on which crypto traded its regular hours (CME trade date booked forward).
KNOWN_FORWARD = [
    (date(2022, 1, 17), date(2022, 1, 18), "cme"),
    (date(2022, 6, 20), date(2022, 6, 21), "cme"),
    (date(2022, 7, 4), date(2022, 7, 5), "cme"),
    (date(2022, 11, 24), date(2022, 11, 25), "cme"),
    (date(2023, 1, 16), date(2023, 1, 17), "unverified"),
    (date(2023, 2, 20), date(2023, 2, 21), "cme"),
    (date(2023, 7, 4), date(2023, 7, 5), "cme"),
    (date(2024, 6, 19), date(2024, 6, 20), "cme"),
    (date(2024, 7, 4), date(2024, 7, 5), "cme"),
    (date(2024, 11, 28), date(2024, 11, 29), "cme"),
    (date(2025, 9, 1), date(2025, 9, 2), "cme"),
    (date(2025, 11, 27), date(2025, 11, 28), "cme"),
    (date(2026, 5, 25), date(2026, 5, 26), "cme"),
    (date(2026, 6, 19), date(2026, 6, 22), "cme"),
]

NORMAL_DAYS = [date(2019, 12, 31), date(2020, 7, 2), date(2021, 7, 2), date(2021, 12, 31),
               date(2022, 12, 23), date(2023, 7, 3), date(2024, 7, 3), date(2025, 1, 9),
               date(2025, 7, 3), date(2025, 12, 31), date(2026, 5, 29)]


# ---------------------------------------------------------------- interface and coverage
def test_types_are_imported_from_the_equity_module_not_redefined():
    assert crypto.Holiday is cme.Holiday
    assert crypto.HolidayKind is cme.HolidayKind
    assert crypto.Citation is cme.Citation
    assert crypto.CalendarCoverageError is cme.CalendarCoverageError


def test_products_are_the_crypto_group():
    assert crypto.CRYPTO_PRODUCTS == ("MBT",)
    assert {p for p, g in GROUP_OF_PRODUCT.items() if g == "crypto"} == {"MBT"}


def test_coverage_is_the_design_window():
    assert crypto.CALENDAR_COVERAGE == (FIRST, LAST)


@pytest.mark.parametrize("outside", [date(2019, 4, 30), date(2026, 6, 20), date(2018, 1, 2)])
def test_coverage_refuses_a_date_outside_the_range(outside):
    with pytest.raises(CalendarCoverageError):
        crypto.assert_calendar_coverage([FIRST, outside])


def test_coverage_accepts_the_boundaries_and_empty_input():
    crypto.assert_calendar_coverage([FIRST, LAST, date(2022, 6, 1)])
    crypto.assert_calendar_coverage([])


def test_coverage_error_reports_the_count_and_the_extremes():
    pattern = r"2 trade date\(s\).*2019-04-01 \.\. 2026-07-01"
    with pytest.raises(CalendarCoverageError, match=pattern):
        crypto.assert_calendar_coverage([date(2026, 7, 1), date(2019, 4, 1), date(2020, 1, 2)])


# ---------------------------------------------------------------- entries
@pytest.mark.parametrize("day, name, kind, halt", KNOWN)
def test_known_entry(day, name, kind, halt):
    h = crypto.HOLIDAYS[day]
    assert (h.day, h.name, h.kind, h.halt_ct) == (day, name, kind, halt)
    assert h.evidence == "cme"
    assert h.time_evidence == ("n/a" if kind is FULL else "cme")


def test_known_answers_are_the_whole_table():
    assert {k[0] for k in KNOWN} == set(crypto.HOLIDAYS)
    assert len(crypto.HOLIDAYS) == 49


def test_entry_counts_by_kind():
    kinds = [h.kind for h in crypto.HOLIDAYS.values()]
    assert kinds.count(FULL) == 17
    assert kinds.count(HALT) == 32


def test_from_2022_us_holiday_halts_are_gone_except_the_friday_july_fourth():
    """From MLK Day 2022 crypto trades regular hours on the holidays equities halt at 12:00 CT;
    the only later 12:00 CT entry is Friday 2025-07-04."""
    noon_after = [d for d, h in crypto.HOLIDAYS.items()
                  if d >= date(2022, 1, 1) and h.halt_ct == time(12, 0)]
    assert noon_after == [date(2025, 7, 4)]


def test_day_after_thanksgiving_close_regimes():
    closes = {d.year: h.halt_ct for d, h in crypto.HOLIDAYS.items()
              if h.name == "Day after Thanksgiving"}
    assert closes == {2019: time(12, 15), 2020: time(12, 15), 2021: time(12, 45),
                      2022: time(12, 45), 2023: time(12, 45), 2024: time(13, 45),
                      2025: time(13, 45)}


def test_good_fridays():
    gf = {d: h for d, h in crypto.HOLIDAYS.items() if h.name.startswith("Good Friday")}
    assert sorted(gf) == [date(2020, 4, 10), date(2021, 4, 2), date(2022, 4, 15),
                          date(2023, 4, 7), date(2024, 3, 29), date(2025, 4, 18),
                          date(2026, 4, 3)]
    assert all(d.weekday() == 4 for d in gf)
    abbreviated = {d: h.halt_ct for d, h in gf.items() if h.kind is HALT}
    assert abbreviated == {date(2021, 4, 2): time(8, 15), date(2023, 4, 7): time(10, 15),
                           date(2026, 4, 3): time(10, 15)}


@pytest.mark.parametrize("day", NORMAL_DAYS)
def test_cme_stated_normal_days_carry_no_entry(day):
    assert day not in crypto.HOLIDAYS
    assert day in crypto.NO_ENTRY_FINDINGS


def test_no_duplicate_dates_and_keys_match_days():
    days = [h.day for h in crypto._ENTRIES]
    assert len(days) == len(set(days)) == len(crypto.HOLIDAYS)
    assert all(k == h.day for k, h in crypto.HOLIDAYS.items())
    assert days == sorted(days)


def test_every_entry_is_a_weekday_inside_the_coverage():
    for d in crypto.HOLIDAYS:
        assert FIRST <= d <= LAST
        assert d.weekday() < 5


def test_kind_and_time_fields_agree():
    for h in crypto.HOLIDAYS.values():
        assert isinstance(h, Holiday)
        if h.kind is FULL:
            assert h.halt_ct is None and h.time_evidence == "n/a"
        else:
            assert h.halt_ct is not None and h.time_evidence != "n/a"
            assert time(8, 0) <= h.halt_ct < time(16, 0)


def test_grades_are_in_the_allowed_sets():
    for h in crypto.HOLIDAYS.values():
        assert h.evidence in STATUS_GRADES
        assert h.time_evidence in TIME_GRADES
    for lo in crypto.LATE_OPENS.values():
        assert lo.evidence in STATUS_GRADES and lo.time_evidence in TIME_GRADES
    for f in crypto.BOOKED_FORWARD.values():
        assert f.evidence in STATUS_GRADES
    everything = [h.evidence for h in crypto.HOLIDAYS.values()] + [
        h.time_evidence for h in crypto.HOLIDAYS.values()]
    assert "empirical" not in everything


# ---------------------------------------------------------------- citations
def _has_quotes(c: Citation, needs_time: bool) -> None:
    assert isinstance(c, Citation)
    assert c.status_url and c.status_url.startswith("https://")
    assert c.status_quote.strip()
    if needs_time:
        assert c.time_url and c.time_url.startswith("https://")
        assert c.time_quote and c.time_quote.strip()


def test_every_entry_has_a_citation_with_non_empty_quotes():
    assert set(crypto.SOURCES) == set(crypto.HOLIDAYS)
    for d, h in crypto.HOLIDAYS.items():
        _has_quotes(crypto.SOURCES[d], needs_time=h.kind is HALT)
        assert crypto.SOURCES[d].note.strip()


def test_citations_are_cme_documents():
    allowed = ("https://www.cmegroup.com/", "https://cmegroupclientsite.atlassian.net/")
    for c in crypto.SOURCES.values():
        assert c.status_url.startswith(allowed)
        assert c.time_url is None or c.time_url.startswith(allowed)


def test_quoted_halt_time_appears_in_the_time_quote():
    """The halt time is stated in the cited quote, in the form that document uses."""
    for d, h in crypto.HOLIDAYS.items():
        if h.kind is not HALT:
            continue
        q = crypto.SOURCES[d].time_quote
        hh, mm = h.halt_ct.hour, h.halt_ct.minute
        forms = (f"{hh:02d}{mm:02d} CT", f"{hh:02d}:{mm:02d}", f"{hh}:{mm:02d}")
        assert any(f in q for f in forms), (d, q)


def test_no_entry_findings_are_cited_and_not_entries():
    assert len(crypto.NO_ENTRY_FINDINGS) == 16
    for d, c in crypto.NO_ENTRY_FINDINGS.items():
        assert d not in crypto.HOLIDAYS
        assert FIRST <= d <= LAST
        _has_quotes(c, needs_time=False)


# ---------------------------------------------------------------- additive extensions
@pytest.mark.parametrize("day, trade_date, evidence", KNOWN_FORWARD)
def test_known_booked_forward_day(day, trade_date, evidence):
    f = crypto.BOOKED_FORWARD[day]
    assert (f.day, f.cme_trade_date, f.evidence) == (day, trade_date, evidence)


def test_booked_forward_days_are_weekdays_booked_to_a_later_weekday_and_not_entries():
    assert len(crypto.BOOKED_FORWARD) == 31
    assert set(crypto.BOOKED_FORWARD_SOURCES) == set(crypto.BOOKED_FORWARD)
    for d, f in crypto.BOOKED_FORWARD.items():
        assert d == f.day and d not in crypto.HOLIDAYS
        assert d.weekday() < 5 and f.cme_trade_date.weekday() < 5
        assert timedelta(days=1) <= f.cme_trade_date - d <= timedelta(days=3)
        assert date(2022, 1, 1) <= d <= LAST


def test_only_the_2023_mlk_record_is_unverified_and_it_says_so():
    unverified = [d for d, f in crypto.BOOKED_FORWARD.items() if f.evidence != "cme"]
    assert unverified == [date(2023, 1, 16)]
    c = crypto.BOOKED_FORWARD_SOURCES[date(2023, 1, 16)]
    assert c.status_url is None and c.status_quote == "[unverified]"
    assert "[unverified]" in c.note
    for d, c in crypto.BOOKED_FORWARD_SOURCES.items():
        if d != date(2023, 1, 16):
            _has_quotes(c, needs_time=False)


def test_late_opens_hold_only_the_outage():
    """LATE_OPENS keeps the rates/energy meaning (open on the trade date itself, an unscheduled
    event named as an outage), which data.group_session relies on."""
    assert set(crypto.LATE_OPENS) == set(crypto.LATE_OPEN_SOURCES) == {date(2025, 11, 28)}
    outage = crypto.LATE_OPENS[date(2025, 11, 28)]
    assert (outage.open_ct, outage.open_offset_days, outage.halt_from_ct) == (
        time(7, 30), 0, None)
    assert "outage" in outage.name.lower()
    assert crypto.HOLIDAYS[date(2025, 11, 28)].halt_ct == time(13, 45)
    for c in crypto.LATE_OPEN_SOURCES.values():
        _has_quotes(c, needs_time=True)


def test_day_one_extended_maintenance_opens_the_first_24_7_trade_date_on_friday():
    assert set(crypto.EXTENDED_MAINTENANCE) == set(crypto.EXTENDED_MAINTENANCE_SOURCES) == {
        date(2026, 6, 1)}
    assert not set(crypto.EXTENDED_MAINTENANCE) & set(crypto.LATE_OPENS)
    day_one = crypto.EXTENDED_MAINTENANCE[date(2026, 6, 1)]
    assert (day_one.open_ct, day_one.open_offset_days) == (time(16, 30), -3)
    assert (day_one.halt_from_ct, day_one.halt_from_offset_days) == (time(16, 0), -3)
    assert date(2026, 6, 1) + timedelta(days=day_one.open_offset_days) == SWITCH_DAY
    regular_start = crypto.SEGMENTS_AFTER_WEEKEND_24_7[0]
    assert (regular_start.start_offset_days, regular_start.start_ct) == (-3, time(16, 2))
    assert day_one.open_ct > regular_start.start_ct
    for c in crypto.EXTENDED_MAINTENANCE_SOURCES.values():
        _has_quotes(c, needs_time=True)


def test_weekend_assignment_starts_with_the_first_24_7_trade_date():
    weekend_from = crypto.WEEKEND_TO_NEXT_TRADE_DATE_FROM
    assert weekend_from == date(2026, 6, 1)
    assert weekend_from == crypto.SESSIONS[1].valid_from


def test_undocumented_hours_are_the_unverified_record():
    assert set(crypto.GLOBEX_HOURS_UNDOCUMENTED) == {date(2023, 1, 16)}
    assert crypto.BOOKED_FORWARD[date(2023, 1, 16)].evidence == "unverified"
    assert all(n.strip() for n in crypto.GLOBEX_HOURS_UNDOCUMENTED.values())


def test_late_open_default_offset_keeps_the_other_groups_meaning():
    lo = crypto.LateOpen(date(2025, 1, 2), "x", time(7, 30), "cme", "cme")
    assert (lo.open_offset_days, lo.halt_from_offset_days, lo.halt_from_ct) == (0, -1, None)


# ---------------------------------------------------------------- sessions
def _segments_ok(segs: tuple[Segment, ...]) -> None:
    for s in segs:
        assert (s.start_offset_days, s.start_ct) < (s.end_offset_days, s.end_ct)
    for a, b in zip(segs, segs[1:], strict=False):
        assert (a.end_offset_days, a.end_ct) < (b.start_offset_days, b.start_ct)


def test_sessions_cover_the_range_without_gap_or_overlap():
    specs = crypto.SESSIONS
    assert all(isinstance(s, SessionSpec) for s in specs)
    assert specs[0].valid_from == FIRST and specs[-1].valid_to == LAST
    day = FIRST
    while day <= LAST:
        if day.weekday() < 5:  # trade dates are weekdays in both regimes
            covering = [s for s in specs if s.valid_from <= day <= s.valid_to]
            assert len(covering) == 1, day
        day += timedelta(days=1)
    for a, b in zip(specs, specs[1:], strict=False):
        assert a.valid_to < b.valid_from
        gap = a.valid_to + timedelta(days=1)
        while gap < b.valid_from:
            assert gap.weekday() >= 5, gap  # only weekend days between regimes
            gap += timedelta(days=1)


def test_the_regime_split_is_at_the_24_7_launch():
    five_day, twenty_four_seven = crypto.SESSIONS
    assert five_day.valid_to == SWITCH_DAY == crypto.LAST_5DAY_TRADE_DATE
    assert twenty_four_seven.valid_from == date(2026, 6, 1) == crypto.FIRST_24_7_TRADE_DATE
    assert five_day.segments == (Segment(-1, time(17, 0), 0, time(16, 0)),)
    assert twenty_four_seven.segments == (Segment(-1, time(16, 2), 0, time(16, 0)),)
    monday = (Segment(-3, time(16, 2), -2, time(2, 0)), Segment(-2, time(4, 0), 0, time(16, 0)))
    after_weekend = crypto.SEGMENTS_AFTER_WEEKEND_24_7
    assert after_weekend == monday
    for s in (five_day.segments, twenty_four_seven.segments, after_weekend):
        _segments_ok(s)


def test_24_7_note_carries_the_weekend_rule_and_maintenance_windows():
    note = crypto.SESSIONS[1].note
    assert ("All holiday or weekend trading from Friday evening through Sunday evening will have "
            "a trade date of the following business day") in note
    assert "4:00 p.m. to 4:02 p.m. CT" in note and "2:00 a.m. to 4:00 a.m. CT" in note


def test_day_session_is_the_d6_value():
    for s in crypto.SESSIONS:
        assert s.day_session_ct == {"MBT": (time(8, 30), time(15, 0))}
        assert "D6 confirmation" in s.note


def test_each_day_session_lies_inside_a_trading_segment():
    shapes = [s.segments for s in crypto.SESSIONS] + [crypto.SEGMENTS_AFTER_WEEKEND_24_7]
    for segs in shapes:
        for o, c in crypto.SESSIONS[0].day_session_ct.values():
            assert any((seg.start_offset_days, seg.start_ct) <= (0, o)
                       and (0, c) <= (seg.end_offset_days, seg.end_ct) for seg in segs)


def test_d6_flatten_time_lies_inside_the_session():
    flatten = time(15, 8)
    for segs in [s.segments for s in crypto.SESSIONS] + [crypto.SEGMENTS_AFTER_WEEKEND_24_7]:
        last = segs[-1]
        assert last.end_offset_days == 0 and flatten < last.end_ct


def test_holiday_entries_lie_in_the_5_day_regime():
    """Every clock departure predates 24/7; the one holiday inside it is booked forward."""
    assert max(crypto.HOLIDAYS) < SWITCH_DAY
    assert [d for d in crypto.BOOKED_FORWARD if d > SWITCH_DAY] == [date(2026, 6, 19)]


def test_session_sources_have_quotes_and_sessions_name_them():
    keys = set(crypto.SESSION_SOURCES)
    assert {s.source for s in crypto.SESSIONS} <= keys
    for c in crypto.SESSION_SOURCES.values():
        _has_quotes(c, needs_time=False)
