"""Stage D.1f steps 5 to 8: run the frozen confirmation list and apply its decision rules.

FROZEN SPECIFICATION (read-only; this module implements it, it does not restate it):
reports/stage_d1f_confirmation_list.md (sections 0, 1.3 to 1.5, 2.1 to 2.3, 3.1 to 3.6, 5.6)
and docs/NULL_CRITERIA.md (sections 1 to 7, 4.1 the start rule).

    uv run python -m strategy.research._d1f_confirmation --step preflight --manifest-sha256 <hex>
    uv run python -m strategy.research._d1f_confirmation --step all --manifest-sha256 <hex>

``--manifest-sha256`` is REQUIRED: the freeze manifest's sha256 as the freeze script printed it
at the freeze commit (STATE file, progress entry, run prompt). Every step first runs
``_d1f_preflight.preflight`` and refuses to run on any problem (the section-0, declaration,
manifest and self hashes; the git anchor of the manifest and every file it lists; the
confirmation build's manifest, stop flag, step 4b and degraded-date comparison; clean
holdouts), or when the manifest's sha256 is not the declared one (review F1). In the build
session there is no committed manifest and no parquet, so it refuses there.

Step 5 records the sha256 of the run-session inputs that cannot be in the freeze manifest (the
confirmation parquet, its build summary, the rolls / condition / symbology files and
docs/HOLDOUT2_MANIFEST.json); every later step recomputes them and refuses on a difference
(review F5). Every output header records the interpreter and library versions (review N5).

STEP ORDER (list 1.5; nothing in 5 to 8 is revisited after 8, so every output is created
exclusively and nothing runs once the step-8 outputs exist):
5. S by the start rule (``_d1f_start_rule``): V_ref, every monthly median, S, the 0.15 / 0.40
   sensitivity, the degraded-date comparison logged. No qualifying month: stop (D-1).
6. Continuity (list 1.4): every one of the 31 trials on ``train_union_window()`` reproduces
   reports/stage_d1d_accounting.json to the cent (net P&L), with its trip count and its daily
   Sharpe to 1e-6 (the _d1b/_d1d precedent), and E-H1 / E-H2 do so under BOTH factories. Any
   problem refuses step 7; no confirmation figure is read before this passes.
7. The list (``_d1f_members``) on ``confirmation_window(S)``: 37 Tier A trials (E-H1 / E-H2 on
   the confirmation factories; H forced exits counted from the engine's ledger, the instances'
   own sets recorded beside them and any difference flagged, review F6), the 64 directional
   statistics through ``_d1f_statistics.compute_statistics`` (21 Tier A with their composite
   verdicts, 43 Tier B), the non-directional facts descriptively.
8. The decision rules (``_d1f_decisions``), then the hash checks again; a changed file marks
   the run void in every output (a voided run's results are still reported).

Outputs (run session only): reports/stage_d1f_step5_start_rule.json, _step6_continuity.json,
_step7_list_run.json, and the step-8 results reports/stage_d1f_tier_a.json, _tier_b.json,
_descriptive_facts.json and _decisions.json. Each carries the manifest's sha256, S and its
inputs, the continuity result and every member, failures and non-survivors included.

Lead rulings (a) to (e) are cited where implemented: (a) to (d) in ``_d1f_decisions``, (e) in
``_d1f_members``. N after D.1f is 58 (31 + 6 Family H + 21 statistics).
"""

from __future__ import annotations

import argparse
import json
import math
import multiprocessing as mp
import re
import sys
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path
from types import MappingProxyType

import numpy as np
import pandas as pd
import pyarrow as pa

