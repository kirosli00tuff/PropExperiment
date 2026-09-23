"""Stage A.1 Task 2: quote, then pull MES ohlcv-1m (continuous) through the spend gate.

    uv run python -m data.pull_mes --quote-only   # prices every chunk, ledgers quotes
    uv run python -m data.pull_mes --pull         # quote + gate + download, newest first

Monthly chunks, pulled newest-first: if the gate closes part-way, what was
already bought is the most recent history, which is what Stage D weights
most. Each chunk is its own priced, ledgered, immutable request.

Stage D.1f (reports/stage_d1f_confirmation_list.md 1.1, 1.2, 1.5 steps 2-3), run only by the
run session with the user's approval:

    uv run python -m data.pull_mes --d1f-quote-only   # prices the 71 chunks (free), ledgered
    uv run python -m data.pull_mes --d1f-rolls        # rolls 2019-04-01..2024-03-01 (free)
    uv run python -m data.pull_mes --d1f-pull         # buy OLDEST first; seal holdout 2 on arrival

Each of the three first runs the D.1f preflight's file-hash checks (the freeze manifest's
files, section 0, the declarations and the git anchor; ``d1f_freeze_check``) and refuses on
any problem, before any vendor call (adversarial review F2).
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Any

from data import adapter
from data import holdout as ho
from data.adapter import (
    MES_CALENDAR_CONTINUOUS,
    MES_CONTINUOUS,
    OHLCV_1M,
    STYPE_CONTINUOUS,
    RawFileExistsError,
    RollBoundary,
    fetch_range,
    raw_path,
    resolve_rolls,
    roll_cycle_violations,
    write_rolls,
)
from data.config import (
    D1F_REQUEST_CAP_USD,
    D1F_SESSION_CAP_USD,
    DATASET,
    REPO_ROOT,
    STAGE_A1_SESSION_ID,
    STAGE_D1F_SESSION_ID,
    VENDOR_ROOT,
    require_databento_key,
)
from data.holdout import is_sealed_raw, request_touches_sealed_window
from data.research_bars import CONFIRMATION_RAW_CHUNKS, HOLDOUT2_RAW_CHUNKS
from data.spend_gate import (
    USD_COMPARE_DECIMALS,
    BudgetRefusedError,
    GateDecision,
    Quote,
    RequestParams,
    SpendGate,
)

WINDOW_START = date(2025, 4, 1)
WINDOW_END = date(2026, 9, 16)  # exclusive; today (2026-09-16) is not yet complete

# Stage D.1f. The last chunk ends where the existing raw data begins (no overlap, no gap).
D1F_WINDOW_START = date(2019, 5, 1)  # MES's first billable month (list 1.1)
D1F_WINDOW_END = date(2025, 4, 1)  # exclusive
D1F_ROLLS_START = date(2019, 4, 1)  # MES's symbology interval opens here
D1F_ROLLS_END = date(2024, 3, 1)  # exclusive: nothing past the confirmation window
D1F_NOTE = "Stage D.1f MES ohlcv-1m history extension"


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
    mode.add_argument("--d1f-quote-only", action="store_true",
                      help="Stage D.1f: price the 71 chunks 2019-05..2025-03 (free)")
    mode.add_argument("--d1f-rolls", action="store_true",
                      help="Stage D.1f: roll boundaries 2019-04-01..2024-03-01 (free)")
    mode.add_argument("--d1f-pull", action="store_true",
                      help="Stage D.1f: buy 2019-05..2025-03 oldest first, sealing holdout 2")
    parser.add_argument("--rolls", action="store_true", help="resolve + store roll boundaries")
    args = parser.parse_args()

    import databento

    client = databento.Historical(require_databento_key())
    if args.d1f_quote_only or args.d1f_rolls or args.d1f_pull:
        return main_d1f(client, args)
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


# ---------------------------------------------------------------- Stage D.1f ----
class RequestCappedGate(SpendGate):
    """SpendGate plus a per-request ceiling, checked on the very quote fetch_range commits.
    data/spend_gate.py has no per-request cap and is frozen, so the cap lives here."""

    def __init__(self, session_id: str, *, request_cap_usd: float, **kwargs: Any) -> None:
        super().__init__(session_id, **kwargs)
        self.request_cap_usd = request_cap_usd

    def authorize(self, params: RequestParams, quote: Quote | None) -> GateDecision:
        if quote is not None and round(quote.usd, USD_COMPARE_DECIMALS) > self.request_cap_usd:
            decision = GateDecision(
                False, f"per-request cap: quoted {quote.usd:.4f} > request cap "
                       f"{self.request_cap_usd:.2f}",
                quote.usd, self.session_spent_usd(), self.shared_spent_usd())
            self._append("refused", params, usd=0.0, quoted_usd=quote.usd, actual_usd=None,
                         billable_bytes=quote.billable_bytes, note=decision.reason)
            self._write_access_note(params, decision)
            raise BudgetRefusedError(decision.reason)
        return super().authorize(params, quote)


def d1f_gate(**overrides: Any) -> RequestCappedGate:
    """The D.1f gate: STAGE_D1F_SESSION_ID with the D.1f session and per-request caps.
    ``overrides`` exist for tests (tmp ledgers); the run session passes none."""
    kwargs = {"session_cap_usd": D1F_SESSION_CAP_USD, "request_cap_usd": D1F_REQUEST_CAP_USD,
              **overrides}
    return RequestCappedGate(STAGE_D1F_SESSION_ID, **kwargs)


def d1f_chunks() -> list[tuple[str, str]]:
    """The 71 D.1f chunks, OLDEST first: the 58 confirmation chunks, then the 13 holdout-2."""
    chunks = monthly_chunks(D1F_WINDOW_START, D1F_WINDOW_END)
    if chunks != [*CONFIRMATION_RAW_CHUNKS, *HOLDOUT2_RAW_CHUNKS]:
        raise ValueError("D.1f chunks disagree with data.research_bars' confirmation and "
                         "holdout-2 chunk lists")
    return chunks


def _d1f_params(start: str, end: str) -> RequestParams:
    return RequestParams(DATASET, (MES_CONTINUOUS,), OHLCV_1M, STYPE_CONTINUOUS, start, end)


def quote_d1f(client: Any, gate: RequestCappedGate, log: Callable[[str], None] = print) -> float:
    """Price every D.1f chunk through the gate (free; each quote is ledgered). Buys nothing."""
    total = 0.0
    for start, end in d1f_chunks():
        quote = gate.quote(client, _d1f_params(start, end))
        if quote is None:
            log(f"{start}..{end}: UNPRICEABLE (the pull would refuse it)")
            continue
        total += quote.usd
        over = " EXCEEDS THE PER-REQUEST CAP" if quote.usd > gate.request_cap_usd else ""
        log(f"{start}..{end}: ${quote.usd:.6f}{over}")
    log(f"TOTAL QUOTED ${total:.6f} (session cap ${gate.session_cap_usd:.2f})")
    return total


def _refuse_out_of_order(h2: ho.HoldoutPaths, start: str, end: str, target: Path) -> None:
    """Holdout-2 chunks are bought and sealed oldest first; refused before any buy or decode."""
    expected = ho.next_holdout2_chunk(h2)
    if expected != (start, end):
        raise ho.SealIntegrityError(f"{target.name} is out of order: the next holdout-2 chunk to "
                                    f"buy and seal is {expected}")


def pull_d1f(client: Any, gate: RequestCappedGate | None = None, *, root: Path = VENDOR_ROOT,
             log: Callable[[str], None] = print) -> list[dict[str, str]]:
    """Quote, gate and download the 71 D.1f chunks OLDEST first; each holdout-2 chunk is sealed
    by this same call, right after fetch_range's record-byte check (its only decode) and before
    the next chunk is requested. Refuses to re-buy a chunk whose plaintext exists or that either
    holdout manifest lists (L-1). A gate refusal (session, shared or per-request cap) or any
    sealing failure raises and stops the whole pull. Reads data.holdout's DEFAULT_PATHS and
    HOLDOUT2_PATHS at call time, the same paths fetch_range's own refusals read.

    Resume: a holdout-2 chunk found on disk unsealed (a pull stopped between fetch_range's link
    and its settle) gets the same record-byte check before it is sealed, and its SEALED entry
    records the byte count; a sealed chunk whose plaintext is still on disk (a seal stopped
    after its manifest record) is finished by ho.complete_interrupted_seal, which removes the
    plaintext only under the normal path's proof and otherwise raises, removing nothing."""
    h1, h2 = ho.DEFAULT_PATHS, ho.HOLDOUT2_PATHS
    gate = d1f_gate() if gate is None else gate
    if not isinstance(gate, RequestCappedGate):
        raise TypeError("the D.1f pull needs the per-request cap: pass a RequestCappedGate")
    if Path(h2.vendor_root).resolve() != Path(root).resolve():
        raise ValueError(f"holdout 2 seals chunks under {h2.vendor_root}, not {root}")
    done: list[dict[str, str]] = []
    for start, end in d1f_chunks():
        target = raw_path(MES_CONTINUOUS, OHLCV_1M, start, end, root)
        holdout2 = (start, end) in HOLDOUT2_RAW_CHUNKS
        if ho.is_sealed_raw(target, h2):
            if target.exists() or ho.partial_path(target).exists():
                ho.complete_interrupted_seal(target, h2)  # raises, removing nothing, unless proven
                action = "plaintext of an interrupted holdout-2 seal removed on resume"
            else:
                action = "skipped: sealed as holdout 2, never re-bought"
        elif ho.is_sealed_raw(target, h1):
            action = "skipped: sealed as holdout 1, never re-bought"
        elif target.exists() and holdout2:
            _refuse_out_of_order(h2, start, end, target)  # before the decode, as before a buy
            delivered = adapter.delivered_record_bytes(target)  # the one decode (list 1.2)
            ho.seal_holdout2_chunk(target, h2, note=(
                "sealed on resume: already downloaded by an interrupted pull, not re-bought; "
                f"record-byte check run on resume: {delivered:,} delivered record bytes"))
            action = "SEALED as holdout 2 on resume (already downloaded, not re-bought)"
        elif target.exists():
            action = "skipped: already on disk, never re-bought"
        else:
            if holdout2:
                _refuse_out_of_order(h2, start, end, target)
            path = fetch_range(gate, client, _d1f_params(start, end), root=root, note=D1F_NOTE)
            if holdout2:
                ho.seal_holdout2_chunk(path, h2)  # raises on any failure: the pull stops here
            action = "bought and SEALED as holdout 2" if holdout2 else "bought"
        done.append({"chunk": target.name, "action": action})
        log(f"{start}..{end}: {action} · session ${gate.session_spent_usd():.4f}")
    report = ho.verify_seal(h2)
    if not report["all_ok"]:
        raise ho.SealIntegrityError(f"holdout 2 does not verify after the pull: {report}")
    return done


