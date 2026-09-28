"""Stage E confirmation verdicts per cluster (Stage E.5, harness v5; stage_e5_harness_plan.md 3b).

Pure functions on the runner's confirmation member records (screening/stage_e_runner.py, window
"confirmation": ``screen`` and ``power`` None, a ``series`` in ticks/ct/day and an ``s_x`` map) and
the hashed confirmation list (schema ``stage_e_confirmation_list/1``, written by the lead). No bar
and no trip file is read.

The D.1f decision functions (strategy/research/_d1f_decisions.py and _d1b_accounting.py, pinned by
reports/stage_d1f_confirmation_list.md 3.1-3.4) are RESTATED here on funnel/null_generator.py and
funnel/multiple_comparisons.py, which the harness manifest lists, so the frozen harness carries
them (lead ruling L-E5-4, the screening/stage_e_stats_power.py pattern); tests/
test_stage_e_verdict.py proves them equal function for function. Nothing is imported from
strategy/.

Per run trial (Tier A and Tier B; docs/NULL_CRITERIA_E.md 3, 6): theta_hat = the mean of the
daily series; stationary block bootstrap (mean block 5, B = 10,000, a fresh generator seeded
20260923 + the trial's list ordinal); UCB95 = np.quantile(means, 0.95); SE_boot = np.std(means);
p_upper = (1 + #{theta* - theta_hat >= theta_hat}) / (B + 1); achieved null power
Phi(eps_X / SE_boot - 1.645). Status: "null" (UCB95 < eps_X and power >= 0.80), "null by
inactivity" (both, fewer than 30 closed trips), else "inconclusive" (so are zero trips and
SE_boot = 0).
Tier A edge chain, every step computed whatever an earlier one gives: Holm over the Tier A
p_upper at 0.05 / K, K = 9 (V14 b); the composite "pending" (V14 a); DSR > 0.95 at the list's
program N, moments on the trial's own series, the Sharpe variance over the Tier A trials when there
are two or more, else over every run trial of the cluster (V14 c); daily t > 3.0 one-sided; CSCV
PBO < 0.5 over the Tier A series (two or more), else over every run trial's series (lead ruling
L-E5-3), aligned on the union of the run trials' window dates with 0 off a trial's own dates (D.1f
ruling (a)), 8 blocks of n_days // 8 dates. A passing trial reads "edge candidate, composite
pending" (V14 a), never "edge"; a source-overlap trial adds that no edge is claimed without a
registered holdout read. The cluster null statement and the per-exposure resolution table follow
NULL_CRITERIA_E 1 and 7; "inconclusive by design" and not-run (excluded) trials are named as not
covered and block nothing (lead ruling L-E5-5).

    uv run python -m screening.stage_e_verdict --harness-sha256 SHA --list LIST.json \\
        --records DIR --out OUT.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import statistics
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np

from funnel.multiple_comparisons import (
    HLZ_HURDLE,
    deflated_sharpe_ratio,
    harvey_liu_zhu_verdict,
    probability_of_backtest_overfitting,
)
from funnel.null_generator import stationary_bootstrap_indices
from screening import harness_freeze
from screening.stage_e_stats import holm_tier_a
from screening.stage_e_stats_power import LABEL_INCONCLUSIVE
from screening.stage_e_stats_units import frozen_epsilon

# ------------------------------------------------------------- constants ----
BOOTSTRAP_SEED_BASE = 20260923  # NULL_CRITERIA_E 3: seed = base + the trial's list ordinal
BOOTSTRAP_RESAMPLES = 10_000
MEAN_BLOCK_DAYS = 5.0
UCB_QUANTILE = 0.95
NULL_Z = 1.645  # as NULL_CRITERIA_E 3 writes it: Phi(eps_X / SE_boot - 1.645)
NULL_POWER_MIN = 0.80
INACTIVITY_MIN = 30
HOLM_K = 9  # V14 (b)
DSR_MIN = 0.95
T_MIN = HLZ_HURDLE  # 3.0
PBO_MAX = 0.5
N_PBO_BLOCKS = 8

LIST_SCHEMA = "stage_e_confirmation_list/1"
VERDICT_SCHEMA = "stage_e_confirmation_verdict/1"
RECORD_SCHEMA = "stage_e_member_record/1"  # screening.stage_e_runner.RECORD_SCHEMA
CONFIRMATION_WINDOW = "confirmation"  # screening.stage_e_runner.CONFIRMATION_WINDOW
RUN_STATUS = "run"
SERIES_UNIT = "net ticks per contract per day"  # the runner's record series unit, verbatim
CONFIRMATION_LAST = date(2024, 2, 29)  # NULL_CRITERIA_E 1: S_X to 2024-02-29

LABEL_SOURCE_OVERLAP = "source-overlap"
LABEL_CALENDAR_UNVERIFIED = "calendar partly unverified"
LABEL_INCONCLUSIVE_BY_DESIGN = LABEL_INCONCLUSIVE  # "inconclusive by design"
LABEL_INACTIVITY = "null by inactivity"
LABEL_EDGE_CANDIDATE = "edge candidate, composite pending"  # V14 (a)
# The runner's D9 labels (screening/stage_e_runner.py LABEL_*), carried by excluded trials.
RUNNER_LABELS = ("coverage_below_0.95", "mean_holding_below_10min", "entries_above_20_per_day",
                 "hold_below_2min")
LIST_LABELS = frozenset((LABEL_SOURCE_OVERLAP, LABEL_CALENDAR_UNVERIFIED,
                         LABEL_INCONCLUSIVE_BY_DESIGN, *RUNNER_LABELS))

NULL, NULL_INACTIVE, INCONCLUSIVE = "null", LABEL_INACTIVITY, "inconclusive"
NO_EDGE = "no edge"
NO_EDGE_DSR_UNDEFINED = "no edge (dsr undefined)"  # review N-4
NO_EDGE_PBO_UNDEFINED = "no edge (pbo undefined)"
DSR_VARIANCE_UNDEFINED = "variance over fewer than 2 series (V14 c)"  # review SF-1
SOURCE_OVERLAP_PASS = (f"{LABEL_EDGE_CANDIDATE}; source-overlap: no edge claim without a "
                       "registered holdout read")
COMPOSITE_PENDING = "pending"
STATEMENT_NULL, NO_STATEMENT = "null", "no statement"
TIERS = ("A", "B", "excluded")


class VerdictRefusal(ValueError):
    """The verdict cannot be computed on these inputs; the reason is named."""


# ------------------------------------------ the D.1f functions, restated ----
@dataclass(frozen=True)
class Bootstrap:
    n_days: int
    theta_hat: float
    ucb95: float
    se_boot: float
    p_upper: float  # H0: theta <= 0 (the Holm input)
    p_lower: float  # H0: theta >= 0 (kept for equality with D.1f; not used here)


def resampled_means(daily: np.ndarray, n_resamples: int, seed: int,
                    mean_block: float = MEAN_BLOCK_DAYS) -> np.ndarray:
    """The B bootstrap means, a fresh generator per call (D.1f ``resampled_means``)."""
    values = np.asarray(daily, dtype=float)
    if len(values) < 1:
        raise ValueError("need at least one day to bootstrap a mean")
    rng = np.random.default_rng(seed)
    means = np.empty(n_resamples)
    for i in range(n_resamples):
        means[i] = values[stationary_bootstrap_indices(rng, len(values), len(values),
                                                       mean_block)].mean()
    return means


def summarize_means(daily: np.ndarray, means: np.ndarray) -> Bootstrap:
    """theta_hat, UCB95 (np.quantile, linear), SE_boot (ddof 0), one-sided p (D.1f 3.1)."""
    values = np.asarray(daily, dtype=float)
    theta = float(values.mean())
    centred = means - theta
    b = len(means)
    return Bootstrap(
        n_days=len(values), theta_hat=theta, ucb95=float(np.quantile(means, UCB_QUANTILE)),
        se_boot=float(np.std(means)),
        p_upper=(1 + int(np.sum(centred >= theta))) / (b + 1),
        p_lower=(1 + int(np.sum(centred <= theta))) / (b + 1))


def null_power(se_boot: float, epsilon: float) -> float:
    """Phi(epsilon / SE_boot - 1.645); 0.0 when SE_boot = 0 (such a trial fails)."""
    if se_boot <= 0.0:
        return 0.0
    return 0.5 * (1.0 + math.erf((epsilon / se_boot - NULL_Z) / math.sqrt(2.0)))


def moments(xs: Sequence[float]) -> dict:
    """n, mean, population sd, skew, raw kurtosis, daily Sharpe (D.1b ``_moments``)."""
    xs = [float(x) for x in xs]
    n = len(xs)
    mean = statistics.fmean(xs)
    sd = statistics.pstdev(xs)
    if sd == 0:
        return {"n": n, "mean": mean, "sd": 0.0, "skew": 0.0, "kurtosis": 3.0, "sharpe": 0.0}
    skew = sum((x - mean) ** 3 for x in xs) / n / sd**3
    kurt = sum((x - mean) ** 4 for x in xs) / n / sd**4
    return {"n": n, "mean": mean, "sd": sd, "skew": skew, "kurtosis": kurt, "sharpe": mean / sd}


def blocks(series: Sequence[float]) -> list[float]:
    """8 contiguous blocks of len // 8 dates, summed (D.1b ``_blocks``)."""
    width = len(series) // N_PBO_BLOCKS
    return [sum(series[b * width:(b + 1) * width]) for b in range(N_PBO_BLOCKS)]


