"""Per-trade-date tables of one vehicle's price path: sigma_X,d (v1 ML-A06), daily bars (CP3, G8).

docs/STAGE_E_ML_V2_DESIGN.md V2.3 (G5, G8, G9) and V2.4 (sigma_X,d); v1 ml_route/features.py
build_daily, whose readings are kept:
- O_X and C_X are D6's (the frozen day_session_ct of the vehicle); the bar at O is the bar opening
  at O on CT date d with trade date d, the bar at C-1 the one opening at C - 1 min;
- complete (v1): both bars present with one instrument_id and d not an early-halt date of the
  group calendar; move = |close(C-1) - open(O)| in vehicle ticks;
- sigma_X,d = the mean move over the SIGMA_D_DATES complete dates with bars strictly before d;
  its availability is the close of the latest of those dates' C-1 bar;
- the port's complete day (CP3, Family H, e.g. strategy/members/k1/cp3.py): the O and C-1 bars
  exist, d is not an early-halt date, and every bar of CT date d opening in [O, C) carries one
  instrument_id; H, L over those bars, C_d = close of the C-1 bar.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache

import numpy as np
import pandas as pd

from ml_route_v2.constants import G9_MEDIAN_DATES, SIGMA_D_DATES
from ml_route_v2.signals._core import (
    NS_MIN,
    BarArrays,
    SignalContext,
    as_date,
    bars_of,
    ct_ns,
    minute_of,
    path_of,
    per_unit,
)


@dataclass(frozen=True)
class Daily:
    vehicle: str
    days: np.ndarray  # trade dates with bars (epoch days), ascending
    o_ns: np.ndarray
    c_ns: np.ndarray
    o_idx: np.ndarray  # bar at O on CT date d with trade date d, -1 absent
    c1_idx: np.ndarray  # bar at C - 1 min
    halt: np.ndarray  # early-halt date of the group calendar
    complete: np.ndarray  # v1 complete
    ret: np.ndarray  # close(C-1) - open(O), vehicle ticks (NaN when not complete)
    sigma: np.ndarray  # sigma_X,d, vehicle ticks
    sigma_avail: np.ndarray
    g9: np.ndarray  # sigma / median(sigma over the 120 dates ending at d)
    port_complete: np.ndarray
    hi: np.ndarray  # daily high over [O, C)
    lo: np.ndarray
    c1_close: np.ndarray

    def pos(self, days: np.ndarray) -> np.ndarray:
        days = np.asarray(days, dtype=np.int64)
        p = np.searchsorted(self.days, days)
        ok = p < len(self.days)
        ok[ok] = self.days[p[ok]] == days[ok]
        return np.where(ok, p, -1)


@cache
def session_minutes(vehicle: str) -> tuple[int, int]:
    """(O, C) of the vehicle as CT minutes, from the frozen D6 table."""
    from screening.stage_e_frozen import load_frozen_tables

    o, c = load_frozen_tables().day_session_ct[vehicle]
    return minute_of(o), minute_of(c)


@cache
def _halt_days(vehicle: str, first: int, last: int) -> frozenset[int]:
    from data.calendars import GROUP_OF_PRODUCT
    from ml_route.inputs import _group_calendar

    cal = _group_calendar(GROUP_OF_PRODUCT[vehicle])
    return frozenset(d for d in range(first, last + 1)
                     if cal.covers(as_date(d)) and cal.early_halt_ct(as_date(d)) is not None)


def halt_flags(vehicle: str, days: np.ndarray) -> np.ndarray:
    if len(days) == 0:
        return np.zeros(0, dtype=bool)
    halts = _halt_days(vehicle, int(days.min()), int(days.max()))
    return np.fromiter((int(d) in halts for d in days), dtype=bool, count=len(days))


def _segment_reduce(values: np.ndarray, lo: np.ndarray, hi: np.ndarray, fn: str) -> np.ndarray:
    """max/min of values[lo:hi] per segment (NaN for an empty one)."""
    out = np.full(len(lo), np.nan)
    ok = hi > lo
    if not ok.any():
        return out
    ufunc = np.maximum if fn == "max" else np.minimum
    ext = np.append(values.astype(np.float64), np.nan)  # an end index may equal len(values)
    pairs = np.column_stack([lo[ok], hi[ok]]).ravel()  # reduceat over [lo, hi) at even slots
    out[ok] = ufunc.reduceat(ext, pairs)[::2]
    return out


def build_daily(vehicle: str, bars: BarArrays) -> Daily:
    days = bars.udays
    o_min, c_min = session_minutes(vehicle)
    o_ns = ct_ns(days, o_min)
    c_ns = ct_ns(days, c_min)
    o_idx = bars.at(o_ns)
    c1_idx = bars.at(c_ns - NS_MIN)
    o_idx = np.where(bars.on_day(o_idx, days), o_idx, -1)
    c1_idx = np.where(bars.on_day(c1_idx, days), c1_idx, -1)
    halt = halt_flags(vehicle, days)
    both = (o_idx >= 0) & (c1_idx >= 0)
    iid_o = np.where(both, bars.iid[np.clip(o_idx, 0, None)].astype(np.int64), -1)
    iid_c = np.where(both, bars.iid[np.clip(c1_idx, 0, None)].astype(np.int64), -2)
    complete = both & (iid_o == iid_c) & ~halt
    pu = per_unit(vehicle)
    ret = np.full(len(days), np.nan)
    ret[complete] = (bars.close[c1_idx[complete]] - bars.open[o_idx[complete]]) * pu
    sigma, sigma_avail = _sigma(np.abs(ret), complete, bars, c1_idx)
    med = pd.Series(sigma).rolling(G9_MEDIAN_DATES, min_periods=G9_MEDIAN_DATES).median()
    g9 = sigma / med.to_numpy()
    lo = np.searchsorted(bars.ts, o_ns)
    hi = np.searchsorted(bars.ts, c_ns)
    hi = np.minimum(hi, bars.last + 1)
    lo = np.maximum(lo, bars.first)
    hmax = _segment_reduce(bars.high, lo, hi, "max")
    lmin = _segment_reduce(bars.low, lo, hi, "min")
    iid_f = bars.iid.astype(np.float64)
    one_iid = _segment_reduce(iid_f, lo, hi, "max") == _segment_reduce(iid_f, lo, hi, "min")
    port_complete = both & ~halt & one_iid
    c1_close = np.where(c1_idx >= 0, bars.close[np.clip(c1_idx, 0, None)], np.nan)
    return Daily(vehicle, days, o_ns, c_ns, o_idx, c1_idx, halt, complete, ret, sigma,
                 sigma_avail, g9, port_complete, hmax, lmin, c1_close)


def _sigma(move: np.ndarray, complete: np.ndarray, bars: BarArrays, c1_idx: np.ndarray
           ) -> tuple[np.ndarray, np.ndarray]:
    n = len(move)
    sigma = np.full(n, np.nan)
    avail = np.full(n, -1, dtype=np.int64)
    comp = np.flatnonzero(complete)
    k = np.searchsorted(comp, np.arange(n))  # complete dates strictly before each date
    have = k >= SIGMA_D_DATES
    if have.any():
        csum = np.concatenate([[0.0], np.cumsum(move[comp])])
        kk = k[have]
        sigma[have] = (csum[kk] - csum[kk - SIGMA_D_DATES]) / SIGMA_D_DATES
        avail[have] = bars.ts[c1_idx[comp[kk - 1]]] + NS_MIN
    return sigma, avail


@cache
def _intervals(group: str, day: int) -> tuple[tuple[int, int], ...]:
    from data.group_session import session_intervals
    from ml_route.inputs import _group_calendar

    return tuple(session_intervals(_group_calendar(group), as_date(day)))


def in_session(vehicle: str, days: np.ndarray, when: np.ndarray) -> np.ndarray:
    """True where the instant ``when`` (a bar open) lies in an open interval of trade date
    ``days`` of the vehicle's group calendar (data.group_session.session_intervals)."""
    from data.calendars import GROUP_OF_PRODUCT

    group = GROUP_OF_PRODUCT[vehicle]
    out = np.zeros(len(days), dtype=bool)
    for d in np.unique(days):
        sel = days == d
        w = when[sel]
        hit = np.zeros(len(w), dtype=bool)
        for lo, hi in _intervals(group, int(d)):
            hit |= (w >= lo) & (w < hi)
        out[sel] = hit
    return out


def daily_of(ctx: SignalContext, vehicle: str) -> Daily:
    key = ("daily", vehicle)
    if key not in ctx.cache:
        ctx.cache[key] = build_daily(vehicle, bars_of(ctx, path_of(vehicle)))
    return ctx.cache[key]


__all__ = ["G9_MEDIAN_DATES", "Daily", "build_daily", "daily_of", "halt_flags", "in_session",
           "session_minutes"]
