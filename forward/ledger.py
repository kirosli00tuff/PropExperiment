"""Append-only JSONL ledger of E22-F1's paper runner (ForwardRunnerCoder, E.22).

One record per trade date, one JSON object per line in canonical form (sorted keys, no spaces,
ASCII, no NaN). Each record carries ``prev_record_sha256`` (the previous record's hash; 64 zeros
for the first record) and ``record_sha256`` = sha256 of the canonical JSON of the record without
``record_sha256``. The ledger refuses rewrites (a date already present), dates going backwards,
and any append onto a chain that no longer verifies. ``verify`` re-hashes the whole chain.
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

GENESIS_SHA256 = "0" * 64
PREV_KEY = "prev_record_sha256"
HASH_KEY = "record_sha256"
HASH_FIELDS = (PREV_KEY, HASH_KEY)


class LedgerError(Exception):
    """Base class for ledger refusals."""


class LedgerOrderError(LedgerError):
    """A rewrite or an out-of-order (backwards) date."""


class LedgerIntegrityError(LedgerError):
    """The chain on disk does not verify; ``line`` is the first bad line when known."""

    def __init__(self, message: str, line: int | None = None):
        super().__init__(message)
        self.line = line


def canonical_json(obj: Any) -> str:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    )


def record_sha256(record: dict[str, Any]) -> str:
    body = {k: v for k, v in record.items() if k != HASH_KEY}
    return hashlib.sha256(canonical_json(body).encode("ascii")).hexdigest()


def strip_hashes(record: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in record.items() if k not in HASH_FIELDS}


@dataclass(frozen=True)
class VerifyReport:
    ok: bool
    n_records: int
    last_date: str | None
    last_sha256: str | None
    error: str | None = None
    line: int | None = None


def _check_line(n: int, line: str, prev_hash: str, prev_date: date | None) -> tuple[dict, date]:
    try:
        record = json.loads(line)
    except json.JSONDecodeError as exc:
        raise LedgerIntegrityError(f"line {n}: not JSON ({exc.msg})", n) from exc
    if not isinstance(record, dict) or not all(k in record for k in ("date", *HASH_FIELDS)):
        raise LedgerIntegrityError(f"line {n}: record lacks date or hash fields", n)
    if record[PREV_KEY] != prev_hash:
        raise LedgerIntegrityError(f"line {n}: prev_record_sha256 does not match line {n - 1}", n)
    if record_sha256(record) != record[HASH_KEY]:
        raise LedgerIntegrityError(f"line {n}: record_sha256 does not match its content", n)
    try:
        day = date.fromisoformat(record["date"])
    except (TypeError, ValueError) as exc:
        raise LedgerIntegrityError(f"line {n}: bad date {record['date']!r}", n) from exc
    if prev_date is not None and day <= prev_date:
        raise LedgerIntegrityError(f"line {n}: date {day} is not after {prev_date}", n)
    return record, day


def parse_chain(text: str) -> list[dict[str, Any]]:
    """Parse and verify ledger text; raises LedgerIntegrityError naming the first bad line."""
    if text and not text.endswith("\n"):
        raise LedgerIntegrityError("last line is truncated (no trailing newline)")
    records: list[dict[str, Any]] = []
    prev_hash, prev_date = GENESIS_SHA256, None
    for n, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            raise LedgerIntegrityError(f"line {n}: blank line inside the ledger", n)
        record, prev_date = _check_line(n, line, prev_hash, prev_date)
        prev_hash = record[HASH_KEY]
        records.append(record)
    return records


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    with open(path, encoding="ascii") as fh:
        return fh.read()


def verify(path: Path | str) -> VerifyReport:
    """Re-hash the chain on disk. Never raises for a bad chain; the report says what failed."""
    try:
        records = parse_chain(_read_text(Path(path)))
    except (LedgerIntegrityError, UnicodeDecodeError) as exc:
        return VerifyReport(False, 0, None, None, str(exc), getattr(exc, "line", None))
    last = records[-1] if records else None
    return VerifyReport(
        True, len(records), last["date"] if last else None, last[HASH_KEY] if last else None
    )


class Ledger:
    """The append-only ledger file. It never truncates, edits or deletes a line."""

    def __init__(self, path: Path | str):
        self.path = Path(path)

    def records(self) -> list[dict[str, Any]]:
        """Every record, after verifying the whole chain (raises LedgerIntegrityError)."""
        return parse_chain(_read_text(self.path))

    def append(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Hash-link ``payload`` onto the chain and write it; returns the stored record."""
        if any(k in payload for k in HASH_FIELDS):
            raise LedgerError("payload must not carry hash fields; the ledger computes them")
        day = date.fromisoformat(payload["date"])
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a+", encoding="ascii") as fh:
            fcntl.flock(fh, fcntl.LOCK_EX)
            try:
                fh.seek(0)
                records = parse_chain(fh.read())
                _check_order(records, day)
                record = dict(payload)
                record[PREV_KEY] = records[-1][HASH_KEY] if records else GENESIS_SHA256
                record[HASH_KEY] = record_sha256(record)
                line = canonical_json(record) + "\n"
                fh.seek(0, os.SEEK_END)
                fh.write(line)
                fh.flush()
                os.fsync(fh.fileno())
            finally:
                fcntl.flock(fh, fcntl.LOCK_UN)
        return json.loads(line)


def _check_order(records: list[dict[str, Any]], day: date) -> None:
    if not records:
        return
    last = date.fromisoformat(records[-1]["date"])
    if day == last or any(r["date"] == day.isoformat() for r in records):
        raise LedgerOrderError(f"{day} is already in the ledger; rewrites are refused")
    if day < last:
        raise LedgerOrderError(
            f"{day} is before the last ledger date {last}; out-of-order dates are refused"
        )


def _main(argv: list[str] | None = None) -> int:
    import argparse
    import sys

    ap = argparse.ArgumentParser(prog="python -m forward.ledger", description="verify a ledger")
    ap.add_argument("ledger")
    report = verify(ap.parse_args(argv).ledger)
    sys.stdout.write(f"{report}\n")
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(_main())
