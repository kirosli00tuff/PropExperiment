"""Flatten times per product group and date (design D9.1, D9.13; brief item 6b), Stage E.

F is the time from which no new position may be opened and by which every position is closed
("no new position after F, every position closed by F", D9.1): both windows start at F, unlike
MES's engine (rules/xfa_rules.py: flatten 15:10 CT, no new positions 2 minutes earlier), which is
not changed.

Per group, on a regular day:
- equity, rates, FX, energy, metals, crypto: F = 15:08 CT (TopstepX, facts F4.2); reopen 17:00 CT.
- grains: F = 13:18 CT (session close 13:20, F4.3); overnight segment 19:00-07:45 CT, and no
  position may be held into the 07:45-08:30 CT pause (F4.5), so an overnight position is closed
  by 07:43 CT and nothing opens in [07:43, 08:30).
- livestock: F = 13:03 CT (session 08:30-13:05, F4.4); no overnight segment.
On a date the group's CME calendar lists:
- FULL_CLOSURE: no trading.
- EARLY_HALT at h: F = min(regular F, h - 15 min) (D9.1, D9.13; Topstep's holiday article,
  F12.3a: "All account types must close positions 15 minutes before any early close").
Topstep's own published holiday schedule binds too (brief item 6b): F on such a date is the
earliest of the regular F, the CME early close minus 15 minutes, and Topstep's published
close-by time, and a date Topstep lists as "Markets closed" has no trading. Topstep's schedules
(help.topstep.com, quoted verbatim in reports/stage_e2a_rules.md) were retrieved for 2024, 2025
and 2026. In 2024 and 2025 Topstep required Funded Accounts to close "30 minutes before the early
close"; from 2026 its article says 15 minutes. For an early-halt date that Topstep's schedule of
that year does not list, the year's published lead applies as well (30 minutes in 2024-2025).
For 2019-2023 no Topstep schedule was retrieved: F is D9.1's rule alone, and those dates are
flagged (``TOPSTEP_SCHEDULE_YEARS``).

Weekends: TopstepX is closed from Friday's F to Sunday's reopen (F4.1).
Scheduled late opens (grains' LATE_OPENS without a halt time, lead ruling L-6): no evening
session into that trade date and no trading before its open time. The unscheduled 2025-11-28 CME
outage (other groups' LATE_OPENS, which carry ``halt_from_ct``) is an event, not a rule, and is
not encoded.

The group calendars are inputs: ``GroupHolidays`` maps a group to its ``HOLIDAYS`` (date ->
data.cme_calendar.Holiday). ``load_group_holidays`` reads the real modules; tests pass synthetic
maps.
"""

from __future__ import annotations

import importlib
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from data.calendars import GROUPS
from data.cme_calendar import Holiday, HolidayKind
from rules.products import product

CT = ZoneInfo("America/Chicago")
_FRIDAY, _SATURDAY, _SUNDAY = 4, 5, 6

F_1508 = time(15, 8)
REGULAR_FLATTEN_CT: dict[str, time] = {
    "equity": F_1508, "rates": F_1508, "fx": F_1508, "energy": F_1508, "metals": F_1508,
    "crypto": F_1508, "grains": time(13, 18), "livestock": time(13, 3),
}
# First minute a new session may trade (TopstepX 17:00 CT reopen; CME grains 19:00 CT;
# livestock has no evening segment: its session starts 08:30 CT the same day).
REOPEN_CT: dict[str, time] = {
    "equity": time(17, 0), "rates": time(17, 0), "fx": time(17, 0), "energy": time(17, 0),
    "metals": time(17, 0), "crypto": time(17, 0), "grains": time(19, 0),
}
LIVESTOCK_OPEN_CT = time(8, 30)
GRAIN_PAUSE_EXIT_CT = time(7, 43)  # 2 minutes before the 07:45 CT pause, as 13:18 is to 13:20
GRAIN_DAY_OPEN_CT = time(8, 30)
EARLY_CLOSE_LEAD = timedelta(minutes=15)  # D9.1, D9.13, facts F12.3a


# ------------------------------------------------------- Topstep holiday schedule ----
@dataclass(frozen=True)
class TopstepHoliday:
    """One row of Topstep's published holiday schedule. ``close_by_ct`` None = markets closed."""

    day: date
    close_by_ct: time | None
    source: str  # source id in reports/stage_e2a_rules.md / the rules cache


