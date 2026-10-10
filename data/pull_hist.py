"""Stage E.14 (harness v10): the hist purchase plans "es2011" (test C2) and "ext2010" (test C1).

    uv run python -m data.pull_step2 --quote-only --plan es2011 --quotes-out <json>
    uv run python -m data.pull_step2 --quote-only --plan ext2010 --quotes-out <json>
    uv run python -m data.pull_step2 --buy --plan es2011 --account acct-2 --harness-sha256 <sha>
(``python -m data.pull_hist`` takes the same arguments; data.pull_step2 hands --plan runs here.)

Plans (``PLANS``), each a fixed list of monthly ohlcv-1m chunks of ``<ROOT>.v.0`` (GLBX.MDP3,
stype continuous), end exclusive at 00:00 UTC, every chunk ending on or before 2019-05-01, where
the program's step 2 data starts:
- "es2011" (C2, reports/stage_e13_prereg_gexmom.md section 2): ES, the 96 chunks
  2011-05-01..2019-05-01; its store holds trade dates 2011-05-02..2019-04-30.
- "ext2010" (C1, reports/stage_e13_prereg_ngrepl.md section 2, rulings C5 and C6): NG, NQ, ZN, 6E,
  GC and ZC, each the partial chunk 2010-06-06..2010-07-01 (GLBX.MDP3 starts 2010-06-06) then the
  106 chunks 2010-07..2019-04, 107 per root; its store holds trade dates 2010-06-07..2019-04-30.
Any chunk, root or request outside its plan is refused (``check_hist_chunk``) before any vendor
call. A ``HistChunk`` is its own type: the step 2 path (data.pull_step2.check_chunk) refuses it,
and these checks refuse a step 2 Chunk or a QuoteOnlyChunk.

--quote-only: free metadata calls only (the billable namespaces are guarded), $0.00 quote lines
under STAGE_E14_SESSION_ID on --account (default acct-2), and a quotes JSON (--quotes-out,
required; E.2b's files are refused) with the plan's total, per-root rows, the total x 1.03 and
the account's headroom. --retry-failed re-quotes only the chunks with no successful quote line.

--buy (es2011 under STAGE_E14_SESSION_ID with E14_SESSION_CAP_USD; ext2010 under
STAGE_E14_EXT2010_SESSION_ID with E14_EXT2010_SESSION_CAP_USD; both E14_REQUEST_CAP_USD), in
order, nothing requested before every check passes:
1. the harness preflight (--harness-sha256);
2. the account is E14_BUY_ACCOUNT (acct-2) and the gate sits on it with the plan's session id;
3. both caps positive (a 0.00 cap refuses the buy: ext2010 stays refused in E.14, V26);
4. the plan's test is registered in ledger/trial_registrations.jsonl (C2-T1 and C2-T2, or C1-T1
   and C1-T2: screening.trial_registry);
5. what is left of the session cap fits the account's headroom;
6. every chunk passes ``check_hist_chunk``; every raw target is either absent or settled, and a
   settled chunk's file exists (else ResumeStateError, nothing deleted).
Then per chunk, serially: quote -> authorize (session, request and account caps) -> commit ->
download to .partial -> os.link -> read-only -> record-byte check -> settle -> the plan's purchase
manifest reports/hist/purchase_<ROOT>_<plan>.json (never reports/step2/: NG's step 2 manifest is
never touched). Billed above quote: actual = quote x delivered / quoted billable bytes; above the
quote by more than 3% (``BILLED_OVER_QUOTE_STOP``) the chunk is settled, recorded and the run
stops before the next chunk; at most 3% it is settled pro rata, recorded and the run continues
(the session cap, quote x 1.03, still bounds the total). After the last chunk the buy run fetches
the free metadata the store needs, each written once and never overwritten: symbology.resolve of
<ROOT>.v.0 over the plan's data window (VENDOR_ROOT/rolls/<ROOT>_v_0_<start>_<end>_symbology.json)
and the dataset condition list (VENDOR_ROOT/condition/GLBX.MDP3_<start>_<end>.json).

Harness v12 (Stage E.17, reports/stage_e16_handoff.md step 8, E.17 amendment A4) adds plan
"ext2010h" (the base-rule batch, test label E16, ids E16-H1..E16-H5); es2011 and ext2010 are
unchanged. Run it with ``python -m data.pull_hist`` (data.pull_step2's --plan choices stay the
v10 two):
    uv run python -m data.pull_hist --quote-only --plan ext2010h --quotes-out <json>
    uv run python -m data.pull_hist --buy --plan ext2010h --account acct-2 --harness-sha256 <sha>
        [--roots ROOT [ROOT ...]]
- Its 21 roots, in reports/stage_e16_windows.json's purchase_21_roots order, each with its OWN
  chunk list (``HistPlan.root_chunks``): the monthly chunks of <ROOT>.v.0 from its U2 start month
  through 2019-04 (end exclusive 2019-05-01): 18 roots from 2010-07 (106 each), TN from 2016-01
  (40), RTY from 2017-06 (23), HE from 2017-07 (22); 1,993 in all. ``check_hist_chunk`` refuses
  any chunk outside its own root's list. Store trade dates 2010-07-01..2019-04-30 (2010-07-01 is
  the first trade date on or after the U2 default start; base_rules.hist_plan.check_name accepts
  it for every root), data window [2010-07-01, 2019-05-01) UTC.
- Quote AND buy run under STAGE_E17_EXT2010H_SESSION_ID (its quote lines are separable from
  E.14's), the buy with E17_EXT2010H_SESSION_CAP_USD (0.00 refuses it) and E14_REQUEST_CAP_USD.
- --roots (A4) restricts the quote or the buy of ext2010h to the named roots (each a plan root,
  distinct, at least one; chunks in the order given); refused for es2011 and ext2010 before any
  vendor call. Every other step of the buy is the one above.
"""

from __future__ import annotations

import argparse
import json
import os
import stat
import sys
import time
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

