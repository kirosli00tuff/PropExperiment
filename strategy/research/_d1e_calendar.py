"""Stage D.1e Task 3: CME trade-date calendar and the supplied-days estimator.

Split out of ``strategy/research/_d1e_power.py`` unchanged (the repo caps a file
at 800 lines). No behaviour differs from the version that lived there.

The estimator counts weekdays in a range, removes CME equity-futures full
closures, removes a pro-rata allowance for roll blackout dates, and removes the
vendor-degraded dates listed in ``reports/stage_d1e_quotes.md``. It reads no
exchange calendar file, so every figure carries the tolerance below.
"""

from __future__ import annotations

import re
from datetime import date, timedelta
from typing import Any

from dateutil.easter import easter

# Supplied-days estimate (Task 3 descriptive input).
SUPPLY_STARTS = (
    "2019-05-06",
    "2019-07-01",
    "2020-01-02",
    "2021-01-04",
    "2022-01-03",
    "2023-01-03",
)
SUPPLY_END = "2024-02-29"
HOLDOUT2_START = "2024-04-01"
HOLDOUT2_END = "2025-03-31"
BLACKOUT_DATES_PER_ROLL = 3
ROLLS_PER_YEAR = 4
DAYS_PER_YEAR = 365.25
SUPPLY_TOLERANCE = "+/-3%"


def _nth_weekday(year: int, month: int, weekday: int, nth: int) -> date:
    first = date(year, month, 1)
    offset = (weekday - first.weekday()) % 7
    return first + timedelta(days=offset + 7 * (nth - 1))


def _last_weekday(year: int, month: int, weekday: int) -> date:
    nxt = date(year + (month == 12), (month % 12) + 1, 1)
    last = nxt - timedelta(days=1)
    return last - timedelta(days=(last.weekday() - weekday) % 7)


def _observed(day: date) -> date | None:
    """Sunday holidays are observed on Monday; Saturday ones close no weekday."""
    if day.weekday() == 6:
        return day + timedelta(days=1)
    if day.weekday() == 5:
        return None
    return day


def cme_full_closures(year: int) -> set[date]:
    """CME equity-futures full-closure holidays for one calendar year."""
    fixed = [date(year, 1, 1), date(year, 7, 4), date(year, 12, 25)]
    if year >= 2022:
        fixed.append(date(year, 6, 19))  # Juneteenth, a CME holiday from 2022
    days = {d for d in (_observed(f) for f in fixed) if d is not None}
    days.add(_nth_weekday(year, 1, 0, 3))  # Martin Luther King Day
    days.add(_nth_weekday(year, 2, 0, 3))  # Presidents' Day
    days.add(easter(year) - timedelta(days=2))  # Good Friday
    days.add(_last_weekday(year, 5, 0))  # Memorial Day
    days.add(_nth_weekday(year, 9, 0, 1))  # Labor Day
    days.add(_nth_weekday(year, 11, 3, 4))  # Thanksgiving
    return days


def weekday_open_dates(start: date, end: date) -> list[date]:
    """Weekdays in [start, end] that are not a CME full closure."""
    closures: set[date] = set()
    for year in range(start.year, end.year + 1):
        closures |= cme_full_closures(year)
    out: list[date] = []
    day = start
    while day <= end:
        if day.weekday() < 5 and day not in closures:
            out.append(day)
        day += timedelta(days=1)
    return out


def roll_blackout_days(start: date, end: date) -> int:
    """3 blackout dates per quarterly roll = 12 a year, pro rata by months."""
    years = ((end - start).days + 1) / DAYS_PER_YEAR
    return int(round(BLACKOUT_DATES_PER_ROLL * ROLLS_PER_YEAR * years))


def supplied_days(start: date, end: date, degraded: list[date]) -> dict[str, Any]:
    open_dates = weekday_open_dates(start, end)
    blackout = roll_blackout_days(start, end)
    degraded_in_range = [d for d in degraded if start <= d <= end]
    total = len(open_dates) - blackout - len(degraded_in_range)
    return {
        "confirmation_days": int(total),
        "method": (
            f"weekdays {start.isoformat()}..{end.isoformat()} minus CME full closures "
            f"= {len(open_dates)}; minus {blackout} roll-blackout dates "
            f"({BLACKOUT_DATES_PER_ROLL} per quarterly roll, pro rata by months); "
            f"minus {len(degraded_in_range)} vendor-degraded dates; "
            f"estimate {SUPPLY_TOLERANCE}"
        ),
        "weekday_open_dates": len(open_dates),
        "roll_blackout_days": blackout,
        "vendor_degraded_days": len(degraded_in_range),
    }


def parse_degraded_dates(quotes_md: str) -> list[date]:
    """The vendor-degraded dates listed in stage_d1e_quotes.md section 1."""
    rows = re.findall(r"^\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*degraded\s*\|", quotes_md, re.MULTILINE)
    return sorted({date.fromisoformat(d) for d in rows})
