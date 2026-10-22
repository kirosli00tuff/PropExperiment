"""Stage E.29 driver: every cell of declaration section 6, resumable (one JSON per cell in cells/).

Cells (limit case): 5 firms x B0 x 2 settings, plus 5 firms x B1..B4 x rho {0, .25, .5, .75} x 2 settings; the
extended alone break-evens of section 5 (0 to 12 ticks; plus MNQ's market case at Topstep and Tradeify, "> 4" in
E.28, needed if B4 is a best basket there, section 6); the market case for B0 and each firm's best basket (section
6 rule, applied here from the limit cells at rho 0.5, at every rho); the Topstep B3 sensitivity (section 4, both
settings, every rho). A cell is skipped when its JSON exists with the same fingerprint (code sha + inputs + spec).

Order (lead, 21:55): limit B0, limit rho 0.5 and 0, then 0.25 and 0.75, then the alone break-evens, then market,
then the sensitivity; a task starts when the results it needs are on disk (setting-(i) cells with a member whose
E.28 break-even is "> 4" wait for its alone break-even). E29_MODE=bisection (default): no grid confirmation pass,
every threshold marked "bisection, unconfirmed".

Usage (repo root): OMP_NUM_THREADS=1 ... nice -n 10 uv run python <this file> run --workers 6
                   ... probe            (two cells, timed)
                   ... collect          (writes reports/stage_e29_briefs/E29_cells.json)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import multiprocessing as mp
import os
import sys
import time
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import e29_basket as B  # noqa: E402

CELLS = HERE / "cells"
OUT_JSON = B.REPO / "reports" / "stage_e29_briefs" / "E29_cells.json"
MAX_WORKERS = 6
OTHER = ("B1", "B2", "B3", "B4")
EXT_CODES = ("ZM", "MGC", "MNQ")


def now() -> str:
    return time.strftime("%H:%M:%S")


def code_fingerprint() -> str:
    h = hashlib.sha256()
    for p in (HERE / "e29_basket.py", HERE / "e29_run.py", B.DECL, B.E28_JSON,
              *(B.E28_WORK / n for n in B.E28_FILES)):
        h.update(p.read_bytes())
    return h.hexdigest()[:16]


def cell_fp(code_fp: str, spec: dict[str, Any]) -> str:
    return hashlib.sha256((code_fp + json.dumps(spec, sort_keys=True)).encode()).hexdigest()[:16]


def rtag(rho: float | None) -> str:
    return "rNA" if rho is None else f"r{rho:.2f}"


def cell_id(spec: dict[str, Any]) -> str:
    if spec["kind"] == "alone":
        return f"alone__{spec['firm']}__{spec['code']}"
    return "__".join((spec["case"], spec["form"], spec["firm"], spec["basket"], spec["setting"], rtag(spec["rho"])))


def load_done(cid: str, fp: str | None = None) -> dict[str, Any] | None:
    p = CELLS / f"{cid}.json"
    if not p.exists():
        return None
    try:
        rec = json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    if fp is not None and rec.get("fingerprint") != fp:
        return None
    return rec


# ------------------------------------------------------------------ alone break-evens ----
def alone_needed() -> list[tuple[str, str]]:
    out = []
    for f in B.FIRMS:
        for c in EXT_CODES:
            r = B.e28_pair(f, c)
            if isinstance(r["mu_star_lim"], str) or isinstance(r["mu_star_mkt"], str):
                out.append((f, c))
    return out


def mu_alone(firm: str, code: str, market: bool, code_fp: str) -> tuple[bool, float | None]:
    """(available, value): E.28's mu*_lim / mu*_mkt when <= 4, else this stage's extended value (None if > 12)."""
    r = B.e28_pair(firm, code)
    v = r["mu_star_mkt" if market else "mu_star_lim"]
    if not isinstance(v, str):
        return True, float(v)
    spec = {"kind": "alone", "firm": firm, "code": code, "mode": MODE}
    rec = load_done(cell_id(spec), cell_fp(code_fp, spec))
    if rec is None:
        return False, None
    x = rec["market" if market else "limit"]["mu_star"]
    return True, (None if isinstance(x, str) else float(x))


# ----------------------------------------------------------------------- best basket ----
def _thr(rec: dict[str, Any] | None) -> float:
    if rec is None or rec.get("status") != "computed":
        return math.inf
    v = rec["threshold"]["value"]
    return math.inf if isinstance(v, str) else float(v)


def best_basket(firm: str, recs: dict[str, dict[str, Any] | None]) -> dict[str, Any]:
    """Section 6: the non-B0 basket with the lowest setting-(i) limit k* at rho 0.5; ties by the lower setting-(ii)
    mu*_QM at rho 0.5, then basket order. Unavailable ("n/a") or "> 4" counts as +inf."""
    rows = []
    for i, b in enumerate(OTHER):
        ki = _thr(recs.get(f"limit__primary__{firm}__{b}__i__r0.50"))
        mii = _thr(recs.get(f"limit__primary__{firm}__{b}__ii__r0.50"))
        rows.append({"basket": b, "k_star_i": ki, "mu_star_QM_ii": mii, "order": i})
    rows.sort(key=lambda r: (r["k_star_i"], r["mu_star_QM_ii"], r["order"]))
    return {"firm": firm, "best": rows[0]["basket"],
            "ranking": [{**r, "k_star_i": None if math.isinf(r["k_star_i"]) else r["k_star_i"],
                         "mu_star_QM_ii": None if math.isinf(r["mu_star_QM_ii"]) else r["mu_star_QM_ii"]}
                        for r in rows]}


# ------------------------------------------------------------------------------ tasks ----
def task_list() -> list[dict[str, Any]]:
    """Abstract tasks in priority order (specs are resolved when ready)."""
    t: list[dict[str, Any]] = []
    for s in ("ii", "i"):
        t += [{"kind": "cell", "case": "limit", "form": "primary", "firm": f, "basket": "B0", "rho": None,
               "setting": s} for f in B.FIRMS]
    for rhos in ((0.5, 0.0), (0.25, 0.75)):
        for rho in rhos:
            for s in ("ii", "i"):
                t += [{"kind": "cell", "case": "limit", "form": "primary", "firm": f, "basket": b, "rho": rho,
                       "setting": s} for f in B.FIRMS for b in OTHER]
    t += [{"kind": "alone", "firm": f, "code": c} for f, c in alone_needed()]
    for s in ("ii", "i"):
        t += [{"kind": "cell", "case": "market", "form": "primary", "firm": f, "basket": "B0", "rho": None,
               "setting": s} for f in B.FIRMS]
    for rho in (0.5, 0.0, 0.25, 0.75):
        for s in ("ii", "i"):
            t += [{"kind": "cell", "case": "market", "form": "primary", "firm": f, "basket": "best", "rho": rho,
                   "setting": s} for f in B.FIRMS]
    for rho in (0.5, 0.0, 0.25, 0.75):
        for s in ("ii", "i"):
            t.append({"kind": "cell", "case": "limit", "form": "b3_sens", "firm": "topstep", "basket": "B3",
                      "rho": rho, "setting": s})
    return t


MODE = os.environ.get("E29_MODE", "bisection")  # "bisection" (unconfirmed) or "confirmed" (grid check)


def resolve(task: dict[str, Any], code_fp: str, b0_mu: dict[str, int]) -> dict[str, Any] | None:
    """The full spec when the task's inputs are on disk, else None."""
    if task["kind"] == "alone":
        return {**task, "mode": MODE}
    spec = dict(task)
    if spec["basket"] == "best":
        recs = {}
        for b in OTHER:
            for s in ("i", "ii"):
                cid = f"limit__primary__{spec['firm']}__{b}__{s}__r0.50"
                sp = resolve_cell_spec({"kind": "cell", "case": "limit", "form": "primary", "firm": spec["firm"],
                                        "basket": b, "rho": 0.5, "setting": s, "mode": MODE}, code_fp, b0_mu)
                rec = None if sp is None else load_done(cid, cell_fp(code_fp, sp))
                if rec is None:
                    return None
                recs[cid] = rec
        spec["basket"] = best_basket(spec["firm"], recs)["best"]
    return resolve_cell_spec(spec, code_fp, b0_mu)


