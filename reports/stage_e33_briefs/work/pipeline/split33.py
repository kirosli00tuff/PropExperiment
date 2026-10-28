"""The E.33 ZS/ZL per-trade-date MBP-1 split (brief_DataCoder deliverable 3; P1.1, F 6.3 item 3).

For each of the 816 trade dates D (P1.4) and root in {ZS, ZL}: every record of the raw Z2/Z3
discovery files with ts_recv in [D-1 16:00 CT, D 16:00 CT) (data33.window), every MBP-1 field
(data33.MBP1_SPLIT; the length byte dropped), in file order (= ts_recv order; a decrease stops
the run), to DERIVED/split/<root>/<YYYY-MM-DD>.npy plus a <YYYY-MM-DD>.DONE marker (JSON with the
record count and source months). A window that crosses a month-file boundary (summer: the
21:00-22:00 UTC hour) takes records from both files. Records outside every trade-date window
(weekends, closures) are counted, not stored.

Resumable: a file is skipped only when every trade date whose window meets its request range is
DONE; DONE dates are not rewritten. Runs at nice 10, one process per root. Refuses to start a new
file between 15:28 and 16:00 America/Vancouver (exit 3); rerun after 16:00 to resume.
Final step: DERIVED/split/<root>/split_manifest.json (source sha256 from the discovery manifest,
per-date counts, totals). CLI: split33.py ZS | ZL | manifest ZS | manifest ZL
"""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, date, datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import data33 as d33  # noqa: E402
import guard33 as g  # noqa: E402
import measure31 as m31  # noqa: E402

PACIFIC = ZoneInfo("America/Vancouver")
QUIET_FROM, QUIET_TO = time(15, 28), time(16, 0)
N_DATES = 816


def trade_dates() -> list[date]:
    months = sorted({sf.month for sf in d33.source_files()["Z1"]})
    days = m31.month_trade_dates(m31.grains(), months)
    if len(days) != N_DATES:
        raise RuntimeError(f"expected {N_DATES} trade dates, found {len(days)}")
    return days


def _quiet_now() -> bool:
    return QUIET_FROM <= datetime.now(PACIFIC).time() < QUIET_TO


def _done(root: str, day: date) -> bool:
    return d33.mbp1_path(root, day).with_suffix(d33.DONE_SUFFIX).is_file()


def _req_ns(stamp: str) -> int:
    return int(datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp()) * g.NS


def _compact(raw: np.ndarray) -> np.ndarray:
    out = np.empty(len(raw), dtype=d33.MBP1_SPLIT)
    for name in d33.MBP1_SPLIT.names:
        src = raw[name]
        if src.dtype.kind == "S":
            src = src.astype("S1").view(np.uint8)
        out[name] = src
    return out


def _write(root: str, day: date, parts: list[np.ndarray], months: list[str]) -> int:
    path = g.check_request(d33.mbp1_path(root, day), day, day)
    arr = np.concatenate(parts) if parts else np.empty(0, dtype=d33.MBP1_SPLIT)
    tmp = path.with_name(f".{path.name}.tmp")
    with tmp.open("wb") as fh:
        np.save(fh, arr)
    tmp.replace(path)
    marker = {"records": int(len(arr)), "source_months": sorted(set(months)),
              "written": datetime.now(UTC).isoformat()}
    done = path.with_suffix(d33.DONE_SUFFIX)
    done_tmp = done.with_name(f".{done.name}.tmp")
    done_tmp.write_text(json.dumps(marker) + "\n", encoding="utf-8")
    done_tmp.replace(done)
    return len(arr)


