"""Stage E.2b Task 4: the Stage E step 2 purchase path (design D4, D11.4, D13; ML design M1).

    uv run python -m data.pull_step2 --quote-only --set ml-route    # free, $0.00 quote lines
    uv run python -m data.pull_step2 --quote-only --set clusters    # free, $0.00 quote lines
    uv run python -m data.pull_step2 --quote-only --set clusters --retry-failed
    uv run python -m data.pull_step2 --buy --ml-route --harness-sha256 <sha256>
    uv run python -m data.pull_step2 --buy --cluster K2 --harness-sha256 <sha256>
    uv run python -m data.pull_step2 --status                       # per-product holdout-2 seals
    # Stage E.12 (harness v8):
    uv run python -m data.pull_step2 --quote-only --set ml-v2 --training-window
    uv run python -m data.pull_step2 --quote-only --set ml-v2 --holdout2-only --quotes-out <json>
    uv run python -m data.pull_step2 --quote-only --set ml-v2 --extension-2010 --quotes-out <json>
    uv run python -m data.pull_step2 --buy --account acct-1 --roots ZN,ZB --training-window \
        --harness-sha256 <sha256>

Step 2 is each product's 2019-05..2025-03 history: 71 ohlcv-1m monthly chunks of ``<ROOT>.v.0``
(continuous, GLBX.MDP3), bought OLDEST first, root by root. Lead ruling OC-R: a contract listed
later starts at its first vendor-priceable month (``FIRST_PRICED_MONTH``: MBT 2021-04, MCL
2021-06, MHG 2022-04); earlier months are never requested. The 58 chunks 2019-05..2024-02 are
kept (the step 2 bar store, data.step2_store, builds trade dates 2019-05-06..2024-02-29 from
them); the 13 chunks range=2024-03-01_2024-04-01 .. range=2025-03-01_2025-04-01 (March 2024's
embargo plus holdout-2) are each sealed in the download call right after the record-byte check,
before the next chunk is requested, in the product's own sealed store (data.step2_seal).

Two request sets:
- ML route (M1, frozen): the 31 price-path contracts ``ML_ROUTE_CONTRACTS``;
- per cluster (D13 step 2, U4): the cluster's traded vehicles (status "chosen" or "undersized",
  R10) from the E.2a vehicle table reports/stage_e2a_vehicles.json (read-only, recorded by
  sha256) and every leg root its active members read (``CLUSTER_EXTRA_EXPOSURES``, from the frozen
  catalog; MES excluded; K8 is legs only). Quote sets: "ml-route" (a), "clusters" (b: chosen
  vehicles only, as first quoted) and "clusters-legs" (b2: the purchase mode's roots, K1..K8).
Only the 45 admissible step 1 contracts can be step 2 roots; MES (its own D.1f store) and the
named step 1 refusals are refused.

Every chunk passes ``check_chunk`` before any vendor call: the root, symbol, dataset, schema and
stype; the chunk must be one of the 71 and not before the root's first priced month
(Step2BeforeListing); and the CME trade-date guard (data.trade_date_guard,
ruling L-9): no minute booked to a holdout-1 trade date, and no minute booked to a holdout-2
trade date unless the chunk is one of the 13 sealing chunks. The whole plan is checked first.

Buy flow per chunk (``run_buy``): harness preflight (screening.harness_freeze.preflight with the
required expected sha256) FIRST, then the caps: the gate is the active step 2 purchase policy of
data/config.py (STEP2_PURCHASE_SESSION_ID with STEP2_SESSION_CAP_USD and STEP2_REQUEST_CAP_USD; a
purchase session sets its own block there and repoints the three) on the account --buy names
(--account, required; its registry cap), and with the session's caps at $0.00 the buy refuses to
start. Then quote ->
authorize (session cap, request cap, the account's cap; no splitting: a chunk over the request cap
is refused) ->
commit -> download to .partial -> os.link -> read-only -> record-byte check -> settle -> for a
holdout-2 chunk, seal. A holdout-2 chunk never leaves plaintext behind: a failure after the
download (byte check, settle or seal) removes the plaintext before the error is raised, and a
failed download removes its .partial (the commit stays in the ledger, pessimistic). Delivery
above the quote is settled pro rata; the chunk is sealed (holdout-2) or kept, and the run stops.

Resume: an unsealed chunk on disk with a settle line of the same request (any session, the step 2
purchase spans several sessions) is skipped; a file without a settle line, or a settle line
without a file, stops the run (ResumeStateError, nothing deleted). A holdout-2 chunk sealed in the
product's manifest is skipped; one sealed but with plaintext left (a seal cut off after its
manifest record) is finished by data.holdout.complete_interrupted_seal; one on disk unsealed (a
run cut off between the link and the seal) is byte-checked and sealed. Each product's purchase
manifest reports/step2/purchase_<ROOT>.json (the store builder's expected sha256s and record
counts) is updated after every chunk and carries the harness sha256.

--quote-only installs the forbidden guards on the client's timeseries and batch namespaces, calls
only ``gate.quote`` (free metadata endpoints) and writes reports/stage_e2b_step2_quotes.json and
.md (costs, bytes and counts only). It does not call the harness preflight (the quote run happens
before the manifest exists). ``--retry-failed`` re-quotes only the chunks of the set with no
successful quote line under this session.

Stage E.12 (harness v8; V19, V23 items 4 and 19):
- ``--account acct-1|acct-2``: the gate is built on that account (data.config.ACCOUNTS; acct-1's
  gate reads its external ledger) and the key loader reads that account's key. Required with
  --buy; --quote-only defaults to ACTIVE_ACCOUNT. The banner names the account, never the key.
- ``--roots R1,R2,...`` (--buy and --quote-only): an explicit list of distinct roots, each one of
  the 28 v2 price paths ``ML_V2_PRICE_PATHS``. ``--set ml-v2`` quotes all 28.
- ``--training-window``: each root's plan is its unsealed chunks from its first priced month
  through range=2024-02-01_2024-03-01 only, and ``check_chunk`` refuses any chunk starting on or
  after 2024-03-01 (Step2AfterTrainingWindow). While data.config.STEP2_TRAINING_WINDOW_ONLY is
  True, --buy without it is refused before any vendor call (in ``main`` and in ``run_buy``).
- ``--holdout2-only`` and ``--extension-2010`` (--quote-only only): the 13 sealed chunks
  2024-03..2025-03 per root, and the monthly chunks 2010-01-01..2019-05-01 (exclusive) per root
  (MBT skipped by name: first priced 2021-04). Their plans are ``QuoteOnlyChunk`` items, a separate
  type that ``check_chunk`` (and so ``validate_plan`` and ``run_buy``) refuses; they reach only
  ``gate.quote`` under ``install_forbidden_guards``.
- ``--quotes-out PATH`` (a .json; the .md is written beside it): default
  reports/stage_e12_quotes.json. E.2b's reports/stage_e2b_step2_quotes.json and .md are refused as
  targets, so they are never overwritten. The quote summary also reports both accounts' positions
  (spent, cap, headroom) from each account's gate.
"""

from __future__ import annotations

import argparse
import json
import os
import stat
import sys
import time
from collections.abc import Callable, Iterable, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

from data import adapter
from data import step2_seal as seal
from data import trade_date_guard as tdg
from data.adapter import OHLCV_1M, STYPE_CONTINUOUS
from data.config import (
    ACCOUNT_2_ID,
    ACCOUNTS,
    ACTIVE_ACCOUNT,
    DATASET,
    REPO_ROOT,
    STEP2_PURCHASE_SESSION_ID,
    STEP2_REQUEST_CAP_USD,
    STEP2_SESSION_CAP_USD,
    STEP2_TRAINING_WINDOW_ONLY,
    VENDOR_ROOT,
    MissingSecretError,
    require_databento_key,
)
from data.pull_mes import monthly_chunks
from data.pull_universe import (
    REFUSED_ROOTS,
    STEP1_ROOTS,
    DeliveryCheckError,
    DownloadError,
    ResumeStateError,
    download,
    file_sha256,
    inventory,
    target_path,
)
from data.quote_universe import (
    LOCAL_TZ,
    MAX_WORKERS,
    PRODUCTS_BY_ROOT,
    ForbiddenNamespace,
    LockedQuoteGate,
    QuoteOnlyView,
    install_forbidden_guards,
    request_key,
)
from data.research_bars import CONFIRMATION_RAW_CHUNKS, HOLDOUT2_RAW_CHUNKS
from data.spend_gate import (
    BudgetRefusedError,
    ExternalLedgerUnavailableError,
    Quote,
    RequestParams,
    UnknownAccountError,
    read_entries,
    resolve_account,
)
from screening import harness_freeze

