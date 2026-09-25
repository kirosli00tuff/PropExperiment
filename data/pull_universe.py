"""Stage E.1: the Stage E step 1 purchase path (45 CME contracts, GLBX.MDP3, continuous).

    uv run python -m data.pull_universe --quote-only   # prices everything (free), ledgered
    uv run python -m data.pull_universe --buy          # quote, gate, buy; needs the lead's cap

The step 1 set is STEP1_ROOTS: 45 admissible contracts of the 31 traded exposures (user
decision U2 removed platinum PL). Per root, symbol ``<ROOT>.v.0``, stype_in continuous:

1. ohlcv-1m, monthly chunks 2025-04-01 .. 2026-06-21 (end exclusive, 00:00 UTC): 15 chunks;
2. mbp-1 on the five fixed trade dates, each over E.0's full-trade-date UTC window
   [d-1 17:00 CT, d 16:00 CT) (``quote_universe.full_trade_date_window_utc``).

The plan runs the ohlcv-1m phase for every root first (roots in STEP1_ROOTS order, chunks
oldest first), then the mbp-1 phase (same root order, dates oldest first).

Every request, split pieces included, passes ``check_request`` BEFORE any vendor call: a root
outside the set (PL, MET, NKD, 6M, ES, MES and anything else) raises RefusedRootError; a
window that overlaps the embargo and holdout 2 [2024-03-01T00:00Z, 2025-04-01T00:00Z), or
leaves [2025-04-01T00:00Z, 2026-06-21T00:00Z], raises DateGuardError. The whole plan is
checked before the first call, so a bad request anywhere stops the run with nothing sent.

Request-cap splitting (lead decision): the request cap E1_REQUEST_CAP_USD is never raised. A
request quoted above it is split into two contiguous halves (midpoint rounded down to the
whole minute), each is quoted, and so on, at most MAX_SPLIT_DEPTH halvings deep; a piece
still over the cap there raises SplitRefusedError. Each piece is its own quoted, gated,
committed, downloaded, checked and settled request, and its own file.

Buy flow per request, as data.pull_mes / data.adapter.fetch_range: quote -> authorize (session
cap E1_SESSION_CAP_USD, request cap, the active account's cap) -> commit -> download to a
.partial file -> os.link (never replaces) -> read-only -> record-byte check against the quoted
billable bytes (``adapter.delivered_record_bytes``, the only decode; it returns a byte count)
-> settle. Any failure stops the run at that request with a named error. Files go to
data/vendor/databento/GLBX.MDP3/<schema>/<ROOT>_v_0/range=<start>_<end>.dbn.zst, the MES
layout; a timestamp bound is written without colons (2025-05-13T220000Z).

Resume: a request whose file exists AND has a settled line (this session, same request key) is
skipped before it is quoted. A file with no settled line, or a settled line with no file, is a
ResumeStateError for the lead; no file is ever deleted. A window whose pieces are already on
disk goes straight to those pieces, so an overlapping range is never bought twice.

--quote-only installs quote_universe's forbidden guards on the client's timeseries and batch
namespaces, calls only ``gate.quote``, and writes reports/stage_e1_quote_summary.json (costs,
bytes and counts only). ``inventory`` reports a downloaded file's record count, first and last
ts_event, symbols, instrument ids, schema and sha256, and nothing else.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import time
from collections.abc import Callable, Iterable, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

from data import adapter
from data import holdout as ho
from data.adapter import OHLCV_1M, STYPE_CONTINUOUS
from data.config import (
    ACTIVE_ACCOUNT,
    DATASET,
    E1_REQUEST_CAP_USD,
    E1_SESSION_CAP_MAX_USD,
    E1_SESSION_CAP_USD,
    REPO_ROOT,
    STAGE_E1_SESSION_ID,
    VENDOR_ROOT,
    MissingSecretError,
    require_databento_key,
)
from data.pull_mes import monthly_chunks
from data.quote_universe import (
    LOCAL_TZ,
    MAX_WORKERS,
    PRODUCTS_BY_ROOT,
    SAMPLE_DATES,
    ForbiddenNamespace,
    LockedQuoteGate,
    QuoteOnlyView,
    full_trade_date_window_utc,
    install_forbidden_guards,
    iso_z,
    parse_utc,
    request_key,
)
from data.spend_gate import (
    USD_COMPARE_DECIMALS,
    BudgetRefusedError,
    ExternalLedgerUnavailableError,
    Quote,
    RequestParams,
    UnknownAccountError,
    read_entries,
)

# ------------------------------------------------------------- the set ----
STEP1_ROOTS: tuple[str, ...] = (
    "MNQ", "NQ", "RTY", "M2K", "MYM", "YM",
    "ZT", "ZF", "ZN", "TN", "ZB", "UB",
    "6E", "M6E", "E7", "6A", "M6A", "6B", "M6B", "6C", "6J", "6S", "6N",
    "CL", "MCL", "QM", "NG", "MNG", "QG", "RB", "HO",
    "MGC", "GC", "SIL", "SI", "HG", "MHG",
    "ZC", "ZW", "ZS", "ZM", "ZL", "HE", "LE",
    "MBT",
)
# Named refusals (U2 removed PL; MET, NKD, 6M and ES are not admissible; MES is the old lane).
REFUSED_ROOTS: tuple[str, ...] = ("PL", "MET", "NKD", "6M", "ES", "MES")
STEP1_ROOT_COUNT = 45
if (len(STEP1_ROOTS) != STEP1_ROOT_COUNT or len(set(STEP1_ROOTS)) != STEP1_ROOT_COUNT
        or not set(STEP1_ROOTS) <= set(PRODUCTS_BY_ROOT) or set(STEP1_ROOTS) & set(REFUSED_ROOTS)):
    raise RuntimeError("the step 1 set must be 45 distinct E.0 products, none of them refused")

MBP_1 = "mbp-1"
SCHEMAS: tuple[str, ...] = (OHLCV_1M, MBP_1)

WINDOW_START = date(2025, 4, 1)
WINDOW_END = date(2026, 6, 21)  # exclusive, 00:00 UTC: holdout 1's first session is after it
WINDOW_START_UTC = datetime(2025, 4, 1, tzinfo=UTC)
WINDOW_END_UTC = datetime(2026, 6, 21, tzinfo=UTC)
# Embargo and holdout 2: trade dates 2024-03-01 .. 2025-03-31 inclusive.
EMBARGO_START_UTC = datetime(2024, 3, 1, tzinfo=UTC)
EMBARGO_END_UTC = datetime(2025, 4, 1, tzinfo=UTC)
MBP1_TRADE_DATES: tuple[date, ...] = (
    date(2025, 5, 14), date(2025, 8, 13), date(2025, 11, 12), date(2026, 2, 11),
    date(2026, 4, 15),
)
if MBP1_TRADE_DATES != SAMPLE_DATES:
    raise RuntimeError("the mbp-1 trade dates must be E.0's five sample dates")
OHLCV_CHUNK_COUNT = 15
MBP1_DAY_COUNT = 5

MAX_SPLIT_DEPTH = 4
SPLIT_UNIT = timedelta(minutes=1)
SUMMARY_PATH = REPO_ROOT / "reports" / "stage_e1_quote_summary.json"
E1_NOTE = "Stage E.1 step 1 purchase"
DBN_SUFFIX = ".dbn.zst"
RC_REFUSED = 2
RC_STOPPED = 1

_DAY = r"\d{4}-\d{2}-\d{2}"
_BOUND_TOKEN = rf"{_DAY}(?:T\d{{6}}Z)?"
_TARGET_NAME = re.compile(rf"range=({_BOUND_TOKEN})_({_BOUND_TOKEN})\.dbn\.zst")


# --------------------------------------------------------------- errors ----
class PullUniverseError(RuntimeError):
    """Base: the step 1 run stopped at a named problem. Nothing after it was requested."""


class RefusedRootError(PullUniverseError):
    """A root outside the 45-contract step 1 set. Raised before any vendor call."""


class DateGuardError(PullUniverseError):
    """A window outside [2025-04-01T00:00Z, 2026-06-21T00:00Z] or touching the embargo."""


class HoldoutGuardError(PullUniverseError):
    """data.holdout says the range or its target file is sealed. Never bought."""


class SplitRefusedError(PullUniverseError):
    """A piece still above the request cap at the depth limit, or too short to halve."""


class ResumeStateError(PullUniverseError):
    """Disk and ledger disagree (file without a settle, settle without a file, overlap)."""


class DownloadError(PullUniverseError):
    """The download failed after the commit. The commit stays (pessimistic ledger)."""


class DeliveryCheckError(PullUniverseError):
    """The record-byte check failed, or more bytes arrived than were quoted."""


# ----------------------------------------------------------------- plan ----
@dataclass(frozen=True, slots=True)
class PlannedRequest:
    root: str
    params: RequestParams
    depth: int = 0  # 0: the planned request; n: a piece after n halvings

    @property
    def cluster(self) -> str:
        return PRODUCTS_BY_ROOT[self.root].cluster

    @property
    def key(self) -> str:
        return request_key(self.params.as_kwargs())


def symbol_for(root: str) -> str:
    """``<ROOT>.v.0`` for a step 1 root; any other root raises RefusedRootError."""
    if root in REFUSED_ROOTS:
        raise RefusedRootError(f"{root!r} is refused for step 1 (named refusals: "
                               f"{', '.join(REFUSED_ROOTS)})")
    if root not in STEP1_ROOTS:
        raise RefusedRootError(f"{root!r} is not in the 45-contract step 1 set")
    return f"{root}.v.0"


def params_for(root: str, schema: str, start: str, end: str) -> RequestParams:
    return RequestParams(DATASET, (symbol_for(root),), schema, STYPE_CONTINUOUS, start, end)


def ohlcv_chunks() -> list[tuple[str, str]]:
    """The 15 monthly chunks 2025-04 .. 2026-06, the last ending 2026-06-21, oldest first."""
    return monthly_chunks(WINDOW_START, WINDOW_END)


def mbp1_windows() -> list[tuple[str, str]]:
    return [full_trade_date_window_utc(day) for day in MBP1_TRADE_DATES]


def plan_requests(roots: Sequence[str] = STEP1_ROOTS) -> list[PlannedRequest]:
    """The step 1 plan before splitting: all ohlcv-1m, then all mbp-1, roots in order."""
    for root in roots:
        symbol_for(root)
    plan = [PlannedRequest(r, params_for(r, OHLCV_1M, s, e)) for r in roots
            for s, e in ohlcv_chunks()]
    plan += [PlannedRequest(r, params_for(r, MBP_1, s, e)) for r in roots
             for s, e in mbp1_windows()]
    validate_plan(plan)
    return plan


# ---------------------------------------------------------------- guards ----
def _canonical_bound(stamp: str) -> datetime:
    """A request bound: ``YYYY-MM-DD`` (00:00 UTC) or ``YYYY-MM-DDTHH:MM:SSZ``, exactly."""
    try:
        moment = parse_utc(stamp)
    except ValueError as exc:
        raise DateGuardError(f"unparseable request bound {stamp!r}") from exc
    canonical = moment.date().isoformat() if "T" not in stamp else iso_z(moment)
    if canonical != stamp:
        raise DateGuardError(f"request bound {stamp!r} is not canonical ({canonical!r})")
    return moment


def check_window(start: str, end: str) -> None:
    """Refuse [start, end) unless it lies in [2025-04-01T00:00Z, 2026-06-21T00:00Z] and misses
    the embargo and holdout 2 [2024-03-01T00:00Z, 2025-04-01T00:00Z) entirely."""
    s, e = _canonical_bound(start), _canonical_bound(end)
    if not s < e:
        raise DateGuardError(f"empty or inverted window {start}..{end}")
    if s < EMBARGO_END_UTC and e > EMBARGO_START_UTC:
        raise DateGuardError(f"{start}..{end} overlaps the embargo and holdout 2 "
                             f"{iso_z(EMBARGO_START_UTC)}..{iso_z(EMBARGO_END_UTC)}")
    if s >= WINDOW_END_UTC or e > WINDOW_END_UTC:
        raise DateGuardError(f"{start}..{end} reaches at or after {iso_z(WINDOW_END_UTC)} "
                             "(holdout 1 side): nothing from there on is bought")
    if s < WINDOW_START_UTC:
        raise DateGuardError(f"{start}..{end} starts before {iso_z(WINDOW_START_UTC)}")


def check_request(request: PlannedRequest) -> None:
    """Everything a request must satisfy before any vendor call. Raises, never warns."""
    p = request.params
    if len(p.symbols) != 1 or p.symbols[0] != symbol_for(request.root):
        raise RefusedRootError(f"request symbols {p.symbols} do not match {request.root}.v.0")
    if (p.dataset, p.stype_in) != (DATASET, STYPE_CONTINUOUS) or p.schema not in SCHEMAS:
        raise PullUniverseError(f"request outside step 1: {p.as_kwargs()}")
    if not 0 <= request.depth <= MAX_SPLIT_DEPTH:
        raise SplitRefusedError(f"depth {request.depth} is outside 0..{MAX_SPLIT_DEPTH}")
    check_window(p.start, p.end)


def validate_plan(requests: Iterable[PlannedRequest]) -> None:
    for request in requests:
        check_request(request)


def check_holdout(request: PlannedRequest, target: Path) -> None:
    """data.holdout's own refusals (read-only): a sealed range or a sealed target file."""
    p = request.params
    if ho.request_touches_sealed_window(p.start, p.end):
        raise HoldoutGuardError(f"{p.start}..{p.end} touches a sealed holdout window")
    if ho.is_sealed_raw(target):
        raise HoldoutGuardError(f"{target} is held in a sealed holdout store")


