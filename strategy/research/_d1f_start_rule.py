"""Stage D.1f step 5: the start rule of docs/NULL_CRITERIA.md 4.1, exactly as written.

- V_ref: for each of the 14 calendar months 2025-04 .. 2026-05, the median volume over that
  month's RTH one-minute bars PRESENT in the research parquet (CT clock time 08:30 to 14:59; a
  missing minute contributes nothing; every trade date, no exclusion); V_ref = the median of
  the 14 monthly medians.
- V_M: the same monthly median for each month 2019-05 .. 2024-02 over the confirmation
  parquet's RTH bars present (after step 4's drop of trade dates after 2024-02-29).
- S = the first trade date with bars of the earliest month M* such that V_M >= 0.25 x V_ref for
  M* and every later month through 2024-02. No qualifying month: the window is empty and D.1f
  stops with that finding (D-1). Sensitivity at 0.15 and 0.40: reported, descriptive.

A month is keyed by its trade date's calendar month. An RTH bar's CT date is its trade date,
so this is also the CT calendar month. A month of the extension with no RTH bar has no V_M
and cannot qualify (it is logged as null); "the first trade date with bars" of M* counts a
bar of any session. If M* = 2019-05 and that date is not 2019-05-06 (the date 4.1 states), the
rule raises: the data contradict the frozen text and the lead decides.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date

import numpy as np
import pandas as pd

from sim.costs import CT

RTH_FIRST_MINUTE_CT = 8 * 60 + 30  # 08:30
RTH_LAST_MINUTE_CT = 14 * 60 + 59  # 14:59
REFERENCE_MONTHS = tuple(f"{y}-{m:02d}" for y, m in
                         [(2025, m) for m in range(4, 13)] + [(2026, m) for m in range(1, 6)])
EXTENSION_MONTHS = tuple(f"{y}-{m:02d}" for y in range(2019, 2025) for m in range(1, 13)
                         if (2019, 5) <= (y, m) <= (2024, 2))
MES_FIRST_TRADE_DATE = date(2019, 5, 6)  # "if M* = 2019-05, S = 2019-05-06" (4.1)
BINDING_FRACTION = 0.25
SENSITIVITY_FRACTIONS = (0.15, 0.40)
COLUMNS = ("ts_event", "volume", "trade_date")


def _months(frame: pd.DataFrame) -> pd.Series:
    return frame["trade_date"].astype(str).str.slice(0, 7)


def rth_monthly_median_volume(frame: pd.DataFrame) -> dict[str, float]:
    """Per trade-date month, the median volume of the bars whose CT clock minute is in
    [08:30, 14:59]."""
    missing = [c for c in COLUMNS if c not in frame.columns]
    if missing:
        raise ValueError(f"bars missing columns {missing}")
    local = pd.to_datetime(frame["ts_event"].to_numpy(np.int64), utc=True).tz_convert(CT)
    minute = np.asarray(local.hour * 60 + local.minute)
    rth = frame[(minute >= RTH_FIRST_MINUTE_CT) & (minute <= RTH_LAST_MINUTE_CT)]
    medians = rth["volume"].astype(float).groupby(_months(rth)).median()
    return {str(k): float(v) for k, v in medians.items()}


def first_trade_date_by_month(frame: pd.DataFrame) -> dict[str, date]:
    """The first trade date with bars (any session) of each month."""
    days = sorted({date.fromisoformat(str(d)) for d in frame["trade_date"].unique()})
    out: dict[str, date] = {}
    for d in days:
        out.setdefault(f"{d.year}-{d.month:02d}", d)
    return out


def reference_volume(research_medians: Mapping[str, float]) -> float:
    missing = [m for m in REFERENCE_MONTHS if m not in research_medians]
    if missing:
        raise ValueError(f"V_ref needs all 14 months 2025-04..2026-05; missing {missing}")
    return float(np.median([research_medians[m] for m in REFERENCE_MONTHS]))


def start_month(extension_medians: Mapping[str, float], v_ref: float, fraction: float,
                months: Sequence[str] = EXTENSION_MONTHS) -> str | None:
    """The earliest month M* with V_M >= fraction x V_ref for M* and every later month; None
    when the last month itself fails (or has no V_M)."""
    bar = fraction * v_ref
    earliest = None
    for month in reversed(months):
        value = extension_medians.get(month)
        if value is None or not value >= bar:
            break
        earliest = month
    return earliest


def start_rule(research_medians: Mapping[str, float], extension_medians: Mapping[str, float],
               first_dates: Mapping[str, date]) -> dict:
    """The whole rule and its sensitivity; S is None when no month qualifies (stop, D-1)."""
    v_ref = reference_volume(research_medians)

    def s_at(fraction: float) -> dict:
        month = start_month(extension_medians, v_ref, fraction)
        s = None if month is None else first_dates.get(month)
        if month is not None and s is None:
            raise ValueError(f"month {month} qualifies but has no trade date with bars")
        if month == EXTENSION_MONTHS[0] and s != MES_FIRST_TRADE_DATE:
            raise ValueError(f"M* = {month} but its first trade date with bars is {s}, not the "
                             f"{MES_FIRST_TRADE_DATE} NULL_CRITERIA 4.1 states: stop for the lead")
        return {"fraction": fraction, "threshold": fraction * v_ref, "m_star": month,
                "s": None if s is None else s.isoformat()}

    binding = s_at(BINDING_FRACTION)
    return {
        "rule": "docs/NULL_CRITERIA.md 4.1",
        "reference_months": list(REFERENCE_MONTHS),
        "reference_monthly_medians": {m: research_medians[m] for m in REFERENCE_MONTHS},
        "v_ref": v_ref,
        "extension_monthly_medians": {m: extension_medians.get(m) for m in EXTENSION_MONTHS},
        "extension_first_trade_dates": {m: (str(first_dates[m]) if m in first_dates else None)
                                        for m in EXTENSION_MONTHS},
        "binding": binding,
        "sensitivity": [s_at(f) for f in SENSITIVITY_FRACTIONS],
        "S": binding["s"],
        "empty_window": binding["s"] is None,
    }