# ------------------------------------------------------------- the range ----
STEP2_START = date(2019, 5, 1)
STEP2_END = date(2025, 4, 1)  # exclusive, 00:00 UTC
STEP2_CHUNKS: tuple[tuple[str, str], ...] = tuple(monthly_chunks(STEP2_START, STEP2_END))
if (*CONFIRMATION_RAW_CHUNKS, *HOLDOUT2_RAW_CHUNKS) != STEP2_CHUNKS or len(STEP2_CHUNKS) != 71:
    raise RuntimeError("step 2 must be the 58 unsealed chunks 2019-05..2024-02 then the 13 "
                       "holdout-2 chunks 2024-03..2025-03 (data.research_bars)")
SEALED_CHUNKS = frozenset(HOLDOUT2_RAW_CHUNKS)

# Lead ruling OC-R (2026-09-26): a contract is never requested for months before it was listed.
# Each root's step 2 plan starts at its FIRST VENDOR-PRICEABLE month; earlier months are not
# requested and are not counted as refusals. Frozen from the ledger's free quote lines (no new
# metadata call): every root with no entry here priced every month 2019-05..2025-03 in E.0's
# quotes (session stage-E.0-2026-09-23) and, for the 37 roots quoted again in this session,
# in E.2b's (stage-E.2b-2026-09-26). The three entries below failed every earlier month in BOTH
# sessions with "422 symbology_invalid_request: None of the symbols could be resolved" and priced
# every month from the listed one through 2025-03 (E.0's notes: MBT before 2021-04, MCL before
# 2021-06, MHG before 2022-04; the catalog's listing dates MBT 2021-05-03, MCL 2021-07-12).
FIRST_PRICED_MONTH: dict[str, str] = {"MBT": "2021-04-01", "MCL": "2021-06-01",
                                      "MHG": "2022-04-01"}
# Refused for step 2 by name: E.0 priced MNG 2019-05..2019-12 and 2023-10 on, but not 2020-01 ..
# 2023-09 (a pricing gap inside the range). MNG is in no step 2 set; the lead decides if needed.
STEP2_UNPLANNABLE: dict[str, str] = {
    "MNG": "E.0 quotes price 2019-05..2019-12 and 2023-10..2025-03 only (gap 2020-01..2023-09)"}
_CHUNK_OF_START = {start: (start, end) for start, end in STEP2_CHUNKS}
if any(m not in _CHUNK_OF_START or _CHUNK_OF_START[m] in SEALED_CHUNKS
       for m in FIRST_PRICED_MONTH.values()):
    raise RuntimeError("a first priced month must start an unsealed step 2 chunk")

# The 31 price-path contracts of the ML route (docs/STAGE_E_ML_DESIGN.md M1, Stage E.2a ruling on
# audit ML-A07; frozen): cluster -> roots.
ML_ROUTE_CONTRACTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("K1", ("NQ", "RTY", "YM")),
    ("K2", ("ZT", "ZF", "ZN", "TN", "ZB", "UB")),
    ("K3", ("6E", "6A", "6B", "6C", "6J", "6S", "6N")),
    ("K4", ("CL", "NG", "RB", "HO")),
    ("K5", ("GC", "SI", "HG")),
    ("K6", ("ZC", "ZW", "ZS", "ZM", "ZL", "HE", "LE")),
    ("K7", ("MBT",)),
)
ML_ROUTE_ROOTS: tuple[str, ...] = tuple(r for _, roots in ML_ROUTE_CONTRACTS for r in roots)
if len(ML_ROUTE_ROOTS) != 31 or len(set(ML_ROUTE_ROOTS)) != 31 \
        or not set(ML_ROUTE_ROOTS) <= set(STEP1_ROOTS) \
        or any(PRODUCTS_BY_ROOT[r].cluster != c for c, rs in ML_ROUTE_CONTRACTS for r in rs):
    raise RuntimeError("the ML route's price-path contracts must be M1's 31 admissible roots")

# Stage E.12 (harness v8): the 28 price paths of ML route v2 = ML_ROUTE_ROOTS minus RB, HO and SI,
# i.e. the values of ml_route_v2.constants.UNIVERSE (docs/STAGE_E_ML_V2_DESIGN.md V2.1). A literal
# on purpose: the harness never imports ml_route_v2; the check below ties it to ML_ROUTE_ROOTS.
ML_V2_PRICE_PATHS: tuple[str, ...] = (
    "NQ", "RTY", "YM", "ZT", "ZF", "ZN", "TN", "ZB", "UB", "6E", "6A", "6B", "6C", "6J", "6S",
    "6N", "CL", "NG", "GC", "HG", "ZC", "ZW", "ZS", "ZM", "ZL", "HE", "LE", "MBT")
ML_V2_DROPPED: tuple[str, ...] = ("RB", "HO", "SI")
if tuple(r for r in ML_ROUTE_ROOTS if r not in ML_V2_DROPPED) != ML_V2_PRICE_PATHS \
        or len(ML_V2_PRICE_PATHS) != 28 or not set(ML_V2_DROPPED) <= set(ML_ROUTE_ROOTS):
    raise RuntimeError("the v2 price paths must be ML_ROUTE_ROOTS minus RB, HO and SI (28)")
ML_V2_CONTRACTS: tuple[tuple[str, tuple[str, ...]], ...] = tuple(
    (c, tuple(r for r in roots if r in ML_V2_PRICE_PATHS)) for c, roots in ML_ROUTE_CONTRACTS)
# V23 item 4: phase 1 is the training window only, ending with range=2024-02-01_2024-03-01; no
# chunk starting on or after TRAINING_WINDOW_END is bought under --training-window.
TRAINING_WINDOW_END = "2024-03-01"
LAST_TRAINING_CHUNK = ("2024-02-01", "2024-03-01")
if LAST_TRAINING_CHUNK not in STEP2_CHUNKS or LAST_TRAINING_CHUNK in SEALED_CHUNKS \
        or LAST_TRAINING_CHUNK[1] != TRAINING_WINDOW_END \
        or any(s < TRAINING_WINDOW_END for s, _ in SEALED_CHUNKS):
    raise RuntimeError("the training window must end with the last unsealed chunk 2024-02")
# Task 7 quote-only plans (priced, never bought): the 2010 extension, monthly chunks from
# 2010-01-01 to 2019-05-01 (exclusive). A root with no history there fails its quotes like any
# unpriceable chunk; MBT is skipped by name (first priced month 2021-04, OC-R).
EXTENSION_2010_START = date(2010, 1, 1)
EXTENSION_2010_END = date(2019, 5, 1)  # exclusive, 00:00 UTC: where step 2 starts
EXTENSION_2010_CHUNKS: tuple[tuple[str, str], ...] = tuple(
    monthly_chunks(EXTENSION_2010_START, EXTENSION_2010_END))
if len(EXTENSION_2010_CHUNKS) != 112 or EXTENSION_2010_CHUNKS[-1][1] != STEP2_CHUNKS[0][0]:
    raise RuntimeError("the 2010 extension must be the 112 months 2010-01..2019-04")
EXTENSION_2010_SKIPPED: dict[str, str] = {
    "MBT": "first priced month 2021-04 (OC-R): no 2010-2019 history to quote"}
PLAN_HOLDOUT2_ONLY, PLAN_EXTENSION_2010 = "holdout2-only", "extension-2010"
CLUSTERS: tuple[str, ...] = ("K1", "K2", "K3", "K4", "K5", "K6", "K7")
LEG_CLUSTERS: tuple[str, ...] = (*CLUSTERS, "K8")
VEHICLES_PATH = REPO_ROOT / "reports" / "stage_e2a_vehicles.json"
CHOSEN = "chosen"
# D2 R10 (reports/stage_e2a_vehicle_rule_readings.md): an "undersized" exposure is traded at the
# cap on its vehicle, so it is a traded vehicle too; "no candidate" exposures are not traded.
TRADED_STATUSES = frozenset({"chosen", "undersized"})
# Lead ruling (InputsCoder Q-6, 2026-09-26): a cluster's step 2 purchase is its traded vehicles AND
# every signal-leg root its active members read (D4 cross-product windows), MES excluded (owned).
# From the frozen catalog (reports/stage_e0_catalog_K1..K8.md, E.1 freeze), "Products read":
# - K1..K7: every active member reads only its own cluster's vehicles (K6's crush member reads ZS,
#   ZM and ZL, all K6 vehicles), plus external data that is not a GLBX product (K1: VXN close, ISM
#   calendar; K3-mehedge-01: the EURO STOXX 50 and Nikkei 225 daily indices; event calendars).
#   K1's MES leg belonged to K1-ml-01 only, which is excluded (U6).
# - K8 has no vehicle of its own: traded legs gold (K8-flight-01), CAD (K8-oilcad-01) and the
#   Nasdaq-100 (K8-wkndbtc-01); signal legs the S&P 500 on MES bars (excluded: owned), WTI crude on
#   the crude exposure's price-path bars ("CL's bars if CL is ... declared MCL's price path,
#   otherwise the vehicle's own bars": no declaration exists, so the vehicle's) and bitcoin on MBT.
# Exposures resolve to vehicles through the E.2a vehicle table.
CLUSTER_EXTRA_EXPOSURES: dict[str, tuple[str, ...]] = {
    "K8": ("gold", "CAD", "Nasdaq-100", "WTI crude", "bitcoin")}

