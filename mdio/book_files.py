"""Per-unit and per-fill files of multi-day books (Stage E.24, V41; E.23 VerdictVerifier NOTE-5).

The layout is E.21's per-root file (multiday.evaluate._root_rows, schema
``stage_e21_per_root/1``): root, vehicle, tick_value_cents, per_contract_daily_dollars (one
vehicle contract held, roll legs included, costs excluded; None on a failed interval), holdings
and fills per book (multiday.book's own BookResult.holdings and BookResult.fills rows,
unchanged) and the root's counters. Added: ``units`` (each book's units, one row per unit, dates
as ISO text) and ``book_counters``. ``schema`` is ``mdio_per_root/1``; ``layout`` names E.21's.

``write_per_root`` writes <out_dir>/per_root/<ROOT>.json once (O_EXCL), as E.21 wrote
reports/stage_e21_runs/per_root/<ROOT>.json; the caller picks out_dir.
"""

from __future__ import annotations

import json
import os
from collections.abc import Mapping, Sequence
from dataclasses import asdict, is_dataclass
from datetime import date
from pathlib import Path

from base_rules import constants as BK
from multiday import constants as MK
from multiday.book import BookResult, RootData

PER_ROOT_SCHEMA = "mdio_per_root/1"
E21_LAYOUT = MK.PER_ROOT_SCHEMA  # "stage_e21_per_root/1"


def unit_rows(units: Sequence[object]) -> list[dict]:
    """One row per unit (a dataclass such as trigger_hold.units.Unit), dates as ISO text."""
    rows = []
    for u in units:
        if not is_dataclass(u) or isinstance(u, type):
            raise ValueError(f"units must be dataclass instances (trigger_hold.units.Unit), "
                             f"got {type(u).__name__}")
        rows.append({k: v.isoformat() if isinstance(v, date) else v
                     for k, v in asdict(u).items()})
    return rows


def per_root_record(rd: RootData, books: Mapping[str, BookResult],
                    units: Mapping[str, Sequence[object]] | None = None) -> dict:
    """The root's per-root record: E.21's layout keyed by book id, plus units."""
    units = units or {}
    stray = sorted(set(units) - set(books))
    if stray:
        raise ValueError(f"units for {stray} have no book")
    pc = rd.path.per_contract_daily()
    return {"schema": PER_ROOT_SCHEMA, "layout": E21_LAYOUT, "root": rd.root,
            "vehicle": rd.vehicle, "tick_value_cents": str(rd.tick_value_cents),
            "per_contract_daily_dollars": {str(d): (None if v is None else float(v) / 100.0)
                                           for d, v in sorted(pc.items())},
            "holdings": {b: list(book.holdings) for b, book in books.items()},
            "fills": {b: list(book.fills) for b, book in books.items()},
            "units": {b: unit_rows(u) for b, u in units.items()},
            "book_counters": {b: dict(sorted(book.counters.items()))
                              for b, book in books.items()},
            "counters": dict(sorted(rd.counters.items()))}


def write_per_root(out_dir: Path, record: Mapping) -> Path:
    """<out_dir>/per_root/<ROOT>.json, written once (an existing file is never replaced)."""
    root = record.get("root")
    if root not in BK.PRODUCTS:
        raise ValueError(f"record root {root!r} is not one of the test products")
    out = Path(out_dir) / "per_root" / f"{root}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    body = (json.dumps(record, indent=1, default=str) + "\n").encode()
    fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, "wb") as fh:
        fh.write(body)
    return out


__all__ = ["E21_LAYOUT", "PER_ROOT_SCHEMA", "per_root_record", "unit_rows", "write_per_root"]
