"""The Stage E runner launched both ways on one synthetic repository (Stage E.4 H1, bug C-1).

Launch 1 is a real ``python -m screening.stage_e_runner`` process. Launch 2 is ``main()`` called on
the imported module (the path E.3's ruling R-T5-1 used). Under ``python -m`` the runner file runs
as ``__main__``, while screening.stage_e_start_dates raises its refusals through ``_runner()``
(``from screening import stage_e_runner``). Before the fix those were a second copy of every
refusal class, so the runner's ``except (RunnerRefusal, StageEBarRefusal)`` missed them.

The child process gets the synthetic world through a ``sitecustomize`` module on its PYTHONPATH
(tmp_path only; nothing under reports/ or data/ is read for the case or written). The hook
patches the modules the runner imports from, never the runner itself, so the same patches reach
the ``__main__`` copy (before the fix) and the imported module (after it):
- screening.harness_freeze.preflight: the synthetic hash is accepted (the repository's manifest
  is the lead's to rebuild);
- screening.stage_e_freeze.load_cluster_freeze: the cluster freeze under tmp_path;
- screening.stage_e_frozen.leg_inputs: the synthetic research parquet's sha256;
- screening.stage_e_rules.load_release_calendar: an empty calendar covering the window;
- screening.stage_e_start_dates.start_rule_files: member i's own start-rule directory (one
  lookup per member that reaches the power check, in ordinal order);
- screening.stage_e_engine.run_engine: the real engine, or a planted engine-level refusal for
  the last members, and a note of which module called it.

Every start-date refusal the runner can meet on a research run is one member of the cluster
(CASES), so one ``--all`` run shows each one caught and recorded by name, under both launches.
This module imports nothing from the Stage E harness at import time: the child imports it from
``sitecustomize`` before the runner exists, and it must not load the runner early.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import date, timedelta
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
RUNNER = "screening.stage_e_runner"
CONFIG_ENV = "PROPEXPERIMENT_E4_LAUNCH_CONFIG"
HARNESS = "a" * 64
CLUSTER = "K1"
ROOT = "ZN"
DAYS = tuple(date(2025, 6, 2) + timedelta(days=i) for i in range(12)
             if (date(2025, 6, 2) + timedelta(days=i)).weekday() < 5)
CHILD_TIMEOUT_S = 600


@dataclass(frozen=True)
class Case:
    """One member of the synthetic cluster and the refusal it must meet.

    ``kind`` "start": the power check's start-rule lookup reads ``files`` (name -> text) and must
    record ``power: not_run`` with ``cls`` and ``fragment`` in the reason. ``kind`` "engine": the
    engine raises ``cls`` and the member must be a ``refused_case`` naming it."""

    case_id: str
    kind: str
    cls: str
    fragment: str
    site: str  # where the refusal is raised (for the report)
    files: tuple[tuple[str, str], ...] = ()


def label(ordinal: int, case: Case) -> str:
    return f"{CLUSTER}-c{ordinal:02d}-{case.case_id} {ROOT}"


def _doc(set_id: str, products: dict, **over: Any) -> str:
    from screening import stage_e_start_dates as sd

    return json.dumps({"schema": sd.SCHEMA, "set": set_id, "products": products, "inputs": [],
                       "harness_sha256": HARNESS, "created_pdt": "2026-09-27T02:00:00-07:00",
                       **over})


def _one(products: dict, **over: Any) -> tuple[tuple[str, str], ...]:
    return (("stage_e_start_rule_K2.json", _doc("K2", products, **over)),)


def _without(entry: dict, key: str) -> dict:
    return {k: v for k, v in entry.items() if k != key}


def start_cases() -> tuple[Case, ...]:
    """Every raise in screening.stage_e_start_dates that a research run's power check can meet
    (all of them through ``_runner()``), then one bar refusal (data.stage_e_bars, the other
    class the runner's except names) as a control."""
    from tests.test_stage_e_start_dates import consistent_entry

    good, empty = consistent_entry("2019-05-06"), consistent_entry(None)
    first = dict(empty["first_trade_dates"])
    sd = "stage_e_start_dates"
    inv, inc = "StartRuleInvalid", "StartRuleInconsistent"
    return (
        Case("missing", "start", "StartRuleMissing", "no frozen S_X for ['ZN']",
             f"{sd}.start_dates_for (E.3's crash)"),
        Case("not_json", "start", inv, "not valid JSON", f"{sd}._parse_file",
             (("stage_e_start_rule_K2.json", "{not json"),)),
        Case("file_name", "start", inv, "not a stage_e_start_rule_<K1..K8|ML>.json file name",
             f"{sd}._parse_doc (name)",
             (("stage_e_start_rule_K2_copy.json", _doc("K2", {ROOT: good})),)),
        Case("schema", "start", inv, "schema 'stage_e_start_rule/1'", f"{sd}._parse_doc (schema)",
             _one({ROOT: good}, schema="stage_e_start_rule/1")),
        Case("set", "start", inv, "set 'K3' is not the file's 'K2'", f"{sd}._parse_doc (set)",
             _one({ROOT: good}, set="K3")),
        Case("no_products", "start", inv, "no products", f"{sd}._parse_doc (products)",
             _one({})),
        Case("no_s_x", "start", inv, "ZN has no s_x", f"{sd}._root_values (s_x)",
             _one({ROOT: {"v_ref": 1.0}})),
        Case("s_x_not_iso", "start", inv, "is not an ISO date", f"{sd}._day (ISO)",
             _one({ROOT: good | {"s_x": "2019-5-6"}})),
        Case("s_x_form", "start", inv, "is not in YYYY-MM-DD form", f"{sd}._day (form)",
             _one({ROOT: good | {"s_x": "20190506"}})),
        Case("s_x_outside", "start", inv, "is outside", f"{sd}._s_x",
             _one({ROOT: good | {"s_x": "2024-03-01"}})),
        Case("v_ref", "start", inv, "v_ref 0 is not a finite number > 0",
             f"{sd}._root_values (v_ref)", _one({ROOT: empty | {"v_ref": 0}})),
        Case("no_medians", "start", inv, "has no monthly_medians mapping", f"{sd}._medians (map)",
             _one({ROOT: _without(empty, "monthly_medians")})),
        Case("bad_median", "start", inv, "monthly median '2019-05': -1.0",
             f"{sd}._medians (value)",
             _one({ROOT: empty | {"monthly_medians": {"2019-05": -1.0}}})),
        Case("no_first_dates", "start", inv, "has no first_trade_dates mapping",
             f"{sd}._first_dates", _one({ROOT: _without(empty, "first_trade_dates")})),
        Case("first_date_form", "start", inv, "first trade date of 2019-05",
             f"{sd}._day via _first_dates",
             _one({ROOT: empty | {"first_trade_dates": first | {"2019-05": "20190506"}}})),
        Case("step2_sha", "start", inv, "step2_sha256 None is not a sha256",
             f"{sd}._root_values (step2_sha256)", _one({ROOT: empty | {"step2_sha256": None}})),
        Case("cannot_rerun", "start", inc, "do not re-run D4's rule",
             f"{sd}._check_follows (re-run)",
             _one({ROOT: good | {"monthly_medians": _without(good["monthly_medians"],
                                                             "2025-09")}})),
        Case("doctored", "start", inc, "['s_x'] do not follow", f"{sd}._check_follows (recorded)",
             _one({ROOT: good | {"s_x": "2023-06-15"}})),
        Case("conflict", "start", "StartRuleConflict", "ZN: the start-rule files differ on",
             f"{sd}.load_start_entries",
             (("stage_e_start_rule_K2.json", _doc("K2", {ROOT: good})),
              ("stage_e_start_rule_ML.json", _doc("ML", {ROOT: consistent_entry("2019-06-03")})))),
        Case("no_step2_store", "start", "ConfirmationStoreMissing", "",
             "data.stage_e_bars.read_leg_dates (control: not through _runner())",
             _one({ROOT: good})),
    )


ENGINE_CASES = (
    Case("engine_refused", "engine", "EngineRefusedCase", "planted engine refusal",
         "screening.stage_e_engine.run_engine (control, OC-T)"),
    Case("frozen_input", "engine", "FrozenInputError", "planted frozen-input error",
         "screening.stage_e_frozen via the engine (control, OC-T)"),
)


def all_cases() -> tuple[Case, ...]:
    # engine cases last: they never reach the power check, so the start-rule lookups stay in
    # step with the members
    return start_cases() + ENGINE_CASES


# ------------------------------------------------------------------- the world ----
def build_world(tmp: Path, monkeypatch: Any, cases: tuple[Case, ...]) -> dict:
    """The synthetic repository under ``tmp``: one member module, the cluster freeze (one member
    per case, ordinal = position), the research parquet, per-member start-rule directories and
    the child's config and ``sitecustomize``. Returns the config."""
    from data.stage_e_bars import research_parquet_path
    from screening.stage_e_freeze import MemberDecl, write_cluster_freeze
    from strategy.stage_e.interface import LegSpec
    from tests._stage_e_synthetic import install_member_package, product_frame, write_parquet

    module = install_member_package(tmp, monkeypatch)
    legs = (LegSpec(ROOT, True),)
    write_cluster_freeze(CLUSTER, [MemberDecl(label(i, c), i, module, "make_member", legs)
                                   for i, c in enumerate(cases, start=1)], root=tmp)
    research = tmp / "research"
    path = research_parquet_path(ROOT, research)
    write_parquet(product_frame(ROOT, DAYS, 5, start=(9, 0), end=(10, 0)), path, {"rolls": []})
    start_dirs = []
    for i, case in enumerate(c for c in cases if c.kind == "start"):
        base = tmp / "start_rules" / f"{i:02d}"
        (base / "reports").mkdir(parents=True)
        for name, text in case.files:
            (base / "reports" / name).write_text(text, encoding="utf-8")
        start_dirs.append(str(base))
    cfg = {"root": str(tmp), "research_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
           "start_dirs": start_dirs, "engine": [c.cls if c.kind == "engine" else None
                                                for c in cases],
           "callers": str(tmp / "engine_callers.txt"), "installed": str(tmp / "installed.txt"),
           "research_root": str(research), "step2_root": str(tmp / "no_step2"),
           "out_dir": str(tmp / "out")}
    config = tmp / "launch_config.json"
    config.write_text(json.dumps(cfg), encoding="utf-8")
    hooks = tmp / "hooks"
    hooks.mkdir()
    (hooks / "sitecustomize.py").write_text(
        "from tests._stage_e_launch import install_in_child\n\ninstall_in_child()\n",
        encoding="utf-8")
    return cfg | {"config": str(config), "hooks": str(hooks)}


def argv(cfg: dict, *who: str) -> list[str]:
    return ["--harness-sha256", HARNESS, "--cluster", CLUSTER, *(who or ("--all",)),
            "--window", "research", "--research-root", cfg["research_root"],
            "--step2-root", cfg["step2_root"], "--out-dir", cfg["out_dir"]]


# ----------------------------------------------------------------- the patches ----
def replacements(cfg: dict) -> dict[tuple[str, str], Callable]:
    """(module, attribute) -> replacement; each call starts its own counters."""
    from screening import stage_e_engine, stage_e_freeze, stage_e_frozen
    from screening import stage_e_start_dates as sd
    from screening.stage_e_rules import ReleaseCalendar

    real_load, real_inputs = stage_e_freeze.load_cluster_freeze, stage_e_frozen.leg_inputs
    real_files, real_engine = sd.start_rule_files, stage_e_engine.run_engine
    starts, engine = list(cfg["start_dirs"]), list(cfg["engine"])
    calls = {"start": 0, "engine": 0}

    def start_rule_files(_root: Path | None = None) -> tuple[Path, ...]:
        if calls["start"] >= len(starts):
            raise AssertionError("more start-rule lookups than start cases")
        calls["start"] += 1
        return real_files(Path(starts[calls["start"] - 1]))

    def run_engine(frames, member, legs, rules):  # noqa: ANN001, ANN202 - the engine's own
        caller = sys._getframe(1).f_globals.get("__name__")
        with open(cfg["callers"], "a", encoding="utf-8") as fh:
            fh.write(f"{caller}\n")
        planted = engine[calls["engine"]]
        calls["engine"] += 1
        if planted == "EngineRefusedCase":
            raise stage_e_engine.EngineRefusedCase("synthetic: planted engine refusal")
        if planted == "FrozenInputError":
            raise stage_e_frozen.FrozenInputError("synthetic: planted frozen-input error")
        return real_engine(frames, member, legs, rules)

    return {
        ("screening.harness_freeze", "preflight"): lambda expected, root=None: expected,
        ("screening.stage_e_freeze", "load_cluster_freeze"):
            lambda cluster, root=None: real_load(cluster, root=Path(cfg["root"])),
        ("screening.stage_e_frozen", "leg_inputs"):
            lambda r, *, traded, tables=None: replace(
                real_inputs(r, traded=traded, tables=tables),
                research_parquet_sha256=cfg["research_sha256"]),
        ("screening.stage_e_rules", "load_release_calendar"):
            lambda: ReleaseCalendar({}, (), date(2019, 5, 1), date(2026, 6, 19), "c" * 64,
                                    "synthetic"),
        ("screening.stage_e_start_dates", "start_rule_files"): start_rule_files,
        ("screening.stage_e_engine", "run_engine"): run_engine,
    }


def install_in_child() -> None:
    """Called by the child's sitecustomize, before the runner module exists."""
    import importlib

    import strategy

    cfg = json.loads(Path(os.environ[CONFIG_ENV]).read_text(encoding="utf-8"))
    if "screening.stage_e_runner" in sys.modules:
        raise AssertionError("the runner was imported before the launch")
    strategy.__path__.insert(0, str(Path(cfg["root"]) / "strategy"))
    for (module, attr), value in replacements(cfg).items():
        setattr(importlib.import_module(module), attr, value)
    if "screening.stage_e_runner" in sys.modules:
        raise AssertionError("installing the patches imported the runner")
    Path(cfg["installed"]).write_text("installed\n", encoding="utf-8")


def install_in_process(cfg: dict, monkeypatch: Any) -> None:
    """The same patches for launch 2: on their modules and on the names the imported runner
    bound from them."""
    import importlib

    import screening.stage_e_runner as runner

    for (module, attr), value in replacements(cfg).items():
        monkeypatch.setattr(importlib.import_module(module), attr, value)
        if module != "screening.stage_e_start_dates" and hasattr(runner, attr):
            monkeypatch.setattr(runner, attr, value)
    monkeypatch.setattr("compute.platform.lower_priority", lambda: None)


def launch(cfg: dict, *args: str) -> subprocess.CompletedProcess:
    """A real ``python -m screening.stage_e_runner`` process (fresh byte-code prefix)."""
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONPYCACHEPREFIX")}
    env |= {"PYTHONPATH": os.pathsep.join((cfg["hooks"], str(REPO))), CONFIG_ENV: cfg["config"],
            "PYTHONPYCACHEPREFIX": str(Path(cfg["root"]) / "pycache")}
    return subprocess.run([sys.executable, "-m", RUNNER, *args], cwd=REPO, env=env,
                          capture_output=True, text=True, encoding="utf-8",
                          timeout=CHILD_TIMEOUT_S, check=False)


def callers(cfg: dict) -> list[str]:
    path = Path(cfg["callers"])
    return path.read_text(encoding="utf-8").split() if path.exists() else []


# -------------------------------------------------------------- the outcomes ----
def record_path(cfg: dict, ordinal: int, case: Case) -> Path:
    from screening.stage_e_runner import _safe

    return Path(cfg["out_dir"]) / f"{_safe(f'{CLUSTER}_{label(ordinal, case)}_research')}.json"


def check_member(cfg: dict, ordinal: int, case: Case) -> dict:
    """The member's record (read from disk) names its refusal; its trip file carries the record's
    name and sha256. Returns the record."""
    path = record_path(cfg, ordinal, case)
    raw = path.read_bytes()
    rec = json.loads(raw)
    if case.kind == "start":
        assert rec["status"] == "run", (case.case_id, rec["status"])
        assert rec["power"]["status"] == "not_run", (case.case_id, rec["power"])
        reason = rec["power"]["reason"]
    else:
        assert rec["status"] == "refused_case" and rec["power"] is None, case.case_id
        reason = rec["refusal"]
    assert reason.startswith(f"{case.cls}: ") and case.fragment in reason, (case.case_id, reason)
    trips = json.loads(path.with_name(f"{path.stem}_trips.json").read_text(encoding="utf-8"))
    assert trips["record_file"] == path.name, case.case_id
    assert trips["record_sha256"] == hashlib.sha256(raw).hexdigest(), case.case_id
    assert trips["status"] == rec["status"] and trips["member"] == rec["member"], case.case_id
    assert (len(trips["trips"]) == rec["series"]["n_trips"] > 0 if case.kind == "start"
            else trips["trips"] == []), case.case_id
    return rec
