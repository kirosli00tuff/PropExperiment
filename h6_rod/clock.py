"""H6's clock (prereg section 3; CP1's conventions, strategy/members/k1/cp1.py and
strategy/members/k1/_port_common.py, copied in structure, never imported).

- A bar is named by its CT open minute and closes one minute later. "The bar at hh:mm" of trade
  date d is the bar opening at hh:mm on CT calendar date d (E.3-L-03): the equity calendar's trade
  date d runs [d-1 17:00, d 16:00) CT, so the bars at C-31 and C-1 of d lie on CT date d.
- C(d): the frozen equity group calendar's early-halt time on a shortened day, else the frozen
  day-session close (screening.stage_e_frozen day_session_ct, CP1's source, which must equal
  15:00 CT, constants.NORMAL_CLOSE_CT).
- The signal bar of d opens at C(d)-31 (it ends at C-30; the entry decision is at its close); the
  prior bar of d opens at C(p)-1 on the previous equity trade date p; the exit is due on the first
  present bar of d opening at or after C(d)-2.
"""

from __future__ import annotations

import functools
from datetime import UTC, date, datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from h6_rod import constants as K

CT = ZoneInfo("America/Chicago")
NS_PER_S = 1_000_000_000
_ANCHOR_DAY = date(2000, 1, 3)  # clock arithmetic on a time of day (as _port_common.shift)


class ClockError(RuntimeError):
    """A frozen calendar input disagrees with the prereg's clock."""


@functools.cache
def equity_calendar() -> Any:
    from data.group_session import load_group_calendar

    return load_group_calendar("equity")


@functools.cache
def normal_close_ct() -> time:
    """D6's C for the vehicle from the frozen tables (CP1's source); must be 15:00 CT."""
    from screening.stage_e_frozen import load_frozen_tables

    c = load_frozen_tables().day_session_ct[K.VEHICLE][1]
    if c != K.NORMAL_CLOSE_CT:
        raise ClockError(f"frozen day_session_ct C for {K.VEHICLE} is {c}, the prereg says "
                         f"{K.NORMAL_CLOSE_CT}")
    return c


def shift(at: time, minutes: int) -> time:
    """A clock time ``minutes`` later (negative: earlier) on the same CT day."""
    return (datetime.combine(_ANCHOR_DAY, at) + timedelta(minutes=minutes)).time()


def close_ct(day: date, calendar: Any = None) -> time:
    """C(d): the early-halt time on a shortened day, else the normal close."""
    cal = calendar if calendar is not None else equity_calendar()
    halt = cal.early_halt_ct(day)
    return halt if halt is not None else normal_close_ct()


def is_shortened(day: date, calendar: Any = None) -> bool:
    cal = calendar if calendar is not None else equity_calendar()
    return cal.early_halt_ct(day) is not None


def ct_ns(day: date, at: time) -> int:
    """UTC ns of CT wall-clock ``at`` on CT date ``day`` (bars sit on whole seconds)."""
    return int(datetime.combine(day, at, tzinfo=CT).astimezone(UTC).timestamp()) * NS_PER_S


def signal_bar_ns(day: date, calendar: Any = None) -> int:
    """The open of the bar ending at C-30 (the bar at C-31; 14:29 on a normal day)."""
    return ct_ns(day, shift(close_ct(day, calendar), -K.SIGNAL_BAR_BEFORE_C_MIN))


def prior_bar_ns(prior_day: date, calendar: Any = None) -> int:
    """The open of the bar ending at the prior trade date's C (14:59 on a normal day)."""
    return ct_ns(prior_day, shift(close_ct(prior_day, calendar), -K.PRIOR_BAR_BEFORE_C_MIN))


def exit_from_ns(day: date, calendar: Any = None) -> int:
    """The open of the bar at C-2 (14:58 on a normal day): the exit is due at or after it."""
    return ct_ns(day, shift(close_ct(day, calendar), -K.EXIT_BEFORE_C_MIN))


def trade_dates(first: date, last: date, calendar: Any = None) -> tuple[date, ...]:
    """Every trade date of the frozen equity group calendar in [first, last]."""
    from data.group_session import trade_dates_between

    cal = calendar if calendar is not None else equity_calendar()
    return tuple(trade_dates_between(cal, first, last))


def previous_trade_date(day: date, calendar: Any = None) -> date | None:
    from data.group_session import previous_trade_date as _prev

    cal = calendar if calendar is not None else equity_calendar()
    return _prev(cal, day)


def t2_warmup_first(calendar: Any = None) -> date:
    """The 60th equity trade date before 2020-06-01 (prereg section 2)."""
    cal = calendar if calendar is not None else equity_calendar()
    before = trade_dates(K.VERDICT_FIRST - timedelta(days=180), K.VERDICT_FIRST
                         - timedelta(days=1), cal)
    if len(before) < K.T2_WARMUP_TRADE_DATES:
        raise ClockError("fewer than 60 equity trade dates in the 180 days before 2020-06-01")
    return before[-K.T2_WARMUP_TRADE_DATES]


def lead_in_dates(first: date, n: int, calendar: Any = None) -> tuple[date, ...]:
    """The ``n`` equity trade dates before ``first`` (the engine's no-entry lead-in), never before
    the store's first trade date."""
    out: list[date] = []
    day = first
    for _ in range(n):
        prev = previous_trade_date(day, calendar)
        if prev is None or prev < K.STORE_FIRST:
            break
        out.append(prev)
        day = prev
    return tuple(sorted(out))


def ct_of_ns(ts_ns: int) -> datetime:
    return datetime.fromtimestamp(ts_ns // NS_PER_S, tz=UTC).astimezone(CT)


__all__ = ["CT", "ClockError", "close_ct", "ct_ns", "ct_of_ns", "equity_calendar",
           "exit_from_ns", "is_shortened", "lead_in_dates", "normal_close_ct",
           "previous_trade_date", "prior_bar_ns", "shift", "signal_bar_ns", "t2_warmup_first",
           "trade_dates"]
