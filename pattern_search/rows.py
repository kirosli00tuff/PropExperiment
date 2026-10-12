"""Decision rows: the frozen V2.2 rows plus t4 = F_X - 60 min (reports/stage_e20_plan.md section 4;
F6 addition 1).

- t1, t2, t3: ml_route_v2.clock.decision_rows on each vehicle's bar trade dates with each
  vehicle's own roll-blackout dates excluded (pipeline.own_blackout), exactly as the frozen
  pipeline.build_world_panel calls it; its exclusions stay as frozen (non-trade dates,
  early-halt dates, early-close dates, own blackout).
- t4: one row per (vehicle, trade date) the frozen clock kept, at flatten_ts_ns - 60 min, with
  t_index 4 and the identifier columns copied (codemap_clock Q1). On kept dates F_X is the
  group's regular F, so t4 is 14:08 CT for equity, rates, FX, energy and gold, 12:18 for grains
  and 12:03 for livestock (checked here against rules.sessions.REGULAR_FLATTEN_CT minus 60).
- The frame keeps the frozen ROW_COLUMNS, dtypes and sort ((decision_ts_ns, root), mergesort).
clock.py is not edited.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from pattern_search import constants as K
from pattern_search import guard  # noqa: F401  (F3)

NS_MIN = 60_000_000_000


class RowsError(RuntimeError):
    """The t4 rows break the plan's rule."""


def frozen_rows(world: Any) -> pd.DataFrame:
    """The frozen t1-t3 rows of the world's vehicles (build_world_panel's call)."""
    from ml_route_v2.clock import decision_rows, trade_dates_of
    from ml_route_v2.constants import UNIVERSE
    from ml_route_v2.pipeline import own_blackout

    vs = tuple(world.vehicles)
    return decision_rows(vs, {v: trade_dates_of(world.bars[UNIVERSE[v][1]]) for v in vs},
                         exclude=own_blackout(world.blackout, vs))


def _expected_t4_minute(group: str) -> int:
    from ml_route_v2.clock import _minutes, _regular_flatten

    return _minutes(_regular_flatten(group)) - K.T4_MINUTES_BEFORE_F


def t4_rows(rows: pd.DataFrame) -> pd.DataFrame:
    """One t4 row per (vehicle, trade date) of ``rows`` (rows of t_index 1..3 only)."""
    from ml_route_v2.clock import ROW_COLUMNS, minutes_after_midnight_ct

    if len(rows) and int(rows["t_index"].max()) > 3:
        raise RowsError("t4_rows takes the frozen t1-t3 rows")
    first = rows.loc[~rows.duplicated(["root", "trade_date"], keep="first"), list(ROW_COLUMNS)]
    out = first.copy()
    out["t_index"] = np.int8(K.T4_INDEX)
    out["decision_ts_ns"] = (out["flatten_ts_ns"].to_numpy(np.int64)
                             - K.T4_MINUTES_BEFORE_F * NS_MIN)
    if len(out):
        got = minutes_after_midnight_ct(out["decision_ts_ns"].to_numpy(np.int64))
        want = np.asarray([_expected_t4_minute(g) for g in out["group"]], dtype=np.int64)
        if not np.array_equal(got, want):
            raise RowsError(f"{int((got != want).sum())} t4 rows are not at the regular F - 60")
        last = rows.groupby(["root", "trade_date"], sort=False)["decision_ts_ns"].max()
        key = pd.MultiIndex.from_frame(out[["root", "trade_date"]])
        if not bool((out["decision_ts_ns"].to_numpy() > last.reindex(key).to_numpy()).all()):
            raise RowsError("a t4 row is not later than its date's t3")
    return out


def with_t4(rows: pd.DataFrame) -> pd.DataFrame:
    """The frozen rows plus their t4 rows, in the frozen sort and dtypes."""
    from ml_route_v2.clock import ROW_COLUMNS

    frame = pd.concat([rows[list(ROW_COLUMNS)], t4_rows(rows)], ignore_index=True)
    frame["t_index"] = frame["t_index"].astype(np.int8)
    for col in ("decision_ts_ns", "flatten_ts_ns"):
        frame[col] = frame[col].astype(np.int64)
    frame["trade_date"] = pd.to_datetime(frame["trade_date"]).astype("datetime64[ns]")
    frame = frame.sort_values(["decision_ts_ns", "root"], kind="mergesort")
    return frame.reset_index(drop=True)


def search_rows(world: Any) -> pd.DataFrame:
    """The search's decision rows: the frozen t1-t3 rows and t4 (module docstring)."""
    return with_t4(frozen_rows(world))


__all__ = ["RowsError", "frozen_rows", "search_rows", "t4_rows", "with_t4"]
