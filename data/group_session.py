"""Group-aware CME sessions for the Stage E bar builds (design D9.1, D10, D11.4; Stage E.2a Task 7).

``data.session`` stays MES's session layer and is not changed. This module generalizes it to a
group calendar: ``data.calendars.<group>`` (``HOLIDAYS``, ``SESSIONS``, ``CALENDAR_COVERAGE``,
``assert_calendar_coverage``), or, for the equity group, ``data.cme_calendar`` with the MES
session of ``data.session`` (17:00 CT on the prior calendar day to 16:00 CT).

The model, stated once:
- A trade date is a weekday that is not a listed FULL_CLOSURE of the group.
- A trade date D's open time is the union of its ``SessionSpec`` segments, each
  ``[D + start_offset_days start_ct, D + end_offset_days end_ct)`` in CT wall-clock time, cut at
  ``halt_ct`` when D is a listed EARLY_HALT (every part at or after the halt is closed).
- Everything else is closed. Closed windows are the complement of the open intervals over the
  range asked for, as half-open UTC-nanosecond windows (``data.intervals`` convention).
- A bar's trade date is the trade date whose open interval contains it. A bar inside a closed
  window (a hard failure of the Stage E build) is given the trade date of the NEXT open interval,
  which is also how a roll splice at 00:00 UTC inside a closure (a grain or livestock evening, a
  weekend, a holiday) gets its trade date; ``data.session.trade_date`` gives the same answer for
  every splice instant of the equity calendar.
For the equity calendar this reproduces ``data.session.trade_date`` and
``data.session.closed_windows_range_ns`` on every open minute (tests/test_e2a_bars.py).

Flatten windows (D9.1) are a ``FlattenPolicy``: F per group (15:08 CT; grains 13:18 CT and no
position into the 07:45 CT pause, so the overnight segment's last two minutes are flagged;
livestock 13:03 CT), and on an early-halt day F = the halt minus 15 minutes when that is earlier.
Stage E encodes "no new position after F, every position closed by F", so both MES-style flag
columns start at F. ``MES_POLICY`` is the MES research parquet's rule (rules.xfa_rules: flatten
15:10 CT, no new positions 2 minutes earlier), kept for the MES regression. The windows are read
per CT calendar date, as MES's are ([F, 17:00) CT), plus TopstepX's weekend closure (Friday from
17:00 to Sunday 17:00 CT), which only weekend-assigned crypto bars reach (from 2026-06-01).

Crypto (data/calendars/crypto.py, lead rulings L-9 and L-10): a BOOKED_FORWARD weekday is not a
trade date; its regular session belongs to CME's trade date for it (two calendar days in one
trade date). From WEEKEND_TO_NEXT_TRADE_DATE_FROM a trade date after a weekend or holiday runs
from the previous trade date's 16:02 CT to its own 16:00 CT, less the Saturday 02:00-04:00 CT
maintenance (SEGMENTS_AFTER_WEEKEND_24_7, checked equal for an ordinary Monday); an
EXTENDED_MAINTENANCE entry delays a trade date's first open. Grains (ruling L-6): a scheduled
late open removes the overnight segment.
"""

from __future__ import annotations

import hashlib
import importlib
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from data.calendars import GROUP_OF_PRODUCT, GROUPS, Segment, SessionSpec
from data.cme_calendar import Holiday, HolidayKind
from data.config import REPO_ROOT
from data.intervals import merge_windows
from data.session import CME_TZ, HALT_END, HALT_START, ct_ns

NS_PER_MIN = 60 * 1_000_000_000
NS_PER_DAY = 86_400 * 1_000_000_000
TOPSTEP_OPEN_CT = time(17, 0)  # TopstepX opens every trade date at 17:00 CT the prior evening
_EPOCH = date(1970, 1, 1)

# The equity group's session when data/calendars/equity.py does not provide SESSIONS: the MES
# session of data/session.py, validated on the MES research bars (reports/bar_validation.md). It
# is used for the research window only, hence valid_from 2025-01-01.
EQUITY_FALLBACK_SESSIONS: tuple[SessionSpec, ...] = (
    SessionSpec(
        valid_from=date(2025, 1, 1),
        valid_to=None,
        segments=(Segment(-1, HALT_END, 0, HALT_START),),
        day_session_ct={"*": (time(8, 30), time(15, 0))},
        source="data/session.py (HALT_START 16:00, HALT_END 17:00 CT)",
        note="MES session (data.session): 17:00 CT prior calendar day to 16:00 CT; the "
             "step-4b day-session close is MES's RTH close 15:00 CT (data.validate).",
    ),
)


