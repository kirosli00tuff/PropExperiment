#!/usr/bin/env python3
"""Stage E.32 Part F scan: counts, sizes, schema field names and timings of the owned soy files.

STRICT data rule: no price, order size, return, markout or feature value is computed, printed or
stored. Only counts (records by trade date, action, side, instrument, flag), schema metadata,
timestamp-difference histograms (timings), byte sizes and run timings are written.

Usage: F_scan.py SERIES [SERIES ...]   (Z1 ZM MBO, Z2 ZS MBP-1, Z3 ZL MBP-1, Z4 definitions)
Writes reports/stage_e32_briefs/work/F_data_facts/F_scan_out/<SERIES>_<YYYY-MM>.json; a file
whose JSON exists is skipped (resumable).
"""
from __future__ import annotations

import json
import os
import re
import resource
import sys
import time
from datetime import date, datetime, timedelta
from datetime import time as dtime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
sys.path.insert(0, str(REPO))
from data.group_session import load_group_calendar  # noqa: E402

VENDOR = REPO / "data/vendor/databento/GLBX.MDP3"
SERIES_DIR = {"Z1": VENDOR / "mbo/Z1_ZM_v_0-ZM_v_1", "Z2": VENDOR / "mbp-1/Z2_ZS_v_0",
              "Z3": VENDOR / "mbp-1/Z3_ZL_v_0", "Z4": VENDOR / "definition/Z4_ZM_FUT-ZS_FUT-ZL_FUT"}
OUT = REPO / "reports/stage_e32_briefs/work/F_data_facts/F_scan_out"
CT = ZoneInfo("America/Chicago")
NS = 1_000_000_000
FIRST_NAME_START = "2020-11-30T220000Z"  # trade date 2020-12-01 window opens 16:00 CT 11-30
LAST_NAME_END = "2024-02-29T220000Z"
CUTOFF_NS = 1_709_251_200 * NS  # 2024-03-01T00:00:00Z: stop if any record reaches it
CHUNK = 1_000_000
F_LAST, F_TOB, F_SNAPSHOT, F_MBP, F_BAD_TS_RECV, F_MAYBE_BAD_BOOK = 128, 64, 32, 16, 8, 4
FLAG_NAMES = {"F_LAST": F_LAST, "F_TOB": F_TOB, "F_SNAPSHOT": F_SNAPSHOT, "F_MBP": F_MBP,
              "F_BAD_TS_RECV": F_BAD_TS_RECV, "F_MAYBE_BAD_BOOK": F_MAYBE_BAD_BOOK,
              "bit1_publisher_specific": 2, "bit0_reserved": 1}
# ts_recv - ts_event histogram edges (ns); a timing, not a market value
LAT_EDGES = [-(2**62), 0, 1_000, 10_000, 100_000, 1_000_000, 10_000_000, 100_000_000, NS,
             60 * NS, 2**62]
LAT_LABELS = ["<0", "[0,1us)", "[1us,10us)", "[10us,100us)", "[100us,1ms)", "[1ms,10ms)",
              "[10ms,100ms)", "[100ms,1s)", "[1s,60s)", ">=60s"]
NAME_RE = re.compile(r"^range=(\d{4}-\d\d-\d\dT\d{6}Z)_(\d{4}-\d\d-\d\dT\d{6}Z)\.dbn\.zst$")
DEF_KEEP = ("raw_symbol", "instrument_class", "asset", "security_type", "expiration",
            "activation", "match_algorithm", "user_defined_instrument", "unit_of_measure_qty",
            "min_price_increment", "security_update_action", "group", "exchange")


class Refused(RuntimeError):
    pass


def guard_name(path: Path) -> tuple[str, str]:
    m = NAME_RE.match(path.name)
    if not m:
        raise Refused(f"unexpected file name {path.name}")
    a, b = m.group(1), m.group(2)
    if a < FIRST_NAME_START or b > LAST_NAME_END:
        raise Refused(f"{path.name}: outside 2020-11-30T22Z..2024-02-29T22Z; not opened")
    return a, b


def day_bounds(start_ns: int, end_ns: int) -> tuple[list[date], np.ndarray]:
    """Trade date D = window [D-1 16:00 CT, D 16:00 CT) (E.31 convention)."""
    first = datetime.fromtimestamp(start_ns / NS, CT).date() - timedelta(days=1)
    last = datetime.fromtimestamp(end_ns / NS, CT).date() + timedelta(days=2)
    days = [first + timedelta(days=k) for k in range((last - first).days + 1)]
    bounds = np.array([int(datetime.combine(d - timedelta(days=1), dtime(16, 0), CT).timestamp())
                       * NS for d in days], dtype=np.int64)
    return days, bounds


