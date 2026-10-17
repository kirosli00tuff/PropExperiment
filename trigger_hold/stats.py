"""Statistics per trigger-hold, window and case; Holm; the discovery survivor rule; DSR and CSCV
PBO; the confirmation composite (lead_spec sections 4 and 7).

- y: the book's daily net values on its series dates; mean, sd (ddof 1), Sharpe = mean / sd x
  sqrt(252); raw t = mean / (sd / sqrt n); NW t with Bartlett lags h (base_rules.stats.
  newey_west_se).
- Alpha: OLS y = a + b1 v_T1 + b2 v_T2 + e. se_HAC: the sandwich (X'X)^-1 S (X'X)^-1 with
  S = sum_t e_t^2 x_t x_t' + sum_{l=1}^{L} w_l sum_t e_t e_{t-l} (x_t x_{t-l}' + x_{t-l} x_t'),
  w_l = 1 - l / (h + 1), L = min(h, n - 1): the kernel and normalization of newey_west_se
  (with no regressor it IS newey_west_se, tested). Plain OLS se: s^2 (X'X)^-1, s^2 = e'e/(n-3).
  p_alpha = max(one-sided Student p of the plain t, n - 3 df; one-sided normal p of t_NW).
  A rank-deficient design (fewer than 3 independent columns, n <= 3) leaves alpha undefined
  (p None: never rejected, still counted in Holm's m).
- Holm: base_rules.stats.holm at one-sided 0.05. DSR: base_rules.stats.dsr_at_n (screening.
  stage_e_verdict's moments and dsr_table). PBO: screening.stage_e_verdict.pbo (CSCV, 8
  contiguous blocks) on the series aligned to the union of their dates, zero off a series' own
  dates (stage_e_verdict.aligned_series, D.1f ruling (a)).
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from datetime import date
from typing import Any

import numpy as np

from base_rules.stats import dsr_at_n, holm, newey_west_se, one_sided_p_normal, one_sided_p_t
from trigger_hold import constants as K


def sharpe(values: Sequence[float]) -> float | None:
    x = np.asarray(values, dtype=float)
    if len(x) < 2:
        return None
    sd = float(x.std(ddof=1))
    return None if sd == 0 else float(x.mean()) / sd * math.sqrt(K.SHARPE_ANNUALIZATION)


def raw_stats(values: Sequence[float], lags: int) -> dict[str, Any]:
    x = np.asarray(values, dtype=float)
    n = len(x)
    out: dict[str, Any] = {"n": n, "mean": float(x.mean()) if n else None, "sd": None,
                           "sharpe": None, "t": None, "t_nw": None, "nw_lags": lags}
    if n < 2:
        return out
    sd = float(x.std(ddof=1))
    out["sd"] = sd
    if sd == 0:
        return out
    mean = float(x.mean())
    out["sharpe"] = mean / sd * math.sqrt(K.SHARPE_ANNUALIZATION)
    out["t"] = mean / (sd / math.sqrt(n))
    se = newey_west_se(x, lags)
    out["t_nw"] = mean / se if se > 0 else None
    return out


def hac_sandwich(X: np.ndarray, e: np.ndarray, lags: int) -> np.ndarray:
    """(X'X)^-1 S (X'X)^-1 with newey_west_se's Bartlett kernel (module docstring)."""
    n = X.shape[0]
    xe = X * e[:, None]
    S = xe.T @ xe
    for lag in range(1, min(lags, n - 1) + 1):
        w = 1.0 - lag / (lags + 1.0)
        g = xe[lag:].T @ xe[:-lag]
        S += w * (g + g.T)
    inv = np.linalg.inv(X.T @ X)
    return inv @ S @ inv