# ---------------------------------------------------------------- split ----
def split_window(start: str, end: str) -> tuple[tuple[str, str], tuple[str, str]]:
    """Two contiguous halves; the midpoint is rounded down to the whole minute."""
    s, e = _canonical_bound(start), _canonical_bound(end)
    mid = s + (e - s) / 2
    mid = mid.replace(second=0, microsecond=0)
    if not s < mid < e:
        raise SplitRefusedError(f"{start}..{end} is too short to halve on whole minutes")
    cut = iso_z(mid)
    return (start, cut), (cut, end)


def split_request(request: PlannedRequest) -> tuple[PlannedRequest, PlannedRequest]:
    if request.depth >= MAX_SPLIT_DEPTH:
        p = request.params
        raise SplitRefusedError(f"{request.root} {p.schema} {p.start}..{p.end} is still over the "
                                f"request cap after {MAX_SPLIT_DEPTH} halvings: refused")
    halves = split_window(request.params.start, request.params.end)
    return tuple(  # type: ignore[return-value]
        PlannedRequest(request.root, params_for(request.root, request.params.schema, s, e),
                       request.depth + 1)
        for s, e in halves)


def over_request_cap(quote: Quote | None, cap_usd: float) -> bool:
    return quote is not None and round(quote.usd, USD_COMPARE_DECIMALS) > cap_usd


