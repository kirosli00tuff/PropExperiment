"""The 2010-2019 tables test C1 supplies to the frozen code (calendar files only, never a price).

Every table is built from a file passed by path and sha256 (``load_*`` refuse a missing file, a
wrong sha256 or a malformed payload, ``TableError``):

- ``load_releases``: reports/stage_e14_cal_releases.json, schema "e14_release_calendar/1"
  (coverage, releases[] rows shaped as reports/stage_e2b_release_calendar.json's, cancellations[],
  unsourced[], sources{}, counts). From it:
  * NG's D8 release calendar: a ``screening.stage_e_rules.ReleaseCalendar`` whose ``by_root["NG"]``
    holds the instant of every row of NG's D8 list (NGS, WPSR, FOMC; the list E.2b's calendar gives
    NG), whatever its grade, as E.2b kept its unverified rows (OC-N); coverage = the file's;
  * the K4 NGS table (strategy/members/k4/_releases.py's NGS shape: (ISO date, "HH:MM" CT) per
    row, T = instant_utc in America/Chicago, K4-L-02) less ruling C13's drop rows: every NGS row
    must state ``"drop_actual_differs": true|false`` (the E.5 rule's name, _releases.py header;
    a row without it is refused, so a renamed field cannot silently keep a drop row); true drops
    the row from the K4 table (it stays in the D8 calendar, as E.5's drops did);
  * the dates no release grade covers (ruling C12): every unsourced[] row's date (an unsourced[]
    row gives "date"/"day", or the "id" of a release row, whose date it takes), and the date of
    every D8 row graded neither "official" nor "secondary".
  * a release row with null instant_utc and time_local is accepted ONLY when unsourced[] lists its
    id (lead ruling, Stage E.14; WPSR-2012-11-01, the post-Sandy delayed WPSR): its date is an
    unsourced release date and no instant of it reaches the frozen code (nor the K4 NGS table).
    Any other null instant is refused.
- ``load_full_sessions``: reports/stage_e14_cal_energy_full_sessions.json (key
  ENERGY_FULL_SESSIONS, ISO dates). It must equal the rule of strategy/members/k4/_calendar.py
  ("every energy trade date ... whose early_halt_ct is None") recomputed on the pinned hist energy
  calendar over the file's own range, else it is refused.
- ``h1_rows``: Topstep flatten rows by Rule H-1 (rules/sessions.py lines 20-40) from the hist
  equity calendar: a full closure -> "markets closed", an early halt at h -> close-by h - 30 min;
  every July 3 unsettled (no row); a late open gets no row; only days before
  rules.sessions.TOPSTEP_DERIVED_FIRST (2019-05-01), where E.5's derived rows begin.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time
from pathlib import Path
from types import MappingProxyType
from typing import Any
from zoneinfo import ZoneInfo

from c1_replication.constants import (
    D8_RELEASES,
    FULL_SESSIONS_KEY,
    H1_LEAD,
    H1_SOURCE,
    H1_UNSETTLED,
    NGS,
    RELEASE_GRADES_SOURCED,
    RELEASE_SCHEMA,
    VEHICLE,
)

CT = ZoneInfo("America/Chicago")
NS_PER_S = 1_000_000_000
NS_PER_MIN = 60 * NS_PER_S
GRADES = ("official", "secondary", "unverified")
DROP_FIELD = "drop_actual_differs"


class TableError(ValueError):
    """A C1 calendar input is missing, not the pinned file, or malformed."""


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_pinned(path: Path, expected_sha256: str, what: str) -> bytes:
    """The file's bytes when it exists and hashes to ``expected_sha256``."""
    path = Path(path)
    if not path.is_file():
        raise TableError(f"{what} {path} does not exist")
    raw = path.read_bytes()
    got = sha256_bytes(raw)
    if got != expected_sha256:
        raise TableError(f"{what} {path.name}: sha256 {got[:12]}... is not the expected "
                         f"{str(expected_sha256)[:12]}...")
    return raw


def _json(raw: bytes, what: str) -> dict:
    try:
        doc = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TableError(f"{what}: not JSON ({exc})") from exc
    if not isinstance(doc, dict):
        raise TableError(f"{what}: not a JSON object")
    return doc