STEP2_REPORTS = REPO_ROOT / "reports" / "step2"
QUOTES_JSON = REPO_ROOT / "reports" / "stage_e2b_step2_quotes.json"
QUOTES_MD = REPO_ROOT / "reports" / "stage_e2b_step2_quotes.md"
# Stage E.12 on: the --quote-only default (--quotes-out); E.2b's files above are never targets.
QUOTES_OUT_DEFAULT = REPO_ROOT / "reports" / "stage_e12_quotes.json"
SET_ML, SET_CLUSTERS, SET_CLUSTERS_LEGS = "ml-route", "clusters", "clusters-legs"
SET_ML_V2 = "ml-v2"
QUOTE_SETS = (SET_ML, SET_CLUSTERS, SET_CLUSTERS_LEGS, SET_ML_V2)
STEP2_NOTE = "Stage E step 2 purchase"
ACCOUNT_2_CREDIT_USD = 125.00  # U5: acct-2's credit when it was opened (docs/STAGE_E_DESIGN.md D13)
RC_REFUSED = 2
RC_STOPPED = 1


# --------------------------------------------------------------- errors ----
class Step2Error(RuntimeError):
    """Base: the step 2 run stopped at a named problem. Nothing after it was requested."""


class Step2RefusedRoot(Step2Error):
    """A root that is not one of the 45 admissible step 1 contracts (MES included)."""


class Step2ChunkError(Step2Error):
    """A request that is not one of the 71 step 2 chunks, or not ohlcv-1m continuous."""


class Step2BeforeListing(Step2ChunkError):
    """A month before the contract's first vendor-priceable month (OC-R): never requested."""


class Step2TradeDateError(Step2Error):
    """data.trade_date_guard refused the chunk (holdout booking or unbookable minutes)."""


class Step2CapError(Step2Error):
    """The buy was asked to start with a zero session or request cap."""


class Step2AfterTrainingWindow(Step2ChunkError):
    """Under --training-window: a chunk starting on or after 2024-03-01 (V23 item 4)."""


class Step2QuoteOnlyChunk(Step2ChunkError):
    """A quote-only plan item (holdout-2-only or 2010 extension) offered to the buy path's
    checks, or a quote-only item that is not one of its plan's chunks."""


class Step2TrainingWindowRequired(Step2Error):
    """STEP2_TRAINING_WINDOW_ONLY is True and a buy was asked for without --training-window."""


# ------------------------------------------------------------------ plan ----
@dataclass(frozen=True, slots=True)
class Chunk:
    root: str
    params: RequestParams
    sealing: bool  # one of the 13 holdout-2 chunks: sealed in its download call

    @property
    def cluster(self) -> str:
        return PRODUCTS_BY_ROOT[self.root].cluster

    @property
    def key(self) -> str:
        return request_key(self.params.as_kwargs())


def check_root(root: str) -> str:
    if root == "MES" or root in REFUSED_ROOTS:
        raise Step2RefusedRoot(f"{root!r} is refused for step 2 (MES has its own D.1f store; "
                               f"named refusals {', '.join(REFUSED_ROOTS)})")
    if root not in STEP1_ROOTS:
        raise Step2RefusedRoot(f"{root!r} is not one of the 45 admissible contracts")
    if root in STEP2_UNPLANNABLE:
        raise Step2RefusedRoot(f"{root!r} is refused for step 2: {STEP2_UNPLANNABLE[root]}")
    return root


def first_priced_month(root: str) -> str:
    """The first month the vendor prices ``root`` (OC-R table), as a chunk start."""
    return FIRST_PRICED_MONTH.get(check_root(root), STEP2_CHUNKS[0][0])


def step2_chunks(root: str) -> tuple[tuple[str, str], ...]:
    """``root``'s step 2 chunks: from its first priced month through 2025-03, oldest first."""
    first = first_priced_month(root)
    return tuple(c for c in STEP2_CHUNKS if c[0] >= first)


def unsealed_chunks(root: str) -> tuple[tuple[str, str], ...]:
    """The kept (unsealed) part of ``root``'s plan: what its step 2 store is built from."""
    return tuple(c for c in step2_chunks(root) if c not in SEALED_CHUNKS)


def training_window_chunks(root: str) -> tuple[tuple[str, str], ...]:
    """``root``'s training-window plan (--training-window, V23 item 4): its unsealed chunks from
    its first priced month through range=2024-02-01_2024-03-01 only."""
    return tuple(c for c in unsealed_chunks(root) if c[0] < TRAINING_WINDOW_END)


def _params(root: str, start: str, end: str) -> RequestParams:
    return RequestParams(DATASET, (seal.continuous(root),), OHLCV_1M, STYPE_CONTINUOUS,
                         start, end)


def chunk_for(root: str, start: str, end: str) -> Chunk:
    check_root(root)
    return Chunk(root, _params(root, start, end), (start, end) in SEALED_CHUNKS)


def _check_distinct(roots: Sequence[str]) -> None:
    if len(set(roots)) != len(roots) or not roots:
        raise Step2RefusedRoot(f"step 2 roots must be distinct and non-empty: {list(roots)}")


def plan_step2(roots: Sequence[str], *, training_window: bool = False) -> list[Chunk]:
    """Every root's chunks from its first priced month (OC-R) through 2025-03, oldest first,
    roots in the given order (each root once). ``training_window``: through 2024-02 only."""
    _check_distinct(roots)
    chunks_of = training_window_chunks if training_window else step2_chunks
    plan = [chunk_for(r, s, e) for r in roots for s, e in chunks_of(r)]
    validate_plan(plan, training_window=training_window)
    return plan


def _check_request(root: str, p: RequestParams) -> None:
    if p.symbols != (seal.continuous(root),) or (p.dataset, p.schema, p.stype_in) != (
            DATASET, OHLCV_1M, STYPE_CONTINUOUS):
        raise Step2ChunkError(f"not a step 2 request for {root}: {p.as_kwargs()}")


def check_chunk(chunk: Chunk, *, training_window: bool = False) -> None:
    """Everything a chunk must satisfy before any vendor call. Raises, never warns.
    ``training_window`` (--training-window): no chunk starting on or after 2024-03-01."""
    if type(chunk) is not Chunk:  # a QuoteOnlyChunk (or anything else) is never bought
        raise Step2QuoteOnlyChunk(
            f"{type(chunk).__name__} {getattr(chunk, 'root', '?')}: only a step 2 Chunk passes "
            "check_chunk; quote-only plans (holdout-2-only, 2010 extension) are never bought")
    check_root(chunk.root)
    p = chunk.params
    _check_request(chunk.root, p)
    if (p.start, p.end) not in STEP2_CHUNKS:
        raise Step2ChunkError(f"{chunk.root} {p.start}..{p.end} is not one of the 71 monthly "
                              "chunks 2019-05..2025-03")
    if training_window and p.start >= TRAINING_WINDOW_END:
        raise Step2AfterTrainingWindow(
            f"{chunk.root} range={p.start}_{p.end} starts on or after {TRAINING_WINDOW_END}: "
            "refused under --training-window (phase 1 ends with range=2024-02-01_2024-03-01)")
    if p.start < first_priced_month(chunk.root):
        raise Step2BeforeListing(
            f"{chunk.root} {p.start}..{p.end} is before its first vendor-priceable month "
            f"{first_priced_month(chunk.root)} (lead ruling OC-R): never requested")
    if chunk.sealing != ((p.start, p.end) in SEALED_CHUNKS):
        raise Step2ChunkError(f"{chunk.root} {p.start}..{p.end}: sealing flag is wrong")
    try:
        tdg.refuse_holdout_bookings(chunk.root, p.start, p.end, sealing=chunk.sealing)
    except tdg.TradeDateRefused as exc:
        raise Step2TradeDateError(str(exc)) from exc


