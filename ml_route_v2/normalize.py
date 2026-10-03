"""V2.4 causal normalization of features: a rolling z-score per product and per feature.

docs/STAGE_E_ML_V2_DESIGN.md V2.4; contract reports/stage_e11_interfaces.md section 4.
- The mean and sd of a feature for a row of product p on trade date d are over p's rows on the
  trailing ``window_dates`` trade dates strictly before d (reading NZ-1: the product's own row
  dates, so an excluded date is not a slot), using the rows where the value is present (NaN, e.g.
  a not-applicable member value the panel masks, does not enter).
- Warm-up: fewer than ``min_dates`` such dates: NaN (the row is excluded by the panel). Same-date
  rows never use each other. Fewer than two values in the window: NaN (no statistic).
- The sums behind the mean and the variance are taken about a shifted origin per product and
  feature: the product's first finite value of the feature (earliest date, a past constant for
  every row that has a window). The variance is shift-invariant, so z is the same to rounding,
  but the cancellation in (sum2 - sum1 x mean) no longer grows with the feature's mean squared
  over its variance (code review C-12: a feature of mean 1e6 and sd 1 keeps its z-scores).
- z = (x - mean) / sd (sample sd, ddof 1), clipped to [-clip, clip]. Reading NZ-2: when every
  value in the window is the same (sd 0, e.g. a fixed-clock "minutes since" that is always 50 at
  one decision time), z = 0 at that value and +-clip away from it, so a constant feature never
  excludes a row.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd

from ml_route_v2.constants import Z_CLIP, Z_MIN_DATES, Z_WINDOW_DATES


def _origin(values: np.ndarray, finite: np.ndarray, date_idx: np.ndarray) -> float:
    """The first finite value on the product's earliest date holding one (0.0 if none)."""
    idx = np.flatnonzero(finite)
    if idx.size == 0:
        return 0.0
    return float(values[idx[np.argmin(date_idx[idx])]])


def _root_z(x: np.ndarray, date_idx: np.ndarray, n_dates: int, window: int, min_dates: int,
            clip: float) -> np.ndarray:
    """z of one product's rows; x is (rows, cols), date_idx the row's position in its dates."""
    finite = np.isfinite(x)
    xz = np.where(finite, x, 0.0)
    out = np.full(x.shape, np.nan)
    lo = np.maximum(np.arange(n_dates) - window, 0)
    hi = np.arange(n_dates)
    warm = (hi - lo) >= min_dates
    for c in range(x.shape[1]):
        origin = _origin(xz[:, c], finite[:, c], date_idx)  # C-12: a shifted origin
        xs = np.where(finite[:, c], xz[:, c] - origin, 0.0)
        s1 = np.bincount(date_idx, weights=xs, minlength=n_dates)
        s2 = np.bincount(date_idx, weights=xs ** 2, minlength=n_dates)
        cn = np.bincount(date_idx, weights=finite[:, c].astype(np.float64), minlength=n_dates)
        c1, c2, cc = (np.concatenate([[0.0], np.cumsum(a)]) for a in (s1, s2, cn))
        n = cc[hi] - cc[lo]
        sum1 = c1[hi] - c1[lo]
        sum2 = c2[hi] - c2[lo]
        with np.errstate(invalid="ignore", divide="ignore"):
            mean_s = sum1 / n  # the mean about the origin
            var = (sum2 - sum1 * mean_s) / (n - 1)
            mean = mean_s + origin
        # a window of equal values: var is 0 up to rounding (relative to the shifted mean's
        # square; exactly 0 when the window's values equal the origin)
        flat = (n >= 2) & (np.abs(var) <= 1e-12 * np.maximum(mean_s * mean_s, 1e-300))
        sd = np.sqrt(np.where((var > 0) & ~flat, var, np.nan))
        good = warm & (n >= 2) & ((np.isfinite(sd) & (sd > 0)) | flat)
        m_row, g_row, f_row = mean[date_idx], good[date_idx], flat[date_idx]
        sd_row = np.where(f_row, np.inf, sd[date_idx])
        xc = x[:, c]
        with np.errstate(invalid="ignore", divide="ignore"):
            z = (xc - m_row) / np.where(g_row & ~f_row, sd_row, 1.0)
        same = np.isclose(xc, m_row, rtol=1e-9, atol=0.0)
        z = np.where(f_row, np.where(same, 0.0, np.sign(xc - m_row) * clip), z)
        z = np.where(g_row & finite[:, c], z, np.nan)
        out[:, c] = np.clip(z, -clip, clip)
    return out


def zscore_causal(raw: pd.DataFrame, rows: pd.DataFrame, cols: Sequence[str], *,
                  window_dates: int = Z_WINDOW_DATES, min_dates: int = Z_MIN_DATES,
                  clip: float = Z_CLIP) -> pd.DataFrame:
    """z-scores of ``cols`` of ``raw`` (aligned to ``rows``), per root (module docstring)."""
    if not raw.index.equals(rows.index):
        raise ValueError("raw is not aligned to the decision rows")
    cols = list(cols)
    x_all = raw[cols].to_numpy(np.float64) if cols else np.zeros((len(raw), 0))
    out = np.full(x_all.shape, np.nan)
    days = rows["trade_date"].to_numpy().astype("datetime64[D]").astype(np.int64)
    root = rows["root"].to_numpy(object)
    for r in pd.unique(root):
        sel = np.flatnonzero(root == r)
        udays, date_idx = np.unique(days[sel], return_inverse=True)
        out[sel] = _root_z(x_all[sel], date_idx, len(udays), window_dates, min_dates, clip)
    return pd.DataFrame(out, index=raw.index, columns=cols)


__all__ = ["zscore_causal"]
