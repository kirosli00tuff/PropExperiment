"""The blessed loaders for MES bars: the research slice and (Stage D.1f) the confirmation window.

Everything in Stages B-D.1 that needs bars goes through ``load_research_bars``.
It returns only trade dates inside the research slice (``data.splits``) and
re-checks the result, so a caller cannot receive a holdout row even if the
file on disk contained one. The file it reads holds research + embargo rows only:
Stage C Task 6 moved the holdout into the encrypted store behind ``data.holdout``,
and this module never touches that store.

Stage D.1f adds ``load_confirmation_bars`` with the same semantics for the confirmation
parquet (reports/stage_d1f_confirmation_list.md 1.3, 5.1, 5.2(iv)): it filters to
2019-05-01..2024-02-29 and then re-checks every returned row, refusing holdout-1,
holdout-2, embargo-2 and mined (research-slice, research-embargo) dates. The research path
now also refuses holdout-2, embargo-2 and confirmation dates. Both re-checks classify each
trade date with ``trade_date_class``; ``funnel.null_generator`` uses the same classes (R-3).
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import pyarrow.dataset as pads

from data.config import PROCESSED_ROOT
from data.splits import EMBARGO_END, HOLDOUT_START, RESEARCH_END, RESEARCH_START

RESEARCH_PARQUET_NAME = "ohlcv-1m_MES_v_0_2025-04-01_2026-06-19_research.parquet"
RESEARCH_SERIES_PATH = PROCESSED_ROOT / "MES" / RESEARCH_PARQUET_NAME

# ---- Stage D.1f date classes (reports/stage_d1f_confirmation_list.md sections 1.2, 1.3) ----
# CME trade dates, inclusive bounds. The confirmation window runs from the start rule's S
# (docs/NULL_CRITERIA.md 4.1, computed in the run session) through CONFIRMATION_LAST_TRADE_DATE;
# CONFIRMATION_EARLIEST_TRADE_DATE is the first date any bar can exist (MES's first month).
CONFIRMATION_EARLIEST_TRADE_DATE = date(2019, 5, 1)
CONFIRMATION_LAST_TRADE_DATE = date(2024, 2, 29)
EMBARGO2_START = date(2024, 3, 1)  # March 2024: inside a sealed chunk, never built into bars
EMBARGO2_END = date(2024, 3, 31)
HOLDOUT2_START = date(2024, 4, 1)
HOLDOUT2_END = date(2025, 3, 31)
# The 13 whole monthly raw chunks sealed as holdout-2, oldest first ([start, end) UTC dates,
# the data.pull_mes.monthly_chunks spelling).
HOLDOUT2_RAW_CHUNKS: tuple[tuple[str, str], ...] = tuple(
    (f"{y}-{m:02d}-01", f"{y + (m == 12)}-{m % 12 + 1:02d}-01")
    for y, m in [(2024, m) for m in range(3, 13)] + [(2025, m) for m in range(1, 4)]
)
# The unsealed chunks the confirmation parquet is built from: 2019-05 .. 2024-02.
CONFIRMATION_RAW_CHUNKS: tuple[tuple[str, str], ...] = tuple(
    (f"{y}-{m:02d}-01", f"{y + (m == 12)}-{m % 12 + 1:02d}-01")
    for y in range(2019, 2025) for m in range(1, 13)
    if (2019, 5) <= (y, m) <= (2024, 2)
)
CONFIRMATION_PARQUET_NAME = "ohlcv-1m_MES_v_0_2019-05-01_2024-02-29_confirmation.parquet"
CONFIRMATION_SERIES_PATH = PROCESSED_ROOT / "MES" / CONFIRMATION_PARQUET_NAME


class HoldoutLeakError(RuntimeError):
    """A holdout-slice row reached a research code path. Never caught and ignored."""


def assert_no_holdout_rows(frame: pd.DataFrame) -> None:
    if "trade_date" not in frame.columns:
        raise HoldoutLeakError("cannot verify slice membership without a trade_date column")
    if len(frame) and str(frame["trade_date"].max()) >= HOLDOUT_START.isoformat():
        raise HoldoutLeakError(
            f"holdout trade date {frame['trade_date'].max()} reached a research code path "
            f"(holdout starts {HOLDOUT_START})"
        )


# ---- Stage D.1f Task 1: trade-date classes and the refusals built on them (R-3) ----
CONFIRMATION = "confirmation"
EMBARGO2 = "embargo-2"
HOLDOUT2 = "holdout-2"
RESEARCH = "research"  # the mined slice: train union, test folds and EDA dates all live here
RESEARCH_EMBARGO = "research embargo"
HOLDOUT1 = "holdout-1"
BEFORE_MES = "before MES"
# Inclusive CME trade-date bounds per class, oldest first. Together they cover every date
# from CONFIRMATION_EARLIEST_TRADE_DATE on with no gap and no overlap (a test pins that).
DATE_CLASSES: tuple[tuple[str, date, date], ...] = (
    (CONFIRMATION, CONFIRMATION_EARLIEST_TRADE_DATE, CONFIRMATION_LAST_TRADE_DATE),
    (EMBARGO2, EMBARGO2_START, EMBARGO2_END),
    (HOLDOUT2, HOLDOUT2_START, HOLDOUT2_END),
    (RESEARCH, RESEARCH_START, RESEARCH_END),
    (RESEARCH_EMBARGO, RESEARCH_END + timedelta(days=1), HOLDOUT_START - timedelta(days=1)),
    (HOLDOUT1, HOLDOUT_START, date.max),
)
# The order refusals are reported in: the most serious class first.
_REFUSAL_ORDER = (HOLDOUT1, HOLDOUT2, EMBARGO2, RESEARCH_EMBARGO, RESEARCH, CONFIRMATION,
                  BEFORE_MES)
_CLASS_WORDING = {
    HOLDOUT1: "holdout-1 (sealed, 2026-06-22 on)",
    HOLDOUT2: "holdout-2 (sealed, 2024-04-01..2025-03-31)",
    EMBARGO2: "embargo-2 (March 2024, in a sealed chunk)",
    RESEARCH_EMBARGO: "research-embargo (mined data, 2026-06-13..2026-06-21)",
    RESEARCH: "mined research-slice (train union, test folds, EDA; 2025-04-01..2026-06-12)",
    CONFIRMATION: "confirmation-window (2019-05-01..2024-02-29)",
    BEFORE_MES: "pre-MES (before 2019-05-01)",
}


def trade_date_class(day: date) -> str:
    """The slice a CME trade date belongs to: one of the ``DATE_CLASSES`` names, or
    ``BEFORE_MES`` for a date before any MES bar can exist."""
    for name, first, last in DATE_CLASSES:
        if first <= day <= last:
            return name
    return BEFORE_MES


def _frame_trade_dates(frame: pd.DataFrame) -> list[date]:
    if "trade_date" not in frame.columns:
        raise HoldoutLeakError("cannot verify slice membership without a trade_date column")
    return sorted({date.fromisoformat(str(d)) for d in frame["trade_date"].unique()})


def refuse_dates_outside(days: Iterable[date], allowed: frozenset[str], where: str) -> None:
    """Raise ``HoldoutLeakError`` naming the most serious class among ``days`` that is not in
    ``allowed`` (holdout-1 first, then holdout-2, embargo-2, the mined data, ...)."""
    by_class: dict[str, list[date]] = {}
    for day in sorted(set(days)):
        by_class.setdefault(trade_date_class(day), []).append(day)
    for name in _REFUSAL_ORDER:
        if name in by_class and name not in allowed:
            found = by_class[name]
            raise HoldoutLeakError(
                f"{_CLASS_WORDING[name]} trade date {found[0]} reached the {where} "
                f"({len(found)} such dates); refused")


def refuse_non_confirmation_dates(days: Iterable[date], where: str) -> None:
    """Every date must be a confirmation-window date (2019-05-01..2024-02-29): refuses
    holdout-1, holdout-2, embargo-2 and every mined date (the train union included)."""
    days = sorted(set(days))
    refuse_dates_outside(days, frozenset({CONFIRMATION}), where)
    if days and days[-1] > CONFIRMATION_LAST_TRADE_DATE:  # the list's 5.2(iv) assertion
        raise HoldoutLeakError(f"max trade date {days[-1]} > {CONFIRMATION_LAST_TRADE_DATE} "
                               f"on the {where}")


def assert_confirmation_rows(frame: pd.DataFrame) -> None:
    """The confirmation loader's re-check: max(trade_date) <= 2024-02-29 and no row of a
    holdout-1, holdout-2, embargo-2 or mined date."""
    refuse_non_confirmation_dates(_frame_trade_dates(frame), "confirmation path")


def assert_research_slice_rows(frame: pd.DataFrame, *, include_embargo: bool = False) -> None:
    """The research loader's re-check: ``assert_no_holdout_rows`` (unchanged) plus, in depth,
    no holdout-2, embargo-2 or confirmation-window row (the research parquet has none)."""
    assert_no_holdout_rows(frame)
    allowed = {RESEARCH, RESEARCH_EMBARGO} if include_embargo else {RESEARCH}
    refuse_dates_outside(_frame_trade_dates(frame), frozenset(allowed), "research path")


def _read_trade_date_range(path: Path, columns: Sequence[str] | None, first: date,
                           last: date) -> pd.DataFrame:
    """Rows of ``path`` whose stored ISO ``trade_date`` is in [first, last]. The callers
    re-check whatever comes back, so this pushdown filter is never the only guard."""
    wanted = None if columns is None else list(dict.fromkeys([*columns, "trade_date"]))
    field = pads.field("trade_date")
    table = pads.dataset(path).to_table(
        columns=wanted,
        filter=(field >= first.isoformat()) & (field <= last.isoformat()),
    )
    return table.to_pandas()


def load_research_bars(
    columns: Sequence[str] | None = None, *, include_embargo: bool = False
) -> pd.DataFrame:
    """Research-slice bars in ``ts_event`` order. ``trade_date`` is always included."""
    last = EMBARGO_END if include_embargo else RESEARCH_END
    frame = _read_trade_date_range(RESEARCH_SERIES_PATH, columns, RESEARCH_START, last)
    assert_research_slice_rows(frame, include_embargo=include_embargo)
    if "ts_event" in frame.columns and not frame["ts_event"].is_monotonic_increasing:
        raise ValueError("research bars are not in ts_event order")
    return frame.reset_index(drop=True)


def load_confirmation_bars(
    columns: Sequence[str] | None = None, *, path: Path = CONFIRMATION_SERIES_PATH
) -> pd.DataFrame:
    """Confirmation-window bars (2019-05-01..2024-02-29) in ``ts_event`` order, with the same
    refusal semantics as ``load_research_bars``: filter, then re-check every returned row.
    ``trade_date`` is always included. The window's start S is the caller's business
    (``screening.runner.confirmation_window``)."""
    frame = _read_trade_date_range(Path(path), columns, CONFIRMATION_EARLIEST_TRADE_DATE,
                                   CONFIRMATION_LAST_TRADE_DATE)
    assert_confirmation_rows(frame)
    if "ts_event" in frame.columns and not frame["ts_event"].is_monotonic_increasing:
        raise ValueError("confirmation bars are not in ts_event order")
    return frame.reset_index(drop=True)
