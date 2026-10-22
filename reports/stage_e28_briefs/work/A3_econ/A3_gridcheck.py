"""A3 grid confirmation of the bisection thresholds, and the monotonicity scan (resumable by pair).

Why: A3_run.py finds mu*_lim, mu*_mkt and mu10K by bisection on the 0.01-tick grid, which is exact only if EV(mu)
(and P10K(mu)) is nondecreasing. The pair records show EV is not monotone at low mu (a trough where the net drift
is near 0 and attempts run to the 756-day horizon paying rebills), so the bisection's final bracket alone does not
prove that no grid point below k* has f >= 0. This script checks it directly on the same common random numbers:

  lattice  j = mu_lim / 0.01 (d = 0.01 j - c_lim; the market case uses the same d at j = k_mkt - 100)
  regions  EV:   j in [0, k*_lim) u [-100, k*_mkt - 100)   (k = 401 when the threshold is "> 4")
           P10K: j in [0, k10)
  points   every j = 0 mod 10 in the regions (0.10-tick sub-grid) and the region ends; every grid point in the
           0.10 ticks below each threshold found; then every grid point of any sub-grid interval with an end
           "near" the threshold (EV >= -max(5 SE, USD 100), or P10K >= 0.40), filled densely
  result   per threshold: the largest f below it (margin), violations (grid points below it with f >= 0) and,
           if any, the corrected smallest grid point (the spec's definition); plus a from-scratch recomputation of
           one stored point (determinism check against the pair record)

Monotonicity scan: EV and P10K at mu = 0, 0.25, ..., 4 (limit case) for A3_run.MONO_PAIRS -> A3_monotone.json.
Usage (from the repo root): PYTHONDONTWRITEBYTECODE=1 uv run python <this file> --workers 4
"""

from __future__ import annotations

import argparse
import json
import math
import multiprocessing as mp
import os
import resource
import sys
import time
from pathlib import Path
from typing import Any

WORK = Path(__file__).resolve().parent
sys.path.insert(0, str(WORK))

import A3_funnel as F  # noqa: E402
import A3_run as R  # noqa: E402

OUT_DIR = WORK / "gridcheck"
MONO_OUT = WORK / "A3_monotone.json"
COARSE = 10  # sub-grid step in grid units (0.10 tick)
DENSE_BELOW = 10  # grid points checked densely below each threshold found
NEAR_SE = 5.0
NEAR_USD = 100.0
NEAR_P = 0.40
J_TOP = 400
J_LOW = -100
MONO_STEP = 25


def _k(mu: float | str) -> int | None:
    return None if isinstance(mu, str) else int(round(mu * 100))


def regions(rec: dict[str, Any]) -> tuple[set[int], set[int]]:
    kl, km, k10 = _k(rec["mu_star_lim"]), _k(rec["mu_star_mkt"]), _k(rec["mu10K"])
    ev = set(range(0, kl if kl is not None else J_TOP + 1))
    ev |= set(range(J_LOW, (km if km is not None else J_TOP + 1) - 100))
    p = set(range(0, k10 if k10 is not None else J_TOP + 1))
    return ev, p


class GridEval:
    """EV (and P10K where needed) at lattice points, seeded with the pair record's on-lattice evaluations."""

    def __init__(self, firm: str, code: str, rec: dict[str, Any], inputs: dict[str, Any]) -> None:
        self.model = R._STATE["models"][firm]
        self.cand = inputs["candidates"][code]
        self.c = rec["c_lim_ticks"]
        self.da, self.dx = R._STATE["draws"][firm]
        self.att, self.xfa = R._STATE["idx"]
        self.pts: dict[int, dict[str, Any]] = {}
        self.n_new = 0
        for e in rec["evaluations"]:
            x = e["mu_lim"] * 100
            j = int(round(x))
            if abs(x - j) < 1e-4:  # on the lattice (sensitivity points at other fees are not)
                self.pts[j] = {"ev": e["ev"], "se": e["se"], "p10k": e["p10k"], "src": "record"}

    def compute(self, j: int, need_p: bool) -> dict[str, Any]:
        d = j * R.STEP - self.c
        v, sig = self.cand["v_usd"], self.cand["sigma_1m_ticks"]
        law = F.DayLaw(m=F.T_RT * d * v, s=math.sqrt(F.T_RT) * sig * v)
        pools = F.simulate_pools(self.model, law, self.da, self.dx)
        st = F.cycle_stats(self.model, pools, self.att, self.xfa)
        p = F.campaign_p_reach(self.model, pools) if need_p else None
        self.n_new += 1
        return {"ev": st.ev, "se": st.se, "p10k": p, "src": "gridcheck"}

    def get(self, j: int, need_p: bool) -> dict[str, Any]:
        r = self.pts.get(j)
        if r is None or (need_p and r["p10k"] is None):
            r = self.compute(j, need_p)
            self.pts[j] = r
        return r


