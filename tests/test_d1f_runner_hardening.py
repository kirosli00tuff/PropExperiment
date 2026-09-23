"""Stage D.1f list runner: the adversarial review's runner-side fixes
(reports/stage_d1f_adversarial_review.md F5, F6, N5).

- F5: step 5 pins the sha256 of the run-session inputs (the confirmation parquet, the build
  summary, the rolls / condition / symbology files, docs/HOLDOUT2_MANIFEST.json); steps 6, 7
  and 8 recompute them and refuse on any difference, before any screen runs.
- F6: an H member's forced exits are counted from the engine's ledger (every fill whose reason
  is not "strategy", on its trade date as screening.runner._fill_trade_date maps it); the
  instance's own set is recorded beside it and a difference is flagged, never refused. The
  reviewer's Gap A (the exit decided on the session's last bar, 14:58) and Gap B (a position
  open at the end of data) are the known-answer cases.
- N5: every output header records the interpreter and library versions.

SYNTHETIC ONLY (R-7): the H module runs on the synthetic sessions of
tests/test_d1f_h_daily_bar.py, moved onto confirmation dates and written like the builder to a
tmp_path parquet. No research or confirmation bar is read.
"""

from __future__ import annotations

import json
import sys
from dataclasses import replace
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pytest

import strategy.research._d1f_confirmation as conf
import strategy.research._d1f_preflight as pf
from screening.runner import confirmation_window
from sim.engine import BAR_COLUMNS
from strategy.research.h_daily_bar import h1_nr4_breakout as h1
from tests.test_d1f_confirmation_window import _write_like_the_builder
from tests.test_d1f_h_daily_bar import DAYS, PREFIX, Day, up
from tests.test_d1f_h_daily_bar import frame as h_frame

PRE = pf.Preflight(True, (), "a" * 64, {"build": {"record": "synthetic"}, "holdouts": {}})


# ========================================================= F5: run inputs ====
@pytest.fixture
def run_inputs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Path]:
    """Every run input as a tmp file; the step outputs under tmp_path; no bar is loaded."""
    inputs = {name: tmp_path / f"{name}.bin" for name in conf.RUN_INPUTS}
    for i, path in enumerate(inputs.values()):
        path.write_bytes(f"input {i}\n".encode())
    monkeypatch.setattr(conf, "RUN_INPUTS", inputs)
    for attr in ("START_RULE_PATH", "CONTINUITY_PATH", "LIST_RUN_PATH"):
        monkeypatch.setattr(conf, attr, tmp_path / f"{attr.lower()}.json")
    monkeypatch.setattr(conf, "compute_start_rule", lambda: {
        "S": "2021-03-01", "v_ref": 1.0, "sensitivity": [], "empty_window": False})
    return inputs


def test_the_run_inputs_are_the_build_outputs_and_the_holdout2_manifest() -> None:
    assert set(conf.RUN_INPUTS) == {"confirmation_parquet", "build_summary", "rolls",
                                    "condition", "symbology", "holdout2_manifest"}
    shown = {k: v["path"] for k, v in conf.run_input_hashes().items()}
    assert shown["holdout2_manifest"] == "docs/HOLDOUT2_MANIFEST.json"
    assert shown["build_summary"] == "reports/stage_d1f_confirmation_build.json"
    assert shown["rolls"].endswith("rolls/MES_v_0_2019-04-01_2024-03-01.jsonl")


def test_step5_pins_every_run_input_and_later_steps_refuse_a_change(
        run_inputs: dict[str, Path], monkeypatch) -> None:
    assert conf.step5(PRE) == 0
    pinned = json.loads(conf.START_RULE_PATH.read_text())["run_inputs_sha256"]
    assert pinned == conf.run_input_hashes()
    assert {k: v["sha256"] for k, v in pinned.items()} == {
        k: pf.sha256_file(p) for k, p in run_inputs.items()}
    assert conf.read_start(PRE)["step"] == 5

    def never(*_a: object, **_k: object) -> None:
        raise AssertionError("a screen or a load ran after a refused input check")

    for attr in ("run_screens", "_research_frame", "_confirmation_frame", "evaluate"):
        monkeypatch.setattr(conf, attr, never)
    steps = (lambda: conf.step6(PRE, 1), lambda: conf.step7(PRE, 1), lambda: conf.step8(PRE))
    for name, path in run_inputs.items():
        original = path.read_bytes()
        path.write_bytes(original + b"rebuilt between steps\n")
        for step in steps:
            with pytest.raises(conf.StepRefused, match=f"changed since step 5.*run input {name}"):
                step()
        path.unlink()
        for step in steps:
            with pytest.raises(conf.StepRefused, match=f"run input {name}"):
                step()
        path.write_bytes(original)
    assert conf.read_start(PRE)["step"] == 5  # restored: accepted again