def dsr(mom: Mapping[str, float], n_trials: int, variance: float
        ) -> tuple[float | None, str | None]:
    """DSR, or (None, reason) when sd = 0 or the moments are degenerate (D.1f ``_dsr``)."""
    if mom["sd"] <= 0:
        return None, "sd = 0"
    try:
        return deflated_sharpe_ratio(mom["sharpe"], mom["n"], n_trials, variance, mom["skew"],
                                     mom["kurtosis"])["deflated_sharpe_ratio"], None
    except ValueError as exc:  # degenerate moments: recorded, the trial fails the criterion
        return None, str(exc)


def t_stat(mom: Mapping[str, float]) -> float | None:
    """harvey_liu_zhu_verdict(mean, population sd, n) t, or None (D.1f ``_t_stat``)."""
    if mom["sd"] <= 0 or mom["n"] < 2:
        return None
    return harvey_liu_zhu_verdict(mom["mean"], mom["sd"], mom["n"])["t_stat"]


def dsr_table(moms: Mapping[str, Mapping[str, float]], variance_over: Sequence[str],
              n_trials: int, members: Sequence[str]) -> dict:
    """D.1f ``dsr_table``: the Sharpe variance over ``variance_over`` (population variance)."""
    variance = statistics.pvariance([moms[k]["sharpe"] for k in variance_over])
    benchmark = deflated_sharpe_ratio(0.0, 2, n_trials, variance)["expected_max_sharpe_under_null"]
    values, notes = {}, {}
    for key in members:
        values[key], note = dsr(moms[key], n_trials, variance)
        if note:
            notes[key] = note
    return {"n_trials": n_trials, "variance_over_n_members": len(variance_over),
            "sharpe_variance": variance, "expected_max_daily_sharpe_under_null": benchmark,
            "dsr": values, "undefined": notes}