# ---------------------------------------------------------------- files ----
def bound_token(stamp: str) -> str:
    """Filename-safe spelling of a canonical bound: a date as is, a timestamp without colons."""
    moment = _canonical_bound(stamp)
    return stamp if "T" not in stamp else moment.strftime("%Y-%m-%dT%H%M%SZ")


def token_bound(token: str) -> str:
    """The inverse of ``bound_token``."""
    if "T" not in token:
        return date.fromisoformat(token).isoformat()
    return iso_z(datetime.strptime(token, "%Y-%m-%dT%H%M%SZ").replace(tzinfo=UTC))


def target_path(params: RequestParams, root: Path = VENDOR_ROOT) -> Path:
    """MES's layout (``adapter.raw_path`` for date bounds), colon-free for timestamp bounds."""
    safe = params.symbols[0].replace(".", "_")
    name = f"range={bound_token(params.start)}_{bound_token(params.end)}{DBN_SUFFIX}"
    return root / params.dataset / params.schema / safe / name


def parse_target_name(name: str) -> tuple[str, str] | None:
    match = _TARGET_NAME.fullmatch(name)
    return None if match is None else (token_bound(match[1]), token_bound(match[2]))


def files_overlapping(directory: Path, start: str, end: str) -> list[tuple[Path, str, str]]:
    """Raw files in ``directory`` whose [start, end) overlaps the given window."""
    if not directory.is_dir():
        return []
    s, e = parse_utc(start), parse_utc(end)
    out = []
    for path in sorted(directory.iterdir()):
        bounds = parse_target_name(path.name)
        if bounds and parse_utc(bounds[0]) < e and parse_utc(bounds[1]) > s:
            out.append((path, *bounds))
    return out


