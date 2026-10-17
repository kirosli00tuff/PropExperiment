"""Power before any outcome read (lead_spec section 5, P2.3). Inputs: trigger events, the
calendars and mark existence (a ``MarkSource``); no price, mark value or forward return.

- units per window: trigger_hold.units.build_units (entry and exit eligibility by mark existence
  and the calendar).
- non-overlapping events: greedy in entry order; a unit counts when its entry mark date is on or
  after the previous COUNTED unit's exit mark date.
- n_dates: the book's series dates (the window's mark dates from the first unit's entry mark
  date on: section 5 addition (a)). In-market fraction: the share of them with net != 0
  (addition (c)). E[t] = 0.5 x sqrt(n_dates / 252);
  power_gate = 1 - Phi(2.0 - E[t]); power_holm1 = 1 - Phi(max(2.0, z_{1 - 0.05/K}) - E[t]).
- Inconclusive by design: fewer than 30 non-overlapping events or power_gate < 0.2.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

from trigger_hold import constants as K
from trigger_hold.types import TriggerEvent
from trigger_hold.units import (
    MarkSource,
    Unit,
    Window,
    book_days,
    build_units,
    in_market_fraction,
)


def _phi(x: float) -> float:
    return 0.5 * math.erfc(-x / math.sqrt(2.0))


def _z(q: float) -> float:
    from scipy.stats import norm

    return float(norm.ppf(q))


def nonoverlapping(units: Sequence[Unit]) -> int:
    count, last_exit = 0, None
    for un in sorted(units, key=lambda u: (u.d_e, u.d_x)):
        if last_exit is None or un.d_e >= last_exit:
            count += 1
            last_exit = un.d_x
    return count


def expected_t(n_dates: int, true_sharpe: float = K.POWER_TRUE_SHARPE) -> float:
    return true_sharpe * math.sqrt(n_dates / K.SHARPE_ANNUALIZATION)


def power_at(hurdle: float, n_dates: int) -> float:
    return 1.0 - _phi(hurdle - expected_t(n_dates))


def power_gate(n_dates: int) -> float:
    return power_at(K.T_BAR, n_dates)


def power_holm1(n_dates: int, k_family: int) -> float:
    return power_at(max(K.T_BAR, _z(1.0 - K.HOLM_ALPHA / k_family)), n_dates)


def inconclusive(nonoverlap: int, gate: float) -> bool:
    return nonoverlap < K.MIN_NONOVERLAP or gate < K.POWER_MIN


def power_row(src: MarkSource, events: Sequence[TriggerEvent], window: Window, *, m: int,
              h: int, k_family: int) -> dict[str, Any]:
    units, counts = build_units(src, events, window, m=m, h=h)
    days = book_days(src, window, units)
    n_dates = len(days)
    non = nonoverlapping(units)
    gate = power_gate(n_dates)
    return {"window": window.name, "first": str(window.first), "last": str(window.last),
            "h": h, "m": m, "events": len(events), "units": len(units),
            "nonoverlapping": non, "n_dates": n_dates,
            "first_book_date": str(days[0]) if days else None,
            "in_market_fraction": in_market_fraction(units, days),
            "expected_t": expected_t(n_dates),
            "power_gate": gate, "power_holm1": power_holm1(n_dates, k_family),
            "k_family": k_family, "inconclusive_by_design": inconclusive(non, gate),
            "unit_counts": dict(sorted(counts.items()))}


__all__ = ["expected_t", "inconclusive", "nonoverlapping", "power_at", "power_gate",
           "power_holm1", "power_row"]
