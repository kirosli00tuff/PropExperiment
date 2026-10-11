"""``python -m h6_rod check | register | evaluate`` (prereg sections 8 and 10).

    uv run python -m h6_rod check    --freeze-sha256 <manifest sha> --harness-sha256 <v12 sha>
    uv run python -m h6_rod register --freeze-sha256 <manifest sha> --harness-sha256 <v12 sha>
    uv run python -m h6_rod evaluate --freeze-sha256 <manifest sha> --harness-sha256 <v12 sha>

- check: the lead's settings (T3_REGISTERED, ENGINE_LEAD_IN_DATES, GEX_CSV_SHA256 when T3, the
  registry names), the harness preflight at v12, the freeze manifest, the read guard on the store
  path, the store's sha256, the GEX CSV's sha256 (T3), the release calendar's coverage, no marker.
  No bar and no GEX value is read.
- register: check, then one registry line (label, the registered ids, the freeze manifest's
  sha256); a second registration is refused.
- evaluate: check; the registration must hold these ids under this freeze sha256; then, before
  the marker, the price-free store validation (data.stage_e_bars.read_leg_dates: every booking,
  holdout, embargo, out-of-store and roll-metadata refusal; duplicate timestamps; the bar guard on
  ts and trade dates) and the GEX CSV's parse (T3). Any problem refuses with nothing consumed.
  Then the marker is written (O_EXCL), and only then are the prices loaded through the frozen
  loader (data.stage_e_bars.load_confirmation_leg), the schedules built, the engine run once per
  test and window, and the result files written. After the marker nothing about the data raises:
  a loader refusal or an engine invariant stops the affected tests (STOPPED, recorded).
The CLI installs the audit hook and lowers the priority first. Tests call the functions with
their own paths and hooks (``RunPaths``, ``Hooks``, ``test_mode``); the CLI takes neither.
"""

from __future__ import annotations

import argparse
import sys
import traceback
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from h6_rod import clock, guard, report, signal, stats
from h6_rod import constants as K
from h6_rod import preflight as pf
from h6_rod.engine import run_tests, vehicle_blackout
from h6_rod.gex import GexInputError, load_gex
from h6_rod.results_io import summary_md, write_atomic, write_json


@dataclass(frozen=True)
class RunPaths:
    store: Path
    allowed_store: Path
    gex: Path
    freeze: Path
    marker: Path
    result_json: Path
    result_md: Path
    registry: Path


def default_paths() -> RunPaths:
    from screening.trial_registry import REGISTRY_PATH

    p = pf.repo_path
    return RunPaths(p(K.NQ_STORE_REL), p(K.NQ_STORE_REL), p(K.GEX_CSV_REL),
                    p(K.FREEZE_MANIFEST_REL), p(K.MARKER_REL), p(K.RESULT_JSON_REL),
                    p(K.RESULT_MD_REL), Path(REGISTRY_PATH))


# ------------------------------------------------------------------ the store ----
def validate_store(paths: RunPaths) -> dict[str, Any]:
    """Before the marker: the frozen loader's price-free checks, duplicates and the bar guard."""
    from data.config import STEP2_ROOT
    from data.stage_e_bars import read_leg_dates
    from data.step2_store import step2_parquet_path

    allowed = paths.allowed_store
    guard.check_store_path(step2_parquet_path(K.PRICE_ROOT, STEP2_ROOT), allowed=allowed)
    guard.check_store_path(paths.store, allowed=allowed)
    days, blackout = read_leg_dates(K.PRICE_ROOT, STEP2_ROOT, K.STORE_FIRST,
                                    expected_sha256=K.NQ_STORE_SHA256)
    guard.check_trade_dates(days, "store trade dates")
    ts = pd.read_parquet(paths.store, columns=["ts_event"])["ts_event"].to_numpy("int64")
    if len(ts) != len(set(ts.tolist())):
        raise pf.Refused("the NQ store holds duplicate bar timestamps")
    if len(ts) and int(ts.max()) >= guard.FORBIDDEN_FROM_NS:
        raise guard.GuardRefusal("H6 guard: a store bar opens on or after 2024-03-01")
    return {"bars": int(len(ts)), "trade_dates": len(days),
            "first_trade_date": days[0] if days else None,
            "last_trade_date": days[-1] if days else None, "roll_blackout_dates": len(blackout)}