def split_root(root: str) -> dict:
    series = d33.ROOT_SERIES[root]
    days = trade_dates()
    lo = np.array([d33.window(d)[0] for d in days], dtype=np.int64)
    hi = np.array([d33.window(d)[1] for d in days], dtype=np.int64)
    if np.any(lo[1:] < hi[:-1]):
        raise RuntimeError("trade-date windows overlap")
    folder = d33.SPLIT_ROOT / root
    folder.mkdir(parents=True, exist_ok=True)
    g.check_path(folder)
    pending: dict[int, list[np.ndarray]] = {}
    pending_months: dict[int, list[str]] = {}
    stats = {"files_processed": 0, "files_skipped": 0, "records_read": 0,
             "outside_trade_dates": {}, "dates_written": 0}
    last_ts: int | None = None
    for sf in d33.source_files()[series]:
        f_lo, f_hi = _req_ns(sf.start), _req_ns(sf.end)
        meets = [j for j in range(len(days)) if lo[j] < f_hi and hi[j] > f_lo]
        if all(_done(root, days[j]) for j in meets):
            stats["files_skipped"] += 1
            last_ts = None
            continue
        if _quiet_now():
            print(f"{datetime.now(PACIFIC):%H:%M:%S} quiet window 15:28-16:00 PDT: stopped before "
                  f"{sf.month}; rerun after 16:00 to resume", flush=True)
            raise SystemExit(3)
        outside = 0
        for raw in d33._decode(sf):
            ts = raw["ts_recv"].astype(np.int64)
            if np.any(np.diff(ts) < 0) or (last_ts is not None and ts[0] < last_ts):
                raise RuntimeError(f"{sf.path}: ts_recv decreases in file order; stopped")
            last_ts = int(ts[-1])
            stats["records_read"] += len(ts)
            rec = _compact(raw)
            first = max(int(np.searchsorted(hi, ts[0], side="right")), 0)
            last = int(np.searchsorted(lo, ts[-1], side="right")) - 1
            kept = 0
            for j in range(first, last + 1):
                a = int(np.searchsorted(ts, lo[j], side="left"))
                b = int(np.searchsorted(ts, hi[j], side="left"))
                if b > a:
                    pending.setdefault(j, []).append(rec[a:b])
                    pending_months.setdefault(j, []).append(sf.month)
                    kept += b - a
            outside += len(ts) - kept
            for j in sorted(k for k in pending if hi[k] <= last_ts):
                _flush(root, days[j], pending.pop(j), pending_months.pop(j), stats)
        for j in sorted(k for k in pending if hi[k] <= f_hi):
            _flush(root, days[j], pending.pop(j), pending_months.pop(j), stats)
        for j in meets:  # a met date with no record at all in its whole window
            if hi[j] <= f_hi and j not in pending and not _done(root, days[j]):
                _flush(root, days[j], [], [sf.month], stats)
        stats["outside_trade_dates"][sf.month] = outside
        stats["files_processed"] += 1
        print(f"{datetime.now(PACIFIC):%H:%M:%S} {root} {sf.month} done", flush=True)
    if pending:
        raise RuntimeError(f"{root}: dates left pending at the end: "
                           f"{[days[j].isoformat() for j in pending]}")
    return stats


def _flush(root: str, day: date, parts: list[np.ndarray], months: list[str], stats: dict) -> None:
    if _done(root, day):
        return
    _write(root, day, parts, months)
    stats["dates_written"] += 1


def write_manifest(root: str, stats: dict | None = None) -> dict:
    series = d33.ROOT_SERIES[root]
    days = trade_dates()
    folder = d33.SPLIT_ROOT / root
    counts, missing = {}, []
    for day in days:
        done = d33.mbp1_path(root, day).with_suffix(d33.DONE_SUFFIX)
        if done.is_file():
            counts[day.isoformat()] = int(json.loads(done.read_text(encoding="utf-8"))["records"])
        else:
            missing.append(day.isoformat())
    man = {"root": root, "series": series, "trade_dates": len(days), "dates_done": len(counts),
           "missing": missing, "total_records": int(sum(counts.values())),
           "zero_record_dates": [k for k, v in counts.items() if v == 0],
           "dtype": [list(x) for x in d33.MBP1_SPLIT.descr],
           "window": "[D-1 16:00 CT, D 16:00 CT) by ts_recv (measure31.day_bounds)",
           "sources": [{"month": sf.month, "path": str(sf.path), "sha256": sf.sha256}
                       for sf in d33.source_files()[series]],
           "discovery_manifest_sha256": g.DISCOVERY_MANIFEST_SHA256,
           "per_date_records": counts, "last_run": stats,
           "written": datetime.now(UTC).isoformat()}
    out = folder / "split_manifest.json"
    tmp = out.with_name(f".{out.name}.tmp")
    tmp.write_text(json.dumps(man, indent=1) + "\n", encoding="utf-8")
    tmp.replace(out)
    return man


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    os.nice(10)
    if len(args) == 1 and args[0] in d33.ROOT_SERIES:
        stats = split_root(args[0])
        man = write_manifest(args[0], stats)
    elif len(args) == 2 and args[0] == "manifest" and args[1] in d33.ROOT_SERIES:
        man = write_manifest(args[1])
    else:
        print(__doc__)
        return 2
    print(json.dumps({k: man[k] for k in ("root", "dates_done", "total_records",
                                          "zero_record_dates")} | {"missing": len(man["missing"])}))
    print(json.dumps(man["last_run"]) if man.get("last_run") else "")
    return 0 if not man["missing"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
