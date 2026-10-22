"""Stage E.28 Part B: the pilot purchase, one mbp-1 request of <ROOT>.v.0 on acct-3 (V44).

    pilot_pull.py --plan        --root ROOT (--first-trade-date D | --start BOUND) [--end BOUND]
    pilot_pull.py --span-search --root ROOT --target-usd X [--earliest D] [--first-listed D]
    pilot_pull.py --quote       --root ROOT (--first-trade-date D | --start BOUND) [--out JSON]
    pilot_pull.py --buy         --root ROOT (--first-trade-date D | --start BOUND)
                                --approved-usd X [--max-quote-age-hours H] [--retry-download]

(run as ``uv run python reports/stage_e28_briefs/work/B_pilot/pilot_pull.py ...`` from the repo
root; README.md in this folder has the exact sequence.)

Every mode refuses, before any vendor call and before the key is read: an account other than
acct-3; a root other than QM (pilot_common.PILOT_ROOT, the frozen spec's one contract, section 0;
RD-01); a dataset other than GLBX.MDP3; a schema other than mbp-1; a symbol other than
QM.v.0 or an stype other than continuous; an end other than exactly 2024-02-29T22:00:00Z
(exclusive: 16:00 CT, the end of trade date 2024-02-29; frozen spec sections 0 and 6, RS-01,
RD-02); a start
before GLBX.MDP3's first date; any overlap with the embargo and holdout 2, the research window,
holdout 1 or a sealed range (pilot_common.request_refusals reuses data.pull_universe's windows,
data.holdout and data.trade_date_guard). Exit codes: 0 done, 2 refused before any vendor call,
1 stopped after one (see the ledger and docs/ACCESS.md).

--plan: prints the request, its target file and the ledger position. No call of any kind.
--quote: prices exactly the one request (free metadata endpoints) through data.spend_gate on
  acct-3 under session ``stage-E.28-pilot``; the quote line is ledgered with the account. The
  client's timeseries and batch namespaces are replaced by raising guards first.
--buy: buys nothing when the start is later than start_bound(2024-01-12) = 2024-01-11T22:00Z,
  the start of the QM minimum span [2024-01-12, 2024-02-29T22:00Z) (frozen spec section 6,
  RS-07; pilot_common.MIN_SPAN_FIRST_TRADE_DATE); with the end pinned (RD-02) every bought span
  holds the whole minimum span. One purchase only (RD-01): it refuses when the ledger already
  holds a commit on acct-3 for any other request (a resume of the same request is unaffected).
  No new quote: it
  authorizes against the session's own newest quote and refuses when that quote is for another
  request, failed, is older than --max-quote-age-hours (default 24), was already followed by a
  commit, exceeds the spend target TARGET = B - max(3.00, 0.03 x B) rounded down to the cent
  (B = --balance-usd, default 125.00; RS-08), or is not what --approved-usd approves (the
  approval is for exactly the fresh quote: quote <= approved < quote + 0.01). The gate then
  refuses any spend past the session cap or acct-3's cap (125.00 committed in total).
  Then: commit -> one get_range to <target>.partial -> link to the target (never replaces)
  -> read-only -> record-byte check -> settle -> purchase record (runs/) -> the free
  dataset-condition list (best effort).
  Resumable and idempotent: a target with a settle line is "already bought" (exit 0, nothing
  called); a target with a commit but no settle (a run cut after the download) is settled
  without downloading again; a commit with no settle and no file (a download cut short, maybe
  billed) is refused unless --retry-download, which needs a newer quote; any other file in the
  folder overlapping the range, a file with no commit, or a settle with no file stops the run
  for the lead. Nothing is ever deleted except this run's own .partial file.
--span-search: the earliest whole trade date D no later than 2024-01-12 (RS-07; never before
  the root's first listed date nor, unless --earliest says otherwise, before the group calendar's
  coverage) with cost([start_bound(D), 2024-02-29T22:00Z)) <= TARGET, found by bisection over
  trade dates with one ledgered quote per step (session ``stage-E.28-pilot-span``, cap 0.00).
  TARGET defaults to the margin rule above from --balance-usd; --target-usd may only lower it.
  If even the minimum span costs more than TARGET, the plan is "buy nothing" (exit 1). It prints
  the plan and never buys (timeseries and batch are guarded).
"""
# ruff: noqa: I001 - pilot_common is imported first on purpose (sys.path)