import screening.runner
from data.build_mes_bars import CONFIRMATION_SUMMARY_PATH, ConfirmationInputs
from data.config import REPO_ROOT, VENDOR_ROOT
from data.holdout import HOLDOUT2_PATHS
from data.research_bars import CONFIRMATION_SERIES_PATH, load_confirmation_bars, load_research_bars
from funnel.power_gate import POWER_GATE_JSON
from screening.runner import (
    ConfirmationWindow,
    _confirmation_frame,
    _fill_trade_date,
    _research_frame,
    confirmation_window,
    screen_candidate,
    train_union_window,
)
from sim.engine import FillEvent, splice_trade_dates_from_parquet
from strategy.research._d1b_accounting import _moments
from strategy.research._d1f_decisions import (
    N_TIER_A,
    N_TIER_B,
    Evaluation,
    Member,
    evaluate,
)
from strategy.research._d1f_members import (
    continuity_trials,
    recorded_edges,
    statistic_composite,
    statistic_directions,
    statistic_member,
    tier_a_trials,
    trial_member,
)
from strategy.research._d1f_preflight import (
    CRITERIA_PATH,
    LIST_PATH,
    Preflight,
    hash_checks,
    preflight,
    sha256_bytes,
    sha256_file,
)
from strategy.research._d1f_start_rule import (
    COLUMNS,
    first_trade_date_by_month,
    rth_monthly_median_volume,
    start_rule,
)
from strategy.research._d1f_statistics import compute_statistics, select_statistic_bars

REPORTS = REPO_ROOT / "reports"
START_RULE_PATH = REPORTS / "stage_d1f_step5_start_rule.json"
CONTINUITY_PATH = REPORTS / "stage_d1f_step6_continuity.json"
LIST_RUN_PATH = REPORTS / "stage_d1f_step7_list_run.json"
TIER_A_PATH = REPORTS / "stage_d1f_tier_a.json"
TIER_B_PATH = REPORTS / "stage_d1f_tier_b.json"
FACTS_PATH = REPORTS / "stage_d1f_descriptive_facts.json"
DECISIONS_PATH = REPORTS / "stage_d1f_decisions.json"
STEP8_OUTPUTS = (TIER_A_PATH, TIER_B_PATH, FACTS_PATH, DECISIONS_PATH)
D1D_ACCOUNTING = REPORTS / "stage_d1d_accounting.json"
SHARPE_TOLERANCE = 1e-6
N_CONTINUITY_RUNS = 33  # the 31 trials, plus E-H1 and E-H2 on their confirmation factories
RC_REFUSED, RC_EMPTY_WINDOW, RC_CONTINUITY = 2, 3, 4
_CONFIRMATION_INPUTS = ConfirmationInputs.under(VENDOR_ROOT)
# Review F5: run-session inputs that cannot be in the freeze manifest; pinned at step 5.
RUN_INPUTS: Mapping[str, Path] = MappingProxyType({
    "confirmation_parquet": CONFIRMATION_SERIES_PATH,
    "build_summary": CONFIRMATION_SUMMARY_PATH,
    "rolls": _CONFIRMATION_INPUTS.rolls,
    "condition": _CONFIRMATION_INPUTS.condition,
    "symbology": _CONFIRMATION_INPUTS.symbology,
    "holdout2_manifest": HOLDOUT2_PATHS.manifest,
})
_SHA256_HEX = re.compile(r"[0-9a-f]{64}")


class StepRefused(RuntimeError):
    """A step's precondition failed; nothing was written."""


# ---------------------------------------------------------------------- JSON ----
def plain(value: object) -> object:
    """JSON-ready: mappings, sequences, numpy scalars, dates; non-finite floats -> None."""
    if isinstance(value, Mapping | MappingProxyType):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, list | tuple | set | frozenset | np.ndarray):
        return [plain(v) for v in (sorted(value) if isinstance(value, set | frozenset)
                                   else value)]
    if isinstance(value, np.generic):
        return plain(value.item())
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, date):
        return value.isoformat()
    return value


def write_once(path: Path, payload: dict) -> str:
    """Create ``path`` exclusively (a step's output is never overwritten); return its sha256."""
    blob = (json.dumps(plain(payload), indent=1) + "\n").encode()
    try:
        with Path(path).open("xb") as fh:
            fh.write(blob)
    except FileExistsError as exc:
        raise StepRefused(f"{path} exists: a finished step is never re-run or overwritten "
                          "(move it aside deliberately, and log why)") from exc
    return sha256_bytes(blob)


def read_step(path: Path, manifest_sha: str, what: str) -> dict:
    if not Path(path).is_file():
        raise StepRefused(f"{what} has not run: {path} is missing")
    payload = json.loads(Path(path).read_text())
    if payload.get("manifest_sha256") != manifest_sha:
        raise StepRefused(f"{path} was written under another freeze manifest")
    return payload


