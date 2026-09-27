"""Stage E D4 power check per member: the D.1e Task 3 method at eps_X.

docs/STAGE_E_DESIGN.md D4 and docs/NULL_CRITERIA_E.md 5: n_b from the member's research-window
daily series, analytic, and the block-bootstrap simulation where the two differ by more than 15%
(the larger governs); a member whose n_b exceeds the days its confirmation window supplies after
exclusions is labelled "inconclusive by design" before confirmation.

Everything is in ticks/ct/day (screening/stage_e_stats_units.py); eps_X comes from the frozen
E.2a table by the series' vehicle. The inference core below is strategy/research/
_d1e_power_stats.py's, restated here so the frozen Stage E harness (screening/) carries it; the
tests prove it equal to D.1e's function for function and reproduce the recorded D.1e figures
(reports/stage_d1e_power.json) for MES at MES's eps = 34 ticks per micro per day.

- Null power target: the one-sided 95% UCB (mean + 1.645 SE) lands below eps with 80%
  probability when the true mean is 0. Analytic: n_b = ceil(((z_95 + z_80) sd sqrt(VIF) / eps)^2),
  sd with ddof 1, VIF = V_B / gamma_0 with V_B the Politis-Romano stationary-bootstrap variance
  (p = 1/5, lags 1..20, floored at 0.2 gamma_0).
- Simulation: 2,000 stationary-bootstrap replicates (mean block 5) of the CENTRED series per
  length; replicate SE = sqrt(var_ddof1(replicate) * VIF(source) / n) (D.1e lead ruling);
  power_b(n) = share of replicates with mean + 1.645 SE < eps; n_b_sim = the first grid length
  reaching 0.80, refined linearly in log n. Lengths: the D.1e grid (10 .. 3,000) plus n_a and n_b
  themselves, each when <= 3,000 (memory guard). Seed = POWER_SEED_BASE + the member's ordinal
  (a fresh generator per member).
- Chosen n_b (D.1e ``_chosen``): if |sim - analytic| / analytic > 15% the larger governs (a
  smaller simulated figure is recorded and ignored); a censored simulation (the shortest length
  already at 80%) keeps the analytic figure.
- Stage E generalization (conservative, D.1e never met it; accepted by the lead): if the
  simulation never reaches 80% on the grid, the simulated threshold is above the longest length,
  n_b_chosen is None (unknown, larger than the grid) and the label is decided from the bounds:
  inconclusive when analytic > supply, or when the longest length is >= supply and >= 1.15 x
  analytic; otherwise the case cannot be decided and raises PowerCheckUndefined.
- n_a (lead ruling OC-I, descriptive only; the label depends on n_b alone): the D.1e detection
  size, ceil(((z_a + z_80) sd sqrt(VIF) / eps)^2) and its simulated curve (share of replicates
  with t > z_a at true mean eps), chosen by the same 15% rule. z_a is one-sided at
  alpha = 0.05 / (9 x m_c): Holm's most stringent step fixed in advance, 9 = at most 8 clusters
  plus the ML route, m_c = the cluster's member count in the frozen E.1 recount (D5). n_a joins
  the simulation lengths exactly as in D.1e (grid plus n_a plus n_b, each only if <= 3,000).
- Refusals by name (PowerCheckUndefined): fewer than two days, a non-finite value, a
  zero-variance research series (no trips: the power check has nothing to measure; lead ruling:
  the refusal stays, the runner catches and records it).
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from statistics import NormalDist
from types import MappingProxyType
from typing import Any

import numpy as np

from funnel.null_generator import stationary_bootstrap_indices
from screening.stage_e_stats_units import DailySeries, frozen_epsilon

# ------------------------------------------------------------- constants ----

POWER_TARGET = 0.80
UCB_LEVEL = 0.95
MEAN_BLOCK = 5.0
BOOTSTRAP_RENEWAL_P = 1.0 / MEAN_BLOCK
MAX_LAG_K = 20
VIF_FLOOR_FRACTION = 0.2
SWITCH_FRACTION = 0.15  # "differ by more than 15%"
POWER_REPLICATIONS = 2000
POWER_GRID = (10, 15, 20, 30, 50, 75, 100, 150, 200, 300, 500, 750, 1000, 1500, 2000, 3000)
POWER_SEED_BASE = 20260922  # D.1e Task 3's seed base; seed = base + member ordinal
MIN_SIM_N = 2

# n_a (descriptive, lead ruling OC-I): one-sided z at alpha = 0.05 / (9 x m_c), 9 = at most 8
# clusters plus the ML route (V6, audit ML-A14), m_c = the cluster's active member count in the
# frozen E.1 recount, docs/STAGE_E_DESIGN.md D5 ("K1 5 / 11; K2 8 / 44; K3 9 / 31; K4 8 / 19;
# K5 7 / 16; K6 7 / 27; K7 6 / 6; K8 3 / 4. Total: 53 members, 158 trials").
DETECTION_FAMILY_ALPHA = 0.05
DETECTION_FAMILY_DIVISOR = 9
CLUSTER_MEMBER_COUNTS = MappingProxyType(
    {"K1": 5, "K2": 8, "K3": 9, "K4": 8, "K5": 7, "K6": 7, "K7": 6, "K8": 3}
)

_ND = NormalDist()
Z_POWER = _ND.inv_cdf(POWER_TARGET)
Z_UCB = _ND.inv_cdf(UCB_LEVEL)

LABEL_INCONCLUSIVE = "inconclusive by design"
LABEL_SUFFICIENT = "power sufficient"


class PowerCheckUndefined(ValueError):
    """The power check cannot be computed or decided for this member; the reason is named."""


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


def _bootstrap_variance(x: np.ndarray, k_max: int = MAX_LAG_K) -> tuple[Any, Any, Any]:
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
    v_b, gamma0, hit_floor = _bootstrap_variance(np.asarray(x, dtype=float), k_max)
    if float(gamma0) <= 0.0:
        return 1.0, bool(hit_floor)
    return float(v_b) / float(gamma0), bool(hit_floor)


def lag1_autocorrelation(x: np.ndarray) -> float:
    gammas = sample_autocovariances(x, 1)
    gamma0 = float(gammas[0])
    return float(gammas[1]) / gamma0 if gamma0 > 0.0 else 0.0


def analytic_sample_size(z_level: float, sd_day: float, vif: float, eps_day: float) -> int:
    """ceil(((z_level + z_80) * sd * sqrt(VIF) / eps)^2); 0 when sd or eps is not positive."""
    if eps_day <= 0.0 or sd_day <= 0.0:
        return 0
    return int(math.ceil((((z_level + Z_POWER) * sd_day * math.sqrt(vif)) / eps_day) ** 2))


def interpolate_threshold(
    ns: Sequence[int], powers: Sequence[float], target: float = POWER_TARGET
) -> float | None:
    """Smallest grid n reaching ``target``, refined linearly in log(n); None if never reached."""
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
    ns: Sequence[int], powers: Sequence[float], target: float = POWER_TARGET
) -> bool:
    """True when the SHORTEST simulated length already meets the target (never bracketed)."""
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


def simulate_power_curve(
    e: np.ndarray,
    eps_day: float,
    ns: Sequence[int],
    seed: int,
    replications: int = POWER_REPLICATIONS,
    z_detect: float | None = None,
) -> tuple[dict[int, dict[str, float]], bool, int]:
    """Bootstrap power curves over ``ns`` (in order) from the centred series ``e``.

    power_b(n): share of replicates whose closed-form UCB95 is below eps (true mean 0).
    power_a(n), only when ``z_detect`` is given: share whose t at true mean eps exceeds z_detect
    (D.1e's detection curve; descriptive here, kept so D.1e's rows reproduce in full).
    Returns the curve, whether the source's V_B hit the floor, and the zero-variance draw count.
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
        ucb = means + Z_UCB * se
        power_b = float(np.mean(ucb < eps_day))
        row = {"power_b": power_b, "se_b": _binomial_se(power_b, replications)}
        if z_detect is not None:
            shifted = means + eps_day
            safe_se = np.where(positive, se, 1.0)
            t_stat = np.where(positive, shifted / safe_se, np.inf * np.sign(shifted))
            power_a = float(np.mean(t_stat > z_detect))
            row["power_a"] = power_a
            row["se_a"] = _binomial_se(power_a, replications)
        curve[n] = row
    return curve, bool(source_floored), degenerate