from __future__ import annotations

import argparse
import json
import sys
import time as time_mod
from collections.abc import Callable
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

import pilot_common as pc  # first: puts the repo root on sys.path

from data import adapter  # noqa: E402
from data.config import (  # noqa: E402
    ACCESS_DOC_PATH,
    LEDGER_PATH,
    MissingSecretError,
    require_databento_key,
)
from data.pull_universe import (  # noqa: E402
    DeliveryCheckError,
    DownloadError,
    ResumeStateError,
    bound_token,
    download,
    file_sha256,
    files_overlapping,
    params_from_request,
    target_path,
)
from data.quote_universe import (  # noqa: E402
    ForbiddenNamespace,
    QuoteOnlyView,
    call_with_retry,
    first_mapped_date,
    install_forbidden_guards,
    request_key,
)
from data.spend_gate import (  # noqa: E402
    BudgetRefusedError,
    ExternalLedgerUnavailableError,
    Quote,
    RequestParams,
    SpendGate,
    UnknownAccountError,
    read_entries,
)

RUNS_DIR = Path(__file__).resolve().parent / "runs"
DEFAULT_MAX_QUOTE_AGE_H = 24.0
BILLED_OVER_QUOTE_STOP = 0.03  # as data.pull_hist: settled pro rata, then the run stops
NOTE = "Stage E.28 Part B order-book pilot purchase (V44, acct-3)"
REFUSALS = (pc.PilotRefused, BudgetRefusedError, UnknownAccountError,
            ExternalLedgerUnavailableError, MissingSecretError, ResumeStateError, ValueError,
            OSError, KeyError)


class SpanSearchError(RuntimeError):
    """The span search could not finish (a quote failed); nothing was bought."""


def log_line(message: str) -> None:
    print(f"[{datetime.now(pc.PT):%Y-%m-%d %H:%M:%S %Z}] {message}", flush=True)


def build_client(key: str) -> Any:
    import databento  # lazy: the tests never build a real client

    return databento.Historical(key)


def build_gate(session_id: str, ledger_path: Path, access_doc_path: Path,
               session_cap_usd: float) -> SpendGate:
    return SpendGate(session_id, ledger_path=ledger_path, access_doc_path=access_doc_path,
                     session_cap_usd=session_cap_usd, account=pc.PILOT_ACCOUNT)


def position(gate: SpendGate) -> dict[str, Any]:
    spent = gate.account_spent_usd()
    return {"account": gate.account_id, "account_cap_usd": gate.account_cap_usd,
            "account_committed_usd": round(spent, 6),
            "account_headroom_usd": round(gate.account_cap_usd - spent, 6),
            "session_id": gate.session_id, "session_cap_usd": gate.session_cap_usd,
            "session_committed_usd": round(gate.session_spent_usd(), 6)}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(payload, indent=1, default=str) + "\n", encoding="utf-8")
    tmp.replace(path)


# ------------------------------------------------------------------ the buy's checks ----
def _same_request(entry: dict[str, Any], key: str) -> bool:
    return "request" in entry and request_key(entry["request"]) == key


