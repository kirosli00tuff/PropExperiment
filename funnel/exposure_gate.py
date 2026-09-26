"""The Stage B power gate re-run per traded exposure (Stage E.2a Task 13; design D3, D11.8).

D3 (frozen): the power gate (funnel/power_gate.py, 8,000 careers per cell, robust verdict, both
payout paths) re-run per exposure with the exposure's own segment moves and its own modelled
round-turn cost; eps_X,funnel = floor(min over passing cells of net $/day / (q_c x tick value_c)),
by D.1e's rule (docs/NULL_CRITERIA.md 2.2), over the fixed cell set (the 120 grid cells plus
D.1e's 100 extension points). Operative eps_X = min(translated, funnel); no passing cell: the
funnel figure is undefined, the translated bar is used and the exposure is flagged (R-12).

What is reused verbatim (nothing under funnel/ changes; MES's behaviour is bit-identical):
``funnel.simulator.run_one`` (every Combine/XFA rule decision, fees, payouts),
``QualityDayGenerator`` / ``NullDayGenerator`` (the draws), ``expected_edge_ticks``,
``summarize`` / ``monthly_net_usd``, and ``power_gate.verdict`` / ``p_beats`` / BASE_SEED /
MIN_RUNS_PER_POINT / CONFIDENCE_LEVELS. What is generalized, and how:

- COST. ``simulator.run_many`` builds MES's CostBook inside its workers; ``run_many_with_book``
  is the same loop with the book passed in. Any object with ``side_cents(minute_ct, size)``
  works: MES's ``CostBook`` for the regression, ``MinuteCostBook`` (a frozen minute -> cents
  table at the exposure's size, built from a per-side cost function) for an exposure.
- SIZE AND MONEY. The simulator books ``round(size x ticks x 125)`` cents and caps ``size`` by
  the Scaling Plan in MICROS. An exposure trades q_c contracts of weight w lots (minis 1, micros
  0.1, SIL 0.2, MBT/MET 1). The gate passes size in micro-equivalents (0.1 lot), ``size_units =
  q_c x 10w``, so the Scaling Plan check stays exact for every vehicle, and wraps the day
  generator so its ticks are re-expressed per micro-equivalent in units of $1.25:
  factor = tick_value_cents / (10w) / 125. Then round(size_units x ticks x factor x 125) =
  round(q_c x ticks x tick_value_cents). For MES (w = 0.1, $1.25 tick) the factor is exactly 1 and
  no wrapper is used, so every draw and every cent is MES's.
- CRITICAL VALUES are an input (``CriticalValues``): MES's frozen null baseline as power_gate.py
  reads it, or anything the lead declares. A missing matched value yields null matched columns,
  flagged ``matched_unavailable``, as D.1e's extension did at T = 8/16/32.

Rows carry D.1e's extension fields, with "micro" read as "contract of the vehicle" and renamed
accordingly (``MES_FIELD_ALIASES`` maps them back for the regression).
"""

from __future__ import annotations

import hashlib
import json
import math
import multiprocessing
import time
from collections import deque
from collections.abc import Callable, Iterable, Mapping, Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field, replace
from functools import cache
from pathlib import Path

import numpy as np

from funnel.null_generator import DayDraws, NullDayGenerator, SegmentTable
from funnel.power_gate import (
    BASE_SEED,
    CONFIDENCE_LEVELS,
    GRID_SEGMENTS_PER_DAY,
    GRID_WIN_LOSS_RATIO,
    GRID_WIN_PROBABILITY,
    HEADLINE_CONFIDENCE,
    MIN_RUNS_PER_POINT,
    p_beats,
    verdict,
)
from funnel.quality_generator import QualityDayGenerator, QualityParams, expected_edge_ticks
from funnel.simulator import FunnelConfig, RunResult, monthly_net_usd, run_one, summarize
from rules.xfa_rules import PayoutPath

MES_TICK_VALUE_CENTS = 125  # the simulator's money unit per "tick" per size unit
TRANSLATED_BAR_USD_PER_DAY = 85.0  # D3 / NULL_CRITERIA_E 2: eps_day at MES's 2 micros
MICROS_PER_LOT = 10
DEFAULT_CHUNK = 250  # simulator.run_many's chunk size (results do not depend on it)
# Addendum A-1: batches of 50 careers, at most workers + 2 batches in flight, so a stop wastes at
# most about workers x 50 careers (the stop itself needs at least 1,532 careers).
EARLY_STOP_CHUNK = 50
PATHS = (PayoutPath.STANDARD, PayoutPath.CONSISTENCY)

