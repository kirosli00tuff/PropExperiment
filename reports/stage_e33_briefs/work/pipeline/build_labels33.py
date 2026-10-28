"""E.33 pipeline A label builder (Coder-A): writes the INTERFACE.md 4.2 tables.

Output: <out-root>/<code_sha12>/<LABEL>/<YYYY-MM-DD>.parquet, <LABEL>/_excl/<YYYY-MM-DD>.json and
<LABEL>/_done/<YYYY-MM-DD>.DONE per (label, OOF date), plus <out-root>/<code_sha12>/manifest.json (the code files
and their sha256s; <code_sha12> = the first 12 hex of the sha256 of their concatenation in CODE_FILES order).
Default out-root: DERIVED/labels. Resumable per (label, date): a (label, date) with a DONE marker whose code and
sigma source match is skipped. At most 3 processes, nice 10, free memory checked first (stop below 2 GB).

Every real-data read goes through data33 / cal33 (guard33). The builder prints COUNTS only (rows, exclusions,
timings): INTERFACE rule 1, no statistic of label values, nets or classes is computed, printed or saved.

Usage (from the repo root):
  uv run python reports/stage_e33_briefs/work/pipeline/build_labels33.py --features-sha <sha12> [--dates all]
      [--labels F05,F15,F30,F60,T15,T30] [--procs 3]
  probe (timing and schema on <= 3 dates; writes under DERIVED/probes/):
  uv run python .../build_labels33.py --probe --dates 2021-07-01,2022-03-14 --sigma-override 3.15
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import cal33  # noqa: E402
import data33  # noqa: E402
import guard33 as g  # noqa: E402  (also puts REPO and the E.31 pilot folder on sys.path)
import lab33 as lb  # noqa: E402

PILOT = g.PILOT
CODE_FILES = (
    HERE / "lab33.py",
    HERE / "build_labels33.py",
    HERE / "cal33.py",
    HERE / "data33.py",
    HERE / "guard33.py",
    PILOT / "mbo_book31.py",
)
DERIVED = g.DERIVED
LABEL_ROOT = DERIVED / "labels"
PROBE_ROOT = DERIVED / "probes" / "lab33_probe"
FEATURE_ROOT = DERIVED / "features"
PROTOCOL_SHA256 = "c4ffb9d79af4bbbf10574ac138668aa49a80b22a8f5fba5879184d357d2c7e05"
MAX_PROCS = 3
MIN_FREE_MB = 2048


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def code_identity() -> tuple[str, dict[str, str]]:
    """(code_sha12, {file: sha256}); sha12 over the concatenated file bytes in CODE_FILES order."""
    h = hashlib.sha256()
    shas = {}
    for p in CODE_FILES:
        data = p.read_bytes()
        h.update(data)
        shas[str(p.relative_to(g.REPO))] = hashlib.sha256(data).hexdigest()
    return h.hexdigest()[:12], shas


def available_mb() -> int:
    with open("/proc/meminfo") as fh:
        for line in fh:
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) // 1024
    raise RuntimeError("MemAvailable not found in /proc/meminfo")


def sigma_from_features(day_dir: Path, d: str) -> float | None:
    """sigma_ZM(D) in ticks from DERIVED/features/<sha>/_day/<D>.json (INTERFACE 4.1); None if null."""
    path = g.check_path(day_dir / f"{d}.json")
    with open(path) as fh:
        val = json.load(fh).get("sigma_zm")
    return None if val is None else float(val)


def day_inputs(d: str, sigma: float | None) -> lb.DayInputs:
    excl, _ = cal33.excluded(d)
    return lb.DayInputs(
        date=d,
        t0_ns=cal33.ct_ns(d, "08:35:00"),
        close_ns=cal33.ct_ns(d, "13:13:00"),
        session_end_ns=cal33.ct_ns(d, "13:20:00"),
        releases=tuple(int(r) for r in cal33.releases(d)),
        limits=cal33.limits(d),
        tick=cal33.tick("ZM"),
        excluded=bool(excl),
        sigma_zm=sigma,
    )


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)


def write_outputs(folder: Path, d: str, cols: dict, excl: dict, marker: dict) -> None:
    import pandas as pd  # local: workers import it once each

    (folder / "_excl").mkdir(parents=True, exist_ok=True)
    (folder / "_done").mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame({k: cols[k] for k in lb.COLUMNS})
    tmp = folder / f"{d}.parquet.tmp"
    frame.to_parquet(tmp, index=False, engine="pyarrow")
    os.replace(tmp, folder / f"{d}.parquet")
    _atomic_write_bytes(
        folder / "_excl" / f"{d}.json", json.dumps(excl, indent=1, sort_keys=True).encode()
    )
    _atomic_write_bytes(folder / "_done" / f"{d}.DONE", json.dumps(marker, sort_keys=True).encode())


def is_done(folder: Path, d: str, expect: dict) -> bool:
    path = folder / "_done" / f"{d}.DONE"
    if not path.exists():
        return False
    got = json.loads(path.read_text())
    for k, v in expect.items():
        if got.get(k) != v:
            raise RuntimeError(
                f"{path}: DONE marker {k}={got.get(k)!r} differs from this run's {v!r}"
            )
    return True


def build_date(task: dict[str, Any]) -> dict[str, Any]:
    """Worker: one trade date, every requested label not yet DONE. Returns counts and seconds only."""
    started = time.perf_counter()
    d: str = task["date"]
    out = Path(task["out"])
    labels: list[str] = task["labels"]
    sigma: float | None = task["sigma"]
    day = day_inputs(d, sigma)
    hist = None
    t_replay = 0.0
    book_missing = False
    # records strictly before 13:20:00 CT (P3.2 exit fallback bound)
    cutoff = day.session_end_ns - 1
    try:
        # the book is replayed on excluded dates too: only for mid_move (READING MIDMOVE-EXCL)
        recs = data33.load_zm(d, cutoff_ns=cutoff)
    except (g.GuardRefused, FileNotFoundError):
        if not day.excluded:
            raise
        recs = None
        book_missing = True  # excluded date without E.31 Z1 records: mid_move stays NaN (reported)
    order_log = dict(data33.ORDER_LOG)  # PipelineReview N11: re-sorts by data33, after the load
    if recs is not None:
        front = int(cal33.fronts(d)["ZM"])
        t0 = time.perf_counter()
        hist = lb.replay(recs, front, day.tick, end_ns=cutoff)
        t_replay = time.perf_counter() - t0
        del recs
    res: dict[str, Any] = {
        "date": d,
        "excluded": day.excluded,
        "labels": {},
        "replay_s": round(t_replay, 2),
        "book_stats": dict(hist.stats) if hist is not None else {},
        "book_missing": book_missing,
        "order_log": order_log,
    }
    for label in labels:
        t1 = time.perf_counter()
        cols, excl = lb.compute_label(hist, day, label)
        marker = {
            "code_sha12": task["code_sha12"],
            "label": label,
            "date": d,
            "sigma_source": task["sigma_source"] if lb.LABELS[label][0] == "TB" else None,
            "rows_kept": excl["rows_kept"],
            "seconds": round(time.perf_counter() - t1, 3),
            "order_log": order_log,
        }
        write_outputs(out / label, d, cols, excl, marker)
        res["labels"][label] = {
            "grid": excl["grid_minutes"],
            "entry_ok": excl["entry_ok_minutes"],
            "rows": excl["rows_kept"],
            "removed_first": excl["rows_removed_first_rule"],
            "seconds": marker["seconds"],
        }
    res["seconds"] = round(time.perf_counter() - started, 2)
    return res


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--dates", default="all", help="'all' (the 796 OOF dates) or a comma list of OOF dates"
    )
    ap.add_argument("--labels", default=",".join(lb.LABELS))
    ap.add_argument(
        "--features-sha", default=None, help="DERIVED/features/<sha> holding _day/<D>.json (TB)"
    )
    ap.add_argument("--procs", type=int, default=MAX_PROCS)
    ap.add_argument("--out-root", default=None)
    ap.add_argument(
        "--probe", action="store_true", help="timing/schema run on <= 3 dates under DERIVED/probes"
    )
    ap.add_argument(
        "--sigma-override",
        type=float,
        default=None,
        help="probe only: a placeholder sigma_ZM (ticks) for TB timing when no feature _day exists",
    )
    return ap.parse_args(argv)


def resolve_dates(spec: str) -> list[str]:
    oof = [x.isoformat() for x in cal33.oof_dates()]
    if spec == "all":
        return oof
    wanted = [x.strip() for x in spec.split(",") if x.strip()]
    bad = [x for x in wanted if x not in set(oof)]
    if bad:
        raise SystemExit(f"not OOF dates (P1.4): {bad}")
    return wanted


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    os.nice(10)
    free = available_mb()
    if free < MIN_FREE_MB:
        raise SystemExit(f"available memory {free} MB < {MIN_FREE_MB} MB: not started")
    labels = [x.strip() for x in args.labels.split(",") if x.strip()]
    unknown = [x for x in labels if x not in lb.LABELS]
    if unknown:
        raise SystemExit(f"unknown labels {unknown}")
    procs = max(1, min(args.procs, MAX_PROCS))
    dates = resolve_dates(args.dates)
    if args.probe and len(dates) > 3:
        raise SystemExit("a probe runs on at most 3 real dates (brief deliverable 3)")
    if args.sigma_override is not None and not args.probe:
        raise SystemExit("--sigma-override is for probes only")
    need_tb = any(lb.LABELS[x][0] == "TB" for x in labels)
    day_dir = None
    if need_tb and args.sigma_override is None:
        if not args.features_sha:
            raise SystemExit(
                "TB labels need --features-sha (sigma_ZM from DERIVED/features/<sha>/_day)"
            )
        day_dir = g.check_path(FEATURE_ROOT / args.features_sha / "_day")
    sigma_source = (
        f"override:{args.sigma_override!r}"
        if args.sigma_override is not None
        else (f"features/{args.features_sha}/_day" if day_dir is not None else None)
    )
    sha12, shas = code_identity()
    root = Path(args.out_root) if args.out_root else (PROBE_ROOT if args.probe else LABEL_ROOT)
    out = root / sha12
    out.mkdir(parents=True, exist_ok=True)
    manifest = {
        "code_sha12": sha12,
        "code_files": shas,
        "protocol_sha256": PROTOCOL_SHA256,
        "L_ns": lb.L_NS,
        "fee_ticks": lb.FEE_TICKS,
        "kappa": lb.KAPPA,
        "sigma_source": sigma_source,
        "columns": list(lb.COLUMNS),
        "labels": {k: list(v) for k, v in lb.LABELS.items()},
    }
    mpath = out / "manifest.json"
    if mpath.exists():
        old = json.loads(mpath.read_text())
        if old.get("code_files") != shas:
            raise SystemExit(f"{mpath}: code files differ from this run")
        if need_tb and old.get("sigma_source") not in (None, sigma_source):
            raise SystemExit(
                f"{mpath}: sigma source {old.get('sigma_source')} differs from {sigma_source}"
            )
        if old.get("sigma_source") is not None and sigma_source is None:
            manifest["sigma_source"] = old["sigma_source"]
    _atomic_write_bytes(mpath, json.dumps(manifest, indent=1, sort_keys=True).encode())
    tasks = []
    for d in dates:
        todo = []
        for label in labels:
            src = sigma_source if lb.LABELS[label][0] == "TB" else None
            if not is_done(out / label, d, {"code_sha12": sha12, "sigma_source": src}):
                todo.append(label)
        if not todo:
            continue
        sigma = None
        if any(lb.LABELS[x][0] == "TB" for x in todo):
            sigma = (
                args.sigma_override
                if args.sigma_override is not None
                else sigma_from_features(day_dir, d)
            )
        tasks.append(
            {
                "date": d,
                "labels": todo,
                "out": str(out),
                "sigma": sigma,
                "code_sha12": sha12,
                "sigma_source": sigma_source,
            }
        )
    print(
        f"labels {labels} code_sha12 {sha12} out {out} dates {len(dates)} to_do {len(tasks)} procs {procs} "
        f"free_mb {free}",
        flush=True,
    )
    results = []
    if procs == 1 or len(tasks) <= 1:
        for task in tasks:
            results.append(_report(build_date(task)))
    else:
        with ProcessPoolExecutor(max_workers=procs) as pool:
            for res in pool.map(build_date, tasks):
                results.append(_report(res))
    print(f"done {len(results)} dates", flush=True)
    return 0


def _report(res: dict[str, Any]) -> dict[str, Any]:
    """Counts only (rows, exclusions, timings)."""
    per = " ".join(
        f"{k}:grid={v['grid']},entry_ok={v['entry_ok']},rows={v['rows']}"
        for k, v in res["labels"].items()
    )
    print(
        f"{res['date']} excluded={res['excluded']} seconds={res['seconds']} replay_s={res['replay_s']} "
        f"updates={res['book_stats'].get('updates', 0)} book_missing={res['book_missing']} {per}",
        flush=True,
    )
    return res


if __name__ == "__main__":
    raise SystemExit(main())
