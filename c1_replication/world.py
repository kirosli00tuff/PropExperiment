"""Test C1's world: the fields of ml_route_v2.phase1.world.Phase1World that the frozen
pipeline.build_world_panel reads, built from the six ext2010 legs and the hist tables.

Call ``build_world`` and ``replication_panel`` INSIDE c1_replication.context.hist_tables (the
training calendar, the decision clock and the signals read the group calendars through it).

- vehicles: ("NG",) only (ruling C8: NG rows only). first / last: 2010-06-07 / 2019-04-30.
- bars: the six legs (NG, NQ, ZN, 6E, GC, ZC) compacted as E.12 compacted them
  (phase1.world.compact_bars: ts_event, OHLC, volume, instrument_id, trade_date); flagged bars
  (in_scheduled_closure, vendor_degraded_day) are kept, as E.12 kept them (counted only).
- CL and MBT (ruling C7): no bar on any NG row's trade date and none closed by any decision time.
  The frozen G17 code (ml_route_v2/signals/generic.py ``_lead``) indexes ``b.ts[0]`` and raises
  IndexError on a frame with no row, so each gets ONE sentinel bar (``C7_SENTINEL``) dated
  2019-05-31, after the window: for every NG row no lead bar is closed by t, which is E.12's
  state for MBT before its listing (G17 "not applicable", value 0). CL is NG's own cluster lead
  and never applicable on NG rows. tests/test_c1_world.py shows the NG-row columns equal those
  of a context with synthetic CL bars (C7's equality test).
- MES: not loaded; the panel's signals are E.12's covered signals, which exclude every MES
  reader (P-1a).
- calendar: synthetic.training_calendar(("NG",), first, last) less the C12-excluded dates; rows
  before the warm-up are dropped by the panel's own missing-statistic rule, as in E.12.
- releases: NG's D8 calendar from the hist release file; costs: the frozen D8
  (targets.frozen_costs); blackout: each leg's roll blackout (the splice date and the two group
  trade dates before it, data.hist_bars), NG's own set joined with the C12-excluded dates, so
  pipeline.own_blackout drops NG's decision rows on them (V2.2's exclude slot).
"""

from __future__ import annotations

import gc
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from types import MappingProxyType
from typing import Any

import numpy as np
import pandas as pd

from c1_replication.constants import (
    EMPTY_ROOTS,
    STORE_ROOTS,
    VEHICLE,
    WINDOW_FIRST,
    WINDOW_LAST,
)

C7_SENTINEL_DAY = date(2019, 5, 31)
C7_SENTINEL_TS_NS = int(pd.Timestamp("2019-05-31 14:00", tz="UTC").value)
FLAG_COLUMNS = ("in_scheduled_closure", "vendor_degraded_day")


class WorldError(RuntimeError):
    """A leg or a table does not fit test C1's world."""


@dataclass(frozen=True)
class ReplicationWorld:
    vehicles: tuple[str, ...]
    first: date
    last: date
    bars_first: date
    calendar: tuple[date, ...]
    bars: Mapping[str, pd.DataFrame]
    frames: Mapping[str, pd.DataFrame]
    releases: Any
    costs: Mapping[str, Any]
    blackout: Mapping[str, frozenset[date]]
    legs: Mapping[str, tuple[str, ...]]
    excluded: frozenset[date] = frozenset()
    roots: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)


def sentinel_frame() -> pd.DataFrame:
    """C7's frame (module docstring): one bar after the window, never read by an NG row."""
    from ml_route_v2.phase1.world import compact_bars

    return compact_bars(pd.DataFrame({
        "ts_event": np.array([C7_SENTINEL_TS_NS], np.int64), "open": [1.0], "high": [1.0],
        "low": [1.0], "close": [1.0], "volume": np.array([1], np.uint32),
        "instrument_id": np.array([0], np.uint32),
        "trade_date": np.array([C7_SENTINEL_DAY.isoformat()], dtype=object)}))


