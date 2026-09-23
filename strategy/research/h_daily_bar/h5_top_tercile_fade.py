"""H5 -- top-tercile prior range, opening-range fade (Stage D.1f, Family H, class C7).

Specification, FROZEN: reports/stage_d1f_confirmation_list.md section 2.1 A3, row H5.
Condition on day d (complete prior daily bars only): Range[d-1] >= P66.67 of Range over the
60 complete bars before d-1, with np.percentile(ranges, 66.67, method="linear") (H-7); the
lookback is 61 (d-1 plus those 60). Entry: FADE, the breakout trigger of the 30-minute opening
range with the opposite side, 2 micros, exit at 14:58 CT; the mechanics are in
``_mechanics``. Instrument guard: d-1 only; the trailing 60 ranges are exempt (NEW-9).
Source: Crabel's contraction-expansion framing; no parameter is taken from any result seen
in this program.

Test-only override (H-4): the constructor's private ``_lookback`` shortens the 61-bar warm-up
in the synthetic known-answer test. Its default is LOOKBACK; no configuration sets it and the
registered ``factory`` never passes it.
"""

from __future__ import annotations

from collections.abc import Sequence
from functools import partial

from strategy.research.h_daily_bar._mechanics import (
    Condition,
    DailyBar,
    DailyBarStrategy,
    range_and_percentile,
)

LABEL = "H5 top-tercile prior range, opening-range fade"
NAME = "h5_top_tercile_prior_range_opening_range_fade"
LOOKBACK = 61
PERCENTILE_Q = 66.67
GUARDED_BARS = 1
ENTRY = "fade"


def condition(prior: Sequence[DailyBar], *, _lookback: int = LOOKBACK) -> Condition | None:
    """Day d's condition from the complete daily bars of dates before d (oldest first).
    values = (Range[d-1] in ticks, P66.67 cut in ticks); None during warm-up."""
    measured = range_and_percentile(prior, _lookback, PERCENTILE_Q)
    if measured is None:
        return None
    last, cut = measured
    return Condition(holds=last >= cut, values=(last, cut))


class H5TopTercileFade(DailyBarStrategy):
    def __init__(self, *, _lookback: int = LOOKBACK) -> None:
        if isinstance(_lookback, bool) or not isinstance(_lookback, int) or _lookback < 2:
            raise ValueError(f"_lookback {_lookback!r} must be an int >= 2")
        super().__init__(name=NAME, condition=partial(condition, _lookback=_lookback),
                         lookback=_lookback, guarded_bars=GUARDED_BARS, entry=ENTRY)


def factory() -> H5TopTercileFade:
    """The registered D.1f factory: no arguments, every parameter a literal above."""
    return H5TopTercileFade()