_TS_2024 = "topstep_8284222_2024"  # help.topstep.com/en/articles/8284222, capture 2024-01-05/10-14
_TS_2025 = "topstep_8284222_2025"  # same article, captures 2025-03-16 and 2025-10-17
_TS_2026 = "topstep_13350348_2026"  # help.topstep.com/en/articles/13350348, 2026-02-19, 2026-09-25
_1130, _1145, _1200 = time(11, 30), time(11, 45), time(12, 0)
_CLOSED = None

TOPSTEP_HOLIDAYS: dict[date, TopstepHoliday] = {
    h.day: h
    for h in (
        # 2024: "Topstep requires traders in Funded Accounts to close all positions 30 minutes
        # before the early close."
        TopstepHoliday(date(2024, 1, 15), _1130, _TS_2024),
        TopstepHoliday(date(2024, 2, 19), _1130, _TS_2024),
        TopstepHoliday(date(2024, 3, 29), _CLOSED, _TS_2024),
        TopstepHoliday(date(2024, 5, 27), _1130, _TS_2024),
        TopstepHoliday(date(2024, 6, 19), _1130, _TS_2024),
        TopstepHoliday(date(2024, 7, 3), _1130, _TS_2024),
        TopstepHoliday(date(2024, 7, 4), _1130, _TS_2024),
        TopstepHoliday(date(2024, 9, 2), _1130, _TS_2024),
        TopstepHoliday(date(2024, 11, 28), _1130, _TS_2024),
        TopstepHoliday(date(2024, 11, 29), _1145, _TS_2024),
        TopstepHoliday(date(2024, 12, 24), _1145, _TS_2024),
        TopstepHoliday(date(2024, 12, 25), _CLOSED, _TS_2024),
        TopstepHoliday(date(2025, 1, 1), _CLOSED, _TS_2024),
        # 2025: same rule text.
        TopstepHoliday(date(2025, 1, 20), _1130, _TS_2025),
        TopstepHoliday(date(2025, 2, 17), _1130, _TS_2025),
        TopstepHoliday(date(2025, 4, 18), _CLOSED, _TS_2025),
        TopstepHoliday(date(2025, 5, 26), _1130, _TS_2025),
        TopstepHoliday(date(2025, 6, 19), _1130, _TS_2025),
        TopstepHoliday(date(2025, 7, 4), _1130, _TS_2025),
        TopstepHoliday(date(2025, 9, 1), _1130, _TS_2025),
        TopstepHoliday(date(2025, 11, 27), _1130, _TS_2025),
        TopstepHoliday(date(2025, 11, 28), _1145, _TS_2025),
        TopstepHoliday(date(2025, 12, 24), _1145, _TS_2025),
        TopstepHoliday(date(2025, 12, 25), _CLOSED, _TS_2025),
        TopstepHoliday(date(2026, 1, 1), _CLOSED, _TS_2025),
        # 2026: "All account types must close positions 15 minutes before any early close."
        TopstepHoliday(date(2026, 1, 19), _1145, _TS_2026),
        TopstepHoliday(date(2026, 2, 16), _1145, _TS_2026),
        TopstepHoliday(date(2026, 4, 3), time(8, 0), _TS_2026),
        TopstepHoliday(date(2026, 5, 25), _1145, _TS_2026),
        TopstepHoliday(date(2026, 6, 19), _1145, _TS_2026),  # "SIM: 11:45 CT"; the XFA is SIM
        TopstepHoliday(date(2026, 7, 3), _1145, _TS_2026),
        TopstepHoliday(date(2026, 9, 7), _1145, _TS_2026),
        TopstepHoliday(date(2026, 11, 26), _1145, _TS_2026),
        TopstepHoliday(date(2026, 11, 27), _1200, _TS_2026),
        TopstepHoliday(date(2026, 12, 24), _1200, _TS_2026),
        TopstepHoliday(date(2026, 12, 25), _CLOSED, _TS_2026),
        TopstepHoliday(date(2027, 1, 1), _CLOSED, _TS_2026),
    )
}
# Topstep's published lead before an early close, per calendar year of its schedule.
TOPSTEP_EARLY_CLOSE_LEAD: dict[int, timedelta] = {
    2024: timedelta(minutes=30), 2025: timedelta(minutes=30), 2026: timedelta(minutes=15),
}
TOPSTEP_SCHEDULE_YEARS: frozenset[int] = frozenset(TOPSTEP_EARLY_CLOSE_LEAD)