from data import adapter
from data.adapter import OHLCV_1M, STYPE_CONTINUOUS
from data.config import (
    ACCOUNTS,
    DATASET,
    E14_BUY_ACCOUNT,
    E14_EXT2010_SESSION_CAP_USD,
    E14_REQUEST_CAP_USD,
    E14_SESSION_CAP_USD,
    E17_EXT2010H_SESSION_CAP_USD,
    REPO_ROOT,
    STAGE_E14_EXT2010_SESSION_ID,
    STAGE_E14_SESSION_ID,
    STAGE_E17_EXT2010H_SESSION_ID,
    VENDOR_ROOT,
    MissingSecretError,
    require_databento_key,
)
from data.pull_mes import monthly_chunks
from data.pull_universe import (
    DeliveryCheckError,
    DownloadError,
    ResumeStateError,
    download,
    files_overlapping,
    inventory,
    target_path,
)
from data.quote_universe import (
    LOCAL_TZ,
    MAX_WORKERS,
    ForbiddenNamespace,
    LockedQuoteGate,
    QuoteOnlyView,
    install_forbidden_guards,
    request_key,
)
from data.spend_gate import (
    BudgetRefusedError,
    ExternalLedgerUnavailableError,
    Quote,
    RequestParams,
    UnknownAccountError,
    read_entries,
    resolve_account,
)
from screening import harness_freeze, trial_registry

PLAN_ES2011, PLAN_EXT2010 = "es2011", "ext2010"
HIST_PLAN_NAMES = (PLAN_ES2011, PLAN_EXT2010)
# The program's earliest read data (step 2 starts here): no hist chunk reaches past it.
STEP2_DATA_START = "2019-05-01"
HIST_REPORTS = REPO_ROOT / "reports" / "hist"
ROLLS_DIR = VENDOR_ROOT / "rolls"
CONDITION_DIR = VENDOR_ROOT / "condition"
HIST_NOTE = "Stage E.14 hist purchase"
BILLED_OVER_QUOTE_STOP = 0.03  # the E.14 prompt's Guardrails: above its quote by more than 3%
RC_REFUSED = 2
RC_STOPPED = 1


class HistPlanError(RuntimeError):
    """A hist plan run stopped at a named problem. Nothing after it was requested."""


@dataclass(frozen=True)
class HistPlan:
    name: str
    test: str  # the trial registry's test label
    test_ids: tuple[str, ...]
    roots: tuple[str, ...]
    chunks: tuple[tuple[str, str], ...]  # every root's chunks, oldest first
    first_trade_date: date  # the store's trade dates (both inclusive)
    last_trade_date: date
    data_start: date  # the chunks' UTC span [data_start, data_end)
    data_end: date
    # Harness v12: per-root chunk lists, (root, its chunks oldest first) in root order; ``chunks``
    # is then their union. Empty (es2011, ext2010): every root holds ``chunks``.
    root_chunks: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = ()

    def chunks_of(self, root: str) -> tuple[tuple[str, str], ...]:
        """``root``'s chunks: its own list in a per-root plan, else ``chunks``."""
        if not self.root_chunks:
            return self.chunks
        for name, chunks in self.root_chunks:
            if name == root:
                return chunks
        raise HistPlanError(f"{root!r} is not a root of plan {self.name} "
                            f"({', '.join(self.roots)})")


ES2011 = HistPlan(
    PLAN_ES2011, "C2", ("C2-T1", "C2-T2"), ("ES",),
    tuple(monthly_chunks(date(2011, 5, 1), date(2019, 5, 1))),
    date(2011, 5, 2), date(2019, 4, 30), date(2011, 5, 1), date(2019, 5, 1))
EXT2010 = HistPlan(
    PLAN_EXT2010, "C1", ("C1-T1", "C1-T2"), ("NG", "NQ", "ZN", "6E", "GC", "ZC"),
    (("2010-06-06", "2010-07-01"), *monthly_chunks(date(2010, 7, 1), date(2019, 5, 1))),
    date(2010, 6, 7), date(2019, 4, 30), date(2010, 6, 6), date(2019, 5, 1))
PLANS: dict[str, HistPlan] = {p.name: p for p in (ES2011, EXT2010)}
if len(ES2011.chunks) != 96 or len(EXT2010.chunks) != 107 or any(
        p.chunks[0][0] != str(p.data_start) or p.chunks[-1][1] != STEP2_DATA_START
        or str(p.data_end) != STEP2_DATA_START
        or any(a[1] != b[0] for a, b in zip(p.chunks, p.chunks[1:], strict=False))
        for p in PLANS.values()):
    raise RuntimeError("hist plans: es2011 is the 96 chunks 2011-05..2019-04, ext2010 the 107 "
                       "chunks 2010-06-06..2019-05-01, contiguous, ending where step 2 starts")

# Harness v12 (Stage E.17): plan "ext2010h", the base-rule batch's 21 roots (module docstring).
# Each root's U2 start month (reports/stage_e16_windows.json products.<ROOT>.start_month), in the
# windows file's purchase_21_roots order; its chunks run monthly from there to 2019-05-01.
PLAN_EXT2010H = "ext2010h"
EXT2010H_START_MONTHS = (
    ("6A", "2010-07"), ("6B", "2010-07"), ("6C", "2010-07"), ("6J", "2010-07"),
    ("6N", "2010-07"), ("6S", "2010-07"), ("CL", "2010-07"), ("HE", "2017-07"),
    ("HG", "2010-07"), ("LE", "2010-07"), ("RTY", "2017-06"), ("TN", "2016-01"),
    ("UB", "2010-07"), ("YM", "2010-07"), ("ZB", "2010-07"), ("ZF", "2010-07"),
    ("ZL", "2010-07"), ("ZM", "2010-07"), ("ZS", "2010-07"), ("ZT", "2010-07"),
    ("ZW", "2010-07"))


def _monthly_to_step2(month: str) -> tuple[tuple[str, str], ...]:
    return tuple(monthly_chunks(date.fromisoformat(f"{month}-01"),
                                date.fromisoformat(STEP2_DATA_START)))