def _leg_record(root: str, leg: Any, first: date, last: date) -> dict[str, Any]:  # noqa: ANN401
    days = tuple(leg.trade_dates)
    if not days:
        raise WorldError(f"{root}: the leg has no trade dates")
    if days[0] < first or days[-1] > last:
        raise WorldError(f"{root}: trade dates {days[0]}..{days[-1]} leave the window "
                         f"{first}..{last}")
    frame = leg.frame
    flags = {c: int(frame[c].to_numpy(bool).sum()) for c in FLAG_COLUMNS if c in frame.columns}
    return {"root": root, "store": getattr(leg, "store", ""), "path": getattr(leg, "path", ""),
            "sha256": getattr(leg, "sha256", ""), "bars": int(len(frame)),
            "trade_dates": len(days), "first_trade_date": days[0].isoformat(),
            "last_trade_date": days[-1].isoformat(),
            "splice_trade_dates": len(tuple(leg.splice_trade_dates)),
            "roll_blackout_dates": len(frozenset(leg.roll_blackout)), "flagged_bars": flags}


def build_world(load: Callable[[str], Any], releases: Any, excluded: Sequence[date], *,  # noqa: ANN401
                first: date = WINDOW_FIRST, last: date = WINDOW_LAST) -> ReplicationWorld:
    """The world (module docstring). ``load(root)`` returns the root's
    data.stage_e_bars.LegFrame; each leg is compacted and released before the next is loaded
    (memory, as phase1.world.load_root does)."""
    from ml_route_v2.phase1.world import compact_bars
    from ml_route_v2.synthetic import training_calendar
    from ml_route_v2.targets import frozen_costs

    records: dict[str, dict[str, Any]] = {}
    bars: dict[str, pd.DataFrame] = {}
    blackout: dict[str, frozenset[date]] = {}
    for root in STORE_ROOTS:
        leg = load(root)
        if getattr(leg, "root", root) != root:
            raise WorldError(f"the loader returned {leg.root}'s leg for {root}")
        records[root] = _leg_record(root, leg, first, last)
        bars[root] = compact_bars(leg.frame)
        blackout[root] = frozenset(leg.roll_blackout)
        del leg
        gc.collect()
    bars.update({r: sentinel_frame() for r in EMPTY_ROOTS})
    excl = frozenset(excluded)
    blackout[VEHICLE] = blackout[VEHICLE] | excl
    blackout.update({r: frozenset() for r in EMPTY_ROOTS})
    calendar = tuple(d for d in training_calendar((VEHICLE,), first, last) if d not in excl)
    if not calendar:
        raise WorldError(f"the NG calendar {first}..{last} is empty")
    bars_first = min(date.fromisoformat(records[r]["first_trade_date"]) for r in STORE_ROOTS)
    return ReplicationWorld(
        vehicles=(VEHICLE,), first=first, last=last, bars_first=bars_first, calendar=calendar,
        bars=MappingProxyType(bars), frames=MappingProxyType({}), releases=releases,
        costs=MappingProxyType(frozen_costs((VEHICLE,))),
        blackout=MappingProxyType(blackout),
        legs=MappingProxyType({VEHICLE: (*STORE_ROOTS, *EMPTY_ROOTS)}), excluded=excl,
        roots=MappingProxyType(records))


def replication_panel(world: ReplicationWorld, signals: Sequence[str]) -> Any:  # noqa: ANN401
    """E.12's call (phase1/build.py _panel_stage): pipeline.build_world_panel(world,
    check_grid=False, signals=<the covered signals>), on the replication world."""
    from ml_route_v2.pipeline import build_world_panel

    return build_world_panel(world, check_grid=False, signals=tuple(signals))


__all__ = ["C7_SENTINEL_DAY", "C7_SENTINEL_TS_NS", "ReplicationWorld", "WorldError",
           "build_world", "replication_panel", "sentinel_frame"]
