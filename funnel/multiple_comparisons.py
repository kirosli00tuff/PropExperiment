"""Multiple-comparisons accounting for Stage D.1 hypothesis screening.

Three named, published corrections, each with its assumptions stated. None of
these is a substitute for out-of-sample evidence; they bound how much of an
apparent edge could be selection.

- Deflated Sharpe Ratio (Bailey & Lopez de Prado 2014). Adjusts an observed
  Sharpe for (a) the number of trials that produced it, (b) non-normal returns
  via skew and kurtosis, and (c) sample length.
- Harvey/Liu/Zhu (2016) hurdle. Their survey of the factor literature concludes
  that a conventional t > 2.0 is far too permissive once the number of tried
  specifications is counted; t > 3.0 is their recommended minimum.
- Probability of Backtest Overfitting via CSCV (Bailey, Borwein, Lopez de Prado,
  Zhu 2017). Asks how often the in-sample best performer lands below the median
  out-of-sample, across all symmetric splits of the observation blocks.

Money is handled in dollars here, not integer cents, because every input is
already a derived statistic rather than an account balance.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import combinations

EULER_MASCHERONI = 0.5772156649015329
HLZ_HURDLE = 3.0
CONVENTIONAL_HURDLE = 2.0


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _norm_ppf(p: float) -> float:
    """Inverse standard normal CDF (Acklam's rational approximation, |err| < 1.15e-9)."""
    if not 0.0 < p < 1.0:
        raise ValueError(f"p {p!r} must be strictly inside (0, 1)")
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    p_low, p_high = 0.02425, 1 - 0.02425
    if p < p_low:
        q = math.sqrt(-2 * math.log(p))
        num = ((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]
        return num / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    if p > p_high:
        q = math.sqrt(-2 * math.log(1 - p))
        num = ((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]
        return -num / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    q = p - 0.5
    r = q * q
    num = (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q
    return num / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)


def expected_max_sharpe(n_trials: int, sharpe_variance: float) -> float:
    """E[max SR] under the null that every trial has true SR = 0.

    Bailey & Lopez de Prado eq. (3). ``sharpe_variance`` is the variance of the
    Sharpe estimates ACROSS trials; with one trial the expected maximum is 0 by
    definition (no selection took place).
    """
    if n_trials < 1:
        raise ValueError(f"n_trials {n_trials!r} must be >= 1")
    if sharpe_variance < 0:
        raise ValueError(f"sharpe_variance {sharpe_variance!r} must be >= 0")
    if n_trials == 1:
        return 0.0
    g = EULER_MASCHERONI
    term = (1 - g) * _norm_ppf(1 - 1.0 / n_trials) + g * _norm_ppf(1 - 1.0 / (n_trials * math.e))
    return math.sqrt(sharpe_variance) * term


def deflated_sharpe_ratio(
    observed_sharpe: float,
    n_observations: int,
    n_trials: int,
    sharpe_variance: float,
    skewness: float = 0.0,
    kurtosis: float = 3.0,
) -> dict:
    """Probability the true Sharpe exceeds 0, given the trial count and return shape.

    ``observed_sharpe`` and ``sharpe_variance`` must be on the SAME period basis
    as ``n_observations`` (e.g. both per trading day). ``kurtosis`` is the raw
    fourth standardised moment, so a normal distribution is 3.0, not 0.0.
    """
    if n_observations < 2:
        raise ValueError(f"n_observations {n_observations!r} must be >= 2")
    benchmark = expected_max_sharpe(n_trials, sharpe_variance)
    denominator_sq = (1.0 - skewness * observed_sharpe
                      + 0.25 * (kurtosis - 1.0) * observed_sharpe**2)
    if denominator_sq <= 0:
        raise ValueError(
            f"degenerate variance term {denominator_sq!r}: skew/kurtosis are inconsistent "
            f"with observed_sharpe {observed_sharpe!r}"
        )
    z = (observed_sharpe - benchmark) * math.sqrt(n_observations - 1) / math.sqrt(denominator_sq)
    return {
        "deflated_sharpe_ratio": _norm_cdf(z),
        "expected_max_sharpe_under_null": benchmark,
        "observed_sharpe": observed_sharpe,
        "z": z,
        "n_trials": n_trials,
        "n_observations": n_observations,
    }


def harvey_liu_zhu_verdict(
    mean: float, stdev: float, n_observations: int, hurdle: float = HLZ_HURDLE
) -> dict:
    """t-stat of a mean against the HLZ (2016) hurdle: t > 3.0, not the usual 2.0."""
    if n_observations < 2:
        raise ValueError(f"n_observations {n_observations!r} must be >= 2")
    if stdev <= 0:
        raise ValueError(f"stdev {stdev!r} must be > 0")
    t = mean / (stdev / math.sqrt(n_observations))
    return {
        "t_stat": t,
        "hurdle": hurdle,
        "passes_hlz": t > hurdle,
        "passes_conventional": t > CONVENTIONAL_HURDLE,
    }


@dataclass(frozen=True)
class PBOResult:
    pbo: float
    n_splits: int
    n_strategies: int
    logits: tuple[float, ...]
    degenerate: bool
    note: str


def probability_of_backtest_overfitting(
    performance: list[list[float]], n_blocks: int = 8
) -> PBOResult:
    """CSCV probability of backtest overfitting.

    ``performance[s][b]`` is strategy ``s``'s performance in observation block
    ``b`` (any consistent measure; per-fold net P&L is fine). Every balanced
    train/test partition of the blocks is formed; the in-sample winner is picked
    and its out-of-sample rank recorded. PBO is the fraction of splits where that
    winner lands at or below the out-of-sample median.

    With fewer than 2 strategies the question is meaningless -- selection needs
    something to select between -- so this returns ``degenerate=True`` and NaN
    rather than a falsely reassuring 0.0.
    """
    n_strategies = len(performance)
    if n_strategies < 2:
        return PBOResult(float("nan"), 0, n_strategies, (), True,
                         "PBO undefined with fewer than 2 candidates: no selection occurs.")
    if n_blocks % 2 != 0:
        raise ValueError(f"n_blocks {n_blocks!r} must be even for a symmetric split")
    widths = {len(row) for row in performance}
    if widths != {n_blocks}:
        raise ValueError(f"every strategy needs exactly {n_blocks} blocks; got {sorted(widths)}")

    blocks = range(n_blocks)
    logits: list[float] = []
    for train in combinations(blocks, n_blocks // 2):
        train_set = set(train)
        test = [b for b in blocks if b not in train_set]
        in_sample = [sum(row[b] for b in train) for row in performance]
        out_sample = [sum(row[b] for b in test) for row in performance]
        best = max(range(n_strategies), key=lambda s: in_sample[s])
        worse = sum(1 for s in range(n_strategies) if out_sample[s] < out_sample[best])
        rank = min(max((worse + 0.5) / n_strategies, 1e-9), 1 - 1e-9)
        logits.append(math.log(rank / (1 - rank)))
    pbo = sum(1 for lg in logits if lg <= 0) / len(logits)
    return PBOResult(pbo, len(logits), n_strategies, tuple(logits), False,
                     "Fraction of symmetric splits where the in-sample best ranked at or "
                     "below the out-of-sample median.")
