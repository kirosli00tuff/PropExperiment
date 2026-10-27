"""Stage E.32 Part 0: the soybean-complex test-window seal (reports/stage_e32_briefs/seal/).

Every test runs on synthetic bytes in tmp_path with its own HoldoutPaths; nothing here reads the
real store, the real logs or REGISTRATION.md.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

from data import holdout as ho

REPO = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location(
    "soy_test_seal", REPO / "reports" / "stage_e32_briefs" / "seal" / "soy_test_seal.py")
soy = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = soy  # dataclasses look their module up while the class is built
_SPEC.loader.exec_module(soy)

GLBX = "data/vendor/databento/GLBX.MDP3"
IN_WINDOW = (
    f"{GLBX}/ohlcv-1m/ZS_v_0/range=2017-04-01_2017-05-01.dbn.zst",
    f"{GLBX}/ohlcv-1m/ZS_v_0/range=2020-11-01_2020-12-01.dbn.zst",
    "data/processed_step2/ZM/ohlcv-1m_ZM_v_0_2019-05-06_2024-02-29_step2.parquet",
    "reports/cache/ZS.parquet",
)
OUT_OF_WINDOW = (
    f"{GLBX}/ohlcv-1m/ZS_v_0/range=2017-03-01_2017-04-01.dbn.zst",
    f"{GLBX}/ohlcv-1m/ZS_v_0/range=2020-12-01_2021-01-01.dbn.zst",
    f"{GLBX}/mbo/Z1_ZM_v_0-ZM_v_1/range=2020-11-30T220000Z_2020-12-31T220000Z.dbn.zst",
    f"{GLBX}/ohlcv-1m/ZC_v_0/range=2018-01-01_2018-02-01.dbn.zst",  # another root
    "data/processed/ZM/ohlcv-1m_ZM_v_0_2025-04-01_2026-06-19_research.parquet",
)
REGISTRATION = ("Registered soybean test. metric: net ticks per trade. threshold: t > 3.0. "
                "decision: pass or fail, written before any read. " * 3)


def _layout(repo: Path) -> soy.Layout:
    return soy.Layout(repo_root=repo, glbx=repo / GLBX,
                      store_globs=("data/processed/{root}/*", "data/processed_step2/{root}/*"),
                      caches=(("reports/cache/ZS.parquet", "2010-07-01", "2024-02-29"),))


def _paths(tmp: Path) -> ho.HoldoutPaths:
    return ho.HoldoutPaths(sealed_root=tmp / "sealed", manifest=tmp / "docs" / "m.json",
                           unlock_log=tmp / "docs" / "log.md", registration=tmp / "REG.md",
                           research_parquet=tmp, holdout_id=3)


@pytest.fixture
def world(tmp_path):
    repo = tmp_path / "repo"
    contents = {}
    for rel in (*IN_WINDOW, *OUT_OF_WINDOW, f"{GLBX}/mbo/Z1_ZM_v_0-ZM_v_1/manifest.json"):
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        contents[rel] = os.urandom(257)
        path.write_bytes(contents[rel])
    return repo, _layout(repo), _paths(tmp_path), contents


@pytest.mark.parametrize(("name", "inside"), [
    ("range=2017-03-01_2017-04-01.dbn.zst", False),
    ("range=2017-04-01_2017-05-01.dbn.zst", True),  # its last hours are 2017-05-01's pre-open
    ("range=2020-11-01_2020-12-01.dbn.zst", True),
    ("range=2020-12-01_2021-01-01.dbn.zst", False),
    ("range=2020-11-30T220000Z_2020-12-31T220000Z.dbn.zst", False),  # E.31's first chunk
    ("range=2020-10-31T220000Z_2020-11-30T220000Z.dbn.zst", True),
    ("glbx-mdp3-ohlcv-1d-QM.FUT_ZM.FUT-parent-2023-01-01_2026-10-22.dbn.zst", False),
    ("glbx-mdp3-ohlcv-1d-ZM.FUT-parent-2015-01-01_2017-04-30.dbn.zst", True),  # inclusive end
])
def test_raw_window_rule_at_the_boundaries(name, inside):
    assert soy.raw_touches_window(*soy.raw_span(name)) is inside


@pytest.mark.parametrize(("first", "last", "inside"), [
    ("2010-07-01", "2017-04-30", False), ("2010-07-01", "2017-05-01", True),
    ("2020-11-30", "2024-02-29", True), ("2020-12-01", "2024-02-29", False),
])
def test_store_window_rule_is_inclusive_on_trade_dates(first, last, inside):
    assert soy.store_touches_window(first, last) is inside


def test_window_utc_bounds_are_16h_central_around_the_trade_dates():
    start, end = soy.WINDOW_UTC
    assert start == datetime(2017, 4, 30, 21, tzinfo=UTC)
    assert end == datetime(2020, 11, 30, 22, tzinfo=UTC)


def test_scan_lists_only_the_three_roots_files_that_touch_the_window(world):
    repo, layout, _, _ = world
    targets, unclassified = soy.scan(layout)
    assert sorted(t.relpath for t in targets) == sorted(IN_WINDOW)
    assert unclassified == []


def test_an_undatable_file_fails_closed(world):
    repo, layout, paths, _ = world
    odd = repo / GLBX / "ohlcv-1m" / "ZL_v_0" / "odd.bin"
    odd.parent.mkdir(parents=True)
    odd.write_bytes(b"x")
    with pytest.raises(soy.UnclassifiedFileError):
        soy.seal_all(paths, layout)
    assert not paths.manifest.exists() and not paths.sealed_root.exists()


def test_seal_removes_in_window_plaintext_only_and_status_is_ok(world):
    repo, layout, paths, contents = world
    manifest = soy.seal_all(paths, layout)
    assert len(manifest["raw_files"]) == len(IN_WINDOW)
    for rel in IN_WINDOW:
        assert not (repo / rel).exists()
        record = next(r for r in manifest["raw_files"] if r["original_relpath"] == rel)
        assert record["sha256_plaintext"] == ho.sha256_bytes(contents[rel])
        assert (paths.sealed_root / record["sealed_relpath"]).read_bytes() != contents[rel]
    for rel in OUT_OF_WINDOW:
        assert (repo / rel).read_bytes() == contents[rel]
    report = soy.status(paths, layout)
    assert report["all_ok"] and report["unlocks_logged"] == 0
    log = paths.unlock_log.read_text()
    assert log.count("SEALED soy test") == len(IN_WINDOW) and " UNLOCK " not in log


def test_rerun_is_a_no_op_and_finishes_an_interrupted_seal(world):
    repo, layout, paths, contents = world
    soy.seal_all(paths, layout)
    soy.seal_all(paths, layout)  # nothing left to do
    rel = IN_WINDOW[2]
    (repo / rel).write_bytes(contents[rel])  # as if removal had not happened
    assert not soy.status(paths, layout)["all_ok"]
    soy.seal_all(paths, layout)
    assert not (repo / rel).exists() and "RESUMED soy test" in paths.unlock_log.read_text()
    assert soy.status(paths, layout)["all_ok"]


def test_a_different_file_at_a_sealed_path_is_kept_and_refused(world):
    repo, layout, paths, _ = world
    soy.seal_all(paths, layout)
    rel = IN_WINDOW[0]
    (repo / rel).write_bytes(b"not the sealed bytes")
    with pytest.raises(ho.SealIntegrityError):
        soy.seal_all(paths, layout)
    assert (repo / rel).exists()


def test_new_in_window_plaintext_after_the_seal_is_flagged_and_refused(world):
    repo, layout, paths, _ = world
    soy.seal_all(paths, layout)
    new = repo / GLBX / "ohlcv-1m" / "ZS_v_0" / "range=2019-01-01_2019-02-01.dbn.zst"
    new.write_bytes(b"re-bought")
    report = soy.status(paths, layout)
    assert not report["all_ok"]
    assert report["plaintext_in_window_present"] == [os.path.relpath(new, repo)]
    with pytest.raises(ValueError, match="not in the fixed plan"):
        soy.seal_all(paths, layout)
    assert new.exists()


def _unseal(paths, layout, rel, repo, **overrides):
    kwargs = {"stage": "Stage E.34 soy test", "reason": "the registered one-shot soybean test",
              "acknowledgement": soy.ACKNOWLEDGEMENT, "prior_unlocks_acknowledged": 0,
              "paths": paths, "layout": layout, **overrides}
    return soy.unseal_file(repo / rel, **kwargs)


def test_unseal_without_a_registration_logs_nothing_and_restores_nothing(world):
    repo, layout, paths, _ = world
    soy.seal_all(paths, layout)
    before = paths.unlock_log.read_bytes()
    paths.registration.write_text("")
    with pytest.raises(ho.HoldoutLockedError):
        _unseal(paths, layout, IN_WINDOW[1], repo)
    assert paths.unlock_log.read_bytes() == before and not (repo / IN_WINDOW[1]).exists()


@pytest.mark.parametrize("override", [
    {"stage": "Stage D.2"}, {"acknowledgement": ho.ACKNOWLEDGEMENT}, {"reason": "short"},
    {"prior_unlocks_acknowledged": 1},
])
def test_unseal_refuses_a_wrong_stage_phrase_reason_or_count(world, override):
    repo, layout, paths, _ = world
    soy.seal_all(paths, layout)
    paths.registration.write_text(REGISTRATION)
    with pytest.raises(ho.HoldoutLockedError):
        _unseal(paths, layout, IN_WINDOW[1], repo, **override)
    assert " UNLOCK " not in paths.unlock_log.read_text()


def test_unseal_with_the_ceremony_logs_first_and_restores_identical_bytes(world):
    repo, layout, paths, contents = world
    soy.seal_all(paths, layout)
    paths.registration.write_text(REGISTRATION)
    restored = _unseal(paths, layout, IN_WINDOW[1], repo)
    assert restored.read_bytes() == contents[IN_WINDOW[1]]
    assert not os.access(restored, os.W_OK)
    assert ho.prior_unlocks(paths) == 1 and "UNLOCK soy test file" in paths.unlock_log.read_text()
    with pytest.raises(ho.HoldoutLockedError):  # the second read must admit the first
        _unseal(paths, layout, IN_WINDOW[0], repo)
    assert _unseal(paths, layout, IN_WINDOW[0], repo, prior_unlocks_acknowledged=1).exists()


def test_the_store_keeps_its_own_log_phrase_and_manifest_dir():
    """A soybean UNLOCK in the shared log would count as holdout 1's (data.holdout.prior_unlocks),
    and a manifest in docs/holdout2/ would be read by data.holdout status as a product store."""
    assert soy.PATHS.unlock_log not in {ho.DEFAULT_PATHS.unlock_log, ho.HOLDOUT2_PATHS.unlock_log}
    assert soy.ACKNOWLEDGEMENT != ho.ACKNOWLEDGEMENT
    assert soy.PATHS.manifest.parent.name != "holdout2"
    assert soy.PATHS.sealed_root.name not in {"MES_holdout_v1", "MES_holdout_v2"}