def _refuse_if_decided() -> None:
    done = [p.name for p in STEP8_OUTPUTS if p.exists()]
    if done:
        raise StepRefused(f"step 8 outputs exist ({done}): steps 5 to 8 are not revisited")


def environment() -> dict:
    """Interpreter and library versions of this process (review N5). scipy is recorded only if
    something imported it (nothing on the runner's path does); databento is imported here for
    its version only: the runner makes no vendor call."""
    import databento

    scipy = sys.modules.get("scipy")
    return {"python": sys.version, "numpy": np.__version__, "pandas": pd.__version__,
            "pyarrow": pa.__version__, "scipy": getattr(scipy, "__version__", None),
            "databento": databento.__version__}


def run_input_hashes(paths: Mapping[str, Path] | None = None) -> dict[str, dict]:
    """sha256 of every run-session input (``RUN_INPUTS``); None for a missing file."""
    out = {}
    for name, path in (RUN_INPUTS if paths is None else paths).items():
        path = Path(path)
        shown = (path.relative_to(REPO_ROOT).as_posix() if path.is_relative_to(REPO_ROOT)
                 else str(path))
        out[name] = {"path": shown, "sha256": sha256_file(path) if path.is_file() else None}
    return out


def changed_run_inputs(pinned: Mapping | None, now: Mapping) -> list[str]:
    """Differences between step 5's pinned run inputs and ``now`` (review F5)."""
    if not isinstance(pinned, Mapping) or not pinned:
        return ["step 5's output pins no run inputs"]
    problems = [f"run input {k}: {dict(pinned.get(k) or {})} at step 5, {dict(now.get(k) or {})} "
                "now" for k in sorted(set(pinned) | set(now)) if pinned.get(k) != now.get(k)]
    problems += [f"run input {k} was missing at step 5" for k, v in sorted(pinned.items())
                 if not isinstance(v, Mapping) or v.get("sha256") is None]
    return problems


def _header(pre: Preflight) -> dict:
    return {"stage": "D.1f", "manifest_sha256": pre.manifest_sha256,
            "list_sha256": sha256_file(REPO_ROOT / LIST_PATH),
            "criteria_sha256": sha256_file(REPO_ROOT / CRITERIA_PATH),
            "generated_local": datetime.now().astimezone().isoformat(timespec="seconds"),
            "environment": environment(), "run_inputs_sha256": run_input_hashes(),
            "preflight": pre.records}


def read_start(pre: Preflight) -> dict:
    """Step 5's output, refused unless every run input still hashes as step 5 pinned it."""
    start = read_step(START_RULE_PATH, pre.manifest_sha256, "step 5")
    problems = changed_run_inputs(start.get("run_inputs_sha256"), run_input_hashes())
    if problems:
        raise StepRefused("run-session inputs changed since step 5: " + "; ".join(problems))
    return start


# ------------------------------------------------------------------ step 5 ----
def compute_start_rule(parquet: Path = CONFIRMATION_SERIES_PATH) -> dict:
    research = load_research_bars(COLUMNS)
    confirmation = load_confirmation_bars(COLUMNS, path=parquet)
    return start_rule(rth_monthly_median_volume(research),
                      rth_monthly_median_volume(confirmation),
                      first_trade_date_by_month(confirmation))


def step5(pre: Preflight) -> int:
    before = run_input_hashes()
    missing = [k for k, v in before.items() if v["sha256"] is None]
    if missing:
        raise StepRefused(f"run-session inputs missing, nothing to pin: {missing}")
    record = compute_start_rule()
    payload = {**_header(pre), "step": 5, "start_rule": record,
               "degraded_dates_logged_before_step_5": pre.records["build"]}
    changed = changed_run_inputs(before, payload["run_inputs_sha256"])
    if changed:
        raise StepRefused(f"run-session inputs changed while step 5 ran: {changed}")
    write_once(START_RULE_PATH, payload)
    print(f"step 5: V_ref {record['v_ref']}; S = {record['S']}; sensitivity "
          f"{[(s['fraction'], s['s']) for s in record['sensitivity']]}")
    if record["empty_window"]:
        print("step 5: NO MONTH QUALIFIES: the confirmation window is empty; D.1f stops (D-1)")
        return RC_EMPTY_WINDOW
    return 0