def resolve_cell_spec(spec: dict[str, Any], code_fp: str, b0_mu: dict[str, int]) -> dict[str, Any] | None:
    spec = {**spec, "mode": MODE}
    market = spec["case"] == "market"
    if spec["setting"] == "i":
        mu = {}
        for c in B.BASKETS[spec["basket"]]:
            ok, v = mu_alone(spec["firm"], c, market, code_fp)
            if not ok:
                return None
            mu[c] = v
        spec["mu_star"] = mu
    else:
        spec["mu_star"] = None
    spec["report_g_b0"] = b0_mu[spec["firm"]] if spec["setting"] == "ii" else None
    return spec


# ---------------------------------------------------------------------------- workers ----
_INPUTS: dict[str, Any] = {}


def _init_worker() -> None:
    os.nice(10)


def _work(spec: dict[str, Any], fp: str) -> tuple[str, float, str]:
    import A3_run as R

    inputs = _INPUTS or B.load_inputs()
    t0 = time.time()
    if spec["kind"] == "alone":
        rec = B.run_alone(spec["firm"], spec["code"], R._STATE, inputs, spec.get("mode") == "bisection")
        msg = f"lim {rec['limit']['mu_star']} mkt {rec['market']['mu_star']} evals {rec['n_evaluations']}"
    else:
        rec = B.run_cell(spec, R._STATE, inputs)
        if rec["status"] == "computed":
            msg = (f"thr {rec['threshold']['value']} x10K {rec.get('x10K', {}).get('value')} "
                   f"check {rec['threshold']['status']} evals {rec['n_evaluations']}")
        else:
            msg = rec["status"]
    rec = {**rec, "spec": spec, "fingerprint": fp, "started_pdt": time.strftime("%H:%M:%S", time.localtime(t0)),
           "ended_pdt": now()}
    cid = cell_id(spec)
    out = CELLS / f"{cid}.json"
    tmp = out.with_suffix(".tmp")
    tmp.write_text(json.dumps(rec, indent=1))
    os.replace(tmp, out)
    return cid, time.time() - t0, msg