def decompressed_bytes(path: Path) -> tuple[int, float]:
    import zstandard
    t0 = time.perf_counter()
    n = 0
    with path.open("rb") as fh, zstandard.ZstdDecompressor().stream_reader(fh) as r:
        while True:
            b = r.read(1 << 24)
            if not b:
                break
            n += len(b)
    return n, time.perf_counter() - t0


def as_u8(col: np.ndarray) -> np.ndarray:
    if col.dtype.kind == "S":
        return col.astype("S1").view(np.uint8)
    return col.astype(np.uint8)


class Carry:
    """Per-instrument state across chunks for tie and inversion counts (file order)."""

    def __init__(self) -> None:
        self.last_ev: dict[int, int] = {}
        self.max_ev: dict[int, int] = {}
        self.last_recv: dict[int, int] = {}
        self.last_ev_event: dict[int, int] = {}


def add(d: dict, k, v: int) -> None:
    d[k] = d.get(k, 0) + int(v)


def scan_records(store, series: str, start_ns: int, end_ns: int, res: dict) -> None:
    days, bounds = day_bounds(start_ns, end_ns)
    per_day = np.zeros(len(days), dtype=np.int64)
    per_day_events = np.zeros(len(days), dtype=np.int64)
    per_day_act = np.zeros((len(days), 256), dtype=np.int64)
    per_day_iid: dict[str, dict[str, int]] = {}
    iid_act: dict[str, dict[str, int]] = {}
    act_side: dict[str, int] = {}
    flags_cnt = {k: 0 for k in FLAG_NAMES}
    a = {"records": 0, "snapshot_records": 0, "recv_lt_event_all": 0,
         "recv_lt_event_nonsnapshot": 0, "ts_event_before_file_start": 0,
         "ts_event_before_2020-12-01T00Z_count": 0,
         "event_ties_record_level_nonsnapshot": 0, "event_ties_between_F_LAST_events": 0,
         "event_inversions_nonsnapshot": 0, "recv_ties_record_level": 0,
         "recv_decreases_per_instrument": 0, "nonsnapshot_records": 0,
         "ts_event_multiple_of_1us": 0, "ts_event_multiple_of_1ms": 0,
         "ts_recv_multiple_of_1us": 0, "ts_in_delta_negative": 0, "F_LAST_records": 0}
    lat = np.zeros(len(LAT_LABELS), dtype=np.int64)
    carry = Carry()
    dtype_info = None
    seal_ns = int(datetime(2020, 12, 1, tzinfo=ZoneInfo("UTC")).timestamp()) * NS
    t0, c0 = time.perf_counter(), time.process_time()
    for chunk in store.to_ndarray(count=CHUNK):
        n = len(chunk)
        if n == 0:
            continue
        if dtype_info is None:
            dtype_info = [[nm, str(chunk.dtype[nm])] for nm in chunk.dtype.names]
            res["ndarray_itemsize"] = int(chunk.dtype.itemsize)
        recv = chunk["ts_recv"].astype(np.int64)
        ev = chunk["ts_event"].astype(np.int64)
        if int(recv.max()) >= CUTOFF_NS or int(ev.max()) >= CUTOFF_NS:
            raise Refused("a record is dated on or after 2024-03-01; stopped")
        fl = chunk["flags"].astype(np.uint8)
        iid = chunk["instrument_id"].astype(np.int64)
        snap = (fl & F_SNAPSHOT) != 0
        last = (fl & F_LAST) != 0
        a["records"] += n
        a["snapshot_records"] += int(snap.sum())
        a["F_LAST_records"] += int(last.sum())
        for k, bit in FLAG_NAMES.items():
            flags_cnt[k] += int(((fl & bit) != 0).sum())
        a["recv_lt_event_all"] += int((recv < ev).sum())
        ns_mask = ~snap
        a["nonsnapshot_records"] += int(ns_mask.sum())
        a["recv_lt_event_nonsnapshot"] += int((recv[ns_mask] < ev[ns_mask]).sum())
        a["ts_event_before_file_start"] += int((ev < start_ns).sum())
        a["ts_event_before_2020-12-01T00Z_count"] += int((ev < seal_ns).sum())
        evn = ev[ns_mask]
        a["ts_event_multiple_of_1us"] += int((evn % 1000 == 0).sum())
        a["ts_event_multiple_of_1ms"] += int((evn % 1_000_000 == 0).sum())
        a["ts_recv_multiple_of_1us"] += int((recv[ns_mask] % 1000 == 0).sum())
        if "ts_in_delta" in chunk.dtype.names:
            a["ts_in_delta_negative"] += int((chunk["ts_in_delta"][ns_mask] < 0).sum())
        lat += np.histogram(recv[ns_mask] - evn, bins=LAT_EDGES)[0]
        idx = np.searchsorted(bounds, recv, side="right") - 1
        per_day += np.bincount(idx, minlength=len(days))
        per_day_events += np.bincount(idx[last], minlength=len(days))
        act = as_u8(chunk["action"]) if "action" in chunk.dtype.names else np.zeros(n, np.uint8)
        side = as_u8(chunk["side"]) if "side" in chunk.dtype.names else np.zeros(n, np.uint8)
        per_day_act += np.bincount(idx * 256 + act, minlength=len(days) * 256).reshape(-1, 256)
        keys, cnt = np.unique(act.astype(np.int64) * 256 + side, return_counts=True)
        for k, c in zip(keys.tolist(), cnt.tolist(), strict=True):
            add(act_side, f"{chr(k // 256) if k // 256 else '0'}:{chr(k % 256) if k % 256 else '0'}", c)
        for i in np.unique(iid).tolist():
            m = iid == i
            si = str(i)
            dd = per_day_iid.setdefault(si, {})
            bc = np.bincount(idx[m], minlength=len(days))
            for j in np.nonzero(bc)[0].tolist():
                add(dd, days[j].isoformat(), bc[j])
            ia = iid_act.setdefault(si, {})
            ab = np.bincount(act[m], minlength=256)
            for j in np.nonzero(ab)[0].tolist():
                add(ia, chr(j) if j else "0", ab[j])
            # record-level ts_recv ties and decreases (all records, file order)
            r = recv[m]
            prev = carry.last_recv.get(i, -1)
            rr = np.concatenate(([prev], r))
            a["recv_ties_record_level"] += int((rr[1:] == rr[:-1]).sum())
            a["recv_decreases_per_instrument"] += int((rr[1:] < rr[:-1]).sum())
            carry.last_recv[i] = int(r[-1])
            # ts_event ties and inversions over non-snapshot records
            mn = m & ns_mask
            if mn.any():
                e = ev[mn]
                pl = carry.last_ev.get(i, -1)
                ee = np.concatenate(([pl], e))
                a["event_ties_record_level_nonsnapshot"] += int((ee[1:] == ee[:-1]).sum())
                pm = carry.max_ev.get(i, -1)
                em = np.concatenate(([pm], e))
                cm = np.maximum.accumulate(em)
                a["event_inversions_nonsnapshot"] += int((em[1:] < cm[:-1]).sum())
                carry.last_ev[i] = int(e[-1])
                carry.max_ev[i] = int(cm[-1])
                ml = mn & last
                if ml.any():
                    e2 = ev[ml]
                    p2 = carry.last_ev_event.get(i, -1)
                    e2e = np.concatenate(([p2], e2))
                    a["event_ties_between_F_LAST_events"] += int((e2e[1:] == e2e[:-1]).sum())
                    carry.last_ev_event[i] = int(e2[-1])
    res["decode_wall_s"] = round(time.perf_counter() - t0, 3)
    res["decode_cpu_s"] = round(time.process_time() - c0, 3)
    res["ndarray_fields"] = dtype_info
    res["counts"] = a
    res["flags"] = flags_cnt
    res["latency_hist_recv_minus_event_nonsnapshot"] = dict(
        zip(LAT_LABELS, lat.tolist(), strict=True))
    res["action_side_counts"] = act_side
    res["instrument_action_counts"] = iid_act
    res["per_day_instrument_counts"] = per_day_iid
    cal = load_group_calendar("grains")
    rows = []
    for j, d in enumerate(days):
        if per_day[j] == 0:
            continue
        acts = {chr(k) if k else "0": int(per_day_act[j, k]) for k in np.nonzero(per_day_act[j])[0]}
        rows.append({"day": d.isoformat(), "records": int(per_day[j]),
                     "events_F_LAST": int(per_day_events[j]), "actions": acts,
                     "regular_trade_date": bool(cal.covers(d) and cal.is_trade_date(d)),
                     "in_file_month": d.strftime("%Y-%m") == res["month"]})
    res["per_day"] = rows