# ------------------------------------------------------------ pool screening ----
_JOBS: tuple = ()
_WINDOW: object = None


@contextmanager
def _keep_backtest_results(sink: list) -> Iterator[None]:
    """Keep the BacktestResult of the screen's own ``run_backtest`` call, so the forced exits
    are read from the very ledger the report was measured from (review F6). ``screen_frame``
    looks ``run_backtest`` up in screening.runner's namespace at call time; the wrapper only
    keeps a reference to what it returns and is removed on exit."""
    original = screening.runner.run_backtest

    def keep(*args: object, **kwargs: object) -> object:
        result = original(*args, **kwargs)
        sink.append(result)
        return result

    screening.runner.run_backtest = keep
    try:
        yield
    finally:
        screening.runner.run_backtest = original


def ledger_forced_exit_dates(fills: Iterable[FillEvent], bar_ts: np.ndarray,
                             bar_days: np.ndarray) -> tuple[date, ...]:
    """Trade dates of every fill the strategy did not ask for (reason != "strategy": the forced
    flattens, the end-of-data close, an MLL liquidation), each mapped to the trade date of the
    bar it happened on exactly as screening.runner._fill_trade_date maps it."""
    return tuple(sorted({_fill_trade_date(bar_ts, bar_days, f.fill_ts_ns) for f in fills
                         if f.reason != "strategy"}))


def forced_exit_record(instance: Iterable[date], ledger: Iterable[date]) -> dict:
    """Both sets; the ledger's count is the reported count; a difference is flagged, never
    refused (review F6)."""
    inst, led = sorted(set(instance)), sorted(set(ledger))
    return {"forced_exit_dates_ledger": [d.isoformat() for d in led],
            "forced_exit_dates_instance": [d.isoformat() for d in inst],
            "n_forced_exits": len(led), "n_forced_exits_instance": len(inst),
            "forced_exit_sets_differ": inst != led,
            "only_in_ledger": [d.isoformat() for d in sorted(set(led) - set(inst))],
            "only_in_instance": [d.isoformat() for d in sorted(set(inst) - set(led))]}


def _window_bar_index(window: object) -> tuple[np.ndarray, np.ndarray]:
    """(bar open ns, trade date) of the window's bars, the frame the screen ran on."""
    frame, days = (_confirmation_frame(window.path) if isinstance(window, ConfirmationWindow)
                   else _research_frame())
    mask = np.isin(days, np.array(window.trade_dates, dtype=object))
    return frame["ts_event"].to_numpy(dtype="int64")[mask], frame["trade_date"].to_numpy()[mask]


def _screen_job(index: int) -> dict:
    label, factory, tag = _JOBS[index]
    made: list[object] = []
    results: list = []

    def make() -> object:
        made.append(factory())
        return made[-1]

    try:
        with _keep_backtest_results(results):
            report = screen_candidate(label, make, _WINDOW)
        out = {"index": index, "label": label, "tag": tag, "report": report.to_dict()}
        forced = getattr(made[-1], "forced_exit_dates", None) if made else None
        if forced is not None:
            if len(made) != 1 or len(results) != 1:
                raise AssertionError(f"{len(made)} instances / {len(results)} backtests for one "
                                     "screen: the ledger cannot be matched to the instance")
            ledger = ledger_forced_exit_dates(results[0].events(FillEvent),
                                              *_window_bar_index(_WINDOW))
            out["forced_exits"] = forced_exit_record(forced, ledger)
    except Exception as exc:  # recorded, never swallowed: the caller refuses on any error
        return {"index": index, "label": label, "tag": tag, "error": repr(exc)}
    return out


def run_screens(jobs: Sequence[tuple], window: object, processes: int) -> list[dict]:
    """Screen every (label, factory, tag) on ``window``; any error refuses."""
    global _JOBS, _WINDOW
    _JOBS, _WINDOW = tuple(jobs), window
    try:
        if processes <= 1:
            results = [_screen_job(i) for i in range(len(_JOBS))]
        else:
            with mp.get_context("fork").Pool(processes=min(processes, len(_JOBS))) as pool:
                results = pool.map(_screen_job, range(len(_JOBS)), chunksize=1)
    finally:
        _JOBS, _WINDOW = (), None
    errors = [r for r in results if "error" in r]
    if errors:
        raise StepRefused("screens errored: " + "; ".join(f"{r['label']} ({r['tag']}): "
                                                          f"{r['error']}" for r in errors))
    return results


