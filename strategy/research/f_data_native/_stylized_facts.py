"""Stage D.1b Task 2b: Family F stylized facts.

Implements ONLY reports/stage_d1b_family_f_declaration.md
sha256 9c17c508c50ee66e37fc471136368c4b364922bc16437f7d9f0b5d860314448d, and nothing else:
no extra horizons, no extra levels, no extra splits, no strategy, no entries/exits, no P&L,
no backtest. This module computes descriptive statistics on MES 1-minute research bars only.

Run as ``uv run python -m strategy.research.f_data_native._stylized_facts``. Writes
``reports/stage_d1b_family_f_facts.json``.
"""

from __future__ import annotations

import json
import math
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd

from data.config import REPO_ROOT
from data.research_bars import RESEARCH_SERIES_PATH, load_research_bars
from data.session import CME_TZ
from funnel.null_generator import stationary_bootstrap_indices
from screening.runner import canonical_engine_config, fold_train_window, train_union_window
from sim.engine import BAR_COLUMNS, splice_trade_dates_from_parquet

DECL_SHA256 = "9c17c508c50ee66e37fc471136368c4b364922bc16437f7d9f0b5d860314448d"

TICK = 0.25
SEED = 20260918
N_RESAMPLES = 2000
MEAN_BLOCK = 5.0
BH_Q = 0.10
M_STATS = 57

# Continuous "session minute" axis, 0 at 17:00 CT (the Globex reopen), 1439 at 16:59 CT
# the next day. ETH occupies [0, 930); RTH (08:30..14:59 CT, i.e. bars OPENING in that
# range) occupies [930, 1320); [1320, 1440) is the declared dead zone (15:00-17:00 CT,
# neither RTH nor ETH by this family's declared clock convention) and is never queried
# except by F4.4's cross-session scan, which does not use this per-day axis at all.
ETH_BASE = 0
ETH_LEN = 930
RTH_BASE = 930
RTH_LEN = 390
BUCKET_H = 30
N_BUCKETS = 13
DAY_SIZE = 1440

EMPTY = np.array([], dtype=float)

OUTPUT_PATH = REPO_ROOT / "reports" / "stage_d1b_family_f_facts.json"

IMPLEMENTATION_CHOICES = [
    "vendor_degraded_day is a per-bar, per-UTC-date flag; a trade date is excluded from "
    "the EDA set if ANY bar within that trade date carries the flag.",
    "'Prior trade date' (F4.2, F4.3) and 'consecutive EDA dates' (F2.2) mean the "
    "immediately preceding date in the POST-EXCLUSION EDA date list, not the raw "
    "calendar-adjacent research trade date -- every computation stays strictly inside "
    "the declared EDA window and never reaches into fold 0's train dates or an excluded "
    "roll/vendor-degraded session.",
    "Every return (1-minute, h-minute tiled window, and 30-minute bucket) is a "
    "close-to-close log return built from the standard 1-minute close-to-close step: it "
    "sums the h consecutive valid 1-minute steps the window's clock minutes cover "
    "(log(close at window end) - log(close of the bar immediately before the window's "
    "first minute)), never an open-to-close return of the window's own first/last bar. "
    "Windows/buckets are aligned to the clock grid (a bucket boundary at :00/:30, an "
    "h-minute window at multiples of h minutes from the segment's anchor: 08:30 CT for "
    "RTH, 17:00 CT for ETH), not to raw bar position, so one missing bar invalidates only "
    "the windows that actually contain it.",
    "A window/bucket is valid only if every one of its h expected clock minutes has a bar "
    "AND every one of those h 1-minute steps (including the very first, which connects to "
    "whatever bar preceded the window) is itself a valid step. This makes ETH's very "
    "first window of every session segment always invalid, since no bar of the SAME "
    "trade date precedes the session's own first bar -- a direct, intentional consequence "
    "of the declared 'same trade date' return rule, not a bug.",
    "Implied gross edge in ticks uses EXACT price differences (target window's "
    "close-of-last-bar minus close-of-bar-immediately-before-the-window, divided by "
    "0.25), not a log-return approximation, for every directional statistic. Exact price "
    "data is always available for the forward window, so no approximation is needed; "
    "this also matches how F4.1/F4.2/F4.4 are defined (their own statistic is already an "
    "exact tick difference).",
    "F6.1's predictor (open position in [0, 1] within the ETH range) is not naturally "
    "zero-centered, so its naive sign-trading rule uses sign(position - 0.5) -- the "
    "midpoint of the declared [0, 1] scale -- rather than sign(position); this is the "
    "only statistic where 'sign(predictor)' needed a centering choice.",
    "F2.3's target (next bucket's realized volatility) has no sign -- it is not a return "
    "-- so the declared edge formula (mean of sign(predictor) x forward return) does not "
    "apply; implied_edge_ticks is null for F2.3, consistent with the declaration's own "
    "classification of F2.3 as eligible only through a directional reading, not as a "
    "directly signed edge.",
    "F1.2 (variance ratio), F2.1 (|return| autocorrelation) and F2.2 (realized-variance "
    "autocorrelation) are non-directional by declaration; implied_edge_ticks is null for "
    "all of them.",
    "F3.1's 'every bucket of the trade date' is read as the same 13 fixed 30-minute RTH "
    "buckets F3.2 defines explicitly, since that is the only bucket grid Family F "
    "declares anywhere; there is no separate ETH bucket grid in the family.",
    "F5.2's trend-efficiency ratio uses an exact price difference in its numerator "
    "(|bucket close - bucket's pre-window close| / (bucket high - bucket low)), not the "
    "log return, since it is paired with a range term that is itself in price units; the "
    "lag-1 correlation that follows still uses the log return, matching every other "
    "correlation in the family.",
    "Tercile/bucket edges (F2.4's trailing-vol terciles, F4.3's |gap| terciles, F5.1's "
    "relative-volume terciles, F5.2's efficiency terciles) are computed once on the full "
    "pooled EDA sample and held FROZEN across every bootstrap resample and sub-block, "
    "never recomputed per resample, since the declaration says a hypothesis's parameters "
    "are 'computed on EDA dates and frozen.'",
    "F4.4's control level set (multiples of 50 offset by +12.5/+37.5 points) is used as "
    "the single, common control baseline for BOTH the multiples-of-50 and "
    "multiples-of-100 comparisons; the declaration defines the control set once, tied to "
    "the 50-point grid, and does not define a separate control grid for the "
    "multiples-of-100 comparison.",
    "F4.4 is the only statistic scoped to 'any session' without a same-trade-date "
    "restriction: its crossing detection and forward-15 measurement use the raw "
    "gap_before_minutes == 0 continuity check only (not the same-trade-date restricted "
    "step validity used everywhere else in this family), so a round-number crossing's "
    "forward return may span the overnight boundary or a trade-date boundary. Every "
    "other statistic is confined to a single trade date (or, for F2.2/F4.2/F4.3, a pair "
    "of adjacent surviving EDA dates).",
    "Bootstrap p-values use the declared two-sided formula (2 x min(share <= null, share "
    ">= null)), null = 0 for every statistic except F1.2 (VR, null = 1, per the "
    "declaration) and F4.4's difference-vs-control (null = 0, per the declaration, "
    "matching the default anyway). F4.3's statistic is a probability bounded below by 0; "
    "the declaration states no exception for it, so the same default (null = 0) formula "
    "is applied literally even though this makes its p-value near-trivial -- flagged "
    "because F4.3 is INELIGIBLE by declaration and never selects a hypothesis.",
    "The 95% CI is the plain percentile bootstrap interval (2.5th/97.5th percentiles of "
    "the resampled statistic), not bias-corrected or accelerated, matching the "
    "percentile-bootstrap convention already used in this repo (screening/drift.py).",
    "Each of the 57 statistics' bootstrap draws its 2,000-resample day-index sequence "
    "from a FRESH numpy Generator seeded with 20260918 (not one global generator "
    "advanced across all 57 statistics in sequence), so every statistic's resample path "
    "is independently reproducible from the declared seed alone. The day-block "
    "resampling itself reuses this repo's existing stationary bootstrap "
    "(funnel.null_generator.stationary_bootstrap_indices), which already implements the "
    "declared scheme (circular stationary block bootstrap, mean block length in days).",
    "'4 contiguous, equal-count sub-blocks of the EDA dates' operates on the 139 EDA "
    "dates that remain AFTER exclusions (not the 147 before exclusions), since every "
    "statistic is computed on the post-exclusion set; 139 does not divide evenly by 4, "
    "so the split uses the most equal partition possible (35, 35, 35, 34 dates, in date "
    "order).",
    "A pair or window is 'adjacent' only if both members are literally consecutive on "
    "the relevant index (consecutive clock-grid window indices within a day for "
    "F1.1/F2.4/F3.2/F5.x, consecutive surviving EDA dates for F2.2); a gap silently "
    "breaks the chain rather than being bridged to the next available observation.",
    "Sub-block sign agreement compares sign(sub-block estimate - null) to sign(full "
    "sample estimate - null); a sub-block with zero valid observations contributes no "
    "sign (recorded as null) and is excluded from both the numerator and denominator of "
    "the agreement count.",
    "F3.1's skew and excess kurtosis use the plain (biased) plug-in moment estimators "
    "(population standard deviation in the denominator): scipy is not a project "
    "dependency and the declaration does not specify a bias correction.",
    "Bootstrap replicates that are undefined (a resample draws zero qualifying "
    "observations, or zero variance in a correlation/VR denominator) are dropped from "
    "the percentile CI and p-value computation rather than imputed.",
]


