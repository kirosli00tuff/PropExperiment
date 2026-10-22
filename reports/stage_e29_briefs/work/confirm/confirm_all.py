"""Stage E.29 SHOULD FIX 7 (R_review.md): grid-confirm (A3_econ.md 2.4) every cell and alone record the reviewer's
task 6 sample did not, with the reviewer's own task code (work/review/review_run.py _work, tags "confirm" and
"alone"), same seed and CRN. Writes only under work/confirm/out. Resumable. Nothing under work/basket/ is written.

Usage (repo root): OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 nice -n 10 \
    uv run python reports/stage_e29_briefs/work/confirm/confirm_all.py --workers 6
"""
from __future__ import annotations

import argparse
import multiprocessing as mp
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REVIEW = HERE.parent / "review"
sys.path.insert(0, str(REVIEW))

import review_run as RR  # noqa: E402

RR.OUT = HERE / "out"  # _work writes to the module global OUT; forked workers inherit it


def tasks() -> list[tuple[str, str]]:
    done = {p.name.split("__", 1)[1][:-5] for p in (REVIEW / "out").glob("confirm__*.json")}
    done |= {p.name.split("__", 1)[1][:-5] for p in (REVIEW / "out").glob("alone__*.json")}
    cells = sorted(p.stem for p in (RR.BASKET / "cells").glob("*.json"))
    t = [("alone" if c.startswith("alone__") else "confirm", c) for c in cells if c not in done]
    return t


def main() -> int:
    import A3_run as R

    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    RR.OUT.mkdir(exist_ok=True)
    todo = [t for t in tasks() if not (RR.OUT / f"{t[0]}__{t[1]}.json").exists()]
    print(f"{time.strftime('%H:%M:%S')} {len(todo)} tasks to run, workers {a.workers}", flush=True)
    R.build_state(list(RR.B.FIRMS))
    with mp.get_context("fork").Pool(min(a.workers, 6), initializer=RR._init, maxtasksperchild=1) as pool:
        res = [pool.apply_async(RR._work, t) for t in todo]
        for r in res:
            tag, cid, sec, msg = r.get()
            print(f"{time.strftime('%H:%M:%S')} done {tag} {cid} {sec:.0f}s {msg}", flush=True)
    print(f"{time.strftime('%H:%M:%S')} all done", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
