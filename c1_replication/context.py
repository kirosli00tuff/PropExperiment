"""The context that supplies test C1's 2010-2019 tables to the frozen code, and restores it.

The frozen modules (ml_route_v2/, ml_route/inputs.py, data/group_session.py, rules/sessions.py,
strategy/members/k4/) are never edited. Where they read a module-level table or calendar that
covers only 2019-05 onward, ``hist_tables(tables)`` swaps that ONE module attribute for the
replication's table while the block runs, and puts every original object back on exit (also on
an exception). It never writes a file. Nested use is refused. On entry and on exit it clears every
functools cache defined in the modules that read a calendar (``CACHE_MODULES``), so nothing
computed under one set of tables is read under the other.

What is swapped (``PATCHES``; module attribute -> what the replication supplies):
1. data.group_session.load_group_calendar and ml_route.inputs._group_calendar -> the six pinned
   hist group calendars (data.hist_calendar.HistGroupCalendar; equity, rates, fx, energy, metals,
   grains); any other group raises (no silent fallback to a 2019+ calendar). Read by the decision
   clock (ml_route.inputs.day_times), the signals (sigma_X,d halts, in-session checks, G5's
   previous trade date, G16's month end) and synthetic.training_calendar.
2. rules.sessions._DEFAULT and _DEFAULT_LATE (the cached results of default_holidays() and
   default_late_opens()) -> the hist calendars' holidays and scheduled late opens per group: the
   flatten rule's CME holidays (day_rule).
3. rules.sessions.TOPSTEP_HOLIDAYS -> the frozen rows plus the Rule H-1 rows derived from the hist
   equity calendar (tables.h1_rows; days before 2019-05-01, disjoint from the frozen rows), and
   rules.sessions.TOPSTEP_EARLY_CLOSE_LEAD -> the frozen leads plus 30 minutes for 2010-2018
   (lead ruling L-E5-2, as 2019-2023).
4. strategy.members.k4.ngpre.make_ng -> NgPre("NG", ngs=<the hist NGS table less C13's drops>)
   (NgPre binds the frozen NGS table as a dataclass default at import, so the factory is the one
   name that carries another table; k4_ngpre_* read ngpre.make_ng().ngs).
5. strategy.members.k4._calendar.ENERGY_FULL_SESSIONS, strategy.members.k4.ovr's
   ENERGY_FULL_SESSIONS, _FULL_SESSIONS and _FULL_ORDINALS -> the hist energy full sessions
   (K4-ovr's 20 reference dates, ovr.reference_dates).
Not swapped, because no NG row reads them (their vehicles have no rows in an NG-only world, so
their signals are "not applicable" on every row, as in E.12): the K1-K3 and K5-K9 member tables,
K4's WPSR / API / NYSE tables (MCL members), the frozen D6 session table and the D8 cost table
(date-independent).
"""

from __future__ import annotations

import importlib
import threading
from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import date
from types import MappingProxyType
from typing import Any

import numpy as np

from c1_replication.constants import H1_LEAD, H1_LEAD_YEARS, VEHICLE

