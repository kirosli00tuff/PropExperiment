"""The registration config (written by the lead before the freeze; schema
"stage_e23_registration/1"), reports/stage_e23_registration.json:

    {"schema": "stage_e23_registration/1",
     "registry_test": "E23",
     "n_before": 533,
     "trigger_holds": [
       {"id": "E23-<trigger>-h5",          # the registry id, unique, "E23-" prefix
        "trigger_id": "<trigger>",          # the events files' trigger_id
        "root": "NQ",                       # one of multiday.constants.ROOTS
        "m": 1,                             # +1 the member's side, -1 the opposite (section 2)
        "h": 5,                             # 5 or 20 mark dates
        "s_x": "2019-05-06" | null,         # the trigger's declared W_cf start S_X, if any
        "events": {"W_ext": "reports/stage_e23_events/<trigger>__W_ext.json",
                   "W_cf": "reports/stage_e23_events/<trigger>__W_cf.json" | null}},
       ...]}

At most 24 trigger-holds (P2.5). Every events file must name the same trigger_id, root and
window as the row that cites it (checked when loaded).
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from trigger_hold import constants as K
from trigger_hold.types import EventsFile, load_events

MAX_TRIGGER_HOLDS = 24
ROW_KEYS = frozenset({"id", "trigger_id", "root", "m", "h", "s_x", "events"})


class ConfigError(ValueError):
    """The registration config does not follow the schema (refused before any marker)."""


@dataclass(frozen=True)
class TriggerHold:
    id: str
    trigger_id: str
    root: str
    m: int
    h: int
    s_x: date | None
    events: Mapping[str, str | None]

    def events_file(self, window: str) -> EventsFile | None:
        path = self.events.get(window)
        if not path:
            return None
        ev = load_events(K.repo_path(path))
        if (ev.trigger_id, ev.root, ev.window) != (self.trigger_id, self.root, window):
            raise ConfigError(f"{self.id}: events file {path} is ({ev.trigger_id}, {ev.root}, "
                              f"{ev.window}), not ({self.trigger_id}, {self.root}, {window})")
        return ev


@dataclass(frozen=True)
class Config:
    registry_test: str
    n_before: int
    rows: tuple[TriggerHold, ...]

    @property
    def ids(self) -> list[str]:
        return [r.id for r in self.rows]

    @property
    def roots(self) -> list[str]:
        return [r for r in K.ROOTS if any(t.root == r for t in self.rows)]

    def event_paths(self) -> list[str]:
        return sorted({p for r in self.rows for p in r.events.values() if p})


def _row(raw: Mapping[str, Any]) -> TriggerHold:
    if set(raw) != ROW_KEYS:
        raise ConfigError(f"a trigger-hold row has keys {sorted(raw)}, not {sorted(ROW_KEYS)}")
    tid, rid = str(raw["trigger_id"]), str(raw["id"])
    if not rid.startswith(f"{K.REGISTRY_TEST}-"):
        raise ConfigError(f"id {rid!r} does not start with {K.REGISTRY_TEST}-")
    if raw["root"] not in K.ROOTS:
        raise ConfigError(f"{rid}: root {raw['root']!r} is not an E.21 root")
    if raw["m"] not in K.DIRECTIONS or isinstance(raw["m"], bool):
        raise ConfigError(f"{rid}: m must be +1 or -1")
    if raw["h"] not in K.HOLDS or isinstance(raw["h"], bool):
        raise ConfigError(f"{rid}: h must be one of {K.HOLDS}")
    ev = raw["events"]
    if not isinstance(ev, Mapping) or set(ev) != set(K.WINDOW_NAMES) or not ev.get(K.W_EXT):
        raise ConfigError(f"{rid}: events must name a W_ext file and a W_cf file or null")
    s_x = date.fromisoformat(raw["s_x"]) if raw["s_x"] else None
    return TriggerHold(rid, tid, str(raw["root"]), int(raw["m"]), int(raw["h"]), s_x, dict(ev))


def parse_config(body: Mapping[str, Any]) -> Config:
    if body.get("schema") != K.CONFIG_SCHEMA:
        raise ConfigError(f"config schema is {body.get('schema')!r}, not {K.CONFIG_SCHEMA!r}")
    if body.get("registry_test") != K.REGISTRY_TEST:
        raise ConfigError(f"registry_test must be {K.REGISTRY_TEST!r}")
    rows = tuple(_row(r) for r in body.get("trigger_holds") or [])
    if not rows or len(rows) > MAX_TRIGGER_HOLDS:
        raise ConfigError(f"{len(rows)} trigger-holds: 1 to {MAX_TRIGGER_HOLDS} required")
    ids = [r.id for r in rows]
    if len(set(ids)) != len(ids):
        raise ConfigError("duplicate trigger-hold ids")
    keys = [(r.trigger_id, r.root, r.m, r.h) for r in rows]
    if len(set(keys)) != len(keys):
        raise ConfigError("two rows with the same trigger, root, m and h")
    return Config(K.REGISTRY_TEST, int(body.get("n_before", K.N_BEFORE)), rows)


def load_config(path: Path) -> Config:
    return parse_config(json.loads(Path(path).read_text(encoding="utf-8")))


__all__ = ["Config", "ConfigError", "MAX_TRIGGER_HOLDS", "TriggerHold", "load_config",
           "parse_config"]
