"""V2.3 member signal of K9-anncday-01, the EC-K9 announcement-day flag (V23 item 8; design V2.3).

Source: reports/stage_e10_catalog_K9.json members[0] (K9-anncday-01): condition "trade date d is
in the EC-K9 announcement date set"; vehicles MNQ, M2K, MYM (members[0].vehicles); decision time
"known in advance from official schedules, fixed before the 17:59 CT entry intent on the evening
before d" (members[0].decision_time_ct). No released value is read.

- ``k9_anncday`` (kind "flag", not normalized; family K9-anncday-01; cluster "K9", a cluster with
  no vehicle of constants.UNIVERSE: the spec's cluster is a label only, the panel's identifier
  one-hots come from the rows): 1.0 iff the row's trade date is in the EC-K9 date set, else 0.0,
  on every row of MNQ, M2K and MYM whose trade date a date set covers. Not applicable (0, flag 0):
  other vehicles' rows, trade dates outside both windows, and trade dates inside a span the
  training file marks uncovered.
- Availability: ENTRY_INTENT_MIN (17:59 CT) on the calendar day before the trade date, the
  member's entry intent, at which the schedule is known; earlier than every V2.2 decision time.
- Date sets (each window's own source; the windows do not overlap):
  - research window (the catalog's research_window start..end): the union of the five
    members[0].event_dates lists in EVENT_KEYS;
  - training window: TRAIN_CALENDAR_PATH (schema "ec_k9/1", written by the E.12 calendar
    builder): its "date_set", checked equal to the union of its five "event_dates" lists and
    inside its "window" (else K9CalendarError), and its "uncovered_spans".
- While TRAIN_CALENDAR_PATH is absent, training-window rows of the three vehicles are not
  applicable and K9CalendarMissing (a warning) is issued; ``training_calendar_present()`` lets a
  caller require the file (a real-data run must).
The path constants are read at call time, so a test can point them at a fixture file.
"""

from __future__ import annotations

import hashlib
import json
import warnings
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

from data.config import REPO_ROOT
from ml_route_v2.signals._core import (
    SignalContext,
    SignalSpec,
    ct_ns,
    day_set,
    empty,
    epoch_day,
    in_days,
    result,
    rows_of,
)

FAMILY = "K9-anncday-01"
CATALOG_PATH = REPO_ROOT / "reports" / "stage_e10_catalog_K9.json"
TRAIN_CALENDAR_PATH = REPO_ROOT / "reports" / "stage_e12_ec_k9_2019_2024.json"
TRAIN_SCHEMA = "ec_k9/1"
TRAIN_WINDOW = ("2019-05-01", "2024-02-29")
EVENT_KEYS = ("FOMC", "NFP", "GDP_first_last", "ISM_manufacturing_scheduled",
              "inflation_earlier_of_CPI_PPI_by_reference_month")
VEHICLES = ("MNQ", "M2K", "MYM")  # members[0].vehicles (Nasdaq-100, Russell 2000, Dow)
ENTRY_INTENT_MIN = 17 * 60 + 59  # 17:59 CT on the evening before d (members[0].decision_time_ct)


class K9CalendarError(ValueError):
    """An EC-K9 date-set file breaks its schema or its own consistency checks."""


class K9CalendarMissing(UserWarning):
    """The training-window EC-K9 file is absent: training-window rows are not applicable."""


@dataclass(frozen=True)
class DateSet:
    first: int  # epoch day, inclusive
    last: int  # epoch day, inclusive
    dates: np.ndarray  # sorted unique epoch days
    uncovered: tuple[tuple[int, int], ...]  # inclusive epoch-day spans
    source: str  # path and sha256

    def covers(self, days: np.ndarray) -> np.ndarray:
        d = np.asarray(days, dtype=np.int64)
        ok = (d >= self.first) & (d <= self.last)
        for lo, hi in self.uncovered:
            ok &= ~((d >= lo) & (d <= hi))
        return ok


def _iso_list(values: object, what: str) -> list[str]:
    if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
        raise K9CalendarError(f"{what}: a list of ISO date strings expected")
    for v in values:
        try:
            epoch_day(v)
        except ValueError as exc:
            raise K9CalendarError(f"{what}: {v!r} is not an ISO date") from exc
    return values


def _union(event_dates: object, what: str) -> set[str]:
    if not isinstance(event_dates, dict):
        raise K9CalendarError(f"{what}: event_dates is not an object")
    missing = [k for k in EVENT_KEYS if k not in event_dates]
    if missing:
        raise K9CalendarError(f"{what}: event_dates lacks {missing}")
    out: set[str] = set()
    for k in EVENT_KEYS:
        out |= set(_iso_list(event_dates[k], f"{what} event_dates.{k}"))
    return out


def _read(path: Path) -> tuple[dict, str]:
    blob = path.read_bytes()
    return json.loads(blob), f"{path} sha256 {hashlib.sha256(blob).hexdigest()}"


