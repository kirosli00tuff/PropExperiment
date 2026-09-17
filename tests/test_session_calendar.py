"""CME session calendar: ported MLCryptoEngine halt/weekend/DST tests plus holidays."""

from __future__ import annotations

from datetime import UTC, date, datetime, time

from data.cme_calendar import HOLIDAYS, HolidayKind
from data.intervals import contains, merge_windows
from data.session import (
    closed_windows_ns,
    closed_windows_range_ns,
    is_closed,
    open_ns,
    trade_date,
)

NS_PER_S = 1_000_000_000
NS_PER_HOUR = 3600 * NS_PER_S


def _ns(iso: str) -> int:
    return int(datetime.fromisoformat(iso).replace(tzinfo=UTC).timestamp()) * NS_PER_S


# ---- ported from MLCryptoEngine tests/test_cme_session.py (same expectations) ----
def test_weekday_has_exactly_one_hour_maintenance_halt() -> None:
    windows = closed_windows_ns("2026-07-30")  # Thursday, CDT: 21:00-22:00 UTC
    assert len(windows) == 1
    start, end = windows[0]
    assert end - start == NS_PER_HOUR
    assert datetime.fromtimestamp(start / 1e9, tz=UTC).hour == 21
    assert open_ns("2026-07-30") == 23 * NS_PER_HOUR


def test_friday_close_runs_into_the_weekend_and_saturday_is_shut() -> None:
    friday = closed_windows_ns("2026-07-31")
    start, end = friday[-1]
    assert datetime.fromtimestamp(start / 1e9, tz=UTC).hour == 21
    assert end == _ns("2026-08-01T00:00:00")
    assert open_ns("2026-07-31") == 21 * NS_PER_HOUR
    assert open_ns("2026-08-01") == 0


def test_sunday_reopens_at_17_00_central() -> None:
    assert open_ns("2026-08-02") == 2 * NS_PER_HOUR
    assert is_closed(_ns("2026-08-02T12:00:00"), "2026-08-02")
    assert not is_closed(_ns("2026-08-02T23:00:00"), "2026-08-02")


def test_halt_membership_is_half_open() -> None:
    date_ = "2026-07-30"
    assert is_closed(_ns("2026-07-30T21:00:00"), date_)
    assert is_closed(_ns("2026-07-30T21:59:59"), date_)
    assert not is_closed(_ns("2026-07-30T22:00:00"), date_)
    assert not is_closed(_ns("2026-07-30T20:59:59"), date_)


def test_dst_is_handled_rather_than_a_fixed_offset() -> None:
    winter = closed_windows_ns("2026-01-15")
    assert datetime.fromtimestamp(winter[0][0] / 1e9, tz=UTC).hour == 22
    assert open_ns("2026-01-15") == 23 * NS_PER_HOUR


# ---- holidays (the gap this port closes) ----
def test_christmas_2025_is_closed_from_the_1215_close_to_the_evening_reopen() -> None:
    # Wed Dec 24 12:15 CST = 18:15 UTC; Thu Dec 25 17:00 CST = 23:00 UTC.
    windows = closed_windows_range_ns(date(2025, 12, 24), date(2025, 12, 25))
    assert contains(windows, _ns("2025-12-24T18:15:00"))
    assert not contains(windows, _ns("2025-12-24T18:14:59"))
    assert contains(windows, _ns("2025-12-25T12:00:00"))
    assert contains(windows, _ns("2025-12-25T22:59:59"))
    assert not contains(windows, _ns("2025-12-25T23:00:00"))


def test_mlk_day_is_an_early_halt_not_a_closure() -> None:
    # Mon 2026-01-19: open until 12:00 CST (18:00 UTC), shut until 17:00 CST (23:00 UTC).
    windows = closed_windows_range_ns(date(2026, 1, 19), date(2026, 1, 19))
    assert not contains(windows, _ns("2026-01-19T15:00:00"))
    assert contains(windows, _ns("2026-01-19T18:00:00"))
    assert not contains(windows, _ns("2026-01-19T23:00:00"))


def test_good_friday_2025_full_closure_spans_thursday_evening_to_sunday() -> None:
    # Thu Apr 17 16:00 CDT (21:00 UTC) through Sun Apr 20 17:00 CDT (22:00 UTC).
    windows = closed_windows_range_ns(date(2025, 4, 17), date(2025, 4, 20))
    assert not contains(windows, _ns("2025-04-17T20:59:00"))
    for probe in ("2025-04-17T22:30:00", "2025-04-18T14:00:00", "2025-04-20T21:59:59"):
        assert contains(windows, _ns(probe))
    assert not contains(windows, _ns("2025-04-20T22:00:00"))


def test_friday_early_halt_runs_into_the_weekend() -> None:
    # Juneteenth Fri 2026-06-19: halt 12:00 CDT (17:00 UTC) -> Sun 17:00 CDT.
    windows = closed_windows_range_ns(date(2026, 6, 19), date(2026, 6, 21))
    assert not contains(windows, _ns("2026-06-19T16:59:00"))
    assert contains(windows, _ns("2026-06-20T12:00:00"))
    assert not contains(windows, _ns("2026-06-21T22:00:00"))


def test_calendar_is_not_the_nyse_calendar() -> None:
    # NYSE closes fully on these days; CME equity futures only halt early.
    for day in (date(2026, 1, 19), date(2026, 5, 25), date(2026, 9, 7)):
        assert HOLIDAYS[day].kind is HolidayKind.EARLY_HALT
    # Good Friday 2026: NYSE closed, CME held an abbreviated equity session.
    assert HOLIDAYS[date(2026, 4, 3)].kind is HolidayKind.EARLY_HALT


def test_every_early_halt_has_a_time_and_every_closure_has_none() -> None:
    for holiday in HOLIDAYS.values():
        assert (holiday.halt_ct is None) == (holiday.kind is HolidayKind.FULL_CLOSURE)
        if holiday.halt_ct is not None:
            assert holiday.halt_ct < time(16, 0)


def test_trade_date_skips_weekends_and_full_closures() -> None:
    # Wed Dec 24 2025 18:00 CST (Thu 00:00 UTC) is inside the closure; the next
    # session opening Thu 17:00 CST belongs to Fri Dec 26.
    assert trade_date(_ns("2025-12-25T23:30:00")) == date(2025, 12, 26)
    # Friday 17:30 CT -> next Monday.
    assert trade_date(_ns("2026-07-31T22:30:00")) == date(2026, 8, 3)
    # Tuesday 10:00 CT -> Tuesday.
    assert trade_date(_ns("2026-07-28T15:00:00")) == date(2026, 7, 28)


def test_merge_windows_unions_rather_than_sums() -> None:
    assert merge_windows([(0, 10), (5, 15), (15, 20), (30, 31)]) == [(0, 20), (30, 31)]


def test_july_4_2025_is_an_early_halt_as_the_bars_show() -> None:
    # Regression for a calendar error the bar validation caught: MES traded
    # Thu 2025-07-03 17:00 CDT -> Fri 11:59 CDT. Fri 12:00 CDT = 17:00 UTC.
    windows = closed_windows_range_ns(date(2025, 7, 3), date(2025, 7, 6))
    assert not contains(windows, _ns("2025-07-03T22:00:00"))  # Thu 17:00 CDT reopen
    assert not contains(windows, _ns("2025-07-04T16:59:00"))  # Fri 11:59 CDT
    assert contains(windows, _ns("2025-07-04T17:00:00"))  # Fri 12:00 CDT halt
    assert contains(windows, _ns("2025-07-03T17:15:00"))  # Thu 12:15 CDT early close