def b0_report_points() -> dict[str, int]:
    return {f: int(round(float(B.e28_pair(f, "QM")["mu_star_lim"]) * 100)) for f in B.FIRMS}


def schedule(tasks: list[dict[str, Any]], workers: int) -> int:
    import A3_run as R

    workers = min(workers, MAX_WORKERS)
    CELLS.mkdir(exist_ok=True)
    code_fp = code_fingerprint()
    b0_mu = b0_report_points()
    pending = list(tasks)
    print(f"{now()} code fingerprint {code_fp}; {len(pending)} tasks; workers {workers}", flush=True)
    R.build_state(list(B.FIRMS))
    _INPUTS.update(B.load_inputs())
    print(f"{now()} state built (models, draws, cycle indices)", flush=True)
    inflight: dict[str, Any] = {}
    n_done = n_skip = 0
    with mp.get_context("fork").Pool(workers, initializer=_init_worker) as pool:
        while pending or inflight:
            launched = True
            while launched and len(inflight) < workers:
                launched = False
                for task in list(pending):
                    spec = resolve(task, code_fp, b0_mu)
                    if spec is None:
                        continue
                    pending.remove(task)
                    cid = cell_id(spec)
                    fp = cell_fp(code_fp, spec)
                    if load_done(cid, fp) is not None or cid in inflight:
                        n_skip += 1
                        launched = True
                        break
                    inflight[cid] = pool.apply_async(_work, (spec, fp))
                    print(f"{now()} start {cid}", flush=True)
                    launched = True
                    break
            finished = [c for c, r in inflight.items() if r.ready()]
            for c in finished:
                cid, sec, msg = inflight.pop(c).get()
                n_done += 1
                print(f"{now()} done {cid} {sec:.0f}s {msg}", flush=True)
            if not finished:
                if not inflight and pending:
                    print(f"{now()} {len(pending)} tasks blocked with nothing running: {pending[:3]}", flush=True)
                    return 1
                time.sleep(1.0)
    print(f"{now()} all tasks finished: {n_done} run, {n_skip} already current", flush=True)
    return 0


