"""Phase A of Stage E.2a Task 13: the generalized gate on MES's own inputs.

    uv run python -m funnel.exposure_gate_mes regression [--workers 8] [--cells KEY ...]
    uv run python -m funnel.exposure_gate_mes probe [--workers 4]
    uv run python -m funnel.exposure_gate_mes shortcut

- regression: builds MES's segment tables through ``funnel.exposure_segments`` and checks them
  array for array against ``funnel.null_generator.load_null_generator(T)``; then evaluates cells
  through ``funnel.exposure_gate`` with MES's inputs (research bars, sim/slippage_calibration.json,
  2 micros, $1.25 tick, the frozen null baseline) and compares every stored field of D.1e's row
  (reports/power_gate.json + reports/stage_d1e_power_gate_cells.json for grid cells,
  reports/stage_d1e_gate_extension.json for extension points) and the sorted net-income samples
  (reports/power_gate_samples.npz, reports/stage_d1e_gate_extension_samples.npz) for exact
  equality. Resumable: one JSONL line per finished cell.
- probe: the same cells at another worker count (rows must be identical: the RNG depends only on
  the run index) for wall time per cell; peak memory of the process tree (PSS) from a sampler
  process.
- shortcut: the ascending-order shortcut and D3's bracketing subset replayed on the 220 stored
  rows (no simulation).

Writes reports/stage_e2a_funnel_phaseA.json (one section per subcommand, merged) and
reports/stage_e2a_funnel/MES_regression/ (cells.jsonl, samples, null samples). Reads only MES's
research bars (research slice, 2025-04-01..2026-06-12), never a holdout, embargo or confirmation
row; no Databento, no TopstepX.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from data.research_bars import RESEARCH, RESEARCH_SERIES_PATH
from data.splits import RESEARCH_END, RESEARCH_START
from funnel.exposure_gate import (
    MES_FIELD_ALIASES,
    Cell,
    ExposureContext,
    ascending_order,
    ascending_shortcut,
    d3_cell_set,
    eps_funnel,
    eps_operative,
    mes_frozen_critical_values,
    run_exposure,
    with_inputs,
)
from funnel.exposure_segments import (
    MES_WINDOW,
    DateRule,
    build_exposure_segment_table,
    load_exposure_bars,
    mean_abs_move_ticks,
)
from funnel.null_generator import load_null_generator
from funnel.simulator import CostBook
from sim.costs import CALIBRATION_PATH, load_slippage_table
from sim.fill_model import MES_TICK_VALUE_CENTS

ROOT = Path(__file__).resolve().parents[1]
BASELINE_JSON = ROOT / "reports/funnel_null_baseline.json"
GATE_JSON = ROOT / "reports/power_gate.json"
GATE_SAMPLES = ROOT / "reports/power_gate_samples.npz"
CELLS_JSON = ROOT / "reports/stage_d1e_power_gate_cells.json"
EXT_JSON = ROOT / "reports/stage_d1e_gate_extension.json"
EXT_SAMPLES = ROOT / "reports/stage_d1e_gate_extension_samples.npz"
OUT_JSON = ROOT / "reports/stage_e2a_funnel_phaseA.json"
OUT_DIR = ROOT / "reports/stage_e2a_funnel/MES_regression"
PROBE_DIR = ROOT / "reports/stage_e2a_funnel/MES_probe"
ALL_T = (1, 2, 4, 8, 16, 32)
MES_Q, MES_LOT_WEIGHT, MES_TICK = 2, 0.1, 0.25
MES_TICK_VALUE_USD = MES_TICK_VALUE_CENTS / 100

BINDING = "consistency|T2|p0.6|R1.0"
REGRESSION_CELLS = (
    BINDING,  # grid; D.1e's binding cell, $87.48 a day, robust power 0.812
    "consistency|T4|p0.58|R1.0",  # extension; the nearest excluded (marginal) cell
    "standard|T1|p0.5|R2.0",  # grid
    "standard|T1|p0.47|R2.0",  # extension, matched available
    "standard|T8|p0.55|R1.0",  # extension, matched unavailable
    "standard|T16|p0.55|R1.0",  # extension
    "standard|T32|p0.425|R2.0",  # extension, standard path only
)
PROBE_CELLS = ("standard|T1|p0.5|R2.0", "consistency|T4|p0.58|R1.0", "standard|T16|p0.55|R1.0")


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(Path(path).resolve().relative_to(ROOT))


# ------------------------------------------------------------------ inputs ----
def mes_tables() -> tuple[dict[int, object], dict[str, dict]]:
    rule = DateRule(RESEARCH_START, RESEARCH_END, frozenset({RESEARCH}))
    bars = load_exposure_bars(RESEARCH_SERIES_PATH, rule)
    tables, reports = {}, {}
    for t in ALL_T:
        tables[t], reports[str(t)] = build_exposure_segment_table(
            bars, t, tick=MES_TICK, window=MES_WINDOW, rule=rule)
    return tables, reports


def mes_context(tables: dict[int, object]) -> ExposureContext:
    baseline = json.loads(BASELINE_JSON.read_text())
    ctx = ExposureContext(
        exposure="MES", vehicle="MES", q=MES_Q, lot_weight=MES_LOT_WEIGHT,
        tick_value_usd=MES_TICK_VALUE_USD, tables=tables,
        book=CostBook(load_slippage_table(), "mean"),
        critical=mes_frozen_critical_values(baseline, micros=MES_Q))
    return with_inputs(ctx, bars=sha256(RESEARCH_SERIES_PATH), costs=sha256(CALIBRATION_PATH),
                       baseline=sha256(BASELINE_JSON))


def table_regression(tables: dict[int, object]) -> dict:
    """Generalized segment tables vs funnel.null_generator's, array for array."""
    out = {}
    fields = ("move_ticks", "low_ticks", "high_ticks", "entry_minute_ct", "exit_minute_ct")
    for t, mine in tables.items():
        ref = load_null_generator(t).table
        checks = {f: bool(np.array_equal(getattr(mine, f), getattr(ref, f))
                          and getattr(mine, f).dtype == getattr(ref, f).dtype) for f in fields}
        checks["trade_dates"] = mine.trade_dates == ref.trade_dates
        checks["skipped_trade_dates"] = mine.skipped_trade_dates == ref.skipped_trade_dates
        out[str(t)] = {"equal": all(checks.values()), "checks": checks, "days": mine.n_days}
    return out


