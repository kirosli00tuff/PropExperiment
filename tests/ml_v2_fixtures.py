"""Shared helpers of the ml_route_v2 tests (Task 5 owns this file; another task may add a helper
here and say so in its return). Synthetic data only (ml_route_v2/synthetic.py).

- ``world``: a cached synthetic_universe (one build per argument set and test session).
- ``world_rows`` / ``context``: the decision rows of every bar date without each product's own
  roll-blackout dates (V2.2, pipeline.own_blackout) and a SignalContext over given bars (with
  the per-root blackout map when given; signals.compute_signals applies the leg rule).
- ``perturb_after``: V2.9's perturbation test input: every bar that opens at or after ``cut_ns`` on
  the true clock is randomized (prices and volume; timestamps and trade dates kept). A root whose
  labels are shifted (``shift_minutes``) is cut on its true clock, and a planted ``leak_fwd``
  column is recomputed from the randomized closes.
- ``perturbation_check``: features at every row with decision_ts_ns <= cut must not change when
  the bars after the cut are randomized; raises ``PerturbationLeak`` naming the columns that did.
- Peeking normalizers (test-only, deliberately wrong) and ``normalizer_check``: a normalizer's
  statistics for a row must not move when later rows' raw values are perturbed.
"""

from __future__ import annotations

import pickle
from collections.abc import Callable, Mapping, Sequence
from datetime import date
from typing import Any

import numpy as np
import pandas as pd

from ml_route_v2.clock import decision_rows, trade_dates_of
from ml_route_v2.constants import UNIVERSE, Z_CLIP
from ml_route_v2.pipeline import own_blackout
from ml_route_v2.signals import SignalContext
from ml_route_v2.synthetic import NS_MIN, SyntheticWorld, leak_column, synthetic_universe
from ml_route_v2.targets import sigma_d

PRICE_JITTER = 0.05  # +-5% multiplicative noise on every randomized price


class PerturbationLeak(AssertionError):
    """A value at t changed when only bars opening at or after t were randomized."""


_WORLDS: dict[bytes, SyntheticWorld] = {}


def world(roots: Sequence[str], first: date, last: date, *, seed: int,
          plant: Mapping | Sequence[Mapping] | None = None, **kwargs: Any) -> SyntheticWorld:
    """A cached synthetic_universe (same arguments, same object, within one test session)."""
    key = pickle.dumps((tuple(roots), first, last, int(seed), plant, sorted(kwargs.items())))
    if key not in _WORLDS:
        _WORLDS[key] = synthetic_universe(roots, first, last, seed=seed, plant=plant, **kwargs)
    return _WORLDS[key]


def world_rows(w: SyntheticWorld) -> pd.DataFrame:
    vs = tuple(w.vehicles)
    return decision_rows(vs, {v: trade_dates_of(w.bars[UNIVERSE[v][1]]) for v in vs},
                         exclude=own_blackout(w.blackout, vs))


def context(rows: pd.DataFrame, bars: Mapping[str, pd.DataFrame], releases: Any,
            blackout: Mapping[str, frozenset[date]] | None = None) -> SignalContext:
    return SignalContext(rows, bars, releases, sigma_d(rows, bars), blackout=blackout or {})


def perturb_after(bars: Mapping[str, pd.DataFrame], cut_ns: int, *, seed: int,
                  shift_minutes: Mapping[str, int] | None = None,
                  leak_minutes: int = 60) -> dict[str, pd.DataFrame]:
    """Copies of ``bars`` whose bars opening at or after ``cut_ns`` (true clock) are randomized."""
    rng = np.random.default_rng(seed)
    out = {}
    for root, frame in bars.items():
        label_cut = cut_ns + int((shift_minutes or {}).get(root, 0)) * NS_MIN
        ts = frame["ts_event"].to_numpy(np.int64)
        after = ts >= label_cut
        new = frame.copy()
        if after.any():
            n = int(after.sum())
            prices = {c: frame[c].to_numpy(np.float64).copy() for c in ("open", "high", "low",
                                                                         "close")}
            for c in prices:
                prices[c][after] *= 1.0 + rng.uniform(-PRICE_JITTER, PRICE_JITTER, size=n)
            hi = np.maximum.reduce([prices[c] for c in prices])
            lo = np.minimum.reduce([prices[c] for c in prices])
            prices["high"], prices["low"] = hi, lo
            for c, v in prices.items():
                new[c] = v
            vol = frame["volume"].to_numpy().copy()
            vol[after] = rng.integers(1, 400, size=n).astype(vol.dtype)
            new["volume"] = vol
            if "leak_fwd" in frame.columns:
                new["leak_fwd"] = leak_column(ts, prices["close"], leak_minutes)
        out[root] = new
    return out


def _changed(a: pd.DataFrame, b: pd.DataFrame, mask: np.ndarray) -> list[str]:
    bad = []
    for col in a.columns:
        x = a[col].to_numpy(np.float64)[mask]
        y = b[col].to_numpy(np.float64)[mask]
        same = (x == y) | (np.isnan(x) & np.isnan(y))
        if not same.all():
            bad.append(f"{col} ({int((~same).sum())} rows)")
    return bad