# ------------------------------------------------------------------ step 6 ----
def continuity_problems(runs: Sequence[dict], recorded: Mapping) -> list[str]:
    """Net P&L to the cent, trip count exactly, daily Sharpe to 1e-6, per run."""
    rows = {r["label"]: r for r in recorded["runs"]}
    per_trial = recorded["per_trial"]
    problems = []
    if len(runs) != N_CONTINUITY_RUNS:
        problems.append(f"{len(runs)} continuity runs, expected {N_CONTINUITY_RUNS}")
    if {r["label"] for r in runs} != set(rows):
        problems.append("the continuity runs do not cover exactly the recorded trials")
    for run in runs:
        rep, want = run["report"], rows.get(run["label"])
        name = f"{run['label']} ({run['tag']})"
        if want is None:
            continue
        if round(rep["net_pnl_usd"], 2) != round(want["net_pnl_usd"], 2):
            problems.append(f"{name}: net {rep['net_pnl_usd']} != {want['net_pnl_usd']}")
        if rep["n_trips"] != want["n_trips"]:
            problems.append(f"{name}: trips {rep['n_trips']} != {want['n_trips']}")
        sharpe = _moments([float(x) for x in rep["daily_net_usd"]])["sharpe"]
        if abs(sharpe - per_trial[run["label"]]["sharpe"]) > SHARPE_TOLERANCE:
            problems.append(f"{name}: daily Sharpe {sharpe:.6f} != "
                            f"{per_trial[run['label']]['sharpe']:.6f}")
    return problems


def step6(pre: Preflight, processes: int) -> int:
    read_start(pre)
    _research_frame()  # loaded once in the parent; forked workers inherit the cache
    window = train_union_window()
    runs = run_screens(continuity_trials(), window, processes)
    problems = continuity_problems(runs, json.loads(D1D_ACCOUNTING.read_text()))
    write_once(CONTINUITY_PATH, {
        **_header(pre), "step": 6, "window": {"name": window.name,
                                              "n_dates": len(window.trade_dates)},
        "passed": not problems, "problems": problems,
        "runs": [{"label": r["label"], "tag": r["tag"],
                  "net_pnl_usd": r["report"]["net_pnl_usd"], "n_trips": r["report"]["n_trips"],
                  "daily_sharpe": _moments([float(x) for x in r["report"]["daily_net_usd"]]
                                           )["sharpe"]} for r in runs]})
    print(f"step 6: {len(runs)} continuity runs, {len(problems)} problems")
    for p in problems:
        print("  PROBLEM", p)
    return RC_CONTINUITY if problems else 0


# ------------------------------------------------------------------ step 7 ----
def member_record(member: Member, dates_ref: str) -> dict:
    return {"id": member.member_id, "tier": member.tier, "kind": member.kind,
            "class": member.klass, "dates_ref": dates_ref, "composite": member.composite,
            "direction": member.direction, "daily": member.daily,
            "daily_activity": member.daily_activity, "extra": member.extra}


def member_from_record(record: Mapping, dates: Mapping[str, Sequence[date]]) -> Member:
    return Member(record["id"], record["tier"], record["kind"], record["class"],
                  tuple(dates[record["dates_ref"]]), np.asarray(record["daily"], dtype=float),
                  np.asarray(record["daily_activity"], dtype=np.int64), record["composite"],
                  record["direction"], record["extra"])


def run_trials(window: object, processes: int) -> tuple[list[Member], list[dict]]:
    jobs = [(label, factory, klass) for label, factory, klass in tier_a_trials()]
    results = run_screens(jobs, window, processes)
    members, raw = [], []
    for r in results:
        extra = r.get("forced_exits", {})
        if extra.get("forced_exit_sets_differ"):
            print(f"FLAG {r['label']}: forced exits differ between the ledger "
                  f"({extra['n_forced_exits']}, reported) and the instance "
                  f"({extra['n_forced_exits_instance']}): only in the ledger "
                  f"{extra['only_in_ledger']}, only in the instance {extra['only_in_instance']}")
        members.append(trial_member(r["label"], r["tag"], r["report"], window.trade_dates,
                                    extra))  # a trial job's tag is its class
        raw.append({"label": r["label"], **{k: r["report"][k] for k in (
            "trip_pnls_usd", "trip_micros", "daily_n_trips", "daily_net_usd")}})
    return members, raw


