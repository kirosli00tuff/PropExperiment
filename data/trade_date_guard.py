"""Stage E.2b Task 4: the CME trade-date purchase guard (lead ruling L-9 carried to every buy).

E.2a found that the step 1 purchase guard was set by timestamp only: MBT's files end at
2026-06-21 00:00 UTC, yet CME books MBT's trading from Thursday 2026-06-18 16:02 CT to Saturday
2026-06-20 (Juneteenth and the 24/7 weekend) to trade date 2026-06-22, holdout-1's first trade
date (reports/E.2a_RETURN.md section 2). This module decides, from the product's GROUP calendar
(data.group_session), which CME trade dates the minutes of a vendor request [start, end) are
booked to, so every purchase path can refuse by trade date before any vendor call.

The booking model, stated once:
- A minute is booked to trade date D when it lies inside one of D's open intervals
  (``data.group_session.open_intervals``: sessions, early halts, late opens, crypto's
  booked-forward days and weekend assignment all included).
- The first minute after a session ends (the close minute) is booked to that session's trade
  date too (lead ruling L-3: a print stamped in the close minute belongs to the session it closes).
- Any other minute of a scheduled closure carries no bar and is booked to nothing.
- Booking is monotone in time (a later minute never books to an earlier trade date). So minutes
  after the last open interval the calendar can show could belong to any later trade date,
  holdout-1 included: such a request is refused by name (``CalendarCoverageRefused``), never
  assumed clean. Minutes before the first open interval it can show could only belong to that
  interval's trade date or an earlier one: they are refused the same way only when that trade
  date is on or after holdout-2's first date (before it, no earlier date is a holdout date).
  This is what lets the step 2 plan's first chunk (2019-05-01 00:00 UTC, before a day-only
  livestock session of the calendar's first covered date) pass.

The refusals (``refuse_holdout_bookings``): any minute booked to a holdout-1 trade date
(>= data.splits.HOLDOUT_START, 2026-06-22) is refused on every path; any minute booked to a
holdout-2 trade date (data.research_bars HOLDOUT2_START..HOLDOUT2_END, 2024-04-01..2025-03-31)
is refused unless the request is fetched through a sealing download (``sealing=True``), which
seals the chunk in the download call. Embargo trade dates (March 2024) are not a purchase
refusal: the February 2024 chunk books its last evening to 2024-03-01, and the step 2 bar store
drops those rows by trade date (data.step2_store).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from functools import lru_cache

import numpy as np

from data.group_session import (
    NS_PER_MIN,
    GroupCalendar,
    OpenIntervals,
    group_of,
    load_group_calendar,
    open_intervals,
)
from data.research_bars import HOLDOUT2_END, HOLDOUT2_START
from data.splits import HOLDOUT_START

HOLDOUT1_FIRST_TRADE_DATE = HOLDOUT_START  # 2026-06-22
HOLDOUT2_FIRST_TRADE_DATE = HOLDOUT2_START  # 2024-04-01
HOLDOUT2_LAST_TRADE_DATE = HOLDOUT2_END  # 2025-03-31
MARGIN_DAYS = 7  # open intervals are built this many days either side of the request
NS_PER_S = 1_000_000_000


class TradeDateRefused(RuntimeError):
    """A request's minutes are booked to a trade date this path may not buy, or cannot be
    booked at all. Raised before any vendor call."""


class HoldoutTradeDateRefused(TradeDateRefused):
    """A minute of the request is booked to a holdout-1 (or, unsealed, a holdout-2) trade date."""


class CalendarCoverageRefused(TradeDateRefused):
    """Part of the request lies where the group calendar shows no session: its minutes cannot
    be booked to a trade date, so the request is not assumed clean."""


@dataclass(frozen=True, slots=True)
class Booking:
    """The trade dates a request's minutes are booked to, and the first booked instant of each."""

    root: str
    group: str
    start: str
    end: str
    trade_dates: tuple[date, ...]
    first_minute_ns: tuple[int, ...]  # aligned with trade_dates


def _to_ns(stamp: str) -> int:
    """A request bound (``YYYY-MM-DD`` = 00:00 UTC, or an ISO timestamp with Z) in UTC ns."""
    if "T" not in stamp:
        moment = datetime.combine(date.fromisoformat(stamp), datetime.min.time(), tzinfo=UTC)
    else:
        moment = datetime.fromisoformat(stamp.replace("Z", "+00:00")).astimezone(UTC)
    return int(moment.timestamp()) * NS_PER_S


