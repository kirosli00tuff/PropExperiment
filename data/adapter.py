"""Databento GLBX.MDP3 adapter for MES: immutable raw storage and roll boundaries.

Ported from MLCryptoEngine ``data/databento/ingest.py`` (``fetch_range``,
``_download_to_file``) and ``data/databento/rolls.py`` (read-only port,
2026-09-16), narrowed to MES:

- **Priced, gated, committed, then fetched.** Every download goes through
  :class:`data.spend_gate.SpendGate`; there is no other download path.
- **Raw is immutable.** A target that already exists is refused *before*
  the request is priced, and the final placement uses ``os.link`` (which
  cannot replace an existing file) rather than ``rename`` (which silently
  can). Written files are made read-only.
- **Rolls are derived, never detected.** The vendor's symbology endpoint
  states which instrument a continuous symbol maps to on each date, so a roll
  is a known fact, not a price-jump inference. Symbology is metadata-only
  and free, so it never touches the spend gate.

Continuous symbol choice: ``MES.v.0`` (volume-ranked front). Databento's
``.c.0`` calendar rule rolls only after expiration (their docs' ES.c.0
example rolls on the Sunday after the March expiry), so it would keep the
expiring, thinning contract through its final week every quarter. The roll
*logic* is unchanged from the port; only the rank rule differs. Both rules'
boundaries are resolved and recorded for comparison.
"""

from __future__ import annotations

import json
import os
import stat
from dataclasses import asdict, dataclass
from itertools import pairwise
from pathlib import Path
from typing import Any

from data.config import DATASET, VENDOR_ROOT
from data.spend_gate import RequestParams, SpendGate

MES_ROOT = "MES"
MES_CONTINUOUS = "MES.v.0"
MES_CALENDAR_CONTINUOUS = "MES.c.0"
STYPE_CONTINUOUS = "continuous"
OHLCV_1M = "ohlcv-1m"
# Equity index quarterly cycle: March, June, September, December.
QUARTERLY_MONTH_CODES = ("H", "M", "U", "Z")


class RawFileExistsError(FileExistsError):
    """Refusal to overwrite paid-for vendor raw data."""


@dataclass(frozen=True, slots=True)
class RollBoundary:
    """One instrument change in a continuous series."""

    symbol: str
    date: str  # first UTC date on which the NEW instrument applies
    ts_ns: int  # midnight UTC of that date — the splice point
    from_instrument: str
    to_instrument: str
    from_raw_symbol: str | None = None
    to_raw_symbol: str | None = None


def raw_path(symbol: str, schema: str, start: str, end: str, root: Path = VENDOR_ROOT) -> Path:
    safe = symbol.replace(".", "_")
    return root / DATASET / schema / safe / f"range={start}_{end}.dbn.zst"


def _refuse_existing(target: Path) -> None:
    from data.holdout import is_sealed_raw  # lazy: holdout reads its manifest from docs/

    if is_sealed_raw(target):
        raise RawFileExistsError(
            f"REFUSED: {target.name} is already owned, held in the sealed holdout store "
            "(docs/HOLDOUT_MANIFEST.json). It is never bought twice."
        )
    if target.exists():
        raise RawFileExistsError(
            f"REFUSED: {target} already exists. Vendor raw is immutable — it cost money "
            "and is never overwritten. Delete it deliberately by hand if it is truly bad."
        )


def fetch_range(
    gate: SpendGate,
    client: Any,
    params: RequestParams,
    root: Path = VENDOR_ROOT,
    note: str = "",
) -> Path:
    """Refuse-existing -> quote -> authorize -> commit -> download -> link -> settle."""
    from data.holdout import request_touches_sealed_window, sealed_window_utc_dates

    if len(params.symbols) != 1:
        raise ValueError("one symbol per stored raw file")
    if request_touches_sealed_window(params.start, params.end):
        window = sealed_window_utc_dates()
        raise RawFileExistsError(
            f"REFUSED: {params.start}..{params.end} overlaps the sealed holdout window "
            f"{window[0]}..{window[1]} (Stage C Task 6). Those bars are already owned and sealed; "
            "buying them again would both cost money and put holdout prices back on disk as "
            f"plaintext. Request data from {window[1]} onward instead."
        )
    target = raw_path(params.symbols[0], params.schema, params.start, params.end, root)
    _refuse_existing(target)

    quote = gate.quote(client, params)
    gate.authorize(params, quote)  # raises BudgetRefusedError on refusal
    assert quote is not None  # authorize refuses an unpriced request
    gate.commit(quote, note=note)

    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.parent / (target.name + ".partial")
    partial.unlink(missing_ok=True)
    try:
        client.timeseries.get_range(**params.as_kwargs(), path=partial)
    except BaseException:
        partial.unlink(missing_ok=True)  # the commit stays: pessimistic ledger
        raise
    try:
        os.link(partial, target)  # fails if target appeared meanwhile — never replaces
    except FileExistsError as exc:
        partial.unlink(missing_ok=True)
        raise RawFileExistsError(f"REFUSED: {target} appeared during download") from exc
    partial.unlink()
    target.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

    delivered = delivered_record_bytes(target)
    exceeded = quote.billable_bytes > 0 and delivered > quote.billable_bytes
    # No per-request invoice exists, so actual = quote unless more bytes arrived
    # than were quoted; then charge pro rata so the ledger stays pessimistic.
    actual = quote.usd * delivered / quote.billable_bytes if exceeded else quote.usd
    gate.settle(
        quote,
        actual_usd=actual,
        note=(
            "actual_usd = quote unless delivery exceeded it (then pro rata): "
            "timeseries.get_range returns no per-request invoice. Delivered uncompressed "
            f"record bytes {delivered:,} vs quoted billable {quote.billable_bytes:,}"
            + (" — DELIVERED EXCEEDS QUOTE" if exceeded else "")
        ),
    )
    return target


