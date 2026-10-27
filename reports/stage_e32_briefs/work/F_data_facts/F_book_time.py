#!/usr/bin/env python3
"""Stage E.32 Part F: time one trade date's ZM MBO book rebuild with E.31's Book (mbo_book31).

Prints one JSON line: wall time, CPU time, peak RSS and COUNTS only (records, instruments,
resting-order counts). No price, size value, return, markout or feature is printed or stored.
The book driver below replicates only the book-changing branches of E.31's
measure31_core.InstrumentRun._run_chunk (valid start, bad-book flags, snapshot end, A/C/M/R,
F counted against TOP Max, T aggressed lots before 2023-10-02); E.31's placements, fill models,
markouts and BBO history are NOT run (they compute market values).

Usage: F_book_time.py YYYY-MM-DD {split|raw}
  split: load E.31's per-trade-date split array (derived/e31/Z1/<date>.npy, MBO_COMPACT)
  raw:   decode the month's Z1 DBN file and keep the trade date's records (whole-month decode
         time included), the route a rebuild without E.31's split store would take.
"""
from __future__ import annotations

import json
import os
import resource
import sys
import time
from datetime import date, datetime, timedelta
from datetime import time as dtime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
PILOT = REPO / "reports/stage_e31_briefs/work/pilot"
sys.path.insert(0, str(PILOT))
import mbo_book31 as mb  # noqa: E402

DERIVED = Path("/mnt/large-storage/market_data/PropExperiment/derived/e31/Z1")
Z1_DIR = REPO / "data/vendor/databento/GLBX.MDP3/mbo/Z1_ZM_v_0-ZM_v_1"
CT = ZoneInfo("America/Chicago")
NS = 1_000_000_000
TOP_RULE_CHANGE = date(2023, 10, 2)
FIRST, LAST = date(2020, 12, 1), date(2024, 2, 29)
MBO_COMPACT = np.dtype([("ts_recv", "<i8"), ("ts_event", "<i8"), ("instrument_id", "<u4"),
                        ("order_id", "<u8"), ("price", "<i8"), ("size", "<u4"), ("flags", "u1"),
                        ("action", "u1"), ("side", "u1"), ("sequence", "<u4")])


def ct_ns(d: date, at: dtime) -> int:
    return int(datetime.combine(d, at, CT).timestamp()) * NS


def load_split(day: date) -> np.ndarray:
    arr = np.load(DERIVED / f"{day.isoformat()}.npy")
    if arr.dtype != MBO_COMPACT:
        raise SystemExit("split dtype differs from E.31 MBO_COMPACT")
    return arr


def load_raw(day: date) -> np.ndarray:
    import databento as db
    man = json.loads((Z1_DIR / "manifest.json").read_text())
    ent = next(f for f in man["files"] if f["series"] == "Z1" and f["month"] == day.strftime("%Y-%m"))
    lo, hi = ct_ns(day - timedelta(days=1), dtime(16, 0)), ct_ns(day, dtime(16, 0))
    parts = []
    store = db.DBNStore.from_file(Z1_DIR / Path(ent["path"]).name)
    for chunk in store.to_ndarray(count=1_000_000):
        recv = chunk["ts_recv"].astype(np.int64)
        m = (recv >= lo) & (recv < hi)
        if not m.any():
            continue
        c = chunk[m]
        out = np.empty(len(c), dtype=MBO_COMPACT)
        for name in MBO_COMPACT.names:
            src = c[name]
            if src.dtype.kind == "S":
                src = src.astype("S1").view(np.uint8)
            out[name] = src
        parts.append(out)
    return np.concatenate(parts)


