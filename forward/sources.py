"""Daily settlement sources for E22-F1's paper runner (ForwardRunnerCoder, E.22).

No network code, no vendor client, no keys. A source answers one question: for a trade date,
what settlement did each instrument's contracts print? The answer is either a mapping
``{instrument: {contract_id: settlement_price}}`` (several contracts per instrument are allowed,
and on a roll date both the held and the next contract are needed), or ``Missing(reason)``.

The single-contract form of the brief, ``{instrument: (contract_id, settlement_price)}``, is
accepted too and normalised by :func:`normalize_day`.

CSV format for manual daily entry (UTF-8, one row per contract per trade date)::

    # lines starting with '#' are comments
    trade_date,instrument,contract_id,settlement
    2026-11-02,MNQ,MNQZ26,21034.25
    2026-11-02,MCL,MCLF27,71.42
    2026-11-02,MCL,MCLG27,71.10

- trade_date: ISO date (YYYY-MM-DD); instrument: the runner's instrument key (e.g. MNQ, 10Y);
  contract_id: root + month code + 2-digit year (MNQZ26); settlement: the exchange settlement in
  the contract's quoted units (a finite decimal; negative values are allowed).
- A trade date with no rows is a missing day. An instrument with no row on a date is missing
  for that date. A duplicated (trade_date, instrument, contract_id) is an error, never "last wins".
"""

from __future__ import annotations

import csv
import math
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

CSV_HEADER = ("trade_date", "instrument", "contract_id", "settlement")
CONTRACT_RE = re.compile(r"^[A-Z0-9]{1,6}[FGHJKMNQUVXZ][0-9]{2}$")
INSTRUMENT_RE = re.compile(r"^[A-Z0-9]{1,6}$")

DaySettlements = dict[str, dict[str, float]]


class SourceError(ValueError):
    """Malformed settlement input."""


@dataclass(frozen=True)
class Missing:
    """No settlements at all for the requested trade date."""

    reason: str


@runtime_checkable
class SettlementSource(Protocol):
    def settlements(self, trade_date: date) -> DaySettlements | Missing:
        """Settlements printed on ``trade_date``, or Missing."""
        ...


def _price(value: Any, where: str) -> float:
    if isinstance(value, bool):
        raise SourceError(f"{where}: settlement must be a number, got a bool")
    try:
        price = float(value)
    except (TypeError, ValueError) as exc:
        raise SourceError(f"{where}: settlement {value!r} is not a number") from exc
    if not math.isfinite(price):
        raise SourceError(f"{where}: settlement {value!r} is not finite")
    return price


def _check_ids(instrument: Any, cid: Any, where: str) -> None:
    if not isinstance(instrument, str) or not INSTRUMENT_RE.match(instrument):
        raise SourceError(f"{where}: bad instrument {instrument!r}")
    if not isinstance(cid, str) or not CONTRACT_RE.match(cid):
        raise SourceError(f"{where}: bad contract id {cid!r} (expected e.g. MNQZ26)")


def normalize_day(raw: Any, where: str = "settlements") -> DaySettlements | Missing:
    """Validate a source answer into ``{instrument: {contract_id: price}}`` or pass Missing on.

    An empty mapping counts as a missing day.
    """
    if isinstance(raw, Missing):
        return raw
    if not isinstance(raw, Mapping):
        raise SourceError(f"{where}: expected a mapping or Missing, got {type(raw).__name__}")
    if not raw:
        return Missing("no settlements for the date")
    out: DaySettlements = {}
    for instrument, entry in raw.items():
        if isinstance(entry, tuple) and len(entry) == 2:
            entry = {entry[0]: entry[1]}
        if not isinstance(entry, Mapping) or not entry:
            raise SourceError(
                f"{where}: {instrument!r} needs (contract_id, price) or {{id: price}}"
            )
        quotes = {}
        for cid, value in entry.items():
            _check_ids(instrument, cid, f"{where}/{instrument}")
            quotes[cid] = _price(value, f"{where}/{instrument}/{cid}")
        out[instrument] = dict(sorted(quotes.items()))
    return dict(sorted(out.items()))


class InMemorySettlementSource:
    """A source over a dict ``{date: answer}``, for tests. Absent dates are Missing."""

    def __init__(self, data: Mapping[date, Any]):
        self._data = {d: normalize_day(v, f"in-memory {d}") for d, v in data.items()}

    def settlements(self, trade_date: date) -> DaySettlements | Missing:
        found = self._data.get(trade_date)
        if found is None:
            return Missing(f"no in-memory settlements for {trade_date.isoformat()}")
        if isinstance(found, Missing):
            return found
        return {inst: dict(quotes) for inst, quotes in found.items()}


def _parse_rows(
    lines: Iterable[str], path: str, instruments: frozenset[str] | None
) -> dict[date, DaySettlements]:
    rows = [
        (n, line)
        for n, line in enumerate(lines, start=1)
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not rows:
        raise SourceError(f"{path}: no header row")
    header_no, header = rows[0]
    if tuple(c.strip() for c in next(csv.reader([header]))) != CSV_HEADER:
        raise SourceError(f"{path}:{header_no}: header must be {','.join(CSV_HEADER)}")
    table: dict[date, DaySettlements] = {}
    for n, line in rows[1:]:
        cells = [c.strip() for c in next(csv.reader([line]))]
        where = f"{path}:{n}"
        if len(cells) != len(CSV_HEADER):
            raise SourceError(f"{where}: expected {len(CSV_HEADER)} fields, got {len(cells)}")
        try:
            day = date.fromisoformat(cells[0])
        except ValueError as exc:
            raise SourceError(f"{where}: bad trade_date {cells[0]!r}") from exc
        instrument, cid = cells[1], cells[2]
        _check_ids(instrument, cid, where)
        if instruments is not None and instrument not in instruments:
            raise SourceError(f"{where}: instrument {instrument!r} is not in the universe")
        quotes = table.setdefault(day, {}).setdefault(instrument, {})
        if cid in quotes:
            raise SourceError(f"{where}: duplicate row for {day} {instrument} {cid}")
        quotes[cid] = _price(cells[3], where)
    return table


class CsvSettlementSource:
    """Manual daily entry: the CSV format in this module's docstring.

    The file is re-read and fully validated on every call, so rows the operator appends between
    calls are seen, and a malformed row anywhere stops the run.
    """

    def __init__(self, path: Path | str, instruments: Iterable[str] | None = None):
        self.path = Path(path)
        self._instruments = frozenset(instruments) if instruments is not None else None

    def load(self) -> dict[date, DaySettlements]:
        with open(self.path, encoding="utf-8", newline="") as fh:
            return _parse_rows(fh.read().splitlines(), str(self.path), self._instruments)

    def settlements(self, trade_date: date) -> DaySettlements | Missing:
        found = self.load().get(trade_date)
        if not found:
            return Missing(f"no rows for {trade_date.isoformat()} in {self.path.name}")
        return normalize_day(found, f"{self.path.name} {trade_date}")
