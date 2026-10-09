"""The power table of lead_spec section 5, by simulation, with the analytic t power beside it.

Per test, window (full, fallback) and prior net Sharpe (annual; the prompt's low and high):
per-unit returns are independent normal with unit sd and mean SR_unit = SR_annual / sqrt(U),
U = the mean units per full calendar year of the calendar-only count; each simulated series has
the counted units per year. A simulated test passes at threshold a in {0.01 (Holm's first step at
0.05/5), 0.05 (Holm's last step)} when p <= a (p = the larger of the plain-t and the Newey-West
p, the test's lags), mean > 0, n >= 30 and year stability (2/3 of the years with at least 10
units, H2 6, positive; at least 3 such years). Analytic: the one-sided t power at a,
noncentral t with df n - 1 and ncp SR_unit sqrt(n). Fixed seed.
"""

from __future__ import annotations

import math
from collections.abc import Mapping

import numpy as np

from base_rules import constants as K

PRIORS = {"H1": (0.3, 0.8), "H2": (0.4, 0.9), "H3": (0.3, 0.7), "H4": (0.2, 0.6),
          "H5": (0.8, 1.5)}
THRESHOLDS = (0.01, 0.05)
SEED = 20261009
N_SIM = 4000
CHUNK = 500


def units_per_full_year(per_year: Mapping[str, int]) -> float:
    years = sorted(int(y) for y in per_year)
    full = [per_year[str(y)] for y in years[1:-1]] if len(years) > 2 else list(per_year.values())
    return float(np.mean(full)) if full else 0.0


def _p_values(x: np.ndarray, lags: int) -> tuple[np.ndarray, np.ndarray]:
    from scipy.stats import norm
    from scipy.stats import t as student_t

    n = x.shape[1]
    mean = x.mean(axis=1)
    sd = x.std(axis=1, ddof=1)
    t = mean / (sd / math.sqrt(n))
    e = x - mean[:, None]
    s = (e * e).sum(axis=1) / n
    for lag in range(1, min(lags, n - 1) + 1):
        s += 2.0 * (1.0 - lag / (lags + 1.0)) * (e[:, lag:] * e[:, :-lag]).sum(axis=1) / n
    t_nw = mean / np.sqrt(np.maximum(s, 1e-300) / n)
    p = np.maximum(student_t.sf(t, n - 1), norm.sf(t_nw))
    return p, mean


def simulate_pass(test: str, per_year: Mapping[str, int], sr_annual: float, *,
                  n_sim: int = N_SIM, seed: int = SEED) -> dict:
    counts = [int(per_year[y]) for y in sorted(per_year)]
    n = int(sum(counts))
    u = units_per_full_year(per_year)
    if n < 2 or u <= 0:
        return {"n_units": n, "sim": {str(a): 0.0 for a in THRESHOLDS}, "analytic": None}
    mu = sr_annual / math.sqrt(u)
    rng = np.random.default_rng(seed)
    min_units = K.YEAR_MIN_UNITS[test]
    bounds = np.cumsum([0, *counts])
    qualifying = [i for i, c in enumerate(counts) if c >= min_units]
    passed = {a: 0 for a in THRESHOLDS}
    p_only = {a: 0 for a in THRESHOLDS}
    done = 0
    while done < n_sim:
        m = min(CHUNK, n_sim - done)
        x = rng.normal(mu, 1.0, size=(m, n))
        p, mean = _p_values(x, K.NW_LAGS[test])
        if len(qualifying) >= K.YEAR_MIN_QUALIFYING:
            sums = np.stack([x[:, bounds[i]:bounds[i + 1]].sum(axis=1) for i in qualifying],
                            axis=1)
            stable = (sums > 0).sum(axis=1) * 3 >= 2 * len(qualifying)
        else:
            stable = np.zeros(m, dtype=bool)
        for a in THRESHOLDS:
            ok = (p <= a) & (mean > 0)
            p_only[a] += int(ok.sum())
            passed[a] += int((ok & stable & (n >= K.MIN_UNITS)).sum())
        done += m
    return {"n_units": n, "units_per_full_year": u, "sr_unit": mu,
            "qualifying_years": len(qualifying),
            "sim_pass_all_bars": {str(a): passed[a] / n_sim for a in THRESHOLDS},
            "sim_p_and_mean_only": {str(a): p_only[a] / n_sim for a in THRESHOLDS},
            "analytic_t_power": {str(a): analytic_power(n, mu, a) for a in THRESHOLDS}}


def analytic_power(n: int, sr_unit: float, alpha: float) -> float:
    from scipy.stats import nct
    from scipy.stats import t as student_t

    crit = float(student_t.isf(alpha, n - 1))
    return float(nct.sf(crit, n - 1, sr_unit * math.sqrt(n)))


def power_table(counts: Mapping[str, Mapping[str, Mapping]], *, n_sim: int = N_SIM) -> dict:
    """``counts``: window -> test -> {"units_per_year": {year: n}}."""
    out: dict = {"seed": SEED, "n_sim": n_sim, "thresholds": list(THRESHOLDS), "priors": PRIORS,
                 "rows": []}
    for window, per_test in counts.items():
        for test in K.TESTS:
            per_year = per_test[test]["units_per_year"]
            for label, sr in zip(("low", "high"), PRIORS[test], strict=True):
                row = simulate_pass(test, per_year, sr, n_sim=n_sim)
                out["rows"].append({"window": window, "test": test, "prior": label,
                                    "sr_annual": sr, **row})
    return out


__all__ = ["PRIORS", "THRESHOLDS", "analytic_power", "power_table", "simulate_pass"]
