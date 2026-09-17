"""Tests for funnel/quality_generator.py (Stage B, Task 4): the assumed-quality
(p, R) daily P&L generator used by the power gate.

All ``SegmentTable`` fixtures here are hand-built directly (bypassing
``build_segment_table`` and its holdout/embargo refusal, which is
``funnel.null_generator``'s job and covered by its own tests), same pattern as
``tests/test_null_generator.py``'s ``_table`` helper.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from funnel.null_generator import SegmentTable
from funnel.quality_generator import (
    NULL_QUALITY,
    QualityDayGenerator,
    QualityParams,
    expected_edge_ticks,
)


def _table(move: list[list[int]], low: list[list[int]], high: list[list[int]]) -> SegmentTable:
    move_a = np.asarray(move, dtype=np.int64)
    low_a = np.asarray(low, dtype=np.int64)
    high_a = np.asarray(high, dtype=np.int64)
    n_days, segs = move_a.shape
    zeros = np.zeros((n_days, segs), dtype=np.int64)
    return SegmentTable(
        trade_dates=tuple(f"day-{i:06d}" for i in range(n_days)),
        segments_per_day=segs,
        move_ticks=move_a, low_ticks=low_a, high_ticks=high_a,
        entry_minute_ct=zeros, exit_minute_ct=zeros,
    )


# ===================================================== QualityParams validation ====
def test_quality_params_rejects_win_probability_outside_open_unit_interval() -> None:
    with pytest.raises(ValueError):
        QualityParams(win_probability=0.0, win_loss_ratio=1.0)
    with pytest.raises(ValueError):
        QualityParams(win_probability=1.0, win_loss_ratio=1.0)
    with pytest.raises(ValueError):
        QualityParams(win_probability=-0.1, win_loss_ratio=1.0)


def test_quality_params_rejects_non_positive_win_loss_ratio() -> None:
    with pytest.raises(ValueError):
        QualityParams(win_probability=0.5, win_loss_ratio=0.0)
    with pytest.raises(ValueError):
        QualityParams(win_probability=0.5, win_loss_ratio=-1.0)


def test_breakeven_win_probability_hand_value() -> None:
    # breakeven = 1 / (1 + R); R = 1.5 -> 1 / 2.5 = 0.4
    params = QualityParams(win_probability=0.5, win_loss_ratio=1.5)
    assert params.breakeven_win_probability == pytest.approx(0.4)


# ===================================================== forced win / forced loss ====
# Shared 1-day, 2-segment table: move = [+8, -4] ticks (long-side move per micro).
# winning_side is therefore [+1, -1] regardless of win/loss outcome: seg 0's
# money-making side is long (move >= 0), seg 1's is short (move < 0).
_FORCED_TABLE = _table(move=[[8, -4]], low=[[-2, -6]], high=[[10, 2]])
_FORCED_R = 4.0  # sqrt(R) = 2, 1/sqrt(R) = 0.5: clean numbers to hand-verify


def test_forced_win_scales_profitable_orientation_by_sqrt_r() -> None:
    """win_probability=0.999999: a uniform [0, 1) draw lands below it with
    probability 1 - 1e-6 per segment, so both segments are WINS with
    overwhelming probability (~1 - 2e-6) for any fixed seed. A win takes
    winning_side, scaled by sqrt(R) = 2:
      seg0: side=+1, pnl = +1 * 8 * 2 = 16;  adverse = low(-2) * 2 = -4 (side>0 -> low)
      seg1: side=-1, pnl = -1 * -4 * 2 = 8;  adverse = -high(2) * 2 = -4 (side<0 -> -high)
    """
    params = QualityParams(win_probability=0.999999, win_loss_ratio=_FORCED_R)
    draws = QualityDayGenerator(_FORCED_TABLE, params).draw(np.random.default_rng(42), 1)

    assert draws.side.tolist() == [[1, -1]]
    assert draws.pnl_ticks.ravel().tolist() == pytest.approx([16.0, 8.0])
    assert draws.adverse_ticks.ravel().tolist() == pytest.approx([-4.0, -4.0])


def test_forced_loss_scales_unprofitable_orientation_by_inverse_sqrt_r() -> None:
    """win_probability=0.000001: a uniform [0, 1) draw lands below it with
    probability 1e-6 per segment, so both segments are LOSSES with overwhelming
    probability (~1 - 2e-6) for any fixed seed. A loss takes -winning_side,
    scaled by 1/sqrt(R) = 0.5:
      seg0: side=-1, pnl = -1 * 8 * 0.5 = -4;  adverse = -high(10) * 0.5 = -5 (side<0)
      seg1: side=+1, pnl = +1 * -4 * 0.5 = -2; adverse = low(-6) * 0.5 = -3 (side>0)
    """
    params = QualityParams(win_probability=0.000001, win_loss_ratio=_FORCED_R)
    draws = QualityDayGenerator(_FORCED_TABLE, params).draw(np.random.default_rng(43), 1)

    assert draws.side.tolist() == [[-1, 1]]
    assert draws.pnl_ticks.ravel().tolist() == pytest.approx([-4.0, -2.0])
    assert draws.adverse_ticks.ravel().tolist() == pytest.approx([-5.0, -3.0])


# ===================================================== long-run statistics ====
# A table where every segment has |move| = 40 ticks exactly (only the sign
# varies by nothing -- every day is +40): this makes every WIN's pnl magnitude
# exactly 40*sqrt(R) and every LOSS's exactly 40/sqrt(R), with zero within-group
# variance, so avg(win)/avg(loss) == R exactly (no statistical tolerance needed,
# for any run with >= 1 win and >= 1 loss).
_UNIFORM_TABLE = _table(move=[[40]], low=[[-10]], high=[[50]])


def test_avg_win_over_avg_loss_equals_r_and_win_share_matches_p() -> None:
    """Win share is genuinely stochastic (independent Bernoulli(p) per segment):
    tolerance is 4 standard errors of a binomial proportion, sqrt(p(1-p)/n)
    (same 4-sigma convention as tests/test_null_generator.py; false-failure
    chance on the order of 1e-4)."""
    p, r = 0.35, 2.0
    params = QualityParams(win_probability=p, win_loss_ratio=r)
    n = 20_000
    draws = QualityDayGenerator(_UNIFORM_TABLE, params).draw(np.random.default_rng(7), n)

    winning_side = np.where(_UNIFORM_TABLE.move_ticks[draws.day_index] >= 0, 1, -1)
    is_win = draws.side == winning_side
    assert is_win.any()
    assert (~is_win).any()

    avg_win = draws.pnl_ticks[is_win].mean()
    avg_loss = -draws.pnl_ticks[~is_win].mean()
    assert avg_win / avg_loss == pytest.approx(r, abs=1e-9)

    win_share = is_win.mean()
    se = math.sqrt(p * (1 - p) / n)
    assert abs(win_share - p) <= 4 * se


# ===================================================== expected_edge_ticks ====
def test_expected_edge_ticks_hand_computed() -> None:
    # E|m| * (p*sqrt(R) - (1-p)/sqrt(R)); E|m| = 40 (uniform table)
    p, r = 0.6, 1.5
    params = QualityParams(win_probability=p, win_loss_ratio=r)
    root = math.sqrt(r)
    expected = 40.0 * (p * root - (1.0 - p) / root)
    assert expected_edge_ticks(params, _UNIFORM_TABLE) == pytest.approx(expected)


def test_expected_edge_ticks_is_zero_at_breakeven_win_probability() -> None:
    r = 1.5
    breakeven = 1.0 / (1.0 + r)
    params = QualityParams(win_probability=breakeven, win_loss_ratio=r)
    assert expected_edge_ticks(params, _UNIFORM_TABLE) == pytest.approx(0.0, abs=1e-9)


# ===================================================== NULL_QUALITY == the null ====
def test_null_quality_mean_pnl_near_zero_on_a_drifted_table() -> None:
    """At NULL_QUALITY (p=0.5, R=1) the side is a fair coin independent of the
    data (same property the null generator itself guarantees), so even on a
    table where EVERY move is +40 ticks (a "drifted" market), the long-run mean
    P&L should be near zero: tolerance is 4 standard errors of the draw's own
    sample mean (computed from the draw, not pasted from a prior run)."""
    draws = QualityDayGenerator(_UNIFORM_TABLE, NULL_QUALITY).draw(np.random.default_rng(11),
                                                                    20_000)
    pnl = draws.pnl_ticks.ravel()
    se = pnl.std(ddof=1) / math.sqrt(pnl.size)
    assert abs(pnl.mean()) <= 4 * se
