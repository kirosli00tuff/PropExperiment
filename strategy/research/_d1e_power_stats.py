"""Stage D.1e Task 3: the inference core - variance, sample size, simulation.

Split out of ``strategy/research/_d1e_power.py`` unchanged (the repo caps a file
at 800 lines); the rationale for every formula here is in that module's
docstring. Nothing in this module reads a file or knows about a member.
"""

from __future__ import annotations

import math
from statistics import NormalDist
from typing import Any

import numpy as np

from funnel.null_generator import stationary_bootstrap_indices

# ------------------------------------------------------------- constants ----

HOLM_FAMILY_SIZE = 58
ALPHA = 0.05
POWER_TARGET = 0.80
UCB_LEVEL = 0.95

MEAN_BLOCK = 5.0
BOOTSTRAP_RENEWAL_P = 1.0 / MEAN_BLOCK
MAX_LAG_K = 20
VIF_FLOOR_FRACTION = 0.2

REPLICATIONS = 2000
SPOT_REPLICATES = 200
SPOT_INNER_B = 1000
MIN_SIM_N = 2  # an autocovariance needs at least two observations

_ND = NormalDist()
Z_POWER = _ND.inv_cdf(POWER_TARGET)
Z_UCB = _ND.inv_cdf(UCB_LEVEL)
Z_HOLM = _ND.inv_cdf(1.0 - ALPHA / HOLM_FAMILY_SIZE)
ALPHA_HOLM = ALPHA / HOLM_FAMILY_SIZE


# ------------------------------------------------------------ statistics ----


def sample_autocovariances(x: np.ndarray, k_max: int = MAX_LAG_K) -> np.ndarray:
    """gamma_k for k = 0..min(k_max, n-1), 1/n divisor. Last axis is time."""
    values = np.asarray(x, dtype=float)
    n = values.shape[-1]
    if n < 2:
        raise ValueError("need at least two observations for an autocovariance")
    lags = min(k_max, n - 1)
    centred = values - values.mean(axis=-1, keepdims=True)
    out = np.empty(centred.shape[:-1] + (lags + 1,), dtype=float)
    out[..., 0] = np.einsum("...i,...i->...", centred, centred) / n
    for k in range(1, lags + 1):
        head, tail = centred[..., :-k], centred[..., k:]
        out[..., k] = np.einsum("...i,...i->...", head, tail) / n
    return out


def bootstrap_variance(x: np.ndarray, k_max: int = MAX_LAG_K) -> tuple[Any, Any, Any]:
    """Politis-Romano stationary-bootstrap variance V_B, gamma_0 and the floor flag."""
    gammas = sample_autocovariances(x, k_max)
    gamma0 = gammas[..., 0]
    lags = np.arange(1, gammas.shape[-1], dtype=float)
    weights = (1.0 - BOOTSTRAP_RENEWAL_P) ** lags
    raw = gamma0 + 2.0 * (weights * gammas[..., 1:]).sum(axis=-1)
    floor_value = VIF_FLOOR_FRACTION * gamma0
    hit_floor = raw <= floor_value
    return np.where(hit_floor, floor_value, raw), gamma0, hit_floor


def variance_inflation(x: np.ndarray, k_max: int = MAX_LAG_K) -> tuple[float, bool]:
    """VIF_boot = V_B / gamma_0 for a single series; 1.0 for a constant series."""
    v_b, gamma0, hit_floor = bootstrap_variance(np.asarray(x, dtype=float), k_max)
    if float(gamma0) <= 0.0:
        return 1.0, bool(hit_floor)
    return float(v_b) / float(gamma0), bool(hit_floor)


def lag1_autocorrelation(x: np.ndarray) -> float:
    gammas = sample_autocovariances(x, 1)
    gamma0 = float(gammas[0])
    return float(gammas[1]) / gamma0 if gamma0 > 0.0 else 0.0


def analytic_sample_size(z_level: float, sd_day: float, vif: float, eps_day: float) -> int:
    """One-sided n for 80% power at ``z_level``; see the module docstring."""
    if eps_day <= 0.0 or sd_day <= 0.0:
        return 0
    return int(math.ceil((((z_level + Z_POWER) * sd_day * math.sqrt(vif)) / eps_day) ** 2))


def interpolate_threshold(
    ns: list[int], powers: list[float], target: float = POWER_TARGET
) -> float | None:
    """Smallest grid n reaching ``target``, refined linearly in log(n).

    The power curve is close to linear in log(n) near 0.80, so the bracketing
    grid points are joined in log space rather than in n. ``None`` means the
    curve never reaches the target anywhere on the grid.
    """
    hits = [i for i, p in enumerate(powers) if p >= target]
    if not hits:
        return None
    i = hits[0]
    if i == 0:
        return float(ns[0])
    n_lo, n_hi = float(ns[i - 1]), float(ns[i])
    p_lo, p_hi = powers[i - 1], powers[i]
    if p_hi <= p_lo:
        return n_hi
    frac = (target - p_lo) / (p_hi - p_lo)
    return float(math.exp(math.log(n_lo) + frac * (math.log(n_hi) - math.log(n_lo))))