def _near_ev(r: dict[str, Any]) -> bool:
    return r["ev"] >= -max(NEAR_SE * r["se"], NEAR_USD)


def _fill(ge: GridEval, region: set[int], is_p: bool, p_region: set[int]) -> int:
    """Dense-fill every gap between evaluated points of `region` that has an end near the threshold."""
    filled = 0
    js = sorted(j for j in ge.pts if j in region and (not is_p or ge.pts[j]["p10k"] is not None))
    for a, b in zip(js, js[1:], strict=False):
        if b - a <= 1:
            continue
        ra, rb = ge.pts[a], ge.pts[b]
        near = (ra["p10k"] >= NEAR_P or rb["p10k"] >= NEAR_P) if is_p else (_near_ev(ra) or _near_ev(rb))
        if near:
            for j in range(a + 1, b):
                ge.get(j, j in p_region)
            filled += 1
    return filled


def _verdict(ge: GridEval, region: set[int], is_p: bool, lo: int, hi: int | None) -> dict[str, Any]:
    """Threshold check on [lo, hi): the largest f below the threshold, violations, corrected threshold."""
    top = hi if hi is not None else (J_TOP + 1 if lo >= 0 else J_TOP + 1 - 100)  # market case: j = k - 100
    key = "p10k" if is_p else "ev"
    js = sorted(j for j in ge.pts if lo <= j < top and j in region and ge.pts[j][key] is not None)
    if not js:
        return {"n_checked": 0}
    vals = [(j, ge.pts[j][key]) for j in js]
    thr = 0.5 if is_p else 0.0
    viol = [j for j, x in vals if x >= thr]
    jmax, xmax = max(vals, key=lambda t: t[1])
    out = {"n_checked": len(js), "n_dense_points": sum(1 for j in js if ge.pts[j]["src"] == "gridcheck"),
           "max_below": {"j": jmax, "value": xmax,
                         "se": None if is_p else ge.pts[jmax]["se"]},
           "violations": viol, "confirmed": not viol}
    if viol:  # find the smallest grid point with f >= thr: fill densely below the first violation
        first = viol[0]
        prev = max([j for j in js if j < first], default=lo)
        for j in range(prev, first):
            ge.get(j, is_p)
        allv = [j for j in range(lo, first + 1) if j in ge.pts and ge.pts[j][key] is not None
                and ge.pts[j][key] >= thr]
        out["corrected_k"] = min(allv)
    return out