def stored_rows() -> dict[str, dict]:
    """D.1e's 220 stored rows, keyed by cell key, in D.1e's own field names."""
    gate = json.loads(GATE_JSON.read_text())
    cells = json.loads(CELLS_JSON.read_text())
    ext = json.loads(EXT_JSON.read_text())
    net = {Cell(c["path"], c["segments_per_day"], c["win_probability"],
                c["win_loss_ratio"]).key: c for c in cells["cells"]}
    out: dict[str, dict] = {}
    for r in gate["rows"]:
        key = Cell(r["path"], r["segments_per_day"], r["win_probability"], r["win_loss_ratio"]).key
        c, t = net[key], str(r["segments_per_day"])
        out[key] = {**r, "net_edge_usd_per_day_at_2_micros": c["net_edge_usd_per_day_at_2_micros"],
                    "net_edge_ticks_per_trade_per_micro": c["net_edge_ticks_per_trade_per_micro"],
                    "mean_round_turn_cost_usd_per_micro": cells["rt_cost_usd_per_micro_by_T"][t],
                    "rt_cost_ticks": cells["rt_cost_ticks_by_T"][t], "_source": "grid"}
    for r in ext["rows"]:
        key = Cell(r["path"], r["segments_per_day"], r["win_probability"], r["win_loss_ratio"]).key
        out[key] = {**r, "_source": "extension"}
    return out


