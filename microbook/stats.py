"""Descriptive statistics of a daily $ P&L series (lead_spec_B.md S5). No p-value anywhere."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

ANNUAL_DAYS = 252  # E.21 / S7 convention (mean / sd x sqrt(252))
BOOT_BLOCK = 21
BOOT_DRAWS = 10_000
BOOT_LENGTH = 252
BOOT_SEED = 20261016
BOOT_PCTS = (95.0, 99.0)


def sharpe(x: np.ndarray) -> float | None:
    x = np.asarray(x, dtype=float)
    if len(x) < 2:
        return None
    sd = float(x.std(ddof=1))
    return None if sd == 0 else float(x.mean() / sd * math.sqrt(ANNUAL_DAYS))


def annual(x: np.ndarray) -> tuple[float, float]:
    x = np.asarray(x, dtype=float)
    return float(x.mean() * ANNUAL_DAYS), float(x.std(ddof=1) * math.sqrt(ANNUAL_DAYS))


def max_drawdown(x: np.ndarray, dates: pd.DatetimeIndex) -> dict:
    """Largest peak-to-trough fall of the cumulative series (the start counts as a peak at 0)."""
    cum = np.concatenate([[0.0], np.cumsum(np.asarray(x, dtype=float))])
    peak = np.maximum.accumulate(cum)
    dd = peak - cum
    j = int(np.argmax(dd))
    i = int(np.argmax(cum[: j + 1])) if j > 0 else 0
    d_of = lambda k: None if k == 0 else str(dates[k - 1].date())  # noqa: E731
    return {"max_dd": float(dd[j]), "peak_date": d_of(i) or str(dates[0].date()),
            "trough_date": d_of(j) or str(dates[0].date())}


def block_bootstrap_mdd(x: np.ndarray, *, block: int = BOOT_BLOCK, draws: int = BOOT_DRAWS,
                        length: int = BOOT_LENGTH, seed: int = BOOT_SEED,
                        chunk: int = 1000) -> np.ndarray:
    """Circular block bootstrap of the daily series: ``draws`` resampled paths of ``length`` days
    (blocks of ``block`` consecutive days, wrapping), each path's max drawdown ($). A fresh
    numpy default_rng(seed) per call: the same seed gives the same draws."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n == 0:
        return np.zeros(0)
    rng = np.random.default_rng(seed)
    n_blocks = -(-length // block)
    out = np.empty(draws)
    offs = np.arange(block)
    for lo in range(0, draws, chunk):
        k = min(chunk, draws - lo)
        starts = rng.integers(0, n, size=(k, n_blocks))
        idx = ((starts[:, :, None] + offs[None, None, :]) % n).reshape(k, -1)[:, :length]
        cum = np.concatenate([np.zeros((k, 1)), np.cumsum(x[idx], axis=1)], axis=1)
        out[lo:lo + k] = (np.maximum.accumulate(cum, axis=1) - cum).max(axis=1)
    return out


def bootstrap_summary(mdd: np.ndarray) -> dict:
    return {"expected": float(mdd.mean()),
            **{f"p{int(p)}": float(np.percentile(mdd, p)) for p in BOOT_PCTS}}


__all__ = ["ANNUAL_DAYS", "BOOT_BLOCK", "BOOT_DRAWS", "BOOT_LENGTH", "BOOT_SEED", "annual",
           "block_bootstrap_mdd", "bootstrap_summary", "max_drawdown", "sharpe"]
