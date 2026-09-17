"""Stage A.1 Task 2: quote, then pull MES ohlcv-1m (continuous) through the spend gate.

    uv run python -m data.pull_mes --quote-only   # prices every chunk, ledgers quotes
    uv run python -m data.pull_mes --pull         # quote + gate + download, newest first

Monthly chunks, pulled newest-first: if the gate closes part-way, what was
already bought is the most recent history, which is what Stage D weights
most. Each chunk is its own priced, ledgered, immutable request.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date

from data.adapter import (
    MES_CALENDAR_CONTINUOUS,
    MES_CONTINUOUS,
    OHLCV_1M,
    STYPE_CONTINUOUS,
    RawFileExistsError,
    fetch_range,
    raw_path,
    resolve_rolls,
    roll_cycle_violations,
    write_rolls,
)
from data.config import DATASET, STAGE_A1_SESSION_ID, VENDOR_ROOT, require_databento_key
from data.holdout import is_sealed_raw, request_touches_sealed_window
from data.spend_gate import BudgetRefusedError, RequestParams, SpendGate

WINDOW_START = date(2025, 4, 1)
WINDOW_END = date(2026, 9, 16)  # exclusive; today (2026-09-16) is not yet complete


def monthly_chunks(start: date, end: date) -> list[tuple[str, str]]:
    chunks: list[tuple[str, str]] = []
    cursor = start
    while cursor < end:
        nxt = date(cursor.year + (cursor.month == 12), cursor.month % 12 + 1, 1)
        chunks.append((cursor.isoformat(), min(nxt, end).isoformat()))
        cursor = nxt
    return chunks


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--quote-only", action="store_true")
    mode.add_argument("--pull", action="store_true")
    parser.add_argument("--rolls", action="store_true", help="resolve + store roll boundaries")
    args = parser.parse_args()

    import databento

    client = databento.Historical(require_databento_key())
    gate = SpendGate(STAGE_A1_SESSION_ID)
    print(f"dataset range: {client.metadata.get_dataset_range(dataset=DATASET)}")
    print(f"shared spent ${gate.shared_spent_usd():.4f} · session spent "
          f"${gate.session_spent_usd():.4f}")

    if args.rolls:
        for sym in (MES_CONTINUOUS, MES_CALENDAR_CONTINUOUS):
            rolls = resolve_rolls(client, sym, WINDOW_START.isoformat(), WINDOW_END.isoformat())
            path = VENDOR_ROOT / "rolls" / (
                f"{sym.replace('.', '_')}_{WINDOW_START}_{WINDOW_END}.jsonl"
            )
            try:
                write_rolls(rolls, path)
            except RawFileExistsError as exc:
                print(exc)
            print(f"{sym}: {len(rolls)} rolls; cycle violations: {roll_cycle_violations(rolls)}")
            for r in rolls:
                print(f"  {r.date}  {r.from_raw_symbol}->{r.to_raw_symbol}")

    chunks = list(reversed(monthly_chunks(WINDOW_START, WINDOW_END)))
    if args.quote_only and args.rolls:
        return 0
    if args.quote_only:
        total = 0.0
        for start, end in chunks:
            params = RequestParams(DATASET, (MES_CONTINUOUS,), OHLCV_1M, STYPE_CONTINUOUS,
                                   start, end)
            quote = gate.quote(client, params)
            if quote is None:
                print(f"{start}..{end}: UNPRICEABLE")
                continue
            total += quote.usd
            print(f"{start}..{end}: ${quote.usd:.6f} ({quote.billable_bytes:,} B)")
        print(f"TOTAL QUOTED ${total:.6f}")
        return 0

    for start, end in chunks:
        params = RequestParams(DATASET, (MES_CONTINUOUS,), OHLCV_1M, STYPE_CONTINUOUS, start, end)
        target = raw_path(MES_CONTINUOUS, OHLCV_1M, start, end)
        if request_touches_sealed_window(start, end):
            print(f"{start}..{end}: overlaps the sealed holdout window — skipped, not re-bought")
            continue
        if target.exists() or is_sealed_raw(target):
            print(f"{start}..{end}: already owned (on disk or sealed) — skipped, not re-bought")
            continue
        try:
            path = fetch_range(gate, client, params, note="Stage A.1 Task 2 MES ohlcv-1m")
        except BudgetRefusedError as exc:
            print(f"{start}..{end}: GATE REFUSED — {exc}. Stopping; see docs/ACCESS.md")
            break
        print(f"{start}..{end}: stored {path.name} · session ${gate.session_spent_usd():.4f}")
    print(f"session spent ${gate.session_spent_usd():.6f} · shared ${gate.shared_spent_usd():.6f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