@lru_cache(maxsize=8)
def _research_set(path: str, _stamp: tuple[int, int]) -> DateSet:
    raw, source = _read(Path(path))
    member = raw["members"][0]
    if member.get("id") != FAMILY:
        raise K9CalendarError(f"{path}: members[0] is {member.get('id')!r}, not {FAMILY}")
    if set(member["vehicles"].values()) != set(VEHICLES):
        raise K9CalendarError(f"{path}: members[0].vehicles {member['vehicles']} != {VEHICLES}")
    window = raw["research_window"]
    first, last = epoch_day(window["start"]), epoch_day(window["end"])
    dates = day_set(sorted(_union(member["event_dates"], path)))
    if len(dates) and (dates[0] < first or dates[-1] > last):
        raise K9CalendarError(f"{path}: an event date lies outside the research window")
    return DateSet(first, last, dates, (), source)


@lru_cache(maxsize=8)
def _training_set(path: str, _stamp: tuple[int, int]) -> DateSet:
    raw, source = _read(Path(path))
    if raw.get("schema") != TRAIN_SCHEMA:
        raise K9CalendarError(f"{path}: schema {raw.get('schema')!r}, not {TRAIN_SCHEMA!r}")
    if tuple(raw.get("window") or ()) != TRAIN_WINDOW:
        raise K9CalendarError(f"{path}: window {raw.get('window')!r}, not {list(TRAIN_WINDOW)}")
    listed = _iso_list(raw.get("date_set"), f"{path} date_set")
    if listed != sorted(set(listed)):
        raise K9CalendarError(f"{path}: date_set is not sorted and unique")
    union = _union(raw.get("event_dates"), path)
    if set(listed) != union:
        raise K9CalendarError(f"{path}: date_set differs from the union of the five event lists "
                              f"({len(set(listed) - union)} extra, {len(union - set(listed))} "
                              "missing)")
    first, last = epoch_day(TRAIN_WINDOW[0]), epoch_day(TRAIN_WINDOW[1])
    dates = day_set(listed)
    if len(dates) and (dates[0] < first or dates[-1] > last):
        raise K9CalendarError(f"{path}: a date_set entry lies outside the window")
    raw_spans = raw.get("uncovered_spans")
    if not isinstance(raw_spans, list):
        raise K9CalendarError(f"{path}: uncovered_spans is not a list")
    spans = []
    for span in raw_spans:
        if not isinstance(span, list) or len(span) != 2:
            raise K9CalendarError(f"{path}: bad uncovered span {span!r}")
        lo, hi = _iso_list(span, f"{path} uncovered_spans")
        if epoch_day(lo) > epoch_day(hi):
            raise K9CalendarError(f"{path}: bad uncovered span {span!r}")
        spans.append((epoch_day(lo), epoch_day(hi)))
    return DateSet(first, last, dates, tuple(spans), source)


def _stamp(path: Path) -> tuple[int, int]:
    st = path.stat()
    return st.st_mtime_ns, st.st_size


def research_dates(path: Path | None = None) -> DateSet:
    p = Path(CATALOG_PATH if path is None else path)
    return _research_set(str(p), _stamp(p))


def training_calendar_present(path: Path | None = None) -> bool:
    return Path(TRAIN_CALENDAR_PATH if path is None else path).exists()


def training_dates(path: Path | None = None) -> DateSet | None:
    """The training-window date set, or None while the file is absent."""
    p = Path(TRAIN_CALENDAR_PATH if path is None else path)
    if not p.exists():
        return None
    return _training_set(str(p), _stamp(p))


def _in_training_window(days: np.ndarray) -> np.ndarray:
    return (days >= epoch_day(TRAIN_WINDOW[0])) & (days <= epoch_day(TRAIN_WINDOW[1]))


def _anncday(ctx: SignalContext) -> pd.DataFrame:
    view = rows_of(ctx)
    value, app, avail = empty(view)
    rows = view.where_root(VEHICLES)
    if len(rows):
        train = training_dates()
        if train is None and _in_training_window(view.day[rows]).any():
            warnings.warn(K9CalendarMissing(
                f"{TRAIN_CALENDAR_PATH} is absent: k9_anncday is not applicable on the "
                "training window"), stacklevel=2)
        for ds in (research_dates(), train):
            if ds is None:
                continue
            r = rows[ds.covers(view.day[rows])]
            value[r] = in_days(view.day[r], ds.dates).astype(np.float64)
            app[r] = True
            avail[r] = ct_ns(view.day[r], ENTRY_INTENT_MIN, day_offset=-1)
    return result(view, value, app, avail)


SPECS = (
    SignalSpec("k9_anncday", FAMILY, "K9", "flag",
               "reports/stage_e10_catalog_K9.json members[0] (condition, vehicles, "
               "decision_time_ct, event_dates); reports/stage_e12_ec_k9_2019_2024.json", (),
               False, _anncday),
)

__all__ = ["CATALOG_PATH", "ENTRY_INTENT_MIN", "EVENT_KEYS", "FAMILY", "SPECS",
           "TRAIN_CALENDAR_PATH", "TRAIN_SCHEMA", "TRAIN_WINDOW", "VEHICLES", "DateSet",
           "K9CalendarError", "K9CalendarMissing", "research_dates", "training_calendar_present",
           "training_dates"]
