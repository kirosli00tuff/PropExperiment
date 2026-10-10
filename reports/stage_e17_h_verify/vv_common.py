"""Shared helpers for the E.17 H1-H5 verdict recomputation (VerdictVerifier-FableXHigh).

Independent of base_rules: every statistic here is written from lead_spec.md section 5 and
reports/stage_e16_prereg_common.md; the DSR follows screening/stage_e_verdict.py (moments with the
population sd, raw kurtosis) and funnel.multiple_comparisons.deflated_sharpe_ratio, re-implemented.
"""
from __future__ import annotations

import json
import math
import os
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Iterator

import numpy as np
from scipy import stats as sps

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
RUNS = REPO / "reports/stage_e17_runs"
OUT = REPO / "reports/stage_e17_h_verify"
TESTS = ("H1", "H2", "H3", "H4", "H5")
CASES = ("base", "stress", "slip150")
NW_LAGS = {"H1": 5, "H2": 1, "H3": 3, "H4": 5, "H5": 5}
YEAR_MIN_UNITS = {"H1": 10, "H2": 6, "H3": 10, "H4": 10, "H5": 10}
HOLM_ALPHA = 0.05
MIN_N = 30
EULER_MASCHERONI = 0.5772156649015329

os.nice(10)


def money(value) -> Fraction:
    """A money field of a units row: int, or a str Fraction such as '3125/4' (cents)."""
    if isinstance(value, str):
        return Fraction(value)
    return Fraction(value)