def check_pair(firm: str, code: str, fp: str) -> dict[str, Any]:
    t0 = time.time()
    inputs = json.loads(R.INPUTS.read_text())
    rec = json.loads((R.PAIRS_DIR / f"{firm}__{code}.json").read_text())
    if rec.get("fingerprint") != fp:
        raise RuntimeError(f"stale pair record {firm} {code}")
    ge = GridEval(firm, code, rec, inputs)
    kl, km, k10 = _k(rec["mu_star_lim"]), _k(rec["mu_star_mkt"]), _k(rec["mu10K"])
    ev_reg, p_reg = regions(rec)
    # determinism check: recompute one stored on-lattice point from scratch
    j_rep = kl if kl is not None else J_TOP
    stored = ge.pts.get(j_rep)
    repro = None
    if stored is not None:
        new = ge.compute(j_rep, True)
        repro = {"j": j_rep, "ev_stored": stored["ev"], "ev_recomputed": new["ev"],
                 "p10k_stored": stored["p10k"], "p10k_recomputed": new["p10k"],
                 "equal": new["ev"] == stored["ev"] and new["p10k"] == stored["p10k"]}
    pts = {j for j in ev_reg | p_reg if j % COARSE == 0}
    pts |= {min(ev_reg), max(ev_reg)} | ({0, max(p_reg)} if p_reg else set())
    for k in (kl, k10):
        if k is not None:
            pts |= set(range(max(k - DENSE_BELOW, J_LOW if k == kl else 0), k))
    if kl is not None:  # the market threshold sits at the same d (j = k_mkt - 100 = k_lim)
        pts |= set(range(max(kl - DENSE_BELOW, J_LOW), kl))
    for j in sorted(pts):
        ge.get(j, j in p_reg)
    n_fill = _fill(ge, ev_reg, False, p_reg) + (_fill(ge, p_reg, True, p_reg) if p_reg else 0)
    checks = {"mu_star_lim": _verdict(ge, ev_reg, False, 0, kl),
              "mu_star_mkt": _verdict(ge, ev_reg, False, J_LOW, None if km is None else km - 100),
              "mu10K": _verdict(ge, p_reg, True, 0, k10)}
    curve = sorted((j, r["ev"], r["se"], r["p10k"]) for j, r in ge.pts.items())
    ev_seq = [x for _, x, _, _ in curve]
    drops = sum(1 for a, b in zip(ev_seq, ev_seq[1:], strict=False) if b < a - 1e-9)
    return {"firm": firm, "code": code, "fingerprint": fp, "c_lim_ticks": ge.c,
            "thresholds": {"mu_star_lim": rec["mu_star_lim"], "mu_star_mkt": rec["mu_star_mkt"],
                           "mu10K": rec["mu10K"]},
            "checks": checks, "repro": repro, "n_points": len(ge.pts), "n_new_evaluations": ge.n_new,
            "n_dense_filled_gaps": n_fill, "ev_decreasing_steps_on_lattice": drops,
            "curve": [{"j": j, "mu_lim": round(j * R.STEP, 2), "ev": e, "se": s, "p10k": p} for j, e, s, p in curve],
            "runtime_s": round(time.time() - t0, 1),
            "maxrss_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024}


def _task(args: tuple[str, str, str]) -> tuple[str, str, float, str]:
    firm, code, fp = args
    res = check_pair(firm, code, fp)
    out = OUT_DIR / f"{firm}__{code}.json"
    tmp = out.with_suffix(".tmp")
    tmp.write_text(json.dumps(res, indent=1))
    os.replace(tmp, out)
    c = res["checks"]
    ok = all(v.get("confirmed", True) for v in c.values())
    rep = res["repro"]["equal"] if res["repro"] else None
    return firm, code, res["runtime_s"], f"confirmed={ok} repro={rep} new={res['n_new_evaluations']}"


def monotone_rows(fp: str) -> None:
    """EV and P10K at mu = 0, 0.25, ..., 4 (limit case) for the check pairs, from the dense curves on disk plus
    the missing quarter points (computed here, single process)."""
    inputs = json.loads(R.INPUTS.read_text())
    rows = []
    for firm, code in R.MONO_PAIRS:
        rec = json.loads((R.PAIRS_DIR / f"{firm}__{code}.json").read_text())
        ge = GridEval(firm, code, rec, inputs)
        gc = OUT_DIR / f"{firm}__{code}.json"
        if gc.exists():
            for p in json.loads(gc.read_text())["curve"]:
                if p["p10k"] is not None:
                    ge.pts[p["j"]] = {"ev": p["ev"], "se": p["se"], "p10k": p["p10k"], "src": "gridcheck"}
        js = list(range(0, J_TOP + 1, MONO_STEP))
        pts = [ge.get(j, True) for j in js]
        ev = [r["ev"] for r in pts]
        p10 = [r["p10k"] for r in pts]
        rows.append({"firm": firm, "code": code, "mu": [j * R.STEP for j in js], "ev": ev,
                     "se": [r["se"] for r in pts], "p10k": p10,
                     "ev_nondecreasing": all(b >= a - 1e-9 for a, b in zip(ev, ev[1:], strict=False)),
                     "p10k_nondecreasing": all(b >= a - 1e-12 for a, b in zip(p10, p10[1:], strict=False))})
        print(f"{time.strftime('%H:%M:%S')} mono {firm} {code} ev_nondecr={rows[-1]['ev_nondecreasing']} "
              f"p_nondecr={rows[-1]['p10k_nondecreasing']}", flush=True)
    MONO_OUT.write_text(json.dumps({"fingerprint": fp, "step_ticks": MONO_STEP * R.STEP, "rows": rows}, indent=1))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--only")
    a = ap.parse_args()
    os.nice(10)
    OUT_DIR.mkdir(exist_ok=True)
    fp = R._fingerprint()
    inputs = json.loads(R.INPUTS.read_text())
    todo = []
    for p in inputs["pairs"]:
        rec = json.loads((R.PAIRS_DIR / f"{p['firm']}__{p['code']}.json").read_text())
        if not rec.get("computed"):
            continue
        if a.only and f"{p['firm']}:{p['code']}" not in a.only.split(","):
            continue
        out = OUT_DIR / f"{p['firm']}__{p['code']}.json"
        if out.exists() and json.loads(out.read_text()).get("fingerprint") == fp:
            continue
        ev_reg, p_reg = regions(rec)
        todo.append((len(ev_reg | p_reg) * rec["runtime_s"] / max(rec["n_evaluations"], 1), p["firm"], p["code"]))
    todo.sort(reverse=True)
    print(f"{time.strftime('%H:%M:%S')} fingerprint {fp}: {len(todo)} pairs to check on {a.workers} workers",
          flush=True)
    if todo:
        R.build_state(sorted({f for _, f, _ in todo} | ({f for f, _ in R.MONO_PAIRS} if not a.only else set())))
        with mp.get_context("fork").Pool(min(a.workers, R.MAX_WORKERS), initializer=R._init_worker) as pool:
            for firm, code, sec, msg in pool.imap_unordered(_task, [(f, c, fp) for _, f, c in todo]):
                print(f"{time.strftime('%H:%M:%S')} {firm} {code} {sec:.0f}s {msg}", flush=True)
    if not a.only:
        if not R._STATE:
            R.build_state(sorted({f for f, _ in R.MONO_PAIRS}))
        monotone_rows(fp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
