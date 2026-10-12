"""The run discipline (reports/stage_e20_plan.md sections 7 and 11): the registry check refuses
before the registration, with another freeze sha256 and with another N; the freeze manifest's
build and verification; the resumable pinned stages; the test-mode run and report end to end; the
CLI refusal. Temporary registries and state only (no ledger write)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from pattern_search import constants as K
from pattern_search import preflight as pf
from pattern_search.run import run_search
from tests._pattern_search_synth import (
    configs_named,
    freeze_file,
    make_hooks,
    run_paths,
    temp_registry,
    world_small,
)

SMALL = ("ridge_l0.1_k1.5_h60", "ridge_l1_k1.5_hF")


def _frozen(tmp: Path) -> tuple[Path, str, Path]:
    f = tmp / "input.txt"
    f.write_text("an input\n")
    path, sha = freeze_file(tmp, [f])
    return path, sha, f


def test_the_registry_check_refuses_before_the_registration(tmp_path) -> None:
    path, sha, _f = _frozen(tmp_path)
    reg = temp_registry(tmp_path, path, sha, with_search=False)
    with pytest.raises(pf.Refused, match="not registered"):
        pf.check_registered(sha, reg)


def test_the_registry_check_refuses_another_freeze_sha256(tmp_path) -> None:
    path, sha, _f = _frozen(tmp_path)
    reg = temp_registry(tmp_path, path, sha)
    assert pf.check_registered(sha, reg)["n_after"] == 528
    with pytest.raises(pf.Refused, match="freeze sha256"):
        pf.check_registered("1" * 64, reg)


def test_the_registry_check_refuses_another_n(tmp_path) -> None:
    from screening.trial_registry import init_registry, register

    path, sha, _f = _frozen(tmp_path)
    reg = tmp_path / "reg_n.jsonl"
    init_registry(reg)
    register(K.REGISTRY_LABEL, list(K.CONFIG_IDS), path, sha, "0" * 64, path=reg)  # 471 -> 516
    with pytest.raises(pf.Refused, match="483 -> 528"):
        pf.check_registered(sha, reg)


def test_the_registry_check_refuses_ids_registered_under_another_label(tmp_path) -> None:
    path, sha, _f = _frozen(tmp_path)
    reg = temp_registry(tmp_path, path, sha, with_search=False)
    from screening.trial_registry import register

    register("E20X", [f"E20X-{i}" for i in range(1, 46)], path, sha, "0" * 64, path=reg)
    with pytest.raises(pf.Refused):
        pf.check_registered(sha, reg)


def test_only_the_test_mode_may_name_another_registry(tmp_path) -> None:
    reg = tmp_path / "r.jsonl"
    reg.write_text("")
    with pytest.raises(pf.Refused, match="test mode"):
        pf.check_registry_path(reg, test_mode=False)
    assert pf.check_registry_path(reg, test_mode=True) == reg


# ------------------------------------------------------------------ the freeze manifest ----
def test_the_freeze_manifest_is_written_once_and_verified(tmp_path) -> None:
    from pattern_search.freeze_manifest import body, write_once

    a, b = tmp_path / "a.txt", tmp_path / "b.txt"
    a.write_text("A")
    b.write_text("B")
    path = tmp_path / "freeze.json"
    sha = write_once(path, body([a, b]))
    doc = json.loads(path.read_text())
    assert doc["schema"] == K.FREEZE_SCHEMA and len(doc["files"]) == 2
    with pytest.raises(pf.Refused, match="written once"):
        write_once(path, body([a]))
    assert pf.check_freeze(path, sha, [a, b])["files"] == 2
    with pytest.raises(pf.Refused, match="sha256"):
        pf.check_freeze(path, "2" * 64, [a])
    c = tmp_path / "c.txt"
    c.write_text("C")
    with pytest.raises(pf.Refused, match="not in the search freeze manifest"):
        pf.check_freeze(path, sha, [a, c])
    b.write_text("changed")
    with pytest.raises(pf.Refused, match="missing or changed"):
        pf.check_freeze(path, sha, [a])


def test_the_required_files_cover_plan_code_tests_inputs_and_v2_modules() -> None:
    from pattern_search.freeze_manifest import required_files

    got = {pf.rel(p) for p in required_files(with_stores=False)}
    assert K.PLAN_REL in got
    assert {"pattern_search/guard.py", "pattern_search/backward.py",
            "pattern_search/dry_check.py", "pattern_search/run.py"} <= got
    assert "tests/test_pattern_search_run.py" in got and "tests/_pattern_search_synth.py" in got
    assert {K.S_X_SOURCE_REL, K.STORE_MANIFEST_REL, K.RELEASE_CALENDAR_REL, K.V2_FREEZE_REL,
            "reports/step2/bars_NQ.json", "data/calendars/grains.py"} <= got
    assert {"ml_route_v2/cpcv.py", "ml_route_v2/panel.py", "ml_route_v2/clock.py"} <= got
    assert not any(p.startswith("data/processed") for p in got)


def test_the_harness_sha256_must_be_v12() -> None:
    with pytest.raises(pf.Refused, match="v12"):
        pf.check_harness("3" * 64, lambda s: s)
    assert pf.check_harness(K.HARNESS_SHA256, lambda s: s) == K.HARNESS_SHA256


# ------------------------------------------------------------------ stages ----
def test_a_stage_written_under_another_pin_is_refused(tmp_path) -> None:
    from pattern_search.stages import Stages, StateMismatch

    st = Stages(tmp_path, {"freeze_sha256": "a"})
    assert st.run("x", lambda: 41) == 41
    assert Stages(tmp_path, {"freeze_sha256": "a"}).run("x", lambda: 0) == 41  # loaded
    with pytest.raises(StateMismatch, match="another pin"):
        Stages(tmp_path, {"freeze_sha256": "b"}).run("x", lambda: 0)


# ------------------------------------------------------------------ end to end ----
def test_run_and_report_end_to_end_in_test_mode(tmp_path) -> None:
    path, sha, f = _frozen(tmp_path)
    reg = temp_registry(tmp_path, path, sha)
    paths = run_paths(tmp_path, path, reg)
    hooks = make_hooks(lambda p: world_small(), configs=configs_named(*SMALL), required=[f])
    doc = run_search(sha, K.HARNESS_SHA256, paths, hooks, test_mode=True)
    assert doc["screen"]["verdict"] in (K.PASS, K.FAIL)
    assert doc["registry_entry"]["n_after"] == 528
    assert [s["name"] for s in doc["stages"]] == ["panel", "filter", "cpcv", "final", "oos"]
    assert all(s["status"] == "computed" for s in doc["stages"])
    assert paths.result_json.is_file() and paths.result_md.is_file()
    assert (paths.reports_dir / "configs.csv").is_file()
    out = json.loads(paths.result_json.read_text())
    assert out["schema"] == K.RESULT_SCHEMA and out["reported"]["dsr"]["n_trials"] == 528
    again = run_search(sha, K.HARNESS_SHA256, paths, hooks, test_mode=True, compute=False)
    assert all(s["status"] == "loaded" for s in again["stages"])
    assert again["screen"]["verdict"] == doc["screen"]["verdict"]
    assert again["screen"]["items"]["1_median_path_t"]["value"] == \
        doc["screen"]["items"]["1_median_path_t"]["value"]


def test_report_refuses_when_the_stages_were_never_computed(tmp_path) -> None:
    path, sha, f = _frozen(tmp_path)
    reg = temp_registry(tmp_path, path, sha)
    paths = run_paths(tmp_path, path, reg)
    hooks = make_hooks(lambda p: world_small(), configs=configs_named(*SMALL), required=[f])
    with pytest.raises(pf.Refused, match="has not been computed"):
        run_search(sha, K.HARNESS_SHA256, paths, hooks, test_mode=True, compute=False)


def test_run_refuses_before_any_stage_without_the_registration(tmp_path) -> None:
    path, sha, f = _frozen(tmp_path)
    reg = temp_registry(tmp_path, path, sha, with_search=False)
    paths = run_paths(tmp_path, path, reg)

    def world(p):  # noqa: ANN001, ANN202
        raise AssertionError("the world was built before the registry check")

    hooks = make_hooks(world, configs=configs_named(*SMALL), required=[f])
    with pytest.raises(pf.Refused, match="not registered"):
        run_search(sha, K.HARNESS_SHA256, paths, hooks, test_mode=True)
    assert not (paths.state_dir / "stages").exists()


def test_an_empty_admissible_set_ends_the_run_with_a_failed_screen(tmp_path, monkeypatch) -> None:
    import ml_route_v2.pipeline as pipeline

    real = pipeline._filter

    def no_pairs(panel):  # noqa: ANN001, ANN202
        out = real(panel)
        return {**out, "admissible": ()}

    monkeypatch.setattr(pipeline, "_filter", no_pairs)
    path, sha, f = _frozen(tmp_path)
    reg = temp_registry(tmp_path, path, sha)
    paths = run_paths(tmp_path, path, reg)
    hooks = make_hooks(lambda p: world_small(), configs=configs_named(*SMALL), required=[f])
    doc = run_search(sha, K.HARNESS_SHA256, paths, hooks, test_mode=True)
    assert doc["screen"]["verdict"] == K.FAIL and "no model" in doc["screen"]["reason"]
    assert [s["name"] for s in doc["stages"]] == ["panel", "filter"]
    assert "not computed" in doc["reported"]["ruin"]["status"]


def test_the_cli_refuses_a_wrong_harness_sha256() -> None:
    from data.config import REPO_ROOT

    proc = subprocess.run([sys.executable, "-m", "pattern_search", "check", "--freeze-sha256",
                           "0" * 64, "--harness-sha256", "4" * 64], cwd=REPO_ROOT,
                          capture_output=True, text=True, timeout=300, check=False)
    assert proc.returncode == K.RC_REFUSED, proc.stderr[-1500:]
    assert "REFUSED" in proc.stderr and "v12" in proc.stderr
