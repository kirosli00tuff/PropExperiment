"""Stage E.31 Part 3: verify every purchased pilot file; write the manifest.

    verify31.py --months K [--allow-missing] [--chunk-records N]

Run from the repo root as ``uv run python reports/stage_e31_briefs/work/pilot/verify31.py ...``
(detached for large files: README31.md). Spec section 9: per file, bytes, sha256, record counts
by record type and instrument, the ts_event range inside the request, no record dated on or
after 2024-03-01, and the DBN metadata (dataset, schema, symbols, stype, start, end, mappings)
against the request. The manifest goes to runs/manifest31.json and, as manifest.json, into every
series folder that holds a verified file.

Checks are "hard" (a failure is exit 2), "quality" (data-quality findings: exit 3 when no hard
check failed) or "info" (counted only). Hard: the purchase record is this request; the file
exists; bytes and sha256 equal the purchase record; the metadata is the request (dataset,
schema, stype_in, symbols, start, end; every symbol mapped; nothing not_found); at least one
record; no record with ts_event or ts_recv at or after the request end; none at or after
2024-03-01T00:00:00Z; every planned request purchased (unless --allow-missing); the record
bytes (SpecReviewer pass 1 item 5): the decoded record bytes == records x the DBN v3 record
size == the records' own length fields == the purchase record's settled
delivered_record_bytes; delivered record bytes not below the quote's billable_bytes. Quality:
the file is read-only; metadata.partial is empty (for a parent request, CME combo children
such as 'ZM:BF K5-N5-Q5' listed partway through the window are listed as info); no record
whose ts_recv is before the request start (Databento selects by ts_recv; a ts_event before
the start with ts_recv inside, as a snapshot's resting orders carry, is counted as info); only
the schema's record type; every record's instrument_id in the metadata mappings; ts_recv
non-decreasing in file order; delivered record bytes above the billable bytes (any difference
is listed; below is hard); Z1: every UTC weekday 00:00Z inside the request has a snapshot
(an R record flagged F_SNAPSHOT, ts_recv within 60 s after that midnight) for each instrument
the metadata maps on that date; Z1, Z2, Z3: ts_event max reaches the month's last DAY session
(its end on the month's last grains trade date, 13:20 CT unless an early halt, by
data.calendars.grains; 60 s tolerance). Info: ts_event inversions in file order (spec section
2 counts them). Exit 0: every check passed. Exit 2 also when nothing can be verified (bad
--months, no purchase record at all). No price field is read.
"""
# ruff: noqa: I001 - pilot31_common is imported first on purpose (sys.path)

from __future__ import annotations

import argparse
import contextlib
import json
import os
import stat
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import numpy as np

import pilot31_common as pc  # first: puts the repo root on sys.path

from data.group_session import session_intervals, trade_dates_between  # noqa: E402
from data.pull_universe import file_sha256  # noqa: E402

RUNS_DIR = Path(__file__).resolve().parent / "runs"
MANIFEST_FILE = "manifest31.json"
SIDE_MANIFEST = "manifest.json"
DEFAULT_CHUNK_RECORDS = 1_000_000
CUTOFF_CHECK = "no_record_on_or_after_2024-03-01T00:00:00Z"
CUTOFF_NS = int(pc.NO_RECORD_FROM_UTC.timestamp()) * pc.NS
_SHIFT = np.uint64(32)
DBN_VERSION = 3
RECORD_SIZE = {"mbo": 56, "mbp-1": 80, "definition": 520}  # DBN v3 wire record bytes
DAY_NS = 86_400 * pc.NS
F_SNAPSHOT = 32  # databento_dbn.F_SNAPSHOT
SNAPSHOT_TOLERANCE_NS = 60 * pc.NS  # snapshot ts_recv = generation time, 00:00:00Z (a1)
LAST_SESSION_TOLERANCE_NS = 60 * pc.NS
TAIL_SERIES = ("Z1", "Z2", "Z3")


