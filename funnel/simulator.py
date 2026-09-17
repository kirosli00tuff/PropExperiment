"""Monte Carlo funnel: Combine -> XFA -> payouts, driven by a daily P&L generator (Stage B, Task 3).

Every rule decision goes through ``rules/xfa_rules.py`` (MLL real-time and EOD
checks, Combine pass with the raised target, Scaling Plan, payout eligibility,
the post-payout MLL reset). Every round turn pays commission and slippage from
``sim.fill_model``, the same cost arithmetic the backtest engine uses. Nothing
here re-implements a rule.

Lifecycle of one run (``horizon_days`` trading days; 21 trading days = 1 month):
- The trader runs ONE Combine at a time. A pass activates one XFA; a breach
  ends that attempt, and a new attempt starts the next day (a reset, billed as
  a new subscription month). No new Combine starts while 5 XFAs are active.
- Up to ``max_xfa_accounts`` (5) XFAs trade at once. With ``correlated=True``
  (the realistic case) every live account, the Combine included, trades the
  SAME market day from ONE generator draw, so a bad sequence hits every MLL
  together. ``correlated=False`` gives each account its own independent draws.
  It exists only as the counterfactual that measures what the correlation costs.
- Each account sizes ``micros_per_trade``, capped by the Scaling Plan
  (``max_position_micros`` on the prior session's balance).
- Per segment (round turn): entry cost booked, then the real-time MLL check at
  the segment's worst excursion, then exit P&L minus exit cost booked.
- Payout policy (stated, greedy): after each XFA close, request
  min(path cap, 50% of balance) whenever that is at least $125. The rules engine
  decides eligibility. A refused request changes nothing and is retried the next
  day.

Not modelled (stated in the report): the gap between a Combine pass and XFA
activation, the profit split (payouts are GROSS), LFA call-up (terminal and out of
scope per docs/DECISIONS.md), inactivity rules, taxes.
"""

from __future__ import annotations

from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import NamedTuple, Protocol

import numpy as np

from funnel.null_generator import DayDraws
from rules.xfa_rules import (
    XFA_50K,
    AccountState,
    PayoutPath,
    Status,
    apply_realtime_mll,
    close_trading_day,
    max_position_micros,
    new_combine_account,
    new_xfa_account,
    process_payout,
    record_realized_pnl,
)
from sim.costs import SlippageTable, load_slippage_table
from sim.fill_model import MES_TICK_VALUE_CENTS, side_cost_at_ct_minute

TRADING_DAYS_PER_MONTH = 21
DAY0 = date(2000, 1, 3)  # label only: DayRecords need a date, the rules never read the calendar
BPS = 10_000


class DayGenerator(Protocol):
    def draw(self, rng: np.random.Generator, n_days: int) -> DayDraws: ...


@dataclass(frozen=True)
class FeeSchedule:
    """Topstep 50K, 'Standard' plan. Help center figures read 2026-09-16 (progress.md, Stage A.1);
    they must be reconfirmed at checkout in Stage A.2."""

    combine_monthly_cents: int = 4_900
    xfa_activation_cents: int = 14_900
    api_monthly_cents: int = 1_450  # $29/mo with the 'topstep' code

    def as_dict(self) -> dict[str, int]:
        return {
            "combine_monthly_cents": self.combine_monthly_cents,
            "xfa_activation_cents": self.xfa_activation_cents,
            "api_monthly_cents": self.api_monthly_cents,
        }


@dataclass(frozen=True)
class FunnelConfig:
    path: PayoutPath
    micros_per_trade: int
    horizon_days: int = 12 * TRADING_DAYS_PER_MONTH
    max_xfa_accounts: int = 5
    correlated: bool = True
    fees: FeeSchedule = field(default_factory=FeeSchedule)
    slippage_statistic: str = "mean"

    def __post_init__(self) -> None:
        if self.micros_per_trade < 1 or self.horizon_days < 1 or self.max_xfa_accounts < 1:
            raise ValueError("micros_per_trade, horizon_days and max_xfa_accounts must be >= 1")


