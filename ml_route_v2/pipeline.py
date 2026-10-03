"""The ML route v2 pipeline end to end on a synthetic world: resumable by stage, timed per stage.

docs/STAGE_E_ML_V2_DESIGN.md V2.2 (c/sigma filter), V2.2b (Gate 0 first; v2 stops when it fails),
V2.8 (the simulator), V2.9 (nested CPCV, PBO, DSR at N_total, final selection, payout simulation,
the training-window verdict's inputs) and V2.11 (per-stage wall time, peak memory and disk);
contract reports/stage_e11_interfaces.md section 8.

Stages, in order. Each writes state_dir/stages/<name>.pkl when it finishes and is loaded, not
recomputed, on a restart (Gate 0 family B and the CPCV are also resumable inside, per split and
per (configuration, split) unit). Every stage file, the CPCV and Gate 0 B state and the per-path
engine and payout checkpoints pin the constants fingerprint (fingerprint.constants_fingerprint,
code review C-01): state written under other constants is refused, never read back:
1. panel: input guard (``assert_bars_on_session_grid``: every bar of every root lies in an open
   interval of its group calendar and carries that interval's trade date); decision rows of the
   world's bar dates without each traded product's own roll-blackout dates (``own_blackout``:
   its root's and its price path's; V2.2 "Excluded dates", which replaces D4's union for v2: a
   signal leg's roll date drops no row); the SignalContext gets the full per-root blackout map
   (world.blackout), so signals.compute_signals makes every signal that reads a leg on its roll
   date not applicable there (signals/_core.py); sigma_X,d; targets; build_panel; then the rows
   on the training calendar (world.calendar) are kept (the earlier dates are warm-up history) and
   assert_window(train) runs.
2. filter: c_sigma_table and risk_table on the training rows (once, volatility only); the
   admissible (root, h) pairs.
3. gate0: families A and B on the admissible pairs, ledger-registered before computation; the
   verdict. A failure stops the run (V2.2b) unless ``force_after_gate0_fail``.
4. cpcv: nested_cpcv over ``configs`` with selection_metric.score_split, the admissible pairs and
   the training calendar. Every validation set is sized with the risk table of its own training
   rows (design review D-04: ``risk_fn`` = cost_filter.risk_table on the outer split's or the
   inner fold's training rows, ``split_risk_fn``: one row per (root, horizon) of the panel, NaN
   figures for a root with fewer than two training rows there, whose candidates are skipped as
   risk_unknown and counted in the unit record, code review C-02); the whole-window table from
   stage 2 (all six blocks) is the frozen model's.
5. stats: PBO (CSCV) on the configurations' path-averaged OOS matrix; the per-path daily t and the
   median-path t; the DSR of the path-averaged nested OOS daily series at N_total read from the
   ledger, with the Sharpe variance over the configurations' path-averaged OOS Sharpes (lead rule,
   the same matrix as PBO); the annualized Sharpe.
6. final: final_selection over the outer splits (it reuses the outer units) and the frozen
   refit's sha256; beside the nested median-path t, the final configuration's own CPCV OOS t and
   Sharpe from its column of the path-averaged OOS matrix (design review D-21: ``own_oos_t``,
   ``own_oos_sharpe_daily``, ``own_oos_sharpe_annual``).
7. schedule: the nested out-of-sample schedule per path. Each outer split's selected configuration
   is refit on that split's outer training rows (its sha256 must equal the CPCV record, so the
   schedule is the record's own model), predicts the split's test rows and goes through
   decide.candidates; path j takes block b's candidates from the split that path j assigns to b.
   Each candidate carries sigma_ticks and loss_ticks from the table of its own split's training
   rows (code review C-04, completing D-04), so the engine and the payout re-sizing size every
   trade from the split that produced it, never from the all-blocks table.
   Cost sensitivity (design review D-08b): the same predictions are re-scored with
   selection_metric.score_split at 1.0 x and COST_SENSITIVITY_SLIPPAGE_MULTIPLE (1.5) x slippage,
   with the split's own risk table, and assembled into the 5 paths. The 1.0 x record must equal
   the CPCV's nested OOS record (else PipelineError); ``cost_sensitivity`` gives the median-path
   t, the Sharpe and the daily mean at each multiple.
8. simulate: simulate.run_portfolio at 50K per path, engine frames cut to the training calendar
   (ml_route_v2/engine_stage.py, lead ruling 2026-10-03, FIX 3): before the engine starts the
   pipeline frees the panel and the world's bars; the traded vehicles' engine frames go to
   state_dir/engine/frames once, each path loads only its own vehicles' frames, and each path's
   summary is checkpointed as state_dir/engine/path_<j>.pkl (skipped on restart). With
   ``isolate_paths`` (the default, ISOLATE_ENGINE_PATHS; lead ruling 2026-10-03, design fix 9:
   measured at size A, 56% of memory combined versus 49% for one inline path, and five inline
   paths were never measured) each path runs in its own spawned process, one at a time; tests
   pass ``isolate_paths=False`` to run inline. The engine refuses entries per product on that
   product's own roll-blackout dates (simulate.PortfolioRules ``product_blackout``, V2.2).
   LABEL (code review C-11): this stage's record (``daily``, ``n_trips``, ``trips_by_root``) and
   its combined-MLL audit (``combined_breaches``) are the KILL SWITCHES OFF record: the member
   sizes at multiplier 1.0 and applies none of KS1-KS4 (only "no bar -> skip"); every path
   summary carries ``kill_switches: "off"``. The kill switches enter only in stage 9.
9. payouts: per path, payout_sim.simulate_payouts_pair at 50K and 150K, Standard and Consistency,
   DLL off and on; kill switches off except KS2's sizing (the verdict's reading, design review
   D-01) and on (context) from one draw; checkpointed per path as
   state_dir/payouts/path_<j>.pkl. Criterion 7 reads ``ruin_prob`` of the ``verdict_reading``
   rows: ruin = the MLL breached or D <= 0.25 x MLL at a close; ``breach_only_prob`` is beside
   it. Every row carries ``n_trips`` (the path's engine trips) and ``empty_schedule``; a path whose
   schedule was empty has one row per (account, path type, DLL, ks) with n_trips 0, NaN figures
   and ``empty_schedule`` True (code review C-03), so no path drops out of the table unseen.
Reading (reported to the lead): the payout and engine figures come from the nested OOS schedule
(V2.9 "Payout simulation ... from the nested OOS daily records"), not from the frozen refit, whose
in-sample schedule would not be a test.

Timing: wall seconds per stage; peak RSS per stage from /proc/self/status VmHWM after resetting it
through /proc/self/clear_refs (Linux), else resource.getrusage's process peak; disk = the bytes
under state_dir after the stage.
"""

