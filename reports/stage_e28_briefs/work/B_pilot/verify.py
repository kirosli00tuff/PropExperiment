"""Stage E.28 Part B: verify the downloaded pilot file(s) and write a manifest (JSON and .md).

    uv run python reports/stage_e28_briefs/work/B_pilot/verify.py --root ROOT \\
        --dbn <file.dbn.zst> [...] --out <manifest.json> --purchase-record JSON [--tick TICK]

--purchase-record is required (RD-03): without it, or when the record cannot be read or holds no
sha256, nothing is opened (exit 2). Every --dbn file gets its own hard check
sha256_matches_purchase_record against the record (one purchase is one file, so with two or more
files at most one can match; none is ever skipped).

Per file: path, size, sha256, the DBN header (dataset, schema, stype, symbols, start, end,
symbology), record counts by record type and by action (the store iterated in chunks), flag
counts, first and last ts_event, the trade dates covered, and per trade date: records, trades,
first and last ts_event, the instrument id(s) behind ROOT.v.0 from the header's symbology and
those seen in the records, bad-flag and crossed/locked/empty counts, the largest gap in
MAIN-session records, and the date's exclusions under spec section 2.

Checks. Hard (exit 1 when any fails): the file name and folder are the pilot's and its range
ends by 2024-02-29T22:00:00Z; the header describes the pilot request; no record with ts_event at
or after 2024-02-29T23:00:00Z, the 17:00 CT open of trade date 2024-03-01 (RS-01; records in
[22:00Z, 23:00Z), the maintenance hour, are counted as info); every record's instrument id is in
the header's symbology;
records arrive in ts_recv order (no record after its trade date was closed); every file's sha256
matches the purchase record; every price is a whole tick (when --tick is given). Data
quality (exit 3 when only these fail): no gap above 60 s in MAIN-session records on any date
that no other rule of spec section 2 excludes (such dates are excluded by measure.py). Reported
only: bad-flag record counts. A file whose name or folder is refused is not opened (exit 2).
"""
# ruff: noqa: I001 - pilot_common is imported first on purpose (sys.path)

from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pilot_common as pc  # first: puts the repo root on sys.path
import pilot_stream as ps
from data.pull_universe import file_sha256  # noqa: E402

RC_QUALITY = 3
CUTOFF_CHECK = "no_record_at_or_after_2024-02-29T23:00Z_open_of_trade_date_2024-03-01"


def _check(name: str, severity: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"name": name, "severity": severity, "passed": bool(passed), "detail": detail}


def _iso(ns: int | None) -> str | None:
    return None if ns is None else pc.iso_ns(ns)


def header(meta: Any, root: str) -> dict[str, Any]:
    return {"dataset": str(meta.dataset), "schema": str(meta.schema),
            "stype_in": str(meta.stype_in), "stype_out": str(getattr(meta, "stype_out", "")),
            "symbols": list(meta.symbols), "start": _iso(int(meta.start)),
            "end": None if meta.end is None else _iso(int(meta.end)),
            "mappings": {k: [{"start_date": str(e["start_date"]), "end_date": str(e["end_date"]),
                              "symbol": str(e["symbol"])} for e in v]
                         for k, v in (meta.mappings or {}).items()}}


def day_row(book: ps.DayBook, mapped: list[str]) -> dict[str, Any]:
    c = book.counts
    return {"date": book.day.isoformat(), "records": c.get("records", 0),
            "trades": c.get("trades", 0), "first_ts_event": _iso(book.first_ts_event),
            "last_ts_event": _iso(book.last_ts_event),
            "main_max_gap_s": None if book.main_max_gap_ns is None
            else book.main_max_gap_ns / pc.NS,
            "main_records": book.main_records,
            "instrument_ids_mapped": mapped, "instrument_ids_records": book.instrument_ids,
            "dropped_bad_flag_records": c.get("dropped_bad_flag_records", 0),
            "dropped_bad_ts_recv": c.get("dropped_bad_ts_recv", 0),
            "dropped_maybe_bad_book": c.get("dropped_maybe_bad_book", 0),
            "records_crossed": c.get("records_crossed", 0),
            "records_locked": c.get("records_locked", 0),
            "records_empty_side": c.get("records_empty_side", 0),
            "off_tick_prices": c.get("off_tick_prices", 0),
            "trades_side_A": c.get("trades_side_A", 0), "trades_side_B": c.get("trades_side_B", 0),
            "trades_side_N": c.get("trades_side_N", 0),
            "sequence_inversions": c.get("sequence_inversions", 0),
            "ts_event_inversions": c.get("ts_event_inversions", 0)}


