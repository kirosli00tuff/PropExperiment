"""H1 -- NR4 opening-range breakout (Stage D.1f, Family H, class C7).

Specification, FROZEN: reports/stage_d1f_confirmation_list.md section 2.1 A3, row H1.
Condition on day d (complete prior daily bars only): Range[d-1] is strictly smaller than each
of Range[d-2], Range[d-3], Range[d-4]. Entry: breakout of the 30-minute opening range, 2
micros, exit at 14:58 CT; the mechanics are in ``_mechanics``. Instrument guard: d-1 only;
Range[d-2..d-4] are basis-free and exempt (H-1). Source: Crabel's narrow-range conditioning
of opening-range breakouts; no parameter is taken from any result seen in this program.
"""

from __future__ import annotations

from collections.abc import Sequence

from strategy.research.h_daily_bar._mechanics import (
    Condition,
    DailyBar,
    DailyBarStrategy,
    narrowest_range,
)

LABEL = "H1 NR4 opening-range breakout"
NAME = "h1_nr4_opening_range_breakout"
LOOKBACK = 4
GUARDED_BARS = 1
ENTRY = "breakout"


def condition(prior: Sequence[DailyBar]) -> Condition | None:
    """Day d's condition from the complete daily bars of dates before d (oldest first).
    values = (Range[d-1], Range[d-2], Range[d-3], Range[d-4]) in ticks; None during warm-up."""
    return narrowest_range(prior, LOOKBACK)


class H1Nr4Breakout(DailyBarStrategy):
    def __init__(self) -> None:
        super().__init__(name=NAME, condition=condition, lookback=LOOKBACK,
                         guarded_bars=GUARDED_BARS, entry=ENTRY)


def factory() -> H1Nr4Breakout:
    """The registered D.1f factory: no arguments, every parameter a literal above."""
    return H1Nr4Breakout()
