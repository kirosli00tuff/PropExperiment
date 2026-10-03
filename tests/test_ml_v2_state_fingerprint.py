"""Stage E.11 code review C-01 (lead ruling 2026-10-03): every piece of ML route v2's resumable
state pins the constants fingerprint (ml_route_v2/fingerprint.py), so state written under one set
of constants is refused under another. Each test writes state under the default
COST_GATE_READING ("net"), flips it to "gross" with monkeypatch (the freeze session's one-line
switch, design D-05) and expects the mismatch error: the CPCV unit store, Gate 0 family B's
state, a pipeline stage file, an engine-path checkpoint and a payout checkpoint. Also: a
functools.partial's bound arguments join the callable's name in the CPCV fingerprint. Synthetic
data only.
"""

from __future__ import annotations

import functools

import numpy as np
import pandas as pd
import pytest

import ml_route_v2.constants as v2c
from ml_route_v2 import engine_stage, pipeline
from ml_route_v2.configs import ConfigLedger
from ml_route_v2.cpcv import StateMismatchError, _callable_name, calendar_blocks, nested_cpcv
from ml_route_v2.engine_stage import EngineInputs, run_engine_paths, run_payout_paths
from ml_route_v2.fingerprint import constants_fingerprint
from ml_route_v2.gate0 import _b_state
from ml_route_v2.pipeline import PipelineError, _save
from tests.test_ml_v2_cpcv import RIDGE_H60, make_panel, stub_score


def _flip(monkeypatch: pytest.MonkeyPatch) -> None:
    assert v2c.COST_GATE_READING == "net"
    monkeypatch.setattr(v2c, "COST_GATE_READING", "gross")


def _boom(*_a, **_k):  # noqa: ANN202 - a computation that must not run
    raise AssertionError("state was recomputed instead of refused")


def test_the_fingerprint_follows_a_constant_changed_at_run_time(
        monkeypatch: pytest.MonkeyPatch) -> None:
    before = constants_fingerprint()
    assert constants_fingerprint() == before  # deterministic
    _flip(monkeypatch)
    flipped = constants_fingerprint()
    assert flipped != before
    monkeypatch.setattr(v2c, "PAYOUT_RESET_DELAY_DATES", 5)  # a V2.9 freeze-session item
    assert constants_fingerprint() not in (before, flipped)
    monkeypatch.undo()
    assert constants_fingerprint() == before


def test_cpcv_state_written_under_net_is_refused_under_gross(
        tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    panel = make_panel(n_dates=60, seed=3)
    ledger = ConfigLedger(tmp_path / "l.jsonl")
    nested_cpcv(panel, RIDGE_H60[:2], stub_score, ledger=ledger, state_dir=tmp_path / "s")
    nested_cpcv(panel, RIDGE_H60[:2], stub_score, ledger=ledger,
                state_dir=tmp_path / "s")  # the same constants: resumes
    _flip(monkeypatch)
    with pytest.raises(StateMismatchError):
        nested_cpcv(panel, RIDGE_H60[:2], stub_score, ledger=ledger, state_dir=tmp_path / "s")


def test_gate0_b_state_written_under_net_is_refused_under_gross(
        tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    panel = make_panel(n_dates=60, seed=4)
    days = np.unique(panel.frame["trade_date"].to_numpy().astype("datetime64[D]")).tolist()
    blocks = calendar_blocks(days)
    _b_state(panel, tmp_path / "g", blocks, None)
    _b_state(panel, tmp_path / "g", blocks, None)  # the same constants: accepted
    _flip(monkeypatch)
    with pytest.raises(StateMismatchError):
        _b_state(panel, tmp_path / "g", blocks, None)


def test_stage_file_written_under_net_is_refused_under_gross(
        tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    first = pipeline._Stages(tmp_path, timing=False)
    assert first.run("filter", lambda: {"x": 1}) == {"x": 1}
    again = pipeline._Stages(tmp_path, timing=False)
    assert again.run("filter", _boom) == {"x": 1}
    assert again.records[-1].status == "loaded"
    _flip(monkeypatch)
    with pytest.raises(PipelineError, match="other constants"):
        pipeline._Stages(tmp_path, timing=False).run("filter", _boom)


def test_a_stage_file_without_the_constants_is_refused(tmp_path) -> None:
    _save(tmp_path / "stages" / "panel.pkl", {"x": 1})  # the format before C-01
    with pytest.raises(PipelineError, match="not a stage file"):
        pipeline._Stages(tmp_path, timing=False).run("panel", _boom)


def _engine_inputs(tmp_path) -> EngineInputs:
    return EngineInputs(tmp_path / "frames", None, frozenset(), frozenset(), "world")


def _schedule() -> pd.DataFrame:
    return pd.DataFrame({"root": ["MNQ"], "horizon": ["h60"], "decision_ts_ns": [1]})


def test_engine_path_checkpoint_written_under_net_is_refused_under_gross(
        tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    engine, sched = _engine_inputs(tmp_path), _schedule()
    risk = pd.DataFrame({"root": ["MNQ"], "horizon": ["h60"], "sigma_ticks": [1.0],
                         "loss_ticks": [1.0]})
    ckpt = tmp_path / "ckpt"
    fp = engine_stage._path_fingerprint(engine, sched, risk)
    _save(ckpt / "path_0.pkl", {"fingerprint": fp, "out": {"n_trips": 7}})
    monkeypatch.setattr(engine_stage, "run_engine_path", _boom)
    out = run_engine_paths(engine, {0: sched}, risk, (0,), ckpt, isolate=False)
    assert out[0] == {"n_trips": 7}  # the same constants: the checkpoint is read back
    _flip(monkeypatch)
    assert engine_stage._path_fingerprint(engine, sched, risk) != fp
    with pytest.raises(PipelineError, match="fingerprint"):
        run_engine_paths(engine, {0: sched}, risk, (0,), ckpt, isolate=False)


def test_payout_checkpoint_written_under_net_is_refused_under_gross(
        tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[int] = []

    def rows(j, days, n):  # noqa: ANN001, ANN202 - a stand-in for the payout draw
        calls.append(j)
        return [{"path": j, "ruin_prob": 0.0}]

    monkeypatch.setattr(engine_stage, "_payout_rows", rows)
    sim = {0: {"days": ("2021-03-01",), "n_trips": 1}}
    first = run_payout_paths(sim, 10, tmp_path / "pay")
    second = run_payout_paths(sim, 10, tmp_path / "pay")
    assert calls == [0]  # the same constants: the checkpoint is read back
    pd.testing.assert_frame_equal(first, second)
    _flip(monkeypatch)
    with pytest.raises(PipelineError, match="fingerprint"):
        run_payout_paths(sim, 10, tmp_path / "pay")


def _score(rows, r_hat, config, *, risk=None):  # noqa: ANN001, ANN202 - a named callable
    return None


def test_partial_bound_arguments_join_the_callable_name() -> None:
    a = pd.DataFrame({"root": ["MNQ"], "sigma_ticks": [1.0]})
    b = a.assign(sigma_ticks=[2.0])
    assert _callable_name(_score).endswith("._score")
    name_a = _callable_name(functools.partial(_score, risk=a))
    assert name_a == _callable_name(functools.partial(_score, risk=a.copy()))
    assert name_a != _callable_name(functools.partial(_score, risk=b))
    assert name_a.startswith(_callable_name(_score))
    roots = _callable_name(functools.partial(_score, roots=("MGC", "MNQ")))
    assert roots != _callable_name(functools.partial(_score, roots=("MNQ",)))
