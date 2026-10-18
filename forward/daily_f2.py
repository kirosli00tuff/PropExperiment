"""E22-F2 daily driver: source -> forward.runner_f2 -> optional shadow route (F2BookCoder, E.24).

    uv run python -m forward.daily_f2 run --date YYYY-MM-DD --ledger L.jsonl --warmup W.jsonl \
        [--closed YYYY-MM-DD ...] [--csv BARS.csv] [--shadow forward/shadow_f2.json]
    uv run python -m forward.daily_f2 warmup --start YYYY-MM-DD --out W.jsonl

``run`` processes one session. Late corporate actions (prereg section 6) are offered to the runner:
what the Alpaca source's corporate actions endpoint now publishes over the recorded sessions, plus a
hand-entered ``--late-ca`` JSON list; the runner books each at most once and skips those already
inside a recorded return. The bars come from forward.sources_alpaca when both credential
environment variables are set (names in forward.sources_alpaca; values are never read here),
otherwise from a CSV in forward.etf_bars format (``--csv``). SourceUnavailable / NotReady write
nothing (exit code 3: retry later). After the E22-F2 record is stored, the shadow route
(forward/orders_alpaca.py) runs only when its config says ``"enabled": true``; it reads the stored
record and nothing else, and never touches the E22-F2 ledger. A shadow failure does not change the
E22-F2 record (exit code 4).

``--feed`` selects the operative data feed: the config's primary ("sip") unless the first
connection session found SIP refused, then the registered fallback ("iex"). config_f2.json holds
both and is never edited; every record stores the feed it used, and the book refuses a feed change
after the first record.

``warmup`` reads the source's raw daily bars and corporate actions of the 11 ETFs and BIL from
2024-03-01 to the session before ``--start`` (prereg section 7; Alpaca's "all" adjustment is not
used), writes the warm-up JSONL (refusing to overwrite) and ``<out>.sha256`` in
``sha256sum -c`` form, and prints the sha256 with each symbol's first date and row count.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Callable, Mapping, Sequence
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from forward.etf_bars import CsvEtfSource, EtfBarSource, SourceUnavailable, load_etf_warmup
from forward.runner_f2 import (
    DEFAULT_CONFIG,
    DEFAULT_TABLES,
    BookConfig,
    PaperBookF2,
    load_book_config,
    summary_line,
)

HERE = Path(__file__).resolve().parent
DEFAULT_SHADOW = HERE / "shadow_f2.json"
EXIT_SOURCE_UNAVAILABLE = 3
EXIT_SHADOW_FAILED = 4


def credential_names() -> tuple[str, str]:
    from forward import sources_alpaca

    return sources_alpaca.KEY_ID_ENV, sources_alpaca.SECRET_KEY_ENV


def credentials_present(environ: Mapping[str, str] | None = None) -> bool:
    """True when both Alpaca paper credential variables are set (values are not inspected)."""
    env = os.environ if environ is None else environ
    return all(str(env.get(name, "")).strip() for name in credential_names())


def make_source(
    cfg: BookConfig,
    *,
    csv_path: Path | str | None,
    closed: Sequence[date] = (),
    environ: Mapping[str, str] | None = None,
    data_client_factory: Callable[[], Any] | None = None,
    feed: str | None = None,
) -> EtfBarSource:
    """Alpaca when credentials exist (on ``feed``, default the config's primary feed), reading
    ``cfg.read_universe`` (the 11 ETFs, BIL and the replacement benchmark SGOV, prereg section 6),
    else the CSV source (``csv_path`` required then)."""
    if credentials_present(environ):
        from forward import sources_alpaca

        client = (data_client_factory or sources_alpaca.make_data_client)()
        return sources_alpaca.AlpacaEtfSource(
            cfg.read_universe, client, feed=feed or cfg.primary_feed, closed_dates=closed
        )
    if csv_path is None:
        raise SystemExit("no Alpaca credentials in the environment and no --csv given")
    return CsvEtfSource(csv_path, cfg.read_universe)


def build_shadow(shadow_path: Path | str | None, ledger_path: Path | str, **route_kwargs: Any):
    """The shadow route when its config exists and is enabled, else None."""
    if shadow_path is None or not Path(shadow_path).exists():
        return None
    from forward import orders_alpaca

    shadow_cfg = orders_alpaca.load_shadow_config(shadow_path)
    if not shadow_cfg.enabled:
        return None
    return orders_alpaca.ShadowRoute(shadow_cfg, ledger_path, **route_kwargs)


LATE_CA_LOOKBACK_DAYS = 31  # the query starts this far before the first record; older ex_dates
# fall in no recorded session and are skipped by the runner


def actions_as_late_input(actions: Any) -> list[dict[str, Any]]:
    """forward.sources_alpaca.CorporateActions -> runner_f2 late-action dicts (ex_date known)."""
    out = []
    for a in (*actions.booked, *actions.other):
        if a.ex_date is None:
            continue
        value = a.ratio if "split" in a.kind else a.amount
        out.append(
            {
                "symbol": a.symbol,
                "type": a.kind,
                "ex_date": a.ex_date.isoformat(),
                "amount_or_ratio": float(value) if value is not None else 0.0,
            }
        )
    return out


def late_actions_for(
    book: PaperBookF2, trade_date: date, manual: Sequence[Mapping[str, Any]] = ()
) -> list[dict[str, Any]] | None:
    """Corporate actions to offer the runner as late (section 6): what the source's corporate
    actions endpoint now publishes over the recorded sessions, plus ``manual`` entries. None for
    a date already recorded (a re-run reuses the stored input)."""
    records = book.ledger.records()
    if any(r["date"] == trade_date.isoformat() for r in records):
        return None
    found = list(manual)
    fetch = getattr(book.source, "corporate_actions", None)
    if records and callable(fetch):
        first = date.fromisoformat(records[0]["date"])
        last = date.fromisoformat(records[-1]["date"])
        found += actions_as_late_input(fetch(first - timedelta(days=LATE_CA_LOOKBACK_DAYS), last))
    return found


def run_session(
    book: PaperBookF2,
    trade_date: date,
    *,
    declared_closed: Sequence[date] = (),
    shadow: Any = None,
    late_actions: Sequence[Mapping[str, Any]] | None = None,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """One session: the E22-F2 record (stored), then the shadow route on that record only."""
    record = book.run_date(trade_date, declared_closed=declared_closed, late_actions=late_actions)
    shadow_record = shadow.run(dict(record)) if shadow is not None else None
    return record, shadow_record


def _cmd_run(args: argparse.Namespace) -> int:
    cfg = load_book_config(args.config, args.tables)
    closed = [date.fromisoformat(x) for x in args.closed]
    feed = args.feed or cfg.primary_feed
    source = make_source(cfg, csv_path=args.csv, closed=closed, feed=feed)
    book = PaperBookF2(args.ledger, source, cfg, warmup=load_etf_warmup(args.warmup), feed=feed)
    shadow = build_shadow(args.shadow, args.ledger)
    trade_date = date.fromisoformat(args.date)
    manual = json.loads(Path(args.late_ca).read_text(encoding="utf-8")) if args.late_ca else []
    try:
        late = late_actions_for(book, trade_date, manual)
        record = book.run_date(trade_date, declared_closed=closed, late_actions=late)
    except SourceUnavailable as exc:
        print(f"source unavailable, no record written: {exc}", file=sys.stderr)
        return EXIT_SOURCE_UNAVAILABLE
    print(summary_line(record))
    if shadow is None:
        return 0
    try:
        out = shadow.run(dict(record))
    except Exception as exc:  # noqa: BLE001 (the E22-F2 record is already stored and unaffected)
        print(
            f"shadow route failed (E22-F2 record unaffected): {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return EXIT_SHADOW_FAILED
    if out is not None:
        print(f"shadow {out['date']} orders={len(out['orders'])} fills={len(out['fills'])}")
    return 0


def _cmd_warmup(args: argparse.Namespace) -> int:
    from forward import sources_alpaca

    cfg = load_book_config(args.config, args.tables)
    if not credentials_present():
        raise SystemExit("the warm-up read needs the Alpaca paper credential variables")
    source = sources_alpaca.AlpacaEtfSource(
        cfg.universe, sources_alpaca.make_data_client(), feed=args.feed or cfg.primary_feed
    )
    result = source.fetch_warmup(date.fromisoformat(args.start))
    digest = sources_alpaca.write_warmup(result, args.out)
    out = Path(args.out)
    sha_path = out.with_name(out.name + ".sha256")
    with open(sha_path, "x", encoding="ascii") as fh:
        fh.write(f"{digest}  {out.name}\n")
    print(f"warm-up {out} sha256 {digest} rows {len(result.rows)}")
    for s in cfg.universe:
        print(
            f"  {s}: first {result.first_date[s]} rows {result.row_count[s]} "
            f"gaps {len(result.gaps.get(s, ()))}"
        )
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="python -m forward.daily_f2", description=__doc__.split("\n")[0]
    )
    sub = ap.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run", help="process one session")
    run.add_argument("--date", required=True, help="session date YYYY-MM-DD (America/New_York)")
    run.add_argument("--ledger", required=True)
    run.add_argument("--warmup", required=True, help="warm-up JSONL (forward.etf_bars format)")
    run.add_argument("--closed", nargs="*", default=[], help="declared exchange-closed weekdays")
    run.add_argument("--csv", help="bar CSV, used when no Alpaca credentials are set")
    run.add_argument("--shadow", default=str(DEFAULT_SHADOW), help="shadow route config JSON")
    run.add_argument(
        "--late-ca",
        help="JSON list of late corporate actions entered by hand "
        "({symbol, type, ex_date, amount_or_ratio}); the Alpaca source adds its own",
    )
    warm = sub.add_parser("warmup", help="write the warm-up file and its sha256")
    warm.add_argument("--start", required=True, help="the start date (first ledger session)")
    warm.add_argument("--out", required=True)
    for p in (run, warm):
        p.add_argument(
            "--feed",
            help="operative data feed: the config's primary (default) or its "
            "registered fallback; fixed before the first record and stored in each record",
        )
        p.add_argument("--config", default=str(DEFAULT_CONFIG))
        p.add_argument("--tables", default=str(DEFAULT_TABLES))
    args = ap.parse_args(argv)
    return _cmd_run(args) if args.cmd == "run" else _cmd_warmup(args)


if __name__ == "__main__":
    sys.exit(main())


__all__ = [
    "actions_as_late_input",
    "build_shadow",
    "credential_names",
    "credentials_present",
    "late_actions_for",
    "main",
    "make_source",
    "run_session",
]