def load_leg(paths: RunPaths) -> tuple[pd.DataFrame, frozenset[date], dict[str, Any]]:
    """After the marker: the bars through the frozen loader, the price path's L-8 blackout."""
    from data.config import STEP2_ROOT
    from data.stage_e_bars import load_confirmation_leg
    from data.step2_store import step2_parquet_path

    allowed = paths.allowed_store
    guard.check_store_path(step2_parquet_path(K.PRICE_ROOT, STEP2_ROOT), allowed=allowed)
    leg = load_confirmation_leg(K.PRICE_ROOT, STEP2_ROOT, K.STORE_FIRST,
                                expected_sha256=K.NQ_STORE_SHA256)
    guard.check_bars(leg.frame, "NQ store")
    record = {"path": pf.rel(Path(leg.path)), "sha256": leg.sha256, "bars": int(len(leg.frame)),
              "trade_dates": len(leg.trade_dates),
              "splice_trade_dates": len(leg.splice_trade_dates),
              "roll_blackout_dates": len(leg.roll_blackout)}
    return leg.frame, frozenset(leg.roll_blackout), record


def _releases() -> Any:
    from screening.stage_e_rules import load_release_calendar

    return load_release_calendar(pf.repo_root())


def _preflight(expected: str) -> str:
    from screening import harness_freeze

    return harness_freeze.preflight(expected)


@dataclass(frozen=True)
class Hooks:
    preflight: Callable[[str], str] = _preflight
    validate_store: Callable[[RunPaths], dict[str, Any]] = validate_store
    load_leg: Callable[[RunPaths], tuple[pd.DataFrame, frozenset[date], dict]] = load_leg
    releases: Callable[[], Any] = _releases
    calendar: Any = None  # None: the frozen equity group calendar


def _import_dependencies() -> None:
    """Every ml_route_v2 module H6 runs, loaded before the freeze check lists them
    (pipeline.own_blackout imports ml_route_v2.clock lazily)."""
    import ml_route_v2.clock  # noqa: F401
    import ml_route_v2.gate0  # noqa: F401
    import ml_route_v2.pipeline  # noqa: F401


# ------------------------------------------------------------------ check / register ----
def check(freeze_sha256: str, harness_sha256: str, paths: RunPaths | None = None,
          hooks: Hooks | None = None) -> dict[str, Any]:
    paths, hooks = paths or default_paths(), hooks or Hooks()
    tests = pf.lead_settings()
    harness = pf.check_harness(harness_sha256, hooks.preflight)
    _import_dependencies()
    freeze = pf.check_freeze(paths.freeze, freeze_sha256, tests, paths.gex)
    guard.check_store_path(paths.store, allowed=paths.allowed_store)
    store_sha = pf.check_pinned(paths.store, K.NQ_STORE_SHA256, "NQ store")
    gex_sha = (pf.check_pinned(paths.gex, str(K.GEX_CSV_SHA256), "GEX CSV")
               if "T3" in tests else None)
    releases = hooks.releases()
    need = clock.trade_dates(K.STORE_FIRST, K.STORE_LAST, hooks.calendar)
    if not releases.covers(need):
        raise pf.Refused(f"the release calendar ({releases.first}..{releases.last}) does not cover "
                         f"{need[0]}..{need[-1]}")
    pf.refuse_if_marked(paths.marker)
    return {"tests": list(tests), "test_ids": pf.test_ids(tests), "harness_sha256": harness,
            "freeze": freeze, "store": {"path": pf.rel(paths.store), "sha256": store_sha},
            "gex_csv": None if gex_sha is None else {"path": pf.rel(paths.gex), "sha256": gex_sha},
            "release_calendar": {"source": releases.source, "sha256": releases.sha256},
            "engine_lead_in_dates": K.ENGINE_LEAD_IN_DATES}