def params_from_request(request: dict[str, Any]) -> RequestParams:
    return RequestParams(request["dataset"], tuple(request["symbols"]), request["schema"],
                         request["stype_in"], request["start"], request["end"])


def settled_keys(entries: Iterable[dict[str, Any]], session_id: str) -> set[str]:
    return {request_key(e["request"]) for e in entries
            if e.get("session_id") == session_id and e.get("event") == "settle"
            and "request" in e}


def is_done(request: PlannedRequest, target: Path, settled: set[str]) -> bool:
    """True when file and settled line both exist; either one alone is a ResumeStateError."""
    has_file, has_settle = target.exists(), request.key in settled
    if has_file and has_settle:
        return True
    if has_file:
        raise ResumeStateError(f"{target} exists but has no settled ledger line for this "
                               "request in this session. Not deleted: the lead decides.")
    if has_settle:
        raise ResumeStateError(f"a settled ledger line exists for {request.params.as_kwargs()} "
                               f"but {target} is missing. The lead decides.")
    return False


def resume_scan(entries: list[dict[str, Any]], session_id: str, root: Path = VENDOR_ROOT,
                roots: Sequence[str] = STEP1_ROOTS) -> dict[str, int]:
    """Before any vendor call: every step 1 file on disk has a settled line and every settled
    line of the session has its file. A mismatch raises ResumeStateError."""
    settled_paths = {target_path(params_from_request(e["request"]), root)
                     for e in entries if e.get("session_id") == session_id
                     and e.get("event") == "settle" and "request" in e}
    on_disk: set[Path] = set()
    partials: list[Path] = []
    for schema in SCHEMAS:
        for r in roots:
            directory = root / DATASET / schema / f"{r}_v_0"
            if directory.is_dir():
                on_disk |= {p for p in directory.iterdir() if parse_target_name(p.name)}
                partials += [p for p in directory.iterdir() if p.name.endswith(".partial")]
    unsettled, missing = sorted(on_disk - settled_paths), sorted(settled_paths - on_disk)
    if unsettled or missing:
        raise ResumeStateError(
            f"disk and ledger disagree: {len(unsettled)} file(s) without a settled line "
            f"{[str(p) for p in unsettled[:5]]}; {len(missing)} settled line(s) without a file "
            f"{[str(p) for p in missing[:5]]}. Nothing was requested or deleted.")
    return {"settled_files_on_disk": len(on_disk), "leftover_partials": len(partials)}