def iter_units(test: str, traded_only: bool = True) -> Iterator[dict]:
    """Stream the units file row by row; never loads the file whole."""
    with open(RUNS / f"{test}_units.jsonl", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if traded_only and row.get("status") != "traded":
                continue
            yield row


# ------------------------------------------------------------------ statistics
def plain_t(xs: np.ndarray) -> dict:
    n = len(xs)
    mean = float(np.mean(xs))
    sd = float(np.std(xs, ddof=1)) if n > 1 else float("nan")
    t = mean / (sd / math.sqrt(n)) if sd > 0 else float("nan")
    p = float(sps.t.sf(t, n - 1)) if sd > 0 else float("nan")
    return {"n": n, "mean": mean, "sd": sd, "t": t, "p_t": p}


def newey_west_t(xs: np.ndarray, lag: int) -> dict:
    """HAC t with a Bartlett kernel and `lag` lags on the demeaned series; one-sided normal p."""
    n = len(xs)
    mean = float(np.mean(xs))
    e = xs - mean
    gamma0 = float(np.dot(e, e)) / n
    s = gamma0
    for k in range(1, lag + 1):
        w = 1.0 - k / (lag + 1.0)
        gk = float(np.dot(e[k:], e[:-k])) / n
        s += 2.0 * w * gk
    if s <= 0:
        return {"lag": lag, "t_nw": float("nan"), "p_nw": float("nan"), "se_nw": float("nan")}
    se = math.sqrt(s / n)
    t_nw = mean / se
    return {"lag": lag, "t_nw": t_nw, "p_nw": float(sps.norm.sf(t_nw)), "se_nw": se}


def year_stability(dates: list[str], xs: np.ndarray, min_units: int) -> dict:
    """Net P&L positive in at least two thirds of the calendar years holding >= min_units units;
    fewer than 3 such years FAILS (lead_spec section 5)."""
    by_year: dict[str, list[float]] = defaultdict(list)
    for d, x in zip(dates, xs):
        by_year[d[:4]].append(float(x))
    table = {y: {"units": len(v), "net_sum": float(sum(v)), "positive": sum(v) > 0}
             for y, v in sorted(by_year.items())}
    qualifying = [y for y, r in table.items() if r["units"] >= min_units]
    positive = [y for y in qualifying if table[y]["positive"]]
    passed = len(qualifying) >= 3 and 3 * len(positive) >= 2 * len(qualifying)
    return {"min_units": min_units, "years": table, "qualifying_years": len(qualifying),
            "positive_years": len(positive), "pass": bool(passed)}


def describe(test: str, dates: list[str], xs: np.ndarray) -> dict:
    out = plain_t(xs)
    out.update(newey_west_t(xs, NW_LAGS[test]))
    out["p"] = max(out["p_t"], out["p_nw"])
    out["year_stability"] = year_stability(dates, xs, YEAR_MIN_UNITS[test])
    out["sd_pop"] = float(np.std(xs, ddof=0))
    out["first_date"], out["last_date"] = dates[0], dates[-1]
    return out


def holm(pvalues: dict[str, float], alpha: float = HOLM_ALPHA) -> dict:
    """Holm step-down at family-wise alpha over m = len(pvalues) hypotheses."""
    m = len(pvalues)
    order = sorted(pvalues.items(), key=lambda kv: kv[1])
    rejected: dict[str, bool] = {}
    steps = []
    stop = False
    for i, (key, p) in enumerate(order, start=1):
        threshold = alpha / (m - i + 1)
        reject = (not stop) and (p <= threshold)
        if not reject:
            stop = True
        rejected[key] = reject
        steps.append({"step": i, "test": key, "p": p, "threshold": threshold, "reject": reject})
    return {"alpha": alpha, "m": m, "steps": steps, "rejected": rejected}


# ------------------------------------------------------------------------- DSR
def moments(xs: np.ndarray) -> dict:
    """screening.stage_e_verdict.moments: n, mean, POPULATION sd, skew, raw kurtosis, sharpe."""
    n = len(xs)
    mean = float(np.mean(xs))
    sd = float(np.std(xs, ddof=0))
    if sd == 0:
        return {"n": n, "mean": mean, "sd": 0.0, "skew": 0.0, "kurtosis": 3.0, "sharpe": 0.0}
    z = (xs - mean) / sd
    return {"n": n, "mean": mean, "sd": sd, "skew": float(np.mean(z ** 3)),
            "kurtosis": float(np.mean(z ** 4)), "sharpe": mean / sd}


def expected_max_sharpe(n_trials: int, sharpe_variance: float) -> float:
    if n_trials == 1:
        return 0.0
    g = EULER_MASCHERONI
    term = ((1 - g) * sps.norm.ppf(1 - 1.0 / n_trials)
            + g * sps.norm.ppf(1 - 1.0 / (n_trials * math.e)))
    return math.sqrt(sharpe_variance) * float(term)


def deflated_sharpe(mom: dict, n_trials: int, sharpe_variance: float) -> dict:
    if mom["sd"] <= 0:
        return {"dsr": None, "undefined": "sd = 0"}
    benchmark = expected_max_sharpe(n_trials, sharpe_variance)
    sr = mom["sharpe"]
    denom_sq = 1.0 - mom["skew"] * sr + 0.25 * (mom["kurtosis"] - 1.0) * sr ** 2
    if denom_sq <= 0:
        return {"dsr": None, "undefined": f"degenerate variance term {denom_sq}"}
    z = (sr - benchmark) * math.sqrt(mom["n"] - 1) / math.sqrt(denom_sq)
    return {"dsr": float(sps.norm.cdf(z)), "z": z, "expected_max_sharpe": benchmark,
            "undefined": None}


def dsr_table(series: dict[str, np.ndarray], n_trials: int) -> dict:
    """stage_e_verdict.dsr_table: the Sharpe variance is the POPULATION variance of the per-unit
    Sharpes over `series` (here the five base-case series); DSR per member at N trials."""
    moms = {k: moments(v) for k, v in series.items()}
    sharpes = [m["sharpe"] for m in moms.values()]
    variance = float(np.var(sharpes, ddof=0))
    return {"n_trials": n_trials, "variance_over": list(series), "sharpe_variance": variance,
            "expected_max_sharpe_under_null": expected_max_sharpe(n_trials, variance),
            "moments": moms,
            "dsr": {k: deflated_sharpe(moms[k], n_trials, variance) for k in series}}


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=1, sort_keys=False, default=str)
