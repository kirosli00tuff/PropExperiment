"""Synthetic inputs for the signal library's tests and the panel's timed build. No market data.

- ``session_bars``: random-walk one-minute bars on every open interval of a root's real group
  calendar (data.group_session.session_intervals: the evening and day segments, early halts cut),
  on the root's vendor tick grid, in the BAR_COLUMNS schema the library reads (ts_event, open,
  high, low, close, volume, instrument_id, trade_date). ``compact`` stores trade_date as a
  categorical of ISO strings and volume as uint32 (the timed build); ``drop`` removes that share
  of bars at random.
- ``synthetic_releases``: a ReleaseCalendar (screening.stage_e_rules) with a release at 07:30 or
  09:00 CT on about 15% of weekdays for every vehicle of constants.UNIVERSE, and CPI instants.
ml_route_v2/synthetic.py (Task 5) owns the pipeline's synthetic world; this module only serves
the Task 2 tests and timing.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date

import numpy as np
import pandas as pd

from ml_route_v2.constants import UNIVERSE

NS_MIN = 60_000_000_000
START_TICKS = 20_000
MAX_STEP_TICKS = 3


def session_bars(root: str, first: date, last: date, seed: int, *, compact: bool = False,
                 drop: float = 0.0, start_ticks: int = START_TICKS) -> pd.DataFrame:
    from data.group_session import group_of, session_intervals, trade_dates_between
    from ml_route.inputs import _group_calendar
    from rules.products import product

    rng = np.random.default_rng(seed)
    tick = float(product(root).vendor_tick)
    cal = _group_calendar(group_of(root))
    ts_parts, day_parts = [], []
    days = trade_dates_between(cal, first, last)
    for code_of_day, day in enumerate(days):
        for lo, hi in session_intervals(cal, day):
            start = -(-lo // NS_MIN) * NS_MIN
            ts = np.arange(start, hi, NS_MIN, dtype=np.int64)
            if len(ts):
                ts_parts.append(ts)
                day_parts.append(np.full(len(ts), code_of_day, dtype=np.int32))
    ts = np.concatenate(ts_parts) if ts_parts else np.zeros(0, np.int64)
    code = np.concatenate(day_parts) if day_parts else np.zeros(0, np.int32)
    if drop > 0 and len(ts):
        keep = rng.random(len(ts)) >= drop
        ts, code = ts[keep], code[keep]
    steps = rng.integers(-MAX_STEP_TICKS, MAX_STEP_TICKS + 1, size=len(ts))
    path = start_ticks + np.cumsum(steps)
    path = np.abs(path - 100) + 100  # stay positive
    close = path * tick
    opens = np.concatenate([[start_ticks * tick], close[:-1]])
    wig = rng.integers(0, 3, size=len(ts)) * tick
    iso = np.array([d.isoformat() for d in days], dtype=object)
    trade = pd.Categorical.from_codes(code, categories=iso) if compact else iso[code]
    return pd.DataFrame({
        "ts_event": ts, "open": opens, "high": np.maximum(opens, close) + wig,
        "low": np.minimum(opens, close) - wig, "close": close,
        "volume": rng.integers(1, 400, size=len(ts)).astype(np.uint32 if compact else np.uint64),
        "instrument_id": np.ones(len(ts), dtype=np.uint32), "trade_date": trade})


def synthetic_releases(first: date, last: date, seed: int,
                       roots: Iterable[str] | None = None):  # noqa: ANN201 - ReleaseCalendar
    from datetime import UTC, datetime
    from types import MappingProxyType

    from screening.stage_e_rules import ReleaseCalendar

    rng = np.random.default_rng(seed)
    days = pd.bdate_range(first, last)
    picks = days[rng.random(len(days)) < 0.15]
    at = np.where(rng.random(len(picks)) < 0.5, 7 * 60 + 30, 9 * 60)
    local = pd.DatetimeIndex(picks) + pd.to_timedelta(at, unit="m")
    rel = np.sort(local.tz_localize("America/Chicago").tz_convert("UTC").as_unit("ns")
                  .asi8.astype(np.int64))
    cpi_days = days[(days.day >= 10) & (days.day <= 12)][::3]
    cpi_local = (pd.DatetimeIndex(cpi_days) + pd.Timedelta(hours=7, minutes=30)
                 ).tz_localize("America/Chicago").tz_convert("UTC")
    cpi = tuple(datetime.fromtimestamp(x.value / 1e9, tz=UTC) for x in cpi_local)
    roots = tuple(roots) if roots is not None else tuple(UNIVERSE)
    by_root = MappingProxyType({r: tuple(int(x) for x in rel) for r in roots})
    return ReleaseCalendar(by_root, cpi, first, last, "0" * 64, "synthetic")


__all__ = ["session_bars", "synthetic_releases"]
