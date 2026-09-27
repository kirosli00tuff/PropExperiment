"""The LSTM's inputs (M3 with ruling ML-A12): clock-aligned 5-minute bars and per-row sequences.

A 5-minute bar covers [xx:00, xx:05), [xx:05, xx:10), ... (UTC and CT clocks agree to the
minute), built from the one-minute bars of one trade date inside it: open = first open, close =
last close, high/low = extremes, volume = sum. A row at decision time t reads the last
``lookback`` 5-minute bars of its trade date that END at or before t (the last one-minute bar
inside closes at or before t), never crossing the trade date's first bar; shorter sequences are
padded and masked (``lengths``; padded steps never reach the final hidden state).

Step inputs: normalized open-to-close return and high-low range (vehicle ticks / sigma_X,d of the
row's date) and the log volume ratio: log of the step's volume over the median volume of the same
5-minute clock slot on the product's 20 previous trade dates (a date with no bar in the slot counts
as zero volume). Reading (worker report): where that ratio is undefined (fewer than 20 previous
dates, or a zero median) the row's LSTM input is missing and, by M4's missing-input rule, the row
is excluded from the LSTM's sets for that lookback (``counts['lstm_step_undefined']``).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from ml_route.constants import FIVE_MIN, SIGMA_LOOKBACK_DATES
from ml_route.features import Bars

NS_MIN = 60_000_000_000
SLOT_NS = FIVE_MIN * NS_MIN


@dataclass(frozen=True)
class FiveMinBars:
    root: str
    end_ns: np.ndarray  # slot end (open + 5 min)
    trade_date: np.ndarray  # datetime64[D]
    oc_ticks: np.ndarray  # (close - open) in vehicle ticks
    hl_ticks: np.ndarray  # (high - low) in vehicle ticks
    log_vol_ratio: np.ndarray  # NaN where undefined
    date_first: np.ndarray  # index of the first 5-minute bar of each bar's trade date


def five_minute_bars(bars: Bars, per_unit: float) -> FiveMinBars:
    slot = (bars.ts // SLOT_NS) * SLOT_NS
    frame = pd.DataFrame({"d": bars.trade_date, "s": slot, "o": bars.open, "h": bars.high,
                          "l": bars.low, "c": bars.close, "v": bars.volume})
    g = frame.groupby(["d", "s"], sort=True)
    agg = g.agg(o=("o", "first"), h=("h", "max"), l=("l", "min"), c=("c", "last"),
                v=("v", "sum")).reset_index()
    days = agg["d"].to_numpy().astype("datetime64[D]")
    starts = agg["s"].to_numpy(np.int64)
    ct = pd.to_datetime(starts, utc=True).tz_convert("America/Chicago")
    clock = (ct.hour * 60 + ct.minute).to_numpy()
    wide = pd.DataFrame({"d": days, "k": clock, "v": agg["v"].to_numpy(np.float64)}).pivot_table(
        index="d", columns="k", values="v", aggfunc="sum", fill_value=0.0).sort_index()
    med = wide.rolling(SIGMA_LOOKBACK_DATES, min_periods=SIGMA_LOOKBACK_DATES).median().shift(1)
    date_pos = np.searchsorted(wide.index.to_numpy().astype("datetime64[D]"), days)
    col_pos = np.searchsorted(wide.columns.to_numpy(), clock)
    base = med.to_numpy()[date_pos, col_pos]
    vol = agg["v"].to_numpy(np.float64)
    ratio = np.full(len(vol), np.nan)
    good = np.isfinite(base) & (base > 0) & (vol > 0)
    ratio[good] = np.log(vol[good] / base[good])
    _, first_of_date = np.unique(days, return_index=True)
    date_first = first_of_date[np.searchsorted(np.unique(days), days)]
    return FiveMinBars(bars.root, starts + SLOT_NS, days,
                       (agg["c"].to_numpy() - agg["o"].to_numpy()) * per_unit,
                       (agg["h"].to_numpy() - agg["l"].to_numpy()) * per_unit, ratio, date_first)


@dataclass(frozen=True)
class SequenceIndex:
    """Where each row's sequence sits in its product's 5-minute arrays."""

    end: np.ndarray  # index of the last 5-minute bar (inclusive); -1 = no sequence
    length: np.ndarray  # number of steps (1..lookback)


def sequence_index(fb: FiveMinBars, day: np.ndarray, t_ns: np.ndarray, lookback: int
                   ) -> SequenceIndex:
    end = np.searchsorted(fb.end_ns, t_ns, side="right") - 1
    ok = end >= 0
    e = np.clip(end, 0, None)
    ok &= fb.trade_date[e] == day
    start = np.maximum(e - lookback + 1, fb.date_first[e])
    length = np.where(ok, e - start + 1, 0)
    return SequenceIndex(np.where(ok, end, -1), length)


def steps_defined(fb: FiveMinBars, idx: SequenceIndex) -> np.ndarray:
    """True where the row has a sequence and every step's inputs are defined."""
    out = idx.end >= 0
    finite = np.isfinite(fb.log_vol_ratio)
    bad_prefix = np.concatenate([[0], np.cumsum(~finite)])
    lo = idx.end - idx.length + 1
    ok = out.copy()
    ok[out] = (bad_prefix[idx.end[out] + 1] - bad_prefix[lo[out]]) == 0
    return ok


def gather(fb: FiveMinBars, idx: SequenceIndex, rows: np.ndarray, sigma: np.ndarray,
           lookback: int) -> tuple[np.ndarray, np.ndarray]:
    """(sequences float32 (n, lookback, 3), lengths int64) for ``rows``, right-padded with
    zeros after each sequence's last step (masked by ``lengths``)."""
    n = len(rows)
    out = np.zeros((n, lookback, 3), dtype=np.float32)
    lengths = idx.length[rows].astype(np.int64)
    if np.any(lengths < 1):
        raise ValueError("a row without a sequence reached the LSTM batch")
    ends = idx.end[rows]
    steps = np.arange(lookback)
    src = (ends - lengths + 1)[:, None] + steps[None, :]
    valid = steps[None, :] < lengths[:, None]
    src = np.where(valid, src, 0)
    sig = sigma[rows][:, None]
    out[..., 0] = np.where(valid, fb.oc_ticks[src] / sig, 0.0)
    out[..., 1] = np.where(valid, fb.hl_ticks[src] / sig, 0.0)
    out[..., 2] = np.where(valid, fb.log_vol_ratio[src], 0.0)
    return out, lengths
