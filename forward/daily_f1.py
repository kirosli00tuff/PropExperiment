"""Daily driver of E22-F1 on IBKR data (Stage E.24, IBKRCoder).

    run         IBKR source -> frozen PaperRunner.run_date -> optional shadow route
    warmup      assemble the warm-up JSONL (2024-03-01 .. the day before the start date)
    probe       one contract's last daily bars, to see what this login can read (writes nothing)
    export-csv  write a warm-up file's prices in forward.sources' CSV format (runner --csv)
    ready       print the latest CME trade date whose cutoff has passed
    env-status  print each connection variable NAME with set/unset (never a value)

Connection settings come from the environment only (names in forward.ibkr_gateway.ENV_NAMES;
e.g. ``uv run --env-file .env ...``); nothing here reads .env or prints a value. ib_async is
needed only for run and warmup against a real gateway:
``uv run --with-requirements forward/requirements_broker.txt python -m forward.daily_f1 run ...``

Exit codes: 0 done; 2 source not ready or unavailable, a contract/convention error, a date the
holiday file lists, no --date and no --holidays, or a runner refusal such as an undeclared gap
(no record written); 3 the whole day is Missing and --accept-missing-day was not given (no
record); 4 the record was written but the shadow route failed (the E22-F1 ledger is
unaffected); 5 every contract of one exchange (the CBOT grains count as their own group) is
affirmed missing while others are priced and --accept-exchange-gap was not given (no record).

Dates (S3, wave 3): ``run`` takes the trade date from --date. Without --date it needs
--holidays FILE, the operator's copy of the published CME holiday calendar (one YYYY-MM-DD per
line, '#' comments, text after the date ignored); it then runs the latest ready trade date. A
date the file lists is never recorded (exit 2: declare it closed), and the listed dates inside
the gap since the ledger's last record are passed to the runner as declared closed.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time as _time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from forward import rolls as R
from forward.history import history_fingerprint, load_warmup
from forward.ibkr_gateway import (
    DEFAULT_MARKET_DATA_TYPE,
    ConnectionParams,
    Gateway,
    GatewaySession,
    IBKRError,
    Pacer,
    RetryPolicy,
    SourceUnavailable,
    Vendor,
    connect_live,
    env_status,
    live_vendor,
)
from forward.orders_ibkr import DEFAULT_SHADOW_CONFIG, ShadowRoute, load_shadow_config
from forward.runner import PaperRunner, RunnerConfig, RunnerError, load_tables
from forward.sources import Missing
from forward.sources_ibkr import (
    FIELD_LABEL,
    USE_RTH,
    WARMUP_FIRST,
    WHAT_TO_SHOW,
    ContractResolver,
    IBKRSettlementSource,
    assemble_rows,
    chicago_date,
    cutoff_utc,
    export_csv,
    fetch_warmup_prices,
    ib_end_of_day,
    is_ready,
    latest_ready_trade_date,
    rows_to_days,
    stale_open_rolls,
    utc_now,
    warmup_summary,
    write_warmup,
)

FORWARD = Path(__file__).resolve().parent
PACING_S = 1.0  # I5 / implication 6: at most about 1 historical request per second


@dataclass
class Deps:
    """Everything the driver touches outside the repo; tests inject mocks."""

    environ: Mapping[str, str] = field(default_factory=lambda: os.environ)
    gateway_factory: Callable[[], Gateway] = connect_live
    vendor_factory: Callable[[], Vendor] = live_vendor
    now: Callable[[], datetime] = utc_now
    sleep: Callable[[float], Any] = _time.sleep
    clock: Callable[[], float] = _time.monotonic
    policy: RetryPolicy = field(default_factory=RetryPolicy)
    pacing_s: float = PACING_S
    out: Callable[[str], Any] = print


def _config(args: argparse.Namespace) -> tuple[RunnerConfig, dict[str, float]]:
    multipliers, costs = load_tables(args.tables)
    with open(args.config, encoding="utf-8") as fh:
        strategy_config = json.load(fh)
    config = RunnerConfig(multipliers, costs, R.load_rolls(args.rolls), strategy_config)
    ticks = {k: float(v["tick"]) for k, v in strategy_config["instruments"].items()}
    return config, ticks


def _session(
    deps: Deps, *, need_account: bool, market_data_type: int | None = DEFAULT_MARKET_DATA_TYPE
) -> tuple[GatewaySession, Vendor]:
    params = ConnectionParams.from_env(deps.environ, need_account=need_account)
    vendor = deps.vendor_factory()
    pacer = Pacer(deps.pacing_s, clock=deps.clock, sleep=deps.sleep)
    session = GatewaySession(
        deps.gateway_factory(),
        params,
        readonly=not need_account,
        market_data_type=market_data_type,
        policy=deps.policy,
        pacer=pacer,
        sleep=deps.sleep,
        clock=deps.clock,
    )
    return session, vendor


class HolidayFileError(ValueError):
    """The holiday file is unreadable, empty or lists a non-date or a weekend day."""


def load_holidays(path: Path | str) -> frozenset[date]:
    """The operator's copy of the published CME holiday calendar: one YYYY-MM-DD per line,
    '#' comments and blank lines skipped, text after the date ignored (S3, wave 3)."""
    days = set()
    for n, raw in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        try:
            day = date.fromisoformat(line.split()[0])
        except ValueError:
            raise HolidayFileError(f"{path}:{n}: not a YYYY-MM-DD date") from None
        if day.weekday() >= 5:
            raise HolidayFileError(f"{path}:{n}: {day} is a weekend day, not a holiday weekday")
        days.add(day)
    if not days:
        raise HolidayFileError(f"{path}: no dates")
    return frozenset(days)


def _run_date(args: argparse.Namespace, deps: Deps) -> tuple[date | None, frozenset[date], str]:
    """(trade date, listed holidays, refusal); a refusal means exit 2 before any connection."""
    if not args.date and not args.holidays:
        return (
            None,
            frozenset(),
            (
                "give --date YYYY-MM-DD, or --holidays FILE (the published CME holiday calendar) "
                "to run the latest ready trade date; no record written"
            ),
        )
    try:
        holidays = load_holidays(args.holidays) if args.holidays else frozenset()
    except (OSError, HolidayFileError) as exc:
        return None, frozenset(), f"holiday file refused: {exc}; no record written"
    day = date.fromisoformat(args.date) if args.date else latest_ready_trade_date(deps.now())
    if day in holidays:
        return (
            day,
            holidays,
            (
                f"{day} is listed in {args.holidays} as an exchange holiday: declare it closed; "
                "no record written"
            ),
        )
    return day, holidays, ""


def _declared_closed(
    args: argparse.Namespace, runner: PaperRunner, day: date, holidays: frozenset[date]
) -> list[date]:
    """--closed, plus the listed holidays strictly inside the gap since the last record."""
    closed = {date.fromisoformat(d) for d in args.closed}
    records = runner.ledger.records()
    if records and holidays:
        last = date.fromisoformat(records[-1]["date"])
        closed |= {h for h in holidays if last < h < day}
    return sorted(closed)


def cmd_run(args: argparse.Namespace, deps: Deps) -> int:
    config, ticks = _config(args)
    if bool(args.warmup) == bool(args.no_warmup):
        deps.out("give exactly one of --warmup FILE or --no-warmup; no record written")
        return 2
    day, holidays, refusal = _run_date(args, deps)
    if refusal:
        deps.out(refusal)
        return 2
    shadow_cfg = load_shadow_config(args.shadow_config)
    warmup = load_warmup(args.warmup) if args.warmup else ()
    session, vendor = _session(
        deps, need_account=shadow_cfg.enabled, market_data_type=args.market_data_type
    )
    try:
        resolver = ContractResolver(
            session, vendor, config.rolls, config_multipliers=config.multipliers
        )
        source = IBKRSettlementSource(
            session,
            resolver,
            config.rolls,
            instruments=config.instruments,
            now=deps.now,
            provenance_path=args.provenance,
        )
        try:
            answer = source.settlements(day)
        except IBKRError as exc:
            deps.out(f"{day}: no record written: {type(exc).__name__}: {exc}")
            return 2
        if isinstance(answer, Missing) and not args.accept_missing_day:
            deps.out(
                f"{day}: whole day Missing ({answer.reason}); no record written. "
                "Declare it closed in the next run, or rerun with --accept-missing-day."
            )
            return 3
        gaps = source.exchange_gaps(day)
        if gaps and not args.accept_exchange_gap:
            listed = "; ".join(f"{g}: {', '.join(c)}" for g, c in gaps.items())
            deps.out(
                f"{day}: every contract of {sorted(gaps)} is affirmed missing while other "
                f"exchanges are priced ({listed}); an exchange holiday? no record written. "
                "Declare the day closed, or rerun with --accept-exchange-gap."
            )
            return 5
        runner = PaperRunner(args.ledger, source, config, warmup=warmup)
        try:
            record = runner.run_date(
                day, declared_closed=_declared_closed(args, runner, day, holidays)
            )
        except RunnerError as exc:  # N3 (wave 3): e.g. an undeclared gap; no traceback
            deps.out(f"{day}: no record written: RunnerError: {exc}")
            return 2
        deps.out(
            f"{record['date']} net_pnl={record['net_pnl']:.2f} fills={len(record['fills'])} "
            f"rolls={len(record['rolls'])} flags={len(record['flags'])} "
            f"sha={record['record_sha256'][:12]}"
        )
        if args.csv_mirror:
            export_csv({day: answer}, args.csv_mirror)
        if not shadow_cfg.enabled:
            return 0
        return _shadow(shadow_cfg, session, resolver, vendor, args, ticks, day, deps)
    finally:
        session.close()


def _shadow(cfg, session, resolver, vendor, args, ticks, day, deps) -> int:  # noqa: ANN001
    try:
        route = ShadowRoute(
            cfg,
            session,
            resolver,
            vendor,
            e22_ledger_path=args.ledger,
            ticks=ticks,
            clock=deps.clock,
        )
        rec = route.run(day)
    except Exception as exc:  # the E22-F1 record is already written; report and exit 4
        text = session.redact(f"{type(exc).__name__}: {exc}")
        deps.out(f"{day}: E22-F1 record kept; shadow route failed: {text}")
        return 4
    deps.out(
        f"{day}: shadow orders={len(rec['orders'])} fills={len(rec['fills'])} "
        f"late_fills={len(rec['late_fills'])}"
    )
    return 0


def previous_weekday(day: date) -> date:
    day -= timedelta(days=1)
    while day.weekday() >= 5:
        day -= timedelta(days=1)
    return day


def cmd_warmup(args: argparse.Namespace, deps: Deps) -> int:
    config, _ = _config(args)
    start = date.fromisoformat(args.start)
    first = date.fromisoformat(args.first)
    last = previous_weekday(start)
    if Path(args.out).exists():
        deps.out(f"{args.out} exists; a warm-up file is never overwritten")
        return 2
    now = deps.now()
    if not is_ready(last, now):
        deps.out(f"{last} is not final before {cutoff_utc(last).isoformat()}; warm-up refused")
        return 2
    session, vendor = _session(deps, need_account=False, market_data_type=args.market_data_type)
    try:
        resolver = ContractResolver(
            session, vendor, config.rolls, config_multipliers=config.multipliers
        )
        prices, notes = fetch_warmup_prices(
            session,
            resolver,
            config.rolls,
            first,
            last,
            today=chicago_date(now),
            instruments=config.instruments,
        )
    except IBKRError as exc:
        deps.out(f"warm-up not written: {type(exc).__name__}: {exc}")
        return 2
    finally:
        session.close()
    rows = assemble_rows(prices, config.rolls, first, last)
    per_instrument = warmup_summary(
        rows,
        config.rolls,
        config.instruments,
        warmup_diffs=int(config.strategy_config["warmup_diffs"]["value"]),
    )
    stale = stale_open_rolls(per_instrument, last)
    if stale:  # S1 (wave 3): a reference stuck on an old contract; nothing is written
        detail = "; ".join(
            f"{i}: reference {per_instrument[i]['last_reference']}, last priced "
            f"{per_instrument[i]['last_date']}"
            for i in stale
        )
        deps.out(f"warm-up not written: open roll with a stale last priced date ({detail})")
        return 2
    digest = write_warmup(rows, args.out)
    summary = {
        "first": first.isoformat(),
        "last": last.isoformat(),
        "start": start.isoformat(),
        "sha256": digest,
        "history_fingerprint": history_fingerprint(rows),
        "instruments": per_instrument,
        "notes": [n.__dict__ for n in notes],
    }
    Path(args.summary or f"{args.out}.summary.json").write_text(
        json.dumps(summary, indent=1, sort_keys=True) + "\n", encoding="utf-8"
    )
    if args.csv:
        export_csv(rows_to_days(rows), args.csv)
    deps.out(f"warm-up {args.out} rows={len(rows)} sha256={digest}")
    for inst, s in summary["instruments"].items():
        deps.out(
            f"  {inst}: rows={s['rows']} first={s['first_date']} "
            f"live_at_start={s['live_at_start']} open_roll={s['open_roll']}"
        )
    return 0


def cmd_export_csv(args: argparse.Namespace, deps: Deps) -> int:
    n = export_csv(rows_to_days(load_warmup(args.warmup)), args.out)
    deps.out(f"{args.out}: {n} rows written")
    return 0


def cmd_ready(args: argparse.Namespace, deps: Deps) -> int:
    now = datetime.fromisoformat(args.now) if args.now else deps.now()
    deps.out(latest_ready_trade_date(now).isoformat())
    return 0


def cmd_env_status(args: argparse.Namespace, deps: Deps) -> int:
    for name, state in env_status(deps.environ).items():
        deps.out(f"{name}: {state}")
    return 0


def _common(p: argparse.ArgumentParser) -> None:
    p.add_argument("--tables", default=str(FORWARD / "tables_f1.json"))
    p.add_argument("--config", default=str(FORWARD / "config_f1.json"))
    p.add_argument("--rolls", default=str(R.DEFAULT_ROLLS_PATH))
    p.add_argument(
        "--market-data-type",
        type=int,
        choices=(1, 2, 3, 4),
        default=DEFAULT_MARKET_DATA_TYPE,
        help="reqMarketDataType(N) after each connect, before any historical request "
        "(default 3 = delayed; factcheck C1)",
    )


def cmd_probe(args: argparse.Namespace, deps: Deps) -> int:
    """One contract's last daily bars, fetched with end="" and with the explicit end time of the
    trade date (N2, wave 3: confirms the endDateTime form), the outcome printed. Nothing is
    written unless --log FILE: then every bar is appended there with its fetch time and age,
    and a bar already logged with another close is printed as changed (S4, wave 3: the same
    bar at different ages, the evidence for the price-definition decision)."""
    config, _ = _config(args)
    day = date.fromisoformat(args.date) if args.date else latest_ready_trade_date(deps.now())
    cid = R.active_contract(config.rolls[args.instrument], day)
    session, vendor = _session(deps, need_account=False, market_data_type=args.market_data_type)
    head = f"probe {args.instrument} {cid} market_data_type={args.market_data_type}"
    try:
        resolver = ContractResolver(session, vendor, config.rolls)
        rc = resolver.resolve(args.instrument, cid)
        answers = {}
        for end in ("", ib_end_of_day(day)):
            answers[end] = session.daily_bars(
                f"probe {cid} end={end or 'now'}",
                rc.contract,
                end=end,
                duration="10 D",
                what_to_show=WHAT_TO_SHOW,
                use_rth=USE_RTH,
            )
        fetched = deps.now()
    except IBKRError as exc:
        deps.out(f"probe {args.instrument} {cid}: {type(exc).__name__}: {exc}")
        return 2
    finally:
        session.close()
    entries = [
        _probe_entry(args, rc, bar, end, fetched) for end, bars in answers.items() for bar in bars
    ]
    if args.log:
        for line in _probe_log(Path(args.log), entries):
            deps.out(line)
    consistent = _explicit_end_consistent(answers, day)
    dates = sorted(b.date for b in answers[""])
    deps.out(
        f"{head}: bars={len(dates)} first={dates[0]} last={dates[-1]} "
        f"explicit_end={'consistent' if consistent else 'INCONSISTENT'}"
    )
    return 0 if consistent else 2


def _probe_entry(args, rc, bar, end: str, fetched: datetime) -> dict[str, Any]:  # noqa: ANN001
    age = (fetched - cutoff_utc(bar.date)).total_seconds() / 3600
    return {
        "probe_utc": fetched.isoformat(),
        "instrument": rc.instrument,
        "contract_id": rc.contract_id,
        "con_id": rc.con_id,
        "bar_date": bar.date.isoformat(),
        "close_ib": float(bar.close),
        "age_h": round(age, 2),  # hours after the bar date's cutoff (negative: session open)
        "request_end": end,
        "field": FIELD_LABEL,
        "what_to_show": WHAT_TO_SHOW,
        "use_rth": USE_RTH,
        "market_data_type": args.market_data_type,
    }


def _probe_log(path: Path, entries: list[dict[str, Any]]) -> list[str]:
    """Append the entries; return a line per bar whose close differs from an earlier fetch."""
    seen: dict[tuple[int, str, str], dict[str, Any]] = {}
    if path.exists():
        for raw in path.read_text(encoding="utf-8").splitlines():
            e = json.loads(raw)
            seen.setdefault((e["con_id"], e["bar_date"], e["request_end"]), e)
    lines = []
    for e in entries:
        first = seen.get((e["con_id"], e["bar_date"], e["request_end"]))
        if first is not None and first["close_ib"] != e["close_ib"]:
            lines.append(
                f"  changed {e['contract_id']} {e['bar_date']} (end={e['request_end'] or 'now'}): "
                f"{first['close_ib']!r} at age {first['age_h']} h -> {e['close_ib']!r} at age "
                f"{e['age_h']} h"
            )
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write("".join(json.dumps(e, sort_keys=True) + "\n" for e in entries))
    return lines


def _explicit_end_consistent(answers: Mapping[str, Sequence[Any]], day: date) -> bool:
    """The explicit-end answer ends at the open-end answer's last bar on or before ``day``,
    and the two agree on every common date (N2: the endDateTime form is read as intended)."""
    open_end = {b.date: float(b.close) for b in answers[""]}
    explicit = {b.date: float(b.close) for b in next(v for k, v in answers.items() if k)}
    upto = [d for d in open_end if d <= day]
    if not explicit or not upto or max(explicit) != max(upto):
        return False
    return all(open_end[d] == c for d, c in explicit.items() if d in open_end)


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="python -m forward.daily_f1", description=__doc__.split("\n")[0]
    )
    sub = ap.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run", help="one trade date through the frozen runner")
    _common(run)
    run.add_argument("--ledger", required=True)
    run.add_argument("--warmup", help="JSONL of HistoryRow objects (the approved warm-up)")
    run.add_argument(
        "--no-warmup",
        action="store_true",
        help="run without a warm-up (it is fingerprinted into every record: tests only)",
    )
    run.add_argument(
        "--date", help="trade date YYYY-MM-DD (required unless --holidays: latest ready)"
    )
    run.add_argument(
        "--holidays",
        help="the operator's copy of the published CME holiday calendar (YYYY-MM-DD per line)",
    )
    run.add_argument("--closed", nargs="*", default=[], help="declared exchange-closed weekdays")
    run.add_argument("--provenance", help="append-only JSONL of the bars used")
    run.add_argument("--csv-mirror", help="append the day to a forward.sources CSV")
    run.add_argument("--shadow-config", default=str(DEFAULT_SHADOW_CONFIG))
    run.add_argument("--accept-missing-day", action="store_true")
    run.add_argument(
        "--accept-exchange-gap",
        action="store_true",
        help="record a day on which one exchange (or the CBOT grains) is wholly missing",
    )
    run.set_defaults(fn=cmd_run)
    wu = sub.add_parser("warmup", help="assemble the warm-up history")
    _common(wu)
    wu.add_argument("--start", required=True, help="the start date (first ledger date)")
    wu.add_argument("--first", default=WARMUP_FIRST.isoformat())
    wu.add_argument("--out", required=True)
    wu.add_argument("--summary")
    wu.add_argument("--csv", help="also export the warm-up prices to this CSV")
    wu.set_defaults(fn=cmd_warmup)
    ex = sub.add_parser("export-csv", help="warm-up JSONL -> forward.sources CSV")
    ex.add_argument("--warmup", required=True)
    ex.add_argument("--out", required=True)
    ex.set_defaults(fn=cmd_export_csv)
    rd = sub.add_parser("ready", help="latest CME trade date past its cutoff")
    rd.add_argument("--now", help="ISO datetime with offset (default: now)")
    rd.set_defaults(fn=cmd_ready)
    pr = sub.add_parser("probe", help="can this login read daily bars? (writes nothing)")
    _common(pr)
    pr.add_argument("--instrument", default="MNQ")
    pr.add_argument("--date", help="trade date whose reference contract is probed")
    pr.add_argument("--log", help="append every bar with its fetch time and age (JSONL)")
    pr.set_defaults(fn=cmd_probe)
    es = sub.add_parser("env-status", help="connection variable names: set/unset")
    es.set_defaults(fn=cmd_env_status)
    return ap


def main(argv: Sequence[str] | None = None, deps: Deps | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        return args.fn(args, deps or Deps())
    except SourceUnavailable as exc:
        (deps or Deps()).out(f"no record written: {type(exc).__name__}: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
