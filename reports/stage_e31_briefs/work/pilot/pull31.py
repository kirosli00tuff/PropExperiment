"""Stage E.31 Part 3: span search, quote and buy of the ZM order-book pilot data on acct-3.

    pull31.py --plan        --months K [--out JSON]
    pull31.py --span-search
    pull31.py --quote       --months K
    pull31.py --buy         --months K --approved-usd X
    pull31.py --retry-download --series S --month YYYY-MM     (lead only)

Run from the repo root as ``uv run python reports/stage_e31_briefs/work/pilot/pull31.py ...``
(README31.md has the sequence). Spec: reports/stage_e31_pilot_spec.md sections 0, 1 and 9.

Every mode refuses, before the key is read and before any vendor call (exit 2): an account other
than acct-3; a request that is not one of the four pilot series (root, schema, symbol set,
stype) or whose window is not the month rule's; a month after 2024-02 or before 2019-06; any
overlap with the embargo, the research window, holdout 1 or a sealed range
(pilot31_common.request_refusals). Exit codes: 0 done, 1 stopped after vendor calls began (or
the plan says buy nothing), 2 refused before any vendor call.

--plan         no call of any kind: the 4K requests, their target files, TARGET and acct-3's
               ledger position.
--span-search  free ledgered quotes (session stage-E.31-2026-10-22-pilot-span, cap 0.00) of the
               4 requests of each month from 2024-02 backwards; stops at the first month whose
               addition makes the cumulative sum exceed TARGET; k = the months before it.
               k < 2: buy nothing (exit 1). Writes runs/span31.json. Never buys (timeseries and
               batch are raising guards).
--quote        fresh free quotes of all 4K requests (session stage-E.31-2026-10-22-pilot),
               written to runs/quote31.json with their sum. Never buys (guards as above).
--buy          refuses unless runs/quote31.json holds this plan's quotes, each under 24 h old
               and in the ledger, with sum <= TARGET and sum <= X < sum + 0.01; and unless
               acct-3's ledger holds no commit other than Part 1's volume request and this
               plan's requests. Session cap TARGET; acct-3 cap 125.00. Order: Z1 latest month
               first, then earlier Z1 months, then Z2, Z3, Z4 in the same month order. Per
               request: fresh re-quote (refused if more than 1% above its quote31 value: stop,
               exit 1) -> authorize (RequestCappedGate, request cap = quote31 x 1.01) -> commit
               -> download (.partial, link, read-only) -> record-byte check -> settle (billing
               more than 3% above the quote: settled pro rata, remaining buys stopped, exit 1)
               -> runs/purchase31_<series>_<month>.json. Resume: a settled file is skipped; a
               file with an open commit is settled without a new download; an open commit with
               no file, a stray .partial, a file with no ledger line, a settle with no file or
               another overlapping file is refused (exit 2) for the lead. Nothing is deleted.
               A request retried by --retry-download resumes from its retry-session lines.
               The free condition list goes to runs/condition31_<first>_<last>.json (best
               effort; --span-search writes it too).
--retry-download  lead only (spec v2 section 9, recovery; SpecReviewer pass 1 item 4): one
               request whose download failed after its commit. Allowed only when that request
               has an open commit in the pilot session, no target file, no .partial, no
               overlapping file and no earlier retry commit (at most one retry per request).
               The failed commit stays counted as spent. Fresh ledgered quote -> authorize in
               session stage-E.31-2026-10-22-pilot-retry, cap 125.00 - acct-3 committed so far,
               request cap = the failed commit's quote x 1.01 -> commit -> download -> record-
               byte check -> settle -> purchase record, as --buy. A failed retry download stops
               (exit 1); a second retry is refused. Then --buy resumes the rest.
--buy and --retry-download hold runs/.buy31.lock (flock) for the whole run; a second process is
refused (exit 2) before the ledger is read.
"""
# ruff: noqa: I001 - pilot31_common is imported first on purpose (sys.path)

from __future__ import annotations

import argparse
import contextlib
import fcntl
import json
import os
import re
import sys
import time as time_mod
from collections.abc import Callable, Iterator
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

import pilot31_common as pc  # first: puts the repo root on sys.path

from data import adapter  # noqa: E402
from data.config import (  # noqa: E402
    ACCESS_DOC_PATH,
    LEDGER_PATH,
    MissingSecretError,
    require_databento_key,
)
from data.pull_mes import RequestCappedGate  # noqa: E402
from data.pull_universe import (  # noqa: E402
    DeliveryCheckError,
    DownloadError,
    ResumeStateError,
    download,
    file_sha256,
    files_overlapping,
    params_from_request,
)
from data.quote_universe import (  # noqa: E402
    ForbiddenNamespace,
    QuoteOnlyView,
    call_with_retry,
    install_forbidden_guards,
    request_key,
)
from data.spend_gate import (  # noqa: E402
    BudgetRefusedError,
    ExternalLedgerUnavailableError,
    Quote,
    SpendGate,
    UnknownAccountError,
    read_entries,
)

RUNS_DIR = Path(__file__).resolve().parent / "runs"
QUOTE_FILE = "quote31.json"
SPAN_FILE = "span31.json"
NOTE = "Stage E.31 Part 3 ZM order-book pilot purchase (V48, acct-3)"
REFUSALS = (pc.PilotRefused, BudgetRefusedError, UnknownAccountError,
            ExternalLedgerUnavailableError, MissingSecretError, ResumeStateError, ValueError,
            OSError, KeyError)


class SpanSearchError(RuntimeError):
    """A span-search quote failed; nothing was bought."""


class Stop(RuntimeError):
    """A stop after vendor calls began (exit 1); the message says why."""


