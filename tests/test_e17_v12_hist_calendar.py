"""Harness v12 (Stage E.17): the livestock hist calendar through data.hist_calendar.

data/calendars/hist2010/livestock.json must be a byte copy of E.16's frozen
reports/stage_e16_calendars/hist2010_livestock.json (sha256 from reports/stage_e16_freeze.json),
and data.hist_calendar's loader must read it exactly as base_rules.calendars parses the frozen
file: the same trade dates, early halts, late opens, sessions and unsourced dates.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date, timedelta

import pytest

from base_rules import calendars as BC
from base_rules import constants as K
from data import hist_calendar as hc
from data.config import REPO_ROOT

FROZEN = REPO_ROOT / "reports" / "stage_e16_calendars" / "hist2010_livestock.json"
COPY = REPO_ROOT / "data" / "calendars" / "hist2010" / "livestock.json"
FREEZE = REPO_ROOT / "reports" / "stage_e16_freeze.json"


def frozen_sha() -> str:
    files = json.loads(FREEZE.read_text(encoding="utf-8"))["files"]
    (row,) = [f for f in files if f["path"] == FROZEN.relative_to(REPO_ROOT).as_posix()]
    return row["sha256"]


@pytest.fixture(scope="module")
def both() -> tuple[hc.HistGroupCalendar, hc.HistGroupCalendar]:
    return (hc.load_hist_group_calendar("livestock", expected_sha256=frozen_sha()),
            BC.load_hist("livestock", expected_sha256=frozen_sha()))


def days() -> list[date]:
    first, last = hc.HIST_COVERAGE
    return [first + timedelta(days=n) for n in range((last - first).days + 1)]


def test_the_copy_is_byte_identical_to_the_frozen_file_and_its_recorded_sha256() -> None:
    sha = frozen_sha()
    assert sha == "802a4dd98a71776af58748c43c2a70772a966a2e37dd08e32fef1ebfe023ba5d"
    assert COPY.read_bytes() == FROZEN.read_bytes()
    assert hashlib.sha256(COPY.read_bytes()).hexdigest() == sha
    assert K.repo_path(K.LIVESTOCK_HIST_PATH) == FROZEN  # base_rules reads the frozen original


def test_livestock_is_a_hist_group_and_the_six_v10_groups_are_unchanged() -> None:
    assert hc.HIST_GROUPS == ("equity", "rates", "fx", "energy", "metals", "grains", "livestock")
    assert hc.HIST_GROUPS[:6] == K.HIST_GROUPS_FROZEN
    assert hc.hist_calendar_path("livestock") == COPY


def test_the_loader_reads_it_unchanged(
        both: tuple[hc.HistGroupCalendar, hc.HistGroupCalendar]) -> None:
    mine, theirs = both
    assert mine.group == "livestock" and mine.products == ("HE", "LE")
    assert mine.file_sha256 == theirs.file_sha256 == frozen_sha()
    assert mine.file_path == "data/calendars/hist2010/livestock.json"
    assert mine.counts == theirs.counts
    with pytest.raises(hc.HistCalendarError, match="expected"):
        hc.load_hist_group_calendar("livestock", expected_sha256="0" * 64)


def test_trade_dates_early_halts_and_unsourced_dates_equal_base_rules_parse(
        both: tuple[hc.HistGroupCalendar, hc.HistGroupCalendar]) -> None:
    # Arrange
    mine, theirs = both
    every = days()

    # Act / Assert
    assert [d for d in every if mine.is_trade_date(d)] == [d for d in every
                                                           if theirs.is_trade_date(d)]
    assert {d: mine.early_halt_ct(d) for d in every} == {d: theirs.early_halt_ct(d)
                                                         for d in every}
    assert any(mine.early_halt_ct(d) is not None for d in every)
    assert mine.unsourced == theirs.unsourced and len(mine.unsourced) == 25
    assert mine.unsourced_reasons == theirs.unsourced_reasons
    assert mine.holidays == theirs.holidays
    assert mine.scheduled_late_opens == theirs.scheduled_late_opens
    assert mine.sessions == theirs.sessions


def test_base_rules_group_calendars_built_on_either_file_agree(
        both: tuple[hc.HistGroupCalendar, hc.HistGroupCalendar]) -> None:
    mine, theirs = both
    a = BC.GroupCalendars("livestock", mine, theirs)  # the frozen era is not compared here
    b = BC.GroupCalendars("livestock", theirs, theirs)
    probe = [d for d in days() if d < K.FROZEN_CAL_FIRST]
    assert [a.is_trade_date(d) for d in probe] == [b.is_trade_date(d) for d in probe]
    assert [a.unsourced(d) for d in probe] == [b.unsourced(d) for d in probe]
    assert [a.early_halt(d) for d in probe] == [b.early_halt(d) for d in probe]
