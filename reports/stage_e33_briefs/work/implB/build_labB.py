"""Build implementation B's label and outcome tables (INTERFACE.md 4.2) for chosen dates.

Usage (repo root):
  nice -n 10 uv run python reports/stage_e33_briefs/work/implB/build_labB.py --dates b3 \
      [--workers 3] [--out DIR] [--sigma auto|feature|own]

--dates: "b3" (the 20 B3 agreement dates), a comma list of YYYY-MM-DD, or a file with one date
per line. Output under DIR (default DERIVED/implB/labels): <LABEL>/<D>.parquet, <LABEL>/_excl/
<D>.json, _day/<D>.json (front, limits flag, sigma and its source, book counts, timing),
_mids/<D>.npz (2 x mid at the minute marks 08:35..13:13, for sigma), manifest.json.
A date with _day/<D>.json is skipped on restart (resumable). Prints counts and timings only
(INTERFACE.md 2 rule 1): no statistic of labels, nets, classes or returns.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import date
from datetime import time as dtime
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PIPELINE = HERE.parent / "pipeline"
for _p in (str(PIPELINE), str(HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import guard33 as g  # noqa: E402
import labB as lb  # noqa: E402
import labB_book as bk  # noqa: E402
import labB_cal as cal  # noqa: E402

DERIVED_B = g.DERIVED / "implB"
OUT_DEFAULT = DERIVED_B / "labels"
FEATURE_DAY = DERIVED_B / "features" / "_day"
CODE_FILES = ("labB.py", "labB_book.py", "labB_cal.py", "build_labB.py")
PROTOCOL_SHA = "c4ffb9d79af4bbbf10574ac138668aa49a80b22a8f5fba5879184d357d2c7e05"
MAX_WORKERS = 3
MIN_AVAILABLE_MB = 2048
REPLAY_STOP = dtime(13, 20)  # records with ts_recv < 13:20:00 CT are all a label can use
MIDS_STOP = dtime(13, 13)  # the last sigma minute mark


def available_mb() -> int:
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) // 1024
    raise RuntimeError("MemAvailable not found")


def memory_guard() -> None:
    mb = available_mb()
    if mb < MIN_AVAILABLE_MB:
        raise SystemExit(f"stopped: available memory {mb} MB < {MIN_AVAILABLE_MB} MB")


def code_manifest() -> dict:
    shas = {f: hashlib.sha256((HERE / f).read_bytes()).hexdigest() for f in CODE_FILES}
    joined = hashlib.sha256(b"".join((HERE / f).read_bytes() for f in CODE_FILES)).hexdigest()
    return {"files": shas, "code_sha12": joined[:12], "protocol_sha256": PROTOCOL_SHA}


def _nice() -> None:
    try:
        if os.nice(0) < 10:
            os.nice(10 - os.nice(0))
    except OSError:
        pass


def replay(day: date, stop: dtime, inclusive: bool) -> tuple[lb.Updates, dict, int]:
    """The front's book updates of ``day`` from records with ts_recv < stop (labels: an exit
    fallback must come before 13:20:00) or <= stop (sigma: the as-of at the 13:13:00 mark)."""
    import data33  # noqa: PLC0415
    iid = cal.zm_front(day)
    if iid is None:
        raise RuntimeError(f"{day}: no ZM.v.0 mapping")
    cutoff = lb.ct_ns(day, stop) - (0 if inclusive else 1)
    rec = data33.load_zm(day, cutoff_ns=cutoff)
    upd, counts = bk.front_updates(rec, iid, cal.zm_tick())
    counts["records_all_instruments"] = int(len(rec))
    if data33.ORDER_LOG:
        counts["data33_order_log"] = dict(data33.ORDER_LOG)
    return upd, counts, int(iid)


def mids_task(day_s: str, out: str) -> tuple[str, float]:
    """Minute-mark mids of one history date (book states only), cached."""
    _nice()
    day = date.fromisoformat(day_s)
    path = Path(out) / "_mids" / f"{day_s}.npz"
    if path.is_file():
        return day_s, 0.0
    t0 = time.time()
    upd, counts, iid = replay(day, MIDS_STOP, inclusive=True)
    s2, valid = bk.minute_mids(upd, day)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp.npz")
    np.savez(tmp, s2=s2, valid=valid, iid=np.int64(iid))
    tmp.replace(path)
    return day_s, time.time() - t0


def sigma_own(day: date, out: Path) -> float | None:  # READING LB-16
    hist = []
    for prev in cal.previous_trade_dates(day, bk.SIGMA_LOOKBACK):
        with np.load(out / "_mids" / f"{prev.isoformat()}.npz") as z:
            hist.append((z["s2"].astype(np.int64), z["valid"].astype(bool)))
    return bk.sigma_from_mids(hist)


def sigma_feature(day: date) -> tuple[float | None, bool]:
    path = FEATURE_DAY / f"{day.isoformat()}.json"
    if not path.is_file():
        return None, False
    data = json.loads(g.check_path(path).read_text(encoding="utf-8"))
    v = data.get("sigma_zm")
    return (None if v is None else float(v)), True


def write_parquet(cols: dict[str, np.ndarray], path: Path) -> None:
    import pyarrow as pa  # noqa: PLC0415
    import pyarrow.parquet as pq  # noqa: PLC0415
    table = pa.table({k: pa.array(v) for k, v in cols.items()})
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp.parquet")
    pq.write_table(table, tmp)
    tmp.replace(path)


def write_json(obj: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp.json")
    tmp.write_text(json.dumps(obj, indent=1, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def label_task(day_s: str, out_s: str, sigma_mode: str) -> dict:
    """All six label tables of one date; the _day json is written last (the done marker)."""
    _nice()
    out = Path(out_s)
    day = date.fromisoformat(day_s)
    marker = out / "_day" / f"{day_s}.json"
    if marker.is_file():
        return {"date": day_s, "skipped": True}
    t0 = time.time()
    upd, counts, iid = replay(day, REPLAY_STOP, inclusive=False)
    t_replay = time.time() - t0
    burn_in = day in set(cal.burn_in_dates())
    excl = cal.exclusions()
    limits, limit_skip = cal.limit_prices(day, iid)
    rel, _found = cal.releases()
    sig_feat, has_feat = sigma_feature(day) if sigma_mode in ("auto", "feature") else (None,
                                                                                      False)
    if sigma_mode == "feature" and not has_feat:
        raise RuntimeError(f"{day}: no FeatureCoder2 sigma file")
    if has_feat:
        sigma, source = sig_feat, "implB/features/_day sigma_zm (FeatureCoder2)"
    else:
        sigma, source = sigma_own(day, out), "own (LabelCoder2, P0.3)"
    ctx = lb.DayContext(day=day, excluded=day in excl, exclusion_reasons=excl.get(day, ()),
                        releases_ns=rel.get(day, ()), limits=limits, sigma_ticks=sigma)
    per_label = {}
    for label in lb.LABELS:
        t1 = time.time()
        cols, ex = lb.label_table(upd, ctx, label, burn_in=burn_in)
        ex["limit_skip_reason"] = limit_skip
        write_parquet(cols, out / label / f"{day_s}.parquet")
        write_json(ex, out / label / "_excl" / f"{day_s}.json")
        per_label[label] = {"rows": ex["rows"], "entry_minutes": ex["entry_minutes"],
                            "seconds": round(time.time() - t1, 3)}
    info = {"date": day_s, "front_instrument_id": iid, "burn_in": burn_in,
            "excluded": ctx.excluded, "exclusion_reasons": list(ctx.exclusion_reasons),
            "limits_present": limits is not None, "limit_skip_reason": limit_skip,
            "n_releases": len(ctx.releases_ns), "sigma_zm_ticks": sigma,
            "sigma_source": source, "book_counts": counts, "n_updates": int(len(upd.t)),
            "seconds_replay": round(t_replay, 3), "seconds_total": round(time.time() - t0, 3),
            "labels": per_label}
    write_json(info, marker)
    return info


def parse_dates(arg: str) -> list[date]:
    if arg == "b3":
        return cal.b3_dates()
    p = Path(arg)
    items = p.read_text().split() if p.is_file() else arg.split(",")
    return sorted(date.fromisoformat(x.strip()) for x in items if x.strip())


def run_pool(fn, jobs: list[tuple], workers: int) -> list:  # noqa: ANN001
    results = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futs = {}
        for job in jobs:
            memory_guard()
            futs[pool.submit(fn, *job)] = job
        for fut in as_completed(futs):
            results.append(fut.result())
    return results


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dates", required=True)
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    ap.add_argument("--workers", type=int, default=MAX_WORKERS)
    ap.add_argument("--sigma", choices=("auto", "feature", "own"), default="auto")
    args = ap.parse_args(argv)
    _nice()
    workers = max(1, min(args.workers, MAX_WORKERS))
    out = Path(args.out)
    g.check_path(out)
    memory_guard()
    days = parse_dates(args.dates)
    universe = set(cal.trade_dates())
    if any(d not in universe for d in days):
        raise SystemExit("a requested date is not one of the 816 trade dates")
    _rel, found = cal.releases()
    print("release counts (P3.6 rule 3, asserted):", json.dumps(found))
    t0 = time.time()
    need_hist = sorted({p for d in days if d not in set(cal.burn_in_dates())
                        and not (args.sigma != "own" and sigma_feature(d)[1])
                        for p in cal.previous_trade_dates(d, bk.SIGMA_LOOKBACK)})
    if need_hist:
        print(f"sigma history: {len(need_hist)} dates to replay (own sigma)")
        res = run_pool(mids_task, [(d.isoformat(), str(out)) for d in need_hist], workers)
        print(f"sigma history done: {len(res)} dates, {time.time() - t0:.1f} s")
    t1 = time.time()
    res = run_pool(label_task, [(d.isoformat(), str(out), args.sigma) for d in days], workers)
    for r in sorted(res, key=lambda x: x["date"]):
        if r.get("skipped"):
            print(r["date"], "skipped (done)")
            continue
        rows = " ".join(f"{k}:{v['rows']}/{v['entry_minutes']}" for k, v in r["labels"].items())
        print(r["date"], "excl" if r["excluded"] else "-", f"upd {r['n_updates']}",
              f"replay {r['seconds_replay']}s total {r['seconds_total']}s", "rows/entries",
              rows)
    manifest = {**code_manifest(), "dates": [d.isoformat() for d in days],
                "sigma_mode": args.sigma, "built_at_unix": int(time.time()),
                "seconds_history": round(t1 - t0, 1), "seconds_labels": round(time.time() - t1, 1)}
    write_json(manifest, out / "manifest.json")
    print(f"done: {len(res)} dates in {time.time() - t0:.1f} s; code_sha12 "
          f"{manifest['code_sha12']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