def resolve_d1f_rolls(client: Any, root: Path = VENDOR_ROOT,
                      log: Callable[[str], None] = print) -> dict[str, list[RollBoundary]]:
    """Roll boundaries over 2019-04-01..2024-03-01 only (free symbology), nothing past the
    confirmation window. Stored next to the raw data; an existing file is never overwritten."""
    start, end = D1F_ROLLS_START.isoformat(), D1F_ROLLS_END.isoformat()
    out: dict[str, list[RollBoundary]] = {}
    for sym in (MES_CONTINUOUS, MES_CALENDAR_CONTINUOUS):
        rolls = resolve_rolls(client, sym, start, end)
        late = [r.date for r in rolls if not start <= r.date < end]
        if late:
            raise ValueError(f"{sym}: symbology returned boundaries outside {start}..{end}: {late}")
        path = root / "rolls" / f"{sym.replace('.', '_')}_{start}_{end}.jsonl"
        try:
            write_rolls(rolls, path)
        except RawFileExistsError as exc:
            log(str(exc))
        log(f"{sym}: {len(rolls)} rolls; cycle violations: {roll_cycle_violations(rolls)}")
        out[sym] = rolls
    return out


RC_FREEZE_REFUSED = 2


def d1f_freeze_check(root: Path | None = None) -> tuple[list[str], str | None]:
    """The D.1f preflight's FILE-hash checks (declarations, freeze manifest files and unlisted
    *.py, section 0, git anchor) against ``root`` (default REPO_ROOT): (problems, manifest
    sha256). Not the build-summary or holdout-2 sealed checks, which cannot pass before the
    pull. Lazy import: strategy.research._d1f_preflight imports data.build_mes_bars, which
    imports this module (review F2)."""
    from strategy.research._d1f_preflight import hash_checks

    return hash_checks(REPO_ROOT if root is None else root)