def run_statistics(window: object, gate_json: Path = POWER_GATE_JSON
                   ) -> tuple[list[Member], dict]:
    frame, days = _confirmation_frame(window.path)
    bars = frame[np.isin(days, np.array(window.trade_dates, dtype=object))]
    run = compute_statistics(bars, window.trade_dates,
                             splice_trade_dates_from_parquet(window.path))
    stat_bars = select_statistic_bars(bars, run.dates)
    directions = statistic_directions(recorded_edges())
    members = []
    for sid, (tier, klass, s) in directions.items():
        ev = run.directional[sid]
        composite = (statistic_composite(ev, s, run.dates, stat_bars, gate_json)
                     if tier == "A" else None)
        members.append(statistic_member(ev, tier, klass, s, run.dates, composite))
    facts = {"statistic_dates": run.dates, "excluded": run.excluded,
             "non_directional_facts": run.descriptive, "g0": run.g0,
             "f3_1_table": run.f3_1_table, "thresholds": run.thresholds,
             "directional_on_confirmation": {
                 sid: {"estimate": ev.estimate, "n": ev.n,
                       "implied_edge_ticks": ev.implied_edge_ticks, "extra": ev.extra}
                 for sid, ev in run.directional.items()}}
    return members, facts


def step7(pre: Preflight, processes: int) -> int:
    start = read_start(pre)
    continuity = read_step(CONTINUITY_PATH, pre.manifest_sha256, "step 6")
    if not continuity["passed"] or start["start_rule"]["S"] is None:
        raise StepRefused("step 6 did not pass or S is undefined: the list does not run")
    window = confirmation_window(date.fromisoformat(start["start_rule"]["S"]))
    _confirmation_frame(window.path)  # loaded once in the parent for the forked workers
    trials, raw_trials = run_trials(window, processes)
    statistics, facts = run_statistics(window)
    write_once(LIST_RUN_PATH, {
        **_header(pre), "step": 7, "S": start["start_rule"]["S"], "window": window.name,
        "window_dates": window.trade_dates, "statistic_dates": facts["statistic_dates"],
        "members": [member_record(m, "window") for m in trials]
        + [member_record(m, "statistic") for m in statistics],
        "raw_trial_series": raw_trials, "facts": facts})
    print(f"step 7: {len(trials)} trials and {len(statistics)} statistics on {window.name}")
    return 0


# ------------------------------------------------------------------ step 8 ----
def split_tiers(members: Sequence[Member]) -> tuple[list[Member], list[Member]]:
    tier_a = [m for m in members if m.tier == "A"]
    tier_b = [m for m in members if m.tier == "B"]
    if (len(tier_a), len(tier_b)) != (N_TIER_A, N_TIER_B):
        raise StepRefused(f"the list holds {len(tier_a)} Tier A / {len(tier_b)} Tier B members, "
                          f"not {N_TIER_A} / {N_TIER_B}")
    return tier_a, tier_b


def summarize(ev: Evaluation) -> dict:
    rows = {**ev.tier_a, **ev.tier_b}
    return {
        "n_after_d1f": ev.family["n_trials"]["after_d1f"],
        "passing_confirmation": sorted(k for k, r in ev.tier_a.items() if r["status"] == "edge"),
        "holm_rejected": ev.family["holm"]["rejected"],
        "inconclusive": sorted(k for k, r in rows.items() if r["status"] == "inconclusive"),
        "null_by_inactivity": sorted(k for k, r in rows.items()
                                     if "null by inactivity" in r["labels"]),
        "tier_b_anomalies": sorted(k for k, r in ev.tier_b.items() if r["anomaly"]["flag"]),
        "tier_b_sign_reversals": sorted(k for k, r in ev.tier_b.items()
                                        if r["sign_reversal"]["flag"]),
        "class_verdicts": {k: v["verdict"] for k, v in ev.classes.items()},
    }