def validate_plan(plan: Iterable[Chunk], *, training_window: bool = False) -> None:
    for chunk in plan:
        check_chunk(chunk, training_window=training_window)


# ------------------------------------------------ quote-only plans (Task 7) ----
@dataclass(frozen=True, slots=True)
class QuoteOnlyChunk:
    """A chunk priced for a later phase and never bought: one of the 13 holdout-2 chunks
    (``PLAN_HOLDOUT2_ONLY``) or a 2010 extension month (``PLAN_EXTENSION_2010``). Not a
    ``Chunk``: check_chunk, validate_plan and run_buy refuse it."""
    root: str
    params: RequestParams
    kind: str

    @property
    def sealing(self) -> bool:  # summaries file a holdout-2 quote under the sealed column
        return self.kind == PLAN_HOLDOUT2_ONLY

    @property
    def cluster(self) -> str:
        return PRODUCTS_BY_ROOT[self.root].cluster

    @property
    def key(self) -> str:
        return request_key(self.params.as_kwargs())


def check_quote_only_chunk(item: QuoteOnlyChunk) -> None:
    """A quote-only item's checks before its (free) metadata call. No bar is downloaded, so the
    trade-date guard (a booking check on downloaded minutes) does not apply."""
    if type(item) is not QuoteOnlyChunk:
        raise Step2QuoteOnlyChunk(f"{type(item).__name__}: not a quote-only plan item")
    check_root(item.root)
    p = item.params
    _check_request(item.root, p)
    if item.kind == PLAN_HOLDOUT2_ONLY:
        if (p.start, p.end) not in SEALED_CHUNKS:
            raise Step2QuoteOnlyChunk(f"{item.root} {p.start}..{p.end} is not one of the 13 "
                                      "holdout-2 chunks 2024-03..2025-03")
        if p.start < first_priced_month(item.root):
            raise Step2BeforeListing(f"{item.root} {p.start}..{p.end} is before its first "
                                     "vendor-priceable month (OC-R): never requested")
    elif item.kind == PLAN_EXTENSION_2010:
        if (p.start, p.end) not in EXTENSION_2010_CHUNKS:
            raise Step2QuoteOnlyChunk(f"{item.root} {p.start}..{p.end} is not one of the 112 "
                                      "extension months 2010-01..2019-04")
        if item.root in EXTENSION_2010_SKIPPED:
            raise Step2RefusedRoot(f"{item.root}: {EXTENSION_2010_SKIPPED[item.root]}")
    else:
        raise Step2QuoteOnlyChunk(f"unknown quote-only plan kind {item.kind!r}")


def plan_quote_only(roots: Sequence[str], kind: str) -> tuple[list[QuoteOnlyChunk], list[str]]:
    """The quote-only plan of ``kind`` for ``roots`` (distinct, in order), and the roots skipped
    by name (the 2010 extension's MBT). Every item passes check_quote_only_chunk."""
    _check_distinct(roots)
    for root in roots:
        check_root(root)
    if kind == PLAN_HOLDOUT2_ONLY:
        skipped: list[str] = []
        months = {r: tuple(c for c in step2_chunks(r) if c in SEALED_CHUNKS) for r in roots}
    elif kind == PLAN_EXTENSION_2010:
        skipped = [r for r in roots if r in EXTENSION_2010_SKIPPED]
        months = {r: EXTENSION_2010_CHUNKS for r in roots if r not in EXTENSION_2010_SKIPPED}
    else:
        raise Step2Error(f"unknown quote-only plan kind {kind!r}")
    plan = [QuoteOnlyChunk(r, _params(r, s, e), kind) for r in roots for s, e in months.get(r, ())]
    if not plan:
        raise Step2Error(f"{kind}: nothing to quote for {list(roots)} (skipped {skipped})")
    for item in plan:
        check_quote_only_chunk(item)
    return plan, skipped


def check_for_quote(item: Chunk | QuoteOnlyChunk, *, training_window: bool = False) -> None:
    """The quote path's check: a quote-only item's own checks, else check_chunk."""
    if type(item) is QuoteOnlyChunk:
        check_quote_only_chunk(item)
    else:
        check_chunk(item, training_window=training_window)


# ------------------------------------------------------------- --roots ----
def parse_roots(text: str) -> tuple[str, ...]:
    """--roots R1,R2,...: distinct, non-empty, each one of the 28 v2 price paths."""
    roots = tuple(r.strip() for r in text.split(","))
    if not text.strip() or any(not r for r in roots):
        raise Step2RefusedRoot(f"--roots must be a comma-separated list of roots: {text!r}")
    outside = [r for r in roots if r not in ML_V2_PRICE_PATHS]
    if outside:
        raise Step2RefusedRoot(f"--roots {outside} not among the 28 v2 price paths "
                               f"ML_V2_PRICE_PATHS ({', '.join(ML_V2_PRICE_PATHS)})")
    _check_distinct(roots)
    for root in roots:
        check_root(root)
    return roots


def groups_by_cluster(roots: Sequence[str]) -> dict[str, tuple[str, ...]]:
    """cluster -> the given roots in it, in the given order (the --roots quote summary)."""
    out: dict[str, list[str]] = {}
    for root in roots:
        out.setdefault(PRODUCTS_BY_ROOT[root].cluster, []).append(root)
    return {c: tuple(rs) for c, rs in sorted(out.items())}


def cluster_vehicles(path: Path = VEHICLES_PATH, statuses: frozenset[str] = frozenset({CHOSEN})
                     ) -> dict[str, tuple[str, ...]]:
    """cluster -> its vehicles with a status in ``statuses`` (default "chosen": set (b)), in
    the table's exposure order."""
    table = json.loads(Path(path).read_text(encoding="utf-8"))
    out: dict[str, list[str]] = {c: [] for c in CLUSTERS}
    for row in table["exposures"]:
        if row["status"] in statuses:
            out[row["cluster"]].append(check_root(row["vehicle"]))
    return {c: tuple(v) for c, v in out.items()}


def exposure_vehicles(path: Path = VEHICLES_PATH) -> dict[str, str]:
    """exposure -> its traded vehicle (status chosen or undersized)."""
    table = json.loads(Path(path).read_text(encoding="utf-8"))
    return {row["exposure"]: check_root(row["vehicle"]) for row in table["exposures"]
            if row["status"] in TRADED_STATUSES}


def cluster_roots(path: Path = VEHICLES_PATH, clusters: Sequence[str] = LEG_CLUSTERS
                  ) -> dict[str, tuple[str, ...]]:
    """cluster (K1..K8) -> the roots its step 2 purchase buys: its traded vehicles (chosen or
    undersized) and every signal- or traded-leg root its active members read (frozen catalog),
    MES excluded. K8 is legs only."""
    traded = cluster_vehicles(path, TRADED_STATUSES)
    by_exposure = exposure_vehicles(path)
    out = {}
    for cluster in clusters:
        roots = list(traded.get(cluster, ()))
        for exposure in CLUSTER_EXTRA_EXPOSURES.get(cluster, ()):
            if exposure not in by_exposure:
                raise Step2Error(f"{cluster}: leg exposure {exposure!r} has no traded vehicle in "
                                 f"{Path(path).name}")
            if by_exposure[exposure] not in roots:
                roots.append(by_exposure[exposure])
        out[cluster] = tuple(roots)
    return out


def roots_for(ml_route: bool, cluster: str | None, vehicles_path: Path = VEHICLES_PATH
              ) -> tuple[str, ...]:
    if ml_route == (cluster is not None):
        raise Step2Error("choose exactly one of the ML route or one cluster")
    if ml_route:
        return ML_ROUTE_ROOTS
    if cluster not in LEG_CLUSTERS:
        raise Step2Error(f"unknown cluster {cluster!r}")
    roots = cluster_roots(vehicles_path, (cluster,))[cluster]
    if not roots:
        raise Step2Error(f"{cluster} has no traded vehicle or leg in {vehicles_path.name}: "
                         "nothing to buy")
    return roots


# ------------------------------------------------------------------ gate ----
def step2_gate(**overrides: Any) -> LockedQuoteGate:
    """The active step 2 purchase policy of data/config.py: STEP2_PURCHASE_SESSION_ID with
    STEP2_SESSION_CAP_USD and STEP2_REQUEST_CAP_USD (from Stage E.12 they point at the E.12
    block: STAGE_E12_SESSION_ID and its caps), on ``account`` (ACTIVE_ACCOUNT, acct-2, unless
    given; the account's registry cap, and acct-1's gate reads its external ledger).
    The CLI passes only ``account``; the other ``overrides`` are for tests (tmp ledgers, caps)."""
    kwargs = {"session_cap_usd": STEP2_SESSION_CAP_USD, "request_cap_usd": STEP2_REQUEST_CAP_USD,
              "account": ACTIVE_ACCOUNT, **overrides}
    return LockedQuoteGate(STEP2_PURCHASE_SESSION_ID, **kwargs)


