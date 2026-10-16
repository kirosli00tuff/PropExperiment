"""E22-F1 rule core (lead_spec_B.md S3, S4, S8): pure functions, numpy and pandas only, no I/O.

Shared by the historical design study (microbook/) and the paper runner (forward/strategy.py), so
one implementation is frozen. Every constant comes from forward/config_f1.json (passed in as a
mapping); the sources are cited there and in reports/stage_e22_briefs/carver_sources.md (CS):

- vol: Carver's mixed volatility of daily PRICE DIFFERENCES (CS A12, C-VOL:121-188): EWMA std, span
  35, min 10, adjust=True; slow = EWMA (span = slow years x 256) of that vol; blend 0.3 slow + 0.7
  recent. Annual dollar volatility per contract = multiplier x 16 x daily vol (lead ruling, S3.4:
  sigma_% := sigma(dP) / P, so M x P x sigma_% = M x 16 x sigma(dP)).
- EWMAC (CS A1): (EWMA span f - EWMA span s of the back-adjusted price) / daily price vol, pandas
  ewm(span, min_periods=1); scaled by Carver's production scalar (S8 B-R1), capped +-20.
- Combined forecast: equal-weight mean of the four capped forecasts x FDM, capped +-20 (CS A8).
- Diversification multiplier: min(1 / sqrt(w' H w), 2.5), negative correlations floored at 0 (CS A9).
- Position: N = (F / 10) x C x tau x IDM x w / (annual $ vol per contract) (S3.5, CS A11).
- Simple rounding (S8 B-R3): rounded and buffered: buffer = 10% of the average position (the
  position at forecast +10), the optimal, top and bottom rounded half away from zero; trade to the
  buffer edge (CS A13, A13b).
- Greedy (S8 B-R4, CS B.1): minimum tracking error plus shadow-cost penalty, start at zero, one
  contract at a time in the direction of the optimum's sign, stop when no step improves; then the
  November 2021 tracking-error buffer (steps 1-3, adjustment factor max((x - b) / x, 0)).
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import numpy as np
import pandas as pd

ANNUALISE = 16.0  # sqrt(256): CS A12c


# ------------------------------------------------------------------ volatility ----
def ewma_std(diffs: pd.Series, span: float, min_periods: int) -> pd.Series:
    """pandas ewm(adjust=True, span).std() (bias-corrected), as C-VOL:188."""
    return diffs.ewm(adjust=True, span=span, min_periods=min_periods).std()


def mixed_vol(diffs: pd.Series, *, days: float = 35, min_periods: int = 10,
              slow_vol_years: float = 10, business_days: float = 256.0,
              proportion_of_slow_vol: float = 0.3, vol_abs_min: float = 1e-10) -> pd.Series:
    """Carver's mixed_vol_calc on daily price differences (CS A12): the daily price vol."""
    vol = ewma_std(diffs, days, min_periods)
    long_vol = vol.ewm(span=slow_vol_years * business_days).mean()
    out = long_vol * proportion_of_slow_vol + vol * (1.0 - proportion_of_slow_vol)
    return out.where(out.isna() | (out >= vol_abs_min), vol_abs_min)


def vol_from_config(diffs: pd.Series, cfg: Mapping) -> pd.Series:
    v = cfg["vol"]
    return mixed_vol(diffs, days=v["recent_span"]["value"],
                     min_periods=v["min_periods"]["value"],
                     slow_vol_years=v["slow_vol_years"]["value"],
                     business_days=v["business_days_per_year"]["value"],
                     proportion_of_slow_vol=v["proportion_of_slow_vol"]["value"],
                     vol_abs_min=v["vol_abs_min"]["value"])


def annual_dollar_vol(daily_price_vol: pd.Series | np.ndarray | float, multiplier: float):
    """Annual dollar volatility of one contract: multiplier x 16 x daily price-difference vol."""
    return multiplier * ANNUALISE * daily_price_vol


# ------------------------------------------------------------------ forecasts ----
def ewmac_raw(price: pd.Series, vol: pd.Series, fast: int, slow: int) -> pd.Series:
    """CS A1: (ewm(span=fast).mean() - ewm(span=slow).mean()) / vol.ffill(), min_periods=1."""
    fast_ewma = price.ewm(span=fast, min_periods=1).mean()
    slow_ewma = price.ewm(span=slow, min_periods=1).mean()
    return (fast_ewma - slow_ewma) / vol.ffill()


def cap(x, limit: float):
    """Clip to [-limit, +limit] (NaN stays NaN)."""
    return np.clip(x, -limit, limit)


