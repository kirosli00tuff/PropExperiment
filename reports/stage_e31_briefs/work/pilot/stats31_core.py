"""E.31 stats layer, core pieces: fees, day-block bootstrap, Kaplan-Meier and the section 5 buckets.

Spec: reports/stage_e31_pilot_spec.md sections 5, 7 and 8 (binding). Copied and adapted from E.28's
reports/stage_e28_briefs/work/B_pilot/measure_stats.py (read-only): the bootstrap weight matrix
(trade dates drawn with replacement, ONE matrix shared by every statistic), ratio statistics and
95% percentile intervals with the positive / negative / not-distinguishable label. New here: a
weighted product-limit estimator, so the KM fill probabilities get bootstrap intervals that stay
exact even if the engine censors a placement before 60 s, and the bucket rules of spec section 5.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np

# ------------------------------------------------------------------ parameters (spec 0, 5, 8) ----
BOOT_REPLICATES = 2000
BOOT_SEED = 31
HORIZONS_S = (1, 10, 60)
KM_CENSOR_S = 60.0
KM_POINTS_S = (1, 10, 60)
ZM_TICK_USD = 10.00
# Spec section 0: round-trip fee in USD and the fee per fill in ticks (RT / 2 / 10).
FEES_RT_USD = {"Topstep": 5.28, "Lucid": 5.60, "Bulenox": 5.72, "MFFU": 6.12, "Tradeify": 9.20}
FEE_PER_FILL_TICKS = {"Topstep": 0.264, "Lucid": 0.280, "Bulenox": 0.286, "MFFU": 0.306,
                      "Tradeify": 0.460}
FIRMS = tuple(FEE_PER_FILL_TICKS)
PRIMARY_FIRM = "Topstep"

POSITIVE, NEGATIVE, NOT_DIST = "positive", "negative", "not distinguishable from 0"

# Section 5 buckets. A ZS / ZL move d is a difference of mids in ticks, so it is a multiple of half
# a tick; the tolerance only absorbs float noise of the tick division (it is not a dead band).
MOVE_TOL_TICKS = 1e-6
MISSING = "missing"
MOVE_BUCKETS = ("against", "flat", "with", MISSING)
JOINT_BUCKETS = ("both against", "both with", "other", MISSING)
USDA_BUCKETS = ("pre (-30, 0)", "post [0, 5)", "post [5, 30)", "other")
IMB_OUTSIDE = "outside (-1, 1)"
IMB_BUCKETS = ("(-1, -0.6]", "(-0.6, -0.2]", "(-0.2, 0.2)", "[0.2, 0.6)", "[0.6, 1)",
               IMB_OUTSIDE, MISSING)

_KM_CHUNK = 250  # bootstrap replicates per matrix product in the weighted KM
_HALF = 0.5 + 1e-12  # KM median: first time with S(t) <= 0.5 (float slack only)


# ------------------------------------------------------------------ bootstrap ----
def bootstrap_weights(n_days: int, replicates: int = BOOT_REPLICATES,
                      seed: int = BOOT_SEED) -> np.ndarray:
    """W[r, d] = how often trade date d is drawn in replicate r (E.28's construction)."""
    if n_days <= 0:
        return np.zeros((replicates, 0), dtype=np.int64)
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, n_days, size=(replicates, n_days))
    w = np.zeros((replicates, n_days), dtype=np.int64)
    np.add.at(w, (np.repeat(np.arange(replicates), n_days), draws.ravel()), 1)
    return w


