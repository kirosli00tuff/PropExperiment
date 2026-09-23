"""H3 -- inside-day opening-range breakout (Stage D.1f, Family H, class C7).

Specification, FROZEN: reports/stage_d1f_confirmation_list.md section 2.1 A3, row H3.
Condition on day d (complete prior daily bars only): H[d-1] < H[d-2] and L[d-1] > L[d-2].
Entry: breakout of the 30-minute opening range, 2 micros, exit at 14:58 CT; the mechanics are
in ``_mechanics``. Instrument guard: both d-1 and d-2 must carry day d's 08:30 instrument_id,
which is what removes the first post-splice day (H-1). Source: Crabel's inside-day
conditioning of opening-range breakouts; no parameter is taken from any result seen here.
"""

from __future__ import annotations

from collections.abc import Sequence

from strategy.research.h_daily_bar._mechanics import Condition, DailyBar, DailyBarStrategy

LABEL = "H3 inside-day opening-range breakout"
NAME = "h3_inside_day_opening_range_breakout"
LOOKBACK = 2
GUARDED_BARS = 2
ENTRY = "breakout"


def condition(prior: Sequence[DailyBar]) -> Condition | None:
    """Day d's condition from the complete daily bars of dates before d (oldest first).
    values = (H[d-1], H[d-2], L[d-1], L[d-2]) in points; None during warm-up."""
    if len(prior) < LOOKBACK:
        return None
    last, before = prior[-1], prior[-2]
    holds = last.high_ticks < before.high_ticks and last.low_ticks > before.low_ticks
    return Condition(holds=holds, values=(last.high, before.high, last.low, before.low))


class H3InsideDayBreakout(DailyBarStrategy):
    def __init__(self) -> None:
        super().__init__(name=NAME, condition=condition, lookback=LOOKBACK,
                         guarded_bars=GUARDED_BARS, entry=ENTRY)


def factory() -> H3InsideDayBreakout:
    """The registered D.1f factory: no arguments, every parameter a literal above."""
    return H3InsideDayBreakout()
