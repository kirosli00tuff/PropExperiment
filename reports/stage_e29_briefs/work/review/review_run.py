"""Stage E.29 review compute (BasketReviewer): re-runs cells with the E.29 code, writing only under work/review/out.

Tasks (each a cell spec read from work/basket/cells/<cid>.json, then changed as stated):
  confirm  task 6: mode "confirmed" (E.28 A3_econ.md 2.4 grid confirmation via e29_basket.grid_confirm), same seed
  reseed   task 2: mode "bisection" (the run's search), master seed F.BASE_SEED = 20261022 instead of 20261021
  b0       task 1: B0 setting (ii) limit and market, mode "bisection", same seed (compared with A3_econ.json)
Each task runs in a fresh forked worker (maxtasksperchild=1) so a reseeded state never leaks into another task.
Resumable: a task whose output JSON exists is skipped. Nothing under work/basket/ is written.

Usage (repo root): OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 nice -n 10 \
    uv run python reports/stage_e29_briefs/work/review/review_run.py --workers 4
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import sys
import time
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
BASKET = HERE.parent / "basket"
sys.path.insert(0, str(BASKET))

import e29_basket as B  # noqa: E402

OUT = HERE / "out"
NEW_SEED = 20261022
BEST = {"topstep": "B2", "lucid": "B4", "tradeify": "B2", "mffu": "B2", "bulenox": "B3"}  # E29_tables.md
RESEED = ("limit__primary__bulenox__B3__ii__r0.25", "limit__primary__bulenox__B3__ii__r0.75")  # pick_cells.py


def tasks(batch: int = 1) -> list[tuple[str, str]]:
    if batch == 2:  # extra confirmations: B0 setting (i) (the comparator of every beats flag) and the runners-up
        t = [("confirm", f"limit__primary__{f}__B0__i__rNA") for f in B.FIRMS]  # whose margin is 0 to 2 steps
        t += [("confirm", f"limit__primary__{c}__r0.50") for c in (
            "lucid__B2__i", "lucid__B4__ii", "lucid__B2__ii", "mffu__B4__i", "mffu__B3__i", "bulenox__B1__i")]
        t += [("reseed", "limit__primary__bulenox__B0__ii__rNA")]  # B0 under the new seed, for the beats flag
        t += [("alone", f"alone__{f}__MGC") for f in ("topstep", "tradeify", "bulenox")]  # setting (i) units
        return t
    t = [("confirm", f"limit__primary__{f}__{b}__i__r{r}") for r in ("0.50", "0.25") for f, b in BEST.items()]
    t += [("reseed", c) for c in RESEED]
    t += [("b0", f"{case}__primary__{f}__B0__ii__rNA") for case in ("limit", "market") for f in B.FIRMS]
    return t


def _init() -> None:
    os.nice(10)


def _work(tag: str, cid: str) -> tuple[str, str, float, str]:
    import A3_run as R

    t0 = time.time()
    spec = json.loads((BASKET / "cells" / f"{cid}.json").read_text())["spec"]
    info: dict[str, Any] = {"seed": B.F.BASE_SEED}
    if tag == "alone":  # extended alone break-even with the grid confirmation (bisect_only=False)
        rec = B.run_alone(spec["firm"], spec["code"], R._STATE, B.load_inputs(), bisect_only=False)
        rec = {**rec, "review_tag": tag, "review_info": info, "spec_used": spec}
        (OUT / f"{tag}__{cid}.json").write_text(json.dumps(rec, indent=1))
        return tag, cid, time.time() - t0, f"lim {rec['limit']['mu_star']} mkt {rec['market']['mu_star']}"
    if tag == "confirm":
        spec = {**spec, "mode": "confirmed"}
    elif tag == "reseed":
        z_old = [float(x) for x in R._STATE["draws"][spec["firm"]][0].z[0, :3]]
        B.F.BASE_SEED = NEW_SEED
        R._STATE.clear()
        R.build_state(list(B.FIRMS))
        z_new = [float(x) for x in R._STATE["draws"][spec["firm"]][0].z[0, :3]]
        info = {"seed": B.F.BASE_SEED, "z_attempt_row0_old": z_old, "z_attempt_row0_new": z_new}
    rec = B.run_cell(spec, R._STATE, B.load_inputs())
    rec = {**rec, "review_tag": tag, "review_info": info, "spec_used": spec,
           "started_pdt": time.strftime("%H:%M:%S", time.localtime(t0)), "ended_pdt": time.strftime("%H:%M:%S")}
    p = OUT / f"{tag}__{cid}.json"
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(rec, indent=1))
    os.replace(tmp, p)
    thr = rec.get("threshold", {}).get("value")
    x10 = rec.get("x10K", {}).get("value")
    return tag, cid, time.time() - t0, f"thr {thr} x10K {x10} evals {rec.get('n_evaluations')}"


def main() -> int:
    import A3_run as R

    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--batch", type=int, default=1)
    a = ap.parse_args()
    workers = min(a.workers, 4)
    OUT.mkdir(exist_ok=True)
    todo = [t for t in tasks(a.batch) if not (OUT / f"{t[0]}__{t[1]}.json").exists()]
    print(f"{time.strftime('%H:%M:%S')} {len(todo)} tasks to run, workers {workers}", flush=True)
    R.build_state(list(B.FIRMS))
    print(f"{time.strftime('%H:%M:%S')} state built (seed {B.F.BASE_SEED})", flush=True)
    with mp.get_context("fork").Pool(workers, initializer=_init, maxtasksperchild=1) as pool:
        res = [pool.apply_async(_work, t) for t in todo]
        for r in res:
            tag, cid, sec, msg = r.get()
            print(f"{time.strftime('%H:%M:%S')} done {tag} {cid} {sec:.0f}s {msg}", flush=True)
    print(f"{time.strftime('%H:%M:%S')} all done", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
