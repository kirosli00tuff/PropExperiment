"""The 17-vehicle world (reports/stage_e20_plan.md sections 1, 2 and 6): real bars from the frozen
phase-1 loaders, or a synthetic world for tests and the timing probe.

Real world (``real_world``), per price path, in this order:
1. S_X is E.12's recorded value (reports/stage_e12_phase1_bars.json "roots" -> "s_x"); the D4
   start rule is never rerun (it reads research-window bytes, F2). The values are checked
   against plan 2's statement (constants.EXPECTED_S_X) and the store sha256 recorded with them
   against the E.17 run manifest's.
2. guard.check_store_path on the step 2 path, then the frozen ``phase1.world.load_root`` with a
   ``RootStart`` built from those records: data.stage_e_bars.load_confirmation_leg (sha256, L-3
   booking, holdout, embargo, store-range and roll-metadata refusals), ``refuse_late``, the
   degraded-day record (reports/step2/bars_<ROOT>.json must record the store sha256),
   ``closure_counts`` and ``compact_bars`` (plan 6, review PR-4); then guard.check_bars.
3. The training calendar (synthetic.training_calendar over [2019-05-06, 2024-02-29]), the frozen
   release calendar (screening.stage_e_rules.load_release_calendar), the frozen D8 costs
   (targets.frozen_costs), each root's roll blackout from its loaded leg, and the signal
   coverage with MES unavailable (phase1.world.signal_coverage; every KEPT signal covered).
MES, the research stores and the 2010-2019 stores are never opened.

Synthetic world (``synthetic_world``): ml_route_v2.synthetic.synthetic_universe over the 17
vehicles, restricted to the 17 price paths (the frozen generator also builds MES, MBT, 6J, 6S, HG
and ZM bars, which the real world does not have), optionally cut at per-root first dates.
"""

from __future__ import annotations

import dataclasses
import json
from collections.abc import Iterable, Mapping, Sequence
from datetime import date
from pathlib import Path
from types import MappingProxyType
from typing import Any

import pandas as pd

from pattern_search import constants as K
from pattern_search import guard


class WorldError(RuntimeError):
    """The world cannot be built as the plan says (nothing about the data is guessed)."""


def repo_root() -> Path:
    from data.config import REPO_ROOT

    return Path(REPO_ROOT)


def check_universe() -> None:
    """Every plan vehicle is a frozen UNIVERSE vehicle with the plan's price path (plan 1)."""
    from ml_route_v2.constants import UNIVERSE

    if len(K.VEHICLES) != K.N_VEHICLES or len(set(K.PATH_ROOTS)) != K.N_VEHICLES:
        raise WorldError(f"the plan's universe has {len(K.VEHICLES)} vehicles, not 17")
    bad = [v for v, p in K.VEHICLE_PATHS.items() if v not in UNIVERSE or UNIVERSE[v][1] != p]
    if bad:
        raise WorldError(f"not UNIVERSE vehicles with the plan's price path: {bad}")


# ------------------------------------------------------------------ recorded inputs ----
def recorded_starts(path: Path | None = None, *,
                    expected: Mapping[str, date] = K.EXPECTED_S_X) -> dict[str, dict[str, Any]]:
    """{price path: {"s_x", "store_sha256", "store_path"}} from E.12's phase-1 report, for the
    17 roots only; WorldError when a value differs from plan 2's statement (``expected``: tests
    pass their fixture stores' values; the CLI never does)."""
    path = Path(path) if path is not None else repo_root() / K.S_X_SOURCE_REL
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    roots = doc.get("roots") or {}
    out: dict[str, dict[str, Any]] = {}
    for root in K.PATH_ROOTS:
        entry = roots.get(root)
        if not isinstance(entry, Mapping) or not entry.get("s_x"):
            raise WorldError(f"{path.name} records no S_X for {root}")
        s_x = date.fromisoformat(str(entry["s_x"]))
        if s_x != expected[root]:
            raise WorldError(f"{root}: recorded S_X {s_x} is not plan 2's {expected[root]}")
        out[root] = {"s_x": s_x, "store_sha256": str(entry["store_sha256"]),
                     "store_path": str(entry.get("store_path", ""))}
    return out