# ============================================================================= data prep ====
def resolve_eda_dates() -> tuple[list[date], list[dict], pd.DataFrame]:
    """The 139 EDA dates (post-exclusion), the excluded-date log, and their bars."""
    frame = load_research_bars(list(BAR_COLUMNS))
    days_arr = pd.to_datetime(frame["trade_date"].astype(str)).dt.date.to_numpy()
    sorted_dates = sorted(set(days_arr))
    eda_raw = sorted_dates[142:289]

    tu = set(train_union_window().trade_dates)
    f0 = set(fold_train_window(0).trade_dates)
    if not set(eda_raw) <= tu:
        raise AssertionError("EDA dates must be a subset of screening.train_union_window()")
    if not set(eda_raw).isdisjoint(f0):
        raise AssertionError("EDA dates must be disjoint from fold 0's train window")

    splice = splice_trade_dates_from_parquet(RESEARCH_SERIES_PATH)
    roll_blackout = canonical_engine_config(splice).roll_blackout
    vdd_dates = set(
        pd.to_datetime(frame.loc[frame["vendor_degraded_day"], "trade_date"].astype(str)).dt.date
    )

    excluded: list[dict] = []
    eda_dates: list[date] = []
    for d in eda_raw:
        reasons = []
        if d in roll_blackout:
            reasons.append("roll_blackout")
        if d in vdd_dates:
            reasons.append("vendor_degraded_day")
        if reasons:
            excluded.append({"date": d.isoformat(), "reason": "+".join(reasons)})
        else:
            eda_dates.append(d)

    eda_date_strs = {d.isoformat() for d in eda_dates}
    bars = (
        frame[frame["trade_date"].isin(eda_date_strs)]
        .sort_values(["trade_date", "ts_event"])
        .reset_index(drop=True)
    )
    return eda_dates, excluded, bars


def engineer_bars(bars: pd.DataFrame) -> pd.DataFrame:
    """Add the return-construction and clock columns every statistic in this file reads."""
    bars = bars.copy()
    bars["trade_date_obj"] = pd.to_datetime(bars["trade_date"]).dt.date
    prev_close = bars.groupby("trade_date")["close"].shift(1)
    prev_instrument = bars.groupby("trade_date")["instrument_id"].shift(1)
    bars["valid_step"] = (
        (bars["instrument_id"] == prev_instrument)
        & (bars["gap_before_minutes"] == 0)
        & prev_close.notna()
    )
    bars["logret1"] = np.where(
        bars["valid_step"], np.log(bars["close"]) - np.log(prev_close), np.nan
    )
    local = pd.to_datetime(bars["ts_event"], unit="ns", utc=True).dt.tz_convert(CME_TZ)
    ct_minute = local.dt.hour * 60 + local.dt.minute
    bars["session_minute"] = (ct_minute - 1020) % 1440
    return bars


def build_day_arrays(g: pd.DataFrame) -> dict[str, np.ndarray]:
    """A dense, session-minute-indexed view of one trade date's bars."""
    out = {
        "close": np.full(DAY_SIZE, np.nan),
        "high": np.full(DAY_SIZE, np.nan),
        "low": np.full(DAY_SIZE, np.nan),
        "open": np.full(DAY_SIZE, np.nan),
        "vol": np.full(DAY_SIZE, np.nan),
        "logret1": np.full(DAY_SIZE, np.nan),
        "instr": np.full(DAY_SIZE, np.nan),
        "valid": np.zeros(DAY_SIZE, dtype=bool),
    }
    m = g["session_minute"].to_numpy()
    out["close"][m] = g["close"].to_numpy()
    out["high"][m] = g["high"].to_numpy()
    out["low"][m] = g["low"].to_numpy()
    out["open"][m] = g["open"].to_numpy()
    out["vol"][m] = g["volume"].to_numpy()
    out["logret1"][m] = g["logret1"].to_numpy()
    out["instr"][m] = g["instrument_id"].to_numpy().astype(float)
    out["valid"][m] = g["valid_step"].to_numpy()
    return out


def build_all_day_arrays(bars: pd.DataFrame) -> dict[date, dict[str, np.ndarray]]:
    return {d: build_day_arrays(g) for d, g in bars.groupby("trade_date_obj", sort=True)}


def bucket_label(k: int) -> str:
    start = 510 + k * 30
    end = start + 30
    return f"{start // 60:02d}{start % 60:02d}-{end // 60:02d}{end % 60:02d}"


# ============================================================================ windows ====
@dataclass(frozen=True)
class WindowStat:
    ret: float
    rvol: float
    range_: float
    volume: float
    close_last: float
    close_before: float
    price_change: float  # close_last - close_before, exact ticks basis