def ratio(num: np.ndarray, den: np.ndarray) -> np.ndarray:
    """num / den where den > 0, else NaN."""
    num = np.asarray(num, dtype=float)
    den = np.asarray(den, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(den > 0, num / np.where(den > 0, den, 1.0), np.nan)


def classify(lo: float | None, hi: float | None) -> str | None:
    if lo is None or hi is None:
        return None
    if lo > 0:
        return POSITIVE
    if hi < 0:
        return NEGATIVE
    return NOT_DIST


def interval(point: float | None, boot: np.ndarray, *, label: bool = False) -> dict[str, Any]:
    """Point value with the 95% two-sided percentile interval of the finite replicates."""
    boot = np.asarray(boot, dtype=float)
    finite = boot[np.isfinite(boot)]
    lo, hi = ((float(np.percentile(finite, 2.5)), float(np.percentile(finite, 97.5)))
              if len(finite) else (None, None))
    value = None if point is None or not np.isfinite(point) else float(point)
    out: dict[str, Any] = {"value": value, "ci95": [lo, hi], "boot_valid": int(len(finite))}
    if label:
        out["label"] = classify(lo, hi)
    return out


def ratio_stat(num_d: np.ndarray, den_d: np.ndarray, w: np.ndarray, *,
               label: bool = False) -> dict[str, Any]:
    """A pooled ratio (rate or mean) with its day-block bootstrap interval."""
    point = float(ratio(np.array([num_d.sum()]), np.array([den_d.sum()]))[0])
    return interval(point, ratio(w @ num_d, w @ den_d), label=label)


def per_day(day: np.ndarray, mask: np.ndarray, n_days: int,
            values: np.ndarray | None = None) -> np.ndarray:
    """Per-trade-date count (or sum of ``values``) over the rows in ``mask``."""
    weights = None if values is None else np.asarray(values, dtype=float)[mask]
    return np.bincount(day[mask], weights=weights, minlength=n_days).astype(float)


def vpo_values(fills: np.ndarray, placements: np.ndarray, e_sum: np.ndarray, e_cnt: np.ndarray,
               fee: float) -> np.ndarray:
    """VPO = fill rate x (mean E - fee). 0 with placements but no fill (an order that never fills
    earns nothing); NaN with no placements, or with fills whose edges were all dropped (E.28)."""
    vpo = ratio(fills, placements) * (ratio(e_sum, e_cnt) - fee)
    return np.where((np.asarray(placements) > 0) & (np.asarray(fills) == 0), 0.0, vpo)


# ------------------------------------------------------------------ Kaplan-Meier ----
def km_weighted(dur: np.ndarray, event: np.ndarray, day: np.ndarray, n_days: int,
                weights: np.ndarray, points: Sequence[float]) -> tuple[np.ndarray, np.ndarray]:
    """Product-limit estimator with per-trade-date weights (one row of ``weights`` per replicate).

    Returns (F, median): F[r, i] = 1 - S(points[i]) and the first event time with S <= 0.5 (NaN
    if not reached), both NaN for a replicate without observations. At a time with events and
    censorings, the censored ones are still at risk (events first, E.28's convention)."""
    weights = np.atleast_2d(np.asarray(weights, dtype=float))
    reps = weights.shape[0]
    has_obs = (weights @ per_day(day, np.ones(len(dur), dtype=bool), n_days)) > 0
    cdf = np.full((reps, len(points)), np.nan)
    med = np.full(reps, np.nan)
    times = np.unique(dur[event])
    if len(times) == 0:
        cdf[has_obs] = 0.0
        return cdf, med
    m = len(times)
    deaths = np.zeros((n_days, m))
    np.add.at(deaths, (day[event], np.searchsorted(times, dur[event])), 1.0)
    hist = np.zeros((n_days, m + 1))
    np.add.at(hist, (day, np.searchsorted(times, dur, side="right")), 1.0)
    at_risk = np.cumsum(hist[:, ::-1], axis=1)[:, ::-1][:, 1:]  # obs with dur >= times[k]
    k_pts = np.searchsorted(times, np.asarray(points, dtype=float), side="right") - 1
    for start in range(0, reps, _KM_CHUNK):
        rows = slice(start, start + _KM_CHUNK)
        d_w = weights[rows] @ deaths
        r_w = weights[rows] @ at_risk
        with np.errstate(divide="ignore", invalid="ignore"):
            factor = np.where(r_w > 0, 1.0 - d_w / np.where(r_w > 0, r_w, 1.0), 1.0)
        surv = np.cumprod(factor, axis=1)
        for i, k in enumerate(k_pts):
            cdf[rows, i] = 0.0 if k < 0 else 1.0 - surv[:, k]
        below = surv <= _HALF
        med[rows] = np.where(below.any(axis=1), times[np.argmax(below, axis=1)], np.nan)
    cdf[~has_obs] = np.nan
    med[~has_obs] = np.nan
    return cdf, med


def km_inputs(wait_s: np.ndarray, filled: np.ndarray,
              censor_s: float = KM_CENSOR_S) -> tuple[np.ndarray, np.ndarray]:
    """Durations and events censored at 60 s: a non-fill, and a fill inside the 50 ms cancel
    latency after j + 60 s, is censored at min(wait, 60)."""
    event = filled & (wait_s <= censor_s)
    return np.where(event, wait_s, np.minimum(wait_s, censor_s)), event


def km_stats(wait_s: np.ndarray, filled: np.ndarray, day: np.ndarray, n_days: int,
             w: np.ndarray) -> dict[str, Any]:
    """KM time to fill: median (point only, as E.28), P(fill by 1, 10, 60 s) with intervals."""
    dur, event = km_inputs(wait_s, filled)
    pt_cdf, pt_med = km_weighted(dur, event, day, n_days, np.ones((1, n_days)), KM_POINTS_S)
    bt_cdf, _ = km_weighted(dur, event, day, n_days, w, KM_POINTS_S)
    med = float(pt_med[0])
    out: dict[str, Any] = {
        "censor_s": KM_CENSOR_S,
        "median_s": med if np.isfinite(med) else None,
        "median_reached": bool(np.isfinite(med)),
        "censored_before_60s": int(np.count_nonzero(~event & (dur < KM_CENSOR_S)))}
    for i, t in enumerate(KM_POINTS_S):
        out[f"p_fill_by_{t}s"] = interval(float(pt_cdf[0, i]), bt_cdf[:, i])
    return out


# ------------------------------------------------------------------ buckets (spec 5) ----
def move_bucket(side: np.ndarray, d: np.ndarray) -> np.ndarray:
    """Sign of s x d: against (< 0), flat (= 0), with (> 0); NaN d -> missing."""
    x = np.asarray(side, dtype=float) * np.asarray(d, dtype=float)
    out = np.full(len(x), MISSING, dtype=object)
    fin = np.isfinite(x)
    out[fin & (x < -MOVE_TOL_TICKS)] = "against"
    out[fin & (np.abs(x) <= MOVE_TOL_TICKS)] = "flat"
    out[fin & (x > MOVE_TOL_TICKS)] = "with"
    return out


def joint_bucket(zs: np.ndarray, zl: np.ndarray) -> np.ndarray:
    """Both against, both with, other; missing if either move is missing (spec section 2: the
    joint condition needs both mids)."""
    out = np.full(len(zs), "other", dtype=object)
    out[(zs == "against") & (zl == "against")] = "both against"
    out[(zs == "with") & (zl == "with")] = "both with"
    out[(zs == MISSING) | (zl == MISSING)] = MISSING
    return out


def usda_bucket(minutes: np.ndarray) -> np.ndarray:
    """Signed minutes from the nearest release: pre (-30, 0), post [0, 5), post [5, 30), other
    (NaN = no release on the trade date, which the spec puts in other)."""
    m = np.asarray(minutes, dtype=float)
    out = np.full(len(m), "other", dtype=object)
    with np.errstate(invalid="ignore"):
        out[(m > -30) & (m < 0)] = USDA_BUCKETS[0]
        out[(m >= 0) & (m < 5)] = USDA_BUCKETS[1]
        out[(m >= 5) & (m < 30)] = USDA_BUCKETS[2]
    return out


def imb_bucket(imb: np.ndarray) -> np.ndarray:
    """Side-adjusted imbalance s x I: (-1, -0.6], (-0.6, -0.2], (-0.2, 0.2), [0.2, 0.6), [0.6, 1);
    NaN -> missing; exactly -1 or 1 (one side empty, so no placement) -> outside."""
    x = np.asarray(imb, dtype=float)
    out = np.full(len(x), IMB_OUTSIDE, dtype=object)
    with np.errstate(invalid="ignore"):
        out[(x > -1) & (x <= -0.6)] = IMB_BUCKETS[0]
        out[(x > -0.6) & (x <= -0.2)] = IMB_BUCKETS[1]
        out[(x > -0.2) & (x < 0.2)] = IMB_BUCKETS[2]
        out[(x >= 0.2) & (x < 0.6)] = IMB_BUCKETS[3]
        out[(x >= 0.6) & (x < 1)] = IMB_BUCKETS[4]
    out[~np.isfinite(x)] = MISSING
    return out
