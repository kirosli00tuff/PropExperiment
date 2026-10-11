"""T3's GEX rows (prereg section 3; reports/stage_e14_briefs/gex/fetch_record.txt: the CSV's
header is ``date,price,dix,gex``).

``load_gex`` checks the file's sha256, then reads it row by row with the csv module: the header
must be exactly date,price,dix,gex; each row's date is parsed first, and a row dated on or after
2024-03-01 is cut right there, before any other field of it is parsed (it is never loaded); every
kept row must have an ISO date, a finite float gex, and a date no other kept row has. Any problem
raises ``GexInputError``; the evaluation calls ``load_gex`` once before the run-once marker (so an
input problem refuses the run with nothing consumed) and once after it.
"""

from __future__ import annotations

import csv
import hashlib
import io
import math
from datetime import date
from pathlib import Path

from h6_rod import constants as K

GEX_COLUMN = K.GEX_HEADER.index("gex")


class GexInputError(ValueError):
    """The GEX CSV is missing, changed or malformed."""


def _rows(text: str) -> tuple[dict[date, float], int]:
    reader = csv.reader(io.StringIO(text))
    try:
        header = tuple(h.strip() for h in next(reader))
    except StopIteration as exc:
        raise GexInputError("the GEX CSV is empty") from exc
    if header != K.GEX_HEADER:
        raise GexInputError(f"GEX CSV header {header} is not {K.GEX_HEADER}")
    kept: dict[date, float] = {}
    cut = 0
    for n, row in enumerate(reader, start=2):
        if not row or all(not c.strip() for c in row):
            continue
        try:
            day = date.fromisoformat(row[0].strip())
        except ValueError as exc:
            raise GexInputError(f"GEX CSV line {n}: date {row[0]!r} is not ISO") from exc
        if day >= K.FORBIDDEN_FROM:
            cut += 1  # never loaded: nothing else of the row is parsed
            continue
        if len(row) != len(K.GEX_HEADER):
            raise GexInputError(f"GEX CSV line {n}: {len(row)} fields, not {len(K.GEX_HEADER)}")
        try:
            value = float(row[GEX_COLUMN])
        except ValueError as exc:
            raise GexInputError(f"GEX CSV line {n}: gex is not a number") from exc
        if not math.isfinite(value):
            raise GexInputError(f"GEX CSV line {n}: gex is not finite")
        if day in kept:
            raise GexInputError(f"GEX CSV line {n}: a second row dated {day}")
        kept[day] = value
    return kept, cut


def load_gex(path: Path, *, expected_sha256: str | None) -> tuple[dict[date, float], dict]:
    """(gex by row date, rows dated before 2024-03-01; a record with the counts and sha256)."""
    path = Path(path)
    if expected_sha256 is None:
        raise GexInputError("GEX_CSV_SHA256 is None: the lead fills it at the freeze")
    if not path.is_file():
        raise GexInputError(f"GEX CSV {path} does not exist")
    raw = path.read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if got != expected_sha256:
        raise GexInputError(f"GEX CSV {path.name}: sha256 {got[:12]}... is not the pinned "
                            f"{expected_sha256[:12]}...")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise GexInputError(f"GEX CSV {path.name} is not UTF-8") from exc
    kept, cut = _rows(text)
    return kept, {"path": str(path), "sha256": got, "rows_kept": len(kept),
                  "rows_cut_on_or_after_2024_03_01": cut}


__all__ = ["GexInputError", "load_gex"]