def window_stats(da: dict[str, np.ndarray], base: int, h: int, k: int) -> WindowStat | None:
    lo = base + k * h
    hi = lo + h
    if hi > DAY_SIZE or lo < 1:
        return None
    idx = np.arange(lo, hi)
    valid = da["valid"][idx]
    if not valid.all():
        return None
    lr = da["logret1"][idx]
    close_last = float(da["close"][idx[-1]])
    close_before = float(da["close"][lo - 1])
    return WindowStat(
        ret=float(lr.sum()),
        rvol=float(np.sqrt(np.sum(lr * lr))),
        range_=float(da["high"][idx].max() - da["low"][idx].min()),
        volume=float(da["vol"][idx].sum()),
        close_last=close_last,
        close_before=close_before,
        price_change=close_last - close_before,
    )


def _first_bar_to_0900(da: dict[str, np.ndarray]) -> WindowStat | None:
    """F3.3(a): close of the trade date's first bar to the close of the 08:59 CT bar (the
    last bar before 09:00), same instrument. Lead fix (D.1b): the declared statistic starts
    at the first bar's CLOSE, so it needs no valid step INTO that bar (which always crosses
    the daily halt) and no gap-free overnight; ``window_stats`` required both, giving n = 0.
    """
    present = np.flatnonzero(~np.isnan(da["close"][: RTH_BASE + 30]))
    end = RTH_BASE + 29
    if present.size == 0 or np.isnan(da["close"][end]) or present[0] >= end:
        return None
    first = int(present[0])
    if da["instr"][first] != da["instr"][end]:
        return None
    c0, c1 = float(da["close"][first]), float(da["close"][end])
    return WindowStat(ret=float(np.log(c1 / c0)), rvol=float("nan"), range_=float("nan"),
                      volume=float("nan"), close_last=c1, close_before=c0,
                      price_change=c1 - c0)