# ------------------------------------------------------------------ calendars ----
GroupHolidays = Mapping[str, Mapping[date, Holiday]]


def load_group_holidays() -> dict[str, dict[date, Holiday]]:
    """HOLIDAYS of every group module (equity: data.cme_calendar)."""
    out: dict[str, dict[date, Holiday]] = {}
    for group in GROUPS:
        name = "data.cme_calendar" if group == "equity" else f"data.calendars.{group}"
        out[group] = dict(importlib.import_module(name).HOLIDAYS)
    return out


def load_scheduled_late_opens() -> dict[str, dict[date, time]]:
    """Scheduled late opens per group (trade date -> first open CT), from each module's
    LATE_OPENS: a scheduled entry has no ``halt_from_ct`` field (grains, lead ruling L-6: no
    overnight segment after a closure); the 2025-11-28 outage entries carry one and are an
    unscheduled event, not a rule, so they are left out."""
    out: dict[str, dict[date, time]] = {}
    for group in GROUPS:
        if group == "equity":
            out[group] = {}
            continue
        mod = importlib.import_module(f"data.calendars.{group}")
        out[group] = {d: e.open_ct for d, e in getattr(mod, "LATE_OPENS", {}).items()
                      if not hasattr(e, "halt_from_ct")}
    return out


_DEFAULT: dict[str, dict[date, Holiday]] | None = None
_DEFAULT_LATE: dict[str, dict[date, time]] | None = None


def default_holidays() -> dict[str, dict[date, Holiday]]:
    global _DEFAULT
    if _DEFAULT is None:
        _DEFAULT = load_group_holidays()
    return _DEFAULT


def default_late_opens() -> dict[str, dict[date, time]]:
    global _DEFAULT_LATE
    if _DEFAULT_LATE is None:
        _DEFAULT_LATE = load_scheduled_late_opens()
    return _DEFAULT_LATE


LateOpens = Mapping[str, Mapping[date, time]]


def _minus(at: time, delta: timedelta) -> time:
    return (datetime.combine(date(2000, 1, 3), at) - delta).time()


@dataclass(frozen=True)
class DayRule:
    """The flatten rule of one product group on one CT calendar date."""

    group: str
    day: date
    closed: bool  # no trading at all on this calendar date
    flatten_ct: time | None  # F (None when closed)
    reasons: tuple[str, ...]  # every candidate that set or tied F, for the audit trail


def day_rule(root: str, day: date, holidays: GroupHolidays | None = None) -> DayRule:
    """F for ``root`` on CT calendar date ``day`` (weekday or not; weekends are handled by the
    window functions)."""
    group = product(root).group
    cal = (holidays if holidays is not None else default_holidays())[group]
    regular = REGULAR_FLATTEN_CT[group]
    cands: list[tuple[time, str]] = [(regular, f"regular F {regular:%H:%M}")]
    hol = cal.get(day)
    if hol is not None and hol.kind is HolidayKind.FULL_CLOSURE:
        return DayRule(group, day, True, None, (f"CME full closure ({hol.name})",))
    topstep = TOPSTEP_HOLIDAYS.get(day)
    if topstep is not None and topstep.close_by_ct is None:
        return DayRule(group, day, True, None, (f"Topstep: markets closed ({topstep.source})",))
    if hol is not None and hol.kind is HolidayKind.EARLY_HALT:
        if hol.halt_ct is None:
            raise ValueError(f"{group} {day}: early halt without a time")
        cands.append((_minus(hol.halt_ct, EARLY_CLOSE_LEAD),
                      f"CME early close {hol.halt_ct:%H:%M} - 15 min"))
        lead = TOPSTEP_EARLY_CLOSE_LEAD.get(day.year)
        if lead is not None and topstep is None:
            cands.append((_minus(hol.halt_ct, lead),
                          f"Topstep {day.year} rule: {int(lead.total_seconds() // 60)} min "
                          f"before the early close {hol.halt_ct:%H:%M}"))
    if topstep is not None and topstep.close_by_ct is not None:
        cands.append((topstep.close_by_ct,
                      f"Topstep close-by {topstep.close_by_ct:%H:%M} ({topstep.source})"))
    f = min(c[0] for c in cands)
    return DayRule(group, day, False, f, tuple(r for t, r in cands if t == f))


