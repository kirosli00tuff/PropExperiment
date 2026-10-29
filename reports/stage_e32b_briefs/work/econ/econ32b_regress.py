"""E.32b economics regression against E.28 (brief B12): with E.28's own inputs (A3_inputs.json) and S = 1, the new
code must reproduce E.28's mu*_mkt and mu10K_mkt (A3_econ.json) for every computed pair within one grid step.

E.28 reports mu10K in the limit case only. EV and P10K depend on mu only through d = mu - c, so with S_rt = 1.00
tick the market-case threshold is the limit-case one plus exactly 100 grid steps: E.28's implied mu10K_mkt =
mu10K + 1.00. The regression grid runs to 5.00 ticks so that every E.28 value <= 4 has its market twin on the grid.
Expected, per pair:
  mu*_mkt:   E.28 x <= 4  -> new = x (within 0.01);       E.28 "> 4" -> new above 4 (on (4, 5]) or above the cap
  mu10K_mkt: E.28 y <= 4  -> new = y + 1.00 (within 0.01); E.28 "> 4" -> new above the cap 5 (none on [0, 5])
  cost per attempt (E.28's definition, mu = 0 limit case): equal to E.28's cost_per_attempt_usd
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

TOL = 0.01 + 1e-9  # one grid step
EXACT = 1e-9


def _check_star(e28: float | str, new: float | None) -> tuple[bool, str]:
    if isinstance(e28, str):
        ok = new is None or new > 4.0
        return ok, "above 4 in both" if ok else f"E.28 > 4, new {new}"
    if new is None:
        return False, f"E.28 {e28}, new above cap"
    d = abs(new - e28)
    return d <= TOL, "exact" if d < EXACT else f"diff {new - e28:+.2f}"


def _check_10k(e28_lim: float | str, new: float | None) -> tuple[bool, str]:
    if isinstance(e28_lim, str):
        ok = new is None
        return ok, "above cap in both" if ok else f"E.28 > 4 (limit), new {new}"
    if new is None:
        return False, f"E.28 {e28_lim} + 1, new above cap"
    d = abs(new - (e28_lim + 1.0))
    return d <= TOL, "exact" if d < EXACT else f"diff {new - e28_lim - 1.0:+.2f}"


def compare(parts: dict[str, dict[str, Any]], e28doc: dict[str, Any]) -> list[dict[str, Any]]:
    e28 = {f"{p['firm']}|{p['code']}": p for p in e28doc["pairs"]}
    rows = []
    for rec in sorted(parts.values(), key=lambda r: r["job"]["pair"]):
        key = rec["job"]["pair"]
        new, old = rec["cases"]["regress"], e28[key]
        ok_s, note_s = _check_star(old["mu_star_mkt"], new["mu_star_mkt"])
        ok_p, note_p = _check_10k(old["mu10K"], new["mu10K_mkt"])
        cost_diff = new["cost_per_attempt"] - old["cost_per_attempt_usd"]
        gc_old = (old.get("grid_check") or {}).get("mu_star_mkt") or {}
        f_new = new["search"]["mu_star_mkt"]["f_at_k"]
        f_diff = None if f_new is None or gc_old.get("f_at_k") is None else f_new - gc_old["f_at_k"]
        rows.append({"pair": key, "e28_mu_star_mkt": old["mu_star_mkt"], "new_mu_star_mkt": new["mu_star_mkt"],
                     "ok_mu_star": ok_s, "note_mu_star": note_s, "e28_mu10K_lim": old["mu10K"],
                     "new_mu10K_mkt": new["mu10K_mkt"], "ok_mu10K": ok_p, "note_mu10K": note_p,
                     "e28_cost": old["cost_per_attempt_usd"], "new_cost": new["cost_per_attempt"],
                     "cost_diff": cost_diff, "ev_at_k_diff": f_diff,
                     "confirmed": all(s["confirmation"]["confirmed"] for s in new["search"].values()),
                     "corrected": [n for n, s in new["search"].items() if s["k"] != s["k_bisection"]],
                     "n_evaluations": rec["n_evaluations"], "runtime_s": rec["runtime_s"]})
    return rows


def _fmt(x: Any) -> str:
    if x is None:
        return "above cap"
    return x if isinstance(x, str) else f"{x:.2f}"


def _md(rows: list[dict[str, Any]], skipped: dict[str, str], stats: dict[str, Any], stamp: str) -> str:
    n = len(rows)
    ok_s = sum(r["ok_mu_star"] for r in rows)
    ok_p = sum(r["ok_mu10K"] for r in rows)
    ex_s = sum(r["note_mu_star"] in ("exact", "above 4 in both") for r in rows)
    ex_p = sum(r["note_mu10K"] in ("exact", "above cap in both") for r in rows)
    cost_max = max((abs(r["cost_diff"]) for r in rows), default=0.0)
    evd = [abs(r["ev_at_k_diff"]) for r in rows if r["ev_at_k_diff"] is not None]
    fails = [r for r in rows if not (r["ok_mu_star"] and r["ok_mu10K"])]
    rt = sum(r["runtime_s"] for r in rows)
    ne = sum(r["n_evaluations"] for r in rows)
    verdict = "PASS" if not fails and cost_max < 1e-6 else "FAIL"
    out = [
        "# E.32b economics: regression against E.28 (A3_econ.json)", "",
        f"Written by econ32b_regress.py at {stamp} (EconSetup-OpusXHigh). Code: work/econ/econ32b*.py on E.28's "
        "A3_funnel.py / A3_models.py / A3_run.py (copied unchanged, COPY_MANIFEST.json); inputs: E.28's "
        "A3_inputs.json (copied), S = 1 tick for every pair, T = 20, sigma_T = sigma_1m, market case only, grid "
        "0..5.00 ticks at 0.01, bisection then E.28's grid confirmation.", "",
        "E.28 reports mu10K in the limit case; with S = 1.00 its market twin is mu10K + 1.00 exactly (EV and P10K "
        "depend on mu only through d = mu - c, on the same common random numbers). The grid runs to 5.00 so every "
        "E.28 value <= 4 has its twin on the grid. A pass is a difference of at most one grid step (0.01).", "",
        f"## Result: {verdict}", "",
        f"- Pairs compared: {n} (every E.28 pair computed; {len(skipped)} E.28 pairs not computed there either: "
        f"{', '.join(sorted(skipped))}).",
        f"- mu*_mkt within one grid step: {ok_s} / {n}; identical (or above 4 in both): {ex_s} / {n}.",
        f"- mu10K_mkt = E.28 mu10K + 1.00 within one grid step: {ok_p} / {n}; identical (or above the cap in both): "
        f"{ex_p} / {n}.",
        f"- Cost per attempt (E.28's definition): largest absolute difference USD {cost_max:.3g}.",
        f"- EV at the mu*_mkt grid point vs E.28's grid_check f_at_k: largest absolute difference "
        f"{max(evd) if evd else 'n/a'} USD over {len(evd)} pairs (floating point only: E.28 passed the unrounded "
        "d to the day law, this code d rounded to 1e-9 ticks; no threshold moves).",
        f"- Thresholds corrected by the grid confirmation: {sum(bool(r['corrected']) for r in rows)}; "
        f"unconfirmed: {sum(not r['confirmed'] for r in rows)}.",
        f"- Work: {ne} evaluations, {rt:.0f} s summed over jobs; run stats: {json.dumps(stats)}.", ""]
    if fails:
        out += ["## Failures", "", "| pair | E.28 mu*_mkt | new | E.28 mu10K (lim) | new mu10K_mkt | notes |",
                "|---|---|---|---|---|---|"]
        out += [f"| {r['pair']} | {_fmt(r['e28_mu_star_mkt'])} | {_fmt(r['new_mu_star_mkt'])} | "
                f"{_fmt(r['e28_mu10K_lim'])} | {_fmt(r['new_mu10K_mkt'])} | {r['note_mu_star']}; {r['note_mu10K']} |"
                for r in fails]
        out.append("")
    out += ["## Every pair", "",
            "| pair | E.28 mu*_mkt | new mu*_mkt | E.28 mu10K (lim) | new mu10K_mkt | cost E.28 | cost new | evals |",
            "|---|---|---|---|---|---|---|---|"]
    out += [f"| {r['pair']} | {_fmt(r['e28_mu_star_mkt'])} | {_fmt(r['new_mu_star_mkt'])} | "
            f"{_fmt(r['e28_mu10K_lim'])} | {_fmt(r['new_mu10K_mkt'])} | {r['e28_cost']:.2f} | {r['new_cost']:.2f} | "
            f"{r['n_evaluations']} |" for r in rows]
    return "\n".join(out) + "\n"


def write_regression(parts: dict[str, dict[str, Any]], skipped: dict[str, str], stats: dict[str, Any],
                     e28doc: dict[str, Any], work: Path, stamp: str) -> int:
    rows = compare(parts, e28doc)
    md = _md(rows, skipped, stats, stamp)
    (work / "REGRESSION.md").write_text(md)
    (work / "regression.json").write_text(json.dumps({"generated_pdt": stamp, "run": stats, "skipped": skipped,
                                                      "rows": rows}, indent=1))
    fails = [r for r in rows if not (r["ok_mu_star"] and r["ok_mu10K"])]
    print(md.split("## Every pair")[0], flush=True)
    return 0 if not fails else 2