# ------------------------------------------------------------------ helpers ----
def log_line(message: str) -> None:
    print(f"[{datetime.now(pc.PT):%Y-%m-%d %H:%M:%S %Z}] {message}", flush=True)


def build_client(key: str) -> Any:
    import databento  # lazy: the tests never build a real client

    return databento.Historical(key)


def build_gate(ctx: dict[str, Any], session_id: str, session_cap_usd: float,
               request_cap_usd: float | None = None) -> SpendGate:
    kwargs = {"ledger_path": ctx["ledger"], "access_doc_path": ctx["access"],
              "session_cap_usd": session_cap_usd, "account": pc.PILOT_ACCOUNT}
    if request_cap_usd is None:
        return SpendGate(session_id, **kwargs)
    return RequestCappedGate(session_id, request_cap_usd=request_cap_usd, **kwargs)


def position(gate: SpendGate) -> dict[str, Any]:
    spent = gate.account_spent_usd()
    return {"account": gate.account_id, "account_cap_usd": gate.account_cap_usd,
            "account_committed_usd": round(spent, 11),
            "account_headroom_usd": round(gate.account_cap_usd - spent, 11),
            "session_id": gate.session_id, "session_cap_usd": gate.session_cap_usd,
            "session_committed_usd": round(gate.session_spent_usd(), 11)}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, indent=1, default=str) + "\n", encoding="utf-8")
    tmp.replace(path)


def now_pt() -> str:
    return datetime.now(pc.PT).isoformat(timespec="seconds")


def last_entry(path: Path) -> dict[str, Any]:
    """The ledger's last line (read from the file's tail)."""
    with path.open("rb") as fh:
        fh.seek(0, 2)
        size = fh.tell()
        fh.seek(max(0, size - (1 << 16)))
        tail = fh.read()
    lines = [x for x in tail.splitlines() if x.strip()]
    return json.loads(lines[-1])


@contextlib.contextmanager
def buy_lock(runs_dir: Path, mode: str) -> Iterator[Path]:
    """flock on runs/.buy31.lock for a whole --buy or --retry-download (SpecReviewer pass 1
    item 12). A held lock is refused at once (no wait). The file is never deleted; it holds
    the last holder's pid, mode and start time."""
    runs_dir.mkdir(parents=True, exist_ok=True)
    path = runs_dir / pc.LOCK_FILE
    with path.open("a+", encoding="utf-8") as fh:
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            fh.seek(0)
            holder = fh.read().strip()[:200] or "holder unknown"
            raise pc.PilotRefused(f"{path} is held by another --buy or --retry-download "
                                  f"({holder}); nothing done") from exc
        fh.seek(0)
        fh.truncate()
        fh.write(f"pid {os.getpid()} {mode} since {now_pt()}\n")
        fh.flush()
        yield path  # closing the file releases the lock


def quote_row(gate: SpendGate, view: Any, item: pc.Planned) -> dict[str, Any]:
    """One ledgered quote of ``item`` as a row (quoted_usd None when it failed)."""
    quote = gate.quote(view, pc.check_request(item.params))
    line = last_entry(gate.ledger_path)
    if line.get("event") != "quote" or request_key(line.get("request") or {}) != item.key:
        raise RuntimeError(f"the ledger's last line is not the quote of {item.label}")
    return {"series": item.series.name, "month": item.month_label,
            "request": item.params.as_kwargs(),
            "quoted_usd": None if quote is None else quote.usd,
            "billable_bytes": None if quote is None else quote.billable_bytes,
            "ledger_ts": line.get("ts"), "note": line.get("note", "")}


def fetch_condition(client: Any, months: list[date], runs_dir: Path,
                    sleep: Callable[[float], None]) -> str:
    """The free dataset-condition list over the span, written once."""
    first, last = min(months), max(months)
    path = runs_dir / f"condition31_{first:%Y-%m}_{last:%Y-%m}.json"
    if path.is_file():
        return f"condition list already on disk ({path.name})"
    start_date = pc.parse_utc(pc.month_bounds(first)[0]).date().isoformat()
    end_date = pc.LAST_TRADE_DATE.isoformat()
    payload = call_with_retry(lambda: client.metadata.get_dataset_condition(
        dataset=pc.PILOT_DATASET, start_date=start_date, end_date=end_date), sleep=sleep)
    write_json(path, {"dataset": pc.PILOT_DATASET, "start_date": start_date,
                      "end_date": end_date, "condition": payload, "written": now_pt()})
    return f"dataset condition (free) written to {path}"


def _condition_best_effort(client: Any, months: list[date], ctx: dict[str, Any]) -> None:
    try:
        ctx["log"](fetch_condition(client, months, ctx["runs"], ctx["sleep"]))
    except Exception as exc:  # noqa: BLE001 - named, never silent; best effort by the brief
        ctx["log"](f"WARNING: free dataset-condition fetch failed ({type(exc).__name__}: {exc})")


