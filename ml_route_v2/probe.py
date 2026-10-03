"""Runtime probe of ML route v2 on a synthetic world of the training window's size (V2.11, V12).

docs/STAGE_E_ML_V2_DESIGN.md V2.11; contract reports/stage_e11_interfaces.md section 8. CLI:

    OPENBLAS_NUM_THREADS=1 nice -n 10 uv run python -m ml_route_v2.probe \
        --products 28|8 --state-dir <dir> [--full] [--payout-paths N] [--isolate-paths]

The world: the products (28: constants.UNIVERSE; 8: a stand-in phase-1 subset, one exposure per
cluster plus MHG, since the real subset is chosen at the freeze, V2.1) on the real group calendars
of the training window (EARLIEST_S_X..TRAIN_LAST, about 1,250 trade dates), synthetic bars only,
no warm-up history before S_X (as the real run: the first dates are lost to warm-up), three
decision times, the full grid of 45 configurations, and a planted sign edge (3 round trips) so the
cost gate trades at a realistic rate.

Steps (each writes its figures to <state-dir>/probe.json as it goes; the pipeline's state files
make a restart resume):
1. the pipeline's panel, filter and Gate 0 stages (force_after_gate0_fail, so every stage runs);
2. ONE complete outer split: every configuration over the split's 4 inner folds plus the outer
   refit (cpcv internals ``_prepare`` and ``_compute_units`` on the first split; the units land in
   the run's own CPCV store, so a full run resumes them);
3. timed pieces for the extrapolation: the frozen refit's largest fit (LightGBM depth 3 on every
   h60 row), PBO and DSR on a matrix of the full run's shape;
4. simulate and payouts for ONE path on a stand-in schedule (ridge lambda 0.1 refit on every h60
   row, k = 1.5: timing only, not a result), extrapolated to 5 paths. As in the pipeline since
   FIX 3 (lead ruling 2026-10-03): the traded vehicles' engine frames go to <state-dir>/engine/
   frames first, then the world's bars and the panel are freed, then the engine runs on the
   frames alone, by default in its own process like the pipeline (``--no-isolate-paths``:
   inline); per-path checkpoints;
5. with --full, and only when the extrapolated total is under 90 minutes (or --force-full): the
   rest of the pipeline end to end (resumable; its CPCV resumes the timed split's units), measured.
Extrapolated full run = panel + filter + gate0 + 15 x split + final refit + PBO/DSR + 15 refits
for the schedule + 5 x (simulate + payouts) of one path.
"""

from __future__ import annotations

import argparse
import dataclasses
import gc
import json
import os
import time
from collections.abc import Callable, Sequence
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np

from ml_route_v2.constants import EARLIEST_S_X, SEED, TRAIN_LAST, UNIVERSE

PHASE1_STANDIN = ("MNQ", "ZN", "6E", "MCL", "MGC", "MHG", "ZC", "MBT")
PROBE_EDGE_C = 3.0
N_OUTER_SPLITS = 15
N_PATHS = 5
PT = ZoneInfo("America/Vancouver")
COLLECTOR_WINDOW = ((15, 30), (16, 0))  # AiTrader news-collect, PT (CLAUDE.md)
FULL_RUN_LIMIT_MIN = 90.0
PROBE_ENGINE_DIR = "probe_engine"  # the stand-in path's simulate checkpoint
PROBE_PAYOUT_DIR = "probe_payouts"


def _now() -> str:
    return datetime.now(PT).isoformat(timespec="seconds")


def wait_outside_collector_window(sleep: Callable[[float], None] = time.sleep) -> float:
    """Block while the wall clock is in the AiTrader window; returns seconds waited."""
    waited = 0.0
    while True:
        now = datetime.now(PT)
        lo = now.replace(hour=COLLECTOR_WINDOW[0][0], minute=COLLECTOR_WINDOW[0][1], second=0)
        hi = now.replace(hour=COLLECTOR_WINDOW[1][0], minute=COLLECTOR_WINDOW[1][1], second=0)
        if not lo <= now < hi:
            return waited
        pause = (hi - now).total_seconds() + 5
        sleep(pause)
        waited += pause


def mem_available_mb() -> float:
    with open("/proc/meminfo", encoding="ascii") as fh:
        for line in fh:
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) / 1024.0
    return float("nan")


class _Log:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.data: dict[str, Any] = json.loads(path.read_text()) if path.exists() else {}

    def put(self, key: str, value: Any) -> None:
        self.data[key] = value
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.data, indent=1, sort_keys=True, default=str))
        tmp.replace(self.path)


def _timed(fn: Callable[[], Any]) -> tuple[Any, dict]:
    from ml_route_v2.pipeline import _peak_rss_mb, _reset_peak

    wait_outside_collector_window()
    _reset_peak()
    start = time.perf_counter()
    out = fn()
    return out, {"wall_s": time.perf_counter() - start, "peak_rss_mb": _peak_rss_mb(),
                 "end": _now()}


