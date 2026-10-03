"""The engine stages of the ML route v2 pipeline (simulate and payouts): engine frames on disk,
per-path checkpoints and, optionally, one process per path.

docs/STAGE_E_ML_V2_DESIGN.md V2.8 (the simulator), V2.9 (payout simulation), V2.11 and V12 (memory,
8-to-10-hour windows, checkpoints); lead ruling 2026-10-03 (Stage E.11 FIX 3): the size-A probe's
simulate stage peaked at 7.2 GB, 73% of the memory available at launch, over CLAUDE.md's 70% rule,
because the process still held every root's bars while the engine ran.

- ``prepare_engine``: the engine frame of every vehicle traded on the run's paths, cut to the
  training calendar, is written once to <dir>/frames/<root>.pkl, one vehicle at a time (skipped
  when present; frames/meta.pkl pins the world, and another world's frames raise). The returned
  ``EngineInputs`` holds only the engine's rule inputs (releases, the roll-blackout union, each
  vehicle's own roll-blackout set, the window dates) and the frame directory. The engine refuses
  an entry in a product only on that product's own roll-blackout dates (pipeline.own_blackout:
  its root's and its price path's; simulate.PortfolioRules ``product_blackout``, V2.2, lead
  ruling 2026-10-03, design fix 8). From then on the simulate stage needs nothing of the bars or the
  panel, and the pipeline drops its references to both before the engine starts.
- ``run_engine_paths``: per path, the engine runs on the frames of that path's traded vehicles
  only, loaded from disk. The path's summary goes to <dir>/path_<j>.pkl as soon as the path
  finishes, and a restart skips it. A fingerprint of the schedule, the risk table, the engine
  inputs and the constants (fingerprint.constants_fingerprint, code review C-01) is stored with
  it; a file written for other inputs raises PipelineError. With
  ``isolate``, each path runs in its own process (multiprocessing spawn, one at a time), so all of
  its memory returns to the system before the next path; the child's peak RSS is kept in the
  summary (``engine_peak_rss_mb``). LABEL (code review C-11): a path summary is the KILL
  SWITCHES OFF record, ``kill_switches: "off"`` (ENGINE_KILL_SWITCHES): its ``daily``,
  ``n_trips`` and ``trips_by_root`` come from a member that sizes at multiplier 1.0 and applies
  none of KS1-KS4 (only "no bar -> skip"), and its combined-MLL audit (``combined_breaches``)
  reads that same run. The kill switches enter only in the payout re-sizing.
- ``run_payout_paths``: per path, payout_sim.simulate_payouts_pair at 50K and 150K, Standard and
  Consistency, DLL off and on, kill switches off except KS2's sizing (the verdict's reading,
  design review D-01) and on from one draw;
  written to <payout dir>/path_<j>.pkl per path and skipped on restart (fingerprint: the path's
  day records, the draw count and the constants fingerprint). Every row carries ``n_trips`` and
  ``empty_schedule``. A path with no day records (an empty schedule: every selected
  configuration's cost gate passed nothing on its blocks) gets one row per (account, path type,
  DLL, ks) with n_trips 0, NaN figures and ``empty_schedule`` True (code review C-03), so an
  average over the ``path`` column shows the missing path instead of silently skipping it.
"""

from __future__ import annotations

import dataclasses
import hashlib
import multiprocessing
import pickle
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from multiprocessing.reduction import ForkingPickler
from pathlib import Path
from types import MappingProxyType
from typing import Any

import pandas as pd

from ml_route_v2.fingerprint import constants_fingerprint
from ml_route_v2.pipeline import PipelineError, _load, _peak_rss_mb, _save

FRAMES_SUBDIR = "frames"
FRAMES_META = "meta.pkl"
CHECKPOINT_KEYS = ("fingerprint", "out")
ENGINE_KILL_SWITCHES = "off"  # C-11: the engine record and its combined-MLL audit


def _mappingproxy(data: dict) -> MappingProxyType:
    return MappingProxyType(data)


def _reduce_mappingproxy(m: MappingProxyType) -> tuple:
    return _mappingproxy, (dict(m),)


# The release calendar holds read-only mappings, which pickle refuses; the spawn child of an
# isolated path receives them as copies (multiprocessing's pickler only, nothing else changes).
ForkingPickler.register(MappingProxyType, _reduce_mappingproxy)


@dataclass(frozen=True)
class EngineInputs:
    """What the engine needs besides a path's schedule and the risk table (module docstring)."""
    frame_dir: Path
    releases: Any  # the world's release calendar (screening.stage_e_rules.ReleaseCalendar)
    blackout: frozenset[date]  # StageERules.blackout: the traded legs' roll-blackout union (D4)
    window_dates: frozenset[date]  # the training calendar
    world_fp: str  # sha256 of the frames' meta (vehicles, calendar, seed)
    # vehicle -> its own roll-blackout dates (V2.2); None: the union above for every product
    product_blackout: Mapping[str, frozenset[date]] | None = None