class CostBook:
    """Memoized one-side cost in cents for (CT minute, size)."""

    def __init__(self, table: SlippageTable, statistic: str) -> None:
        self._table = table
        self._statistic = statistic
        self._cache: dict[tuple[int, int], int] = {}

    def side_cents(self, minute_ct: int, micros: int) -> int:
        key = (minute_ct, micros)
        cost = self._cache.get(key)
        if cost is None:
            cost = side_cost_at_ct_minute(self._table, minute_ct, micros, self._statistic)
            cost = cost.total_cents
            self._cache[key] = cost
        return cost


class _Stream(NamedTuple):
    """One draw of ``horizon_days`` as plain lists (fast scalar indexing)."""

    pnl: list[list[float]]
    adverse: list[list[float]]
    entry_minute: list[list[int]]
    exit_minute: list[list[int]]

    @classmethod
    def of(cls, draws: DayDraws) -> _Stream:
        return cls(draws.pnl_ticks.tolist(), draws.adverse_ticks.tolist(),
                   draws.entry_minute_ct.tolist(), draws.exit_minute_ct.tolist())


class _Xfa(NamedTuple):
    account_id: int
    state: AccountState
    stream: _Stream


@dataclass(frozen=True)
class RunResult:
    combine_attempts: int
    combine_passes: int
    combine_breaches: int  # resolved failures; attempts - passes - breaches = open at horizon
    first_pass_day: int  # -1: never
    first_payout_day: int  # -1: never
    payout_count: int
    payout_cents: int
    fee_cents: int
    monthly_payout_cents: tuple[int, ...]
    xfa_activated: int
    xfa_breaches: int
    breach_days: tuple[tuple[int, int, int], ...]  # (day, XFAs active at open, XFAs breached)
    xfa_account_days: int
    max_concurrent_xfa: int

    @property
    def net_cents(self) -> int:
        return self.payout_cents - self.fee_cents


def trade_day(
    state: AccountState, stream: _Stream, day: int, micros: int, book: CostBook, label: date
) -> AccountState:
    """One account, one day: every segment through the rules engine, then the close."""
    size = min(micros, max_position_micros(state.phase, state.session_start_balance_cents))
    segments = len(stream.pnl[day])
    for s in range(segments):
        state = record_realized_pnl(state, -book.side_cents(stream.entry_minute[day][s], size))
        if state.status is not Status.ACTIVE:
            break
        worst = round(size * stream.adverse[day][s] * MES_TICK_VALUE_CENTS)
        state = apply_realtime_mll(state, worst)
        if state.status is not Status.ACTIVE:
            break
        gross = round(size * stream.pnl[day][s] * MES_TICK_VALUE_CENTS)
        exit_cost = book.side_cents(stream.exit_minute[day][s], size)
        state = record_realized_pnl(state, gross - exit_cost)
        if state.status is not Status.ACTIVE:
            break
    return close_trading_day(state, label, segments)