EXT2010H = HistPlan(
    PLAN_EXT2010H, "E16", ("E16-H1", "E16-H2", "E16-H3", "E16-H4", "E16-H5"),
    tuple(root for root, _ in EXT2010H_START_MONTHS),
    tuple(monthly_chunks(date(2010, 7, 1), date(2019, 5, 1))),
    date(2010, 7, 1), date(2019, 4, 30), date(2010, 7, 1), date(2019, 5, 1),
    root_chunks=tuple((root, _monthly_to_step2(month)) for root, month in EXT2010H_START_MONTHS))
_EXT2010H_COUNTS = {root: len(chunks) for root, chunks in EXT2010H.root_chunks}
if (len(EXT2010H.roots) != 21 or sum(_EXT2010H_COUNTS.values()) != 1993
        or len(EXT2010H.chunks) != 106
        or {r: n for r, n in _EXT2010H_COUNTS.items() if n != 106} != {"HE": 22, "RTY": 23,
                                                                       "TN": 40}
        or EXT2010H.chunks[0][0] != str(EXT2010H.data_start)
        or str(EXT2010H.data_end) != STEP2_DATA_START
        or any(a[1] != b[0] for a, b in zip(EXT2010H.chunks, EXT2010H.chunks[1:], strict=False))
        or any(c[-1][1] != STEP2_DATA_START or not set(c) <= set(EXT2010H.chunks)
               or any(a[1] != b[0] for a, b in zip(c, c[1:], strict=False))
               for _, c in EXT2010H.root_chunks)):
    raise RuntimeError("hist plan ext2010h: 21 roots, 1,993 chunks (18 x 106 from 2010-07, TN 40, "
                       "RTY 23, HE 22), each root's list contiguous and ending where step 2 "
                       "starts")
PLANS = {**PLANS, PLAN_EXT2010H: EXT2010H}
HIST_PLAN_NAMES = (*HIST_PLAN_NAMES, PLAN_EXT2010H)
# A4 (E.17): the plans whose quote or buy --roots may restrict to some of their roots.
ROOTS_OPTION_PLANS = (PLAN_EXT2010H,)


# ------------------------------------------------------------------ plan ----
@dataclass(frozen=True, slots=True)
class HistChunk:
    plan: str
    root: str
    params: RequestParams

    @property
    def key(self) -> str:
        return request_key(self.params.as_kwargs())


def get_plan(name: str) -> HistPlan:
    if name not in PLANS:
        raise HistPlanError(f"unknown hist plan {name!r} (plans {list(HIST_PLAN_NAMES)})")
    return PLANS[name]


def _params(root: str, start: str, end: str) -> RequestParams:
    return RequestParams(DATASET, (f"{root}.v.0",), OHLCV_1M, STYPE_CONTINUOUS, start, end)


def check_hist_chunk(item: Any, plan: HistPlan) -> None:
    """Everything a hist chunk must satisfy before any vendor call. Raises, never warns."""
    if type(item) is not HistChunk:
        raise HistPlanError(f"{type(item).__name__}: only a HistChunk of plan {plan.name} is "
                            "quoted or bought here")
    if item.plan != plan.name:
        raise HistPlanError(f"{item.root}: a chunk of plan {item.plan!r}, not {plan.name!r}")
    if item.root not in plan.roots:
        raise HistPlanError(f"{item.root!r} is not a root of plan {plan.name} "
                            f"({', '.join(plan.roots)})")
    p = item.params
    if p.symbols != (f"{item.root}.v.0",) or (p.dataset, p.schema, p.stype_in) != (
            DATASET, OHLCV_1M, STYPE_CONTINUOUS):
        raise HistPlanError(f"not a {plan.name} request for {item.root}: {p.as_kwargs()}")
    own = plan.chunks_of(item.root)  # v12: the root's own list in a per-root plan
    if (p.start, p.end) not in own:
        what = f"{item.root} chunks" if plan.root_chunks else "chunks"
        raise HistPlanError(f"{item.root} {p.start}..{p.end} is not one of plan {plan.name}'s "
                            f"{len(own)} {what} {own[0][0]}..{own[-1][1]}")
    if p.end > STEP2_DATA_START:
        raise HistPlanError(f"{item.root} {p.start}..{p.end} reaches past {STEP2_DATA_START}")


def plan_chunks(plan: HistPlan, roots: Sequence[str] | None = None) -> list[HistChunk]:
    """The plan's chunks, roots in plan order (or ``roots``, each a plan root), oldest first
    (per root: the root's own chunk list, ``HistPlan.chunks_of``)."""
    chosen = plan.roots if roots is None else tuple(roots)
    if not chosen or len(set(chosen)) != len(chosen):
        raise HistPlanError(f"roots must be distinct and non-empty: {list(chosen)}")
    items = [HistChunk(plan.name, r, _params(r, s, e)) for r in chosen
             for s, e in plan.chunks_of(r)]
    for item in items:
        check_hist_chunk(item, plan)
    return items


def select_roots(plan: HistPlan, roots: Sequence[str] | None) -> tuple[str, ...] | None:
    """A4 (E.17): --roots restricts a quote or buy of a ROOTS_OPTION_PLANS plan to some of its
    roots, each a plan root, distinct, at least one. None means the whole plan. Refused for every
    other plan (es2011 and ext2010 are quoted and bought whole, as in v10)."""
    if roots is None:
        return None
    if plan.name not in ROOTS_OPTION_PLANS:
        raise HistPlanError(f"--roots is for plan {', '.join(ROOTS_OPTION_PLANS)} only; plan "
                            f"{plan.name} is quoted and bought whole")
    chosen = tuple(roots)
    if not chosen:
        raise HistPlanError("--roots needs at least one root")
    repeated = sorted({r for r in chosen if chosen.count(r) > 1})
    if repeated:
        raise HistPlanError(f"--roots names {repeated} more than once")
    unknown = [r for r in chosen if r not in plan.roots]
    if unknown:
        raise HistPlanError(f"--roots {unknown}: not root(s) of plan {plan.name} "
                            f"({', '.join(plan.roots)})")
    return chosen


