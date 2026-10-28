"""Stage E.33 search runner (SearchCoder): run P7.1 configurations through search33 (P5, P6, P10).

Process pool under a thread cap of 8 (P5, CLAUDE.md): LOGIT fits one thread each (up to --max-procs
processes), LGBM fits --lgbm-threads (4 -> 2 at a time, 8 -> 1 at a time). Tasks are (config, fold) and
are submitted strictly in the given order. DONE markers per (config, fold) and per config; a restart
skips finished pieces; a fold started twice without finishing fails its configuration (P5, P10).

  uv run python reports/stage_e33_briefs/work/pipeline/run_search33.py --root DIR --ids E33-S5F15L001A ...
  ... --all                       the 300 E33 ids in P5 run order
  ... --probe E33-S5F15L100E ...  time fold 6 alone (writes timing only, under <root>/probes/search/)
"""
from __future__ import annotations

import os

for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_var] = "1"  # INTERFACE 2.4; LightGBM sets its own num_threads per fit

import argparse  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import logging  # noqa: E402
import multiprocessing as mp  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import traceback  # noqa: E402
from collections import deque  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
from multiprocessing.connection import wait as mp_wait  # noqa: E402
from datetime import datetime  # noqa: E402
from pathlib import Path  # noqa: E402
from zoneinfo import ZoneInfo  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import search33 as s  # noqa: E402

REAL_ROOT = s.DERIVED_E33
THREAD_CAP = 8
MIN_AVAILABLE_MB = 2048
PT = ZoneInfo("America/Vancouver")
log = logging.getLogger("run_search33")


def mem_available_mb() -> int:
    with open("/proc/meminfo") as fh:
        for line in fh:
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) // 1024
    raise RuntimeError("MemAvailable not found")


def in_collector_window(now: datetime | None = None) -> bool:
    """CLAUDE.md: no heavy run 15:30-16:00 PT on weekdays (news-collect.timer)."""
    now = now or datetime.now(PT)
    return now.weekday() < 5 and (15, 30) <= (now.hour, now.minute) < (16, 0)


def versions() -> dict:
    import pandas
    import pyarrow
    import scipy
    out = dict(s.library_versions(), pandas=pandas.__version__, pyarrow=pyarrow.__version__,
               scipy=scipy.__version__)
    lock = s.REPO / "uv.lock"
    out["uv_lock_sha256"] = hashlib.sha256(lock.read_bytes()).hexdigest() if lock.exists() else None
    return out


def check_root(root: Path, ids: list, args) -> None:
    """Real outcomes are read only after the P7.1 registration (INTERFACE 2.1)."""
    if not (REAL_ROOT.exists() and root.resolve() == REAL_ROOT.resolve()):
        return
    if not args.registered:  # READING S10: the real root needs --registered and a registry check
        raise SystemExit("refused: the real DERIVED root needs --registered (P7.1 registration first)")
    if args.expected_n != s.N_OOF:
        raise SystemExit("refused: the real root runs with --expected-n 796 only")
    from screening import trial_registry
    for prefix in sorted({s.parse_config_id(c).prefix for c in ids}):
        group = [c for c in ids if s.parse_config_id(c).prefix == prefix]
        trial_registry.require_registered(group, test=prefix)
    log.info("registration checked for %d ids", len(ids))


def setup_logging(root: Path, tag: str) -> Path:
    logdir = root / "search" / "_logs"
    logdir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(PT).strftime("%Y%m%d_%H%M%S")
    path = logdir / f"{tag}_{stamp}_{os.getpid()}.log"
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    for handler in (logging.FileHandler(path), logging.StreamHandler(sys.stderr)):
        handler.setFormatter(fmt)
        log.addHandler(handler)
    log.setLevel(logging.INFO)
    return path


def threads_for(cid: str, lgbm_threads: int) -> int:
    return 1 if s.parse_config_id(cid).family == "LOGIT" else lgbm_threads


def config_done(root: Path, cid: str) -> bool:
    return (s.config_dir(root, cid) / "DONE").exists()


