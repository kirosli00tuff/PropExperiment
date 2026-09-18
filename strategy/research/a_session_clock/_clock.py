"""Shared clock-only helpers for family A: session-clock seasonality (Stage D.1).

Every function here reads ONLY a bar's timestamp and its already-computed
``trade_date`` calendar label -- never price, volume, or any quantity derived
from them. That is what keeps every hypothesis file in this directory inside
the family's declared scope: "ONLY the clock: time-of-day, position within
the RTH/ETH session, day-of-week." No conditioning on price, range,
volatility, or calendar events lives here or in any file that imports this
module.

RTH convention used throughout this family: 09:30-16:00 US/Eastern, the
cash-equity convention the source papers themselves use (Boyarchenko, Larsen
& Whelan frame the European-open window in ET; Baltussen, Da, Lammers &
Martens frame "hedging demand into the close" against the 16:00 ET NYSE cash
close). This is CME's own core-trading-hours window for MES (08:30-15:15 CT)
shifted to ET is close but not identical (CME's own session runs a further
15 minutes past 16:00 ET); this family uses the cash-market 09:30-16:00 ET
window because that is what the mechanism in every cited paper actually
refers to, and states that choice once here rather than re-deriving it in
each hypothesis file.

Day-of-week comes from ``Bar.trade_date`` (the CME trade-date label already
computed by the Stage A.1 pipeline), not from the raw UTC or ET calendar
date of a timestamp: an overnight bar in the small hours of, say, a Tuesday
UTC/ET wall-clock date can belong to the Monday CME trade date (a session
opens at 17:00 CT the evening before). Using ``trade_date.weekday()``
sidesteps that mismatch and is exactly the "day-of-week" the family is
scoped to condition on.
"""

from __future__ import annotations

from datetime import datetime, time
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
RTH_OPEN_ET = time(9, 30)
RTH_CLOSE_ET = time(16, 0)

MONDAY = 0
TUESDAY = 1
WEDNESDAY = 2
THURSDAY = 3
FRIDAY = 4


def et_time(ts_utc: datetime) -> time:
    """The wall-clock time in US/Eastern of a tz-aware UTC timestamp."""
    return ts_utc.astimezone(ET).time()


def in_window_et(ts_utc: datetime, start: time, end: time) -> bool:
    """Half-open ``[start, end)`` in US/Eastern wall-clock time. ``start < end`` always
    holds for every window used in this family (none crosses midnight ET)."""
    t = et_time(ts_utc)
    return start <= t < end


def is_rth(ts_utc: datetime) -> bool:
    """Whether ``ts_utc`` falls in the 09:30-16:00 ET cash-market session window."""
    return in_window_et(ts_utc, RTH_OPEN_ET, RTH_CLOSE_ET)