def generalized(row: dict) -> dict:
    """A stored D.1e row with the generalized field names (for the shortcut and eps rule)."""
    inverse = {v: k for k, v in MES_FIELD_ALIASES.items()}
    out = {inverse.get(k, k): v for k, v in row.items()}
    out["cell_key"] = Cell(row["path"], row["segments_per_day"], row["win_probability"],
                           row["win_loss_ratio"]).key
    return out


def _same(ours: object, value: object) -> bool:
    """Exact equality; int and float count as one kind (JSON writes 2.0 as 2.0), bool does not."""
    if ours != value:
        return False
    numeric = (int, float)
    if isinstance(ours, bool) or isinstance(value, bool):
        return type(ours) is type(value)
    return type(ours) is type(value) or (isinstance(ours, numeric) and isinstance(value, numeric))


def compare_row(mine: dict, stored: dict) -> dict:
    """Every stored field (except timing and bookkeeping) against the generalized row."""
    inverse = {v: k for k, v in MES_FIELD_ALIASES.items()}
    compared, mismatches = [], {}
    for key, value in stored.items():
        if key in ("wall_seconds", "_source"):
            continue
        ours = mine.get(inverse.get(key, key), "<missing>")
        compared.append(key)
        if not _same(ours, value):
            mismatches[key] = {"stored": value, "generalized": ours}
    return {"fields_compared": len(compared), "mismatches": mismatches,
            "equal": not mismatches}


def samples_equal(key: str, source: str, out_dir: Path) -> bool:
    ours = np.load(out_dir / "samples" / (key.replace("|", "_") + ".npy"))
    with np.load(GATE_SAMPLES if source == "grid" else EXT_SAMPLES) as z:
        ref = z[key]
    return bool(np.array_equal(ours, ref))


# -------------------------------------------------------------- sampler ----
def _tree(pid: int) -> list[int]:
    """``pid`` and its descendants, without the sampler itself."""
    out, stack = [], [pid]
    while stack:
        p = stack.pop()
        if p != os.getpid():
            out.append(p)
        try:
            for task in os.listdir(f"/proc/{p}/task"):
                with open(f"/proc/{p}/task/{task}/children") as fh:
                    stack += [int(c) for c in fh.read().split()]
        except OSError:
            continue
    return out


def _pss_kb(pid: int) -> int:
    try:
        with open(f"/proc/{pid}/smaps_rollup") as fh:
            for line in fh:
                if line.startswith("Pss:"):
                    return int(line.split()[1])
    except OSError:
        return 0
    return 0


def sample_memory(pid: int, out: Path, every: float = 0.5) -> None:
    """Runs in its own process: peak summed PSS of ``pid``'s tree until ``pid`` exits."""
    peak = 0
    while os.path.exists(f"/proc/{pid}"):
        peak = max(peak, sum(_pss_kb(p) for p in _tree(pid)))
        tmp = Path(out).with_suffix(".tmp")  # atomic replace, so a reader never sees a partial file
        tmp.write_text(json.dumps({"peak_pss_mb": round(peak / 1024, 1)}))
        tmp.replace(out)
        time.sleep(every)


def start_sampler(out: Path) -> subprocess.Popen:
    return subprocess.Popen([sys.executable, "-m", "funnel.exposure_gate_mes", "sample-mem",
                             str(os.getpid()), str(out)], cwd=ROOT)


# --------------------------------------------------------------- commands ----
def merge_report(section: str, payload: dict) -> None:
    doc = json.loads(OUT_JSON.read_text()) if OUT_JSON.exists() else {}
    doc[section] = {"generated_utc": datetime.now(UTC).isoformat(), **payload}
    OUT_JSON.write_text(json.dumps(doc, indent=1, default=float))