def _day(value: Any, what: str) -> date:  # noqa: ANN401
    if not isinstance(value, str) or len(value) != 10:
        raise TableError(f"{what}: {value!r} is not an ISO date")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise TableError(f"{what}: {value!r} is not an ISO date") from exc


# ------------------------------------------------------------------ releases ----
@dataclass(frozen=True)
class HistReleases:
    calendar: Any  # screening.stage_e_rules.ReleaseCalendar (NG only)
    ngs_table: tuple[tuple[str, str], ...]  # (ISO date, "HH:MM" CT), C13 drops removed
    ngs_dropped: tuple[str, ...]
    unsourced: Mapping[date, tuple[str, ...]]  # date -> reasons (ruling C12)
    counts: Mapping[str, Any] = field(default_factory=dict)
    path: str = ""
    sha256: str = ""

    def record(self) -> dict[str, Any]:
        return {"path": self.path, "sha256": self.sha256, "counts": dict(self.counts),
                "ngs_dropped": list(self.ngs_dropped),
                "unsourced_dates": sorted(d.isoformat() for d in self.unsourced)}


def _instant(row: Mapping[str, Any], what: str) -> datetime:
    text = row.get("instant_utc")
    if not isinstance(text, str):
        raise TableError(f"{what}: no instant_utc")
    try:
        when = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise TableError(f"{what}: instant_utc {text!r} is not ISO 8601") from exc
    if when.tzinfo is None:
        raise TableError(f"{what}: instant_utc {text!r} is not timezone-aware")
    when = when.astimezone(UTC)
    if when.second or when.microsecond:
        raise TableError(f"{what}: instant_utc {text!r} is not on a minute")
    return when


def _listed_ids(doc: Mapping[str, Any], where: str) -> frozenset[str]:
    """The release ids unsourced[] names (rows of the form {"id", "what", "reason"})."""
    ids = set()
    for j, row in enumerate(doc.get("unsourced", [])):
        if not isinstance(row, dict):
            raise TableError(f"{where}: unsourced[{j}] is not an object")
        if isinstance(row.get("id"), str):
            ids.add(row["id"])
    return frozenset(ids)


def _release_row(row: Any, i: int, cov: tuple[date, date], listed: frozenset[str]  # noqa: ANN401
                 ) -> tuple[str, date, datetime | None, str, bool]:
    """(release, date, instant or None, grade, C13 drop). The instant is None only for a row
    with null instant_utc and time_local that unsourced[] lists by id (lead ruling, Stage
    E.14); any other missing instant is refused."""
    what = f"releases[{i}]"
    if not isinstance(row, dict):
        raise TableError(f"{what}: not an object")
    kind, grade = row.get("release"), row.get("evidence")
    if not isinstance(kind, str) or not kind:
        raise TableError(f"{what}: no release name")
    if grade not in GRADES:
        raise TableError(f"{what} ({row.get('id')}): evidence {grade!r} is not one of {GRADES}")
    day = _day(row.get("date"), f"{what} date")
    untimed = row.get("instant_utc") is None and row.get("time_local") is None
    if untimed and row.get("id") in listed:
        when = None
    elif row.get("instant_utc") is None:
        raise TableError(f"{what} ({row.get('id')}): no instant_utc (a null time is accepted "
                         "only for a row that unsourced[] lists by id)")
    else:
        when = _instant(row, what)
        tz = row.get("tz")
        if isinstance(tz, str) and when.astimezone(ZoneInfo(tz)).date() != day:
            raise TableError(f"{what} ({row.get('id')}): instant {when.isoformat()} is not on "
                             f"{day} in {tz}")
    if not cov[0] <= day <= cov[1]:
        raise TableError(f"{what} ({row.get('id')}): {day} outside the coverage {cov[0]}..{cov[1]}")
    drop = row.get(DROP_FIELD, None if kind == NGS else False)
    if not isinstance(drop, bool):
        raise TableError(f"{what} ({row.get('id')}): {DROP_FIELD} must be true or false (every "
                         "NGS row states it, ruling C13)")
    return kind, day, when, grade, drop


