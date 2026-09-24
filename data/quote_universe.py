"""Stage E.0: Databento GLBX.MDP3 cost QUOTES for 50 CME products. No download.

    uv run python -m data.quote_universe --probe ES --n 5   # time a few quotes
    uv run python -m data.quote_universe --run              # symbology + sets A, B, C
    uv run python -m data.quote_universe --report           # ledger -> reports/stage_e0_quotes.*

Budget for this stage is $0.00. Only the free ``symbology.resolve`` and
``metadata.get_cost`` / ``metadata.get_billable_size`` endpoints are reached.
Every priced request goes through the quote path of the spend gate
(:meth:`data.spend_gate.SpendGate.quote`), which appends a ledger line with
``usd = 0.0`` under ``STAGE_E0_SESSION_ID``. The gate is built with $0.00
session and per-request caps, so even a stray ``authorize`` would refuse any
billable request; this module never calls ``authorize``, ``commit``,
``settle`` or ``data.adapter.fetch_range``.

Belt and braces: before any vendor call, the client's two billable namespaces
are replaced by a guard whose every attribute access raises, and the gate is
handed a view of the client that has only a (retrying) ``metadata``.

Quote sets, per product (continuous symbol ``ROOT.v.0``):

- A, history: ohlcv-1m monthly chunks from 2019-05-01 (or the first day of the
  first mapped month, if later) to an exclusive 2026-06-21 (00:00 UTC). Holdout
  1 starts 2026-06-21 22:00 UTC, so nothing of it is priced.
- B, spread calibration: mbp-1 and tbbo over five full CME trade dates
  [d-1 17:00 CT, d 16:00 CT).
- C, day-session coverage proxy: ohlcv-1m over the product's declared day
  session on the same five dates.

Symbology results (first mapped date per product) are kept in
reports/stage_e0_symbology.json, because the spend ledger records quotes only.
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
import time
from collections.abc import Callable, Iterable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from datetime import time as clock
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from data.adapter import OHLCV_1M, STYPE_CONTINUOUS
from data.config import (
    DATASET,
    E0_REQUEST_CAP_USD,
    E0_SESSION_CAP_USD,
    LEDGER_PATH,
    REPO_ROOT,
    STAGE_E0_SESSION_ID,
    MissingSecretError,
    require_databento_key,
)
from data.pull_mes import RequestCappedGate, monthly_chunks
from data.spend_gate import (
    ExternalLedgerUnavailableError,
    RequestParams,
    committed_usd,
    read_entries,
)

# ---------------------------------------------------------------- guard ----
# The two billable client namespaces, named only as strings so this file has no
# dotted access to either (tests/test_quote_universe.py checks the AST).
FORBIDDEN_NAMESPACES = ("timeseries", "batch")
FORBIDDEN_MESSAGE = "E.0: timeseries/batch forbidden (quote-only module)"


class ForbiddenNamespace:
    """Stands in for a billable client namespace: every attribute access raises."""

    def __getattr__(self, name: str) -> Any:
        raise RuntimeError(FORBIDDEN_MESSAGE)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise RuntimeError(FORBIDDEN_MESSAGE)


def install_forbidden_guards(client: Any) -> Any:
    """Replace every billable namespace on ``client`` with a raising guard, and verify it."""
    for name in FORBIDDEN_NAMESPACES:
        setattr(client, name, ForbiddenNamespace())
    for name in FORBIDDEN_NAMESPACES:
        if not isinstance(getattr(client, name), ForbiddenNamespace):
            raise RuntimeError(f"guard on {name!r} did not install; refusing to continue")
    return client


# ------------------------------------------------------------ constants ----
CT = ZoneInfo("America/Chicago")
LOCAL_TZ = ZoneInfo("America/Vancouver")  # progress timestamps (operator's local time)

HISTORY_START = date(2019, 5, 1)
HISTORY_END = date(2026, 6, 21)  # exclusive: 2026-06-21T00:00Z
HISTORY_END_UTC = datetime(2026, 6, 21, tzinfo=UTC)
SYMBOLOGY_START = HISTORY_START.isoformat()
SYMBOLOGY_END = HISTORY_END.isoformat()
SAMPLE_DATES = tuple(
    date.fromisoformat(d)
    for d in ("2025-05-14", "2025-08-13", "2025-11-12", "2026-02-11", "2026-04-15")
)
SAMPLE_SCHEMAS = ("mbp-1", "tbbo")
OHLCV_RECORD_BYTES = 56  # asserted against databento_dbn.OHLCVMsg in the tests

MAX_WORKERS = 4
MAX_TRIES = 5
BACKOFF_BASE_S = 1.0

JSON_PATH = REPO_ROOT / "reports" / "stage_e0_quotes.json"
MD_PATH = REPO_ROOT / "reports" / "stage_e0_quotes.md"
SYMBOLOGY_PATH = REPO_ROOT / "reports" / "stage_e0_symbology.json"

RC_REFUSED = 2


@dataclass(frozen=True, slots=True)
class Product:
    root: str
    cluster: str
    group: str
    session_start: clock  # America/Chicago
    session_end: clock

    @property
    def symbol(self) -> str:
        return f"{self.root}.v.0"

    @property
    def window_minutes(self) -> int:
        start = self.session_start.hour * 60 + self.session_start.minute
        return self.session_end.hour * 60 + self.session_end.minute - start

    @property
    def window_ct(self) -> str:
        return f"{self.session_start:%H:%M}-{self.session_end:%H:%M}"


_GROUPS: tuple[tuple[str, str, str, str, tuple[str, ...]], ...] = (
    ("K1", "K1", "08:30", "15:00", ("ES", "NQ", "RTY", "YM", "MNQ", "M2K", "MYM", "NKD")),
    ("K2", "K2", "07:20", "14:00", ("ZT", "ZF", "ZN", "TN", "ZB", "UB")),
    ("K3", "K3", "07:20", "14:00",
     ("6A", "6B", "6C", "6E", "6J", "6S", "6M", "6N", "E7", "M6E", "M6A", "M6B")),
    ("K4", "K4", "08:00", "13:30", ("CL", "QM", "MCL", "NG", "QG", "MNG", "RB", "HO")),
    ("K5", "K5", "07:20", "12:30", ("GC", "MGC", "SI", "SIL", "HG", "MHG", "PL")),
    ("K6", "K6 grains", "08:30", "13:20", ("ZC", "ZW", "ZS", "ZM", "ZL")),
    ("K6", "K6 livestock", "08:30", "13:05", ("HE", "LE")),
    ("K7", "K7", "08:30", "15:00", ("MBT", "MET")),
)

PRODUCTS: tuple[Product, ...] = tuple(
    Product(root, cluster, group, clock.fromisoformat(start), clock.fromisoformat(end))
    for cluster, group, start, end, roots in _GROUPS
    for root in roots
)
PRODUCTS_BY_ROOT: dict[str, Product] = {p.root: p for p in PRODUCTS}
CLUSTERS: tuple[str, ...] = tuple(dict.fromkeys(p.cluster for p in PRODUCTS))
if len(PRODUCTS_BY_ROOT) != 50 or len(PRODUCTS) != 50 or "MES" in PRODUCTS_BY_ROOT:
    raise RuntimeError("E.0 universe must be 50 distinct products, MES excluded")


def ohlcv_record_bytes() -> int:
    """The ohlcv-1m record size from the installed DBN definition (not assumed)."""
    import databento_dbn  # lazy: only the report and the tests need it

    return int(databento_dbn.OHLCVMsg.size_hint)


# ------------------------------------------------------------- windows ----
def iso_z(moment: datetime) -> str:
    """UTC ISO-8601 with a trailing Z, seconds resolution."""
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S") + "Z"


def full_trade_date_window_utc(day: date) -> tuple[str, str]:
    """CME trade date ``day``: [d-1 17:00 CT, d 16:00 CT), DST computed, not assumed."""
    start = datetime.combine(day - timedelta(days=1), clock(17, 0), tzinfo=CT)
    end = datetime.combine(day, clock(16, 0), tzinfo=CT)
    return iso_z(start), iso_z(end)


def day_session_window_utc(product: Product, day: date) -> tuple[str, str]:
    """The product's declared day session on ``day`` (CT), converted to UTC."""
    start = datetime.combine(day, product.session_start, tzinfo=CT)
    end = datetime.combine(day, product.session_end, tzinfo=CT)
    return iso_z(start), iso_z(end)