# ------------------------------------------------------------------ span search ----
def span_search(months: list[date], quote_month: Callable[[date], list[dict[str, Any]]],
                target_usd: float, log: Callable[[str], None]) -> dict[str, Any]:
    """Months latest first; stop at the first month whose addition makes the cumulative sum
    exceed TARGET. k = the months before it. A failed quote ends the search incomplete."""
    rows: list[dict[str, Any]] = []
    cumulative, k, over, error = 0.0, 0, None, None
    for month in months:
        try:
            quotes = quote_month(month)
        except SpanSearchError as exc:
            error = str(exc)
            break
        month_usd = sum(float(q["quoted_usd"]) for q in quotes)
        after = cumulative + month_usd
        within = round(after, pc.USD_DECIMALS) <= target_usd
        rows.append({"month": f"{month:%Y-%m}", "quotes": quotes, "month_usd": month_usd,
                     "cumulative_usd": after, "within_target": within})
        log(f"span {month:%Y-%m}: month ${month_usd:.6f}, cumulative ${after:.6f} "
            f"({'<=' if within else '>'} TARGET ${target_usd:.2f})")
        if not within:
            over = f"{month:%Y-%m}"
            break
        cumulative, k = after, k + 1
    complete = error is None
    chosen = [f"{m:%Y-%m}" for m in months[:k]]
    return {"complete": complete, "error": error, "k": k if complete else None,
            "k_before_error": None if complete else k, "months": chosen,
            "cost_usd": cumulative, "first_month_over_target": over,
            "limited_by_lower_bound": complete and over is None,
            "target_usd": target_usd, "buy": complete and k >= pc.MIN_MONTHS_TO_BUY,
            "rows": rows}


# ------------------------------------------------------------------ the buy's checks ----
def quote31_refusals(payload: Any, items: list[pc.Planned], entries: list[dict[str, Any]],
                     now: datetime, target_usd: float, approved_usd: float
                     ) -> tuple[list[str], dict[str, float]]:
    """Why runs/quote31.json may not pay for this plan; and its quote per request key."""
    if not isinstance(payload, dict):
        return ["quote31.json is not a JSON object"], {}
    reasons: list[str] = []
    k = len(items) // len(pc.SERIES)
    if payload.get("months") != k:
        reasons.append(f"quote31.json is for {payload.get('months')!r} months, not {k}")
    if payload.get("session_id") != pc.PILOT_SESSION or payload.get("account") != \
            pc.PILOT_ACCOUNT:
        reasons.append("quote31.json is not from session "
                       f"{pc.PILOT_SESSION} on {pc.PILOT_ACCOUNT}")
    if payload.get("complete") is not True:
        reasons.append("quote31.json is incomplete (a quote failed): run --quote again")
    rows = payload.get("requests") or []
    keys = [request_key(r.get("request") or {}) for r in rows]
    if sorted(keys) != sorted(i.key for i in items):
        reasons.append("quote31.json's requests are not this plan's 4k requests")
    ledger = {(e.get("ts"), request_key(e["request"])): e for e in entries
              if e.get("session_id") == pc.PILOT_SESSION and e.get("event") == "quote"
              and e.get("account") == pc.PILOT_ACCOUNT and isinstance(e.get("request"), dict)}
    by_key: dict[str, float] = {}
    for key, row in zip(keys, rows, strict=True):
        reasons.extend(_row_refusals(row, ledger.get((row.get("ledger_ts"), key)), now))
        if row.get("quoted_usd") is not None:
            by_key[key] = float(row["quoted_usd"])
    total = round(sum(by_key.values()), pc.USD_DECIMALS)
    stated = payload.get("sum_usd")
    if not isinstance(stated, int | float) or abs(total - float(stated)) > 1e-9:
        reasons.append(f"quote31.json's sum_usd {payload.get('sum_usd')} != its quotes' sum "
                       f"{total:.9f}")
    if total > target_usd:
        reasons.append(f"quoted sum ${total:.6f} > TARGET ${target_usd:.2f}: nothing is bought")
    if total > approved_usd:
        reasons.append(f"quoted sum ${total:.6f} > --approved-usd ${approved_usd:.6f}")
    if approved_usd >= total + 0.01:
        reasons.append(f"--approved-usd ${approved_usd:.6f} is not the quoted sum "
                       f"${total:.6f} (sum <= X < sum + 0.01)")
    return reasons, by_key


def _row_refusals(row: dict[str, Any], line: dict[str, Any] | None, now: datetime) -> list[str]:
    label = f"{row.get('series')} {row.get('month')}"
    if row.get("quoted_usd") is None:
        return [f"{label}: its quote failed"]
    out = []
    if line is None or line.get("quoted_usd") != row.get("quoted_usd") \
            or line.get("billable_bytes") != row.get("billable_bytes"):
        out.append(f"{label}: no matching quote line in the ledger (session "
                   f"{pc.PILOT_SESSION}, ts {row.get('ledger_ts')})")
    try:
        age = now - datetime.fromisoformat(str(row.get("ledger_ts")))
    except ValueError:
        return [*out, f"{label}: unreadable quote time {row.get('ledger_ts')!r}"]
    if age > timedelta(hours=pc.QUOTE_MAX_AGE_H):
        out.append(f"{label}: quote is {age} old (> {pc.QUOTE_MAX_AGE_H:.0f} h): quote again")
    if age < -timedelta(minutes=5):
        out.append(f"{label}: quote time {row.get('ledger_ts')} is in the future")
    return out


def _same_request(entry: dict[str, Any], key: str) -> bool:
    return isinstance(entry.get("request"), dict) and request_key(entry["request"]) == key


def flow_lines(entries: list[dict[str, Any]], key: str, session: str) -> list[dict[str, Any]]:
    """acct-3's commit and settle lines of one request in one session, oldest first."""
    return [e for e in pc.acct3_lines(entries) if e.get("session_id") == session
            and e.get("event") in ("commit", "settle") and _same_request(e, key)]


def _stray_file_refusals(item: pc.Planned, target: Path) -> None:
    partial = target.with_name(target.name + ".partial")
    if partial.exists():
        raise ResumeStateError(f"{item.label}: {partial} exists (a download was cut short). "
                               "Nothing deleted; the lead decides")
    others = [p.name for p, _, _ in files_overlapping(target.parent, item.params.start,
                                                      item.params.end) if p != target]
    if others:
        raise ResumeStateError(f"{item.label}: other file(s) in {target.parent} overlap the "
                               f"request: {others[:3]}. Nothing deleted; the lead decides")