def folds_settled(root: Path, cid: str) -> bool:
    states = [s.fold_state(root, cid, k) for k in range(1, s.N_FOLDS + 1)]
    return all(st == "done" for st in states) or any(st == "failed" for st in states)


def mark_twice_interrupted(root: Path, cid: str, k: int) -> None:
    paths = s.fold_paths(root, cid, k)
    paths["npz"].parent.mkdir(parents=True, exist_ok=True)
    s.atomic_write_json(paths["failed"], {"config": cid, "fold": k, "time": s.now_local(),
                                          "pipeline_sha": s.PIPELINE_SHA,
                                          "error": "interrupted twice (P5 failed fits: a second "
                                                   "interruption of the same fold fails the configuration)"})


def plan(root: Path, ids: list, lgbm_threads: int) -> deque:
    stale = []
    for cid in ids:  # SF1: refuse the whole run before anything starts if any marker is stale
        try:
            s.check_markers(root, cid)
        except s.StaleMarkerError as exc:
            stale.append(str(exc))
    if stale:
        raise s.StaleMarkerError(f"{len(stale)} configurations hold markers of another pipeline version:\n"
                                 + "\n".join(stale[:20]))
    tasks: deque = deque()
    for cid in ids:
        if config_done(root, cid):
            continue
        for k in range(1, s.N_FOLDS + 1):
            if s.fold_state(root, cid, k) != "pending":
                continue
            if s.read_attempts(root, cid, k) >= 2:
                log.warning("%s fold %d: started twice without finishing -> failed", cid, k)
                mark_twice_interrupted(root, cid, k)
                continue
            tasks.append((cid, k, threads_for(cid, lgbm_threads)))
    return tasks


def finalize(root: Path, cid: str, args) -> None:
    t0 = time.perf_counter()
    stats = s.finalize_config(root, cid, feat_sha=args.feat_sha, label_sha=args.label_sha,
                              expected_n=args.expected_n)
    status = "failed" if stats.get("failed") else "ok"
    (log.warning if stats.get("failed") else log.info)("%s finalized (%s) in %.1f s", cid, status,
                                                        time.perf_counter() - t0)


def wait_for_window(busy: bool) -> bool:
    """True if submission must wait (collector window); sleeps only when nothing is running."""
    if not in_collector_window():
        return False
    if not busy:
        log.info("collector window 15:30-16:00 PT: pausing submissions")
        while in_collector_window():
            time.sleep(20)
        log.info("collector window over: resuming")
        return False
    return True


def worker_main(conn) -> None:
    """A long-lived worker process: runs the fold tasks the parent sends, one at a time. A worker that
    dies (killed, out of memory) takes only its own fold with it (SF3)."""
    while True:
        task = conn.recv()
        if task is None:
            return
        fn, fargs, fkwargs = task
        try:
            conn.send(("ok", fn(*fargs, **fkwargs)))
        except BaseException as exc:  # noqa: BLE001  reported to the parent, which stops the run
            conn.send(("error", type(exc).__name__, repr(exc), traceback.format_exc()))


class Slot:
    """One worker process with its pipe and the fold it is running."""

    def __init__(self, ctx):
        self.conn, child = ctx.Pipe()
        self.proc = ctx.Process(target=worker_main, args=(child,), daemon=True)
        self.proc.start()
        child.close()
        self.task = None

    def close(self) -> None:
        if self.proc.is_alive():
            try:
                self.conn.send(None)
            except OSError:
                pass
            self.proc.join(timeout=30)
        if self.proc.is_alive():
            self.proc.terminate()
            self.proc.join(timeout=10)


def _receive(slot: Slot):
    """The slot's message, or None when its worker died."""
    try:
        if slot.conn.poll():
            return slot.conn.recv()
    except (EOFError, OSError):
        return None
    return None if not slot.proc.is_alive() else "pending"


