"""M6's training-window accounting: the DSR of each selected configuration and the PBO over the
36 configurations, from the route's hash-chained ledgers (lead ruling OC-L item 3).

M6: "the training-window DSR of the selected configuration is computed at that count, with the
effective number of trials estimated as E1-ML-17 (Appendix 3) and E1-ML-19 describe. PBO (CSCV)
over the 36 configurations' training-window daily P&L series is reported. These training-window
figures inform; they do not decide anything."

The statistics are the program's pinned functions: ``funnel.multiple_comparisons``'s
``deflated_sharpe_ratio`` and ``probability_of_backtest_overfitting``, with D.1's daily moments
(population sd, raw kurtosis; ``moments`` below is ``strategy.research._d1b_accounting._moments``
line for line, and ``contiguous_blocks`` is its ``_blocks``: 8 contiguous blocks of n // 8 dates,
the remainder at the end left out; a test proves both identical without importing that module's
D.1 runner dependencies into the pipeline).

READINGS (the frozen text leaves these details open; audit ML-A24 said so; each is recorded in
the output and in reports/stage_e2b_g4_mltest_worker.md as a question the lead can overturn):
- RA-1 (series per configuration). The ledger keeps, per configuration, each of its 10 CPCV
  splits' validation portfolio daily P&L (ML-A01, at 1.0 x cost, sigma units). Every date of
  blocks 1-5 is validated in exactly 4 splits (C(4, 1)) with the same rows, so a configuration's
  training-window daily series is the per-date mean over those 4 splits. That is the mean of
  CPCV's four backtest paths under ANY assignment of splits to paths, so no path convention is
  chosen; a date that does not appear in exactly 4 splits is refused by name.
- RA-2 (common dates). The 36 series are put on the union of their dates; a configuration with
  no rows on a date trades nothing there and scores 0 (the program's zeros-on-no-trade-days
  convention). Sharpes, their variance, the correlations and the CSCV blocks use that one axis.
- RA-3 (the count). DSR is reported at three counts, never one chosen silently: the 36
  configurations; the implied number of independent trials N_hat of Appendix 3 (below) over those
  36 series; and the literal "full search" of M6's list, 36 + candidate leaves + pre-test
  survivors (the survivors are a subset of the candidates; M6 lists both, so both are added).
  The Sharpe variance is over the 36 configurations' daily Sharpes (the only trials with daily
  series).
- RA-4 (effective N). Appendix 3 of Bailey and Lopez de Prado (2014), fetched 2026-09-26 from
  https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf: "Given an estimated average
  correlation [rho_hat], we could therefore interpolate between these two extreme outcomes to
  obtain (9)", the extremes being "as [rho -> 1], then [N -> 1]. Similarly, as [rho -> 0], then
  [N -> M]" (symbols lost in text extraction; bracketed). The linear interpolation is
  N_hat = rho_hat + (1 - rho_hat) M, with rho_hat the equal-weighted average off-diagonal
  correlation of Eq. (8). The appendix notes that a correlation matrix must be positive-definite
  and that dimension reduction is for ill-conditioned matrices (T < M); E1-ML-19 suggests PCA for
  the same purpose but fixes no retention rule. So N_hat is computed from the full 36 x 36
  matrix, and it is reported as undefined, by name, when a series is constant (a correlation is
  undefined) or the matrix is not positive-definite; PCA is not computed (no frozen rule).
- RA-5 (PBO blocks). CSCV on 8 contiguous blocks, the program's pinned block count
  (NULL_CRITERIA_E 3, D.1's accounting), since M6 names none for the training window.
"""

from __future__ import annotations

import statistics
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from itertools import combinations
from math import comb, prod
from pathlib import Path

import numpy as np

from funnel.multiple_comparisons import deflated_sharpe_ratio, probability_of_backtest_overfitting
from ml_route.constants import (
    CPCV_BLOCKS,
    CPCV_TEST_BLOCKS,
    HORIZONS,
    LGBM_GRID_AXES,
    LSTM_GRID_AXES,
)