PATCHES: tuple[tuple[str, str], ...] = (
    ("data.group_session", "load_group_calendar"),
    ("ml_route.inputs", "_group_calendar"),
    ("rules.sessions", "_DEFAULT"),
    ("rules.sessions", "_DEFAULT_LATE"),
    ("rules.sessions", "TOPSTEP_HOLIDAYS"),
    ("rules.sessions", "TOPSTEP_EARLY_CLOSE_LEAD"),
    ("strategy.members.k4.ngpre", "make_ng"),
    ("strategy.members.k4._calendar", "ENERGY_FULL_SESSIONS"),
    ("strategy.members.k4.ovr", "ENERGY_FULL_SESSIONS"),
    ("strategy.members.k4.ovr", "_FULL_SESSIONS"),
    ("strategy.members.k4.ovr", "_FULL_ORDINALS"),
)
CACHE_MODULES: tuple[str, ...] = (
    "ml_route.inputs", "ml_route_v2.clock", "ml_route_v2.synthetic", "ml_route_v2.targets",
    "ml_route_v2.signals._core", "ml_route_v2.signals._daily", "ml_route_v2.signals._events",
    "ml_route_v2.signals.generic", "ml_route_v2.signals.ports", "ml_route_v2.signals.k1",
    "ml_route_v2.signals.k2", "ml_route_v2.signals.k3", "ml_route_v2.signals.k4",
    "ml_route_v2.signals.k5", "ml_route_v2.signals.k6", "ml_route_v2.signals.k7",
    "ml_route_v2.signals.k8", "ml_route_v2.signals.k9", "data.group_session", "rules.sessions",
    "strategy.members.k4.ngpre", "strategy.members.k4.ovr",
)
HIST_GROUPS_REQUIRED = ("equity", "rates", "fx", "energy", "metals", "grains")
_LOCK = threading.Lock()
_ACTIVE = {"on": False}


class ContextError(RuntimeError):
    """The replication tables are incomplete, or the context is already active."""


@dataclass(frozen=True)
class HistTables:
    """Everything the context supplies (module docstring)."""

    calendars: Mapping[str, Any]  # group -> data.hist_calendar.HistGroupCalendar
    topstep_rows: Mapping[date, Any]  # Rule H-1 rows (rules.sessions.TopstepHoliday)
    ngs_table: tuple[tuple[str, str], ...]  # (ISO date, "HH:MM" CT), C13 drops removed
    full_sessions: tuple[str, ...]  # ISO dates, hist ENERGY_FULL_SESSIONS
    note: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        missing = [g for g in HIST_GROUPS_REQUIRED if g not in self.calendars]
        if missing:
            raise ContextError(f"hist calendars missing for {missing}")
        wrong = [g for g, c in self.calendars.items() if getattr(c, "group", None) != g]
        if wrong:
            raise ContextError(f"calendar keyed under another group: {wrong}")


def _module(name: str) -> Any:  # noqa: ANN401
    return importlib.import_module(name)


def clear_caches() -> list[str]:
    """Clear every functools cache defined in CACHE_MODULES (returns their qualified names)."""
    cleared = []
    for name in CACHE_MODULES:
        mod = _module(name)
        for attr, obj in sorted(vars(mod).items()):
            fn = getattr(obj, "cache_clear", None)
            if callable(fn) and getattr(obj, "__module__", None) == name:
                fn()
                cleared.append(f"{name}.{attr}")
    return cleared


def _calendar_loader(calendars: Mapping[str, Any]) -> Callable[[str], Any]:
    def load(group: str) -> Any:  # noqa: ANN401
        from data.hist_calendar import HistCalendarError

        cal = calendars.get(group)
        if cal is None:
            raise HistCalendarError(f"C1 replication: no hist calendar for group {group!r} "
                                    f"(hist groups {sorted(calendars)})")
        return cal

    return load


