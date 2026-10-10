"""Stage E.14 (harness v10): the 2010-2019 group calendars of the hist stores (tests C1 and C2).

    from data.hist_calendar import load_hist_group_calendar
    cal = load_hist_group_calendar("equity")   # data/calendars/hist2010/equity.json

One JSON file per group (equity, rates, fx, energy, metals, grains) in schema
"e14_hist_calendar/1" (reports/stage_e14_briefs/calendar_rules.md, "Output format"), coverage
2010-06-01..2019-05-31. The loader builds a ``HistGroupCalendar``: a ``data.group_session``
``GroupCalendar`` (so open_intervals, assign_trade_dates, roll_blackout, flatten_masks and the
bar checks run on it unchanged) plus the set of UNSOURCED dates every reader excludes and counts
(C1 ruling C12, C2 section 3), the file's sha256 and computed counts.

Mapping of the file to the GroupCalendar model:
- entries kind "full_closure" / "early_halt" -> ``data.cme_calendar.Holiday`` (FULL_CLOSURE with
  halt_ct None; EARLY_HALT with halt_ct, the CT minute trading stops);
- entries kind "late_open" -> ``HistLateOpen`` under the grains LateOpen convention
  (data/calendars/grains.py): a scheduled late open, the trade date's first trading minute is
  ``open_ct`` CT on the trade date itself, nothing before it trades (ruling L-6);
- sessions -> ``data.calendars.SessionSpec`` rows (contiguous, covering the whole coverage).

UNSOURCED dates (a date is unsourced for every reason that applies; the reasons are recorded):
- "listed": the file's own "unsourced" list;
- "entry_unverified": an entry whose status grade ("evidence") is "unverified";
- "session_unverified": a weekday inside a SessionSpec whose evidence is "unverified";
- "year_not_covered": a weekday of a calendar year whose year_coverage row is missing, is
  graded "unverified", or has complete_exception_list not true (calendar_rules.md: "A date with
  no such coverage is UNSOURCED"), unless the date has its own entry or no-entry finding graded
  "cme" or "secondary".
Weekends are never trade dates and never unsourced.

Refusals (``HistCalendarError``, nothing is returned): an unknown group, a malformed file (schema,
types, a weekend or duplicate entry, a kind whose time fields do not match it, sessions that
overlap, leave a gap or do not cover the coverage), any entry, unsourced date or session outside
the coverage, and an unknown grade. ``assert_coverage`` refuses any date outside
2010-06-01..2019-05-31. Existing (2019-05 on) callers never use this module: it is read only by
data.hist_store, data.hist_bars and screening.stage_e14_c2.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import date, time, timedelta
from pathlib import Path
from typing import Any

from data.calendars import GROUP_OF_PRODUCT, Segment, SessionSpec
from data.cme_calendar import CalendarCoverageError, Holiday, HolidayKind
from data.config import REPO_ROOT
from data.group_session import CalendarNotReady, GroupCalendar

HIST_CALENDAR_SCHEMA = "e14_hist_calendar/1"
HIST_CALENDAR_DIR = REPO_ROOT / "data" / "calendars" / "hist2010"
HIST_GROUPS = ("equity", "rates", "fx", "energy", "metals", "grains")
HIST_COVERAGE = (date(2010, 6, 1), date(2019, 5, 31))
STATUS_GRADES = ("cme", "secondary", "unverified")
TIME_GRADES = ("cme", "secondary", "inferred", "unverified", "n/a")
SOURCED_GRADES = ("cme", "secondary")
UNVERIFIED = "unverified"
FULL_CLOSURE, EARLY_HALT, LATE_OPEN = "full_closure", "early_halt", "late_open"
KINDS = (FULL_CLOSURE, EARLY_HALT, LATE_OPEN)
REASON_LISTED = "listed"
REASON_ENTRY = "entry_unverified"
REASON_SESSION = "session_unverified"
REASON_YEAR = "year_not_covered"
UNSOURCED_REASONS = (REASON_LISTED, REASON_ENTRY, REASON_SESSION, REASON_YEAR)
_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
_CLOCK = re.compile(r"\d{2}:\d{2}")
MODULE_FILE = REPO_ROOT / "data" / "hist_calendar.py"


class HistCalendarError(CalendarNotReady):
    """A hist calendar file is missing, malformed, or asks for something outside its coverage."""


@dataclass(frozen=True)
class HistLateOpen:
    """A scheduled late open (the grains LateOpen convention): the trade date's first trading
    minute is ``open_ct`` CT on ``day`` itself. No ``halt_from_ct``: never an outage record."""

    day: date
    name: str
    open_ct: time
    evidence: str
    time_evidence: str


@dataclass(frozen=True)
class HistGroupCalendar(GroupCalendar):
    """A GroupCalendar built from one e14_hist_calendar/1 file, with its unsourced dates."""

    unsourced: frozenset[date] = frozenset()
    unsourced_reasons: Mapping[date, tuple[str, ...]] = field(default_factory=dict)
    products: tuple[str, ...] = ()
    file_path: str = ""
    file_sha256: str = ""
    counts: Mapping[str, Any] = field(default_factory=dict)

    def is_unsourced(self, day: date) -> bool:
        return day in self.unsourced

    def record(self) -> dict[str, Any]:
        """What a reader writes into its outputs: path, sha256 and the computed counts."""
        return {"group": self.group, "path": self.file_path, "sha256": self.file_sha256,
                "coverage": [str(d) for d in self.coverage], "counts": dict(self.counts)}


# ------------------------------------------------------------------ parsing helpers ----
def _fail(where: str, message: str) -> HistCalendarError:
    return HistCalendarError(f"hist calendar {where}: {message}")


def _day(value: Any, where: str) -> date:
    if not isinstance(value, str) or not _DATE.fullmatch(value):
        raise _fail(where, f"{value!r} is not a YYYY-MM-DD date")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise _fail(where, f"{value!r} is not a valid date") from exc


def _clock(value: Any, where: str) -> time:
    if not isinstance(value, str) or not _CLOCK.fullmatch(value):
        raise _fail(where, f"{value!r} is not an HH:MM time")
    try:
        return time.fromisoformat(value)
    except ValueError as exc:
        raise _fail(where, f"{value!r} is not a valid time") from exc


def _grade(value: Any, allowed: tuple[str, ...], where: str) -> str:
    if value not in allowed:
        raise _fail(where, f"unknown grade {value!r} (allowed {list(allowed)})")
    return str(value)


def _text(value: Any, where: str, *, required: bool = True) -> str:
    if value is None and not required:
        return ""
    if not isinstance(value, str) or (required and not value.strip()):
        raise _fail(where, f"{value!r} is not a non-empty string")
    return value


def _in_coverage(day: date, where: str) -> date:
    first, last = HIST_COVERAGE
    if not first <= day <= last:
        raise _fail(where, f"{day} is outside the coverage {first}..{last}")
    return day


def _dict(value: Any, where: str) -> dict:
    if not isinstance(value, dict):
        raise _fail(where, "is not an object")
    return value


def _list(value: Any, where: str) -> list:
    if not isinstance(value, list):
        raise _fail(where, "is not a list")
    return value


def _weekdays(first: date, last: date) -> list[date]:
    days = (first + timedelta(days=n) for n in range((last - first).days + 1))
    return [d for d in days if d.weekday() < 5]


# ------------------------------------------------------------------ sections ----
def _header(payload: dict, group: str, where: str) -> tuple[str, ...]:
    if payload.get("schema") != HIST_CALENDAR_SCHEMA:
        raise _fail(where, f"schema is {payload.get('schema')!r}, not {HIST_CALENDAR_SCHEMA!r}")
    if payload.get("group") != group:
        raise _fail(where, f"group is {payload.get('group')!r}, not {group!r}")
    products = _list(payload.get("products"), f"{where} products")
    if not products or any(not isinstance(p, str) for p in products):
        raise _fail(where, "products must be a non-empty list of strings")
    wrong = [p for p in products if GROUP_OF_PRODUCT.get(p) != group]
    if wrong or len(set(products)) != len(products):
        raise _fail(where, f"products {wrong or products} are not distinct products of {group}")
    labels = _list(payload.get("cme_row_labels"), f"{where} cme_row_labels")
    if any(not isinstance(x, str) for x in labels):
        raise _fail(where, "cme_row_labels must be strings")
    cov = _dict(payload.get("coverage"), f"{where} coverage")
    got = (_day(cov.get("first"), f"{where} coverage"), _day(cov.get("last"), f"{where} coverage"))
    if got != HIST_COVERAGE:
        raise _fail(where, f"coverage {got[0]}..{got[1]} is not {HIST_COVERAGE[0]}.."
                           f"{HIST_COVERAGE[1]}")
    return tuple(products)


def _segment(raw: Any, where: str) -> Segment:
    seg = _dict(raw, where)
    offsets = (seg.get("start_offset_days"), seg.get("end_offset_days"))
    if any(not isinstance(o, int) or isinstance(o, bool) or o not in (-1, 0) for o in offsets):
        raise _fail(where, f"offset days {offsets} must be -1 or 0")
    return Segment(offsets[0], _clock(seg.get("start_ct"), where), offsets[1],
                   _clock(seg.get("end_ct"), where))


def _check_segments(segments: tuple[Segment, ...], where: str) -> None:
    def minutes(offset: int, at: time) -> int:
        return offset * 1440 + at.hour * 60 + at.minute

    spans = [(minutes(s.start_offset_days, s.start_ct), minutes(s.end_offset_days, s.end_ct))
             for s in segments]
    if any(lo >= hi for lo, hi in spans) or any(a[1] > b[0] for a, b in zip(spans, spans[1:],
                                                                         strict=False)):
        raise _fail(where, "segments must each be non-empty, in time order and disjoint")


def _session(raw: Any, i: int, where: str) -> tuple[SessionSpec, str]:
    here = f"{where} sessions[{i}]"
    row = _dict(raw, here)
    valid_from = _day(row.get("valid_from"), here)
    valid_to = None if row.get("valid_to") is None else _day(row.get("valid_to"), here)
    if valid_to is not None and valid_to < valid_from:
        raise _fail(here, f"valid_to {valid_to} is before valid_from {valid_from}")
    segments = tuple(_segment(s, f"{here} segment") for s in _list(row.get("segments"), here))
    if not segments:
        raise _fail(here, "has no segments")
    _check_segments(segments, here)
    table = _dict(row.get("day_session_ct"), f"{here} day_session_ct")
    day_session: dict[str, tuple[time, time]] = {}
    for key, pair in table.items():
        if not isinstance(pair, list) or len(pair) != 2:
            raise _fail(here, f"day_session_ct[{key!r}] must be [open, close]")
        day_session[str(key)] = (_clock(pair[0], here), _clock(pair[1], here))
    if not day_session:
        raise _fail(here, "day_session_ct is empty")
    evidence = _grade(row.get("evidence"), STATUS_GRADES, f"{here} evidence")
    spec = SessionSpec(valid_from, valid_to, segments, day_session,
                       _text(row.get("source"), f"{here} source"),
                       _text(row.get("note"), f"{here} note", required=False))
    return spec, evidence


def _sessions(payload: dict, where: str) -> tuple[tuple[SessionSpec, ...], dict[date, str]]:
    """The SessionSpec rows, contiguous over the whole coverage; and each unverified spec's
    weekdays inside the coverage (date -> reason)."""
    rows = [_session(r, i, where) for i, r in enumerate(_list(payload.get("sessions"),
                                                              f"{where} sessions"))]
    if not rows:
        raise _fail(where, "has no sessions")
    rows.sort(key=lambda r: r[0].valid_from)
    first, last = HIST_COVERAGE
    if rows[0][0].valid_from > first:
        raise _fail(where, f"sessions start {rows[0][0].valid_from}, after the coverage {first}")
    for i, ((a, a_ev), (b, _)) in enumerate(zip(rows, rows[1:], strict=False)):
        gap = [] if a.valid_to is None else [
            a.valid_to + timedelta(days=k) for k in range(1, (b.valid_from - a.valid_to).days)]
        if a.valid_to is None or a.valid_to >= b.valid_from or any(d.weekday() < 5 for d in gap):
            raise _fail(where, f"sessions from {a.valid_from} and {b.valid_from} overlap or "
                               "leave a gap (they must be contiguous)")
        if gap:  # E.14 lead: a Friday-to-Monday handover is contiguous in trade dates; the
            # weekend between is closed onto the earlier row (no trade date changes).
            rows[i] = (SessionSpec(a.valid_from, b.valid_from - timedelta(days=1), a.segments,
                                   a.day_session_ct, a.source, a.note), a_ev)
    end = rows[-1][0].valid_to
    if end is not None and end < last:
        raise _fail(where, f"sessions end {end}, before the coverage {last}")
    unverified = {}
    for spec, evidence in rows:
        if evidence == UNVERIFIED:
            lo = max(spec.valid_from, first)
            hi = last if spec.valid_to is None else min(spec.valid_to, last)
            unverified.update({d: REASON_SESSION for d in _weekdays(lo, hi)})
    return tuple(r[0] for r in rows), unverified


def _entry(raw: Any, i: int, where: str) -> Holiday | HistLateOpen:
    here = f"{where} entries[{i}]"
    row = _dict(raw, here)
    day = _in_coverage(_day(row.get("day"), here), here)
    if day.weekday() >= 5:
        raise _fail(here, f"{day} is a weekend day (weekends are not entries)")
    name = _text(row.get("name"), f"{here} name")
    kind = row.get("kind")
    if kind not in KINDS:
        raise _fail(here, f"unknown kind {kind!r} (allowed {list(KINDS)})")
    evidence = _grade(row.get("evidence"), STATUS_GRADES, f"{here} evidence")
    time_evidence = _grade(row.get("time_evidence"), TIME_GRADES, f"{here} time_evidence")
    _text(row.get("source"), f"{here} source")
    halt, open_ct = row.get("halt_ct"), row.get("open_ct")
    if kind == FULL_CLOSURE:
        if halt is not None or open_ct is not None or time_evidence != "n/a":
            raise _fail(here, "a full closure has halt_ct and open_ct null and time_evidence n/a")
        return Holiday(day, name, HolidayKind.FULL_CLOSURE, None, evidence, time_evidence)
    if time_evidence == "n/a":
        raise _fail(here, f"a {kind} needs a time grade, not n/a")
    if kind == EARLY_HALT:
        if open_ct is not None:
            raise _fail(here, "an early halt has open_ct null")
        return Holiday(day, name, HolidayKind.EARLY_HALT, _clock(halt, f"{here} halt_ct"),
                       evidence, time_evidence)
    if halt is not None:
        raise _fail(here, "a late open has halt_ct null")
    return HistLateOpen(day, name, _clock(open_ct, f"{here} open_ct"), evidence, time_evidence)


def _entries(payload: dict, where: str) -> list[Holiday | HistLateOpen]:
    out = [_entry(r, i, where) for i, r in enumerate(_list(payload.get("entries"),
                                                           f"{where} entries"))]
    # E.14 lead: a day may hold one holiday entry (full closure or early halt) and one late open,
    # as data/calendars/grains.py's HOLIDAYS and LATE_OPENS both hold the day after Thanksgiving
    # (late open and early halt); a late open beside a full closure, or any other repeat, refuses.
    holiday_days = [e.day for e in out if isinstance(e, Holiday)]
    late_days = [e.day for e in out if isinstance(e, HistLateOpen)]
    closed = {e.day for e in out if isinstance(e, Holiday) and e.kind is HolidayKind.FULL_CLOSURE}
    dup = sorted({d for d in holiday_days if holiday_days.count(d) > 1}
                 | {d for d in late_days if late_days.count(d) > 1}
                 | (set(late_days) & closed))
    if dup:
        raise _fail(where, f"entries repeat day(s) {[str(d) for d in dup]}")
    return out


def _listed_unsourced(payload: dict, where: str) -> dict[date, str]:
    out: dict[date, str] = {}
    for i, raw in enumerate(_list(payload.get("unsourced"), f"{where} unsourced")):
        here = f"{where} unsourced[{i}]"
        row = _dict(raw, here)
        day = _in_coverage(_day(row.get("day"), here), here)
        if day.weekday() >= 5:
            raise _fail(here, f"{day} is a weekend day (never a trade date, never unsourced)")
        if day in out:
            raise _fail(here, f"{day} is listed twice")
        out[day] = _text(row.get("reason"), f"{here} reason")
    return out


def _year_rows(payload: dict, where: str) -> dict[int, dict]:
    out: dict[int, dict] = {}
    for i, raw in enumerate(_list(payload.get("year_coverage"), f"{where} year_coverage")):
        here = f"{where} year_coverage[{i}]"
        row = _dict(raw, here)
        year = row.get("year")
        if not isinstance(year, int) or isinstance(year, bool) or not (
                HIST_COVERAGE[0].year <= year <= HIST_COVERAGE[1].year):
            raise _fail(here, f"year {year!r} is outside the coverage")
        if year in out:
            raise _fail(here, f"year {year} is listed twice")
        _grade(row.get("evidence"), STATUS_GRADES, f"{here} evidence")
        if not isinstance(row.get("complete_exception_list"), bool):
            raise _fail(here, "complete_exception_list must be true or false")
        out[year] = row
    return out


def _sourced_findings(payload: dict, where: str) -> set[date]:
    """Days of no_entry_findings graded cme or secondary (checked and found normal)."""
    out: set[date] = set()
    for i, raw in enumerate(_list(payload.get("no_entry_findings", []),
                                  f"{where} no_entry_findings")):
        here = f"{where} no_entry_findings[{i}]"
        row = _dict(raw, here)
        day = _day(row.get("day"), here)
        if HIST_COVERAGE[0] <= day <= HIST_COVERAGE[1] and row.get("evidence") in SOURCED_GRADES:
            out.add(day)
    return out


# ------------------------------------------------------------------ unsourced ----
def _unsourced(entries: list[Holiday | HistLateOpen], listed: dict[date, str],
               session_unverified: dict[date, str], years: dict[int, dict],
               findings: set[date]) -> dict[date, tuple[str, ...]]:
    reasons: dict[date, list[str]] = {}
    for day in listed:
        reasons.setdefault(day, []).append(REASON_LISTED)
    sourced_days = set(findings)
    for e in entries:
        if e.evidence == UNVERIFIED:
            reasons.setdefault(e.day, []).append(REASON_ENTRY)
        else:
            sourced_days.add(e.day)
    for day in session_unverified:
        reasons.setdefault(day, []).append(REASON_SESSION)
    for day in _weekdays(*HIST_COVERAGE):
        row = years.get(day.year)
        covered = row is not None and row["evidence"] in SOURCED_GRADES \
            and row["complete_exception_list"] is True
        if not covered and day not in sourced_days:
            reasons.setdefault(day, []).append(REASON_YEAR)
    return {d: tuple(r) for d, r in sorted(reasons.items())}


def _counts(holidays: Mapping[date, Holiday], late: Mapping[date, HistLateOpen],
            unsourced: Mapping[date, tuple[str, ...]], file_counts: Any) -> dict[str, Any]:
    weekdays = _weekdays(*HIST_COVERAGE)
    trade = [d for d in weekdays if not (d in holidays and holidays[d].kind
                                         is HolidayKind.FULL_CLOSURE)]
    unsourced_trade = [d for d in trade if d in unsourced]
    by_reason = {r: sum(r in v for v in unsourced.values()) for r in UNSOURCED_REASONS}
    per_year: dict[str, dict[str, int]] = {}
    for d in trade:
        row = per_year.setdefault(str(d.year), {"trade_dates": 0, "unsourced": 0})
        row["trade_dates"] += 1
        row["unsourced"] += d in unsourced
    return {
        "weekdays": len(weekdays), "trade_dates": len(trade),
        "full_closures": sum(h.kind is HolidayKind.FULL_CLOSURE for h in holidays.values()),
        "early_halts": sum(h.kind is HolidayKind.EARLY_HALT for h in holidays.values()),
        "late_opens": len(late),
        "time_unverified_entries": sum(getattr(e, "time_evidence", "") == UNVERIFIED
                                       for e in (*holidays.values(), *late.values())),
        "unsourced": len(unsourced), "unsourced_trade_dates": len(unsourced_trade),
        "unsourced_share_of_trade_dates": (len(unsourced_trade) / len(trade)) if trade else None,
        "unsourced_by_reason": by_reason, "per_year": per_year,
        "file_counts": file_counts if isinstance(file_counts, dict) else None,
    }


def assert_hist_coverage(days: Iterable[date]) -> None:
    """Refuse any date outside 2010-06-01..2019-05-31 (the hist calendars' coverage)."""
    first, last = HIST_COVERAGE
    outside = sorted(d for d in set(days) if not first <= d <= last)
    if outside:
        raise CalendarCoverageError(
            f"{len(outside)} date(s) outside the hist calendar coverage {first}..{last}: "
            f"{outside[0]} .. {outside[-1]}")


# ------------------------------------------------------------------ the loader ----
def parse_hist_calendar(raw: bytes, group: str, path: Path) -> HistGroupCalendar:
    """Validate the bytes of one e14_hist_calendar/1 file and build its calendar."""
    where = Path(path).name
    try:
        payload = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise _fail(where, f"not JSON ({exc})") from exc
    payload = _dict(payload, where)
    products = _header(payload, group, where)
    sessions, session_unverified = _sessions(payload, where)
    entries = _entries(payload, where)
    unsourced = _unsourced(entries, _listed_unsourced(payload, where), session_unverified,
                           _year_rows(payload, where), _sourced_findings(payload, where))
    _dict(payload.get("sources"), f"{where} sources")
    holidays = {e.day: e for e in entries if isinstance(e, Holiday)}
    late = {e.day: e for e in entries if isinstance(e, HistLateOpen)}
    path = Path(path)
    rel = str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)
    return HistGroupCalendar(
        group=group, holidays=holidays, sessions=sessions, coverage=HIST_COVERAGE,
        assert_coverage=assert_hist_coverage, module_paths=(path, MODULE_FILE),
        late_opens=late, scheduled_late_opens={d: e.open_ct for d, e in late.items()},
        unsourced=frozenset(unsourced), unsourced_reasons=unsourced, products=products,
        file_path=rel, file_sha256=hashlib.sha256(raw).hexdigest(),
        counts=_counts(holidays, late, unsourced, payload.get("counts")))


