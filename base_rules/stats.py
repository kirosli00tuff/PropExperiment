"""Statistics and the pass bar (lead_spec section 5).

Per test and cost case: n, mean, sd (ddof 1), t = mean / (sd / sqrt n); the one-sided p is the
LARGER of the plain-t p (Student t, n - 1 df) and the Newey-West p (normal; Bartlett weights,
lags fixed per test: H1, H4, H5 5; H2 1; H3 3). Holm at family-wise 0.05 across the registered
tests on the base case. Pass: Holm rejects, mean > 0, n >= 30, year stability (net P&L positive in
at least two thirds of the calendar years holding at least 10 units, H2 6; fewer than 3 such years
fails). Reported beside, never part of the bar: the stress and 1.5 x slippage cases, DSR at the
program's N (screening.stage_e_verdict's moments and dsr_table, the program's existing function).
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from datetime import date
from fractions import Fraction

import numpy as np

from base_rules import constants as K


def newey_west_se(x: np.ndarray, lags: int) -> float:
    """HAC standard error of the mean (Bartlett kernel, ``lags`` lags)."""
    n = len(x)
    e = x - x.mean()
    s = float(e @ e) / n
    for lag in range(1, min(lags, n - 1) + 1):
        w = 1.0 - lag / (lags + 1.0)
        s += 2.0 * w * float(e[lag:] @ e[:-lag]) / n
    return math.sqrt(max(s, 0.0) / n)


def one_sided_p_t(t: float, df: int) -> float:
    from scipy.stats import t as student_t  # scipy ships with the pinned lightgbm

    return float(student_t.sf(t, df))


def one_sided_p_normal(z: float) -> float:
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def unit_stats(values: Sequence[float], lags: int) -> dict:
    x = np.asarray(values, dtype=float)
    n = len(x)
    if n < 2:
        return {"n": n, "mean": float(x.mean()) if n else None, "sd": None, "t": None,
                "p_t": None, "p_nw": None, "p": None, "nw_lags": lags}
    mean, sd = float(x.mean()), float(x.std(ddof=1))
    if sd == 0:
        return {"n": n, "mean": mean, "sd": 0.0, "t": None, "p_t": None, "p_nw": None,
                "p": None, "nw_lags": lags}
    t = mean / (sd / math.sqrt(n))
    se_nw = newey_west_se(x, lags)
    t_nw = mean / se_nw if se_nw > 0 else math.copysign(math.inf, mean)
    p_t, p_nw = one_sided_p_t(t, n - 1), one_sided_p_normal(t_nw)
    return {"n": n, "mean": mean, "sd": sd, "t": t, "t_nw": t_nw, "p_t": p_t, "p_nw": p_nw,
            "p": max(p_t, p_nw), "nw_lags": lags}


def holm(pvalues: Mapping[str, float | None], alpha: float = K.HOLM_ALPHA) -> dict[str, bool]:
    """Holm's step-down: sort ascending, reject p_(i) <= alpha / (m - i) while it holds. A test
    with no p (undefined) is never rejected and still counts in m."""
    m = len(pvalues)
    order = sorted(pvalues, key=lambda k: (math.inf if pvalues[k] is None else pvalues[k], k))
    out = {k: False for k in pvalues}
    for i, k in enumerate(order):
        p = pvalues[k]
        if p is None or p > alpha / (m - i):
            break
        out[k] = True
    return out


def year_table(series: Sequence[tuple[date, float]], min_units: int) -> dict:
    years: dict[int, list[float]] = {}
    for d, v in series:
        years.setdefault(d.year, []).append(float(v))
    rows = {str(y): {"units": len(v), "net": float(sum(v)), "qualifies": len(v) >= min_units,
                     "positive": sum(v) > 0} for y, v in sorted(years.items())}
    q = [r for r in rows.values() if r["qualifies"]]
    pos = sum(r["positive"] for r in q)
    passed = len(q) >= K.YEAR_MIN_QUALIFYING and Fraction(pos, len(q)) >= K.YEAR_POSITIVE_SHARE
    return {"min_units": min_units, "qualifying_years": len(q), "positive_years": pos,
            "passes": bool(passed), "years": rows}


def stats_for_test(test: str, series: Mapping[str, Sequence[tuple[date, float]]]) -> dict:
    """Every case's statistics and year table for one test."""
    return {case: {**unit_stats([v for _, v in series[case]], K.NW_LAGS[test]),
                   "year_stability": year_table(series[case], K.YEAR_MIN_UNITS[test])}
            for case in K.COST_CASES if case in series}


def dsr_at_n(series: Mapping[str, Sequence[float]], n_trials: int) -> dict:
    """DSR per test at the program's N, the Sharpe variance taken across the given tests
    (screening.stage_e_verdict.dsr_table; reported only)."""
    from screening.stage_e_verdict import dsr_table, moments

    keys = [k for k, v in series.items() if len(v) >= 2]
    if len(keys) < 2:
        return {"n_trials": n_trials, "undefined": "fewer than two tests with a series"}
    moms = {k: moments(series[k]) for k in keys}
    return dsr_table(moms, keys, n_trials, keys)


def verdict(stats: Mapping[str, Mapping], n_trials: int | None = None,
            series: Mapping[str, Sequence[float]] | None = None) -> dict:
    """Holm (base case) across the registered tests and the pass bar per test."""
    base = {t: s[K.BASE] for t, s in stats.items()}
    rejected = holm({t: b["p"] for t, b in base.items()})
    out = {}
    for t, b in base.items():
        checks = {"holm_rejects": rejected[t], "mean_positive": (b["mean"] or 0) > 0,
                  "n_at_least_30": b["n"] >= K.MIN_UNITS,
                  "year_stability": b["year_stability"]["passes"]}
        out[t] = {"pass": all(checks.values()), "checks": checks, "p": b["p"],
                  "mean": b["mean"], "n": b["n"]}
    report = {"holm_alpha": K.HOLM_ALPHA, "tests": out,
              "reported_cases": {t: {c: {k: s[c].get(k) for k in ("n", "mean", "t", "p")}
                                     for c in (K.STRESS, K.SLIP150) if c in s}
                                 for t, s in stats.items()}}
    if n_trials is not None and series is not None:
        report["dsr"] = dsr_at_n(series, n_trials)
    return report


__all__ = ["dsr_at_n", "holm", "newey_west_se", "one_sided_p_normal", "one_sided_p_t",
           "stats_for_test", "unit_stats", "verdict", "year_table"]
