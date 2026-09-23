"""Stage D.1f step 8: the decision rules of reports/stage_d1f_confirmation_list.md 3.1 to 3.6.

Pure functions over per-member daily series (net ticks per micro per day, each on the member's
OWN date set). No bars, no files, no screening: ``_d1f_confirmation`` builds the members in
step 7 and hands them here. Everything below is the frozen text, implemented literally.

3.1 Per member: theta_hat = mean(d_t); stationary block bootstrap through
    ``funnel.null_generator.stationary_bootstrap_indices(rng, n, n, 5.0)`` exactly as
    ``screening.drift.bootstrap_mean_lower_bounds`` uses it, B = 10,000, a FRESH
    ``np.random.default_rng(20260921)`` per member; UCB95 = np.quantile(means, 0.95) (linear);
    SE_boot = np.std(means) (ddof 0); p = (1 + #{theta* - theta_hat >= theta_hat}) / (B + 1).
    Per-trade translation theta_hat / r and UCB95 / r, r = activity per own date (reporting
    only).
3.2 Edge exists (Tier A only): Holm step-down over the Tier A p at family-wise 5% rejects it;
    its composite screening verdict is "pass"; DSR > 0.95 at N = 58 with the population
    variance of the 58 Tier A daily Sharpes and ``_d1b_accounting._moments`` on d_t;
    t = harvey_liu_zhu_verdict(mean, population sd, n_days) > 3.0; PBO over the 58 Tier A
    series on 8 contiguous equal blocks of n_days // 8 dates < 0.5.
3.3 Null for a class: every Tier A and Tier B member has UCB95 < epsilon_day = 34 and achieved
    power Phi(34 / SE_boot - 1.645) >= 0.80; SE_boot = 0 fails. Fewer than 30 trips / events
    with both conditions met: "null by inactivity".
3.4 Inconclusive otherwise; zero trips / events or SE_boot = 0 is inconclusive (N-2).
3.5 C6: C-H4 below epsilon is "null under the pessimistic fill model"; the class stays
    inconclusive until D.1g. A pass under the pessimistic model is a pass.
3.6 Per calendar year theta_hat and UCB95, descriptive.
2.2 Tier B: anomaly iff BH-significant (one-sided, direction s) at 10% within Tier B and net
    edge per event >= +2.11 ticks; sign reversal reported separately (lead ruling (c)).

LEAD RULINGS for points the frozen text leaves open (Stage D.1f lead, Task 7 brief; not
re-decided here):
(a) PBO and any cross-member matrix align members on the full window date list (S..2024-02-29,
    every trade date of the confirmation parquet); each member's series sits on its own dates
    and is 0 elsewhere (a no-event day is 0, the list's own within-member convention). DSR and
    t use each member's own series (3.2(iii): "_moments on the member's d_t").
(b) Reported-only accounting: at N = 101, DSR with the population variance over the 101 Tier A
    + Tier B daily Sharpes and PBO over those 101 series; at N = 186, DSR only, N = 186 with the
    101-member variance (the 85 EDA statistics have no confirmation series beyond Tiers A and
    B). t is unchanged by N. Precedent: _d1d_accounting's N = 116 sensitivity widened N and
    kept the variance over the members that have a series (there, the 31 trials).
(c) Tier B sign reversal (revised): "a sign reversal versus the mined window" (2.2) is about the
    DIRECTION of the effect, so it is tested on the GROSS per-date series g_t = the sum of s x e
    over the date's events, 0 on dates without events, on the member's own post-exclusion dates
    (``gross_daily``: g_t = d_t + 2.11 x n_t, since v = s x e - 2.11 per event), one-sided for
    mean < 0: p = (1 + #{theta* - theta_hat <= theta_hat}) / (B + 1) with the same bootstrap
    (a fresh default_rng(20260921), mean block 5, B = 10,000), BH at 10% within Tier B, run
    separately from the anomaly BH. A member whose net mean is negative only because of the
    2.11-tick cost is NOT a reversal. The anomaly test is unchanged: net v, one-sided in
    direction s, BH at 10%, mean v per event >= 2.11.
(d) Year slices: bootstrap within each year's slice with a fresh default_rng(20260921) per
    member per slice.

Readings of this module where the frozen text is silent (reported to the lead, not rulings):
- A Tier A member can both pass 3.2 and meet 3.3 (a real edge below epsilon). Its status is
  "edge"; the class null is decided on 3.3 alone ("every member satisfies both").
- "Net edge >= +2.11 ticks per event" (2.2) is read literally on the net value v: the mean of
  v over the member's events (= theta_hat / r) must be >= 2.11.
- The class's "per-trade epsilon at its confirmation-window frequency" (NULL_CRITERIA 1, 7)
  uses NULL_CRITERIA 2.3's definition of the typical frequency moved to the confirmation
  window: the median trades per window day of the class's trial members.
"""

