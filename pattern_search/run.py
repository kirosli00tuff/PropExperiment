"""``python -m pattern_search check | run | report`` (reports/stage_e20_plan.md sections 6-9, 11).

    uv run python -m pattern_search check  --freeze-sha256 <manifest sha> --harness-sha256 <v12>
    uv run python -m pattern_search run    --freeze-sha256 <manifest sha> --harness-sha256 <v12>
    uv run python -m pattern_search report --freeze-sha256 <manifest sha> --harness-sha256 <v12>

- check: the harness preflight at v12; the v2 freeze verification
  (reports/stage_e12_ml_v2_freeze.json at its pinned sha256); the search freeze manifest (its
  sha256 from the command line; every required file listed and unchanged); the registry names;
  the 17 stores' sha256s against the E.17 manifest (bytes only, behind the guard); the release
  calendar's coverage of the training calendar. No bar is decoded.
- check --world (review SC-1, lead ruling): after every check above, the real 17-root world
  through world.real_world (the frozen loaders with their sha256, booking, holdout, embargo,
  store-range and roll checks; refuse_late; the guard's bar check; the training calendar). The
  session-grid assertion runs on synthetic worlds only; on real bars the frozen loader's L-3
  booking check replaces it (V2.2b) and the frozen closure counts are recorded (lead ruling after
  the first check --world). A per-root summary (bars, first and last trade date, S_X, splices,
  closure counts) is printed and written to reports/stage_e20_search/world_check.json. No row,
  feature, panel, statistic or fit; nothing in the state directory; no registration needed
  (the registry check stays in ``run``).
- run: check; then the registry must hold E20S-01..E20S-45 under label E20S with this freeze
  sha256 and N 483 -> 528 (before any bar is decoded, any statistic or any fit: plan 6, PR-13);
  then the stages, each checkpointed in the state directory (~/.cache/propexp_e20_search) and
  pinned to the freeze sha256: panel (the real world and the composed panel), filter, cpcv
  (resumable by configuration and split: state_dir/cpcv/cpcv_units.jsonl), final, oos; then the
  screen and the reported items, written to reports/stage_e20_search.json and .md and the tables
  under reports/stage_e20_search/. An empty admissible set ends the search with a failed screen.
- report: check and the registry check; the result files rebuilt from the saved stages only
  (refused when a stage is missing). Nothing is computed.
The CLI installs the audit hook and lowers the priority first (nice 10). Tests call the
functions with their own paths and hooks (``RunPaths``, ``Hooks``, ``test_mode``).
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from pattern_search import constants as K
from pattern_search import guard
from pattern_search import preflight as pf


@dataclass(frozen=True)
class RunPaths:
    freeze: Path
    registry: Path
    state_dir: Path
    reports_dir: Path
    result_json: Path
    result_md: Path
    step2_root: Path | None = None
    summaries_root: Path | None = None
    s_x: Path | None = None
    store_manifest: Path | None = None


def default_paths() -> RunPaths:
    from screening.trial_registry import REGISTRY_PATH

    p = pf.repo_path
    return RunPaths(p(K.FREEZE_MANIFEST_REL), Path(REGISTRY_PATH), Path.home() / K.STATE_DIR_NAME,
                    p(K.REPORTS_SUBDIR_REL), p(K.RESULT_JSON_REL), p(K.RESULT_MD_REL))


# ------------------------------------------------------------------ default hooks ----
def _harness_preflight(expected: str) -> str:
    from screening import harness_freeze

    return harness_freeze.preflight(expected)


def _required() -> list[Path]:
    from pattern_search.freeze_manifest import required_files

    return required_files()


def _stores(paths: RunPaths) -> dict[str, Any]:
    from pattern_search.world import store_records

    recs = store_records(paths.s_x, paths.store_manifest)
    return {"sha256": pf.check_stores(recs, paths.step2_root),
            "s_x": {r: recs[r]["s_x"].isoformat() for r in K.PATH_ROOTS}}


def _releases_cover() -> dict[str, Any]:
    from pattern_search.world import search_calendar
    from screening.stage_e_rules import load_release_calendar

    rel = load_release_calendar(pf.repo_root())
    cal = search_calendar()
    if not rel.covers(cal):
        raise pf.Refused(f"the release calendar does not cover {cal[0]}..{cal[-1]}")
    return {"source": rel.source, "sha256": rel.sha256, "calendar": [cal[0], cal[-1], len(cal)]}


def _real_world(paths: RunPaths) -> Any:
    from pattern_search.world import real_world

    return real_world(step2_root=paths.step2_root, summaries_root=paths.summaries_root,
                      s_x_path=paths.s_x, manifest_path=paths.store_manifest)


@dataclass(frozen=True)
class Hooks:
    preflight: Callable[[str], str] = _harness_preflight
    v2_freeze: Callable[[], dict] = pf.check_v2_freeze
    required: Callable[[], list[Path]] = _required
    stores: Callable[[RunPaths], dict] = _stores
    releases: Callable[[], dict] = _releases_cover
    world: Callable[[RunPaths], Any] = _real_world
    world_pin: str = "real"
    configs: Sequence[Any] | None = None  # None: the 45 frozen CONFIGS (tests pass fewer)
    extra: dict = field(default_factory=dict)


# ------------------------------------------------------------------ check ----
WORLD_CHECK_FILE = "world_check.json"
WORLD_CHECK_SCHEMA = "stage_e20_search_world_check/1"


GRID_NOT_APPLIED = ("not applied: real bars are checked by the frozen loader's L-3 booking "
                    "check (V2.2b); scheduled-closure bars are kept and counted (closure_counts)")


def closure_record(world: Any) -> dict[str, dict[str, Any]]:
    """Per root of a real world: the frozen phase-1 closure counts its loader recorded
    (phase1.world.closure_counts: bars outside the group calendar's open intervals, and of those
    the close-minute prints booked to the session they close, L-3) and the store's
    scheduled-closure flag count; empty for a synthetic world."""
    out = {}
    for root, rec in (getattr(world, "records", {}) or {}).items():
        counts = dict(rec.get("bars_closure") or {})
        out[root] = {"outside_open_intervals": counts.get("outside_open_intervals"),
                     "close_minute": counts.get("close_minute"),
                     "bars_in_scheduled_closure": rec.get("bars_in_scheduled_closure")}
    return out


def world_summary(world: Any) -> dict[str, Any]:
    """Per root: bars, first and last trade date, S_X, splices and roll-blackout dates in the
    window, store sha256, closure counts; the training calendar's span."""
    closures = closure_record(world)
    roots = {}
    for root, frame in world.bars.items():
        days = frame["trade_date"].astype(str)
        rec = (getattr(world, "records", {}) or {}).get(root, {}) or {}
        roots[root] = {"bars": int(len(frame)),
                       "first_trade_date": str(days.iloc[0]) if len(frame) else None,
                       "last_trade_date": str(days.iloc[-1]) if len(frame) else None,
                       "s_x": (getattr(world, "starts", {}) or {}).get(root),
                       "splice_trade_dates_in_window": rec.get("splice_trade_dates_in_window"),
                       "roll_blackout_dates_in_window": rec.get("roll_blackout_dates_in_window"),
                       "store_sha256": rec.get("store_sha256"),
                       "closure_counts": closures.get(root)}
    cal = tuple(world.calendar)
    return {"roots": roots, "calendar": {"first": cal[0].isoformat() if cal else None,
                                         "last": cal[-1].isoformat() if cal else None,
                                         "dates": len(cal)}}


