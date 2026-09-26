"""Per-exposure segment tables for the funnel re-derivation (Stage E.2a Task 13; design D3, D11.8).

``funnel.null_generator.build_segment_table`` is MES's table (08:30 CT to the Topstep flatten, the
0.25 tick, research-slice dates only) and stays unchanged. This module builds the same
``SegmentTable`` for any exposure's vehicle from its research-window bars, with every MES constant
turned into a parameter:

- the window: bars at or after the day-session open O, strictly before an end minute (MES: the
  16:00 CT daily halt; an exposure: its F or its C, per the lead's declaration), and not flagged
  ``in_flatten_window`` (the parquet's F, which also carries early closes);
- the tick, in the VENDOR's price units (Databento quotes ZC, ZW, ZS, ZL, HE and LE in cents, so
  their vendor tick is 100 x the E.0 USD tick): every price must sit on that grid, and the grid
  must be the smallest one (``tick_scale_check``), so a tick 10x or 100x too fine is refused
  instead of silently inflating every move;
- the trade dates: an explicit first/last and the date classes allowed (MES: the research slice;
  Stage E's D4 window also reaches into MES's research embargo, 2026-06-13..19), plus an optional
  set of excluded trade dates (e.g. D2's roll-blackout and vendor-degraded dates);
- one instrument per day window (optional; a segment spanning a roll splice would book a
  calendar spread as a move).

Segments are MES's: the day's in-window bars split into T runs of (nearly) equal BAR COUNT by
``np.array_split``; a day is skipped when it has fewer bars than T or its first in-window bar is
not exactly at O (MES's rule). With MES's parameters this reproduces
``funnel.null_generator.build_segment_table`` array for array (tests/test_e2a_exposure_gate.py
and the MES regression).

From research-window data this module computes the segment table and E|m_T| only: no returns,
volatility summaries or charts (brief, Task 13).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.dataset as pads

from data.research_bars import RESEARCH, RESEARCH_EMBARGO, refuse_dates_outside
from funnel.null_generator import SegmentTable

CT = ZoneInfo("America/Chicago")
MES_OPEN_MINUTE_CT = 8 * 60 + 30
MES_HALT_MINUTE_CT = 16 * 60
BAR_COLUMNS = ("ts_event", "open", "high", "low", "close", "trade_date", "in_flatten_window",
               "instrument_id")
GRID_TOLERANCE_TICKS = 1e-6  # |price / tick - rint| above this is off the grid
# A true tick leaves roughly half of all prices off the 2x grid; a tick that is too fine by a
# factor of 2 or more leaves none. The floor only has to separate those two cases.
MIN_OFF_GRID_SHARE_AT_2X = 0.10
RESEARCH_PARQUET_SUFFIX = "_research.parquet"


class TickScaleError(ValueError):
    """The tick given is not the vendor price grid of these bars."""


@dataclass(frozen=True)
class SessionWindow:
    """Which bars of a trade date form the funnel's trading window."""

    open_minute_ct: int  # O: bars at or after this CT minute
    end_minute_ct: int  # bars strictly before this CT minute (MES: 16:00 halt; else F or C)
    use_flatten_flag: bool = True  # drop bars flagged in_flatten_window (F, early closes)
    # MES: the day's first in-window bar must be exactly at O, else the day is skipped. Stage E
    # (readings R3): the first bar at or after O, whatever its minute.
    require_bar_at_open: bool = True
    # Ruling L-10: only bars on the trade date's own CT calendar day (a booked-forward trade date
    # spans two calendar days; its window never reaches into the booked-in holiday session).
    same_calendar_day: bool = False

    def __post_init__(self) -> None:
        if not 0 <= self.open_minute_ct < self.end_minute_ct <= 24 * 60:
            raise ValueError(f"window [{self.open_minute_ct}, {self.end_minute_ct}) is not a "
                             "non-empty range of CT minutes")


MES_WINDOW = SessionWindow(MES_OPEN_MINUTE_CT, MES_HALT_MINUTE_CT, use_flatten_flag=True)


@dataclass(frozen=True)
class DateRule:
    first: date
    last: date
    allowed_classes: frozenset[str] = frozenset({RESEARCH})
    exclude: frozenset[str] = frozenset()  # ISO trade dates dropped before segmenting

    def __post_init__(self) -> None:
        if self.first > self.last:
            raise ValueError("first trade date after last")
        if not self.allowed_classes <= {RESEARCH, RESEARCH_EMBARGO}:
            raise ValueError(f"only research-window classes may be allowed, not "
                             f"{sorted(self.allowed_classes)}")


