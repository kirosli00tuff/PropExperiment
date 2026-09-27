"""M4: decision rows, the features F1-F17 with an availability time on every value, the net
target (with ml_route.target), and M7.1's feature-timestamp validator.

Conventions (bars as in data/bars.py: ``ts`` is the bar OPEN; a bar closes 60 s later):
- A decision time t runs over O_X + 30 k minutes, k = 1, 2, ..., with t < C_X (D6 session table,
  ML-A09). A value is available at t when every bar it reads closes at or before t.
- A value's availability time is derived mechanically from the latest bar it reads (that bar's
  close), or is the decision time itself for calendar values (F11-F15, known in advance). The
  validator raises if any non-missing value is available after its row's t (M7.1).
- Prices are converted to ticks of the exposure's D2 vehicle and divided by sigma_X,d (M2, ML-A06,
  ML-A08). Missing inputs are NaN and exclude the row (ML-A05); nothing is imputed.

Readings of the frozen text taken here (each listed in the worker report):
- F1-F5 read the bar closing exactly at t and the bar closing exactly at t - k minutes, both of
  trade date d; either absent makes the value missing ("a lookback that is not full").
- F6 and F9 run from the trade date's first bar; F9 = (highest high - lowest low) of the bars of
  d closing at or before t.
- F7 = open of the bar at O_X on d minus the close of the bar at C_X - 1 min of the calendar's
  previous trade date; F8 = CP3's CLV of that previous trade date, which must be complete.
- F10: the volume of d's bars closing in (t - 30, t] over the median of the same CT clock window
  on the product's 20 previous trade dates with bars; missing below 20 dates or at a zero volume.
- F13/F14: minutes to the first release at or after t, and since the last one before t; F15: a
  release on t's CT calendar date. F16: the lead's normalized 30-minute return ending at the
  lead's latest bar closing at or before t on the same trade date (sigma of the lead).
- F17 = sigma_X,d over the median of sigma over the 120 trade dates ending at d (all present).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date
from functools import lru_cache

import numpy as np
import pandas as pd

from ml_route.constants import (
    DECISION_SPACING_MIN,
    EVENT_GUARD_MIN,
    F17_MEDIAN_DATES,
    FEATURES_DISTILLABLE,
    MAX_DECISIONS_PER_DAY,
    SIGMA_LOOKBACK_DATES,
)
from ml_route.inputs import DayTimes, ProductSpec

NS_MIN = 60_000_000_000
BAR_NS = NS_MIN
N_FEATURES = len(FEATURES_DISTILLABLE)
CPI_HALF_WINDOW_MIN = 5


class FeatureLeak(RuntimeError):
    """M7.1: a feature value is available after its row's decision time."""


@dataclass(frozen=True)
class Bars:
    """One product's bars (sorted by ts), prices in vendor units."""

    root: str
    ts: np.ndarray
    open: np.ndarray
    high: np.ndarray
    low: np.ndarray
    close: np.ndarray
    volume: np.ndarray
    instrument_id: np.ndarray
    trade_date: np.ndarray  # datetime64[D]

    def __post_init__(self) -> None:
        if len(self.ts) and np.any(np.diff(self.ts) <= 0):
            raise ValueError(f"{self.root}: bars are not strictly ascending in ts")

    def idx_at(self, when: np.ndarray) -> np.ndarray:
        """Index of the bar opening exactly at ``when`` (int64 ns), -1 when absent."""
        when = np.asarray(when, dtype=np.int64)
        pos = np.searchsorted(self.ts, when)
        ok = pos < len(self.ts)
        ok[ok] = self.ts[pos[ok]] == when[ok]
        return np.where(ok, pos, -1)


@dataclass(frozen=True)
class Daily:
    """Per trade date of one product: sessions, sigma_X,d, F7, F8, F17 (all causal)."""

    dates: np.ndarray  # datetime64[D], the product's trade dates with bars
    first_idx: np.ndarray
    times: tuple[DayTimes, ...]
    sigma: np.ndarray  # vehicle ticks; NaN = missing
    sigma_avail: np.ndarray  # ns; the close of the latest date sigma reads
    f7: np.ndarray
    f7_avail: np.ndarray
    f8: np.ndarray
    f8_avail: np.ndarray
    f17: np.ndarray
    complete: np.ndarray

    def pos_of(self, day: np.datetime64) -> int:
        i = int(np.searchsorted(self.dates, day))
        return i if i < len(self.dates) and self.dates[i] == day else -1