def register(freeze_sha256: str, harness_sha256: str, paths: RunPaths | None = None,
             hooks: Hooks | None = None, *, test_mode: bool = False) -> dict[str, Any]:
    from screening.trial_registry import register as registry_register

    paths, hooks = paths or default_paths(), hooks or Hooks()
    rec = check(freeze_sha256, harness_sha256, paths, hooks)
    pf.check_registry_path(paths.registry, test_mode)
    pf.refuse_if_registered(rec["tests"], paths.registry)
    return registry_register(K.REGISTRY_LABEL, rec["test_ids"], paths.freeze, freeze_sha256,
                             harness_sha256, path=paths.registry, preflight=hooks.preflight,
                             note="Stage E.20 H6 (reports/stage_e20_prereg_H6.md)")


# ------------------------------------------------------------------ evaluate ----
def _windows(cal: Any) -> dict[str, Any]:
    n = int(K.ENGINE_LEAD_IN_DATES or 0)
    return {
        "verdict": {"first": K.VERDICT_FIRST, "last": K.VERDICT_LAST,
                    "days": clock.trade_dates(K.VERDICT_FIRST, K.VERDICT_LAST, cal),
                    "t2_lookback_first": clock.t2_warmup_first(cal),
                    "lead_in": clock.lead_in_dates(K.VERDICT_FIRST, n, cal)},
        "overlap": {"first": K.OVERLAP_FIRST, "last": K.OVERLAP_LAST,
                    "days": clock.trade_dates(K.OVERLAP_FIRST, K.OVERLAP_LAST, cal),
                    "t2_lookback_first": K.OVERLAP_FIRST,
                    "lead_in": clock.lead_in_dates(K.OVERLAP_FIRST, n, cal)},
    }


def _all_stopped(tests: Sequence[str], exc: BaseException,
                 trace: str | None = None) -> dict[str, Any]:
    reason = f"{type(exc).__name__}: {exc}"
    out = {}
    for t in tests:
        rec: dict[str, Any] = {"test": t, "test_id": K.TEST_IDS[t], "status": K.STOPPED,
                               "reason": reason}
        if trace is not None:
            rec["traceback"] = trace
        out[t] = rec
    return out


def _stop_all(doc: dict[str, Any], tests: Sequence[str], exc: BaseException,
              trace: str | None = None) -> None:
    """Review H6R-1: after the marker, any exception stops every test, recorded; the caller
    still writes the result, so the result file exists whenever the marker does."""
    doc["tests"] = _all_stopped(tests, exc, trace)
    doc["overlap"] = _all_stopped(tests, exc, trace)
    doc["verdicts"] = {t: K.STOPPED for t in tests}
    doc.pop("holm", None)
    doc["post_marker_exception"] = {"type": type(exc).__name__, "message": str(exc),
                                    "traceback": trace}


def evaluation_exit_code(doc: Mapping[str, Any]) -> int:
    """The CLI's code for a written result: RC_ERROR when the run stopped on an exception after
    the marker (the result file still exists), else RC_OK."""
    return K.RC_ERROR if doc.get("post_marker_exception") else K.RC_OK


def _evaluate_window(name: str, w: Mapping[str, Any], facts: Mapping[date, Any],
                     tests: Sequence[str], gex: Mapping[date, float] | None, bars: pd.DataFrame,
                     blackout: frozenset[date], releases: Any, cal: Any) -> dict[str, Any]:
    scheds = signal.schedules(facts, tests, w["first"], w["last"], w["t2_lookback_first"], gex,
                              cal)
    runs = run_tests(bars, scheds, w["days"], w["lead_in"], blackout, releases)
    shortened = {d: clock.is_shortened(d, cal) for d in w["days"]}
    out = {}
    for test in tests:
        run = runs[test]
        if isinstance(run, Exception):
            out[test] = report.stopped_record(test, run, scheds[test])
        else:
            out[test] = report.window_record(test, run, scheds[test], w["days"], shortened,
                                             verdict=name == "verdict")
    return out


def verdicts(records: Mapping[str, dict[str, Any]], tests: Sequence[str]) -> dict[str, Any]:
    """Holm over the registered tests (a STOPPED test enters with p = 1, m unchanged) and each
    test's pass bar; adds ``pass_bar`` to each completed record."""
    pvals = {t: (1.0 if records[t].get("status") == K.STOPPED else records[t]["p_one_sided"])
             for t in tests}
    h = stats.holm(pvals)
    out = {}
    for t in tests:
        rec = records[t]
        if rec.get("status") == K.STOPPED:
            out[t] = K.STOPPED
            continue
        rec["pass_bar"] = stats.pass_bar(
            t, holm_rejected=h["rejected"][t], mean_gross=rec["mean_gross_ticks"],
            mean_cost=rec["mean_cost_ticks"], n_trades=rec["n_trades"],
            sharpe=rec["annualized_net_sharpe"])
        out[t] = rec["pass_bar"]["verdict"]
    return {"holm": h, "verdicts": out}


