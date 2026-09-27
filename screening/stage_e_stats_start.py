"""Stage E D4 start rule per exposure (docs/NULL_CRITERIA.md 4.1 generalized); reads no bars.

docs/STAGE_E_DESIGN.md D4 and docs/NULL_CRITERIA_E.md 4:
- V_ref,X = the median of the 14 monthly medians (2025-04..2026-05) of the vehicle's day-session
  one-minute volume over the bars present (contracts per one-minute bar);
- S_X = the first trade date with bars of the earliest month M* such that every month from M*
  through 2024-02 has a median day-session one-minute volume >= 0.25 V_ref,X;
- 0.15 and 0.40: the same rule, descriptive only;
- the earliest possible S_X is the first trade date with bars on or after 2019-05-06.

Inputs are computed elsewhere (the runner, from the vehicle's bars; or from the full-size
contract's bars where E.2 declares them as the price path): the monthly medians keyed "YYYY-MM"
by trade-date month, and the first trade date with bars (any session) of each month.
A month with no day-session bar has no median (omit it or pass None) and cannot qualify.
No qualifying month (2024-02 itself fails): S_X is None and the window is empty.
Strict inputs: a reference month missing or extra, an extension month outside 2019-05..2024-02, a
non-finite or negative median, a first date outside its month or a 2019-05 date before
2019-05-06 all raise.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date

import numpy as np

BINDING_FRACTION = 0.25
SENSITIVITY_FRACTIONS = (0.15, 0.40)
REFERENCE_MONTHS = tuple(
    f"{y}-{m:02d}" for y, m in [(2025, m) for m in range(4, 13)] + [(2026, m) for m in range(1, 6)]
)
EXTENSION_MONTHS = tuple(
    f"{y}-{m:02d}"
    for y in range(2019, 2025)
    for m in range(1, 13)
    if (2019, 5) <= (y, m) <= (2024, 2)
)
EARLIEST_START = date(2019, 5, 6)
LAST_CONFIRMATION_DATE = date(2024, 2, 29)


@dataclass(frozen=True)
class StartAt:
    fraction: float
    threshold: float  # fraction x V_ref, contracts per one-minute bar
    m_star: str | None  # earliest qualifying month, "YYYY-MM"; None: no month qualifies
    s: date | None  # first trade date with bars of m_star


@dataclass(frozen=True)
class StartRule:
    vehicle: str
    v_ref: float  # contracts per one-minute day-session bar
    reference_monthly_medians: tuple[tuple[str, float], ...]
    extension_monthly_medians: tuple[tuple[str, float | None], ...]
    binding: StartAt  # at 0.25
    sensitivity: tuple[StartAt, StartAt]  # 0.15 and 0.40, descriptive
    s_x: date | None
    empty_window: bool


def _month_key(day: date) -> str:
    return f"{day.year}-{day.month:02d}"


def _checked_median(month: str, value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"median volume of {month} must be finite and >= 0, got {value!r}")
    value = float(value)
    if not (math.isfinite(value) and value >= 0.0):
        raise ValueError(f"median volume of {month} must be finite and >= 0, got {value!r}")
    return value


def reference_volume(reference_medians: Mapping[str, float]) -> float:
    """V_ref: the median of the 14 reference monthly medians; exactly those 14 months."""
    extra = sorted(set(reference_medians) - set(REFERENCE_MONTHS))
    if extra:
        raise ValueError(f"reference months outside 2025-04..2026-05: {extra}")
    missing = [m for m in REFERENCE_MONTHS if m not in reference_medians]
    if missing:
        raise ValueError(f"V_ref needs all 14 months 2025-04..2026-05; missing {missing}")
    values = [_checked_median(m, reference_medians[m]) for m in REFERENCE_MONTHS]
    v_ref = float(np.median(values))
    if v_ref <= 0.0:
        raise ValueError("V_ref = 0: every month would qualify; the reference volumes are wrong")
    return v_ref


def _checked_extension(extension_medians: Mapping[str, float | None]) -> dict[str, float | None]:
    extra = sorted(set(extension_medians) - set(EXTENSION_MONTHS))
    if extra:
        raise ValueError(f"extension months outside 2019-05..2024-02: {extra}")
    return {
        m: (None if extension_medians.get(m) is None else _checked_median(m, extension_medians[m]))
        for m in EXTENSION_MONTHS
    }


def _checked_first_dates(first_trade_dates: Mapping[str, date]) -> dict[str, date]:
    for month, day in first_trade_dates.items():
        if _month_key(day) != month:
            raise ValueError(f"first trade date {day} of {month} is not in its month")
        if day < EARLIEST_START:
            raise ValueError(f"first trade date {day} of {month} is before 2019-05-06, the "
                             "earliest possible S_X")
        if day > LAST_CONFIRMATION_DATE:
            raise ValueError(f"first trade date {day} of {month} is after 2024-02-29")
    return dict(first_trade_dates)


def start_month(extension: Mapping[str, float | None], v_ref: float, fraction: float) -> str | None:
    """The earliest month M* with V_M >= fraction x V_ref for M* and every later month."""
    bar = fraction * v_ref
    earliest = None
    for month in reversed(EXTENSION_MONTHS):
        value = extension.get(month)
        if value is None or not value >= bar:
            break
        earliest = month
    return earliest


def first_trade_dates_by_month(trade_dates: Iterable[date]) -> dict[str, date]:
    """The first trade date with bars of each month, dates before 2019-05-06 dropped.

    A trade date after 2024-02-29 (embargo or holdout) raises: it must never reach this rule.
    """
    out: dict[str, date] = {}
    for day in sorted(set(trade_dates)):
        if day > LAST_CONFIRMATION_DATE:
            raise ValueError(f"trade date {day} is after 2024-02-29, outside the confirmation "
                             "extension")
        if day < EARLIEST_START:
            continue
        out.setdefault(_month_key(day), day)
    return out


def start_rule(
    vehicle: str,
    reference_medians: Mapping[str, float],
    extension_medians: Mapping[str, float | None],
    first_trade_dates: Mapping[str, date],
) -> StartRule:
    """The D4 start rule of one vehicle and its descriptive sensitivity."""
    v_ref = reference_volume(reference_medians)
    extension = _checked_extension(extension_medians)
    first = _checked_first_dates(first_trade_dates)

    def s_at(fraction: float) -> StartAt:
        month = start_month(extension, v_ref, fraction)
        s = None if month is None else first.get(month)
        if month is not None and s is None:
            raise ValueError(f"{vehicle}: month {month} qualifies but has no trade date with bars")
        return StartAt(fraction=fraction, threshold=fraction * v_ref, m_star=month, s=s)

    binding = s_at(BINDING_FRACTION)
    sensitivity = (s_at(SENSITIVITY_FRACTIONS[0]), s_at(SENSITIVITY_FRACTIONS[1]))
    return StartRule(
        vehicle=vehicle,
        v_ref=v_ref,
        reference_monthly_medians=tuple(
            (m, float(reference_medians[m])) for m in REFERENCE_MONTHS
        ),
        extension_monthly_medians=tuple((m, extension[m]) for m in EXTENSION_MONTHS),
        binding=binding,
        sensitivity=sensitivity,
        s_x=binding.s,
        empty_window=binding.s is None,
    )
