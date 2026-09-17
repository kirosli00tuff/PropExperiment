"""Assumed-quality daily P&L generator for the power gate (Stage B, Task 4).

This is NOT a strategy and encodes no signal. It is a hypothetical trade-outcome
distribution, "a strategy that wins with probability p and whose average win is R
times its average loss", laid over the same empirical MES magnitudes as the null,
so the power gate asks one question: would that quality beat luck through the
Topstep funnel?

Per segment (one round turn), on a stationary-block-bootstrapped research day:
- m = |long-side move| of the segment (ticks per micro), with its excursions;
- the trade WINS with probability p, drawn independently of every price;
- a win takes the orientation that made money (long if move >= 0, else short) and
  scales that path by sqrt(R); a loss takes the other orientation and scales by
  1/sqrt(R). So avg win / avg loss = R exactly, and the geometric mean scale is 1.
- Expected gross edge per segment = E[m] * (p*sqrt(R) - (1-p)/sqrt(R)); zero on the
  line p = 1/(1+R). At p = 0.5, R = 1 the side is a fair coin independent of the
  data: exactly the null generator's distribution.

Modelling caveat (in the report too): scaling a real path by sqrt(R) stands in for
whatever mechanism (stops, targets, holding time) produces that win/loss shape. The
grid screens funnel economics as a function of per-trade outcome statistics; it says
nothing about how to obtain them.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from funnel.null_generator import (
    DEFAULT_MEAN_BLOCK_DAYS,
    DayDraws,
    SegmentTable,
    stationary_bootstrap_indices,
)


@dataclass(frozen=True)
class QualityParams:
    win_probability: float
    win_loss_ratio: float  # average win / average loss

    def __post_init__(self) -> None:
        if not 0.0 < self.win_probability < 1.0:
            raise ValueError("win_probability must be in (0, 1)")
        if self.win_loss_ratio <= 0.0:
            raise ValueError("win_loss_ratio must be > 0")

    @property
    def breakeven_win_probability(self) -> float:
        return 1.0 / (1.0 + self.win_loss_ratio)


NULL_QUALITY = QualityParams(win_probability=0.5, win_loss_ratio=1.0)


def expected_edge_ticks(params: QualityParams, table: SegmentTable) -> float:
    """Expected gross P&L per segment per micro, in ticks, before costs."""
    root = math.sqrt(params.win_loss_ratio)
    mean_abs = float(np.abs(table.move_ticks).mean())
    p = params.win_probability
    return mean_abs * (p * root - (1.0 - p) / root)


@dataclass(frozen=True)
class QualityDayGenerator:
    table: SegmentTable
    params: QualityParams
    mean_block_days: float = DEFAULT_MEAN_BLOCK_DAYS

    def draw(self, rng: np.random.Generator, n_days: int) -> DayDraws:
        t = self.table
        idx = stationary_bootstrap_indices(rng, t.n_days, n_days, self.mean_block_days)
        win = rng.random((n_days, t.segments_per_day)) < self.params.win_probability
        move, low, high = t.move_ticks[idx], t.low_ticks[idx], t.high_ticks[idx]
        winning_side = np.where(move >= 0, 1, -1)
        side = np.where(win, winning_side, -winning_side)
        root = math.sqrt(self.params.win_loss_ratio)
        scale = np.where(win, root, 1.0 / root)
        return DayDraws(
            day_index=idx,
            side=side,
            pnl_ticks=side * move * scale,
            adverse_ticks=np.where(side > 0, low, -high) * scale,
            entry_minute_ct=t.entry_minute_ct[idx],
            exit_minute_ct=t.exit_minute_ct[idx],
        )