def perturbation_check(w: SyntheticWorld, features: Callable[[SignalContext], pd.DataFrame],
                       cuts: Sequence[int], *, seed: int = 1,
                       shift_minutes: Mapping[str, int] | None = None,
                       bars: Mapping[str, pd.DataFrame] | None = None) -> int:
    """Raise PerturbationLeak if a feature at a row with decision_ts_ns <= cut changes when the
    bars opening at or after the cut are randomized. Returns the number of rows compared."""
    rows = world_rows(w)
    src = w.bars if bars is None else bars
    base = features(context(rows, src, w.releases))
    t = rows["decision_ts_ns"].to_numpy(np.int64)
    compared = 0
    leaks = []
    for k, cut in enumerate(cuts):
        moved = perturb_after(src, int(cut), seed=seed + k, shift_minutes=shift_minutes)
        got = features(context(rows, moved, w.releases))
        mask = t <= int(cut)
        compared += int(mask.sum())
        bad = _changed(base, got, mask)
        if bad:
            leaks.append(f"cut {int(cut)}: {', '.join(bad[:6])}")
    if leaks:
        raise PerturbationLeak("features at t moved with bars after t: " + "; ".join(leaks))
    return compared


def cuts_of_date(w: SyntheticWorld, day: date) -> list[int]:
    """Every decision time (UTC ns) of ``day`` across the world's vehicles."""
    rows = world_rows(w)
    on = pd.to_datetime(rows["trade_date"]).dt.date == day
    return sorted({int(x) for x in rows.loc[on.to_numpy(), "decision_ts_ns"]})


# ------------------------------------------------------------------ normalizers ----
def _per_root(raw: pd.DataFrame, rows: pd.DataFrame, cols: Sequence[str],
              stat: Callable[[np.ndarray, np.ndarray, int], tuple[float, float]]) -> pd.DataFrame:
    out = np.full((len(raw), len(cols)), np.nan)
    x_all = raw[list(cols)].to_numpy(np.float64)
    days = rows["trade_date"].to_numpy().astype("datetime64[D]").astype(np.int64)
    root = rows["root"].to_numpy(object)
    for r in pd.unique(root):
        sel = np.flatnonzero(root == r)
        for i in sel:
            for j in range(len(cols)):
                m, s = stat(x_all[sel, j], days[sel], int(days[i]))
                if np.isfinite(s) and s > 0:
                    out[i, j] = np.clip((x_all[i, j] - m) / s, -Z_CLIP, Z_CLIP)
    return pd.DataFrame(out, index=raw.index, columns=list(cols))


def zscore_peek_future(raw: pd.DataFrame, rows: pd.DataFrame, cols: Sequence[str]
                       ) -> pd.DataFrame:
    """WRONG on purpose: mean and sd over every date of the product, later dates included."""
    return _per_root(raw, rows, cols, lambda x, d, day: (np.nanmean(x), np.nanstd(x, ddof=1)))


def zscore_peek_today(raw: pd.DataFrame, rows: pd.DataFrame, cols: Sequence[str]
                      ) -> pd.DataFrame:
    """WRONG on purpose: the trailing window includes the current date's rows."""
    def stat(x: np.ndarray, d: np.ndarray, day: int) -> tuple[float, float]:
        win = x[d <= day]
        return float(np.nanmean(win)), float(np.nanstd(win, ddof=1))
    return _per_root(raw, rows, cols, stat)


def normalizer_check(fn: Callable[..., pd.DataFrame], raw: pd.DataFrame, rows: pd.DataFrame,
                     cols: Sequence[str], moved: pd.DataFrame, compare: np.ndarray,
                     **kwargs: Any) -> None:
    """Raise PerturbationLeak if fn's value on a ``compare`` row changes between ``raw`` and
    ``moved`` (whose difference lies only in rows a causal normalizer may not read for them)."""
    a = fn(raw, rows, cols, **kwargs)
    b = fn(moved, rows, cols, **kwargs)
    bad = _changed(a, b, compare)
    if bad:
        raise PerturbationLeak("normalized values moved with later raw values: " + ", ".join(bad))


def raw_rows(n_dates: int = 90, roots: Sequence[str] = ("MNQ", "MGC"), seed: int = 5
             ) -> tuple[pd.DataFrame, pd.DataFrame]:
    """A DecisionRows-shaped frame (root, trade_date, t_index, decision_ts_ns) and raw values."""
    rng = np.random.default_rng(seed)
    days = pd.bdate_range("2021-01-04", periods=n_dates)
    recs = [(r, d, k) for d in days for r in roots for k in (1, 2, 3)]
    rows = pd.DataFrame(recs, columns=["root", "trade_date", "t_index"])
    rows["trade_date"] = pd.to_datetime(rows["trade_date"]).astype("datetime64[ns]")
    rows["decision_ts_ns"] = (rows["trade_date"].astype("int64")
                              + rows["t_index"].astype("int64") * 3_600_000_000_000)
    raw = pd.DataFrame({"f1": rng.standard_normal(len(rows)),
                        "f2": rng.standard_normal(len(rows)) * 3 + 1}, index=rows.index)
    return rows, raw


__all__ = [
    "PerturbationLeak", "context", "cuts_of_date", "normalizer_check", "perturb_after",
    "perturbation_check", "raw_rows", "world", "world_rows", "zscore_peek_future",
    "zscore_peek_today",
]
