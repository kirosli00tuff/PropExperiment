"""E.32b economics driver (spec section 4 E): econ32b.json from F3_vol.json + F4_facts_unmasked.json, and the
regression against E.28's A3_econ.json. Resumable: one part file per (pair, curve) under parts/<tag>/.

Usage (from the repo root; heavy runs through the shared lock, nice 10):
  R=reports/stage_e32b_briefs; W=$R/work/econ
  flock $R/work/heavy.lock env PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 nice -n 10 uv run python $W/econ32b.py \
      run --f3 $R/F3_vol.json --f4 $R/F4_facts_unmasked.json --edir-pairs <top15.json> --workers 6 \
      > $W/run_real.log 2>&1
  ... econ32b.py regress --workers 6      (E.28 inputs, S = 1 -> REGRESSION.md, regression.json)
  ... econ32b.py collect --tag real ...   (rebuild the output from the parts only)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
import os
import resource
import sys
import threading
import time
from pathlib import Path
from typing import Any

WORK = Path(__file__).resolve().parent
REPO = WORK.parents[3]
sys.path.insert(0, str(WORK))

import econ32b_core as C  # noqa: E402
import econ32b_inputs as I  # noqa: E402

SPEC = REPO / "reports" / "stage_e32b_ranking_spec.md"
SPEC_SHA256 = "09ebe6970fcf027009152fa81a414360a015d535b095138cdf65cf1a4eb58635"
BRIEFS = REPO / "reports" / "stage_e32b_briefs"
DEFAULT_OUT = BRIEFS / "econ32b.json"
E28_INPUTS = WORK / "A3_inputs.json"
E28_ECON = REPO / "reports" / "stage_e28_briefs" / "A3_econ.json"
RULES = REPO / "reports" / "stage_e19_rules.json"
CODE_FILES = ("A3_funnel.py", "A3_models.py", "A3_run.py", "econ32b_core.py", "econ32b_model.py")
MAX_WORKERS = min(8, max(1, (os.cpu_count() or 2) // 2))
_STATE: dict[str, Any] = {}


def now() -> str:
    os.environ["TZ"] = "America/Vancouver"
    time.tzset()
    return time.strftime("%Y-%m-%d %H:%M:%S %Z")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_spec() -> None:
    got = sha256(SPEC)
    if got != SPEC_SHA256:
        raise SystemExit(f"refused: spec sha256 {got} != frozen {SPEC_SHA256}")


def code_fingerprint() -> str:
    h = hashlib.sha256()
    for name in CODE_FILES:
        h.update((WORK / name).read_bytes())
    h.update(RULES.read_bytes())
    return h.hexdigest()[:16]


def job_hash(job: dict[str, Any], fp: str) -> str:
    return hashlib.sha256((fp + json.dumps(job, sort_keys=True)).encode()).hexdigest()[:16]


def part_path(tag: str, job: dict[str, Any]) -> Path:
    return WORK / "parts" / tag / f"{job['firm']}__{job['code']}__{job['curve']}.json"


def _done(tag: str, job: dict[str, Any], jh: str) -> bool:
    p = part_path(tag, job)
    try:
        return p.exists() and json.loads(p.read_text()).get("job_hash") == jh
    except (OSError, json.JSONDecodeError):
        return False


# ------------------------------------------------------------------------------------------- workers ----
def run_job(job: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    import econ32b_model as M

    t0 = time.time()
    curve = C.Curve(M.make_evaluator(state, job["firm"], job["T"], job["sigma_T"], job["v_usd"]))
    cases = {}
    for cs in job["cases"]:
        case = C.CostCase(cs["name"], cs["f_rt_usd"], cs["v_usd"], cs["s_rt_ticks"])
        rec = C.evaluate_case(curve, case, job["k_max"], job["sigma60"])
        cases[cs["name"]] = {"curve": job["curve"], "h": job["h"], "T": job["T"], "sigma_T": job["sigma_T"], **rec}
    evals = [{"d": r["d"], "ev": r["ev"], "se": r["se"], "p10k": r["p10k"]}
             for r in sorted(curve.cache.values(), key=lambda r: r["d"])]
    return {"job": job, "cases": cases, "n_evaluations": curve.n_evals, "evaluations": evals,
            "runtime_s": round(time.time() - t0, 2),
            "maxrss_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024}


def ensure_nice(level: int = 10) -> None:
    """Niceness at least `level` (an outer `nice -n 10` is not doubled)."""
    cur = os.nice(0)
    if cur < level:
        os.nice(level - cur)


def _init_worker() -> None:
    ensure_nice()


def _task(args: tuple[str, dict[str, Any], str]) -> tuple[str, float, int, str]:
    tag, job, jh = args
    rec = {"job_hash": jh, **run_job(job, _STATE)}
    out = part_path(tag, job)
    tmp = out.with_suffix(".tmp")
    tmp.write_text(json.dumps(rec, indent=1))
    os.replace(tmp, out)
    msg = " ".join(f"{n}: mu*={c['mu_star_mkt']} mu10K={c['mu10K_mkt']}" for n, c in rec["cases"].items())
    return f"{job['pair']} {job['curve']}", rec["runtime_s"], rec["n_evaluations"], msg


class MemSampler(threading.Thread):
    """Peak PSS of this process and its children (the pool), and the lowest MemAvailable, every 2 s."""

    def __init__(self) -> None:
        super().__init__(daemon=True)
        self.peak_pss_mb = 0.0
        self.min_avail_mb = float("inf")
        self.stop = threading.Event()

    @staticmethod
    def _pss_kb(pid: int) -> int:
        try:
            for line in Path(f"/proc/{pid}/smaps_rollup").read_text().splitlines():
                if line.startswith("Pss:"):
                    return int(line.split()[1])
        except OSError:
            return 0
        return 0

    def sample(self) -> None:
        pid = os.getpid()
        try:
            kids = Path(f"/proc/{pid}/task/{pid}/children").read_text().split()
        except OSError:
            kids = []
        total = self._pss_kb(pid) + sum(self._pss_kb(int(k)) for k in kids)
        self.peak_pss_mb = max(self.peak_pss_mb, total / 1024)
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemAvailable:"):
                self.min_avail_mb = min(self.min_avail_mb, int(line.split()[1]) / 1024)

    def run(self) -> None:
        while not self.stop.wait(2.0):
            self.sample()


def execute(tag: str, jobs: list[dict[str, Any]], workers: int) -> dict[str, Any]:
    """Run every job not already on disk (same job hash); returns run statistics."""
    import econ32b_model as M

    (WORK / "parts" / tag).mkdir(parents=True, exist_ok=True)
    fp = code_fingerprint()
    todo = [(tag, j, job_hash(j, fp)) for j in jobs]
    todo = [t for t in todo if not _done(tag, t[1], t[2])]
    todo.sort(key=lambda t: (t[1]["sigma_T"] * t[1]["v_usd"] * t[1]["T"] ** 0.5, -t[1]["k_max"]))
    workers = max(1, min(workers, MAX_WORKERS, len(todo) or 1))
    print(f"{now()} fingerprint {fp}: {len(jobs)} jobs, {len(todo)} to run on {workers} workers", flush=True)
    stats = {"fingerprint": fp, "jobs": len(jobs), "ran": len(todo), "workers": workers}
    if not todo:
        return stats
    mem = MemSampler()
    t0 = time.time()
    _STATE.update(M.build_state(sorted({t[1]["firm"] for t in todo})))
    with mp.get_context("fork").Pool(workers, initializer=_init_worker) as pool:
        mem.start()  # after the fork: no thread exists while the workers are forked
        for name, sec, n, msg in pool.imap_unordered(_task, todo):
            print(f"{now()} {name} {sec:.0f}s {n} evals | {msg}", flush=True)
            mem.sample()
    mem.stop.set()
    stats.update(wall_s=round(time.time() - t0, 1), peak_pss_mb=round(mem.peak_pss_mb),
                 min_mem_available_mb=round(mem.min_avail_mb))
    print(f"{now()} done: wall {stats['wall_s']} s, peak PSS {stats['peak_pss_mb']} MB, "
          f"min MemAvailable {stats['min_mem_available_mb']} MB", flush=True)
    return stats


# ------------------------------------------------------------------------------------------- collect ----
def load_parts(tag: str, jobs: list[dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], list[str]]:
    fp = code_fingerprint()
    got, missing = {}, []
    for j in jobs:
        jh = job_hash(j, fp)
        if not _done(tag, j, jh):
            missing.append(f"{j['pair']} {j['curve']}")
            continue
        got[f"{j['pair']}|{j['curve']}"] = json.loads(part_path(tag, j).read_text())
    return got, missing


def _block(rec: dict[str, Any]) -> dict[str, Any]:
    out = {k: v for k, v in rec.items() if k != "search"}
    out["search"] = {name: {"k_bisection": s["k_bisection"], "f_at_k": s["f_at_k"],
                            "f_at_k_minus_1": s["f_at_k_minus_1"],
                            **{k: s["confirmation"].get(k) for k in ("confirmed", "violations", "n_checked",
                                                                      "max_below")}}
                     for name, s in rec["search"].items()}
    return out


def build_doc(parts: dict[str, dict[str, Any]], meta: dict[str, dict[str, Any]], skipped: dict[str, str],
              extra: dict[str, Any]) -> dict[str, Any]:
    import econ32b_model as M

    pairs: dict[str, dict[str, Any]] = {k: {"inputs": m} for k, m in meta.items()}
    for rec in parts.values():
        key = rec["job"]["pair"]
        for name, case in rec["cases"].items():
            b = _block(case)
            if name.startswith("E_dir") and name != "E_dir60":
                pairs[key].setdefault("E_dir", {})[name[len("E_dir"):]] = b
            else:
                pairs[key][name] = b
    for p in pairs.values():
        p.setdefault("E_dir60", None)
    return {"spec_sha256": SPEC_SHA256, "generated_pdt": now(), "fingerprint": code_fingerprint(), **extra,
            "grid": {"step_ticks": C.STEP, "cap_rule": "max(4, ceil(0.30 sigma_60)) ticks, every curve of a pair",
                     "search": "bisection on k, then E.28's grid confirmation",
                     "confirmation": {"subgrid_ticks": C.COARSE * C.STEP, "dense_below_ticks": C.DENSE_BELOW * C.STEP,
                                      "near_ev": f"EV >= -max({C.NEAR_SE} SE, USD {C.NEAR_USD})",
                                      "near_p10k": f"P10K >= {C.NEAR_P}"}},
            "model": {**M.MODEL_CONSTANTS, "source": "E.28 A3_funnel.py / A3_models.py (copied unchanged)",
                      "daily_pnl": "normal, mean T (mu - c) v, sd sqrt(T) sigma_T v",
                      "c_mkt": "F_rt / v + S_rt", "cost_per_attempt": "E.28: evaluation fees per attempt at "
                      "mu = 0, limit case (d = -F_rt / v); cost_per_attempt_mkt_mu0 = the same at d = -c_mkt"},
            "pairs": pairs, "not_computed": skipped}


def write_json(path: Path, doc: dict[str, Any]) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc, indent=1))
    os.replace(tmp, path)


# ------------------------------------------------------------------------------------------ commands ----
def _facts_jobs(a: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, str], dict]:
    import econ32b_model as M

    f3, f4 = json.loads(Path(a.f3).read_text()), json.loads(Path(a.f4).read_text())
    for name, doc in (("F3", f3), ("F4", f4)):
        if doc.get("spec_sha256") not in (None, SPEC_SHA256):
            raise SystemExit(f"refused: {name} spec_sha256 {doc.get('spec_sha256')} != {SPEC_SHA256}")
    limits = M.model_limits()
    edir = None
    if a.edir_pairs:
        raw = json.loads(Path(a.edir_pairs).read_text())
        edir = raw["pairs"] if isinstance(raw, dict) else raw
    only = a.only.split(",") if a.only else None
    jobs, meta, skipped = I.jobs_from_facts(f3, f4, set(limits), edir, only)
    fc = I.firm_check(f4, limits)
    inputs = {"F3": {"path": a.f3, "sha256": sha256(Path(a.f3))}, "F4": {"path": a.f4, "sha256": sha256(Path(a.f4))},
              "edir_pairs": None if not a.edir_pairs else {"path": a.edir_pairs, "sha256": sha256(Path(a.edir_pairs)),
                                                           "pairs": edir}}
    return jobs, meta, skipped, {"inputs": inputs, "firm_check": fc}


def cmd_run(a: argparse.Namespace, collect_only: bool = False) -> int:
    check_spec()
    jobs, meta, skipped, extra = _facts_jobs(a)
    fc = extra["firm_check"]
    print(f"{now()} {len(meta)} pairs, {len(jobs)} jobs, {len(skipped)} not computed; firm check mismatches: "
          f"{fc['mismatches'] or 'none'}", flush=True)
    if fc["mismatches"] and not a.allow_firm_mismatch:
        print("refused: F4 firm limits differ from E.28's firm models (lead decision; rerun with "
              "--allow-firm-mismatch to keep E.28's models)", flush=True)
        return 3
    if a.chunk and not collect_only:  # "i/n": every n-th job from i, under its own lock; then `collect`
        i, n = (int(x) for x in a.chunk.split("/"))
        stats = execute(a.tag, jobs[i::n], a.workers)
        print(f"{now()} chunk {a.chunk} done: {json.dumps(stats)}", flush=True)
        return 0
    stats = {} if collect_only else execute(a.tag, jobs, a.workers)
    parts, missing = load_parts(a.tag, jobs)
    if missing:
        print(f"{now()} {len(missing)} jobs missing: {missing[:8]}", flush=True)
        return 1
    out = Path(a.out) if a.out else DEFAULT_OUT
    write_json(out, build_doc(parts, meta, skipped, {**extra, "run": stats, "tag": a.tag}))
    print(f"{now()} wrote {out}", flush=True)
    return 0


def chunk_stats(log: Path) -> dict[str, Any]:
    """The 'chunk i/n done: {...}' records of a chunked run's log (for a --collect-only report)."""
    if not log.exists():
        return {}
    marker = " done: "
    rows = [json.loads(line.split(marker, 1)[1]) for line in log.read_text().splitlines()
            if " chunk " in line and marker in line]
    return {"chunks": rows, "wall_s_total": round(sum(r.get("wall_s", 0.0) for r in rows), 1),
            "peak_pss_mb_max": max((r.get("peak_pss_mb", 0) for r in rows), default=0)}


