"""MES 1-minute continuous series: load immutable raw DBN, attach session flags.

Flags live as COLUMNS on the bar table (documented in the Parquet schema
metadata under ``propexperiment``), never as side files:

- ``trade_date``           CME trade date (sessions reopening 17:00 CT roll forward).
- ``instrument_id``/``raw_symbol``  the contract the continuous series held.
- ``is_roll_session``      the trade date contains a vendor splice (unadjusted prices).
- ``in_scheduled_closure`` bar start falls inside the calendar's closed windows
                           (daily 16:00-17:00 CT halt, weekend, holidays). Expected: never.
- ``in_flatten_window``    bar start >= the Topstep flatten (15:10 CT, or 15 min before a
                           CME early close) and < 17:00 CT. No position may be held.
- ``in_no_new_positions_window``  bar start >= 15:08 CT (2 min before the flatten).
- ``early_halt_ct``        the CME early halt time for that CT date, if any ("" otherwise).
- ``gap_before_minutes``   expected-open minutes with NO bar immediately before this bar.
                           Gaps are flagged, never filled.
- ``vendor_degraded_day``  Databento reports reduced quality for this UTC date.

Bar timestamp convention: ``ts_event`` is the bar OPEN (UTC ns); the 15:09 CT bar
covers [15:09, 15:10) and is the last bar before the flatten.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from data.adapter import RollBoundary
from data.session import CME_TZ, early_halt_ct, trade_date
from data.validate import in_windows
from rules.xfa_rules import flatten_time_ct, no_new_positions_time_ct

PRICE_SCALE = 1_000_000_000
MES_TICK_FIXED = 250_000_000  # 0.25 in Databento fixed-point
NS_PER_MIN = 60 * 1_000_000_000


def load_raw_bars(paths: Iterable[Path]) -> pd.DataFrame:
    """Concatenate raw ohlcv-1m DBN files in file order. No sorting, no dedup:
    ordering and duplicates are for the validator to find, not to hide."""
    import databento  # lazy

    frames = []
    for path in paths:
        store = databento.DBNStore.from_file(path)
        for arr in store.to_ndarray(count=1_000_000):
            frames.append(
                pd.DataFrame(
                    {
                        "ts_event": arr["ts_event"].astype(np.int64),
                        "instrument_id": arr["instrument_id"].astype(np.int64),
                        "open_fixed": arr["open"].astype(np.int64),
                        "high_fixed": arr["high"].astype(np.int64),
                        "low_fixed": arr["low"].astype(np.int64),
                        "close_fixed": arr["close"].astype(np.int64),
                        "volume": arr["volume"].astype(np.int64),
                        "source_file": path.name,
                    }
                )
            )
    return pd.concat(frames, ignore_index=True)


def instrument_raw_symbols(rolls: list[RollBoundary]) -> dict[int, str]:
    out: dict[int, str] = {}
    for r in rolls:
        if r.from_raw_symbol:
            out[int(r.from_instrument)] = r.from_raw_symbol
        if r.to_raw_symbol:
            out[int(r.to_instrument)] = r.to_raw_symbol
    return out


def add_flags(
    bars: pd.DataFrame,
    rolls: list[RollBoundary],
    closed_starts: np.ndarray,
    closed_ends: np.ndarray,
    gap_before: np.ndarray,
    degraded_utc_dates: set[str],
) -> pd.DataFrame:
    """Return a NEW frame with prices in points and every documented flag."""
    ts = bars["ts_event"].to_numpy()
    out = pd.DataFrame(
        {
            "ts_event": ts,
            "open": bars["open_fixed"].to_numpy() / PRICE_SCALE,
            "high": bars["high_fixed"].to_numpy() / PRICE_SCALE,
            "low": bars["low_fixed"].to_numpy() / PRICE_SCALE,
            "close": bars["close_fixed"].to_numpy() / PRICE_SCALE,
            "volume": bars["volume"].to_numpy(),
            "instrument_id": bars["instrument_id"].to_numpy(),
        }
    )
    raw = instrument_raw_symbols(rolls)
    out["raw_symbol"] = out["instrument_id"].map(raw).fillna("")

    local = pd.to_datetime(ts, utc=True).tz_convert(CME_TZ)
    local_date = local.date
    local_minutes = local.hour * 60 + local.minute
    unique_dates = sorted(set(local_date))
    halt_by_date = {d: early_halt_ct(d) for d in unique_dates}
    flat_min = {d: _minutes(flatten_time_ct(halt_by_date[d])) for d in unique_dates}
    nonew_min = {d: _minutes(no_new_positions_time_ct(halt_by_date[d])) for d in unique_dates}
    reopen = 17 * 60
    flatten_start = np.array([flat_min[d] for d in local_date])
    nonew_start = np.array([nonew_min[d] for d in local_date])
    before_reopen = local_minutes < reopen
    out["in_flatten_window"] = before_reopen & (local_minutes >= flatten_start)
    out["in_no_new_positions_window"] = before_reopen & (local_minutes >= nonew_start)
    out["early_halt_ct"] = [
        halt_by_date[d].strftime("%H:%M") if halt_by_date[d] else "" for d in local_date
    ]

    out["in_scheduled_closure"] = in_windows(ts, closed_starts, closed_ends)

    minute_to_tdate = {m: trade_date(int(m)) for m in np.unique(ts // NS_PER_MIN * NS_PER_MIN)}
    out["trade_date"] = [minute_to_tdate[m] for m in ts // NS_PER_MIN * NS_PER_MIN]
    roll_dates = {trade_date(r.ts_ns) for r in rolls}
    out["is_roll_session"] = out["trade_date"].isin(roll_dates)
    out["gap_before_minutes"] = gap_before
    utc_dates = pd.to_datetime(ts, utc=True).strftime("%Y-%m-%d")
    out["vendor_degraded_day"] = np.isin(utc_dates, sorted(degraded_utc_dates))
    return out


def _minutes(at) -> int:  # noqa: ANN001 — datetime.time
    return at.hour * 60 + at.minute


def trade_dates_of(bars: pd.DataFrame) -> list[date]:
    return sorted(set(bars["trade_date"]))