# ---------------------------------------------------------- chosen and label ----


def choose_null_days(
    analytic: int, simulated: float | None, censored: bool, tag: str = "b"
) -> tuple[int | None, float | None, tuple[str, ...]]:
    """(chosen, diff_pct, flags): D.1e's ``_chosen``, plus None when the grid is never reached.

    ``tag`` is "b" (null days, the criterion) or "a" (detection days, descriptive).
    """
    if tag not in ("a", "b"):
        raise ValueError(f"tag must be 'a' or 'b', got {tag!r}")
    if simulated is None:
        return None, None, (f"power_{tag}_never_reaches_target",)
    diff_pct = 100.0 * (simulated - analytic) / analytic if analytic > 0 else 0.0
    if censored:
        return analytic, diff_pct, (f"sim_censored_below_grid_{tag}",)
    if abs(diff_pct) > 100.0 * SWITCH_FRACTION:
        simulated_days = int(math.ceil(simulated))
        if simulated_days > analytic:
            return simulated_days, diff_pct, (f"sim_used_larger_{tag}",)
        return analytic, diff_pct, (f"sim_smaller_ignored_{tag}",)
    return analytic, diff_pct, ()


def label_power(
    n_b_chosen: int | None, n_b_analytic: int, max_length: int, supply_days: int
) -> tuple[bool, str]:
    """(inconclusive_by_design, label) from n_b alone: n_b > supply is inconclusive by design."""
    if n_b_chosen is not None:
        inconclusive = n_b_chosen > supply_days
    elif n_b_analytic > supply_days:
        inconclusive = True  # the chosen figure is never below the analytic one
    elif max_length >= supply_days and max_length >= (1.0 + SWITCH_FRACTION) * n_b_analytic:
        inconclusive = True  # simulated threshold > max_length: it governs and exceeds supply
    else:
        raise PowerCheckUndefined(
            f"the simulation never reached {POWER_TARGET:.0%} by n = {max_length} and the label "
            f"cannot be decided (analytic n_b {n_b_analytic}, supply {supply_days})"
        )
    return inconclusive, (LABEL_INCONCLUSIVE if inconclusive else LABEL_SUFFICIENT)