def _prepare(freeze_sha256: str, harness_sha256: str, paths: RunPaths, hooks: Hooks,
             test_mode: bool) -> tuple[dict[str, Any], dict[date, float] | None]:
    """Everything before the marker; any problem refuses with nothing consumed. Returns the
    record and the GEX rows (T3; parsed here once, so nothing about the file can fail later)."""
    rec = check(freeze_sha256, harness_sha256, paths, hooks)
    pf.check_registry_path(paths.registry, test_mode)
    reg = pf.check_registered(rec["tests"], freeze_sha256, paths.registry)
    rec["registration"] = {k: reg[k] for k in ("entry_id", "test", "test_ids", "freeze_sha256",
                                               "n_before", "n_after", "time_local")}
    try:
        rec["store_validation"] = hooks.validate_store(paths)
    except (OSError, ValueError, RuntimeError) as exc:
        if isinstance(exc, guard.GuardRefusal):
            raise
        raise pf.Refused(f"store validation refused: {type(exc).__name__}: {exc}") from exc
    gex = None
    if "T3" in rec["tests"]:
        try:
            gex, rec["gex_load"] = load_gex(paths.gex, expected_sha256=K.GEX_CSV_SHA256)
        except GexInputError as exc:
            raise pf.Refused(f"GEX CSV refused: {exc}") from exc
    return rec, gex


def evaluate(freeze_sha256: str, harness_sha256: str, paths: RunPaths | None = None,
             hooks: Hooks | None = None, *, test_mode: bool = False,
             log: Callable[[str], None] = print) -> dict[str, Any]:
    from data.stage_e_bars import StageEBarRefusal

    paths, hooks = paths or default_paths(), hooks or Hooks()
    rec, gex = _prepare(freeze_sha256, harness_sha256, paths, hooks, test_mode)
    tests, cal = tuple(rec["tests"]), hooks.calendar
    pf.write_marker(paths.marker, {k: rec[k] for k in ("test_ids", "harness_sha256", "freeze",
                                                       "registration", "store")})
    log(f"H6 marker written: {paths.marker}")
    doc: dict[str, Any] = {"schema": K.RESULT_SCHEMA, "label": K.REGISTRY_LABEL, **rec,
                           "marker": pf.rel(paths.marker), "constants": constants_record()}
    try:
        bars, nq_blackout, doc["load"] = hooks.load_leg(paths)
    except (StageEBarRefusal, OSError) as exc:
        _stop_all(doc, tests, exc, traceback.format_exc())
        return _write(doc, paths, log)
    try:  # review H6R-1: nothing after the marker may leave it without a result file
        w = _windows(cal)
        facts = signal.compute_facts(bars[["ts_event", "close", "instrument_id"]],
                                     clock.trade_dates(K.STORE_FIRST, K.STORE_LAST, cal), cal)
        blackout = vehicle_blackout(nq_blackout)
        releases = hooks.releases()
        doc["eligibility"] = {n: signal.eligibility_counts(facts, v["first"], v["last"])
                              for n, v in w.items()}
        doc["eligibility"]["t2_warmup"] = signal.eligibility_counts(
            facts, w["verdict"]["t2_lookback_first"], K.OVERLAP_LAST)
        doc["windows"] = {n: {"first": v["first"], "last": v["last"],
                              "trade_dates": len(v["days"]),
                              "t2_lookback_first": v["t2_lookback_first"],
                              "lead_in": list(v["lead_in"])} for n, v in w.items()}
        doc["vehicle_roll_blackout_dates"] = sorted(blackout)
        doc["tests"] = _evaluate_window("verdict", w["verdict"], facts, tests, gex, bars,
                                        blackout, releases, cal)
        doc["overlap"] = _evaluate_window("overlap", w["overlap"], facts, tests, gex, bars,
                                          blackout, releases, cal)
        doc.update(verdicts(doc["tests"], tests))
    except Exception as exc:  # noqa: BLE001 - every post-marker failure is recorded, not raised
        _stop_all(doc, tests, exc, traceback.format_exc())
    return _write(doc, paths, log)


