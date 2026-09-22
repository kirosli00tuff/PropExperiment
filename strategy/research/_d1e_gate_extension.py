"""Stage D.1e, Task 2b: extra power-gate points, finer in quality and deeper in activity.

    uv run python -m strategy.research._d1e_gate_extension

Why: the Stage B power gate is a 5 x 4 x 3 grid (p x R x round turns/day), too coarse to
place the gate's pass/fail boundary in NET ticks per trade, and it stops at 4 round turns
per day. This script evaluates a lead-specified list of extra (T, p, R) points with the
EXISTING funnel code, unchanged, and reports each point's net edge per trade so the lead
can read the boundary off a net-ticks axis instead of a (p, R) lattice.

What is reused verbatim (nothing under funnel/ is modified):
- ``funnel.power_gate.evaluate_point`` for every cell, with the same baseline JSON, the
  same ``BASE_SEED``, the same 8,000 runs per point and the same 2 headline micros;
- the per-path null comparison sample built exactly as ``power_gate.main`` builds it: the
  T=1 null generator, seed ``BASE_SEED + 1``, same runs;
- ``funnel.null_generator.load_null_generator(T)`` for every T, including T = 8/16/32.

Matched vs robust at T outside the baseline grid: the null baseline's sensitivity rows only
cover T = 1/2/4, so ``matched_critical_value`` raises ``KeyError`` at T = 8/16/32. Rather
than edit funnel/, those cells are computed with ``matched_critical_value`` temporarily
swapped for a NaN sentinel inside this module's namespace-level wrapper. Every other call
(``run_many`` / ``monthly_net_usd`` / ``summarize`` / ``verdict``) is identical; the matched
columns that the sentinel would have produced are then overwritten with null and the row is
flagged ``"matched_unavailable": true``. Only the ROBUST verdicts are meaningful there.

Outputs (nothing else is written):
- ``reports/stage_d1e_gate_extension.json`` - meta + one row per point, rewritten after
  every completed (path, T) group so an interrupted run leaves usable partial results;
- ``reports/stage_d1e_gate_extension_samples.npz`` - each cell's sorted monthly-net-income
  samples under ``power_gate.sample_key(...)``, so verdicts can be re-scored later.

Safety: bars are read only through ``data.research_bars`` (inside ``load_null_generator``,
which refuses holdout and embargo dates at construction). Nothing here touches the sealed
holdout, the TopstepX API or Databento. Re-running resumes: points already present in the
JSON are skipped.
"""

from __future__ import annotations

import hashlib
import json
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from funnel import power_gate
from funnel.null_generator import load_null_generator
from funnel.power_gate import BASE_SEED, CONFIDENCE_LEVELS, QualityParams, sample_key
from funnel.simulator import FunnelConfig, monthly_net_usd, run_many
from rules.xfa_rules import PayoutPath

OUT_JSON = Path("reports/stage_d1e_gate_extension.json")
OUT_SAMPLES = Path("reports/stage_d1e_gate_extension_samples.npz")
HASHED_SOURCES = (
    Path("funnel/power_gate.py"),
    Path("funnel/quality_generator.py"),
    Path("funnel/null_generator.py"),
)

POINT_LIST_SOURCE = "lead brief, Stage D.1e Task 2b"
MATCHED_AVAILABLE_T = (1, 2, 4)
MES_TICK_VALUE_USD = 1.25

BOTH = (PayoutPath.STANDARD, PayoutPath.CONSISTENCY)
STANDARD_ONLY = (PayoutPath.STANDARD,)

# (T, paths, ((p, R), ...)) in execution order.
PLAN: tuple[tuple[int, tuple[PayoutPath, ...], tuple[tuple[float, float], ...]], ...] = (
    (1, BOTH, ((0.47, 2.0), (0.48, 2.0), (0.49, 2.0),
               (0.56, 1.5), (0.57, 1.5), (0.58, 1.5), (0.59, 1.5),
               (0.52, 1.75), (0.54, 1.75),
               (0.65, 1.0), (0.70, 1.0),
               (0.45, 2.5))),
    (2, BOTH, ((0.47, 2.0), (0.48, 2.0), (0.49, 2.0),
               (0.52, 1.5), (0.53, 1.5), (0.54, 1.5),
               (0.62, 1.0), (0.65, 1.0),
               (0.50, 1.75), (0.52, 1.75))),
    (4, BOTH, ((0.42, 2.0), (0.43, 2.0), (0.44, 2.0),
               (0.48, 1.5), (0.49, 1.5),
               (0.58, 1.0), (0.59, 1.0),
               (0.46, 1.75), (0.48, 1.75),
               (0.66, 0.75), (0.68, 0.75))),
    (8, BOTH, ((0.40, 2.0), (0.425, 2.0), (0.45, 2.0),
               (0.45, 1.5), (0.475, 1.5), (0.50, 1.5),
               (0.55, 1.0), (0.575, 1.0), (0.60, 1.0))),
    (16, BOTH, ((0.40, 2.0), (0.425, 2.0),
                (0.45, 1.5), (0.475, 1.5),
                (0.55, 1.0), (0.60, 1.0))),
    (32, STANDARD_ONLY, ((0.40, 2.0), (0.425, 2.0), (0.45, 1.5), (0.475, 1.5))),
)