def run_search(root: Path, ids: list, args, fold_fn=None) -> int:
    fold_fn = fold_fn or s.run_fold
    tasks = plan(root, ids, args.lgbm_threads)
    for cid in ids:  # resume: configurations whose folds settled before a crash
        if not config_done(root, cid) and folds_settled(root, cid):
            finalize(root, cid, args)
    log.info("%d fold tasks to run (%d configs)", len(tasks), len({t[0] for t in tasks}))
    used, stop, rc = 0, False, 0
    ctx = mp.get_context("spawn")
    slots = [Slot(ctx) for _ in range(args.max_procs)]
    try:
        while True:
            while tasks and not stop:
                cid, k, thr = tasks[0]
                idle = next((sl for sl in slots if sl.task is None and sl.proc.is_alive()), None)
                if used + thr > THREAD_CAP or idle is None:
                    break
                if any(s.fold_state(root, cid, j) == "failed" for j in range(1, s.N_FOLDS + 1)):
                    tasks.popleft()  # a failed sibling fold already fails the configuration
                    continue
                if not args.no_window_pause and wait_for_window(any(sl.task for sl in slots)):
                    break
                avail = mem_available_mb()
                if avail < MIN_AVAILABLE_MB:
                    log.error("available memory %d MB < %d MB: stopping submissions", avail, MIN_AVAILABLE_MB)
                    stop, rc = True, 3
                    break
                idle.conn.send((fold_fn, (str(root), cid, k), {"feat_sha": args.feat_sha, "label_sha": args.label_sha,
                                                               "threads": thr, "expected_n": args.expected_n}))
                idle.task = (cid, k, thr)
                used += thr
                tasks.popleft()
                log.info("start %s fold %d (%d thr; pid %d; %d MB available)", cid, k, thr, idle.proc.pid, avail)
            busy = [sl for sl in slots if sl.task is not None]
            if not busy or (stop and not busy):
                break
            mp_wait([sl.conn for sl in busy] + [sl.proc.sentinel for sl in busy], timeout=30)
            for sl in busy:
                msg = _receive(sl)
                if msg == "pending":
                    continue
                cid, k, thr = sl.task
                sl.task = None
                used -= thr
                if msg is None:
                    log.error("%s fold %d: worker pid %d died (exit code %s: killed or out of memory). Only "
                              "this fold is charged an interruption; the folds beside it finish. Counts toward "
                              "P10's two-failure stop if it was an OOM kill. Stopping.", cid, k, sl.proc.pid,
                              sl.proc.exitcode)
                    stop, rc = True, 4
                    continue
                if msg[0] == "error":
                    oom = msg[1] == "MemoryError"
                    log.error("%s fold %d raised %s (%s; the fold is an interruption, not a failed fit):\n%s",
                              cid, k, msg[2], "out of memory, counts toward P10" if oom else "stopping",
                              msg[3])
                    stop, rc = True, (4 if oom else 5)
                    continue
                res = msg[1]
                if res["status"] == "done":
                    log.info("%s fold %d done %.1f s", cid, k, res["seconds"])
                else:
                    log.warning("%s fold %d FAILED FIT: %s", cid, k, res.get("error"))
                if not config_done(root, cid) and folds_settled(root, cid) and \
                        not any(sl2.task and sl2.task[0] == cid for sl2 in slots):
                    finalize(root, cid, args)
    finally:
        for sl in slots:
            sl.close()
    left = [c for c in ids if not config_done(root, c)]
    failed = [c for c in ids if config_done(root, c) and
              json.loads((s.config_dir(root, c) / "DONE").read_text()).get("status") == "failed"]
    log.info("finished: %d/%d configs DONE (%d failed: %s); not done: %s", len(ids) - len(left), len(ids),
             len(failed), failed[:10], left[:10])
    return rc