def _late_v2_modules(doc: Mapping[str, Any]) -> list[str]:
    """ml_route_v2 files loaded after the freeze check listed them (should be none)."""
    checked = set(doc.get("freeze", {}).get("v2_files", []))
    return sorted(set(pf.rel(p) for p in pf.loaded_v2_files()) - checked)


def _write(doc: dict[str, Any], paths: RunPaths, log: Callable[[str], None]) -> dict[str, Any]:
    from zoneinfo import ZoneInfo

    doc["written_local"] = datetime.now(ZoneInfo("America/Vancouver")).isoformat(
        timespec="seconds")
    doc["v2_modules_loaded_after_the_freeze_check"] = _late_v2_modules(doc)
    write_json(paths.result_json, doc)
    write_atomic(paths.result_md, summary_md(doc).encode())
    log(f"H6 verdicts: {doc.get('verdicts')} -> {paths.result_json}")
    return doc


def constants_record() -> dict[str, Any]:
    return {k: getattr(K, k) for k in (
        "PRICE_ROOT", "VEHICLE", "QUANTITY", "NQ_STORE_REL", "NQ_STORE_SHA256", "VERDICT_FIRST",
        "VERDICT_LAST", "OVERLAP_FIRST", "OVERLAP_LAST", "T2_WARMUP_TRADE_DATES",
        "T2_LOOKBACK_ELIGIBLE", "SIGNAL_BAR_BEFORE_C_MIN", "PRIOR_BAR_BEFORE_C_MIN",
        "EXIT_BEFORE_C_MIN", "HOLM_ALPHA", "COST_MULTIPLE", "SHARPE_BAR", "ANNUALIZATION_DAYS",
        "STRESS_SLIPPAGE_MULTIPLE", "REGISTRY_LABEL", "T3_REGISTERED", "ENGINE_LEAD_IN_DATES",
        "GEX_CSV_REL", "GEX_CSV_SHA256", "HARNESS_SHA256")} | {"MIN_TRADES": dict(K.MIN_TRADES),
                                                              "TEST_IDS": dict(K.TEST_IDS)}


# ------------------------------------------------------------------ CLI ----
def main(argv: Sequence[str] | None = None) -> int:
    guard.install_audit_hook()  # F3 (b), before anything else is read
    parser = argparse.ArgumentParser(prog="python -m h6_rod")
    parser.add_argument("command", choices=("check", "register", "evaluate"))
    parser.add_argument("--freeze-sha256", required=True)
    parser.add_argument("--harness-sha256", required=True)
    args = parser.parse_args(argv)
    from compute.platform import lower_priority
    from screening.harness_freeze import HarnessFreezeError
    from screening.trial_registry import TrialRegistryError

    lower_priority()
    try:
        if args.command == "check":
            rec = check(args.freeze_sha256, args.harness_sha256)
            print(f"H6 check passed: tests {rec['tests']}, "
                  f"freeze {rec['freeze']['sha256'][:12]}...")
        elif args.command == "register":
            entry = register(args.freeze_sha256, args.harness_sha256)
            print(f"registered {entry['test']} {entry['test_ids']}: N {entry['n_before']} -> "
                  f"{entry['n_after']} ({entry['entry_id']})")
        else:
            doc = evaluate(args.freeze_sha256, args.harness_sha256)
            failure = doc.get("post_marker_exception")
            if failure:
                print(f"H6 STOPPED after the marker ({failure['type']}): {failure['message']}\n"
                      f"{failure.get('traceback') or ''}", file=sys.stderr)
            return evaluation_exit_code(doc)
    except (pf.Refused, HarnessFreezeError, TrialRegistryError, guard.GuardRefusal) as exc:
        print(f"REFUSED ({type(exc).__name__}): {exc}", file=sys.stderr)
        return K.RC_REFUSED
    return K.RC_OK


__all__ = ["Hooks", "RunPaths", "check", "constants_record", "default_paths", "evaluate",
           "evaluation_exit_code", "load_leg", "main", "register", "validate_store", "verdicts"]
