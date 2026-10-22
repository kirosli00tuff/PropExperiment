"""A3 driver: mu*_lim, mu*_mkt, mu10K and cost per attempt for every (firm, candidate) pair, resumable by pair.

For each pair, mu (gross edge per trade, ticks) lives on the spec's grid 0, 0.01, ..., 4. The expected net cash per
cycle EV(mu) and the 250-day probability P10K(mu) depend on mu only through d = mu - c (common random numbers),
so every evaluation at a d is cached and shared by the limit case (c = F_rt / v) and the market case
(c = F_rt / v + S_rt). Each threshold is found by bisection on the integer grid index k (mu = 0.01 k) for the
smallest k with f(k) >= 0, assuming f monotone in mu; the final bracket (f(k*-1) < 0 <= f(k*)) is the spec's
"final check" of the grid point, and every pair's cached points are tested for monotonicity afterwards.
"> 4" when f(400) < 0.

Usage: uv run python A3_run.py run --workers 3 [--firms topstep,lucid] [--codes NQ,MNQ]
       uv run python A3_run.py monotone      (EV and P10K on mu = 0, 0.25, ..., 4 for the check pairs)
       uv run python A3_run.py collect       (writes reports/stage_e28_briefs/A3_econ.json)
"""

from __future__ import annotations

import argparse
import hashlib
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
REPO = WORK.parents[3]
PAIRS_DIR = WORK / "pairs"
INPUTS = WORK / "A3_inputs.json"
OUT_JSON = REPO / "reports" / "stage_e28_briefs" / "A3_econ.json"
GRID_N = 400  # mu = 0.01 k, k = 0..400
STEP = 0.01
MONO_PAIRS = (("topstep", "NQ"), ("topstep", "MNQ"), ("lucid", "CL"), ("tradeify", "6E"), ("mffu", "GC"),
              ("bulenox", "NQ"), ("bulenox", "ZS"), ("tradeify", "MCL"))
MAX_WORKERS = 4


def _fingerprint() -> str:
    h = hashlib.sha256()
    for name in ("A3_funnel.py", "A3_models.py", "A3_run.py", "A3_inputs.json"):
        h.update((WORK / name).read_bytes())
    return h.hexdigest()[:16]


def _fmt_mu(k: int | None) -> float | str:
    return "> 4" if k is None else round(k * STEP, 2)


class PairEval:
    """Cached evaluations of one pair: d -> (EV incl. API, SE, EV ex API, P10K, cycle stats)."""

    def __init__(self, model: Any, cand: dict[str, Any], c_lim: float, draws: tuple[Any, Any],
                 idx: tuple[Any, Any]) -> None:
        self.model, self.cand, self.c_lim = model, cand, c_lim
        self.da, self.dx = draws
        self.att, self.xfa = idx
        self.cache: dict[float, dict[str, Any]] = {}
        self.n_evals = 0

    def at(self, d: float) -> dict[str, Any]:
        import A3_funnel as F

        key = round(d, 9)
        if key not in self.cache:
            law = F.DayLaw(m=F.T_RT * d * self.cand["v_usd"],
                           s=math.sqrt(F.T_RT) * self.cand["sigma_1m_ticks"] * self.cand["v_usd"])
            pools = F.simulate_pools(self.model, law, self.da, self.dx)
            st = F.cycle_stats(self.model, pools, self.att, self.xfa)
            p = F.campaign_p_reach(self.model, pools)
            self.cache[key] = {"d": key, "ev": st.ev, "se": st.se, "ev_ex_api": st.ev_ex_api, "p10k": p,
                               "stats": st.__dict__}
            self.n_evals += 1
        return self.cache[key]

    def f(self, k: int, c: float, what: str) -> float:
        r = self.at(k * STEP - c)
        if what == "ev":
            return r["ev"]
        if what == "ev_ex_api":
            return r["ev_ex_api"]
        return r["p10k"] - 0.5

    def smallest(self, c: float, what: str, lo: int = 0, hi: int = GRID_N) -> int | None:
        """Smallest k in [lo, hi] with f(k) >= 0 (f assumed nondecreasing); None if f(hi) < 0."""
        if self.f(hi, c, what) < 0:
            return None
        if self.f(lo, c, what) >= 0:
            return lo
        while hi - lo > 1:  # invariant f(lo) < 0 <= f(hi)
            mid = (lo + hi) // 2
            if self.f(mid, c, what) >= 0:
                hi = mid
            else:
                lo = mid
        return hi

    def near(self, k_guess: int, c: float, what: str) -> int | None:
        """Smallest k with f(k) >= 0 found by walking from a guess (for sensitivities sharing the curve)."""
        k = min(max(k_guess, 0), GRID_N)
        if self.f(k, c, what) >= 0:
            while k > 0 and self.f(k - 1, c, what) >= 0:
                k -= 1
            return k
        while k < GRID_N:
            k += 1
            if self.f(k, c, what) >= 0:
                return k
        return None


