"""ETF daily bar interface for E22-F2's paper runner (AlpacaCoder, Stage E.24 Part C).

No network code, no vendor client, no keys. A source answers one question: for a session date
``t`` (the America/New_York trading date, never the machine's local date), what did each ETF
close at, and what was its total return from the previous session's close?

- ``EtfBar.close``: the session's raw, unadjusted closing price, USD per share.
- ``EtfBar.ret``: total return from the previous session's close,
  ``k x (rawclose(t) + D) / rawclose(prev) - 1`` (E22-F2 registration section 6: ``k`` the
  product of the split ratios and ``D`` the sum of the per-share distributions with ex_date in
  (prev, t]), so splits and distributions are inside the return. ``None`` only for the first row
  of a history.
- ``EtfBar.prev_date``: the session ``ret`` is measured from (``None`` exactly when ``ret`` is).

``EtfBarSource.bars(t)`` returns an ``EtfDay`` (``{symbol: EtfBar}``), or ``Missing(reason)`` for
the whole day. A symbol with no bar on ``t`` is absent from the mapping (as in forward/sources.py,
where an instrument with no row is missing for that date). ``SourceUnavailable`` (and its subclass
``NotReady``) mean the answer is not known yet: the caller writes NO ledger record.

Warm-up JSONL (UTF-8, ASCII content, one line per session, strictly ascending)::

    {"bars":{"BIL":{"close":91.52,"prev_date":"2026-11-02","ret":0.00012},...},"date":"2026-11-03"}

Lines are canonical JSON (sorted keys, no spaces), so ``etf_history_sha256(rows)`` equals the
sha256 of the file that ``dump_etf_warmup(rows, path)`` writes.

CSV format for manual daily entry (one row per symbol per session)::

    # lines starting with '#' are comments
    trade_date,symbol,close,ret,prev_date
    2026-11-03,QQQ,512.34,0.0041,2026-11-02
    2026-11-03,BIL,91.52,0.00012,2026-11-02

- ``ret`` and ``prev_date`` are both empty (first row of a history) or both set.
- A session with no rows is a missing day; a symbol with no row is missing for that session.
- A duplicated (trade_date, symbol) is an error, never "last wins".
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from types import MappingProxyType
from typing import Any, Protocol, runtime_checkable

from forward.sources import Missing, SourceError

__all__ = [
    "CSV_HEADER",
    "CsvEtfSource",
    "EtfBar",
    "EtfBarError",
    "EtfBarSource",
    "EtfDay",
    "EtfDayRow",
    "InMemoryEtfSource",
    "Missing",
    "NotReady",
    "SourceUnavailable",
    "dump_etf_warmup",
    "etf_history_sha256",
    "load_etf_warmup",
    "normalize_etf_day",
]

CSV_HEADER = ("trade_date", "symbol", "close", "ret", "prev_date")
SYMBOL_RE = re.compile(r"^[A-Z][A-Z0-9.]{0,9}$")


class EtfBarError(SourceError):
    """Malformed ETF bar input (a ValueError, like forward.sources.SourceError)."""


class SourceUnavailable(Exception):  # noqa: N818 (name fixed by the E.24 brief)
    """A connection failure, timeout, rate limit or partial response.

    The answer for the date is unknown: the caller must write NO ledger record and retry later.
    """


class NotReady(SourceUnavailable):
    """The session is not over yet, or its bars are not final (before the source's cutoff).

    Handled exactly like SourceUnavailable: no ledger record yet.
    """


def _number(value: Any, where: str) -> float:
    if isinstance(value, bool):
        raise EtfBarError(f"{where}: expected a number, got a bool")
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise EtfBarError(f"{where}: {value!r} is not a number") from exc
    if not math.isfinite(out):
        raise EtfBarError(f"{where}: {value!r} is not finite")
    return out


def _session_date(value: Any, where: str) -> date:
    if isinstance(value, datetime) or not isinstance(value, date):
        raise EtfBarError(f"{where}: expected a date (not a datetime), got {value!r}")
    return value


@dataclass(frozen=True)
class EtfBar:
    close: float
    ret: float | None = None
    prev_date: date | None = None

    def __post_init__(self) -> None:
        close = _number(self.close, "close")
        if close <= 0:
            raise EtfBarError(f"close must be > 0, got {close!r}")
        object.__setattr__(self, "close", close)
        if (self.ret is None) != (self.prev_date is None):
            raise EtfBarError("ret and prev_date must both be set or both be None")
        if self.ret is not None:
            ret = _number(self.ret, "ret")
            if ret <= -1:
                raise EtfBarError(f"ret must be > -1, got {ret!r}")
            object.__setattr__(self, "ret", ret)
            _session_date(self.prev_date, "prev_date")

    def to_json(self) -> dict[str, Any]:
        return {
            "close": self.close,
            "ret": self.ret,
            "prev_date": None if self.prev_date is None else self.prev_date.isoformat(),
        }

    @classmethod
    def from_json(cls, raw: Mapping[str, Any]) -> EtfBar:
        if not isinstance(raw, Mapping) or set(raw) != {"close", "ret", "prev_date"}:
            raise EtfBarError(f"bar must have exactly close, ret, prev_date: {raw!r}")
        prev = raw["prev_date"]
        try:
            prev_date = None if prev is None else date.fromisoformat(prev)
        except (TypeError, ValueError) as exc:
            raise EtfBarError(f"bad prev_date {prev!r}") from exc
        return cls(raw["close"], raw["ret"], prev_date)


EtfDay = Mapping[str, EtfBar]


@runtime_checkable
class EtfBarSource(Protocol):
    def bars(self, trade_date: date) -> EtfDay | Missing:
        """Bars for the America/New_York session ``trade_date``, or Missing.

        Raises SourceUnavailable (or NotReady) when the answer is not known yet.
        """
        ...


def _check_symbol(symbol: Any, where: str) -> str:
    if not isinstance(symbol, str) or not SYMBOL_RE.match(symbol):
        raise EtfBarError(f"{where}: bad symbol {symbol!r}")
    return symbol


def _as_bar(value: Any, where: str) -> EtfBar:
    if isinstance(value, EtfBar):
        return value
    if isinstance(value, Mapping):
        try:
            return EtfBar.from_json(value)
        except EtfBarError as exc:
            raise EtfBarError(f"{where}: {exc}") from exc
    raise EtfBarError(f"{where}: expected an EtfBar, got {type(value).__name__}")


def normalize_etf_day(
    raw: Any, trade_date: date, where: str = "bars"
) -> dict[str, EtfBar] | Missing:
    """Validate a source answer into a fresh ``{symbol: EtfBar}`` (sorted) or pass Missing on.

    An empty mapping counts as a missing day. Every ``prev_date`` must precede ``trade_date``.
    """
    _session_date(trade_date, f"{where}: trade_date")
    if isinstance(raw, Missing):
        return raw
    if not isinstance(raw, Mapping):
        raise EtfBarError(f"{where}: expected a mapping or Missing, got {type(raw).__name__}")
    if not raw:
        return Missing(f"no bars for {trade_date.isoformat()}")
    out: dict[str, EtfBar] = {}
    for symbol, value in raw.items():
        _check_symbol(symbol, where)
        bar = _as_bar(value, f"{where}/{symbol}")
        if bar.prev_date is not None and bar.prev_date >= trade_date:
            raise EtfBarError(
                f"{where}/{symbol}: prev_date {bar.prev_date} is not before {trade_date}"
            )
        out[symbol] = bar
    return dict(sorted(out.items()))


@dataclass(frozen=True)
class EtfDayRow:
    """One warm-up session: its date and every symbol's bar."""

    date: date
    bars: Mapping[str, EtfBar]

    def __post_init__(self) -> None:
        day = normalize_etf_day(self.bars, self.date, f"warm-up {self.date}")
        if isinstance(day, Missing):
            raise EtfBarError(f"warm-up {self.date}: a row needs at least one bar")
        object.__setattr__(self, "bars", MappingProxyType(day))

    def to_json(self) -> dict[str, Any]:
        bars = {s: b.to_json() for s, b in self.bars.items()}
        return {"date": self.date.isoformat(), "bars": bars}

    @classmethod
    def from_json(cls, raw: Mapping[str, Any]) -> EtfDayRow:
        if not isinstance(raw, Mapping) or set(raw) != {"date", "bars"}:
            raise EtfBarError(f"warm-up row must have exactly date and bars: {raw!r}")
        try:
            day = date.fromisoformat(raw["date"])
        except (TypeError, ValueError) as exc:
            raise EtfBarError(f"bad warm-up date {raw['date']!r}") from exc
        if not isinstance(raw["bars"], Mapping):
            raise EtfBarError(f"warm-up {day}: bars must be a mapping")
        return cls(day, {s: _as_bar(b, f"warm-up {day}/{s}") for s, b in raw["bars"].items()})


def _as_row(row: Any) -> EtfDayRow:
    if isinstance(row, EtfDayRow):
        return row
    if isinstance(row, tuple) and len(row) == 2:
        return EtfDayRow(row[0], row[1])
    raise EtfBarError(f"expected an EtfDayRow or (date, bars), got {type(row).__name__}")


def check_etf_history(rows: Iterable[EtfDayRow]) -> tuple[EtfDayRow, ...]:
    """Strictly ascending dates; per symbol, ``prev_date`` is its previous row's date and
    ``ret`` is None only on the symbol's first row."""
    rows = tuple(rows)
    last_seen: dict[str, date] = {}
    for a, b in zip(rows, rows[1:], strict=False):
        if b.date <= a.date:
            raise EtfBarError(f"warm-up rows must be strictly ascending: {a.date} then {b.date}")
    for row in rows:
        for symbol, bar in row.bars.items():
            seen = last_seen.get(symbol)
            if seen is not None and bar.prev_date != seen:
                raise EtfBarError(
                    f"warm-up {row.date}/{symbol}: prev_date {bar.prev_date} is not the "
                    f"symbol's previous row {seen}"
                )
            last_seen[symbol] = row.date
    return rows


def _canonical_line(row: EtfDayRow) -> str:
    return json.dumps(
        row.to_json(), sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    )


def etf_history_sha256(rows: Iterable[EtfDayRow | tuple[date, Mapping[str, EtfBar]]]) -> str:
    """sha256 of the canonical JSONL text of ``rows`` (equal to the dumped file's sha256)."""
    checked = check_etf_history(_as_row(r) for r in rows)
    body = "".join(_canonical_line(r) + "\n" for r in checked)
    return hashlib.sha256(body.encode("ascii")).hexdigest()


def dump_etf_warmup(
    rows: Iterable[EtfDayRow | tuple[date, Mapping[str, EtfBar]]], path: Path | str
) -> str:
    """Write the warm-up JSONL (refuses to overwrite an existing file); returns its sha256."""
    checked = check_etf_history(_as_row(r) for r in rows)
    body = "".join(_canonical_line(r) + "\n" for r in checked)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "x", encoding="ascii", newline="\n") as fh:
        fh.write(body)
    return hashlib.sha256(body.encode("ascii")).hexdigest()