def greedy_payout_cents(state: AccountState, path: PayoutPath) -> int:
    rules = XFA_50K.standard if path is PayoutPath.STANDARD else XFA_50K.consistency
    return min(rules.per_request_cap_cents, state.balance_cents * XFA_50K.payout_balance_ceiling_bps
               // BPS)


def run_one(
    run_index: int, base_seed: int, cfg: FunnelConfig, generator: DayGenerator, book: CostBook
) -> RunResult:
    """One simulated trader-year. Seeded by (base_seed, run_index) only: chunking-invariant."""
    rng = np.random.default_rng(np.random.SeedSequence(entropy=base_seed, spawn_key=(run_index,)))
    horizon = cfg.horizon_days
    market = _Stream.of(generator.draw(rng, horizon))

    def stream_for_new_account() -> _Stream:
        return market if cfg.correlated else _Stream.of(generator.draw(rng, horizon))

    months = [0] * -(-horizon // TRADING_DAYS_PER_MONTH)
    fee = attempts = passes = failed = payouts = paid = activated = breaches = account_days = 0
    first_pass = first_payout = -1
    max_live = 0
    combine: AccountState | None = None
    combine_stream = market
    combine_bill_day = 0
    xfas: list[_Xfa] = []
    breach_days: list[tuple[int, int, int]] = []

    for day in range(horizon):
        label = DAY0 + timedelta(days=day)
        if day % TRADING_DAYS_PER_MONTH == 0:
            fee += cfg.fees.api_monthly_cents
        if combine is None and len(xfas) < cfg.max_xfa_accounts:
            combine, combine_stream = new_combine_account(), stream_for_new_account()
            attempts += 1
            fee += cfg.fees.combine_monthly_cents
            combine_bill_day = day + TRADING_DAYS_PER_MONTH
        elif combine is not None and day == combine_bill_day:
            fee += cfg.fees.combine_monthly_cents
            combine_bill_day += TRADING_DAYS_PER_MONTH

        # XFAs first: an account activated today starts trading tomorrow.
        live_at_open = len(xfas)
        account_days += live_at_open
        max_live = max(max_live, live_at_open)
        survivors: list[_Xfa] = []
        breached_today = 0
        for xfa in xfas:
            state = trade_day(xfa.state, xfa.stream, day, cfg.micros_per_trade, book, label)
            if state.status is Status.BREACHED:
                breached_today += 1
                continue
            amount = greedy_payout_cents(state, cfg.path)
            if amount >= XFA_50K.min_payout_cents:
                outcome = process_payout(state, cfg.path, amount)
                if outcome.refusal is None:
                    state = outcome.state
                    payouts += 1
                    paid += amount
                    months[day // TRADING_DAYS_PER_MONTH] += amount
                    first_payout = day if first_payout < 0 else first_payout
            survivors.append(xfa._replace(state=state))
        if breached_today:
            breaches += breached_today
            breach_days.append((day, live_at_open, breached_today))
        xfas = survivors

        if combine is not None:
            combine = trade_day(combine, combine_stream, day, cfg.micros_per_trade, book, label)
            if combine.status is Status.PASSED:
                passes += 1
                first_pass = day if first_pass < 0 else first_pass
                fee += cfg.fees.xfa_activation_cents
                xfas.append(_Xfa(activated, new_xfa_account(), stream_for_new_account()))
                activated += 1
                combine = None
            elif combine.status is Status.BREACHED:
                failed += 1
                combine = None

    return RunResult(
        combine_attempts=attempts, combine_passes=passes, combine_breaches=failed,
        first_pass_day=first_pass,
        first_payout_day=first_payout, payout_count=payouts, payout_cents=paid, fee_cents=fee,
        monthly_payout_cents=tuple(months), xfa_activated=activated, xfa_breaches=breaches,
        breach_days=tuple(breach_days), xfa_account_days=account_days, max_concurrent_xfa=max_live,
    )


# ------------------------------------------------------------ parallel runs ----
_WORKER: dict = {}


def _init_worker(cfg: FunnelConfig, generator: DayGenerator, base_seed: int) -> None:
    _WORKER.update(cfg=cfg, generator=generator, base_seed=base_seed,
                   book=CostBook(load_slippage_table(), cfg.slippage_statistic))


def _run_chunk(indices: Sequence[int]) -> list[RunResult]:
    w = _WORKER
    return [run_one(i, w["base_seed"], w["cfg"], w["generator"], w["book"]) for i in indices]


def run_many(
    cfg: FunnelConfig,
    generator: DayGenerator,
    n_runs: int,
    base_seed: int,
    *,
    workers: int = 18,
    start_index: int = 0,
    chunk: int = 250,
) -> list[RunResult]:
    """Runs ``start_index .. start_index + n_runs - 1``, in index order, results identical for
    any ``workers``/``chunk`` (each run's RNG depends only on base_seed and its index)."""
    indices = list(range(start_index, start_index + n_runs))
    chunks = [indices[k:k + chunk] for k in range(0, len(indices), chunk)]
    if workers <= 1:
        _init_worker(cfg, generator, base_seed)
        return [r for c in chunks for r in _run_chunk(c)]
    with ProcessPoolExecutor(workers, initializer=_init_worker,
                             initargs=(cfg, generator, base_seed)) as pool:
        return [r for part in pool.map(_run_chunk, chunks) for r in part]


# ------------------------------------------------------------- aggregation ----
def _q(values: np.ndarray, qs: Sequence[float]) -> dict[str, float]:
    return {f"p{round(q * 100)}": float(np.quantile(values, q)) for q in qs}


def monthly_net_usd(results: Sequence[RunResult], horizon_days: int) -> np.ndarray:
    months = horizon_days / TRADING_DAYS_PER_MONTH
    return np.array([r.net_cents for r in results], dtype=float) / 100.0 / months


def summarize(results: Sequence[RunResult], cfg: FunnelConfig) -> dict:
    """Distributions over runs. Money in USD; months = 21 trading days."""
    n = len(results)
    months = cfg.horizon_days / TRADING_DAYS_PER_MONTH
    attempts = np.array([r.combine_attempts for r in results], dtype=float)
    passes = np.array([r.combine_passes for r in results], dtype=float)
    gross_m = np.array([r.payout_cents for r in results], dtype=float) / 100.0 / months
    net_m = monthly_net_usd(results, cfg.horizon_days)
    first_payout = np.array([r.first_payout_day for r in results])
    has_payout = first_payout >= 0
    ttfp_months = first_payout[has_payout] / TRADING_DAYS_PER_MONTH
    qs = (0.10, 0.25, 0.50, 0.75, 0.90)

    multi_open = [(a, b) for r in results for (_, a, b) in r.breach_days if a >= 2]
    breach_events = sum(len(r.breach_days) for r in results)
    return {
        "runs": n,
        "combine": {
            "attempts_total": int(attempts.sum()),
            "passes_total": int(passes.sum()),
            "pass_rate_per_attempt": float(passes.sum() / attempts.sum()),
            "pass_rate_per_resolved_attempt": float(passes.sum() / (passes.sum() + sum(
                r.combine_breaches for r in results))),
            "p_run_passes_at_least_once": float((passes > 0).mean()),
            "mean_attempts_per_run": float(attempts.mean()),
        },
        "first_payout": {
            "p_within_horizon": float(has_payout.mean()),
            "months_to_first_payout_given_payout": _q(ttfp_months, qs) if has_payout.any() else {},
            "median_months_all_runs_censored": (
                float(np.quantile(np.where(has_payout, first_payout, np.inf), 0.5)
                      / TRADING_DAYS_PER_MONTH) if has_payout.mean() >= 0.5 else None
            ),
        },
        "monthly_income_usd": {
            "gross_payouts": {"mean": float(gross_m.mean()), **_q(gross_m, qs)},
            "net_of_fees": {"mean": float(net_m.mean()), **_q(net_m, qs),
                            "p_positive": float((net_m > 0).mean())},
            "mean_fees_per_month": float(
                np.mean([r.fee_cents for r in results]) / 100.0 / months),
        },
        "xfa": {
            "mean_activated_per_run": float(np.mean([r.xfa_activated for r in results])),
            "mean_breaches_per_run": float(np.mean([r.xfa_breaches for r in results])),
            "mean_payouts_per_run": float(np.mean([r.payout_count for r in results])),
            "mean_xfa_account_days_per_run": float(np.mean([r.xfa_account_days for r in results])),
            "p_run_reaches_5_live": float(
                np.mean([r.max_concurrent_xfa >= cfg.max_xfa_accounts for r in results])),
        },
        "blowups": {
            "xfa_breach_events_days": breach_events,
            "days_with_2plus_live_and_a_breach": len(multi_open),
            "share_multi_account_given_2plus_live": (
                float(np.mean([b >= 2 for a, b in multi_open])) if multi_open else None),
            "share_all_live_breached_given_2plus_live": (
                float(np.mean([b == a for a, b in multi_open])) if multi_open else None),
            "p_run_has_same_day_multi_breach": float(
                np.mean([any(b >= 2 for (_, _, b) in r.breach_days) for r in results])),
            "breached_count_histogram_given_2plus_live": {
                str(k): int(sum(1 for _, b in multi_open if b == k))
                for k in range(1, cfg.max_xfa_accounts + 1)
            },
        },
    }


# ------------------------------------------------------ sample-size stability ----
STABILITY_RATE_TOL = 0.01  # 1 percentage point
STABILITY_USD_TOL_ABS = 10.0  # $10 per month ...
STABILITY_USD_TOL_REL = 0.02  # ... or 2% of the value, whichever is larger
BOOTSTRAP_RESAMPLES = 400


def _headline_metrics(results: Sequence[RunResult], cfg: FunnelConfig, rng: np.random.Generator
                      ) -> dict[str, tuple[float, float, str]]:
    """metric -> (estimate, Monte Carlo standard error, kind)."""
    n = len(results)
    net = monthly_net_usd(results, cfg.horizon_days)
    passes = np.array([r.combine_passes for r in results], dtype=float)
    attempts = np.array([r.combine_attempts for r in results], dtype=float)
    ratio = passes.sum() / attempts.sum()
    ratio_se = float(np.sqrt(np.var(passes - ratio * attempts, ddof=1) / n) / attempts.mean())
    any_payout = np.array([r.first_payout_day >= 0 for r in results], dtype=float)
    multi = np.array([any(b >= 2 for (_, _, b) in r.breach_days) for r in results], dtype=float)
    boot = rng.integers(0, n, size=(BOOTSTRAP_RESAMPLES, n))
    resampled = net[boot]
    return {
        "pass_rate_per_attempt": (float(ratio), ratio_se, "rate"),
        "p_first_payout_within_horizon": (float(any_payout.mean()),
                                          float(any_payout.std(ddof=1) / np.sqrt(n)), "rate"),
        "p_same_day_multi_xfa_breach": (float(multi.mean()),
                                        float(multi.std(ddof=1) / np.sqrt(n)), "rate"),
        "monthly_net_usd_mean": (float(net.mean()), float(net.std(ddof=1) / np.sqrt(n)), "usd"),
        "monthly_net_usd_median": (float(np.median(net)),
                                   float(np.median(resampled, axis=1).std(ddof=1)), "usd"),
        "monthly_net_usd_p80": (float(np.quantile(net, 0.8)),
                                float(np.quantile(resampled, 0.8, axis=1).std(ddof=1)), "usd"),
    }


def _tolerance(kind: str, value: float) -> float:
    if kind == "rate":
        return STABILITY_RATE_TOL
    return max(STABILITY_USD_TOL_ABS, STABILITY_USD_TOL_REL * abs(value))


def stability_ladder(
    results: Sequence[RunResult], cfg: FunnelConfig, ladder: Sequence[int], seed: int = 7
) -> dict:
    """Nested prefixes of one run set. N is STABLE when, for every headline metric,
    |m(N) - m(next N)| <= tol and 1.96 * SE(N) <= tol (tolerances fixed above, before any run)."""
    rng = np.random.default_rng(seed)
    rows = []
    for n in ladder:
        metrics = _headline_metrics(results[:n], cfg, rng)
        rows.append({"n": n, "metrics": {k: {"estimate": v[0], "mc_se": v[1], "kind": v[2]}
                                         for k, v in metrics.items()}})
    stable_n: int | None = None
    for cur, nxt in zip(rows, rows[1:], strict=False):
        checks = {}
        for name, m in cur["metrics"].items():
            tol = _tolerance(m["kind"], nxt["metrics"][name]["estimate"])
            delta = abs(m["estimate"] - nxt["metrics"][name]["estimate"])
            checks[name] = {"delta_to_next": delta, "halfwidth_95": 1.96 * m["mc_se"],
                            "tolerance": tol,
                            "ok": delta <= tol and 1.96 * m["mc_se"] <= tol}
        cur["checks_vs_next"] = checks
        cur["stable"] = all(c["ok"] for c in checks.values())
    # stable_n is the smallest rung from which EVERY later comparable rung is also stable: a
    # single rung that passes by luck, with a later one failing, must not count as converged.
    for index, row in enumerate(rows[:-1]):
        if all(later["stable"] for later in rows[index:-1]):
            stable_n = row["n"]
            break
    return {"ladder": rows, "stable_n": stable_n,
            "criterion": {"rate_tol": STABILITY_RATE_TOL, "usd_tol_abs": STABILITY_USD_TOL_ABS,
                          "usd_tol_rel": STABILITY_USD_TOL_REL, "z": 1.96,
                          "rule": "|m(N)-m(next)| <= tol AND 1.96*SE(N) <= tol for every metric"}}
