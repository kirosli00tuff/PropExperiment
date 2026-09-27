"""Source checks of the release calendar assembler (Stage E.2b, lead rulings OC-J and OC-N).

Used by screening.build_release_calendar (which re-exports these names):
- ``check_source``: the source is final (its log does not say "STATUS: DRAFT"), covers
  2019-05-01..2026-06-21, lists only the releases the lead assigned to it, and has a coverage
  table (release x year) with expected = found + unverified + cancelled that the entries and the
  cancellation records reproduce; every move points to an entry;
- ``verify_entries``: every entry's quote occurs verbatim (whitespace normalised) in its saved
  page (strict UTF-8, a relative path inside the repository) and its instant_utc equals date +
  time_local in tz (zoneinfo; a local time in a DST gap fails);
- ``verify_evidence``: every cancellation's and move's evidence quote occurs in its page.
Any failure raises CalendarBuildRefused naming the case.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from datetime import UTC, date, datetime, time
from pathlib import Path, PurePosixPath
from typing import Any
from zoneinfo import ZoneInfo

COVERAGE_FIRST = "2019-05-01"
COVERAGE_LAST = "2026-06-21"
YEARS: tuple[str, ...] = tuple(str(y) for y in range(2019, 2027))
DRAFT_MARK = "STATUS: DRAFT"
UNVERIFIED_MARK = "[unverified]"
ANNOUNCED = "announced_schedule"


class CalendarBuildRefused(RuntimeError):
    """The calendar cannot be built as the rulings define it; the message names the case."""


def _refuse(message: str) -> CalendarBuildRefused:
    return CalendarBuildRefused(message)


# ----------------------------------------------------------------- sources ----
def evidence_of(entry: Mapping[str, Any]) -> str:
    if UNVERIFIED_MARK in (entry.get("note") or ""):
        return "unverified"
    kind = entry.get("evidence_kind")
    if kind is None:
        return "verified"
    if kind == ANNOUNCED:
        return ANNOUNCED
    raise _refuse(f"{entry.get('id')}: unknown evidence_kind {kind!r}")


def _cancel_year(cancel: Mapping[str, Any]) -> str:
    m = re.match(r"(\d{4})-\d{2}-\d{2}", cancel.get("originally_scheduled") or "")
    if m is None:
        m = re.search(r"\b(20\d{2})\b", cancel.get("reference_period") or "")
    if m is None:
        raise _refuse(f"cancellation {cancel.get('release')} {cancel.get('reference_period')!r} "
                      "has no year")
    return m.group(1)


def check_source(name: str, source: Mapping[str, Any], log_text: str,
                 release_source: Mapping[str, str]) -> None:
    """Final, full coverage, and a coverage table the entries and cancellations reproduce;
    ``release_source`` is the lead's release code -> source name table."""
    if DRAFT_MARK in log_text:
        raise _refuse(f"source {name}: its log still says {DRAFT_MARK!r}")
    if source.get("coverage") != {"first": COVERAGE_FIRST, "last": COVERAGE_LAST}:
        raise _refuse(f"source {name}: coverage {source.get('coverage')} is not "
                      f"{COVERAGE_FIRST}..{COVERAGE_LAST}")
    entries, table = source["entries"], source["coverage_table"]
    for code in set(table) | {e["release"] for e in entries}:
        if release_source.get(code) != name:
            raise _refuse(f"source {name}: release {code!r} is not one the lead assigned to it")
        if code not in table:
            raise _refuse(f"source {name}: release {code} has entries but no coverage table")
    found = Counter((e["release"], e["date"][:4]) for e in entries
                    if evidence_of(e) != "unverified")
    unverified = Counter((e["release"], e["date"][:4]) for e in entries
                         if evidence_of(e) == "unverified")
    cancelled = Counter((c["release"], _cancel_year(c)) for c in source["cancellations"])
    for code, years in table.items():
        if set(years) != set(YEARS):
            raise _refuse(f"source {name}: {code}'s coverage table years {sorted(years)}")
        for year, row in years.items():
            f, u, c = row["found"], row["unverified"], row["cancelled"]
            if row["expected"] != f + u + c:
                raise _refuse(f"source {name}: {code} {year} expects {row['expected']} releases, "
                              f"but found {f} + unverified {u} + cancelled {c}")
            recount = (found[(code, year)], unverified[(code, year)], cancelled[(code, year)])
            if (f, u, c) != recount:
                raise _refuse(f"source {name}: {code} {year} table (found, unverified, cancelled) "
                              f"{(f, u, c)} but the entries give {recount}")
    ids = {e["id"] for e in entries}
    for move in source.get("moves", ()):
        if move["entry_id"] not in ids:
            raise _refuse(f"source {name}: move to {move['entry_id']} has no entry")


