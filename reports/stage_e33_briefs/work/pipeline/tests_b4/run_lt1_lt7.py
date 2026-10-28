"""B4 driver for LT1 and LT7 on one Coder-A feature code (the newest; its code_sha12 must equal --expect-sha).

Steps (each resumable through the builders' DONE markers):
 1. production features of the 178 LT1 draw dates with build_features33.build under a separate root
    DERIVED/b4/lt_features/<sha>/ (pass 1 for the dates and their 21 history dates, pass 2 for the dates), so the
    production folders of the coders and the lead are not touched;
 2. LT1: every one of the 200 draws with prior=production (D re-streamed from all four inputs truncated at t), and
    the first --recompute-n draws in the seeded order of the draw file also with prior=recompute (all 22 dates
    re-streamed) in a separate folder;
 3. production labels of the 178 dates (lab33 as on disk; TB sigma from step 1's _day) under DERIVED/b4/lt_labels/;
 4. LT7: lt7_causality on the seed-1 null proof fold models (read only).
Outputs: reports/stage_e33_briefs/work/b4_runs/LT1_full_<sha>.json, LT1_recompute_<sha>.json, LT7_<sha>.json.
At most 3 processes; nice 10; counts only.

Usage: uv run python .../tests_b4/run_lt1_lt7.py --expect-sha <sha12> [--steps 1,2,3,4] [--recompute-n 20]
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import shutil
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
PIPE = HERE.parent
for _p in (str(HERE), str(PIPE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import build_features33 as bf  # noqa: E402
import cal33  # noqa: E402
import guard33 as g  # noqa: E402
import lt1_truncation as lt  # noqa: E402

ROOT_F = g.DERIVED / "b4" / "lt_features"
ROOT_FR = g.DERIVED / "b4" / "lt_features_recompute"
ROOT_L = g.DERIVED / "b4" / "lt_labels"
RUNS = PIPE.parent / "b4_runs"
REPO = PIPE.parents[3]


def _draw() -> list[dict]:
    return json.loads(lt.DRAW_PATH.read_text())["times"]


def step1(procs: int) -> Path:
    dates = sorted({date.fromisoformat(x["date"]) for x in _draw()})
    t0 = time.time()
    res = bf.build(dates, procs, ROOT_F)
    print(f"step1 features: {res['pass1_dates']} pass-1 dates, {res['pass2_dates']} pass-2 dates, "
          f"{time.time() - t0:.0f} s", flush=True)
    return Path(res["folder"])


def _lt1_one(args: tuple) -> dict:
    os.nice(10) if os.getpriority(os.PRIO_PROCESS, 0) < 10 else None
    fdir, x, prior = args
    return lt.check_one(Path(fdir), x, prior)


def step2(fdir: Path, sha: str, procs: int, recompute_n: int) -> None:
    draw = _draw()
    for prior, n, out_name in (("production", len(draw), f"LT1_full_{sha}.json"),
                               ("recompute", recompute_n, f"LT1_recompute_{sha}.json")):
        out = RUNS / out_name
        done = json.loads(out.read_text()) if out.exists() else {"prior": prior, "results": []}
        seen = {(r["date"], r["i"]) for r in done["results"]}
        # the recompute subset: the first n draws of the file in idx order (the draw file is sorted by date, so take
        # every k-th draw to spread the subset across the period)
        pick = draw if prior == "production" else draw[:: max(1, len(draw) // max(1, n))][:n]
        target = fdir
        if prior == "recompute":
            # a separate copy of the production folder's pass-2 tables is not needed: build_cutoff writes its own
            # rebuilt tables under <fdir>/_lt1/<t>/ and only compares with <fdir>/<D>.parquet
            target = fdir
        todo = [(str(target), x, prior) for x in pick if (x["date"], x["i"]) not in seen
                and (target / f"{x['date']}.parquet").exists()]
        if prior == "recompute":
            for _f, x, _p in todo:  # recompute folders must not reuse the production-prior rebuild of the same t
                shutil.rmtree(target / "_lt1" / str(x["t_ns"]), ignore_errors=True)
        t0 = time.time()
        with mp.get_context("fork").Pool(processes=procs) as pool:
            for r in pool.imap_unordered(_lt1_one, todo):
                done["results"].append(r)
                out.write_text(json.dumps(done, indent=1))
        res = done["results"]
        print(f"step2 LT1 {prior}: {len(res)} checked, {sum(1 for r in res if r['bad_cols'])} with a column outside "
              f"G7, {sum(r['rows_after_t'] for r in res)} rows after t, {time.time() - t0:.0f} s", flush=True)


def step3(fsha: str, procs: int) -> Path:
    dates = sorted({x["date"] for x in _draw()})
    # TB needs sigma_ZM(D) from DERIVED/features/<sha>/_day: pass step 1's folder relative to DERIVED/features
    rel = os.path.relpath(ROOT_F / fsha, g.DERIVED / "features")
    cmd = ["nice", "-n", "10", "uv", "run", "python", str(PIPE / "build_labels33.py"), "--dates", ",".join(dates),
           "--features-sha", rel, "--procs", str(procs), "--out-root", str(ROOT_L)]
    t0 = time.time()
    p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, check=False)
    tail = (p.stdout or "").strip().splitlines()[-1:] + (p.stderr or "").strip().splitlines()[-3:]
    print(f"step3 labels rc={p.returncode} {time.time() - t0:.0f} s; {tail}", flush=True)
    if p.returncode:
        raise SystemExit("label build failed")
    subs = [d for d in ROOT_L.iterdir() if d.is_dir()]
    return max(subs, key=lambda d: d.stat().st_mtime)


def step4(fdir: Path, ldir: Path, sha: str) -> None:
    import lt7_causality as lt7  # noqa: PLC0415
    out = RUNS / f"LT7_{sha}.json"
    t0 = time.time()
    lt7.main(["--features", str(fdir), "--labels", str(ldir), "--out", str(out)])
    print(f"step4 LT7 {time.time() - t0:.0f} s -> {out}", flush=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--expect-sha", required=True)
    ap.add_argument("--steps", default="1,2,3,4")
    ap.add_argument("--procs", type=int, default=3)
    ap.add_argument("--recompute-n", type=int, default=20)
    args = ap.parse_args(argv)
    os.nice(10)
    sha = bf.code_sha12()
    if sha != args.expect_sha:
        raise SystemExit(f"Coder-A feature code on disk is {sha}, not {args.expect_sha}")
    procs = max(1, min(args.procs, 3))
    steps = set(args.steps.split(","))
    fdir = ROOT_F / sha
    if "1" in steps:
        fdir = step1(procs)
    if "2" in steps:
        step2(fdir, sha, procs, args.recompute_n)
    ldir = None
    if "3" in steps:
        ldir = step3(sha, procs)
    if "4" in steps:
        if ldir is None:
            subs = [d for d in ROOT_L.iterdir() if d.is_dir()]
            ldir = max(subs, key=lambda d: d.stat().st_mtime)
        step4(fdir, ldir, sha)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
