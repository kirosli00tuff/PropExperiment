"""Stage E.12 Task 1b: build -> register -> run on fixture stores through the CLI
(ml_route_v2/phase1; lead rule P-2; design V2.2b). Synthetic stores only. The CLI takes no path
(freeze review F-2): the tests point its canonical module constants (cli.FREEZE_ROOT,
REPORTS_DIR, LEDGER_PATH, STATE_DIR, WORLD_KW) at tmp dirs and stub the harness preflight; the
vehicles come from the fixture ranking (F-3: ZN has no store and is dropped by name).

Covers: the P-2 list (|A| = covered signals x horizons, |B| = admissible pairs, gate0's own ids and
specs) and its registration being a no-op for the later run; the list-hash refusal; the
unregistered-test refusal; the run-once refusal; a resume after an interrupted family B (same
result, fewer fits) and the refusal to resume under changed constants; a planted gross edge
passing Gate 0 and noise failing it.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from ml_route_v2 import gate0 as g0
from ml_route_v2.constants import HORIZONS
from ml_route_v2.phase1 import cli
from ml_route_v2.phase1.build import BARS_REPORT, C_SIGMA_REPORT, load_build
from ml_route_v2.phase1.gate0_stage import (
    DONE_FILE,
    GATE0_JSON,
    GATE0_MD,
    LIST_FILE,
    Gate0AlreadyRan,
    Gate0ListError,
    list_tests,
)
from ml_route_v2.phase1.world import NO_STORE, Phase1Error
from ml_route_v2.pipeline import PipelineError
from screening import harness_freeze
from tests.test_ml_v2_phase1_support import (
    EDGE_C,
    EMPTY_ROOT,
    NO_STORE_VEHICLE,
    REQUESTED,
    VEHICLES,
    Stores,
    build_stores,
    write_freeze,
    write_ranking,
)

HARNESS = "a" * 64


@dataclass(frozen=True)
class Built:
    base: Path
    stores: Stores
    freeze_path: Path
    freeze_sha: str
    list_sha: str


def _cli(ctx: Built, step: str, where: Path, *extra: str, ledger: Path | None = None) -> int:
    """The CLI with its canonical paths pointed at ``where`` (state, reports, ledger.jsonl)."""
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(cli, "FREEZE_ROOT", ctx.base / "frozen")
        mp.setattr(cli, "REPORTS_DIR", where / "reports")
        mp.setattr(cli, "LEDGER_PATH", ledger or where / "ledger.jsonl")
        mp.setattr(cli, "STATE_DIR", where / "state")
        mp.setattr(cli, "WORLD_KW", ctx.stores.world_kw())
        mp.setattr(harness_freeze, "preflight", lambda sha: sha)
        return cli.main([step, "--harness-sha256", HARNESS, "--freeze-sha256", ctx.freeze_sha,
                         *extra])


def _built(base: Path, stores: Stores) -> Built:
    freeze_path, freeze_sha = write_freeze(base / "frozen", {"ml_route_v2/x.py": b"X = 1\n"})
    ctx = Built(base, stores, freeze_path, freeze_sha, "")
    write_ranking(base / "reports")
    assert _cli(ctx, "build", base) == 0
    assert _cli(ctx, "register", base) == 0
    sha = __import__("hashlib").sha256((base / "reports" / LIST_FILE).read_bytes()).hexdigest()
    return Built(base, stores, freeze_path, freeze_sha, sha)


def _copy(ctx: Built, dest: Path) -> tuple[Path, Path, Path]:
    """A fresh copy of the registered build (state, reports, ledger) under ``dest``."""
    shutil.copytree(ctx.base / "state", dest / "state")
    shutil.copytree(ctx.base / "reports", dest / "reports")
    shutil.copy(ctx.base / "ledger.jsonl", dest / "ledger.jsonl")
    return dest / "state", dest / "reports", dest / "ledger.jsonl"


def _run(ctx: Built, where: Path, sha: str | None = None, ledger: Path | None = None) -> int:
    return _cli(ctx, "run", where, "--expected-list-sha256", sha or ctx.list_sha, ledger=ledger)


@pytest.fixture(scope="module")
def edge(tmp_path_factory) -> Built:
    base = tmp_path_factory.mktemp("p1_edge")
    stores = build_stores(base / "stores", plant={"kind": "sign",
                                                  "edge_cost_multiple": EDGE_C})
    return _built(base, stores)


@pytest.fixture(scope="module")
def edge_run(edge, tmp_path_factory) -> tuple[Path, Path, Path, bytes]:
    dest = tmp_path_factory.mktemp("p1_edge_run")
    state, reports, ledger = _copy(edge, dest)
    before = ledger.read_bytes()
    assert _run(edge, dest) == 0
    return state, reports, ledger, before


@pytest.fixture(scope="module")
def noise_report(edge, tmp_path_factory) -> dict[str, Any]:
    base = tmp_path_factory.mktemp("p1_noise")
    stores = build_stores(base / "stores", plant=None, mes_path=edge.stores.mes_path,
                          mes_sha256=edge.stores.mes_start.store_sha256)
    ctx = _built(base, stores)
    assert _run(ctx, base) == 0
    return json.loads((base / "reports" / GATE0_JSON).read_text(encoding="utf-8"))


def _report(reports: Path) -> dict[str, Any]:
    return json.loads((reports / GATE0_JSON).read_text(encoding="utf-8"))


# ------------------------------------------------------------------ build and list ----
def test_build_reports_counts_coverage_and_the_filter(edge) -> None:
    bars = json.loads((edge.base / "reports" / BARS_REPORT).read_text(encoding="utf-8"))
    assert bars["vehicles"] == list(VEHICLES) and EMPTY_ROOT in bars["dropped_roots"]
    assert bars["requested_vehicles"] == list(REQUESTED)  # derived from the ranking (F-3)
    ranking = (edge.base / "reports" / "stage_e12_ranking.json").read_bytes()
    assert bars["ranking"]["sha256"] == __import__("hashlib").sha256(ranking).hexdigest()
    assert bars["ranking"]["dropped_no_store"] == {NO_STORE_VEHICLE: NO_STORE}
    build = load_build(edge.base / "state")
    assert build.out["inputs"]["ranking"]["sha256"] == bars["ranking"]["sha256"]
    assert bars["signals"]["uncovered"]["g17_nq"] == ["NQ"]
    for v in VEHICLES:
        rec = bars["rows"][v]
        assert 0 < rec["panel_rows"] < rec["decision_rows"]  # warm-up rows dropped
        assert set(rec["ok_rows"]) == set(HORIZONS)
    c_sigma = json.loads((edge.base / "reports" / C_SIGMA_REPORT).read_text(encoding="utf-8"))
    assert len(c_sigma["pairs"]) == len(VEHICLES) * len(HORIZONS)
    assert {tuple(p) for p in c_sigma["admissible"]} == {
        (p["vehicle"], p["horizon"]) for p in c_sigma["pairs"] if p["admissible"]}
    assert all("ratio" in p for p in c_sigma["dropped_pairs"])


def test_list_follows_p2_with_gate0s_own_ids_and_specs(edge) -> None:
    doc = json.loads((edge.base / "reports" / LIST_FILE).read_text(encoding="utf-8"))
    build = load_build(edge.base / "state")
    covered = list(build.panel.signal_names)
    adm = sorted(tuple(p) for p in build.filt["admissible"])
    assert doc["covered_signals"] == covered and "g17_nq" not in covered
    assert doc["n_a"] == len(covered) * len(HORIZONS) and doc["n_b"] == len(adm)
    ids = [t["test_id"] for t in doc["tests"]]
    assert ids == ([g0.family_a_id(s, h) for h in HORIZONS for s in covered]
                   + [g0.family_b_id(r, h) for r, h in adm])
    lines = (edge.base / "ledger.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == doc["n_tests"]
    assert {json.loads(x)["entry_id"] for x in lines} == set(ids)


def test_no_admissible_pair_means_no_test_as_pipeline_gate0(edge) -> None:
    build = load_build(edge.base / "state")
    assert list_tests(build.panel, ()) == []


def test_register_is_idempotent_and_refuses_a_changed_list(edge, tmp_path) -> None:
    _state, reports, ledger = _copy(edge, tmp_path)
    before = ledger.read_bytes()
    assert _cli(edge, "register", tmp_path) == 0
    assert ledger.read_bytes() == before
    path = reports / LIST_FILE
    path.chmod(0o644)
    path.write_text(path.read_text(encoding="utf-8").replace('"n_a"', '"n_a_x"'),
                    encoding="utf-8")
    with pytest.raises(Gate0ListError, match="written once"):
        _cli(edge, "register", tmp_path)


def test_a_rebuild_under_another_ranking_is_refused(edge, tmp_path) -> None:
    _copy(edge, tmp_path)
    assert _cli(edge, "build", tmp_path) == 0  # resumes: same ranking, same derived set
    write_ranking(tmp_path / "reports", (*REQUESTED,))  # the file changes (ZN removed)
    with pytest.raises(Phase1Error, match="changed input"):
        _cli(edge, "build", tmp_path)


def test_build_refuses_without_the_ranking_file(edge, tmp_path) -> None:
    with pytest.raises(Phase1Error, match="stage_e12_ranking.json does not exist"):
        _cli(edge, "build", tmp_path)
    assert not (tmp_path / "state").exists()


def test_the_cli_takes_no_path_flags(edge, tmp_path) -> None:
    for flag in ("--state-dir", "--reports-dir", "--ledger", "--freeze-manifest", "--vehicles"):
        with pytest.raises(SystemExit):
            cli.main(["build", "--harness-sha256", HARNESS, "--freeze-sha256", edge.freeze_sha,
                      flag, str(tmp_path)])


# ------------------------------------------------------------------ the run ----
def test_planted_edge_passes_and_the_registration_is_a_no_op(edge_run) -> None:
    _state, reports, ledger, before = edge_run
    rep = _report(reports)
    assert rep["verdict"] == "PASS" and rep["passing_pairs"]
    assert ledger.read_bytes() == before and rep["ledger"]["unchanged"]
    assert rep["n_contributed"] == rep["n_a"] + rep["n_b"] == len(rep["tests"])
    b = [t for t in rep["tests"] if t["family"] == "B"]
    assert all(t["n_trades"] >= 1 and t["cost_ticks"] > 0 for t in b)
    passing = [t for t in b if t["decision"] == "PASS"]
    assert all(t["gross_cost_multiple"] >= rep["rule"]["cost_multiple"] and t["holm_rejected"]
               and t["t_B"] >= rep["rule"]["t_min"] for t in passing)
    assert rep["pooled_b"]["n_trades"] == sum(t["n_trades"] for t in b)
    assert (reports / GATE0_MD).read_text(encoding="utf-8").startswith("# Stage E.12 Gate 0")


def test_noise_fails(noise_report) -> None:
    assert noise_report["verdict"] == "FAIL" and noise_report["passing_pairs"] == []
    assert noise_report["n_b"] >= 1


def test_run_once(edge, edge_run) -> None:
    state, _reports, _ledger, _before = edge_run
    assert (state / DONE_FILE).exists()
    with pytest.raises(Gate0AlreadyRan):
        _run(edge, state.parent)


def test_list_hash_and_list_content_refusals(edge, tmp_path) -> None:
    state, reports, _ledger = _copy(edge, tmp_path)
    with pytest.raises(Gate0ListError, match="not the expected"):
        _run(edge, tmp_path, sha="0" * 64)
    path = reports / LIST_FILE
    path.chmod(0o644)
    data = path.read_bytes().replace(b'"n_b": ', b'"n_b":  ')
    path.write_bytes(data)
    with pytest.raises(Gate0ListError, match="does not follow"):
        _run(edge, tmp_path, sha=__import__("hashlib").sha256(data).hexdigest())
    assert not (state / "gate0").exists()  # nothing computed


def test_an_unregistered_list_is_refused(edge, tmp_path) -> None:
    _copy(edge, tmp_path)
    with pytest.raises(Gate0ListError, match="not registered"):
        _run(edge, tmp_path, ledger=tmp_path / "empty_ledger.jsonl")


def _interrupt_after(monkeypatch, n: int) -> list[int]:
    calls = [0]
    real = g0.fit_model

    def flaky(*a, **k):
        calls[0] += 1
        if calls[0] > n:
            raise KeyboardInterrupt("simulated crash in family B")
        return real(*a, **k)

    monkeypatch.setattr(g0, "fit_model", flaky)
    return calls


def test_resume_after_an_interrupted_family_b(edge, edge_run, tmp_path, monkeypatch) -> None:
    state, reports, _ledger = _copy(edge, tmp_path)
    _interrupt_after(monkeypatch, 7)
    with pytest.raises(KeyboardInterrupt):
        _run(edge, tmp_path)
    assert not (reports / GATE0_JSON).exists() and not (state / DONE_FILE).exists()
    saved = sorted((state / "gate0").glob("gate0B_*_s*.npy"))
    assert len(saved) == 7
    monkeypatch.undo()
    calls = [0]
    real = g0.fit_model

    def counting(*a, **k):
        calls[0] += 1
        return real(*a, **k)

    monkeypatch.setattr(g0, "fit_model", counting)
    assert _run(edge, tmp_path) == 0
    total = len(list((state / "gate0").glob("gate0B_*_s*.npy")))
    assert calls[0] == total - 7  # the saved splits were not refit
    clean, resumed = _report(edge_run[1]), _report(reports)
    assert clean["tests"] == resumed["tests"] and clean["verdict"] == resumed["verdict"]


def test_resume_under_changed_constants_is_refused(edge, tmp_path, monkeypatch) -> None:
    _copy(edge, tmp_path)
    _interrupt_after(monkeypatch, 3)
    with pytest.raises(KeyboardInterrupt):
        _run(edge, tmp_path)
    monkeypatch.undo()
    from ml_route_v2 import constants

    monkeypatch.setattr(constants, "GATE0_T_MIN", 2.5)
    with pytest.raises(PipelineError, match="other constants"):
        _run(edge, tmp_path)
