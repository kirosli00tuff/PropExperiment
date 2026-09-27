"""Stage E statistics: the one unit, the frozen epsilon lookup and the member daily series.

Unit. Every series and every epsilon in screening/stage_e_stats*.py is in NET TICKS PER CONTRACT
PER DAY OF THE VEHICLE ("ticks/ct/day"), the unit of eps_X in reports/stage_e2a_epsilon.json
(``eps_operative``; docs/STAGE_E_DESIGN.md D3, docs/NULL_CRITERIA_E.md 2 and 3):
- a single-vehicle member: each round trip's net P&L divided by its OWN contract quantity and by
  the vehicle's tick value, summed per window date, 0.0 on a window date without a trip
  (NULL_CRITERIA_E 3, the R-1 lesson of D.1e);
- a multi-leg member: its combined net dollars per day at its frozen leg sizes, divided by
  (q_c x tick value) of its primary leg (NULL_CRITERIA_E 3).
In dollars, x ticks/ct/day is x * q_c * tick_value_usd a day at the vehicle's size q_c.

Frozen values (eps_X, q_c, tick value) come from reports/stage_e2a_epsilon.json by vehicle, never
from an argument. The file is one of E.2a's hashed tables; its sha256 is carried in every result.
No bar is read here.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from functools import lru_cache

import numpy as np

from data.config import REPO_ROOT

EPSILON_TABLE = "reports/stage_e2a_epsilon.json"
UNIT = "net ticks per contract per day of the vehicle"


# ------------------------------------------------------------ frozen epsilon ----


@dataclass(frozen=True)
class FrozenEpsilon:
    """eps_X of one traded exposure, read from the frozen E.2a table."""

    vehicle: str
    eps_ticks: int  # operative eps_X, ticks/ct/day
    q_c: int  # the vehicle's risk-matched size, contracts
    tick_value_usd: float  # USD per tick per contract
    eps_usd_per_day_at_q: float  # eps_ticks * q_c * tick_value_usd
    source_sha256: str  # sha256 of reports/stage_e2a_epsilon.json


def _positive_int(value: object, what: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{what} must be a positive int, got {value!r}")
    return value


@lru_cache(maxsize=1)
def _epsilon_table() -> tuple[dict[str, FrozenEpsilon], str]:
    raw = (REPO_ROOT / EPSILON_TABLE).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    payload = json.loads(raw.decode("utf-8"))
    table: dict[str, FrozenEpsilon] = {}
    for row in payload["exposures"]:
        vehicle = row["vehicle"]
        if vehicle in table:
            raise ValueError(f"{EPSILON_TABLE} lists vehicle {vehicle!r} twice")
        eps = _positive_int(row["eps_operative"], f"{vehicle} eps_operative")
        q_c = _positive_int(row["q_c"], f"{vehicle} q_c")
        tick = float(row["tick_value_usd"])
        if not (math.isfinite(tick) and tick > 0.0):
            raise ValueError(f"{vehicle} tick_value_usd must be finite and > 0, got {tick!r}")
        table[vehicle] = FrozenEpsilon(
            vehicle=vehicle,
            eps_ticks=eps,
            q_c=q_c,
            tick_value_usd=tick,
            eps_usd_per_day_at_q=ticks_to_usd_per_day(float(eps), q_c, tick),
            source_sha256=digest,
        )
    return table, digest


def frozen_epsilon(vehicle: str) -> FrozenEpsilon:
    """The operative eps_X of ``vehicle`` (a traded exposure's vehicle); unknown vehicles raise."""
    table, _digest = _epsilon_table()
    if vehicle not in table:
        raise KeyError(
            f"vehicle {vehicle!r} has no operative eps in {EPSILON_TABLE} "
            f"(traded vehicles: {sorted(table)})"
        )
    return table[vehicle]


def ticks_to_usd_per_day(ticks_per_contract: float, q_c: int, tick_value_usd: float) -> float:
    """ticks/ct/day -> USD a day at size q_c: ticks * q_c * tick value."""
    _positive_int(q_c, "q_c")
    if not (math.isfinite(tick_value_usd) and tick_value_usd > 0.0):
        raise ValueError(f"tick_value_usd must be finite and > 0, got {tick_value_usd!r}")
    return float(ticks_per_contract) * q_c * tick_value_usd


# ----------------------------------------------------------------- series ----


@dataclass(frozen=True)
class Trip:
    """One closed round trip of a single-vehicle member."""

    trade_date: date  # the trade date the round trip closes on
    net_usd: float  # net P&L after costs, USD, whole position
    contracts: int  # the trip's own contract quantity, >= 1


@dataclass(frozen=True)
class DailySeries:
    """A member's research-window daily series in ticks/ct/day, one value per window date."""

    member_id: str
    vehicle: str  # the (primary-leg) vehicle whose eps_X applies
    dates: tuple[date, ...]  # every research-window trade date after exclusions, ascending
    values: tuple[float, ...]  # ticks/ct/day, 0.0 on a window date without a trip
    n_trips: int

    def array(self) -> np.ndarray:
        return np.asarray(self.values, dtype=float)


def _checked_window(window_dates: Sequence[date]) -> tuple[date, ...]:
    dates = tuple(window_dates)
    if not dates:
        raise ValueError("the research window is empty")
    for earlier, later in zip(dates, dates[1:], strict=False):
        if not later > earlier:
            raise ValueError(
                f"window dates must be strictly ascending and unique; {later} follows {earlier}"
            )
    return dates


def _aggregate_trips(
    trips: Sequence[Trip], window_dates: Sequence[date], tick_value_usd: float
) -> np.ndarray:
    """Sum over the trips closing on each window date of net_usd / (contracts * tick value)."""
    dates = _checked_window(window_dates)
    index = {d: i for i, d in enumerate(dates)}
    out = np.zeros(len(dates), dtype=float)
    for trip in trips:
        contracts = trip.contracts
        if isinstance(contracts, bool) or not isinstance(contracts, int) or contracts < 1:
            raise ValueError(f"trip on {trip.trade_date}: contracts must be an int >= 1, "
                             f"got {contracts!r}")
        if not math.isfinite(trip.net_usd):
            raise ValueError(f"trip on {trip.trade_date}: net_usd must be finite")
        if trip.trade_date not in index:
            raise ValueError(f"trip on {trip.trade_date} is outside the research window")
        out[index[trip.trade_date]] += trip.net_usd / (contracts * tick_value_usd)
    return out


def daily_series_from_trips(
    member_id: str, vehicle: str, trips: Sequence[Trip], window_dates: Sequence[date]
) -> DailySeries:
    """A single-vehicle member's series; the tick value is the frozen table's."""
    frozen = frozen_epsilon(vehicle)
    values = _aggregate_trips(trips, window_dates, frozen.tick_value_usd)
    return DailySeries(
        member_id=member_id,
        vehicle=vehicle,
        dates=_checked_window(window_dates),
        values=tuple(float(v) for v in values),
        n_trips=len(trips),
    )


def daily_series_from_leg_dollars(
    member_id: str,
    primary_vehicle: str,
    daily_net_usd: Mapping[date, float],
    window_dates: Sequence[date],
    n_trips: int,
) -> DailySeries:
    """A multi-leg member's series: combined net USD per day / (q_c x tick value) of the
    primary leg (frozen table); a window date absent from ``daily_net_usd`` is 0.0."""
    if isinstance(n_trips, bool) or not isinstance(n_trips, int) or n_trips < 0:
        raise ValueError(f"n_trips must be an int >= 0, got {n_trips!r}")
    frozen = frozen_epsilon(primary_vehicle)
    dates = _checked_window(window_dates)
    index = {d: i for i, d in enumerate(dates)}
    divisor = frozen.q_c * frozen.tick_value_usd
    out = np.zeros(len(dates), dtype=float)
    for day, usd in daily_net_usd.items():
        if day not in index:
            raise ValueError(f"leg dollars on {day} are outside the research window")
        if not math.isfinite(usd):
            raise ValueError(f"leg dollars on {day} must be finite")
        out[index[day]] = usd / divisor
    return DailySeries(
        member_id=member_id,
        vehicle=primary_vehicle,
        dates=dates,
        values=tuple(float(v) for v in out),
        n_trips=n_trips,
    )