def _check(name: str, severity: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"name": name, "severity": severity, "passed": bool(passed), "detail": detail}


@dataclass
class Scan:
    """Counts over every record of one file, in file order."""

    records: int = 0
    by_rtype_iid: Counter = field(default_factory=Counter)
    ts_event_min: int | None = None
    ts_event_max: int | None = None
    ts_recv_min: int | None = None
    ts_recv_max: int | None = None
    at_or_after_end: int = 0
    on_or_after_cutoff: int = 0
    before_start: int = 0  # ts_recv (the index time; ts_event when a schema has none)
    ts_event_only_before_start: int = 0  # ts_event before the start, ts_recv inside
    ts_recv_inversions: int = 0
    ts_event_inversions: int = 0
    last_ts_event: int | None = None
    last_ts_recv: int | None = None
    nbytes: int = 0  # decoded record bytes, as data.adapter.delivered_record_bytes
    length_bytes: int | None = 0  # sum of the records' own length fields x 4
    snapshot_clears: Counter = field(default_factory=Counter)  # (midnight ns, iid) -> n
    snapshot_clears_off_midnight: int = 0

    def by_rtype(self) -> dict[str, int]:
        out: Counter = Counter()
        for (rtype, _), n in self.by_rtype_iid.items():
            out[str(rtype)] += n
        return dict(sorted(out.items()))

    def by_instrument(self) -> dict[str, int]:
        out: Counter = Counter()
        for (_, iid), n in self.by_rtype_iid.items():
            out[str(iid)] += n
        return dict(sorted(out.items(), key=lambda kv: int(kv[0])))


def _minmax(lo: int | None, hi: int | None, arr: np.ndarray) -> tuple[int, int]:
    a, b = int(arr.min()), int(arr.max())
    return (a if lo is None else min(lo, a)), (b if hi is None else max(hi, b))


def _inversions(arr: np.ndarray, last: int | None) -> int:
    n = int(np.count_nonzero(arr[1:] < arr[:-1]))
    return n + (1 if last is not None and int(arr[0]) < last else 0)


def _scan_snapshots(scan: Scan, chunk: np.ndarray) -> None:
    """Z1: the R (clear) records flagged F_SNAPSHOT, by the UTC midnight their ts_recv follows
    by less than SNAPSHOT_TOLERANCE_NS, and per instrument_id."""
    mask = (chunk["action"] == b"R") & ((chunk["flags"].astype(np.uint16) & F_SNAPSHOT) != 0)
    if not mask.any():
        return
    recv = chunk["ts_recv"][mask].astype(np.int64)
    iid = chunk["instrument_id"][mask].astype(np.int64)
    midnight = recv - recv % DAY_NS
    near = (recv - midnight) < SNAPSHOT_TOLERANCE_NS
    scan.snapshot_clears_off_midnight += int((~near).sum())
    for mid, ins in zip(midnight[near].tolist(), iid[near].tolist(), strict=True):
        scan.snapshot_clears[(mid, ins)] += 1