def fresh_quote(entries: list[dict[str, Any]], params: RequestParams, session_id: str,
                now: datetime, max_age_h: float, approved_usd: float,
                target_usd: float = pc.PILOT_ACCOUNT_CAP_USD) -> Quote:
    """The session's newest quote line, as a Quote, if it may pay for ``params``."""
    key = request_key(params.as_kwargs())
    quotes = [(i, e) for i, e in enumerate(entries)
              if e.get("session_id") == session_id and e.get("event") == "quote"]
    if not quotes:
        raise pc.PilotRefused(f"no quote in session {session_id}: run --quote first")
    i, line = quotes[-1]
    reasons = []
    if line.get("account") != pc.PILOT_ACCOUNT:
        reasons.append(f"the newest quote is on account {line.get('account')!r}")
    if not _same_request(line, key):
        reasons.append("the session's newest quote is for another request "
                       f"({line.get('date')}); an older quote is never used: quote this request "
                       "again")
    if line.get("quoted_usd") is None:
        reasons.append(f"the session's newest quote failed ({line.get('note')})")
    age = now - datetime.fromisoformat(line["ts"])
    if age > timedelta(hours=max_age_h):
        reasons.append(f"the newest quote is {age} old (> {max_age_h} h): quote again")
    if any(e.get("session_id") == session_id and e.get("event") == "commit"
           for e in entries[i + 1:]):
        reasons.append("a commit follows the session's newest quote: quote again first")
    usd = line.get("quoted_usd")
    if usd is not None and round(float(usd), 9) > approved_usd:
        reasons.append(f"quoted ${float(usd):.6f} > --approved-usd ${approved_usd:.6f}")
    if usd is not None and approved_usd >= float(usd) + 0.01:
        reasons.append(f"--approved-usd ${approved_usd:.6f} is not the fresh quote "
                       f"${float(usd):.6f}: the buy is approved for exactly that quote (RS-08)")
    if usd is not None and round(float(usd), 9) > target_usd:
        reasons.append(f"quoted ${float(usd):.6f} > the spend target ${target_usd:.2f} (balance "
                       "minus max(3.00, 3%), RS-08): nothing is bought")
    if reasons:
        raise pc.PilotRefused("; ".join(reasons))
    return Quote(params=params, usd=float(usd), billable_bytes=int(line["billable_bytes"]))


def other_purchases(entries: list[dict[str, Any]], params: RequestParams) -> list[str]:
    """RD-01: commit lines on acct-3 (the pilot-only account) for any request other than
    ``params``, described briefly. A commit line without a request counts as another one."""
    key = request_key(params.as_kwargs())
    out = []
    for e in entries:
        if e.get("account") != pc.PILOT_ACCOUNT or e.get("event") != "commit":
            continue
        if _same_request(e, key):
            continue
        req = e.get("request") or {}
        out.append(f"{e.get('ts')} {e.get('session_id')} {req.get('symbols')} "
                   f"{req.get('start')}..{req.get('end')}")
    return out


def resume_state(entries: list[dict[str, Any]], params: RequestParams, target: Path,
                 retry_download: bool) -> tuple[str, dict[str, Any] | None]:
    """'done', 'settle_only' (with the open commit line), 'retry' or 'new'; else raises."""
    key = request_key(params.as_kwargs())
    flow = [e for e in entries if e.get("account") == pc.PILOT_ACCOUNT
            and e.get("event") in ("commit", "settle") and _same_request(e, key)]
    last = flow[-1] if flow else None  # the state is the last commit/settle of the request
    unsettled = last is not None and last["event"] == "commit"
    others = [p.name for p, _, _ in files_overlapping(target.parent, params.start, params.end)
              if p != target]
    if others:
        raise ResumeStateError(f"other file(s) in {target.parent} overlap {params.start}.."
                               f"{params.end}: {others[:3]}. Nothing deleted; the lead decides")
    has_file = target.exists()
    if has_file and unsettled:
        return "settle_only", last
    if has_file and last is not None:
        return "done", None
    if has_file:
        raise ResumeStateError(f"{target} exists with no commit or settle line on "
                               f"{pc.PILOT_ACCOUNT}: a foreign or unfinished file. Nothing "
                               "deleted; the lead decides")
    if last is not None and not unsettled:
        raise ResumeStateError(f"a settle line exists for this request but {target} is missing;"
                               " the lead decides")
    if unsettled and not retry_download:
        raise pc.PilotRefused("an earlier commit of this request has no settle and no file: a "
                              "download was cut short and may have been billed. The lead "
                              "decides; --retry-download (after a new --quote) buys it again")
    return ("retry" if unsettled else "new"), None


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


def record_path(runs_dir: Path, root: str, params: RequestParams) -> Path:
    return runs_dir / (f"purchase_{root}_{bound_token(params.start)}_"
                       f"{bound_token(params.end)}.json")


def write_record(path: Path, root: str, params: RequestParams, target: Path, gate: SpendGate,
                 billing: dict[str, Any]) -> dict[str, Any]:
    payload = {"root": root, "request": params.as_kwargs(), "target": str(target),
               "bytes": target.stat().st_size, "sha256": file_sha256(target),
               "billing": billing, "position_after": position(gate),
               "written": datetime.now(pc.PT).isoformat(timespec="seconds")}
    write_json(path, payload)
    return payload


