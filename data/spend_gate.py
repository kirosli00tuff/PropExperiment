"""Spend gate for Databento: quote every request, refuse past either cap.

Ported from MLCryptoEngine ``data/databento/budget.py`` (read-only port,
2026-09-16) and extended for an account shared across projects. The three
properties that make the MLCryptoEngine gate trustworthy carry over:

1. **Every request is priced before it is issued**, via the free
   ``metadata.get_cost`` / ``metadata.get_billable_size`` endpoints, and the
   quote itself is ledgered.
2. **Caps are cumulative and on disk.** Two of them:
   - the *session* cap: new spend attributed to one ``session_id`` in this
     repo's ledger;
   - the *shared account* cap: every project's spend on the Databento
     account, i.e. MLCryptoEngine's ledger (read, never written) plus this
     repo's. A missing external ledger closes the gate.
3. **Unpriceable means refused.** A request with unknown cost is never
   assumed cheap.

Ledger shape: MLCryptoEngine's ``SpendEntry`` fields (``ts, dataset, symbol,
schema, date, usd, billable_bytes, note``) are kept with the same meaning —
``sum(usd)`` is committed spend — and extended with an ``event`` type, the
exact request parameters, quoted/actual cost, and running totals. Events:

- ``quote``   — a price was obtained. ``usd = 0``.
- ``refused`` — the gate closed. ``usd = 0``. Also written to docs/ACCESS.md.
- ``commit``  — recorded *before* download. ``usd = quoted`` (pessimistic:
  a crash mid-download never leaves money spent that the ledger missed).
- ``settle``  — after download. ``usd = actual - quoted`` (normally 0).

The file is append-only: entries are only ever appended, never rewritten.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

from data.config import (
    ACCESS_DOC_PATH,
    EXTERNAL_LEDGER_PATHS,
    LEDGER_PATH,
    SESSION_CAP_USD,
    SHARED_ACCOUNT_CAP_USD,
)

EVENTS = ("quote", "refused", "commit", "settle")
# Cap comparisons round to a billionth of a dollar so a quote landing exactly on
# a cap is not refused by float noise (82.12 + 37.88 != 120.0 in binary).
USD_COMPARE_DECIMALS = 9


class BudgetRefusedError(RuntimeError):
    """The gate refused a request. The ledger and ACCESS.md say why."""


class ExternalLedgerUnavailableError(RuntimeError):
    """A shared-account ledger could not be read, so shared spend is unknown."""


class _Metadata(Protocol):
    def get_cost(self, **kwargs: Any) -> float: ...
    def get_billable_size(self, **kwargs: Any) -> int: ...


class _Client(Protocol):
    metadata: _Metadata


@dataclass(frozen=True, slots=True)
class RequestParams:
    """Exactly what is sent to Databento — the same dict prices and fetches."""

    dataset: str
    symbols: tuple[str, ...]
    schema: str
    stype_in: str
    start: str
    end: str

    def as_kwargs(self) -> dict[str, Any]:
        return {
            "dataset": self.dataset,
            "symbols": list(self.symbols),
            "schema": self.schema,
            "stype_in": self.stype_in,
            "start": self.start,
            "end": self.end,
        }


@dataclass(frozen=True, slots=True)
class Quote:
    params: RequestParams
    usd: float
    billable_bytes: int


@dataclass(frozen=True, slots=True)
class GateDecision:
    allowed: bool
    reason: str
    quoted_usd: float
    session_spent_usd: float
    shared_spent_usd: float


def read_entries(path: Path) -> list[dict[str, Any]]:
    """Every ledger line, oldest first. A missing ledger has no entries."""
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def committed_usd(entries: list[dict[str, Any]], session_id: str | None = None) -> float:
    """Sum of ``usd`` — MLCryptoEngine semantics — optionally for one session."""
    return sum(
        float(e.get("usd", 0.0))
        for e in entries
        if session_id is None or e.get("session_id") == session_id
    )


def decide(
    quoted_usd: float | None,
    session_spent_usd: float,
    shared_spent_usd: float,
    session_cap_usd: float = SESSION_CAP_USD,
    shared_cap_usd: float = SHARED_ACCOUNT_CAP_USD,
) -> GateDecision:
    """Pure cap arithmetic. Checked in fixed order: unpriced, session, shared."""
    if quoted_usd is None or quoted_usd < 0:
        return GateDecision(
            False,
            f"unpriceable request (quote={quoted_usd!r}): never assumed cheap",
            float("nan"),
            session_spent_usd,
            shared_spent_usd,
        )
    if round(session_spent_usd + quoted_usd, USD_COMPARE_DECIMALS) > session_cap_usd:
        return GateDecision(
            False,
            f"session cap: {session_spent_usd:.4f} spent + {quoted_usd:.4f} quoted = "
            f"{session_spent_usd + quoted_usd:.4f} > session cap {session_cap_usd:.2f}",
            quoted_usd,
            session_spent_usd,
            shared_spent_usd,
        )
    if round(shared_spent_usd + quoted_usd, USD_COMPARE_DECIMALS) > shared_cap_usd:
        return GateDecision(
            False,
            f"shared account cap: {shared_spent_usd:.4f} spent + {quoted_usd:.4f} quoted = "
            f"{shared_spent_usd + quoted_usd:.4f} > shared cap {shared_cap_usd:.2f}",
            quoted_usd,
            session_spent_usd,
            shared_spent_usd,
        )
    return GateDecision(True, "within both caps", quoted_usd, session_spent_usd, shared_spent_usd)


class SpendGate:
    """Ledgered quote -> decide -> commit -> settle for one session."""

    def __init__(
        self,
        session_id: str,
        ledger_path: Path = LEDGER_PATH,
        external_ledger_paths: tuple[Path, ...] = EXTERNAL_LEDGER_PATHS,
        access_doc_path: Path = ACCESS_DOC_PATH,
        session_cap_usd: float = SESSION_CAP_USD,
        shared_cap_usd: float = SHARED_ACCOUNT_CAP_USD,
    ) -> None:
        self.session_id = session_id
        self.ledger_path = ledger_path
        self.external_ledger_paths = external_ledger_paths
        self.access_doc_path = access_doc_path
        self.session_cap_usd = session_cap_usd
        self.shared_cap_usd = shared_cap_usd

    # -- totals -----------------------------------------------------------
    def session_spent_usd(self) -> float:
        return committed_usd(read_entries(self.ledger_path), self.session_id)

    def external_spent_usd(self) -> float:
        total = 0.0
        for path in self.external_ledger_paths:
            if not path.is_file():
                raise ExternalLedgerUnavailableError(
                    f"shared-account ledger {path} is missing: shared spend is unknown, "
                    "so the gate stays closed"
                )
            total += committed_usd(read_entries(path))
        return total

    def shared_spent_usd(self) -> float:
        return self.external_spent_usd() + committed_usd(read_entries(self.ledger_path))

    # -- ledger -----------------------------------------------------------
    def _append(
        self,
        event: str,
        params: RequestParams,
        *,
        usd: float,
        quoted_usd: float | None,
        actual_usd: float | None,
        billable_bytes: int,
        note: str = "",
    ) -> dict[str, Any]:
        if event not in EVENTS:
            raise ValueError(f"unknown ledger event {event!r}")
        session_after = self.session_spent_usd() + usd
        shared_after = self.shared_spent_usd() + usd
        entry = {
            "ts": datetime.now(UTC).isoformat(),
            "event": event,
            "session_id": self.session_id,
            "dataset": params.dataset,
            "symbol": ",".join(params.symbols),
            "schema": params.schema,
            "date": f"{params.start}..{params.end}",
            "usd": usd,
            "billable_bytes": billable_bytes,
            "note": note,
            "request": params.as_kwargs(),
            "quoted_usd": quoted_usd,
            "actual_usd": actual_usd,
            "session_cumulative_usd": round(session_after, 6),
            "shared_cumulative_usd": round(shared_after, 6),
        }
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger_path.open("a") as fh:  # append-only
            fh.write(json.dumps(entry) + "\n")
        return entry

    # -- flow -------------------------------------------------------------
    def quote(self, client: _Client, params: RequestParams) -> Quote | None:
        """Price a request (free endpoints) and ledger the quote.

        Returns ``None`` if no price could be obtained; ``authorize`` then refuses.
        """
        try:
            usd = float(client.metadata.get_cost(**params.as_kwargs()))
            billable = int(client.metadata.get_billable_size(**params.as_kwargs()))
        except Exception as exc:  # noqa: BLE001 — any failure means unpriced
            self._append(
                "quote", params, usd=0.0, quoted_usd=None, actual_usd=None,
                billable_bytes=0, note=f"quote failed: {type(exc).__name__}: {exc}",
            )
            return None
        self._append(
            "quote", params, usd=0.0, quoted_usd=usd, actual_usd=None, billable_bytes=billable
        )
        return Quote(params=params, usd=usd, billable_bytes=billable)

    def authorize(self, params: RequestParams, quote: Quote | None) -> GateDecision:
        """Decide; on refusal ledger it, write docs/ACCESS.md, and raise."""
        decision = decide(
            None if quote is None else quote.usd,
            self.session_spent_usd(),
            self.shared_spent_usd(),
            self.session_cap_usd,
            self.shared_cap_usd,
        )
        if decision.allowed:
            return decision
        self._append(
            "refused", params, usd=0.0,
            quoted_usd=None if quote is None else quote.usd, actual_usd=None,
            billable_bytes=0 if quote is None else quote.billable_bytes, note=decision.reason,
        )
        self._write_access_note(params, decision)
        raise BudgetRefusedError(decision.reason)

    def commit(self, quote: Quote, note: str = "") -> dict[str, Any]:
        """Record the charge BEFORE the download it pays for."""
        return self._append(
            "commit", quote.params, usd=quote.usd, quoted_usd=quote.usd, actual_usd=None,
            billable_bytes=quote.billable_bytes, note=note,
        )

    def settle(self, quote: Quote, actual_usd: float, note: str) -> dict[str, Any]:
        """Record the actual cost once known, as a delta against the commit."""
        return self._append(
            "settle", quote.params, usd=actual_usd - quote.usd, quoted_usd=quote.usd,
            actual_usd=actual_usd, billable_bytes=quote.billable_bytes, note=note,
        )

    def _write_access_note(self, params: RequestParams, decision: GateDecision) -> None:
        self.access_doc_path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            f"\n### Databento request refused by spend gate — {datetime.now(UTC).isoformat()}\n",
            f"- session: `{self.session_id}`",
            f"- quoted cost (USD): {decision.quoted_usd}",
            f"- request parameters: `{json.dumps(params.as_kwargs())}`",
            f"- session spent before: ${decision.session_spent_usd:.4f} "
            f"(cap ${self.session_cap_usd:.2f})",
            f"- shared account spent before: ${decision.shared_spent_usd:.4f} "
            f"(cap ${self.shared_cap_usd:.2f})",
            f"- reason stopped: {decision.reason}\n",
        ]
        with self.access_doc_path.open("a") as fh:
            fh.write("\n".join(lines))