def scan_chunk(scan: Scan, chunk: np.ndarray, start_ns: int, end_ns: int,
               snapshots: bool = False) -> None:
    if len(chunk) == 0:
        return
    names = chunk.dtype.names or ()
    scan.nbytes += int(chunk.nbytes)
    if "length" in names and scan.length_bytes is not None:
        scan.length_bytes += int(chunk["length"].astype(np.uint64).sum()) * 4
    else:
        scan.length_bytes = None
    if snapshots:
        _scan_snapshots(scan, chunk)
    rtype = chunk["rtype"].astype(np.uint64)
    iid = chunk["instrument_id"].astype(np.uint64)
    keys, counts = np.unique((rtype << _SHIFT) | iid, return_counts=True)
    for key, n in zip(keys.tolist(), counts.tolist(), strict=True):
        scan.by_rtype_iid[(key >> 32, key & 0xFFFFFFFF)] += n
    stamps = [chunk["ts_event"].astype(np.uint64)]
    if "ts_recv" in names:
        stamps.append(chunk["ts_recv"].astype(np.uint64))
    end, cutoff, start = np.uint64(end_ns), np.uint64(CUTOFF_NS), np.uint64(start_ns)
    late = np.zeros(len(chunk), dtype=bool)
    after_cut = np.zeros(len(chunk), dtype=bool)
    for arr in stamps:
        late |= arr >= end
        after_cut |= arr >= cutoff
    scan.at_or_after_end += int(late.sum())
    scan.on_or_after_cutoff += int(after_cut.sum())
    # Databento selects records by ts_recv (the index time); an older ts_event (a snapshot's
    # resting orders, a definition) inside a request is expected, so it is only counted.
    early_recv = stamps[-1] < start
    scan.before_start += int(early_recv.sum())
    scan.ts_event_only_before_start += int(((stamps[0] < start) & ~early_recv).sum())
    scan.ts_event_min, scan.ts_event_max = _minmax(scan.ts_event_min, scan.ts_event_max,
                                                   stamps[0])
    scan.ts_event_inversions += _inversions(stamps[0], scan.last_ts_event)
    scan.last_ts_event = int(stamps[0][-1])
    if len(stamps) > 1:
        scan.ts_recv_min, scan.ts_recv_max = _minmax(scan.ts_recv_min, scan.ts_recv_max,
                                                     stamps[1])
        scan.ts_recv_inversions += _inversions(stamps[1], scan.last_ts_recv)
        scan.last_ts_recv = int(stamps[1][-1])
    scan.records += len(chunk)


def header(meta: Any) -> dict[str, Any]:
    return {"version": int(getattr(meta, "version", 0) or 0),
            "dataset": str(meta.dataset), "schema": str(meta.schema),
            "stype_in": str(meta.stype_in), "stype_out": str(getattr(meta, "stype_out", "")),
            "symbols": [str(s) for s in meta.symbols],
            "partial": [str(s) for s in (meta.partial or [])],
            "not_found": [str(s) for s in (meta.not_found or [])],
            "start_ns": int(meta.start), "end_ns": None if meta.end is None else int(meta.end),
            "start": pc.iso_ns(int(meta.start)),
            "end": None if meta.end is None else pc.iso_ns(int(meta.end)),
            "mappings": {str(k): [{"start_date": str(e["start_date"]),
                                   "end_date": str(e["end_date"]), "symbol": str(e["symbol"])}
                                  for e in v] for k, v in (meta.mappings or {}).items()}}


def metadata_refusals(hdr: dict[str, Any], item: pc.Planned) -> list[str]:
    p, s = item.params, item.series
    out = []
    if hdr["dataset"] != p.dataset:
        out.append(f"dataset {hdr['dataset']} != {p.dataset}")
    if hdr["schema"] != s.schema:
        out.append(f"schema {hdr['schema']} != {s.schema}")
    if hdr["stype_in"] != s.stype_in:
        out.append(f"stype_in {hdr['stype_in']} != {s.stype_in}")
    if sorted(hdr["symbols"]) != sorted(s.symbols):
        out.append(f"symbols {hdr['symbols']} != {list(s.symbols)}")
    if hdr["start_ns"] != pc.bound_ns(p.start):
        out.append(f"start {hdr['start']} != {p.start}")
    if hdr["end_ns"] != pc.bound_ns(p.end):
        out.append(f"end {hdr['end']} != {p.end}")
    out.extend(mapping_refusals(hdr, s))
    if hdr["not_found"]:
        out.append(f"metadata.not_found {hdr['not_found']}")
    return out


def _has_id(intervals: list[dict[str, Any]]) -> bool:
    return any(e["symbol"].strip() for e in intervals)


