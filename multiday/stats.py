"""Statistics and the pass bar (F6, lead_spec section 9).

Per test and cost case: n, mean, sd (ddof 1), t, the one-sided p as the LARGER of the plain-t p
(Student t, n - 1 df) and the Newey-West p (normal; Bartlett lags 21 for T1, T2, T4 and 5 for
T3): base_rules.stats.unit_stats. Annualized net Sharpe = mean / sd x sqrt(252); its 95% interval
from a circular moving-block bootstrap (block 21, 10,000 resamples, a fresh
numpy.random.default_rng(20261014) per test, percentiles 2.5 and 97.5). Holm's step-down at family
alpha 0.025 over the four tests (base_rules.stats.holm). PASS iff Holm rejects AND Sharpe >= 0.3.
Reported only: the stress and 1.5 x slippage cases, per year, per root, DSR at N.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from datetime import date

import numpy as np

from base_rules.stats import dsr_at_n, holm, unit_stats
from multiday import constants as K


def sharpe(values: Sequence[float]) -> float | None:
    x = np.asarray(values, dtype=float)
    if len(x) < 2:
        return None
    sd = float(x.std(ddof=1))
    return None if sd == 0 else float(x.mean()) / sd * math.sqrt(K.SHARPE_ANNUALIZATION)


def block_indices(rng: np.random.Generator, n: int, draws: int, block: int) -> np.ndarray:
    """Circular moving-block resample indices, shape (draws, n): ceil(n / block) block starts per
    draw, uniform on 0..n-1, each block start + 0..block-1 modulo n, concatenated, cut to n."""
    nb = -(-n // block)
    starts = rng.integers(0, n, size=(draws, nb))
    idx = (starts[:, :, None] + np.arange(block)[None, None, :]) % n
    return idx.reshape(draws, nb * block)[:, :n]


def bootstrap_sharpe(values: Sequence[float], *, seed: int = K.BOOT_SEED,
                     draws: int = K.BOOT_DRAWS, block: int = K.BOOT_BLOCK,
                     chunk: int = K.BOOT_CHUNK) -> dict:
    """The circular block bootstrap of the annualized Sharpe (a fresh generator per call; the
    chunking only bounds memory: the draws are taken in the same order)."""
    x = np.asarray(values, dtype=float)
    n = len(x)
    if n < 2:
        return {"lo": None, "hi": None, "draws": 0, "undefined_draws": 0}
    rng = np.random.default_rng(seed)
    out = []
    left = draws
    while left > 0:
        m = min(chunk, left)
        sample = x[block_indices(rng, n, m, block)]
        mean, sd = sample.mean(axis=1), sample.std(axis=1, ddof=1)
        with np.errstate(divide="ignore", invalid="ignore"):
            out.append(np.where(sd > 0, mean / sd * math.sqrt(K.SHARPE_ANNUALIZATION), np.nan))
        left -= m
    sh = np.concatenate(out)
    undefined = int(np.isnan(sh).sum())
    lo, hi = (np.nanpercentile(sh, K.BOOT_PERCENTILES) if undefined < len(sh)
              else (np.nan, np.nan))
    return {"lo": float(lo), "hi": float(hi), "draws": draws, "block": block, "seed": seed,
            "percentiles": list(K.BOOT_PERCENTILES), "undefined_draws": undefined}


def case_stats(values: Sequence[float], lags: int) -> dict:
    return {**unit_stats(values, lags), "sharpe_annualized": sharpe(values)}


def per_year(series: Sequence[tuple[date, float]]) -> dict[str, dict]:
    years: dict[int, list[float]] = {}
    for d, v in series:
        years.setdefault(d.year, []).append(float(v))
    return {str(y): {"n": len(v), "mean": float(np.mean(v)), "sharpe_annualized": sharpe(v),
                     "sum": float(np.sum(v))} for y, v in sorted(years.items())}


def own_t(values: Sequence[float]) -> float | None:
    x = np.asarray(values, dtype=float)
    if len(x) < 2 or float(x.std(ddof=1)) == 0:
        return None
    return float(x.mean()) / (float(x.std(ddof=1)) / math.sqrt(len(x)))


def holm_025(pvalues: Mapping[str, float | None]) -> dict[str, bool]:
    """Holm's step-down at family alpha 0.025: p ascending, reject while p_(k) <= 0.025 /
    (m - k + 1), stop at the first failure (an undefined p is never rejected, counts in m)."""
    return holm(pvalues, alpha=K.HOLM_ALPHA)


def verdict(base: Mapping[str, Mapping], boots: Mapping[str, Mapping]) -> dict:
    """PASS per test iff Holm rejects (base case) AND the annualized net Sharpe >= 0.3."""
    rejected = holm_025({t: b.get("p") for t, b in base.items()})
    tests = {}
    for t, b in base.items():
        sh = b.get("sharpe_annualized")
        checks = {"holm_rejects": bool(rejected[t]),
                  "sharpe_at_least_bar": sh is not None and sh >= K.SHARPE_BAR}
        tests[t] = {"pass": all(checks.values()), "checks": checks, "p": b.get("p"),
                    "p_t": b.get("p_t"), "p_nw": b.get("p_nw"), "t": b.get("t"),
                    "t_nw": b.get("t_nw"), "n": b.get("n"), "mean": b.get("mean"),
                    "sharpe_annualized": sh, "sharpe_ci95": boots.get(t)}
    return {"holm_alpha": K.HOLM_ALPHA, "sharpe_bar": K.SHARPE_BAR, "tests": tests}


__all__ = ["block_indices", "bootstrap_sharpe", "case_stats", "dsr_at_n", "holm_025",
           "own_t", "per_year", "sharpe", "verdict"]
