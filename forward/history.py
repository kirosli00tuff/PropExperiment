"""The price history E22-F1's runner passes to forward.strategy.target_positions (E.22).

``history`` is a tuple of :class:`HistoryRow`, oldest first, ending with the decision date t:
the warm-up rows (if any) followed by one row per ledger trade date. A row holds every settlement
the source gave that day (``prices``: instrument -> contract_id -> price) and each instrument's
reference contract after that day's rolls (``reference``: instrument -> contract_id). A missing
day is a row with empty ``prices``. Rows are read-only.

Helpers for the strategy: :func:`reference_series` (the held contract's own price, for sizing)
and :func:`back_adjusted_series` (additive, "Panama" back-adjustment at each reference switch,
for signals). On a switch date the row holds both contracts' prices, because the runner switches
the reference contract only on a date where both settled.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from types import MappingProxyType
from typing import Any

import pandas as pd


def _freeze(prices: Mapping[str, Mapping[str, float]]) -> Mapping[str, Mapping[str, float]]:
    return MappingProxyType(
        {inst: MappingProxyType(dict(sorted(q.items()))) for inst, q in sorted(prices.items())}
    )


@dataclass(frozen=True)
class HistoryRow:
    date: date
    prices: Mapping[str, Mapping[str, float]] = field(default_factory=dict)
    reference: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "prices", _freeze(self.prices))
        object.__setattr__(
            self, "reference", MappingProxyType(dict(sorted(self.reference.items())))
        )

    def price(self, instrument: str) -> float | None:
        """The reference contract's settlement on this row, or None when it is missing."""
        cid = self.reference.get(instrument)
        return None if cid is None else self.prices.get(instrument, {}).get(cid)

    def to_json(self) -> dict[str, Any]:
        return {
            "date": self.date.isoformat(),
            "prices": {i: dict(q) for i, q in self.prices.items()},
            "reference": dict(self.reference),
        }

    @classmethod
    def from_json(cls, raw: Mapping[str, Any]) -> HistoryRow:
        return cls(
            date.fromisoformat(raw["date"]),
            {i: {c: float(p) for c, p in q.items()} for i, q in raw["prices"].items()},
            dict(raw["reference"]),
        )


def row_from_record(record: Mapping[str, Any]) -> HistoryRow:
    reference = {
        inst: pos["contract"] for inst, pos in record["positions"].items() if pos.get("contract")
    }
    return HistoryRow(date.fromisoformat(record["date"]), record["prices"], reference)


def check_ascending(rows: Sequence[HistoryRow]) -> None:
    for a, b in zip(rows, rows[1:], strict=False):
        if b.date <= a.date:
            raise ValueError(f"history rows must be strictly ascending: {a.date} then {b.date}")


def history_fingerprint(rows: Iterable[HistoryRow]) -> str:
    body = json.dumps([r.to_json() for r in rows], sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(body.encode("ascii")).hexdigest()


def load_warmup(path: Path | str) -> tuple[HistoryRow, ...]:
    """Warm-up rows from a JSONL file of HistoryRow.to_json objects (strictly ascending)."""
    with open(path, encoding="utf-8") as fh:
        rows = tuple(HistoryRow.from_json(json.loads(line)) for line in fh if line.strip())
    check_ascending(rows)
    return rows


def reference_series(
    history: Sequence[HistoryRow], instrument: str
) -> list[tuple[date, str, float]]:
    """(date, reference contract, its settlement) on every row where that settlement exists."""
    out = []
    for row in history:
        price = row.price(instrument)
        if price is not None:
            out.append((row.date, row.reference[instrument], price))
    return out


def back_adjusted_series(
    history: Sequence[HistoryRow], instrument: str
) -> list[tuple[date, float]]:
    """Additively back-adjusted reference prices; the latest price is unadjusted.

    At each reference switch (old contract on the previous observed row, new on this row) every
    earlier price is shifted by new - old, both read from the switch row. Raises ValueError when
    the switch row lacks the old contract's settlement.
    """
    series = reference_series(history, instrument)
    rows_by_date = {row.date: row for row in history}
    adjusted: list[tuple[date, float]] = []
    shift = 0.0
    for i in range(len(series) - 1, -1, -1):
        day, cid, price = series[i]
        adjusted.append((day, price + shift))
        if i == 0 or series[i - 1][1] == cid:
            continue
        old_cid = series[i - 1][1]
        old_price = rows_by_date[day].prices.get(instrument, {}).get(old_cid)
        if old_price is None:
            raise ValueError(
                f"{instrument}: switch {old_cid}->{cid} on {day} lacks {old_cid}'s settlement"
            )
        shift += price - old_price
    adjusted.reverse()
    return adjusted


def instrument_frame(history: Sequence[HistoryRow], instrument: str) -> pd.DataFrame:
    """One instrument's observed rows as a DataFrame indexed by date (DatetimeIndex).

    Columns: ``contract`` (reference contract), ``price`` (its settlement, for sizing) and
    ``adjusted`` (the back-adjusted series, for signals). Dates without a settlement are absent.
    """
    series = reference_series(history, instrument)
    adjusted = back_adjusted_series(history, instrument)
    index = pd.DatetimeIndex([pd.Timestamp(d) for d, _, _ in series], name="date")
    return pd.DataFrame(
        {
            "contract": [c for _, c, _ in series],
            "price": [p for _, _, p in series],
            "adjusted": [a for _, a in adjusted],
        },
        index=index,
    )
