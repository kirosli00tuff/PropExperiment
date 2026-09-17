"""The one blessed loader for research-slice MES bars.

Everything in Stages B-D.1 that needs bars goes through ``load_research_bars``.
It returns only trade dates inside the research slice (``data.splits``) and
re-checks the result, so a caller cannot receive a holdout row even if the
file on disk contained one. The file it reads holds research + embargo rows only:
Stage C Task 6 moved the holdout into the encrypted store behind ``data.holdout``,
and this module never touches that store.
"""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd
import pyarrow.dataset as pads

from data.config import PROCESSED_ROOT
from data.splits import EMBARGO_END, HOLDOUT_START, RESEARCH_END, RESEARCH_START

RESEARCH_PARQUET_NAME = "ohlcv-1m_MES_v_0_2025-04-01_2026-06-19_research.parquet"
RESEARCH_SERIES_PATH = PROCESSED_ROOT / "MES" / RESEARCH_PARQUET_NAME


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


def load_research_bars(
    columns: Sequence[str] | None = None, *, include_embargo: bool = False
) -> pd.DataFrame:
    """Research-slice bars in ``ts_event`` order. ``trade_date`` is always included."""
    last = EMBARGO_END if include_embargo else RESEARCH_END
    wanted = None if columns is None else list(dict.fromkeys([*columns, "trade_date"]))
    field = pads.field("trade_date")
    table = pads.dataset(RESEARCH_SERIES_PATH).to_table(
        columns=wanted,
        filter=(field >= RESEARCH_START.isoformat()) & (field <= last.isoformat()),
    )
    frame = table.to_pandas()
    assert_no_holdout_rows(frame)
    if "ts_event" in frame.columns and not frame["ts_event"].is_monotonic_increasing:
        raise ValueError("research bars are not in ts_event order")
    return frame.reset_index(drop=True)