# ------------------------------------------------------------------ paths ----
def purchase_manifest_path(root: str, plan: str, base: Path = HIST_REPORTS) -> Path:
    return Path(base) / f"purchase_{root}_{plan}.json"


def _span(plan: HistPlan) -> str:
    return f"{plan.data_start}_{plan.data_end}"


def symbology_cache_path(root: str, plan: HistPlan, rolls_dir: Path = ROLLS_DIR) -> Path:
    return Path(rolls_dir) / f"{root}_v_0_{_span(plan)}_symbology.json"


def rolls_cache_path(root: str, plan: HistPlan, rolls_dir: Path = ROLLS_DIR) -> Path:
    return Path(rolls_dir) / f"{root}_v_0_{_span(plan)}.jsonl"


def condition_path(plan: HistPlan, condition_dir: Path = CONDITION_DIR) -> Path:
    return Path(condition_dir) / f"{DATASET}_{_span(plan)}.json"


# ------------------------------------------------------------------ gates ----
def quote_gate(account: str = E14_BUY_ACCOUNT, **overrides: Any) -> LockedQuoteGate:
    """Quotes of either plan: STAGE_E14_SESSION_ID on ``account`` (the caps do not matter for a
    quote). ``overrides`` are for tests (tmp ledgers). (v12: ext2010h quotes through
    ``plan_quote_gate``.)"""
    kwargs = {"session_cap_usd": E14_SESSION_CAP_USD, "request_cap_usd": E14_REQUEST_CAP_USD,
              "account": account, **overrides}
    return LockedQuoteGate(STAGE_E14_SESSION_ID, **kwargs)


def quote_session_id(plan: str) -> str:
    """The session a plan's $0.00 quote lines go under: E.14's for es2011 and ext2010 (v10),
    STAGE_E17_EXT2010H_SESSION_ID for ext2010h (v12)."""
    if plan in (PLAN_ES2011, PLAN_EXT2010):
        return STAGE_E14_SESSION_ID
    if plan == PLAN_EXT2010H:
        return STAGE_E17_EXT2010H_SESSION_ID
    raise HistPlanError(f"unknown hist plan {plan!r}")


def plan_quote_gate(plan: str, account: str = E14_BUY_ACCOUNT, **overrides: Any
                    ) -> LockedQuoteGate:
    """Quotes of ``plan`` under its quote session (``quote_session_id``); ``quote_gate`` is the
    v10 gate of es2011 and ext2010. ``overrides`` are for tests (tmp ledgers)."""
    kwargs = {"session_cap_usd": E14_SESSION_CAP_USD, "request_cap_usd": E14_REQUEST_CAP_USD,
              "account": account, **overrides}
    return LockedQuoteGate(quote_session_id(plan), **kwargs)


def buy_policy(plan: str) -> tuple[str, float, float]:
    """(session id, session cap, request cap) of a plan's buy, read at call time."""
    if plan == PLAN_ES2011:
        return STAGE_E14_SESSION_ID, E14_SESSION_CAP_USD, E14_REQUEST_CAP_USD
    if plan == PLAN_EXT2010:
        return STAGE_E14_EXT2010_SESSION_ID, E14_EXT2010_SESSION_CAP_USD, E14_REQUEST_CAP_USD
    if plan == PLAN_EXT2010H:  # v12: its own session for the quote and the buy
        return STAGE_E17_EXT2010H_SESSION_ID, E17_EXT2010H_SESSION_CAP_USD, E14_REQUEST_CAP_USD
    raise HistPlanError(f"unknown hist plan {plan!r}")


def buy_gate(plan: str, account: str = E14_BUY_ACCOUNT, **overrides: Any) -> LockedQuoteGate:
    session_id, session_cap, request_cap = buy_policy(plan)
    kwargs = {"session_cap_usd": session_cap, "request_cap_usd": request_cap,
              "account": account, **overrides}
    return LockedQuoteGate(session_id, **kwargs)


def banner(gate: LockedQuoteGate) -> str:
    """Session, account and caps. Never the key."""
    return (f"{gate.session_id}: account {gate.account_id} (cap ${gate.account_cap_usd:.2f}, "
            f"spent ${gate.account_spent_usd():.6f}) · session cap ${gate.session_cap_usd:.2f} "
            f"(spent ${gate.session_spent_usd():.6f}) · request cap ${gate.request_cap_usd:.2f}")


def account_position(gate: LockedQuoteGate) -> dict[str, Any]:
    spent = gate.account_spent_usd()
    return {"account": gate.account_id, "account_cap_usd": gate.account_cap_usd,
            "spent_usd": round(spent, 6), "headroom_usd": round(gate.account_cap_usd - spent, 6)}


def require_buy_ready(gate: LockedQuoteGate, plan: HistPlan, account: str, *,
                      registry_path: Path) -> None:
    """Checks 2 to 5 of the buy (module docstring). Raises before any vendor call."""
    resolve_account(account)
    if account != E14_BUY_ACCOUNT or gate.account_id != account:
        raise UnknownAccountError(f"plan {plan.name} buys on {E14_BUY_ACCOUNT} only (asked "
                                  f"{account}, gate on {gate.account_id})")
    session_id, _, _ = buy_policy(plan.name)
    if gate.session_id != session_id:
        raise HistPlanError(f"plan {plan.name} buys under {session_id}, not {gate.session_id}")
    if not (gate.session_cap_usd > 0.0 and gate.request_cap_usd > 0.0):
        raise HistPlanError(f"{plan.name} buy refused: session cap ${gate.session_cap_usd:.2f}, "
                            f"request cap ${gate.request_cap_usd:.2f} ({gate.session_id}); the "
                            "lead sets the cap in data/config.py before the manifest")
    trial_registry.require_registered(plan.test_ids, test=plan.test, path=registry_path)
    left = gate.session_cap_usd - gate.session_spent_usd()
    headroom = gate.account_cap_usd - gate.account_spent_usd()
    if round(left - headroom, 9) > 0:
        raise HistPlanError(f"{plan.name} buy refused: ${left:.6f} left under the session cap "
                            f"exceeds {gate.account_id}'s headroom ${headroom:.6f}")