def rebuild(rec: np.ndarray, iid: int, count_initial: bool) -> dict:
    m = rec["instrument_id"] == iid
    ts_event, ts_recv, flags = rec["ts_event"][m], rec["ts_recv"][m], rec["flags"][m]
    t, inversions = mb.time_axis(ts_event, ts_recv, flags)
    book = mb.Book(1, 100, count_initial)  # E.31 kalgo31.ZM_K defaults: top_min 1, top_max 100
    aggressed: dict[int, int] = {}
    A, C, M, R, T, F = mb.ACT_ADD, mb.ACT_CANCEL, mb.ACT_MODIFY, mb.ACT_CLEAR, mb.ACT_TRADE, mb.ACT_FILL
    S_A, S_B, S_N = mb.SIDE_ASK_CODE, mb.SIDE_BID_CODE, mb.SIDE_NONE_CODE
    BAD, SNAP, LAST, TOBMBP = mb.F_MAYBE_BAD_BOOK, mb.F_SNAPSHOT, mb.F_LAST, mb.F_TOB | mb.F_MBP
    n = {"records": int(m.sum()), "before_valid_start": 0, "bad_flag_records": 0,
         "side_n_book_records": 0, "ts_event_inversions": int(inversions), "max_resting_orders": 0}
    acts = rec["action"][m].tolist()
    sides = rec["side"][m].tolist()
    pxs = rec["price"][m].tolist()
    szs = rec["size"][m].tolist()
    oids = rec["order_id"][m].tolist()
    fls = flags.tolist()
    max_orders = 0
    for k, (act, side, px, sz, oid, fl) in enumerate(zip(acts, sides, pxs, szs, oids, fls,
                                                         strict=True)):
        if not book.started and act != R:
            n["before_valid_start"] += 1
            continue
        if fl & (BAD | TOBMBP):
            n["bad_flag_records"] += 1
            if not book.bad:
                book.mark_bad()
        if book.in_snapshot and not fl & SNAP:
            book.end_snapshot()
        if act == T:
            if count_initial and oid and side != S_N:
                aggressed[oid] = aggressed.get(oid, 0) + sz
            continue
        if act == F:
            book.on_fill(oid, sz)
            continue
        if act in (A, M) and side != S_B and side != S_A:
            n["side_n_book_records"] += 1
            continue
        bs = mb.BID if side == S_B else mb.ASK
        if act == A:
            book.add(oid, bs, px, sz, aggressed.pop(oid, 0) if count_initial else 0)
        elif act == C:
            book.cancel(oid, sz)
        elif act == M:
            book.modify(oid, bs, px, sz)
        elif act == R:
            book.clear(bool(fl & SNAP))
        if fl & SNAP and fl & LAST:
            book.end_snapshot()
        if k % 4096 == 0:
            max_orders = max(max_orders, len(book.orders))
    n["max_resting_orders_sampled"] = max(max_orders, len(book.orders))
    n["resting_orders_at_end"] = len(book.orders)
    n["book_anomaly_count_total"] = int(sum(book.anomalies.values()))
    n["book_anomaly_kinds"] = sorted(book.anomalies)
    del n["max_resting_orders"]
    return n


def main(argv: list[str]) -> int:
    os.nice(10)
    day, source = date.fromisoformat(argv[0]), argv[1]
    if not FIRST <= day <= LAST:
        raise SystemExit("date outside 2020-12-01..2024-02-29; refused")
    w0, c0 = time.perf_counter(), time.process_time()
    rec = load_split(day) if source == "split" else load_raw(day)
    w1, c1 = time.perf_counter(), time.process_time()
    per = {}
    for iid in np.unique(rec["instrument_id"]).tolist():
        per[str(iid)] = rebuild(rec, iid, day < TOP_RULE_CHANGE)
    w2, c2 = time.perf_counter(), time.process_time()
    out = {"day": day.isoformat(), "source": source, "records": int(len(rec)),
           "load_wall_s": round(w1 - w0, 3), "load_cpu_s": round(c1 - c0, 3),
           "book_wall_s": round(w2 - w1, 3), "book_cpu_s": round(c2 - c1, 3),
           "total_wall_s": round(w2 - w0, 3), "total_cpu_s": round(c2 - c0, 3),
           "peak_rss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1),
           "records_per_s_book": round(len(rec) / (w2 - w1), 0), "instruments": per}
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
