"""E.32b economics, core logic (spec section 4 E): grid, thresholds, grid confirmation. No simulator import here.

The model is E.28's (A3_funnel.py / A3_models.py, copied unchanged). For one pair and one "curve" (a per-trade law:
T round trips a day, per-trade SD sigma_T ticks, tick value v), the expected net cash per cycle EV and the 250-day
probability P10K depend on the gross edge mu only through d = mu - c (common random numbers), so one cache keyed by
d serves every cost c on that curve (the primary and spread1 share the primary curve).

Market case only (E.28's limit case is not used): c = c_mkt = F_rt / v + S_rt, mu on the grid k * 0.01 ticks,
k = 0..K with K = 100 * max(4, ceil(0.30 sigma_60)).
  mu*_mkt   = the smallest grid mu with EV >= 0               (None: above the grid cap)
  mu10K_mkt = the smallest grid mu with P10K >= 0.5           (None: above the grid cap)
Search: E.28's bisection on k (invariant f(lo) < 0 <= f(hi), after f(K) and f(0)), then E.28's grid confirmation
(A3_gridcheck.py) generalised to the market case and the cap K: every k = 0 mod 10 below the threshold (0.10-tick
sub-grid) and the region ends, every k in the 0.10 ticks below it, then every grid point of a sub-grid gap with an
end near the threshold (EV >= -max(5 SE, USD 100), or P10K >= 0.40). A checked point below the threshold with
f >= 0 replaces the bisection value by the smallest grid point with f >= 0 (the spec's definition).
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

STEP = 0.01  # grid step, ticks
GRID_FLOOR_TICKS = 4  # the cap is at least 4 ticks (spec 4)
CAP_SIGMA_FRAC = 0.30  # cap = max(4, ceil(0.30 sigma_60)) ticks (spec 4)
T_MAX = 20  # at most 20 round trips a day (spec 0)
COARSE = 10  # confirmation sub-grid, grid units (0.10 tick), E.28 A3_gridcheck.COARSE
DENSE_BELOW = 10  # grid points checked densely below each threshold, E.28 A3_gridcheck.DENSE_BELOW
NEAR_SE = 5.0  # E.28 A3_gridcheck.NEAR_SE
NEAR_USD = 100.0  # E.28 A3_gridcheck.NEAR_USD
NEAR_P = 0.40  # E.28 A3_gridcheck.NEAR_P
P_TARGET = 0.5  # mu10K: P(net cash >= USD 10,000 within 250 trading days) >= 0.5
D_ROUND = 9  # cache key and law input: d rounded to 1e-9 ticks (E.28 PairEval.at key)

Evaluator = Callable[[float], dict[str, Any]]


def grid_cap_ticks(sigma60: float) -> int:
    """max(4, ceil(0.30 sigma_60)) in whole ticks; the product is rounded to 1e-9 first so that 0.30 * 20 = 6."""
    if sigma60 is None or not math.isfinite(sigma60) or sigma60 <= 0:
        raise ValueError(f"sigma_60 must be a positive number, got {sigma60!r}")
    return max(GRID_FLOOR_TICKS, math.ceil(round(CAP_SIGMA_FRAC * sigma60, 9)))


def grid_cap_k(sigma60: float) -> int:
    return 100 * grid_cap_ticks(sigma60)


def trades_per_day(l_main_min: float, h_min: int) -> int:
    """T = min(20, floor(L_main / h)) (spec 4, E_dir60 and E_dir at h). 0 when the main session is shorter than h."""
    if l_main_min is None or l_main_min <= 0 or h_min <= 0:
        raise ValueError(f"L_main and h must be positive, got {l_main_min!r}, {h_min!r}")
    return min(T_MAX, math.floor(round(l_main_min / h_min, 9)))


def d_of(k: int, c: float) -> float:
    return round(k * STEP - c, D_ROUND)


def mu_of(k: int | None) -> float | None:
    return None if k is None else round(k * STEP, 2)


class Curve:
    """Cached evaluations of one pair on one per-trade law: d -> {"ev", "se", "p10k", "stats"}."""

    def __init__(self, evaluate: Evaluator) -> None:
        self._evaluate = evaluate
        self.cache: dict[float, dict[str, Any]] = {}
        self.n_evals = 0

    def at(self, d: float) -> dict[str, Any]:
        key = round(d, D_ROUND)
        if key not in self.cache:
            r = dict(self._evaluate(key))
            r["d"] = key
            self.cache[key] = r
            self.n_evals += 1
        return self.cache[key]

    def f(self, k: int, c: float, what: str) -> float:
        r = self.at(d_of(k, c))
        return r["ev"] if what == "ev" else r["p10k"] - P_TARGET

    def has(self, k: int, c: float) -> bool:
        return d_of(k, c) in self.cache


def bisect_smallest(curve: Curve, c: float, what: str, k_max: int) -> int | None:
    """E.28 PairEval.smallest on [0, k_max]: None if f(k_max) < 0, else the bisection's smallest k with f >= 0."""
    lo, hi = 0, k_max
    if curve.f(hi, c, what) < 0:
        return None
    if curve.f(lo, c, what) >= 0:
        return lo
    while hi - lo > 1:  # invariant f(lo) < 0 <= f(hi)
        mid = (lo + hi) // 2
        if curve.f(mid, c, what) >= 0:
            hi = mid
        else:
            lo = mid
    return hi