def scan_definitions(store, res: dict) -> None:
    t0, c0 = time.perf_counter(), time.process_time()
    per_iid: dict[str, dict] = {}
    cls_cnt: dict[str, int] = {}
    n = 0
    dtype_info = None
    for chunk in store.to_ndarray(count=200_000):
        if len(chunk) == 0:
            continue
        if dtype_info is None:
            dtype_info = [[nm, str(chunk.dtype[nm])] for nm in chunk.dtype.names]
            res["ndarray_itemsize"] = int(chunk.dtype.itemsize)
        names = chunk.dtype.names
        recv = chunk["ts_recv"].astype(np.int64)
        if int(recv.max()) >= CUTOFF_NS:
            raise Refused("definition record on or after 2024-03-01")
        n += len(chunk)
        for k in range(len(chunk)):
            r = chunk[k]
            cls = r["instrument_class"]
            cls = cls.decode() if isinstance(cls, bytes) else str(cls)
            add(cls_cnt, cls, 1)
            raw = r["raw_symbol"]
            raw = raw.decode("ascii", "replace").rstrip("\x00") if isinstance(raw, bytes) else str(raw)
            i = str(int(r["instrument_id"]))
            ent = per_iid.get(i)
            if ent is None:
                ent = {"raw_symbol": raw, "instrument_class": cls, "n": 0,
                       "first_ts_recv": int(r["ts_recv"]), "symbols_seen": []}
                if cls == "F" and raw[:2] in ("ZM", "ZS", "ZL") and "-" not in raw:
                    for f in DEF_KEEP:
                        if f in names and f not in ent:
                            v = r[f]
                            if isinstance(v, (bytes, np.bytes_)):
                                v = v.decode("ascii", "replace").rstrip("\x00")
                            elif isinstance(v, np.generic):
                                v = v.item()
                            ent[f] = v
                per_iid[i] = ent
            ent["n"] += 1
            ent["last_ts_recv"] = int(r["ts_recv"])
            if raw != ent["raw_symbol"] and raw not in ent["symbols_seen"]:
                ent["symbols_seen"].append(raw)
    res["decode_wall_s"] = round(time.perf_counter() - t0, 3)
    res["decode_cpu_s"] = round(time.process_time() - c0, 3)
    res["ndarray_fields"] = dtype_info
    res["counts"] = {"records": n, "instruments": len(per_iid)}
    res["instrument_class_counts"] = cls_cnt
    res["outrights"] = {k: v for k, v in per_iid.items()
                        if v["instrument_class"] == "F" and v["raw_symbol"][:2] in ("ZM", "ZS", "ZL")
                        and "-" not in v["raw_symbol"]}
    res["outright_ids_all_records"] = sorted(res["outrights"])