def parse_releases(raw: bytes, path: Path) -> HistReleases:
    """The NG tables of one e14_release_calendar/1 file (module docstring)."""
    from screening.stage_e_rules import ReleaseCalendar

    where = Path(path).name
    doc = _json(raw, where)
    if doc.get("schema") != RELEASE_SCHEMA:
        raise TableError(f"{where}: schema {doc.get('schema')!r} is not {RELEASE_SCHEMA!r}")
    cov_raw = doc.get("coverage")
    if not isinstance(cov_raw, dict):
        raise TableError(f"{where}: no coverage")
    cov = (_day(cov_raw.get("first"), f"{where} coverage"),
           _day(cov_raw.get("last"), f"{where} coverage"))
    rows = doc.get("releases")
    if not isinstance(rows, list) or not rows:
        raise TableError(f"{where}: no releases")
    for key in ("cancellations", "unsourced"):
        if not isinstance(doc.get(key, []), list):
            raise TableError(f"{where}: {key} is not a list")
    listed = _listed_ids(doc, where)
    instants: set[int] = set()
    ngs: dict[str, str] = {}
    dropped: list[str] = []
    ngs_untimed: list[str] = []
    unsourced: dict[date, list[str]] = {}
    per_kind: dict[str, int] = {}
    by_id: dict[str, tuple[str, date]] = {}
    for i, row in enumerate(rows):
        kind, day, when, grade, drop = _release_row(row, i, cov, listed)
        if isinstance(row.get("id"), str):
            by_id[row["id"]] = (kind, day)
        if kind not in D8_RELEASES:
            continue
        per_kind[kind] = per_kind.get(kind, 0) + 1
        if grade not in RELEASE_GRADES_SOURCED:
            unsourced.setdefault(day, []).append(f"{kind} graded {grade}")
        if kind == NGS:
            iso = day.isoformat()
            if iso in ngs or iso in dropped or iso in ngs_untimed:
                raise TableError(f"{where}: two NGS rows on {iso}")
        if when is None:  # listed by id in unsourced[]: its date is excluded (C12), no instant
            if kind == NGS:
                ngs_untimed.append(day.isoformat())
            continue
        instants.add(int(when.timestamp()) * NS_PER_S)
        if kind == NGS:
            if drop:
                dropped.append(day.isoformat())
            else:
                ngs[day.isoformat()] = when.astimezone(CT).strftime("%H:%M")
    for j, row in enumerate(doc.get("unsourced", [])):
        if "date" in row or "day" in row:
            kind = row.get("release")
            day = _day(row.get("date", row.get("day")), f"{where} unsourced[{j}]")
        elif isinstance(row.get("id"), str):
            if row["id"] not in by_id:
                raise TableError(f"{where}: unsourced[{j}] names {row['id']!r}, which no "
                                 "release row has")
            kind, day = by_id[row["id"]]
        else:
            raise TableError(f"{where}: unsourced[{j}] has neither a date nor a release id")
        if kind is not None and kind not in D8_RELEASES:
            continue
        unsourced.setdefault(day, []).append(
            f"{kind or 'release'} unsourced ({row.get('what', 'release')}): "
            f"{row.get('reason', '')}"[:200])
    cal = ReleaseCalendar(MappingProxyType({VEHICLE: tuple(sorted(instants))}), (), cov[0],
                          cov[1], sha256_bytes(raw), where)
    counts = {"d8_rows": sum(per_kind.values()), "d8_rows_by_release": dict(sorted(
        per_kind.items())), "d8_instants": len(instants), "ngs_table_rows": len(ngs),
        "ngs_dropped_c13": len(dropped), "ngs_untimed_listed": len(ngs_untimed),
        "untimed_rows_listed": sum(1 for r in rows if isinstance(r, dict)
                                   and r.get("instant_utc") is None),
        "unsourced_or_unverified_dates": len(unsourced),
        "cancellations": len(doc.get("cancellations", []))}
    return HistReleases(cal, tuple(sorted(ngs.items())), tuple(sorted(dropped)),
                        MappingProxyType({d: tuple(v) for d, v in sorted(unsourced.items())}),
                        MappingProxyType(counts), str(path), sha256_bytes(raw))