def _retry_hint(item: pc.Planned) -> str:
    return (f"--retry-download --series {item.series.name} --month {item.month_label} (lead "
            "only, once)")


def resume_state(entries: list[dict[str, Any]], item: pc.Planned, target: Path
                 ) -> tuple[str, dict[str, Any] | None]:
    """'done', 'settle_only' (with the open commit line, of the pilot or the retry session) or
    'new'; else raises (exit 2). A request with retry-session lines resumes from them."""
    _stray_file_refusals(item, target)
    pilot = flow_lines(entries, item.key, pc.PILOT_SESSION)
    retry = flow_lines(entries, item.key, pc.RETRY_SESSION)
    has_file = target.exists()
    if retry:
        return _retry_resume(item, target, pilot, retry, has_file)
    last = pilot[-1] if pilot else None
    unsettled = last is not None and last["event"] == "commit"
    if has_file and unsettled:
        return "settle_only", last
    if has_file and last is not None:
        return "done", None
    if has_file:
        raise ResumeStateError(f"{item.label}: {target} exists with no commit or settle line "
                               f"on {pc.PILOT_ACCOUNT}. Nothing deleted; the lead decides")
    if last is not None:
        if not unsettled:
            raise ResumeStateError(f"{item.label}: a settle line exists but {target} is "
                                   "missing; the lead decides")
        raise pc.PilotRefused(f"{item.label}: an open commit ({last.get('ts')}, "
                              f"${last.get('usd')}) has no file: a download was cut short and "
                              "may have been billed. The lead decides; the recovery is "
                              + _retry_hint(item))
    return "new", None


def _retry_resume(item: pc.Planned, target: Path, pilot: list[dict[str, Any]],
                  retry: list[dict[str, Any]], has_file: bool
                  ) -> tuple[str, dict[str, Any] | None]:
    if not pilot or pilot[-1]["event"] != "commit":
        raise ResumeStateError(f"{item.label}: retry-session lines exist but the pilot session "
                               "holds no open (failed) commit for it; the lead decides")
    last = retry[-1]
    unsettled = last["event"] == "commit"
    if has_file:
        return ("settle_only", last) if unsettled else ("done", None)
    if not unsettled:
        raise ResumeStateError(f"{item.label}: a retry settle line exists but {target} is "
                               "missing; the lead decides")
    raise pc.PilotRefused(f"{item.label}: its retry commit ({last.get('ts')}, "
                          f"${last.get('usd')}) has no file either: a second failure. The "
                          "purchases stop and the lead reports the gap (spec v2 section 9)")


def open_pilot_commit(entries: list[dict[str, Any]], key: str) -> dict[str, Any] | None:
    """The pilot session's open (unsettled) commit of a request, or None."""
    pilot = flow_lines(entries, key, pc.PILOT_SESSION)
    return pilot[-1] if pilot and pilot[-1]["event"] == "commit" else None


def settle_download(gate: SpendGate, quote: Quote, target: Path) -> dict[str, Any]:
    """Record-byte check (the one decode, a byte count) and settle, as data.pull_hist."""
    try:
        delivered = adapter.delivered_record_bytes(target)
    except Exception as exc:
        raise DeliveryCheckError(f"record-byte check of {target.name} failed "
                                 f"({type(exc).__name__}: {exc}); file kept, not settled") from exc
    billable = quote.billable_bytes
    ratio = delivered / billable if billable > 0 else (float("inf") if delivered else 1.0)
    over = ratio > 1.0
    actual = quote.usd * ratio if over and billable > 0 else quote.usd
    gate.settle(quote, actual_usd=actual, note=(
        f"{NOTE}: delivered uncompressed record bytes {delivered:,} vs quoted billable "
        f"{billable:,}" + (" - DELIVERED EXCEEDS QUOTE" if over else "")))
    return {"quoted_usd": quote.usd, "settled_usd": actual, "quoted_billable_bytes": billable,
            "delivered_record_bytes": delivered,
            "billed_over_quote_ratio": None if ratio == float("inf") else ratio,
            "billed_above_quote": over}


def write_record(path: Path, item: pc.Planned, target: Path, gate: SpendGate,
                 quote31_usd: float | None, billing: dict[str, Any],
                 rebuilt: bool = False, retry_of: dict[str, Any] | None = None
                 ) -> dict[str, Any]:
    payload = {"series": item.series.name, "month": item.month_label,
               "request": item.params.as_kwargs(), "target": str(target),
               "bytes": target.stat().st_size, "sha256": file_sha256(target),
               "quote31_usd": quote31_usd,
               "quote": {"usd": billing["quoted_usd"],
                         "billable_bytes": billing["quoted_billable_bytes"]},
               "settled": billing, "session_id": gate.session_id,
               "retry_of_commit": None if retry_of is None else {
                   "ts": retry_of.get("ts"), "usd": retry_of.get("usd"),
                   "session_id": retry_of.get("session_id")},
               "position_after": position(gate),
               "rebuilt_from_ledger": rebuilt, "written": now_pt()}
    write_json(path, payload)
    return payload


_DELIVERED_RE = re.compile(r"delivered uncompressed record bytes ([\d,]+)")


def delivered_from_note(note: Any) -> int | None:
    """The delivered record bytes a settle note states (settle_download's wording), or None."""
    found = _DELIVERED_RE.search(str(note or ""))
    return None if found is None else int(found.group(1).replace(",", ""))


