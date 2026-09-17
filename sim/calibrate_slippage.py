"""Calibrate MES market-order slippage by CT time of day from existing mbp-10 data.

    uv run python -m sim.calibrate_slippage

Inputs (read IN PLACE, read-only, already paid for — not re-purchased, not copied):
MLCryptoEngine/data/vendor/databento/GLBX.MDP3/date={2026-07-15,2026-07-31}/MES_c_0.mbp-10.dbn.zst

Method:
1. Stream the book (bounded memory); verify ts_recv is monotone (ported check).
2. Sample the 10-level book once per second on a uniform clock (last update at or
   before each second; book state persists between updates). Uniform-time sampling
   models an order arriving at an arbitrary moment, e.g. a bar close.
3. Drop seconds in scheduled closures, within the 1 s reopen-auction grace, and
   any crossed/locked/empty book.
4. For each size q in SIZES, walk the ask (buy) and bid (sell) side:
   slippage_ticks = |VWAP fill - mid| / 0.25, averaged over the two sides. A size
   that exceeds the visible 10 levels is counted as ``insufficient_depth``.
5. Aggregate by 15-minute CT bucket and by named window.

What this does NOT include (stated, not implied): latency/adverse selection
between decision and fill, queue position, hidden liquidity, and news spikes
beyond these two days. Two days is a small sample.
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, date, datetime

import numpy as np
import pandas as pd

from data.config import REPO_ROOT
from data.session import CME_TZ, closed_windows_range_ns
from data.validate import in_windows

MLCE_VENDOR = REPO_ROOT.parent / "MLCryptoEngine" / "data" / "vendor" / "databento" / "GLBX.MDP3"
DATES = ("2026-07-15", "2026-07-31")
OUT_PATH = REPO_ROOT / "sim" / "slippage_calibration.json"
SIZES = (1, 5, 10, 20, 50)  # micros; 50 = 5-mini cap on 50K
LEVELS = 10
NS = 1_000_000_000
TICK_FIXED = 250_000_000
NULL_PRICE = 9_223_372_036_854_775_807
REOPEN_GRACE_S = 1
BUCKET_MINUTES = 15
WINDOWS = {  # CT minutes-of-day, [start, end)
    "open_0830_0900": (8 * 60 + 30, 9 * 60),
    "midday_1100_1300": (11 * 60, 13 * 60),
    "close_1430_1510": (14 * 60 + 30, 15 * 60 + 10),
    "overnight_1700_0830": None,  # 17:00-24:00 and 00:00-08:30
}


def _sample_seconds(path) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, int]]:  # noqa: ANN001
    """Last book per second: (seconds, prices[n, 2*LEVELS], sizes[n, 2*LEVELS], stats)."""
    import databento

    store = databento.DBNStore.from_file(path)
    px_cols = [f"{side}_px_{i:02d}" for side in ("bid", "ask") for i in range(LEVELS)]
    sz_cols = [f"{side}_sz_{i:02d}" for side in ("bid", "ask") for i in range(LEVELS)]
    secs, pxs, szs = [], [], []
    records, regressions, prev_last = 0, 0, None
    for chunk in store.to_ndarray(count=500_000):
        recv = chunk["ts_recv"].astype(np.int64)
        records += recv.size
        regressions += int((np.diff(recv) < 0).sum())
        if prev_last is not None and recv[0] < prev_last:
            regressions += 1
        prev_last = int(recv[-1])
        sec = recv // NS
        last = np.flatnonzero(np.append(np.diff(sec) != 0, True))
        secs.append(sec[last])
        pxs.append(np.stack([chunk[c][last].astype(np.int64) for c in px_cols], axis=1))
        szs.append(np.stack([chunk[c][last].astype(np.int64) for c in sz_cols], axis=1))
    sec = np.concatenate(secs)
    keep = np.append(np.diff(sec) != 0, True)  # a second split across chunks: keep the last
    return (sec[keep], np.concatenate(pxs)[keep], np.concatenate(szs)[keep],
            {"records": records, "ts_recv_regressions": regressions})


def _walk(prices: np.ndarray, sizes: np.ndarray, qty: int) -> np.ndarray:
    """VWAP (fixed-point) to fill ``qty`` walking levels in order; NaN if too thin."""
    remaining = np.full(prices.shape[0], qty, dtype=np.int64)
    cost = np.zeros(prices.shape[0], dtype=np.float64)
    for lvl in range(prices.shape[1]):
        valid = prices[:, lvl] != NULL_PRICE
        take = np.where(valid, np.minimum(remaining, sizes[:, lvl]), 0)
        cost += take * prices[:, lvl].astype(np.float64)
        remaining -= take
    vwap = cost / qty
    vwap[remaining > 0] = np.nan
    return vwap


def calibrate_day(day: str) -> tuple[pd.DataFrame, dict]:
    path = MLCE_VENDOR / f"date={day}" / "MES_c_0.mbp-10.dbn.zst"
    upd_sec, px, sz, stats = _sample_seconds(path)
    d = date.fromisoformat(day)
    start = int(datetime(d.year, d.month, d.day, tzinfo=UTC).timestamp())
    grid = np.arange(start, start + 86_400, dtype=np.int64)
    pos = np.searchsorted(upd_sec, grid, side="right") - 1
    grid, pos = grid[pos >= 0], pos[pos >= 0]

    closed = closed_windows_range_ns(d, d)
    starts = np.array([a for a, _ in closed], dtype=np.int64)
    ends = np.array([b + REOPEN_GRACE_S * NS for _, b in closed], dtype=np.int64)
    open_mask = ~in_windows(grid * NS, starts, ends)
    grid, pos = grid[open_mask], pos[open_mask]
    book_px, book_sz = px[pos], sz[pos]
    bid, ask = book_px[:, 0], book_px[:, LEVELS]
    good = (bid != NULL_PRICE) & (ask != NULL_PRICE) & (ask > bid)
    stats["seconds_open"] = int(grid.size)
    stats["seconds_bad_book"] = int((~good).sum())
    grid, book_px, book_sz = grid[good], book_px[good], book_sz[good]
    bid, ask = bid[good], ask[good]
    mid = (bid + ask) / 2.0

    local = pd.to_datetime(grid * NS, utc=True).tz_convert(CME_TZ)
    minute_of_day = local.hour * 60 + local.minute
    frame = pd.DataFrame({
        "date": day,
        "minute_of_day": minute_of_day,
        "half_spread_ticks": (ask - bid) / 2.0 / TICK_FIXED,
    })
    for q in SIZES:
        buy = _walk(book_px[:, LEVELS:], book_sz[:, LEVELS:], q)
        sell = _walk(book_px[:, :LEVELS], book_sz[:, :LEVELS], q)
        frame[f"slip_{q}"] = ((buy - mid) + (mid - sell)) / 2.0 / TICK_FIXED
    return frame, stats


def _window_of(minute: int) -> str:
    for name, bounds in WINDOWS.items():
        if bounds is not None and bounds[0] <= minute < bounds[1]:
            return name
    if minute >= 17 * 60 or minute < 8 * 60 + 30:
        return "overnight_1700_0830"
    return "other_rth"


def _stats(group: pd.DataFrame) -> dict:
    out = {"samples_s": int(len(group)), "days": sorted(group["date"].unique().tolist()),
           "half_spread_ticks_mean": round(float(group["half_spread_ticks"].mean()), 4)}
    for q in SIZES:
        col = group[f"slip_{q}"]
        out[str(q)] = {
            "mean": round(float(col.mean()), 4),
            "p50": round(float(col.median()), 4),
            "p90": round(float(col.quantile(0.90)), 4),
            "p99": round(float(col.quantile(0.99)), 4),
            "insufficient_depth": int(col.isna().sum()),
        }
    return out


def main() -> int:
    frames, day_stats = [], {}
    for day in DATES:
        frame, stats = calibrate_day(day)
        frames.append(frame)
        day_stats[day] = stats
        print(day, stats, flush=True)
    data = pd.concat(frames, ignore_index=True)
    data["bucket"] = data["minute_of_day"] // BUCKET_MINUTES * BUCKET_MINUTES
    data["window"] = data["minute_of_day"].map(_window_of)
    payload = {
        "generated_utc": datetime.now(UTC).isoformat(),
        "source_files": [str(MLCE_VENDOR / f"date={d}" / "MES_c_0.mbp-10.dbn.zst") for d in DATES],
        "method": "uniform 1s sampling of 10-level book; slippage vs mid, avg of buy/sell sides; "
                  "excludes latency/adverse selection/queue effects",
        "tick_size": 0.25, "tick_value_usd": 1.25, "sizes_micros": list(SIZES),
        "bucket_minutes": BUCKET_MINUTES,
        "day_stats": day_stats,
        "windows": {w: _stats(g) for w, g in data.groupby("window")},
        "buckets_ct": {
            f"{b // 60:02d}:{b % 60:02d}": _stats(g) for b, g in data.groupby("bucket")
        },
    }
    OUT_PATH.write_text(json.dumps(payload, indent=1))
    for w, s in payload["windows"].items():
        print(w, s["samples_s"], "hs", s["half_spread_ticks_mean"],
              {q: (s[str(q)]["mean"], s[str(q)]["p90"], s[str(q)]["insufficient_depth"])
               for q in SIZES})
    return 0 if all(v["ts_recv_regressions"] == 0 for v in day_stats.values()) else 3


if __name__ == "__main__":
    sys.exit(main())