from __future__ import annotations

import math
import statistics
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from itertools import combinations

import numpy as np

from funnel.multiple_comparisons import (
    HLZ_HURDLE,
    deflated_sharpe_ratio,
    harvey_liu_zhu_verdict,
    probability_of_backtest_overfitting,
)
from funnel.null_generator import stationary_bootstrap_indices
from strategy.research._d1b_accounting import _blocks, _moments

EPSILON_DAY_TICKS = 34.0  # net ticks per micro per day (NULL_CRITERIA 2.2, FINAL)
STAT_COST_TICKS = 2.11  # flat modelled round turn per event (list 2.1 A2)
BOOTSTRAP_RESAMPLES = 10_000
BOOTSTRAP_SEED = 20_260_921
MEAN_BLOCK_DAYS = 5.0
UCB_QUANTILE = 0.95
NULL_Z = 1.645  # as 3.3 writes it: Phi(epsilon_day / SE_boot - 1.645)
NULL_POWER_MIN = 0.80
INACTIVITY_MIN = 30
HOLM_FWE = 0.05
BH_Q = 0.10
DSR_MIN = 0.95
T_MIN = HLZ_HURDLE  # 3.0
PBO_MAX = 0.5
N_PBO_BLOCKS = 8
N_TIER_A = 58
N_TIER_B = 43
N_EDA_STATISTICS = 85  # Family F's 57 + Family G's 28 declared EDA statistics (N = 186)
PRIOR_N = 31
C6 = "C6"
CLASSES = ("C1", "C2", "C3", "C4", "C5", "C6", "C7")
EDGE, NULL, INCONCLUSIVE = "edge", "null", "inconclusive"
LABEL_INACTIVITY = "null by inactivity"
LABEL_PESSIMISTIC = "null under the pessimistic fill model"


@dataclass(frozen=True)
class Member:
    """One list member's daily series on its own dates (trial: every window date; statistic:
    its post-exclusion dates). ``daily`` in net ticks per micro per day; ``daily_activity``
    closed round trips or events per date; ``composite`` the 3.2(ii) verdict (Tier A)."""

    member_id: str
    tier: str  # "A" | "B"
    kind: str  # "trial" | "statistic"
    klass: str  # "C1" .. "C7"
    dates: tuple[date, ...]
    daily: np.ndarray
    daily_activity: np.ndarray
    composite: str | None = None  # "pass" | "fail"; None for Tier B
    direction: int | None = None  # s, statistics only
    extra: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.tier not in ("A", "B") or self.klass not in CLASSES:
            raise ValueError(f"{self.member_id}: bad tier {self.tier!r} or class {self.klass!r}")
        if not (len(self.dates) == len(self.daily) == len(self.daily_activity)) or not self.dates:
            raise ValueError(f"{self.member_id}: dates, daily and activity must align, non-empty")
        if list(self.dates) != sorted(set(self.dates)):
            raise ValueError(f"{self.member_id}: dates must be strictly increasing")
        if self.tier == "A" and self.composite not in ("pass", "fail"):
            raise ValueError(f"{self.member_id}: a Tier A member needs a composite verdict")

    @property
    def n_activity(self) -> int:
        return int(np.sum(self.daily_activity))

    @property
    def activity_per_day(self) -> float:
        return self.n_activity / len(self.dates)


# ------------------------------------------------------------------ bootstrap ----
@dataclass(frozen=True)
class Bootstrap:
    n_days: int
    theta_hat: float
    ucb95: float
    se_boot: float
    p_upper: float  # H0: theta <= 0 (3.1)
    p_lower: float  # H0: theta >= 0; lead ruling (c) reads it on the GROSS Tier B series