def _iso(ns: int) -> str:
    return datetime.fromtimestamp(ns / NS_PER_S, UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


@lru_cache(maxsize=16)
def calendar_of_group(group: str) -> GroupCalendar:
    return load_group_calendar(group)


@lru_cache(maxsize=4096)
def _intervals(group: str, first: date, last: date) -> OpenIntervals:
    return open_intervals(calendar_of_group(group), first, last)


def booking(root: str, start: str, end: str) -> Booking:
    """The trade dates the minutes of [start, end) are booked to by ``root``'s group calendar.
    Raises CalendarCoverageRefused when the calendar cannot book every minute."""
    group = group_of(root)
    lo, hi = _to_ns(start), _to_ns(end)
    if not lo < hi:
        raise TradeDateRefused(f"{root} {start}..{end}: empty or inverted request")
    first = datetime.fromtimestamp(lo / NS_PER_S, UTC).date() - timedelta(days=MARGIN_DAYS)
    last = datetime.fromtimestamp(hi / NS_PER_S, UTC).date() + timedelta(days=MARGIN_DAYS)
    opened = _intervals(group, first, last)
    unknown_before = len(opened) > 0 and int(opened.starts[0]) > lo \
        and opened.days[0] >= HOLDOUT2_FIRST_TRADE_DATE
    if len(opened) == 0 or unknown_before or int(opened.ends.max()) < hi:
        known = ("none" if len(opened) == 0 else
                 f"{_iso(int(opened.starts[0]))}..{_iso(int(opened.ends.max()))}")
        raise CalendarCoverageRefused(
            f"{root} {start}..{end}: the {group} calendar (coverage "
            f"{calendar_of_group(group).coverage[0]}..{calendar_of_group(group).coverage[1]}) "
            f"shows sessions only over {known} near this request, so not every minute of it "
            "can be booked to a trade date; refused, never assumed clean")
    starts, ends = opened.starts.astype(np.int64), opened.ends.astype(np.int64)
    inside = (starts < hi) & (ends > lo)
    close_minute = (ends < hi) & (ends + NS_PER_MIN > lo)  # L-3: booked to the closed session
    first_ns: dict[date, int] = {}
    for idx in np.flatnonzero(inside | close_minute).tolist():
        day = opened.days[idx]
        at = max(int(starts[idx]), lo) if inside[idx] else max(int(ends[idx]), lo)
        first_ns[day] = min(at, first_ns.get(day, at))
    days = tuple(sorted(first_ns))
    return Booking(root, group, start, end, days, tuple(first_ns[d] for d in days))


def is_holdout1(day: date) -> bool:
    return day >= HOLDOUT1_FIRST_TRADE_DATE


def is_holdout2(day: date) -> bool:
    return HOLDOUT2_FIRST_TRADE_DATE <= day <= HOLDOUT2_LAST_TRADE_DATE


def refuse_holdout_bookings(root: str, start: str, end: str, *, sealing: bool = False
                            ) -> Booking:
    """Refuse [start, end) for ``root`` if any minute is booked to a holdout-1 trade date, or,
    unless ``sealing`` (the chunk is sealed in its download call), to a holdout-2 trade date.
    Returns the booking when the request is admissible."""
    got = booking(root, start, end)
    pairs = list(zip(got.trade_dates, got.first_minute_ns, strict=True))
    h1 = [(d, ns) for d, ns in pairs if is_holdout1(d)]
    if h1:
        day, ns = h1[0]
        raise HoldoutTradeDateRefused(
            f"{root} {start}..{end}: minutes from {_iso(ns)} are booked by the {got.group} "
            f"calendar to trade date {day}, a holdout-1 trade date (>= "
            f"{HOLDOUT1_FIRST_TRADE_DATE}); refused on every purchase path (ruling L-9)")
    h2 = [(d, ns) for d, ns in pairs if is_holdout2(d)]
    if h2 and not sealing:
        day, ns = h2[0]
        raise HoldoutTradeDateRefused(
            f"{root} {start}..{end}: minutes from {_iso(ns)} are booked by the {got.group} "
            f"calendar to trade date {day}, a holdout-2 trade date ({HOLDOUT2_FIRST_TRADE_DATE}"
            f"..{HOLDOUT2_LAST_TRADE_DATE}); only the sealing download may fetch them")
    return got