# ------------------------------------------------------- detection level (OC-I) ----


def detection_alpha(cluster: str) -> float:
    """alpha for n_a: 0.05 / (9 x m_c), the most stringent Holm step fixed in advance (OC-I)."""
    if cluster not in CLUSTER_MEMBER_COUNTS:
        raise ValueError(f"unknown cluster {cluster!r}; known: {sorted(CLUSTER_MEMBER_COUNTS)}")
    return DETECTION_FAMILY_ALPHA / (DETECTION_FAMILY_DIVISOR * CLUSTER_MEMBER_COUNTS[cluster])


def detection_z(alpha: float) -> float:
    """One-sided z at ``alpha``: Phi^-1(1 - alpha)."""
    if not 0.0 < alpha < 1.0:
        raise ValueError(f"alpha must be in (0, 1), got {alpha!r}")
    return _ND.inv_cdf(1.0 - alpha)


# ------------------------------------------------------------- per member ----


@dataclass(frozen=True)
class SeriesStatistics:
    days: int
    mean: float
    sd_day: float  # ddof 1
    lag1: float
    vif_boot: float
    vif_floored: bool


def series_statistics(daily: np.ndarray) -> SeriesStatistics:
    values = np.asarray(daily, dtype=float)
    if values.ndim != 1 or len(values) < 2:
        raise PowerCheckUndefined("the power check needs a 1-D series of at least two days")
    if not np.all(np.isfinite(values)):
        raise PowerCheckUndefined("the research-window series has a non-finite value")
    vif, floored = variance_inflation(values)
    return SeriesStatistics(
        days=len(values),
        mean=float(values.mean()),
        sd_day=float(np.std(values, ddof=1)),
        lag1=lag1_autocorrelation(values),
        vif_boot=vif,
        vif_floored=floored,
    )


@dataclass(frozen=True)
class CurvePoint:
    n: int
    power_b: float  # share of replicates with UCB95 < eps at true mean 0
    se_b: float  # binomial se of power_b
    power_a: float | None  # share with t > z_a at true mean eps (None when n_a is not computed)
    se_a: float | None


@dataclass(frozen=True)
class NullPowerFigures:
    """The power figures of one series at one eps (no identity, no label)."""

    stats: SeriesStatistics
    eps_ticks: float
    seed: int
    replications: int
    lengths: tuple[int, ...]
    curve: tuple[CurvePoint, ...]
    zero_variance_draws: int
    n_b_analytic: int
    n_b_sim: float | None
    n_b_censored: bool
    diff_b_pct: float | None
    n_b_chosen: int | None
    z_a: float | None  # None: n_a not computed
    n_a_analytic: int | None
    n_a_sim: float | None
    n_a_censored: bool | None
    diff_a_pct: float | None
    n_a_chosen: int | None
    flags: tuple[str, ...]

    def curve_power_b(self, n: int) -> float:
        return self._point(n).power_b

    def curve_power_a(self, n: int) -> float | None:
        return self._point(n).power_a

    def _point(self, n: int) -> CurvePoint:
        for point in self.curve:
            if point.n == n:
                return point
        raise KeyError(f"length {n} was not simulated")