def replacement_values(tables: HistTables) -> dict[tuple[str, str], Any]:
    """The object each PATCHES entry gets inside the context."""
    from rules import sessions
    from strategy.members.k4 import ngpre

    overlap = set(tables.topstep_rows) & set(sessions.TOPSTEP_HOLIDAYS)
    if overlap:
        raise ContextError(f"Rule H-1 rows overlap the frozen Topstep rows: {sorted(overlap)[:3]}")
    loader = _calendar_loader(MappingProxyType(dict(tables.calendars)))
    holidays = {g: dict(c.holidays) for g, c in tables.calendars.items()}
    late = {g: dict(getattr(c, "scheduled_late_opens", {})) for g, c in tables.calendars.items()}
    topstep = {**dict(tables.topstep_rows), **sessions.TOPSTEP_HOLIDAYS}
    leads = {**{y: H1_LEAD for y in H1_LEAD_YEARS}, **sessions.TOPSTEP_EARLY_CLOSE_LEAD}
    ngs = tuple((str(d), str(t)) for d, t in tables.ngs_table)

    def make_ng() -> Any:  # noqa: ANN401
        return ngpre.NgPre(VEHICLE, ngs=ngs)

    full = tuple(str(d) for d in tables.full_sessions)
    full_dates = tuple(date.fromisoformat(d) for d in full)
    return {
        ("data.group_session", "load_group_calendar"): loader,
        ("ml_route.inputs", "_group_calendar"): loader,
        ("rules.sessions", "_DEFAULT"): holidays,
        ("rules.sessions", "_DEFAULT_LATE"): late,
        ("rules.sessions", "TOPSTEP_HOLIDAYS"): topstep,
        ("rules.sessions", "TOPSTEP_EARLY_CLOSE_LEAD"): leads,
        ("strategy.members.k4.ngpre", "make_ng"): make_ng,
        ("strategy.members.k4._calendar", "ENERGY_FULL_SESSIONS"): full,
        ("strategy.members.k4.ovr", "ENERGY_FULL_SESSIONS"): full,
        ("strategy.members.k4.ovr", "_FULL_SESSIONS"): full_dates,
        ("strategy.members.k4.ovr", "_FULL_ORDINALS"): np.array(
            [d.toordinal() for d in full_dates], dtype=np.int64),
    }


def originals() -> dict[tuple[str, str], Any]:
    """The objects PATCHES name, as they are now (for the restore check)."""
    return {(m, a): getattr(_module(m), a) for m, a in PATCHES}


@contextmanager
def hist_tables(tables: HistTables) -> Iterator[dict[tuple[str, str], Any]]:
    """Swap PATCHES for the replication's tables while the block runs (module docstring).
    Yields the replacement objects."""
    with _LOCK:
        if _ACTIVE["on"]:
            raise ContextError("the C1 hist-table context is already active (no nesting)")
        _ACTIVE["on"] = True
    saved: dict[tuple[str, str], Any] = {}
    try:
        values = replacement_values(tables)
        clear_caches()
        for key in PATCHES:
            mod = _module(key[0])
            saved[key] = getattr(mod, key[1])
            setattr(mod, key[1], values[key])
        clear_caches()
        yield values
    finally:
        for key in reversed(PATCHES):
            if key in saved:
                setattr(_module(key[0]), key[1], saved[key])
        clear_caches()
        with _LOCK:
            _ACTIVE["on"] = False


def is_active() -> bool:
    return bool(_ACTIVE["on"])


def patch_record(tables: HistTables) -> list[dict[str, Any]]:
    """What each patch supplied (for the outputs): names, sizes and the calendars' files."""
    return [
        {"module": "data.group_session / ml_route.inputs",
         "names": ["load_group_calendar", "_group_calendar"],
         "supplied": {g: {"path": getattr(c, "file_path", ""),
                          "sha256": getattr(c, "file_sha256", "")}
                      for g, c in sorted(tables.calendars.items())}},
        {"module": "rules.sessions", "names": ["_DEFAULT", "_DEFAULT_LATE"],
         "supplied": "the hist calendars' holidays and scheduled late opens"},
        {"module": "rules.sessions", "names": ["TOPSTEP_HOLIDAYS", "TOPSTEP_EARLY_CLOSE_LEAD"],
         "supplied": {"h1_rows": len(tables.topstep_rows),
                      "lead_years_added": list(H1_LEAD_YEARS)}},
        {"module": "strategy.members.k4.ngpre", "names": ["make_ng"],
         "supplied": {"ngs_rows": len(tables.ngs_table)}},
        {"module": "strategy.members.k4._calendar / strategy.members.k4.ovr",
         "names": ["ENERGY_FULL_SESSIONS", "_FULL_SESSIONS", "_FULL_ORDINALS"],
         "supplied": {"full_sessions": len(tables.full_sessions)}},
    ]


__all__ = ["CACHE_MODULES", "PATCHES", "ContextError", "HistTables", "clear_caches",
           "hist_tables", "is_active", "originals", "patch_record", "replacement_values"]