def mapping_refusals(hdr: dict[str, Any], s: pc.Series) -> list[str]:
    """Continuous: every requested symbol is a mapping key with an instrument_id. Parent
    (FixCoder 2026-10-23: the real Z4 headers key their mappings by child raw symbol, e.g.
    'ZMH4', 'ZSX6-ZSN7', 'ZL:BF F5-H5-K5', not by 'ZM.FUT'): every parent root has a child key
    with an instrument_id, and no key belongs to another root."""
    maps = hdr["mappings"]
    if s.stype_in != "parent":
        unmapped = [sym for sym in s.symbols if not _has_id(maps.get(sym, []))]
        return [f"no symbology mapping for {unmapped}"] if unmapped else []
    roots = [sym.split(".")[0] for sym in s.symbols]
    unmapped = [sym for sym, root in zip(s.symbols, roots, strict=True)
                if not any(k.startswith(root) and _has_id(v) for k, v in maps.items())]
    foreign = sorted(k for k in maps if not any(k.startswith(r) for r in roots))
    out = [f"no symbology mapping for {unmapped}"] if unmapped else []
    if foreign:
        out.append(f"mapping keys outside {roots}: {foreign[:5]}")
    return out


def mapped_ids(hdr: dict[str, Any]) -> set[int]:
    return {int(e["symbol"]) for v in hdr["mappings"].values() for e in v
            if e["symbol"].strip().isdigit()}


def partial_checks(hdr: dict[str, Any], item: pc.Planned) -> list[dict[str, Any]]:
    """metadata.partial lists symbols that did not resolve on every day of the request. For a
    parent request those are children; CME combos ('ZM:BF K5-N5-Q5', 'ZL:CF N4Q4U4V4') listed
    partway through the window are expected and only listed (info). Anything else is quality."""
    partial = list(hdr["partial"])
    combos = [p for p in partial if item.series.stype_in == "parent" and ":" in p]
    other = [p for p in partial if p not in combos]
    out = [_check("metadata_partial_empty", "quality", not other, other)]
    if combos:
        out.append(_check("metadata_partial_parent_combos_listed", "info", True, combos))
    return out


def record_checks(scan: Scan, item: pc.Planned, hdr: dict[str, Any]) -> list[dict[str, Any]]:
    expected = pc.EXPECTED_RTYPE[item.series.schema]
    rtypes = scan.by_rtype()
    unmapped = sorted({iid for (_, iid) in scan.by_rtype_iid} - mapped_ids(hdr))
    return [
        _check("records_present", "hard", scan.records > 0, scan.records),
        _check("no_record_at_or_after_request_end", "hard", scan.at_or_after_end == 0,
               {"records": scan.at_or_after_end, "end": item.params.end}),
        _check(CUTOFF_CHECK, "hard", scan.on_or_after_cutoff == 0, scan.on_or_after_cutoff),
        _check("no_record_before_request_start", "quality", scan.before_start == 0,
               {"records_ts_recv_before_start": scan.before_start,
                "start": item.params.start, "by": "ts_recv (Databento's index time)"}),
        _check("ts_event_before_request_start_counted", "info", True,
               {"records_ts_event_only_before_start": scan.ts_event_only_before_start}),
        _check("only_the_schema_record_type", "quality", set(rtypes) <= {str(expected)},
               {"expected": expected, "found": rtypes}),
        _check("record_instrument_ids_in_mappings", "quality", not unmapped, unmapped[:50]),
        _check("ts_recv_non_decreasing", "quality", scan.ts_recv_inversions == 0,
               scan.ts_recv_inversions),
        _check("ts_event_inversions_counted", "info", True, scan.ts_event_inversions),
        *partial_checks(hdr, item),
    ]


