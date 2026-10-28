"""Implementation B feature builder (E.33 B2): day raws, then the INTERFACE 4.1 tables.

Usage (repo root):
  nice -n 10 uv run python reports/stage_e33_briefs/work/implB/build_featB.py \
      --dates b3|all|2021-01-19,2021-01-25|<file> [--workers 3] [--cutoff-ns N] [--out DIR]

Outputs (DIR defaults to DERIVED/implB):
  dayraw/<code_sha12>/<D>.npz            one replay per date (resumable: an existing file is kept)
  features/<code_sha12>/<D>.parquet      OOF dates only: date, i, t_ns, the 59 features
  features/<code_sha12>/_day/<D>.json    sigma_zm, sigma_zs, sigma_zl (ticks; null if undefined)
  features/<code_sha12>/manifest.json    code files and sha256, dates, counts, timings
With --cutoff-ns (LT1, P4.1): every input stream of the target date is truncated at
ts_recv <= cutoff; history day raws are reused only when their whole ts_recv window ends at or
before the cutoff (they then contain no record after it; READING B-LT1-1), else rebuilt with the
cutoff. Outputs go under DIR/lt1/<cutoff>/.
Real-data runs: nice 10, at most 3 processes, `free -m` checked first (stop below 2.5 GB).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import UTC, date, datetime
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import calB  # noqa: E402
import data33  # noqa: E402
import dayB  # noqa: E402
import featB  # noqa: E402
import guard33  # noqa: E402

CODE_FILES = ("calB.py", "replayB.py", "dayB.py", "featB.py", "build_featB.py")
OUT_DEFAULT = guard33.DERIVED / "implB"
MAX_WORKERS = 3
MIN_AVAILABLE_MB = 2560  # lead 2026-10-28: stop below 2.5 GB
N_HIST_RAW = 21  # 20 trade dates before D plus the previous trade date of the oldest (gaps)
B3_SEED, B3_N = 20261028, 20


def code_sha() -> tuple[str, dict[str, str]]:
    files = {}
    digest = hashlib.sha256()
    for name in CODE_FILES:
        data = (HERE / name).read_bytes()
        files[name] = hashlib.sha256(data).hexdigest()
        digest.update(data)
    return digest.hexdigest()[:12], files


def b3_dates() -> list[date]:
    """reports/stage_e33_STATE.md 14:45: OOF sorted; rng(20261028).choice(796, 20, False)."""
    oof = list(calB.oof_dates())
    idx = np.random.default_rng(B3_SEED).choice(len(oof), B3_N, replace=False)
    return sorted(oof[int(k)] for k in idx)


def parse_dates(spec: str) -> list[date]:
    if spec == "b3":
        return b3_dates()
    if spec == "all":
        return list(calB.trade_dates())
    path = Path(spec)
    if path.is_file():
        return sorted({date.fromisoformat(x.strip()) for x in path.read_text().split()
                       if x.strip()})
    return sorted({date.fromisoformat(x.strip()) for x in spec.split(",") if x.strip()})


def available_mb() -> int:
    out = subprocess.run(["free", "-m"], capture_output=True, text=True, check=True).stdout
    return int(out.splitlines()[1].split()[6])


# ------------------------------------------------------------------ raw cache ----
def save_raw(path: Path, raw: dict) -> None:
    tmp = path.with_name(f".{path.stem}.tmp.npz")
    arrays = {k: np.asarray(v) for k, v in raw.items()}
    np.savez(tmp, **arrays)
    tmp.replace(path)


def load_raw(path: Path) -> dict:
    guard33.check_path(path)
    with np.load(path, allow_pickle=False) as z:
        out = {}
        for k in z.files:
            v = z[k]
            out[k] = v.item() if v.ndim == 0 else v
    return out


def _worker_init() -> None:
    os.nice(10)


def raw_job(day: str, path: str, cutoff_ns: int | None) -> tuple[str, float, dict]:
    t0 = time.time()
    raw = dayB.day_raw(date.fromisoformat(day), cutoff_ns)
    save_raw(Path(path), raw)
    return day, time.time() - t0, {"orders_log": dict(data33.ORDER_LOG)}


def build_raws(days: list[date], folder: Path, cutoff_ns: int | None, workers: int,
               log: dict) -> None:
    todo = [d for d in days if not (folder / f"{d}.npz").is_file()]
    if not todo:
        return
    if available_mb() < MIN_AVAILABLE_MB:
        raise SystemExit("free -m: available memory below 2.5 GB; stopped")
    with ProcessPoolExecutor(max_workers=min(workers, MAX_WORKERS),
                             initializer=_worker_init) as pool:
        futs = [pool.submit(raw_job, d.isoformat(), str(folder / f"{d}.npz"), cutoff_ns)
                for d in todo]
        for fut in as_completed(futs):
            day, secs, info = fut.result()
            log["raw_seconds"][day] = round(secs, 2)
            if info["orders_log"]:
                log["order_log"][day] = info["orders_log"]
            if available_mb() < MIN_AVAILABLE_MB:
                pool.shutdown(cancel_futures=True)
                raise SystemExit("free -m: available memory below 2.5 GB; stopped")


# ------------------------------------------------------------------ features ----
def write_features(d: date, raw: dict, hist: list[dict], folder: Path) -> dict:
    x, day_stats = featB.features(d, raw, hist)
    stats = {"date": d.isoformat(), **day_stats,
             "front_zm": int(raw["fronts"][0]), "front_zs": int(raw["fronts"][1]),
             "front_zl": int(raw["fronts"][2]), "n_hist": len(hist)}
    (folder / "_day").mkdir(parents=True, exist_ok=True)
    (folder / "_day" / f"{d}.json").write_text(json.dumps(stats, indent=1) + "\n")
    if d in set(calB.oof_dates()):
        import pyarrow as pa
        import pyarrow.parquet as pq

        cols = {"date": pa.array([d.isoformat()] * featB.N_ROWS, pa.string()),
                "i": pa.array(np.arange(featB.N_ROWS, dtype=np.int16)),
                "t_ns": pa.array(calB.grid_ns(d, featB.N_ROWS))}
        for k, name in enumerate(featB.NAMES):
            cols[name] = pa.array(x[:, k].astype(np.float64))
        tmp = folder / f".{d}.parquet.tmp"
        pq.write_table(pa.table(cols), tmp)
        tmp.replace(folder / f"{d}.parquet")
    return stats


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dates", required=True)
    ap.add_argument("--workers", type=int, default=MAX_WORKERS)
    ap.add_argument("--cutoff-ns", type=int, default=None)
    ap.add_argument("--out", type=Path, default=OUT_DEFAULT)
    args = ap.parse_args(argv)
    os.nice(10)
    sha, files = code_sha()
    targets = parse_dates(args.dates)
    for d in targets:
        guard33.check_date(d, "build_featB target")
    base = args.out if args.cutoff_ns is None else args.out / "lt1" / str(args.cutoff_ns)
    raw_dir = args.out / "dayraw" / sha
    feat_dir = base / "features" / sha
    raw_dir.mkdir(parents=True, exist_ok=True)
    feat_dir.mkdir(parents=True, exist_ok=True)
    log: dict = {"raw_seconds": {}, "order_log": {}, "started": datetime.now(UTC).isoformat()}
    print("P3.6 rule 3 counts:", calB.release_count_table())
    hist_days = sorted({h for d in targets for h in calB.previous_dates(d, N_HIST_RAW)})
    if args.cutoff_ns is None:
        build_raws(sorted(set(hist_days) | set(targets)), raw_dir, None, args.workers, log)
        target_dir = raw_dir
    else:
        late = [h for h in hist_days if data33.window(h)[1] > args.cutoff_ns]
        if late:
            raise SystemExit(f"history dates end after the cutoff: {late[:3]}; use targets only "
                             "on or after them")
        build_raws(hist_days, raw_dir, None, args.workers, log)
        target_dir = base / "dayraw" / sha  # keyed by code, like the production raws
        target_dir.mkdir(parents=True, exist_ok=True)
        build_raws(targets, target_dir, args.cutoff_ns, args.workers, log)
    t0 = time.time()
    written = []
    for d in targets:
        raw = load_raw(target_dir / f"{d}.npz")
        hist = [load_raw(raw_dir / f"{h}.npz") for h in calB.previous_dates(d, N_HIST_RAW)]
        written.append(write_features(d, raw, hist, feat_dir))
    log["feature_seconds"] = round(time.time() - t0, 2)
    log["finished"] = datetime.now(UTC).isoformat()
    manifest = {"code_sha12": sha, "code_files": files, "cutoff_ns": args.cutoff_ns,
                "targets": [d.isoformat() for d in targets], "columns": featB.NAMES,
                "n_raw_built": len(log["raw_seconds"]), "log": log}
    mpath = feat_dir / "manifest.json"
    if mpath.is_file():
        old = json.loads(mpath.read_text())
        manifest["targets"] = sorted(set(old.get("targets", [])) | set(manifest["targets"]))
    mpath.write_text(json.dumps(manifest, indent=1) + "\n")
    secs = list(log["raw_seconds"].values())
    print(f"code {sha}: {len(written)} targets, {len(secs)} day raws built "
          f"(median {np.median(secs) if secs else 0:.1f} s), features {log['feature_seconds']} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