def verify_file(path: Path, root: str, tick_1e9: int, chunk_records: int,
                expected_sha256: str) -> dict[str, Any]:
    cal = pc.calendar_for(root)
    store = ps.open_store(path)
    meta = store.metadata
    meta_bad = pc.metadata_refusals(meta, root)
    out: dict[str, Any] = {"path": str(path), "bytes": path.stat().st_size,
                           "sha256": file_sha256(path), "header": header(meta, root)}
    checks = [_check("metadata_is_the_pilot_request", "hard", not meta_bad, meta_bad),
              _check("sha256_matches_purchase_record", "hard",
                     out["sha256"] == expected_sha256, expected_sha256)]  # RD-03: every file
    if meta_bad:
        return {**out, "checks": checks, "days": []}
    intervals = list((meta.mappings or {}).get(pc.symbol_for(root), []))
    cover_lo, cover_hi = int(meta.start), int(meta.end)
    stats = ps.FileStats()
    plans: dict[date, pc.DayPlan] = {}

    def plan_for(day: date) -> pc.DayPlan:
        return plans.setdefault(day, pc.build_day_plan(cal, day))

    rows = []
    for book in ps.iter_days(store, plan_for, lambda d: True, tick_1e9,
                             chunk_records=chunk_records, stats=stats):
        plan = plans[book.day]
        lo = plan.open_lo if plan.open_lo is not None else pc.day_window_ns(book.day)[0]
        hi = plan.open_hi if plan.open_hi is not None else pc.day_window_ns(book.day)[1]
        rows.append(day_row(book, pc.mapped_ids(intervals, lo, hi)))
    _add_exclusions(rows, plans, cal, cover_lo, cover_hi)
    out.update({"records": stats.records, "records_by_rtype": stats.rtype,
                "records_by_action": stats.action, "flag_counts": stats.flags,
                "first_ts_event": _iso(stats.first_ts_event),
                "last_ts_event": _iso(stats.last_ts_event), "max_ts_recv": _iso(stats.max_ts_recv),
                "trade_dates_with_records": [r["date"] for r in rows], "days": rows})
    checks += _record_checks(stats, rows, tick_1e9 > 1)
    return {**out, "checks": checks}


def _add_exclusions(rows: list[dict[str, Any]], plans: dict[date, pc.DayPlan], cal: Any,
                    cover_lo: int, cover_hi: int) -> None:
    ids = {date.fromisoformat(r["date"]): pc.ordered_union(r["instrument_ids_mapped"],
                                                           r["instrument_ids_records"])
           for r in rows}
    rolls = pc.roll_exclusions(sorted(ids), ids, cal)
    for r in rows:
        day = date.fromisoformat(r["date"])
        reasons = pc.static_exclusions(plans[day], cover_lo, cover_hi)
        if day in rolls:
            reasons.append(rolls[day])
        r["excluded_by_other_rules"] = reasons
        gap = r["main_max_gap_s"]
        r["main_gap_gt_60s"] = gap is not None and gap > pc.MAX_MAIN_GAP_NS / pc.NS


def _record_checks(stats: ps.FileStats, rows: list[dict[str, Any]],
                   tick_given: bool) -> list[dict[str, Any]]:
    unmapped = {r["date"]: sorted(set(r["instrument_ids_records"])
                                  - set(r["instrument_ids_mapped"]))
                for r in rows if set(r["instrument_ids_records"]) - set(r["instrument_ids_mapped"])}
    gaps = [r["date"] for r in rows if r["main_gap_gt_60s"] and not r["excluded_by_other_rules"]]
    out = [
        _check(CUTOFF_CHECK, "hard", stats.records_at_or_after_cutoff_open == 0,
               stats.records_at_or_after_cutoff_open),
        _check("records_in_maintenance_hour_2024-02-29T22-23Z", "info", True,
               stats.records_in_cutoff_maintenance_hour),
        _check("record_instrument_ids_in_symbology", "hard", not unmapped, unmapped),
        _check("records_in_ts_recv_order", "hard",
               stats.late_records_dropped == 0 and stats.records_outside_day_range == 0,
               {"late_records": stats.late_records_dropped,
                "outside_day_range": stats.records_outside_day_range}),
        _check("main_session_gap_le_60s", "quality", not gaps,
               {"dates_otherwise_included_with_gap_gt_60s": gaps}),
        _check("bad_flag_records", "info", True,
               {k: stats.flags.get(k, 0) for k in ("F_BAD_TS_RECV", "F_MAYBE_BAD_BOOK")}),
        _check("trades_by_aggressor_side", "info", True,
               {k: sum(r[f"trades_side_{k}"] for r in rows) for k in ("A", "B", "N")}),
    ]
    if tick_given:
        off = {r["date"]: r["off_tick_prices"] for r in rows if r["off_tick_prices"]}
        out.append(_check("prices_on_tick_grid", "hard", not off, off))
    return out


def exit_code(files: list[dict[str, Any]]) -> int:
    checks = [c for f in files for c in f["checks"]]
    if any(not c["passed"] and c["severity"] == "hard" for c in checks):
        return pc.RC_STOPPED
    if any(not c["passed"] and c["severity"] == "quality" for c in checks):
        return RC_QUALITY
    return pc.RC_OK