def resampled_means(daily: np.ndarray, n_resamples: int = BOOTSTRAP_RESAMPLES,
                    seed: int = BOOTSTRAP_SEED, mean_block: float = MEAN_BLOCK_DAYS
                    ) -> np.ndarray:
    """The B bootstrap means, drawn exactly as ``bootstrap_mean_lower_bounds`` draws them."""
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
    values = np.asarray(daily, dtype=float)
    theta = float(values.mean())
    centred = means - theta
    b = len(means)
    return Bootstrap(
        n_days=len(values), theta_hat=theta, ucb95=float(np.quantile(means, UCB_QUANTILE)),
        se_boot=float(np.std(means)),
        p_upper=(1 + int(np.sum(centred >= theta))) / (b + 1),
        p_lower=(1 + int(np.sum(centred <= theta))) / (b + 1))


def bootstrap(daily: np.ndarray, n_resamples: int = BOOTSTRAP_RESAMPLES) -> Bootstrap:
    """3.1 for one series, with its own fresh generator."""
    return summarize_means(daily, resampled_means(daily, n_resamples))


def null_power(se_boot: float, epsilon: float = EPSILON_DAY_TICKS) -> float:
    """Phi(epsilon / SE_boot - 1.645); 0.0 when SE_boot = 0 (3.3: such a member fails)."""
    if se_boot <= 0.0:
        return 0.0
    return 0.5 * (1.0 + math.erf((epsilon / se_boot - NULL_Z) / math.sqrt(2.0)))


# ------------------------------------------------------- multiple comparisons ----
def holm(pvalues: Mapping[str, float], alpha: float = HOLM_FWE) -> dict[str, dict]:
    """Holm step-down: sort ascending, reject while p_(i) <= alpha / (m - i + 1)."""
    m = len(pvalues)
    order = sorted(pvalues, key=lambda k: (pvalues[k], k))
    out, rejecting = {}, True
    for i, key in enumerate(order):
        threshold = alpha / (m - i)
        rejecting = rejecting and pvalues[key] <= threshold
        out[key] = {"rank": i + 1, "threshold": threshold, "reject": rejecting}
    return out


def benjamini_hochberg(pvalues: Mapping[str, float], q: float = BH_Q) -> dict[str, dict]:
    """BH step-up: reject ranks 1..k, k the largest rank with p_(k) <= k q / m."""
    m = len(pvalues)
    order = sorted(pvalues, key=lambda k: (pvalues[k], k))
    k_max = max((i + 1 for i, key in enumerate(order) if pvalues[key] <= (i + 1) * q / m),
                default=0)
    return {key: {"rank": i + 1, "threshold": (i + 1) * q / m, "reject": i + 1 <= k_max}
            for i, key in enumerate(order)}


def aligned_series(member: Member, window_dates: Sequence[date]) -> np.ndarray:
    """Lead ruling (a): the member's series on the full window date list, 0 off its dates."""
    index = {d: i for i, d in enumerate(window_dates)}
    missing = [d for d in member.dates if d not in index]
    if missing:
        raise ValueError(f"{member.member_id}: {len(missing)} own dates outside the window, "
                         f"e.g. {missing[0]}")
    out = np.zeros(len(window_dates))
    for d, v in zip(member.dates, member.daily, strict=True):
        out[index[d]] = v
    return out


def _dsr(moments: dict, n_trials: int, variance: float) -> tuple[float | None, str | None]:
    if moments["sd"] <= 0:
        return None, "sd = 0"
    try:
        return deflated_sharpe_ratio(moments["sharpe"], moments["n"], n_trials, variance,
                                     moments["skew"], moments["kurtosis"]
                                     )["deflated_sharpe_ratio"], None
    except ValueError as exc:  # degenerate moments: recorded, the member fails the criterion
        return None, str(exc)


def _t_stat(moments: dict) -> float | None:
    if moments["sd"] <= 0 or moments["n"] < 2:
        return None
    return harvey_liu_zhu_verdict(moments["mean"], moments["sd"], moments["n"])["t_stat"]


