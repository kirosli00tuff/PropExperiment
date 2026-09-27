"""Harness bug C-1 (Stage E.3 return, section 7; Stage E.4 H1): launched as a real
``python -m screening.stage_e_runner`` process, the runner records a start-date refusal raised
through screening.stage_e_start_dates' ``_runner()`` by name (power not_run) and exits 0, exactly
as when ``main()`` is called on the imported module. Every raise of the start-date loader that a
research run can meet is one member of a synthetic cluster (tests/_stage_e_launch.py), so one
``--all`` run per launch shows each caught by name; the confirmation window's refusals, which the
runner lets propagate by design, propagate by name under both launches. The engine is always
called from the module ``screening.stage_e_runner``: ``python -m`` and an import run one module
object. Nothing is written outside tmp_path."""

from __future__ import annotations

import json
import subprocess

import pytest

from tests import _stage_e_launch as launch_kit

PYTHON_M, IMPORTED = "python -m", "import"


def _tail(proc: subprocess.CompletedProcess, lines: int = 12) -> str:
    return "\n".join((proc.stdout + proc.stderr).splitlines()[-lines:])


def _written(cfg: dict) -> list[str]:
    from pathlib import Path

    return sorted(p.name for p in Path(cfg["out_dir"]).iterdir())


def _expected_files(cases: tuple[launch_kit.Case, ...], cluster_record: bool) -> list[str]:
    names = []
    for i, case in enumerate(cases, start=1):
        stem = launch_kit.record_path({"out_dir": "."}, i, case).stem
        names += [f"{stem}.json", f"{stem}_trips.json"]
    return sorted(names + (["K1_research_cluster.json"] if cluster_record else []))


def test_c1_a_start_date_refusal_under_python_m_is_recorded_by_name_and_exits_0(
        tmp_path, monkeypatch) -> None:
    """E.3's attempt 1: the power check finds no start-rule file; stage_e_start_dates raises
    StartRuleMissing through _runner(). The member is recorded (power not_run, the class named)
    and the process exits 0. A second launch into the same directory is refused by the runner's
    own write-once refusal, whose class is the imported module's too."""
    case = launch_kit.start_cases()[0]
    assert case.case_id == "missing"
    cfg = launch_kit.build_world(tmp_path, monkeypatch, (case,))
    who = ("--member", launch_kit.label(1, case))
    proc = launch_kit.launch(cfg, *launch_kit.argv(cfg, *who))
    assert proc.returncode == 0, _tail(proc)
    assert (tmp_path / "installed.txt").is_file()  # the child's synthetic world was in place
    assert proc.stdout.strip() == f"K1 {launch_kit.label(1, case)} research: run []"
    rec = launch_kit.check_member(cfg, 1, case)
    assert rec["power"]["reason"].startswith("StartRuleMissing: no frozen S_X for ['ZN']")
    assert launch_kit.callers(cfg) == ["screening.stage_e_runner"]
    assert _written(cfg) == _expected_files((case,), cluster_record=False)

    again = launch_kit.launch(cfg, *launch_kit.argv(cfg, *who))
    assert again.returncode == 1
    assert "screening.stage_e_runner.RunnerRefusal: " in again.stderr, _tail(again)
    assert "already exists; records are written once" in again.stderr
    assert _written(cfg) == _expected_files((case,), cluster_record=False)


@pytest.mark.parametrize("how", [PYTHON_M, IMPORTED])
def test_c1_every_start_date_refusal_is_caught_by_name_under_both_launches(
        tmp_path, monkeypatch, capsys, how) -> None:
    cases = launch_kit.all_cases()
    cfg = launch_kit.build_world(tmp_path, monkeypatch, cases)
    if how == PYTHON_M:
        proc = launch_kit.launch(cfg, *launch_kit.argv(cfg))
        assert proc.returncode == 0, _tail(proc)
        stdout = proc.stdout
    else:
        launch_kit.install_in_process(cfg, monkeypatch)
        import screening.stage_e_runner as runner

        assert runner.main(launch_kit.argv(cfg)) == 0
        stdout = capsys.readouterr().out
    engine = [c for c in cases if c.kind == "engine"]
    assert stdout.splitlines()[0] == f"K1 research: {len(cases)} members, {len(engine)} refused"
    for i, case in enumerate(cases, start=1):
        launch_kit.check_member(cfg, i, case)
    assert launch_kit.callers(cfg) == ["screening.stage_e_runner"] * len(cases)
    assert _written(cfg) == _expected_files(cases, cluster_record=True)
    summary = json.loads((tmp_path / "out" / "K1_research_cluster.json").read_text(
        encoding="utf-8"))
    assert sorted(summary["refused_members"]) == sorted(
        launch_kit.label(i, c) for i, c in enumerate(cases, start=1) if c.kind == "engine")


@pytest.mark.parametrize("how", [PYTHON_M, IMPORTED])
@pytest.mark.parametrize("case_id, cls, fragment", [
    ("missing", "StartRuleMissing", "no frozen S_X for ['ZN']"),
    ("empty_window", "StartWindowEmpty", "['ZN']: the start rule found no qualifying month"),
])
def test_c1_a_confirmation_run_without_s_x_is_refused_by_name_under_both_launches(
        tmp_path, monkeypatch, how, case_id, cls, fragment) -> None:
    """The confirmation window needs S_X (screening.stage_e_start_dates.start_dates_for without
    allow_empty); its refusal propagates by design, names its class and writes nothing."""
    from tests.test_stage_e_start_dates import consistent_entry

    files = () if case_id == "missing" else (
        ("stage_e_start_rule_K2.json", launch_kit._doc("K2", {"ZN": consistent_entry(None)})),)
    case = launch_kit.Case(case_id, "start", cls, fragment, "start_dates_for", files)
    cfg = launch_kit.build_world(tmp_path, monkeypatch, (case,))
    args = [a if a != "research" else "confirmation" for a in launch_kit.argv(cfg)]
    if how == PYTHON_M:
        proc = launch_kit.launch(cfg, *args)
        assert proc.returncode == 1, _tail(proc)
        assert f"screening.stage_e_runner.{cls}: " in proc.stderr and fragment in proc.stderr, (
            _tail(proc))
    else:
        launch_kit.install_in_process(cfg, monkeypatch)
        import screening.stage_e_runner as runner

        with pytest.raises(getattr(runner, cls)) as caught:
            runner.main(args)
        assert type(caught.value) is getattr(runner, cls) and fragment in str(caught.value)
    assert not (tmp_path / "out").exists() and launch_kit.callers(cfg) == []