def threshold_is_censored(
    ns: list[int], powers: list[float], target: float = POWER_TARGET
) -> bool:
    """True when the SHORTEST simulated length already meets the target.

    The crossing is then below every length simulated and was never bracketed,
    so the returned figure is an upper bound on the simulated threshold, not a
    measurement of it. Such a figure never overrides the analytic sample size.
    """
    return bool(powers) and powers[0] >= target


def _binomial_se(p: float, n: int) -> float:
    return math.sqrt(max(p * (1.0 - p), 0.0) / n)


# ------------------------------------------------------------- simulation ----


def _draw_matrix(rng: np.random.Generator, e: np.ndarray, n: int, reps: int) -> np.ndarray:
    """(reps, n) stationary-bootstrap draws, one independent block series per row."""
    out = np.empty((reps, n), dtype=float)
    n_source = len(e)
    for r in range(reps):
        out[r] = e[stationary_bootstrap_indices(rng, n_source, n, MEAN_BLOCK)]
    return out


def simulate_powers(
    e: np.ndarray,
    eps_day: float,
    ns: list[int],
    seed: int,
    replications: int = REPLICATIONS,
) -> tuple[dict[int, dict[str, float]], bool, int]:
    """Bootstrap power curves. One draw set per length serves both shifts.

    Shifting a series by a constant leaves every autocovariance unchanged, so
    the detection test (shift = eps_day) and the null test (shift = 0) share the
    replicate's draw and its SE; only the mean differs.

    The replicate's standard error is
    ``sqrt(gamma_0_hat(x) * VIF_boot(source) / n)`` with ``gamma_0_hat(x)`` its
    own sample variance (ddof = 1): the replicate carries the finite-sample
    variance noise and the heavy tails, the dependence factor is the source's,
    because the replicate's own autocovariances are already attenuated by the
    block resampling. See the module docstring.

    Returns the curve, whether the SOURCE series' V_B hit the variance floor,
    and the number of zero-variance draws.
    """
    rng = np.random.default_rng(seed)
    vif_source, source_floored = variance_inflation(e)
    curve: dict[int, dict[str, float]] = {}
    degenerate = 0
    for n in ns:
        draws = _draw_matrix(rng, e, n, replications)
        means = draws.mean(axis=1)
        gamma0_hat = draws.var(axis=1, ddof=1)
        se = np.sqrt(gamma0_hat * vif_source / n)
        positive = se > 0.0
        degenerate += int(np.count_nonzero(~positive))
        # A zero-variance draw (every resampled day identical, e.g. all no-trade
        # days) has no finite t; the shifted mean decides the direction.
        shifted = means + eps_day
        safe_se = np.where(positive, se, 1.0)
        t_stat = np.where(positive, shifted / safe_se, np.inf * np.sign(shifted))
        ucb = means + Z_UCB * se
        power_a = float(np.mean(t_stat > Z_HOLM))
        power_b = float(np.mean(ucb < eps_day))
        curve[n] = {
            "power_a": power_a,
            "se_a": _binomial_se(power_a, replications),
            "power_b": power_b,
            "se_b": _binomial_se(power_b, replications),
        }
    return curve, source_floored, degenerate


def percentile_ucb_success(
    e: np.ndarray,
    n: int,
    eps_day: float,
    seed: int,
    replicates: int = SPOT_REPLICATES,
    inner_b: int = SPOT_INNER_B,
) -> float:
    """Fraction of replicates whose PERCENTILE bootstrap UCB falls below eps_day.

    The D.1f construction: resample the confirmation window, then bootstrap the
    mean of that window ``inner_b`` times and take the 95th percentile as the
    upper bound, instead of ``mean + 1.645 * SE``.

    This compares the closed form with the percentile construction INSIDE THE
    BOOTSTRAP WORLD. The inner bootstrap resamples a window that has already
    been block-resampled once, so it carries the same double attenuation the
    per-replicate ``V_B`` had: for an autocorrelated member the figure is
    biased upward. It is not a check of the absolute level, and it changes no
    chosen figure.
    """
    rng = np.random.default_rng(seed)
    successes = 0
    for _ in range(replicates):
        window = e[stationary_bootstrap_indices(rng, len(e), n, MEAN_BLOCK)]
        inner = np.empty(inner_b, dtype=float)
        for b in range(inner_b):
            inner[b] = window[stationary_bootstrap_indices(rng, n, n, MEAN_BLOCK)].mean()
        if float(np.percentile(inner, 100.0 * UCB_LEVEL)) < eps_day:
            successes += 1
    return successes / replicates
