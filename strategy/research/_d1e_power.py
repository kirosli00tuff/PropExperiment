"""Stage D.1e Task 3: power and sample size for the MES class null.

    uv run python -m strategy.research._d1e_power --eps-day 34

What this answers. The D.1f class null asks, for each class of hypotheses, how
many confirmation days are needed (a) to DETECT a true net edge of ``eps_day``
ticks per micro per day with 80% power at the Holm-corrected one-sided level,
and (b) to RULE OUT such an edge with 80% probability when the true edge is
zero, i.e. for the one-sided 95% upper confidence bound to land below
``eps_day``.

Units. Net ticks per micro per day throughout.
- Trial member: ``d_t = daily_net_ticks_per_micro[t]``, taken as is from
  ``reports/stage_d1e_members_trials.json``. That artifact divides EACH round
  trip by its OWN contract quantity, ``trip_pnl_usd / (1.25 * trip_micros)``,
  and sums the trips closing on date t.

  UNIT CORRECTION (reports/stage_d1e_adjudication.md, finding R-1). This module
  previously read ``daily_net_usd[t] / 2.5``, i.e. it assumed every trial traded
  2 micros. It does not: 29 trials and C-H4 code 1 micro, and D-H2 and RT7 size
  1 to 5 micros by rule. Every trial series was therefore at half its per-micro
  scale, every trial SD was halved, and every trial sample size was a quarter of
  the right one. The proxy per-trade SDs for Family H were read off the same
  half-scale table and are corrected with it (200 ticks for H1-H5, 230 for H6).
  Statistic members were never affected: they are built from tick sums, not
  from dollars.
- Statistic member: ``d_t = s * daily_sum_ticks[t] - 2.11 * daily_count[t]``,
  with ``s`` the recorded confirmation direction and 2.11 ticks the market
  round-turn cost. This is the D.1f tested quantity summed over each day.
- ``e_t = d_t - mean(d)`` is the centred series; every power calculation shifts
  ``e`` to the hypothesised true mean (``eps_day`` or 0).

Multiplicity. The Holm family is m = 58 (31 trials + 21 logged near-misses + 6
Family H tests). Holm's MOST STRINGENT step is 0.05/58, which is exactly
Bonferroni; using it for every member is conservative for every member except
the one tested first, so the sample sizes here are upper bounds on what Holm
actually requires. That conservatism is deliberate and is not corrected for.

Variance. Inference in this program resamples whole days with the circular
stationary block bootstrap (``funnel.null_generator.stationary_bootstrap_indices``,
mean block 5). The variance that bootstrap actually sees is the
Politis-Romano kernel-weighted long-run variance with p = 1/mean_block:

    V_B = gamma_0 + 2 * sum_{k=1..K} (1 - p)^k gamma_k,   K = 20

and ``VIF_boot = V_B / gamma_0`` is the inflation factor over the iid formula.
For a persistent series this is SMALLER than the true long-run factor (for an
AR(1) with phi, V_B/gamma_0 -> 1 + 2*sum((1-p)phi)^k, versus (1+phi)/(1-phi)):
the block-5 bootstrap under-corrects, by design, and the sample sizes below are
the ones the program's own inference implies, not the ones an oracle would give.
``V_B`` is floored at ``0.2 * gamma_0`` so a strongly negatively autocorrelated
series cannot produce a near-zero or negative variance; every floor hit is
flagged and counted.

Simulation SE. A block-bootstrap replicate's own lag-k autocovariance is
already about (1-p)^k times the source's, so computing ``V_B`` from the
REPLICATE attenuates the dependence term a second time and understates the
standard error for an autocorrelated member (measured: simulated power_b of
0.848 instead of 0.80 for an AR(1) with phi = 0.3). The per-replicate standard
error is therefore

    SE_hat = sqrt( gamma_0_hat(x) * VIF_boot(source) / n )

with ``gamma_0_hat(x)`` the replicate's own sample variance (ddof = 1). The
replicate supplies the finite-sample variance noise and the heavy tails; the
dependence factor comes from the source series, exactly as the analytic formula
uses it. (Lead ruling, Stage D.1e Task 3.)

Chosen figure. Where the simulated and analytic sizes differ by more than
15%, the chosen figure is ``max(analytic, simulated)``, not the simulated one.
A simulated size BELOW the analytic one is not evidence that fewer days suffice:
for a heavy-tailed member at short lengths the replicate's variance estimate is
right-skewed, so the closed-form UCB under-covers there and the simulated
threshold is anti-conservative. Where the simulation asks for MORE days than the
closed form (the case the design is looking for), the simulated figure is used.
Both figures and their difference are reported in every row; the flags are
``sim_used_larger_{a,b}`` where the simulation won and
``sim_smaller_ignored_{a,b}`` where it lost. (Lead ruling, Stage D.1e Task 3.)

Numerics. ``Phi^-1`` comes from ``statistics.NormalDist().inv_cdf`` (standard
library) rather than ``scipy.stats.norm.ppf``: scipy is not a project
dependency. The two agree to ~1e-15 at every quantile used here.

Family H (class C7) has never been run, by design. Its rows are PROJECTED from
the proxy rule in ``reports/stage_d1e_coverage.md`` section 5 and are labelled
``kind = "projected"``; they are analytic only, with no simulation.

Outputs ``reports/stage_d1e_power.json`` and ``reports/stage_d1e_power.md``.
Reads nothing but the three Task 1/4 artifacts. No holdout date is touched.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import numpy as np

from strategy.research._d1e_calendar import (
    HOLDOUT2_END,
    HOLDOUT2_START,
    SUPPLY_END,
    SUPPLY_STARTS,
    SUPPLY_TOLERANCE,
    parse_degraded_dates,
    supplied_days,
)
from strategy.research._d1e_power_report import render_markdown
from strategy.research._d1e_power_stats import (
    ALPHA_HOLM,
    HOLM_FAMILY_SIZE,
    MAX_LAG_K,
    MEAN_BLOCK,
    MIN_SIM_N,
    REPLICATIONS,
    SPOT_INNER_B,
    SPOT_REPLICATES,
    VIF_FLOOR_FRACTION,
    Z_HOLM,
    Z_POWER,
    Z_UCB,
    analytic_sample_size,
    interpolate_threshold,
    lag1_autocorrelation,
    percentile_ucb_success,
    simulate_powers,
    threshold_is_censored,
    variance_inflation,
)

# ------------------------------------------------------------- constants ----

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORTS = REPO_ROOT / "reports"
COVERAGE_MD = REPORTS / "stage_d1e_coverage.md"
TRIALS_JSON = REPORTS / "stage_d1e_members_trials.json"
EVENTS_JSON = REPORTS / "stage_d1e_members_events.json"
QUOTES_MD = REPORTS / "stage_d1e_quotes.md"
OUT_JSON = REPORTS / "stage_d1e_power.json"
OUT_MD = REPORTS / "stage_d1e_power.md"

DEFAULT_EPS_DAY = 34.0
MARKET_COST_TICKS = 2.11  # round-turn cost at market fills
PASSIVE_COST_TICKS = 0.98  # round-turn cost at passive fills (cost bar only)

N_GRID = (10, 15, 20, 30, 50, 75, 100, 150, 200, 300, 500, 750, 1000, 1500, 2000, 3000)
SEED_BASE = 20260922
SPOT_SEED_OFFSET = 1_000_000

EPS_REF_PER_TRADE = 1.0  # descriptive reference threshold, net ticks per trade
EPS_SENSITIVITY = (30.0, 32.0, 34.0, 36.0, 38.0, 40.0)

# Family H projection (reports/stage_d1e_coverage.md section 5). f = firing fraction.
FAMILY_H = (
    ("H1 NR4 opening-range breakout", 200.0, 0.25 * 0.9),
    ("H2 NR7 opening-range breakout", 200.0, 0.9 / 7.0),
    ("H3 inside-day opening-range breakout", 200.0, 0.25 * 0.9),
    ("H4 bottom-tercile prior range, breakout", 200.0, 0.9 / 3.0),
    ("H5 top-tercile prior range, opening-range fade", 200.0, 0.9 / 3.0),
    ("H6 prior-close location follow-through", 230.0, 0.4),
)

DESCRIPTIVE_NOTE = "descriptive, not a criterion"


# ------------------------------------------------------------- membership ----


def parse_class_map(coverage_md: str) -> dict[str, str]:
    """Class per member id, read verbatim from coverage.md sections 2, 3 and 4.

    Those rows begin ``| C<n> | <id> |``. Section 1's rows begin with a class
    NAME (``| C1 session-clock effects |``) and so do not match.
    """
    rows = re.findall(r"^\|\s*(C[1-7])\s*\|\s*([^|]+?)\s*\|", coverage_md, re.MULTILINE)
    mapping: dict[str, str] = {}
    for klass, member in rows:
        if member in mapping and mapping[member] != klass:
            raise ValueError(f"coverage.md gives {member!r} two classes")
        mapping[member] = klass
    return mapping


@dataclass(frozen=True)
class Member:
    """One null member: its daily net-ticks-per-micro series and its labels."""

    member_id: str
    klass: str
    tier: str
    kind: str
    daily: np.ndarray | None
    r: float
    sd_day: float
    lag1: float
    vif_boot: float
    vif_floored: bool
    window_days: int | None
    cluster_vif: float | None = None
    flags: tuple[str, ...] = field(default=())

    @property
    def centred(self) -> np.ndarray:
        assert self.daily is not None
        return self.daily - self.daily.mean()


def trial_series(record: dict[str, Any]) -> np.ndarray:
    """Per-micro daily net ticks, taken as is; see the module docstring (R-1).

    No rescaling happens here. The upstream artifact already divides each round
    trip by its own contract quantity, so any assumption about position size in
    this module would reintroduce the error it corrects.
    """
    return np.asarray(record["daily_net_ticks_per_micro"], dtype=float)


def statistic_series(record: dict[str, Any]) -> np.ndarray:
    side = float(record["recorded_direction"])
    sums = np.asarray(record["daily_sum_ticks"], dtype=float)
    counts = np.asarray(record["daily_count"], dtype=float)
    return side * sums - MARKET_COST_TICKS * counts


def _measured_member(
    member_id: str, klass: str, tier: str, kind: str, daily: np.ndarray, trades: float,
    cluster_vif: float | None,
) -> Member:
    vif, floored = variance_inflation(daily)
    n_days = len(daily)
    return Member(
        member_id=member_id,
        klass=klass,
        tier=tier,
        kind=kind,
        daily=daily,
        r=trades / n_days,
        sd_day=float(np.std(daily, ddof=1)),
        lag1=lag1_autocorrelation(daily),
        vif_boot=vif,
        vif_floored=floored,
        window_days=n_days,
        cluster_vif=cluster_vif,
        flags=("vif_floored",) if floored else (),
    )


def projected_member(member_id: str, per_trade_sd: float, firing_fraction: float) -> Member:
    """Family H, from the coverage map's proxy rule. No data, no simulation."""
    return Member(
        member_id=member_id,
        klass="C7",
        tier="H",
        kind="projected",
        daily=None,
        r=firing_fraction,
        sd_day=per_trade_sd * math.sqrt(firing_fraction),
        lag1=0.0,
        vif_boot=1.0,
        vif_floored=False,
        window_days=None,
        flags=("projected",),
    )


