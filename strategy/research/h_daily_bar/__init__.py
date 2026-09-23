"""Family H (Stage D.1f, class C7): daily-bar constructions for intraday entries.

Specification, FROZEN: reports/stage_d1f_confirmation_list.md section 2.1 A3. The shared
mechanics are in ``_mechanics``; each h*_ module holds one row of the condition table.

R-7: an H module run on real bars before step 7 of the confirmation counts as a screen
against N and must be logged as a look. Until then these modules run on synthetic bars only.

``H_TRIALS`` is the list runner's input: six (label, zero-argument factory) pairs, the labels
exactly as the table's ID column.
"""

from __future__ import annotations

from collections.abc import Callable

from strategy.interface import Strategy
from strategy.research.h_daily_bar import (
    h1_nr4_breakout,
    h2_nr7_breakout,
    h3_inside_day_breakout,
    h4_bottom_tercile_breakout,
    h5_top_tercile_fade,
    h6_prior_close_location,
)

H_MODULES = (
    h1_nr4_breakout,
    h2_nr7_breakout,
    h3_inside_day_breakout,
    h4_bottom_tercile_breakout,
    h5_top_tercile_fade,
    h6_prior_close_location,
)
H_TRIALS: tuple[tuple[str, Callable[[], Strategy]], ...] = tuple(
    (module.LABEL, module.factory) for module in H_MODULES
)

__all__ = ["H_MODULES", "H_TRIALS"]