def speed_forecasts(price: pd.Series, vol: pd.Series, speeds: Sequence[Sequence[int]],
                    scalars: Sequence[float], forecast_cap: float) -> pd.DataFrame:
    """Scaled and capped forecast per speed (columns 'f/s')."""
    cols = {}
    for (f, s), sc in zip(speeds, scalars, strict=True):
        cols[f"{f}/{s}"] = cap(ewmac_raw(price, vol, f, s) * sc, forecast_cap)
    return pd.DataFrame(cols, index=price.index)


def combine_forecasts(speed_fc: pd.DataFrame, fdm: float, forecast_cap: float,
                      weights: Sequence[float] | None = None) -> pd.Series:
    """Weighted mean of the capped speed forecasts x FDM, capped (CS A8)."""
    w = np.full(speed_fc.shape[1], 1.0 / speed_fc.shape[1]) if weights is None \
        else np.asarray(weights, dtype=float)
    return cap(speed_fc.mul(w, axis=1).sum(axis=1, min_count=speed_fc.shape[1]) * fdm,
               forecast_cap)


def forecasts_from_config(price: pd.Series, vol: pd.Series, cfg: Mapping, *,
                          fdm: float | None = None) -> tuple[pd.DataFrame, pd.Series]:
    e = cfg["ewmac"]
    speeds = [tuple(x) for x in e["speeds"]["value"]]
    scalars = [e["scalars"]["value"][f"{f}/{s}"] for f, s in speeds]
    fc_cap = cfg["forecast_cap"]["value"]
    sp = speed_forecasts(price, vol, speeds, scalars, fc_cap)
    fdm_v = cfg["fdm"]["value"] if fdm is None else fdm
    return sp, combine_forecasts(sp, fdm_v, fc_cap)


# ------------------------------------------------------------------ diversification ----
def floor_corr(corr: np.ndarray, floor: float = 0.0) -> np.ndarray:
    out = np.array(corr, dtype=float, copy=True)
    out[out < floor] = floor
    np.fill_diagonal(out, 1.0)
    return out


def div_multiplier(corr: np.ndarray, weights: np.ndarray, *, floor_at_zero: bool = True,
                   dm_max: float = 2.5) -> float:
    """min(1 / sqrt(w' H w), dm_max), H floored at 0 when ``floor_at_zero`` (CS A9)."""
    h = floor_corr(corr) if floor_at_zero else np.asarray(corr, dtype=float)
    w = np.asarray(weights, dtype=float)
    risk = float(w @ h @ w)
    if not risk > 0:
        return dm_max
    return float(min(1.0 / math.sqrt(risk), dm_max))


def idm_for_live(full_corr: np.ndarray, live: np.ndarray, dm_max: float = 2.5) -> float:
    """S3.5: the same formula on the live sub-matrix, equal weights over the live instruments."""
    idx = np.flatnonzero(live)
    if len(idx) == 0:
        return 0.0
    sub = np.asarray(full_corr)[np.ix_(idx, idx)]
    return div_multiplier(sub, np.full(len(idx), 1.0 / len(idx)), dm_max=dm_max)


# ------------------------------------------------------------------ positions ----
def unrounded_position(forecast, capital: float, tau: float, idm: float, weight,
                       dollar_vol):
    """S3.5: N = (F / 10) x C x tau x IDM x w / (annual $ vol per contract)."""
    return (np.asarray(forecast, dtype=float) / 10.0) * capital * tau * idm \
        * np.asarray(weight, dtype=float) / np.asarray(dollar_vol, dtype=float)


def average_position(capital: float, tau: float, idm: float, weight, dollar_vol):
    """The position at forecast +10 (CS A13: the buffer's base)."""
    return unrounded_position(10.0, capital, tau, idm, weight, dollar_vol)


def round_half_away(x):
    """Round half away from zero (S4 / S8 B-R3); works on scalars and arrays."""
    a = np.asarray(x, dtype=float)
    out = np.sign(a) * np.floor(np.abs(a) + 0.5)
    return out + 0.0 if out.ndim else float(out) + 0.0


def buffered_round(optimal, avg_position, last, buffer_size: float = 0.10):
    """CS A13b with trade_to_edge: optimal, top = optimal + B, bottom = optimal - B, each rounded
    (half away from zero); B = buffer_size x |average position|. last > top -> top; last <
    bottom -> bottom; else hold ``last``. Returns integer-valued floats."""
    opt = np.asarray(optimal, dtype=float)
    b = buffer_size * np.abs(np.asarray(avg_position, dtype=float))
    top = round_half_away(opt + b)
    bot = round_half_away(opt - b)
    lst = np.asarray(last, dtype=float)
    out = np.where(lst > top, top, np.where(lst < bot, bot, lst))
    return out + 0.0 if np.ndim(out) else float(out) + 0.0