def banner(gate: LockedQuoteGate) -> str:
    """Session, account and caps. Never the key."""
    return (f"{gate.session_id}: account {gate.account_id} (cap ${gate.account_cap_usd:.2f}, "
            f"spent ${gate.account_spent_usd():.4f}) · session cap ${gate.session_cap_usd:.2f} "
            f"(spent ${gate.session_spent_usd():.4f}) · request cap ${gate.request_cap_usd:.2f}")


def require_account(gate: LockedQuoteGate, account: str) -> None:
    """The gate must sit on ``account``, a registered account (unknown ids fail closed)."""
    resolve_account(account)
    if gate.account_id != account:
        raise UnknownAccountError(f"gate account {gate.account_id} is not {account}")


def require_buy_caps(gate: LockedQuoteGate, account: str | None = None) -> None:
    """The gate is on ``account`` (any registered account passed explicitly; ACTIVE_ACCOUNT when
    None) and both session caps are positive."""
    require_account(gate, ACTIVE_ACCOUNT if account is None else account)
    if not (gate.session_cap_usd > 0.0 and gate.request_cap_usd > 0.0):
        raise Step2CapError(
            f"step 2 buy refused: session cap ${gate.session_cap_usd:.2f}, request cap "
            f"${gate.request_cap_usd:.2f} ({gate.session_id}). A purchase session sets its own "
            "caps in data/config.py first")


def require_training_window(training_window: bool) -> None:
    """The interlock: while data.config.STEP2_TRAINING_WINDOW_ONLY is True, a buy must run under
    --training-window. Read from this module at call time (tests patch it here)."""
    if STEP2_TRAINING_WINDOW_ONLY and not training_window:
        raise Step2TrainingWindowRequired(
            "step 2 buy refused: STEP2_TRAINING_WINDOW_ONLY is True (V23 item 4), so --buy needs "
            "--training-window (chunks through range=2024-02-01_2024-03-01 only)")


# ------------------------------------------------------------ quote-only ----
@dataclass(frozen=True, slots=True)
class ChunkQuote:
    chunk: Chunk | QuoteOnlyChunk
    usd: float | None
    billable_bytes: int | None

    @property
    def ok(self) -> bool:
        return self.usd is not None


def _quote_one(chunk: Chunk | QuoteOnlyChunk, view: Any, gate: LockedQuoteGate,
               training_window: bool = False) -> ChunkQuote:
    check_for_quote(chunk, training_window=training_window)
    quote = gate.quote(view, chunk.params)
    if quote is None:
        return ChunkQuote(chunk, None, None)
    return ChunkQuote(chunk, quote.usd, quote.billable_bytes)


def successful_quote_keys(entries: Iterable[dict[str, Any]], session_id: str) -> set[str]:
    return {request_key(e["request"]) for e in entries
            if e.get("session_id") == session_id and e.get("event") == "quote"
            and e.get("quoted_usd") is not None and "request" in e}


def run_quote_only(client: Any, gate: LockedQuoteGate, plan: list[Chunk] | list[QuoteOnlyChunk],
                   *, log: Callable[[str], None], retry_failed: bool = False,
                   workers: int = MAX_WORKERS, sleep: Callable[[float], None] = time.sleep,
                   training_window: bool = False) -> list[ChunkQuote]:
    """Quote the plan (free). Billable namespaces are guarded first; only ``gate.quote`` is
    called. ``retry_failed`` quotes only chunks with no successful quote under this session.
    A plan of QuoteOnlyChunk items (holdout-2-only, 2010 extension) is quoted the same way."""
    for item in plan:
        check_for_quote(item, training_window=training_window)
    install_forbidden_guards(client)
    todo = plan
    if retry_failed:
        done = successful_quote_keys(read_entries(gate.ledger_path), gate.session_id)
        todo = [c for c in plan if c.key not in done]
    view = QuoteOnlyView(client, sleep)
    with ThreadPoolExecutor(max_workers=max(1, min(workers, MAX_WORKERS))) as pool:
        futures = [pool.submit(_quote_one, c, view, gate, training_window) for c in todo]
        try:
            got = [f.result() for f in futures]
        except BaseException:
            pool.shutdown(wait=True, cancel_futures=True)
            raise
    log(f"quoted {len(todo)} of {len(plan)} chunks; {sum(not q.ok for q in got)} failed")
    return got


def quotes_from_ledger(plan: list[Chunk] | list[QuoteOnlyChunk], entries: list[dict[str, Any]],
                       session_id: str) -> list[ChunkQuote]:
    """The latest successful quote of each planned chunk under ``session_id``, else a failure.
    Lets a --retry-failed run and the first run form one summary."""
    latest: dict[str, dict[str, Any]] = {}
    for e in entries:
        if e.get("session_id") == session_id and e.get("event") == "quote" and "request" in e \
                and e.get("quoted_usd") is not None:
            latest[request_key(e["request"])] = e
    out = []
    for c in plan:
        e = latest.get(c.key)
        out.append(ChunkQuote(c, None, None) if e is None else
                   ChunkQuote(c, float(e["quoted_usd"]), int(e["billable_bytes"])))
    return out


# ------------------------------------------------------------- summaries ----
def account_position(gate: LockedQuoteGate) -> dict[str, Any]:
    """The gate's account by the gate's own arithmetic: spent = SpendGate.account_spent_usd (the
    sum of ``usd`` over this repo's ledger lines of the account, plus acct-1's external ledger;
    quotes $0.00, commits at the quote, settles as deltas), cap, headroom = cap - spent.
    Credit left is the cap headroom: since V19 acct-2's cap is its funds (the spend plus the
    2026-10-02 top-up, rounded down), and V23 counts acct-1's headroom as its funds.
    ``account_credit_usd`` stays acct-2's opening credit (U5); acct-1 shows its cap."""
    spent = gate.account_spent_usd()
    headroom = round(gate.account_cap_usd - spent, 6)
    credit = ACCOUNT_2_CREDIT_USD if gate.account_id == ACCOUNT_2_ID else gate.account_cap_usd
    return {"account": gate.account_id, "account_cap_usd": gate.account_cap_usd,
            "account_credit_usd": credit, "spent_usd": round(spent, 6),
            "cap_headroom_usd": headroom, "credit_left_usd": headroom}


def accounts_summary(gates: dict[str, LockedQuoteGate]) -> dict[str, Any]:
    """Both accounts' positions (spent, cap, headroom), each from its own gate, and the
    combined headroom (the E.12 session caps may never exceed it)."""
    positions = {a: account_position(g) for a, g in gates.items()}
    combined = round(sum(p["cap_headroom_usd"] for p in positions.values()), 6)
    return {"positions": positions, "combined_headroom_usd": combined}


def _topup(total: float, position: dict[str, Any]) -> dict[str, float]:
    """Money and cap needed to buy ``total`` (and total + 10%, D13's session-cap rule)."""
    out = {}
    for label, need in (("at_quote", total), ("at_quote_plus_10pct", total * 1.10)):
        out[f"topup_usd_{label}"] = round(max(0.0, need - position["credit_left_usd"]), 2)
        out[f"account_cap_needed_usd_{label}"] = round(position["spent_usd"] + need, 2)
    return out


def _usd_bucket(chunk: Chunk | QuoteOnlyChunk) -> str:
    """The per-contract column a quoted chunk adds to: kept, sealed, or the 2010 extension."""
    if getattr(chunk, "kind", None) == PLAN_EXTENSION_2010:
        return "usd_extension_2010_01_2019_04"
    return "usd_sealed_2024_03_2025_03" if chunk.sealing else "usd_unsealed_2019_05_2024_02"