def refuse_unless_frozen(what: str, check: Callable[[], tuple[list[str], str | None]]
                         ) -> str | None:
    """Run ``check``; print and return None on any problem, else return the manifest sha256."""
    problems, manifest_sha = check()
    if problems or manifest_sha is None:
        print(f"REFUSED ({what}): the harness does not match the committed freeze manifest; "
              "nothing was requested or written:", file=sys.stderr)
        for problem in problems or ["no manifest sha256"]:
            print(f"  - {problem}", file=sys.stderr)
        return None
    print(f"freeze check passed ({what}); manifest sha256 {manifest_sha}")
    return manifest_sha


def main_d1f(client: Any, args: argparse.Namespace) -> int:
    if refuse_unless_frozen("D.1f quote / rolls / pull", d1f_freeze_check) is None:
        return RC_FREEZE_REFUSED
    if args.d1f_rolls:
        resolve_d1f_rolls(client)
        return 0
    gate = d1f_gate()
    print(f"{gate.session_id}: session spent ${gate.session_spent_usd():.4f} (cap "
          f"${gate.session_cap_usd:.2f}, per request ${gate.request_cap_usd:.2f}) · shared "
          f"${gate.shared_spent_usd():.4f}")
    if args.d1f_quote_only:
        quote_d1f(client, gate)
        return 0
    try:
        pull_d1f(client, gate, root=ho.HOLDOUT2_PATHS.vendor_root)  # VENDOR_ROOT in the repo
    except BudgetRefusedError as exc:
        print(f"GATE REFUSED — {exc}. Pull stopped; see docs/ACCESS.md")
        return 1
    except (ho.SealIntegrityError, OSError, ValueError) as exc:  # any sealing failure
        print(f"PULL STOPPED — {type(exc).__name__}: {exc}\nNothing after this chunk was "
              "requested. A chunk whose seal failed keeps its plaintext (fail-closed). Run "
              "`uv run python -m data.holdout status`, fix the cause, then re-run --d1f-pull; "
              "a chunk on disk or sealed is never re-bought.", file=sys.stderr)
        return 1
    report = ho.verify_seal(ho.HOLDOUT2_PATHS)
    print(f"holdout 2: {report['state']}, {report['chunks_sealed']} chunks, "
          f"all_ok {report['all_ok']} · session ${gate.session_spent_usd():.6f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