def fetch_condition(client: Any, params: RequestParams, runs_dir: Path,
                    sleep: Callable[[float], None]) -> str:
    """The dataset condition list over the request (a free metadata call), written once."""
    s, e = pc.parse_utc(params.start).date(), pc.parse_utc(params.end).date()
    path = runs_dir / f"condition_{params.dataset}_{s}_{e}.json"
    if path.is_file():
        return f"condition list already on disk ({path.name})"
    payload = call_with_retry(lambda: client.metadata.get_dataset_condition(
        dataset=params.dataset, start_date=s.isoformat(), end_date=e.isoformat()), sleep=sleep)
    write_json(path, payload)
    return f"dataset condition (free) written to {path}"


# ------------------------------------------------------------------ span search ----
def span_candidates(cal: Any, first: date, last: date = pc.LAST_PILOT_TRADE_DATE) -> list[date]:
    """Trade dates first..last: the group calendar's where it covers, weekdays before that."""
    days = (first + timedelta(days=n) for n in range((last - first).days + 1))
    return [d for d in days if (cal.covers(d) and cal.is_trade_date(d))
            or (not cal.covers(d) and d < cal.coverage[0] and d.weekday() < 5)]


def first_candidate_day(first_listed: date, earliest: date | None, cal: Any) -> date:
    """The earliest admissible first trade date: its start bound is at or after the first
    listed date's 00:00 UTC and the dataset's first date; not before ``earliest`` (default:
    the calendar's coverage start)."""
    floor = max(first_listed, pc.DATASET_FIRST_DATE)
    day = floor
    while pc.bound_ns(pc.start_bound(day)) < pc.ns_of(datetime.combine(floor, datetime.min.time(),
                                                                       tzinfo=UTC)):
        day += timedelta(days=1)
    return max(day, cal.coverage[0] if earliest is None else earliest)


def span_search(candidates: list[date], cost: Callable[[date], float], target_usd: float,
                log: Callable[[str], None] = lambda m: None) -> dict[str, Any]:
    """Bisection for the earliest candidate D with cost(D) <= target (cost falls as D moves
    later). Every cost() call is one ledgered quote."""
    if not candidates:
        raise SpanSearchError("no candidate trade dates")
    quotes: dict[date, float] = {}

    def q(day: date) -> float:
        if day not in quotes:
            quotes[day] = cost(day)
            log(f"span quote: first trade date {day} (start {pc.start_bound(day)}) "
                f"${quotes[day]:.6f}")
        return quotes[day]

    def fits(day: date) -> bool:
        return round(q(day), 9) <= target_usd

    rows = lambda: [{"first_trade_date": d.isoformat(), "start": pc.start_bound(d),  # noqa: E731
                     "usd": quotes[d]} for d in sorted(quotes)]
    if not fits(candidates[-1]):
        return {"feasible": False, "target_usd": target_usd, "quotes": rows(),
                "reason": f"even one trade date ({candidates[-1]}) costs more than the target"}
    lo, hi = -1, len(candidates) - 1
    if fits(candidates[0]):
        hi = 0
    else:
        lo = 0
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if fits(candidates[mid]):
                hi = mid
            else:
                lo = mid
    best = candidates[hi]
    ordered = [quotes[d] for d in sorted(quotes)]
    monotone = all(a >= b - 1e-9 for a, b in zip(ordered, ordered[1:], strict=False))
    return {"feasible": True, "target_usd": target_usd, "first_trade_date": best.isoformat(),
            "start": pc.start_bound(best), "end": pc.CUTOFF_BOUND, "cost_usd": quotes[best],
            "trade_dates_in_span": len(candidates) - hi,
            "next_earlier": None if lo < 0 else {"first_trade_date": candidates[lo].isoformat(),
                                                 "usd": quotes[candidates[lo]]},
            "limited_by_lower_bound": hi == 0, "costs_monotone": monotone,
            "quotes": rows()}