def render_markdown(manifest: dict[str, Any]) -> str:
    lines = [f"# Stage E.28 pilot data manifest: {manifest['root']}\n",
             f"Written {manifest['written']}; exit code {manifest['exit_code']}.\n"]
    for f in manifest["files"]:
        lines += [f"## {Path(f['path']).name}\n", f"- path: `{f['path']}`",
                  f"- bytes: {f['bytes']:,}; sha256 `{f['sha256']}`",
                  f"- header: {f['header']['dataset']} {f['header']['schema']} "
                  f"{f['header']['symbols']} {f['header']['start']} .. {f['header']['end']}",
                  f"- records: {f.get('records', 0):,}; by rtype {f.get('records_by_rtype')}; "
                  f"by action {f.get('records_by_action')}",
                  f"- flags: {f.get('flag_counts')}",
                  f"- ts_event {f.get('first_ts_event')} .. {f.get('last_ts_event')}\n",
                  "| check | severity | passed | detail |", "|---|---|---|---|"]
        lines += [f"| {c['name']} | {c['severity']} | {'yes' if c['passed'] else 'NO'} | "
                  f"{json.dumps(c['detail'], default=str)[:200].replace('|', '/')} |"
                  for c in f["checks"]]
        lines += ["", "| trade date | records | trades (A/B/N) | v.0 instrument (symbology) "
                  "| ids in records | MAIN max gap (s) | bad-flag | crossed/locked/empty "
                  "| excluded |",
                  "|---|---:|---:|---|---|---:|---:|---|---|"]
        for r in f.get("days", []):
            gap = "" if r["main_max_gap_s"] is None else f"{r['main_max_gap_s']:.1f}"
            excl = list(r["excluded_by_other_rules"]) + (
                [pc.EXCL_GAP] if r["main_gap_gt_60s"] else [])
            lines.append(f"| {r['date']} | {r['records']:,} | {r['trades']:,} "
                         f"({r['trades_side_A']}/{r['trades_side_B']}/{r['trades_side_N']}) | "
                         f"{', '.join(r['instrument_ids_mapped'])} | "
                         f"{', '.join(r['instrument_ids_records'])} | {gap} | "
                         f"{r['dropped_bad_flag_records']} | {r['records_crossed']}/"
                         f"{r['records_locked']}/{r['records_empty_side']} | "
                         f"{', '.join(excl)} |")
        lines.append("")
    return "\n".join(lines) + "\n"


def _parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="verify.py", description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", required=True)
    ap.add_argument("--dbn", nargs="+", required=True)
    ap.add_argument("--out", required=True, help="manifest JSON (the .md goes beside it)")
    ap.add_argument("--tick", type=float, help="tick size: enables the whole-tick price check")
    ap.add_argument("--purchase-record",
                    help="pilot_pull.py's purchase record JSON (required, RD-03)")
    ap.add_argument("--chunk-records", type=int, default=ps.DEFAULT_CHUNK_RECORDS)
    return ap


def purchase_sha256(record_path: str | None) -> str:
    """RD-03: the sha256 of pilot_pull.py's purchase record; PilotRefused when the record is
    not given or holds no 64-hex sha256 (verify.py never runs without one)."""
    if not record_path:
        raise pc.PilotRefused("--purchase-record is required: every file's sha256 is checked "
                              "against pilot_pull.py's purchase record (RD-03)")
    record = json.loads(Path(record_path).read_text())
    sha = record.get("sha256") if isinstance(record, dict) else None
    if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha):
        raise pc.PilotRefused(f"{record_path} holds no sha256 (64 lowercase hex characters)")
    return sha


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        pc.require_root(args.root)
        paths = [Path(p) for p in args.dbn]
        for path in paths:
            reasons = pc.file_name_refusals(path, args.root)
            if reasons or not path.is_file():
                raise pc.PilotRefused("; ".join(reasons) or f"{path} does not exist")
        tick_1e9 = ps.tick_units(args.tick) if args.tick else 1
        expected = purchase_sha256(args.purchase_record)
    except (pc.PilotRefused, ValueError, OSError, KeyError) as exc:
        print(f"REFUSED, nothing opened ({type(exc).__name__}): {exc}", file=sys.stderr)
        return pc.RC_REFUSED
    with contextlib.suppress(OSError):  # a long read: low priority (CLAUDE.md limits)
        os.nice(10)
    files = [verify_file(p, args.root, tick_1e9, args.chunk_records, expected) for p in paths]
    manifest = {"root": args.root, "files": files, "exit_code": exit_code(files),
                "written": datetime.now(pc.PT).isoformat(timespec="seconds")}
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=1, default=str) + "\n", encoding="utf-8")
    out.with_suffix(".md").write_text(render_markdown(manifest), encoding="utf-8")
    failed = [c["name"] for f in files for c in f["checks"] if not c["passed"]]
    print(f"verify: exit {manifest['exit_code']}; failed checks: {failed or 'none'}; wrote {out}")
    return manifest["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