MES_FIELD_ALIASES = {  # generalized row field -> the field name in D.1e's stored rows
    "size_contracts": "micros",
    "expected_gross_edge_ticks_per_trade_per_contract":
        "expected_gross_edge_ticks_per_trade_per_micro",
    "expected_gross_edge_usd_per_trade_per_contract":
        "expected_gross_edge_usd_per_trade_per_micro",
    "mean_round_turn_cost_usd_per_contract": "mean_round_turn_cost_usd_per_micro",
    "net_edge_ticks_per_trade_per_contract": "net_edge_ticks_per_trade_per_micro",
    "net_edge_usd_per_day_at_q": "net_edge_usd_per_day_at_2_micros",
}


# ------------------------------------------------------------------ cells ----
@dataclass(frozen=True, order=True)
class Cell:
    path: str
    segments_per_day: int
    win_probability: float
    win_loss_ratio: float
    source: str = field(default="grid", compare=False)

    @property
    def key(self) -> str:  # power_gate.sample_key's spelling
        return (f"{self.path}|T{self.segments_per_day}|p{self.win_probability}"
                f"|R{self.win_loss_ratio}")

    @property
    def params(self) -> QualityParams:
        return QualityParams(self.win_probability, self.win_loss_ratio)


def grid_cells() -> tuple[Cell, ...]:
    """power_gate.main's 120 grid points, in its loop order."""
    return tuple(Cell(path.value, t, p, r, "grid") for path in PATHS
                 for t in GRID_SEGMENTS_PER_DAY for p in GRID_WIN_PROBABILITY
                 for r in GRID_WIN_LOSS_RATIO)


def extension_cells() -> tuple[Cell, ...]:
    """D.1e's 100 extension points (strategy.research._d1e_gate_extension.PLAN), in order."""
    from strategy.research._d1e_gate_extension import PLAN  # the frozen list, not a copy

    return tuple(Cell(path.value, t, p, r, "extension") for t, paths, points in PLAN
                 for path in paths for p, r in points)


def d3_cell_set() -> tuple[Cell, ...]:
    """D3's fixed set: 120 grid cells + 100 extension points = 220 distinct cells."""
    cells = grid_cells() + extension_cells()
    if len({c.key for c in cells}) != len(cells):
        raise ValueError("duplicate cell in the D3 set")
    return cells


# ------------------------------------------------------------------ sizes ----
def units_per_contract(lot_weight: float) -> int:
    """Micro-equivalents (0.1 lot) per contract: micros 1, SIL 2, minis/MBT/MET 10."""
    units = lot_weight * MICROS_PER_LOT
    if units < 1 or abs(units - round(units)) > 1e-9:
        raise ValueError(f"lot weight {lot_weight} is not a whole number of micro-equivalents")
    return round(units)


def money_factor(tick_value_usd: float, lot_weight: float) -> float:
    """Vehicle ticks -> simulator ticks ($1.25 each) per micro-equivalent."""
    return tick_value_usd * 100 / units_per_contract(lot_weight) / MES_TICK_VALUE_CENTS


@dataclass(frozen=True)
class ScaledDayGenerator:
    """Wraps a day generator; multiplies its P&L and excursions by ``factor``. Consumes the
    RNG exactly as the wrapped generator does."""

    inner: object
    factor: float

    def draw(self, rng: np.random.Generator, n_days: int) -> DayDraws:
        d = self.inner.draw(rng, n_days)
        return DayDraws(day_index=d.day_index, side=d.side, pnl_ticks=d.pnl_ticks * self.factor,
                        adverse_ticks=d.adverse_ticks * self.factor,
                        entry_minute_ct=d.entry_minute_ct, exit_minute_ct=d.exit_minute_ct)


def scaled(generator: object, factor: float) -> object:
    return generator if factor == 1 else ScaledDayGenerator(generator, factor)


# ------------------------------------------------------------------- cost ----
SideCostFn = Callable[[int], int]  # CT minute of day -> cents for ONE side of q_c contracts


@dataclass(frozen=True)
class MinuteCostBook:
    """Per-side cost in cents at one size, by CT minute (the ``CostBook`` interface)."""

    size_units: int
    cents_by_minute: Mapping[int, int]

    def side_cents(self, minute_ct: int, size: int) -> int:
        if size != self.size_units:
            raise ValueError(f"cost book is for size {self.size_units}, asked {size}: the Scaling "
                             "Plan cannot bind at a 1-lot size, so this is a wiring error")
        return self.cents_by_minute[int(minute_ct)]

    def fingerprint(self) -> str:
        items = sorted((int(k), int(v)) for k, v in self.cents_by_minute.items())
        return hashlib.sha256(json.dumps([self.size_units, items]).encode()).hexdigest()