# ------------------------------------------------------------------ gate ----
def e1_gate(**overrides: Any) -> LockedQuoteGate:
    """STAGE_E1_SESSION_ID on ACTIVE_ACCOUNT with the E.1 session and request caps. The lock
    serialises ledger writes for the threaded quote-only run. ``overrides`` are for tests."""
    kwargs = {"session_cap_usd": E1_SESSION_CAP_USD, "request_cap_usd": E1_REQUEST_CAP_USD,
              "account": ACTIVE_ACCOUNT, **overrides}
    return LockedQuoteGate(STAGE_E1_SESSION_ID, **kwargs)


def banner(gate: LockedQuoteGate) -> str:
    """Session, account and caps. Never the key."""
    return (f"{gate.session_id}: account {gate.account_id} (cap ${gate.account_cap_usd:.2f}, "
            f"spent ${gate.account_spent_usd():.4f}) · session cap ${gate.session_cap_usd:.2f} "
            f"(spent ${gate.session_spent_usd():.4f}) · request cap ${gate.request_cap_usd:.2f}")


# ------------------------------------------------------------ quote-only ----
@dataclass(frozen=True, slots=True)
class PieceQuote:
    request: PlannedRequest
    usd: float | None
    billable_bytes: int | None
    status: str  # "ok", "quote_failed" or "split_refused"
    parent_key: str  # the planned (depth 0) request this piece belongs to


def quote_tree(request: PlannedRequest, view: Any, gate: LockedQuoteGate,
               parent_key: str | None = None) -> list[PieceQuote]:
    """Quote a request; above the request cap, quote its halves instead, recursively."""
    check_request(request)
    parent_key = request.key if parent_key is None else parent_key
    quote = gate.quote(view, request.params)
    if quote is None:
        return [PieceQuote(request, None, None, "quote_failed", parent_key)]
    if not over_request_cap(quote, gate.request_cap_usd):
        return [PieceQuote(request, quote.usd, quote.billable_bytes, "ok", parent_key)]
    try:
        halves = split_request(request)
    except SplitRefusedError:
        return [PieceQuote(request, quote.usd, quote.billable_bytes, "split_refused", parent_key)]
    return [piece for half in halves for piece in quote_tree(half, view, gate, parent_key)]


def run_quote_only(client: Any, gate: LockedQuoteGate, requests: list[PlannedRequest], *,
                   log: Callable[[str], None], workers: int = MAX_WORKERS,
                   sleep: Callable[[float], None] = time.sleep) -> list[PieceQuote]:
    """Quote every request (free). The billable namespaces are guarded first; the gate sees a
    metadata-only view; only ``gate.quote`` is ever called."""
    validate_plan(requests)
    install_forbidden_guards(client)
    view = QuoteOnlyView(client, sleep)
    with ThreadPoolExecutor(max_workers=max(1, min(workers, MAX_WORKERS))) as pool:
        futures = [pool.submit(quote_tree, r, view, gate) for r in requests]
        try:
            trees = [f.result() for f in futures]
        except BaseException:
            pool.shutdown(wait=True, cancel_futures=True)
            raise
    pieces = [p for tree in trees for p in tree]
    log(f"quoted {len(requests)} requests -> {len(pieces)} pieces")
    return pieces


def _bucket() -> dict[str, Any]:
    return {"usd": 0.0, "billable_bytes": 0, "requests": 0, "pieces": 0}


def _piece_row(piece: PieceQuote) -> dict[str, Any]:
    p = piece.request.params
    return {"root": piece.request.root, "schema": p.schema, "start": p.start, "end": p.end,
            "depth": piece.request.depth, "usd": piece.usd, "billable_bytes": piece.billable_bytes,
            "status": piece.status}