class CalendarNotReady(RuntimeError):
    """A group's calendar module is missing or lacks part of the interface."""


class SessionModelError(ValueError):
    """The session tables give overlapping or unsorted open intervals."""


@dataclass(frozen=True)
class GroupCalendar:
    """One group's calendar, as the bar builder uses it."""

    group: str
    holidays: Mapping[date, Holiday]
    sessions: tuple[SessionSpec, ...]
    coverage: tuple[date, date]
    assert_coverage: Callable[[Iterable[date]], None]
    module_paths: tuple[Path, ...]
    late_opens: Mapping[date, Any] = field(default_factory=dict)
    # Days a module lists for the bar check without an entry (rates GLOBEX_HOURS_UNDOCUMENTED):
    # the check reports what the bars show there.
    watch_days: Mapping[date, str] = field(default_factory=dict)
    # Lead ruling L-6: SCHEDULED late opens (grains: no overnight segment, first minute at the
    # 08:30 CT day open) are closed windows; unscheduled ones (the 2025-11-28 outage) are only
    # checked (ruling L-4 revised). date -> the scheduled open time.
    scheduled_late_opens: Mapping[date, time] = field(default_factory=dict)
    # D6 sub-group keys of SessionSpec.day_session_ct (metals: gold / silver / copper).
    subgroup_of_product: Mapping[str, str] = field(default_factory=dict)
    # Crypto BOOKED_FORWARD (lead ruling L-10): a weekday B with regular hours but no CME trade
    # date; its session belongs to trade date booked_forward[B]. B is not a trade date.
    booked_forward: Mapping[date, date] = field(default_factory=dict)
    # Crypto SEGMENTS_AFTER_WEEKEND_24_7: the session of the first trade date after a weekend in
    # the weekend-assignment regime (its internal gap is the weekly maintenance).
    after_weekend_segments: tuple[Segment, ...] = ()
    # Crypto EXTENDED_MAINTENANCE (scheduled): trade date -> the instant its session opened.
    delayed_starts: Mapping[date, tuple[int, time]] = field(default_factory=dict)
    # Crypto (D10): from this trade date on, trading that falls on a weekend (or on a full
    # closure) belongs to the next trade date; the builder follows it. None for other groups.
    weekend_to_next_trade_date_from: date | None = None

    def spec_for(self, day: date) -> SessionSpec:
        found = [s for s in self.sessions
                 if s.valid_from <= day and (s.valid_to is None or day <= s.valid_to)]
        if not found:  # a booked-forward target past the specs takes its booked day's spec
            booked = [b for b, d in self.booked_forward.items() if d == day]
            if booked:
                return self.spec_for(max(booked))
        if len(found) != 1:
            raise SessionModelError(
                f"{self.group}: {len(found)} session specs cover trade date {day}")
        return found[0]

    def holiday(self, day: date) -> Holiday | None:
        return self.holidays.get(day)

    def is_full_closure(self, day: date) -> bool:
        hol = self.holidays.get(day)
        return hol is not None and hol.kind is HolidayKind.FULL_CLOSURE

    def early_halt_ct(self, day: date) -> time | None:
        hol = self.holidays.get(day)
        if hol is not None and hol.kind is HolidayKind.EARLY_HALT:
            return hol.halt_ct
        return None

    def is_trade_date(self, day: date) -> bool:
        return day.weekday() < 5 and not self.is_full_closure(day) \
            and day not in self.booked_forward

    def booked_target_covered(self, day: date) -> bool:
        """``day`` is past the coverage but is the CME trade date of a covered booked day."""
        return any(d == day and self.covers(b) for b, d in self.booked_forward.items())

    def covers(self, day: date) -> bool:
        first, last = self.coverage
        in_specs = any(s.valid_from <= day and (s.valid_to is None or day <= s.valid_to)
                       for s in self.sessions)
        return first <= day <= last and in_specs

    def day_session_close(self, product: str) -> dict[date, time]:
        """D6's day-session close C per SessionSpec (valid_from -> C) for ``product``."""
        out: dict[date, time] = {}
        for spec in self.sessions:
            table = spec.day_session_ct
            if product in table:
                out[spec.valid_from] = table[product][1]
            elif self.subgroup_of_product.get(product) in table:
                out[spec.valid_from] = table[self.subgroup_of_product[product]][1]
            elif "*" in table:
                out[spec.valid_from] = table["*"][1]
            elif len({v[1] for v in table.values()}) == 1:
                out[spec.valid_from] = next(iter(table.values()))[1]
            else:
                raise CalendarNotReady(
                    f"{self.group}: SessionSpec from {spec.valid_from} has no day-session close "
                    f"for {product} (keys {sorted(table)})")
        return out

    def module_sha256(self) -> dict[str, str]:
        return {(str(p.relative_to(REPO_ROOT)) if p.is_relative_to(REPO_ROOT) else str(p)):
                sha256_file(p) for p in self.module_paths}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _module_file(name: str) -> Path:
    base = REPO_ROOT / name.replace(".", "/")
    return base / "__init__.py" if base.is_dir() else base.with_suffix(".py")