def step8(pre: Preflight, recheck: Callable[[], tuple[list[str], str | None]] = hash_checks
          ) -> int:
    start = read_start(pre)
    continuity = read_step(CONTINUITY_PATH, pre.manifest_sha256, "step 6")
    listed = read_step(LIST_RUN_PATH, pre.manifest_sha256, "step 7")
    dates = {"window": [date.fromisoformat(d) for d in listed["window_dates"]],
             "statistic": [date.fromisoformat(d) for d in listed["statistic_dates"]]}
    tier_a, tier_b = split_tiers([member_from_record(r, dates) for r in listed["members"]])
    ev = evaluate(tier_a, tier_b, dates["window"])
    problems, manifest_sha = recheck()
    void = bool(problems) or manifest_sha != pre.manifest_sha256
    header = {**_header(pre), "step": 8, "S": start["start_rule"]["S"],
              "start_rule": start["start_rule"],
              "continuity": {k: continuity[k] for k in ("passed", "problems", "window")},
              "list_run_sha256": sha256_file(LIST_RUN_PATH),
              "void": void, "void_reasons": problems + (
                  [] if manifest_sha == pre.manifest_sha256 else ["manifest sha256 changed"])}
    shas = {
        "tier_a": write_once(TIER_A_PATH, {**header, "tier": "A", "members": ev.tier_a,
                                           "family": ev.family}),
        "tier_b": write_once(TIER_B_PATH, {**header, "tier": "B", "members": ev.tier_b,
                                           "bh": ev.family["tier_b_bh"]}),
        "facts": write_once(FACTS_PATH, {**header, **listed["facts"]}),
    }
    write_once(DECISIONS_PATH, {**header, "summary": summarize(ev), "classes": ev.classes,
                                "family": ev.family,
                                "outputs_sha256": shas})
    print(f"step 8: {summarize(ev)['class_verdicts']}; void = {void}")
    return RC_REFUSED if void else 0


# --------------------------------------------------------------------- CLI ----
STEPS = ("preflight", "5", "6", "7", "8", "all")


def declared_manifest_problems(pre: Preflight, declared_sha256: str) -> list[str]:
    """Review F1: the manifest on disk must be the one declared at the freeze commit."""
    if pre.manifest_sha256 == declared_sha256:
        return []
    return [f"freeze manifest sha256 {pre.manifest_sha256} is not the declared "
            f"{declared_sha256} (a re-frozen or edited manifest voids the run)"]


def run_step(step: str, processes: int, declared_sha256: str) -> int:
    pre = preflight()
    problems = [*pre.problems, *declared_manifest_problems(pre, declared_sha256)]
    if problems:
        print("REFUSED by the preflight checks:")
        for p in problems:
            print("  -", p)
        return RC_REFUSED
    print(f"preflight passed; manifest sha256 {pre.manifest_sha256} (as declared)")
    if step == "preflight":
        return 0
    _refuse_if_decided()
    runners = {"5": lambda: step5(pre), "6": lambda: step6(pre, processes),
               "7": lambda: step7(pre, processes), "8": lambda: step8(pre)}
    return runners[step]()


def _sha256_hex(text: str) -> str:
    if not _SHA256_HEX.fullmatch(text):
        raise argparse.ArgumentTypeError("expected 64 lowercase hex digits")
    return text


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Stage D.1f list runner (steps 5 to 8)")
    parser.add_argument("--step", choices=STEPS, required=True)
    parser.add_argument("--manifest-sha256", type=_sha256_hex, required=True,
                        help="the freeze manifest's sha256 declared at the freeze commit")
    parser.add_argument("--processes", type=int, default=12)
    args = parser.parse_args(argv)
    steps = ("5", "6", "7", "8") if args.step == "all" else (args.step,)
    for step in steps:
        try:
            rc = run_step(step, args.processes, args.manifest_sha256)
        except StepRefused as exc:
            print(f"REFUSED at step {step}: {exc}")
            return RC_REFUSED
        if rc:
            return rc
    return 0


if __name__ == "__main__":
    sys.exit(main())