def load_releases(path: Path, expected_sha256: str) -> HistReleases:
    return parse_releases(read_pinned(path, expected_sha256, "release calendar"), Path(path))


# ------------------------------------------------------------------ full sessions ----
def full_sessions_rule(energy: Any, first: date, last: date) -> tuple[str, ...]:  # noqa: ANN401
    """k4/_calendar.py's rule on a calendar: trade dates in [first, last] with no early halt."""
    from data.group_session import trade_dates_between

    return tuple(d.isoformat() for d in trade_dates_between(energy, first, last)
                 if energy.early_halt_ct(d) is None)


def parse_full_sessions(raw: bytes, path: Path, energy: Any) -> tuple[str, ...]:  # noqa: ANN401
    where = Path(path).name
    doc = _json(raw, where)
    days = doc.get(FULL_SESSIONS_KEY)
    rng = doc.get("range")
    if not isinstance(days, list) or not days or not isinstance(rng, dict):
        raise TableError(f"{where}: no {FULL_SESSIONS_KEY} list or no range")
    first, last = _day(rng.get("first"), f"{where} range"), _day(rng.get("last"), f"{where} range")
    listed = tuple(str(d) for d in days)
    if list(listed) != sorted(set(listed)):
        raise TableError(f"{where}: {FULL_SESSIONS_KEY} is not sorted and distinct")
    src = doc.get("source_sha256")
    if src is not None and src != getattr(energy, "file_sha256", None):
        raise TableError(f"{where}: derived from energy calendar sha256 {str(src)[:12]}..., not "
                         f"the pinned {str(getattr(energy, 'file_sha256', ''))[:12]}...")
    want = full_sessions_rule(energy, first, last)
    if listed != want:
        diff = sorted(set(listed) ^ set(want))
        raise TableError(f"{where}: {len(diff)} dates differ from the rule recomputed on the "
                         f"energy calendar (first {diff[0] if diff else '?'})")
    return listed


def load_full_sessions(path: Path, expected_sha256: str, energy: Any) -> tuple[str, ...]:  # noqa: ANN401
    raw = read_pinned(path, expected_sha256, "energy full sessions")
    return parse_full_sessions(raw, Path(path), energy)


# ------------------------------------------------------------------ Rule H-1 ----
def _minus(at: time, lead: Any) -> time:  # noqa: ANN401
    return (datetime.combine(date(2000, 1, 3), at) - lead).time()


def h1_rows(equity: Any) -> dict[date, Any]:  # noqa: ANN401
    """Topstep rows by Rule H-1 from a hist equity calendar (module docstring)."""
    from data.cme_calendar import HolidayKind
    from rules.sessions import TOPSTEP_DERIVED_FIRST, TopstepHoliday

    out = {}
    for day, hol in sorted(equity.holidays.items()):
        if day >= TOPSTEP_DERIVED_FIRST or (day.month, day.day) == H1_UNSETTLED:
            continue
        if day.weekday() >= 5:
            continue
        if hol.kind is HolidayKind.FULL_CLOSURE:
            out[day] = TopstepHoliday(day, None, H1_SOURCE)
        elif hol.kind is HolidayKind.EARLY_HALT:
            if hol.halt_ct is None:
                raise TableError(f"equity {day}: early halt without a time")
            out[day] = TopstepHoliday(day, _minus(hol.halt_ct, H1_LEAD), H1_SOURCE)
    return out


def h1_unsettled(equity: Any) -> tuple[date, ...]:  # noqa: ANN401
    """The equity entries Rule H-1 leaves without a row (July 3 and late opens)."""
    from rules.sessions import TOPSTEP_DERIVED_FIRST

    hol = [d for d in equity.holidays if d < TOPSTEP_DERIVED_FIRST
           and (d.month, d.day) == H1_UNSETTLED]
    late = [d for d in getattr(equity, "late_opens", {}) if d < TOPSTEP_DERIVED_FIRST]
    return tuple(sorted(set(hol) | set(late)))


__all__ = ["DROP_FIELD", "HistReleases", "TableError", "full_sessions_rule", "h1_rows",
           "h1_unsettled", "load_full_sessions", "load_releases", "parse_full_sessions",
           "parse_releases", "read_pinned", "sha256_bytes"]