def load_group_calendar(group: str) -> GroupCalendar:
    """The group's calendar. Equity: data.cme_calendar's entries (final for the research window)
    with data/calendars/equity.py's SESSIONS if that module exists, else the MES session."""
    if group not in GROUPS:
        raise CalendarNotReady(f"unknown group {group!r}")
    if group == "equity":
        return _equity_calendar()
    name = f"data.calendars.{group}"
    if not _module_file(name).is_file():
        raise CalendarNotReady(f"{_module_file(name)} does not exist yet")
    mod = importlib.import_module(name)
    missing = [a for a in ("HOLIDAYS", "SESSIONS", "CALENDAR_COVERAGE", "assert_calendar_coverage")
               if not hasattr(mod, a)]
    if missing:
        raise CalendarNotReady(f"{name} lacks {missing}")
    weekend_from = getattr(mod, "WEEKEND_TO_NEXT_TRADE_DATE_FROM", None)
    late_opens = dict(getattr(mod, "LATE_OPENS", {}))
    return GroupCalendar(
        group=group, holidays=dict(mod.HOLIDAYS), sessions=tuple(mod.SESSIONS),
        coverage=tuple(mod.CALENDAR_COVERAGE), assert_coverage=mod.assert_calendar_coverage,
        module_paths=(_module_file(name), _module_file("data.calendars")),
        late_opens=late_opens,
        watch_days=dict(getattr(mod, "GLOBEX_HOURS_UNDOCUMENTED", {})),
        weekend_to_next_trade_date_from=weekend_from,
        scheduled_late_opens={d: e.open_ct for d, e in late_opens.items()
                              if is_scheduled_late_open(e)},
        subgroup_of_product=dict(getattr(mod, "SUBGROUP_OF_PRODUCT", {})),
        booked_forward={d: b.cme_trade_date for d, b in
                        getattr(mod, "BOOKED_FORWARD", {}).items()},
        after_weekend_segments=tuple(getattr(mod, "SEGMENTS_AFTER_WEEKEND_24_7", ())),
        delayed_starts={d: (e.open_offset_days, e.open_ct) for d, e in
                        getattr(mod, "EXTENDED_MAINTENANCE", {}).items()},
    )


def is_scheduled_late_open(entry: Any) -> bool:  # noqa: ANN401 — a module's LateOpen
    """Ruling L-6: tell a scheduled late open from an unscheduled one by the module's own type.
    The grains LateOpen ("a trade date with no overnight segment", cited to CME's holiday
    trading schedules) has no stop-time field; the rates/FX/energy/metals LateOpen ("did not
    trade from its regular start", the 2025-11-28 outage) carries ``halt_from_ct``. The entry
    name must agree (an outage or unscheduled halt on one side only), else the module is
    refused as ambiguous."""
    outage_named = any(w in entry.name.lower() for w in ("outage", "unscheduled"))
    scheduled = not hasattr(entry, "halt_from_ct")
    if scheduled == outage_named:
        raise CalendarNotReady(f"late open {entry.day} ({entry.name!r}): cannot tell a "
                               "scheduled late open from an outage")
    return scheduled