def table_minutes(tables: Iterable[SegmentTable]) -> list[int]:
    out: set[int] = set()
    for t in tables:
        out.update(int(m) for m in np.unique(t.entry_minute_ct))
        out.update(int(m) for m in np.unique(t.exit_minute_ct))
    return sorted(out)


def minute_cost_book(size_units: int, side_cost: SideCostFn, minutes: Iterable[int]
                     ) -> MinuteCostBook:
    return MinuteCostBook(size_units, {int(m): int(side_cost(int(m))) for m in minutes})


def side_cents(q: int, commission_rt_usd: float, slip_ticks: float, tick_value_usd: float) -> int:
    """One side of q contracts: half the round-turn commission plus slippage, ceil to the cent
    (MES's convention: sim.fill_model books commission in whole cents and ceils slippage)."""
    return math.ceil(round(q * (commission_rt_usd * 100 / 2 + slip_ticks * tick_value_usd * 100),
                           6))


def d8_side_cost_fn(model: object, q: int) -> SideCostFn:
    """A sim.product_costs.ProductCostModel at size q -> per-side cents by CT minute. The funnel's
    trade side is a coin (null) or follows the move (quality), so the per-side slippage is the
    mean of the buy and sell figures of the minute's bucket. No event-window cost (the funnel's
    segments carry clock times, not dates)."""
    from datetime import time as dtime

    def fn(minute: int) -> int:
        at = dtime(minute // 60, minute % 60)
        slip = (model.side_slippage_ticks(at, "buy") + model.side_slippage_ticks(at, "sell")) / 2
        return side_cents(q, model.commission_rt_usd, slip, model.tick_value_usd)

    return fn


def mean_round_turn_cost_usd_per_contract(table: SegmentTable, book: object, size_units: int,
                                          q: int) -> float:
    """power_gate.mean_round_turn_cost_usd_per_micro with the book and size as inputs."""
    total = sum(book.side_cents(int(a), size_units) + book.side_cents(int(b), size_units)
                for a, b in zip(table.entry_minute_ct.ravel(), table.exit_minute_ct.ravel(),
                                strict=True))
    return total / table.entry_minute_ct.size / q / 100.0


# ------------------------------------------------------------- simulation ----
_WORKER: dict = {}


def _init_worker(cfg: FunnelConfig, generator: object, base_seed: int, book: object) -> None:
    _WORKER.update(cfg=cfg, generator=generator, base_seed=base_seed, book=book)


def _run_chunk(indices: Sequence[int]) -> list[RunResult]:
    w = _WORKER
    return [run_one(i, w["base_seed"], w["cfg"], w["generator"], w["book"]) for i in indices]


def run_many_with_book(cfg: FunnelConfig, generator: object, n_runs: int, base_seed: int,
                       book: object, *, workers: int, chunk: int = DEFAULT_CHUNK,
                       start_method: str | None = None) -> list[RunResult]:
    """simulator.run_many with the cost book passed in. Each run's RNG depends only on
    (base_seed, run index), so results are identical for any ``workers``, ``chunk`` and
    ``start_method`` (None: the platform default, fork on Linux, as simulator.run_many;
    "forkserver" avoids forking a parent that holds pyarrow threads)."""
    indices = list(range(n_runs))
    chunks = [indices[k:k + chunk] for k in range(0, n_runs, chunk)]
    if workers <= 1:
        _init_worker(cfg, generator, base_seed, book)
        return [r for c in chunks for r in _run_chunk(c)]
    context = None if start_method is None else multiprocessing.get_context(start_method)
    with ProcessPoolExecutor(workers, mp_context=context, initializer=_init_worker,
                             initargs=(cfg, generator, base_seed, book)) as pool:
        return [r for part in pool.map(_run_chunk, chunks) for r in part]


@cache
def max_failures_for_pass(n: int) -> int:
    """Addendum A-1: the largest number of failing careers (net income not above the robust
    critical value) that still allows ``power_gate.verdict`` to say "pass" at n careers
    (n = 8,000: k_min = 6,469, so 1,531)."""
    passing = [k for k in range(n + 1) if verdict(k / n, n)[0] == "pass"]
    return n - min(passing) if passing else -1


def failures_above(results: Sequence[RunResult], horizon_days: int, critical_value: float) -> int:
    """Careers whose monthly net income does NOT exceed the critical value (power counts
    net > k, so everything else, NaN included, fails)."""
    net = monthly_net_usd(results, horizon_days)
    return int(np.sum(~(net > critical_value)))


def run_many_early_stop(cfg: FunnelConfig, generator: object, n_runs: int, base_seed: int,
                        book: object, *, workers: int, critical_value: float, max_failures: int,
                        chunk: int = EARLY_STOP_CHUNK, start_method: str | None = None
                        ) -> tuple[list[RunResult], bool, int]:
    """Addendum A-1. Runs 0..n_runs-1 in chunks of ``chunk`` run indices, consumed strictly in
    index order; after each chunk, stops once the prefix holds more than ``max_failures``
    failures. Returns (the prefix's results in index order, stopped, failures in the prefix).
    Each run's RNG depends only on (base_seed, run index) (simulator.run_one), so the prefix is
    exactly the first len(prefix) runs of ``run_many_with_book``, and a run that does not stop
    returns exactly its full result list."""
    indices = list(range(n_runs))
    chunks = [indices[k:k + chunk] for k in range(0, n_runs, chunk)]
    results: list[RunResult] = []
    failures = 0
    if workers <= 1:
        _init_worker(cfg, generator, base_seed, book)
        for c in chunks:
            part = _run_chunk(c)
            results += part
            failures += failures_above(part, cfg.horizon_days, critical_value)
            if failures > max_failures:
                return results, True, failures
        return results, False, failures
    context = None if start_method is None else multiprocessing.get_context(start_method)
    pool = ProcessPoolExecutor(workers, mp_context=context, initializer=_init_worker,
                               initargs=(cfg, generator, base_seed, book))
    stopped = False
    try:
        pending: deque = deque()
        queue = deque(chunks)
        while queue and len(pending) < workers + 2:
            pending.append(pool.submit(_run_chunk, queue.popleft()))
        while pending:
            part = pending.popleft().result()
            results += part
            failures += failures_above(part, cfg.horizon_days, critical_value)
            if failures > max_failures:
                stopped = True
                break
            if queue:
                pending.append(pool.submit(_run_chunk, queue.popleft()))
    finally:
        pool.shutdown(wait=True, cancel_futures=True)
    return results, stopped, failures


# --------------------------------------------------------- critical values ----
@dataclass(frozen=True)
class CriticalValues:
    source: str
    robust: Mapping[str, float]  # "standard|c80" -> monthly net USD
    matched: Mapping[str, float] = field(default_factory=dict)  # "standard|c80|T1"

    def robust_value(self, path: str, c: float) -> float:
        return float(self.robust[f"{path}|c{round(c * 100)}"])

    def matched_value(self, path: str, c: float, t: int) -> float | None:
        v = self.matched.get(f"{path}|c{round(c * 100)}|T{t}")
        return None if v is None else float(v)


def mes_frozen_critical_values(baseline: dict, micros: int = 2, with_matched: bool = True
                               ) -> CriticalValues:
    """reports/funnel_null_baseline.json as power_gate.critical_value / matched_critical_value
    read it (matched: the sensitivity row at ``micros`` and each T it has)."""
    robust = {f"{p}|c{round(c * 100)}": float(
        baseline["null_critical_values_monthly_net_usd"][p][f"monthly_net_p{round(c * 100)}"]
        ["value"]) for p in ("standard", "consistency") for c in CONFIDENCE_LEVELS}
    matched: dict[str, float] = {}
    if with_matched:
        for row in baseline["sensitivity"]:
            if row["micros"] == micros:
                for c in CONFIDENCE_LEVELS:
                    matched[f"{row['path']}|c{round(c * 100)}|T{row['segments_per_day']}"] = float(
                        row[f"monthly_net_p{round(c * 100)}"])
    return CriticalValues(f"reports/funnel_null_baseline.json ({baseline['generated_utc']}); "
                          f"matched at {micros} micros: {with_matched}", robust, matched)


# ------------------------------------------------------------------ context ----
@dataclass(frozen=True)
class ExposureContext:
    """Everything one exposure's cells need; built once, then read by every cell."""

    exposure: str
    vehicle: str
    q: int  # contracts of the vehicle (q_c)
    lot_weight: float
    tick_value_usd: float
    tables: Mapping[int, SegmentTable]  # T -> table (vendor ticks per contract)
    book: object  # side_cents(minute_ct, size_units)
    critical: CriticalValues
    runs: int = MIN_RUNS_PER_POINT
    inputs: Mapping[str, str] = field(default_factory=dict)  # provenance, for the fingerprint

    @property
    def size_units(self) -> int:
        return self.q * units_per_contract(self.lot_weight)

    @property
    def factor(self) -> float:
        return money_factor(self.tick_value_usd, self.lot_weight)

    def rt_cost_usd(self, t: int) -> float:
        return mean_round_turn_cost_usd_per_contract(self.tables[t], self.book, self.size_units,
                                                     self.q)

    def fingerprint(self) -> str:
        doc = {"exposure": self.exposure, "vehicle": self.vehicle, "q": self.q,
               "lot_weight": self.lot_weight, "tick_value_usd": self.tick_value_usd,
               "runs": self.runs, "base_seed": BASE_SEED, "critical": self.critical.source,
               "robust": dict(self.critical.robust), "matched": dict(self.critical.matched),
               "tables": {str(t): hashlib.sha256(b"".join(
                   np.ascontiguousarray(a).tobytes() for a in (
                       tb.move_ticks, tb.low_ticks, tb.high_ticks, tb.entry_minute_ct,
                       tb.exit_minute_ct))).hexdigest() for t, tb in sorted(self.tables.items())},
               "book": getattr(self.book, "fingerprint", lambda: type(self.book).__name__)(),
               "inputs": dict(self.inputs)}
        return hashlib.sha256(json.dumps(doc, sort_keys=True).encode()).hexdigest()


def analytic_fields(ctx: ExposureContext, cell: Cell) -> dict:
    """The cell's pre-simulation economics (D.1e's add_net_edge_fields, per contract at q)."""
    table = ctx.tables[cell.segments_per_day]
    edge_ticks = expected_edge_ticks(cell.params, table)
    gross_usd = edge_ticks * ctx.tick_value_usd
    rt_cost_usd = ctx.rt_cost_usd(cell.segments_per_day)
    rt_cost_ticks = rt_cost_usd / ctx.tick_value_usd
    return {
        "expected_gross_edge_ticks_per_trade_per_contract": edge_ticks,
        "expected_gross_edge_usd_per_trade_per_contract": gross_usd,
        "mean_round_turn_cost_usd_per_contract": rt_cost_usd,
        "rt_cost_ticks": rt_cost_ticks,
        "net_edge_ticks_per_trade_per_contract": edge_ticks - rt_cost_ticks,
        "net_edge_usd_per_day_at_q": (gross_usd - rt_cost_usd) * ctx.q * cell.segments_per_day,
    }


def null_samples(ctx: ExposureContext, path: str, workers: int,
                 start_method: str | None = None) -> np.ndarray:
    """power_gate.main's comparison sample: the T=1 zero-edge trader at the cells' size, seed
    BASE_SEED + 1, sorted monthly net income."""
    cfg = FunnelConfig(PayoutPath(path), ctx.size_units)
    gen = scaled(NullDayGenerator(ctx.tables[1]), ctx.factor)
    return np.sort(monthly_net_usd(run_many_with_book(cfg, gen, ctx.runs, BASE_SEED + 1, ctx.book,
                                                      workers=workers, start_method=start_method),
                                   cfg.horizon_days))


def _identity_fields(ctx: ExposureContext, cell: Cell, econ: dict) -> dict:
    table = ctx.tables[cell.segments_per_day]
    return {
        "exposure": ctx.exposure, "vehicle": ctx.vehicle, "cell_key": cell.key,
        "cell_source": cell.source, "path": cell.path,
        "win_probability": cell.win_probability, "win_loss_ratio": cell.win_loss_ratio,
        "segments_per_day": cell.segments_per_day, "size_contracts": ctx.q,
        "size_units": ctx.size_units, "tick_value_usd": ctx.tick_value_usd, "runs": ctx.runs,
        "breakeven_win_probability": cell.params.breakeven_win_probability,
        "e_abs_move_ticks": float(np.abs(table.move_ticks).mean()),
        "expected_gross_edge_ticks_per_trade_per_contract":
            econ["expected_gross_edge_ticks_per_trade_per_contract"],
        "expected_gross_edge_usd_per_trade_per_contract":
            econ["expected_gross_edge_usd_per_trade_per_contract"],
    }


def early_stopped_row(ctx: ExposureContext, cell: Cell, econ: dict, runs_done: int,
                      failures: int, critical_value: float, seconds: float) -> dict:
    """Addendum A-1: a cell stopped once a robust pass became impossible. Only the identity,
    the analytic economics and the stopping record are kept; no power, quantile or sample."""
    row = _identity_fields(ctx, cell, econ)
    row |= {"robust_c80_critical_value": critical_value, "robust_c80_verdict": "fail",
            "verdict_note": f"fail (pass impossible after {runs_done} runs)",
            "early_stopped": True, "early_stop_runs": runs_done,
            "early_stop_failures": failures,
            "early_stop_max_failures": max_failures_for_pass(ctx.runs),
            "robust_c80_power": None, "matched_unavailable": True}
    row |= {k: econ[k] for k in ("mean_round_turn_cost_usd_per_contract", "rt_cost_ticks",
                                 "net_edge_ticks_per_trade_per_contract",
                                 "net_edge_usd_per_day_at_q")}
    row["wall_seconds"] = round(seconds, 1)
    return row


def evaluate_cell(ctx: ExposureContext, cell: Cell, null_sorted: np.ndarray, workers: int,
                  start_method: str | None = None, early_stop: bool = False) -> dict:
    """power_gate.evaluate_point + D.1e's add_net_edge_fields for one exposure. The returned row
    holds the sorted net-income samples under ``_net_samples``. With ``early_stop`` (addendum
    A-1) a cell whose robust pass has become impossible returns ``early_stopped_row``; every
    other cell runs all careers and is identical to the full computation (plus
    ``early_stopped: False``)."""
    t0 = time.perf_counter()
    table = ctx.tables[cell.segments_per_day]
    cfg = FunnelConfig(PayoutPath(cell.path), ctx.size_units)
    gen = scaled(QualityDayGenerator(table, cell.params), ctx.factor)
    econ = analytic_fields(ctx, cell)
    if early_stop:
        k = ctx.critical.robust_value(cell.path, HEADLINE_CONFIDENCE)
        results, stopped, failures = run_many_early_stop(
            cfg, gen, ctx.runs, BASE_SEED, ctx.book, workers=workers, critical_value=k,
            max_failures=max_failures_for_pass(ctx.runs), start_method=start_method)
        if stopped and len(results) < ctx.runs:  # stopped at the last chunk: a full run
            return early_stopped_row(ctx, cell, econ, len(results), failures, k,
                                     time.perf_counter() - t0)
        if len(results) != ctx.runs:
            raise RuntimeError(f"{cell.key}: {len(results)} runs, expected {ctx.runs}")
    else:
        results = run_many_with_book(cfg, gen, ctx.runs, BASE_SEED, ctx.book, workers=workers,
                                     start_method=start_method)
    net = monthly_net_usd(results, cfg.horizon_days)
    summary = summarize(results, cfg)
    row = {
        **_identity_fields(ctx, cell, econ),
        "pass_rate_per_attempt": summary["combine"]["pass_rate_per_attempt"],
        "p_first_payout_within_12m": summary["first_payout"]["p_within_horizon"],
        "monthly_net_mean": float(net.mean()),
        "monthly_net_p10": float(np.quantile(net, 0.10)),
        "monthly_net_p50": float(np.quantile(net, 0.50)),
        "monthly_net_p90": float(np.quantile(net, 0.90)),
        "p_beats_random_null_trader": p_beats(net, null_sorted),
        "mean_xfa_breaches": summary["xfa"]["mean_breaches_per_run"],
        "p_run_reaches_5_live": summary["xfa"]["p_run_reaches_5_live"],
        "p_same_day_multi_breach": summary["blowups"]["p_run_has_same_day_multi_breach"],
    }
    matched_unavailable = False
    for c in CONFIDENCE_LEVELS:
        for prefix, k in (("", ctx.critical.matched_value(cell.path, c, cell.segments_per_day)),
                          ("robust_", ctx.critical.robust_value(cell.path, c))):
            tag = f"{prefix}c{round(c * 100)}"
            if k is None:
                matched_unavailable = True
                row |= {f"{tag}_critical_value": None, f"{tag}_power": None,
                        f"{tag}_power_se": None, f"{tag}_power_lower95": None,
                        f"{tag}_verdict": None}
                continue
            power = float(np.mean(net > k))
            label, se, lower = verdict(power, ctx.runs)
            row |= {f"{tag}_critical_value": k, f"{tag}_power": power, f"{tag}_power_se": se,
                    f"{tag}_power_lower95": lower, f"{tag}_verdict": label}
    row["matched_unavailable"] = matched_unavailable
    row |= {k: econ[k] for k in ("mean_round_turn_cost_usd_per_contract", "rt_cost_ticks",
                                 "net_edge_ticks_per_trade_per_contract",
                                 "net_edge_usd_per_day_at_q")}
    if early_stop:
        row["early_stopped"] = False
    row["wall_seconds"] = round(time.perf_counter() - t0, 1)
    row["_net_samples"] = np.sort(net)
    return row


# ------------------------------------------------------------ epsilon rule ----
def eps_translated(q: int, tick_value_usd: float) -> int:
    return math.floor(TRANSLATED_BAR_USD_PER_DAY / (q * tick_value_usd))


def eps_funnel(rows: Sequence[dict], q: int, tick_value_usd: float) -> dict:
    """NULL_CRITERIA.md 2.2: floor(min over robust_c80 == "pass" of net $/day / (q x tick value));
    marginal cells excluded; no pass -> undefined and flagged (R-12)."""
    counts = {v: sum(1 for r in rows if r["robust_c80_verdict"] == v)
              for v in ("pass", "marginal", "fail")}
    counts["of_which_early_stopped"] = sum(1 for r in rows if r.get("early_stopped"))
    passing = [r for r in rows if r["robust_c80_verdict"] == "pass"]
    if not passing:
        return {"eps_funnel": None, "flag": "no_passing_cell", "binding_cell": None,
                "binding_net_usd_per_day": None, "counts": counts}
    best = min(passing, key=lambda r: r["net_edge_usd_per_day_at_q"])
    value = best["net_edge_usd_per_day_at_q"] / (q * tick_value_usd)
    return {"eps_funnel": math.floor(value), "flag": None, "binding_cell": best["cell_key"],
            "binding_net_usd_per_day": best["net_edge_usd_per_day_at_q"],
            "eps_unfloored": value, "counts": counts}


def eps_operative(q: int, tick_value_usd: float, funnel: dict) -> dict:
    tr = eps_translated(q, tick_value_usd)
    fn = funnel["eps_funnel"]
    return {"eps_translated": tr, "eps_funnel": fn,
            "eps_operative": tr if fn is None else min(tr, fn),
            "flag_r12_no_passing_cell": fn is None}


# ---------------------------------------------------- ascending shortcut ----
def ascending_order(cells: Sequence[Cell], net_usd: Mapping[str, float]) -> list[list[Cell]]:
    """Cells grouped by equal net $/day (the two payout paths of one (T, p, R) always tie),
    groups in ascending order of that figure."""
    groups: dict[float, list[Cell]] = {}
    for c in sorted(cells, key=lambda c: (net_usd[c.key], c.segments_per_day, c.path,
                                          c.win_probability, c.win_loss_ratio)):
        groups.setdefault(net_usd[c.key], []).append(c)
    return [groups[k] for k in sorted(groups)]


def ascending_shortcut(rows_by_key: Mapping[str, dict], cells: Sequence[Cell]) -> dict:
    """Replays the shortcut on already-evaluated rows: which cells it would have evaluated and
    what it returns, beside the full-set answer."""
    net = {c.key: rows_by_key[c.key]["net_edge_usd_per_day_at_q"] for c in cells}
    evaluated: list[str] = []
    found = None
    for group in ascending_order(cells, net):
        evaluated += [c.key for c in group]
        passing = [c for c in group if rows_by_key[c.key]["robust_c80_verdict"] == "pass"]
        if passing:
            found = net[passing[0].key]
            break
    full = [net[k] for k in net if rows_by_key[k]["robust_c80_verdict"] == "pass"]
    return {"cells_total": len(cells), "cells_evaluated": len(evaluated),
            "cells_saved": len(cells) - len(evaluated),
            "min_pass_net_usd_per_day_shortcut": found,
            "min_pass_net_usd_per_day_full": min(full) if full else None,
            "exact_here": found == (min(full) if full else None),
            "evaluated_verdicts": {v: sum(1 for k in evaluated
                                          if rows_by_key[k]["robust_c80_verdict"] == v)
                                   for v in ("pass", "marginal", "fail")},
            "evaluated_by_T": {str(t): sum(1 for k in evaluated
                                           if rows_by_key[k]["segments_per_day"] == t)
                               for t in sorted({c.segments_per_day for c in cells})}}


# ------------------------------------------------------ resumable runner ----
def _jsonable(row: dict) -> dict:
    return {k: v for k, v in row.items() if not k.startswith("_")}


def read_done(jsonl: Path, fingerprint: str | Iterable[str]) -> dict[str, dict]:
    """Finished rows of this exact configuration (or of the accepted earlier fingerprints of the
    same inputs); a line of any other configuration refuses the resume instead of mixing runs."""
    accepted = {fingerprint} if isinstance(fingerprint, str) else set(fingerprint)
    done: dict[str, dict] = {}
    if not jsonl.exists():
        return done
    for n, line in enumerate(jsonl.read_text().splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("fingerprint") not in accepted:
            raise ValueError(f"{jsonl}:{n} was written under another configuration "
                             f"({row.get('fingerprint')} not in {sorted(accepted)}); refusing "
                             "to resume")
        done[row["cell_key"]] = row
    return done


def append_row(jsonl: Path, row: dict) -> None:
    jsonl.parent.mkdir(parents=True, exist_ok=True)
    with jsonl.open("a") as fh:
        fh.write(json.dumps(_jsonable(row)) + "\n")
        fh.flush()


def _sample_path(out_dir: Path, key: str) -> Path:
    return out_dir / "samples" / (key.replace("|", "_") + ".npy")


def cached_null(ctx: ExposureContext, path: str, out_dir: Path, fingerprint: str, workers: int,
                log: Callable[[str], None], start_method: str | None = None,
                earlier: Iterable[str] = ()) -> np.ndarray:
    target = out_dir / f"null_{path}_{fingerprint[:16]}.npy"
    for fp in (fingerprint, *earlier):
        found = out_dir / f"null_{path}_{fp[:16]}.npy"
        if found.exists():
            return np.load(found)
    t0 = time.perf_counter()
    arr = null_samples(ctx, path, workers, start_method)
    target.parent.mkdir(parents=True, exist_ok=True)
    np.save(target, arr)
    log(f"{ctx.exposure} null comparison sample {path}: {time.perf_counter() - t0:.0f}s")
    return arr


def run_exposure(ctx: ExposureContext, cells: Sequence[Cell], out_dir: Path, *, workers: int,
                 mode: str = "all", save_samples: bool = True,
                 log: Callable[[str], None] = print, start_method: str | None = None,
                 before_cell: Callable[[], None] | None = None, early_stop: bool = False,
                 accept_fingerprints: Iterable[str] = ()) -> list[dict]:
    """Evaluates ``cells`` for one exposure into out_dir/cells.jsonl (one line per finished
    cell; finished cells are skipped on restart). ``mode="ascending"`` evaluates cells in
    ascending net $/day and stops after the first tie group holding a robust pass."""
    if mode not in ("all", "ascending"):
        raise ValueError(f"mode must be 'all' or 'ascending', not {mode!r}")
    out_dir = Path(out_dir)
    fingerprint = ctx.fingerprint()
    jsonl = out_dir / "cells.jsonl"
    earlier = tuple(fp for fp in accept_fingerprints if fp != fingerprint)
    done = read_done(jsonl, {fingerprint, *earlier})
    nulls: dict[str, np.ndarray] = {}
    if mode == "all":
        order = [[c] for c in cells]
    else:
        order = ascending_order(cells, {c.key: analytic_fields(ctx, c)["net_edge_usd_per_day_at_q"]
                                        for c in cells})
    for group in order:
        for cell in group:
            if cell.key in done:
                continue
            if before_cell is not None:
                before_cell()
            if cell.path not in nulls:
                nulls[cell.path] = cached_null(ctx, cell.path, out_dir, fingerprint, workers, log,
                                               start_method, earlier)
            row = evaluate_cell(ctx, cell, nulls[cell.path], workers, start_method, early_stop)
            samples = row.pop("_net_samples", None)
            if save_samples and samples is not None:
                target = _sample_path(out_dir, cell.key)
                target.parent.mkdir(parents=True, exist_ok=True)
                np.save(target, samples)
            row["fingerprint"] = fingerprint
            append_row(jsonl, row)
            done[cell.key] = row
            detail = (row["verdict_note"] + f", {row['early_stop_failures']} failures"
                      if row.get("early_stopped") else f"({row['robust_c80_power']:.4f})")
            log(f"  {ctx.exposure} {cell.key}: {row['wall_seconds']}s net/day "
                f"{row['net_edge_usd_per_day_at_q']:.2f} robust_c80={row['robust_c80_verdict']} "
                f"{detail}")
        if mode == "ascending" and any(done[c.key]["robust_c80_verdict"] == "pass"
                                       for c in group):
            break
    return [done[c.key] for c in cells if c.key in done]


def with_inputs(ctx: ExposureContext, **inputs: str) -> ExposureContext:
    return replace(ctx, inputs={**ctx.inputs, **inputs})