N_PBO_BLOCKS = 8
N_SPLITS = comb(len(CPCV_BLOCKS), CPCV_TEST_BLOCKS)  # 10
SPLITS_PER_DATE = comb(len(CPCV_BLOCKS) - 1, CPCV_TEST_BLOCKS - 1)  # 4
GRID_SIZE = {"lgbm": prod(len(v) for _, v in LGBM_GRID_AXES),
             "lstm": prod(len(v) for _, v in LSTM_GRID_AXES)}
N_CONFIGURATIONS = sum(GRID_SIZE.values()) * len(HORIZONS)  # 36
REFIT_SPLIT = "refit_blocks_1_5"
SCHEMA = "ml_route_training_accounting/1"
DSR_SOURCE = ("Bailey and Lopez de Prado (2014), The Deflated Sharpe Ratio, Appendix 3 "
              "(Eq. 8 and 9), https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf")


class AccountingError(RuntimeError):
    """The ledgers do not hold the complete, consistent search M6 accounts for."""


# ------------------------------------------------------- D.1's pinned helpers ----
def moments(xs: Sequence[float]) -> dict:
    """strategy.research._d1b_accounting._moments, line for line."""
    n = len(xs)
    mean = statistics.fmean(xs)
    sd = statistics.pstdev(xs)
    if sd == 0:
        return {"n": n, "mean": mean, "sd": 0.0, "skew": 0.0, "kurtosis": 3.0, "sharpe": 0.0}
    skew = sum((x - mean) ** 3 for x in xs) / n / sd**3
    kurt = sum((x - mean) ** 4 for x in xs) / n / sd**4
    return {"n": n, "mean": mean, "sd": sd, "skew": skew, "kurtosis": kurt, "sharpe": mean / sd}


def contiguous_blocks(series: Sequence[float], n_blocks: int = N_PBO_BLOCKS) -> list[float]:
    """strategy.research._d1b_accounting._blocks: sums of n // n_blocks contiguous values."""
    width = len(series) // n_blocks
    return [sum(series[b * width:(b + 1) * width]) for b in range(n_blocks)]


# --------------------------------------------------------- series from ledgers ----
@dataclass(frozen=True)
class ConfigSeries:
    challenger: str
    horizon: str
    config_id: str
    config: Mapping
    daily: Mapping[str, float]  # ISO date -> per-date mean over the 4 splits validating it
    split_scores: Mapping[str, float]

    @property
    def key(self) -> str:
        return f"{self.challenger}_{self.horizon}|{self.config_id}"


def configuration_series(records: Iterable[Mapping], challenger: str, horizon: str
                         ) -> list[ConfigSeries]:
    """RA-1: one series per configuration of one ledger (challenger x horizon)."""
    by_cid: dict[str, list[Mapping]] = {}
    for r in records:
        if r.get("split") == REFIT_SPLIT:
            continue
        if r.get("challenger") != challenger or r.get("horizon") != horizon:
            raise AccountingError(f"{r.get('key')}: record of {r.get('challenger')}/"
                                  f"{r.get('horizon')} in the {challenger}_{horizon} ledger")
        by_cid.setdefault(str(r["key"]).split("|")[0], []).append(r)
    out = []
    for cid, recs in sorted(by_cid.items()):
        splits = [str(r["split"]) for r in recs]
        if len(recs) != N_SPLITS or len(set(splits)) != N_SPLITS:
            raise AccountingError(f"{challenger}_{horizon} {cid}: {len(set(splits))} distinct "
                                  f"splits, not the {N_SPLITS} of M7.3")
        configs = {repr(sorted(dict(r["config"]).items())) for r in recs}
        if len(configs) != 1:
            raise AccountingError(f"{challenger}_{horizon} {cid}: the splits disagree on the "
                                  "configuration")
        values: dict[str, list[float]] = {}
        for r in recs:
            for day, value in r["daily_pnl"]:
                values.setdefault(str(day), []).append(float(value))
        wrong = {d: len(v) for d, v in values.items() if len(v) != SPLITS_PER_DATE}
        if wrong:
            first = sorted(wrong)[0]
            raise AccountingError(
                f"{challenger}_{horizon} {cid}: {len(wrong)} dates are not validated in exactly "
                f"{SPLITS_PER_DATE} splits (e.g. {first}: {wrong[first]}); RA-1 needs each date's "
                "rows in every split that validates it")
        daily = {d: statistics.fmean(v) for d, v in sorted(values.items())}
        out.append(ConfigSeries(challenger, horizon, cid, dict(recs[0]["config"]), daily,
                                {str(r["split"]): float(r["score"]) for r in recs}))
    return out