def _equity_calendar() -> GroupCalendar:
    import data.cme_calendar as cme

    paths = [_module_file("data.cme_calendar")]
    sessions = EQUITY_FALLBACK_SESSIONS
    late_opens: dict = {}
    if _module_file("data.calendars.equity").is_file():
        mod = importlib.import_module("data.calendars.equity")
        if getattr(mod, "SESSIONS", None):
            if dict(getattr(mod, "HOLIDAYS", cme.HOLIDAYS)) != dict(cme.HOLIDAYS):
                raise CalendarNotReady("data/calendars/equity.py HOLIDAYS differ from "
                                       "data.cme_calendar's")
            sessions = tuple(mod.SESSIONS)
            paths.append(_module_file("data.calendars.equity"))
            # The 2025-11-28 outage: unscheduled, so checked only (ruling L-4 revised).
            late_opens = dict(getattr(mod, "LATE_OPENS", {}))
            if any(is_scheduled_late_open(e) for e in late_opens.values()):
                raise CalendarNotReady("equity LATE_OPENS lists a scheduled late open; the "
                                       "equity sessions would change (not expected)")
    if sessions is EQUITY_FALLBACK_SESSIONS:
        paths.append(_module_file("data.session"))
    paths.append(_module_file("data.calendars"))
    return GroupCalendar(
        group="equity", holidays=dict(cme.HOLIDAYS), sessions=sessions,
        coverage=tuple(cme.CALENDAR_COVERAGE), assert_coverage=cme.assert_calendar_coverage,
        module_paths=tuple(paths), late_opens=late_opens,
    )


def group_of(product: str) -> str:
    return GROUP_OF_PRODUCT[product]


# ------------------------------------------------------------------ open intervals ----
def trade_dates_between(cal: GroupCalendar, first: date, last: date) -> list[date]:
    days = (first + timedelta(days=n) for n in range((last - first).days + 1))
    return [d for d in days if cal.is_trade_date(d)]


def _ct(day: date, offset: int, at: time) -> int:
    return ct_ns(day + timedelta(days=offset), at)


def regular_intervals(cal: GroupCalendar, day: date) -> list[tuple[int, int]]:
    """Trade date ``day``'s segments from its SessionSpec, ignoring holidays."""
    spec = cal.spec_for(day)
    return [(_ct(day, s.start_offset_days, s.start_ct), _ct(day, s.end_offset_days, s.end_ct))
            for s in spec.segments]


def session_intervals(cal: GroupCalendar, day: date) -> list[tuple[int, int]]:
    """Trade date ``day``'s open intervals: its segments, starting no earlier than a scheduled
    late open and cut at a listed early halt; none on a weekend or a listed full closure."""
    if not cal.is_trade_date(day):
        return []
    out = _base_intervals(cal, day)
    delayed = cal.delayed_starts.get(day)
    if delayed is not None:  # a scheduled maintenance extension delayed the first open
        start = ct_ns(day + timedelta(days=delayed[0]), delayed[1])
        out = [(max(lo, start), hi) for lo, hi in out if hi > start]
    late = cal.scheduled_late_opens.get(day)
    if late is not None:  # ruling L-6: nothing before the scheduled open trades
        start = ct_ns(day, late)
        out = [(max(lo, start), hi) for lo, hi in out if hi > start]
    halt = cal.early_halt_ct(day)
    if halt is not None:
        cut = ct_ns(day, halt)
        out = [(lo, min(hi, cut)) for lo, hi in out if lo < cut]
    return out


def previous_trade_date(cal: GroupCalendar, day: date, max_back: int = 10) -> date | None:
    for n in range(1, max_back + 1):
        if cal.is_trade_date(day - timedelta(days=n)):
            return day - timedelta(days=n)
    return None


def _base_intervals(cal: GroupCalendar, day: date) -> list[tuple[int, int]]:
    """Trade date ``day``'s segments before halts and late opens.
    - Weekend-assignment regime (crypto 24/7, from ``weekend_to_next_trade_date_from``): when
      weekend, holiday or booked days lie between the previous trade date P and ``day``, the
      session runs from P at the segment's start time to ``day``'s end, less the weekly
      maintenance of ``after_weekend_segments`` on every such weekday in between; for an
      ordinary Monday this must equal the module's SEGMENTS_AFTER_WEEKEND_24_7 exactly.
    - Otherwise the regular segments, preceded by the regular sessions of the booked-forward
      days whose CME trade date is ``day`` (ruling L-10)."""
    start_rule = cal.weekend_to_next_trade_date_from
    if start_rule is not None and day >= start_rule:
        prev = previous_trade_date(cal, day)
        if prev is not None and (day - prev).days > 1:
            return _anchored_span(cal, day, prev)
        return regular_intervals(cal, day)
    out: list[tuple[int, int]] = []
    for booked in sorted(b for b, d in cal.booked_forward.items() if d == day):
        out.extend(regular_intervals(cal, booked))
    out.extend(regular_intervals(cal, day))
    return out