def hist_calendar_path(group: str, base: Path = HIST_CALENDAR_DIR) -> Path:
    if group not in HIST_GROUPS:
        raise HistCalendarError(f"unknown hist calendar group {group!r} (groups "
                                f"{list(HIST_GROUPS)})")
    return Path(base) / f"{group}.json"


def load_hist_group_calendar(group: str, *, base: Path = HIST_CALENDAR_DIR,
                             expected_sha256: str | None = None) -> HistGroupCalendar:
    """The group's hist calendar from ``<base>/<group>.json``. ``expected_sha256``, when given,
    must equal the sha256 of the bytes read (a pinned reader)."""
    path = hist_calendar_path(group, base)
    if not path.is_file():
        raise HistCalendarError(f"{path} does not exist (the lead copies the E.14 calendar "
                                "files there)")
    raw = path.read_bytes()
    cal = parse_hist_calendar(raw, group, path)
    if expected_sha256 is not None and cal.file_sha256 != expected_sha256:
        raise HistCalendarError(f"{path.name}: sha256 {cal.file_sha256[:12]}... is not the "
                                f"expected {expected_sha256[:12]}...")
    return cal


__all__ = [
    "HIST_CALENDAR_DIR", "HIST_CALENDAR_SCHEMA", "HIST_COVERAGE", "HIST_GROUPS",
    "HistCalendarError", "HistGroupCalendar", "HistLateOpen", "UNSOURCED_REASONS",
    "assert_hist_coverage", "hist_calendar_path", "load_hist_group_calendar",
    "parse_hist_calendar",
]