def _near(r: dict[str, Any], what: str) -> bool:
    if what == "p10k":
        return r["p10k"] >= NEAR_P
    return r["ev"] >= -max(NEAR_SE * r["se"], NEAR_USD)


def _checked(curve: Curve, c: float, lo: int, top: int) -> list[int]:
    return [k for k in range(lo, top) if curve.has(k, c)]


def _dense_fill(curve: Curve, c: float, what: str, top: int) -> int:
    """Evaluate every grid point of each gap between checked points of [0, top) that has an end near the
    threshold (E.28 A3_gridcheck._fill)."""
    filled = 0
    ks = _checked(curve, c, 0, top)
    for a, b in zip(ks, ks[1:], strict=False):
        if b - a <= 1:
            continue
        if _near(curve.at(d_of(a, c)), what) or _near(curve.at(d_of(b, c)), what):
            for k in range(a + 1, b):
                curve.at(d_of(k, c))
            filled += 1
    return filled


def confirm(curve: Curve, c: float, what: str, k_star: int | None, k_max: int) -> dict[str, Any]:
    """E.28's grid confirmation of one threshold on [0, k_star) (the whole grid [0, k_max] when above the cap)."""
    top = k_max + 1 if k_star is None else k_star
    if top <= 0:
        return {"n_checked": 0, "violations": [], "confirmed": True, "k_final": k_star, "n_dense_filled_gaps": 0}
    pts = {k for k in range(0, top) if k % COARSE == 0} | {0, top - 1}
    if k_star is not None:
        pts |= set(range(max(k_star - DENSE_BELOW, 0), k_star))
    for k in sorted(pts):
        curve.at(d_of(k, c))
    n_fill = _dense_fill(curve, c, what, top)
    ks = _checked(curve, c, 0, top)
    vals = [(k, curve.f(k, c, what)) for k in ks]
    viol = [k for k, x in vals if x >= 0]
    kmax, xmax = max(vals, key=lambda t: t[1])
    out: dict[str, Any] = {"n_checked": len(ks), "n_dense_filled_gaps": n_fill,
                           "max_below": {"k": kmax, "f": xmax,
                                         "se": curve.at(d_of(kmax, c))["se"] if what == "ev" else None},
                           "violations": viol, "confirmed": not viol, "k_final": k_star}
    if viol:  # the smallest grid point with f >= 0: fill densely below the first violation
        first = viol[0]
        prev = max([k for k in ks if k < first], default=0)
        for k in range(prev, first):
            curve.at(d_of(k, c))
        out["k_final"] = min(k for k in range(0, first + 1) if curve.has(k, c) and curve.f(k, c, what) >= 0)
    return out


def threshold(curve: Curve, c: float, what: str, k_max: int) -> dict[str, Any]:
    """Bisection then confirmation; the final value is the confirmed (or corrected) smallest grid k."""
    k_bis = bisect_smallest(curve, c, what, k_max)
    conf = confirm(curve, c, what, k_bis, k_max)
    k = conf["k_final"]
    return {"k_bisection": k_bis, "k": k, "mu": mu_of(k), "above_cap": k is None,
            "f_at_k": None if k is None else curve.f(k, c, what),
            "f_at_k_minus_1": None if k is None or k == 0 else curve.f(k - 1, c, what),
            "confirmation": conf}


@dataclass(frozen=True)
class CostCase:
    """One market cost on a curve: name (primary, spread1, E_dir60, E_dir30, ...), F_rt, v, S_rt."""

    name: str
    f_rt_usd: float
    v_usd: float
    s_rt_ticks: float

    @property
    def c_lim(self) -> float:
        return self.f_rt_usd / self.v_usd

    @property
    def c_mkt(self) -> float:
        return self.f_rt_usd / self.v_usd + self.s_rt_ticks


def in_sigma(mu: float | None, sigma60: float | None) -> float | None:
    return None if mu is None or not sigma60 else mu / sigma60


def evaluate_case(curve: Curve, case: CostCase, k_max: int, sigma60: float | None) -> dict[str, Any]:
    """mu*_mkt and mu10K_mkt on [0, k_max] for one cost, plus the cost per attempt (E.28: evaluation fees per
    attempt at mu = 0, limit case: d = -F_rt / v; the market-case mu = 0 value is reported beside it)."""
    c = case.c_mkt
    ev = threshold(curve, c, "ev", k_max)
    p = threshold(curve, c, "p10k", k_max)
    at0_lim = curve.at(round(-case.c_lim, D_ROUND))
    at0_mkt = curve.at(d_of(0, c))
    return {"mu_star_mkt": ev["mu"], "mu10K_mkt": p["mu"],
            "above_cap": {"mu_star": ev["above_cap"], "mu10K": p["above_cap"]},
            "cost_per_attempt": at0_lim["stats"]["eval_fees_per_attempt"],
            "cost_per_attempt_mkt_mu0": at0_mkt["stats"]["eval_fees_per_attempt"],
            "sigma60": sigma60, "m_star": in_sigma(ev["mu"], sigma60), "m10K": in_sigma(p["mu"], sigma60),
            "grid_cap": round(k_max * STEP, 2),
            "F_rt_usd": case.f_rt_usd, "v_usd": case.v_usd, "S_rt_ticks": case.s_rt_ticks,
            "c_lim_ticks": case.c_lim, "c_mkt_ticks": c,
            "search": {"mu_star_mkt": ev, "mu10K_mkt": p}}