def ensure_record(item: pc.Planned, target: Path, entries: list[dict[str, Any]],
                  gate: SpendGate, ctx: dict[str, Any]) -> None:
    """A settled file whose purchase record is missing (a run cut after the settle): rebuild
    it from the ledger (the retry session's lines when the request was retried). No vendor
    call; the delivered record bytes come from the settle note."""
    path = ctx["runs"] / pc.record_name(item)
    if path.is_file():
        return
    retry = flow_lines(entries, item.key, pc.RETRY_SESSION)
    retried = any(e["event"] == "settle" for e in retry)
    flow = retry if retried else flow_lines(entries, item.key, pc.PILOT_SESSION)
    commit = [e for e in flow if e.get("event") == "commit"][-1]
    settle = [e for e in flow if e.get("event") == "settle"][-1]
    delivered = delivered_from_note(settle.get("note"))
    billable = int(commit["billable_bytes"])
    ratio = None if delivered is None or billable <= 0 else delivered / billable
    billing = {"quoted_usd": commit["quoted_usd"], "settled_usd": settle["actual_usd"],
               "quoted_billable_bytes": billable, "delivered_record_bytes": delivered,
               "billed_over_quote_ratio": ratio,
               "billed_above_quote": None if ratio is None else ratio > 1.0,
               "settle_note": settle.get("note")}
    if retried:
        gate = retry_gate(ctx)
    write_record(path, item, target, gate, None, billing, rebuilt=True,
                 retry_of=open_pilot_commit(entries, item.key) if retried else None)
    ctx["log"](f"{item.label}: purchase record rebuilt from the ledger ({path.name})")


def retry_gate(ctx: dict[str, Any], request_cap_usd: float | None = None) -> SpendGate:
    """A gate of the retry session, its cap 125.00 - acct-3 committed so far (read now)."""
    probe = build_gate(ctx, pc.RETRY_SESSION, 0.0)
    cap = pc.retry_cap_usd(probe.account_spent_usd())
    return build_gate(ctx, pc.RETRY_SESSION, cap, request_cap_usd=request_cap_usd)