def cmd_regress(a: argparse.Namespace) -> int:
    import econ32b_regress as RG

    check_spec()
    jobs, skipped = I.jobs_from_e28(json.loads(E28_INPUTS.read_text()))
    if a.only:
        jobs = [j for j in jobs if j["pair"] in a.only.split(",")]
    if a.chunk:  # "i/n": every n-th job from i (run chunk by chunk, each under its own lock; then --collect-only)
        i, n = (int(x) for x in a.chunk.split("/"))
        stats = execute("regress", jobs[i::n], a.workers)
        print(f"{now()} chunk {a.chunk} done: {json.dumps(stats)}", flush=True)
        return 0
    stats = chunk_stats(WORK / "regress_run.log") if a.collect_only else execute("regress", jobs, a.workers)
    parts, missing = load_parts("regress", jobs)
    if missing:
        print(f"{now()} {len(missing)} jobs missing: {missing[:8]}", flush=True)
        return 1
    return RG.write_regression(parts, skipped, stats, json.loads(E28_ECON.read_text()), WORK, now())


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("run", "collect", "regress"))
    ap.add_argument("--f3", default=str(BRIEFS / "F3_vol.json"))
    ap.add_argument("--f4", default=str(BRIEFS / "F4_facts_unmasked.json"))
    ap.add_argument("--edir-pairs", help='JSON list of "firm|CODE" (or {"pairs": [...]}) for E_dir at 30/120/240')
    ap.add_argument("--only", help='comma-separated "firm|CODE" keys')
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--tag", default="real", help="parts/<tag>/ folder")
    ap.add_argument("--out", help=f"output JSON (default {DEFAULT_OUT.relative_to(REPO)})")
    ap.add_argument("--allow-firm-mismatch", action="store_true")
    ap.add_argument("--collect-only", action="store_true", help="regress: rebuild REGRESSION.md from the parts")
    ap.add_argument("--chunk", help='run, regress: "i/n" runs jobs i, i+n, ... only (no output file)')
    a = ap.parse_args(argv)
    ensure_nice()
    if a.cmd == "regress":
        return cmd_regress(a)
    return cmd_run(a, collect_only=a.cmd == "collect")


if __name__ == "__main__":
    sys.exit(main())