# ---------------------------------------------------------------------------- collect ----
def cmd_collect() -> int:
    code_fp = code_fingerprint()
    b0_mu = b0_report_points()
    cells, missing, alone, seen = [], [], [], set()
    for task in task_list():
        spec = resolve(task, code_fp, b0_mu)
        if spec is None:
            missing.append(task)
            continue
        cid = cell_id(spec)
        if cid in seen:
            continue
        seen.add(cid)
        rec = load_done(cid, cell_fp(code_fp, spec))
        if rec is None:
            missing.append(cid)
            continue
        rec = {k: v for k, v in rec.items() if k != "evaluations"}
        if task["kind"] == "alone":
            for case in ("limit", "market"):
                rec[case] = {k: v for k, v in rec[case].items() if k != "evaluations"}
            alone.append({**rec, "cell_file": str((CELLS / f"{cid}.json").relative_to(B.REPO))})
        else:
            cells.append({**rec, "cell_id": cid, "cell_file": str((CELLS / f"{cid}.json").relative_to(B.REPO))})
    lim = {c["cell_id"]: c for c in cells}
    best = []
    for f in B.FIRMS:
        ids = [f"limit__primary__{f}__{b}__{s}__r0.50" for b in OTHER for s in ("i", "ii")]
        if all(i in lim for i in ids):
            best.append(best_basket(f, {i: lim[i] for i in ids}))
    out = {"stage": "E.29", "worker": "BasketCoder-OpusXHigh", "generated_pdt": time.strftime("%Y-%m-%d %H:%M %Z"),
           "declaration": {"path": "reports/stage_e29_model.md", "sha256": B.sha256_file(B.DECL),
                           "expected": B.DECL_SHA},
           "e28_sha256": B.e28_shas(), "code_fingerprint": code_fp,
           "code_sha256": {n: B.sha256_file(HERE / n) for n in ("e29_basket.py", "e29_run.py")},
           "b0_check": b0_check(cells), "best_basket": best, "alone": alone, "cells": cells,
           "missing": missing, "n_cells": len(cells), "n_missing": len(missing)}
    OUT_JSON.write_text(json.dumps(out, indent=1))
    print(f"{len(cells)} cells, {len(alone)} alone records, {len(missing)} missing -> {OUT_JSON}")
    return 0


def b0_check(cells: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """B0 setting (ii) against E.28's QM pair: mu*_lim, mu*_mkt, mu10K, cost per attempt."""
    rows = []
    for f in B.FIRMS:
        e = B.e28_pair(f, "QM")
        lim = next((c for c in cells if c["cell_id"] == f"limit__primary__{f}__B0__ii__rNA"), None)
        mkt = next((c for c in cells if c["cell_id"] == f"market__primary__{f}__B0__ii__rNA"), None)
        row = {"firm": f, "e28": {k: e[k] for k in ("mu_star_lim", "mu_star_mkt", "mu10K", "cost_per_attempt_usd")}}
        if lim:
            row["e29"] = {"mu_star_lim": lim["threshold"]["value"], "mu10K": lim["x10K"]["value"],
                          "cost_per_attempt_usd": lim["cost_per_attempt_usd"]}
        if mkt:
            row.setdefault("e29", {})["mu_star_mkt"] = mkt["threshold"]["value"]
        row["equal"] = bool(lim and mkt) and all(row["e29"][k] == row["e28"][k] for k in row["e28"])
        rows.append(row)
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("run", "probe", "collect", "list"))
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args(argv)
    if a.cmd == "collect":
        return cmd_collect()
    tasks = task_list()
    if a.cmd == "list":
        print(len(tasks), "tasks;", sum(t["kind"] == "alone" for t in tasks), "alone:", alone_needed())
        return 0
    if a.cmd == "probe":
        probe = [t for t in tasks if t["kind"] == "cell" and t["case"] == "limit" and t["form"] == "primary"
                 and t["rho"] == 0.5 and ((t["firm"], t["basket"], t["setting"]) in
                                          {("topstep", "B3", "ii"), ("bulenox", "B1", "i")})]
        return schedule(probe, 2)
    return schedule(tasks, a.workers)


if __name__ == "__main__":
    sys.exit(main())
