"""Addendum A-1's three validations (reports/stage_e2a_epsilon_declaration_addendum.md).

    uv run python -m funnel.exposure_gate_run validate-a1 [--workers 12]

1. Batched evaluation reproduces the full run: for three stored ZT cells, the full run is
   recomputed through the path that wrote the stored rows (``run_many_with_book``) in run order,
   and checked to be the stored run (its sorted net incomes equal the stored samples bit for
   bit); then the batched path (``run_many_early_stop``, batches of EARLY_STOP_CHUNK = 50, never
   stopping) must give the same first n net incomes, bit for bit, at every batch boundary
   n = 50, 100, ..., 8,000.
2. Early stop on stored failing cells of ZT (and ZF): the verdict is "not pass"; the failure
   count equals the count over the batched prefix, and the prefix's net incomes are a
   sub-multiset of the stored run's samples (so the count is a count over careers of the stored
   run: a prefix count).
3. ZT's binding cell (consistency, T = 2, p = 0.55, R = 2.0) through the early-stop path gives the
   stored row, every field, and the stored samples.
Writes reports/stage_e2a_funnel/a1_validation.json; ``write_report`` adds it to the epsilon md.
"""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from funnel.exposure_gate import (
    BASE_SEED,
    EARLY_STOP_CHUNK,
    HEADLINE_CONFIDENCE,
    FunnelConfig,
    PayoutPath,
    QualityDayGenerator,
    d3_cell_set,
    evaluate_cell,
    max_failures_for_pass,
    monthly_net_usd,
    run_many_early_stop,
    run_many_with_book,
    scaled,
)
from funnel.exposure_gate_run import OUT_DIR, build_context, read_rows

OUT = OUT_DIR / "a1_validation.json"
# ZT stored rows: robust power 0.727 (fail), 0.220 (fail), 0.000 (fail)
V1_CELLS = ("consistency|T1|p0.55|R2.0", "consistency|T1|p0.55|R1.5", "standard|T2|p0.5|R1.0")
# failing cells from power 0.727 and 0.644 (late stops) down to 0 (early stops), T = 1..16
V2_CELLS = ("consistency|T1|p0.55|R2.0", "consistency|T4|p0.6|R1.5", "standard|T1|p0.45|R1.5",
            "consistency|T2|p0.45|R2.0", "standard|T4|p0.5|R1.5", "consistency|T8|p0.425|R2.0",
            "standard|T16|p0.45|R1.5")
V3_CELL = "consistency|T2|p0.55|R2.0"
START = "forkserver"


def _samples(vehicle: str, key: str) -> np.ndarray:
    return np.load(OUT_DIR / vehicle / "samples" / (key.replace("|", "_") + ".npy"))


def _generator(ctx, cell):
    cfg = FunnelConfig(PayoutPath(cell.path), ctx.size_units)
    return cfg, scaled(QualityDayGenerator(ctx.tables[cell.segments_per_day], cell.params),
                       ctx.factor)


def _sub_multiset(part: np.ndarray, whole_sorted: np.ndarray) -> bool:
    values, counts = np.unique(part, return_counts=True)
    have = (np.searchsorted(whole_sorted, values, side="right")
            - np.searchsorted(whole_sorted, values, side="left"))
    return bool(np.all(have >= counts))


def validation_1(ctx, cells: dict, workers: int) -> list[dict]:
    out = []
    for key in V1_CELLS:
        t0 = time.perf_counter()
        cell = cells[key]
        cfg, gen = _generator(ctx, cell)
        ref = monthly_net_usd(run_many_with_book(cfg, gen, ctx.runs, BASE_SEED, ctx.book,
                                                 workers=workers, start_method=START),
                              cfg.horizon_days)
        stored = _samples(ctx.vehicle, key)
        batched, stopped, _ = run_many_early_stop(
            cfg, gen, ctx.runs, BASE_SEED, ctx.book, workers=workers, critical_value=np.inf,
            max_failures=ctx.runs + 1, start_method=START)
        net_b = monthly_net_usd(batched, cfg.horizon_days)
        bounds = list(range(EARLY_STOP_CHUNK, ctx.runs + 1, EARLY_STOP_CHUNK))
        prefix_equal = [bool(np.array_equal(net_b[:n], ref[:n])) for n in bounds]
        out.append({"cell": key, "reference_is_stored_run": bool(np.array_equal(np.sort(ref),
                                                                                  stored)),
                    "batched_stopped": stopped, "batch_boundaries_checked": len(bounds),
                    "prefixes_equal_at_every_boundary": all(prefix_equal),
                    "first_unequal_boundary": next((n for n, ok in zip(bounds, prefix_equal,
                                                                        strict=True)
                                                    if not ok), None),
                    "passed": bool(np.array_equal(np.sort(ref), stored)) and all(prefix_equal),
                    "seconds": round(time.perf_counter() - t0, 1)})
        print(f"V1 {key}: {out[-1]}", flush=True)
    return out