# ------------------------------------------------------------ verification ----
def _normalise(text: str) -> str:
    return " ".join(text.split())


def _page_path(page_root: Path, saved_path: str) -> Path:
    rel = PurePosixPath(saved_path)
    if rel.is_absolute() or ".." in rel.parts or not rel.parts:
        raise _refuse(f"saved_path {saved_path!r} is not a relative path inside the repository")
    return Path(page_root).joinpath(*rel.parts)


class Pages:
    """Normalised page texts, read once each (strict UTF-8)."""

    def __init__(self, page_root: Path) -> None:
        self._root = Path(page_root)
        self._cache: dict[str, str] = {}

    def contains(self, saved_path: str, quote: str) -> bool:
        if saved_path not in self._cache:
            path = _page_path(self._root, saved_path)
            if not path.is_file():
                raise _refuse(f"saved page {saved_path} does not exist")
            self._cache[saved_path] = _normalise(path.read_bytes().decode("utf-8"))
        needle = _normalise(quote)
        return bool(needle) and needle in self._cache[saved_path]


def instant_matches(entry: Mapping[str, Any]) -> bool:
    """instant_utc (ISO 8601, Z) equals date + time_local in tz; the local time exists."""
    text = entry["instant_utc"]
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", text):
        return False
    if not re.fullmatch(r"\d{2}:\d{2}", entry["time_local"]):
        return False
    local = datetime.combine(date.fromisoformat(entry["date"]),
                             time.fromisoformat(entry["time_local"]), tzinfo=ZoneInfo(entry["tz"]))
    utc = local.astimezone(UTC)
    if utc.astimezone(ZoneInfo(entry["tz"])).replace(tzinfo=None) != local.replace(tzinfo=None):
        return False  # a local time inside a DST gap
    return utc == datetime.fromisoformat(text.replace("Z", "+00:00"))


def verify_entries(entries: Sequence[Mapping[str, Any]], pages: Pages) -> dict[str, int]:
    failures: list[str] = []
    counts = Counter()
    for e in entries:
        counts["instants_checked"] += 1
        if instant_matches(e):
            counts["instants_ok"] += 1
        else:
            failures.append(f"{e['id']}: instant {e['instant_utc']} != {e['date']} "
                            f"{e['time_local']} {e['tz']}")
        if not e.get("quote"):
            failures.append(f"{e['id']}: no quote")
            continue
        counts["quotes_checked"] += 1
        if pages.contains(e["saved_path"], e["quote"]):
            counts["quotes_ok"] += 1
        else:
            failures.append(f"{e['id']}: quote not in {e['saved_path']}")
    if failures:
        raise _refuse(f"{len(failures)} entry check(s) failed: " + "; ".join(failures[:20]))
    return dict(counts)


def _evidence_items(record: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
    for key in ("evidence", "evidence_original", "evidence_published"):
        value = record.get(key)
        if value is None:
            continue
        yield from (value if isinstance(value, list) else [value])


def verify_evidence(sources: Mapping[str, Mapping[str, Any]], pages: Pages) -> dict[str, int]:
    """Every cancellation's and move's evidence quote (items marked found: false are claims of
    absence and carry no quote to check)."""
    failures, counts = [], Counter()
    for name, source in sources.items():
        for kind in ("cancellations", "moves"):
            for record in source.get(kind, ()):
                for item in _evidence_items(record):
                    if item.get("found") is False:
                        counts["evidence_not_found_items"] += 1
                        continue
                    counts["evidence_quotes_checked"] += 1
                    if item.get("quote") and pages.contains(item["saved_path"], item["quote"]):
                        counts["evidence_quotes_ok"] += 1
                    else:
                        failures.append(f"{name} {kind} {record.get('release')} "
                                        f"{record.get('reference_period')}")
    if failures:
        raise _refuse(f"{len(failures)} evidence quote(s) failed: " + "; ".join(failures[:20]))
    return dict(counts)

