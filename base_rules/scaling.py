"""Risk scaling (lead_spec section 3) and H5's trailing scaling (section 4, H5).

Per key (product, leg or tenor), the units the rule would trade, in entry order, each with its
hypothetical GROSS P&L g in dollars per vehicle contract (signed by the rule's direction):
- the first ``WARMUP_UNITS`` units are warm-up: their g enters the history, they are never
  traded or counted;
- every later unit's sigma is the sample standard deviation (ddof 1) of the last
  ``SIGMA_WINDOW`` values of g of units whose EXIT date is strictly before the unit's ENTRY date
  (so every g used is known at the entry decision; for H1 and H4 this is "strictly before the
  entry date"); fewer values: "sigma undefined"; sigma 0: "sigma zero"; neither is traded.
H5: sigma_i,d = sample std of x_i over the ``H5_SIGMA_WINDOW`` grid dates strictly before d.
"""

from __future__ import annotations

import math
from collections import deque
from collections.abc import Sequence
from datetime import date

import numpy as np

from base_rules import constants as K

WARMUP, UNDEFINED, ZERO, TRADED = "warmup", "sigma undefined", "sigma zero", "traded"


def sample_std(values: Sequence[float]) -> float:
    arr = np.asarray(values, dtype=float)
    return float(np.std(arr, ddof=1))


def unit_sigmas(entry: Sequence[date], exit_: Sequence[date], g: Sequence[float], *,
                warmup: int = K.WARMUP_UNITS, window: int = K.SIGMA_WINDOW
                ) -> list[tuple[str, float | None]]:
    """(status, sigma) per unit, units given in entry order (ties keep their order)."""
    n = len(g)
    if not (len(entry) == len(exit_) == n):
        raise ValueError("entry, exit and g differ in length")
    if any(entry[k] > entry[k + 1] for k in range(n - 1)):
        raise ValueError("units must be in entry order")
    by_exit = sorted(range(n), key=lambda j: (exit_[j], entry[j], j))
    hist: deque[float] = deque(maxlen=window)
    p, out = 0, []
    for k in range(n):
        while p < n and exit_[by_exit[p]] < entry[k]:
            hist.append(float(g[by_exit[p]]))
            p += 1
        if k < warmup:
            out.append((WARMUP, None))
            continue
        if len(hist) < window:
            out.append((UNDEFINED, None))
            continue
        sd = sample_std(list(hist))
        if not math.isfinite(sd) or sd <= 0:
            out.append((ZERO, None))
            continue
        out.append((TRADED, sd))
    return out


def trailing_sigma(values: Sequence[float], *, window: int = K.H5_SIGMA_WINDOW
                   ) -> list[float | None]:
    """sigma at position k: sample std of values[k - window:k] (None for k < window)."""
    arr = np.asarray(values, dtype=float)
    out: list[float | None] = []
    for k in range(len(arr)):
        if k < window:
            out.append(None)
            continue
        out.append(float(np.std(arr[k - window:k], ddof=1)))
    return out


__all__ = ["TRADED", "UNDEFINED", "WARMUP", "ZERO", "sample_std", "trailing_sigma",
           "unit_sigmas"]
