"""The trigger event record (lead_spec section 2) and the events file it travels in (section 6).

STABLE INTERFACE between the trigger extraction (trigger_hold/events*.py, TriggerCoder) and the
book engine (trigger_hold/units.py, book.py, power.py). A trigger event is the frozen member's
ENTRY EVENT only: (trigger id, trade date d0, decision timestamp tau in ns UTC, side +1 / -1).
Never a fill price, an exit, a mark or a P&L: an events-file row with any other key is refused.

Events file (reports/stage_e23_events/<trigger>__<window>.json), schema "stage_e23_events/1":

    {"schema": "stage_e23_events/1",
     "trigger_id": "<id>",            # the registration config's trigger id
     "root": "<ROOT>",                # one of multiday.constants.ROOTS
     "window": "W_ext" | "W_cf",
     "events": [{"d0": "YYYY-MM-DD", "tau_ns": <int>, "side": 1 | -1}, ...],
     "counts": {"<reason>": <int>, ...},   # no signal, guard, missing bar, halt, ...
     "inputs": {"<role>": {"path": "...", "sha256": "..."}, ...}}
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

EVENTS_SCHEMA = "stage_e23_events/1"
WINDOWS = ("W_ext", "W_cf")
EVENT_KEYS = frozenset({"d0", "tau_ns", "side"})
FILE_KEYS = frozenset({"schema", "trigger_id", "root", "window", "events", "counts", "inputs"})


class EventsError(ValueError):
    """An events record that does not follow the schema (refused, never repaired)."""


@dataclass(frozen=True, order=True)
class TriggerEvent:
    """One entry event of a frozen member: trade date d0, decision instant tau (ns UTC), side."""

    d0: date
    tau_ns: int
    side: int
    trigger_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.d0, date):
            raise EventsError(f"d0 must be a date, got {type(self.d0).__name__}")
        if isinstance(self.tau_ns, bool) or not isinstance(self.tau_ns, int):
            raise EventsError(f"tau_ns must be an int (ns UTC), got {self.tau_ns!r}")
        if isinstance(self.side, bool) or self.side not in (1, -1):
            raise EventsError(f"side must be +1 or -1, got {self.side!r}")
        if not isinstance(self.trigger_id, str) or not self.trigger_id:
            raise EventsError("trigger_id must be a non-empty string")


def event_row(e: TriggerEvent) -> dict[str, Any]:
    return {"d0": e.d0.isoformat(), "tau_ns": int(e.tau_ns), "side": int(e.side)}


def event_from_row(row: Mapping[str, Any], trigger_id: str) -> TriggerEvent:
    keys = set(row)
    if keys != EVENT_KEYS:
        raise EventsError(f"an event row has keys {sorted(keys)}, not {sorted(EVENT_KEYS)}")
    try:
        d0 = date.fromisoformat(str(row["d0"]))
    except ValueError as exc:
        raise EventsError(f"bad d0 {row['d0']!r}") from exc
    return TriggerEvent(d0, row["tau_ns"], row["side"], trigger_id)


@dataclass(frozen=True)
class EventsFile:
    trigger_id: str
    root: str
    window: str
    events: tuple[TriggerEvent, ...]
    counts: Mapping[str, int]
    inputs: Mapping[str, Any]


def events_record(trigger_id: str, root: str, window: str, events: Iterable[TriggerEvent],
                  counts: Mapping[str, int], inputs: Mapping[str, Any]) -> dict[str, Any]:
    evs = sorted(events)
    if any(e.trigger_id != trigger_id for e in evs):
        raise EventsError("every event must carry the file's trigger_id")
    if window not in WINDOWS:
        raise EventsError(f"window {window!r} is not one of {WINDOWS}")
    return {"schema": EVENTS_SCHEMA, "trigger_id": trigger_id, "root": root, "window": window,
            "events": [event_row(e) for e in evs], "counts": dict(sorted(counts.items())),
            "inputs": dict(inputs)}


def parse_events(body: Mapping[str, Any]) -> EventsFile:
    if body.get("schema") != EVENTS_SCHEMA:
        raise EventsError(f"events schema is {body.get('schema')!r}, not {EVENTS_SCHEMA!r}")
    extra = set(body) - FILE_KEYS
    if extra:
        raise EventsError(f"events file has unexpected keys {sorted(extra)}")
    if body.get("window") not in WINDOWS:
        raise EventsError(f"window {body.get('window')!r} is not one of {WINDOWS}")
    tid = str(body["trigger_id"])
    evs = tuple(sorted(event_from_row(r, tid) for r in body.get("events", [])))
    if len(set(evs)) != len(evs):
        raise EventsError(f"{tid}: duplicate events")
    return EventsFile(tid, str(body["root"]), str(body["window"]), evs,
                      dict(body.get("counts") or {}), dict(body.get("inputs") or {}))


def load_events(path: Path) -> EventsFile:
    return parse_events(json.loads(Path(path).read_text(encoding="utf-8")))


def events_on(events: Sequence[TriggerEvent], first: date, last: date) -> list[TriggerEvent]:
    return [e for e in events if first <= e.d0 <= last]


__all__ = ["EVENTS_SCHEMA", "EVENT_KEYS", "WINDOWS", "EventsError", "EventsFile", "TriggerEvent",
           "event_from_row", "event_row", "events_on", "events_record", "load_events",
           "parse_events"]