# ----------------------------------------------------------------- ticks ----
def to_ticks(prices: np.ndarray, tick: float) -> np.ndarray:
    """Prices (vendor units) -> integer ticks; raises if any price is off the tick grid."""
    if not tick > 0:
        raise ValueError(f"tick {tick!r} must be positive")
    scaled = np.asarray(prices, dtype=float) / tick
    ticks = np.rint(scaled)
    if len(scaled) and np.abs(scaled - ticks).max() > GRID_TOLERANCE_TICKS:
        raise TickScaleError(f"price off the {tick} tick grid")
    return ticks.astype(np.int64)


def off_grid_share(prices: np.ndarray, grid: float) -> float:
    scaled = np.asarray(prices, dtype=float) / grid
    if not len(scaled):
        return 0.0
    return float(np.mean(np.abs(scaled - np.rint(scaled)) > GRID_TOLERANCE_TICKS))


def tick_scale_check(prices: np.ndarray, tick: float) -> dict:
    """The tick must be the price grid (0 prices off it) and the finest one: at 2 x tick at
    least MIN_OFF_GRID_SHARE_AT_2X of prices must be off. Raises ``TickScaleError`` otherwise."""
    at_1x = off_grid_share(prices, tick)
    at_2x = off_grid_share(prices, 2 * tick)
    out = {"tick": tick, "prices_checked": int(len(prices)), "off_grid_share_1x": at_1x,
           "off_grid_share_2x": at_2x, "min_off_grid_share_2x": MIN_OFF_GRID_SHARE_AT_2X}
    if at_1x > 0:
        raise TickScaleError(f"{at_1x:.3%} of prices off the {tick} grid: {out}")
    if at_2x < MIN_OFF_GRID_SHARE_AT_2X:
        raise TickScaleError(f"only {at_2x:.3%} of prices off the 2 x {tick} grid: the vendor "
                             f"tick is coarser than {tick} (cents-quoted product?): {out}")
    return out


def vendor_tick_from_probe(e0_tick: float, grid_scale_probe: dict[str, int]) -> float:
    """BarsCoder's grid_scale_probe (off-grid counts at 1x, 10x, 100x the E.0 tick) -> the
    vendor-unit tick: the E.0 tick times the largest probed factor with no off-grid price."""
    factor = 1
    for key, k in (("x1", 1), ("x10", 10), ("x100", 100)):
        if key not in grid_scale_probe:
            raise KeyError(f"grid_scale_probe lacks {key}")
        if grid_scale_probe[key] == 0:
            factor = k
    if grid_scale_probe["x1"] != 0:
        raise TickScaleError(f"prices off the E.0 tick grid itself: {grid_scale_probe}")
    return e0_tick * factor


# ------------------------------------------------------------------ bars ----
def load_exposure_bars(path: Path, rule: DateRule,
                       columns: Iterable[str] = BAR_COLUMNS) -> pd.DataFrame:
    """A research-window parquet's rows with trade dates in [rule.first, rule.last], re-checked
    against ``rule.allowed_classes`` (holdout, embargo-2 and confirmation dates always refused).
    ``trade_date`` comes back as ISO strings whatever the parquet stores (string or date32)."""
    path = Path(path)
    if not path.name.endswith(RESEARCH_PARQUET_SUFFIX):
        raise ValueError(f"{path.name}: the funnel reads research-window parquets only")
    dataset = pads.dataset(path)
    kind = dataset.schema.field("trade_date").type
    lo, hi = ((rule.first, rule.last) if pa.types.is_date(kind)
              else (rule.first.isoformat(), rule.last.isoformat()))
    field = pads.field("trade_date")
    table = dataset.to_table(columns=list(dict.fromkeys([*columns, "trade_date"])),
                             filter=(field >= lo) & (field <= hi))
    frame = table.to_pandas()
    frame["trade_date"] = frame["trade_date"].astype(str)
    days = {date.fromisoformat(d) for d in frame["trade_date"].unique()}
    refuse_dates_outside(days, rule.allowed_classes, "funnel exposure gate")
    if not frame["ts_event"].is_monotonic_increasing:
        raise ValueError(f"{path.name}: bars not in ts_event order")
    return frame.reset_index(drop=True)


