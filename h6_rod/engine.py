"""H6 through the frozen engine, unchanged (prereg section 3): screening.stage_e_engine.run_engine
with screening.stage_e_rules.StageERules on MNQ, the vehicle, fed the NQ price path's bars as read
(MNQ and NQ quote the same index on the same 0.25 grid; prereg section 2).

Every fill, cost and refusal is the engine's: D8 MNQ costs per 30-minute bucket and the event
window (screening.stage_e_frozen, the frozen D8 table), D9.5a, D9.12, D9.7 with its prior-settlement
proxy and locked fills, the 2-minute hold, the XFA 50K gate, the trailing MLL with restart on a
terminal account, and the roll-blackout refusal. The roll-blackout set is the one the v2 engine
stage uses for MNQ (ml_route_v2.pipeline.own_blackout over {price path: its L-8 blackout}: the
vehicle's own store is not read, E.12 lead rule P-1, so MNQ's set is NQ's). The window dates passed
to the engine are the window's equity trade dates; the frame holds the bars of the lead-in dates
(constants.ENGINE_LEAD_IN_DATES; no entry is possible there: they are not window dates and carry no
schedule) and of the window.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from typing import Any

import pandas as pd

from h6_rod import constants as K
from h6_rod.member import H6Member
from h6_rod.signal import Schedule


@dataclass(frozen=True)
class EngineRun:
    """One test on one window through the engine."""

    test: str
    window: tuple[date, date]
    window_dates: tuple[date, ...]
    lead_in: tuple[date, ...]
    result: Any  # screening.stage_e_engine.EngineResult
    rules: Any  # the StageERules instance (price_ticks, tick_value)


def vehicle_blackout(price_path_blackout: frozenset[date]) -> frozenset[date]:
    """MNQ's own roll-blackout dates as the v2 engine stage builds them (module docstring)."""
    from ml_route_v2.pipeline import own_blackout

    return frozenset(own_blackout({K.PRICE_ROOT: frozenset(price_path_blackout)},
                                  (K.VEHICLE,))[K.VEHICLE])


def make_rules(window_dates: Sequence[date], blackout: frozenset[date], releases: Any) -> Any:
    from screening.stage_e_frozen import leg_inputs
    from screening.stage_e_rules import StageERules

    return StageERules({K.VEHICLE: leg_inputs(K.VEHICLE, traded=True)},
                       frozenset(window_dates), frozenset(blackout), releases)


def frame_for(bars: pd.DataFrame, dates: Sequence[date]) -> pd.DataFrame:
    """The bars of ``dates`` (data.stage_e_bars.restrict's rule on a frame)."""
    wanted = {d.isoformat() for d in dates}
    mask = bars["trade_date"].astype(str).isin(wanted).to_numpy()
    return bars[mask].reset_index(drop=True)


def run_schedule(bars: pd.DataFrame, schedule: Schedule, window_dates: Sequence[date],
                 lead_in: Sequence[date], blackout: frozenset[date], releases: Any) -> EngineRun:
    """One engine run of ``schedule`` (its window's dates, plus the lead-in's bars)."""
    from screening.stage_e_engine import run_engine
    from strategy.stage_e.interface import LegSpec

    rules = make_rules(window_dates, blackout, releases)
    frame = frame_for(bars, (*lead_in, *window_dates))
    member = H6Member(dict(schedule.entries), test=schedule.test)
    result = run_engine({K.VEHICLE: frame}, member, (LegSpec(K.VEHICLE, True),), rules)
    return EngineRun(schedule.test, schedule.window, tuple(window_dates), tuple(lead_in),
                     result, rules)


def run_tests(bars: pd.DataFrame, schedules: Mapping[str, Schedule],
              window_dates: Sequence[date], lead_in: Sequence[date],
              blackout: frozenset[date], releases: Any) -> dict[str, EngineRun | Exception]:
    """Every test's run; a run the engine cannot complete (EngineInvariantError,
    EngineRefusedCase) is kept as its exception, so the caller reports that test STOPPED."""
    from screening.stage_e_engine import EngineInvariantError, EngineRefusedCase

    out: dict[str, EngineRun | Exception] = {}
    for test, sched in schedules.items():
        try:
            out[test] = run_schedule(bars, sched, window_dates, lead_in, blackout, releases)
        except (EngineInvariantError, EngineRefusedCase) as exc:
            out[test] = exc
    return out


__all__ = ["EngineRun", "frame_for", "make_rules", "run_schedule", "run_tests",
           "vehicle_blackout"]