def parse_utc(stamp: str) -> datetime:
    """A request bound: a date string (00:00 UTC) or an ISO timestamp with Z."""
    if "T" not in stamp:
        return datetime.combine(date.fromisoformat(stamp), clock(0), tzinfo=UTC)
    return datetime.fromisoformat(stamp.replace("Z", "+00:00")).astimezone(UTC)


def history_chunks(first_mapped: date) -> list[tuple[str, str]]:
    """Set A chunks: from the later of 2019-05-01 and the first mapped month, to 2026-06-21."""
    start = max(HISTORY_START, first_mapped.replace(day=1))
    return monthly_chunks(start, HISTORY_END)


# ----------------------------------------------------------------- plan ----
@dataclass(frozen=True, slots=True)
class PlannedQuote:
    set_name: str  # "A", "B" or "C"
    root: str
    params: RequestParams


def _params(product: Product, schema: str, start: str, end: str) -> RequestParams:
    return RequestParams(DATASET, (product.symbol,), schema, STYPE_CONTINUOUS, start, end)


def plan_set_a(product: Product, first_mapped: date) -> list[PlannedQuote]:
    return [PlannedQuote("A", product.root, _params(product, OHLCV_1M, s, e))
            for s, e in history_chunks(first_mapped)]


def plan_set_b(product: Product) -> list[PlannedQuote]:
    out: list[PlannedQuote] = []
    for day in SAMPLE_DATES:
        start, end = full_trade_date_window_utc(day)
        out.extend(PlannedQuote("B", product.root, _params(product, schema, start, end))
                   for schema in SAMPLE_SCHEMAS)
    return out


