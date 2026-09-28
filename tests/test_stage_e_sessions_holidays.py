"""Stage E.5 (harness v5): the derived 2019-2023 Topstep holiday rows in rules/sessions.py.

reports/stage_e5_harness_plan.md 3a. Rule H-1 is re-derived here from the frozen equity calendar
(data.cme_calendar.HOLIDAYS) and checked (i) against every published 2024-2026 row, with the four
known exceptions named; (ii) against the literal 2019-2023 rows and the unsettled list; (iii) for
the rows' span; (iv) through day_rule on derived dates, the audit's 15 FX dates and an unsettled
date; (v) nothing from 2024-01-01 on changes against a frozen copy of the v4 tables.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta

import pytest

from data.calendars import GROUPS
from data.cme_calendar import HOLIDAYS as EQUITY
from data.cme_calendar import Holiday, HolidayKind
from rules import sessions as S

LEAD_30, LEAD_15 = timedelta(minutes=30), timedelta(minutes=15)
PUBLISHED_LEAD = {2024: LEAD_30, 2025: LEAD_30, 2026: LEAD_15}
DERIVED_LEAD = LEAD_30  # lead ruling L-E5-2
DERIVED_SOURCE = "topstep_derived_e5_equity_calendar"
ROOT_OF_GROUP = {"equity": "NQ", "rates": "ZN", "fx": "6E", "energy": "CL", "metals": "GC",
                 "crypto": "MBT", "grains": "ZC", "livestock": "LE"}

# The four dates where Rule H-1 and the published schedules differ (plan section 2).
KNOWN_EXCEPTIONS = {
    date(2024, 7, 3): "published 11:30, rule 11:45: the equity halt was 12:15",
    date(2024, 1, 1): "rule date not published: before the 2024 article's first row (the 2023 "
                      "article is not held)",
    date(2025, 1, 9): "rule date not published: the unscheduled national day of mourning, closed "
                      "by CME after the schedule was published",
    date(2025, 7, 3): "rule date not published: omitted from Topstep's 2025 schedule",
}
# A published row the rule cannot reach: the frozen equity calendar ends in 2026.
PUBLISHED_BEYOND_THE_CALENDAR = {date(2027, 1, 1)}

# The v4 tables (harness v4, sha256 82ae8536...), frozen here as they stood before Stage E.5.
V4_LEAD = {2024: LEAD_30, 2025: LEAD_30, 2026: LEAD_15}
V4_ROWS = (
    (date(2024, 1, 15), time(11, 30), "topstep_8284222_2024"),
    (date(2024, 2, 19), time(11, 30), "topstep_8284222_2024"),
    (date(2024, 3, 29), None, "topstep_8284222_2024"),
    (date(2024, 5, 27), time(11, 30), "topstep_8284222_2024"),
    (date(2024, 6, 19), time(11, 30), "topstep_8284222_2024"),
    (date(2024, 7, 3), time(11, 30), "topstep_8284222_2024"),
    (date(2024, 7, 4), time(11, 30), "topstep_8284222_2024"),
    (date(2024, 9, 2), time(11, 30), "topstep_8284222_2024"),
    (date(2024, 11, 28), time(11, 30), "topstep_8284222_2024"),
    (date(2024, 11, 29), time(11, 45), "topstep_8284222_2024"),
    (date(2024, 12, 24), time(11, 45), "topstep_8284222_2024"),
    (date(2024, 12, 25), None, "topstep_8284222_2024"),
    (date(2025, 1, 1), None, "topstep_8284222_2024"),
    (date(2025, 1, 20), time(11, 30), "topstep_8284222_2025"),
    (date(2025, 2, 17), time(11, 30), "topstep_8284222_2025"),
    (date(2025, 4, 18), None, "topstep_8284222_2025"),
    (date(2025, 5, 26), time(11, 30), "topstep_8284222_2025"),
    (date(2025, 6, 19), time(11, 30), "topstep_8284222_2025"),
    (date(2025, 7, 4), time(11, 30), "topstep_8284222_2025"),
    (date(2025, 9, 1), time(11, 30), "topstep_8284222_2025"),
    (date(2025, 11, 27), time(11, 30), "topstep_8284222_2025"),
    (date(2025, 11, 28), time(11, 45), "topstep_8284222_2025"),
    (date(2025, 12, 24), time(11, 45), "topstep_8284222_2025"),
    (date(2025, 12, 25), None, "topstep_8284222_2025"),
    (date(2026, 1, 1), None, "topstep_8284222_2025"),
    (date(2026, 1, 19), time(11, 45), "topstep_13350348_2026"),
    (date(2026, 2, 16), time(11, 45), "topstep_13350348_2026"),
    (date(2026, 4, 3), time(8, 0), "topstep_13350348_2026"),
    (date(2026, 5, 25), time(11, 45), "topstep_13350348_2026"),
    (date(2026, 6, 19), time(11, 45), "topstep_13350348_2026"),
    (date(2026, 7, 3), time(11, 45), "topstep_13350348_2026"),
    (date(2026, 9, 7), time(11, 45), "topstep_13350348_2026"),
    (date(2026, 11, 26), time(11, 45), "topstep_13350348_2026"),
    (date(2026, 11, 27), time(12, 0), "topstep_13350348_2026"),
    (date(2026, 12, 24), time(12, 0), "topstep_13350348_2026"),
    (date(2026, 12, 25), None, "topstep_13350348_2026"),
    (date(2027, 1, 1), None, "topstep_13350348_2026"),
)
V4_TABLE = {d: S.TopstepHoliday(d, t, src) for d, t, src in V4_ROWS}

# The audit's 15 FX dates (E.4c N-1): F was the regular 15:08 CT under v4.
AUDIT_FX_DATES = (
    date(2019, 7, 3), date(2022, 1, 17), date(2022, 2, 21), date(2022, 5, 30), date(2022, 7, 4),
    date(2022, 9, 5), date(2022, 11, 24), date(2023, 1, 16), date(2023, 2, 20), date(2023, 5, 29),
    date(2023, 6, 19), date(2023, 7, 3), date(2023, 7, 4), date(2023, 9, 4), date(2023, 11, 23),
)


def _minus(at: time, delta: timedelta) -> time:
    return (datetime.combine(date(2000, 1, 3), at) - delta).time()


def _rule_h1(first: date, last: date, lead: dict[int, timedelta] | timedelta
             ) -> dict[date, time | None]:
    """Rule H-1 on the frozen equity calendar: close-by per listed weekday (None = closed)."""
    out: dict[date, time | None] = {}
    for day, hol in sorted(EQUITY.items()):
        if not first <= day <= last or day.weekday() >= 5:
            continue
        y_lead = lead if isinstance(lead, timedelta) else lead[day.year]
        if hol.kind is HolidayKind.FULL_CLOSURE:
            out[day] = None
        else:
            assert hol.halt_ct is not None
            out[day] = _minus(hol.halt_ct, y_lead)
    return out


def _base_name(name: str) -> str:
    """The holiday without its qualifier: "Christmas Day (observed)" -> "Christmas Day"."""
    return name.split(" (")[0]


def _published() -> dict[date, time | None]:
    return {d: r.close_by_ct for d, r in S.TOPSTEP_HOLIDAYS.items()
            if r.source != DERIVED_SOURCE}


def _derived() -> dict[date, time | None]:
    return {d: r.close_by_ct for d, r in S.TOPSTEP_HOLIDAYS.items()
            if r.source == DERIVED_SOURCE}


def _ordinary_names() -> set[str]:
    """Holidays Topstep published in 2024-2026: base names of the equity entries on its dates."""
    return {_base_name(EQUITY[d].name) for d in _published() if d in EQUITY}


def _state(rule: S.DayRule) -> str:
    return "closed" if rule.closed else f"{rule.flatten_ct:%H:%M}"


# ------------------------------------------------------------ (i) validation ----
def test_rule_h1_reproduces_every_published_row_but_the_four_named_exceptions() -> None:
    # Arrange
    published = _published()
    rule = _rule_h1(date(2024, 1, 1), date(2026, 12, 31), PUBLISHED_LEAD)

    # Act
    in_domain = {d for d in published if d in rule}
    mismatched = {d for d in in_domain if rule[d] != published[d]}
    unpublished = set(rule) - set(published)
    matched = in_domain - mismatched

    # Assert: a fifth mismatch, a new unpublished rule date or a lost row fails here.
    assert len(published) == 37 and len(matched) == 35
    assert mismatched | unpublished == set(KNOWN_EXCEPTIONS)
    assert mismatched == {date(2024, 7, 3)}
    assert (rule[date(2024, 7, 3)], published[date(2024, 7, 3)]) == (time(11, 45), time(11, 30))
    assert EQUITY[date(2024, 7, 3)].halt_ct == time(12, 15)
    assert rule[date(2024, 1, 1)] is None and rule[date(2025, 1, 9)] == time(8, 0)
    assert rule[date(2025, 7, 3)] == time(11, 45)
    assert EQUITY[date(2025, 1, 9)].name.startswith("National Day of Mourning")
    assert set(published) - set(rule) == PUBLISHED_BEYOND_THE_CALENDAR
    assert max(EQUITY) < min(PUBLISHED_BEYOND_THE_CALENDAR)


def test_the_published_exceptions_are_july_3_and_the_calendar_edges_only() -> None:
    july_3 = {d for d in KNOWN_EXCEPTIONS if (d.month, d.day) == (7, 3)}
    assert july_3 == {date(2024, 7, 3), date(2025, 7, 3)}
    # 2026-07-03 (Independence Day observed) IS reproduced: 12:00 - 15 = 11:45 published.
    assert S.TOPSTEP_HOLIDAYS[date(2026, 7, 3)].close_by_ct == time(11, 45)


# ------------------------------------------------ (ii) the derived rows ----
def test_derived_rows_equal_rule_h1_minus_the_unsettled_dates() -> None:
    # Arrange
    rule = _rule_h1(S.TOPSTEP_DERIVED_FIRST, S.TOPSTEP_DERIVED_LAST, DERIVED_LEAD)
    unsettled = {d for d, _reason in S.TOPSTEP_UNSETTLED_DATES}

    # Act
    expected = {d: v for d, v in rule.items() if d not in unsettled}

    # Assert
    assert _derived() == expected
    assert len(rule) == 51 and len(expected) == 48 and not unsettled & set(_derived())


def test_unsettled_dates_are_the_rules_july_3_and_non_ordinary_dates() -> None:
    # Arrange
    rule = _rule_h1(S.TOPSTEP_DERIVED_FIRST, S.TOPSTEP_DERIVED_LAST, DERIVED_LEAD)
    ordinary = _ordinary_names()

    # Act
    july_3 = {d for d in rule if (d.month, d.day) == (7, 3)}
    non_ordinary = {d for d in rule if _base_name(EQUITY[d].name) not in ordinary}

    # Assert
    assert [d for d, _ in S.TOPSTEP_UNSETTLED_DATES] == sorted(july_3 | non_ordinary)
    assert july_3 == {date(2019, 7, 3), date(2020, 7, 3), date(2023, 7, 3)}
    assert non_ordinary == set()
    assert all("July 3" in reason for _d, reason in S.TOPSTEP_UNSETTLED_DATES)
    assert "National Day of Mourning" not in ordinary  # the unscheduled closure is not ordinary


def test_the_lead_table_and_the_year_sets() -> None:
    lead, published, derived = (S.TOPSTEP_EARLY_CLOSE_LEAD, S.TOPSTEP_SCHEDULE_YEARS,
                                S.TOPSTEP_DERIVED_YEARS)
    assert lead == {**{y: LEAD_30 for y in range(2019, 2024)}, **V4_LEAD}
    assert published == frozenset({2024, 2025, 2026})
    assert derived == frozenset(range(2019, 2024))
    span = (S.TOPSTEP_DERIVED_FIRST, S.TOPSTEP_DERIVED_LAST)
    assert span == (date(2019, 5, 1), date(2023, 12, 31))


# --------------------------------------------------------- (iii) the span ----
def test_no_row_outside_the_derived_span_or_beyond_the_published_rows() -> None:
    derived = _derived()
    assert all(S.TOPSTEP_DERIVED_FIRST <= d <= S.TOPSTEP_DERIVED_LAST for d in derived)
    assert all(d.weekday() < 5 for d in derived)
    assert {d.year for d in derived} == set(S.TOPSTEP_DERIVED_YEARS)
    # From 2024 on the table is exactly the v4 table: the 37 published rows, nothing added.
    after = {d: r for d, r in S.TOPSTEP_HOLIDAYS.items() if d >= date(2024, 1, 1)}
    assert after == V4_TABLE
    assert set(S.TOPSTEP_HOLIDAYS) == set(derived) | set(V4_TABLE)


# ------------------------------------------------------------ (iv) day_rule ----
@pytest.mark.parametrize("group", GROUPS)
def test_day_rule_on_a_derived_early_close_date_per_group(group: str) -> None:
    # Arrange: MLK 2022 (equity halt 12:00 -> close-by 11:30) for the groups that trade it;
    # grains and livestock are CME-closed then, so the Friday after Thanksgiving 2022.
    day = date(2022, 11, 25) if group in ("grains", "livestock") else date(2022, 1, 17)
    root = ROOT_OF_GROUP[group]
    hol = S.default_holidays()[group].get(day)
    close_by = S.TOPSTEP_HOLIDAYS[day].close_by_ct
    assert S.TOPSTEP_HOLIDAYS[day].source == DERIVED_SOURCE and close_by is not None
    cands = [S.REGULAR_FLATTEN_CT[group], close_by]
    if hol is not None:
        assert hol.kind is HolidayKind.EARLY_HALT and hol.halt_ct is not None
        cands.append(_minus(hol.halt_ct, LEAD_15))

    # Act
    rule = S.day_rule(root, day)

    # Assert: F = min(regular F, group halt - 15, the derived close-by). As on a published date
    # (2025-11-28: grains 11:45), a row suppresses the year-lead candidate (group halt - 30).
    assert not rule.closed and rule.flatten_ct == min(cands)
    assert rule.flatten_ct == (time(11, 45) if day.month == 11 else time(11, 30))
    if hol is not None and _minus(hol.halt_ct, LEAD_30) >= close_by:
        assert rule.flatten_ct == min(*cands, _minus(hol.halt_ct, LEAD_30))


def test_the_friday_after_thanksgiving_matches_the_published_year_for_grains() -> None:
    # 2022-11-25 derived 11:45 and 2025-11-28 published 11:45: grains halt 12:05 in both, and
    # both give 11:45 (not 12:05 - 30 = 11:35), the same code path.
    for day in (date(2022, 11, 25), date(2025, 11, 28)):
        assert S.default_holidays()["grains"][day].halt_ct == time(12, 5)
        assert S.flatten_time_ct("ZC", day) == time(11, 45)
        assert S.flatten_time_ct("LE", day) == time(11, 45)


def test_derived_markets_closed_rows_close_every_group() -> None:
    for day in (date(2019, 12, 25), date(2021, 12, 24), date(2023, 1, 2)):
        assert S.TOPSTEP_HOLIDAYS[day].close_by_ct is None
        for root in ROOT_OF_GROUP.values():
            assert S.day_rule(root, day).closed


def test_the_audit_fx_dates_flatten_at_the_derived_close_by_except_the_unsettled_july_3() -> None:
    unsettled = {d for d, _ in S.TOPSTEP_UNSETTLED_DATES}
    for day in AUDIT_FX_DATES:
        rule = S.day_rule("6E", day)
        assert S.default_holidays()["fx"].get(day) is None  # FX's calendar lists none of them
        if day in unsettled:  # no row: D9.1 plus the lead on FX's own (empty) calendar entry
            assert _state(rule) == "15:08", day
        else:
            assert _state(rule) == "11:30", day
            assert rule.reasons == (f"Topstep close-by 11:30 ({DERIVED_SOURCE})",)
    assert sum(d in unsettled for d in AUDIT_FX_DATES) == 2


def test_an_unsettled_date_applies_the_year_lead_to_the_group_calendar() -> None:
    # 2020-07-03: no row; metals and energy halt 12:00 -> F = 12:00 - 30 = 11:30 (v4: 11:45).
    day = date(2020, 7, 3)
    assert day not in S.TOPSTEP_HOLIDAYS
    for root in ("GC", "CL", "6E", "NQ"):
        rule = S.day_rule(root, day)
        assert rule.flatten_ct == time(11, 30)
        assert any("Topstep 2020 rule: 30 min before the early close 12:00" in r
                   for r in rule.reasons)
    # 2019-07-03: no row, energy's calendar lists nothing -> the regular 15:08.
    assert S.flatten_time_ct("CL", date(2019, 7, 3)) == time(15, 8)
    assert S.flatten_time_ct("NQ", date(2019, 7, 3)) == time(11, 45)  # equity 12:15 - 30


def test_a_group_halt_the_equity_calendar_does_not_list_gets_the_derived_year_lead() -> None:
    wed = date(2021, 3, 10)  # no row; a synthetic energy halt
    cal = {g: {} for g in GROUPS}
    cal["energy"] = {wed: Holiday(wed, "synthetic", HolidayKind.EARLY_HALT, time(13, 30),
                                  "cme", "cme")}
    rule = S.day_rule("CL", wed, cal)
    assert rule.flatten_ct == time(13, 0)  # 13:30 - 30 (derived lead), below 13:30 - 15


# ------------------------------------------------ (v) nothing from 2024 on ----
def _weekdays(first: date, last: date) -> list[date]:
    out, day = [], first
    while day <= last:
        if day.weekday() < 5:
            out.append(day)
        day += timedelta(days=1)
    return out


def test_every_day_rule_from_2024_equals_the_v4_result(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    days = _weekdays(date(2024, 1, 1), date(2027, 12, 31))
    v5 = {(g, d): S.day_rule(r, d) for g, r in ROOT_OF_GROUP.items() for d in days}
    monkeypatch.setattr(S, "TOPSTEP_HOLIDAYS", V4_TABLE)
    monkeypatch.setattr(S, "TOPSTEP_EARLY_CLOSE_LEAD", V4_LEAD)

    # Act
    v4 = {(g, d): S.day_rule(r, d) for g, r in ROOT_OF_GROUP.items() for d in days}

    # Assert: every group, every weekday, closed flag, F and reasons.
    assert len(v4) == 8 * len(days) and v5 == v4


def test_v5_changes_only_2019_2023_holiday_dates(monkeypatch: pytest.MonkeyPatch) -> None:
    days = _weekdays(date(2019, 5, 1), date(2023, 12, 31))
    v5 = {(g, d): _state(S.day_rule(r, d)) for g, r in ROOT_OF_GROUP.items() for d in days}
    monkeypatch.setattr(S, "TOPSTEP_HOLIDAYS", V4_TABLE)
    monkeypatch.setattr(S, "TOPSTEP_EARLY_CLOSE_LEAD", V4_LEAD)
    v4 = {(g, d): _state(S.day_rule(r, d)) for g, r in ROOT_OF_GROUP.items() for d in days}
    changed = {k for k in v5 if v5[k] != v4[k]}
    changed_days = {d for _g, d in changed}
    # Only dates the equity calendar lists (a row, or the lead on an unsettled July 3), and a
    # group early halt the equity calendar does not list (the derived-year lead): 2020-07-02,
    # grains 12:05 and livestock 12:15 ("Day before Independence Day (observed)").
    assert changed_days - set(EQUITY) == {date(2020, 7, 2)}
    assert {k: (v4[k], v5[k]) for k in changed if k[1] == date(2020, 7, 2)} == {
        ("grains", date(2020, 7, 2)): ("11:50", "11:35"),
        ("livestock", date(2020, 7, 2)): ("12:00", "11:45")}
    assert len(changed) == 251 and len(changed_days) == 42
    for key in changed:  # v5 never flattens later than v4
        assert v5[key] == "closed" or (v4[key] != "closed" and v5[key] <= v4[key]), key