def flatten_time_ct(root: str, day: date, holidays: GroupHolidays | None = None) -> time | None:
    """F on ``day``, or None when the group does not trade that calendar date."""
    return day_rule(root, day, holidays).flatten_ct


# ------------------------------------------------------------- the windows ----
def _to_ct(ts: datetime) -> datetime:
    if ts.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    return ts.astimezone(CT)


@dataclass(frozen=True)
class SessionState:
    can_open: bool  # a new (non-reducing) position may be opened now
    must_be_flat: bool  # every position must be closed now
    reason: str


def _closed(reason: str) -> SessionState:
    return SessionState(False, True, reason)


def _open(reason: str = "inside the session") -> SessionState:
    return SessionState(True, False, reason)


def _next_weekday(day: date) -> date:
    nxt = day + timedelta(days=1)
    while nxt.weekday() >= _SATURDAY:
        nxt += timedelta(days=1)
    return nxt


def session_state(root: str, ts: datetime, holidays: GroupHolidays | None = None,
                  late_opens: LateOpens | None = None) -> SessionState:
    """Whether a position may be opened and whether one must be flat at ``ts``."""
    group = product(root).group
    local = _to_ct(ts)
    day, t, wd = local.date(), local.time(), local.weekday()
    if group == "livestock":
        return _livestock_state(root, day, t, wd, holidays)
    late = (late_opens if late_opens is not None else default_late_opens()).get(group, {})
    reopen = REOPEN_CT[group]
    if wd == _SATURDAY or (wd == _SUNDAY and t < reopen):
        return _closed("weekend")
    if wd == _SUNDAY or t >= reopen:  # the evening segment of the next trade date
        if wd == _FRIDAY:
            return _closed("weekend")
        nxt = _next_weekday(day)
        if day_rule(root, nxt, holidays).closed:
            return _closed(f"next trade date {nxt} is closed")
        if nxt in late:
            return _closed(f"no evening session: {nxt} opens late at {late[nxt]:%H:%M} CT")
        return _open("evening session")
    rule = day_rule(root, day, holidays)
    if rule.closed:
        return _closed("; ".join(rule.reasons))
    assert rule.flatten_ct is not None
    if day in late and t < late[day]:
        return _closed(f"late open at {late[day]:%H:%M} CT")
    if t >= rule.flatten_ct:
        return _closed(f"flatten window from {rule.flatten_ct:%H:%M} CT "
                       f"({'; '.join(rule.reasons)})")
    if group == "grains" and GRAIN_PAUSE_EXIT_CT <= t < GRAIN_DAY_OPEN_CT:
        return _closed("grain pause: flat from 07:43 CT until the 08:30 CT open")
    return _open()


def _livestock_state(root: str, day: date, t: time, wd: int,
                     holidays: GroupHolidays | None) -> SessionState:
    if wd >= _SATURDAY:
        return _closed("weekend")
    rule = day_rule(root, day, holidays)
    if rule.closed:
        return _closed("; ".join(rule.reasons))
    assert rule.flatten_ct is not None
    if t < LIVESTOCK_OPEN_CT:
        return _closed("before the 08:30 CT livestock open")
    if t >= rule.flatten_ct:
        return _closed(f"flatten window from {rule.flatten_ct:%H:%M} CT "
                       f"({'; '.join(rule.reasons)})")
    return _open()


@dataclass(frozen=True)
class ForcedFlatten:
    root: str
    side: str
    quantity: int
    reason: str


def required_flatten(root: str, position: int, ts: datetime,
                     holidays: GroupHolidays | None = None,
                     late_opens: LateOpens | None = None) -> ForcedFlatten | None:
    """The close the rules force, or None. There is no override input."""
    if position == 0:
        return None
    state = session_state(root, ts, holidays, late_opens)
    if not state.must_be_flat:
        return None
    return ForcedFlatten(root, "sell" if position > 0 else "buy", abs(position), state.reason)