from __future__ import annotations

import dataclasses
import functools
import gc
import os
import pickle
import resource
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ml_route_v2.configs import CONFIGS, Config, ConfigLedger
from ml_route_v2.constants import (
    COST_SENSITIVITY_SLIPPAGE_MULTIPLE,
    N_PROGRAM_AT_FREEZE,
    PAYOUT_PATHS,
    UNIVERSE,
)

STAGES = ("panel", "filter", "gate0", "cpcv", "stats", "final", "schedule", "simulate",
          "payouts")
LEDGER_FILE = "ledger.jsonl"
ENGINE_DIR = "engine"  # engine frames and per-path simulate checkpoints (engine_stage.py)
PAYOUT_DIR = "payouts"  # per-path payout checkpoints
ISOLATE_ENGINE_PATHS = True  # default of run_pipeline(isolate_paths=...): one process per path
TRADE_DATES_PER_YEAR = 252
STAGE_FILE_KEYS = ("constants", "out")  # a stage file: the constants fingerprint, the output


class PipelineError(RuntimeError):
    """A pipeline input or stage result is unusable."""


class BarGridError(PipelineError):
    """A bar lies outside its group's open intervals or carries another trade date."""


@dataclass(frozen=True)
class StageRecord:
    name: str
    status: str  # "computed" | "loaded"
    wall_s: float
    peak_rss_mb: float | None
    disk_mb: float


