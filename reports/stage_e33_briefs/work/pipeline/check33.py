"""Independent raw-file record counts per trade date (P1.1 store check; split check).

``raw_counts(series, dates)`` decodes the raw discovery files whose request range meets each
trade date's window [D-1 16:00 CT, D 16:00 CT) and counts, from the raw records in file order:
records with ts_recv inside the window, ts_recv decreases over the window's records (the whole
feed, file order) and ts_recv decreases per instrument. The window is computed here with zoneinfo,
not with measure31.day_bounds or data33.window, so the count does not share the split's code.

CLI:
  check33.py e31-store D1 D2 D3      ZM: E.31 store length and marker count vs the raw count
  check33.py split ROOT D1 D2 D3     ZS/ZL: E.33 split length and DONE count vs the raw count
  check33.py e31-all                 ZM: all 816 dates, one pass over the 39 raw Z1 files
Prints one line per date (counts only; no market values).
"""

from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import data33 as d33  # noqa: E402
import guard33 as g  # noqa: E402
import measure31 as m31  # noqa: E402

CHICAGO = ZoneInfo("America/Chicago")


def _window(day: date) -> tuple[int, int]:
    prev = day - timedelta(days=1)
    lo = datetime(prev.year, prev.month, prev.day, 16, 0, tzinfo=CHICAGO)
    hi = datetime(day.year, day.month, day.day, 16, 0, tzinfo=CHICAGO)
    return int(lo.timestamp()) * g.NS, int(hi.timestamp()) * g.NS


def _req_ns(stamp: str) -> int:
    return int(datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp()) * g.NS


def raw_counts(series: str, days: list[date]) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    files = d33.source_files()[series]
    for day in days:
        g.check_date(day)
        lo, hi = _window(day)
        count, feed_dec, inst_dec = 0, 0, 0
        last_feed: int | None = None
        last_inst: dict[int, int] = {}
        for sf in files:
            if not (_req_ns(sf.start) < hi and _req_ns(sf.end) > lo):
                continue
            g.check_path(sf.path)
            store = m31.open_store(sf)
            for chunk in store.to_ndarray(count=m31.DEFAULT_CHUNK):
                ts = chunk["ts_recv"].astype(np.int64)
                sel = (ts >= lo) & (ts < hi)
                if not sel.any():
                    continue
                g.check_records(ts[sel], chunk["ts_event"][sel], str(sf.path))
                t = ts[sel]
                ids = chunk["instrument_id"][sel]
                count += len(t)
                feed_dec += int(np.count_nonzero(np.diff(t) < 0))
                if last_feed is not None and t[0] < last_feed:
                    feed_dec += 1
                last_feed = int(t[-1])
                for iid in np.unique(ids).tolist():
                    ti = t[ids == iid]
                    inst_dec += int(np.count_nonzero(np.diff(ti) < 0))
                    if iid in last_inst and ti[0] < last_inst[iid]:
                        inst_dec += 1
                    last_inst[iid] = int(ti[-1])
        out[day.isoformat()] = {"raw_records": count, "ts_recv_decreases_feed": feed_dec,
                                "ts_recv_decreases_per_instrument": inst_dec}
    return out


def check_e31_store(days: list[date]) -> list[dict]:
    rows = []
    raw = raw_counts("Z1", days)
    markers = d33._e31_markers_ok()
    for day in days:
        path = g.check_request(d33.zm_path(day), day, day)
        stored = np.load(path, mmap_mode="r")
        row = {"date": day.isoformat(), "store_records": int(len(stored)),
               "marker_records": markers[f"{day:%Y-%m}"].get(day.isoformat()),
               "store_ts_recv_decreases": d33.ts_recv_decreases(np.asarray(stored["ts_recv"])),
               **raw[day.isoformat()]}
        row["equal"] = row["store_records"] == row["marker_records"] == row["raw_records"]
        rows.append(row)
    return rows


def check_split(root: str, days: list[date]) -> list[dict]:
    rows = []
    raw = raw_counts(d33.ROOT_SERIES[root], days)
    for day in days:
        path = g.check_request(d33.mbp1_path(root, day), day, day)
        stored = np.load(path, mmap_mode="r")
        done = json.loads(path.with_suffix(d33.DONE_SUFFIX).read_text(encoding="utf-8"))
        row = {"date": day.isoformat(), "split_records": int(len(stored)),
               "done_records": int(done["records"]),
               "split_ts_recv_decreases": d33.ts_recv_decreases(np.asarray(stored["ts_recv"])),
               **raw[day.isoformat()]}
        row["equal"] = row["split_records"] == row["done_records"] == row["raw_records"]
        rows.append(row)
    return rows


def full_counts(series: str, days: list[date]) -> tuple[dict[str, int], int, int]:
    """One pass over every raw file of a series: records per trade-date window (all dates at
    once), records outside every window, and ts_recv decreases in file order (whole series)."""
    lo = np.array([_window(d)[0] for d in days], dtype=np.int64)
    hi = np.array([_window(d)[1] for d in days], dtype=np.int64)
    counts = np.zeros(len(days), dtype=np.int64)
    outside, dec, last = 0, 0, None
    for sf in d33.source_files()[series]:
        g.check_path(sf.path)
        for chunk in m31.open_store(sf).to_ndarray(count=m31.DEFAULT_CHUNK):
            ts = chunk["ts_recv"].astype(np.int64)
            g.check_records(ts, chunk["ts_event"], str(sf.path))
            dec += int(np.count_nonzero(np.diff(ts) < 0)) + int(last is not None and ts[0] < last)
            last = int(ts[-1])
            j = np.searchsorted(lo, ts, side="right") - 1
            ok = (j >= 0) & (ts < hi[np.clip(j, 0, None)])
            np.add.at(counts, j[ok], 1)
            outside += int(np.count_nonzero(~ok))
    return {d.isoformat(): int(n) for d, n in zip(days, counts, strict=True)}, outside, dec


def check_e31_all() -> dict:
    """P1.1 store check on every one of the 816 trade dates (beyond the 3 the protocol asks)."""
    days = m31.month_trade_dates(m31.grains(), sorted({sf.month for sf in
                                                       d33.source_files()["Z1"]}))
    raw, outside, dec = full_counts("Z1", days)
    markers = d33._e31_markers_ok()
    diff = []
    for day in days:
        path = g.check_request(d33.zm_path(day), day, day)
        n = int(len(np.load(path, mmap_mode="r")))
        if not n == markers[f"{day:%Y-%m}"][day.isoformat()] == raw[day.isoformat()]:
            diff.append(day.isoformat())
    return {"dates": len(days), "dates_differing": diff, "raw_records_in_windows":
            sum(raw.values()), "raw_records_outside_windows": outside,
            "ts_recv_decreases_file_order": dec}


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args == ["e31-all"]:
        res = check_e31_all()
        print(json.dumps(res))
        return 0 if not res["dates_differing"] else 1
    if len(args) >= 2 and args[0] == "e31-store":
        rows = check_e31_store([date.fromisoformat(a) for a in args[1:]])
    elif len(args) >= 3 and args[0] == "split":
        rows = check_split(args[1], [date.fromisoformat(a) for a in args[2:]])
    else:
        print(__doc__)
        return 2
    for row in rows:
        print(json.dumps(row))
    return 0 if all(r["equal"] for r in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