def world_check(paths: RunPaths, hooks: Hooks) -> dict[str, Any]:
    """check --world (module docstring): the world, the guard's bar check, the session-grid
    assertion on a synthetic world only, the summary file."""
    import gc

    from ml_route_v2.pipeline import assert_bars_on_session_grid
    from pattern_search.panel import is_real
    from pattern_search.results import write_json

    world = hooks.world(paths)
    guard.check_frames(world.bars)
    real = is_real(world)
    if not real:
        assert_bars_on_session_grid(world.bars)
    doc = {"schema": WORLD_CHECK_SCHEMA, "world_source": hooks.world_pin,
           "session_grid_assertion": GRID_NOT_APPLIED if real else "applied (synthetic world)",
           "written_local": datetime.now(ZoneInfo("America/Vancouver")).isoformat(
               timespec="seconds"), **world_summary(world)}
    del world
    gc.collect()
    write_json(paths.reports_dir / WORLD_CHECK_FILE, doc)
    return doc


def check(freeze_sha256: str, harness_sha256: str, paths: RunPaths | None = None,
          hooks: Hooks | None = None, *, world: bool = False) -> dict[str, Any]:
    from pattern_search.freeze_manifest import import_dependencies

    paths, hooks = paths or default_paths(), hooks or Hooks()
    harness = pf.check_harness(harness_sha256, hooks.preflight)
    v2 = hooks.v2_freeze()
    import_dependencies()
    freeze = pf.check_freeze(paths.freeze, freeze_sha256, hooks.required())
    pf.registry_names_valid()
    stores = hooks.stores(paths)
    releases = hooks.releases()
    out = {"harness_sha256": harness, "v2_freeze": v2, "freeze": freeze, "stores": stores,
           "release_calendar": releases, "registry_label": K.REGISTRY_LABEL,
           "registry_ids": [K.CONFIG_IDS[0], K.CONFIG_IDS[-1]]}
    if world:
        out["world"] = world_check(paths, hooks)
    return out


