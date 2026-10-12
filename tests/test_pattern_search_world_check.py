"""``check --world`` (review SC-1, lead ruling) on synthetic fixture stores: all 17 step 2 stores
written in the real formats by the frozen phase-1 fixture writers (tests/test_ml_v2_phase1_support:
write_step2, synthetic_bars) under a temporary directory, with E.12-style S_X records and an
E.17-style manifest. check --world loads them through world.real_world (the frozen loader's
sha256, booking, holdout, embargo, store-range and roll checks, refuse_late, the guard's bar
check, the training calendar) and pipeline.assert_bars_on_session_grid, and writes the summary;
it builds no row, feature or panel, writes nothing to the state directory and needs no
registration. No real store is opened."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from pattern_search import constants as K
from pattern_search import guard
from pattern_search.run import WORLD_CHECK_FILE, check
from tests._pattern_search_synth import freeze_file, make_hooks, run_paths

FIRST, LAST = date(2023, 1, 3), date(2023, 3, 31)


@pytest.fixture(scope="module")
def stores(tmp_path_factory):  # noqa: ANN201
    """Fixture step 2 stores and summaries for the 17 roots; (base, records)."""
    from tests.test_ml_v2_phase1_support import synthetic_bars, write_step2

    base = tmp_path_factory.mktemp("fixture_stores")
    step2, summaries = base / "step2", base / "summaries"
    recs = {}
    for root in K.PATH_ROOTS:
        frame = synthetic_bars(root, FIRST, LAST, plant=None)
        if root == "NQ":
            frame = _with_closure_bars(frame)
        recs[root] = write_step2(root, frame, step2, summaries)
    return base, recs


CLOSURE_DAY, NEXT_DAY = date(2023, 2, 14), date(2023, 2, 15)


def _with_closure_bars(frame):  # noqa: ANN001, ANN202
    """NQ plus two bars outside the open intervals, labelled as the frozen L-3 booking books
    them: a close-minute print at the session's end (its own trade date) and a bar 30 minutes
    into the daily break (the next trade date). The frozen loader accepts both; the synthetic
    session-grid assertion would refuse them."""
    import numpy as np
    import pandas as pd

    from data.group_session import load_group_calendar, session_intervals

    end = max(hi for _lo, hi in session_intervals(load_group_calendar("equity"), CLOSURE_DAY))
    last = frame.loc[frame["trade_date"].astype(str) == CLOSURE_DAY.isoformat()].iloc[[-1]]
    extra = pd.concat([last, last], ignore_index=True)
    extra["ts_event"] = np.asarray([end, end + 30 * 60_000_000_000], dtype=np.int64)
    extra["trade_date"] = [CLOSURE_DAY.isoformat(), NEXT_DAY.isoformat()]
    out = pd.concat([frame, extra], ignore_index=True)
    return out.sort_values("ts_event", kind="mergesort").reset_index(drop=True)


def _records(base: Path, recs: dict[str, str], *, tamper: str | None = None) -> tuple[Path, Path]:
    sha = {r: ("f" * 64 if r == tamper else s) for r, s in recs.items()}
    s_x = {"roots": {r: {"s_x": FIRST.isoformat(), "store_sha256": sha[r],
                         "store_path": str(guard.step2_store_path(r, base / "step2"))}
                     for r in K.PATH_ROOTS}}
    man = {"schema": "fixture", "stores": {r: {"step2": {"path": "fixture", "sha256": sha[r]}}
                                           for r in K.PATH_ROOTS}}
    tag = tamper or "ok"
    (base / f"s_x_{tag}.json").write_text(json.dumps(s_x))
    (base / f"manifest_{tag}.json").write_text(json.dumps(man))
    return base / f"s_x_{tag}.json", base / f"manifest_{tag}.json"


def _world_fn(base: Path, recs: dict[str, str], tamper: str | None = None):  # noqa: ANN202
    from pattern_search.world import real_world

    s_x, man = _records(base, recs, tamper=tamper)
    fixture = {str(Path(guard.step2_store_path(r, base / "step2")).resolve())
               for r in K.PATH_ROOTS}

    def build(paths):  # noqa: ANN001, ANN202
        return real_world(step2_root=base / "step2", summaries_root=base / "summaries",
                          s_x_path=s_x, manifest_path=man, test_stores=fixture,
                          test_expected_s_x={r: FIRST for r in K.PATH_ROOTS})

    return build


def _no_panel(monkeypatch) -> None:  # noqa: ANN001
    import ml_route_v2.panel  # noqa: F401  (imported before the patches: no name binds to boom)
    import pattern_search.panel  # noqa: F401

    def boom(*a, **k):  # noqa: ANN002, ANN003, ANN202
        raise AssertionError("check --world touched rows, features or the panel")

    monkeypatch.setattr("pattern_search.panel.build_search_panel", boom)
    monkeypatch.setattr("pattern_search.rows.search_rows", boom)
    monkeypatch.setattr("ml_route_v2.clock.decision_rows", boom)
    monkeypatch.setattr("ml_route_v2.signals.compute_signals", boom)
    monkeypatch.setattr("ml_route_v2.panel.build_panel", boom)


def test_check_world_loads_and_summarizes_every_root_without_a_panel(stores, tmp_path,
                                                                     monkeypatch) -> None:
    base, recs = stores
    _no_panel(monkeypatch)
    f = tmp_path / "input.txt"
    f.write_text("x")
    freeze, sha = freeze_file(tmp_path, [f])
    paths = run_paths(tmp_path, freeze, tmp_path / "no_registry.jsonl")  # never read
    hooks = make_hooks(_world_fn(base, recs), required=[f], pin="fixture-stores")
    rec = check(sha, K.HARNESS_SHA256, paths, hooks, world=True)
    roots = rec["world"]["roots"]
    assert sorted(roots) == sorted(K.PATH_ROOTS)
    for root, r in roots.items():
        assert r["bars"] > 1000, root
        assert r["first_trade_date"] == FIRST.isoformat() and r["s_x"] == FIRST.isoformat()
        assert r["last_trade_date"] == LAST.isoformat()
        assert r["splice_trade_dates_in_window"] >= 1  # the March roll
        assert r["store_sha256"] == recs[root]
    assert roots["NQ"]["closure_counts"] == {"outside_open_intervals": 2, "close_minute": 1,
                                             "bars_in_scheduled_closure": 0}
    for root in K.PATH_ROOTS:
        if root != "NQ":
            assert roots[root]["closure_counts"]["outside_open_intervals"] == 0, root
    assert rec["world"]["session_grid_assertion"].startswith("not applied")
    assert rec["world"]["calendar"]["first"] == K.SEARCH_FIRST.isoformat()
    assert rec["world"]["calendar"]["last"] == K.SEARCH_LAST.isoformat()
    out = json.loads((paths.reports_dir / WORLD_CHECK_FILE).read_text())
    assert out["schema"] == "stage_e20_search_world_check/1" and len(out["roots"]) == 17
    assert not paths.state_dir.exists()  # nothing in the state directory
    assert not paths.registry.exists()  # no registration needed or read


def test_check_without_world_builds_no_world(stores, tmp_path) -> None:
    f = tmp_path / "input.txt"
    f.write_text("x")
    freeze, sha = freeze_file(tmp_path, [f])
    paths = run_paths(tmp_path, freeze, tmp_path / "r.jsonl")

    def never(p):  # noqa: ANN001, ANN202
        raise AssertionError("check built the world without --world")

    rec = check(sha, K.HARNESS_SHA256, paths, make_hooks(never, required=[f]))
    assert "world" not in rec and not (paths.reports_dir / WORLD_CHECK_FILE).exists()


def test_check_world_refuses_a_store_whose_sha256_differs(stores, tmp_path) -> None:
    from data.stage_e_bars import ParquetHashMismatch

    base, recs = stores
    f = tmp_path / "input.txt"
    f.write_text("x")
    freeze, sha = freeze_file(tmp_path, [f])
    paths = run_paths(tmp_path, freeze, tmp_path / "r.jsonl")
    hooks = make_hooks(_world_fn(base, recs, tamper="ZC"), required=[f])
    with pytest.raises(ParquetHashMismatch):
        check(sha, K.HARNESS_SHA256, paths, hooks, world=True)
    assert not (paths.reports_dir / WORLD_CHECK_FILE).exists()


def test_fixture_stores_under_a_store_root_are_refused(tmp_path) -> None:
    from data.config import HIST_ROOT
    from pattern_search.world import load_search_root

    rec = {"s_x": FIRST, "store_sha256": "0" * 64}
    bad = {str(Path(HIST_ROOT) / "ext2010" / "NQ" / "x.parquet")}
    with pytest.raises(guard.GuardRefusal, match="test stores under a store root"):
        load_search_root("NQ", rec, step2_root=tmp_path, summaries_root=tmp_path, repo=tmp_path,
                         test_stores=bad)


def test_the_cli_takes_world_only_with_check() -> None:
    import subprocess
    import sys

    from data.config import REPO_ROOT

    proc = subprocess.run([sys.executable, "-m", "pattern_search", "run", "--world",
                           "--freeze-sha256", "0" * 64, "--harness-sha256", "0" * 64],
                          cwd=REPO_ROOT, capture_output=True, text=True, timeout=300, check=False)
    assert proc.returncode != 0 and "--world applies to check only" in proc.stderr


def test_real_world_closure_bars_are_counted_not_refused(stores) -> None:
    """The lead's ruling after the first check --world (V2.2b): on a real world the panel builder
    and check skip the synthetic session-grid assertion, which would refuse NQ's closure bars;
    the frozen loader accepted them and their counts are recorded."""
    from ml_route_v2.pipeline import BarGridError, PipelineError, assert_bars_on_session_grid
    from pattern_search.panel import build_search_panel, is_real
    from pattern_search.run import closure_record

    base, recs = stores
    world = _world_fn(base, recs)(None)
    assert is_real(world)
    with pytest.raises(BarGridError, match="NQ: 2 bars outside the open intervals"):
        assert_bars_on_session_grid(world.bars)  # what the synthetic guard would have done
    counts = closure_record(world)
    assert counts["NQ"]["outside_open_intervals"] == 2 and counts["NQ"]["close_minute"] == 1
    nq = world.bars["NQ"]
    assert (nq["trade_date"].astype(str) == NEXT_DAY.isoformat()).sum() > 0
    with pytest.raises(PipelineError, match="empty"):  # past the grid stage: a 3-month fixture
        build_search_panel(world)  # has no row after the warm-up, and no BarGridError is raised
    with pytest.raises(BarGridError):
        build_search_panel(world, check_grid=True)  # an explicit request still applies it
