"""The phase-1 build step: world -> training panel -> c/sigma filter and risk table (Stage E.12
Task 1b; design V2.2, V2.9; lead rules P-1 and P-3).

Vehicles (freeze review F-3): derived, never passed. ``run_build`` reads the ranking's subset
(reports/stage_e12_ranking.json, world.phase1_subset): a subset vehicle without its price path's
step 2 store and summary is dropped by name; the file's sha256 enters the input record (so the
input fingerprint) and the bars report; a resume under another ranking file or another derived
set is refused.

Resumable stage files (pipeline._Stages: state_dir/stages/<name>.pkl, each pinning the constants
fingerprint, fingerprint.constants_fingerprint; a finished stage is loaded, never recomputed, and
one written under other constants is refused):
- ``phase1_panel``: phase1_world, then pipeline.build_world_panel on it with the covered signals
  (P-1) and ``check_grid=False``: pipeline.assert_bars_on_session_grid books bars without the
  close-minute rule L-3, so it would refuse a real store's close-minute prints, which
  data.stage_e_bars has already booked under L-3 to their own labels (the root is refused
  otherwise); the bars report counts them per root. The world is dropped when the stage returns
  (memory, V2.11). Output: the panel, the calendar, the vehicles, the coverage, the bars-report
  body, the input record and the input fingerprint (cpcv.input_fingerprint of the panel frame and
  the input record: store sha256s, S_X, the release calendar's sha256, the frozen tables' hashes,
  the calendar, the signals).
- ``phase1_filter``: pipeline._filter on the panel: cost_filter.c_sigma_table (tau read from
  constants.C_SIGMA_TAU when it runs) and risk_table; the admissible (vehicle, horizon) pairs.
Reports (counts and volatility only; the step prints counts, never a return, mean or t):
reports/stage_e12_phase1_bars.json and reports/stage_e12_c_sigma.json; state_dir/phase1_build.json
records the fingerprints and the stage files' sha256.
"""

from __future__ import annotations

import gc
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from ml_route_v2.constants import HORIZONS
from ml_route_v2.phase1._io import now_local, write_json
from ml_route_v2.phase1.world import (
    RANKING_FILE,
    Phase1Error,
    Phase1Subset,
    Phase1World,
    phase1_subset,
    phase1_world,
    price_path,
)

PANEL_STAGE = "phase1_panel"
FILTER_STAGE = "phase1_filter"
BUILD_FILE = "phase1_build.json"
BARS_REPORT = "stage_e12_phase1_bars.json"
C_SIGMA_REPORT = "stage_e12_c_sigma.json"
RULE_P1 = ("E.12 lead rule P-1: roots available = the phase-1 price paths "
           "(constants.UNIVERSE[v][1]) plus MES; the owned micro step 2 stores MCL, MGC, MHG are "
           "never read; a signal is covered iff spec.own_path_only or every root in "
           "spec.roots_read is available; uncovered signals are left out of the panel and "
           "listed with their missing roots")
RULE_P1A = ("E.12 lead rule P-1a: if loading MES's frozen confirmation store raises a "
            "data.stage_e_bars.StageEBarRefusal or D.1f's record check fails, MES is unavailable "
            "and every signal reading MES is a coverage exclusion ('MES store refused: <class>: "
            "<message>'); a price-path refusal still stops the build")
RULE_P3 = ("E.12 lead rule P-3: S_X per price path = D4's frozen start rule "
           "(screening.stage_e_start_dates.product_start_rule: ts_event, volume, trade_date of "
           "the research and step 2 stores, never a price); MES = D4's fixed 2020-02-03 "
           "(mes_from_d1f); "
           "a root with an empty window is dropped by name; bars cut to trade dates "
           "[S_X, 2024-02-29] by data.stage_e_bars")
RULE_FILTER = ("V2.2: c(p,h) = mean max(cost_long, cost_short) and sigma(p,h) = sd of y_gross over "
               "the ok rows of the training panel; admissible iff c / sigma <= tau "
               "(constants.C_SIGMA_TAU); a product with no admissible horizon is dropped")


@dataclass(frozen=True)
class Build:
    panel: Any  # panel.Panel
    filt: Mapping[str, Any]  # {"c_sigma", "risk", "admissible"}
    calendar: tuple
    vehicles: tuple[str, ...]
    out: Mapping[str, Any]  # the panel stage's output (report, inputs, coverage)
    constants: str
    input_fingerprint: str