def _anchored_span(cal: GroupCalendar, day: date, prev: date) -> list[tuple[int, int]]:
    segs = cal.spec_for(day).segments
    if len(segs) != 1:
        raise SessionModelError(f"{cal.group}: weekend assignment needs one segment on {day}")
    lo = ct_ns(prev, segs[0].start_ct)
    hi = _ct(day, segs[0].end_offset_days, segs[0].end_ct)
    gaps: list[tuple[int, int]] = []
    tpl = cal.after_weekend_segments
    if len(tpl) >= 2:  # the template is a Monday trade date: its gaps' weekdays are fixed
        for a, b in zip(tpl, tpl[1:], strict=False):
            weekday = (a.end_offset_days) % 7  # Monday is weekday 0
            span = (prev + timedelta(days=n) for n in range((day - prev).days + 1))
            gaps.extend((ct_ns(d, a.end_ct), _ct(d, b.start_offset_days - a.end_offset_days,
                                                  b.start_ct))
                        for d in span if d.weekday() == weekday)
    out, cursor = [], lo
    for g0, g1 in sorted(gaps):
        if g0 > cursor:
            out.append((cursor, min(g0, hi)))
        cursor = max(cursor, g1)
    if cursor < hi:
        out.append((cursor, hi))
    if tpl and (day - prev).days == 3 and day.weekday() == 0:
        expected = [(_ct(day, t.start_offset_days, t.start_ct), _ct(day, t.end_offset_days,
                                                                    t.end_ct)) for t in tpl]
        if out != expected:
            raise SessionModelError(f"{cal.group}: the anchored span of {day} differs from "
                                    "SEGMENTS_AFTER_WEEKEND_24_7")
    return out


@dataclass(frozen=True)
class OpenIntervals:
    """Open intervals, sorted and disjoint, each labelled with its trade date."""

    starts: np.ndarray  # int64 UTC ns
    ends: np.ndarray
    days: tuple[date, ...]

    def __len__(self) -> int:
        return len(self.days)


def open_intervals(cal: GroupCalendar, first: date, last: date) -> OpenIntervals:
    """Every open interval of the trade dates ``first..last`` (both inclusive, clipped to the
    calendar's coverage, plus a booked-forward target of a covered day: crypto's 2026-06-22).
    Weekend assignment and booked-forward days: ``_base_intervals``."""
    rows: list[tuple[int, int, date]] = []
    for day in trade_dates_between(cal, first, last):
        if not (cal.covers(day) or cal.booked_target_covered(day)):
            continue
        rows.extend((lo, hi, day) for lo, hi in session_intervals(cal, day))
    rows.sort(key=lambda r: r[0])
    for (_s0, e0, d0), (s1, _e1, d1) in zip(rows, rows[1:], strict=False):
        if s1 < e0:
            raise SessionModelError(f"{cal.group}: open intervals of {d0} and {d1} overlap")
    return OpenIntervals(np.array([r[0] for r in rows], dtype=np.int64),
                         np.array([r[1] for r in rows], dtype=np.int64),
                         tuple(r[2] for r in rows))


def closed_windows(opened: OpenIntervals, lo_ns: int, hi_ns: int) -> tuple[np.ndarray, np.ndarray]:
    """The complement of ``opened`` inside ``[lo_ns, hi_ns)``, as (starts, ends) arrays."""
    windows: list[tuple[int, int]] = []
    cursor = lo_ns
    for s, e in zip(opened.starts.tolist(), opened.ends.tolist(), strict=True):
        if e <= lo_ns:
            continue
        if s >= hi_ns:
            break
        if s > cursor:
            windows.append((cursor, min(s, hi_ns)))
        cursor = max(cursor, e)
    if cursor < hi_ns:
        windows.append((cursor, hi_ns))
    merged = merge_windows(windows)
    return (np.array([w[0] for w in merged], dtype=np.int64),
            np.array([w[1] for w in merged], dtype=np.int64))


@dataclass(frozen=True)
class TradeDateAssignment:
    days: np.ndarray  # datetime64[D]; NaT where no covered trade date follows the bar
    in_closure: np.ndarray  # bool: the bar is in no open interval
    boundary: np.ndarray | None = None  # bool: a closure bar in the minute after a session end

    def as_dates(self) -> list[date | None]:
        return [None if np.isnat(d) else d.astype(object) for d in self.days]


