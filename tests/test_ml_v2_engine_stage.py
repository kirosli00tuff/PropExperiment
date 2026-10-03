"""Stage E.11 FIX 3 (lead ruling 2026-10-03): the engine stages' memory and per-path checkpoints
(ml_route_v2/engine_stage.py; docs/STAGE_E_ML_V2_DESIGN.md V2.11, V12).

On a small synthetic world (two products, about four months, a planted sign edge so the stand-in
schedule trades):
- prepare_engine writes one frame file per traded vehicle, and another world's frames raise;
- the simulate stage writes one checkpoint per path; a run killed in path 1 keeps path 0, and the
  restart recomputes only path 1, with the same figures as an uninterrupted run;
- a checkpoint written for another schedule raises instead of being reused;
- an isolated path (its own spawned process) gives the inline figures and reports its own peak;
- the payouts stage writes one checkpoint per path and a restart recomputes only the missing one.
Synthetic data only.
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from ml_route_v2 import engine_stage
from ml_route_v2.engine_stage import (
    prepare_engine,
    run_engine_paths,
    run_payout_paths,
    traded_roots,
)
from ml_route_v2.pipeline import PipelineError, _filter, build_world_panel
from ml_route_v2.probe import standin_schedule
from tests.ml_v2_fixtures import world

VEHICLES = ("MGC", "6E")
FIRST, LAST = date(2021, 3, 1), date(2021, 6, 30)
SEED = 20261005
PAYOUT_N = 40


def _world(seed: int = SEED):
    return world(VEHICLES, FIRST, LAST, seed=seed,
                 plant={"kind": "sign", "edge_cost_multiple": 10.0})


@pytest.fixture(scope="module")
def small(tmp_path_factory) -> dict:
    w = _world()
    panel = build_world_panel(w)
    filt = _filter(panel)
    sched = standin_schedule(panel, filt["admissible"])
    assert len(sched) > 20
    schedules = {0: sched, 1: sched.iloc[::2].reset_index(drop=True)}
    engine_dir = tmp_path_factory.mktemp("engine")
    engine = prepare_engine(w, schedules, (0, 1), engine_dir)
    ref = run_engine_paths(engine, schedules, filt["risk"], (0, 1), engine_dir / "ref",
                           isolate=False)
    return {"world": w, "risk": filt["risk"], "schedules": schedules, "engine": engine,
            "engine_dir": engine_dir, "ref": ref}


def _counting(monkeypatch: pytest.MonkeyPatch, fail_on: int | None = None) -> list[int]:
    calls: list[int] = []
    original = engine_stage.run_engine_path

    def wrapped(engine, sched, risk):  # noqa: ANN001, ANN202 - test double
        calls.append(len(sched))
        if fail_on is not None and len(calls) == fail_on:
            raise KeyboardInterrupt("simulated kill")
        return original(engine, sched, risk)

    monkeypatch.setattr(engine_stage, "run_engine_path", wrapped)
    return calls


def _same(a: dict, b: dict) -> None:
    pd.testing.assert_series_equal(a["daily"], b["daily"])
    assert a["n_trips"] == b["n_trips"] and a["trips_by_root"] == b["trips_by_root"]


def test_prepare_engine_writes_one_frame_file_per_traded_vehicle(small: dict) -> None:
    files = sorted(p.stem for p in (small["engine_dir"] / "frames").glob("*.pkl"))
    assert files == sorted([*traded_roots(small["schedules"], (0, 1)), "meta"])
    assert set(traded_roots(small["schedules"], (0, 1))) == set(VEHICLES)
    with pytest.raises(PipelineError, match="another world"):
        prepare_engine(_world(SEED + 1), small["schedules"], (0, 1), small["engine_dir"])


def test_killed_run_keeps_finished_paths_and_restart_computes_only_the_rest(
        small: dict, tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    ckpt = tmp_path / "ckpt"
    args = (small["engine"], small["schedules"], small["risk"], (0, 1), ckpt)
    calls = _counting(monkeypatch, fail_on=2)
    with pytest.raises(KeyboardInterrupt):
        run_engine_paths(*args, isolate=False)
    assert (ckpt / "path_0.pkl").exists() and not (ckpt / "path_1.pkl").exists()

    monkeypatch.undo()
    calls = _counting(monkeypatch)
    out = run_engine_paths(*args, isolate=False)
    assert calls == [len(small["schedules"][1])]  # path 0 loaded, path 1 computed
    for j in (0, 1):
        _same(out[j], small["ref"][j])

    calls.clear()
    again = run_engine_paths(*args, isolate=False)
    assert calls == []  # every path loaded
    _same(again[1], out[1])


def test_checkpoint_of_another_schedule_raises(small: dict, tmp_path) -> None:
    ckpt = tmp_path / "ckpt"
    sch = small["schedules"]
    run_engine_paths(small["engine"], sch, small["risk"], (1,), ckpt, isolate=False)
    other = {1: sch[1].iloc[1:].reset_index(drop=True)}
    with pytest.raises(PipelineError, match="fingerprint"):
        run_engine_paths(small["engine"], other, small["risk"], (1,), ckpt, isolate=False)


def test_isolated_path_gives_the_inline_figures(small: dict, tmp_path) -> None:
    out = run_engine_paths(small["engine"], small["schedules"], small["risk"], (1,),
                           tmp_path / "iso", isolate=True)
    _same(out[1], small["ref"][1])
    assert out[1]["engine_peak_rss_mb"] > 0


def test_payouts_checkpoint_per_path_and_restart(small: dict, tmp_path,
                                                 monkeypatch: pytest.MonkeyPatch) -> None:
    ckpt = tmp_path / "pay"
    first = run_payout_paths(small["ref"], PAYOUT_N, ckpt)
    assert sorted(p.name for p in ckpt.glob("*.pkl")) == ["path_0.pkl", "path_1.pkl"]
    (ckpt / "path_1.pkl").unlink()
    calls: list[int] = []
    original = engine_stage._payout_rows

    def wrapped(j, days, n):  # noqa: ANN001, ANN202 - test double
        calls.append(j)
        return original(j, days, n)

    monkeypatch.setattr(engine_stage, "_payout_rows", wrapped)
    second = run_payout_paths(small["ref"], PAYOUT_N, ckpt)
    assert calls == [1]
    pd.testing.assert_frame_equal(first, second)


def test_engine_inputs_carry_each_vehicles_own_roll_blackout(small: dict) -> None:
    """Design fix 8 (V2.2): the engine refuses an entry in P only on P's own roll dates; the
    inputs carry every vehicle's own set (pipeline.own_blackout) beside the D4 union."""
    from ml_route_v2.pipeline import own_blackout

    w, engine = small["world"], small["engine"]
    want = own_blackout(w.blackout, VEHICLES)
    assert engine.product_blackout == {r: frozenset(d) for r, d in want.items()}
    assert set(engine.product_blackout) == set(VEHICLES)
    assert set().union(*engine.product_blackout.values()) <= engine.blackout


