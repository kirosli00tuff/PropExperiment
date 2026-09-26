"""Stage E.2a Task 13, phase B: eps per traded exposure (reports/stage_e2a_epsilon_declaration.md).

    uv run python -m funnel.exposure_gate_run drive [--parallel 2] [--workers 6] [--phases B1 B2]
    uv run python -m funnel.exposure_gate_run one --vehicle ZN --phase B1 [--workers 6]
    uv run python -m funnel.exposure_gate_run report

``drive`` runs every traded exposure's B1 in the lead's cluster order (K2, K4, K5, K3, K6, K7, K1),
two exposures at a time, each in its own ``one`` subprocess; then B2 for the exposures whose B1
found no pass below the bar. ``one`` builds the exposure's context (declaration points 3-8, 13,
14), asserts E|m_1| x tick value = r_c against reports/stage_e2a_vehicle_sizes.json (a mismatch
stops that exposure), and evaluates its phase's cells in ascending analytic net $/day, stopping at
the first robust pass (point 11). Every finished cell is one JSONL line under
reports/stage_e2a_funnel/<VEHICLE>/; a restart skips finished cells. ``report`` rewrites
reports/stage_e2a_epsilon.json and .md from those directories (``drive`` does it as it goes).

Declaration points as coded: 1 MES's frozen robust critical values; 2 matched values not computed;
3 size in 0.1-lot units; 4 window [O_X, C_X) on the trade date's own calendar day, flatten flag on;
5 D2's dates exactly (the sizes file's dates_used); 6 first bar at or after O_X, last before C_X,
equal-bar-count split; 7 T = 1..32; 8 D8 cost, mean of buy and sell at q_c, half the commission,
ceil to the cent, no event window; 9 own T = 1 null for p_beats; 16 BASE_SEED, 8,000 runs,
forkserver, nice 10, no cell starts in 15:20-16:05 PT on weekdays.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import math
import os
import subprocess
import sys
import time
from datetime import UTC, date, datetime
from datetime import time as dtime
from fractions import Fraction
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

from data.research_bars import RESEARCH, RESEARCH_EMBARGO
from funnel.exposure_gate import (
    ExposureContext,
    analytic_fields,
    d3_cell_set,
    d8_side_cost_fn,
    eps_funnel,
    mes_frozen_critical_values,
    minute_cost_book,
    run_exposure,
    table_minutes,
    units_per_contract,
)
from funnel.exposure_segments import (
    DateRule,
    SessionWindow,
    build_exposure_segment_table,
    load_exposure_bars,
    mean_abs_move_ticks,
    vendor_tick_from_probe,
)

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "reports"
DECLARATION = (R / "stage_e2a_epsilon_declaration.md",
               "ccdb8ec53f9015d45f60de7d7b6a8a37f1fc8e3dd921723e78b01d158be28c7c")
VEHICLES = (R / "stage_e2a_vehicles.json",
            "1f1cafee4330961799f33d5493e640897cfa79827be98597dbaba23292e29913")
SIZES = (R / "stage_e2a_vehicle_sizes.json",
         "280d7e9df1953069448ca1762588477146a5d3c35bc53d3e9e2df50272c47325")
COSTS = (R / "stage_e2a_costs.json",
         "f4360bb77272d0335485a9e01c0f6fc6ab99c47d52e640d95f9cd0397296df14")
BASELINE = R / "funnel_null_baseline.json"
BARS_JSON = R / "stage_e2a_bars.json"
E0_LIQUIDITY = R / "stage_e0_liquidity.json"
OUT_DIR = R / "stage_e2a_funnel"
OUT_JSON = R / "stage_e2a_epsilon.json"
OUT_MD = R / "stage_e2a_epsilon.md"
COMPUTE_CODE = ("funnel/exposure_gate.py", "funnel/exposure_segments.py", "funnel/simulator.py",
                "funnel/quality_generator.py", "funnel/null_generator.py", "funnel/power_gate.py",
                "rules/xfa_rules.py", "sim/product_costs.py")
RUNNER_CODE = ("funnel/exposure_gate_run.py",)

# The lead's order (U3 cluster order K2, K4, K5, K3, K6, K7, K1; within a cluster as listed).
ORDER = ("ZT", "ZF", "ZN", "TN", "ZB", "UB", "MCL", "NG", "MGC", "MHG",
         "6E", "6A", "6B", "6C", "6J", "6S", "6N", "ZC", "ZW", "ZS", "ZM", "ZL", "HE", "LE",
         "MBT", "MNQ", "M2K", "MYM")
# D9.6 lot-equivalent weights: minis 1, micros 0.1, SIL 0.2, MBT 1, MET 1.
MICROS = frozenset({"MNQ", "M2K", "MYM", "MCL", "MGC", "MHG", "MNG", "M6E", "M6A", "M6B", "MES"})
LOT_WEIGHT_SPECIAL = {"SIL": 0.2, "MBT": 1.0, "MET": 1.0}
ALL_T = (1, 2, 4, 8, 16, 32)
WINDOW_START_UTC, WINDOW_END = date(2025, 4, 1), date(2026, 6, 19)
PT = ZoneInfo("America/Los_Angeles")
AITRADER = (dtime(15, 20), dtime(16, 5))  # no cell starts in [15:20, 16:05) PT on weekdays
FLOOR_EPS = 1e-9


class RcMismatch(RuntimeError):
    """E|m_1| x tick value != r_c: the exposure is stopped (declaration point 6)."""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def rel(path: Path) -> str:
    return str(Path(path).resolve().relative_to(ROOT))


def verified(pair: tuple[Path, str]) -> dict:
    path, expected = pair
    got = sha256(path)
    if got != expected:
        raise RuntimeError(f"{rel(path)}: sha256 {got} != declared {expected}")
    return json.loads(path.read_text()) if path.suffix == ".json" else {}


def lot_weight(root: str) -> float:
    return LOT_WEIGHT_SPECIAL.get(root, 0.1 if root in MICROS else 1.0)


def minute_of(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def traded() -> dict[str, dict]:
    """vehicle root -> its exposure entry (chosen or undersized), checked against ORDER."""
    vehicles = verified(VEHICLES)
    out = {e["vehicle"]: e for e in vehicles["exposures"]
           if e["status"] in ("chosen", "undersized")}
    if set(out) != set(ORDER) or len(ORDER) != len(set(ORDER)):
        raise RuntimeError(f"traded vehicles {sorted(out)} != the lead's order {sorted(ORDER)}")
    return out


def aitrader_gate() -> None:
    """Blocks while now (PT) is a weekday in [15:20, 16:05)."""
    while True:
        now = datetime.now(PT)
        if now.weekday() >= 5 or not (AITRADER[0] <= now.time() < AITRADER[1]):
            return
        time.sleep(30)


# ----------------------------------------------------------------- context ----
def build_context(vehicle: str) -> tuple[ExposureContext, dict]:
    entry = traded()[vehicle]
    sizes = verified(SIZES)["contracts"][vehicle]
    verified(DECLARATION)
    from sim.product_costs import load_cost_table

    verified(COSTS)
    model = load_cost_table()[vehicle]
    parquet = ROOT / sizes["parquet"]
    parquet_sha = sha256(parquet)
    vehicles_inputs = json.loads(VEHICLES[0].read_text())["inputs_sha256"]
    if not (parquet_sha == sizes["parquet_sha256"] == vehicles_inputs[sizes["parquet"]]):
        raise RuntimeError(f"{vehicle}: parquet sha256 {parquet_sha} disagrees with the frozen "
                           "files")
    q, tick_value = int(entry["q_c"]), float(Fraction(sizes["tick_value_usd"]))
    if model.q_c != q or model.tick_value_usd != tick_value or sizes["q_c"] != q:
        raise RuntimeError(f"{vehicle}: q_c or tick value disagree between vehicles, sizes, costs")
    vendor_tick = float(Fraction(sizes["vendor_tick"]))
    e0 = {r["symbol"]: r for r in json.loads(E0_LIQUIDITY.read_text())["products"]}
    from data.build_bars import parse_tick

    probe = json.loads(BARS_JSON.read_text())["products"][vehicle]["raw_checks"]["grid_scale_probe"]
    probed = vendor_tick_from_probe(float(parse_tick(str(e0[vehicle]["tick_size"]))), probe)
    if not math.isclose(probed, vendor_tick, rel_tol=1e-12):
        raise RuntimeError(f"{vehicle}: vendor tick {vendor_tick} != bars.json probe {probed}")

    used = list(sizes["dates_used"])
    last = min(WINDOW_END, date.fromisoformat(sizes["last_trade_date"]))
    rule0 = DateRule(WINDOW_START_UTC, last, frozenset({RESEARCH, RESEARCH_EMBARGO}))
    bars = load_exposure_bars(parquet, rule0)
    exclude = frozenset(set(bars["trade_date"].unique()) - set(used))
    rule = DateRule(WINDOW_START_UTC, last, rule0.allowed_classes, exclude)
    window = SessionWindow(minute_of(sizes["O_X"]), minute_of(sizes["C_X"]), use_flatten_flag=True,
                           require_bar_at_open=False, same_calendar_day=True)
    tables, builds = {}, {}
    for t in ALL_T:
        tables[t], builds[str(t)] = build_exposure_segment_table(
            bars, t, tick=vendor_tick, window=window, rule=rule)
    del bars

    t1 = tables[1]
    sum_abs = int(np.abs(t1.move_ticks).sum())
    rc = Fraction(sum_abs, t1.n_days) * Fraction(sizes["tick_value_usd"])
    rc_check = {"days_equal_dates_used": list(t1.trade_dates) == used,
                "sum_abs_move_ticks": sum_abs,
                "sizes_sum_abs_move_ticks": sizes["sum_abs_move_ticks"],
                "e_abs_m1_x_tick_value": str(rc), "r_c_usd_exact": sizes["r_c_usd_exact"],
                "equal": (list(t1.trade_dates) == used and sum_abs == sizes["sum_abs_move_ticks"]
                          and rc == Fraction(sizes["r_c_usd_exact"]))}
    if not rc_check["equal"]:
        raise RcMismatch(f"{vehicle}: {rc_check}")

    size_units = q * units_per_contract(lot_weight(vehicle))
    book = minute_cost_book(size_units, d8_side_cost_fn(model, q), table_minutes(tables.values()))
    critical = mes_frozen_critical_values(json.loads(BASELINE.read_text()), micros=2,
                                          with_matched=False)
    inputs = {"declaration": DECLARATION[1], "vehicles": VEHICLES[1], "sizes": SIZES[1],
              "costs": COSTS[1], "parquet": parquet_sha, "baseline": sha256(BASELINE),
              **{f"code:{p}": sha256(ROOT / p) for p in COMPUTE_CODE}}
    ctx = ExposureContext(exposure=entry["exposure"], vehicle=vehicle, q=q,
                          lot_weight=lot_weight(vehicle), tick_value_usd=tick_value,
                          tables=tables, book=book, critical=critical, inputs=inputs)
    n_used = len(used)
    facts = {
        "exposure": entry["exposure"], "cluster": entry["cluster"], "vehicle": vehicle,
        "status": entry["status"], "q_c": q, "lot_weight": lot_weight(vehicle),
        "size_units": size_units, "tick_value_usd": tick_value, "vendor_tick": sizes["vendor_tick"],
        "O_X": sizes["O_X"], "C_X": sizes["C_X"], "group": sizes["group"],
        "eps_translated": int(entry["eps_X_net_ticks"]),
        "bar_usd_per_day": int(entry["eps_X_net_ticks"]) * q * tick_value,
        "dates_used": n_used, "r_c_check": rc_check, "vendor_tick_probe": probed,
        "e_abs_move_ticks": {str(t): mean_abs_move_ticks(tb) for t, tb in tables.items()},
        "e_abs_move_usd_at_q": {str(t): mean_abs_move_ticks(tb) * tick_value * q
                                for t, tb in tables.items()},
        "rt_cost_usd_per_contract": {str(t): ctx.rt_cost_usd(t) for t in ALL_T},
        "rt_cost_ticks": {str(t): ctx.rt_cost_usd(t) / tick_value for t in ALL_T},
        "segment_builds": builds,
        "days_skipped_short": {str(t): builds[str(t)]["skipped_by_cause"].get("short", 0)
                               for t in ALL_T},
        "flag_skipped_days_over_5pct": any(
            builds[str(t)]["skipped_by_cause"].get("short", 0) > 0.05 * n_used for t in ALL_T),
        "cost_minutes": len(book.cents_by_minute), "cost_book_sha256": book.fingerprint(),
        "fingerprint": ctx.fingerprint(), "inputs_sha256": inputs,
        "runner_code_sha256": {p: sha256(ROOT / p) for p in RUNNER_CODE},
    }
    if int(entry["eps_X_net_ticks"]) != math.floor(85.0 / (q * tick_value)):
        raise RuntimeError(f"{vehicle}: eps_translated in the vehicles file != floor(85/(q tv))")
    return ctx, facts


def split_cells(ctx: ExposureContext, bar_usd: float) -> tuple[list, list, dict[str, float]]:
    cells = list(d3_cell_set())
    net = {c.key: analytic_fields(ctx, c)["net_edge_usd_per_day_at_q"] for c in cells}
    below = [c for c in cells if net[c.key] < bar_usd]
    above = [c for c in cells if net[c.key] >= bar_usd]
    return below, above, net


# -------------------------------------------------------------- one phase ----
def exposure_dir(vehicle: str) -> Path:
    return OUT_DIR / vehicle


def write_json(path: Path, doc: dict) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc, indent=1, default=float))
    os.replace(tmp, path)


def earlier_fingerprints(status: dict, facts: dict) -> list[str]:
    """Fingerprints of earlier runs of this exposure whose inputs differ from the current ones
    only in code hashes (addendum A-1 changed funnel/exposure_gate.py, not the computation of a
    full cell): their rows are kept and not re-run."""
    out = list(status.get("accepted_fingerprints", []))
    old_fp, old_inputs = status.get("fingerprint"), status.get("inputs_sha256") or {}
    if old_fp and old_fp != facts["fingerprint"]:
        data = {k: v for k, v in old_inputs.items() if not k.startswith("code:")}
        now = {k: v for k, v in facts["inputs_sha256"].items() if not k.startswith("code:")}
        if data != now:
            raise RuntimeError(f"{facts['vehicle']}: earlier rows used other data inputs "
                               f"({sorted(set(data.items()) ^ set(now.items()))})")
        out.append(old_fp)
    return sorted(set(out))


def run_one(vehicle: str, phase: str, workers: int, early_stop: bool = False) -> None:
    out = exposure_dir(vehicle)
    out.mkdir(parents=True, exist_ok=True)
    status_path = out / "status.json"
    status = json.loads(status_path.read_text()) if status_path.exists() else {}
    t0 = time.perf_counter()
    started = datetime.now(UTC).isoformat()
    try:
        ctx, facts = build_context(vehicle)
    except Exception as exc:  # recorded for the lead, then re-raised (the exposure stops)
        status.update({"vehicle": vehicle, "error": f"{type(exc).__name__}: {exc}",
                       "error_phase": phase, "error_utc": datetime.now(UTC).isoformat()})
        write_json(status_path, status)
        raise
    accepted = earlier_fingerprints(status, facts)
    status.update(facts)
    status["accepted_fingerprints"] = accepted
    status.pop("error", None)
    below, above, net = split_cells(ctx, facts["bar_usd_per_day"])
    status["cells_below_bar"] = len(below)
    status["cells_at_or_above_bar"] = len(above)
    cells = below if phase == "B1" else above
    if phase == "B2" and status.get("B1", {}).get("state") != "done":
        raise RuntimeError(f"{vehicle}: B2 before B1 is done")
    if phase == "B2" and status["B1"].get("first_pass") is not None:
        status["B2"] = {"state": "not needed: B1 found a pass below the bar"}
        write_json(status_path, status)
        return
    runs = status.get(phase, {}).get("runs", [])
    runs.append({"started_utc": started, "workers": workers, "early_stop_a1": early_stop,
                 "pid": os.getpid()})
    status[phase] = {**status.get(phase, {}), "state": "running", "started_utc": started,
                     "workers": workers, "start_method": "forkserver", "pid": os.getpid(),
                     "runs": runs}
    write_json(status_path, status)
    run_exposure(ctx, cells, out, workers=workers, mode="ascending", start_method="forkserver",
                 before_cell=aitrader_gate, log=lambda s: print(s, flush=True),
                 early_stop=early_stop, accept_fingerprints=accepted)
    rows = read_rows(out)
    evaluated = [c for c in cells if c.key in rows]
    passing = [rows[c.key] for c in evaluated if rows[c.key]["robust_c80_verdict"] == "pass"]
    first = min(passing, key=lambda r: r["net_edge_usd_per_day_at_q"]) if passing else None
    status = json.loads(status_path.read_text())
    status[phase] = {**status[phase], "state": "done",
                     "finished_utc": datetime.now(UTC).isoformat(),
                     "wall_seconds_this_run": round(time.perf_counter() - t0, 1),
                     "cells_in_phase": len(cells), "cells_evaluated": len(evaluated),
                     "cells_skipped": len(cells) - len(evaluated),
                     "first_pass": None if first is None else first["cell_key"],
                     "cells_early_stopped": sum(1 for c in evaluated
                                                if rows[c.key].get("early_stopped")),
                     "cell_seconds_sum": round(sum(rows[c.key]["wall_seconds"]
                                                   for c in evaluated), 1)}
    write_json(status_path, status)


def check_one(vehicle: str) -> None:
    """Pre-flight: build the context (hashes, vendor tick, r_c assertion, cost lookups for every
    segment minute) and record the facts, without running any cell."""
    out = exposure_dir(vehicle)
    out.mkdir(parents=True, exist_ok=True)
    status_path = out / "status.json"
    status = json.loads(status_path.read_text()) if status_path.exists() else {}
    t0 = time.perf_counter()
    try:
        ctx, facts = build_context(vehicle)
    except Exception as exc:
        status.update({"vehicle": vehicle, "error": f"{type(exc).__name__}: {exc}",
                       "error_phase": "check", "error_utc": datetime.now(UTC).isoformat()})
        write_json(status_path, status)
        raise
    below, above, _ = split_cells(ctx, facts["bar_usd_per_day"])
    status.update(facts)
    status.pop("error", None)
    status.update({"cells_below_bar": len(below), "cells_at_or_above_bar": len(above),
                   "check_seconds": round(time.perf_counter() - t0, 1)})
    write_json(status_path, status)
    print(f"{vehicle}: r_c equal {facts['r_c_check']['equal']}; below bar {len(below)}; "
          f"E|m_1| {facts['e_abs_move_ticks']['1']:.2f} ticks; {status['check_seconds']}s",
          flush=True)


def read_rows(out: Path) -> dict[str, dict]:
    path = out / "cells.jsonl"
    if not path.exists():
        return {}
    return {r["cell_key"]: r for r in (json.loads(line) for line in path.read_text().splitlines()
                                        if line.strip())}


# ---------------------------------------------------------------- report ----
ROW_FIELDS = ("cell_key", "path", "segments_per_day", "win_probability", "win_loss_ratio",
              "net_edge_usd_per_day_at_q", "net_edge_ticks_per_trade_per_contract",
              "expected_gross_edge_ticks_per_trade_per_contract", "rt_cost_ticks",
              "e_abs_move_ticks", "robust_c80_critical_value", "robust_c80_power",
              "robust_c80_power_lower95", "robust_c80_verdict", "monthly_net_mean",
              "monthly_net_p50", "p_first_payout_within_12m", "p_beats_random_null_trader",
              "wall_seconds")


def summarize_exposure(vehicle: str) -> dict:
    out = exposure_dir(vehicle)
    status = json.loads((out / "status.json").read_text()) if (out / "status.json").exists() else {}
    rows = read_rows(out)
    doc = {"vehicle": vehicle, **{k: v for k, v in status.items() if k not in (
        "segment_builds", "inputs_sha256", "runner_code_sha256")}}
    if not status or "q_c" not in status:
        return doc
    q, tv = status["q_c"], status["tick_value_usd"]
    bar = status["bar_usd_per_day"]
    below = [r for r in rows.values() if r["net_edge_usd_per_day_at_q"] < bar]
    above = [r for r in rows.values() if r["net_edge_usd_per_day_at_q"] >= bar]
    b1_state = status.get("B1", {}).get("state", "pending")
    b2_state = status.get("B2", {}).get("state", "pending")
    b1_pass = [r for r in below if r["robust_c80_verdict"] == "pass"]
    fn_rows = eps_funnel(list(rows.values()), q, tv) if rows else None
    if b1_pass:
        best = min(b1_pass, key=lambda r: r["net_edge_usd_per_day_at_q"])
        doc["B1_result"] = {k: best[k] for k in ROW_FIELDS}
    else:
        doc["B1_result"] = "none below the bar" if b1_state == "done" else b1_state
    doc["B1_cells_evaluated"] = len(below)
    doc["B2_cells_evaluated"] = len(above)
    eps_tr = status["eps_translated"]
    if b1_pass:
        fn = eps_funnel(b1_pass, q, tv)
        doc["eps_funnel"] = fn["eps_funnel"]
        doc["eps_operative"] = min(eps_tr, fn["eps_funnel"])
        binding = fn
    elif b1_state == "done":
        doc["eps_operative"] = eps_tr
        a_pass = [r for r in above if r["robust_c80_verdict"] == "pass"]
        if a_pass:
            binding = eps_funnel(a_pass, q, tv)
            doc["eps_funnel"] = binding["eps_funnel"] if b2_state == "done" else \
                f"pending (B2 running; first pass so far gives {binding['eps_funnel']})"
        else:
            binding = None
            doc["eps_funnel"] = ("undefined: no cell passes" if b2_state == "done"
                                 else "pending B2")
    else:
        doc["eps_operative"] = "pending B1"
        binding = None
    above_pass = [r for r in above if r["robust_c80_verdict"] == "pass"]
    if b1_pass:
        doc["B2_result"] = "not needed (B1 found a pass below the bar)"
    elif above_pass:
        best = min(above_pass, key=lambda r: r["net_edge_usd_per_day_at_q"])
        doc["B2_result"] = {k: best[k] for k in ROW_FIELDS}
    else:
        doc["B2_result"] = ("no cell passes" if b2_state == "done" else b2_state)
    unfloored = binding.get("eps_unfloored") if binding else None
    doc["flags"] = {
        "undersized": status["status"] == "undersized",
        "no_passing_cell": doc.get("eps_funnel") == "undefined: no cell passes",
        "t32_binding": bool(binding and binding.get("binding_cell")
                            and "|T32|" in binding["binding_cell"]),
        "skipped_days_over_5pct": status.get("flag_skipped_days_over_5pct"),
        "floor_within_1e-9": (unfloored is not None
                              and abs(unfloored - round(unfloored)) < FLOOR_EPS),
    }
    doc["verdict_counts_evaluated"] = fn_rows["counts"] if fn_rows else None
    doc["cells_evaluated_total"] = len(rows)
    doc["cells_early_stopped"] = sum(1 for r in rows.values() if r.get("early_stopped"))
    doc["cells_full_length"] = len(rows) - doc["cells_early_stopped"]
    doc["cells_skipped_total"] = 220 - len(rows)
    doc["cell_seconds_sum"] = round(sum(r["wall_seconds"] for r in rows.values()), 1)
    doc["inputs_sha256"] = status.get("inputs_sha256")
    return doc


def write_report(compute: dict | None = None) -> None:
    per = [summarize_exposure(v) for v in ORDER]
    prev = json.loads(OUT_JSON.read_text()) if OUT_JSON.exists() else {}
    doc = {"stage": "E.2a", "task": "13 phase B (funnel re-derivation of eps per exposure)",
           "declaration": {"path": rel(DECLARATION[0]), "sha256": DECLARATION[1]},
           "inputs_sha256": {rel(VEHICLES[0]): VEHICLES[1], rel(SIZES[0]): SIZES[1],
                             rel(COSTS[0]): COSTS[1], rel(BASELINE): sha256(BASELINE)},
           "generated_utc": datetime.now(UTC).isoformat(),
           "compute": compute if compute is not None else prev.get("compute", {}),
           "exposures": per}
    write_json(OUT_JSON, doc)
    OUT_MD.write_text(render_md(doc))


def _fmt(v: object) -> str:
    if isinstance(v, float):
        return f"{v:,.2f}"
    return "—" if v is None else str(v)


def render_md(doc: dict) -> str:
    lines = ["# Stage E.2a Task 13: epsilon per traded exposure (funnel re-derivation)", "",
             f"Generated {doc['generated_utc']} by `funnel.exposure_gate_run`; declaration "
             f"`{doc['declaration']['path']}` (sha256 {doc['declaration']['sha256'][:16]}...). "
             "Machine-readable: `reports/stage_e2a_epsilon.json`; per-cell rows: "
             "`reports/stage_e2a_funnel/<VEHICLE>/cells.jsonl`. Written progressively: "
             "'pending' and 'running' mean the pass has not finished.", "",
             "Operative eps = min(translated, funnel). B1 evaluates, in ascending net $/day, the "
             "cells below eps_translated x q_c x tick value and stops at the first robust pass; B2 "
             "continues above the bar for the reported funnel figure only.", "",
             "Early stop (addendum A-1, sha256 e6253be2...): a failing cell stops once more than "
             "1,531 of its 8,000 careers have failed (a robust pass is then impossible); it is "
             "recorded as 'fail (pass impossible after n runs)'. Every passing cell runs in full. "
             "Cells evaluated before the restart at 06:37 PDT (ZT, ZF all; ZN, TN 53 each) ran "
             "in full.", "",
             "| # | Cluster | Exposure | Vehicle | q_c | Status | eps translated | bar $/day | "
             "B1 | B1 cells | early-stopped | eps operative | eps funnel | B2 | flags |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, e in enumerate(doc["exposures"], 1):
        if "q_c" not in e:
            lines.append(f"| {i} | | | {e['vehicle']} | | {e.get('error', 'pending')} "
                         "| | | | | | | | | |")
            continue
        b1 = e.get("B1_result")
        b1s = (f"pass {b1['cell_key']} (${b1['net_edge_usd_per_day_at_q']:.2f})"
               if isinstance(b1, dict) else _fmt(b1))
        b2 = e.get("B2_result")
        b2s = (f"pass {b2['cell_key']} (${b2['net_edge_usd_per_day_at_q']:.2f})"
               if isinstance(b2, dict) else _fmt(b2))
        flags = ", ".join(k for k, v in e.get("flags", {}).items() if v) or "none"
        if e.get("error"):
            flags += f"; ERROR {e['error']}"
        lines.append(f"| {i} | {e['cluster']} | {e['exposure']} | {e['vehicle']} | {e['q_c']} | "
                     f"{e['status']} | {e['eps_translated']} | {e['bar_usd_per_day']:.2f} | "
                     f"{b1s} | {e.get('B1_cells_evaluated')}/{e.get('cells_below_bar')} | "
                     f"{e.get('cells_early_stopped', 0)} | "
                     f"{_fmt(e.get('eps_operative'))} | {_fmt(e.get('eps_funnel'))} | {b2s} | "
                     f"{flags} |")
    lines += ["", "## E|m_T| (vendor ticks per contract) and round-turn cost (ticks)", "",
              "| Vehicle | " + " | ".join(f"T={t}" for t in ALL_T) + " | RT cost T=1 | "
              "E|m_1| x tv = r_c | days used | short days (max over T) |",
              "|---|" + "---|" * (len(ALL_T) + 4)]
    for e in doc["exposures"]:
        if "e_abs_move_ticks" not in e:
            continue
        moves = " | ".join(f"{e['e_abs_move_ticks'][str(t)]:.2f}" for t in ALL_T)
        lines.append(f"| {e['vehicle']} | {moves} | {e['rt_cost_ticks']['1']:.3f} | "
                     f"{e['r_c_check']['equal']} "
                     f"({float(Fraction(e['r_c_check']['r_c_usd_exact'])):.2f}) | "
                     f"{e['dates_used']} | {max(e['days_skipped_short'].values())} |")
    a1 = OUT_DIR / "a1_validation.json"
    if a1.exists():
        lines += a1_section(json.loads(a1.read_text()))
    comp = doc.get("compute") or {}
    lines += ["", "## Compute", "", "```", json.dumps(comp, indent=1, default=float), "```", ""]
    lines += ["Per exposure: cell seconds summed and wall time per phase are in the JSON "
              "(`cell_seconds_sum`, `B1.wall_seconds_this_run`, `B2...`).", ""]
    return "\n".join(lines)


def a1_section(v: dict) -> list[str]:
    out = ["", "## Addendum A-1 validations (before any early stop was used)", "",
           f"All passed: **{v['all_passed']}** ({v['seconds']} s, {v['workers']} workers, "
           f"{v['start_method']}, batches of {v['chunk']} careers, pass needs at most "
           f"{v['max_failures_for_pass']} failures of 8,000). Exposure {v['exposure']}; detail in "
           "`reports/stage_e2a_funnel/a1_validation.json` (a first run with batches of 250 also "
           "passed: `a1_validation_chunk250.json`).", "",
           "1. Batched = full run, bit for bit, at every batch boundary:", "",
           "| Cell | recomputed full run is the stored run | boundaries | all prefixes equal |",
           "|---|---|---|---|"]
    out += [f"| {c['cell']} | {c['reference_is_stored_run']} | {c['batch_boundaries_checked']} | "
            f"{c['prefixes_equal_at_every_boundary']} |" for c in v["validation_1"]]
    out += ["", "2. Early stop on stored failing cells:", "",
            "| Cell | stored power | stopped after n | failures | stored failures of 8,000 | "
            "not pass | prefix count | prefix sub-multiset of stored samples |",
            "|---|---|---|---|---|---|---|---|"]
    out += [f"| {c['cell']} | {c['stored_power']} | {c['runs_done']} | {c['failures']} | "
            f"{c['stored_failures_of_8000']} | {c['verdict_not_pass']} | "
            f"{c['failure_count_is_prefix_count']} | "
            f"{c['prefix_is_sub_multiset_of_stored_samples']} |" for c in v["validation_2"]]
    c3 = v["validation_3"]
    out += ["", f"3. ZT binding cell {c3['cell']} through the new path: {c3['fields_compared']} "
            f"stored fields, differences {c3['differences'] or 'none'}, samples equal "
            f"{c3['samples_equal']}, early_stopped {c3['early_stopped']} (the one added field: "
            f"{', '.join(c3['extra_fields_in_new_row'])}).", ""]
    return out


# ----------------------------------------------------------------- driver ----
def drive(phases: list[str], parallel: int, workers: int, peak_estimate_gb: float | None,
          early_stop: bool = False) -> None:
    from funnel.exposure_gate_mes import start_sampler

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    mem_file = OUT_DIR / "drive_memory.json"
    sampler = start_sampler(mem_file)
    log_dir = OUT_DIR / "logs"
    log_dir.mkdir(exist_ok=True)
    compute = {"threads": parallel * workers, "parallel_exposures": parallel,
               "workers_per_exposure": workers, "start_method": "forkserver", "nice": 10,
               "drive_started_utc": datetime.now(UTC).isoformat(), "phases": {},
               "failures": {}}
    prev = json.loads(OUT_JSON.read_text()).get("compute", {}) if OUT_JSON.exists() else {}
    compute["failures"] = prev.get("failures", {})
    compute["peak_estimate_gb"] = peak_estimate_gb or prev.get("peak_estimate_gb")
    compute["free_gb_at_launch"] = _free_gb()
    compute["early_stop_a1"] = early_stop
    compute["drives"] = [*prev.get("drives", []), {
        "started_utc": compute["drive_started_utc"], "phases": phases, "parallel": parallel,
        "workers": workers, "early_stop_a1": early_stop, "free_gb_at_launch": _free_gb()}]
    try:
        for phase in phases:
            t0 = time.perf_counter()
            queue = list(ORDER)
            if phase == "B2":
                queue = [v for v in ORDER if needs_b2(v)]
            running: dict[str, subprocess.Popen] = {}
            while queue or running:
                while queue and len(running) < parallel:
                    v = queue.pop(0)
                    log = open(log_dir / f"{v}_{phase}.log", "a")  # noqa: SIM115
                    running[v] = subprocess.Popen(  # inherits nice 10 from this process
                        [sys.executable, "-m", "funnel.exposure_gate_run",
                         "one", "--vehicle", v, "--phase", phase, "--workers", str(workers),
                         *(["--early-stop"] if early_stop else [])],
                        cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
                    print(f"{datetime.now(PT):%H:%M:%S} start {v} {phase}", flush=True)
                time.sleep(20)
                for v, proc in list(running.items()):
                    if proc.poll() is not None:
                        del running[v]
                        if proc.returncode:
                            compute["failures"][f"{v}_{phase}"] = proc.returncode
                        print(f"{datetime.now(PT):%H:%M:%S} end {v} {phase} rc={proc.returncode}",
                              flush=True)
                compute["phases"][phase] = {"wall_seconds": round(time.perf_counter() - t0, 1),
                                            "state": "running"}
                # The sampler may be mid-write: keep the last reading (lead fix, 18:05 PDT).
                with contextlib.suppress(json.JSONDecodeError):
                    compute["peak_memory"] = (json.loads(mem_file.read_text())
                                              if mem_file.exists() else {})
                write_report(compute)
            compute["phases"][phase]["state"] = "done"
            write_report(compute)
            print(f"{datetime.now(PT):%H:%M:%S} {phase} done", flush=True)
    finally:
        sampler.terminate()


def _free_gb() -> dict:
    with open("/proc/meminfo") as fh:
        info = {line.split(":")[0]: int(line.split()[1]) for line in fh}
    return {"available_gb": round(info["MemAvailable"] / 2**20, 2),
            "total_gb": round(info["MemTotal"] / 2**20, 2)}


def needs_b2(vehicle: str) -> bool:
    path = exposure_dir(vehicle) / "status.json"
    if not path.exists():
        return False
    status = json.loads(path.read_text())
    return status.get("B1", {}).get("state") == "done" and status["B1"].get("first_pass") is None


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="funnel.exposure_gate_run")
    sub = parser.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("drive")
    d.add_argument("--parallel", type=int, default=2)
    d.add_argument("--workers", type=int, default=6)
    d.add_argument("--phases", nargs="+", default=["B1", "B2"])
    d.add_argument("--peak-estimate-gb", type=float, default=None)
    d.add_argument("--early-stop", action="store_true")
    o = sub.add_parser("one")
    o.add_argument("--vehicle", required=True)
    o.add_argument("--phase", choices=("B1", "B2"), required=True)
    o.add_argument("--workers", type=int, default=6)
    o.add_argument("--early-stop", action="store_true")
    va = sub.add_parser("validate-a1")
    va.add_argument("--workers", type=int, default=12)
    sub.add_parser("report")
    c = sub.add_parser("check")
    c.add_argument("--vehicle", required=True)
    args = parser.parse_args(argv)
    if args.cmd == "report":
        write_report()
        return
    current = os.nice(0)
    if current < 10:
        os.nice(10 - current)
    if args.cmd == "check":
        check_one(args.vehicle)
    elif args.cmd == "drive":
        drive(args.phases, args.parallel, args.workers, args.peak_estimate_gb, args.early_stop)
    elif args.cmd == "validate-a1":
        from funnel.exposure_gate_a1 import validate

        validate(args.workers)
    else:
        run_one(args.vehicle, args.phase, args.workers, args.early_stop)


if __name__ == "__main__":
    main()