def _guess(k_main: int | None, c_main: float, c_new: float) -> int:
    if k_main is None:
        return GRID_N
    return int(math.ceil((k_main * STEP - c_main + c_new) / STEP - 1e-9))


def monotone_violations(cache: dict[float, dict[str, Any]], key: str) -> list[list[float]]:
    pts = sorted((d, r[key]) for d, r in cache.items())
    return [[a[0], a[1], b[0], b[1]] for a, b in zip(pts, pts[1:], strict=False) if b[1] < a[1] - 1e-9]


def run_pair(firm: str, code: str, inputs: dict[str, Any], fp: str, state: dict[str, Any]) -> dict[str, Any]:
    import A3_funnel as F

    t0 = time.time()
    pair = next(p for p in inputs["pairs"] if p["firm"] == firm and p["code"] == code)
    cand = inputs["candidates"][code]
    model = state["models"][firm]
    flags = list(pair["flags"])
    v, sig = cand["v_usd"], cand["sigma_1m_ticks"]
    base = {"firm": firm, "code": code, "plan": model.plan, "F_rt_usd": pair["F_rt_usd"],
            "F_rt_status": pair["F_rt_status"],
            "F_rt_source": {k: pair["fee_src"].get(k) for k in ("source_file", "quote", "unit", "note")},
            "F_rt_ticks": None if pair["F_rt_usd"] is None else pair["F_rt_usd"] / v,
            "S_rt_ticks": cand["S_rt_ticks"], "S_rt_status": cand["S_rt_status"], "S_rt_note": cand["S_rt_note"],
            "v": v, "v_source": cand["v_source"], "sigma_T": sig, "sigma_source": cand["magnitude_source"],
            "R_d_ticks": cand["R_d_ticks"], "MLL_usd": model.mll_usd, "DLL_usd": model.dll_usd,
            "DLL_ticks": None if model.dll_usd is None else model.dll_usd / v,
            "position_limit": pair["position_limit"], "position_limit_text": pair["position_limit_text"],
            "room": None if cand["R_d_ticks"] is None else model.mll_usd / (cand["R_d_ticks"] * v),
            "api_monthly_usd": model.api_monthly_usd, "fingerprint": fp}
    if "sibling" in cand:
        flags.append(f"sigma_1m and R_d from sibling {cand['sibling']} (OC-1)")
    if cand["S_rt_status"] == "u":
        flags.append("S_rt default 1 (u)")
    if sig is None or pair["F_rt_usd"] is None:
        flags.append("not computed: sigma_1m unknown" if sig is None else "not computed: fee unknown")
        return {**base, "mu_star_lim": None, "mu_star_mkt": None, "mu10K": None, "cost_per_attempt_usd": None,
                "flags": flags, "computed": False, "runtime_s": round(time.time() - t0, 2)}
    c_lim = pair["F_rt_usd"] / v
    c_mkt = c_lim + cand["S_rt_ticks"]
    pe = PairEval(model, cand, c_lim, state["draws"][firm], state["idx"])
    k_lim = pe.smallest(c_lim, "ev")
    k_mkt = pe.near(_guess(k_lim, c_lim, c_mkt), c_mkt, "ev") if k_lim is not None else None
    k10 = pe.smallest(c_lim, "p10k")
    at0 = pe.at(-c_lim)
    sens: dict[str, Any] = {}
    if model.api_monthly_usd > 0:
        k_ex = pe.smallest(c_lim, "ev_ex_api", 0, k_lim if k_lim is not None else GRID_N)
        sens["mu_star_lim_ex_api"] = _fmt_mu(k_ex)
    alt = None
    if firm == "lucid" and pair.get("F_rt_alt_usd") is not None:
        alt = max(pair["F_rt_alt_usd"], pair["F_rt_usd"])
    elif firm == "topstep":
        alt = max(3.70, pair["F_rt_usd"])
    if alt is not None:
        c_alt = alt / v
        sens["alt_fee"] = {"F_rt_usd": alt, "rule": ("highest fee for this product at the other four firms "
                                                     "('u' rule: exchange/NFA inclusion not stated)")
                           if firm == "lucid" else "LFA-costs page: $3.70/lot simulated fee (both stages)",
                           "mu_star_lim": _fmt_mu(pe.near(_guess(k_lim, c_lim, c_alt), c_alt, "ev"))}
    if cand.get("S_rt_mean_sourced"):
        c_m = c_lim + cand["S_rt_mean_sourced"]
        sens["S_rt_mean"] = {"S_rt_ticks": cand["S_rt_mean_sourced"],
                             "mu_star_mkt": _fmt_mu(pe.near(_guess(k_lim, c_lim, c_m), c_m, "ev"))}
    if k_lim is not None and k_mkt is not None:
        assert k_mkt >= k_lim
    viol = monotone_violations(pe.cache, "ev") + monotone_violations(pe.cache, "p10k")
    if viol:
        flags.append(f"non-monotone cached points: {len(viol)}")
    st0 = at0["stats"]
    rec = {**base, "c_lim_ticks": c_lim, "c_mkt_ticks": c_mkt,
           "mu_star_lim": _fmt_mu(k_lim), "mu_star_mkt": _fmt_mu(k_mkt), "mu10K": _fmt_mu(k10),
           "cost_per_attempt_usd": st0["eval_fees_per_attempt"],
           "cost_per_attempt_variants": {"eval_fees_plus_api": st0["eval_fees_api_per_attempt"],
                                         "all_fees_incl_activation_and_api": st0["all_fees_per_attempt"]},
           "at_mu0_lim": {k: st0[k] for k in ("ev", "se", "p_pass_attempt", "mean_attempts", "p_no_payout",
                                              "mean_cycle_days")},
           "grid_check": {name: (None if k is None else {
               "k": k, "f_at_k": pe.f(k, c, what), "f_at_k_minus_1": None if k == 0 else pe.f(k - 1, c, what)})
               for name, k, c, what in (("mu_star_lim", k_lim, c_lim, "ev"), ("mu_star_mkt", k_mkt, c_mkt, "ev"),
                                        ("mu10K", k10, c_lim, "p10k"))},
           "sensitivities": sens, "flags": flags, "computed": True, "monotone_violations": viol,
           "n_evaluations": pe.n_evals,
           "evaluations": [{"d": r["d"], "mu_lim": round(r["d"] + c_lim, 6), "ev": r["ev"], "se": r["se"],
                            "ev_ex_api": r["ev_ex_api"], "p10k": r["p10k"]} for r in
                           sorted(pe.cache.values(), key=lambda r: r["d"])],
           "runtime_s": round(time.time() - t0, 2),
           "maxrss_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024}
    return rec


_STATE: dict[str, Any] = {}


def build_state(firms: list[str]) -> None:
    """Models, common random numbers and cycle index draws, built once in the parent: forked workers share
    the read-only arrays (copy-on-write pages are never written). The intraday firms reuse the same z and e1
    and add only the bridge-maximum draws e2."""
    import A3_funnel as F
    import A3_models as M

    models = M.firm_models()
    plain = (F.make_draws("attempt"), F.make_draws("xfa"))
    draws = {}
    for f in firms:
        if models[f].needs_max:
            e2 = [F.make_e2(ph) for ph in ("attempt", "xfa")]
            draws[f] = tuple(F.Draws(d.z, d.e1, e) for d, e in zip(plain, e2, strict=True))
        else:
            draws[f] = plain
    _STATE.update(models=models, draws=draws, idx=F.cycle_indices())


def _init_worker() -> None:
    os.nice(10)


def _task(args: tuple[str, str, str]) -> tuple[str, str, float, str]:
    firm, code, fp = args
    inputs = json.loads(INPUTS.read_text())
    rec = run_pair(firm, code, inputs, fp, _STATE)
    out = PAIRS_DIR / f"{firm}__{code}.json"
    tmp = out.with_suffix(".tmp")
    tmp.write_text(json.dumps(rec, indent=1))
    os.replace(tmp, out)
    return firm, code, rec["runtime_s"], f"{rec['mu_star_lim']} {rec['mu_star_mkt']} {rec['mu10K']}"


def _done(firm: str, code: str, fp: str) -> bool:
    out = PAIRS_DIR / f"{firm}__{code}.json"
    if not out.exists():
        return False
    try:
        return json.loads(out.read_text()).get("fingerprint") == fp
    except (OSError, json.JSONDecodeError):
        return False


def cmd_run(workers: int, firms: list[str] | None, codes: list[str] | None) -> int:
    workers = min(workers, MAX_WORKERS)
    PAIRS_DIR.mkdir(exist_ok=True)
    fp = _fingerprint()
    inputs = json.loads(INPUTS.read_text())
    todo = [(p["firm"], p["code"], fp) for p in inputs["pairs"]
            if (firms is None or p["firm"] in firms) and (codes is None or p["code"] in codes)
            and not _done(p["firm"], p["code"], fp)]
    # long pairs first (low vol micro products need long attempts); unknown sigma is instant
    todo.sort(key=lambda t: -(inputs["candidates"][t[1]]["sigma_1m_ticks"] or 1e9) ** -1)
    need = sorted({t[0] for t in todo})
    stamp = time.strftime("%H:%M:%S")
    print(f"{stamp} fingerprint {fp}: {len(todo)} pairs to run on {workers} workers", flush=True)
    if not todo:
        return 0
    build_state(need)
    ctx = mp.get_context("fork")
    with ctx.Pool(workers, initializer=_init_worker, maxtasksperchild=None) as pool:
        for firm, code, sec, mus in pool.imap_unordered(_task, todo):
            print(f"{time.strftime('%H:%M:%S')} {firm} {code} {sec:.0f}s mu*_lim mu*_mkt mu10K = {mus}",
                  flush=True)
    return 0


def cmd_monotone() -> int:
    import A3_funnel as F

    os.nice(10)
    inputs = json.loads(INPUTS.read_text())
    firms = sorted({f for f, _ in MONO_PAIRS})
    build_state(firms)
    rows = []
    for firm, code in MONO_PAIRS:
        pair = next(p for p in inputs["pairs"] if p["firm"] == firm and p["code"] == code)
        cand = inputs["candidates"][code]
        c = pair["F_rt_usd"] / cand["v_usd"]
        pe = PairEval(_STATE["models"][firm], cand, c, _STATE["draws"][firm], _STATE["idx"])
        pts = [pe.at(k * STEP - c) for k in range(0, GRID_N + 1, 25)]
        ev = [r["ev"] for r in pts]
        p10 = [r["p10k"] for r in pts]
        rows.append({"firm": firm, "code": code, "mu": [k * STEP for k in range(0, GRID_N + 1, 25)], "ev": ev,
                     "se": [r["se"] for r in pts], "p10k": p10,
                     "ev_nondecreasing": all(b >= a - 1e-9 for a, b in zip(ev, ev[1:], strict=False)),
                     "p10k_nondecreasing": all(b >= a - 1e-12 for a, b in zip(p10, p10[1:], strict=False))})
        print(firm, code, rows[-1]["ev_nondecreasing"], rows[-1]["p10k_nondecreasing"],
              [round(x) for x in ev], flush=True)
    (WORK / "A3_monotone.json").write_text(json.dumps({"fingerprint": _fingerprint(), "rows": rows}, indent=1))
    _ = F
    return 0


def cmd_collect() -> int:
    fp = _fingerprint()
    inputs = json.loads(INPUTS.read_text())
    recs, missing = [], []
    for p in inputs["pairs"]:
        out = PAIRS_DIR / f"{p['firm']}__{p['code']}.json"
        if not _done(p["firm"], p["code"], fp):
            missing.append(f"{p['firm']}:{p['code']}")
            continue
        r = json.loads(out.read_text())
        r.pop("evaluations", None)
        recs.append(r)
    print(f"{len(recs)} pairs collected, {len(missing)} missing: {missing[:10]}")
    return 0 if not missing else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("run", "monotone", "collect"))
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--firms")
    ap.add_argument("--codes")
    a = ap.parse_args(argv)
    if a.cmd == "run":
        return cmd_run(a.workers, a.firms.split(",") if a.firms else None,
                       a.codes.split(",") if a.codes else None)
    if a.cmd == "monotone":
        return cmd_monotone()
    return cmd_collect()


if __name__ == "__main__":
    sys.path.insert(0, str(WORK))
    sys.exit(main())
