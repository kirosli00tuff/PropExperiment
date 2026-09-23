"""H6 -- prior-close location follow-through (Stage D.1f, Family H, class C7).

Specification, FROZEN: reports/stage_d1f_confirmation_list.md section 2.1 A3, row H6.
Condition on day d (complete prior daily bars only): CLV = (C[d-1] - L[d-1]) / (H[d-1] -
L[d-1]), requiring Range[d-1] > 0; CLV >= 0.8 buys, CLV <= 0.2 sells, otherwise no trade.
Entry: OPEN, a market order decided on day d's 08:30 CT bar (it fills at the 08:31 open), 2
micros, exit at 14:58 CT; the mechanics are in ``_mechanics``. Instrument guard: d-1.
CLV is computed in whole ticks, which is the same ratio as in points without float rounding.
"""

from __future__ import annotations

from collections.abc import Sequence

from strategy.research.h_daily_bar._mechanics import Condition, DailyBar, DailyBarStrategy

LABEL = "H6 prior-close location follow-through"
NAME = "h6_prior_close_location_follow_through"
LOOKBACK = 1
CLV_BUY_AT_OR_ABOVE = 0.8
CLV_SELL_AT_OR_BELOW = 0.2
GUARDED_BARS = 1
ENTRY = "open"


def condition(prior: Sequence[DailyBar]) -> Condition | None:
    """Day d's condition from the complete daily bars of dates before d (oldest first).
    values = (Range[d-1] in ticks, CLV), or (0.0,) when Range[d-1] is 0; side = the entry
    side the CLV selects; None during warm-up."""
    if len(prior) < LOOKBACK:
        return None
    last = prior[-1]
    span = last.range_ticks
    if span <= 0:
        return Condition(holds=False, values=(float(span),))
    clv = (last.close_ticks - last.low_ticks) / span
    if clv >= CLV_BUY_AT_OR_ABOVE:
        side: str | None = "buy"
    elif clv <= CLV_SELL_AT_OR_BELOW:
        side = "sell"
    else:
        side = None
    return Condition(holds=side is not None, values=(float(span), clv), side=side)


class H6PriorCloseLocation(DailyBarStrategy):
    def __init__(self) -> None:
        super().__init__(name=NAME, condition=condition, lookback=LOOKBACK,
                         guarded_bars=GUARDED_BARS, entry=ENTRY)


def factory() -> H6PriorCloseLocation:
    """The registered D.1f factory: no arguments, every parameter a literal above."""
    return H6PriorCloseLocation()