def assign_trade_dates(opened: OpenIntervals, ts: np.ndarray, *,
                       close_minute_to_previous: bool = False) -> TradeDateAssignment:
    """Trade date of every bar: the open interval containing it, else the next one (NaT when
    no covered open interval follows, i.e. past the calendar's coverage).

    ``close_minute_to_previous`` (lead ruling L-3, 2026-09-25): a closure bar in the first
    minute after an open interval ends (a print stamped in the close minute) takes the trade
    date of the session it closes; ``boundary`` marks those bars."""
    ts = np.asarray(ts, dtype=np.int64)
    day_arr = np.array([np.datetime64(d, "D") for d in opened.days] + [np.datetime64("NaT", "D")],
                       dtype="datetime64[D]")
    idx = np.searchsorted(opened.starts, ts, side="right") - 1
    if len(opened):
        prev_end = opened.ends[np.clip(idx, 0, None)]
        inside = (idx >= 0) & (ts < prev_end)
        boundary = (idx >= 0) & ~inside & (ts < prev_end + NS_PER_MIN)
    else:
        inside = boundary = np.zeros(ts.shape, dtype=bool)
    pick = np.where(inside, idx, idx + 1)
    if close_minute_to_previous:
        pick = np.where(boundary, idx, pick)
    pick = np.clip(pick, 0, len(opened))  # len(opened) -> the NaT sentinel
    return TradeDateAssignment(day_arr[pick], ~inside, boundary)


def trade_date_of_instant(opened: OpenIntervals, ts_ns: int) -> date | None:
    """The trade date of an instant (a roll splice): its open interval, else the next one."""
    got = assign_trade_dates(opened, np.array([ts_ns], dtype=np.int64)).as_dates()[0]
    return got


def roll_blackout(cal: GroupCalendar, splices: Iterable[date], sessions_before: int
                  ) -> frozenset[date]:
    """sim.engine.roll_blackout_dates with the GROUP's trade dates: the splice trade date and the
    ``sessions_before`` group trade dates before it."""
    out: set[date] = set()
    for splice in splices:
        out.add(splice)
        day, found = splice, 0
        while found < sessions_before:
            day -= timedelta(days=1)
            if cal.is_trade_date(day):
                out.add(day)
                found += 1
    return frozenset(out)