# ------------------------------------------------------------------ covariance ----
def covariance(corr: np.ndarray, dollar_vol: np.ndarray) -> np.ndarray:
    """Annual dollar covariance of one contract of each instrument: D rho D."""
    d = np.asarray(dollar_vol, dtype=float)
    return np.asarray(corr, dtype=float) * np.outer(d, d)


def ew_corr_pairwise(returns: np.ndarray, span: float, min_periods: int, clip: float,
                     offdiag: float = 0.0) -> np.ndarray:
    """Exponentially weighted correlation of the columns of ``returns`` (rows oldest first,
    NaN = missing), pairwise-complete: for each pair, the rows where both are present, weighted
    (1 - alpha)^age with age counted over those rows from the latest, alpha = 2 / (span + 1)
    (pandas ewm(span, ignore_na=True) weights). Fewer than ``min_periods`` common rows: ``offdiag``.
    Clipped to [-clip, clip] (CS B.2, C-DEF instrument_returns_correlation)."""
    r = np.asarray(returns, dtype=float)
    n = r.shape[1]
    out = np.full((n, n), offdiag, dtype=float)
    np.fill_diagonal(out, 1.0)
    if r.shape[0] == 0:
        return out
    decay = 1.0 - 2.0 / (span + 1.0)
    ok = ~np.isnan(r)
    for i in range(n):
        for j in range(i + 1, n):
            m = ok[:, i] & ok[:, j]
            k = int(m.sum())
            if k < min_periods:
                continue
            x, y = r[m, i], r[m, j]
            w = decay ** np.arange(k - 1, -1, -1, dtype=float)
            w /= w.sum()
            mx, my = float(w @ x), float(w @ y)
            cx, cy = x - mx, y - my
            vx, vy = float(w @ (cx * cx)), float(w @ (cy * cy))
            if vx <= 0 or vy <= 0:
                continue
            c = float(w @ (cx * cy)) / math.sqrt(vx * vy)
            out[i, j] = out[j, i] = float(np.clip(c, -clip, clip))
    return out


def shrink_corr(corr: np.ndarray, shrinkage: float | None, offdiag: float = 0.0) -> np.ndarray:
    """shrinkage x prior + (1 - shrinkage) x corr, prior = 1 on the diagonal and ``offdiag``
    elsewhere (C-CORR:95 shrink_to_offdiag). None or 0: unchanged."""
    c = np.asarray(corr, dtype=float)
    if not shrinkage:
        return c
    prior = np.full_like(c, offdiag)
    np.fill_diagonal(prior, 1.0)
    return shrinkage * prior + (1.0 - shrinkage) * c


def correlation_from_config(returns: np.ndarray, cfg: Mapping) -> np.ndarray:
    """The greedy's correlation from sampled returns, by config greedy.correlation."""
    c = cfg["greedy"]["correlation"]
    corr = ew_corr_pairwise(returns, c["ew_span"]["value"], int(c["min_periods"]["value"]),
                            c["clip"]["value"], c["offdiag"]["value"])
    return shrink_corr(corr, c["shrinkage"]["value"], c["offdiag"]["value"])


def sampled_returns(cum_index: np.ndarray, index_days: np.ndarray, decision_day: int,
                    step_days: int, n_steps: int) -> np.ndarray:
    """Returns over consecutive ``step_days`` calendar windows ending at ``decision_day``
    (ordinal days), from cumulated return indices (rows = dates ascending, columns = instruments,
    NaN before an instrument's first value): the index is carried forward to each sample point;
    a window with an undefined end point is NaN. Rows oldest first."""
    pts = decision_day - step_days * np.arange(n_steps, -1, -1)
    pos = np.searchsorted(index_days, pts, side="right") - 1
    vals = np.full((len(pts), cum_index.shape[1]), np.nan)
    good = pos >= 0
    vals[good] = cum_index[pos[good]]
    return np.diff(vals, axis=0)


# ------------------------------------------------------------------ the greedy optimiser ----
def tracking_error(gap: np.ndarray, cov: np.ndarray, capital: float) -> float:
    """Annualised tracking error as a fraction of capital: sqrt(g' Sigma g) / C (CS B.1 step 2;
    in contract space: weights = contracts x value per contract / capital)."""
    g = np.asarray(gap, dtype=float)
    v = float(g @ cov @ g)
    if v < -1e-9:
        raise ValueError("negative tracking-error variance")
    return math.sqrt(max(v, 0.0)) / capital


@dataclass(frozen=True)
class GreedyResult:
    positions: np.ndarray  # integer-valued
    steps: int
    objective: float