# ------------------------------------------------------------------ fingerprints ----
def frame_fingerprint(*objs: pd.DataFrame | pd.Series) -> str:
    """sha256 over the columns and pandas' row hashes of each frame or series."""
    h = hashlib.sha256()
    for obj in objs:
        cols = tuple(obj.columns) if isinstance(obj, pd.DataFrame) else (obj.name,)
        h.update(repr(cols).encode())
        h.update(pd.util.hash_pandas_object(obj, index=True).to_numpy().tobytes())
    return h.hexdigest()


def _world_meta(world: Any) -> dict:
    cal = tuple(world.calendar)
    return {"vehicles": tuple(world.vehicles),
            "calendar": (cal[0], cal[-1], len(cal)) if cal else None,
            "seed": getattr(world, "seed", None),
            "plant": repr(getattr(world, "plant", None))}


def _path_fingerprint(engine: EngineInputs, sched: pd.DataFrame, risk: pd.DataFrame) -> str:
    h = hashlib.sha256()
    h.update(constants_fingerprint().encode())  # code review C-01
    h.update(frame_fingerprint(sched, risk).encode())
    h.update(engine.world_fp.encode())
    h.update(repr(sorted(engine.blackout)).encode())
    if engine.product_blackout is not None:
        h.update(repr(sorted((r, sorted(d)) for r, d in engine.product_blackout.items()))
                 .encode())
    return h.hexdigest()


def _read_checkpoint(path: Path, fingerprint: str) -> Any:
    saved = _load(path)
    if not isinstance(saved, dict) or tuple(saved) != CHECKPOINT_KEYS:
        raise PipelineError(f"{path} is not a per-path checkpoint")
    if saved["fingerprint"] != fingerprint:
        raise PipelineError(f"{path} was written for other inputs (fingerprint mismatch); "
                            "delete it to recompute that path")
    return saved["out"]


def _checkpointed(path: Path, fingerprint: str, compute: Callable[[], Any]) -> Any:
    if not path.exists():
        _save(path, {"fingerprint": fingerprint, "out": compute()})
    return _read_checkpoint(path, fingerprint)


# ------------------------------------------------------------------ engine inputs ----
def traded_roots(schedules: Mapping[int, pd.DataFrame], paths: Sequence[int]) -> tuple[str, ...]:
    return tuple(sorted({str(r) for j in paths for r in schedules[j]["root"]}))


def prepare_engine(world: Any, schedules: Mapping[int, pd.DataFrame], paths: Sequence[int],
                   engine_dir: Path) -> EngineInputs:
    """Engine frames of the traded vehicles to <engine_dir>/frames (module docstring)."""
    frame_dir = Path(engine_dir) / FRAMES_SUBDIR
    meta = _world_meta(world)
    meta_path = frame_dir / FRAMES_META
    if meta_path.exists():
        if _load(meta_path) != meta:
            raise PipelineError(f"{frame_dir} holds the engine frames of another world; delete it")
    else:
        _save(meta_path, meta)
    from ml_route_v2.pipeline import own_blackout

    calendar = tuple(world.calendar)
    for root in traded_roots(schedules, paths):
        path = frame_dir / f"{root}.pkl"
        if not path.exists():
            _save(path, world.engine_frames([root], calendar)[root])
    own = own_blackout(world.blackout, tuple(world.vehicles))
    return EngineInputs(frame_dir, world.releases, frozenset(world.engine_blackout()),
                        frozenset(calendar), hashlib.sha256(pickle.dumps(meta)).hexdigest(),
                        {str(r): frozenset(d) for r, d in own.items()})


# ------------------------------------------------------------------ one path ----
def _empty_path() -> dict:
    return {"days": (), "daily": pd.Series(dtype=float), "n_trips": 0, "trips_by_root": {},
            "combined_breaches": 0, "engine_breaches": 0,
            "kill_switches": ENGINE_KILL_SWITCHES}


def run_engine_path(engine: EngineInputs, sched: pd.DataFrame, risk: pd.DataFrame) -> dict:
    """One path through simulate.run_portfolio at 50K on its traded vehicles' frames only: the
    kill-switches-off record and its combined-MLL audit (module docstring, C-11)."""
    from ml_route_v2.simulate import run_portfolio

    if not len(sched):
        return _empty_path()
    roots = sorted({str(r) for r in sched["root"]})
    frames = {r: _load(engine.frame_dir / f"{r}.pkl") for r in roots}
    kw = {"releases": engine.releases, "blackout": engine.blackout,
          "window_dates": set(engine.window_dates)}
    if engine.product_blackout is not None:
        kw["product_blackout"] = {r: engine.product_blackout[r] for r in roots}
    run = run_portfolio(frames, sched, risk, rules_kwargs=kw)
    roots_traded = pd.Series([t.root for d in run.days for t in d.trades], dtype=object)
    return {"days": run.days, "daily": run.daily, "n_trips": len(run.trips),
            "trips_by_root": roots_traded.value_counts().to_dict(),
            "combined_breaches": len(run.combined_mll_breaches),
            "engine_breaches": int(run.engine_result.accounts_started) - 1,
            "minutes_processed": int(run.engine_result.minutes_processed),
            "kill_switches": ENGINE_KILL_SWITCHES}


