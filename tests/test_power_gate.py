"""Tests for funnel/power_gate.py (Stage B, Task 4): the power screen's pure
statistics (verdict, p_beats) and its I/O-light helpers (critical_value,
runs_per_point, screen) against hand-built baseline/gate dictionaries."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pytest

from funnel.power_gate import (
    MIN_RUNS_PER_POINT,
    critical_value,
    p_beats,
    runs_per_point,
    screen,
    verdict,
)


# ===================================================== verdict() ====
def test_verdict_hand_cases() -> None:
    """se = sqrt(power*(1-power)/n); lower = power - 1.96*se;
    pass if lower >= 0.80, marginal if power >= 0.80 (but lower < 0.80),
    else fail."""
    n = 8_000

    power = 0.9
    se = math.sqrt(power * (1 - power) / n)
    lower = power - 1.96 * se
    assert se == pytest.approx(0.003354, abs=1e-6)
    assert lower == pytest.approx(0.8934, abs=1e-4)
    label, se_out, lower_out = verdict(power, n)
    assert se_out == pytest.approx(se)
    assert lower_out == pytest.approx(lower)
    assert label == "pass"

    power = 0.805
    se = math.sqrt(power * (1 - power) / n)
    lower = power - 1.96 * se
    assert se == pytest.approx(0.004432, abs=1e-4)
    assert lower == pytest.approx(0.7963, abs=1e-4)
    label, se_out, lower_out = verdict(power, n)
    assert se_out == pytest.approx(se)
    assert lower_out == pytest.approx(lower)
    assert label == "marginal"

    power = 0.79
    label, se_out, lower_out = verdict(power, n)
    assert label == "fail"


# ===================================================== p_beats() ====
def test_p_beats_hand_value_ties_count_half() -> None:
    # X = [1, 2, 3], null sorted = [2]: 1 is strictly below (0), 2 ties (0.5),
    # 3 is strictly above (1) -> mean(0, 0.5, 1) / len([2]) = 0.5 / 1 = 0.5
    result = p_beats(np.array([1.0, 2.0, 3.0]), np.array([2.0]))
    assert result == pytest.approx(0.5)


# ===================================================== critical_value() / runs_per_point() ====
def test_critical_value_reads_hand_built_baseline() -> None:
    baseline = {
        "null_critical_values_monthly_net_usd": {
            "standard": {"monthly_net_p80": {"value": 123.45}},
            "consistency": {"monthly_net_p90": {"value": -7.0}},
        },
    }
    assert critical_value(baseline, "standard", 0.80) == pytest.approx(123.45)
    assert critical_value(baseline, "consistency", 0.90) == pytest.approx(-7.0)


def test_runs_per_point_returns_min_runs_when_baseline_is_stable() -> None:
    baseline = {
        "headline": {
            "standard": {"stability": {"stable_n": 4_000}},
            "consistency": {"stability": {"stable_n": 8_000}},
        },
    }
    assert runs_per_point(baseline) == MIN_RUNS_PER_POINT


def test_runs_per_point_raises_when_a_stable_n_is_none() -> None:
    baseline = {
        "headline": {
            "standard": {"stability": {"stable_n": None}},
            "consistency": {"stability": {"stable_n": 8_000}},
        },
    }
    with pytest.raises(ValueError):
        runs_per_point(baseline)


# ===================================================== screen() ====
def _write_gate(tmp_path: Path) -> Path:
    """A tiny power_gate.json: 2 paths x 2 win_probability x 2 win_loss_ratio x
    1 segments_per_day = 8 rows. Each row's verdict fields are unique marker
    strings so a lookup's identity is unambiguous."""
    grid = {
        "win_probability": [0.5, 0.55],
        "win_loss_ratio": [1.0, 1.5],
        "segments_per_day": [1],
    }
    rows = []
    for path in ("standard", "consistency"):
        for p in grid["win_probability"]:
            for r in grid["win_loss_ratio"]:
                rows.append({
                    "path": path,
                    "win_probability": p,
                    "win_loss_ratio": r,
                    "segments_per_day": 1,
                    "c80_verdict": f"v80_{path}_{p}_{r}",
                    "c80_power": 0.80,
                    "c80_power_lower95": 0.75,
                    "c90_verdict": f"v90_{path}_{p}_{r}",
                    "c90_power": 0.90,
                    "c90_power_lower95": 0.85,
                })
    gate_path = tmp_path / "power_gate.json"
    gate_path.write_text(json.dumps({"grid": grid, "rows": rows}))
    return gate_path


def test_screen_picks_conservative_floor_grid_point(tmp_path: Path) -> None:
    """p=0.57 -> largest grid p <= 0.57 is 0.55; R=1.4 -> largest grid R <= 1.4
    is 1.0 (1.5 is excluded). Expected row: p=0.55, R=1.0."""
    gate_path = _write_gate(tmp_path)
    result = screen("standard", win_probability=0.57, win_loss_ratio=1.4, segments_per_day=1,
                     gate_json=gate_path)
    assert result["verdict"] == "v80_standard_0.55_1.0"
    assert result["grid_point"]["win_probability"] == pytest.approx(0.55)
    assert result["grid_point"]["win_loss_ratio"] == pytest.approx(1.0)


def test_screen_confidence_tag_selects_c80_vs_c90(tmp_path: Path) -> None:
    gate_path = _write_gate(tmp_path)
    r80 = screen("standard", 0.57, 1.4, 1, confidence=0.80, gate_json=gate_path)
    r90 = screen("standard", 0.57, 1.4, 1, confidence=0.90, gate_json=gate_path)
    assert r80["verdict"] == "v80_standard_0.55_1.0"
    assert r80["power"] == pytest.approx(0.80)
    assert r90["verdict"] == "v90_standard_0.55_1.0"
    assert r90["power"] == pytest.approx(0.90)


def test_screen_below_grid_win_probability(tmp_path: Path) -> None:
    gate_path = _write_gate(tmp_path)
    result = screen("standard", win_probability=0.45, win_loss_ratio=1.0, segments_per_day=1,
                     gate_json=gate_path)
    assert result == {"verdict": "below_grid", "grid_point": None}


def test_screen_rejects_unsupported_segments_per_day(tmp_path: Path) -> None:
    gate_path = _write_gate(tmp_path)
    with pytest.raises(ValueError):
        screen("standard", 0.5, 1.0, segments_per_day=3, gate_json=gate_path)