def delivered_record_bytes(path: Path) -> int:
    import databento  # lazy

    store = databento.DBNStore.from_file(path)
    return sum(chunk.nbytes for chunk in store.to_ndarray(count=1_000_000))


# ---------------------------------------------------------------- rolls ----
def resolve_rolls(
    client: Any, symbol: str, start_date: str, end_date: str, dataset: str = DATASET
) -> list[RollBoundary]:
    """Roll boundaries for ``symbol`` over ``[start_date, end_date)``. Free."""
    by_id = client.symbology.resolve(
        dataset=dataset, symbols=[symbol], stype_in=STYPE_CONTINUOUS,
        stype_out="instrument_id", start_date=start_date, end_date=end_date,
    )
    intervals = sorted(by_id["result"].get(symbol, []), key=lambda e: str(e["d0"]))
    ids = sorted({str(e["s"]) for e in intervals})
    by_raw = client.symbology.resolve(
        dataset=dataset, symbols=ids, stype_in="instrument_id",
        stype_out="raw_symbol", start_date=start_date, end_date=end_date,
    )
    return boundaries_from_intervals(symbol, intervals, by_raw["result"])


def boundaries_from_intervals(
    symbol: str,
    intervals: list[dict[str, Any]],
    raw_intervals: dict[str, list[dict[str, Any]]] | None = None,
) -> list[RollBoundary]:
    """Pure: symbology intervals -> boundaries (contiguous same-instrument merged).

    ``raw_intervals`` maps instrument_id -> dated raw-symbol intervals. CME
    reuses instrument ids over time, so the raw symbol is looked up for the
    date the continuous symbol actually mapped to that id, never "latest".
    """
    from datetime import UTC, datetime

    raw = raw_intervals or {}

    def raw_on(instrument: str, day: str) -> str | None:
        for entry in raw.get(instrument, []):
            if str(entry["d0"]) <= day < str(entry["d1"]):
                return str(entry["s"])
        return None
    out: list[RollBoundary] = []
    for previous, current in pairwise(intervals):
        if str(previous["s"]) == str(current["s"]):
            continue
        d0 = str(current["d0"])
        ts = int(datetime.strptime(d0, "%Y-%m-%d").replace(tzinfo=UTC).timestamp()) * 10**9
        out.append(
            RollBoundary(
                symbol=symbol, date=d0, ts_ns=ts,
                from_instrument=str(previous["s"]), to_instrument=str(current["s"]),
                from_raw_symbol=raw_on(str(previous["s"]), str(previous["d0"])),
                to_raw_symbol=raw_on(str(current["s"]), d0),
            )
        )
    return out


def roll_cycle_violations(boundaries: list[RollBoundary]) -> list[str]:
    """Rolls that break the H->M->U->Z->H quarterly cycle (by raw symbol)."""
    problems: list[str] = []
    for b in boundaries:
        if not (b.from_raw_symbol and b.to_raw_symbol):
            problems.append(f"{b.date}: raw symbols unresolved")
            continue
        f_code, t_code = b.from_raw_symbol[-2], b.to_raw_symbol[-2]
        if f_code not in QUARTERLY_MONTH_CODES or t_code not in QUARTERLY_MONTH_CODES:
            problems.append(f"{b.date}: non-quarterly {b.from_raw_symbol}->{b.to_raw_symbol}")
            continue
        expected = QUARTERLY_MONTH_CODES[(QUARTERLY_MONTH_CODES.index(f_code) + 1) % 4]
        if t_code != expected:
            problems.append(f"{b.date}: {b.from_raw_symbol}->{b.to_raw_symbol} skips a quarter")
    return problems


def write_rolls(boundaries: list[RollBoundary], path: Path) -> Path:
    """Persist boundaries next to the raw data; refuses to overwrite."""
    _refuse_existing(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as fh:
        for b in sorted(boundaries, key=lambda x: x.ts_ns):
            fh.write(json.dumps(asdict(b)) + "\n")
    return path


def read_rolls(path: Path) -> list[RollBoundary]:
    if not path.is_file():
        return []
    return [RollBoundary(**json.loads(x)) for x in path.read_text().splitlines() if x.strip()]