def scan_file(series: str, path: Path, manifest_entry: dict) -> dict:
    import databento as db
    a, b = guard_name(path)
    res: dict = {"series": series, "month": manifest_entry["month"], "file": path.name,
                 "name_start": a, "name_end": b, "bytes_compressed": path.stat().st_size,
                 "manifest_bytes": manifest_entry["bytes"],
                 "manifest_records": manifest_entry["records"],
                 "manifest_delivered_record_bytes": manifest_entry["delivered_record_bytes"]}
    res["bytes_decompressed_dbn"], res["decompress_wall_s"] = decompressed_bytes(path)
    store = db.DBNStore.from_file(path)
    meta = store.metadata
    if meta.end is None or int(meta.end) > 1_709_244_000 * NS:
        raise Refused("metadata end after 2024-02-29T22Z")
    res["metadata"] = {"version": int(meta.version), "schema": str(meta.schema),
                       "stype_in": str(meta.stype_in), "stype_out": str(meta.stype_out),
                       "start": int(meta.start), "end": int(meta.end),
                       "symbols": list(meta.symbols)}
    if series == "Z4":
        scan_definitions(store, res)
    else:
        scan_records(store, series, int(meta.start), int(meta.end), res)
    res["peak_rss_mb_process_so_far"] = round(
        resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
    return res


def main(argv: list[str]) -> int:
    os.nice(10)
    OUT.mkdir(parents=True, exist_ok=True)
    for series in argv:
        man = json.loads((SERIES_DIR[series] / "manifest.json").read_text())
        entries = sorted((f for f in man["files"] if f["series"] == series),
                         key=lambda f: f["month"])
        for ent in entries:
            out = OUT / f"{series}_{ent['month']}.json"
            if out.is_file():
                continue
            path = SERIES_DIR[series] / Path(ent["path"]).name
            t0 = time.perf_counter()
            res = scan_file(series, path, ent)
            res["file_wall_s"] = round(time.perf_counter() - t0, 3)
            tmp = out.with_suffix(".tmp")
            tmp.write_text(json.dumps(res, indent=0, default=str))
            tmp.replace(out)
            print(f"{series} {ent['month']} records={res['counts']['records']} "
                  f"wall={res['file_wall_s']}s rss={res['peak_rss_mb_process_so_far']}MB",
                  flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