def plan_set_c(product: Product) -> list[PlannedQuote]:
    return [PlannedQuote("C", product.root, _params(product, OHLCV_1M, *window))
            for window in (day_session_window_utc(product, d) for d in SAMPLE_DATES)]


def plan_quotes(symbology: dict[str, dict[str, Any]],
                products: Iterable[Product] = PRODUCTS) -> list[PlannedQuote]:
    """Sets A, then B, then C, for every product whose continuous symbol resolved."""
    resolved = [(p, date.fromisoformat(symbology[p.root]["first_mapped"])) for p in products
                if symbology.get(p.root, {}).get("status") == "resolved"]
    return ([q for p, first in resolved for q in plan_set_a(p, first)]
            + [q for p, _ in resolved for q in plan_set_b(p)]
            + [q for p, _ in resolved for q in plan_set_c(p)])


def check_windows(planned: Iterable[PlannedQuote]) -> None:
    """Refuse any request that ends after 2026-06-21T00:00Z (holdout 1 is after it)."""
    late = [q for q in planned if parse_utc(q.params.end) > HISTORY_END_UTC]
    if late:
        raise ValueError(f"{len(late)} planned request(s) end after {iso_z(HISTORY_END_UTC)}; "
                         f"first: {late[0].params.as_kwargs()}")


