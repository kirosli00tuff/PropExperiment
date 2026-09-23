"""Zero-edge daily P&L generator for the funnel Monte Carlo (Stage B, Task 2).

What it is: a symmetric random process for the gross P&L of a trader with NO
edge, calibrated to how MES actually moved. Each simulated day:

1. picks a historical RESEARCH trade date by stationary block bootstrap
   (Politis & Romano 1994, circular, mean block ``mean_block_days``), so quiet
   and violent stretches arrive in runs as they did historically. Volatility
   clustering is what makes several MLLs die in the same week;
2. splits that day's RTH window (the 08:30 CT bar up to the last bar before the
   Topstep flatten) into ``segments_per_day`` equal runs of bars, one round turn
   each, and reads per segment the long-side move (last close - first open) and
   the long-side excursions (lowest low, highest high, relative to the entry);
3. flips a fair coin per segment for the side, independently of everything else.

Why the expectation is exactly zero (the property to point at): the side comes
from ``fair_signs(rng, shape)``, which depends on nothing but the shape: not on
the chosen day, not on any price. For every segment
E[pnl] = P(long)*move + P(short)*(-move) = move/2 - move/2 = 0, and the P&L
distribution is mirror-symmetric about zero by construction. The research
slice's historical drift (+13.65 ticks per RTH session) cannot leak through.
``tests/test_null_generator.py`` checks sign independence, exact mirror symmetry,
and the long-run mean within a stated tolerance.

Calibration: magnitudes come from the research slice's own bars, loaded through
``data.research_bars``. Holdout and embargo dates are refused at construction.
With one segment per day there are 310 RTH sessions, sd 226.9 ticks = $283.62
per micro (measured 2026-09-17; ``calibration_summary`` recomputes it).

Units: ticks (0.25 pt) per ONE micro, gross of costs. The funnel simulator
applies size, commission and slippage (``sim.fill_model``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from data.research_bars import (
    CONFIRMATION,
    EMBARGO2,
    HOLDOUT1,
    HOLDOUT2,
    RESEARCH,
    trade_date_class,
)

CT = ZoneInfo("America/Chicago")
MES_TICK = 0.25
MES_TICK_VALUE_USD = 1.25
RTH_OPEN_MINUTE_CT = 8 * 60 + 30
DAILY_HALT_MINUTE_CT = 16 * 60
DEFAULT_MEAN_BLOCK_DAYS = 5.0  # one trading week of volatility persistence
REQUIRED_COLUMNS = ("ts_event", "open", "high", "low", "close", "trade_date", "in_flatten_window")


def _frozen(values: np.ndarray) -> np.ndarray:
    out = np.array(values, copy=True)
    out.flags.writeable = False
    return out


def _to_ticks(prices: np.ndarray) -> np.ndarray:
    ticks = np.rint(prices / MES_TICK)
    if len(prices) and np.abs(ticks * MES_TICK - prices).max() > 1e-9:
        raise ValueError("price off the MES 0.25 tick grid")
    return ticks.astype(np.int64)


@dataclass(frozen=True)
class SegmentTable:
    """Per research day, per segment: long-side move and excursions, in ticks per micro."""

    trade_dates: tuple[str, ...]
    segments_per_day: int
    move_ticks: np.ndarray  # (days, T) last close - first open
    low_ticks: np.ndarray  # (days, T) lowest low - entry, <= 0
    high_ticks: np.ndarray  # (days, T) highest high - entry, >= 0
    entry_minute_ct: np.ndarray  # (days, T) CT minute of entry (segment's first bar open)
    exit_minute_ct: np.ndarray  # (days, T) CT minute of exit (segment's last bar close)
    skipped_trade_dates: tuple[str, ...] = field(default=())

    @property
    def n_days(self) -> int:
        return len(self.trade_dates)


def _refuse_outside_one_slice(trade_dates: pd.Series) -> None:
    """R-3 (Stage D.1f): accepted only if ALL dates are research dates or ALL are
    confirmation-window dates (``data.research_bars.trade_date_class``). Never mixed, never
    holdout-1, holdout-2, embargo-2 or the research embargo."""
    days = sorted({str(d) for d in trade_dates.unique()})
    kind = {d: trade_date_class(date.fromisoformat(d)) for d in days}
    held = [d for d in days if kind[d] == HOLDOUT1]
    if held:
        raise ValueError(f"holdout trade dates refused by the null generator: {held[:3]}...")
    sealed = [d for d in days if kind[d] in (HOLDOUT2, EMBARGO2)]
    if sealed:
        raise ValueError(f"holdout-2 / embargo-2 trade dates refused by the null generator: "
                         f"{sealed[:3]}...")
    outside = [d for d in days if kind[d] not in (RESEARCH, CONFIRMATION)]
    if outside:
        raise ValueError(f"non-research (embargo/out-of-range) trade dates refused: {outside[:3]}")
    if len(set(kind.values())) > 1:
        raise ValueError("mixed research and confirmation-window trade dates refused: a frame "
                         f"is all research dates or all confirmation dates ({days[0]}..{days[-1]})")


def build_segment_table(bars: pd.DataFrame, segments_per_day: int) -> SegmentTable:
    """Pure: research bars -> per-day RTH segments. Bars must be in time order."""
    if segments_per_day < 1:
        raise ValueError("segments_per_day must be >= 1")
    missing = [c for c in REQUIRED_COLUMNS if c not in bars.columns]
    if missing:
        raise ValueError(f"bars missing columns {missing}")
    _refuse_outside_one_slice(bars["trade_date"])
    ts = bars["ts_event"].to_numpy(np.int64)
    if len(ts) > 1 and not (np.diff(ts) > 0).all():
        raise ValueError("bars must be strictly increasing in ts_event")

    local = pd.to_datetime(ts, utc=True).tz_convert(CT)
    minute = np.asarray(local.hour * 60 + local.minute)
    in_rth = (
        (minute >= RTH_OPEN_MINUTE_CT)
        & (minute < DAILY_HALT_MINUTE_CT)
        & ~bars["in_flatten_window"].to_numpy(bool)
    )
    opens, closes = _to_ticks(bars["open"].to_numpy()), _to_ticks(bars["close"].to_numpy())
    lows, highs = _to_ticks(bars["low"].to_numpy()), _to_ticks(bars["high"].to_numpy())
    trade_dates = bars["trade_date"].astype(str).to_numpy()

    kept: list[str] = []
    skipped: list[str] = []
    rows: list[tuple[list[int], list[int], list[int], list[int], list[int]]] = []
    for day in dict.fromkeys(trade_dates):  # first-seen order == time order
        idx = np.flatnonzero((trade_dates == day) & in_rth)
        if len(idx) < segments_per_day or minute[idx[0]] != RTH_OPEN_MINUTE_CT:
            skipped.append(day)
            continue
        move, low, high, entry_m, exit_m = [], [], [], [], []
        for seg in np.array_split(idx, segments_per_day):
            entry = opens[seg[0]]
            move.append(int(closes[seg[-1]] - entry))
            low.append(int(lows[seg].min() - entry))
            high.append(int(highs[seg].max() - entry))
            entry_m.append(int(minute[seg[0]]))
            exit_m.append(int(minute[seg[-1]]) + 1)
        kept.append(day)
        rows.append((move, low, high, entry_m, exit_m))

    def column(k: int) -> np.ndarray:
        return _frozen(np.array([r[k] for r in rows], dtype=np.int64).reshape(-1, segments_per_day))

    return SegmentTable(
        trade_dates=tuple(kept),
        segments_per_day=segments_per_day,
        move_ticks=column(0),
        low_ticks=column(1),
        high_ticks=column(2),
        entry_minute_ct=column(3),
        exit_minute_ct=column(4),
        skipped_trade_dates=tuple(skipped),
    )


# ---------------------------------------------------------------- sampling ----
def fair_signs(rng: np.random.Generator, shape: tuple[int, ...]) -> np.ndarray:
    """+1 (long) or -1 (short), each with probability exactly 1/2. Reads no data."""
    return rng.integers(0, 2, size=shape, dtype=np.int64) * 2 - 1


def stationary_bootstrap_indices(
    rng: np.random.Generator, n_source: int, n_draw: int, mean_block: float
) -> np.ndarray:
    """Circular stationary bootstrap: each step starts a new block with prob 1/mean_block."""
    if n_source < 1 or n_draw < 0:
        raise ValueError("need n_source >= 1 and n_draw >= 0")
    if mean_block < 1.0:
        raise ValueError("mean_block must be >= 1 day")
    if n_draw == 0:
        return np.empty(0, dtype=np.int64)
    starts = rng.integers(0, n_source, size=n_draw)
    renew = rng.random(n_draw) < 1.0 / mean_block
    renew[0] = True
    block = np.cumsum(renew) - 1
    block_start = np.flatnonzero(renew)
    offset = np.arange(n_draw) - block_start[block]
    return (starts[block_start][block] + offset) % n_source


@dataclass(frozen=True)
class DayDraws:
    """``n_days`` simulated days x ``T`` segments; per micro, gross of costs."""

    day_index: np.ndarray  # (n,) row of the SegmentTable each day came from
    side: np.ndarray  # (n, T) +1 long / -1 short
    pnl_ticks: np.ndarray  # (n, T) side * move
    adverse_ticks: np.ndarray  # (n, T) worst open-trade excursion for that side, <= 0
    entry_minute_ct: np.ndarray  # (n, T)
    exit_minute_ct: np.ndarray  # (n, T)


@dataclass(frozen=True)
class NullDayGenerator:
    table: SegmentTable
    mean_block_days: float = DEFAULT_MEAN_BLOCK_DAYS

    def draw(self, rng: np.random.Generator, n_days: int) -> DayDraws:
        idx = stationary_bootstrap_indices(rng, self.table.n_days, n_days, self.mean_block_days)
        side = fair_signs(rng, (n_days, self.table.segments_per_day))
        adverse = np.where(side > 0, self.table.low_ticks[idx], -self.table.high_ticks[idx])
        return DayDraws(
            day_index=idx,
            side=side,
            pnl_ticks=side * self.table.move_ticks[idx],
            adverse_ticks=adverse,
            entry_minute_ct=self.table.entry_minute_ct[idx],
            exit_minute_ct=self.table.exit_minute_ct[idx],
        )


def calibration_summary(table: SegmentTable) -> dict:
    """The volatility figures the generator inherits from the bars (long side, per micro)."""
    session_move = table.move_ticks.sum(axis=1)
    return {
        "research_days": table.n_days,
        "first_trade_date": table.trade_dates[0] if table.n_days else None,
        "last_trade_date": table.trade_dates[-1] if table.n_days else None,
        "skipped_trade_dates": list(table.skipped_trade_dates),
        "segments_per_day": table.segments_per_day,
        "rth_session_move_sd_ticks": round(float(session_move.std(ddof=1)), 3),
        "rth_session_move_sd_usd_per_micro": round(
            float(session_move.std(ddof=1)) * MES_TICK_VALUE_USD, 2
        ),
        "rth_session_move_mean_ticks_long_drift": round(float(session_move.mean()), 3),
        "segment_move_sd_ticks": round(float(table.move_ticks.std(ddof=1)), 3),
        "segment_abs_move_median_ticks": float(np.median(np.abs(table.move_ticks))),
        "segment_low_median_ticks": float(np.median(table.low_ticks)),
        "segment_high_median_ticks": float(np.median(table.high_ticks)),
    }


def load_null_generator(
    segments_per_day: int, mean_block_days: float = DEFAULT_MEAN_BLOCK_DAYS
) -> NullDayGenerator:
    """The calibrated null, from research-slice bars only."""
    from data.research_bars import load_research_bars  # I/O kept at the edge

    bars = load_research_bars(columns=REQUIRED_COLUMNS)
    return NullDayGenerator(build_segment_table(bars, segments_per_day), mean_block_days)