def _registered(freeze_sha256: str, paths: RunPaths, test_mode: bool) -> dict[str, Any]:
    pf.check_registry_path(paths.registry, test_mode)
    return pf.check_registered(freeze_sha256, paths.registry)


# ------------------------------------------------------------------ the stages ----
def _panel_stage(paths: RunPaths, hooks: Hooks) -> dict[str, Any]:
    import gc

    from pattern_search.panel import build_search_panel, check_panel, is_real

    world = hooks.world(paths)
    panel = build_search_panel(world)
    record = {"check": check_panel(panel), "counts": dict(panel.counts),
              "starts": dict(getattr(world, "starts", {}) or {}),
              "closure_counts": closure_record(world),
              "session_grid_assertion": (GRID_NOT_APPLIED if is_real(world)
                                         else "applied (synthetic world)")}
    calendar = tuple(world.calendar)
    del world
    gc.collect()
    return {"panel": panel, "calendar": calendar, "record": record}


def _filter_stage(panel: Any) -> dict[str, Any]:
    from pattern_search.search import EmptyAdmissible, admissibility

    try:
        return admissibility(panel)
    except EmptyAdmissible as exc:
        return {"empty": str(exc), "admissible": ()}


def _oos_stage(panel: Any, filt: dict, nested: Any, final: Any, configs: Sequence[Any]) -> dict:
    from ml_route_v2.pipeline import split_risk_fn
    from pattern_search.oos import Refits, final_record, nested_record

    refits = Refits(panel, nested, filt["admissible"], split_risk_fn(panel))
    by_id = {c.config_id: c for c in configs}
    return {"nested": nested_record(refits, by_id),
            "final": final_record(refits, final.config if final is not None else None)}


def _stages(freeze_sha256: str, paths: RunPaths, hooks: Hooks) -> Any:
    from pattern_search.stages import Stages

    return Stages(paths.state_dir, {"freeze_sha256": freeze_sha256, "world": hooks.world_pin})


def _search(st: Any, paths: RunPaths, hooks: Hooks, *, compute: bool) -> dict[str, Any]:
    from pattern_search.search import frozen_configs, run_final, run_nested

    def stage(name: str, fn: Callable[[], Any]) -> Any:
        if not compute and not st.has(name):
            raise pf.Refused(f"stage {name} has not been computed (run first)")
        return st.run(name, fn)

    configs = tuple(hooks.configs) if hooks.configs is not None else frozen_configs()
    built = stage("panel", lambda: _panel_stage(paths, hooks))
    panel, calendar = built["panel"], built["calendar"]
    filt = stage("filter", lambda: _filter_stage(panel))
    out = {"panel_record": built["record"], "filter": filt, "configs": configs}
    if filt.get("empty"):
        return out
    nested = stage("cpcv", lambda: run_nested(panel, filt, calendar, paths.state_dir, configs))
    final = stage("final", lambda: run_final(panel, filt, calendar, paths.state_dir, configs))
    oos = stage("oos", lambda: _oos_stage(panel, filt, nested, final, configs))
    out.update(nested=nested, final=final, oos=oos)
    return out