def alpha_ols(y: Sequence[float], regressors: Sequence[Sequence[float]], lags: int
              ) -> dict[str, Any]:
    """OLS of y on a constant and ``regressors`` with the HAC and plain alpha t (section 4)."""
    yv = np.asarray(y, dtype=float)
    n = len(yv)
    cols = [np.ones(n), *[np.asarray(r, dtype=float) for r in regressors]]
    if any(len(c) != n for c in cols):
        raise ValueError("y and the regressors differ in length")
    k = len(cols)
    out: dict[str, Any] = {"n": n, "k": k, "lags": lags, "alpha": None, "betas": None,
                           "t_plain": None, "t_nw": None, "se_plain": None, "se_hac": None,
                           "p_plain": None, "p_nw": None, "p_alpha": None, "r2": None,
                           "corr": None, "undefined": None}
    X = np.column_stack(cols)
    if n <= k or np.linalg.matrix_rank(X) < k:
        out["undefined"] = "rank-deficient design or n <= k"
        return out
    beta, *_ = np.linalg.lstsq(X, yv, rcond=None)
    e = yv - X @ beta
    sse = float(e @ e)
    sst = float(((yv - yv.mean()) ** 2).sum())
    s2 = sse / (n - k)
    inv = np.linalg.inv(X.T @ X)
    se_plain = math.sqrt(max(s2 * float(inv[0, 0]), 0.0))
    se_hac = math.sqrt(max(float(hac_sandwich(X, e, lags)[0, 0]), 0.0))
    a = float(beta[0])
    t_plain = a / se_plain if se_plain > 0 else None
    t_nw = a / se_hac if se_hac > 0 else None
    p_plain = one_sided_p_t(t_plain, n - k) if t_plain is not None else None
    p_nw = one_sided_p_normal(t_nw) if t_nw is not None else None
    out.update({"alpha": a, "betas": [float(b) for b in beta[1:]], "se_plain": se_plain,
                "se_hac": se_hac, "t_plain": t_plain, "t_nw": t_nw, "p_plain": p_plain,
                "p_nw": p_nw, "r2": (1.0 - sse / sst) if sst > 0 else None,
                "corr": [_corr(yv, c) for c in cols[1:]]})
    if p_plain is not None and p_nw is not None:
        out["p_alpha"] = max(p_plain, p_nw)
    else:
        out["undefined"] = "zero standard error"
    return out


def _corr(a: np.ndarray, b: np.ndarray) -> float | None:
    if a.std() == 0 or b.std() == 0:
        return None
    return float(np.corrcoef(a, b)[0, 1])


def per_year(series: Sequence[tuple[date, float]]) -> dict[str, dict]:
    years: dict[int, list[float]] = {}
    for d, v in series:
        years.setdefault(d.year, []).append(float(v))
    return {str(y): {"n": len(v), "mean": float(np.mean(v)), "sharpe": sharpe(v)}
            for y, v in sorted(years.items())}


def case_record(series: Sequence[tuple[date, float]], v_t1: Sequence[float],
                v_t2: Sequence[float], h: int, buy_hold: Sequence[float] | None = None
                ) -> dict[str, Any]:
    """Section 4. ``alpha3`` (addition (b), DESCRIPTIVE only, never part of a bar): the same OLS
    with the root's buy-and-hold daily return as a third regressor."""
    y = [v for _, v in series]
    out = {"raw": raw_stats(y, h), "alpha": alpha_ols(y, [v_t1, v_t2], h),
           "per_year": per_year(series)}
    if buy_hold is not None:
        out["alpha3_descriptive"] = alpha_ols(y, [v_t1, v_t2, buy_hold], h)
    return out


def holm05(pvalues: Mapping[str, float | None]) -> dict[str, bool]:
    return holm(pvalues, alpha=K.HOLM_ALPHA)


def _key(row: Mapping[str, Any]) -> tuple[float, float]:
    t = row.get("t_nw")
    s = row.get("sharpe")
    return (-math.inf if t is None else t, -math.inf if s is None else s)