def _input_fingerprint(panel: Any, inputs: Mapping[str, Any]) -> str:
    from ml_route_v2.cpcv import input_fingerprint

    return input_fingerprint(panel.frame, {"inputs": inputs, "signals": list(panel.signal_names),
                                           "feature_cols": list(panel.feature_cols)})


def _ranking_record(subset: Phase1Subset) -> dict[str, Any]:
    return {"path": Path(subset.ranking_path).name, "sha256": subset.ranking_sha256,
            "subset": list(subset.subset), "dropped_no_store": dict(subset.dropped)}


def _inputs(world: Phase1World, subset: Phase1Subset) -> dict[str, Any]:
    from screening.stage_e_frozen import load_frozen_tables

    return {
        "ranking": _ranking_record(subset),  # freeze review F-3
        "requested": list(world.requested), "vehicles": list(world.vehicles),
        "dropped": dict(world.dropped),
        "roots": {r: {"s_x": None if s.s_x is None else s.s_x.isoformat(),
                      "store_sha256": s.store_sha256, "research_sha256": s.research_sha256}
                  for r, s in sorted(world.starts.items())},
        "release_calendar_sha256": getattr(world.releases, "sha256", None),
        "frozen_tables": dict(load_frozen_tables().hashes),
        "calendar": {"first": world.calendar[0].isoformat(),
                     "last": world.calendar[-1].isoformat(), "n": len(world.calendar)},
        "covered": list(world.coverage.covered),
        "uncovered": {k: list(v) for k, v in world.coverage.uncovered.items()},
        "mes": {"status": world.mes_status, "refusal": world.mes_refusal},  # P-1a
    }


def _rows_in(world: Phase1World) -> dict[str, dict[str, int]]:
    """Per vehicle: trade dates with bars, decision rows and dates with rows after V2.2's
    exclusions (build_world_panel's own decision_rows call)."""
    from ml_route_v2.clock import decision_rows, trade_dates_of
    from ml_route_v2.pipeline import own_blackout

    vs = tuple(world.vehicles)
    dates = {v: trade_dates_of(world.bars[price_path(v)]) for v in vs}
    rows = decision_rows(vs, dates, exclude=own_blackout(world.blackout, vs))
    out = {}
    for v in vs:
        sub = rows.loc[rows["root"] == v]
        out[v] = {"dates_with_bars": len(dates[v]), "decision_rows": int(len(sub)),
                  "dates_with_rows": int(sub["trade_date"].nunique())}
    return out


def _panel_rows(panel: Any, rows_in: Mapping[str, Mapping[str, int]]) -> dict[str, Any]:
    frame = panel.frame
    roots = frame["root"].to_numpy(object)
    out = {}
    for v, rec in rows_in.items():
        sel = roots == v
        out[v] = {**rec, "panel_rows": int(sel.sum()),
                  "rows_dropped_in_panel": int(rec["decision_rows"] - sel.sum()),
                  "ok_rows": {h: int((sel & frame[f"ok_{h}"].to_numpy(bool)).sum())
                              for h in HORIZONS if f"ok_{h}" in frame.columns}}
    return out


def _bars_body(world: Phase1World, panel: Any, rows_in: Mapping[str, Any],
               subset: Phase1Subset) -> dict[str, Any]:
    days = set(pd.to_datetime(panel.frame["trade_date"]).dt.date)
    return {
        "schema": "stage_e12_phase1_bars/1",
        "rules": {"P-1": RULE_P1, "P-1a": RULE_P1A, "P-3": RULE_P3},
        "ranking": _ranking_record(subset),  # freeze review F-3
        "requested_vehicles": list(world.requested), "vehicles": list(world.vehicles),
        "dropped_roots": dict(world.dropped),
        "mes_status": world.mes_status, "mes_refusal": world.mes_refusal,  # E.12 lead rule P-1a
        "dropped_vehicles": [v for v in world.requested if v not in world.vehicles],
        "roots": {r: dict(rec) for r, rec in sorted(world.roots.items())},
        "calendar": {"first": world.calendar[0], "last": world.calendar[-1],
                     "trade_dates": len(world.calendar),
                     "dates_without_panel_rows": sum(d not in days for d in world.calendar)},
        "rows": _panel_rows(panel, rows_in),
        "panel_counts": dict(panel.counts),
        "signals": {"covered": list(world.coverage.covered),
                    "uncovered": {k: list(v) for k, v in world.coverage.uncovered.items()},
                    "uncovered_reasons": world.coverage.reasons(),
                    "unavailable_roots": dict(world.coverage.unavailable),
                    "n_covered": len(world.coverage.covered),
                    "n_uncovered": len(world.coverage.uncovered)},
        "grid_check": ("pipeline.assert_bars_on_session_grid not run (no L-3); every bar was "
                       "booked by data.stage_e_bars under L-3 to its own label"),
    }


