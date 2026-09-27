"""Stage E statistics the runner calls: the D5 screen and tiers, Holm at alpha_k, and (re-exported)
the D4 power check, the D4 start rule and the unit helpers. Pure functions; no bar is read.

Sources: docs/STAGE_E_DESIGN.md D4 and D5 (frozen), docs/NULL_CRITERIA_E.md 3 to 5, lead ruling
OC-H (Stage E.2b, 2026-09-26 12:58 PDT) on D9-excluded members.

One unit everywhere: net ticks per contract per day of the vehicle ("ticks/ct/day"), the unit of
eps_X (screening/stage_e_stats_units.py). Frozen values (eps_X, q_c, tick value) are read from
reports/stage_e2a_epsilon.json by vehicle, never passed in.

Public signatures
-----------------
Units and series (screening/stage_e_stats_units.py):
    Trip(trade_date: date, net_usd: float, contracts: int)
    DailySeries(member_id, vehicle, dates: tuple[date, ...], values: tuple[float, ...] ticks/ct/day,
                n_trips); .array() -> np.ndarray
    daily_series_from_trips(member_id, vehicle, trips, window_dates) -> DailySeries
    daily_series_from_leg_dollars(member_id, primary_vehicle, daily_net_usd: Mapping[date, float],
                                  window_dates, n_trips) -> DailySeries
    FrozenEpsilon(vehicle, eps_ticks, q_c, tick_value_usd, eps_usd_per_day_at_q, source_sha256)
    frozen_epsilon(vehicle) -> FrozenEpsilon
    ticks_to_usd_per_day(ticks_per_contract, q_c, tick_value_usd) -> float
D5 screen (this module):
    screen(series: DailySeries) -> ScreenResult
        passes = mean > 0 and daily t >= 1.0, over every window date (zeros on no-trade days);
        t = mean / (population sd / sqrt(n)), the program's pinned daily t
        (funnel.multiple_comparisons.harvey_liu_zhu_verdict, as D.1f 3.2 uses it).
    assign_tiers(cluster, members: Sequence[TierInput]) -> ClusterTiers
        tier "A" (unlabelled, passes), "B" (unlabelled, fails) or "excluded" (any D9 label,
        whatever its screen says; lead ruling OC-H).
    k_from_tiers(tiers: Sequence[ClusterTiers], *, route_tested: bool) -> int
        # clusters with a non-empty Tier A, plus 1 when the ML route has a tested rule (V6, F-4)
Holm (this module):
    holm_alpha_k(k_clusters: int) -> float                  # 0.05 / K, K an int in 1..9 (V6)
    holm_tier_a(pvalues: Mapping[str, float], k_clusters: int) -> HolmResult
D4 power check (screening/stage_e_stats_power.py):
    power_check(series: DailySeries, cluster: str, ordinal: int, supply_days: int) -> PowerCheck
        label from n_b alone; n_a descriptive at alpha = 0.05 / (9 x m_c) (lead ruling OC-I)
D4 start rule (screening/stage_e_stats_start.py):
    first_trade_dates_by_month(trade_dates) -> dict[str, date]
    start_rule(vehicle, reference_medians, extension_medians, first_trade_dates) -> StartRule
"""

from __future__ import annotations

import math
import statistics
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from funnel.multiple_comparisons import harvey_liu_zhu_verdict
from screening.stage_e_stats_power import (
    CLUSTER_MEMBER_COUNTS,
    LABEL_INCONCLUSIVE,
    LABEL_SUFFICIENT,
    POWER_GRID,
    POWER_REPLICATIONS,
    POWER_SEED_BASE,
    CurvePoint,
    PowerCheck,
    PowerCheckUndefined,
    detection_alpha,
    power_check,
)
from screening.stage_e_stats_start import (
    BINDING_FRACTION,
    EARLIEST_START,
    EXTENSION_MONTHS,
    REFERENCE_MONTHS,
    SENSITIVITY_FRACTIONS,
    StartAt,
    StartRule,
    first_trade_dates_by_month,
    start_rule,
)
from screening.stage_e_stats_units import (
    UNIT,
    DailySeries,
    FrozenEpsilon,
    Trip,
    _aggregate_trips,
    daily_series_from_leg_dollars,
    daily_series_from_trips,
    frozen_epsilon,
    ticks_to_usd_per_day,
)

__all__ = [
    "BINDING_FRACTION", "CLUSTER_MEMBER_COUNTS", "D9_LABELS", "EARLIEST_START",
    "EXTENSION_MONTHS", "FAMILY_ALPHA", "LABEL_INCONCLUSIVE", "LABEL_SUFFICIENT", "MAX_CLUSTERS",
    "MAX_FAMILIES",
    "POWER_GRID", "POWER_REPLICATIONS", "POWER_SEED_BASE", "REFERENCE_MONTHS", "SCREEN_T_MIN",
    "SENSITIVITY_FRACTIONS", "UNIT",
    "ClusterTiers", "CurvePoint", "DailySeries", "FrozenEpsilon", "HolmResult", "HolmRow",
    "MemberTier", "PowerCheck", "PowerCheckUndefined", "ScreenResult", "ScreenUndefined",
    "StartAt", "StartRule", "TierInput", "Trip", "_aggregate_trips", "assign_tiers",
    "daily_series_from_leg_dollars", "daily_series_from_trips", "detection_alpha",
    "first_trade_dates_by_month", "frozen_epsilon", "holm_alpha_k", "holm_tier_a",
    "k_from_tiers", "power_check", "screen", "start_rule", "ticks_to_usd_per_day",
]