# ----------------------------------------------------------------- gate ----
class LockedQuoteGate(RequestCappedGate):
    """The E.0 gate: every ledger write holds one lock (SpendGate._append is not thread-safe)."""

    def __init__(self, session_id: str, *, request_cap_usd: float, **kwargs: Any) -> None:
        super().__init__(session_id, request_cap_usd=request_cap_usd, **kwargs)
        self.ledger_lock = threading.Lock()

    def _append(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        with self.ledger_lock:
            return super()._append(*args, **kwargs)


def e0_gate(**overrides: Any) -> LockedQuoteGate:
    """STAGE_E0_SESSION_ID with $0.00 session and per-request caps. ``overrides`` are for
    tests (tmp ledgers); the CLI passes none."""
    kwargs = {"session_cap_usd": E0_SESSION_CAP_USD, "request_cap_usd": E0_REQUEST_CAP_USD,
              **overrides}
    return LockedQuoteGate(STAGE_E0_SESSION_ID, **kwargs)


def require_zero_caps(gate: LockedQuoteGate) -> None:
    if gate.session_cap_usd != 0.0 or gate.request_cap_usd != 0.0:
        raise RuntimeError("E.0 is quote-only: the gate's session and request caps must be $0.00")


def preflight(gate: LockedQuoteGate) -> str:
    """Read this repo's ledger and every external ledger; raises if either is unreadable."""
    require_zero_caps(gate)
    read_entries(gate.ledger_path)
    shared = gate.shared_spent_usd()  # raises ExternalLedgerUnavailableError if missing
    return (f"{gate.session_id}: session spent ${gate.session_spent_usd():.4f} (caps "
            f"${gate.session_cap_usd:.2f} session, ${gate.request_cap_usd:.2f} per request) "
            f"· shared ${shared:.4f}")


# ---------------------------------------------------------------- retry ----
def is_retryable(exc: BaseException) -> bool:
    """HTTP 429 or 5xx (databento's BentoHttpError carries ``http_status``)."""
    status = getattr(exc, "http_status", None)
    return isinstance(status, int) and (status == 429 or 500 <= status < 600)


def call_with_retry(fn: Callable[[], Any], *, tries: int = MAX_TRIES,
                    base_delay_s: float = BACKOFF_BASE_S,
                    sleep: Callable[[float], None] = time.sleep) -> Any:
    """Exponential backoff on 429/5xx, at most ``tries`` attempts; anything else re-raises."""
    for attempt in range(1, tries + 1):
        try:
            return fn()
        except Exception as exc:
            if attempt == tries or not is_retryable(exc):
                raise
            sleep(base_delay_s * 2 ** (attempt - 1))
    raise AssertionError("unreachable")


class RetryingMetadata:
    """The two free pricing endpoints, each retried on 429/5xx."""

    def __init__(self, metadata: Any, sleep: Callable[[float], None]) -> None:
        self._metadata = metadata
        self._sleep = sleep

    def get_cost(self, **kwargs: Any) -> float:
        return call_with_retry(lambda: self._metadata.get_cost(**kwargs), sleep=self._sleep)

    def get_billable_size(self, **kwargs: Any) -> int:
        return call_with_retry(lambda: self._metadata.get_billable_size(**kwargs),
                               sleep=self._sleep)


class QuoteOnlyView:
    """What the gate sees: a ``metadata`` attribute and nothing else."""

    def __init__(self, client: Any, sleep: Callable[[float], None] = time.sleep) -> None:
        self.metadata = RetryingMetadata(client.metadata, sleep)


# ----------------------------------------------------------- symbology ----
def first_mapped_date(response: dict[str, Any], symbol: str) -> str | None:
    intervals = (response.get("result") or {}).get(symbol) or []
    starts = [str(e["d0"]) for e in intervals if str(e.get("s", "")).strip()]
    return min(starts) if starts else None


def resolve_product(client: Any, product: Product,
                    sleep: Callable[[float], None] = time.sleep) -> dict[str, Any]:
    """Free symbology lookup. An unresolved symbol is recorded, never fatal."""
    base = {"root": product.root, "symbol": product.symbol, "cluster": product.cluster,
            "window": f"{SYMBOLOGY_START}..{SYMBOLOGY_END}"}
    try:
        response = call_with_retry(lambda: client.symbology.resolve(
            dataset=DATASET, symbols=[product.symbol], stype_in=STYPE_CONTINUOUS,
            stype_out="instrument_id", start_date=SYMBOLOGY_START, end_date=SYMBOLOGY_END,
        ), sleep=sleep)
    except Exception as exc:  # noqa: BLE001 - recorded as unresolved with the error
        return {**base, "status": "unresolved", "error": f"{type(exc).__name__}: {exc}"}
    first = first_mapped_date(response, product.symbol)
    if first is None:
        return {**base, "status": "unresolved",
                "error": f"no mapping returned; not_found={response.get('not_found')}"}
    intervals = (response.get("result") or {}).get(product.symbol) or []
    return {**base, "status": "resolved", "first_mapped": first, "intervals": len(intervals)}


def load_symbology(path: Path) -> dict[str, dict[str, Any]]:
    if not path.is_file():
        return {}
    return {r["root"]: r for r in json.loads(path.read_text())["products"]}


def save_symbology(path: Path, records: dict[str, dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    body = {"session_id": STAGE_E0_SESSION_ID, "updated": iso_z(datetime.now(UTC)),
            "products": [records[k] for k in sorted(records)]}
    tmp.write_text(json.dumps(body, indent=1) + "\n")
    tmp.replace(path)


def resolve_symbology(client: Any, products: Iterable[Product], path: Path, *,
                      log: Callable[[str], None], sleep: Callable[[float], None] = time.sleep,
                      workers: int = MAX_WORKERS) -> dict[str, dict[str, Any]]:
    """Resolve every product not already resolved in ``path``; merge and save."""
    products = list(products)
    existing = load_symbology(path)
    todo = [p for p in products if existing.get(p.root, {}).get("status") != "resolved"]
    log(f"symbology: {len(todo)} to resolve, {len(products) - len(todo)} already resolved")
    with ThreadPoolExecutor(max_workers=max(1, min(workers, MAX_WORKERS))) as pool:
        results = list(pool.map(lambda p: resolve_product(client, p, sleep), todo))
    for r in results:
        detail = r.get("first_mapped") or r.get("error")
        log(f"symbology {r['root']:>4}: {r['status']} {detail}")
    merged = {**existing, **{r["root"]: r for r in results}}
    save_symbology(path, merged)
    return merged


# --------------------------------------------------------------- quotes ----
def request_key(request: dict[str, Any]) -> str:
    return json.dumps(request, sort_keys=True)


def already_quoted(entries: Iterable[dict[str, Any]], session_id: str) -> set[str]:
    """Request keys with a successful quote event under ``session_id``."""
    return {request_key(e["request"]) for e in entries
            if e.get("session_id") == session_id and e.get("event") == "quote"
            and e.get("quoted_usd") is not None and "request" in e}


@dataclass(frozen=True, slots=True)
class QuoteOutcome:
    planned: PlannedQuote
    usd: float | None
    billable_bytes: int | None
    seconds: float


def run_quotes(client: Any, gate: LockedQuoteGate, planned: list[PlannedQuote], *,
               log: Callable[[str], None], workers: int = MAX_WORKERS,
               sleep: Callable[[float], None] = time.sleep) -> list[QuoteOutcome]:
    """Quote every planned request not already quoted in this session (at most 4 threads).
    Only ``gate.quote`` is called; a failed quote stays ledgered as failed."""
    require_zero_caps(gate)
    check_windows(planned)
    done = already_quoted(read_entries(gate.ledger_path), gate.session_id)
    unique = {request_key(q.params.as_kwargs()): q for q in planned}
    todo = [q for k, q in unique.items() if k not in done]
    log(f"{len(todo)} to quote, {len(unique) - len(todo)} already quoted (skipped)")
    view = QuoteOnlyView(client, sleep)
    counter = {"n": 0}
    progress_lock = threading.Lock()

    def one(q: PlannedQuote) -> QuoteOutcome:
        t0 = time.monotonic()
        quote = gate.quote(view, q.params)
        outcome = QuoteOutcome(q, None if quote is None else quote.usd,
                               None if quote is None else quote.billable_bytes,
                               time.monotonic() - t0)
        with progress_lock:
            counter["n"] += 1
            price = ("QUOTE FAILED" if quote is None
                     else f"${quote.usd:.6f} {quote.billable_bytes:,} B")
            log(f"[{counter['n']}/{len(todo)}] {q.set_name} {q.root} {q.params.schema} "
                f"{q.params.start}..{q.params.end}: {price} ({outcome.seconds:.2f}s)")
        return outcome

    with ThreadPoolExecutor(max_workers=max(1, min(workers, MAX_WORKERS))) as pool:
        futures = [pool.submit(one, q) for q in todo]
        try:
            return [f.result() for f in futures]
        except BaseException:
            pool.shutdown(wait=True, cancel_futures=True)
            raise


def probe(client: Any, gate: LockedQuoteGate, root: str, n: int, *,
          symbology_path: Path | None = None, log: Callable[[str], None],
          sleep: Callable[[float], None] = time.sleep) -> list[QuoteOutcome]:
    """Quote the first ``n`` set-A chunks of one product, serially, timing each quote."""
    product = PRODUCTS_BY_ROOT.get(root)
    if product is None:
        raise ValueError(f"{root!r} is not in the E.0 universe")
    symbology = resolve_symbology(client, [product], symbology_path or SYMBOLOGY_PATH, log=log,
                                  sleep=sleep, workers=1)
    record = symbology[root]
    if record["status"] != "resolved":
        log(f"{root}: unresolved, nothing quoted: {record.get('error')}")
        return []
    planned = plan_set_a(product, date.fromisoformat(record["first_mapped"]))[:n]
    outcomes = run_quotes(client, gate, planned, log=log, workers=1, sleep=sleep)
    if outcomes:
        mean = sum(o.seconds for o in outcomes) / len(outcomes)
        log(f"probe {root}: {len(outcomes)} quotes, mean {mean:.2f}s per quote serially "
            f"(the run uses {MAX_WORKERS} threads)")
    return outcomes


def run_all(client: Any, gate: LockedQuoteGate, *, symbology_path: Path | None = None,
            log: Callable[[str], None], sleep: Callable[[float], None] = time.sleep,
            products: Iterable[Product] = PRODUCTS) -> dict[str, int]:
    """Symbology, then sets A, B and C. Returns counts; failures are left in the ledger."""
    products = list(products)
    symbology = resolve_symbology(client, products, symbology_path or SYMBOLOGY_PATH, log=log,
                                  sleep=sleep)
    planned = plan_quotes(symbology, products)
    check_windows(planned)
    counts = {"unresolved": sum(1 for p in products
                                if symbology.get(p.root, {}).get("status") != "resolved")}
    for set_name in ("A", "B", "C"):
        wave = [q for q in planned if q.set_name == set_name]
        log(f"set {set_name}: {len(wave)} planned requests")
        outcomes = run_quotes(client, gate, wave, log=log, sleep=sleep)
        counts[f"set_{set_name}_quoted"] = len(outcomes)
        counts[f"set_{set_name}_failed"] = sum(1 for o in outcomes if o.usd is None)
    log(f"run finished: {counts}; now run --report")
    return counts


# --------------------------------------------------------------- report ----
def session_entries(ledger_path: Path, session_id: str) -> list[tuple[int, dict[str, Any]]]:
    """(1-based ledger line number, entry) for every line of ``session_id``."""
    if not ledger_path.is_file():
        return []
    out: list[tuple[int, dict[str, Any]]] = []
    for n, line in enumerate(ledger_path.read_text().splitlines(), start=1):
        if line.strip():
            entry = json.loads(line)
            if entry.get("session_id") == session_id:
                out.append((n, entry))
    return out


def classify(request: dict[str, Any]) -> tuple[str, str, str | None]:
    """(set, root, sample date) from the request shape."""
    root = request["symbols"][0].removesuffix(".v.0")
    if request["schema"] in SAMPLE_SCHEMAS:
        return "B", root, request["end"][:10]
    if request["schema"] == OHLCV_1M and "T" in request["start"]:
        return "C", root, request["start"][:10]
    if request["schema"] == OHLCV_1M:
        return "A", root, None
    return "other", root, None


def weekdays_between(start: date, end: date) -> int:
    """Monday-Friday dates in [start, end)."""
    return sum(1 for i in range((end - start).days) if (start + timedelta(days=i)).weekday() < 5)


def _blank_product(p: Product, sym: dict[str, Any]) -> dict[str, Any]:
    first = sym.get("first_mapped")
    return {
        "root": p.root, "symbol": p.symbol, "cluster": p.cluster, "group": p.group,
        "session_window_ct": p.window_ct, "window_minutes": p.window_minutes,
        "symbology_status": sym.get("status", "not resolved yet"), "first_mapped": first,
        "symbology_error": sym.get("error"),
        "months_planned": len(history_chunks(date.fromisoformat(first))) if first else None,
        "months_quoted": 0, "ohlcv_1m_usd": 0.0, "ohlcv_1m_bytes": 0, "_a_windows": [],
        "mbp1_usd": 0.0, "mbp1_bytes": 0, "mbp1_dates_quoted": 0,
        "tbbo_usd": 0.0, "tbbo_bytes": 0, "tbbo_dates_quoted": 0,
        "set_c_bytes": {}, "coverage": {},
    }


def _accumulate(row: dict[str, Any], entry: dict[str, Any]) -> None:
    set_name, _, day = classify(entry["request"])
    usd, nbytes = float(entry["quoted_usd"]), int(entry["billable_bytes"])
    if set_name == "A":
        row["months_quoted"] += 1
        row["ohlcv_1m_usd"] += usd
        row["ohlcv_1m_bytes"] += nbytes
        row["_a_windows"].append((entry["request"]["start"], entry["request"]["end"]))
    elif set_name == "B":
        key = "mbp1" if entry["request"]["schema"] == "mbp-1" else "tbbo"
        row[f"{key}_usd"] += usd
        row[f"{key}_bytes"] += nbytes
        row[f"{key}_dates_quoted"] += 1
    elif set_name == "C" and day is not None:
        row["set_c_bytes"][day] = nbytes


def _finish_product(row: dict[str, Any], record_bytes: int) -> dict[str, Any]:
    windows = sorted(row.pop("_a_windows"))
    row["ohlcv_1m_records"] = row["ohlcv_1m_bytes"] / record_bytes
    if windows:
        start, end = date.fromisoformat(windows[0][0]), date.fromisoformat(windows[-1][1])
        weekdays = weekdays_between(start, end)
        row["quoted_range"] = [start.isoformat(), end.isoformat()]
        row["weekdays_in_range"] = weekdays
        row["records_per_weekday"] = row["ohlcv_1m_records"] / weekdays if weekdays else None
    else:
        row.update(quoted_range=None, weekdays_in_range=0, records_per_weekday=None)
    set_c = row.pop("set_c_bytes")
    row["coverage"] = {d: set_c[d] / record_bytes / row["window_minutes"] for d in sorted(set_c)}
    row["coverage_mean"] = (sum(row["coverage"].values()) / len(row["coverage"])
                            if row["coverage"] else None)
    return row


TOTAL_FIELDS = ("ohlcv_1m_usd", "ohlcv_1m_bytes", "mbp1_usd", "mbp1_bytes",
                "tbbo_usd", "tbbo_bytes")


def _totals(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    rows = list(rows)
    out: dict[str, Any] = {f: sum(r[f] for r in rows) for f in TOTAL_FIELDS}
    out["products"] = len(rows)
    out["ohlcv_1m_records"] = sum(r["ohlcv_1m_records"] for r in rows)
    return out


def _ledger_checks(lined: list[tuple[int, dict[str, Any]]], session_id: str) -> dict[str, Any]:
    entries = [e for _, e in lined]
    non_quote = [n for n, e in lined if e.get("event") != "quote" or float(e.get("usd", 0)) != 0.0]
    committed = committed_usd(entries, session_id)
    return {
        "first_line": lined[0][0] if lined else None,
        "last_line": lined[-1][0] if lined else None,
        "session_events": len(entries),
        "non_quote_or_nonzero_lines": non_quote,
        "all_events_are_zero_usd_quotes": not non_quote,
        "session_committed_usd": committed,
        "passed": not non_quote and committed == 0.0,
    }


def build_report(lined: list[tuple[int, dict[str, Any]]], symbology: dict[str, dict[str, Any]],
                 *, session_id: str = STAGE_E0_SESSION_ID, products: Iterable[Product] = PRODUCTS,
                 record_bytes: int = OHLCV_RECORD_BYTES) -> dict[str, Any]:
    """Pure: this session's ledger lines + the symbology file -> the report dict."""
    products = list(products)
    quotes = [e for _, e in lined if e.get("event") == "quote" and "request" in e]
    latest: dict[str, dict[str, Any]] = {}
    for e in quotes:
        if e.get("quoted_usd") is not None:
            latest[request_key(e["request"])] = e
    failed = [e for e in quotes if e.get("quoted_usd") is None]
    outstanding = {request_key(e["request"]): e for e in failed
                   if request_key(e["request"]) not in latest}
    rows = {p.root: _blank_product(p, symbology.get(p.root, {})) for p in products}
    unplanned = 0
    for e in latest.values():
        root = classify(e["request"])[1]
        if root not in rows:
            unplanned += 1
            continue
        _accumulate(rows[root], e)
    finished = [_finish_product(rows[p.root], record_bytes) for p in products]
    planned_keys = {request_key(q.params.as_kwargs()) for q in plan_quotes(symbology, products)}
    missing = sorted(planned_keys - set(latest))
    return {
        "session_id": session_id,
        "record_bytes_ohlcv_1m": record_bytes,
        "windows": {"history": f"{HISTORY_START}..{HISTORY_END} (end exclusive, 00:00 UTC)",
                    "sample_dates": [d.isoformat() for d in SAMPLE_DATES]},
        "counts": {
            "quote_events": len(quotes), "successful_quote_events":
                sum(1 for e in quotes if e.get("quoted_usd") is not None),
            "distinct_requests_quoted": len(latest), "failed_quote_events": len(failed),
            "outstanding_failures": len(outstanding), "planned_requests": len(planned_keys),
            "planned_not_yet_quoted": len(missing), "quoted_outside_universe": unplanned,
            "unresolved_symbols": sum(1 for r in finished if r["symbology_status"] != "resolved"),
        },
        "outstanding_failures": [{"request": e["request"], "note": e.get("note", "")}
                                 for e in outstanding.values()],
        "planned_not_yet_quoted_sample": [json.loads(k) for k in missing[:20]],
        "unresolved": [{"root": r["root"], "status": r["symbology_status"],
                        "error": r["symbology_error"]}
                       for r in finished if r["symbology_status"] != "resolved"],
        "products": finished,
        "clusters": {c: _totals(r for r in finished if r["cluster"] == c) for c in CLUSTERS},
        "universe": _totals(finished),
        "ledger": _ledger_checks(lined, session_id),
    }


def _usd(x: float) -> str:
    return f"${x:,.2f}"


def _gb(x: float) -> str:
    return f"{x / 1e9:,.3f}"


def render_markdown(report: dict[str, Any]) -> str:
    c, led, uni = report["counts"], report["ledger"], report["universe"]
    lines = [
        "# Stage E.0 Databento quotes (GLBX.MDP3, 50 CME products)", "",
        f"Session `{report['session_id']}`. Quotes only: every figure is a price Databento "
        "returned from the free metadata endpoints; nothing was bought.", "",
        f"- History (set A): ohlcv-1m, {report['windows']['history']}.",
        f"- Samples (sets B, C): {', '.join(report['windows']['sample_dates'])}.",
        f"- ohlcv-1m record size {report['record_bytes_ohlcv_1m']} B; records = bytes / size.",
        f"- Quote events {c['quote_events']} ({c['successful_quote_events']} ok, "
        f"{c['failed_quote_events']} failed, {c['outstanding_failures']} still failing); "
        f"distinct requests {c['distinct_requests_quoted']} of {c['planned_requests']} planned "
        f"({c['planned_not_yet_quoted']} not yet quoted); unresolved symbols "
        f"{c['unresolved_symbols']}.",
        f"- Ledger lines {led['first_line']}..{led['last_line']} ({led['session_events']} "
        f"events); all zero-USD quotes: {led['all_events_are_zero_usd_quotes']}; session "
        f"committed ${led['session_committed_usd']:.2f}; check passed: {led['passed']}.", "",
        "## Totals", "",
        "| scope | products | ohlcv-1m USD | ohlcv-1m GB | mbp-1 5d USD | mbp-1 5d GB "
        "| tbbo 5d USD | tbbo 5d GB |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, t in [*report["clusters"].items(), ("universe", uni)]:
        lines.append(f"| {name} | {t['products']} | {_usd(t['ohlcv_1m_usd'])} | "
                     f"{_gb(t['ohlcv_1m_bytes'])} | {_usd(t['mbp1_usd'])} | {_gb(t['mbp1_bytes'])}"
                     f" | {_usd(t['tbbo_usd'])} | {_gb(t['tbbo_bytes'])} |")
    lines += ["", "## Per product", "",
              "| root | group | first mapped | months | ohlcv-1m USD | records | rec/weekday "
              "| mbp-1 USD | tbbo USD | window CT | coverage mean |",
              "|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|"]
    for r in report["products"]:
        rpw = "" if r["records_per_weekday"] is None else f"{r['records_per_weekday']:,.0f}"
        cov = "" if r["coverage_mean"] is None else f"{r['coverage_mean']:.3f}"
        months = f"{r['months_quoted']}/{r['months_planned'] or '-'}"
        lines.append(f"| {r['root']} | {r['group']} | {r['first_mapped'] or r['symbology_status']}"
                     f" | {months} | {_usd(r['ohlcv_1m_usd'])} | {r['ohlcv_1m_records']:,.0f} | "
                     f"{rpw} | {_usd(r['mbp1_usd'])} | {_usd(r['tbbo_usd'])} | "
                     f"{r['session_window_ct']} | {cov} |")
    lines += ["", "## Set C coverage per date (records / window minutes)", "",
              "| root | " + " | ".join(report["windows"]["sample_dates"]) + " |",
              "|---|" + "---:|" * len(report["windows"]["sample_dates"])]
    for r in report["products"]:
        cells = [f"{r['coverage'][d]:.3f}" if d in r["coverage"] else ""
                 for d in report["windows"]["sample_dates"]]
        lines.append(f"| {r['root']} | " + " | ".join(cells) + " |")
    lines += ["", "## Failures and unresolved symbols", ""]
    lines += [f"- quote failed: `{json.dumps(f['request'])}`: {f['note']}"
              for f in report["outstanding_failures"]] or ["- no outstanding quote failures"]
    lines += [f"- unresolved {u['root']} ({u['status']}): {u['error']}"
              for u in report["unresolved"]] or ["- no unresolved symbols"]
    return "\n".join(lines) + "\n"


def write_report(*, ledger_path: Path = LEDGER_PATH, symbology_path: Path = SYMBOLOGY_PATH,
                 json_path: Path = JSON_PATH, md_path: Path = MD_PATH,
                 session_id: str = STAGE_E0_SESSION_ID) -> dict[str, Any]:
    """No vendor call: this session's ledger lines + the symbology file -> JSON and Markdown."""
    record_bytes = ohlcv_record_bytes()
    if record_bytes != OHLCV_RECORD_BYTES:
        raise RuntimeError(f"installed OHLCVMsg is {record_bytes} B, expected 56")
    report = build_report(session_entries(ledger_path, session_id), load_symbology(symbology_path),
                          session_id=session_id, record_bytes=record_bytes)
    report["generated"] = datetime.now(LOCAL_TZ).isoformat(timespec="seconds")
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=1) + "\n")
    md_path.write_text(render_markdown(report))
    return report


# ------------------------------------------------------------------ CLI ----
def log_line(message: str) -> None:
    print(f"[{datetime.now(LOCAL_TZ):%Y-%m-%d %H:%M:%S %Z}] {message}", flush=True)


def build_client(key: str) -> Any:
    """databento.Historical with both billable namespaces guarded before it is returned."""
    import databento  # lazy: the tests never build a real client

    return install_forbidden_guards(databento.Historical(key))


def main(argv: list[str] | None = None, *,
         key_loader: Callable[[], str] = require_databento_key,
         gate_factory: Callable[[], LockedQuoteGate] = e0_gate,
         client_factory: Callable[[str], Any] = build_client) -> int:
    parser = argparse.ArgumentParser(prog="python -m data.quote_universe")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--probe", metavar="ROOT", help="quote the first N set-A chunks of ROOT")
    mode.add_argument("--run", action="store_true", help="symbology and sets A, B, C")
    mode.add_argument("--report", action="store_true", help="build the report (no vendor call)")
    parser.add_argument("--n", type=int, default=5, help="chunks for --probe (default 5)")
    args = parser.parse_args(argv)

    if args.report:
        report = write_report()
        print(f"wrote {JSON_PATH} and {MD_PATH}; ledger check passed: "
              f"{report['ledger']['passed']}; counts {report['counts']}")
        return 0 if report["ledger"]["passed"] else 1
    if args.probe and args.probe not in PRODUCTS_BY_ROOT:
        print(f"REFUSED: {args.probe!r} is not in the E.0 universe", file=sys.stderr)
        return RC_REFUSED
    try:
        key = key_loader()
        gate = gate_factory()
        log_line(preflight(gate))
    except (MissingSecretError, ExternalLedgerUnavailableError, OSError, ValueError,
            RuntimeError) as exc:
        print(f"REFUSED before any vendor call ({type(exc).__name__}): {exc}. "
              "Nothing was requested or ledgered.", file=sys.stderr)
        return RC_REFUSED
    client = client_factory(key)
    if args.probe:
        probe(client, gate, args.probe, args.n, log=log_line)
    else:
        run_all(client, gate, log=log_line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