def _panel_stage(subset: Phase1Subset, world_kw: Mapping[str, Any]) -> dict[str, Any]:
    from ml_route_v2.pipeline import build_world_panel

    world = phase1_world(subset.vehicles, **world_kw)
    rows_in = _rows_in(world)
    panel = build_world_panel(world, check_grid=False, signals=world.coverage.covered)
    inputs = _inputs(world, subset)
    out = {"panel": panel, "calendar": tuple(world.calendar), "vehicles": tuple(world.vehicles),
           "requested": tuple(world.requested), "covered": tuple(world.coverage.covered),
           "uncovered": {k: tuple(v) for k, v in world.coverage.uncovered.items()},
           "report": _bars_body(world, panel, rows_in, subset), "inputs": inputs,
           "input_fingerprint": _input_fingerprint(panel, inputs), "created_pdt": now_local()}
    del world
    gc.collect()
    return out


def check_panel_out(out: Mapping[str, Any]) -> None:
    """The saved panel still hashes to its input fingerprint (a changed or corrupted state file
    is refused)."""
    got = _input_fingerprint(out["panel"], out["inputs"])
    if got != out["input_fingerprint"]:
        raise Phase1Error("the saved phase-1 panel does not match its input fingerprint")


def c_sigma_body(filt: Mapping[str, Any], vehicles: Sequence[str]) -> dict[str, Any]:
    from ml_route_v2.constants import C_SIGMA_TAU

    table: pd.DataFrame = filt["c_sigma"]
    pairs = [{"vehicle": str(r.root), "horizon": str(r.horizon), "c_ticks": r.c_ticks,
              "sigma_ticks": r.sigma_ticks, "ratio": r.ratio, "admissible": bool(r.admissible),
              "n_rows": int(r.n_rows)} for r in table.itertuples(index=False)]
    adm = {(p["vehicle"], p["horizon"]) for p in pairs if p["admissible"]}
    present = {p["vehicle"] for p in pairs}
    return {
        "schema": "stage_e12_c_sigma/1", "rule": RULE_FILTER, "tau": C_SIGMA_TAU,
        "pairs": pairs, "admissible": [list(p) for p in filt["admissible"]],
        "dropped_pairs": [{"vehicle": p["vehicle"], "horizon": p["horizon"], "ratio": p["ratio"],
                           "n_rows": p["n_rows"]} for p in pairs if not p["admissible"]],
        "dropped_products": sorted(v for v in present if not any(a[0] == v for a in adm)),
        "vehicles_without_rows": sorted(set(vehicles) - present),
    }


def load_build(state_dir: Path) -> Build:
    """The saved build (both stage files, constants fingerprint and input fingerprint checked)."""
    from ml_route_v2.fingerprint import constants_fingerprint
    from ml_route_v2.pipeline import _read_stage

    state_dir = Path(state_dir)
    fp = constants_fingerprint()
    paths = {n: state_dir / "stages" / f"{n}.pkl" for n in (PANEL_STAGE, FILTER_STAGE)}
    missing = [n for n, p in paths.items() if not p.is_file()]
    if missing:
        raise Phase1Error(f"{state_dir}: no finished build ({missing} missing); run build first")
    out = _read_stage(paths[PANEL_STAGE], fp)
    filt = _read_stage(paths[FILTER_STAGE], fp)
    check_panel_out(out)
    return Build(out["panel"], filt, tuple(out["calendar"]), tuple(out["vehicles"]), out, fp,
                 out["input_fingerprint"])