def manifest_store_sha256(path: Path | None = None) -> dict[str, str]:
    """{price path: step 2 store sha256} from the E.17 run manifest (17 roots only)."""
    path = Path(path) if path is not None else repo_root() / K.STORE_MANIFEST_REL
    stores = json.loads(Path(path).read_text(encoding="utf-8")).get("stores") or {}
    out = {}
    for root in K.PATH_ROOTS:
        step2 = (stores.get(root) or {}).get("step2") or {}
        sha = step2.get("sha256")
        if not isinstance(sha, str) or len(sha) != 64:
            raise WorldError(f"{path.name} records no step 2 sha256 for {root}")
        out[root] = sha
    return out


def store_records(s_x_path: Path | None = None, manifest_path: Path | None = None, *,
                  expected: Mapping[str, date] = K.EXPECTED_S_X) -> dict[str, dict[str, Any]]:
    """recorded_starts with the E.17 manifest's sha256 checked equal to E.12's record."""
    starts = recorded_starts(s_x_path, expected=expected)
    shas = manifest_store_sha256(manifest_path)
    bad = [r for r in K.PATH_ROOTS if starts[r]["store_sha256"] != shas[r]]
    if bad:
        raise WorldError(f"E.12's recorded store sha256 differs from the E.17 manifest: {bad}")
    return starts


# ------------------------------------------------------------------ the real world ----
@dataclasses.dataclass(frozen=True)
class SearchWorld:
    vehicles: tuple[str, ...]
    first: date
    last: date
    calendar: tuple[date, ...]
    bars: Mapping[str, pd.DataFrame]  # price path -> compact bars from its S_X
    releases: Any
    costs: Mapping[str, Any]
    blackout: Mapping[str, frozenset[date]]  # price path -> its L-8 roll blackout
    starts: Mapping[str, str]  # price path -> S_X (ISO)
    records: Mapping[str, Any]  # price path -> phase-1 report record (closures, degraded days)
    coverage: Any  # phase1.world.Coverage with MES unavailable
    source: str = "real"


def _root_start(root: str, rec: Mapping[str, Any], step2_root: Path) -> Any:
    from ml_route_v2.phase1.world import STEP2_STORE, RootStart

    entry = {"s_x": rec["s_x"].isoformat(), "source": K.S_X_SOURCE_REL,
             "step2_sha256": rec["store_sha256"]}
    return RootStart(root, rec["s_x"], None, STEP2_STORE,
                     str(guard.step2_store_path(root, step2_root)), rec["store_sha256"], None,
                     None, MappingProxyType(entry), ())


def load_search_root(root: str, rec: Mapping[str, Any], *, step2_root: Path,
                     summaries_root: Path, repo: Path,
                     test_stores: Iterable[str] | None = None
                     ) -> tuple[pd.DataFrame, frozenset[date], dict[str, Any]]:
    """One price path's (compact bars from S_X, roll blackout, record) through the frozen
    phase-1 loader, behind the guard's path check and bar check. ``test_stores``: real paths of
    fixture stores a test may open instead of the 17 real ones (the CLI never passes it)."""
    from ml_route_v2.phase1.world import load_root

    if root not in K.PATH_ROOTS:
        raise guard.GuardRefusal(f"E.20 search guard: {root} is not one of the 17 price paths")
    if test_stores is not None:  # a fixture store never lies under a forbidden store root
        bad = [t for t in test_stores if guard.refusal_reason(t, allowed=()) is not None]
        if bad:
            raise guard.GuardRefusal(f"E.20 search guard: test stores under a store root: {bad}")
    guard.check_store_path(guard.step2_store_path(root, step2_root),
                           allowed=test_stores)  # None: only the 17 real stores
    bars, blackout, record = load_root(_root_start(root, rec, step2_root), step2_root=step2_root,
                                       summaries_root=summaries_root, repo_root=repo)
    guard.check_bars(bars, f"{root} store")
    return bars, blackout, record


def _coverage() -> Any:
    from ml_route_v2.phase1.world import signal_coverage

    cov = signal_coverage(K.VEHICLES, unavailable=dict(K.UNAVAILABLE_ROOTS))
    missing = [n for n in K.KEPT_SIGNALS if n not in cov.covered]
    if missing:
        raise WorldError(f"KEPT signals not covered by the 17 roots without MES: {missing}")
    return cov


