"""V2.2 decision clock: three decision times per product and trade date, and the DecisionRows table.

docs/STAGE_E_ML_V2_DESIGN.md V2.2; contract reports/stage_e11_interfaces.md section 2.

- O_X (the day-session open) is D6's, from the frozen session table
  (screening.stage_e_frozen.load_frozen_tables().day_session_ct for the representative vehicle
  of the group); F_X is D9's regular flatten (rules.sessions.REGULAR_FLATTEN_CT). The rule:
  t1 = O + 30 min; t3 = the latest O + 30k with t3 + 120 min <= F;
  t2 = O + 30 x floor((1 + k3) / 2).
  ``decision_times_ct`` reproduces constants.DECISION_TIMES_CT (a test pins the whole table).
- Per trade date, O_X and F_X come from ml_route.inputs.day_times (the group calendar's D6 session
  and rules.sessions' flatten on that date). Excluded dates (V2.2, v1 M4 and ML-A09):
  - not a trade date of the group calendar, or no flatten time (a closure);
  - an early-halt date of the group calendar (DayTimes.early_halt);
  - an early close of the flatten table: F_X on that date earlier than the group's regular F
    (Topstep close-by days; reading TC-1, reported: such a date has fewer than three admissible
    times under the rule, and V2.2 excludes early-close dates as a whole);
  - the caller's ``exclude`` map. Under V2.2 (lead ruling 2026-10-03) the v2 pipeline passes only
    each product's own roll-blackout dates (pipeline.own_blackout, ``exclude_union`` with the
    price path as the only leg); a signal leg's roll date drops no row and makes the signals that
    read that leg not applicable instead (signals/_core.py). D4's union over every leg
    (``exclude_union`` with all legs) stays the rule for the frozen K8 members as trials.
- decision_ts_ns = t in UTC ns (the close of the bar opening at t - 1 min); the entry fills at the
  open of the bar opening at t (V2.2 notation).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date, datetime, time
from functools import lru_cache

import numpy as np
import pandas as pd

from ml_route_v2.constants import (
    DECISION_STEP_MIN,
    DECISION_TIMES_CT,
    FIRST_DECISION_OFFSET_MIN,
    LONGEST_FIXED_HORIZON_MIN,
    N_DECISION_TIMES,
    UNIVERSE,
)

ROW_COLUMNS = ("root", "path_root", "cluster", "group", "trade_date", "t_index",
               "decision_ts_ns", "flatten_ts_ns")
# The session group (V2.2 table) of each vehicle: data.calendars' group, metals split by D6's
# sub-group (gold, copper).
_METALS = "metals"
# One vehicle per session group whose frozen D6 session gives the group's O_X.
GROUP_REPRESENTATIVE = {"equity": "MNQ", "crypto": "MBT", "rates": "ZN", "fx": "6E",
                        "energy": "MCL", "gold": "MGC", "copper": "MHG", "grains": "ZC",
                        "livestock": "HE"}


class ClockError(ValueError):
    """The decision clock cannot be formed (an unknown root or group, or a degenerate session)."""


def _minutes(at: time) -> int:
    return at.hour * 60 + at.minute


def _clock(minutes: int) -> time:
    if not 0 <= minutes < 24 * 60:
        raise ClockError(f"clock minute {minutes} is not inside one day")
    return time(minutes // 60, minutes % 60)


def decision_times_from(open_ct: time, flatten_ct: time) -> tuple[time, ...]:
    """V2.2's rule for one session: (t1, t2, t3) from O_X and F_X (CT)."""
    o, f = _minutes(open_ct), _minutes(flatten_ct)
    k3 = (f - LONGEST_FIXED_HORIZON_MIN - o) // DECISION_STEP_MIN
    first_k = FIRST_DECISION_OFFSET_MIN // DECISION_STEP_MIN
    if k3 < first_k + N_DECISION_TIMES - 1:
        raise ClockError(f"O {open_ct} and F {flatten_ct} leave fewer than {N_DECISION_TIMES} "
                         "distinct decision times")
    k2 = (1 + k3) // 2
    return tuple(_clock(o + DECISION_STEP_MIN * k) for k in (first_k, k2, k3))


@lru_cache(maxsize=64)
def _data_group(root: str) -> str:
    from data.calendars import GROUP_OF_PRODUCT

    if root not in GROUP_OF_PRODUCT:
        raise ClockError(f"{root}: no group calendar")
    return GROUP_OF_PRODUCT[root]


@lru_cache(maxsize=64)
def session_group(root: str) -> str:
    """The V2.2 session group of a vehicle (metals split into gold and copper)."""
    group = _data_group(root)
    if group != _METALS:
        return group
    from ml_route.inputs import _group_calendar

    sub = _group_calendar(_METALS).subgroup_of_product.get(root)
    if sub is None:
        raise ClockError(f"{root}: no metals sub-group")
    return sub


def _regular_flatten(group: str) -> time:
    from rules.sessions import REGULAR_FLATTEN_CT

    data_group = _METALS if group in ("gold", "copper") else group
    if data_group not in REGULAR_FLATTEN_CT:
        raise ClockError(f"no regular flatten time for group {group!r}")
    return REGULAR_FLATTEN_CT[data_group]