@dataclass(frozen=True)
class PipelineReport:
    state_dir: Path
    stages: tuple[StageRecord, ...]
    stopped_at: str | None  # None: every stage ran; "gate0": V2.2b stop; "after:<stage>"
    results: Mapping[str, Any] = field(default_factory=dict)  # stage name -> its output

    def status(self, name: str) -> str | None:
        return next((s.status for s in self.stages if s.name == name), None)


# ------------------------------------------------------------------ timing ----
def _reset_peak() -> bool:
    try:
        with open("/proc/self/clear_refs", "w", encoding="ascii") as fh:
            fh.write("5")
        return True
    except OSError:
        return False


def _peak_rss_mb() -> float:
    try:
        with open("/proc/self/status", encoding="ascii") as fh:
            for line in fh:
                if line.startswith("VmHWM:"):
                    return int(line.split()[1]) / 1024.0
    except OSError:
        pass
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def disk_mb(path: Path) -> float:
    total = 0
    for root, _dirs, files in os.walk(path):
        for f in files:
            try:
                total += (Path(root) / f).stat().st_size
            except OSError:
                continue
    return total / 2**20


def _save(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with tmp.open("wb") as fh:
        pickle.dump(obj, fh, protocol=pickle.HIGHEST_PROTOCOL)
    tmp.replace(path)


def _load(path: Path) -> Any:
    with path.open("rb") as fh:
        return pickle.load(fh)  # noqa: S301 - the pipeline's own state files


def _read_stage(path: Path, constants_fp: str) -> Any:
    """A stage file's output; refused when it is not {"constants", "out"} or was written under
    other constants (code review C-01)."""
    saved = _load(path)
    if not isinstance(saved, dict) or tuple(saved) != STAGE_FILE_KEYS:
        raise PipelineError(f"{path} is not a stage file of this pipeline version; delete it")
    if saved["constants"] != constants_fp:
        raise PipelineError(f"{path} was written under other constants (constants fingerprint "
                            "mismatch); use a new state_dir or delete it to recompute")
    return saved["out"]


class _Stages:
    """Runs a stage or loads its saved output; records timing. Every stage file pins the
    constants fingerprint taken when the pipeline starts (code review C-01)."""

    def __init__(self, state_dir: Path, timing: bool) -> None:
        from ml_route_v2.fingerprint import constants_fingerprint

        self.dir = state_dir
        self.timing = timing
        self.constants = constants_fingerprint()
        self.records: list[StageRecord] = []
        self.results: dict[str, Any] = {}

    def run(self, name: str, fn: Callable[[], Any]) -> Any:
        path = self.dir / "stages" / f"{name}.pkl"
        start = time.perf_counter()
        measured = self.timing and _reset_peak()
        if path.exists():
            out, status = _read_stage(path, self.constants), "loaded"
        else:
            out, status = fn(), "computed"
            _save(path, {"constants": self.constants, "out": out})
        peak = _peak_rss_mb() if self.timing else None
        if self.timing and not measured:
            peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
        self.records.append(StageRecord(name, status, time.perf_counter() - start, peak,
                                        disk_mb(self.dir)))
        self.results[name] = out
        return out


# ------------------------------------------------------------------ guards ----
def assert_bars_on_session_grid(bars: Mapping[str, pd.DataFrame]) -> None:
    """Every bar opens inside an open interval of its root's group calendar and carries that
    interval's trade date (catches a series whose timestamps are shifted off the clock, V2.9)."""
    from data.group_session import assign_trade_dates, group_of, open_intervals
    from ml_route.inputs import _group_calendar

    for root, frame in bars.items():
        ts = frame["ts_event"].to_numpy(np.int64)
        if len(ts) == 0:
            continue
        labels = pd.to_datetime(frame["trade_date"].astype(str)).to_numpy("datetime64[D]")
        first, last = labels.min().astype(object), labels.max().astype(object)
        opened = open_intervals(_group_calendar(group_of(root)), first, last)
        got = assign_trade_dates(opened, ts)
        outside = int(got.in_closure.sum())
        relabelled = int((got.days != labels).sum())
        if outside or relabelled:
            raise BarGridError(f"{root}: {outside} bars outside the open intervals, "
                               f"{relabelled} with another trade date (first at "
                               f"{int(ts[np.argmax(got.in_closure | (got.days != labels))])})")


# ------------------------------------------------------------------ stage bodies ----
def own_blackout(blackout: Mapping[str, frozenset[date]],
                 vehicles: Sequence[str]) -> dict[str, frozenset[date]]:
    """V2.2: each traded product's own roll-blackout dates, its root's and its price path's
    (clock.exclude_union with the path as the only leg); the decision rows' exclude map."""
    from ml_route_v2.clock import exclude_union

    return exclude_union(blackout, {v: (UNIVERSE[v][1],) for v in vehicles})


def build_world_panel(world: Any, *, check_grid: bool = True,
                      signals: Sequence[str] | None = None) -> Any:
    """Stage 1 (module docstring): the training panel of a synthetic world (or of phase 1's real
    world, ml_route_v2/phase1). ``signals``: the panel's signals (None: all of REGISTRY; phase 1
    passes the covered ones, Stage E.12 lead rule P-1)."""
    from ml_route_v2.clock import decision_rows, trade_dates_of
    from ml_route_v2.panel import assert_window, build_panel
    from ml_route_v2.signals import SignalContext
    from ml_route_v2.targets import build_targets, sigma_d

    if check_grid:
        assert_bars_on_session_grid(world.bars)
    vs = tuple(world.vehicles)
    rows = decision_rows(vs, {v: trade_dates_of(world.bars[UNIVERSE[v][1]]) for v in vs},
                         exclude=own_blackout(world.blackout, vs))
    ctx = SignalContext(rows, world.bars, world.releases, sigma_d(rows, world.bars),
                        blackout=world.blackout)
    targets = build_targets(rows, world.bars, releases=world.releases, costs=world.costs)
    panel = build_panel(ctx, targets, mode="train", signals=signals)
    keep = pd.to_datetime(panel.frame["trade_date"]).dt.date.isin(set(world.calendar))
    keep = keep.to_numpy()
    counts = dict(panel.counts)
    counts["rows_warmup_dropped"] = int((~keep).sum())
    counts["rows_training"] = int(keep.sum())
    out = dataclasses.replace(panel, frame=panel.frame.loc[keep],
                              avail_max_ts_ns=panel.avail_max_ts_ns[keep], counts=counts)
    assert_window(out, "train")
    if len(out.frame) == 0:
        raise PipelineError("the training panel is empty")
    return out


def _filter(panel: Any) -> dict:
    from ml_route_v2.cost_filter import c_sigma_table, risk_table

    table = c_sigma_table(panel)
    adm = table.loc[table["admissible"], ["root", "horizon"]]
    return {"c_sigma": table, "risk": risk_table(panel),
            "admissible": tuple((str(r), str(h)) for r, h in adm.itertuples(index=False))}


def admissible_ok_panel(panel: Any, admissible: Sequence[tuple[str, str]]) -> Any:
    """The panel with ok_<h> False on rows whose (root, h) pair is not admissible (a copy)."""
    from ml_route_v2.constants import HORIZONS

    frame = panel.frame.copy()
    roots = frame["root"].to_numpy(object)
    for h in HORIZONS:
        col = f"ok_{h}"
        if col in frame.columns:
            keep = np.isin(roots, [r for r, hh in admissible if hh == h])
            frame[col] = frame[col].to_numpy(dtype=bool) & keep
    return dataclasses.replace(panel, frame=frame)


def _gate0(panel: Any, admissible: tuple, ledger: ConfigLedger, state_dir: Path,
           calendar: Sequence[date]) -> dict:
    from ml_route_v2.gate0 import (
        gate0_b_pooled,
        gate0_b_trades,
        gate0_family_a,
        gate0_family_b,
        gate0_verdict,
    )

    adm = admissible if admissible else None
    # The designed call (bug G0-1 fixed in gate0._family_a_horizon); admissible_ok_panel stays as
    # the test's reference for the same rows.
    tests_a = gate0_family_a(panel, ledger=ledger, admissible=adm) if admissible else []
    tests_b = (gate0_family_b(panel, ledger=ledger, state_dir=state_dir, admissible=adm,
                              calendar=calendar) if admissible else [])
    verdict = gate0_verdict([*tests_a, *tests_b])
    pooled = None
    if admissible:
        trades = gate0_b_trades(panel, ledger=ledger, state_dir=state_dir, admissible=adm,
                                calendar=calendar)
        pooled = gate0_b_pooled(trades) if len(trades) else None
    return {"tests": tuple([*tests_a, *tests_b]), "verdict": verdict, "pooled_b": pooled,
            "n_a": len(tests_a), "n_b": len(tests_b)}


def score_fn_for(risk: pd.DataFrame) -> Callable:
    from ml_route_v2.selection_metric import score_split

    return functools.partial(score_split, risk=risk)


def split_risk_fn(panel: Any) -> Callable:
    """D-04's per-split risk table (cost_filter.risk_table on a split's training rows) with a row
    for every (root, horizon) of the panel: a root with no or one training row in the split gets
    NaN figures, so its candidates are skipped as risk_unknown and counted (code review C-02)
    rather than missing from the table, which stays an error."""
    from ml_route_v2.cost_filter import risk_table

    roots = tuple(sorted(map(str, pd.unique(panel.frame["root"]))))
    return functools.partial(risk_table, roots=roots)


def _daily_t(xs: np.ndarray) -> float:
    xs = np.asarray(xs, dtype=np.float64)
    if xs.size < 2:
        return float("nan")
    sd = float(np.std(xs, ddof=1))
    return float(np.mean(xs) / (sd / np.sqrt(xs.size))) if sd > 0 else 0.0


def _sharpe_daily(xs: np.ndarray) -> float:
    sd = float(np.std(xs, ddof=1)) if xs.size > 1 else 0.0
    return float(np.mean(xs) / sd) if sd > 0 else 0.0


def record_figures(path_daily: pd.DataFrame) -> dict:
    """A nested OOS record's (dates x paths) per-path daily t, median-path t, the path-averaged
    daily Sharpe (ddof 1; annualized x sqrt(252)) and daily mean."""
    path_t = [_daily_t(path_daily[c].to_numpy()) for c in path_daily.columns]
    avg = path_daily.mean(axis=1).to_numpy()
    sharpe = _sharpe_daily(avg)
    return {"path_t": path_t, "median_path_t": float(np.median(path_t)),
            "sharpe_daily": sharpe, "sharpe_annual": sharpe * float(np.sqrt(TRADE_DATES_PER_YEAR)),
            "daily_mean": float(np.mean(avg)) if avg.size else float("nan")}


def _stats(nested: Any, ledger: ConfigLedger, n_program: int) -> dict:
    from ml_route_v2.cpcv import CPCVError, dsr_at_n, pbo_cscv, sharpe_variance

    path_daily: pd.DataFrame = nested.path_daily
    path_t = [_daily_t(path_daily[c].to_numpy()) for c in path_daily.columns]
    avg = path_daily.mean(axis=1).to_numpy()
    sharpes = nested.config_sharpes.to_numpy(dtype=np.float64)
    finite = sharpes[np.isfinite(sharpes)]
    n_total = ledger.n_total(n_program)
    try:
        pbo = pbo_cscv(nested.config_daily.to_numpy())
    except CPCVError as exc:
        pbo = {"pbo": float("nan"), "error": str(exc)}
    try:
        dsr = dsr_at_n(avg, n_total, sharpe_variance(finite)) if finite.size else {
            "status": "undefined", "reason": "no finite configuration Sharpe"}
    except CPCVError as exc:
        dsr = {"status": "undefined", "reason": str(exc)}
    sd = float(np.std(avg, ddof=1)) if avg.size > 1 else 0.0
    return {"path_t": path_t, "median_path_t": float(np.median(path_t)),
            "pbo": pbo, "dsr": dsr, "n_total": n_total, "n_program": n_program,
            "n_registered": ledger.n_registered(),
            "sharpe_daily": float(np.mean(avg) / sd) if sd > 0 else 0.0,
            "sharpe_annual": float(np.mean(avg) / sd * np.sqrt(TRADE_DATES_PER_YEAR))
            if sd > 0 else 0.0,
            "n_dates": int(avg.size), "selected": nested.selected}


def assemble_record(nested: Any, daily_by_split: Mapping[int, pd.Series]) -> pd.DataFrame:
    """Dates x paths: path j's block b from the daily series of the split path j assigns to b,
    0 on dates without one (cpcv's nested OOS assembly)."""
    index = pd.Index([d for block in nested.blocks for d in block], name="trade_date")
    lookup = {s: {pd.Timestamp(k).date(): float(v) for k, v in daily.items()}
              for s, daily in daily_by_split.items()}
    cols = {}
    for j, path in enumerate(nested.paths):
        vals: list[float] = []
        for b, block in enumerate(nested.blocks):
            got = lookup.get(path[b], {})
            vals.extend(got.get(d, 0.0) for d in block)
        cols[j] = vals
    return pd.DataFrame(cols, index=index)


COST_CHECK_TOL_USD = 1e-6  # the 1.0 x re-score must reproduce the CPCV record to this


def _nested_schedule(panel: Any, nested: Any, configs: Sequence[Config], admissible: tuple,
                     risk: pd.DataFrame | None = None, risk_fn: Callable | None = None,
                     multiples: Sequence[float] = (1.0, COST_SENSITIVITY_SLIPPAGE_MULTIPLE)
                     ) -> dict:
    """Stage 7 (module docstring): candidates per path from the nested OOS models, each row
    carrying sigma_ticks and loss_ticks of its own split's training-row table (C-04), and the
    record re-priced at each slippage multiple (D-08b) with the split's own risk table (D-04)."""
    from ml_route_v2.cpcv import horizon_data, split_masks
    from ml_route_v2.decide import CANDIDATE_COLUMNS, candidates
    from ml_route_v2.models import fit_model, predict
    from ml_route_v2.portfolio import join_risk
    from ml_route_v2.selection_metric import score_split

    by_id = {c.config_id: c for c in configs}
    adm = admissible if admissible else None
    per_split: dict[int, pd.DataFrame] = {}
    daily_by_m: dict[float, dict[int, pd.Series]] = {float(m): {} for m in multiples}
    data_cache: dict[str, Any] = {}
    for split, cid, sha in zip(nested.splits, nested.selected, nested.selected_sha256,
                               strict=True):
        if cid is None:
            continue
        cfg = by_id[cid]
        if cfg.horizon not in data_cache:
            data_cache[cfg.horizon] = horizon_data(panel, cfg.horizon, adm)
        data = data_cache[cfg.horizon]
        train, test = split_masks(split, data.days, data.t_ns, data.x_ns)
        model = fit_model(cfg.model, data.X[train], data.y[train])
        if model.sha256 != sha:
            raise PipelineError(f"split {split.index}: refit sha256 {model.sha256[:12]} differs "
                                f"from the CPCV record {str(sha)[:12]}")
        r_hat = predict(model, data.X[test]) * data.sigma[test]
        rows = data.rows.iloc[np.flatnonzero(test)]
        cands = candidates(rows, r_hat, cfg)
        if risk is None and risk_fn is None:
            per_split[split.index] = cands
            continue
        table = risk_fn(data.rows.iloc[np.flatnonzero(train)]) if risk_fn is not None else risk
        per_split[split.index] = join_risk(cands, table)  # C-04: the split's own sigma, loss
        for m in daily_by_m:
            daily_by_m[m][split.index] = score_split(rows, r_hat, cfg, risk=table,
                                                     slippage_multiple=m).daily
    cols = list(CANDIDATE_COLUMNS)
    if risk is not None or risk_fn is not None:
        cols += ["sigma_ticks", "loss_ticks"]
    empty = pd.DataFrame(columns=cols)
    paths = {}
    for j, path in enumerate(nested.paths):
        parts = []
        for b, block in enumerate(nested.blocks):
            cand = per_split.get(path[b])
            if cand is None or not len(cand):
                continue
            days = pd.to_datetime(cand["trade_date"]).dt.date
            parts.append(cand.loc[days.isin(set(block)).to_numpy()])
        sched = pd.concat(parts, ignore_index=True) if parts else empty.copy()
        if len(sched):
            sched = sched.sort_values(["decision_ts_ns", "edge_over_cost", "root"],
                                      ascending=[True, False, True], kind="mergesort")
        paths[j] = sched.reset_index(drop=True)
    out = {"paths": paths, "n_per_split": {s: len(c) for s, c in per_split.items()}}
    if risk is None and risk_fn is None:
        return out
    records = {m: assemble_record(nested, d) for m, d in daily_by_m.items()}
    if 1.0 in records:
        diff = float(np.max(np.abs(records[1.0].to_numpy() - nested.path_daily.to_numpy()),
                            initial=0.0))
        if not diff <= COST_CHECK_TOL_USD:
            raise PipelineError(f"the 1.0 x re-score differs from the nested OOS record by "
                                f"${diff:.6g}")
        out["cost_check_max_abs_diff"] = diff
    out["path_daily_by_multiple"] = records
    out["cost_sensitivity"] = {m: record_figures(r) for m, r in records.items()}
    return out


def _simulate_stage(held: dict, schedules: Mapping[int, pd.DataFrame], risk: pd.DataFrame,
                    paths: Sequence[int], state_dir: Path, isolate: bool) -> dict:
    """Stage 8 (module docstring): the traded vehicles' engine frames to disk, then the pipeline's
    last reference to the world (its bars) is dropped, then the engine per path."""
    from ml_route_v2.engine_stage import prepare_engine, run_engine_paths

    engine = prepare_engine(held["world"], schedules, paths, state_dir / ENGINE_DIR)
    held.clear()
    gc.collect()
    return run_engine_paths(engine, schedules, risk, paths, state_dir / ENGINE_DIR,
                            isolate=isolate)


def _payouts_stage(sim: Mapping[int, dict], n_paths: int, state_dir: Path) -> pd.DataFrame:
    """Stage 9 (module docstring), one checkpoint file per path."""
    from ml_route_v2.engine_stage import run_payout_paths

    return run_payout_paths(sim, n_paths, state_dir / PAYOUT_DIR)


# ------------------------------------------------------------------ the pipeline ----
def run_pipeline(world: Any, *, state_dir: Path, configs: Sequence[Config] = CONFIGS,
                 timing: bool = True, force_after_gate0_fail: bool = False,
                 stop_after: str | None = None, paths: Sequence[int] | None = None,
                 payout_paths: int = PAYOUT_PATHS,
                 n_program: int = N_PROGRAM_AT_FREEZE,
                 isolate_paths: bool = ISOLATE_ENGINE_PATHS) -> PipelineReport:
    """panel -> filter -> Gate 0 -> nested CPCV -> stats -> final -> schedule -> simulate ->
    payouts (module docstring); resumable from state_dir. ``isolate_paths``: each engine path in
    its own process. Memory (V2.11): the pipeline holds ``world`` in one place and drops it, and
    the panel, before the engine starts; the bars are freed only when the caller keeps no other
    reference (probe.py passes a world it does not keep). A report that reaches simulate has no
    "panel" result (it is on disk, stages/panel.pkl)."""
    from ml_route_v2.cpcv import final_selection, nested_cpcv

    if stop_after is not None and stop_after not in STAGES:
        raise PipelineError(f"stop_after {stop_after!r} not in {STAGES}")
    state_dir = Path(state_dir)
    state_dir.mkdir(parents=True, exist_ok=True)
    ledger = ConfigLedger(state_dir / LEDGER_FILE)
    st = _Stages(state_dir, timing)
    configs = tuple(configs)

    def done(name: str) -> PipelineReport | None:
        if stop_after == name:
            return PipelineReport(state_dir, tuple(st.records), f"after:{name}", st.results)
        return None

    held = {"world": world}  # the pipeline's only reference from here (V2.11 memory)
    del world
    panel = st.run("panel", lambda: build_world_panel(held["world"]))
    if (r := done("panel")) is not None:
        return r
    filt = st.run("filter", lambda: _filter(panel))
    if (r := done("filter")) is not None:
        return r
    adm = filt["admissible"]
    calendar = list(held["world"].calendar)
    g0 = st.run("gate0", lambda: _gate0(panel, adm, ledger, state_dir / "gate0", calendar))
    if (r := done("gate0")) is not None:
        return r
    if not g0["verdict"].passed and not force_after_gate0_fail:
        return PipelineReport(state_dir, tuple(st.records), "gate0", st.results)
    score = score_fn_for(filt["risk"])
    split_risk_table = split_risk_fn(panel)  # D-04, per split (C-02: every root listed)
    nested = st.run("cpcv", lambda: nested_cpcv(
        panel, configs, score, ledger=ledger, state_dir=state_dir / "cpcv",
        admissible=adm or None, calendar=calendar, risk_fn=split_risk_table))
    if (r := done("cpcv")) is not None:
        return r
    stats = st.run("stats", lambda: _stats(nested, ledger, n_program))
    if (r := done("stats")) is not None:
        return r
    final = st.run("final", lambda s=stats: _final(final_selection(
        panel, configs, score, ledger=ledger, state_dir=state_dir / "cpcv",
        admissible=adm or None, calendar=calendar, risk_fn=split_risk_table), nested, s))
    if (r := done("final")) is not None:
        return r
    sched = st.run("schedule", lambda: _nested_schedule(panel, nested, configs, adm,
                                                        filt["risk"], split_risk_table))
    if (r := done("schedule")) is not None:
        return r
    run_paths = tuple(range(len(nested.paths))) if paths is None else tuple(paths)
    # V2.11 memory: the engine needs neither the panel nor the bars (the stage drops the world)
    panel = None  # noqa: F841 - releases the frame (the closures above are spent)
    st.results.pop("panel", None)
    gc.collect()
    sim = st.run("simulate", lambda: _simulate_stage(held, sched["paths"], filt["risk"],
                                                     run_paths, state_dir, isolate_paths))
    if (r := done("simulate")) is not None:
        return r
    st.run("payouts", lambda: _payouts_stage(sim, payout_paths, state_dir))
    del stats, final
    return PipelineReport(state_dir, tuple(st.records), None, st.results)


def _final(res: Any, nested: Any = None, stats: Mapping | None = None) -> dict:
    """Stage 6's record; with ``nested``, the final configuration's own CPCV OOS t and Sharpe
    from its column of the path-averaged OOS matrix, beside the nested median-path t (D-21)."""
    out = {"config": res.config, "table": res.table, "n_train_rows": res.n_train_rows,
           "sha256": res.model.sha256 if res.model is not None else None,
           "payload": res.model.payload if res.model is not None else None}
    if nested is None:
        return out
    nan = float("nan")
    own = {"own_oos_t": nan, "own_oos_sharpe_daily": nan, "own_oos_sharpe_annual": nan}
    cid = res.config.config_id if res.config is not None else None
    if cid is not None and cid in nested.config_daily.columns:
        col = nested.config_daily[cid].to_numpy(dtype=np.float64)
        sharpe = _sharpe_daily(col)
        own = {"own_oos_t": _daily_t(col), "own_oos_sharpe_daily": sharpe,
               "own_oos_sharpe_annual": sharpe * float(np.sqrt(TRADE_DATES_PER_YEAR))}
    median_t = float(stats["median_path_t"]) if stats is not None else nan
    return {**out, **own, "nested_median_path_t": median_t}


def stage_table(report: PipelineReport) -> pd.DataFrame:
    """One row per stage: status, wall seconds, peak RSS MB, disk MB."""
    return pd.DataFrame([dataclasses.asdict(s) for s in report.stages])


__all__ = [
    "ENGINE_DIR", "LEDGER_FILE", "PAYOUT_DIR", "STAGES", "BarGridError", "PipelineError",
    "PipelineReport", "StageRecord", "assert_bars_on_session_grid", "build_world_panel",
    "assemble_record", "disk_mb", "own_blackout", "record_figures", "run_pipeline",
    "score_fn_for", "split_risk_fn", "stage_table",
]