PROBE_POINT = (PayoutPath.STANDARD, 1, 0.50, 1.75)  # timing probe only, not a reported row

_MATCHED_FIELD_SUFFIXES = ("critical_value", "power", "power_se", "power_lower95", "verdict")


def _nan_matched_critical_value(*_args: object, **_kwargs: object) -> float:
    """Sentinel standing in for a matched null that the baseline does not contain."""
    return float("nan")


def evaluate_point_any_t(path: PayoutPath, params: QualityParams, segments: int, micros: int,
                         n: int, generators: dict, baseline: dict,
                         null_sorted: np.ndarray) -> dict:
    """``power_gate.evaluate_point``; at T outside the baseline grid, robust verdicts only."""
    if segments in MATCHED_AVAILABLE_T:
        row = power_gate.evaluate_point(path, params, segments, micros, n, generators,
                                        baseline, null_sorted)
        row["matched_unavailable"] = False
        return row

    original = power_gate.matched_critical_value
    power_gate.matched_critical_value = _nan_matched_critical_value
    try:
        with np.errstate(invalid="ignore"):
            row = power_gate.evaluate_point(path, params, segments, micros, n, generators,
                                            baseline, null_sorted)
    finally:
        power_gate.matched_critical_value = original
    for c in CONFIDENCE_LEVELS:
        tag = f"c{round(c * 100)}"
        for suffix in _MATCHED_FIELD_SUFFIXES:
            row[f"{tag}_{suffix}"] = None
    row["matched_unavailable"] = True
    return row


def add_net_edge_fields(row: dict, rt_cost_usd_per_micro: float, micros: int) -> dict:
    """Net-of-cost edge per trade and per day, from the row's gross edge."""
    rt_cost_ticks = rt_cost_usd_per_micro / MES_TICK_VALUE_USD
    gross_ticks = row["expected_gross_edge_ticks_per_trade_per_micro"]
    gross_usd = row["expected_gross_edge_usd_per_trade_per_micro"]
    row["mean_round_turn_cost_usd_per_micro"] = rt_cost_usd_per_micro
    row["rt_cost_ticks"] = rt_cost_ticks
    row["net_edge_ticks_per_trade_per_micro"] = gross_ticks - rt_cost_ticks
    row["net_edge_usd_per_day_at_2_micros"] = (
        (gross_usd - rt_cost_usd_per_micro) * micros * row["segments_per_day"])
    return row


def row_key(path: str, segments: int, p: float, r: float) -> str:
    return sample_key(path, segments, p, r)


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def per_cell_seconds_by_t(rows: list[dict]) -> dict:
    out: dict[str, dict] = {}
    for t in sorted({r["segments_per_day"] for r in rows}):
        secs = [r["wall_seconds"] for r in rows if r["segments_per_day"] == t]
        by_path = {}
        for p in ("standard", "consistency"):
            xs = [r["wall_seconds"] for r in rows
                  if r["segments_per_day"] == t and r["path"] == p]
            if xs:
                by_path[p] = round(float(np.mean(xs)), 1)
        out[str(t)] = {"cells": len(secs), "mean": round(float(np.mean(secs)), 1),
                       "min": round(min(secs), 1), "max": round(max(secs), 1),
                       "mean_by_path": by_path}
    return out


def write_outputs(rows: list[dict], samples: dict[str, np.ndarray], meta: dict) -> None:
    meta = dict(meta)
    meta["per_cell_seconds_by_T"] = per_cell_seconds_by_t(rows)
    meta["generated_utc"] = datetime.now(UTC).isoformat()
    OUT_JSON.write_text(json.dumps({"meta": meta, "rows": rows}, indent=1, default=float))
    np.savez_compressed(OUT_SAMPLES, **samples)


def load_resume() -> tuple[list[dict], dict[str, np.ndarray]]:
    if not OUT_JSON.exists():
        return [], {}
    rows = json.loads(OUT_JSON.read_text())["rows"]
    samples: dict[str, np.ndarray] = {}
    if OUT_SAMPLES.exists():
        with np.load(OUT_SAMPLES) as z:
            samples = {k: z[k] for k in z.files}
    keep = [r for r in rows
            if row_key(r["path"], r["segments_per_day"], r["win_probability"],
                       r["win_loss_ratio"]) in samples]
    return keep, samples