def products_of(n: int) -> tuple[str, ...]:
    if n == len(UNIVERSE):
        return tuple(UNIVERSE)
    if n == len(PHASE1_STANDIN):
        return PHASE1_STANDIN
    raise SystemExit(f"--products must be {len(UNIVERSE)} or {len(PHASE1_STANDIN)}")


def build_world(products: Sequence[str]) -> Any:
    from ml_route_v2.synthetic import synthetic_universe

    return synthetic_universe(products, EARLIEST_S_X, TRAIN_LAST, seed=SEED,
                              plant={"kind": "sign", "edge_cost_multiple": PROBE_EDGE_C},
                              warmup_dates=0, compact=True, eager_frames=False)


def time_one_split(panel: Any, adm: tuple, risk: Any, state_dir: Path, calendar: list) -> dict:
    """Every configuration over outer split 0's 4 inner folds plus its outer refit."""
    from ml_route_v2 import cpcv
    from ml_route_v2.configs import CONFIGS, ConfigLedger
    from ml_route_v2.pipeline import LEDGER_FILE, score_fn_for, split_risk_fn

    split_risk_table = split_risk_fn(panel)  # as the pipeline (D-04, C-02)
    ledger = ConfigLedger(state_dir / LEDGER_FILE)
    run = cpcv._prepare(panel, CONFIGS, score_fn_for(risk), ledger, state_dir / "cpcv",
                        adm or None, calendar, split_risk_table)
    one = dataclasses.replace(run, outer=run.outer[:1])
    rows = {h: int(d.X.shape[0]) for h, d in run.data.items()}
    _, fig = _timed(lambda: cpcv._compute_units(one, CONFIGS, score_fn_for(risk),
                                                with_inner=True, risk_fn=split_risk_table))
    return {**fig, "rows_by_horizon": rows, "n_features": len(panel.feature_cols),
            "n_configs": len(CONFIGS)}


def time_pieces(panel: Any, adm: tuple, n_dates: int) -> dict:
    from ml_route_v2.configs import lgbm_spec
    from ml_route_v2.cpcv import dsr_at_n, horizon_data, pbo_cscv
    from ml_route_v2.models import fit_model

    data = horizon_data(panel, "h60", adm or None)
    _, refit = _timed(lambda: fit_model(lgbm_spec(3), data.X, data.y))
    rng = np.random.default_rng(SEED)
    mat = rng.standard_normal((n_dates, 45))
    _, stats = _timed(lambda: (pbo_cscv(mat), dsr_at_n(mat[:, 0], 500, 0.01)))
    return {"final_refit_lgbm_d3_all_rows": refit, "pbo_dsr": stats,
            "rows_h60": int(data.X.shape[0])}


def standin_schedule(panel: Any, adm: tuple) -> Any:
    from ml_route_v2.configs import CONFIGS, ridge_spec
    from ml_route_v2.cpcv import horizon_data
    from ml_route_v2.decide import candidates
    from ml_route_v2.models import fit_model, predict

    cfg = next(c for c in CONFIGS if c.config_id == "ridge_l0.1_k1.5_h60")
    data = horizon_data(panel, "h60", adm or None)
    model = fit_model(ridge_spec(0.1), data.X, data.y)
    return candidates(data.rows, predict(model, data.X) * data.sigma, cfg)


def time_engine_and_payouts(engine: Any, sched: Any, risk: Any, payout_paths: int,
                            state_dir: Path, isolate: bool) -> dict:
    """ONE path through the engine stages from engine inputs alone (the world and the panel are
    already freed, V2.11 memory). Checkpoints go to probe_engine/ and probe_payouts/, apart from
    the pipeline's own engine/ and payouts/ files; the frames under engine/frames are shared."""
    from ml_route_v2.engine_stage import run_engine_paths, run_payout_paths

    sim, f_sim = _timed(lambda: run_engine_paths(engine, {0: sched}, risk, (0,),
                                                 state_dir / PROBE_ENGINE_DIR, isolate=isolate))
    _, f_pay = _timed(lambda: run_payout_paths(sim, payout_paths, state_dir / PROBE_PAYOUT_DIR))
    res = sim[0]
    return {"simulate_one_path": {**f_sim, "n_trips": res["n_trips"],
                                  "n_schedule": int(len(sched)), "isolated": isolate,
                                  "child_peak_rss_mb": res.get("engine_peak_rss_mb"),
                                  "minutes_processed": res.get("minutes_processed")},
            "payouts_one_path": {**f_pay, "n_calls": 8, "n_paths": payout_paths}}