def route_series(route_dir: Path) -> list[ConfigSeries]:
    """All 36 configurations from the six verified ledgers under ``route_dir/ledger``."""
    from ml_route.ledger import Ledger, verify_chain

    out: list[ConfigSeries] = []
    for ch, size in GRID_SIZE.items():
        for h in HORIZONS:
            ledger = Ledger(Path(route_dir) / "ledger" / f"{ch}_{h}.jsonl")
            if not ledger.path.exists():
                raise AccountingError(f"{ledger.path.name} is missing: the search is incomplete")
            verify_chain(ledger)
            series = configuration_series(ledger.records(), ch, h)
            if len(series) != size:
                raise AccountingError(f"{ch}_{h}: {len(series)} configurations, the grid has "
                                      f"{size}")
            out += series
    if len(out) != N_CONFIGURATIONS:
        raise AccountingError(f"{len(out)} configurations, M6 accounts for {N_CONFIGURATIONS}")
    return out


# ------------------------------------------------------------------ statistics ----
def aligned_matrix(series: Sequence[ConfigSeries]) -> tuple[list[str], np.ndarray]:
    """RA-2: the union of dates, each series zero-filled on dates it has no rows."""
    dates = sorted({d for s in series for d in s.daily})
    matrix = np.array([[s.daily.get(d, 0.0) for d in dates] for s in series], dtype=np.float64)
    return dates, matrix


def implied_independent_trials(matrix: np.ndarray) -> dict:
    """RA-4: Appendix 3's N_hat = rho_hat + (1 - rho_hat) M, or the named reason it is undefined."""
    m = matrix.shape[0]
    sd = matrix.std(axis=1)
    if m < 2:
        return {"status": "undefined", "reason": "fewer than 2 trials", "m": m}
    if (sd == 0).any():
        return {"status": "undefined", "m": m,
                "reason": f"{int((sd == 0).sum())} constant series: their correlations are "
                          "undefined (question for the lead)"}
    corr = np.corrcoef(matrix)
    min_eig = float(np.linalg.eigvalsh(corr).min())
    rho = float((corr.sum() - m) / (m * (m - 1)))  # Eq. (8), unit weights
    if min_eig <= 0:
        return {"status": "undefined", "m": m, "average_correlation": rho,
                "min_eigenvalue": min_eig,
                "reason": "the correlation matrix is not positive-definite; Appendix 3's "
                          "dimension reduction (and E1-ML-19's PCA) has no frozen rule"}
    return {"status": "computed", "m": m, "average_correlation": rho, "min_eigenvalue": min_eig,
            "n_hat": rho + (1.0 - rho) * m, "source": DSR_SOURCE}


def _dsr(stats: Mapping, n_trials: float, variance: float) -> dict:
    if stats["sd"] <= 0:
        return {"status": "undefined", "reason": "sd = 0", "n_trials": n_trials}
    try:
        out = deflated_sharpe_ratio(stats["sharpe"], stats["n"], n_trials, variance,
                                    stats["skew"], stats["kurtosis"])
    except ValueError as exc:  # degenerate moments: recorded by name
        return {"status": "undefined", "reason": str(exc), "n_trials": n_trials}
    return {"status": "computed", **out}


