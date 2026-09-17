"""CME Globex session windows for MES, including the holiday calendar.

Ported from MLCryptoEngine ``data/databento/session.py`` (read-only port,
2026-09-16), which encodes the daily 16:00-17:00 CT maintenance halt and the
Friday 16:00 CT -> Sunday 17:00 CT weekend close, with US/Central converted
through ``zoneinfo`` so DST never shifts the halt. That module had no
holiday calendar (a documented gap); this port adds one from
:mod:`data.cme_calendar`:

- ``FULL_CLOSURE`` on calendar day D: Globex does not reopen at 17:00 CT on
  D-1, and reopens at 17:00 CT on D. Closed ``[D-1 17:00, D 17:00)``.
- ``EARLY_HALT`` on D at T: trading stops at T instead of the 16:00 halt and
  resumes at the normal 17:00 CT reopen (or Sunday 17:00 if D is a Friday).

Every window is half-open ``[start, end)`` in UTC nanoseconds and unioned via
:func:`data.intervals.merge_windows` before use.
"""

from __future__ import annotations

from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from data.cme_calendar import HOLIDAYS, HolidayKind
from data.intervals import contains, merge_windows

CME_TZ = ZoneInfo("America/Chicago")
NS_PER_S = 1_000_000_000
NS_PER_DAY = 86_400 * NS_PER_S

# Daily maintenance halt, US/Central (verified against the ported calendar
# and, empirically, against the pulled MES bars — see reports/bar_validation.md).
HALT_START = time(16, 0)
HALT_END = time(17, 0)  # also the daily Globex reopen
FRIDAY, SATURDAY, SUNDAY = 4, 5, 6


def ct_ns(day: date, at: time) -> int:
    """UTC nanoseconds of a US/Central wall-clock time (DST-aware)."""
    return int(datetime.combine(day, at, tzinfo=CME_TZ).astimezone(UTC).timestamp()) * NS_PER_S


def early_halt_ct(day: date) -> time | None:
    """The CME early halt time on CT calendar day ``day``, if any."""
    holiday = HOLIDAYS.get(day)
    if holiday is not None and holiday.kind is HolidayKind.EARLY_HALT:
        return holiday.halt_ct
    return None


def is_full_closure(day: date) -> bool:
    holiday = HOLIDAYS.get(day)
    return holiday is not None and holiday.kind is HolidayKind.FULL_CLOSURE


def _day_windows(day: date) -> list[tuple[int, int]]:
    weekday = day.weekday()
    if weekday == SATURDAY:
        return []  # inside the Friday-to-Sunday close
    windows: list[tuple[int, int]] = []
    halt_start = early_halt_ct(day) or HALT_START
    if weekday == FRIDAY:
        windows.append((ct_ns(day, halt_start), ct_ns(day + timedelta(days=2), HALT_END)))
    else:
        windows.append((ct_ns(day, halt_start), ct_ns(day, HALT_END)))
    if is_full_closure(day):
        windows.append((ct_ns(day - timedelta(days=1), HALT_END), ct_ns(day, HALT_END)))
    return windows


def closed_windows_range_ns(start: date, end: date) -> list[tuple[int, int]]:
    """Merged closed windows covering CT days ``[start, end]`` (with margin)."""
    windows: list[tuple[int, int]] = []
    day = start - timedelta(days=3)
    while day <= end + timedelta(days=1):
        windows.extend(_day_windows(day))
        day += timedelta(days=1)
    return merge_windows(windows)


def closed_windows_ns(utc_date: str) -> list[tuple[int, int]]:
    """Closed windows clipped to one UTC day (MLCryptoEngine-compatible API)."""
    day = datetime.strptime(utc_date, "%Y-%m-%d").date()
    day_start = int(datetime.combine(day, time(0), tzinfo=UTC).timestamp()) * NS_PER_S
    day_end = day_start + NS_PER_DAY
    clipped = [
        (max(lo, day_start), min(hi, day_end))
        for lo, hi in closed_windows_range_ns(day - timedelta(days=1), day + timedelta(days=1))
        if min(hi, day_end) > max(lo, day_start)
    ]
    return merge_windows(clipped)


def open_ns(utc_date: str) -> int:
    """Nanoseconds of the UTC day the exchange was scheduled open."""
    return NS_PER_DAY - sum(end - start for start, end in closed_windows_ns(utc_date))


def is_closed(ts_ns: int, utc_date: str) -> bool:
    return contains(closed_windows_ns(utc_date), ts_ns)


def trade_date(ts_ns: int) -> date:
    """CME trade date of an instant: sessions reopening at 17:00 CT belong to
    the next business day that is not a weekend or full closure.

    Topstep treats each calendar day on its own on holidays (no CME blended
    trade dates — help.topstep.com holiday article, retrieved 2026-09-16), so
    an early-halt day remains its own trade date here.
    """
    local = datetime.fromtimestamp(ts_ns / NS_PER_S, tz=UTC).astimezone(CME_TZ)
    day = local.date()
    if local.time() >= HALT_END:
        day += timedelta(days=1)
    while day.weekday() in (SATURDAY, SUNDAY) or is_full_closure(day):
        day += timedelta(days=1)
    return day