def _buckets_of(piece: PieceQuote, per_root: dict[str, Any], per_schema: dict[str, Any],
                per_cluster: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    return (per_root[piece.request.root], per_schema[piece.request.params.schema],
            per_cluster[piece.request.cluster])


def build_summary(pieces: list[PieceQuote], gate: LockedQuoteGate) -> dict[str, Any]:
    """Costs, bytes and counts only (a quote carries no price data). Totals and buckets sum
    the buyable ("ok") pieces; a failed quote or a refused split is listed under failures."""
    per_root = {r: {"cluster": PRODUCTS_BY_ROOT[r].cluster, **_bucket()} for r in STEP1_ROOTS}
    per_schema = {s: _bucket() for s in SCHEMAS}
    per_cluster = {PRODUCTS_BY_ROOT[r].cluster: _bucket() for r in STEP1_ROOTS}
    first_piece: dict[str, PieceQuote] = {}
    for piece in pieces:
        first_piece.setdefault(piece.parent_key, piece)
    for piece in first_piece.values():  # one count per planned request
        for bucket in _buckets_of(piece, per_root, per_schema, per_cluster):
            bucket["requests"] += 1
    ok = [p for p in pieces if p.status == "ok"]
    for piece in ok:
        for bucket in _buckets_of(piece, per_root, per_schema, per_cluster):
            bucket["usd"] += piece.usd or 0.0
            bucket["billable_bytes"] += piece.billable_bytes or 0
            bucket["pieces"] += 1
    failed = [p for p in pieces if p.status != "ok"]
    split = [p for p in pieces if p.request.depth > 0]
    largest = max(ok, key=lambda p: p.usd or 0.0, default=None)
    return {
        "session_id": gate.session_id, "account": gate.account_id,
        "account_cap_usd": gate.account_cap_usd, "request_cap_usd": gate.request_cap_usd,
        "session_cap_usd": gate.session_cap_usd, "dataset": DATASET,
        "generated": datetime.now(LOCAL_TZ).isoformat(timespec="seconds"),
        "window": f"{WINDOW_START}..{WINDOW_END} (end exclusive, 00:00 UTC)",
        "mbp1_trade_dates": [d.isoformat() for d in MBP1_TRADE_DATES],
        "total_usd": sum(p.usd or 0.0 for p in ok),
        "total_billable_bytes": sum(p.billable_bytes or 0 for p in ok),
        "counts": {
            "roots": len({p.request.root for p in pieces}),
            "planned_requests": len(first_piece), "pieces": len(pieces),
            "buyable_pieces": len(ok), "requests_split": len({p.parent_key for p in split}),
            "split_pieces": len(split),
            "max_depth": max((p.request.depth for p in pieces), default=0),
            "quote_failed": sum(1 for p in failed if p.status == "quote_failed"),
            "split_refused": sum(1 for p in failed if p.status == "split_refused"),
        },
        "complete": not failed,
        "largest_piece": None if largest is None else _piece_row(largest),
        "split_pieces": [_piece_row(p) for p in split],
        "failures": [_piece_row(p) for p in failed],
        "per_root": per_root, "per_schema": per_schema, "per_cluster": per_cluster,
    }


def write_summary(summary: dict[str, Any], path: Path = SUMMARY_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(summary, indent=1) + "\n")
    tmp.replace(path)
    return path


# ------------------------------------------------------------------- buy ----
def download(client: Any, params: RequestParams, target: Path) -> None:
    """timeseries.get_range to ``<target>.partial``, then os.link (never replaces), read-only."""
    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.parent / (target.name + ".partial")
    partial.unlink(missing_ok=True)
    try:
        client.timeseries.get_range(**params.as_kwargs(), path=partial)
    except Exception as exc:
        partial.unlink(missing_ok=True)
        raise DownloadError(f"download of {params.as_kwargs()} failed ({type(exc).__name__}: "
                            f"{exc}); its commit stays in the ledger (pessimistic)") from exc
    except BaseException:
        partial.unlink(missing_ok=True)
        raise
    try:
        os.link(partial, target)
    except FileExistsError as exc:
        partial.unlink(missing_ok=True)
        raise ResumeStateError(f"{target} appeared during the download; not replaced") from exc
    partial.unlink()
    target.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)


