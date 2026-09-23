"""MES 1-minute continuous series: load immutable raw DBN, attach session flags.

Flags live as COLUMNS on the bar table (documented in the Parquet schema
metadata under ``propexperiment``), never as side files:

- ``trade_date``           CME trade date (sessions reopening 17:00 CT roll forward).
- ``instrument_id``/``raw_symbol``  the contract the continuous series held (Stage D.1f
                           confirmation build: the MES outright symbology maps the id to on
                           the bar's UTC date, ``raw_symbols_on_bar_dates``).
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

import re
from collections.abc import Iterable, Mapping, Sequence
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from data.adapter import RollBoundary
from data.cme_calendar import assert_calendar_coverage
from data.session import CME_TZ, early_halt_ct, trade_date
from data.validate import in_windows
from rules.xfa_rules import flatten_time_ct, no_new_positions_time_ct

PRICE_SCALE = 1_000_000_000
MES_TICK_FIXED = 250_000_000  # 0.25 in Databento fixed-point
NS_PER_MIN = 60 * 1_000_000_000
NS_PER_DAY = 86_400 * 1_000_000_000
# An MES outright: MES, a futures month letter, a single year digit (list 1.1, D-4).
MES_OUTRIGHT = re.compile(r"MES[FGHJKMNQUVXZ][0-9]")
_EPOCH = date(1970, 1, 1)


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


def is_mes_outright(symbol: str) -> bool:
    return MES_OUTRIGHT.fullmatch(symbol) is not None


def raw_symbols_on_bar_dates(
    ts: np.ndarray,
    instrument_ids: np.ndarray,
    raw_intervals: Mapping[str, Sequence[Mapping[str, Any]]],
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    """Stage D.1f raw-symbol rule (reports/stage_d1f_confirmation_list.md 1.1, D-4).

    For each bar: the MES outright that symbology maps its ``instrument_id`` to ON THE BAR'S
    DATE (the UTC date of ``ts_event``: symbology intervals ``[d0, d1)`` are UTC dates, and the
    continuous series splices at 00:00 UTC). ``raw_intervals`` is symbology.resolve's
    instrument_id -> raw_symbol ``result``. A bar whose id maps to no MES outright that day
    gets ``""`` (the caller drops it); the second return value lists every such
    (UTC date, instrument_id) with its bar count and the symbols that DID map, so every drop is
    logged. Two different MES outrights on one id and date raise: that is not a drop case."""
    days = np.asarray(ts, dtype=np.int64) // NS_PER_DAY
    ids = np.asarray(instrument_ids, dtype=np.int64)
    pairs, inverse, counts = np.unique(np.stack([ids, days], axis=1), axis=0,
                                       return_inverse=True, return_counts=True)
    symbols: list[str] = []
    unmapped: list[dict[str, Any]] = []
    for (iid, day_num), count in zip(pairs.tolist(), counts.tolist(), strict=True):
        day = (_EPOCH + timedelta(days=int(day_num))).isoformat()
        mapped = sorted({str(e["s"]) for e in raw_intervals.get(str(iid), [])
                         if str(e["d0"]) <= day < str(e["d1"])})
        outrights = [s for s in mapped if is_mes_outright(s)]
        if len(outrights) > 1:
            raise ValueError(f"instrument {iid} maps to several MES outrights on {day}: "
                             f"{outrights}")
        symbols.append(outrights[0] if outrights else "")
        if not outrights:
            unmapped.append({"utc_date": day, "instrument_id": int(iid), "bars": int(count),
                             "mapped_symbols": mapped})
    return np.array(symbols, dtype=object)[inverse.reshape(-1)], unmapped


def bar_trade_dates(ts: np.ndarray) -> list[date]:
    """CME trade date of every bar (data.session.trade_date), computed once per minute."""
    minutes = np.asarray(ts, dtype=np.int64) // NS_PER_MIN * NS_PER_MIN
    minute_to_tdate = {m: trade_date(int(m)) for m in np.unique(minutes)}
    return [minute_to_tdate[m] for m in minutes]


def add_flags(
    bars: pd.DataFrame,
    rolls: list[RollBoundary],
    closed_starts: np.ndarray,
    closed_ends: np.ndarray,
    gap_before: np.ndarray,
    degraded_utc_dates: set[str],
    raw_symbols: np.ndarray | None = None,
) -> pd.DataFrame:
    """Return a NEW frame with prices in points and every documented flag.

    ``raw_symbols`` (Stage D.1f): the per-bar symbols of ``raw_symbols_on_bar_dates``; when
    omitted, the Stage A.1 rule (the roll boundaries' raw symbol per instrument) applies.
    Every built trade date must lie inside ``CALENDAR_COVERAGE``, or this raises."""
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
    if raw_symbols is None:
        raw = instrument_raw_symbols(rolls)
        out["raw_symbol"] = out["instrument_id"].map(raw).fillna("")
    else:
        if len(raw_symbols) != len(out):
            raise ValueError(f"{len(raw_symbols)} raw symbols for {len(out)} bars")
        out["raw_symbol"] = np.asarray(raw_symbols, dtype=object)

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

    out["trade_date"] = bar_trade_dates(ts)
    assert_calendar_coverage(set(out["trade_date"]))  # every built trade date (list 5.3)
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