def _default_lengths(analytic_sizes: Sequence[int]) -> tuple[int, ...]:
    """D.1e's lengths: the grid plus each analytic size (n_a, n_b), those above the grid left out
    (memory guard; flagged by the caller)."""
    wanted = set(POWER_GRID)
    for size in analytic_sizes:
        if size <= max(POWER_GRID):
            wanted.add(max(size, MIN_SIM_N))
    return tuple(sorted(n for n in wanted if n >= MIN_SIM_N))


def _pick_threshold(
    lengths: Sequence[int], powers: Sequence[float], analytic: int, tag: str
) -> tuple[float | None, bool, int | None, float | None, tuple[str, ...]]:
    simulated = interpolate_threshold(lengths, powers)
    censored = threshold_is_censored(lengths, powers)
    chosen, diff_pct, flags = choose_null_days(analytic, simulated, censored, tag)
    return simulated, censored, chosen, diff_pct, flags


def null_power_figures(
    daily: np.ndarray,
    eps_ticks: float,
    seed: int,
    lengths: Sequence[int] | None = None,
    replications: int = POWER_REPLICATIONS,
    z_detect: float | None = None,
) -> NullPowerFigures:
    """Analytic and simulated n_b (and n_a when ``z_detect`` is given) at ``eps_ticks``.

    ``lengths`` defaults to D.1e's rule (the grid plus n_a and n_b); tests pass D.1e's recorded
    lengths to reproduce its rows. Stage E sessions call ``power_check``, which fixes eps, the
    detection level, the seed and the lengths.
    """
    if not (math.isfinite(eps_ticks) and eps_ticks > 0.0):
        raise ValueError(f"eps must be finite and > 0 ticks/ct/day, got {eps_ticks!r}")
    stats = series_statistics(daily)
    if stats.sd_day <= 0.0:
        raise PowerCheckUndefined(
            "the research-window series has zero variance (no trips, or every day identical): "
            "n_b cannot be measured"
        )
    flags: list[str] = ["vif_floored"] if stats.vif_floored else []
    n_b = analytic_sample_size(Z_UCB, stats.sd_day, stats.vif_boot, eps_ticks)
    n_a = (
        None if z_detect is None
        else analytic_sample_size(z_detect, stats.sd_day, stats.vif_boot, eps_ticks)
    )
    for tag, size in (("a", n_a), ("b", n_b)):
        if size is not None and size > max(POWER_GRID):
            flags.append(f"n_{tag}_analytic_above_grid")
    if lengths is not None:
        sim_lengths = tuple(lengths)
    else:
        sim_lengths = _default_lengths([s for s in (n_a, n_b) if s is not None])
    if not sim_lengths or list(sim_lengths) != sorted(set(sim_lengths)) or sim_lengths[0] < 2:
        raise ValueError(f"lengths must be ascending, unique and >= 2, got {sim_lengths!r}")
    centred = np.asarray(daily, dtype=float) - stats.mean
    curve, _floored, degenerate = simulate_power_curve(
        centred, eps_ticks, sim_lengths, seed, replications, z_detect=z_detect
    )
    if degenerate:
        flags.append("zero_variance_draws")
    a_fields: tuple = (None, None, None, None)
    if n_a is not None:
        powers_a = [curve[n]["power_a"] for n in sim_lengths]
        sim_a, cens_a, chosen_a, diff_a, flags_a = _pick_threshold(sim_lengths, powers_a, n_a, "a")
        a_fields = (sim_a, cens_a, diff_a, chosen_a)
        flags.extend(flags_a)
    powers_b = [curve[n]["power_b"] for n in sim_lengths]
    sim_b, cens_b, chosen_b, diff_b, flags_b = _pick_threshold(sim_lengths, powers_b, n_b, "b")
    flags.extend(flags_b)
    return NullPowerFigures(
        stats=stats,
        eps_ticks=float(eps_ticks),
        seed=seed,
        replications=replications,
        lengths=sim_lengths,
        curve=tuple(
            CurvePoint(n, curve[n]["power_b"], curve[n]["se_b"],
                       curve[n].get("power_a"), curve[n].get("se_a"))
            for n in sim_lengths
        ),
        zero_variance_draws=degenerate,
        n_b_analytic=n_b,
        n_b_sim=sim_b,
        n_b_censored=cens_b,
        diff_b_pct=diff_b,
        n_b_chosen=chosen_b,
        z_a=z_detect,
        n_a_analytic=n_a,
        n_a_sim=a_fields[0],
        n_a_censored=a_fields[1],
        diff_a_pct=a_fields[2],
        n_a_chosen=a_fields[3],
        flags=tuple(flags),
    )