# ------------------------------------------------------------ quote-only ----
@dataclass(frozen=True, slots=True)
class HistQuote:
    chunk: HistChunk
    usd: float | None
    billable_bytes: int | None


def run_hist_quotes(client: Any, gate: LockedQuoteGate, plan: HistPlan, items: list[HistChunk],
                    *, log: Callable[[str], None], retry_failed: bool = False,
                    workers: int = MAX_WORKERS, sleep: Callable[[float], None] = time.sleep
                    ) -> None:
    """Quote the plan (free). Billable namespaces are guarded first; only ``gate.quote`` runs."""
    for item in items:
        check_hist_chunk(item, plan)
    install_forbidden_guards(client)
    todo = items
    if retry_failed:
        done = _quoted_keys(read_entries(gate.ledger_path), gate.session_id)
        todo = [c for c in items if c.key not in done]
    view = QuoteOnlyView(client, sleep)
    with ThreadPoolExecutor(max_workers=max(1, min(workers, MAX_WORKERS))) as pool:
        futures = [pool.submit(gate.quote, view, c.params) for c in todo]
        try:
            got = [f.result() for f in futures]
        except BaseException:
            pool.shutdown(wait=True, cancel_futures=True)
            raise
    log(f"{plan.name}: quoted {len(todo)} of {len(items)} chunks; "
        f"{sum(q is None for q in got)} failed")


def _quoted_keys(entries: list[dict[str, Any]], session_id: str) -> set[str]:
    return {request_key(e["request"]) for e in entries
            if e.get("session_id") == session_id and e.get("event") == "quote"
            and e.get("quoted_usd") is not None and "request" in e}


def quotes_from_ledger(items: list[HistChunk], entries: list[dict[str, Any]],
                       session_id: str) -> list[HistQuote]:
    """The latest successful quote of each chunk under ``session_id``, else a failure."""
    latest = {request_key(e["request"]): e for e in entries
              if e.get("session_id") == session_id and e.get("event") == "quote"
              and e.get("quoted_usd") is not None and "request" in e}
    return [HistQuote(c, None, None) if c.key not in latest else
            HistQuote(c, float(latest[c.key]["quoted_usd"]),
                      int(latest[c.key]["billable_bytes"])) for c in items]


def summarize_quotes(plan: HistPlan, quotes: list[HistQuote], position: dict[str, Any],
                     roots: Sequence[str] | None = None) -> dict[str, Any]:
    """Per root and plan totals (costs, bytes, counts; no price data), with the 3% margin.
    ``roots``: the --roots selection (v12, ext2010h), recorded as the section's roots."""
    per_root: dict[str, dict[str, Any]] = {}
    for q in quotes:
        row = per_root.setdefault(q.chunk.root, {"usd": 0.0, "billable_bytes": 0, "chunks": 0,
                                                 "quoted": 0, "failed": [],
                                                 "largest_chunk_usd": 0.0})
        row["chunks"] += 1
        if q.usd is None:
            row["failed"].append(f"{q.chunk.params.start}..{q.chunk.params.end}")
            continue
        row["quoted"] += 1
        row["usd"] += q.usd
        row["billable_bytes"] += q.billable_bytes or 0
        row["largest_chunk_usd"] = max(row["largest_chunk_usd"], q.usd)
    total = sum(r["usd"] for r in per_root.values())
    failed = sum(len(r["failed"]) for r in per_root.values())
    margin = total * (1.0 + BILLED_OVER_QUOTE_STOP)
    return {"set": f"plan:{plan.name}", "plan": plan.name, "test": plan.test,
            "roots": list(plan.roots if roots is None else roots), "chunks": len(quotes),
            "chunks_failed": failed,
            "complete": failed == 0, "chunk_range": [plan.chunks[0][0], plan.chunks[-1][1]],
            "store_trade_dates": [str(plan.first_trade_date), str(plan.last_trade_date)],
            "total_usd": total, "total_usd_x_1_03": margin, "account": position,
            "fits_headroom_with_3pct": margin <= position["headroom_usd"],
            "shortfall_usd_with_3pct": max(0.0, margin - position["headroom_usd"]),
            "per_root": per_root,
            "generated": datetime.now(LOCAL_TZ).isoformat(timespec="seconds")}


def render_quotes_markdown(payload: dict[str, Any]) -> str:
    lines = [f"# Hist quotes, session {payload.get('session_id')} (free; $0.00 quote lines only)",
             ""]
    for section in payload.get("sets", {}).values():
        pos = section["account"]
        lines += [f"## Plan {section['plan']} (test {section['test']})", "",
                  f"- Chunks {section['chunk_range'][0]}..{section['chunk_range'][1]} (end "
                  f"exclusive, 00:00 UTC); store trade dates {section['store_trade_dates'][0]}.."
                  f"{section['store_trade_dates'][1]}",
                  f"- Total ${section['total_usd']:.6f}; x 1.03 = "
                  f"${section['total_usd_x_1_03']:.6f}; {section['chunks_failed']} of "
                  f"{section['chunks']} chunk quotes failed",
                  f"- {pos['account']}: spent ${pos['spent_usd']:.6f}, cap "
                  f"${pos['account_cap_usd']:.2f}, headroom ${pos['headroom_usd']:.6f}; fits with "
                  f"3%: {section['fits_headroom_with_3pct']} (shortfall "
                  f"${section['shortfall_usd_with_3pct']:.6f})", "",
                  "| Root | Quoted $ | Chunks | Failed | Billable bytes |",
                  "|---|---:|---:|---:|---:|"]
        lines += [f"| {r} | {row['usd']:.6f} | {row['chunks']} | {len(row['failed'])} | "
                  f"{row['billable_bytes']:,} |" for r, row in section["per_root"].items()]
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def write_quotes(section: dict[str, Any], extra: dict[str, Any], path: Path) -> dict[str, Any]:
    """Update the plan's section (and the shared header) of the quotes JSON, atomically, and
    write the markdown beside it."""
    current = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {"sets": {}}
    payload = {**current, **extra, "sets": {**current.get("sets", {}), section["set"]: section}}
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    tmp.replace(path)
    path.with_suffix(".md").write_text(render_quotes_markdown(payload), encoding="utf-8")
    return payload