def decision_times_ct(group: str) -> tuple[time, ...]:
    """The V2.2 rule on the group's frozen D6 open and regular F; pinned to DECISION_TIMES_CT."""
    from screening.stage_e_frozen import load_frozen_tables

    if group not in GROUP_REPRESENTATIVE:
        raise ClockError(f"unknown session group {group!r}")
    table = load_frozen_tables().day_session_ct
    opens = {table[v][0] for v in UNIVERSE if session_group(v) == group}
    if len(opens) != 1:
        raise ClockError(f"group {group}: the vehicles' D6 opens differ ({sorted(opens)})")
    return decision_times_from(opens.pop(), _regular_flatten(group))


def pinned_table() -> Mapping[str, tuple[time, ...]]:
    """The design's table (constants.DECISION_TIMES_CT), for the pin test and the report."""
    return DECISION_TIMES_CT


@lru_cache(maxsize=200_000)
def _day_times(root: str, day: date):  # noqa: ANN202 - ml_route.inputs.DayTimes | None
    from ml_route.inputs import day_times

    return day_times(root, _data_group(root), day)


def _ct_minute_of(ns: int) -> int:
    from ml_route.inputs import ct_minute_of_ns

    return ct_minute_of_ns(ns)


def _date_rows(root: str, day: date) -> list[tuple[int, int, int]]:
    """[(t_index, decision_ts_ns, flatten_ts_ns)] of one product date; [] when excluded."""
    dt = _day_times(root, day)
    if dt is None or dt.early_halt:
        return []
    group = session_group(root)
    f_min = _ct_minute_of(dt.flatten_ns)
    if f_min != _minutes(_regular_flatten(group)):
        return []  # an early close of the flatten table (reading TC-1)
    o_min = _ct_minute_of(dt.open_ns)
    times = decision_times_from(_clock(o_min), _clock(f_min))
    out = []
    for k, at in enumerate(times, start=1):
        offset = (_minutes(at) - o_min) * 60_000_000_000
        out.append((k, dt.open_ns + offset, dt.flatten_ns))
    return out


def decision_rows(roots: Sequence[str], trade_dates: Mapping[str, Sequence[date]], *,
                  exclude: Mapping[str, frozenset[date]] | None = None) -> pd.DataFrame:
    """DecisionRows (interfaces section 2) of ``roots`` on their ``trade_dates``, sorted by
    (decision_ts_ns, root); excluded dates are dropped (module docstring)."""
    exclude = exclude or {}
    recs: list[tuple] = []
    for root in roots:
        if root not in UNIVERSE:
            raise ClockError(f"{root} is not a vehicle of constants.UNIVERSE")
        cluster, path = UNIVERSE[root]
        group = session_group(root)
        skip = exclude.get(root, frozenset())
        for day in sorted(set(trade_dates.get(root, ()))):
            day = _as_date(day)
            if day in skip:
                continue
            for k, t_ns, f_ns in _date_rows(root, day):
                recs.append((root, path, cluster, group, day, k, t_ns, f_ns))
    frame = pd.DataFrame.from_records(recs, columns=list(ROW_COLUMNS))
    frame["trade_date"] = pd.to_datetime(frame["trade_date"]).astype("datetime64[ns]")
    frame["t_index"] = frame["t_index"].astype(np.int8)
    for col in ("decision_ts_ns", "flatten_ts_ns"):
        frame[col] = frame[col].astype(np.int64)
    for col in ("root", "path_root", "cluster", "group"):
        frame[col] = frame[col].astype(object)
    frame = frame.sort_values(["decision_ts_ns", "root"], kind="mergesort")
    return frame.reset_index(drop=True)


def _as_date(day: object) -> date:
    if isinstance(day, datetime):
        return day.date()
    if isinstance(day, date):
        return day
    if isinstance(day, (np.datetime64, pd.Timestamp)):
        return pd.Timestamp(day).date()
    if isinstance(day, str):
        return date.fromisoformat(day[:10])
    raise ClockError(f"not a date: {day!r}")


def trade_dates_of(bars: pd.DataFrame) -> list[date]:
    """The distinct trade dates of a bar frame (its ``trade_date`` column)."""
    codes = pd.Series(bars["trade_date"]).astype(str).unique()
    return sorted(date.fromisoformat(c[:10]) for c in codes)


def exclude_union(blackout_by_root: Mapping[str, frozenset[date]],
                  legs_by_root: Mapping[str, Sequence[str]]) -> dict[str, frozenset[date]]:
    """D4's union: a product's excluded dates are its own and those of every leg it reads."""
    out: dict[str, frozenset[date]] = {}
    for root, legs in legs_by_root.items():
        days: set[date] = set(blackout_by_root.get(root, frozenset()))
        for leg in legs:
            days |= set(blackout_by_root.get(leg, frozenset()))
        out[root] = frozenset(days)
    return out


def minutes_after_midnight_ct(ts_ns: np.ndarray) -> np.ndarray:
    """CT clock minute of each UTC ns instant (vectorized)."""
    idx = pd.to_datetime(np.asarray(ts_ns, dtype=np.int64), utc=True).tz_convert("America/Chicago")
    return (idx.hour * 60 + idx.minute).to_numpy().astype(np.int64)


__all__ = [
    "GROUP_REPRESENTATIVE", "ROW_COLUMNS", "ClockError", "decision_rows", "decision_times_ct",
    "decision_times_from", "exclude_union", "minutes_after_midnight_ct", "pinned_table",
    "session_group", "trade_dates_of",
]