def summarize_set(name: str, groups: dict[str, tuple[str, ...]], quotes: list[ChunkQuote],
                  position: dict[str, Any]) -> dict[str, Any]:
    """Per contract, per cluster and set totals (costs, bytes, counts; no price data)."""
    per_root: dict[str, dict[str, Any]] = {}
    for q in quotes:
        row = per_root.setdefault(q.chunk.root, {
            "cluster": q.chunk.cluster, "usd": 0.0, "usd_unsealed_2019_05_2024_02": 0.0,
            "usd_sealed_2024_03_2025_03": 0.0, "billable_bytes": 0, "chunks": 0,
            "quoted": 0, "failed": [], "largest_chunk_usd": 0.0})
        row["chunks"] += 1
        if not q.ok:
            row["failed"].append(f"{q.chunk.params.start}..{q.chunk.params.end}")
            continue
        usd = q.usd or 0.0
        row["quoted"] += 1
        row["usd"] += usd
        bucket = _usd_bucket(q.chunk)
        row[bucket] = row.get(bucket, 0.0) + usd
        row["billable_bytes"] += q.billable_bytes or 0
        row["largest_chunk_usd"] = max(row["largest_chunk_usd"], usd)
    per_cluster = {}
    for cluster, roots in groups.items():
        rows = [per_root[r] for r in roots if r in per_root]
        per_cluster[cluster] = {
            "contracts": list(roots), "usd": sum(r["usd"] for r in rows),
            "chunks_failed": sum(len(r["failed"]) for r in rows),
            "complete": all(not r["failed"] for r in rows)}
        per_cluster[cluster].update(_topup(per_cluster[cluster]["usd"], position))
    total = sum(r["usd"] for r in per_root.values())
    failed = sum(len(r["failed"]) for r in per_root.values())
    return {"set": name, "contracts": len(per_root), "chunks": len(quotes),
            "chunks_quoted": len(quotes) - failed, "chunks_failed": failed,
            "complete": failed == 0, "total_usd": total,
            "total_billable_bytes": sum(r["billable_bytes"] for r in per_root.values()),
            **_topup(total, position), "per_cluster": per_cluster, "per_contract": per_root}


def write_quotes_json(section: dict[str, Any], extra: dict[str, Any], path: Path = QUOTES_JSON
                      ) -> dict[str, Any]:
    """Update one set's section (and the shared header) of the quotes JSON, atomically."""
    current = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {"sets": {}}
    payload = {**current, **extra, "sets": {**current.get("sets", {}), section["set"]: section}}
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    tmp.replace(path)
    return payload


# ------------------------------------------------------------------- buy ----
def _purge(path: Path) -> None:
    """Remove a plaintext holdout file and its .partial (read-only files included, any OS)."""
    for p in (path, path.with_name(path.name + ".partial")):
        if p.exists():
            p.chmod(stat.S_IRUSR | stat.S_IWUSR)
            p.unlink()


def manifest_path(root: str, base: Path = STEP2_REPORTS) -> Path:
    return base / f"purchase_{root}.json"


def record_file(root: str, entry: dict[str, Any], base: Path, harness_sha: str) -> None:
    """Add (or replace by name) one chunk's entry in the product's purchase manifest."""
    path = manifest_path(root, base)
    current = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {
        "product": root, "continuous": seal.continuous(root), "schema": OHLCV_1M,
        "dataset": DATASET, "files": [], "sealed_chunks": []}
    key = "sealed_chunks" if entry.get("sealed") else "files"
    rows = [r for r in current[key] if r["name"] != entry["name"]] + [entry]
    payload = {**current, key: sorted(rows, key=lambda r: r["name"]),
               "harness_sha256": harness_sha,
               "updated": datetime.now(LOCAL_TZ).isoformat(timespec="seconds")}
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    tmp.replace(path)


def _file_entry(chunk: Chunk, target: Path, session_id: str) -> dict[str, Any]:
    inv = inventory(target)  # ts_event, symbols and ids only; no price column is read
    rel = target.resolve().relative_to(REPO_ROOT) if target.resolve().is_relative_to(
        REPO_ROOT) else target
    return {"name": target.name, "path": str(rel).replace(os.sep, "/"),
            "request_start": chunk.params.start, "request_end": chunk.params.end,
            "sha256": inv.sha256, "record_count": inv.record_count,
            "instrument_ids": list(inv.instrument_ids), "first_ts_event_utc":
            inv.first_ts_event_utc, "last_ts_event_utc": inv.last_ts_event_utc,
            "session_id": session_id}


def settled_step2_keys(entries: Iterable[dict[str, Any]], account: str) -> set[str]:
    """Settled request keys on ``account`` under ANY session: step 2 spans several sessions."""
    return {request_key(e["request"]) for e in entries
            if e.get("event") == "settle" and e.get("account") == account and "request" in e}


def _buy(chunk: Chunk, view: Any, client: Any, gate: LockedQuoteGate, target: Path) -> Quote:
    """quote -> authorize -> commit -> download (.partial, link, read-only). Returns the quote."""
    quote = gate.quote(view, chunk.params)
    gate.authorize(chunk.params, quote)  # session, request and account caps; raises
    if quote is None:
        raise BudgetRefusedError("unpriceable chunk passed authorize")  # unreachable
    kind = "holdout-2, sealed on arrival" if chunk.sealing else "kept"
    gate.commit(quote, note=f"{STEP2_NOTE} ({kind})")
    download(client, chunk.params, target)
    return quote


def _check_and_settle(chunk: Chunk, quote: Quote, gate: LockedQuoteGate, target: Path,
                      settled: set[str]) -> bool:
    """Record-byte check (the one decode) and settle. Returns True when delivery exceeded the
    quote (settled pro rata; the caller stops the run after sealing or keeping the file)."""
    try:
        delivered = adapter.delivered_record_bytes(target)
    except Exception as exc:
        raise DeliveryCheckError(f"record-byte check of {target.name} failed "
                                 f"({type(exc).__name__}: {exc}); not settled") from exc
    exceeded = quote.billable_bytes > 0 and delivered > quote.billable_bytes
    actual = quote.usd * delivered / quote.billable_bytes if exceeded else quote.usd
    gate.settle(quote, actual_usd=actual, note=(
        f"{STEP2_NOTE}: delivered uncompressed record bytes {delivered:,} vs quoted billable "
        f"{quote.billable_bytes:,}" + (" — DELIVERED EXCEEDS QUOTE" if exceeded else "")))
    settled.add(chunk.key)
    return exceeded


def _acquire_sealed(chunk: Chunk, view: Any, client: Any, gate: LockedQuoteGate, target: Path,
                    paths: Any, settled: set[str], base: Path, harness: str) -> str:
    root = chunk.root
    if seal.is_sealed(target, paths):
        if target.exists() or target.with_name(target.name + ".partial").exists():
            seal.complete_interrupted_seal(target, paths)
            return "plaintext of an interrupted seal removed on resume"
        return "skipped: sealed as holdout 2, never re-bought"
    expected = seal.next_chunk(paths)
    if expected != (chunk.params.start, chunk.params.end):
        raise ResumeStateError(f"{root} {target.name} is out of order: the next holdout-2 chunk "
                               f"to buy and seal is {expected}")
    if target.exists():  # cut off between the link and the seal: check, seal, never re-buy
        try:
            delivered = adapter.delivered_record_bytes(target)
            record = seal.seal_chunk(root, target, paths, note=(
                "sealed on resume: already downloaded, not re-bought; record-byte check on "
                f"resume: {delivered:,} delivered record bytes"))
        except BaseException:
            _purge(target)
            raise
        _record_sealed(root, target, record, base, harness)
        return "SEALED as holdout 2 on resume (already downloaded, not re-bought)"
    quote = _buy(chunk, view, client, gate, target)
    try:
        exceeded = _check_and_settle(chunk, quote, gate, target, settled)
        record = seal.seal_chunk(root, target, paths, note=f"harness sha256 {harness}")
    except BaseException:
        _purge(target)  # no plaintext holdout byte persists after any failure
        raise
    _record_sealed(root, target, record, base, harness)
    if exceeded:
        raise DeliveryCheckError(f"{root} {target.name}: delivery exceeded the quote; settled "
                                 "pro rata and sealed. Run stopped for the lead.")
    return f"bought for ${quote.usd:.6f} and SEALED as holdout 2"


def _record_sealed(root: str, target: Path, record: dict, base: Path, harness: str) -> None:
    record_file(root, {"name": target.name, "sealed": True, "bytes": record["bytes"],
                       "sha256_sealed": record["sha256_sealed"]}, base, harness)


