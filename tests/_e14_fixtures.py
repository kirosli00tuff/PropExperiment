"""Shared synthetic fixtures for the Stage E.14 (harness v10) tests. Nothing here is market data.

- ``calendar_payload``: an e14_hist_calendar/1 payload (SYNTHETIC entries, never a sourced
  calendar); tests/fixtures/e14_hist/<group>.json are written from it by ``write_fixture_files``.
- ``write_chunk``: a zstd DBN ohlcv-1m file with planted bars (prices in 1e-9 units).
- ``make_store_inputs``: every chunk of a plan for one root, its purchase manifest, the cached
  symbology and the condition list, all under tmp paths.
"""

from __future__ import annotations

import copy
import hashlib
import json
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import databento_dbn as dbn
import zstandard

from data.pull_hist import (
    HistPlan,
    condition_path,
    plan_chunks,
    purchase_manifest_path,
    symbology_cache_path,
)
from data.pull_universe import target_path
from data.session import ct_ns

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "e14_hist"
SOURCE = "synthetic-test-fixture"
SESSIONS = {
    "equity": ([(-1, "17:00", 0, "15:15"), (0, "15:30", 0, "16:15")], {"*": ["08:30", "15:15"]}),
    "energy": ([(-1, "17:00", 0, "16:00")], {"*": ["08:00", "13:30"]}),
}
PRODUCTS = {"equity": ["ES", "NQ"], "energy": ["NG"]}
# SYNTHETIC entries: chosen to exercise the code, not CME's real schedule.
ENTRIES = {
    "equity": [
        ("2010-07-05", "Independence Day (observed)", "full_closure", None, None, "cme"),
        ("2011-05-30", "Memorial Day", "early_halt", "12:00", None, "cme"),
        ("2011-11-24", "Thanksgiving", "full_closure", None, None, "cme"),
        ("2011-11-25", "Thanksgiving Friday", "early_halt", "12:15", None, "cme"),
        ("2012-10-29", "Hurricane Sandy", "full_closure", None, None, "secondary"),
        ("2016-03-25", "Good Friday", "full_closure", None, None, "unverified"),
        ("2018-12-05", "Day of mourning (synthetic late open)", "late_open", None, "09:30",
         "secondary"),
    ],
    "energy": [
        ("2010-07-05", "Independence Day (observed)", "full_closure", None, None, "cme"),
        ("2012-11-22", "Thanksgiving", "full_closure", None, None, "cme"),
    ],
}
UNSOURCED = {"equity": [("2015-06-15", "synthetic: no source found")], "energy": []}


def calendar_payload(group: str) -> dict[str, Any]:
    segments, day_session = SESSIONS[group]
    entries = []
    for day, name, kind, halt, open_ct, evidence in ENTRIES[group]:
        entries.append({
            "day": day, "name": name, "kind": kind, "halt_ct": halt,
            **({"open_ct": open_ct} if kind == "late_open" else {}),
            "evidence": evidence, "time_evidence": "n/a" if kind == "full_closure" else "cme",
            "source": SOURCE, "status_quote": "synthetic", "time_quote": None, "note": ""})
    return {
        "schema": "e14_hist_calendar/1", "group": group, "products": list(PRODUCTS[group]),
        "cme_row_labels": ["synthetic"],
        "coverage": {"first": "2010-06-01", "last": "2019-05-31"},
        "sessions": [{"valid_from": "2010-06-01", "valid_to": None,
                      "segments": [{"start_offset_days": a, "start_ct": b, "end_offset_days": c,
                                    "end_ct": d} for a, b, c, d in segments],
                      "day_session_ct": day_session, "source": SOURCE, "evidence": "cme",
                      "note": "synthetic"}],
        "entries": entries,
        "no_entry_findings": [],
        "year_coverage": [{"year": y, "documents": [SOURCE], "complete_exception_list": True,
                           "unscheduled_check": "synthetic", "evidence": "cme"}
                          for y in range(2010, 2020)],
        "unsourced": [{"day": d, "reason": r} for d, r in UNSOURCED[group]],
        "sources": {SOURCE: {"url": None, "capture": None, "fetched_utc": None,
                             "saved_file": None, "sha256": None,
                             "title": "SYNTHETIC TEST FIXTURE, not a sourced calendar"}},
        "counts": {},
    }


def fixture_payload(group: str) -> dict[str, Any]:
    """The committed fixture file's payload (a deep copy, safe to mutate)."""
    return copy.deepcopy(json.loads((FIXTURE_DIR / f"{group}.json").read_text(encoding="utf-8")))


def write_calendar(base: Path, payload: dict[str, Any]) -> Path:
    base.mkdir(parents=True, exist_ok=True)
    path = base / f"{payload['group']}.json"
    path.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_fixture_files() -> list[Path]:
    """(Re)write tests/fixtures/e14_hist/*.json from ``calendar_payload`` (run by hand)."""
    return [write_calendar(FIXTURE_DIR, calendar_payload(g)) for g in sorted(SESSIONS)]


# ------------------------------------------------------------------ bars ----
TICK_ES = 250_000_000  # 0.25 in 1e-9 units
PX = 1_300_000_000_000  # 1300.00