def main() -> None:
    started = time.perf_counter()
    baseline = json.loads(power_gate.NULL_BASELINE_JSON.read_text())
    micros = int(baseline["sizing"]["headline_micros"])
    n = power_gate.runs_per_point(baseline)
    rows, samples = load_resume()
    done = {row_key(r["path"], r["segments_per_day"], r["win_probability"], r["win_loss_ratio"])
            for r in rows}
    if done:
        print(f"resuming: {len(done)} points already present", flush=True)

    meta = {
        "base_seed": BASE_SEED,
        "runs_per_point": n,
        "headline_micros": micros,
        "null_baseline_generated_utc": baseline["generated_utc"],
        "source_sha256": {str(p): sha256_of(p) for p in HASHED_SOURCES},
        "point_list_source": POINT_LIST_SOURCE,
        "matched_available_T": list(MATCHED_AVAILABLE_T),
        "runs_per_point_rationale": "power_gate.runs_per_point(baseline) == MIN_RUNS_PER_POINT",
        "null_comparison_sample": "power_gate.main construction: T=1 generator, seed BASE_SEED+1",
        "samples_file": str(OUT_SAMPLES),
        "null_table_by_T": {},
        "probe": None,
        "total_runtime_seconds": None,
    }

    generators: dict[int, object] = {}

    def generator_for(t: int):
        if t not in generators:
            t0 = time.perf_counter()
            generators[t] = load_null_generator(t)
            table = generators[t].table
            meta["null_table_by_T"][str(t)] = {
                "move_ticks_shape": list(table.move_ticks.shape),
                "research_days": table.n_days,
                "mean_abs_move_ticks_per_segment": float(np.abs(table.move_ticks).mean()),
                "mean_round_turn_cost_usd_per_micro": (
                    power_gate.mean_round_turn_cost_usd_per_micro(generators[t], micros)),
                "build_seconds": round(time.perf_counter() - t0, 1),
            }
            print(f"built null generator T={t}: {meta['null_table_by_T'][str(t)]}", flush=True)
        return generators[t]

    generator_for(1)

    null_sorted: dict[str, np.ndarray] = {}
    for path in BOTH:
        cfg = FunnelConfig(path, micros)
        t0 = time.perf_counter()
        null_sorted[path.value] = np.sort(
            monthly_net_usd(run_many(cfg, generators[1], n, BASE_SEED + 1), cfg.horizon_days))
        print(f"null comparison sample {path.value}: {time.perf_counter() - t0:.0f}s", flush=True)

    # ------------------------------------------------------------ timing probe ----
    probe_path, probe_t, probe_p, probe_r = PROBE_POINT
    generator_for(probe_t)
    t0 = time.perf_counter()
    evaluate_point_any_t(probe_path, QualityParams(probe_p, probe_r), probe_t, micros, n,
                         generators, baseline, null_sorted[probe_path.value])
    probe_seconds = round(time.perf_counter() - t0, 1)
    meta["probe"] = {"path": probe_path.value, "segments_per_day": probe_t,
                     "win_probability": probe_p, "win_loss_ratio": probe_r,
                     "wall_seconds": probe_seconds,
                     "note": "timing probe only; not included in rows"}
    print(f"PROBE standard T=1 p=0.50 R=1.75: {probe_seconds}s", flush=True)

    # ------------------------------------------------------------------ cells ----
    for t, paths, points in PLAN:
        gen = generator_for(t)
        rt_cost = power_gate.mean_round_turn_cost_usd_per_micro(gen, micros)
        for path in paths:
            group_t0 = time.perf_counter()
            new = 0
            for p, r in points:
                key = row_key(path.value, t, p, r)
                if key in done:
                    continue
                cell_t0 = time.perf_counter()
                row = evaluate_point_any_t(path, QualityParams(p, r), t, micros, n,
                                           generators, baseline, null_sorted[path.value])
                samples[key] = row.pop("_net_samples")
                row["wall_seconds"] = round(time.perf_counter() - cell_t0, 1)
                add_net_edge_fields(row, rt_cost, micros)
                rows.append(row)
                done.add(key)
                new += 1
                print(f"  {path.value} T={t} p={p} R={r}: {row['wall_seconds']}s "
                      f"net_edge_ticks={row['net_edge_ticks_per_trade_per_micro']:.3f} "
                      f"robust_c80={row['robust_c80_verdict']} "
                      f"({100 * row['robust_c80_power']:.0f}%)", flush=True)
            meta["total_runtime_seconds"] = round(time.perf_counter() - started, 1)
            write_outputs(rows, samples, meta)
            print(f"{path.value} T={t} group done: {new} new cells in "
                  f"{time.perf_counter() - group_t0:.0f}s; total "
                  f"{time.perf_counter() - started:.0f}s; wrote {OUT_JSON}", flush=True)

    meta["total_runtime_seconds"] = round(time.perf_counter() - started, 1)
    write_outputs(rows, samples, meta)
    print(f"done: {len(rows)} rows in {meta['total_runtime_seconds']}s -> {OUT_JSON}", flush=True)


if __name__ == "__main__":
    main()