# ------------------------------------------------------------------ flatten policy ----
@dataclass(frozen=True)
class FlattenPolicy:
    """When a bar is inside the flatten / no-new-positions windows of its trade date."""

    name: str
    flatten_ct: time  # regular F
    no_new_lead: timedelta  # the no-new window starts this long before the flatten
    early_close_lead: timedelta = timedelta(minutes=15)
    pause_exit_lead: timedelta | None = None  # grains: no position into a session pause

    def flatten_on(self, halt: time | None) -> time:
        if halt is None:
            return self.flatten_ct
        cut = (datetime.combine(_EPOCH, halt) - self.early_close_lead).time()
        return min(self.flatten_ct, cut)

    def no_new_on(self, halt: time | None) -> time:
        return (datetime.combine(_EPOCH, self.flatten_on(halt)) - self.no_new_lead).time()

    def as_dict(self) -> dict[str, str]:
        return {"name": self.name, "flatten_ct": self.flatten_ct.strftime("%H:%M"),
                "no_new_lead_min": str(int(self.no_new_lead.total_seconds() // 60)),
                "early_close_lead_min": str(int(self.early_close_lead.total_seconds() // 60)),
                "pause_exit_lead_min": ("" if self.pause_exit_lead is None else
                                        str(int(self.pause_exit_lead.total_seconds() // 60)))}


# MES research parquet (rules.xfa_rules): flatten 15:10 CT or 15 minutes before an early close,
# no new positions 2 minutes earlier.
MES_POLICY = FlattenPolicy("mes_stage_a1", time(15, 10), timedelta(minutes=2))
_F = time(15, 8)
STAGE_E_POLICIES: dict[str, FlattenPolicy] = {
    **{g: FlattenPolicy(f"stage_e_d9_1_{g}", _F, timedelta(0))
       for g in ("equity", "rates", "fx", "energy", "metals", "crypto")},
    "grains": FlattenPolicy("stage_e_d9_1_grains", time(13, 18), timedelta(0),
                            pause_exit_lead=timedelta(minutes=2)),
    "livestock": FlattenPolicy("stage_e_d9_1_livestock", time(13, 3), timedelta(0)),
}


def _date_min(days: np.ndarray, at_of: Callable[[date], time]) -> np.ndarray:
    uniq, inverse = np.unique(days, return_inverse=True)
    values = np.array([(t := at_of(d.astype(object))).hour * 60 + t.minute for d in uniq],
                      dtype=np.int64)
    return values[inverse.reshape(-1)]


def flatten_masks(cal: GroupCalendar, policy: FlattenPolicy, ts: np.ndarray,
                  days: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(in_flatten_window, in_no_new_positions_window) per bar. MES's rule, per CT CALENDAR
    date X of the bar (TopstepX treats each calendar day on its own, data.session): inside when
    the bar's CT time is in [F_X, 17:00) (no-new: [N_X, 17:00)), F_X from X's early halt; plus
    TopstepX's weekend closure (Friday from 17:00, Saturday, Sunday before 17:00 CT), which only
    weekend-assigned crypto bars reach; plus (pause policy) the last ``pause_exit_lead`` of a
    segment followed by a pause on the same trade date (``days``, datetime64[D]). On a crypto
    booked-forward trade date the booked-in holiday session is its own calendar day here."""
    ts = np.asarray(ts, dtype=np.int64)
    local = pd.to_datetime(ts, utc=True).tz_convert(CME_TZ)
    local_date = np.array(local.date, dtype="datetime64[D]")
    minutes = np.asarray(local.hour * 60 + local.minute)
    weekday = np.asarray(local.weekday)
    reopen = TOPSTEP_OPEN_CT.hour * 60 + TOPSTEP_OPEN_CT.minute
    flat_min = _date_min(local_date, lambda d: policy.flatten_on(cal.early_halt_ct(d)))
    nonew_min = _date_min(local_date, lambda d: policy.no_new_on(cal.early_halt_ct(d)))
    weekend = ((weekday == 4) & (minutes >= reopen)) | (weekday == 5) | \
        ((weekday == 6) & (minutes < reopen))
    before_reopen = minutes < reopen
    in_flat = (before_reopen & (minutes >= flat_min)) | weekend
    in_nonew = (before_reopen & (minutes >= nonew_min)) | weekend
    if policy.pause_exit_lead is not None:
        pre_pause = _pause_windows(cal, policy, days)
        mask = _in_any(ts, pre_pause)
        in_flat |= mask
        in_nonew |= mask
    return in_flat, in_nonew


def _pause_windows(cal: GroupCalendar, policy: FlattenPolicy, days: np.ndarray
                   ) -> list[tuple[int, int]]:
    lead = int(policy.pause_exit_lead.total_seconds()) * 1_000_000_000  # type: ignore[union-attr]
    out: list[tuple[int, int]] = []
    for d in np.unique(days):
        day = d.astype(object)
        segs = session_intervals(cal, day)
        out.extend((hi - lead, hi) for (_lo, hi), (nxt, _h) in zip(segs, segs[1:], strict=False)
                   if nxt > hi)
    return merge_windows(out)


def _in_any(ts: np.ndarray, windows: list[tuple[int, int]]) -> np.ndarray:
    if not windows:
        return np.zeros(ts.shape, dtype=bool)
    starts = np.array([w[0] for w in windows], dtype=np.int64)
    ends = np.array([w[1] for w in windows], dtype=np.int64)
    idx = np.searchsorted(starts, ts, side="right") - 1
    return (idx >= 0) & (ts < ends[np.clip(idx, 0, None)])


def early_halt_labels(cal: GroupCalendar, ts: np.ndarray) -> list[str]:
    """MES's ``early_halt_ct`` column: the early halt ("HH:MM") of the bar's CT CALENDAR date
    (not its trade date), "" when none."""
    local_date = pd.to_datetime(np.asarray(ts, dtype=np.int64), utc=True).tz_convert(CME_TZ).date
    labels = {d: (h.strftime("%H:%M") if (h := cal.early_halt_ct(d)) else "")
              for d in set(local_date)}
    return [labels[d] for d in local_date]


def utc_midnight_ns(day: date) -> int:
    return int(datetime(day.year, day.month, day.day, tzinfo=UTC).timestamp()) * 1_000_000_000