# ------------------------------------------------------------------ the result ----
RUIN_FAILED = ("not computed: the screen failed; the ruin probability (V2.9 criterion 7) needs "
               "engine trade records and no real-data engine path exists in the frozen code "
               "(plan 9, review PR-6)")
RUIN_PASSED = ("pending: on a passed screen the engine adapter (composition, no edit) is written, "
               "tested and hashed by the B1 freeze before the B1 registration (plan 9)")


def _tables(res: dict[str, Any], paths: RunPaths) -> dict[str, str]:
    from pattern_search.results import write_csv
    from pattern_search.search import config_table

    d = paths.reports_dir
    out = {"c_sigma": str(write_csv(d / "c_sigma.csv", res["filter"]["c_sigma"]))} \
        if "c_sigma" in res["filter"] else {}
    if "nested" not in res:
        return out
    nested, oos = res["nested"], res["oos"]
    out["configs"] = str(write_csv(d / "configs.csv", config_table(nested, res["final"])))
    out["round_trips"] = str(write_csv(d / "round_trips.csv", oos["nested"]["trips"]))
    out["path_daily"] = str(write_csv(d / "path_daily.csv", nested.path_daily))
    out["path_daily_1_5x"] = str(write_csv(d / "path_daily_1_5x.csv",
                                           oos["nested"]["path_daily_1_5x"]))
    out["config_daily"] = str(write_csv(d / "config_daily.csv", nested.config_daily))
    return out


def assemble(res: dict[str, Any], rec: dict[str, Any], entry: dict[str, Any] | None,
             freeze_sha256: str, hooks: Hooks, stage_records: Sequence[Any],
             tables: dict[str, str]) -> dict[str, Any]:
    from pattern_search.search import config_table, dsr_record, empty_screen, final_own_record
    from pattern_search.search import screen as screen_fn

    filt = res["filter"]
    doc: dict[str, Any] = {
        "schema": K.RESULT_SCHEMA, "freeze_sha256": freeze_sha256, "world_source": hooks.world_pin,
        "check": rec, "registry_entry": entry, "panel": res["panel_record"],
        "filter": {"admissible": [list(p) for p in filt.get("admissible", ())],
                   "empty": filt.get("empty")},
        "tables": tables,
        "stages": [{"name": s.name, "status": s.status, "wall_s": s.wall_s,
                    "peak_rss_mb": s.peak_rss_mb} for s in stage_records],
        "n_configs": len(res["configs"]),
    }
    if filt.get("empty"):
        doc["screen"] = empty_screen(filt["empty"])
        doc["reported"] = {"ruin": {"status": RUIN_FAILED}}
        return doc
    nested, final, oos = res["nested"], res["final"], res["oos"]
    sc = screen_fn(nested, final)
    doc["screen"] = sc
    doc["reported"] = {
        "dsr": dsr_record(nested, K.N_TOTAL_AT_SCREEN),
        "configs": config_table(nested, final),
        "final_own": final_own_record(nested, final),
        "final_selection_table": final.table,
        "oos": {"final": oos["final"],
                "cost_sensitivity": oos["nested"]["cost_sensitivity"],
                "round_trips": oos["nested"]["trips"].reset_index(),
                "trades_t4": oos["nested"]["trades_t4"],
                "trades_total": oos["nested"]["trades_total"],
                "cost_check_max_abs_diff": oos["nested"]["cost_check_max_abs_diff"]},
        "ruin": {"status": RUIN_PASSED if sc["verdict"] == K.PASS else RUIN_FAILED},
    }
    return doc