def validation_2(ctx, cells: dict, rows: dict, workers: int) -> list[dict]:
    out = []
    m = max_failures_for_pass(ctx.runs)
    for key in V2_CELLS:
        t0 = time.perf_counter()
        cell = cells[key]
        stored = rows[key]
        k = ctx.critical.robust_value(cell.path, HEADLINE_CONFIDENCE)
        cfg, gen = _generator(ctx, cell)
        prefix, stopped, failures = run_many_early_stop(
            cfg, gen, ctx.runs, BASE_SEED, ctx.book, workers=workers, critical_value=k,
            max_failures=m, start_method=START)
        net = monthly_net_usd(prefix, cfg.horizon_days)
        samples = _samples(ctx.vehicle, key)
        stored_failures = int(np.sum(~(samples > k)))
        row = evaluate_cell(ctx, cell, np.load(next((OUT_DIR / ctx.vehicle).glob(
            f"null_{cell.path}_*.npy"))), workers, START, early_stop=True)
        checks = {
            "stored_verdict": stored["robust_c80_verdict"],
            "stored_power": stored["robust_c80_power"],
            "stored_failures_of_8000": stored_failures,
            "stopped": stopped, "runs_done": len(prefix), "failures": failures,
            "verdict_not_pass": row["robust_c80_verdict"] != "pass",
            "row_early_stop_matches": (row.get("early_stop_runs") == len(prefix)
                                       and row.get("early_stop_failures") == failures)
            if row.get("early_stopped") else row.get("robust_c80_verdict") == stored[
                "robust_c80_verdict"],
            "failure_count_is_prefix_count": failures == int(np.sum(~(net > k))),
            "prefix_is_sub_multiset_of_stored_samples": _sub_multiset(net, samples),
            "failures_not_above_stored": failures <= stored_failures,
            "max_failures": m, "seconds": round(time.perf_counter() - t0, 1)}
        checks["passed"] = all(checks[c] for c in (
            "verdict_not_pass", "row_early_stop_matches", "failure_count_is_prefix_count",
            "prefix_is_sub_multiset_of_stored_samples", "failures_not_above_stored"))
        out.append({"cell": key, **checks})
        print(f"V2 {key}: {out[-1]}", flush=True)
    return out


def validation_3(ctx, cells: dict, rows: dict, workers: int) -> dict:
    t0 = time.perf_counter()
    cell = cells[V3_CELL]
    stored = rows[V3_CELL]
    null = np.load(next((OUT_DIR / ctx.vehicle).glob(f"null_{cell.path}_*.npy")))
    row = evaluate_cell(ctx, cell, null, workers, START, early_stop=True)
    samples_equal = bool(np.array_equal(row.pop("_net_samples"), _samples(ctx.vehicle, V3_CELL)))
    skip = {"wall_seconds", "fingerprint"}
    diffs = {k: {"stored": v, "new": row.get(k, "<missing>")} for k, v in stored.items()
             if k not in skip and row.get(k, "<missing>") != v}
    extra = sorted(set(row) - set(stored) - skip)
    out = {"cell": V3_CELL, "stored_verdict": stored["robust_c80_verdict"],
           "fields_compared": len([k for k in stored if k not in skip]),
           "differences": diffs, "extra_fields_in_new_row": extra,
           "samples_equal": samples_equal, "early_stopped": row.get("early_stopped"),
           "passed": not diffs and samples_equal and row.get("early_stopped") is False,
           "seconds": round(time.perf_counter() - t0, 1)}
    print(f"V3 {V3_CELL}: {out}", flush=True)
    return out


def validate(workers: int) -> None:
    t0 = time.perf_counter()
    ctx, facts = build_context("ZT")
    cells = {c.key: c for c in d3_cell_set()}
    rows = read_rows(OUT_DIR / "ZT")
    for key in (*V1_CELLS, *V2_CELLS, V3_CELL):
        if key not in rows:
            raise KeyError(f"ZT has no stored row for {key}")
    doc = {"addendum": "reports/stage_e2a_epsilon_declaration_addendum.md",
           "addendum_sha256": "e6253be2274303f8b219bef539b3807935bbe80e0c1462289c56ff0dc6b88d32",
           "exposure": "ZT", "workers": workers, "start_method": START,
           "chunk": EARLY_STOP_CHUNK, "max_failures_for_pass": max_failures_for_pass(ctx.runs),
           "started_utc": datetime.now(UTC).isoformat()}
    doc["validation_1"] = validation_1(ctx, cells, workers)
    doc["validation_2"] = validation_2(ctx, cells, rows, workers)
    doc["validation_3"] = validation_3(ctx, cells, rows, workers)
    doc["all_passed"] = (all(v["passed"] for v in doc["validation_1"])
                         and all(v["passed"] for v in doc["validation_2"])
                         and doc["validation_3"]["passed"])
    doc["seconds"] = round(time.perf_counter() - t0, 1)
    Path(OUT).write_text(json.dumps(doc, indent=1, default=float))
    print(f"A-1 validations all passed: {doc['all_passed']} ({doc['seconds']}s)", flush=True)