def byte_checks(scan: Scan, item: pc.Planned, hdr: dict[str, Any],
                record: dict[str, Any]) -> list[dict[str, Any]]:
    """Hard: decoded record bytes == records x record size == the length fields == the
    purchase record's settled delivered_record_bytes. Delivered vs the quote's billable bytes:
    equal passes; above is a quality finding; below is hard (SpecReviewer pass 1 item 5)."""
    size = RECORD_SIZE[item.series.schema]
    settled = (record.get("settled") or {}).get("delivered_record_bytes")
    expected = scan.records * size
    values = {"decoded_record_bytes": scan.nbytes, "records": scan.records,
              "record_size": size, "records_x_record_size": expected,
              "length_field_bytes": scan.length_bytes, "dbn_version": hdr.get("version"),
              "purchase_record_delivered_record_bytes": settled}
    same = (hdr.get("version") == DBN_VERSION and scan.nbytes == expected
            and scan.length_bytes == expected and settled == expected)
    out = [_check("record_bytes_match_purchase_record", "hard", same, values)]
    billable = (record.get("quote") or {}).get("billable_bytes")
    if not isinstance(billable, int) or isinstance(billable, bool):
        return [*out, _check("delivered_bytes_equal_quoted_billable", "hard", False,
                             {"billable_bytes": billable, "why": "no quoted billable_bytes"})]
    diff = scan.nbytes - billable
    detail = {"delivered_record_bytes": scan.nbytes, "quoted_billable_bytes": billable,
              "delivered_minus_billable": diff,
              "ratio": None if billable == 0 else scan.nbytes / billable}
    # Lead ruling 2026-10-23: for the definition schema (Z4) a delivery below the quoted billable
    # bytes is a quality finding, not hard. The canary's Z4 files came 3.7% under the estimate,
    # settled at the quote; the outrights' match algorithm and ticks are checked directly by
    # canary_check31. Z1-Z3 (mbo, mbp-1) keep the hard rule.
    hard_below = diff < 0 and item.series.schema != "definition"
    return [*out, _check("delivered_bytes_equal_quoted_billable",
                         "hard" if hard_below else "quality", diff == 0, detail)]