SCREEN_T_MIN = 1.0
FAMILY_ALPHA = 0.05
MAX_CLUSTERS = 8  # cluster ids K1..K8
# V6 (docs/DECISIONS.md, Stage E.2a freeze ruling on audit ML-A14): K counts every family with a
# non-empty tested set, the ML route included once it has a tested rule; D5's "at most 8" reads
# "at most 9" (review finding F-4).
MAX_FAMILIES = MAX_CLUSTERS + 1

TIER_A, TIER_B, TIER_EXCLUDED = "A", "B", "excluded"
COVERAGE_LABEL = "coverage_below_0.95"
# D9: coverage < 0.95 excludes before screening; the trade-rate floor (a) at most 20 entries per
# product per trade date, (b) the 2-minute minimum hold and (c) mean hold >= 10 minutes exclude
# before confirmation (lead ruling OC-H).
D9_LABELS = (
    COVERAGE_LABEL,
    "mean_holding_below_10min",
    "entries_above_20_per_day",
    "hold_below_2min",
)


# ---------------------------------------------------------------- screen ----


class ScreenUndefined(ValueError):
    """The D5 screen cannot be decided for this series; the reason is named."""


@dataclass(frozen=True)
class ScreenResult:
    member_id: str
    n_days: int
    n_trips: int
    mean_ticks: float  # ticks/ct/day over every window date, zeros included
    sd_pop_ticks: float  # population sd (ddof 0)
    t_daily: float | None  # None only when sd = 0 and mean <= 0 (the member fails on the mean)
    passes: bool


def screen(series: DailySeries) -> ScreenResult:
    """D5: research-window mean net P&L > 0 and daily t >= 1.0 (zeros on no-trade days)."""
    values = list(series.values)
    n = len(values)
    if n < 2:
        raise ScreenUndefined(f"{series.member_id}: the screen needs at least two window days")
    if not all(math.isfinite(v) for v in values):
        raise ScreenUndefined(f"{series.member_id}: the series has a non-finite value")
    mean = statistics.fmean(values)
    sd = statistics.pstdev(values)
    if sd > 0.0:
        t = float(harvey_liu_zhu_verdict(mean, sd, n)["t_stat"])
        passes = mean > 0.0 and t >= SCREEN_T_MIN
    elif mean <= 0.0:
        t, passes = None, False
    else:
        raise ScreenUndefined(
            f"{series.member_id}: sd = 0 with mean {mean} > 0; the daily t is undefined"
        )
    return ScreenResult(
        member_id=series.member_id,
        n_days=n,
        n_trips=series.n_trips,
        mean_ticks=mean,
        sd_pop_ticks=sd,
        t_daily=t,
        passes=passes,
    )


# ----------------------------------------------------------------- tiers ----


@dataclass(frozen=True)
class TierInput:
    member_id: str
    screen: ScreenResult | None  # None only for a coverage-excluded member (never screened)
    labels: tuple[str, ...] = ()  # D9 exclusion labels


@dataclass(frozen=True)
class MemberTier:
    member_id: str
    tier: str  # "A", "B" or "excluded"
    screen: ScreenResult | None
    labels: tuple[str, ...]
    note: str


@dataclass(frozen=True)
class ClusterTiers:
    cluster: str
    members: tuple[MemberTier, ...]

    def _ids(self, tier: str) -> tuple[str, ...]:
        return tuple(m.member_id for m in self.members if m.tier == tier)

    @property
    def tier_a(self) -> tuple[str, ...]:
        return self._ids(TIER_A)

    @property
    def tier_b(self) -> tuple[str, ...]:
        return self._ids(TIER_B)

    @property
    def excluded(self) -> tuple[str, ...]:
        return self._ids(TIER_EXCLUDED)

    @property
    def has_tier_a(self) -> bool:
        return bool(self.tier_a)


def _tier_one(item: TierInput) -> MemberTier:
    labels = tuple(item.labels)
    unknown = [label for label in labels if label not in D9_LABELS]
    if unknown:
        raise ValueError(f"{item.member_id}: unknown label(s) {unknown}; known: {D9_LABELS}")
    if item.screen is not None and item.screen.member_id != item.member_id:
        raise ValueError(f"{item.member_id}: its screen belongs to {item.screen.member_id!r}")
    if COVERAGE_LABEL in labels:
        if item.screen is not None:
            raise ValueError(f"{item.member_id}: a coverage-excluded member is not screened "
                             "(screen must be None)")
        return MemberTier(item.member_id, TIER_EXCLUDED, None, labels,
                          "excluded before screening (D9 coverage; ruling OC-H)")
    if labels:
        if item.screen is None:
            raise ValueError(f"{item.member_id}: a member excluded for {labels} keeps its screen "
                             "result (ruling OC-H)")
        return MemberTier(item.member_id, TIER_EXCLUDED, item.screen, labels,
                          "excluded before confirmation (D9 trade-rate/holding floor; ruling OC-H)")
    if item.screen is None:
        raise ValueError(f"{item.member_id}: an unlabelled member needs its screen result")
    tier = TIER_A if item.screen.passes else TIER_B
    note = "passes the D5 screen" if item.screen.passes else "fails the D5 screen"
    return MemberTier(item.member_id, tier, item.screen, labels, note)