def _acquire_kept(chunk: Chunk, view: Any, client: Any, gate: LockedQuoteGate, target: Path,
                  settled: set[str], base: Path, harness: str) -> str:
    has_file, has_settle = target.exists(), chunk.key in settled
    if has_file and has_settle:
        _ensure_listed(chunk, target, gate, base, harness)
        return "skipped: already bought and settled"
    if has_file or has_settle:
        raise ResumeStateError(f"{chunk.root} {target.name}: "
                               + ("file without a settled ledger line" if has_file else
                                  "settled ledger line without its file")
                               + ". Nothing deleted; the lead decides.")
    quote = _buy(chunk, view, client, gate, target)
    exceeded = _check_and_settle(chunk, quote, gate, target, settled)
    record_file(chunk.root, _file_entry(chunk, target, gate.session_id), base, harness)
    if exceeded:
        raise DeliveryCheckError(f"{chunk.root} {target.name}: delivery exceeded the quote; "
                                 "settled pro rata, file kept. Run stopped for the lead.")
    return f"bought for ${quote.usd:.6f}"


def _ensure_listed(chunk: Chunk, target: Path, gate: LockedQuoteGate, base: Path,
                   harness: str) -> None:
    path = manifest_path(chunk.root, base)
    listed = json.loads(path.read_text(encoding="utf-8"))["files"] if path.is_file() else []
    if not any(r["name"] == target.name for r in listed):
        record_file(chunk.root, _file_entry(chunk, target, gate.session_id), base, harness)


def run_buy(client: Any, gate: LockedQuoteGate, plan: list[Chunk], *, expected_harness_sha256:
            str, vendor_root: Path = VENDOR_ROOT, seal_paths: Callable[[str], Any] | None = None,
            reports_base: Path = STEP2_REPORTS, log: Callable[[str], None],
            sleep: Callable[[float], None] = time.sleep, account: str | None = None,
            training_window: bool = False) -> tuple[str, list[dict[str, str]]]:
    """The harness preflight first, then the caps (the gate on ``account``, ACTIVE_ACCOUNT when
    None), the training-window interlock and the plan (``training_window``: nothing from
    2024-03-01 on), then every chunk in plan order, serially. Returns (harness sha256, actions).
    The first failure raises and stops the run."""
    harness = harness_freeze.preflight(expected_harness_sha256)
    require_buy_caps(gate, account)
    require_training_window(training_window)
    validate_plan(plan, training_window=training_window)
    seal_paths = seal_paths or (lambda r: seal.step2_holdout_paths(r, vendor_root=vendor_root))
    client.batch = ForbiddenNamespace()  # the buy path needs timeseries.get_range only
    settled = settled_step2_keys(read_entries(gate.ledger_path), gate.account_id)
    view = QuoteOnlyView(client, sleep)
    done = []
    for chunk in plan:
        check_chunk(chunk, training_window=training_window)
        target = target_path(chunk.params, vendor_root)
        if chunk.sealing:
            action = _acquire_sealed(chunk, view, client, gate, target, seal_paths(chunk.root),
                                     settled, reports_base, harness)
        else:
            action = _acquire_kept(chunk, view, client, gate, target, settled, reports_base,
                                   harness)
        done.append({"root": chunk.root, "chunk": target.name, "action": action})
        log(f"{chunk.root} {target.name}: {action} · session ${gate.session_spent_usd():.4f}")
    return harness, done


# ---------------------------------------------------------------- status ----
def status(roots: Sequence[str] = STEP1_ROOTS) -> dict[str, Any]:
    """Every admissible product's holdout-2 store (checksums only; decrypts nothing)."""
    out = {}
    for root in roots:
        paths = seal.step2_holdout_paths(root)
        out[root] = seal.verify(root, paths) if paths.manifest.exists() else {
            "state": "not_bought"}
    return out


# ------------------------------------------------------------------- CLI ----
def log_line(message: str) -> None:
    print(f"[{datetime.now(LOCAL_TZ):%Y-%m-%d %H:%M:%S %Z}] {message}", flush=True)


def build_client(key: str) -> Any:
    import databento  # lazy: the tests never build a real client

    return databento.Historical(key)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m data.pull_step2")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--quote-only", action="store_true", help="price a set (free)")
    mode.add_argument("--buy", action="store_true", help="buy through the gate")
    mode.add_argument("--status", action="store_true", help="per-product holdout-2 seals")
    parser.add_argument("--set", choices=QUOTE_SETS, help="quote set")
    parser.add_argument("--retry-failed", action="store_true")
    which = parser.add_mutually_exclusive_group()
    which.add_argument("--ml-route", action="store_true", help="buy the 31 price-path contracts")
    which.add_argument("--cluster", choices=LEG_CLUSTERS,
                       help="buy one cluster's traded vehicles and its members' legs")
    which.add_argument("--roots", help="R1,R2,...: distinct v2 price paths (--buy, --quote-only)")
    parser.add_argument("--account", choices=tuple(ACCOUNTS),
                        help=f"the Databento account (required with --buy; quotes default to "
                             f"{ACTIVE_ACCOUNT})")
    window = parser.add_mutually_exclusive_group()
    window.add_argument("--training-window", action="store_true",
                        help="chunks through range=2024-02-01_2024-03-01 only")
    window.add_argument("--holdout2-only", action="store_true",
                        help="quote only: the 13 holdout-2 chunks per root (never bought)")
    window.add_argument("--extension-2010", action="store_true",
                        help="quote only: 2010-01..2019-04 per root (never bought; MBT skipped)")
    parser.add_argument("--quotes-out", help="quotes JSON (.json; the .md is written beside it); "
                                             "default reports/stage_e12_quotes.json")
    parser.add_argument("--harness-sha256", help="the frozen harness manifest's sha256 (--buy)")
    return parser


def quote_groups(which: str, vehicles_path: Path = VEHICLES_PATH) -> dict[str, tuple[str, ...]]:
    if which == SET_ML:
        return dict(ML_ROUTE_CONTRACTS)
    if which == SET_ML_V2:
        return dict(ML_V2_CONTRACTS)
    if which == SET_CLUSTERS_LEGS:
        return cluster_roots(vehicles_path)
    return cluster_vehicles(vehicles_path)


def quote_paths(quotes_out: str | None, quotes_json: Path, quotes_md: Path | None = None
                ) -> tuple[Path, Path]:
    """The quotes JSON and .md of a --quote-only run: --quotes-out (the .md beside it), else the
    given paths. E.2b's files are refused, so they are never overwritten."""
    if quotes_out is not None:
        quotes_json, quotes_md = Path(quotes_out), None
    if quotes_json.suffix != ".json":
        raise Step2Error(f"--quotes-out must name a .json file (the .md goes beside it): "
                         f"{quotes_json}")
    md = quotes_json.with_suffix(".md") if quotes_md is None else quotes_md
    if {quotes_json.resolve(), md.resolve()} & {QUOTES_JSON.resolve(), QUOTES_MD.resolve()}:
        raise Step2Error(f"{QUOTES_JSON.name} and {QUOTES_MD.name} are Stage E.2b's quotes and "
                         "are never overwritten: choose another --quotes-out")
    return quotes_json, md


def _window(args: argparse.Namespace) -> str | None:
    if args.training_window:
        return "training-window"
    if args.holdout2_only:
        return PLAN_HOLDOUT2_ONLY
    return PLAN_EXTENSION_2010 if args.extension_2010 else None


def _range_text(window: str | None) -> str:
    if window == "training-window":
        return (f"{STEP2_START}..{TRAINING_WINDOW_END} (end exclusive, 00:00 UTC): the training "
                "window, through range=2024-02-01_2024-03-01; a contract listed later starts at "
                "its first priced month (OC-R)")
    if window == PLAN_HOLDOUT2_ONLY:
        return ("the 13 holdout-2 chunks 2024-03-01..2025-04-01 (end exclusive) per root; "
                "quote only, never bought")
    if window == PLAN_EXTENSION_2010:
        return (f"{EXTENSION_2010_START}..{EXTENSION_2010_END} (end exclusive, 00:00 UTC), 112 "
                "monthly chunks per root; quote only, never bought; MBT skipped by name")
    return (f"{STEP2_START}..{STEP2_END} (end exclusive, 00:00 UTC), 71 monthly chunks; a "
            "contract listed later starts at its first priced month (OC-R)")


def _quote_roots(args: argparse.Namespace, vehicles_path: Path
                 ) -> tuple[list[str], dict[str, tuple[str, ...]], str]:
    """--quote-only's roots, summary groups and section name (the set or the --roots list,
    plus the window option, so one quotes file holds each plan in its own section)."""
    if args.ml_route or args.cluster or args.harness_sha256:
        raise Step2Error("--quote-only takes --set or --roots, with --retry-failed, --account, a "
                         "window option and --quotes-out only")
    if (args.set is None) == (args.roots is None):
        raise Step2Error("--quote-only takes exactly one of --set or --roots")
    if args.set is not None:
        groups = quote_groups(args.set, vehicles_path)
        roots = list(dict.fromkeys(r for rs in groups.values() for r in rs))  # each once
        name = args.set
    else:
        roots = list(parse_roots(args.roots))
        groups = groups_by_cluster(roots)
        name = "roots:" + ",".join(roots)
    window = _window(args)
    return roots, groups, name if window is None else f"{name}+{window}"