def buy_one(request: PlannedRequest, quote: Quote | None, client: Any, gate: LockedQuoteGate,
            target: Path, settled: set[str]) -> str:
    """authorize -> commit -> download -> record-byte check -> settle, for one request."""
    gate.authorize(request.params, quote)  # raises BudgetRefusedError on any cap
    if quote is None:
        raise BudgetRefusedError("unpriceable request passed authorize")  # unreachable
    gate.commit(quote, note=f"{E1_NOTE} (piece depth {request.depth})")
    download(client, request.params, target)
    try:
        delivered = adapter.delivered_record_bytes(target)  # the only decode: a byte count
    except Exception as exc:
        raise DeliveryCheckError(f"record-byte check of {target} failed ({type(exc).__name__}: "
                                 f"{exc}); file kept, not settled. The lead decides.") from exc
    exceeded = quote.billable_bytes > 0 and delivered > quote.billable_bytes
    actual = quote.usd * delivered / quote.billable_bytes if exceeded else quote.usd
    gate.settle(quote, actual_usd=actual, note=(
        "actual_usd = quote unless delivery exceeded it (then pro rata). Delivered "
        f"uncompressed record bytes {delivered:,} vs quoted billable {quote.billable_bytes:,}"
        + (" — DELIVERED EXCEEDS QUOTE" if exceeded else "")))
    settled.add(request.key)
    if exceeded:
        raise DeliveryCheckError(f"{target.name}: {delivered:,} record bytes delivered > "
                                 f"{quote.billable_bytes:,} quoted; settled pro rata at "
                                 f"${actual:.6f}. Run stopped for the lead.")
    return f"bought {delivered:,} record bytes for ${quote.usd:.6f}"


def acquire(request: PlannedRequest, view: Any, client: Any, gate: LockedQuoteGate, *,
            root: Path, settled: set[str], log: Callable[[str], None]) -> list[dict[str, Any]]:
    """Skip, split or buy one request (recursively for its pieces). Raises on any problem."""
    check_request(request)
    p = request.params
    target = target_path(p, root)
    check_holdout(request, target)
    label = f"{request.root} {p.schema} {p.start}..{p.end} (depth {request.depth})"
    if is_done(request, target, settled):
        log(f"{label}: skipped, already bought and settled")
        return [{"request": p.as_kwargs(), "action": "skipped"}]
    overlapping = files_overlapping(target.parent, p.start, p.end)
    outside = [str(f) for f, s, e in overlapping
               if parse_utc(s) < parse_utc(p.start) or parse_utc(e) > parse_utc(p.end)]
    if outside:
        raise ResumeStateError(f"{label}: on-disk file(s) straddle this window: {outside}")
    if overlapping:
        if request.depth >= MAX_SPLIT_DEPTH:
            raise ResumeStateError(f"{label}: on-disk file(s) {[str(f) for f, _, _ in overlapping]}"
                                   " overlap it but are not its halves")
        log(f"{label}: pieces already on disk, continuing with its halves")
        return [row for half in split_request(request)
                for row in acquire(half, view, client, gate, root=root, settled=settled, log=log)]
    quote = gate.quote(view, p)
    if over_request_cap(quote, gate.request_cap_usd):
        assert quote is not None
        log(f"{label}: quoted ${quote.usd:.6f} > request cap ${gate.request_cap_usd:.2f}, "
            "splitting")
        return [row for half in split_request(request)
                for row in acquire(half, view, client, gate, root=root, settled=settled, log=log)]
    action = buy_one(request, quote, client, gate, target, settled)
    log(f"{label}: {action} · session ${gate.session_spent_usd():.4f}")
    return [{"request": p.as_kwargs(), "action": "bought", "path": str(target)}]


def run_buy(client: Any, gate: LockedQuoteGate, requests: list[PlannedRequest], *,
            root: Path = VENDOR_ROOT, log: Callable[[str], None],
            sleep: Callable[[float], None] = time.sleep) -> list[dict[str, Any]]:
    """Every request in plan order, serially. The plan and the disk/ledger state are checked
    before the first vendor call; the first failure raises and stops the run."""
    if not 0.0 < gate.session_cap_usd <= E1_SESSION_CAP_MAX_USD:
        raise BudgetRefusedError(f"session cap ${gate.session_cap_usd:.2f} is not in "
                                 f"(0, {E1_SESSION_CAP_MAX_USD:.2f}]: set by the lead first")
    validate_plan(requests)
    client.batch = ForbiddenNamespace()  # the buy path needs timeseries.get_range only
    entries = read_entries(gate.ledger_path)
    log(f"resume scan: {resume_scan(entries, gate.session_id, root)}")
    settled = settled_keys(entries, gate.session_id)
    view = QuoteOnlyView(client, sleep)
    return [row for r in requests
            for row in acquire(r, view, client, gate, root=root, settled=settled, log=log)]