def discovery_survivors(rows: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    """Section 7: ``rows`` maps each of the K registered trigger-hold ids to its BASE-case
    {"p_alpha", "t_nw", "sharpe"} (None when not read: inconclusive by design, undefined).
    Holm over all K; a survivor needs Holm rejection, t_NW >= 2.0 and Sharpe >= 0.3; at most 4:
    the largest t_NW, ties by the larger Sharpe, then by id (ascending) so the order is total."""
    rejected = holm05({k: r.get("p_alpha") for k, r in rows.items()})
    checks = {}
    for k, r in rows.items():
        t, s = r.get("t_nw"), r.get("sharpe")
        checks[k] = {"holm_rejects": rejected[k], "t_nw_at_least_2": t is not None and t >= K.T_BAR,
                     "sharpe_at_least_0.3": s is not None and s >= K.SHARPE_BAR}
    eligible = [k for k, ch in checks.items() if all(ch.values())]
    ranked = sorted(eligible, key=lambda k: (*(-x for x in _key(rows[k])), k))
    return {"k": len(rows), "holm_alpha": K.HOLM_ALPHA, "checks": checks, "eligible": eligible,
            "ranked": ranked, "survivors": ranked[:K.MAX_SURVIVORS],
            "cut_by_cap": ranked[K.MAX_SURVIVORS:]}


def aligned(series: Mapping[str, Sequence[tuple[date, float]]]) -> tuple[list[date],
                                                                          dict[str, np.ndarray]]:
    grid = sorted({d for s in series.values() for d, _ in s})
    index = {d: i for i, d in enumerate(grid)}
    out = {}
    for k, s in series.items():
        v = np.zeros(len(grid))
        for d, x in s:
            v[index[d]] = x
        out[k] = v
    return grid, out


def pbo_cscv(series: Mapping[str, Sequence[tuple[date, float]]]) -> dict[str, Any]:
    from screening.stage_e_verdict import pbo

    if len(series) < 2:
        return {"pbo": None, "undefined": "fewer than two series"}
    grid, vals = aligned(series)
    try:
        return {**pbo(vals), "aligned_dates": len(grid), "first": str(grid[0]),
                "last": str(grid[-1])}
    except ValueError as exc:
        return {"pbo": None, "undefined": str(exc)}


def dsr(series: Mapping[str, Sequence[float]], n_trials: int) -> dict[str, Any]:
    return dsr_at_n(series, n_trials)


def dsr_with_variance(member: Sequence[float], variance_over: Mapping[str, Sequence[float]],
                      n_trials: int) -> dict[str, Any]:
    """One series' DSR with the Sharpe variance taken over ``variance_over`` (the K discovery
    series; confirmation, Questions for the lead Q4)."""
    from screening.stage_e_verdict import dsr_table, moments

    keys = [k for k, v in variance_over.items() if len(v) >= 2]
    if len(keys) < 2 or len(member) < 2:
        return {"n_trials": n_trials, "dsr": None, "undefined": "fewer than two series"}
    moms = {k: moments(variance_over[k]) for k in keys}
    moms["__member__"] = moments(member)
    tab = dsr_table(moms, keys, n_trials, ["__member__"])
    return {**{k: v for k, v in tab.items() if k not in ("dsr", "undefined")},
            "dsr": tab["dsr"]["__member__"], "undefined": tab["undefined"].get("__member__")}


def confirmation_hurdle(n_survivors: int) -> float:
    from scipy.stats import norm

    if n_survivors < 1:
        return K.T_BAR
    return max(K.T_BAR, float(norm.ppf(1.0 - K.HOLM_ALPHA / n_survivors)))


def confirmation_verdicts(rows: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    """Section 7: ``rows`` maps each discovery survivor to {"status": "read" | INCONCLUSIVE |
    UNCONFIRMABLE, and for a read one: "p_alpha", "t_nw", "sharpe_base", "sharpe_stress",
    "dsr", "pbo_discovery"}. Holm over ALL the survivors (S, gated ones included, p None)."""
    rejected = holm05({k: (r.get("p_alpha") if r.get("status") == "read" else None)
                       for k, r in rows.items()})
    out = {}
    for k, r in rows.items():
        if r.get("status") != "read":
            out[k] = {"verdict": r.get("status"), "checks": None}
            continue
        t, sb, ss = r.get("t_nw"), r.get("sharpe_base"), r.get("sharpe_stress")
        d, p = r.get("dsr"), r.get("pbo_discovery")
        checks = {"holm_rejects": rejected[k], "t_nw_at_least_2": t is not None and t >= K.T_BAR,
                  "base_sharpe_at_least_0.3": sb is not None and sb >= K.SHARPE_BAR,
                  "stress_sharpe_positive": ss is not None and ss > 0,
                  "dsr_above_0.95": d is not None and d > K.DSR_MIN,
                  "pbo_below_0.5": p is not None and p < K.PBO_MAX}
        out[k] = {"verdict": K.PASS if all(checks.values()) else K.NULL, "checks": checks}
    return {"s": len(rows), "holm_alpha": K.HOLM_ALPHA, "rows": out}


__all__ = ["aligned", "alpha_ols", "case_record", "confirmation_hurdle", "confirmation_verdicts",
           "discovery_survivors", "dsr", "dsr_with_variance", "hac_sandwich", "holm05",
           "pbo_cscv", "per_year", "raw_stats", "sharpe"]