def dsr_table(moments: Mapping[str, dict], variance_over: Sequence[str], n_trials: int,
              members: Sequence[str]) -> dict:
    variance = statistics.pvariance([moments[k]["sharpe"] for k in variance_over])
    benchmark = deflated_sharpe_ratio(0.0, 2, n_trials, variance)["expected_max_sharpe_under_null"]
    dsr, notes = {}, {}
    for key in members:
        dsr[key], note = _dsr(moments[key], n_trials, variance)
        if note:
            notes[key] = note
    return {"n_trials": n_trials, "variance_over_n_members": len(variance_over),
            "sharpe_variance": variance, "expected_max_daily_sharpe_under_null": benchmark,
            "dsr": dsr, "undefined": notes}


def pbo(series: Mapping[str, np.ndarray]) -> dict:
    """CSCV PBO on 8 contiguous blocks of n_days // 8 dates (``_d1b_accounting._blocks``)."""
    labels = list(series)
    n_days = len(next(iter(series.values())))
    if n_days // N_PBO_BLOCKS < 1:
        raise ValueError(f"{n_days} window days cannot form {N_PBO_BLOCKS} blocks")
    matrix = [_blocks(list(series[k])) for k in labels]
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


# ------------------------------------------------------------------ per member ----
def year_slices(member: Member, n_resamples: int = BOOTSTRAP_RESAMPLES) -> dict[str, dict]:
    """3.6, lead ruling (d): per calendar year, a fresh generator per member per slice."""
    years = np.array([d.year for d in member.dates])
    out = {}
    for year in sorted(set(years.tolist())):
        mask = years == year
        boot = bootstrap(member.daily[mask], n_resamples)
        out[str(year)] = {"n_days": boot.n_days, "activity": int(member.daily_activity[mask].sum()),
                          "theta_hat": boot.theta_hat, "ucb95": boot.ucb95}
    return out


def _per_trade(value: float, member: Member) -> float | None:
    r = member.activity_per_day
    return value / r if r > 0 else None


def _member_core(member: Member, boot: Bootstrap) -> dict:
    power = null_power(boot.se_boot)
    no_evidence = member.n_activity == 0 or boot.se_boot == 0.0
    ucb_ok, power_ok = boot.ucb95 < EPSILON_DAY_TICKS, power >= NULL_POWER_MIN
    return {
        "id": member.member_id, "tier": member.tier, "kind": member.kind, "class": member.klass,
        "direction_s": member.direction, "n_days": boot.n_days,
        "first_date": str(member.dates[0]), "last_date": str(member.dates[-1]),
        "n_activity": member.n_activity, "activity_per_day": member.activity_per_day,
        "theta_hat": boot.theta_hat, "ucb95": boot.ucb95, "se_boot": boot.se_boot,
        "p_one_sided": boot.p_upper,
        "per_trade": {"theta_hat": _per_trade(boot.theta_hat, member),
                      "ucb95": _per_trade(boot.ucb95, member)},
        "null": {"ucb95_below_epsilon": ucb_ok, "achieved_power": power,
                 "power_at_least_80": power_ok, "no_evidence_n2": no_evidence,
                 "meets": (not no_evidence) and ucb_ok and power_ok},
        "composite": member.composite,
    }


@dataclass(frozen=True)
class Evaluation:
    tier_a: dict[str, dict]
    tier_b: dict[str, dict]
    family: dict
    classes: dict[str, dict]


def _accounting(members_a: Sequence[Member], members_b: Sequence[Member],
                window_dates: Sequence[date]) -> tuple[dict, dict[str, dict]]:
    all_members = [*members_a, *members_b]
    moments = {m.member_id: _moments([float(x) for x in m.daily]) for m in all_members}
    ids_a = [m.member_id for m in members_a]
    ids_all = [m.member_id for m in all_members]
    aligned = {m.member_id: aligned_series(m, window_dates) for m in all_members}
    n_a, n_all = len(ids_a), len(ids_all)
    family = {
        "n_trials": {"prior": PRIOR_N, "after_d1f": n_a, "reported_101": n_all,
                     "reported_186": n_all + N_EDA_STATISTICS},
        "dsr_n58": dsr_table(moments, ids_a, n_a, ids_a),
        "pbo_n58": pbo({k: aligned[k] for k in ids_a}),
        "reported_dsr_n101": dsr_table(moments, ids_all, n_all, ids_all),
        "reported_pbo_n101": pbo(aligned),
        "reported_dsr_n186": dsr_table(moments, ids_all, n_all + N_EDA_STATISTICS, ids_all),
        "alignment": "lead ruling (a): full window date list, 0 off a member's own dates",
        "window_n_days": len(window_dates),
    }
    per_member = {}
    for key in ids_all:
        t = _t_stat(moments[key])
        per_member[key] = {
            "moments": moments[key], "t_stat": t,
            "dsr_n58": family["dsr_n58"]["dsr"].get(key),
            "dsr_n101": family["reported_dsr_n101"]["dsr"][key],
            "dsr_n186": family["reported_dsr_n186"]["dsr"][key],
        }
    return family, per_member