def _late_v2_modules(rec: dict[str, Any]) -> list[str]:
    from pattern_search.freeze_manifest import loaded_v2_files

    return [pf.rel(p) for p in loaded_v2_files()]


def _write(doc: dict[str, Any], paths: RunPaths) -> dict[str, Any]:
    from pattern_search.results import summary_md, write_atomic, write_json

    doc["written_local"] = datetime.now(ZoneInfo("America/Vancouver")).isoformat(
        timespec="seconds")
    doc["v2_modules_loaded_at_write"] = _late_v2_modules(doc)
    write_json(paths.result_json, doc)
    write_atomic(paths.result_md, summary_md(doc).encode())
    return doc


def run_search(freeze_sha256: str, harness_sha256: str, paths: RunPaths | None = None,
               hooks: Hooks | None = None, *, test_mode: bool = False,
               compute: bool = True) -> dict[str, Any]:
    """``run`` (compute=True) or ``report`` (compute=False): module docstring."""
    paths, hooks = paths or default_paths(), hooks or Hooks()
    rec = check(freeze_sha256, harness_sha256, paths, hooks)
    entry = _registered(freeze_sha256, paths, test_mode)  # before any bar is decoded
    st = _stages(freeze_sha256, paths, hooks)
    res = _search(st, paths, hooks, compute=compute)
    tables = _tables(res, paths)
    doc = assemble(res, rec, entry, freeze_sha256, hooks, st.records, tables)
    return _write(doc, paths)


# ------------------------------------------------------------------ CLI ----
def main(argv: Sequence[str] | None = None) -> int:
    guard.install_audit_hook()  # F3 (b), before anything else is read
    parser = argparse.ArgumentParser(prog="python -m pattern_search")
    parser.add_argument("command", choices=("check", "run", "report"))
    parser.add_argument("--freeze-sha256", required=True)
    parser.add_argument("--harness-sha256", required=True)
    parser.add_argument("--world", action="store_true",
                        help="check only: also load the real 17-root world and summarize it")
    args = parser.parse_args(argv)
    if args.world and args.command != "check":
        parser.error("--world applies to check only")
    from compute.platform import lower_priority
    from data.stage_e_bars import StageEBarRefusal
    from ml_route_v2.phase1.world import Phase1Error
    from ml_route_v2.pipeline import BarGridError
    from pattern_search.world import WorldError
    from screening.harness_freeze import HarnessFreezeError
    from screening.trial_registry import TrialRegistryError

    lower_priority()
    try:
        if args.command == "check":
            rec = check(args.freeze_sha256, args.harness_sha256, world=args.world)
            print(f"search check passed: freeze {rec['freeze']['sha256'][:12]}..., "
                  f"{rec['freeze']['files']} files, 17 stores verified")
            if args.world:
                w = rec["world"]
                for root, r in w["roots"].items():
                    print(f"  {root}: {r['bars']} bars, {r['first_trade_date']}.."
                          f"{r['last_trade_date']}, S_X {r['s_x']}, "
                          f"splices {r['splice_trade_dates_in_window']}")
                print(f"  calendar {w['calendar']['first']}..{w['calendar']['last']} "
                      f"({w['calendar']['dates']} dates) -> "
                      f"{K.REPORTS_SUBDIR_REL}/{WORLD_CHECK_FILE}")
        else:
            doc = run_search(args.freeze_sha256, args.harness_sha256,
                             compute=args.command == "run")
            print(f"SCREEN {doc['screen']['verdict']} -> {K.RESULT_JSON_REL}")
    except (pf.Refused, HarnessFreezeError, TrialRegistryError, guard.GuardRefusal,
            WorldError, StageEBarRefusal, Phase1Error, BarGridError) as exc:
        print(f"REFUSED ({type(exc).__name__}): {exc}", file=sys.stderr)
        return K.RC_REFUSED
    return K.RC_OK


__all__ = ["WORLD_CHECK_FILE", "Hooks", "RunPaths", "assemble", "check", "default_paths", "main",
           "run_search", "world_check", "world_summary"]