def _check_buy_args(args: argparse.Namespace) -> None:
    if args.harness_sha256 is None:
        raise Step2Error("--buy requires --harness-sha256 (the frozen manifest's sha256)")
    if args.set or args.retry_failed:
        raise Step2Error("--buy takes --ml-route, --cluster or --roots, not --set")
    if args.holdout2_only or args.extension_2010:
        raise Step2QuoteOnlyChunk("--holdout2-only and --extension-2010 are quote-only plans: "
                                  "never bought")
    if args.quotes_out is not None:
        raise Step2Error("--quotes-out is for --quote-only")
    if args.account is None:
        raise Step2Error(f"--buy requires --account ({', '.join(ACCOUNTS)}): the gate and the "
                         "key are that account's")
    require_training_window(args.training_window)


def _gate_on(gate_factory: Callable[..., LockedQuoteGate], account: str) -> LockedQuoteGate:
    gate = gate_factory(account=account)
    require_account(gate, account)
    return gate


def main(argv: list[str] | None = None, *,
         key_loader: Callable[..., str] = require_databento_key,
         gate_factory: Callable[..., LockedQuoteGate] = step2_gate,
         client_factory: Callable[[str], Any] = build_client,
         quotes_json: Path = QUOTES_OUT_DEFAULT, quotes_md: Path | None = None,
         vehicles_path: Path = VEHICLES_PATH, vendor_root: Path = VENDOR_ROOT,
         reports_base: Path = STEP2_REPORTS, log: Callable[[str], None] = log_line) -> int:
    """The CLI. ``gate_factory`` and ``key_loader`` are called with ``account=`` (--account, or
    ACTIVE_ACCOUNT for --quote-only); the other keywords are for tests."""
    args = _parser().parse_args(argv)
    if args.status:
        print(json.dumps(status(), indent=1))
        return 0
    account = ACTIVE_ACCOUNT if args.account is None else args.account
    try:
        if args.quote_only:
            roots, groups, name = _quote_roots(args, vehicles_path)
            out_json, out_md = quote_paths(args.quotes_out, quotes_json, quotes_md)
        else:
            _check_buy_args(args)
            roots = list(parse_roots(args.roots) if args.roots is not None else
                         roots_for(args.ml_route, args.cluster, vehicles_path))
        gate = _gate_on(gate_factory, account)
        log(banner(gate))
        window = _window(args)
        skipped: list[str] = []
        if window in (PLAN_HOLDOUT2_ONLY, PLAN_EXTENSION_2010):
            plan, skipped = plan_quote_only(roots, window)
        else:
            plan = plan_step2(roots, training_window=args.training_window)
        log(f"plan: {len(plan)} chunks over {len(roots) - len(skipped)} contracts "
            f"({window or 'full step 2 range'})" + (f"; skipped by name: {', '.join(skipped)}"
                                                     if skipped else ""))
        if args.buy:
            harness = harness_freeze.preflight(args.harness_sha256)
            log(f"harness preflight passed: {harness}")
            require_buy_caps(gate, args.account)
        else:  # both accounts' positions, each from its own gate, before any vendor call
            gates = {a: gate if a == account else _gate_on(gate_factory, a) for a in ACCOUNTS}
            accounts = accounts_summary(gates)
            for p in accounts["positions"].values():
                log(f"{p['account']}: spent ${p['spent_usd']:.6f} · cap "
                    f"${p['account_cap_usd']:.2f} · headroom ${p['cap_headroom_usd']:.6f}")
        key = key_loader(account=account)
    except (Step2Error, harness_freeze.HarnessFreezeError, BudgetRefusedError,
            UnknownAccountError, MissingSecretError, ExternalLedgerUnavailableError,
            OSError, ValueError, KeyError) as exc:
        print(f"REFUSED before any vendor call ({type(exc).__name__}): {exc}", file=sys.stderr)
        return RC_REFUSED
    client = client_factory(key)
    try:
        if args.quote_only:
            return _quote_main(client, gate, plan, groups, args, out_json, out_md,
                               vehicles_path, log, name=name, accounts=accounts, skipped=skipped)
        harness, done = run_buy(client, gate, plan, expected_harness_sha256=args.harness_sha256,
                                vendor_root=vendor_root, reports_base=reports_base, log=log,
                                account=args.account, training_window=args.training_window)
    except (Step2Error, harness_freeze.HarnessFreezeError, BudgetRefusedError,
            UnknownAccountError, ExternalLedgerUnavailableError, ResumeStateError,
            DownloadError, DeliveryCheckError, OSError, ValueError) as exc:
        print(f"RUN STOPPED ({type(exc).__name__}): {exc}. Nothing after this chunk was "
              "requested; see the ledger and docs/ACCESS.md.", file=sys.stderr)
        return RC_STOPPED
    log(f"buy finished: {len(done)} chunks · harness {harness} · {banner(gate)}")
    return 0


def render_quotes_markdown(payload: dict[str, Any]) -> str:
    """data.pull_step2_report's markdown, titled by session, plus every section it does not
    render (ml-v2, --roots, the window options) and both accounts' positions."""
    from data.pull_step2_report import _set_lines, render_markdown

    _, _, body = render_markdown(payload).partition("\n")
    lines = [f"# Step 2 quotes, session {payload.get('session_id')} (free; $0.00 quote lines "
             "only)"]
    for name, section in payload.get("sets", {}).items():
        if name in (SET_ML, SET_CLUSTERS, SET_CLUSTERS_LEGS):
            continue  # rendered by render_markdown
        block = _set_lines(section)
        lines += [*block[:2], f"- Plan: {section.get('plan', '')}", *block[2:]]
    accounts = payload.get("accounts")
    if accounts:
        lines += ["## Account positions (each account's gate)", "",
                  "| Account | Spent | Cap | Headroom |", "|---|---:|---:|---:|"]
        lines += [f"| {p['account']} | ${p['spent_usd']:.6f} | ${p['account_cap_usd']:.2f} | "
                  f"${p['cap_headroom_usd']:.6f} |" for p in accounts["positions"].values()]
        lines += ["", f"Combined headroom: ${accounts['combined_headroom_usd']:.6f}", ""]
    head, extra = lines[0], lines[1:]
    return "\n".join([head, body.rstrip("\n"), "", *extra]).rstrip("\n") + "\n"


def _quote_main(client: Any, gate: LockedQuoteGate, plan: list[Chunk] | list[QuoteOnlyChunk],
                groups: dict[str, tuple[str, ...]], args: argparse.Namespace, quotes_json: Path,
                quotes_md: Path, vehicles_path: Path, log: Callable[[str], None], *, name: str,
                accounts: dict[str, Any], skipped: list[str]) -> int:
    run_quote_only(client, gate, plan, log=log, retry_failed=args.retry_failed,
                   training_window=args.training_window)
    quotes = quotes_from_ledger(plan, read_entries(gate.ledger_path), gate.session_id)
    section = summarize_set(name, groups, quotes, account_position(gate))
    section["vehicles_table_sha256"] = file_sha256(vehicles_path) if args.set in (
        SET_CLUSTERS, SET_CLUSTERS_LEGS) else None
    section["first_priced_month"] = {r: first_priced_month(r) for r in dict.fromkeys(
        r for rs in groups.values() for r in rs) if r in FIRST_PRICED_MONTH}
    section["plan"] = _range_text(_window(args))
    section["skipped_roots"] = {r: EXTENSION_2010_SKIPPED[r] for r in skipped}
    section["generated"] = datetime.now(LOCAL_TZ).isoformat(timespec="seconds")
    extra = {"session_id": gate.session_id, "dataset": DATASET, "schema": OHLCV_1M,
             "range": section["plan"], "account": account_position(gate), "accounts": accounts,
             "session_cap_usd": gate.session_cap_usd, "request_cap_usd": gate.request_cap_usd}
    payload = write_quotes_json(section, extra, quotes_json)
    quotes_md.write_text(render_quotes_markdown(payload), encoding="utf-8")
    log(f"{name}: TOTAL QUOTED ${section['total_usd']:.6f} over {section['contracts']} "
        f"contracts; {section['chunks_failed']} chunk quote(s) failed; wrote {quotes_json.name}")
    return 0 if section["complete"] else RC_STOPPED


if __name__ == "__main__":
    sys.exit(main())
