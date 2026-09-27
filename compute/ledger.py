"""The job ledgers of the compute backend: append-only JSONL step records (Stage E.2b, V10).

The ThinkPad keeps one ledger per job (steps prepared, code_synced, sent, started, done, pulled,
verified); the far side keeps its own (received, started, spawned, restarted, done). A restart
reads the ledger and skips every step already recorded. Each line is written whole and flushed;
a crash can leave only a final line without its newline, which is reported as ``truncated_tail``
and ignored; any other unreadable line refuses the ledger (``LedgerCorrupt``), never skipped.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


class LedgerCorrupt(RuntimeError):
    """A ledger line other than an unterminated last line is not a JSON object."""


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


@dataclass(frozen=True)
class LedgerRead:
    entries: tuple[dict, ...]
    truncated_tail: bool

    def steps(self) -> tuple[str, ...]:
        return tuple(str(entry.get("step")) for entry in self.entries)

    def has(self, step: str) -> bool:
        return step in self.steps()

    def last(self, *steps: str) -> dict | None:
        for entry in reversed(self.entries):
            if entry.get("step") in steps:
                return entry
        return None


class JobLedger:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def read(self) -> LedgerRead:
        if not self.path.is_file():
            return LedgerRead((), False)
        raw = self.path.read_bytes()
        lines = raw.split(b"\n")
        truncated = bool(lines and lines[-1].strip())
        body, tail = lines[:-1], lines[-1]
        entries = []
        for number, line in enumerate(body, start=1):
            if not line.strip():
                continue
            try:
                entry = json.loads(line.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise LedgerCorrupt(f"{self.path}: line {number} is not JSON ({exc})") from exc
            if not isinstance(entry, dict) or "step" not in entry:
                raise LedgerCorrupt(f"{self.path}: line {number} has no step")
            entries.append(entry)
        if truncated:
            try:
                entry = json.loads(tail.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                entry = None
            if isinstance(entry, dict) and "step" in entry:
                entries.append(entry)
                truncated = False
        return LedgerRead(tuple(entries), truncated)

    def append(self, step: str, **fields: object) -> dict:
        entry = {"step": step, "time": now_iso(), **fields}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.read().truncated_tail:  # drop a crash's torn last line, and say so
            raw = self.path.read_bytes()
            with self.path.open("r+b") as handle:
                handle.truncate(raw.rfind(b"\n") + 1)
            entry["dropped_torn_line"] = True
        line = json.dumps(entry, sort_keys=True, default=str).encode("utf-8") + b"\n"
        with self.path.open("ab") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())
        return entry