# ------------------------------------------------------------------ buy ----
def record_file(root: str, plan: HistPlan, entry: dict[str, Any], base: Path, harness: str
                ) -> None:
    """Add (or replace by name) one chunk's entry in the plan's purchase manifest."""
    path = purchase_manifest_path(root, plan.name, base)
    current = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {
        "product": root, "plan": plan.name, "test": plan.test, "continuous": f"{root}.v.0",
        "schema": OHLCV_1M, "dataset": DATASET, "files": []}
    rows = [r for r in current["files"] if r["name"] != entry["name"]] + [entry]
    payload = {**current, "files": sorted(rows, key=lambda r: r["request_start"]),
               "harness_sha256": harness,
               "updated": datetime.now(LOCAL_TZ).isoformat(timespec="seconds")}
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    tmp.replace(path)


def _check_manifest(root: str, plan: HistPlan, base: Path) -> list[str]:
    path = purchase_manifest_path(root, plan.name, base)
    if not path.is_file():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("product") != root or payload.get("plan") != plan.name:
        raise HistPlanError(f"{path.name} is {payload.get('product')!r} plan "
                            f"{payload.get('plan')!r}, not {root} {plan.name}")
    return [r["name"] for r in payload.get("files", [])]


def _file_entry(item: HistChunk, target: Path, session_id: str, billing: dict[str, Any]
                ) -> dict[str, Any]:
    inv = inventory(target)  # ts_event, symbols and ids only; no price column is read
    rel = target.resolve().relative_to(REPO_ROOT) if target.resolve().is_relative_to(
        REPO_ROOT) else target
    return {"name": target.name, "path": str(rel).replace(os.sep, "/"),
            "request_start": item.params.start, "request_end": item.params.end,
            "sha256": inv.sha256, "record_count": inv.record_count,
            "instrument_ids": list(inv.instrument_ids),
            "first_ts_event_utc": inv.first_ts_event_utc,
            "last_ts_event_utc": inv.last_ts_event_utc, "session_id": session_id, **billing}


def preflight_targets(items: list[HistChunk], settled: set[str], vendor_root: Path) -> None:
    """Before any vendor call: every target is absent and unsettled, or present and settled,
    and no other raw file of the root overlaps its range (no collision with any owned file)."""
    for item in items:
        target = target_path(item.params, vendor_root)
        others = [p.name for p, _, _ in files_overlapping(target.parent, item.params.start,
                                                          item.params.end) if p != target]
        if others:
            raise ResumeStateError(f"{item.root} {target.name} overlaps existing raw file(s) "
                                   f"{others[:3]}. Nothing deleted; the lead decides.")
        has_file, has_settle = target.exists(), item.key in settled
        if has_file != has_settle:
            raise ResumeStateError(
                f"{item.root} {target.name}: " + ("a file without a settled ledger line (a "
                                                  "foreign or unfinished file)" if has_file else
                                                  "a settled ledger line without its file")
                + ". Nothing deleted; the lead decides.")


def _settle(item: HistChunk, quote: Quote, gate: LockedQuoteGate, target: Path
            ) -> dict[str, Any]:
    """Record-byte check (the one decode) and settle. Returns the billing record."""
    try:
        delivered = adapter.delivered_record_bytes(target)
    except Exception as exc:
        raise DeliveryCheckError(f"record-byte check of {target.name} failed "
                                 f"({type(exc).__name__}: {exc}); not settled") from exc
    if quote.billable_bytes > 0:
        ratio = delivered / quote.billable_bytes
    else:
        ratio = float("inf") if delivered > 0 else 1.0
    over = ratio > 1.0
    actual = quote.usd * ratio if over and quote.billable_bytes > 0 else quote.usd
    gate.settle(quote, actual_usd=actual, note=(
        f"{HIST_NOTE} ({item.plan}): delivered uncompressed record bytes {delivered:,} vs "
        f"quoted billable {quote.billable_bytes:,}" + (" — DELIVERED EXCEEDS QUOTE" if over
                                                         else "")))
    return {"quoted_usd": quote.usd, "settled_usd": actual,
            "quoted_billable_bytes": quote.billable_bytes, "delivered_record_bytes": delivered,
            "billed_over_quote_ratio": None if ratio == float("inf") else ratio,
            "billed_above_quote": over}


def _acquire(item: HistChunk, plan: HistPlan, view: Any, client: Any, gate: LockedQuoteGate,
             target: Path, settled: set[str], listed: list[str], base: Path, harness: str
             ) -> str:
    if target.exists() and item.key in settled:
        if target.name not in listed:
            record_file(item.root, plan, _file_entry(item, target, gate.session_id, {}), base,
                        harness)
        return "skipped: already bought and settled"
    quote = gate.quote(view, item.params)
    gate.authorize(item.params, quote)  # session, request and account caps; raises
    if quote is None:
        raise BudgetRefusedError("unpriceable chunk passed authorize")  # unreachable
    gate.commit(quote, note=f"{HIST_NOTE} ({plan.name}, test {plan.test})")
    download(client, item.params, target)
    billing = _settle(item, quote, gate, target)
    settled.add(item.key)
    record_file(item.root, plan, _file_entry(item, target, gate.session_id, billing), base,
                harness)
    ratio = billing["billed_over_quote_ratio"]
    if ratio is None or ratio > 1.0 + BILLED_OVER_QUOTE_STOP:
        raise DeliveryCheckError(
            f"{item.root} {target.name}: BILLED ABOVE ITS QUOTE BY MORE THAN 3% (delivered "
            f"{billing['delivered_record_bytes']:,} vs quoted {quote.billable_bytes:,} bytes); "
            "settled pro rata and recorded. Run stopped before the next chunk.")
    extra = f" (billed {100 * (ratio - 1):.3f}% above the quote)" if ratio > 1.0 else ""
    return f"bought for ${billing['settled_usd']:.6f}{extra}"