def ct(day: str | date, hhmm: str) -> int:
    d = date.fromisoformat(day) if isinstance(day, str) else day
    return ct_ns(d, time.fromisoformat(hhmm))


def bar(ts: int, open_px: int, close_px: int, volume: int = 5) -> tuple[int, ...]:
    return (ts, open_px, max(open_px, close_px), min(open_px, close_px), close_px, volume)


def _utc_ns(day: str) -> int:
    return int(datetime.fromisoformat(day).replace(tzinfo=UTC).timestamp()) * 10**9


def symbology_payload(root: str, plan: HistPlan, splice: str, iids: tuple[int, int],
                      raws: tuple[str, str]) -> dict[str, Any]:
    """Two contracts, spliced at 00:00 UTC of ``splice``."""
    start, end = str(plan.data_start), str(plan.data_end)
    sym = f"{root}.v.0"
    return {"symbol": sym, "start_date": start, "end_date": end, "fetched_utc": "synthetic",
            "continuous_to_instrument_id": {"result": {sym: [
                {"d0": start, "d1": splice, "s": str(iids[0])},
                {"d0": splice, "d1": end, "s": str(iids[1])}]}},
            "queried_instrument_ids": [str(i) for i in iids],
            "instrument_id_to_raw_symbol": {"result": {
                str(iids[0]): [{"d0": start, "d1": end, "s": raws[0]}],
                str(iids[1]): [{"d0": start, "d1": end, "s": raws[1]}]}}}


def iid_on(ts: int, splice: str, iids: tuple[int, int]) -> int:
    return iids[0] if ts < _utc_ns(splice) else iids[1]


def make_store_inputs(tmp_path: Path, plan: HistPlan, root: str, bars: list[tuple[int, ...]],
                      *, splice: str, iids: tuple[int, int], raws: tuple[str, str],
                      degraded: tuple[str, ...] = ()) -> dict[str, Path]:
    """Every plan chunk of ``root`` (bars placed by ts_event; chunk files may be empty), the
    plan's purchase manifest, the cached symbology and the condition list."""
    vendor, reports, rolls = tmp_path / "v", tmp_path / "reports", tmp_path / "rolls"
    files = []
    for item in plan_chunks(plan, (root,)):
        p = item.params
        lo, hi = _utc_ns(p.start), _utc_ns(p.end)
        mine = [b for b in bars if lo <= b[0] < hi]
        by_id: dict[int, list] = {}
        for b in mine:
            by_id.setdefault(iid_on(b[0], splice, iids), []).append(b)
        target = target_path(p, vendor)
        records = [(b, iid_on(b[0], splice, iids)) for b in mine]
        write_chunk(target, p.start, p.end, f"{root}.v.0", records, iids[0])
        files.append({"name": target.name, "path": str(target), "request_start": p.start,
                      "request_end": p.end,
                      "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
                      "record_count": len(mine), "instrument_ids": sorted(
                          {str(i) for i in by_id} or {str(iids[0])})})
    manifest = purchase_manifest_path(root, plan.name, reports)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps({"product": root, "plan": plan.name, "files": files}),
                        encoding="utf-8")
    sym = symbology_cache_path(root, plan, rolls)
    sym.parent.mkdir(parents=True, exist_ok=True)
    sym.write_text(json.dumps(symbology_payload(root, plan, splice, iids, raws)),
                   encoding="utf-8")
    cond = condition_path(plan, tmp_path / "condition")
    cond.parent.mkdir(parents=True, exist_ok=True)
    cond.write_text(json.dumps([{"date": d, "condition": "degraded"} for d in degraded]
                               + [{"date": "2012-01-03", "condition": "available"}]),
                    encoding="utf-8")
    return {"vendor": vendor, "reports": reports, "rolls": rolls,
            "condition_dir": tmp_path / "condition", "manifest": manifest}


def write_chunk(path: Path, start: str, end: str, symbol: str,
                 records: list[tuple[tuple[int, ...], int]], default_iid: int) -> None:
    mapping = SimpleNamespace(raw_symbol=symbol, intervals=[SimpleNamespace(
        start_date=date.fromisoformat(start), end_date=date.fromisoformat(end),
        symbol=str(default_iid))])
    meta = dbn.Metadata("GLBX.MDP3", _utc_ns(start), dbn.SType.CONTINUOUS,
                        dbn.SType.INSTRUMENT_ID, dbn.Schema.OHLCV_1M, symbols=[symbol],
                        partial=[], not_found=[], mappings=[mapping], end=_utc_ns(end))
    raw = bytes(meta.encode()) + b"".join(
        bytes(dbn.OHLCVMsg(0x21, 1, iid, ts, o, h, lo, c, v))
        for (ts, o, h, lo, c, v), iid in sorted(records, key=lambda r: r[0][0]))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(zstandard.ZstdCompressor().compress(raw))


def day_bars(day: str, prices: dict[str, tuple[int, int]]) -> list[tuple[int, ...]]:
    """Bars on CT calendar day ``day`` at the given HH:MM: (open, close) in 1e-9 units."""
    return [bar(ct(day, hhmm), o, c) for hhmm, (o, c) in sorted(prices.items())]


def next_weekday(day: date) -> date:
    nxt = day + timedelta(days=1)
    while nxt.weekday() >= 5:
        nxt += timedelta(days=1)
    return nxt