@dataclass(frozen=True)
class PowerCheck:
    """D4's power check of one member at its exposure's frozen eps_X (ticks/ct/day)."""

    member_id: str
    vehicle: str
    cluster: str
    ordinal: int
    seed: int
    eps_ticks: int
    eps_usd_per_day_at_q: float
    epsilon_table_sha256: str
    research_days: int
    mean_ticks: float
    sd_day_ticks: float  # ddof 1
    lag1: float
    vif_boot: float
    vif_floored: bool
    n_b_analytic: int
    n_b_sim: float | None
    n_b_censored: bool
    diff_b_pct: float | None
    n_b_chosen: int | None  # None: never reached 80% on the grid (threshold > max length)
    cluster_members: int  # m_c, the frozen E.1 recount (OC-I)
    alpha_a: float  # 0.05 / (9 x m_c)
    z_a: float
    n_a_analytic: int  # descriptive only (OC-I)
    n_a_sim: float | None
    n_a_censored: bool
    diff_a_pct: float | None
    n_a_chosen: int | None
    supply_days: int
    inconclusive_by_design: bool  # from n_b alone
    label: str
    flags: tuple[str, ...]
    curve: tuple[CurvePoint, ...]
    replications: int
    lengths: tuple[int, ...]
    zero_variance_draws: int


def _non_negative_int(value: object, what: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{what} must be an int >= 0, got {value!r}")
    return value


def power_check(series: DailySeries, cluster: str, ordinal: int, supply_days: int) -> PowerCheck:
    """The D4 power check of ``series`` at its vehicle's frozen eps_X.

    ``cluster``: "K1".."K8" (a cross-cluster member: "K8"); sets n_a's level (OC-I).
    ``ordinal``: the member's ordinal in its cluster list (seed = POWER_SEED_BASE + ordinal).
    ``supply_days``: the days the member's confirmation window supplies after exclusions.
    """
    alpha_a = detection_alpha(cluster)
    _non_negative_int(ordinal, "ordinal")
    _non_negative_int(supply_days, "supply_days")
    frozen = frozen_epsilon(series.vehicle)
    seed = POWER_SEED_BASE + ordinal
    z_a = detection_z(alpha_a)
    figures = null_power_figures(series.array(), float(frozen.eps_ticks), seed, z_detect=z_a)
    inconclusive, label = label_power(
        figures.n_b_chosen, figures.n_b_analytic, max(figures.lengths), supply_days
    )
    stats = figures.stats
    return PowerCheck(
        member_id=series.member_id,
        vehicle=series.vehicle,
        cluster=cluster,
        ordinal=ordinal,
        seed=seed,
        eps_ticks=frozen.eps_ticks,
        eps_usd_per_day_at_q=frozen.eps_usd_per_day_at_q,
        epsilon_table_sha256=frozen.source_sha256,
        research_days=stats.days,
        mean_ticks=stats.mean,
        sd_day_ticks=stats.sd_day,
        lag1=stats.lag1,
        vif_boot=stats.vif_boot,
        vif_floored=stats.vif_floored,
        n_b_analytic=figures.n_b_analytic,
        n_b_sim=figures.n_b_sim,
        n_b_censored=figures.n_b_censored,
        diff_b_pct=figures.diff_b_pct,
        n_b_chosen=figures.n_b_chosen,
        cluster_members=CLUSTER_MEMBER_COUNTS[cluster],
        alpha_a=alpha_a,
        z_a=z_a,
        n_a_analytic=int(figures.n_a_analytic),
        n_a_sim=figures.n_a_sim,
        n_a_censored=bool(figures.n_a_censored),
        diff_a_pct=figures.diff_a_pct,
        n_a_chosen=figures.n_a_chosen,
        supply_days=supply_days,
        inconclusive_by_design=inconclusive,
        label=label,
        flags=figures.flags,
        curve=figures.curve,
        replications=figures.replications,
        lengths=figures.lengths,
        zero_variance_draws=figures.zero_variance_draws,
    )