def assign_tiers(cluster: str, members: Sequence[TierInput]) -> ClusterTiers:
    """D5 tiers of one cluster (ruling OC-H for labelled members), in input order."""
    if not members:
        raise ValueError(f"{cluster}: no members to tier")
    seen: set[str] = set()
    for item in members:
        if item.member_id in seen:
            raise ValueError(f"{cluster}: member {item.member_id!r} listed twice")
        seen.add(item.member_id)
    return ClusterTiers(cluster=cluster, members=tuple(_tier_one(m) for m in members))


def k_from_tiers(tiers: Sequence[ClusterTiers], *, route_tested: bool) -> int:
    """K = the clusters with a non-empty Tier A, plus one when the ML route has a tested rule
    (V6, audit ML-A14; review F-4). 1..9; K = 0 raises (nothing to test).

    ``route_tested`` is a required keyword with no default, so no caller can forget the route.
    """
    if not isinstance(route_tested, bool):
        raise ValueError(f"route_tested must be a bool, got {route_tested!r}")
    names = [t.cluster for t in tiers]
    duplicated = sorted({n for n in names if names.count(n) > 1})
    if duplicated:
        raise ValueError(f"clusters listed twice: {duplicated}")
    clusters = sum(1 for t in tiers if t.has_tier_a)
    if clusters > MAX_CLUSTERS:
        raise ValueError(
            f"{clusters} clusters with a non-empty Tier A; at most {MAX_CLUSTERS} exist"
        )
    k = clusters + (1 if route_tested else 0)
    if k == 0:
        raise ValueError("K = 0: no cluster has a non-empty Tier A and the route has no tested "
                         "rule, so there is no Holm family")
    return _checked_k(k)


# ------------------------------------------------------------------ Holm ----


def _checked_k(k_clusters: object) -> int:
    if isinstance(k_clusters, bool) or not isinstance(k_clusters, int):
        raise ValueError(f"K must be an int in 1..{MAX_FAMILIES}, got {k_clusters!r}")
    if not 1 <= k_clusters <= MAX_FAMILIES:
        raise ValueError(f"K must be in 1..{MAX_FAMILIES}, got {k_clusters}")
    return k_clusters


def holm_alpha_k(k_clusters: int) -> float:
    """alpha_k = 0.05 / K, K the number of families with a non-empty tested set: the clusters
    with a non-empty Tier A, plus the ML route once it has a tested rule (D5 read with V6: every
    family then tests at 0.05 / (K_clusters + 1)); K in 1..9. The parameter keeps its name
    ``k_clusters`` for existing callers; it counts families."""
    return FAMILY_ALPHA / _checked_k(k_clusters)


@dataclass(frozen=True)
class HolmRow:
    member_id: str
    p_value: float
    rank: int  # 1 = smallest p
    threshold: float  # alpha_k / (m - rank + 1)
    reject: bool


@dataclass(frozen=True)
class HolmResult:
    k_clusters: int
    alpha_k: float
    m: int  # Tier A size
    rows: tuple[HolmRow, ...]  # ascending p (ties broken by member id)

    @property
    def rejected(self) -> tuple[str, ...]:
        return tuple(r.member_id for r in self.rows if r.reject)


def holm_tier_a(pvalues: Mapping[str, float], k_clusters: int) -> HolmResult:
    """Holm step-down over one family's one-sided p-values (a cluster's Tier A, or the ML
    route's tested rules) at family-wise 0.05 / K, K in 1..9."""
    alpha_k = holm_alpha_k(k_clusters)
    if not pvalues:
        raise ValueError("an empty Tier A has no Holm family")
    for key, p in pvalues.items():
        if not (isinstance(p, (int, float)) and not isinstance(p, bool) and math.isfinite(p)
                and 0.0 <= p <= 1.0):
            raise ValueError(f"p-value of {key!r} must be in [0, 1], got {p!r}")
    m = len(pvalues)
    order = sorted(pvalues, key=lambda k: (pvalues[k], k))
    rows, rejecting = [], True
    for i, key in enumerate(order):
        threshold = alpha_k / (m - i)
        rejecting = rejecting and pvalues[key] <= threshold
        rows.append(HolmRow(key, float(pvalues[key]), i + 1, threshold, rejecting))
    return HolmResult(k_clusters=k_clusters, alpha_k=alpha_k, m=m, rows=tuple(rows))