def build_members(
    trials: dict[str, Any], events: dict[str, Any], class_map: dict[str, str]
) -> list[Member]:
    members: list[Member] = []
    for label, record in trials["members"].items():
        daily = trial_series(record)
        trades = float(np.sum(record["daily_n_trips"]))
        members.append(
            _measured_member(
                label, class_map[label], "A", "trial", daily, trades,
                float(record["cluster_vif"]),
            )
        )
    for tier, key in (("A", "statistics"), ("B", "coverage_statistics")):
        for stat_id, record in events[key].items():
            daily = statistic_series(record)
            events_total = float(np.sum(record["daily_count"]))
            members.append(
                _measured_member(
                    stat_id, class_map[stat_id], tier, "statistic", daily, events_total, None
                )
            )
    members.extend(projected_member(name, sd, f) for name, sd, f in FAMILY_H)
    return members


# ----------------------------------------------------------------- per row ----


def _sensitivity(member: Member) -> dict[str, int]:
    return {
        f"{eps:g}": analytic_sample_size(Z_UCB, member.sd_day, member.vif_boot, eps)
        for eps in EPS_SENSITIVITY
    }


def _eps_min_table(member: Member, supply: dict[str, dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    scale = (Z_UCB + Z_POWER) * member.sd_day * math.sqrt(member.vif_boot)
    for start, info in supply.items():
        days = info["confirmation_days"]
        per_day = scale / math.sqrt(days) if days > 0 else None
        out[start] = {
            "per_day": per_day,
            "per_trade": (per_day / member.r) if (per_day is not None and member.r > 0) else None,
        }
    return out


def _eps_ref_days(member: Member) -> dict[str, int | None]:
    eps_ref_day = member.r * EPS_REF_PER_TRADE
    if eps_ref_day <= 0.0:
        return {"n_a": None, "n_b": None, "eps_day_ref": 0.0}
    return {
        "n_a": analytic_sample_size(Z_HOLM, member.sd_day, member.vif_boot, eps_ref_day),
        "n_b": analytic_sample_size(Z_UCB, member.sd_day, member.vif_boot, eps_ref_day),
        "eps_day_ref": eps_ref_day,
    }


def _simulation_lengths(n_a: int, n_b: int, grid: tuple[int, ...]) -> list[int]:
    wanted = set(grid) | {max(n_a, MIN_SIM_N), max(n_b, MIN_SIM_N)}
    return sorted(n for n in wanted if n >= MIN_SIM_N)


def _chosen(
    analytic: int, simulated: float | None, censored: bool, tag: str
) -> tuple[int, float | None, list[str]]:
    """max(analytic, simulated) when the two differ by more than 15%.

    The simulation can only ADD days. A simulated size below the analytic one is
    not evidence that fewer days suffice: for a heavy-tailed member at short
    lengths the replicate's variance estimate is right-skewed, the closed-form
    UCB under-covers, and adopting the smaller figure would plan on an
    anti-conservative test. Both figures and the difference stay in the row.

    A censored threshold (the shortest simulated length already meets 80%, so
    the crossing was never bracketed) is reported but never allowed to override:
    it is an upper bound, and adopting it would claim fewer days than any
    measured crossing supports.
    """
    if simulated is None:
        return analytic, None, [f"power_{tag}_never_reaches_target"]
    diff_pct = 100.0 * (simulated - analytic) / analytic if analytic > 0 else 0.0
    if censored:
        return analytic, diff_pct, [f"sim_censored_below_grid_{tag}"]
    if abs(diff_pct) > 15.0:
        simulated_days = int(math.ceil(simulated))
        if simulated_days > analytic:
            return simulated_days, diff_pct, [f"sim_used_larger_{tag}"]
        return analytic, diff_pct, [f"sim_smaller_ignored_{tag}"]
    return analytic, diff_pct, []


def evaluate_member(
    member: Member, index: int, eps_day: float, supply: dict[str, dict[str, Any]],
    replications: int, grid: tuple[int, ...],
) -> dict[str, Any]:
    n_a = analytic_sample_size(Z_HOLM, member.sd_day, member.vif_boot, eps_day)
    n_b = analytic_sample_size(Z_UCB, member.sd_day, member.vif_boot, eps_day)
    flags = list(member.flags)
    row: dict[str, Any] = {
        "id": member.member_id,
        "class": member.klass,
        "tier": member.tier,
        "kind": member.kind,
        "window_days": member.window_days,
        "r": member.r,
        "sd_day": member.sd_day,
        "lag1": member.lag1,
        "vif_boot": member.vif_boot,
        "cluster_vif": member.cluster_vif,
        "eps_trade": (eps_day / member.r) if member.r > 0 else None,
        "n_a_analytic": n_a,
        "n_b_analytic": n_b,
        "curve": {},
        "n_a_sim": None,
        "n_b_sim": None,
        "diff_a_pct": None,
        "diff_b_pct": None,
        "chosen_a": n_a,
        "chosen_b": n_b,
        "flags": flags,
        "eps_min_at_supplied": _eps_min_table(member, supply),
        "eps_ref_days": _eps_ref_days(member),
        "n_b_sensitivity": _sensitivity(member),
        "spot_check": None,
    }
    if member.kind == "projected":
        return row

    lengths = _simulation_lengths(n_a, n_b, grid)
    curve, source_floored, degenerate = simulate_powers(
        member.centred, eps_day, lengths, SEED_BASE + index, replications
    )
    row["curve"] = {str(n): curve[n] for n in lengths}
    row["sim_source_vif_floored"] = bool(source_floored)
    row["sim_zero_variance_draws"] = degenerate
    if degenerate:
        flags.append("zero_variance_draws")
    powers_a = [curve[n]["power_a"] for n in lengths]
    powers_b = [curve[n]["power_b"] for n in lengths]
    n_a_sim = interpolate_threshold(lengths, powers_a)
    n_b_sim = interpolate_threshold(lengths, powers_b)
    chosen_a, diff_a, flags_a = _chosen(
        n_a, n_a_sim, threshold_is_censored(lengths, powers_a), "a"
    )
    chosen_b, diff_b, flags_b = _chosen(
        n_b, n_b_sim, threshold_is_censored(lengths, powers_b), "b"
    )
    row.update(
        n_a_sim=n_a_sim,
        n_b_sim=n_b_sim,
        diff_a_pct=diff_a,
        diff_b_pct=diff_b,
        chosen_a=chosen_a,
        chosen_b=chosen_b,
    )
    flags.extend(flags_a + flags_b)
    return row


def _evaluate_one(args: tuple[Member, int, float, dict[str, Any], int, tuple[int, ...]]):
    return evaluate_member(*args)


# ------------------------------------------------------------------ classes ----


def _extreme(
    rows: list[dict[str, Any]], start: str, field_name: str, largest: bool
) -> dict[str, Any] | None:
    """The member with the smallest (or largest) eps_min at ``start``."""
    pairs = [
        (row["id"], row["eps_min_at_supplied"][start][field_name])
        for row in rows
        if row["eps_min_at_supplied"][start][field_name] is not None
    ]
    if not pairs:
        return None
    member, value = (max if largest else min)(pairs, key=lambda pair: pair[1])
    return {"member": member, "value": value}


def resolution_range(
    klass_rows: list[dict[str, Any]], supply: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    """Per supplied-days start, the spread of eps_min ACROSS the class.

    Measured members only. A class whose members are all projected (C7, Family
    H) has no measured row, so its projected members are used instead and
    ``basis`` says so; the figures are then projections, not measurements.
    """
    measured = [row for row in klass_rows if row["kind"] != "projected"]
    basis = "measured"
    if not measured:
        measured = list(klass_rows)
        basis = "projected"
    out: dict[str, Any] = {}
    for start in supply:
        out[start] = {
            "basis": basis,
            "members": len(measured),
            "min_per_trade": _extreme(measured, start, "per_trade", largest=False),
            "max_per_trade": _extreme(measured, start, "per_trade", largest=True),
            "min_per_day": _extreme(measured, start, "per_day", largest=False),
            "max_per_day": _extreme(measured, start, "per_day", largest=True),
        }
    return out


def roll_up_classes(
    rows: list[dict[str, Any]], eps_day: float, supply: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    by_class: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_class.setdefault(row["class"], []).append(row)
    out: dict[str, Any] = {}
    for klass in sorted(by_class):
        klass_rows = by_class[klass]
        # Typical r: the median over the class's TRIAL members (C7: over the
        # projected firing fractions, its only members).
        basis = [r["r"] for r in klass_rows if r["kind"] in ("trial", "projected")]
        typical_r = float(np.median(basis)) if basis else float(
            np.median([r["r"] for r in klass_rows])
        )
        eps_trade = eps_day / typical_r if typical_r > 0 else None
        binding_a = max(klass_rows, key=lambda r: r["chosen_a"])
        binding_b = max(klass_rows, key=lambda r: r["chosen_b"])
        supplied = {s: info["confirmation_days"] for s, info in supply.items()}
        out[klass] = {
            "members": [r["id"] for r in klass_rows],
            "typical_r": typical_r,
            "eps_trade": eps_trade,
            "gross_equivalent_trade": (eps_trade + MARKET_COST_TICKS) if eps_trade else None,
            "cost_bar_market_ticks": MARKET_COST_TICKS,
            "cost_bar_passive_ticks": PASSIVE_COST_TICKS,
            "binding_a": {"id": binding_a["id"], "days": binding_a["chosen_a"]},
            "binding_b": {"id": binding_b["id"], "days": binding_b["chosen_b"]},
            "supplied_days": supplied,
            "resolution_range": resolution_range(klass_rows, supply),
            "null_power_achievable_at": {
                s: bool(days >= binding_b["chosen_b"]) for s, days in supplied.items()
            },
        }
    return out


def attach_spot_checks(
    classes: dict[str, Any], rows: dict[str, dict[str, Any]], members: dict[str, Member],
    eps_day: float, replications: int,
) -> None:
    """Percentile-bootstrap check at each class's binding n_b (measured members only).

    Biased upward for autocorrelated members; see ``percentile_ucb_success``.
    """
    order = {row["id"]: i for i, row in enumerate(rows.values())}
    for summary in classes.values():
        member_id = summary["binding_b"]["id"]
        member = members[member_id]
        if member.kind == "projected":
            continue
        n = max(int(summary["binding_b"]["days"]), MIN_SIM_N)
        index = order[member_id]
        curve, _floor, _deg = simulate_powers(
            member.centred, eps_day, [n], SEED_BASE + index, replications
        )
        success = percentile_ucb_success(
            member.centred, n, eps_day, SEED_BASE + SPOT_SEED_OFFSET + index
        )
        rows[member_id]["spot_check"] = {
            "n": n,
            "closed_form_power_b": curve[n]["power_b"],
            "percentile_success": success,
            "replicates": SPOT_REPLICATES,
            "inner_B": SPOT_INNER_B,
            "interpretation": (
                "a check of the closed form against the percentile construction inside the "
                "bootstrap world, biased upward for autocorrelated members by the double "
                "attenuation; not a check of the absolute level"
            ),
        }


# -------------------------------------------------------------------- output ----


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------- main ----


def build_payload(eps_day: float, replications: int, jobs: int, grid: tuple[int, ...]):
    started = time.time()
    coverage_md = COVERAGE_MD.read_text()
    quotes_md = QUOTES_MD.read_text()
    trials = json.loads(TRIALS_JSON.read_text())
    events = json.loads(EVENTS_JSON.read_text())

    class_map = parse_class_map(coverage_md)
    members = build_members(trials, events, class_map)
    measured_ids = {m.member_id for m in members if m.kind != "projected"}
    if measured_ids != set(class_map):
        raise ValueError("coverage.md class map and the input series disagree member for member")

    degraded = parse_degraded_dates(quotes_md)
    supply = {
        start: supplied_days(date.fromisoformat(start), date.fromisoformat(SUPPLY_END), degraded)
        for start in SUPPLY_STARTS
    }
    holdout2 = supplied_days(
        date.fromisoformat(HOLDOUT2_START), date.fromisoformat(HOLDOUT2_END), degraded
    )

    tasks = [(m, i, eps_day, supply, replications, grid) for i, m in enumerate(members)]
    if jobs > 1:
        with ProcessPoolExecutor(max_workers=jobs) as pool:
            rows = list(pool.map(_evaluate_one, tasks))
    else:
        rows = [_evaluate_one(t) for t in tasks]

    by_id = {m.member_id: m for m in members}
    row_by_id = {r["id"]: r for r in rows}
    classes = roll_up_classes(rows, eps_day, supply)
    attach_spot_checks(classes, row_by_id, by_id, eps_day, replications)

    floor_hits = sum(1 for m in members if m.vif_floored)
    notes = [
        f"{DESCRIPTIVE_NOTE}: sections 5a, 5b and 5c, and every eps_min / eps_ref field.",
        "Holm's most stringent step (alpha/58 = Bonferroni) is applied to every member, so "
        "every n_a is an upper bound on what Holm requires.",
        "VIF_boot is the inflation the program's own block-5 stationary bootstrap sees "
        "(Politis-Romano, p = 1/5), not the true long-run variance ratio; for a persistent "
        "series it is the smaller of the two, so the bootstrap under-corrects by design.",
        f"V_B floored at {VIF_FLOOR_FRACTION} x gamma_0 for {floor_hits} of "
        f"{len(members)} members.",
        "Family H (C7) rows are projected from the coverage map's proxy rule, analytic only, "
        "never simulated; their achieved null power is measured in D.1f on the H series.",
        "Phi^-1 comes from statistics.NormalDist().inv_cdf (standard library); scipy is not a "
        "project dependency. The values agree with scipy.stats.norm.ppf to ~1e-15.",
        f"Supplied days are an estimate, {SUPPLY_TOLERANCE}; no exchange calendar file was read.",
        "sim_censored_below_grid_*: the shortest simulated length already reached 80% power, "
        "so the crossing was never bracketed; the figure is reported as an upper bound and "
        "the analytic sample size is kept.",
        "Simulation SE: SE_hat = sqrt(gamma_0_hat(x) * VIF_boot(source) / n), gamma_0_hat(x) "
        "the replicate's own sample variance (ddof = 1). A block-bootstrap replicate's lag-k "
        "autocovariance is already about (1-p)^k times the source's, so a V_B computed from "
        "the replicate attenuates the dependence term twice and understates the SE; measured "
        "on an AR(1) with phi = 0.3 that put simulated power_b at 0.848 instead of 0.80. The "
        "replicate supplies the finite-sample variance noise and the heavy tails; the "
        "dependence factor comes from the source, exactly as the analytic formula uses it "
        "(lead ruling, Stage D.1e Task 3).",
        "UNIT CORRECTION (reports/stage_d1e_adjudication.md, finding R-1): trial series are "
        "read from members_trials.json as daily_net_ticks_per_micro, which divides each round "
        "trip by its OWN contract quantity (trip net / ($1.25 x trip_micros)). The earlier "
        "run divided daily dollars by $2.50, assuming 2 micros for every trial; 29 trials and "
        "C-H4 code 1 micro and D-H2 and RT7 size 1 to 5 by rule, so every trial series was at "
        "half scale, every trial SD was halved and every trial sample size was a quarter of "
        "the right one. Family H per-trade SD proxies were read off the same half-scale table "
        "and are corrected with it: 200 ticks for H1-H5, 230 for H6. Statistic members are "
        "built from tick sums and were never affected.",
        "Chosen figure: where the simulated and analytic sizes differ by more than 15% the "
        "chosen figure is max(analytic, simulated). A simulated size below the analytic one "
        "is not evidence that fewer days suffice: for a heavy-tailed member at short lengths "
        "the replicate's variance estimate is right-skewed, so the closed-form UCB "
        "under-covers there and adopting the smaller figure would plan on an anti-conservative "
        "test. Where the simulation asks for MORE days the simulated figure is used "
        "(sim_used_larger_*); where it asks for fewer it is recorded and ignored "
        "(sim_smaller_ignored_*). Both figures and the difference stay in every row "
        "(lead ruling, Stage D.1e Task 3).",
        "classes[c].resolution_range is descriptive: the spread of eps_min ACROSS a class's "
        "measured members at each supplied-days start, not only at its binding member. C7 has "
        "no measured member, so its range is over the projected Family H rows (basis field).",
        "spot_check.percentile_success is a check of the closed form against the percentile "
        "construction inside the bootstrap world, biased upward for autocorrelated members by "
        "the same double attenuation; it is not a check of the absolute level.",
    ]
    payload = {
        "meta": {
            "generated_utc": datetime.now(UTC).isoformat(),
            "eps_day": eps_day,
            "m": HOLM_FAMILY_SIZE,
            "alpha_holm": ALPHA_HOLM,
            "z_a": Z_HOLM,
            "z_b": Z_POWER,
            "z_95": Z_UCB,
            "mean_block": MEAN_BLOCK,
            "K": MAX_LAG_K,
            "replications": replications,
            "n_grid": list(grid),
            "seed_base": SEED_BASE,
            "eps_sensitivity": list(EPS_SENSITIVITY),
            "eps_ref_per_trade": EPS_REF_PER_TRADE,
            "descriptive_note": DESCRIPTIVE_NOTE,
            "cost_bar_market_ticks": MARKET_COST_TICKS,
            "cost_bar_passive_ticks": PASSIVE_COST_TICKS,
            "source_sha256": {
                "reports/stage_d1e_coverage.md": _sha256(COVERAGE_MD),
                "reports/stage_d1e_members_trials.json": _sha256(TRIALS_JSON),
                "reports/stage_d1e_members_events.json": _sha256(EVENTS_JSON),
                "reports/stage_d1e_quotes.md": _sha256(QUOTES_MD),
            },
            "runtime_seconds": 0.0,
            "floor_hits": floor_hits,
            "notes": notes,
        },
        "members": rows,
        "classes": classes,
        "supplied_days": supply,
        "holdout2_days": holdout2["confirmation_days"],
        "holdout2_detail": holdout2,
    }
    payload["meta"]["runtime_seconds"] = time.time() - started
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--eps-day", type=float, default=DEFAULT_EPS_DAY)
    parser.add_argument("--replications", type=int, default=REPLICATIONS)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--max-grid-n", type=int, default=max(N_GRID))
    args = parser.parse_args(argv)

    grid = tuple(n for n in N_GRID if n <= args.max_grid_n)
    payload = build_payload(args.eps_day, args.replications, args.jobs, grid)
    OUT_JSON.write_text(json.dumps(payload, indent=1) + "\n")
    OUT_MD.write_text(render_markdown(payload))
    print(f"wrote {OUT_JSON} and {OUT_MD} in {payload['meta']['runtime_seconds']:.1f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