def load_etf_warmup(path: Path | str) -> tuple[EtfDayRow, ...]:
    """Warm-up rows from the JSONL file (validated; strictly ascending)."""
    rows = []
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, start=1):
            if not line.strip():
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                raise EtfBarError(f"{path}:{n}: not JSON") from exc
            rows.append(EtfDayRow.from_json(raw))
    return check_etf_history(rows)


class InMemoryEtfSource:
    """A source over ``{date: answer}`` for tests and manual use. Absent dates are Missing.

    An answer may be an EtfDay (EtfBar or bar-JSON values), Missing, or a SourceUnavailable
    instance, which is raised (to exercise the caller's no-record rule).
    """

    def __init__(self, data: Mapping[date, Any]):
        self._data: dict[date, Any] = {}
        for day, answer in data.items():
            if isinstance(answer, SourceUnavailable):
                self._data[day] = answer
            else:
                self._data[day] = normalize_etf_day(answer, day, f"in-memory {day}")

    def bars(self, trade_date: date) -> EtfDay | Missing:
        found = self._data.get(trade_date)
        if found is None:
            return Missing(f"no in-memory bars for {trade_date.isoformat()}")
        if isinstance(found, SourceUnavailable):
            raise found
        if isinstance(found, Missing):
            return found
        return dict(found)