def test_step5_refuses_a_missing_input_before_computing_anything(
        run_inputs: dict[str, Path], monkeypatch) -> None:
    run_inputs["symbology"].unlink()
    monkeypatch.setattr(conf, "compute_start_rule", lambda: pytest.fail("S was computed"))
    with pytest.raises(conf.StepRefused, match=r"missing, nothing to pin: \['symbology'\]"):
        conf.step5(PRE)
    assert not conf.START_RULE_PATH.exists()


def test_a_step5_output_without_pinned_inputs_is_refused(run_inputs, tmp_path) -> None:
    conf.write_once(conf.START_RULE_PATH, {"manifest_sha256": PRE.manifest_sha256, "step": 5})
    with pytest.raises(conf.StepRefused, match="pins no run inputs"):
        conf.read_start(PRE)


# ======================================================= N5: environment ====
def test_every_header_records_the_interpreter_and_library_versions(run_inputs) -> None:
    import databento

    header = conf._header(PRE)
    assert header["environment"] == {
        "python": sys.version, "numpy": np.__version__, "pandas": pd.__version__,
        "pyarrow": pa.__version__,
        "scipy": getattr(sys.modules.get("scipy"), "__version__", None),
        "databento": databento.__version__}
    assert header["run_inputs_sha256"] == conf.run_input_hashes()
    assert header["manifest_sha256"] == PRE.manifest_sha256


# ===================================================== F6: forced exits ====
def _weekdays(start: date, n: int) -> tuple[date, ...]:
    days = (start + timedelta(days=i) for i in range(3 * n))
    return tuple(d for d in days if d.weekday() < 5)[:n]


CONF_DAYS = _weekdays(date(2021, 3, 1), len(DAYS))  # confirmation dates, no exchange holiday


def _h1_window(tmp_path: Path, *days: Day):
    """H1 on the test file's NR4 prefix plus ``days``, moved from DAYS onto CONF_DAYS."""
    moved = [replace(d, day=CONF_DAYS[DAYS.index(d.day)]) for d in (*PREFIX, *days)]
    bars = h_frame(moved)[list(BAR_COLUMNS)]
    path = _write_like_the_builder(bars, tmp_path / "h1_synthetic.parquet", [])
    return confirmation_window(CONF_DAYS[0], path=path)


D4 = CONF_DAYS[4].isoformat()
F6_CASES = {
    # Gap A: exit decided on the 14:58 bar, the session's last; the engine force-closes it.
    "gap_a_exit_on_the_last_bar": ((up(4, 44, end="14:58"), Day(DAYS[5])), [D4], []),
    # Gap B: the last date of the data ends at 14:57 with the position open (end_of_data).
    "gap_b_open_at_end_of_data": ((up(4, 44, end="14:57"),), [D4], []),
    # Control: the 14:57 session followed by a later date; both sets agree.
    "control_session_ends_at_1457": ((up(4, 44, end="14:57"), Day(DAYS[5])), [D4], [D4]),
    # A normal strategy exit at 14:59: no forced exit anywhere.
    "strategy_exit": ((up(4, 44), Day(DAYS[5])), [], []),
}


@pytest.mark.parametrize("case", sorted(F6_CASES))
def test_h_forced_exits_are_counted_from_the_ledger(tmp_path: Path, case: str) -> None:
    days, ledger, instance = F6_CASES[case]
    window = _h1_window(tmp_path, *days)
    [result] = conf.run_screens([(h1.LABEL, h1.factory, "H")], window, 1)
    forced = result["forced_exits"]
    assert forced["forced_exit_dates_ledger"] == ledger
    assert forced["forced_exit_dates_instance"] == instance
    assert forced["n_forced_exits"] == len(ledger)  # the ledger's count is the reported one
    assert forced["forced_exit_sets_differ"] is (ledger != instance)
    assert forced["only_in_ledger"] == sorted(set(ledger) - set(instance))
    assert result["report"]["n_trips"] == 1 and "error" not in result


def test_a_forced_exit_difference_is_flagged_not_refused(tmp_path: Path, monkeypatch,
                                                         capsys) -> None:
    window = _h1_window(tmp_path, *F6_CASES["gap_a_exit_on_the_last_bar"][0])
    monkeypatch.setattr(conf, "tier_a_trials", lambda: [(h1.LABEL, h1.factory, "C7")])
    [member], _ = conf.run_trials(window, 1)
    assert member.extra["n_forced_exits"] == 1 and member.extra["forced_exit_sets_differ"]
    assert member.extra["forced_exit_dates_ledger"] == [D4]
    assert f"FLAG {h1.LABEL}: forced exits differ" in capsys.readouterr().out


def test_the_backtest_capture_is_removed_after_every_screen(tmp_path: Path) -> None:
    import screening.runner

    original = screening.runner.run_backtest
    window = _h1_window(tmp_path, *F6_CASES["strategy_exit"][0])
    conf.run_screens([(h1.LABEL, h1.factory, "H")], window, 1)

    def broken() -> object:
        raise RuntimeError("boom")

    with pytest.raises(conf.StepRefused, match="boom"):
        conf.run_screens([("broken", broken, "H")], window, 1)
    assert screening.runner.run_backtest is original
