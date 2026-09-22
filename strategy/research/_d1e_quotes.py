"""Stage D.1e Tasks 4a/4b: MES availability and Databento cost QUOTES. No download.

    uv run python -m strategy.research._d1e_quotes

Budget for this stage is $0.00. Only free metadata and symbology endpoints are
called. Every priced request goes through :meth:`data.spend_gate.SpendGate.quote`,
which calls ``metadata.get_cost`` / ``metadata.get_billable_size`` and appends a
ledger line with ``usd = 0.0``. ``gate.authorize`` / ``gate.commit`` /
``gate.settle`` and ``data.adapter.fetch_range`` are never called, so no money
can move down any path this module can reach.

Belt and braces: immediately after the client is built, its two billable
namespaces are replaced by a guard object whose every attribute access raises.
See :func:`install_forbidden_guards` and ``tests/test_d1e_quotes.py``.

Outputs reports/stage_d1e_quotes.json and reports/stage_d1e_quotes.md.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from data.adapter import MES_CALENDAR_CONTINUOUS, MES_CONTINUOUS, OHLCV_1M, STYPE_CONTINUOUS
from data.config import (
    DATASET,
    EXTERNAL_LEDGER_PATHS,
    LEDGER_PATH,
    REPO_ROOT,
    VENDOR_ROOT,
    require_databento_key,
)
from data.pull_mes import monthly_chunks
from data.spend_gate import RequestParams, SpendGate, read_entries

# ---------------------------------------------------------------- guard ----
# The two billable client namespaces. Naming them as plain strings (never as
# attribute access in source) keeps this file free of any dotted call site.
FORBIDDEN_NAMESPACES = ("timeseries", "batch")
FORBIDDEN_MESSAGE = "D.1e: timeseries/batch forbidden"


class ForbiddenNamespace:
    """Stands in for a billable client namespace: every attribute access raises."""

    def __getattr__(self, name: str) -> Any:
        raise RuntimeError(FORBIDDEN_MESSAGE)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise RuntimeError(FORBIDDEN_MESSAGE)


def install_forbidden_guards(client: Any) -> Any:
    """Replace every billable namespace on ``client`` with a raising guard."""
    for name in FORBIDDEN_NAMESPACES:
        setattr(client, name, ForbiddenNamespace())
    return client


# ------------------------------------------------------------ constants ----
SESSION_ID = "stage-D.1e-2026-09-21"
CT = ZoneInfo("America/Chicago")

# The extension's exclusive end. data/vendor already holds
# range=2025-04-01_2025-05-01, so the last new chunk is 2025-03-01..2025-04-01.
EXTENSION_END = date(2025, 4, 1)
SEARCH_START = "2019-04-01"  # MES listed 2019-05-06; start the search before it

REQUIRED_SCHEMAS = ("ohlcv-1m", "mbo", "mbp-10", "trades", "definition", "statistics")
BOOK_SCHEMAS = ("mbo", "mbp-10")
SAMPLE_DAYS = ("2025-05-14", "2025-08-13", "2025-11-12", "2026-02-11", "2026-04-15")
BLOCK_START = "2025-10-01T00:00:00Z"
BLOCK_END = "2025-10-29T00:00:00Z"
BLOCK_TRADING_DAYS = 20
DAY_COUNTS = (20, 40, 60, 120)
PARENT_SYMBOL = "MES.FUT"

# Measured zstd ratio source: the one raw file whose billable size the ledger records.
REFERENCE_RAW = (
    VENDOR_ROOT / DATASET / OHLCV_1M / "MES_v_0" / "range=2025-04-01_2025-05-01.dbn.zst"
)
REFERENCE_BILLABLE_BYTES = 1_622_824  # ledger line for that range

MAIN_DRIVE_FREE_GB = 368.0
LARGE_STORAGE_FREE_GB = 770.0
LARGE_STORAGE_ROOT = "/mnt/large-storage"

EXPECTED_SHARED_CUMULATIVE_USD = 84.006048

# data/config.EXTERNAL_LEDGER_PATHS points at ~/Documents/GitHub/MLCryptoEngine,
# which has been moved. Read-only, never written. Verified 2026-09-21: 29 lines
# summing to $82.117874, which with this repo's $1.888175 reproduces
# shared_cumulative_usd = 84.006048 exactly -- the value on the last Stage A.1
# line. Without it SpendGate fails closed and nothing can be ledgered.
RELOCATED_EXTERNAL_LEDGER = Path(
    "/mnt/large-storage/Archive/GitHub/MLCryptoEngine/data/vendor/spend_ledger.jsonl"
)

JSON_PATH = REPO_ROOT / "reports" / "stage_d1e_quotes.json"
MD_PATH = REPO_ROOT / "reports" / "stage_d1e_quotes.md"

ENDPOINTS_CALLED = [
    "metadata.get_dataset_range", "metadata.list_schemas", "metadata.list_datasets",
    "metadata.get_dataset_condition", "metadata.get_cost", "metadata.get_billable_size",
    "symbology.resolve",
]
ENDPOINTS_NOT_CALLED = [
    "metadata.get_record_count (optional, not needed)",
    "every method under the two guarded billable namespaces (replaced by a raising guard)",
    "data.adapter.fetch_range, SpendGate.authorize, SpendGate.commit, SpendGate.settle",
]


# -------------------------------------------------------------- helpers ----
def iso_z(moment: datetime) -> str:
    """UTC ISO-8601 with a trailing Z, seconds resolution."""
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S") + "Z"


def rth_window_utc(day: date) -> tuple[str, str]:
    """08:30--15:10 America/Chicago on ``day``, converted (not assumed) to UTC."""
    start = datetime.combine(day, time(8, 30), tzinfo=CT)
    end = datetime.combine(day, time(15, 10), tzinfo=CT)
    return iso_z(start), iso_z(end)


def full_trade_date_window_utc(day: date) -> tuple[str, str]:
    """CME trade date ``day``: 17:00 CT the previous calendar day to 16:00 CT."""
    start = datetime.combine(day - timedelta(days=1), time(17, 0), tzinfo=CT)
    end = datetime.combine(day, time(16, 0), tzinfo=CT)
    return iso_z(start), iso_z(end)


def total_for_days(
    n_days: int, mean_usd_per_day: float, mean_bytes_per_day: float
) -> dict[str, float]:
    """Linear scaling of a measured mean per-day figure to ``n_days``.

    This is NOT a quote: Databento was never asked to price ``n_days``. It is
    the arithmetic mean over the five sampled days multiplied by ``n_days``.
    Order-book volume varies with volatility and with the roll cycle, so treat
    the result as a planning figure with maybe +/-30% spread, not a price. The
    ``block_quotes`` section of the JSON gives one real 20-day quote to check
    the linearity of this scaling against.
    """
    return {
        "days": n_days,
        "usd": mean_usd_per_day * n_days,
        "billable_bytes": mean_bytes_per_day * n_days,
    }


def repo_relative(path: Path) -> str:
    """Repo-relative when possible; the absolute path otherwise (tests use tmp dirs)."""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def ledger_length(path: Path = LEDGER_PATH) -> int:
    if not path.is_file():
        return 0
    return len([ln for ln in path.read_text().splitlines() if ln.strip()])


def vendor_listing() -> list[str]:
    if not VENDOR_ROOT.exists():
        return []
    return sorted(str(p.relative_to(REPO_ROOT)) for p in VENDOR_ROOT.rglob("*") if p.is_file())


def build_gate() -> tuple[SpendGate, str]:
    """A gate for this session, with the external ledger found wherever it lives."""
    paths = EXTERNAL_LEDGER_PATHS
    note = "data.config.EXTERNAL_LEDGER_PATHS used as configured"
    if not all(p.is_file() for p in paths):
        if not RELOCATED_EXTERNAL_LEDGER.is_file():
            raise FileNotFoundError(
                "the shared-account (MLCryptoEngine) ledger is missing from both the "
                f"configured path {paths} and {RELOCATED_EXTERNAL_LEDGER}; the gate fails "
                "closed and no quote can be ledgered"
            )
        paths = (RELOCATED_EXTERNAL_LEDGER,)
        note = (
            f"configured external ledger {paths} absent; used the relocated copy "
            f"{RELOCATED_EXTERNAL_LEDGER} (read-only). data/config.py NOT modified."
        )
    return SpendGate(SESSION_ID, external_ledger_paths=paths), note


def record_quote(
    gate: SpendGate, client: Any, params: RequestParams, label: str, sink: list[dict[str, Any]]
) -> dict[str, Any]:
    """One ledgered quote. Returns a record; never raises on a vendor refusal."""
    before = ledger_length(gate.ledger_path)
    quote = gate.quote(client, params)
    entries = read_entries(gate.ledger_path)
    line = entries[-1] if entries else {}
    record = {
        "label": label,
        "request": params.as_kwargs(),
        "ok": quote is not None,
        "usd": None if quote is None else quote.usd,
        "billable_bytes": None if quote is None else quote.billable_bytes,
        "ledger_index_0based": len(entries) - 1,
        "ledger_ts": line.get("ts"),
        "ledger_note": line.get("note", ""),
        "ledger_lines_appended": len(entries) - before,
    }
    sink.append(record)
    money = "UNPRICEABLE" if quote is None else f"${quote.usd:.6f}"
    size = "-" if quote is None else f"{quote.billable_bytes:,} B"
    print(f"  [{record['ledger_index_0based']}] {label}: {money} ({size})")
    return record


# --------------------------------------------------------- 4a availability -
def symbol_history(client: Any, symbol: str) -> dict[str, Any]:
    """Continuous-symbol instrument intervals over the search range."""
    out: dict[str, Any] = {"symbol": symbol}
    try:
        raw = client.symbology.resolve(
            dataset=DATASET, symbols=[symbol], stype_in=STYPE_CONTINUOUS,
            stype_out="instrument_id", start_date=SEARCH_START,
            end_date=EXTENSION_END.isoformat(),
        )
    except Exception as exc:  # noqa: BLE001 -- record, do not crash the run
        out["error"] = f"{type(exc).__name__}: {exc}"
        return out
    out["raw_response_keys"] = sorted(raw.keys())
    out["not_found"] = list(raw.get("not_found", []))
    out["partial"] = list(raw.get("partial", []))
    intervals = sorted(raw["result"].get(symbol, []), key=lambda e: str(e["d0"]))
    out["interval_count"] = len(intervals)
    out["intervals"] = intervals
    if not intervals:
        out["first_d0"] = None
        return out
    out["first_d0"] = str(intervals[0]["d0"])
    out["first_instrument_id"] = str(intervals[0]["s"])
    changes: list[str] = []
    for previous, current in zip(intervals, intervals[1:], strict=False):
        if str(previous["s"]) != str(current["s"]):
            changes.append(str(current["d0"]))
    out["instrument_change_dates"] = changes
    out["instrument_changes_per_year"] = dict(sorted(Counter(d[:4] for d in changes).items()))
    # raw symbols of the first two distinct instrument ids, each looked up over
    # the dates on which the continuous symbol actually mapped to that id
    seen: list[dict[str, Any]] = []
    for interval in intervals:
        if not seen or str(seen[-1]["s"]) != str(interval["s"]):
            seen.append(interval)
        if len(seen) == 2:
            break
    named = []
    for interval in seen:
        entry: dict[str, Any] = {
            "instrument_id": str(interval["s"]),
            "d0": str(interval["d0"]),
            "d1": str(interval["d1"]),
        }
        try:
            res = client.symbology.resolve(
                dataset=DATASET, symbols=[str(interval["s"])], stype_in="instrument_id",
                stype_out="raw_symbol", start_date=str(interval["d0"]),
                end_date=str(interval["d1"]),
            )
            entry["raw_response"] = res
            entry["raw_symbols"] = [
                str(e["s"]) for e in res["result"].get(str(interval["s"]), [])
            ]
        except Exception as exc:  # noqa: BLE001
            entry["error"] = f"{type(exc).__name__}: {exc}"
        named.append(entry)
    out["first_two_instruments"] = named
    return out


def dataset_condition(client: Any) -> dict[str, Any]:
    out: dict[str, Any] = {}
    try:
        cond = client.metadata.get_dataset_condition(
            dataset=DATASET, start_date=SEARCH_START, end_date=EXTENSION_END.isoformat()
        )
    except Exception as exc:  # noqa: BLE001
        return {"error": f"{type(exc).__name__}: {exc}"}
    out["record_count"] = len(cond)
    out["raw_response"] = cond
    per_year: dict[str, Counter[str]] = {}
    for row in cond:
        per_year.setdefault(str(row["date"])[:4], Counter())[str(row["condition"])] += 1
    out["per_year"] = {y: dict(sorted(c.items())) for y, c in sorted(per_year.items())}
    out["conditions_seen"] = sorted({str(r["condition"]) for r in cond})
    out["not_available_dates"] = [
        {"date": str(r["date"]), "condition": str(r["condition"]),
         "last_modified_date": str(r.get("last_modified_date"))}
        for r in cond if str(r["condition"]) != "available"
    ]
    return out


def availability(client: Any) -> dict[str, Any]:
    out: dict[str, Any] = {}
    print("4a.1 dataset range and schemas")
    out["dataset_range"] = client.metadata.get_dataset_range(dataset=DATASET)
    schemas = list(client.metadata.list_schemas(dataset=DATASET))
    out["schemas"] = schemas
    out["required_schemas_present"] = {s: (s in schemas) for s in REQUIRED_SCHEMAS}
    out["missing_required_schemas"] = [s for s in REQUIRED_SCHEMAS if s not in schemas]
    try:
        datasets = list(client.metadata.list_datasets())
        out["datasets"] = datasets
        out["glbx_mdp3_listed"] = DATASET in datasets
    except Exception as exc:  # noqa: BLE001
        out["datasets_error"] = f"{type(exc).__name__}: {exc}"
    print(f"      range={out['dataset_range']} schemas={len(schemas)}")

    print("4a.2 symbology: first date MES exists")
    out["symbols"] = {
        sym: symbol_history(client, sym) for sym in (MES_CONTINUOUS, MES_CALENDAR_CONTINUOUS)
    }
    for sym, hist in out["symbols"].items():
        print(f"      {sym}: first d0={hist.get('first_d0')} "
              f"intervals={hist.get('interval_count')}")

    print("4a.3 dataset condition 2019-04-01..2025-04-01")
    out["condition"] = dataset_condition(client)
    print(f"      rows={out['condition'].get('record_count')} "
          f"not-available={len(out['condition'].get('not_available_dates', []))}")
    return out


def boundary_note(first_chunk_start: str) -> dict[str, Any]:
    return {
        "existing_raw_first_chunk": "range=2025-04-01_2025-05-01",
        "existing_raw_starts_utc": "2025-04-01T00:00:00Z",
        "extension_last_chunk": "range=2025-03-01_2025-04-01",
        "extension_first_chunk_start": first_chunk_start,
        "extension_end_exclusive": EXTENSION_END.isoformat(),
        "statement": (
            "The current raw data begins at UTC 2025-04-01T00:00 (range="
            "2025-04-01_2025-05-01), so the extension's last chunk must END at "
            "2025-04-01 (exclusive end), i.e. range=2025-03-01_2025-04-01. That gives "
            "no overlap and no gap in UTC time."
        ),
        "trade_date_caveat": (
            "The 2025-03-31 22:00-24:00 UTC bars inside range=2025-03-01_2025-04-01 belong "
            "to CME trade date 2025-04-01 -- the research parquet's first trade date, which "
            "currently starts late and is missing its 17:00-19:00 CT open. Extending the raw "
            "data would therefore complete an existing research trade date as well as add new "
            "ones. How D.1f treats those bars (complete the existing first trade date, or drop "
            "it and start the extended series at the first fully covered trade date) is a "
            "LEAD decision, not made here."
        ),
    }


# --------------------------------------------------------- 4b extension ----
def extension_quotes(
    gate: SpendGate, client: Any, first_available: date, sink: list[dict[str, Any]]
) -> dict[str, Any]:
    first_month = date(first_available.year, first_available.month, 1)
    chunks = monthly_chunks(first_month, EXTENSION_END)
    print(f"4b.5 extension ohlcv-1m: {len(chunks)} monthly chunks "
          f"{first_month}..{EXTENSION_END}")
    records = []
    for start, end in chunks:
        params = RequestParams(DATASET, (MES_CONTINUOUS,), OHLCV_1M, STYPE_CONTINUOUS, start, end)
        records.append(record_quote(gate, client, params, f"ext ohlcv-1m {start}..{end}", sink))
    priced = [r for r in records if r["ok"]]
    whole = RequestParams(
        DATASET, (MES_CONTINUOUS,), OHLCV_1M, STYPE_CONTINUOUS,
        first_month.isoformat(), EXTENSION_END.isoformat(),
    )
    whole_record = record_quote(
        gate, client, whole,
        f"ext ohlcv-1m WHOLE RANGE {first_month}..{EXTENSION_END}", sink,
    )
    total_usd = sum(r["usd"] for r in priced)
    total_bytes = sum(r["billable_bytes"] for r in priced)
    return {
        "first_month": first_month.isoformat(),
        "end_exclusive": EXTENSION_END.isoformat(),
        "chunk_count": len(chunks),
        "priced_chunk_count": len(priced),
        "unpriceable_chunks": [r["label"] for r in records if not r["ok"]],
        "chunks": records,
        "sum_of_chunks_usd": total_usd,
        "sum_of_chunks_billable_bytes": total_bytes,
        "whole_range_quote": whole_record,
        "whole_vs_sum_usd_delta": (
            None if not whole_record["ok"] else whole_record["usd"] - total_usd
        ),
        "whole_vs_sum_bytes_delta": (
            None if not whole_record["ok"] else whole_record["billable_bytes"] - total_bytes
        ),
    }


def auxiliary_schema_finding() -> dict[str, Any]:
    """What the bar pipeline needs besides ohlcv-1m. Established by reading, not quoting."""
    return {
        "paid_schemas_besides_ohlcv_1m": [],
        "conclusion": (
            "The pipeline needs only the paid schema ohlcv-1m, plus free metadata and "
            "symbology. No auxiliary paid schema was quoted because none is used."
        ),
        "evidence": [
            {"file": "data/adapter.py", "line": 43,
             "text": 'OHLCV_1M = "ohlcv-1m"',
             "why": "the only schema constant in the data package"},
            {"file": "data/pull_mes.py", "lines": "83, 95",
             "text": "RequestParams(DATASET, (MES_CONTINUOUS,), OHLCV_1M, STYPE_CONTINUOUS, ...)",
             "why": "the only two RequestParams construction sites outside tests; "
                    "both pass OHLCV_1M"},
            {"file": "data/adapter.py", "line": 85,
             "text": "def fetch_range(gate, client, params, root=VENDOR_ROOT, note='')",
             "why": "the only download path; its sole non-test caller is "
                    "data/pull_mes.py:104, which passes an ohlcv-1m params"},
            {"file": "data/build_mes_bars.py", "lines": "41-53",
             "text": "client.metadata.get_dataset_condition(dataset=DATASET, ...)",
             "why": "the vendor_degraded_day source; free metadata, cached to "
                    "data/vendor/databento/condition/ and never rewritten"},
            {"file": "data/adapter.py", "lines": "162-180",
             "text": "client.symbology.resolve(... stype_out='instrument_id' / 'raw_symbol')",
             "why": "roll boundaries; the module docstring states symbology is "
                    "metadata-only and free, so it never touches the spend gate"},
            {"file": "data/pull_mes.py", "line": 58,
             "text": "client.metadata.get_dataset_range(dataset=DATASET)",
             "why": "free metadata, printed at startup"},
            {"file": "data/bars.py", "lines": "17, 127",
             "text": "vendor_degraded_day flag column",
             "why": "consumes the cached condition list; buys nothing"},
            {"file": "data/tick_crosscheck.py", "lines": "1-10, 40, 107",
             "text": "MLCE_VENDOR / f'date={day}' / 'MES_c_0.trades.dbn.zst'",
             "why": "the only use of the trades schema anywhere; it reads "
                    "MLCryptoEngine's already-paid-for files IN PLACE, read-only, and "
                    "never buys trades on this account"},
            {"file": "data/validate.py", "lines": "7-9",
             "text": "ts_recv ordering check applies to the tick data (trades / mbp-10)",
             "why": "a comment about borrowed tick data, not a purchase by this pipeline"},
        ],
        "consequence_for_the_extension": (
            "Extending ohlcv-1m back before 2025-04-01 needs exactly one paid schema. "
            "get_dataset_condition and symbology.resolve must be re-run over the extended "
            "range so vendor_degraded_day and the roll boundaries cover it, but both are free."
        ),
    }


# -------------------------------------------------------- 4b order book ----
def front_raw_symbol(client: Any, day: date) -> str | None:
    try:
        res = client.symbology.resolve(
            dataset=DATASET, symbols=[MES_CONTINUOUS], stype_in=STYPE_CONTINUOUS,
            stype_out="raw_symbol", start_date=day.isoformat(),
            end_date=(day + timedelta(days=1)).isoformat(),
        )
    except Exception:  # noqa: BLE001
        return None
    entries = res["result"].get(MES_CONTINUOUS, [])
    return str(entries[0]["s"]) if entries else None


def book_quote_with_fallback(
    gate: SpendGate, client: Any, schema: str, start: str, end: str, label: str,
    day: date, sink: list[dict[str, Any]],
) -> dict[str, Any]:
    """Quote a book request, falling back continuous -> raw front month -> parent."""
    attempts: list[dict[str, Any]] = []
    forms = [("continuous", (MES_CONTINUOUS,), STYPE_CONTINUOUS)]
    record = record_quote(
        gate, client,
        RequestParams(DATASET, forms[0][1], schema, forms[0][2], start, end),
        f"{label} [continuous]", sink,
    )
    attempts.append({"symbol_form": "continuous MES.v.0", **record})
    if not record["ok"]:
        raw = front_raw_symbol(client, day)
        if raw:
            record = record_quote(
                gate, client,
                RequestParams(DATASET, (raw,), schema, "raw_symbol", start, end),
                f"{label} [raw {raw}]", sink,
            )
            attempts.append({"symbol_form": f"raw_symbol {raw}", **record})
    if not record["ok"]:
        record = record_quote(
            gate, client,
            RequestParams(DATASET, (PARENT_SYMBOL,), schema, "parent", start, end),
            f"{label} [parent {PARENT_SYMBOL}]", sink,
        )
        attempts.append({"symbol_form": f"parent {PARENT_SYMBOL}", **record})
    return {
        "schema": schema, "start": start, "end": end,
        "symbol_form_used": attempts[-1]["symbol_form"] if record["ok"] else None,
        "ok": record["ok"], "usd": record["usd"], "billable_bytes": record["billable_bytes"],
        "attempts": attempts,
    }


def orderbook_quotes(
    gate: SpendGate, client: Any, sink: list[dict[str, Any]]
) -> dict[str, Any]:
    print("4b.7 order-book sample days")
    per_day: list[dict[str, Any]] = []
    for day_str in SAMPLE_DAYS:
        day = date.fromisoformat(day_str)
        rth = rth_window_utc(day)
        full = full_trade_date_window_utc(day)
        offset = datetime.combine(day, time(8, 30), tzinfo=CT).utcoffset()
        entry: dict[str, Any] = {
            "day": day_str,
            "ct_utc_offset_hours": offset.total_seconds() / 3600 if offset else None,
            "rth_window_utc": {"start": rth[0], "end": rth[1]},
            "full_trade_date_window_utc": {"start": full[0], "end": full[1]},
            "front_raw_symbol": front_raw_symbol(client, day),
            "quotes": {},
        }
        print(f"    {day_str} CT offset {entry['ct_utc_offset_hours']}h "
              f"RTH {rth[0]}..{rth[1]} front {entry['front_raw_symbol']}")
        for schema in BOOK_SCHEMAS:
            entry["quotes"][f"{schema}/rth"] = book_quote_with_fallback(
                gate, client, schema, rth[0], rth[1], f"{schema} RTH {day_str}", day, sink
            )
            entry["quotes"][f"{schema}/full"] = book_quote_with_fallback(
                gate, client, schema, full[0], full[1], f"{schema} FULL {day_str}", day, sink
            )
        per_day.append(entry)

    print("4b.8 20-day contiguous block quotes")
    blocks: dict[str, Any] = {}
    for schema in BOOK_SCHEMAS:
        blocks[schema] = book_quote_with_fallback(
            gate, client, schema, BLOCK_START, BLOCK_END,
            f"{schema} BLOCK {BLOCK_START}..{BLOCK_END}", date(2025, 10, 1), sink,
        )

    means: dict[str, Any] = {}
    for schema in BOOK_SCHEMAS:
        for variant in ("rth", "full"):
            key = f"{schema}/{variant}"
            got = [d["quotes"][key] for d in per_day if d["quotes"][key]["ok"]]
            means[key] = {
                "sampled_days": len(got),
                "mean_usd_per_day": (sum(g["usd"] for g in got) / len(got)) if got else None,
                "mean_billable_bytes_per_day": (
                    sum(g["billable_bytes"] for g in got) / len(got) if got else None
                ),
                "min_usd": min((g["usd"] for g in got), default=None),
                "max_usd": max((g["usd"] for g in got), default=None),
            }

    scalings: dict[str, Any] = {}
    for key, m in means.items():
        if m["mean_usd_per_day"] is None:
            scalings[key] = {"error": "no priced sample day"}
            continue
        scalings[key] = {
            str(n): total_for_days(n, m["mean_usd_per_day"], m["mean_billable_bytes_per_day"])
            for n in DAY_COUNTS
        }

    linearity: dict[str, Any] = {}
    for schema in BOOK_SCHEMAS:
        block = blocks[schema]
        m = means[f"{schema}/full"]
        if block["ok"] and m["mean_usd_per_day"] is not None:
            scaled = m["mean_usd_per_day"] * BLOCK_TRADING_DAYS
            linearity[schema] = {
                "block_quoted_usd": block["usd"],
                "block_quoted_billable_bytes": block["billable_bytes"],
                "scaled_from_full_day_mean_usd": scaled,
                "ratio_block_over_scaled": block["usd"] / scaled if scaled else None,
                "note": (
                    "The block covers 2025-10-01..2025-10-29 UTC as one contiguous request, "
                    "which includes weekends (no data) as well as 20 trading days, so it is "
                    "comparable to 20 x the full-trade-date mean."
                ),
            }
        else:
            linearity[schema] = {"error": "block or per-day mean unavailable"}

    return {
        "sample_days": list(SAMPLE_DAYS),
        "rth_definition_ct": "08:30 to 15:10 America/Chicago",
        "full_trade_date_definition_ct": "17:00 CT previous calendar day to 16:00 CT",
        "per_day": per_day,
        "block_quotes": blocks,
        "means": means,
        "scalings_linear": scalings,
        "scaling_caveat": (
            "Every 20/40/60/120-day figure is a LINEAR SCALING of the five-day mean, not a "
            "quote. See total_for_days() in strategy/research/_d1e_quotes.py."
        ),
        "linearity_check": linearity,
    }


# -------------------------------------------------------------- 10 disk ----
def disk_table(extension: dict[str, Any], book: dict[str, Any]) -> dict[str, Any]:
    on_disk = REFERENCE_RAW.stat().st_size if REFERENCE_RAW.is_file() else None
    ratio = on_disk / REFERENCE_BILLABLE_BYTES if on_disk else None
    rows: list[dict[str, Any]] = []

    ext_bytes = extension["sum_of_chunks_billable_bytes"]
    rows.append({
        "dataset": f"ohlcv-1m extension {extension['first_month']}..{extension['end_exclusive']}",
        "days": None,
        "billable_bytes": ext_bytes,
        "billable_mib": ext_bytes / 1024**2,
        "est_disk_bytes": ext_bytes * ratio if ratio else None,
        "est_disk_mib": (ext_bytes * ratio) / 1024**2 if ratio else None,
        "ratio_is_measured_for_this_schema": True,
        "estimate_quality": "measured ratio, same schema and symbol as the reference file",
        "drive": "main drive, beside the existing raw files",
    })
    for schema in BOOK_SCHEMAS:
        for variant in ("rth", "full"):
            m = book["means"][f"{schema}/{variant}"]
            if m["mean_billable_bytes_per_day"] is None:
                continue
            for n in DAY_COUNTS:
                b = m["mean_billable_bytes_per_day"] * n
                rows.append({
                    "dataset": f"{schema} {variant} x{n} days",
                    "days": n,
                    "billable_bytes": b,
                    "billable_mib": b / 1024**2,
                    "est_disk_bytes": b * ratio if ratio else None,
                    "est_disk_gib": (b * ratio) / 1024**3 if ratio else None,
                    "ratio_is_measured_for_this_schema": False,
                    "estimate_quality": (
                        "ESTIMATE ONLY -- the ratio was measured on ohlcv-1m; book data "
                        "usually compresses differently (mbo in particular)"
                    ),
                    "drive": LARGE_STORAGE_ROOT,
                })
    return {
        "reference_file": repo_relative(REFERENCE_RAW) if on_disk else None,
        "reference_on_disk_bytes": on_disk,
        "reference_billable_bytes": REFERENCE_BILLABLE_BYTES,
        "zstd_ratio_on_disk_over_billable": ratio,
        "ratio_caveat": (
            "Measured on one month of MES ohlcv-1m. Book schemas compress differently, so "
            "every mbo / mbp-10 disk figure below is an estimate, not a measurement."
        ),
        "free_space": {
            "main_drive_gb": MAIN_DRIVE_FREE_GB,
            "large_storage_gb": LARGE_STORAGE_FREE_GB,
            "large_storage_root": LARGE_STORAGE_ROOT,
        },
        "rows": rows,
        "recommendation": {
            "ohlcv-1m extension": (
                "main drive, data/vendor/databento/GLBX.MDP3/ohlcv-1m/MES_v_0/, beside the "
                "existing monthly chunks -- it is small and the bar pipeline reads it by path"
            ),
            "mbo / mbp-10": (
                f"{LARGE_STORAGE_ROOT} -- bulk order-book data only; nothing secret is ever "
                "written there, and the sealed holdout stays on the main drive"
            ),
        },
    }


# ------------------------------------------------------- 11 accounting ----
def ledger_accounting(
    before_count: int, before_vendor: list[str], quotes: list[dict[str, Any]],
    ledger_path: Path = LEDGER_PATH,
) -> dict[str, Any]:
    entries = read_entries(ledger_path)
    after_count = len(entries)
    new = entries[before_count:]
    after_vendor = vendor_listing()
    checks = {
        "every_new_line_is_a_quote": all(e.get("event") == "quote" for e in new),
        "every_new_line_usd_is_zero": all(float(e.get("usd", -1)) == 0.0 for e in new),
        "no_commit_settle_or_refused_added": not any(
            e.get("event") in ("commit", "settle", "refused") for e in new
        ),
        "no_new_vendor_file": before_vendor == after_vendor,
        "new_line_count_matches_quote_records": len(new) == len(quotes),
        "shared_cumulative_unchanged": (
            bool(new) and float(new[-1]["shared_cumulative_usd"]) == EXPECTED_SHARED_CUMULATIVE_USD
        ),
        "session_cumulative_is_zero": all(
            float(e.get("session_cumulative_usd", -1)) == 0.0 for e in new
        ),
    }
    return {
        "ledger_path": repo_relative(ledger_path),
        "lines_before": before_count,
        "lines_after": after_count,
        "lines_added": after_count - before_count,
        "new_line_indices_0based": list(range(before_count, after_count)),
        "new_line_events": dict(Counter(e.get("event") for e in new)),
        "new_line_sessions": dict(Counter(e.get("session_id") for e in new)),
        "sum_usd_of_new_lines": sum(float(e.get("usd", 0.0)) for e in new),
        "unpriceable_new_lines": [
            {"index": before_count + i, "note": e.get("note")}
            for i, e in enumerate(new) if e.get("quoted_usd") is None
        ],
        "expected_shared_cumulative_usd": EXPECTED_SHARED_CUMULATIVE_USD,
        "observed_shared_cumulative_usd": (
            float(new[-1]["shared_cumulative_usd"]) if new else None
        ),
        "vendor_files_before": len(before_vendor),
        "vendor_files_after": len(after_vendor),
        "vendor_files_added": sorted(set(after_vendor) - set(before_vendor)),
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


# ------------------------------------------------------------- markdown ----
def usd(value: float | None) -> str:
    return "n/a" if value is None else f"${value:.4f}"


def mib(value: float | None) -> str:
    """Bytes as MiB, or GiB once the number stops being readable in MiB."""
    if value is None:
        return "n/a"
    if value >= 1024**3:
        return f"{value / 1024**3:,.2f} GiB"
    return f"{value / 1024**2:,.1f} MiB"


def render_markdown(doc: dict[str, Any]) -> str:
    av, ext, book, disk, acct = (
        doc["availability"], doc["extension"], doc["orderbook"],
        doc["disk"], doc["ledger_accounting"],
    )
    L: list[str] = []
    a = L.append
    a("# Stage D.1e Tasks 4a/4b: MES availability and Databento cost quotes")
    a("")
    a(f"Generated {doc['generated_utc']} · session `{doc['session_id']}` · "
      f"**spend this run: $0.00** (quotes only, nothing downloaded).")
    a("")
    a(f"Gate note: {doc['gate_note']}")
    a("")
    a("## 1. Availability (4a)")
    a("")
    a(f"- `metadata.get_dataset_range(\"{DATASET}\")` -> `{av['dataset_range']}`")
    a(f"- `metadata.list_schemas(\"{DATASET}\")` -> {len(av['schemas'])} schemas")
    a("")
    a("| schema | present |")
    a("|---|---|")
    for s, present in av["required_schemas_present"].items():
        a(f"| `{s}` | {'yes' if present else '**NO**'} |")
    a("")
    a("### First date MES exists")
    a("")
    a("| symbol | first `d0` | intervals | instrument changes per year |")
    a("|---|---|---|---|")
    for sym, hist in av["symbols"].items():
        if "error" in hist:
            a(f"| `{sym}` | ERROR | - | {hist['error']} |")
            continue
        per_year = hist.get("instrument_changes_per_year", {})
        a(f"| `{sym}` | {hist.get('first_d0')} | {hist.get('interval_count')} | "
          f"{', '.join(f'{y}:{n}' for y, n in per_year.items())} |")
    a("")
    for sym, hist in av["symbols"].items():
        for entry in hist.get("first_two_instruments", []):
            names = entry.get("raw_symbols") or [entry.get("error", "unresolved")]
            a(f"- `{sym}` instrument `{entry['instrument_id']}` "
              f"({entry['d0']}..{entry['d1']}) -> raw symbol(s) {names}")
    a("")
    a("### Dataset condition 2019-04-01 to 2025-04-01")
    a("")
    cond = av["condition"]
    if "error" in cond:
        a(f"ERROR: {cond['error']}")
    else:
        years = sorted(cond["per_year"])
        seen = cond["conditions_seen"]
        a("| year | " + " | ".join(seen) + " |")
        a("|---|" + "---|" * len(seen))
        for y in years:
            row = cond["per_year"][y]
            a(f"| {y} | " + " | ".join(str(row.get(c, 0)) for c in seen) + " |")
        a("")
        bad = cond["not_available_dates"]
        a(f"Dates not `available`: **{len(bad)}**")
        if bad:
            a("")
            a("| date | condition | last modified |")
            a("|---|---|---|")
            for r in bad:
                a(f"| {r['date']} | {r['condition']} | {r['last_modified_date']} |")
    a("")
    a("### Boundary")
    a("")
    a(doc["boundary"]["statement"])
    a("")
    a(f"Trade-date caveat: {doc['boundary']['trade_date_caveat']}")
    a("")
    a("## 2. ohlcv-1m extension quote (4b.5)")
    a("")
    a(f"- range: **{ext['first_month']} .. {ext['end_exclusive']}** (end exclusive)")
    a(f"- monthly chunks: **{ext['chunk_count']}** ({ext['priced_chunk_count']} priced)")
    a(f"- **sum of chunk quotes: {usd(ext['sum_of_chunks_usd'])}**, "
      f"{ext['sum_of_chunks_billable_bytes']:,} billable bytes "
      f"({mib(ext['sum_of_chunks_billable_bytes'])})")
    w = ext["whole_range_quote"]
    a(f"- single whole-range quote: {usd(w['usd'])}, "
      f"{(w['billable_bytes'] or 0):,} billable bytes")
    a(f"- whole minus sum: {usd(ext['whole_vs_sum_usd_delta'])}, "
      f"{ext['whole_vs_sum_bytes_delta']} bytes")
    if ext["unpriceable_chunks"]:
        a(f"- UNPRICEABLE chunks: {ext['unpriceable_chunks']}")
    a("")
    a("<details><summary>Per-chunk quotes</summary>")
    a("")
    a("| chunk | ledger idx | usd | billable bytes |")
    a("|---|---|---|---|")
    for r in ext["chunks"]:
        a(f"| {r['request']['start']}..{r['request']['end']} | {r['ledger_index_0based']} | "
          f"{usd(r['usd'])} | {(r['billable_bytes'] or 0):,} |")
    a("")
    a("</details>")
    a("")
    a("## 3. Auxiliary schemas (4b.6)")
    a("")
    a(doc["auxiliary_schemas"]["conclusion"])
    a("")
    for e in doc["auxiliary_schemas"]["evidence"]:
        where = e.get("line") or e.get("lines")
        a(f"- `{e['file']}:{where}` — `{e['text']}` — {e['why']}")
    a("")
    a(doc["auxiliary_schemas"]["consequence_for_the_extension"])
    a("")
    a("## 4. Order book (4b.7 to 4b.9)")
    a("")
    a(f"RTH = {book['rth_definition_ct']}; full trade date = "
      f"{book['full_trade_date_definition_ct']}. Offsets computed with "
      "`zoneinfo` (CDT/CST differ).")
    a("")
    a("| day | CT offset | RTH UTC | front month | "
      "mbo RTH | mbo full | mbp-10 RTH | mbp-10 full |")
    a("|---|---|---|---|---|---|---|---|")
    for d in book["per_day"]:
        q = d["quotes"]
        a(f"| {d['day']} | UTC{d['ct_utc_offset_hours']:+g} | "
          f"{d['rth_window_utc']['start'][11:16]}–{d['rth_window_utc']['end'][11:16]}Z | "
          f"{d['front_raw_symbol']} | "
          f"{usd(q['mbo/rth']['usd'])} | {usd(q['mbo/full']['usd'])} | "
          f"{usd(q['mbp-10/rth']['usd'])} | {usd(q['mbp-10/full']['usd'])} |")
    a("")
    a("Billable bytes per day:")
    a("")
    a("| day | mbo RTH | mbo full | mbp-10 RTH | mbp-10 full |")
    a("|---|---|---|---|---|")
    for d in book["per_day"]:
        q = d["quotes"]
        a(f"| {d['day']} | " + " | ".join(
            mib(q[k]["billable_bytes"]) for k in
            ("mbo/rth", "mbo/full", "mbp-10/rth", "mbp-10/full")
        ) + " |")
    a("")
    a("Symbol form used (fallback chain continuous -> raw front month -> parent):")
    a("")
    keys = ("mbo/rth", "mbo/full", "mbp-10/rth", "mbp-10/full")
    for key in keys:
        tally = Counter(
            str(d["quotes"][key]["symbol_form_used"]) for d in book["per_day"]
        )
        a(f"- {key}: " + ", ".join(f"{form} x{n}" for form, n in sorted(tally.items())))
    a("")
    a("### Means and linear scalings")
    a("")
    a("| series | days sampled | mean $/day | mean bytes/day | "
      "20 d | 40 d | 60 d | 120 d |")
    a("|---|---|---|---|---|---|---|---|")
    for key, m in book["means"].items():
        sc = book["scalings_linear"].get(key, {})
        if m["mean_usd_per_day"] is None:
            a(f"| {key} | 0 | n/a | n/a | n/a | n/a | n/a | n/a |")
            continue
        cells = " | ".join(usd(sc[str(n)]["usd"]) for n in DAY_COUNTS)
        a(f"| {key} | {m['sampled_days']} | {usd(m['mean_usd_per_day'])} | "
          f"{mib(m['mean_billable_bytes_per_day'])} | {cells} |")
    a("")
    a(book["scaling_caveat"])
    a("")
    a("### 20-day contiguous block quotes (linearity check)")
    a("")
    a(f"Range {BLOCK_START} .. {BLOCK_END}.")
    a("")
    a("| schema | block quote | scaled 20 x full-day mean | ratio |")
    a("|---|---|---|---|")
    for schema in BOOK_SCHEMAS:
        lin = book["linearity_check"][schema]
        if "error" in lin:
            a(f"| {schema} | {lin['error']} | | |")
            continue
        a(f"| {schema} | {usd(lin['block_quoted_usd'])} | "
          f"{usd(lin['scaled_from_full_day_mean_usd'])} | "
          f"{lin['ratio_block_over_scaled']:.3f} |")
    a("")
    a("## 5. Disk footprint (4b.10)")
    a("")
    a(f"Measured zstd ratio: {disk['reference_on_disk_bytes']:,} bytes on disk / "
      f"{disk['reference_billable_bytes']:,} billable = "
      f"**{disk['zstd_ratio_on_disk_over_billable']:.4f}** "
      f"(`{disk['reference_file']}`).")
    a("")
    a(disk["ratio_caveat"])
    a("")
    a(f"Free space: main drive ~{disk['free_space']['main_drive_gb']:.0f} GB, "
      f"`{LARGE_STORAGE_ROOT}` ~{disk['free_space']['large_storage_gb']:.0f} GB.")
    a("")
    a("| dataset | billable | est. on disk | quality | drive |")
    a("|---|---|---|---|---|")
    for r in disk["rows"]:
        est = r.get("est_disk_bytes")
        est_s = "n/a" if est is None else (
            f"{est / 1024**3:,.2f} GiB" if est >= 1024**3 else f"{est / 1024**2:,.1f} MiB"
        )
        short = "measured ratio" if r["ratio_is_measured_for_this_schema"] else "ESTIMATE"
        a(f"| {r['dataset']} | {mib(r['billable_bytes'])} | {est_s} | {short} | {r['drive']} |")
    a("")
    a("**Recommendation**")
    a("")
    for k, v in disk["recommendation"].items():
        a(f"- {k}: {v}")
    a("")
    a("## 6. Ledger accounting (4b.11)")
    a("")
    a(f"- `{acct['ledger_path']}`: **{acct['lines_before']} lines before, "
      f"{acct['lines_after']} after** ({acct['lines_added']} added)")
    a(f"- new line indices (0-based): {acct['new_line_indices_0based'][0]}"
      f"..{acct['new_line_indices_0based'][-1]}" if acct["new_line_indices_0based"]
      else "- no new lines")
    a(f"- events on new lines: {acct['new_line_events']}")
    a(f"- sum of `usd` on new lines: ${acct['sum_usd_of_new_lines']:.4f}")
    a(f"- `shared_cumulative_usd`: {acct['observed_shared_cumulative_usd']} "
      f"(expected {acct['expected_shared_cumulative_usd']})")
    a(f"- files under `data/vendor`: {acct['vendor_files_before']} before, "
      f"{acct['vendor_files_after']} after; added {acct['vendor_files_added']}")
    if acct["unpriceable_new_lines"]:
        a(f"- unpriceable quotes: {len(acct['unpriceable_new_lines'])} "
          "(see JSON for the vendor error on each)")
    a("")
    a("| check | result |")
    a("|---|---|")
    for k, v in acct["checks"].items():
        a(f"| {k} | {'PASS' if v else '**FAIL**'} |")
    a("")
    a("## 7. Endpoints")
    a("")
    a("Called (all free): " + ", ".join(f"`{e}`" for e in doc["endpoints_called"]))
    a("")
    a("Not called:")
    for e in doc["endpoints_not_called"]:
        a(f"- {e}")
    a("")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ main ---
def main() -> int:
    import databento

    gate, gate_note = build_gate()
    before_count = ledger_length(gate.ledger_path)
    before_vendor = vendor_listing()
    print(f"ledger lines before: {before_count} · vendor files before: {len(before_vendor)}")
    print(f"gate: {gate_note}")

    client = install_forbidden_guards(databento.Historical(require_databento_key()))

    quotes: list[dict[str, Any]] = []
    av = availability(client)

    first_d0 = av["symbols"][MES_CONTINUOUS].get("first_d0")
    if not first_d0:
        print("FATAL: symbology returned no interval for MES.v.0; cannot build a chunk list")
        return 2
    first_available = date.fromisoformat(first_d0)

    ext = extension_quotes(gate, client, first_available, quotes)
    aux = auxiliary_schema_finding()
    book = orderbook_quotes(gate, client, quotes)
    disk = disk_table(ext, book)
    acct = ledger_accounting(before_count, before_vendor, quotes, gate.ledger_path)

    doc = {
        "session_id": SESSION_ID,
        "generated_utc": datetime.now(UTC).isoformat(),
        "budget_usd": 0.0,
        "spend_this_run_usd": 0.0,
        "gate_note": gate_note,
        "availability": av,
        "boundary": boundary_note(date(first_available.year, first_available.month, 1).isoformat()),
        "extension": ext,
        "auxiliary_schemas": aux,
        "orderbook": book,
        "disk": disk,
        "ledger_accounting": acct,
        "all_quotes": quotes,
        "endpoints_called": ENDPOINTS_CALLED,
        "endpoints_not_called": ENDPOINTS_NOT_CALLED,
    }

    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(doc, indent=1, default=str) + "\n")
    MD_PATH.write_text(render_markdown(doc))
    print(f"wrote {JSON_PATH}")
    print(f"wrote {MD_PATH}")
    print(f"ledger lines after: {acct['lines_after']} (added {acct['lines_added']})")
    print(f"all accounting checks pass: {acct['all_checks_pass']}")
    return 0 if acct["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