def _counts_line(out: Mapping[str, Any], filt: Mapping[str, Any]) -> list[str]:
    rep = out["report"]
    lines = [f"vehicles {len(out['vehicles'])} (ranking subset {len(rep['ranking']['subset'])}, "
             f"no step 2 store {sorted(rep['ranking']['dropped_no_store'])}, empty window "
             f"{sorted(rep['dropped_roots'])})"]
    if rep["mes_status"] == "refused":  # E.12 lead rule P-1a
        lines.append("MES store: refused, every signal reading MES excluded "
                     f"({rep['mes_refusal']})")
    else:
        lines.append("MES store: loaded")
    for r, rec in rep["roots"].items():
        lines.append(f"  {r}: S_X {rec['s_x']}, {rec['trade_dates']} trade dates, {rec['bars']} "
                     f"bars, {rec['roll_blackout_dates_in_window']} roll-blackout dates, "
                     f"{len(rec['degraded']['in_window_trade_dates'])} degraded dates")
    for v, rec in rep["rows"].items():
        lines.append(f"  {v}: {rec['decision_rows']} decision rows, {rec['panel_rows']} panel rows "
                     f"(ok {rec['ok_rows']})")
    lines.append(f"calendar {rep['calendar']['trade_dates']} trade dates "
                 f"({rep['calendar']['dates_without_panel_rows']} without a panel row)")
    lines.append(f"signals covered {rep['signals']['n_covered']}, uncovered "
                 f"{rep['signals']['n_uncovered']}")
    table = filt["c_sigma"]
    lines.append(f"c/sigma pairs {len(table)}, admissible {len(filt['admissible'])}, dropped "
                 f"{int((~table['admissible']).sum())}")
    return lines


def run_build(*, state_dir: Path, reports_dir: Path, world_kw: Mapping[str, Any] | None = None,
              harness_sha256: str | None = None, freeze_sha256: str | None = None
              ) -> dict[str, Any]:
    """The build step (module docstring): the vehicles come from reports_dir's ranking (F-3).
    Returns the paths, fingerprints and printable counts."""
    from ml_route_v2.phase1.freeze import file_sha256
    from ml_route_v2.pipeline import _filter, _Stages

    state_dir, reports_dir = Path(state_dir), Path(reports_dir)
    kw = dict(world_kw or {})
    subset = phase1_subset(reports_dir / RANKING_FILE, step2_root=kw.get("step2_root"),
                           summaries_root=kw.get("summaries_root"))
    state_dir.mkdir(parents=True, exist_ok=True)
    stages = _Stages(state_dir, timing=True)
    out = stages.run(PANEL_STAGE, lambda: _panel_stage(subset, kw))
    saved = out["inputs"].get("ranking", {})
    if tuple(out["requested"]) != subset.vehicles or saved.get("sha256") != subset.ranking_sha256:
        raise Phase1Error(f"{state_dir} holds the build of {list(out['requested'])} from ranking "
                          f"sha256 {str(saved.get('sha256'))[:12]}..., not "
                          f"{list(subset.vehicles)} from {subset.ranking_sha256[:12]}...; a "
                          "changed input is a stop")
    check_panel_out(out)
    filt = stages.run(FILTER_STAGE, lambda: _filter(out["panel"]))
    fps = {"constants": stages.constants, "inputs": out["input_fingerprint"],
           "harness_sha256": harness_sha256, "freeze_sha256": freeze_sha256}
    bars_doc = {**out["report"], "fingerprints": fps, "created_pdt": out["created_pdt"]}
    c_doc = {**c_sigma_body(filt, out["vehicles"]), "fingerprints": fps,
             "created_pdt": out["created_pdt"]}
    bars_sha = write_json(reports_dir / BARS_REPORT, bars_doc)
    c_sha = write_json(reports_dir / C_SIGMA_REPORT, c_doc)
    stage_files = {n: file_sha256(state_dir / "stages" / f"{n}.pkl")
                   for n in (PANEL_STAGE, FILTER_STAGE)}
    write_json(state_dir / BUILD_FILE, {
        "fingerprints": fps, "vehicles": list(out["vehicles"]),
        "requested": list(out["requested"]), "stage_files_sha256": stage_files,
        "reports_sha256": {BARS_REPORT: bars_sha, C_SIGMA_REPORT: c_sha},
        "stages": [{"name": s.name, "status": s.status, "wall_s": s.wall_s,
                    "peak_rss_mb": s.peak_rss_mb} for s in stages.records]})
    return {"bars_report": reports_dir / BARS_REPORT, "c_sigma_report": reports_dir /
            C_SIGMA_REPORT, "fingerprints": fps, "lines": _counts_line(out, filt),
            "stages": stages.records, "n_admissible": len(filt["admissible"])}


def panel_peak_note(records: Sequence[Any]) -> list[str]:
    return [f"stage {s.name}: {s.status}, {s.wall_s:.1f} s, peak RSS "
            f"{'n/a' if s.peak_rss_mb is None else f'{s.peak_rss_mb:.0f} MB'}" for s in records]


__all__ = ["BARS_REPORT", "BUILD_FILE", "C_SIGMA_REPORT", "FILTER_STAGE", "PANEL_STAGE", "Build",
           "c_sigma_body", "check_panel_out", "load_build", "panel_peak_note", "run_build"]