def run_hist_buy(client: Any, gate: LockedQuoteGate, plan: HistPlan, items: list[HistChunk], *,
                 expected_harness_sha256: str, account: str, registry_path: Path,
                 vendor_root: Path = VENDOR_ROOT, reports_base: Path = HIST_REPORTS,
                 rolls_dir: Path = ROLLS_DIR, condition_dir: Path = CONDITION_DIR,
                 log: Callable[[str], None], sleep: Callable[[float], None] = time.sleep
                 ) -> tuple[str, list[dict[str, str]]]:
    """The preflight first, then checks 2 to 6, then every chunk in plan order, serially, then
    the free metadata. Returns (harness sha256, actions). The first failure raises."""
    harness = harness_freeze.preflight(expected_harness_sha256)
    require_buy_ready(gate, plan, account, registry_path=registry_path)
    for item in items:
        check_hist_chunk(item, plan)
    listed = {r: _check_manifest(r, plan, reports_base) for r in dict.fromkeys(
        i.root for i in items)}
    settled = _settled_keys(read_entries(gate.ledger_path), gate.account_id)
    preflight_targets(items, settled, vendor_root)
    client.batch = ForbiddenNamespace()  # the buy path needs timeseries.get_range only
    view = QuoteOnlyView(client, sleep)
    done = []
    for item in items:
        check_hist_chunk(item, plan)
        target = target_path(item.params, vendor_root)
        action = _acquire(item, plan, view, client, gate, target, settled, listed[item.root],
                          reports_base, harness)
        done.append({"root": item.root, "chunk": target.name, "action": action})
        log(f"{item.root} {target.name}: {action} · session ${gate.session_spent_usd():.6f}")
    try:
        messages = fetch_free_metadata(client, plan, tuple(listed), rolls_dir=rolls_dir,
                                       condition_dir=condition_dir)
    except Exception as exc:  # noqa: BLE001 — named, never silent: the store needs these files
        raise HistPlanError(f"every chunk is bought, but the free metadata fetch failed "
                            f"({type(exc).__name__}: {exc}); rerun the buy (bought chunks are "
                            "skipped) to fetch it") from exc
    for message in messages:
        log(message)
    return harness, done


def _settled_keys(entries: list[dict[str, Any]], account: str) -> set[str]:
    """Settled request keys on ``account`` under any session (a plan's buy may resume later)."""
    return {request_key(e["request"]) for e in entries
            if e.get("event") == "settle" and e.get("account") == account and "request" in e}


def _write_once(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1, default=str)
    path.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)


def fetch_free_metadata(client: Any, plan: HistPlan, roots: Sequence[str], *,
                        rolls_dir: Path = ROLLS_DIR, condition_dir: Path = CONDITION_DIR
                        ) -> list[str]:
    """The store's free metadata, each file written once: symbology.resolve per root over the
    plan's data window, and the dataset condition list. Returns log lines."""
    from data.build_bars import fetch_symbology  # lazy: keeps the import light for quotes

    out = []
    for root in roots:
        path = symbology_cache_path(root, plan, rolls_dir)
        if path.is_file():
            out.append(f"{root}: symbology already cached ({path.name})")
            continue
        _write_once(path, fetch_symbology(root, client, plan.data_start, plan.data_end))
        out.append(f"{root}: symbology.resolve (free) written to {path.name}")
    cond = condition_path(plan, condition_dir)
    if cond.is_file():
        out.append(f"condition list already cached ({cond.name})")
    else:
        _write_once(cond, client.metadata.get_dataset_condition(
            dataset=DATASET, start_date=str(plan.data_start), end_date=str(plan.data_end)))
        out.append(f"dataset condition (free) written to {cond.name}")
    return out


# ------------------------------------------------------------------ CLI ----
def log_line(message: str) -> None:
    print(f"[{datetime.now(LOCAL_TZ):%Y-%m-%d %H:%M:%S %Z}] {message}", flush=True)


def build_client(key: str) -> Any:
    import databento  # lazy: the tests never build a real client

    return databento.Historical(key)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m data.pull_hist")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--quote-only", action="store_true", help="price a plan (free)")
    mode.add_argument("--buy", action="store_true", help="buy a plan through the gate")
    parser.add_argument("--plan", required=True, choices=HIST_PLAN_NAMES)
    parser.add_argument("--account", choices=tuple(ACCOUNTS),
                        help=f"the Databento account (required with --buy; quotes default to "
                             f"{E14_BUY_ACCOUNT})")
    parser.add_argument("--quotes-out", help="quotes JSON (--quote-only; the .md goes beside it)")
    parser.add_argument("--retry-failed", action="store_true")
    parser.add_argument("--harness-sha256", help="the frozen harness manifest's sha256 (--buy)")
    parser.add_argument("--roots", nargs="+", metavar="ROOT",
                        help=f"restrict the quote or buy to these roots (plan "
                             f"{', '.join(ROOTS_OPTION_PLANS)} only; E.17 amendment A4)")
    return parser


def _quotes_path(text: str | None) -> Path:
    from data.pull_step2 import QUOTES_JSON, QUOTES_MD  # E.2b's files are never targets

    if text is None:
        raise HistPlanError("--quote-only --plan needs --quotes-out <json>")
    path = Path(text)
    if path.suffix != ".json":
        raise HistPlanError(f"--quotes-out must name a .json file: {path}")
    if {path.resolve(), path.with_suffix(".md").resolve()} & {QUOTES_JSON.resolve(),
                                                              QUOTES_MD.resolve()}:
        raise HistPlanError("E.2b's quote files are never overwritten: choose another path")
    return path