def build_daily(bars: Bars, spec: ProductSpec, times: Mapping[date, DayTimes]) -> Daily:
    """sigma_X,d (ML-A06), F7, F8 and F17 per trade date, from bars of earlier dates only."""
    dates, first_idx = np.unique(bars.trade_date, return_index=True)
    n = len(dates)
    pu = spec.vehicle_ticks_per_vendor_unit
    if pu is None:
        raise ValueError(f"{spec.root} has no vehicle; it has no target and no rows")
    tt = []
    for d in dates:
        dt = times.get(d.astype(object))
        if dt is None:
            raise ValueError(f"{spec.root}: bars on {d}, which has no session times")
        tt.append(dt)
    o_i = bars.idx_at(np.array([x.open_ns for x in tt], dtype=np.int64))
    c_i = bars.idx_at(np.array([x.close_ns - BAR_NS for x in tt], dtype=np.int64))
    halt = np.array([x.early_halt for x in tt], dtype=bool)
    both = (o_i >= 0) & (c_i >= 0)
    same_inst = np.zeros(n, dtype=bool)
    same_inst[both] = bars.instrument_id[o_i[both]] == bars.instrument_id[c_i[both]]
    complete = both & same_inst & ~halt
    move = np.full(n, np.nan)
    move[complete] = np.abs(bars.close[c_i[complete]] - bars.open[o_i[complete]]) * pu
    close_ns = np.array([x.close_ns for x in tt], dtype=np.int64)
    sigma = np.full(n, np.nan)
    sigma_avail = np.full(n, -1, dtype=np.int64)
    comp_pos = np.flatnonzero(complete)
    k = np.searchsorted(comp_pos, np.arange(n))  # complete dates strictly before each date
    have = k >= SIGMA_LOOKBACK_DATES
    if have.any():
        csum = np.concatenate([[0.0], np.cumsum(move[comp_pos])])
        kk = k[have]
        sigma[have] = (csum[kk] - csum[kk - SIGMA_LOOKBACK_DATES]) / SIGMA_LOOKBACK_DATES
        sigma_avail[have] = close_ns[comp_pos[kk - 1]]
    f17 = np.full(n, np.nan)
    if n >= F17_MEDIAN_DATES:
        med = pd.Series(sigma).rolling(F17_MEDIAN_DATES, min_periods=F17_MEDIAN_DATES).median()
        f17 = sigma / med.to_numpy()
    f7 = np.full(n, np.nan)
    f7_avail = np.full(n, -1, dtype=np.int64)
    f8 = np.full(n, np.nan)
    f8_avail = np.full(n, -1, dtype=np.int64)
    for i in range(1, n):
        if not _is_previous_trade_date(spec, dates[i - 1], dates[i]):
            continue
        if o_i[i] >= 0 and c_i[i - 1] >= 0:
            f7[i] = (bars.open[o_i[i]] - bars.close[c_i[i - 1]]) * pu
            f7_avail[i] = bars.ts[o_i[i]] + BAR_NS
        if complete[i - 1]:
            lo, hi = o_i[i - 1], c_i[i - 1] + 1
            h, lw = bars.high[lo:hi].max(), bars.low[lo:hi].min()
            if h > lw:
                f8[i] = (bars.close[c_i[i - 1]] - lw) / (h - lw)
                f8_avail[i] = bars.ts[c_i[i - 1]] + BAR_NS
    return Daily(dates, first_idx, tuple(tt), sigma, sigma_avail, f7, f7_avail, f8, f8_avail,
                 f17, complete)


def _is_previous_trade_date(spec: ProductSpec, prev: np.datetime64, day: np.datetime64) -> bool:
    got = _previous_trade_date(spec.group, day.astype(object))
    return got is not None and np.datetime64(got) == prev


@lru_cache(maxsize=65_536)
def _previous_trade_date(group: str, day: date) -> date | None:
    from data.group_session import previous_trade_date
    from ml_route.inputs import _group_calendar

    return previous_trade_date(_group_calendar(group), day)


@dataclass(frozen=True)
class LeadContext:
    """What F16 reads of a cluster's lead product."""

    root: str
    bars: Bars
    daily: Daily
    per_unit: float