def greedy_integer(optimal: np.ndarray, prior: np.ndarray, cov: np.ndarray,
                   cost_per_contract: np.ndarray, capital: float, shadow_cost: float,
                   max_steps: int = 100_000) -> GreedyResult:
    """CS B.1 steps 2, 4, 5: minimise sqrt(gap' Sigma gap) / C + shadow x sum |cost x (n - prior)|
    / C over integer n, greedily: start at zero; each pass tries one contract more in the
    direction sign(optimal) (sign(0) = +1, C-GEN) on every instrument and keeps the single best
    improvement; stop when no step improves the objective."""
    opt = np.asarray(optimal, dtype=float)
    pri = np.asarray(prior, dtype=float)
    cst = np.asarray(cost_per_contract, dtype=float)
    cov = np.asarray(cov, dtype=float)
    direction = np.where(opt < 0, -1.0, 1.0)
    n = np.zeros_like(opt)
    gap = n - opt
    sg = cov @ gap
    var = float(gap @ sg)
    diag = np.diag(cov)
    cost_now = np.abs(cst * (n - pri))
    cost_sum = float(cost_now.sum())

    def obj(v: float, c: float) -> float:
        return math.sqrt(max(v, 0.0)) / capital + shadow_cost * c / capital

    best = obj(var, cost_sum)
    steps = 0
    while steps < max_steps:
        new_var = var + 2.0 * direction * sg + diag
        new_cost_i = np.abs(cst * (n + direction - pri))
        new_cost = cost_sum - cost_now + new_cost_i
        vals = np.sqrt(np.maximum(new_var, 0.0)) / capital + shadow_cost * new_cost / capital
        i = int(np.argmin(vals))
        if not vals[i] < best:
            break
        best = float(vals[i])
        n[i] += direction[i]
        var = float(new_var[i])
        sg = sg + direction[i] * cov[:, i]
        cost_sum = float(new_cost[i])
        cost_now[i] = new_cost_i[i]
        steps += 1
    return GreedyResult(n + 0.0, steps, best)


@dataclass(frozen=True)
class OptimiseResult:
    positions: np.ndarray
    stage: str  # "inside buffer" | "no trade (integer optimum = current)" |
    # "no trade (x <= buffer)" | "no trade (trades round to 0)" | "traded"
    te_prior_unrounded: float
    te_prior_rounded: float | None
    adjustment: float | None
    greedy_steps: int
    greedy_all_zero: bool


def dynamic_optimise(optimal: np.ndarray, prior: np.ndarray, cov: np.ndarray,
                     cost_per_contract: np.ndarray, capital: float, *, shadow_cost: float,
                     te_buffer: float) -> OptimiseResult:
    """The November 2021 version (CS B.1 step 6): 1) TE(prior vs unrounded optimal) < buffer:
    keep the prior; 2) greedy integer positions; 3) x = TE(prior vs integer), adjustment =
    max((x - b) / x, 0); trades = adjustment x (integer - prior), rounded half away from zero;
    new = prior + rounded trades."""
    opt = np.asarray(optimal, dtype=float)
    pri = np.asarray(prior, dtype=float)
    te_u = tracking_error(pri - opt, cov, capital)
    if te_u < te_buffer:
        return OptimiseResult(pri + 0.0, "inside buffer", te_u, None, None, 0, False)
    g = greedy_integer(opt, pri, cov, cost_per_contract, capital, shadow_cost)
    x = tracking_error(pri - g.positions, cov, capital)
    all_zero = bool(not np.any(g.positions))
    adj = max((x - te_buffer) / x, 0.0) if x > 0 else 0.0
    if adj <= 0:
        stage = "no trade (integer optimum = current)" if x == 0 else "no trade (x <= buffer)"
        return OptimiseResult(pri + 0.0, stage, te_u, x, adj, g.steps, all_zero)
    trades = round_half_away(adj * (g.positions - pri))
    stage = "traded" if np.any(trades) else "no trade (trades round to 0)"
    return OptimiseResult(pri + trades, stage, te_u, x, adj, g.steps, all_zero)


# ------------------------------------------------------------------ yield proxy (study) ----
def yield_proxy_diffs(dp, price, duration: float):
    """S3.6: dy (bp) = -dP / PVBP, PVBP = P x D / 10,000 price points per bp (P = the held
    contract's mark on the same date as dP)."""
    return -np.asarray(dp, dtype=float) / (np.asarray(price, dtype=float) * duration / 10_000.0)


__all__ = ["ANNUALISE", "GreedyResult", "OptimiseResult", "annual_dollar_vol", "average_position",
           "buffered_round", "cap", "combine_forecasts", "correlation_from_config", "covariance", "div_multiplier",
           "dynamic_optimise", "ew_corr_pairwise", "ewma_std", "ewmac_raw", "floor_corr",
           "forecasts_from_config", "greedy_integer", "idm_for_live", "mixed_vol",
           "round_half_away", "sampled_returns", "shrink_corr", "speed_forecasts", "tracking_error",
           "unrounded_position", "vol_from_config", "yield_proxy_diffs"]