def windows_for_day(
    da: dict[str, np.ndarray], base: int, h: int, n_slots: int
) -> dict[int, WindowStat]:
    out: dict[int, WindowStat] = {}
    for k in range(n_slots // h):
        w = window_stats(da, base, h, k)
        if w is not None:
            out[k] = w
    return out


def get_window_table(
    wcache: dict[tuple[int, int], dict[date, dict[int, WindowStat]]],
    day_arrays: dict[date, dict[str, np.ndarray]],
    eda_dates: list[date],
    base: int,
    h: int,
    n_slots: int,
) -> dict[date, dict[int, WindowStat]]:
    key = (base, h)
    if key not in wcache:
        wcache[key] = {d: windows_for_day(day_arrays[d], base, h, n_slots) for d in eda_dates}
    return wcache[key]


def lag1_pairs(
    win: dict[int, WindowStat],
) -> tuple[list[float], list[float], list[float], list[float]]:
    pred, targ, sign_pred, ticks = [], [], [], []
    for k, w in win.items():
        nxt = win.get(k + 1)
        if nxt is None:
            continue
        pred.append(w.ret)
        targ.append(nxt.ret)
        sign_pred.append(w.ret)
        ticks.append(nxt.price_change / TICK)
    return pred, targ, sign_pred, ticks


def raw_lag1(
    da: dict[str, np.ndarray], base: int, length: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    v = da["valid"][base : base + length]
    lr = da["logret1"][base : base + length]
    cl = da["close"][base : base + length]
    mask = v[:-1] & v[1:]
    pred = lr[:-1][mask]
    targ = lr[1:][mask]
    ticks = (cl[1:][mask] - cl[:-1][mask]) / TICK
    return pred, targ, pred, ticks


def raw_lag_abs(
    da: dict[str, np.ndarray], base: int, length: int, lag: int
) -> tuple[np.ndarray, np.ndarray]:
    v = da["valid"][base : base + length]
    lr = da["logret1"][base : base + length]
    mask = v[:-lag] & v[lag:]
    return np.abs(lr[:-lag][mask]), np.abs(lr[lag:][mask])


def all_raw_returns(da: dict[str, np.ndarray], base: int, length: int) -> np.ndarray:
    v = da["valid"][base : base + length]
    return da["logret1"][base : base + length][v]


def forward_clean_close(da: dict[str, np.ndarray], m: int, k: int) -> float | None:
    end = m + k
    if end >= DAY_SIZE:
        return None
    if not da["valid"][m + 1 : end + 1].all():
        return None
    v = da["close"][end]
    return float(v) if np.isfinite(v) else None


def forward_clean_flat(gap0: np.ndarray, close_: np.ndarray, i: int, k: int) -> float | None:
    end = i + k
    if end >= len(close_):
        return None
    if not gap0[i + 1 : end + 1].all():
        return None
    v = close_[end]
    return float(v) if np.isfinite(v) else None


def scan_reference_crossings(
    da: dict[str, np.ndarray], candidate_minutes: range, reference: float, refractory: int
) -> list[float]:
    valid = da["valid"]
    close = da["close"]
    events: list[float] = []
    next_eligible = -1
    for m in candidate_minutes:
        if m < next_eligible or not valid[m]:
            continue
        prev_c = close[m - 1]
        cur_c = close[m]
        if not (np.isfinite(prev_c) and np.isfinite(cur_c)):
            continue
        if (prev_c - reference) * (cur_c - reference) >= 0:
            continue
        direction = 1.0 if cur_c > reference else -1.0
        next_eligible = m + refractory
        fwd = forward_clean_close(da, m, 15)
        if fwd is None:
            continue
        events.append(direction * (fwd - cur_c) / TICK)
    return events


def scan_round_levels(
    ts: np.ndarray,
    trade_date_obj: np.ndarray,
    close_: np.ndarray,
    high_: np.ndarray,
    low_: np.ndarray,
    gap0: np.ndarray,
    levels: list[float],
) -> dict[float, list[tuple[date, float]]]:
    prev_close = np.empty_like(close_)
    prev_close[:] = np.nan
    prev_close[1:] = close_[:-1]
    refractory_ns = 30 * 60 * 1_000_000_000
    out: dict[float, list[tuple[date, float]]] = {}
    for lv in levels:
        cross_up = (prev_close < lv) & (high_ >= lv)
        cross_down = (prev_close > lv) & (low_ <= lv)
        candidate = (cross_up | cross_down) & gap0
        idxs = np.flatnonzero(candidate)
        events: list[tuple[date, float]] = []
        next_eligible = -1
        for i in idxs:
            t = int(ts[i])
            if t < next_eligible:
                continue
            next_eligible = t + refractory_ns
            fwd = forward_clean_flat(gap0, close_, int(i), 15)
            if fwd is None:
                continue
            direction = 1.0 if cross_up[i] else -1.0
            events.append((trade_date_obj[i], direction * (fwd - lv) / TICK))
        out[lv] = events
    return out


def pearson_r(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 2:
        return math.nan
    if np.std(x) == 0 or np.std(y) == 0:
        return math.nan
    return float(np.corrcoef(x, y)[0, 1])


def split_equal(n: int, parts: int) -> list[int]:
    base, rem = divmod(n, parts)
    return [base + 1] * rem + [base] * (parts - rem)


# ======================================================================== bootstrap ====
@dataclass
class DayObs:
    obs_date: date
    data: dict[str, np.ndarray]


@dataclass
class TestedStat:
    id: str
    family: str
    description: str
    directional: bool
    null: float
    days: list[DayObs]
    keys: tuple[str, ...]
    estimate_fn: Callable[[dict[str, np.ndarray]], float]
    n_fn: Callable[[dict[str, np.ndarray]], int]
    edge_fn: Callable[[dict[str, np.ndarray]], float] | None = None
    edge_equals_estimate: bool = False
    extra_fn: Callable[[dict[str, np.ndarray]], dict] | None = None


def pool_days(days: list[DayObs], keys: tuple[str, ...]) -> dict[str, np.ndarray]:
    out = {}
    for k in keys:
        arrs = [d.data.get(k, EMPTY) for d in days]
        out[k] = np.concatenate(arrs) if arrs else EMPTY
    return out


def bootstrap_replicates(stat: TestedStat) -> np.ndarray:
    n_days = len(stat.days)
    if n_days == 0:
        return EMPTY
    rng = np.random.default_rng(SEED)
    by_key = {k: [d.data.get(k, EMPTY) for d in stat.days] for k in stat.keys}
    reps = []
    for _ in range(N_RESAMPLES):
        idx = stationary_bootstrap_indices(rng, n_days, n_days, MEAN_BLOCK)
        pooled = {k: np.concatenate([arr[i] for i in idx]) for k, arr in by_key.items()}
        v = stat.estimate_fn(pooled)
        if v is not None and not (isinstance(v, float) and math.isnan(v)):
            reps.append(v)
    return np.array(reps)


def _safe_float(v: float | None) -> float | None:
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    return float(v)


def _sign(v: float | None, null: float) -> int | None:
    if v is None:
        return None
    d = v - null
    if d > 0:
        return 1
    if d < 0:
        return -1
    return 0


def compute_result(stat: TestedStat, subblock_map: dict[date, int]) -> dict:
    full_pool = pool_days(stat.days, stat.keys)
    estimate = _safe_float(stat.estimate_fn(full_pool))
    n = stat.n_fn(full_pool)
    if stat.edge_equals_estimate:
        edge = estimate
    elif stat.directional and stat.edge_fn is not None:
        edge = _safe_float(stat.edge_fn(full_pool))
    else:
        edge = None

    reps = bootstrap_replicates(stat)
    if len(reps):
        ci_low = float(np.percentile(reps, 2.5))
        ci_high = float(np.percentile(reps, 97.5))
        share_le = float(np.mean(reps <= stat.null))
        share_ge = float(np.mean(reps >= stat.null))
        p_boot: float | None = float(min(1.0, 2.0 * min(share_le, share_ge)))
    else:
        ci_low = ci_high = p_boot = None

    sub_ests: list[float | None] = []
    for b in range(4):
        bd = [d for d in stat.days if subblock_map[d.obs_date] == b]
        v = _safe_float(stat.estimate_fn(pool_days(bd, stat.keys))) if bd else None
        sub_ests.append(v)
    full_sign = _sign(estimate, stat.null)
    agree = sum(1 for v in sub_ests if v is not None and _sign(v, stat.null) == full_sign)

    extra = stat.extra_fn(full_pool) if stat.extra_fn else {}
    record = {
        "id": stat.id,
        "family": stat.family,
        "description": stat.description,
        "directional": stat.directional,
        "n": n,
        "estimate": estimate,
        "ci95_low": ci_low,
        "ci95_high": ci_high,
        "p_boot": p_boot,
        "sub_block_estimates": sub_ests,
        "sub_block_sign_agree": agree,
        "implied_edge_ticks": edge,
    }
    record.update(extra)
    return record


def bh_flags(records: list[dict], q: float) -> None:
    m = len(records)
    pvals = [r["p_boot"] if r["p_boot"] is not None else 1.0 for r in records]
    order = sorted(range(m), key=lambda i: pvals[i])
    n_reject = 0
    for rank, i in enumerate(order, start=1):
        if pvals[i] <= (rank / m) * q:
            n_reject = rank
    rejected = set(order[:n_reject])
    for idx, r in enumerate(records):
        r["bh_reject"] = idx in rejected


def _corr_edge_fn(p: dict[str, np.ndarray]) -> float:
    if len(p["ticks"]) == 0:
        return math.nan
    return float(np.mean(np.sign(p["sign_pred"]) * p["ticks"]))


def _corr_estimate_fn(p: dict[str, np.ndarray]) -> float:
    return pearson_r(p["pred"], p["targ"])


def _corr_n_fn(p: dict[str, np.ndarray]) -> int:
    return int(len(p["pred"]))


PAIR_KEYS = ("pred", "targ", "sign_pred", "ticks")


def _pair_day(
    d: date, pred: list[float] | np.ndarray, targ: list[float] | np.ndarray,
    sign_pred: list[float] | np.ndarray, ticks: list[float] | np.ndarray,
) -> DayObs:
    return DayObs(
        d,
        {
            "pred": np.asarray(pred, dtype=float),
            "targ": np.asarray(targ, dtype=float),
            "sign_pred": np.asarray(sign_pred, dtype=float),
            "ticks": np.asarray(ticks, dtype=float),
        },
    )


# ================================================================================ F1 ====
def build_f1(
    day_arrays: dict[date, dict[str, np.ndarray]],
    eda_dates: list[date],
    wcache: dict,
) -> list[TestedStat]:
    stats: list[TestedStat] = []
    segments = (("RTH", RTH_BASE, RTH_LEN), ("ETH", ETH_BASE, ETH_LEN))

    for seg_name, base, length in segments:
        for h in (1, 5, 15, 30, 60):
            days = []
            for d in eda_dates:
                da = day_arrays[d]
                if h == 1:
                    pred, targ, sp, tk = raw_lag1(da, base, length)
                else:
                    win = get_window_table(wcache, day_arrays, eda_dates, base, h, length)[d]
                    pred, targ, sp, tk = lag1_pairs(win)
                days.append(_pair_day(d, pred, targ, sp, tk))
            stats.append(
                TestedStat(
                    id=f"F1_1_h{h}_{seg_name}",
                    family="F1.1",
                    description=(
                        f"Lag-1 autocorrelation of consecutive non-overlapping {h}-min "
                        f"returns, {seg_name}"
                    ),
                    directional=True,
                    null=0.0,
                    days=days,
                    keys=PAIR_KEYS,
                    estimate_fn=_corr_estimate_fn,
                    edge_fn=_corr_edge_fn,
                    n_fn=_corr_n_fn,
                )
            )

    for seg_name, base, length in segments:
        for h in (5, 15, 30, 60):
            days = []
            for d in eda_dates:
                da = day_arrays[d]
                win = get_window_table(wcache, day_arrays, eda_dates, base, h, length)[d]
                winret = np.array([w.ret for w in win.values()], dtype=float)
                minret = all_raw_returns(da, base, length)
                days.append(DayObs(d, {"winret": winret, "minret": minret}))

            def vr_fn(p: dict[str, np.ndarray], hh: int = h) -> float:
                wr, mr = p["winret"], p["minret"]
                if len(wr) < 2 or len(mr) < 2:
                    return math.nan
                vm = np.var(mr, ddof=1)
                if vm == 0:
                    return math.nan
                return float(np.var(wr, ddof=1) / (hh * vm))

            stats.append(
                TestedStat(
                    id=f"F1_2_VR{h}_{seg_name}",
                    family="F1.2",
                    description=(
                        f"Variance ratio VR({h}) = Var({h}-min return)/"
                        f"({h}*Var(1-min return)), {seg_name}"
                    ),
                    directional=False,
                    null=1.0,
                    days=days,
                    keys=("winret", "minret"),
                    estimate_fn=vr_fn,
                    n_fn=lambda p: int(len(p["winret"])),
                )
            )
    return stats


# ================================================================================ F2 ====
def build_f2(
    day_arrays: dict[date, dict[str, np.ndarray]],
    eda_dates: list[date],
    wcache: dict,
) -> list[TestedStat]:
    stats: list[TestedStat] = []
    segments = (("RTH", RTH_BASE, RTH_LEN), ("ETH", ETH_BASE, ETH_LEN))

    # F2.1
    for seg_name, base, length in segments:
        for lag in (1, 5, 15, 60):
            days = []
            for d in eda_dates:
                x, y = raw_lag_abs(day_arrays[d], base, length, lag)
                days.append(DayObs(d, {"pred": x, "targ": y}))
            stats.append(
                TestedStat(
                    id=f"F2_1_lag{lag}_{seg_name}",
                    family="F2.1",
                    description=f"Autocorrelation of |1-min return| at lag {lag} min, {seg_name}",
                    directional=False,
                    null=0.0,
                    days=days,
                    keys=("pred", "targ"),
                    estimate_fn=lambda p: pearson_r(p["pred"], p["targ"]),
                    n_fn=lambda p: int(len(p["pred"])),
                )
            )

    # F2.2
    rv_by_date: dict[date, float | None] = {}
    for d in eda_dates:
        rr = all_raw_returns(day_arrays[d], RTH_BASE, RTH_LEN)
        rv_by_date[d] = float(np.sum(rr * rr)) if len(rr) else None
    days = []
    for i, d in enumerate(eda_dates):
        v1 = rv_by_date[d]
        v2 = rv_by_date[eda_dates[i + 1]] if i + 1 < len(eda_dates) else None
        if v1 is None or v2 is None:
            days.append(DayObs(d, {"pred": EMPTY, "targ": EMPTY}))
        else:
            days.append(DayObs(d, {"pred": np.array([v1]), "targ": np.array([v2])}))
    stats.append(
        TestedStat(
            id="F2_2_RV_autocorr_lag1",
            family="F2.2",
            description=(
                "Lag-1 autocorrelation of daily RTH realized variance across "
                "consecutive EDA dates"
            ),
            directional=False,
            null=0.0,
            days=days,
            keys=("pred", "targ"),
            estimate_fn=lambda p: pearson_r(p["pred"], p["targ"]),
            n_fn=lambda p: int(len(p["pred"])),
        )
    )

    # F2.3
    bucket_win = get_window_table(wcache, day_arrays, eda_dates, RTH_BASE, BUCKET_H, RTH_LEN)
    days = []
    for d in eda_dates:
        win = bucket_win[d]
        pred, targ = [], []
        for k in range(N_BUCKETS - 1):
            if k in win and (k + 1) in win:
                pred.append(win[k].ret)
                targ.append(win[k + 1].rvol)
        days.append(DayObs(d, {"pred": np.array(pred, dtype=float),
                                "targ": np.array(targ, dtype=float)}))
    stats.append(
        TestedStat(
            id="F2_3_leverage_asymmetry",
            family="F2.3",
            description=(
                "Correlation between a 30-min RTH bucket return and the next bucket's "
                "realized volatility"
            ),
            directional=False,
            null=0.0,
            days=days,
            keys=("pred", "targ"),
            estimate_fn=lambda p: pearson_r(p["pred"], p["targ"]),
            n_fn=lambda p: int(len(p["pred"])),
        )
    )

    # F2.4
    win_by_date = get_window_table(wcache, day_arrays, eda_dates, RTH_BASE, 15, RTH_LEN)
    records = []
    for d in eda_dates:
        da = day_arrays[d]
        win = win_by_date[d]
        valid, logret1 = da["valid"], da["logret1"]
        for k, w in win.items():
            nxt = win.get(k + 1)
            if nxt is None:
                continue
            trail_start = RTH_BASE + k * 15 - 60
            if trail_start < 0:
                continue
            seg = valid[trail_start : trail_start + 60]
            if not seg.all():
                continue
            lr = logret1[trail_start : trail_start + 60]
            trailvol = float(np.sqrt(np.sum(lr * lr)))
            records.append((d, w.ret, nxt.ret, w.ret, nxt.price_change / TICK, trailvol))
    trailvols = np.array([r[5] for r in records])
    if len(trailvols) >= 3:
        lo_edge, hi_edge = np.percentile(trailvols, [100 / 3, 200 / 3])
    else:
        lo_edge = hi_edge = math.nan
    for label, cond in (
        ("bottom", lambda v: v <= lo_edge),
        ("top", lambda v: v >= hi_edge),
    ):
        by_date: dict[date, list] = {d: [] for d in eda_dates}
        for d, pred, targ, sp, tk, tv in records:
            if cond(tv):
                by_date[d].append((pred, targ, sp, tk))
        days = []
        for d in eda_dates:
            rows = by_date[d]
            if rows:
                arr = np.array(rows, dtype=float)
                days.append(_pair_day(d, arr[:, 0], arr[:, 1], arr[:, 2], arr[:, 3]))
            else:
                days.append(_pair_day(d, EMPTY, EMPTY, EMPTY, EMPTY))
        stats.append(
            TestedStat(
                id=f"F2_4_15min_vol_tercile_{label}",
                family="F2.4",
                description=(
                    f"Lag-1 autocorrelation of 15-min RTH returns, {label} tercile of "
                    "trailing 60-min realized vol"
                ),
                directional=True,
                null=0.0,
                days=days,
                keys=PAIR_KEYS,
                estimate_fn=_corr_estimate_fn,
                edge_fn=_corr_edge_fn,
                n_fn=_corr_n_fn,
            )
        )
    return stats


# ================================================================================ F3 ====
def build_f3(
    day_arrays: dict[date, dict[str, np.ndarray]],
    eda_dates: list[date],
    wcache: dict,
) -> tuple[list[TestedStat], list[dict]]:
    bucket_win = get_window_table(wcache, day_arrays, eda_dates, RTH_BASE, BUCKET_H, RTH_LEN)

    # F3.1 -- descriptive only, not among the 57 tested statistics.
    f3_1_table = []
    for k in range(N_BUCKETS):
        rets = [bucket_win[d][k].ret for d in eda_dates if k in bucket_win[d]]
        arr = np.array(rets, dtype=float)
        n = len(arr)
        if n > 1 and float(arr.std(ddof=0)) > 0:
            mean = float(arr.mean())
            std = float(arr.std(ddof=1))
            pop_std = float(arr.std(ddof=0))
            m = arr - mean
            skew = float(np.mean(m**3) / pop_std**3)
            kurt = float(np.mean(m**4) / pop_std**4 - 3.0)
        else:
            mean = std = skew = kurt = None
        f3_1_table.append(
            {
                "bucket": bucket_label(k),
                "n": n,
                "mean_logret": mean,
                "std_logret": std,
                "skew": skew,
                "excess_kurtosis": kurt,
                "ineligible": True,
                "reason": (
                    "descriptive only per declaration; bucket means are clock "
                    "seasonality and cannot clear the drift benchmark in-sample"
                ),
            }
        )

    # F3.2
    stats: list[TestedStat] = []
    for k in range(N_BUCKETS - 1):
        days = []
        for d in eda_dates:
            win = bucket_win[d]
            w, nxt = win.get(k), win.get(k + 1)
            if w is not None and nxt is not None:
                days.append(
                    _pair_day(d, [w.ret], [nxt.ret], [w.ret], [nxt.price_change / TICK])
                )
            else:
                days.append(_pair_day(d, EMPTY, EMPTY, EMPTY, EMPTY))
        stats.append(
            TestedStat(
                id=f"F3_2_bucket{k + 1:02d}_bucket{k + 2:02d}",
                family="F3.2",
                description=(
                    f"Cross-day correlation between bucket {bucket_label(k)} return and "
                    f"bucket {bucket_label(k + 1)} return"
                ),
                directional=True,
                null=0.0,
                days=days,
                keys=PAIR_KEYS,
                estimate_fn=_corr_estimate_fn,
                edge_fn=_corr_edge_fn,
                n_fn=_corr_n_fn,
            )
        )

    # F3.3
    days_a, days_b = [], []
    for d in eda_dates:
        da = day_arrays[d]
        first_to_9 = _first_bar_to_0900(da)
        win = bucket_win[d]
        b1, b13 = win.get(0), win.get(N_BUCKETS - 1)
        if first_to_9 is not None and b13 is not None:
            days_a.append(
                _pair_day(
                    d, [first_to_9.ret], [b13.ret], [first_to_9.ret], [b13.price_change / TICK]
                )
            )
        else:
            days_a.append(_pair_day(d, EMPTY, EMPTY, EMPTY, EMPTY))
        if b1 is not None and b13 is not None:
            days_b.append(_pair_day(d, [b1.ret], [b13.ret], [b1.ret], [b13.price_change / TICK]))
        else:
            days_b.append(_pair_day(d, EMPTY, EMPTY, EMPTY, EMPTY))
    stats.append(
        TestedStat(
            id="F3_3_overnight_to_close_momentum",
            family="F3.3",
            description=(
                "Correlation of (first bar to 09:00 CT return) with the 14:30-15:00 "
                "return (literature-sourced, GHLZ/Baltussen form)"
            ),
            directional=True,
            null=0.0,
            days=days_a,
            keys=PAIR_KEYS,
            estimate_fn=_corr_estimate_fn,
            edge_fn=_corr_edge_fn,
            n_fn=_corr_n_fn,
        )
    )
    stats.append(
        TestedStat(
            id="F3_3_opening_30min_to_close_momentum",
            family="F3.3",
            description=(
                "Correlation of (08:30-09:00 return) with the 14:30-15:00 return "
                "(literature-sourced, GHLZ/Baltussen form)"
            ),
            directional=True,
            null=0.0,
            days=days_b,
            keys=PAIR_KEYS,
            estimate_fn=_corr_estimate_fn,
            edge_fn=_corr_edge_fn,
            n_fn=_corr_n_fn,
        )
    )
    return stats, f3_1_table


# ================================================================================ F4 ====
def build_f4(
    bars: pd.DataFrame,
    day_arrays: dict[date, dict[str, np.ndarray]],
    eda_dates: list[date],
) -> list[TestedStat]:
    stats: list[TestedStat] = []

    # F4.1
    events1 = {d: [] for d in eda_dates}
    for d in eda_dates:
        da = day_arrays[d]
        ref = da["open"][RTH_BASE]
        if np.isfinite(ref):
            events1[d] = scan_reference_crossings(da, range(960, 1290), float(ref), 15)
    days1 = [DayObs(d, {"ticks": np.array(events1[d], dtype=float)}) for d in eda_dates]
    stats.append(
        TestedStat(
            id="F4_1_rth_open_crossing",
            family="F4.1",
            description=(
                "Mean signed forward 15-min return (ticks) after a close crosses the "
                "RTH-open reference, 09:00-14:29 CT"
            ),
            directional=True,
            null=0.0,
            days=days1,
            keys=("ticks",),
            estimate_fn=lambda p: (float(np.mean(p["ticks"])) if len(p["ticks"]) else math.nan),
            n_fn=lambda p: int(len(p["ticks"])),
            edge_equals_estimate=True,
        )
    )

    # F4.2 and F4.3 share the prior-EDA-date reference close.
    events2 = {d: [] for d in eda_dates}
    gap_records: list[tuple[date, float, float]] = []
    for i, d in enumerate(eda_dates):
        if i == 0:
            continue
        prior = eda_dates[i - 1]
        da_prior, da = day_arrays[prior], day_arrays[d]
        prior_close = da_prior["close"][RTH_BASE + RTH_LEN - 1]
        prior_instr = da_prior["instr"][RTH_BASE + RTH_LEN - 1]
        cur_instr = da["instr"][RTH_BASE]
        open_0830 = da["open"][RTH_BASE]
        if not (
            np.isfinite(prior_close)
            and np.isfinite(prior_instr)
            and np.isfinite(cur_instr)
            and prior_instr == cur_instr
        ):
            continue
        events2[d] = scan_reference_crossings(da, range(930, 1290), float(prior_close), 15)
        if np.isfinite(open_0830):
            gap_ticks = (open_0830 - prior_close) / TICK
            rth_low = da["low"][RTH_BASE : RTH_BASE + RTH_LEN]
            rth_high = da["high"][RTH_BASE : RTH_BASE + RTH_LEN]
            filled = bool(np.any((rth_low <= prior_close) & (rth_high >= prior_close)))
            gap_records.append((d, abs(gap_ticks), 1.0 if filled else 0.0))

    days2 = [DayObs(d, {"ticks": np.array(events2[d], dtype=float)}) for d in eda_dates]
    stats.append(
        TestedStat(
            id="F4_2_prior_rth_close_crossing",
            family="F4.2",
            description=(
                "Mean signed forward 15-min return (ticks) after a close crosses the "
                "prior RTH-close reference, 08:30-14:29 CT"
            ),
            directional=True,
            null=0.0,
            days=days2,
            keys=("ticks",),
            estimate_fn=lambda p: (float(np.mean(p["ticks"])) if len(p["ticks"]) else math.nan),
            n_fn=lambda p: int(len(p["ticks"])),
            edge_equals_estimate=True,
        )
    )

    # F4.3
    abs_gaps = np.array([r[1] for r in gap_records])
    if len(abs_gaps) >= 3:
        g_lo, g_hi = np.percentile(abs_gaps, [100 / 3, 200 / 3])
    else:
        g_lo = g_hi = math.nan
    for label, cond in (
        ("low", lambda g: g <= g_lo),
        ("mid", lambda g: g_lo < g < g_hi),
        ("high", lambda g: g >= g_hi),
    ):
        by_date: dict[date, list[float]] = {d: [] for d in eda_dates}
        for d, g, filled in gap_records:
            if cond(g):
                by_date[d].append(filled)
        days3 = [DayObs(d, {"fill": np.array(by_date[d], dtype=float)}) for d in eda_dates]
        stats.append(
            TestedStat(
                id=f"F4_3_gap_fill_tercile_{label}",
                family="F4.3",
                description=(
                    f"P(RTH trades back to prior close by 15:00) | |gap| {label} tercile "
                    "(novelty check only, INELIGIBLE)"
                ),
                directional=False,
                null=0.0,
                days=days3,
                keys=("fill",),
                estimate_fn=lambda p: (
                    float(np.mean(p["fill"])) if len(p["fill"]) else math.nan
                ),
                n_fn=lambda p: int(len(p["fill"])),
            )
        )

    # F4.4
    ts = bars["ts_event"].to_numpy()
    trade_date_obj = bars["trade_date_obj"].to_numpy()
    close_ = bars["close"].to_numpy(dtype=float)
    high_ = bars["high"].to_numpy(dtype=float)
    low_ = bars["low"].to_numpy(dtype=float)
    gap0 = (bars["gap_before_minutes"] == 0).to_numpy()

    lo_price = float(np.nanmin(low_))
    hi_price = float(np.nanmax(high_))
    level_lo = math.floor(lo_price / 50.0) * 50.0 - 50.0
    level_hi = math.ceil(hi_price / 50.0) * 50.0 + 50.0
    n_levels = int(round((level_hi - level_lo) / 50.0)) + 1
    levels_50 = [level_lo + 50.0 * i for i in range(n_levels)]
    levels_100 = [lv for lv in levels_50 if lv % 100.0 == 0.0]
    control_levels = [lv + 12.5 for lv in levels_50] + [lv + 37.5 for lv in levels_50]

    scan_levels = sorted(set(levels_50) | set(control_levels))
    events_by_level = scan_round_levels(ts, trade_date_obj, close_, high_, low_, gap0, scan_levels)

    def collect(levels: list[float]) -> dict[date, list[float]]:
        out: dict[date, list[float]] = {d: [] for d in eda_dates}
        for lv in levels:
            for d, tk in events_by_level.get(lv, []):
                if d in out:
                    out[d].append(tk)
        return out

    round50 = collect(levels_50)
    round100 = collect(levels_100)
    control = collect(control_levels)

    for suffix, round_dict in (("50", round50), ("100", round100)):
        days4 = [
            DayObs(
                d,
                {
                    "round_ticks": np.array(round_dict[d], dtype=float),
                    "control_ticks": np.array(control[d], dtype=float),
                },
            )
            for d in eda_dates
        ]
        stats.append(
            TestedStat(
                id=f"F4_4_round_number_multiples_of_{suffix}",
                family="F4.4",
                description=(
                    f"Mean forward 15-min return from L (ticks), multiples of {suffix} vs "
                    "control levels (multiples of 50 offset +12.5/+37.5), any session, "
                    "30-min refractory per level"
                ),
                directional=True,
                null=0.0,
                days=days4,
                keys=("round_ticks", "control_ticks"),
                estimate_fn=lambda p: (
                    float(np.mean(p["round_ticks"]) - np.mean(p["control_ticks"]))
                    if len(p["round_ticks"]) and len(p["control_ticks"])
                    else math.nan
                ),
                edge_fn=lambda p: (
                    float(np.mean(p["round_ticks"])) if len(p["round_ticks"]) else math.nan
                ),
                n_fn=lambda p: int(len(p["round_ticks"])),
                extra_fn=lambda p: {
                    "control_mean_ticks": (
                        float(np.mean(p["control_ticks"])) if len(p["control_ticks"]) else None
                    ),
                    "n_control": int(len(p["control_ticks"])),
                },
            )
        )
    return stats


# ================================================================================ F5 ====
def build_f5(
    day_arrays: dict[date, dict[str, np.ndarray]],
    eda_dates: list[date],
    wcache: dict,
) -> list[TestedStat]:
    stats: list[TestedStat] = []
    bucket_win = get_window_table(wcache, day_arrays, eda_dates, RTH_BASE, BUCKET_H, RTH_LEN)

    # F5.1
    history = {k: deque(maxlen=20) for k in range(N_BUCKETS)}
    records1 = []
    for d in eda_dates:
        win = bucket_win[d]
        for k in range(N_BUCKETS - 1):
            w = win.get(k)
            if w is not None and len(history[k]) == 20:
                relvol = w.volume / (sum(history[k]) / 20.0)
                nxt = win.get(k + 1)
                if nxt is not None:
                    records1.append((d, w.ret, nxt.ret, w.ret, nxt.price_change / TICK, relvol))
        for k in range(N_BUCKETS):
            w = win.get(k)
            if w is not None:
                history[k].append(w.volume)
    relvols = np.array([r[5] for r in records1])
    lo1, hi1 = (
        np.percentile(relvols, [100 / 3, 200 / 3]) if len(relvols) >= 3 else (math.nan, math.nan)
    )
    for label, cond in (("bottom", lambda v: v <= lo1), ("top", lambda v: v >= hi1)):
        by_date: dict[date, list] = {d: [] for d in eda_dates}
        for d, pred, targ, sp, tk, rv in records1:
            if cond(rv):
                by_date[d].append((pred, targ, sp, tk))
        days = []
        for d in eda_dates:
            rows = by_date[d]
            if rows:
                arr = np.array(rows, dtype=float)
                days.append(_pair_day(d, arr[:, 0], arr[:, 1], arr[:, 2], arr[:, 3]))
            else:
                days.append(_pair_day(d, EMPTY, EMPTY, EMPTY, EMPTY))
        stats.append(
            TestedStat(
                id=f"F5_1_relvol_tercile_{label}",
                family="F5.1",
                description=(
                    "Lag-1 correlation of consecutive 30-min RTH bucket returns, "
                    f"{label} tercile of first bucket's relative volume (20-day trailing)"
                ),
                directional=True,
                null=0.0,
                days=days,
                keys=PAIR_KEYS,
                estimate_fn=_corr_estimate_fn,
                edge_fn=_corr_edge_fn,
                n_fn=_corr_n_fn,
            )
        )

    # F5.2
    records2 = []
    for d in eda_dates:
        win = bucket_win[d]
        for k in range(N_BUCKETS - 1):
            w, nxt = win.get(k), win.get(k + 1)
            if w is None or nxt is None or w.range_ <= 0:
                continue
            eff = abs(w.price_change) / w.range_
            records2.append((d, w.ret, nxt.ret, w.ret, nxt.price_change / TICK, eff))
    effs = np.array([r[5] for r in records2])
    lo2, hi2 = (
        np.percentile(effs, [100 / 3, 200 / 3]) if len(effs) >= 3 else (math.nan, math.nan)
    )
    for label, cond in (("bottom", lambda v: v <= lo2), ("top", lambda v: v >= hi2)):
        by_date = {d: [] for d in eda_dates}
        for d, pred, targ, sp, tk, ef in records2:
            if cond(ef):
                by_date[d].append((pred, targ, sp, tk))
        days = []
        for d in eda_dates:
            rows = by_date[d]
            if rows:
                arr = np.array(rows, dtype=float)
                days.append(_pair_day(d, arr[:, 0], arr[:, 1], arr[:, 2], arr[:, 3]))
            else:
                days.append(_pair_day(d, EMPTY, EMPTY, EMPTY, EMPTY))
        stats.append(
            TestedStat(
                id=f"F5_2_efficiency_tercile_{label}",
                family="F5.2",
                description=(
                    "Lag-1 correlation of consecutive 30-min RTH bucket returns, "
                    f"{label} tercile of first bucket's trend efficiency "
                    "|price change|/range"
                ),
                directional=True,
                null=0.0,
                days=days,
                keys=PAIR_KEYS,
                estimate_fn=_corr_estimate_fn,
                edge_fn=_corr_edge_fn,
                n_fn=_corr_n_fn,
            )
        )

    # F5.3
    all_obs = []
    for d in eda_dates:
        win = bucket_win[d]
        for k, w in win.items():
            if w.range_ > 0 and w.volume > 0:
                all_obs.append((d, k, math.log(w.range_), math.log(w.volume), w.ret))
    xv = np.array([o[3] for o in all_obs])
    yv = np.array([o[2] for o in all_obs])
    if len(xv) >= 2 and np.std(xv) > 0:
        b = float(np.cov(xv, yv, ddof=1)[0, 1] / np.var(xv, ddof=1))
        a = float(yv.mean() - b * xv.mean())
    else:
        a = b = 0.0
    resid = {(o[0], o[1]): o[2] - (a + b * o[3]) for o in all_obs}
    days3 = []
    for d in eda_dates:
        win = bucket_win[d]
        preds, targs, sps, tks = [], [], [], []
        for k in range(N_BUCKETS - 1):
            w, nxt = win.get(k), win.get(k + 1)
            if w is None or nxt is None or (d, k) not in resid:
                continue
            r = resid[(d, k)]
            pv = r * (1.0 if w.ret >= 0 else -1.0)
            preds.append(pv)
            targs.append(nxt.ret)
            sps.append(pv)
            tks.append(nxt.price_change / TICK)
        days3.append(_pair_day(d, preds, targs, sps, tks))
    stats.append(
        TestedStat(
            id="F5_3_range_volume_residual",
            family="F5.3",
            description=(
                "Correlation of (range-vs-volume OLS residual x sign(bucket return)) "
                "with the next bucket's return"
            ),
            directional=True,
            null=0.0,
            days=days3,
            keys=PAIR_KEYS,
            estimate_fn=_corr_estimate_fn,
            edge_fn=_corr_edge_fn,
            n_fn=_corr_n_fn,
        )
    )
    return stats


# ================================================================================ F6 ====
def build_f6(
    day_arrays: dict[date, dict[str, np.ndarray]],
    eda_dates: list[date],
    wcache: dict,
) -> list[TestedStat]:
    win60 = get_window_table(wcache, day_arrays, eda_dates, RTH_BASE, 60, RTH_LEN)
    days = []
    for d in eda_dates:
        da = day_arrays[d]
        eth_high_seg = da["high"][ETH_BASE : ETH_BASE + ETH_LEN]
        eth_low_seg = da["low"][ETH_BASE : ETH_BASE + ETH_LEN]
        has_eth = bool(np.any(~np.isnan(eth_high_seg)))
        eth_high = float(np.nanmax(eth_high_seg)) if has_eth else math.nan
        eth_low = float(np.nanmin(eth_low_seg)) if has_eth else math.nan
        open_0830 = da["open"][RTH_BASE]
        target_win = win60[d].get(0)
        if (
            math.isnan(eth_high)
            or math.isnan(eth_low)
            or eth_high <= eth_low
            or not np.isfinite(open_0830)
            or target_win is None
        ):
            days.append(_pair_day(d, EMPTY, EMPTY, EMPTY, EMPTY))
            continue
        position = (open_0830 - eth_low) / (eth_high - eth_low)
        days.append(
            _pair_day(
                d,
                [position],
                [target_win.ret],
                [position - 0.5],
                [target_win.price_change / TICK],
            )
        )
    stat = TestedStat(
        id="F6_1_overnight_range_position",
        family="F6.1",
        description=(
            "Correlation of (08:30 open position within ETH high-low range) with the "
            "08:30-09:30 return"
        ),
        directional=True,
        null=0.0,
        days=days,
        keys=PAIR_KEYS,
        estimate_fn=_corr_estimate_fn,
        edge_fn=_corr_edge_fn,
        n_fn=_corr_n_fn,
    )
    return [stat]


# ================================================================================ main ====
def _sanitize(obj):
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize(v) for v in obj]
    if isinstance(obj, np.floating):
        v = float(obj)
        return None if math.isnan(v) else v
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, float) and math.isnan(obj):
        return None
    return obj


def main() -> None:
    eda_dates, excluded, bars = resolve_eda_dates()
    bars = engineer_bars(bars)
    day_arrays = build_all_day_arrays(bars)

    wcache: dict = {}
    all_stats: list[TestedStat] = []
    all_stats += build_f1(day_arrays, eda_dates, wcache)
    all_stats += build_f2(day_arrays, eda_dates, wcache)
    f3_stats, f3_1_table = build_f3(day_arrays, eda_dates, wcache)
    all_stats += f3_stats
    all_stats += build_f4(bars, day_arrays, eda_dates)
    all_stats += build_f5(day_arrays, eda_dates, wcache)
    all_stats += build_f6(day_arrays, eda_dates, wcache)

    if len(all_stats) != M_STATS:
        raise AssertionError(f"expected {M_STATS} tested statistics, got {len(all_stats)}")
    ids = [s.id for s in all_stats]
    if len(set(ids)) != len(ids):
        raise AssertionError("duplicate statistic ids")

    sizes = split_equal(len(eda_dates), 4)
    subblock_map: dict[date, int] = {}
    pos = 0
    for b, size in enumerate(sizes):
        for d in eda_dates[pos : pos + size]:
            subblock_map[d] = b
        pos += size

    records = [compute_result(s, subblock_map) for s in all_stats]
    bh_flags(records, BH_Q)

    out = {
        "meta": {
            "declaration_sha256": DECL_SHA256,
            "eda_date_range": [eda_dates[0].isoformat(), eda_dates[-1].isoformat()],
            "n_eda_dates_before_exclusions": len(eda_dates) + len(excluded),
            "n_eda_dates_after_exclusions": len(eda_dates),
            "excluded_dates": excluded,
            "sub_block_sizes": sizes,
            "seed": SEED,
            "n_resamples": N_RESAMPLES,
            "mean_block_days": MEAN_BLOCK,
            "bh_fdr_q": BH_Q,
            "m_tested_statistics": M_STATS,
        },
        "implementation_choices": IMPLEMENTATION_CHOICES,
        "tested_statistics": records,
        "f3_1_descriptive_table": f3_1_table,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(_sanitize(out), indent=2))
    n_reject = sum(1 for r in records if r["bh_reject"])
    print(f"wrote {OUTPUT_PATH} ({len(records)} tested statistics, {n_reject} BH-significant)")


if __name__ == "__main__":
    main()