@dataclass
class RowTable:
    """Decision rows of one or more products. ``X`` columns follow FEATURES_DISTILLABLE."""

    product: np.ndarray  # str
    cluster: np.ndarray  # str
    day: np.ndarray  # datetime64[D]
    t_ns: np.ndarray
    X: np.ndarray  # float64 (n, 17)
    avail: np.ndarray  # int64 (n, 17)
    sigma: np.ndarray
    y: dict[str, np.ndarray]  # horizon -> net target in sigma units (NaN = missing)
    cost: dict[str, np.ndarray]  # horizon -> 1.0 x D8 round-turn cost in sigma units
    exit_ns: dict[str, np.ndarray]  # horizon -> exit fill time (-1 = missing)
    counts: dict[str, int] = field(default_factory=dict)
    store_sha256: dict[str, str] = field(default_factory=dict)  # root -> step 2 parquet read

    def __len__(self) -> int:
        return len(self.t_ns)

    def complete_mask(self, horizon: str) -> np.ndarray:
        """Rows with every feature and the horizon's target present (ML-A05)."""
        return np.isfinite(self.X).all(axis=1) & np.isfinite(self.y[horizon])


def _in_windows(when: np.ndarray, starts: np.ndarray, width_ns: int, before_ns: int = 0
                ) -> np.ndarray:
    """True where ``when`` lies in [s - before, s + width) for some sorted start s."""
    if len(starts) == 0:
        return np.zeros(len(when), dtype=bool)
    pos = np.searchsorted(starts, when + before_ns, side="right") - 1
    ok = pos >= 0
    out = np.zeros(len(when), dtype=bool)
    s = starts[np.clip(pos, 0, None)]
    out[ok] = (when[ok] >= s[ok] - before_ns) & (when[ok] < s[ok] + width_ns)
    return out


def decision_grid(bars: Bars, daily: Daily, spec: ProductSpec, blackout: frozenset[date],
                  releases: np.ndarray, cpi: np.ndarray, counts: dict[str, int],
                  only_date_pos: int | None = None) -> tuple[np.ndarray, np.ndarray]:
    """(date position, t) of every admissible decision time (M4, ML-A09, D9.5a, D9.12); with
    ``only_date_pos``, of that one date (the rule wrapper's per-decision call)."""
    pos_l, t_l = [], []
    span = range(len(daily.dates)) if only_date_pos is None else (only_date_pos,)
    for i in span:
        d = daily.dates[i]
        dt = daily.times[i]
        if d.astype(object) in blackout:
            counts["dates_roll_blackout"] = counts.get("dates_roll_blackout", 0) + 1
            continue
        if dt.early_halt:
            counts["dates_early_halt"] = counts.get("dates_early_halt", 0) + 1
            continue
        for k in range(1, MAX_DECISIONS_PER_DAY + 1):
            t = dt.open_ns + k * DECISION_SPACING_MIN * NS_MIN
            if t >= dt.close_ns:
                break
            pos_l.append(i)
            t_l.append(t)
        beyond = dt.open_ns + (MAX_DECISIONS_PER_DAY + 1) * DECISION_SPACING_MIN * NS_MIN
        if beyond < dt.close_ns:
            raise ValueError(f"{spec.root} {d}: the D6 session gives more than "
                             f"{MAX_DECISIONS_PER_DAY} decision times (M4 says at most 13)")
    pos = np.array(pos_l, dtype=np.int64)
    t = np.array(t_l, dtype=np.int64)
    entry = t + BAR_NS
    guard = _in_windows(entry, releases, EVENT_GUARD_MIN * NS_MIN)
    cpi_hit = (_in_windows(entry, cpi, (CPI_HALF_WINDOW_MIN * 2) * NS_MIN + 1,
                           CPI_HALF_WINDOW_MIN * NS_MIN) if spec.cpi_no_open
               else np.zeros(len(t), dtype=bool))
    counts["decisions_event_guard"] = int(guard.sum())
    counts["decisions_cpi_window"] = int((cpi_hit & ~guard).sum())
    keep = ~guard & ~cpi_hit
    return pos[keep], t[keep]


def _ct_minute(ns: np.ndarray) -> np.ndarray:
    idx = pd.to_datetime(ns, utc=True).tz_convert("America/Chicago")
    return (idx.hour * 60 + idx.minute).to_numpy()


def _ct_date(ns: np.ndarray) -> np.ndarray:
    idx = pd.to_datetime(ns, utc=True).tz_convert("America/Chicago")
    return idx.tz_localize(None).normalize().to_numpy().astype("datetime64[D]")
