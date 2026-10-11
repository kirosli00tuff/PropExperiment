"""Stage E.19 grid runner (reports/stage_e19_briefs/brief_grid.md; model sim_spec.md section 6).

One job = one Combine attempt pool (one size, shock configuration, edge, f, DLL choice and rule
variant) + its XFA pools (payout paths standard and consistency) + every post hoc rule set on them
(pricing path x Back2Funded; campaigns for the headline band f). Jobs that share shocks (same shock
configuration, size and edge) run together as one task, so the shock sets are built once per task.

Seeds (common random numbers): the shock seed depends only on (phase, size, tail, direction,
products, cost model, mode); the cycle and campaign index-draw seeds only on (size, tail,
direction, products, cost model, mode). Every edge, f, DLL choice, payout path and rule variant of a
size therefore sees the same shocks, and cycles are paired across f and edge.

Wallet (L-12, brief "Wallet accounting"): the API subscription is one per user, paid per started
billing period of operation: ceil(end / period) periods for a cycle that ends at elapsed day
``end``; floor(t / period) + 1 periods for a campaign event at the start of day t. The payout
transfer fee is 0 in the headline (Wise / Aeropay); the ACH / wire fee is a post hoc sensitivity.

CLI: ``python -m prop_econ.grid count`` | ``run --workers N [--job JOB_ID] [--family NAME]``.
Results: one JSON per job in reports/stage_e19_runs/ (written last, atomically; a job is skipped
when its JSON is complete and its settings fingerprint matches).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import multiprocessing as mp
import os
import resource
import sys
import time
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

from prop_econ.assemble import (
    KIND_ACTIVATION,
    KIND_B2F,
    KIND_REBILL,
    KIND_RESET,
    KIND_START,
    PURCHASE_KINDS,
    CycleBatch,
    FeeTerms,
    assemble_cycles,
    billing_period_days,
    campaign_quantiles,
    draw_indices,
    fee_terms,
    run_campaign,
)
from prop_econ.funnel import (
    ATTEMPT_BREACH,
    ATTEMPT_TIMEOUT,
    TRADING_DAYS_PER_YEAR,
    XFA_BREACH,
    XFA_CALLUP,
    XFA_HORIZON,
    XFA_PAYOUT_LIMIT,
    Policy,
    run_attempt,
    run_xfa,
)
from prop_econ.returns import build_shocks, load_paths
from prop_econ.rules import RuleBook, SizeRules, apply_readings, load_rules, size_rules
from prop_econ.types import ShockSet
from prop_econ.vec import AttemptPool, XfaPool, simulate_attempts, simulate_xfas

REPO_ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = REPO_ROOT / "reports" / "stage_e19_rules.json"
RUNS_DIR = REPO_ROOT / "reports" / "stage_e19_runs"
BASE_SEED = 20261019
MAX_WORKERS = 8  # CLAUDE.md: half the cores, never more than 8

SIZES = ("50K", "100K", "150K")
PAYOUT_PATHS = ("standard", "consistency")
PRICING_PATHS = ("standard", "no_activation_fee")
F_BAND = (0.05, 0.10, 0.15, 0.20, 0.25)
F_DIAG = (0.35, 0.50)
F_ALL = F_BAND + F_DIAG
SHARPES = (0.0, 0.15, 0.3, 0.5, 0.75, 1.0)
ZERO_EDGES = ("zero_k1", "zero_k3")
EDGES = ZERO_EDGES + tuple(f"S{s:g}" for s in SHARPES)
PRODUCTS = ("NQ", "CL", "GC", "ZN", "6E")
VARIANTS = ("base", "keepd0.5", "callup1", "callup3", "scaling_upper", "ccons_inclusive")
FEE_KINDS = {"start": KIND_START, "rebill": KIND_REBILL, "reset": KIND_RESET,
             "activation": KIND_ACTIVATION, "back2funded": KIND_B2F}
XFA_REASONS = {"breach": XFA_BREACH, "callup": XFA_CALLUP, "payout_limit": XFA_PAYOUT_LIMIT,
               "horizon": XFA_HORIZON}


# ------------------------------------------------------------------------ configuration ----
@dataclass(frozen=True)
class ShockConfig:
    tail: str = "bootstrap"
    direction: str = "random"
    products: str = "all"
    cost: str = "d8"
    mode: str = "continuous"

    @property
    def id(self) -> str:
        return f"{self.tail}-{self.direction}-{self.products}-{self.cost}-{self.mode}"


HEADLINE = ShockConfig()


@dataclass(frozen=True)
class Job:
    sc: ShockConfig
    size: str
    edge: str
    f: float
    dll: bool
    variant: str
    family: str  # headline or the sensitivity family that put the job in the grid

    @property
    def id(self) -> str:
        return (f"{self.sc.id}__{self.size}__{self.edge}__f{self.f:.2f}__dll{int(self.dll)}"
                f"__{self.variant}")

    @property
    def is_headline(self) -> bool:
        return self.sc == HEADLINE and self.variant == "base"

    @property
    def f_label(self) -> str:
        return "band" if self.f in F_BAND else "diagnostic (outside the policy band)"

    @property
    def b2f_set(self) -> tuple[bool, ...]:
        return (False, True) if self.is_headline else (False,)

    @property
    def campaigns(self) -> bool:
        return self.is_headline and self.f in F_BAND

    @property
    def task_key(self) -> tuple[ShockConfig, str, str]:
        return (self.sc, self.size, self.edge)


@dataclass(frozen=True)
class Settings:
    n_paths: int = 20_000
    horizon: int = 756
    max_payouts: int = 192
    attempt_cap: int = 60
    n_cycles: int = 20_000
    n_reps: int = 20_000
    purchase_cap: int = 400
    targets: tuple[float, ...] = (5000.0, 10000.0)
    slots: tuple[int, ...] = (1, 5)
    trace_rows: int = 200  # rows per phase replayed by the scalar reference for the cost mix
    base_seed: int = BASE_SEED

    def fingerprint(self, rules_path: Path = RULES_PATH) -> str:
        h = hashlib.sha256(json.dumps(asdict(self), sort_keys=True).encode())
        h.update(Path(rules_path).read_bytes())
        return h.hexdigest()[:16]


def edge_policy_fields(edge: str) -> dict[str, Any]:
    if edge in ZERO_EDGES:
        return {"edge": "zero", "sharpe": 0.0, "k": int(edge[-1])}
    if edge.startswith("S"):
        return {"edge": "sharpe", "sharpe": float(edge[1:]), "k": 1}  # L-17: k = 1 at a Sharpe edge
    raise ValueError(f"unknown edge {edge!r}")


def _jobs(sc: ShockConfig, edges: Iterable[str], fs: Iterable[float], dlls: Iterable[bool],
          variant: str, family: str, sizes: Iterable[str] = SIZES) -> list[Job]:
    return [Job(sc, size, e, f, d, variant, family)
            for size in sizes for e in edges for f in fs for d in dlls]


def enumerate_jobs() -> list[Job]:
    """The full grid of the brief: headline, then every sensitivity family."""
    off = (False,)
    jobs = _jobs(HEADLINE, EDGES, F_ALL, (False, True), "base", "headline")
    jobs += _jobs(ShockConfig(tail="normal"), EDGES, F_BAND, off, "base", "tail_normal")
    jobs += _jobs(ShockConfig(direction="long"), ("zero_k1",), F_BAND, off, "base",
                  "direction_long")
    jobs += _jobs(ShockConfig(cost="wall"), ZERO_EDGES, F_BAND, off, "base", "cost_wall")
    for p in PRODUCTS:
        jobs += _jobs(ShockConfig(products=p, mode="integer"), ("zero_k1", "S0.5"), F_BAND, off,
                      "base", f"integer_{p}")
    jobs += _jobs(HEADLINE, ("zero_k1", "S0.5", "S1"), F_BAND, off, "keepd0.5", "keep_d")
    for v in ("callup1", "callup3"):
        jobs += _jobs(HEADLINE, ("zero_k1", "S0.5"), F_BAND, off, v, v)
    for v in ("scaling_upper", "ccons_inclusive"):
        jobs += _jobs(HEADLINE, ("zero_k1", "S0.5"), (0.10, 0.25), off, v, v)
    ids = [j.id for j in jobs]
    if len(set(ids)) != len(ids):
        raise AssertionError("duplicate job ids")
    return jobs


def group_tasks(jobs: Sequence[Job]) -> list[list[Job]]:
    """Jobs sharing (shock configuration, size, edge); campaign-heavy tasks first."""
    groups: dict[tuple, list[Job]] = {}
    for j in jobs:
        groups.setdefault(j.task_key, []).append(j)
    return sorted(groups.values(), key=lambda g: -sum(30 if j.campaigns else 1 for j in g))


# -------------------------------------------------------------------------------- seeds ----
def derive_seed(*parts: Any) -> int:
    return int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:16], 16)


def shock_seed(settings: Settings, phase: str, size: str, sc: ShockConfig) -> int:
    return derive_seed(settings.base_seed, "shock", phase, size, sc.tail, sc.direction,
                       sc.products, sc.cost, sc.mode)


def draw_seed(settings: Settings, kind: str, size: str, sc: ShockConfig) -> int:
    """kind 'cycle' or 'campaign'."""
    return derive_seed(settings.base_seed, kind, size, sc.tail, sc.direction, sc.products,
                       sc.cost, sc.mode)


# -------------------------------------------------------------------------------- rules ----
def headline_book(path: Path = RULES_PATH) -> RuleBook:
    """The FINAL rules file with every multi-reading rule at readings[0]."""
    book = load_rules(path)
    if book.status != "FINAL":
        raise ValueError(f"{path}: status {book.status}, the grid needs FINAL")
    alts = book.alternative_readings()
    return apply_readings(book, {p: r[0] for p, r in alts.items()}) if alts else book


def variant_book(book: RuleBook, variant: str, size: str) -> RuleBook:
    if variant in ("base", "keepd0.5"):
        return book
    if variant in ("callup1", "callup3"):
        return apply_readings(book, {"global.callup.type": "after_n_payouts",
                                     "global.callup.n": int(variant[-1])}, allow_unlisted=True)
    if variant == "scaling_upper":
        return apply_readings(book, {f"sizes.{size}.xfa.scaling_boundary": "upper"})
    if variant == "ccons_inclusive":
        return apply_readings(book, {"global.combine_consistency_inclusive": True})
    raise ValueError(f"unknown variant {variant!r}")


def job_policy(job: Job, path: str, settings: Settings) -> Policy:
    return Policy(f=job.f, mode=job.sc.mode, dll_chosen=job.dll, payout_path=path,
                  keep_d=0.5 if job.variant == "keepd0.5" else 0.0,
                  attempt_max_days=settings.horizon, xfa_max_days=settings.horizon,
                  max_payouts=settings.max_payouts, **edge_policy_fields(job.edge))


@dataclass(frozen=True)
class Wallet:
    """Post hoc cash items read from the rules file (none hard-coded)."""

    api_usd: float
    period_days: int
    payout_fee_usd: float  # ACH / wire, the sensitivity (headline 0)
    split: float
    close_frac: float
    close_cap_usd: float
    start_balance: float
    copies: int  # copy-traded accounts (global.max_active_xfas)


def wallet_from(book: RuleBook, rules: SizeRules) -> Wallet:
    v = book.value
    return Wallet(api_usd=float(v("global.api_access_monthly_usd")),
                  period_days=billing_period_days(rules.glob.billing_period_calendar_days),
                  payout_fee_usd=float(v("global.payout_fee_usd.ach")),
                  split=rules.glob.profit_split_trader,
                  close_frac=float(v("global.xfa_voluntary_close_payout_frac")),
                  close_cap_usd=float(v("global.xfa_voluntary_close_payout_cap_usd")),
                  start_balance=rules.xfa.start_balance_usd,
                  copies=int(rules.glob.max_active_xfas))


def api_periods_cycle(end: np.ndarray, period: int) -> np.ndarray:
    """Started billing periods of a cycle that operated days 0 .. end - 1."""
    return -(-np.asarray(end, dtype=np.int64) // period)


def api_periods_at(t: np.ndarray, period: int) -> np.ndarray:
    """Started billing periods by an event at the start of day t (day t is in operation)."""
    return np.asarray(t, dtype=np.int64) // period + 1


# ------------------------------------------------------------------------------ metrics ----
def _num(x: Any) -> Any:
    """JSON-safe number: non-finite -> None."""
    if x is None:
        return None
    x = float(x)
    return x if math.isfinite(x) else None


def _mean_se(x: np.ndarray) -> dict[str, Any]:
    n = x.size
    se = float(np.std(x, ddof=1) / math.sqrt(n)) if n > 1 else None
    return {"mean": _num(np.mean(x)), "se": _num(se)}


def attempt_metrics(pool: AttemptPool) -> dict[str, Any]:
    p = float(pool.passed.mean())
    return {"p_pass": p, "mean_length": float(pool.length.mean()),
            "timeout_share": float((pool.reason == ATTEMPT_TIMEOUT).mean()),
            "attempts_per_pass": _num(1.0 / p) if p > 0 else None}


def xfa_metrics(pool: XfaPool, split: float) -> dict[str, Any]:
    has = pool.n_payouts > 0
    out = {"p_any_payout": float(has.mean()),
           "mean_user_cash": float(split * pool.total_gross.mean()),
           "mean_n_payouts": float(pool.n_payouts.mean()),
           "mean_days_to_first_payout": _num(pool.first_payout_day[has].mean()) if has.any()
           else None,
           "alive_at_horizon": float((pool.end_reason == XFA_HORIZON).mean()),
           "overflow_count": int(pool.overflow.sum()),
           "mean_life_days": float(pool.end_day.mean())}
    for name, code in XFA_REASONS.items():
        out[f"end_{name}"] = float((pool.end_reason == code).mean())
    return out


def cycle_post_hoc(batch: CycleBatch, pool: XfaPool, wallet: Wallet) -> dict[str, np.ndarray]:
    """Per-cycle cash items applied after assembly (L-12, L-15, brief 'Post hoc')."""
    rows = batch.xfa_row
    used = rows >= 0
    r = np.where(used, rows, 0)
    n_pay = np.where(used, pool.n_payouts[r], 0).sum(axis=1)
    alive = used & (pool.end_reason[r] == XFA_HORIZON)
    bal = np.maximum(pool.end_balance[r] - wallet.start_balance, 0.0)
    close = np.where(alive, wallet.split * np.minimum(wallet.close_frac * bal,
                                                      wallet.close_cap_usd), 0.0).sum(axis=1)
    api = wallet.api_usd * api_periods_cycle(batch.end, wallet.period_days)
    return {"api": api, "n_payouts": n_pay, "payout_fee": wallet.payout_fee_usd * n_pay,
            "close_value": close}


def first_cash_time(batch: CycleBatch) -> np.ndarray:
    """Per cycle: time of the first user cash event, -1 when none (events sorted by cycle, time)."""
    out = np.full(batch.n, -1, dtype=np.int64)
    if batch.cash_cycle.size:
        first = np.flatnonzero(np.r_[True, batch.cash_cycle[1:] != batch.cash_cycle[:-1]])
        out[batch.cash_cycle[first]] = batch.cash_time[first]
    return out


CHURN_WINDOW_DAYS = 252  # first trading year of a slot chained from consecutive cycles


def slot_window_purchases(batch: CycleBatch, window: int = CHURN_WINDOW_DAYS) -> np.ndarray:
    """Combine purchases in the first ``window`` trading days of one slot running cycles back to
    back, per slot; slots are formed from consecutive cycles of the batch (i.i.d. draws), and
    the last slot is dropped when its cycles do not cover the window."""
    ends = batch.end.astype(np.int64)
    offset = np.zeros(batch.n, dtype=np.int64)
    slot = np.zeros(batch.n, dtype=np.int64)
    s = cum = 0
    for i, e in enumerate(ends.tolist()):
        if cum >= window:
            s, cum = s + 1, 0
        offset[i], slot[i] = cum, s
        cum += e
    n_slots = s + 1 if cum >= window else s
    is_p = np.isin(batch.fee_kind, PURCHASE_KINDS)
    t = batch.fee_time + offset[batch.fee_cycle]
    m = is_p & (t < window)
    counts = np.bincount(slot[batch.fee_cycle[m]], minlength=s + 1)
    return counts[:n_slots]


def churn_metrics(batch: CycleBatch, pool: XfaPool, apool: AttemptPool, att_idx: np.ndarray
                  ) -> dict[str, Any]:
    """Lead RR-1 / L-19 inputs. Combine-phase days per cycle = the time the subscription ends
    (activation day after a pass, else the end of the last attempt) = the sum of the attempts'
    lengths, since a reset starts the next attempt the next trading day (no gap days)."""
    cap = att_idx.shape[1]
    used_att = np.arange(cap)[None, :] < batch.n_attempts[:, None]
    combine_breaches = ((apool.reason[att_idx] == ATTEMPT_BREACH) & used_att).sum(axis=1)
    combine_days = np.where(batch.passed, batch.xfa_start[:, 0], batch.end)
    used = batch.xfa_row >= 0
    r = np.where(used, batch.xfa_row, 0)
    xfa_days = np.where(used, batch.xfa_end - batch.xfa_start, 0).sum(axis=1)
    xfa_breaches = (used & (pool.end_reason[r] == XFA_BREACH)).sum(axis=1)
    win = slot_window_purchases(batch)
    return {"combine_days_mean": float(combine_days.mean()),
            "combine_breaches_mean": float(combine_breaches.mean()),
            "xfa_days_mean": float(xfa_days.mean()),
            "xfa_breaches_mean": float(xfa_breaches.mean()),
            "slot_first252_purchases_mean": _num(win.mean()) if win.size else None,
            "slot_first252_n_slots": int(win.size)}


def cycle_metrics(batch: CycleBatch, pool: XfaPool, wallet: Wallet, apool: AttemptPool,
                  att_idx: np.ndarray) -> tuple[dict[str, Any], np.ndarray]:
    """Cycle record (API fee included unless named ex_api) and the per-cycle net incl. API."""
    n = batch.n
    ph = cycle_post_hoc(batch, pool, wallet)
    net_ex = batch.net
    net = net_ex - ph["api"]
    by_kind = np.bincount(batch.fee_kind, weights=batch.fee_usd, minlength=5) / n
    fees = {name: float(by_kind[k]) for name, k in FEE_KINDS.items()}
    fees["api"] = float(ph["api"].mean())
    first = first_cash_time(batch)
    got = first >= 0
    purchases = float(batch.purchases.mean())
    q = np.quantile(net, (0.05, 0.5, 0.95))
    rec = {
        "net": _mean_se(net), "net_ex_api": _mean_se(net_ex),
        "net_p5": float(q[0]), "net_p50": float(q[1]), "net_p95": float(q[2]),
        "p_no_payout": float((~got).mean()), "p_reaches_xfa": float(batch.passed.mean()),
        "mean_purchases": purchases, "mean_fees_total": float(batch.fees_total.mean())
        + fees["api"], "mean_fees_by_type": fees,
        "net_per_purchase": _num(net.mean() / purchases) if purchases > 0 else None,
        "mean_days_to_first_payout": _num(first[got].mean()) if got.any() else None,
        "mean_cycle_days": float(batch.end.mean()), "mean_attempts": float(
            batch.n_attempts.mean()), "mean_xfas": float(batch.n_xfas.mean()),
        "overflow_xfas": int(batch.overflow_xfas.sum()),
        "mean_user_cash": float(batch.cash_total.mean()),
        "churn": churn_metrics(batch, pool, apool, att_idx),
        "post_hoc": {
            "payout_fee_ach": _mean_se(net - ph["payout_fee"]),
            "voluntary_close": _mean_se(net + ph["close_value"]),
            "copy_traded": _mean_se(wallet.copies * net_ex - ph["api"]),
        },
    }
    return rec, net


def campaign_metrics(result: Any, wallet: Wallet, probs: Sequence[float] = (0.5, 0.8)
                     ) -> dict[str, Any]:
    """P50 / P80 (the K reached with that probability; None when the share reached is lower)."""
    base = campaign_quantiles(result, probs)
    out: dict[str, Any] = {"cycles_drawn": int(result.cycles_drawn),
                           "overflow_xfas": int(result.overflow_xfas)}
    for ti, target in enumerate(result.targets):
        reached = result.reached[ti]
        days = result.days[ti]
        api = wallet.api_usd * api_periods_at(np.where(reached, days, 0), wallet.period_days)
        fees_api = np.where(reached, result.fees[ti] + api, np.inf)
        row = {"share_not_reached": float(1.0 - reached.mean())}
        ok = reached & (days > 0)
        row["purchases_per_21d_reached_mean"] = _num(np.mean(
            21.0 * result.purchases[ti][ok] / days[ok])) if ok.any() else None
        for p in probs:
            tag = f"p{round(p * 100)}"
            row[f"purchases_{tag}"] = _num(base[target][f"purchases_{tag}"])
            row[f"days_{tag}"] = _num(base[target][f"days_{tag}"])
            row[f"fees_ex_api_{tag}"] = _num(base[target][f"fees_{tag}"])
            row[f"fees_{tag}"] = _num(np.quantile(fees_api, p, method="inverted_cdf"))
        out[f"{target:g}"] = row
    return out


# ----------------------------------------------------------------- effective net Sharpe ----
def _cost_mix_rows(shocks: ShockSet, outcomes: Iterable[Any], rows: Iterable[int], k: int,
                   acc: dict[str, float]) -> None:
    for row, out in zip(rows, outcomes, strict=True):
        for log in out.days:
            spec = shocks.products[int(shocks.prod[row, log.day])]
            sigma = spec.sigma_full_usd if log.full_size else spec.sigma_micro_usd
            rt = spec.rt_full_usd if log.full_size else spec.rt_micro_usd
            acc["risk"] += log.contracts * sigma
            acc["cost"] += log.contracts * k * rt
            acc["ratio"] += k * rt / sigma
            acc["days"] += 1
            acc["full_days"] += int(log.full_size)


def cost_mix(shocks: ShockSet, phase: str, rules: SizeRules, policy: Policy, n_rows: int
             ) -> dict[str, float]:
    """Traded vehicle mix of the first n_rows rows, replayed by the scalar reference."""
    rows = range(min(n_rows, shocks.n_paths))
    run = run_attempt if phase == "attempt" else run_xfa
    acc = {"risk": 0.0, "cost": 0.0, "ratio": 0.0, "days": 0, "full_days": 0}
    _cost_mix_rows(shocks, (run(shocks, r, rules, policy, trace=True) for r in rows), rows,
                   policy.k, acc)
    return acc


def effective_sharpe(mixes: Sequence[dict[str, float]]) -> dict[str, Any]:
    """Net Sharpe of the zero edge: -sqrt(252) x cost / risk, risk-weighted (expected cost per
    dollar of daily sd actually traded) and day-weighted (mean of k x rt_u / sigma_u)."""
    tot = {key: sum(m[key] for m in mixes) for key in ("risk", "cost", "ratio", "days",
                                                       "full_days")}
    root = math.sqrt(TRADING_DAYS_PER_YEAR)
    if tot["days"] == 0:
        return {"risk_weighted": None, "day_weighted": None, "days": 0, "full_share": None}
    return {"risk_weighted": -root * tot["cost"] / tot["risk"],
            "day_weighted": -root * tot["ratio"] / tot["days"], "days": int(tot["days"]),
            "full_share": tot["full_days"] / tot["days"]}


# ------------------------------------------------------------------------------ running ----
_PATHS: tuple | None = None


def _paths() -> tuple:
    global _PATHS
    if _PATHS is None:
        _PATHS = load_paths()
    return _PATHS


@dataclass(frozen=True)
class _N:
    n: int


def job_files(out_dir: Path, job: Job) -> tuple[Path, Path]:
    return out_dir / f"{job.id}.json", out_dir / f"{job.id}.npz"


def is_complete(out_dir: Path, job: Job, fingerprint: str) -> bool:
    js, npz = job_files(out_dir, job)
    if not js.exists() or (job.is_headline and not npz.exists()):
        return False
    try:
        doc = json.loads(js.read_text())
    except (OSError, json.JSONDecodeError):
        return False
    return bool(doc.get("complete")) and doc.get("fingerprint") == fingerprint \
        and doc.get("job_id") == job.id


def _write_atomic(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text)
    os.replace(tmp, path)


def _save_nets(path: Path, nets: dict[str, np.ndarray]) -> None:
    tmp = path.with_name(path.stem + ".tmp.npz")
    np.savez_compressed(tmp, **nets)
    os.replace(tmp, path)


@dataclass
class _TaskContext:
    settings: Settings
    book: RuleBook
    shocks_x: ShockSet
    att_idx: np.ndarray
    xfa_idx: np.ndarray
    campaign_seed: int


def _attempt_pools(jobs: Sequence[Job], ctx_book: RuleBook, settings: Settings
                   ) -> tuple[dict[tuple, AttemptPool], dict[tuple, dict[str, float]]]:
    """Attempt pools (and zero-edge cost mixes) per (f, dll, combine-relevant variant)."""
    sc, size = jobs[0].sc, jobs[0].size
    shocks = build_shocks(settings.n_paths, settings.horizon,
                          shock_seed(settings, "attempt", size, sc), sc.tail, sc.direction,
                          sc.products, sc.cost, paths=_paths())
    pools, mixes = {}, {}
    for j in jobs:
        key = (j.f, j.dll, j.variant == "ccons_inclusive")
        if key in pools:
            continue
        rules = size_rules(variant_book(ctx_book, j.variant, size), size)
        pol = job_policy(j, "standard", settings)
        pools[key] = simulate_attempts(shocks, rules, pol)
        if j.edge in ZERO_EDGES:
            mixes[key] = cost_mix(shocks, "attempt", rules, pol, settings.trace_rows)
    return pools, mixes


def run_job(job: Job, apool: AttemptPool, att_mix: dict | None, ctx: _TaskContext
            ) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    s = ctx.settings
    book = variant_book(ctx.book, job.variant, job.size)
    rules = size_rules(book, job.size)
    wallet = wallet_from(book, rules)
    doc: dict[str, Any] = {"attempts": attempt_metrics(apool), "xfa": {}, "records": []}
    nets: dict[str, np.ndarray] = {}
    xfa_mix = None
    for path in PAYOUT_PATHS:
        pol = job_policy(job, path, s)
        pool = simulate_xfas(ctx.shocks_x, rules, pol)
        xm = xfa_metrics(pool, wallet.split)
        doc["xfa"][path] = xm
        if job.edge in ZERO_EDGES and path == "standard":
            xfa_mix = cost_mix(ctx.shocks_x, "xfa", rules, pol, s.trace_rows)
        for pricing in PRICING_PATHS:
            for b2f in job.b2f_set:
                terms = fee_terms(rules, pricing_path=pricing, dll_chosen=job.dll, b2f_on=b2f,
                                  attempt_cap=s.attempt_cap)
                batch = assemble_cycles(ctx.att_idx, ctx.xfa_idx, apool, pool, terms)
                rec, net = cycle_metrics(batch, pool, wallet, apool, ctx.att_idx)
                rec = {"path": path, "pricing": pricing, "b2f": b2f, **rec,
                       "per_funded_xfa": xm["mean_user_cash"] - terms.activation_usd}
                if job.is_headline and not b2f:
                    nets[f"{path}|{pricing}"] = net
                if job.campaigns and not b2f:
                    rec["campaigns"] = _campaigns(apool, pool, terms, rules, wallet, ctx)
                doc["records"].append(rec)
    if job.edge in ZERO_EDGES:
        doc["eff_sharpe"] = {"attempt": effective_sharpe([att_mix]),
                             "xfa": effective_sharpe([xfa_mix]),
                             "pooled": effective_sharpe([att_mix, xfa_mix])}
    return doc, nets


def _campaigns(apool: AttemptPool, pool: XfaPool, terms: FeeTerms, rules: SizeRules,
               wallet: Wallet, ctx: _TaskContext) -> dict[str, Any]:
    s = ctx.settings
    out = {}
    for slots in s.slots:
        res = run_campaign(apool, pool, terms, slots=slots,
                           max_active_xfas=rules.glob.max_active_xfas, n_reps=s.n_reps,
                           seed=ctx.campaign_seed, targets=s.targets,
                           purchase_cap=s.purchase_cap)
        out[f"slots{slots}"] = campaign_metrics(res, wallet)
    return out


def run_task(jobs: Sequence[Job], settings: Settings, out_dir: Path,
             rules_path: Path = RULES_PATH) -> list[tuple[str, float]]:
    """Run the pending jobs of one task (same shock configuration, size and edge)."""
    if len({j.task_key for j in jobs}) != 1:
        raise ValueError("a task's jobs must share (shock configuration, size, edge)")
    fp = settings.fingerprint(rules_path)
    pending = [j for j in jobs if not is_complete(out_dir, j, fp)]
    if not pending:
        return []
    out_dir.mkdir(parents=True, exist_ok=True)
    book = headline_book(rules_path)
    sc, size = pending[0].sc, pending[0].size
    apools, amixes = _attempt_pools(pending, book, settings)
    shocks_x = build_shocks(settings.n_paths, settings.horizon,
                            shock_seed(settings, "xfa", size, sc), sc.tail, sc.direction,
                            sc.products, sc.cost, paths=_paths())
    base_terms = fee_terms(size_rules(book, size), pricing_path="standard", dll_chosen=False,
                           b2f_on=False, attempt_cap=settings.attempt_cap)
    rng = np.random.Generator(np.random.PCG64(draw_seed(settings, "cycle", size, sc)))
    att_idx, xfa_idx = draw_indices(rng, settings.n_cycles, _N(settings.n_paths),
                                    _N(settings.n_paths), base_terms)
    ctx = _TaskContext(settings, book, shocks_x, att_idx, xfa_idx,
                       draw_seed(settings, "campaign", size, sc))
    done = []
    for j in pending:
        t0 = time.time()
        key = (j.f, j.dll, j.variant == "ccons_inclusive")
        doc, nets = run_job(j, apools[key], amixes.get(key), ctx)
        js, npz = job_files(out_dir, j)
        if nets:
            _save_nets(npz, nets)
        meta = {"job_id": j.id, "fingerprint": fp, "job": _job_dict(j),
                "seeds": {"attempt_shock": shock_seed(settings, "attempt", size, sc),
                          "xfa_shock": shock_seed(settings, "xfa", size, sc),
                          "cycle": draw_seed(settings, "cycle", size, sc),
                          "campaign": ctx.campaign_seed},
                "settings": asdict(settings), "seconds": round(time.time() - t0, 2),
                "maxrss_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024}
        _write_atomic(js, json.dumps({**meta, **doc, "complete": True}, allow_nan=False))
        done.append((j.id, time.time() - t0))
    return done


def _job_dict(j: Job) -> dict[str, Any]:
    return {"sc": asdict(j.sc), "sc_id": j.sc.id, "size": j.size, "edge": j.edge, "f": j.f,
            "f_label": j.f_label, "dll": j.dll, "variant": j.variant, "family": j.family,
            "headline": j.is_headline}


# ---------------------------------------------------------------------------------- CLI ----
def _worker_init() -> None:
    os.environ.setdefault("OMP_NUM_THREADS", "1")


def _task_entry(args: tuple[list[Job], Settings, str]) -> tuple[str, int, float, str]:
    jobs, settings, out_dir = args
    t0 = time.time()
    try:
        done = run_task(jobs, settings, Path(out_dir))
    except Exception as exc:  # reported in the log; the task's jobs stay pending
        return (_task_name(jobs), 0, time.time() - t0, f"FAILED {type(exc).__name__}: {exc}")
    return (_task_name(jobs), len(done), time.time() - t0, "ok")


def _task_name(jobs: Sequence[Job]) -> str:
    sc, size, edge = jobs[0].task_key
    return f"{sc.id}/{size}/{edge} ({len(jobs)} jobs)"


def _stamp() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S %Z")


def run_grid(workers: int, jobs: Sequence[Job], settings: Settings, out_dir: Path) -> int:
    workers = max(1, min(workers, MAX_WORKERS, max(1, (os.cpu_count() or 2) // 2)))
    fp = settings.fingerprint()
    pending = [j for j in jobs if not is_complete(out_dir, j, fp)]
    tasks = group_tasks(pending)
    print(f"{_stamp()} grid: {len(jobs)} jobs, {len(jobs) - len(pending)} complete, "
          f"{len(pending)} pending in {len(tasks)} tasks; workers {workers}; fingerprint {fp}",
          flush=True)
    t0, n_done, failures = time.time(), 0, 0
    args = [(t, settings, str(out_dir)) for t in tasks]
    ctx = mp.get_context("fork")
    with ctx.Pool(workers, initializer=_worker_init, maxtasksperchild=4) as pool:
        for i, (name, n, secs, status) in enumerate(pool.imap_unordered(_task_entry, args), 1):
            n_done += n
            failures += status != "ok"
            el = time.time() - t0
            eta = el / max(n_done, 1) * (len(pending) - n_done)
            print(f"{_stamp()} task {i}/{len(tasks)} {name}: {n} jobs in {secs:.0f} s, {status}; "
                  f"jobs {n_done}/{len(pending)}; elapsed {el / 60:.1f} min; "
                  f"ETA {eta / 60:.1f} min", flush=True)
    print(f"{_stamp()} grid finished: {n_done} jobs run, {failures} failed tasks, "
          f"{(time.time() - t0) / 60:.1f} min", flush=True)
    return 1 if failures else 0


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m prop_econ.grid")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("count")
    rp = sub.add_parser("run")
    rp.add_argument("--workers", type=int, default=1)
    rp.add_argument("--job", action="append", default=[], help="run only these job ids")
    rp.add_argument("--family", action="append", default=[], help="run only these families")
    a = ap.parse_args(argv)
    jobs = enumerate_jobs()
    if a.cmd == "count":
        fams: dict[str, int] = {}
        for j in jobs:
            fams[j.family] = fams.get(j.family, 0) + 1
        print(json.dumps({"jobs": len(jobs), "tasks": len(group_tasks(jobs)),
                          "campaign_jobs": sum(j.campaigns for j in jobs), "families": fams}))
        return 0
    os.nice(10)
    if a.job:
        jobs = [j for j in jobs if j.id in set(a.job)]
    if a.family:
        jobs = [j for j in jobs if j.family in set(a.family)]
    if not jobs:
        print("no jobs selected", file=sys.stderr)
        return 2
    return run_grid(a.workers, jobs, Settings(), RUNS_DIR)


if __name__ == "__main__":
    sys.exit(main())