def _edge_checks(row: dict, acct: dict, holm_row: dict, pbo58: float) -> dict:
    dsr = acct["dsr_n58"]
    t = acct["t_stat"]
    checks = {"holm_reject": holm_row["reject"], "composite_pass": row["composite"] == "pass",
              "dsr_above_0_95": dsr is not None and dsr > DSR_MIN,
              "t_above_3": t is not None and t > T_MIN,
              "pbo_below_0_5": not math.isnan(pbo58) and pbo58 < PBO_MAX}
    return {**checks, "passes": all(checks.values())}


def _status(row: dict, tier: str, klass: str) -> tuple[str, list[str]]:
    labels = []
    if tier == "A" and row["edge_checks"]["passes"]:
        status = EDGE
    elif row["null"]["meets"]:
        status = NULL
    else:
        status = INCONCLUSIVE
    if row["null"]["meets"]:
        if row["n_activity"] < INACTIVITY_MIN:
            labels.append(LABEL_INACTIVITY)
        if klass == C6:
            labels.append(LABEL_PESSIMISTIC)
    if row["null"]["no_evidence_n2"]:
        labels.append("no evidence (N-2): zero trips/events or SE_boot = 0")
    return status, labels


def evaluate(members_a: Sequence[Member], members_b: Sequence[Member],
             window_dates: Sequence[date], n_resamples: int = BOOTSTRAP_RESAMPLES) -> Evaluation:
    """Every decision rule of 3.1 to 3.6 over the whole list. ``window_dates`` is the full
    confirmation window (lead ruling (a))."""
    ids = [m.member_id for m in (*members_a, *members_b)]
    if len(set(ids)) != len(ids):
        raise ValueError("member ids must be unique")
    if any(m.tier != "A" for m in members_a) or any(m.tier != "B" for m in members_b):
        raise ValueError("members passed under the wrong tier")
    boots = {m.member_id: bootstrap(m.daily, n_resamples) for m in (*members_a, *members_b)}
    family, acct = _accounting(members_a, members_b, window_dates)
    holm_rows = holm({m.member_id: boots[m.member_id].p_upper for m in members_a})
    family["holm"] = {"alpha": HOLM_FWE, "m": len(members_a),
                      "rejected": sorted(k for k, v in holm_rows.items() if v["reject"])}
    pbo58 = family["pbo_n58"]["pbo"]
    tier_a = {}
    for m in members_a:
        row = _member_core(m, boots[m.member_id])
        row["holm"] = holm_rows[m.member_id]
        row["accounting"] = acct[m.member_id]
        row["edge_checks"] = _edge_checks(row, acct[m.member_id], holm_rows[m.member_id], pbo58)
        tier_a[m.member_id] = _finish(row, m, n_resamples)
    tier_b = _tier_b(members_b, boots, acct, n_resamples)
    family["tier_b_bh"] = {"q": BH_Q, "m": len(members_b)}
    classes = class_verdicts([*members_a, *members_b], {**tier_a, **tier_b})
    return Evaluation(tier_a, tier_b, family, classes)


def _finish(row: dict, member: Member, n_resamples: int) -> dict:
    row["status"], row["labels"] = _status(row, member.tier, member.klass)
    row["year_slices"] = year_slices(member, n_resamples)
    row["extra"] = dict(member.extra)
    row["dates"] = [str(d) for d in member.dates]
    row["daily_ticks_per_micro"] = [float(x) for x in member.daily]
    row["daily_activity"] = [int(x) for x in member.daily_activity]
    return row


def gross_daily(member: Member) -> np.ndarray:
    """Lead ruling (c): a statistic's GROSS per-date series, the sum of s x e over each own date's
    events (0 on a date without events). Per event v = s x e - 2.11 (list 2.1 A2), so
    g_t = d_t + 2.11 x n_t with n_t the date's event count."""
    if member.kind != "statistic":
        raise ValueError(f"{member.member_id}: only a statistic has a gross s x e series")
    return (np.asarray(member.daily, dtype=float)
            + STAT_COST_TICKS * np.asarray(member.daily_activity, dtype=float))