def weekday_midnights(start_ns: int, end_ns: int) -> list[int]:
    """Every 00:00Z inside [start, end) whose UTC date is Monday to Friday."""
    first = -(-start_ns // DAY_NS) * DAY_NS
    out = []
    for mid in range(first, end_ns, DAY_NS):
        if datetime.fromtimestamp(mid // pc.NS, UTC).weekday() < 5:
            out.append(mid)
    return out


def mapped_on(hdr: dict[str, Any], day: date) -> dict[str, list[int]]:
    """symbol -> the instrument_ids its metadata mapping gives for UTC date ``day``
    (start_date inclusive, end_date exclusive)."""
    out: dict[str, list[int]] = {}
    for sym, intervals in sorted(hdr["mappings"].items()):
        ids = [int(e["symbol"]) for e in intervals if e["symbol"].strip().isdigit()
               and date.fromisoformat(e["start_date"]) <= day
               < date.fromisoformat(e["end_date"])]
        out[sym] = ids
    return out


def snapshot_table(scan: Scan, hdr: dict[str, Any], start_ns: int, end_ns: int
                   ) -> list[dict[str, Any]]:
    """One row per (weekday midnight, symbol, mapped instrument): is its snapshot there."""
    rows = []
    for mid in weekday_midnights(start_ns, end_ns):
        day = datetime.fromtimestamp(mid // pc.NS, UTC).date()
        for sym, ids in mapped_on(hdr, day).items():
            for iid in ids or [None]:
                n = 0 if iid is None else scan.snapshot_clears.get((mid, iid), 0)
                rows.append({"midnight": pc.iso_ns(mid), "midnight_ns": mid, "symbol": sym,
                             "instrument_id": iid, "snapshot_clears": n})
    return rows


def snapshot_check(scan: Scan, hdr: dict[str, Any], start_ns: int, end_ns: int
                   ) -> dict[str, Any]:
    rows = snapshot_table(scan, hdr, start_ns, end_ns)
    missing = [r for r in rows if r["instrument_id"] is None or r["snapshot_clears"] == 0]
    return _check("z1_weekday_midnight_snapshot_per_mapped_instrument", "quality", not missing,
                  {"cells": len(rows), "missing": missing[:60], "n_missing": len(missing),
                   "snapshot_clears_off_midnight": scan.snapshot_clears_off_midnight})


def last_day_session_end_ns(item: pc.Planned) -> tuple[date, int]:
    """The month's last grains trade date and the end of its DAY session (UTC ns)."""
    cal = pc.calendar_for(item.series.roots[0])
    days = trade_dates_between(cal, item.month, pc.last_day(item.month))
    if not days:
        raise pc.PilotRefused(f"{item.label}: no grains trade date in the month")
    return days[-1], int(session_intervals(cal, days[-1])[-1][1])


def tail_check(scan: Scan, item: pc.Planned) -> dict[str, Any]:
    last, end_ns = last_day_session_end_ns(item)
    reached = scan.ts_event_max is not None and \
        scan.ts_event_max >= end_ns - LAST_SESSION_TOLERANCE_NS
    gap = None if scan.ts_event_max is None else (end_ns - scan.ts_event_max) / pc.NS
    return _check("ts_event_max_reaches_last_day_session", "quality", reached,
                  {"last_trade_date": last.isoformat(), "day_session_end": pc.iso_ns(end_ns),
                   "ts_event_max": _iso(scan.ts_event_max),
                   "seconds_before_session_end": gap,
                   "tolerance_s": LAST_SESSION_TOLERANCE_NS / pc.NS})


def _iso(ns: int | None) -> str | None:
    return None if ns is None else pc.iso_ns(ns)


def verify_file(item: pc.Planned, record: dict[str, Any], path: Path,
                chunk_records: int) -> dict[str, Any]:
    out: dict[str, Any] = {"series": item.series.name, "month": item.month_label,
                           "path": str(path), "request": item.params.as_kwargs()}
    checks = [_check("purchase_record_is_this_request", "hard",
                     record.get("request") == item.params.as_kwargs()
                     and record.get("target") == str(path),
                     {"record_target": record.get("target")})]
    if not path.is_file():
        checks.append(_check("file_exists", "hard", False, str(path)))
        return {**out, "checks": checks}
    out.update({"bytes": path.stat().st_size, "sha256": file_sha256(path)})
    checks += [
        _check("file_exists", "hard", True, str(path)),
        _check("bytes_match_purchase_record", "hard", out["bytes"] == record.get("bytes"),
               record.get("bytes")),
        _check("sha256_matches_purchase_record", "hard", out["sha256"] == record.get("sha256"),
               record.get("sha256")),
        _check("file_read_only", "quality", not path.stat().st_mode & (stat.S_IWUSR
                                                                     | stat.S_IWGRP
                                                                     | stat.S_IWOTH),
               oct(path.stat().st_mode & 0o777)),
    ]
    import databento  # lazy

    store = databento.DBNStore.from_file(path)
    hdr = header(store.metadata)
    out["header"] = hdr
    bad = metadata_refusals(hdr, item)
    checks.append(_check("metadata_is_the_request", "hard", not bad, bad))
    if bad:
        return {**out, "checks": checks}
    scan = Scan()
    start_ns, end_ns = pc.bound_ns(item.params.start), pc.bound_ns(item.params.end)
    is_z1 = item.series.name == "Z1"
    for chunk in store.to_ndarray(count=chunk_records):
        scan_chunk(scan, chunk, start_ns, end_ns, snapshots=is_z1)
    out.update({"records": scan.records, "records_by_rtype": scan.by_rtype(),
                "records_by_instrument_id": scan.by_instrument(),
                "records_by_rtype_and_instrument_id": {
                    f"{r}:{i}": n for (r, i), n in sorted(scan.by_rtype_iid.items())},
                "delivered_record_bytes": scan.nbytes,
                "ts_event_min": _iso(scan.ts_event_min), "ts_event_max": _iso(scan.ts_event_max),
                "ts_recv_min": _iso(scan.ts_recv_min), "ts_recv_max": _iso(scan.ts_recv_max)})
    checks += record_checks(scan, item, hdr) + byte_checks(scan, item, hdr, record)
    if is_z1:
        checks.append(snapshot_check(scan, hdr, start_ns, end_ns))
    if item.series.name in TAIL_SERIES:
        checks.append(tail_check(scan, item))
    return {**out, "checks": checks}


def exit_code(files: list[dict[str, Any]], extra: list[dict[str, Any]]) -> int:
    checks = [c for f in files for c in f["checks"]] + extra
    if any(not c["passed"] and c["severity"] == "hard" for c in checks):
        return pc.RC_REFUSED
    if any(not c["passed"] and c["severity"] == "quality" for c in checks):
        return pc.RC_QUALITY
    return pc.RC_OK


def _parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="verify31.py", description=__doc__.split("\n\n")[0])
    ap.add_argument("--months", type=int, required=True)
    ap.add_argument("--allow-missing", action="store_true",
                    help="list planned requests with no purchase record as info, not hard")
    ap.add_argument("--chunk-records", type=int, default=DEFAULT_CHUNK_RECORDS)
    ap.add_argument("--no-side-manifests", action="store_true",
                    help="write runs/manifest31.json only, nothing beside the data")
    return ap


def _load_records(items: list[pc.Planned], runs_dir: Path) -> dict[str, dict[str, Any]]:
    out = {}
    for item in items:
        path = runs_dir / pc.record_name(item)
        if path.is_file():
            out[item.key] = json.loads(path.read_text())
    return out


def write_manifests(manifest: dict[str, Any], runs_dir: Path, side: bool = True) -> list[str]:
    text = json.dumps(manifest, indent=1, default=str) + "\n"
    paths = [runs_dir / MANIFEST_FILE]
    if side:
        paths += sorted({Path(f["path"]).parent / SIDE_MANIFEST for f in manifest["files"]
                         if Path(f["path"]).parent.is_dir()})
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(path)
    return [str(p) for p in paths]


def main(argv: list[str] | None = None, *, vendor_root: Path = pc.PILOT_VENDOR_ROOT,
         runs_dir: Path = RUNS_DIR) -> int:
    args = _parser().parse_args(argv)
    runs_dir = Path(runs_dir)
    try:
        items = pc.plan(args.months)
        records = _load_records(items, runs_dir)
        if not records:
            raise pc.PilotRefused(f"no purchase31_*.json record in {runs_dir} for this plan")
    except (pc.PilotRefused, ValueError, OSError, KeyError) as exc:
        print(f"REFUSED, nothing opened ({type(exc).__name__}): {exc}", file=sys.stderr)
        return pc.RC_REFUSED
    with contextlib.suppress(OSError):  # a long read: low priority (CLAUDE.md limits)
        os.nice(10)
    files = [verify_file(i, records[i.key], pc.target_path(i, vendor_root), args.chunk_records)
             for i in items if i.key in records]
    missing = [i.label for i in items if i.key not in records]
    extra = [_check("every_planned_request_purchased", "info" if args.allow_missing else "hard",
                    not missing, missing)]
    code = exit_code(files, extra)
    manifest = {"months": args.months, "n_planned": len(items), "n_verified": len(files),
                "missing": missing, "plan_checks": extra, "files": files, "exit_code": code,
                "written": datetime_pt()}
    written = write_manifests(manifest, runs_dir, side=not args.no_side_manifests)
    failed = sorted({f"{f['series']} {f['month']}: {c['name']}" for f in files
                     for c in f["checks"] if not c["passed"]}
                    | {c["name"] for c in extra if not c["passed"]})
    print(f"verify31: exit {code}; {len(files)}/{len(items)} files; failed checks: "
          f"{failed[:12] or 'none'}{' ...' if len(failed) > 12 else ''}; wrote {written[0]} "
          f"and {len(written) - 1} manifest.json")
    return code


def datetime_pt() -> str:
    return datetime.now(pc.PT).isoformat(timespec="seconds")


if __name__ == "__main__":
    sys.exit(main())