def search_calendar() -> tuple[date, ...]:
    """The union of the 17 vehicles' group trade dates in [2019-05-06, 2024-02-29] (plan 2)."""
    from ml_route_v2.synthetic import training_calendar

    cal = training_calendar(K.VEHICLES, K.SEARCH_FIRST, K.SEARCH_LAST)
    if not cal or cal[-1] >= K.FORBIDDEN_FROM:
        raise WorldError("the training calendar is empty or reaches 2024-03-01")
    return cal


def real_world(*, step2_root: Path | None = None, summaries_root: Path | None = None,
               repo: Path | None = None, s_x_path: Path | None = None,
               manifest_path: Path | None = None,
               test_stores: Iterable[str] | None = None,
               test_expected_s_x: Mapping[str, date] | None = None) -> SearchWorld:
    """The real 17-root world (module docstring). ``run`` builds it only after the 45
    registrations (run.run_search checks the registry first; plan 6, review PR-13); ``check
    --world`` builds it with no row, feature or panel (review SC-1). ``test_stores`` and
    ``test_expected_s_x`` are for fixture stores in tests; the CLI never passes them."""
    from data.config import STEP2_ROOT
    from ml_route_v2.targets import frozen_costs
    from screening.stage_e_rules import load_release_calendar

    check_universe()
    repo = Path(repo) if repo is not None else repo_root()
    step2_root = Path(step2_root) if step2_root is not None else Path(STEP2_ROOT)
    summaries_root = (Path(summaries_root) if summaries_root is not None
                      else repo / K.STEP2_SUMMARIES_REL)
    recs = store_records(s_x_path, manifest_path,
                         expected=test_expected_s_x if test_expected_s_x else K.EXPECTED_S_X)
    coverage = _coverage()
    bars: dict[str, pd.DataFrame] = {}
    blackout: dict[str, frozenset[date]] = {}
    records: dict[str, Any] = {}
    for root in K.PATH_ROOTS:
        bars[root], blackout[root], records[root] = load_search_root(
            root, recs[root], step2_root=step2_root, summaries_root=summaries_root, repo=repo,
            test_stores=test_stores)
    return SearchWorld(
        vehicles=K.VEHICLES, first=K.SEARCH_FIRST, last=K.SEARCH_LAST,
        calendar=search_calendar(), bars=MappingProxyType(bars),
        releases=load_release_calendar(repo), costs=MappingProxyType(frozen_costs(K.VEHICLES)),
        blackout=MappingProxyType(blackout),
        starts=MappingProxyType({r: recs[r]["s_x"].isoformat() for r in K.PATH_ROOTS}),
        records=MappingProxyType(records), coverage=coverage)


# ------------------------------------------------------------------ synthetic ----
def synthetic_world(first: date, last: date, *, seed: int,
                    plant: Mapping[str, Any] | Sequence[Mapping[str, Any]] | None = None,
                    warmup_dates: int | None = None,
                    root_first: Mapping[str, date] | None = None,
                    vehicles: Sequence[str] = K.VEHICLES) -> Any:
    """A synthetic world of ``vehicles`` (default the 17) whose bars and blackouts are restricted
    to their price paths, with each root in ``root_first`` cut to start at that trade date."""
    from ml_route_v2.synthetic import WARMUP_DATES, synthetic_universe

    w = synthetic_universe(tuple(vehicles), first, last, seed=seed, plant=plant,
                           warmup_dates=WARMUP_DATES if warmup_dates is None else warmup_dates,
                           compact=True, eager_frames=False)
    paths = tuple(K.VEHICLE_PATHS.get(v) or _path_of(v) for v in w.vehicles)
    bars = {}
    for r in paths:
        frame = w.bars[r]
        cut = (root_first or {}).get(r)
        if cut is not None:
            keep = frame["trade_date"].astype(str).to_numpy(dtype=object) >= cut.isoformat()
            frame = frame.loc[keep].reset_index(drop=True)
        bars[r] = frame
    return dataclasses.replace(
        w, bars=MappingProxyType(bars),
        blackout=MappingProxyType({r: w.blackout[r] for r in paths}),
        legs=MappingProxyType({v: (p,) for v, p in zip(w.vehicles, paths, strict=True)}))


def _path_of(vehicle: str) -> str:
    from ml_route_v2.constants import UNIVERSE

    return UNIVERSE[vehicle][1]


__all__ = ["SearchWorld", "WorldError", "check_universe", "load_search_root",
           "manifest_store_sha256", "real_world", "recorded_starts", "search_calendar",
           "store_records", "synthetic_world"]