def pbo(series: Mapping[str, np.ndarray]) -> dict:
    """CSCV PBO on 8 contiguous blocks of n_days // 8 dates (D.1f ``pbo``)."""
    labels = list(series)
    n_days = len(next(iter(series.values())))
    if n_days // N_PBO_BLOCKS < 1:
        raise ValueError(f"{n_days} window days cannot form {N_PBO_BLOCKS} blocks")
    matrix = [blocks(list(series[k])) for k in labels]
    result = probability_of_backtest_overfitting(matrix, N_PBO_BLOCKS)
    oos = []
    for train in combinations(range(N_PBO_BLOCKS), N_PBO_BLOCKS // 2):
        test = [b for b in range(N_PBO_BLOCKS) if b not in train]
        best = max(range(len(labels)), key=lambda s: sum(matrix[s][b] for b in train))
        oos.append(sum(matrix[best][b] for b in test))
    return {"n_strategies": len(labels), "n_days": n_days,
            "block_days": n_days // N_PBO_BLOCKS, "pbo": result.pbo,
            "n_splits": result.n_splits, "degenerate": result.degenerate,
            "winner_mean_oos_ticks_per_micro": statistics.fmean(oos) if oos else None,
            "p_winner_positive_oos": (sum(x > 0 for x in oos) / len(oos)) if oos else None}


def aligned_series(dates: Sequence[date], values: Sequence[float],
                   window_dates: Sequence[date]) -> np.ndarray:
    """D.1f ruling (a): a series on the full window date list, 0 off its own dates."""
    index = {d: i for i, d in enumerate(window_dates)}
    missing = [d for d in dates if d not in index]
    if missing:
        raise ValueError(f"{len(missing)} own dates outside the window, e.g. {missing[0]}")
    out = np.zeros(len(window_dates))
    for d, v in zip(dates, values, strict=True):
        out[index[d]] = v
    return out


# ---------------------------------------------------------------- inputs ----
@dataclass(frozen=True)
class ListTrial:
    ordinal: int
    member: str
    vehicle: str
    q_c: int
    eps_ticks: float
    eps_usd_per_day_at_q: float
    tier: str  # "A" | "B" | "excluded"
    run: bool
    labels: tuple[str, ...]
    bootstrap_seed: int
    power: Mapping[str, Any] | None

    @property
    def by_design(self) -> bool:
        return LABEL_INCONCLUSIVE_BY_DESIGN in self.labels

    @property
    def covered(self) -> bool:
        return self.run and not self.by_design


@dataclass(frozen=True)
class ConfirmationList:
    cluster: str
    harness_sha256: str
    cluster_freeze_sha256: str
    program_n: int
    start_dates: Mapping[str, date]
    trials: tuple[ListTrial, ...]


def _int(value: object, what: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise VerdictRefusal(f"{what} must be an int >= {minimum}, got {value!r}")
    return value


def _number(value: object, what: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise VerdictRefusal(f"{what} must be a finite number, got {value!r}")
    return float(value)


def _trial(raw: Mapping[str, Any], seed_base: int) -> ListTrial:
    member = raw.get("member")
    if not isinstance(member, str) or not member:
        raise VerdictRefusal(f"a list trial has no member name: {raw!r}")
    ordinal = _int(raw.get("ordinal"), f"{member}: ordinal")
    tier, run, labels = raw.get("tier"), raw.get("run"), raw.get("labels")
    if tier not in TIERS or not isinstance(run, bool) or (tier == "excluded") == run:
        raise VerdictRefusal(f"{member}: tier {tier!r} and run {run!r} disagree (Tier A and B "
                             "trials are run, excluded trials are not)")
    if not isinstance(labels, list) or not all(isinstance(x, str) for x in labels):
        raise VerdictRefusal(f"{member}: labels must be a list of strings")
    unknown = sorted(set(labels) - LIST_LABELS)
    if unknown:
        raise VerdictRefusal(f"{member}: unknown labels {unknown}")
    seed = _int(raw.get("bootstrap_seed"), f"{member}: bootstrap_seed")
    if seed != seed_base + ordinal:
        raise VerdictRefusal(f"{member}: bootstrap_seed {seed} is not {seed_base} + ordinal "
                             f"{ordinal}")
    vehicle = raw.get("vehicle")
    if not isinstance(vehicle, str) or not vehicle:
        raise VerdictRefusal(f"{member}: no vehicle")
    try:
        frozen = frozen_epsilon(vehicle)
    except KeyError as exc:  # review N-5: a named refusal, not a traceback
        raise VerdictRefusal(f"{member}: vehicle {vehicle!r} has no operative eps in the frozen "
                             "E.2a epsilon table") from exc
    q_c = _int(raw.get("q_c"), f"{member}: q_c", 1)
    eps = _number(raw.get("eps_ticks"), f"{member}: eps_ticks")
    usd = _number(raw.get("eps_usd_per_day_at_q"), f"{member}: eps_usd_per_day_at_q")
    if (frozen.eps_ticks, frozen.q_c) != (eps, q_c) or not math.isclose(
            frozen.eps_usd_per_day_at_q, usd, rel_tol=1e-9):
        raise VerdictRefusal(f"{member}: vehicle {vehicle!r}, eps {eps}, q_c {q_c}, ${usd} differ "
                             "from the frozen E.2a epsilon table")
    power = raw.get("power")
    if power is not None and not isinstance(power, Mapping):
        raise VerdictRefusal(f"{member}: power must be an object or null")
    return ListTrial(ordinal, member, vehicle, q_c, eps, usd, tier, run, tuple(labels), seed,
                     power)


def parse_list(payload: Mapping[str, Any]) -> ConfirmationList:
    """The hashed confirmation list; every field the module reads is checked, or refused."""
    if payload.get("schema") != LIST_SCHEMA:
        raise VerdictRefusal(f"list schema {payload.get('schema')!r} is not {LIST_SCHEMA!r}")
    if payload.get("k_holm") != HOLM_K or isinstance(payload.get("k_holm"), bool):
        raise VerdictRefusal(f"list K {payload.get('k_holm')!r} is not {HOLM_K} (V14 b)")
    boot = payload.get("bootstrap")
    expected = {"seed_base": BOOTSTRAP_SEED_BASE, "resamples": BOOTSTRAP_RESAMPLES,
                "mean_block": MEAN_BLOCK_DAYS, "ucb_quantile": UCB_QUANTILE}
    if not isinstance(boot, Mapping) or boot.get("seed_base") != BOOTSTRAP_SEED_BASE:
        raise VerdictRefusal(f"list seed base is not {BOOTSTRAP_SEED_BASE} (NULL_CRITERIA_E 3)")
    if dict(boot) != expected:
        raise VerdictRefusal(f"list bootstrap {dict(boot)} is not {expected}")
    for key in ("cluster", "harness_sha256", "cluster_freeze_sha256"):
        if not isinstance(payload.get(key), str) or not payload[key]:
            raise VerdictRefusal(f"list {key} missing")
    program_n = _int(payload.get("program_n"), "program_n", 1)
    starts = payload.get("start_dates")
    if not isinstance(starts, Mapping) or not starts:
        raise VerdictRefusal("list start_dates missing")
    try:
        start_dates = {str(r): date.fromisoformat(v) for r, v in starts.items()}
    except (TypeError, ValueError) as exc:
        raise VerdictRefusal(f"list start_dates unreadable: {exc}") from exc
    raw_trials = payload.get("trials")
    if not isinstance(raw_trials, list) or not raw_trials:
        raise VerdictRefusal("list has no trials")
    trials = tuple(_trial(t, BOOTSTRAP_SEED_BASE) for t in raw_trials)
    for what in ("member", "ordinal"):
        values = [getattr(t, what) for t in trials]
        if len(set(values)) != len(values):
            raise VerdictRefusal(f"list repeats a trial {what}")
    return ConfirmationList(payload["cluster"], payload["harness_sha256"],
                            payload["cluster_freeze_sha256"], program_n, start_dates, trials)


def record_name(cluster: str, member: str) -> str:
    """The runner's file name for a confirmation member record (stage_e_runner._safe)."""
    name = f"{cluster}_{member}_{CONFIRMATION_WINDOW}"
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("_") + ".json"


@dataclass(frozen=True)
class Series:
    dates: tuple[date, ...]
    values: np.ndarray
    n_trips: int


def check_record(record: Mapping[str, Any], trial: ListTrial, clist: ConfirmationList
                 ) -> Series | None:
    """The record against the list (refusals by name); its series, or None when not run."""
    who = trial.member
    wanted = {"schema": RECORD_SCHEMA, "cluster": clist.cluster, "member": trial.member,
              "ordinal": trial.ordinal, "window": CONFIRMATION_WINDOW,
              "harness_sha256": clist.harness_sha256,
              "cluster_freeze_sha256": clist.cluster_freeze_sha256}
    for key, value in wanted.items():
        if record.get(key) != value or isinstance(record.get(key), bool):
            raise VerdictRefusal(f"{who}: record {key} {record.get(key)!r} differs from the list "
                                 f"({value!r})")
    s_x = record.get("s_x")
    if not isinstance(s_x, Mapping) or not s_x:
        raise VerdictRefusal(f"{who}: record has no S_X map")
    for root, day in s_x.items():
        listed = clist.start_dates.get(root)
        if listed is None or str(day) != listed.isoformat():
            raise VerdictRefusal(f"{who}: S_X {root} {day} differs from the list ({listed})")
    if record.get("status") != RUN_STATUS:
        return None
    return _series(record.get("series"), trial, clist)


def _series(raw: object, trial: ListTrial, clist: ConfirmationList) -> Series:
    who = trial.member
    if not isinstance(raw, Mapping):
        raise VerdictRefusal(f"{who}: a run record without a series")
    if raw.get("unit") != SERIES_UNIT:
        raise VerdictRefusal(f"{who}: series unit {raw.get('unit')!r} is not {SERIES_UNIT!r}")
    if raw.get("vehicle") != trial.vehicle:
        raise VerdictRefusal(f"{who}: series vehicle {raw.get('vehicle')!r} is not the list's "
                             f"{trial.vehicle!r}")
    try:
        dates = tuple(date.fromisoformat(str(d)) for d in raw["dates"])
        values = [float(v) for v in raw["values"]]
    except (KeyError, TypeError, ValueError) as exc:
        raise VerdictRefusal(f"{who}: series unreadable: {exc}") from exc
    if not dates or len(dates) != len(values):
        raise VerdictRefusal(f"{who}: series dates and values must align, non-empty")
    for earlier, later in zip(dates, dates[1:], strict=False):
        if not later > earlier:
            raise VerdictRefusal(f"{who}: series dates not strictly increasing ({later} after "
                                 f"{earlier})")
    if not all(math.isfinite(v) for v in values):
        raise VerdictRefusal(f"{who}: series has a non-finite value")
    start = clist.start_dates.get(trial.vehicle)  # review N-6: the window bounds
    if start is None or dates[0] < start:
        raise VerdictRefusal(f"{who}: series starts {dates[0]}, before the list's S_X of "
                             f"{trial.vehicle} ({start})")
    if dates[-1] > CONFIRMATION_LAST:
        raise VerdictRefusal(f"{who}: series ends {dates[-1]}, after {CONFIRMATION_LAST}")
    n_trips = _int(raw.get("n_trips"), f"{who}: series n_trips")
    return Series(dates, np.asarray(values, dtype=float), n_trips)


# ------------------------------------------------------------- per trial ----
def trial_figures(series: Series, eps_ticks: float, seed: int,
                  n_resamples: int = BOOTSTRAP_RESAMPLES) -> dict:
    """NULL_CRITERIA_E 3 and 6 for one run trial: the estimates, the null conditions, the status."""
    boot = summarize_means(series.values, resampled_means(series.values, n_resamples, seed))
    power = null_power(boot.se_boot, eps_ticks)
    rate = series.n_trips / boot.n_days
    ucb_below, power_ok = boot.ucb95 < eps_ticks, power >= NULL_POWER_MIN
    reasons = []
    if series.n_trips == 0:
        reasons.append("zero trips")
    if boot.se_boot == 0.0:
        reasons.append("SE_boot = 0")
    if not ucb_below:
        reasons.append("UCB95 >= eps_X")
    if not power_ok:
        reasons.append("null power < 0.80")
    inactive = series.n_trips < INACTIVITY_MIN
    status = INCONCLUSIVE if reasons else (NULL_INACTIVE if inactive else NULL)
    return {"n_days": boot.n_days, "n_trips": series.n_trips, "trips_per_day": rate,
            "theta_hat": boot.theta_hat, "ucb95": boot.ucb95, "se_boot": boot.se_boot,
            "p_upper": boot.p_upper, "theta_per_trade": boot.theta_hat / rate if rate else None,
            "ucb95_per_trade": boot.ucb95 / rate if rate else None, "eps_ticks": eps_ticks,
            "null_power": power, "ucb_below_eps": ucb_below, "power_ok": power_ok,
            "status": status, "reasons": reasons, "seed": seed, "resamples": n_resamples}


def _trial_row(trial: ListTrial, series: Series | None, record_status: str | None,
               n_resamples: int) -> dict:
    row: dict[str, Any] = {
        "ordinal": trial.ordinal, "member": trial.member, "vehicle": trial.vehicle,
        "q_c": trial.q_c, "tier": trial.tier, "run": trial.run, "labels": list(trial.labels),
        "record_status": record_status, "covered": trial.covered,
        "d4_power": None if trial.power is None else dict(trial.power)}
    if series is not None and trial.run:
        row.update(trial_figures(series, trial.eps_ticks, trial.bootstrap_seed, n_resamples))
    elif trial.run:  # a confirmation record that is not "run": no evidence (NULL_CRITERIA_E 6)
        row.update(status=INCONCLUSIVE, reasons=[f"record status {record_status!r}: no series"])
    else:
        reason = "excluded (not Tier A or B): not run"
        if record_status is not None:
            reason += f"; its record (status {record_status!r}) is present and not used"
        row.update(status="not run", reasons=[reason])
    return row


# ------------------------------------------------------------ edge chain ----
def _union_dates(series: Mapping[str, Series]) -> list[date]:
    return sorted(set().union(*(s.dates for s in series.values())))


def edge_chain(clist: ConfirmationList, rows: Mapping[str, dict],
               series: Mapping[str, Series]) -> dict | None:
    """Holm, composite (pending), DSR, t and PBO for every Tier A trial; None without Tier A."""
    tier_a = [t.member for t in clist.trials if t.tier == "A"]
    if not tier_a:
        return None
    # A Tier A trial without a series enters Holm at p = 1 (no evidence; it cannot reject).
    pvalues = {m: rows[m].get("p_upper", 1.0) for m in tier_a}
    holm = holm_tier_a(pvalues, HOLM_K)
    a_series = [m for m in tier_a if m in series]
    run_series = [t.member for t in clist.trials if t.member in series]
    moms = {m: moments(series[m].values.tolist()) for m in run_series}
    dsr_over = a_series if len(a_series) >= 2 else run_series
    if len(dsr_over) >= 2:
        table, dsr_undefined = dsr_table(moms, dsr_over, clist.program_n, a_series), None
    else:  # SF-1: a one-series Sharpe variance is undefined (V14 c); no DSR is computed
        table, dsr_undefined = None, DSR_VARIANCE_UNDEFINED
    pbo_set = a_series if len(a_series) >= 2 else run_series
    window = _union_dates({m: series[m] for m in run_series}) if run_series else []
    pbo_out = _pbo_over(pbo_set, series, window)
    rejected = set(holm.rejected)
    verdicts = {m: _chain_verdict(m, m in rejected, moms.get(m), table, dsr_undefined, pbo_out,
                                  LABEL_SOURCE_OVERLAP in rows[m]["labels"]) for m in tier_a}
    return {"holm": {"k": holm.k_clusters, "alpha_k": holm.alpha_k, "m": holm.m,
                     "rows": [_holm_row(r) for r in holm.rows]},
            "composite": COMPOSITE_PENDING,
            "dsr": {**({k: v for k, v in table.items() if k not in ("dsr", "undefined")}
                       if table is not None else {}),
                    "variance_over": list(dsr_over), "undefined": dsr_undefined},
            "pbo": pbo_out, "trials": verdicts}


def _chain_verdict(member: str, holm_rejects: bool, mom: Mapping[str, float] | None,
                   table: Mapping[str, Any] | None, dsr_undefined: str | None,
                   pbo_out: Mapping[str, Any], source_overlap: bool) -> dict:
    """One Tier A trial's chain: every step reported; the first failing one named. An undefined
    DSR or PBO fails its step and says so in the verdict (review N-4)."""
    t_value = t_stat(mom) if mom is not None else None
    if mom is None:
        d_value, d_undefined = None, "no series"
    elif table is None:
        d_value, d_undefined = None, dsr_undefined
    else:
        d_value, d_undefined = table["dsr"].get(member), table["undefined"].get(member)
    pbo_value, p_undefined = pbo_out["pbo"], pbo_out["undefined"]
    steps = {"holm": holm_rejects, "composite": COMPOSITE_PENDING,
             "dsr": d_value is not None and d_value > DSR_MIN,
             "t": t_value is not None and t_value > T_MIN,
             "pbo": pbo_value is not None and pbo_value < PBO_MAX}
    failing = next((k for k in ("holm", "dsr", "t", "pbo") if not steps[k]), None)
    if failing == "dsr" and d_value is None:
        verdict = NO_EDGE_DSR_UNDEFINED
    elif failing == "pbo" and pbo_value is None:
        verdict = NO_EDGE_PBO_UNDEFINED
    elif failing:
        verdict = NO_EDGE
    else:
        verdict = SOURCE_OVERLAP_PASS if source_overlap else LABEL_EDGE_CANDIDATE
    return {"verdict": verdict, "first_failing_step": failing, "passes": steps,
            "dsr": d_value, "dsr_undefined": d_undefined, "t_stat": t_value, "pbo": pbo_value,
            "pbo_undefined": p_undefined}


def _holm_row(row: Any) -> dict:
    return {"member": row.member_id, "p_value": row.p_value, "rank": row.rank,
            "threshold": row.threshold, "reject": row.reject}


def _pbo_over(members: Sequence[str], series: Mapping[str, Series], window: Sequence[date]
              ) -> dict:
    base = {"over": list(members), "window_days": len(window)}
    if len(members) < 2:
        return {**base, "pbo": None, "undefined": "fewer than 2 series: no selection (L-E5-3)"}
    if len(window) // N_PBO_BLOCKS < 1:
        return {**base, "pbo": None, "undefined": f"{len(window)} days cannot form 8 blocks"}
    aligned = {m: aligned_series(series[m].dates, series[m].values, window) for m in members}
    out = pbo(aligned)
    return {**base, **out, "undefined": None}


# ------------------------------------------------------ cluster statement ----
def null_statement(clist: ConfirmationList, rows: Mapping[str, dict],
                   chain: Mapping[str, Any] | None = None) -> dict:
    """NULL_CRITERIA_E 1, 6 and 7: "null" or "no statement", with who is not covered and why.
    A blocking Tier A trial carries its edge-chain verdict beside its null status."""
    verdicts = (chain or {}).get("trials", {})
    covered = [t for t in clist.trials if t.covered]
    not_covered = [{"member": t.member,
                    "reason": LABEL_INCONCLUSIVE_BY_DESIGN if t.run else
                    "not run: excluded (not Tier A or B)", "labels": list(t.labels)}
                   for t in clist.trials if not t.covered]
    blocking = [{"member": t.member, "status": rows[t.member]["status"],
                 "reasons": rows[t.member]["reasons"],
                 "edge_chain": verdicts.get(t.member, {}).get("verdict")}
                for t in covered if rows[t.member]["status"] not in (NULL, NULL_INACTIVE)]
    verdict = STATEMENT_NULL if covered and not blocking else NO_STATEMENT
    return {"verdict": verdict, "covered": [t.member for t in covered],
            "not_covered": not_covered, "blocking": blocking,
            "null_by_inactivity": [t.member for t in covered
                                   if rows[t.member]["status"] == NULL_INACTIVE],
            "note": None if covered else "no covered trial: nothing to state"}


def resolution_table(clist: ConfirmationList, rows: Mapping[str, dict]) -> list[dict]:
    """NULL_CRITERIA_E 7, per exposure (vehicle): eps_X, q_X, the fewest-trip covered trial and
    its count, the largest per-trade upper bound, the inactivity labels, the trials not covered."""
    out = []
    for vehicle in sorted({t.vehicle for t in clist.trials}):
        trials = [t for t in clist.trials if t.vehicle == vehicle]
        first = trials[0]
        fig = [rows[t.member] for t in trials if t.covered and "n_trips" in rows[t.member]]
        fewest = min(fig, key=lambda r: (r["n_trips"], r["member"])) if fig else None
        per_trade = [r for r in fig if r["ucb95_per_trade"] is not None]
        largest = max(per_trade, key=lambda r: (r["ucb95_per_trade"], r["member"])) \
            if per_trade else None
        out.append({
            "vehicle": vehicle, "q_c": first.q_c, "eps_ticks": first.eps_ticks,
            "eps_usd_per_day_at_q": first.eps_usd_per_day_at_q,
            "fewest_trips": None if fewest is None else {"member": fewest["member"],
                                                         "n_trips": fewest["n_trips"]},
            "largest_ucb95_per_trade": None if largest is None else {
                "member": largest["member"], "ticks": largest["ucb95_per_trade"]},
            "null_by_inactivity": [r["member"] for r in fig if r["status"] == NULL_INACTIVE],
            "not_covered": [t.member for t in trials if not t.covered]})
    return out


# ------------------------------------------------------------------ run ----
def evaluate(list_payload: Mapping[str, Any], records: Mapping[str, Mapping[str, Any]],
             n_resamples: int = BOOTSTRAP_RESAMPLES) -> dict:
    """The verdict of one cluster from its list and its confirmation records (by member).
    ``n_resamples`` is for tests only; the CLI uses the list's (10,000)."""
    clist = parse_list(list_payload)
    listed = {t.member for t in clist.trials}
    extra = sorted(set(records) - listed)
    if extra:
        raise VerdictRefusal(f"records not in the list: {extra}")
    rows, series = {}, {}
    for trial in clist.trials:
        record = records.get(trial.member)
        if trial.run and record is None:
            raise VerdictRefusal(f"{trial.member}: marked run in the list, no record")
        # An excluded trial may have a record (the runner's --all runs every frozen member):
        # it is checked against the list like any other and never used.
        got = check_record(record, trial, clist) if record is not None else None
        if got is not None and trial.run:
            series[trial.member] = got
        status = None if record is None else record.get("status")
        rows[trial.member] = _trial_row(trial, got, status, n_resamples)
    chain = edge_chain(clist, rows, series)
    return {"schema": VERDICT_SCHEMA, "cluster": clist.cluster,
            "harness_sha256": clist.harness_sha256,
            "cluster_freeze_sha256": clist.cluster_freeze_sha256,
            "program_n": clist.program_n, "k_holm": HOLM_K,
            "constants": {"seed_base": BOOTSTRAP_SEED_BASE, "resamples": n_resamples,
                          "mean_block": MEAN_BLOCK_DAYS, "ucb_quantile": UCB_QUANTILE,
                          "null_z": NULL_Z, "null_power_min": NULL_POWER_MIN,
                          "inactivity_min": INACTIVITY_MIN, "dsr_min": DSR_MIN, "t_min": T_MIN,
                          "pbo_max": PBO_MAX, "pbo_blocks": N_PBO_BLOCKS},
            "trials": [rows[t.member] for t in clist.trials],
            "edge_chain": chain,
            "statement": null_statement(clist, rows, chain),
            "resolution": resolution_table(clist, rows)}


def load_records(records_dir: Path, list_payload: Mapping[str, Any]) -> dict[str, dict]:
    """The cluster's confirmation member records in ``records_dir`` by member (trip files are
    not read). A record file of this cluster that names no list trial is refused."""
    clist = parse_list(list_payload)
    names = {record_name(clist.cluster, t.member): t.member for t in clist.trials}
    prefix = record_name(clist.cluster, "x")[: -len(f"x_{CONFIRMATION_WINDOW}.json")]
    out = {}
    for path in sorted(Path(records_dir).glob(f"*_{CONFIRMATION_WINDOW}.json")):
        if not path.name.startswith(prefix):
            continue
        if path.name not in names:
            raise VerdictRefusal(f"record {path.name} is not in the list")
        out[names[path.name]] = json.loads(path.read_text(encoding="utf-8"))
    return out


def write_verdict(verdict: Mapping[str, Any], out: Path) -> Path:
    data = json.dumps(verdict, indent=2, sort_keys=True, default=_json_default) + "\n"
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        with out.open("x", encoding="utf-8") as fh:
            fh.write(data)
    except FileExistsError as exc:
        raise VerdictRefusal(f"{out} already exists; the verdict is written once") from exc
    return out


def _json_default(value: Any) -> Any:
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(f"not JSON serializable: {type(value).__name__}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m screening.stage_e_verdict")
    parser.add_argument("--harness-sha256", required=True)
    parser.add_argument("--list", required=True, type=Path)
    parser.add_argument("--records", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        path, verdict = _run(args)
    except (VerdictRefusal, harness_freeze.HarnessFreezeError, OSError, ValueError) as exc:
        print(f"REFUSED ({type(exc).__name__}): {exc}", file=sys.stderr)
        return 2
    print(f"{path}: {verdict['cluster']} statement {verdict['statement']['verdict']}")
    return 0


def _run(args: argparse.Namespace) -> tuple[Path, dict]:
    harness = harness_freeze.preflight(args.harness_sha256)  # first, before any file is read
    if args.out.exists():
        raise VerdictRefusal(f"{args.out} already exists; the verdict is written once")
    raw = args.list.read_bytes()
    payload = json.loads(raw.decode("utf-8"))
    if payload.get("harness_sha256") != harness:
        raise VerdictRefusal(f"list harness {payload.get('harness_sha256')!r} is not the "
                             f"preflighted {harness}")
    verdict = evaluate(payload, load_records(args.records, payload))
    verdict = {**verdict, "list_sha256": hashlib.sha256(raw).hexdigest(),
               "list_file": args.list.name}
    return write_verdict(verdict, args.out), verdict


if __name__ == "__main__":
    sys.exit(main())