def extrapolate(log: dict) -> dict:
    stages = log["stages"]
    split = log["one_split"]["wall_s"]
    pieces = log["pieces"]
    fixed = sum(stages[s]["wall_s"] for s in ("world", "panel", "filter", "gate0"))
    cpcv_s = N_OUTER_SPLITS * split
    final_s = pieces["final_refit_lgbm_d3_all_rows"]["wall_s"]
    stats_s = pieces["pbo_dsr"]["wall_s"]
    schedule_s = N_OUTER_SPLITS * final_s
    eng = log.get("engine_payouts")
    sim_s = N_PATHS * eng["simulate_one_path"]["wall_s"] if eng else float("nan")
    pay_s = N_PATHS * eng["payouts_one_path"]["wall_s"] if eng else float("nan")
    total = fixed + cpcv_s + final_s + stats_s + schedule_s + sim_s + pay_s
    return {"fixed_stages_s": fixed, "cpcv_s": cpcv_s, "final_s": final_s, "stats_s": stats_s,
            "schedule_s": schedule_s, "simulate_s": sim_s, "payouts_s": pay_s,
            "total_s": total, "total_min": total / 60.0}


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--products", type=int, required=True)
    ap.add_argument("--state-dir", type=Path, required=True)
    ap.add_argument("--full", action="store_true", help="run the full pipeline after the split")
    ap.add_argument("--force-full", action="store_true", help="ignore the 90-minute limit")
    ap.add_argument("--payout-paths", type=int, default=None)
    ap.add_argument("--isolate-paths", action=argparse.BooleanOptionalAction, default=None,
                    help="each engine path in its own process (default: the pipeline's)")
    args = ap.parse_args(argv)
    products_of(args.products)  # fail fast on an unknown size
    if args.payout_paths is not None and args.payout_paths < 1:
        ap.error("--payout-paths must be at least 1")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)

    from ml_route_v2.constants import PAYOUT_PATHS
    from ml_route_v2.engine_stage import prepare_engine
    from ml_route_v2.pipeline import (
        ENGINE_DIR,
        ISOLATE_ENGINE_PATHS,
        disk_mb,
        run_pipeline,
        stage_table,
    )

    state = args.state_dir
    state.mkdir(parents=True, exist_ok=True)
    log = _Log(state / "probe.json")
    payout_paths = args.payout_paths or PAYOUT_PATHS
    isolate = ISOLATE_ENGINE_PATHS if args.isolate_paths is None else args.isolate_paths
    products = products_of(args.products)
    log.put("machine", {"cpu_count": os.cpu_count(), "mem_available_mb_start": mem_available_mb(),
                        "nice": os.nice(0), "start": _now(), "products": list(products),
                        "openblas_threads": os.environ.get("OPENBLAS_NUM_THREADS")})
    world, f_world = _timed(lambda: build_world(products))
    stages = {"world": {**f_world, "n_bar_roots": len(world.bars),
                        "n_bars": int(sum(len(b) for b in world.bars.values())),
                        "n_calendar_dates": len(world.calendar)}}
    rep = run_pipeline(world, state_dir=state, force_after_gate0_fail=True, stop_after="gate0")
    for rec in rep.stages:
        stages[rec.name] = dataclasses.asdict(rec)
    stages["gate0"]["passed"] = bool(rep.results["gate0"]["verdict"].passed)
    stages["gate0"]["n_tests"] = int(rep.results["gate0"]["verdict"].n_tests)
    stages["panel"]["rows"] = int(len(rep.results["panel"].frame))
    # a restart (e.g. --full after a split-only run) keeps the first pass's measured figures
    log.put("stages" if "stages" not in log.data else "stages_restart", stages)
    panel, filt = rep.results["panel"], rep.results["filter"]
    adm, risk = filt["admissible"], filt["risk"]
    log.put("n_admissible_pairs", len(adm))
    if "one_split" not in log.data:
        log.put("one_split", {**time_one_split(panel, adm, risk, state, list(world.calendar)),
                              "disk_mb": disk_mb(state)})
    if "pieces" not in log.data:
        log.put("pieces", time_pieces(panel, adm, len(world.calendar)))
    if "engine_payouts" not in log.data:
        sched = standin_schedule(panel, adm)
        engine, f_frames = _timed(lambda: prepare_engine(world, {0: sched}, (0,),
                                                         state / ENGINE_DIR))
        # V2.11 memory: the engine runs with neither the bars nor the panel held
        world = panel = rep = None
        gc.collect()
        log.put("engine_payouts", {
            **time_engine_and_payouts(engine, sched, risk, payout_paths, state, isolate),
            "engine_frames": f_frames, "mem_available_mb_before_engine": mem_available_mb()})
    world = panel = rep = None
    gc.collect()
    est = extrapolate(log.data)
    log.put("extrapolated", est)
    if not args.full:
        log.put("end", _now())
        return 0
    if not args.force_full and est["total_min"] > FULL_RUN_LIMIT_MIN:
        log.put("full_run", f"skipped: extrapolated {est['total_min']:.0f} min > "
                            f"{FULL_RUN_LIMIT_MIN:.0f}")
        return 0
    # a fresh world the probe keeps no reference to, so the pipeline frees its bars before the
    # engine (V2.11 memory); deterministic, so it equals the first one
    rep = run_pipeline(build_world(products), state_dir=state, force_after_gate0_fail=True,
                       payout_paths=payout_paths, isolate_paths=isolate)
    log.put("full_run", {"stages": stage_table(rep).to_dict(orient="records"),
                         "stopped_at": rep.stopped_at, "disk_mb": disk_mb(state),
                         "end": _now(), "selected": list(rep.results["stats"]["selected"]),
                         "median_path_t": rep.results["stats"]["median_path_t"]})
    log.put("end", _now())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
