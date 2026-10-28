"""Unit tests of the B3 harness's cell rules and frame join (pipeline/tests_b3/compare_b3.py). Synthetic frames only."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests_b3"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import compare_b3 as cb  # noqa: E402


def test_feature_rule_relative_and_absolute() -> None:
    a = np.array([1.0, 1.0, 0.0, 0.0, np.nan, 5.0, 1e6])
    b = np.array([1.0 + 5e-10, 1.0 + 2e-9, 5e-13, 2e-12, np.nan, np.nan, 1e6 + 5e-4])
    assert cb.eq_feature(a, b).tolist() == [True, False, True, False, True, False, True]


def test_exact_rule_nan_and_ints() -> None:
    assert cb.eq_exact(np.array([1.0, np.nan, 0.528]), np.array([1.0, np.nan, 0.5280000000000001])).tolist() == [
        True, True, False]
    assert cb.eq_exact(np.array([3, -1], np.int64), np.array([3, 1], np.int64)).tolist() == [True, False]


def test_weight_rule() -> None:
    assert cb.eq_weight(np.array([0.5, 0.5, np.nan]), np.array([0.5 + 1e-13, 0.5 + 1e-11, np.nan])).tolist() == [
        True, False, True]


def test_compare_frames_counts_and_locations() -> None:
    a = pd.DataFrame({"i": [0, 1, 2, 3], "y": [1, 0, -1, 0], "w": [0.5, 0.25, np.nan, 1.0]})
    b = pd.DataFrame({"i": [0, 1, 2, 4], "y": [1, 1, -1, 0], "w": [0.5, 0.25, np.nan, 1.0]})
    t, cells = cb.compare_frames(a, b, {"y": "exact", "w": "weight"})
    assert t.rows == 3 and t.disagree["y"] == 1 and t.disagree.get("w", 0) == 0
    assert t.disagree[cb.ROW_COL] == 2 and t.rows_with_mismatch == 1
    locs = {(c["i"], c["column"]) for c in cells}
    assert locs == {(1, "y"), (3, cb.ROW_COL), (4, cb.ROW_COL)}


def test_b3_dates_rule() -> None:
    d = cb.b3_dates()
    assert len(d) == 20 and d == sorted(d) and d[0] == "2021-01-19" and d[-1] == "2024-02-15"