def test_isolation_is_the_pipeline_default() -> None:
    """Design fix 9: one process per engine path is the default; tests run inline."""
    import inspect

    from ml_route_v2 import pipeline

    assert pipeline.ISOLATE_ENGINE_PATHS is True
    default = inspect.signature(pipeline.run_pipeline).parameters["isolate_paths"].default
    assert default is True


def test_an_empty_schedule_path_keeps_flagged_payout_rows(small: dict, tmp_path) -> None:
    """Code review C-03: a path whose schedule was empty (no day records) still has its rows in
    the payouts table, one per (account, path type, DLL, ks), n_trips 0, the figures NaN and
    empty_schedule True; a traded path's rows carry its n_trips and empty_schedule False."""
    sim = {0: small["ref"][0], 1: engine_stage._empty_path()}
    pay = run_payout_paths(sim, PAYOUT_N, tmp_path / "pay")
    empty, full = pay[pay["path"] == 1], pay[pay["path"] == 0]
    assert len(empty) == len(full) == 16 and list(pay.columns)[-2:] == ["n_trips",
                                                                       "empty_schedule"]
    assert empty["empty_schedule"].all() and (empty["n_trips"] == 0).all()
    assert not full["empty_schedule"].any()
    assert (full["n_trips"] == small["ref"][0]["n_trips"]).all()
    for col in ("monthly_net_mean", "ruin_prob", "breach_only_prob", "p_any_payout"):
        assert empty[col].isna().all() and full[col].notna().all()
    keys = ["account", "path_type", "dll", "ks", "ks2_sizing", "verdict_reading"]
    pd.testing.assert_frame_equal(empty[keys].reset_index(drop=True),
                                  full[keys].reset_index(drop=True))
    assert not (tmp_path / "pay" / "path_1.pkl").exists()  # nothing to checkpoint


def test_engine_path_summaries_are_labelled_kill_switches_off(small: dict) -> None:
    """Code review C-11 (label): the engine record and its combined-MLL audit are the kill
    switches off record."""
    assert engine_stage.ENGINE_KILL_SWITCHES == "off"
    assert all(res["kill_switches"] == "off" for res in small["ref"].values())
    assert engine_stage._empty_path()["kill_switches"] == "off"