# ------------------------------------------------------------------ CLI ----
def _parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="pull31.py", description=__doc__.split("\n\n")[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--plan", action="store_true")
    mode.add_argument("--span-search", action="store_true")
    mode.add_argument("--quote", action="store_true")
    mode.add_argument("--buy", action="store_true")
    mode.add_argument("--retry-download", action="store_true",
                      help="lead only: retry one failed download once (spec v2 section 9)")
    ap.add_argument("--months", type=int, help="k: the months ending with 2024-02")
    ap.add_argument("--approved-usd", type=float, help="--buy: the approved quoted sum")
    ap.add_argument("--account", default=pc.PILOT_ACCOUNT)
    ap.add_argument("--out", help="--plan: also write the plan JSON here")
    ap.add_argument("--series", help="--retry-download: Z1, Z2, Z3 or Z4")
    ap.add_argument("--month", help="--retry-download: YYYY-MM")
    return ap


def main(argv: list[str] | None = None, *,
         key_loader: Callable[..., str] = require_databento_key,
         client_factory: Callable[[str], Any] = build_client,
         ledger_path: Path = LEDGER_PATH, access_doc_path: Path = ACCESS_DOC_PATH,
         vendor_root: Path = pc.PILOT_VENDOR_ROOT, runs_dir: Path = RUNS_DIR,
         now: Callable[[], datetime] = lambda: datetime.now(UTC),
         log: Callable[[str], None] = log_line,
         sleep: Callable[[float], None] = time_mod.sleep) -> int:
    """The CLI. Keyword arguments exist for tests (fake clients, tmp ledgers and paths)."""
    args = _parser().parse_args(argv)
    ctx: dict[str, Any] = {
        "key_loader": key_loader, "client_factory": client_factory, "ledger": Path(ledger_path),
        "access": Path(access_doc_path), "vendor": Path(vendor_root), "runs": Path(runs_dir),
        "now": now, "log": log, "sleep": sleep, "network": False}
    try:
        pc.require_account(args.account)
        if args.span_search:
            return _span_main(ctx)
        if args.retry_download:
            return _retry_main(args, ctx)
        if args.series is not None or args.month is not None:
            raise pc.PilotRefused("--series and --month belong to --retry-download only")
        if args.months is None:
            raise pc.PilotRefused("--months K is required for --plan, --quote and --buy")
        items = pc.plan(args.months)
        if args.plan:
            return _plan_main(args, items, ctx)
        if args.months < pc.MIN_MONTHS_TO_BUY:
            raise pc.PilotRefused(f"--months {args.months} < {pc.MIN_MONTHS_TO_BUY}: nothing "
                                  "is quoted for a buy or bought (spec sections 1 and 9)")
        if args.quote:
            return _quote_main(args, items, ctx)
        return _buy_main(args, items, ctx)
    except Stop as exc:
        print(f"RUN STOPPED: {exc}. See the ledger and README31.md for the resume.",
              file=sys.stderr)
        return pc.RC_STOPPED
    except Exception as exc:  # noqa: BLE001 - classified by whether a client exists yet
        if not ctx["network"]:
            if not isinstance(exc, REFUSALS):
                raise
            print(f"REFUSED before any vendor call ({type(exc).__name__}): {exc}",
                  file=sys.stderr)
            return pc.RC_REFUSED
        print(f"RUN STOPPED after vendor calls began ({type(exc).__name__}): {exc}. See the "
              "ledger, docs/ACCESS.md and README31.md for the resume.", file=sys.stderr)
        return pc.RC_STOPPED


def _client(ctx: dict[str, Any], *, guard_all: bool) -> Any:
    key = ctx["key_loader"](account=pc.PILOT_ACCOUNT)
    ctx["network"] = True  # from here on a failure is a stop, not a refusal
    client = ctx["client_factory"](key)
    if guard_all:
        install_forbidden_guards(client)  # timeseries and batch raise: nothing can be bought
    else:
        client.batch = ForbiddenNamespace()  # the buy needs timeseries.get_range only
    return client


def _plan_main(args: argparse.Namespace, items: list[pc.Planned], ctx: dict[str, Any]) -> int:
    entries = read_entries(ctx["ledger"])
    spend = pc.spend_target(entries)
    gate = build_gate(ctx, pc.PILOT_SESSION, spend["target_usd"])
    payload = {"months": args.months, "month_labels": sorted({i.month_label for i in items},
                                                             reverse=True),
               "n_requests": len(items), "buy_order": [i.label for i in items],
               "requests": [{"series": i.series.name, "month": i.month_label,
                             "request": i.params.as_kwargs(),
                             "target": str(pc.target_path(i, ctx["vendor"]))} for i in items],
               "spend": spend, "position": position(gate),
               "other_acct3_commits": pc.other_commits(entries, {i.key for i in items}),
               "buy_possible": args.months >= pc.MIN_MONTHS_TO_BUY, "vendor_calls": 0}
    print(json.dumps(payload, indent=1))
    if args.out:
        write_json(Path(args.out), payload)
    return pc.RC_OK


def _span_main(ctx: dict[str, Any]) -> int:
    log = ctx["log"]
    months = pc.span_months()
    pc.span_order(months)  # every request of every month is checked before any call
    spend = pc.spend_target(read_entries(ctx["ledger"]))
    target_usd = spend["target_usd"]
    gate = build_gate(ctx, pc.SPAN_SESSION, 0.0)
    log(f"span search: TARGET ${target_usd:.2f}, months {months[0]:%Y-%m} back to at most "
        f"{months[-1]:%Y-%m}, 4 quotes per month, session {pc.SPAN_SESSION} (cap 0.00)")
    client = _client(ctx, guard_all=True)
    view = QuoteOnlyView(client, ctx["sleep"])

    def quote_month(month: date) -> list[dict[str, Any]]:
        rows = [quote_row(gate, view, item) for item in pc.span_order([month])]
        failed = [f"{r['series']} {r['month']}" for r in rows if r["quoted_usd"] is None]
        if failed:
            raise SpanSearchError(f"quote(s) failed for {failed} (ledgered)")
        return rows

    result = span_search(months, quote_month, target_usd, log)
    result = {**result, "spend": spend, "session_id": gate.session_id,
              "account": pc.PILOT_ACCOUNT, "earliest_month": f"{months[-1]:%Y-%m}",
              "bought": False, "written": now_pt()}
    write_json(ctx["runs"] / SPAN_FILE, result)
    if not result["complete"]:
        log(f"SPAN SEARCH STOPPED: {result['error']}; nothing bought")
        return pc.RC_STOPPED
    if not result["buy"]:
        log(f"SPAN PLAN: k = {result['k']} < {pc.MIN_MONTHS_TO_BUY}: buy nothing")
        return pc.RC_STOPPED
    _condition_best_effort(client, pc.months_back(result["k"]), ctx)
    log(f"SPAN PLAN: k = {result['k']} months ({result['months'][-1]}..{result['months'][0]}), "
        f"quoted ${result['cost_usd']:.6f} <= TARGET ${target_usd:.2f}"
        + (" (limited by the 2019-06 lower bound)" if result["limited_by_lower_bound"] else "")
        + f"; wrote {ctx['runs'] / SPAN_FILE}; nothing bought")
    return pc.RC_OK


def _quote_main(args: argparse.Namespace, items: list[pc.Planned], ctx: dict[str, Any]) -> int:
    log = ctx["log"]
    entries = read_entries(ctx["ledger"])
    spend = pc.spend_target(entries)
    others = pc.other_commits(entries, {i.key for i in items})
    if others:
        log(f"WARNING: --buy will refuse: acct-3 holds other commit(s): {others[:2]}")
    span = ctx["runs"] / SPAN_FILE
    if span.is_file():
        span_k = json.loads(span.read_text()).get("k")
        if span_k != args.months:
            log(f"WARNING: --months {args.months} differs from span31.json's k = {span_k}")
    gate = build_gate(ctx, pc.PILOT_SESSION, spend["target_usd"])
    client = _client(ctx, guard_all=True)
    view = QuoteOnlyView(client, ctx["sleep"])
    rows = []
    for item in items:
        rows.append(quote_row(gate, view, item))
        if rows[-1]["quoted_usd"] is None:
            log(f"QUOTE FAILED for {item.label} (ledgered); stopping")
            break
    complete = len(rows) == len(items) and all(r["quoted_usd"] is not None for r in rows)
    total = round(sum(float(r["quoted_usd"]) for r in rows if r["quoted_usd"] is not None),
                  pc.USD_DECIMALS)
    within = complete and total <= spend["target_usd"]
    payload = {"months": args.months, "session_id": gate.session_id,
               "account": pc.PILOT_ACCOUNT, "spend": spend, "requests": rows, "sum_usd": total,
               "complete": complete, "within_target": within, "position": position(gate),
               "written": now_pt()}
    write_json(ctx["runs"] / QUOTE_FILE, payload)
    log(f"QUOTED {len(rows)}/{len(items)} requests, sum ${total:.6f} "
        f"({'<=' if within else 'NOT <='} TARGET ${spend['target_usd']:.2f}); wrote "
        f"{ctx['runs'] / QUOTE_FILE}")
    return pc.RC_OK if within else pc.RC_STOPPED


def _buy_main(args: argparse.Namespace, items: list[pc.Planned], ctx: dict[str, Any]) -> int:
    if args.approved_usd is None or args.approved_usd <= 0:
        raise pc.PilotRefused("--buy requires --approved-usd > 0 (the approved quoted sum)")
    with buy_lock(ctx["runs"], "--buy"):
        return _buy_locked(args, items, ctx)


def _buy_locked(args: argparse.Namespace, items: list[pc.Planned], ctx: dict[str, Any]) -> int:
    log = ctx["log"]
    entries = read_entries(ctx["ledger"])
    spend = pc.spend_target(entries)
    target_usd = spend["target_usd"]
    others = pc.other_commits(entries, {i.key for i in items})
    if others:
        raise pc.PilotRefused(f"{pc.PILOT_ACCOUNT} holds {len(others)} commit(s) for requests "
                              f"other than Part 1's volume request and this plan's (first: "
                              f"{others[0]}); nothing bought")
    targets = {i.key: pc.target_path(i, ctx["vendor"]) for i in items}
    states = [(i, *resume_state(entries, i, targets[i.key])) for i in items]
    gate = build_gate(ctx, pc.PILOT_SESSION, target_usd)
    if all(state == "done" for _, state, _ in states):
        for item, _, _ in states:
            ensure_record(item, targets[item.key], entries, gate, ctx)
        log(f"all {len(items)} files already bought and settled; nothing requested")
        return pc.RC_OK
    q31 = _load_quote31(ctx, items, entries, target_usd, args.approved_usd)
    if not ctx["vendor"].is_dir():
        raise pc.PilotRefused(f"vendor root {ctx['vendor']} is missing (large storage mounted?)")
    log(f"buy: {len(items)} requests, quoted sum ${sum(q31.values()):.6f}, approved "
        f"${args.approved_usd:.6f}, TARGET ${target_usd:.2f}; {position(gate)}")
    client = None
    for item, state, commit in states:
        target = targets[item.key]
        if state == "done":
            log(f"{item.label}: already bought and settled; skipped")
            ensure_record(item, target, entries, gate, ctx)
            continue
        if state == "settle_only":
            assert commit is not None
            quote = Quote(params_from_request(commit["request"]), float(commit["quoted_usd"]),
                          int(commit["billable_bytes"]))
            retried = commit.get("session_id") == pc.RETRY_SESSION
            log(f"{item.label}: on disk with an open {'retry ' if retried else ''}commit; "
                "settling without a new download")
            _finish(item, target, retry_gate(ctx) if retried else gate, quote, q31[item.key],
                    ctx, retry_of=open_pilot_commit(entries, item.key) if retried else None)
            continue
        if client is None:
            client = _client(ctx, guard_all=False)
        _buy_one(item, target, q31[item.key], client, target_usd, ctx)
    if client is not None:
        _condition_best_effort(client, pc.months_back(args.months), ctx)
    log(f"buy finished: {position(gate)}")
    return pc.RC_OK


def _load_quote31(ctx: dict[str, Any], items: list[pc.Planned], entries: list[dict[str, Any]],
                  target_usd: float, approved_usd: float) -> dict[str, float]:
    path = ctx["runs"] / QUOTE_FILE
    if not path.is_file():
        raise pc.PilotRefused(f"{path} is missing: run --quote --months K first")
    reasons, by_key = quote31_refusals(json.loads(path.read_text()), items, entries,
                                       ctx["now"](), target_usd, approved_usd)
    if reasons:
        raise pc.PilotRefused("; ".join(reasons))
    return by_key


def _buy_one(item: pc.Planned, target: Path, quote31_usd: float, client: Any,
             target_usd: float, ctx: dict[str, Any]) -> None:
    log = ctx["log"]
    view = QuoteOnlyView(client, ctx["sleep"])
    limit = round(quote31_usd * (1.0 + pc.REQUOTE_TOLERANCE), pc.USD_DECIMALS)
    gate = build_gate(ctx, pc.PILOT_SESSION, target_usd, request_cap_usd=limit)
    requote = gate.quote(view, pc.check_request(item.params))
    if requote is None:
        raise Stop(f"{item.label}: the fresh re-quote failed (ledgered); nothing committed")
    if round(requote.usd, pc.USD_DECIMALS) > limit:
        raise Stop(f"{item.label}: re-quote ${requote.usd:.6f} is more than "
                   f"{pc.REQUOTE_TOLERANCE:.0%} above its quote31 value ${quote31_usd:.6f}; "
                   "nothing committed")
    gate.authorize(item.params, requote)  # request, session and acct-3 caps; raises
    gate.commit(requote, note=f"{NOTE}: {item.label}")
    log(f"{item.label}: committed ${requote.usd:.6f}; downloading to {target}.partial")
    try:
        download(client, item.params, target)
    except (DownloadError, ResumeStateError, OSError) as exc:
        raise Stop(f"{item.label}: {type(exc).__name__}: {exc}") from exc
    log(f"{item.label}: downloaded {target.stat().st_size:,} bytes")
    _finish(item, target, gate, requote, quote31_usd, ctx)


def _finish(item: pc.Planned, target: Path, gate: SpendGate, quote: Quote,
            quote31_usd: float | None, ctx: dict[str, Any],
            retry_of: dict[str, Any] | None = None) -> None:
    try:
        billing = settle_download(gate, quote, target)
    except DeliveryCheckError as exc:
        raise Stop(f"{item.label}: {exc}") from exc
    record = write_record(ctx["runs"] / pc.record_name(item), item, target, gate, quote31_usd,
                          billing, retry_of=retry_of)
    ctx["log"](f"{item.label}: settled ${billing['settled_usd']:.6f} (sha256 "
               f"{record['sha256'][:16]}...)")
    ratio = billing["billed_over_quote_ratio"]
    if ratio is None or ratio > 1.0 + pc.BILLED_OVER_QUOTE_STOP:
        raise Stop(f"{item.label}: billed more than {pc.BILLED_OVER_QUOTE_STOP:.0%} above the "
                   f"quote (delivered {billing['delivered_record_bytes']:,} vs quoted "
                   f"{billing['quoted_billable_bytes']:,} bytes); settled pro rata and "
                   "recorded; the remaining buys are stopped")


# ------------------------------------------------------------------ retry (lead only) ----
def retry_item(series_name: str | None, month_label: str | None) -> pc.Planned:
    series = pc.SERIES_BY_NAME.get(str(series_name or ""))
    if series is None:
        raise pc.PilotRefused(f"--series {series_name!r} refused: one of "
                              f"{sorted(pc.SERIES_BY_NAME)}")
    month = pc.parse_month(month_label)
    return pc.Planned(series, month, pc.check_request(pc.request_for(series, month)))


def retry_refusals(entries: list[dict[str, Any]], item: pc.Planned, target: Path
                   ) -> dict[str, Any]:
    """The failed (open) pilot commit a retry may replace; raises when a retry is not
    allowed: a target file, a .partial or an overlapping file exists, no open pilot commit,
    or an earlier retry commit of this request (at most one retry per request)."""
    _stray_file_refusals(item, target)
    if target.exists():
        raise ResumeStateError(f"{item.label}: {target} exists: nothing to retry (--buy settles "
                               "or skips it)")
    earlier = [e for e in flow_lines(entries, item.key, pc.RETRY_SESSION)
               if e["event"] == "commit"]
    if earlier:
        raise pc.PilotRefused(f"{item.label}: already retried once (retry commit "
                              f"{earlier[0].get('ts')}): at most one retry per request; the "
                              "purchases stop and the lead reports the gap")
    failed = open_pilot_commit(entries, item.key)
    if failed is None:
        raise pc.PilotRefused(f"{item.label}: no open commit in session {pc.PILOT_SESSION}: "
                              "nothing to retry")
    return failed


def _quote31_value(ctx: dict[str, Any], item: pc.Planned) -> float | None:
    """The request's quote31 value when runs/quote31.json holds it (information only)."""
    path = ctx["runs"] / QUOTE_FILE
    if not path.is_file():
        return None
    for row in json.loads(path.read_text()).get("requests") or []:
        if request_key(row.get("request") or {}) == item.key and row.get("quoted_usd") is not None:
            return float(row["quoted_usd"])
    return None


def _retry_main(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    log = ctx["log"]
    item = retry_item(args.series, args.month)
    with buy_lock(ctx["runs"], "--retry-download"):
        entries = read_entries(ctx["ledger"])
        span_keys = {p.key for p in pc.span_order(pc.span_months())}
        others = pc.other_commits(entries, span_keys)
        if others:
            raise pc.PilotRefused(f"{pc.PILOT_ACCOUNT} holds {len(others)} commit(s) outside "
                                  f"the pilot's requests (first: {others[0]}); nothing done")
        target = pc.target_path(item, ctx["vendor"])
        failed = retry_refusals(entries, item, target)
        if not ctx["vendor"].is_dir():
            raise pc.PilotRefused(f"vendor root {ctx['vendor']} is missing")
        limit = round(float(failed["quoted_usd"]) * (1.0 + pc.REQUOTE_TOLERANCE),
                      pc.USD_DECIMALS)
        gate = retry_gate(ctx, request_cap_usd=limit)
        if gate.session_cap_usd <= 0:
            raise pc.PilotRefused(f"retry cap {gate.session_cap_usd:.6f} <= 0: acct-3 is spent")
        log(f"retry {item.label}: failed commit {failed.get('ts')} ${failed.get('usd')} stays "
            f"counted; session {pc.RETRY_SESSION} cap ${gate.session_cap_usd:.6f} (125.00 - "
            f"acct-3 committed), request cap ${limit:.6f}")
        client = _client(ctx, guard_all=False)
        requote = gate.quote(QuoteOnlyView(client, ctx["sleep"]), pc.check_request(item.params))
        if requote is None:
            raise Stop(f"{item.label}: the retry's fresh quote failed (ledgered); nothing "
                       "committed")
        if round(requote.usd, pc.USD_DECIMALS) > limit:
            raise Stop(f"{item.label}: retry quote ${requote.usd:.6f} is more than "
                       f"{pc.REQUOTE_TOLERANCE:.0%} above the failed commit's "
                       f"${float(failed['quoted_usd']):.6f}; nothing committed")
        gate.authorize(item.params, requote)  # request, retry-session and acct-3 caps; raises
        gate.commit(requote, note=f"{NOTE}: {item.label} RETRY of the failed commit "
                                  f"{failed.get('ts')} (${failed.get('usd')}, counted as spent)")
        log(f"{item.label}: retry committed ${requote.usd:.6f}; downloading to "
            f"{target}.partial")
        try:
            download(client, item.params, target)
        except (DownloadError, ResumeStateError, OSError) as exc:
            raise Stop(f"{item.label}: the retry's download failed too ({type(exc).__name__}: "
                       f"{exc}): a second failure stops the purchases; the lead reports the "
                       "gap") from exc
        log(f"{item.label}: downloaded {target.stat().st_size:,} bytes")
        _finish(item, target, gate, requote, _quote31_value(ctx, item), ctx, retry_of=failed)
        log(f"retry {item.label} settled; rerun --buy to resume the rest: {position(gate)}")
        return pc.RC_OK


if __name__ == "__main__":
    sys.exit(main())