def resolve_first_listed(client: Any, root: str, sleep: Callable[[float], None]) -> date:
    """The first date ROOT.v.0 maps to an instrument (free symbology call)."""
    sym = pc.symbol_for(root)
    response = call_with_retry(lambda: client.symbology.resolve(
        dataset=pc.PILOT_DATASET, symbols=[sym], stype_in=pc.PILOT_STYPE_IN,
        stype_out="instrument_id", start_date=pc.DATASET_FIRST_DATE.isoformat(),
        end_date=pc.CUTOFF_BOUND), sleep=sleep)
    first = first_mapped_date(response if isinstance(response, dict) else dict(response), sym)
    if first is None:
        raise SpanSearchError(f"symbology.resolve returned no mapping for {sym}")
    return date.fromisoformat(str(first)[:10])


# ------------------------------------------------------------------ CLI ----
def _parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="pilot_pull.py", description=__doc__.split("\n\n")[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    for flag in ("--plan", "--quote", "--buy", "--span-search"):
        mode.add_argument(flag, action="store_true")
    ap.add_argument("--root", required=True)
    when = ap.add_mutually_exclusive_group()
    when.add_argument("--start", help="request start bound (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ)")
    when.add_argument("--first-trade-date", type=date.fromisoformat,
                      help="first whole trade date; the start becomes D-1 16:00 CT")
    ap.add_argument("--end", default=pc.CUTOFF_BOUND)
    ap.add_argument("--account", default=pc.PILOT_ACCOUNT)
    ap.add_argument("--dataset", default=pc.PILOT_DATASET)
    ap.add_argument("--schema", default=pc.PILOT_SCHEMA)
    ap.add_argument("--symbol", default=None, help="must equal ROOT.v.0 (default)")
    ap.add_argument("--stype-in", default=pc.PILOT_STYPE_IN)
    ap.add_argument("--session-id", default=pc.QUOTE_SESSION_ID)
    ap.add_argument("--approved-usd", type=float, help="--buy: the most the buy may cost")
    ap.add_argument("--max-quote-age-hours", type=float, default=DEFAULT_MAX_QUOTE_AGE_H)
    ap.add_argument("--session-cap-usd", type=float, default=pc.PILOT_ACCOUNT_CAP_USD)
    ap.add_argument("--retry-download", action="store_true")
    ap.add_argument("--balance-usd", type=float, default=pc.PILOT_ACCOUNT_CAP_USD,
                    help="acct-3's usable balance B (default and maximum 125.00); TARGET = "
                         "B - max(3.00, 0.03 x B), rounded down to the cent")
    ap.add_argument("--target-usd", type=float,
                    help="--span-search: a TARGET below the margin rule's (default: the rule)")
    ap.add_argument("--earliest", type=date.fromisoformat,
                    help="--span-search: lowest first trade date (default: calendar coverage)")
    ap.add_argument("--first-listed", type=date.fromisoformat,
                    help="--span-search: the root's first listed date (default: free lookup)")
    ap.add_argument("--out", help="JSON output (--quote, --span-search, --plan)")
    return ap


def _request(args: argparse.Namespace) -> RequestParams:
    if args.first_trade_date is None and args.start is None:
        raise pc.PilotRefused("give --first-trade-date or --start")
    start = pc.start_bound(args.first_trade_date) if args.first_trade_date else args.start
    params = pc.pilot_params(args.root, start, args.end, dataset=args.dataset,
                             schema=args.schema, symbol=args.symbol, stype_in=args.stype_in)
    return pc.check_request(params, args.root)


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
    ctx = {"key_loader": key_loader, "client_factory": client_factory, "ledger": ledger_path,
           "access": access_doc_path, "vendor": Path(vendor_root), "runs": Path(runs_dir),
           "now": now, "log": log, "sleep": sleep}
    try:
        pc.require_account(args.account)
        pc.require_root(args.root)
        pc.require_pilot_root(args.root)  # RD-01: QM only, every mode
        if args.span_search:
            return _span_main(args, ctx)
        pc.require_session_id(args.session_id)
        params = _request(args)
        target = target_path(params, ctx["vendor"])
        mode = "plan" if args.plan else "quote" if args.quote else "buy"
        log(f"pilot_pull --{mode} {args.root}: {params.as_kwargs()} on {pc.PILOT_ACCOUNT}, "
            f"session {args.session_id}; target {target}")
        if args.plan:
            return _plan_main(args, params, target, ctx)
        if args.quote:
            return _quote_main(args, params, ctx)
        return _buy_main(args, params, target, ctx)
    except Exception as exc:  # noqa: BLE001 - classified by whether a client exists yet
        if not ctx.get("network"):
            if not isinstance(exc, REFUSALS):
                raise
            print(f"REFUSED before any vendor call ({type(exc).__name__}): {exc}",
                  file=sys.stderr)
            return pc.RC_REFUSED
        print(f"RUN STOPPED after vendor calls began ({type(exc).__name__}): {exc}. See the "
              "ledger, docs/ACCESS.md and README for the resume.", file=sys.stderr)
        return pc.RC_STOPPED


def _balance(args: argparse.Namespace) -> float:
    if not 0 < args.balance_usd <= pc.PILOT_ACCOUNT_CAP_USD:
        raise pc.PilotRefused(f"--balance-usd must be in (0, {pc.PILOT_ACCOUNT_CAP_USD}]")
    return args.balance_usd


def _plan_main(args: argparse.Namespace, params: RequestParams, target: Path,
               ctx: dict[str, Any]) -> int:
    cal = pc.calendar_for(args.root)
    first = pc.first_whole_trade_date(params.start, cal)
    gate = build_gate(args.session_id, ctx["ledger"], ctx["access"], args.session_cap_usd)
    plan = {"request": params.as_kwargs(), "target": str(target),
            "first_whole_trade_date": None if first is None else first.isoformat(),
            "start_aligned_to_whole_trade_date": first is not None
            and pc.start_bound(first) == params.start,
            "last_trade_date": pc.LAST_PILOT_TRADE_DATE.isoformat(),
            "minimum_span": f"[{pc.MIN_SPAN_FIRST_TRADE_DATE}, {pc.CUTOFF_BOUND})",
            "covers_minimum_span": pc.min_span_refusal(params.start) is None,
            "spend_target_usd": pc.margin_target(_balance(args)),
            "position": position(gate), "vendor_calls": 0}
    print(json.dumps(plan, indent=1))
    if args.out:
        write_json(Path(args.out), plan)
    return pc.RC_OK


def _client(ctx: dict[str, Any], *, guard_all: bool) -> Any:
    key = ctx["key_loader"](account=pc.PILOT_ACCOUNT)
    ctx["network"] = True  # from here on a failure is a stop, not a refusal
    client = ctx["client_factory"](key)
    if guard_all:
        install_forbidden_guards(client)  # timeseries and batch raise: nothing can be bought
    else:
        client.batch = ForbiddenNamespace()  # the buy needs timeseries.get_range only
    return client


def _quote_main(args: argparse.Namespace, params: RequestParams, ctx: dict[str, Any]) -> int:
    gate = build_gate(args.session_id, ctx["ledger"], ctx["access"], args.session_cap_usd)
    short = pc.min_span_refusal(params.start)
    if short:
        ctx["log"](f"WARNING: --buy will refuse this request: {short}")
    ctx["log"](f"position before the quote: {position(gate)}")
    client = _client(ctx, guard_all=True)
    quote = gate.quote(QuoteOnlyView(client, ctx["sleep"]), params)
    if quote is None:
        ctx["log"]("QUOTE FAILED (ledgered as a failed quote); nothing else was requested")
        return pc.RC_STOPPED
    line = read_entries(gate.ledger_path)[-1]
    payload = {"request": params.as_kwargs(), "quoted_usd": quote.usd,
               "billable_bytes": quote.billable_bytes, "ledger_ts": line.get("ts"),
               "session_id": gate.session_id, "position": position(gate)}
    if args.out:
        write_json(Path(args.out), payload)
    ctx["log"](f"QUOTED ${quote.usd:.6f} for {quote.billable_bytes:,} billable bytes "
               f"({params.start}..{params.end}); headroom on {pc.PILOT_ACCOUNT} "
               f"${payload['position']['account_headroom_usd']:.6f}")
    return pc.RC_OK


def _buy_main(args: argparse.Namespace, params: RequestParams, target: Path,
              ctx: dict[str, Any]) -> int:
    log = ctx["log"]
    short = pc.min_span_refusal(params.start)
    if short:
        raise pc.PilotRefused(short)
    target_usd = pc.margin_target(_balance(args))
    if args.approved_usd is None or args.approved_usd <= 0:
        raise pc.PilotRefused("--buy requires --approved-usd > 0 (the amount approved after the "
                              "balance check)")
    if not 0 < args.session_cap_usd <= pc.PILOT_ACCOUNT_CAP_USD:
        raise pc.PilotRefused(f"--session-cap-usd must be in (0, {pc.PILOT_ACCOUNT_CAP_USD}]")
    gate = build_gate(args.session_id, ctx["ledger"], ctx["access"], args.session_cap_usd)
    entries = read_entries(gate.ledger_path)
    earlier = other_purchases(entries, params)
    if earlier:
        raise pc.PilotRefused(
            f"{pc.PILOT_ACCOUNT} already holds {len(earlier)} committed pilot purchase(s) of "
            f"another request (first: {earlier[0]}): one purchase only, no second contract and "
            "no second buy (RD-01); nothing bought")
    state, commit = resume_state(entries, params, target, args.retry_download)
    out = record_path(ctx["runs"], args.root, params)
    if state == "done":
        log(f"{target.name}: already bought and settled; nothing requested")
        return pc.RC_OK
    if state == "settle_only":
        assert commit is not None
        quote = Quote(params_from_request(commit["request"]), float(commit["quoted_usd"]),
                      int(commit["billable_bytes"]))
        log(f"{target.name}: on disk with an open commit; settling without a new download")
        return _finish(args, params, target, gate, quote, None, out, ctx)
    quote = fresh_quote(entries, params, args.session_id, ctx["now"](),
                        args.max_quote_age_hours, args.approved_usd, target_usd)
    if not ctx["vendor"].is_dir():
        raise pc.PilotRefused(f"vendor root {ctx['vendor']} is missing (large storage mounted?)")
    gate.authorize(params, quote)  # session and acct-3 caps; a refusal is ledgered and raises
    log(f"authorized ${quote.usd:.6f} on {pc.PILOT_ACCOUNT}: {position(gate)}")
    client = _client(ctx, guard_all=False)
    try:
        gate.commit(quote, note=NOTE)
        log(f"committed ${quote.usd:.6f}; downloading to {target}.partial")
        download(client, params, target)
        log(f"downloaded {target.stat().st_size:,} bytes to {target}")
    except (DownloadError, ResumeStateError, OSError) as exc:
        print(f"RUN STOPPED ({type(exc).__name__}): {exc}. The commit stays in the ledger "
              "(pessimistic); see README for the resume.", file=sys.stderr)
        return pc.RC_STOPPED
    return _finish(args, params, target, gate, quote, client, out, ctx)


def _finish(args: argparse.Namespace, params: RequestParams, target: Path, gate: SpendGate,
            quote: Quote, client: Any, out: Path, ctx: dict[str, Any]) -> int:
    log = ctx["log"]
    try:
        billing = settle_download(gate, quote, target)
    except DeliveryCheckError as exc:
        print(f"RUN STOPPED ({type(exc).__name__}): {exc}", file=sys.stderr)
        return pc.RC_STOPPED
    record = write_record(out, args.root, params, target, gate, billing)
    log(f"settled ${billing['settled_usd']:.6f}; record {out} (sha256 {record['sha256']})")
    if client is not None:
        try:
            log(fetch_condition(client, params, ctx["runs"], ctx["sleep"]))
        except Exception as exc:  # noqa: BLE001 - named, never silent; the purchase is done
            log(f"WARNING: free dataset-condition fetch failed ({type(exc).__name__}: {exc})")
    ratio = billing["billed_over_quote_ratio"]
    if ratio is None or ratio > 1.0 + BILLED_OVER_QUOTE_STOP:
        print(f"RUN STOPPED: billed above the quote by more than 3% (delivered "
              f"{billing['delivered_record_bytes']:,} vs quoted "
              f"{billing['quoted_billable_bytes']:,} bytes); settled pro rata and recorded",
              file=sys.stderr)
        return pc.RC_STOPPED
    log(f"buy finished: {position(gate)}")
    return pc.RC_OK


def _span_main(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    log = ctx["log"]
    rule_target = pc.margin_target(_balance(args))
    target_usd = rule_target if args.target_usd is None else args.target_usd
    if not 0 < target_usd <= rule_target:
        raise pc.PilotRefused(f"--target-usd must be in (0, {rule_target:.2f}], the margin rule's "
                              f"TARGET for balance {args.balance_usd:.2f} (RS-08)")
    if args.end != pc.CUTOFF_BOUND:
        raise pc.PilotRefused(f"--span-search prices [start, {pc.CUTOFF_BOUND}) only")
    # the same request refusals, on the shortest span, before any call
    pc.check_request(pc.pilot_params(args.root, pc.start_bound(pc.LAST_PILOT_TRADE_DATE),
                                     dataset=args.dataset, schema=args.schema,
                                     symbol=args.symbol, stype_in=args.stype_in), args.root)
    cal = pc.calendar_for(args.root)
    gate = build_gate(pc.SPAN_SESSION_ID, ctx["ledger"], ctx["access"], 0.0)
    client = _client(ctx, guard_all=True)
    view = QuoteOnlyView(client, ctx["sleep"])
    try:
        listed = args.first_listed or resolve_first_listed(client, args.root, ctx["sleep"])
        first = first_candidate_day(listed, args.earliest, cal)
        candidates = span_candidates(cal, first, pc.MIN_SPAN_FIRST_TRADE_DATE)
        if not candidates:
            raise SpanSearchError(f"no whole trade date from {first} to "
                                  f"{pc.MIN_SPAN_FIRST_TRADE_DATE}: the minimum span cannot be "
                                  "bought (RS-07)")
        log(f"span search {args.root}: target ${target_usd:.2f} (balance "
            f"${args.balance_usd:.2f}), first listed {listed}, {len(candidates)} candidate first "
            f"trade dates {candidates[0]}..{candidates[-1]} (the minimum span starts "
            f"{pc.MIN_SPAN_FIRST_TRADE_DATE})")

        def cost(day: date) -> float:
            params = pc.check_request(pc.pilot_params(
                args.root, pc.start_bound(day), dataset=args.dataset, schema=args.schema,
                symbol=args.symbol, stype_in=args.stype_in), args.root)
            quote = gate.quote(view, params)
            if quote is None:
                raise SpanSearchError(f"the quote for first trade date {day} failed (ledgered)")
            return quote.usd

        result = span_search(candidates, cost, target_usd, log)
    except (SpanSearchError, pc.PilotRefused) as exc:
        print(f"SPAN SEARCH STOPPED ({type(exc).__name__}): {exc}; nothing was bought",
              file=sys.stderr)
        return pc.RC_STOPPED
    if result["feasible"]:
        result["trade_dates_in_span"] = len(span_candidates(
            cal, date.fromisoformat(result["first_trade_date"])))
    else:
        result["reason"] = (f"the minimum span [{pc.MIN_SPAN_FIRST_TRADE_DATE}, "
                            f"{pc.CUTOFF_BOUND}) costs more than TARGET ${target_usd:.2f}: buy "
                            "nothing (RS-07, RS-08)")
    result = {**result, "root": args.root, "first_listed": listed.isoformat(),
              "balance_usd": args.balance_usd, "approve_exactly_the_fresh_quote": True,
              "lower_bound": first.isoformat(), "session_id": gate.session_id,
              "calendar_coverage_start": cal.coverage[0].isoformat(), "bought": False}
    print(json.dumps(result, indent=1))
    if args.out:
        write_json(Path(args.out), result)
    if not result["feasible"]:
        log(f"SPAN PLAN: infeasible: {result['reason']}")
        return pc.RC_STOPPED
    log(f"SPAN PLAN: first trade date {result['first_trade_date']} (start {result['start']}, "
        f"end {result['end']}), {result['trade_dates_in_span']} trade dates, quoted "
        f"${result['cost_usd']:.6f} <= ${target_usd:.2f}; {len(result['quotes'])} quotes "
        f"ledgered under {gate.session_id}; nothing bought")
    return pc.RC_OK


if __name__ == "__main__":
    sys.exit(main())
