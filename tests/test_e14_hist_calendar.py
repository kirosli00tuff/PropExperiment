"""Harness v10 (Stage E.14): data.hist_calendar, the 2010-2019 group calendar loader.

Synthetic fixture JSONs only (tests/fixtures/e14_hist/); malformed variants are written to
tmp_path. No price is read anywhere.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date, time
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from data.cme_calendar import CalendarCoverageError, HolidayKind
from data.group_session import (
    GroupCalendar,
    assign_trade_dates,
    open_intervals,
    session_intervals,
)
from data.hist_calendar import (
    HIST_COVERAGE,
    HistCalendarError,
    HistGroupCalendar,
    load_hist_group_calendar,
)
from data.session import ct_ns
from tests._e14_fixtures import FIXTURE_DIR, fixture_payload, write_calendar


def load(tmp_path: Path, payload: dict[str, Any], group: str = "equity") -> HistGroupCalendar:
    write_calendar(tmp_path, payload)
    return load_hist_group_calendar(group, base=tmp_path)


def refused(tmp_path: Path, payload: dict[str, Any], match: str) -> None:
    with pytest.raises(HistCalendarError, match=match):
        load(tmp_path, payload)


# ------------------------------------------------------------------ the fixture ----
def test_the_fixture_loads_as_a_group_calendar_with_its_entries_and_sha() -> None:
    # Act
    cal = load_hist_group_calendar("equity", base=FIXTURE_DIR)

    # Assert
    assert isinstance(cal, GroupCalendar) and cal.group == "equity"
    assert cal.coverage == HIST_COVERAGE == (date(2010, 6, 1), date(2019, 5, 31))
    assert cal.is_full_closure(date(2012, 10, 29)) and not cal.is_trade_date(date(2012, 10, 29))
    assert cal.early_halt_ct(date(2011, 11, 25)) == time(12, 15)
    assert cal.holidays[date(2011, 5, 30)].kind is HolidayKind.EARLY_HALT
    assert cal.scheduled_late_opens == {date(2018, 12, 5): time(9, 30)}
    assert cal.products == ("ES", "NQ")
    raw = (FIXTURE_DIR / "equity.json").read_bytes()
    assert cal.file_sha256 == hashlib.sha256(raw).hexdigest()
    assert cal.record()["sha256"] == cal.file_sha256
    assert set(cal.module_sha256().values()) >= {cal.file_sha256}


def test_unsourced_dates_are_the_listed_and_the_unverified_entries() -> None:
    # Act
    cal = load_hist_group_calendar("equity", base=FIXTURE_DIR)

    # Assert
    assert cal.unsourced == frozenset({date(2015, 6, 15), date(2016, 3, 25)})
    assert cal.unsourced_reasons[date(2015, 6, 15)] == ("listed",)
    assert cal.unsourced_reasons[date(2016, 3, 25)] == ("entry_unverified",)
    assert cal.counts["unsourced"] == 2 and cal.counts["unsourced_trade_dates"] == 1


def test_a_year_without_a_complete_sourced_exception_list_makes_its_normal_days_unsourced(
        tmp_path: Path) -> None:
    # Arrange: 2013 graded unverified, 2014's row missing; 2014-04-18 gets a sourced entry
    payload = fixture_payload("equity")
    payload["year_coverage"] = [r for r in payload["year_coverage"] if r["year"] != 2014]
    for row in payload["year_coverage"]:
        if row["year"] == 2013:
            row["evidence"] = "unverified"
    payload["entries"].append({"day": "2014-04-18", "name": "Good Friday", "kind": "full_closure",
                               "halt_ct": None, "evidence": "cme", "time_evidence": "n/a",
                               "source": "s"})

    # Act
    cal = load(tmp_path, payload)

    # Assert
    weekdays_2013 = [d for d in cal.unsourced if d.year == 2013]
    assert len(weekdays_2013) == 261 and cal.unsourced_reasons[date(2013, 3, 5)] == (
        "year_not_covered",)
    assert date(2014, 4, 18) not in cal.unsourced and date(2014, 4, 17) in cal.unsourced
    assert date(2012, 3, 5) not in cal.unsourced
    assert cal.counts["unsourced_by_reason"]["year_not_covered"] == len(
        [d for d in cal.unsourced if d.year in (2013, 2014)])


def test_a_session_spec_graded_unverified_makes_its_weekdays_unsourced(tmp_path: Path) -> None:
    # Arrange: split the session in two; the second half is unverified
    payload = fixture_payload("equity")
    first = payload["sessions"][0]
    second = {**first, "valid_from": "2018-01-01", "valid_to": None, "evidence": "unverified"}
    payload["sessions"] = [{**first, "valid_to": "2017-12-31"}, second]

    # Act
    cal = load(tmp_path, payload)

    # Assert
    assert date(2018, 1, 2) in cal.unsourced and date(2017, 12, 29) not in cal.unsourced
    assert "session_unverified" in cal.unsourced_reasons[date(2019, 5, 31)]


def test_weekends_are_never_trade_dates_or_unsourced() -> None:
    cal = load_hist_group_calendar("equity", base=FIXTURE_DIR)
    assert not cal.is_trade_date(date(2015, 6, 13)) and date(2015, 6, 13) not in cal.unsourced


# ------------------------------------------------------------------ sessions ----
def test_a_late_open_follows_the_grains_convention_and_an_early_halt_cuts_the_day() -> None:
    # Arrange
    cal = load_hist_group_calendar("equity", base=FIXTURE_DIR)

    # Act
    late = session_intervals(cal, date(2018, 12, 5))
    halt = session_intervals(cal, date(2011, 11, 25))

    # Assert: nothing before 09:30 CT on the late-open day; nothing at or after 12:15 CT
    assert late[0][0] == ct_ns(date(2018, 12, 5), time(9, 30))
    assert halt[-1][1] == ct_ns(date(2011, 11, 25), time(12, 15))


def test_bars_book_to_hist_trade_dates_with_the_close_minute_rule() -> None:
    # Arrange
    cal = load_hist_group_calendar("equity", base=FIXTURE_DIR)
    opened = open_intervals(cal, date(2012, 10, 25), date(2012, 11, 2))
    ts = np.array([ct_ns(date(2012, 10, 26), time(15, 0)),  # Friday day session
                   ct_ns(date(2012, 10, 28), time(18, 0)),  # Sunday evening of the closure
                   ct_ns(date(2012, 10, 30), time(10, 0))], dtype=np.int64)

    # Act
    days = assign_trade_dates(opened, ts, close_minute_to_previous=True).as_dates()

    # Assert: the closed Monday's evening is a closure bar booked to the next trade date
    assert days == [date(2012, 10, 26), date(2012, 10, 30), date(2012, 10, 30)]


def test_assert_coverage_refuses_any_date_outside_the_coverage() -> None:
    cal = load_hist_group_calendar("equity", base=FIXTURE_DIR)
    cal.assert_coverage({date(2010, 6, 1), date(2019, 5, 31)})
    for outside in (date(2010, 5, 31), date(2019, 6, 3)):
        with pytest.raises(CalendarCoverageError):
            cal.assert_coverage({outside})
    assert not cal.covers(date(2019, 6, 3)) and cal.covers(date(2019, 5, 31))


# ------------------------------------------------------------------ refusals ----
def test_a_missing_file_an_unknown_group_and_a_wrong_expected_sha_are_refused(
        tmp_path: Path) -> None:
    with pytest.raises(HistCalendarError, match="does not exist"):
        load_hist_group_calendar("rates", base=tmp_path)
    with pytest.raises(HistCalendarError, match="unknown hist calendar group"):
        load_hist_group_calendar("crypto", base=FIXTURE_DIR)  # v12: livestock is a hist group
    with pytest.raises(HistCalendarError, match="expected"):
        load_hist_group_calendar("equity", base=FIXTURE_DIR, expected_sha256="0" * 64)


def test_malformed_json_and_a_wrong_schema_or_group_are_refused(tmp_path: Path) -> None:
    (tmp_path / "equity.json").write_text("{not json", encoding="utf-8")
    with pytest.raises(HistCalendarError, match="not JSON"):
        load_hist_group_calendar("equity", base=tmp_path)
    refused(tmp_path, {**fixture_payload("equity"), "schema": "e14_hist_calendar/0"}, "schema")
    (tmp_path / "equity.json").write_text(json.dumps({**fixture_payload("equity"),
                                                      "group": "rates"}), encoding="utf-8")
    with pytest.raises(HistCalendarError, match="group is 'rates'"):
        load_hist_group_calendar("equity", base=tmp_path)
    refused(tmp_path, {**fixture_payload("equity"), "products": ["NG"]}, "products")
    refused(tmp_path, {**fixture_payload("equity"),
                       "coverage": {"first": "2010-06-01", "last": "2019-06-30"}}, "coverage")


@pytest.mark.parametrize("change,match", [
    ({"day": "2009-12-24"}, "outside the coverage"),
    ({"day": "2019-06-03"}, "outside the coverage"),
    ({"day": "2012-10-27"}, "weekend"),
    ({"evidence": "probable"}, "unknown grade"),
    ({"time_evidence": "guess"}, "unknown grade"),
    ({"kind": "half_day"}, "unknown kind"),
    ({"halt_ct": "12:00"}, "full closure"),
    ({"time_evidence": "cme"}, "full closure"),
    ({"day": "2012/10/29"}, "YYYY-MM-DD"),
])
def test_a_bad_entry_is_refused(tmp_path: Path, change: dict[str, Any], match: str) -> None:
    # Arrange: change the Hurricane Sandy full closure
    payload = fixture_payload("equity")
    entry = next(e for e in payload["entries"] if e["day"] == "2012-10-29")
    entry.update(change)

    # Act / Assert
    refused(tmp_path, payload, match)


def test_halt_and_open_times_must_match_the_entry_kind(tmp_path: Path) -> None:
    payload = fixture_payload("equity")
    halt = next(e for e in payload["entries"] if e["kind"] == "early_halt")
    halt["halt_ct"] = "25:00"
    refused(tmp_path, payload, "valid time")
    payload = fixture_payload("equity")
    next(e for e in payload["entries"] if e["kind"] == "early_halt")["time_evidence"] = "n/a"
    refused(tmp_path, payload, "time grade")
    payload = fixture_payload("equity")
    next(e for e in payload["entries"] if e["kind"] == "late_open")["open_ct"] = None
    refused(tmp_path, payload, "HH:MM")


def test_a_repeated_entry_or_unsourced_day_is_refused(tmp_path: Path) -> None:
    payload = fixture_payload("equity")
    payload["entries"].append(dict(payload["entries"][0]))
    refused(tmp_path, payload, "repeat")
    payload = fixture_payload("equity")
    payload["unsourced"].append(dict(payload["unsourced"][0]))
    refused(tmp_path, payload, "listed twice")
    payload = fixture_payload("equity")
    payload["unsourced"].append({"day": "2019-06-04", "reason": "x"})
    refused(tmp_path, payload, "outside the coverage")


def test_sessions_must_be_contiguous_and_cover_the_coverage(tmp_path: Path) -> None:
    payload = fixture_payload("equity")
    first = payload["sessions"][0]
    payload["sessions"] = [{**first, "valid_to": "2014-12-31"},
                           {**first, "valid_from": "2015-01-05"}]
    refused(tmp_path, payload, "gap")
    payload["sessions"] = [{**first, "valid_to": "2014-12-31"},
                           {**first, "valid_from": "2014-12-31"}]
    refused(tmp_path, payload, "overlap")
    payload["sessions"] = [{**first, "valid_from": "2010-06-02"}]
    refused(tmp_path, payload, "after the coverage")
    payload["sessions"] = [{**first, "valid_to": "2019-05-30"}]
    refused(tmp_path, payload, "before the coverage")
    payload["sessions"] = [{**first, "evidence": "maybe"}]
    refused(tmp_path, payload, "unknown grade")
    payload["sessions"] = [{**first, "segments": [{"start_offset_days": 0, "start_ct": "16:00",
                                                   "end_offset_days": 0, "end_ct": "15:00"}]}]
    refused(tmp_path, payload, "segments")


def test_year_coverage_rows_are_checked(tmp_path: Path) -> None:
    payload = fixture_payload("equity")
    payload["year_coverage"][0]["evidence"] = "official-ish"
    refused(tmp_path, payload, "unknown grade")
    payload = fixture_payload("equity")
    payload["year_coverage"].append(dict(payload["year_coverage"][0]))
    refused(tmp_path, payload, "listed twice")
    payload = fixture_payload("equity")
    payload["year_coverage"][0]["complete_exception_list"] = "yes"
    refused(tmp_path, payload, "true or false")


def test_a_friday_to_monday_session_handover_is_contiguous(tmp_path: Path) -> None:
    # Arrange: CME hour changes take effect on a Monday trade date; the earlier row ends Friday
    payload = fixture_payload("equity")
    first = payload["sessions"][0]
    payload["sessions"] = [{**first, "valid_to": "2012-11-16"},
                           {**first, "valid_from": "2012-11-19"}]
    # Act
    cal = load(tmp_path, payload)
    # Assert: the weekend is closed onto the earlier row; no weekday changes its spec
    assert [s.valid_to for s in cal.sessions][0] == date(2012, 11, 18)
    assert cal.spec_for(date(2012, 11, 16)) is cal.sessions[0]
    assert cal.spec_for(date(2012, 11, 19)) is cal.sessions[1]


def test_one_day_may_hold_an_early_halt_and_a_late_open_but_not_a_closure_and_a_late_open(
        tmp_path: Path) -> None:
    # Arrange: grains' day after Thanksgiving opens late and halts early (grains.py holds both)
    payload = fixture_payload("equity")
    halt = next(e for e in payload["entries"] if e["kind"] == "early_halt")
    late = next(e for e in payload["entries"] if e["kind"] == "late_open")
    payload["entries"].append({**late, "day": halt["day"]})
    # Act
    cal = load(tmp_path, payload)
    # Assert: the day is in both maps
    day = date.fromisoformat(halt["day"])
    assert cal.holidays[day].halt_ct is not None
    assert day in cal.scheduled_late_opens
    # A late open beside a full closure is refused
    payload = fixture_payload("equity")
    closure = next(e for e in payload["entries"] if e["kind"] == "full_closure")
    payload["entries"].append({**late, "day": closure["day"]})
    refused(tmp_path, payload, "repeat")