def _path_worker(engine: EngineInputs, sched: pd.DataFrame, risk: pd.DataFrame, out_file: Path,
                 fingerprint: str) -> None:
    """The child process of an isolated path: run it, add its own peak RSS, write the file."""
    out = run_engine_path(engine, sched, risk)
    out["engine_peak_rss_mb"] = _peak_rss_mb()
    _save(out_file, {"fingerprint": fingerprint, "out": out})


def _run_isolated(j: int, engine: EngineInputs, sched: pd.DataFrame, risk: pd.DataFrame,
                  out_file: Path, fingerprint: str) -> None:
    proc = multiprocessing.get_context("spawn").Process(
        target=_path_worker, args=(engine, sched, risk, out_file, fingerprint),
        name=f"ml_v2_engine_path_{j}")
    proc.start()
    proc.join()
    if proc.exitcode != 0 or not out_file.exists():
        raise PipelineError(f"engine path {j}: the child process exited with code "
                            f"{proc.exitcode} and left no checkpoint")


# ------------------------------------------------------------------ stages ----
def run_engine_paths(engine: EngineInputs, schedules: Mapping[int, pd.DataFrame],
                     risk: pd.DataFrame, paths: Sequence[int], ckpt_dir: Path, *,
                     isolate: bool) -> dict[int, dict]:
    """The simulate stage: every path in order, one checkpoint file per path (module
    docstring)."""
    out: dict[int, dict] = {}
    for j in paths:
        sched = schedules[j]
        path = Path(ckpt_dir) / f"path_{j}.pkl"
        fp = _path_fingerprint(engine, sched, risk)
        if not path.exists():
            if isolate and len(sched):
                _run_isolated(j, engine, sched, risk, path, fp)
            else:
                _save(path, {"fingerprint": fp, "out": run_engine_path(engine, sched, risk)})
        out[j] = _read_checkpoint(path, fp)
    return out


def _payout_rows(j: int, days: Sequence[Any], n_paths: int) -> list[dict]:
    from ml_route_v2.account import ACCOUNT_50K, ACCOUNT_150K, PATH_TYPES
    from ml_route_v2.payout_sim import simulate_payouts_pair

    rows = []
    for account in (ACCOUNT_50K, ACCOUNT_150K):
        for path_type in PATH_TYPES:
            for dll in (False, True):
                pair = simulate_payouts_pair(days, account, path_type=path_type, dll=dll,
                                             n_paths=n_paths)
                for ks, summary in sorted(pair.items()):
                    rows.append({"path": j, **dataclasses.asdict(summary),
                                 "verdict_reading": not ks})
    return rows


def _empty_schedule_rows(j: int, n_paths: int) -> list[dict]:
    """C-03: a path without day records, one row per (account, path type, DLL, ks) with the
    figures NaN."""
    from ml_route_v2.account import ACCOUNT_50K, ACCOUNT_150K, PATH_TYPES
    from ml_route_v2.constants import N_COPIED_ACCOUNTS, PAYOUT_HORIZON_DATES
    from ml_route_v2.payout_sim import PayoutSummary

    keys = ("account", "path_type", "dll", "ks", "ks2_sizing", "n_paths", "horizon",
            "n_accounts")
    nan_fields = [f.name for f in dataclasses.fields(PayoutSummary) if f.name not in keys]
    return [{"path": j, "account": account.name, "path_type": path_type, "dll": dll, "ks": ks,
             "ks2_sizing": True, "n_paths": int(n_paths), "horizon": PAYOUT_HORIZON_DATES,
             "n_accounts": N_COPIED_ACCOUNTS, **dict.fromkeys(nan_fields, float("nan")),
             "verdict_reading": not ks}
            for account in (ACCOUNT_50K, ACCOUNT_150K) for path_type in PATH_TYPES
            for dll in (False, True) for ks in (False, True)]


def run_payout_paths(sim: Mapping[int, dict], n_paths: int, ckpt_dir: Path) -> pd.DataFrame:
    """The payouts stage: one checkpoint file per path; every row with ``n_trips`` and
    ``empty_schedule`` (module docstring, C-03)."""
    rows: list[dict] = []
    cfp = constants_fingerprint()  # code review C-01
    for j, res in sim.items():
        n_trips = int(res.get("n_trips", 0))
        if not res["days"]:
            rows.extend({**r, "n_trips": n_trips, "empty_schedule": True}
                        for r in _empty_schedule_rows(j, n_paths))
            continue
        fp = hashlib.sha256(pickle.dumps((tuple(res["days"]), int(n_paths), cfp))).hexdigest()
        days = res["days"]
        got = _checkpointed(Path(ckpt_dir) / f"path_{j}.pkl", fp,
                            lambda j=j, days=days: _payout_rows(j, days, n_paths))
        rows.extend({**r, "n_trips": n_trips, "empty_schedule": False} for r in got)
    return pd.DataFrame(rows)


__all__ = [
    "ENGINE_KILL_SWITCHES", "EngineInputs", "frame_fingerprint", "prepare_engine",
    "run_engine_path", "run_engine_paths", "run_payout_paths", "traded_roots",
]