def run_cells(keys: list[str], workers: int, out_dir: Path) -> tuple[list[dict], dict]:
    cells = {c.key: c for c in d3_cell_set()}
    tables, table_reports = mes_tables()
    ctx = mes_context(tables)
    mem_file = out_dir / "memory.json"
    out_dir.mkdir(parents=True, exist_ok=True)
    sampler = start_sampler(mem_file)
    try:
        rows = run_exposure(ctx, [cells[k] for k in keys], out_dir, workers=workers,
                            log=lambda s: print(s, flush=True))
    finally:
        sampler.terminate()
    peak = json.loads(mem_file.read_text()) if mem_file.exists() else {}
    meta = {"workers": workers, "fingerprint": ctx.fingerprint(), "memory": peak,
            "table_reports": table_reports, "tables": table_regression(tables),
            "e_abs_move_ticks": {str(t): mean_abs_move_ticks(tb) for t, tb in tables.items()},
            "rt_cost_usd_per_micro": {str(t): ctx.rt_cost_usd(t) for t in ALL_T},
            "inputs": dict(ctx.inputs)}
    return rows, meta


def cmd_regression(args: argparse.Namespace) -> None:
    keys = args.cells or list(REGRESSION_CELLS)
    rows, meta = run_cells(keys, args.workers, OUT_DIR)
    stored = stored_rows()
    ext_meta = json.loads(EXT_JSON.read_text())["meta"]["null_table_by_T"]
    cost_check = {t: {"generalized": meta["rt_cost_usd_per_micro"][t],
                      "stored": ext_meta[t]["mean_round_turn_cost_usd_per_micro"],
                      "equal": meta["rt_cost_usd_per_micro"][t]
                      == ext_meta[t]["mean_round_turn_cost_usd_per_micro"]} for t in ext_meta}
    move_check = {t: {"generalized": meta["e_abs_move_ticks"][t],
                      "stored": ext_meta[t]["mean_abs_move_ticks_per_segment"],
                      "equal": meta["e_abs_move_ticks"][t]
                      == ext_meta[t]["mean_abs_move_ticks_per_segment"]} for t in ext_meta}
    results = []
    for row in rows:
        ref = stored[row["cell_key"]]
        cmp = compare_row(row, ref)
        results.append({"cell": row["cell_key"], "source": ref["_source"],
                        "wall_seconds": row["wall_seconds"],
                        "samples_equal": samples_equal(row["cell_key"], ref["_source"], OUT_DIR),
                        **cmp})
    ok = (all(r["equal"] and r["samples_equal"] for r in results)
          and all(v["equal"] for v in meta["tables"].values())
          and all(v["equal"] for v in cost_check.values())
          and all(v["equal"] for v in move_check.values()))
    merge_report("regression", {"all_equal": ok, "cells": results, "rt_cost_check": cost_check,
                                "e_abs_move_check": move_check, **meta})
    print(json.dumps({"all_equal": ok, "cells": [(r["cell"], r["equal"], r["samples_equal"],
                                                  r["fields_compared"], r["wall_seconds"])
                                                 for r in results]}, indent=1))


def cmd_probe(args: argparse.Namespace) -> None:
    out_dir = PROBE_DIR / f"w{args.workers}"
    rows, meta = run_cells(list(PROBE_CELLS), args.workers, out_dir)
    reg = {}
    reg_file = OUT_DIR / "cells.jsonl"
    if reg_file.exists():
        reg = {json.loads(line)["cell_key"]: json.loads(line)
               for line in reg_file.read_text().splitlines() if line.strip()}
    per_cell = []
    for row in rows:
        other = reg.get(row["cell_key"])
        same = None if other is None else all(
            row[k] == other[k] for k in row if k not in ("wall_seconds", "fingerprint"))
        per_cell.append({"cell": row["cell_key"], "T": row["segments_per_day"],
                         "wall_seconds": row["wall_seconds"],
                         "rows_equal_to_regression_run": same,
                         "regression_wall_seconds": None if other is None
                         else other["wall_seconds"]})
    doc = json.loads(OUT_JSON.read_text()) if OUT_JSON.exists() else {}
    probes = doc.get("probe", {}).get("runs", {})
    probes[f"workers_{args.workers}"] = {"cells": per_cell, "memory": meta["memory"],
                                         "cpu_count": os.cpu_count()}
    merge_report("probe", {"runs": probes})
    print(json.dumps(per_cell, indent=1), meta["memory"])