# ------------------------------------------------------------- inventory ----
@dataclass(frozen=True, slots=True)
class FileInventory:
    """What the lead's integrity check may see of a raw file. No price, size or volume."""

    record_count: int
    first_ts_event_utc: str | None
    last_ts_event_utc: str | None
    symbols: tuple[str, ...]
    instrument_ids: tuple[str, ...]
    schema: str
    sha256: str


def ns_to_iso_z(ns: int) -> str:
    seconds, frac = divmod(int(ns), 10**9)
    return f"{datetime.fromtimestamp(seconds, UTC):%Y-%m-%dT%H:%M:%S}.{frac:09d}Z"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def inventory(path: Path) -> FileInventory:
    """Record count, first and last ts_event, the metadata's symbols and mapped instrument ids,
    schema and sha256. Only the ts_event column of the records is read."""
    import databento  # lazy: tests use synthetic files

    store = databento.DBNStore.from_file(path)
    count, first, last = 0, None, None
    for chunk in store.to_ndarray(count=1_000_000):
        ts_event = chunk["ts_event"]
        if len(ts_event) == 0:
            continue
        first = int(ts_event[0]) if first is None else first
        last = int(ts_event[-1])
        count += len(ts_event)
    mappings = store.metadata.mappings or {}
    ids = sorted({str(i["symbol"]) for intervals in mappings.values() for i in intervals
                  if str(i["symbol"]).strip()})
    return FileInventory(
        record_count=count,
        first_ts_event_utc=None if first is None else ns_to_iso_z(first),
        last_ts_event_utc=None if last is None else ns_to_iso_z(last),
        symbols=tuple(store.metadata.symbols), instrument_ids=tuple(ids),
        schema=str(store.schema), sha256=file_sha256(Path(path)))


# ------------------------------------------------------------------- CLI ----
def log_line(message: str) -> None:
    print(f"[{datetime.now(LOCAL_TZ):%Y-%m-%d %H:%M:%S %Z}] {message}", flush=True)


def build_client(key: str) -> Any:
    import databento  # lazy: the tests never build a real client

    return databento.Historical(key)


def main(argv: list[str] | None = None, *,
         key_loader: Callable[[], str] = require_databento_key,
         gate_factory: Callable[[], LockedQuoteGate] = e1_gate,
         client_factory: Callable[[str], Any] = build_client,
         summary_path: Path = SUMMARY_PATH, vendor_root: Path = VENDOR_ROOT,
         log: Callable[[str], None] = log_line) -> int:
    parser = argparse.ArgumentParser(prog="python -m data.pull_universe")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--quote-only", action="store_true", help="price step 1 (free)")
    mode.add_argument("--buy", action="store_true", help="buy step 1 through the gate")
    args = parser.parse_args(argv)
    try:
        gate = gate_factory()
        log(banner(gate))
        if gate.account_id != ACTIVE_ACCOUNT:
            raise UnknownAccountError(f"gate account {gate.account_id} is not the active "
                                      f"account {ACTIVE_ACCOUNT}")
        if args.buy and not 0.0 < gate.session_cap_usd <= E1_SESSION_CAP_MAX_USD:
            raise BudgetRefusedError(
                f"--buy needs the lead-set E1_SESSION_CAP_USD in (0, "
                f"{E1_SESSION_CAP_MAX_USD:.2f}]; it is {gate.session_cap_usd:.2f}")
        plan = plan_requests()
        log(f"plan: {len(plan)} requests over {len(STEP1_ROOTS)} roots before splitting")
        key = key_loader()
    except (PullUniverseError, BudgetRefusedError, UnknownAccountError, MissingSecretError,
            ExternalLedgerUnavailableError, OSError, ValueError) as exc:
        print(f"REFUSED before any vendor call ({type(exc).__name__}): {exc}", file=sys.stderr)
        return RC_REFUSED
    client = client_factory(key)
    try:
        if args.quote_only:
            pieces = run_quote_only(client, gate, plan, log=log)
            summary = build_summary(pieces, gate)
            log(f"TOTAL QUOTED ${summary['total_usd']:.6f} · {summary['counts']} · wrote "
                f"{write_summary(summary, summary_path)}")
            return 0 if summary["complete"] else RC_STOPPED
        done = run_buy(client, gate, plan, root=vendor_root, log=log)
    except (PullUniverseError, BudgetRefusedError, UnknownAccountError,
            ExternalLedgerUnavailableError, OSError) as exc:
        print(f"RUN STOPPED ({type(exc).__name__}): {exc}. Nothing after this request was "
              "requested; see the ledger and docs/ACCESS.md.", file=sys.stderr)
        return RC_STOPPED
    log(f"buy finished: {len(done)} pieces · {banner(gate)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