# -------------------------------------------------------------- segments ----
def _day_rows(in_window: np.ndarray, trade_dates: np.ndarray) -> dict[str, np.ndarray]:
    """ISO trade date -> indices of its in-window bars (ascending), days in first-seen order;
    a day with no in-window bar maps to an empty array. One pass instead of one scan per day."""
    codes, uniques = pd.factorize(trade_dates, sort=False)  # first-seen order
    idx = np.flatnonzero(in_window)
    by_day = idx[np.argsort(codes[idx], kind="stable")]
    bounds = np.searchsorted(codes[by_day], np.arange(len(uniques) + 1), side="left")
    return {str(day): by_day[bounds[k]:bounds[k + 1]] for k, day in enumerate(uniques)}


def build_exposure_segment_table(
    bars: pd.DataFrame, segments_per_day: int, *, tick: float, window: SessionWindow,
    rule: DateRule, require_single_instrument: bool = False,
) -> tuple[SegmentTable, dict]:
    """(table in vendor ticks per contract, build report). Pure given ``bars``."""
    if segments_per_day < 1:
        raise ValueError("segments_per_day must be >= 1")
    ts = bars["ts_event"].to_numpy(np.int64)
    if len(ts) > 1 and not (np.diff(ts) > 0).all():
        raise ValueError("bars must be strictly increasing in ts_event")
    trade_dates = bars["trade_date"].astype(str).to_numpy()
    days = {date.fromisoformat(d) for d in set(trade_dates)}
    refuse_dates_outside(days, rule.allowed_classes, "funnel exposure segment table")
    if days and (min(days) < rule.first or max(days) > rule.last):
        raise ValueError(f"bars span {min(days)}..{max(days)}, outside {rule.first}..{rule.last}")

    local = pd.to_datetime(ts, utc=True).tz_convert(CT)
    minute = np.asarray(local.hour * 60 + local.minute)
    in_window = (minute >= window.open_minute_ct) & (minute < window.end_minute_ct)
    if window.same_calendar_day:
        in_window &= np.asarray(pd.Index(local.date).astype(str)) == trade_dates
    if window.use_flatten_flag:
        in_window &= ~bars["in_flatten_window"].to_numpy(bool)
    in_window &= ~np.isin(trade_dates, sorted(rule.exclude))
    prices = np.concatenate([bars[c].to_numpy(float)[in_window]
                             for c in ("open", "high", "low", "close")])
    scale = tick_scale_check(prices, tick) if len(prices) else None
    opens, closes = to_ticks(bars["open"].to_numpy(), tick), to_ticks(bars["close"].to_numpy(),
                                                                       tick)
    lows, highs = to_ticks(bars["low"].to_numpy(), tick), to_ticks(bars["high"].to_numpy(), tick)
    instruments = bars["instrument_id"].to_numpy() if require_single_instrument else None

    kept: list[str] = []
    skipped: dict[str, str] = {}
    rows: list[tuple[list[int], ...]] = []
    for day, idx in _day_rows(in_window, trade_dates).items():
        if day in rule.exclude:
            skipped[day] = "excluded"
            continue
        if len(idx) < segments_per_day:
            skipped[day] = "short"
            continue
        if window.require_bar_at_open and minute[idx[0]] != window.open_minute_ct:
            skipped[day] = "no_bar_at_open"
            continue
        if instruments is not None and len(np.unique(instruments[idx])) != 1:
            skipped[day] = "two_instruments"
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
    if not rows:
        raise ValueError("no trade date survives the window and date rules")

    def column(k: int) -> np.ndarray:
        out = np.array([r[k] for r in rows], dtype=np.int64).reshape(-1, segments_per_day)
        out.flags.writeable = False
        return out

    table = SegmentTable(
        trade_dates=tuple(kept), segments_per_day=segments_per_day, move_ticks=column(0),
        low_ticks=column(1), high_ticks=column(2), entry_minute_ct=column(3),
        exit_minute_ct=column(4), skipped_trade_dates=tuple(skipped))
    report = {"segments_per_day": segments_per_day, "days_kept": len(kept),
              "days_skipped": len(skipped),
              "skipped_by_cause": {c: sum(1 for v in skipped.values() if v == c)
                                   for c in sorted(set(skipped.values()))},
              "first_trade_date": kept[0], "last_trade_date": kept[-1],
              "tick_scale_check": scale}
    return table, report


def mean_abs_move_ticks(table: SegmentTable) -> float:
    """E|m_T|: mean absolute segment move, vendor ticks per contract (the gate's edge scale)."""
    return float(np.abs(table.move_ticks).mean())