def probe_worker(root: str, cid: str, k: int, feat_sha, label_sha, threads: int, expected_n) -> dict:
    """Fit fold k only and keep its timing (no probabilities, no mu_k, no losses are written)."""
    cfg = s.parse_config_id(cid)
    tables = s.load_tables(root, cfg.label, feat_sha, label_sha, expected_n)
    fold = s.make_folds(tables.dates, expected_n=expected_n)[k - 1]
    t0 = time.perf_counter()
    _, meta = s.fit_fold(cfg, tables, fold, threads)
    wall = time.perf_counter() - t0
    keep = ("seconds", "n_iter", "converged", "best_iteration", "rounds_run", "cal_converged", "threads",
            "n_train_rows", "n_train_dates", "n_inner_train_rows", "n_inner_val_rows", "warnings")
    out = {key: meta[key] for key in keep if key in meta}
    out.update({"config": cid, "fold": k, "wall_seconds_incl_mu": wall, "time": s.now_local(),
                "cpu_count": os.cpu_count()})
    path = Path(root) / "probes" / "search" / cid / f"fold{k}.timing.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    s.atomic_write_json(path, out)
    return out


def run_probe(root: Path, ids: list, args) -> int:
    ctx = mp.get_context("spawn")
    with ProcessPoolExecutor(max_workers=1, mp_context=ctx) as ex:
        for cid in ids:
            thr = threads_for(cid, args.lgbm_threads)
            out = ex.submit(probe_worker, str(root), cid, s.N_FOLDS, args.feat_sha, args.label_sha, thr,
                            args.expected_n).result()
            log.info("probe %s fold 6: %.1f s (%s thr, %d train rows)", cid, out["seconds"], thr,
                     out["n_train_rows"])
    return 0


def parse_args(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", required=True, type=Path, help="DERIVED tree or a proofs/seed<s> tree")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--ids", nargs="+")
    group.add_argument("--ids-file", type=Path, help="one P7.1 id per line")
    group.add_argument("--all", action="store_true", help="the 300 E33 ids in P5 run order")
    group.add_argument("--probe", nargs="+", metavar="CONFIG_ID", help="time fold 6 alone")
    ap.add_argument("--max-procs", type=int, default=8)
    ap.add_argument("--lgbm-threads", type=int, choices=(4, 8), default=4)
    ap.add_argument("--feat-sha", default=None)
    ap.add_argument("--label-sha", default=None)
    ap.add_argument("--registered", action="store_true", help="assert the P7.1 registration (real root)")
    ap.add_argument("--expected-n", type=int, default=s.N_OOF, help="OOF dates (796; 0 = unchecked, tests)")
    ap.add_argument("--no-window-pause", action="store_true")
    args = ap.parse_args(argv)
    if not 1 <= args.max_procs <= THREAD_CAP:
        ap.error("--max-procs must be 1..8")
    args.expected_n = None if args.expected_n == 0 else args.expected_n
    return args


def main(argv=None) -> int:
    args = parse_args(argv)
    root = args.root
    if args.all:
        ids = s.all_config_ids()
    elif args.ids_file:
        ids = [ln.strip() for ln in args.ids_file.read_text().splitlines() if ln.strip()]
    else:
        ids = list(args.probe or args.ids)
    for cid in ids:
        s.parse_config_id(cid)
    if len(set(ids)) != len(ids):
        raise SystemExit("duplicate ids")
    logpath = setup_logging(root, "probe" if args.probe else "run")
    check_root(root, ids, args)
    cur = os.nice(0)
    if cur < 10:
        os.nice(10 - cur)
    manifest = {"argv": sys.argv, "root": str(root), "ids": ids, "seed": s.SEED, "versions": versions(),
                "env": {v: os.environ.get(v) for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                                                       "MKL_NUM_THREADS")},
                "nice": os.nice(0), "max_procs": args.max_procs, "lgbm_threads": args.lgbm_threads,
                "expected_n": args.expected_n, "start": s.now_local(), "pid": os.getpid()}
    log.info("manifest %s", json.dumps(manifest, sort_keys=True))
    try:
        rc = run_probe(root, ids, args) if args.probe else run_search(root, ids, args)
    except s.StaleMarkerError as exc:  # SF1
        log.error("REFUSED: %s", exc)
        rc = 6
    manifest.update({"end": s.now_local(), "rc": rc})
    s.atomic_write_json(logpath.with_suffix(".json"), manifest)
    return rc


if __name__ == "__main__":
    sys.exit(main())