def bracket_subset(rows: dict[str, dict], cells: list[Cell], bar_usd: float, width: float = 0.30
                   ) -> dict:
    lo, hi = bar_usd * (1 - width), bar_usd * (1 + width)
    inside = [c.key for c in cells if lo <= rows[c.key]["net_edge_usd_per_day_at_q"] <= hi]
    passing = [rows[k]["net_edge_usd_per_day_at_q"] for k in inside
               if rows[k]["robust_c80_verdict"] == "pass"]
    full = [rows[c.key]["net_edge_usd_per_day_at_q"] for c in cells
            if rows[c.key]["robust_c80_verdict"] == "pass"]
    return {"bar_usd_per_day": bar_usd, "range": [lo, hi], "cells_in_subset": len(inside),
            "min_pass_subset": min(passing) if passing else None,
            "min_pass_full": min(full) if full else None,
            "passes_below_subset": sum(1 for v in full if v < lo),
            "by_T": {str(t): sum(1 for k in inside if rows[k]["segments_per_day"] == t)
                     for t in ALL_T}}


def cmd_shortcut(_args: argparse.Namespace) -> None:
    cells = list(d3_cell_set())
    rows = {k: generalized(v) for k, v in stored_rows().items()}
    missing = [c.key for c in cells if c.key not in rows]
    if missing:
        raise ValueError(f"stored rows missing for {missing}")
    short = ascending_shortcut(rows, cells)
    groups = ascending_order(cells, {c.key: rows[c.key]["net_edge_usd_per_day_at_q"]
                                     for c in cells})
    evaluated = [c.key for g in groups for c in g][:short["cells_evaluated"]]
    funnel = eps_funnel([rows[c.key] for c in cells], MES_Q, MES_TICK_VALUE_USD)
    tr_bar = eps_operative(MES_Q, MES_TICK_VALUE_USD, funnel)["eps_translated"] * MES_Q * \
        MES_TICK_VALUE_USD
    merge_report("shortcut", {
        "ascending": short, "eps": funnel,
        "operative": eps_operative(MES_Q, MES_TICK_VALUE_USD, funnel),
        "evaluated_cells": [{"cell": k, "net_usd_per_day": rows[k]["net_edge_usd_per_day_at_q"],
                             "robust_c80_verdict": rows[k]["robust_c80_verdict"],
                             "robust_c80_power": rows[k]["robust_c80_power"]} for k in evaluated],
        "bracket_85": bracket_subset(rows, cells, 85.0),
        "bracket_translated": bracket_subset(rows, cells, tr_bar),
        "cells_below_translated_bar": sum(1 for c in cells
                                          if rows[c.key]["net_edge_usd_per_day_at_q"] < tr_bar),
        "pass_cells_by_T": {str(t): sum(1 for c in cells if c.segments_per_day == t
                                        and rows[c.key]["robust_c80_verdict"] == "pass")
                            for t in ALL_T},
        "cells_by_T": {str(t): sum(1 for c in cells if c.segments_per_day == t) for t in ALL_T},
    })
    print(json.dumps({"ascending": short, "eps": funnel}, indent=1, default=float))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="funnel.exposure_gate_mes")
    sub = parser.add_subparsers(dest="cmd", required=True)
    reg = sub.add_parser("regression")
    reg.add_argument("--workers", type=int, default=8)
    reg.add_argument("--cells", nargs="*")
    probe = sub.add_parser("probe")
    probe.add_argument("--workers", type=int, default=4)
    sub.add_parser("shortcut")
    mem = sub.add_parser("sample-mem")
    mem.add_argument("pid", type=int)
    mem.add_argument("out")
    args = parser.parse_args(argv)
    if args.cmd == "sample-mem":
        sample_memory(args.pid, Path(args.out))
        return
    os.nice(10)
    {"regression": cmd_regression, "probe": cmd_probe, "shortcut": cmd_shortcut}[args.cmd](args)


if __name__ == "__main__":
    main()