def _parse_csv(
    lines: list[str], path: str, symbols: frozenset[str] | None
) -> dict[date, dict[str, EtfBar]]:
    rows = [
        (n, line)
        for n, line in enumerate(lines, start=1)
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not rows:
        raise EtfBarError(f"{path}: no header row")
    header_no, header = rows[0]
    if tuple(c.strip() for c in next(csv.reader([header]))) != CSV_HEADER:
        raise EtfBarError(f"{path}:{header_no}: header must be {','.join(CSV_HEADER)}")
    table: dict[date, dict[str, EtfBar]] = {}
    for n, line in rows[1:]:
        cells = [c.strip() for c in next(csv.reader([line]))]
        where = f"{path}:{n}"
        if len(cells) != len(CSV_HEADER):
            raise EtfBarError(f"{where}: expected {len(CSV_HEADER)} fields, got {len(cells)}")
        try:
            day = date.fromisoformat(cells[0])
            prev = date.fromisoformat(cells[4]) if cells[4] else None
        except ValueError as exc:
            raise EtfBarError(f"{where}: bad date in {cells[0]!r} / {cells[4]!r}") from exc
        symbol = _check_symbol(cells[1], where)
        if symbols is not None and symbol not in symbols:
            raise EtfBarError(f"{where}: symbol {symbol!r} is not in the universe")
        try:
            ret = _number(cells[3], where) if cells[3] else None
            bar = EtfBar(_number(cells[2], where), ret, prev)
        except EtfBarError as exc:
            raise EtfBarError(f"{where}: {exc}") from exc
        day_bars = table.setdefault(day, {})
        if symbol in day_bars:
            raise EtfBarError(f"{where}: duplicate row for {day} {symbol}")
        day_bars[symbol] = bar
    for day, day_bars in table.items():
        normalize_etf_day(day_bars, day, f"{path} {day}")
    return table


class CsvEtfSource:
    """Manual daily entry: the CSV format in this module's docstring.

    The file is re-read and fully validated on every call, so rows appended between calls are
    seen, and a malformed row anywhere stops the run.
    """

    def __init__(self, path: Path | str, symbols: Iterable[str] | None = None):
        self.path = Path(path)
        self._symbols = frozenset(symbols) if symbols is not None else None

    def load(self) -> dict[date, dict[str, EtfBar]]:
        with open(self.path, encoding="utf-8", newline="") as fh:
            return _parse_csv(fh.read().splitlines(), str(self.path), self._symbols)

    def bars(self, trade_date: date) -> EtfDay | Missing:
        found = self.load().get(trade_date)
        if not found:
            return Missing(f"no rows for {trade_date.isoformat()} in {self.path.name}")
        return normalize_etf_day(found, trade_date, f"{self.path.name} {trade_date}")