def pbo(matrix: np.ndarray, n_blocks: int = N_PBO_BLOCKS) -> dict:
    """RA-5: CSCV over the configurations on contiguous blocks, with the in-sample winner's
    out-of-sample figures (as D.1's accounting reports them)."""
    n_days = matrix.shape[1]
    if n_days // n_blocks < 1:
        raise AccountingError(f"{n_days} dates cannot form {n_blocks} blocks")
    rows = [contiguous_blocks(list(row), n_blocks) for row in matrix]
    result = probability_of_backtest_overfitting(rows, n_blocks)
    oos = []
    for train in combinations(range(n_blocks), n_blocks // 2):
        test = [b for b in range(n_blocks) if b not in train]
        best = max(range(len(rows)), key=lambda s: sum(rows[s][b] for b in train))
        oos.append(sum(rows[best][b] for b in test))
    return {"pbo": result.pbo, "n_splits": result.n_splits, "n_strategies": result.n_strategies,
            "n_blocks": n_blocks, "block_days": n_days // n_blocks,
            "days_left_out": n_days - n_blocks * (n_days // n_blocks),
            "degenerate": result.degenerate, "note": result.note,
            "winner_mean_oos_sigma": statistics.fmean(oos) if oos else None,
            "p_winner_positive_oos": (sum(x > 0 for x in oos) / len(oos)) if oos else None}


def _selected_index(series: Sequence[ConfigSeries], key: str, config: Mapping) -> int:
    ch, h = key.split("_", 1)
    hits = [i for i, s in enumerate(series)
            if s.challenger == ch and s.horizon == h and dict(s.config) == dict(config)]
    if len(hits) != 1:
        raise AccountingError(f"selected {key} {dict(config)} matches {len(hits)} ledger "
                              "configurations, not one")
    return hits[0]


def training_accounting(series: Sequence[ConfigSeries], selected: Mapping[str, Mapping],
                        trial_counts: Mapping | None = None) -> dict:
    """M6's training-window figures (RA-1..RA-5). ``selected``: the route manifest's
    ``selected`` block ({"lgbm_h30": {"config": {...}, ...}, ...}); ``trial_counts``: its
    ``trial_counts`` block (for the full-search count)."""
    if len(series) != N_CONFIGURATIONS:
        raise AccountingError(f"{len(series)} configurations, M6 accounts for {N_CONFIGURATIONS}")
    dates, matrix = aligned_matrix(series)
    stats = [moments(list(row)) for row in matrix]
    variance = statistics.pvariance([s["sharpe"] for s in stats])
    n_hat = implied_independent_trials(matrix)
    counts: dict[str, float | None] = {"configurations": float(N_CONFIGURATIONS),
                                       "implied_independent": n_hat.get("n_hat")}
    if trial_counts is not None:
        counts["full_search"] = float(N_CONFIGURATIONS + int(trial_counts["candidate_leaves"])
                                      + int(trial_counts["pretest_survivors"]))
    per_selected = {}
    for key in sorted(selected):
        i = _selected_index(series, key, selected[key]["config"])
        dsr = {name: (_dsr(stats[i], n, variance) if n is not None
                      else {"status": "undefined", "reason": n_hat.get("reason")})
               for name, n in counts.items()}
        per_selected[key] = {"config_id": series[i].config_id, "moments": stats[i],
                             "mean_of_split_scores": statistics.fmean(
                                 series[i].split_scores.values()),
                             "dsr": dsr}
    return {
        "schema": SCHEMA, "unit": "sigma units per day (ML-A01's portfolio P&L at 1.0 x cost)",
        "readings": ["RA-1", "RA-2", "RA-3", "RA-4", "RA-5"],
        "n_configurations": len(series), "n_dates": len(dates),
        "first_date": dates[0] if dates else None, "last_date": dates[-1] if dates else None,
        "sharpe_variance_over_configurations": variance,
        "counts": counts, "implied_independent_trials": n_hat,
        "pca_effective_n": {"status": "not computed",
                            "reason": "E1-ML-19 suggests PCA but no retention rule is frozen"},
        "selected": per_selected, "pbo": pbo(matrix),
        "configurations": {s.key: {"moments": st, "daily_sharpe": st["sharpe"]}
                           for s, st in zip(series, stats, strict=True)},
        "note": "M6: these training-window figures inform; they do not decide anything.",
    }


def route_training_accounting(route_dir: Path, manifest: Mapping) -> dict:
    """``training_accounting`` over the six verified ledgers of a finalized route."""
    return training_accounting(route_series(route_dir), manifest["selected"],
                               manifest.get("trial_counts"))


__all__ = ["AccountingError", "ConfigSeries", "N_CONFIGURATIONS", "aligned_matrix",
           "configuration_series", "contiguous_blocks", "implied_independent_trials", "moments",
           "pbo", "route_series", "route_training_accounting", "training_accounting"]