def _tier_b(members_b: Sequence[Member], boots: Mapping[str, Bootstrap],
            acct: Mapping[str, dict], n_resamples: int) -> dict[str, dict]:
    anomaly_bh = benjamini_hochberg({m.member_id: boots[m.member_id].p_upper for m in members_b})
    gross = {m.member_id: bootstrap(gross_daily(m), n_resamples) for m in members_b}
    reversal_bh = benjamini_hochberg({k: g.p_lower for k, g in gross.items()})
    out = {}
    for m in members_b:
        row = _member_core(m, boots[m.member_id])
        net_per_event = _per_trade(row["theta_hat"], m)
        g = gross[m.member_id]
        row["accounting"] = acct[m.member_id]
        row["anomaly"] = {"bh": anomaly_bh[m.member_id], "net_edge_per_event": net_per_event,
                          "flag": anomaly_bh[m.member_id]["reject"] and net_per_event is not None
                          and net_per_event >= STAT_COST_TICKS}
        row["sign_reversal"] = {
            "series": "gross per-date sum of s x e on the member's own dates (lead ruling (c))",
            "theta_hat_gross": g.theta_hat, "gross_per_event": _per_trade(g.theta_hat, m),
            "ucb95_gross": g.ucb95, "p_one_sided_gross_below_0": g.p_lower,
            "bh": reversal_bh[m.member_id], "flag": reversal_bh[m.member_id]["reject"]}
        row["edge_checks"] = None  # Tier B never carries an edge claim (2.2)
        out[m.member_id] = _finish(row, m, n_resamples)
    return out


# --------------------------------------------------------------------- classes ----
def class_verdicts(members: Sequence[Member], rows: Mapping[str, dict]) -> dict[str, dict]:
    """3.3 / 3.4 / 3.5 per class, plus the fields NULL_CRITERIA 7 requires of a statement."""
    out = {}
    for klass in CLASSES:
        group = [m for m in members if m.klass == klass]
        if not group:
            out[klass] = {"verdict": "no members", "members": []}
            continue
        not_null = [m.member_id for m in group if not rows[m.member_id]["null"]["meets"]]
        inconclusive = [m.member_id for m in group
                        if rows[m.member_id]["status"] == INCONCLUSIVE]
        edge = [m.member_id for m in group if rows[m.member_id]["status"] == EDGE]
        if klass == C6:
            verdict = "inconclusive until Stage D.1g (list 3.5)"
        elif not_null:
            verdict = "no null statement"
        else:
            verdict = NULL
        out[klass] = {"verdict": verdict, "members": [m.member_id for m in group],
                      "members_not_meeting_null": not_null, "inconclusive": inconclusive,
                      "passing_confirmation": edge,
                      "statement_fields": _statement_fields(group, rows)}
    return out


def _statement_fields(group: Sequence[Member], rows: Mapping[str, dict]) -> dict:
    trial_rates = [m.activity_per_day for m in group if m.kind == "trial"]
    frequency = float(np.median(trial_rates)) if trial_rates else None
    least = min(group, key=lambda m: (m.n_activity, m.member_id))
    per_trade_ucb = [(rows[m.member_id]["per_trade"]["ucb95"], m.member_id) for m in group
                     if rows[m.member_id]["per_trade"]["ucb95"] is not None]
    largest = max(per_trade_ucb) if per_trade_ucb else (None, None)
    inactive = sorted(m.member_id for m in group
                      if LABEL_INACTIVITY in rows[m.member_id].get("labels", []))
    return {
        "class_frequency_trades_per_day": frequency,
        "class_frequency_definition": "median trades per window day of the class's trial "
                                      "members (NULL_CRITERIA 2.3's rule on the confirmation "
                                      "window)",
        "epsilon_per_trade": (EPSILON_DAY_TICKS / frequency) if frequency else None,
        "least_active_member": {"id": least.member_id, "count": least.n_activity},
        "largest_per_trade_ucb95": {"value": largest[0], "member": largest[1]},
        "null_by_inactivity_members": inactive,
        "label": LABEL_INACTIVITY if inactive else None,
    }
