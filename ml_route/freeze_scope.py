"""M7.8's scope: what the Stage E harness manifest must hash for the ML route, and the check.

M7.8 (Stage E.2a ruling on audit ML-A04): "E.2b's harness manifest hashes the route's whole
pipeline (the feature and target builders, the block cut, the CPCV splitter, the selection,
surrogate, pre-test, ranking and write-up code, and every M7 test) before E.ML-buy; ...
E.ML-train and E.ML-test refuse to run when any hashed file differs."

``screening.harness_freeze.preflight`` refuses any listed file that differs and any *.py under a
harness directory (ml_route/ is one) that the manifest does not list, so every pipeline module is
covered by construction. The M7 TESTS live under tests/, which is not a harness directory, so
nothing forced the manifest to list them. ``check_harness_scope`` closes that gap: E.ML-test
calls it right after the preflight and refuses, naming each file, when the manifest leaves out
an ml_route module or an M7 test. ``M78_ITEMS`` maps each item M7.8 names to where it lives
(the completeness table of reports/stage_e2b_g4_mltest_worker.md is this mapping).
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from data.config import REPO_ROOT

# Each item M7.8 names -> the files that implement it (function names in the worker report).
M78_ITEMS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("feature builders", ("ml_route/features.py", "ml_route/rows.py", "ml_route/dataset.py",
                          "ml_route/lstm_data.py", "ml_route/store.py", "ml_route/inputs.py")),
    ("target builders", ("ml_route/rows.py",)),
    ("block cut", ("ml_route/blocks.py",)),
    ("CPCV splitter", ("ml_route/blocks.py",)),
    ("selection", ("ml_route/selection.py", "ml_route/adapters.py", "ml_route/lgbm.py",
                   "ml_route/lstm.py", "ml_route/lstm_machine.py", "ml_route/train.py",
                   "ml_route/ledger.py")),
    ("surrogate", ("ml_route/surrogate.py",)),
    ("pre-test", ("ml_route/surrogate.py",)),
    ("ranking", ("ml_route/surrogate.py",)),
    ("write-up", ("ml_route/surrogate.py", "ml_route/manifest.py")),
    ("E.ML-test and its engine path", ("ml_route/test.py", "ml_route/stage_e_adapter.py",
                                       "ml_route/rule_wrapper.py", "ml_route/accounting.py",
                                       "ml_route/freeze_scope.py")),
)
# M7.7's canaries outside tests/test_ml_route_*.py: the existing MES-engine canaries and the
# Stage E engine canaries (CanaryCoder, Stage E.2b Task 3).
M7_EXTRA_TESTS: tuple[str, ...] = ("tests/test_leakage_canaries.py",
                                   "tests/test_stage_e_canaries.py")
M7_TEST_GLOB = "tests/test_ml_route_*.py"


class RouteScopeError(RuntimeError):
    """The harness manifest does not hash everything M7.8 names."""


def required_files(root: Path = REPO_ROOT) -> tuple[str, ...]:
    """Every ml_route module, every tests/test_ml_route_*.py and the extra M7 tests."""
    root = Path(root)
    modules = {p.relative_to(root).as_posix() for p in (root / "ml_route").glob("*.py")}
    tests = {p.relative_to(root).as_posix() for p in root.glob(M7_TEST_GLOB)}
    return tuple(sorted(modules | tests | set(M7_EXTRA_TESTS)))


def uncovered(listed: Iterable[str], root: Path = REPO_ROOT) -> list[str]:
    listed = set(listed)
    return [f for f in required_files(root) if f not in listed]


def check_harness_scope(root: Path = REPO_ROOT) -> None:
    """Refuse unless the Stage E harness manifest lists every M7.8 file (call after preflight)."""
    from screening.harness_freeze import load_manifest

    manifest, _, problems = load_manifest(Path(root))
    if manifest is None:
        raise RouteScopeError("the harness manifest cannot be read: " + "; ".join(problems))
    missing = uncovered(manifest["files"], root)
    if missing:
        raise RouteScopeError("M7.8: the harness manifest does not hash " + ", ".join(missing))


__all__ = ["M78_ITEMS", "M7_EXTRA_TESTS", "RouteScopeError", "check_harness_scope",
           "required_files", "uncovered"]