def _check_args(args: argparse.Namespace) -> None:
    if args.quote_only and args.harness_sha256 is not None:
        raise HistPlanError("--quote-only takes no --harness-sha256")
    if args.buy:
        if args.harness_sha256 is None:
            raise HistPlanError("--buy requires --harness-sha256 (the frozen manifest's sha256)")
        if args.account is None:
            raise HistPlanError(f"--buy requires --account ({E14_BUY_ACCOUNT})")
        if args.quotes_out is not None or args.retry_failed:
            raise HistPlanError("--quotes-out and --retry-failed are for --quote-only")
        if args.plan in ROOTS_OPTION_PLANS and not args.roots:
            raise HistPlanError(f"--buy --plan {args.plan} requires --roots (A4: a buy of this plan "
                                "is restricted to the lead's selection; review F-1)")


def _plan_quote_gate(plan: HistPlan, account: str, quote_gate_factory: Callable[..., Any],
                     plan_quote_gate_factory: Callable[..., Any]) -> LockedQuoteGate:
    """es2011 and ext2010: the v10 quote gate, as in v10. ext2010h (v12): its own quote
    session, checked."""
    if plan.name in (PLAN_ES2011, PLAN_EXT2010):
        return quote_gate_factory(account=account)
    gate = plan_quote_gate_factory(plan=plan.name, account=account)
    if gate.session_id != quote_session_id(plan.name):
        raise HistPlanError(f"plan {plan.name} quotes under {quote_session_id(plan.name)}, not "
                            f"{gate.session_id}")
    return gate


def main(argv: list[str] | None = None, *,
         key_loader: Callable[..., str] = require_databento_key,
         quote_gate_factory: Callable[..., LockedQuoteGate] = quote_gate,
         buy_gate_factory: Callable[..., LockedQuoteGate] = buy_gate,
         client_factory: Callable[[str], Any] = build_client,
         vendor_root: Path = VENDOR_ROOT, reports_base: Path = HIST_REPORTS,
         registry_path: Path = trial_registry.REGISTRY_PATH, rolls_dir: Path = ROLLS_DIR,
         condition_dir: Path = CONDITION_DIR, log: Callable[[str], None] = log_line,
         plan_quote_gate_factory: Callable[..., LockedQuoteGate] = plan_quote_gate) -> int:
    """The CLI. The keyword arguments are for tests (fake clients, tmp ledgers and paths).
    ``quote_gate_factory`` serves es2011 and ext2010, ``plan_quote_gate_factory`` ext2010h."""
    args = _parser().parse_args(argv)
    account = E14_BUY_ACCOUNT if args.account is None else args.account
    try:
        _check_args(args)
        plan = get_plan(args.plan)
        roots = select_roots(plan, args.roots)  # A4: None unless --roots (ext2010h only)
        items = plan_chunks(plan, roots)
        if args.quote_only:
            out = _quotes_path(args.quotes_out)
            gate = _plan_quote_gate(plan, account, quote_gate_factory, plan_quote_gate_factory)
        else:
            gate = buy_gate_factory(plan=plan.name, account=account)
        log(banner(gate))
        chosen = plan.roots if roots is None else roots
        log(f"plan {plan.name} (test {plan.test}): {len(items)} chunks over "
            f"{len(chosen)} root(s) {', '.join(chosen)}, {plan.chunks[0][0]}.."
            f"{plan.chunks[-1][1]} (end exclusive, 00:00 UTC)")
        if roots is not None:
            log(f"--roots: {len(roots)} of plan {plan.name}'s {len(plan.roots)} roots; no other "
                "root is quoted or bought")
        if args.buy:
            log(f"harness preflight passed: {harness_freeze.preflight(args.harness_sha256)}")
            require_buy_ready(gate, plan, account, registry_path=registry_path)
        key = key_loader(account=account)
    except (HistPlanError, harness_freeze.HarnessFreezeError, trial_registry.TrialRegistryError,
            BudgetRefusedError, UnknownAccountError, MissingSecretError,
            ExternalLedgerUnavailableError, OSError, ValueError, KeyError) as exc:
        print(f"REFUSED before any vendor call ({type(exc).__name__}): {exc}", file=sys.stderr)
        return RC_REFUSED
    client = client_factory(key)
    try:
        if args.quote_only:
            return _quote_main(client, gate, plan, items, out, args.retry_failed, log,
                               roots=roots)
        harness, done = run_hist_buy(
            client, gate, plan, items, expected_harness_sha256=args.harness_sha256,
            account=account, registry_path=registry_path, vendor_root=vendor_root,
            reports_base=reports_base, rolls_dir=rolls_dir, condition_dir=condition_dir, log=log)
    except (HistPlanError, harness_freeze.HarnessFreezeError, trial_registry.TrialRegistryError,
            BudgetRefusedError, UnknownAccountError, ExternalLedgerUnavailableError,
            ResumeStateError, DownloadError, DeliveryCheckError, OSError, ValueError) as exc:
        print(f"RUN STOPPED ({type(exc).__name__}): {exc}. Nothing after this step was "
              "requested; see the ledger and docs/ACCESS.md.", file=sys.stderr)
        return RC_STOPPED
    log(f"buy finished: {len(done)} chunks · harness {harness} · {banner(gate)}")
    return 0


def _quote_main(client: Any, gate: LockedQuoteGate, plan: HistPlan, items: list[HistChunk],
                out: Path, retry_failed: bool, log: Callable[[str], None], *,
                roots: Sequence[str] | None = None) -> int:
    run_hist_quotes(client, gate, plan, items, log=log, retry_failed=retry_failed)
    quotes = quotes_from_ledger(items, read_entries(gate.ledger_path), gate.session_id)
    section = summarize_quotes(plan, quotes, account_position(gate), roots)
    extra = {"session_id": gate.session_id, "dataset": DATASET, "schema": OHLCV_1M}
    write_quotes(section, extra, out)
    log(f"{plan.name}: TOTAL QUOTED ${section['total_usd']:.6f} (x 1.03 = "
        f"${section['total_usd_x_1_03']:.6f}); {section['chunks_failed']} chunk quote(s) "
        f"failed; wrote {out.name}")
    return 0 if section["complete"] else RC_STOPPED


if __name__ == "__main__":
    sys.exit(main())
